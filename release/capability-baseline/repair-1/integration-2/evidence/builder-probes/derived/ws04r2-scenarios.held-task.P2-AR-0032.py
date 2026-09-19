# DERIVED COPY (P2-AR-0032, round-2 integration builder) of
#   release/capability-baseline/repair-1/r2-ws04/evidence/derived/ws04r2-scenarios.py (P2-AR-0025, WS-4).
# ORIGINAL-PROBE-ID: ws04-r2-scenarios
# Changes, and nothing else:
#  (1) S4.boundaries-observed fixture: the explicit hold is set on the claimed task t1 (a real state change) instead of
#      t2 — with WS-5 (P2-AR-0026, BC-P2-16) t2 is already stored BLOCKED (its mandatory input is missing), so
#      `task status t2 BLOCKED` changes no task state and there is no transition to observe. The check is unchanged.
# Run like the original (run-builder-probe.sh, through the labelled derived evidence adapter).
"""P2-AR-0025 (WS-4, repair-1 round 2) BUILDER SCENARIO PROBE — regression evidence only (Contract v3 O3), not an
audit-of-record probe. It imports the unedited delta-r harness (run it with run-derived.sh, which puts the family's
evidence directory on PYTHONPATH and routes human answers through the P2-AR-0022 owner-channel adapter).

S1 BC-P2-11 approval bound to content, impact and CIT     S2 BC-P2-13 materiality derived from what changes
S3 BC-P2-04 upstream change reaches completed work         S4 BC-P2-05 checkpoint and handoff continuity
S5 BC-P2-18 contradictions detected, blocked and routed
"""
import json
import os
import sys

sys.path.insert(0, os.environ.get("PYTHONPATH", "").split(":")[0])
from harness import Proj, check, observe, summary, write_record, edit_record, json_file, cit_via_cli, cit_through, load_record_file  # noqa: E402


def err(v):
    return (v.get("error") or {}).get("code")


def spec(p):
    write_record(p, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
                                                   "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "readiness": {"requirements": "PRESENT"}})
    write_record(p, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
                                                        "feature": "F-0001", "kind": "functional", "statement": "totals are integer cents", "acceptance_criteria": ["2 x 199 = 398"]})
    write_record(p, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Cart total", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
                                                     "feature": "F-0001", "requirements": ["REQ-0001"], "then": ["total is 398"]})
    write_record(p, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Totals test", "status": "ACTIVE", "feature": "F-0001", "family": "unit", "tests": ["REQ-0001"]})
    p.git("add", "-A"); p.git("commit", "-q", "-m", "spec")
    p.ok(["rebuild-memory"])


# ============================================================ S1 BC-P2-11
print("\n## S1 BC-P2-11: an approval binds the exact transaction, its simulated impact and the CIT")
p = Proj("s1")
spec(p)
man = [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "totals are integer cents, rounded half-even"}]
cid, gid, _, sim = cit_via_cli(p, "s1a", man, trigger="behaviour_change", targets=["REQ-0001"])
check("S1.gate-carries-binding", bool(gid) and bool(sim["impact"].get("binding_sha256")) and (p.ok(["gate", "show", gid])["gate"].get("subject") or {}).get("sha256") == sim["impact"].get("binding_sha256"),
      "the gate raised for the CIT carries the transaction+impact digest as its subject (inside the signed package)", {"gate": gid, "binding": sim["impact"].get("binding_sha256")})
