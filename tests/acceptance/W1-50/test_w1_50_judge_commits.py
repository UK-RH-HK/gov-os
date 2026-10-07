"""W1-50 — a public, read-only judgement of commits by their trailers (DEC-453).

``gov.guard.containment.judge_commits`` judges a list of commits by their
trailers exactly as the post-command check judges the commits of an
orchestrator session's own call (DEC-453), and returns the findings.

``gov.guard.containment.ContainmentError`` is raised for an empty list, an
unknown commit id, a path that is not a repository, or a git failure: nothing
judged is never "no finding" (DEC-425).

Red reason for every case: ``judge_commits`` and ``ContainmentError`` do not
exist in ``gov.guard.containment``.
"""

from __future__ import annotations

import json
import os

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET
AS_ENGINEER = support.AS_ENGINEER
AS_DESIGNER = support.AS_DESIGNER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS
OWNER = support.OWNER

SOURCE = support.SOURCE
README = support.README
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
NEW_TEST = support.NEW_TEST
NOTES = support.NOTES
BOOTSTRAP = support.BOOTSTRAP


# ── helpers ──────────────────────────────────────────────────────────


def _judge(project, commit_ids):
    """Import and call ``judge_commits``; the ImportError is the red reason."""
    from gov.guard.containment import judge_commits

    return judge_commits(str(project), commit_ids)


def _error_class():
    """Import ``ContainmentError``; the ImportError is the red reason."""
    from gov.guard.containment import ContainmentError

    return ContainmentError


def _head(project):
    return check_support.head(project)[0]


def _hook_finding_for(result, commit_id):
    """The sorted relative paths the hook flagged for this commit, or None when silent."""
    for line in result.new_lines:
        data = json.loads(line)
        reason = data.get("reason", "")
        if f"commit {commit_id[:12]}" in reason:
            return sorted(check_support.finding_paths(result, data))
    return None


def _func_finding_for(findings, commit_id):
    """The sorted paths the function returned for this commit, or None when no finding."""
    for f in findings:
        if f.commit == commit_id:
            return sorted(f.paths)
    return None


def _assert_equality(project, result, commit_ids, what):
    """Assert ``judge_commits`` and the hook agree for every named commit."""
    findings = _judge(project, commit_ids)
    for cid in commit_ids:
        hook = _hook_finding_for(result, cid)
        func = _func_finding_for(findings, cid)
        assert hook == func, (
            f"{what}: commit {cid[:12]} — hook {hook}, function {func}"
        )


# ── case 1: same judgement as the post-command check ─────────────────


SIMPLE = {
    "engineer-inside-paths": (AS_ENGINEER, SOURCE),
    "engineer-outside-paths": (AS_ENGINEER, README),
    "engineer-of-acceptance-test": (AS_ENGINEER, ACCEPTANCE_FILE),
    "test-designer-inside-acceptance": (AS_DESIGNER, NEW_TEST),
    "test-designer-outside-acceptance": (AS_DESIGNER, SOURCE),
    "no-trailers-of-readme": (NO_TRAILERS, README),
    "no-trailers-of-acceptance-test": (NO_TRAILERS, ACCEPTANCE_FILE),
    "orchestrator-commit": (AS_ORCHESTRATOR, README),
}


@pytest.mark.parametrize("case", sorted(SIMPLE), ids=sorted(SIMPLE))
def test_the_function_s_answer_equals_the_hook_s_for_a_single_commit(project, sandbox, call, case):
    """Run the hook (orchestrator's own call) and the function on the same commit; they agree."""
    trailers, path = SIMPLE[case]
    command = support.commit(path, trailers)
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], f"case {case}")


def test_the_function_agrees_with_the_hook_for_a_worker_commit_of_a_ticket_file(project, sandbox, call):
    """DP-16: a change under ``.tickets/**`` in a commit with a worker's ``Role:`` trailer."""
    command = (
        support.widen_paths(TICKET)
        + " && " + support.change(README)
        + " && " + support.commit_paths([support.ticket_file(TICKET), README], AS_ENGINEER, subject="widen and work")
    )
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "worker commit of a ticket file")


def test_the_function_agrees_with_the_hook_for_two_role_values(project, sandbox, call):
    """DEC-268: several different ``Role`` values allow nothing."""
    command = support.commit_with(
        README,
        "--trailer", "Task: " + TICKET,
        "--trailer", "Role: " + ENGINEER,
        "--trailer", "Role: " + DESIGNER,
    )
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "two Role values")


def test_the_function_agrees_with_the_hook_for_two_task_values(project, sandbox, call):
    """DEC-268: several different ``Task`` values allow nothing."""
    command = support.commit_with(
        README,
        "--trailer", "Task: " + TICKET,
        "--trailer", "Task: " + ORCHESTRATOR_TICKET,
        "--trailer", "Role: " + ENGINEER,
    )
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "two Task values")


