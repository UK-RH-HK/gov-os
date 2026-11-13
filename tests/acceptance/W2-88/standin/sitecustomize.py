"""A stand-in for the engineer's store layout (I5, I6), used only to show that S10's cases bite. It is not the product's code and
is never imported by a case: a child process loads it as ``sitecustomize`` when ``W2_88_STANDIN`` names this folder (the
suite's ``w2_88_support.env`` then puts it first on the child's PYTHONPATH). Modes (``W2_88_STANDIN_MODE``):

``good``: behaves as I5/I6 state. ``gov.store.layout`` exists (``LAYOUT_VERSION = 2``, ``STORES``, ``STAMP_TABLE``, ``stamp``,
``version_of``, ``check``); ``loader.load`` stamps; ``loader.connect`` checks after its STORE_MISSING check (an older or newer
stamp, or an unstamped store missing a column a table of STORES names, is ``STORE_LAYOUT_STALE`` with found and expected;
an unstamped store with complete tables is current); ``gov rebuild`` replaces a stale store and reports
``layout: {found, expected, rebuilt: true}`` and ``digests``.
``never-stale``: the same, except ``check`` never refuses (a store of another layout is read as current).
``wrong-found``: the refusal's details say ``found`` is always 1 (the versions are not both named truthfully).
"""

import hashlib
import json
import os
import sqlite3
import sys
import types
from pathlib import Path

MODE = os.environ.get("W2_88_STANDIN_MODE", "good")
VERSION = 2


def _install():
    from gov.cli.errors import GovError
    from gov.store import loader
    import gov.store as store_package
    import gov.rebuild.command as rebuild

    layout = types.ModuleType("gov.store.layout")
    layout.LAYOUT_VERSION = VERSION
    layout.STAMP_TABLE = "store_layout"
    layout.STORES = {
        "record": {"file": ".gov-runtime/store.db",
                   "tables": {"register_entries": ("id", "heading", "title", "span", "content_hash"),
                              "records": ("path", "id", "type", "status")}},
        "lexical": {"file": ".gov-runtime/store.db", "tables": ("lexical_chunks",)},
        "vectors": {"file": ".gov-runtime/store.db", "tables": ("semantic_chunks",)},
        "codegraph": {"file": ".gov-runtime/codeintel/", "tables": ()},
    }

    def stamp(conn):
        conn.execute("CREATE TABLE IF NOT EXISTS store_layout (version INTEGER NOT NULL)")
        conn.execute("DELETE FROM store_layout")
        conn.execute("INSERT INTO store_layout VALUES (?)", (VERSION,))
        conn.commit()

    def version_of(conn):
        try:
            row = conn.execute("SELECT version FROM store_layout").fetchone()
        except sqlite3.Error:
            return None
        return row[0] if row else None

    def found_of(conn):
        """The layout version the store stands at: its stamp, 0 for an unstamped store missing a column, else current."""
        stamped = version_of(conn)
        if stamped is not None:
            return stamped
        for table, columns in layout.STORES["record"]["tables"].items():
            have = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            if have and any(column not in have for column in columns):
                return 0
        return VERSION

    def check(conn, path):
        found = found_of(conn)
        if found != VERSION and MODE != "never-stale":
            shown = 1 if MODE == "wrong-found" else found
            raise GovError("STORE_LAYOUT_STALE", f"{path}: store layout {shown}, this gov reads {VERSION}; run gov rebuild",
                           {"found": shown, "expected": VERSION})

    layout.stamp, layout.version_of, layout.check, layout.found_of = stamp, version_of, check, found_of
    sys.modules["gov.store.layout"] = layout
    store_package.layout = layout

    connect, load = loader.connect, loader.load

    def checked_connect(root):
        conn = connect(root)
        try:
            check(conn, str(Path(root) / loader.STORE_REL))
        except GovError:
            conn.close()
            raise
        return conn

    def stamped_load(root):
        result = load(root)
        conn = sqlite3.connect(Path(root) / loader.STORE_REL)
        stamp(conn)
        conn.close()
        return result

    loader.connect, loader.load = checked_connect, stamped_load
    store_package.connect, store_package.load = checked_connect, stamped_load

    run = rebuild.run

    def replacing_run(root, args, config):
        sys.stderr.write("standin: rebuild.run called\n")
        found = None
        db = Path(root) / loader.STORE_REL
        if db.is_file():
            conn = sqlite3.connect(db)
            try:
                found = found_of(conn)
            finally:
                conn.close()
            if found != VERSION:
                db.unlink()
        result = run(root, args, config)
        if found is not None and found != VERSION:
            result["layout"] = {"found": found, "expected": VERSION, "rebuilt": True}
        conn = sqlite3.connect(db)
        try:
            def rows(prefix):
                names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
                                                    (prefix + "%",))]
                return hashlib.sha256(json.dumps([[n, sorted(map(str, conn.execute(f"SELECT * FROM {n}").fetchall()))]
                                                  for n in sorted(names)]).encode()).hexdigest()
            result["digests"] = {"record": result.get("digest"), "lexical": rows("lexical"), "vectors": rows("semantic"),
                                 "codegraph_bytes": 0}
        finally:
            conn.close()
        return result

    rebuild.run = replacing_run


try:
    _install()
except Exception as exc:  # noqa: BLE001: a stand-in that cannot load says so on stderr and the case fails on that
    sys.stderr.write(f"standin: not installed: {exc!r}\n")
