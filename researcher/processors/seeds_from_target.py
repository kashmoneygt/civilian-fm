"""Convert identify+discover_people output into EntitySeed[].

Goal pipeline emits ONE primary seed by default. If discover_people surfaced
strong secondary candidates we could emit them too (future).
"""
from __future__ import annotations

from ..pipeline import Request
from ..seed import EntitySeed


def run(req: Request) -> Request:
    target = req.state.get("target", {})
    seed = EntitySeed(
        name=target.get("person_name_hint") or target.get("role_slug", "unknown"),
        slug=target.get("person_slug") or target.get("role_slug", "unknown"),
        kind="person",
        role_hint=target.get("role_overview", ""),
        role_slug=target.get("role_slug", ""),
        jurisdiction_hint=target.get("jurisdiction_overview", ""),
        jurisdiction_path=target.get("jurisdiction_path") or "",
        domains=target.get("domains", []),
        search_queries=target.get("search_queries", []),
        origin="goal",
        origin_goal=req.user_goal,
        primary=True,
    )
    req.state["seeds"] = [seed]
    return req
