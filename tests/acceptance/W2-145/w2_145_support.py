"""Support for the W2-145 acceptance tests: no private reranker beside the shared service (DAEO-2tfd).

Built on W2-112's boxes (``tests/acceptance/W2-112/w2_112_support.py``): a temporary ``HOME`` per case, short
enough for a Unix socket's path, holding a real ``python -m venv`` where DEC-397 puts the reranker environment, with
W2-112's stand-in ``sentence_transformers`` and ``torch`` (no model, no GPU: the stand-in logs every load with its
process and device), a private GPU lock folder (``GOV_RERANK_GPU_LOCK_DIR``, never ``/tmp``), a dead Ollama address,
and every process that carries the ``HOME`` ended when the case ends. This module adds what W2-145 needs on top:

- **The interpreter records every program it is asked to run.** The planted environment's ``bin/python`` (the one
  ``gov.retrieval.rerank`` starts, ``~/.local/share/gov-os/reranker-venv/bin/python``) is a small shell script that
  writes one ``start`` line (its pid, the time, its arguments) and one ``end`` line (the time, the exit code) to
  ``programs.log`` in the box's state folder, and runs the environment's own ``python3`` in between (not ``exec``:
  the end is recorded). So a case sees every reranker process any search started: the shared service
  (``rerank_service.py``) and anything else (``rerank_worker.py``, or any other program).
- **The environment records every import of the model's libraries** (``torch``, ``sentence_transformers``,
  ``transformers``) by any of its processes: a ``.pth`` installs ``standin/w145_imports.py``, which writes
  ``imports.log``. Used to see that ``rerank_worker.py`` run as a program ends before torch or the model loads.
- **A stand-in socket server** (``StandIn``) at the service's socket (``~/.cache/gov-os/rerank.sock``), holding the
  service's start lock (``rerank.lock`` beside it) for its life as a live service does, so no search can start
  another service beside it. Its ways of failing are S1's: ``full`` (it takes no connection: none can be had within
  ``CONNECT_S``), ``silent`` (it reads the request and never answers), ``error`` (an error answer), ``close`` (it
  reads the request and closes without an answer), ``garbage`` (a line that is not JSON), ``short`` and ``long``
  (one score fewer or one more than the texts sent).
- **The GPU slot locks' holders, by pid,** from ``/proc/locks`` (``lock_holders``), and a slot held by another
  process (``SlotHolder``: a child that holds one slot until the case lets it go).
- **Sessions** run ``w2_145_session.py``: ``rerank(query, candidates)`` with no reranker given, then
  ``last_outcome()``; the call's own start and end; and which model libraries the session itself then holds.

Nothing real is touched: not the real reranker environment, not ``/tmp``'s GPU lock files, not the live service's
socket, not Ollama. The S1 failure kinds are planted by ``plant``; each kind's reason pattern, bound and premise are
in ``KINDS``.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
W2_112 = HERE.parent / "W2-112"
if str(W2_112) not in sys.path:
    sys.path.insert(0, str(W2_112))

import w2_112_support as base  # noqa: E402
from w2_112_support import (alive, candidates, check_scored, check_unranked, query_of, raised,  # noqa: E402,F401
                            unix_sockets_refused)

SESSION = HERE / "w2_145_session.py"
IMPORTS = HERE / "standin" / "w145_imports.py"
SLOT_RULE_WORKER = HERE / "standin" / "w145_slot_rule_worker.py"

# ---- the bounds (S4) and the settings every box gives its sessions
MARGIN_S = 1.0            # S4: "within CONNECT_S plus 1 s", "within the request's time limit plus 1 s"
TIME_LIMIT_S = 3.0        # GOV_RERANK_TIMEOUT_S in every W2-145 box: a request's time limit, short
SLOT_WAIT_S = 4.0         # GOV_RERANK_GPU_WAIT_S where a case plants "no GPU slot": longer than CONNECT_S + 1 s,
                          # so a second wait for a slot after the service's own (a private's) cannot hide in the bound
SERVICE_SLOTS_S = 3.0     # S3: a slot freed by another process is held by the service within 3 s
HUNG_S = base.HUNG_S
TIMEOUT_SETTING, WAIT_SETTING = base.TIMEOUT_SETTING, base.WAIT_SETTING
SLOTS_SETTING, LOCK_DIR_SETTING, IDLE_SETTING = base.SLOTS_SETTING, base.LOCK_DIR_SETTING, base.IDLE_SETTING
LOCK_NAME = base.LOCK_NAME
MODEL, REVISION = base.MODEL, base.REVISION
NAMED_EXIT = "no private reranker runs: the shared service reranks"   # S2, the worker's named exit text
HEAVY = ("torch", "sentence_transformers", "transformers")
SERVICE_WORDS = re.compile(r"service|shared", re.IGNORECASE)


def connect_s() -> float:
    """``rerank.CONNECT_S`` of the code under test (the ticket names it), at most the 2 s of DEC-1034 T3."""
    from gov.retrieval import rerank

    value = float(getattr(rerank, "CONNECT_S", 2.0))
    assert 0 < value <= 2.0, f"rerank.CONNECT_S is {value} s: DEC-1034 T3 bounds the connection at about 2 s"
    return value


# ---------------------------------------------------------------- the recording interpreter

# Every tool by its full path: a search may run with a PATH that holds no /usr/bin (the bundle cases' does not).
RECORDER = """#!/bin/sh
# The W2-145 tests: this reranker environment's interpreter records every program it is asked to run.
log={log}
printf '%s\\tstart\\t%s\\t%s\\n' "$$" "$({date} +%s.%N)" "$*" >> "$log"
{python} "$@"
code=$?
printf '%s\\tend\\t%s\\t%s\\n' "$$" "$({date} +%s.%N)" "$code" >> "$log"
exit $code
"""


@dataclass
class Program:
    """One run of the planted interpreter: its (wrapper's) pid, its arguments, when it started and ended, its code."""
    pid: int
    args: str
    start: float
    end: float | None = None
    code: int | None = None

    @property
    def service(self) -> bool:
        return "rerank_service.py" in self.args

    @property
    def worker(self) -> bool:
        return "rerank_worker.py" in self.args


# ---------------------------------------------------------------- sessions and boxes


class Session(base.Session):
    """One running W2-145 session (``w2_145_session.py``)."""

    def __init__(self, box, request: dict, name: str, env: dict):  # noqa: D107 - base.Session's, with this script
        self.box, self.name = box, name
        self.request_path = box.work / f"{name}.request.json"
        self.result_path = box.work / f"{name}.result.json"
        self.stdout_path, self.stderr_path = box.work / f"{name}.out", box.work / f"{name}.err"
        self.request_path.write_text(json.dumps(request), encoding="utf-8")
        with open(self.stdout_path, "wb") as out, open(self.stderr_path, "wb") as err:
            self.process = subprocess.Popen([sys.executable, str(SESSION), str(self.request_path),
                                             str(self.result_path)], env=env, cwd=str(box.work),
                                            stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                            start_new_session=True)
        self.launched = time.monotonic()
        self.seconds = None


class Box(base.Box):
    """A W2-112 box with W2-145's recorders, a short request time limit and ``slots`` GPU slots."""

    def __init__(self, *, environment: bool = True, gpu: dict | None = None, settings: dict | None = None,
                 slots: int = base.SLOTS):
        merged = {TIMEOUT_SETTING: f"{TIME_LIMIT_S:g}", SLOTS_SETTING: str(slots), **(settings or {})}
        super().__init__(environment=environment, gpu=gpu, settings=merged)
        self.slots = slots
        self.config(slots=slots)
        self._children: list[subprocess.Popen] = []
        if environment:
            self._recorders()

    def _recorders(self) -> None:
        shutil.copy2(IMPORTS, self.site / IMPORTS.name)
        (self.site / "w145_imports.json").write_text(json.dumps({"state": str(self.state)}), encoding="utf-8")
        (self.site / "w145-imports.pth").write_text("import w145_imports; w145_imports.install()\n",
                                                     encoding="utf-8")
        python = self.venv / "bin" / "python"
        assert (self.venv / "bin" / "python3").exists(), f"the planted environment has no bin/python3: {self.venv}"
        date = shutil.which("date") or "/bin/date"
        python.unlink()
        python.write_text(RECORDER.format(log=json.dumps(str(self.state / "programs.log")), date=json.dumps(date),
                                          python=json.dumps(str(self.venv / "bin" / "python3"))), encoding="utf-8")
        python.chmod(0o755)

    # ---- what the recorders saw

    def programs(self) -> list[Program]:
        found: dict[int, Program] = {}
        try:
            lines = (self.state / "programs.log").read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        for line in lines:
            parts = line.split("\t", 3)
            if len(parts) < 3:
                continue
            try:
                pid, what, when = int(parts[0]), parts[1], float(parts[2])
            except ValueError:
                raise AssertionError(f"the recording interpreter wrote a line it cannot read: {line!r}") from None
            if what == "start":
                found[pid] = Program(pid, parts[3] if len(parts) > 3 else "", when)
            elif what == "end" and pid in found:
                found[pid].end, found[pid].code = when, int(parts[3]) if len(parts) > 3 else None
        return list(found.values())

    def imports(self) -> list[dict]:
        try:
            lines = (self.state / "imports.log").read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        out = []
        for line in lines:
            parts = line.split("\t", 3)
            if len(parts) == 4:
                out.append({"pid": int(parts[0]), "ppid": int(parts[1]), "module": parts[2], "argv": parts[3]})
        return out

    def log_lines(self) -> list[tuple[str, str]]:
        """``rerank.log``'s lines as ``(kind, detail)``: the kind is the second tab field, the detail the rest."""
        path = self.home / base.CACHE_REL / "rerank.log"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, IsADirectoryError):
            return []
        out = []
        for line in text.splitlines():
            parts = line.split("\t", 2)
            if len(parts) >= 2:
                out.append((parts[1], parts[2] if len(parts) > 2 else ""))
        return out

    # ---- sessions

    def start(self, request: dict, *, env: dict | None = None, name: str | None = None) -> Session:
        self._names += 1
        session = Session(self, request, name or f"s{self._names}", env or self.env())
        self._session_pids.append(session.pid)
        return session

    def search(self, query: str, given: list[dict], *, env: dict | None = None, timeout: float = HUNG_S,
               **_ignored) -> dict:
        return self.start({"query": query, "candidates": given}, env=env).wait(timeout)

    # ---- the GPU slots

    def slot_path(self, number: int) -> Path:
        return self.locks / LOCK_NAME.format(number)

    def holders(self) -> dict[int, set[int]]:
        """Each slot's holders by pid (``/proc/locks``)."""
        return {number: lock_holders(self.slot_path(number)) for number in range(self.slots)}

    def free_slots(self) -> list[int]:
        return [number for number, pids in self.holders().items() if not pids]

    def hold_in_child(self, number: int) -> "SlotHolder":
        holder = SlotHolder(self.slot_path(number))
        self._children.append(holder.process)
        return holder

    def wait_for(self, predicate, seconds: float, step: float = 0.05):
        """``predicate()``'s first true value within ``seconds``, else its last value."""
        deadline, value = time.monotonic() + seconds, None
        while True:
            value = predicate()
            if value or time.monotonic() >= deadline:
                return value
            time.sleep(step)

    def close(self) -> None:
        for child in self._children:
            try:
                child.kill()
                child.wait(5)
            except OSError:
                pass
        super().close()


