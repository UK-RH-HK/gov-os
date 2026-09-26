"""``govbridge.code.lineage_layer`` (BR-AR-0019 REOPENED ruling): the persisted, registered, digested "lineage"
store layer for TESTS-beyond-a-direct-call (CLI dispatch, test-registry shape), DEPENDS_ON_DATA and
CITES_REQUIREMENT edges. Lives under ``govbridge/code/`` (see its own module docstring for why); tested here
because ``tests/code/**`` is this node's mutation scope and already provides the ``repo``/isolated-store fixtures
(``tests/code/conftest.py``).

Hermetic (BR-DAG-AMEND-R1-4): every test builds its OWN throwaway repo (the ``repo`` fixture, a fresh ``tmp_path``
per test), passes ``repo=`` explicitly everywhere, never chdirs, and any GOV_BRIDGE_DOMAIN override is
``monkeypatch``-scoped to one test.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import govbridge

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fixtures" / "authority"))
import authority_repobuilder  # noqa: E402

from govbridge.code import lineage_layer as LL
from govbridge.core import corpus, gitobj
from govbridge.core import view as viewmod


def _resolved_view(repo, refs: list, partitions: "list | None" = None) -> viewmod.ResolvedView:
    """A REAL ``govbridge.core.view.ResolvedView`` (never a hand-rolled fake of its interface -- BR-AR-0019
    reopening, third pass, Defect A: ``lineage_layer_builder`` now calls ``partition_for``/``classify_occurrence``
    too, not just ``ref_commit``, so a fake that only implements one method is no longer a faithful stand-in).
    ``refs``: ``[(name, commit, role)]``, each admitted to the "code" layer (``layers=["code"]``, matching every
    real ``config/canonical-view.yaml`` ref) so ``govbridge.code.build.eager_ref_names`` selects all of them.
    ``partitions``: defaults to ONE catch-all ``"**"`` partition owned by the FIRST ref, with every other ref as
    its fallback chain, in order -- reproducing this repository's own real shape (one canonical owner, named
    fallbacks) without needing a ``paths_from``/product-identity file for a test that does not care about that
    machinery."""
    refspecs = [viewmod.RefSpec(name=n, ref=None, ref_glob=None, follow="pinned", pinned_commit=c, role=role,
                                 layers=["code"]) for (n, c, role) in refs]
    named = {n: viewmod.ResolvedRef(name=n, commit=c, status=viewmod.REF_OK) for (n, c, _r) in refs}
    if partitions is None:
        owner = refs[0][0]
        fallback = [r[0] for r in refs[1:]]
        partitions = [{"name": "all", "owner": owner, "fallback": fallback, "paths": ["**"]}]
    partobjs = [viewmod.Partition(name=p["name"], owner=p["owner"], fallback=list(p.get("fallback") or []),
                                   paths=list(p.get("paths") or []), paths_from=p.get("paths_from"),
                                   extra=list(p.get("extra") or [])) for p in partitions]
    config = viewmod.ViewConfig(view_id="test-lineage", refs=refspecs, partitions=partobjs, raw={})
    return viewmod.ResolvedView(view_id="test-lineage", config=config, named=named, history=[], repo=str(repo))


def _resolved_view_one_ref(repo, commit: str) -> viewmod.ResolvedView:
    """Every PRE-EXISTING (single-commit) test in this file uses this -- one ref named "records", owning a
    catch-all partition with no fallback, which reproduces EXACTLY the single-ref behaviour the builder had before
    Defect A: everything found is trivially CANONICAL, since there is nothing else to be stale against."""
    return _resolved_view(repo, [("records", commit, "primary")])


def _rules(repo) -> list:
    authority_repobuilder.write(repo, "config/corpus-rules.yaml",
                                 "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    return corpus.load_rules(str(repo / "config" / "corpus-rules.yaml"))


def test_lineage_layer_registered_after_ensure_all_layer_packages_imported():
    from govbridge.core import freshness as F
    from govbridge.core import manifest as M

    F.ensure_all_layer_packages_imported()
    assert "lineage" in F.get_layer_builders()
    assert "lineage" in M._LAYER_REGISTRY


def test_lineage_layer_builder_persists_all_four_edge_kinds(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))

    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs",
        "// See framework/contracts/contract.md:3 for the rule.\n"
        "// Also framework/contracts/contract.md section 4 covers budgets.\n"
        "fn f() {\n"
        "    let p = \"config/corpus-rules.yaml\";\n"
        "}\n",
    )
    authority_repobuilder.write(repo, "framework/contracts/contract.md", "# Contract\n\n## 4 Budgets\ntext\n")
    authority_repobuilder.write(
        repo, "tests/fixtures/demo-registry.yaml",
        "schema: fx-registry/1\nrows:\n  - capability: FX-CAP-1\n    tests: [tests/fx/test_fx_cap.py::test_one]\n",
    )
    authority_repobuilder.write(repo, "topcli/__init__.py", "")
    authority_repobuilder.write(
        repo, "topcli/main.py",
        "def main(argv):\n"
        "    cmd, rest = argv[0], argv[1:]\n"
        "    if cmd == 'greet':\n"
        "        from topcli import greeter\n"
        "        return greeter.main(rest)\n"
        "    return 2\n",
    )
    authority_repobuilder.write(
        repo, "topcli/greeter.py",
        "import argparse\n"
        "def say_hello(name):\n"
        "    return f'hello {name}'\n"
        "def main(argv):\n"
        "    p = argparse.ArgumentParser()\n"
        "    sub = p.add_subparsers(dest='cmd', required=True)\n"
        "    s = sub.add_parser('hello')\n"
        "    s.add_argument('name')\n"
        "    args = p.parse_args(argv)\n"
        "    if args.cmd == 'hello':\n"
        "        result = say_hello(args.name)\n"
        "    print(result)\n"
        "    return 0\n",
    )
    authority_repobuilder.write(
        repo, "tests/test_via_cli.py",
        "import subprocess, sys\n"
        "def test_cli_invocation():\n"
        "    subprocess.run([sys.executable, '-m', 'topcli.main', 'greet', 'hello', 'world'])\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "lineage fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)

    assert stats["edges_by_type"].get("DEPENDS_ON_DATA", 0) > 0
    assert stats["edges_by_type"].get("CITES_REQUIREMENT", 0) > 0
    assert stats["edges_by_type"].get("TESTS", 0) >= 2  # one CLI-dispatch row, one registry-shape row

    rows = conn.execute("SELECT src, type, dst, derivation FROM lineage_edge ORDER BY type").fetchall()
    by_type_derivation = {(r[1], r[3]) for r in rows}
    assert ("DEPENDS_ON_DATA", "EXACT_LITERAL_PATH") in by_type_derivation
    assert ("CITES_REQUIREMENT", "EXACT_COMMENT_CITATION") in by_type_derivation
    assert ("CITES_REQUIREMENT", "HEURISTIC_COMMENT_SECTION") in by_type_derivation
    assert ("TESTS", "EXACT_CLI_DISPATCH") in by_type_derivation
    # BR-AR-0019 reopening (fourth pass): this fixture's own registry entry ("tests/fx/test_fx_cap.py::test_one",
    # a pytest node id -- a '/' and a '.', never a bare Rust `a::b::fn` path) now correctly lands in the raw-text
    # bucket rather than the old blanket EXACT label; see tests/graph/test_derive.py's own registry tests for
    # full coverage of the OTHER three buckets (exact code-symbol match, ambiguous symbol, id-grammar token).
    assert ("TESTS", "HEURISTIC_TEST_REGISTRY_RAW_TEXT") in by_type_derivation

    digest = LL.lineage_layer_digest(conn)
    assert digest.rows == len(rows)
    assert digest.digest != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # not the empty hash


def test_lineage_layer_digest_reproducible_across_two_from_clean_builds(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs",
        "fn f() {\n    let p = \"config/corpus-rules.yaml\";\n}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "reproducibility fixture")

    digests = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)
        digests.append(LL.lineage_layer_digest(conn).digest)
    assert digests[0] == digests[1]


def test_lineage_layer_never_descends_into_excluded_paths(repo, monkeypatch):
    """The code layer must keep honouring corpus-rule exclusions (BR-AR-0014): a rule that EXCLUDEs a path means
    ``corpus.classify_entry`` never returns INCLUDE for it, so ``lineage_layer_builder`` -- which gates on
    ``verdict.effect != INCLUDE_EFFECT`` before reading any blob -- never derives an edge from its content."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(
        repo, "runtime/src/secret.rs",
        "fn f() {\n    let p = \"config/corpus-rules.yaml\";\n}\n",
    )
    authority_repobuilder.write(
        repo, "config/corpus-rules.yaml",
        "schema: govbridge-corpus-rules/1\n"
        "rules:\n"
        "- {id: EXCLUDE_SECRET, effect: EXCLUDE, match: {globs: ['runtime/src/secret.rs']}}\n"
        "- {id: INCLUDED, effect: INCLUDE, match: {}}\n",
    )
    rules = corpus.load_rules(str(repo / "config" / "corpus-rules.yaml"))
    commit = authority_repobuilder._commit(repo, "exclusion fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)
    rows = conn.execute("SELECT * FROM lineage_edge WHERE src LIKE 'runtime/src/secret.rs%'").fetchall()
    assert rows == []
    assert stats["blobs_scanned"] == 1  # only config/corpus-rules.yaml itself (a yaml file, INCLUDEd)


# --- BR-AR-0019 REOPENING: Gap 1 telemetry (never silently drop a citation) ----------------------------------

def test_lineage_layer_gap1_telemetry_document_only_and_unresolved(repo, monkeypatch):
    """The three-way split the reopening ruling asks for: resolved to section, resolved to document only,
    unresolved by reason -- and every unresolved citation persisted, never just discarded."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(repo, "release/x/DOC.md", "# Doc\n\n## 1 Something\ntext\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs",
        "// resolved to section: release/x/DOC.md section 1\n"
        "// resolved to document only: release/x/DOC.md section 99\n"
        "// unresolved (no such document): NOSUCHDOC.md section 1\n"
        "fn f() {}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "gap1 telemetry fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)

    assert stats["cites_requirement_resolved_to_section"] == 1
    assert stats["cites_requirement_resolved_to_document_only"] == 1
    assert stats["cites_requirement_unresolved_by_reason"]
    assert sum(stats["cites_requirement_unresolved_by_reason"].values()) == 1

    unresolved_rows = conn.execute("SELECT path, candidate, form, reason FROM lineage_unresolved").fetchall()
    assert len(unresolved_rows) == 1
    assert unresolved_rows[0][1] == "NOSUCHDOC.md"
    assert unresolved_rows[0][2] == "section"
    assert "no path matches" in unresolved_rows[0][3]

    doc_only_rows = conn.execute(
        "SELECT dst FROM lineage_edge WHERE derivation = ?", ("HEURISTIC_SECTION_UNRESOLVED",)
    ).fetchall()
    assert doc_only_rows == [("release/x/DOC.md",)]


def test_lineage_layer_digest_covers_unresolved_rows_too(repo, monkeypatch):
    """Two from-clean builds of the SAME fixture (including its unresolved citation) still produce an identical
    digest -- the digest is not blind to what lineage_unresolved holds."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs", "// NOSUCHDOC.md section 1\nfn f() {}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "digest fixture")

    digests = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)
        digests.append(LL.lineage_layer_digest(conn))
    assert digests[0].digest == digests[1].digest
    assert digests[0].extra["unresolved_rows"] == 1


