"""Tests for the probe-record gate on FULL-profile tickets: S7 (CAP-38.f).

S7: A FULL-profile ticket closes only with a post-green probe record made by a
    fresh reviewer session other than the implementer, commissioned and judged by
    the orchestrator; the reviewer wrote nothing to the repository (DEC-137).
"""

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-prob"
WBS = "W1-probe"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-prob", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _full_project_without_probe(project, ticket_id=TICKET, wbs=WBS):
    """A FULL-profile ticket that is green but has no probe record."""
    project.add_ticket(ticket_id, wbs, profile="FULL")
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    return ticket_id


def _full_project_with_probe(project, ticket_id=TICKET, wbs=WBS, **probe_kwargs):
    """A FULL-profile ticket that is green and has a probe record."""
    _full_project_without_probe(project, ticket_id, wbs)
    project.add_probe(ticket_id, **probe_kwargs)
    project.commit("add probe", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# S7: FULL ticket requires probe record (CAP-38.f)
# --------------------------------------------------------------------------

def test_full_ticket_requires_probe_record(project, sandbox, interface):
    """KPI S7, CAP-38.f: a FULL ticket without a probe record cannot close."""
    _full_project_without_probe(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a FULL ticket without a probe record must not close"
    assert run.returncode in (support.EXIT_GOV_ERROR, support.EXIT_BLOCKED), \
        f"expected exit 1 or 4, got {run.returncode}"


def test_full_ticket_closes_with_valid_probe(project, sandbox, interface):
    """KPI S7, CAP-38.f: a FULL ticket with a valid probe record closes."""
    _full_project_with_probe(project)
    run = support.run_close(project, sandbox, TICKET)
    result = support.result_of(run, interface)
    assert result is not None


def test_probe_from_non_implementer(project, sandbox, interface):
    """KPI S7, CAP-38.f: the probe reviewer must not be the implementer."""
    _full_project_without_probe(project)
    project.add_probe(TICKET,
                      reviewer_session="impl-001",
                      implementer_session="impl-001")
    project.commit("add probe same reviewer", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe where reviewer == implementer must be rejected"


def test_probe_reviewer_wrote_nothing(project, sandbox, interface):
    """KPI S7, CAP-38.f: the reviewer wrote nothing to the repository."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, reviewer_wrote_nothing=False)
    project.commit("add probe reviewer wrote", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe whose reviewer wrote to the repository must be rejected"


def test_standard_profile_closes_without_probe(project, sandbox, interface):
    """KPI S7, CAP-38.f: a STANDARD-profile ticket does not need a probe record."""
    ticket_id = "PROJ-std1"
    wbs = "W1-std"
    project.add_ticket(ticket_id, wbs, profile="STANDARD")
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL,
                   trailers=("Task: PROJ-std1", "Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, ticket_id)
    result = support.result_of(run, interface)
    assert result is not None


# --------------------------------------------------------------------------
# Probe-gate fail-open: missing fields must be rejected (reviewer findings)
# --------------------------------------------------------------------------

def _probe_yaml_missing_reviewer_wrote_nothing(ticket_id):
    """A probe record that omits the reviewer_wrote_nothing field entirely."""
    probe_id = f"PR-{ticket_id}"
    lines = [
        "---",
        f"id: {probe_id}",
        "type: probe",
        "status: ACTIVE",
        "state_class: NARRATIVE",
        f"task: {ticket_id}",
        "reviewer_session: reviewer-001",
        "implementer_session: impl-001",
        "commissioned_by: orchestrator",
        "judged_by: orchestrator",
        "---",
        "",
        f"# {probe_id} — Probe record for {ticket_id}",
        "",
        "Post-green probe.",
        "",
    ]
    return "\n".join(lines)


def _probe_yaml_missing_implementer_session(ticket_id):
    """A probe record that omits the implementer_session field entirely."""
    probe_id = f"PR-{ticket_id}"
    lines = [
        "---",
        f"id: {probe_id}",
        "type: probe",
        "status: ACTIVE",
        "state_class: NARRATIVE",
        f"task: {ticket_id}",
        "reviewer_session: reviewer-001",
        "reviewer_wrote_nothing: true",
        "commissioned_by: orchestrator",
        "judged_by: orchestrator",
        "---",
        "",
        f"# {probe_id} — Probe record for {ticket_id}",
        "",
        "Post-green probe.",
        "",
    ]
    return "\n".join(lines)


def test_probe_missing_reviewer_wrote_nothing_field(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe that omits reviewer_wrote_nothing must be rejected.

    Bug: pf.get("reviewer_wrote_nothing", True) defaults to True when absent,
    so `not True` is False and the validation error is never raised.
    """
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, _probe_yaml_missing_reviewer_wrote_nothing(TICKET))
    project.commit("add probe missing reviewer_wrote_nothing",
                   who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe that omits reviewer_wrote_nothing must be rejected"
    assert run.returncode in (support.EXIT_GOV_ERROR, support.EXIT_BLOCKED), \
        f"expected exit 1 or 4, got {run.returncode}"


def test_probe_missing_implementer_session_field(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe that omits implementer_session must be rejected.

    Bug: pf.get("implementer_session", "") defaults to "", which differs from
    the reviewer_session value, so the independence check passes vacuously.
    """
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, _probe_yaml_missing_implementer_session(TICKET))
    project.commit("add probe missing implementer_session",
                   who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe that omits implementer_session must be rejected"
    assert run.returncode in (support.EXIT_GOV_ERROR, support.EXIT_BLOCKED), \
        f"expected exit 1 or 4, got {run.returncode}"


# --------------------------------------------------------------------------
# Point 4 (MISSING): commissioned_by / judged_by validation (S7, CAP-38.f)
# --------------------------------------------------------------------------

def test_probe_requires_commissioned_by_orchestrator(project, sandbox, interface):
    """KPI S7, CAP-38.f: commissioned_by must be 'orchestrator'; another value is refused."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, commissioned_by="engineer")
    project.commit("add probe bad commissioned_by", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with commissioned_by != 'orchestrator' must be rejected"


def test_probe_requires_judged_by_orchestrator(project, sandbox, interface):
    """KPI S7, CAP-38.f: judged_by must be 'orchestrator'; another value is refused."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, judged_by="engineer")
    project.commit("add probe bad judged_by", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with judged_by != 'orchestrator' must be rejected"


def test_probe_requires_judgement_present(project, sandbox, interface):
    """KPI S7, CAP-38.f: 'judged by the orchestrator' means a judgement must exist.

    A probe that has judged_by but no judgement field (or empty) is refused.
    """
    _full_project_without_probe(project)
    import yaml
    probe_id = f"PR-{TICKET}"
    front = {
        "id": probe_id, "type": "probe", "status": "ACTIVE",
        "state_class": "NARRATIVE", "task": TICKET,
        "reviewer_session": "reviewer-001", "implementer_session": "impl-001",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator", "judged_by": "orchestrator",
    }
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {probe_id} — Probe record for {TICKET}\n\nPost-green probe.\n"
    probe_path = f"docs/probes/{TICKET}/{probe_id}.md"
    project.write(probe_path, text)
    project.commit("add probe without judgement", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with judged_by but no judgement field must be rejected"


def test_probe_malformed_yaml_is_refused_by_name(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe file with invalid YAML is refused, naming the file."""
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, "---\ninvalid: yaml: [broken\n---\n\nBad probe.\n")
    project.commit("add malformed probe", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe file with invalid YAML must be refused, not skipped"


def test_probe_unreadable_file_is_refused(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe directory with an unparseable file is refused."""
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, "not a yaml frontmatter file at all\n")
    project.commit("add unparseable probe", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe directory with unparseable files must be refused, not skipped"
