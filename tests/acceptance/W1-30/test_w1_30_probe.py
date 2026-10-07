"""Tests for the probe-record gate on FULL-profile tickets: S7 (CAP-38.f), A5.

S7: A FULL-profile ticket closes only with a post-green probe record made by a
    fresh reviewer session other than the implementer, commissioned and judged by
    the orchestrator; the reviewer wrote nothing to the repository (DEC-137).
A5: Checked against the repository, not believed:
    - No commit among the ticket's commits carries the reviewer's role in its
      Role trailer or names the reviewer's session.
    - No commit between the probed commit and HEAD carries the reviewer's role.
    - The probe record names the commit it probed; that commit is an ancestor of
      HEAD, and no commit of the ticket outside tests/ and docs/probes/ follows it.
    - The existing reviewer_wrote_nothing field is still required.
"""

import pytest
import yaml

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
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


def _full_project_with_probe(project, ticket_id=TICKET, wbs=WBS, **probe_kwargs):
    """A FULL-profile ticket that is green and has a valid probe record."""
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


def test_probe_reviewer_wrote_nothing_required(project, sandbox, interface):
    """KPI S7, CAP-38.f, A5: the reviewer_wrote_nothing field is still required."""
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
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, ticket_id)
    result = support.result_of(run, interface)
    assert result is not None


# --------------------------------------------------------------------------
# A5: Reviewer verification against the repository
# --------------------------------------------------------------------------

def test_reviewer_commit_in_ticket_commits_refused(project, sandbox, interface):
    """A5: a reviewer commit with the reviewer's Role in the ticket's commits -> refused."""
    project.add_ticket(TICKET, WBS, profile="FULL",
                       allowed_paths=["src/example/**", "tests/**", "docs/**"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.write("tests/acceptance/W1-probe/test_extra.py",
                  "def test_extra():\n    assert True\n")
    project.commit("reviewer also committed", who=support.REVIEWER,
                   trailers=("Task: PROJ-prob", "Role: independent-auditor"))
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    project.add_probe(TICKET, reviewer_session="reviewer-001")
    project.commit("add probe", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a reviewer commit in the ticket's commits must refuse close (A5)"


def test_reviewer_commit_between_probed_and_head_refused(project, sandbox, interface):
    """A5: a commit between the probed commit and HEAD with the reviewer's role -> refused."""
    _full_project_without_probe(project)
    probed = support.git(project.root, "rev-parse", "HEAD").strip()
    project.add_probe(TICKET, probed_commit=probed)
    project.commit("add probe", who=support.ORCHESTRATOR)
    project.write("docs/extra_note.md", "# note\n")
    project.commit("reviewer commit after probe", who=support.REVIEWER,
                   trailers=("Role: independent-auditor",))
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a reviewer commit between the probed commit and HEAD must refuse close (A5)"


def test_probe_must_name_probed_commit(project, sandbox, interface):
    """A5: the probe record must name the commit it probed (probed_commit field)."""
    _full_project_without_probe(project)
    probe_id = f"PR-{TICKET}"
    front = {
        "id": probe_id, "type": "probe", "status": "ACTIVE",
        "state_class": "NARRATIVE", "task": TICKET,
        "reviewer_session": "reviewer-001", "implementer_session": "impl-001",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator", "judged_by": "orchestrator",
        "judgement": "pass",
    }
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {probe_id} — Probe\n\nPost-green probe.\n"
    support.write(project.root, f"docs/probes/{TICKET}/{probe_id}.md", text)
    project.commit("add probe without probed_commit", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe without probed_commit must be refused (A5)"


def test_probed_commit_must_be_ancestor_of_head(project, sandbox, interface):
    """A5: the probed commit must be an ancestor of HEAD."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, probed_commit="0" * 40)
    project.commit("add probe with fake commit", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probed_commit that is not an ancestor of HEAD must be refused (A5)"


def test_ticket_commit_after_probed_commit_refused(project, sandbox, interface):
    """A5: a ticket commit outside tests/ and docs/probes/ after the probed commit -> refused.

    The probe is of a state; new implementation commits after the probe make it stale.
    """
    _full_project_without_probe(project)
    probed = support.git(project.root, "rev-parse", "HEAD").strip()
    project.add_probe(TICKET, probed_commit=probed)
    project.commit("add probe", who=support.ORCHESTRATOR)
    project.write("src/example/post_probe.py", "# new code after probe\n")
    project.commit("implement after probe", who=IMPL, trailers=TRAILERS)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a ticket commit outside tests/ and docs/probes/ after the probed commit is stale (A5)"


def test_reviewer_session_name_not_in_trailers(project, sandbox, interface):
    """A5: the reviewer session name must not appear in any commit's trailers."""
    _full_project_without_probe(project)
    reviewer_session = "reviewer-001"
    project.write("src/example/extra.py", "# extra\n")
    project.commit("extra commit naming reviewer session", who=IMPL,
                   trailers=TRAILERS + (f"Session: {reviewer_session}",))
    project.add_probe(TICKET, reviewer_session=reviewer_session)
    project.commit("add probe", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a commit naming the reviewer session must refuse close (A5)"


# --------------------------------------------------------------------------
# Probe-gate fail-open: missing fields must be rejected
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
        "probed_commit: abc123",
        "---",
        "",
        f"# {probe_id} — Probe record for {ticket_id}",
        "",
        "Post-green probe.",
        "",
    ]
    return "\n".join(lines)


def test_probe_missing_reviewer_wrote_nothing_field(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe that omits reviewer_wrote_nothing must be rejected."""
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, _probe_yaml_missing_reviewer_wrote_nothing(TICKET))
    project.commit("add probe missing reviewer_wrote_nothing",
                   who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe that omits reviewer_wrote_nothing must be rejected"


def test_probe_requires_commissioned_by_orchestrator(project, sandbox, interface):
    """KPI S7, CAP-38.f: commissioned_by must be 'orchestrator'."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, commissioned_by="engineer")
    project.commit("add probe bad commissioned_by", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with commissioned_by != 'orchestrator' must be rejected"


def test_probe_requires_judged_by_orchestrator(project, sandbox, interface):
    """KPI S7, CAP-38.f: judged_by must be 'orchestrator'."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, judged_by="engineer")
    project.commit("add probe bad judged_by", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with judged_by != 'orchestrator' must be rejected"


def test_probe_requires_judgement_present(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe with judged_by but no judgement field is refused."""
    _full_project_without_probe(project)
    probe_id = f"PR-{TICKET}"
    probed = support.git(project.root, "rev-parse", "HEAD").strip()
    front = {
        "id": probe_id, "type": "probe", "status": "ACTIVE",
        "state_class": "NARRATIVE", "task": TICKET,
        "reviewer_session": "reviewer-001", "implementer_session": "impl-001",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator", "judged_by": "orchestrator",
        "probed_commit": probed,
    }
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {probe_id} — Probe\n\nPost-green probe.\n"
    support.write(project.root, f"docs/probes/{TICKET}/{probe_id}.md", text)
    project.commit("add probe without judgement", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe with judged_by but no judgement field must be rejected"


def test_probe_malformed_yaml_is_refused(project, sandbox, interface):
    """KPI S7, CAP-38.f: a probe file with invalid YAML is refused."""
    _full_project_without_probe(project)
    probe_path = f"docs/probes/{TICKET}/PR-{TICKET}.md"
    project.write(probe_path, "---\ninvalid: yaml: [broken\n---\n\nBad probe.\n")
    project.commit("add malformed probe", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe file with invalid YAML must be refused, not skipped"
