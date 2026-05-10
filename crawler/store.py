"""Write crawled raw documents to wiki/raw/<source>/<slug>.md with YAML frontmatter."""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "wiki" / "raw"


def slugify(text: str, max_len: int = 80) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "untitled"


def write_raw(source: str, slug: str, body: str, frontmatter: dict[str, Any]) -> Path:
    """Write a raw document. `source` is youtube/web/etc. Returns the file path."""
    fm = {"source": source, "fetched_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", **frontmatter}
    out_dir = RAW_DIR / source
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.md"
    yaml_block = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{yaml_block}\n---\n\n{body.strip()}\n", encoding="utf-8")
    return path
