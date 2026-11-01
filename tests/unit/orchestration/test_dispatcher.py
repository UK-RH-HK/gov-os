"""The dispatcher (governance/project/orchestration/tools/dispatch/, DEC-1010 item 6): one suite, from the first
version's cases through admission by peaks (DEC-1008 item 5) to the real CPU and the embedding server (DEC-1010 item 7).
The dispatcher's tests: planted repositories, fake processes, gates, launcher and land command; nothing real starts.
Run: python3 -m pytest -q tests/unit/orchestration/test_dispatcher.py."""
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/dispatch/dispatcher.py"
NOW = 1_800_000_000.0
PROCSTAT = "cpu  {busy} 0 0 {idle} {iowait} 0 0 0 0 0\ncpu0 1 0 0 1 0 0 0 0 0 0\n"
LEAD = '/home/u/.local/bin/claude -p --model x --settings {{"env":{{"GOV_ROLE":"orchestrator","GOV_TICKET":"{}"}}}}'


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def ticket(tid, status):
    return f"---\nid: {tid}\nstatus: {status}\nwbs_id: W2-X\n---\n# {tid}\n"


@pytest.fixture(scope="session")
def healthy_embed():
    """One planted embedding server answering at once, for every test that does not plant its own (DEC-1015: a
    server down holds starts)."""
    srv, mode = fake_embed_server()
    yield mode["url"]
    srv.shutdown()
    srv.server_close()


@pytest.fixture
def w(tmp_path, healthy_embed):
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
    (tmp_path / "procstat").write_text(PROCSTAT.format(busy=1000, iowait=0, idle=9000))
    (tmp_path / "proc").mkdir()
    (tmp_path / "proc" / "locks").write_text("")
    (tmp_path / "slots").mkdir()
    env = dict(os.environ, DISPATCH_ORCH=str(orch), DISPATCH_STATE=str(orch / "dispatch"), DISPATCH_REPO=str(repo),
               DISPATCH_PROCSTAT=str(tmp_path / "procstat"), DISPATCH_NPROC="20", DISPATCH_GUARD_CMD="true",
               DISPATCH_GUARD_SYNC="1",  # the harvest in the pass, for determinism; one test runs it detached
               # DEC-1015 item 2, all planted: a fake server answering; no slot file; an empty lock table
               DISPATCH_EMBED_URL=healthy_embed,
               DISPATCH_SLOT_GLOB=str(tmp_path / "slots" / "gov-os-heavy-slot-*.lock"), DISPATCH_PROC=str(tmp_path / "proc"),
               DISPATCH_WORKTREES=str(wt), DISPATCH_FAKE_PROCS=str(procs), DISPATCH_FAKE_HELD=str(held),
               DISPATCH_GATE_CMD="echo OPEN", DISPATCH_DISK_CMD="true",
               DISPATCH_LAUNCH_CMD=f"{sys.executable} {launcher}", DISPATCH_LAND_CMD=f"{sys.executable} {lander}",
               DISPATCH_LOADAVG=str(tmp_path / "loadavg"), DISPATCH_MEMINFO=str(tmp_path / "meminfo"),
               DISPATCH_NOW=str(NOW))
    d = orch / "dispatch"
    (d / "ready.txt").write_text("# the CTO's list\nW2-A T-A A.md W2-A-A5-run1.json\nW2-B T-B B.md W2-B-A5-run1.json\n")
    return type("W", (), dict(tmp=tmp_path, repo=repo, wt=wt, orch=orch, d=d, env=env, calls=calls, procs=procs,
                              held=held))


def tick(w, *extra, minute=True, **env):
    """One pass. `minute`: as a dispatcher running each minute, the last CPU sample is a minute old and the machine
    was idle since (a CPU test passes minute=False and plants its own samples)."""
    e = dict(w.env, **{k: str(v) for k, v in env.items()})
    if minute:
        t = float(e.get("DISPATCH_NOW", NOW))
        stat = Path(e["DISPATCH_PROCSTAT"])
        if stat.exists():
            f = [int(x) for x in stat.read_text().splitlines()[0].split()[1:9]]
            busy, total = f[0] + f[1] + f[2] + f[5] + f[6] + f[7], sum(f[:8])
            (w.d / "cpu_prev.json").write_text(json.dumps({"t": t - 60, "busy": busy, "total": total - 1000,
                                                           "emb": {}}))
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
    assert calls(w) == [] and all(r.startswith("not admitted: fallback") for r in status(w)["ready_waits"].values())


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
    w.procs.write_text(json.dumps([{"cmd": "python3 tools/close_build.py W2-A", "cwd": "/"}]))  # the same ticket
    tick(w)
    assert calls(w) == [] and status(w)["land"].startswith("a close of W2-A is running")
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


# ---- DEC-1008 item 5: admission by each job's peak ----------------------------------------------------------------

GB = 1024 * 1024  # kB


