"""Edge derivation (ARCHITECTURE.md section 6.1) on the fixture repo: DEFINES, MENTIONS (EXACT_ID), CITES_PATH/
CITES_LINE, CITES_COMMIT, SUPERSEDES (registry + metadata), CODE_CITES, RELATION_CUE, and CALLS/READS_KEY/TESTS
against a synthetic connection matching B3's table schema (symbol, call_site, literal, resolution --
ARCHITECTURE.md section 4.6). The B3-dependent functions must return [] with conn=None (a legitimate MISSING, not
an error) -- the real code route arrives in I1.
"""
import sqlite3
from pathlib import Path

from govbridge.authority import records, registry
from govbridge.core import view as viewmod
from govbridge.graph import derive as D
from govbridge.graph import edges as E


def _commit(fixture_repo, view_path):
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    return rv.ref_commit("records")


def test_defines_edge_for_table_id(fixture_repo, view_path, registry_path):
    import authority_repobuilder as repobuilder
    grammar = records.load_grammar("config/id-grammar.yaml")
    commit = _commit(fixture_repo, view_path)
    edges = D.defines_edges_for_id("OA-FX-06", commit, repo=str(fixture_repo.root), grammar=grammar)
    assert any(e.dst == "OA-FX-06" and e.type == E.DEFINES and repobuilder.OWNER_AUTH_PATH in e.src
               for e in edges)


def test_mentions_edge_exact_id(fixture_repo, view_path):
    grammar = records.load_grammar("config/id-grammar.yaml")
    commit = _commit(fixture_repo, view_path)
    edges = D.mentions_edges_for_id("FX-0001", commit, repo=str(fixture_repo.root), grammar=grammar)
    assert any(e.derivation == E.EXACT_ID for e in edges)
    # the ledger mentions FX-0001
    assert any("PHASE_LEDGER" in e.evidence_occurrence for e in edges)


def test_cites_path_and_line(fixture_repo, view_path):
    import authority_repobuilder as repobuilder
    commit = _commit(fixture_repo, view_path)
    text = (
        "See runtime/src/fx_module.rs for the implementation.\n"
        "See runtime/src/fx_module.rs:2 for the exact line.\n"
    )
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=str(fixture_repo.root))
    edges = D.cites_edges_in_text(text, "some/citing-record.md", commit, rv, repo=str(fixture_repo.root))
    types = {e.type for e in edges}
    assert E.CITES_PATH in types
    assert E.CITES_LINE in types
    line_edge = [e for e in edges if e.type == E.CITES_LINE][0]
    assert line_edge.dst == "runtime/src/fx_module.rs:2-2"


def test_cites_commit(fixture_repo, view_path):
    commit = _commit(fixture_repo, view_path)
    text = f"see commit {fixture_repo.c1} for the original content\n"
    edges = D.cites_commit_edges_in_text(text, "some/citing-record.md", commit, repo=str(fixture_repo.root))
    assert any(e.dst == fixture_repo.c1 for e in edges)


