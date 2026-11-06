"""Support for the W2-112 acceptance tests: one reranker service for every session (P-RERANKER-1, DEC-979 item 4).

Everything runs on any machine, in a sandbox, with no model, no GPU and no network:

- **The code under test is this worktree's** (DEC-732): every session is a new Python process whose ``PYTHONPATH``
  is the ``src/`` folder of the ``gov`` package the test process itself imports, which the caller's
  ``PYTHONPATH`` names. No worktree path is written here.
- **A box per test:** a temporary ``HOME`` made for the test alone, short enough for a Unix socket's path. It holds
  a real reranker environment where DEC-397 puts it (``HOME/.local/share/gov-os/reranker-venv``, a
  ``python -m venv`` of this interpreter), whose site folder holds the stand-in model (``standin/``): a
  ``sentence_transformers`` whose ``CrossEncoder`` scores a pair by a hash of its texts, and a ``torch`` whose
  ``cuda`` reports the stand-in GPU (by default one with room: 14 GiB of 16 free). A stand-in ``nvidia-smi``
  comes first on the sessions' ``PATH``. The stand-in logs every load (with its device and how many GPU slots
  were held) and every scoring call with its process id, so the tests count models and see who scored what.
- **The GPU slot rule (KPI 7, DEC-1033)** runs on a private lock folder in the box (``GOV_RERANK_GPU_LOCK_DIR``),
  never ``/tmp``: the real lock files are never touched. Every session gets that folder, two slots and a short wait
  (``GOV_RERANK_GPU_WAIT_S``), and never ``GOV_RERANK_ALLOW_CPU``. A test holds slots itself with ``hold_slots``.
  The box's reranker environment holds no ``gov_reranker_gpu_slot`` module: the rule is the product's.
- **Sessions** run ``w2_112_session.py``: ``gov.retrieval.rerank.rerank(query, candidates)`` with no reranker
  given, as a search calls it. With a barrier, many call at the same moment.
- **The service** is found from outside: the Unix socket P-RERANKER-1 names (``~/.cache/gov-os/rerank.sock``), the
  processes that carry the box's ``HOME``, and the stand-in's log (the process that loaded the model and is still
  alive after every session has ended).
- **Nothing is left running:** the box ends every process that carries its ``HOME`` when its test ends. Nothing
  real is touched: not the real reranker environment, not its GPU lock files, not Ollama.

The interface the tests rely on, beyond the base's public ``gov.retrieval.rerank`` (each one constant below):
the socket's place and the one-line request ``[query, [text, ...]]`` answered by one line of scores, both from
P-RERANKER-1; the idle and time-limit settings (DEC-1034 item 3); the GPU slot rule's settings and lock files
(ACT-RERANK-WAIT-1, KPI 7), which the service obeys too (DEC-1036 T6 (b): it holds one of the two slots); the
fallback log with its reason in a file under ``~/.cache/gov-os/`` (DEC-1034 item 3); the bundle's ``rerank`` entry
(DEC-1034 item 2). No reranker loads on the CPU anywhere (DEC-1033, DEC-1036 T5 (b)).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SESSION = HERE / "w2_112_session.py"
STANDIN = HERE / "standin" / "w2112_standin.py"
UNIX_OVER_TCP = HERE / "standin" / "w2112_unix_over_tcp.py"  # the memory-release cases' answer to the sandbox

# ---- the pins and the places (ADR-0002 §2, DEC-397, P-RERANKER-1)
MODEL = "Qwen/Qwen3-Reranker-0.6B"
REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
VENV_REL = ".local/share/gov-os/reranker-venv"
PYTHON_REL = f"{VENV_REL}/bin/python"
SOCKET_REL = ".cache/gov-os/rerank.sock"            # P-RERANKER-1: "~/.cache/gov-os/rerank.sock, mode 0600"
CACHE_REL = ".cache/gov-os"                         # DEC-1034 item 3: the fallback log, with its reason, lives here
# ---- the two settings a test needs to see an idle end and a time limit within a minute (DEC-1034 item 3, T1)
IDLE_SETTING = "GOV_RERANK_IDLE_S"                   # seconds without a request before the service ends itself
TIMEOUT_SETTING = "GOV_RERANK_TIMEOUT_S"             # a request's time limit, in seconds
# ---- the GPU slot rule (KPI 7, DEC-1033; ACT-RERANK-WAIT-1)
SLOTS_SETTING = "GOV_RERANK_GPU_SLOTS"
LOCK_DIR_SETTING = "GOV_RERANK_GPU_LOCK_DIR"
WAIT_SETTING = "GOV_RERANK_GPU_WAIT_S"
SLOTS = 2
SLOT_WAIT_S = 5.0        # the boxes' default wait for a slot: short, so a case never waits the real 20 s
LOCK_NAME = "gov-os-rerank-gpu-{}.lock"
# ---- the bounds
CONNECT_S = 2.0          # "does not answer within about 2 s" (the KPI, P-RERANKER-1)
FALLBACK_S = 20.0        # a search whose service is down answers within this: 2 s, a private reranker's start, slack
HUNG_S = 120.0           # a session not ended by then is hung
OVER_CAP = 20_000        # texts in one request: above any cap the bundle's candidate limit gives
GIB = 1024 ** 3
TOLERANCE = 1e-6         # "within float rounding"; the stand-in's scores lie in [-10, 10)
SETTLE_S = 1.0           # a private reranker ends within this once its session has ended
ROOM = {"present": True, "total": 16 * GIB, "free": 14 * GIB, "name": "Stand-in GPU"}
SHORT = {"present": True, "total": 16 * GIB, "free": 1 * GIB, "name": "Stand-in GPU"}
NO_GPU = {"present": False}

_SKIP_IN_HOME = (".w2112", VENV_REL)


class Missing(AssertionError):
    """What the test needs from this machine is not here (not a failure of the ticket)."""


REFUSE_UNIX_SOCKETS = '''"""The W2-112 tests: this Python may not create a Unix socket, as in the launch sandbox (EPERM)."""
import errno
import socket as _socket

_Socket = _socket.socket


class _Refused(_Socket):
    def __init__(self, family=-1, type=-1, proto=-1, fileno=None):
        if fileno is None and family == _socket.AF_UNIX:
            raise PermissionError(errno.EPERM, "Operation not permitted")
        super().__init__(family, type, proto, fileno)


_socket.socket = _Refused
'''


def unix_sockets_refused() -> str | None:
    """Why no Unix socket can be made in this process (a sandbox that filters ``socket(AF_UNIX)``), or None."""
    try:
        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).close()
    except OSError as error:
        return (f"this sandbox refuses Unix sockets ({error}): no service can listen here, so the cases that need "
                "one fail whatever the code; run the suite where Unix sockets are allowed")
    return None


def note() -> str:
    """The sandbox's refusal, to append to a failure message, or nothing."""
    refused = unix_sockets_refused()
    return f" [NOTE: {refused}]" if refused else ""


