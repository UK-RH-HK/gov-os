"""C9 Working memory / context packet (Contract v3 lines 285-292).

b1 small reproducible, b2 deterministic authority block, b3 retrieved supplementary block, b4 bounded size (tight
CONTEXT_POLICY.max_packet_chars; deterministic block alone over budget), b5 provenance/citations (can each cited hit be
re-resolved to path + content hash + index snapshot?), b6 duplicate suppression (same artefact, copied content,
parent/child overlap, cross-block repeats), b7 active-vs-historical separation.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich, y  # noqa

root, g = build_rich("c9")
# a verbatim copy of the runbook under another name (renamed-duplicate challenge)
write(root, "docs/runbook-copy.md", (root / "docs/runbook.md").read_text())
y(root, "spec/decisions/D-0103.yaml", {"id": "D-0103", "type": "decision", "title": "Reconciliation runs nightly", "status": "ACTIVE",
  "question": "When does reconciliation run?", "rationale": "Nightly reconciliation after the settlement window keeps totals auditable.",
  "affects": ["F-0001"], "supersedes": [], "superseded_by": ""})
y(root, "spec/decisions/D-0104.yaml", {"id": "D-0104", "type": "decision", "title": "Reconciliation runs hourly (stale ACTIVE)", "status": "ACTIVE",
  "question": "When does reconciliation run?", "rationale": "Hourly reconciliation.", "affects": ["F-0001"]})
d103 = yaml.safe_load((root / "spec/decisions/D-0103.yaml").read_text())
d103["supersedes"] = ["D-0104"]
y(root, "spec/decisions/D-0103.yaml", d103)
commit_all(root, "c9 content")
g.ok("rebuild-memory")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Implement nightly reconciliation of order totals", "--feature", "F-0001",
         "--status", "READY", "--allowed", "src/**,tests/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
                                                                                        "required_skills": ["SKL-BACKEND-IMPL"]}))
tid = t["id"]
g.ok("rebuild-memory", "--incremental", show=False)
p1 = g.ok("context", "compile", tid)
p2 = g.ok("context", "compile", tid)
p3 = g.as_session("S-other").ok("context", "compile", tid)
det, ret = p1["deterministic_authority"], p1["retrieved_intelligence"]

section("C9-b1 small reproducible current-task context")
log("packet chars:", p1["chars"], "| det hash run1/run2/other-session:", p1["deterministic_hash"][:16], p2["deterministic_hash"][:16], p3["deterministic_hash"][:16])
log("packet_hash run1/run2:", p1["packet_hash"][:16], p2["packet_hash"][:16], "| file:", (root / f".governance-runtime/context/{tid}.json").exists())
check("C9-b1", p1["deterministic_hash"] == p2["deterministic_hash"] == p3["deterministic_hash"] and p1["packet_hash"] == p2["packet_hash"]
      and p1["chars"] < 60000 and p1["task"] == tid, "the packet is task-scoped, bounded and reproducible (identical hashes across compiles and sessions)")

section("C9-b2 deterministic authority block")
pol = g.ok("policy", "effective", "CONTEXT_POLICY")["effective"]
need = pol["deterministic_authority_fields"]
missing = [f for f in need if f not in det]
log("deterministic fields required by CONTEXT_POLICY:", need)
log("missing:", missing, "| authority layers:", [l["name"] for l in det["authority_layers"]])
log("governing requirements / active decisions / scenarios / allowed / prohibited:", [r["id"] for r in det["governing_requirements"]],
    [d["id"] for d in det["active_decisions"]], [s["id"] for s in det["scenarios"]], det["allowed_writes"], det["prohibited_writes"])
check("C9-b2", not missing and det["governing_requirements"] and det["allowed_writes"] and "governance/kernel/**" in det["prohibited_writes"],
      "a hash-stable deterministic authority block carries every policy-required authority field")

section("C9-b3 retrieved supplementary intelligence")
rneed = pol["retrieved_fields"]
rmissing = [f for f in rneed if f not in ret]
log("retrieved fields required by CONTEXT_POLICY:", rneed, "| missing:", rmissing)
log("query:", ret["query"], "| strategy:", ret["retrieval_strategy"], "| routes:", ret["routes"], "| index snapshot:", ret["index_snapshot"])
log("ranked evidence:", [(e["artifact_id"], e["routes"]) for e in ret["ranked_evidence"]])
log("semantic-route hits inside ranked_evidence:", [e["artifact_id"] for e in ret["ranked_evidence"] if "semantic" in e["routes"]])
log("lessons_failures:", [e["artifact_id"] for e in ret["lessons_failures"]], "| code refs:", ret["code_references"][:5])
check("C9-b3", ret["ranked_evidence"] and ret["index_snapshot"]["manifest_hash"] and "deterministic_authority" in p1 and "retrieved_intelligence" in p1,
      "a separate retrieved block carries query, strategy, index snapshot, ranked evidence (incl. semantic hits), lessons/failures, code refs")
check("C9-b3-policy-fields", not rmissing, "every CONTEXT_POLICY.retrieved_fields entry is present in the packet")

section("C9-b4 bounded size")
det_len = len(json.dumps(det, separators=(",", ":")))
budget = det_len + 2500
log("deterministic block ~chars:", det_len, "| full packet chars:", p1["chars"], "| budget chosen:", budget)
set_overrides(root, {"CONTEXT_POLICY.max_packet_chars": budget})
commit_all(root, "tight packet budget")
ov = g.ok("policy", "overrides")
log("override applied/refused:", [o for o in ov["applied"] if "CONTEXT" in o.get("policy", "")], [o for o in ov["refused"] if "CONTEXT" in o.get("policy", "")])
pb = g.ok("context", "compile", tid)
same_mandatory = all([r["id"] for r in pb["deterministic_authority"][k]] == [r["id"] for r in det[k]]
                     for k in ("governing_requirements", "active_decisions", "scenarios", "interfaces"))
log(f"budget {budget}: chars", pb["chars"], "| truncated_slices:", pb["retrieved_intelligence"].get("truncated_slices"),
    "| mandatory authority content unchanged:", same_mandatory, "| warning:", pb.get("warning"),
    "| (deterministic hash differs only because the applied override is itself listed in authority layer 3)")
set_overrides(root, {"CONTEXT_POLICY.max_packet_chars": 1500})
commit_all(root, "budget below the deterministic block")
pt = g.run("context", "compile", tid)
ptb = body_of(pt)
log("budget 1500 (below the deterministic block):", pt.get("ok"), (pt.get("error") or {}).get("code"), "chars", ptb.get("chars"), "| warning:", ptb.get("warning"),
    "| retrieved slices left:", len(ptb.get("retrieved_intelligence", {}).get("ranked_evidence", [])))
set_overrides(root, {"CONTEXT_POLICY.max_packet_chars": 60000})
commit_all(root, "budget restored")
check("C9-b4", pb["chars"] <= budget + 500 and pb["retrieved_intelligence"].get("truncated_slices", 0) > 0 and same_mandatory and not pb.get("warning"),
      "packet size is bounded by dropping retrieved slices first; the deterministic block is never truncated")
check("C9-b4-overbudget", not pt.get("ok") or bool(ptb.get("warning")),
      "a deterministic block larger than the budget is surfaced explicitly (refusal or warning), not silently cut")

section("C9-b5 provenance / citations")
man = json.loads((root / "governance/generated/index-manifest.json").read_text())
ok_prov = True
for e in ret["ranked_evidence"]:
    m = man["artifacts"].get(e["path"])
    good = m is not None and m.get("artifact_id") == e["artifact_id"] and e.get("section") is not None
    ok_prov &= good
    log(f"  {e['artifact_id']:<34} path={e['path']:<45} section={e['section'][:30]!r:<34} manifest_hash_entry={'yes' if m else 'NO'} "
        f"content_hash={(m or {}).get('content_hash', '')[:12]} status={e['status']} state_class={e['state_class']}")
log("per-hit fields present:", sorted(ret["ranked_evidence"][0].keys()))
log("index snapshot manifest hash == live manifest hash:", ret["index_snapshot"]["manifest_hash"] == man["manifest_hash"])
check("C9-b5", ok_prov and ret["index_snapshot"]["manifest_hash"] == man["manifest_hash"] and p1.get("packet_hash"),
      "every cited slice resolves through the pinned index snapshot to artefact id, path, section, content hash and authority status")

section("C9-b6 duplicate suppression")
aids = [e["artifact_id"] for e in ret["ranked_evidence"]]
per = {a: aids.count(a) for a in set(aids)}
log("ranked_evidence artefact multiplicity:", per)
rq = g.ok("memory", "query", "reconciliation procedure settlement window operators rerun export", "--k", "10")
hits = [(h["artifact_id"], h["chunk_id"], h["level"]) for h in rq["hits"]]
log("query hits:", hits)
both = "file:docs/runbook.md" in [h[0] for h in hits] and "file:docs/runbook-copy.md" in [h[0] for h in hits]
texts = {}
for h in rq["hits"]:
    texts.setdefault(h["excerpt"].strip(), []).append(h["artifact_id"])
dup_text = {k[:60]: v for k, v in texts.items() if len(v) > 1}
log("identical excerpts returned more than once:", dup_text)
cross = set(aids) & {e["artifact_id"] for e in ret["lessons_failures"]}
log("artefacts repeated across ranked_evidence and lessons_failures:", cross)
check("C9-b6-per-artifact-cap", max(per.values()) <= 2, "at most two slices per artefact (per-artefact de-duplication)")
check("C9-b6-content-dups", not both and not dup_text, "verbatim-duplicate content from a copied/renamed file is suppressed")

section("C9-b7 active vs historical separation")
act = [d["id"] for d in det["active_decisions"]]
conf = [(d["id"], d.get("authority_flag"), d.get("superseded_by")) for d in det["conflicting_decisions"]]
log("active_decisions:", act, "| conflicting_decisions:", conf)
hist_in_ret = [e for e in ret["ranked_evidence"] if e["status"] in ("SUPERSEDED", "HISTORICAL") or any("superseded_by" in f for f in e["flags"])]
log("historical/superseded slices in retrieved block:", hist_in_ret)
check("C9-b7", "D-0101" not in act and "D-0104" not in act and ("D-0104", "UNKNOWN_OR_CONFLICTING", "D-0103") in conf and not hist_in_ret,
      "superseded authority is excluded from the active block, superseded-but-ACTIVE is flagged as conflicting, historical slices are not retrieved")
summary()
