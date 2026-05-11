"""CLI: run bare / persona / stuffed / agentic on a person-agent and a query.

Usage:
    uv run python -m scripts.run_comparison \\
        entities/people/mountlake-terrace-permit-office \\
        "do I need a permit for a 60 sq ft deck attached to my house?"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

from dashboard import runners, store

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "runs"
RUNS_DIR.mkdir(exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("person_dir", help="path to entities/people/<slug>/")
    ap.add_argument("query", help="user query")
    ap.add_argument("--model", default="gpt-4o-mini")
    args = ap.parse_args()

    person_dir = Path(args.person_dir).resolve()
    if not (person_dir / "persona.md").exists():
        print(f"error: no persona.md at {person_dir}")
        return 1

    print(f"\nComparing 4 variants on: {person_dir.relative_to(REPO)}")
    print(f"Query: {args.query}\n")

    results: dict[str, dict] = {}
    for name in ("bare", "persona", "stuffed", "agentic"):
        print(f"  -> {name}...", end="", flush=True)
        try:
            r = runners.RUNNERS[name](person_dir, args.query, args.model)
            store.log_run(args.query, r)
            results[name] = r
            print(f" {r['elapsed_s']}s  ({r['prompt_tokens']} prompt + {r['completion_tokens']} completion)")
        except Exception as e:
            print(f" ERR ({e!r})")
            results[name] = {"runner": name, "content": f"ERROR: {e}", "model": args.model, "prompt_tokens": 0, "completion_tokens": 0, "elapsed_s": 0}

    ts = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = RUNS_DIR / f"v2-{person_dir.name}-{ts}.md"
    lines: list[str] = [
        f"# v2 comparison — {ts}",
        "",
        f"**Person-agent**: `{person_dir.relative_to(REPO)}`",
        f"**Query**: {args.query}",
        f"**Model**: {args.model}",
        "",
        "| runner | prompt_tok | completion_tok | elapsed_s |",
        "|---|---:|---:|---:|",
    ]
    for name in ("bare", "persona", "stuffed", "agentic"):
        r = results[name]
        lines.append(f"| {name} | {r.get('prompt_tokens', 0)} | {r.get('completion_tokens', 0)} | {r.get('elapsed_s', 0)} |")
    lines.append("")
    for name in ("bare", "persona", "stuffed", "agentic"):
        lines += [f"## {name}", "", results[name]["content"], "", "---", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
