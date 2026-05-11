"""Thin LiteLLM wrapper with JSON-mode helper. Used by processors."""
from __future__ import annotations

import json
import os

import litellm
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("RESEARCHER_MODEL", "gpt-4o-mini")


def complete(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.2, system: str | None = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = litellm.completion(model=model, messages=messages, temperature=temperature)
    return resp.choices[0].message.content.strip()


def complete_json(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.0) -> dict:
    """LLM call that returns parsed JSON. Uses LiteLLM JSON mode."""
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)
