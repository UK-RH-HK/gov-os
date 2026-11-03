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


OLD_HOOK = 'import os\n    slots = int(os.environ.get("GOV_RERANK_GPU_SLOTS", "2"))\n'  # the installed copy today
NEW_HOOK = 'def _slots():\n    pass  # reads limits.json\n'


def plant_hook(tmp, text):
    p = tmp / "hook" / "gov_reranker_gpu_slot.py"
    p.parent.mkdir(exist_ok=True)
    p.write_text(text)
    return p


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
               # DEC-1030, all planted: no nvidia-smi (unless a test plants one), the two servers' logs in the folder
               DISPATCH_NVIDIA_SMI=str(tmp_path / "nvidia-smi"), DISPATCH_GPU_LOG_SHARED=str(tmp_path / "serve-11434.log"),
               DISPATCH_GPU_LOG_QUERY=str(tmp_path / "serve-11435.log"),
               # DEC-1032, all planted: no ss (unless a test plants one), the rerankers' GPU lock files in the folder
               DISPATCH_SS=str(tmp_path / "ss"), DISPATCH_RERANK_GLOB=str(tmp_path / "rerank" / "gov-os-rerank-gpu-*.lock"),
               # DEC-1039 (1b), planted: no shared-GPU-memory reader (unless a test plants one)
               DISPATCH_GPU_SHARED_CMD=str(tmp_path / "shared-counter"),
               # review F2, planted: the installed reranker hook, today's copy (2 locks); a test may plant another
               DISPATCH_RERANK_HOOK=str(plant_hook(tmp_path, OLD_HOOK)),
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


def test_the_lead_cap_comes_from_memory_not_slots_times_k(wp):
    """DEC-1032: lead_cap = floor(room / a lead's p95), room = available + the leads' trees - the floor - the slot
    runs - the services' headroom; slots x K (6) no longer caps."""
    leads(wp, 6)  # 6 leads at 0.3 GB: the old rule (3 slots x K 2) refused a seventh whatever the memory
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    tick(wp)
    s = status(wp)
    # room: 60 GB + 6 x 0.3 GB - floor 3 GB - the embedding p95 headroom 600,000 kB; a lead (literal) 2,500,000 kB
    room = 60 * GB + 6 * 300_000 - 3 * GB - 600_000
    assert s["admit"] and f"of {room // 2_500_000} leads (cap from memory)" in s["admit_reason"]
    assert s["lead_cap"] == {"cap": room // 2_500_000, "room_kb": room, "p95_kb": 2_500_000}
    assert f"lead cap {room // 2_500_000} from memory" in (wp.d / "status.txt").read_text()
    assert calls(wp)[0].startswith("launch W2-A")
    leads(wp, 6)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {18 * GB} kB\n")  # room for 6 leads, not 7
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    tick(wp, DISPATCH_NOW=NOW + 300)
    s = status(wp)
    assert not s["admit"] and s["admit_reason"].startswith("memory: lead cap 6 (literal rule: ")
    assert "6 leads running and 0 launching" in s["admit_reason"] and calls(wp) == []


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
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {18 * GB} kB\n")  # DEC-1032: a lead cap of 6 from memory
    leads(wp, 5, extra=[{"cmd": "bash /x/dispatch/launch_now.sh W2-Q T-Q Q.md W2-Q-A5-run1.json", "cwd": "/"}])
    tick(wp)
    s = status(wp)
    assert s["pending_launches"] == ["W2-Q"] and not s["admit"] and "1 launching" in s["admit_reason"]


def test_f1_a_recent_start_without_a_process_counts_as_a_lead(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {60 * GB} kB\n")
    (wp.d / "started.txt").write_text(f"{datetime.fromtimestamp(NOW - 300):%Y-%m-%d %H:%M:%S} W2-Q Q.md W2-Q-A5-run1.json\n")
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {18 * GB} kB\n")  # DEC-1032: a lead cap of 6 from memory
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
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "literal", "cpu_margin": "two"}))  # K unused (DEC-1032)
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
SCRATCH_TOOLS = pytest.mark.skipif(not (TOOLS / "land.py").exists(),
                                   reason="the CTO's untracked scratch tools are not in this tree (a clean clone)")


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


@SCRATCH_TOOLS
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


@SCRATCH_TOOLS
@pytest.mark.parametrize("tool", ["land.py", "close_build.py"])
def test_f6_retry_exhaustion_fails_cleanly(tmp_path, tool):
    repo, lock = locked_repo(tmp_path)  # held throughout
    mod = load_tool(tool)
    t0 = time.time()
    r = mod.git_retry(["add", "--", "b.txt"], root=repo, tries=3, wait=0.2)
    assert r.returncode != 0 and "index.lock" in r.stderr and lock.exists()
    assert time.time() - t0 >= 0.4  # three tries, two waits; then it gives back, no exception
    assert "b.txt" not in git(repo, "diff", "--cached", "--name-only")


@SCRATCH_TOOLS
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
    conf(w, embed_check_every=1)  # the fallback test request every pass (DEC-1032's default: every 5)
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
    conf(w, embed_hung_after=1, embed_restart_after_s=60, embed_restart_cmd=f"{sys.executable} {r}", embed_check_every=1)
    (w.d / "ready.txt").write_text("")
    for t in (NOW, NOW + 30, NOW + 90, NOW + 150):
        tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    assert calls(w).count("restart") == 1


HELD = "embedding server hung: starts held (DEC-1015)"


@pytest.mark.parametrize("why", ["hung", "refused"])
def test_embed_starts_are_held_while_the_server_is_down_and_landings_are_not(w, server, why):
    conf(w, embed_timeout_s=0.5, embed_hung_after=1, embed_check_every=1)
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
    conf(w, embed_timeout_s=0.5, embed_check_every=1)
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
         embed_restart_cmd=f"{sys.executable} {r}", embed_check_every=1)
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


# ---- DEC-1030: the GPU, its holders and each embedding model's layers ---------------------------------------------------

GPU_OK = "NVIDIA GeForce RTX 5070 Ti, 3584, 16303, 5"
LOADED = "load_tensors: offloaded 29/29 layers to GPU\n"
ON_CPU = "load_tensors: offloaded 0/29 layers to GPU\n"
CUDA = "CUDA error: unknown error\n"


def smi(w, gpu=GPU_OK, apps="", rc=0):
    """A stand-in nvidia-smi: answers each query from planted text, counts its calls."""
    exe = w.tmp / "nvidia-smi"
    (w.tmp / "smi-gpu.txt").write_text(gpu + "\n")
    (w.tmp / "smi-apps.txt").write_text(apps)
    exe.write_text(f"#!{sys.executable}\nimport sys\nopen({str(w.tmp / 'smi-calls.txt')!r}, 'a').write(sys.argv[1] + '\\n')\n"
                   f"if {rc}:\n    print('NVIDIA-SMI has failed', file=sys.stderr); sys.exit({rc})\n"
                   f"q = 'gpu' if sys.argv[1].startswith('--query-gpu') else 'apps'\n"
                   f"sys.stdout.write(open({str(w.tmp)!r} + '/smi-' + q + '.txt').read())\n")
    exe.chmod(0o755)


def smi_calls(w):
    p = w.tmp / "smi-calls.txt"
    return p.read_text().splitlines() if p.exists() else []


def glog(w, server, text, mode="a"):
    with open(w.tmp / ("serve-11434.log" if server == "shared" else "serve-11435.log"), mode) as f:
        f.write(text)


def gpu_items(w):
    return sorted((w.d / "inbox").glob("*-gpu-alert*.txt"))


def gpu_status(w):
    return next(l for l in (w.d / "status.txt").read_text().splitlines() if l.startswith("GPU: "))


def test_gpu_the_state_line_from_a_normal_nvidia_smi(w):
    smi(w)
    glog(w, "shared", "time=x level=INFO msg=start\n" + LOADED)
    r = tick(w)
    assert r.returncode == 0 and status(w)["failures"] == []
    assert gpu_status(w) == ("GPU: RTX 5070 Ti 3.5/15.9 GB, 5 %; holders: embedder shared (0), reranker (0); "
                             "layers: shared 29/29, query cpu-only by design")
    assert len(smi_calls(w)) == 2 and gpu_items(w) == []  # one read a pass (two queries); a first pass alerts nothing
    assert status(w)["gpu"]["state"]["total_mib"] == 16303


def test_gpu_wsl_na_memory_keeps_the_pid(w):
    fake_proc(w, 4242, 1, 0, cmd="/home/u/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Qwen/Qwen3-Reranker-0.6B")
    smi(w, apps="4242, [Not Found], [N/A]\n")
    tick(w)
    h = status(w)["gpu"]["state"]["holders"]
    assert h == [{"pid": 4242, "name": "[Not Found]", "mib": None, "kind": "reranker"}]
    assert "reranker (1)" in gpu_status(w)


@pytest.mark.parametrize("how", ["missing", "failing"])
def test_gpu_an_unreadable_nvidia_smi_is_a_status_line_not_a_failure(w, how):
    if how == "failing":
        smi(w, rc=9)
    glog(w, "shared", LOADED)
    r = tick(w)
    assert r.returncode == 0 and status(w)["failures"] == []
    line = gpu_status(w)
    assert line.startswith("GPU: unreadable (") and "layers: shared 29/29" in line
    assert ("exit 9" in line) if how == "failing" else ("nvidia-smi" in line)
    assert (w.d / "status.txt").read_text().startswith("dispatcher ") and gpu_items(w) == []


