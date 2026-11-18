"""The limits from the machine detected at the pass (W2-121c, RT-3): ratios only, and the GPU never spills."""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import limits  # noqa: E402

GIB, MIB = 1024 ** 3, 1024 ** 2


@pytest.fixture
def box(tmp_path, monkeypatch):
    home, bin_ = tmp_path / "home", tmp_path / "bin"
    home.mkdir()
    bin_.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", f"{bin_}:/usr/bin:/bin")

    def profile(cpus, ram_gib, gpu_total=None, gpu_used=0, smi_exit=0):
        monkeypatch.setenv("GOV_RESOURCES_NPROC", str(cpus))
        meminfo = tmp_path / "meminfo"
        meminfo.write_text(f"MemTotal: {ram_gib * GIB // 1024} kB\nMemAvailable: 1000 kB\n")
        monkeypatch.setenv("GOV_RESOURCES_MEMINFO", str(meminfo))
        smi = bin_ / "nvidia-smi"
        if gpu_total is None:
            smi.unlink(missing_ok=True)
            return
        smi.write_text("#!/bin/sh\ncase \"$1\" in --query-gpu*) echo \"%d, %d, %d, 5\";; esac\nexit %d\n"
                       % (gpu_total, gpu_used, gpu_total - gpu_used, smi_exit))
        smi.chmod(smi.stat().st_mode | stat.S_IEXEC)

    def gate(**values):
        folder = home / ".gov-os" / "machine"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "gate.json").write_text(json.dumps(
            {k: {"value": v, "date": "2026-11-17", "source": "test"} for k, v in values.items()}))

    return type("Box", (), {"profile": staticmethod(profile), "gate": staticmethod(gate)})


def test_the_limits_follow_their_rules_on_two_profiles(box):
    box.profile(32, 64, 24576)
    big = limits.detect()
    assert big["machine"]["cpus"] == 32 and big["machine"]["ram_bytes"] == 64 * GIB
    assert big["limits"] == {"heavy_slots": 4, "workers_per_slot": 7, "sessions_max": 16, "gpu_budget_mib": 21504}
    box.profile(8, 16, 8192)
    small = limits.detect()
    assert small["limits"] == {"heavy_slots": 1, "workers_per_slot": 7, "sessions_max": 4, "gpu_budget_mib": 7168}


def test_a_measured_peak_binds_where_smaller(box):
    box.profile(32, 64, 24576)
    box.gate(verification_peak_bytes=16 * GIB, working_size_bytes=8 * GIB)
    found = limits.detect()["limits"]
    assert found["heavy_slots"] == 2 and found["sessions_max"] == 4
    assert found["workers_per_slot"] == 14


def test_no_gpu_budget_is_zero_and_not_a_problem(box):
    box.profile(8, 16)
    found = limits.detect()
    assert found["limits"]["gpu_budget_mib"] == 0 and found["problems"] == []


def test_a_failing_nvidia_smi_is_a_problem(box):
    box.profile(8, 16, 8192, smi_exit=9)
    assert any("nvidia-smi" in p for p in limits.detect()["problems"])


@pytest.mark.parametrize("used,need,answer", [(1000, 2000, "admit"), (6000, 2000, "wait")])
def test_the_gpu_answer(box, used, need, answer):
    box.profile(8, 16, 8192, gpu_used=used)
    verdict, reason = limits.gpu_answer(limits.detect(), need)
    assert verdict == answer and "cpu" not in reason.lower()


def test_no_gpu_refuses_and_says_memory_is_unavailable(box):
    box.profile(8, 16)
    verdict, reason = limits.gpu_answer(limits.detect(), 100)
    assert verdict == "refuse" and "memory is unavailable" in reason and "cpu" not in reason.lower()


def test_no_machine_figure_in_the_module():
    text = (REPO / "src/gov/dispatch/limits.py").read_text()
    for figure in ("24576", "8192", "65536", "1024 ** 3 *", "nproc() or 20"):
        assert figure not in text