def history(w, lead_kb=(2_500_000, 2_200_000, 300_000), days_old=0):
    t0 = datetime.fromtimestamp(NOW - days_old * 86400 - 3600)
    cap = w.orch / "log" / "capacity"
    cap.mkdir(parents=True, exist_ok=True)
    kinds, mem = [], []
    for i in range(60):
        ts = (t0.replace(microsecond=0) + __import__("datetime").timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%S")
        kinds.append(json.dumps({"t": ts, "kinds": {"test_run": {"n": 20, "cpu": 6.0 + (i % 5), "rss_kb": 3 * GB},
                                                    "rebuild": {"n": 1 if i % 3 else 0, "cpu": 0.0, "rss_kb": 120_000},
                                                    "embedding": {"n": 1, "cpu": 4.0, "rss_kb": 600_000}}}))
        mem.append(json.dumps({"t": ts, "leads_kb": {"T-A": lead_kb[i % len(lead_kb)], "T-B": 400_000}}))
    (cap / "kinds.jsonl").write_text("\n".join(kinds) + "\n")
    (w.orch / "log" / "lead-mem.jsonl").write_text("\n".join(mem) + "\n")


def leads(w, n, rss_kb=300_000, extra=()):
    procs = [{"cmd": LEAD.format(f"T-L{i}"), "cwd": str(w.wt / "W2-A") + f"/../L{i}", "pid": 100 + i, "rss_kb": rss_kb}
             for i in range(n)]
    for i in range(n):  # a real lead worktree each, so lead_w2 maps it
        (w.wt / f"L{i}").mkdir(exist_ok=True)
        procs[i]["cwd"] = str(w.wt / f"L{i}")
    w.procs.write_text(json.dumps(procs + list(extra)))


@pytest.fixture
def wp(w):
    (w.orch / "tools" / "gate-config.json").write_text(json.dumps({"floor_kb": 3 * GB}))
    (w.orch / "tools" / "heavy_slots.conf").write_text("SLOTS=3\nWORKERS=6\n")
    history(w)
    w.env["DISPATCH_SLOTS_CONF"] = str(w.orch / "tools" / "heavy_slots.conf")
    (w.d / "config.json").write_text(json.dumps({"memory_rule": "literal"}))
    return w


def test_peaks_are_computed_from_the_history(wp):
    tick(wp)
    pk = json.loads((wp.d / "peaks.json").read_text())
    assert pk["lead"]["rss_kb_max"] == 2_500_000 and pk["lead"]["rss_kb_p95"] == 2_500_000
    assert pk["lead_own_max_kb"]["T-A"] == 2_500_000 and pk["lead_own_max_kb"]["T-B"] == 400_000
    assert pk["kinds"]["test_run"]["cpu_max"] == 10.0 and "rebuild_with_embedding" in pk["kinds"]
    assert "peaks" in (wp.d / "status.txt").read_text()


def test_the_owners_case_five_leads_at_a_low_load_are_refused_when_their_peaks_do_not_fit(wp):
    leads(wp, 5)  # 5 leads holding 0.3 GB each now; the load is low and gate_check says open
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {6 * GB} kB\n")
    tick(wp)
    s = status(wp)
    assert s["gate_open"] and not s["admit"] and "memory" in s["admit_reason"]
    assert calls(wp) == []


def test_admits_when_the_peaks_fit(wp):
    leads(wp, 1)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    tick(wp)
    assert status(wp)["admit"] and calls(wp) == ["launch W2-A T-A A.md W2-A-A5-run1.json"]


def test_the_cpu_rule_caps_leads_at_slots_times_k(wp):
    leads(wp, 6)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    tick(wp)
    assert not status(wp)["admit"] and "allows 6" in status(wp)["admit_reason"] and calls(wp) == []


def test_stale_peaks_fall_back_to_gate_check(wp):
    tick(wp)
    pk = json.loads((wp.d / "peaks.json").read_text())
    pk["computed"] = datetime.fromtimestamp(NOW - 8 * 86400).strftime("%Y-%m-%d %H:%M:%S")
    (wp.d / "peaks.json").write_text(json.dumps(pk))
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'", DISPATCH_NOW=NOW + 300)
    s = status(wp)
    assert not s["admit"] and s["admit_reason"].startswith("fallback to gate_check") and calls(wp) == []


def test_missing_peaks_fall_back_to_gate_check(w):
    tick(w)
    assert status(w)["admit_reason"].startswith("fallback to gate_check")


def test_a_heavy_step_outside_a_slot_is_named_and_holds_starts(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    outside = {"cmd": "/usr/bin/python3 -P -m gov.context.context_check", "cwd": str(wp.wt / "W2-B"), "pid": 500,
               "ppid": 1, "age_s": 400}
    leads(wp, 1, extra=[outside])
    tick(wp)
    s = status(wp)
    assert s["outside_slot"] and not s["admit"] and "outside a slot" in s["admit_reason"]
    assert "FINDING" in (wp.d / "status.txt").read_text() and calls(wp) == []


def test_a_heavy_step_inside_a_slot_is_not_a_finding(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    slot = {"cmd": "bash /x/tools/heavy_slot.sh python3 -m gov.context.context_check", "cwd": "/", "pid": 600, "ppid": 1}
    step = {"cmd": "/usr/bin/python3 -P -m gov.context.context_check", "cwd": str(wp.wt / "W2-B"), "pid": 601,
            "ppid": 600, "age_s": 900}
    leads(wp, 1, extra=[slot, step])
    tick(wp)
    assert status(wp)["outside_slot"] == [] and status(wp)["admit"]


def mixed_history(w):
    """Half the minutes with no test run (leads small), half with test runs (leads large)."""
    import datetime as dt
    t0 = datetime.fromtimestamp(NOW - 6 * 3600).replace(microsecond=0)
    cap = w.orch / "log" / "capacity"
    cap.mkdir(parents=True, exist_ok=True)
    kinds, mem = [], []
    for i in range(300):
        ts = (t0 + dt.timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%S")
        running = i % 2 == 1
        kinds.append(json.dumps({"t": ts, "kinds": {"test_run": {"n": 20 if running else 0, "cpu": 6.0,
                                                                 "rss_kb": 3 * GB if running else 0}}}))
        kb = 2_500_000 if running else 500_000
        mem.append(json.dumps({"t": ts, "leads_kb": {"T-A": kb, "T-B": kb}}))
    (cap / "kinds.jsonl").write_text("\n".join(kinds) + "\n")
    (w.orch / "log" / "lead-mem.jsonl").write_text("\n".join(mem) + "\n")


def test_the_slots_rule_admits_what_the_literal_rule_refuses(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "slots"}))
    mixed_history(wp)
    leads(wp, 4)  # 4 leads at 0.3 GB now
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {11 * GB} kB\n")
    tick(wp)
    s = status(wp)
    pk = json.loads((wp.d / "peaks.json").read_text())
    assert pk["lead_outside"]["rss_kb_p95"] == 500_000 and pk["lead_inside"]["rss_kb_p95"] == 2_500_000
    assert pk["slot_run_kb"] == 2_000_000  # the leads' rise beats the test run's own 1 GB share
    assert s["admit"] and "slots rule" in s["admit_reason"] and calls(wp)[0].startswith("launch W2-A")


def test_the_literal_rule_is_kept_as_an_option(wp):
    mixed_history(wp)
    leads(wp, 4)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {11 * GB} kB\n")
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "literal"}))
    tick(wp)
    s = status(wp)
    assert not s["admit"] and "literal rule" in s["admit_reason"] and calls(wp) == []


def test_the_slots_rule_without_enough_history_falls_back_to_gate_check(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "slots"}))
    leads(wp, 1)  # wp's history has a test run every minute: no minute outside verification
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    tick(wp)
    assert status(wp)["admit_reason"].startswith("fallback to gate_check (fewer than 120 minutes")


# ---- the review of dispatcher_next.py (F1 to F5) ------------------------------------------------------------------

def test_f1_a_waiting_launcher_counts_as_a_lead(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    leads(wp, 5, extra=[{"cmd": "bash /x/dispatch/launch_now.sh W2-Q T-Q Q.md W2-Q-A5-run1.json", "cwd": "/"}])
    tick(wp)
    s = status(wp)
    assert s["pending_launches"] == ["W2-Q"] and not s["admit"] and "1 launching" in s["admit_reason"]


def test_f1_a_recent_start_without_a_process_counts_as_a_lead(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    (wp.d / "started.txt").write_text(f"{datetime.fromtimestamp(NOW - 300):%Y-%m-%d %H:%M:%S} W2-Q Q.md W2-Q-A5-run1.json\n")
    leads(wp, 5)
    tick(wp, DISPATCH_NOW=NOW)
    assert status(wp)["pending_launches"] == ["W2-Q"] and not status(wp)["admit"]


def test_f1_the_dispatcher_launches_without_the_gate_wait():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dn", TOOL)
    dn = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dn)
    argv = dn.default_launch_argv()
    assert argv[-1].endswith("dispatch/launch_now.sh") and "launch_when_gate_opens" not in " ".join(argv)
    text = (TOOL.parent / "launch_now.sh").read_text()
    assert "gate_check" not in text.split("\n", 6)[-1] and "disk_gate.sh" in text


def test_f2_the_shared_services_headroom_is_counted_once(wp):
    leads(wp, 1, extra=[{"cmd": "/x/ollama/llama-server --model m", "cwd": "/", "rss_kb": 200_000}])
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    tick(wp)
    # the planted embedding p95 is 600,000 kB; 200,000 resident: 400,000 kB (390 MB) of headroom
    assert "services' headroom 390 MB" in status(wp)["admit_reason"]


def test_f3_a_bad_peaks_value_refuses_and_the_tick_goes_on(wp):
    tick(wp)
    pk = json.loads((wp.d / "peaks.json").read_text())
    pk["lead"]["rss_kb_p95"] = "x"
    (wp.d / "peaks.json").write_text(json.dumps(pk))
    (wp.orch / "log" / "W2-B-A5-run0.json").write_text(json.dumps({"result": "status: DONE"}))
    (wp.d / "started.txt").write_text("")
    leads(wp, 1)
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 300)
    s = status(wp)
    assert not s["admit"] and ("unreadable" in s["admit_reason"] or "error" in s["admit_reason"])
    assert "W2-B-A5-run0.json" in (wp.orch / "log" / "returns-seen.txt").read_text()


