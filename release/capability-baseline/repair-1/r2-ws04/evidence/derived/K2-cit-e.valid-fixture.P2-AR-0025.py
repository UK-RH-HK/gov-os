# DERIVED COPY (P2-AR-0025, WS-4 round 2) of release/capability-baseline/audit-0/delta-r/evidence/K2-cit-e.py.
# ONE change only: the fixture feature F-0001 gets the schema-required `readiness` field (feature.schema.json
# requires it). Unedited, the fixture is schema-invalid, which the governance suite reports as a HIGH schema_invariants
# finding; once the G4 tier runs after a CIT (IP-WS02-06) that finding is a recorded hard-block the G0 guard enforces at
# `cit.execute` (IP-WS02-05), so the unedited probe's later CIT-E lines stop on HEALTH_HARD_BLOCK. This copy shows the
# CIT-E behaviours themselves with a valid fixture. Run from the audit-of-record evidence directory (it imports harness).
"""K2 CIT-E (Contract v3 lines 628-636; framework §47.2) and the K2 <-> W6 interaction (AC-16).

b1 Final decision   b2 mutation manifest   b3 authoritative updates   b4 staleness/retest/rework propagation
b5 derived-view regeneration   b6 memory/index refresh   b7 verification   b8 commit or rollback/block atomically

Run:  python3 K2-cit-e.py > K2-cit-e.out 2>&1
"""
import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import GOV, Proj, check, observe, summary, write_record, edit_record, cit_via_cli, cit_through, json_file  # noqa: E402


