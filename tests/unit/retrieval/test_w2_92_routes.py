"""Builder tests for the record and code routes of plain-question retrieval (W2-92; DEC-957, DEC-859, DEC-860).

Regression evidence only (DEC-136). The record route takes only the ids, W2 ids and titles the store holds; the code
route asks the code-graph tool's own traversal in small pages, never the whole graph, leaves test files out and maps
spans to chunks; a missing or unreadable index is named, never ok; a question naming nothing gets today's bundle.
The code-graph tool is replaced by a planted graph; the retrieve cases build their store in a temporary repository.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel, store  # noqa: E402
from gov.retrieval import code_route, graph_route, lexical, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402

KNOWN = [{"id": "DEC-957", "type": "decision", "status": "ACCEPTED", "path": "docs/DECISION_REGISTER.md",
          "title": "The owner's decisions on memory"},
         {"id": "DEC-026", "type": "decision", "status": "ACCEPTED", "path": "docs/DECISION_REGISTER.md",
          "title": "Telemetry"},
         {"id": "CAP-12", "type": "capability", "status": "ACTIVE", "path": "docs/contract/CAP-12.md"},
         {"id": "CP-DAEO-0i6h-0001", "type": "checkpoint", "status": "ACTIVE", "path": "cp/1.md"},
         {"id": "DAEO-n0wb", "type": "task", "status": "open", "path": ".tickets/DAEO-n0wb.md"}]


@pytest.fixture()
def tickets(tmp_path):
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".tickets/DAEO-n0wb.md").write_text(
        "---\nid: DAEO-n0wb\nexternal-ref: W2-92\nwbs_id: W2-92\n---\n# x\n", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("query, expected", [
    ("What replaced DEC-957's listing refusal, and CAP-12?", ["CAP-12", "DEC-957"]),
    ("Is W2-92-tests merged into W2-92?", ["DAEO-n0wb"]),
    ("What did CP-DAEO-0i6h-0001 record?", ["CP-DAEO-0i6h-0001"]),
    ("what does   TELEMETRY keep?", ["DEC-026"]),
    ("what about the owner's decisions on memory", ["DEC-957"]),
    ("DEC-999, CAP-1 and W2-7 are no records here; telemetryx is no title", []),
    ("How does the lexical route rank chunks?", []),
])
def test_only_ids_and_titles_the_store_holds_become_start_ids(tickets, query, expected):
    assert graph_route.start_ids(tickets, query, KNOWN) == expected


def test_a_records_title_is_read_from_the_frontmatter_that_declares_it(tickets):
    (tickets / "docs/contract").mkdir(parents=True)
    (tickets / "docs/contract/CAP-12.md").write_text(
        "---\nid: CAP-12\ntype: capability\ntitle: Code intelligence\n---\n# x\n", encoding="utf-8")
    assert graph_route.start_ids(tickets, "what does code   intelligence answer?", KNOWN) == ["CAP-12"]
    assert graph_route.start_ids(tickets, "what about intelligence?", KNOWN) == []  # a title is found whole


def test_a_title_read_once_is_read_again_when_its_file_changes(tickets):
    record = tickets / "docs/contract/CAP-12.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\nid: CAP-12\ntitle: Code intelligence\n---\n", encoding="utf-8")
    assert graph_route.start_ids(tickets, "code intelligence", KNOWN) == ["CAP-12"]
    record.write_text("---\nid: CAP-12\ntitle: Harbour charts\n---\n", encoding="utf-8")
    assert graph_route.start_ids(tickets, "code intelligence", KNOWN) == []
    assert graph_route.start_ids(tickets, "the harbour charts", KNOWN) == ["CAP-12"]


# The planted code graph: qualified name -> (name, label, file, lines); and the calls between them.
NODES = {"code.src.fus.rrf": ("rrf", "Function", "src/fus.py", "10-14"),
         "code.tests.test_fus.rrf": ("rrf", "Function", "tests/test_fus.py", "1-3"),
         "code.src.ret.retrieve": ("retrieve", "Function", "src/ret.py", "20-30"),
         "code.src.ret.search": ("search", "Function", "src/ret.py", "40-45"),
         "code.tests.test_ret.test_it": ("test_it", "Function", "tests/test_ret.py", "5-9"),
         "code.src.fus.helper": ("helper", "Function", "src/fus.py", "1-3"),
         "code.src.fus.RRF": ("RRF", "Variable", "src/fus.py", "5-5")}
CALLS = {("code.src.ret.retrieve", "code.src.fus.rrf"), ("code.src.ret.search", "code.src.fus.rrf"),
         ("code.tests.test_ret.test_it", "code.src.fus.rrf"), ("code.src.fus.rrf", "code.src.fus.helper")}


class Planted:
    """The code-graph tool's search_graph and query_graph over the planted graph, one row a page, every call kept."""

    def __init__(self, calls, fail=False):
        self.calls, self.fail = calls, fail

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def tool(self, tool, **args):
        import re
        self.calls.append((tool, args))
        if self.fail:
            raise RuntimeError("codebase-memory-mcp search_graph failed (exit code 1)")
        if tool == "search_graph":
            pattern = re.compile(args.get("name_pattern") or args["qn_pattern"], re.IGNORECASE)
            keys = sorted(key for key, node in NODES.items()
                          if pattern.search(node[0] if "name_pattern" in args else key))
            offset = args["offset"]
            groups = [{"qn_prefix": key.rpartition(".")[0], "file": NODES[key][2],
                       "rows": [[NODES[key][0], NODES[key][1], NODES[key][3], 0, 0]]}
                      for key in keys[offset:offset + 1]]
            more = offset + 1 < len(keys)
            return {"groups": groups, "has_more": more, **({"next_offset": offset + 1} if more else {})}
        assert tool == "query_graph"
        side, key = re.fullmatch(r"MATCH \(a\)-\[:CALLS\]->\(b\) WHERE (a|b)\.qualified_name = '([^']+)' RETURN .*",
                                 args["query"]).groups()
        near = sorted(a if side == "b" else b for a, b in CALLS if (b if side == "b" else a) == key)
        rows = [[other, NODES[other][1], NODES[other][2], *NODES[other][3].split("-")]
                for other in near[args["offset"]:args["offset"] + 1]]
        return {"rows": rows, "has_more": args["offset"] + 1 < len(near)}


