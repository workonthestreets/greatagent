from pathlib import Path

from agent import answers

FIXTURES = Path(__file__).parent / "fixtures" / "Insurance Claims Processing"


def test_writes_submission_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(answers, "decide", lambda case: {
        "action": "request", "party": "carrier", "org": "Plover Arc Logistics", "team": "Parcel trace team",
        "channel": "Email", "message": "Please trace DL-1.", "question_for_human": "", "escalate": False,
        "flags": [], "need": "parcel_action", "missing": "a trace", "confidence": 0.8})
    assert answers.main(["--cases", str(FIXTURES), "--out", str(tmp_path)]) == 0
    case = tmp_path / "901"
    assert "Parcel trace team" in (case / "ANSWER.md").read_text()
    assert "What the system received" in (case / "REASONING.md").read_text()
    assert (case / "outbox.eml").exists() and (tmp_path / "results.jsonl").read_text().count("\n") == 1