def test_supersession_edges_from_registry(fixture_repo, view_path, registry_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    edges = D.supersession_edges("OA-FX-06", reg)
    assert any(e.type == E.SUPERSEDES and e.src == "OD-FX-07" and e.dst == "OA-FX-06" for e in edges)


def test_metadata_supersession_edges():
    doc = {"id": "FX-0001", "status": "SUPERSEDED", "superseded_by": "FX-0002"}
    edges = D.metadata_supersession_edges("FX-0001", doc, "spec/decisions/FX-0001.yaml", "deadbeef")
    assert any(e.src == "FX-0001" and e.dst == "FX-0002" and e.derivation == E.EXACT_METADATA for e in edges)


def test_code_cites_finds_comment_mention(fixture_repo, view_path):
    commit = _commit(fixture_repo, view_path)
    edges = D.code_cites_edges_for_id("FX-0001", commit, repo=str(fixture_repo.root), code_dirs=("runtime/",))
    assert len(edges) == 1
    assert edges[0].type == E.CODE_CITES
    assert edges[0].derivation == E.EXACT_ID


def test_relation_cue_reopens():
    edges = [E.Edge(src="a", type=E.MENTIONS, dst="FX-0002", derivation=E.EXACT_ID, evidence_occurrence="x@y",
                     evidence_line=1)]
    sentences = {1: "Second ledger entry, mentions FX-0001 and reopens FX-0002."}
    cue_edges = D.relation_cue_edges(edges, sentences)
    assert len(cue_edges) == 1
    assert cue_edges[0].note == "reopens"
    assert cue_edges[0].derivation == E.HEURISTIC_CUE


# --- CALLS / READS_KEY / TESTS against a synthetic connection matching B3's table schema -----------------------

def _b3_shaped_conn():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE symbol (symbol_id TEXT, blob TEXT, kind TEXT, name TEXT, qualified_name TEXT,
                              module_path TEXT, start INTEGER, end INTEGER, is_test INTEGER);
        CREATE TABLE call_site (blob TEXT, line INTEGER, caller_symbol TEXT, callee_text TEXT, callee_name TEXT,
                                 call_kind TEXT);
        CREATE TABLE literal (blob TEXT, line INTEGER, enclosing_symbol TEXT, value TEXT);
        CREATE TABLE resolution (call_site INTEGER, target_symbol TEXT, label TEXT, n_candidates INTEGER);
    """)
    conn.execute("INSERT INTO symbol VALUES ('s1','b1','fn','fx_rule','fx_module::fx_rule','fx_module',1,3,0)")
    conn.execute("INSERT INTO symbol VALUES ('s2','b1','fn','caller','fx_module::caller','fx_module',5,8,0)")
    conn.execute("INSERT INTO symbol VALUES ('s3','b1','fn','test_fx','fx_module::test_fx','fx_module',10,12,1)")
    cur = conn.execute(
        "INSERT INTO call_site(blob, line, caller_symbol, callee_text, callee_name, call_kind) "
        "VALUES ('b1', 6, 'fx_module::caller', 'fx_rule()', 'fx_rule', 'call')"
    )
    call_site_rowid = cur.lastrowid
    conn.execute(
        "INSERT INTO resolution(call_site, target_symbol, label, n_candidates) VALUES (?, 's1', 'EXACT_PATH', 1)",
        (call_site_rowid,),
    )
    cur2 = conn.execute(
        "INSERT INTO call_site(blob, line, caller_symbol, callee_text, callee_name, call_kind) "
        "VALUES ('b1', 11, 'fx_module::test_fx', 'fx_rule()', 'fx_rule', 'call')"
    )
    conn.execute(
        "INSERT INTO resolution(call_site, target_symbol, label, n_candidates) VALUES (?, 's1', 'EXACT_PATH', 1)",
        (cur2.lastrowid,),
    )
    conn.execute("INSERT INTO literal VALUES ('b1', 7, 'fx_module::caller', 'mutation')")
    conn.commit()
    return conn


def test_calls_missing_without_conn():
    assert D.callers_of(None, "fx_module::fx_rule") == []
    assert D.callees_of(None, "fx_module::caller") == []
    assert D.reads_key_of(None, "mutation") == []
    assert D.tests_of(None, "fx_module::fx_rule") == []


def test_callers_of_b3_shaped_conn():
    conn = _b3_shaped_conn()
    edges = D.callers_of(conn, "fx_module::fx_rule")
    assert len(edges) == 2
    assert all(e.type == E.CALLS and e.dst == "fx_module::fx_rule" for e in edges)
    assert all(e.derivation == "EXACT_PATH" for e in edges)


def test_callees_of_b3_shaped_conn():
    conn = _b3_shaped_conn()
    edges = D.callees_of(conn, "fx_module::caller")
    assert len(edges) == 1
    assert edges[0].dst == "fx_module::fx_rule"


def test_reads_key_of_b3_shaped_conn():
    conn = _b3_shaped_conn()
    edges = D.reads_key_of(conn, "mutation")
    assert len(edges) == 1
    assert edges[0].src == "fx_module::caller"
    assert edges[0].type == E.READS_KEY


def test_tests_of_b3_shaped_conn():
    conn = _b3_shaped_conn()
    edges = D.tests_of(conn, "fx_module::fx_rule")
    assert len(edges) == 1
    assert edges[0].src == "fx_module::test_fx"
    assert edges[0].type == E.TESTS
    assert edges[0].derivation == E.EXACT_PATH


# --- R1-RL additions: paging over tests_of/reads_key_of ----------------------------------------------------------

def _b3_shaped_conn_many_tests(n: int = 5):
    """A B3-shaped connection (the same schema _b3_shaped_conn() uses) with ``n`` distinct test symbols, each
    calling the SAME target, plus ``n`` distinct literal reads of the same key -- enough rows to page over."""
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE symbol (symbol_id TEXT, blob TEXT, kind TEXT, name TEXT, qualified_name TEXT,
                              module_path TEXT, start INTEGER, end INTEGER, is_test INTEGER);
        CREATE TABLE call_site (blob TEXT, line INTEGER, caller_symbol TEXT, callee_text TEXT, callee_name TEXT,
                                 call_kind TEXT);
        CREATE TABLE literal (blob TEXT, line INTEGER, enclosing_symbol TEXT, value TEXT);
        CREATE TABLE resolution (call_site INTEGER, target_symbol TEXT, label TEXT, n_candidates INTEGER);
    """)
    conn.execute("INSERT INTO symbol VALUES ('s0','b1','fn','fx_rule','fx_module::fx_rule','fx_module',1,3,0)")
    for i in range(n):
        conn.execute(
            "INSERT INTO symbol VALUES (?,?,?,?,?,?,?,?,1)",
            (f"st{i}", "b1", "fn", f"test_{i}", f"fx_module::test_{i}", "fx_module", 10 + i, 12 + i),
        )
        cur = conn.execute(
            "INSERT INTO call_site(blob, line, caller_symbol, callee_text, callee_name, call_kind) "
            "VALUES ('b1', ?, ?, 'fx_rule()', 'fx_rule', 'call')", (20 + i, f"fx_module::test_{i}"),
        )
        conn.execute(
            "INSERT INTO resolution(call_site, target_symbol, label, n_candidates) VALUES (?, 's0', 'EXACT_PATH', 1)",
            (cur.lastrowid,),
        )
        conn.execute("INSERT INTO literal VALUES ('b1', ?, ?, 'mutation')", (30 + i, f"fx_module::test_{i}"))
    conn.commit()
    return conn


