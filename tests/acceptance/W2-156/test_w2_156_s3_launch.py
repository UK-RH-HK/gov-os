"""S3 (and F3): ``gov launch`` refuses a new session for a ticket that has a brake marker, naming the marker, the cost and
the projection (``SPEND_BRAKED``), after the resource gate's check and before anything starts; a ticket with no marker
launches as before. The launcher is W2-60a's, over its stand-in CLI (it starts no model): a refused launch never runs the
CLI and leaves no launch record and no session record."""

from __future__ import annotations

import w2_156_support as t

b = t.b
MARKER_TAIL = f"{t.BRAKED_REL}/{t.TK}.json"


def _refused_by_the_brake(box, project, run):
    """The refusal is SPEND_BRAKED, names the marker, the cost and the projection; nothing was started or written."""
    b.assert_refused(run, "SPEND_BRAKED", MARKER_TAIL, "10.05", "5.00")


def test_s3_a_ticket_with_a_marker_is_refused_naming_the_marker_the_cost_and_the_projection(box, project, cli):
    t.plant_marker(project, t.TK, 10.05, 5.0)
    sessions, launches = t.session_files(project), t.launch_files(project)
    run = b.launch(box, cli, b.ENGINEER, t.TK)
    _refused_by_the_brake(box, project, run)
    assert t.session_files(project) == sessions, f"a refused launch left a session record: {t.session_files(project)}"
    assert t.launch_files(project) == launches, f"a refused launch left a launch record: {t.launch_files(project)}"
    assert (project / MARKER_TAIL).is_file(), "the refusal removed the marker"


def test_s3_a_session_of_another_role_on_the_braked_ticket_is_refused_too(box, project, cli):
    t.plant_marker(project, t.TK, 10.05, 5.0)
    run = b.launch(box, cli, b.TEST_DESIGNER, t.TK)
    _refused_by_the_brake(box, project, run)


def test_s3_a_ticket_with_no_marker_launches_as_before(box, project, cli):
    # a guard: green on the base (a launch with no marker starts, and must still start)
    run = b.launch(box, cli, b.ENGINEER, t.TK)
    b.assert_launched(run)
    assert run.new_records, "the launch left no launch record"


def test_s3_a_marker_of_another_ticket_does_not_hold_this_ticket(box, project, cli):
    # a guard: green on the base
    t.plant_marker(project, t.OTHER_TK, 10.05, 5.0)
    b.assert_launched(b.launch(box, cli, b.ENGINEER, t.TK))


def test_s3_a_removed_marker_lets_the_ticket_launch(box, project, cli):
    marker = t.plant_marker(project, t.TK, 10.05, 5.0)
    _refused_by_the_brake(box, project, b.launch(box, cli, b.ENGINEER, t.TK))
    marker.unlink()
    b.assert_launched(b.launch(box, cli, b.ENGINEER, t.TK))


def test_s3_with_the_resource_gate_shut_and_a_marker_planted_the_refusal_is_the_gate_s(box, project, cli):
    # a guard: green on the base. The check stands after the gate's: a shut gate refuses first.
    t.plant_marker(project, t.TK, 10.05, 5.0)
    b.plant_open_gate(box)
    (box.home / ".gov-os" / "machine" / "gate.json").unlink()     # no gate configuration: the gate is shut (W2-20 S8)
    run = b.launch(box, cli, b.ENGINEER, t.TK)
    b.assert_refused(run, "LAUNCH_REFUSED", "the resource gate is shut")
    assert "SPEND_BRAKED" not in b.said(run), f"the brake refused before the gate:\n{run.describe()}"
