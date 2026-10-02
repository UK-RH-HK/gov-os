"""W1-03 — on a tree that was already dirty, only this call's changes are acted on.

DEC-124: "Containment acts only on changes made by the current call. It
snapshots the changed-path set before the call (PreToolUse) and compares it
after (PostToolUse). Paths already changed before the call are never touched.
When attribution is uncertain, it flags and doesn't revert."

KPI success 1 and 2, KPI failure 1 and 2, read with that decision. From the
switch-over all roles work in one working tree (DEC-118, DEC-119), so the tree a
call starts in holds other roles' uncommitted work: the test designer's new
tests, the engineer's source.

In each test the earlier work is put in the tree first, with no hook: it was
there before the call under test began. Then one whole Bash call is made:
PreToolUse hook, command, PostToolUse hook.
"""

from __future__ import annotations

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE

# The test designer's uncommitted work: a changed test, a new staged test, and a new directory git does not track.
DESIGNER_WORK = (
    f"echo '# designer' >> {ACCEPTANCE_FILE} "
    f"&& echo draft > {ACCEPTANCE}/{WBS}/test_draft.py && git add {ACCEPTANCE}/{WBS}/test_draft.py "
    f"&& mkdir -p {ACCEPTANCE}/W1-77 && echo new > {ACCEPTANCE}/W1-77/test_new.py"
)
DESIGNER_PATHS = (ACCEPTANCE_FILE, f"{ACCEPTANCE}/{WBS}/test_draft.py", f"{ACCEPTANCE}/W1-77/test_new.py")

# The engineer's uncommitted work inside the ticket's paths.
ENGINEER_WORK = (
    f"echo '# engineer' >> {SOURCE} "
    "&& echo new > src/gov/guard/new_module.py && git add src/gov/guard/new_module.py"
)
ENGINEER_PATHS = (SOURCE, "src/gov/guard/new_module.py")


def _tree(project, paths):
    """What must not change: ``git status`` with every file listed, and the content of ``paths``."""
    return support.porcelain_all(project), {path: support.read(project, path) for path in paths}


def _assert_untouched(project, before, what):
    status, contents = before
    for path, text in contents.items():
        assert support.read(project, path) == text, (
            f"{what}: {path} was in the tree before the call and is changed or gone after the check"
        )
    assert support.porcelain_all(project) == status, (
        f"{what}: git status changed although the call changed nothing:\n"
        f"before:\n{status}after:\n{support.porcelain_all(project)}"
    )


# name: (GOV_ROLE, GOV_TICKET, agent_type)
LATER_CALLERS = {
    "orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, None),
    "engineer": (ENGINEER, TICKET, None),
    "product-spec": (PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, None),
    "auditor": (AUDITOR, support.AUDITOR_TICKET_ID, None),
    "no-role": (None, None, None),
    "engineer-subagent-in-orchestrator-session": (ORCHESTRATOR, TICKET, ENGINEER),
    "general-purpose-subagent-in-orchestrator-session": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "general-purpose"),
}


@pytest.mark.parametrize("case", sorted(LATER_CALLERS), ids=sorted(LATER_CALLERS))
def test_the_test_designer_s_uncommitted_tests_survive_another_role_s_call(project, earlier_work, after_bash,
                                                                           case):
    """The case that decided DEC-124: a later ``git status`` by anyone else must not undo the new tests."""
    role, ticket, subagent = LATER_CALLERS[case]
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    before = _tree(project, DESIGNER_PATHS)
    command = "git status --porcelain"
    result = after_bash(project, command, role, ticket, subagent=subagent)
    what = f"`{command}` with GOV_ROLE={role!r} agent_type={subagent!r}, after the test designer's uncommitted work"
    _assert_untouched(project, before, what)
    support.assert_silent(result, what)


def test_the_caller_s_own_change_is_judged_and_the_earlier_work_is_not(project, earlier_work, after_bash):
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    before = _tree(project, DESIGNER_PATHS)
    command = f"echo changed >> {SOURCE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[SOURCE])
    what = f"`{command}` by the engineer on {TICKET}, after the test designer's uncommitted work"
    support.assert_silent(result, what)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"
    for path, text in before[1].items():
        assert support.read(project, path) == text, f"{what}: the test designer's {path} was changed or removed"


def test_an_engineer_s_uncommitted_work_is_not_reported_after_another_role_s_call(project, earlier_work,
                                                                                  after_bash):
    """The engineer's paths are outside the orchestrator's ticket. The orchestrator's call did not change them."""
    earlier_work(project, ENGINEER_WORK, changed=ENGINEER_PATHS)
    before = _tree(project, ENGINEER_PATHS)
    for command in ("ls -la", "git status --porcelain"):
        result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
        what = f"`{command}` by the orchestrator, after the engineer's uncommitted work"
        _assert_untouched(project, before, what)
        support.assert_silent(result, what)


