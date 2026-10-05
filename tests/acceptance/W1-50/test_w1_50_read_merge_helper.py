"""W1-50 — the one helper that reads a merge: ``gov.guard.containment_merge.read_merge``.

Added after implementation; reason: owner decision, DEC-398.

DEC-398: the approval rule (W1-11) "shares one helper with W1-50's three-way
rule (DEC-394), so the approval check and containment read merges the same
way"; "the shared helper is the one place that reads a merge, so it fails
closed for both callers"; "W1-50 builds the helper; W1-11 uses it after W1-50
is merged."

Its public name, fixed for this batch::

    from gov.guard.containment_merge import read_merge
    reading = read_merge(root, commit)   # root: the repository's path (str); commit: a merge commit's id
    reading.own       # sorted list of repository-relative paths the merge commit changed itself
    reading.brought   # sorted list of paths another parent brought

``own`` and ``brought`` are disjoint (both ends of a rename appear as two
paths; a deleted path is a path). The helper takes no caller, no role and no
ticket.

Revised after implementation; reason: delegated decision, DEC-403 (DP-20). The
helper reads every parent the way it reads the first, so ``own`` and
``brought`` together are no longer exactly the paths the merge commit changes
against its first parent: ``own`` also holds a path where the merge commit
differs from another parent and no parent brought its content. The cases of
DEC-403 are in ``test_w1_50_read_merge_every_parent.py``.

These are the only cases of the suite that import from ``src``. The helper is
imported through the fixture ``read_merge``, so its absence fails these cases
and not the collection of the others. Each history is one of
``test_w1_50_merge_read_by_the_merge_base.py`` (or, for the conflict resolved
by hand, of ``test_w1_50_merge_commit_own_changes.py``), built with no hook
around any command; the helper's answer is the one the check gives there.
What the helper does for a commit that is no merge is not tested.
"""

from __future__ import annotations

import importlib
import os

import pytest

import w1_50_support as support

check_support = support.check_support

AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

MODULE = "gov.guard.containment_merge"
SOURCES = check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL

RENAMED_FROM = support.NOTES
RENAMED_TO = "docs/renamed.md"


@pytest.fixture()
def read_merge(monkeypatch):
    """``read_merge(root, commit)``: the helper, imported from this repository's ``src`` when it is first
    called, in a process that says nothing of a caller. The test has built its history by then, so a missing
    helper fails the test itself, after the fixture's guards."""
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.syspath_prepend(str(SOURCES))

    def _read_merge(root, commit):
        try:
            module = importlib.import_module(MODULE)
        except ImportError as exc:
            pytest.fail(f"the helper that reads a merge (DEC-398) cannot be imported: `import {MODULE}` fails: "
                        f"{exc}", pytrace=False)
        helper = getattr(module, "read_merge", None)
        if not callable(helper):
            pytest.fail(f"{MODULE} has no function `read_merge` (DEC-398)", pytrace=False)
        assert str(module.__file__).startswith(str(SOURCES)), (
            f"`{MODULE}` was imported from {module.__file__}, not from this repository's {SOURCES}"
        )
        return helper(root, commit)

    return _read_merge


def _renaming_merge(project, sandbox):
    """An ordinary merge of a branch on which an engineer's commit renamed a file."""
    check_support.git(project, "checkout", "-q", "-b", support.TICKET_BRANCH)
    support.run(project, sandbox,
                f"git mv {RENAMED_FROM} {RENAMED_TO} && git commit -q -m 'a rename'"
                f" --trailer 'Task: {support.DOCS_TICKET}' --trailer 'Role: {support.ENGINEER}'")
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, support.commit(support.BOOTSTRAP, support.ORCHESTRATOR_ON_MAIN,
                                                 subject="main moves on"))
    return support.MergeShape(support.merge(), own=(), brought=(RENAMED_FROM, RENAMED_TO),
                              what=f"an ordinary --no-ff merge of a branch that renamed {RENAMED_FROM} to "
                                   f"{RENAMED_TO}")


# name: the history. Each builder returns the command that makes the merge commit, with the paths that are the
# merge commit's own and the paths another parent brought.
HISTORIES = {
    "an-ordinary-integration-merge":
        lambda project, sandbox: support.ordinary_integration_merge(project, sandbox),
    "a-merge-that-undoes-commits-through-a-new-empty-commit":
        lambda project, sandbox: support.merge_through_a_new_empty_commit(project, sandbox, AS_ORCHESTRATOR),
    "a-merge-that-sets-a-test-back-to-the-merged-branch-s-unchanged-content":
        lambda project, sandbox: support.merge_setting_a_test_back_by_hand(project, sandbox, AS_ORCHESTRATOR),
    "a-conflict-resolved-by-hand-to-content-neither-parent-holds":
        lambda project, sandbox: support.merge_resolved_by_hand(project, sandbox),
    "an-octopus-merge":
        lambda project, sandbox: support.octopus_merge(project, sandbox),
    "a-criss-cross-merge":
        lambda project, sandbox: support.criss_cross_merge(project, sandbox, (support.NEW_TEST, AS_DESIGNER),
                                                           AS_ORCHESTRATOR),
    "a-merge-of-an-unrelated-history":
        lambda project, sandbox: support.unrelated_merge(project, sandbox, (support.NEW_TEST, AS_DESIGNER),
                                                         AS_ORCHESTRATOR),
    "a-merge-of-a-branch-that-renamed-a-file": _renaming_merge,
}


@pytest.mark.parametrize("case", sorted(HISTORIES), ids=sorted(HISTORIES))
def test_read_merge_says_which_paths_are_the_merge_commit_s_own_and_which_another_parent_brought(
        project, sandbox, read_merge, case):
    """DEC-398, DEC-394. ``own`` and ``brought`` are the sorted lists the history's builder names; together
    they are the paths the merge commit changes against its first parent. Reading changes nothing."""
    shape = HISTORIES[case](project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    support.run(project, sandbox, shape.command)
    support.assert_shape(project, shape, before)
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    left = check_support.state(project, support.WATCHED)
    findings = check_support.finding_lines(project)

    reading = read_merge(str(project), merge_commit)

    what = f"read_merge on {shape.what}"
    # Revised after implementation; reason: delegated decision, DEC-403 (DP-20). `own` is read against every
    # parent. Of these histories only the merge of an unrelated history gives another `own`: with no merge base
    # every path that differs from any parent is the merge commit's own, and every path main holds differs from
    # the other parent. `brought` holds at least the paths another parent brought against the first parent;
    # what else it holds DEC-403 does not say (README, package DP-22).
    own = sorted(shape.own)
    if case == "a-merge-of-an-unrelated-history":
        own = sorted(check_support.git(project, "ls-tree", "-r", "--name-only", merge_commit).split())
    differs = set()
    for parent in support.parents_of(project, merge_commit):
        differs.update(check_support.git(project, "diff", "--no-renames", "--name-only", parent,
                                         merge_commit).split())
    assert reading.own == own, (
        f"{what}: `own` is {reading.own!r}, not {own!r}"
    )
    assert reading.brought == sorted(reading.brought) and set(shape.brought) <= set(reading.brought), (
        f"{what}: `brought` is {reading.brought!r}; it is not sorted, or lacks one of {sorted(shape.brought)!r}"
    )
    assert set(reading.brought) <= differs - set(own), (
        f"{what}: `brought` is {reading.brought!r}; it holds a path of `own`, or one that differs from no parent"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)
    assert check_support.finding_lines(project) == findings, f"{what}: reading a merge added a finding"
