"""S4: every heavy step takes a heavy-job slot; one found running outside a slot is named in the status as a finding
(ticket DAEO-ifgf, Interface item 4).

The heavy steps are the ``job_markers`` kinds ``test``, ``rebuild``, ``check`` and ``measure``, planted as ``/proc``
entries (``GOV_RESOURCES_PROC``). A slot is held the way W2-20's runner holds it: ``slot-<n>.json`` with the runner's pid
in ``$HOME/.gov-os/machine/slots/`` and ``slot-<n>.lock`` flock-held (here by the test process); a record whose lock is
not held counts for nothing. A heavy step is in a slot when it or an ancestor is a slot's runner (the parent pid in its
planted ``stat``).
"""

from __future__ import annotations

import pytest

import w2_121b_support as s

KINDS = ("test", "rebuild", "check", "measure")
MARKERS = {kind: f"hv-job-{kind}" for kind in KINDS}
RUNNER = ["python3", "-m", "gov.cli.main", "resources", "--slot", "test", "--"]


def configure(p) -> None:
    p.cfg(job_markers=dict(MARKERS))


def plant_in_slot(p, kind: str, slot: int, relation: str) -> int:
    """A heavy step of ``kind`` whose runner holds ``slot``: the step is its runner (``self``), its child (``parent``) or
    its grandchild (``grandparent``). The pid of the heavy step."""
    if relation == "self":
        pid = p.plant_proc(RUNNER + ["pytest", MARKERS[kind]])
        p.hold_slot(slot, pid)
        return pid
    runner = p.plant_proc(RUNNER + ["sleep"])
    p.hold_slot(slot, runner)
    parent = runner
    if relation == "grandparent":
        parent = p.plant_proc(["sh"], ppid=runner)
    return p.plant_proc(["pytest", MARKERS[kind]], ppid=parent)


def plant_outside(p, kind: str) -> int:
    return p.plant_proc(["pytest", MARKERS[kind]], ppid=1)


def finding_for(kind: str, pid: int) -> str:
    return f"heavy step outside a slot: {kind} pid {pid}"


CASES = [("test", "parent"), ("rebuild", "grandparent"), ("check", "self"), ("measure", "parent"),
         ("test", "self"), ("rebuild", "parent"), ("check", "grandparent"), ("measure", "grandparent")]


@pytest.mark.parametrize("kind,relation", CASES, ids=[f"{k}-{r}" for k, r in CASES])
def test_a_heavy_step_in_a_slot_is_shown_holding_it(landing, kind, relation):
    p = landing
    configure(p)
    slot = 1 + CASES.index((kind, relation)) % 3
    pid = plant_in_slot(p, kind, slot, relation)
    run = p.tick()
    assert run.code == 0, run
    steps = s.heavy_steps(p)
    assert s.has_step(steps, kind, pid, slot), f"{kind} pid {pid} is not shown holding slot {slot}: {steps}"
    outside = [f for f in s.findings(p) if "outside a slot" in f]
    assert outside == [], f"a heavy step in a slot is named as outside one: {outside}"


@pytest.mark.parametrize("kind", KINDS)
def test_a_heavy_step_running_with_no_slot_is_a_finding_never_a_failed_pass(landing, kind):
    p = landing
    configure(p)
    baseline = p.tick()
    assert baseline.code == 0, baseline
    pid = plant_outside(p, kind)
    run = p.tick()
    assert run.code == baseline.code == 0, f"a heavy step outside a slot changed the pass's exit code: {run}"
    found = s.findings(p)
    expected = finding_for(kind, pid)
    assert any(expected in f for f in found), f"status.json `findings` lacks `{expected}`: {found}"
    assert expected in p.status_blob()
    steps = s.heavy_steps(p)
    assert all(step.get("slot") is None for step in steps if isinstance(step, dict) and step.get("pid") == pid), \
        f"a step with no slot is shown holding one: {steps}"
    assert p.status_json()["ok"] is True


def test_a_slot_record_whose_lock_is_not_held_is_no_slot(landing):
    p = landing
    configure(p)
    runner = p.plant_proc(RUNNER + ["sleep"])
    p.hold_slot(1, runner, held=False)  # the runner ended: its record is left, its lock is free
    pid = p.plant_proc(["pytest", MARKERS["test"]], ppid=runner)
    run = p.tick()
    assert run.code == 0, run
    assert any(finding_for("test", pid) in f for f in s.findings(p)), s.findings(p)
    assert not s.has_step(s.heavy_steps(p), "test", pid, 1)


def test_slotted_and_unslotted_heavy_steps_in_one_pass(landing):
    p = landing
    configure(p)
    in_test = plant_in_slot(p, "test", 1, "parent")
    in_rebuild = plant_in_slot(p, "rebuild", 2, "grandparent")
    in_check = plant_in_slot(p, "check", 3, "self")
    loose = plant_outside(p, "measure")
    run = p.tick()
    assert run.code == 0, run
    steps = s.heavy_steps(p)
    assert s.has_step(steps, "test", in_test, 1), steps
    assert s.has_step(steps, "rebuild", in_rebuild, 2), steps
    assert s.has_step(steps, "check", in_check, 3), steps
    assert not any(isinstance(x, dict) and x.get("pid") == loose and x.get("slot") is not None for x in steps), steps
    found = s.findings(p)
    assert any(finding_for("measure", loose) in f for f in found), found
    assert len([f for f in found if "outside a slot" in f]) == 1, f"only the step with no slot is a finding: {found}"