p.ok(["gate", "present", gid]); p.ok(["decide", gid, "--option", "A", "--rationale", "approve the rounding change"])
edit_record(p, cid, lambda d: d["mutation_manifest"].append({"op": "write_file", "path": "governance/project/INJECTED.md", "content": "x\n"}))
v = p.run(["cit", "approve", cid])
check("S1.content-edit-before-approve", err(v) == "APPROVAL_STALE", "a manifest edited after the answer cannot be approved under that answer", v.get("error"))
cid2, gid2, _, sim2 = cit_via_cli(p, "s1b", man, trigger="behaviour_change", targets=["REQ-0001"])
p.ok(["gate", "present", gid2]); p.ok(["decide", gid2, "--option", "A"])
edit_record(p, cid2, lambda d: d["impact"].update({"radius": "R0", "human_gate_required": False}))
v = p.run(["cit", "approve", cid2, "--method", "auto"])
check("S1.impact-edit-refused", err(v) == "APPROVAL_STALE", "a recorded impact edited after simulation (radius lowered) cannot be approved", v.get("error"))
cid3, gid3, _, _ = cit_via_cli(p, "s1c", [{"op": "write_file", "path": "src/lib3.rs", "content": "pub fn f() {}\n"}], trigger="behaviour_change")
edit_record(p, cid3, lambda d: d.update({"cit_status": "APPROVED", "approval": {"gate": None, "decision": "D-0999", "method": "auto", "human_approved": False}}))
v = p.run(["cit", "execute", cid3])
check("S1.forged-auto-approval-refused", (not v["ok"]) and not os.path.exists(p.path("src/lib3.rs")), "a forged automatic approval on a transaction that requires a gate never executes", v.get("error"))
_, d1 = load_record_file(p, cid)
cid4, _, _, _ = cit_via_cli(p, "s1d", [{"op": "write_file", "path": "docs/s1d.md", "content": "d\n"}], trigger="editorial")
edit_record(p, cid4, lambda d: d.update({"os_state": d1.get("os_state")}))
v = p.run(["cit", "simulate", cid4])
check("S1.copied-state-refused", err(v) in ("CIT_STATE_MISMATCH", "T2_UNBOUND"), "the sealed state of another transaction copied into a record is refused", v.get("error"))
cid5, _, _, _ = cit_via_cli(p, "s1e", [{"op": "write_file", "path": "docs/s1e.md", "content": "e\n"}], trigger="editorial")
edit_record(p, cid5, lambda d: d.pop("os_state", None))
v = p.run(["cit", "approve", cid5, "--method", "auto"])
check("S1.unsealed-state-refused", err(v) == "T2_UNBOUND", "a CIT record whose sealed state was removed is not a transaction gov wrote", v.get("error"))
write_record(p, "spec/decisions/CIT-0099.yaml", {"id": "CIT-0099", "type": "cit", "title": "hand-written", "status": "ACTIVE", "cit_status": "APPROVED", "proposal": "x",
                                                  "mutation_manifest": [{"op": "write_file", "path": "docs/forged.md", "content": "f\n"}], "approval": {"method": "auto"}, "impact": {"radius": "R0", "human_gate_required": False}})
v = p.run(["cit", "execute", "CIT-0099"])
check("S1.hand-written-cit-refused", (not v["ok"]) and not os.path.exists(p.path("docs/forged.md")), "a hand-written CIT record claiming APPROVED never executes", v.get("error"))

