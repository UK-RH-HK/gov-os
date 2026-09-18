"""C4 Lexical memory (Contract v3 lines 243-249).

For each facet: (1) the query as an agent would type it, through the DEFAULT router (no --route), and (2) the lexical
route in isolation (`--route lexical` / `--route lexical_exact`). The expected artefact must be returned; the routes
chosen are recorded. FTS5 table rows prove the lexical store holds the content.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

ROUTES_PY = '"""Refund HTTP routes."""\nfrom flask import Flask\n\napp = Flask(__name__)\n' + "".join(
    f"\n\n@app.route(\"/refunds/v{i}/<rid>\", methods=[\"POST\"])\ndef refund_v{i}(rid):\n    return {{\"rid\": rid, \"version\": {i}}}\n" for i in range(1, 7)
) + "\n\nREFUND_WINDOW_DAYS_SENTINEL = 45\n\nif __name__ == \"__main__\":\n    app.run(port=8088)\n"
root, g = build_rich("c4", extra_files={"src/app/refunds.py": ROUTES_PY})
g.ok("rebuild-memory")
tok = q(root, "SELECT value FROM meta WHERE key='lexical'")
log("lexical engine pin (runtime meta):", tok)
log("FTS rows:", q(root, "SELECT COUNT(*) FROM chunks_fts")[0][0])


def run(query, route=None, k=8):
    args = ["memory", "query", query, "--k", str(k)]
    if route:
        args += ["--route", route]
    r = g.ok(*args, show=False)
    return r["routes"], [h["artifact_id"] for h in r["hits"]]


def facet(bid, label, query, expected, iso_route="lexical"):
    section(f"{bid} {label}")
    rt, hits = run(query)
    rt2, hits2 = run(query, iso_route)
    log(f"query={query!r}")
    log(f"  default router: routes={rt} hits={hits}")
    log(f"  --route {iso_route}: hits={hits2}")
    d_ok = expected in hits
    i_ok = expected in hits2
    check(f"{bid}-router", d_ok, f"{label}: default routing returns {expected}")
    check(f"{bid}-lexical", i_ok, f"{label}: lexical store alone returns {expected}")
    return rt, hits


facet("C4-b1", "exact terms", "reconciliation", "file:docs/runbook.md")
facet("C4-b2", "identifiers (snake_case)", "compute_total", "file:src/app/models.py")
facet("C4-b2c", "identifiers (camelCase)", "formatCents", "file:src/web/format.ts")
facet("C4-b3", "filenames (bare)", "runbook.md", "file:docs/runbook.md")
facet("C4-b3b", "filenames (bare, source)", "ledger.rs", "file:src/core/ledger.rs")
facet("C4-b3p", "filenames (path)", "docs/runbook.md", "file:docs/runbook.md")
facet("C4-b4", "error strings (code)", "ERR_LEDGER_DRIFT_4711", "file:docs/runbook.md", "lexical_exact")
facet("C4-b4m", "error strings (message)", '"quantity must be non-negative"', "file:src/app/models.py", "lexical_exact")
facet("C4-b5k", "config keys", "max_retries_per_gateway", "file:config/settings.yaml")
facet("C4-b5a", "API names (route path)", '"/api/orders/:id"', "file:src/web/api.ts", "lexical_exact")
facet("C4-b5n", "API names (symbol)", "SqlOrderRepository", "file:src/web/api.ts")
facet("C4-b6", "literal phrases", '"compares the append-only ledger with the payment processor export"', "file:docs/runbook.md", "lexical_exact")

facet("C4-b6l", "literal phrase inside a record list field (acceptance criterion)", '"total_cents equals quantity times unit_cents"', "REQ-0001", "lexical_exact")
facet("C4-b6s", "literal phrase inside scenario steps", '"two orders are appended"', "SCN-0001", "lexical_exact")

section("C4 coverage: which non-empty source lines are held by NO chunk (lexical+semantic store)")
import sqlite3
cov_missing = {}
for f in ["src/app/refunds.py", "src/web/api.ts", "src/app/api.py", "src/app/models.py", "src/core/ledger.rs", "src/server/server.go"]:
    src = (root / f).read_text().splitlines()
    blob = "\n".join(r[0] for r in q(root, "SELECT text FROM chunks WHERE artifact_id=?", ("file:" + f,)))
    miss = [(i + 1, l.strip()) for i, l in enumerate(src) if l.strip() and l.strip() not in blob]
    cov_missing[f] = miss
    log(f"{f}: {len(src)} lines, {len(miss)} non-empty lines in no chunk: {miss}")
# tokens that occur ONLY on the unchunked lines (a fuzzy OR-of-subtokens match elsewhere in the file cannot satisfy them)
facet("C4-cov-q1", "module-level constant beyond the header (token only on line 37)", "SENTINEL", "file:src/app/refunds.py", "lexical_exact")
facet("C4-cov-q2", "trailing __main__ block literal (token only on line 40)", "8088", "file:src/app/refunds.py", "lexical_exact")
# (a decorator-path query is not discriminating: porter-stemmed tokens "refund v4" also occur in `def refund_v4`)
check("C4-coverage", not any(cov_missing.values()), "every non-empty source line is held by at least one chunk (no silent lexical blind spots)")

section("C4 negative control: exact literal does not match a near-miss")
rt, hits = run("ERR_LEDGER_DRIFT_4712")
log("routes:", rt, "hits:", hits)
check("C4-exactness", "file:docs/runbook.md" not in hits, "a near-miss literal (…4712) does not return the …4711 document")
summary()
