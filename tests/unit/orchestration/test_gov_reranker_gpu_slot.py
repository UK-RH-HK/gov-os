"""The reranker's GPU slot module (governance/project/orchestration/tools/gov_reranker_gpu_slot.py, DEC-1033): a
reranker worker without a GPU slot waits for one, then ends named before torch, and the search goes on unranked; no
reranker grinds on the CPU unless GOV_RERANK_ALLOW_CPU=1; any other Python of that environment is untouched.

Hermetic: a throwaway venv (``--without-pip``) in a temporary HOME, at the reranker environment's path, holds a copy of
the module, its ``.pth`` line and stand-in ``torch`` and ``sentence_transformers`` modules that only leave a mark;
stand-in workers named ``rerank_worker.py``; the lock folder is temporary (GOV_RERANK_GPU_LOCK_DIR). No model, no
GPU, never the real reranker environment.
Run: python3 -m pytest -q tests/unit/orchestration/test_gov_reranker_gpu_slot.py."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
MODULE = REPO / "governance/project/orchestration/tools/gov_reranker_gpu_slot.py"
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import rerank  # noqa: E402

NAMED = "gov reranker: no GPU slot free within {} s; this search goes without reranking"

# A stand-in worker: leaves a mark, imports (the stand-in) torch, says what it was given, and holds until its input
# closes, as the real worker holds its model for the session's life.
WORKER = """import json, os, sys
open(os.path.join(os.environ["MARKS"], "worker-%d" % os.getpid()), "w").close()
import torch
print(json.dumps({"slot": os.environ.get("GOV_RERANK_GPU_SLOT"), "cuda": os.environ.get("CUDA_VISIBLE_DEVICES")}),
      flush=True)
sys.stdin.read()
"""
FAKE_TORCH = """import os
if os.environ.get("MARKS"):
    open(os.path.join(os.environ["MARKS"], "torch-%d" % os.getpid()), "w").close()
"""
# The real rerank_worker.py imports this; it scores a text by its length.
FAKE_SENTENCE_TRANSFORMERS = """import os
if os.environ.get("MARKS"):
    open(os.path.join(os.environ["MARKS"], "model-%d" % os.getpid()), "w").close()
class CrossEncoder:
    def __init__(self, model, revision=None):
        pass
    def predict(self, pairs):
        return [float(len(text)) for _, text in pairs]
"""


@pytest.fixture(scope="module")
def home(tmp_path_factory):
    """A temporary HOME whose reranker environment is a throwaway venv carrying the module and its ``.pth``."""
    home = tmp_path_factory.mktemp("home")
    venv = home / ".local/share/gov-os/reranker-venv"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
    python = home / rerank.PYTHON_REL
    assert python.exists()
    purelib = subprocess.run([str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                             capture_output=True, text=True, check=True).stdout.strip()
    site = Path(purelib)
    assert str(site).startswith(str(home)), site  # the throwaway venv's, never the real one's
    shutil.copy(MODULE, site / "gov_reranker_gpu_slot.py")
    (site / "gov-reranker-gpu-slot.pth").write_text("import gov_reranker_gpu_slot\n")
    (site / "torch.py").write_text(FAKE_TORCH)
    (site / "sentence_transformers.py").write_text(FAKE_SENTENCE_TRANSFORMERS)
    return home


@pytest.fixture
def setup(home, tmp_path):
    """``(python, worker, env, marks)``: a lock folder and a mark folder of this test's own."""
    locks, marks, scripts = tmp_path / "locks", tmp_path / "marks", tmp_path / "scripts"
    for folder in (locks, marks, scripts):
        folder.mkdir()
    worker = scripts / "rerank_worker.py"
    worker.write_text(WORKER)
    env = {k: v for k, v in os.environ.items()
           if k != "CUDA_VISIBLE_DEVICES" and not k.startswith(("GOV_RERANK_", "PYTHON"))}
    env.update(GOV_RERANK_GPU_LOCK_DIR=str(locks), MARKS=str(marks), HOME=str(home),
               GOV_RERANK_GPU_LIMITS=str(tmp_path / "limits.json"))  # none planted: the default of 2 (DEC-1039)
    return str(home / rerank.PYTHON_REL), worker, env, marks


@pytest.mark.parametrize("planted, slots", [(3, 3), (0, 2), ("three", 2), (None, 2)])
def test_the_slot_count_follows_the_dispatchers_derived_number(setup, tmp_path, planted, slots):
    """DEC-1037 (4), DEC-1039 (1b): with GOV_RERANK_GPU_SLOTS unset, the count is the dispatcher's `rerank_gpu_slots`
    (limits.json); 0 (no GPU), a non-number or no file: 2. Each worker past the count waits, then ends named."""
    python, worker, env, _ = setup
    if planted is not None:
        (tmp_path / "limits.json").write_text(json.dumps({"rerank_gpu_slots": planted}))
    started = [start(python, worker, env) for _ in range(slots)]
    try:
        assert sorted(first_line(p)["slot"] for p in started) == [str(i) for i in range(slots)]
        extra = start(python, worker, env, GOV_RERANK_GPU_WAIT_S="0")
        out, err = extra.communicate(timeout=15)
        assert extra.returncode == 75 and out == ""
    finally:
        stop(*started)


