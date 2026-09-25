#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001). Cost of a content-addressed SQLite FTS5 lexical index over the included blobs of
several refs (blob-level dedupe; occurrences table maps (ref, path) -> blob), and three smoke queries.

usage: fts_spike.py DB_PATH REF [REF...]
"""
import hashlib, json, os, re, sqlite3, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus_measure as cm


def main():
    db, refs = sys.argv[1], sys.argv[2:]
    if os.path.exists(db):
        os.replace(db, db + ".old")
    con = sqlite3.connect(db)
    con.executescript("""
      CREATE TABLE occurrence(ref TEXT, commit_id TEXT, path TEXT, blob TEXT, mode TEXT);
      CREATE TABLE blob(blob TEXT PRIMARY KEY, bytes INT, lines INT);
      CREATE VIRTUAL TABLE chunk USING fts5(blob UNINDEXED, start_line UNINDEXED, end_line UNINDEXED, text,
                                            tokenize = "porter unicode61 tokenchars '_'");
    """)
    cat = cm.Cat(); seen = set(); t0 = time.time(); nchunks = 0
    for ref in refs:
        commit = subprocess.run(["git", "rev-parse", ref + "^{commit}"], capture_output=True, text=True).stdout.strip()
        for mode, typ, oid, size, path in cm.ls_tree(commit):
            rule, _ = cm.classify(path, mode, typ, size, cat, {})
            if rule is not None:
                continue
            con.execute("INSERT INTO occurrence VALUES (?,?,?,?,?)", (ref, commit, path, oid, mode))
            if oid in seen:
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
            lines = text.split("\n")
            con.execute("INSERT INTO blob VALUES (?,?,?)", (oid, size, len(lines)))
            # line-aligned chunks of <= ~1200 chars with a one-line overlap
            i = 0
            while i < len(lines):
                j, n = i, 0
                while j < len(lines) and (n + len(lines[j]) + 1 <= 1200 or j == i):
                    n += len(lines[j]) + 1; j += 1
                con.execute("INSERT INTO chunk VALUES (?,?,?,?)", (oid, i + 1, j, "\n".join(lines[i:j])))
                nchunks += 1
                i = j if j >= len(lines) else max(j - 1, i + 1)
    con.commit(); t1 = time.time()
    con.execute("INSERT INTO chunk(chunk) VALUES('optimize')"); con.commit(); t2 = time.time()
    out = {"refs": refs, "unique_blobs": len(seen), "chunks": nchunks, "build_s": round(t1 - t0, 1),
           "optimize_s": round(t2 - t1, 1), "db_bytes": os.path.getsize(db)}
    print(json.dumps(out))
    for q in ['"partition_floor_rules_against_kernel"', 'NEAR(last match wins, 3)', '"creator liveness"']:
        t = time.time()
        rows = con.execute("""SELECT c.blob, c.start_line, bm25(chunk) AS s FROM chunk c WHERE chunk MATCH ?
                              ORDER BY s LIMIT 5""", (q,)).fetchall()
        hits = []
        for b, sl, s in rows:
            occ = con.execute("SELECT ref, path FROM occurrence WHERE blob=? ORDER BY ref, path LIMIT 3", (b,)).fetchall()
            hits.append({"blob": b[:12], "line": sl, "bm25": round(s, 2), "occurrences": occ})
        n = con.execute("SELECT count(*) FROM chunk WHERE chunk MATCH ?", (q,)).fetchone()[0]
        print(json.dumps({"query": q, "matching_chunks": n, "ms": round((time.time() - t) * 1000, 1), "top5": hits}))


if __name__ == "__main__":
    main()
