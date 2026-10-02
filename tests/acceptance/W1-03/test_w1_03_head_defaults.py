"""W1-03 — the owner's defaults for three ``HEAD`` cases (DEC-132).

KPI success 1, KPI success 3 (form 8), KPI failure 1 and 2, read with DEC-129:
a forward move on the same branch has the paths of its new commits checked; any
other ``HEAD`` move is flagged and never reverted.

DEC-132 refines it:

- "Checking out a branch that points at the same commit isn't a ``HEAD`` move."
- "Creating a new branch and committing on it in one call is flagged."
- "A merge that isn't a fast-forward is flagged."

Its fourth default, a ``HEAD`` move with no before-snapshot, is tested in
``test_w1_03_probe_findings.py``.

Each test makes one whole Bash call: PreToolUse hook, command, PostToolUse
hook. "Flagged" is: reported to the agent and recorded with action ``flagged``,
whatever the paths of the commits are. "Never reverted" is: after the check
``HEAD``, the branch, ``git status`` and the files are as the call left them.
"""

from __future__ import annotations

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE


def _call(project, sandbox, command, role=None, ticket=None, subagent=None):
    """One whole call -> (result, where HEAD was before it, the state the command left behind)."""
    seen = len(support.finding_lines(project))
    before = support.head(project)
    call = support.script_call(sandbox, command)
    guard = support.run_guard(project, call, sandbox, role=role, ticket=ticket, subagent=subagent)
    support.assert_let_through(guard, call)
    bash = support.run_bash(project, call.command, sandbox)
    assert bash.returncode == 0, f"the fixture command `{command}` failed: {bash.stderr.strip()!r}"
    left = support.state(project)
    result = support.run_check(project, call, sandbox, role=role, ticket=ticket, subagent=subagent, bash=bash,
                               seen=seen)
    return result, before, left


# --------------------------------------------------------------------------
# A branch that points at the same commit
# --------------------------------------------------------------------------

# name: command. ``same`` is a branch at the commit ``main`` is at.
TO_A_BRANCH_AT_THE_SAME_COMMIT = {
    "checkout-of-an-existing-branch": "git checkout -q same",
    "switch-to-an-existing-branch": "git switch -q same",
    "checkout-of-a-new-branch": "git checkout -q -b fresh",
    "switch-to-a-new-branch": "git switch -q -c fresh",
}


def _assert_on_another_branch_at_the_same_commit(before, left, command):
    assert left[0][0] == before[0] and left[0][1] not in ("", before[1]), (
        f"the fixture command `{command}` did not check out another branch at the same commit: "
        f"HEAD was {before} and is {left[0]}"
    )


@pytest.mark.parametrize("case", sorted(TO_A_BRANCH_AT_THE_SAME_COMMIT), ids=sorted(TO_A_BRANCH_AT_THE_SAME_COMMIT))
def test_checking_out_a_branch_at_the_same_commit_is_no_head_move(project, sandbox, case):
    """DEC-132, first default. Nothing moved and nothing changed: nothing to report (KPI failure 2)."""
    support.git(project, "branch", "same")
    command = TO_A_BRANCH_AT_THE_SAME_COMMIT[case]
    result, before, left = _call(project, sandbox, command, ENGINEER, TICKET)
    _assert_on_another_branch_at_the_same_commit(before, left, command)
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_silent(result, what)
    support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(TO_A_BRANCH_AT_THE_SAME_COMMIT), ids=sorted(TO_A_BRANCH_AT_THE_SAME_COMMIT))