def test_the_function_agrees_with_the_hook_for_a_role_owner_commit(project, sandbox, call):
    """DEC-360: ``Role: owner`` is a finding in any agent's call."""
    command = support.commit_with(
        README,
        "--trailer", "Task: " + TICKET,
        "--trailer", "Role: " + OWNER,
    )
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "Role: owner")


def test_the_function_agrees_with_the_hook_for_a_ticket_not_in_progress(project, sandbox, call):
    """DEC-318: a commit naming a ticket that was never started is a finding."""
    support.closed_ticket(
        project, sandbox,
        (support.CLOSED_SOURCE, (ENGINEER, support.CLOSED_TICKET)),
    )
    command = support.commit(support.OPEN_SOURCE, (ENGINEER, support.OPEN_TICKET))
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "ticket not in progress")


def test_the_function_agrees_with_the_hook_for_a_closed_ticket_before_its_close_commit(project, sandbox, call):
    """DEC-318: the closed ticket's work commit, before its close commit, inside the ticket's paths, passes."""
    close = support.closed_ticket(
        project, sandbox,
        (support.CLOSED_SOURCE, (ENGINEER, support.CLOSED_TICKET)),
        (support.CLOSED_TEST, (DESIGNER, support.CLOSED_TICKET)),
    )
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    command = "git merge -q --ff-only main"
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    work_id = support.commit_of(project, support.CLOSED_SOURCE)
    assert support.is_ancestor(project, work_id, close)
    _assert_equality(project, result, [work_id], "closed ticket, before close")


def test_the_function_agrees_with_the_hook_for_a_closed_ticket_after_its_close_commit(project, sandbox, call):
    """DEC-318: a commit after the close commit naming the closed ticket is a finding."""
    support.closed_ticket(
        project, sandbox,
        (support.CLOSED_SOURCE, (ENGINEER, support.CLOSED_TICKET)),
    )
    command = support.commit(support.CLOSED_LATE_SOURCE, (ENGINEER, support.CLOSED_TICKET))
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    commit_id = _head(project)
    _assert_equality(project, result, [commit_id], "closed ticket, after close")


def test_the_function_agrees_with_the_hook_for_a_merge_with_own_change_of_a_ticket_file(project, sandbox, call):
    """DP-21: a merge commit's own change of a ticket file is a finding whatever its trailers."""
    support.ticket_branch(project, sandbox, (SOURCE, AS_ENGINEER), (NEW_TEST, AS_DESIGNER))
    command = support.merge_with_own_change(support.ticket_file(TICKET))
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    merge_id = _head(project)
    _assert_equality(project, result, [merge_id], "merge with own change of a ticket file")


def test_the_function_agrees_with_the_hook_for_a_merge_with_own_change_of_an_acceptance_test(project, sandbox, call):
    """DP-27: a merge commit's own change of an acceptance test is a finding whatever its trailers."""
    support.ticket_branch(project, sandbox, (SOURCE, AS_ENGINEER))
    command = support.merge_with_own_change(ACCEPTANCE_FILE)
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    merge_id = _head(project)
    _assert_equality(project, result, [merge_id], "merge with own change of an acceptance test")


def test_the_function_agrees_with_the_hook_for_a_clean_merge(project, sandbox, call):
    """A merge whose own change touches no ticket file and no acceptance test: no finding for the merge commit."""
    support.ticket_branch(project, sandbox, (SOURCE, AS_ENGINEER), (NEW_TEST, AS_DESIGNER))
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    merge_id = _head(project)
    _assert_equality(project, result, [merge_id], "clean merge")


# ── case 2: read-only ────────────────────────────────────────────────


def _gov_runtime_snapshot(project):
    """A dict {relative_path: content_bytes} for every file under ``.gov-runtime/``."""
    runtime = project / ".gov-runtime"
    snapshot = {}
    if runtime.is_dir():
        for dirpath, _dirs, filenames in os.walk(runtime):
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, project)
                with open(full, "rb") as fh:
                    snapshot[rel] = fh.read()
    return snapshot


def test_the_function_does_not_change_the_project(project, sandbox, tmp_path):
    """Read-only: HEAD, index, working tree, and ``.gov-runtime/`` are unchanged."""
    support.run(project, sandbox, support.commit(SOURCE, AS_ENGINEER))
    passing = _head(project)
    support.run(project, sandbox, support.commit(README, AS_ENGINEER))
    failing = _head(project)

    before_head = _head(project)
    before_status = check_support.porcelain_all(project)
    before_runtime = _gov_runtime_snapshot(project)

    fake_home = tmp_path / "judge_home"
    fake_home.mkdir()
    state_dir = fake_home / ".local" / "state" / "gov-os"

    old_home = os.environ.get("HOME")
    try:
        os.environ["HOME"] = str(fake_home)
        findings = _judge(project, [passing, failing])
    finally:
        if old_home is not None:
            os.environ["HOME"] = old_home
        else:
            os.environ.pop("HOME", None)

    assert _head(project) == before_head, "judge_commits moved HEAD"
    assert check_support.porcelain_all(project) == before_status, (
        "judge_commits changed the working tree or index"
    )
    assert _gov_runtime_snapshot(project) == before_runtime, (
        "judge_commits changed something under .gov-runtime/"
    )
    assert not state_dir.exists(), "judge_commits wrote under the state home"

    assert len(findings) == 1, f"expected one finding, got {len(findings)}"
    assert findings[0].commit == failing


