"""List every cache.db under ~/gov-os-runs/D4B: its meta, memo and score counts (read-only; counts only)."""
import sqlite3
from pathlib import Path

root = Path.home() / "gov-os-runs" / "D4B"
for db_path in sorted(root.rglob("cache.db")):
    try:
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        meta = dict(db.execute("SELECT k, v FROM meta").fetchall()) if "meta" in tables else {}
        memo = db.execute("SELECT COUNT(*) FROM memo").fetchone()[0] if "memo" in tables else "-"
        score = db.execute("SELECT COUNT(*) FROM score").fetchone()[0] if "score" in tables else "-"
        db.close()
    except sqlite3.Error as error:
        print(f"{db_path}: {error}")
        continue
    rm = meta.get("rerank_model", "-")
    rm2 = meta.get("rerank_model2", "")
    print(f"{db_path.relative_to(root)}\tmemo {memo}\tscore {score}\tmodel {rm.split('@')[0]}"
          f"{(' + ' + rm2.split('@')[0]) if rm2 else ''}\tkeys {meta.get('memo_keys', '-')}\tstore {meta.get('store', '-')[:90]}")
