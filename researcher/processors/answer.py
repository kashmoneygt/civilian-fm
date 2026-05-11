"""Answer: spawn the new PersonAgent and have it respond to the user's original goal."""
from __future__ import annotations

from pathlib import Path

from entities._base import PersonAgent

from ..pipeline import Request


def run(req: Request) -> Request:
    person_dir = req.state.get("person_dir")
    if not person_dir:
        req.state["initial_answer"] = "(distillation failed; nothing to answer)"
        return req
    agent = PersonAgent(Path(person_dir))
    req.state["agent"] = agent
    req.state["initial_answer"] = agent.chat(req.user_goal)
    return req
