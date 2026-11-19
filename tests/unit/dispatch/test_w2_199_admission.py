"""The load admission (W2-199, RT-3): the start threshold, the margin from the runtime log, the room, the log line and the
limits' formulas. A fixture HOME, a planted load file and a planted CPU count; never the machine's own readings."""
from __future__ import annotations

import json
import math
import os
import stat
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import admission, limits  # noqa: E402

GIB = 1024 ** 3


@pytest.fixture
def box(tmp_path, monkeypatch):
    home, bin_ = tmp_path / "home", tmp_path / "bin"
    home.mkdir()
    bin_.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", f"{bin_}:/usr/bin:/bin")
    for name in ("GOV_HEAVY_START_BELOW", "GOV_ADMISSION_POLL_S", "GOV_ADMISSION_SAMPLE_S"):
        monkeypatch.delenv(name, raising=False)
    meminfo, loadavg = tmp_path / "meminfo", tmp_path / "loadavg"
    meminfo.write_text(f"MemTotal: {64 * GIB // 1024} kB\n")
    monkeypatch.setenv("GOV_RESOURCES_MEMINFO", str(meminfo))
    monkeypatch.setenv("GOV_RESOURCES_LOADAVG", str(loadavg))
    monkeypatch.setenv("GOV_RESOURCES_NPROC", "20")
    loadavg.write_text("3.0 3.0 3.0 1/1 1\n")

    def load(value):
        loadavg.write_text(f"{value} {value} {value} 1/1 1\n" if value is not None else "garbage\n")

    def log(*events):
        folder = home / ".gov-os" / "runtime"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "log.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    def gpu(total, used):
        smi = bin_ / "nvidia-smi"
        smi.write_text("#!/bin/sh\ncase \"$1\" in --query-gpu*) echo \"%d, %d, %d, 5\";; esac\nexit 0\n"
                       % (total, used, total - used))
        smi.chmod(smi.stat().st_mode | stat.S_IEXEC)

    return type("Box", (), {"load": staticmethod(load), "log": staticmethod(log), "gpu": staticmethod(gpu),
                            "home": home})


def ended(peak, **extra):
    return {"at": "2026-11-18T00:00:00Z", "event": "ended", "job": "j", "kind": "test", "pid": 1,
            "peak_per_worker": peak, **extra}


def test_the_start_threshold_is_0_6_of_the_cpus_and_the_override_is_absolute(box, monkeypatch):
    assert admission.START_RATIO == 0.6
    assert admission.start_below(20) == 12.0 and admission.start_below(8) == 4.8 and admission.start_below(32) == 19.2
    monkeypatch.setenv("GOV_HEAVY_START_BELOW", "5")
    assert admission.start_below(32) == 5.0
    monkeypatch.setenv("GOV_HEAVY_START_BELOW", "garbage")
    assert admission.start_below(32) == 19.2


def test_no_log_gives_margin_1(box):
    assert admission.margin() == 1.0


def test_margin_is_the_nearest_rank_90th_percentile_of_the_last_20_jobs_and_never_under_1(box):
    box.log(*[ended(v) for v in (1.2, 1.5, 1.8, 2.1, 2.4)])
    assert admission.margin() == 2.4
    box.log(*[ended(0.4) for _ in range(5)])
    assert admission.margin() == 1.0
    box.log(*([ended(9.0)] * 5 + [ended(1.5)] * 20))  # only the last 20 count
    assert admission.margin() == 1.5


def test_a_session_ended_event_without_a_peak_is_no_job(box):
    box.log({"at": "x", "event": "ended", "id": "end:1", "role": "engineer"}, ended(2.0), "not json")
    assert admission.margin() == 2.0


def test_the_log_line_is_one_whole_json_object_with_the_common_fields(box):
    admission.log("ready", "job1", "test", workers=4)
    admission.log("started", "job1", "test", slot=1)
    lines = (box.home / ".gov-os" / "runtime" / "log.jsonl").read_text().splitlines()
    first, second = (json.loads(x) for x in lines)
    assert first["event"] == "ready" and first["job"] == "job1" and first["kind"] == "test"
    assert first["pid"] == os.getpid() and first["workers"] == 4 and first["at"].endswith("Z")
    assert second["slot"] == 1


@pytest.mark.parametrize("load,workers,ok,reason", [(11.9, 4, True, None), (12.0, 4, False, "load"),
                                                    (13.0, 4, False, "load"), (11.0, 10, True, None),
                                                    (3.0, 4, True, None)])
