"""Discover named individuals in the crawled raw sources.

Runs after `research` and before `distill`. Scans crawled pages for named
individuals (elected officials, council members, named staff). Updates the
target with a specific person if a high-relevance candidate is found.

Why this exists: without this step, the goal pipeline collapses to a generic
"office" composite even when the jurisdiction has named, publicly-documented
people who would be much better steered-away-from-the-mean targets. A real
named council member with a public bio is denser, more unique source material
than a generic "permit specialist" role description.
"""
from __future__ import annotations

import re
from pathlib import Path

from entities._refs import ENTITIES_DIR

from ..llm import complete_json
from ..pipeline import Request

REPO = ENTITIES_DIR.parent
RAW_DIR = REPO / "wiki" / "raw" / "web"

SOURCE_BUDGET_CHARS = 200_000

PROMPT = """Given the user's goal, the identified jurisdiction/role, and the raw pages crawled, identify NAMED INDIVIDUALS who would be the best person for the user to chat with.

# User goal
{goal}

# Identified target context
- jurisdiction: {jurisdiction}
- role context: {role_overview}
- domains: {domains}

# Crawled pages (raw text)

{pages}

# Task

Find up to 5 NAMED INDIVIDUALS — real people with first and last names — extracted from the pages above. Rules:

- MUST have a full name (first + last). Skip "the planning director", "city staff", "the permit office", or any unnamed reference.
- MUST have a clear public role (council member, mayor, named staff, planning commissioner, etc.).
- Prefer elected officials and senior named staff over committee mentions.
- The source_file MUST be a basename from the pages above (e.g. `cityofmlt-com--587-city-council.md`).
- relevance_score (1-10): how relevant is this person to the user's specific goal? Council members with permit/planning-committee assignments score higher for a permit goal than at-large members.

Return JSON:

{{
  "candidates": [
    {{
      "name": "<full name>",
      "slug": "<kebab-case-name>-<jurisdiction-disambiguator>",
      "role_hint": "<their actual role, e.g. 'Mountlake Terrace City Council Member'>",
      "source_file": "<basename>.md",
      "relevance_to_goal": "<one sentence: why this person is well-positioned to help with the user's goal>",
      "relevance_score": <1-10 integer>
    }}
  ]
}}

If no NAMED INDIVIDUALS are extractable, return: {{"candidates": []}}"""


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "unknown"


def _build_pages_block(crawled: list[dict]) -> str:
    chunks: list[str] = []
    total = 0
    for c in crawled:
        if "raw_path" not in c:
            continue
        path = Path(c["raw_path"])
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        chunks.append(f"### {path.name}\n\n{text}")
        total += len(text)
        if total > SOURCE_BUDGET_CHARS:
            break
    return "\n\n---\n\n".join(chunks)


def _looks_like_human_name(s: str | None) -> bool:
    """Heuristic: a real human's name has 2+ space-separated words, both alpha-starting,
    and isn't full of role-y words like 'specialist', 'office', 'director'."""
    if not s:
        return False
    parts = s.split()
    if len(parts) < 2:
        return False
    role_words = {"specialist", "office", "officer", "director", "department", "staff",
                  "manager", "coordinator", "assistant", "clerk", "secretary"}
    if any(p.lower() in role_words for p in parts):
        return False
    return all(p[:1].isalpha() for p in parts)


def run(req: Request) -> Request:
    target = req.state.get("target", {})
    # If identify already pinned a real named individual (e.g. a public figure), respect it.
    if _looks_like_human_name(target.get("person_name_hint")):
        return req

    crawled = req.state.get("crawled", [])
    pages_block = _build_pages_block(crawled)
    if not pages_block:
        req.state["candidates"] = []
        return req

    out = complete_json(
        PROMPT.format(
            goal=req.user_goal,
            jurisdiction=target.get("jurisdiction_path") or "(none)",
            role_overview=target.get("role_overview", ""),
            domains=target.get("domains", []),
            pages=pages_block,
        ),
        temperature=0.0,
    )
    candidates = sorted(
        [c for c in out.get("candidates", []) if c.get("name")],
        key=lambda c: -int(c.get("relevance_score", 0)),
    )
    req.state["candidates"] = candidates

    if candidates:
        pick = candidates[0]
        target["person_name_hint"] = pick["name"]
        target["person_slug"] = _slugify(pick.get("slug") or pick["name"])
        # The chosen person's ACTUAL role replaces the goal-derived role.
        # Steve Woodard is a Mayor, not a permit-specialist — even if the goal was about permits.
        # The mayor-agent answers permit questions in their capacity as an elected official
        # who can direct constituents; the role wiki captures that distinction.
        role_hint = pick.get("role_hint") or ""
        if role_hint:
            target["role_slug"] = _slugify(role_hint)
            target["role_overview"] = role_hint
        target["picked_from_candidates"] = True
        req.state["target"] = target
    return req
