"""S5: ``gov spend clear <ticket> [--projection-usd N] --note <text>`` removes the marker and restarts the ticket's count
from that moment, with the note and the new projection (if given) in the brake record; a cost before the clear is no
longer counted. The records before the clear carry stamps well in the past, those after it stamps in 2099, never within
the clear's second."""

from __future__ import annotations

import calendar
import time

import w2_156_support as t

b = t.b
NOTE = "the CTO reviewed the spend and lets the ticket go on"


def _braked_ticket(box, project, ticket=t.TK, projection=5.0):
    """A ticket planted at 2.01 times its projection (10.05 against 5.00), braked by ``gov spend check``."""
    t.plant_over(project, ticket, projection=projection)
    t.assert_ok(t.spend(box, "check"))
    t.assert_one_brake(project, ticket, 10.05, projection)


def _epoch(stamp):
    return calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))


def test_s5_clear_removes_the_marker_and_writes_one_clear_record_with_the_note_and_the_new_projection(box, project):
    _braked_ticket(box, project)
    before = time.time()
    run = t.assert_ok(t.spend(box, "clear", t.TK, "--projection-usd", "8", "--note", NOTE))
    after = time.time()
    w = t.written(project)
    assert f"{t.TK}.json" not in w.markers, f"the marker is still there after `clear`: {sorted(w.markers)}\n{run.describe()}"
    clears = w.of_kind("clear")
    assert len(clears) == 1, f"{len(clears)} clear records, not one: {w.lines}"
    clear = clears[0]
    assert clear.get("ticket") == t.TK and clear.get("note") == NOTE, f"the clear record's ticket and note: {clear}"
    assert clear.get("projection_usd") is not None and abs(float(clear["projection_usd"]) - 8.0) < 0.005, (
        f"the clear record does not hold the new projection 8: {clear}")
    assert isinstance(clear.get("at"), str) and t.STAMP.fullmatch(clear["at"]), f"the clear record's at: {clear}"
    assert before - 5 <= _epoch(clear["at"]) <= after + 5, f"the clear's time {clear['at']} is not the time of the command"
    assert len(w.of_kind("brake")) == 1, f"`clear` changed the brake records: {w.lines}"


def test_s5_clear_without_a_new_projection_records_null_and_keeps_the_launch_s_projection(box, project):
    _braked_ticket(box, project)
    t.assert_ok(t.spend(box, "clear", t.TK, "--note", NOTE))
    clears = t.written(project).of_kind("clear")
    assert len(clears) == 1 and clears[0].get("projection_usd") is None and "projection_usd" in clears[0], (
        f"the clear record, given no projection, does not hold projection_usd null: {clears}")
    t.plant_session(project, t.TK, 1.25, started=t.FUTURE)
    run = t.assert_ok(t.spend(box, "sum"))
    line = t.one_line(run, t.TK)
    assert t.has_amount(line, "1.25") and t.has_amount(line, "5.00") and t.brake_state(line) == "not braked", (
        f"the line (cost since the clear 1.25, the launch's projection 5.00, not braked):\n{line}")


def test_s5_after_clear_sum_shows_the_cost_since_the_clear_only_and_the_new_projection(box, project):
    _braked_ticket(box, project)
    t.assert_ok(t.spend(box, "clear", t.TK, "--projection-usd", "8", "--note", NOTE))
    t.plant_session(project, t.TK, 1.25, started=t.FUTURE)
    run = t.assert_ok(t.spend(box, "sum"))
    line = t.one_line(run, t.TK)
    assert t.has_amount(line, "1.25"), f"the cost since the clear is not 1.25:\n{line}"
    assert not t.has_amount(line, "11.30") and not t.has_amount(line, "10.05"), (
        f"a cost before the clear is still counted:\n{line}")
    assert t.has_amount(line, "8.00") and t.brake_state(line) == "not braked", (
        f"the line (projection 8.00 from the clear, not braked):\n{line}")


def test_s5_a_cost_before_the_clear_is_no_longer_counted_so_check_does_not_brake_again(box, project):
    _braked_ticket(box, project)
    t.assert_ok(t.spend(box, "clear", t.TK, "--note", NOTE))
    t.plant_session(project, t.TK, 1.25, started=t.FUTURE)
    before = t.written(project)
    t.assert_ok(t.spend(box, "check"))
    after = t.written(project)
    assert not after.markers, f"`check` braked a ticket whose cost since the clear is 1.25: {sorted(after.markers)}"
    assert after.lines == before.lines and after.inbox == before.inbox, (
        f"`check` wrote a record or an inbox item after the clear: {after.lines}, {sorted(after.inbox)}")


def test_s5_a_new_overspend_after_the_clear_brakes_again_counting_the_cost_since_the_clear_only(box, project):
    _braked_ticket(box, project)
    t.assert_ok(t.spend(box, "clear", t.TK, "--projection-usd", "8", "--note", NOTE))
    t.plant_session(project, t.TK, 20.0, started=t.FUTURE)       # 20.00 > 2 x 8.00; with the old 10.05 it would be 30.05
    t.assert_ok(t.spend(box, "check"))
    w = t.written(project)
    assert f"{t.TK}.json" in w.markers, f"the ticket over twice its new projection is not braked: {sorted(w.markers)}"
    brakes = w.of_kind("brake")
    assert len(brakes) == 2, f"{len(brakes)} brake records, not two (the first and the new): {w.lines}"
    new = brakes[-1]
    assert abs(float(new["cost_usd"]) - 20.0) < 0.005 and abs(float(new["projection_usd"]) - 8.0) < 0.005, (
        f"the new brake record is not cost 20.00 over projection 8.00: {new}")
    assert abs(float(w.markers[f"{t.TK}.json"]["cost_usd"]) - 20.0) < 0.005, f"the new marker: {w.markers}"
    # the item's file name is not stated: an item that names the ticket and gives the new cost and projection is there
    assert any(t.TK in text and t.has_amount(text, "20.00") and t.has_amount(text, "8.00")
               for text in w.inbox.values()), f"no inbox item names {t.TK} with 20.00 and 8.00: {w.inbox}"


def test_s5_clear_refuses_without_a_note_and_keeps_the_marker(box, project):
    _braked_ticket(box, project)
    before = t.written(project)
    run = t.spend(box, "clear", t.TK)
    assert run.returncode == 2, f"`clear` without --note did not end with exit code 2\n{run.describe()}"
    assert "--note" in t.said(run), f"the refusal does not name --note:\n{run.describe()}"
    after = t.written(project)
    assert after.markers == before.markers and after.lines == before.lines, "a refused `clear` changed the brake"


def test_s5_after_a_planted_brake_clear_then_launch_starts(box, project, cli):
    _braked_ticket(box, project)
    refused = b.launch(box, cli, b.ENGINEER, t.TK)
    b.assert_refused(refused, "SPEND_BRAKED")                    # the control: braked, so refused
    t.assert_ok(t.spend(box, "clear", t.TK, "--projection-usd", "8", "--note", NOTE))
    b.assert_launched(b.launch(box, cli, b.ENGINEER, t.TK))
