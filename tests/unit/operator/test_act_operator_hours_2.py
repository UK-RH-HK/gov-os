"""ACT-OPERATOR-HOURS-2 (DEC-1141 (6)), revised by ACT-OPERATOR-HOURS-3 (DEC-1157 (2)): G9 has no time hold.

The night hold is removed (DEC-1157 (2)), so G9 no longer holds from 02:10 to 03:09, nor from 03:10 to 07:59 on the night
hold's state file (log/night-hold.state.json); the file is not read at any hour, whatever it holds (true, false, missing,
stale, malformed, a directory). Every other hold is as before, at every hour, the night included: the NIGHTLY-RUNNING
flag, an explicit nightly_window, the close queue, the CTO's and the operator's act-in-progress.txt, a clock that cannot
be read. Everything on planted folders (test_w2_148_kit). The file keeps its name: it is the one unit file for G9's hours."""
import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, OPDIR, Kit, write  # noqa: E402

sys.path.insert(0, str(OPDIR))
sys.dont_write_bytecode = True
import opcommon  # noqa: E402

NIGHT = ["00:00", "01:30", "02:05", "02:09", "02:10", "02:15", "02:30", "02:59", "03:00", "03:09", "03:10", "03:30",
         "04:00", "05:10", "05:30", "07:29", "07:30", "07:45", "07:59", "08:00", "08:01", "14:00", "23:59"]
STATES = ["true", "false", "missing", "stale-true", "stale-false", "malformed", "empty", "strfalse", "dir"]


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def settings(kit, **over):
    conf = json.loads(kit.config.read_text())
    conf.pop("nightly_window", None)             # the kit names the old window; the default is none
    conf.update(over)
    kit.config.write_text(json.dumps(conf))
    return opcommon.load_settings(str(kit.config))


def state_file(kit):
    return kit.scratch / "log/night-hold.state.json"


def plant(kit, holding, age_s=5, raw=None):
    p = state_file(kit)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raw if raw is not None else json.dumps({"pid": 1, "at": "x", "holding": holding, "in_window": True,
                                                         "nightly": "n"}))
    t = time.time() - age_s
    os.utime(p, (t, t))
    return p


def plant_state(kit, state):
    if state == "true":
        plant(kit, True)
    elif state == "false":
        plant(kit, False)
    elif state == "stale-true":
        plant(kit, True, age_s=3600)
    elif state == "stale-false":
        plant(kit, False, age_s=3600)
    elif state == "malformed":
        plant(kit, None, raw="{not json")
    elif state == "empty":
        plant(kit, None, raw="")
    elif state == "strfalse":
        plant(kit, None, raw='{"holding": "false"}')
    elif state == "dir":
        state_file(kit).mkdir(parents=True)


def at(kit, hm):
    kit.set_clock(f"{DAY}T{hm}:00+00:00")


def hold_reasons(kit, hm, **over):
    s = settings(kit, **over)
    at(kit, hm)
    return opcommon.holds(s)


# ------------------------------------------------------------------------------------------------ the code's shape
def test_the_night_hold_constants_reader_and_settings_are_gone(kit):
    s = opcommon.load_settings(str(kit.config))
    assert "night_hold_state" not in s and "night_hold_max_age_s" not in s
    for name in ("HOLD_FROM", "HOLD_READ_FROM", "HOLD_END", "NIGHT_HOLD_MAX_AGE_S", "night_hold_reasons", "QUIET"):
        assert not hasattr(opcommon, name), name
    assert opcommon.DEFAULT_NIGHTLY is None


# ------------------------------------------------------------------------------------------------ no time hold at any hour
@pytest.mark.parametrize("hm", NIGHT)
@pytest.mark.parametrize("state", STATES)
def test_no_time_hold_at_any_hour_whatever_the_night_hold_file_holds(kit, hm, state):
    plant_state(kit, state)
    assert hold_reasons(kit, hm) == []


@pytest.mark.parametrize("hm", ["02:30", "05:10", "14:00"])
def test_no_time_hold_with_no_night_hold_file_at_all(kit, hm):
    assert not state_file(kit).exists()
    assert hold_reasons(kit, hm) == []


def test_the_night_hold_file_is_not_opened(kit, monkeypatch):
    """holds() never stats or opens the night hold's state file, at night or by day."""
    p = str(plant(kit, True))
    seen = []
    real_open, real_stat = open, os.stat

    def spy_open(f, *a, **k):
        seen.append(str(f))
        return real_open(f, *a, **k)

    def spy_stat(f, *a, **k):
        seen.append(str(f))
        return real_stat(f, *a, **k)

    s = settings(kit)
    monkeypatch.setattr("builtins.open", spy_open)
    monkeypatch.setattr(os, "stat", spy_stat)
    for hm in ("02:30", "05:10", "14:00"):
        at(kit, hm)
        assert opcommon.holds(s) == []
    assert p not in seen and not [f for f in seen if f.endswith("night-hold.state.json")]


