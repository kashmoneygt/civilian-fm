"""Distill — read all_crawled (broad + targeted), produce persona.md or overview.md.

Consumes:
  req.state["seed"]: EntitySeed
  req.state["all_crawled"]: list of {url, raw_path, ...}
  req.state["refine"]: optional output from refine_subject

Produces (for kind=='person'):
  entities/people/<slug>/persona.md
  entities/people/<slug>/skills.md
  entities/people/<slug>/wiki/public/<basename>.md (copy of raw sources)
  entities/roles/<role_slug>/overview.md  (stub if not exists)
  entities/jurisdictions/<path>/overview.md (stub if not exists)

For kind=='topic':
  entities/topics/<slug>/overview.md
  entities/topics/<slug>/wiki/public/<basename>.md
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from entities._refs import ENTITIES_DIR

from ..llm import complete
from ..pipeline import Request

REPO = ENTITIES_DIR.parent
RAW_DIR = REPO / "wiki" / "raw" / "web"

PERSONA_BUDGET_CHARS = {True: 20_000, False: 60_000}  # keyed by thin_source bool
TOPIC_BUDGET_CHARS = 15_000
SOURCE_BUDGET_CHARS = 80_000
PER_SOURCE_BUDGET_CHARS = 8_000
THIN_SOURCE_THRESHOLD = 8


def _strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n", "", s)
    s = re.sub(r"\n```\s*$", "", s)
    return s.strip()


def _read_raw_sources(crawled: list[dict]) -> tuple[str, list[str]]:
    chunks: list[str] = []
    basenames: list[str] = []
    total = 0
    for c in crawled:
        if "raw_path" not in c:
            continue
        path = Path(c["raw_path"])
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if len(text) > PER_SOURCE_BUDGET_CHARS:
            text = text[:PER_SOURCE_BUDGET_CHARS] + f"\n[... truncated at {PER_SOURCE_BUDGET_CHARS} chars]"
        basename = path.name
        chunks.append(f"### {basename}\n\n{text}")
        basenames.append(basename)
        total += len(text)
        if total > SOURCE_BUDGET_CHARS:
            break
    return "\n\n---\n\n".join(chunks), basenames


def _ensure_role_stub(role_slug: str, role_overview: str) -> Path:
    role_dir = ENTITIES_DIR / "roles" / role_slug
    role_dir.mkdir(parents=True, exist_ok=True)
    overview = role_dir / "overview.md"
    if not overview.exists():
        overview.write_text(
            f"---\nslug: {role_slug}\nkind: role\n---\n\n# {role_slug.replace('-', ' ').title()}\n\n{role_overview}\n",
            encoding="utf-8",
        )
    (role_dir / "wiki").mkdir(exist_ok=True)
    return role_dir


def _ensure_jurisdiction_stub(jur_path: str, jur_overview: str) -> Path:
    if not jur_path:
        return ENTITIES_DIR / "jurisdictions"
    jur_dir = ENTITIES_DIR / "jurisdictions" / jur_path
    jur_dir.mkdir(parents=True, exist_ok=True)
    overview = jur_dir / "overview.md"
    if not overview.exists():
        overview.write_text(
            f"---\npath: {jur_path}\nkind: jurisdiction\n---\n\n# {jur_path}\n\n{jur_overview}\n",
            encoding="utf-8",
        )
    (jur_dir / "wiki").mkdir(exist_ok=True)
    return jur_dir


def _save_raw_to_entity_wiki(entity_dir: Path, basenames: list[str]) -> None:
    public_dir = entity_dir / "wiki" / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    for basename in basenames:
        src = RAW_DIR / basename
        if src.exists():
            (public_dir / basename).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


PERSONA_PROMPT = """You are building a `persona.md` for a person-agent. The persona is loaded into an LLM's system prompt at runtime so users can chat AS this person.

# Subject

- Name: {name}
- Slug: {slug}
- Role: {role_slug} ({role_hint})
- Jurisdiction: {jurisdiction_path} ({jurisdiction_hint})
- Domains: {domains}
- Source density: {density} ({source_count} sources)

# Available raw source material

{sources}

# Critical instructions

For RICH-source (well-documented public figures, named officials):

- CAPTURE their actual views and tools. Even "well-known" views — that's the persona. A Karpathy persona without his actual stances isn't a Karpathy persona.
- Quote verbatim phrases they're known for.
- Workflows/tools section MUST list specific named things (nanoGPT, SuperWhisper, Cash Balance Plans).
- 5-7 mental models, each grounded in a quoted claim from sources.
- Expression DNA filled with verbal habits from sources.

For THIN-source (composite roles, limited public material):

- 2-3 mental models, each labeled "(inferred from limited sources)".
- Voice approximated from role norms.
- Honest boundaries section is heavy.

# Hard rules

1. Cite every fact with `[source: <basename>.md]`.
2. No fabrication. Unknown sections say `> not in sources`.
3. Speak in first person ("I think X", "I use Y").
4. Honest boundaries are mandatory — list specific gaps in source material.
5. No "consult a professional" deflections.
6. Do NOT invent statistics ("N sources mention X").
7. Output raw markdown only — no code fences. Begin with `---`.
8. Stay under {budget_chars} chars total.

# Output structure

