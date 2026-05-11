"""Pass 1.5: read the broad crawl results, identify the subject's CANONICAL sources.

The intelligent-crawling moat: instead of taking whatever random pages
the broad search returned, read them, figure out where the subject actually
publishes (their site, their books, their podcast, their YouTube channel),
and emit targeted queries that will deepen on THOSE primary sources.
"""
from __future__ import annotations

from pathlib import Path

from ..llm import complete_json
from ..pipeline import Request

PER_SOURCE_CHARS = 6_000
TOTAL_CHARS = 60_000

PROMPT = """You're researching {kind}: {name} ({role_hint}). The user's goal: {origin_goal!r}.

# Broad-search crawl results (snippets and pages we already pulled)

{pages}

# Task

Identify this subject's CANONICAL primary sources — places where THEY publish their own thinking, not third-party mentions. Then produce targeted search queries that will deepen our knowledge of how *they specifically* think about the user's goal.

Return JSON:

{{
  "primary_subject_confirmed": true|false,
  "canonical_sources": [
    "<URL or domain — their site, their blog, their book page, their podcast page, their YouTube channel, etc. Order by authority (most authoritative first).>"
  ],
  "targeted_queries": [
    "<3-5 specific queries that would deepen on THIS subject's actual voice/views. Examples for Karpathy: 'karpathy nanoGPT explanation', 'karpathy software 2.0 essay', 'karpathy zero to hero series'. Examples for Tom Wheelwright: 'tom wheelwright cash balance plan podcast', 'tom wheelwright tax-free wealth book key strategies', 'wealthability.com cost segregation'.>"
  ],
  "notes": "<one sentence: what we learned from the broad pass that informs the targeted pass>"
}}

Rules:
- Prefer first-party domains over third-party blogs.
- If broad-pass yielded mostly third-party mentions (Wikipedia, news articles), explicitly include `site:<their-domain>` style search queries.
- Skip queries that would just return more third-party summaries."""


def _build_pages_block(crawled: list[dict]) -> str:
    chunks: list[str] = []
    total = 0
    for c in crawled:
        if "raw_path" not in c:
            continue
        path = Path(c["raw_path"])
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if len(text) > PER_SOURCE_CHARS:
            text = text[:PER_SOURCE_CHARS] + f"\n[...truncated]"
        chunks.append(f"### {path.name} ({c['url']})\n\n{text}")
        total += len(text)
        if total > TOTAL_CHARS:
            break
    return "\n\n---\n\n".join(chunks)


def run(req: Request) -> Request:
    seed = req.state["seed"]
    broad = req.state.get("broad_crawled", [])
    pages_block = _build_pages_block(broad)
    if not pages_block:
        req.state["refine"] = {"primary_subject_confirmed": False, "canonical_sources": [], "targeted_queries": [], "notes": "no broad crawls"}
        return req

    out = complete_json(
        PROMPT.format(
            kind=seed.kind,
            name=seed.name,
            role_hint=seed.role_hint or "(no role hint)",
            origin_goal=seed.origin_goal or seed.origin_url or "(none)",
            pages=pages_block,
        ),
        temperature=0.0,
    )
    req.state["refine"] = out
    return req