def test_gpu_a_cuda_error_is_one_item_at_once_and_not_again(w):
    (w.d / "ready.txt").write_text("")  # no lead starts: the inbox holds only the GPU's items
    # 13,000 MiB: within the budget (16,303 - 2,048); above it is a gpu-alert of its own (DEC-1039 (1b))
    smi(w, gpu="NVIDIA GeForce RTX 5070 Ti, 13000, 16303, 99")
    glog(w, "shared", LOADED + "an old " + CUDA)  # history before the first pass: not alerted
    tick(w)
    assert gpu_items(w) == []
    glog(w, "shared", "ggml_cuda_compute_forward: x\n" + CUDA + "/build/ggml-cuda.cu:108: CUDA error\n")
    tick(w, DISPATCH_NOW=NOW + 60)
    items = gpu_items(w)
    assert len(items) == 1 and items[0].name.endswith("-gpu-alert.txt") and not items[0].name.endswith("-server-hung.txt")
    body = items[0].read_text().splitlines()
    assert body[0] == "log: serve-11434.log" and body[1] == "GPU: CUDA error (shared)" and body[2].startswith("status: ")
    text = items[0].read_text()
    assert "shared: CUDA error: unknown error" in text and "12.7/15.9 GB, 99 %" in text and "W2:" not in text
    assert "holders:" in text and "layers: shared 29/29" in text
    assert (w.d / "inbox-stale.txt").read_text().startswith("gpu: the GPU CUDA error (shared) since ")
    tick(w, DISPATCH_NOW=NOW + 120)  # no new line: not again
    assert len(gpu_items(w)) == 1 and "last alert " in gpu_status(w)
    items[0].rename(w.d / "inbox" / (items[0].name + ".read"))  # read: the stale line clears
    tick(w, DISPATCH_NOW=NOW + 180)
    assert not (w.d / "inbox-stale.txt").exists()
    glog(w, "shared", CUDA)  # a second crash minutes later: every crash alerts (DEC-1030; review F3)
    tick(w, DISPATCH_NOW=NOW + 240)
    assert len(gpu_items(w)) == 1 and len(list((w.d / "inbox").glob("*.txt"))) == 1


def test_gpu_an_empty_nvidia_smi_answer_still_reads_the_logs(w):
    """Review F1: nvidia-smi answering nothing (exit 0) must not stop the logs being read."""
    (w.d / "ready.txt").write_text("")
    smi(w, gpu="")
    glog(w, "shared", LOADED)
    tick(w)
    glog(w, "shared", CUDA)
    r = tick(w, DISPATCH_NOW=NOW + 60)
    assert r.returncode == 0 and status(w)["failures"] == []
    assert len(gpu_items(w)) == 1 and gpu_status(w).startswith("GPU: unreadable (")


def test_gpu_an_unreadable_state_file_still_counts_new_errors(w):
    """Review F2: a damaged gpu-health.json re-reads the recent log with its errors counted (an extra alert at
    worst, never a missed one); the state is written whole (a rename)."""
    (w.d / "ready.txt").write_text("")
    smi(w)
    glog(w, "shared", LOADED)
    tick(w)
    assert json.loads((w.d / "gpu-health.json").read_text())["offsets"]
    (w.d / "gpu-health.json").write_text("{not json")
    glog(w, "shared", CUDA)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert len(gpu_items(w)) == 1
    assert json.loads((w.d / "gpu-health.json").read_text())["offsets"] and not (w.d / "gpu-health.json.tmp").exists()


def test_gpu_a_zero_layer_load_on_the_shared_server_is_one_item(w):
    smi(w)
    glog(w, "shared", LOADED)
    tick(w)
    glog(w, "shared", "load_tensors: offloading 0 repeating layers to GPU\n" + ON_CPU)
    tick(w, DISPATCH_NOW=NOW + 60)
    items = gpu_items(w)
    assert len(items) == 1 and "GPU: 0 layers (shared)" in items[0].read_text()
    assert "offloaded 0/29 layers to GPU" in items[0].read_text() and "layers: shared 0/29" in gpu_status(w)
    glog(w, "shared", ON_CPU)  # loaded on the CPU again: the same incident
    items[0].rename(w.d / "inbox" / (items[0].name + ".read"))
    tick(w, DISPATCH_NOW=NOW + 120)
    assert gpu_items(w) == [] and (w.d / "inbox-stale.txt").read_text().startswith("gpu: ")  # held while on the CPU
    glog(w, "shared", LOADED)  # back on the GPU: cleared
    tick(w, DISPATCH_NOW=NOW + 180)
    assert not (w.d / "inbox-stale.txt").exists() and "layers: shared 29/29" in gpu_status(w)
    glog(w, "shared", ON_CPU)  # a new incident
    tick(w, DISPATCH_NOW=NOW + 240)
    assert len(gpu_items(w)) == 1


def test_gpu_a_zero_layer_load_already_current_at_the_first_pass_alerts(w):
    smi(w)
    glog(w, "shared", LOADED + ON_CPU)
    tick(w)
    assert len(gpu_items(w)) == 1
    tick(w, DISPATCH_NOW=NOW + 60)
    assert len(gpu_items(w)) == 1


def test_gpu_a_zero_layer_load_on_the_query_server_is_by_design(w):
    smi(w)
    glog(w, "query", "time=x msg=start\n")
    tick(w)
    glog(w, "query", ON_CPU)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert gpu_items(w) == [] and "query cpu-only by design" in gpu_status(w)
    conf(w, gpu_expected={"query": True})  # configurable: then it is an alert (and the shared default is kept)
    glog(w, "query", ON_CPU)
    tick(w, DISPATCH_NOW=NOW + 120)
    assert len(gpu_items(w)) == 1 and "0 layers (query)" in gpu_items(w)[0].read_text()


def test_gpu_offsets_survive_a_truncated_log(w):
    smi(w)
    glog(w, "shared", LOADED + "x" * 200 + "\n" * 50)
    tick(w)
    off = json.loads((w.d / "gpu-health.json").read_text())["offsets"]["shared"]["off"]
    assert off == (w.tmp / "serve-11434.log").stat().st_size
    glog(w, "shared", CUDA, mode="w")  # truncated (a restart's `>`): shorter than the offset
    r = tick(w, DISPATCH_NOW=NOW + 60)
    assert r.returncode == 0 and status(w)["failures"] == [] and len(gpu_items(w)) == 1
    assert json.loads((w.d / "gpu-health.json").read_text())["offsets"]["shared"]["off"] == len(CUDA)


def test_gpu_a_partial_last_line_waits_for_the_next_pass(w):
    smi(w)
    glog(w, "shared", LOADED)
    tick(w)
    glog(w, "shared", "CUDA err")  # being written
    tick(w, DISPATCH_NOW=NOW + 60)
    assert gpu_items(w) == []
    glog(w, "shared", "or: unknown error\n")
    tick(w, DISPATCH_NOW=NOW + 120)
    assert len(gpu_items(w)) == 1 and "CUDA error: unknown error" in gpu_items(w)[0].read_text()


def environ(w, pid, **env):
    (w.tmp / "proc" / str(pid) / "environ").write_bytes(b"".join(f"{k}={v}".encode() + b"\0" for k, v in env.items()))


def test_gpu_holders_are_classified_by_command_line_and_parents(w):
    serve, llama = "/home/u/.local/ollama/bin/ollama serve", "/home/u/.local/ollama/lib/ollama/llama-server --model m"
    fake_proc(w, 300, 1, 0, cmd=serve)
    environ(w, 300, HOME="/home/u", SECRET_TOKEN="x")  # no OLLAMA_HOST: the shared server
    fake_proc(w, 301, 300, 0, cmd=llama)
    fake_proc(w, 310, 1, 0, cmd=serve)
    environ(w, 310, OLLAMA_HOST="127.0.0.1:11435", CUDA_VISIBLE_DEVICES="-1")
    fake_proc(w, 311, 310, 0, cmd=llama)
    fake_proc(w, 320, 1, 0, cmd=serve)
    environ(w, 320, OLLAMA_HOST="127.0.0.1:11447")  # a private test server
    fake_proc(w, 321, 320, 0, cmd=llama)
    fake_proc(w, 330, 1, 0, cmd="/v/bin/python -m gov.retrieval.rerank_worker Qwen/Qwen3-Reranker-0.6B")
    fake_proc(w, 340, 1, 0, cmd="/usr/bin/python3 train.py")
    apps = "".join(f"{p}, x, {m}\n" for p, m in ((301, "1200 MiB"), (311, "[N/A]"), (321, "300 MiB"), (330, "[N/A]"),
                                                 (340, "10 MiB"), (999, "[N/A]")))
    smi(w, apps=apps)
    tick(w)
    kinds = {h["pid"]: h["kind"] for h in status(w)["gpu"]["state"]["holders"]}
    assert kinds == {301: "embedder shared", 311: "embedder query", 321: "embedder other", 330: "reranker",
                     340: "other", 999: "other"}
    assert ("holders: embedder shared (1), embedder query (1), embedder other (1), reranker (1), other (2)"
            in gpu_status(w))
    assert "SECRET" not in (w.d / "gpu-health.json").read_text() + (w.d / "status.json").read_text()


def test_gpu_checked_every_n_passes(w):
    smi(w)
    conf(w, gpu_check_every=2)
    for t in (NOW, NOW + 60, NOW + 120):
        tick(w, DISPATCH_NOW=t)
    assert len(smi_calls(w)) == 4  # passes 1 and 3, two queries each


def test_gpu_a_dry_pass_reads_nothing(w):
    smi(w)
    glog(w, "shared", LOADED)
    tick(w, "--dry")
    assert smi_calls(w) == [] and not (w.d / "gpu-health.json").exists()


# ---- DEC-1032: the whole machine balanced by measured peaks --------------------------------------------------------------

TASKS = ("slot launch_slot_: id  0 | task 7 | processing task, is_child = 0\n"
         "slot      release: id  0 | task 7 | stop processing: n_tokens = 129, truncated = 0\n"
         "srv  update_slots: all slots are idle\n")
GIN = '[GIN] 2026/11/02 - 12:45:47 | 200 |  1.414239796s |       127.0.0.1 | POST     "/api/embed"\n'


def sock_listen(port=11434):
    return f"LISTEN    0      4096   127.0.0.1:{port}   0.0.0.0:*\n\t cubic cwnd:10\n"


