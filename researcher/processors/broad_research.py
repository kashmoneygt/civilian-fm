"""Pass 1: broad search + crawl based on seed.search_queries.

Writes results to wiki/raw/web/ and records them in req.state["broad_hits"].
Same logic as v2 research.py, but now scoped to a single seed.
"""
from __future__ import annotations

from crawler.web import ingest_url

from ..pipeline import Request
from ..search import search

PER_QUERY = 3
MAX_QUERIES = 6
SKIP_DOMAINS = {"facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com"}


def _interesting(url: str) -> bool:
    return not any(d in url for d in SKIP_DOMAINS)


def run(req: Request) -> Request:
    seed = req.state["seed"]
    queries = seed.search_queries[:MAX_QUERIES]
    if not queries:
        req.state["broad_hits"] = []
        req.state["broad_crawled"] = []
        return req

    seen_urls: set[str] = set()
    crawled: list[dict] = []
    hits: list[dict] = []

    for q in queries:
        try:
            results = search(q, max_results=PER_QUERY * 2)
        except Exception as e:
            hits.append({"query": q, "error": str(e)})
            continue
        kept = []
        for h in results:
            if h.url in seen_urls or not _interesting(h.url):
                continue
            seen_urls.add(h.url)
            kept.append(h)
            if len(kept) >= PER_QUERY:
                break
        hits.append({"query": q, "kept": [(h.title, h.url) for h in kept]})

    for url in seen_urls:
        try:
            path = ingest_url(url)
            crawled.append({"url": url, "raw_path": str(path)})
        except Exception as e:
            crawled.append({"url": url, "error": str(e)})

    successful = [c for c in crawled if "raw_path" in c]
    req.state["broad_hits"] = hits
    req.state["broad_crawled"] = crawled
    req.state["broad_source_count"] = len(successful)
    return req
