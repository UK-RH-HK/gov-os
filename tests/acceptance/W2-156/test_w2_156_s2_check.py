"""S2: ``gov spend check`` brakes a ticket whose running cost is more than twice its latest projection: one brake record,
one marker, one inbox item naming the ticket, the cost and the projection, once per ticket until it is cleared."""

from __future__ import annotations

import w2_156_support as t


def test_s2_a_cost_of_1_99_times_the_projection_gives_no_brake(box, project):
    t.plant_over(project, t.A, projection=5.0, cost_parts=(4.95, 5.0))      # 9.95 = 1.99 x 5.00
    run = t.assert_ok(t.spend(box, "check"))
    t.assert_nothing_written(project, f"for a cost of 1.99 times the projection\n{run.describe()}")


def test_s2_a_cost_of_exactly_twice_the_projection_is_not_braked(box, project):
    t.plant_over(project, t.A, projection=5.0, cost_parts=(5.0, 5.0))       # 10.00 = 2.00 x 5.00
    run = t.assert_ok(t.spend(box, "check"))
    t.assert_nothing_written(project, f"for a cost of exactly twice the projection\n{run.describe()}")


def test_s2_a_cost_of_2_01_times_the_projection_gives_one_record_one_marker_one_inbox_item(box, project):
    t.plant_over(project, t.A, projection=5.0, cost_parts=(4.05, 3.0, 3.0))   # 10.05 = 2.01 x 5.00
    run = t.assert_ok(t.spend(box, "check"))
    t.assert_one_brake(project, t.A, 10.05, 5.0)
    w = t.written(project)
    assert len(w.of_kind("brake")) == 1 and len(w.markers) == 1 and len(w.inbox) == 1, (
        f"more than one record, marker or item was written: {w}\n{run.describe()}")


def test_s2_a_second_check_writes_nothing_more_for_a_ticket_already_braked(box, project):
    t.plant_over(project, t.A)
    t.assert_ok(t.spend(box, "check"))
    first = t.written(project)
    t.assert_one_brake(project, t.A, 10.05, 5.0)
    t.plant_session(project, t.A, 7.0)                       # still over, with more cost: no second brake
    again = t.assert_ok(t.spend(box, "check"))
    second = t.written(project)
    assert second.lines == first.lines, f"a second `check` wrote a brake record: {second.lines}\n{again.describe()}"
    assert second.inbox == first.inbox, f"a second `check` wrote an inbox item: {sorted(second.inbox)}"
    assert second.markers == first.markers, f"a second `check` changed the marker: {second.markers}"


def test_s2_check_judges_every_ticket_and_brakes_only_those_over_twice_the_projection(box, project):
    t.plant_over(project, t.A, projection=5.0, cost_parts=(4.05, 3.0, 3.0))    # over
    t.plant_over(project, t.B, projection=5.0, cost_parts=(4.95, 5.0))         # under
    t.plant_over(project, t.C, projection=2.0, cost_parts=(2.5, 2.5))          # over (5.00 > 4.00)
    t.assert_ok(t.spend(box, "check"))
    w = t.written(project)
    assert sorted(w.markers) == [f"{t.A}.json", f"{t.C}.json"], f"the markers are {sorted(w.markers)}"
    t.assert_one_brake(project, t.A, 10.05, 5.0)
    t.assert_one_brake(project, t.C, 5.0, 2.0)
    assert len(w.of_kind("brake")) == 2 and len(w.inbox) == 2, f"not one record and one item per braked ticket: {w}"
    assert not any(t.B in text for text in w.inbox.values()), "B, under twice its projection, is in an inbox item"


def test_s2_a_ticket_that_already_has_a_marker_gets_nothing_more(box, project):
    t.plant_over(project, t.A)
    t.plant_marker(project, t.A, 10.05, 5.0)
    before = t.written(project)
    run = t.assert_ok(t.spend(box, "check"))
    after = t.written(project)
    assert after.lines == before.lines == [] and after.inbox == before.inbox == {}, (
        f"`check` wrote a brake record or an inbox item for a ticket with a marker: {after}\n{run.describe()}")
    assert after.markers == before.markers, "the existing marker was changed"


def test_s2_the_projection_is_the_latest_launch_record_s_not_the_first(box, project):
    # A: first projection 1.00, later 5.00; cost 4.00 is over twice the first and under twice the latest: not braked.
    t.plant_launch(project, t.A, 1.0, started=t.PAST)
    t.plant_launch(project, t.A, 5.0, started=t.PAST_LATER)
    t.plant_session(project, t.A, 4.0)
    # B: first projection 5.00, later 1.00; cost 2.50 is under twice the first and over twice the latest: braked.
    t.plant_launch(project, t.B, 5.0, started=t.PAST)
    t.plant_launch(project, t.B, 1.0, started=t.PAST_LATER)
    t.plant_session(project, t.B, 2.5)
    t.assert_ok(t.spend(box, "check"))
    w = t.written(project)
    assert sorted(w.markers) == [f"{t.B}.json"], f"the markers are {sorted(w.markers)}, not B's alone"
    t.assert_one_brake(project, t.B, 2.5, 1.0)
    assert not any(t.A in text for text in w.inbox.values()), "A, under twice its latest projection, is in an inbox item"


def test_s2_a_later_launch_without_a_projection_does_not_remove_the_earlier_one(box, project):
    t.plant_launch(project, t.A, 5.0, started=t.PAST)
    t.plant_launch(project, t.A, None, started=t.PAST_LATER)           # a launch that holds none
    t.plant_launch_without_projection(project, t.A, started="2026-01-03T00:00:00Z")
    for part in (4.05, 3.0, 3.0):
        t.plant_session(project, t.A, part)
    t.assert_ok(t.spend(box, "check"))
    t.assert_one_brake(project, t.A, 10.05, 5.0)


def test_s2_the_root_option_names_the_project_the_check_works_on(box, project):
    t.plant_over(project, t.A)
    t.assert_ok(t.spend(box, "check", "--root", str(project), cwd=box.elsewhere))
    t.assert_one_brake(project, t.A, 10.05, 5.0)
