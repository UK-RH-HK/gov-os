"""W2-69 (K1): a real token is found in every form the derived stores hold it.

Success: "A real token is found at every offset and in every form the derived
stores hold it: in a stored value, in a SQLite row read as text, in UTF-16 text,
and across every boundary where the check splits or reads its input, at a word
boundary as the rule defines it [DEC-897 item 1, W2-M404]."

Failure: "A real token at a word boundary that the check misses, at any offset
or in any stored form."

This file holds the forms, one store or file per case, each holding one token
(a github-pat shape) at a word boundary: a plain file, a SQLite text value, a
value in a full-text index, a blob, UTF-16 text (a UTF-16 store, UTF-16 bytes in
a blob and in a plain file), a long value, the schema text, the freed space of
an uncompacted store, and the write-ahead log. The offsets across read edges are
in ``test_w2_69_real_token_across_read_edges.py``.

The design (DEC-897 item 1) reads each SQLite store's content as its stored
values, the schema table included, and its freed space as a backstop; a file that
is no SQLite store as its raw bytes, and also without its zero bytes. Every case
here is found by today's check too (it scans the raw bytes, the rows as text and
the bytes without zeros): these cases guard the change. The token is built at run
time; none stands whole in this file, and none may be printed.
"""

from __future__ import annotations

import codecs
import sqlite3
from pathlib import Path

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME


def _text(secret, before="before", after="after"):
    return f"{support.prose(400, before)} {secret} {support.prose(400, after)}"


def _plain(project, secret, rel=f"{R}/notes.txt"):
    support.write(project / rel, _text(secret))
    return [rel], None


def _nested(project, secret):
    rel = f"{R}/codeintel/files/src/app.py"
    support.write(project / rel, f"# a module\nVALUE = 1\nlabel = \"{secret}\"\n")
    return [rel], None


def _zero_bytes(project, secret):
    rel = f"{R}/cache/blob.bin"
    support.write(project / rel, b"\0\1\2\3" + _text(secret).encode() + b"\0\0\7")
    return [rel], None


def _utf16_plain(encoding, bom):
    def build(project, secret):
        rel = f"{R}/notes-{encoding}{'-bom' if bom else ''}.txt"
        mark = {"utf-16-le": codecs.BOM_UTF16_LE, "utf-16-be": codecs.BOM_UTF16_BE}[encoding] if bom else b""
        support.write(project / rel, mark + _text(secret).encode(encoding))
        return [rel], None
    return build


def _store(rel_name, schema, rows, **options):
    def build(project, secret):
        rel = f"{R}/{rel_name}"
        support.sqlite_store(project / rel, schema, [(sql, tuple(v(secret) if callable(v) else v for v in values))
                                                     for sql, values in rows], **options)
        return [rel], None
    return build


def _text_value(project, secret):
    return _store("store.db", ["CREATE TABLE notes (id INTEGER PRIMARY KEY, path TEXT, body TEXT)"],
                  [("INSERT INTO notes (path, body) VALUES (?, ?)", ("docs/a.md", _text))])(project, secret)


def _integer_column(project, secret):
    rels, _ = _store("typed.db", ["CREATE TABLE counts (id INTEGER PRIMARY KEY, n INTEGER)"],
                     [("INSERT INTO counts (n) VALUES (?)", (_text,))])(project, secret)
    connection = sqlite3.connect(project / rels[0])
    try:
        assert connection.execute("SELECT typeof(n) FROM counts").fetchone()[0] == "text", \
            "premise: the INTEGER column holds the value as text"
    finally:
        connection.close()
    return rels, None


def _without_rowid(project, secret):
    return _store("keyed.db", ["CREATE TABLE notes (path TEXT PRIMARY KEY, body TEXT) WITHOUT ROWID"],
                  [("INSERT INTO notes VALUES (?, ?)", ("docs/a.md", _text))])(project, secret)


