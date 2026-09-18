"""L3 Gate presentation — attack probe (P2-AR-0011, family delta; also exercises L3 <-> E1).

Contract v3 lines 674-679:
  b1 Gate in a file only is NOT presented.            b2 It must surface in active human interface.
  b3 Presented != answered.                            b4 Declined/revoked/stale/other-CIT gates cannot authorise execution.
  b5 Human approval cannot be fabricated by agent/CLI metadata.
Family duty (P2-HO-0004): execute a CIT with a declined, revoked, stale and other-CIT gate; fabricate approval through
CLI flags, environment, role claims and record edits.

Run:  python3 L3-gate-presentation-attacks.py > L3-gate-presentation-attacks.out 2>&1
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary  # noqa: E402


def manifest(p, name, ops):
    path = os.path.join(os.path.dirname(p.root), f"{name}.json")
    with open(path, "w") as f:
        json.dump(ops, f)
    return path  # `gov cit propose --manifest` takes a plain path (the CLI adds the @ itself)


class _NoDates(yaml.SafeLoader):
    """SafeLoader that keeps ISO timestamps as strings, so a probe's edit never reformats a value it did not mean to touch."""


_NoDates.yaml_implicit_resolvers = {k: [(t, r) for t, r in v if t != "tag:yaml.org,2002:timestamp"] for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}


def edit(p, rid, fn):
    rel = p.find_record_file(rid)
    with open(p.path(rel)) as f:
        d = yaml.load(f, Loader=_NoDates)
    fn(d)
    with open(p.path(rel), "w") as f:
        yaml.safe_dump(d, f, sort_keys=False)
    print(f"# RECORD EDIT (direct file write, no gov command): {rel}", flush=True)
    return rel


def new_gated_cit(p, tag, trigger="governance_change", path=None):
    m = manifest(p, f"m-{tag}", [{"op": "write_file", "path": path or f"docs/{tag}.md", "content": f"{tag}\n"}])
    r = p.ok(["cit", "propose", "--proposal", f"probe change {tag}", "--trigger", trigger, "--manifest", m])
    cid = r["id"]
    gid = (r.get("simulation") or {}).get("human_gate")
    return cid, gid, r


p = Proj("l3")

# ---------------------------------------------------------------- b1: a gate in a file only is not presented
print("\n## b1 Gate in a file only is NOT presented")
cid, gid, r = new_gated_cit(p, "b1")
observe("L3.b1.0", "propose auto-simulated and raised a gate", {"cit": cid, "gate": gid, "radius": r["simulation"]["impact"]["radius"], "auto_simulated": r.get("auto_simulated")})
g = p.record(gid)
check("L3.b1.1", g["gate_status"] == "PENDING" and g["presented_in_chat"] is False, "freshly raised gate is PENDING and presented_in_chat=false (exists only as a file)", {"gate_status": g["gate_status"], "presented_in_chat": g["presented_in_chat"]})
v = p.run(["decide", gid, "--option", "A"])
check("L3.b1.2", (not v["ok"]) and v["error"]["code"] == "GATE_NOT_PRESENTED", "gov decide on a file-only gate is refused GATE_NOT_PRESENTED", v.get("error"))
v = p.run(["cit", "approve", cid])
check("L3.b1.3", (not v["ok"]) and v["error"]["code"] == "GATE_NOT_PRESENTED", "gov cit approve against a file-only gate is refused GATE_NOT_PRESENTED", v.get("error"))
v = p.run(["doctor"])
d019 = [c for c in (v.get("result") or v.get("error", {}).get("details") or {}).get("checks", []) if c.get("id") == "D019"]
check("L3.b1.4", bool(d019) and d019[0].get("ok") is False and gid in json.dumps(d019[0]), "gov doctor D019 reports the gate as existing only in files", d019[0] if d019 else v.get("error"))
st = p.ok(["status"])
check("L3.b1.5", gid in st["next_action"] and "present" in st["next_action"], "gov status next_action instructs presenting the file-only gate", st["next_action"])
# attack: flip the file flag directly, never run `gov gate present`
edit(p, gid, lambda d: d.update({"presented_in_chat": True}))
v = p.run(["decide", gid, "--option", "A", "--rationale", "record-edit presentation"])
check("L3.b1.6", (not v["ok"]) and v["error"]["code"] == "GATE_NOT_PRESENTED", "a gate whose presented_in_chat flag was set by a direct file edit (never surfaced) is still treated as NOT presented", v.get("result") or v.get("error"))

