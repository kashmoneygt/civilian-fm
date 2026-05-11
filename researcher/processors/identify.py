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
  "person_name_hint": "<best guess at the specific person, or null if a generic office>",
  "person_slug": "<slugified name + disambiguator (city/role) if a common name>",
  "role_slug": "<short kebab-case role identifier, e.g. 'mountlake-terrace-permit-specialist' or 'ai-researcher'>",
  "role_overview": "<one sentence: what this role does>",
  "jurisdiction_path": "<slash path like 'us/wa/mountlake-terrace' or 'us' for federal, or null if no jurisdiction applies>",
  "jurisdiction_overview": "<one sentence: what this jurisdiction is>",
  "domains": ["<short tags, e.g. 'local-government', 'permits'>"],
  "search_queries": [
    "<3-6 web search queries that would find authoritative source material about this person/role/jurisdiction. Order by specificity: most specific first.>"
  ]
}}

Rules:
- If the subject is a jurisdiction (e.g. "Mountlake Terrace WA"), the role + jurisdiction define the entity. The specific person may be unknown — set person_name_hint to null and use a slug like "mountlake-terrace-permit-office".
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
