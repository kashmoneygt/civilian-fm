"""Pass 2: targeted search + crawl based on canonical sources discovered in refine_subject."""
from __future__ import annotations

from crawler.web import ingest_url

from ..pipeline import Request
from ..search import search

PER_QUERY = 3
PER_DOMAIN = 2  # how many results to pull per canonical domain
SKIP_DOMAINS = {"facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com"}


def _interesting(url: str) -> bool:
    return not any(d in url for d in SKIP_DOMAINS)


def run(req: Request) -> Request:
    refine = req.state.get("refine", {})
    canonical = refine.get("canonical_sources", [])
    targeted_queries = refine.get("targeted_queries", [])

    # The URLs we already crawled in broad pass — skip duplicates.
    seen_urls: set[str] = {c["url"] for c in req.state.get("broad_crawled", []) if "url" in c}

    # 1) Targeted searches.
    for q in targeted_queries[:6]:
        try:
            results = search(q, max_results=PER_QUERY * 2)
        except Exception:
            continue
        for h in results[:PER_QUERY]:
            if h.url in seen_urls or not _interesting(h.url):
                continue
            seen_urls.add(h.url)

    # 2) Canonical-source biased searches — search "<source>" if it's a domain.
    for src in canonical[:5]:
        try:
            # If a URL was given, just crawl directly.
            if src.startswith("http"):
                if src in seen_urls:
                    continue
                seen_urls.add(src)
                continue
            # Otherwise treat as a domain/site name; use a site-restricted search.
            site_q = f'"{req.state["seed"].name}" site:{src}'
            results = search(site_q, max_results=PER_DOMAIN * 2)
            for h in results[:PER_DOMAIN]:
                if h.url in seen_urls or not _interesting(h.url):
                    continue
                seen_urls.add(h.url)
        except Exception:
            continue

    # Crawl any NEW URLs (excluding broad-pass ones).
    broad_urls = {c["url"] for c in req.state.get("broad_crawled", []) if "url" in c}
    new_urls = seen_urls - broad_urls
    crawled: list[dict] = []
    for url in new_urls:
        try:
            path = ingest_url(url)
            crawled.append({"url": url, "raw_path": str(path)})
        except Exception as e:
            crawled.append({"url": url, "error": str(e)})

    successful = [c for c in crawled if "raw_path" in c]
    req.state["targeted_crawled"] = crawled
    req.state["targeted_source_count"] = len(successful)

    # Merge broad + targeted into a single "all_crawled" list distill can consume.
    req.state["all_crawled"] = req.state.get("broad_crawled", []) + crawled
    return req
