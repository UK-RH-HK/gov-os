"""Child program of RV1-6's cases (S10, F3): a store the layout calls stale is loaded, then opened.

``load_then_open.py <project> <state>`` plants the store at ``<project>`` (a committed repository) in a stale ``state``, runs
``gov.store.loader.load`` on it, then opens it through ``gov.store.loader.connect`` and prints one JSON line:
``{"state", "before": <the open before the load>, "load": <None or the load's GovError code>, "after": <the open after it>}``, each
open ``{"outcome": "opened"}`` or ``{"outcome": "error", "code", "message", "details"}``.

States: ``unstamped-lexical-no-parent`` (a hand-built store with no stamp whose ``lexical_chunk`` lacks ``parent_id``: a table the
layout names present without one of its columns, so stale with ``found`` 0), ``stamped-1`` (the load's own store with its stamp
moved to 1, an older layout). The load of a stale store must not stamp it current (RV1-6): the open after it is the open before."""

import json
import sqlite3
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.store import layout, loader

root, state = Path(sys.argv[1]), sys.argv[2]
db = root / ".gov-runtime" / "store.db"


def opened():
    try:
        loader.connect(root).close()
        return {"outcome": "opened"}
    except GovError as error:
        return {"outcome": "error", "code": error.code, "message": error.message, "details": error.details}


if state == "unstamped-lexical-no-parent":
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, path TEXT NOT NULL, "
                 "start_line INTEGER NOT NULL, end_line INTEGER NOT NULL)")
    conn.commit()
    conn.close()
elif state == "stamped-1":
    loader.load(root)
    conn = sqlite3.connect(db)
    table = layout.STAMP_TABLE
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    assert rows, f"{table} holds no row after the load: the load did not stamp"
    for index, column in enumerate(columns):
        if rows[0][index] == layout.LAYOUT_VERSION:
            conn.execute(f"UPDATE {table} SET {column} = 1")
    conn.commit()
    conn.close()
else:
    raise SystemExit(f"unknown state {state!r}")

before = opened()
load_error = None
try:
    loader.load(root)
except GovError as error:
    load_error = error.code
except Exception as error:  # noqa: BLE001: reported, never hidden: the case names it
    load_error = type(error).__name__ + ": " + str(error)[:200]
print(json.dumps({"state": state, "before": before, "load": load_error, "after": opened()}, default=str))
