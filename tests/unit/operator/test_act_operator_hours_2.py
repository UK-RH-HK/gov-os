"""ACT-OPERATOR-HOURS-2 (DEC-1141 (6)): G9 holds only while the night hold is on, not for fixed hours.

From 02:10 to 03:09 G9 holds (no session starts that could run into the hold); from 03:10 to 07:59 it holds unless the
night hold's state file (log/night-hold.state.json) is under 300 s old and its "holding" is exactly false; at every other
hour there is no time hold and the file is not read. The same rule and the same fail-closed reading as the crontab's
guard (ACT-OPERATOR-HOURS-1). Every other hold (NIGHTLY-RUNNING, the close queue, the CTO's and the operator's
act-in-progress.txt, an explicit nightly_window) is as before. Everything on planted folders (test_w2_148_kit)."""
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

ORIG = b"one\ntwo\nthree\n"


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def settings(kit, **over):
    conf = json.loads(kit.config.read_text())
    conf.pop("nightly_window", None)             # the kit names the old window; the new default is none
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


def at(kit, hm):
    kit.set_clock(f"{DAY}T{hm}:00+00:00")


def hold_reasons(kit, hm, **over):
    s = settings(kit, **over)
    at(kit, hm)
    return opcommon.holds(s)


# ------------------------------------------------------------------------------------------------ the default setting
def test_the_state_file_defaults_to_the_ctos_scratch_and_the_old_constants_are_gone(kit):
    s = opcommon.load_settings(str(kit.config))
    assert s["night_hold_state"] == str(kit.scratch / "log/night-hold.state.json")
    assert s["night_hold_max_age_s"] == 300.0
    assert not hasattr(opcommon, "QUIET") and opcommon.DEFAULT_NIGHTLY is None


# ------------------------------------------------------------------------------------------------ every hour but the hold
@pytest.mark.parametrize("hm", ["00:00", "01:30", "02:05", "02:09", "08:00", "08:01", "14:00", "23:59"])
@pytest.mark.parametrize("state", ["true", "false", "missing", "malformed"])
def test_no_time_hold_outside_0210_to_0759_and_the_file_is_not_read(kit, hm, state):
    if state == "true":
        plant(kit, True)
    elif state == "false":
        plant(kit, False)
    elif state == "malformed":
        plant(kit, None, raw="{not json")
    assert hold_reasons(kit, hm) == []


def test_a_days_old_true_does_not_hold_in_the_day(kit):
    plant(kit, True, age_s=86400)
    assert hold_reasons(kit, "14:00") == [] and hold_reasons(kit, "08:00") == [] and hold_reasons(kit, "01:30") == []


@pytest.mark.parametrize("hm", ["02:10", "02:30", "02:59", "03:09"])
@pytest.mark.parametrize("holding", [True, False])
def test_0210_to_0309_always_holds(kit, hm, holding):
    plant(kit, holding)
    why = hold_reasons(kit, hm)
    assert len(why) == 1 and "before the night hold" in why[0]


def test_0210_to_0309_holds_with_no_state_file_too(kit):
    assert [("before the night hold" in w) for w in hold_reasons(kit, "02:40")] == [True]


# ------------------------------------------------------------------------------------------------ 03:10 to 07:59
@pytest.mark.parametrize("hm", ["03:10", "03:30", "05:10", "07:30", "07:45", "07:59"])
def test_a_fresh_false_releases_from_0310(kit, hm):
    plant(kit, False)
    assert hold_reasons(kit, hm) == []


@pytest.mark.parametrize("hm", ["03:10", "03:30", "05:10", "07:45", "07:59"])
def test_a_fresh_true_holds(kit, hm):
    plant(kit, True)
    assert hold_reasons(kit, hm) == ["the night hold is on"]


@pytest.mark.parametrize("raw", ["", "{not json", "[false]", "{}", '{"holding": null}', '{"holding": 0}',
                                 '{"holding": "false"}', '{"holding": "true"}', '{"holding": 1}', "false", "null"])
def test_an_unreadable_or_odd_file_holds(kit, raw):
    plant(kit, None, raw=raw)
    assert hold_reasons(kit, "05:10") != []


def test_a_missing_file_holds(kit):
    why = hold_reasons(kit, "05:10")
    assert len(why) == 1 and "cannot be read" in why[0] and "FileNotFoundError" in why[0]


def test_a_directory_in_its_place_holds(kit):
    state_file(kit).mkdir(parents=True)
    assert hold_reasons(kit, "05:10") != []


@pytest.mark.parametrize("age,held", [(5, False), (299, False), (301, True), (400, True), (3600, True)])
def test_a_stale_false_holds_past_300_seconds(kit, age, held):
    plant(kit, False, age_s=age)
    why = hold_reasons(kit, "05:10")
    assert (why != []) is held
    if held:
        assert "stale" in why[0]


def test_the_age_is_a_setting(kit):
    plant(kit, False, age_s=100)
    assert hold_reasons(kit, "05:10", night_hold_max_age_s=60) != []
    assert hold_reasons(kit, "05:10", night_hold_max_age_s=200) == []


