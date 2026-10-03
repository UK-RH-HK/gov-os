"""W1-03 — a call that moves ``HEAD`` is caught although ``git status`` is clean afterwards.

KPI success 3: "All nine Bash write forms from S0b2 I-06 are caught" (form 8 is
``git checkout`` and ``git reset --hard``). KPI success 1 and KPI failure 1.

Owner answer of 2026-10-02 to KD-4 (accepted, refined): containment also
snapshots ``HEAD`` before the call.

- If ``HEAD`` moves forward on the same branch (a normal commit), the paths in
  the new commits are checked against the allowed paths, and anything outside
  is flagged.
- Any other ``HEAD`` move (``git reset``, a checkout of another branch, a
  rebase) is flagged and never reverted.

Each test makes one whole Bash call: PreToolUse hook, command, PostToolUse
hook. "Flagged" is: reported to the agent and recorded with action ``flagged``.
"Never reverted" is: after the check ``HEAD``, the branch, ``git status`` and
the files are as the call left them. The check does not rewrite history either
way, so a commit that is flagged stays.
"""

from __future__ import annotations

import shutil

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE
WATCHED = ("README.md", ACCEPTANCE_FILE, SOURCE, "docs/notes.md", "docs/spec/feature.md")


def _state(project):
    """What the check must leave alone: where HEAD is, ``git status``, and the content of the watched files."""
    return support.head(project), support.porcelain_all(project), {p: support.read(project, p) for p in WATCHED}


@pytest.fixture()
def call(sandbox, before_bash, check):
    """``call(project, command, role, ticket, subagent=None, failed=False)`` -> (result, HEAD before, state after).

    One whole Bash call. ``state after`` is taken between the command and the
    PostToolUse hook: it is what the call left behind.
    """

    def _call(project, command, role=None, ticket=None, subagent=None, failed=False):
        seen = len(support.finding_lines(project))
        before = support.head(project)
        the_call, guard = before_bash(project, command, role, ticket, subagent=subagent)
        support.assert_let_through(guard, the_call)
        bash = support.run_bash(project, the_call.command, sandbox)
        left = _state(project)
        assert left[0] != before, (
            f"the fixture command `{command}` did not move HEAD: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
        )
        result = check(project, the_call, role, ticket, subagent=subagent, bash=bash, failed=failed, seen=seen)
        return result, before, left

    return _call


def _assert_left_as_the_call_left_it(project, left, what):
    head, status, contents = left
    assert support.head(project) == head, (
        f"{what}: the check moved HEAD; it was {head} after the call and is {support.head(project)}"
    )
    assert support.porcelain_all(project) == status, (
        f"{what}: the check changed the working tree or the index:\n"
        f"after the call:\n{status}after the check:\n{support.porcelain_all(project)}"
    )
    for path, text in contents.items():
        assert support.read(project, path) == text, f"{what}: the check changed {path}"


# --------------------------------------------------------------------------
# HEAD moves forward on the same branch: the paths of the new commits are checked
# --------------------------------------------------------------------------

def _branch_ahead(project):
    """A branch ``ahead``: the current revision plus one commit that changes a product-spec file."""
    support.git(project, "checkout", "-q", "-b", "ahead")
    (project / "docs/spec/feature.md").write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "a commit ahead of main")
    support.git(project, "checkout", "-q", "main")


# name: (command, the paths outside the engineer's ticket that the new commits hold, the paths inside it)
COMMITS_OUTSIDE = {
    "one-file": ("echo changed >> README.md && git commit -qam work", ["README.md"], []),
    "in-scope-and-outside-in-one-commit": (
        f"echo changed >> README.md && echo changed >> {SOURCE} && git commit -qam work", ["README.md"], [SOURCE]),
    "two-commits-in-one-call": (
        "echo changed >> README.md && git commit -qam one && echo changed >> docs/notes.md && git commit -qam two",
        ["README.md", "docs/notes.md"], []),
    "new-file": ("echo new > docs/new.md && git add docs/new.md && git commit -qm work", ["docs/new.md"], []),
    "deleted-file": ("git rm -q docs/notes.md && git commit -qm work", ["docs/notes.md"], []),
    "acceptance-test": (f"echo changed >> {ACCEPTANCE_FILE} && git commit -qam work", [ACCEPTANCE_FILE], []),
    "through-a-form-the-guard-cannot-see": (
        "perl -e 'open(my $f, \">>\", \"README.md\") or die; print $f \"changed\\n\"; close($f)' "
        "&& git commit -qam work", ["README.md"], []),
    "fast-forward-merge": ("git merge -q --ff-only ahead", ["docs/spec/feature.md"], []),
}


