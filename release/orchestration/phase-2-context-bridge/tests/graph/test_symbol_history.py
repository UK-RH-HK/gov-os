"""``govbridge.graph.symbol_history`` (REPAIR_PLAN.md section 4, R1-RL: "a 'why was it created' facet can reach
the introducing commit"). ``govbridge.code.history.diff`` (EXISTING, unchanged) already answers INTRODUCED_IN/
DELETED_IN between two COMMITS a caller already knows; this module finds that commit automatically, bounded by
configuration (``max_commits``), reusing the SAME ``tests/code/_repobuilder.py`` helper
``tests/graph/test_code_bridge.py`` already imports this way.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import _repobuilder as rb  # noqa: E402

from govbridge.code import build as codebuild
from govbridge.core import store as corestore
from govbridge.core.view import Partition, RefSpec, ResolvedRef, ResolvedView, ViewConfig
from govbridge.graph import symbol_history as SH


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    rb.init(root)
    return root


def _eager_build(root, *commits: str) -> None:
    """BR-DAG-AMEND-R1-17 item 5 reopening (rule-5 correction, justified in this run's checkpoint `decisions`):
    symbol_history's own introduced_in/deleted_in walk many HISTORICAL commits (never eager-built by a real
    deployment's own index, which only reaches the current tip of each ref), examining each one through
    ensure_indexed_readonly -- which now raises StoreNeedsRebuild for a commit the eager builder has not already
    reached, rather than lazily indexing it on the spot. Every test in this file builds the code layer eagerly for
    EVERY commit its own walk could examine, by giving each one its own named ref in one resolved view (mirroring
    tests/code/test_eager_build.py's own pattern)."""
    refs = [RefSpec(name=f"c{i}", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                     role="primary", layers=None) for i in range(len(commits))]
    view = ViewConfig(view_id="test-view", refs=refs,
                       partitions=[Partition(name="all", owner="records", fallback=[], paths=["**"])], raw={})
    resolved = ResolvedView(
        view_id=view.view_id, config=view,
        named={f"c{i}": ResolvedRef(name=f"c{i}", commit=c, status="OK") for i, c in enumerate(commits)},
        history=[], repo=str(root),
    )
    conn = corestore.open_db()
    codebuild.code_layer_builder(conn, resolved, rules=None, repo=str(root), from_clean=True)
    conn.close()


def test_introduced_in_finds_the_commit_that_added_the_symbol(repo):
    rb.write(repo, "runtime/src/lib.rs", "pub fn old_fn() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.write(repo, "runtime/src/lib.rs", "pub fn old_fn() {}\n\npub fn new_fn() {}\n")
    c2 = rb.commit(repo, "c2")
    rb.write(repo, "runtime/src/lib.rs",
              "pub fn old_fn() {}\n\npub fn new_fn() {}\n\npub fn caller() { new_fn(); }\n")
    c3 = rb.commit(repo, "c3")
    _eager_build(repo, c1, c2, c3)

    result = SH.introduced_in("new_fn", c3, repo=str(repo), max_commits=10)
    assert result["found"] is True
    assert len(result["results"]) == 1
    r = result["results"][0]
    assert r["introduced_commit"] == c2
    assert r["bounded_incomplete"] is False

    # old_fn was already there at c1 -- the oldest commit examined
    result_old = SH.introduced_in("old_fn", c3, repo=str(repo), max_commits=10)
    assert result_old["results"][0]["introduced_commit"] == c1


def test_introduced_in_bounded_by_max_commits(repo):
    """A tiny max_commits truncates the walk before it can reach the true origin -- an HONEST lower bound
    (bounded_incomplete=True), never a wrong claim of certainty."""
    rb.write(repo, "runtime/src/lib.rs", "pub fn a() {}\n")
    commits = [rb.commit(repo, "c1")]
    for i in range(5):
        rb.write(repo, "runtime/src/lib.rs", f"pub fn a() {{}}\n// churn {i}\n")
        commits.append(rb.commit(repo, f"churn {i}"))
    rb.write(repo, "runtime/src/lib.rs", "pub fn a() {}\npub fn b() {}\n")
    last = rb.commit(repo, "add b")
    commits.append(last)
    _eager_build(repo, *commits)

    result = SH.introduced_in("a", last, repo=str(repo), max_commits=2)
    r = result["results"][0]
    assert r["commits_examined"] == 2
    assert r["bounded_incomplete"] is True


def test_introduced_in_no_current_definition(repo):
    rb.write(repo, "runtime/src/lib.rs", "pub fn only_fn() {}\n")
    c1 = rb.commit(repo, "c1")
    _eager_build(repo, c1)
    result = SH.introduced_in("does_not_exist", c1, repo=str(repo))
    assert result["found"] is False
    assert result["results"] == []


def test_deleted_in_finds_the_commit_that_removed_the_symbol(repo):
    rb.write(repo, "runtime/src/lib.rs", "pub fn keep_fn() {}\n\npub fn doomed_fn() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.write(repo, "runtime/src/lib.rs", "pub fn keep_fn() {}\n\npub fn doomed_fn() {}\n// still here\n")
    c2 = rb.commit(repo, "c2 (unrelated touch)")
    rb.write(repo, "runtime/src/lib.rs", "pub fn keep_fn() {}\n")
    c3 = rb.commit(repo, "c3 (removed)")
    _eager_build(repo, c1, c2, c3)

    result = SH.deleted_in("doomed_fn", c1, until_ref=c3, repo=str(repo), max_commits=10)
    assert result["found"] is True
    assert result["deleted_commit"] == c3


def test_deleted_in_still_present_reports_not_found(repo):
    rb.write(repo, "runtime/src/lib.rs", "pub fn stays() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.write(repo, "runtime/src/lib.rs", "pub fn stays() {}\n// touch\n")
    c2 = rb.commit(repo, "c2")
    _eager_build(repo, c1, c2)

    result = SH.deleted_in("stays", c1, until_ref=c2, repo=str(repo), max_commits=10)
    assert result["found"] is False


def test_deleted_in_rejects_a_since_commit_without_the_symbol(repo):
    rb.write(repo, "runtime/src/lib.rs", "pub fn only_fn() {}\n")
    c1 = rb.commit(repo, "c1")
    _eager_build(repo, c1)
    result = SH.deleted_in("not_present", c1, until_ref=c1, repo=str(repo))
    assert result["found"] is False
    assert "not present" in result["reason"]


def test_default_max_commits_is_configuration_not_a_code_literal(monkeypatch):
    """BR-AR-0019 reopening ruling item 3: the bound must come from configuration, resolved FRESH on every call
    (never baked into a module-level constant at import time), so a config/env-var change takes effect
    immediately -- proven here via monkeypatch, without ever touching a real environment variable."""
    assert SH._default_max_commits() == 500  # govbridge/code/lineage_config.yaml's own default, unmodified
    monkeypatch.setenv("GOVBRIDGE_SYMBOL_HISTORY_MAX_COMMITS", "7")
    assert SH._default_max_commits() == 7
    # introduced_in/deleted_in resolve max_commits fresh (never DEFAULT_MAX_COMMITS baked in at import time)
    # when the caller omits it -- confirmed by inspecting the default parameter value directly.
    import inspect
    assert inspect.signature(SH.introduced_in).parameters["max_commits"].default is None
    assert inspect.signature(SH.deleted_in).parameters["max_commits"].default is None


def test_cli_introduced_in(repo):
    """A subprocess invocation (never an in-process ``os.chdir`` + call: ``govbridge.core.gitobj.repo_root`` is
    ``functools.lru_cache``d by its ``start`` argument, so an in-process ``chdir`` after an earlier test already
    cached a different cwd's root would silently resolve against the WRONG repo -- the same reason
    ``tests/code/test_symbols_integration.py``'s own CLI test already uses a subprocess)."""
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path

    domain = str(Path(__file__).resolve().parents[2])  # release/orchestration/phase-2-context-bridge
    rb.write(repo, "runtime/src/lib.rs", "pub fn a() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.write(repo, "runtime/src/lib.rs", "pub fn a() {}\npub fn b() {}\n")
    c2 = rb.commit(repo, "c2")
    _eager_build(repo, c1, c2)  # into the SAME GOVBRIDGE_STORE the subprocess below inherits via os.environ

    env = dict(os.environ)
    env["PYTHONPATH"] = domain
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge.graph.symbol_history", "introduced-in", "b", "--commit", c2, "--json"],
        cwd=str(repo), capture_output=True, text=True, env=env, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["results"][0]["introduced_commit"] == c2
