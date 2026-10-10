"""Stateless API for web_v2: case markdown -> preprocess -> deskagent_v1_1 -> combined run JSON. No database, no login.

    uvicorn api_v2.app:app --port 8100
Set V2_API_TOKEN to require `Authorization: Bearer <token>` on /api/v2 (recommended if the port is exposed)."""
from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from deskagent_v1_1 import run_case
from .cases import list_cases
from deskagent_v1_1.agent import ROOT

SPEC = ROOT / "preprocess" / "delivery_classifications_v2_4.json"
CASES = Path(os.environ.get("V2_CASES_DIR") or ROOT / "cases")
SPEC_KEYS = ("meta", "classifications", "routing_rules", "routing_map", "channel_rules")

app = FastAPI(title="greatagent v2 api")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def auth(authorization: Optional[str] = Header(None)) -> None:
    token = os.environ.get("V2_API_TOKEN")
    if token and not secrets.compare_digest(authorization or "", f"Bearer {token}"):
        raise HTTPException(401, "unauthorized")


class RunIn(BaseModel):
    case_md: str
    name: Optional[str] = None
    model: Optional[str] = None


@app.get("/api/v2/health")
def health() -> dict:
    return {"ok": True, "cases_dir": str(CASES), "samples": len(list(CASES.glob("*.md"))) if CASES.exists() else 0}


@app.get("/api/v2/spec", dependencies=[Depends(auth)])
def spec() -> dict:
    full = json.loads(SPEC.read_text())
    return {k: full[k] for k in SPEC_KEYS if k in full}


@app.get("/api/v2/cases", dependencies=[Depends(auth)])
def cases() -> list:
    return list_cases(CASES)


@app.post("/api/v2/cases/{name}/run", dependencies=[Depends(auth)])
async def run_named(name: str, model: Optional[str] = None) -> dict:
    path = CASES / f"{Path(name).name}.md"
    if not path.is_file():
        raise HTTPException(404, "no such case")
    return await run_in_threadpool(run_case, path.read_text(), path.stem, model)


@app.get("/api/v2/samples", dependencies=[Depends(auth)])
def samples() -> list:
    return sorted(p.stem for p in CASES.glob("*.md")) if CASES.exists() else []


@app.get("/api/v2/samples/{name}", dependencies=[Depends(auth)])
def sample(name: str) -> dict:
    path = CASES / f"{Path(name).name}.md"
    if not path.is_file():
        raise HTTPException(404, "no such sample")
    return {"name": path.stem, "case_md": path.read_text()}


@app.post("/api/v2/run", dependencies=[Depends(auth)])
async def run(req: RunIn) -> dict:
    if not req.case_md.strip():
        raise HTTPException(400, "case_md is empty")
    name = "".join(c for c in (req.name or "case") if c.isalnum() or c in "-_.")[:60] or "case"
    return await run_in_threadpool(run_case, req.case_md, name, req.model)


# Serve the built web_v2 (web_v2/dist) from the same origin, so no Node is needed to use it.
DIST = ROOT / "web_v2" / "dist"
if DIST.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web_v2")
