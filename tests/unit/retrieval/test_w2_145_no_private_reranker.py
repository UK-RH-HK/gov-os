"""Builder tests for W2-145: no private reranker beside the shared service (DEC-1048 (5), DEC-1046 (1), DEC-1097 (8)).

Regression evidence only (DEC-136); the acceptance tests are the independent test designer's. Stand-ins only: a
stand-in socket (in this process) or a stand-in socket server (a thread), a stand-in reranker environment under a
planted HOME whose interpreter records every program it is asked to run, a planted GPU lock folder
(``GOV_RERANK_GPU_LOCK_DIR``) and stand-in ``torch`` and ``sentence_transformers`` that leave a mark when imported.
No model, no GPU, never the live service, its socket or the real reranker environment.

The cases marked ``needs_sockets`` make Unix sockets; where a sandbox refuses them (EPERM) they are skipped, named.
"""
from __future__ import annotations

import errno
import fcntl
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import fusion, rerank, rerank_service  # noqa: E402
from gov.status import command as status_command  # noqa: E402

WORKER = REPO / "src/gov/retrieval/rerank_worker.py"
SERVICE = REPO / "src/gov/retrieval/rerank_service.py"
GIVEN = [{"n": 0, "text": "a"}, {"n": 1, "text": "bbb"}, {"n": 2, "text": "cc"}]


def _sockets_allowed() -> bool:
    try:
        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).close()
        return True
    except OSError as error:
        return error.errno not in (errno.EPERM, errno.EACCES)


needs_sockets = pytest.mark.skipif(not _sockets_allowed(), reason="Unix sockets are refused here (EPERM): the CTO "
                                                                   "runs this case outside the sandbox")


@pytest.fixture
def home(tmp_path_factory, monkeypatch):
    """A planted HOME (short: a socket's path is at most 107 bytes) with a stand-in reranker environment whose
    interpreter records every program it is asked to run, then ends 75 (no GPU slot)."""
    home = tmp_path_factory.mktemp("h")
    interpreter = home / rerank.PYTHON_REL
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text(f'#!/bin/sh\necho "$@" >> "{home}/programs"\nexit 75\n')
    interpreter.chmod(0o755)
    (home / "locks").mkdir()
    for key in list(os.environ):
        if key == "CUDA_VISIBLE_DEVICES" or key.startswith("GOV_RERANK_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GOV_RERANK_GPU_LOCK_DIR", str(home / "locks"))
    return home


def programs(home: Path) -> list[str]:
    path = home / "programs"
    return path.read_text().splitlines() if path.exists() else []


def fallbacks(home: Path) -> list[list[str]]:
    path = home / rerank.CACHE_REL / rerank.LOG
    return [line.split("\t") for line in path.read_text().splitlines() if "\tFALLBACK\t" in line] \
        if path.exists() else []


# --- S1, S4: every way the service fails, in this process (a stand-in socket; no Unix socket is made) ---

class _Process:
    """A started service that ends before it listens, with ``code``."""

    def __init__(self, code: int):
        self.returncode, self.code = None, code

    def poll(self):
        self.returncode = self.code
        return self.code


class _File:
    def __init__(self, sock):
        self.sock = sock

    def readline(self):
        return self.sock.kind["answer"](self.sock)


class _Socket:
    kind: dict = {}

    def __init__(self, *_args, **_kwargs):
        self.timeout = None
        if "make" in self.kind:
            self.kind["make"]()

    def settimeout(self, value):
        self.timeout = value

    def connect(self, _path):
        self.kind.get("connect", lambda sock: None)(self)

    def sendall(self, data):
        self.sent = data

    def makefile(self, _mode):
        return _File(self)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _eperm():
    raise PermissionError(1, "Operation not permitted")


def _no_listener(_sock):
    raise FileNotFoundError(2, "No such file or directory")


def _times_out(sock):
    time.sleep(sock.timeout)
    raise socket.timeout("timed out")


def _queue_full(_sock):
    raise BlockingIOError(errno.EAGAIN, "Resource temporarily unavailable")


def _answer(payload):
    return lambda sock: payload


def _scores(count_less: int):
    def answer(sock):
        _query, texts = json.loads(sock.sent)
        return json.dumps({"scores": [1.0] * (len(texts) - count_less), "device": "cuda:0"}).encode() + b"\n"
    return answer


