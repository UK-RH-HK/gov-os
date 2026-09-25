"""BR-AR-0014/BR-HO-0014 (bounded repair B3R): the eager code-layer builder and its build-manifest digest.

Covers the handoff's own acceptance checks 3-5 as fast, deterministic, hermetic tests over a throwaway Git repo
(check 1/2's real-repository, from-clean, cross-store proofs are the checkpoint's own recorded commands -- a real
`.rs` corpus of that size does not belong in a unit test):

* eager-ref derivation is generic (an explicit per-ref ``layers`` list, or the omitted-``layers`` role fallback --
  never a hard-coded ref name, mirroring ``govbridge.semantic.profile.eligible_ref_names``'s own rule);
* query-invariance: a LAZY query (``govbridge.code.symbols.ensure_indexed``) against a commit outside the eager set
  parses and persists new rows, but never changes the manifest digest (check 3);
* incremental == full on a fixture repo (check 4);
* the digest is sensitive to a single ``code_call_site`` row, and separately a single ``code_literal`` row,
  changing -- proving all three tables (not just ``code_symbol``, the original defect) are covered (check 5).
"""
from __future__ import annotations

from govbridge.code import build as codebuild
from govbridge.code import symbols as codesymbols
from govbridge.core import store as corestore
from govbridge.core.view import Partition, ResolvedRef, ResolvedView, RefSpec, ViewConfig

import _repobuilder as rb


def _view(refs: list[RefSpec]) -> ViewConfig:
    return ViewConfig(view_id="test-view", refs=refs, partitions=[Partition(name="all", owner="records",
                                                                             fallback=[], paths=["**"])], raw={})


def _resolved(view: ViewConfig, named: dict[str, str], history: list[tuple[str, str]] = (), repo=None) \
        -> ResolvedView:
    """``named``: {ref_name: commit}. Builds the ResolvedRef wrapper generically; no test here needs REF_MOVED."""
    return ResolvedView(
        view_id=view.view_id, config=view,
        named={n: ResolvedRef(name=n, commit=c, status="OK") for n, c in named.items()},
        history=list(history), repo=repo,
    )


def test_eager_ref_names_uses_explicit_layers_list():
    view = _view([
        RefSpec(name="records", ref="refs/heads/records", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=["exact", "lexical", "code"]),
        RefSpec(name="product", ref="refs/heads/product", ref_glob=None, follow="tip", pinned_commit=None,
                role="product", layers=["exact", "lexical"]),  # explicitly omits "code"
    ])
    resolved = _resolved(view, {"records": "c1", "product": "c1"})
    assert codebuild.eager_ref_names(resolved) == {"records"}


def test_eager_ref_names_falls_back_to_role_when_layers_is_omitted():
    """The single-ref V8.3 collapse (ARCHITECTURE.md section 10) and the tests/fixtures/core canonical-view.yaml
    both omit `layers` entirely; every non-history role is then eager by default, never hard-coded by name."""
    view = _view([
        RefSpec(name="records", ref="refs/heads/records", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=None),
        RefSpec(name="product", ref="refs/heads/product", ref_glob=None, follow="tip", pinned_commit=None,
                role="product", layers=None),
        RefSpec(name="evidence", ref="refs/heads/evidence", ref_glob=None, follow="tip", pinned_commit=None,
                role="evidence", layers=None),
        RefSpec(name="oldest-attempt", ref="refs/heads/oldest-attempt", ref_glob=None, follow="tip",
                pinned_commit=None, role="history", layers=None),  # a NAMED ref with role history -- edge case
    ])
    resolved = _resolved(view, {"records": "c1", "product": "c1", "evidence": "c2", "oldest-attempt": "c3"})
    assert codebuild.eager_ref_names(resolved) == {"records", "product", "evidence"}


def test_eager_ref_names_never_includes_history_glob_refs():
    view = _view([
        RefSpec(name="records", ref="refs/heads/records", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=None),
        RefSpec(name="history", ref=None, ref_glob="refs/heads/phase2/*", follow="tip", pinned_commit=None,
                role="history", layers=None),
    ])
    resolved = _resolved(view, {"records": "c1"}, history=[("refs/heads/phase2/a", "cA"),
                                                             ("refs/heads/phase2/b", "cB")])
    assert codebuild.eager_ref_names(resolved) == {"records"}


def _write_v1(root):
    rb.write(root, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    rb.write(root, "runtime/src/mod_b.rs",
             "fn caller(d: &D) {\n    helper();\n    if d.str(\"widget_kind\") == \"x\" {}\n}\n")
    return rb.commit(root, "v1")


def _eager_view_for(root, commit) -> ResolvedView:
    view = _view([
        RefSpec(name="records", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                role="primary", layers=None),
    ])
    return _resolved(view, {"records": commit}, repo=str(root))


def test_incremental_equals_full_on_a_fixture_repo(repo):
    c1 = _write_v1(repo)
    conn = corestore.open_db()

    stats1 = codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo),
                                           from_clean=True)
    assert stats1["eager_blobs"] > 0
    digest_c1 = codebuild.code_layer_digest(conn)

    # C2: one .rs file changes (an extra call site AND a changed literal), the other is untouched
    rb.write(repo, "runtime/src/mod_b.rs",
             "fn caller(d: &D) {\n    helper();\n    helper();\n    if d.str(\"other_kind\") == \"x\" {}\n}\n")
    c2 = rb.commit(repo, "v2: mod_b.rs changes")

    stats2 = codebuild.code_layer_builder(conn, _eager_view_for(repo, c2), rules=None, repo=str(repo),
                                           from_clean=False, changed_refs=["records"])
    digest_incremental = codebuild.code_layer_digest(conn)
    assert digest_incremental.digest != digest_c1.digest  # the change must actually be visible

    # a SEPARATE from-clean build directly at C2 must reach the identical digest -- a second, independent store
    # root (never the same file as `conn`'s)
    from pathlib import Path
    import tempfile
    conn_clean = corestore.open_db(root=Path(tempfile.mkdtemp()) / "store")
    codebuild.code_layer_builder(conn_clean, _eager_view_for(repo, c2), rules=None, repo=str(repo), from_clean=True)
    digest_full_c2 = codebuild.code_layer_digest(conn_clean)

    assert digest_incremental.digest == digest_full_c2.digest
    assert digest_incremental.rows == digest_full_c2.rows
    assert digest_incremental.extra["blobs_parsed"] == digest_full_c2.extra["blobs_parsed"]


