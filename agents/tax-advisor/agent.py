"""Tax-advisor agentic container.

Loads personality + skills + globbed wiki topics into a system prompt and runs a query.

Usage: uv run python -m agents.tax-advisor.agent "<query>"
"""
from __future__ import annotations

import os
import sys
from glob import glob
from pathlib import Path

import litellm
from dotenv import load_dotenv

load_dotenv()

REPO = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_wiki(globs_file: Path) -> str:
    patterns = [line.strip() for line in _read(globs_file).splitlines() if line.strip() and not line.startswith("#")]
    files: list[Path] = []
    for pat in patterns:
        files.extend(Path(p) for p in glob(str(REPO / pat), recursive=True))
    files = sorted(set(files))
    chunks = []
    for f in files:
        rel = f.relative_to(REPO)
        chunks.append(f"### {rel}\n\n{_read(f)}")
    return "\n\n---\n\n".join(chunks)


def build_system_prompt() -> str:
    persona = _read(HERE / "personality.md")
    skills = _read(HERE / "skills.md")
    wiki = _load_wiki(HERE / "wiki_glob.txt")
    return (
        f"{persona}\n\n---\n\n{skills}\n\n---\n\n"
        f"## WIKI (your authoritative source — cite by topic path)\n\n{wiki}"
    )


def run(query: str, model: str = DEFAULT_MODEL) -> dict:
    system = build_system_prompt()
    resp = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        temperature=0.2,
    )
    return {
        "content": resp.choices[0].message.content,
        "model": resp.model,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: agent.py '<query>'")
        sys.exit(1)
    out = run(sys.argv[1])
    print(out["content"])
    print(f"\n\n[model={out['model']} prompt_tokens={out['prompt_tokens']} completion_tokens={out['completion_tokens']}]")
