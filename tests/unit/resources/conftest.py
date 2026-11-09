"""A planted machine for the resource gate's unit tests (W2-20): a temporary HOME, planted readings (the interface's
``GOV_RESOURCES_*`` variables), a planted process table and a PATH with no real ``nvidia-smi``; never the real
``~/.gov-os/``, the real servers or the GPU."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.resources import config as configuration  # noqa: E402

GIB = 1024 ** 3
SMI = """#!{python}
import json, os, sys
with open(os.environ["SMI_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
if os.environ.get("SMI_EXIT"):
    print(os.environ.get("SMI_SAY", ""))
    sys.exit(int(os.environ["SMI_EXIT"]))
if any(a.startswith("--query-gpu") for a in sys.argv):
    print(os.environ.get("SMI_GPU", "8000, 1000, 7000, 5"))
elif any(a.startswith("--query-compute-apps") for a in sys.argv):
    print(os.environ.get("SMI_APPS", ""))
"""


class Machine:
    def __init__(self, root: Path, monkeypatch):
        self.root, self.mp = root, monkeypatch
        self.home = root / "home"
        self.home.mkdir()
        self.proc = root / "proc"
        self.proc.mkdir()
        self.bin = root / "bin"
        self.bin.mkdir()
        self.dir = self.home / ".gov-os" / "machine"
        monkeypatch.setenv("HOME", str(self.home))
        monkeypatch.setenv("GOV_RESOURCES_PROC", str(self.proc))
        monkeypatch.setenv("PATH", f"{self.bin}:{os.path.dirname(sys.executable)}:/usr/bin:/bin")
        for name in ("GOV_RESOURCES_NPROC", "GOV_RESOURCES_STAT", "OLLAMA_HOST", "GOV_QUERY_OLLAMA_HOST"):
            monkeypatch.delenv(name, raising=False)
        self.memory(available=20 * GIB)
        self.loads(1.0, 1.0)
        self.nproc(20)
        self.busy(2.0)
        self.servers(0.5, 0.5)
        self.servers_now(0.0, 0.0)  # idle now: their whole p95 is headroom (round 7)
        self.disk(500 * GIB, 50_000_000)

    # readings
    def memory(self, available: int):
        path = self.root / "meminfo"
        path.write_text(f"MemTotal: {32 * GIB // 1024} kB\nMemFree: 1 kB\nMemAvailable: {available // 1024} kB\n")
        self.mp.setenv("GOV_RESOURCES_MEMINFO", str(path))

    def loads(self, one: float, fifteen: float):
        path = self.root / "loadavg"
        path.write_text(f"{one} 0.5 {fifteen} 1/100 12345\n")
        self.mp.setenv("GOV_RESOURCES_LOADAVG", str(path))

    def nproc(self, count: int):
        self.count = count
        self.mp.setenv("GOV_RESOURCES_NPROC", str(count))

    def busy(self, cores):
        self.mp.setenv("GOV_RESOURCES_BUSY_CORES", str(cores))

    def servers(self, shared, query):
        self.mp.setenv("GOV_RESOURCES_EMBEDDING_CPU", json.dumps({"shared": shared, "query": query}))

    def servers_now(self, shared, query):
        self.mp.setenv("GOV_RESOURCES_EMBEDDING_CPU_NOW", json.dumps({"shared": shared, "query": query}))

    def disk(self, free: int, inodes: int):
        self.mp.setenv("GOV_RESOURCES_DISK", json.dumps({"free_bytes": free, "free_inodes": inodes}))

    def smi(self, gpu: str | None = None, apps: str | None = None, exit_code: int | None = None, say: str = ""):
        """A stand-in ``nvidia-smi`` on PATH; returns a reader of its calls."""
        program = self.bin / "nvidia-smi"
        program.write_text(SMI.format(python=sys.executable))
        program.chmod(0o755)
        log = self.root / "smi.log"
        self.mp.setenv("SMI_LOG", str(log))
        for name, value in (("SMI_GPU", gpu), ("SMI_APPS", apps), ("SMI_EXIT", exit_code)):
            if value is None:
                self.mp.delenv(name, raising=False)
            else:
                self.mp.setenv(name, str(value))
        self.mp.setenv("SMI_SAY", say)
        return lambda: [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    # processes
    def process(self, pid: int, ppid: int = 1, rss: int = 0, cmdline: str = "proc", ticks: int = 0):
        folder = self.proc / str(pid)
        folder.mkdir(exist_ok=True)
        (folder / "stat").write_text(f"{pid} ({cmdline.split()[0]}) S {ppid} 0 0 0 0 0 0 0 0 0 {ticks} 0 0 0\n")
        (folder / "statm").write_text(f"0 {rss // page()} 0 0 0 0 0\n")
        (folder / "cmdline").write_bytes(cmdline.replace(" ", "\0").encode() + b"\0")

    def gone(self, pid: int):
        import shutil
        shutil.rmtree(self.proc / str(pid), ignore_errors=True)

    # configuration
    def config(self, **changes):
        data = configuration.template(cpus=list(range(20)))
        for key, value in changes.items():
            if value is None:
                data.pop(key, None)
            elif key == configuration.SERVERS_KEY or (isinstance(value, dict) and "value" in value):
                data[key] = value
            else:
                data.setdefault(key, {"date": "", "source": "test"})
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


def page() -> int:
    from gov.resources import machine
    return machine.PAGE


@pytest.fixture
def planted(tmp_path, monkeypatch):
    return Machine(tmp_path, monkeypatch)
