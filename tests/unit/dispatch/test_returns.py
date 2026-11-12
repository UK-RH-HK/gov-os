"""Returns: every finished session one inbox item, a start that never ran, an escalation, resolved commits (S4, S8, S9)."""
from __future__ import annotations

import os
import time

from conftest import git


def start_and_finish(project, w2="W2-1", log_text=None, exit_code=0):
    project.ticket(w2)
    project.ready(project.entry(w2))
    project.tick()
    project.wait_exit(f"{w2}-log")
    if log_text is not None:
        (project.state / "logs" / f"{w2}-log").write_text(log_text)
    if exit_code:
        (project.state / "logs" / f"{w2}-log.exit").write_text(f"{exit_code}\n")


def items(project):
    return [p.read_text() for p in project.inbox()]


def test_a_finished_session_is_one_item_once(project):
    start_and_finish(project)
    project.tick()
    found = items(project)
    assert len(found) == 1
    assert "log: W2-1-log" in found[0] and "W2: W2-1" in found[0] and "status: DONE" in found[0]
    project.tick()
    project.tick()
    assert len(project.inbox()) == 1
    project.read_all()
    project.tick()
    assert project.inbox() == []   # a read item is not written again


def test_the_status_line_comes_from_the_return_else_the_exit_code(project):
    start_and_finish(project, log_text="chatter\nstatus: PACKAGES\nmore\n")
    project.tick()
    assert "status: PACKAGES" in items(project)[0]
    project.read_all()
    start_and_finish(project, "W2-2", log_text="no status in this one\n", exit_code=7)
    project.tick()
    assert "status: exit 7" in items(project)[0]


def test_commits_and_paths_are_resolved_against_git(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()                       # started with the claim as the worktree's head
    project.wait_exit("W2-1-log")
    worktree = project.worktree("W2-1")
    (worktree / "src").mkdir()
    (worktree / "src" / "real.py").write_text("x = 1\n")
    git(worktree, "add", "src/real.py")
    git(worktree, "commit", "-q", "-m", "work")
    commit = git(worktree, "rev-parse", "HEAD")[:12]
    (project.state / "logs" / "W2-1-log").write_text(
        f"status: DONE\ncommits: {commit}, deadbeef0123\nfiles_changed: src/real.py, src/ghost.py\n")
    project.tick()
    text = items(project)[0]
    unresolved = [line for line in text.splitlines() if line.startswith("unresolved:")]
    assert len(unresolved) == 1
    assert "deadbeef0123" in unresolved[0] and "src/ghost.py" in unresolved[0]
    assert commit not in unresolved[0] and "src/real.py" not in unresolved[0]


def test_a_return_naming_only_existing_things_has_no_unresolved_line(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    project.wait_exit("W2-1-log")
    head = git(project.worktree("W2-1"), "rev-parse", "HEAD")[:12]
    (project.state / "logs" / "W2-1-log").write_text(
        f"status: DONE\ncommits: {head} claim\nfiles_changed: README, .tickets/T-W2-1.md\n")
    project.tick()
    assert "unresolved" not in items(project)[0]


def test_a_start_that_never_ran_is_one_item_once(project):
    project.ticket("W2-1")
    project.state.mkdir(parents=True, exist_ok=True)
    old = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(time.time() - 3600))
    (project.state / "started.txt").write_text(f"W2-1-log {old} W2-1 T-W2-1\n")
    project.tick()
    found = items(project)
    assert len(found) == 1 and "never-ran" in found[0] and "log: W2-1-log" in found[0] and "W2: W2-1" in found[0]
    assert "W2-1-log" in (project.state / "never-ran.txt").read_text()
    project.tick()
    assert len(project.inbox()) == 1


def test_a_recent_start_without_a_process_is_not_yet_a_start_that_never_ran(project):
    project.ticket("W2-1")
    project.state.mkdir(parents=True, exist_ok=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    (project.state / "started.txt").write_text(f"W2-1-log {now} W2-1 T-W2-1\n")
    project.tick()
    assert project.inbox() == []
    project.lead_process(500, "T-W2-1")   # and one with a process never is
    old = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(time.time() - 3600))
    (project.state / "started.txt").write_text(f"W2-1-log {old} W2-1 T-W2-1\n")
    project.tick()
    assert project.inbox() == []


def test_an_item_unread_past_the_time_raises_one_escalation(project):
    start_and_finish(project)
    project.tick()
    item = project.inbox()[0]
    assert project.notify_log.exists() is False
    old = time.time() - 4000
    os.utime(item, (old, old))
    project.tick()
    project.tick()
    pushed = project.notify_log.read_text().splitlines()
    assert pushed == [str(item)]        # the item's path is the last argument, and once
    assert item.name in (project.state / "escalated.txt").read_text()


def test_a_read_item_is_never_escalated(project):
    start_and_finish(project)
    project.tick()
    project.read_all()
    for item in (project.state / "inbox" / "read").iterdir():
        old = time.time() - 9000
        os.utime(item, (old, old))
    project.tick()
    assert project.notify_log.exists() is False


def test_a_hung_notifier_is_limited_by_the_timeout(project):
    start_and_finish(project)
    project.tick()
    old = time.time() - 4000
    os.utime(project.inbox()[0], (old, old))
    project.write_config(notifier_command=[__import__("sys").executable, str(project.base / "hang_stub.py")],
                         command_timeout_s=1)
    began = time.time()
    project.tick()
    assert time.time() - began < 15
    assert any("timed out" in p for p in project.status()["problems"])


def test_a_finished_session_is_counted_from_its_exit_file_not_the_process_list(project):
    start_and_finish(project)
    project.lead_process(900, "T-W2-1")  # a stray marker process does not hide the finished return
    project.tick()
    assert len(project.inbox()) == 1
