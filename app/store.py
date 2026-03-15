from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Protocol
from uuid import uuid4

from app.models import now_iso


TABLES = (
    "users",
    "customers",
    "assessments",
    "recommendations",
    "reports",
    "followups",
    "compliance_events",
)


class StoreProtocol(Protocol):
    def get(self, table: str, record_id: str) -> dict[str, Any] | None: ...
    def upsert(self, table: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any]: ...
    def list(self, table: str, limit: int | None = None) -> list[dict[str, Any]]: ...
    def audit(self, actor_id: str, action: str, resource: str, resource_id: str, reason: str, after: dict[str, Any]) -> None: ...
    def list_audit(self, limit: int = 100) -> list[dict[str, Any]]: ...


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


class SQLiteStore:
    def __init__(self, db_path: str = "data/nutrition_assistant.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = Lock()
        self._init_schema()

    @staticmethod
    def new_id(prefix: str) -> str:
        return new_id(prefix)

    def _init_schema(self) -> None:
        with self.lock, self.conn:
            for table in TABLES:
                self.conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                      id TEXT PRIMARY KEY,
                      payload TEXT NOT NULL
                    )
                    """
                )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                  id TEXT PRIMARY KEY,
                  actor_id TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  action TEXT NOT NULL,
                  resource TEXT NOT NULL,
                  resource_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  after_snapshot TEXT NOT NULL
                )
                """
            )

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(f"SELECT payload FROM {table} WHERE id = ?", (record_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])

    def upsert(self, table: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload_str = json.dumps(payload, ensure_ascii=True)
        with self.lock, self.conn:
            self.conn.execute(
                f"""
                INSERT INTO {table}(id, payload)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET payload = excluded.payload
                """,
                (record_id, payload_str),
            )
        return payload

    def list(self, table: str, limit: int | None = None) -> list[dict[str, Any]]:
        sql = f"SELECT payload FROM {table} ORDER BY rowid DESC"
        params: tuple[Any, ...] = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        rows = self.conn.execute(sql, params).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def audit(self, actor_id: str, action: str, resource: str, resource_id: str, reason: str, after: dict[str, Any]) -> None:
        with self.lock, self.conn:
            self.conn.execute(
                """
                INSERT INTO audit_logs(id, actor_id, timestamp, action, resource, resource_id, reason, after_snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_id("audit"),
                    actor_id,
                    now_iso(),
                    action,
                    resource,
                    resource_id,
                    reason,
                    json.dumps(after, ensure_ascii=True),
                ),
            )

    def list_audit(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT id, actor_id, timestamp, action, resource, resource_id, reason, after_snapshot
            FROM audit_logs
            ORDER BY rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            out.append(
                {
                    "id": row["id"],
                    "actor_id": row["actor_id"],
                    "timestamp": row["timestamp"],
                    "action": row["action"],
                    "resource": row["resource"],
                    "resource_id": row["resource_id"],
                    "reason": row["reason"],
                    "after_snapshot": json.loads(row["after_snapshot"]),
                }
            )
        return out


class PostgresStore:
    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("psycopg is required for PostgreSQL backend. Install with: pip install psycopg[binary]") from exc

        self.psycopg = psycopg
        self.conn = psycopg.connect(dsn, autocommit=True)
        self.lock = Lock()
        self._init_schema()

    @staticmethod
    def new_id(prefix: str) -> str:
        return new_id(prefix)

    def _init_schema(self) -> None:
        with self.lock, self.conn.cursor() as cur:
            for table in TABLES:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                      id TEXT PRIMARY KEY,
                      payload JSONB NOT NULL
                    );
                    """
                )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                  id TEXT PRIMARY KEY,
                  actor_id TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  action TEXT NOT NULL,
                  resource TEXT NOT NULL,
                  resource_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  after_snapshot JSONB NOT NULL
                );
                """
            )

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT payload FROM {table} WHERE id = %s", (record_id,))
            row = cur.fetchone()
            if not row:
                return None
            payload = row[0]
            return payload if isinstance(payload, dict) else json.loads(payload)

    def upsert(self, table: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock, self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {table}(id, payload)
                VALUES (%s, %s::jsonb)
                ON CONFLICT(id) DO UPDATE SET payload = EXCLUDED.payload
                """,
                (record_id, json.dumps(payload, ensure_ascii=True)),
            )
        return payload

    def list(self, table: str, limit: int | None = None) -> list[dict[str, Any]]:
        sql = f"SELECT payload FROM {table} ORDER BY id DESC"
        params: tuple[Any, ...] = ()
        if limit is not None:
            sql += " LIMIT %s"
            params = (limit,)
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            payload = row[0]
            out.append(payload if isinstance(payload, dict) else json.loads(payload))
        return out

    def audit(self, actor_id: str, action: str, resource: str, resource_id: str, reason: str, after: dict[str, Any]) -> None:
        with self.lock, self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit_logs(id, actor_id, timestamp, action, resource, resource_id, reason, after_snapshot)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    new_id("audit"),
                    actor_id,
                    now_iso(),
                    action,
                    resource,
                    resource_id,
                    reason,
                    json.dumps(after, ensure_ascii=True),
                ),
            )

    def list_audit(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, actor_id, timestamp, action, resource, resource_id, reason, after_snapshot
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            after_snapshot = row[7]
            out.append(
                {
                    "id": row[0],
                    "actor_id": row[1],
                    "timestamp": row[2],
                    "action": row[3],
                    "resource": row[4],
                    "resource_id": row[5],
                    "reason": row[6],
                    "after_snapshot": after_snapshot if isinstance(after_snapshot, dict) else json.loads(after_snapshot),
                }
            )
        return out


def build_store() -> StoreProtocol:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        return PostgresStore(database_url)
    return SQLiteStore()


STORE = build_store()