def sock_waiting(port=11434, age_ms=100_000, local=34494):
    """A client socket whose request has had no answer yet (no byte received)."""
    return (f"ESTAB     0      0      127.0.0.1:{local} 127.0.0.1:{port}\n\t cubic wscale:10,10 rto:204 "
            f"rtt:0.042/0.027 bytes_sent:6698 bytes_acked:6699 segs_out:4 lastsnd:{age_ms} lastrcv:{age_ms} lastack:4\n")


def sock_idle(port=11434, local=34500):
    """An idle keep-alive connection: its answer arrived after its last send."""
    return (f"ESTAB     0      0      127.0.0.1:{local} 127.0.0.1:{port}\n\t cubic bytes_sent:500 bytes_acked:501 "
            "bytes_received:9000 lastsnd:90000 lastrcv:89990 lastack:89990\n")


def plant_ss(w, *socks):
    """A stand-in ss: prints the planted sockets (ss -Htnia's form), whatever its arguments."""
    exe = w.tmp / "ss"
    (w.tmp / "ss.txt").write_text("".join(socks))
    exe.write_text(f"#!{sys.executable}\nimport sys\nsys.stdout.write(open({str(w.tmp / 'ss.txt')!r}).read())\n")
    exe.chmod(0o755)


def ptick(w, server, t, **env):
    """One pass with the planted server as the fallback's target (its hits count the test requests)."""
    return tick(w, DISPATCH_EMBED_URL=server["url"], DISPATCH_NOW=t, **env)


def server_stale(w):
    """The inbox-stale lines of the servers' causes (an inbox line keeps its first wording, which may name an item)."""
    text = (w.d / "inbox-stale.txt").read_text() if (w.d / "inbox-stale.txt").exists() else ""
    return [l for l in text.splitlines() if l.startswith("server")]


def emb_shared(w):
    return json.loads((w.d / "embed-health.json").read_text())["servers"]["shared"]


def test_progress_a_busy_runner_with_slow_requests_is_never_hung(w, server):
    """Requests wait 150 s each (the CPU fallback's slow requests), but tasks complete every pass: BUSY, never HUNG,
    no item, starts not held, and no test request is sent (the log is readable)."""
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen(), sock_waiting(age_ms=150_000), sock_waiting(age_ms=40_000, local=34495))
    ptick(w, server, NOW)
    for n in range(1, 11):  # ten minutes, far past embed_stall_s (180 s)
        glog(w, "shared", TASKS * 3 + GIN)
        ptick(w, server, NOW + 60 * n)
        sv = emb_shared(w)
        assert sv["state"] == "BUSY" and sv["tasks_per_min"] == 3 and sv["waiting"] == 2
    assert not items_with(w, "Server:") and server["hits"] == 0
    assert status(w)["embedding_server"]["state"] == "BUSY" and status(w)["embedding_server"]["how"] == "progress"
    text = (w.d / "status.txt").read_text()
    assert "embedding server: shared BUSY 3 tasks/min (2 waiting, the oldest 150.0 s)" in text
    assert "embedders: shared BUSY 3 tasks/min" in next(l for l in text.splitlines() if l.startswith("Balance: "))
    assert server_stale(w) == []
    assert len([c for c in calls(w) if c.startswith("launch")]) == 2  # W2-A, then W2-B: never held


def test_progress_waiting_requests_and_no_task_for_the_stall_time_is_hung_once(w, server):
    glog(w, "shared", LOADED + TASKS)
    plant_ss(w, sock_listen(), sock_waiting(age_ms=5_000))
    ptick(w, server, NOW)  # the first read: the stall is measured from here
    for t in (NOW + 60, NOW + 120):
        ptick(w, server, t)
        assert emb_shared(w)["state"] == "WAITING" and not items_with(w, "Server:")
    ptick(w, server, NOW + 180)  # embed_stall_s with requests waiting and no task: HUNG
    hung = items_with(w, "Server:")
    assert len(hung) == 1 and "HUNG since" in hung[0] and "1 request(s) waiting on port 11434" in hung[0]
    assert "no task completed for 180 s" in hung[0] and "W2:" not in hung[0]
    assert (w.d / "inbox-stale.txt").read_text().startswith("server: the embedding server HUNG since")
    ptick(w, server, NOW + 240)
    assert len(items_with(w, "Server:")) == 1  # once per incident
    assert status(w)["ready_waits"]["W2-B T-B"] == HELD and server["hits"] == 0
    assert "embedding server: shared HUNG since" in (w.d / "status.txt").read_text()
    for i in (w.d / "inbox").glob("*.txt"):
        i.rename(w.d / "inbox" / (i.name + ".read"))
    glog(w, "shared", TASKS)  # progress again: cleared
    ptick(w, server, NOW + 300)
    assert emb_shared(w)["state"] == "BUSY" and server_stale(w) == []
    ptick(w, server, NOW + 420)
    assert any(c.startswith("launch") and "W2-B" in c for c in calls(w))


def test_progress_nothing_waiting_is_idle_never_hung(w, server):
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen(), sock_idle())  # a keep-alive connection, its answer received: not waiting
    for n in range(0, 12):
        ptick(w, server, NOW + 60 * n)
    sv = emb_shared(w)
    assert sv["state"] == "IDLE" and sv["waiting"] == 0 and sv["quiet_s"] == 660
    assert not items_with(w, "Server:") and server["hits"] == 0


def test_progress_nothing_listening_is_not_running_once(w, server):
    (w.d / "ready.txt").write_text("")
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen(11435))  # the query server listens; nothing on 11434
    for n in range(4):
        ptick(w, server, NOW + 60 * n)
    down = items_with(w, "Server:")
    assert len(down) == 1 and "NOT RUNNING since" in down[0] and "nothing listens on port 11434" in down[0]
    assert emb_shared(w)["state"] == "NOT RUNNING"


def test_progress_the_query_server_hung_is_its_own_item_and_line_and_holds_no_start(w, server):
    glog(w, "shared", LOADED)
    glog(w, "query", "time=x msg=start\n")
    plant_ss(w, sock_listen(), sock_listen(11435), sock_waiting(11435, age_ms=200_000))
    for n in range(4):
        glog(w, "shared", TASKS)
        ptick(w, server, NOW + 60 * n)
    hung = items_with(w, "Server:")
    assert len(hung) == 1 and "Server: the query embedding server" in hung[0] and "starts are not held" in hung[0]
    assert "-server-query-hung" in next(i.name for i in (w.d / "inbox").glob("*.txt") if "Server:" in i.read_text())
    assert "server query: the query embedding server HUNG since" in (w.d / "inbox-stale.txt").read_text()
    assert status(w)["embedding_server"]["state"] == "BUSY"  # the shared server's: starts not held
    assert HELD not in status(w)["ready_waits"].values() and [c for c in calls(w) if c.startswith("launch")]


def test_progress_an_unreadable_log_falls_back_to_the_test_request_every_5_passes(w, server):
    plant_ss(w, sock_listen())  # no log planted: progress cannot be judged
    for n in range(6):
        ptick(w, server, NOW + 60 * n)
    assert server["hits"] == 2  # passes 1 and 6
    assert status(w)["embedding_server"]["how"] == "probe" and status(w)["embedding_server"]["state"] == "healthy"
    glog(w, "shared", LOADED)  # the log readable again: by progress, no more test requests
    for n in range(6, 12):
        ptick(w, server, NOW + 60 * n)
    assert server["hits"] == 2 and status(w)["embedding_server"]["how"] == "progress"


def gpu_used(w, used_mib):
    smi(w, gpu=f"NVIDIA GeForce RTX 5070 Ti, {used_mib}, 16303, 5")


def hold_rerank_gpu(w, *slots):
    d = w.tmp / "rerank"
    d.mkdir(exist_ok=True)
    with open(w.tmp / "proc" / "locks", "a") as f:
        for i in slots:
            p = d / f"gov-os-rerank-gpu-{i}.lock"
            p.write_text("")
            f.write(f"1: FLOCK  ADVISORY  WRITE {4000 + i} 08:30:{os.stat(p).st_ino} 0 EOF\n")


def own_max_history(wp, tid, kb):
    lines = (wp.orch / "log" / "lead-mem.jsonl").read_text().splitlines()
    r = json.loads(lines[0])
    r["leads_kb"][tid] = kb
    lines[0] = json.dumps(r)
    (wp.orch / "log" / "lead-mem.jsonl").write_text("\n".join(lines) + "\n")


@pytest.mark.parametrize("short", ["cpu", "ram", "gpu", "lead cap"])
def test_admission_refuses_for_each_short_resource_naming_it(wp, short):
    """DEC-1032: a newcomer starts only with room on every resource; each refusal names the one that is short."""
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    if short == "ram":  # the running lead once used 20 GB: the cap fits, its own max does not
        own_max_history(wp, "T-L0", 20 * GB)
    gpu_used(wp, 12000 if short == "gpu" else 3584)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")  # the first pass reads the GPU; nothing starts (no peaks yet)
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    leads(wp, 1)
    if short == "lead cap":
        (wp.tmp / "meminfo").write_text(f"MemAvailable: {5 * GB} kB\n")
    if short == "cpu":
        cpu_prev(wp, busy=1000, total=10000)
        (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2900, idle=9100, iowait=0))
    tick(wp, minute=short != "cpu", DISPATCH_NOW=NOW + 60)
    s = status(wp)
    want = {"cpu": "real CPU: 19.0 busy cores", "ram": "memory: available + leads'",
            "gpu": "GPU memory: 4303 MiB free < 5632 MiB (a reranker's 3584 MiB (a GPU reranker slot free: 0 of 2 held)"
                   " + headroom 2048 MiB)", "lead cap": "memory: lead cap 0 (literal rule: "}[short]
    assert not s["admit"] and s["admit_reason"].startswith(want), s["admit_reason"]
    assert all(r.startswith("not admitted: " + want[:20]) for r in s["ready_waits"].values()) and calls(wp) == []