```
---
name: {name}
slug: {slug}
aliases: []
roles:
  - role: {role_slug}
    period: [<start-year-or-null>, null]
jurisdictions:
  primary: {jurisdiction_path_or_n_a}
domains: {domains}
linked_topics: []
confidence: low|medium|high
---

# {name}

## Identity card
<2-3 first-person sentences. Use [[role:...]] and [[jur:...]] cross-refs.>

## Mental models
<5-7 for rich-source, 2-3 for thin. Each cited.>

## Decision heuristics
<5-10 for rich, 2-4 for thin. Specific to this person.>

## Workflows and specific tools
<REQUIRED for rich-source. Specific tools, repos, apps, products, books, podcasts. Each cited.>

## Expression DNA
<For rich-source REQUIRED. Verbal habits, recurring phrases. Quote verbatim where possible.>

## Timeline
<Only if dates are in sources.>

## Values and anti-patterns

## Honest boundaries
<MANDATORY. List 3-6 specific things NOT in sources.>

## Sources
<basenames used>
```"""


TOPIC_PROMPT = """You are building an `overview.md` for a TOPIC entity (a concept, event, or domain — not a person). Loaded into agent context when persons link to it via [[topic:...]].

# Topic

- Name: {name}
- Slug: {slug}
- Domains: {domains}
- Source density: {density}

# Raw sources

{sources}

# Rules

1. Cite every fact: `[source: <basename>.md]`.
2. Non-obvious facts only. Skip anything Wikipedia already explains.
3. Quote verbatim where material (specific numbers, dates, named cases, named people).
4. Stay under {budget_chars} chars.

# Output

```
---
name: {name}
slug: {slug}
kind: topic
domains: {domains}
---

# {name}

## What it is (one paragraph)

## Key facts
- ...

## Connected people
- [[person:<slug>]] — one-line on how they relate to this topic

## Contested or non-obvious points
- ...

## Sources
```"""


SKILLS_PROMPT = """Build `skills.md` for {name} ({role_slug}{jur_suffix}).

Produce <2000 chars markdown:
1. Areas of expertise (4-8 bullets, specific to this person).
2. Link-following rules ONLY if you'd genuinely link to a {{role:..., jur:..., topic:...}} that EXISTS. Do NOT invent links.
3. Deferral patterns ("if asked about ... say so").

Output markdown only, no code fences."""


def _distill_person(req: Request, sources_block: str, basenames: list[str]) -> Path:
    seed = req.state["seed"]
    thin = req.state.get("source_count", len(basenames)) < THIN_SOURCE_THRESHOLD
    _ensure_role_stub(seed.role_slug or "unknown-role", seed.role_hint)
    _ensure_jurisdiction_stub(seed.jurisdiction_path, seed.jurisdiction_hint)

    person_dir = ENTITIES_DIR / "people" / seed.slug
    person_dir.mkdir(parents=True, exist_ok=True)

    persona_md = complete(
        PERSONA_PROMPT.format(
            name=seed.name,
            slug=seed.slug,
            role_slug=seed.role_slug or "unknown",
            role_hint=seed.role_hint or "",
            jurisdiction_path=seed.jurisdiction_path or "n/a",
            jurisdiction_path_or_n_a=seed.jurisdiction_path or "n/a",
            jurisdiction_hint=seed.jurisdiction_hint or "",
            domains=seed.domains,
            density="thin" if thin else "rich",
            source_count=len(basenames),
            sources=sources_block[:SOURCE_BUDGET_CHARS],
            budget_chars=PERSONA_BUDGET_CHARS[thin],
        ),
        temperature=0.3,
    )
    persona_md = _strip_fences(persona_md)
    (person_dir / "persona.md").write_text(persona_md + "\n", encoding="utf-8")

    skills_md = complete(
        SKILLS_PROMPT.format(
            name=seed.name,
            role_slug=seed.role_slug or "unknown",
            jur_suffix=f" in {seed.jurisdiction_path}" if seed.jurisdiction_path else "",
        ),
        temperature=0.2,
    )
    skills_md = _strip_fences(skills_md)
    (person_dir / "skills.md").write_text(skills_md + "\n", encoding="utf-8")

    _save_raw_to_entity_wiki(person_dir, basenames)
    return person_dir


def _distill_topic(req: Request, sources_block: str, basenames: list[str]) -> Path:
    seed = req.state["seed"]
    topic_dir = ENTITIES_DIR / "topics" / seed.slug
    topic_dir.mkdir(parents=True, exist_ok=True)

    overview_md = complete(
        TOPIC_PROMPT.format(
            name=seed.name,
            slug=seed.slug,
            domains=seed.domains,
            density="rich" if len(basenames) >= THIN_SOURCE_THRESHOLD else "thin",
            sources=sources_block[:SOURCE_BUDGET_CHARS],
            budget_chars=TOPIC_BUDGET_CHARS,
        ),
        temperature=0.3,
    )
    overview_md = _strip_fences(overview_md)
    (topic_dir / "overview.md").write_text(overview_md + "\n", encoding="utf-8")
    _save_raw_to_entity_wiki(topic_dir, basenames)
    return topic_dir


def run(req: Request) -> Request:
    seed = req.state["seed"]
    crawled = req.state.get("all_crawled", req.state.get("broad_crawled", []))
    sources_block, basenames = _read_raw_sources(crawled)
    if not basenames:
        req.state["distill_error"] = "no successful crawls"
        return req

    req.state["source_count"] = len(basenames)
    if seed.kind == "topic":
        topic_dir = _distill_topic(req, sources_block, basenames)
        req.state["topic_dir"] = str(topic_dir)
    else:
        person_dir = _distill_person(req, sources_block, basenames)
        req.state["person_dir"] = str(person_dir)
    req.state["distilled_at"] = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return req
