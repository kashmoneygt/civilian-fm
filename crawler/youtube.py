"""YouTube transcript ingestion. Public API: ingest_url(url) -> Path."""
from __future__ import annotations

import re
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

from .store import write_raw


def _fetch_metadata(url: str) -> dict:
    """Best-effort: get title/uploader/duration via yt-dlp. Returns {} on failure."""
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "duration_seconds": info.get("duration"),
        }
    except Exception:
        return {}


def video_id_from_url(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})", url)
    if not m:
        raise ValueError(f"Could not extract video id from {url}")
    return m.group(1)


def _format_transcript(snippets) -> str:
    """Convert FetchedTranscript snippets into readable markdown."""
    lines = []
    for s in snippets:
        ts = int(s.start)
        mm, ss = divmod(ts, 60)
        hh, mm = divmod(mm, 60)
        stamp = f"[{hh:02d}:{mm:02d}:{ss:02d}]" if hh else f"[{mm:02d}:{ss:02d}]"
        lines.append(f"{stamp} {s.text.strip()}")
    return "\n".join(lines)


def ingest_url(url: str) -> Path:
    vid = video_id_from_url(url)
    api = YouTubeTranscriptApi()
    fetched = api.fetch(vid)
    body = _format_transcript(fetched.snippets)
    meta = _fetch_metadata(url)
    fm = {
        "url": url,
        "video_id": vid,
        "language": getattr(fetched, "language_code", "en"),
        **meta,
    }
    return write_raw("youtube", vid, body, fm)


if __name__ == "__main__":
    import sys

    path = ingest_url(sys.argv[1])
    print(f"wrote {path}")
