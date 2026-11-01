"""Counts, read-only, each path-map namespace's tracked files, chunks and chunks with vectors in a clone's store,
judged by the namespaces of the path map given (the head's), and the paths that gain or lose vectors between two
stores. Prints paths only, never file contents.

    python3 vectors.py <base clone> <head clone> <out.json>
"""
import fnmatch
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

base, head, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])


def rx(pattern):
    parts = pattern.split("**")
    segs = [re.escape(p).replace(r"\*", "[^/]*") for p in parts]
    r = "^" + ".*".join(segs)
    if pattern.endswith("**"):
        r += ".*"
    return re.compile(r + "$")


def namespaces(clone):
    data = yaml.safe_load((clone / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    return {name: ([rx(p) for p in ns["paths"]], ns["embedding_policy"], ns.get("sensitivity"), ns.get("export_policy"))
            for name, ns in data["namespaces"].items()}


def tracked(clone):
    return subprocess.run(["git", "-C", str(clone), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")[:-1]


def store(clone):
    c = sqlite3.connect(f"file:{clone}/.gov-runtime/store.db?mode=ro", uri=True)
    chunks = {}
    for path, chunk_id in c.execute("select path, chunk_id from lexical_chunk"):
        chunks.setdefault(path, []).append(chunk_id)
    vec = {row[0] for row in c.execute("select chunk_id from semantic_vector")}
    return chunks, vec


def tally(clone, ns):
    files = tracked(clone)
    chunks, vec = store(clone)
    per = {}
    with_vec_paths = set()
    for path in files:
        names = [n for n, (pats, *_rest) in ns.items() if any(p.match(path) for p in pats)]
        key = names[0] if len(names) == 1 else ("NONE" if not names else "MANY:" + ",".join(names))
        row = per.setdefault(key, {"files": 0, "chunks": 0, "chunks_with_vectors": 0, "files_with_vectors": 0})
        row["files"] += 1
        cs = chunks.get(path, [])
        row["chunks"] += len(cs)
        n = sum(1 for cid in cs if cid in vec)
        row["chunks_with_vectors"] += n
        if n:
            row["files_with_vectors"] += 1
            with_vec_paths.add(path)
    total = {"paths_with_chunks": len(chunks), "chunks": sum(len(v) for v in chunks.values()), "chunks_with_vectors": len(vec)}
    return per, with_vec_paths, total


ns_head = namespaces(head)
per_base, vb, tb = tally(base, ns_head)
per_head, vh, th = tally(head, ns_head)
doc = {
    "namespaces_by_head_map": {n: {"embedding_policy": v[1], "sensitivity": v[2], "export_policy": v[3]} for n, v in ns_head.items()},
    "base": {"per_namespace": per_base, "total": tb},
    "head": {"per_namespace": per_head, "total": th},
    "gained_vectors": sorted(vh - vb),
    "lost_vectors": sorted(vb - vh),
}
out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
for side in ("base", "head"):
    print(side, doc[side]["total"])
    for n, row in sorted(doc[side]["per_namespace"].items()):
        print("  ", n, row)
print("gained", len(doc["gained_vectors"]), "lost", len(doc["lost_vectors"]))
outside = [p for p in doc["gained_vectors"] if not (("/" not in p) or p.startswith("governance/") or p.startswith("schemas/"))]
print("gained outside root/governance/schemas:", outside)
