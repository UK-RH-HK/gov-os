"""Tests for night_hold.py (DEC-1138 (3)): planted ready.txt, nightly status/run folders/marker and a fake clock; `orch` is a
tmp folder, so no live ready.txt, nightly log or clock is used.

    python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_night_hold.py
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hold_lib as H  # noqa: E402
import mem_hold as M  # noqa: E402
import night_hold as N  # noqa: E402
from test_mem_hold import READY, STARTED, LOW, HIGH, dispatcher_read_list, live  # noqa: E402


def at(hm, day="2026-11-12"):
    return datetime.fromisoformat(f"{day}T{hm}:00")


class Rig:
    def __init__(self, tmp, leads=("W2-170",), hm="02:50"):
        self.cfg = H.Cfg(str(tmp / "orch"), str(tmp / "wt"))
        os.makedirs(self.cfg.dispatch)
        os.makedirs(self.cfg.nightly)
        Path(self.cfg.ready).write_text(READY)
        Path(self.cfg.started).write_text(STARTED)
        self.hm = hm
        self.leads = list(leads)
        self.n = N.NightHold(self.cfg, now=lambda: at(self.hm), leads=lambda: list(self.leads))

    def step(self, hm):
        self.hm = hm
        return self.n.step()

    def ready(self):
        return Path(self.cfg.ready).read_text()

    def inbox(self):
        return sorted(Path(self.cfg.inbox).glob("*-night-hold*.txt")) if Path(self.cfg.inbox).is_dir() else []

    def jsonl(self):
        p = Path(self.cfg.log) / "night-hold.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    def run_folder(self, hm="0400", day="20261112", text="2026-11-12 04:05:00 nightly night: start\n"):
        d = Path(self.cfg.nightly) / f"{day}-{hm}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "run.txt").write_text(text)
        return d

    def marker(self, label="2026-11-12"):
        Path(self.cfg.orch, "NIGHTLY-RUNNING").write_text(f"{label} 04:05:00 pid 1\n")


@pytest.fixture
def rig(tmp_path):
    return Rig(tmp_path)


# ---- the window ------------------------------------------------------------------------------------------------------

def test_window_edges():
    assert not N.in_window(at("02:59")) and N.in_window(at("03:00")) and N.in_window(at("07:29"))
    assert not N.in_window(at("07:30")) and not N.in_window(at("12:00")) and not N.in_window(at("00:00"))


def test_nothing_is_held_before_03_00(rig):
    assert rig.step("02:59") is None and rig.ready() == READY and rig.inbox() == [] and rig.jsonl() == []


def test_red_without_the_action_green_with_it(rig):
    rl = dispatcher_read_list()
    assert len(rl(Path(rig.cfg.ready))) == 4  # RED: at 03:00 with no hold four lines are live
    rig.step("03:00")
    assert rl(Path(rig.cfg.ready)) == [["W2-170", "DAEO-61vm", "W2-170-A5-build.md", "W2-170-A5-build.json"]]  # GREEN


# ---- the hold --------------------------------------------------------------------------------------------------------

def test_hold_at_03_00_comments_every_live_line_not_a_running_leads_own(rig):
    ev = rig.step("03:00")
    assert ev["event"] == "hold"
    lines = rig.ready().splitlines()
    assert "W2-170 DAEO-61vm W2-170-A5-build.md W2-170-A5-build.json" in lines  # the running lead: untouched
    for held in ("W2-05 DAEO-0z8c W2-05-A5-r7-fix.md W2-05-A5-r7-fix.json",
                 "W2-81 DAEO-l78m W2-81-A5-r6-land.md W2-81-A5-r6-land.json",
                 "W2-170 DAEO-61vm W2-170-A5-fix.md W2-170-A5-fix.json"):
        assert "#HELD-NIGHT " + held in lines
    assert "# a comment about W2-170" in lines and not re.search(r"^#HELD-NIGHT #", rig.ready(), re.M)
    copies = list(Path(rig.cfg.dispatch).glob("ready.txt.pre-hold-*"))
    assert len(copies) == 1 and copies[0].read_text() == READY


def test_hold_logs_and_writes_one_inbox_item(rig):
    rig.step("03:00")
    rig.step("03:01")
    rig.step("03:02")
    assert [r["event"] for r in rig.jsonl()] == ["hold"]
    items = rig.inbox()
    assert len(items) == 1 and re.match(r"\d{8}-\d{6}-night-hold\.txt$", items[0].name)
    body = items[0].read_text()
    assert body.startswith("log: night-hold.jsonl\n") and "status:" in body and not re.search(r"^W2:", body, re.M)


def test_a_line_the_cto_adds_while_held_is_held_and_kept(rig):
    rig.step("03:00")
    with open(rig.cfg.ready, "a") as f:
        f.write("W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n")
    ev = rig.step("03:30")
    assert ev["event"] == "extend"
    assert "#HELD-NIGHT W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n" in rig.ready()
    rig.step("07:30")
    assert "\nW2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n" in rig.ready()


def test_the_cto_may_remove_a_held_line_and_release_does_not_bring_it_back(rig):
    rig.step("03:00")
    t = rig.ready().replace("#HELD-NIGHT W2-05 DAEO-0z8c W2-05-A5-r7-fix.md W2-05-A5-r7-fix.json\n", "")
    Path(rig.cfg.ready).write_text(t)
    rig.step("07:30")
    assert "W2-05" not in rig.ready()


# ---- the end of the nightly ------------------------------------------------------------------------------------------

def test_release_when_the_nightly_run_has_a_verdict(rig):
    rig.step("03:00")
    d = rig.run_folder()
    rig.marker()
    assert rig.step("05:00") is None and "#HELD-NIGHT" in rig.ready()  # running: marker is today's, no verdict
    (d / "run.txt").write_text("2026-11-12 04:05:00 nightly night: start\nverdict: red 3\nduration: 4000 s\n")
    assert rig.step("05:30") is None and "#HELD-NIGHT" in rig.ready()  # verdict line but the marker is still there
    os.remove(Path(rig.cfg.orch, "NIGHTLY-RUNNING"))
    ev = rig.step("05:31")
    assert ev["event"] == "release" and "run.txt holds its end" in ev["why"]
    assert rig.ready() == READY
    assert rig.step("05:32") is None and rig.step("06:00") is None  # not held again today
    assert [r["event"] for r in rig.jsonl()] == ["hold", "release"] and len(rig.inbox()) == 2


@pytest.mark.parametrize("text", [
    "2026-11-12 04:00:00 nightly night: NOT STARTED by nightly_restart.sh: the main tree is not clean\n",
    "2026-11-12 04:05:00 nightly night: start\n2026-11-12 05:00:00 nightly_restart.sh: the run was KILLED by its memory cap; its clone is kept\n",
])
def test_release_when_the_run_did_not_start_or_was_killed(rig, text):
    rig.step("03:00")
    rig.run_folder(text=text)
    ev = rig.step("04:30")
    assert ev["event"] == "release" and rig.ready() == READY


def test_release_by_the_status_line_for_today(rig):
    rig.step("03:00")
    with open(os.path.join(rig.cfg.nightly, "status.txt"), "w") as f:
        f.write("2026-11-11 ran | verdict: red 2\n2026-11-12 running | something\n")
    assert rig.step("04:00") is None  # `running` is not an end, and yesterday's line is not today's
    with open(os.path.join(rig.cfg.nightly, "status.txt"), "a") as f:
        f.write("2026-11-12 FAILED | no verdict\n")
    assert rig.step("04:01")["event"] == "release"


def test_release_by_the_restart_wrapper_log(rig):
    rig.step("03:00")
    log = Path(rig.cfg.nightly, "restart")
    log.mkdir()
    (log / "2026-11-12.log").write_text("2026-11-12 04:00:01 nightly_restart: start (pid 5)\n"
                                        "2026-11-12 04:06:00 nightly_restart: quiet for 5 minutes, starting\n")
    assert rig.step("04:30") is None
    with open(log / "2026-11-12.log", "a") as f:
        f.write("2026-11-12 05:40:00 nightly_restart: run ended: exit 0, unit result success\n")
    assert rig.step("05:41")["event"] == "release"


def test_yesterdays_and_early_run_folders_do_not_end_todays_hold(rig):
    rig.step("03:00")
    rig.run_folder(day="20261111", hm="0400", text="verdict: green\n")  # yesterday
    rig.run_folder(day="20261112", hm="0200", text="verdict: green\n")  # before the 03:55-07:59 window of the check
    assert rig.step("04:00") is None and "#HELD-NIGHT" in rig.ready()


def test_release_at_07_30_when_the_nightly_never_ended(rig):
    rig.step("03:00")
    rig.run_folder()
    rig.marker()
    assert rig.step("07:29") is None and "#HELD-NIGHT" in rig.ready()
    ev = rig.step("07:30")
    assert ev["event"] == "release" and "07:30" in ev["why"] and rig.ready() == READY


def test_a_fresh_night_holds_again_the_next_day(rig):
    rig.step("03:00")
    rig.step("07:30")
    rig.hm = "03:00"
    rig.n.now = lambda: at("03:00", "2026-11-13")
    assert rig.n.step()["event"] == "hold"


# ---- release touches only its own lines; cooperation with mem_hold ---------------------------------------------------------

def test_release_uncomments_only_its_own_lines(rig):
    with open(rig.cfg.ready, "a") as f:
        f.write("#HELD-MEM W2-60 DAEO-x W2-60-A5-run1.md W2-60-A5-run1.json\n#NEXT 7 (note): W2-98 DAEO-wi46 a b\n")
    base = rig.ready()
    rig.step("03:00")
    rig.step("07:30")
    assert rig.ready() == base


def test_night_release_hands_lines_to_mem_hold_when_it_is_on(rig):
    rig.step("03:00")
    H.write_json_atomic(H.active_path(rig.cfg, "mem-hold"), {"pid": os.getpid()})
    ev = rig.step("07:30")
    assert ev["handed_to_mem_hold"] and "#HELD-NIGHT" not in rig.ready()
    assert "#HELD-MEM W2-05 DAEO-0z8c W2-05-A5-r7-fix.md" in rig.ready()


def test_both_tools_on_one_file_never_open_a_window_and_never_lose_a_line(tmp_path):
    """Memory low at 03:10 while the night hold is on; recovery at 03:20, still night; nightly ends 05:00."""
    r = Rig(tmp_path)
    mem = {"kb": HIGH}
    t = {"hm": "02:50"}
    m = M.MemHold(r.cfg, meminfo=lambda: mem["kb"], leads=lambda: list(r.leads), now=lambda: at(t["hm"]).timestamp())
    r.n.now = lambda: at(t["hm"])
    live_started = [["W2-170", "DAEO-61vm", "W2-170-A5-build.md", "W2-170-A5-build.json"]]
    rl = dispatcher_read_list()
    def go(hm, kb=None):
        t["hm"] = hm
        if kb:
            mem["kb"] = kb
        r.n.step()
        m.step()
        return rl(Path(r.cfg.ready))
    assert len(go("02:50")) == 4
    assert go("03:00") == live_started
    with open(r.cfg.ready, "a") as f:
        f.write("W2-99 DAEO-new W2-99-A5-run1.md W2-99-A5-run1.json\n")  # the CTO adds a line during the hold
    assert go("03:05") == live_started
    assert go("03:10", LOW) == live_started  # memory low: mem hold finds nothing live (the night hold has them)
    assert go("03:15", HIGH) == live_started
    assert go("03:20") == live_started  # mem hold releases at the second sample: night hold is on, nothing opens
    assert "#HELD-MEM" not in r.ready() and r.ready().count("#HELD-NIGHT") == 4
    r.run_folder(text="verdict: green\n")
    assert go("05:00") == live_started + [["W2-81", "DAEO-l78m", "W2-81-A5-r6-land.md", "W2-81-A5-r6-land.json"],
                                         ["W2-05", "DAEO-0z8c", "W2-05-A5-r7-fix.md", "W2-05-A5-r7-fix.json"],
                                         ["W2-170", "DAEO-61vm", "W2-170-A5-fix.md", "W2-170-A5-fix.json"],
                                         ["W2-99", "DAEO-new", "W2-99-A5-run1.md", "W2-99-A5-run1.json"]]


def test_night_hold_while_mem_hold_has_the_lines_then_mem_releases_into_the_night(tmp_path):
    r = Rig(tmp_path)
    mem = {"kb": LOW}
    t = {"hm": "02:50"}
    m = M.MemHold(r.cfg, meminfo=lambda: mem["kb"], leads=lambda: list(r.leads), now=lambda: at(t["hm"]).timestamp())
    r.n.now = lambda: at(t["hm"])
    rl = dispatcher_read_list()
    t["hm"] = "02:55"; m.step()  # memory hold first
    assert "#HELD-MEM" in r.ready()
    t["hm"] = "03:00"; r.n.step()  # night starts: the lines are comments already; the night hold marks itself active
    mem["kb"] = HIGH
    t["hm"] = "03:05"; m.step(); t["hm"] = "03:06"; m.step()  # mem hold releases: lines go to the night hold, not live
    assert len(rl(Path(r.cfg.ready))) == 1 and r.ready().count("#HELD-NIGHT") == 3


def test_a_restart_while_holding_resumes_from_the_files(rig):
    rig.step("03:00")
    n2 = N.NightHold(rig.cfg, now=lambda: at("07:30"), leads=lambda: [])
    assert n2.holding and n2.step()["event"] == "release" and rig.ready() == READY


def test_release_now_with_nothing_held_is_quiet(rig):
    assert not rig.n.holding
    assert rig.step("12:00") is None and rig.ready() == READY


def test_the_loop_end_to_end_as_a_process(tmp_path):
    import subprocess
    import time
    rig = Rig(tmp_path)
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "night_hold.py"), "--every", "0.05", "--orch", str(tmp_path / "orch"),
           "--wt", str(tmp_path / "wt"), "--now", "2026-11-12T03:30:00"]
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        end = time.time() + 5
        while time.time() < end and "#HELD-NIGHT " not in rig.ready():
            time.sleep(0.05)
        assert "#HELD-NIGHT " in rig.ready() and not live(rig.ready())
    finally:
        p.terminate()  # this test's own child, by its pid
        p.wait(5)
    assert not p.stderr.read()
    rel = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "night_hold.py"), "--orch", str(tmp_path / "orch"),
                          "--wt", str(tmp_path / "wt"), "--now", "2026-11-12T03:31:00", "--release-now"],
                         capture_output=True, text=True, timeout=20)
    assert rel.returncode == 0 and rig.ready() == READY