# ---------------------------------------------------------------- b2: must surface in the active human interface
print("\n## b2 It must surface in active human interface")
cid2, gid2, _ = new_gated_cit(p, "b2")
t = p.run(["gate", "present", gid2], json_mode=False)
check("L3.b2.1", t["exit"] == 0 and "HUMAN DECISION GATE" in t["stdout"] and "Permitted next actions" in t["stdout"], "gov gate present (text mode) prints the decision package on stdout", t["stdout"][:900])
cid3, gid3, _ = new_gated_cit(p, "b2json")
v = p.run(["gate", "present", gid3])
g3 = p.record(gid3)
observe("L3.b2.2", "--json gate present returns chat_text inside a machine envelope (nothing is printed for a human) yet the record is marked presented", {"chat_text_in_json": bool(v["result"].get("chat_text")), "presented_in_chat": g3["presented_in_chat"], "presented_by": g3.get("presented_by")})
check("L3.b2.2", not g3["presented_in_chat"], "a gate rendered only into a JSON envelope consumed by a program is NOT recorded as presented to a human", {"presented_in_chat": g3["presented_in_chat"]})
# isolated project so that the gate under test is the only (hence top-priority) pending gate
pc = Proj("l3cont")
cid4, gid4, _ = new_gated_cit(pc, "b2cont")
before = pc.record(gid4)["presented_in_chat"]
v = pc.run(["continue"])
after = pc.record(gid4)
pend_first = v["result"].get("gate")
observe("L3.b2.3", "gov --json continue presents the top pending gate as a side effect", {"before": before, "after": after["presented_in_chat"], "gate_text_returned": bool(pend_first), "presented_by": after.get("presented_by"), "continue_status": v["result"].get("status")})
check("L3.b2.3", after["presented_in_chat"] is False or before is True, "an agent calling `gov --json continue` does not by itself make a gate count as presented in the human interface", {"before": before, "after": after["presented_in_chat"]})
cid5, gid5, _ = new_gated_cit(p, "b2role")
v = p.run(["gate", "present", gid5], role="independent-auditor")
check("L3.b2.4a", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "L0 role (independent-auditor) cannot mark a gate presented (E1 role authority on present_gate)", v.get("error"))
v = p.run(["gate", "present", gid5], role="research-agent")
observe("L3.b2.4b", "an L1 worker role (research-agent) may mark a gate presented", {"ok": v["ok"], "presented_by": (p.record(gid5) or {}).get("presented_by")})
g5 = p.record(gid5)
check("L3.b2.5", any(k in g5 for k in ("human_acknowledged", "acknowledged_by", "presentation_receipt")), "the presentation record carries some human-side acknowledgement/receipt, not only the caller's session/role", {k: g5.get(k) for k in ("presented_in_chat", "presented_at", "presented_by")})

# ---------------------------------------------------------------- b3: presented != answered
print("\n## b3 Presented != answered")
cid6, gid6, _ = new_gated_cit(p, "b3")
p.ok(["gate", "present", gid6])
v = p.run(["cit", "approve", cid6])
check("L3.b3.1", (not v["ok"]) and v["error"]["code"] == "GATE_NOT_ANSWERED", "cit approve on a PRESENTED-but-unanswered gate is refused GATE_NOT_ANSWERED", v.get("error"))
v = p.run(["cit", "execute", cid6])
check("L3.b3.2", (not v["ok"]) and "APPROVED" in v["error"]["message"], "cit execute of the unapproved CIT is refused", v.get("error"))
c6 = p.record(cid6)
decs = [d for d in os.listdir(p.path("spec/decisions")) if d.startswith("D-")]
check("L3.b3.3", c6["cit_status"] == "SIMULATED" and p.record(gid6)["gate_status"] == "PRESENTED" and not os.path.exists(p.path("docs/b3.md")), "after presentation alone: CIT SIMULATED, gate PRESENTED, manifest not applied", {"cit_status": c6["cit_status"], "gate_status": p.record(gid6)["gate_status"], "decision_files": decs})

