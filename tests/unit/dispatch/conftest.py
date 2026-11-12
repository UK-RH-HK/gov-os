"""A planted machine and project for the dispatcher's unit tests (W2-121 part a): a git project with an integration
branch and ticket worktrees, a temporary HOME with the gate's ``gate.json``, the ``GOV_RESOURCES_*`` readings, a planted
``/proc`` folder, a stub launch command and a stub notifier; never the real HOME, a real session or the crontab."""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.resources import config as gate_config  # noqa: E402

GIB = 1024 ** 3
BRANCH = "integ"
GIT_ENV = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "T",
           "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}

STUB_LAUNCH = """import os, sys
with open(os.environ["STUB_LAUNCH_LOG"], "a") as log:
    log.write(" ".join(sys.argv[1:]) + " | " + sys.stdin.read().strip() + " | " + os.getcwd() + "\\n")
print("status: DONE")
sys.exit(int(os.environ.get("STUB_LAUNCH_EXIT", "0")))
"""
STUB_NOTIFY = """import os, sys
with open(os.environ["STUB_NOTIFY_LOG"], "a") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
sys.exit(int(os.environ.get("STUB_NOTIFY_EXIT", "0")))
"""
HANG = """import time
time.sleep(30)
"""
HANG_LOGGED = """import os, sys, time
with open(os.environ["STUB_NOTIFY_LOG"], "a") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
time.sleep(30)
"""


def git(cwd: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env={**os.environ, **GIT_ENV})
    assert done.returncode == 0, (args, done.stderr)
    return done.stdout.strip()