def _chunk(path, first, last):
    return {"chunk_id": f"{path}:{first}", "path": path, "start_line": first, "end_line": last, "parent_id": path}


CHUNKS = {chunk["chunk_id"]: chunk for chunk in (
    _chunk("src/fus.py", 1, 8), _chunk("src/fus.py", 9, 12), _chunk("src/fus.py", 13, 20), _chunk("src/ret.py", 1, 19),
    _chunk("src/ret.py", 20, 39), _chunk("src/ret.py", 40, 60), _chunk("tests/test_ret.py", 1, 9),
    _chunk("tests/test_fus.py", 1, 3))}


SOURCES = {"src/fus.py": "def helper():\n    pass\nRRF = 60\n\n\nclass Fused:\n    pass\n\n\ndef rrf(ranks):\n    return 1\n",
           "tests/test_ret.py": "def test_it():\n    pass\n\n\ndef heron():\n    pass\n"}


@pytest.fixture()
def indexed(tmp_path, monkeypatch):
    (tmp_path / codeintel.BASE_REL / "home").mkdir(parents=True)
    (tmp_path / codeintel.BASE_REL / "files").mkdir()
    for rel, text in SOURCES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    calls = []
    monkeypatch.setattr(codeintel, "_Session", lambda _root: Planted(calls))
    return tmp_path, calls


