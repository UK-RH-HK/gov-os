"""Per-commit symbol history (govbridge.code.history): DELETED_IN / INTRODUCED_IN as an exact set difference
between two commits' parsed Rust definitions, over a small throwaway Git repository."""
from __future__ import annotations

from pathlib import Path

from govbridge.code import build as codebuild
from govbridge.code import history
from govbridge.code.adapters.rust_treesitter import DERIVATION_EXACT_PARSE
from govbridge.core import store as corestore
from govbridge.core.view import Partition, RefSpec, ResolvedRef, ResolvedView, ViewConfig

import _repobuilder as rb


def _eager_build(root: Path, *commits: str) -> None:
    """BR-DAG-AMEND-R1-17 item 5 reopening (rule-5 correction, justified in this run's checkpoint `decisions`):
    govbridge.code.history.diff() no longer lazily builds the code layer for either commit it diffs -- it reads
    via ensure_indexed_readonly, raising StoreNeedsRebuild for a commit the eager builder has not already reached.
    Builds the code layer eagerly for EVERY commit this file diffs, by giving each one its own named ref in the
    SAME resolved view (mirroring tests/code/test_eager_build.py's own pattern of constructing a ResolvedView
    directly, with explicit commits, rather than a real git-ref-following one)."""
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


def test_deleted_symbol_is_reported_with_exact_parse_derivation(repo):
    rb.write(repo, "runtime/src/paths.rs", "pub fn reanchor_project_identity() {}\npub fn stays() {}\n")
    c1 = rb.commit(repo, "c1: has reanchor_project_identity")

    rb.write(repo, "runtime/src/paths.rs", "pub fn stays() {}\n")
    c2 = rb.commit(repo, "c2: removed it")
    _eager_build(repo, c1, c2)

    result = history.deleted(c1, c2, repo=str(repo))
    assert result["from"] == c1 and result["to"] == c2
    names = {r["qualified_name"] for r in result["deleted"]}
    assert "reanchor_project_identity" in names
    assert "stays" not in names
    row = next(r for r in result["deleted"] if r["qualified_name"] == "reanchor_project_identity")
    assert row["event"] == history.DELETED_IN
    assert row["at_commit"] == c2
    assert row["derivation"] == DERIVATION_EXACT_PARSE
    assert row["path"] == "runtime/src/paths.rs"


def test_introduced_symbol_is_reported(repo):
    rb.write(repo, "runtime/src/a.rs", "pub fn old_fn() {}\n")
    c1 = rb.commit(repo, "c1")

    rb.write(repo, "runtime/src/a.rs", "pub fn old_fn() {}\npub fn new_fn() {}\n")
    c2 = rb.commit(repo, "c2")
    _eager_build(repo, c1, c2)

    result = history.introduced(c1, c2, repo=str(repo))
    names = {r["qualified_name"] for r in result["introduced"]}
    assert "new_fn" in names
    assert "old_fn" not in names
    row = next(r for r in result["introduced"] if r["qualified_name"] == "new_fn")
    assert row["event"] == history.INTRODUCED_IN


def test_unchanged_symbol_is_neither_deleted_nor_introduced(repo):
    rb.write(repo, "runtime/src/a.rs", "pub fn steady() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.write(repo, "runtime/src/b.rs", "pub fn unrelated() {}\n")
    c2 = rb.commit(repo, "c2: unrelated file added, steady untouched")
    _eager_build(repo, c1, c2)

    result = history.diff(c1, c2, repo=str(repo))
    deleted_names = {r["qualified_name"] for r in result["deleted"]}
    introduced_names = {r["qualified_name"] for r in result["introduced"]}
    assert "steady" not in deleted_names
    assert "steady" not in introduced_names
    assert "unrelated" in introduced_names


def test_moved_symbol_is_not_reported_as_deleted(repo):
    """A symbol that only changes file keeps the same (kind, qualified_name), so it is correctly invisible to a
    set-difference-by-name diff -- this is the documented limitation (history.py's module docstring), checked here
    so a future change does not silently start claiming move tracking it cannot back up exactly."""
    rb.write(repo, "runtime/src/here.rs", "pub fn mover() {}\n")
    c1 = rb.commit(repo, "c1")
    rb.remove(repo, "runtime/src/here.rs")
    rb.write(repo, "runtime/src/there.rs", "pub fn mover() {}\n")
    c2 = rb.commit(repo, "c2: moved")
    _eager_build(repo, c1, c2)

    result = history.diff(c1, c2, repo=str(repo))
    names_deleted = {r["qualified_name"] for r in result["deleted"]}
    names_introduced = {r["qualified_name"] for r in result["introduced"]}
    assert "mover" not in names_deleted
    assert "mover" not in names_introduced
