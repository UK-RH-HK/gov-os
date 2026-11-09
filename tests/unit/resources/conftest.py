"""A planted machine for the resource gate's unit tests (W2-20): a temporary HOME, planted /proc files, a planted
process table, a planted CPU history; never the real ``~/.gov-os/``, the real servers or the GPU."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.resources import config as configuration  # noqa: E402

GIB = 1024 ** 3


class Machine:
    def __init__(self, root: Path, monkeypatch):
        self.root, self.mp = root, monkeypatch
        self.home = root / "home"
        self.home.mkdir()
        self.proc = root / "proc"
        self.proc.mkdir()
        self.dir = self.home / ".gov-os" / "machine"
        monkeypatch.setenv("HOME", str(self.home))
        monkeypatch.setenv("GOV_RESOURCES_PROC", str(self.proc))
        monkeypatch.setenv("GOV_RESOURCES_NVIDIA_SMI", str(root / "no-nvidia-smi"))
        monkeypatch.delenv("GOV_RESOURCES_NPROC", raising=False)
        self.memory(available=20 * GIB)
        self.loads(1.0, 1.0, 1.0)
        self.nproc(20)
        self.busy(2.0)

    # readings
    def memory(self, available: int, total: int = 32 * GIB):
        path = self.root / "meminfo"
        path.write_text(f"MemTotal: {total // 1024} kB\nMemFree: 1 kB\nMemAvailable: {available // 1024} kB\n")
        self.mp.setenv("GOV_RESOURCES_MEMINFO", str(path))

    def loads(self, one: float, five: float, fifteen: float):
        path = self.root / "loadavg"
        path.write_text(f"{one} {five} {fifteen} 1/100 12345\n")
        self.mp.setenv("GOV_RESOURCES_LOADAVG", str(path))

    def nproc(self, count: int):
        self.count = count
        self.mp.setenv("GOV_RESOURCES_NPROC", str(count))

    def busy(self, cores: float, window_s: float = 61.0):
        """Plant /proc/stat and a CPU history sample ``window_s`` ago so the last minute shows ``cores`` busy."""
        total = 100 * self.count * int(window_s)
        busy = int(round(total * cores / self.count))
        stat = self.root / "stat"
        stat.write_text(f"cpu  {busy + 1000} 0 0 {total - busy + 5000} 0 0 0 0 0 0\ncpu0 1 0 0 1 0 0 0 0\n")
        self.mp.setenv("GOV_RESOURCES_STAT", str(stat))
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "cpu-stat.json").write_text(json.dumps([{"t": time.time() - window_s, "busy": 1000,
                                                             "total": 6000}]))

    # processes
    def process(self, pid: int, ppid: int = 1, rss: int = 0, cmdline: str = "proc", ticks: int = 0):
        folder = self.proc / str(pid)
        folder.mkdir(exist_ok=True)
        (folder / "stat").write_text(f"{pid} ({cmdline.split()[0]}) S {ppid} 0 0 0 0 0 0 0 0 0 {ticks} 0 0 0\n")
        (folder / "statm").write_text(f"0 {rss // configuration_page()} 0 0 0 0 0\n")
        (folder / "cmdline").write_bytes(cmdline.replace(" ", "\0").encode() + b"\0")

    def gone(self, pid: int):
        import shutil
        shutil.rmtree(self.proc / str(pid), ignore_errors=True)

    # configuration
    def config(self, **changes):
        data = configuration.template(cpus=list(range(20)), home=str(self.home))
        data["disk_floor_bytes"]["value"] = 0
        data["inode_floor"]["value"] = 0
        for key, value in changes.items():
            if value is None:
                data.pop(key, None)
            elif isinstance(value, dict) and ("value" in value or key == configuration.SERVERS_KEY):
                data[key] = value
            else:
                data[key]["value"] = value
                data[key]["date"] = time.strftime("%Y-%m-%d")
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "gate.json").write_text(json.dumps(data))
        return data

    def session(self, pid: int, ticket: str = "DAEO-x", role: str = "engineer", repository: str | None = None):
        folder = self.dir / "sessions"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{pid}.json").write_text(json.dumps({"pid": pid, "repository": repository or str(self.root),
                                                        "ticket": ticket, "role": role}))


def configuration_page() -> int:
    from gov.resources import machine
    return machine.PAGE


@pytest.fixture
def planted(tmp_path, monkeypatch):
    return Machine(tmp_path, monkeypatch)
