"""Postgres access for the hub: one pool, small helpers, and the agent's read-only query path."""
from __future__ import annotations

import re
from typing import Any, Optional

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from .config import settings

_pool: Optional[ConnectionPool] = None


def pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        # prepare_threshold=None: Supabase's transaction pooler can't hold prepared statements.
        _pool = ConnectionPool(settings.database_url, min_size=1, max_size=8, open=True,
                               kwargs={"row_factory": dict_row, "autocommit": True, "prepare_threshold": None})
    return _pool


def query(sql: str, params: Any = None) -> list[dict]:
    with pool().connection() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall() if cur.description else []


def one(sql: str, params: Any = None) -> Optional[dict]:
    rows = query(sql, params)
    return rows[0] if rows else None


def jsonb(value: Any) -> Jsonb:
    return Jsonb(value)


# ------------------------------------------------------------------ agent read path
_ALLOWED_START = re.compile(r"^\s*(select|with|explain)\b", re.I)
_FORBIDDEN = re.compile(r"\b(set|reset|grant|revoke|copy|pg_sleep|dblink|lo_\w+|pg_read\w*|current_setting|set_config)\b", re.I)
MAX_ROWS = 200


class QueryRejected(ValueError):
    pass


def read_only_query(sql: str) -> dict:
    """Run one SELECT for the agent: single statement, read-only transaction, agent_ro role, 5s timeout."""
    stmt = sql.strip().rstrip(";").strip()
    if ";" in stmt:
        raise QueryRejected("one statement only")
    if not _ALLOWED_START.match(stmt):
        raise QueryRejected("only SELECT / WITH / EXPLAIN queries are allowed")
    if _FORBIDDEN.search(stmt):
        raise QueryRejected("query uses a forbidden keyword or function")
    with pool().connection() as conn:
        with conn.transaction():
            conn.execute("set transaction read only")
            conn.execute("set local role agent_ro")
            conn.execute("set local statement_timeout = '5s'")
            cur = conn.execute(stmt)
            rows = cur.fetchmany(MAX_ROWS + 1)
    truncated = len(rows) > MAX_ROWS
    return {"rows": rows[:MAX_ROWS], "row_count": min(len(rows), MAX_ROWS), "truncated": truncated}