def test_f3_a_bad_config_value_refuses(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "literal", "K": "two"}))
    tick(wp)
    assert not status(wp)["admit"] and "error" in status(wp)["admit_reason"] and calls(wp) == []


def test_f4_the_newcomer_is_priced_at_its_own_max(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "slots"}))
    mixed_history(wp)
    lines = (wp.orch / "log" / "lead-mem.jsonl").read_text().splitlines()
    r = json.loads(lines[0])
    r["leads_kb"]["T-A"] = 20 * GB  # T-A once used 20 GB outside verification
    lines[0] = json.dumps(r)
    (wp.orch / "log" / "lead-mem.jsonl").write_text("\n".join(lines) + "\n")
    leads(wp, 1)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    tick(wp)
    s = status(wp)
    assert "memory" in s["ready_waits"]["W2-A T-A"] and calls(wp)[0].startswith("launch W2-B")


def test_f5_gov_check_by_the_shim_and_a_bare_pytest_are_heavy_a_single_file_is_not(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    leads(wp, 1, extra=[
        {"cmd": "/home/u/.local/bin/gov check --json", "cwd": "/w", "pid": 700, "age_s": 400},
        {"cmd": "/usr/bin/python3 /home/usain/.local/bin/pytest tests/unit", "cwd": "/w", "pid": 701, "age_s": 400},
        {"cmd": "/usr/bin/python3 -m pytest tests/unit/test_one.py -q", "cwd": "/w", "pid": 702, "age_s": 900}])
    tick(wp)
    found = " ".join(status(wp)["outside_slot"])
    assert "pid 700" in found and "pid 701" in found and "pid 702" not in found


def test_review2_a_single_file_with_an_option_path_is_not_heavy_a_folder_is(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    leads(wp, 1, extra=[
        {"cmd": "/usr/bin/python3 -m pytest tests/unit/test_one.py --junitxml /tmp/x.xml -q", "cwd": "/w", "pid": 710,
         "age_s": 900},
        {"cmd": "/usr/bin/python3 /home/usain/.local/bin/pytest tests/unit/test_two.py::test_x", "cwd": "/w", "pid": 711,
         "age_s": 900},
        {"cmd": "/usr/bin/python3 -m pytest tests/unit/big --junitxml /tmp/y.xml", "cwd": "/w", "pid": 712,
         "age_s": 900}])
    tick(wp)
    found = " ".join(status(wp)["outside_slot"])
    assert "pid 710" not in found and "pid 711" not in found and "pid 712" in found


def plant_reranker_peak(wp):
    tick(wp)
    pk = json.loads((wp.d / "peaks.json").read_text())
    pk.setdefault("kinds", {})["reranker"] = {"cpu_p95": 1, "cpu_max": 1, "rss_kb_p95": 3 * GB, "rss_kb_max": 3 * GB,
                                              "samples": 60}
    (wp.d / "peaks.json").write_text(json.dumps(pk))
    (wp.d / "started.txt").write_text("")
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {30 * GB} kB\n")


def test_review2_a_reranker_outside_every_lead_tree_gets_headroom(wp):
    plant_reranker_peak(wp)
    queue_rr = [{"cmd": "/usr/bin/python3 /x/tools/land.py W2-Q=abcdef1", "cwd": "/", "pid": 800, "ppid": 1},
                {"cmd": "/home/u/.local/share/gov-os/reranker-venv/bin/python -I serve.py", "cwd": "/", "pid": 801,
                 "ppid": 800, "rss_kb": 1 * GB}]
    leads(wp, 1, extra=queue_rr)
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 300)
    # the planted embedding p95 600,000 kB (none resident) + the reranker's 3 GB p95 minus its 1 GB resident
    assert f"services' headroom {(600_000 + 2 * GB) // 1024} MB" in status(wp)["admit_reason"]
    leads(wp, 1)  # no queue, no close, no reranker outside the leads: no reranker headroom
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 600)
    assert f"services' headroom {600_000 // 1024} MB" in status(wp)["admit_reason"]


def test_review2_a_reranker_inside_a_lead_tree_is_not_counted_again(wp):
    plant_reranker_peak(wp)
    leads(wp, 1, extra=[{"cmd": "/home/u/.local/share/gov-os/reranker-venv/bin/python -I serve.py", "cwd": "/",
                         "pid": 820, "ppid": 100, "rss_kb": 1 * GB}])  # pid 100: the lead L0
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 300)
    s = status(wp)
    assert s["rerankers_outside_kb"] == 0 and f"services' headroom {600_000 // 1024} MB" in s["admit_reason"]


# ---- DEC-1010 item 6: the code apart from its state ----------------------------------------------------------------

def test_the_launcher_is_the_committed_one_and_the_state_is_not_the_code_folder(w):
    import importlib.util
    spec = importlib.util.spec_from_file_location("dv", TOOL)
    dv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dv)
    assert dv.default_launch_argv()[-1] == str(TOOL.parent / "launch_now.sh")
    tick(w)
    assert (w.d / "status.json").exists() and not (TOOL.parent / "status.json").exists()


# ---- DEC-1010 item 7: the real CPU and the embedding server ---------------------------------------------------------

def cpu_prev(w, busy, total, emb=None):
    (w.d / "cpu_prev.json").write_text(json.dumps({"t": NOW - 60, "busy": busy, "total": total, "emb": emb or {}}))


def test_real_busy_cores_refuse_a_start_though_memory_fits(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    cpu_prev(wp, busy=1000, total=10000)
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2900, idle=9100, iowait=0))  # 1,900 of 2,000 busy: 19 cores
    tick(wp, minute=False)
    s = status(wp)
    assert s["busy_cores"] == 19.0 and not s["admit"] and "real CPU" in s["admit_reason"] and calls(wp) == []


def test_a_quiet_machine_admits_and_iowait_is_not_busy(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    cpu_prev(wp, busy=1000, total=10000)
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=1200, idle=9000, iowait=1800))  # 200 busy, 1,800 iowait
    tick(wp, minute=False)
    s = status(wp)
    assert s["busy_cores"] == 2.0 and s["admit"] and calls(wp)[0].startswith("launch W2-A")
    assert "real busy cores 2.0 of 20" in (wp.d / "status.txt").read_text()


