"""S2 (and failure line 1): no private reranker is left as a mode of the product (DEC-1048 (5), DEC-1046 (1),
DEC-1033, DEC-1065 (1)).

- ``rerank_worker.py`` run as a program ends at once, named ("no private reranker runs: the shared service
  reranks", a non-zero exit), before torch or the model loads: run with the planted reranker environment's
  interpreter, whose ``.pth`` records every import of ``torch``, ``sentence_transformers`` and ``transformers``;
  whatever the settings (``GOV_RERANK_ALLOW_CPU=1``, every GPU slot held with a long wait, the GPU hidden, the
  interim module's ``GOV_RERANK_GPU_SLOT`` already set) and with a request on its input. It keeps what the service
  shares (``take_slot``, ``load``, ``scores``, ``device_of``).
- ``gov.retrieval.rerank`` holds no path that starts a reranker process except the shared service: ``_started`` and
  its cache are gone; every process start in ``rerank.py`` names the service; no process start anywhere in
  ``src/gov/`` names ``rerank_worker.py`` (an AST search: a call of ``subprocess``'s ``Popen``, ``run``, ``call``,
  ``check_call``, ``check_output``, ``os.exec*``, ``os.spawn*``, ``os.posix_spawn*`` or
  ``asyncio.create_subprocess_*`` whose arguments name the worker's file or a module-level name bound to it).
- ``GOV_RERANK_ALLOW_CPU=1`` opens no CPU path: a search with it set and no usable GPU stays unranked, named, with no
  model loaded and no private started.
- ``last_outcome()``'s ``by`` is never ``private``: held over every S1 kind (``unavailable``) in
  ``test_w2_145_s1_unreachable.py`` and the service's own answers (``service``) in ``test_w2_145_s3_slots.py``.

The worker runs and the source search need no Unix socket: they run in the launch sandbox too.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import time
from pathlib import Path

import pytest

import w2_145_support as support
from w2_145_support import base, candidates, check_unranked, query_of, raised

WORKER_RUNS = {
    "plain": {},
    "gpu-rerank-allow-cpu": {"GOV_RERANK_ALLOW_CPU": "1"},
    "every-slot-held-long-wait": {support.WAIT_SETTING: "30"},
    "gpu-hidden": {"CUDA_VISIBLE_DEVICES": "-1"},
    "interim-module-slot-set": {"GOV_RERANK_GPU_SLOT": "0"},
}
AT_ONCE_S = 3.0  # "ends at once": the interpreter's start and the exit, far under any slot wait or model load
PROCESS_STARTS = {("subprocess", name) for name in ("Popen", "run", "call", "check_call", "check_output")} | {
    ("asyncio", "create_subprocess_exec"), ("asyncio", "create_subprocess_shell")}
OS_STARTS = re.compile(r"^(exec[lv]p?e?|spawn[lv]p?e?|posix_spawnp?|system|popen)$")


def _worker_path() -> Path:
    return base.gov_src() / "gov" / "retrieval" / "rerank_worker.py"


@pytest.mark.parametrize("how", list(WORKER_RUNS), ids=list(WORKER_RUNS))
def test_s2_rerank_worker_run_as_a_program_ends_at_once_named_before_torch_or_the_model(boxes, how):
    box = boxes()
    extra = dict(WORKER_RUNS[how])
    if how == "every-slot-held-long-wait":
        box.hold_slots(*range(box.slots))
    env = box.env(**extra)
    began = time.monotonic()
    try:
        done = subprocess.run([str(box.venv / "bin" / "python"), "-I", str(_worker_path()), support.MODEL,
                               support.REVISION], input='["a question", ["a text", "another"]]\n', text=True,
                              capture_output=True, env=env, timeout=60, cwd=str(box.work))
    except subprocess.TimeoutExpired:
        pytest.fail(f"rerank_worker.py run as a program ({how}) had not ended after 60 s", pytrace=False)
    seconds = time.monotonic() - began
    who = f"rerank_worker.py run as a program ({how})"
    assert done.returncode != 0, \
        f"{who} ended 0 (stdout {done.stdout[:300]!r}): it is to end named with a non-zero exit"
    said = " ".join(done.stderr.split()).lower()
    assert support.NAMED_EXIT in said, \
        f"{who}: its standard error does not say {support.NAMED_EXIT!r}: {done.stderr[-600:]!r}"
    assert seconds <= AT_ONCE_S, f"{who} took {seconds:.1f} s to end: it is to end at once"
    assert done.stdout.strip() == "", f"{who} wrote an answer or a device line: {done.stdout[:300]!r}"
    imported = sorted({record["module"] for record in box.imports() if "rerank_worker.py" in record["argv"]})
    assert imported == [], f"{who} imported {imported} before it ended: it is to end before torch or the model loads"
    loads = [(record["pid"], record["device"]) for record in box.loads()]
    assert loads == [], f"{who} loaded the model: {loads}"


def test_s2_rerank_worker_keeps_what_the_service_shares_and_imports_no_library_of_the_model():
    spec = importlib.util.spec_from_file_location("w145_rerank_worker", _worker_path())
    module = importlib.util.module_from_spec(spec)
    before = {name for name in __import__("sys").modules if name.split(".")[0] in support.HEAVY}
    spec.loader.exec_module(module)
    after = {name for name in __import__("sys").modules if name.split(".")[0] in support.HEAVY}
    for name in ("take_slot", "load", "scores", "device_of"):
        assert callable(getattr(module, name, None)), \
            f"rerank_worker.py no longer has {name}(), which the shared service shares (S2)"
    assert after - before == set(), f"importing rerank_worker.py imported {sorted(after - before)}"


def test_s2_gov_retrieval_rerank_has_no_private_reranker_left():
    from gov.retrieval import rerank

    assert not hasattr(rerank, "_started"), \
        "gov.retrieval.rerank still has _started (the private reranker's start and its cache): S2 says it is gone"


def _starts(tree: ast.AST):
    """Every call in ``tree`` that starts a process: ``(node, its arguments' source)``."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func, owner, name = node.func, None, None
        if isinstance(func, ast.Attribute):
            name = func.attr
            owner = func.value.id if isinstance(func.value, ast.Name) else None
        elif isinstance(func, ast.Name):
            name = func.id
        hit = (owner, name) in PROCESS_STARTS or (owner == "os" and OS_STARTS.match(name or "")) or \
            (owner is None and name in {"Popen", "check_output", "check_call", "create_subprocess_exec"})
        if hit:
            parts = [ast.unparse(argument) for argument in node.args] + \
                    [ast.unparse(keyword.value) for keyword in node.keywords]
            yield node, " ".join(parts)


def _names_bound_to(tree: ast.AST, word: str) -> set[str]:
    """The names a module assigns from an expression that holds ``word`` (as ``_WORKER = ....with_name(...)``),
    followed through further assignments from those names."""
    names, changed = set(), True
    assigns = [node for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.AnnAssign))]
    while changed:
        changed = False
        for node in assigns:
            value = node.value
            if value is None:
                continue
            text = ast.unparse(value)
            if word in text or any(re.search(rf"\b{re.escape(name)}\b", text) for name in names):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    for leaf in ast.walk(target):
                        if isinstance(leaf, ast.Name) and leaf.id not in names:
                            names.add(leaf.id)
                            changed = True
    return names


