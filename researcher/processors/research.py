"""Research: search + crawl per the identified target. Adapts to thin-source targets.

For each search query from the identify processor:
  1. ddgs search -> top N results
  2. crawl the top hits via existing crawler/web.py
  3. record URLs in state["sources"]

Source counts feed thin-source adaptation in the distill step (per Appendix A
nuwa adaptation rules).
"""
from __future__ import annotations

from pathlib import Path

from crawler.web import ingest_url

from ..pipeline import Request
from ..search import search

DEFAULT_PER_QUERY = 3
THIN_SOURCE_THRESHOLD = 8  # nuwa: <10 sources = thin
SKIP_DOMAINS = {"facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com"}  # auth-walled / blocked


def _interesting(url: str) -> bool:
    return not any(d in url for d in SKIP_DOMAINS)


def run(req: Request) -> Request:
    target = req.state.get("target", {})
    queries = target.get("search_queries", [])
    if not queries:
        req.state["sources"] = []
        req.state["thin_source"] = True
        return req

    sources: list[dict] = []
    seen_urls: set[str] = set()
    for q in queries[:6]:
        try:
            hits = search(q, max_results=DEFAULT_PER_QUERY * 2)
        except Exception as e:
            sources.append({"query": q, "error": str(e), "hits": []})
            continue
        kept = []
        for h in hits:
            if h.url in seen_urls or not _interesting(h.url):
                continue
            seen_urls.add(h.url)
            kept.append(h)
            if len(kept) >= DEFAULT_PER_QUERY:
                break
        sources.append({"query": q, "hits": [{"title": h.title, "url": h.url, "snippet": h.snippet} for h in kept]})

    # Crawl the unique URLs we found
    crawled: list[dict] = []
    for url in seen_urls:
        try:
            path = ingest_url(url)
            crawled.append({"url": url, "raw_path": str(path)})
        except Exception as e:
            crawled.append({"url": url, "error": str(e)})

    req.state["sources"] = sources
    req.state["crawled"] = crawled
    successful_crawls = [c for c in crawled if "raw_path" in c]
    req.state["source_count"] = len(successful_crawls)
    req.state["thin_source"] = len(successful_crawls) < THIN_SOURCE_THRESHOLD
    return req