def test_admission_gpu_need_is_only_the_headroom_when_both_reranker_gpu_slots_are_held(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 12000)  # 4303 MiB free: a reranker's share would not fit, the headroom does
    hold_rerank_gpu(wp, 0, 1)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")
    tick(wp, DISPATCH_NOW=NOW + 60)
    s = status(wp)
    assert s["admit"] and "GPU memory 4303 MiB free >= 2048 MiB" in s["admit_reason"]
    assert s["rerankers"]["gpu_held"] == 2 and calls(wp)[0].startswith("launch W2-A")


def test_admission_a_gpu_read_older_than_its_limit_is_not_judged(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 16000)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")
    conf(wp, memory_rule="literal", gpu_check_every=100)  # no new read: the last is 400 s old at the next pass
    tick(wp, DISPATCH_NOW=NOW + 400)
    s = status(wp)
    assert s["admit"] and "GPU memory: not judged" in s["admit_reason"]


def test_slots_follow_the_shared_embedders_device(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "slots"}))
    mixed_history(wp)
    (wp.d / "ready.txt").write_text("")
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    smi(wp)
    glog(wp, "shared", LOADED)

    def target(t):
        tick(wp, DISPATCH_NOW=t)
        return status(wp)["slots_target"], status(wp)["admit_reason"], (wp.d / "status.txt").read_text()
    target(NOW)  # the first pass reads the layers
    n, why, text = target(NOW + 60)
    assert n == 3 and "+ 3 slot runs at" in why and "slots 3 by device (gpu 29/29)" in text
    glog(wp, "shared", "load_tensors: offloaded 20/29 layers to GPU\n")
    target(NOW + 120)
    n, why, text = target(NOW + 180)
    assert n == 2 and "+ 2 slot runs at" in why and "slots 2 by device (partial 20/29)" in text
    glog(wp, "shared", ON_CPU)
    target(NOW + 240)
    assert target(NOW + 300)[0] == 2 and "slots 2 by device (cpu 0/29)" in target(NOW + 360)[2]
    conf(wp, memory_rule="slots", slots_gpu=4, slots_cpu=1)  # configured
    glog(wp, "shared", LOADED)
    target(NOW + 420)
    assert target(NOW + 480)[0] == 4


def test_slots_never_count_fewer_than_the_slots_held(wp):
    (wp.d / "config.json").write_text(json.dumps({"memory_rule": "slots"}))
    mixed_history(wp)
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    smi(wp)
    glog(wp, "shared", ON_CPU)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")
    wp.held.write_text(json.dumps(["/tmp/gov-os-heavy-slot-1.lock", "/tmp/gov-os-heavy-slot-2.lock",
                                   "/tmp/gov-os-heavy-slot-3.lock"]))
    tick(wp, DISPATCH_NOW=NOW + 60)
    assert status(wp)["slots_target"] == 2 and "+ 3 slot runs at" in status(wp)["admit_reason"]


def test_gpu_a_partial_load_is_one_alert_per_incident(w):
    smi(w)
    glog(w, "shared", LOADED)
    tick(w)
    glog(w, "shared", "load_tensors: offloaded 20/29 layers to GPU\n")
    tick(w, DISPATCH_NOW=NOW + 60)
    items = gpu_items(w)
    assert len(items) == 1 and "GPU: partial 20/29 layers (shared)" in items[0].read_text()
    assert "only 20/29 layers on the GPU" in items[0].read_text() and "offloaded 20/29 layers" in items[0].read_text()
    glog(w, "shared", "load_tensors: offloaded 18/29 layers to GPU\n")  # still short: the same incident
    items[0].rename(w.d / "inbox" / (items[0].name + ".read"))
    tick(w, DISPATCH_NOW=NOW + 120)
    assert gpu_items(w) == [] and (w.d / "inbox-stale.txt").read_text().startswith("gpu: ")
    glog(w, "shared", LOADED)  # all layers again: cleared
    tick(w, DISPATCH_NOW=NOW + 180)
    assert not (w.d / "inbox-stale.txt").exists()
    glog(w, "shared", "load_tensors: offloaded 1/29 layers to GPU\n")  # a new incident
    tick(w, DISPATCH_NOW=NOW + 240)
    assert len(gpu_items(w)) == 1


def test_gpu_a_partial_load_already_current_at_the_first_pass_alerts(w):
    smi(w)
    glog(w, "shared", "load_tensors: offloaded 27/29 layers to GPU\n")
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert len(gpu_items(w)) == 1 and "partial 27/29 layers (shared)" in gpu_items(w)[0].read_text()


def test_gpu_the_query_server_expected_on_the_gpu_alerts_on_0_and_partial_loads(w):
    smi(w)
    conf(w, gpu_expected={"query": True})  # the CTO's switch after the query server moves to the GPU
    glog(w, "query", ON_CPU)
    tick(w)
    assert len(gpu_items(w)) == 1 and "0 layers (query)" in gpu_items(w)[0].read_text()
    glog(w, "query", LOADED + "load_tensors: offloaded 10/29 layers to GPU\n")
    gpu_items(w)[0].rename(w.d / "inbox" / "read-1.txt.read")
    tick(w, DISPATCH_NOW=NOW + 60)
    assert len(gpu_items(w)) == 1 and "partial 10/29 layers (query)" in gpu_items(w)[0].read_text()
    conf(w)  # the default: CPU-only by design, a partial load is no alert either
    glog(w, "query", LOADED + "load_tensors: offloaded 10/29 layers to GPU\n")
    gpu_items(w)[0].rename(w.d / "inbox" / "read-2.txt.read")
    tick(w, DISPATCH_NOW=NOW + 120)
    assert gpu_items(w) == []


def test_balance_line_shows_every_resource_and_the_rerankers(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    smi(wp, gpu="NVIDIA GeForce RTX 5070 Ti, 7168, 16303, 30", apps="4001, x, [N/A]\n")
    fake_proc(wp, 4001, 1, 0, cmd="/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Qwen/Q")
    glog(wp, "shared", LOADED + TASKS)
    plant_ss(wp, sock_listen(), sock_listen(11435))
    hold_rerank_gpu(wp, 0)
    rr = [{"cmd": "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Qwen/Q", "cwd": "/",
           "pid": 4000 + i, "ppid": 100 if i == 0 else 1, "rss_kb": GB} for i in range(3)]
    leads(wp, 1, extra=rr)
    cpu_prev(wp, busy=1000, total=10000)
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2600, idle=9400, iowait=0))  # 16 busy cores
    tick(wp, minute=False)
    tick(wp, DISPATCH_NOW=NOW + 60)
    line = next(l for l in (wp.d / "status.txt").read_text().splitlines() if l.startswith("Balance: "))
    for part in ("CPU ", "/20 busy (band 14-18: ", "RAM 16.0 GB available (floor 3.0 GB)",
                 "GPU 7.0/15.9 GB used, 8.9 free (headroom 2.0 GB; embedders' layers: shared 29/29; holders: reranker 1)",
                 "embedders: shared IDLE", "slots 3 by device (gpu 29/29)", "lead cap ", " from memory (",
                 "rerankers 3 (3.0 GB RSS; 1 of 2 GPU slots held; reserve "):
        assert part in line, (part, line)
    b = status(wp)["balance"]
    assert b["rerankers"]["n"] == 3 and b["rerankers"]["outside_kb"] == 2 * GB and b["slots_target"] == 3
    assert b["gpu"]["free_mib"] == 16303 - 7168 and b["lead_cap"]["cap"] >= 1


def test_balance_the_cpu_band(w):
    for busy, band in ((1200, "below"), (2600, "within"), (2900, "above")):  # 2, 16 and 19 cores of 20
        cpu_prev(w, busy=1000, total=10000)
        (w.tmp / "procstat").write_text(PROCSTAT.format(busy=busy, idle=12000 - busy, iowait=0))
        tick(w, minute=False)
        assert status(w)["balance"]["cpu_in_band"] == band


# ---- the review of v4.6 (F1 to F4) --------------------------------------------------------------------------------------

def gin(code):
    return f'[GIN] 2026/11/02 - 12:45:47 | {code} |  1.0s |       127.0.0.1 | POST     "/api/embed"\n'


def test_review46_f1_a_first_request_after_an_idle_spell_is_not_hung_its_wait_is_timed(w, server):
    """The stall clock starts when the wait starts, never at the last task: idle 10 minutes, then a request caught in
    flight (sent 0.4 s ago) is WAITING; HUNG only once it has waited embed_stall_s with no task done."""
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen())
    for n in range(11):  # 10 idle minutes: no task, nothing waiting
        ptick(w, server, NOW + 60 * n)
    assert emb_shared(w)["state"] == "IDLE" and emb_shared(w)["quiet_s"] == 600
    plant_ss(w, sock_listen(), sock_waiting(age_ms=400))
    ptick(w, server, NOW + 660)
    assert emb_shared(w)["state"] == "WAITING" and not items_with(w, "Server:")
    for t in (NOW + 720, NOW + 780):  # the same wait goes on, under 180 s
        ptick(w, server, t)
        assert emb_shared(w)["state"] == "WAITING" and not items_with(w, "Server:")
    ptick(w, server, NOW + 840)  # 180.4 s of waiting with no task: HUNG, since the wait began
    hung = items_with(w, "Server:")
    assert len(hung) == 1 and f"HUNG since {datetime.fromtimestamp(NOW + 659.6):%Y-%m-%d %H:%M:%S}" in hung[0]
    plant_ss(w, sock_listen(), sock_waiting(age_ms=150_000))  # a request found already waiting 150 s: timed from its send
    glog(w, "shared", TASKS)
    ptick(w, server, NOW + 900)  # progress: cleared
    ptick(w, server, NOW + 960)
    assert emb_shared(w)["state"] == "WAITING" and emb_shared(w)["stalled_s"] == 60  # since the last task, not 150 s


