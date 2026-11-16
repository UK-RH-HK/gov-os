"""S4 (and F2's second half): a ticket with no projection is never braked: ``check`` names it "no projection" and writes
nothing."""

from __future__ import annotations

import pytest

import w2_156_support as t


def _plant(project, form):
    if form == "no launch record":
        pass
    elif form == "launch record without the key":
        t.plant_launch_without_projection(project, t.A)
    elif form == "launch record with a null projection":
        t.plant_launch(project, t.A, None)
    for part in (60.0, 40.0):                                  # a large cost: 100.00
        t.plant_session(project, t.A, part)


@pytest.mark.parametrize("form", ["no launch record", "launch record without the key",
                                  "launch record with a null projection"])
def test_s4_a_large_cost_and_no_projection_gives_no_marker_no_record_no_inbox_item(box, project, form):
    _plant(project, form)
    t.plant_over(project, t.B)                                 # another ticket, with a projection, is braked
    run = t.assert_ok(t.spend(box, "check"))
    text = t.said(run)
    assert t.A in text and "no projection" in text, f"`check` does not name {t.A} with 'no projection':\n{run.describe()}"
    w = t.written(project)
    assert f"{t.A}.json" not in w.markers, f"a ticket with no projection was braked: {sorted(w.markers)}"
    assert not [line for line in w.lines if line.get("ticket") == t.A], f"a brake record for {t.A}: {w.lines}"
    assert not any(t.A in item for item in w.inbox.values()), "an inbox item names the ticket with no projection"
    t.assert_one_brake(project, t.B, 10.05, 5.0)               # the check did judge the other ticket


def test_s4_another_ticket_s_projection_is_not_this_ticket_s(box, project):
    t.plant_launch(project, t.B, 1.0)                          # only B has a projection
    t.plant_session(project, t.A, 50.0)
    t.plant_session(project, t.B, 0.5)
    t.assert_ok(t.spend(box, "check"))
    t.assert_nothing_written(project, "for a ticket whose only projection is another ticket's")


def test_s4_sum_gives_the_words_no_projection_on_the_ticket_s_line(box, project):
    t.plant_launch_without_projection(project, t.A)
    t.plant_session(project, t.A, 100.0)
    run = t.assert_ok(t.spend(box, "sum"))
    line = t.one_line(run, t.A)
    assert "no projection" in line and t.has_amount(line, "100.00") and t.brake_state(line) == "not braked", (
        f"the line for A (100.00, no projection, not braked):\n{line}")
