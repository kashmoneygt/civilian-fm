"""Distill: turn crawled raw sources into persona.md + skills.md + entity stubs.

Enforces Section 2.7 content discipline:
  1. Uniqueness test — every fact must be non-obvious to a bare LLM.
  2. Density over volume — token caps per entity kind.
  3. Honest boundaries are mandatory.

Also creates role and jurisdiction entity stubs if they don't yet exist,
so cross-references resolve.
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

# Token-ish budgets (rough char limits, 1 token ≈ 4 chars)
PERSONA_BUDGET_CHARS = {True: 20_000, False: 60_000}  # keyed by thin_source bool
SOURCE_BUDGET_CHARS = 250_000  # how much raw context we feed to the LLM at most


def _strip_fences(s: str) -> str:
    """Strip any leading/trailing code fences the LLM may have wrapped output in."""
    s = s.strip()
    # leading ``` or ```anything
    s = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n", "", s)
    # trailing ```
    s = re.sub(r"\n```\s*$", "", s)
    return s.strip()


PERSONA_PROMPT = """You are building a `persona.md` file for a person-agent in a civic-information system. The persona is loaded into an LLM's system prompt at runtime so users can chat with this person.

# Target

- Name hint: {name_hint}
- Person slug: {person_slug}
- Role: {role_slug} ({role_overview})
- Jurisdiction: {jurisdiction_path} ({jurisdiction_overview})
- Domains: {domains}
- Thin-source target: {thin_source}  (true means fewer than 8 sources available — apply nuwa thin-source adaptation: 2-3 mental models max, all labeled "inferred from limited sources")

# Available raw source material (verbatim crawler output)

{sources}

# Content discipline — non-negotiable

1. **Uniqueness test.** Every fact you include must be NON-OBVIOUS to a bare LLM. If GPT-4o-mini could generate the claim from training data alone (e.g., "permits ensure projects meet local building codes"), DO NOT include it. We're hunting for: specific names, dates, dollar amounts, phone numbers, addresses, hidden gotchas, recent regulatory changes, named-person quirks.
2. **Quote verbatim** when material: dollar figures, dates, names, IRS phrasing, ordinance numbers — in quotation marks with source citation.
3. **No filler.** No "consult a professional" deflections. No "ensures compliance with local code" boilerplate. Facts only.
4. **Honest boundaries are mandatory.** Include a section listing what we DON'T know.
5. **Cite every fact** with `[source: <basename>.md]` using the filenames from the raw material above.
6. **Stay under {budget_chars} chars total.**
7. **Do NOT invent statistics.** Do not write "N sources mention X" unless you have actually counted. Do not fabricate confidence percentages or numerical claims. If you don't know, say "unknown."
8. **Output raw markdown only — no code fences.** Do not wrap the file in ```markdown or ```yaml. Begin directly with `---`.

# Output

Produce a complete markdown file with this exact structure. Use the `[[role:...]]`, `[[jur:...]]`, `[[topic:...]]` syntax inline in the body where it makes sense — these are cross-references resolved at runtime.

---
name: {name_hint_or_placeholder}
slug: {person_slug}
aliases: []
roles:
  - role: {role_slug}
    period: [<best-guess-start-year-or-null>, null]
jurisdictions:
  primary: {jurisdiction_path}
domains: {domains}
linked_topics: []
confidence: low|medium|high
---

# <Name>

## Identity card

<2-3 sentences in first person. Who am I, what role do I hold, where, since when. Use [[role:...]] and [[jur:...]] cross-references.>

## Mental models

<For thin-source: 2-3 bullets, each "(inferred from limited sources)". For rich-source: 3-7 bullets. Each fact cited.>

- ...

## Decision heuristics

<5-10 heuristics for rich-source; 2-4 for thin-source. Extracted from observed decisions in sources.>

- ...

## Expression DNA

<Only fill this if there are direct quotes / writings. Otherwise: "> not in sources — defer to role tone defaults".>

## Timeline

<Only fill if dates are in sources. Otherwise: "> not in sources".>

## Values and anti-patterns

<What this person/role pursues; what they reject. Only from evidence.>

## Honest boundaries

