"""Web tools used by the bare_search runner.

Same DDGS wrapper as researcher/search.py + a simple fetch_url tool.
Exposed in OpenAI/LiteLLM function-calling format.
"""
from __future__ import annotations

import json
from typing import Any

import requests

from researcher.search import search as ddgs_search

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
FETCH_BUDGET_CHARS = 12_000


WEB_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web (DuckDuckGo) for a query. Returns title, url, and snippet for each result. Use this to find sources before answering questions where current or specific information matters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "the search query"},
                    "max_results": {"type": "integer", "description": "max results to return (1-10)", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the text content of a URL. Use after web_search to read the contents of a result that looks relevant.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "URL to fetch"}},
                "required": ["url"],
            },
        },
    },
]


def dispatch(name: str, args: dict) -> str:
    if name == "web_search":
        try:
            hits = ddgs_search(args["query"], max_results=int(args.get("max_results", 5)))
        except Exception as e:
            return f"ERROR: {e}"
        return json.dumps(
            [{"title": h.title, "url": h.url, "snippet": h.snippet} for h in hits],
            indent=2,
        )
    if name == "fetch_url":
        try:
            r = requests.get(args["url"], headers={"User-Agent": UA}, timeout=15)
            r.raise_for_status()
            # Strip HTML lightly — keep text content.
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            if len(text) > FETCH_BUDGET_CHARS:
                text = text[:FETCH_BUDGET_CHARS] + f"\n[... truncated at {FETCH_BUDGET_CHARS} chars]"
            return text
        except Exception as e:
            return f"ERROR: {e}"
    return f"ERROR: unknown tool {name}"
