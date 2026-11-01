"""Builder tests for the ranked lexical route (W2-13; DEC-725).

Regression evidence only (DEC-136). A plain-word question is ranked by BM25 with the id, title and body weights; an
exact identifier ranks first; the fusion takes the ranked list; no question and no store makes ``search`` raise; a
store of the code before W2-13 is stale until a refresh builds it again; a file the filter refuses enters no column.
Every index is built in a temporary git repository, with the secret filter replaced, so no test needs gitleaks.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import fusion, lexical, semantic  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
CANARY = "-".join(("canary", "osprey", "4417"))  # assembled at run time: no literal of it is in the tree
FILES = {
    ".gitignore": ".gov-runtime/\n",
    "docs/register.md": "# Register\n\n### DEC-12 — The pier\n\nThe harbour keeps one pier.\n\n"
                        "### DEC-13 — The boats\n\nBoats are counted at dawn, as DEC-12 says.\n",
    "docs/heron.md": "# Heron\n\nThe herons nest beside the old Ledger every spring.\n",
    "docs/other.md": "# Other\n\nNothing about birds here; the pool size is set by hand.\n",
    "app/pool.py": "def resize(pool_size):\n    return pool_size\n",
    "docs/ticket.md": "---\nid: TK-7\nstatus: open\n---\n# W9-4 Fix the gate\n\nThe gate sticks.\n",
    "secret.md": f"# Keys\n\nThe token is {CANARY}.\n",
}


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda _root, paths: [rel for rel in paths if rel != "secret.md"])
    _git(tmp_path, "init", "-q", "-b", "main")
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    lexical.refresh(tmp_path)
    return tmp_path


def _ranked(root, query):
    answer = lexical.search(root, query, refresh=False)
    assert answer["available"] is True, answer
    return answer


def test_a_plain_word_question_is_matched_by_its_words_with_case_and_stems(root):
    answer = _ranked(root, "Which ledger do the HERON nest by?")
    assert answer["hits"] == []  # no line holds the question as one string
    assert answer["ranked"][0]["path"] == "docs/heron.md" and answer["ranked"][0]["exact"] is False
    assert all(entry["bm25"] <= later["bm25"] for entry, later in zip(answer["ranked"], answer["ranked"][1:]))


def test_a_word_is_matched_as_a_whole_token(root):
    assert [entry["path"] for entry in _ranked(root, "hero")["ranked"]] == []


def test_the_id_column_ranks_the_entry_an_id_heads_first(root):
    answer = _ranked(root, "DEC-12")
    assert {hit["line"] for hit in answer["hits"]} == {3, 9}  # every line that holds it, CAP-11
    first = answer["ranked"][0]
    assert (first["path"], first["start_line"]) == ("docs/register.md", 3)


def test_the_frontmatter_id_and_the_heading_id_are_ids_of_the_document(root):
    for name in ("TK-7", "W9-4"):
        assert _ranked(root, f"gate {name}")["ranked"][0]["path"] == "docs/ticket.md"


def test_the_title_outweighs_the_body(root):
    ranked = _ranked(root, "pier boats")["ranked"]
    assert [entry["path"] for entry in ranked[:2]] == ["docs/register.md"] * 2


def test_an_exact_identifier_ranks_before_its_words(root):
    answer = _ranked(root, "pool_size")
    assert answer["ranked"][0]["path"] == "app/pool.py" and answer["ranked"][0]["exact"] is True
    assert {hit["path"] for hit in answer["hits"]} == {"app/pool.py"}


def test_no_question_raises(root):
    for query in ("", "   ", '"', 'a AND (b OR', "NEAR(x y)", "*", "title:x", "^gate", "a\x00b", "\ud800",
                  "OR", "- -", "DEC-12 OR NOT"):
        answer = lexical.search(root, query, refresh=False)
        assert answer["available"] is True and isinstance(answer["ranked"], list), (query, answer)


def test_an_unreadable_store_is_unavailable_and_raises_nothing(root):
    (root / STORE_REL).write_bytes(b"this is no database" * 100)
    for refresh in (False, True):
        answer = lexical.search(root, "heron", refresh=refresh)
        assert (answer["available"], answer["state"], answer["reason"]) == (False, "FACET_UNAVAILABLE", "unreadable")


def test_a_missing_store_and_a_folder_without_git_are_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))  # no repository above the folder is found
    assert lexical.search(tmp_path, "heron", refresh=False)["reason"] == "missing"
    assert lexical.search(tmp_path, "heron")["reason"] == "unreadable"


def test_a_store_of_the_code_before_is_stale_until_a_refresh_builds_it_again(root):
    before = lexical.digest(root)
    connection = sqlite3.connect(root / STORE_REL)
    connection.executescript(f"DROP TABLE lexical_fts; CREATE VIRTUAL TABLE lexical_fts USING fts5(text, tokenize = "
                             f"\"{lexical.TOKENIZE}\"); INSERT INTO lexical_fts (rowid, text) "
                             f"SELECT id, 'old' FROM lexical_chunk;")
    connection.close()
    answer = lexical.search(root, "heron", refresh=False)
    assert (answer["available"], answer["reason"]) == (False, "stale")
    assert lexical.freshness(root)["status"] == "stale"
    assert lexical.refresh(root)["digest"] == before
    assert _ranked(root, "heron")["ranked"][0]["path"] == "docs/heron.md"


def test_a_file_the_filter_refuses_enters_no_column(root):
    connection = sqlite3.connect(root / STORE_REL)
    try:
        rows = connection.execute("SELECT text, ident, title FROM lexical_fts").fetchall()
        assert not any(CANARY in column or "secret.md" in column for row in rows for column in row)
        assert connection.execute("SELECT count(*) FROM lexical_fts WHERE lexical_fts MATCH ?",
                                  ('"' + CANARY + '"',)).fetchone() == (0,)
    finally:
        connection.close()
    assert _ranked(root, "token keys")["ranked"] == []


def test_the_fusion_takes_the_ranked_lexical_list(root, monkeypatch):
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "facet": "semantic",
                                                                       "state": "AVAILABLE", "reason": None,
                                                                       "hits": []})
    answer = fusion.search(root, "herons nesting", limit=5, refresh=False, reranker=lambda: None)
    assert answer["hits"][0]["path"] == "docs/heron.md" and answer["hits"][0]["routes"] == ["lexical"]
    assert "ranked" not in answer["facets"]["lexical"] and "hits" not in answer["facets"]["lexical"]