# kind: (the stand-in's behaviour, a fragment the reason names, the bound in seconds after the failure is known)
KINDS = {
    "the socket refused by a sandbox (EPERM)": ({"make": _eperm}, "PermissionError", rerank.CONNECT_S + 1),
    "no listener and its start refused (no GPU slot)": ({"connect": _no_listener},
                                                        "no GPU slot freed within its wait", rerank.CONNECT_S + 1),
    "no connection within CONNECT_S": ({"connect": _times_out}, "timed out", rerank.CONNECT_S + 1),
    "the listen queue full (EAGAIN on connect)": ({"connect": _queue_full}, "BlockingIOError", rerank.CONNECT_S + 1),
    "no answer within the request's time limit": ({"answer": _times_out}, "timed out", 1 + 1),
    "an error answer": ({"answer": _answer(b'{"error": "ValueError: stand-in", "device": "cuda:0"}\n')},
                        "refused the request", 1),
    "the connection closed without an answer": ({"answer": _answer(b"")}, "without an answer", 1),
    "an answer of the wrong length": ({"answer": _scores(1)}, "does not match the request", 1),
    "an answer that is not JSON": ({"answer": _answer(b"garbage\n")}, "JSONDecodeError", 1),
}


@pytest.fixture
def standin(home, monkeypatch):
    """The stand-in socket, and every process start recorded (a start answers as a service that ends 75)."""
    started: list = []

    def popen(argv, **_kwargs):
        started.append([str(arg) for arg in argv])
        return _Process(75)

    monkeypatch.setattr(rerank.socket, "socket", _Socket)
    monkeypatch.setattr(rerank.subprocess, "Popen", popen)
    monkeypatch.setenv("GOV_RERANK_TIMEOUT_S", "1")
    return started


@pytest.mark.parametrize("kind", KINDS, ids=list(KINDS))
def test_s1_each_service_failure_keeps_the_order_given_and_names_it(home, standin, monkeypatch, kind):
    behaviour, named, bound = KINDS[kind]
    monkeypatch.setattr(_Socket, "kind", behaviour)
    modules = set(sys.modules)
    began = time.monotonic()
    ranked = rerank.rerank("q", GIVEN)
    took = time.monotonic() - began
    outcome = rerank.last_outcome()
    assert ranked == GIVEN and not any("rerank_score" in entry for entry in ranked)  # the order given, unscored
    assert outcome["by"] == "unavailable" and outcome["device"] is None
    assert outcome["reason"].startswith("the shared reranker did not answer") and named in outcome["reason"]
    # DEC-1048 (5): nothing but the shared service is ever started, and no model is loaded in this process
    assert all(argv[2] == str(SERVICE) for argv in standin) and not any("rerank_worker" in " ".join(argv)
                                                                           for argv in standin)
    assert not {"torch", "sentence_transformers"} & (set(sys.modules) - modules)
    assert took <= bound, took  # S4: no wait for anything else
    [line] = fallbacks(home)  # one FALLBACK line per search: the service's failure, then "unranked"
    assert line[2] == outcome["reason"] and line[3] == "unranked" and "private" not in "\t".join(line)


@pytest.mark.parametrize("connect, original", [(_queue_full, "BlockingIOError: [Errno 11] Resource temporarily "
                                                             "unavailable"), (_times_out, "TimeoutError: timed out")],
                         ids=["EAGAIN", "timeout"])
def test_s1_a_connect_that_fails_names_no_connection_within_connect_s_alike_everywhere(home, standin, monkeypatch,
                                                                                         connect, original):
    """The connect phase's failure (the listen queue full: EAGAIN; no accept within CONNECT_S) says no connection was
    made within CONNECT_S, with the error itself, the same in last_outcome, the FALLBACK line and the bundle; EAGAIN
    is asked again only until CONNECT_S has passed, and nothing is started (a listener is there)."""
    tries = []
    monkeypatch.setattr(_Socket, "kind", {"connect": lambda sock: tries.append(1) or connect(sock)})
    began = time.monotonic()
    assert rerank.rerank("q", GIVEN) == GIVEN
    took = time.monotonic() - began
    reason = rerank.last_outcome()["reason"]
    assert reason == (f"the shared reranker did not answer (ConnectionError: no connection to the shared reranker "
                      f"within CONNECT_S ({rerank.CONNECT_S:g} s): {original})")
    assert took <= rerank.CONNECT_S + 1, took
    assert len(tries) >= (2 if connect is _queue_full else 1) and standin == []
    [line] = fallbacks(home)
    assert line[2] == reason and line[3] == "unranked"
    hits = [{"chunk_id": f"c{n}", "path": f"notes/{n}.md", "start_line": 1, "end_line": 2, "parent_id": "p"}
            for n in range(3)]
    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": hits})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": False, "hits": []})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": hit["chunk_id"]} for hit in fused])
    answer = fusion.search(Path("unused"), "q", limit=None)
    assert answer["reranked"] is False and answer["rerank"]["by"] == "unavailable"
    assert answer["rerank"]["reason"] == reason


