"""SQLite tables the code route owns (ARCHITECTURE.md section 4.6): ``code_blob`` (one row per parsed blob, the
per-blob parse cache -- "cached by blob, so unchanged files are parsed once"), ``code_symbol``, ``code_call_site``
and ``code_literal``. Added to the same ``store.db`` govbridge.core opens (``govbridge.core.store.open_db``); this
module never computes the store path itself (BR-DAG-AMEND-1 -- every module goes through
``govbridge.core.store.store_root()``, which is what lets parallel builders use their own store via
``GOVBRIDGE_STORE`` without colliding).

Resolution (the ``resolution`` table ARCHITECTURE.md section 4.6 names) is deliberately **not** persisted here: a
call site's label depends on which *other* blobs are present in the commit being queried (a name unique in one
commit's tree can become ambiguous in another), so caching it keyed only by call site would silently go stale
across commits. ``govbridge.code.resolve`` recomputes it, cheaply, in memory, from the rows below, every query
(SO-12 measured this at ~0.1 s for the whole corpus) -- see resolve.py's module docstring.

``code_blob.eager`` (BR-AR-0014/BR-HO-0014): 0 by default -- set only by ``govbridge.code.build.code_layer_builder``,
for exactly the blobs reachable, right now, at the canonical view's eager (non-``history``) refs. A blob a query
lazily parses through ``govbridge.code.symbols.ensure_indexed`` (``stats``/``callers``/``reads-key``/
``history diff``, or a ``callers --commit <history commit>``) is inserted with ``eager`` at its schema default and
is never flipped by anything other than the eager builder -- see ``govbridge.code.build``'s module docstring for
why this makes the build-manifest ``code`` digest query-invariant.

``code_excluded_blob`` (BR-AR-0014 follow-up 1): one row per ``.rs`` blob ``govbridge.code.symbols.ensure_indexed``
classified through ``govbridge.core.corpus.classify_entry`` as anything OTHER than ``INCLUDE`` (SECURITY_POLICY
content exclusions -- ARCHITECTURE.md section 1.1/14 item 2 -- and any other corpus-rules.yaml effect: EXCLUDE,
METADATA_ONLY, LEXICAL_ONLY, NO_DEFAULT_RETRIEVAL are all "not code-indexable", generically, never only EXCLUDE by
name). Such a blob is NEVER parsed and NEVER gets a ``code_blob``/``code_symbol``/``code_call_site``/``code_literal``
row -- its exclusion is instead recorded here, with the rule id that decided it, so a query discloses the gap
explicitly (``govbridge.code.symbols.stats``'s ``files_excluded``) rather than the blob simply looking unindexed.
Consulting this table is how ``ensure_indexed`` recognises an already-classified-excluded blob on a later call
without reclassifying it (BR-AR-0014/BR-HO-0014's own "cached by blob" discipline, extended to the exclusion
verdict) -- see ``ensure_indexed``'s own module docstring.

Migration (BR-AR-0014 follow-up 2): ``code_blob.eager`` was added, in place, to an EXISTING table by an earlier
BR-AR-0014 commit. ``CREATE TABLE IF NOT EXISTS`` is a no-op against a store whose ``code_blob`` table already
exists WITHOUT that column (for example the demonstration store, ``store-BR-AR-0010``, built before this repair) --
it does not retrofit a column. ``ensure_schema()`` therefore runs a small, idempotent, data-driven migration
(``_MIGRATIONS``/``_add_column_if_missing``) after the schema script, and only then creates the ``eager`` index
(which would otherwise fail with "no such column" against an unmigrated table).
"""
from __future__ import annotations

import hashlib
import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS code_blob (
    blob_id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    language TEXT NOT NULL,
    adapter_id TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    grammar_version TEXT NOT NULL,
    ok_parse INTEGER NOT NULL,
    error_count INTEGER NOT NULL,
    eager INTEGER NOT NULL DEFAULT 0
);
-- the `eager` column's index is created by ensure_schema(), AFTER the migration step below -- see this module's
-- own docstring ("Migration") for why it cannot live in this script.