# ---------------------------------------------------------------- the GPU slot locks' holders


def lock_holders(path: Path) -> set[int]:
    """The live pids holding a ``flock`` on ``path``, from ``/proc/locks`` (by the file's inode)."""
    try:
        inode = os.stat(path).st_ino
    except FileNotFoundError:
        return set()
    found = set()
    try:
        lines = Path("/proc/locks").read_text(encoding="utf-8").splitlines()
    except OSError as error:  # pragma: no cover - a machine without /proc/locks
        pytest.fail(f"/proc/locks cannot be read here ({error}): the slots' holders cannot be seen", pytrace=False)
    for line in lines:
        parts = line.split()
        if "->" in parts or "FLOCK" not in parts:
            continue  # a waiter, or a POSIX lock
        at = parts.index("FLOCK")
        try:
            pid, where = int(parts[at + 3]), parts[at + 4]
        except (IndexError, ValueError):
            continue
        if where.rsplit(":", 1)[-1] == str(inode) and alive(pid):
            found.add(pid)
    return found


HOLD = ("import fcntl, os, sys\n"
        "fd = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o600)\n"
        "fcntl.flock(fd, fcntl.LOCK_EX)\n"
        "print('held', flush=True)\n"
        "sys.stdin.read()\n")


class SlotHolder:
    """Another process holding one GPU slot (as a private reranker of an older tree would) until ``release``."""

    def __init__(self, path: Path):
        self.process = subprocess.Popen([sys.executable, "-I", "-c", HOLD, str(path)], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, text=True)
        line = self.process.stdout.readline()
        assert line.strip() == "held", f"the test's slot holder could not hold {path}"

    @property
    def pid(self) -> int:
        return self.process.pid

    def release(self) -> float:
        """Let the slot go; the moment the holder's process had ended, as ``time.monotonic()``."""
        self.process.stdin.close()
        self.process.wait(10)
        return time.monotonic()


