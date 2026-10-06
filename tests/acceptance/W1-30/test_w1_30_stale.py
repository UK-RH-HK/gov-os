"""Tests for stale check evidence rejection: S4 (CAP-38.d).

S4: A ticket that changes governance files cannot close on check results recorded
    for another commit or inputs hash: gov close re-runs the checks or rejects the
    stale green evidence.
"""

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

def _project_with_governance_change(project, ticket_id=TICKET, wbs=WBS):
    """A project where the ticket's commits touch governance files."""
    project.add_ticket(ticket_id, wbs,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**"])
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    return ticket_id


# --------------------------------------------------------------------------
# S4: Stale evidence rejected for governance changes (CAP-38.d)
# --------------------------------------------------------------------------

def test_close_rejects_stale_check_results_after_governance_change(project, sandbox, interface):
    """KPI S4, CAP-38.d: checks recorded at an old commit are rejected when governance changed."""
    _project_with_governance_change(project)
    run1 = support.run_close(project, sandbox, TICKET)
    support.envelope_of(run1, interface)
    project.write("template/governance/kernel/checks/extra.yaml",
                  'id: "extra"\nfamily: "schema/invariants"\ntier: "G1"\n'
                  'severity: "warning"\ncommand: "true"\n')
    project.commit("add governance check", who=IMPL, trailers=TRAILERS)
    run2 = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run2, interface)
    assert envelope["ok"] is False or run2.returncode != support.EXIT_OK, \
        "gov close must not accept stale check results after a governance change"


def test_close_accepts_checks_at_current_commit(project, sandbox, interface):
    """KPI S4, CAP-38.d: fresh check results at the current commit are accepted."""
    _project_with_governance_change(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "gov close should accept checks at the current commit"


def test_close_reruns_checks_when_commit_differs(project, sandbox, interface):
    """KPI S4, CAP-38.d: gov close re-runs checks when HEAD has moved since the last run."""
    _project_with_governance_change(project)
    support.run_close(project, sandbox, TICKET)
    project.write("src/example/extra.py", "# more code\n")
    project.commit("more work", who=IMPL, trailers=TRAILERS)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope is not None, "gov close must handle a changed HEAD"


def test_non_governance_change_does_not_require_rerun(project, sandbox, interface):
    """KPI S4, CAP-38.d: a non-governance change does not force a check re-run."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True


# --------------------------------------------------------------------------
# Point 9 (WEAK): Stale evidence after governance change, no prior close
# The existing test_close_rejects_stale_check_results_after_governance_change
# first closes the ticket (run1 succeeds), then the second attempt hits
# "already closed", not the stale-evidence check. This new case does NOT
# close first: it records green evidence (passing checks), then changes
# governance, then tries to close. Close must refuse because the evidence
# is stale.
# --------------------------------------------------------------------------

def test_stale_evidence_after_governance_change_without_prior_close(project, sandbox, interface):
    """KPI S4, CAP-38.d: stale evidence after a governance change blocks close (no prior close).

    Set up: ticket has passing tests and a governance file in its commits.
    Run gov check (evidence recorded). Then change a governance file and
    commit. Then run gov close. The close must refuse because the check
    evidence is stale (recorded at an old commit / old inputs hash).
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

    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False or run.returncode != support.EXIT_OK, \
        "gov close must refuse stale evidence after a governance change (no prior close)"
