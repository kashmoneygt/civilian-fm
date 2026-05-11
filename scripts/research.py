"""CLI: run the researcher pipeline on a goal or a URL.

Usage:
    uv run python -m scripts.research "i want a building permit for a deck in Mountlake Terrace WA"
    uv run python -m scripts.research --url "https://www.youtube.com/watch?v=GCygktDbU3Q"
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from researcher.pipeline import Request, run
from researcher.pipelines import GOAL_PIPELINE
from researcher.processors import distill, identify, research


def run_goal(goal: str) -> Request:
    print(f"\n=== Goal pipeline: {goal!r}\n")
    req = Request(user_goal=goal)
    for step in GOAL_PIPELINE:
        t0 = time.time()
        name = step.__module__.split(".")[-1]
        print(f"  -> {name}...", end="", flush=True)
        try:
            req = step(req)
        except Exception as e:
            print(f" ERR ({e!r})")
            raise
        print(f" {time.time() - t0:.1f}s")
    return req


def run_url(url: str) -> Request:
    print(f"\n=== URL pipeline: {url}\n")
    from researcher.processors import crawl_url, extract_entities

    req = Request(user_url=url)
    print("  -> crawl_url...", end="", flush=True)
    t0 = time.time()
    req = crawl_url.run(req)
    print(f" {time.time() - t0:.1f}s")

    print("  -> extract_entities...", end="", flush=True)
    t0 = time.time()
    req = extract_entities.run(req)
    print(f" {time.time() - t0:.1f}s")

    extracted = req.state["extracted_entities"]
    print(f"\nExtracted: {len(extracted.get('people', []))} people, {len(extracted.get('topics', []))} topics")
    for p in extracted.get("people", [])[:8]:
        print(f"  person: {p['name']} ({p['slug']}) — {p.get('role_hint', '')}")
    for t in extracted.get("topics", [])[:6]:
        print(f"  topic:  {t['name']} ({t['slug']})")

    # Sub-loop: run identify (pre-resolved target) + research + distill for each person.
    for p in extracted.get("people", [])[:8]:
        sub_req = Request(user_goal=f"{p['name']} — {p.get('role_hint', '')}")
        sub_req.state["target"] = {
            "target_kind": "person",
            "person_name_hint": p["name"],
            "person_slug": p["slug"],
            "role_slug": (p.get("role_hint") or "unknown-role").lower().replace(" ", "-")[:60],
            "role_overview": p.get("role_hint", ""),
            "jurisdiction_path": None,
            "jurisdiction_overview": "",
            "domains": [],
            "search_queries": p.get("search_queries", []),
        }
        print(f"\n  ## researching person: {p['name']}")
        sub_req = research.run(sub_req)
        print(f"     sources: {sub_req.state.get('source_count', 0)}  (thin={sub_req.state.get('thin_source')})")
        sub_req = distill.run(sub_req)
        if "person_dir" in sub_req.state:
            print(f"     wrote: {sub_req.state['person_dir']}")
        elif "distill_error" in sub_req.state:
            print(f"     skipped: {sub_req.state['distill_error']}")

    # Topics: same pattern but simpler (no persona)
    # For v2 first cut we skip topic distillation — covered in a later iteration.

    return req


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="user goal text (omit if --url is given)")
    ap.add_argument("--url", help="entry point URL for URL-mode pipeline")
    ap.add_argument("--json", action="store_true", help="dump final state as JSON")
    args = ap.parse_args()

    if args.url:
        req = run_url(args.url)
    elif args.input:
        req = run_goal(args.input)
    else:
        ap.print_help()
        return 2

    print("\n=== Result\n")
    if "person_dir" in req.state:
        print(f"Built person-agent at: {req.state['person_dir']}")
    if "initial_answer" in req.state:
        print("\n--- initial answer ---\n")
        print(req.state["initial_answer"])
    if args.json:
        printable = {k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else repr(v)) for k, v in req.state.items()}
        print("\n--- state ---\n")
        print(json.dumps(printable, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
