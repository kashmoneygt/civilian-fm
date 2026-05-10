"""Three runners for the comparison dashboard.

- bare: no system prompt. The "mean of the internet" baseline.
- stuffed: the entire wiki/topics/ corpus dumped into the system prompt. The "too much context" baseline.
- agentic: the tax-advisor agentic container — persona + skills + scoped wiki glob.

All three accept a user query and a LiteLLM model id, return the same dict shape.
"""
from __future__ import annotations

import importlib.util
import os
import time
from glob import glob
from pathlib import Path

import litellm
from dotenv import load_dotenv

load_dotenv()

REPO = Path(__file__).resolve().parent.parent
TOPICS_DIR = REPO / "wiki" / "topics"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _full_wiki_dump() -> str:
    files = sorted(TOPICS_DIR.rglob("*.md"))
    return "\n\n---\n\n".join(f"### {f.relative_to(REPO)}\n\n{_read(f)}" for f in files)


def _completion(messages: list[dict], model: str) -> dict:
    t0 = time.time()
    resp = litellm.completion(model=model, messages=messages, temperature=0.2)
    elapsed = time.time() - t0
    return {
        "content": resp.choices[0].message.content,
        "model": resp.model,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "elapsed_s": round(elapsed, 2),
    }


def run_bare(query: str, model: str = "gpt-4o-mini") -> dict:
    """Just the user query. No system prompt. Mean-of-the-internet baseline."""
    return _completion([{"role": "user", "content": query}], model) | {"runner": "bare"}


def run_stuffed(query: str, model: str = "gpt-4o-mini") -> dict:
    """Entire wiki dumped into the system prompt. The 'too much context' baseline."""
    system = (
        "You are a helpful assistant. Below is a knowledge base of tax topics. "
        "Use it when answering. Cite sources by file path when you do.\n\n"
        f"## KNOWLEDGE BASE\n\n{_full_wiki_dump()}"
    )
    return _completion(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        model,
    ) | {"runner": "stuffed"}


def run_agentic(query: str, model: str = "gpt-4o-mini") -> dict:
    """The tax-advisor agentic container — curated personality + skills + scoped wiki glob."""
    spec = importlib.util.spec_from_file_location("tax_advisor_agent", REPO / "agents" / "tax-advisor" / "agent.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    system = mod.build_system_prompt()
    return _completion(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        model,
    ) | {"runner": "agentic"}


RUNNERS = {"bare": run_bare, "stuffed": run_stuffed, "agentic": run_agentic}


if __name__ == "__main__":
    import json
    import sys

    runner_name = sys.argv[1]
    query = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o-mini"
    print(json.dumps(RUNNERS[runner_name](query, model), indent=2))
