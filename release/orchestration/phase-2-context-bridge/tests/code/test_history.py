"""Lazy per-commit symbol history (govbridge.code.history): DELETED_IN / INTRODUCED_IN as an exact set difference
between two commits' parsed Rust definitions, over a small throwaway Git repository."""
from __future__ import annotations

from govbridge.code import history
from govbridge.code.adapters.rust_treesitter import DERIVATION_EXACT_PARSE

import _repobuilder as rb


def test_deleted_symbol_is_reported_with_exact_parse_derivation(repo):
    rb.write(repo, "runtime/src/paths.rs", "pub fn reanchor_project_identity() {}\npub fn stays() {}\n")
    c1 = rb.commit(repo, "c1: has reanchor_project_identity")

    rb.write(repo, "runtime/src/paths.rs", "pub fn stays() {}\n")
    c2 = rb.commit(repo, "c2: removed it")

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

    result = history.diff(c1, c2, repo=str(repo))
    names_deleted = {r["qualified_name"] for r in result["deleted"]}
    names_introduced = {r["qualified_name"] for r in result["introduced"]}
    assert "mover" not in names_deleted
    assert "mover" not in names_introduced
