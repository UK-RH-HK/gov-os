"""C7 Episodic execution memory (Contract v3 lines 268-274).

An execution episode is driven through the product: task -> context compile -> handoff (A2A) -> worker return
(failed attempt with discoveries/lessons) -> second attempt -> task close with a report -> telemetry.
For each facet the probe shows where the product persisted it, whether it is product-observed or self-reported,
and whether it can be recalled later through the fabric (retrieval) by a different session.
"""
import json
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

root, g = build_rich("c7")
g.ok("rebuild-memory")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Add refund totals to the ledger", "--feature", "F-0001",
         "--status", "READY", "--allowed", "src/**,tests/**", "--fields", json.dumps({"requirements": ["REQ-0001"]}))
tid = t["id"]
pk = g.ok("context", "compile", tid)
h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", tid)
hid = h["id"]
log("handoff record:", {k: h.get(k) for k in ["id", "from_role", "to_role", "task", "inputs", "required_return", "handoff_status"]})
worker = g.as_role("backend-engineer").as_session("S-worker-1")
ret = BASE / "c7-return-failed.json"
ret.write_text(json.dumps({"task": tid, "status": "failed", "work_completed": "Attempted refund totals via float arithmetic; reverted",
                           "files_changed": [], "evidence": ["pytest -q: 2 failed"], "tests": {"status": "failed", "failed": 2},
                           "discoveries": ["refund rows are negative cents; sign convention undocumented"],
                           "risks": ["float arithmetic reintroduces drift"],
                           "lessons": ["Refund totals must use integer cents; the float attempt failed the exactness test"],
                           "proposed_decisions": [], "unresolved": ["sign convention for refunds"],
                           "recommended_next_action": "decide refund sign convention"}))
wr = worker.ok("handoff", "return", hid, "--file", str(ret))
log("worker return result:", wr)
hrec = yaml.safe_load((root / f"spec/planning/{hid}.yaml").read_text())
log("handoff after return:", {k: hrec.get(k) for k in ["handoff_status", "returned_at"]}, "return.status:", hrec["return"]["status"])
g.as_role("backend-engineer").as_session("S-worker-1").ok("telemetry", "emit", "--name", "tool.invoked", "--attrs", json.dumps({"task": tid, "tool": "pytest", "exit": 1, "files_read": ["src/app/models.py"]}))
# second attempt by the orchestrator session, closed with a report
g.ok("task", "claim", tid)
write(root, "src/app/models.py", (root / "src/app/models.py").read_text() + "\n\ndef refund_total(entries):\n    return sum(e for e in entries if e < 0)\n")
rep = BASE / "c7-report.json"
rep.write_text(json.dumps({"task": tid, "outcome": "success", "work_completed": "Refund totals as integer cents",
                           "files_changed": ["src/app/models.py"], "files_read": ["src/app/models.py", "spec/requirements/REQ-0001.yaml"],
                           "tools_used": ["pytest", "ruff"], "skills_used": [{"id": "SKL-BACKEND-IMPL", "version": "1.0.0"}], "model": {"provider": "prov-a", "model": "mid"},
                           "evidence": ["pytest -q: 3 passed"], "tests": {"status": "passed", "passed": 3},
                           "discoveries": ["refund sign convention documented in REQ-0001"], "risks": [], "lessons": [],
                           "proposed_decisions": [], "unresolved": [], "recommended_next_action": "none"}))
g.ok("rebuild-memory", "--incremental", show=False)
cl = g.ok("task", "close", tid, "--report", str(rep))
rpt = yaml.safe_load((root / f"spec/reports/{cl['report']}.yaml").read_text())
ck = yaml.safe_load((root / f"spec/reports/checkpoints/{cl['checkpoint']}.yaml").read_text())
commit_all(root, "episode")
g.ok("rebuild-memory", "--incremental", show=False)
tel = g.ok("telemetry", "summary")
events = [json.loads(l) for l in (root / ".governance-runtime/telemetry/events.jsonl").read_text().splitlines()]
fresh = g.as_session("S-fresh")

section("C7-b1 agent/session")
log("report session/role:", rpt.get("session"), rpt.get("role"), "| handoff from/to:", hrec.get("from_role"), hrec.get("to_role"),
    "| checkpoint session/role:", ck.get("session"), ck.get("role"))
log("telemetry event sessions/roles:", sorted({(e.get("session"), e.get("role")) for e in events}))
check("C7-b1", rpt.get("session") == "S-probe" and rpt.get("role") == "orchestrator" and hrec.get("to_role") == "backend-engineer"
      and ("S-worker-1", "backend-engineer") in {(e.get("session"), e.get("role")) for e in events} and ck.get("session") == "S-probe",
      "the acting agent role and session are stamped by the product on reports, handoffs, checkpoints and telemetry")

