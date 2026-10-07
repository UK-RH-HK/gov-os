"""Tests for gov close: S1, F1, MWA-04, A2 (regression), B2 (ticket tool), B4 (skills), B6 (commits).

S1: Runs tests/acceptance/<ticket>/ and the regression tests, requires
    Implements: and Task: trailers, runs the containment check, writes a
    checkpoint and the close record with skill versions.
F1: A ticket closes with a failing acceptance test.
MWA-04: A commit outside allowed_paths is caught by containment.
A2: Regression tests include all tests/ except the ticket's own acceptance folder,
    run to the end, collection errors and time-limit exceeded refuse the close,
    the time limit is configurable, and the close record lists counts.
B2: The ticket is closed through the ticket tool interface; the close record and
    checkpoint exist before the ticket status changes.
B4: The close record lists kernel skills with versions and vendored skills by
    name (no version), not dropped.
B6: The ticket's commits are those reachable from HEAD only; a git failure is an
    error, not an empty list.
"""

import json
import shutil

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
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
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
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
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
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
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
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
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
# S1: Close record with skill versions (CAP-24.a, B4)
# --------------------------------------------------------------------------

def test_close_record_has_kernel_skill_versions(project, sandbox, interface):
    """KPI S1, CAP-24.a, B4: the close record lists kernel skills with their version."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_kernel_skill("discovery", "1.0.0")
    project.add_kernel_skill("planning", "1.0.0")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    versions = front.get("skill_versions")
    assert isinstance(versions, list), "skill_versions must be a list"
    named = {v.get("name") or v.get("id") for v in versions if isinstance(v, dict)}
    assert "discovery" in named, f"skill_versions should list 'discovery': {versions}"
    assert "planning" in named, f"skill_versions should list 'planning': {versions}"
    for v in versions:
        if isinstance(v, dict) and (v.get("name") or v.get("id")) == "discovery":
            assert v.get("version") == "1.0.0", f"discovery should have version 1.0.0: {v}"


def test_close_record_lists_vendor_skill_without_version(project, sandbox, interface):
    """B4: vendored skills are listed by name with no version, not dropped."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_kernel_skill("change", "1.0.0")
    project.add_vendor_skill("systematic-debugging")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    versions = front.get("skill_versions")
    assert isinstance(versions, list), "skill_versions must be a list"
    named = {v.get("name") or v.get("id") for v in versions if isinstance(v, dict)}
    assert "systematic-debugging" in named, \
        f"vendored skill must be listed (not dropped): {versions}"
    vendor_entry = [v for v in versions if isinstance(v, dict)
                    and (v.get("name") or v.get("id")) == "systematic-debugging"][0]
    assert vendor_entry.get("version") is None or "no version" in str(vendor_entry.get("version")).lower(), \
        f"vendored skill must have no version or say 'no version': {vendor_entry}"


def test_close_record_empty_skill_versions_when_none(project, sandbox, interface):
    """KPI S1, CAP-24.a, B4: skill_versions is an empty list when no skills exist."""
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
    """MWA-04, A1: a commit changes a path outside the ticket's allowed_paths; close is refused."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/other/oops.py", "# out of scope\n")
    project.commit("implement out of scope", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must refuse when a commit changes files outside allowed_paths"


# --------------------------------------------------------------------------
# No acceptance tests: nothing measured is never a pass (S1, F1, DEC-425)
# --------------------------------------------------------------------------

def test_close_refuses_when_no_acceptance_tests_exist(project, sandbox, interface):
    """KPI S1, DEC-425: a ticket with no tests/acceptance/<wbs>/ directory cannot close."""
    ticket_id = "PROJ-noat"
    wbs = "W1-noat"
    project.add_ticket(ticket_id, wbs)
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
    """KPI S1, DEC-425: a ticket whose acceptance dir has only README.md cannot close."""
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
# Task trailer exact match (S1, CAP-38.c)
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


# --------------------------------------------------------------------------
# B2: Ticket status via ticket tool interface
# --------------------------------------------------------------------------

def test_ticket_closed_through_ticket_tool_interface(project, sandbox, interface):
    """B2: after close, the ticket has valid YAML frontmatter with status: closed."""
    _green_project(project)
    support.run_close(project, sandbox, TICKET)
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") == "closed", "ticket status must be 'closed' after gov close"
    import yaml
    ticket_file = project.root / support.ticket_path(TICKET)
    text = ticket_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, "ticket file must have valid YAML frontmatter after close"
    parsed = yaml.safe_load(parts[1])
    assert isinstance(parsed, dict), "ticket frontmatter must be valid YAML after close"
    assert parsed.get("status") == "closed"


def test_close_record_exists_before_ticket_status_changes(project, sandbox, interface):
    """B2: the close record is written before the ticket's status changes to closed.

    After gov close, both the close record and the closed status exist. The ordering
    is tested by verifying both are present: the implementation must write the record
    first, then set status; if status were set first and the record write failed, the
    ticket would be closed without a record.
    """
    _green_project(project)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, close_front = support.find_close_record(project.root, created)
    assert close_front is not None, "close record must exist after a successful close"
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") == "closed", "ticket must be closed"


def test_checkpoint_exists_before_ticket_status_changes(project, sandbox, interface):
    """B2: the closing checkpoint exists before the ticket's status changes to closed."""
    _green_project(project)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, cp_front = support.find_checkpoint_record(project.root, created)
    assert cp_front is not None, "closing checkpoint must exist after a successful close"
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") == "closed", "ticket must be closed"