def test_room_is_left_for_the_embedding_servers_p95(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    cpu_prev(wp, busy=1000, total=10000)
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2400, idle=9600, iowait=0))  # 14 cores busy
    tick(wp, minute=False)  # the planted embedding p95 is 4.0 cores and it uses none now: 14 + 4 >= 20 - 2
    assert not status(wp)["admit"] and "embedding server" in status(wp)["admit_reason"]


def test_an_embedding_server_already_at_its_p95_needs_no_more_room(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    hz = os.sysconf("SC_CLK_TCK")
    cpu_prev(wp, busy=1000, total=10000, emb={"900": 0})
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2400, idle=9600, iowait=0))
    leads(wp, 1, extra=[{"cmd": "/x/ollama/llama-server --model m", "cwd": "/", "pid": 900, "cpu_ticks": 4 * 60 * hz}])
    tick(wp, minute=False)  # the server used 4 cores over the minute: no room left to add
    s = status(wp)
    assert s["embedding_cores"] == 4.0 and s["admit"]


def test_an_unreadable_proc_stat_refuses(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    tick(wp, DISPATCH_PROCSTAT=str(wp.tmp / "missing"))
    assert not status(wp)["admit"] and "real CPU unreadable" in status(wp)["admit_reason"]


# ---- the review of v3 (F1 to F3) -------------------------------------------------------------------------------------

def test_v3_f1_the_real_cpu_refuses_even_without_peaks(w):
    cpu_prev(w, busy=1000, total=10000)
    (w.tmp / "procstat").write_text(PROCSTAT.format(busy=2900, idle=9100, iowait=0))  # 19 busy cores
    tick(w, minute=False)  # no peaks.json: the gate_check fallback, which says open
    s = status(w)
    assert s["gate_open"] and not s["admit"] and s["admit_reason"].startswith("real CPU: 19.0 busy cores")
    assert calls(w) == []


def test_v3_f2_a_first_pass_measures_and_refuses(w):
    tick(w, minute=False)  # no cpu_prev.json
    s = status(w)
    assert s["cpu_measuring"] and "measuring" in s["admit_reason"] and calls(w) == []
    assert (w.d / "cpu_prev.json").exists()


def test_v3_f2_a_sample_older_than_3_minutes_measures_again(w):
    (w.d / "cpu_prev.json").write_text(json.dumps({"t": NOW - 200, "busy": 1000, "total": 9000, "emb": {}}))
    tick(w, minute=False)
    assert "measuring" in status(w)["admit_reason"] and calls(w) == []
    assert json.loads((w.d / "cpu_prev.json").read_text())["t"] == NOW  # the new sample, for the next pass


def test_v3_f2_a_dry_pass_records_no_cpu_sample(w):
    tick(w, "--dry", minute=False)
    assert not (w.d / "cpu_prev.json").exists()


def test_v3_f3_a_state_folder_inside_the_code_is_refused(w):
    r = tick(w, minute=False, DISPATCH_STATE=str(TOOL.parent))
    assert r.returncode != 0 and "inside it" in r.stderr
    assert not (TOOL.parent / "status.json").exists() and not (TOOL.parent / "cpu_prev.json").exists()


def test_v3_f3_the_scripts_clear_every_dispatch_variable():
    for script in ("run_tick.sh", "loop.sh"):
        line = next(l for l in (TOOL.parent / script).read_text().splitlines() if "compgen -v DISPATCH_" in l)
        r = subprocess.run(["bash", "-c", line + "\nenv | grep '^DISPATCH_' || true"], capture_output=True, text=True,
                           env=dict(os.environ, DISPATCH_STATE="/tmp/stray", DISPATCH_DIR="/tmp/stray2"))
        assert r.stdout.strip() == "", script


# ---- DEC-1014 item 1: a landing never waits for a close it does not conflict with ---------------------------------

def land_one(w, line="W2-A=abcdef1"):
    (w.d / "land.txt").write_text(line + "\n")
    (w.d / "ready.txt").write_text("")


def commit(d, files, msg, task=None):
    for rel, text in files.items():
        p = Path(d) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg, *(["--trailer", f"Task: {task}"] if task else []))
    return git(d, "rev-parse", "HEAD")


def test_a_close_of_other_tickets_does_not_hold_a_landing(w):
    land_one(w)
    w.procs.write_text(json.dumps([{"cmd": "python3 /x/tools/close_build.py W2-B W2-C", "cwd": "/"}]))
    tick(w)
    assert calls(w) == ["land W2-A=abcdef1"]


def test_a_close_of_the_same_ticket_holds_it(w):
    land_one(w)
    w.procs.write_text(json.dumps([{"cmd": "python3 /x/tools/close_build.py W2-A", "cwd": "/"}]))
    tick(w)
    assert calls(w) == [] and "a close of W2-A is running" in status(w)["land"]


def test_a_close_committing_its_records_holds_one_pass(w):
    land_one(w)
    w.procs.write_text(json.dumps([{"cmd": "python3 /x/tools/close_build.py W2-B", "cwd": "/"}]))
    (w.repo / ".tickets" / "T-A.md").write_text(ticket("T-A", "closed"))  # a close mid-commit
    tick(w)
    assert calls(w) == [] and "committing its records" in status(w)["land"]


# ---- DEC-1014 item 2: the watcher watched ----------------------------------------------------------------------------

def deadman_line(w, at):
    (w.orch / "log" / "deadman.log").write_text(json.dumps({"at": at, "verdict": "alive"}) + "\n")


def test_a_silent_sentinel_is_flagged_once_while_it_is_expected(w):
    (w.d / "sentinel-expected").write_text("started 2026-11-01\n")
    deadman_line(w, datetime.fromtimestamp(NOW - 3 * 3600).strftime("%Y-%m-%d %H:%M:%S"))
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert "sentinel" in (w.d / "inbox-stale.txt").read_text()
    assert len([i for i in (w.d / "inbox").glob("*.txt") if "Sentinel: silent" in i.read_text()]) == 1
    deadman_line(w, datetime.fromtimestamp(NOW + 100).strftime("%Y-%m-%d %H:%M:%S"))
    for i in (w.d / "inbox").glob("*.txt"):
        i.rename(w.d / "inbox" / (i.name + ".read"))
    tick(w, DISPATCH_NOW=NOW + 120)
    assert not (w.d / "inbox-stale.txt").exists() and status(w)["sentinel"] == "watched"


def test_no_sentinel_expected_no_flag(w):
    deadman_line(w, datetime.fromtimestamp(NOW - 3 * 3600).strftime("%Y-%m-%d %H:%M:%S"))
    tick(w)
    assert not (w.d / "inbox-stale.txt").exists() and status(w)["sentinel"] == "not expected"


# ---- DEC-1014 item 3: the CTO's watchers as passes --------------------------------------------------------------------

def test_an_interim_result_becomes_one_inbox_item_and_holds_no_start(w):
    tick(w)  # the first pass marks each worktree's history seen
    commit(w.wt / "W2-B", {"docs/m.md": "x"}, "W2-B: the measure after the fix (hit@5 12 of 20)", "T-B")
    commit(w.wt / "W2-B", {"docs/n.md": "y"}, "W2-B: a plain step", "T-B")
    tick(w, DISPATCH_NOW=NOW + 200)
    tick(w, DISPATCH_NOW=NOW + 400)
    items = [i.read_text() for i in (w.d / "inbox").glob("*.txt") if "Interim:" in i.read_text()]
    assert len(items) == 1 and "the measure after the fix" in items[0]
    assert all("W2: W2-B" not in i for i in items)  # an interim item never holds a lead's start


