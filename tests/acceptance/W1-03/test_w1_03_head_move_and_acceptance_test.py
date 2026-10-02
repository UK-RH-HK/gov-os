"""W1-03 — an acceptance test changed in a call that also moves ``HEAD`` is restored from the pre-call ``HEAD``.

KPI success 2: "Changes under tests/acceptance/** by a non-test-designer role
are restored from HEAD and the breach is recorded". KPI failure 2.

DEC-143 (owner answer to KD-6): "When a non-designer changes an acceptance test
in the same call as a non-forward ``HEAD`` move, the test is restored from the
pre-call ``HEAD`` recorded in the snapshot, when attribution is certain. The
``HEAD`` move itself is still flagged and never reverted."

Each test makes one whole Bash call: PreToolUse hook, command, PostToolUse
hook. The command moves ``HEAD`` in a way that is not a move forward on the
same branch (DEC-129) and writes under ``tests/acceptance`` next to it.

- **Restored from the pre-call HEAD:** after the check, each acceptance test
  the call wrote holds the content the pre-call ``HEAD`` holds for it, and a
  test that commit does not hold is gone.
- **The move is never reverted:** ``HEAD`` and the branch are where the call
  left them, and so is every path outside ``tests/acceptance``.
- **Flagged:** the call adds a finding with action ``flagged`` for the move,
  next to the one that says ``reverted`` for the acceptance test.
"""

from __future__ import annotations

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

NEW_TEST = f"{ACCEPTANCE}/{WBS}/test_written.py"
NEW_DIRECTORY = f"{ACCEPTANCE}/W1-77"
NEW_DIRECTORY_TEST = f"{NEW_DIRECTORY}/test_new.py"
DESIGNER_AGENT = "agent-w1-03-designer"
ENGINEER_AGENT = "agent-w1-03-engineer"


def _history(project, acceptance_test_differs):
    """``main`` gets a second revision; a branch ``other`` leaves the first revision with a commit of its own.

    The second revision changes ``README.md`` and the engineer's source. With
    ``acceptance_test_differs`` it changes the acceptance test too, so the test
    reads ``VALUE = 2`` at ``main`` and ``VALUE = 1`` at every other commit.
    """
    first = support.git(project, "rev-parse", "HEAD").strip()
    (project / "README.md").write_text("# Fixture project\nsecond revision\n", encoding="utf-8")
    (project / SOURCE).write_text("VALUE = 2\n", encoding="utf-8")
    if acceptance_test_differs:
        (project / ACCEPTANCE_FILE).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "second revision")
    support.git(project, "checkout", "-q", "-b", "other", first)
    (project / "docs/spec/feature.md").write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "a commit on the other branch")
    support.git(project, "checkout", "-q", "main")


def _acceptance_tests_at(project, commit):
    """Every file under ``tests/acceptance`` that ``commit`` holds, with its content."""
    names = support.git(project, "ls-tree", "-r", "--name-only", commit, "--", ACCEPTANCE).splitlines()
    return {name: support.git(project, "show", f"{commit}:{name}") for name in names}


def _acceptance_tests_in_the_tree(project):
    root = project / ACCEPTANCE
    return {str(path.relative_to(project)): path.read_text(encoding="utf-8")
            for path in sorted(root.rglob("*")) if path.is_file() and not path.is_symlink()}


def _outside_acceptance(status):
    return [line for line in status.splitlines() if ACCEPTANCE not in line]


def _call(project, sandbox, command, role=None, ticket=None, subagent=None, agent_id=None, snapshot=True):
    """One whole call -> (result, pre-call HEAD commit, the state the command left behind)."""
    seen = len(support.finding_lines(project))
    before = support.head(project)
    call = support.script_call(sandbox, command)
    if snapshot:
        guard = support.run_guard(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                                  agent_id=agent_id)
        support.assert_let_through(guard, call)
    bash = support.run_bash(project, call.command, sandbox)
    left = support.state(project)
    assert left[0] != before, (
        f"the fixture command `{command}` did not move HEAD: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
    )
    result = support.run_check(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                               agent_id=agent_id, bash=bash, seen=seen)
    return result, before[0], left


