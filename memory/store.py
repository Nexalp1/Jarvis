from __future__ import annotations

import sqlite3
from pathlib import Path


class MemoryStore:
    def __init__(self, sqlite_path: str) -> None:
        self.path = Path(sqlite_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS engineering_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                approved INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def save_interaction(self, role: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO interactions(role, message) VALUES(?, ?)",
            (role, message),
        )
        self.conn.commit()

    def recent_context(self, limit: int = 6) -> list[tuple[str, str]]:
        cur = self.conn.execute(
            "SELECT role, message FROM interactions ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return list(reversed(cur.fetchall()))

    def save_engineering_action(self, action: str, details: str, approved: bool) -> None:
        self.conn.execute(
            "INSERT INTO engineering_history(action, details, approved) VALUES(?, ?, ?)",
            (action, details, int(approved)),
        )
        self.conn.commit()