def test_tests_of_unpaged_return_type_is_unchanged():
    conn = _b3_shaped_conn_many_tests(3)
    edges = D.tests_of(conn, "fx_module::fx_rule")
    assert isinstance(edges, list) and len(edges) == 3


def test_tests_of_paged_union_equals_unpaged():
    conn = _b3_shaped_conn_many_tests(5)
    full = D.tests_of(conn, "fx_module::fx_rule")
    collected, cursor, pages = [], None, 0
    while True:
        page = D.tests_of(conn, "fx_module::fx_rule", page_size=2, cursor=cursor)
        pages += 1
        assert isinstance(page, dict) and page["total"] == 5
        collected.extend(page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert pages == 3
    assert [e.to_dict() for e in collected] == [e.to_dict() for e in full]


def test_reads_key_of_paged_union_equals_unpaged():
    conn = _b3_shaped_conn_many_tests(5)
    full = D.reads_key_of(conn, "mutation")
    collected, cursor = [], None
    while True:
        page = D.reads_key_of(conn, "mutation", page_size=2, cursor=cursor)
        collected.extend(page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert [e.to_dict() for e in collected] == [e.to_dict() for e in full]


def test_paging_of_missing_conn_is_still_a_page_shape():
    assert D.tests_of(None, "x", page_size=2) == {"items": [], "next_cursor": None, "total": 0}
    assert D.reads_key_of(None, "x", page_size=2) == {"items": [], "next_cursor": None, "total": 0}


# --- R1-RL additions: DEPENDS_ON_DATA / CITES_REQUIREMENT ----------------------------------------------------------

def _code_repo(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    import _repobuilder as rb
    root = tmp_path / "repo"
    rb.init(root)
    return rb, root


def test_depends_on_data_single_literal_and_joined_literals(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "config/corpus-rules.yaml", "rules: []\n")
    rb.write(root, "config/id-grammar.yaml", "version: 1\n")
    rb.write(
        root, "runtime/src/lib.rs",
        'fn f() {\n'
        '    let p = "config/corpus-rules.yaml";\n'
        '    let j = path_of("config", "id-grammar.yaml");\n'
        '}\n',
    )
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/lib.rs").read_text()
    edges = D.depends_on_data_edges(text, "runtime/src/lib.rs", commit, repo=str(root))
    by_dst = {e.dst: e for e in edges}
    assert by_dst["config/corpus-rules.yaml"].derivation == E.EXACT_LITERAL_PATH
    assert by_dst["config/id-grammar.yaml"].derivation == E.HEURISTIC_JOINED_PATH


def test_depends_on_data_ignores_non_code_dirs(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "config/corpus-rules.yaml", "rules: []\n")
    rb.write(root, "spec/notes.md", 'See "config/corpus-rules.yaml".\n')
    commit = rb.commit(root, "c1")
    text = (root / "spec/notes.md").read_text()
    assert D.depends_on_data_edges(text, "spec/notes.md", commit, repo=str(root)) == []


def test_cites_requirement_line_and_section_forms(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "framework/contracts/contract.md", "# Contract\n\n## 4 Budgets\ntext here\n")
    rb.write(
        root, "runtime/src/lib.rs",
        "// See framework/contracts/contract.md:3 for the rule.\n"
        "// Also framework/contracts/contract.md section 4 covers budgets.\n"
        "fn f() {}\n",
    )
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/lib.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/lib.rs", commit, repo=str(root))
    assert unresolved == []
    by_derivation = {e.derivation: e for e in edges}
    assert by_derivation[E.EXACT_COMMENT_CITATION].dst == "framework/contracts/contract.md:3-3"
    assert by_derivation[E.HEURISTIC_COMMENT_SECTION].dst == "framework/contracts/contract.md:3"


def test_cites_requirement_ignores_non_comment_lines(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "framework/contracts/contract.md", "# Contract\n")
    rb.write(root, "runtime/src/lib.rs", 'let s = "framework/contracts/contract.md:1";\n')
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/lib.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/lib.rs", commit, repo=str(root))
    assert edges == []
    assert unresolved == []


def test_cites_requirement_backtick_bare_name_and_doc_comments(tmp_path):
    """BR-AR-0019 reopening, Gap 1's own worked example: a backticked BARE document name (no path separator),
    resolved as a unique suffix, inside a `///`/`//!` doc comment, with a decimal section number."""
    rb, root = _code_repo(tmp_path)
    rb.write(root, "release/x/SYNTHESIS.md", "# Synthesis\n\n## 10 Something\ntext\n\n### 10.4 Sub-point\nmore\n")
    rb.write(
        root, "runtime/src/adopt.rs",
        "/// (`SYNTHESIS.md §10.4`), so without being recorded as an authenticated floor\n"
        "//! also verified here, in an inner doc comment\n"
        "fn f() {}\n",
    )
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/adopt.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/adopt.rs", commit, repo=str(root))
    assert unresolved == []
    section_edges = [e for e in edges if e.derivation == E.HEURISTIC_COMMENT_SECTION]
    assert len(section_edges) == 1
    assert section_edges[0].dst == "release/x/SYNTHESIS.md:6"  # the "### 10.4 Sub-point" heading line
    assert section_edges[0].note == "section 10.4"


def test_cites_requirement_document_resolves_but_section_does_not_is_never_dropped(tmp_path):
    """BR-AR-0019 reopening, Gap 1's central requirement: the document is real and unique, but the cited section
    number is not a heading there -- an edge to the DOCUMENT, never a silent drop."""
    rb, root = _code_repo(tmp_path)
    rb.write(root, "release/x/SYNTHESIS.md", "# Synthesis\n\n## 0 Independence\ntext\n\n## 6 Something\nmore\n")
    rb.write(
        root, "runtime/src/adopt.rs",
        "/// (`SYNTHESIS.md §10.4`), a section that this document does not have\n"
        "fn f() {}\n",
    )
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/adopt.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/adopt.rs", commit, repo=str(root))
    assert unresolved == []
    assert len(edges) == 1
    assert edges[0].derivation == E.HEURISTIC_SECTION_UNRESOLVED
    assert edges[0].dst == "release/x/SYNTHESIS.md"
    assert edges[0].note == "section 10.4"


def test_cites_requirement_range_form(tmp_path):
    """A §N-M / §N–M range (BR-AR-0019 reopening, Gap 1): resolves against its start section; extends through the
    end section's own heading when that ALSO resolves."""
    rb, root = _code_repo(tmp_path)
    rb.write(
        root, "release/x/REPORT.md",
        "# Report\n\n## 11 First\ntext\n\n## 12 Second\nmore\n\n## 13 Third\nyet more\n",
    )
    rb.write(
        root, "runtime/src/repair.rs",
        "//! (release/x/REPORT.md §11–12). Each test names the finding it covers\n"
        "fn f() {}\n",
    )
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/repair.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/repair.rs", commit, repo=str(root))
    assert unresolved == []
    assert len(edges) == 1
    assert edges[0].derivation == E.HEURISTIC_COMMENT_SECTION
    assert edges[0].dst == "release/x/REPORT.md:3-6"  # section 11's heading line through section 12's own line
    assert edges[0].note == "sections 11-12"


def test_cites_requirement_document_does_not_resolve_is_reported_unresolved(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "runtime/src/lib.rs", "// See NOSUCHDOC.md:3 for the rule.\n// NOSUCHDOC.md section 4 too.\nfn f() {}\n")
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/lib.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/lib.rs", commit, repo=str(root))
    assert edges == []
    forms = {u["form"] for u in unresolved}
    assert forms == {"path:line", "section"}
    assert all(u["reason"] and "no path matches" in u["reason"] for u in unresolved)


def test_cites_requirement_ambiguous_document_is_reported_unresolved(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(root, "a/NOTES.md", "# A\n")
    rb.write(root, "b/NOTES.md", "# B\n")
    rb.write(root, "runtime/src/lib.rs", "// See NOTES.md section 1 for context.\nfn f() {}\n")
    commit = rb.commit(root, "c1")
    text = (root / "runtime/src/lib.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "runtime/src/lib.rs", commit, repo=str(root))
    assert edges == []
    assert len(unresolved) == 1
    assert unresolved[0]["form"] == "section"
    assert "ambiguous" in unresolved[0]["reason"]


def test_cites_requirement_scans_rust_test_files_too(tmp_path):
    """The CODE_DIRS gate must reach tests/**/*.rs (BR-AR-0019 reopening, Gap 1: certification tests' own doc
    comments were silently excluded before)."""
    rb, root = _code_repo(tmp_path)
    rb.write(root, "release/x/REPORT.md", "# Report\n\n## 11 Something\ntext\n")
    rb.write(
        root, "tests/certification/repair.rs",
        "//! (release/x/REPORT.md §11). Each test names the finding it covers\nfn f() {}\n",
    )
    commit = rb.commit(root, "c1")
    text = (root / "tests/certification/repair.rs").read_text()
    edges, unresolved = D.cites_requirement_edges_in_text(text, "tests/certification/repair.rs", commit,
                                                            repo=str(root))
    assert unresolved == []
    assert len(edges) == 1
    assert edges[0].derivation == E.HEURISTIC_COMMENT_SECTION


# --- R1-RL additions: TESTS beyond a direct call -- a test registry, and a CLI-dispatch-driven test ---------------

def test_registry_edges_generic_shape(tmp_path):
    rb, root = _code_repo(tmp_path)
    rb.write(
        root, "tests/fixtures/graph/demo-registry.yaml",
        "schema: fx-registry/1\n"
        "rows:\n"
        "  - capability: FX-CAP-1\n"
        "    tests:\n"
        "      - tests/fx/test_fx_cap.py::test_one\n"
        "      - tests/fx/test_fx_cap.py::test_two\n",
    )
    commit = rb.commit(root, "c1")
    edges = D.test_registry_edges_for_id("FX-CAP-1", commit, repo=str(root))
    srcs = {e.src for e in edges}
    assert srcs == {"tests/fx/test_fx_cap.py::test_one", "tests/fx/test_fx_cap.py::test_two"}
    assert all(e.type == E.TESTS and e.derivation == E.EXACT_TEST_REGISTRY_ROW for e in edges)


def test_cli_dispatch_tests_edge_resolves_a_subprocess_invoked_subcommand(tmp_path, monkeypatch):
    """A process-level test reaches its handler (the acceptance check, verbatim). Fully hermetic (BR-DAG-AMEND-R1-4):
    a SYNTHETIC two-level CLI dispatch (mirroring govbridge/cli.py's own "if cmd == '<name>': from <pkg> import
    <mod> as alias; return alias.main(rest)" shape, generically -- never this repository's real cli.py content, and
    never its live HEAD) committed to its own throwaway repo. ``resolve_cli_handler`` resolves a module path via a
    GOV_BRIDGE_DOMAIN-relative git path, so GOV_BRIDGE_DOMAIN is monkeypatched (module attribute, not env -- read
    inside the function via a fresh `from govbridge import GOV_BRIDGE_DOMAIN` every call) to this fixture's own
    root; no chdir, no dependence on the shared repository's refs, and no GOVBRIDGE_* environment leak."""
    import govbridge as govbridge_pkg

    rb, root = _code_repo(tmp_path)
    monkeypatch.setattr(govbridge_pkg, "GOV_BRIDGE_DOMAIN", str(root))

    rb.write(root, "topcli/__init__.py", "")
    rb.write(
        root, "topcli/main.py",
        "def main(argv):\n"
        "    cmd, rest = argv[0], argv[1:]\n"
        "    if cmd == 'greet':\n"
        "        from topcli import greeter\n"
        "        return greeter.main(rest)\n"
        "    return 2\n",
    )
    rb.write(
        root, "topcli/greeter.py",
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
    test_source = (
        "import subprocess, sys\n"
        "def test_cli_invocation():\n"
        "    subprocess.run([sys.executable, '-m', 'topcli.main', 'greet', 'hello', 'world'])\n"
    )
    rb.write(root, "tests/test_via_cli.py", test_source)
    commit = rb.commit(root, "synthetic CLI dispatch fixture")

    edges = D.cli_dispatch_tests_edges(test_source, "tests/test_via_cli.py", commit, repo=str(root))
    matches = [e for e in edges if e.dst == "topcli.greeter.say_hello"]
    assert matches, [e.to_dict() for e in edges]
    assert matches[0].derivation == E.EXACT_CLI_DISPATCH
    assert matches[0].type == E.TESTS
    assert matches[0].src == "test_cli_invocation"