@pytest.mark.parametrize("case", sorted(COMMITS_OUTSIDE), ids=sorted(COMMITS_OUTSIDE))
def test_a_commit_of_a_path_outside_the_ticket_paths_is_flagged(project, call, case):
    command, outside, inside = COMMITS_OUTSIDE[case]
    if case == "fast-forward-merge":
        _branch_ahead(project)
    if case == "through-a-form-the-guard-cannot-see" and shutil.which("perl") is None:
        pytest.skip("perl is not installed on this machine")
    result, _, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    assert left[1] == "", f"the fixture command `{command}` left uncommitted changes:\n{left[1]}"
    support.assert_caught(result, *outside, what=what, action=support.FLAGGED)
    for path in inside:
        assert path not in result.report, f"{what}: the report names the in-scope file {path}: {result.report!r}"
    support.assert_not_recorded(result, *inside, what=what)
    _assert_left_as_the_call_left_it(project, left, what)


# name: (GOV_ROLE, GOV_TICKET, agent_type, command)
COMMITS_INSIDE = {
    "engineer-changed-file": (ENGINEER, TICKET, None, f"echo changed >> {SOURCE} && git commit -qam work"),
    "engineer-new-file": (
        ENGINEER, TICKET, None,
        "echo new > src/gov/guard/new_module.py && git add src/gov/guard/new_module.py && git commit -qm work"),
    "engineer-two-commits": (
        ENGINEER, TICKET, None,
        f"echo changed >> {SOURCE} && git commit -qam one && echo changed >> pyproject.toml && git commit -qam two"),
    "test-designer-acceptance-tests": (
        DESIGNER, TICKET, None,
        f"echo changed >> {ACCEPTANCE_FILE} && echo new > {ACCEPTANCE}/{WBS}/test_new.py "
        f"&& git add {ACCEPTANCE} && git commit -qm tests"),
    "orchestrator-on-its-own-ticket": (
        ORCHESTRATOR, ORCHESTRATOR_TICKET, None, "echo changed >> .claude/settings.json && git commit -qam work"),
    "engineer-subagent-in-orchestrator-session": (
        ORCHESTRATOR, TICKET, ENGINEER, f"echo changed >> {SOURCE} && git commit -qam work"),
    # DEC-156 / DEC-171 (W1-45): moved from NOT_THEIR_PATH; the orchestrator may
    # write README.md (not under tests/acceptance/**) and the commit is a record,
    # not a finding.  Rewrite: owner correction, DEC-156.
    "orchestrator-on-the-engineer-s-ticket": (
        ORCHESTRATOR, TICKET, None, "echo changed >> README.md && git commit -qam work"),
}


@pytest.mark.parametrize("case", sorted(COMMITS_INSIDE), ids=sorted(COMMITS_INSIDE))
def test_a_commit_inside_the_caller_s_paths_is_silent(project, call, case):
    """KPI failure 2. An ordinary commit of one's own work is no finding, and it stays."""
    role, ticket, subagent, command = COMMITS_INSIDE[case]
    result, _, left = call(project, command, role, ticket, subagent=subagent)
    what = f"`{command}` with GOV_ROLE={role!r} agent_type={subagent!r} on {ticket}"
    support.assert_silent(result, what)
    _assert_left_as_the_call_left_it(project, left, what)


