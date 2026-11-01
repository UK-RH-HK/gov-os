"""The dispatcher's tests: planted repositories, fake processes, gates, launcher and land command; nothing real starts.
Run: python3 -m pytest -q dispatch/test_dispatcher.py (from the orchestrator scratch folder)."""
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent / "dispatcher.py"
NOW = 1_800_000_000.0
LEAD = '/home/u/.local/bin/claude -p --model x --settings {{"env":{{"GOV_ROLE":"orchestrator","GOV_TICKET":"{}"}}}}'


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def ticket(tid, status):
    return f"---\nid: {tid}\nstatus: {status}\nwbs_id: W2-X\n---\n# {tid}\n"


@pytest.fixture
def w(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    for tid, st in (("T-A", "in_progress"), ("T-B", "in_progress"), ("T-O", "open")):
        (repo / ".tickets" / f"{tid}.md").write_text(ticket(tid, st))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "tickets")
    wt = tmp_path / "wt"
    wt.mkdir()
    for name in ("W2-A", "W2-B", "W2-O"):
        git(repo, "worktree", "add", "-q", str(wt / name), "-b", f"w2/{name}", "w2/integrate")
    orch = tmp_path / "orch"
    for sub in ("log", "briefs", "dispatch", "tools", "merge-queue"):
        (orch / sub).mkdir(parents=True)
    for b in ("A.md", "B.md", "O.md"):
        (orch / "briefs" / b).write_text("a brief\n")
    calls = tmp_path / "calls.txt"
    launcher = tmp_path / "launch.py"
    launcher.write_text(f"import sys\nopen({str(calls)!r}, 'a').write('launch ' + ' '.join(sys.argv[1:]) + '\\n')\n")
    lander = tmp_path / "land.py"
    lander.write_text(f"import sys\nopen({str(calls)!r}, 'a').write('land ' + ' '.join(sys.argv[1:]) + '\\n')\n"
                      "for a in sys.argv[1:]:\n    print('CLOSED ' + a.split('=')[0] + ': x')\n")
    procs = tmp_path / "procs.json"
    procs.write_text("[]")
    held = tmp_path / "held.json"
    held.write_text("[]")
    (tmp_path / "loadavg").write_text("3.0 4.0 5.0 1/100 1\n")
    (tmp_path / "meminfo").write_text("MemAvailable:   16384000 kB\n")
    env = dict(os.environ, DISPATCH_ORCH=str(orch), DISPATCH_DIR=str(orch / "dispatch"), DISPATCH_REPO=str(repo),
               DISPATCH_WORKTREES=str(wt), DISPATCH_FAKE_PROCS=str(procs), DISPATCH_FAKE_HELD=str(held),
               DISPATCH_GATE_CMD="echo OPEN", DISPATCH_DISK_CMD="true",
               DISPATCH_LAUNCH_CMD=f"{sys.executable} {launcher}", DISPATCH_LAND_CMD=f"{sys.executable} {lander}",
               DISPATCH_LOADAVG=str(tmp_path / "loadavg"), DISPATCH_MEMINFO=str(tmp_path / "meminfo"),
               DISPATCH_NOW=str(NOW))
    d = orch / "dispatch"
    (d / "ready.txt").write_text("# the CTO's list\nW2-A T-A A.md W2-A-A5-run1.json\nW2-B T-B B.md W2-B-A5-run1.json\n")
    return type("W", (), dict(tmp=tmp_path, repo=repo, wt=wt, orch=orch, d=d, env=env, calls=calls, procs=procs,
                              held=held))


def tick(w, *extra, **env):
    e = dict(w.env, **{k: str(v) for k, v in env.items()})
    return subprocess.run([sys.executable, str(TOOL), "tick", *extra], capture_output=True, text=True, env=e)


def calls(w):
    return w.calls.read_text().splitlines() if w.calls.exists() else []


def status(w):
    return json.loads((w.d / "status.json").read_text())


def test_starts_the_first_ready_entry_when_every_check_passes(w):
    assert tick(w).returncode == 0
    assert calls(w) == ["launch W2-A T-A A.md W2-A-A5-run1.json"]
    assert "W2-A" in (w.d / "started.txt").read_text()