def test_a_commit_already_on_integrate_is_not_an_interim_result(w):
    tick(w)
    commit(w.repo, {"docs/p.md": "z"}, "a probe record on integrate")  # the fixture's repository is on w2/integrate
    git(w.wt / "W2-B", "merge", "-q", "--ff-only", "w2/integrate")
    tick(w, DISPATCH_NOW=NOW + 200)
    assert not [i for i in (w.d / "inbox").glob("*.txt") if "Interim:" in i.read_text()]


def test_a_new_guard_refusal_becomes_one_inbox_item(w):
    gl = w.orch / "log" / "guard-refusals.jsonl"
    gl.write_text('{"at": "old 1"}\n{"at": "old 2"}\n')
    tick(w)  # notes where the file ends
    with open(gl, "a") as f:
        f.write('{"at": "new 3", "form": "x"}\n')
    tick(w, DISPATCH_NOW=NOW + 200)
    tick(w, DISPATCH_NOW=NOW + 400)
    items = [i.read_text() for i in (w.d / "inbox").glob("*.txt") if "Guard:" in i.read_text()]
    assert len(items) == 1 and "new 3" in items[0]


def test_the_nightlys_line_for_today_becomes_one_inbox_item(w):
    nd = w.orch / "log" / "nightly"
    nd.mkdir(parents=True)
    today = datetime.fromtimestamp(NOW).strftime("%Y-%m-%d")
    (nd / "status.txt").write_text(f"2000-01-01 ran | old\n{today} ran | verdict: green\n")
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    items = [i.read_text() for i in (w.d / "inbox").glob("*.txt") if "Nightly:" in i.read_text()]
    assert len(items) == 1 and "verdict: green" in items[0]


# ---- DEC-1014 item 1: land.py's commit tolerates a concurrent close's commit ----------------------------------------

TOOLS = Path(__file__).resolve().parents[3] / ".gov-runtime/scratch/orchestrator/tools"


def load_tool(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name.replace(".", "_") + "_under_test", TOOLS / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def locked_repo(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "w2/integrate")
    commit(repo, {"a.txt": "1"}, "base")
    (repo / "b.txt").write_text("2")
    lock = repo / ".git" / "index.lock"
    lock.write_text("")
    return repo, lock


@pytest.mark.parametrize("tool", ["land.py", "close_build.py"])
def test_the_record_commit_is_retried_while_another_holds_the_index_lock(tmp_path, tool):
    import threading
    repo, lock = locked_repo(tmp_path)
    threading.Timer(0.6, lock.unlink).start()  # the other commit finishes 0.6 s later
    mod = load_tool(tool)
    assert mod.git_retry(["add", "--", "b.txt"], root=repo, wait=0.5).returncode == 0
    r = mod.git_retry(["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "close", "--", "b.txt"],
                      root=repo, wait=0.5)
    assert r.returncode == 0 and git(repo, "log", "-1", "--format=%s") == "close"


@pytest.mark.parametrize("tool", ["land.py", "close_build.py"])
def test_f6_retry_exhaustion_fails_cleanly(tmp_path, tool):
    repo, lock = locked_repo(tmp_path)  # held throughout
    mod = load_tool(tool)
    t0 = time.time()
    r = mod.git_retry(["add", "--", "b.txt"], root=repo, tries=3, wait=0.2)
    assert r.returncode != 0 and "index.lock" in r.stderr and lock.exists()
    assert time.time() - t0 >= 0.4  # three tries, two waits; then it gives back, no exception
    assert "b.txt" not in git(repo, "diff", "--cached", "--name-only")


@pytest.mark.parametrize("tool", ["land.py", "close_build.py"])
def test_f1_both_tools_commit_their_records_through_the_retry(tool):
    src = (TOOLS / tool).read_text()
    assert 'git_retry(["add", "--", *paths])' in src and 'cm = git_retry(["commit", "-q", "-m",' in src


# ---- v4 review F6: the missing tests --------------------------------------------------------------------------------

def test_f6_another_dirty_path_still_refuses_while_a_close_runs(w):
    land_one(w)
    w.procs.write_text(json.dumps([{"cmd": "python3 /x/tools/close_build.py W2-B", "cwd": "/"}]))
    (w.repo / ".tickets" / "T-A.md").write_text(ticket("T-A", "closed"))  # the close's record
    (w.repo / "notes.txt").write_text("someone else's edit\n")  # and something that is not
    tick(w)
    assert calls(w) == [] and status(w)["land"] == "main tree not clean"


def test_f6_an_interim_item_leaves_a_leads_start_free(w):
    (w.d / "ready.txt").write_text("")
    tick(w)  # marks each worktree's history seen
    commit(w.wt / "W2-B", {"docs/m.md": "x"}, "W2-B: the baseline figures", "T-B")
    (w.d / "ready.txt").write_text("W2-B T-B B.md W2-B-A5-run1.json\n")
    tick(w, DISPATCH_NOW=NOW + 200)
    assert [i for i in (w.d / "inbox").glob("*.txt") if "Interim: W2-B" in i.read_text()]
    assert any(c.startswith("launch") and "W2-B" in c for c in calls(w))


def test_f6_the_sentinel_re_silences_after_clearing(w):
    (w.d / "sentinel-expected").write_text("started\n")
    old = lambda t: datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
    deadman_line(w, old(NOW - 3 * 3600))
    tick(w)
    deadman_line(w, old(NOW + 100))
    tick(w, DISPATCH_NOW=NOW + 120)  # cleared
    assert status(w)["sentinel"] == "watched"
    tick(w, DISPATCH_NOW=NOW + 100 + 7300)  # silent again
    assert len([i for i in (w.d / "inbox").glob("*.txt") if "Sentinel: silent" in i.read_text()]) == 2


# F2: the harvest out of the critical path

def harvester(w, body):
    h = w.tmp / "harvest.py"
    h.write_text(f"import sys, time\nopen({str(w.calls)!r}, 'a').write('harvest\\n')\n{body}\n")
    return f"{sys.executable} {h}"


def test_f2_the_harvest_runs_detached_and_does_not_hold_the_pass(w):
    t0 = time.time()
    r = tick(w, DISPATCH_GUARD_SYNC="0", DISPATCH_GUARD_CMD=harvester(w, "time.sleep(4)"))
    assert r.returncode == 0 and time.time() - t0 < 3.5
    assert not (w.d / "guard-harvest.json").exists()  # still running when the pass has ended
    for _ in range(100):
        if (w.d / "guard-harvest.json").exists():
            break
        time.sleep(0.1)
    assert json.loads((w.d / "guard-harvest.json").read_text())["rc"] == 0


def test_f2_the_harvest_comes_after_the_start_and_land_decisions(w):
    (w.d / "land.txt").write_text("W2-B=abcdef1\n")
    tick(w, DISPATCH_GUARD_CMD=harvester(w, ""))
    assert [c.split()[0] for c in calls(w)] == ["launch", "land", "harvest"]


def test_f2_the_harvest_runs_at_most_every_guard_harvest_s(w):
    cmd = harvester(w, "")
    for t in (NOW, NOW + 60, NOW + 700):
        tick(w, DISPATCH_GUARD_CMD=cmd, DISPATCH_NOW=t)
    assert calls(w).count("harvest") == 2


def test_f2_a_failed_harvest_is_one_of_the_pass_failures(w):
    tick(w, DISPATCH_GUARD_CMD=harvester(w, "sys.exit(3)"))
    assert any("guard harvest: exit 3" in f for f in status(w)["failures"])
    assert (w.d / "status.txt").read_text().startswith("TICK FAILED in part: guard harvest")


def test_f2_a_harvest_past_its_time_limit_is_a_failure(w):
    (w.d / "config.json").write_text(json.dumps({"guard_harvest_timeout_s": 1}))
    tick(w, DISPATCH_GUARD_CMD=harvester(w, "time.sleep(5)"))
    assert any("guard harvest: timed out" in f for f in status(w)["failures"])
    assert status(w)["guard_harvest"]["rc"] == 124


def test_f2_a_second_harvest_waits_for_the_first(w):
    with open(w.d / "guard-harvest.lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        r = subprocess.run([sys.executable, str(TOOL), "harvest"], capture_output=True, text=True,
                           env=dict(w.env, DISPATCH_GUARD_CMD=harvester(w, "")))
    assert r.returncode == 0 and "harvest" not in calls(w)


# F3: refusals already judged, the offset, a shrunk file

def guard_rows(w, *rows, mode="a"):
    with open(w.orch / "log" / "guard-refusals.jsonl", mode) as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))