# ============================================================ S2 BC-P2-13
print("\n## S2 BC-P2-13: materiality is derived from what a change touches, not from the label")
q = Proj("s2")
spec(q)
q.write("src/payments/auth.py", "def authorise(t):\n    return verify_signature(t)\n")
q.write("ops/cluster.yaml", "apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 2\n")
q.write("tests/features/cart.feature", "Scenario: total\n  Then total is 398\n")
q.git("add", "-A"); q.git("commit", "-q", "-m", "code")
q.ok(["rebuild-memory", "--incremental"])
cases = [("auth", [{"op": "write_file", "path": "src/payments/auth.py", "content": "def authorise(t):\n    return True\n"}], "security_change"),
         ("k8s", [{"op": "write_file", "path": "ops/cluster.yaml", "content": "apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 40\n"}], "infrastructure_cost"),
         ("gherkin", [{"op": "write_file", "path": "tests/features/cart.feature", "content": "Scenario: total\n  Then total is 400\n"}], "acceptance_criteria_change"),
         ("req-criteria", [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400"]}], "acceptance_criteria_change")]
for tag, ops, want in cases:
    r = q.ok(["cit", "propose", "--proposal", f"tidy {tag}", "--trigger", "editorial", "--manifest", json_file(q, f"m-{tag}", ops)])
    mat = r.get("materiality") or {}
    sim = r.get("simulation") or {}
    check(f"S2.{tag}", want in (mat.get("derived_classes") or []) and r.get("auto_simulated") is True and bool(sim.get("human_gate")),
          f"'editorial' label on a {want} change: derived, simulated automatically and human-gated", {"derived": mat.get("derived_classes"), "radius": (sim.get("impact") or {}).get("radius"), "gate": sim.get("human_gate")})
r = q.ok(["cit", "propose", "--proposal", "fix typo", "--trigger", "editorial", "--manifest", json_file(q, "m-doc", [{"op": "write_file", "path": "docs/guide.md", "content": "typo fixed\n"}])])
check("S2.editorial-stays-editorial", not (r.get("materiality") or {}).get("derived_classes") and r["cit_status"] == "PROPOSED",
      "a genuinely editorial change is not made material", r.get("materiality"))
# the executable form of WS-2's deferred skill scenario SKL-IMPACT-ANALYSIS V1 (IP-WS02-20): a CIT that only DECLARES a
# governance path as its target (no manifest) is classified by that path, estimated R5 and human-gated
r = q.ok(["cit", "propose", "--proposal", "change the project policy overlay", "--targets", "governance/project/PROJECT_POLICY.yaml"])
check("S2.declared-governance-target", (r.get("impact") or {}).get("radius") == "R5" and bool(r.get("human_gate")) and "governance_change" in ((r.get("materiality") or {}).get("derived_classes") or []),
      "a CIT whose declared target is a governance path is R5 and human-gated (SKL-IMPACT-ANALYSIS V1)", {"radius": (r.get("impact") or {}).get("radius"), "gate": r.get("human_gate"), "derived": (r.get("materiality") or {}).get("derived_classes")})
q.write("src/payments/auth.py", "def authorise(t):\n    return t is not None\n")
q.write("spec/requirements/REQ-0001.yaml", q.read("spec/requirements/REQ-0001.yaml").replace("2 x 199 = 398", "2 x 199 = 400"))
c = q.run(["cit", "classify", "--paths", "src/payments/auth.py,spec/requirements/REQ-0001.yaml"]).get("result") or {}
need = [f["class"] for f in (c.get("materiality") or {}).get("requires_cit_in_task", [])]
check("S2.performed-changes-classified", "security_change" in need and "acceptance_criteria_change" in need,
      "changes already made in the working tree are classified, and the ones that must pass a CIT even inside a task are named (the task-close API)", need)

# ============================================================ S3 BC-P2-04
print("\n## S3 BC-P2-04: an upstream change reaches completed work, its evidence, packets and checkpoints")
s = Proj("s3")
spec(s)
fields = json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]})
done = s.ok(["task", "create", "--objective", "implement totals", "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--fields", fields])["id"]
opn = s.ok(["task", "create", "--objective", "tune totals", "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--fields", fields])["id"]
s.ok(["context", "compile", done]); s.ok(["task", "claim", done])
s.write("src/totals.rs", "pub fn t() -> i64 { 398 }\n"); s.ok(["rebuild-memory", "--incremental"])
cl = s.ok(["task", "close", done, "--report", json_file(s, "rep", {"work_completed": "totals", "files_changed": ["src/totals.rs"], "tests": {"status": "passed"}})])
s.ok(["rebuild-memory", "--incremental"])
s.ok(["context", "compile", opn]); ck = s.ok(["checkpoint", "create", "--task", opn, "--next-action", "continue"])
check("S3.checkpoint-records-inputs", any(i.get("id") == "REQ-0001" and i.get("content_hash") for i in ck.get("inputs", [])), "a task checkpoint records its mandatory inputs with content hashes", ck.get("inputs"))
tasks0 = {t["id"] for t in s.ok(["task", "list"])}
cA, ex = cit_through(s, "s3", [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400"]}], trigger="acceptance_criteria_change", targets=["REQ-0001"])
tasks1 = {t["id"]: t for t in s.ok(["task", "list"])}
new = [t for t in tasks1 if t not in tasks0]
rt = s.record(new[0]) if new else {}
check("S3.cit-committed", ex.get("ok"), "the CIT commits", ex.get("error"))
check("S3.done-task-revalidated", tasks1[done]["retest_required"] is True and (s.record(done).get("revalidation") or {}).get("required") is True, "the DONE consumer is marked for revalidation", s.record(done).get("revalidation"))
check("S3.revalidation-task", bool(new) and rt.get("revalidates") == done and rt.get("class") == "validation", "a revalidation task is generated for the completed work", {"new": new, "revalidates": rt.get("revalidates")})
check("S3.report-stale", (s.record(cl["report"]).get("staleness") or {}).get("stale") is True, "the closing report is no longer green", s.record(cl["report"]).get("staleness"))
check("S3.validation-evidence-stale", (s.record("TST-0001").get("staleness") or {}).get("stale") is True and (s.record("SCN-0001").get("staleness") or {}).get("stale") is True, "the test obligation and scenario that validate the changed criterion are stale at R1", None)
check("S3.checkpoint-stale", (s.record(ck["id"]).get("staleness") or {}).get("stale") is True, "the checkpoint that recorded the old input is stale", s.record(ck["id"]).get("staleness"))
pk = json.load(open(s.path(f".governance-runtime/context/{opn}.json")))
check("S3.packet-invalidated", bool(pk.get("invalidated")), "the stored packet of the open consumer is invalidated", pk.get("invalidated"))
v = s.run(["cit", "propagate"]).get("result") or {}
check("S3.idempotent", v.get("changes") == 0 and len(s.ok(["task", "list"])) == len(tasks1), "re-running propagation for a recorded change writes nothing and generates nothing", v)
# a direct change (no CIT): detected from what the work consumed, not from index freshness
edit_record(s, "REQ-0001", lambda d: d.update({"statement": "totals are integer cents (direct edit)"}))
s.ok(["rebuild-memory", "--incremental"])
st = s.run(["context", "staleness", opn]).get("result") or {"stale_inputs": []}
check("S3.direct-detected-after-rebuild", any(x["id"] == "REQ-0001" and not x["propagated"] for x in st["stale_inputs"]), "after an index rebuild, the direct change is still detected as stale input of the consumer", st["stale_inputs"])
dry = s.run(["cit", "propagate", "--dry-run"]).get("result") or {}
v = s.run(["cit", "propagate"]).get("result") or {}
check("S3.direct-propagated", v.get("propagated") is True and opn in (v["propagation"].get("retest_required") or []) + (v["propagation"]["plan"].get("open_tasks") and [x["id"] for x in v["propagation"]["plan"]["open_tasks"]] or []),
      "the same propagation is applied to a change made outside change control", {"dry_run_changes": dry.get("changes"), "result": v.get("propagation", {}).get("retest_required")})
pk2 = s.ok(["context", "compile", opn])
check("S3.redelivery-recorded", bool(pk2.get("redelivery")), "recompiling a stale packet records what changed since the previous delivery", pk2.get("redelivery"))

# ============================================================ S4 BC-P2-05
print("\n## S4 BC-P2-05: checkpoint staleness, handoff and session-close continuity, the watchdog")
h = Proj("s4")
spec(h)
t1 = h.ok(["task", "create", "--objective", "totals", "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001"]})])["id"]
t2 = h.ok(["task", "create", "--objective", "refunds", "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-9999"]})])["id"]
h.ok(["context", "compile", t1]); h.ok(["task", "claim", t1])
ck = h.ok(["checkpoint", "create", "--task", t1, "--next-action", "implement"])
check("S4.state-reference", bool((ck.get("state_reference") or {}).get("governed_state_digest")) and (ck.get("input_state") or {}).get("packet_current") is True, "the checkpoint records a current state reference and its packet is current", {"state_reference": ck.get("state_reference"), "packet_current": (ck.get("input_state") or {}).get("packet_current")})
v = h.run(["handoff", "create", "--to-role", "backend-engineer", "--task", t2])
check("S4.handoff-missing-refused", err(v) == "HANDOFF_INPUTS_UNSATISFIED", "a handoff whose mandatory input is absent is refused", v.get("error"))
edit_record(h, "REQ-0001", lambda d: d.update({"statement": "changed after the packet"}))
h.ok(["rebuild-memory", "--incremental"])
f = h.run(["checkpoint", "freshness", ck["id"]]).get("result") or {}
check("S4.checkpoint-freshness", f.get("state") == "STALE" and any(r["kind"] == "input_changed" for r in f.get("reasons", [])), "the checkpoint is stale once an input it recorded changed", f)
v = h.run(["handoff", "create", "--to-role", "backend-engineer", "--task", t1])
res = v.get("result") or {}
check("S4.handoff-stale-degraded", v["ok"] and (res.get("freshness") or {}).get("state") == "REFRESHED" and res.get("degraded"), "a handoff of in-progress work on a stale packet re-delivers the current inputs and is explicitly degraded", {"freshness": res.get("freshness", {}).get("state"), "degraded": res.get("degraded")})
check("S4.handoff-marks-retest", h.record(t1).get("retest_required") is True, "the in-progress work on stale inputs is marked retest_required", h.record(t1).get("staleness"))
sc = h.run(["session", "close", "--task", t2]).get("result") or {}
check("S4.session-close-degraded", sc.get("blocked") is False and sc.get("degraded") and sc.get("checkpoint"), "session close writes its checkpoint and is explicitly degraded when the session's work has missing inputs", sc.get("degraded"))
for i in range(30):
    h.run(["task", "list"], show=False)
    h.run(["task", "create", "--objective", f"op {i}", "--class", "discovery"], show=False)
