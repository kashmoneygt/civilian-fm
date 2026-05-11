"""Unified runner — both goal-mode and url-mode reduce to:
    discover seeds → for each seed: build_entity → answer the original query (primary only).

Removes the URL-mode subloop hack from v2.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from .pipeline import Request, run as run_processors
from .seed import EntitySeed

Processor = Callable[[Request], Request]


def run(
    discovery: list[Processor],
    build: list[Processor],
    user_goal: str = "",
    user_url: str | None = None,
    verbose: bool = True,
) -> dict:
    """Run discovery → for each seed: build → return summary.

    `discovery` produces `req.state["seeds"] : list[EntitySeed]`.
    `build` is the per-seed sub-pipeline. Each build run gets its own Request
    seeded with the entity seed.
    """
    t0 = time.time()
    req = Request(user_goal=user_goal, user_url=user_url)

    if verbose:
        print(f"\n=== discovery ({'url' if user_url else 'goal'}) ===")
    for p in discovery:
        name = p.__module__.split(".")[-1]
        t = time.time()
        if verbose:
            print(f"  -> {name}...", end="", flush=True)
        req = p(req)
        if verbose:
            print(f" {time.time()-t:.1f}s")

    seeds: list[EntitySeed] = req.state.get("seeds", [])
    if verbose:
        print(f"\nseeds: {len(seeds)} entities to build")
        for s in seeds:
            mark = " (primary)" if s.primary else ""
            print(f"  - {s.kind}: {s.name} ({s.slug}){mark}")

    built: list[dict] = []
    for seed in seeds:
        if verbose:
            print(f"\n=== build: {seed.name} ===")
        sub_req = Request(user_goal=f"build entity {seed.name}")
        sub_req.state["seed"] = seed
        sub_req.state["origin_state"] = req.state  # let build steps see discovery output
        for p in build:
            name = p.__module__.split(".")[-1]
            t = time.time()
            if verbose:
                print(f"  -> {name}...", end="", flush=True)
            try:
                sub_req = p(sub_req)
            except Exception as e:
                if verbose:
                    print(f" ERR ({e!r})")
                sub_req.state["build_error"] = repr(e)
                break
            if verbose:
                print(f" {time.time()-t:.1f}s")
        built.append({
            "seed": seed,
            "person_dir": sub_req.state.get("person_dir"),
            "topic_dir": sub_req.state.get("topic_dir"),
            "initial_answer": sub_req.state.get("initial_answer"),
            "error": sub_req.state.get("build_error"),
        })

    if verbose:
        print(f"\n=== done in {time.time()-t0:.1f}s ===")

    return {
        "discovery_state": req.state,
        "seeds": seeds,
        "built": built,
    }
