"""W1-03 — cases the review probe found after the check was built (DEC-136).

The orchestrator's review of W1-03 passed thirteen cases to the test designer
as described behaviours. Each test below states the KPI line and the decision
it is held to; the cases the specification does not settle are in the README
under "Specification gaps".

KPI success 1 and 2, KPI failure 1 and 2, read with:

- DEC-124: containment acts only on changes made by the current call; a path
  already changed before the call is never touched; uncertain attribution is
  flagged and not reverted.
- DEC-130: no before-snapshot or overlapping calls means flag and never
  revert; a path changed before the call is never restored.
- DEC-129, DEC-132: a forward ``HEAD`` move has the paths of its commits
  checked; any other move is flagged and never reverted; a ``HEAD`` move with
  no before-snapshot is flagged.
- DEC-122, extending DEC-110: the finding record, in the file the guard's
  failures go to.

Each test makes whole Bash calls: PreToolUse hook, command, PostToolUse hook.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import subprocess
import sys

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
ACCEPTANCE_README = f"{ACCEPTANCE}/{WBS}/README.md"
SOURCE = support.SOURCE_FILE
GUARD_DIR = "src/gov/guard"
WATCHED = ("README.md", ACCEPTANCE_FILE, SOURCE, "docs/notes.md", "docs/spec/feature.md")

# The test designer's uncommitted work: a changed test, a new staged test, and a new directory git does not track.
DRAFT = f"{ACCEPTANCE}/{WBS}/test_draft.py"
NEW_DIRECTORY_TEST = f"{ACCEPTANCE}/W1-77/test_new.py"
DESIGNER_WORK = (
    f"echo '# designer' >> {ACCEPTANCE_FILE} "
    f"&& echo draft > {DRAFT} && git add {DRAFT} "
    f"&& mkdir -p {ACCEPTANCE}/W1-77 && echo new > {NEW_DIRECTORY_TEST}"
)
DESIGNER_PATHS = (ACCEPTANCE_FILE, DRAFT, NEW_DIRECTORY_TEST)

DESIGNER_AGENT = "agent-w1-03-designer"
ENGINEER_AGENT = "agent-w1-03-engineer"


# --------------------------------------------------------------------------
# One Bash call, step by step
# --------------------------------------------------------------------------

def _begin(project, sandbox, command, role=None, ticket=None, subagent=None, agent_id=None, with_id=True):
    """The call begins: the PreToolUse hook runs and lets it through. Nothing else has happened yet."""
    call = support.script_call(sandbox, command)
    if not with_id:
        call = dataclasses.replace(call, tool_use_id=None)
    guard = support.run_guard(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                              agent_id=agent_id)
    support.assert_let_through(guard, call)
    return call


def _state(project):
    """Where HEAD is, ``git status`` with every file listed, and the content of the watched files."""
    return support.head(project), support.porcelain_all(project), {p: support.read(project, p) for p in WATCHED}


def _whole(project, sandbox, command, role=None, ticket=None, subagent=None, agent_id=None, changed=(),
           snapshot=True, pre_id=True, post_id=True):
    """One whole call -> (PostToolUse result, the state the command left behind).

    ``snapshot=False`` leaves the PreToolUse hook out. ``pre_id`` and
    ``post_id`` say whether that hook's input carries a ``tool_use_id``.
    """
    seen = len(support.finding_lines(project))
    if snapshot:
        call = _begin(project, sandbox, command, role, ticket, subagent=subagent, agent_id=agent_id,
                      with_id=pre_id)
    else:
        call = support.script_call(sandbox, command)
    bash = support.run_bash(project, call.command, sandbox)
    support.assert_changed(project, *changed, command=command)
    left = _state(project)
    call = dataclasses.replace(call, tool_use_id=call.tool_use_id if post_id else None)
    result = support.run_check(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                               agent_id=agent_id, bash=bash, seen=seen)
    return result, left


def _tree(project, paths):
    """What must not change: ``git status`` with every file listed, and the content of ``paths``."""
    return support.porcelain_all(project), {path: support.read(project, path) for path in paths}


def _assert_untouched(project, before, what):
    status, contents = before
    for path, text in contents.items():
        assert support.read(project, path) == text, (
            f"{what}: {path} was in the tree before the check and is changed or gone after it"
        )
    assert support.porcelain_all(project) == status, (
        f"{what}: git status changed:\nbefore:\n{status}after:\n{support.porcelain_all(project)}"
    )


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


def _assert_flagged_and_nothing_reverted(project, result, left, what):
    assert result.outcome == "report", f"{what}: nothing was reported to the agent: {result.describe()}"
    findings = support.new_findings(result, what)
    assert findings, f"{what}: no finding was added to {support.FINDINGS_REL}"
    actions = [finding["action"] for finding in findings]
    assert support.FLAGGED in actions and support.REVERTED not in actions, (
        f"{what}: the findings have the actions {actions}; the call is flagged and nothing is reverted"
    )
    _assert_left_as_the_call_left_it(project, left, what)


def _assert_acceptance_equals_head(project, what):
    """``tests/acceptance`` is HEAD again, and nothing in it is a symbolic link."""
    status = support.porcelain(project, ACCEPTANCE)
    assert status == "", f"{what}: tests/acceptance was not restored from HEAD; git status shows:\n{status}"
    for directory, names, files in os.walk(project / ACCEPTANCE):
        for name in (*names, *files):
            path = os.path.join(directory, name)
            assert not os.path.islink(path), f"{what}: {path} is a symbolic link after the check"
    for path in (ACCEPTANCE_FILE, ACCEPTANCE_README):
        assert support.read(project, path) == support.head_text(project, path), (
            f"{what}: {path} does not hold its HEAD content"
        )


def _files(project, directory):
    """Every file below ``directory`` with its content; a symbolic link is listed with its target."""
    found = {}
    root = project / directory
    for current, names, files in os.walk(root):
        for name in (*names, *files):
            path = os.path.join(current, name)
            rel = os.path.relpath(path, project)
            if os.path.islink(path):
                found[rel] = f"-> {os.readlink(path)}"
            elif os.path.isfile(path):
                with open(path, encoding="utf-8") as handle:
                    found[rel] = handle.read()
    return found


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


# --------------------------------------------------------------------------
# A path changed before the call, and changed again by it
# --------------------------------------------------------------------------

# name: (path, the earlier uncommitted change to it, the name the report and the finding must hold)
CHANGED_AGAIN = {
    "file-outside-the-ticket-paths": ("docs/notes.md", "echo '# someone' >> docs/notes.md", "docs/notes.md"),
    "new-file-outside-the-ticket-paths": (
        "docs/spec/draft.md", "echo '# someone' > docs/spec/draft.md", "docs/spec/draft.md"),
    "acceptance-test-the-designer-changed": (
        ACCEPTANCE_FILE, f"echo '# someone' >> {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
    "acceptance-test-new-and-staged": (DRAFT, f"echo '# someone' > {DRAFT} && git add {DRAFT}", DRAFT),
    "acceptance-test-in-a-new-directory": (
        NEW_DIRECTORY_TEST, f"mkdir -p {ACCEPTANCE}/W1-77 && echo '# someone' > {NEW_DIRECTORY_TEST}",
        f"{ACCEPTANCE}/W1-77"),
}


@pytest.mark.parametrize("case", sorted(CHANGED_AGAIN), ids=sorted(CHANGED_AGAIN))
def test_a_path_changed_before_the_call_and_again_by_it_is_flagged_and_not_put_back(project, sandbox,
                                                                                    earlier_work, case):
    """KPI failure 1: the call changed a path outside its scope, so there is a finding.

    DEC-124, DEC-130: the path held someone's uncommitted work before the call,
    so it is never put back to HEAD, an acceptance test included. The finding
    says ``flagged``, and the file is as the call left it.
    """
    path, earlier, name = CHANGED_AGAIN[case]
    earlier_work(project, earlier, changed=[path])
    command = f"echo '# engineer' >> {path}"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on a path changed before the call"
    support.assert_caught(result, name, what=what, action=support.FLAGGED)
    text = support.read(project, path)
    assert text is not None and "# someone" in text, (
        f"{what}: the earlier uncommitted work in {path} is gone after the check: {text!r}"
    )
    assert "# engineer" in text, (
        f"{what}: the finding says flagged, and the call's change to {path} is gone: {text!r}"
    )
    assert path in support.porcelain_all(project), f"{what}: {path} was put back to HEAD"


def test_only_the_path_changed_again_is_named(project, sandbox, earlier_work):
    """The other paths changed before the call were not changed by it: they are neither named nor touched."""
    earlier_work(project, DESIGNER_WORK + " && echo '# someone' >> docs/notes.md",
                 changed=[*DESIGNER_PATHS, "docs/notes.md"])
    before = _tree(project, DESIGNER_PATHS)
    command = "echo '# engineer' >> docs/notes.md"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, on a tree with other uncommitted work"
    support.assert_caught(result, "docs/notes.md", what=what, action=support.FLAGGED)
    support.assert_not_recorded(result, *DESIGNER_PATHS, what=what)
    for path in DESIGNER_PATHS:
        assert path not in result.report, f"{what}: the report names {path}, which this call did not change"
    _assert_untouched(project, before, what)


# name: command
STAGE_EVERYTHING = {
    "git-add-all": "git add -A",
    "git-add-dot": "git add .",
    "git-add-update": "git add -u",
    "after-a-change-of-its-own": f"echo changed >> {SOURCE} && git add -A",
}


@pytest.mark.parametrize("case", sorted(STAGE_EVERYTHING), ids=sorted(STAGE_EVERYTHING))
def test_staging_everything_leaves_the_test_designer_s_uncommitted_tests_intact(project, sandbox, earlier_work,
                                                                                case):
    """KPI failure 2. ``git add -A`` changes how ``git status`` shows the designer's tests, not what they hold.

    DEC-124: they were changed before the call, so they are never touched. A
    restore from HEAD would delete tests that exist nowhere else.
    """
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    contents = {path: support.read(project, path) for path in DESIGNER_PATHS}
    command = STAGE_EVERYTHING[case]
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}, after the test designer's uncommitted work"
    status = support.porcelain_all(project, ACCEPTANCE)
    for path, text in contents.items():
        assert support.read(project, path) == text, (
            f"{what}: the test designer's uncommitted {path} was changed or removed by the check"
        )
        assert path in status, f"{what}: {path} no longer shows as a change; git status:\n{status}"
    for finding in support.new_findings(result, what):
        under_acceptance = [p for p in support.finding_paths(result, finding) if p.startswith(ACCEPTANCE)]
        assert not (under_acceptance and finding["action"] == support.REVERTED), (
            f"{what}: a finding says {under_acceptance} was reverted; the designer's tests are to stay"
        )
    if case == "after-a-change-of-its-own":
        assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


# --------------------------------------------------------------------------
# A symbolic link under tests/acceptance that points into the caller's own paths
# --------------------------------------------------------------------------

# name: (command, the link, the name the report and the finding must hold)
LINKS = {
    "to-its-own-directory": (
        f"ln -s ../../../{GUARD_DIR} {ACCEPTANCE}/{WBS}/own", f"{ACCEPTANCE}/{WBS}/own", f"{ACCEPTANCE}/{WBS}/own"),
    "to-its-own-file": (
        f"ln -s ../../../{SOURCE} {ACCEPTANCE}/{WBS}/test_own.py",
        f"{ACCEPTANCE}/{WBS}/test_own.py", f"{ACCEPTANCE}/{WBS}/test_own.py"),
    "absolute-target": (
        f"ln -s \"$PWD/{GUARD_DIR}\" {ACCEPTANCE}/{WBS}/own", f"{ACCEPTANCE}/{WBS}/own", f"{ACCEPTANCE}/{WBS}/own"),
    "in-a-new-directory": (
        f"mkdir -p {ACCEPTANCE}/W1-77 && ln -s ../../../{GUARD_DIR} {ACCEPTANCE}/W1-77/own",
        f"{ACCEPTANCE}/W1-77/own", f"{ACCEPTANCE}/W1-77"),
}


@pytest.mark.parametrize("case", sorted(LINKS), ids=sorted(LINKS))
def test_a_link_the_engineer_makes_under_acceptance_tests_is_removed_and_its_target_stays(project, sandbox,
                                                                                         case):
    """KPI success 2: the link is a change under ``tests/acceptance/**`` by a non-test-designer.

    It is judged by where it is, not by where it points. Removing it must not
    reach through it: the engineer's own directory keeps every file.
    """
    command, link, name = LINKS[case]
    own = _files(project, GUARD_DIR)
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=[link])
    what = f"`{command}` by the engineer on {TICKET}"
    assert not os.path.lexists(project / link), f"{what}: the link {link} is still there after the check"
    _assert_acceptance_equals_head(project, what)
    assert _files(project, GUARD_DIR) == own, (
        f"{what}: removing the link changed {GUARD_DIR}, the directory it pointed into: "
        f"{sorted(_files(project, GUARD_DIR))}"
    )
    support.assert_caught(result, name, what=what, action=support.REVERTED)


def test_a_write_through_such_a_link_stays_where_it_really_is(project, sandbox):
    """The file is written through the link, so it lies in the engineer's own directory: in scope (KPI failure 2)."""
    link = f"{ACCEPTANCE}/{WBS}/own"
    written = f"{GUARD_DIR}/via_link.py"
    command = f"ln -s ../../../{GUARD_DIR} {link} && echo new > {link}/via_link.py"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=[link, written])
    what = f"`{command}` by the engineer on {TICKET}"
    assert not os.path.lexists(project / link), f"{what}: the link {link} is still there after the check"
    _assert_acceptance_equals_head(project, what)
    assert support.read(project, written) == "new\n", f"{what}: the in-scope file {written} was removed or changed"
    assert support.read(project, SOURCE) == "VALUE = 1\n", f"{what}: {SOURCE} was changed by the check"
    support.assert_caught(result, link, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, written, what=what)


def test_a_link_put_in_the_place_of_an_acceptance_test_is_replaced_by_the_test(project, sandbox):
    """The restore writes the test, not through the link: the engineer's file keeps its own change."""
    command = (f"echo own >> {SOURCE} && rm {ACCEPTANCE_FILE} "
               f"&& ln -s ../../../{SOURCE} {ACCEPTANCE_FILE}")
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE, SOURCE])
    what = f"`{command}` by the engineer on {TICKET}"
    _assert_acceptance_equals_head(project, what)
    assert support.read(project, SOURCE) == "VALUE = 1\nown\n", (
        f"{what}: the restore reached through the link into {SOURCE}: {support.read(project, SOURCE)!r}"
    )
    lines = set(support.porcelain_all(project).splitlines())
    assert lines == {f" M {SOURCE}"}, (
        f"{what}: git status after the check is not the engineer's own change alone: {sorted(lines)}"
    )
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, SOURCE, what=what)


def test_a_link_put_in_the_place_of_an_acceptance_directory_is_replaced_by_the_directory(project, sandbox):
    """The whole ticket directory becomes a link into the engineer's paths. The restored tests must not land there."""
    directory = f"{ACCEPTANCE}/{WBS}"
    command = f"rm -r {directory} && ln -s ../../{GUARD_DIR} {directory}"
    own = _files(project, GUARD_DIR)
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    assert not os.path.islink(project / directory), f"{what}: {directory} is still a link after the check"
    _assert_acceptance_equals_head(project, what)
    assert _files(project, GUARD_DIR) == own, (
        f"{what}: the restore reached through the link into {GUARD_DIR}: {sorted(_files(project, GUARD_DIR))}"
    )
    assert support.porcelain_all(project) == "", (
        f"{what}: the tree is not clean after the check:\n{support.porcelain_all(project)}"
    )
    support.assert_caught(result, ACCEPTANCE, what=what, action=support.REVERTED)


# --------------------------------------------------------------------------
# HEAD moves
# --------------------------------------------------------------------------

# name: command
MOVES_WITHOUT_A_SNAPSHOT = {
    "reset-hard-to-an-older-revision": "git reset -q --hard HEAD~1",
    "checkout-of-another-branch": "git checkout -q other",
    "commit-of-a-path-outside-the-ticket-paths": "echo changed >> docs/notes.md && git commit -qam work",
}


@pytest.mark.parametrize("case", sorted(MOVES_WITHOUT_A_SNAPSHOT), ids=sorted(MOVES_WITHOUT_A_SNAPSHOT))
def test_a_head_move_in_a_call_with_no_before_snapshot_is_flagged(project, sandbox, case):
    """DEC-132: "A HEAD move with no before-snapshot is flagged." DEC-130: and never reverted.

    The hooks saw ``HEAD`` one call earlier; DEC-134 accepts that a move with
    no snapshot is checked only against the last ``HEAD`` they saw.
    """
    _history(project)
    result, _ = _whole(project, sandbox, "ls -la", ENGINEER, TICKET)
    support.assert_silent(result, "`ls -la` by the engineer on a clean tree")
    command = MOVES_WITHOUT_A_SNAPSHOT[case]
    before = support.head(project)
    result, left = _whole(project, sandbox, command, ENGINEER, TICKET, snapshot=False)
    assert left[0] != before, f"the fixture command `{command}` did not move HEAD"
    _assert_flagged_and_nothing_reverted(project, result, left,
                                         f"`{command}` by the engineer with no before-snapshot")


# name: (command, the paths outside the engineer's ticket that the commit holds, the paths inside it)
COMMITTED_MOVES = {
    "out-of-an-out-of-scope-path-into-the-ticket-paths": (
        f"git mv docs/notes.md {GUARD_DIR}/notes.md && git commit -qm work",
        ["docs/notes.md"], [f"{GUARD_DIR}/notes.md"]),
    "moved-and-changed": (
        f"git mv docs/notes.md {GUARD_DIR}/notes.md && echo more >> {GUARD_DIR}/notes.md && git commit -qam work",
        ["docs/notes.md"], [f"{GUARD_DIR}/notes.md"]),
    "an-acceptance-test-into-the-ticket-paths": (
        f"git mv {ACCEPTANCE_FILE} {GUARD_DIR}/test_fixture.py && git commit -qm work",
        [ACCEPTANCE_FILE], [f"{GUARD_DIR}/test_fixture.py"]),
    "out-of-the-ticket-paths": (
        f"git mv {SOURCE} docs/decide.py && git commit -qm work", ["docs/decide.py"], [SOURCE]),
    "between-two-out-of-scope-paths": (
        "git mv docs/notes.md docs/spec/notes.md && git commit -qm work",
        ["docs/notes.md", "docs/spec/notes.md"], []),
}


@pytest.mark.parametrize("case", sorted(COMMITTED_MOVES), ids=sorted(COMMITTED_MOVES))
def test_a_commit_that_moves_a_file_has_both_ends_checked(project, sandbox, case):
    """DEC-129: the paths in the new commits are checked. A moved file is two paths: where it was, where it is.

    The commit takes the file away from the path it left; outside the caller's
    paths that end is flagged, also when git shows the commit as one rename.
    """
    command, outside, inside = COMMITTED_MOVES[case]
    before = support.head(project)
    result, left = _whole(project, sandbox, command, ENGINEER, TICKET)
    assert left[0] != before and left[1] == "", (
        f"the fixture command `{command}` did not commit the move; git status:\n{left[1]}"
    )
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, *outside, what=what, action=support.FLAGGED)
    support.assert_not_recorded(result, *inside, what=what)
    _assert_left_as_the_call_left_it(project, left, what)


# name: (the move, the change outside the ticket paths made in the same call, its path)
MOVE_AND_CHANGE = {
    "reset-and-a-new-file": ("git reset -q --hard HEAD~1", "echo new > docs/new.md", "docs/new.md"),
    "reset-and-a-changed-file": ("git reset -q --hard HEAD~1", "echo changed >> docs/notes.md", "docs/notes.md"),
    "checkout-of-another-branch-and-a-new-file": ("git checkout -q other", "echo new > docs/new.md", "docs/new.md"),
    "amended-commit-and-a-new-file": (
        f"echo changed >> {SOURCE} && git commit -q --amend -am amended", "echo new > docs/new.md", "docs/new.md"),
    "new-file-first-then-a-soft-reset": ("git reset -q --soft HEAD~1", "echo new > docs/new.md", "docs/new.md"),
}


@pytest.mark.parametrize("case", sorted(MOVE_AND_CHANGE), ids=sorted(MOVE_AND_CHANGE))
def test_a_change_next_to_a_head_move_that_is_not_forward_is_named_and_nothing_is_reverted(project, sandbox,
                                                                                          case):
    """KPI failure 1: the move must not hide what the call wrote outside its scope.

    DEC-129: the move is flagged and never reverted, so after the check the
    tree is as the call left it.
    """
    move, change, path = MOVE_AND_CHANGE[case]
    _history(project)
    command = f"{change} && {move}" if case.startswith("new-file-first") else f"{move} && {change}"
    before = support.head(project)
    result, left = _whole(project, sandbox, command, ENGINEER, TICKET)
    assert left[0] != before and path in left[1], (
        f"the fixture command `{command}` did not move HEAD and leave {path} changed; git status:\n{left[1]}"
    )
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, path, what=what, action=support.FLAGGED)
    _assert_flagged_and_nothing_reverted(project, result, left, what)


# --------------------------------------------------------------------------
# Names that are not ASCII
# --------------------------------------------------------------------------

# name: (path, committed before the call)
NOT_ASCII = {
    "new-file": ("docs/über-uns.md", False),
    "tracked-file-changed": ("docs/résumé.md", True),
    "another-script": ("docs/設計メモ.md", False),
    "name-with-a-space-too": ("docs/señal de prueba.md", False),
}


@pytest.mark.parametrize("case", sorted(NOT_ASCII), ids=sorted(NOT_ASCII))
def test_a_name_that_is_not_ascii_is_reported_and_recorded_as_written(project, sandbox, case):
    """KPI success 1. The agent and the record get the name of the file, not git's octal spelling of it."""
    path, committed = NOT_ASCII[case]
    if committed:
        (project / path).write_text("VALUE = 1\n", encoding="utf-8")
        support.commit_all(project, "a file with a name that is not ASCII")
    command = f"echo changed >> '{path}'"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_reported(result, path, what=what)
    recorded = [name for finding in support.new_findings(result, what)
                for name in support.finding_paths(result, finding)]
    assert recorded == [path], f"{what}: the recorded paths are {recorded}, not the one name as written"


@pytest.mark.parametrize("committed", [False, True], ids=["new-test", "tracked-test-changed"])
def test_an_acceptance_test_with_a_name_that_is_not_ascii_is_restored(project, sandbox, committed):
    """KPI success 2 holds for every file name."""
    path = f"{ACCEPTANCE}/{WBS}/test_prüfung.py"
    if committed:
        (project / path).write_text("VALUE = 1\n", encoding="utf-8")
        support.commit_all(project, "an acceptance test with a name that is not ASCII")
    command = f"echo changed >> '{path}'"
    seen = len(support.finding_lines(project))
    call = _begin(project, sandbox, command, ENGINEER, TICKET)
    bash = support.run_bash(project, call.command, sandbox)
    assert support.read(project, path).endswith("changed\n"), f"the fixture command `{command}` wrote nothing"
    result = support.run_check(project, call, sandbox, role=ENGINEER, ticket=TICKET, bash=bash, seen=seen)
    what = f"`{command}` by the engineer on {TICKET}"
    assert support.read(project, path) == ("VALUE = 1\n" if committed else None), (
        f"{what}: {path} was not restored from HEAD: {support.read(project, path)!r}"
    )
    _assert_acceptance_equals_head(project, what)
    support.assert_caught(result, path, what=what, action=support.REVERTED)


# --------------------------------------------------------------------------
# A hook input without tool_use_id
# --------------------------------------------------------------------------

# name: (the PreToolUse input has a tool_use_id, the PostToolUse input has one)
WITHOUT_AN_ID = {
    "neither-input-has-one": (False, False),
    "only-the-post-input-lacks-one": (True, False),
}


@pytest.mark.parametrize("case", sorted(WITHOUT_AN_ID), ids=sorted(WITHOUT_AN_ID))
def test_a_call_whose_hook_input_has_no_tool_use_id_is_checked_all_the_same(project, sandbox, case):
    """KPI success 1: "After every Bash call". KPI failure 1.

    The check cannot tie such a call to a before-snapshot with certainty. The
    tests take no side on ``action``; it must tell the truth.
    """
    pre_id, post_id = WITHOUT_AN_ID[case]
    command = f"echo changed >> README.md && echo changed >> {SOURCE}"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=["README.md", SOURCE],
                       pre_id=pre_id, post_id=post_id)
    what = f"`{command}` by the engineer on {TICKET}, {case}"
    support.assert_caught(result, "README.md", what=what)
    support.assert_not_recorded(result, SOURCE, what=what)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"

    command = f"echo changed >> {ACCEPTANCE_FILE}"
    result, _ = _whole(project, sandbox, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE],
                       pre_id=pre_id, post_id=post_id)
    what = f"`{command}` by the engineer on {TICKET}, {case}"
    findings = support.assert_caught(result, ACCEPTANCE_FILE, what=what)
    actions = {finding["action"] for finding in findings
               if ACCEPTANCE_FILE in support.finding_paths(result, finding)}
    restored = support.read(project, ACCEPTANCE_FILE) == support.head_text(project, ACCEPTANCE_FILE)
    assert actions == ({support.REVERTED} if restored else {support.FLAGGED}), (
        f"{what}: the finding says {sorted(actions)}, and {ACCEPTANCE_FILE} "
        f"{'holds its HEAD content' if restored else 'still holds the change'}"
    )


@pytest.mark.parametrize("case", sorted(WITHOUT_AN_ID), ids=sorted(WITHOUT_AN_ID))
def test_a_call_without_tool_use_id_does_not_cost_the_test_designer_its_uncommitted_tests(project, sandbox,
                                                                                          earlier_work, case):
    """KPI failure 2, DEC-124: whatever the check makes of such a call, earlier work is never put back to HEAD."""
    pre_id, post_id = WITHOUT_AN_ID[case]
    earlier_work(project, DESIGNER_WORK, changed=DESIGNER_PATHS)
    before = _tree(project, DESIGNER_PATHS)
    _whole(project, sandbox, "ls -la", ENGINEER, TICKET, pre_id=pre_id, post_id=post_id)
    _assert_untouched(project, before, f"`ls -la` by the engineer, {case}, after the test designer's work")


# --------------------------------------------------------------------------
# Calls and writes that overlap
# --------------------------------------------------------------------------

# name: (agent_type, agent_id) of the actor whose Bash call overlaps the test designer's work.
# The session is the orchestrator's, on the engineer's ticket.
OTHER_ACTORS = {
    "orchestrator-main-thread": (None, None),
    "engineer-subagent": (ENGINEER, ENGINEER_AGENT),
}


def _designer_file_tool(project, sandbox, tool_name, relpath, text):
    """The test designer subagent uses a file tool: the guard runs, lets it through, and the file is written."""
    path = project / relpath
    if tool_name == "Write":
        tool_input = {"file_path": str(path), "content": text}
    else:
        tool_input = {"file_path": str(path), "old_string": path.read_text(encoding="utf-8"),
                      "new_string": text, "replace_all": False}
    guard = support.run_guard_for_file_tool(project, sandbox, tool_name, tool_input, role=ORCHESTRATOR,
                                            ticket=TICKET, subagent=DESIGNER, agent_id=DESIGNER_AGENT)
    assert guard.decision == "allow", (
        f"the guard did not let the test designer subagent's {tool_name} of {relpath} through: {guard.describe()}"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.mark.parametrize("other", sorted(OTHER_ACTORS), ids=sorted(OTHER_ACTORS))
def test_a_file_tool_write_by_the_test_designer_during_another_actor_s_bash_call_survives(project, sandbox,
                                                                                          other):
    """KPI failure 2. The designer subagent writes tests with Write and Edit while someone's Bash call runs.

    That call's before-snapshot does not hold the new tests, and the call did
    not write them. DEC-130: overlapping work is never reverted.
    """
    agent_type, agent_id = OTHER_ACTORS[other]
    outer = _begin(project, sandbox, "sleep 0", ORCHESTRATOR, TICKET, subagent=agent_type, agent_id=agent_id)
    written = f"{ACCEPTANCE}/{WBS}/test_written.py"
    in_new_directory = f"{ACCEPTANCE}/W1-77/test_written.py"
    _designer_file_tool(project, sandbox, "Write", written, "written by the test designer\n")
    _designer_file_tool(project, sandbox, "Write", in_new_directory, "written by the test designer\n")
    _designer_file_tool(project, sandbox, "Edit", ACCEPTANCE_FILE, "VALUE = 1\n# edited by the test designer\n")
    before = _tree(project, (written, in_new_directory, ACCEPTANCE_FILE))

    bash = support.run_bash(project, outer.command, sandbox)
    support.run_check(project, outer, sandbox, role=ORCHESTRATOR, ticket=TICKET, subagent=agent_type,
                      agent_id=agent_id, bash=bash)
    _assert_untouched(project, before,
                      f"the {other}'s Bash call that ran while the test designer subagent used Write and Edit")


@pytest.mark.parametrize("order", ["designer-began-first", "other-began-first"])
@pytest.mark.parametrize("other", sorted(OTHER_ACTORS), ids=sorted(OTHER_ACTORS))
def test_a_test_written_by_the_designer_s_running_bash_call_survives_another_actor_s_check(project, sandbox,
                                                                                           other, order):
    """KPI failure 2. The designer subagent's Bash call is still running when another actor's call ends.

    The other call's check sees new acceptance tests that its before-snapshot
    does not hold. They are the running call's. DEC-130: never reverted. When
    the designer's call ends, its own tests are in scope: nothing to report.
    """
    agent_type, agent_id = OTHER_ACTORS[other]

    def begin_designer():
        return _begin(project, sandbox, DESIGNER_WORK, ORCHESTRATOR, TICKET, subagent=DESIGNER,
                      agent_id=DESIGNER_AGENT)

    def begin_other():
        return _begin(project, sandbox, "ls -la", ORCHESTRATOR, TICKET, subagent=agent_type, agent_id=agent_id)

    if order == "designer-began-first":
        designer_call, other_call = begin_designer(), begin_other()
    else:
        other_call, designer_call = begin_other(), begin_designer()

    designer_bash = support.run_bash(project, designer_call.command, sandbox)   # still running: no PostToolUse yet
    support.assert_changed(project, *DESIGNER_PATHS, command=DESIGNER_WORK)
    before = _tree(project, DESIGNER_PATHS)

    other_bash = support.run_bash(project, other_call.command, sandbox)
    support.run_check(project, other_call, sandbox, role=ORCHESTRATOR, ticket=TICKET, subagent=agent_type,
                      agent_id=agent_id, bash=other_bash)
    what = f"the {other}'s call that ended while the test designer subagent's call was running ({order})"
    _assert_untouched(project, before, what)

    seen = len(support.finding_lines(project))
    result = support.run_check(project, designer_call, sandbox, role=ORCHESTRATOR, ticket=TICKET,
                               subagent=DESIGNER, agent_id=DESIGNER_AGENT, bash=designer_bash, seen=seen)
    support.assert_silent(result, f"the test designer subagent's own call, ending after {what}")
    _assert_untouched(project, before, "the test designer subagent's own call")


# name: (GOV_ROLE, agent_type, agent_id) of the engineer who breaches the acceptance tests
SAME_ACTOR = {
    "engineer-main-thread": (ENGINEER, None, None),
    "engineer-subagent": (ORCHESTRATOR, ENGINEER, ENGINEER_AGENT),
}


@pytest.mark.parametrize("leftovers", [1, 3], ids=["one-call-never-ended", "three-calls-never-ended"])
@pytest.mark.parametrize("actor", sorted(SAME_ACTOR), ids=sorted(SAME_ACTOR))
def test_a_call_of_the_same_actor_that_never_ended_does_not_switch_the_restore_off(project, sandbox, actor,
                                                                                   leftovers):
    """KPI success 2, MR-3. A before-snapshot is left behind when the PreToolUse hook ran and the call never ended:

    the permission prompt was declined, or the session was interrupted. One
    actor makes one Bash call at a time, so its own leftover is no overlapping
    call. Its next call is attributed with certainty, and its breach restored.
    """
    role, agent_type, agent_id = SAME_ACTOR[actor]
    for _ in range(leftovers):
        _begin(project, sandbox, "ls -la", role, TICKET, subagent=agent_type, agent_id=agent_id)
    added = f"{ACCEPTANCE}/{WBS}/test_added.py"
    command = f"echo changed >> {ACCEPTANCE_FILE} && echo new > {added} && echo changed >> {SOURCE}"
    result, _ = _whole(project, sandbox, command, role, TICKET, subagent=agent_type, agent_id=agent_id,
                       changed=[ACCEPTANCE_FILE, added, SOURCE])
    what = f"`{command}` by the {actor}, after {leftovers} of its calls that never ended"
    _assert_acceptance_equals_head(project, what)
    support.assert_caught(result, ACCEPTANCE_FILE, added, what=what, action=support.REVERTED)
    assert support.read(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change was reverted"


# --------------------------------------------------------------------------
# The hook's own failure
# --------------------------------------------------------------------------

def _assert_a_failure_finding(result, what, role, ticket):
    """Reported to the agent, and recorded as lines with the ten fields of DEC-122. Nothing was reverted."""
    assert result.outcome == "report", f"{what}: the failure was not reported to the agent: {result.describe()}"
    assert result.new_lines, f"{what}: the failure was not recorded in {support.FINDINGS_REL}"
    findings = []
    for line in result.new_lines:
        try:
            data = json.loads(line)
        except ValueError:
            raise AssertionError(f"{what}: a line of {support.FINDINGS_REL} is not JSON: {line[:300]!r}") from None
        assert isinstance(data, dict), f"{what}: a line of {support.FINDINGS_REL} is not a JSON object: {line!r}"
        missing = [name for name in support.FINDING_FIELDS if name not in data]
        assert not missing, f"{what}: the finding lacks {', '.join(missing)}: {line[:400]!r}"
        assert data["action"] == support.FLAGGED, (
            f"{what}: `action` is {data['action']!r}; the check failed, so nothing was reverted"
        )
        assert isinstance(data["reason"], str) and data["reason"].strip(), f"{what}: `reason` is empty"
        assert data["time"], f"{what}: `time` is empty"
        assert isinstance(data["paths"], list) and all(isinstance(p, str) for p in data["paths"]), (
            f"{what}: `paths` is not a list of path names: {data['paths']!r}"
        )
        assert data["role"] == role and data["ticket"] == ticket, (
            f"{what}: `role` and `ticket` are {data['role']!r} and {data['ticket']!r}, "
            f"not the session's {role!r} and {ticket!r}"
        )
        findings.append(data)
    return findings


# name: what arrives on stdin
UNUSABLE_STDIN = {
    "not-json": "{not json",
    "empty": "",
    "a-json-list": "[1, 2]",
    "cut-off": '{"session_id": "' + support.SESSION_ID + '", "hook_event_name": "PostToolUse", "tool_na',
}


@pytest.mark.parametrize("case", sorted(UNUSABLE_STDIN), ids=sorted(UNUSABLE_STDIN))
def test_stdin_the_check_cannot_read_is_reported_and_recorded(project, sandbox, case):
    """KPI failure 1: a check that fails without a word lets every change of the call survive without a finding.

    DEC-122 extends DEC-110: the hook's failure goes to the same file, as a
    finding with the same ten fields.
    """
    support.run_bash(project, "echo changed >> README.md", sandbox)
    status = support.porcelain_all(project)
    result = support.run_check_with_stdin(project, UNUSABLE_STDIN[case], sandbox, role=ENGINEER, ticket=TICKET)
    what = f"the PostToolUse hook with stdin {UNUSABLE_STDIN[case][:20]!r}"
    _assert_a_failure_finding(result, what, ENGINEER, TICKET)
    text = (project / support.FINDINGS_REL).read_text(encoding="utf-8")
    assert text.endswith("\n") and len(text.splitlines()) == len(result.new_lines), (
        f"{what}: the failure is not recorded as whole lines of {support.FINDINGS_REL}: {text[:400]!r}"
    )
    assert support.porcelain_all(project) == status, f"{what}: the failed check changed the working tree"


def _python_only(sandbox):
    """A ``PATH`` that holds the interpreter and nothing else: ``git`` cannot be found."""
    directory = sandbox.elsewhere / "python-only"
    directory.mkdir(exist_ok=True)
    for name in ("python3", "python"):
        if not os.path.lexists(directory / name):
            os.symlink(sys.executable, directory / name)
    return {"PATH": str(directory)}


def _no_gov_package(sandbox):
    """A ``PYTHONPATH`` that does not hold the ``gov`` package: the hook cannot load the check."""
    directory = sandbox.elsewhere / "no-gov-package"
    directory.mkdir(exist_ok=True)
    probe = subprocess.run([sys.executable, "-c", "import gov.guard"], capture_output=True, check=False,
                           cwd=str(directory), env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(directory)})
    if probe.returncode == 0:
        pytest.skip("this interpreter finds a `gov` package without PYTHONPATH")
    return {"PYTHONPATH": str(directory)}


BROKEN_ENVIRONMENTS = {"git-is-missing": _python_only, "the-gov-package-is-missing": _no_gov_package}


@pytest.mark.parametrize("case", sorted(BROKEN_ENVIRONMENTS), ids=sorted(BROKEN_ENVIRONMENTS))
def test_a_check_that_cannot_run_is_reported_and_recorded_with_the_call_s_own_fields(project, sandbox, case):
    """The call is known, so the finding names it: session, tool, command, role and ticket (DEC-122)."""
    assert shutil.which("git"), "the tests themselves need git"
    environment = BROKEN_ENVIRONMENTS[case](sandbox)
    command = "echo changed >> README.md"
    seen = len(support.finding_lines(project))
    call = _begin(project, sandbox, command, ENGINEER, TICKET)
    bash = support.run_bash(project, call.command, sandbox)
    support.assert_changed(project, "README.md", command=command)
    status = support.porcelain_all(project)
    result = support.run_check(project, call, sandbox, role=ENGINEER, ticket=TICKET, bash=bash, seen=seen,
                               environment=environment)
    what = f"the PostToolUse hook after `{command}` by the engineer, when {case.replace('-', ' ')}"
    _assert_a_failure_finding(result, what, ENGINEER, TICKET)
    support.new_findings(result, what)   # session_id, tool and command are the call's
    assert support.porcelain_all(project) == status, f"{what}: the failed check changed the working tree"
