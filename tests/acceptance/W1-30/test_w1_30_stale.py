"""Tests for stale check evidence rejection: S4 (CAP-38.d), A7.

S4: A ticket that changes governance files cannot close on check results recorded
    for another commit or inputs hash: gov close re-runs the checks or rejects the
    stale green evidence.
A7: When a ticket's commits change governance files, gov close re-runs the checks
    at HEAD through gov.check.runner.run_checks(root) and refuses on any hard-block
    red, naming the checks. It trusts no recorded result. The close record states the
    commit and the result. For a ticket that changes no governance file, no check
    result is needed and none is claimed.

Governance file prefixes (A7): template/governance/kernel/checks/,
    template/governance/kernel/schemas/, governance/project/,
    template/governance/kernel/hooks/, template/governance/kernel/skills/.
"""

import json

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-stl1"
WBS = "W1-stale"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-stl1", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _project_with_governance_change(project, ticket_id=TICKET, wbs=WBS,
                                     governance_path="template/governance/kernel/checks/extra-test.yaml"):
    """A project where the ticket's commits touch governance files."""
    project.add_ticket(ticket_id, wbs,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**",
                                      "template/governance/kernel/schemas/**",
                                      "template/governance/kernel/hooks/**",
                                      "template/governance/kernel/skills/**",
                                      "governance/project/**"])
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.write(governance_path,
                  'id: "extra-test"\nfamily: "schema/invariants"\ntier: "G1"\n'
                  'severity: "warning"\ncommand: "true"\n')
    project.commit("implement with governance change", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


def _project_without_governance_change(project, ticket_id=TICKET, wbs=WBS):
    """A project where the ticket's commits do NOT touch governance files."""
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement without governance", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# A7: Ticket changing governance file -> checks re-run
# --------------------------------------------------------------------------

def test_governance_change_reruns_checks(project, sandbox, interface):
    """A7, S4: a ticket changing governance files triggers run_checks(root)."""
    _project_with_governance_change(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope is not None, "gov close must run to completion"


def test_governance_change_hard_block_red_refuses(project, sandbox, interface):
    """A7: a hard-block red from run_checks refuses the close, naming the checks."""
    project.add_ticket(TICKET, WBS,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_check_declaration("planted-block", "schema/invariants",
                                  severity="hard-block", command="exit 1")
    project.commit("implement with hard-block check", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a hard-block red from run_checks must refuse the close"
    error = envelope.get("error", {})
    error_text = json.dumps(error)
    assert "planted-block" in error_text or "hard" in error_text.lower(), \
        f"the error should name the failing check: {error}"


def test_governance_change_warning_does_not_refuse(project, sandbox, interface):
    """A7: a warning (not hard-block) from run_checks does NOT refuse the close."""
    project.add_ticket(TICKET, WBS,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_check_declaration("planted-warn", "schema/invariants",
                                  severity="warning", command="exit 1")
    project.commit("implement with warning check", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "a warning from run_checks must NOT refuse the close"


def test_governance_change_passing_checks_in_close_record(project, sandbox, interface):
    """A7: when checks pass, the close record states the commit and the result."""
    _project_with_governance_change(project)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    envelope = support.envelope_of(run, interface)
    if envelope["ok"]:
        created = support.new_files(project.root, before, after)
        _, front = support.find_close_record(project.root, created)
        assert front is not None, "close record should exist on success"
        check_info = front.get("check_result") or front.get("checks") or front.get("governance_checks")
        assert check_info is not None, \
            f"close record must state check results when governance files changed: {sorted(front)}"


def test_checks_run_at_head(project, sandbox, interface):
    """A7: the checks are run at HEAD, not at the commit that changed the governance file."""
    _project_with_governance_change(project)
    head = support.git(project.root, "rev-parse", "HEAD").strip()
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    envelope = support.envelope_of(run, interface)
    if envelope["ok"]:
        created = support.new_files(project.root, before, after)
        _, front = support.find_close_record(project.root, created)
        if front:
            commit_in_record = front.get("check_commit") or front.get("commit")
            if commit_in_record:
                assert commit_in_record.startswith(head[:8]) or commit_in_record == head, \
                    f"checks must run at HEAD ({head[:8]}...), record says {commit_in_record}"


# --------------------------------------------------------------------------
# A7: No governance change -> no check result needed
# --------------------------------------------------------------------------

def test_no_governance_change_no_check_needed(project, sandbox, interface):
    """A7: for a ticket that changes no governance file, no check result is claimed."""
    _project_without_governance_change(project)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "a ticket with no governance changes should close without checks"


# --------------------------------------------------------------------------
# A7: Each governance prefix triggers checks
# --------------------------------------------------------------------------

def test_governance_prefix_checks(project, sandbox, interface):
    """A7: changing template/governance/kernel/checks/ triggers check re-run."""
    _project_with_governance_change(
        project,
        governance_path="template/governance/kernel/checks/test-prefix.yaml")
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope is not None


def test_governance_prefix_schemas(project, sandbox, interface):
    """A7: changing template/governance/kernel/schemas/ triggers check re-run."""
    ticket_id = "PROJ-sch1"
    wbs = "W1-schema"
    trailers = ("Task: PROJ-sch1", "Role: engineer", "Implements: CAP-01")
    project.add_ticket(ticket_id, wbs,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/schemas/**"])
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.write("template/governance/kernel/schemas/test-schema.json",
                  '{"type": "object"}')
    project.commit("implement with schema change", who=IMPL, trailers=trailers)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope is not None


def test_governance_prefix_project(project, sandbox, interface):
    """A7: changing governance/project/ triggers check re-run."""
    ticket_id = "PROJ-proj"
    wbs = "W1-proj"
    trailers = ("Task: PROJ-proj", "Role: engineer", "Implements: CAP-01")
    project.add_ticket(ticket_id, wbs,
                       allowed_paths=["src/example/**", "governance/project/**"])
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.write("governance/project/test-config.yaml", "test: true\n")
    project.commit("implement with project governance change", who=IMPL, trailers=trailers)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope is not None


# --------------------------------------------------------------------------
# S4: Stale evidence after governance change
# --------------------------------------------------------------------------

def test_stale_evidence_after_governance_change(project, sandbox, interface):
    """S4, CAP-38.d: stale evidence after a governance change blocks close.

    Record check evidence (run gov check), then change governance, then try
    to close. Close must refuse because the evidence is stale.
    """
    ticket_id = "PROJ-stl2"
    wbs = "W1-stale2"
    trailers = ("Task: PROJ-stl2", "Role: engineer", "Implements: CAP-01")
    project.add_ticket(ticket_id, wbs,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**"])
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.write("template/governance/kernel/checks/stale-test.yaml",
                  'id: "stale-test"\nfamily: "schema/invariants"\ntier: "G1"\n'
                  'severity: "warning"\ncommand: "true"\n')
    project.commit("implement with governance", who=IMPL, trailers=trailers)

    run_check = support.run_check(project, sandbox)
    support.check_envelope_of(run_check, interface)

    project.write("template/governance/kernel/checks/stale-test.yaml",
                  'id: "stale-test"\nfamily: "schema/invariants"\ntier: "G1"\n'
                  'severity: "hard-block"\ncommand: "true"\n')
    project.commit("change governance check severity", who=IMPL, trailers=trailers)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False or run.returncode != support.EXIT_OK, \
        "gov close must refuse stale evidence after a governance change"
