"""S4: the planted graphs, each with its stated outcome: two separate cycles, each broken once inside itself; a
self-loop, broken at that ticket and named; no cycle, the output byte-identical to integrate's (DEC-1102). S1's
graph is in ``test_w2_147_inside.py``."""

from __future__ import annotations

import pytest

import w2_147_support as support
from w2_147_graphs import NO_CYCLE_GRAPHS, S1, SELF_LOOP, TWO_CYCLES


def _kept_and_after(tickets, data):
    """Every planted wait not broken is a WAITS_ON entry, its ticket batched after the one it waits on."""
    waits, batch = data["result"]["waits"], support.batch_of(data)
    for entry in support.kept_waits(tickets):
        assert entry in waits, f"wait {entry} missing from {waits}"
        assert batch[entry["ticket"]] > batch[entry["waits_for"]], (entry, data["result"]["batches"])


def test_s4_two_separate_cycles_are_each_broken_once_inside_themselves(tmp_path):
    support.plant(tmp_path / "repo", TWO_CYCLES)
    code, data = support.run_json(tmp_path / "repo")
    assert code in (0, 1), data
    got = support.breaks(data)
    for cycle in ({"TK-a", "TK-b"}, {"TK-d", "TK-e"}):
        inside = [b for b in got if {b["ticket"], b["waits_for"]} <= cycle]
        assert len(inside) == 1, f"cycle {sorted(cycle)}: breaks {got}"
    assert len(got) == 2, f"a wait between the cycles or to an outside ticket broken: {got}"
    _kept_and_after(TWO_CYCLES, data)  # E on B (between them), A on G and F on D (outside) kept


def test_s4_a_self_loop_is_broken_at_that_ticket_and_named(tmp_path):
    support.plant(tmp_path / "repo", SELF_LOOP)
    code, data = support.run_json(tmp_path / "repo")
    assert code in (0, 1), data
    assert support.breaks(data) == [
        {"ticket": "TK-x", "waits_for": "TK-x", "code": "CYCLE_TIEBREAK", "what": "WAITS_ON TK-x"}], data
    assert "TK-x" in support.batch_of(data) and data["result"]["held"] == [], data
    _kept_and_after(SELF_LOOP, data)  # Y on X kept, Y after X
    _, out = support.run(tmp_path / "repo")
    assert "TK-x waits for TK-x (CYCLE_TIEBREAK WAITS_ON TK-x)" in out.splitlines(), out


@pytest.mark.parametrize("form", ["text", "json"])
@pytest.mark.parametrize("graph", list(NO_CYCLE_GRAPHS))
def test_s4_no_cycle_gives_integrates_output_byte_for_byte(tmp_path, graph, form):
    """The running tree against ``src/gov/plan`` at ``PIN`` (``support.run_today``), same store, same flags."""
    tickets, files = NO_CYCLE_GRAPHS[graph]
    assert not support.cycles(tickets), graph
    root = support.plant(tmp_path / "repo", tickets, files=files)
    flags = ("--json",) if form == "json" else ()
    today = support.run_today(root, *flags)
    assert today[1].startswith(("gov plan:", "{")), today
    assert support.run(root, *flags) == today


def test_s4_premise_todays_code_breaks_the_outside_waiter(tmp_path):
    """The reference is the code before the fix: at ``PIN`` S1's graph names C (outside the cycle) as broken."""
    support.plant(tmp_path / "repo", S1)
    _, out = support.run_today(tmp_path / "repo", "--json")
    import json

    named = support.breaks(json.loads(out))
    assert any(support.mentions(b, "TK-c") for b in named), named
