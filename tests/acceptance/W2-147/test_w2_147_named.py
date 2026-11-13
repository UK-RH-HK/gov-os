"""S3: the choice is deterministic and named. The same tickets give byte-identical output in any file order, and
each break is named in the text and ``--json`` outputs (CYCLE_TIEBREAK) with the ticket chosen and the waits broken
(DEC-1102, DEC-1088 (1))."""

from __future__ import annotations

import pytest

import w2_147_support as support
from w2_147_graphs import CYCLE_GRAPHS


@pytest.mark.parametrize("form", ["text", "json"])
@pytest.mark.parametrize("graph", list(CYCLE_GRAPHS))
def test_s3_two_shuffled_file_orders_give_byte_identical_output(tmp_path, graph, form):
    tickets = CYCLE_GRAPHS[graph]
    flags = ("--json",) if form == "json" else ()
    root, outs = tmp_path / "repo", []
    for seed in (1, 2):  # rebuilt at the same path, so the root does not differ
        names = support.shuffled_names(tickets, seed)
        support.plant(root, tickets, names)
        outs.append(support.run(root, *flags))
    assert outs[0][1].startswith(("gov plan:", "{")), outs[0]
    assert support.shuffled_names(tickets, 1) != support.shuffled_names(tickets, 2)
    assert outs[0] == outs[1], "\n=====\n".join(out for _, out in outs)


@pytest.mark.parametrize("graph", list(CYCLE_GRAPHS))
def test_s3_each_break_is_named_with_the_ticket_chosen_and_the_waits_broken(tmp_path, graph):
    """In ``--json``: the CYCLE_TIEBREAK entries are exactly the oracle's (``waits_for`` the ticket chosen,
    ``ticket`` the one it had waited on, ``what`` the broken wait's code and id); the text writes each as a line."""
    tickets = CYCLE_GRAPHS[graph]
    support.plant(tmp_path / "repo", tickets)
    _, data = support.run_json(tmp_path / "repo")
    want = support.expected_breaks(tickets)
    assert want, graph  # every graph here has a cycle
    got = support.breaks(data)
    assert sorted(map(str, got)) == sorted(map(str, want)), f"breaks {got}, expected {want}"
    assert "CYCLE_TIEBREAK" in data["result"]["codes"], data["result"]["codes"]
    _, out = support.run(tmp_path / "repo")
    for entry in want:
        assert support.text_line(entry) in out.splitlines(), out
    assert "CYCLE_TIEBREAK" in out.splitlines()[0], out
