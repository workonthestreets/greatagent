"""The v2 investigation endpoints as a router, mounted twice: by the standalone api_v2 app (V2_API_TOKEN auth) and by
the hub under /api/v2 (desk-staff login), so web/ can show the Investigate page without a second service.

Case markdown -> preprocess -> deskagent_v1_1 -> combined run JSON. Stateless: no database."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from deskagent_v1_1 import run_case
from deskagent_v1_1.agent import ROOT

from .cases import list_cases

SPEC = ROOT / "preprocess" / "delivery_classifications_v2_4.json"
CASES = Path(os.environ.get("V2_CASES_DIR") or ROOT / "cases")
SPEC_KEYS = ("meta", "classifications", "routing_rules", "routing_map", "channel_rules")

router = APIRouter()


class RunIn(BaseModel):
    case_md: str
    name: Optional[str] = None
    model: Optional[str] = None


def health() -> dict:
    return {"ok": True, "cases_dir": str(CASES), "samples": len(list(CASES.glob("*.md"))) if CASES.exists() else 0}


@router.get("/spec")
def spec() -> dict:
    full = json.loads(SPEC.read_text())
    return {k: full[k] for k in SPEC_KEYS if k in full}


@router.get("/cases")
def cases() -> list:
    return list_cases(CASES)


@router.post("/cases/{name}/run")
async def run_named(name: str, model: Optional[str] = None) -> dict:
    path = CASES / f"{Path(name).name}.md"
    if not path.is_file():
        raise HTTPException(404, "no such case")
    return await run_in_threadpool(run_case, path.read_text(), path.stem, model)


@router.get("/samples")
def samples() -> list:
    return sorted(p.stem for p in CASES.glob("*.md")) if CASES.exists() else []


@router.get("/samples/{name}")
def sample(name: str) -> dict:
    path = CASES / f"{Path(name).name}.md"
    if not path.is_file():
        raise HTTPException(404, "no such sample")
    return {"name": path.stem, "case_md": path.read_text()}


@router.post("/run")
async def run(req: RunIn) -> dict:
    if not req.case_md.strip():
        raise HTTPException(400, "case_md is empty")
    name = "".join(c for c in (req.name or "case") if c.isalnum() or c in "-_.")[:60] or "case"
    return await run_in_threadpool(run_case, req.case_md, name, req.model)