# ---------------------------------------------------------------- the stand-in socket server


class StandIn:
    """A broken service at the service's socket, holding its start lock for its life (see the module's text)."""

    def __init__(self, box: Box, how: str):
        self.box, self.how, self.stop = box, how, threading.Event()
        self.requests = 0
        refused = unix_sockets_refused()
        if refused:
            pytest.fail(f"the stand-in socket server cannot be made: {refused}", pytrace=False)
        folder = box.socket.parent
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = os.open(folder / "rerank.lock", os.O_CREAT | os.O_RDWR, 0o600)
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # as a live service holds it: no second service
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(box.socket))
        os.chmod(box.socket, 0o600)
        self.held, self.fillers = [], []
        if how == "full":
            self.server.listen(0)
            for _ in range(3):
                filler = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                filler.setblocking(False)
                try:
                    filler.connect(str(box.socket))
                except OSError:
                    pass
                self.fillers.append(filler)
            return
        self.server.listen(64)
        self.server.settimeout(0.2)
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self) -> None:
        while not self.stop.is_set():
            try:
                connection, _ = self.server.accept()
            except (TimeoutError, socket.timeout):
                continue
            except OSError:
                return
            threading.Thread(target=self._answer, args=(connection,), daemon=True).start()

    def _answer(self, connection) -> None:
        try:
            connection.settimeout(10)
            received = b""
            while b"\n" not in received:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                received += chunk
            self.requests += 1
            if self.how == "silent":
                self.held.append(connection)
                return
            try:
                texts = json.loads(received.split(b"\n", 1)[0])[1]
            except (ValueError, IndexError, TypeError):
                texts = []
            if self.how == "error":
                reply = {"error": "the stand-in service failed", "device": "cuda"}
            elif self.how == "short":
                reply = {"scores": [0.5] * max(0, len(texts) - 1), "device": "cuda"}
            elif self.how == "long":
                reply = {"scores": [0.5] * (len(texts) + 1), "device": "cuda"}
            else:
                reply = None
            if self.how == "garbage":
                connection.sendall(b"not an answer\n")
            elif reply is not None:
                connection.sendall((json.dumps(reply) + "\n").encode())
            connection.close()  # "close": read, then closed with no answer
        except OSError:
            pass

    def close(self) -> None:
        self.stop.set()
        for held in self.held + self.fillers:
            try:
                held.close()
            except OSError:
                pass
        self.server.close()
        os.close(self.lock)


