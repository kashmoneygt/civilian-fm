"""Four runners for variant comparison. Each takes a person-agent directory
and a user query, returns {content, model, prompt_tokens, completion_tokens, elapsed_s, runner}.

Variants (per PLAN.md Section 2.6):
- bare:    no system prompt, no wiki. Mean-of-internet baseline.
- persona: persona.md body only. No wiki, no linked entities. Isolates persona effect.
- stuffed: generic "be helpful" system + entire wiki (own + linked) dumped in.
- agentic: full PersonAgent (persona + skills + own wiki + resolved cross-refs).
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv

from entities._base import PersonAgent
from entities._refs import (
    load_entity_content,
    parse_frontmatter,
    refs_in_body,
    refs_in_frontmatter,
)

load_dotenv()

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")


def _completion(messages: list[dict], model: str) -> dict:
    t0 = time.time()
    resp = litellm.completion(model=model, messages=messages, temperature=0.3)
    return {
        "content": resp.choices[0].message.content,
        "model": resp.model,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "elapsed_s": round(time.time() - t0, 2),
    }


def _load_own_wiki(person_dir: Path) -> str:
    wiki_dir = person_dir / "wiki"
    if not wiki_dir.exists():
        return ""
    chunks = []
    for f in sorted(wiki_dir.rglob("*.md")):
        chunks.append(f"### {f.relative_to(person_dir)}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(chunks)


def run_bare(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    return _completion([{"role": "user", "content": query}], model) | {"runner": "bare"}


def run_persona(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    persona = (person_dir / "persona.md").read_text(encoding="utf-8")
    fm, body = parse_frontmatter(persona)
    name = fm.get("name", person_dir.name)
    system = f"You are {name}. Respond in first person.\n\n{body}"
    return _completion(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        model,
    ) | {"runner": "persona"}


def run_stuffed(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    persona = (person_dir / "persona.md").read_text(encoding="utf-8")
    fm, body = parse_frontmatter(persona)
    own_wiki = _load_own_wiki(person_dir)
    linked_parts = []
    for ref in list({*refs_in_frontmatter(fm), *refs_in_body(body)}):
        content = load_entity_content(ref)
        if content:
            linked_parts.append(f"## Linked: [[{ref.kind}:{ref.slug}]]\n\n{content}")
    linked = "\n\n---\n\n".join(linked_parts)

    system = (
        "You are a helpful assistant. Below is a knowledge base. "
        "Use it when answering. Cite the source filenames you draw on.\n\n"
        f"## OWN WIKI\n\n{own_wiki}\n\n## LINKED ENTITIES\n\n{linked}"
    )
    return _completion(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        model,
    ) | {"runner": "stuffed"}


def run_agentic(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    t0 = time.time()
    agent = PersonAgent(person_dir, model=model)
    # Match other runners' shape by going through litellm directly so we capture usage stats.
    resp = litellm.completion(
        model=model,
        messages=[{"role": "system", "content": agent.system_prompt}, {"role": "user", "content": query}],
        temperature=0.3,
    )
    return {
        "content": resp.choices[0].message.content,
        "model": resp.model,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "elapsed_s": round(time.time() - t0, 2),
        "runner": "agentic",
    }


RUNNERS = {
    "bare": run_bare,
    "persona": run_persona,
    "stuffed": run_stuffed,
    "agentic": run_agentic,
}
