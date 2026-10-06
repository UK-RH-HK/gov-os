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
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import w1_27_support as support


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

def test_rebuild_recreates_lexical_index(gov, project, interface):
    """After rebuild, the lexical index tables exist in ``store.db``.

    KPI: "rebuild recreates every derived store" [CAP-07.a].
    The lexical index (W1-17) is a derived store; rebuild must create its
    tables (lexical_file, lexical_parent, lexical_chunk).
    """
    run = gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    tables = _tables_in_store(project)
    missing = LEXICAL_TABLES - tables
    assert not missing, (
        f"rebuild does not create the lexical index tables: "
        f"missing {sorted(missing)}; tables present: {sorted(tables)}\n"
        f"{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Rebuild must not silently drop existing lexical tables
# --------------------------------------------------------------------------- #

def test_rebuild_does_not_silently_drop_lexical_tables(gov, project, interface):
    """Existing lexical index tables must not be silently deleted by rebuild.

    The current implementation deletes ``store.db`` entirely and rebuilds
    only the record graph, silently losing the lexical (and semantic) tables.
    """
    run1 = gov("rebuild", "--json")
    support.assert_envelope(run1, interface, command="rebuild")
    assert run1.returncode == 0, f"first rebuild failed\n{run1.describe()}"

    store_path = project / ".gov-runtime" / "store.db"
    conn = sqlite3.connect(str(store_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS lexical_file "
        "(path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL)"
    )
    conn.execute("INSERT INTO lexical_file VALUES ('test.py', 'abc123', 1)")
    conn.commit()
    conn.close()

    run2 = gov("rebuild", "--json")
    support.assert_envelope(run2, interface, command="rebuild")
    assert run2.returncode == 0, f"second rebuild failed\n{run2.describe()}"

    tables = _tables_in_store(project)
    assert "lexical_file" in tables, (
        f"rebuild silently dropped lexical_file; tables after rebuild: "
        f"{sorted(tables)}\n{run2.describe()}"
    )


# --------------------------------------------------------------------------- #
# Rebuild must report stores it could not recreate
# --------------------------------------------------------------------------- #

def test_rebuild_result_names_unreconstructed_stores(gov, project, interface):
    """If rebuild cannot recreate a derived store it must name it in the result.

    The semantic index requires a model (Ollama + qwen3-embedding).  If
    the model is absent, rebuild must say so by name — not silently drop
    the tables.  "Semantic needs a model that may be absent" is answered
    by the sources or returned as a package, never by silently dropping
    the tables.
    """
    run = gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    tables = _tables_in_store(project)
    result_text = json.dumps(result).lower()

    if not SEMANTIC_TABLES.issubset(tables):
        assert "semantic" in result_text, (
            f"the semantic index was not recreated but rebuild does not "
            f"name it in the result; tables: {sorted(tables)}\n"
            f"result: {result}\n{run.describe()}"
        )