# ---------------------------------------------------------------- the code under test


def gov_src() -> Path:
    """The ``src/`` folder of the ``gov`` package this process imports: the caller's ``PYTHONPATH`` decides it."""
    try:
        import gov
    except ImportError as error:  # pragma: no cover - the README says how to run
        raise Missing(f"gov cannot be imported ({error}): run with PYTHONPATH=<worktree>/src") from None
    return Path(gov.__file__).resolve().parent.parent


# ---------------------------------------------------------------- a short temporary base


def short_base() -> Path:
    """A new folder in the temporary folder, or in its nearest writable parent when the path is too long for a
    Unix socket under it (108 bytes in all); never inside the repository, never ``/`` or ``/tmp`` itself."""
    import tempfile

    seen, candidates = set(), []
    for start in (os.environ.get("TMPDIR"), tempfile.gettempdir()):
        if not start:
            continue
        path = Path(start).resolve()
        for folder in (path, *path.parents):
            if len(folder.parts) < 3 or folder in seen:
                continue
            seen.add(folder)
            if folder == REPO_ROOT or REPO_ROOT in folder.parents:
                continue
            candidates.append(folder)
    for folder in candidates:
        if len(str(folder)) + len("/r0000/h/") + len(SOCKET_REL) > 104:
            continue
        for number in range(100_000):
            made = folder / f"r{number}"
            try:
                made.mkdir(mode=0o700)
                return made
            except FileExistsError:
                continue
            except OSError:
                break
    raise Missing(f"no temporary folder ({os.environ.get('TMPDIR')!r} or a parent of it, outside the repository) is "
                  "both writable here and short enough for a Unix socket's path under it (108 bytes): set TMPDIR to "
                  "a writable, shorter folder")


# ---------------------------------------------------------------- processes


def alive(pid: int) -> bool:
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
            return handle.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def _environ(pid: int) -> bytes:
    try:
        with open(f"/proc/{pid}/environ", "rb") as handle:
            return handle.read()
    except OSError:
        return b""


def _cmdline(pid: int) -> bytes:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            return handle.read()
    except OSError:
        return b""


def processes_of(home: Path) -> list[int]:
    """The live processes that carry ``home``: as their ``HOME``, or in their command line."""
    marker, key = str(home).encode(), b"HOME=" + str(home).encode() + b"\0"
    found = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit() or int(entry) == os.getpid():
            continue
        pid = int(entry)
        environ = b"\0" + _environ(pid)
        if (b"\0" + key in environ or marker in _cmdline(pid)) and alive(pid):
            found.append(pid)
    return sorted(found)


