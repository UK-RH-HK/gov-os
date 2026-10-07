"""The pre-push hook: G3, and the evidence record bound to the head commit (KPI S1 second clause, F2) [CAP-39.a].

Every push is a plain ``git push origin main`` to a bare repository in the test's temporary folder (DEC-465: no
push leaves the machine). A push is refused when the bare repository does not hold the pushed commit afterwards.

Whether the record is there is asked here the way DEC-087 fixes: the CI job is green for that commit. The
record as a git note (DEC-489) is held by ``test_w1_40_evidence_record.py``.
"""

from __future__ import annotations

import pytest

import w1_40_support as support


def test_a_push_runs_the_g3_check(project, machine):
    dev = machine()
    project.commit(dev)
    project.forget_runs()
    done, arrived = project.push(dev)
    assert arrived, f"a push with every check passing was refused:\n{support.said(done)}"
    assert project.ran("G3") >= 1, f"the project's G3 check did not run at push:\n{support.said(done)}"


def test_a_failing_g3_check_stops_the_push(project, machine):
    dev = machine()
    project.commit(dev)
    before = project.remote_head()
    project.fail("G3")
    done, arrived = project.push(dev)
    assert project.ran("G3") >= 1, f"the G3 check did not run at push:\n{support.said(done)}"
    assert not arrived and project.remote_head() == before, (
        f"a failing G3 check did not stop the push:\n{support.said(done)}")
    assert done.returncode != 0


def test_the_push_passes_again_once_the_g3_check_passes(project, machine):
    dev = machine()
    project.commit(dev)
    project.fail("G3")
    _, arrived = project.push(dev)
    assert not arrived
    project.fail("G3", failing=False)
    done, arrived = project.push(dev)
    assert arrived, f"the push stayed refused after the G3 check passed:\n{support.said(done)}"


def test_one_push_through_the_hook_leaves_the_record_ci_asks_for(pushed, ci):
    """Success, end to end: commit, one ``git push``, then the CI job on a fresh checkout of that commit is green."""
    result = ci()
    assert result.green, f"CI is red for a commit pushed through the hook with every check passing:\n{result}"


def test_the_record_follows_the_head_commit_push_after_push(project, machine, pushed, ci):
    """A second commit pushed through the hook has its own record: CI is green for it too."""
    dev = machine()
    project.commit(dev, "more.txt")
    done, arrived = project.push(dev)
    assert arrived, support.said(done)
    assert project.head() != pushed
    result = ci()
    assert result.green, f"CI is red for the second commit pushed through the hook:\n{result}"


def test_the_push_leaves_the_project_clean(project, pushed):
    """The record is not an untracked or modified file left in the working tree (CAP-27 as W1-26 reads it)."""
    status = support.sh(["git", "status", "--porcelain"], project.root, project.setup.env(), check=True).stdout
    assert status == "", f"the push left changes in the working tree:\n{status}"


@pytest.mark.parametrize("missing", ["gov", "lefthook"])
def test_a_push_without_a_tool_the_hook_needs_never_ends_with_ci_green(project, machine, ci, missing):
    """DEC-449, DEC-454: G3 that could not run is not a pass. Either the push is refused or CI is red for it.

    Without ``lefthook`` on PATH the installed hook may let the push through; the commit then has no record, and
    the CI job is what refuses it.
    """
    project.unhooked_commit()
    if missing == "lefthook":
        project.lose_lefthook()
    done, arrived = project.push(machine(**{missing: False}))
    if arrived:
        result = ci()
        assert not result.green, (
            f"the push passed although {missing} could not run, and CI is green for the commit:\n"
            f"{support.said(done)}\n{result}")
