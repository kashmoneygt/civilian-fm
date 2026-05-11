"""Interactive REPL chat with a person-agent.

Usage:
    uv run python -m scripts.chat entities/people/andrej-karpathy
    uv run python -m scripts.chat entities/people/karlton-dennis --model gpt-4o
    uv run python -m scripts.chat entities/people/naval-ravikant --tools --trace

Modes:
    (default) PersonAgent — dumps everything into the system prompt, one LLM call.
    --tools   ToolPersonAgent — exposes wiki/linked entities as tool calls, model
              decides what to read. Observable: see which refs got loaded per turn.

Flags:
    --trace   After each response, print which tool calls were made (only with --tools)
              AND which `[source:]` citations appeared in the response (both modes).

In the REPL: type a message and hit enter. Empty line is ignored.
Commands:  /quit, /reset, /info
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from entities._base import PersonAgent
from entities._tool_agent import ToolPersonAgent

CITATION_RE = re.compile(r"\[\s*source\s*:\s*([^\]]+?)\s*\]|\[\[(?:source|ref)\s*:\s*([^\]]+?)\s*\]\]")


def parse_citations(text: str) -> list[str]:
    """Pull `[source: foo.md]` and `[[source: foo.md]]` citations out of a response."""
    out: list[str] = []
    for m in CITATION_RE.finditer(text):
        cite = (m.group(1) or m.group(2) or "").strip()
        if cite and cite not in out:
            out.append(cite)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("person_dir", help="path to entities/people/<slug>/")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--tools", action="store_true", help="use ToolPersonAgent (tool-call observability)")
    ap.add_argument("--trace", action="store_true", help="after each response, show tool calls + citation analysis")
    args = ap.parse_args()

    person_dir = Path(args.person_dir).resolve()
    if not (person_dir / "persona.md").exists():
        print(f"error: no persona.md at {person_dir}", file=sys.stderr)
        return 1

    if args.tools:
        agent = ToolPersonAgent(person_dir, model=args.model)
        mode = "tools"
    else:
        agent = PersonAgent(person_dir, model=args.model)
        mode = "dump"

    def info():
        print(f"  name:       {agent.name}")
        print(f"  slug:       {agent.slug}")
        print(f"  model:      {agent.model}")
        print(f"  mode:       {mode}")
        if mode == "dump":
            print(f"  persona:    {len(agent.persona):>7,} chars")
            print(f"  own wiki:   {len(agent.own_wiki):>7,} chars")
            print(f"  linked:     {len(agent.linked)} entities ({', '.join(agent.linked) or 'none'})")
            print(f"  system:     {len(agent.system_prompt):>7,} chars total (loaded up-front)")
        else:
            print(f"  wiki files: {len(agent._wiki_files)} (lazy-loaded via tools)")
            print(f"  linked:     {len(agent._linked_refs)} entities (lazy-loaded via tools)")
            print(f"  system:     {len(agent.system_prompt):>7,} chars (just index, content via tools)")

    print(f"\n=== Chat with {agent.name} ({agent.slug}) ===")
    info()
    print(f"\nType your message. Commands: /quit  /reset  /info\n")

    while True:
        try:
            msg = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not msg:
            continue
        if msg == "/quit":
            break
        if msg == "/reset":
            agent.reset()
            print("(history cleared)")
            continue
        if msg == "/info":
            info()
            continue
        try:
            response = agent.chat(msg)
        except Exception as e:
            print(f"error: {e}")
            continue
        print(f"\n{agent.name}>\n{response}\n")

        if args.trace:
            print("--- trace ---")
            if mode == "tools":
                last = agent.last_trace()
                if last:
                    if last.tool_calls:
                        print(f"  tool calls ({len(last.tool_calls)}):")
                        for tc in last.tool_calls:
                            args_str = ", ".join(f"{k}={v!r}" for k, v in tc.args.items())
                            print(f"    -> {tc.name}({args_str}) → {tc.result_chars:,} chars")
                            print(f"       preview: {tc.result_preview[:120]}...")
                    else:
                        print("  (no tool calls — model answered from system prompt / memory alone)")
                    print(f"  total tokens: {last.total_tokens:,}  |  elapsed: {last.elapsed_s}s")
            cites = parse_citations(response)
            if cites:
                print(f"  citations in response ({len(cites)}):")
                for c in cites:
                    print(f"    - {c}")
            else:
                print("  citations in response: (none)")
            print("--- end trace ---\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