def test_an_out_of_scope_change_is_reported_once(project, after_bash):
    """The change is the first call's. Later calls that change nothing more have nothing to report."""
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    support.assert_caught(result, "README.md", what=f"`{command}` by the engineer on {TICKET}")
    for command in ("ls -la", f"echo changed >> {SOURCE}", "git status --porcelain"):
        result = after_bash(project, command, ENGINEER, TICKET)
        support.assert_silent(result, f"`{command}` by the engineer, one call after the out-of-scope change")
    assert len(support.finding_lines(project)) == 1, (
        "one out-of-scope change gave more than one finding over four calls: "
        f"{support.finding_lines(project)}"
    )


def test_only_the_new_change_is_reported_on_a_dirty_tree(project, earlier_work, after_bash):
    earlier_work(project, DESIGNER_WORK + " && echo '# someone' >> docs/notes.md",
                 changed=[*DESIGNER_PATHS, "docs/notes.md"])
    earlier = (*DESIGNER_PATHS, "docs/notes.md")
    before = _tree(project, earlier)
    command = f"echo changed >> README.md && echo changed >> {SOURCE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md", SOURCE])
    what = f"`{command}` by the engineer on {TICKET}, on a tree with other uncommitted work"
    support.assert_caught(result, "README.md", what=what)
    for path in (*earlier, SOURCE):
        assert path not in result.report, (
            f"{what}: the report names {path}, which this call did not change out of scope: {result.report!r}"
        )
    support.assert_not_recorded(result, *earlier, SOURCE, what=what)
    for path, text in before[1].items():
        assert support.read(project, path) == text, f"{what}: {path}, changed before the call, was touched"
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


@pytest.mark.parametrize("failed", [False, True], ids=["call-succeeded", "call-failed"])
def test_the_restore_takes_back_only_what_this_call_changed(project, earlier_work, after_bash, failed):
    """KPI success 2 on a dirty tree: ``tests/acceptance`` is put back as it was before the call."""
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    contents = {path: support.read(project, path) for path in DESIGNER_PATHS}
    status = support.porcelain_all(project, ACCEPTANCE)
    by_engineer = (f"{ACCEPTANCE}/{WBS}/test_by_engineer.py", f"{ACCEPTANCE}/W1-77/test_by_engineer.py")
    readme = f"{ACCEPTANCE}/{WBS}/README.md"
    command = (f"echo new > {by_engineer[0]} && echo new > {by_engineer[1]} && rm {readme}"
               + ("; exit 3" if failed else ""))
    result = after_bash(project, command, ENGINEER, TICKET, changed=[*by_engineer, readme], failed=failed)
    what = f"`{command}` by the engineer on {TICKET}, after the test designer's uncommitted work"
    for path in by_engineer:
        assert not (project / path).exists(), f"{what}: the engineer's new file {path} is still there"
    assert support.read(project, readme) == support.head_text(project, readme), (
        f"{what}: {readme}, deleted by the call, was not restored from HEAD"
    )
    for path, text in contents.items():
        assert support.read(project, path) == text, (
            f"{what}: the test designer's uncommitted {path} was changed or removed by the restore"
        )
    assert support.porcelain_all(project, ACCEPTANCE) == status, (
        f"{what}: tests/acceptance is not as it was before the call:\n"
        f"before:\n{status}after:\n{support.porcelain_all(project, ACCEPTANCE)}"
    )
    support.assert_caught(result, *by_engineer, readme, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, *DESIGNER_PATHS, what=what)


# name: (path, the earlier uncommitted change to it)
ALREADY_CHANGED = {
    "acceptance-test": (ACCEPTANCE_FILE, "# designer"),
    "file-outside-the-ticket-paths": ("docs/notes.md", "# someone"),
}