def sha(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except FileNotFoundError:
        return None


p = Proj("k2")
print("\n## setup: requirement with an open task, a DONE task, a test obligation and a scenario that depend on it")
write_record(p, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Payment retries", "status": "ACTIVE", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "readiness": {"requirements": "PRESENT"}})  # DERIVED: schema-required readiness added
write_record(p, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Retries are bounded", "status": "ACTIVE", "statement": "The client retries a failed charge at most five times.", "feature": "F-0001"})
write_record(p, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Flaky gateway", "status": "ACTIVE", "feature": "F-0001", "requirements": ["REQ-0001"]})
write_record(p, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Retry bound test", "status": "ACTIVE", "feature": "F-0001", "family": "unit", "tests": ["REQ-0001"]})
p.git("add", "-A"); p.git("commit", "-q", "-m", "records")
p.ok(["rebuild-memory"])
t_open = p.ok(["task", "create", "--objective", "tune retry backoff", "--class", "discovery", "--status", "READY", "--allowed", "product/**", "--fields", json.dumps({"requirements": ["REQ-0001"]})])["id"]
t_done = p.ok(["task", "create", "--objective", "implement bounded retry", "--class", "discovery", "--status", "READY", "--allowed", "product/**", "--fields", json.dumps({"requirements": ["REQ-0001"]})])["id"]
p.ok(["task", "claim", t_done])
p.write("product/retry.txt", "MAX_RETRIES=5\n")
p.ok(["rebuild-memory", "--incremental"])
closed = p.ok(["task", "close", t_done, "--report", json_file(p, "rep-done", {"work_completed": "implemented retry bound 5", "files_changed": ["product/retry.txt"], "tests": {"status": "passed"}})])
p.ok(["rebuild-memory"])
pk1 = p.ok(["context", "compile", t_open])
ck1 = p.ok(["checkpoint", "create", "--task", t_open, "--next-action", "continue tuning", "--step", "context compiled"])
observe("K2.setup", "ids", {"open_task": t_open, "done_task": t_done, "report": closed["report"], "ctx_hash_before": pk1["packet_hash"], "checkpoint": ck1["id"]})
tasks_before = sorted(t["id"] for t in p.ok(["task", "list"]))
gen = {f: sha(p.path(f"governance/generated/{f}")) for f in ("tool-registry.json", "adapter-manifest.json")}
gen_ts = json.load(open(p.path("governance/generated/tool-registry.json")))["generated_from"]["generated_at"]
time.sleep(1.1)

print("\n## CIT-A: change the requirement, add a new requirement, write a doc (behaviour_change, human-gated at R2)")
ops = [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "The client retries a failed charge at most three times."},
       {"op": "append_record", "record": {"id": "REQ-0002", "type": "requirement", "title": "Backoff is exponential", "status": "ACTIVE", "statement": "Retry delays double each attempt.", "feature": "F-0001"}},
       {"op": "write_file", "path": "docs/retry.md", "content": "Retries: 3\n"}]
cA, ex = cit_through(p, "A", ops, trigger="behaviour_change", targets=["REQ-0001"])
rec = p.record(cA)
check("K2.b1.1", ex["ok"] and rec["cit_status"] == "COMMITTED" and rec.get("decision") and rec["execution"]["decision"] == rec["decision"], "execution is bound to the final decision record derived from the answered gate", {"cit_status": rec["cit_status"], "decision": rec.get("decision"), "execution.decision": rec["execution"].get("decision"), "execution.gate": rec["execution"].get("gate")})
check("K2.b1.2", [j["event"] for j in rec["journal"]] == ["proposed", "simulated", "approved", "executing", "committed"], "the journal shows proposal -> simulation -> approval -> execution -> commit", [j["event"] for j in rec["journal"]])
dec = p.record(rec["decision"])
check("K2.b1.3", dec["status"] == "ACTIVE" and dec.get("human_approved") is True, "the final decision record is ACTIVE", {k: dec.get(k) for k in ("status", "human_approved", "approved_by_kind")})
req1 = p.record("REQ-0001"); req2 = p.record("REQ-0002")
check("K2.b2.1", "three times" in req1["statement"] and req2 is not None and os.path.exists(p.path("docs/retry.md")), "every op of the mutation manifest was applied (set_field, append_record, write_file)", {"REQ-0001.statement": req1["statement"], "REQ-0002": bool(req2), "docs/retry.md": os.path.exists(p.path("docs/retry.md"))})
check("K2.b3.1", req1.get("updated") is not None and req2.get("type") == "requirement", "authoritative records are updated in place (updated date) and new records are created as governed records", {"REQ-0001.updated": req1.get("updated")})
v = p.run(["cit", "propose", "--proposal", "unknown op", "--trigger", "editorial", "--manifest", json_file(p, "m-unknown-op", [{"op": "write_file", "path": "docs/u.md", "content": "u"}, {"op": "no_such_op"}])])
check("K2.b2.2", (not v["ok"]) and v["error"]["code"] == "SCHEMA_INVALID" and "no_such_op" in v["error"]["message"], "a manifest with an op outside the cit schema's op enum is refused at propose (never reaches execution)", v.get("error"))
v = p.run(["cit", "propose", "--proposal", "bad record", "--trigger", "editorial", "--manifest", json_file(p, "m-badrec", [{"op": "append_record", "record": {"id": "REQ-0003", "type": "requirement", "status": "NOT_A_STATUS"}}])])
cbad = v["result"]["id"] if v["ok"] else None
if cbad:
    p.ok(["cit", "simulate", cbad]); p.ok(["cit", "approve", cbad])
    e = p.run(["cit", "execute", cbad])
    check("K2.b3.2", (not e["ok"]) and p.record("REQ-0003") is None, "an authoritative update that violates its schema is refused and nothing is persisted", e.get("error"))

print("\n## b4 staleness / retest / rework propagation (and K2 <-> W6)")
to = p.record(t_open); tst = p.record("TST-0001"); scn = p.record("SCN-0001"); td = p.record(t_done); rpt = p.record(closed["report"])
check("K2.b4.1", to.get("retest_required") is True and cA in (to.get("retest_reason") or ""), "the open dependent task is marked retest_required with the CIT as reason", {k: to.get(k) for k in ("retest_required", "retest_reason", "task_status")})
dag = p.ok(["task", "dag"])
check("K2.b4.2", t_open not in dag["runnable"] and any(b["task"] == t_open and "retest" in json.dumps(b["reasons"]) for b in dag["blocked"]), "the retest flag blocks the task in the DAG", [b for b in dag["blocked"] if b["task"] == t_open])
check("K2.b4.3", (tst.get("staleness") or {}).get("stale") is True and (scn.get("staleness") or {}).get("stale") is True, "the dependent test obligation and scenario are marked stale", {"TST-0001": tst.get("staleness"), "SCN-0001": scn.get("staleness")})
check("K2.b4.4", td.get("retest_required") is True or (td.get("staleness") or {}).get("stale") is True, "a COMPLETED (DONE) task that implemented the changed requirement is marked stale / for re-validation (W6: COMPLETE does not imply permanently valid)", {k: td.get(k) for k in ("task_status", "retest_required", "staleness")})
check("K2.b4.5", (rpt.get("staleness") or {}).get("stale") is True, "the DONE task's closing evidence (report) is invalidated by the upstream change", {"report": closed["report"], "staleness": rpt.get("staleness")})
tasks_after = sorted(t["id"] for t in p.ok(["task", "list"]))
check("K2.b4.6", len(tasks_after) > len(tasks_before), "revalidation/rework tasks are generated for the affected completed work", {"before": tasks_before, "after": tasks_after})
ctx_file = json.load(open(p.path(f".governance-runtime/context/{t_open}.json")))
pk2 = p.ok(["context", "compile", t_open])
latest = p.ok(["checkpoint", "latest"])
observe("K2.w6.ctx", "context packet and checkpoint after the upstream change", {"stored_packet_hash_before_recompile": ctx_file["packet_hash"], "recompiled_hash": pk2["packet_hash"], "stored_packet_top_level_keys": sorted(ctx_file.keys()), "latest_checkpoint": latest.get("id"), "latest_checkpoint_trigger": latest.get("trigger")})
ck_old = p.record(ck1["id"])
check("K2.w6.1", bool(set(ctx_file.keys()) & {"stale", "staleness", "invalidated", "invalidated_by"}) or ctx_file["packet_hash"] != pk1["packet_hash"], "the context packet compiled before the change is invalidated (W6: affected context packets are invalidated)", {"stored_hash": ctx_file["packet_hash"], "before": pk1["packet_hash"]})
check("K2.w6.2", (ck_old.get("staleness") or {}).get("stale") is True, "the checkpoint that recorded the pre-change context hash is marked stale", {"checkpoint": ck1["id"], "context_packet_hash": ck_old.get("context_packet_hash"), "staleness": ck_old.get("staleness")})

print("\n## b5 derived-view regeneration   b6 memory/index refresh")
gen2 = {f: sha(p.path(f"governance/generated/{f}")) for f in ("tool-registry.json", "adapter-manifest.json")}
gen_ts2 = json.load(open(p.path("governance/generated/tool-registry.json")))["generated_from"]["generated_at"]
check("K2.b5.1", gen_ts2 != gen_ts, "the tool registry was regenerated by CIT-E (generated_at advanced)", {"before": gen_ts, "after": gen_ts2, "hashes_before": gen, "hashes_after": gen2})
fr = p.ok(["memory", "freshness"])
check("K2.b6.1", fr["fresh"] is True, "the index is fresh immediately after commit", {k: fr.get(k) for k in ("fresh", "stale", "added", "removed")})
q = p.ok(["memory", "query", "retries a failed charge at most three times"])
check("K2.b6.2", any(h["artifact_id"] == "REQ-0001" and "three" in (h.get("excerpt") or "") for h in q["hits"]), "retrieval returns the updated requirement text", [(h["artifact_id"], (h.get("excerpt") or "")[:80]) for h in q["hits"][:3]])

print("\n## b7 verification failure rolls back; b8 atomicity")
reg_before = json.load(open(p.path("governance/generated/tool-registry.json")))
cB, exB = cit_through(p, "B", [{"op": "write_file", "path": "governance/project/tools/probe-tool.yaml", "content": "tool_id: probe-tool\nstatus: active\nversion: '1'\n"},
                               {"op": "set_field", "target": t_open, "field": "task_status", "value": "BOGUS"}], trigger="governance_change")
rb = p.record(cB); to2 = p.record(t_open)
check("K2.b7.1", (not exB["ok"]) and exB["error"]["code"] == "VERIFICATION_FAILED" and rb["cit_status"] == "ROLLED_BACK", "a schema-invalid authoritative update fails CIT-E verification and the transaction is ROLLED_BACK", {"error": exB.get("error", {}).get("message"), "cit_status": rb["cit_status"]})
check("K2.b8.1", to2["task_status"] != "BOGUS" and not os.path.exists(p.path("governance/project/tools/probe-tool.yaml")), "every applied op was undone: the task record restored and the created tool descriptor removed", {"task_status": to2["task_status"], "tool_file": os.path.exists(p.path("governance/project/tools/probe-tool.yaml"))})
reg_after = json.load(open(p.path("governance/generated/tool-registry.json")))
check("K2.b8.2", not any(t.get("tool_id") == "probe-tool" for t in reg_after["tools"]), "derived views regenerated during the failed execution are rolled back too (no phantom tool in the registry)", {"probe-tool_in_registry": any(t.get("tool_id") == "probe-tool" for t in reg_after["tools"]), "was_in_registry_before": any(t.get("tool_id") == "probe-tool" for t in reg_before["tools"])})
before_stmt = p.record("REQ-0001")["statement"]
cC, exC = cit_through(p, "C", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "MID-MANIFEST"}, {"op": "write_file", "path": "docs/c.md", "content": "c\n"}, {"op": "set_field", "target": "REQ-9999", "field": "x", "value": 1}], trigger="behaviour_change", targets=["REQ-0001"])
check("K2.b8.3", (not exC["ok"]) and p.record("REQ-0001")["statement"] == before_stmt and not os.path.exists(p.path("docs/c.md")) and p.record(cC)["cit_status"] == "ROLLED_BACK", "a failure in the third op (RECORD_NOT_FOUND at apply time) undoes the first two (all-or-nothing)", {"error": exC.get("error", {}).get("code"), "statement": p.record("REQ-0001")["statement"], "docs/c.md": os.path.exists(p.path("docs/c.md"))})
cD, exD = cit_through(p, "D", [{"op": "write_file", "path": "docs/d.md", "content": "d\n"}, {"op": "write_file", "path": "governance/kernel/evil.md", "content": "x\n"}], trigger="governance_change")
check("K2.b8.4", (not exD["ok"]) and exD["error"]["code"] == "INV_007" and not os.path.exists(p.path("docs/d.md")) and not os.path.exists(p.path("governance/kernel/evil.md")), "a kernel write (INV-007) is refused and the earlier op is rolled back", exD.get("error"))

print("\n## b8 interrupted execution (process killed mid-manifest) is recovered")
fake = os.path.join(os.path.dirname(p.root), "fakebin")
os.makedirs(fake, exist_ok=True)
with open(os.path.join(fake, "git"), "w") as f:
    f.write("#!/bin/sh\nif [ \"$1\" = \"mv\" ]; then sleep 120; fi\nexec /usr/bin/git \"$@\"\n")
os.chmod(os.path.join(fake, "git"), 0o755)
cI, gI, _, _ = cit_via_cli(p, "I", [{"op": "write_file", "path": "docs/int.md", "content": "interrupted\n"}, {"op": "move_file", "path": "docs/int.md", "to": "docs/int2.md"}], trigger="behaviour_change")
if gI:
    p.ok(["gate", "present", gI]); p.ok(["decide", gI, "--option", "A"])
p.ok(["cit", "approve", cI])
env = p.env({"PATH": fake + ":" + os.environ.get("PATH", "")})
print(f"$ PATH=<fakebin git that hangs on mv>:$PATH gov --json --root <proj> cit execute {cI}   (killed with SIGKILL once EXECUTING)", flush=True)
proc = subprocess.Popen([GOV, "--json", "--root", p.root, "--session", p.session, "cit", "execute", cI], cwd=p.root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
state = None
for _ in range(200):
    time.sleep(0.1)
    r = p.record(cI)
    if r and r["cit_status"] == "EXECUTING" and os.path.exists(p.path("docs/int.md")):
        state = r["cit_status"]
        break
os.killpg(proc.pid, signal.SIGKILL); proc.wait()  # kills gov and its hanging git/sleep children (own process group)
observe("K2.b8.5a", "state after SIGKILL", {"cit_status": p.record(cI)["cit_status"], "docs/int.md": os.path.exists(p.path("docs/int.md")), "seen_executing": state})
st = p.ok(["status"])
check("K2.b8.5", any(o["id"] == cI and o["cit_status"] == "EXECUTING" for o in st["open_transactions"]), "the interrupted transaction is visible as EXECUTING in gov status", st["open_transactions"])
dry = p.ok(["recover", "--dry-run"])
observe("K2.b8.6a", "recover --dry-run classification", [i for i in dry["items"] if i.get("kind") == "cit"])
rc = p.ok(["recover"])
check("K2.b8.6", p.record(cI)["cit_status"] == "ROLLED_BACK" and not os.path.exists(p.path("docs/int.md")), "gov recover rolls the interrupted transaction back from its snapshot", {"cit_status": p.record(cI)["cit_status"], "docs/int.md": os.path.exists(p.path("docs/int.md")), "actions": rc.get("actions")})

print("\n## explicit rollback of a committed transaction")
rbA = p.run(["cit", "rollback", cA, "--reason", "probe"])
check("K2.b8.7", rbA["ok"] and "five times" in p.record("REQ-0001")["statement"] and p.record("REQ-0002") is None and not os.path.exists(p.path("docs/retry.md")) and p.record(rec["decision"])["status"] == "REJECTED", "rolling back CIT-A restores REQ-0001, removes REQ-0002 and docs/retry.md, and retires the decision", {"statement": p.record("REQ-0001")["statement"], "REQ-0002": p.record("REQ-0002") is not None, "decision_status": p.record(rec["decision"])["status"]})

print("\n## CIT-E verification against a stale index blames the transaction for pre-existing damage")
edit_record(p, "SCN-0001", lambda d: d.update({"depends_on": ["REQ-9999"]}))
cE, exE = cit_through(p, "E", [{"op": "write_file", "path": "docs/e.md", "content": "harmless\n"}], trigger="editorial")
observe("K2.b7.2", "a harmless editorial CIT executed while an unindexed dangling reference already existed", {"ok": exE["ok"], "error": exE.get("error", {}).get("message", "")[:300]})
check("K2.b7.2", exE["ok"], "a transaction is not rolled back for graph damage that pre-dates it (verification compares against a fresh pre-execution baseline)", exE.get("error", {}).get("code"))
summary()