def test_the_state_path_is_a_setting(kit):
    other = write(kit.root / "elsewhere.json", json.dumps({"holding": False}))
    assert hold_reasons(kit, "05:10") != []                           # the default path has no file
    assert hold_reasons(kit, "05:10", night_hold_state=str(other)) == []


def test_the_state_changing_is_read_afresh_each_time(kit):
    s = settings(kit)
    at(kit, "03:30")
    plant(kit, True)
    assert opcommon.holds(s) == ["the night hold is on"]
    plant(kit, False)
    assert opcommon.holds(s) == []
    plant(kit, True)
    assert opcommon.holds(s) == ["the night hold is on"]


# ------------------------------------------------------------------------------------------------ the other holds stay
def test_a_fresh_nightly_flag_still_holds_after_the_release_and_at_any_hour(kit):
    plant(kit, False)
    write(kit.scratch / "NIGHTLY-RUNNING", "2026-11-10 04:00:05 nightly: running\n")
    for hm in ("05:10", "08:30", "14:00"):
        assert any("NIGHTLY-RUNNING" in w for w in hold_reasons(kit, hm)), hm


@pytest.mark.parametrize("name,make", [("close", lambda k: write(k.scratch / "CLOSE-RUNNING", "x\n")),
                                       ("cto", lambda k: write(k.scratch / "log/act-in-progress.txt", "x\n")),
                                       ("freeze", lambda k: write(k.install / "act-in-progress.txt", "x\n"))])
def test_the_other_holds_stay_at_every_hour(kit, name, make):
    plant(kit, False)
    make(kit)
    for hm in ("01:30", "05:10", "14:00"):
        assert hold_reasons(kit, hm) != [], (name, hm)


def test_an_explicit_nightly_window_still_holds_and_there_is_none_by_default(kit):
    plant(kit, False)
    assert hold_reasons(kit, "05:10") == []                          # the old default 03:50-08:00 is gone
    why = hold_reasons(kit, "21:30", nightly_window="21:00-22:00")
    assert why and "nightly's window (21:00-22:00)" in why[0]
    assert hold_reasons(kit, "22:30", nightly_window="21:00-22:00") == []


def test_a_clock_that_cannot_be_read_still_holds(kit):
    s = settings(kit)
    write(kit.clock, "not a time\n")
    assert any("clock cannot be read" in w for w in opcommon.holds(s))


# ------------------------------------------------------------------------------------------------ the launcher and the run
def test_the_launcher_goes_on_at_0130_and_holds_at_0230(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR2-L", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    write(kit.root / "queue/one.req", f"ACT-HR2-L {msha}\n")
    at(kit, "02:30")
    rc, res, _ = kit.launch()
    assert res["result"] == "held" and res["gate"] == "G9" and "before the night hold" in res["reason"], res
    assert (kit.root / "queue/one.req").exists()
    at(kit, "01:30")
    rc, res, _ = kit.launch()
    assert res.get("gate") != "G9" and res["result"] != "held", res          # no hold: the launcher takes the request


def test_the_launcher_holds_at_0530_on_a_true_and_goes_on_after_the_release(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR2-M", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    write(kit.root / "queue/one.req", f"ACT-HR2-M {msha}\n")
    at(kit, "05:30")
    plant(kit, True)
    rc, res, _ = kit.launch()
    assert res["result"] == "held" and "the night hold is on" in res["reason"], res
    plant(kit, False)
    rc, res, _ = kit.launch()
    assert res["result"] != "held", res


def test_a_run_waits_at_g9_in_the_hold_and_applies_once_the_hold_is_released(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR2-R", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, "05:30")
    plant(kit, True)
    threading.Timer(2.0, plant, args=(kit, False)).start()
    rc, res, _ = kit.run("run", "ACT-HR2-R", msha)
    assert res["result"] == "applied", res
    g9 = [e for e in kit.log() if e["gate"] == "G9"]
    assert [e["result"] for e in g9] == ["held", "pass"] and "the night hold is on" in g9[0]["why"]
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"


def test_a_run_that_reaches_g9_at_0215_waits_and_does_not_apply(kit):
    """A session begun before 02:10 that is still at G9 after it holds (G9 is read again at the gate, not only by the launcher)."""
    settings(kit, hold_max_s=1)
    msha = kit.bundle("ACT-HR2-Q", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, "02:15")
    plant(kit, False)
    rc, res, _ = kit.run("run", "ACT-HR2-Q", msha)
    assert res["gate"] == "G9" and "outlasted" in res["reason"], res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == ORIG


def test_a_run_goes_through_at_0130_with_no_file_at_all(kit):
    settings(kit)
    msha = kit.bundle("ACT-HR2-N", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    at(kit, "01:30")
    rc, res, _ = kit.run("run", "ACT-HR2-N", msha)
    assert res["result"] == "applied", res
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["pass"]
