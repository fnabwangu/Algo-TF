from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from threading import RLock


class Database:
    """Small transactional SQLite store for immutable operational documents."""

    def __init__(self, url: str = "sqlite:///:memory:") -> None:
        if not url.startswith("sqlite:///"):
            raise ValueError("only sqlite database URLs are supported")
        location = url.removeprefix("sqlite:///")
        if location != ":memory:":
            Path(location).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(location, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        with self._connection:
            self._connection.execute(
                """
				CREATE TABLE IF NOT EXISTS documents (
					collection TEXT NOT NULL,
					document_id TEXT NOT NULL,
					parent_id TEXT,
					payload TEXT NOT NULL,
					PRIMARY KEY (collection, document_id)
				)
				"""
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS documents_parent ON documents(collection, parent_id)"
            )

    def upsert(
        self,
        collection: str,
        document_id: str,
        payload: dict[str, object],
        parent_id: str | None = None,
    ) -> dict[str, object]:
        encoded = json.dumps(payload, default=str, sort_keys=True, separators=(",", ":"))
        with self._lock, self._connection:
            self._connection.execute(
                """
				INSERT INTO documents(collection, document_id, parent_id, payload)
				VALUES (?, ?, ?, ?)
				ON CONFLICT(collection, document_id) DO UPDATE SET
					parent_id = excluded.parent_id, payload = excluded.payload
				""",
                (collection, document_id, parent_id, encoded),
            )
        return payload

    def get(self, collection: str, document_id: str) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT payload FROM documents WHERE collection = ? AND document_id = ?",
                (collection, document_id),
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def list(self, collection: str, parent_id: str | None = None) -> list[dict[str, object]]:
        query = "SELECT payload FROM documents WHERE collection = ?"
        parameters: Iterable[object] = (collection,)
        if parent_id is not None:
            query += " AND parent_id = ?"
            parameters = (collection, parent_id)
        query += " ORDER BY rowid"
        with self._lock:
            rows = self._connection.execute(query, tuple(parameters)).fetchall()
        return [json.loads(row["payload"]) for row in rows]
