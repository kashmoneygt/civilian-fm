"""Crawl a URL provided as an entry point (URL pipeline)."""
from __future__ import annotations

from pathlib import Path

from crawler.web import ingest_url as ingest_web
from crawler.youtube import ingest_url as ingest_youtube

from ..pipeline import Request


def run(req: Request) -> Request:
    url = req.user_url
    if not url:
        return req

    if "youtube.com" in url or "youtu.be" in url:
        path = ingest_youtube(url)
    else:
        path = ingest_web(url)
    raw = Path(path).read_text(encoding="utf-8")
    req.state["raw_path"] = str(path)
    req.state["raw_content"] = raw
    return req
