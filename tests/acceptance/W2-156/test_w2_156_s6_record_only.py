"""S6 and F1: usage stays record-only. The brake only holds a new launch and writes its one inbox item; it stops no running
session, sends no notification outside the project's inbox, and raises no alarm about usage.

The running session is a stand-in process the test starts, whose pid a planted session record of the braked ticket holds
with ``ended_at`` null; the notifier is a stub planted as the dispatcher's ``notifier_command`` (the product's one
notifier), which appends a line to a file each time it runs."""

from __future__ import annotations

import subprocess
import sys

import w2_156_support as t

b = t.b
RECORD_PATHS = (t.SPEND_REL, t.INBOX_REL)    # the brake may write only here, in the project


def _state_letter(pid):
    """The process state letter in ``/proc/<pid>/stat`` (``T`` is stopped); None when the process is gone."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
            return handle.read().rsplit(")", 1)[1].split()[0]
    except OSError:
        return None


def _plant_notifier(box, project):
    calls = box.elsewhere / "notifier-calls.txt"
    stub = box.elsewhere / "notifier.py"
    stub.write_text(f"#!{sys.executable}\nimport sys\nwith open({str(calls)!r}, 'a') as handle:\n"
                    "    handle.write(' '.join(sys.argv[1:]) + '\\n')\n", encoding="utf-8")
    stub.chmod(0o755)
    b.write(project / t.DISPATCH_REL, t.dispatch_yaml([str(stub)]))
    return calls


def _notifier_calls(calls):
    return calls.read_text(encoding="utf-8").splitlines() if calls.is_file() else []


def test_s6_check_leaves_a_running_session_alive_calls_no_notifier_and_writes_only_its_record_and_one_inbox_item(
        box, project):
    calls = _plant_notifier(box, project)
    t.plant_over(project, t.A)                                          # braked by `check`: 10.05 over 5.00
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        record = t.plant_session(project, t.A, None, started=t.PAST_LATER, pid=sleeper.pid, ended=False,
                                 worktree=str(project.parent / "running-tree"))
        record_before = record.read_bytes()
        b.base_environment(box)                                         # plants the gate once, before the snapshots
        tree_before = t.snapshot(project)
        home_before = t.snapshot(box.home, skip=("work/repo",))

        run = t.assert_ok(t.spend(box, "check"))

        # the brake did its work, and only that
        t.assert_one_brake(project, t.A, 10.05, 5.0)
        # F1: the running session is untouched
        assert sleeper.poll() is None, f"the running session's process ended (exit code {sleeper.returncode})"
        assert _state_letter(sleeper.pid) not in (None, "T", "t", "Z"), (
            f"the running session's process was stopped or killed: state {_state_letter(sleeper.pid)!r}")
        assert record.read_bytes() == record_before, "the running session's record was changed"
        # F1: no push, no alarm: the notifier stub never ran
        assert _notifier_calls(calls) == [], f"the notifier ran: {_notifier_calls(calls)}\n{run.describe()}"
        # nothing written outside the brake's own folder and the one inbox item
        added, removed, changed = t.difference(tree_before, t.snapshot(project))
        outside = [p for p in (*added, *removed, *changed) if not p.startswith(RECORD_PATHS)]
        assert not outside, f"`check` wrote outside {RECORD_PATHS}: {outside}\n{run.describe()}"
        assert not removed and not changed, f"`check` removed or changed files: {removed}, {changed}"
        inbox_new = [p for p in added if p.startswith(t.INBOX_REL)]
        assert len(inbox_new) == 1, f"`check` wrote {len(inbox_new)} inbox items, not one: {inbox_new}"
        assert t.difference(home_before, t.snapshot(box.home, skip=("work/repo",))) == ([], [], []), (
            "`check` wrote in the home folder")
    finally:
        sleeper.kill()
        sleeper.wait()


def test_s6_the_brake_holds_the_next_launch_only_and_stops_nothing_else(box, project, cli):
    # F1/F3 together: a braked ticket's running session stays alive while its next launch is refused.
    calls = _plant_notifier(box, project)
    t.plant_over(project, t.TK)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        t.plant_session(project, t.TK, None, started=t.PAST_LATER, pid=sleeper.pid, ended=False,
                        worktree=str(project.parent / "running-tree"))
        t.assert_ok(t.spend(box, "check"))
        refused = b.launch(box, cli, b.ENGINEER, t.TK)
        b.assert_refused(refused, "SPEND_BRAKED")
        assert sleeper.poll() is None and _state_letter(sleeper.pid) not in (None, "T", "t", "Z"), (
            "the running session was stopped by the brake or by the refused launch")
        assert _notifier_calls(calls) == [], f"the notifier ran: {_notifier_calls(calls)}"
    finally:
        sleeper.kill()
        sleeper.wait()