def test_room_holds_a_start_at_or_over_the_threshold_only(box, load, workers, ok, reason):
    box.load(load)
    found, why, readings = admission.room("test", workers)
    assert (found, why) == (ok, reason)
    assert readings["load_1m"] == load and readings["start_below"] == 12.0 and readings["load_limit"] == 20


def test_room_reports_the_measured_margin_and_a_run_that_can_never_fit_is_held_by_the_threshold_alone(box):
    box.load(11.9)
    box.log(*[ended(2.4)] * 3)
    found, why, readings = admission.room("test", 4)  # 4 x 2.4 = 9.6 is over 20 - 12: it can never fit; 11.9 is under 12
    assert (found, why) == (True, None) and readings["margin"] == 2.4
    box.load(12.0)
    assert admission.room("test", 4)[:2] == (False, "load")
    box.load(3.0)
    assert admission.room("test", 20)[0] is True  # an idle machine always admits it


def test_a_wait_has_room_only_for_a_priority_waiter_ahead(box):
    box.load(13.0)
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        if len(slept) == 1:
            box.load(3.0)

    def say(line):
        pass

    admission.wait_for_room("j1", "test", 4, None, say, sleep=sleep)
    taken = iter([None, (1, 5)])
    admission.wait_for_room("j2", "test", 4, None, say, take=lambda: next(taken), sleep=lambda s: None)
    holds = iter([("priority", "a landing waits first"), None])
    admission.wait_for_room("j3", "test", 4, None, say, gate=lambda: next(holds), take=lambda: (1, 5),
                            sleep=lambda s: None)
    waits = {e["job"]: (e["reason"], e["room"]) for e in
             (json.loads(x) for x in (box.home / ".gov-os" / "runtime" / "log.jsonl").read_text().splitlines())
             if e["event"] == "wait"}
    assert waits == {"j1": ("load", False), "j2": ("slots", False), "j3": ("priority", True)}


def test_an_unreadable_load_opens_and_says_why(box):
    box.load(None)
    found, why, readings = admission.room("test", 4)
    assert found is True and why is None and "load" in readings["problem"]


def test_the_gpu_kinds_follow_the_gpu_answer(box):
    box.load(3.0)
    box.gpu(24576, 20000)  # the budget is 21,504 MiB
    assert admission.room("embedder", 1, 1504)[:2] == (True, None)
    ok, why, readings = admission.room("embedder", 1, 1505)
    assert (ok, why) == (False, "gpu") and "over the GPU budget" in readings["gpu_reason"]


def test_no_gpu_is_a_refusal_never_the_cpu(box):
    ok, why, readings = admission.room("reranker", 1, 500)
    assert ok is False and why == "refused" and "memory is unavailable" in readings["gpu_reason"]
    assert "cpu" not in readings["gpu_reason"].lower()


@pytest.mark.parametrize("cpus,ram,slots,workers", [(8, 16, 1, 3), (32, 64, 3, 4), (20, 64, 2, 4)])
def test_slots_and_workers_follow_the_gate(cpus, ram, slots, workers):
    found = limits.derive(cpus, ram * GIB, None, {})
    assert (found["heavy_slots"], found["workers_per_slot"]) == (slots, workers)
    assert found["start_below"] == pytest.approx(0.6 * cpus) and found["load_limit"] == cpus


def test_the_ram_term_binds_the_slots(box):
    found = limits.derive(32, 64 * GIB, None, {"verification_peak_bytes": 16 * GIB})
    assert found["heavy_slots"] == 2 and found["workers_per_slot"] == 6


@pytest.mark.parametrize("m", [1.0, 1.5, 2.0])
def test_the_invariant_holds_for_every_cpu_count(m):
    for cpus in range(4, 65):
        found = limits.derive(cpus, 1024 * GIB, None, {}, margin=m)
        if found["workers_per_slot"] > 1:  # the floor of one worker is the formula's own (max(1, ...))
            assert found["start_below"] + found["heavy_slots"] * found["workers_per_slot"] * m <= found["load_limit"], \
                (cpus, m, found)


def test_a_heavier_margin_shrinks_the_workers():
    plain = limits.derive(32, 64 * GIB, None, {})["workers_per_slot"]
    heavy = limits.derive(32, 64 * GIB, None, {}, margin=2.4)["workers_per_slot"]
    assert heavy < plain


def test_the_override_sets_start_below_in_the_limits(box, monkeypatch):
    monkeypatch.setenv("GOV_RESOURCES_NPROC", "32")
    assert limits.detect()["limits"]["start_below"] == 19.2
    monkeypatch.setenv("GOV_HEAVY_START_BELOW", "5")
    assert limits.detect()["limits"]["start_below"] == 5.0
