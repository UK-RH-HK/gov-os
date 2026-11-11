"""Builder tests for S6 of W2-92 (DEC-1065 (4)): the record route reads the frontmatter titles the store kept at the
load, never parsing every record's file in each process; a store built before the titles table is read file by file
as before, with the C loader where PyYAML has it. The answers are the same both ways.

Regression evidence only (DEC-136). Each case builds its store in a temporary repository from scratch; no embedder,
no reranker, no model.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.rebuild import seed  # noqa: E402
from gov.records import queries  # noqa: E402
from gov.retrieval import graph_route  # noqa: E402
from gov.store import loader  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
FILES = {
    "docs/contract/CAP-12.md": "---\nid: CAP-12\ntype: capability\nstatus: ACTIVE\ntitle: Code intelligence\n---\n",
    "docs/contract/CAP-13.md": "---\nid: CAP-13\ntype: capability\nstatus: ACTIVE\ntitle: 13\n---\n",  # no string
    "docs/contract/CAP-14.md": "---\nid: CAP-14\ntype: capability\nstatus: ACTIVE\n---\n",  # no title
    ".tickets/DAEO-n0wb.md": "---\nid: DAEO-n0wb\ntype: task\nstatus: open\nexternal-ref: W2-92\n"
                             "title: 'The knowledge graph as a route'\n---\n# x\n",
    REGISTER: "# Register\n\n### DEC-020: The harbour rule\n**Status:** ACCEPTED\n\nText.\n",
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
}
QUESTIONS = [
    ("what does code   intelligence answer?", ["CAP-12"]),
    ("what about intelligence?", []),
    ("what did the harbour rule decide?", ["DEC-020"]),
    ("is the knowledge graph as a route done, and W2-92?", ["DAEO-n0wb"]),
    ("what does 13 mean?", []),  # a title that is no string is no title
    ("How does the lexical route rank chunks?", []),
]


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid", *args],
                   check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    store.load(tmp_path)
    return tmp_path


def _sql(root: Path, sql: str) -> list[tuple]:
    connection = sqlite3.connect(root / store.STORE_REL)
    try:
        rows = connection.execute(sql).fetchall()
        connection.commit()
        return rows
    finally:
        connection.close()


def test_the_load_keeps_each_record_files_string_title(repo):
    assert sorted(_sql(repo, f"SELECT path, id, title FROM {loader.TITLES_TABLE}")) == [
        (".tickets/DAEO-n0wb.md", "DAEO-n0wb", "The knowledge graph as a route"),
        ("docs/contract/CAP-12.md", "CAP-12", "Code intelligence")]


def test_the_titles_leave_the_digest_and_the_joined_query_as_they_were(repo):
    before = store.digest(repo)
    _sql(repo, f"DELETE FROM {loader.TITLES_TABLE}")
    assert store.digest(repo) == before
    _sql(repo, f"DROP TABLE {loader.TITLES_TABLE}")
    assert store.digest(repo) == before
    by_id = {record["id"]: record for record in queries.records(repo)}
    assert by_id["DEC-020"]["title"] == "The harbour rule" and "title" not in by_id["CAP-12"]


def test_the_titles_table_is_part_of_the_schema_version(monkeypatch):
    assert loader.TITLES_TABLE in json.dumps(loader._TABLES)
    now = seed.schema_version()
    monkeypatch.delitem(loader._TABLES, loader.TITLES_TABLE)
    assert seed.schema_version() != now  # a warm base recorded without the table is refused


@pytest.mark.parametrize("query, expected", QUESTIONS)
def test_the_route_reads_the_stores_titles_and_parses_no_file(repo, monkeypatch, query, expected):
    monkeypatch.setattr(graph_route, "_parsed", lambda *_: pytest.fail("a record's file was parsed"))
    assert graph_route.start_ids(repo, query, queries.records(repo)) == expected


@pytest.mark.parametrize("query, expected", QUESTIONS)
def test_a_store_without_the_titles_table_reads_the_files_with_the_same_answers(repo, monkeypatch, query, expected):
    known = queries.records(repo)
    _sql(repo, f"DROP TABLE {loader.TITLES_TABLE}")
    monkeypatch.setattr(graph_route, "_FRONTS", {})
    parsed = []
    real = graph_route._parsed
    monkeypatch.setattr(graph_route, "_parsed", lambda root, path: parsed.append(path) or real(root, path))
    assert graph_route.start_ids(repo, query, known) == expected
    assert "docs/contract/CAP-12.md" in parsed


def test_the_titles_are_the_commits_not_the_working_trees(repo):
    known = queries.records(repo)
    (repo / "docs/contract/CAP-12.md").write_text(
        "---\nid: CAP-12\ntype: capability\nstatus: ACTIVE\ntitle: Harbour charts\n---\n", encoding="utf-8")
    assert graph_route.start_ids(repo, "code intelligence", known) == ["CAP-12"]  # the store's, from HEAD
    assert graph_route.start_ids(repo, "harbour charts", known) == []


SPEC = "specs/SPEC-0092.md"
SPEC_TEXT = ("---\nid: SPEC-0092\ntype: spec\nstatus: ACTIVE\ntitle: Cormorant Nesting Protocol\n---\n# Spec\n\n"
             "The birds nest on the east jetty.\n")


@pytest.fixture()
def indexed(tmp_path, monkeypatch):
    """A repository indexed and loaded whose record's title the working file then changes; no embedder (a stand-in)."""
    import shutil

    from gov.retrieval import lexical, semantic

    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH")
    _git(tmp_path, "init", "-q")
    (tmp_path / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (tmp_path / "specs").mkdir()
    (tmp_path / SPEC).write_text(SPEC_TEXT, encoding="utf-8")
    (tmp_path / "note.md").write_text("# Note\n\nThe heron ledger of the pier.\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    (tmp_path / SPEC).write_text(SPEC_TEXT.replace("Cormorant Nesting Protocol", "Heron Roosting Rules"),
                                 encoding="utf-8")
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(graph_route, "_parsed", lambda *_: pytest.fail("a record's file was parsed"))
    return tmp_path


def _closure_ids(root: Path, query: str) -> list[str]:
    from gov.retrieval.retrieve import retrieve

    bundle = retrieve(root, query, reranker=lambda: None)
    return sorted({item["id"] for item in bundle["evidence"] if "closure" in item["routes"]})


def test_a_title_changed_in_the_working_file_is_matched_as_the_store_holds_it(indexed):
    from gov.retrieval import lexical

    lexical.refresh(indexed)  # the working file's text indexed again; the record store still holds the old title
    assert _closure_ids(indexed, "What does the Cormorant Nesting Protocol say?") == ["SPEC-0092"]
    assert _closure_ids(indexed, "What do the Heron Roosting Rules say?") == []


def test_a_working_file_changed_after_the_index_leaves_no_chunk_to_cite(indexed):
    """The record route still finds the record by the store's title; the bundle has no chunk to cite for it, as the
    lexical index is stale (DEC-342: ``retrieve`` takes no chunk from a stale index), which S6 does not change."""
    from gov.records import queries as records
    from gov.retrieval import lexical

    query = "What does the Cormorant Nesting Protocol say?"
    assert graph_route.start_ids(indexed, query, records.records(indexed)) == ["SPEC-0092"]
    assert lexical.search(indexed, query, refresh=False)["reason"] == "stale"
    assert _closure_ids(indexed, query) == []


def test_no_store_reads_the_files(tmp_path):
    (tmp_path / "docs/contract").mkdir(parents=True)
    (tmp_path / "docs/contract/CAP-12.md").write_text("---\nid: CAP-12\ntitle: Code intelligence\n---\n",
                                                       encoding="utf-8")
    known = [{"id": "CAP-12", "type": "capability", "status": "ACTIVE", "path": "docs/contract/CAP-12.md"}]
    assert graph_route.start_ids(tmp_path, "code intelligence", known) == ["CAP-12"]


def test_the_files_are_parsed_with_the_c_loader_where_pyyaml_has_it():
    assert graph_route._LOADER is getattr(yaml, "CSafeLoader", yaml.SafeLoader)
