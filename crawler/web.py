"""Static web page ingestion. Fetches HTML, extracts main text as markdown."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .store import slugify, write_raw

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"


def _html_to_markdown(html: str) -> tuple[str, str | None]:
    """Returns (text, title). Strips scripts/styles/nav/footer, preserves headings + paragraphs."""
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "form", "svg"]):
        tag.decompose()

    body = soup.body or soup
    parts: list[str] = []
    for el in body.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = el.get_text(separator=" ", strip=True)
        if not text or len(text) < 3:
            continue
        if el.name == "h1":
            parts.append(f"# {text}")
        elif el.name == "h2":
            parts.append(f"## {text}")
        elif el.name == "h3":
            parts.append(f"### {text}")
        elif el.name == "h4":
            parts.append(f"#### {text}")
        elif el.name == "li":
            parts.append(f"- {text}")
        else:
            parts.append(text)
    return "\n\n".join(parts), title


def ingest_url(url: str, slug: str | None = None) -> Path:
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    body, title = _html_to_markdown(r.text)
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    if slug is None:
        path_slug = slugify(parsed.path or "root")
        slug = f"{slugify(domain)}--{path_slug}"
    fm = {"url": url, "title": title, "domain": domain}
    return write_raw("web", slug, body, fm)


if __name__ == "__main__":
    import sys

    print(ingest_url(sys.argv[1]))
