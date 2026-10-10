"""Public references (C-10009, DL-4829137, ...; see db/migrations/004_refs.sql and user/andrey/drafts/naming.md).

One place for: minting a new case id, turning anything a person typed or said into a case id, and the reference to
show or say for a case. Falls back to the pre-004 behaviour when the database hasn't been migrated yet, so this code
is safe to deploy before the migration runs.
"""
from __future__ import annotations

import re
import secrets
from typing import Optional

from . import db

_migrated: Optional[bool] = None


def migrated() -> bool:
    global _migrated
    if not _migrated:   # re-check until true, so a migration applied while the hub runs is picked up
        row = db.one("select to_regprocedure('public.resolve_case(text)') is not null as ok")
        _migrated = bool(row and row["ok"])
    return _migrated


def new_case_id() -> str:
    """Id for a new case. After the migration the id is its own public reference (C-10009)."""
    if migrated():
        return db.one("select public.next_ref('case') as ref")["ref"]
    return f"C-{secrets.token_hex(3).upper()}"


def resolve_case(text: Optional[str]) -> Optional[str]:
    """Case id for a case reference, legacy id, tracking reference or old shipment id; open cases first."""
    ref = (text or "").strip()
    if not ref:
        return None
    if migrated():
        row = db.one("select public.resolve_case(%s) as id", (ref,))
        return row["id"] if row else None
    # Pre-migration: compare on letters and digits only, so "DL 103", "dl-103" and "DL103" are the same reference.
    key = re.sub(r"[^A-Za-z0-9]", "", ref).upper()
    col = "upper(regexp_replace(coalesce({}, ''), '[^A-Za-z0-9]', '', 'g'))"
    row = db.one(f"select id from cases where {col.format('id')} = %s order by updated_at desc limit 1", (key,)) or db.one(
        f"""select c.id from cases c left join shipments s on s.case_id = c.id
            where {col.format('c.shipment_id')} = %s or {col.format('s.id')} = %s
            order by (c.status in ('resolved', 'closed')), c.updated_at desc limit 1""", (key, key))
    return row["id"] if row else None


def case_ref(case_id: str) -> str:
    """The reference to show or read out for a case (its id before the migration)."""
    if migrated():
        row = db.one("select ref from cases where id = %s", (case_id,))
        if row and row["ref"]:
            return row["ref"]
    return case_id