def test_changes_made_next_to_such_a_checkout_are_judged_as_on_any_call(project, sandbox, case):
    """It is no ``HEAD`` move, so "flagged and never reverted" does not apply to the call.

    The in-scope change is silent and stays, the out-of-scope change is caught,
    and the acceptance test is restored from HEAD (KPI success 1 and 2).
    """
    support.git(project, "branch", "same")
    command = (f"{TO_A_BRANCH_AT_THE_SAME_COMMIT[case]} && echo changed >> {SOURCE} "
               f"&& echo changed >> README.md && echo changed >> {ACCEPTANCE_FILE}")
    result, before, left = _call(project, sandbox, command, ENGINEER, TICKET)
    _assert_on_another_branch_at_the_same_commit(before, left, command)
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what)
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, SOURCE, what=what)
    assert support.read(project, ACCEPTANCE_FILE) == "VALUE = 1\n" and support.porcelain(project, ACCEPTANCE) == "", (
        f"{what}: {ACCEPTANCE_FILE} was not restored from HEAD"
    )
    assert support.read(project, SOURCE) == "VALUE = 1\nchanged\n", f"{what}: the in-scope change was reverted"
    assert support.head(project) == left[0], f"{what}: the check moved HEAD from {left[0]} to {support.head(project)}"


def test_a_later_commit_on_the_branch_checked_out_is_an_ordinary_commit(project, sandbox):
    """The checkout was one call. The commit in the next call moves forward on the branch that call began on."""
    result, before, left = _call(project, sandbox, "git checkout -q -b fresh", ENGINEER, TICKET)
    _assert_on_another_branch_at_the_same_commit(before, left, "git checkout -q -b fresh")
    support.assert_silent(result, "`git checkout -q -b fresh` by the engineer")
    command = f"echo changed >> {SOURCE} && git commit -qam work"
    result, before, left = _call(project, sandbox, command, ENGINEER, TICKET)
    assert left[0][0] != before[0] and left[0][1] == "fresh", f"the fixture command `{command}` did not commit"
    what = f"`{command}` by the engineer on the branch checked out one call earlier"
    support.assert_silent(result, what)
    support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A new branch and a commit on it in one call
# --------------------------------------------------------------------------

# name: (GOV_ROLE, GOV_TICKET, command). The first three commit only paths the caller may write.
NEW_BRANCH_AND_COMMIT = {
    "checkout-b-then-a-commit-of-own-work": (
        ENGINEER, TICKET, f"git checkout -q -b fresh && echo changed >> {SOURCE} && git commit -qam work"),
    "switch-c-then-a-commit-of-own-work": (
        ENGINEER, TICKET, f"git switch -q -c fresh && echo changed >> {SOURCE} && git commit -qam work"),
    "own-work-first-then-the-branch-and-the-commit": (
        ENGINEER, TICKET, f"echo changed >> {SOURCE} && git checkout -q -b fresh && git commit -qam work"),
    "two-commits-on-the-new-branch": (
        ENGINEER, TICKET,
        f"git checkout -q -b fresh && echo changed >> {SOURCE} && git commit -qam one "
        "&& echo changed >> pyproject.toml && git commit -qam two"),
    "a-commit-of-a-path-outside-the-ticket-paths": (
        ENGINEER, TICKET, "git checkout -q -b fresh && echo changed >> README.md && git commit -qam work"),
    "a-commit-of-an-acceptance-test-by-the-engineer": (
        ENGINEER, TICKET, f"git checkout -q -b fresh && echo changed >> {ACCEPTANCE_FILE} && git commit -qam work"),
    "the-test-designer-s-own-tests": (
        DESIGNER, TICKET, f"git checkout -q -b fresh && echo changed >> {ACCEPTANCE_FILE} && git commit -qam tests"),
    "the-orchestrator-on-its-own-ticket": (
        ORCHESTRATOR, ORCHESTRATOR_TICKET,
        "git checkout -q -b fresh && echo changed >> .claude/settings.json && git commit -qam work"),
}


