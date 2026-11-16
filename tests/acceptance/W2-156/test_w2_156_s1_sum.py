"""S1 (and F2's first half): a ticket's running cost is the sum of the measured cost of its sessions' records; a session
whose cost is not measured is counted as unknown and named, never as zero. ``gov spend sum`` prints one line per ticket
that has a counted session record, holding the ticket id, the cost, ``N unknown``, the projection and the brake state."""

from __future__ import annotations

import re

import w2_156_support as t


def test_s1_sum_prints_the_total_of_the_three_measured_one_unknown_the_projection_and_the_brake_state(box, project):
    t.plant_launch(project, t.A, 3.0)
    t.plant_session(project, t.A, 1.25, role="engineer")
    t.plant_session(project, t.A, 2.5, role="independent-test-designer")
    t.plant_session(project, t.A, 0.75, role="independent-auditor")      # a reviewer's session counts (not exempt)
    t.plant_session(project, t.A, None, role="engineer")                  # not measured

    run = t.assert_ok(t.spend(box, "sum"))
    line = t.one_line(run, t.A)
    assert t.has_amount(line, "4.50"), f"the line does not give the total of the three measured, 4.50:\n{line}"
    assert re.search(r"\b1 unknown\b", line), f"the line does not name the one unknown session ('1 unknown'):\n{line}"
    assert t.has_amount(line, "3.00"), f"the line does not give the projection 3.00:\n{line}"
    assert t.brake_state(line) == "not braked", f"the line does not say 'not braked':\n{line}"


def test_s1_sum_gives_one_line_per_ticket_with_a_counted_record_and_only_those(box, project):
    t.plant_launch(project, t.A, 10.0)
    t.plant_session(project, t.A, 1.5)
    t.plant_session(project, t.A, 2.0)
    t.plant_session(project, t.A, 2.5)
    t.plant_session(project, t.B, 0.5)                      # B has no projection
    t.plant_launch(project, t.C, 4.0)                       # C has a launch record and no session record
    run = t.assert_ok(t.spend(box, "sum"))

    line_a = t.one_line(run, t.A)
    assert t.has_amount(line_a, "6.00") and t.has_amount(line_a, "10.00") and t.brake_state(line_a) == "not braked", (
        f"A's line (cost 6.00, projection 10.00, not braked):\n{line_a}")
    assert not re.search(r"[1-9]\d* unknown", line_a), f"A has no session whose cost is not measured:\n{line_a}"
    line_b = t.one_line(run, t.B)
    assert t.has_amount(line_b, "0.50") and "no projection" in line_b and t.brake_state(line_b) == "not braked", (
        f"B's line (cost 0.50, no projection, not braked):\n{line_b}")
    assert not t.lines_of(run, t.C), f"C has no session record yet `sum` has a line for it:\n{run.stdout}"
    assert not t.has_amount(line_a, "0.50"), f"another ticket's cost reached A's line:\n{line_a}"


def test_s1_a_ticket_whose_sessions_are_all_not_measured_is_named_with_its_unknowns(box, project):
    t.plant_launch(project, t.A, 1.0)
    t.plant_session(project, t.A, None)
    t.plant_session(project, t.A, None)
    run = t.assert_ok(t.spend(box, "sum"))
    line = t.one_line(run, t.A)
    assert re.search(r"\b2 unknown\b", line), f"the line does not say '2 unknown':\n{line}"
    assert t.brake_state(line) == "not braked", f"a ticket with no measured cost is braked or has no state:\n{line}"


def test_s1_a_braked_ticket_is_shown_braked(box, project):
    t.plant_over(project, t.A)
    t.plant_over(project, t.B, projection=5.0, cost_parts=(1.0,))
    t.assert_ok(t.spend(box, "check"))
    run = t.assert_ok(t.spend(box, "sum"))
    line_a, line_b = t.one_line(run, t.A), t.one_line(run, t.B)
    assert t.brake_state(line_a) == "braked" and t.has_amount(line_a, "10.05"), (
        f"A (cost 10.05, braked by `check`) is not shown 'braked':\n{line_a}")
    assert t.brake_state(line_b) == "not braked", f"B is not shown 'not braked':\n{line_b}"


def test_s1_the_root_option_names_the_project_the_command_works_on(box, project):
    t.plant_launch(project, t.A, 3.0)
    t.plant_session(project, t.A, 2.0)
    run = t.assert_ok(t.spend(box, "sum", "--root", str(project), cwd=box.elsewhere))
    line = t.one_line(run, t.A)
    assert t.has_amount(line, "2.00") and t.has_amount(line, "3.00"), f"the line for A (2.00, 3.00):\n{line}"
