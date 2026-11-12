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


# --- the fix round (review round 1: F-1 to F-4, F-6) -----------------------------------------------------------------

def age(path, seconds=4000):
    old = time.time() - seconds
    os.utime(path, (old, old))


def two_old_items(project):
    start_and_finish(project, "W2-1")
    start_and_finish(project, "W2-2")
    project.tick()
    found = project.inbox()
    assert len(found) == 2
    for item in found:
        age(item)
    return found


def test_f1_a_return_deleted_from_the_inbox_or_from_read_is_never_written_again(project):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    item.unlink()                       # an honest operator removes a handled item
    project.tick()
    assert project.inbox() == []
    start_and_finish(project, "W2-2")
    project.tick()
    project.read_all()
    for gone in (project.state / "inbox" / "read").iterdir():
        gone.unlink()                   # a tidy-up of the read folder
    project.tick()
    project.tick()
    assert project.inbox() == [] and list((project.state / "inbox" / "read").iterdir()) == []


def test_f1_a_deleted_never_ran_item_is_not_written_again(project):
    project.ticket("W2-1")
    project.state.mkdir(parents=True, exist_ok=True)
    old = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(time.time() - 3600))
    (project.state / "started.txt").write_text(f"W2-1-log {old} W2-1 T-W2-1\n")
    project.tick()
    [item] = project.inbox()
    item.unlink()
    project.tick()
    project.tick()
    assert project.inbox() == []
    project.read_all()


def test_f1_a_deleted_owner_item_is_not_written_again(project):
    project.ticket("W2-1", brief="run: review\nreview it\n")
    probes = project.worktree("W2-1") / "docs" / "probes" / "T-W2-1"
    probes.mkdir(parents=True)
    (probes / "r1.md").write_text("one\n")
    (probes / "r2.md").write_text("two\n")
    project.ready(project.entry("W2-1"))
    project.tick()
    [item] = [p for p in project.inbox() if "status: owner" in p.read_text()]
    item.unlink()
    project.tick()
    project.tick()
    assert project.inbox() == [] and project.started() == []


def test_f1_a_deleted_item_never_raises_its_escalation_again(project):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    age(item)
    project.tick()
    assert len(project.notify_log.read_text().splitlines()) == 1
    item.unlink()
    project.tick()
    project.tick()
    assert project.inbox() == [] and len(project.notify_log.read_text().splitlines()) == 1


def test_f2_a_failing_notifier_leaves_the_escalation_due_and_named_in_every_pass(project, monkeypatch):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    age(item)
    project.write_config(notify_retry_s=100000)
    monkeypatch.setenv("STUB_NOTIFY_EXIT", "3")
    code, _ = project.tick()
    assert code == 0 and project.status()["ok"] is True
    assert len(project.notify_log.read_text().splitlines()) == 1
    assert not (project.state / "escalated.txt").exists() or item.name not in (project.state / "escalated.txt").read_text()
    for _ in range(2):                       # not retried before notify_retry_s, but named in every pass
        problems = [p for p in project.status()["problems"] if item.name in p]
        assert len(problems) == 1 and "3" in problems[0]
        assert item.name in project.status_text().split("problems:")[1]
        assert project.tick()[0] == 0
        assert len(project.notify_log.read_text().splitlines()) == 1
    assert [p for p in project.status()["problems"] if item.name in p]


def test_f2_a_failed_escalation_is_retried_after_notify_retry_s_and_recorded_only_when_sent(project, monkeypatch):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    age(item)
    project.write_config(notify_retry_s=1)
    monkeypatch.setenv("STUB_NOTIFY_EXIT", "3")
    project.tick()
    time.sleep(1.2)
    monkeypatch.setenv("STUB_NOTIFY_EXIT", "0")
    project.tick()
    assert len(project.notify_log.read_text().splitlines()) == 2        # the retry
    assert item.name in (project.state / "escalated.txt").read_text()
    assert not [p for p in project.status()["problems"] if item.name in p]
    project.tick()
    assert len(project.notify_log.read_text().splitlines()) == 2        # sent: never again


def test_f2_notify_retry_s_zero_retries_every_pass(project, monkeypatch):
    start_and_finish(project)
    project.tick()
    age(project.inbox()[0])
    project.write_config(notify_retry_s=0)
    monkeypatch.setenv("STUB_NOTIFY_EXIT", "1")
    project.tick()
    project.tick()
    assert len(project.notify_log.read_text().splitlines()) == 2