def _fts(project, secret):
    return _store("lexical.db", ["CREATE VIRTUAL TABLE chunks USING fts5(path, body)"],
                  [("INSERT INTO chunks (path, body) VALUES (?, ?)", ("docs/a.md", _text))])(project, secret)


def _blob(encoding):
    def build(project, secret):
        rel = f"{R}/blob-{encoding or 'bytes'}.db"
        data = _text(secret).encode(encoding or "utf-8")
        support.blob_store(project / rel, data)
        return [rel], None
    return build


def _utf16_store(encoding):
    def build(project, secret):
        rel = f"{R}/store-{encoding}.db"
        support.sqlite_store(project / rel, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                             [("INSERT INTO notes (body) VALUES (?)", (_text(secret),))], encoding=encoding)
        assert secret.encode() not in (project / rel).read_bytes(), "premise: the store holds the text as UTF-16 only"
        return [rel], None
    return build


def _long_value(project, secret):
    """A value of 300,000 characters (longer than one gitleaks read from a pipe or a file, and than 4 KiB pages):
    the token at an offset that is no known read edge."""
    rel = f"{R}/long.db"
    body = support.prose(150_001, "long1") + " " + secret + " " + support.prose(149_000, "long2")
    support.long_value_store(project / rel, body)
    return [rel], None


def _value_alone(project, secret):
    return _store("alone.db", ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                  [("INSERT INTO notes (body) VALUES (?)", (lambda s: s,))])(project, secret)


def _value_start(project, secret):
    return _store("start.db", ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                  [("INSERT INTO notes (body) VALUES (?)", (lambda s: s + " " + support.prose(3000, "s"),))])(
        project, secret)


def _value_end(project, secret):
    return _store("end.db", ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                  [("INSERT INTO notes (body) VALUES (?)", (lambda s: support.prose(3000, "e") + " " + s,))])(
        project, secret)


def _among_many(project, secret):
    rel = f"{R}/many.db"
    values = [support.prose(120, f"v{n}") for n in range(5000)]
    values[2500] = f"value {secret} here"
    support.values_store(project / rel, values)
    return [rel], None