def test_review46_f2_failed_requests_are_not_progress_and_a_run_of_them_is_failing(w, server):
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen())
    rtick = lambda t: tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)  # the fallback test request fails too
    rtick(NOW)
    glog(w, "shared", gin(500) + gin(200) + gin(499) + gin(500) + gin(500))  # a 2xx breaks the run; a 499 is the
    rtick(NOW + 60)                                                          # client's: 2 in a row, not failing
    assert emb_shared(w)["state"] == "BUSY" and emb_shared(w)["fails_in_a_row"] == 2
    glog(w, "shared", gin(500))  # the third failure in a row, no success: FAILING
    rtick(NOW + 120)
    sv = emb_shared(w)
    assert sv["state"] == "FAILING" and sv["requests_per_min"] == 0 and sv["failed_per_min"] == 1
    failing = items_with(w, "Server:")
    assert len(failing) == 1 and "FAILING since" in failing[0] and "3 requests in a row failed" in failing[0]
    assert "the last with status 500" in failing[0] and "starts are held" in failing[0]
    assert (w.d / "inbox-stale.txt").read_text().startswith("server: the embedding server FAILING since")
    glog(w, "shared", gin(500) * 4)
    rtick(NOW + 180)  # starts held, once per incident
    assert len(items_with(w, "Server:")) == 1 and status(w)["ready_waits"]["W2-B T-B"] == HELD
    glog(w, "shared", gin(200))
    rtick(NOW + 240)
    assert emb_shared(w)["state"] == "BUSY" and server_stale(w) == []


def test_review46_f2_a_5xx_line_never_clears_a_hang(w, server):
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen(), sock_waiting(age_ms=5_000))
    for t in (NOW, NOW + 60, NOW + 120, NOW + 180):
        ptick(w, server, t)
    assert emb_shared(w)["state"] == "HUNG" and len(items_with(w, "Server:")) == 1
    glog(w, "shared", gin(500))  # a failed request: not progress (v4.6 counted it and cleared the hang)
    ptick(w, server, NOW + 240)
    sv = emb_shared(w)
    assert sv["state"] == "HUNG" and sv["hung_since"] == NOW and sv["requests_per_min"] == 0
    assert len(items_with(w, "Server:")) == 1 and server_stale(w)


def test_review46_f3_a_connection_that_sent_nothing_is_not_waiting(w, server):
    glog(w, "shared", LOADED)
    never_used = ("ESTAB     0      0      127.0.0.1:34600 127.0.0.1:11434\n\t cubic wscale:10,10 rto:204 rtt:0.03/0.01 "
                  "lastsnd:900000 lastrcv:900000 lastack:900000\n")  # -i prints lastsnd though nothing was sent
    plant_ss(w, sock_listen(), never_used)
    for n in range(6):
        ptick(w, server, NOW + 60 * n)
    sv = emb_shared(w)
    assert sv["state"] == "IDLE" and sv["waiting"] == 0 and not items_with(w, "Server:")


def test_review46_f4_the_rerankers_reserve_is_repriced_from_their_peak_since_the_era(wp):
    plant_reranker_peak(wp)  # the rerankers' p95: 3 GB
    queue_rr = [{"cmd": "/usr/bin/python3 /x/tools/land.py W2-Q=abcdef1", "cwd": "/", "pid": 800, "ppid": 1},
                {"cmd": "/home/u/.local/share/gov-os/reranker-venv/bin/python -I serve.py", "cwd": "/", "pid": 801,
                 "ppid": 800, "rss_kb": 600_000}]
    leads(wp, 1, extra=queue_rr)
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 300)  # 1 sample of 30: the old p95
    assert f"services' headroom {(600_000 + 3 * GB - 600_000) // 1024} MB" in status(wp)["admit_reason"]
    assert "reserve 3.0 GB: the rerankers' p95 (1 of 30 samples, 0.0 of 24 h, since 2026-11-02 13:00)" in \
        (wp.d / "status.txt").read_text()
    many = [{"cmd": "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Q", "cwd": "/",
             "pid": 900 + i, "ppid": 100, "rss_kb": 500_000} for i in range(29)]  # inside the lead: sampled only
    leads(wp, 1, extra=queue_rr + many)
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 360)  # 31 samples over 60 s: under a day, the p95 (G2)
    assert status(wp)["reranker_reserve"]["kb"] == 3 * GB and "31 of 30 samples, 0.0 of 24 h" in \
        status(wp)["reranker_reserve"]["how"]
    leads(wp, 1, extra=queue_rr)
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 300 + 86400)  # 32 samples over a day: the peak
    s = status(wp)
    # reserved: 2 allowed x the 600,000 kB peak = 1,200,000, less the 600,000 held outside the leads now
    assert f"services' headroom {(600_000 + 600_000) // 1024} MB" in s["admit_reason"]
    assert s["reranker_reserve"]["kb"] == 1_200_000 and s["reranker_reserve"]["samples"] == 32
    assert "reserve 1.1 GB: 2 x the 585 MB peak (32 samples since 2026-11-02 13:00)" in (wp.d / "status.txt").read_text()
    conf(wp, memory_rule="literal", reranker_era_from="2099-01-01 00:00")  # an era not begun: no samples, the p95
    tick(wp, DISPATCH_NO_PEAKS_REFRESH=1, DISPATCH_NOW=NOW + 360 + 86400)
    assert status(wp)["reranker_reserve"]["samples"] == 0 and status(wp)["reranker_reserve"]["kb"] == 3 * GB


# ---- review round 2 (G1, G2) ----------------------------------------------------------------------------------------------

def test_round2_g1_client_4xx_never_fail_the_server_and_5xx_failing_clears_after_a_quiet_span(w, server):
    """Three 400s (and 404s, 499s) on a quiet server: the client's, never FAILING. Three 500s: FAILING (the fallback
    test request refused, so it cannot clear it), then cleared after embed_fail_clear_s with nothing new."""
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen())
    rtick = lambda t: tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    rtick(NOW)
    glog(w, "shared", gin(400) * 3 + gin(404) + gin(499))
    for n in range(1, 8):  # and seven quiet passes after them
        rtick(NOW + 60 * n)
        sv = emb_shared(w)
        assert sv["state"] == "IDLE" and sv["fails_in_a_row"] == 0 and not items_with(w, "Server:")
    glog(w, "shared", gin(500) * 3)
    rtick(NOW + 480)
    assert emb_shared(w)["state"] == "FAILING" and len(items_with(w, "Server:")) == 1
    for t in (NOW + 540, NOW + 600, NOW + 720):  # quiet, under 300 s since the last failure: still FAILING
        rtick(t)
        assert emb_shared(w)["state"] == "FAILING"
    assert status(w)["ready_waits"]["W2-B T-B"] == HELD
    rtick(NOW + 780)  # 300 s with no new failure: the run ends, the incident clears, starts are free
    sv = emb_shared(w)
    assert sv["state"] == "IDLE" and sv["fails_in_a_row"] == 0 and not sv["hung_since"] and server_stale(w) == []
    assert status(w)["embedding_server"]["state"] == "IDLE" and len(items_with(w, "Server:")) == 1
    rtick(NOW + 900)
    assert any(c.startswith("launch") and "W2-B" in c for c in calls(w))


def test_round2_g1_the_test_request_clears_failing_and_a_runner_task_error_counts(w, server):
    conf(w, embed_fail_clear_s=3600)  # the quiet span apart: only the test request can clear it here
    glog(w, "shared", LOADED)
    plant_ss(w, sock_listen())
    rtick = lambda t: tick(w, DISPATCH_EMBED_URL=REFUSED, DISPATCH_NOW=t)
    rtick(NOW)
    glog(w, "shared", gin(500) + "srv    send_error: task id = 42, error: the runner failed\n" + gin(503))
    rtick(NOW + 60)  # three server failures, the test request refused: FAILING
    assert emb_shared(w)["state"] == "FAILING" and emb_shared(w)["last_fail_code"] == 503
    for n in range(2, 6):  # passes 3 to 6: within embed_check_every (5) passes of the last test request: none sent
        ptick(w, server, NOW + 60 * n)
        assert server["hits"] == 0 and emb_shared(w)["state"] == "FAILING"
    ptick(w, server, NOW + 360)  # pass 7, five after the refused one: one test request, it answers: cleared
    assert server["hits"] == 1 and emb_shared(w)["state"] == "IDLE" and server_stale(w) == []


# ---- DEC-1039 (1b): the Gov Load Balancer; DEC-1037 (4): limits from the machine; DEC-1038 (4): targets -------------

def shared_counter(w, shared_mib, dedicated_mib=6000):
    """A stand-in for the Windows counters (powershell.exe Get-Counter): two adapters, the card and a virtual one."""
    exe = w.tmp / "shared-counter"
    (w.tmp / "shared.txt").write_text(
        f"\\\\h\\gpu adapter memory(luid_0x00000000_0x00011f5c_phys_0)\\dedicated usage {dedicated_mib * 2 ** 20}\n"
        "\\\\h\\gpu adapter memory(luid_0x00000000_0x00013318_phys_0)\\dedicated usage 0\n"
        f"\\\\h\\gpu adapter memory(luid_0x00000000_0x00011f5c_phys_0)\\shared usage {shared_mib * 2 ** 20}\n"
        "\\\\h\\gpu adapter memory(luid_0x00000000_0x00013318_phys_0)\\shared usage 8192\n")
    exe.write_text(f"#!{sys.executable}\nimport sys\nsys.stdout.write(open({str(w.tmp / 'shared.txt')!r}).read())\n")
    exe.chmod(0o755)


def lead_proc(w, i, pid, age_s=3600, rss_kb=300_000):
    (w.wt / f"L{i}").mkdir(exist_ok=True)
    return {"cmd": LEAD.format(f"T-L{i}"), "cwd": str(w.wt / f"L{i}"), "pid": pid, "ppid": 1, "age_s": age_s,
            "rss_kb": rss_kb}


def jobs_by_name(w):
    return {j["name"]: j for j in status(w)["jobs"]}


def status_line(w, start):
    return next(l for l in (w.d / "status.txt").read_text().splitlines() if l.startswith(start))


