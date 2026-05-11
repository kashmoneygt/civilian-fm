"""Composed pipelines."""
from __future__ import annotations

from .pipeline import run, Request
from .processors import answer, clarify, crawl_url, distill, extract_entities, identify, research

GOAL_PIPELINE = [
    clarify.run,
    identify.run,
    research.run,
    distill.run,
    answer.run,
]

URL_PIPELINE = [
    crawl_url.run,
    extract_entities.run,
    # For each extracted entity, the dispatcher runs identify-with-pre-resolved-target +
    # research + distill. Implemented in scripts/research.py rather than as a single
    # processor (variable-length subloop is cleaner outside the linear pipeline).
]