def test_s1_a_start_refused_after_its_own_wait_is_not_followed_by_another_wait(home, standin, monkeypatch):
    """P-1: S4's bound starts when the refused start ends; no second wait and no private reranker follow it."""
    monkeypatch.setattr(_Socket, "kind", {"connect": _no_listener})
    ended = []

    class Waits(_Process):  # a service that waits 1 s for a slot, then refuses
        def __init__(self):
            super().__init__(75)
            self.at = time.monotonic() + 1.0

        def poll(self):
            if time.monotonic() < self.at:
                return None
            ended.append(ended[0] if ended else time.monotonic())
            return super().poll()

    monkeypatch.setattr(rerank.subprocess, "Popen", lambda argv, **_: standin.append(argv) or Waits())
    rerank.rerank("q", GIVEN)
    after = time.monotonic() - ended[0]
    assert after <= rerank.CONNECT_S + 1, after
    assert len(standin) == 1 and rerank.last_outcome()["by"] == "unavailable"


def test_s1_a_search_that_waited_for_a_refused_service_names_its_refusal(home, standin, monkeypatch):
    """A search that found the start lock held (another search's service) and saw that service end without listening
    starts nothing: its reason is the service's REFUSED line."""
    monkeypatch.setattr(_Socket, "kind", {"connect": _no_listener})
    folder = home / rerank.CACHE_REL
    folder.mkdir(parents=True)
    (folder / rerank.LOG).write_text("2026-11-09T00:00:00+0000\tREFUSED\tthe shared reranker does not start: no GPU "
                                     "slot free within 20 s\n")
    lock = os.open(folder / rerank.LOCK, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(lock, fcntl.LOCK_EX)  # the other search's service holds the start lock
    threading.Timer(0.5, os.close, (lock,)).start()  # and ends
    assert rerank.rerank("q", GIVEN) == GIVEN
    reason = rerank.last_outcome()["reason"]
    assert "waited for ended before it listened" in reason and "no GPU slot free within 20 s" in reason
    assert standin == []


def test_s1_the_bundle_says_unranked_and_names_the_service_s_failure(home, standin, monkeypatch):
    monkeypatch.setattr(_Socket, "kind", {"make": _eperm})
    hits = [{"chunk_id": f"c{n}", "path": f"notes/{n}.md", "start_line": 1, "end_line": 2, "parent_id": "p"}
            for n in range(5)]
    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": hits})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": False, "hits": []})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": hit["chunk_id"]} for hit in fused])
    answer = fusion.search(Path("unused"), "q", limit=None)
    assert answer["reranked"] is False and answer["rerank"]["by"] == "unavailable"
    assert "PermissionError" in answer["rerank"]["reason"]
    assert [hit["chunk_id"] for hit in answer["hits"]] == [hit["chunk_id"] for hit in hits]


def test_s1_an_answering_service_still_ranks(home, standin, monkeypatch):
    monkeypatch.setattr(_Socket, "kind", {"answer": lambda sock: json.dumps(
        {"scores": [float(len(text)) for text in json.loads(sock.sent)[1]], "device": "cuda:0"}).encode() + b"\n"})
    ranked = rerank.rerank("q", GIVEN)
    assert [(entry["n"], entry["rerank_score"]) for entry in ranked] == [(1, 3.0), (2, 2.0), (0, 1.0)]
    assert rerank.last_outcome() == {"by": "service", "device": "cuda:0", "reason": None}
    assert fallbacks(home) == [] and standin == []


# --- S4: the log ---

def test_s4_a_search_of_several_requests_writes_one_line_and_stays_unranked(home, standin, monkeypatch):
    asked = []

    def second_fails(sock):
        asked.append(1)
        if len(asked) > 1:
            return b""
        return _scores(0)(sock)

    monkeypatch.setattr(_Socket, "kind", {"answer": second_fails})
    given = [{"n": n, "text": "x"} for n in range(rerank.MAX_REQUEST_TEXTS + 5)]  # two requests
    assert rerank.rerank("q", given) == given and len(asked) == 2
    assert rerank.last_outcome()["by"] == "unavailable" and len(fallbacks(home)) == 1


