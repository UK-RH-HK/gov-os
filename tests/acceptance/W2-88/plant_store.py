"""Child program of the S10 cases: plant a store at ``argv[1]`` (a committed repository) in the state ``argv[2]`` names.

``load``: the product's own load (stamps the store where the head stamps). ``older`` / ``newer``: the stamp the load wrote,
moved to 1 / ``LAYOUT_VERSION + 1`` (every column of the stamp table that holds the current version is rewritten, so the
case needs no knowledge of the table's columns). ``unstamped``: the stamp table dropped. Prints the version ``layout.
version_of`` reads afterwards (None where there is none)."""

import json
import sqlite3
import sys
from pathlib import Path

from gov.store import loader

root, mode = Path(sys.argv[1]), sys.argv[2]
loader.load(root)
db = root / ".gov-runtime" / "store.db"
result = {"mode": mode, "version": None}
if mode != "load":
    from gov.store import layout
    conn = sqlite3.connect(db)
    table = layout.STAMP_TABLE
    if mode == "unstamped":
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    else:
        target = 1 if mode == "older" else layout.LAYOUT_VERSION + 1
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        assert rows, f"{table} holds no row after the load: the load did not stamp"
        for index, column in enumerate(columns):
            if rows[0][index] == layout.LAYOUT_VERSION:
                conn.execute(f"UPDATE {table} SET {column} = ?", (target,))
    conn.commit()
    result["version"] = None if mode == "unstamped" else layout.version_of(conn)
    conn.close()
else:
    try:
        from gov.store import layout
        conn = sqlite3.connect(db)
        result["version"] = layout.version_of(conn)
        result["expected"] = layout.LAYOUT_VERSION
        conn.close()
    except ImportError:
        pass
print(json.dumps(result))
