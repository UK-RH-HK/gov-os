"""List the tables of a store and try the records query (W2-87 lead: store schema of the pinned gov)."""
import sqlite3
import sys

db = sqlite3.connect(f"file:{sys.argv[1]}/.gov-runtime/store.db?mode=ro", uri=True)
print(sorted(row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")))
try:
    db.execute("SELECT records.id FROM records LEFT JOIN register_entries ON register_entries.id = records.id LIMIT 1")
    print("records join: ok")
except sqlite3.OperationalError as error:
    print("records join:", error)
print(db.execute("SELECT count(*), count(DISTINCT path) FROM records").fetchone())
