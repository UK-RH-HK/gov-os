"""Round 2, KPI success 2: rebuild recreates every derived store.

The current ``src/gov/rebuild/command.py`` deletes ``store.db`` entirely
and calls ``store_load``, which builds only the record graph (five tables).
The lexical index (W1-17) and semantic index (W1-19) tables are lost.

Either rebuild recreates each derived store by calling the code that owns
it, or it removes only what it can recreate and names what it left out.

Predecessor analysis
--------------------
The first round's ``test_w1_27_rebuild.py`` has five cases.  The closest
is ``test_rebuild_recreates_derived_stores``, which only asserts that
``.gov-runtime/`` **exists** — it never opens ``store.db`` to check
which tables are present.  The predecessor's case was **weak**: it
verified the directory, not the table set.

Revised after implementation: rebuild goes through the lexical index's
owner and its secrets filter (DEC-440); the fixture's size, not the
behaviour, made it time out.  Every case now uses a tiny project with
``run_gov_with_code`` for the code root.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import w1_27_support as support
import w2_67b_support


LEXICAL_TABLES = {"lexical_file", "lexical_parent", "lexical_chunk"}
SEMANTIC_TABLES = {"semantic_vector", "semantic_manifest"}


def _tables_in_store(project):
    """Return the set of table names in ``.gov-runtime/store.db``."""
    store_path = Path(project) / ".gov-runtime" / "store.db"
    assert store_path.is_file(), "store.db does not exist"
    conn = sqlite3.connect(store_path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Rebuild must recreate the lexical index
# --------------------------------------------------------------------------- #

def test_rebuild_recreates_lexical_index(rebuild_gov, rebuild_project, interface):
    """After rebuild, the lexical index tables exist in ``store.db``.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    The lexical index (W1-17) is a derived store; rebuild must create its
    tables (lexical_file, lexical_parent, lexical_chunk).

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    tables = _tables_in_store(rebuild_project)
    missing = LEXICAL_TABLES - tables
    assert not missing, (
        f"rebuild does not create the lexical index tables: "
        f"missing {sorted(missing)}; tables present: {sorted(tables)}\n"
        f"{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Rebuild must not silently drop existing lexical tables
# --------------------------------------------------------------------------- #

def test_rebuild_does_not_silently_drop_lexical_tables(sandbox, tmp_path):
    """Existing lexical index tables must not be silently deleted by rebuild.

    The current implementation deletes ``store.db`` entirely and rebuilds
    only the record graph, silently losing the lexical (and semantic) tables.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): it repeated the table-presence check of
    ``test_rebuild_recreates_lexical_index`` and never read the planted
    row's fate.  The table is kept and recreated from git: the row planted
    for a file git does not hold is gone after the rebuild, and the
    project's own tracked file is there.
    """
    rebuild_project = w2_67b_support.rebuild_project(tmp_path / "repo")
    run1, _ = w2_67b_support.rebuild(rebuild_project, sandbox)

    store_path = rebuild_project / ".gov-runtime" / "store.db"
    conn = sqlite3.connect(str(store_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS lexical_file "
        "(path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL)"
    )
    conn.execute("INSERT INTO lexical_file VALUES ('test.py', 'abc123', 1)")
    conn.commit()
    conn.close()

    run2, _ = w2_67b_support.rebuild(rebuild_project, sandbox)

    tables = _tables_in_store(rebuild_project)
    assert "lexical_file" in tables, (
        f"rebuild silently dropped lexical_file; tables after rebuild: "
        f"{sorted(tables)}\n{run2.describe()}"
    )
    paths = {row[0] for row in w2_67b_support.store_rows(rebuild_project, "SELECT path FROM lexical_file")}
    assert "test.py" not in paths, (
        f"the row planted for test.py, which git does not hold, survives the rebuild: lexical_file holds "
        f"{sorted(paths)}\n{run2.describe()}"
    )
    assert support.PATH_MAP_REL in paths, (
        f"the rebuilt lexical_file does not hold the tracked {support.PATH_MAP_REL}: {sorted(paths)}\n"
        f"{run2.describe()}"
    )


# --------------------------------------------------------------------------- #
# Rebuild must report stores it could not recreate
# --------------------------------------------------------------------------- #

def test_rebuild_result_names_unreconstructed_stores(sandbox, tmp_path):
    """If rebuild cannot recreate a derived store it must name it in the result.

    The semantic index requires a model (Ollama + qwen3-embedding).  If
    the model is absent, rebuild must say so by name — not silently drop
    the tables.  "Semantic needs a model that may be absent" is answered
    by the sources or returned as a package, never by silently dropping
    the tables.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion does not read what
    the case's name claims): ``stores.semantic`` is always in the result.
    The case now reads the status and reason of each store: one whose
    tables are not in the store is ``not_recreated`` with a reason, and the
    lexical store, whose tables are there, is ``recreated``.
    """
    rebuild_project = w2_67b_support.rebuild_project(tmp_path / "repo")
    run, result = w2_67b_support.rebuild(rebuild_project, sandbox)
    tables = _tables_in_store(rebuild_project)
    stores = result.get("stores")
    assert isinstance(stores, dict) and stores, f"the result names no store: {result}\n{run.describe()}"

    if not SEMANTIC_TABLES.issubset(tables):
        semantic = stores.get("semantic") or {}
        assert semantic.get("status") == "not_recreated" and semantic.get("reason"), (
            f"the semantic index was not recreated but rebuild does not "
            f"name it not_recreated with a reason; tables: {sorted(tables)}\n"
            f"result: {result}\n{run.describe()}"
        )
    assert LEXICAL_TABLES <= tables and (stores.get("lexical") or {}).get("status") == "recreated", (
        f"the lexical store is not both in the store and named recreated; tables: {sorted(tables)}\n"
        f"result: {result}\n{run.describe()}"
    )
    for name, entry in stores.items():
        assert isinstance(entry, dict) and entry.get("status") in ("recreated", "not_recreated"), (
            f"store {name} has no status recreated or not_recreated: {entry}\n{run.describe()}"
        )
        if entry["status"] == "not_recreated":
            assert entry.get("reason"), f"store {name} is not recreated and gives no reason: {entry}"
