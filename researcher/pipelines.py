"""Composed pipelines.

Unified DAG: both entry points produce a list[EntitySeed], then each seed
flows through the same BUILD_ENTITY sub-pipeline.

Run via researcher.runner.run(discovery, BUILD_ENTITY, ...)
"""
from __future__ import annotations

from .processors import (
    answer,
    broad_research,
    clarify,
    crawl_url,
    discover_people,
    distill,
    extract_entities,
    identify,
    refine_subject,
    seeds_from_extraction,
    seeds_from_target,
    targeted_research,
)

# --- Discovery pipelines (entry-specific) ---

GOAL_DISCOVERY = [
    clarify.run,
    identify.run,
    seeds_from_target.run,
]

URL_DISCOVERY = [
    crawl_url.run,
    extract_entities.run,
    seeds_from_extraction.run,
]

# --- Build sub-pipeline (shared, per seed) ---

BUILD_ENTITY = [
    broad_research.run,
    discover_people.run,    # may refine the seed (if seed didn't have a specific person name yet)
    refine_subject.run,     # LLM identifies canonical sources + targeted queries
    targeted_research.run,  # pass 2: deepen
    distill.run,
    answer.run,             # only fires for the primary seed
]
