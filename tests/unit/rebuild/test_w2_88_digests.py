"""W2-88 S4, F3: the rebuild's four digests, and a stale layout replaced and said so (stand-ins for the other stores)."""
from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess

import pytest

from gov.rebuild.command import add_arguments, run
from gov.store import STORE_REL, connect, layout

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t"}
EMBEDDED = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded"}}}}


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True, capture_output=True, env=ENV)
    (root / "a.md").write_text("---\nid: R-1\ntype: note\nstatus: ACTIVE\n---\n\nbody\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True, env=ENV)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "one"], check=True, capture_output=True, env=ENV)

    def lexical(where):
        db = sqlite3.connect(where / STORE_REL)
        db.execute("CREATE TABLE IF NOT EXISTS lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, "
                   "indexed INTEGER NOT NULL)")
        db.execute("INSERT OR REPLACE INTO lexical_file VALUES ('a.md', 'b1', 1)")
        db.commit()
        db.close()
        return {"digest": "x", "indexed": 1}

    monkeypatch.setattr("gov.retrieval.lexical.refresh", lexical)
    monkeypatch.setattr("gov.retrieval.semantic.refresh", lambda where: {"available": True})
    monkeypatch.setattr("gov.codeintel.index", lambda where: None)
    return root


def test_the_result_holds_four_digests_the_first_as_the_record_graphs(repo):
    result = run(repo, _args(), EMBEDDED)
    digests = result["digests"]
    assert set(digests) == {"record", "lexical", "vectors", "codegraph_bytes"}
    assert digests["record"] == result["digest"]
    assert all(len(digests[key]) == 64 for key in ("record", "lexical", "vectors"))
    assert isinstance(digests["codegraph_bytes"], int)


def test_two_runs_on_one_commit_give_equal_digests_for_the_three_stores(repo):
    first, second = run(repo, _args(), EMBEDDED)["digests"], run(repo, _args(), EMBEDDED)["digests"]
    for key in ("record", "lexical", "vectors"):
        assert first[key] == second[key]


@pytest.mark.parametrize("version", [None, 1, 3], ids=["unstamped", "older", "newer"])
def test_a_store_of_another_layout_is_replaced_and_said_so(repo, version):
    (repo / ".gov-runtime").mkdir()
    db = sqlite3.connect(repo / STORE_REL)
    db.execute("CREATE TABLE register_entries (id TEXT PRIMARY KEY, heading TEXT, title TEXT, content_hash TEXT)")
    if version is not None:
        db.execute("CREATE TABLE store_layout (version INTEGER NOT NULL)")
        db.execute("INSERT INTO store_layout VALUES (?)", (version,))
    db.commit()
    db.close()
    result = run(repo, _args(), EMBEDDED)
    expected = 0 if version is None else version
    if version is not None:  # a stamped store is stale by its stamp alone: its tables may be whole
        pass
    assert result["layout"] == {"found": expected, "expected": layout.LAYOUT_VERSION, "rebuilt": True}
    connect(repo).close()  # now current


def test_a_current_store_is_not_replaced(repo):
    run(repo, _args(), EMBEDDED)
    assert "layout" not in run(repo, _args(), EMBEDDED)