# ---------------------------------------------------------------- b4: declined / revoked / stale / other-CIT
print("\n## b4 Declined/revoked/stale/other-CIT gates cannot authorise execution")
# declined
cD, gD, _ = new_gated_cit(p, "b4declined")
p.ok(["gate", "present", gD])
r = p.ok(["decide", gD, "--option", "B", "--rationale", "no"])
check("L3.b4.d1", p.record(cD)["cit_status"] == "REJECTED", "declining (option B) marks the CIT REJECTED durably", {"decide": r, "cit_status": p.record(cD)["cit_status"]})
v = p.run(["cit", "approve", cD])
check("L3.b4.d2", not v["ok"], "cit approve after decline is refused", v.get("error"))
v = p.run(["cit", "execute", cD])
check("L3.b4.d3", not v["ok"] and not os.path.exists(p.path("docs/b4declined.md")), "cit execute after decline is refused and nothing is written", v.get("error"))
edit(p, cD, lambda d: d.update({"cit_status": "SIMULATED"}))
v = p.run(["cit", "approve", cD])
check("L3.b4.d4", (not v["ok"]) and v["error"]["code"] == "GATE_DECLINED", "even with the CIT status hand-reset to SIMULATED, approval re-derives from the gate and is refused GATE_DECLINED", v.get("error"))

# revoked before approval
cR1, gR1, _ = new_gated_cit(p, "b4revoked1")
p.ok(["gate", "present", gR1])
p.ok(["decide", gR1, "--option", "A", "--rationale", "yes"])
v = p.run(["gate", "revoke", gR1, "--reason", "probe"], role="research-agent")
check("L3.b4.r0", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "an L1 role cannot revoke a gate (revoke_gate requires L4; E1)", v.get("error"))
p.ok(["gate", "revoke", gR1, "--reason", "probe"])
v = p.run(["cit", "approve", cR1])
check("L3.b4.r1", (not v["ok"]) and v["error"]["code"] == "GATE_REVOKED", "approval against a revoked (WITHDRAWN) gate is refused GATE_REVOKED", v.get("error"))
# revoked after approval
cR2, gR2, _ = new_gated_cit(p, "b4revoked2")
p.ok(["gate", "present", gR2])
p.ok(["decide", gR2, "--option", "A"])
p.ok(["cit", "approve", cR2])
rv = p.ok(["gate", "revoke", gR2, "--reason", "changed mind"])
c = p.record(cR2)
check("L3.b4.r2", c["cit_status"] == "SIMULATED" and "approval" not in c, "revoking after approval returns the CIT to SIMULATED and removes the approval", {"revoke": rv, "cit_status": c["cit_status"], "has_approval": "approval" in c})
v = p.run(["cit", "execute", cR2])
check("L3.b4.r3", not v["ok"], "execute after revocation is refused", v.get("error"))
# restore APPROVED + approval by record edit -> execute must re-derive and refuse
appr_saved = {}


def restore(d):
    d["cit_status"] = "APPROVED"
    d["approval"] = {"gate": gR2, "decision": d.get("decision"), "method": "human", "human_approved": True}


edit(p, cR2, restore)
v = p.run(["cit", "execute", cR2])
check("L3.b4.r4", (not v["ok"]) and v["error"]["code"] == "GATE_REVOKED" and not os.path.exists(p.path("docs/b4revoked2.md")), "hand-restored APPROVED status does not execute: execute revalidates the gate and refuses GATE_REVOKED", v.get("error"))
# decision record rejected by edit while gate still ANSWERED
cR3, gR3, _ = new_gated_cit(p, "b4revoked3")
p.ok(["gate", "present", gR3])
dres = p.ok(["decide", gR3, "--option", "A"])
p.ok(["cit", "approve", cR3])
edit(p, dres["decision"], lambda d: d.update({"status": "REJECTED"}))
v = p.run(["cit", "execute", cR3])
check("L3.b4.r5", (not v["ok"]) and v["error"]["code"] == "GATE_REVOKED", "if the gate's decision record is no longer ACTIVE, execute is refused GATE_REVOKED", v.get("error"))

