"""W2-69, added after implementation from the review (DEC-136), behaviours 4 and 5: the rebuild's compaction step.

KPI 3, success: "Deleted text does not survive a rebuild: after a full rebuild,
text deleted from a SQLite store is in neither its rows nor its free pages ..."
Failure: "Deleted text left in a store's free pages after a rebuild."

Behaviour 4: ``gov rebuild --json`` given the project as a relative path (``--root
.`` from the project's folder; the folder's name from its parent) returns its
result with exit 0 and compacts every SQLite store it builds, as it does with an
absolute path: no store is left with a free page. Each case rebuilds the project
first by its absolute path, deletes most of its pages, and rebuilds it by the
relative path, so a store that is not compacted keeps free pages. The code-graph
store is the real tool's where ``codebase-memory-mcp`` is on ``PATH`` (as W1-16's
cases: ``local_only``, it starts the tool's daemon, so the cases run alone);
without it, a stand-in first on ``PATH`` writes a SQLite store with free pages in
the tool's home. Today the rebuild raises after building, exit 1 with a traceback,
and leaves the code-graph store uncompacted.

Behaviour 5: another process holds a SQLite store under ``.gov-runtime/`` during
``gov rebuild --json``, so the rebuild cannot compact it: the rebuild names that
store, with the reason, on its standard error as well as in its JSON result. The
held store is the code-graph store, written by the stand-in tool, which starts the
holding process (an exclusive lock, so no way of compacting gets through) before
it returns: the code index is the rebuild's last store, so the store is held from
its build to the end of the rebuild. Its exit code is not asked. Today the JSON
result alone names it.

Every rebuild is full (never ``--no-embeddings``): the semantic index is built
against the first batch's stand-in embedder on a loopback port.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import time
from pathlib import Path

import pytest

import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
PAGES, KEPT = 24, 4
REAL_TOOL = support.CODE_TOOL is not None

needs_vectors = pytest.mark.skipif(importlib.util.find_spec("sqlite_vec") is None,
                                   reason="sqlite_vec is not installed: the semantic index cannot be built")


@pytest.fixture()
def embedder():
    stand_in = support.EmbedderStandIn()
    yield stand_in
    stand_in.close()


def _files():
    files = {f"docs/page{n:02d}.md": f"# Page {n}\n\n" + support.prose(4000, f"page{n}") for n in range(PAGES)}
    files["src/app.py"] = "def keeper():\n    return 1\n\n\ndef caller():\n    return keeper()\n"
    return files


def _free(project):
    return {str(path.relative_to(project)): support.free_pages(path) for path in support.sqlite_files(project / R)}


# --------------------------------------------------------------------------
# Behaviour 4: a relative root
# --------------------------------------------------------------------------

HOW = ("dot-from-the-project", "a-relative-path-from-its-parent")


@needs_vectors
@pytest.mark.parametrize("how", HOW)
def test_a_rebuild_given_the_project_relatively_returns_its_result_and_compacts_every_store(sandbox, embedder, how):
    project = support.make_rebuild_project(sandbox, _files())
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=REAL_TOOL)
    if not REAL_TOOL:
        env = review.with_code_stand_in(env, review.install_code_stand_in(sandbox))
    daemon = support.code_daemon_dir(project)
    try:
        first = support.rebuild(project, env)
        assert support.store_status(first, "codeintel") == "recreated", (
            f"premise: the code-graph store was built by the rebuild given the absolute path\n{first.describe()}")
        assert support.sqlite_files(project / R / "codeintel"), "premise: a SQLite store in the code-graph tool's home"
        for n in range(KEPT, PAGES):
            (project / f"docs/page{n:02d}.md").unlink()
        support.commit_all(project, "most pages deleted")
        if how == "dot-from-the-project":
            run = support.run_gov(project, env, "rebuild", "--json", "--root", ".")
        else:
            run = support.run_gov(project.parent, env, "rebuild", "--json", "--root", project.name)
        free = _free(project)
    finally:
        if daemon is not None and daemon.is_dir():
            shutil.rmtree(daemon, ignore_errors=True)
    assert run.returncode == 0 and "Traceback" not in run.stderr, (
        f"gov rebuild --json given the project relatively ({how}) did not return its result\n{run.describe()}")
    envelope = run.envelope()
    assert envelope.get("ok") is True and (envelope.get("result") or {}).get("stores"), (
        f"gov rebuild --json ({how}): no result envelope\n{run.describe()}")
    for store in ("lexical", "semantic", "codeintel"):
        assert support.store_status(run, store) == "recreated", f"{how}: the {store} store was not recreated"
    assert f"{R}/store.db" in free and any(rel.startswith(f"{R}/codeintel/") for rel in free), (
        f"premise: the record store and the code-graph store are SQLite files under {R}/: {sorted(free)}")
    assert all(count == 0 for count in free.values()), (
        f"gov rebuild --json given the project relatively ({how}) left SQLite stores with free pages (not "
        f"compacted): { {rel: n for rel, n in free.items() if n} }")


# --------------------------------------------------------------------------
# Behaviour 5: a store the rebuild cannot compact is named on standard error
# --------------------------------------------------------------------------

_REASON = re.compile(r"lock|busy|held|holds|in use", re.IGNORECASE)


def _strings(value):
    """Every key and string value of a JSON value."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def _json_reason(result, rel):
    """The reason the JSON result gives next to the store's name: the string value under a key that names it."""
    found = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if rel in str(key) and isinstance(item, str):
                    found.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(result)
    return found


@needs_vectors
def test_a_store_the_rebuild_cannot_compact_is_named_with_its_reason_on_standard_error(sandbox, embedder):
    project = support.make_rebuild_project(sandbox, _files())
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    env = review.with_code_stand_in(env, review.install_code_stand_in(sandbox))
    hold = sandbox.elsewhere / "code-store-hold"
    env["W2_69_HOLD"] = str(hold)
    daemon = support.code_daemon_dir(project)
    try:
        run = support.run_gov(project, env, "rebuild", "--json")
    finally:
        Path(str(hold) + ".release").touch()
        if daemon is not None and daemon.is_dir():
            shutil.rmtree(daemon, ignore_errors=True)
    end = time.monotonic() + 30
    while not Path(str(hold) + ".release.done").exists() and time.monotonic() < end:
        time.sleep(0.05)       # the holder lets the store go before the test reads it
    rel = review.CODE_STORE_REL
    absolute = str(project / rel)
    assert Path(str(hold) + ".ready").exists(), f"premise: another process held {rel} during the rebuild"
    assert support.free_pages(project / rel) > 0, f"premise: the rebuild could not compact {rel}\n{run.describe()}"
    envelope = run.envelope()
    payload = envelope.get("result") if envelope.get("ok") else envelope.get("error")
    assert payload and any(rel in text or absolute in text for text in _strings(payload)), (
        f"the rebuild's JSON result does not name {rel}, which it could not compact\n{run.describe()}")
    lines = [line for line in run.stderr.splitlines() if rel in line or absolute in line]
    reasons = [reason for reason in _json_reason(payload, rel) if reason.strip()]
    told = any(_REASON.search(line) for line in lines) or any(
        reason in run.stderr or reason.split(":", 1)[-1].strip() in run.stderr for reason in reasons)
    assert lines and told, (
        f"another process held {rel} during the rebuild, which could not compact it: its standard error does not "
        f"name the store with the reason (the JSON result gives {json.dumps(reasons)})\n{run.describe()}")
