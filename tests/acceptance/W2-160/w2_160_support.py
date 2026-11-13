"""Support for the W2-160 acceptance tests: ``gov wait`` and ``gov session-watch helper-watch`` (DAEO-fd0p).

Everything is planted under the test's own ``tmp_path``: exit, pid, log, json and summary files of stand-in jobs, a project
root holding ``.gov-runtime/session-watch/session.txt``, helper transcripts and their meta files (a ``subagents`` folder),
worker pid / exit / json files. Stand-in jobs are small Python child processes this module starts; each is killed and reaped
by the pid it holds in the ``procs`` fixture's teardown (never by name). Never a live session, never a hook, never the real
``~/.claude`` (HOME is a temporary folder).

Both commands run as a child process, ``python -B -m gov.cli.main ...``, with the tree under test's ``src`` on ``PYTHONPATH``,
a clean environment (no ``GOV_*`` or ``GIT_*`` of the session running the tests) and the Interface's test hooks:
``GOV_WAIT_EVERY``, ``GOV_WAIT_LINES``, ``GOV_WAIT_LOG`` (I1) and ``GOV_SESSION_WATCH_NOW``, ``GOV_SESSION_WATCH_SUBAGENTS`` (I2).

The module never imports ``gov.wait`` or ``gov.session_watch.helper_watch``: the engineer's inner names are not the interface.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import gov

SRC = Path(gov.__file__).resolve().parents[1]  # the tree under test: <tree>/src
TREE = SRC.parent
HELPER_WATCH_SRC = SRC / "gov" / "session_watch" / "helper_watch.py"
WAIT_SRC = SRC / "gov" / "wait"

NOW = float(int(time.time()))  # the watch's clock (GOV_SESSION_WATCH_NOW); every planted age is relative to it
MINUTE = 60.0
HOUR = 3600.0

CANARY = "CANARY-7f3a91c4d2b8e605"  # the text of every planted message: it must never be copied anywhere
SESSION = "0a1b2c3d-registered-orchestrator-session"

SLEEP = "import time; time.sleep(600)"
ZOMBIE_PARENT = (
    "import os, subprocess, sys, time\n"
    "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'])\n"
    "os.kill(child.pid, 9)\n"
    "print(child.pid, flush=True)\n"
    "time.sleep(600)\n"  # never reaps the child: it stays a zombie until this parent is killed
)
JOB = (
    "import os, sys, time\n"
    "base, code, lines, delay = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])\n"
    "with open(base + '.log', 'w') as log:\n"
    "    for i in range(1, lines + 1):\n"
    "        log.write(f'job-line-{i}\\n')\n"
    "        log.flush()\n"
    "time.sleep(delay)\n"
    "with open(base + '.tmp-exit', 'w') as out:\n"
    "    out.write(code + '\\n')\n"
    "os.replace(base + '.tmp-exit', base + '.exit')\n"
)


# --- processes ------------------------------------------------------------------------------------------------------------

def proc_state(pid: int) -> str | None:
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    return text.rpartition(")")[2].split()[0]


class Procs:
    """Stand-in processes; ``close`` kills and reaps each one by the pid held (never by name)."""

    def __init__(self):
        self.started: list[subprocess.Popen] = []

    def start(self, code: str = SLEEP, *args, **kw) -> subprocess.Popen:
        kw.setdefault("stdin", subprocess.DEVNULL)
        kw.setdefault("stdout", subprocess.DEVNULL)
        kw.setdefault("stderr", subprocess.DEVNULL)
        process = subprocess.Popen([sys.executable, "-c", code, *map(str, args)], **kw)
        self.started.append(process)
        return process

    def sleeper(self) -> subprocess.Popen:
        return self.start(SLEEP)

    def dead(self) -> int:
        """A pid whose process was killed and reaped: gone."""
        process = self.sleeper()
        process.kill()
        process.wait(timeout=10)
        return process.pid

    def zombie(self) -> int | None:
        """The pid of a child killed and never reaped by its parent (state Z), or None if /proc cannot show it."""
        if not Path("/proc/self/stat").exists():
            return None
        parent = self.start(ZOMBIE_PARENT, stdout=subprocess.PIPE, text=True)
        pid = int(parent.stdout.readline())
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if proc_state(pid) == "Z":
                return pid
            time.sleep(0.05)
        return None

    def job(self, base: str, code: int, *, lines: int = 5, delay: float = 2.0) -> subprocess.Popen:
        """A stand-in job: writes ``<base>.log`` lines, then after ``delay`` seconds its code into ``<base>.exit``."""
        return self.start(JOB, base, code, lines, delay)

    def close(self) -> None:
        for process in self.started:
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            if process.stdout is not None:
                process.stdout.close()


def base_env(home: Path, scratch: Path, extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.update(HOME=str(home), PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(scratch))
    env.update(extra or {})
    return env


@dataclass
class Result:
    code: int
    out: str
    err: str
    elapsed: float = 0.0
    new_items: dict = field(default_factory=dict)  # helper-watch only: name -> text of the inbox files this run wrote

    def __str__(self) -> str:
        return f"exit {self.code} in {self.elapsed:.1f}s\n--- stdout ---\n{self.out}\n--- stderr ---\n{self.err}"


# --- gov wait -------------------------------------------------------------------------------------------------------------

class Wait:
    """A folder of stand-in jobs' files and the runs of ``gov wait`` against them."""

    def __init__(self, tmp: Path):
        self.dir = tmp / "jobs"
        self.home = tmp / "home"
        self.cwd = tmp / "cwd"
        self.scratch = tmp / "tmp"
        for folder in (self.dir, self.home, self.cwd, self.scratch):
            folder.mkdir(parents=True, exist_ok=True)

    def base(self, name: str = "job1") -> str:
        """``<base>``: the exit file's path less ``.exit``."""
        return str(self.dir / name)

    def write(self, base: str, suffix: str, text: str) -> Path:
        path = Path(base + suffix)
        path.write_text(text, encoding="utf-8")
        return path

    def run(self, *args, every: str = "0.2", lines: int | None = None, log: str | None = None,
            timeout: float = 60.0) -> Result:
        env = base_env(self.home, self.scratch, {"GOV_WAIT_EVERY": every})
        if lines is not None:
            env["GOV_WAIT_LINES"] = str(lines)
        if log is not None:
            env["GOV_WAIT_LOG"] = log
        argv = [sys.executable, "-B", "-m", "gov.cli.main", "wait", *map(str, args)]
        started = time.monotonic()
        done = subprocess.run(argv, cwd=self.cwd, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)
        return Result(done.returncode, done.stdout, done.stderr, time.monotonic() - started)