def test_lb_a_jobs_phase_is_detected_from_its_processes(w):
    (w.d / "ready.txt").write_text("")
    (w.d / "embed-health.json").write_text(json.dumps({"servers": {"shared": {"state": "BUSY"}}}))
    rr = "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Q"
    review = '/home/u/.local/bin/claude -p --settings {"env":{"GOV_ROLE":"independent-auditor","GOV_TICKET":"T-L4"}}'
    procs = [lead_proc(w, 0, 100), {"cmd": rr, "cwd": "/", "pid": 101, "ppid": 100, "rss_kb": 2_000_000},
             lead_proc(w, 1, 110), {"cmd": "python3 -m pytest tests -n 6", "cwd": "/", "pid": 111, "ppid": 110},
             lead_proc(w, 2, 120, age_s=60), lead_proc(w, 3, 130),
             lead_proc(w, 4, 140), {"cmd": review, "cwd": "/", "pid": 141, "ppid": 140},
             {"cmd": "/usr/bin/python3 /x/tools/land.py W2-Q=abcdef1", "cwd": "/", "pid": 200, "ppid": 1},
             {"cmd": "bash /x/tools/rebuild_slot.sh /tree", "cwd": "/", "pid": 201, "ppid": 200},
             {"cmd": "flock -n -o -E 213 /tmp/gov-os-heavy-slot-1.lock python3 -m gov.cli.main rebuild --json",
              "cwd": "/", "pid": 202, "ppid": 201},
             {"cmd": "python3 -m gov.cli.main rebuild --json", "cwd": "/", "pid": 203, "ppid": 202},
             # waiting for a slot (the live dry pass, 20:05): a wrapper with no flock yet is no running job
             {"cmd": "bash /x/tools/heavy_slot.sh python3 -m pytest tests", "cwd": "/", "pid": 450, "ppid": 1},
             {"cmd": "bash /x/tools/rebuild_slot.sh /tree2", "cwd": "/", "pid": 460, "ppid": 1},
             {"cmd": "python3 -m gov.cli.main rebuild --json", "cwd": "/", "pid": 300, "ppid": 1, "age_s": 100,
              "cpu_ticks": 2 * 100 * os.sysconf("SC_CLK_TCK")},  # no earlier sample: its lifetime's 2 cores
             {"cmd": "flock -n -o -E 213 /tmp/gov-os-heavy-slot-2.lock python3 -m pytest tests", "cwd": "/",
              "pid": 400, "ppid": 1}, {"cmd": "python3 -m pytest tests", "cwd": "/", "pid": 401, "ppid": 400},
             {"cmd": "/usr/bin/python3 /x/tools/close_build.py W2-C", "cwd": "/", "pid": 500, "ppid": 1}]
    w.procs.write_text(json.dumps(procs))
    tick(w)
    j = jobs_by_name(w)
    assert {n: (v["kind"], v["phase"]) for n, v in j.items()} == {
        "L0": ("lead", "retrieval"), "L1": ("lead", "test"), "L2": ("lead", "start"), "L3": ("lead", "build"),
        "L4": ("lead", "review"), "land": ("landing", "rebuild.embedding"), "pid 300": ("rebuild", "rebuild.embedding"),
        "pid 400": ("slot", "test"), "W2-C": ("close", "other")}
    assert j["L0"]["rss_kb"] == 2_300_000 and j["pid 300"]["cpu"] == 2.0
    assert "pid 450" not in j and "pid 460" not in j  # waiting for a slot: no job
    assert "Jobs by phase: lead L0 retrieval (" in (w.d / "status.txt").read_text()
    (w.d / "embed-health.json").write_text(json.dumps({"servers": {"shared": {"state": "IDLE"}}}))
    tick(w, DISPATCH_NOW=NOW + 60)
    assert jobs_by_name(w)["pid 300"]["phase"] == "rebuild.lexical"


def test_lb_todays_numbers_are_unchanged_on_this_machines_figures(wp):
    (wp.tmp / "meminfo").write_text(f"MemTotal:       24607384 kB\nMemAvailable: {16 * GB} kB\n")
    smi(wp)
    tick(wp)
    tick(wp, DISPATCH_NOW=NOW + 60)
    line = status_line(wp, "Limits: ")
    assert ("from 20 CPUs" in line and "23.5 GB, RTX 5070 Ti 16303 MiB: band 14-18, margin 2, heavy slots 3 x 6 "
            "workers (heavy_slots.conf 3 x 6), slots gpu/cpu 3/2, GPU headroom 2048 MiB, reranker GPU slots 2 priced "
            "(the installed hook's own default: 2; proposed 2), spill floor 1019 MiB; config.json overrides: none") \
        in line, line
    lim = json.loads((wp.d / "limits.json").read_text())
    assert lim["rerank_gpu_slots"] == 2 and lim["limits"]["cpu_band"] == [14, 18]
    assert "(band 14-18: " in status_line(wp, "Balance: ")


def test_lb_an_explicit_number_in_config_wins_and_the_status_says_so(wp):
    conf(wp, memory_rule="literal", cpu_band=[12, 16], rerank_gpu_slots=3)
    smi(wp)
    tick(wp)
    tick(wp, DISPATCH_NOW=NOW + 60)
    line = status_line(wp, "Limits: ")
    assert "config.json overrides: cpu_band [12, 16] (derived [14, 18]), rerank_gpu_slots 3 (derived 2)" in line
    assert "(band 12-16: " in status_line(wp, "Balance: ")


def test_lb_a_machine_change_raises_one_item(w):
    (w.d / "ready.txt").write_text("")
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert not items_with(w, "Machine:")
    tick(w, DISPATCH_NOW=NOW + 120, DISPATCH_NPROC=32)
    items = items_with(w, "Machine:")
    assert len(items) == 1 and "cpus 20 -> 32" in items[0] and "band 22-29" in items[0]
    tick(w, DISPATCH_NOW=NOW + 180, DISPATCH_NPROC=32)
    assert len(items_with(w, "Machine:")) == 1


def test_lb_the_forecast_refuses_a_start_that_would_put_gpu_memory_over_its_budget(wp):
    """The embedders (5.6 GiB) and a reranker service (3.5 GiB, one GPU slot) on the 16 GB card, a running lead in
    its retrieval whose reranker has not taken the GPU yet, and 3 GPU reranker slots enforced (the hook copy that reads
    limits.json, 3 there): the newcomer's retrieval would bring it to 16.1 of 13.9 GiB: refused, GPU named (the
    free-memory check alone admits it)."""
    conf(wp, memory_rule="literal", rerank_gpu_slots=3)
    wp.env["DISPATCH_RERANK_HOOK"] = str(plant_hook(wp.tmp, NEW_HOOK))
    (wp.d / "limits.json").write_text(json.dumps({"rerank_gpu_slots": 3}))
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 5734 + 3584)
    hold_rerank_gpu(wp, 0)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")  # the first pass reads the GPU
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    rr = "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Q"
    wp.procs.write_text(json.dumps([lead_proc(wp, 0, 100), {"cmd": rr, "cwd": "/", "pid": 101, "ppid": 100}]))
    tick(wp, DISPATCH_NOW=NOW + 60)
    s = status(wp)
    assert not s["admit"] and s["admit_reason"].startswith("forecast refuses (GPU binding): GPU memory 16.1 of 13.9 GB")
    assert all(r.startswith("not admitted: forecast refuses (GPU binding)") for r in s["ready_waits"].values())
    assert calls(wp) == [] and "lead: REFUSES, binding GPU: GPU memory 16.1 of 13.9 GB" in status_line(wp, "Forecast: ")


def test_lb_the_forecast_names_the_binding_resource_when_it_admits(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 5734 + 3584)
    hold_rerank_gpu(wp, 0)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")  # the first pass reads the GPU
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    tick(wp, DISPATCH_NOW=NOW + 60)
    s = status(wp)
    assert s["admit"] and "forecast admits (binding GPU: GPU memory 12.6 of 13.9 GB" in s["admit_reason"]
    assert calls(wp)[0].startswith("launch W2-A")


