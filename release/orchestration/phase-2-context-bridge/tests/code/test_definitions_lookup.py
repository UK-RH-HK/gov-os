"""``govbridge.code.symbols.definitions`` (routed to I1/BR-AR-0009 as part of wiring the real code route into the
compiler, B6 open issue "the real B2/B3/B4 routes are not wired"): the missing "given a symbol name, return each
definition site" half of ARCHITECTURE.md section 4.6's generic chain probe -- ``callers``/``reads_key`` already
existed; nothing returned a definition's OWN path/lines. New test file; existing tests/code/*.py are unmodified."""
from __future__ import annotations

from pathlib import Path

from govbridge.code import build as codebuild
from govbridge.code import symbols
from govbridge.core import store as corestore
from govbridge.core.view import Partition, RefSpec, ResolvedRef, ResolvedView, ViewConfig

import _repobuilder as rb


def _eager_build(root: Path, commit: str) -> None:
    """BR-DAG-AMEND-R1-17 item 5 reopening (rule-5 correction, justified in this run's checkpoint `decisions`):
    symbols.definitions() no longer lazily builds the code layer itself -- it raises StoreNeedsRebuild for a
    commit the eager builder has not already reached, so this test builds the code layer eagerly first."""
    view = ViewConfig(view_id="test-view", refs=[
        RefSpec(name="records", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=None),
    ], partitions=[Partition(name="all", owner="records", fallback=[], paths=["**"])], raw={})
    resolved = ResolvedView(view_id=view.view_id, config=view,
                             named={"records": ResolvedRef(name="records", commit=commit, status="OK")},
                             history=[], repo=str(root))
    conn = corestore.open_db()
    codebuild.code_layer_builder(conn, resolved, rules=None, repo=str(root), from_clean=True)
    conn.close()


def test_definitions_finds_bare_and_qualified_name_matches(repo):
    rb.write(repo, "runtime/src/paths.rs", "pub fn reanchor_project_identity() {}\n")
    rb.write(repo, "runtime/src/other.rs", "fn unrelated() {}\n")
    c1 = rb.commit(repo, "c1")
    _eager_build(repo, c1)

    out = symbols.definitions("reanchor_project_identity", c1, repo=str(repo))
    assert out["symbol"] == "reanchor_project_identity"
    assert len(out["definitions"]) == 1
    d = out["definitions"][0]
    assert d["path"] == "runtime/src/paths.rs"
    assert d["qualified_name"].endswith("reanchor_project_identity")
    assert d["start_line"] >= 1 and d["end_line"] >= d["start_line"]

    # a qualified lookup (crate::module::name) also matches via the "endswith ::name" rule
    out2 = symbols.definitions(d["qualified_name"], c1, repo=str(repo))
    assert len(out2["definitions"]) == 1
    assert out2["definitions"][0]["symbol_id"] == d["symbol_id"]


def test_definitions_empty_for_unknown_name(repo):
    rb.write(repo, "runtime/src/x.rs", "pub fn known() {}\n")
    c1 = rb.commit(repo, "c1")
    _eager_build(repo, c1)
    out = symbols.definitions("does_not_exist_anywhere", c1, repo=str(repo))
    assert out["definitions"] == []