def _schema(kind):
    def build(project, secret):
        rel = f"{R}/schema-{kind}.db"
        statements = {
            "a-default-value": [f"CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT DEFAULT '{secret}')"],
            "a-view": ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)",
                       f"CREATE VIEW labels AS SELECT id, '{secret}' AS label FROM notes"],
            "a-trigger": ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)",
                          "CREATE TABLE seen (id INTEGER PRIMARY KEY, what TEXT)",
                          f"CREATE TRIGGER noted AFTER INSERT ON notes BEGIN INSERT INTO seen (what) VALUES "
                          f"('{secret}'); END"],
        }[kind]
        support.sqlite_store(project / rel, statements)
        connection = sqlite3.connect(project / rel)
        try:
            tables = [n for (n,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
            rows = [v for t in tables for row in connection.execute(f'SELECT * FROM "{t}"') for v in row]
        finally:
            connection.close()
        assert not any(secret in str(v) for v in rows), "premise: only the schema holds the token"
        return [rel], None
    return build


def _freed(kind, encoding=None):
    def build(project, secret):
        rel = f"{R}/freed-{kind}{'-' + encoding if encoding else ''}.db"
        path = support.freed_store(project / rel, kind, secret, encoding=encoding)
        form = secret.encode({"UTF-16le": "utf-16-le", None: "utf-8"}[encoding])
        assert form in path.read_bytes(), f"premise: the token is still in the bytes of the store ({kind})"
        assert not support.held_by_a_value(path, secret), f"premise: no live value holds the token ({kind})"
        return [rel], None
    return build


def _wal(project, secret):
    """A store in WAL mode whose row holding the token is committed in its log only (no checkpoint yet)."""
    rel = f"{R}/wal.db"
    path = project / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA wal_autocheckpoint = 0")
    connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    connection.execute("INSERT INTO notes (body) VALUES (?)", (_text(secret),))
    wal = Path(str(path) + "-wal")
    assert wal.is_file() and secret.encode() in wal.read_bytes(), "premise: the row is in the write-ahead log"
    assert secret.encode() not in path.read_bytes(), "premise: the row is not in the main file yet"
    return [rel, rel + "-wal"], connection.close


FORMS = {
    "a-plain-file": _plain,
    "a-plain-file-in-a-nested-folder": _nested,
    "a-plain-file-with-zero-bytes": _zero_bytes,
    "a-utf16le-plain-file-with-a-bom": _utf16_plain("utf-16-le", True),
    "a-utf16le-plain-file": _utf16_plain("utf-16-le", False),
    "a-utf16be-plain-file": _utf16_plain("utf-16-be", False),
    "a-text-value": _text_value,
    "a-text-value-in-an-integer-column": _integer_column,
    "a-value-of-a-table-without-rowid": _without_rowid,
    "a-value-in-a-full-text-index": _fts,
    "a-blob-of-its-bytes": _blob(None),
    "a-blob-of-utf16le-bytes": _blob("utf-16-le"),
    "a-blob-of-utf16be-bytes": _blob("utf-16-be"),
    "a-utf16le-store": _utf16_store("UTF-16le"),
    "a-utf16be-store": _utf16_store("UTF-16be"),
    "a-value-longer-than-one-gitleaks-read": _long_value,
    "a-value-that-is-only-the-token": _value_alone,
    "the-start-of-a-value": _value_start,
    "the-end-of-a-value": _value_end,
    "one-value-among-five-thousand": _among_many,
    "the-schema-a-default-value": _schema("a-default-value"),
    "the-schema-a-view": _schema("a-view"),
    "the-schema-a-trigger": _schema("a-trigger"),
    **{f"freed-space-{kind}": _freed(kind) for kind in support.FREED_KINDS},
    "freed-space-a-freeblock-of-a-utf16-store": _freed("a-freeblock", "UTF-16le"),
    "the-write-ahead-log": _wal,
}


@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_real_token_is_found_in_every_form_a_store_holds_it(sandbox, project, form):
    secret = support.ghp_token(f"every-form-{form}")
    rels, close = FORMS[form](project, secret)
    try:
        run = support.run_check(sandbox, project)
    finally:
        if close:
            close()
    assert run.returncode is not None, f"{form}: the check did not end within its declared limit\n{run.describe()}"
    assert secret not in run.stdout + run.stderr, f"{form}: the check printed the secret"
    assert run.returncode == support.FINDING_EXIT, (
        f"{form}: the store holds a real token at a word boundary and the check did not report a finding "
        f"(exit code {run.returncode}, not {support.FINDING_EXIT})\n{run.describe()}")
    assert any(run.names(rel) for rel in rels), (
        f"{form}: the check is red but names none of {rels}\n{run.describe()}")


def test_control_every_form_without_a_token_is_green(sandbox, project):
    """The same forms holding no token: none is a finding by its form alone (UTF-16, zero bytes, blobs, freed space,
    the schema, the log)."""
    clean = support.marker("nothingsecret")
    closers = []
    for form, build in sorted(FORMS.items()):
        if form.startswith("freed-space") or form.startswith("the-schema"):
            continue   # these builders assert a premise about the token's place; their clean forms are below
        _rels, close = build(project, clean)
        if close:
            closers.append(close)
    for kind in support.FREED_KINDS:
        support.freed_store(project / R / f"freed-clean-{kind}.db", kind, clean)
    support.sqlite_store(project / R / "schema-clean.db",
                         [f"CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT DEFAULT '{clean}')",
                          f"CREATE VIEW labels AS SELECT id, '{clean}' AS label FROM notes"])
    try:
        run = support.run_check(sandbox, project)
    finally:
        for close in closers:
            close()
    assert run.returncode == 0, f"the forms without a token are not green\n{run.describe()}"