def test_s4_a_search_that_cannot_write_the_log_still_searches(home, standin, monkeypatch):
    monkeypatch.setattr(_Socket, "kind", {"make": _eperm})
    (home / rerank.CACHE_REL / rerank.LOG).mkdir(parents=True)  # the log's path is not writable as a file
    assert rerank.rerank("q", GIVEN) == GIVEN
    assert rerank.last_outcome()["by"] == "unavailable" and "PermissionError" in rerank.last_outcome()["reason"]


def test_s4_gov_status_counts_the_unranked_searches_as_before(home, standin, monkeypatch):
    monkeypatch.setattr(_Socket, "kind", {"make": _eperm})
    for number in range(3):
        rerank.rerank(f"q{number}", GIVEN)
    with open(home / rerank.CACHE_REL / rerank.LOG, "a") as log:
        log.write("2026-11-09T00:00:00+0000\tREFUSED\tthe shared reranker does not start: no GPU slot free\n")
    assert status_command._reranker() == {"fallbacks": 3, "service_refusals": 1,
                                          "log": str(home / rerank.CACHE_REL / rerank.LOG)}


# --- S2: no private reranker left as a mode of the product ---

def test_s2_rerank_holds_no_path_that_starts_a_private_reranker():
    assert not hasattr(rerank, "_started") and not hasattr(rerank, "_WORKER")
    mentions = {path.name for path in (REPO / "src/gov").rglob("*.py") if "rerank_worker" in path.read_text()}
    assert mentions - {"rerank_worker.py"} == {"rerank_service.py"}  # the service loads it by its file, never runs it
    service = SERVICE.read_text()
    assert "spec_from_file_location(\"rerank_worker\"" in service and "Popen" not in service
    assert not [path for path in (REPO / "src/gov").rglob("*.py") if "GOV_RERANK_ALLOW_CPU" in path.read_text()]