@pytest.mark.parametrize("case", sorted(NEW_BRANCH_AND_COMMIT), ids=sorted(NEW_BRANCH_AND_COMMIT))
def test_a_new_branch_and_a_commit_on_it_in_one_call_is_flagged(project, sandbox, case):
    """DEC-132, second default; DEC-129, DEC-131: flagged whoever makes it, and never reverted.

    ``HEAD`` ends on another branch than the call began on, so this is no move
    forward on the same branch, also when the commit holds only the caller's
    own paths.
    """
    role, ticket, command = NEW_BRANCH_AND_COMMIT[case]
    result, before, left = _call(project, sandbox, command, role, ticket)
    assert left[0][0] != before[0] and left[0][1] == "fresh" and left[1] == "", (
        f"the fixture command `{command}` did not commit on a new branch; HEAD is {left[0]}, git status:\n{left[1]}"
    )
    assert support.git(project, "rev-parse", "main").strip() == before[0], "the fixture command moved `main`"
    support.assert_flagged_and_nothing_reverted(project, result, left,
                                                f"`{command}` with GOV_ROLE={role!r} on {ticket}")


# --------------------------------------------------------------------------
# A merge that is not a fast-forward
# --------------------------------------------------------------------------

def _diverged(project, path):
    """``main`` and a branch ``other`` each get a commit of their own. The one on ``other`` changes ``path``."""
    first = support.git(project, "rev-parse", "HEAD").strip()
    (project / "pyproject.toml").write_text("[project]\nname = \"fixture\"\nversion = \"2\"\n", encoding="utf-8")
    support.commit_all(project, "a commit on main")
    support.git(project, "checkout", "-q", "-b", "other", first)
    (project / path).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "a commit on the other branch")
    support.git(project, "checkout", "-q", "main")


def _ahead(project, path):
    """A branch ``other``: the current revision plus one commit that changes ``path``. It could be fast-forwarded."""
    support.git(project, "checkout", "-q", "-b", "other")
    (project / path).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "a commit ahead of main")
    support.git(project, "checkout", "-q", "main")


# name: (how the branches lie, the path the other branch's commit changes, command)
MERGES = {
    "diverged-branch-with-the-caller-s-own-path": (_diverged, SOURCE, "git merge -q --no-edit other"),
    "diverged-branch-with-a-path-outside-the-ticket-paths": (
        _diverged, "docs/spec/feature.md", "git merge -q --no-edit other"),
    "diverged-branch-with-an-acceptance-test": (_diverged, ACCEPTANCE_FILE, "git merge -q --no-edit other"),
    "no-ff-merge-of-a-branch-that-is-ahead": (_ahead, SOURCE, "git merge -q --no-ff --no-edit other"),
}


@pytest.mark.parametrize("case", sorted(MERGES), ids=sorted(MERGES))
def test_a_merge_that_is_not_a_fast_forward_is_flagged(project, sandbox, case):
    """DEC-132, third default: flagged, also when the merged commits hold only the caller's own paths.

    DEC-129: never reverted. The merged content stays, an acceptance test
    included: it is committed content, and the check does not rewrite history.
    """
    lay_out, path, command = MERGES[case]
    lay_out(project, path)
    result, before, left = _call(project, sandbox, command, ENGINEER, TICKET)
    assert left[0][0] != before[0] and left[0][1] == "main" and left[1] == "", (
        f"the fixture command `{command}` did not commit a merge on main; HEAD is {left[0]}, git status:\n{left[1]}"
    )
    assert support.read(project, path) == "VALUE = 2\n", f"the fixture command `{command}` did not bring in {path}"
    what = f"`{command}` by the engineer on {TICKET}"
    parents = support.git(project, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert len(parents) == 3, f"the fixture command `{command}` made no merge commit: {parents}"
    support.assert_flagged_and_nothing_reverted(project, result, left, what)


def test_a_fast_forward_merge_of_the_caller_s_own_paths_is_silent(project, sandbox):
    """The contrast, DEC-129: a fast-forward is a move forward on the same branch, judged by its commits' paths."""
    _ahead(project, SOURCE)
    command = "git merge -q --ff-only other"
    result, before, left = _call(project, sandbox, command, ENGINEER, TICKET)
    assert left[0][0] != before[0] and left[0][1] == "main", f"the fixture command `{command}` did not move HEAD"
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_silent(result, what)
    support.assert_left_as_the_call_left_it(project, left, what)
