"""Child program of the F2 case: ``gov`` with one planted fault. ``a9_drop_file.py <path> <gov arguments...>`` runs the
CLI with ``gov.rebuild.command.run`` (which A9 calls in full, I3) wrapped: after the real rebuild, every row that names
``<path>`` is deleted from the lexical and semantic tables of ``.gov-runtime/store.db`` (the tables I5 says
``lexical_*`` and ``semantic_*``). A tracked file the rebuild judged is then in no store: neither indexed nor named with
a reason. It prints ``planted: removed <n> rows`` on stderr, so the case can tell a plant that took from one that did not."""

import sqlite3
import sys
from pathlib import Path

import gov.rebuild.command as rebuild

original = rebuild.run
dropped = sys.argv[1]


def planted(root, args, config):
    result = original(root, args, config)
    conn = sqlite3.connect(Path(root) / ".gov-runtime" / "store.db")
    removed = 0
    names = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND "
                                            "(name LIKE 'lexical%' OR name LIKE 'semantic%')")]
    for table in names:
        for column in [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]:
            if column in ("path", "file", "source", "rel"):
                try:
                    removed += conn.execute(f"DELETE FROM {table} WHERE {column} = ?", (dropped,)).rowcount
                except sqlite3.Error:
                    pass
    conn.commit()
    conn.close()
    sys.stderr.write(f"planted: removed {removed} rows\n")
    return result


rebuild.run = planted
sys.argv = ["gov", *sys.argv[2:]]
from gov.cli.main import main  # noqa: E402

raise SystemExit(main())