CREATE TABLE IF NOT EXISTS code_excluded_blob (
    blob_id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    effect TEXT NOT NULL,
    eager INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS code_excluded_blob_by_rule ON code_excluded_blob(rule_id);
CREATE INDEX IF NOT EXISTS code_excluded_blob_by_eager ON code_excluded_blob(eager);

CREATE TABLE IF NOT EXISTS code_symbol (
    symbol_id TEXT PRIMARY KEY,
    blob_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    module_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    is_test INTEGER NOT NULL,
    derivation TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS code_symbol_by_blob ON code_symbol(blob_id);
CREATE INDEX IF NOT EXISTS code_symbol_by_name ON code_symbol(name);
CREATE INDEX IF NOT EXISTS code_symbol_by_qualname ON code_symbol(qualified_name);

CREATE TABLE IF NOT EXISTS code_call_site (
    call_site_id TEXT PRIMARY KEY,
    blob_id TEXT NOT NULL,
    path TEXT NOT NULL,
    line INTEGER NOT NULL,
    caller_symbol TEXT,
    callee_text TEXT NOT NULL,
    callee_name TEXT NOT NULL,
    call_kind TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS code_call_site_by_blob ON code_call_site(blob_id);
CREATE INDEX IF NOT EXISTS code_call_site_by_name ON code_call_site(callee_name);

CREATE TABLE IF NOT EXISTS code_literal (
    blob_id TEXT NOT NULL,
    path TEXT NOT NULL,
    line INTEGER NOT NULL,
    enclosing_symbol TEXT,
    value TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS code_literal_by_blob ON code_literal(blob_id);
CREATE INDEX IF NOT EXISTS code_literal_by_value ON code_literal(value);

CREATE TABLE IF NOT EXISTS code_parse_error (
    blob_id TEXT NOT NULL,
    path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    start_col INTEGER NOT NULL,
    end_col INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS code_parse_error_by_blob ON code_parse_error(blob_id);
"""


#: (table, column, declaration) -- every idempotent in-place migration ensure_schema() applies, data-driven so a
#: future column addition never needs a new function, only a new entry here (BR-AR-0014 follow-up 2).
_MIGRATIONS = [
    ("code_blob", "eager", "INTEGER NOT NULL DEFAULT 0"),
]


def _add_column_if_missing(conn: sqlite3.Connection, table: str, column: str, decl_sql: str) -> None:
    """``ALTER TABLE ... ADD COLUMN`` only when ``column`` is actually missing from ``table`` -- idempotent:
    running this twice (or against a store that already has the column, including every FRESH store, whose
    ``CREATE TABLE`` already declares it) is a no-op the second time. ``PRAGMA table_info`` never errors against a
    table that does not exist yet either (empty result), so this is always safe to call right after the schema
    script, which guarantees the table itself exists by then."""
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl_sql}")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    for table, column, decl in _MIGRATIONS:
        _add_column_if_missing(conn, table, column, decl)
    conn.execute("CREATE INDEX IF NOT EXISTS code_blob_by_eager ON code_blob(eager)")
    conn.commit()


def has_blob(conn: sqlite3.Connection, blob_id: str) -> bool:
    return conn.execute("SELECT 1 FROM code_blob WHERE blob_id=?", (blob_id,)).fetchone() is not None


def symbol_id(blob_id: str, kind: str, qualified_name: str, start_line: int) -> str:
    """symbol_id = sha256(blob_id || kind || qualified_name || start_line)[:24] (ARCHITECTURE.md section 2)."""
    h = hashlib.sha256()
    for part in (blob_id, kind, qualified_name, str(start_line)):
        h.update(part.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()[:24]


def call_site_id(blob_id: str, line: int, callee_text: str, ordinal: int) -> str:
    """A stable id for one call site within a blob: the parse is deterministic, so (blob, line, callee text,
    occurrence-on-that-line) is enough to identify it without needing a global counter."""
    h = hashlib.sha256()
    for part in (blob_id, str(line), callee_text, str(ordinal)):
        h.update(part.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()[:24]


def put_blob(conn: sqlite3.Connection, blob_id: str, path: str, language: str, adapter_id: str,
             adapter_version: str, grammar_version: str, ok_parse: bool, error_count: int) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO code_blob(blob_id,path,language,adapter_id,adapter_version,grammar_version,"
        "ok_parse,error_count) VALUES (?,?,?,?,?,?,?,?)",
        (blob_id, path, language, adapter_id, adapter_version, grammar_version, 1 if ok_parse else 0, error_count),
    )


def put_symbol(conn: sqlite3.Connection, sid: str, blob_id: str, kind: str, name: str, qualified_name: str,
               module_path: str, start_line: int, end_line: int, is_test: bool, derivation: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO code_symbol(symbol_id,blob_id,kind,name,qualified_name,module_path,start_line,"
        "end_line,is_test,derivation) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (sid, blob_id, kind, name, qualified_name, module_path, start_line, end_line, 1 if is_test else 0,
         derivation),
    )


def put_call_site(conn: sqlite3.Connection, cid: str, blob_id: str, path: str, line: int,
                   caller_symbol: str | None, callee_text: str, callee_name: str, call_kind: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO code_call_site(call_site_id,blob_id,path,line,caller_symbol,callee_text,"
        "callee_name,call_kind) VALUES (?,?,?,?,?,?,?,?)",
        (cid, blob_id, path, line, caller_symbol, callee_text, callee_name, call_kind),
    )


def put_literal(conn: sqlite3.Connection, blob_id: str, path: str, line: int, enclosing_symbol: str | None,
                 value: str) -> None:
    conn.execute(
        "INSERT INTO code_literal(blob_id,path,line,enclosing_symbol,value) VALUES (?,?,?,?,?)",
        (blob_id, path, line, enclosing_symbol, value),
    )


def put_parse_error(conn: sqlite3.Connection, blob_id: str, path: str, start_line: int, end_line: int,
                     start_col: int, end_col: int) -> None:
    conn.execute(
        "INSERT INTO code_parse_error(blob_id,path,start_line,end_line,start_col,end_col) VALUES (?,?,?,?,?,?)",
        (blob_id, path, start_line, end_line, start_col, end_col),
    )


def clear_blob(conn: sqlite3.Connection, blob_id: str) -> None:
    """Used when a blob is re-indexed under a new adapter/grammar version (ARCHITECTURE.md section 3: "symbols,
    calls, literals ... invalidated by: a new blob; an adapter or grammar change")."""
    conn.execute("DELETE FROM code_symbol WHERE blob_id=?", (blob_id,))
    conn.execute("DELETE FROM code_call_site WHERE blob_id=?", (blob_id,))
    conn.execute("DELETE FROM code_literal WHERE blob_id=?", (blob_id,))
    conn.execute("DELETE FROM code_parse_error WHERE blob_id=?", (blob_id,))


def put_excluded_blob(conn: sqlite3.Connection, blob_id: str, path: str, rule_id: str, effect: str) -> None:
    """Record ``blob_id`` as NOT code-indexable, per ``govbridge.core.corpus.classify_entry`` -- ``effect`` is
    whatever corpus-rules.yaml's matching rule declares (EXCLUDE, METADATA_ONLY, LEXICAL_ONLY,
    NO_DEFAULT_RETRIEVAL -- anything other than INCLUDE), never assumed to be EXCLUDE specifically. Sticky: a blob
    recorded here is never reclassified by a later ``ensure_indexed`` call (its own module docstring) -- exactly
    the same "cached by blob" discipline a successfully-parsed blob already gets in ``code_blob``. ``INSERT OR
    REPLACE`` would reset ``eager`` back to its column default on a row that ``set_eager_blobs`` already marked --
    ``INSERT OR IGNORE`` instead, since a blob classified excluded once never needs reclassifying (its rule_id/
    effect cannot change without a corpus-rules.yaml edit, which forces a from-clean rebuild -- see this module's
    own docstring)."""
    conn.execute(
        "INSERT OR IGNORE INTO code_excluded_blob(blob_id, path, rule_id, effect) VALUES (?,?,?,?)",
        (blob_id, path, rule_id, effect),
    )


def is_excluded(conn: sqlite3.Connection, blob_id: str) -> bool:
    return conn.execute("SELECT 1 FROM code_excluded_blob WHERE blob_id=?", (blob_id,)).fetchone() is not None


def excluded_for_blobs(conn: sqlite3.Connection, blob_ids: list[str]) -> list[sqlite3.Row]:
    """Every ``code_excluded_blob`` row among ``blob_ids`` -- ``govbridge.code.symbols.stats``'s ``files_excluded``
    disclosure calls this with a commit's whole entry set, exactly the way it already calls
    ``parse_errors_for_blobs`` for ``files_with_parse_errors``."""
    if not blob_ids:
        return []
    return _rows_cursor(conn).execute(
        f"SELECT * FROM code_excluded_blob WHERE blob_id IN ({_in_clause(len(blob_ids))})", blob_ids
    ).fetchall()


def set_eager_blobs(conn: sqlite3.Connection, blob_ids: set[str]) -> None:
    """Recompute ``eager`` from scratch, on BOTH ``code_blob`` and ``code_excluded_blob``: every row in each table
    is cleared, then set for exactly the ids in ``blob_ids`` that table actually has a row for (a successfully
    indexed blob and an excluded one are never the same id, so each table simply ignores ids belonging to the
    other). ``blob_ids`` is every blob reachable, right now, at the eager ref set -- included or excluded alike;
    the caller classifies/parses-or-records them first, via ``ensure_indexed``. Always a full reset-then-set,
    never an incremental patch, so an eager ref that stops reaching a blob (content changed, or the ref moved away
    from it) is reflected exactly as a from-clean build would see it -- this is what keeps BR-HO-0014 acceptance
    check 4 ("incremental == full") exact regardless of history."""
    conn.execute("UPDATE code_blob SET eager=0")
    conn.execute("UPDATE code_excluded_blob SET eager=0")
    if blob_ids:
        ids = sorted(blob_ids)
        placeholders = _in_clause(len(ids))
        conn.execute(f"UPDATE code_blob SET eager=1 WHERE blob_id IN ({placeholders})", ids)
        conn.execute(f"UPDATE code_excluded_blob SET eager=1 WHERE blob_id IN ({placeholders})", ids)
    conn.commit()


def eager_blob_ids(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute("SELECT blob_id FROM code_blob WHERE eager=1 ORDER BY blob_id").fetchall()]


def eager_excluded_blob_ids(conn: sqlite3.Connection) -> list[str]:
    """The excluded counterpart of ``eager_blob_ids``: every ``code_excluded_blob`` row reachable, right now, at
    the eager ref set (BR-AR-0014 follow-up 1's own acceptance check 9, "the excluded count")."""
    return [r[0] for r in
            conn.execute("SELECT blob_id FROM code_excluded_blob WHERE eager=1 ORDER BY blob_id").fetchall()]


def _in_clause(n: int) -> str:
    return ",".join("?" * n)


def _rows_cursor(conn: sqlite3.Connection) -> sqlite3.Cursor:
    """A cursor scoped to sqlite3.Row results, without mutating the shared connection's row_factory (the same
    connection is also used by govbridge.core.manifest's plain-tuple digest queries)."""
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row
    return cur


def symbols_for_blobs(conn: sqlite3.Connection, blob_ids: list[str]) -> list[sqlite3.Row]:
    if not blob_ids:
        return []
    return _rows_cursor(conn).execute(
        f"SELECT * FROM code_symbol WHERE blob_id IN ({_in_clause(len(blob_ids))})", blob_ids
    ).fetchall()


def call_sites_for_blobs(conn: sqlite3.Connection, blob_ids: list[str]) -> list[sqlite3.Row]:
    if not blob_ids:
        return []
    return _rows_cursor(conn).execute(
        f"SELECT * FROM code_call_site WHERE blob_id IN ({_in_clause(len(blob_ids))})", blob_ids
    ).fetchall()


def literals_for_blobs(conn: sqlite3.Connection, blob_ids: list[str]) -> list[sqlite3.Row]:
    if not blob_ids:
        return []
    return _rows_cursor(conn).execute(
        f"SELECT * FROM code_literal WHERE blob_id IN ({_in_clause(len(blob_ids))})", blob_ids
    ).fetchall()


def parse_errors_for_blobs(conn: sqlite3.Connection, blob_ids: list[str]) -> list[sqlite3.Row]:
    if not blob_ids:
        return []
    return _rows_cursor(conn).execute(
        f"SELECT * FROM code_parse_error WHERE blob_id IN ({_in_clause(len(blob_ids))})", blob_ids
    ).fetchall()
