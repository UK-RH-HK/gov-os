"""E0b (E0-DECLARATION plan step 3): a score cache seeded from kept caches' scores only, the stored route answers
dropped. Scores are keyed by (model, question, text), a pointwise cross-encoder's score of a text, so they carry to a
new clone; route answers are a store's and never do (rx.py's store key).

    python3 seed_scores.py <new cache folder> <kept cache folder> [<kept cache folder> ...]

Every source must mark the same ``rerank_model``; the new cache gets that mark, ``memo_keys`` ``store`` (rx.py's
current key form) and no route answer. The union of the sources' score rows is written; a key two sources score
differently keeps the first source's and is counted (``conflicts``). The new folder must not hold a cache already.
Prints counts only (rows per source, rows written, conflicts); no question or text is read or written.
"""
import sqlite3
import sys
from pathlib import Path


def seed(dest: Path, sources: list[Path]) -> dict:
    if (dest / "cache.db").exists():
        raise SystemExit(f"seed_scores: {dest / 'cache.db'} exists: refused (a new folder)")
    if not sources:
        raise SystemExit("seed_scores: name at least one kept cache")
    model, rows, per = None, {}, {}
    conflicts = 0
    for src in sources:
        db = sqlite3.connect(f"file:{src / 'cache.db'}?mode=ro", uri=True)
        try:
            mark = db.execute("SELECT v FROM meta WHERE k = 'rerank_model'").fetchone()
            if mark is None:
                raise SystemExit(f"seed_scores: {src} marks no rerank_model: refused")
            if model is not None and mark[0] != model:
                raise SystemExit(f"seed_scores: {src} holds {mark[0]}, not {model}: refused (one model per cache)")
            model = mark[0]
            got = db.execute("SELECT k, s FROM score").fetchall()
        finally:
            db.close()
        per[str(src)] = len(got)
        for k, s in got:
            if k in rows:
                conflicts += rows[k] != s
            else:
                rows[k] = s
    dest.mkdir(parents=True, exist_ok=True)
    out = sqlite3.connect(dest / "cache.db")
    try:
        out.execute("CREATE TABLE memo (k TEXT PRIMARY KEY, v BLOB)")
        out.execute("CREATE TABLE score (k TEXT PRIMARY KEY, s REAL)")
        out.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
        out.execute("INSERT INTO meta VALUES ('rerank_model', ?)", (model,))
        out.execute("INSERT INTO meta VALUES ('memo_keys', 'store')")
        out.executemany("INSERT INTO score VALUES (?, ?)", sorted(rows.items()))
        out.commit()
    finally:
        out.close()
    return {"model": model, "per_source": per, "written": len(rows), "conflicts": conflicts}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    report = seed(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]])
    print(f"seed_scores: {report['written']} score rows of {report['model']} written to {sys.argv[1]}; "
          f"conflicts {report['conflicts']}")
    for src, n in report["per_source"].items():
        print(f"  {n} rows from {src}")
