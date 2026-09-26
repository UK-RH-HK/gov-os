"""End-to-end tests over a small synthetic Rust crate committed to a throwaway Git repository: real parsing (tree-
sitter, not synthetic Definition objects -- see tests/code/test_resolve.py for the resolver in isolation), real
persistence into an isolated store, and the govbridge.code.symbols query surface (stats/callers/reads-key) plus its
CLI. Exercises the acceptance checks' exact shapes ("a synthetic fixture crate proving each label ... and that an
ambiguous call never yields a single chosen target") against this node's own code, not the product repository.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from govbridge.code import build as codebuild
from govbridge.code import resolve as R
from govbridge.code import symbols
from govbridge.core import store as corestore
from govbridge.core.view import Partition, RefSpec, ResolvedRef, ResolvedView, ViewConfig

import _repobuilder as rb

_D = str(Path(__file__).resolve().parents[2])  # release/orchestration/phase-2-context-bridge


def _eager_build(root: Path, commit: str) -> None:
    """BR-DAG-AMEND-R1-17 item 5 reopening (rule-5 correction, justified in this run's checkpoint `decisions`):
    govbridge.code.symbols's query surface (stats/definitions/callers/reads_key) no longer lazily classifies/
    parses/persists a commit's .rs blobs itself -- it raises the typed StoreNeedsRebuild for any blob the eager
    code-layer builder has not already reached. Every test in this file now builds the code layer eagerly first,
    via the SAME govbridge.code.build.code_layer_builder tests/code/test_eager_build.py already drives directly,
    exactly the way a real deployment's `index rebuild` would -- never a narrower assertion, the same real parsing/
    labelling/paging behaviour as before, just measured after a real build instead of after an implicit lazy one."""
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


def _write_label_fixture(root: Path) -> str:
    rb.write(root, "runtime/src/mod_a.rs", "pub fn exact_target() {}\n")
    rb.write(root, "runtime/src/mod_b.rs", "fn caller_exact() {\n    crate::mod_a::exact_target();\n}\n")
    rb.write(root, "runtime/src/types.rs",
              "struct Foo;\nimpl Foo {\n    fn method_x(&self) {}\n}\n"
              "fn caller_type_path(f: &Foo) {\n    Foo::method_x(f);\n}\n")
    rb.write(root, "runtime/src/samefile.rs", "fn helper() {}\nfn caller_same_file() {\n    helper();\n}\n")
    rb.write(root, "runtime/src/unique_a.rs", "pub fn unique_target() {}\n")
    rb.write(root, "runtime/src/unique_b.rs", "fn caller_unique() {\n    unique_target();\n}\n")
    # Different blob content (a trailing comment) so the two definitions get distinct blob/symbol ids -- symbols
    # are cached keyed by blob (ARCHITECTURE.md section 4.6), so two byte-identical files would collapse to one
    # cached parse and defeat the ambiguity this fixture exists to prove.
    rb.write(root, "runtime/src/amb_a.rs", "pub fn ambiguous_target() {}\n// variant a\n")
    rb.write(root, "runtime/src/amb_b.rs", "pub fn ambiguous_target() {}\n// variant b\n")
    rb.write(root, "runtime/src/amb_caller.rs", "fn caller_ambiguous() {\n    ambiguous_target();\n}\n")
    rb.write(root, "runtime/src/macros.rs",
              "fn caller_macro() {\n    my_macro!();\n}\n\n"
              "struct Obj;\nimpl Obj {\n    fn inner_call(&self) -> &'static str { \"x\" }\n}\n"
              "fn caller_macro_token(o: &Obj) {\n    matches!(o.inner_call(), \"ok\");\n}\n")
    rb.write(root, "runtime/src/external.rs", "fn caller_external() {\n    String::new();\n}\n")
    rb.write(root, "runtime/src/keys.rs",
              "fn reads_the_key(d: &D) {\n    if d.str(\"widget_kind\") == \"x\" {}\n}\n\n"
              "fn reads_key_via_macro(d: &D) {\n    matches!(d.str(\"shape_flag\").as_str(), \"y\" | \"\");\n}\n")
    return rb.commit(root, "label fixture")


def test_stats_counts_rs_files_and_definitions(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.stats(commit, repo=str(repo))
    assert result["rs_files"] == 12
    assert result["definitions"] >= 12  # at least one def per file, several files have two
    assert result["commit"] == commit


def test_every_resolution_label_is_reachable_through_real_parsing(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)

    def labels_for(name: str) -> set[str]:
        r = symbols.callers(name, commit, repo=str(repo))
        return {row["label"] for row in r["callers"]}

    assert labels_for("exact_target") == {R.EXACT_PATH}
    assert labels_for("method_x") == {R.HEURISTIC_TYPE_PATH}
    assert labels_for("helper") == {R.HEURISTIC_SAME_FILE}
    assert labels_for("unique_target") == {R.HEURISTIC_UNIQUE_NAME}
    assert labels_for("ambiguous_target") == {R.HEURISTIC_AMBIGUOUS}
    assert labels_for("new") == {R.UNRESOLVED_EXTERNAL}

    macro_rows = symbols.callers("my_macro", commit, repo=str(repo))["callers"]
    assert macro_rows and all(row["label"] == R.MACRO for row in macro_rows)

    token_rows = symbols.callers("inner_call", commit, repo=str(repo))["callers"]
    assert token_rows and any(row["label"] == R.HEURISTIC_MACRO_TOKEN for row in token_rows)


def test_ambiguous_call_never_yields_a_single_chosen_target(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.callers("ambiguous_target", commit, repo=str(repo))
    assert result["callers"], "expected at least one call site"
    for row in result["callers"]:
        assert row["label"] == R.HEURISTIC_AMBIGUOUS
        assert row["n_candidates"] >= 2
        assert len(row["targets"]) >= 2
        target_paths = {t["path"] for t in row["targets"]}
        assert target_paths == {"runtime/src/amb_a.rs", "runtime/src/amb_b.rs"}


def test_exact_path_caller_is_exactly_one_site(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.callers("exact_target", commit, repo=str(repo))
    assert len(result["callers"]) == 1
    row = result["callers"][0]
    assert row["at"] == "runtime/src/mod_b.rs:2"
    assert row["label"] == R.EXACT_PATH
    assert len(row["targets"]) == 1


def test_reads_key_finds_normal_method_accessor(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.reads_key("widget_kind", commit, repo=str(repo))
    row = next(row for row in result["reads"] if row["at"] == "runtime/src/keys.rs:2")
    assert row["enclosing_symbol"] == "reads_the_key"
    assert "str" in row["accessors"][0]


def test_reads_key_finds_accessor_inside_macro_token_tree(repo):
    # Mirrors the real shape at runtime/src/tools.rs:1817 in the product repository: the literal sits inside a
    # matches!() macro, so only the macro-token scan (not a parsed field_expression) sees the accessor.
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.reads_key("shape_flag", commit, repo=str(repo))
    row = next(row for row in result["reads"] if row["at"] == "runtime/src/keys.rs:6")
    assert row["enclosing_symbol"] == "reads_key_via_macro"
    assert "str" in row["accessors"]


def test_reads_key_no_false_positive_for_unused_literal(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    result = symbols.reads_key("no_such_literal_anywhere", commit, repo=str(repo))
    assert result["reads"] == []


def test_query_never_reparses_after_the_eager_build(repo, monkeypatch):
    """BR-DAG-AMEND-R1-17 item 5 reopening strengthens this invariant: parsing now happens ONLY at the eager build
    (govbridge.code.build.code_layer_builder), never at query time at all -- stats() is read-only
    (ensure_indexed_readonly), so it never calls the parser, on the first query call or any later one."""
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)

    calls = {"n": 0}
    from govbridge.code.adapters import rust_treesitter as rt
    original = rt.parse_module

    def counting(*a, **kw):
        calls["n"] += 1
        return original(*a, **kw)

    monkeypatch.setattr(rt, "parse_module", counting)
    symbols.stats(commit, repo=str(repo))  # first query call after the build: already fully cached
    symbols.stats(commit, repo=str(repo))  # second call: still cached
    assert calls["n"] == 0


def test_cli_callers_subcommand_matches_library_call(repo):
    commit = _write_label_fixture(repo)
    _eager_build(repo, commit)
    env = dict(os.environ)
    env["PYTHONPATH"] = _D
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge.code.symbols", "callers", "exact_target", "--commit", commit, "--json"],
        cwd=str(repo), capture_output=True, text=True, env=env, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["symbol"] == "exact_target"
    assert len(payload["callers"]) == 1
    assert payload["callers"][0]["label"] == R.EXACT_PATH


def test_byte_identical_files_share_one_cached_blob_by_design(repo):
    """A documented edge case, not a bug: govbridge.code.store keys the parse cache by blob id alone
    (ARCHITECTURE.md section 3: "symbols, calls, literals ... keyed by (blob, adapter id+version, grammar
    version)"), and Git blob ids are content-addressed. Two source files with byte-identical content are therefore
    the SAME blob and share one cached parse -- a call to a name defined only in such a pair resolves as if the
    definition existed once, not twice. Real Rust source essentially never collides this way (this fixture's
    amb_a.rs/amb_b.rs deliberately differ by a trailing comment for exactly this reason); this test pins the
    behaviour so a future change does not silently alter it."""
    rb.write(repo, "runtime/src/twin_a.rs", "pub fn twin_fn() {}\n")
    rb.write(repo, "runtime/src/twin_b.rs", "pub fn twin_fn() {}\n")  # byte-identical -> same blob id
    rb.write(repo, "runtime/src/twin_caller.rs", "fn call_twin() {\n    twin_fn();\n}\n")
    commit = rb.commit(repo, "byte-identical twin files")
    _eager_build(repo, commit)

    result = symbols.stats(commit, repo=str(repo))
    assert result["rs_files"] == 3

    caller_result = symbols.callers("twin_fn", commit, repo=str(repo))
    labels = {row["label"] for row in caller_result["callers"]}
    # one cached blob -> one definition -> resolved as unique, not ambiguous (the documented trade-off)
    assert labels == {R.HEURISTIC_UNIQUE_NAME}


# --- R1-RL: paging over `callers` -----------------------------------------------------------------------------

def _write_many_callers_fixture(root: Path, n: int) -> None:
    rb.write(root, "runtime/src/paged_target.rs", "pub fn paged_target() {}\n")
    lines = "\n".join(f"fn paged_caller_{i}() {{ paged_target(); }}" for i in range(n))
    rb.write(root, "runtime/src/paged_callers.rs", lines + "\n")


def test_callers_paged_matches_the_unpaged_query_50_callers_page_8(repo):
    """The acceptance check, verbatim: "a 50-caller symbol paged 8 at a time gives the same union as the unpaged
    query"."""
    _write_many_callers_fixture(repo, 50)
    commit = rb.commit(repo, "50 callers of paged_target")
    _eager_build(repo, commit)

    full = symbols.callers("paged_target", commit, repo=str(repo))
    assert len(full["callers"]) == 50

    collected = []
    cursor = None
    pages = 0
    while True:
        page = symbols.callers("paged_target", commit, repo=str(repo), page_size=8, cursor=cursor)
        pages += 1
        assert page["total"] == 50
        collected.extend(page["callers"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert pages == 7  # ceil(50 / 8)
    assert collected == full["callers"]


def test_cli_callers_page_size_returns_a_continuation_handle(repo):
    _write_many_callers_fixture(repo, 50)
    commit = rb.commit(repo, "50 callers of paged_target, via CLI")
    _eager_build(repo, commit)
    env = dict(os.environ)
    env["PYTHONPATH"] = _D
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge.code.symbols", "callers", "paged_target", "--commit", commit,
         "--page-size", "6", "--json"],
        cwd=str(repo), capture_output=True, text=True, env=env, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert len(payload["callers"]) == 6
    assert payload["next_cursor"] == "6"
    assert payload["total"] == 50
