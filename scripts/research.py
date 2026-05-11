"""CLI: run the researcher unified pipeline on a goal or a URL.

Usage:
    uv run python -m scripts.research "i want to learn from naval ravikant"
    uv run python -m scripts.research --url "https://www.youtube.com/watch?v=GCygktDbU3Q"

Both entry points produce list[EntitySeed] then build each seed.
"""
from __future__ import annotations

import argparse
import sys

from researcher.pipelines import BUILD_ENTITY, GOAL_DISCOVERY, URL_DISCOVERY
from researcher.runner import run


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="user goal (omit if --url is given)")
    ap.add_argument("--url", help="URL entry point")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.url:
        result = run(URL_DISCOVERY, BUILD_ENTITY, user_url=args.url, verbose=not args.quiet)
    elif args.input:
        result = run(GOAL_DISCOVERY, BUILD_ENTITY, user_goal=args.input, verbose=not args.quiet)
    else:
        ap.print_help()
        return 2

    print("\n=== Result ===\n")
    for b in result["built"]:
        seed = b["seed"]
        dir_ = b.get("person_dir") or b.get("topic_dir")
        mark = " (primary)" if seed.primary else ""
        if dir_:
            print(f"  ✓ {seed.kind}: {seed.name}{mark} → {dir_}")
        elif b.get("error"):
            print(f"  ✗ {seed.kind}: {seed.name}{mark} — ERROR: {b['error']}")
        else:
            print(f"  ? {seed.kind}: {seed.name}{mark} — (no output)")

    primary = next((b for b in result["built"] if b["seed"].primary and b.get("initial_answer")), None)
    if primary:
        print("\n--- initial answer ---\n")
        print(primary["initial_answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