def test_one_start_per_tick_and_the_stagger(w):
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)  # within 120 s: nothing
    assert len(calls(w)) == 1 and "stagger" in status(w)["ready_waits"]
    tick(w, DISPATCH_NOW=NOW + 130)
    assert calls(w)[-1] == "launch W2-B T-B B.md W2-B-A5-run1.json"


def test_an_uncommitted_claim_on_integrate_is_skipped_with_its_reason(w):
    (w.d / "ready.txt").write_text("W2-O T-O O.md W2-O-A5-run1.json\n")
    tick(w)
    assert calls(w) == [] and "claim not committed" in status(w)["ready_waits"]["W2-O T-O"]


def test_a_worktree_that_reads_open_is_skipped(w):
    (w.wt / "W2-A" / ".tickets" / "T-A.md").write_text(ticket("T-A", "open"))
    git(w.wt / "W2-A", "commit", "-q", "-am", "reads open")
    tick(w)
    assert calls(w) == ["launch W2-B T-B B.md W2-B-A5-run1.json"]
    assert "does not read in_progress" in status(w)["ready_waits"]["W2-A T-A"]


def test_a_brief_with_a_placeholder_is_skipped(w):
    (w.orch / "briefs" / "A.md").write_text("head @@HEAD@@\n")
    tick(w)
    assert "@@" in status(w)["ready_waits"]["W2-A T-A"] and calls(w)[0].startswith("launch W2-B")


def test_a_running_lead_is_not_started_again_and_is_counted_from_the_processes(w):
    w.procs.write_text(json.dumps([{"cmd": LEAD.format("T-A"), "cwd": str(w.wt / "W2-A")},
                                   {"cmd": LEAD.format("T-X"), "cwd": str(w.wt / "W2-A-tests")},
                                   {"cmd": "python3 x.py", "cwd": str(w.wt / "W2-B")}]))
    tick(w)
    s = status(w)
    assert s["leads"] == ["W2-A"] and s["lead_count"] == 1 and s["ready_waits"]["W2-A T-A"] == "running"
    assert calls(w) == ["launch W2-B T-B B.md W2-B-A5-run1.json"]


def test_an_unread_inbox_item_holds_that_ticket(w):
    (w.d / "inbox").mkdir()
    (w.d / "inbox" / "x.txt").write_text("log: W2-A-A5-run0.json\nW2: W2-A\nstatus: PACKAGES\n")
    tick(w)
    assert "unread inbox" in status(w)["ready_waits"]["W2-A T-A"] and calls(w)[0].startswith("launch W2-B")


def test_a_shut_gate_starts_nothing(w):
    tick(w, DISPATCH_GATE_CMD="sh -c 'echo SHUT load; exit 1'")
    assert calls(w) == [] and all(r.startswith("gate shut") for r in status(w)["ready_waits"].values())


def test_nothing_outside_the_ready_list_starts(w):
    (w.d / "ready.txt").write_text("# empty\n")
    tick(w)
    assert calls(w) == []


def test_a_finished_return_becomes_one_inbox_item_and_is_marked_seen_once(w):
    (w.orch / "log" / "W2-A-A5-run1.json").write_text(json.dumps({"result": "task: x\nstatus: DONE at abc\n"}))
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 200)
    items = list((w.d / "inbox").glob("*.txt"))
    assert len(items) == 1 and "status: DONE at abc" in items[0].read_text()
    assert (w.orch / "log" / "returns-seen.txt").read_text().split() == ["W2-A-A5-run1.json"]
    assert "W2-A-A5-run1.json already holds a return" in status(w)["ready_waits"]["W2-A T-A"]


