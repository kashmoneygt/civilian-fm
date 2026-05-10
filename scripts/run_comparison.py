"""Run the bare/stuffed/agentic comparison from the CLI and write a markdown report.

Usage:
    uv run python -m scripts.run_comparison "<query>" [model]

Writes to runs/<timestamp>.md and logs each run to runs.db.
Designed for autonomous testing without the Streamlit UI.
"""
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

from dashboard import runners, store

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "runs"
RUNS_DIR.mkdir(exist_ok=True)


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: run_comparison.py '<query>' [model]")
        sys.exit(1)
    query = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4o-mini"

    results: dict[str, dict] = {}
    for name in ("bare", "stuffed", "agentic"):
        print(f"-> running {name}...")
        try:
            r = runners.RUNNERS[name](query, model)
            store.log_run(query, r)
            results[name] = r
        except Exception as e:
            results[name] = {"runner": name, "model": model, "content": f"ERROR: {e}", "elapsed_s": 0, "prompt_tokens": 0, "completion_tokens": 0}

    ts = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = RUNS_DIR / f"{ts}.md"
    lines: list[str] = []
    lines.append(f"# Comparison run — {ts}")
    lines.append("")
    lines.append(f"**Query**: {query}")
    lines.append(f"**Model**: {model}")
    lines.append("")
    lines.append("| runner | model | prompt_tok | completion_tok | elapsed_s |")
    lines.append("|---|---|---:|---:|---:|")
    for name in ("bare", "stuffed", "agentic"):
        r = results[name]
        lines.append(
            f"| {name} | {r.get('model','')} | {r.get('prompt_tokens',0)} | "
            f"{r.get('completion_tokens',0)} | {r.get('elapsed_s',0)} |"
        )
    lines.append("")
    for name in ("bare", "stuffed", "agentic"):
        r = results[name]
        lines.append(f"## {name}")
        lines.append("")
        lines.append(r["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
