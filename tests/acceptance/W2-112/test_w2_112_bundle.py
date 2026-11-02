"""The bundle's `rerank` entry and `gov status`'s fallback count (KPI success 4, 6 and 7; DEC-1034 items 2 and 3).

- KPI 4: where no private reranker can start either, "the bundle is marked `rerank: unavailable` (DEC-374)"; each
  fallback is logged "and `gov status` counts them".
- KPI 6 as decided by DEC-1036 T5 (b): below its GPU share the service does not start; searches fall back through
  the slot rule or go unranked, named; no reranker on the CPU anywhere.
- KPI 7: without a GPU slot the search goes on unranked, "named: `merge.reranked` false with its reason"; and by
  DEC-1036 T6 (b), with both slots held before any service exists the service cannot start on the GPU either.
- DEC-1034 item 2: the bundle carries a `rerank` entry: `unavailable` with its reason when unranked; otherwise which
  reranker answered and its device. `src/gov/retrieval/retrieve.py` and `src/gov/status/command.py` are in the
  ticket's paths.

What the cases accept: the `rerank` entry at the bundle's top level or in its `merge`; `unavailable` as its value
or a value inside it; its reason as any other text in it, or in a key beside it whose name holds "reason"; which
reranker answered in the KPI's own words (the service, "shared" also taken; a "private" reranker); the device as
`cuda` or `gpu`, or `cpu`. `gov status --json`: a whole number of at least the fallbacks made, under an entry whose
key holds "rerank".

These cases call ``gov.retrieval.retrieve.retrieve(root, query)`` and ``gov status --json`` on a small project of
their own (built as W1-21's tests build theirs: a path map, the kernel's gitleaks rules, the lexical index and the
record store; no vectors, a dead Ollama address and no ``ollama`` on ``PATH``, so nothing real is touched). They need
``gitleaks`` on this machine (the lexical index's secret filter) and skip, with the reason, without it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

import pytest
import yaml

import w2_112_support as support

QUERY = "amber lantern"
NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W2-112 tests", "deletion_rebuild": "authoritative; restored from git only",
}
DOCS = {
    "docs/harbour.md": "# Harbour\n\nThe amber lantern hangs above the harbour gate.\n",
    "docs/kiln.md": "# Kiln\n\nAn amber lantern was found in the old kiln, east of the yard.\n",
    "docs/ledger.md": "# Ledger\n\nThe keeper lists each amber lantern lit at dusk.\n",
}
SERVICE = re.compile(r"service|shared", re.IGNORECASE)
PRIVATE = re.compile(r"private", re.IGNORECASE)
ON_GPU = re.compile(r"cuda|gpu", re.IGNORECASE)
ON_CPU = re.compile(r"\bcpu\b", re.IGNORECASE)


def _git(root, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(root), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "W2-112 tests", "GIT_AUTHOR_EMAIL": "w2-112@example.invalid",
           "GIT_COMMITTER_NAME": "W2-112 tests", "GIT_COMMITTER_EMAIL": "w2-112@example.invalid",
           "GIT_AUTHOR_DATE": "2026-11-01T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-01T12:00:00+00:00"}
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, timeout=60)
    assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"


@pytest.fixture(scope="module")
def tools():
    """A folder of the tools a retrieval may run: git, gitleaks and this interpreter, and no ``ollama``."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine; the lexical index's secret filter cannot run")
    try:
        base = support.short_base()
    except support.Missing as reason:
        pytest.fail(f"the case cannot run on this machine: {reason}", pytrace=False)
    folder = base / "bin"
    folder.mkdir()
    for tool in ("git", "gitleaks", "python3"):
        found = sys.executable if tool == "python3" else shutil.which(tool)
        wrapper = folder / tool
        wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
        wrapper.chmod(0o755)
    yield base
    shutil.rmtree(base, ignore_errors=True)


