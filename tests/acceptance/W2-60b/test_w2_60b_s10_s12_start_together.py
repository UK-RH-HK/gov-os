"""W2-60b, KPI success-10 and success-12 -- two writing launches into one worktree that start together (round 1,
finding F1, taken as described behaviour, DEC-136).

success-10 [DEC-847, DEC-963, DEC-983, DEC-982]: "``gov launch`` refuses a second writing session in a worktree that has
one live (read from the session records), naming it; a reviewer or the QA engineer, which write only their reports, are
not counted; ..."

success-12 [DEC-847, DEC-963, DEC-983, DEC-1156 (3)]: "the launcher refuses to start a second writing session in a
worktree where a writing session is live, naming the worktree; read-only sessions are not refused."

The finding, as behaviour: two writing launches into one worktree started within about 0.1 s of each other both start
their CLI; and when a third party holds the machine-wide start lock (``<HOME>/.gov-os/machine/launch.lock``, an
exclusive ``flock``), two writing launches started 1 s apart both start once it is given back. What must hold: of two
writing launches into one worktree, however close together they start and whether or not the start lock is held while
they wait, exactly one starts its CLI; the other is refused (``LAUNCH_REFUSED``, non-zero exit, no CLI start) naming the
started session's id and the worktree, and leaves no session record and no launch record of its own. A read-only
reviewer (``independent-auditor``) launched together with a writer into the same tree still starts.

Each started session is the planted CLI sleeping until it is signalled (no model); a ``gov launch`` runs in a session
of its own (``w2_60b_support.start_launch``) and is ended by SIGTERM; every process is reaped in a ``finally``.
"""

from __future__ import annotations

import fcntl
import os
import signal
import time

import pytest

import w2_60b_support as t

b, s = t.b, t.s
ENG, TD, AUD = t.ENGINEER, t.TEST_DESIGNER, t.AUDITOR
T = b.T
TREE = "W2-zw61"
SLEEP_S = 40             # the planted session sleeps this long unless it is signalled first
JUDGE_WAIT_S = 30        # the longest wait for both launches to be judged (one start, one refusal; or two starts)
LOCK_HOLD_S = 1.0        # case 2: the gap between launch A and launch B while the test holds the start lock


@pytest.fixture()
def tree(box, project):
    return t.add_tree(box, TREE)


def _start_pair(box, tree, first, second, gap):
    """``first`` started, then ``second`` after ``gap`` seconds (none for 0), both ``gov launch`` into ``tree``."""
    procs = [t.start_launch(box, first, T.tk, cwd=tree)]
    if gap:
        time.sleep(gap)
    procs.append(t.start_launch(box, second, T.tk, cwd=tree))
    return procs


def _end_all(procs):
    """SIGTERM to every ``gov launch`` still running, then reap it; SIGKILL to its group if it does not end."""
    for process in procs:
        if process.poll() is None:
            try:
                process.send_signal(signal.SIGTERM)
            except OSError:
                pass
    for process in procs:
        try:
            process.communicate(timeout=t.END_WAIT_S + 20)
        except Exception:  # noqa: BLE001 - reaping whatever is left, the case's own failure is already raised
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                process.communicate(timeout=10)
            except Exception:  # noqa: BLE001
                pass


def _describe(cli, procs):
    lines = [f"CLI starts recorded: {len(t.calls(cli))} (session ids {[c['session_id'] for c in t.calls(cli)]})"]
    for index, process in enumerate(procs):
        lines.append(f"launch {'AB'[index]}: pid {process.pid}, exit code {process.poll()!r}")
    return "\n".join(lines)


