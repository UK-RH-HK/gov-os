"""AC-16 interactions owned by family beta: K2 <-> D1 (CIT-E triggers memory/index refresh) and D1 <-> W6 (index
staleness <-> upstream-change staleness propagation). Only the D1 side is graded here; K2/W6 behaviour is recorded.

K2-D1-1 governed record change -> CIT-E -> index refreshed + verified fresh, retrieval returns the new content.
K2-D1-2 CIT whose index refresh FAILS (pins an unavailable embedder) -> CIT-E verification -> rollback; index intact.
K2-D1-3 CIT that reclassifies a path (path map) -> CIT-E incremental refresh -> does the committed index reflect it?
D1-W6-1 ungoverned upstream edit -> index staleness detected, task close blocked until refresh.
D1-W6-2 after refresh: are downstream DONE tasks / previously compiled context packets flagged stale?
D1-W6-3 governed (CIT) upstream edit -> retest/staleness propagation + index refresh in one transaction.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("x-k2d1")
g.ok("rebuild-memory")


def run_cit(proposal, trigger, targets, manifest):
    mf = BASE / f"x-{abs(hash(proposal)) % 10**6}.json"
    mf.write_text(json.dumps(manifest))
    c = g.ok("cit", "propose", "--proposal", proposal, "--trigger", trigger, "--targets", targets, "--manifest", str(mf))
    cid = c["id"]
    sim = g.ok("cit", "simulate", cid, show=False)
    gate = sim.get("human_gate")
    if gate:
        g.ok("gate", "present", gate, show=False)
        g.ok("decide", gate, "--option", "A", "--by", "owner", show=False)
        g.ok("cit", "approve", cid, "--by", "owner", "--method", "human", show=False)
    else:
        g.ok("cit", "approve", cid, "--by", "orchestrator", "--method", "auto", show=False)
    ex = g.run("cit", "execute", cid)
    return cid, ex


section("K2-D1-1 governed change -> CIT-E refreshes the index")
h0 = json.loads((root / "governance/generated/index-manifest.json").read_text())["artifacts"]["spec/requirements/REQ-0001.yaml"]["content_hash"]
cid, ex = run_cit("Clarify REQ-0001 statement with the refund sign convention", "acceptance_criteria_change", "REQ-0001",
                  [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "Order totals are exact integer cents; refunds are negative cents with an explicit REFUND_SIGN_MARKER."}])
log("cit execute ->", ex.get("ok"), (ex.get("result") or {}).get("cit_status"), (ex.get("error") or {}).get("code"))
man = json.loads((root / "governance/generated/index-manifest.json").read_text())
fr = g.ok("memory", "freshness", show=False)
qq = g.ok("memory", "query", "REFUND_SIGN_MARKER", "--k", "3", show=False)
log("manifest REQ-0001 content hash changed:", man["artifacts"]["spec/requirements/REQ-0001.yaml"]["content_hash"] != h0, "| freshness after CIT-E:", fr["fresh"],
    "| query for the new literal ->", [h["artifact_id"] for h in qq["hits"]])
check("K2-D1-1", ex.get("ok") and fr["fresh"] and "REQ-0001" in [h["artifact_id"] for h in qq["hits"]],
      "CIT-E refreshes the index inside the transaction and verifies freshness; the new content is retrievable immediately")
commit_all(root, "cit 1")

section("K2-D1-2 index refresh failure inside CIT-E -> rollback")
pp_before = (root / "governance/project/PROJECT_POLICY.yaml").read_text()
pp = yaml.safe_load(pp_before)
pp.setdefault("policy_overrides", {})["MEMORY_POLICY.embedding.provider"] = "no-such-embedder"
cid2, ex2 = run_cit("Switch embedder via overlay edit", "governance_change", "REQ-0001",
                    [{"op": "write_file", "path": "governance/project/PROJECT_POLICY.yaml", "content": yaml.safe_dump(pp, sort_keys=False)}])
log("cit execute ->", ex2.get("ok"), (ex2.get("error") or {}).get("code"), (ex2.get("error") or {}).get("message", "")[:220])
st = yaml.safe_load((root / f"spec/decisions/{cid2}.yaml").read_text()) if (root / f"spec/decisions/{cid2}.yaml").exists() else {}
fr2 = g.ok("memory", "freshness", show=False)
qq2 = g.run("memory", "query", "REFUND_SIGN_MARKER", "--k", "3")
log("cit_status:", st.get("cit_status"), "| overlay restored:", (root / "governance/project/PROJECT_POLICY.yaml").read_text() == pp_before,
    "| freshness:", fr2["fresh"], fr2["pin_mismatch"], "| retrieval still works:", qq2.get("ok"))
check("K2-D1-2", not ex2.get("ok") and st.get("cit_status") == "ROLLED_BACK" and (root / "governance/project/PROJECT_POLICY.yaml").read_text() == pp_before and qq2.get("ok"),
      "a failed index refresh aborts CIT-E atomically: the change is rolled back and the index remains usable")
sem = g.run("memory", "query", "why integer cents rationale", "--route", "semantic", "--k", "3")
log("semantic query after the CIT outcome ->", sem.get("ok"), (sem.get("error") or {}).get("code"))
log("OBSERVATION: cit::execute applies the manifest, then refreshes and verifies the index with the SAME Project value whose policies/contract"
    " were cached before the mutation (runtime/src/cit/mod.rs execute: no p.invalidate() after apply_op; project.rs OnceCell caches)")
if (root / "governance/project/PROJECT_POLICY.yaml").read_text() != pp_before:
    (root / "governance/project/PROJECT_POLICY.yaml").write_text(pp_before)
commit_all(root, "cit 2 outcome; overlay restored by the auditor")
g.ok("rebuild-memory", show=False)

section("K2-D1-3 CIT reclassifies docs/** as historical -> committed index?")
c = yaml.safe_load((root / "governance/project/REPOSITORY_CONTRACT.yaml").read_text())
for r in c["paths"]:
    if r["pattern"] == "docs/**":
        r.update({"class": "historical", "default_retrieval": False, "namespace": "archive"})
cid3, ex3 = run_cit("Archive the old docs tree", "governance_change", "REQ-0001",
                    [{"op": "write_file", "path": "governance/project/REPOSITORY_CONTRACT.yaml", "content": yaml.safe_dump(c, sort_keys=False)}])
log("cit execute ->", ex3.get("ok"), (ex3.get("result") or {}).get("cit_status"), (ex3.get("error") or {}).get("code"))
row = q(root, "SELECT path_class, status, default_retrieval, namespace FROM artifacts WHERE path='docs/runbook.md'")
fr3 = g.ok("memory", "freshness", show=False)
qd = g.ok("memory", "query", "reconciliation procedure settlement window", "--k", "5", show=False)
log("after the committed CIT: docs/runbook.md row:", row, "| freshness:", fr3["fresh"], "| archived runbook returned as current:",
    "file:docs/runbook.md" in [h["artifact_id"] for h in qd["hits"]])
check("K2-D1-3", row and row[0][0] == "historical" and "file:docs/runbook.md" not in [h["artifact_id"] for h in qd["hits"]],
      "a path-map change committed through CIT-E is reflected in the refreshed index (no archive-as-current after COMMITTED)")
commit_all(root, "cit 3")
g.ok("rebuild-memory", show=False)

section("D1-W6-1 ungoverned upstream edit -> index staleness -> task close blocked")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Implement refund sign", "--feature", "F-0001", "--status", "READY",
         "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001"]}))["id"]
g.ok("task", "claim", t, show=False)
pk_before = g.ok("context", "compile", t, show=False)
write(root, "src/app/models.py", (root / "src/app/models.py").read_text() + "\nREFUND_SIGN = -1\n")
rep = BASE / "x-rep.json"
rep.write_text(json.dumps({"task": t, "work_completed": "refund sign", "files_changed": ["src/app/models.py"], "tests": {"status": "passed"}}))
g.ok("rebuild-memory", "--incremental", show=False)
cl = g.ok("task", "close", t, "--report", str(rep))
commit_all(root, "task closed")
req = yaml.safe_load((root / "spec/requirements/REQ-0001.yaml").read_text())
req["statement"] = "Order totals are exact integer cents; refunds are POSITIVE cents with a separate REFUND flag."
(root / "spec/requirements/REQ-0001.yaml").write_text(yaml.safe_dump(req, sort_keys=False))
commit_all(root, "ungoverned upstream change to REQ-0001")
fr = g.ok("memory", "freshness", show=False)
t2 = g.ok("task", "create", "--class", "documentation", "--objective", "doc", "--status", "READY", "--allowed", "docs/**")["id"]
g.ok("task", "claim", t2, show=False)
rep2 = BASE / "x-rep2.json"
rep2.write_text(json.dumps({"task": t2, "work_completed": "doc", "files_changed": [], "tests": {"status": "not_applicable_with_reason", "reason": "doc"}}))
c2 = g.run("task", "close", t2, "--report", str(rep2))
log("after the upstream edit: freshness stale:", fr["stale"], "| unrelated task close ->", (c2.get("error") or {}).get("code"))
check("D1-W6-1", "spec/requirements/REQ-0001.yaml" in fr["stale"] and (c2.get("error") or {}).get("code") == "INDEX_STALE",
      "an upstream authoritative change makes the index stale and blocks task close until refreshed")

section("D1-W6-2 after refresh: downstream evidence / context packets")
g.ok("rebuild-memory", "--incremental", show=False)
tr = yaml.safe_load((root / f"spec/tasks/{t}.yaml").read_text())
pk_after = g.ok("context", "compile", t, show=False)
st = g.ok("status", show=False)
log("DONE task governed by REQ-0001:", {k: tr.get(k) for k in ["task_status", "retest_required", "staleness"]})
log("context packet index snapshot before/after:", pk_before["retrieved_intelligence"]["index_snapshot"]["manifest_hash"][:12],
    pk_after["retrieved_intelligence"]["index_snapshot"]["manifest_hash"][:12], "| gov status memory:", st["memory"])
log("OBSERVATION (W6, other family): after an ungoverned upstream edit and an index refresh, the DONE task is",
    "flagged" if tr.get("retest_required") or tr.get("staleness") else "NOT flagged", "stale; index freshness is green")

section("D1-W6-3 governed upstream change: staleness propagation + index refresh together")
cid4, ex4 = run_cit("Revert refund convention to negative cents", "acceptance_criteria_change", "REQ-0001",
                    [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "Order totals are exact integer cents; refunds are negative cents."}])
res = ex4.get("result") or {}
tr2 = yaml.safe_load((root / f"spec/tasks/{t}.yaml").read_text())
tst = yaml.safe_load((root / "spec/tasks/TST-0001.yaml").read_text())
fr4 = g.ok("memory", "freshness", show=False)
log("cit execute ->", ex4.get("ok"), res.get("cit_status"), "| propagation:", res.get("propagation"))
log("TST-0001 staleness:", tst.get("staleness"), "| DONE task retest flag:", tr2.get("retest_required"), "| freshness after:", fr4["fresh"])
check("D1-W6-3", ex4.get("ok") and fr4["fresh"] and (tst.get("staleness") or {}).get("stale"),
      "a governed upstream change propagates staleness to dependent tests and refreshes the index in the same transaction")
summary()
