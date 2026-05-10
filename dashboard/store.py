"""SQLite run log. Every comparison stored for later analysis."""
from __future__ import annotations

import datetime as _dt
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "runs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    query TEXT NOT NULL,
    runner TEXT NOT NULL,
    model TEXT NOT NULL,
    content TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    elapsed_s REAL,
    score INTEGER,
    notes TEXT
);
"""


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_SCHEMA)
    return conn


def log_run(query: str, result: dict) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO runs (created_at, query, runner, model, content, prompt_tokens, completion_tokens, elapsed_s) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                query,
                result["runner"],
                result["model"],
                result["content"],
                result.get("prompt_tokens"),
                result.get("completion_tokens"),
                result.get("elapsed_s"),
            ),
        )
        return cur.lastrowid


def update_score(run_id: int, score: int, notes: str = "") -> None:
    with _conn() as c:
        c.execute("UPDATE runs SET score=?, notes=? WHERE id=?", (score, notes, run_id))


def all_runs() -> list[dict]:
    with _conn() as c:
        c.row_factory = sqlite3.Row
        return [dict(r) for r in c.execute("SELECT * FROM runs ORDER BY id DESC")]