# stale: re-answered gate (answer timestamp changed after approval)
cS1, gS1, _ = new_gated_cit(p, "b4stale1")
p.ok(["gate", "present", gS1])
p.ok(["decide", gS1, "--option", "A"])
p.ok(["cit", "approve", cS1])
edit(p, gS1, lambda d: d["answer"].update({"at": "2099-01-01T00:00:00Z"}))
v = p.run(["cit", "execute", cS1])
check("L3.b4.s1", (not v["ok"]) and v["error"]["code"] == "APPROVAL_STALE", "a gate re-answered after approval makes the approval APPROVAL_STALE at execute", v.get("error"))
# stale: transaction content changed after the human answered and after approval
cS2, gS2, _ = new_gated_cit(p, "b4stale2", trigger="security_change")
imp0 = p.record(cS2)["impact"]
p.ok(["gate", "present", gS2])
p.ok(["decide", gS2, "--option", "A", "--rationale", "approve the docs-only change"])
p.ok(["cit", "approve", cS2])
edit(p, cS2, lambda d: d["mutation_manifest"].append({"op": "write_file", "path": "governance/project/INJECTED-AFTER-APPROVAL.md", "content": "not what the human approved\n"}))
v = p.run(["cit", "execute", cS2])
check("L3.b4.s2", (not v["ok"]) and v["error"]["code"] in ("APPROVAL_STALE", "GATE_REVOKED", "GATE_STATE_INVALID") and not os.path.exists(p.path("governance/project/INJECTED-AFTER-APPROVAL.md")), "a mutation manifest changed after the human answered cannot execute under the old answer (approval bound to transaction content)", {"execute": v.get("result") or v.get("error"), "injected_file_written": os.path.exists(p.path("governance/project/INJECTED-AFTER-APPROVAL.md")), "radius_when_answered": imp0["radius"]})
# stale: manifest changed after the answer, re-simulated through the CLI (radius rises R2 -> R5), then approved
cS3, gS3, _ = new_gated_cit(p, "b4stale3", trigger="security_change")
r0 = p.record(cS3)["impact"]["radius"]
p.ok(["gate", "present", gS3])
p.ok(["decide", gS3, "--option", "A", "--rationale", "approve the docs-only change"])
edit(p, cS3, lambda d: d["mutation_manifest"].append({"op": "write_file", "path": "governance/project/INJECTED-BEFORE-APPROVAL.md", "content": "x\n"}))
sim = p.ok(["cit", "simulate", cS3])
r1 = sim["impact"]["radius"]
v = p.run(["cit", "approve", cS3])
observe("L3.b4.s3", "radius when the human answered vs after re-simulation", {"answered_at_radius": r0, "resimulated_radius": r1, "gate_after_resim": sim.get("human_gate"), "approve": v.get("result") or v.get("error")})
v2 = p.run(["cit", "execute", cS3]) if v["ok"] else v
check("L3.b4.s3", ((not v["ok"]) or (not v2["ok"])) and not os.path.exists(p.path("governance/project/INJECTED-BEFORE-APPROVAL.md")), "an answer given at radius R2 cannot authorise the transaction after it re-simulates to a larger radius (R5 governance change)", {"approve_ok": v["ok"], "execute": v2.get("result") or v2.get("error"), "file_written": os.path.exists(p.path("governance/project/INJECTED-BEFORE-APPROVAL.md"))})

# other-CIT
cO1, gO1, _ = new_gated_cit(p, "b4other1")
cO2, gO2, _ = new_gated_cit(p, "b4other2")
p.ok(["gate", "present", gO1])
p.ok(["decide", gO1, "--option", "A"])
edit(p, cO2, lambda d: d.update({"human_gate": gO1}))
v = p.run(["cit", "approve", cO2])
check("L3.b4.o1", (not v["ok"]) and v["error"]["code"] == "GATE_MISMATCH", "pointing CIT-2 at the gate answered for CIT-1 is refused GATE_MISMATCH", v.get("error"))
edit(p, gO1, lambda d: d.update({"cit": cO2}))
v = p.run(["cit", "approve", cO2])
v2 = p.run(["cit", "execute", cO2]) if v["ok"] else v
check("L3.b4.o2", (not v2["ok"]) and not os.path.exists(p.path("docs/b4other2.md")), "re-binding the answered gate (and its decision) from CIT-1 to CIT-2 by editing the gate's cit field does not let CIT-1's answer execute CIT-2", {"approve": v.get("result") or v.get("error"), "execute": v2.get("result") or v2.get("error")})

