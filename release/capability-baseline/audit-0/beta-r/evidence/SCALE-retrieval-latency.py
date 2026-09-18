"""Scale datapoint for qualification planning (chaos/scale/soak column of the coverage matrix; NOT a Phase-2 gate).

Measures full-index time and per-query latency by route as the corpus grows (N synthetic markdown documents, three
sections each), using the kernel-default embedder. The semantic route scores every stored vector per query
(retrieval/mod.rs: SELECT ... FROM vectors, JSON-decoded, cosine in a loop), so latency is expected to grow linearly.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

words = ("settlement ledger quote carrier refund invoice reconcile gateway cache batch export window drift cents "
         "tariff zone weight parcel customs manifest route depot courier").split()


def doc(i):
    w = lambda k: " ".join(words[(i * 7 + j * 3 + k) % len(words)] for j in range(40))  # noqa
    return f"# Operations note {i}\n\nSummary {w(0)}.\n\n## Detail A\n\n{w(1)}\n\n## Detail B\n\n{w(2)} marker-{i}.\n"


results = []
for n in (200, 1000, 3000):
    files = {f"docs/notes/note-{i:05d}.md": doc(i) for i in range(n)}
    root, g = build_rich(f"scale-{n}", extra_files=files)
    t0 = time.time()
    rb = g.ok("rebuild-memory", show=False)
    t_index = time.time() - t0
    lat = {}
    for route, qq in [("semantic", "reconcile the carrier refund drift"), ("lexical", "tariff zone parcel customs"),
                      ("structured", "REQ-0001"), ("default", "why do refunds drift during settlement")]:
        args = ["memory", "query", qq, "--k", "8"] + ([] if route == "default" else ["--route", route])
        ts = []
        for _ in range(3):
            t1 = time.time()
            r = g.ok(*args, show=False)
            ts.append(time.time() - t1)
        lat[route] = (round(min(ts) * 1000), r["latency_ms"])
    row = {"docs": n, "chunks": rb["counts"]["chunks"], "vectors": rb["counts"]["vectors"], "index_s": round(t_index, 1),
           "latency_ms_wall_and_reported": lat, "db_bytes": (root / ".governance-runtime/state.db").stat().st_size}
    results.append(row)
    log(json.dumps(row))
log("")
log("vectors vs semantic-route latency (reported ms):", [(r["vectors"], r["latency_ms_wall_and_reported"]["semantic"][1]) for r in results])
summary()
