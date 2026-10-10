"""The hub: /mcp (agent tools), /api (web app), /webhooks (ElevenLabs).

    uvicorn hub.app:app --port 8000
"""
from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.transport_security import TransportSecuritySettings

from . import api, webhooks
from .config import settings
from .mcp_tools import mcp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# Stateless JSON transport: each tool call is one POST, which suits the Managed Agents MCP proxy and tunnels.
# DNS-rebinding checks are off because the hub sits behind a public tunnel; the bearer token guards /mcp.
mcp_app = mcp.streamable_http_app(
    stateless_http=True, json_response=True, host="0.0.0.0",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="greatagent hub", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def mcp_bearer(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        expected = f"Bearer {settings.mcp_token}"
        if not settings.mcp_token or not secrets.compare_digest(request.headers.get("authorization", ""), expected):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)


app.include_router(api.router)
app.include_router(webhooks.router)
app.mount("/", mcp_app)   # serves /mcp; mounted last so it doesn't shadow the routers