# --- BR-AR-0019 REOPENING: Gap 2 (Rust CLI dispatch), wired end to end through the builder ---------------------

def test_lineage_layer_builder_persists_rust_cli_dispatch_edges(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "cli/src/main.rs",
        "#[derive(Parser)]\nstruct Cli { #[command(subcommand)] cmd: Cmd }\n"
        "#[derive(Subcommand)]\nenum Cmd { Version }\n"
        "fn dispatch(cli: &Cli) { match &cli.cmd { Cmd::Version => print_version(), } }\n",
    )
    authority_repobuilder.write(
        repo, "tests/certification/basic.rs",
        "fn my_bin() -> std::path::PathBuf { std::path::PathBuf::from(env!(\"CARGO_BIN_EXE_mybin\")) }\n"
        "#[test]\nfn test_version() {\n"
        "    let out = std::process::Command::new(my_bin()).args([\"version\"]).output().unwrap();\n"
        "}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "gap2 fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)

    assert stats["rust_cli_dispatch_variants"] > 0
    assert stats["rust_cli_bin_helpers"] == 1
    assert stats["rust_cli_test_files_scanned"] == 1

    rows = conn.execute(
        "SELECT src, dst, derivation FROM lineage_edge WHERE derivation = ?", ("EXACT_RUST_CLI_DISPATCH",)
    ).fetchall()
    assert rows == [("test_version", "print_version", "EXACT_RUST_CLI_DISPATCH")]


