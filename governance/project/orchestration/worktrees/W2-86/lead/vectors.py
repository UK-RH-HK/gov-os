"""W2-86: the chunks with vectors in a store, by group, and the paths whose vector set differs between two stores.

python3 vectors.py <base clone> <head clone> > out.json   (each store opened read-only)
"""
import json
import sqlite3
import sys
from pathlib import Path

GROUPS = {
    "roles": "template/governance/kernel/roles/",
    "hooks": "template/governance/kernel/hooks/",
    "skills (kernel, incl. superpowers/vendored.yaml)": "template/governance/kernel/skills/",
    "vendor": "template/governance/kernel/vendor/",
    "skills/superpowers/<skill>/": "template/governance/kernel/skills/superpowers/",
    "bin": "template/governance/kernel/bin/",
    "template/.rulesync": "template/.rulesync/",
    "template (all)": "template/",
}


def per_path(clone: str) -> dict:
    store = Path(clone) / ".gov-runtime" / "store.db"
    connection = sqlite3.connect(store.resolve().as_uri() + "?mode=ro", uri=True)
    rows = connection.execute("SELECT c.path, c.chunk_id, v.chunk_id IS NOT NULL FROM lexical_chunk c "
                              "LEFT JOIN semantic_vector v ON v.chunk_id = c.chunk_id").fetchall()
    connection.close()
    paths: dict = {}
    for rel, _chunk, has in rows:
        entry = paths.setdefault(rel, [0, 0])
        entry[0] += 1
        entry[1] += 1 if has else 0
    return paths


def summary(paths: dict) -> dict:
    out = {}
    for name, prefix in GROUPS.items():
        chosen = {rel: v for rel, v in paths.items() if rel.startswith(prefix)}
        if name == "skills/superpowers/<skill>/":
            chosen = {rel: v for rel, v in chosen.items() if "/" in rel[len(prefix):]}
        out[name] = {"files": len(chosen), "chunks": sum(v[0] for v in chosen.values()),
                     "chunks_with_vectors": sum(v[1] for v in chosen.values()),
                     "files_with_vectors": sum(1 for v in chosen.values() if v[1])}
    out["all"] = {"files": len(paths), "chunks": sum(v[0] for v in paths.values()),
                  "chunks_with_vectors": sum(v[1] for v in paths.values())}
    return out


def blobs(clone: str) -> dict:
    store = Path(clone) / ".gov-runtime" / "store.db"
    connection = sqlite3.connect(store.resolve().as_uri() + "?mode=ro", uri=True)
    rows = dict(connection.execute("SELECT path, blob FROM lexical_file").fetchall())
    connection.close()
    return rows


def main() -> None:
    base, head = per_path(sys.argv[1]), per_path(sys.argv[2])
    base_blobs, head_blobs = blobs(sys.argv[1]), blobs(sys.argv[2])
    lexical_changed = sorted(rel for rel in set(base_blobs) | set(head_blobs)
                             if base_blobs.get(rel) != head_blobs.get(rel))
    diff = sorted(rel for rel in set(base) | set(head)
                  if (base.get(rel, [0, 0])[1] > 0) != (head.get(rel, [0, 0])[1] > 0)
                  or base.get(rel, [0, 0])[1] != head.get(rel, [0, 0])[1])
    gained = [rel for rel in diff if head.get(rel, [0, 0])[1] > base.get(rel, [0, 0])[1]]
    lost = [rel for rel in diff if head.get(rel, [0, 0])[1] < base.get(rel, [0, 0])[1]]
    lexical_only = sorted(rel for rel in set(base) ^ set(head))
    json.dump({"base": summary(base), "head": summary(head),
               "vector_diff": {"paths": len(diff), "gained": gained, "lost": lost,
                               "outside_template": [rel for rel in diff if not rel.startswith("template/")]},
               "lexical_paths_only_in_one": lexical_only,
               "lexical_files_changed": lexical_changed}, sys.stdout, indent=1)


main()