section("C7-b2 task/context")
log("report.task:", rpt.get("task"), "| handoff inputs:", hrec.get("inputs"), "| checkpoint context_packet_hash:", ck.get("context_packet_hash"),
    "| packet hash compiled:", pk["packet_hash"])
check("C7-b2", rpt.get("task") == tid and ck.get("context_packet_hash") and hrec["inputs"].get("context_packet"),
      "episode is bound to its task and to the context packet the worker was given (path in handoff, hash in checkpoint)")

section("C7-b3 tools")
log("report tools_used / skills_used / model:", rpt.get("tools_used"), rpt.get("skills_used"), rpt.get("model"))
log("telemetry tool events:", [(e["name"], e["attributes"].get("tool")) for e in events if e["name"] == "tool.invoked"])
log("telemetry command counts:", [(c["name"], c["count"]) for c in tel["commands"]])
check("C7-b3", rpt.get("tools_used") == ["pytest", "ruff"] and any(e["name"] == "tool.invoked" for e in events),
      "tools used are recorded (report tools_used, telemetry events); tool usage outside `gov` is self-reported, not observed")

section("C7-b4 files read/changed")
log("report files_changed (declared):", rpt.get("files_changed"), "| observed_files_changed (product-observed):", rpt.get("observed_files_changed"),
    "| files_read (declared):", rpt.get("files_read"))
check("C7-b4", rpt.get("observed_files_changed") == ["src/app/models.py"] and rpt.get("files_read"),
      "files changed are product-observed against the claim baseline; files read are recorded as declared by the worker")

section("C7-b5 tests/outcomes")
log("report tests/outcome:", rpt.get("tests"), rpt.get("outcome"), "| failed attempt (handoff return):", hrec["return"]["tests"], hrec["return"]["status"],
    "| checkpoint tests_status:", ck.get("tests_status"))
bad = BASE / "c7-report-bad.json"
bad.write_text(json.dumps({"task": tid, "work_completed": "x", "files_changed": [], "tests": {"status": "failed"}}))
t2 = g.ok("task", "create", "--class", "implementation", "--objective", "second", "--status", "READY", "--allowed", "src/**")
r_bad = g.run("task", "close", t2["id"], "--report", str(bad))
log("closing with tests.status=failed ->", (r_bad.get("error") or {}).get("code"))
check("C7-b5", rpt["tests"]["status"] == "passed" and hrec["return"]["status"] == "failed" and (r_bad.get("error") or {}).get("code") == "EVIDENCE_REQUIRED",
      "test results and outcomes are recorded for successful and failed attempts; close without passing tests is refused")

section("C7-b6 failures/discoveries")
lessons = [p for p in (root / "spec/lessons").glob("L-*.yaml") if "L-0101" not in p.name]
lrec = [yaml.safe_load(p.read_text()) for p in lessons]
log("lessons created from the failed worker return:", [(l["id"], l["status"], l.get("provenance")) for l in lrec])
log("failed attempt discoveries/risks/unresolved:", hrec["return"]["discoveries"], hrec["return"]["risks"], hrec["return"]["unresolved"])
rq = fresh.ok("memory", "query", "what did the failed refund attempt discover about sign convention", "--k", "6")
log("fresh session recall:", [(h["artifact_id"], h["record_type"], h["section"]) for h in rq["hits"]])
disc_chunks = q(root, "SELECT artifact_id, section FROM chunks WHERE text LIKE '%sign convention undocumented%'")
risk_chunks = q(root, "SELECT artifact_id, section FROM chunks WHERE text LIKE '%reintroduces drift%'")
log("chunks holding the worker's discovery text:", disc_chunks, "| risk text:", risk_chunks)
rq2 = fresh.ok("memory", "query", "\"sign convention undocumented\"", "--k", "5")
log("exact recall of the discovery text:", [(h["artifact_id"], h["section"]) for h in rq2["hits"]])
check("C7-b6-discovery-indexed", bool(disc_chunks) and bool(risk_chunks),
      "the worker's discoveries/risks (handoff return) are held in the retrievable fabric, not only in the YAML record")
check("C7-b6", lrec and any(h["artifact_id"] in (hid,) or h["record_type"] in ("handoff", "lesson", "report") for h in rq["hits"]),
      "failures and discoveries persist (handoff return, lesson candidates, report) and are recalled by a fresh session")

section("C7 persistence class")
log("episode artefacts tracked in Git:", git(root, "ls-files", f"spec/planning/{hid}.yaml", f"spec/reports/{cl['report']}.yaml", "spec/reports/checkpoints"))
log("telemetry file tracked?:", git(root, "ls-files", ".governance-runtime/telemetry/events.jsonl") or "NO (untracked runtime state)")
summary()