def test_lineage_layer_rust_cli_dispatch_digest_reproducible(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "cli/src/main.rs",
        "#[derive(Parser)]\nstruct Cli { #[command(subcommand)] cmd: Cmd }\n"
        "#[derive(Subcommand)]\nenum Cmd { Version }\n"
        "fn dispatch(cli: &Cli) { match &cli.cmd { Cmd::Version => print_version(), } }\n",
    )
    authority_repobuilder.write(
        repo, "tests/certification/basic.rs",
        "fn my_bin() -> std::path::PathBuf { std::path::PathBuf::from(env!(\"CARGO_BIN_EXE_mybin\")) }\n"
        "#[test]\nfn test_version() {\n"
        "    let out = std::process::Command::new(my_bin()).args([\"version\"]).output().unwrap();\n"
        "}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "gap2 digest fixture")

    digests = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)
        digests.append(LL.lineage_layer_digest(conn).digest)
    assert digests[0] == digests[1]
    # end of Gap-2 (second pass) coverage; BR-AR-0019's THIRD pass (Defect A/B) tests follow below.


# --- BR-AR-0019 REOPENING (third pass), Defect A: walk every eager ref, tag ref/commit/version_status -----------

def test_lineage_layer_walks_every_eager_ref_and_tags_version_status(repo, monkeypatch):
    """Two commits on the SAME fixture repo stand in for a stale "records" ref and a canonical "product" ref: the
    builder must derive edges from BOTH (not just the one it used to hard-code), and every row's own version
    status must say which one is canonical."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(repo, "config/old-data.yaml", "old: true\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs", "fn f() {\n    let p = \"config/old-data.yaml\";\n}\n",
    )
    rules = _rules(repo)
    old_commit = authority_repobuilder._commit(repo, "stale (records) content")

    authority_repobuilder.write(repo, "config/new-data.yaml", "new: true\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs", "fn f() {\n    let p = \"config/new-data.yaml\";\n}\n",
    )
    new_commit = authority_repobuilder._commit(repo, "canonical (product) content")

    resolved = _resolved_view(
        repo, [("product", new_commit, "product"), ("records", old_commit, "primary")],
        partitions=[{"name": "all", "owner": "product", "fallback": ["records"], "paths": ["**"]}],
    )

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, resolved, rules, str(repo), from_clean=True)

    assert stats["eager_refs"] == ["product", "records"]
    assert stats["by_ref"]["product"]["edges"] >= 1
    assert stats["by_ref"]["records"]["edges"] >= 1

    rows = conn.execute(
        "SELECT ref_name, commit_id, dst, version_status, canonical_ref, canonical_commit FROM lineage_edge "
        "WHERE type = 'DEPENDS_ON_DATA' ORDER BY ref_name"
    ).fetchall()
    assert rows == [
        ("product", new_commit, "config/new-data.yaml", "CANONICAL", "product", new_commit),
        ("records", old_commit, "config/old-data.yaml", "HISTORICAL_VERSION", "product", new_commit),
    ]


def test_lineage_layer_same_test_name_and_handler_in_two_refs_both_retained(repo, monkeypatch):
    """The PK gained ref_name/commit_id precisely so a TESTS edge (keyed by bare test name, not occ()) from a
    STALE ref never silently overwrites -- or gets silently overwritten by -- the same-named edge from a
    canonical ref: BOTH rows must survive, each correctly tagged."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(repo, "topcli/__init__.py", "")
    authority_repobuilder.write(
        repo, "topcli/main.py",
        "def main(argv):\n"
        "    cmd, rest = argv[0], argv[1:]\n"
        "    if cmd == 'greet':\n"
        "        from topcli import greeter\n"
        "        return greeter.main(rest)\n"
        "    return 2\n",
    )
    authority_repobuilder.write(repo, "topcli/greeter.py", "def main(argv):\n    return 0\n")
    authority_repobuilder.write(
        repo, "tests/test_via_cli.py",
        "import subprocess, sys\n"
        "def test_cli_invocation():\n"
        "    subprocess.run([sys.executable, '-m', 'topcli.main', 'greet', 'hello'])\n",
    )
    rules = _rules(repo)
    commit_1 = authority_repobuilder._commit(repo, "first (records)")
    # a second, otherwise-unrelated commit -- the test file's content is UNCHANGED, so both refs derive the exact
    # same (src, type, dst, derivation), which is exactly the collision the old schema could not tell apart.
    authority_repobuilder.write(repo, "README.md", "unrelated change\n")
    commit_2 = authority_repobuilder._commit(repo, "second (product)")

    resolved = _resolved_view(
        repo, [("product", commit_2, "product"), ("records", commit_1, "primary")],
        partitions=[{"name": "all", "owner": "product", "fallback": ["records"], "paths": ["**"]}],
    )

    conn = sqlite3.connect(":memory:")
    LL.lineage_layer_builder(conn, resolved, rules, str(repo), from_clean=True)

    rows = conn.execute(
        "SELECT ref_name, commit_id FROM lineage_edge WHERE src = 'test_cli_invocation' ORDER BY ref_name"
    ).fetchall()
    assert rows == [("product", commit_2), ("records", commit_1)]


