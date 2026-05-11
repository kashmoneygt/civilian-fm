"""Four variant runners for the comparison harness (v3).

The four variants represent four real-world alternatives the user could pick:

- bare:        "What if I just ask ChatGPT?"          (no system prompt, no tools)
- bare_search: "What if I just ask Perplexity?"       (web_search + fetch_url tools, no persona)
- persona:    "What if the model knew the right voice?" (persona only, no wiki, no tools)
- agentic:    Our actual product — ToolPersonAgent with curated-wiki tools.

Each returns {content, model, prompt_tokens, completion_tokens, elapsed_s, runner, trace}.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv

from entities._agent import ToolPersonAgent
from entities._refs import parse_frontmatter

from . import web_tools

load_dotenv()

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")
MAX_TOOL_TURNS = 6


def _tool_loop(messages: list[dict], tools: list[dict], dispatcher, model: str) -> dict:
    """Run a tool-calling loop until the model stops requesting tools.

    Returns {content, prompt_tokens, completion_tokens, elapsed_s, trace, model}.
    """
    t0 = time.time()
    trace: list[dict] = []
    total_prompt = 0
    total_completion = 0

    msgs = list(messages)
    for _ in range(MAX_TOOL_TURNS):
        resp = litellm.completion(model=model, messages=msgs, tools=tools, temperature=0.3)
        choice = resp.choices[0]
        msg = choice.message
        msgs.append(msg.model_dump(exclude_none=True))
        total_prompt += resp.usage.prompt_tokens
        total_completion += resp.usage.completion_tokens

        if not msg.tool_calls:
            return {
                "content": msg.content or "",
                "prompt_tokens": total_prompt,
                "completion_tokens": total_completion,
                "elapsed_s": round(time.time() - t0, 2),
                "trace": trace,
                "model": resp.model,
            }

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}
            result = dispatcher(tc.function.name, args)
            trace.append({
                "name": tc.function.name,
                "args": args,
                "result_chars": len(result),
                "result_preview": result[:200].replace("\n", " "),
            })
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return {
        "content": "(tool turn limit hit)",
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "elapsed_s": round(time.time() - t0, 2),
        "trace": trace,
        "model": model,
    }


def _no_tools_completion(messages: list[dict], model: str) -> dict:
    t0 = time.time()
    resp = litellm.completion(model=model, messages=messages, temperature=0.3)
    return {
        "content": resp.choices[0].message.content,
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "elapsed_s": round(time.time() - t0, 2),
        "trace": [],
        "model": resp.model,
    }


# --- Variants ---


def run_bare(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    """Plain LLM call. The 'what if I just ask ChatGPT?' baseline."""
    return _no_tools_completion([{"role": "user", "content": query}], model) | {"runner": "bare"}


def run_bare_search(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    """LLM + web_search + fetch_url tools. The 'what if I just ask Perplexity?' baseline.

    No persona, no curated wiki — just a generic agent with web access.
    """
    system = (
        "You are a helpful assistant with access to web search and URL fetching tools. "
        "When the user's question would benefit from current or specific information, "
        "use web_search to find sources, then fetch_url to read the most promising hits. "
        "Cite sources by URL in your final answer."
    )
    result = _tool_loop(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        web_tools.WEB_TOOLS,
        web_tools.dispatch,
        model,
    )
    return result | {"runner": "bare_search"}


def run_persona(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    """Persona body only. No wiki, no linked entities, no tools.

    Tests: how much does the persona alone (voice/framework instruction) move the needle?
    """
    persona = (person_dir / "persona.md").read_text(encoding="utf-8")
    fm, body = parse_frontmatter(persona)
    name = fm.get("name", person_dir.name)
    system = f"You are {name}. Respond in first person, in your own voice.\n\n{body}"
    return _no_tools_completion(
        [{"role": "system", "content": system}, {"role": "user", "content": query}],
        model,
    ) | {"runner": "persona"}


def run_agentic(person_dir: Path, query: str, model: str = DEFAULT_MODEL) -> dict:
    """Full product: ToolPersonAgent. Persona + skills + wiki tools + linked-entity tools."""
    agent = ToolPersonAgent(person_dir, model=model)
    content = agent.chat(query)
    last = agent.last_trace()
    return {
        "content": content,
        "model": agent.model,
        "prompt_tokens": last.total_tokens if last else 0,
        "completion_tokens": 0,  # ToolPersonAgent currently aggregates total
        "elapsed_s": last.elapsed_s if last else 0,
        "trace": [
            {"name": tc.name, "args": tc.args, "result_chars": tc.result_chars, "result_preview": tc.result_preview}
            for tc in (last.tool_calls if last else [])
        ],
        "runner": "agentic",
    }


RUNNERS = {
    "bare": run_bare,
    "bare_search": run_bare_search,
    "persona": run_persona,
    "agentic": run_agentic,
}
