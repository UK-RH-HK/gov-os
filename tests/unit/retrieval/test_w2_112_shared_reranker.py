"""Builder tests for the shared reranker service and its fallbacks (W2-112; DEC-979 item 4, DEC-374, DEC-1032,
DEC-1033).

Regression evidence only (DEC-136). Hermetic: a throwaway venv (``--without-pip``) stands at the reranker
environment's path in a temporary HOME, with a stand-in ``torch`` (its free GPU memory read from
``STANDIN_GPU_FREE``) and a stand-in ``sentence_transformers`` (a text's score is its length plus the question's length
over 1000). A ``.pth`` marks every process the stand-in interpreter runs, so each test ends them all and checks none is
left. The GPU slot locks are in a temporary folder; no model, no GPU, never the real environment or lock files.
"""
from __future__ import annotations

import fcntl
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
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import rerank, rerank_service  # noqa: E402
from gov.status import command as status_command  # noqa: E402

GIB = 2 ** 30
FAKE_TORCH = """import os
class _Cuda:
    @staticmethod
    def is_available():
        return "STANDIN_GPU_FREE" in os.environ
    @staticmethod
    def mem_get_info():
        if "STANDIN_GPU_FREE" not in os.environ:
            raise RuntimeError("no CUDA GPU (stand-in)")
        return int(os.environ["STANDIN_GPU_FREE"]), 16 * 2 ** 30
cuda = _Cuda()
"""
FAKE_SENTENCE_TRANSFORMERS = """import json, os, sys, time
ROLE = os.path.basename(sys.argv[0]) if sys.argv else ""
class CrossEncoder:
    def __init__(self, model, revision=None, device=None):
        if os.environ.get("STANDIN_FAIL") in (ROLE, "all"):
            raise RuntimeError("stand-in load failure")
        time.sleep(float(os.environ.get("STANDIN_LOAD_S", "0")))
        self.device = device or "cuda:0"
        open(os.path.join(os.environ["MARKS"], "model-%s-%d" % (ROLE, os.getpid())), "w").close()
    def predict(self, pairs):
        if ROLE == "rerank_service.py" and pairs and pairs[0][0] == "hang":
            time.sleep(30)
        with open(os.path.join(os.environ["MARKS"], "asked"), "a") as out:
            out.write(json.dumps([ROLE, pairs[0][0] if pairs else None]) + "\\n")
        return [float(len(text)) + len(query) / 1000 for query, text in pairs]
"""
MARK = """import os, sys
if os.environ.get("MARKS"):
    with open(os.path.join(os.environ["MARKS"], "proc-%d" % os.getpid()), "w") as out:
        out.write(os.path.basename(sys.argv[0]) if sys.argv else "")
"""
SERVICE, WORKER = "rerank_service.py", "rerank_worker.py"