def test_version_status_agrees_with_classify_occurrence(repo, monkeypatch):
    """A standing guard against ``_version_status`` ever diverging from the real, git-backed
    ``classify_occurrence`` it is a measured substitution for (see its own docstring) -- exercised across the
    CANONICAL, HISTORICAL_VERSION and fallback-only cases a real multi-ref build hits."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "shared.txt", "v1\n")
    authority_repobuilder.write(repo, "records-only.txt", "records\n")
    commit_1 = authority_repobuilder._commit(repo, "records state")
    authority_repobuilder.write(repo, "shared.txt", "v2\n")
    import os
    os.remove(str(repo / "records-only.txt"))
    authority_repobuilder.write(repo, "product-only.txt", "product\n")
    commit_2 = authority_repobuilder._commit(repo, "product state")

    resolved = _resolved_view(
        repo, [("product", commit_2, "product"), ("records", commit_1, "primary")],
        partitions=[{"name": "all", "owner": "product", "fallback": ["records"], "paths": ["**"]}],
    )
    ref_trees = {
        name: {e.path: e.oid for e in gitobj.ls_tree(resolved.named[name].commit, repo=str(repo))
               if e.type == "blob"}
        for name in ("product", "records")
    }

    cases = [
        ("product", commit_2, "shared.txt"),        # CANONICAL (this ref IS the owner, at the owner's commit)
        ("records", commit_1, "shared.txt"),         # HISTORICAL_VERSION (owner has a DIFFERENT blob for it)
        ("records", commit_1, "records-only.txt"),   # absent at owner -> falls back to "records" itself
    ]
    for ref_name, commit, path in cases:
        blob_id = ref_trees[ref_name][path]
        fast = LL._version_status(resolved, ref_trees, ref_name, commit, path, blob_id)
        real_cls = resolved.classify_occurrence(path, commit, queried_blob=blob_id)
        real = (real_cls.status, real_cls.canonical_ref, real_cls.canonical_commit)
        assert fast == real, (ref_name, path, fast, real)


# --- BR-AR-0019 REOPENING (third pass), Defect B: harness-METHOD dispatch, wired end to end through the builder -

def test_lineage_layer_builder_persists_harness_method_dispatch_edges(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "cli/src/main.rs",
        "#[derive(Parser)]\nstruct Cli { #[command(subcommand)] cmd: Cmd }\n"
        "#[derive(Subcommand)]\nenum Cmd { Version }\n"
        "fn dispatch(cli: &Cli) { match &cli.cmd { Cmd::Version => print_version(), } }\n",
    )
    authority_repobuilder.write(
        repo, "tests/certification/harness.rs",
        "fn my_bin() -> std::path::PathBuf { std::path::PathBuf::from(env!(\"CARGO_BIN_EXE_mybin\")) }\n"
        "struct Harness { session: String }\n"
        "impl Harness {\n"
        "    fn new() -> Self { Harness { session: \"s\".into() } }\n"
        "    fn ok(&self, args: &[&str]) -> Vec<u8> {\n"
        "        std::process::Command::new(my_bin()).args(args).output().unwrap().stdout\n"
        "    }\n"
        "}\n"
        "#[test]\nfn test_harness_version() {\n"
        "    let h = Harness::new();\n"
        "    let out = h.ok(&[\"version\"]);\n"
        "}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "defect b fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)

    assert stats["rust_cli_harness_wrapper_methods"] >= 1
    rows = conn.execute(
        "SELECT src, dst, derivation FROM lineage_edge WHERE type = 'TESTS' AND src = 'test_harness_version'"
    ).fetchall()
    assert rows == [("test_harness_version", "print_version", "EXACT_RUST_CLI_DISPATCH")]
    assert stats["rust_cli_harness_dispatch_edges_declared_type"] == 1


def test_lineage_layer_builder_test_registry_resolves_against_real_code_symbols(repo, monkeypatch):
    """BR-AR-0019 reopening (fourth pass), requirement 3, wired end to end through the builder against the SAME
    on-disk code index the real pipeline shares (tests/code/conftest.py's autouse ``_isolated_store`` fixture
    gives this test its own, so it never touches another test's or the real domain's store). Two real code-layer
    test symbols: an ``impl`` method (qualified_name carries "Type::method", so a registry entry with that SHAPE
    resolves EXACTLY) and a plain ``mod``-nested function (this repository's own tree-sitter adapter gives it a
    BARE qualified_name, no module prefix at all -- rust_treesitter.py's own ``_walk``, module comment above --
    so a registry entry that itself carries a module prefix, e.g. "ws03::my_check", resolves only by its own
    trailing segment, landing in the heuristic bucket with a note saying exactly why)."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "tests/certification/demo.rs",
        "mod ws03 {\n"
        "    #[test]\n"
        "    fn my_check() {}\n"
        "}\n"
        "struct Harness2;\n"
        "impl Harness2 {\n"
        "    #[test]\n"
        "    fn my_method_test() {}\n"
        "}\n",
    )
    authority_repobuilder.write(
        repo, "release/decision-register/DEMO_REGISTER.yaml",
        "decisions:\n"
        "  - id: DR-01\n"
        "    tests: [Harness2::my_method_test]\n"
        "  - id: DR-02\n"
        "    tests: [ws03::my_check]\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "registry code-symbol fixture")
    resolved = _resolved_view_one_ref(repo, commit)

    # populate code_symbol on the SAME connection first, exactly like a real freshness.run() would (the "core"
    # then "code" layer builders run before "lineage" -- see _test_symbol_counts_for_ref's own comment for why
    # this MUST be the same connection, never a second one opened internally)
    conn = sqlite3.connect(":memory:")
    from govbridge.core import freshness as F
    from govbridge.core import store as corestore
    from govbridge.code import build as codebuild
    conn.executescript(corestore.SCHEMA_SQL)
    F.core_layer_builder(conn, resolved, rules, str(repo), from_clean=True)
    codebuild.code_layer_builder(conn, resolved, rules, str(repo), from_clean=True)

    stats = LL.lineage_layer_builder(conn, resolved, rules, str(repo), from_clean=True)

    assert stats["test_registry_rows"] == 2
    rows = conn.execute(
        "SELECT dst, src, derivation, note FROM lineage_edge WHERE type = 'TESTS' "
        "AND (derivation LIKE 'HEURISTIC_TEST_REGISTRY%' OR derivation = 'EXACT_TEST_REGISTRY_ROW') "
        "ORDER BY dst"
    ).fetchall()
    by_dst = {r[0]: r for r in rows}
    assert by_dst["DR-01"][2] == "EXACT_TEST_REGISTRY_ROW"
    assert by_dst["DR-02"][2] == "HEURISTIC_TEST_REGISTRY_SYMBOL"
    assert "bare name only" in by_dst["DR-02"][3]


def test_lineage_layer_builder_records_ambiguous_harness_method_unresolved(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "cli/src/main.rs",
        "#[derive(Parser)]\nstruct Cli { #[command(subcommand)] cmd: Cmd }\n"
        "#[derive(Subcommand)]\nenum Cmd { Version }\n"
        "fn dispatch(cli: &Cli) { match &cli.cmd { Cmd::Version => print_version(), } }\n",
    )
    authority_repobuilder.write(
        repo, "tests/certification/ambiguous.rs",
        "fn my_bin() -> std::path::PathBuf { std::path::PathBuf::from(env!(\"CARGO_BIN_EXE_mybin\")) }\n"
        "struct Alpha;\n"
        "impl Alpha { fn ok(&self, args: &[&str]) -> Vec<u8> "
        "{ std::process::Command::new(my_bin()).args(args).output().unwrap().stdout } }\n"
        "struct Beta;\n"
        "impl Beta { fn ok(&self, args: &[&str]) -> Vec<u8> "
        "{ std::process::Command::new(my_bin()).args(args).output().unwrap().stdout } }\n"
        "#[test]\nfn test_ambiguous() {\n"
        "    let out = make_either().ok(&[\"version\"]);\n"
        "}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "defect b ambiguous fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _resolved_view_one_ref(repo, commit), rules, str(repo), from_clean=True)

    assert stats["rust_harness_method_unresolved_by_reason"]
    rows = conn.execute(
        "SELECT candidate, form, reason FROM lineage_unresolved WHERE form = 'rust_harness_method'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "ok"
    assert "ambiguous method name" in rows[0][2]
