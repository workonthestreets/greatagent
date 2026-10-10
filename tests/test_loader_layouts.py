"""Unusual case layouts the loader must not drop silently (offline, no API)."""
import zipfile

from deskagent.loader import discover_cases, load_case
from deskagent.pipeline import case_body_text

INDEX = "# Case 039: Duplicate parcel\n\n## Case details\n- **Primary task reference:** TG-039\n\n## Initial request\nBoth arrived.\n"
HISTORY = ('<a id="event-001"></a>\n## 2026-03-12 09:00:00 UTC — event 001\n\n- **Stage:** Context\n'
           "- **From:** Ops, Tallowmere Goods\n\nTG-039 ordered one floor light.\n")


def _case(folder):
    folder.mkdir(parents=True)
    (folder / "index.md").write_text(INDEX)
    (folder / "history.md").write_text(HISTORY)
    return folder


def test_case_one_folder_deeper_is_found_and_named_after_its_case_folder(tmp_path):
    track = tmp_path / "Delivery & Logistics"
    _case(track / "001")
    _case(track / "002" / "sub")
    found = discover_cases(track)
    assert [p.name for p in found] == ["001", "002"]
    case = load_case(found[1])
    assert case.answer_id == "2" and len(case.events) == 1 and "TG-039 ordered" in case_body_text(case)
    assert [n for n, _ in case.files] == ["index.md", "history.md"] and not case.attachments  # not read twice


def test_a_track_holding_one_case_is_still_a_track(tmp_path):
    root = tmp_path / "HackatonChallendges"
    _case(root / "Delivery & Logistics" / "007")
    _case(root / "Banking & Financial Services" / "001")
    assert [(p.parent.name, p.name) for p in discover_cases(root)] == [
        ("Banking & Financial Services", "001"), ("Delivery & Logistics", "007")]
