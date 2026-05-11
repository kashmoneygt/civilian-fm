"""EntitySeed — the hand-off contract between discovery and build phases.

Both entry points (goal pipeline, URL pipeline) reduce to producing a list
of EntitySeed. After that, every seed flows through the same build sub-pipeline:
broad_research → refine_subject → targeted_research → distill.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EntitySeed:
    """A description of an entity we intend to build."""

    name: str
    slug: str
    kind: str = "person"          # "person" | "topic"
    role_hint: str = ""
    role_slug: str = ""
    jurisdiction_hint: str = ""
    jurisdiction_path: str = ""
    domains: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)

    # Origin context — what surfaced this seed
    origin: str = ""              # "goal" | "url"
    origin_url: str | None = None
    origin_goal: str | None = None

    # Set to True for the seed that should answer the user's original query
    # (only one seed per run is primary)
    primary: bool = False
