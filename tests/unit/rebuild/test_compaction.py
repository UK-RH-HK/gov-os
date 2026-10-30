"""Builder tests for the rebuild's compaction step and the freed space the secrets check reads (W2-69, DEC-897).

Regression evidence only (MR-3). They cover what the acceptance tests leave to the builder: a deleted word leaves
neither the full-text index's rows nor the freed pages of a store the rebuild compacts, a store that cannot be
compacted is named with its reason (in the result and on standard error), a project given by a relative path has its
code-graph stores compacted, and the check's freed-space reader takes the unused tail of an overflow chain's
last page without reading the live value before it.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pytest

from gov import secrets
from gov.rebuild.command import add_arguments, run

WORD = "zebracornquill"  # an ordinary word, deleted and looked for


@pytest.fixture()
def rebuild(monkeypatch):
    """A rebuild with stand-ins for every store's build: only the compaction step works on the files."""
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: None)
    monkeypatch.setattr("gov.retrieval.semantic.refresh", lambda root: {"available": True})
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return lambda root: run(root, parser.parse_args([]), {})


def _store(root):
    path = root / ".gov-runtime" / "store.db"
    path.parent.mkdir(parents=True)
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute("PRAGMA secure_delete = OFF")
    connection.execute("CREATE TABLE rows (body TEXT)")
    connection.execute("CREATE VIRTUAL TABLE lexical_fts USING fts5(body)")
    for number in range(200):
        body = f"ordinary row {number} " * 20 + (WORD if number == 7 else "")
        connection.execute("INSERT INTO rows VALUES (?)", (body,))
        connection.execute("INSERT INTO lexical_fts VALUES (?)", (body,))
    connection.execute("DELETE FROM rows WHERE body LIKE ?", (f"%{WORD}%",))
    connection.execute("DELETE FROM lexical_fts WHERE body LIKE ?", (f"%{WORD}%",))
    connection.close()
    return path


def test_a_deleted_word_is_in_no_row_and_no_freed_byte_after_the_rebuild(tmp_path, rebuild):
    path = _store(tmp_path)
    assert WORD.encode() in path.read_bytes()  # the premise: deleting leaves it in the file
    result = rebuild(tmp_path)
    assert result["compaction"] == {".gov-runtime/store.db": "compacted"} and result["digest"] == "d"
    assert WORD.encode() not in path.read_bytes()
    connection = sqlite3.connect(path)
    assert connection.execute("PRAGMA freelist_count").fetchone() == (0,)
    connection.close()


def test_a_store_that_cannot_be_compacted_is_named_with_its_reason(tmp_path, rebuild, capsys):
    path = tmp_path / ".gov-runtime" / "store.db"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"SQLite format 3\0" + b"\x07" * 4000)
    reason = rebuild(tmp_path)["compaction"][".gov-runtime/store.db"]
    assert reason.startswith("not compacted: ")
    assert f"rebuild: .gov-runtime/store.db {reason}" in capsys.readouterr().err


def test_a_relative_root_compacts_the_code_graph_tool_s_stores(tmp_path, rebuild, monkeypatch):
    from gov.codeintel import home

    path = home(tmp_path) / "code.db"
    path.parent.mkdir(parents=True)
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE nodes (name TEXT)")
    connection.close()
    monkeypatch.chdir(tmp_path)
    assert rebuild(Path("."))["compaction"] == {".gov-runtime/codeintel/home/code.db": "compacted"}


def test_the_freed_space_holds_an_overflow_tail_and_never_the_live_value(tmp_path):
    path = tmp_path / "long.db"
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute("PRAGMA page_size = 1024")
    connection.execute("CREATE TABLE values_ (v BLOB)")
    # 3,044 bytes of payload keep 104 on the page and 2,940 in three overflow pages: 120 bytes unused on the last
    connection.execute("INSERT INTO values_ VALUES (?)", (b"\x01" * 3041,))
    connection.close()
    content = bytearray(path.read_bytes())
    last = next(at for at in range(0, len(content), 1024) if content[at:at + 5] == b"\0\0\0\0\x01")
    tail = last + 4 + content[last + 4:last + 1024].index(b"\0")
    content[tail + 10:tail + 16] = b"MARKER"
    regions = secrets._freed(bytes(content))
    assert any(b"MARKER" in region for region in regions)
    assert not any(b"\x01" * 64 in region for region in regions)
