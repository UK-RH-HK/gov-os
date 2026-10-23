"""Which part of .gov-runtime/store.db makes the secrets-indexing check red: its raw bytes, or its rows as text.

Prints booleans and sizes only, never a match (the scan runs gitleaks with --redact and keeps only the exit code).
"""
import sqlite3
import sys
from pathlib import Path

from gov.secrets import _holds_secret, _rules

root = Path("/home/usain/gov-os-worktrees/W2-67")
store = root / ".gov-runtime" / "store.db"
rules = _rules(root)
raw = store.read_bytes()
print("raw bytes", len(raw), flush=True)
connection = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
tables = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
hits = []
for name in tables:
    text = "\n".join(" ".join(str(v) for v in row) for row in connection.execute(f'SELECT * FROM "{name}"'))
    data = text.encode("utf-8", "replace")
    found = _holds_secret(rules, b"\n" + data) if data else False
    print(f"table {name}: {len(data)} bytes of rows, token found: {found}", flush=True)
    if found:
        hits.append(name)
connection.close()
print("rows hit tables:", hits, flush=True)
print("raw bytes token found:", _holds_secret(rules, raw), flush=True)
sys.exit(0)