def test_f2_a_notifier_that_cannot_be_started_is_not_recorded(project):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    age(item)
    project.write_config(notifier_command=["/nonexistent/notify-program"], notify_retry_s=0)
    assert project.tick()[0] == 0
    assert [p for p in project.status()["problems"] if item.name in p]
    assert not (project.state / "escalated.txt").exists() or item.name not in (project.state / "escalated.txt").read_text()


def test_f2_a_read_item_is_not_retried_and_its_problem_line_goes(project, monkeypatch):
    start_and_finish(project)
    project.tick()
    [item] = project.inbox()
    age(item)
    project.write_config(notify_retry_s=0)
    monkeypatch.setenv("STUB_NOTIFY_EXIT", "3")
    project.tick()
    assert [p for p in project.status()["problems"] if item.name in p]
    project.read_all()
    project.tick()
    assert len(project.notify_log.read_text().splitlines()) == 1
    assert project.status()["problems"] == []


def test_f2_a_notifier_timeout_ends_the_passes_escalations_and_records_none_of_the_rest(project):
    first, second = two_old_items(project)
    project.write_config(notifier_command=[__import__("sys").executable, str(project.base / "hang_logged_stub.py")],
                         command_timeout_s=1, notify_retry_s=0)
    began = time.time()
    code, _ = project.tick()
    assert time.time() - began < 15 and code == 0 and project.status()["ok"] is True
    assert len(project.notify_log.read_text().splitlines()) == 1        # the second was not run
    problems = project.status()["problems"]
    for item in (first, second):         # each item due is named as not sent: the one that hung, and the one not run
        assert len([p for p in problems if item.name in p and "not sent" in p and "timed out" in p]) == 1
    assert not (project.state / "escalated.txt").exists() or (project.state / "escalated.txt").read_text().strip() == ""
    project.write_config(notifier_command=[__import__("sys").executable, str(project.base / "notify_stub.py")],
                         notify_retry_s=0)
    project.tick()
    assert len((project.state / "escalated.txt").read_text().splitlines()) == 2    # both sent on the next pass


def test_f4_a_path_only_untracked_or_only_staged_is_unresolved_an_ignored_one_resolves(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    project.wait_exit("W2-1-log")
    worktree = project.worktree("W2-1")
    (worktree / ".gitignore").write_text("scratch/\n")
    (worktree / "src").mkdir()
    (worktree / "src" / "tracked.py").write_text("x = 1\n")
    git(worktree, "add", ".gitignore", "src/tracked.py")
    git(worktree, "commit", "-q", "-m", "work")
    (worktree / "src" / "untracked.py").write_text("y = 2\n")
    (worktree / "src" / "staged.py").write_text("z = 3\n")
    git(worktree, "add", "src/staged.py")
    (worktree / "scratch").mkdir()
    (worktree / "scratch" / "out.log").write_text("ignored\n")
    (project.state / "logs" / "W2-1-log").write_text(
        "status: DONE\nfiles_changed: src/tracked.py, src/untracked.py, src/staged.py, scratch/out.log\n")
    project.tick()
    [line] = [x for x in items(project)[0].splitlines() if x.startswith("unresolved:")]
    assert "src/untracked.py" in line and "src/staged.py" in line
    assert "src/tracked.py" not in line and "scratch/out.log" not in line


def test_f6_a_hung_git_names_the_commits_and_paths_as_not_checked_never_as_unresolved(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    project.wait_exit("W2-1-log")
    head = git(project.worktree("W2-1"), "rev-parse", "HEAD")[:12]
    (project.state / "logs" / "W2-1-log").write_text(f"status: DONE\ncommits: {head}\nfiles_changed: README\n")
    program = project.bin / "git"
    program.write_text(f"#!{__import__('sys').executable}\nimport time\ntime.sleep(60)\n")
    program.chmod(0o755)
    project.mp.setenv("PATH", f"{project.bin}:{os.environ['PATH']}")
    project.write_config(command_timeout_s=1)
    began = time.time()
    project.tick()
    assert time.time() - began < 20
    text = items(project)[0]
    assert not [x for x in text.splitlines() if x.startswith("unresolved:")]
    [line] = [x for x in text.splitlines() if x.startswith("unchecked:")]
    assert line.startswith("unchecked: could not be checked (") and "timed out" in line
    assert head in line and "README" in line
    assert any("could not be checked" in p for p in project.status()["problems"])
