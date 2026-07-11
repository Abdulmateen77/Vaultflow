"""Waitlist lead-capture storage backed by a local SQLite database."""
from __future__ import annotations

import pathlib
import sqlite3
import time

_DB_PATH = pathlib.Path(__file__).parent.parent / "data" / "waitlist.db"


def _get_connection() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS waitlist_leads (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                email     TEXT NOT NULL,
                company   TEXT NOT NULL,
                use_case  TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )


_ensure_table()


def insert_lead(*, name: str, email: str, company: str, use_case: str) -> int:
    """Insert a new lead and return its id."""
    with _get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO waitlist_leads (name, email, company, use_case, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, company, use_case, int(time.time())),
        )
        return cursor.lastrowid  # type: ignore[return-value]


def lead_exists(email: str) -> bool:
    """Return True if this email is already on the waitlist."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM waitlist_leads WHERE email = ? LIMIT 1", (email,)
        ).fetchone()
        return row is not None
