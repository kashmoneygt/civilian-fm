"""Interactive REPL chat with a person-agent.

Usage:
    uv run python -m scripts.chat entities/people/andrej-karpathy
    uv run python -m scripts.chat entities/people/naval-ravikant --model gpt-4o
    uv run python -m scripts.chat entities/people/karlton-dennis --trace

The agent is always tool-call based (ToolPersonAgent) — there's no longer a
dump-everything alternative. The persona + skills + index of available wiki/
linked entities goes in the system prompt; the model uses read_wiki_file and
read_linked_entity tools to consult sources on demand.

REPL commands: /quit, /reset, /info, /trace (toggle live trace printing)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from entities._agent import ToolPersonAgent

CITATION_RE = re.compile(r"\[\s*source\s*:\s*([^\]]+?)\s*\]|\[\[(?:source|ref)\s*:\s*([^\]]+?)\s*\]\]")


def parse_citations(text: str) -> list[str]:
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
    ap.add_argument("--trace", action="store_true", help="after each response, print tool calls + citations")
    args = ap.parse_args()

    person_dir = Path(args.person_dir).resolve()
    if not (person_dir / "persona.md").exists():
        print(f"error: no persona.md at {person_dir}", file=sys.stderr)
        return 1

    agent = ToolPersonAgent(person_dir, model=args.model)
    show_trace = args.trace

    def info():
        print(f"  name:       {agent.name}")
        print(f"  slug:       {agent.slug}")
        print(f"  model:      {agent.model}")
        print(f"  wiki files: {len(agent._wiki_files)} (lazy-loaded via tools)")
        print(f"  linked:     {len(agent._linked_refs)} entities (lazy-loaded via tools)")
        print(f"  system:     {len(agent.system_prompt):,} chars (just index, content via tools)")

    print(f"\n=== Chat with {agent.name} ({agent.slug}) ===")
    info()
    print(f"\nType your message. Commands: /quit  /reset  /info  /trace\n")

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
        if msg == "/trace":
            show_trace = not show_trace
            print(f"(trace {'on' if show_trace else 'off'})")
            continue
        try:
            response = agent.chat(msg)
        except Exception as e:
            print(f"error: {e}")
            continue
        print(f"\n{agent.name}>\n{response}\n")

        if show_trace:
            print("--- trace ---")
            last = agent.last_trace()
            if last:
                if last.tool_calls:
                    print(f"  tool calls ({len(last.tool_calls)}):")
                    for tc in last.tool_calls:
                        args_str = ", ".join(f"{k}={v!r}" for k, v in tc.args.items())
                        print(f"    -> {tc.name}({args_str}) → {tc.result_chars:,} chars")
                else:
                    print("  (no tool calls — model answered from system prompt / memory)")
                print(f"  total tokens: {last.total_tokens:,}  |  elapsed: {last.elapsed_s}s")
            cites = parse_citations(response)
            print(f"  citations: {cites if cites else '(none)'}")
            print("--- end trace ---\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
