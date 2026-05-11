"""Identify: turn the clarified goal into a concrete entity target.

For a jurisdiction-shaped goal ("permit in Mountlake Terrace"), this produces:
  - jurisdiction_path (e.g. "us/wa/mountlake-terrace")
  - role_slug (e.g. "mountlake-terrace-permit-specialist")
  - person_name_hint (often None until research crawls staff pages)

For a public-figure goal ("Andrej Karpathy on transformers"), this produces:
  - person_slug (e.g. "karpathy")
  - person_name (e.g. "Andrej Karpathy")
  - domains (e.g. ["ai-ml"])
"""
from __future__ import annotations

import re

from ..llm import complete_json
from ..pipeline import Request

PROMPT = """The user's clarified goal:
  action: {action}
  subject: {subject}
  subject_kind: {subject_kind}

Identify the target entity that should answer this. Return JSON:

{{
  "target_kind": "person",
  "person_name_hint": "<MUST be a real human's first+last name (e.g. 'Andrej Karpathy', 'Brian Kemp') OR null. NEVER a role title like 'permit specialist' or 'building official'. If you don't know a specific named individual, return null and the system will discover one from crawled pages.>",
  "person_slug": "<slugified first-last name + disambiguator if common name, OR null when person_name_hint is null>",
  "role_slug": "<short kebab-case role identifier, e.g. 'mountlake-terrace-permit-specialist' or 'ai-researcher'>",
  "role_overview": "<one sentence: what this role does>",
  "jurisdiction_path": "<slash path like 'us/wa/mountlake-terrace' or 'us' for federal, or null if no jurisdiction applies>",
  "jurisdiction_overview": "<one sentence: what this jurisdiction is>",
  "domains": ["<short tags, e.g. 'local-government', 'permits'>"],
  "search_queries": [
    "<6-8 queries. STRUCTURE:",
    "  - 2-3 queries about the procedural specifics of the goal (e.g. 'mountlake terrace deck permit requirements')",
    "  - 3-5 queries that would surface NAMED INDIVIDUALS in this jurisdiction —",
    "    elected officials, council members, mayor, named department staff, planning commissioners.",
    "    Examples: '<city> city council members', '<city> mayor', '<city> staff directory',",
    "    '<city> planning commission members', '<city> building department director'.",
    "  Most-specific first."
  ]
}}

Rules:
- If the subject is a jurisdiction (e.g. "Mountlake Terrace WA"), we PREFER to surface a specific named person eventually. Set person_name_hint to null only when no obvious named individual exists (we'll discover candidates from the crawled pages).
- If the subject is a public figure, use their canonical slug (karpathy, donald-trump, brian-kemp).
- Slugs are lowercase, kebab-case, ASCII only.
- search_queries should be web-search-ready text (no operators required)."""


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "unknown"


def run(req: Request) -> Request:
    if req.user_url:  # URL-mode handled in extract_entities, not here
        return req

    out = complete_json(
        PROMPT.format(
            action=req.state.get("clarified_action", req.user_goal),
            subject=req.state.get("clarified_subject", ""),
            subject_kind=req.state.get("clarified_subject_kind", "other"),
        )
    )

    # normalize slugs
    if out.get("person_slug"):
        out["person_slug"] = _slugify(out["person_slug"])
    out["role_slug"] = _slugify(out.get("role_slug", "unknown-role"))

    req.state["target"] = out
    return req