def guard_items(w):
    return [i.read_text() for i in (w.d / "inbox").glob("*.txt") if "Guard:" in i.read_text()]


def test_f3_rows_already_judged_raise_no_item(w):
    guard_rows(w, {"time": "old"}, mode="w")
    tick(w)
    guard_rows(w, {"time": "a", "verdict": "false-positive"}, {"at": "b", "judgement": "a known pattern"},
               {"time": "c", "verdict": ""})
    tick(w, DISPATCH_NOW=NOW + 60)
    items = guard_items(w)
    assert len(items) == 1 and '"c"' in items[0]


def test_f3_the_offset_is_written_only_when_the_file_grows(w):
    guard_rows(w, {"time": "old"}, mode="w")
    tick(w)
    off = w.d / "guard-offset.txt"
    os.utime(off, (1, 1))
    tick(w, DISPATCH_NOW=NOW + 60)
    assert off.stat().st_mtime == 1 and off.read_text() == "1"


def test_f3_a_shrunk_file_is_re_baselined_without_a_flood(w):
    guard_rows(w, {"time": "1"}, {"time": "2"}, {"time": "3"}, mode="w")
    tick(w)
    guard_rows(w, {"time": "reset"}, mode="w")  # rewritten shorter
    tick(w, DISPATCH_NOW=NOW + 60)
    assert guard_items(w) == [] and (w.d / "guard-offset.txt").read_text() == "1"
    guard_rows(w, {"time": "fresh"})
    tick(w, DISPATCH_NOW=NOW + 120)
    items = guard_items(w)
    assert len(items) == 1 and "fresh" in items[0]


# F4: the sentinel's own line; a malformed deadman.log

def test_f4_the_sentinels_silence_is_added_though_the_inbox_is_already_stale(w):
    old_item(w)
    tick(w)
    first = (w.d / "inbox-stale.txt").read_text()
    assert first.startswith("inbox: ")
    (w.d / "sentinel-expected").write_text("started\n")
    deadman_line(w, datetime.fromtimestamp(NOW - 3 * 3600).strftime("%Y-%m-%d %H:%M:%S"))
    tick(w, DISPATCH_NOW=NOW + 60)
    both = (w.d / "inbox-stale.txt").read_text()
    lines = both.splitlines()
    assert lines[0].startswith("sentinel: ") and lines[1] == first.strip() and len(lines) == 2
    assert "sentinel" in both[:150]  # within what deadman.py keys on
    tick(w, DISPATCH_NOW=NOW + 120)
    assert (w.d / "inbox-stale.txt").read_text() == both  # no second line, no change


def test_f4_a_malformed_deadman_line_falls_back_to_the_newest_parseable_one(w):
    (w.d / "sentinel-expected").write_text("started\n")
    recent = datetime.fromtimestamp(NOW - 60).strftime("%Y-%m-%d %H:%M:%S")
    (w.orch / "log" / "deadman.log").write_text(json.dumps({"at": recent}) + "\n{broken\n[1, 2]\n")
    tick(w)
    assert status(w)["sentinel"] == "watched" and not status(w)["failures"]


def test_f4_a_deadman_log_with_no_parseable_line_reads_unreadable(w):
    (w.d / "sentinel-expected").write_text("started\n")
    (w.orch / "log" / "deadman.log").write_text("{broken\nnot json\n")
    tick(w)
    assert "unreadable" in status(w)["sentinel"]
    assert (w.d / "status.txt").read_text().startswith("dispatcher ")  # the status is whole, not a failed tick


# F5: unique names; a rebased interim result

def test_f5_two_nightly_lines_give_two_items(w):
    nd = w.orch / "log" / "nightly"
    nd.mkdir(parents=True)
    today = datetime.fromtimestamp(NOW).strftime("%Y-%m-%d")
    (nd / "status.txt").write_text(f"{today} ran | verdict: red\n{today} re-ran | verdict: green\n")
    tick(w)
    items = [i.read_text() for i in (w.d / "inbox").glob("*.txt") if "Nightly:" in i.read_text()]
    assert len(items) == 2


