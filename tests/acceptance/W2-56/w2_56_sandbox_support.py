"""Support for W2-56's second half, the guard-alone outcome (DEC-1112 (1)): standard library, PyYAML, gov's constants.

Built on ``w2_56_support`` (the fixture project, the stand-in CLI, the launch helpers). What it adds:

- **The sandbox block, read from ``--settings``** as the stand-in recorded it: the write list
  (``sandbox.filesystem.allowWrite``), the Unix sockets (``sandbox.network.allowUnixSockets``), each path entry
  normalised to one leading ``/`` (today's launcher writes ``//<absolute path>``, the CLI's absolute form).
- **The reranker's own setting** (W2-112): the socket and the log are ``<HOME>/.cache/gov-os/rerank.sock`` and
  ``rerank.log``, read from ``gov.retrieval.rerank`` (``CACHE_REL``, ``SOCKET``, ``LOG``) with the launcher's ``HOME``.
- **The guard**: the kernel's PreToolUse hook (``template/governance/kernel/hooks/pretooluse.py``), copied into the
  fixture project at ``governance/kernel/hooks/pretooluse.py`` (where its settings point) and run as the harness runs
  it: the call as event JSON on stdin, the session's role and ticket in ``GOV_ROLE`` and ``GOV_TICKET`` (W2-58's form).
- **A command in the session**: a stand-in plan step (``run``) that runs Python with the session's own environment
  (the one the launcher handed the CLI), the tree's ``src`` put on ``sys.path`` by the code itself (the launcher keeps
  ``PYTHONPATH`` from the session, S5).
- **A planted reranker** under the planted ``HOME``: its interpreter file, and a stand-in service on the socket (a
  thread of the test's own process; never the live service).
- **``sandbox_faults``**, called as ``gov.launch.launcher.sandbox_faults(settings)`` in a child process whose ``HOME``
  is the launcher's.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

import w2_56_support as s

GUARD_SOURCE = s.REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
SOCKET_LIMIT = 107                 # bytes of a Unix socket path (DEC-338)
TOOL_SOCKET_TAIL = 50              # the code-graph tool's longest name under its daemon folder (see test_w2_56_suite_daemon)
REAL_TMP_ROOT = "/tmp"             # the launcher's temp root outside a test: a test's own root is projected onto it

# A ticket whose allowed paths hold a name pattern (S3) beside a folder and a single file.
PATTERN = s.Ticket("DAEO-zw64", s.ENGINEER, "W2-85", ("src/app/**", "tests/unit/test_batch*", "docs/one.md"))


# --------------------------------------------------------------------------
# The sandbox block
# --------------------------------------------------------------------------

def norm(entry) -> str:
    """A path entry with one leading ``/`` (``//abs`` and ``/abs`` name the same absolute path)."""
    return "/" + str(entry).lstrip("/")


def block(settings: dict) -> dict:
    value = settings.get("sandbox")
    assert isinstance(value, dict), f"the --settings value has no sandbox block: {json.dumps(settings)[:600]}"
    return value


def network(settings: dict) -> dict:
    value = block(settings).get("network")
    assert isinstance(value, dict), f"the sandbox block has no network map: {json.dumps(block(settings))[:600]}"
    return value


def write_list(settings: dict) -> list[str]:
    files = block(settings).get("filesystem") or {}
    entries = files.get("allowWrite", []) if isinstance(files, dict) else files
    assert isinstance(entries, list), f"sandbox.filesystem.allowWrite is not a list: {entries!r}"
    return [norm(entry) for entry in entries]


def unix_sockets(settings: dict):
    value = network(settings).get("allowUnixSockets", [])
    return [norm(entry) for entry in value] if isinstance(value, list) else value


def session_tmpdir(launch) -> str:
    """The session's own temp folder: the ``TMPDIR`` the launcher handed the CLI."""
    return os.path.realpath(launch.call["env"]["TMPDIR"])


def run_folders(box: s.Box, entries) -> list[str]:
    root = os.path.realpath(box.home / "gov-os-runs")
    return [entry for entry in entries if os.path.realpath(entry).startswith(root + "/")]


def under(path: str, folder: str) -> bool:
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder.rstrip("/") + "/")


# --------------------------------------------------------------------------
# The reranker's setting (W2-112)
# --------------------------------------------------------------------------

def _rerank():
    from gov.retrieval import rerank
    return rerank


def reranker_cache(home) -> Path:
    return Path(home) / _rerank().CACHE_REL


def reranker_socket(home) -> str:
    return str(reranker_cache(home) / _rerank().SOCKET)


def reranker_log(home) -> str:
    return str(reranker_cache(home) / _rerank().LOG)


def reranker_interpreter(home) -> Path:
    return Path(home) / _rerank().PYTHON_REL


def plant_interpreter(home, text="#!/bin/sh\nexit 78\n") -> Path:
    """The reranker environment's interpreter, planted: by default one that ends at once (exit 78, "no GPU")."""
    path = reranker_interpreter(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def unix_sockets_refused_here() -> str | None:
    """Why this process cannot make a Unix socket (the launch sandbox refuses it), or None."""
    try:
        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).close()
    except OSError as error:
        return f"{type(error).__name__}: {error}"
    return None