def end_processes_of(home: Path, deadline_s: float = 10.0) -> None:
    deadline = time.monotonic() + deadline_s
    while time.monotonic() < deadline:
        left = processes_of(home)
        if not left:
            return
        for pid in left:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        time.sleep(0.05)


def _socket_inodes(pid: int) -> set[str]:
    found = set()
    try:
        for name in os.listdir(f"/proc/{pid}/fd"):
            try:
                target = os.readlink(f"/proc/{pid}/fd/{name}")
            except OSError:
                continue
            if target.startswith("socket:["):
                found.add(target[8:-1])
    except OSError:
        pass
    return found


def network_sockets(pid: int) -> list[str]:
    """The TCP and UDP sockets ``pid`` holds (any state), as ``protocol inode``."""
    held, found = _socket_inodes(pid), []
    for protocol in ("tcp", "tcp6", "udp", "udp6"):
        try:
            lines = Path(f"/proc/{pid}/net/{protocol}").read_text(encoding="utf-8").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            parts = line.split()
            if len(parts) > 9 and parts[9] in held:
                found.append(f"{protocol} {parts[9]}")
    return found


def listening(path: Path) -> set[str]:
    """The inodes of the Unix sockets listening at ``path`` (accepted connections left out): one per service."""
    inodes = set()
    try:
        for line in Path("/proc/net/unix").read_text(encoding="utf-8").splitlines()[1:]:
            parts = line.split(None, 7)
            if len(parts) == 8 and parts[7] == str(path) and int(parts[3], 16) & 0x10000:  # __SO_ACCEPTCON
                inodes.add(parts[6])
    except (OSError, ValueError):
        return set()
    return inodes


def unix_listeners(path: Path) -> list[int]:
    """The live processes that hold a Unix socket listening at ``path``."""
    inodes = listening(path)
    if not inodes:
        return []
    owners = []
    for entry in os.listdir("/proc"):
        if entry.isdigit() and int(entry) != os.getpid() and _socket_inodes(int(entry)) & inodes and alive(int(entry)):
            owners.append(int(entry))
    return sorted(owners)


# ---------------------------------------------------------------- texts and expected answers


def score(query: str, text: str) -> float:
    """The stand-in model's score (the same function as ``standin/w2112_standin.py``)."""
    digest = hashlib.sha256((str(query) + "\x1f" + str(text)).encode("utf-8")).digest()
    return int.from_bytes(digest[:6], "big") / float(1 << 48) * 20.0 - 10.0


def candidates(tag: str, count: int, *, ties: int = 0) -> list[dict]:
    """``count`` candidates of one session, each text its own (``tag`` in it); the last ``ties`` repeat one text."""
    found = []
    for number in range(count):
        same = number >= count - ties if ties else False
        text = f"[path: notes/{tag}.md]\nThe {tag} text that only one place holds." if same else \
            f"[path: notes/{tag}-{number}.md]\nSession {tag}, passage {number}: the keeper's ledger, line {number * 7}."
        found.append({"chunk_id": f"{tag}-{number}", "path": f"notes/{tag}-{number}.md", "start_line": 1,
                      "end_line": 3, "parent_id": f"parent-of-{tag}-{number}", "text": text,
                      "score": round(1.0 / (number + 1), 6), "routes": ["lexical"]})
    return found


def query_of(tag: str) -> str:
    return f"where does session {tag} keep its ledger"


def expected(query: str, given: list[dict]) -> list[dict]:
    """What a private reranker of the stand-in model gives: the order of the scores, equal scores in the order
    given, each candidate with its ``rerank_score``."""
    ranked = sorted(((score(query, item["text"]), item) for item in given), key=lambda pair: -pair[0])
    return [{**item, "rerank_score": value} for value, item in ranked]


def _same_fields(entry: dict, given: dict) -> bool:
    return {key: entry.get(key) for key in given} == given


def check_scored(result, query: str, given: list[dict], who: str = "the search") -> None:
    """``result`` is the private reranker's answer: the same order, the same scores within rounding, nothing lost."""
    assert isinstance(result, list), f"{who} did not return a list of candidates: {result!r}"[:600]
    want = expected(query, given)
    assert [entry.get("chunk_id") for entry in result] == [entry["chunk_id"] for entry in want], \
        (f"{who}: the order is not the one a private reranker gives on the same inputs (equal scores keep the order "
         f"given): got {[entry.get('chunk_id') for entry in result]}, expected {[e['chunk_id'] for e in want]}")
    for entry, wanted in zip(result, want):
        value = entry.get("rerank_score")
        assert isinstance(value, (int, float)) and not isinstance(value, bool), \
            f"{who}: {entry.get('chunk_id')} carries no score: {entry!r}"[:600]
        assert abs(float(value) - wanted["rerank_score"]) <= TOLERANCE, \
            (f"{who}: {entry['chunk_id']} scored {value}, a private reranker scores it {wanted['rerank_score']}: "
             "another text's or another session's score")
        assert _same_fields(entry, next(item for item in given if item["chunk_id"] == entry["chunk_id"])), \
            f"{who}: a candidate lost what it came with: {entry!r}"[:600]


