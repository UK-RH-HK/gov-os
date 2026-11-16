"""W2-60b, KPI success-10, success-12 and success-9's reviewer set -- one writer per worktree; ``--tests-worktree``.

success-10 [DEC-847, DEC-963, DEC-983, DEC-982]: "``gov launch`` refuses a second writing session in a worktree that has
one live (read from the session records), naming it; a reviewer or the QA engineer, which write only their reports, are
not counted; ``gov launch --tests-worktree`` makes a ticket's tests worktree on its own branch from the ticket's head."
Verify: a planted live writing session record in a worktree: a second writing launch is refused naming it; a planted
reviewer or QA engineer session is not counted; ``gov launch --tests-worktree`` makes a worktree on its own branch at
the ticket's head.

success-12 [DEC-847, DEC-963, DEC-983, DEC-1156 (3)]: "the launcher refuses to start a second writing session in a
worktree where a writing session is live, naming the worktree; read-only sessions are not refused." Verify: a planted
live writing session record in a worktree, then a launch of another writing role into it: refused, the message names
the worktree; the same launch of a read-only reviewer starts.

Interface: a record in the main checkout's ``.gov-runtime/sessions/`` whose ``worktree`` is the launch's tree, whose
``ended_at`` is null and whose ``pid`` is alive is a live writing session unless its role is in the reviewer set
(``independent-auditor``, ``qa-engineer``); the launch is then refused, ``LAUNCH_REFUSED``, naming that session's id and
the worktree. ``gov launch independent-test-designer <ticket> --tests-worktree``, run in the ticket's worktree, makes
``<tree>-tests`` on the new branch ``<tree's branch>-tests`` at the tree's HEAD, prints its path, exits 0 and starts no
session; an existing path or branch refuses. Planted live records name this test process's own pid. A case that shows
a record is not counted then plants a live writing record and shows the refusal, so it is red until the check exists.
"""

from __future__ import annotations

import os

import pytest

import w2_60b_support as t

b, s = t.b, t.s
ENG, TD, AUD, QA = t.ENGINEER, t.TEST_DESIGNER, t.AUDITOR, t.QA
T = b.T
TREE = "W2-zw60"


@pytest.fixture()
def tree(box, project):
    return t.add_tree(box, TREE)


def _refused_naming(result, sid, tree):
    s.refused(result, sid, os.path.realpath(tree))


def _starts(result):
    b.assert_launched(result)
    return result


def test_s10_a_second_writing_launch_into_a_tree_with_a_live_writing_session_is_refused_naming_it(
        project, tree, launch):
    sid = t.plant_record(project, tree, ENG, pid=os.getpid())
    _refused_naming(launch(ENG, T.tk, cwd=tree), sid, tree)
    assert t.record_files(project) == [f"{sid}.json"], (
        f"a refused launch left a session record: {t.record_files(project)}")


def test_s12_another_writing_role_is_refused_naming_the_worktree_and_a_read_only_reviewer_starts(
        project, tree, launch):
    sid = t.plant_record(project, tree, ENG, pid=os.getpid())
    _refused_naming(launch(TD, T.tk, cwd=tree), sid, tree)
    _starts(launch(AUD, T.tk, cwd=tree))


def test_s10_a_live_reviewer_or_qa_engineer_session_is_not_counted(project, tree, launch):
    t.plant_record(project, tree, AUD, pid=os.getpid())
    t.plant_record(project, tree, QA, pid=os.getpid())
    _starts(launch(ENG, T.tk, cwd=tree))
    sid = t.plant_record(project, tree, TD, pid=os.getpid())
    _refused_naming(launch(ENG, T.tk, cwd=tree), sid, tree)


def test_s10_a_record_whose_pid_is_dead_or_that_has_ended_is_not_live(project, tree, launch):
    t.plant_record(project, tree, ENG, pid=t.dead_pid())
    t.plant_record(project, tree, ENG, pid=os.getpid(), ended=True)
    _starts(launch(ENG, T.tk, cwd=tree))
    sid = t.plant_record(project, tree, ENG, pid=os.getpid())
    _refused_naming(launch(ENG, T.tk, cwd=tree), sid, tree)


def test_s10_a_live_writing_session_in_another_worktree_is_not_counted(project, tree, launch):
    t.plant_record(project, project, ENG, pid=os.getpid())
    _starts(launch(ENG, T.tk, cwd=tree))
    sid = t.plant_record(project, tree, ENG, pid=os.getpid())
    _refused_naming(launch(ENG, T.tk, cwd=tree), sid, tree)


def _tests_worktree(launch, tree):
    return launch(TD, T.tk, options=("--tests-worktree",), cwd=tree)


def test_s10_tests_worktree_makes_the_tests_worktree_on_its_own_branch_at_the_ticket_s_head(project, tree, launch):
    b.write(tree / "src/app/ticket_work.py", "WORK = 1\n")
    s.commit_all(tree, "the ticket's own commit, so that its head is not the main checkout's")
    made = tree.parent / f"{TREE}-tests"
    result = _tests_worktree(launch, tree)
    assert result.run.returncode == 0, f"--tests-worktree did not exit 0\n{result.describe()}"
    assert made.is_dir(), f"no tests worktree at {made}\n{result.describe()}"
    assert t.branch(made) == f"w2/{TREE}-tests", f"the tests worktree is on {t.branch(made)!r}, not w2/{TREE}-tests"
    assert t.head(made) == t.head(tree) != t.head(project), (
        f"the tests worktree's HEAD {t.head(made)} is not the ticket's HEAD {t.head(tree)}")
    assert os.path.realpath(made) in result.run.stdout, f"the tests worktree's path is not printed\n{result.describe()}"
    assert not result.calls and not result.new_records and not t.record_files(project), (
        f"--tests-worktree started a session or left a record\n{result.describe()}")
    again = _tests_worktree(launch, tree)
    assert again.run.returncode != 0 and not again.calls, f"a second --tests-worktree did not refuse\n{again.describe()}"
    assert t.head(made) == t.head(tree), "the refused second call changed the tests worktree"


def test_s10_tests_worktree_refuses_while_its_branch_exists(project, tree, launch):
    made = tree.parent / f"{TREE}-tests"
    b.git(project, "branch", f"w2/{TREE}-tests")
    refused = _tests_worktree(launch, tree)
    assert refused.run.returncode != 0 and not made.exists() and not refused.calls, (
        f"--tests-worktree did not refuse an existing branch w2/{TREE}-tests\n{refused.describe()}")
    b.git(project, "branch", "-D", f"w2/{TREE}-tests")
    result = _tests_worktree(launch, tree)
    assert result.run.returncode == 0 and made.is_dir(), (
        f"--tests-worktree did not make the tests worktree once the branch was gone\n{result.describe()}")
    assert t.head(made) == t.head(tree)