# task-level gates (execution of blocked work)
print("\n## b4 (task-level gates: a gate that blocks a task)")
tasks = {}
for k in ("T_decl", "T_revA", "T_revP", "T_missing"):
    r = p.ok(["task", "create", "--objective", f"probe {k}", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])
    tasks[k] = r["id"]
observe("L3.b4.t0", "tasks", tasks)
gT = {}
for k in ("T_decl", "T_revA", "T_revP"):
    g = p.ok(["gate", "create", "--question", f"May {k} proceed?", "--fields", json.dumps({"blocks_tasks": [tasks[k]], "options": [{"id": "A", "description": "proceed"}, {"id": "B", "description": "do not proceed"}], "impact_radius": "R3"})])
    gT[k] = g["id"]
dag = p.ok(["task", "dag"])
check("L3.b4.t1", all(tasks[k] in json.dumps(dag["waiting_human"]) for k in gT) and not any(tasks[k] in dag["runnable"] for k in gT), "tasks blocked by pending gates are WAITING_HUMAN and not runnable", {"waiting": dag["waiting_human"], "runnable": dag["runnable"]})
p.ok(["gate", "present", gT["T_decl"]])
r = p.ok(["decide", gT["T_decl"], "--option", "B", "--rationale", "do not proceed"])
dag = p.ok(["task", "dag"])
check("L3.b4.t2", tasks["T_decl"] not in dag["runnable"], "a task whose blocking gate was DECLINED (option B) does not become runnable", {"decide": r, "runnable": dag["runnable"], "task_status": p.record(tasks["T_decl"])["task_status"]})
p.ok(["gate", "present", gT["T_revA"]])
p.ok(["decide", gT["T_revA"], "--option", "A"])
p.ok(["gate", "revoke", gT["T_revA"], "--reason", "approval withdrawn"])
dag = p.ok(["task", "dag"])
check("L3.b4.t3", tasks["T_revA"] not in dag["runnable"], "a task whose approving gate was REVOKED does not remain runnable", {"runnable": dag["runnable"], "task_status": p.record(tasks["T_revA"])["task_status"], "gate_status": p.record(gT["T_revA"])["gate_status"]})
p.ok(["gate", "revoke", gT["T_revP"], "--reason", "question withdrawn"])
rp = p.ok(["task", "replan"])
v = p.run(["task", "claim", tasks["T_revP"]])
check("L3.b4.t4", not v["ok"], "a task whose blocking gate was withdrawn without any answer cannot be replanned READY and claimed", {"replan": rp["changed"], "claim": v.get("result") or v.get("error")})
edit(p, tasks["T_missing"], lambda d: d.update({"human_gate": "HDG-9999", "task_status": "WAITING_HUMAN"}))
dag = p.ok(["task", "dag"])
check("L3.b4.t5", tasks["T_missing"] not in dag["runnable"], "a task referencing a non-existent gate is not runnable", {"runnable": dag["runnable"], "gate_deps": dag["human_gate_dependencies"]})

p.ok(["rebuild-memory", "--incremental"])  # index the t5 edit now, so later CIT-E verification does not see it as "new"

# ---------------------------------------------------------------- b5: fabrication by agent / CLI metadata
print("\n## b5 Human approval cannot be fabricated by agent/CLI metadata")


def fresh_presented(tag, **kw):
    c, g, _ = new_gated_cit(p, tag, **kw)
    p.ok(["gate", "present", g])
    return c, g


