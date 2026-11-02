"""missing.py <root>: read-only; the chunks the semantic store wants and lacks, their paths, and the store's status."""
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from gov.retrieval import semantic
from gov.store import STORE_REL

root = Path(sys.argv[1])
connection = sqlite3.connect((root / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
wanted = semantic._wanted(root, connection)
have = {c for (c,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
missing = [c for c in wanted if c not in have]
print(f"wanted {len(wanted)}, have {len(have)}, missing {len(missing)}")
paths = Counter()
for chunk_id in missing:
    row = connection.execute("SELECT path FROM lexical_chunk WHERE chunk_id = ?", (chunk_id,)).fetchone()
    paths[row[0] if row else "?"] += 1
for path, n in paths.most_common(25):
    print(n, path)
print("first missing batch:", missing[:semantic.BATCH][:3], "...")
print("manifest:", connection.execute("SELECT * FROM semantic_manifest").fetchall())