def test_s2_no_process_start_in_src_gov_names_rerank_worker():
    found = []
    root = base.gov_src() / "gov"
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        bound = _names_bound_to(tree, "rerank_worker")
        for node, text in _starts(tree):
            if "rerank_worker" in text or any(re.search(rf"\b{re.escape(name)}\b", text) for name in bound):
                found.append(f"{path.relative_to(root.parent)}:{node.lineno}: {text[:160]}")
    assert found == [], f"a process start in src/gov/ names rerank_worker.py (a private reranker): {found}"


def test_s2_every_process_start_in_rerank_names_the_shared_service():
    path = base.gov_src() / "gov" / "retrieval" / "rerank.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    bound = _names_bound_to(tree, "rerank_service")
    starts = list(_starts(tree))
    assert starts, "rerank.py starts no process at all: the shared service is to be started by a search (W2-112)"
    other = [f"rerank.py:{node.lineno}: {text[:160]}" for node, text in starts
             if "rerank_service" not in text and not any(re.search(rf"\b{re.escape(n)}\b", text) for n in bound)]
    assert other == [], f"rerank.py starts a process that is not the shared service: {other}"


ALLOW_CPU_SEARCHES = {
    # the service cannot start (a folder stands at its socket's place) and there is no GPU
    "service-blocked-no-gpu": {"gpu": base.NO_GPU, "block": True, "env": {}},
    # the service starts and refuses (no GPU: its free memory cannot be read)
    "service-refuses-no-gpu": {"gpu": base.NO_GPU, "block": False, "env": {}},
    # the GPU is there but hidden from the search's processes
    "gpu-hidden": {"gpu": base.ROOM, "block": False, "env": {"CUDA_VISIBLE_DEVICES": "-1"}},
}


@pytest.mark.parametrize("how", list(ALLOW_CPU_SEARCHES), ids=list(ALLOW_CPU_SEARCHES))
def test_s2_gov_rerank_allow_cpu_opens_no_cpu_path_in_a_search(boxes, how):
    plan = ALLOW_CPU_SEARCHES[how]
    box = boxes(gpu=plan["gpu"])
    if plan["block"]:
        box.block_service()
    env = box.env(GOV_RERANK_ALLOW_CPU="1", **plan["env"])
    query, given = query_of(f"cpu-{how}"), candidates(f"cpu-{how}", 5)
    report = box.search(query, given, env=env)
    who = f"the search with GOV_RERANK_ALLOW_CPU=1 ({how})"
    assert raised(report) is None, f"{who} raised: {raised(report)}"
    check_unranked(report["result"], given, who)
    outcome = report.get("outcome") or {}
    assert outcome.get("by") == "unavailable", f"{who}: last_outcome() is {outcome}"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"{who}: a model was loaded on the CPU ({on_cpu})"
    support.check_no_private(box, report, who)
