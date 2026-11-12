"""One pass: the start, its readiness checks and every refusal named in the status (S1, S2, S6, S10, F1)."""
from __future__ import annotations

import fcntl
import os
import subprocess
import sys

from conftest import GIB, REPO, git


def reasons(project) -> dict:
    return {s["W2"]: s["reason"] for s in project.status()["skipped"]}


def test_a_ready_entry_starts_once_and_its_exit_is_written(project):
    project.ticket("W2-1")
    project.ready("# batch 1", project.entry("W2-1"))
    code, _ = project.tick()
    assert code == 0
    assert project.started() == ["W2-1-log"]
    assert project.wait_exit("W2-1-log") == "0"
    line = project.launches()[0]
    assert line.startswith("T-W2-1 W2-1 W2-1-log | go | ")  # the placeholders filled, the brief on stdin
    assert line.endswith(str(project.worktree("W2-1")))      # run in the ticket's worktree
    assert project.status()["started"]["log"] == "W2-1-log"
    assert (project.state / "logs" / "W2-1-log").read_text().strip() == "status: DONE"


def test_one_start_per_pass_in_the_lists_order(project):
    for name in ("W2-1", "W2-2", "W2-3"):
        project.ticket(name)
    project.ready(project.entry("W2-2"), project.entry("W2-1"), project.entry("W2-3"))
    project.tick()
    assert project.started() == ["W2-2-log"]          # the list's order, never the dispatcher's
    assert reasons(project)["W2-1"].startswith("one start per pass")
    project.wait_exit("W2-2-log")
    project.tick()
    assert project.started() == ["W2-2-log", "W2-1-log"]


def test_an_entry_not_on_the_list_is_never_started(project):
    project.ticket("W2-1")
    project.ticket("W2-2")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_no_list_means_nothing_to_do(project):
    code, _ = project.tick()
    assert code == 0 and project.started() == [] and project.status()["ok"] is True