# name: (GOV_ROLE, GOV_TICKET, agent_type). None of these callers may write README.md.
NOT_THEIR_PATH = {
    "no-role": (None, None, None),
    "engineer-without-a-ticket": (ENGINEER, None, None),
    # DEC-156 / DEC-171 (W1-45): the orchestrator case is moved to COMMITS_INSIDE;
    # the orchestrator may write README.md (not under tests/acceptance/**).
    # Rewrite: owner correction, DEC-156.
    "test-designer": (DESIGNER, TICKET, None),
    "general-purpose-subagent-in-engineer-session": (ENGINEER, TICKET, "general-purpose"),
    "engineer-subagent-in-a-session-without-a-role": (None, TICKET, ENGINEER),
}


@pytest.mark.parametrize("case", sorted(NOT_THEIR_PATH), ids=sorted(NOT_THEIR_PATH))
def test_the_commit_is_judged_by_the_caller_s_own_paths(project, call, case):
    role, ticket, subagent = NOT_THEIR_PATH[case]
    command = "echo changed >> README.md && git commit -qam work"
    result, _, left = call(project, command, role, ticket, subagent=subagent)
    what = f"`{command}` with GOV_ROLE={role!r} agent_type={subagent!r} GOV_TICKET={ticket!r}"
    support.assert_caught(result, "README.md", what=what, action=support.FLAGGED)
    _assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_and_an_uncommitted_change_in_one_call_are_both_caught(project, call):
    command = "echo changed >> README.md && git commit -qam work && echo changed >> docs/notes.md"
    result, _, _ = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what, action=support.FLAGGED)
    support.assert_caught(result, "docs/notes.md", what=what)


def test_a_commit_made_by_a_failed_call_is_flagged_too(project, call):
    command = "echo changed >> README.md; git commit -qam work; exit 3"
    result, _, left = call(project, command, ENGINEER, TICKET, failed=True)
    what = f"`{command}` (failed call) by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what, action=support.FLAGGED)
    _assert_left_as_the_call_left_it(project, left, what)


def test_committing_another_role_s_uncommitted_work_is_flagged(project, earlier_work, call):
    """``git commit -a`` sweeps up what other roles left uncommitted. The commit holds paths outside the ticket."""
    draft = f"{ACCEPTANCE}/{WBS}/test_draft.py"
    earlier_work(project, f"echo '# designer' >> {ACCEPTANCE_FILE} && echo draft > {draft} && git add {draft} "
                          "&& echo '# someone' >> docs/notes.md", changed=[ACCEPTANCE_FILE, draft, "docs/notes.md"])
    command = f"echo changed >> {SOURCE} && git commit -qam work"
    result, _, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on a tree with other roles' uncommitted work"
    support.assert_caught(result, ACCEPTANCE_FILE, draft, "docs/notes.md", what=what, action=support.FLAGGED)
    support.assert_not_recorded(result, SOURCE, what=what)
    _assert_left_as_the_call_left_it(project, left, what)
    assert "# designer" in support.read(project, ACCEPTANCE_FILE) and support.read(project, draft) == "draft\n", (
        f"{what}: the test designer's work, now committed, was changed by the check"
    )


def test_committing_only_one_s_own_paths_on_a_dirty_tree_is_silent(project, earlier_work, call):
    draft = f"{ACCEPTANCE}/{WBS}/test_draft.py"
    earlier_work(project, f"echo '# designer' >> {ACCEPTANCE_FILE} && echo draft > {draft} && git add {draft}",
                 changed=[ACCEPTANCE_FILE, draft])
    command = f"echo changed >> {SOURCE} && git commit -q -m work -- {SOURCE}"
    result, _, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on a tree with the test designer's uncommitted work"
    support.assert_silent(result, what)
    _assert_left_as_the_call_left_it(project, left, what)
    assert ACCEPTANCE_FILE in left[1] and draft in left[1], (
        f"the fixture command committed the test designer's work as well:\n{left[1]}"
    )


# --------------------------------------------------------------------------
# Any other HEAD move: flagged, never reverted
# --------------------------------------------------------------------------

def _history(project):
    """``main`` gets a second revision; a branch ``other`` leaves the first revision with a commit of its own."""
    first = support.git(project, "rev-parse", "HEAD").strip()
    (project / "README.md").write_text("# Fixture project\nsecond revision\n", encoding="utf-8")
    (project / ACCEPTANCE_FILE).write_text("VALUE = 2\n", encoding="utf-8")
    (project / SOURCE).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "second revision")
    support.git(project, "checkout", "-q", "-b", "other", first)
    (project / "docs/spec/feature.md").write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "a commit on the other branch")
    support.git(project, "checkout", "-q", "main")


