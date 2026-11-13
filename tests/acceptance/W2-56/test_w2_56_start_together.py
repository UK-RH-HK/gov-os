"""S7: sessions started together in worktrees that share one .git do not fail on a lock.

S7: sandboxed sessions started together in worktrees that share one .git do not fail on a missing .git/*.lock source
path: the launcher starts sessions one at a time per repository (a short start lock), or the CIT-E shows another
way; a test starts at least three launches at once [lens E F17].

What is the same whichever set-up the experiment chooses (DEC-1099 (1)): three ``gov launch`` calls made at the same
moment, from three worktrees of one repository, all start their sessions, the sessions run at the same time (each
waits until all three are running, so a lock held for a session's whole life fails it), each commits in its own
worktree through the shared ``.git``, and each launch ends with its session's exit code. A launch after them starts.
Why a sandbox fails without the lock (bubblewrap binding a lock file git has just removed) needs the real sandbox,
and is left for after the experiment.
"""

from __future__ import annotations

import pytest

import w2_56_support as s

NAMES = ("wt-a", "wt-b", "wt-c")
TICKET_OF_TREE = {"wt-a": s.T, "wt-b": s.T2, "wt-c": s.T3}
BARRIER_S = 25


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    project = s.make_project(box)
    for name in NAMES:
        s.add_worktree(project, name)
    s.install_stand_in_cli(box)
    barrier = box.elsewhere / "barrier"
    plans = {name: [
        {"do": "touch", "path": str(barrier / f"{name}.up")},
        {"do": "wait_for", "paths": [str(barrier / f"{other}.up") for other in NAMES], "timeout": BARRIER_S,
         "fail_code": 7},
        {"do": "write", "path": f"src/{name}.txt", "text": f"{name}\n"},
        {"do": "git", "argv": ["add", "-A"], "label": "add"},
        {"do": "git", "argv": ["commit", "-q", "-m", f"the session in {name}"], "label": "commit"},
        {"do": "exit", "code": 0},
    ] for name in NAMES}
    s.set_plan(box, [{"do": "exit", "code": 0}], **plans)
    return box


def test_s7_three_launches_at_once_in_worktrees_sharing_one_git_all_start_run_together_and_commit(box):
    trees = {name: box.project.parent / name for name in NAMES}
    processes = {name: s.start_launch(box, s.ENGINEER, TICKET_OF_TREE[name].tk, cwd=trees[name]) for name in NAMES}
    ended = {name: s.finish(process, timeout=BARRIER_S + 30) for name, process in processes.items()}
    for name, (code, _, err) in ended.items():
        assert code != 7, f"the session in {name} never saw all three sessions running at once (a lock held for a " \
                          f"whole session?): {err[-800:]}"
        assert code == 0, f"the launch in {name} ended with {code}: {err[-1200:]}"
    started = sorted(call["name"] for call in s.calls(box))
    assert started == sorted(NAMES), f"sessions started in {started}, not once in each of {NAMES}"
    for name in NAMES:
        committed = s.result(box, name, "commit")
        assert committed["code"] == 0, f"the commit in {name} failed: {committed['stderr']}"
        files = s.git(trees[name], "show", "--name-only", "--format=", "HEAD").stdout.split()
        assert f"src/{name}.txt" in files, f"the commit in {name} does not hold its file: {files}"


def test_s7_a_launch_after_three_at_once_still_starts(box):
    trees = {name: box.project.parent / name for name in NAMES}
    processes = [s.start_launch(box, s.ENGINEER, TICKET_OF_TREE[name].tk, cwd=trees[name]) for name in NAMES]
    for process in processes:
        s.finish(process, timeout=BARRIER_S + 30)
    launch = s.run_launch(box, s.TEST_DESIGNER, s.T.tk, cwd=box.project)
    assert launch.returncode == 0 and launch.started, f"a later launch did not start\n{launch.describe()}"