def check_unranked(result, given: list[dict], who: str = "the search") -> None:
    """``result`` is the order given, no candidate scored, nothing lost (DEC-374)."""
    assert isinstance(result, list), f"{who} did not return a list of candidates: {result!r}"[:600]
    assert [entry.get("chunk_id") for entry in result] == [entry["chunk_id"] for entry in given], \
        f"{who}: unranked, the order given must be kept: got {[entry.get('chunk_id') for entry in result]}"
    for entry, item in zip(result, given):
        assert not isinstance(entry.get("rerank_score"), (int, float)), \
            f"{who}: a candidate carries a score although nothing was reranked: {entry!r}"[:600]
        assert _same_fields(entry, item), f"{who}: a candidate lost what it came with: {entry!r}"[:600]


def is_scored(result) -> bool:
    return isinstance(result, list) and bool(result) and all(
        isinstance(entry.get("rerank_score"), (int, float)) for entry in result)


def check_scored_or_unranked(result, query: str, given: list[dict], who: str = "the search") -> str:
    """Either a private reranker's answer or the order given, unscored; never anything in between."""
    if is_scored(result):
        check_scored(result, query, given, who)
        return "scored"
    check_unranked(result, given, who)
    return "unranked"


# ---------------------------------------------------------------- the box


class Session:
    """One running session (``w2_112_session.py``)."""

    def __init__(self, box, request: dict, name: str, env: dict):
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

    @property
    def pid(self) -> int:
        return self.process.pid

    def wait(self, timeout: float = HUNG_S) -> dict:
        """The session's report; a session that has not ended by ``timeout`` is hung, and the test fails."""
        try:
            self.process.wait(timeout=max(0.1, timeout - (time.monotonic() - self.launched)))
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
            pytest.fail(f"a search hung: session {self.name} had not ended {timeout:.0f} s after it started "
                        f"(stderr: {self.stderr()[-1500:]})", pytrace=False)
        self.seconds = time.monotonic() - self.launched
        try:
            report = json.loads(self.result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pytest.fail(f"session {self.name} ended without a report (exit {self.process.returncode}); "
                        f"stderr: {self.stderr()[-2000:]}", pytrace=False)
        # The search's own time: the call, from just before it to just after it, in the session's process.
        both = isinstance(report.get("started"), (int, float)) and isinstance(report.get("ended"), (int, float))
        report["seconds"] = report["ended"] - report["started"] if both else self.seconds
        report["stderr"] = self.stderr()
        return report

    def stderr(self) -> str:
        try:
            return self.stderr_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""


def raised(report: dict) -> str | None:
    error = report.get("error")
    return None if error is None else f"{error['type']}: {error['message']}\n{error.get('trace', '')[-1500:]}"


class Box:
    """One test's world: its ``HOME`` (with or without the stand-in reranker environment) and its sessions."""

    def __init__(self, *, environment: bool = True, gpu: dict | None = None, settings: dict | None = None):
        self._session_pids: list[int] = []
        self.base = short_base()
        self.home, self.work = self.base / "h", self.base / "w"
        self.state = self.home / ".w2112"
        for folder in (self.home, self.work, self.state, self.state / "log", self.state / "bin", self.state / "lib",
                       self.home / ".run"):
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.socket = self.home / SOCKET_REL
        self.venv = self.home / VENV_REL
        self.locks = self.base / "locks"  # the GPU slot rule's private lock folder (never /tmp)
        self.locks.mkdir(mode=0o700)
        self.settings = dict(settings or {})
        self._names = 0
        self._held: list[int] = []
        self.config(gpu=gpu or ROOM, lock_dir=str(self.locks), slots=SLOTS)
        shutil.copy2(STANDIN, self.state / "lib" / STANDIN.name)
        if environment:
            self._environment()
        self.dead_host = f"127.0.0.1:{_free_port()}"

    # ---- the stand-in reranker environment

    def _environment(self) -> None:
        done = subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(self.venv)], capture_output=True,
                              text=True, timeout=120)
        if done.returncode != 0:
            raise Missing(f"python -m venv cannot make a reranker environment here: {done.stderr[-500:]}")
        version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site = self.venv / "lib" / version / "site-packages"
        site.mkdir(parents=True, exist_ok=True)
        self.site = site
        shutil.copy2(STANDIN, site / STANDIN.name)
        (site / "w2112_standin.json").write_text(json.dumps({"state": str(self.state)}), encoding="utf-8")
        files = {
            "sentence_transformers/__init__.py":
                "from w2112_standin import CrossEncoder, __version__  # the W2-112 tests' stand-in\n",
            "sentence_transformers/cross_encoder/__init__.py": "from w2112_standin import CrossEncoder\n",
            "sentence_transformers/cross_encoder/CrossEncoder.py": "from w2112_standin import CrossEncoder\n",
            "torch/__init__.py":
                "import w2112_standin as _s\nfrom . import cuda\n__version__ = _s.TORCH_VERSION\ndevice = _s.Device\n"
                "float16 = bfloat16 = float32 = 'dtype'\n\n\ndef no_grad(*a, **k):\n    return _s.ANYTHING\n\n\n"
                "inference_mode = no_grad\n\n\ndef set_num_threads(n):\n    pass\n\n\ndef get_num_threads():\n"
                "    return 4\n\n\ndef __getattr__(name):\n    if name.startswith('__'):\n"
                "        raise AttributeError(name)\n    return _s.ANYTHING\n",
            "torch/cuda/__init__.py":
                "import w2112_standin as _s\nis_available = _s.cuda_is_available\ndevice_count = _s.cuda_device_count\n"
                "mem_get_info = _s.cuda_mem_get_info\nget_device_name = _s.cuda_get_device_name\n"
                "get_device_properties = _s.cuda_get_device_properties\n\n\nclass OutOfMemoryError(RuntimeError):\n"
                "    pass\n\n\nfrom .memory import *  # noqa: F401,F403 - the allocator's figures and empty_cache\n"
                "from . import memory\n\n\n"
                "def current_device():\n    return 0\n\n\ndef __getattr__(name):\n    if name.startswith('__'):\n"
                "        raise AttributeError(name)\n    return _s.ANYTHING\n",
            # the caching allocator (DEC-1068): empty_cache is recorded, the figures are the stand-in's
            "torch/cuda/memory.py":
                "import w2112_standin as _s\nempty_cache = _s.cuda_empty_cache\n"
                "memory_allocated = _s.cuda_memory_allocated\nmemory_reserved = _s.cuda_memory_reserved\n"
                "memory_stats = _s.cuda_memory_stats\nmax_memory_allocated = _s.cuda_max_memory_allocated\n"
                "max_memory_reserved = _s.cuda_max_memory_reserved\nmemory_cached = memory_reserved\n"
                "synchronize = reset_peak_memory_stats = reset_max_memory_allocated = ipc_collect = _s.cuda_nothing\n"
                "__all__ = ['empty_cache', 'memory_allocated', 'memory_reserved', 'memory_stats',\n"
                "           'max_memory_allocated', 'max_memory_reserved', 'memory_cached', 'synchronize',\n"
                "           'reset_peak_memory_stats', 'reset_max_memory_allocated', 'ipc_collect']\n",
        }
        for rel, text in files.items():
            path = site / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        smi = self.state / "bin" / "nvidia-smi"
        smi.write_text(f"#!{sys.executable} -I\nimport sys\nsys.path.insert(0, {str(site)!r})\n"
                       "import w2112_standin\nsys.exit(w2112_standin.nvidia_smi(sys.argv[1:]))\n", encoding="utf-8")
        smi.chmod(0o755)
        assert not list(site.glob("gov_reranker_gpu_slot*")) and not list(site.glob("gov-reranker-gpu-slot*")), \
            "the box's reranker environment holds a start-up module: the GPU slot rule must be the product's own"

    def config(self, **changes) -> dict:
        """Change the stand-in's configuration (read again at every load and every scoring call)."""
        path = self.state / "config.json"
        current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        current.update(changes)
        partial = self.state / "config.json.part"
        partial.write_text(json.dumps(current), encoding="utf-8")
        os.replace(partial, path)
        return current

    def for_pid(self, pid: int, **settings) -> None:
        """Settings for one process only (``predict_delay``, ``predict_error``)."""
        current = self.config()
        pids = dict(current.get("pids") or {})
        pids[str(pid)] = {**pids.get(str(pid), {}), **settings}
        self.config(pids=pids)

    # ---- the conditions a case plants

    def hold_slots(self, *numbers: int) -> None:
        """Hold the GPU slots ``numbers`` (all of them when none is named) from this test's own process, as other
        rerankers would: an exclusive ``flock`` on each slot's lock file in the box's private lock folder."""
        import fcntl

        for number in numbers or range(SLOTS):
            descriptor = os.open(self.locks / LOCK_NAME.format(number), os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(descriptor)
                raise
            self._held.append(descriptor)

    def hold_free_slots(self) -> list[int]:
        """Hold every GPU slot that no one holds now; the numbers taken."""
        import fcntl

        taken = []
        for number in range(SLOTS):
            descriptor = os.open(self.locks / LOCK_NAME.format(number), os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(descriptor)
                continue
            self._held.append(descriptor)
            taken.append(number)
        return taken

    def slots_held(self) -> int:
        """How many GPU slots in the box's lock folder are held now, by anyone (this test's own count too)."""
        import fcntl

        held = 0
        for number in range(SLOTS):
            try:
                descriptor = os.open(self.locks / LOCK_NAME.format(number), os.O_RDWR)  # never creates a slot
            except OSError:
                continue
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            except OSError:
                held += 1
            finally:
                os.close(descriptor)
        return held

    def release_slots(self) -> float:
        """Release every slot this test holds; the moment it did, as ``time.time()``."""
        while self._held:
            os.close(self._held.pop())
        return time.time()

    def block_service(self) -> None:
        """The service cannot start: a folder, not empty, stands where its socket goes. ``~/.cache/gov-os/`` stays
        writable for the fallback log (DEC-1034 item 3)."""
        self.socket.mkdir(parents=True, mode=0o700)
        (self.socket / "keep").write_text("the W2-112 tests keep the service from starting\n", encoding="utf-8")

    def refuse_unix_sockets(self) -> None:
        """The sessions' own Python (the system interpreter with this ``HOME``) may not create a Unix socket, as in
        the launch sandbox (``socket(AF_UNIX)`` gives EPERM): a ``usercustomize`` in the user site folder of this
        ``HOME``. The reranker environment's Python (``-I``, a venv) does not read it."""
        version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site = self.home / ".local" / "lib" / version / "site-packages"
        site.mkdir(parents=True, exist_ok=True)
        (site / "usercustomize.py").write_text(REFUSE_UNIX_SOCKETS, encoding="utf-8")

    def unix_over_tcp(self) -> bool:
        """Where this machine refuses ``socket(AF_UNIX)`` (the launch sandbox), carry the box's Unix sockets over
        loopback TCP (``standin/w2112_unix_over_tcp.py``) in its reranker environment (a ``.pth``) and its sessions
        (a ``usercustomize``), so a case can see the service at all; elsewhere nothing is installed. Whether it was.
        The test's own process is the caller's (``over_tcp_here``). Only the memory-release cases use it."""
        if not unix_sockets_refused():
            return False
        shutil.copy2(UNIX_OVER_TCP, self.state / "lib" / UNIX_OVER_TCP.name)
        if hasattr(self, "site"):
            shutil.copy2(UNIX_OVER_TCP, self.site / UNIX_OVER_TCP.name)
            (self.site / "w2112-unix-over-tcp.pth").write_text(
                "import w2112_unix_over_tcp; w2112_unix_over_tcp.install()\n", encoding="utf-8")
        version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        user_site = self.home / ".local" / "lib" / version / "site-packages"
        user_site.mkdir(parents=True, exist_ok=True)
        (user_site / "usercustomize.py").write_text(
            f"import sys\nsys.path.insert(0, {str(self.state / 'lib')!r})\nimport w2112_unix_over_tcp\n"
            "w2112_unix_over_tcp.install()\n", encoding="utf-8")
        return True

    def cache_texts(self, since: float) -> list[str]:
        """Every file under ``~/.cache/gov-os/`` written since ``since`` (the planted blocker left out), as
        ``path: text``: where the fallback log goes, with its reason (DEC-1034 item 3, DEC-1036)."""
        found, folder = [], self.home / CACHE_REL
        for path in sorted(folder.rglob("*")) if folder.is_dir() else []:
            if path == self.socket or self.socket in path.parents:
                continue
            try:
                if path.is_file() and path.stat().st_mtime >= since - 1:
                    found.append(f"{path.relative_to(self.home)}: " +
                                 path.read_text(encoding="utf-8", errors="replace")[-4000:])
            except OSError:
                continue
        return found

    # ---- what the stand-in saw

    def events(self, kind: str | None = None) -> list[dict]:
        found = []
        for path in sorted((self.state / "log").glob("[0-9]*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if kind is None or record.get("event") == kind:
                found.append(record)
        return found

    def loads(self) -> list[dict]:
        return self.events("load")

    def live_loads(self, settle: float = SETTLE_S) -> list[dict]:
        """The loads whose process is still alive, once the processes that are ending have ended: a private
        reranker ends when its session closes its input, which takes a moment after the session's own end."""
        deadline, last, steady_since = time.monotonic() + settle, None, time.monotonic()
        while True:
            now = [record for record in self.loads() if alive(record["pid"])]
            pids = [record["pid"] for record in now]
            if pids != last:
                last, steady_since = pids, time.monotonic()
            if time.monotonic() >= deadline and time.monotonic() - steady_since >= 0.3:
                return now
            time.sleep(0.05)

    def on_gpu(self) -> list[int]:
        """The live processes that hold the model on the stand-in GPU (their last load or move says ``cuda``)."""
        device: dict[int, str] = {}
        for record in self.events():
            if record["event"] in ("load", "move"):
                device[record["pid"]] = record["device"]
        return [pid for pid, name in device.items() if name == "cuda" and alive(pid)]

    def scorers_of(self, query: str) -> set[int]:
        """The processes that scored a pair of ``query``."""
        return {record["pid"] for record in self.events("predict-begin") if query in record.get("queries", [])}

    # ---- the service, from outside

    def sockets(self) -> list[Path]:
        """Every Unix socket file under ``HOME`` (the stand-in's own folders left out)."""
        found = []
        for folder, names, files in os.walk(self.home):
            rel = Path(folder).relative_to(self.home).as_posix()
            if any(rel == skip or rel.startswith(skip + "/") for skip in _SKIP_IN_HOME):
                names[:] = []
                continue
            for name in names + files:
                path = Path(folder) / name
                try:
                    if stat.S_ISSOCK(path.lstat().st_mode):
                        found.append(path)
                except OSError:
                    continue
        return sorted(found)

    def service(self) -> list[int]:
        """The processes of the service: those that hold its socket, and the live holders of the model that are
        no session of this test."""
        sessions = set(self._session_pids)
        pids = set(unix_listeners(self.socket))
        pids |= {record["pid"] for record in self.live_loads(settle=0) if record["pid"] not in sessions}
        return sorted(pid for pid in pids if alive(pid))

    def kill_service(self) -> list[int]:
        victims = self.service()
        for pid in victims:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        deadline = time.monotonic() + 10
        while any(alive(pid) for pid in victims) and time.monotonic() < deadline:
            time.sleep(0.02)
        return victims

    def answers(self) -> bool:
        """Whether something accepts a connection at the socket's place."""
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        probe.settimeout(1.0)
        try:
            probe.connect(str(self.socket))
            return True
        except OSError:
            return False
        finally:
            probe.close()

    # ---- sessions

    def env(self, **extra) -> dict:
        """A session's environment: this box's ``HOME``, this worktree's ``src``, the stand-in ``nvidia-smi``
        first on ``PATH``, and nothing of the caller's reranker, CUDA or Hugging Face settings."""
        drop = ("GOV_RERANK", "CUDA_", "HF_", "TRANSFORMERS_", "SENTENCE_TRANSFORMERS", "XDG_", "PYTHON", "OLLAMA",
                "GOV_QUERY_OLLAMA", "GOV_OLLAMA", "GOV_ROLE", "GOV_TICKET", "TORCH")
        env = {key: value for key, value in os.environ.items() if not key.startswith(drop)}
        env.update({
            "HOME": str(self.home),
            "XDG_CACHE_HOME": str(self.home / ".cache"),
            "XDG_DATA_HOME": str(self.home / ".local" / "share"),
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_RUNTIME_DIR": str(self.home / ".run"),
            "PYTHONPATH": str(gov_src()),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PATH": f"{self.state / 'bin'}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}",
            "OLLAMA_HOST": self.dead_host,
            "GOV_QUERY_OLLAMA_HOST": self.dead_host,
            "LC_ALL": "C.UTF-8",
            # the GPU slot rule on the box's own lock folder, never the real one in /tmp; no GOV_RERANK_ALLOW_CPU
            LOCK_DIR_SETTING: str(self.locks),
            SLOTS_SETTING: str(SLOTS),
            WAIT_SETTING: f"{SLOT_WAIT_S:g}",
        })
        env.update({key: str(value) for key, value in self.settings.items()})
        env.update({key: str(value) for key, value in extra.items()})
        return env

    def start(self, request: dict, *, env: dict | None = None, name: str | None = None) -> Session:
        self._names += 1
        session = Session(self, request, name or f"s{self._names}", env or self.env())
        self._session_pids.append(session.pid)
        return session

    def search(self, query: str, given: list[dict], *, private: bool = False, timeout: float = HUNG_S,
               env: dict | None = None) -> dict:
        """One search's ``rerank``, in a session of its own, to its end."""
        request = {"query": query, "candidates": given}
        if private:
            request["private"] = str(self.state / "lib")
        return self.start(request, env=env).wait(timeout)

    def together(self, requests: list[dict], *, env: dict | None = None, timeout: float = HUNG_S) -> list[dict]:
        """Many sessions that call at the same moment: each imports, says it is ready, then all go at once."""
        self._names += 1
        barrier = self.work / f"barrier{self._names}"
        sessions = [self.start({**request, "barrier": str(barrier)}, env=env) for request in requests]
        deadline = time.monotonic() + HUNG_S
        while time.monotonic() < deadline:
            ready = len(list(self.work.glob(f"{barrier.name}.ready-*")))
            if ready >= len(sessions) or any(session.process.poll() is not None for session in sessions):
                break
            time.sleep(0.01)
        Path(f"{barrier}.go").touch()
        return [session.wait(timeout) for session in sessions]

    def warm(self, tag: str = "warm") -> int:
        """Start the service with one search and return the process that loaded its model."""
        query, given = query_of(tag), candidates(tag, 4)
        report = self.search(query, given)
        assert raised(report) is None, f"the first search raised: {raised(report)}"
        check_scored(report["result"], query, given, "the first search")
        holders = [record["pid"] for record in self.live_loads()]
        assert len(holders) == 1, \
            (f"after one search ended, {len(holders)} live processes hold the model ({holders}): one service is "
             f"expected to stay up for the next session{note()}")
        return holders[0]

    def close(self) -> None:
        self.release_slots()
        end_processes_of(self.home)
        for pid in self._session_pids:
            try:
                os.killpg(pid, signal.SIGKILL)
            except OSError:
                pass
        shutil.rmtree(self.base, ignore_errors=True)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# ---------------------------------------------------------------- the one-line request (P-RERANKER-1)


def ask(path: Path, query: str, texts: list[str], timeout: float = 30.0):
    """Send ``[query, [text, ...]]`` as one line to the socket at ``path`` and return the one line answered, as
    JSON (a value that is not JSON comes back as the text). Raises ``OSError`` when the connection fails or closes
    without an answer, ``TimeoutError`` when nothing is answered by ``timeout``."""
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(str(path))
        client.sendall((json.dumps([query, texts]) + "\n").encode("utf-8"))
        received = b""
        while b"\n" not in received:
            chunk = client.recv(65536)
            if not chunk:
                if received.strip():
                    break
                raise ConnectionError("the connection closed without an answer")
            received += chunk
    finally:
        client.close()
    line = received.split(b"\n", 1)[0].decode("utf-8", "replace")
    try:
        return json.loads(line)
    except ValueError:
        return line


def scores_in(value, count: int) -> list[float] | None:
    """The scores an answer carries, one number per text in the request's order, or None when it carries none.

    The answer's form is not fixed by P-RERANKER-1 or the KPIs (DEC-1036, the moderator's (a)): a JSON object whose
    ``scores`` holds them (other keys, such as ``device``, beside it) or a bare list of them are both taken."""
    found = value.get("scores") if isinstance(value, dict) else value
    if isinstance(found, list) and len(found) == count and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) for item in found):
        return [float(item) for item in found]
    return None


def is_scores(value, count: int) -> bool:
    """Whether an answer carries one score per text (see ``scores_in``)."""
    return scores_in(value, count) is not None


# ---------------------------------------------------------------- stand-ins of a broken service


class FakeService:
    """Something else at the service's socket: ``silent`` takes requests and never answers, ``error`` answers an
    error, ``garbage`` answers what is no answer, ``full`` never takes a connection (its queue is full)."""

    def __init__(self, path: Path, how: str):
        self.path, self.how, self.stop = path, how, threading.Event()
        refused = unix_sockets_refused()
        if refused:
            pytest.fail(f"the stand-in of a broken service cannot be made: {refused}", pytrace=False)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(path))
        os.chmod(path, 0o600)
        self.held, self.fillers = [], []
        if how == "full":
            self.server.listen(0)
            for _ in range(3):
                filler = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                filler.setblocking(False)
                try:
                    filler.connect(str(path))
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
            if self.how == "silent":
                self.held.append(connection)
                continue
            threading.Thread(target=self._answer, args=(connection,), daemon=True).start()

    def _answer(self, connection) -> None:
        try:
            connection.settimeout(5)
            received = b""
            while b"\n" not in received:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                received += chunk
            reply = b'{"error": "the stand-in service failed"}\n' if self.how == "error" else b"not an answer\n"
            connection.sendall(reply)
        except OSError:
            pass
        finally:
            connection.close()

    def close(self) -> None:
        self.stop.set()
        for held in self.held + self.fillers:
            held.close()
        self.server.close()


# ---------------------------------------------------------------- the bundle's rerank entry (DEC-1034 item 2)


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, (list, tuple)):
        return [text for item in value for text in _strings(item)]
    return []


def rerank_entry(bundle: dict):
    """``(where, value, reasons)``: the bundle's ``rerank`` entry, at its top level or in its ``merge``; and every
    text that could be its reason (in the entry, or in a key beside it whose name holds "reason")."""
    for where, scope in (("bundle", bundle), ("merge", bundle.get("merge") or {})):
        if isinstance(scope, dict) and "rerank" in scope:
            value = scope["rerank"]
            reasons = [text for text in _strings(value) if text.strip().lower() != "unavailable"]
            reasons += [text for key, item in scope.items() if "reason" in str(key).lower() for text in _strings(item)]
            return where, value, [text for text in reasons if len(text.strip()) >= 3]
    return None, None, []


def unavailable(value) -> bool:
    """The entry says ``unavailable``: as its value, or as a value inside it."""
    return any(text.strip().lower() == "unavailable" for text in _strings(value))