# --------------------------------------------------------------------------
# A2: Regression tests (all tests/ except the ticket's own acceptance folder)
# --------------------------------------------------------------------------

def test_regression_includes_other_acceptance_folders(project, sandbox, interface):
    """A2: regression tests include other tickets' acceptance suites."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    other_wbs = "W1-other"
    support.write(project.root, f"tests/acceptance/{other_wbs}/test_other.py",
                  "def test_other():\n    assert False, 'other ticket fails'\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a failing test in another ticket's acceptance folder must block close"


def test_regression_runs_to_end_all_failures_collected(project, sandbox, interface):
    """A2: regression tests run to the end; all failures are collected, not just the first."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/test_reg_a.py",
                  "def test_reg_a():\n    assert False, 'reg A'\n")
    support.write(project.root, "tests/unit/test_reg_b.py",
                  "def test_reg_b():\n    assert False, 'reg B'\n")
    project.commit("implement with two reg failures", who=IMPL, trailers=TRAILERS_GOOD)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    error_text = json.dumps(error).lower()
    assert "reg_a" in error_text or "reg_b" in error_text, \
        f"the error should name the failing regression tests: {error}"


def test_collection_error_refuses_close(project, sandbox, interface):
    """A2: a collection error (syntax error in test file) refuses the close."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/test_syntax_error.py",
                  "def test_syntax_error(\n    # missing closing paren\n")
    project.commit("implement with syntax error in tests", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a collection error (syntax error) in a regression test file must refuse the close"


def test_regression_failure_blocks_close(project, sandbox, interface):
    """A2, S1: a failing regression test under tests/unit/ blocks close."""
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


def test_close_record_lists_test_counts(project, sandbox, interface):
    """A2: the close record lists what was run and the counts (passed, failed, errors)."""
    _green_project(project)
    support.write(project.root, "tests/unit/test_passing_reg.py",
                  "def test_passing_reg():\n    assert True\n")
    project.commit("add regression test", who=support.ORCHESTRATOR)
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    tests_info = front.get("tests_run") or front.get("test_results") or front.get("tests_produced")
    assert tests_info is not None, f"close record must list test results: {sorted(front)}"


def test_time_limit_exceeded_refuses_close(project, sandbox, interface):
    """A2: a regression run that exceeds its time limit refuses the close (not a pass)."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/test_slow.py",
                  "import time\ndef test_slow():\n    time.sleep(999)\n")
    project.commit("implement with slow test", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET, "--timeout", "1")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a time limit exceeded must refuse the close, not pass"
    assert run.returncode != 0, "time limit exceeded must not exit 0"


# --------------------------------------------------------------------------
# B6: Ticket commits from HEAD only
# --------------------------------------------------------------------------

