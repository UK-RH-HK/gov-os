"""C6 Temporal memory (Contract v3 lines 261-266): what changed / when / why / causal decision / supersession lineage.

A governed change (CIT-P -> gate -> CIT-E) to REQ-0001, a governed task close, and an UNGOVERNED direct commit are made;
for each facet the probe asks the product (records, `gov cit show`, `gov memory graph`, `gov memory query`) and
records what it can and cannot answer. Git history is also checked: does the fabric read it?
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("c6")
g.ok("rebuild-memory")
man0 = json.loads((root / "governance/generated/index-manifest.json").read_text())

section("governed change: CIT-P / gate / CIT-E on REQ-0001")
mf = BASE / "c6-manifest.json"
mf.write_text(json.dumps([{"op": "set_field", "target": "REQ-0001", "field": "statement",
                           "value": "The ledger computes order totals as exact integer cents; totals above 10^12 cents are rejected."}]))
c = g.ok("cit", "propose", "--proposal", "Bound order totals to 10^12 cents after overflow incident INC-77",
         "--trigger", "acceptance_criteria_change", "--targets", "REQ-0001", "--manifest", str(mf))
cid = c["id"]
sim = g.ok("cit", "simulate", cid)
gate = sim.get("human_gate")
log("simulate: radius", sim["impact"]["radius"], "human_gate_required", sim["impact"]["human_gate_required"], "gate", gate)
if gate:
    g.ok("gate", "present", gate)
    g.ok("decide", gate, "--option", "A", "--by", "owner", "--rationale", "overflow incident INC-77 requires a bound")
    g.ok("cit", "approve", cid, "--by", "owner", "--method", "human")
else:
    g.ok("cit", "approve", cid, "--by", "orchestrator", "--method", "auto")
ex = g.ok("cit", "execute", cid)
commit_all(root, "CIT executed")
show = g.ok("cit", "show", cid)
log("cit show keys:", sorted(show.keys()))
log("journal:", show.get("journal"))
log("execution:", {k: show.get("execution", {}).get(k) for k in ["started", "finished", "result", "gate", "decision", "propagation"]})
req = yaml.safe_load((root / "spec/requirements/REQ-0001.yaml").read_text())
log("REQ-0001 after CIT: updated=", req.get("updated"), "statement=", req.get("statement"))
man1 = json.loads((root / "governance/generated/index-manifest.json").read_text())
h0 = man0["artifacts"]["spec/requirements/REQ-0001.yaml"]["content_hash"]
h1 = man1["artifacts"]["spec/requirements/REQ-0001.yaml"]["content_hash"]
log("index-manifest content_hash REQ-0001 before/after:", h0[:16], h1[:16])

section("C6-b1 what changed")
touched = show.get("execution", {}).get("propagation", {}).get("touched", [])
log("CIT touched paths:", touched, "; mutation_manifest:", show.get("mutation_manifest"))
check("C6-b1", "spec/requirements/REQ-0001.yaml" in touched and h0 != h1,
      "a governed change records exactly what changed (CIT manifest + touched paths) and the index manifest reflects the new content hash")

section("C6-b2 when")
times = [e.get("at") for e in show.get("journal", [])]
log("journal timestamps:", times, "execution started/finished:", show["execution"].get("started"), show["execution"].get("finished"))
check("C6-b2", len(times) >= 3 and show["execution"].get("finished"), "timestamps of proposal/simulation/approval/execution are recorded")

section("C6-b3 why")
why = show.get("proposal")
rq = g.ok("memory", "query", "why was the order total bounded after the overflow incident", "--k", "6")
log("CIT proposal:", why)
log("retrieval hits:", [(h["artifact_id"], h["record_type"]) for h in rq["hits"]])
check("C6-b3", "INC-77" in (why or "") and any(h["artifact_id"] == cid for h in rq["hits"]),
      "the reason for the change is recorded on the transaction and retrievable by a why-question")

section("C6-b4 causal decision")
appr = show.get("approval", {})
did = appr.get("decision") or show.get("decision")
log("approval:", appr)
dec = g.ok("memory", "query", did, show=False) if did else {"hits": []}
log("decision record:", did, "retrievable:", [h["artifact_id"] for h in dec["hits"]][:3])
nb = g.ok("memory", "graph", "REQ-0001", "--depth", "2")
log("gov memory graph REQ-0001 --depth 2:", [(n["via"], n["node"], n["from"]) for n in nb])
linked = any(n["node"] == cid for n in nb) and any(n["node"] == did for n in nb)
check("C6-b4", bool(did) and linked, "the causal decision behind the change is recorded and navigable from the changed artefact (REQ-0001 -> CIT -> decision)")

section("C6-b5 supersession / version lineage")
nb2 = g.ok("memory", "graph", "D-0101", "--depth", "1")
log("gov memory graph D-0101:", [(n["via"], n["node"]) for n in nb2])
rh = g.ok("memory", "query", "D-0101", "--include-historical", show=False)
log("D-0101 hit flags:", [(h["artifact_id"], h["status"], h["flags"]) for h in rh["hits"] if h["artifact_id"] == "D-0101"][:1])
check("C6-b5", any(n["node"] == "D-0102" and "SUPERSEDES" in n["via"] for n in nb2)
      and any("superseded_by:D-0102" in h["flags"] for h in rh["hits"] if h["artifact_id"] == "D-0101"),
      "supersession lineage (D-0101 superseded by D-0102) is stored and surfaced on retrieval")

section("governed task close: when/what/why on the report")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Reject oversize totals", "--feature", "F-0001",
         "--status", "READY", "--allowed", "src/**,tests/**", "--fields", json.dumps({"requirements": ["REQ-0001"]}))
tid = t["id"]
g.ok("task", "claim", tid)
write(root, "src/app/models.py", (root / "src/app/models.py").read_text() + "\n\nMAX_TOTAL_CENTS = 10 ** 12\n")
rep = BASE / "c6-report.json"
rep.write_text(json.dumps({"task": tid, "outcome": "success", "work_completed": "Added MAX_TOTAL_CENTS bound per CIT " + cid,
                           "files_changed": ["src/app/models.py"], "evidence": ["pytest -q"], "tests": {"status": "passed"},
                           "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "none"}))
g.ok("rebuild-memory", "--incremental", show=False)
cl = g.ok("task", "close", tid, "--report", str(rep))
rpt = yaml.safe_load((root / f"spec/reports/{cl['report']}.yaml").read_text())
log("report:", {k: rpt.get(k) for k in ["task", "session", "role", "work_completed", "files_changed", "observed_files_changed", "created"]})
log("task closed_at:", yaml.safe_load((root / f"spec/tasks/{tid}.yaml").read_text()).get("closed_at"))
commit_all(root, "task closed")

section("ungoverned direct commit: what does the fabric know?")
write(root, "config/settings.yaml", (root / "config/settings.yaml").read_text().replace("settlement_window_minutes: 90", "settlement_window_minutes: 120"))
commit_all(root, "Extend settlement window to 120 minutes because processor batches run late (INC-91)")
g.ok("rebuild-memory", "--incremental", show=False)
rq2 = g.ok("memory", "query", "why was the settlement window extended to 120 minutes INC-91", "--k", "6")
log("hits:", [(h["artifact_id"], h["section"]) for h in rq2["hits"]])
art = q(root, "SELECT content_hash, repo_commit, indexed_at FROM artifacts WHERE path='config/settings.yaml'")
log("artifact row (content_hash, repo_commit at index time, indexed_at):", art)
log("git log (outside the fabric):", git(root, "log", "-1", "--format=%h %ad %s", "--", "config/settings.yaml"))
knows_why = any("INC-91" in json.dumps(h) for h in rq2["hits"])
check("C6-ungoverned-why", knows_why, "the reason for an ungoverned commit (commit message) is available through the fabric")
log("NOTE: the runtime never reads git log/diff/blame (grep of runtime/src shows only rev-parse/ls-files/mv/rm)")
summary()
