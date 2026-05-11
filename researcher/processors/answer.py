"""Answer the user's original goal using the newly built person-agent.

Only runs for the PRIMARY seed (the one marked primary=True). Topics skip this.
"""
from __future__ import annotations

from pathlib import Path

from entities._agent import ToolPersonAgent

from ..pipeline import Request


def run(req: Request) -> Request:
    seed = req.state["seed"]
    if not seed.primary or seed.kind != "person":
        return req
    person_dir = req.state.get("person_dir")
    if not person_dir:
        return req
    agent = ToolPersonAgent(Path(person_dir))
    user_msg = seed.origin_goal or seed.origin_url or "Tell me about yourself."
    req.state["initial_answer"] = agent.chat(user_msg)
    return req
