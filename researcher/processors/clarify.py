"""Clarify: decide whether the goal is specific enough or needs follow-up questions.

In auto mode, we never block the pipeline — we either accept the goal as-is or
emit a synthetic clarification ("assuming X based on the goal text"). The
clarifying questions are recorded in state but don't halt execution.
"""
from __future__ import annotations

from ..llm import complete_json
from ..pipeline import Request

PROMPT = """The user said: "{goal}"

Decide if this goal has enough specificity to start research. Required: an action and a jurisdiction (or a clearly-named subject like a public figure).

Return JSON with this exact shape:
{{
  "specific_enough": true|false,
  "extracted_action": "<verb phrase, e.g. 'get a building permit for a deck'>",
  "extracted_subject": "<jurisdiction OR public-figure name, e.g. 'Mountlake Terrace WA' or 'Andrej Karpathy'>",
  "extracted_subject_kind": "jurisdiction|person|other",
  "clarifying_questions": [<up to 3 short questions the user could answer to disambiguate; empty if specific_enough is true>],
  "assumed_fill_ins": {{<dict of any values you assumed in order to proceed; empty if specific_enough is true>}}
}}"""


def run(req: Request) -> Request:
    if req.user_url:  # URL-mode bypass: no clarification needed
        return req

    out = complete_json(PROMPT.format(goal=req.user_goal))
    req.state["clarified"] = out
    req.state["clarified_action"] = out["extracted_action"]
    req.state["clarified_subject"] = out["extracted_subject"]
    req.state["clarified_subject_kind"] = out["extracted_subject_kind"]
    return req
