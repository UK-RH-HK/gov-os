"""Builder tests for the boost of an id the question holds among other words (W2-13; DEC-725, KPI success 1).

Regression evidence only (DEC-136). A question that holds an id among other words ranks the chunks that hold that id
verbatim, as a whole token, first and marks them ``exact``, ahead of noise that mentions its parts or its other words
more often; ``hits`` stays the lines that hold the whole question; a question without an id ranks as before; and the
boost costs no FTS5 query more. Every index is built in a temporary git repository, with the secret filter replaced.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import lexical  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
NOISE = "The gauge reading of the QX line was 4471 at noon; every gauge reading is logged. " * 6
FILES = {
    ".gitignore": ".gov-runtime/\n",
    "ids/a-noise.md": f"# Gauge log\n\n{NOISE}\n",
    "ids/b-noise.md": f"# Gauge readings\n\nqx-4471 and QX-44710 and QX-4471-b: gauge reading, gauge reading.\n\n{NOISE}\n",
    "ids/z-holder.md": "# Holder\n\nThe valve QX-4471 sits behind the pump.\n",
    "manual/manual.md": "# Manual\n\nRead the gauge before the shift.\n",
    "dial/line.md": "# Dial\n\nNote QX-9 dial reading at dawn.\n",
    "dial/other.md": "# Other dial\n\nQX-9 is the second valve.\n",
}


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda _root, paths: list(paths))
    _git(tmp_path, "init", "-q", "-b", "main")
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    lexical.refresh(tmp_path)
    return tmp_path


def _answer(root, query):
    answer = lexical.search(root, query, refresh=False)
    assert answer["available"] is True, answer
    return answer


def _ordered(ranked):
    """Every exact chunk above every other, and each chunk once."""
    flags = [entry["exact"] for entry in ranked]
    assert flags == sorted(flags, reverse=True), flags
    assert len({entry["chunk_id"] for entry in ranked}) == len(ranked)


def test_the_holder_of_an_id_among_other_words_ranks_first(root):
    answer = _answer(root, "QX-4471 gauge reading")
    ranked = answer["ranked"]
    assert answer["hits"] == []  # no line holds the whole question
    assert ranked[0]["path"] == "ids/z-holder.md" and ranked[0]["exact"] is True, [e["path"] for e in ranked]
    assert [entry["path"] for entry in ranked if entry["exact"]] == ["ids/z-holder.md"]  # whole token, case and all
    assert {"ids/a-noise.md", "ids/b-noise.md"} <= {entry["path"] for entry in ranked if not entry["exact"]}
    _ordered(ranked)


def test_the_id_alone_ranks_its_holder_first_as_before(root):
    answer = _answer(root, "QX-4471")
    assert answer["ranked"][0]["path"] == "ids/z-holder.md" and answer["ranked"][0]["exact"] is True
    assert {hit["path"] for hit in answer["hits"]} == {"ids/z-holder.md", "ids/b-noise.md"}  # the exact string's lines
    _ordered(answer["ranked"])


def test_a_chunk_that_holds_the_whole_question_stays_boosted(root):
    answer = _answer(root, "QX-9 dial reading")
    assert [(hit["path"], hit["line"]) for hit in answer["hits"]] == [("dial/line.md", 3)]
    exact = {entry["path"] for entry in answer["ranked"] if entry["exact"]}
    assert exact == {"dial/line.md", "dial/other.md"} and answer["ranked"][0]["exact"] is True
    _ordered(answer["ranked"])


def test_a_question_without_an_id_is_not_boosted(root):
    answer = _answer(root, "gauge reading noon")
    assert answer["hits"] == [] and not any(entry["exact"] for entry in answer["ranked"])
    assert answer["ranked"][0]["path"] in ("ids/a-noise.md", "ids/b-noise.md")


def test_the_boost_costs_no_more_fts_queries(root, monkeypatch):
    lexical.search(root, "warm", refresh=False)  # the freshness of the store is worked out once per process
    statements = []
    connect = sqlite3.connect

    def traced(*args, **kwargs):
        connection = connect(*args, **kwargs)
        connection.set_trace_callback(statements.append)
        return connection

    monkeypatch.setattr(lexical.sqlite3, "connect", traced)
    for query in ("QX-4471 gauge reading", "QX-4471 and QX-9 by the gauge", "QX-4471"):
        statements.clear()
        assert _answer(root, query)["ranked"]
        assert 1 <= len([sql for sql in statements if "MATCH" in sql]) <= 2, statements
