"""Interactive REPL chat with a person-agent.

Usage:
    uv run python -m scripts.chat entities/people/andrej-karpathy
    uv run python -m scripts.chat entities/people/karlton-dennis --model gpt-4o

In the REPL: type a message and hit enter. Empty line is ignored.
Commands:  /quit, /reset, /info
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from entities._base import PersonAgent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("person_dir", help="path to entities/people/<slug>/")
    ap.add_argument("--model", default="gpt-4o-mini")
    args = ap.parse_args()

    person_dir = Path(args.person_dir).resolve()
    if not (person_dir / "persona.md").exists():
        print(f"error: no persona.md at {person_dir}", file=sys.stderr)
        return 1

    agent = PersonAgent(person_dir, model=args.model)

    def info():
        print(f"  name:       {agent.name}")
        print(f"  slug:       {agent.slug}")
        print(f"  model:      {agent.model}")
        print(f"  persona:    {len(agent.persona):>7,} chars")
        print(f"  own wiki:   {len(agent.own_wiki):>7,} chars")
        print(f"  linked:     {len(agent.linked)} entities ({', '.join(agent.linked) or 'none'})")
        print(f"  system:     {len(agent.system_prompt):>7,} chars total")

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

    return 0


if __name__ == "__main__":
    sys.exit(main())
