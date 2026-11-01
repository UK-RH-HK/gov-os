import sqlite3
import sys

conn = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    try:
        n = conn.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
    except sqlite3.Error as exc:
        n = f"error {exc}"
    print(name, n)
try:
    print("meta:", conn.execute("SELECT * FROM meta").fetchall()[:10])
except sqlite3.Error as exc:
    print("no meta:", exc)