# ---------------------------------------------------------------- S1's failure kinds


@dataclass
class Kind:
    """One way the shared service is unreachable (S1), how it is planted, and what a search must then name."""
    name: str
    bound: str                    # "start" (CONNECT_S + 1 s after the refused start ended), "connect", "answer"
    reason: str                   # the pattern the reason must hold beside the service's name (case aside)
    box: dict = field(default_factory=dict)        # the box's own settings
    env: dict = field(default_factory=dict)        # the session's extra environment
    codes: tuple = ()             # a refused start: the service's exit codes taken as this kind's refusal
    stand_in: str | None = None   # the stand-in server's way of failing
    eperm: bool = False           # the session's own Python refuses socket(AF_UNIX)
    hold_all: bool = False        # the test holds every GPU slot before the search


KINDS = [
    Kind("start-refused-no-gpu-slot", "start", r"slot", box={WAIT_SETTING: f"{SLOT_WAIT_S:g}"}, codes=(75,),
         hold_all=True),
    Kind("start-refused-below-gpu-share", "start", r"share|memory|GiB", box={"gpu": base.SHORT}, codes=(77,)),
    Kind("start-refused-no-gpu", "start", r"GPU", box={"gpu": base.NO_GPU}, codes=(77, 78)),
    Kind("start-refused-gpu-hidden", "start", r"hidden|CUDA_VISIBLE", env={"CUDA_VISIBLE_DEVICES": "-1"},
         codes=(76,)),
    Kind("socket-refused-eperm", "connect", r"EPERM|not permitted|PermissionError|Errno 1|sandbox", eperm=True),
    Kind("no-connection-within-connect-s", "connect", r"timed out|timeout|time out|within|connect",
         stand_in="full"),
    Kind("no-answer-within-the-time-limit", "answer", r"timed out|timeout|time out|within|time limit",
         stand_in="silent"),
    Kind("an-error-answer", "answer", r"stand-in service failed|refused the request|answered (with )?an error|"
         r"error answer", stand_in="error"),
    Kind("closed-without-an-answer", "answer", r"closed|without an answer|EOF|reset|no answer", stand_in="close"),
    Kind("not-an-answer", "answer", r"JSON|decode|Expecting|not an answer|malformed|invalid", stand_in="garbage"),
    Kind("too-few-scores", "answer", r"match|length|count|number|\d+ scores?", stand_in="short"),
    Kind("too-many-scores", "answer", r"match|length|count|number|\d+ scores?", stand_in="long"),
]
KIND_IDS = [kind.name for kind in KINDS]
BY_NAME = {kind.name: kind for kind in KINDS}