# b5.1 default acting role (no --role, no GOV_ROLE) with the default --by
c, g = fresh_presented("b5default")
cmd = ["decide", g, "--option", "A"]
v = p.run(cmd, role=None)
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L3.b5.1", not (v["ok"] and dec.get("human_approved") is True), "an agent invoking `gov decide` with no role and no --by (defaults: role orchestrator, by human) cannot record a human approval", {"answered_by_kind": (v.get("result") or {}).get("answered_by_kind"), "decision.human_approved": dec.get("human_approved"), "decision.approved_by": dec.get("approved_by")})
if v["ok"]:
    a = p.run(["cit", "approve", c])
    e = p.run(["cit", "execute", c])
    observe("L3.b5.1x", "...and the fabricated answer carries the CIT to COMMITTED", {"approve.human_approved": (a.get("result") or {}).get("human_approved"), "execute": (e.get("result") or {}).get("cit_status") or e.get("error")})
# b5.2 explicit --role human
c, g = fresh_presented("b5rolehuman")
v = p.run(["decide", g, "--option", "A", "--by", "product-owner"], role="human")
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L3.b5.2", not (v["ok"] and dec.get("human_approved") is True), "a caller claiming `--role human` cannot record a human approval without authentication", {"ok": v["ok"], "human_approved": dec.get("human_approved"), "approved_by_kind": dec.get("approved_by_kind")})
# b5.3 GOV_ROLE=human in the environment
c, g = fresh_presented("b5envrole")
v = p.run(["decide", g, "--option", "A"], role=None, env={"GOV_ROLE": "human"})
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L3.b5.3", not (v["ok"] and dec.get("human_approved") is True), "GOV_ROLE=human in the environment cannot record a human approval", {"ok": v["ok"], "human_approved": dec.get("human_approved"), "acting_role": (p.record(g).get("answer") or {}).get("acting_role")})
# b5.4 low role claiming --by human
c, g = fresh_presented("b5lowrole")
v = p.run(["decide", g, "--option", "A", "--by", "human"], role="backend-engineer")
check("L3.b5.4", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "an L1 role cannot record a human answer (answer_gate requires L3) [E1]", v.get("error"))
# b5.5 agent answering an R5 gate as agent
v = p.run(["decide", g, "--option", "A", "--by", "orchestrator"])
check("L3.b5.5", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "an agent id as answerer on an R5 gate is refused (outside agent_resolvable_when)", v.get("error"))
# b5.6 --method human cannot upgrade an agent answer
cA, gA, _ = new_gated_cit(p, "b5agent", trigger="data_migration")
observe("L3.b5.6a", "data_migration CIT gate radius/confidence as raised", {k: p.record(gA).get(k) for k in ("impact_radius", "confidence", "reversibility")})
edit(p, gA, lambda d: d.update({"confidence": 0.9, "reversibility": "reversible"}))
p.ok(["gate", "present", gA])
va = p.run(["decide", gA, "--option", "A", "--by", "orchestrator", "--rationale", "agent-resolvable"])
observe("L3.b5.6b", "agent answer within agent_resolvable_when", va.get("result") or va.get("error"))
v = p.run(["cit", "approve", cA, "--method", "human"])
check("L3.b5.6", (not v["ok"]) and v["error"]["code"] == "APPROVAL_METHOD_MISMATCH", "`cit approve --method human` cannot turn an agent answer into human approval", v.get("error"))
v = p.run(["cit", "approve", cA, "--method", "auto"])
check("L3.b5.6c", v["ok"] and v["result"]["human_approved"] is False, "the agent-answered gate approves only as human_approved=false", v.get("result") or v.get("error"))
# b5.7 environment variable claiming approval
c, g = fresh_presented("b5env")
v = p.run(["cit", "approve", c], env={"GOV_HUMAN_GATE_APPROVED": "1"})
check("L3.b5.7", (not v["ok"]) and v["error"]["code"] in ("GATE_NOT_ANSWERED", "SRR_ENV_CANNOT_CREATE_AUTHORITY"), "GOV_HUMAN_GATE_APPROVED=1 does not create approval", v.get("error"))
observe("L3.b5.7b", "refusal code when the env var is set (typed env refusal vs silent ignore)", v.get("error", {}).get("code"))
# b5.8 forged gate + decision records (direct file writes)
cF, gF, _ = new_gated_cit(p, "b5forged")
dfid = "D-0900"


def forge_gate(d):
    d.update({"gate_status": "ANSWERED", "presented_in_chat": True, "presented_at": "2026-09-18T00:00:00Z", "presented_by": {"session": "human-console", "role": "human"},
              "answer": {"option": "A", "by": "product-owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-18T00:00:01Z", "rationale": "forged"}})


