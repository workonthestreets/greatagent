import hashlib
import hmac
import json
import time

import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from voice import app as voice


def test_tool_speaks_template_and_post_call_checks_signature(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("ELEVENLABS_WEBHOOK_SECRET", "wh")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(voice, "decide", lambda case: {
        "action": "request", "party": "carrier", "team": "Parcel trace team", "org": "Plover Arc Logistics",
        "missing": "a trace of DL-1", "escalate": False, "message": "We will refund you £20"})
    client = TestClient(voice.app)
    body = {"conversation_id": "c1", "caller_name": "Ana", "order_ref": "DL-1", "issue": "Parcel missing"}
    assert client.post("/voice/tool", json=body).status_code == 401
    say = client.post("/voice/tool", json=body, headers={"X-Tool-Secret": "s3"}).json()["say"]
    assert "Plover Arc Logistics" in say and "£" not in say
    raw = json.dumps({"type": "post_call_transcription", "data": {"conversation_id": "c1", "transcript": []}})
    t = str(int(time.time()))
    sig = hmac.new(b"wh", f"{t}.{raw}".encode(), hashlib.sha256).hexdigest()
    ok = client.post("/voice/post-call", content=raw, headers={"ElevenLabs-Signature": f"t={t},v0={sig}"})
    bad = client.post("/voice/post-call", content=raw, headers={"ElevenLabs-Signature": f"t={t},v0=00"})
    assert (ok.status_code, bad.status_code) == (200, 401) and (tmp_path / "c1-transcript.json").exists()
