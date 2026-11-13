"""S1 and S2: a cycle is broken only at a ticket inside it, and a ticket outside every cycle keeps all its waits
(DEC-1102, DEC-1088 (1))."""

from __future__ import annotations

import w2_147_support as support
from w2_147_graphs import S1, S2


def test_s1_the_break_falls_inside_the_cycle_at_its_first_ticket_by_the_key(tmp_path):
    """A waits on B, B on A; C waits on A and sorts first. The one break is A's wait on B (A first of {A, B})."""
    support.plant(tmp_path / "repo", S1)
    code, data = support.run_json(tmp_path / "repo")
    assert code in (0, 1), data
    got = support.breaks(data)
    for entry in got:
        assert {entry["ticket"], entry["waits_for"]} <= {"TK-a", "TK-b"}, f"a break outside the cycle: {got}"
    assert got == support.expected_breaks(S1) == [
        {"ticket": "TK-b", "waits_for": "TK-a", "code": "CYCLE_TIEBREAK", "what": "WAITS_ON TK-b"}], got


def test_s1_the_outside_waiters_wait_is_kept_and_never_named_broken(tmp_path):
    support.plant(tmp_path / "repo", S1)
    code, out = support.run(tmp_path / "repo")
    assert code in (0, 1), out
    lines = out.splitlines()
    assert "TK-c waits for TK-a (WAITS_ON TK-a)" in lines, out
    assert not [line for line in lines if "CYCLE_TIEBREAK" in line and "TK-c" in line.split(" (", 1)[0]], out


def test_s2_the_outside_waiter_is_batched_after_the_ticket_it_waits_on(tmp_path):
    support.plant(tmp_path / "repo", S1)
    _, data = support.run_json(tmp_path / "repo")
    batch = support.batch_of(data)
    assert set(batch) == {"TK-a", "TK-b", "TK-c"}, data["result"]["batches"]
    assert batch["TK-c"] > batch["TK-a"], data["result"]["batches"]


def test_s2_the_case_of_2026_11_09_keeps_w2_27s_wait_on_w2_88(tmp_path):
    """W2-145 and W2-137 in a cycle, W2-88 waiting on W2-145, W2-27 on W2-88 (stand-ins of the same shape)."""
    support.plant(tmp_path / "repo", S2)
    code, data = support.run_json(tmp_path / "repo")
    assert code in (0, 1), data
    waits = data["result"]["waits"]
    assert {"ticket": "DAEO-s027", "waits_for": "DAEO-s088", "code": "WAITS_ON", "what": "W2-88"} in waits, waits
    assert {"ticket": "DAEO-s088", "waits_for": "DAEO-s145", "code": "WAITS_ON", "what": "W2-145"} in waits, waits
    named = [b for b in support.breaks(data) if support.mentions(b, "DAEO-s027") or support.mentions(b, "DAEO-s088")]
    assert not named, f"a ticket outside every cycle named in a break: {named}"
    batch = support.batch_of(data)
    assert batch["DAEO-s027"] > batch["DAEO-s088"] > batch["DAEO-s145"], data["result"]["batches"]
