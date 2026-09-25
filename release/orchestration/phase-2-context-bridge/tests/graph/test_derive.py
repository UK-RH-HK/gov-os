"""Edge derivation (ARCHITECTURE.md section 6.1) on the fixture repo: DEFINES, MENTIONS (EXACT_ID), CITES_PATH/
CITES_LINE, CITES_COMMIT, SUPERSEDES (registry + metadata), CODE_CITES, RELATION_CUE, and CALLS/READS_KEY/TESTS
against a synthetic connection matching B3's table schema (symbol, call_site, literal, resolution --
ARCHITECTURE.md section 4.6). The B3-dependent functions must return [] with conn=None (a legitimate MISSING, not
an error) -- the real code route arrives in I1.
"""
import sqlite3

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
