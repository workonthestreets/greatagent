from pathlib import Path

from scorer.cases import load_cases, snapshot

FIXTURES = Path(__file__).parent / "fixtures"


def test_insurance_cut_hides_the_ending_and_the_brokers_plan():
    [case] = load_cases(FIXTURES, ["insurance"], None)
    snap = snapshot(case)  # no picker: first broker message carries the action
    assert snap is not None
    assert snap.expected.startswith("Forward Example Mutual's decision wording")
    seen = snap.agent_input
    assert not hasattr(seen, "expected")
    for leak in ("Hidden from the agent", "Plan: forward", "word for word", "Thanks, received",
                 "Completed", "Status"):
        assert leak not in seen.text
    assert "cover applies to the kitchen only" in seen.text
