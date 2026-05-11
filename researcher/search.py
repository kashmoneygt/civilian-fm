"""Thin wrapper over a search provider. Default: ddgs (free, no key)."""
from __future__ import annotations

from dataclasses import dataclass

from ddgs import DDGS


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str


def search(query: str, max_results: int = 10) -> list[SearchHit]:
    """Web search. Returns ranked hits."""
    out: list[SearchHit] = []
    with DDGS() as ddg:
        for r in ddg.text(query, max_results=max_results):
            out.append(
                SearchHit(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                )
            )
    return out


if __name__ == "__main__":
    import sys

    for h in search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5):
        print(f"- {h.title}\n  {h.url}\n  {h.snippet[:120]}...")