# name: command
OTHER_MOVES = {
    "reset-hard-to-an-older-revision": "git reset -q --hard HEAD~1",
    "reset-mixed-to-an-older-revision": "git reset -q HEAD~1",
    "reset-soft-to-an-older-revision": "git reset -q --soft HEAD~1",
    "checkout-of-another-branch": "git checkout -q other",
    "switch-to-another-branch": "git switch -q other",
    "checkout-of-an-older-revision": "git checkout -q HEAD~1",
    "rebase-onto-another-branch": "git rebase -q other",
    "amended-commit": f"echo changed >> {SOURCE} && git commit -q --amend -am amended",
}


def _assert_flagged_and_not_reverted(project, result, left, what):
    assert result.outcome == "report", f"{what}: the HEAD move was not reported to the agent: {result.describe()}"
    findings = support.new_findings(result, what)
    assert findings, f"{what}: no finding was added to {support.FINDINGS_REL} for the HEAD move"
    actions = [finding["action"] for finding in findings]
    assert support.FLAGGED in actions and support.REVERTED not in actions, (
        f"{what}: the findings have the actions {actions}; a HEAD move is flagged and nothing is reverted"
    )
    _assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(OTHER_MOVES), ids=sorted(OTHER_MOVES))
def test_any_other_head_move_is_flagged_and_never_reverted(project, call, case):
    """The second revision changed an acceptance test. Whatever the move leaves of it, the check leaves alone."""
    _history(project)
    command = OTHER_MOVES[case]
    result, _, left = call(project, command, ENGINEER, TICKET)
    _assert_flagged_and_not_reverted(project, result, left, f"`{command}` by the engineer on {TICKET}")


# name: (GOV_ROLE, GOV_TICKET, agent_type)
EVERY_CALLER = {
    "orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, None),
    "test-designer": (DESIGNER, TICKET, None),
    "no-role": (None, None, None),
    "engineer-subagent-in-orchestrator-session": (ORCHESTRATOR, TICKET, ENGINEER),
}


@pytest.mark.parametrize("case", sorted(EVERY_CALLER), ids=sorted(EVERY_CALLER))
def test_a_head_move_is_flagged_whoever_makes_it(project, call, case):
    """ "Any other HEAD move": the answer names no role and no path that would make one acceptable."""
    role, ticket, subagent = EVERY_CALLER[case]
    _history(project)
    command = "git reset -q --hard HEAD~1"
    result, _, left = call(project, command, role, ticket, subagent=subagent)
    _assert_flagged_and_not_reverted(project, result, left,
                                     f"`{command}` with GOV_ROLE={role!r} agent_type={subagent!r}")


def test_a_reset_that_undoes_only_one_s_own_commit_is_flagged_too(project, call):
    """The commits that differ hold only the engineer's paths. It is still not a move forward."""
    (project / SOURCE).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "the engineer's own commit")
    command = "git reset -q --hard HEAD~1"
    result, _, left = call(project, command, ENGINEER, TICKET)
    _assert_flagged_and_not_reverted(project, result, left, f"`{command}` by the engineer on {TICKET}")


def test_a_mixed_reset_does_not_cost_an_acceptance_test_its_content(project, call):
    """After ``git reset HEAD~1`` the committed tests show as uncommitted changes. They are not this call's writes.

    Restoring them from the new HEAD would delete content that was committed.
    """
    _history(project)
    command = "git reset -q HEAD~1"
    result, _, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    assert ACCEPTANCE_FILE in left[1], f"the fixture command did not leave {ACCEPTANCE_FILE} as a change:\n{left[1]}"
    _assert_flagged_and_not_reverted(project, result, left, what)
    assert support.read(project, ACCEPTANCE_FILE) == "VALUE = 2\n", (
        f"{what}: {ACCEPTANCE_FILE} lost the content of the second revision"
    )