def test_lb_pairing_chooses_a_gpu_heavy_start_beside_two_running_test_slots(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    (wp.d / "ready.txt").write_text("W2-A T-A A.md W2-A-A5-run1.json first=test\nW2-B T-B B.md W2-B-A5-run1.json\n")
    hz = os.sysconf("SC_CLK_TCK")
    procs = []
    for n, pid in enumerate((400, 410)):
        procs += [{"cmd": f"flock -n -o -E 213 /tmp/gov-os-heavy-slot-{n + 1}.lock python3 -m pytest tests", "cwd": "/",
                   "pid": pid, "ppid": 1}, {"cmd": "python3 -m pytest tests -n 6", "cwd": "/", "pid": pid + 1,
                                            "ppid": pid, "cpu_ticks": int(5.9 * 60 * hz)}]
    wp.procs.write_text(json.dumps(procs))
    (wp.d / "jobs-prev.json").write_text(json.dumps({"t": NOW - 60, "ticks": {"401": 0, "411": 0, "400": 0, "410": 0}}))
    cpu_prev(wp, busy=1000, total=10000)
    (wp.tmp / "procstat").write_text(PROCSTAT.format(busy=2200, idle=9800, iowait=0))  # 12 busy cores
    tick(wp, minute=False)
    s = status(wp)
    assert s["pair_load"]["cpu"] > s["pair_load"]["gpu"], s["pair_load"]
    assert calls(wp) == ["launch W2-B T-B B.md W2-B-A5-run1.json"], (calls(wp), s["ready_waits"])
    assert s["ready_waits"]["W2-A T-A"].startswith("paired: W2-B goes first (its heavy resource gpu is the idler")


def test_lb_pairing_chooses_a_cpu_heavy_start_while_the_gpu_embeds(wp):
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    (wp.d / "ready.txt").write_text("W2-B T-B B.md W2-B-A5-run1.json\nW2-A T-A A.md W2-A-A5-run1.json first=test\n")
    (wp.d / "embed-health.json").write_text(json.dumps({"servers": {"shared": {"state": "BUSY"}}}))
    wp.procs.write_text(json.dumps([{"cmd": "python3 -m gov.cli.main rebuild --json", "cwd": "/", "pid": 300,
                                     "ppid": 1}]))
    tick(wp)
    assert calls(wp) == ["launch W2-A T-A A.md W2-A-A5-run1.json"], status(wp)["ready_waits"]
    assert jobs_by_name(wp)["pid 300"]["phase"] == "rebuild.embedding"


def test_lb_a_malformed_first_phase_is_refused(w):
    (w.d / "ready.txt").write_text("W2-A T-A A.md W2-A-A5-run1.json first=lunch\n")
    tick(w)
    assert calls(w) == [] and status(w)["ready_waits"]["W2-A T-A"].startswith("malformed line")


def test_lb_the_spill_check_raises_one_item_per_incident(w):
    (w.d / "ready.txt").write_text("")
    smi(w, gpu="NVIDIA GeForce RTX 5070 Ti, 6000, 16303, 5")
    shared_counter(w, 600)
    tick(w)
    assert gpu_items(w) == [] and "shared GPU memory 600 MiB (floor 1019 MiB): no spill" in status_line(w, "GPU rule: ")
    shared_counter(w, 1500)
    tick(w, DISPATCH_NOW=NOW + 60)
    items = gpu_items(w)
    assert len(items) == 1 and "GPU: GPU spill" in items[0].read_text() and "1500 MiB of shared GPU memory" in \
        items[0].read_text()
    assert "SPILL" in status_line(w, "GPU rule: ")
    tick(w, DISPATCH_NOW=NOW + 120)
    assert len(gpu_items(w)) == 1  # the same incident
    shared_counter(w, 600)
    tick(w, DISPATCH_NOW=NOW + 180)
    shared_counter(w, 1500)
    tick(w, DISPATCH_NOW=NOW + 240)
    assert len(gpu_items(w)) == 2  # a new spill, a new item


def test_lb_an_unreadable_shared_counter_is_said_and_is_no_failure(w):
    smi(w)
    tick(w)
    assert "shared GPU memory unread (shared-counter: No such file" in status_line(w, "GPU rule: ")
    assert not (w.d / "status.txt").read_text().startswith("TICK FAILED")


def test_lb_the_gpu_budget_is_checked_each_pass(w):
    (w.d / "ready.txt").write_text("")
    smi(w, gpu="NVIDIA GeForce RTX 5070 Ti, 14400, 16303, 5")
    shared_counter(w, 600)
    tick(w)
    items = gpu_items(w)
    assert len(items) == 1 and "GPU: GPU budget" in items[0].read_text()
    assert "ABOVE total minus headroom" in status_line(w, "GPU rule: ")
    tick(w, DISPATCH_NOW=NOW + 60)
    assert len(gpu_items(w)) == 1


def test_lb_each_pass_appends_one_balance_row_and_a_dry_pass_none(w):
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    rows = (w.orch / "log" / "capacity" / "balance.jsonl").read_text().splitlines()
    assert len(rows) == 2
    r = json.loads(rows[-1])
    assert {"busy_cores", "mem_available_mb", "gpu", "jobs", "targets", "forecast", "embedders"} <= set(r)
    tick(w, "--dry", DISPATCH_NOW=NOW + 120)
    assert len((w.orch / "log" / "capacity" / "balance.jsonl").read_text().splitlines()) == 2


def test_lb_a_16_minute_breach_opens_one_incident_and_15_minutes_held_close_it(wp):
    (wp.d / "ready.txt").write_text("")
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {2 * GB} kB\n")  # under the 3 GB floor: T2 breached
    for m in range(15):
        tick(wp, DISPATCH_NOW=NOW + 60 * m)
    assert not items_with(wp, "Incident: T2")
    tick(wp, DISPATCH_NOW=NOW + 60 * 16)
    items = items_with(wp, "Incident: T2")
    recs = sorted((wp.orch / "log" / "incidents").glob("*-T2.md"))
    assert len(items) == 1 and len(recs) == 1
    text = recs[0].read_text()
    for part in ("— T2: memory available above the floor", "- **Readings:** busy cores", "grouped by tree and session",
                 "- **Cause:** \n- **Fix:** \n"):
        assert part in text, part
    for m in range(17, 21):  # still breached: no second
        tick(wp, DISPATCH_NOW=NOW + 60 * m)
    assert len(items_with(wp, "Incident: T2")) == 1 and status(wp)["incidents_open"] == ["T2"]
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    for m in range(21, 36):
        tick(wp, DISPATCH_NOW=NOW + 60 * m)
    assert "Closed:" not in recs[0].read_text()
    tick(wp, DISPATCH_NOW=NOW + 60 * 36)
    assert "- **Closed:** " in recs[0].read_text() and "T2" not in status(wp)["incidents_open"]


def test_lb_t4_a_timed_out_embedding_opens_an_incident_at_once(w):
    (w.d / "ready.txt").write_text("")
    glog(w, "shared", LOADED)
    tick(w)
    slow = '[GIN] 2026/11/02 - 12:45:47 | 200 |  2m5.1s |       127.0.0.1 | POST     "/api/embed"\n'
    glog(w, "shared", gin(200) + gin(499) + slow + gin(503))
    tick(w, DISPATCH_NOW=NOW + 60)
    items = items_with(w, "Incident: T4")
    recs = sorted((w.orch / "log" / "incidents").glob("*-T4.md"))
    assert len(items) == 1 and len(recs) == 1 and "3 timed-out embedding(s)" in items[0]
    text = recs[0].read_text()
    assert "| 499 |" in text and "2m5.1s" in text and "| 503 |" in text and "| 200 |  1.0s" not in text
    glog(w, "shared", gin(499))
    tick(w, DISPATCH_NOW=NOW + 120)
    assert len(items_with(w, "Incident: T4")) == 1 and "- **More, " in recs[0].read_text()


def test_lb_t5_a_cold_rebuild_in_the_seed_log_opens_an_incident(w):
    (w.d / "ready.txt").write_text("")
    seed = w.orch / "log" / "seed.jsonl"
    seed.write_text(json.dumps({"kind": "rebuild", "tree": "/old", "seed": {"status": "refused"}}) + "\n")
    tick(w)  # the first read starts at the end: no old event
    assert not items_with(w, "Incident: T5")
    with open(seed, "a") as f:
        f.write(json.dumps({"kind": "rebuild", "tree": "/t", "who": "W2-X", "seed": {"status": "seeded"},
                            "timing": {"semantic_s": 20}}) + "\n")
    tick(w, DISPATCH_NOW=NOW + 60)
    assert not items_with(w, "Incident: T5")
    with open(seed, "a") as f:
        f.write(json.dumps({"kind": "rebuild", "tree": "/t", "who": "W2-X", "seed": {"status": "refused"},
                            "timing": {"semantic_s": 3000}}) + "\n")
    tick(w, DISPATCH_NOW=NOW + 120)
    assert len(items_with(w, "Incident: T5")) == 1


def test_lb_a_heavy_step_outside_a_slot_becomes_an_incident_after_15_minutes(wp):
    (wp.d / "ready.txt").write_text("")
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    wp.procs.write_text(json.dumps([{"cmd": "python3 -m pytest tests", "cwd": str(wp.wt / "W2-A"), "pid": 700,
                                     "ppid": 1, "age_s": 400}]))
    for m in range(16):
        tick(wp, DISPATCH_NOW=NOW + 60 * m)
    assert not items_with(wp, "Incident: outside-slot")
    tick(wp, DISPATCH_NOW=NOW + 60 * 16)
    items = items_with(wp, "Incident: outside-slot")
    assert len(items) == 1 and "pid 700" in items[0] and "W2-A" in items[0]


# ---- review round 1 of emg/lb: F1 (CPU of reaped children), F2 (reranker slots priced as enforced), F4 (T4) --------

def slot_run(hz, pytest_ticks):
    return [{"cmd": "flock -n -o -E 213 /tmp/gov-os-heavy-slot-1.lock python3 -m pytest tests", "cwd": "/", "pid": 10,
             "ppid": 1}, {"cmd": "python3 -m pytest tests -n 6", "cwd": "/", "pid": 11, "ppid": 10,
                          "cpu_ticks_all": pytest_ticks}]


def test_lbr_f1_a_reaped_childs_lifetime_is_not_counted_again(w):
    """The reviewer's case: a slot run's 6 workers ran 1 core each for 6 minutes and were reaped this interval (one of
    them had reaped its own child, 100 s seen, 160 s in all): the job counts their last minute, 7 cores, not their
    lifetimes again (37 cores before the fix)."""
    (w.d / "ready.txt").write_text("")
    hz = os.sysconf("SC_CLK_TCK")
    w.procs.write_text(json.dumps(slot_run(hz, (6 * 360 + 160) * hz)))  # the workers' lifetimes now in its cutime
    old = {"10": 0, "11": 0, "20": 100 * hz, **{str(p): 300 * hz for p in range(12, 18)}}
    pp = {"10": 1, "11": 10, "20": 12, **{str(p): 11 for p in range(12, 18)}}
    (w.d / "jobs-prev.json").write_text(json.dumps({"t": NOW - 60, "ticks": old, "ppid": pp}))
    tick(w)
    assert jobs_by_name(w)["pid 10"]["cpu"] == 7.0


def test_lbr_f1_a_job_is_capped_at_the_machines_cpus(w):
    (w.d / "ready.txt").write_text("")
    hz = os.sysconf("SC_CLK_TCK")
    w.procs.write_text(json.dumps(slot_run(hz, 50 * 60 * hz)))  # 50 cores' worth in a minute (an earlier record's
    (w.d / "jobs-prev.json").write_text(json.dumps({"t": NOW - 60, "ticks": {"10": 0, "11": 0}}))  # form: no ppid)
    tick(w)
    assert jobs_by_name(w)["pid 10"]["cpu"] == 20.0


def phase_shares(w, emb, rr):
    """A phase-peaks.json not due for refresh, with these measured GPU shares."""
    (w.d / "phase-peaks.json").write_text(json.dumps({"_at": NOW + 86400, "_shares": {"embedders_gpu_mib": emb,
                                                                                       "reranker_gpu_mib": rr}}))


def test_lbr_f2_the_reranker_slots_are_priced_with_the_installed_hooks_count(wp):
    """The reviewer's case: the shares measured at 5,800 and 4,655 MiB derive 1 reranker GPU slot, while today's
    installed hook hands out 2. Priced with 1 (1 held, none free) the newcomer's reranker cost nothing and the forecast
    admitted (10.2 of 13.9 GB); priced with the hook's 2 it is refused: 14.8 of 13.9 GB."""
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 10455)
    hold_rerank_gpu(wp, 0)  # pid 4000, a private reranker
    rr = "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Q"
    wp.procs.write_text(json.dumps([{"cmd": rr, "cwd": "/", "pid": 4000, "ppid": 1}]))
    phase_shares(wp, 5800, 4655)
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")  # the first pass reads the GPU
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    tick(wp, DISPATCH_NOW=NOW + 60)
    s = status(wp)
    assert not s["admit"] and s["admit_reason"].startswith("forecast refuses (GPU binding): GPU memory 14.8 of 13.9 GB")
    assert "1 GPU reranker slot(s) free" in s["admit_reason"] and calls(wp) == []
    assert "reranker GPU slots 2 priced (the installed hook's own default: 2; proposed 1)" in status_line(wp, "Limits: ")
    assert json.loads((wp.d / "limits.json").read_text())["rerank_gpu_slots"] == 1  # the proposal, for the new copy
    # once the owner installs the copy that reads limits.json, it enforces the 1 written there: priced with 1
    tick(wp, DISPATCH_NOW=NOW + 120, DISPATCH_RERANK_HOOK=str(plant_hook(wp.tmp, NEW_HOOK)))
    assert "reranker GPU slots 1 priced (the installed hook reads limits.json: 1; proposed 1)" in \
        status_line(wp, "Limits: ")
    # no hook at all: nothing bounds the rerankers, every newcomer's reranker is priced
    tick(wp, DISPATCH_NOW=NOW + 180, DISPATCH_RERANK_HOOK=str(wp.tmp / "none" / "gov_reranker_gpu_slot.py"))
    assert "reranker GPU slots 64 priced (no hook installed; proposed 1)" in status_line(wp, "Limits: ")