def test_the_environment_wins_over_the_derived_number(setup, tmp_path):
    python, worker, env, _ = setup
    (tmp_path / "limits.json").write_text(json.dumps({"rerank_gpu_slots": 3}))
    started = [start(python, worker, env, GOV_RERANK_GPU_SLOTS="1")]
    try:
        assert first_line(started[0])["slot"] == "0"
        extra = start(python, worker, env, GOV_RERANK_GPU_SLOTS="1", GOV_RERANK_GPU_WAIT_S="0")
        assert extra.wait(timeout=15) == 75
    finally:
        stop(*started)


def start(python, script, env, *args, **extra):
    return subprocess.Popen([python, "-I", str(script), *args], env={**env, **extra}, text=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def first_line(process):
    line = process.stdout.readline()
    return json.loads(line) if line else None


def stop(*processes):
    for process in processes:
        if process.poll() is None:
            process.stdin.close()
            process.wait(timeout=10)


@pytest.fixture
def holders(setup):
    """Two workers holding slots 0 and 1, as two sessions' rerankers do."""
    python, worker, env, _ = setup
    started = [start(python, worker, env) for _ in range(2)]
    try:
        assert sorted(first_line(p)["slot"] for p in started) == ["0", "1"]
        yield started
    finally:
        stop(*started)


def test_a_free_slot_keeps_the_gpu(setup):
    python, worker, env, marks = setup
    process = start(python, worker, env)
    try:
        assert first_line(process) == {"slot": "0", "cuda": None}
    finally:
        stop(process)


def test_without_a_slot_it_waits_then_ends_named_before_torch(setup, holders):
    python, worker, env, marks = setup
    began = time.monotonic()
    third = start(python, worker, env, GOV_RERANK_GPU_WAIT_S="2")
    out, err = third.communicate(timeout=15)
    took = time.monotonic() - began
    assert third.returncode == 75
    assert out == ""  # nothing the caller could read as "the model is loaded"
    assert err.strip() == NAMED.format(2)
    assert 1.9 <= took < 6, took  # it waited the whole wait, and no longer
    assert sorted(path.name.split("-")[0] for path in marks.iterdir()) == ["torch", "torch", "worker", "worker"], \
        "the third reached its script or imported torch"  # the marks are the two holders' only


def test_the_default_wait_is_twenty_seconds(setup, holders):
    python, worker, env, _ = setup
    third = start(python, worker, env)
    try:
        time.sleep(3)
        assert third.poll() is None  # still waiting at 3 s
    finally:
        third.kill()
        third.wait()


def test_a_slot_freed_during_the_wait_is_taken(setup, holders):
    python, worker, env, _ = setup
    third = start(python, worker, env, GOV_RERANK_GPU_WAIT_S="15")
    try:
        time.sleep(1.5)
        assert third.poll() is None  # waiting, not ended and not on the CPU
        stop(holders[0])  # the session holding slot 0 ends
        freed = time.monotonic()
        answer = first_line(third)
        assert time.monotonic() - freed < 3  # taken at the next poll, about a second
        assert answer["cuda"] is None and answer["slot"] in ("0", "1")
    finally:
        stop(third)


def test_the_opt_out_restores_the_cpu_fallback(setup, holders):
    python, worker, env, _ = setup
    began = time.monotonic()
    third = start(python, worker, env, GOV_RERANK_ALLOW_CPU="1", GOV_RERANK_GPU_WAIT_S="15")
    try:
        assert first_line(third) == {"slot": None, "cuda": "-1"}
        assert time.monotonic() - began < 5  # at once, as before: no wait
    finally:
        stop(third)


def test_a_hidden_gpu_ends_named_unless_the_opt_out(setup):
    python, worker, env, marks = setup
    for hidden in ("-1", ""):
        process = start(python, worker, env, CUDA_VISIBLE_DEVICES=hidden)
        out, err = process.communicate(timeout=10)
        assert process.returncode == 76 and out == ""
        assert err.startswith("gov reranker: the GPU is hidden from it") and "this search goes without reranking" in err
    assert not list(marks.iterdir())
    process = start(python, worker, env, CUDA_VISIBLE_DEVICES="-1", GOV_RERANK_ALLOW_CPU="1")
    try:
        assert first_line(process) == {"slot": None, "cuda": "-1"}
    finally:
        stop(process)


def test_a_python_that_is_not_the_worker_is_untouched(setup, holders, tmp_path):
    python, _, env, _ = setup
    other = tmp_path / "scripts" / "other.py"
    other.write_text(WORKER)
    check = "import os, sys, json; print(json.dumps([os.environ.get('GOV_RERANK_GPU_SLOT'), " \
            "os.environ.get('CUDA_VISIBLE_DEVICES'), 'gov_reranker_gpu_slot' in sys.modules]))"
    began = time.monotonic()
    for argv in ([python, "-I", "-c", check], [python, "-c", check, "rerank_worker.py"],
                 [python, "-I", str(other), "rerank_worker.py"]):
        result = subprocess.run(argv, env={**env, "GOV_RERANK_GPU_WAIT_S": "15"}, input="", text=True,
                                capture_output=True, timeout=10)
        assert result.returncode == 0 and result.stderr == "", (argv, result.stderr)
        answer = json.loads(result.stdout.splitlines()[0])
        if isinstance(answer, list):
            assert answer == [None, None, True]  # the .pth ran, and did nothing
        else:
            assert answer == {"slot": None, "cuda": None}
    assert time.monotonic() - began < 8  # none of them waited for a slot


def test_a_python_that_is_not_the_worker_takes_no_slot(setup):
    python, worker, env, _ = setup
    other = Path(worker).with_name("serve.py")
    other.write_text(WORKER)
    bystander = start(python, other, env)
    try:
        assert first_line(bystander) == {"slot": None, "cuda": None}
        workers = [start(python, worker, env) for _ in range(2)]
        try:
            assert sorted(first_line(p)["slot"] for p in workers) == ["0", "1"]
        finally:
            stop(*workers)
    finally:
        stop(bystander)


def test_the_worker_started_as_a_module_is_recognised(setup, holders, tmp_path):
    python, _, env, marks = setup
    package = tmp_path / "pkg" / "gov" / "retrieval"
    package.mkdir(parents=True)
    for folder in (package.parent, package):
        (folder / "__init__.py").write_text("")
    (package / "rerank_worker.py").write_text(WORKER)
    result = subprocess.run([python, "-m", "gov.retrieval.rerank_worker", "Qwen", "rev"], cwd=tmp_path / "pkg",
                            env={**env, "GOV_RERANK_GPU_WAIT_S": "1"}, input="", text=True, capture_output=True,
                            timeout=10)
    assert result.returncode == 75 and result.stdout == "" and result.stderr.strip() == NAMED.format(1)


@pytest.mark.parametrize("bad", [{"GOV_RERANK_GPU_SLOTS": "two"}, {"GOV_RERANK_GPU_WAIT_S": "soon"},
                                 {"GOV_RERANK_GPU_LOCK_DIR": "/nonexistent/gov-os-locks"}])
def test_an_internal_error_ends_named(setup, bad):
    python, worker, env, marks = setup
    process = start(python, worker, env, **bad)
    out, err = process.communicate(timeout=10)
    assert process.returncode == 70 and out == ""
    assert err.startswith("gov reranker: the GPU slot check failed (") and \
        err.rstrip().endswith("; this search goes without reranking"), err
    assert len(err.strip().splitlines()) == 1  # one line, no traceback
    assert not list(marks.iterdir())  # neither the script nor torch


# The real caller: gov.retrieval.rerank starting the real rerank_worker.py with the environment's interpreter.
CANDIDATES = [{"chunk_id": "short", "text": "ab"}, {"chunk_id": "long", "text": "abcdef"}]


@pytest.fixture
def caller(setup, monkeypatch):
    _, _, env, marks = setup
    for key in list(os.environ):
        if key == "CUDA_VISIBLE_DEVICES" or key.startswith("GOV_RERANK_"):
            monkeypatch.delenv(key)
    for key in ("HOME", "GOV_RERANK_GPU_LOCK_DIR", "MARKS"):
        monkeypatch.setenv(key, env[key])
    rerank._started.cache_clear()
    yield marks
    rerank._started.cache_clear()


def test_the_search_reranks_on_a_free_slot(caller):
    ranked = rerank.rerank("a question", CANDIDATES)
    assert [(entry["chunk_id"], entry["rerank_score"]) for entry in ranked] == [("long", 6.0), ("short", 2.0)]


def test_the_search_goes_on_unranked_when_no_slot_frees(caller, holders, monkeypatch, capfd):
    monkeypatch.setenv("GOV_RERANK_GPU_WAIT_S", "1")
    ranked = rerank.rerank("a question", CANDIDATES)
    assert ranked == CANDIDATES and not any("rerank_score" in entry for entry in ranked)  # merge.reranked: false
    assert NAMED.format(1) in capfd.readouterr().err  # the caller's standard error names why
    assert not [path for path in caller.iterdir() if path.name.startswith("model-")]  # no model was loaded
