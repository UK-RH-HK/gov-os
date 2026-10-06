"""Tests for the stale-checkpoint watchdog at close: Point 10 (S1, DEC-416).

DEC-416 decides: gov close calls gov.checkpoint.record.watch before it closes
and refuses on a stale or missing checkpoint with the watchdog's own code.
The closing checkpoint is written after the checks pass.

DEC-321 defaults: 240 minutes max age, 20 max commits.
"""

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-wdog"
WBS = "W1-wdog"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-wdog", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _green_project(project, ticket_id=TICKET, wbs=WBS):
    """A project whose ticket can close: passing tests, correct trailers."""
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    return ticket_id


def _write_stale_checkpoint(project, ticket_id):
    """Write a checkpoint with a created time far in the past (stale by DEC-321: > 240 min)."""
    import yaml

    cp_dir = project.root / "docs" / "checkpoints" / ticket_id
    cp_dir.mkdir(parents=True, exist_ok=True)
    cp_id = f"CP-{ticket_id}-0001"
    front = {
        "id": cp_id,
        "type": "checkpoint",
        "status": "ACTIVE",
        "state_class": "NARRATIVE",
        "title": f"{ticket_id} at task-start",
        "task": ticket_id,
        "task_status": "open",
        "trigger": "stop",
        "next_action": "implement the feature",
        "created": "2026-09-01T00:00:00Z",
        "inputs": [{"id": ticket_id, "version": "abc1234", "hash": "sha256:" + "a" * 64}],
    }
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {cp_id} — {ticket_id} at task-start\n\n## Next action\n\nimplement the feature\n"
    (cp_dir / f"{cp_id}.md").write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# Point 10 (MISSING): Stale-checkpoint watchdog (S1, DEC-416)
# --------------------------------------------------------------------------

def test_close_refuses_on_stale_checkpoint(project, sandbox, interface):
    """KPI S1, DEC-416: gov close refuses on a checkpoint older than the threshold."""
    _green_project(project)
    _write_stale_checkpoint(project, TICKET)
    project.commit("add stale checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when the latest checkpoint is stale (DEC-416)"


def test_close_refuses_on_missing_checkpoint(project, sandbox, interface):
    """KPI S1, DEC-416: gov close refuses when no checkpoint exists at all."""
    _green_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when no checkpoint exists at all (DEC-416)"


def test_closing_checkpoint_written_after_checks_pass(project, sandbox, interface):
    """KPI S1, DEC-416: on success, the checkpoint is written after containment/trailer/test checks pass."""
    _green_project(project)
    from gov.checkpoint.record import write as cp_write
    import yaml
    cp_info = cp_write(project.root, TICKET, "stop", "begin", [])
    project.commit("add fresh checkpoint", who=support.ORCHESTRATOR)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    result = support.result_of(run, interface)
    created = support.new_files(project.root, before, after)
    _, cp_front = support.find_checkpoint_record(project.root, created)
    assert cp_front is not None, "a closing checkpoint must be written on success"
    assert cp_front.get("trigger") == "ticket-transition", \
        f"the closing checkpoint's trigger must be 'ticket-transition', got {cp_front.get('trigger')!r}"
