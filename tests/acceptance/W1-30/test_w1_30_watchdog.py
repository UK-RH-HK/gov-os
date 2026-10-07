"""Tests for the stale-checkpoint watchdog at close: B1 (S1, DEC-416).

B1: Any error from the watchdog (not just CHECKPOINT_STALE and CHECKPOINT_MISSING)
    refuses the close with the watchdog's own code. The close uses W1-25's
    thresholds (MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT from
    gov.checkpoint.command), not its own constants.
DEC-416: gov close calls gov.checkpoint.record.watch before it closes and refuses
    on a stale or missing checkpoint with the watchdog's own code. The closing
    checkpoint is written after the checks pass.
"""

import os

import yaml

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
# B1: Stale-checkpoint watchdog (DEC-416)
# --------------------------------------------------------------------------

def test_close_refuses_on_stale_checkpoint(project, sandbox, interface):
    """B1, DEC-416: gov close refuses on a checkpoint older than the threshold."""
    _green_project(project)
    _write_stale_checkpoint(project, TICKET)
    project.commit("add stale checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when the latest checkpoint is stale (DEC-416)"


def test_close_refuses_on_missing_checkpoint(project, sandbox, interface):
    """B1, DEC-416: gov close refuses when no checkpoint exists at all."""
    _green_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when no checkpoint exists at all (DEC-416)"


def test_closing_checkpoint_written_after_checks_pass(project, sandbox, interface):
    """B1, DEC-416: the closing checkpoint is written after checks pass.

    Revised after implementation: the case imported the package into the test
    process and passed only where PYTHONPATH was set.
    """
    _green_project(project)
    project.add_checkpoint(TICKET, trigger="stop", next_action="begin")
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


def test_any_watchdog_error_refuses_close(project, sandbox, interface):
    """B1: any GovError from the watchdog (not just two codes) refuses the close.

    The close uses the watchdog with W1-25's thresholds. Any GovError from
    gov.checkpoint.record.watch refuses the close with the watchdog's own code.
    """
    _green_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "without a checkpoint, the watchdog should refuse with its own GovError code"
    error = envelope.get("error", {})
    code = error.get("code", "")
    assert code and code != "NOT_IMPLEMENTED", \
        f"the error code must be the watchdog's own code: {code!r}"


def test_close_uses_w1_25_thresholds(project, sandbox, interface):
    """B1: the close uses W1-25's thresholds (MAX_AGE_MINUTES=240, MAX_COMMITS=20).

    Revised after implementation: the case imported the package into the test
    process and passed only where PYTHONPATH was set.
    """
    import subprocess, sys
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPATH": str(support.REPO_ROOT / "src"),
    }
    result = subprocess.run(
        [sys.executable, "-c",
         "from gov.checkpoint.command import MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT; "
         "print(MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT)"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, f"could not read W1-25 thresholds: {result.stderr}"
    values = result.stdout.strip().split()
    assert values == ["240", "20", "0.3"], \
        f"W1-25 thresholds should be 240, 20, 0.30: got {values}"