# ── case 3: several commits, mixed ───────────────────────────────────


def test_a_list_of_clean_and_finding_commits_returns_exactly_the_findings_in_order(project, sandbox):
    """Clean commits and findings in a specific order; the function returns only the findings, in that order."""
    support.run(project, sandbox, support.commit(SOURCE, AS_ENGINEER))
    clean_1 = _head(project)
    support.run(project, sandbox, support.commit(README, AS_ENGINEER))
    finding_1 = _head(project)
    support.run(project, sandbox, support.commit(NEW_TEST, AS_DESIGNER))
    clean_2 = _head(project)
    support.run(project, sandbox, support.commit(ACCEPTANCE_FILE, AS_ENGINEER))
    finding_2 = _head(project)

    findings = _judge(project, [clean_1, finding_1, finding_2, clean_2])
    assert len(findings) == 2, f"expected 2 findings, got {len(findings)}"
    assert findings[0].commit == finding_1, (
        f"first finding is for {findings[0].commit[:12]}, expected {finding_1[:12]}"
    )
    assert findings[1].commit == finding_2, (
        f"second finding is for {findings[1].commit[:12]}, expected {finding_2[:12]}"
    )
    assert README in findings[0].paths, f"first finding does not name {README}"
    assert ACCEPTANCE_FILE in findings[1].paths, (
        f"second finding does not name {ACCEPTANCE_FILE}"
    )


# ── case 4: nothing judged is an error ───────────────────────────────


def test_an_empty_list_of_commits_raises(project, sandbox):
    """Nothing judged is never "no finding" (DEC-425)."""
    support.run(project, sandbox, support.commit(SOURCE, AS_ENGINEER))
    with pytest.raises(_error_class()):
        _judge(project, [])


def test_an_unknown_commit_id_raises(project, sandbox):
    """A commit id that names no object is an error, not an empty result."""
    support.run(project, sandbox, support.commit(SOURCE, AS_ENGINEER))
    unknown = "0" * 40
    with pytest.raises(_error_class()):
        _judge(project, [unknown])


def test_a_path_that_is_not_a_repository_raises(tmp_path):
    """A path that is not a git repository is an error."""
    not_a_repo = tmp_path / "empty"
    not_a_repo.mkdir()
    with pytest.raises(_error_class()):
        _judge(not_a_repo, ["0" * 40])


# ── case 5: the freeze ──────────────────────────────────────────────
#
# While the project is frozen, every commit is a finding.  The post-command
# check uses two mechanisms:
#
#   - For a commit with both trailers and a valid ticket: the lambda ``fn``
#     in ``_judge_commit`` checks ``os.path.exists(FREEZE_FLAG)``; if it
#     exists, every path is denied (the lambda always returns False).
#
#   - For a commit without trailers, or whose ticket can't be loaded:
#     ``outside(role, tid, sub)`` calls ``decide``, which checks the freeze
#     through ``freeze_state`` and denies every path.
#
# The result is that no path is allowed while the freeze flag exists with the
# ``FROZEN`` marker, regardless of the commit's trailers or the ticket's
# ``allowed_paths``.  Every commit is a finding.


def test_every_commit_is_a_finding_while_the_project_is_frozen(project, sandbox):
    """While frozen, the check allows nothing: every commit is a finding."""
    support.run(project, sandbox, support.commit(SOURCE, AS_ENGINEER))
    engineer_id = _head(project)
    support.run(project, sandbox, support.commit(NEW_TEST, AS_DESIGNER))
    designer_id = _head(project)
    support.run(project, sandbox, support.commit(README, AS_ORCHESTRATOR))
    orchestrator_id = _head(project)

    freeze_path = project / ".gov-runtime" / "freeze"
    freeze_path.parent.mkdir(parents=True, exist_ok=True)
    freeze_path.write_bytes(b"FROZEN\n")

    findings = _judge(project, [engineer_id, designer_id, orchestrator_id])
    found_ids = {f.commit for f in findings}
    assert engineer_id in found_ids, (
        f"the engineer's commit {engineer_id[:12]} was not a finding while frozen"
    )
    assert designer_id in found_ids, (
        f"the test designer's commit {designer_id[:12]} was not a finding while frozen"
    )
    assert orchestrator_id in found_ids, (
        f"the orchestrator's commit {orchestrator_id[:12]} was not a finding while frozen"
    )
