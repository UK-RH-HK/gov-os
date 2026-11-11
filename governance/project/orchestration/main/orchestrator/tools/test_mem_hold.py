"""Tests for mem_hold.py and hold_lib.py (DEC-1138 (2)): planted ready.txt, brake folder, started.txt, meminfo values and
leads; `orch` is a tmp folder, so no live ready.txt, brake folder or /proc/meminfo is read or written.

    python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_mem_hold.py
"""
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hold_lib as H  # noqa: E402
import mem_hold as M  # noqa: E402

GB = 1024 * 1024  # kB
LOW, MID, HIGH = int(4.9 * GB), int(5.2 * GB), int(5.6 * GB)

READY = """# The CTO's ready list
# a comment about W2-170
W2-170 DAEO-61vm W2-170-A5-build.md W2-170-A5-build.json
#NEXT 3 (after W2-105's fixes): W2-105 DAEO-zpdj W2-105-A5-r4-tests.md W2-105-A5-r4-tests.json
W2-81 DAEO-l78m W2-81-A5-r6-land.md W2-81-A5-r6-land.json
W2-05 DAEO-0z8c W2-05-A5-r7-fix.md W2-05-A5-r7-fix.json

W2-170 DAEO-61vm W2-170-A5-fix.md W2-170-A5-fix.json
"""
STARTED = """2026-11-11 18:32:04 W2-170 W2-170-A5-build.md W2-170-A5-build.json
2026-11-11 19:36:02 W2-81 W2-81-A5-r6-land.md W2-81-A5-r6-land.json
"""