@pytest.mark.parametrize("query", ["Who calls `rrf`?", "Who calls rrf?"])
def test_a_symbol_is_asked_in_small_pages_and_its_spans_join_as_chunks(indexed, query):
    root, calls = indexed
    hits, facet = code_route.route(root, query, CHUNKS)
    assert facet == {"available": True, "reason": None}
    assert [hit["chunk_id"] for hit in hits] == ["src/fus.py:9", "src/fus.py:13", "src/fus.py:1", "src/ret.py:20",
                                                 "src/ret.py:40"]  # the definition, then its neighbours, no test
    assert {tool for tool, _ in calls} == {"search_graph", "query_graph"}
    assert all(args.get("limit", args.get("max_rows")) == code_route.PAGE <= 500 for _, args in calls)
    assert calls[0] == ("search_graph", {"project": codeintel.PROJECT, "format": "json", "limit": code_route.PAGE,
                                         "offset": 0, "name_pattern": "^(rrf)$"})  # only the word that names a symbol
    queried = [args["query"] for tool, args in calls if tool == "query_graph"]
    assert queried and all("qualified_name = 'code.src.fus.rrf'" in query for query in queried)  # that one symbol
    assert code_route.route(root, query, CHUNKS) == (hits, facet)  # the same answer twice


def test_a_question_naming_no_symbol_gives_no_route(indexed):
    root, calls = indexed
    assert code_route.route(root, "How are the RRF ranks summed?", CHUNKS) is None  # a Variable, and case differs
    assert code_route.route(root, "harbour tide almanac", CHUNKS) is None  # plain words no code file defines
    assert code_route.route(root, "Who keeps the heron?", CHUNKS) is None  # defined, but only in a test
    assert code_route.route(root, "?!", CHUNKS) is None
    assert calls == []  # the index is not asked


@pytest.mark.parametrize("query", ["Who calls fuse_scores?", "what does `rrf` do", "who uses rankItems"])
def test_a_missing_index_is_named_for_a_question_shaped_as_code(tmp_path, query):
    hits, facet = code_route.route(tmp_path, query, CHUNKS)
    assert hits == [] and facet["available"] is False and "code index is missing" in facet["reason"]


def test_a_missing_index_is_named_for_a_plain_word_a_code_file_defines(indexed):
    root, calls = indexed
    shutil.rmtree(root / codeintel.BASE_REL)
    hits, facet = code_route.route(root, "Who calls rrf?", CHUNKS)
    assert hits == [] and facet["available"] is False and "code index is missing" in facet["reason"]
    assert calls == []


def test_a_missing_index_leaves_a_plain_words_question_as_today(tmp_path):
    assert code_route.route(tmp_path, "How is the heron ledger kept?", CHUNKS) is None