def test_a_started_log_name_never_starts_again(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    project.wait_exit("W2-1-log")
    project.read_all()
    project.tick()
    assert project.started() == ["W2-1-log"] and len(project.launches()) == 1
    assert "already started" in reasons(project)["W2-1"]


def test_stagger_holds_the_second_start(project):
    project.write_config(stagger_s=3600)
    project.ticket("W2-1")
    project.ticket("W2-2")
    project.ready(project.entry("W2-1"), project.entry("W2-2"))
    project.tick()
    project.wait_exit("W2-1-log")
    project.read_all()
    code, _ = project.tick()
    assert project.started() == ["W2-1-log"] and "stagger" in reasons(project)["W2-2"]


def test_uncommitted_claim_is_skipped_and_named(project):
    project.ticket("W2-1", committed=False)
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == [] and "claim" in reasons(project)["W2-1"]


def test_claim_not_in_progress_on_the_branch_is_skipped(project):
    project.ticket("W2-1", status="open")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == [] and "claim" in reasons(project)["W2-1"]


def test_claim_missing_from_the_worktree_head_is_skipped(project):
    project.ticket("W2-1")
    git(project.worktree("W2-1"), "reset", "-q", "--hard", "HEAD~1")  # the worktree behind the claim
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == [] and "claim" in reasons(project)["W2-1"]


def test_unclean_worktree_is_skipped(project):
    project.ticket("W2-1")
    (project.worktree("W2-1") / "README").write_text("changed\n")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == [] and "not clean" in reasons(project)["W2-1"]


def test_an_untracked_file_does_not_make_the_worktree_unclean(project):
    project.ticket("W2-1")
    (project.worktree("W2-1") / "new.txt").write_text("x\n")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_incomplete_briefs_are_skipped(project):
    project.ticket("W2-1", brief="")
    project.ticket("W2-2", brief="do @@ this\n")
    project.ticket("W2-3", brief="the {TICKET_ID} slot\n")
    project.ticket("W2-4", brief=None)
    project.ticket("W2-5", brief="{braces} and {lower} are fine\n")
    project.ready(*(project.entry(f"W2-{n}") for n in (1, 2, 3, 4)))
    project.tick()
    skipped = reasons(project)
    assert project.started() == []
    assert all("brief" in skipped[f"W2-{n}"] for n in (1, 2, 3, 4))
    project.ready(project.entry("W2-5"))
    project.tick()
    assert project.started() == ["W2-5-log"]


def test_a_running_ticket_is_skipped(project):
    project.ticket("W2-1")
    project.lead_process(4242, "T-W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == [] and "running" in reasons(project)["W2-1"]
    assert project.status()["running"] == [{"ticket": "T-W2-1", "pid": 4242}]


def test_a_process_with_another_role_or_no_marker_is_not_a_lead(project):
    project.ticket("W2-1")
    project.process(10, ["claude", "--settings", '{"env": {"GOV_ROLE": "engineer", "GOV_TICKET": "T-W2-1"}}'])
    project.process(11, ["vim", "T-W2-1"])
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == ["W2-1-log"] and project.status()["running"] == []


def test_an_unread_return_skips_the_entry_until_it_is_read(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.state.joinpath("inbox").mkdir(parents=True)
    (project.state / "inbox" / "a.txt").write_text("log: old-log\nW2: W2-1\nstatus: DONE\n")
    project.tick()
    assert project.started() == [] and "unread return" in reasons(project)["W2-1"]
    project.read_all()
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_malformed_lines_are_named_and_the_others_still_read(project):
    project.ticket("W2-1")
    project.ready("only two", "W2-9 T-9 b.md log extra tokens", "W2-8 T-8 b.md ../escape", project.entry("W2-1"))
    code, _ = project.tick()
    assert code == 0 and project.started() == ["W2-1-log"]
    bad = [s for s in project.status()["skipped"] if s["reason"].startswith("malformed")]
    assert len(bad) == 3


def test_a_shut_gate_refuses_every_entry_with_exit_3(project):
    project.ticket("W2-1")
    project.ticket("W2-2")
    project.memory(1 * GIB)  # under the floor plus a working size
    project.ready(project.entry("W2-1"), project.entry("W2-2"))
    code, _ = project.tick()
    assert code == 3 and project.started() == []
    assert all("gate shut" in r and "memory" in r for r in reasons(project).values())
    assert project.status()["gate"]["open"] is False


def test_a_full_disk_refuses_with_exit_3(project):
    project.ticket("W2-1")
    project.disk(1 * GIB, 50_000_000)
    project.ready(project.entry("W2-1"))
    code, _ = project.tick()
    assert code == 3 and project.started() == [] and "disk" in reasons(project)["W2-1"]


def test_max_leads_counts_processes_and_recent_starts_without_one(project):
    project.write_config(max_leads=2)
    for name in ("W2-1", "W2-2", "W2-3"):
        project.ticket(name)
    project.lead_process(100, "T-other-a")
    project.lead_process(101, "T-other-b")
    project.ready(project.entry("W2-1"))
    code, _ = project.tick()
    assert project.started() == [] and "max_leads" in reasons(project)["W2-1"]
    project.end_process(101)
    project.tick()
    assert project.started() == ["W2-1-log"]
    project.wait_exit("W2-1-log")
    project.read_all()
    project.lead_process(102, "T-other-c")  # two running again; the finished start does not count
    project.ready(project.entry("W2-2"))
    project.tick()
    assert project.started() == ["W2-1-log"]


def test_a_third_review_round_is_refused_once_as_an_owner_item(project):
    project.ticket("W2-1", brief="run: review\nreview it\n")
    probes = project.worktree("W2-1") / "docs" / "probes" / "T-W2-1"
    probes.mkdir(parents=True)
    (probes / "r1.md").write_text("one\n")
    project.ready(project.entry("W2-1"))
    project.tick()
    assert project.started() == ["W2-1-log"]  # one probe record: started
    project.wait_exit("W2-1-log")
    project.tick()      # the finished session's return is written ...
    project.read_all()  # ... and read
    (probes / "r2.md").write_text("two\n")
    project.ready(project.entry("W2-1").replace("W2-1-log", "W2-1-log2"))
    project.tick()
    assert project.started() == ["W2-1-log"] and "review" in reasons(project)["W2-1"]
    owner = [p for p in project.inbox() if "status: owner" in p.read_text()]
    assert len(owner) == 1 and "W2: W2-1" in owner[0].read_text()
    project.read_all()
    project.tick()
    assert project.inbox() == [] or all("status: owner" not in p.read_text() for p in project.inbox())  # once


def test_a_hung_command_is_a_named_failed_check_not_a_hung_pass(project):
    project.ticket("W2-1")
    project.ticket("W2-2")
    project.ready(project.entry("W2-1"), project.entry("W2-2"))
    program = project.bin / "git"
    program.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(60)\n")
    program.chmod(0o755)
    project.mp.setenv("PATH", f"{project.bin}:{os.environ['PATH']}")
    project.write_config(command_timeout_s=1)
    import time
    began = time.time()
    code, _ = project.tick()
    assert time.time() - began < 15
    assert project.started() == []
    assert all("timed out" in r and "git" in r for r in reasons(project).values())


def test_a_crash_after_a_launch_never_starts_that_log_again(project, monkeypatch):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    from gov.dispatch import status as status_module

    def boom(*args, **kwargs):
        raise RuntimeError("crash after the launch")
    original = status_module.write
    monkeypatch.setattr(status_module, "write", boom)
    try:
        project.tick()
    except RuntimeError:
        pass
    assert project.started() == ["W2-1-log"]
    monkeypatch.setattr(status_module, "write", original)
    project.wait_exit("W2-1-log")
    project.read_all()
    project.tick()
    assert project.started() == ["W2-1-log"] and len(project.launches()) == 1


def test_the_log_name_is_recorded_before_the_launch_is_spawned(project, monkeypatch):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    from gov.dispatch import run as run_module

    def spawn(*args, **kwargs):
        assert project.started() == ["W2-1-log"]  # already in started.txt when the launch is spawned
        raise OSError("cannot spawn")
    monkeypatch.setattr(run_module, "spawn", spawn)
    project.tick()
    assert project.started() == ["W2-1-log"] and project.launches() == []


def test_an_off_file_stops_the_pass(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.state.joinpath("OFF").write_text("")
    code, _ = project.tick()
    assert code == 0 and project.started() == [] and project.launches() == []
    assert not (project.state / "started.txt").exists()
    assert "OFF" in project.status_text()


def test_a_held_lock_exits_4_and_writes_nothing(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    project.tick()
    project.wait_exit("W2-1-log")
    before = {p.name: p.read_bytes() for p in project.state.iterdir() if p.is_file()}
    handle = open(project.state / "tick.lock", "a")
    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        code, _ = project.tick()
    finally:
        handle.close()
    after = {p.name: p.read_bytes() for p in project.state.iterdir() if p.is_file()}
    assert code == 4 and before == after


def test_two_ticks_started_together_run_one_pass(project):
    project.ticket("W2-1")
    project.ready(project.entry("W2-1"))
    env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
    command = [sys.executable, "-m", "gov.cli.main", "dispatch", "tick", "--root", str(project.root)]
    first = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    second = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    codes = sorted([first.wait(), second.wait()])
    assert codes in ([0, 0], [0, 4])  # when they do not overlap the second finds nothing to start
    project.wait_exit("W2-1-log")
    assert project.started() == ["W2-1-log"] and len(project.launches()) == 1


def test_the_command_runs_through_the_cli(project):
    env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "dispatch", "status", "--root", str(project.root)],
                          env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "dispatch", "tick", "--root", str(project.root),
                           "--json"], env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    import json
    assert json.loads(done.stdout)["command"] == "dispatch"
