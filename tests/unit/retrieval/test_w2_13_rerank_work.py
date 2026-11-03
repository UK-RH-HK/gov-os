"""Builder tests for the fused path's work once the lexical route gives its ranked list (W2-13; DEC-725, KPI success 3).

Regression evidence only (DEC-136). The ranked route adds up to ``lexical.TOP_K`` chunks to the fusion, never to the
reranker's work: one rerank call, at most ``RERANK_TOP`` candidates, each its path and at most ``RERANK_CHARS`` of
its text (DEC-406), as before W2-13; and a question costs the lexical route two FTS5 queries at most, the exact
phrase and the words. No wall-clock assertion: the work is counted.
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

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
FILES = 90  # more chunks than both routes give together


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda _root, paths: list(paths))
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    for number in range(FILES):  # every file holds the words; some chunks are far longer than RERANK_CHARS
        body = "The lantern keeper logs the tide. " * (1 + number % 7 * 10)
        (tmp_path / "docs" / f"n{number:02}.md").write_text(f"# Note {number}\n\n{body}\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    lexical.refresh(tmp_path)
    return tmp_path


def _semantic(root):
    """A stand-in semantic route: the last ``semantic.TOP_K`` chunks, as its records."""
    hits = lexical.chunks(root)[-semantic.TOP_K:]
    return lambda *_args, **_kwargs: {"available": True, "facet": "semantic", "state": "AVAILABLE", "reason": None,
                                      "hits": hits}


def test_the_ranked_route_adds_no_rerank_work(root, monkeypatch):
    monkeypatch.setattr(semantic, "search", _semantic(root))
    calls = []

    def score(query, texts):
        calls.append(texts)
        return [0.0] * len(texts)

    lexical_answer = lexical.search(root, "lantern keeper tide", refresh=False)
    assert len([entry for entry in lexical_answer["ranked"] if not entry["exact"]]) == lexical.TOP_K
    answer = fusion.search(root, "lantern keeper tide", limit=None, refresh=False, reranker=lambda: score)
    assert len(calls) == 1 and len(calls[0]) == fusion.RERANK_TOP == len(answer["hits"])
    assert set(answer["facets"]) == {"lexical", "semantic"} and any("lexical" in hit["routes"] for hit in answer["hits"])
    for text in calls[0]:
        head, _, body = text.partition("\n")
        assert head.startswith("[path: docs/") and len(body) <= fusion.RERANK_CHARS


def test_a_question_costs_the_lexical_route_two_fts_queries_at_most(root, monkeypatch):
    lexical.search(root, "warm", refresh=False)  # the freshness of the store is worked out once per process
    statements = []
    connect = sqlite3.connect

    def traced(*args, **kwargs):
        connection = connect(*args, **kwargs)
        connection.set_trace_callback(statements.append)
        return connection

    monkeypatch.setattr(lexical.sqlite3, "connect", traced)
    for query in ("lantern keeper tide", "Which note does the lantern keeper log the tide in, and when?", "Note 7"):
        statements.clear()
        assert lexical.search(root, query, refresh=False)["available"] is True
        assert 1 <= len([sql for sql in statements if "MATCH" in sql]) <= 2, statements
