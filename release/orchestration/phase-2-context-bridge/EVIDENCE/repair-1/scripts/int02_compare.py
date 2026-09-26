"""BR-AR-0028 check 2: compare two from-clean stores built with the pinned view.

Two independent comparisons:
  (1) the stores' own build manifests (manifest.json): every registered layer digest, pins, view, config shas,
      bridge code tree, and manifest_sha256 -- the code under test's own digests;
  (2) an INDEPENDENT per-TABLE digest computed here, straight from SQLite (every table in sqlite_master, rows
      ordered by every column, each value repr'd), opened read-only -- this covers tables no registered layer
      digests (occurrence_distinct_path, lineage_unresolved, store_meta, ...), without trusting any govbridge code.
Usage: $PY int02_compare.py <storeA> <storeB>
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def table_digests(store: Path) -> dict:
    db = store / "store.db"
    wal = store / "store.db-wal"
    uri = f"file:{db}?mode=ro" + ("" if wal.exists() else "&immutable=1")
    conn = sqlite3.connect(uri, uri=True)
    out = {}
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table') ORDER BY name").fetchall()]
        for t in tables:
            try:
                cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")').fetchall()]
                order = ", ".join(f'"{c}"' for c in cols) if cols else "rowid"
                h = hashlib.sha256()
                n = 0
                for row in conn.execute(f'SELECT * FROM "{t}" ORDER BY {order}'):
                    h.update(repr(row).encode("utf-8"))
                    h.update(b"\x1e")
                    n += 1
                out[t] = {"rows": n, "sha256": h.hexdigest()}
            except sqlite3.Error as e:
                out[t] = {"error": str(e)}
    finally:
        conn.close()
    return out


def main():
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    ma = json.loads((a / "manifest.json").read_text())
    mb = json.loads((b / "manifest.json").read_text())
    report = {"store_a": str(a), "store_b": str(b)}
    la, lb = ma["manifest"]["layers"], mb["manifest"]["layers"]
    report["manifest_sha256"] = {"a": ma["manifest"]["manifest_sha256"], "b": mb["manifest"]["manifest_sha256"],
                                 "equal": ma["manifest"]["manifest_sha256"] == mb["manifest"]["manifest_sha256"]}
    report["layers"] = {name: {"a": la.get(name), "b": lb.get(name), "equal": la.get(name) == lb.get(name)}
                        for name in sorted(set(la) | set(lb))}
    report["layer_errors"] = {n: v.get("error") for n, v in la.items() if isinstance(v, dict) and v.get("error")}
    for key in ("view", "config_sha256", "bridge_code_tree", "pins", "coverage"):
        report[f"{key}_equal"] = ma["manifest"].get(key) == mb["manifest"].get(key)
    report["fingerprint_equal"] = ma.get("fingerprint") == mb.get("fingerprint")
    report["fingerprint_refs"] = ma.get("fingerprint", {}).get("refs")
    report["fingerprint_history_count"] = len(ma.get("fingerprint", {}).get("history") or [])
    report["fingerprint_config_files"] = sorted((ma.get("fingerprint", {}).get("config_sha256") or {}).keys())
    ta, tb = table_digests(a), table_digests(b)
    report["tables"] = {t: {"a": ta.get(t), "b": tb.get(t), "equal": ta.get(t) == tb.get(t)}
                        for t in sorted(set(ta) | set(tb))}
    report["tables_differing"] = [t for t, v in report["tables"].items() if not v["equal"]]
    report["layers_differing"] = [n for n, v in report["layers"].items() if not v["equal"]]
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0 if (report["manifest_sha256"]["equal"] and not report["layers_differing"]) else 1


if __name__ == "__main__":
    sys.exit(main())