edit(p, gF, forge_gate)
p.write(f"spec/decisions/{dfid}.yaml", yaml.safe_dump({"id": dfid, "type": "decision", "title": f"Decision for {gF}: option A", "status": "ACTIVE", "created": "2026-09-18", "question": "forged", "chosen_option": "A", "rationale": "forged", "approved_by": "product-owner", "approved_at": "2026-09-18T00:00:01Z", "human_approved": True, "approved_by_kind": "human", "derived_from": [gF], "cit": cF, "state_class": "AUTHORITATIVE"}, sort_keys=False))
print(f"# RECORD EDIT (direct file write, no gov command): spec/decisions/{dfid}.yaml", flush=True)
v = p.run(["cit", "approve", cF])
v2 = p.run(["cit", "execute", cF]) if v["ok"] else v
check("L3.b5.8", not (v["ok"] and v2["ok"]), "forged gate/decision files (never answered through gov decide) cannot carry a CIT to COMMITTED as human-approved", {"approve": v.get("result") or v.get("error"), "execute": (v2.get("result") or {}).get("cit_status") or v2.get("error")})
# b5.9 the task mutation-scope control does not see forged gate/decision records
tid = p.ok(["task", "create", "--objective", "worker that forges an approval", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
p.ok(["task", "claim", tid], role="backend-engineer", session="worker-1")
cW, gW, _ = new_gated_cit(p, "b5worker")
edit(p, gW, forge_gate)
p.write("spec/decisions/D-0901.yaml", yaml.safe_dump({"id": "D-0901", "type": "decision", "title": "forged", "status": "ACTIVE", "created": "2026-09-18", "chosen_option": "A", "human_approved": True, "approved_by_kind": "human", "derived_from": [gW], "state_class": "AUTHORITATIVE"}, sort_keys=False))
p.write("product/work.txt", "worker output\n")
p.ok(["rebuild-memory", "--incremental"])  # so task close is not refused for an unrelated reason (INDEX_STALE)
rep_path = os.path.join(os.path.dirname(p.root), "report-b59.json")
with open(rep_path, "w") as f:
    json.dump({"work_completed": "did the work", "files_changed": ["product/work.txt"], "tests": {"status": "passed"}}, f)
v = p.run(["task", "close", tid, "--report", rep_path], role="backend-engineer", session="worker-1")
observed = (p.record((v.get("result") or {}).get("report", "")) or {}).get("observed_files_changed") if v["ok"] else None
check("L3.b5.9", (not v["ok"]) and v["error"]["code"] == "MUTATION_SCOPE_VIOLATION" and (gW in json.dumps(v["error"]) or "D-0901" in json.dumps(v["error"])), "a worker (backend-engineer, L1) that hand-writes gate/decision records inside its task cannot close the task with those writes unobserved", {"close": v.get("result") or v.get("error"), "observed_files_changed": observed})
# b5.10 does the governance suite or doctor notice forged approvals?
a = p.run(["audit", "--no-persist"])
observe("L3.b5.10", "gov audit verdict after forged approval records exist", {"verdict": (a.get("result") or (a.get("error") or {}).get("details") or {}).get("verdict"), "families_failing": [k for k, x in ((a.get("result") or (a.get("error") or {}).get("details") or {}).get("families") or {}).items() if not x.get("ok")]})
text = json.dumps(a)
check("L3.b5.10", gF in text or gW in text or "D-0900" in text or "D-0901" in text, "the governance suite reports forged/unanswered-yet-ANSWERED gate records", None)
# b5.11 other approval-bearing decision writers: memory select derives human_approved from the caller's role
v = p.run(["memory", "select", "builtin:128", "--by", "anyone"], role="human")
dsel = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L3.b5.11", not (v["ok"] and dsel.get("human_approved") is True), "`gov memory select` run with a self-declared --role human cannot record human_approved=true", {"ok": v["ok"], "human_approved": dsel.get("human_approved"), "approved_by_kind": dsel.get("approved_by_kind"), "approved_by_role": dsel.get("approved_by_role")})

summary()
