"""Tests for gov close: S1 (CAP-13.a, CAP-24.a, CAP-38.a, CAP-38.c), F1, MWA-04.

S1: Runs tests/acceptance/<ticket>/ and the regression tests, requires
    Implements: and Task: trailers, runs the containment check, writes a
    checkpoint and the close record with skill versions.
F1: A ticket closes with a failing acceptance test.
MWA-04: A commit outside allowed_paths is caught by containment.
"""

import pytest

import w1_30_support as support

cli_support = support.cli_support


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

TICKET = "PROJ-aaaa"
WBS = "W1-test"
IMPL = support.IMPLEMENTER
TRAILERS_GOOD = ("Task: PROJ-aaaa", "Role: engineer", "Implements: CAP-01")


def _green_project(project, ticket_id=TICKET, wbs=WBS, profile="STANDARD"):
    """Set up a project whose ticket can close: passing tests, correct trailers."""
    project.add_ticket(ticket_id, wbs, profile=profile)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement feature", who=IMPL, trailers=TRAILERS_GOOD)
    if profile == "FULL":
        project.add_probe(ticket_id)
        project.commit("add probe", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# S1: Envelope (raw_project, skips on NOT_IMPLEMENTED)
# --------------------------------------------------------------------------

def test_close_returns_api_0002_envelope(raw_project, sandbox, interface):
    """KPI S1, CAP-13.a: the command returns the API-0002 envelope."""
    _green_project(raw_project)
    run = support.run_close(raw_project, sandbox, TICKET)
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.skip("gov close is not built yet")
    support.envelope_of(run, interface)


# --------------------------------------------------------------------------
# S1: A green ticket closes
# --------------------------------------------------------------------------

def test_close_succeeds_on_green_standard_ticket(project, sandbox, interface):
    """KPI S1, CAP-13.a: a STANDARD ticket with passing tests closes with exit 0."""
    _green_project(project)
    run = support.run_close(project, sandbox, TICKET)
    result = support.result_of(run, interface)
    assert result.get("ticket") == TICKET or TICKET in str(result)


def test_close_sets_ticket_status(project, sandbox, interface):
    """KPI S1, CAP-13.a: after close the ticket's status is closed."""
    _green_project(project)
    support.run_close(project, sandbox, TICKET)
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") == "closed"


# --------------------------------------------------------------------------
# S1: Runs acceptance tests (CAP-38.a)
# --------------------------------------------------------------------------

def test_close_runs_acceptance_tests(project, sandbox, interface):
    """KPI S1, CAP-38.a: gov close runs tests/acceptance/<ticket>/."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True


def test_close_runs_regression_tests_when_present(project, sandbox, interface):
    """KPI S1, CAP-38.a: regression tests under tests/unit/ are run too."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/close/test_regression.py",
                  "def test_regression():\n    assert True\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True


# --------------------------------------------------------------------------
# S1: Requires trailers (CAP-38.c)
# --------------------------------------------------------------------------

def test_close_requires_implements_trailer(project, sandbox, interface):
    """KPI S1, CAP-38.c: a ticket whose commits lack Implements: cannot close."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL,
                   trailers=("Task: PROJ-aaaa", "Role: engineer"))
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, "close should refuse a ticket without Implements: trailers"


def test_close_requires_task_trailer(project, sandbox, interface):
    """KPI S1, CAP-38.c: a commit for the ticket must carry Task: <ticket>."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL,
                   trailers=("Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, "close should refuse a ticket without Task: trailers"


# --------------------------------------------------------------------------
# S1: Runs the containment check (CAP-13.a)
# --------------------------------------------------------------------------

def test_close_runs_containment_check(project, sandbox, interface):
    """KPI S1, CAP-13.a: gov close runs the containment check on the ticket's commits."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True


# --------------------------------------------------------------------------
# S1: Writes a checkpoint on success (CAP-13.a)
# --------------------------------------------------------------------------

def test_close_writes_checkpoint_on_success(project, sandbox, interface):
    """KPI S1, CAP-13.a: a successful close writes a checkpoint record."""
    _green_project(project)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_checkpoint_record(project.root, created)
    assert front is not None, f"no checkpoint found among new files: {created}"
    assert front.get("task") == TICKET


# --------------------------------------------------------------------------
# S1: Close record with skill versions (CAP-24.a)
# --------------------------------------------------------------------------

def test_close_record_has_skill_versions(project, sandbox, interface):
    """KPI S1, CAP-24.a: the close record lists skill versions."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_skill("retrieval", "1.0.0")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    versions = front.get("skill_versions")
    assert isinstance(versions, list), "skill_versions must be a list"
    assert any(v.get("id") == "retrieval" for v in versions if isinstance(v, dict)), \
        f"skill_versions should list the 'retrieval' skill: {versions}"


def test_close_record_empty_skill_versions_when_none(project, sandbox, interface):
    """KPI S1, CAP-24.a: skill_versions is an empty list when no skills exist."""
    _green_project(project)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    versions = front.get("skill_versions")
    assert isinstance(versions, list), "skill_versions must be a list"
    assert versions == [], f"skill_versions should be empty: {versions}"


# --------------------------------------------------------------------------
# F1: A ticket with failing acceptance tests cannot close
# --------------------------------------------------------------------------

def test_close_refuses_when_acceptance_tests_fail(project, sandbox, interface):
    """KPI F1: a ticket closes with a failing acceptance test — this must be refused."""
    project.add_ticket(TICKET, WBS)
    project.add_failing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, "gov close must refuse when acceptance tests fail"
    assert run.returncode == support.EXIT_CHECK_FAILED


# --------------------------------------------------------------------------
# MWA-04: Containment blocks close when commit outside allowed_paths
# --------------------------------------------------------------------------

def test_containment_blocks_close_for_out_of_scope_commit(project, sandbox, interface):
    """MWA-04: a commit changes a path outside the ticket's allowed_paths; close is refused."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/other/oops.py", "# out of scope\n")
    project.commit("implement out of scope", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when a commit changes files outside allowed_paths"


# --------------------------------------------------------------------------
# Point 2 (MISSING): No acceptance tests closes green (S1, F1)
# DEC-425: nothing measured is never a pass.
# --------------------------------------------------------------------------

def test_close_refuses_when_no_acceptance_tests_exist(project, sandbox, interface):
    """KPI S1, DEC-425: a ticket with no tests/acceptance/<wbs>/ directory cannot close."""
    ticket_id = "PROJ-noat"
    wbs = "W1-noat"
    project.add_ticket(ticket_id, wbs)
    import shutil
    acc_dir = project.root / "tests" / "acceptance" / wbs
    if acc_dir.is_dir():
        shutil.rmtree(acc_dir)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement without acceptance tests", who=IMPL,
                   trailers=("Task: PROJ-noat", "Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when no acceptance test directory exists (DEC-425)"


def test_close_refuses_when_acceptance_dir_is_empty(project, sandbox, interface):
    """KPI S1, DEC-425: a ticket whose acceptance dir has only README.md (no test files) cannot close."""
    ticket_id = "PROJ-empt"
    wbs = "W1-empt"
    project.add_ticket(ticket_id, wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement with empty acceptance dir", who=IMPL,
                   trailers=("Task: PROJ-empt", "Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, ticket_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when the acceptance dir has no test files (DEC-425)"


# --------------------------------------------------------------------------
# Point 3 (WEAK): Regression test failure blocks close (S1, CAP-38.a)
# --------------------------------------------------------------------------

def test_close_refuses_when_regression_test_fails(project, sandbox, interface):
    """KPI S1, CAP-38.a, CAP-13.a: a failing regression test under tests/unit/ blocks close."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/close/test_regression_fail.py",
                  "def test_regression_fail():\n    assert False, 'regression broke'\n")
    project.commit("implement with broken regression", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when a regression test under tests/unit/ fails"


# --------------------------------------------------------------------------
# Point 8 (MISSING): Task trailer exact match, not substring (S1)
# --------------------------------------------------------------------------

def test_task_trailer_exact_match_not_substring(project, sandbox, interface):
    """KPI S1, CAP-38.c: Task: AB must not count as a commit of ticket A."""
    ticket_a = "PROJ-a"
    ticket_ab = "PROJ-ab"
    wbs_a = "W1-tka"
    wbs_ab = "W1-tkab"
    project.add_ticket(ticket_a, wbs_a)
    project.add_ticket(ticket_ab, wbs_ab)
    project.add_passing_test(wbs_a)
    project.add_passing_test(wbs_ab)
    project.write("src/example/feature_ab.py", "# feature for AB\n")
    project.commit("implement AB only", who=IMPL,
                   trailers=("Task: PROJ-ab", "Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, ticket_a)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a commit with Task: PROJ-ab must not match ticket PROJ-a (substring match bug)"


def test_ticket_closed_through_ticket_tool_interface(project, sandbox, interface):
    """KPI S1: after close, the ticket file has valid YAML frontmatter with status: closed."""
    _green_project(project)
    support.run_close(project, sandbox, TICKET)
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") == "closed", "ticket status must be 'closed' after gov close"
    import yaml
    ticket_path = project.root / support.ticket_path(TICKET)
    text = ticket_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, "ticket file must have valid YAML frontmatter after close"
    parsed = yaml.safe_load(parts[1])
    assert isinstance(parsed, dict), "ticket frontmatter must be valid YAML after close"
    assert parsed.get("status") == "closed"