def box_for(boxes, kind: Kind, **extra):
    """The box of ``kind``: its GPU and settings."""
    settings = {key: value for key, value in kind.box.items() if key != "gpu"}
    settings.update(extra.pop("settings", {}))
    return boxes(gpu=kind.box.get("gpu"), settings=settings, **extra)


class Planted:
    """``kind`` planted in ``box``: the session environment to search with, and what to close afterwards."""

    def __init__(self, box: Box, kind: Kind, env: dict | None = None):
        self.box, self.kind, self.stand_in = box, kind, None
        if kind.hold_all:
            box.hold_slots(*range(box.slots))
        if kind.eperm:
            box.refuse_unix_sockets()
        if kind.stand_in:
            self.stand_in = StandIn(box, kind.stand_in)
        self.env = {**(env or box.env()), **kind.env}

    def premise(self) -> None:
        """Fails, naming it, when the planted failure did not take place (the case would test nothing)."""
        if self.kind.codes:
            services = [program for program in self.box.programs() if program.service]
            if not services:
                pytest.fail(f"premise ({self.kind.name}): no search started the shared service "
                            f"(rerank_service.py), so its refusal was never seen{base.note()}", pytrace=False)
            codes = [program.code for program in services]
            assert all(code in self.kind.codes for code in codes), \
                (f"premise ({self.kind.name}): the service's start was to be refused with exit "
                 f"{self.kind.codes}, it ended {codes}")
        if self.stand_in is not None and self.kind.stand_in != "full":
            assert self.stand_in.requests >= 1, \
                f"premise ({self.kind.name}): the stand-in service at the socket never received the request"

    def service_end(self) -> float:
        ended = [program.end for program in self.box.programs() if program.service and program.end is not None]
        assert ended, f"premise ({self.kind.name}): the refused service's end was not recorded"
        return max(ended)

    def close(self) -> None:
        if self.stand_in is not None:
            self.stand_in.close()


def check_reason(reason, kind: Kind, who: str) -> None:
    assert isinstance(reason, str) and reason.strip(), f"{who}: no reason is named: {reason!r}"
    assert SERVICE_WORDS.search(reason), f"{who}: the reason does not name the shared service: {reason!r}"
    assert re.search(kind.reason, reason, re.IGNORECASE), \
        f"{who}: the reason does not name the service's failure ({kind.name}, /{kind.reason}/): {reason!r}"


def check_no_private(box: Box, report: dict, who: str) -> None:
    """S1: no reranker process other than the shared service was started; no model loaded anywhere; the calling
    process holds none of the model's libraries."""
    programs = box.programs()
    workers = [program.args for program in programs if program.worker]
    assert workers == [], f"{who}: a private reranker (rerank_worker.py) was started: {workers}"
    others = [program.args for program in programs if not program.service]
    assert others == [], f"{who}: a program other than the shared service was started from the reranker " \
                         f"environment: {others}"
    loads = [(record["pid"], record["device"]) for record in box.loads()]
    assert loads == [], f"{who}: a model was loaded (pid, device): {loads}"
    assert report.get("heavy") == [], f"{who}: the calling process loaded {report.get('heavy')}"


def bound_of(kind: Kind) -> float:
    return (TIME_LIMIT_S if kind.bound == "answer" else connect_s()) + MARGIN_S


# ---------------------------------------------------------------- a small project for the bundle (W2-112's)

QUERY = "amber lantern"
NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W2-145 tests", "deletion_rebuild": "authoritative; restored from git only",
}
DOCS = {
    "docs/harbour.md": "# Harbour\n\nThe amber lantern hangs above the harbour gate.\n",
    "docs/kiln.md": "# Kiln\n\nAn amber lantern was found in the old kiln, east of the yard.\n",
    "docs/ledger.md": "# Ledger\n\nThe keeper lists each amber lantern lit at dusk.\n",
}


