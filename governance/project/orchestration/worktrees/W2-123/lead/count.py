"""Count the semantic vectors in a store, read-only: count.py <store.db>."""
import sqlite3
import sys
import time

connection = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True, timeout=5)
try:
    print(time.strftime("%H:%M:%S"), connection.execute("SELECT count(*) FROM semantic_vector").fetchone()[0])
except sqlite3.Error as error:
    print("unreadable:", error)
finally:
    connection.close()
