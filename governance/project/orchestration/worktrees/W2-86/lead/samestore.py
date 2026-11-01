"""Compare two stores' lexical file sets and vector sets by path (read-only). usage: samestore.py <root a> <root b>"""
import sqlite3
import sys
from pathlib import Path


def load(root):
    connection = sqlite3.connect((Path(root) / ".gov-runtime/store.db").resolve().as_uri() + "?mode=ro", uri=True)
    files = dict(connection.execute("SELECT path, blob FROM lexical_file").fetchall())
    vectors = {}
    for rel, has in connection.execute("SELECT c.path, v.chunk_id IS NOT NULL FROM lexical_chunk c LEFT JOIN "
                                       "semantic_vector v ON v.chunk_id = c.chunk_id"):
        vectors[rel] = vectors.get(rel, 0) + (1 if has else 0)
    connection.close()
    return files, vectors


(fa, va), (fb, vb) = load(sys.argv[1]), load(sys.argv[2])
print("files", len(fa), len(fb), "blob differs", sorted(p for p in set(fa) | set(fb) if fa.get(p) != fb.get(p))[:20])
print("vector counts differ", sorted(p for p in set(va) | set(vb) if va.get(p, 0) != vb.get(p, 0))[:20])
print("chunks with vectors", sum(va.values()), sum(vb.values()))
