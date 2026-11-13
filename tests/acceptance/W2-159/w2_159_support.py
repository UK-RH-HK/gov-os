"""Support for the W2-159 acceptance tests: ``gov session-watch stop-check waiter|idle`` (DAEO-6lid).

Everything is planted under the test's own ``tmp_path``: a project root with ``governance/project/session-watch.yaml``,
the runtime folder ``.gov-runtime/session-watch/`` (``session.txt``, ``standby.txt``, ``state.json``), the dispatcher's
``.gov-runtime/dispatch/status.json``, pid and exit files, a transcript (JSON lines), a folder of background agents' files,
a folder of background tasks' output files, a fake ``gov`` program for the dispatcher source and a planted process list.
Never a live session, never ``/proc`` (the process list is always the planted one), never a hook registered in a
``.claude/``.

``Watch.run()`` runs ``python -B -m gov.cli.main session-watch stop-check <check> --root <root>`` as a child process with the
tree under test's ``src`` on ``PYTHONPATH``, the hook's JSON on standard input and a clean environment (no ``GOV_*`` or
``GIT_*`` of the session running the tests, ``HOME`` a temporary folder), plus the test overrides of the ticket's Interface
(item 6): ``GOV_SESSION_WATCH_PS``, ``GOV_SESSION_WATCH_NOW``, ``GOV_SESSION_WATCH_GOV`` and the lead's two names
``GOV_SESSION_WATCH_SUBAGENTS`` and ``GOV_SESSION_WATCH_TASKS``. Ages are set with ``os.utime`` against the fixed "now" of
``GOV_SESSION_WATCH_NOW``; no test sleeps.

The module never imports ``gov.session_watch``: the engineer's inner names are not the interface.
"""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import gov

SRC = Path(gov.__file__).resolve().parents[1]  # the tree under test: <tree>/src
TREE = SRC.parent
SESSION_WATCH_SRC = SRC / "gov" / "session_watch"

NOW = float(int(time.time()))  # the check's "now" for every age (GOV_SESSION_WATCH_NOW)
HOUR = 3600.0
MINUTE = 60.0

# How GOV_SESSION_WATCH_PS carries the planted process list. The ticket's Interface (item 6) says "a JSON list of {pid,
# cmdline, start, state, fds} in place of /proc" and does not say whether the variable holds the list itself or the path
# of a file holding it. The reference this was named after (stop_idle_check.py's GOV_STOPIDLE_PROC) holds a PATH. One
# switch, one place: True = the value is the path of a file holding the JSON list; False = the value is the JSON text.
PS_AS_FILE = True

REGISTERED = "0a1b2c3d-registered-orchestrator-session"
OTHER = "9f8e7d6c-some-other-session"

NAMES_ERROR = re.compile(r"state|json|unreadable|invalid|cannot|could not|error|fail", re.I)


@dataclass
class Result:
    code: int
    out: str
    err: str
    log_new: list = field(default_factory=list)

    @property
    def doc(self):
        text = self.out.strip()
        return json.loads(text) if text else None

    @property
    def silent(self) -> bool:
        return self.out.strip() == ""

    @property
    def blocked(self) -> bool:
        return bool(self.doc) and self.doc.get("decision") == "block"

    @property
    def reason(self) -> str:
        return (self.doc or {}).get("reason", "") or ""

    @property
    def message(self) -> str:
        return (self.doc or {}).get("systemMessage", "") or ""

    @property
    def log_text(self) -> str:
        return "\n".join(self.log_new)

    def __str__(self) -> str:
        return (f"exit {self.code}\n--- stdout ---\n{self.out}\n--- stderr ---\n{self.err}\n"
                f"--- new log lines ---\n{self.log_text}")


def set_age(path: Path, seconds: float) -> None:
    """The file's mtime ``seconds`` before the fixed now."""
    moment = NOW - seconds
    os.utime(path, (moment, moment))


FAKE_GOV_IMPL = r'''
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
with open(os.path.join(here, "argv.json"), "w") as handle:
    json.dump(args, handle)
if "--ready" in args:
    target = args[args.index("--ready") + 1]
    with open(os.path.join(here, "ready.txt")) as src, open(target, "w") as dst:
        dst.write(src.read())
with open(os.path.join(here, "exit.txt")) as handle:
    sys.exit(int(handle.read().strip() or 0))
'''

READER_INIT = ""
READER_ITEMS = r'''
import json, os


def read_items(path):
    with open(os.path.join(os.path.dirname(__file__), "got.txt"), "a") as handle:
        handle.write(str(path) + "\n")
    with open(path) as handle:
        return json.load(handle)
'''


