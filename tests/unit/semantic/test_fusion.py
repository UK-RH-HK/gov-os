"""Builder tests for what the whole retrieval gives the reranker (W1-19; DEC-406).

Regression evidence only (DEC-136). No store, no model: the two routes and the chunk records are stand-ins. The
lexical route names 35 chunks, the semantic route is unavailable, and a chunk's text is longer than what the
reranker reads of it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import fusion  # noqa: E402

NAMES = [f"chunk-{number:02}" for number in range(35)]


def _text(name):
    return f"{name} " + "x" * 600


@pytest.fixture()
def passes(monkeypatch):
    """The stand-ins, and the texts of each pass of the scorer, which scores a text by the number in its path."""
    seen = []
    hits = [{"chunk_id": name, "path": f"notes/{name}.md", "start_line": 1, "end_line": 2, "parent_id": "p"}
            for name in NAMES]

    def score(query, texts):
        seen.append(texts)
        return [float(text.splitlines()[0][-6:-4]) for text in texts]

    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": hits})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": False, "hits": []})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": _text(hit["chunk_id"])}
                                                                 for hit in fused])
    return seen, lambda: score


def test_only_the_first_30_fused_chunks_are_scored_and_returned(passes):
    seen, reranker = passes
    answer = fusion.search(Path("unused"), "a question", limit=None, reranker=reranker)
    assert fusion.RERANK_TOP == 30 and len(seen) == 1 and len(seen[0]) == 30
    assert [hit["chunk_id"] for hit in answer["hits"]] == NAMES[29::-1]  # the reranker's order, of the first 30
    assert answer["reranked"] is True
    assert [hit["chunk_id"] for hit in fusion.search(Path("unused"), "a question", limit=2, reranker=reranker)["hits"]] \
        == ["chunk-29", "chunk-28"]
    unranked = fusion.search(Path("unused"), "a question", limit=None, reranker=lambda: None)
    assert [hit["chunk_id"] for hit in unranked["hits"]] == NAMES[:30] and unranked["reranked"] is False


def test_the_scorer_reads_the_path_and_the_first_500_characters_and_a_hit_keeps_its_own_text(passes):
    seen, reranker = passes
    answer = fusion.search(Path("unused"), "a question", limit=None, reranker=reranker)
    assert fusion.RERANK_CHARS == 500
    assert seen[0][0] == "[path: notes/chunk-00.md]\n" + _text("chunk-00")[:500]
    for hit in answer["hits"]:
        assert hit["text"] == _text(hit["chunk_id"]) and hit["path"] == f"notes/{hit['chunk_id']}.md"