def test_land_runs_only_land_txt_lines_in_one_call_when_free_and_records_the_outcome(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\nW2-B=1234567\n")
    (w.d / "ready.txt").write_text("")
    tick(w)
    assert calls(w) == ["land W2-A=abcdef1 W2-B=1234567"]
    tick(w, DISPATCH_NOW=NOW + 60)  # land.py has exited: its outcome is read
    done = (w.d / "land-done.txt").read_text()
    assert "W2-A=abcdef1 CLOSED" in done and "W2-B=1234567 CLOSED" in done
    assert any("land batch" in i.read_text() for i in (w.d / "inbox").glob("*.txt"))
    tick(w, DISPATCH_NOW=NOW + 120)
    assert calls(w) == ["land W2-A=abcdef1 W2-B=1234567"]  # not landed twice


def test_land_waits_for_a_busy_queue_a_running_close_or_a_dirty_tree(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    w.held.write_text(json.dumps([str(w.orch / "merge-queue" / "run.lock")]))
    tick(w)
    assert calls(w) == [] and status(w)["land"] == "queue busy"
    w.held.write_text("[]")
    w.procs.write_text(json.dumps([{"cmd": "python3 tools/close_build.py W2-05", "cwd": "/"}]))
    tick(w)
    assert calls(w) == [] and status(w)["land"] == "a close is running"
    w.procs.write_text("[]")
    (w.repo / "dirty.txt").write_text("x")
    tick(w)
    assert calls(w) == [] and status(w)["land"] == "main tree not clean"


def test_a_malformed_land_line_lands_nothing(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\nrm -rf /\n")
    tick(w)
    assert not any(c.startswith("land") for c in calls(w)) and "malformed" in status(w)["land"]


def test_status_has_its_fields(w):
    tick(w)
    s = status(w)
    for k in ("time", "leads", "lead_count", "load", "mem_available_mb", "gate_open", "disk_open", "slots_held",
              "queue_busy", "main_clean", "inbox_unread", "inbox_oldest_age_s", "ready_waits", "land", "last_start"):
        assert k in s
    assert s["load"] == [3.0, 4.0, 5.0] and s["mem_available_mb"] == 16000
    assert "leads running (0, from the processes)" in (w.d / "status.txt").read_text()


def test_a_second_concurrent_tick_does_nothing(w):
    with open(w.d / "tick.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        r = tick(w)
    assert r.returncode == 0 and calls(w) == [] and "another tick is running" in (w.d / "dispatch.log").read_text()


def test_an_inbox_unread_for_30_minutes_is_flagged_stale(w):
    (w.d / "inbox").mkdir()
    item = w.d / "inbox" / "old.txt"
    item.write_text("log: x\nW2: W2-Z\nstatus: DONE\n")
    os.utime(item, (NOW - 1900, NOW - 1900))
    tick(w)
    assert (w.d / "inbox-stale.txt").exists()
    item.rename(w.d / "inbox" / "read.done")
    tick(w, DISPATCH_NOW=NOW + 200)
    assert not (w.d / "inbox-stale.txt").exists()


def test_dry_starts_and_lands_nothing(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    tick(w, "--dry")
    assert calls(w) == [] and "would start W2-A" in (w.d / "dispatch.log").read_text()


def test_a_dry_pass_marks_no_return_seen(w):
    (w.orch / "log" / "W2-A-A5-run1.json").write_text(json.dumps({"result": "status: DONE"}))
    tick(w, "--dry")
    assert not (w.orch / "log" / "returns-seen.txt").exists() and not list((w.d / "inbox").glob("*.txt"))


# ---- the review's findings (F1 to F8) ----------------------------------------------------------------------------

def old_item(w, name="old.txt", w2="W2-Z", age=1900):
    (w.d / "inbox").mkdir(exist_ok=True)
    item = w.d / "inbox" / name
    item.write_text(f"log: x\nW2: {w2}\nstatus: DONE\n")
    os.utime(item, (NOW - age, NOW - age))
    return item


def test_f1_the_stale_file_is_stable_across_ticks(w):
    old_item(w)
    tick(w)
    first = (w.d / "inbox-stale.txt").read_bytes()
    tick(w, DISPATCH_NOW=NOW + 300)
    assert (w.d / "inbox-stale.txt").read_bytes() == first and b"old.txt" in first


def test_f2_an_error_right_after_the_launch_does_not_land_twice(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    tick(w, DISPATCH_TEST_FAIL_AFTER_LAUNCH=1)
    tick(w, DISPATCH_NOW=NOW + 60)
    tick(w, DISPATCH_NOW=NOW + 120)
    assert [c for c in calls(w) if c.startswith("land")] == ["land W2-A=abcdef1"]
    assert "W2-A=abcdef1 CLOSED" in (w.d / "land-done.txt").read_text()


def test_f2_a_line_the_cto_appends_during_a_pass_survives(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    appender = w.tmp / "land_append.py"
    appender.write_text(f"import sys\nopen({str(w.calls)!r}, 'a').write('land ' + ' '.join(sys.argv[1:]) + '\\n')\n"
                        f"open({str(w.d / 'land.txt')!r}, 'a').write('W2-B=1234567\\n')\n"
                        "print('CLOSED W2-A: x')\n")
    tick(w, DISPATCH_LAND_CMD=f"{sys.executable} {appender}")
    assert (w.d / "land.txt").read_text() == "W2-B=1234567\n"
    tick(w, DISPATCH_NOW=NOW + 60)  # finalise W2-A
    tick(w, DISPATCH_NOW=NOW + 120)  # then land W2-B
    assert [c for c in calls(w) if c.startswith("land")] == ["land W2-A=abcdef1", "land W2-B=1234567"]


def test_f3_a_ready_entry_whose_log_is_not_a_lead_log_is_refused(w):
    (w.d / "ready.txt").write_text("W2-A T-A A.md notes.json\n")
    tick(w)
    assert calls(w) == [] and "not a lead log" in status(w)["ready_waits"]["W2-A T-A"]


def test_f4_a_start_that_never_ran_is_reported_once_and_not_retried(w):
    (w.d / "started.txt").write_text(f"{datetime.fromtimestamp(NOW - 400):%Y-%m-%d %H:%M:%S} W2-A A.md W2-A-A5-run1.json\n")
    (w.d / "ready.txt").write_text("W2-A T-A A.md W2-A-A5-run1.json\n")
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 200)
    never = [i for i in (w.d / "inbox").glob("*.txt") if "never ran" in i.read_text()]
    assert len(never) == 1 and calls(w) == []


def test_f4_the_start_is_recorded_before_the_launch(w):
    tick(w, DISPATCH_LAUNCH_CMD="false")
    assert "W2-A-A5-run1.json" in (w.d / "started.txt").read_text()


def test_f5_a_hanging_gate_fails_closed(w):
    r = tick(w, DISPATCH_GATE_CMD="sleep 30", DISPATCH_TIMEOUT_S=1)
    assert r.returncode == 0 and calls(w) == [] and not status(w)["gate_open"]


def test_f5_a_failed_truth_says_so_in_the_status(w):
    w.procs.write_text("not json")
    tick(w)
    assert (w.d / "status.txt").read_text().startswith("TICK FAILED") and calls(w) == []


def test_f6_land_and_close_are_detected_by_their_arguments(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    w.procs.write_text(json.dumps([{"cmd": "vim notes/land.py", "cwd": "/"},
                                   {"cmd": "grep close_build.py x", "cwd": "/"}]))
    tick(w)
    assert calls(w) == ["land W2-A=abcdef1"]
    w2 = json.loads((w.d / "status.json").read_text())
    assert not w2["close_running"]


def test_f6_a_running_land_makes_the_queue_busy(w):
    w.procs.write_text(json.dumps([{"cmd": "/usr/bin/python3 /x/tools/land.py W2-A=abcdef1", "cwd": "/"}]))
    tick(w)
    assert status(w)["queue_busy"]


def test_f7_a_claude_process_without_the_identity_is_not_a_lead(w):
    w.procs.write_text(json.dumps([{"cmd": "/home/u/.local/bin/claude -p hello", "cwd": str(w.wt / "W2-A")}]))
    tick(w)
    assert status(w)["leads"] == []


def test_f8_land_refused_off_the_integration_branch(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    git(w.repo, "checkout", "-q", "-b", "other")
    tick(w)
    assert calls(w) == [] and "not w2/integrate" in status(w)["land"]


def test_f8_a_dry_pass_finalises_nothing(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    tick(w)
    tick(w, "--dry", DISPATCH_NOW=NOW + 60)
    assert (w.d / "land-inflight.txt").exists() and not (w.d / "land-done.txt").exists()


def test_f8_a_refused_land_shows_its_output_tail(w):
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    (w.d / "ready.txt").write_text("")
    tick(w, DISPATCH_LAND_CMD="sh -c 'echo REFUSED before anything was queued: W2-A gitleaks'")
    tick(w, DISPATCH_NOW=NOW + 60)
    item = [i for i in (w.d / "inbox").glob("*.txt") if "land batch" in i.read_text()][0].read_text()
    assert "REFUSED before anything was queued" in item


def test_f8_an_unreadable_start_time_keeps_the_stagger(w):
    (w.d / "started.txt").write_text("garbled W2-Q Q.md W2-Q-A5-run1.json\n")
    tick(w)
    assert calls(w) == [] and "stagger" in status(w)["ready_waits"]