def _assert_restored_from_the_pre_call_head(project, result, pre_call_head, left, written, what):
    """DEC-143. ``written``: the paths under ``tests/acceptance`` the call wrote, changed or removed."""
    for path in written:
        assert path in left[1], f"the fixture command did not leave {path} changed; git status:\n{left[1]}"

    # Restored from the pre-call HEAD.
    then = _acceptance_tests_at(project, pre_call_head)
    now = _acceptance_tests_in_the_tree(project)
    assert now == then, (
        f"{what}: tests/acceptance is not what the pre-call HEAD holds.\n"
        f"pre-call HEAD: {then}\nafter the check: {now}"
    )
    assert not (project / NEW_DIRECTORY).exists(), f"{what}: the new directory {NEW_DIRECTORY} is still there"

    # The move is never reverted, and nothing outside tests/acceptance is touched.
    head, status, contents = left
    assert support.head(project) == head, (
        f"{what}: the check moved HEAD; it was {head} after the call and is {support.head(project)}"
    )
    assert _outside_acceptance(support.porcelain_all(project)) == _outside_acceptance(status), (
        f"{what}: the check changed the tree outside tests/acceptance:\n"
        f"after the call:\n{status}after the check:\n{support.porcelain_all(project)}"
    )
    for path, text in contents.items():
        if not path.startswith(ACCEPTANCE):
            assert support.read(project, path) == text, f"{what}: the check changed {path}"

    # The breach is reported and recorded as reverted; the move is flagged.
    support.assert_reported(result, *written, what=what)
    findings = support.assert_recorded(result, *written, what=what)
    for path in written:
        actions = [f["action"] for f in findings
                   if any(e == path or path.startswith(e + "/") for e in support.finding_paths(result, f))]
        assert support.REVERTED in actions, (
            f"{what}: no finding says {path} was reverted; the findings that name it say {actions}"
        )
    assert support.FLAGGED in [f["action"] for f in findings], (
        f"{what}: no finding with action `flagged`; the HEAD move is still flagged"
    )


# --------------------------------------------------------------------------
# The two commits hold the same acceptance tests
# --------------------------------------------------------------------------

# name: (command, the paths under tests/acceptance it writes)
SAME_TESTS_IN_BOTH_COMMITS = {
    "amended-commit-then-a-changed-test": (
        f"git commit -q --amend --no-edit && echo changed >> {ACCEPTANCE_FILE}", [ACCEPTANCE_FILE]),
    "amended-commit-of-own-work-then-a-new-test": (
        f"echo changed >> {SOURCE} && git commit -q --amend -am amended && echo new > {NEW_TEST}", [NEW_TEST]),
    "reset-hard-then-a-new-test": (f"git reset -q --hard HEAD~1 && echo new > {NEW_TEST}", [NEW_TEST]),
    "reset-hard-then-a-changed-test": (
        f"git reset -q --hard HEAD~1 && echo changed >> {ACCEPTANCE_FILE}", [ACCEPTANCE_FILE]),
    "checkout-of-another-branch-then-a-changed-test": (
        f"git checkout -q other && echo changed >> {ACCEPTANCE_FILE}", [ACCEPTANCE_FILE]),
    "checkout-of-an-older-revision-then-a-test-in-a-new-directory": (
        f"git checkout -q HEAD~1 && mkdir -p {NEW_DIRECTORY} && echo new > {NEW_DIRECTORY_TEST}",
        [NEW_DIRECTORY_TEST]),
    "changed-test-then-a-soft-reset": (
        f"echo changed >> {ACCEPTANCE_FILE} && git reset -q --soft HEAD~1", [ACCEPTANCE_FILE]),
    "mixed-reset-then-a-deleted-test": (f"git reset -q HEAD~1 && rm {ACCEPTANCE_FILE}", [ACCEPTANCE_FILE]),
    "rebase-then-a-changed-and-a-new-test": (
        f"git rebase -q other && echo changed >> {ACCEPTANCE_FILE} && echo new > {NEW_TEST}",
        [ACCEPTANCE_FILE, NEW_TEST]),
}


