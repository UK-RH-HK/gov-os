#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001). Size of the semantic tier under the draft embed profile (ARCHITECTURE.md section 1.1
L-MACHINE-OUTPUT; SEMANTIC_ROUTE.md section 3): unique included blobs across the given refs, split into embedded kinds
and lexical-only kinds, with line-aligned chunk counts (<=1200 chars, one-line overlap, as fts_spike.py).

usage: embed_tier_measure.py REF [REF...]
"""
import collections, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus_measure as cm

EMBED = {"md", "txt", "html", "yaml", "yml", "toml", "rs", "py", "sh"}
LEXICAL_ONLY = {"out", "log", "shimlog", "stderr", "diff", "patch", "tsv", "jsonl", "summary"}


def chunk_count(text):
    lines = text.split("\n"); i = 0; n = 0
    while i < len(lines):
        j, b = i, 0
        while j < len(lines) and (b + len(lines[j]) + 1 <= 1200 or j == i):
            b += len(lines[j]) + 1; j += 1
        n += 1
        i = j if j >= len(lines) else max(j - 1, i + 1)
    return n


def main():
    cat = cm.Cat(); seen = set(); tier = collections.Counter(); tier_bytes = collections.Counter(); tier_chunks = collections.Counter()
    for ref in sys.argv[1:]:
        commit = subprocess.run(["git", "rev-parse", ref + "^{commit}"], capture_output=True, text=True).stdout.strip()
        for mode, typ, oid, size, path in cm.ls_tree(commit):
            if oid in seen:
                continue
            rule, _ = cm.classify(path, mode, typ, size, cat, {})
            if rule is not None:
                continue
            data = cat.read(oid)
            if b"\0" in data[:8000]:
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if any(re.search(rx, text) for rx in cm.SECRET_CONTENT.values()):
                continue
            seen.add(oid)
            ext = path.rsplit(".", 1)[-1] if "." in path.rsplit("/", 1)[-1] else "(none)"
            if ext in EMBED or (ext == "json" and size <= 65536):
                t = "embedded"
            elif ext in LEXICAL_ONLY or ext == "json":
                t = "lexical_only"
            else:
                t = "embedded_other_kind(" + ext + ")"
            k = "embedded" if t.startswith("embedded") else t
            tier[k] += 1; tier_bytes[k] += size; tier_chunks[k] += chunk_count(text)
    rate = 24.9  # chunks/s measured, SO-10 batch-1 16 threads
    print(json.dumps({"refs": sys.argv[1:], "unique_blobs": len(seen), "blobs": dict(tier), "bytes": dict(tier_bytes),
                      "chunks": dict(tier_chunks),
                      "est_full_semantic_minutes_at_24_9_chunks_per_s": round(tier_chunks["embedded"] / rate / 60, 1)}, indent=1))


if __name__ == "__main__":
    main()