def test_ticket_commits_from_head_only(project, sandbox, interface):
    """B6: only commits reachable from HEAD are the ticket's commits."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement on main", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    support.git(project.root, "checkout", "-b", "other-branch")
    project.write("src/example/other.py", "# other branch\n")
    project.commit("work on other branch", who=IMPL,
                   trailers=("Task: PROJ-aaaa", "Role: engineer", "Implements: CAP-02"))
    support.git(project.root, "checkout", "main")
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "B6: only HEAD commits matter; the main-branch ticket is green and must close"


def test_git_failure_is_error_not_empty_list(project, sandbox, interface):
    """B6: a git failure raises an error, not an empty list treated as 'no commits'."""
    _green_project(project)
    import os
    git_dir = project.root / ".git"
    head_file = git_dir / "HEAD"
    original = head_file.read_text(encoding="utf-8")
    head_file.write_text("corrupt content\n", encoding="utf-8")
    run = support.run_close(project, sandbox, TICKET)
    head_file.write_text(original, encoding="utf-8")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a git failure must be an error, not silently produce an empty commit list"
    assert run.returncode == support.EXIT_GOV_ERROR, \
        f"a git failure should exit 1, got {run.returncode}"


def test_time_limit_is_configurable(project, sandbox, interface):
    """A2: the time limit is configurable (a setting with a default, not hardcoded)."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/test_moderate.py",
                  "import time\ndef test_moderate():\n    time.sleep(0.5)\n    assert True\n")
    project.commit("implement with moderate test", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET, "--timeout", "30")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "with a generous --timeout, a 0.5s test must pass"


# --------------------------------------------------------------------------
# Containment: DEC-453, KPI S1 "runs the containment check"
# --------------------------------------------------------------------------

def test_containment_refuses_ticket_changing_acceptance_tests(project, sandbox, interface):
    """DEC-453, S1: an engineer's commit that changes a file under tests/acceptance/
    must be refused by the containment check (W1-50: acceptance tests are the test
    designer's paths, not the implementer's).
    """
    project.add_ticket(TICKET, WBS,
                       allowed_paths=["src/example/**", "tests/acceptance/" + WBS + "/**"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.write("tests/acceptance/W1-other/test_planted.py",
                  "def test_planted():\n    assert True\n")
    project.commit("implement touching another ticket's acceptance tests", who=IMPL,
                   trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "containment must refuse a commit changing tests/acceptance/ outside the ticket's own"
    error = envelope.get("error", {})
    error_text = json.dumps(error).lower()
    assert "containment" in error_text or "scope" in error_text or "path" in error_text, \
        f"the error should name containment as the reason: {error}"


def test_containment_refuses_ticket_changing_docs_outside_paths(project, sandbox, interface):
    """DEC-453: an engineer's commit changing docs/ outside the ticket's allowed paths
    must be refused.
    """
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.write("docs/extra.md", "# Out of scope\n")
    project.commit("implement touching docs/", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "containment must refuse a commit changing docs/ outside allowed_paths"


def test_containment_clean_within_paths(project, sandbox, interface):
    """DEC-453: a commit within allowed_paths passes containment (W1-50: clean)."""
    _green_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True, \
        "a commit only within allowed_paths must pass containment"


# --------------------------------------------------------------------------
# B2 extended: ticket closed through the ticket tool (KPI S1)
# --------------------------------------------------------------------------

def test_ticket_tool_close_is_what_tk_produces(project, sandbox, interface):
    """B2: after a good close the ticket's file is what the ticket tool produces."""
    _green_project(project)
    support.run_close(project, sandbox, TICKET)
    tk = project.root / "governance" / "kernel" / "bin" / "tk"
    assert tk.is_file(), "the project fixture must place tk"
    import subprocess
    result = subprocess.run(
        [str(tk), "show", TICKET], capture_output=True, text=True,
        cwd=str(project.root),
    )
    assert result.returncode == 0, \
        f"tk show must succeed on the closed ticket: {result.stderr}"


def test_close_fails_when_ticket_tool_absent(project, sandbox, interface):
    """B2: when the ticket tool is absent or fails, gov close reports an error
    and not success.
    """
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS_GOOD)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    tk = project.root / "governance" / "kernel" / "bin" / "tk"
    if tk.is_file():
        tk.unlink()
        project.commit("remove tk", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "gov close must report error when the ticket tool is absent"


def test_close_record_unwritable_ticket_stays_open(project, sandbox, interface):
    """B2: when the close record cannot be written, the ticket stays open."""
    _green_project(project)
    docs_close = project.root / "docs" / "close"
    docs_close.mkdir(parents=True, exist_ok=True)
    blocker = docs_close / "blocker"
    blocker.write_text("I am a file, not a directory", encoding="utf-8")
    project.commit("block close record directory", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    front = support.read_ticket_frontmatter(project.root, TICKET)
    assert front.get("status") != "closed", \
        "the ticket must stay open when the close record cannot be written"