def test_digest_is_query_invariant_against_a_non_eager_commit(repo):
    c1 = _write_v1(repo)
    conn = corestore.open_db()
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    before = codebuild.code_layer_digest(conn)

    # a commit OUTSIDE the eager set (a "history"-shaped query, never built eagerly): different content entirely
    rb.write(repo, "runtime/src/mod_c.rs", "pub fn only_in_history() {\n    helper();\n}\n")
    c_history = rb.commit(repo, "history-only commit")
    entries = codesymbols.ensure_indexed(conn, c_history, repo=str(repo))
    assert entries  # the lazy query really did parse something new

    after = codebuild.code_layer_digest(conn)
    assert after.digest == before.digest
    assert after.rows == before.rows
    assert after.extra["blobs_parsed"] == before.extra["blobs_parsed"]


def test_digest_changes_when_a_single_call_site_row_differs(repo):
    rb.write(repo, "runtime/src/mod_a.rs", "pub fn helper() {}\n")
    rb.write(repo, "runtime/src/mod_b.rs", "fn caller() {\n    helper();\n}\n")
    c1 = rb.commit(repo, "one call site")
    conn1 = corestore.open_db()
    codebuild.code_layer_builder(conn1, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    d1 = codebuild.code_layer_digest(conn1)

    rb.write(repo, "runtime/src/mod_b.rs", "fn caller() {\n    helper();\n    helper();\n}\n")  # +1 call_site row
    c2 = rb.commit(repo, "two call sites, same symbols, no literals")
    conn2 = corestore.open_db()
    codebuild.code_layer_builder(conn2, _eager_view_for(repo, c2), rules=None, repo=str(repo), from_clean=True)
    d2 = codebuild.code_layer_digest(conn2)

    assert d1.extra["symbol_rows"] == d2.extra["symbol_rows"]
    assert d1.extra["literal_rows"] == d2.extra["literal_rows"] == 0
    assert d1.extra["call_site_rows"] != d2.extra["call_site_rows"]
    assert d1.digest != d2.digest


def test_digest_changes_when_a_single_literal_row_differs(repo):
    rb.write(repo, "runtime/src/keys.rs", "fn reads(d: &D) {\n    if d.str(\"widget_kind\") == \"x\" {}\n}\n")
    c1 = rb.commit(repo, "one literal")
    conn1 = corestore.open_db()
    codebuild.code_layer_builder(conn1, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)
    d1 = codebuild.code_layer_digest(conn1)

    # same symbols, same number/shape of call sites (still one `d.str(...)` call on the same line), different value
    rb.write(repo, "runtime/src/keys.rs", "fn reads(d: &D) {\n    if d.str(\"shape_flag\") == \"x\" {}\n}\n")
    c2 = rb.commit(repo, "literal value changes")
    conn2 = corestore.open_db()
    codebuild.code_layer_builder(conn2, _eager_view_for(repo, c2), rules=None, repo=str(repo), from_clean=True)
    d2 = codebuild.code_layer_digest(conn2)

    assert d1.extra["symbol_rows"] == d2.extra["symbol_rows"]
    assert d1.extra["call_site_rows"] == d2.extra["call_site_rows"]
    assert d1.extra["literal_rows"] == d2.extra["literal_rows"]
    assert d1.digest != d2.digest


def test_eager_build_parses_only_new_blobs_on_a_second_call(repo, monkeypatch):
    c1 = _write_v1(repo)
    conn = corestore.open_db()
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo), from_clean=True)

    from govbridge.code.adapters import rust_treesitter as rt
    calls = {"n": 0}
    original = rt.parse_module

    def counting(*a, **kw):
        calls["n"] += 1
        return original(*a, **kw)

    monkeypatch.setattr(rt, "parse_module", counting)
    stats = codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=None, repo=str(repo),
                                          from_clean=False, changed_refs=[])
    assert calls["n"] == 0  # nothing changed -- every blob was already cached
    assert stats["eager_blobs"] == 2  # mod_a.rs, mod_b.rs -- membership still recomputed correctly


def test_eager_build_is_a_noop_stats_shape_with_no_eager_refs(repo):
    c1 = _write_v1(repo)
    view = _view([
        RefSpec(name="history", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                role="history", layers=None),
    ])
    resolved = _resolved(view, {"history": c1}, repo=str(repo))
    conn = corestore.open_db()
    stats = codebuild.code_layer_builder(conn, resolved, rules=None, repo=str(repo), from_clean=True)
    assert stats["eager_refs"] == []
    assert stats["eager_blobs"] == 0
    digest = codebuild.code_layer_digest(conn)
    assert digest.rows == 0
    assert digest.extra["blobs_parsed"] == 0
