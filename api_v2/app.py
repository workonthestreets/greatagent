"""Stateless API for web_v2: case markdown -> preprocess -> deskagent_v1_1 -> combined run JSON. No database, no login.

    uvicorn api_v2.app:app --port 8100
Set V2_API_TOKEN to require `Authorization: Bearer <token>` on /api/v2 (recommended if the port is exposed).
The endpoints live in api_v2/routes.py; the hub mounts the same router behind desk-staff login (web/ Investigate page)."""
from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from deskagent_v1_1.agent import ROOT

from . import routes

app = FastAPI(title="greatagent v2 api")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def auth(authorization: Optional[str] = Header(None)) -> None:
    token = os.environ.get("V2_API_TOKEN")
    if token and not secrets.compare_digest(authorization or "", f"Bearer {token}"):
        raise HTTPException(401, "unauthorized")


app.get("/api/v2/health")(routes.health)
app.include_router(routes.router, prefix="/api/v2", dependencies=[Depends(auth)])

# Serve the built web_v2 (web_v2/dist) from the same origin, so no Node is needed to use it.
DIST = ROOT / "web_v2" / "dist"
if DIST.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web_v2")
