"""Builder tests for what the secrets check reads of a store (W2-69, DEC-897).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: an FTS5 index's leaf
pages are read as their terms, each whole, so no term's tail after a shared prefix is read as if a text began there;
a blank line of the text no longer ends one of gitleaks' reads; a key block of up to 24 KiB in a long text is also a
piece whole (DEC-909); and a store judged by its bytes because it could not
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


def _block(size):
    """A key-shaped block of ``size`` bytes, its markers built from parts, with a blank line after its header."""
    begin, end = "-" * 5 + "BEGIN PGP PRIVATE KEY BLOCK" + "-" * 5, "-" * 5 + "END PGP PRIVATE KEY BLOCK" + "-" * 5
    head = f"{begin}\nVersion: x\n\n".encode()
    body = size - len(head) - len(end) - 1
    return head + (b"A" * 63 + b"\n") * (body // 64) + b"A" * (body % 64) + b"\n" + end.encode()


def test_a_key_block_of_up_to_24_kib_is_also_a_piece_whole_and_a_larger_or_open_one_is_not():
    text = b"word " * 9000
    for size in (9_300, secrets._BLOCK):
        pieces = list(secrets._pieces(text + b"x" + _block(size) + b"y " + text))
        whole = [piece for piece in pieces if piece.startswith(b"-" * 5 + b"BEGIN")]
        assert len(whole) == 1 and len(whole[0]) == size + 1 and whole[0].endswith(b"-")  # a form feed in the blank line
        assert b"\n\n" not in whole[0]
    begins = lambda chunk: [piece for piece in secrets._pieces(chunk) if piece.startswith(b"-" * 5 + b"BEGIN")]  # noqa: E731
    assert begins(text + _block(secrets._BLOCK + 1) + text) == []
    assert begins(text + _block(10_000).rsplit(b"\n", 1)[0] + text) == []  # a BEGIN marker with no END
    assert len(begins(_block(10_000))) == 1  # one piece holds it whole, and no other is added


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