@pytest.fixture(scope="module")
def project(tools):
    """A small project with its lexical index and record store, never written by a retrieval."""
    root = tools / "p"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    document = yaml.safe_load((support.REPO_ROOT / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    document.pop("decision_register", None)  # the project holds no register
    document["namespaces"] = {name: {"paths": patterns, "memory_class": "governance", **NAMESPACE_FIELDS,
                                     "embedding_policy": "not embedded"}
                              for name, patterns in (("top", ["*"]), ("overlay", ["governance/**"]),
                                                     ("docs", ["docs/**"]))}
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    shutil.copy2(support.REPO_ROOT / "template/.gitleaks.toml", root / ".gitleaks.toml")
    for rel, text in DOCS.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "the W2-112 bundle project")
    script = tools / "build.py"
    script.write_text("import sys\nfrom pathlib import Path\nfrom gov.retrieval import lexical\nfrom gov import store\n"
                      "root = Path(sys.argv[1])\nlexical.refresh(root)\nstore.load(root)\n", encoding="utf-8")
    home = tools / "build-home"
    home.mkdir()
    env = {"PATH": str(tools / "bin"), "HOME": str(home), "PYTHONPATH": str(support.gov_src()),
           "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
           "OLLAMA_HOST": "127.0.0.1:9", "GOV_QUERY_OLLAMA_HOST": "127.0.0.1:9", "TMPDIR": str(tools)}
    done = subprocess.run([sys.executable, str(script), str(root)], capture_output=True, text=True, env=env,
                          timeout=600, cwd=str(tools))
    assert done.returncode == 0, f"the project's index and store could not be built:\n{done.stderr[-3000:]}"
    return root


def _env(box, tools):
    return box.env(PATH=f"{box.state / 'bin'}{os.pathsep}{tools / 'bin'}")


def _retrieve(box, tools, project):
    report = box.start({"mode": "retrieve", "root": str(project), "query": QUERY}, env=_env(box, tools)).wait()
    assert support.raised(report) is None, f"retrieve raised: {support.raised(report)}"
    bundle = report["result"]
    assert isinstance(bundle, dict) and isinstance(bundle.get("merge"), dict), f"no bundle: {bundle!r}"[:800]
    assert bundle.get("evidence"), f"the project's question found no evidence: {bundle!r}"[:800]
    return bundle


def _entry(bundle):
    where, value, reasons = support.rerank_entry(bundle)
    assert where is not None, \
        (f"the bundle carries no `rerank` entry (DEC-1034 item 2), at its top level or in its merge: "
         f"{sorted(bundle)} / {bundle.get('merge')}")[:800]
    return value, reasons


def test_the_bundle_is_marked_rerank_unavailable_with_its_reason_when_nothing_can_rerank(boxes, tools, project):
    box = boxes(environment=False)  # a sandboxed worker: no reranker environment, so no service and no private one
    bundle = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is False, f"the bundle says reranked: {bundle['merge']}"
    value, reasons = _entry(bundle)
    assert support.unavailable(value), f"the bundle's rerank entry does not say `unavailable`: {value!r}"
    assert reasons, f"the bundle says `rerank: unavailable` without its reason: {value!r}"


@pytest.mark.parametrize("how", ["service-down", "no-service-yet"])
def test_with_both_gpu_slots_held_the_bundle_is_unranked_named_with_its_reason(boxes, tools, project, how):
    # "service-down": the service cannot start, and the fallback finds no slot (KPI 7). "no-service-yet": both slots
    # are held before any service exists, so the service cannot start on the GPU either (DEC-1036 T6 (b)).
    box = boxes(settings={support.WAIT_SETTING: 2})
    if how == "service-down":
        box.block_service()
    box.hold_slots()
    bundle = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is False, \
        f"with both GPU slots held ({how}) the bundle says reranked: {bundle['merge']}"
    value, reasons = _entry(bundle)
    assert support.unavailable(value), f"the bundle's rerank entry does not say `unavailable`: {value!r}"
    assert any(re.search(r"slot|gpu", reason, re.IGNORECASE) for reason in reasons), \
        f"the reason given does not name the GPU slot the search waited for: {reasons!r} (KPI 7: named with its reason)"


def test_the_bundle_names_the_service_and_its_gpu_when_the_service_answers(boxes, tools, project):
    box = boxes(gpu=support.ROOM)
    bundle = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is True, f"the bundle was not reranked: {bundle['merge']}"
    value, _ = _entry(bundle)
    text = json.dumps(value)
    assert not support.unavailable(value), f"a reranked bundle says `rerank: unavailable`: {value!r}"
    assert SERVICE.search(text) and ON_GPU.search(text), \
        f"the bundle's rerank entry does not name the service and the GPU it ran on: {value!r}{support.note()}"


@pytest.mark.parametrize("gpu", [support.SHORT, support.NO_GPU], ids=["less-than-its-share-free", "no-gpu"])
def test_below_its_share_the_bundle_never_names_the_cpu_and_gives_its_reason(boxes, tools, project, gpu):
    # DEC-1036 T5 (b): below its share the service does not start; the search falls back through the slot rule
    # (a private reranker on a free GPU slot) or goes on unranked, named with its reason; never the CPU.
    box = boxes(gpu=gpu)
    bundle = _retrieve(box, tools, project)
    value, reasons = _entry(bundle)
    text = json.dumps(value)
    assert not ON_CPU.search(text), f"the bundle names the CPU below the service's share of the GPU: {value!r}"
    if bundle["merge"].get("reranked") is True:
        assert gpu is not support.NO_GPU, f"with no GPU the bundle was reranked, so on the CPU: {value!r}"
        assert PRIVATE.search(text) and ON_GPU.search(text), \
            f"the bundle was reranked below the service's share, but not by a private reranker on the GPU: {value!r}"
    else:
        assert support.unavailable(value), f"an unranked bundle's rerank entry does not say `unavailable`: {value!r}"
        assert any(re.search(r"gpu|cuda|share|memory|slot", reason, re.IGNORECASE) for reason in reasons), \
            f"the unranked bundle does not give its reason (the GPU, its share, its memory or a slot): {reasons!r}"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"a model was loaded on the CPU ({on_cpu}): no reranker on the CPU anywhere (DEC-1036)"


def test_the_bundle_names_a_private_reranker_and_its_gpu_when_the_service_is_down(boxes, tools, project):
    box = boxes(gpu=support.ROOM)
    box.block_service()
    bundle = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is True, f"the fallback did not rerank the bundle: {bundle['merge']}"
    value, _ = _entry(bundle)
    text = json.dumps(value)
    assert PRIVATE.search(text) and ON_GPU.search(text), \
        f"the bundle's rerank entry does not name the private reranker that answered and its GPU: {value!r}"


def test_gov_status_counts_the_searches_that_fell_back(boxes, tools, project):
    box = boxes()
    box.block_service()
    for _ in range(2):
        bundle = _retrieve(box, tools, project)
        assert bundle["merge"].get("reranked") is True, "the fallback private reranker did not rerank the bundle"
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "status", "--json", "--root", str(project)],
                          capture_output=True, text=True, env=_env(box, tools), cwd=str(box.work), timeout=600,
                          stdin=subprocess.DEVNULL)
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        pytest.fail(f"gov status --json gave no JSON (exit {done.returncode}): {done.stderr[-1500:]}", pytrace=False)

    def counts(value, under=False):
        if isinstance(value, dict):
            return [n for key, item in value.items() for n in counts(item, under or "rerank" in str(key).lower())]
        if isinstance(value, list):
            return [n for item in value for n in counts(item, under)]
        return [value] if under and isinstance(value, int) and not isinstance(value, bool) else []

    assert any(number >= 2 for number in counts(answer)), \
        f"gov status does not count the 2 searches that fell back (no count under a rerank entry): {done.stdout[:1500]}"