class Project:
    def __init__(self, root: Path, monkeypatch):
        self.base, self.mp = root, monkeypatch
        self.root = root / "project"
        self.worktrees = root / "wt"
        self.home = root / "home"
        self.proc = root / "proc"
        self.bin = root / "bin"
        for folder in (self.root, self.worktrees, self.home, self.proc, self.bin):
            folder.mkdir(parents=True)
        self.state = self.root / ".gov-runtime" / "dispatch"
        self.launch_log, self.notify_log = root / "launch.log", root / "notify.log"
        (root / "launch_stub.py").write_text(STUB_LAUNCH)
        (root / "notify_stub.py").write_text(STUB_NOTIFY)
        (root / "hang_stub.py").write_text(HANG)
        (root / "hang_logged_stub.py").write_text(HANG_LOGGED)
        monkeypatch.setenv("HOME", str(self.home))
        monkeypatch.setenv("GOV_RESOURCES_PROC", str(self.proc))
        monkeypatch.setenv("STUB_LAUNCH_LOG", str(self.launch_log))
        monkeypatch.setenv("STUB_NOTIFY_LOG", str(self.notify_log))
        for key, value in GIT_ENV.items():
            monkeypatch.setenv(key, value)
        for name in ("GOV_RESOURCES_STAT", "STUB_LAUNCH_EXIT", "STUB_NOTIFY_EXIT"):
            monkeypatch.delenv(name, raising=False)
        self.memory(20 * GIB)
        self.loads(1.0, 1.0)
        monkeypatch.setenv("GOV_RESOURCES_NPROC", "20")
        monkeypatch.setenv("GOV_RESOURCES_BUSY_CORES", "2")
        monkeypatch.setenv("GOV_RESOURCES_EMBEDDING_CPU", json.dumps({"shared": 0.5, "query": 0.5}))
        monkeypatch.setenv("GOV_RESOURCES_EMBEDDING_CPU_NOW", json.dumps({"shared": 0.0, "query": 0.0}))
        self.disk(500 * GIB, 50_000_000)
        self.gate()
        git(self.root, "init", "-q", "-b", BRANCH)
        (self.root / "README").write_text("x\n")
        git(self.root, "add", "README")
        git(self.root, "commit", "-q", "-m", "init")
        self.settings = {"max_leads": 3, "stagger_s": 0, "cpu_band": 1, "integration_branch": BRANCH,
                         "worktrees_root": str(self.worktrees),
                         "launch_command": [sys.executable, str(root / "launch_stub.py"), "{ticket}", "{w2}", "{log}"],
                         "notifier_command": [sys.executable, str(root / "notify_stub.py")],
                         "command_timeout_s": 20}
        self.write_config()

    # the machine
    def memory(self, available: int):
        path = self.base / "meminfo"
        path.write_text(f"MemTotal: {32 * GIB // 1024} kB\nMemAvailable: {available // 1024} kB\n")
        self.mp.setenv("GOV_RESOURCES_MEMINFO", str(path))

    def loads(self, one: float, fifteen: float):
        path = self.base / "loadavg"
        path.write_text(f"{one} 0.5 {fifteen} 1/100 12345\n")
        self.mp.setenv("GOV_RESOURCES_LOADAVG", str(path))

    def disk(self, free: int, inodes: int):
        self.mp.setenv("GOV_RESOURCES_DISK", json.dumps({"free_bytes": free, "free_inodes": inodes}))

    def gate(self, **changes):
        data = gate_config.template(cpus=list(range(20)))
        data["memory_floor_bytes"]["value"] = 3 * GIB
        data["working_size_bytes"]["value"] = 1 * GIB
        for key, value in changes.items():
            data[key]["value"] = value
        folder = self.home / ".gov-os" / "machine"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "gate.json").write_text(json.dumps(data))

    def process(self, pid: int, cmdline: list[str], rss: int = 0, ppid: int = 1):
        folder = self.proc / str(pid)
        folder.mkdir(exist_ok=True)
        (folder / "stat").write_text(f"{pid} (x) S {ppid} 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        page = os.sysconf("SC_PAGE_SIZE")
        (folder / "statm").write_text(f"0 {rss // page} 0 0 0 0 0\n")
        (folder / "cmdline").write_bytes(b"\0".join(a.encode() for a in cmdline) + b"\0")

    def lead_process(self, pid: int, ticket: str, rss: int = 0):
        settings = {"env": {"GOV_ROLE": "orchestrator", "GOV_TICKET": ticket}}
        self.process(pid, ["claude", "--settings", json.dumps(settings), "-p"], rss=rss)

    def end_process(self, pid: int):
        import shutil
        shutil.rmtree(self.proc / str(pid), ignore_errors=True)

    # the project
    def write_config(self, **changes):
        for key, value in changes.items():
            if value is None:
                self.settings.pop(key, None)
            else:
                self.settings[key] = value
        path = self.root / "governance" / "project" / "dispatch.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({"dispatch": self.settings}))

    def ticket(self, w2: str, ticket: str = None, *, committed: bool = True, in_worktree: bool = True,
               brief: str | None = "go\n", status: str = "in_progress"):
        """A ticket with its claim on the integration branch and its worktree, and a brief."""
        ticket = ticket or f"T-{w2}"
        file = self.root / ".tickets" / f"{ticket}.md"
        file.parent.mkdir(exist_ok=True)
        file.write_text(f"---\nid: {ticket}\nstatus: {status}\n---\n# {w2}\n")
        if committed:
            git(self.root, "add", f".tickets/{ticket}.md")
            git(self.root, "commit", "-q", "-m", f"claim {ticket}")
        else:
            git(self.root, "add", "-N", f".tickets/{ticket}.md")
        if in_worktree:
            git(self.root, "worktree", "add", "-q", "-b", f"wb/{w2}", str(self.worktrees / w2),
                BRANCH if committed else "HEAD")
        if brief is not None:
            (self.state / "briefs").mkdir(parents=True, exist_ok=True)
            (self.state / "briefs" / f"{w2}.md").write_text(brief)
        return ticket

    def worktree(self, w2: str) -> Path:
        return self.worktrees / w2

    def ready(self, *lines: str):
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "ready.txt").write_text("\n".join(lines) + "\n")

    def entry(self, w2: str, ticket: str = None) -> str:
        return f"{w2} {ticket or 'T-' + w2} {w2}.md {w2}-log"

    def history(self, *rows: dict):
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

    # running a pass
    def tick(self, action: str = "tick", as_json: bool = False):
        from gov.dispatch import command
        out = io.StringIO()
        with redirect_stdout(out):
            code = command.run(self.root, argparse.Namespace(action=action, json=as_json, session="", role=None), {})
        return code, out.getvalue()

    def status(self) -> dict:
        return json.loads((self.state / "status.json").read_text())

    def status_text(self) -> str:
        return (self.state / "status.txt").read_text()

    def started(self) -> list[str]:
        file = self.state / "started.txt"
        return [line.split()[0] for line in file.read_text().splitlines() if line.strip()] if file.exists() else []

    def launches(self) -> list[str]:
        return self.launch_log.read_text().splitlines() if self.launch_log.exists() else []

    def wait_exit(self, log: str, seconds: float = 15.0) -> str:
        file = self.state / "logs" / f"{log}.exit"
        end = time.time() + seconds
        while time.time() < end:
            if file.exists():
                return file.read_text().strip()
            time.sleep(0.05)
        raise AssertionError(f"{file} never appeared")

    def inbox(self) -> list[Path]:
        folder = self.state / "inbox"
        return sorted(p for p in folder.iterdir() if p.is_file()) if folder.exists() else []

    def read_all(self):
        folder = self.state / "inbox"
        (folder / "read").mkdir(parents=True, exist_ok=True)
        for item in self.inbox():
            item.rename(folder / "read" / item.name)


@pytest.fixture
def project(tmp_path, monkeypatch):
    return Project(tmp_path, monkeypatch)