@pytest.mark.parametrize("case", sorted(ALREADY_CHANGED), ids=sorted(ALREADY_CHANGED))
def test_a_path_already_changed_before_the_call_is_never_put_back_to_head(project, earlier_work, after_bash,
                                                                         case):
    """The call changes a path that already held someone's uncommitted work. HEAD does not hold that work."""
    path, marker = ALREADY_CHANGED[case]
    earlier_work(project, f"echo '{marker}' >> {path}", changed=[path])
    command = f"echo '# engineer' >> {path}"
    after_bash(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on a path changed before the call"
    text = support.read(project, path)
    assert text is not None and marker in text, (
        f"{what}: the earlier uncommitted work in {path} is gone after the check: {text!r}"
    )
    assert path in support.porcelain(project), f"{what}: {path} was put back to HEAD"


def test_the_before_snapshot_leaves_no_trace_in_git_status(project, earlier_work, before_bash):
    call, guard = before_bash(project, "ls -la", ENGINEER, TICKET)
    support.assert_let_through(guard, call)
    assert support.porcelain_all(project) == "", (
        "the PreToolUse hook changed a clean working tree:\n" + support.porcelain_all(project)
    )
    earlier_work(project, DESIGNER_WORK + " && " + ENGINEER_WORK, changed=[*DESIGNER_PATHS, *ENGINEER_PATHS])
    before = _tree(project, (*DESIGNER_PATHS, *ENGINEER_PATHS))
    call, guard = before_bash(project, "ls -la", ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_let_through(guard, call)
    _assert_untouched(project, before, "the PreToolUse hook on a dirty tree")


# --------------------------------------------------------------------------
# "When attribution is uncertain, it flags and doesn't revert."
# --------------------------------------------------------------------------

def test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted(project, after_bash):
    """The PreToolUse hook never ran for this call (DEC-110: a timeout does not block the call)."""
    command = f"echo changed >> README.md && echo changed >> {ACCEPTANCE_FILE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md", ACCEPTANCE_FILE], snapshot=False)
    what = f"`{command}` by the engineer on {TICKET}, with no before-snapshot"
    support.assert_caught(result, "README.md", ACCEPTANCE_FILE, what=what, action=support.FLAGGED)
    for path in ("README.md", ACCEPTANCE_FILE):
        assert support.read(project, path).endswith("changed\n"), (
            f"{what}: {path} was reverted although the check cannot tell whose change it is"
        )


def test_without_a_before_snapshot_another_role_s_uncommitted_tests_are_not_restored(project, earlier_work,
                                                                                     after_bash):
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    before = _tree(project, DESIGNER_PATHS)
    command = "ls -la"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, snapshot=False)
    what = f"`{command}` by the orchestrator with no before-snapshot, after the test designer's uncommitted work"
    _assert_untouched(project, before, what)
    support.assert_caught(result, ACCEPTANCE, what=what, action=support.FLAGGED)


def test_without_a_before_snapshot_an_in_scope_change_is_still_silent(project, after_bash):
    command = f"echo changed >> {SOURCE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[SOURCE], snapshot=False)
    what = f"`{command}` by the engineer on {TICKET}, with no before-snapshot"
    support.assert_silent(result, what)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


def test_the_snapshot_of_an_earlier_call_is_not_used_for_a_later_one(project, earlier_work, after_bash):
    """Between two Bash calls the test designer writes tests with the Write tool. The second call has no snapshot."""
    result = after_bash(project, "ls -la", ENGINEER, TICKET)
    support.assert_silent(result, "`ls -la` by the engineer on a clean tree")
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    before = _tree(project, DESIGNER_PATHS)
    after_bash(project, "ls -la", ENGINEER, TICKET, snapshot=False)
    _assert_untouched(project, before,
                      "a call with no before-snapshot of its own, after an earlier call that had one")


# name: (subagent type, its command, the paths it changes)
OVERLAPPING = {
    "test-designer-writes-tests": (DESIGNER, DESIGNER_WORK, DESIGNER_PATHS),
    "engineer-works-inside-the-ticket-paths": (ENGINEER, ENGINEER_WORK, ENGINEER_PATHS),
}


@pytest.mark.parametrize("case", sorted(OVERLAPPING), ids=sorted(OVERLAPPING))
def test_a_change_made_by_an_overlapping_call_is_not_reverted(project, sandbox, before_bash, check, after_bash,
                                                             case):
    """Two calls run at the same moment: the orchestrator's begins, a subagent's whole call runs, the first ends.

    The first call's check sees changes it cannot attribute to that call.
    Whatever it reports, it must not undo the subagent's legitimate work.
    """
    subagent, command, paths = OVERLAPPING[case]
    outer, guard = before_bash(project, "sleep 0", ORCHESTRATOR, TICKET)
    support.assert_let_through(guard, outer)

    inner = after_bash(project, command, ORCHESTRATOR, TICKET, changed=paths, subagent=subagent)
    support.assert_silent(inner, f"the {subagent} subagent's own call, inside its scope")
    before = _tree(project, paths)

    bash = support.run_bash(project, outer.command, sandbox)
    check(project, outer, ORCHESTRATOR, TICKET, bash=bash)
    _assert_untouched(project, before,
                      f"the orchestrator's call that overlapped the {subagent} subagent's call")