@pytest.fixture(scope="module")
def standin(tmp_path_factory):
    venv = tmp_path_factory.mktemp("venv") / "reranker-venv"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
    purelib = subprocess.run([str(venv / "bin/python"), "-I", "-c",
                              "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                             capture_output=True, text=True, check=True).stdout.strip()
    site = Path(purelib)
    assert str(site).startswith(str(venv)), site  # the throwaway venv's, never the real one's
    (site / "torch.py").write_text(FAKE_TORCH)
    (site / "sentence_transformers.py").write_text(FAKE_SENTENCE_TRANSFORMERS)
    (site / "standin_mark.py").write_text(MARK)
    (site / "standin-mark.pth").write_text("import standin_mark\n")
    return venv


def _alive(pid: int) -> bool:
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (FileNotFoundError, ProcessLookupError):
        return False
    return state not in ("Z", "X")


def _pids(home: Path, role: str | None = None, alive: bool = True) -> list[int]:
    found = []
    for mark in (home / "marks").glob("proc-*"):
        pid = int(mark.name.split("-")[1])
        if (role is None or mark.read_text() == role) and (not alive or _alive(pid)):
            found.append(pid)
    return found


def _wait_until(condition, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


@pytest.fixture
def home(standin, tmp_path_factory, monkeypatch):
    home = tmp_path_factory.mktemp("h")  # short: a socket's path is at most 107 bytes
    link = home / ".local/share/gov-os/reranker-venv"
    link.parent.mkdir(parents=True)
    link.symlink_to(standin)
    for folder in ("marks", "locks"):
        (home / folder).mkdir()
    for key in list(os.environ):
        if key == "CUDA_VISIBLE_DEVICES" or key.startswith(("GOV_RERANK_", "STANDIN_")):
            monkeypatch.delenv(key)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("MARKS", str(home / "marks"))
    monkeypatch.setenv("GOV_RERANK_GPU_LOCK_DIR", str(home / "locks"))
    monkeypatch.setenv("GOV_RERANK_GPU_WAIT_S", "2")
    monkeypatch.setenv("GOV_RERANK_IDLE_S", "60")
    monkeypatch.setenv("STANDIN_GPU_FREE", str(12 * GIB))
    rerank._started.cache_clear()
    yield home
    rerank._started.cache_clear()
    for pid in _pids(home):
        os.kill(pid, signal.SIGKILL)
    assert _wait_until(lambda: not _pids(home), 10), "a process of this test is still running"


def ask(query: str, texts: list[str]):
    ranked = rerank.rerank(query, [{"n": number, "text": text} for number, text in enumerate(texts)])
    return ranked, rerank.last_outcome()


def expected(query: str, texts: list[str]) -> list[tuple[int, float]]:
    scored = [(number, float(len(text)) + len(query) / 1000) for number, text in enumerate(texts)]
    return sorted(scored, key=lambda pair: -pair[1])


def pairs(ranked) -> list[tuple[int, float]]:
    return [(entry["n"], entry["rerank_score"]) for entry in ranked]


def kinds(home: Path) -> list[str]:
    path = home / rerank.CACHE_REL / rerank.LOG
    return [line.split("\t")[1] for line in path.read_text().splitlines()] if path.exists() else []


def fallbacks(home: Path) -> list[list[str]]:
    path = home / rerank.CACHE_REL / rerank.LOG
    return [line.split("\t") for line in path.read_text().splitlines() if "\tFALLBACK\t" in line]


def in_threads(count: int, target) -> list:
    results = [None] * count

    def run(number):
        results[number] = target(number)

    threads = [threading.Thread(target=run, args=(number,)) for number in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=120)
    return results


# --- one service, many callers ---

def test_searches_starting_together_start_one_service(home, monkeypatch):
    monkeypatch.setenv("STANDIN_LOAD_S", "1")  # a slow load widens the race
    results = in_threads(8, lambda number: ask(f"q{number}", ["a", "bbb", "cc"]))
    for number, (ranked, outcome) in enumerate(results):
        assert outcome == {"by": "service", "device": "cuda:0", "reason": None}
        assert pairs(ranked) == expected(f"q{number}", ["a", "bbb", "cc"])
    assert len(_pids(home, SERVICE, alive=False)) == 1 and len(_pids(home, SERVICE)) == 1
    assert kinds(home).count("READY") == 1 and not _pids(home, WORKER, alive=False)


def test_twenty_concurrent_callers_each_get_their_own_scores(home):
    ask("warm", ["x"])
    texts = {number: ["t" * (number + 1), "u" * (40 - number), "v" * 7] for number in range(20)}
    results = in_threads(20, lambda number: ask(f"question {number:02d}", texts[number]))
    for number, (ranked, outcome) in enumerate(results):
        assert outcome["by"] == "service"
        assert pairs(ranked) == expected(f"question {number:02d}", texts[number])
    asked = [json.loads(line) for line in (home / "marks/asked").read_text().splitlines()]
    assert sorted(query for _, query in asked) == sorted(["warm"] + [f"question {n:02d}" for n in range(20)])
    assert {role for role, _ in asked} == {SERVICE} and len(_pids(home, SERVICE, alive=False)) == 1


def test_the_socket_is_the_users_alone(home):
    ask("q", ["a"])
    folder, sock = home / rerank.CACHE_REL, home / rerank.CACHE_REL / rerank.SOCKET
    assert stat.S_ISSOCK(sock.stat().st_mode) and stat.S_IMODE(sock.stat().st_mode) == 0o600
    assert stat.S_IMODE(folder.stat().st_mode) == 0o700


def test_ties_keep_the_given_order_and_the_answers_match_a_private_reranker(home):
    texts = ["same", "four", "a longer text", "tied"]
    ranked, outcome = ask("q", texts)
    assert outcome["by"] == "service"
    assert [entry["n"] for entry in ranked] == [2, 0, 1, 3]
    private, _, _ = rerank._started(str(home / rerank.PYTHON_REL))
    assert private("q", texts) == [entry["rerank_score"] for entry in sorted(ranked, key=lambda e: e["n"])]


def test_the_service_ends_after_its_idle_time_and_removes_its_socket(home, monkeypatch):
    monkeypatch.setenv("GOV_RERANK_IDLE_S", "1")
    ask("q", ["a"])
    [pid] = _pids(home, SERVICE)
    assert _wait_until(lambda: not _alive(pid), 10)
    assert not (home / rerank.CACHE_REL / rerank.SOCKET).exists() and kinds(home)[-1] == "END"


def test_a_service_stopped_with_sigterm_removes_its_socket(home):
    ask("q", ["a"])
    [pid] = _pids(home, SERVICE)
    sock = home / rerank.CACHE_REL / rerank.SOCKET
    assert sock.exists()
    os.kill(pid, signal.SIGTERM)
    assert _wait_until(lambda: not _alive(pid), 5)
    assert not sock.exists() and kinds(home)[-1] == "END" and _held_slots(home) == []
    assert ask("q2", ["a"])[1]["by"] == "service"


# --- the GPU only, within its share and a slot (DEC-1032, DEC-1036 T5 and T6) ---

def test_the_gpu_share_is_read_from_the_free_gpu_memory():
    assert rerank_service.gpu_short(lambda: 6 * GIB) is None
    assert "5.0 GiB free" in rerank_service.gpu_short(lambda: 5 * GIB)

    def broken():
        raise RuntimeError("no CUDA")
    assert "could not be read" in rerank_service.gpu_short(broken)


def _service_never_loaded(home: Path) -> bool:
    return not list((home / "marks").glob(f"model-{SERVICE}-*")) and "READY" not in kinds(home)


def test_below_its_gpu_share_the_service_does_not_start_and_the_search_falls_back(home, monkeypatch):
    monkeypatch.setenv("STANDIN_GPU_FREE", str(4 * GIB))
    ranked, outcome = ask("q", ["a", "bb"])
    assert outcome["by"] == "private" and "too little free memory" in outcome["reason"]
    assert pairs(ranked) == expected("q", ["a", "bb"]) and _service_never_loaded(home)
    log = (home / rerank.CACHE_REL / rerank.LOG).read_text()
    assert "\tREFUSED\tthe shared reranker does not start: the GPU" in log and rerank.status()["service_refusals"] == 1


def test_without_a_gpu_no_reranker_loads_and_the_search_goes_on_unranked_named(home, monkeypatch):
    monkeypatch.delenv("STANDIN_GPU_FREE")  # torch sees no GPU at all; nothing hides it
    candidates = [{"n": 0, "text": "a"}, {"n": 1, "text": "bbb"}]
    assert rerank.rerank("q", candidates) == candidates
    outcome = rerank.last_outcome()
    assert outcome["by"] == "unavailable" and outcome["device"] is None
    assert "could not be read" in (home / rerank.CACHE_REL / rerank.LOG).read_text()  # the service's refusal
    assert outcome["reason"].endswith("the private reranker ended without the model (no GPU is available to it)")
    assert not list((home / "marks").glob("model-*"))  # no model loaded, on any device


@pytest.mark.parametrize("allow_cpu", [False, True])
def test_with_the_gpu_hidden_the_service_never_runs_on_the_cpu(home, monkeypatch, allow_cpu):
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "-1")
    if allow_cpu:  # the tests' opt-out reaches the private worker only, never the service
        monkeypatch.setenv("GOV_RERANK_ALLOW_CPU", "1")
    candidates = [{"n": 0, "text": "a"}, {"n": 1, "text": "bbb"}]
    ranked = rerank.rerank("q", candidates)
    outcome = rerank.last_outcome()
    assert "the GPU is hidden from it" in outcome["reason"] and _service_never_loaded(home)
    if allow_cpu:
        assert outcome["by"] == "private" and pairs(ranked) == expected("q", ["a", "bbb"])
    else:
        assert outcome["by"] == "unavailable" and ranked == candidates


def _held_slots(home: Path) -> list[int]:
    """The slots some process holds, found by trying each lock without waiting."""
    held = []
    for i in (0, 1):
        fd = os.open(home / "locks" / f"gov-os-rerank-gpu-{i}.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            held.append(i)
        finally:
            os.close(fd)
    return held


def _hold_slots(home: Path) -> list[int]:
    fds = [os.open(home / "locks" / f"gov-os-rerank-gpu-{i}.lock", os.O_CREAT | os.O_RDWR, 0o600) for i in (0, 1)]
    for fd in fds:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fds


def test_the_service_holds_one_gpu_slot_for_its_life(home):
    assert ask("q", ["a"])[1]["by"] == "service" and _held_slots(home) == [0]
    ask("q2", ["a"])
    assert _held_slots(home) == [0]  # one slot, held between requests, none for the requests
    [pid] = _pids(home, SERVICE)
    os.kill(pid, signal.SIGKILL)
    assert _wait_until(lambda: not _alive(pid), 5) and _wait_until(lambda: _held_slots(home) == [], 5)


def test_the_service_waits_for_a_slot(home, monkeypatch):
    monkeypatch.setenv("GOV_RERANK_GPU_WAIT_S", "10")
    fds = _hold_slots(home)
    threading.Timer(1.0, os.close, (fds[1],)).start()  # a private reranker's session ends
    try:
        ranked, outcome = ask("q", ["a", "bb"])
    finally:
        os.close(fds[0])
    assert outcome["by"] == "service" and pairs(ranked) == expected("q", ["a", "bb"])


def test_without_a_slot_the_service_ends_named_and_searches_go_on_unranked(home, monkeypatch):
    monkeypatch.setenv("GOV_RERANK_GPU_WAIT_S", "1")
    fds = _hold_slots(home)
    try:
        began = time.monotonic()
        results = in_threads(4, lambda number: (rerank.rerank(f"q{number}", [{"n": 0, "text": "a"}]),
                                                rerank.last_outcome()))
        took = time.monotonic() - began
    finally:
        for fd in fds:
            os.close(fd)
    for ranked, outcome in results:
        assert ranked == [{"n": 0, "text": "a"}] and outcome["by"] == "unavailable"
        assert "no GPU slot freed within its wait" in outcome["reason"]
    assert took < 15, took
    assert len(_pids(home, SERVICE, alive=False)) == 1  # the searches that waited for it did not start another
    assert _service_never_loaded(home) and not list((home / "marks").glob(f"model-{WORKER}-*"))
    assert "\tREFUSED\tthe shared reranker does not start: no GPU slot free within 1 s" in \
        (home / rerank.CACHE_REL / rerank.LOG).read_text()


# --- the fallbacks (DEC-374, DEC-1033) ---

def test_a_killed_service_is_replaced_by_the_next_search(home):
    ask("q", ["a"])
    [first] = _pids(home, SERVICE)
    os.kill(first, signal.SIGKILL)
    assert _wait_until(lambda: not _alive(first), 5)
    ranked, outcome = ask("q2", ["a", "bb"])
    assert outcome["by"] == "service" and pairs(ranked) == expected("q2", ["a", "bb"])
    assert len(_pids(home, SERVICE)) == 1 and _pids(home, SERVICE) != [first]


def test_a_service_killed_mid_request_leaves_the_search_to_the_private_reranker(home):
    ask("warm", ["a"])
    [pid] = _pids(home, SERVICE)
    threading.Timer(1.0, os.kill, (pid, signal.SIGKILL)).start()
    began = time.monotonic()
    ranked, outcome = ask("hang", ["a", "bb"])
    assert time.monotonic() - began < 10
    assert outcome["by"] == "private" and outcome["reason"].startswith("the shared reranker did not answer")
    assert pairs(ranked) == expected("hang", ["a", "bb"])
    assert fallbacks(home)[-1][-1] == "private"


def test_a_service_that_does_not_answer_in_time_is_left(home, monkeypatch):
    monkeypatch.setenv("GOV_RERANK_TIMEOUT_S", "1")
    ask("warm", ["a"])
    began = time.monotonic()
    ranked, outcome = ask("hang", ["a", "bb"])
    assert time.monotonic() - began < 8
    assert outcome["by"] == "private" and "timed out" in outcome["reason"]
    assert pairs(ranked) == expected("hang", ["a", "bb"])


def test_a_request_over_the_cap_is_refused_and_the_search_falls_back(home):
    texts = ["x"] * (rerank_service.MAX_TEXTS + 1)
    ranked, outcome = ask("q", texts)
    assert outcome["by"] == "private" and "refused the request" in outcome["reason"]
    assert len(ranked) == len(texts) and all("rerank_score" in entry for entry in ranked)
    assert len(_pids(home, SERVICE)) == 1  # the service stays up for the next search


def test_a_service_that_cannot_start_leaves_the_search_to_the_private_reranker(home, monkeypatch):
    monkeypatch.setenv("STANDIN_FAIL", SERVICE)
    ranked, outcome = ask("q", ["a", "bb"])
    assert outcome["by"] == "private" and outcome["device"] == "cuda:0"
    assert "ended before it listened (exit 1)" in outcome["reason"] and pairs(ranked) == expected("q", ["a", "bb"])
    assert _held_slots(home) == [0]  # the service's slot freed with it; the private reranker holds one
    [line] = fallbacks(home)
    assert line[2].startswith("the shared reranker did not answer") and line[3] == "private"
    assert rerank.fallback_count() == 1 and rerank.status()["fallbacks"] == 1


def test_without_service_or_private_reranker_the_order_is_kept_and_named(home, monkeypatch):
    monkeypatch.setenv("STANDIN_FAIL", "all")
    candidates = [{"n": 0, "text": "a"}, {"n": 1, "text": "bbb"}]
    assert rerank.rerank("q", candidates) == candidates
    outcome = rerank.last_outcome()
    assert outcome["by"] == "unavailable" and "ended without the model" in outcome["reason"]
    assert fallbacks(home)[-1][3].startswith("unavailable: the private reranker ended without the model")


def test_a_session_that_cannot_make_a_socket_falls_back_at_once(home, monkeypatch):
    def refused(*_args, **_kwargs):
        raise PermissionError(1, "Operation not permitted")
    monkeypatch.setattr(rerank.socket, "socket", refused)
    began = time.monotonic()
    ranked, outcome = ask("q", ["a", "bb"])
    assert time.monotonic() - began < 5 and outcome["by"] == "private" and "PermissionError" in outcome["reason"]
    assert pairs(ranked) == expected("q", ["a", "bb"]) and not _pids(home, SERVICE, alive=False)


def test_a_search_that_cannot_write_the_log_still_searches(home, monkeypatch):
    monkeypatch.setenv("STANDIN_FAIL", SERVICE)
    (home / rerank.CACHE_REL).mkdir(parents=True)
    (home / rerank.CACHE_REL / rerank.LOG).mkdir()  # the log's path is not writable as a file
    assert ask("q", ["a"])[1]["by"] == "private"


def test_no_environment_is_unavailable_and_starts_nothing(home):
    (home / ".local/share/gov-os/reranker-venv").unlink()
    candidates = [{"n": 0, "text": "a"}]
    assert rerank.rerank("q", candidates) == candidates
    assert rerank.last_outcome()["by"] == "unavailable" and "no reranker environment" in rerank.last_outcome()["reason"]
    assert not _pids(home, alive=False)


# --- the private worker's GPU slot rule (DEC-1033, without the interim module) ---

def _worker(home: Path, **extra) -> subprocess.Popen:
    env = {**os.environ, **extra}
    return subprocess.Popen([str(home / rerank.PYTHON_REL), "-I", str(rerank._WORKER), rerank.MODEL, rerank.REVISION],
                            env=env, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_the_private_worker_holds_a_slot_or_waits_then_ends_named(home):
    holders = [_worker(home) for _ in range(2)]
    try:
        assert [json.loads(process.stdout.readline()) for process in holders] == [{"device": "cuda:0"}] * 2
        third = _worker(home, GOV_RERANK_GPU_WAIT_S="1")
        out, err = third.communicate(timeout=10)
        assert third.returncode == 75 and out == ""
        assert err.strip() == "gov reranker: no GPU slot free within 1 s; this search goes without reranking"
        assert not (home / "marks" / f"model-{WORKER}-{third.pid}").exists()
        hidden = _worker(home, CUDA_VISIBLE_DEVICES="-1")
        out, err = hidden.communicate(timeout=10)
        assert hidden.returncode == 76 and out == "" and "the GPU is hidden" in err
        holders[1].stdin.close()  # a slot frees: the next worker takes it, then finds no GPU
        holders[1].wait(timeout=10)
        no_gpu = {key: value for key, value in os.environ.items() if key != "STANDIN_GPU_FREE"}
        without = subprocess.run([str(home / rerank.PYTHON_REL), "-I", str(rerank._WORKER), rerank.MODEL,
                                  rerank.REVISION], env=no_gpu, input="", text=True, capture_output=True, timeout=10)
        assert without.returncode == 78 and without.stdout == ""
        assert without.stderr.strip() == ("gov reranker: no GPU is available to it, and no reranker runs on the CPU; "
                                          "this search goes without reranking")
        on_cpu = subprocess.run([str(home / rerank.PYTHON_REL), "-I", str(rerank._WORKER), rerank.MODEL,
                                 rerank.REVISION], env={**no_gpu, "GOV_RERANK_ALLOW_CPU": "1"}, input="", text=True,
                                capture_output=True, timeout=10)
        assert on_cpu.returncode == 0 and json.loads(on_cpu.stdout.splitlines()[0]) == {"device": "cuda:0"}
        for extra in ({"GOV_RERANK_GPU_SLOT": "0"}, {"GOV_RERANK_ALLOW_CPU": "1"}):  # the interim module's slot; tests
            allowed = _worker(home, **extra)
            assert json.loads(allowed.stdout.readline()) == {"device": "cuda:0"}
            allowed.stdin.close()
            allowed.wait(timeout=10)
    finally:
        for process in holders:
            process.stdin.close()
            process.wait(timeout=10)


# --- what gov status and the bundle report ---

def test_gov_status_counts_the_fallbacks(home, monkeypatch):
    assert status_command._reranker() == {"fallbacks": 0, "service_refusals": 0,
                                          "log": str(home / rerank.CACHE_REL / rerank.LOG)}
    monkeypatch.setenv("STANDIN_FAIL", SERVICE)
    ask("q", ["a"])
    ask("q2", ["a"])
    assert status_command._reranker()["fallbacks"] == 2


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
def test_the_bundle_names_who_reranked(home, tmp_path, monkeypatch):
    from gov import store
    from gov.retrieval import lexical, semantic
    from gov.retrieval.retrieve import retrieve

    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for number in (1, 2):
        (tmp_path / f"note{number}.md").write_text(f"# Note {number}\n\nThe heron ledger {number}.\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})

    bundle = retrieve(tmp_path, "heron ledger")
    assert bundle["merge"]["reranked"] and bundle["rerank"] == {"by": "service", "device": "cuda:0", "reason": None}
    monkeypatch.setenv("STANDIN_FAIL", "all")
    for pid in _pids(home, SERVICE):
        os.kill(pid, signal.SIGKILL)
    assert _wait_until(lambda: not _pids(home, SERVICE), 5)
    rerank._started.cache_clear()
    bundle = retrieve(tmp_path, "heron ledger")
    assert not bundle["merge"]["reranked"] and bundle["rerank"]["by"] == "unavailable"
    assert "ended without the model" in bundle["rerank"]["reason"]
