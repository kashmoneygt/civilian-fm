"""Convert extract_entities output into EntitySeed[].

The first extracted person is marked primary (the one we'll answer with).
Topics also become seeds but with kind='topic'. (Topic distill is simpler;
see processors/distill.py.)
"""
from __future__ import annotations

import re

from ..pipeline import Request
from ..seed import EntitySeed


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "unknown"


def run(req: Request) -> Request:
    extracted = req.state.get("extracted_entities", {})
    seeds: list[EntitySeed] = []

    for i, p in enumerate(extracted.get("people", [])):
        seeds.append(EntitySeed(
            name=p["name"],
            slug=_slugify(p.get("slug") or p["name"]),
            kind="person",
            role_hint=p.get("role_hint", ""),
            role_slug=_slugify(p.get("role_hint", "")) if p.get("role_hint") else "",
            search_queries=p.get("search_queries", []),
            origin="url",
            origin_url=req.user_url,
            primary=(i == 0),  # first extracted person answers the initial query
        ))

    for t in extracted.get("topics", []):
        seeds.append(EntitySeed(
            name=t["name"],
            slug=_slugify(t.get("slug") or t["name"]),
            kind="topic",
            search_queries=t.get("search_queries", []),
            origin="url",
            origin_url=req.user_url,
            primary=False,
        ))

    req.state["seeds"] = seeds
    return req