# --- the helper watch -----------------------------------------------------------------------------------------------------

def iso(age_s: float) -> str:
    return datetime.fromtimestamp(NOW - age_s, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def touch(path: Path, age_s: float) -> None:
    moment = NOW - age_s
    os.utime(path, (moment, moment))


_n = [0]


def _uuid() -> str:
    _n[0] += 1
    return f"entry-{_n[0]:05d}"


def user(age: float, label: str = "prompt") -> dict:
    return {"type": "user", "uuid": _uuid(), "timestamp": iso(age),
            "message": {"role": "user", "content": f"{CANARY}-user-{label}"}}


def assistant(age: float, label: str = "reply") -> dict:
    return {"type": "assistant", "uuid": _uuid(), "timestamp": iso(age),
            "message": {"role": "assistant", "model": "claude-x",
                        "content": [{"type": "text", "text": f"{CANARY}-assistant-{label}"}]}}


def tool_call(age: float, name: str = "Bash") -> dict:
    return {"type": "assistant", "uuid": _uuid(), "timestamp": iso(age),
            "message": {"role": "assistant", "model": "claude-x",
                        "content": [{"type": "tool_use", "id": "toolu_1", "name": name,
                                     "input": {"command": f"echo {CANARY}-tool-input"}}]}}


def tool_result(age: float) -> dict:
    return {"type": "user", "uuid": _uuid(), "timestamp": iso(age),
            "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "toolu_1", "content": f"{CANARY}-tool-result"}]}}


def api_error(age: float, *, key: str = "isApiErrorMessage", synthetic: bool = False, code: str = "ECONNRESET") -> dict:
    """An assistant entry that is an API or network error: flagged by ``isApiErrorMessage`` or by ``apiError``. A
    synthetic one (``model == "<synthetic>"``) carries the client's fixed text; any other carries the canary."""
    entry = {"type": "assistant", "uuid": _uuid(), "timestamp": iso(age), "error": "unknown",
             "message": {"role": "assistant", "model": "<synthetic>" if synthetic else "claude-x",
                         "content": [{"type": "text",
                                      "text": "API Error: Unable to connect to API (ECONNRESET)" if synthetic
                                      else f"{CANARY}-error-text"}]}}
    if key == "isApiErrorMessage":
        entry["isApiErrorMessage"] = True
    else:
        entry["apiError"] = code
    return entry


def bookkeeping(age: float) -> dict:
    """An entry that is none of assistant, user or system (a queue note)."""
    return {"type": "queue-operation", "operation": "enqueue", "timestamp": iso(age)}


def mangled(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9-]", "-", str(path))


ITEM_NAME = re.compile(r"^\d{8}-\d{6}-helper-watch(-\d+)?\.txt$")


class Watch:
    """A planted project root, its helpers and workers, and the runs of ``gov session-watch helper-watch``."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.root = tmp.resolve() / "p"
        self.home = tmp / "h"
        self.cwd = tmp / "c"
        self.scratch = tmp / "t"
        self.session_dir = tmp / "sess"
        self.subagents = self.session_dir / "subagents"
        for folder in (self.root, self.home, self.cwd, self.scratch, self.subagents):
            folder.mkdir(parents=True, exist_ok=True)
        self.rt = self.root / ".gov-runtime" / "session-watch"
        self.inbox = self.root / ".gov-runtime" / "dispatch" / "inbox"
        self.state_file = self.rt / "helper-watch-state.json"
        self.log_file = self.rt / "helper-watch.log"
        self.rt.mkdir(parents=True, exist_ok=True)
        self.register()

    # --- the registered session ----------------------------------------------------------------------------------------
    def register(self, sid: str = SESSION) -> None:
        (self.rt / "session.txt").write_text(sid + "\n", encoding="utf-8")

    def unregister(self) -> None:
        (self.rt / "session.txt").unlink(missing_ok=True)

    def config(self, text: str) -> None:
        target = self.root / "governance" / "project" / "session-watch.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    # --- helpers -----------------------------------------------------------------------------------------------------------
    def helper(self, aid: str, entries: list, age: float, *, finished: bool = False, folder: Path | None = None) -> Path:
        """``agent-<aid>.jsonl`` (JSON lines) and ``agent-<aid>.meta.json``; both files' mtime ``age`` s before the clock,
        which is also the age of the newest entry (the entry's timestamp and the file's mtime agree)."""
        folder = folder or self.subagents
        folder.mkdir(parents=True, exist_ok=True)
        trail = folder / f"agent-{aid}.jsonl"
        trail.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
        meta = {"description": "planted helper", "agentType": "general-purpose"}
        if finished:
            meta["finished"] = True
        meta_file = folder / f"agent-{aid}.meta.json"
        meta_file.write_text(json.dumps(meta), encoding="utf-8")
        touch(trail, age)
        touch(meta_file, age)
        return trail

    # --- workers -----------------------------------------------------------------------------------------------------------
    def worker(self, name: str, pid: int, *, code: int | None = None, exit_age: float = 0.0, result: dict | None = None,
               pid_age: float = 600.0, folder: str = ".gov-runtime/jobs/launch") -> Path:
        """``<name>.pid`` (the pid; mtime ``pid_age`` before the clock), ``<name>.exit`` when ``code`` is given (mtime
        ``exit_age`` before the clock) and ``<name>.json`` (launcher lines, then one result object) when ``result`` is."""
        where = self.root / folder
        where.mkdir(parents=True, exist_ok=True)
        pid_file = where / f"{name}.pid"
        pid_file.write_text(f"{pid}\n", encoding="utf-8")
        touch(pid_file, pid_age)
        if code is not None:
            exit_file = where / f"{name}.exit"
            exit_file.write_text(f"{code}\n", encoding="utf-8")
            touch(exit_file, exit_age)
        if result is not None:
            doc = {"type": "result", "subtype": "success", "session_id": f"sess-{name}", "is_error": False,
                   "num_turns": 3, "result": f"{CANARY}-result-{name}"}
            doc.update(result)
            log = where / f"{name}.json"
            log.write_text(f"launch: starting {name}\nlaunch: model ready\n{json.dumps(doc)}\n", encoding="utf-8")
            touch(log, pid_age)
        return pid_file

    # --- running -----------------------------------------------------------------------------------------------------------
    def items(self) -> list[Path]:
        return sorted(self.inbox.glob("*-helper-watch*.txt")) if self.inbox.is_dir() else []

    def run(self, *args, once: bool = True, now: float | None = None, subagents: bool = True, env: dict | None = None,
            expect: int | None = 0, timeout: float = 60.0) -> Result:
        before = {p.name for p in self.items()}
        argv = [sys.executable, "-B", "-m", "gov.cli.main", "session-watch", "helper-watch", "--root", str(self.root)]
        if once:
            argv.append("--once")
        argv += [str(a) for a in args]
        extra = {"GOV_SESSION_WATCH_NOW": str(NOW if now is None else now)}
        if subagents:
            extra["GOV_SESSION_WATCH_SUBAGENTS"] = str(self.subagents)
        extra.update(env or {})
        started = time.monotonic()
        done = subprocess.run(argv, cwd=self.cwd, env=base_env(self.home, self.scratch, extra), capture_output=True,
                              text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        result = Result(done.returncode, done.stdout, done.stderr, time.monotonic() - started)
        result.new_items = {p.name: p.read_text(encoding="utf-8") for p in self.items() if p.name not in before}
        if expect is not None:
            assert done.returncode == expect, f"expected exit {expect}:\n{result}"
        if expect == 0:
            said = {Path(line.split(" ", 2)[2].strip()).name for line in done.stdout.splitlines()
                    if line.startswith("HELPER_WATCH item ")}
            assert said == set(result.new_items), (
                f"stdout must hold one `HELPER_WATCH item <path>` per item written ({sorted(result.new_items)}):\n{result}")
            for name in result.new_items:
                assert ITEM_NAME.match(name), f"an item is named <UTC yyyymmdd-HHMMSS>-helper-watch[-<n>].txt, not {name!r}"
        return result

    # --- spying ------------------------------------------------------------------------------------------------------------
    def snapshot(self) -> dict:
        """Every file under the root, HOME, the temporary folder and the session folder: (size, mtime)."""
        seen = {}
        for base in (self.root, self.home, self.scratch, self.session_dir):
            for path in base.rglob("*"):
                if path.is_file() and not path.is_symlink():
                    stat = path.stat()
                    seen[str(path)] = (stat.st_size, stat.st_mtime_ns)
        return seen

    def is_allowed(self, path: str) -> bool:
        p = Path(path)
        inbox = self.inbox
        return inbox in p.parents or p in (self.state_file, self.log_file)

    def written_outside_the_allowed(self, before: dict, after: dict) -> list[str]:
        changed = [p for p in set(before) | set(after) if before.get(p) != after.get(p)]
        return sorted(p for p in changed if not self.is_allowed(p))

    def every_new_or_changed_text(self, before: dict, after: dict) -> dict:
        """Path -> text of each file the run wrote (new or changed)."""
        out = {}
        for path in sorted(p for p in after if before.get(p) != after[p]):
            out[path] = Path(path).read_text(encoding="utf-8", errors="replace")
        return out


# --- the plant of the first pass (S3) ----------------------------------------------------------------------------------------

CONDITIONS = {  # subject -> the condition planted
    "apierr01": "api-error (isApiErrorMessage)",
    "apierr02": "api-error (apiError only)",
    "stall01": "stalled (31 minutes, not finished)",
    "wk-gone": "worker gone, no exit file",
    "wk-exit3": "worker exit file holds 3",
    "wk-iserr": "worker exit 0, result is_error true",
    "wk-apistat": "worker exit 0, result api_error_status 529",
}
HEALTHY = ("fin01", "live01", "wk-run", "wk-clean")


def plant_all(w: Watch, procs: Procs) -> None:
    """One planted condition each (CONDITIONS) and a healthy helper and worker each (HEALTHY), every message text the canary."""
    w.helper("apierr01", [user(900), assistant(600), api_error(300)], age=300)
    w.helper("apierr02", [user(900), tool_call(600), tool_result(580), api_error(200, key="apiError")], age=200)
    w.helper("stall01", [user(2400), assistant(2000), assistant(31 * MINUTE)], age=31 * MINUTE)
    w.helper("fin01", [user(900), assistant(300), assistant(100)], age=100, finished=True)
    w.helper("live01", [user(900), tool_call(200), tool_result(120)], age=120)
    w.worker("wk-gone", procs.dead(), pid_age=600)
    w.worker("wk-exit3", procs.dead(), code=3, result={}, pid_age=900)
    w.worker("wk-iserr", procs.dead(), code=0, result={"is_error": True}, pid_age=900)
    w.worker("wk-apistat", procs.dead(), code=0, result={"api_error_status": 529}, pid_age=900)
    w.worker("wk-run", procs.sleeper().pid, pid_age=300)
    w.worker("wk-clean", procs.dead(), code=0, result={"is_error": False, "api_error_status": None}, pid_age=900)


def item_subjects(text: str, subjects) -> list[str]:
    return [s for s in subjects if s in text]


# --- the source search (S4) ------------------------------------------------------------------------------------------------

_BANNED = re.compile(r"(?<![\w.-])(pgrep|pkill|killall|pidof|psutil)(?![\w-])|proc\.sh|/cmdline|/comm(?!\w)|(?<!\w)ps -")


def process_name_hits(path: Path) -> list[str]:
    """Process-name matching in the CODE of a Python file: its string constants (docstrings left out), names, attributes
    and imports. Whole tokens: ``pgrep pkill killall pidof psutil proc.sh /cmdline /comm`` the string ``"ps"`` and ``ps -``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docstrings.add(id(first.value))
    hits = []
    for node in ast.walk(tree):
        texts = []
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            texts.append(node.value)
            if node.value.strip() == "ps":
                hits.append(f"{path.name}:{node.lineno}: the string 'ps'")
        elif isinstance(node, ast.Name):
            texts.append(node.id)
        elif isinstance(node, ast.Attribute):
            texts.append(node.attr)
        elif isinstance(node, ast.Import):
            texts += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            texts += [node.module or ""] + [a.name for a in node.names]
        for text in texts:
            found = _BANNED.search(text)
            if found:
                hits.append(f"{path.name}:{getattr(node, 'lineno', '?')}: {found.group(0)!r} in {text[:60]!r}")
    return hits
