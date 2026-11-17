"""``gov dispatch watch`` and ``gov dispatch limits`` (W2-121c): machine-wide, no project and no dispatch.yaml."""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture
def run(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(f"MemTotal: {16 * 1024 * 1024} kB\n")
    env = dict(os.environ, HOME=str(home), PYTHONPATH=str(REPO / "src"), PATH="/usr/bin:/bin",
               GOV_RESOURCES_NPROC="8", GOV_RESOURCES_MEMINFO=str(meminfo))

    def gov(*argv):
        return subprocess.run([sys.executable, "-m", "gov.cli.main", "dispatch", *argv], env=env, cwd=tmp_path,
                              capture_output=True, text=True, timeout=60)
    gov.home = home
    return gov


def test_limits_prints_each_limit_with_its_rule(run):
    done = run("limits")
    assert done.returncode == 0, done.stderr
    for word in ("heavy_slots", "workers_per_slot", "sessions_max", "gpu_budget_mib", "floor(0.15 x CPUs)"):
        assert word in done.stdout
    result = json.loads(run("limits", "--json").stdout)["result"]
    assert result["limits"]["sessions_max"] == 4 and result["machine"]["cpus"] == 8


def test_a_gpu_need_with_no_gpu_is_refused(run):
    done = run("limits", "--gpu-need-mib", "500")
    assert done.returncode == 3 and done.stdout.startswith("refuse")
    assert "memory is unavailable" in done.stdout and "cpu" not in done.stdout.lower()


def test_watch_runs_one_pass_and_a_held_lock_exits_4(run):
    done = run("watch")
    assert done.returncode == 0, done.stderr
    folder = run.home / ".gov-os" / "runtime"
    fd = os.open(folder, os.O_RDONLY)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        assert run("watch").returncode == 4
    finally:
        os.close(fd)
