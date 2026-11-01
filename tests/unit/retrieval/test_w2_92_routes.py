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
    """The code-graph tool's search_graph and trace_path over the planted graph, one row a page, every call kept."""

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
        assert tool == "trace_path"
        key, at = args["function_name"], int(args.get("cursor") or 0)
        near = sorted([("callers", a) for a, b in CALLS if b == key] + [("callees", b) for a, b in CALLS if a == key])
        page = {"callers": {"groups": []}, "callees": {"groups": []}}
        for side, other in near[at:at + 1]:
            prefix, _, name = other.rpartition(".")
            page[side]["groups"].append({"qn_prefix": prefix, "rows": [[name, 1]]})
        more = at + 1 < len(near)
        return {**page, "has_more": more, **({"next_cursor": str(at + 1)} if more else {})}


def _chunk(path, first, last):
    return {"chunk_id": f"{path}:{first}", "path": path, "start_line": first, "end_line": last, "parent_id": path}


CHUNKS = {chunk["chunk_id"]: chunk for chunk in (
    _chunk("src/fus.py", 1, 8), _chunk("src/fus.py", 9, 12), _chunk("src/fus.py", 13, 20), _chunk("src/ret.py", 1, 19),
    _chunk("src/ret.py", 20, 39), _chunk("src/ret.py", 40, 60), _chunk("tests/test_ret.py", 1, 9),
    _chunk("tests/test_fus.py", 1, 3))}


@pytest.fixture()
def indexed(tmp_path, monkeypatch):
    (tmp_path / codeintel.BASE_REL / "home").mkdir(parents=True)
    (tmp_path / codeintel.BASE_REL / "files").mkdir()
    calls = []
    monkeypatch.setattr(codeintel, "_Session", lambda _root: Planted(calls))
    return tmp_path, calls


def test_a_symbol_is_asked_in_small_pages_and_its_spans_join_as_chunks(indexed):
    root, calls = indexed
    hits, facet = code_route.route(root, "Who calls rrf?", CHUNKS)
    assert facet == {"available": True, "reason": None}
    assert [hit["chunk_id"] for hit in hits] == ["src/fus.py:9", "src/fus.py:13", "src/fus.py:1", "src/ret.py:20",
                                                 "src/ret.py:40"]  # the definition, then its neighbours, no test
    assert {tool for tool, _ in calls} == {"search_graph", "trace_path"}  # never query_graph: no whole-graph read
    assert all(args["limit"] == code_route.PAGE <= 500 for _, args in calls)
    assert [args["function_name"] for tool, args in calls if tool == "trace_path"] == ["code.src.fus.rrf"] * 4
    assert code_route.route(root, "Who calls rrf?", CHUNKS) == (hits, facet)  # the same answer twice


def test_a_question_naming_no_symbol_gives_no_route(indexed):
    root, _ = indexed
    assert code_route.route(root, "How are the RRF ranks summed?", CHUNKS) is None  # a Variable, and case differs
    assert code_route.route(root, "?!", CHUNKS) is None


@pytest.mark.parametrize("query", ["Who calls fuse_scores?", "what does `rrf` do", "who uses rankItems"])
def test_a_missing_index_is_named_for_a_question_shaped_as_code(tmp_path, query):
    hits, facet = code_route.route(tmp_path, query, CHUNKS)
    assert hits == [] and facet["available"] is False and "code index is missing" in facet["reason"]


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