class Watch:
    """A planted project and the runs of the checks against it."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.root = tmp / "project"
        self.home = tmp / "home"
        self.cwd = tmp / "cwd"
        self.scratch = tmp / "tmp"
        self.rt = self.root / ".gov-runtime" / "session-watch"
        self.dispatch = self.root / ".gov-runtime" / "dispatch"
        self.subagents = tmp / "session" / "subagents"
        self.tasks = tmp / "session" / "tasks"
        self.transcript = tmp / "session" / "transcript.jsonl"
        self.ps_path = tmp / "ps.json"
        self.gov_path = tmp / "no-such-gov"
        self.fake_dir = tmp / "fakegov"
        self.readers = tmp / "readers"
        self.python_path = [str(SRC)]
        self.config: dict = {}
        self.raw_config: str | None = None
        self.procs: list[dict] = []
        self.entries: list[dict] = []
        self.sid = REGISTERED
        self._n = 0
        for folder in (self.root, self.home, self.cwd, self.scratch, self.rt, self.subagents, self.tasks,
                       self.transcript.parent):
            folder.mkdir(parents=True, exist_ok=True)
        self.tasks = self.tasks.resolve()
        self.register()
        self.user("start the work")

    # --- configuration ----------------------------------------------------------------------------------------------

    def cfg(self, **changes) -> None:
        self.config.update(changes)

    def write_config(self) -> None:
        target = self.root / "governance" / "project" / "session-watch.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        text = self.raw_config if self.raw_config is not None else yaml.safe_dump({"session_watch": self.config})
        target.write_text(text, encoding="utf-8")

    # --- the registered session, the stand-by note, the state --------------------------------------------------------

    def register(self, sid: str | None = None) -> None:
        (self.rt / "session.txt").write_text((sid or self.sid) + "\n", encoding="utf-8")

    def unregister(self) -> None:
        (self.rt / "session.txt").unlink(missing_ok=True)

    def standby(self, age_s: float) -> Path:
        path = self.rt / "standby.txt"
        path.write_text("owner decides; stand-by declared\n", encoding="utf-8")
        set_age(path, age_s)
        return path

    def state_path(self) -> Path:
        return self.rt / "state.json"

    def state(self):
        return json.loads(self.state_path().read_text(encoding="utf-8"))

    def log_path(self) -> Path:
        return self.rt / "stop-check.log"

    def log_lines(self) -> list[str]:
        if not self.log_path().is_file():
            return []
        return self.log_path().read_text(encoding="utf-8").splitlines()

    # --- the transcript (JSON lines) -----------------------------------------------------------------------------------

    def _uuid(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}-{self._n:04d}"

    def _flush(self) -> None:
        self.transcript.write_text("".join(json.dumps(e) + "\n" for e in self.entries), encoding="utf-8")

    def user(self, text: str = "next request", **extra) -> str:
        """A user entry that starts a turn; its uuid."""
        entry = {"type": "user", "uuid": self._uuid("user"), "timestamp": f"2026-11-12T10:{self._n % 60:02d}:00Z",
                 "message": {"role": "user", "content": text}}
        entry.update(extra)
        self.entries.append(entry)
        self._flush()
        return entry["uuid"]

    def assistant(self, text: str) -> None:
        self.entries.append({"type": "assistant", "uuid": self._uuid("asst"),
                             "timestamp": f"2026-11-12T10:{self._n % 60:02d}:30Z",
                             "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}})
        self._flush()

    def tool_round(self) -> None:
        """An assistant tool call and its result (a user entry that is not a prompt: no new turn)."""
        use = self._uuid("toolu")
        self.entries.append({"type": "assistant", "uuid": self._uuid("asst"),
                             "message": {"role": "assistant", "content": [
                                 {"type": "tool_use", "id": use, "name": "Bash", "input": {"command": "true"}}]}})
        self.entries.append({"type": "user", "uuid": self._uuid("user"),
                             "message": {"role": "user", "content": [
                                 {"type": "tool_result", "tool_use_id": use, "content": "ok"}]}})
        self._flush()

    # --- processes, pid files, background agents and tasks ------------------------------------------------------------

    def proc(self, pid: int, cmdline: str, *, started_ago: float = 600.0, state: str = "S", fds=()) -> None:
        self.procs.append({"pid": pid, "cmdline": cmdline, "start": NOW - started_ago, "state": state,
                           "fds": list(fds)})

    def job(self, pid: int, *, started_ago: float = 600.0, rel: str = ".gov-runtime/jobs/launch/job1.pid",
            alive: bool = True, state: str = "S", exit_file: bool = False) -> Path:
        """A launched worker or run: a pid file (written just after the process started) and, when ``alive``, the
        process in the planted list; ``exit_file`` writes ``<name>.exit`` beside the pid file."""
        if alive:
            self.proc(pid, "bash /opt/runner/launch_job.sh --run job1", started_ago=started_ago, state=state)
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{pid}\n", encoding="utf-8")
        set_age(path, max(started_ago - 5.0, 0.0))
        if exit_file:
            path.with_suffix(".exit").write_text("0\n", encoding="utf-8")
        return path

    def agent(self, name: str, *, finished: bool = False, silent_for: float = 60.0) -> None:
        """One of the session's background agents: ``agent-<name>.meta.json`` and its transcript."""
        meta = self.subagents / f"agent-{name}.meta.json"
        doc = {"description": f"planted agent {name}"}
        if finished:
            doc["finished"] = True
        meta.write_text(json.dumps(doc), encoding="utf-8")
        trail = self.subagents / f"agent-{name}.jsonl"
        trail.write_text("{}\n", encoding="utf-8")
        set_age(trail, silent_for)
        set_age(meta, silent_for)

    def task(self, name: str, pid: int, *, started_ago: float = 600.0, cmdline: str = "make all-targets") -> Path:
        """One of the session's background tasks: its output file held open by a live process."""
        out = self.tasks / f"{name}.output"
        out.write_text("running\n", encoding="utf-8")
        self.proc(pid, cmdline, started_ago=started_ago, fds=[str(out)])
        return out

    def write_ps(self) -> str:
        text = json.dumps(self.procs)
        if PS_AS_FILE:
            self.ps_path.write_text(text, encoding="utf-8")
            return str(self.ps_path)
        return text

    # --- the dispatcher's status ----------------------------------------------------------------------------------------

    def status(self, age_s: float = 30.0, *, gate_open: bool = True, disk_open: bool = True, outcome: str = "idle",
               running=(), running_jobs=(), pending_starts=()) -> Path:
        """``.gov-runtime/dispatch/status.json`` in W2-121's schema, its mtime ``age_s`` before the fixed now."""
        doc = {"ok": True, "time": "2026-11-12T10:00:00Z", "outcome": outcome, "exit_code": 3 if outcome == "refused" else 0,
               "running": [{"ticket": t, "pid": 7000 + i} for i, t in enumerate(running)],
               "running_jobs": [{"kind": k, "pid": 7100 + i} for i, k in enumerate(running_jobs)],
               "pending_starts": [{"log": f"{t}-log.json", "ticket": t} for t in pending_starts],
               "gate": {"open": gate_open, "reasons": [] if gate_open else ["planted: the gate is shut"],
                        "disk": {"open": disk_open, "free_bytes": 500 * 1024 ** 3, "free_inodes": 50_000_000}}}
        path = self.dispatch / "status.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc), encoding="utf-8")
        set_age(path, age_s)
        return path

    # --- the open items ---------------------------------------------------------------------------------------------------

    def items_lines(self, text: str, rel: str = "items/open.txt") -> None:
        """A file source with the built-in ``lines`` reader."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.cfg(items={"source": "file", "path": rel, "reader": "lines"})

    def unblocked(self) -> None:
        """Two unblocked items (u101, u102), one waiting on the owner (u103), one waiting on a job (u105), two closed."""
        self.items_lines("# the planted open items\n\n"
                         "DAEO-u101 READY to start\n"
                         "DAEO-u102 NOT STARTED\n"
                         "DAEO-u103 WAIT owner decides\n"
                         "DAEO-u105 WAIT running job\n"
                         "DAEO-u104 DONE\n"
                         "DAEO-u106 CLOSED\n")

    def all_waiting_on_owner(self) -> None:
        self.items_lines("DAEO-u103 WAIT owner decides the scope\nDAEO-u107 WAIT owner approves the design\n"
                         "DAEO-u104 DONE\n")

    def waiter_configured(self, arm: str | None = "bash tools/arm-inbox-waiter.sh --background") -> None:
        cfg = {"waiter_commands": ["tools/inbox-wait.sh", "tools/inbox-wait-quiet.sh"]}
        if arm is not None:
            cfg["waiter_arm"] = arm
        self.cfg(**cfg)

    def blocking_project(self) -> None:
        """Both checks would block: a waiter configured and not running, unblocked items and nothing running."""
        self.waiter_configured()
        self.unblocked()
        self.status()

    def fake_gov(self, *batches, exit_code: int = 0) -> Path:
        """The ``gov`` program for the dispatcher source: writes the ready list after ``--ready``. ``batches`` are
        lists of ticket ids (batch 1 first); records its argv in ``argv.json``."""
        self.fake_dir.mkdir(parents=True, exist_ok=True)
        lines = []
        for k, batch in enumerate(batches, 1):
            lines.append(f"# batch {k}")
            for i, ticket in enumerate(batch, 1):
                name = f"W2-9{k}{i}"
                lines.append(f"{name} {ticket} {name}-A5-run.md {name}-A5-run.json")
        (self.fake_dir / "ready.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (self.fake_dir / "exit.txt").write_text(f"{exit_code}\n", encoding="utf-8")
        (self.fake_dir / "impl.py").write_text(FAKE_GOV_IMPL, encoding="utf-8")
        program = self.fake_dir / "gov"
        program.write_text(f"#!/bin/sh\nexec '{sys.executable}' '{self.fake_dir / 'impl.py'}' \"$@\"\n", encoding="utf-8")
        program.chmod(program.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        self.gov_path = program
        return program

    def fake_gov_argv(self) -> list:
        return json.loads((self.fake_dir / "argv.json").read_text(encoding="utf-8"))

    def module_reader(self, items: list, rel: str = "items/open.json") -> Path:
        """A file source with a ``module.path:function`` reader planted on a path the child imports from; the file of
        paths the reader was called with."""
        package = self.readers / "swreader_w2159"
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text(READER_INIT, encoding="utf-8")
        (package / "items.py").write_text(READER_ITEMS, encoding="utf-8")
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items), encoding="utf-8")
        self.cfg(items={"source": "file", "path": rel, "reader": "swreader_w2159.items:read_items"})
        if str(self.readers) not in self.python_path:
            self.python_path.append(str(self.readers))
        return package / "got.txt"

    # --- running the checks -------------------------------------------------------------------------------------------------

    def env(self) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
        env.update(HOME=str(self.home), PYTHONPATH=os.pathsep.join(self.python_path), PYTHONDONTWRITEBYTECODE="1",
                   TMPDIR=str(self.scratch),
                   GOV_SESSION_WATCH_PS=self.write_ps(),
                   GOV_SESSION_WATCH_NOW=str(NOW),
                   GOV_SESSION_WATCH_GOV=str(self.gov_path),
                   GOV_SESSION_WATCH_SUBAGENTS=str(self.subagents),
                   GOV_SESSION_WATCH_TASKS=str(self.tasks))
        return env

    def hook(self, *, session: str | None = None, active: bool = False, extra: dict | None = None) -> dict:
        data = {"session_id": session if session is not None else self.sid, "transcript_path": str(self.transcript),
                "cwd": str(self.root), "hook_event_name": "Stop", "stop_hook_active": active}
        data.update(extra or {})
        return data

    def run(self, check: str, *, session: str | None = None, active: bool = False, extra: dict | None = None,
            stdin: str | None = None, timeout: float = 60.0) -> Result:
        self.write_config()
        before = len(self.log_lines())
        argv = [sys.executable, "-B", "-m", "gov.cli.main", "session-watch", "stop-check", check, "--root",
                str(self.root)]
        data = stdin if stdin is not None else json.dumps(self.hook(session=session, active=active, extra=extra))
        done = subprocess.run(argv, cwd=self.cwd, env=self.env(), input=data, capture_output=True, text=True,
                              timeout=timeout)
        result = Result(done.returncode, done.stdout, done.stderr, self.log_lines()[before:])
        assert done.returncode == 0, f"the check must exit 0, always:\n{result}"
        if result.out.strip():
            try:
                doc = json.loads(result.out)
            except ValueError as exc:
                raise AssertionError(f"standard output must be at most one JSON object ({exc}):\n{result}") from exc
            assert isinstance(doc, dict), f"standard output must be a JSON object:\n{result}"
            assert set(doc) <= {"decision", "reason", "systemMessage"}, f"keys outside the hook's form:\n{result}"
            if "decision" in doc:
                assert doc["decision"] == "block" and isinstance(doc.get("reason"), str) and doc["reason"].strip(), \
                    f"a decision is a block with a reason:\n{result}"
        return result


# --- assertions shared by the files ------------------------------------------------------------------------------------------

def assert_blocks(result: Result, what: str = "") -> None:
    assert result.blocked, f"expected a block {what}:\n{result}"


def assert_no_block(result: Result, what: str = "") -> None:
    assert not result.blocked, f"expected no block {what}:\n{result}"


def assert_let_through(result: Result, pattern: str, what: str) -> None:
    """No block; a ``systemMessage`` and a log line that both name the wait (``pattern``, case-insensitive)."""
    assert not result.blocked, f"a legitimate wait ({what}) must not block:\n{result}"
    assert re.search(pattern, result.message, re.I), f"the systemMessage must name the wait ({what}: /{pattern}/):\n{result}"
    assert re.search(pattern, result.log_text, re.I), f"the log must name the wait ({what}: /{pattern}/):\n{result}"
    assert any("\t" in line for line in result.log_new), f"the log line is tab-separated:\n{result}"


def ids_named(text: str) -> set:
    return set(re.findall(r"DAEO-u\d{3}", text))