w = h.ok(["checkpoint", "watchdog"])
check("S4.watchdog-counts-itself", w["fired"] is True and (w.get("observed") or {}).get("commands", 0) >= 25, "the watchdog counts the gov commands executed since the last checkpoint itself", w.get("observed"))
h.ok(["task", "status", t1, "BLOCKED", "--note", "waiting"])  # (1)
ov = h.read("governance/project/MODEL_ROUTING_OVERRIDES.yaml").replace("providers: []", "providers:\n  - name: new-provider\n    models:\n      - {id: new-model, tier: T3, max_reasoning: extra_high}")
h.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", ov)
w = h.ok(["checkpoint", "watchdog"])
trig = sorted({b["trigger"] for b in w.get("boundaries", [])})
check("S4.boundaries-observed", "task_transition" in trig and "before_model_switch" in trig, "unobserved mandatory triggers (a task transition, a provider switch) become checkpoints at the next boundary", trig)

# ============================================================ S5 BC-P2-18
print("\n## S5 BC-P2-18: contradictions are detected, never delivered together as authority, and routed")
c = Proj("s5")
spec(c)
write_record(c, "spec/decisions/D-0103.yaml", {"id": "D-0103", "type": "decision", "title": "Persist totals in Postgres", "status": "ACTIVE", "chosen_option": "postgres", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
write_record(c, "spec/decisions/D-0104.yaml", {"id": "D-0104", "type": "decision", "title": "Persist totals in MySQL", "status": "ACTIVE", "chosen_option": "mysql", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
c.git("add", "-A"); c.git("commit", "-q", "-m", "decisions"); c.ok(["rebuild-memory", "--incremental"])
t = c.ok(["task", "create", "--objective", "store totals", "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--feature", "F-0001"])["id"]
m = c.ok(["context", "manifest", t])
check("S5.manifest-blocked", m["delivery_state"] == "BLOCKED" and any(x["kind"] == "DECISION_CONFLICT" for x in m.get("contradictions") or []), "the manifest is BLOCKED by the contradiction", m.get("contradictions"))
pk = c.ok(["context", "compile", t])
act = [d["id"] for d in pk["deterministic_authority"]["active_decisions"]]
check("S5.not-delivered-as-authority", "D-0103" not in act and "D-0104" not in act and pk["delivery_state"] == "BLOCKED", "neither contradicting decision is delivered as active authority", act)
routed = pk.get("contradiction_routing") or []
gid = routed[0]["routed"]["gate"] if routed and routed[0].get("routed") else None
check("S5.routed-to-gate", bool(gid) and c.ok(["gate", "show", gid])["gate"].get("trigger") == "contradiction", "the contradiction is routed to a system-raised gate", routed)
pk_again = c.ok(["context", "compile", t])
check("S5.routing-idempotent", bool(gid) and not pk_again.get("contradiction_routing"), "a second dispatch does not raise a second gate", pk_again.get("contradiction_routing"))
if gid:
    c.ok(["gate", "present", gid]); c.ok(["decide", gid, "--option", "A", "--rationale", "postgres governs"])
m2 = c.ok(["context", "manifest", t])
pk3 = c.ok(["context", "compile", t])
act3 = [d["id"] for d in pk3["deterministic_authority"]["active_decisions"]]
check("S5.resolution-honoured", m2["delivery_state"] == "COMPLETE" and "D-0103" in act3 and "D-0104" not in act3, "after the answer, the governing decision is active and the other set aside", {"state": m2["delivery_state"], "active": act3})
write_record(c, "spec/tasks/TASK-0900.yaml", {"id": "TASK-0900", "type": "task", "title": "explicit", "status": "ACTIVE", "class": "discovery", "task_status": "READY", "objective": "o", "decisions": ["D-0104"], "state_class": "AUTHORITATIVE"})
m3 = c.ok(["context", "manifest", "TASK-0900"])
check("S5.explicit-set-aside-blocks", m3["delivery_state"] == "BLOCKED", "a task that explicitly depends on the set-aside decision stays blocked", m3.get("input_violations"))
summary()