def test_f5_an_inbox_item_never_overwrites_another(w, monkeypatch):
    import importlib.util
    for k, v in w.env.items():
        if k.startswith("DISPATCH_"):
            monkeypatch.setenv(k, v)
    spec = importlib.util.spec_from_file_location("dispatcher_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    a, b = mod.inbox_item("same", "one\n"), mod.inbox_item("same", "two\n")
    assert a != b and a.read_text() == "one\n" and b.read_text() == "two\n"


def test_f5_a_rebased_interim_result_is_not_reported_again(w):
    tick(w)
    commit(w.wt / "W2-B", {"docs/m.md": "x"}, "W2-B: the baseline figures", "T-B")
    tick(w, DISPATCH_NOW=NOW + 200)
    commit(w.repo, {"docs/other.md": "y"}, "another landing on integrate")
    git(w.wt / "W2-B", "rebase", "-q", "w2/integrate")  # a new commit id, the same change
    tick(w, DISPATCH_NOW=NOW + 400)
    items = [i for i in (w.d / "inbox").glob("*.txt") if "Interim:" in i.read_text()]
    assert len(items) == 1


# ---- DEC-1015 item 2: the embedding server's health -------------------------------------------------------------------

@pytest.fixture
def server():
    """A planted embedding server on a free port: "ok" answers at once, "hang" answers after 3 s."""
    srv, mode = fake_embed_server()
    yield mode
    srv.shutdown()
    srv.server_close()


def fake_embed_server():
    import http.server
    import threading
    mode = {"m": "ok", "hits": 0}

    class H(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            mode["hits"] += 1
            if mode["m"] == "hang":
                time.sleep(3)
            body = json.dumps({"embeddings": [[0.1, 0.2]]}).encode()
            try:
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except OSError:
                pass

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    mode["url"] = f"http://127.0.0.1:{srv.server_address[1]}/api/embed"
    return srv, mode


def conf(w, **kv):
    (w.d / "config.json").write_text(json.dumps(kv))


def etick(w, server, t):
    return tick(w, DISPATCH_EMBED_URL=server["url"], DISPATCH_NOW=t)


def items_with(w, label):
    return [i.read_text() for i in (w.d / "inbox").glob("*.txt") if label in i.read_text()]


def test_embed_a_server_answering_is_healthy(w, server):
    etick(w, server, NOW)
    assert server["hits"] == 1 and status(w)["embedding_server"]["state"] == "healthy"
    assert "embedding server: healthy (" in (w.d / "status.txt").read_text() and not items_with(w, "Server:")


REFUSED = "http://127.0.0.1:9/api/embed"  # nothing listens: a refused connection


def test_embed_refused_three_times_is_not_running_one_item_and_recovery_clears_it(w, server):
    (w.d / "ready.txt").write_text("")
    for t in (NOW, NOW + 60):
        tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    assert not items_with(w, "Server:") and status(w)["embedding_server"]["state"] == "failing"
    for t in (NOW + 120, NOW + 180):  # the third refusal in a row, then a fourth
        tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    down = items_with(w, "Server:")
    assert len(down) == 1 and "NOT RUNNING since" in down[0] and "W2:" not in down[0]
    assert (w.d / "inbox-stale.txt").read_text().startswith("server: the embedding server NOT RUNNING since")
    assert "embedding server: NOT RUNNING since" in (w.d / "status.txt").read_text()
    for i in (w.d / "inbox").glob("*.txt"):
        i.rename(w.d / "inbox" / (i.name + ".read"))
    etick(w, server, NOW + 240)
    assert not (w.d / "inbox-stale.txt").exists() and status(w)["embedding_server"]["state"] == "healthy"


def test_embed_a_configured_restart_applies_to_not_running(w):
    r = w.tmp / "restart.py"
    r.write_text(f"open({str(w.calls)!r}, 'a').write('restart\\n')\n")
    conf(w, embed_hung_after=1, embed_restart_after_s=60, embed_restart_cmd=f"{sys.executable} {r}")
    (w.d / "ready.txt").write_text("")
    for t in (NOW, NOW + 30, NOW + 90, NOW + 150):
        tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    assert calls(w).count("restart") == 1


HELD = "embedding server hung: starts held (DEC-1015)"


@pytest.mark.parametrize("why", ["hung", "refused"])
def test_embed_starts_are_held_while_the_server_is_down_and_landings_are_not(w, server, why):
    conf(w, embed_timeout_s=0.5, embed_hung_after=1)
    server["m"] = "hang"
    url = server["url"] if why == "hung" else REFUSED
    tick(w, DISPATCH_EMBED_URL=url, DISPATCH_NOW=NOW)  # starts W2-A (no state yet), then finds the server down
    assert [c for c in calls(w) if c.startswith("launch")] and status(w)["embedding_server"]["state"] in (
        "HUNG", "NOT RUNNING")
    (w.d / "land.txt").write_text("W2-A=abcdef1\n")
    tick(w, DISPATCH_EMBED_URL=url, DISPATCH_NOW=NOW + 200)  # past the stagger: W2-B would start
    assert len([c for c in calls(w) if c.startswith("launch")]) == 1
    assert status(w)["ready_waits"]["W2-B T-B"] == HELD and "land W2-A=abcdef1" in calls(w)
    server["m"] = "ok"
    etick(w, server, NOW + 400)  # answers again: the next pass may start
    etick(w, server, NOW + 600)
    assert any(c.startswith("launch") and "W2-B" in c for c in calls(w))


def test_embed_timeouts_count_to_hung_one_item_and_recovery_clears_it(w, server):
    conf(w, embed_timeout_s=0.5)
    server["m"] = "hang"
    etick(w, server, NOW)
    etick(w, server, NOW + 60)
    assert not items_with(w, "Server:") and status(w)["embedding_server"]["state"] == "failing"
    etick(w, server, NOW + 120)  # the third failure in a row
    etick(w, server, NOW + 180)
    hung = items_with(w, "Server:")
    assert len(hung) == 1 and "HUNG since" in hung[0] and "W2:" not in hung[0]
    assert (w.d / "inbox-stale.txt").read_text().startswith("server: the embedding server HUNG since")
    assert "embedding server: HUNG since" in (w.d / "status.txt").read_text()
    server["m"] = "ok"
    for i in (w.d / "inbox").glob("*.txt"):
        i.rename(w.d / "inbox" / (i.name + ".read"))
    etick(w, server, NOW + 240)
    assert not (w.d / "inbox-stale.txt").exists() and status(w)["embedding_server"]["state"] == "healthy"


def test_embed_no_restart_unless_configured(w, server):
    conf(w, embed_timeout_s=0.5, embed_hung_after=1, embed_restart_after_s=60)
    server["m"] = "hang"
    etick(w, server, NOW)
    etick(w, server, NOW + 2000)
    assert len(items_with(w, "Server:")) == 1 and "restart" not in calls(w)


def test_embed_a_configured_restart_waits_for_its_time_and_is_rate_limited(w, server):
    r = w.tmp / "restart.py"
    r.write_text(f"open({str(w.calls)!r}, 'a').write('restart\\n')\n")
    conf(w, embed_timeout_s=0.5, embed_hung_after=1, embed_restart_after_s=60,
         embed_restart_cmd=f"{sys.executable} {r}")
    server["m"] = "hang"
    for t in (NOW, NOW + 30, NOW + 90, NOW + 150, NOW + 1900):  # HUNG at NOW; 30 s: too soon; 150 s: within 30 min
        etick(w, server, t)
    assert calls(w).count("restart") == 2
    assert len([i for i in items_with(w, "Server:") if "restarted" in i]) == 2


def test_embed_checked_every_n_passes(w, server):
    conf(w, embed_check_every=2)
    for t in (NOW, NOW + 60, NOW + 120):
        etick(w, server, t)
    assert server["hits"] == 2


# ---- DEC-1015 item 2: the heavy-slot holders' progress ----------------------------------------------------------------

def fake_proc(w, pid, ppid, ticks, start=100, cmd="python3 -m pytest tests", cwd=None):
    d = w.tmp / "proc" / str(pid)
    d.mkdir(exist_ok=True)
    fields = ["S", str(ppid)] + ["0"] * 9 + [str(ticks), "0"] + ["0"] * 6 + [str(start)] + ["0"] * 5
    (d / "stat").write_text(f"{pid} (a name) " + " ".join(fields) + "\n")  # a space inside the name, as /proc allows
    (d / "cmdline").write_bytes(cmd.replace(" ", "\0").encode() + b"\0")
    if not (d / "cwd").is_symlink():
        (d / "cwd").symlink_to(cwd or (w.wt / "W2-A"))


def hold(w, slot=1, pid=500):
    p = w.tmp / "slots" / f"gov-os-heavy-slot-{slot}.lock"
    p.write_text("")
    ino = os.stat(p).st_ino
    with open(w.tmp / "proc" / "locks", "a") as f:
        f.write(f"1: FLOCK  ADVISORY  WRITE {pid} 08:30:{ino} 0 EOF\n")
        f.write(f"1: -> FLOCK  ADVISORY  WRITE 999 08:30:{ino} 0 EOF\n")  # a waiter, not a holder


def slot_tree(w, child_ticks):
    fake_proc(w, 500, 1, 5, cmd="flock /tmp/gov-os-heavy-slot-1.lock gov rebuild")
    fake_proc(w, 501, 500, child_ticks)


def test_slot_a_holder_whose_cpu_grows_raises_nothing(w):
    hold(w)
    for n, t in enumerate((NOW, NOW + 1000, NOW + 2000)):
        slot_tree(w, 10 + n * 10)
        tick(w, DISPATCH_NOW=t)
    assert not items_with(w, "Slot:")
    assert "heavy slot holders: slot 1 pid 500" in (w.d / "status.txt").read_text()


def test_slot_a_holder_idle_past_the_limit_is_one_item_not_repeated(w):
    hold(w)
    slot_tree(w, 10)
    for t in (NOW, NOW + 600, NOW + 1000, NOW + 1100):
        tick(w, DISPATCH_NOW=t)
    found = items_with(w, "Slot:")
    assert len(found) == 1
    assert all(x in found[0] for x in ("heavy slot 1", "pid 500", "gov rebuild", str(w.wt / "W2-A"), "IDLE", "16 min"))
    assert "slot 1 pid 500: IDLE since" in (w.d / "inbox-stale.txt").read_text()


def test_slot_cpu_growing_again_clears_the_idle_line(w):
    hold(w)
    slot_tree(w, 10)
    tick(w, DISPATCH_NOW=NOW)
    tick(w, DISPATCH_NOW=NOW + 1000)
    slot_tree(w, 11)
    tick(w, DISPATCH_NOW=NOW + 1060)
    assert "slot 1" not in ((w.d / "inbox-stale.txt").read_text() if (w.d / "inbox-stale.txt").exists() else "")


def test_slot_a_holder_ending_clears_it(w):
    hold(w)
    slot_tree(w, 10)
    tick(w, DISPATCH_NOW=NOW)
    tick(w, DISPATCH_NOW=NOW + 1000)
    (w.tmp / "proc" / "locks").write_text("")  # the holder ended
    for i in (w.d / "inbox").glob("*.txt"):
        i.rename(w.d / "inbox" / (i.name + ".read"))
    tick(w, DISPATCH_NOW=NOW + 1060)
    assert not (w.d / "inbox-stale.txt").exists() and status(w)["slot_holders"] == []
    assert "heavy slot holders: none" in (w.d / "status.txt").read_text()


def test_slot_an_idle_holder_while_the_server_is_hung_is_likely_waiting_on_it(w, server):
    conf(w, embed_timeout_s=0.5, embed_hung_after=1, slot_idle_s=60)
    server["m"] = "hang"
    hold(w)
    slot_tree(w, 10)
    etick(w, server, NOW)
    etick(w, server, NOW + 120)
    found = items_with(w, "Slot:")
    assert len(found) == 1 and "likely waiting on the embedding server" in found[0]


# ---- DEC-1018 item 1: no landing claimed before the nightly has started ------------------------------------------------

HELD_FOR_NIGHTLY = "held for the nightly (DEC-1018) until it starts"


def at(hh, mm):
    """NOW's day at a local time (the dispatcher runs in the same time zone as the test)."""
    return datetime.fromtimestamp(NOW).replace(hour=hh, minute=mm, second=0, microsecond=0).timestamp()


def nightly_running(w, mtime):
    m = w.orch / "NIGHTLY-RUNNING"
    m.write_text("nightly: running\n")
    os.utime(m, (mtime, mtime))


def test_nightly_hold_inside_the_window_claims_nothing(w):
    land_one(w)
    tick(w, DISPATCH_NOW=at(3, 30))
    assert calls(w) == [] and status(w)["land"] == HELD_FOR_NIGHTLY and (w.d / "land.txt").exists()


def test_nightly_hold_not_before_the_window(w):
    land_one(w)
    tick(w, DISPATCH_NOW=at(3, 14))
    assert calls(w) == ["land W2-A=abcdef1"]


def test_nightly_hold_does_not_hold_starts(w):
    tick(w, DISPATCH_NOW=at(3, 30))
    assert [c for c in calls(w) if c.startswith("launch")] and status(w)["land"] == HELD_FOR_NIGHTLY


def test_nightly_hold_released_by_nightly_running(w):
    land_one(w)
    nightly_running(w, at(4, 1))
    tick(w, DISPATCH_NOW=at(4, 10))
    assert calls(w) == ["land W2-A=abcdef1"]


def test_nightly_hold_released_by_a_status_line_for_today(w):
    land_one(w)
    nd = w.orch / "log" / "nightly"
    nd.mkdir(parents=True)
    today = datetime.fromtimestamp(NOW).strftime("%Y-%m-%d")
    (nd / "status.txt").write_text(f"{today} FAILED | nightly NOT STARTED: by the latest start, ...\n")
    tick(w, DISPATCH_NOW=at(4, 55))
    assert calls(w) == ["land W2-A=abcdef1"]


def test_nightly_hold_released_by_the_until_time(w):
    land_one(w)
    tick(w, DISPATCH_NOW=at(5, 30))
    assert calls(w) == ["land W2-A=abcdef1"]


def test_nightly_hold_a_stale_nightly_running_from_yesterday_does_not_release(w):
    land_one(w)
    nightly_running(w, at(4, 1) - 86400)
    nd = w.orch / "log" / "nightly"
    nd.mkdir(parents=True)
    yesterday = datetime.fromtimestamp(NOW - 86400).strftime("%Y-%m-%d")
    (nd / "status.txt").write_text(f"{yesterday} ran | verdict: green\n")  # yesterday's line does not release either
    tick(w, DISPATCH_NOW=at(4, 10))
    assert calls(w) == [] and status(w)["land"] == HELD_FOR_NIGHTLY


def test_nightly_hold_a_landing_in_flight_is_finalised_not_stopped(w):
    land_one(w)
    tick(w, DISPATCH_NOW=at(3, 10))  # claimed before the hold
    assert calls(w) == ["land W2-A=abcdef1"] and (w.d / "land-inflight.txt").exists()
    tick(w, DISPATCH_NOW=at(3, 20))
    assert not (w.d / "land-inflight.txt").exists() and "CLOSED" in (w.d / "land-done.txt").read_text()


def test_nightly_hold_times_are_configured(w):
    conf(w, nightly_hold_from="02:00", nightly_hold_until="02:30")
    land_one(w)
    tick(w, DISPATCH_NOW=at(2, 10))
    assert calls(w) == [] and status(w)["land"] == HELD_FOR_NIGHTLY
    tick(w, DISPATCH_NOW=at(3, 30))  # outside the configured window: the default window does not apply
    assert calls(w) == ["land W2-A=abcdef1"]