# ------------------------------------------------------------------------------------------------ the other holds stay, the night included
@pytest.mark.parametrize("hm", ["02:30", "05:10", "08:30", "14:00"])
def test_a_fresh_nightly_flag_holds_at_night_and_by_day(kit, hm):
    write(kit.scratch / "NIGHTLY-RUNNING", "2026-11-10 04:00:05 nightly: running\n")
    why = hold_reasons(kit, hm)
    assert why == ["the nightly runs (NIGHTLY-RUNNING)"], why


def test_a_nightly_flag_older_than_six_hours_does_not_hold(kit):
    f = write(kit.scratch / "NIGHTLY-RUNNING", "old\n")
    t = time.time() - 7 * 3600
    os.utime(f, (t, t))
    assert hold_reasons(kit, "05:10") == []


@pytest.mark.parametrize("name,make,phrase", [
    ("close", lambda k: write(k.scratch / "CLOSE-RUNNING", "x\n"), "a close queue runs"),
    ("cto", lambda k: write(k.scratch / "log/act-in-progress.txt", "x\n"), "the CTO's log/act-in-progress.txt exists"),
    ("freeze", lambda k: write(k.install / "act-in-progress.txt", "x\n"), "the commit freeze install/act-in-progress.txt")])
def test_the_other_holds_stay_at_every_hour(kit, name, make, phrase):
    make(kit)
    for hm in ("01:30", "02:30", "05:10", "14:00"):
        why = hold_reasons(kit, hm)
        assert len(why) == 1 and phrase in why[0], (name, hm, why)


def test_an_explicit_nightly_window_still_holds_and_there_is_none_by_default(kit):
    assert hold_reasons(kit, "05:10") == []                          # the old default 03:50-08:00 is gone
    why = hold_reasons(kit, "21:30", nightly_window="21:00-22:00")
    assert why == ["the nightly's window (21:00-22:00)"]
    assert hold_reasons(kit, "22:30", nightly_window="21:00-22:00") == []
    why = hold_reasons(kit, "05:10", nightly_window="03:50-08:00")   # a window set at night holds at night
    assert why == ["the nightly's window (03:50-08:00)"]


def test_a_clock_that_cannot_be_read_still_holds(kit):
    s = settings(kit)
    write(kit.clock, "not a time\n")
    assert any("clock cannot be read" in w for w in opcommon.holds(s))


# ------------------------------------------------------------------------------------------------ the launcher and the run
@pytest.mark.parametrize("hm,state", [("02:30", "missing"), ("02:30", "false"), ("05:30", "true"), ("05:30", "stale-false")])
def test_the_launcher_goes_on_at_night(kit, hm, state):
    settings(kit)
    msha = kit.bundle("ACT-HR3-L", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    write(kit.root / "queue/one.req", f"ACT-HR3-L {msha}\n")
    at(kit, hm)
    plant_state(kit, state)
    rc, res, _ = kit.launch()
    assert res.get("gate") != "G9" and res["result"] != "held", res          # no hold: the launcher takes the request
    assert not (kit.root / "queue/one.req").exists()


def test_the_launcher_holds_at_0530_while_the_nightly_flag_is_fresh(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR3-M", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    write(kit.root / "queue/one.req", f"ACT-HR3-M {msha}\n")
    at(kit, "05:30")
    plant(kit, False)
    write(kit.scratch / "NIGHTLY-RUNNING", "2026-11-10 04:00:05 nightly: running\n")
    rc, res, _ = kit.launch()
    assert res["result"] == "held" and res["gate"] == "G9" and "NIGHTLY-RUNNING" in res["reason"], res
    assert (kit.root / "queue/one.req").exists()


@pytest.mark.parametrize("hm,state", [("02:15", "false"), ("05:30", "true"), ("05:30", "missing")])
def test_a_run_at_night_applies_without_a_g9_hold(kit, hm, state):
    settings(kit, hold_max_s=1)
    msha = kit.bundle("ACT-HR3-N", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, hm)
    plant_state(kit, state)
    rc, res, _ = kit.run("run", "ACT-HR3-N", msha)
    assert res["result"] == "applied", res
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["pass"]
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"


def test_a_run_waits_at_g9_while_the_nightly_runs_and_applies_once_it_ends(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR3-R", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, "05:30")
    flag = write(kit.scratch / "NIGHTLY-RUNNING", "2026-11-10 04:00:05 nightly: running\n")
    threading.Timer(2.0, flag.unlink).start()
    rc, res, _ = kit.run("run", "ACT-HR3-R", msha)
    assert res["result"] == "applied", res
    g9 = [e for e in kit.log() if e["gate"] == "G9"]
    assert [e["result"] for e in g9] == ["held", "pass"] and "the nightly runs (NIGHTLY-RUNNING)" in g9[0]["why"]
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"


def test_a_run_goes_through_at_0130_with_no_file_at_all(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR3-D", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, "01:30")
    rc, res, _ = kit.run("run", "ACT-HR3-D", msha)
    assert res["result"] == "applied", res
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["pass"]