<MANDATORY. List 3-6 specific things we DO NOT KNOW about this person/role/jurisdiction. Be specific to what is or isn't in the sources above. Do NOT invent statistics about source counts. Examples of good entries (substitute real specifics from the sources):

- "We have no direct quotes from <named person> — voice is approximated from generic role norms."
- "Sources don't say what happens if an applicant misses the inspection window."
- "No information about <specific scenario>."
- "Sources reflect <year range>; recent changes may not be captured."

Generate your own specific honest-boundary statements grounded in what's actually missing from THESE sources.>

- ...

## Sources

<List the source basenames used.>

Begin the output with the YAML frontmatter. Output ONLY the markdown — no commentary."""


SKILLS_PROMPT = """Building `skills.md` for the person-agent {name_hint} ({role_slug} in {jurisdiction_path}).

Produce a short markdown file (<2000 chars) that:

1. Lists what this agent can confidently speak to (4-8 bullets, specific to their role+jurisdiction).
2. Lists when to draw on which kind of context: "asked about X → consult [[jur:Y]]" patterns.
3. Lists when to defer ("if asked about ___ outside this role, say so plainly").

Output ONLY markdown, no commentary."""


def _read_raw_sources(crawled: list[dict]) -> tuple[str, list[str]]:
    """Read raw markdown files referenced by crawl results. Returns (concatenated_block, basenames)."""
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
    """Copy raw source files into entity's wiki/public/ for traceability."""
    public_dir = entity_dir / "wiki" / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    for basename in basenames:
        src = RAW_DIR / basename
        if src.exists():
            (public_dir / basename).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def run(req: Request) -> Request:
    target = req.state["target"]
    thin = req.state.get("thin_source", True)

    sources_block, basenames = _read_raw_sources(req.state.get("crawled", []))
    if not basenames:
        req.state["distill_error"] = "no successful crawls — cannot distill"
        return req

    # 1. Build role + jurisdiction stubs first so cross-refs resolve.
    _ensure_role_stub(target["role_slug"], target.get("role_overview", ""))
    _ensure_jurisdiction_stub(target.get("jurisdiction_path"), target.get("jurisdiction_overview", ""))

    # 2. Determine person slug + create entity dir.
    person_slug = target.get("person_slug") or target["role_slug"] + "-office"
    person_dir = ENTITIES_DIR / "people" / person_slug
    person_dir.mkdir(parents=True, exist_ok=True)

    # 3. Distill persona.md.
    persona_md = complete(
        PERSONA_PROMPT.format(
            name_hint=target.get("person_name_hint") or f"{target['role_slug']} (composite)",
            name_hint_or_placeholder=target.get("person_name_hint") or f"{target['role_slug'].replace('-', ' ').title()} (composite)",
            person_slug=person_slug,
            role_slug=target["role_slug"],
            role_overview=target.get("role_overview", ""),
            jurisdiction_path=target.get("jurisdiction_path") or "n/a",
            jurisdiction_overview=target.get("jurisdiction_overview", ""),
            domains=target.get("domains", []),
            thin_source=thin,
            sources=sources_block[:SOURCE_BUDGET_CHARS],
            budget_chars=PERSONA_BUDGET_CHARS[thin],
        ),
        temperature=0.2,
    )
    persona_md = _strip_fences(persona_md)
    (person_dir / "persona.md").write_text(persona_md + "\n", encoding="utf-8")

    # 4. Distill skills.md.
    skills_md = complete(
        SKILLS_PROMPT.format(
            name_hint=target.get("person_name_hint") or f"{target['role_slug']} office",
            role_slug=target["role_slug"],
            jurisdiction_path=target.get("jurisdiction_path") or "n/a",
        ),
        temperature=0.2,
    )
    skills_md = _strip_fences(skills_md)
    (person_dir / "skills.md").write_text(skills_md + "\n", encoding="utf-8")

    # 5. Copy raw sources into the entity's wiki/public/ for provenance.
    _save_raw_to_entity_wiki(person_dir, basenames)

    req.state["person_dir"] = str(person_dir)
    req.state["person_slug"] = person_slug
    req.state["distilled_at"] = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return req
