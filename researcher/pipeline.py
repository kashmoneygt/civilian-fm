"""Lean processor pipeline (ADK-inspired). ~30 LOC of framework.

Each processor is a plain function `Request -> Request`. Each writes its output
to `req.state[<key>]` by convention; downstream processors read by key.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Request:
    user_goal: str = ""
    user_url: str | None = None
    state: dict[str, Any] = field(default_factory=dict)


Processor = Callable[[Request], Request]


def run(processors: list[Processor], req: Request) -> Request:
    for p in processors:
        req = p(req)
    return req