def test_an_unreadable_index_is_named_never_ok(indexed, monkeypatch):
    root, calls = indexed
    monkeypatch.setattr(codeintel, "_Session", lambda _root: Planted(calls, fail=True))
    hits, facet = code_route.route(root, "Who calls fuse_scores?", CHUNKS)
    assert hits == [] and facet["available"] is False and "code index is unreadable" in facet["reason"]


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """A temporary repository, indexed and loaded: a decision record, and notes and code that hold a phrase."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (tmp_path / "dec.md").write_text("---\nid: DEC-001\ntype: decision\nstatus: ACCEPTED\n---\n# DEC-001\n\nThe pier "
                                     "is kept dry.\n", encoding="utf-8")
    (tmp_path / "note.md").write_text("# Note\n\nThe heron ledger of the pier.\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/fus.py").write_text("def fuse_scores(a):\n    return a\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return tmp_path


needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@needs_gitleaks
def test_a_question_naming_nothing_gets_todays_bundle(repo, monkeypatch):
    asked = retrieve(repo, "heron ledger", reranker=lambda: None)
    monkeypatch.setattr(graph_route, "start_ids", lambda *_args: [])
    monkeypatch.setattr(code_route, "route", lambda *_args: None)
    assert asked == retrieve(repo, "heron ledger", reranker=lambda: None)  # today's: neither new route asked
    assert set(asked["facets"]) == {"lexical", "semantic"} and asked["stopping_reason"] == "SATURATED"


@needs_gitleaks
def test_a_record_named_in_a_question_joins_through_the_closure(repo):
    bundle = retrieve(repo, "What does DEC-001 say about the pier?", reranker=lambda: None)
    assert bundle["facets"]["closure"] == {"available": True, "reason": None}
    assert any(item["id"] == "DEC-001" and "closure" in item["routes"] for item in bundle["evidence"])
    assert bundle == retrieve(repo, "What does DEC-001 say about the pier?", reranker=lambda: None)


@needs_gitleaks
def test_a_missing_index_fails_the_route_not_the_answer(repo):
    bundle = retrieve(repo, "fuse_scores", reranker=lambda: None)
    assert bundle["facets"]["code"]["available"] is False and bundle["stopping_reason"] == "FACET_UNAVAILABLE"
    assert [item["path"] for item in bundle["evidence"]] == ["src/fus.py"]  # the lexical route still answers


@needs_gitleaks
def test_a_symbol_named_in_a_question_joins_as_the_code_route(repo, monkeypatch):
    (repo / codeintel.BASE_REL / "home").mkdir(parents=True)
    (repo / codeintel.BASE_REL / "files").mkdir()
    monkeypatch.setattr(code_route, "_spans", lambda _root, words: [("src/fus.py", 1, 2)] if "fuse_scores" in words
                        else [])
    bundle = retrieve(repo, "fuse_scores", reranker=lambda: None)
    assert bundle["facets"]["code"] == {"available": True, "reason": None}
    assert [(item["path"], sorted(item["routes"])) for item in bundle["evidence"]] == [("src/fus.py",
                                                                                         ["code", "lexical"])]


# DEC-1006 (P-W2-92-1, -3, -4): the cue gate, one session per process, a missing record store named for its route.

@pytest.mark.parametrize("query", ["Which paths are embedded for semantic rrf?", "How is the rrf summed?",
                                   "Which ranks does the helper keep?"])
def test_a_plain_word_without_a_code_cue_asks_nothing(indexed, query):
    root, calls = indexed
    assert code_route.route(root, query, CHUNKS) is None and calls == []


@pytest.mark.parametrize("query, asked", [
    ("Who calls rrf?", "^(rrf)$"), ("Where is rrf defined?", "^(rrf)$"), ("Which functions reach rrf?", "^(rrf)$"),
    ("What are the callers of rrf?", "^(rrf)$"), ("Which class is Fused?", "^(Fused)$"),
    ("Does `helper` reach rrf?", "^(helper|rrf)$"), ("Does helper() reach rrf?", "^(helper|rrf)$"),
    ("Is rrf faster than fuse_scores?", "^(fuse_scores)$"),  # shaped as code without a cue: that word alone
])
def test_a_plain_word_joins_only_with_a_code_cue(indexed, query, asked):
    root, calls = indexed
    code_route.route(root, query, CHUNKS)
    assert calls[0][1]["name_pattern"] == asked


class Counted(Planted):
    """A planted session that counts its starts and its ends."""
    started, ended = [], []

    def __init__(self, calls, fail=False):
        super().__init__(calls, fail)
        Counted.started.append(self)

    def __exit__(self, *_):
        Counted.ended.append(self)


@pytest.fixture()
def counted(indexed, monkeypatch):
    root, calls = indexed
    monkeypatch.setattr(Counted, "started", []), monkeypatch.setattr(Counted, "ended", [])
    monkeypatch.setattr(codeintel, "_Session", lambda _root: Counted(calls))
    monkeypatch.setattr(code_route, "_SESSIONS", {})
    return root, calls


def test_one_session_serves_every_question_of_a_process(counted):
    root, _ = counted
    first = code_route.route(root, "Who calls rrf?", CHUNKS)
    assert code_route.route(root, "Who calls `helper`?", CHUNKS)[1]["available"] is True
    assert code_route.route(root, "Who calls rrf?", CHUNKS) == first  # the same answer from the reused session
    assert len(Counted.started) == 1 and Counted.ended == []
    code_route._end_sessions()  # at exit
    assert Counted.ended == Counted.started and code_route._SESSIONS == {}


def test_a_changed_index_or_a_failed_question_starts_another_session(counted, monkeypatch):
    root, calls = counted
    code_route.route(root, "Who calls rrf?", CHUNKS)
    (root / codeintel.BASE_REL / "home" / f"{codeintel.PROJECT}.db").write_bytes(b"rebuilt")
    code_route.route(root, "Who calls rrf?", CHUNKS)
    assert len(Counted.started) == 2 and Counted.ended == Counted.started[:1]
    monkeypatch.setattr(codeintel, "_Session", lambda _root: Counted(calls, fail=True))
    monkeypatch.setattr(code_route, "_SESSIONS", {})
    hits, facet = code_route.route(root, "Who calls rrf?", CHUNKS)
    assert hits == [] and "code index is unreadable" in facet["reason"]  # a reused session still names it
    assert Counted.ended[-1] is Counted.started[-1] and code_route._SESSIONS == {}


def _break_records(repo, sql):
    import sqlite3
    connection = sqlite3.connect(repo / ".gov-runtime/store.db")
    connection.execute(sql)
    connection.commit()
    connection.close()


@needs_gitleaks
@pytest.mark.parametrize("sql, named", [("DROP TABLE records", "the record store is missing"),
                                        ("ALTER TABLE records RENAME COLUMN status TO state",
                                         "the record store is unreadable")])
def test_a_missing_or_unreadable_record_store_is_named_and_the_other_routes_answer(repo, monkeypatch, sql, named):
    (repo / codeintel.BASE_REL / "home").mkdir(parents=True)
    (repo / codeintel.BASE_REL / "files").mkdir()
    monkeypatch.setattr(code_route, "_spans", lambda _root, words: [("src/fus.py", 1, 2)])
    _break_records(repo, sql)
    bundle = retrieve(repo, "fuse_scores and DEC-001", ids=("DEC-001",), reranker=lambda: None)
    assert bundle["facets"]["closure"]["available"] is False and named in bundle["facets"]["closure"]["reason"]
    assert bundle["facets"]["code"] == {"available": True, "reason": None} and bundle["facets"]["lexical"]["available"]
    assert bundle["stopping_reason"] == "FACET_UNAVAILABLE"
    assert [(item["path"], item["routes"]) for item in bundle["evidence"]] == [("src/fus.py", ["code"])]
    assert sorted(retrieve(repo, "fuse_scores", reranker=lambda: None)["evidence"][0]["routes"]) == ["code", "lexical"]
    assert bundle == retrieve(repo, "fuse_scores and DEC-001", ids=("DEC-001",), reranker=lambda: None)


@needs_gitleaks
def test_no_store_at_all_is_named_never_refused(repo):
    (repo / ".gov-runtime/store.db").unlink()
    bundle = retrieve(repo, "What does DEC-001 say?", reranker=lambda: None)
    assert "the record store is missing" in bundle["facets"]["closure"]["reason"] and bundle["evidence"] == []


@needs_gitleaks
def test_a_fault_that_is_not_the_stores_is_raised(repo, monkeypatch):
    import sqlite3

    from gov import records

    for fault in (sqlite3.ProgrammingError("a bad query"), TypeError("a bad argument")):
        def faulty(*_args, fault=fault, **_kwargs):
            raise fault

        monkeypatch.setattr(records, "records", faulty)
        with pytest.raises(type(fault)):
            retrieve(repo, "heron ledger", reranker=lambda: None)


@needs_gitleaks
def test_the_authority_order_is_kept_with_a_record_graph_and_skipped_without(repo, monkeypatch):
    from gov.retrieval import authority

    ordered, real = [], authority.order
    monkeypatch.setattr(authority, "order", lambda *args: ordered.append(args) or real(*args))
    retrieve(repo, "heron ledger", reranker=lambda: None)
    assert len(ordered) == 1 and ordered[0][1]  # the store's records
    _break_records(repo, "DROP TABLE records")
    retrieve(repo, "heron ledger", reranker=lambda: None)
    assert len(ordered) == 1