def _exactly_one_admitted(box, cli, project, tree, procs):
    """Wait until both launches are judged; then exactly one CLI start, the other ``gov launch`` refused naming the
    started session's id and the worktree, with no session record and no launch record of its own. Returns the
    started session's call."""
    def judged():
        return len(t.calls(cli)) + sum(p.poll() is not None for p in procs) >= 2

    assert t.wait_for(judged, JUDGE_WAIT_S), (
        f"the two launches were not both judged within {JUDGE_WAIT_S} s\n{_describe(cli, procs)}")
    started = t.calls(cli)
    assert len(started) == 1, (
        f"two writing launches into one worktree started {len(started)} CLIs, not exactly one: both were admitted "
        f"(the one-writer check does not hold for launches that start together)\n{_describe(cli, procs)}")
    ended = [p for p in procs if p.poll() is not None]
    assert len(ended) == 1, f"not exactly one launch ended (was refused)\n{_describe(cli, procs)}"
    code, out, err = t.finish(ended[0], timeout=10)
    sid, said = started[0]["session_id"], out + "\n" + err
    where = os.path.realpath(tree)
    assert code != 0, f"the launch that started no CLI exited 0\nstdout:\n{out[-1500:]}\nstderr:\n{err[-1500:]}"
    assert "LAUNCH_REFUSED" in said, f"the second writing launch is not LAUNCH_REFUSED\nstderr:\n{err[-1500:]}"
    assert sid in said, (
        f"the refusal does not name the started session's id {sid}\nstdout:\n{out[-1500:]}\nstderr:\n{err[-1500:]}")
    assert where in said, (
        f"the refusal does not name the worktree {where}\nstdout:\n{out[-1500:]}\nstderr:\n{err[-1500:]}")
    other_sessions = [name for name in t.record_files(project) if name != f"{sid}.json"]
    assert not other_sessions, f"the refused launch left a session record of its own: {other_sessions}"
    other_launches = [name for name in b._listing(box.records) if name != f"{sid}.json"]
    assert not other_launches, f"the refused launch left a launch record of its own: {other_launches}"
    return started[0]


@pytest.mark.parametrize(("gap", "second"), [(0, TD), (0.05, TD), (0.1, TD), (0, ENG)],
                         ids=["no-gap-test-designer", "gap-0.05-test-designer", "gap-0.1-test-designer",
                              "no-gap-second-engineer"])
def test_s10_s12_two_writing_launches_started_together_into_one_tree_admit_exactly_one(
        box, project, tree, cli, gap, second):
    t.set_plan(cli, sleep=SLEEP_S)
    procs = []
    try:
        procs = _start_pair(box, tree, ENG, second, gap)
        _exactly_one_admitted(box, cli, project, tree, procs)
    finally:
        _end_all(procs)


def test_s10_s12_two_writing_launches_waiting_on_a_held_start_lock_admit_exactly_one(box, project, tree, cli):
    t.set_plan(cli, sleep=SLEEP_S)
    lock_path = box.home / ".gov-os" / "machine" / "launch.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
    procs = []
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        procs = _start_pair(box, tree, ENG, TD, LOCK_HOLD_S)
        assert not t.calls(cli), (
            f"a launch started its CLI while the test held the start lock {lock_path}\n{_describe(cli, procs)}")
        os.close(fd)
        fd = None
        _exactly_one_admitted(box, cli, project, tree, procs)
    finally:
        if fd is not None:
            os.close(fd)
        _end_all(procs)


def test_s12_a_writer_and_a_read_only_auditor_launched_together_into_one_tree_both_start(box, project, tree, cli):
    t.set_plan(cli, sleep=SLEEP_S)
    procs = []
    try:
        procs = _start_pair(box, tree, ENG, AUD, 0)
        assert t.wait_for(lambda: len(t.calls(cli)) >= 2 or any(p.poll() is not None for p in procs),
                          JUDGE_WAIT_S), f"neither both started nor one ended within {JUDGE_WAIT_S} s"
        time.sleep(0.3)
        assert len(t.calls(cli)) == 2 and all(p.poll() is None for p in procs), (
            f"a writer and a read-only auditor launched together into one tree did not both start\n"
            f"{_describe(cli, procs)}\n" + "".join(
                f"launch {'AB'[i]} stderr:\n{p.communicate(timeout=10)[1][-1500:]}\n"
                for i, p in enumerate(procs) if p.poll() is not None))
    finally:
        _end_all(procs)