def git(root: Path, *args) -> None:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(root), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "W2-145 tests", "GIT_AUTHOR_EMAIL": "w2-145@example.invalid",
           "GIT_COMMITTER_NAME": "W2-145 tests", "GIT_COMMITTER_EMAIL": "w2-145@example.invalid",
           "GIT_AUTHOR_DATE": "2026-11-09T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-09T12:00:00+00:00"}
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, timeout=60)
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"


def build_project(base_dir: Path) -> tuple[Path, Path]:
    """``(tools folder, project root)``: git, gitleaks and this interpreter (no ``ollama``), and a small project
    with its lexical index and record store (as W2-112's bundle cases build theirs)."""
    import yaml

    tools = base_dir / "bin"
    tools.mkdir()
    for tool in ("git", "gitleaks", "python3"):
        found = sys.executable if tool == "python3" else shutil.which(tool)
        wrapper = tools / tool
        wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
        wrapper.chmod(0o755)
    root = base_dir / "p"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    document = yaml.safe_load((REPO_ROOT / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    document.pop("decision_register", None)
    document["namespaces"] = {name: {"paths": patterns, "memory_class": "governance", **NAMESPACE_FIELDS,
                                     "embedding_policy": "not embedded"}
                              for name, patterns in (("top", ["*"]), ("overlay", ["governance/**"]),
                                                     ("docs", ["docs/**"]))}
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    shutil.copy2(REPO_ROOT / "template/.gitleaks.toml", root / ".gitleaks.toml")
    for rel, text in DOCS.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the W2-145 bundle project")
    script = base_dir / "build.py"
    script.write_text("import sys\nfrom pathlib import Path\nfrom gov.retrieval import lexical\nfrom gov import store\n"
                      "root = Path(sys.argv[1])\nlexical.refresh(root)\nstore.load(root)\n", encoding="utf-8")
    home = base_dir / "build-home"
    home.mkdir()
    env = {"PATH": str(tools), "HOME": str(home), "PYTHONPATH": str(base.gov_src()), "PYTHONDONTWRITEBYTECODE": "1",
           "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "OLLAMA_HOST": "127.0.0.1:9",
           "GOV_QUERY_OLLAMA_HOST": "127.0.0.1:9", "TMPDIR": str(base_dir)}
    done = subprocess.run([sys.executable, str(script), str(root)], capture_output=True, text=True, env=env,
                          timeout=600, cwd=str(base_dir))
    assert done.returncode == 0, f"the project's index and store could not be built:\n{done.stderr[-3000:]}"
    return tools, root


# ---------------------------------------------------------------- git (S5, S6, failure lines 4 and 5)

FILED = "f916c5766f7f618288cd65857ab36bbb39c1a180"   # the commit that filed W2-145 (DAEO-2tfd)
TICKET = REPO_ROOT / ".tickets" / "DAEO-2tfd.md"
S6_FILES = [
    "tests/acceptance/W2-112/test_w2_112_fallback.py",
    "tests/acceptance/W2-112/test_w2_112_slots.py",
    "tests/acceptance/W2-112/test_w2_112_gpu.py",
    "tests/acceptance/W2-112/test_w2_112_bundle.py",
    "tests/acceptance/W2-112/test_w2_112_concurrency.py",
    "tests/acceptance/W2-112/w2_112_support.py",
    "tests/acceptance/W2-112/w2_112_session.py",
    "tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py",
]
REWRITE_REASON = "Rewrite-Reason: DEC-1048 (5)"


def run_git(*args) -> str:
    done = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, f"git {' '.join(args)} failed here: {done.stderr.strip()}"
    return done.stdout


def commits_since_filed(*paths: str) -> list[dict]:
    """The commits after W2-145 was filed that touch ``paths``: ``{"hash", "message", "files"}`` each."""
    try:
        run_git("cat-file", "-e", f"{FILED}^{{commit}}")
    except AssertionError:
        pytest.fail(f"the commit that filed W2-145 ({FILED[:12]}) is not in this repository's history: the "
                    "ticket's commits cannot be told apart", pytrace=False)
    hashes = run_git("log", "--format=%H", f"{FILED}..HEAD", "--", *paths).split()
    out = []
    for commit in hashes:
        message = run_git("show", "-s", "--format=%B", commit)
        files = [line for line in run_git("show", "--format=", "--name-only", commit).splitlines() if line.strip()]
        out.append({"hash": commit, "message": message, "files": files})
    return out


def trailer(message: str, key: str) -> list[str]:
    return [line.split(":", 1)[1].strip() for line in message.splitlines()
            if line.lower().startswith(key.lower() + ":")]
