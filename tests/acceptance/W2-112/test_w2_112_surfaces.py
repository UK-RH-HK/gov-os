"""The KPI words that need surfaces outside W2-112's allowed paths (the lead's scope package decides who builds them).

- KPI success 4: where no private reranker can start either, "the bundle is marked `rerank: unavailable`
  (DEC-374)", and "`gov status` counts" the searches that fell back. The bundle is built in
  ``src/gov/retrieval/retrieve.py`` and ``gov status`` in ``src/gov/status/``; neither is in W2-112's paths.
- KPI success 6: below its share of the GPU the service "starts on the CPU, named, and alerts". The device is
  named in the bundle; where the alert goes is not stated, so any trace a reader can find counts (a ``logging``
  record, standard error, or a file under ``HOME``).

These cases call ``gov.retrieval.retrieve.retrieve(root, query)`` and ``gov status --json`` on a small project
of their own (built as W1-21's tests build theirs: a path map, the kernel's gitleaks rules, the lexical index and
the record store; no vectors, a dead Ollama address and no ``ollama`` on ``PATH``, so nothing real is touched).
They need ``gitleaks`` on this machine and skip, with the reason, without it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

import w2_112_support as support

pytestmark = pytest.mark.w2_112_surfaces

QUERY = "amber lantern"
SHORT = {"present": True, "total": 16 * support.GIB, "free": 1 * support.GIB, "name": "Stand-in GPU"}
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
    base = support.short_base()
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
    _git(root, "commit", "-q", "-m", "the W2-112 surfaces project")
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


def _retrieve(box, tools, project):
    env = box.env(PATH=f"{box.state / 'bin'}{os.pathsep}{tools / 'bin'}")
    report = box.start({"mode": "retrieve", "root": str(project), "query": QUERY}, env=env).wait()
    assert support.raised(report) is None, f"retrieve raised: {support.raised(report)}"
    bundle = report["result"]
    assert isinstance(bundle, dict) and isinstance(bundle.get("merge"), dict), f"no bundle: {bundle!r}"[:800]
    assert bundle.get("evidence"), f"the project's question found no evidence: {bundle!r}"[:800]
    return bundle, report


def _rerank_entries(bundle):
    """Every ``key: value`` of the bundle or its ``merge`` whose key names the rerank (``reranked`` aside)."""
    found = []
    for scope in (bundle, bundle.get("merge") or {}):
        for key, value in scope.items():
            if "rerank" in key.lower() and key != "reranked":
                found.append((key, value))
    return found


def test_the_bundle_is_marked_rerank_unavailable_when_nothing_can_rerank(boxes, tools, project):
    box = boxes(environment=False)  # a sandboxed worker: no reranker environment, so no service and no private one
    bundle, _ = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is False, f"the bundle says reranked: {bundle['merge']}"
    marks = [value for key, value in _rerank_entries(bundle) if key == "rerank"]
    assert "unavailable" in marks, \
        f"the bundle is not marked `rerank: unavailable` (DEC-374, the KPI): its rerank entries are {_rerank_entries(bundle)}"


def test_the_bundle_names_the_cpu_when_the_service_runs_there(boxes, tools, project):
    box = boxes(gpu=SHORT)
    bundle, _ = _retrieve(box, tools, project)
    assert bundle["merge"].get("reranked") is True, f"the bundle was not reranked: {bundle['merge']}"
    named = [(key, value) for key, value in _rerank_entries(bundle) if "cpu" in json.dumps(value).lower()]
    assert named, \
        f"below its share of the GPU the service runs on the CPU, and the bundle does not name it: {_rerank_entries(bundle)}"


def test_the_service_alerts_when_it_starts_on_the_cpu_below_its_share(boxes):
    box = boxes(gpu=SHORT)
    since = time.time()
    query, given = support.query_of("alert"), support.candidates("alert", 4)
    report = box.search(query, given)
    assert support.raised(report) is None, f"the search raised: {support.raised(report)}"
    support.check_scored(report["result"], query, given)
    found = support.traces(box, report, since)
    assert any(re.search(r"\bcpu\b", trace, re.IGNORECASE) for trace in found), \
        ("the service started on the CPU below its share of the GPU and left no alert a reader can find (no logging "
         f"record, nothing on standard error, no file under HOME names the CPU): {found!r}")[:1500]


def test_gov_status_counts_the_searches_that_fell_back(boxes, tools, project):
    box = boxes()
    folder = box.socket.parent  # the service cannot start: its socket's folder cannot be made
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.write_text("not a folder\n", encoding="utf-8")
    for _ in range(2):
        bundle, _ = _retrieve(box, tools, project)
        assert bundle["merge"].get("reranked") is True, "the fallback private reranker did not rerank the bundle"
    env = box.env(PATH=f"{box.state / 'bin'}{os.pathsep}{tools / 'bin'}")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "status", "--json", "--root", str(project)],
                          capture_output=True, text=True, env=env, cwd=str(box.work), timeout=600,
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
