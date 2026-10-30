"""W2-72, review 1, F4 — git's own clean merge across a rename is no change (DEC-918 item 1, DEC-912).

DEC-918 item 1: a merge-back file under ``tests/acceptance/`` equal to git's own merge of its parents (``git
merge-tree --write-tree``) is neither reverted, refused nor counted as a change, by the live hook or by the
close's gate. DEC-912 (W1-01's rule): a merge commit passes when every file it changes under ``tests/acceptance/``
equals git's own merge of its parents.

**The history.** A test designer's twenty-line acceptance test on ``main``. Since the fork the merged side renamed
it (``git mv``, a test designer's commit) and got an engineer's ``pyproject.toml``; ``main`` changed its line 2 (a
test designer's commit). Git's own merge is clean: ``main``'s edit at the new name, the old path gone, a content
neither parent holds at the new name. The merge commit holds it exactly (``assert_moved_shape``, from git's own
answers).

Expected: the orchestrator's merge in its own call (DEC-266) is silent and moves nothing; ``judge_commits`` on the
merge commit alone returns no finding; and the same history merged over two calls (``git merge --no-ff
--no-commit``, then ``git commit``, the form of F1 (b)) keeps git's own merge as
``test_w2_72_merge_over_two_calls.py`` expects it.

Red reason now: the new path is flagged ("a merge commit's own change to a ticket file or an acceptance test")
and ``judge_commits`` returns that finding; over two calls the first call's check restores the tests from
``HEAD``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_72_support as support  # noqa: E402
from w2_72_support import call, guard_hook, hook, judge, project, sandbox  # noqa: E402,F401  fixtures

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


def _assert_across_a_rename(project, shape, before, merge_id):
    """Guard: git's own merge, held by the merge commit, has the old path gone and at the new name a content
    neither parent holds."""
    support.assert_moved_shape(project, shape, before, merge_id)
    side = support.full_id(project, support.BRANCH)
    held = support.content_at(project, merge_id, support.RENAMED_TEST)
    assert support.content_at(project, merge_id, support.MERGED_TEST) is None and held is not None and held not in (
        support.content_at(project, before, support.RENAMED_TEST), support.content_at(project, side,
                                                                                      support.RENAMED_TEST)), (
        f"the fixture is wrong: {shape.what}: the merge commit holds {held} at {support.RENAMED_TEST}"
    )


def test_the_live_check_is_silent_on_git_s_own_merge_across_a_rename(project, sandbox, call):
    shape = support.clean_merge_across_a_rename(project, sandbox)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    merge_id = support.full_id(project, "HEAD")
    _assert_across_a_rename(project, shape, before, merge_id)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_judge_commits_returns_no_finding_for_git_s_own_merge_across_a_rename(project, sandbox, judge):
    shape = support.clean_merge_across_a_rename(project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    _assert_across_a_rename(project, shape, before, merge_id)
    findings = judge(project, [merge_id])
    assert findings == [], (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not no finding (DEC-918 item 1, DEC-912)"
    )


def test_git_s_own_merge_across_a_rename_over_two_calls_is_kept(project, sandbox, judge):
    """F1 (b)'s form for the same history: neither call's check restores, flags or reports; the merge commit
    holds git's own merge (the new name with ``main``'s edit, the old path gone); ``judge_commits`` finds
    nothing."""
    shape = support.two_calls_across_a_rename(project, sandbox)
    problems, told = support.merge_back_over_two_calls(project, sandbox, judge, shape)
    assert not problems, (
        f"{shape.what}, in the orchestrator's own calls on {TICKET} (DEC-918 item 1): " + "; ".join(problems)
        + f". {told}"
    )
