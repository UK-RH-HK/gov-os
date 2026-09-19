"""DERIVED COPY (P2-AR-0027, WS-6 round 2) of release/capability-baseline/audit-0/beta-r/evidence/D5-model-selection.py.
The audit-of-record probe is run UNEDITED as well (evidence/after/beta-r.D5-model-selection.out); it stops at D5-b5
because `gov memory select` now applies a profile change only after the change-control gate for its radius is answered
(BC-P2-30 / A0-D5-02), and the probe never answers a gate. This copy changes ONLY:
  (1) `governed_select()`: when select returns applied=false with a human gate, the owner answers it through the
      human channel (WS-3 test-material signer repair-1/ws03/evidence/hc_owner.py, published seed 7; a standalone
      anchor is provisioned from outside the repository if the machine has none) and select is re-run with --gate;
  (2) D5-b6: `select builtin:8` without evidence is now REFUSED (the check's own wording: "select refuses an
      unbenchmarked candidate"), so it is run with g.run and the refusal code is checked; the regression-record check
      counts the audit records the governed select of D5-b5 wrote;
  (0) the helper library is imported from the audit of record's evidence directory (unedited);
  (3) one added line D5-b6-ungoverned-product reading the product's own ungoverned-profile report (rebuild report
      `retrieval_profile` and `gov memory profile`); the unedited audit-findings line is kept as it was.
Every other line is byte-identical to the audit of record.
"""
"""D5 Evidence-driven retrieval model selection (Contract v3 lines 342-348) — the core of the AC-7 determination.

Auditor-authored, token-overlap-free paraphrase queries are added to the held-out set so that the benchmark can
DISCRIMINATE candidates (the generated starter set is exact-id/path/symbol/literal only). Four candidates are
benchmarked (baseline, baseline@64d, an auditor-authored concept embedder, the same + a reranker) plus one unusable one.
Then selection / pinning / change governance are exercised, including the paths that bypass them.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[6] / "release/capability-baseline/audit-0/beta-r/evidence/lib"))  # (derived) the audit-of-record helper library, unedited
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("d5")

import os
import subprocess
import tempfile
HC = str(WT / "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")


def owner_answer(gid, option="A"):
    """(derived) the owner answers `gid` through the human channel (signed document), relayed by the orchestrator."""
    st = g.run("trust", "human-channel", show=False)
    if not (st.get("result") or {}).get("available"):
        d = tempfile.mkdtemp(prefix="p2ar0027-admin-")
        af = os.path.join(d, "anchor.json")
        subprocess.run([sys.executable, HC, "anchor", af, "7"], check=True, capture_output=True)
        g.ok("trust", "human-channel", "--provision", af, show=False)
    pr = g.ok("gate", "present", gid, show=False)["gate"]
    d = tempfile.mkdtemp(prefix="p2ar0027-owner-")
    af = os.path.join(d, f"answer-{gid}.json")
    subprocess.run([sys.executable, HC, "answer", af, gid, pr["gate_instance"], pr["package_sha256"], option], check=True, capture_output=True)
    return g.ok("decide", gid, "--option", option, "--answer-file", af)


def governed_select(*args):
    """(derived) select; if the change-control gate is pending, the owner answers it and select is re-run with --gate."""
    r = g.ok("memory", "select", *args)
    if r.get("applied") is False and r.get("human_gate"):
        log("(derived) change-control gate", r["human_gate"], "radius", r.get("impact_radius"), "-> owner answers A through the human channel")
        owner_answer(r["human_gate"])
        r = g.ok("memory", "select", *args, "--gate", r["human_gate"])
    return r

g.ok("rebuild-memory")
install_plugin(root, "concept_embedder.py", "concept-embedder", "embed")
install_plugin(root, "logging_reranker.py", "logging-reranker", "rerank")
install_plugin(root, "bad_dim_embedder.py", "bad-dim", "embed")
hf = root / "governance/tests/memory/heldout.yaml"
held = yaml.safe_load(hf.read_text())
PARA = [
    ("HQ-P1", "why do we keep cash as whole units instead of imprecise decimals", ["D-0102"]),
    ("HQ-P2", "memoize the order lookups so responses are quicker", ["EXP-0001"]),
    ("HQ-P3", "which feed do we use when balancing funds", ["RES-0101"]),
    ("HQ-P4", "imprecise decimal amounts caused drift", ["L-0101"]),
    ("HQ-P5", "stored currency must be exact integer amounts", ["REQ-0001"]),
]
for qid, text, exp in PARA:
    held["queries"].append({"id": qid, "category": "semantic_paraphrase", "query": text, "expected_refs": exp, "forbidden": ["D-0101"], "k": 5, "route": "semantic"})
hf.write_text(yaml.safe_dump(held, sort_keys=False))
commit_all(root, "auditor paraphrase queries + candidate plugins")
g.ok("rebuild-memory", "--incremental", show=False)

section("D5-b3 golden / held-out retrieval queries")
cats = {}
for qq in held["queries"]:
    cats[qq.get("category")] = cats.get(qq.get("category"), 0) + (0 if qq.get("pending") else 1)
log("held-out file:", hf.relative_to(root), "| non-pending queries by category:", cats, "| pending:", sum(1 for qq in held["queries"] if qq.get("pending")))
v = g.run("memory", "verify")
vb = body_of(v)
log("gov memory verify (current baseline):", vb.get("status"), "recall", vb.get("recall_at_k"), "mrr", vb.get("mrr"), "failed:", [r["id"] for r in vb.get("results", []) if not r["pass"]])
check("D5-b3", cats.get("semantic_paraphrase", 0) >= 5 and vb.get("measured"), "held-out retrieval queries exist (generated starter + authored paraphrase set) and are measured")

section("D5-b1/b2/b4 benchmark: multiple candidates compared on the held-out set")
b = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:64", "--candidate", "plugin:concept-embedder:256",
         "--candidate", "plugin:concept-embedder:256+rerank:logging-reranker", "--candidate", "plugin:bad-dim:64", "--record")
for r in b["rows"]:
    if r.get("usable"):
        log(f"  {r['candidate']:<52} recall@k={r['recall_at_k']:.3f} mrr={r['mrr']:.3f} p@k={r['precision_at_k']:.3f} stale={r['stale_hit_rate']} "
            f"superseded={r['superseded_hit_rate']} forbidden={r['forbidden_violations']} sym={r['symbol_recall']} lat={r['avg_query_latency_ms']:.2f}ms "
            f"index_ms={r['index_ms']} vectors={r['vectors']} dims={r['dimensions']}")
        log(f"      by category: {[(c['category'], round(c['recall'], 2)) for c in r['by_category']]}")
    else:
        log(f"  {r['candidate']:<52} UNUSABLE: {r.get('error', '')[:160]}")
log("recommended:", b["recommended"], "| research record:", b.get("research_record"))
metric_keys = {"recall_at_k", "mrr", "precision_at_k", "stale_hit_rate", "avg_query_latency_ms", "index_ms", "vectors"}
usable = [r for r in b["rows"] if r.get("usable")]
check("D5-b1", b.get("research_record") and (root / f"spec/research/{b['research_record']}.yaml").exists(),
      "a benchmark mechanism exists and records its measurements as a governed research record")
check("D5-b2", len(usable) == 4 and len({r["recall_at_k"] for r in usable}) > 1 and any(not r.get("usable") for r in b["rows"]),
      "several embedders/runtimes (+reranker) are compared side by side; an unusable candidate is reported, not silently dropped")
check("D5-b4", all(metric_keys <= set(r.keys()) for r in usable), "Recall@K, MRR, precision, stale-hit, latency and resource (index time, vector count/dims) metrics exist per candidate")
log("resource metrics present:", sorted(k for k in usable[0] if k in ("index_ms", "vectors", "dimensions", "memory_mb", "disk_bytes", "rss_mb")),
    "(no memory/disk footprint measurement)")

section("D5-b5 selected embedder / reranker revisions are pinned")
res = b.get("research_record")
held_before = sorted(p.name for p in (root / "spec/audits").glob("AUD-*.yaml"))  # (derived) around the governed select
sel = governed_select("plugin:concept-embedder:256+rerank:logging-reranker", "--research", res, "--by", "owner")
held_after = sorted(p.name for p in (root / "spec/audits").glob("AUD-*.yaml"))  # (derived)
dec = yaml.safe_load((root / f"spec/decisions/{sel['decision']}.yaml").read_text())
pp = yaml.safe_load((root / "governance/project/PROJECT_POLICY.yaml").read_text())
man = json.loads((root / "governance/generated/index-manifest.json").read_text())
log("select ->", sel)
log("decision:", {k: dec.get(k) for k in ["id", "title", "chosen_option", "approved_by", "approved_by_role", "human_approved", "impact_radius", "derived_from"]})
log("decision options (alternatives with measurements):", dec.get("options"))
log("overlay pins:", pp.get("policy_overrides"))
log("manifest embedder / reranker:", man["embedder"], man["reranker"])
check("D5-b5", man["embedder"]["id"] == "concept-embedder" and man["reranker"]["provider"] == "logging-reranker" and dec.get("options"),
      "the selection is pinned (overlay + manifest) through a decision that carries the measured alternatives")
# is the pinned REVISION bound to the implementation actually used?
desc = yaml.safe_load((root / "governance/project/plugins/concept-embedder.yaml").read_text())
desc["version"] = "2"
write(root, "governance/project/plugins/concept-embedder.yaml", yaml.safe_dump(desc))
commit_all(root, "plugin descriptor now claims version 2; pin still says 1")
qv = g.run("memory", "query", "why integer cents", "--route", "semantic", "--k", "3")
fr = g.ok("memory", "freshness", show=False)
log("plugin revision changed (descriptor v2, pin v1): query ->", qv.get("ok"), (qv.get("error") or {}).get("code"), "| freshness pin_mismatch:", fr["pin_mismatch"])
log("reranker revision recorded in manifest:", man["reranker"], "vs plugin descriptor version:", yaml.safe_load((root / "governance/project/plugins/logging-reranker.yaml").read_text())["version"])
check("D5-b5-revision-bound", not qv.get("ok") or bool(fr["pin_mismatch"]),
      "the pinned embedder revision is bound to the implementation revision actually executed (a revision change is detected)")
desc["version"] = "1"
write(root, "governance/project/plugins/concept-embedder.yaml", yaml.safe_dump(desc))
commit_all(root, "restore descriptor version")

section("D5-b6 changing them requires governed migration / reindex / regression")
low = g.as_role("memory-engineer").run("memory", "select", "builtin:64", "--by", "memory-engineer")
log("select as memory-engineer (L2) ->", (low.get("error") or {}).get("code"))
# (a) governed path: does select run the regression after the reindex?
sel2 = g.run("memory", "select", "builtin:8", "--by", "orchestrator")  # (derived) refused: no evidence
dec2 = {}
vr = body_of(g.run("memory", "verify"))
log("select builtin:8 WITHOUT any research record ->", sel2, "| decision rationale:", dec2.get("rationale"), "| derived_from:", dec2.get("derived_from"),
    "| human_approved:", dec2.get("human_approved"))
log("audit/regression records created by select:", sorted(set(held_after) - set(held_before)), "| regression status after the switch (run manually):", vr.get("status"),
    "recall", vr.get("recall_at_k"))
# (b) ungoverned path: edit the pin directly
set_overrides(root, {"MEMORY_POLICY.embedding.provider": "hashed-ngram", "MEMORY_POLICY.embedding.dimensions": 16})
commit_all(root, "direct pin edit, no decision")
qd = g.run("memory", "query", "why integer cents")
rb = g.ok("rebuild-memory", "--incremental")
decs = sorted(p.name for p in (root / "spec/decisions").glob("D-*.yaml"))
aud = body_of(g.run("audit", "--no-persist"))
flag = [f["message"] for f in aud.get("findings", []) if any(w in f["message"].lower() for w in ("embed", "pin", "decision", "select"))]
log("direct pin edit: query before rebuild ->", (qd.get("error") or {}).get("code"), "| rebuild mode:", rb["mode"], "| decisions:", decs, "| audit findings about an ungoverned pin change:", flag)
check("D5-b6-reindex", (qd.get("error") or {}).get("code") == "EMBEDDER_MISMATCH" and rb["mode"] == "full", "a pin change cannot be used until the index is fully re-embedded")
check("D5-b6-authority", (low.get("error") or {}).get("code") == "AUTHORITY_DENIED", "selection is authority-gated (memory_select L3)")
check("D5-b6-evidence", (sel2.get("error") or {}).get("code") == "PROFILE_EVIDENCE_REQUIRED" and bool(yaml.safe_load((root / f"spec/decisions/{sel['decision']}.yaml").read_text()).get("derived_from")), "a pin change must be derived from benchmark evidence (select refuses an unbenchmarked candidate)")  # (derived)
check("D5-b6-regression", bool(set(held_after) - set(held_before)), "the governed switch runs/records the held-out regression after re-indexing")
check("D5-b6-ungoverned", bool(flag), "an embedder pin changed outside `gov memory select` (no decision) is flagged")
prof = g.ok("memory", "profile", show=False)  # (derived) the product's own report
log("(derived) rebuild report retrieval_profile:", rb.get("retrieval_profile"), "| gov memory profile:", {k: prof.get(k) for k in ("state", "decision", "message")})
check("D5-b6-ungoverned-product", (rb.get("retrieval_profile") or {}).get("state") in ("UNGOVERNED", "UNGOVERNED_CHANGE") and prof.get("state") in ("UNGOVERNED", "UNGOVERNED_CHANGE"), "(derived) the product reports the ungoverned pin change (rebuild report, gov memory profile)")
summary()
