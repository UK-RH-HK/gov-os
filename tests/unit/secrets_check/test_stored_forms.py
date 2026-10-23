"""Builder tests for what the secrets check reads of a store (W2-69, DEC-897).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: an FTS5 index's leaf
pages are read as their terms, each whole, so no term's tail after a shared prefix is read as if a text began there;
a blank line of the text no longer ends one of gitleaks' reads; and a store judged by its bytes because it could not
be read leaves no clean result to reuse.
No secret stands whole in this file: the identifiers are built from parts.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import secrets  # noqa: E402

TOKENIZE = "porter unicode61 tokenchars '_'"  # the lexical index's tokenizer
TAIL = "".join(["sk", "_", "1"]) + "abcdefghijklmnopqrstu"


def _index(path):
    connection = sqlite3.connect(path)
    connection.execute(f"CREATE VIRTUAL TABLE lexical_fts USING fts5(text, tokenize = \"{TOKENIZE}\")")
    words = [f"headword{TAIL}{number}" for number in range(300)] + ["plain"]
    for at in range(0, len(words), 7):
        connection.execute("INSERT INTO lexical_fts(text) VALUES (?)", (" ".join(words[at:at + 7]),))
    connection.commit()
    connection.close()
    return words


def test_an_fts5_index_is_read_as_its_terms_each_whole(tmp_path):
    words = _index(tmp_path / "store.db")
    connection = sqlite3.connect(tmp_path / "store.db")
    terms = [term for rowid, block in connection.execute("SELECT id, block FROM lexical_fts_data")
             for term in secrets._fts_terms(rowid, block) or []]
    connection.close()
    assert sorted(term.decode() for term in terms) == sorted(words)
    _content, chunks, kept = secrets._store(tmp_path / "store.db")
    assert kept and not any(chunk.startswith(TAIL[:4].encode()) for chunk in chunks)


def test_a_block_that_is_no_leaf_page_is_read_by_its_bytes():
    assert secrets._fts_terms(10, b"\x00\x00\x01") is None  # the structure record
    assert secrets._fts_terms((1 << 37) | (1 << 36) | 1, b"\x00\x04\x00\x04") is None  # a doclist index page
    assert secrets._fts_terms((1 << 37) | 1, b"\x00\x00\x00\x02") is None  # a leaf that does not parse


def test_a_blank_line_no_longer_ends_a_read_and_the_pieces_cover_a_long_block():
    text = b"head\n\n" + b"word " * 6000 + b"\n \n\ntail"
    pieces = list(secrets._pieces(text))
    assert all(b"\n\n" not in piece and b"\n \n" not in piece for piece in pieces)
    assert all(len(piece) <= secrets._PIECE + 2 for piece in pieces) and secrets._OVERLAP >= 8_192


def test_a_store_that_cannot_be_read_leaves_no_clean_result(tmp_path, monkeypatch):
    path = tmp_path / "store.db"
    _index(path)
    monkeypatch.setattr(secrets, "_BUSY_S", 0.1)
    holder = sqlite3.connect(path, isolation_level=None)
    holder.execute("BEGIN EXCLUSIVE")
    try:
        _content, chunks, kept = secrets._store(path)
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert not kept and chunks