@pytest.mark.parametrize("case", sorted(SAME_TESTS_IN_BOTH_COMMITS), ids=sorted(SAME_TESTS_IN_BOTH_COMMITS))
def test_an_acceptance_test_changed_next_to_a_head_move_is_restored(project, sandbox, case):
    """DEC-143. The move cannot explain the change: both commits hold the same acceptance tests.

    After the check ``tests/acceptance`` shows no change in ``git status``, and
    the move stays.
    """
    command, written = SAME_TESTS_IN_BOTH_COMMITS[case]
    _history(project, acceptance_test_differs=False)
    result, pre_call_head, left = _call(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    _assert_restored_from_the_pre_call_head(project, result, pre_call_head, left, written, what)
    status = support.porcelain_all(project, ACCEPTANCE)
    assert status == "", f"{what}: tests/acceptance still shows a change in git status:\n{status}"


# name: (GOV_ROLE, GOV_TICKET, agent_type, agent_id). None of them is a test designer.
NOT_A_DESIGNER = {
    "orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, None, None),
    "no-role": (None, None, None, None),
    "engineer-subagent-in-orchestrator-session": (ORCHESTRATOR, TICKET, ENGINEER, ENGINEER_AGENT),
    "designer-subagent-in-a-session-without-a-role": (None, TICKET, DESIGNER, DESIGNER_AGENT),   # DEC-125
}


@pytest.mark.parametrize("case", sorted(NOT_A_DESIGNER), ids=sorted(NOT_A_DESIGNER))
def test_the_restore_next_to_a_head_move_holds_for_every_non_designer(project, sandbox, case):
    role, ticket, subagent, agent_id = NOT_A_DESIGNER[case]
    _history(project, acceptance_test_differs=False)
    command = f"git reset -q --hard HEAD~1 && echo changed >> {ACCEPTANCE_FILE} && echo new > {NEW_TEST}"
    result, pre_call_head, left = _call(project, sandbox, command, role, ticket, subagent=subagent,
                                        agent_id=agent_id)
    _assert_restored_from_the_pre_call_head(
        project, result, pre_call_head, left, [ACCEPTANCE_FILE, NEW_TEST],
        f"`{command}` with GOV_ROLE={role!r} agent_type={subagent!r}")


def test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else(project, sandbox):
    """KPI failure 2, KPI failure 1. The engineer's own change stays; an out-of-scope file stays and is flagged."""
    _history(project, acceptance_test_differs=False)
    command = (f"git commit -q --amend --no-edit && echo changed >> {ACCEPTANCE_FILE} "
               f"&& echo changed >> {SOURCE} && echo new > docs/new.md")
    result, pre_call_head, left = _call(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    _assert_restored_from_the_pre_call_head(project, result, pre_call_head, left, [ACCEPTANCE_FILE], what)
    assert support.read(project, SOURCE) == "VALUE = 2\nchanged\n", f"{what}: the in-scope change was reverted"
    assert support.read(project, "docs/new.md") == "new\n", f"{what}: docs/new.md was removed"
    support.assert_caught(result, "docs/new.md", what=what, action=support.FLAGGED)
    support.assert_not_recorded(result, SOURCE, what=what)
    assert set(support.porcelain_all(project).splitlines()) == {f" M {SOURCE}", "?? docs/new.md"}, (
        f"{what}: git status after the check:\n{support.porcelain_all(project)}"
    )


# --------------------------------------------------------------------------
# The two commits hold different content for the acceptance test
# --------------------------------------------------------------------------

# name: command. The acceptance test reads ``VALUE = 2`` at the pre-call HEAD and ``VALUE = 1`` where HEAD goes.
DIFFERENT_TESTS_IN_THE_TWO_COMMITS = {
    "reset-hard-then-a-changed-test": f"git reset -q --hard HEAD~1 && echo changed >> {ACCEPTANCE_FILE}",
    "checkout-of-another-branch-then-a-changed-test": f"git checkout -q other && echo changed >> {ACCEPTANCE_FILE}",
    "mixed-reset-then-a-deleted-test": f"git reset -q HEAD~1 && rm {ACCEPTANCE_FILE}",
    "soft-reset-then-a-changed-test": f"git reset -q --soft HEAD~1 && echo changed >> {ACCEPTANCE_FILE}",
}


@pytest.mark.parametrize("case", sorted(DIFFERENT_TESTS_IN_THE_TWO_COMMITS),
                         ids=sorted(DIFFERENT_TESTS_IN_THE_TWO_COMMITS))
def test_where_the_two_commits_differ_the_test_gets_the_content_of_the_pre_call_head(project, sandbox, case):
    """DEC-143: "restored from the pre-call HEAD recorded in the snapshot".

    The call wrote the test, so its content is neither commit's. After the
    check it reads ``VALUE = 2`` again, the committed content the call began
    with. ``HEAD`` stays where the call put it, so ``git status`` may show the
    test as a change, as after a mixed reset.
    """
    command = DIFFERENT_TESTS_IN_THE_TWO_COMMITS[case]
    _history(project, acceptance_test_differs=True)
    result, pre_call_head, left = _call(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    assert support.read(project, ACCEPTANCE_FILE) == "VALUE = 2\n", (
        f"{what}: {ACCEPTANCE_FILE} does not hold the content of the pre-call HEAD: "
        f"{support.read(project, ACCEPTANCE_FILE)!r}"
    )
    _assert_restored_from_the_pre_call_head(project, result, pre_call_head, left, [ACCEPTANCE_FILE], what)


# --------------------------------------------------------------------------
# What DEC-143 leaves as it was
# --------------------------------------------------------------------------

def test_the_test_designer_keeps_the_tests_it_writes_next_to_a_head_move(project, sandbox):
    """KPI failure 2. DEC-143 names a non-designer. The designer's move is flagged (DEC-131); its tests stay."""
    _history(project, acceptance_test_differs=False)
    command = f"git reset -q --hard HEAD~1 && echo changed >> {ACCEPTANCE_FILE} && echo new > {NEW_TEST}"
    result, _, left = _call(project, sandbox, command, DESIGNER, TICKET)
    what = f"`{command}` by the test designer"
    assert ACCEPTANCE_FILE in left[1] and NEW_TEST in left[1], f"the fixture command wrote no tests:\n{left[1]}"
    support.assert_flagged_and_nothing_reverted(project, result, left, what)
    assert support.read(project, NEW_TEST) == "new\n", f"{what}: the designer's new test is gone"


def test_without_a_before_snapshot_the_test_is_flagged_and_not_restored(project, sandbox):
    """DEC-143: "when attribution is certain". DEC-130, DEC-132: no before-snapshot means flag and never revert."""
    _history(project, acceptance_test_differs=False)
    first = support.script_call(sandbox, "ls -la")           # the hooks have seen HEAD once (DEC-134)
    support.assert_let_through(support.run_guard(project, first, sandbox, role=ENGINEER, ticket=TICKET), first)
    support.run_check(project, first, sandbox, role=ENGINEER, ticket=TICKET,
                      bash=support.run_bash(project, first.command, sandbox))
    command = f"git reset -q --hard HEAD~1 && echo changed >> {ACCEPTANCE_FILE}"
    result, _, left = _call(project, sandbox, command, ENGINEER, TICKET, snapshot=False)
    what = f"`{command}` by the engineer with no before-snapshot"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.FLAGGED)
    support.assert_flagged_and_nothing_reverted(project, result, left, what)


def test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored(project, sandbox):
    """DEC-143: "when attribution is certain". DEC-130: overlapping calls mean flag and never revert."""
    _history(project, acceptance_test_differs=False)
    running = support.script_call(sandbox, "ls -la")
    guard = support.run_guard(project, running, sandbox, role=ORCHESTRATOR, ticket=TICKET, subagent=DESIGNER,
                              agent_id=DESIGNER_AGENT)
    support.assert_let_through(guard, running)
    command = f"git commit -q --amend --no-edit && echo changed >> {ACCEPTANCE_FILE}"
    result, _, left = _call(project, sandbox, command, ORCHESTRATOR, TICKET, subagent=ENGINEER,
                            agent_id=ENGINEER_AGENT)
    what = f"`{command}` by the engineer subagent while the designer subagent's call is open"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.FLAGGED)
    support.assert_flagged_and_nothing_reverted(project, result, left, what)


def test_a_test_changed_before_the_call_is_not_put_back_next_to_a_head_move(project, sandbox, earlier_work):
    """DEC-124: a path changed before the call is never touched. The designer's uncommitted test keeps its work."""
    _history(project, acceptance_test_differs=False)
    draft = f"{ACCEPTANCE}/{WBS}/test_draft.py"
    earlier_work(project, f"echo '# designer' > {draft}", changed=[draft])
    command = f"git commit -q --amend --no-edit && echo '# engineer' >> {draft}"
    result, _, left = _call(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on the designer's uncommitted test"
    support.assert_caught(result, draft, what=what, action=support.FLAGGED)
    support.assert_flagged_and_nothing_reverted(project, result, left, what)
    assert support.read(project, draft) == "# designer\n# engineer\n", (
        f"{what}: {draft} was put back or removed: {support.read(project, draft)!r}"
    )
