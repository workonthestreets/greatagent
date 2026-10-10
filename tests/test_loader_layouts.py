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


def test_case_without_history_says_so(tmp_path):
    folder = tmp_path / "Delivery & Logistics" / "005"
    folder.mkdir(parents=True)
    (folder / "index.md").write_text(INDEX)
    case = load_case(folder)
    assert not case.events and any(w.startswith("no history.md") for w in case.warnings)
    assert not any(w.startswith("no history.md") for w in load_case(_case(tmp_path / "x" / "006")).warnings)


def test_zip_attachment_lists_members_and_reads_text_ones(tmp_path):
    folder = _case(tmp_path / "Delivery & Logistics" / "008")
    (folder / "attachments").mkdir()
    with zipfile.ZipFile(folder / "attachments" / "bundle.zip", "w") as z:
        z.writestr("scans/carrier.txt", "Carrier scan DL-039-O at Northgate")
        z.writestr("photo.jpg", b"\xff\xd8not text")
        z.writestr("inner.zip", b"PK nested")
    body = case_body_text(load_case(folder))
    assert "Carrier scan DL-039-O at Northgate" in body
    assert "photo.jpg" in body and "inner.zip" in body and "PK nested" not in body
