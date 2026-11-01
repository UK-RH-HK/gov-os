"""Probe (not a test): the store's tables after a cold rebuild of a planted tree, and cold-vs-cold stability."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests/acceptance/W2-122"))
import w2_122_support as S

work = Path(tempfile.mkdtemp(prefix="w2122-probe-"))
box = S.make_box(work)
end = S.OllamaStandIn()
try:
    env = S.environment(box, end.host)
    base = S.make_base(box)
    run = S.built(base, env)
    print("base result keys:", sorted(run.result))
    print("stores:", json.dumps(run.result.get("stores")))
    print("embed texts:", len(end.embedded), "requests:", end.embed_requests)
    print("sample text:", end.embedded[:2])
    tables = S.store_tables(base)
    for name, (cols, rows) in tables.items():
        print(name, cols, len(rows), rows[:1][0][:300] if rows else None)
    tree = S.make_tree(box, base)
    end.forget()
    a = S.built(tree, env)
    snap_a = S.snapshot(tree, a)
    print("tree embed texts:", len(end.embedded))
    S.remove_store(tree)
    b = S.built(tree, env)
    snap_b = S.snapshot(tree, b)
    print("cold vs cold:", S.diff_tables(snap_a["tables"], snap_b["tables"]), snap_a["digest"] == snap_b["digest"],
          snap_a["stores"] == snap_b["stores"])
    print("seconds", a.seconds, b.seconds)
    print("rebuild dir:", sorted(p.name for p in (tree / ".gov-runtime").rglob("*"))[:40])
    r = S.rebuild(tree, env, "--seed", str(base))
    print("seed today:", r.returncode, r.stdout[-400:], r.stderr[-400:])
finally:
    end.close()
print("work:", work)
