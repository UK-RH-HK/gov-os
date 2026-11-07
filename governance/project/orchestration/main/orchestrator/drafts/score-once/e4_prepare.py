"""E4 (E3-E5-DESIGN §1, E0B-RESULT "Next"): the per-model window caches, and the checks e4_window.sh and
e4_replays.sh make on them. Counts and digests only: no question or text is read or written.

    python3 e4_prepare.py routes <new cache folder> <seed folder> <routes cache folder> <clone>
    python3 e4_prepare.py store <clone>
    python3 e4_prepare.py check <cache folder> <clone> <model> [<seed folder>]

``routes``: the new cache is the seed (``seed_scores.py``'s output: one model's kept scores, no route answer, marked
``memo_keys`` ``store``) copied whole, plus every route answer of ``<routes cache>`` (E0b's run-A cache on window 4's
clone), with its meta ``store``. So a single-model trial run (``GOV_RX_RERANK_DIR``) on this cache asks the routes
nothing new (the candidate lists are E0b's, those the replays reuse) and scores on the trial service only the texts the
seed lacks, into this cache (extend_window.sh's form: the kept caches are only read). Refused: a new folder that holds a
cache already; a seed that is not one model's scores alone (no route answer, ``memo_keys`` ``store``, one
``rerank_model``, no ``rerank_model2``); a routes cache keyed otherwise than by its store, or filled for another store
than the clone's now (its root resolved and its store's fingerprints head: rx.py's ``_store_of``), or holding scores of
a model mark.

``store``: the clone's store key as rx.py makes it, as JSON.

``check``: exit 0 when the cache marks ``<model>`` alone, is keyed by its store, holds the clone's store now and its route
answers; with ``<seed folder>``, also when it holds exactly the seed's scores (nothing scored into it yet). Prints one
line of counts either way.
"""
import json
import sqlite3
import sys
from pathlib import Path


def store_key(clone: Path) -> list:
    """[resolved root, fingerprints head] of ``clone``'s store, as rx.py's ``_store_of`` keys route answers."""
    where = str(Path(clone).resolve())
    path = Path(where) / ".gov-runtime" / "store.db"
    if not path.is_file():
        raise SystemExit(f"e4_prepare: no store at {path}: refused")
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        table = db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'fingerprints'").fetchone()
        rows = db.execute("SELECT head FROM fingerprints").fetchall() if table else []
    finally:
        db.close()
    if len(rows) != 1 or not rows[0][0]:
        raise SystemExit(f"e4_prepare: the store at {where} has no single fingerprints head: refused")
    return [where, rows[0][0]]


def _ro(folder: Path) -> sqlite3.Connection:
    path = Path(folder) / "cache.db"
    if not path.is_file():
        raise SystemExit(f"e4_prepare: no cache at {path}: refused")
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _facts(db: sqlite3.Connection) -> dict:
    meta = dict(db.execute("SELECT k, v FROM meta").fetchall())
    return {"meta": meta, "memo": db.execute("SELECT COUNT(*) FROM memo").fetchone()[0],
            "score": db.execute("SELECT COUNT(*) FROM score").fetchone()[0]}


def routes(dest: Path, seed: Path, source: Path, clone: Path) -> dict:
    if (Path(dest) / "cache.db").exists():
        raise SystemExit(f"e4_prepare: {Path(dest) / 'cache.db'} exists: refused (a new folder)")
    want = json.dumps(store_key(clone))
    s_db, r_db = _ro(seed), _ro(source)
    try:
        s, r = _facts(s_db), _facts(r_db)
        if s["memo"] or s["meta"].get("memo_keys") != "store" or not s["meta"].get("rerank_model") \
                or "rerank_model2" in s["meta"] or "store" in s["meta"]:
            raise SystemExit(f"e4_prepare: {seed} is not one model's scores alone (seed_scores.py's form): refused")
        if r["meta"].get("memo_keys") != "store":
            raise SystemExit(f"e4_prepare: {source}'s route answers are not keyed by their store: refused")
        if r["meta"].get("store") != want:
            raise SystemExit(f"e4_prepare: {source} holds the route answers of {r['meta'].get('store')}, and the "
                             f"clone's store is now {want}: refused (its store was rebuilt, or another clone)")
        if "rerank_model" in r["meta"] or "rerank_model2" in r["meta"]:
            raise SystemExit(f"e4_prepare: {source} marks a model: not a replay's own cache: refused")
        if not r["memo"]:
            raise SystemExit(f"e4_prepare: {source} holds no route answer: refused")
        Path(dest).mkdir(parents=True, exist_ok=True)
        out = sqlite3.connect(Path(dest) / "cache.db")
        try:
            s_db.backup(out)  # the seed whole: its scores, its tables, its meta (model, memo_keys store)
            memo = r_db.execute("SELECT k, v FROM memo").fetchall()
            out.executemany("INSERT INTO memo VALUES (?, ?)", memo)
            out.execute("INSERT INTO meta VALUES ('store', ?)", (want,))
            out.commit()
            got = _facts(out)
        finally:
            out.close()
    finally:
        s_db.close()
        r_db.close()
    return {"model": got["meta"]["rerank_model"], "scores": got["score"], "routes": got["memo"], "store": want,
            "seed_scores": s["score"], "source_routes": r["memo"]}


def check(cache: Path, clone: Path, model: str, seed: Path | None = None) -> tuple[bool, str]:
    db = _ro(cache)
    try:
        c = _facts(db)
    finally:
        db.close()
    want = json.dumps(store_key(clone))
    faults = []
    if c["meta"].get("rerank_model") != model:
        faults.append(f"marks {c['meta'].get('rerank_model')}, not {model}")
    if "rerank_model2" in c["meta"]:
        faults.append("marks a second model")
    if c["meta"].get("memo_keys") != "store":
        faults.append("not keyed by its store")
    if c["meta"].get("store") != want:
        faults.append(f"holds the store {c['meta'].get('store')}, not the clone's {want}")
    if not c["memo"]:
        faults.append("no route answer")
    line = f"{cache}: {c['score']} scores, {c['memo']} route answers, model {c['meta'].get('rerank_model')}"
    if seed is not None:
        sdb = _ro(seed)
        try:
            n = sdb.execute("SELECT COUNT(*) FROM score").fetchone()[0]
        finally:
            sdb.close()
        line += f" (its seed {n})"
        if c["score"] != n:
            faults.append(f"{c['score'] - n} scores beyond its seed's {n}: scored into already")
    return (not faults), line + ("" if not faults else "; " + "; ".join(faults))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["routes"] and len(args) == 5:
        rep = routes(Path(args[1]), Path(args[2]), Path(args[3]), Path(args[4]))
        print(f"e4_prepare: {args[1]}: {rep['scores']} scores of {rep['model']} (the seed's {rep['seed_scores']}), "
              f"{rep['routes']} route answers (the source's {rep['source_routes']}), store {rep['store']}")
    elif args[:1] == ["store"] and len(args) == 2:
        print(json.dumps(store_key(Path(args[1]))))
    elif args[:1] == ["check"] and len(args) in (4, 5):
        ok, text = check(Path(args[1]), Path(args[2]), args[3], Path(args[4]) if len(args) == 5 else None)
        print(text)
        sys.exit(0 if ok else 1)
    else:
        raise SystemExit(__doc__)