def dispatcher_read_list():
    """The dispatcher's own parsing of ready.txt (read-only import of the committed-to-nothing class (b) file)."""
    p = Path(H.DEFAULT_ORCH) / "dispatch/dispatcher.py"
    spec = importlib.util.spec_from_file_location("dispatcher_for_test", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_list


class Rig:
    def __init__(self, tmp, leads=("W2-170",), mem=None):
        self.cfg = H.Cfg(str(tmp / "orch"), str(tmp / "wt"))
        os.makedirs(self.cfg.dispatch)
        os.makedirs(self.cfg.brake)
        Path(self.cfg.ready).write_text(READY)
        Path(self.cfg.started).write_text(STARTED)
        self.mem = [HIGH] if mem is None else list(mem)
        self.leads = list(leads)
        self.t = 1_800_000_000.0
        self.m = M.MemHold(self.cfg, meminfo=self.reading, leads=lambda: list(self.leads), now=lambda: self.t)

    def reading(self):
        return self.mem.pop(0) if len(self.mem) > 1 else self.mem[0]

    def step(self, kb):
        self.mem = [kb]
        self.t += 15
        return self.m.step()

    def ready(self):
        return Path(self.cfg.ready).read_text()

    def brakes(self):
        return sorted(p.stem for p in Path(self.cfg.brake).glob("*.json"))

    def inbox(self):
        return sorted(Path(self.cfg.inbox).glob("*-mem-hold*.txt")) if Path(self.cfg.inbox).is_dir() else []

    def jsonl(self):
        p = Path(self.cfg.log) / "mem-hold.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


@pytest.fixture
def rig(tmp_path):
    return Rig(tmp_path)


def live(text):
    return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


# ---- the dispatcher's view: red without the tool's action, green with it --------------------------------------------

def test_without_the_hold_the_dispatcher_still_sees_startable_lines(rig):
    rl = dispatcher_read_list()
    assert len(rl(Path(rig.cfg.ready))) == 4  # RED: with no tool action four lines are live for the dispatcher
    rig.step(LOW)
    # GREEN: only the running lead's own started line is left live (the dispatcher says "running" for it)
    assert rl(Path(rig.cfg.ready)) == [["W2-170", "DAEO-61vm", "W2-170-A5-build.md", "W2-170-A5-build.json"]]


def test_no_hold_above_five_gb(rig):
    for kb in (HIGH, int(5.0 * GB), MID):
        assert rig.step(kb) is None
    assert rig.ready() == READY and rig.brakes() == [] and rig.inbox() == [] and rig.jsonl() == []


# ---- the hold --------------------------------------------------------------------------------------------------------

def test_hold_writes_brakes_and_comments_lines(rig):
    Path(rig.cfg.brake, "W2-81.json").write_text(json.dumps({"wbs": "W2-81", "brake": "runaway", "by": "spend.py"}))
    before = Path(rig.cfg.brake, "W2-81.json").read_text()
    ev = rig.step(LOW)
    assert ev["event"] == "hold"
    # brakes: running lead W2-170, live lines' W2s (W2-05, W2-170, W2-81); W2-81's belongs to someone else: kept as is
    assert rig.brakes() == ["W2-05", "W2-170", "W2-81"]
    assert Path(rig.cfg.brake, "W2-81.json").read_text() == before
    own = json.loads(Path(rig.cfg.brake, "W2-05.json").read_text())
    assert own["by"] == "mem_hold.py" and "5 GB" in own["reason"] and own["mem_available_mb"] == int(4.9 * 1024) \
        and own["W2"] == "W2-05" and own["brake"]
    assert ev["foreign_brakes_kept"] == ["W2-81"]
    # lines: the running lead's own started line stays live; the others are held in place, text kept
    lines = rig.ready().splitlines()
    assert "W2-170 DAEO-61vm W2-170-A5-build.md W2-170-A5-build.json" in lines
    assert "#HELD-MEM W2-05 DAEO-0z8c W2-05-A5-r7-fix.md W2-05-A5-r7-fix.json" in lines
    assert "#HELD-MEM W2-170 DAEO-61vm W2-170-A5-fix.md W2-170-A5-fix.json" in lines  # same W2, not yet started
    assert "#HELD-MEM W2-81 DAEO-l78m W2-81-A5-r6-land.md W2-81-A5-r6-land.json" in lines  # started, but W2-81 is not running


def test_running_leads_started_line_is_not_commented(tmp_path):
    r = Rig(tmp_path, leads=("W2-170", "W2-81"))
    r.step(LOW)
    t = r.ready()
    assert "\nW2-170 DAEO-61vm W2-170-A5-build.md W2-170-A5-build.json\n" in t
    assert "\nW2-81 DAEO-l78m W2-81-A5-r6-land.md W2-81-A5-r6-land.json\n" in t
    assert "#HELD-MEM W2-05 " in t and "#HELD-MEM W2-170 DAEO-61vm W2-170-A5-fix.md" in t
    assert r.brakes() == ["W2-05", "W2-170", "W2-81"]  # running leads and live-line W2s


def test_hold_keeps_a_copy_and_all_other_text(rig):
    rig.step(LOW)
    copies = sorted(Path(rig.cfg.dispatch).glob("ready.txt.pre-hold-*"))
    assert len(copies) == 1 and copies[0].read_text() == READY
    t = rig.ready()
    for keep in ("# The CTO's ready list", "# a comment about W2-170", "#NEXT 3 (after W2-105's fixes)"):
        assert keep in t
    assert not re.search(r"^#HELD-MEM #", t, re.M)  # a comment is never labelled
    assert not [p for p in Path(rig.cfg.dispatch).iterdir() if "hold-tmp" in p.name]  # the temp file is gone


def test_hold_logs_and_writes_an_inbox_item_that_does_not_block_a_ticket(rig):
    rig.step(LOW)
    row = [r for r in rig.jsonl() if r["event"] == "hold"][0]
    assert row["avail_mb"] == int(4.9 * 1024) and "W2-05" in row["brakes_written"] and row["lines_held"]
    items = rig.inbox()
    assert len(items) == 1 and re.match(r"\d{8}-\d{6}-mem-hold\.txt$", items[0].name)
    body = items[0].read_text()
    assert body.startswith("log: mem-hold.jsonl\n") and "status:" in body and "5 GB" in body
    assert not re.search(r"^W2:", body, re.M)  # a `W2:` line would hold that ticket's start (dispatcher inbox rule)


def test_no_second_hold_while_holding_but_new_lines_are_held(rig):
    rig.step(LOW)
    n = len(rig.inbox())
    with open(rig.cfg.ready, "a") as f:  # the CTO adds a line (and a comment) while held
        f.write("W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n# a CTO note\n")
    ev = rig.step(MID)
    assert ev["event"] == "extend" and ev["lines_held"] == ["W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json"]
    t = rig.ready()
    assert "#HELD-MEM W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n# a CTO note\n" in t
    assert "W2-99" in rig.brakes()
    assert len(rig.inbox()) == n  # an extension is logged, not an inbox item
    assert rig.step(MID) is None  # nothing new: quiet


def test_a_lead_that_appears_while_holding_is_braked(rig):
    rig.step(LOW)
    rig.leads.append("W2-40")
    rig.step(MID)
    assert "W2-40" in rig.brakes()


# ---- the release -----------------------------------------------------------------------------------------------------

def test_release_needs_two_samples_in_a_row(rig):
    rig.step(LOW)
    assert rig.step(HIGH) is None
    assert rig.step(int(5.3 * GB)) is None  # between 5 and 5.5: still held, and the run restarts
    assert rig.step(HIGH) is None
    assert rig.brakes() and "#HELD-MEM " in rig.ready()
    ev = rig.step(HIGH)
    assert ev["event"] == "release"
    assert rig.brakes() == [] and "#HELD-MEM " not in rig.ready()


def test_release_removes_only_own_brakes_and_uncomments_only_own_lines(rig):
    Path(rig.cfg.brake, "W2-81.json").write_text(json.dumps({"wbs": "W2-81", "brake": "runaway", "by": "spend.py"}))
    Path(rig.cfg.brake, "W2-77.json").write_text("not json at all")
    rig.step(LOW)
    with open(rig.cfg.ready, "a") as f:
        f.write("#HELD-NIGHT W2-60 DAEO-x W2-60-A5-run1.md W2-60-A5-run1.json\n")  # the night hold's line
    rig.step(HIGH)
    ev = rig.step(HIGH)
    assert ev["event"] == "release"
    assert rig.brakes() == ["W2-77", "W2-81"]  # others' files untouched
    t = rig.ready()
    assert "\nW2-05 DAEO-0z8c W2-05-A5-r7-fix.md W2-05-A5-r7-fix.json\n" in t
    assert "#HELD-NIGHT W2-60 DAEO-x" in t
    assert t.splitlines()[:2] == READY.splitlines()[:2]
    # every original line is back exactly (the CTO's added night line stays as it was)
    assert t.replace("#HELD-NIGHT W2-60 DAEO-x W2-60-A5-run1.md W2-60-A5-run1.json\n", "") == READY
    rel = [r for r in rig.jsonl() if r["event"] == "release"][0]
    assert sorted(rel["brakes_removed"]) == ["W2-05", "W2-170"]
    assert len(rig.inbox()) == 2  # one on the hold, one on the release


def test_release_hands_lines_to_the_night_hold_when_it_is_on(rig):
    rig.step(LOW)
    H.write_json_atomic(H.active_path(rig.cfg, "night-hold"), {"pid": os.getpid()})  # a live pid
    rig.step(HIGH)
    rig.step(HIGH)
    t = rig.ready()
    assert "#HELD-MEM " not in t and "#HELD-NIGHT W2-05 DAEO-0z8c W2-05-A5-r7-fix.md" in t


def test_a_stale_night_active_file_does_not_capture_lines(rig):
    rig.step(LOW)
    H.write_json_atomic(H.active_path(rig.cfg, "night-hold"), {"pid": 2 ** 22 + 12345})  # no such process
    rig.step(HIGH)
    rig.step(HIGH)
    assert "#HELD-NIGHT" not in rig.ready() and "\nW2-05 DAEO-0z8c" in rig.ready()


def test_a_restart_while_holding_resumes_from_the_files(rig):
    rig.step(LOW)
    m2 = M.MemHold(rig.cfg, meminfo=lambda: HIGH, leads=lambda: [], now=lambda: rig.t)
    assert m2.holding
    m2.step()
    ev = m2.step()
    assert ev["event"] == "release" and rig.brakes() == [] and "#HELD-MEM" not in rig.ready()


def test_release_now_flag_releases_at_once(rig, capsys):
    rig.step(LOW)
    ev = rig.m.release(MID)
    assert ev["event"] == "release" and rig.brakes() == [] and rig.ready() == READY


# ---- cooperation on ready.txt ----------------------------------------------------------------------------------------

def test_a_line_added_between_read_and_rename_is_not_lost(rig):
    added = "W2-77 DAEO-late W2-77-A5-run1.md W2-77-A5-run1.json\n"

    def editor():  # an unlocked editor appends after the tool's read, before its rename
        with open(rig.cfg.ready, "a") as f:
            f.write(added)

    info, changed = H.rewrite_ready(rig.cfg, lambda ls: H.hold_live_lines(ls, H.MEM_PREFIX), backup=True, after_read=editor)
    assert changed
    t = rig.ready()
    assert "#HELD-MEM " + added in t  # re-read, applied to the new content, renamed
    assert not live(t)


def test_the_lock_is_taken_and_a_busy_lock_is_not_overrun(rig):
    import fcntl
    fd = os.open(rig.cfg.lock, os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        with pytest.raises(H.LockTimeout):
            H.rewrite_ready(rig.cfg, lambda ls: H.hold_live_lines(ls, H.MEM_PREFIX), lock_timeout=0.2)
        assert rig.ready() == READY
        rig.mem = [LOW]
        with pytest.raises(H.LockTimeout):
            H.rewrite_ready(rig.cfg, lambda ls: (ls, {}), lock_timeout=0.1)  # even a read waits its turn
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    assert rig.step(LOW)["event"] == "hold"


def test_a_missing_ready_file_is_not_an_error(tmp_path):
    cfg = H.Cfg(str(tmp_path / "orch"), str(tmp_path / "wt"))
    os.makedirs(cfg.dispatch)
    assert H.rewrite_ready(cfg, lambda ls: (ls, {})) == ({}, False)


def test_file_mode_is_kept(rig):
    os.chmod(rig.cfg.ready, 0o640)
    rig.step(LOW)
    assert (os.stat(rig.cfg.ready).st_mode & 0o777) == 0o640


# ---- reading the machine; no signals, no name matching ----------------------------------------------------------------

def test_running_leads_by_marker_and_worktree(tmp_path):
    cfg = H.Cfg(str(tmp_path / "orch"), str(tmp_path / "wt"))
    proc = tmp_path / "proc"

    def plant(pid, argv, cwd):
        d = proc / str(pid)
        d.mkdir(parents=True)
        (d / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")
        (tmp_path / "wt" / cwd).mkdir(parents=True, exist_ok=True)
        os.symlink(str(tmp_path / "wt" / cwd), d / "cwd")

    plant(11, ["claude", "--settings", '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"X"}}'], "W2-05")
    plant(12, ["claude", "--settings", '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"X"}}'], "W2-81/src")
    plant(13, ["claude", "--settings", '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"X"}}'], "W2-66c-tests")  # a worker folder
    plant(14, ["python3", "x.py"], "W2-40")  # no marker
    plant(15, ["claude", '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"X"}}'], "W2-00-store")  # the store
    assert H.running_leads(cfg, str(proc)) == ["W2-05", "W2-81"]


def test_meminfo_reader(tmp_path):
    p = tmp_path / "meminfo"
    p.write_text("MemTotal:       24030000 kB\nMemAvailable:    4999999 kB\n")
    assert H.mem_available_kb(str(p)) == 4999999
    assert H.mem_available_kb(str(tmp_path / "none")) is None


def test_the_tools_never_signal_or_match_a_process_by_name():
    here = Path(__file__).resolve().parent
    for name in ("mem_hold.py", "night_hold.py", "hold_lib.py"):
        src = (here / name).read_text()
        for bad in ("pkill", "pgrep", "killall", "SIGTERM", "SIGKILL", "subprocess", "os.killpg", "proc.sh stop"):
            assert bad not in src, (name, bad)
    kills = re.findall(r"os\.kill\(.*\)", (here / "hold_lib.py").read_text())
    assert [k.split("#")[0].strip() for k in kills] == ["os.kill(int(pid), 0)"]  # signal 0: existence check only
    assert "os.kill" not in (here / "mem_hold.py").read_text()


def test_none_meminfo_changes_nothing(tmp_path):
    r = Rig(tmp_path)
    r.m.meminfo = lambda: None
    assert r.m.step() is None and r.ready() == READY and r.brakes() == []


def test_the_loop_end_to_end_as_a_process(tmp_path):
    """The real script on planted folders and a planted meminfo: hold, then release, then --release-now finds nothing."""
    import subprocess
    import time
    rig = Rig(tmp_path)
    mi = tmp_path / "meminfo"
    mi.write_text("MemAvailable:    4000000 kB\n")
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "mem_hold.py"), "--every", "0.05", "--orch", str(tmp_path / "orch"),
           "--wt", str(tmp_path / "wt"), "--meminfo", str(mi)]
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        def wait(cond, secs=5):
            end = time.time() + secs
            while time.time() < end and not cond():
                time.sleep(0.05)
            return cond()
        assert wait(lambda: rig.brakes() and "#HELD-MEM " in rig.ready())
        assert not live(rig.ready())  # no leads run in this planted tree: every live line is held
        mi.write_text("MemAvailable:    6000000 kB\n")
        assert wait(lambda: not rig.brakes() and "#HELD-MEM " not in rig.ready())
        assert rig.ready() == READY
    finally:
        p.terminate()  # this test's own child, by its pid
        p.wait(5)
    assert [r["event"] for r in rig.jsonl()] == ["hold", "release"]
    assert not p.stderr.read()