STANDIN_TORCH = """import os
open(os.path.join(os.environ["MARKS"], "imported-%s" % __name__), "w").close()
"""
RUN_AS_PROGRAM = """import runpy, sys
sys.path.insert(0, sys.argv[1])
sys.argv = [sys.argv[2], "Qwen/Qwen3-Reranker-0.6B", "rev"]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


@pytest.mark.parametrize("extra", [{}, {"GOV_RERANK_ALLOW_CPU": "1"}, {"CUDA_VISIBLE_DEVICES": "-1"},
                                   {"GOV_RERANK_GPU_SLOT": "0"}, {"GOV_RERANK_ALLOW_CPU": "1",
                                                                  "CUDA_VISIBLE_DEVICES": "-1"}],
                         ids=["plain", "allow-cpu", "gpu-hidden", "interim-slot", "allow-cpu-gpu-hidden"])
def test_s2_the_worker_run_as_a_program_ends_at_once_named_before_torch(tmp_path, extra):
    standins, marks, locks = tmp_path / "standins", tmp_path / "marks", tmp_path / "locks"
    for folder in (standins, marks, locks):
        folder.mkdir()
    for name in ("torch", "sentence_transformers"):
        (standins / f"{name}.py").write_text(STANDIN_TORCH)
    env = {key: value for key, value in os.environ.items()
           if key != "CUDA_VISIBLE_DEVICES" and not key.startswith(("GOV_RERANK_", "PYTHON"))}
    env.update(MARKS=str(marks), GOV_RERANK_GPU_LOCK_DIR=str(locks), **extra)
    began = time.monotonic()
    for argv in ([sys.executable, "-c", RUN_AS_PROGRAM, str(standins), str(WORKER)],
                 [sys.executable, "-I", str(WORKER), rerank.MODEL, rerank.REVISION]):
        done = subprocess.run(argv, env=env, input="", text=True, capture_output=True, timeout=20)
        assert done.returncode == 69 and done.stdout == ""
        assert done.stderr.strip() == "no private reranker runs: the shared service reranks"
    assert time.monotonic() - began < 10
    assert list(marks.iterdir()) == [] and list(locks.iterdir()) == []  # no torch, no model, no slot


def test_s2_the_worker_keeps_only_what_the_service_shares():
    spec = importlib.util.spec_from_file_location("rerank_worker_w2_145", WORKER)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    for name in ("take_slot", "load", "scores", "device_of"):
        assert callable(getattr(worker, name))
    assert not hasattr(worker, "gpu_present")


def test_s2_the_slot_rule_opens_no_cpu_path(home, monkeypatch):
    from gov.retrieval import rerank_worker

    monkeypatch.setenv("GOV_RERANK_GPU_WAIT_S", "0")
    monkeypatch.setenv("GOV_RERANK_ALLOW_CPU", "1")
    held = [os.open(home / "locks" / f"gov-os-rerank-gpu-{i}.lock", os.O_CREAT | os.O_RDWR, 0o600) for i in (0, 1)]
    try:
        for fd in held:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert rerank_worker.take_slot(True)[0] == rerank_worker.NO_SLOT  # it waits, then ends: never the CPU
        assert "CUDA_VISIBLE_DEVICES" not in os.environ
        monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "-1")
        assert rerank_worker.take_slot(allow_cpu=True)[0] == rerank_worker.GPU_HIDDEN
    finally:
        for fd in held:
            os.close(fd)


# --- S3: the service holds every reranker GPU slot for its life ---

def _held(locks: Path, slots: int = 2) -> list[int]:
    """The slots some other open file holds, found by trying each lock without waiting."""
    held = []
    for i in range(slots):
        fd = os.open(locks / f"gov-os-rerank-gpu-{i}.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            held.append(i)
        finally:
            os.close(fd)
    return held


def _hold(locks: Path, i: int) -> int:
    fd = os.open(locks / f"gov-os-rerank-gpu-{i}.lock", os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fd


def test_s3_one_pass_takes_every_free_slot_but_the_first(home, monkeypatch):
    monkeypatch.setenv("GOV_RERANK_GPU_SLOTS", "4")
    monkeypatch.setenv("GOV_RERANK_GPU_SLOT", "0")  # the first slot, the slot rule's
    other = _hold(home / "locks", 2)  # another process's
    held: dict = {}
    try:
        assert rerank_service.take_free_slots(held) == [1, 3]
        os.close(other)
        assert rerank_service.take_free_slots(held) == [2] and rerank_service.take_free_slots(held) == []
        assert _held(home / "locks", 4) == [1, 2, 3]
    finally:
        for fd in held.values():
            os.close(fd)


def test_s3_a_slot_held_elsewhere_is_taken_within_2_s_of_its_release(home, monkeypatch):
    monkeypatch.setattr(rerank_service, "_SLOTS", {})
    other = _hold(home / "locks", 1)
    stop = threading.Event()
    thread = rerank_service.hold_every_slot(stop=stop)
    try:
        assert _wait(lambda: 0 in rerank_service._SLOTS, 2)
        time.sleep(1.0)
        os.close(other)
        released = time.monotonic()
        assert _wait(lambda: 1 in rerank_service._SLOTS, 3)
        assert time.monotonic() - released <= 2.0
        assert _wait(lambda: not thread.is_alive(), 3)  # every slot held: the thread is done
    finally:
        stop.set()
        for fd in rerank_service._SLOTS.values():
            os.close(fd)


def _wait(condition, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


STANDIN_SERVICE = """import importlib.util, sys
spec = importlib.util.spec_from_file_location("rerank_service", sys.argv[1])
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)
refused = service._worker.take_slot(allow_cpu=False)
if refused:
    sys.exit(refused[0])