def test_lbr_f2_a_derived_count_is_never_0_with_a_gpu(wp):
    smi(wp)
    phase_shares(wp, 15000, 3584)  # a spurious embedders' share: (16303 - 15000 - 2048) // 3584 < 0
    tick(wp)
    tick(wp, DISPATCH_NOW=NOW + 60)
    assert json.loads((wp.d / "limits.json").read_text())["rerank_gpu_slots"] == 1


def test_lbr_f2_slots_held_beside_the_shared_service_count_as_used(wp):
    """DEC-1043 item 2: while the shared reranker service runs, the CTO's tool holds every other slot. Held is used:
    no slot is free, the newcomer's reranker cannot take the GPU and is priced at nothing; and the tool's slot holds no
    GPU memory, so it is not a reranker on the GPU in the balance row (the shares' measure)."""
    (wp.tmp / "meminfo").write_text(f"MemAvailable: {16 * GB} kB\n")
    gpu_used(wp, 5800 + 3584)
    hold_rerank_gpu(wp, 0, 1)  # pids 4000 and 4001
    wp.procs.write_text(json.dumps([
        {"cmd": "/v/reranker-venv/bin/python /x/tools/rerank_service.py", "cwd": "/", "pid": 4000, "ppid": 1},
        {"cmd": "python3 /x/tools/rerank_service_slot_hold.py", "cwd": "/", "pid": 4001, "ppid": 1}]))
    tick(wp, DISPATCH_GATE_CMD="sh -c 'echo SHUT; exit 1'")
    (wp.d / "started.txt").write_text("")
    wp.calls.write_text("")
    tick(wp, DISPATCH_NOW=NOW + 60)
    s = status(wp)
    assert s["admit"] and "the newcomer's 0.0; 0 GPU reranker slot(s) free" in s["admit_reason"], s["admit_reason"]
    row = json.loads((wp.orch / "log" / "capacity" / "balance.jsonl").read_text().splitlines()[-1])
    assert row["rr_held"] == 2 and row["rr_gpu"] == 1


def test_lbr_f4_t4_events_are_not_repeated_when_the_log_becomes_unreadable(w):
    (w.d / "ready.txt").write_text("")
    glog(w, "shared", LOADED)
    tick(w)
    glog(w, "shared", gin(499))
    tick(w, DISPATCH_NOW=NOW + 60)
    recs = sorted((w.orch / "log" / "incidents").glob("*-T4.md"))
    assert len(recs) == 1
    (w.tmp / "serve-11434.log").unlink()  # moved away: the last read's events must not count again
    for m in range(2, 17):
        tick(w, DISPATCH_NOW=NOW + 60 * m)
    assert "- **More, " not in recs[0].read_text() and "Closed:" not in recs[0].read_text()
    tick(w, DISPATCH_NOW=NOW + 60 * 17)  # 15 minutes with no event: closed
    assert "- **Closed:** " in recs[0].read_text()


# ---- live 2026-11-02 23:01 and 23:04: two false GPU budget alerts (EMG-lb2) -------------------------------------------

def hold_locks(w, holders):
    """The reranker GPU slot lock files held by the given pids (slot i by holders[i]), in the planted lock table."""
    d = w.tmp / "rerank"
    d.mkdir(exist_ok=True)
    with open(w.tmp / "proc" / "locks", "a") as f:
        for i, pid in enumerate(holders):
            p = d / f"gov-os-rerank-gpu-{i}.lock"
            p.write_text("")
            f.write(f"{20 + i}: FLOCK  ADVISORY  WRITE {pid} 08:30:{os.stat(p).st_ino} 0 EOF\n")


@pytest.mark.parametrize("slot1", ["worker", "hold tool"])
def test_lb2_both_reranker_slots_held_is_no_gpu_budget_alert(w, slot1):
    """dispatch/inbox/read/20261102-230406-gpu-alert.txt: GPU 11.5 of 15.9 GB; slot 0 held by W2-112's shared
    rerank_service.py (pid 3361765), slot 1 by a private rerank_worker.py of the merge queue's warm clone (pid 2902931)
    or by the CTO's rerank_service_slot_hold.py --watch (DEC-1043 item 2); running: lead W2-112 building, the landing
    in its test run, two slot runs; the measured shares 5,800 and 1,650 MiB derive a proposal of 5 slots, and the phases'
    peaks hold one reranker each. Priced with the proposal the pass found 3 slots free and added the running jobs'
    reranker peaks (4.8 GB) to what nvidia-smi already counted: "GPU memory 16.3 of 13.9 GB ... 3 GPU reranker slot(s)
    free", a false alert. Priced with the hook's 2, both held: none free, nothing added, no alert."""
    (w.d / "ready.txt").write_text("")
    smi(w, gpu="NVIDIA GeForce RTX 5070 Ti, 11776, 16303, 35",
        apps="3361765, [Not Found], [N/A]\n2902931, [Not Found], [N/A]\n")
    rr = 1650
    peak = lambda gpu: {"cpu": 5.9, "ram_kb": 1910344, "gpu": gpu, "util": 0, "heavy": "cpu", "samples": 40, "how": "p95"}
    (w.d / "phase-peaks.json").write_text(json.dumps({
        "_at": NOW + 86400, "_shares": {"embedders_gpu_mib": 5800, "reranker_gpu_mib": rr},
        "lead.build": dict(peak(rr), cpu=1.0, heavy=None), "landing.test": peak(rr), "slot.test": peak(rr)}))
    worker = "/v/reranker-venv/bin/python -I /x/src/gov/retrieval/rerank_worker.py Qwen/Q"
    second = ({"cmd": worker, "cwd": "/", "pid": 2902931, "ppid": 201} if slot1 == "worker" else
              {"cmd": "python3 /x/tools/rerank_service_slot_hold.py --watch", "cwd": "/", "pid": 3518237, "ppid": 1})
    procs = [lead_proc(w, 0, 100),
             {"cmd": "/v/reranker-venv/bin/python /x/tools/rerank_service.py", "cwd": "/", "pid": 3361765, "ppid": 1},
             {"cmd": "/usr/bin/python3 /x/tools/land.py W2-Q=abcdef1", "cwd": "/", "pid": 200, "ppid": 1},
             {"cmd": "python3 -m pytest tests -n 6", "cwd": "/", "pid": 201, "ppid": 200}, second]
    for pid in (3423200, 3544196):
        procs += [{"cmd": "flock -n -o -E 213 /tmp/gov-os-heavy-slot-2.lock python3 -m pytest tests", "cwd": "/",
                   "pid": pid, "ppid": 1}, {"cmd": "python3 -m pytest tests", "cwd": "/", "pid": pid + 1, "ppid": pid}]
    w.procs.write_text(json.dumps(procs))
    hold_locks(w, [3361765, second["pid"]])
    tick(w)
    tick(w, DISPATCH_NOW=NOW + 60)
    assert gpu_items(w) == [], [i.read_text() for i in gpu_items(w)]
    line = status_line(w, "GPU rule: ")
    assert ("GPU memory 11.5 of 13.9 GB (used 11.5 + running jobs' peaks 0.0 + the newcomer's 0.0; 0 GPU reranker "
            "slot(s) free): within total minus headroom") in line, line
    assert "reranker GPU slots 2 priced (the installed hook's own default: 2; proposed 5)" in status_line(w, "Limits: ")
    s = status(w)
    assert s["rerankers"]["gpu_held"] == 2 and s["rerankers"]["gpu_slots"] == 2
    row = json.loads((w.orch / "log" / "capacity" / "balance.jsonl").read_text().splitlines()[-1])
    assert row["rr_held"] == 2 and row["rr_gpu"] == (2 if slot1 == "worker" else 1)
    assert s["forecast"]["lead"]["resources"]["gpu"]["text"].endswith("the newcomer's 0.0; 0 GPU reranker slot(s) free)")