class StandInService:
    """A stand-in for the shared reranker service on a planted socket: each request ``[query, texts]`` (one JSON line)
    gets ``{"scores": [...], "device": "stand-in"}``, the scores ``len(texts) - i`` in the request's order."""

    def __init__(self, path: str):
        self.path, self.requests, self._stop = path, [], threading.Event()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        os.chmod(Path(path).parent, 0o700)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(path)
        os.chmod(path, 0o600)
        self.server.listen(8)
        self.server.settimeout(0.2)
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        while not self._stop.is_set():
            try:
                connection, _ = self.server.accept()
            except (TimeoutError, OSError):
                continue
            with connection:
                connection.settimeout(10)
                try:
                    line = connection.makefile("rb").readline()
                    query, texts = json.loads(line)
                    self.requests.append((query, texts))
                    answer = {"scores": [float(len(texts) - i) for i in range(len(texts))], "device": "stand-in"}
                    connection.sendall((json.dumps(answer) + "\n").encode())
                except (OSError, ValueError):
                    pass

    def close(self):
        self._stop.set()
        self.thread.join(timeout=5)
        self.server.close()
        try:
            os.unlink(self.path)
        except OSError:
            pass


# --------------------------------------------------------------------------
# A command in the session (the stand-in's ``run`` step)
# --------------------------------------------------------------------------

def python_step(label: str, code: str, args=(), env=None, mkdir=()) -> dict:
    """A plan step that runs ``code`` with the session's environment, the tree's src first on ``sys.path``."""
    prefix = f"import sys\nsys.path[:0] = {s.python_path().split(os.pathsep)!r}\n"
    return {"do": "run", "label": label, "argv": [sys.executable, "-c", prefix + code, *args],
            "env": dict(env or {}), "mkdir": list(mkdir)}


def step_json(box: s.Box, label: str, name: str = s.T.wbs) -> dict:
    done = s.result(box, name, label)
    assert done["code"] == 0, f"the command {label!r} in the session failed ({done['code']}):\n{done['stderr'][-1500:]}"
    lines = [line for line in done["stdout"].splitlines() if line.strip()]
    assert lines, f"the command {label!r} in the session printed nothing:\n{done['stderr'][-800:]}"
    return json.loads(lines[-1])


# --------------------------------------------------------------------------
# Projects and launches
# --------------------------------------------------------------------------

def project(box: s.Box, extra=None, guard=False, tickets=(PATTERN,)) -> Path:
    files = {f".tickets/{ticket.tk}.md": s.ticket_text(ticket) for ticket in tickets}
    if guard:
        files[GUARD_REL] = GUARD_SOURCE.read_text(encoding="utf-8")
    files.update(extra or {})
    made = s.make_project(box, extra=files)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return made


def started(launch) -> dict:
    assert launch.returncode == 0 and launch.started, f"the launch did not start one session\n{launch.describe()}"
    return launch.settings()


def refused(launch) -> bool:
    return launch.returncode != 0 and not launch.calls and "LAUNCH_REFUSED" in launch.output


def faults(box: s.Box, settings: dict) -> list:
    """``gov.launch.launcher.sandbox_faults(settings)``, in a child process with the launcher's environment."""
    code = ("import json, sys\nfrom gov.launch.launcher import sandbox_faults\n"
            "print(json.dumps(sandbox_faults(json.load(sys.stdin))))\n")
    done = subprocess.run([sys.executable, "-c", code], input=json.dumps(settings), capture_output=True, text=True,
                          env=s.base_environment(box), cwd=str(box.project), timeout=s.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"sandbox_faults could not be called:\n{done.stderr[-1500:]}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def short_base(prefix: str) -> Path | None:
    """A short folder of the test's own (a Unix socket path holds at most 107 bytes): under /tmp when it is
    writable, else under the temp root; None when neither can be had."""
    for root in (REAL_TMP_ROOT, tempfile.gettempdir()):
        try:
            return Path(tempfile.mkdtemp(prefix=prefix, dir=root)).resolve()
        except OSError:
            continue
    return None


def remove(folder) -> None:
    if folder is not None:
        shutil.rmtree(folder, ignore_errors=True)


# --------------------------------------------------------------------------
# The guard (the kernel's PreToolUse hook, as the harness runs it)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Decision:
    decision: str    # allow | ask | deny | error
    reason: str
    returncode: int | None
    stderr: str

    def describe(self) -> str:
        return (f"decision={self.decision} exit={self.returncode} reason={self.reason[:400]!r} "
                f"stderr={self.stderr.strip()[:300]!r}")


_CALLS = iter(range(1, 10_000_000))


def ask_guard(box: s.Box, tool: str, tool_input: dict, role: str, ticket: str) -> Decision:
    project_root = box.project
    data = {"session_id": "w2-56-acceptance-session", "transcript_path": str(box.elsewhere / "transcript.jsonl"),
            "cwd": str(project_root), "permission_mode": "default", "hook_event_name": "PreToolUse",
            "tool_name": tool, "tool_input": tool_input, "tool_use_id": f"toolu_w2_56_{next(_CALLS):06d}"}
    env = s.base_environment(box)
    env.update(CLAUDE_PROJECT_DIR=str(project_root), GOV_ROLE=role, GOV_TICKET=ticket)
    try:
        done = subprocess.run([sys.executable, str(project_root / GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(project_root), env=env,
                              timeout=s.COMMAND_TIMEOUT_S)
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired:
        return Decision("error", "timed out", None, "")
    if code == 2:
        return Decision("deny", err.strip(), code, err)
    if code != 0:
        return Decision("error", err.strip(), code, err)
    try:
        answer = json.loads(out.strip() or "null")
    except ValueError:
        return Decision("allow", "", code, err)
    specific = answer.get("hookSpecificOutput") if isinstance(answer, dict) else None
    if isinstance(specific, dict) and specific.get("permissionDecision") in ("deny", "ask"):
        return Decision(specific["permissionDecision"], str(specific.get("permissionDecisionReason") or ""),
                        code, err)
    return Decision("allow", "", code, err)