service.hold_every_slot()
print("started", flush=True)
sys.stdin.read()
"""
SLOT_RULE_WORKER = """import importlib.util, sys
spec = importlib.util.spec_from_file_location("rerank_worker", sys.argv[1])
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
refused = worker.take_slot(False)
sys.exit(refused[0] if refused else 0)
"""


def test_s3_beside_a_running_service_a_slot_rule_worker_waits_then_ends_75_and_the_slots_go_with_it(home, tmp_path):
    locks = home / "locks"
    env = {key: value for key, value in os.environ.items() if not key.startswith(("GOV_RERANK_", "PYTHON"))}
    env.update(GOV_RERANK_GPU_LOCK_DIR=str(locks), GOV_RERANK_GPU_WAIT_S="1")
    other = _hold(locks, 1)  # an older tree's private reranker holds slot 1
    service = subprocess.Popen([sys.executable, "-I", "-c", STANDIN_SERVICE, str(SERVICE)], env=env, text=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        assert service.stdout.readline().strip() == "started"
        time.sleep(1.0)
        os.close(other)  # it ends
        released = time.monotonic()
        assert _wait(lambda: _held(locks) == [0, 1], 3) and time.monotonic() - released <= 3
        began = time.monotonic()
        worker = subprocess.run([sys.executable, "-I", "-c", SLOT_RULE_WORKER, str(WORKER)], env=env,
                                timeout=20)
        assert worker.returncode == 75 and 0.9 <= time.monotonic() - began < 6  # it waited its wait, then ended
    finally:
        service.send_signal(signal.SIGKILL)  # a crash: the slots go with the process
        service.wait(timeout=10)
    assert _wait(lambda: _held(locks) == [], 3)


class _Loaded(Exception):
    pass


def test_s3_main_holds_every_slot_after_its_share_check_and_before_the_load(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(sys, "stdout", sys.stdout)  # main sends its output to standard error: put back after
    monkeypatch.setattr(rerank_service._worker, "take_slot", lambda allow_cpu: events.append("slot") or None)
    monkeypatch.setattr(rerank_service, "gpu_short", lambda: events.append("share") or None)
    monkeypatch.setattr(rerank_service, "hold_every_slot", lambda: events.append("every slot"))

    def load(*_args):
        events.append("load")
        raise _Loaded

    monkeypatch.setattr(rerank_service, "load", load)
    lock = os.open(tmp_path / "rerank.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        with pytest.raises(_Loaded):
            rerank_service.main("m", "r", str(tmp_path / "rerank.sock"), str(lock))
    finally:
        os.close(lock)
    assert events == ["slot", "share", "every slot", "load"]
    events.clear()
    monkeypatch.setattr(rerank_service, "gpu_short", lambda: "the GPU has 1.0 GiB free")
    lock = os.open(tmp_path / "rerank.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        with pytest.raises(SystemExit) as ended:
            rerank_service.main("m", "r", str(tmp_path / "rerank.sock"), str(lock))
    finally:
        os.close(lock)
    assert ended.value.code == rerank_service.NO_GPU_SHARE and events == ["slot"]  # refused: no slot taken beyond


# --- S1 over a stand-in socket server (a thread; needs Unix sockets) ---

def _server(home: Path, reply):
    """A stand-in service listening on the planted HOME's socket, answering each request with ``reply(request)``."""
    folder = home / rerank.CACHE_REL
    folder.mkdir(parents=True, exist_ok=True)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(folder / rerank.SOCKET))
    listener.listen(8)

    def run():
        while True:
            try:
                connection, _ = listener.accept()
            except OSError:
                return
            with connection:
                line = connection.makefile("rb").readline()
                answer = reply(json.loads(line))
                if answer is not None:
                    connection.sendall(answer)

    threading.Thread(target=run, daemon=True).start()
    return listener


SERVED = {
    "an error answer": (lambda request: b'{"error": "ValueError: stand-in", "device": "cuda:0"}\n',
                        "refused the request"),
    "the connection closed without an answer": (lambda request: None, "without an answer"),
    "an answer of the wrong length": (lambda request: json.dumps({"scores": [1.0], "device": "cuda:0"}).encode()
                                      + b"\n", "does not match the request"),
    "no answer within the request's time limit": (lambda request: time.sleep(3) or None, "timed out"),
}


@needs_sockets
@pytest.mark.parametrize("kind", SERVED, ids=list(SERVED))
def test_s1_a_stand_in_server_s_failures_keep_the_order_and_start_nothing(home, monkeypatch, kind):
    reply, named = SERVED[kind]
    monkeypatch.setenv("GOV_RERANK_TIMEOUT_S", "1")
    listener = _server(home, reply)
    try:
        began = time.monotonic()
        ranked = rerank.rerank("q", GIVEN)
        took = time.monotonic() - began
    finally:
        listener.close()
    outcome = rerank.last_outcome()
    assert ranked == GIVEN and outcome["by"] == "unavailable" and named in outcome["reason"]
    assert took <= 1 + 1, took
    assert programs(home) == []  # the stand-in environment was asked to run nothing
    assert fallbacks(home)[-1][3] == "unranked"


@needs_sockets
def test_s1_no_listener_and_a_refused_start_runs_the_service_alone(home):
    began = time.monotonic()
    ranked = rerank.rerank("q", GIVEN)
    took = time.monotonic() - began
    outcome = rerank.last_outcome()
    assert ranked == GIVEN and outcome["by"] == "unavailable"
    assert "no GPU slot freed within its wait" in outcome["reason"]
    [program] = programs(home)  # the stand-in interpreter ran the shared service, and nothing else
    assert program.split()[:2] == ["-I", str(SERVICE)] and "rerank_worker" not in program
    assert took <= rerank.CONNECT_S + 1, took
