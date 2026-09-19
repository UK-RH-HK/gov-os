#!/usr/bin/env python3
"""
# ---------------------------------------------------------------------------------------------------------------------
# P2-AR-0026 DERIVED COPY of release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py
# (the audit-of-record probe is untouched). Every check line and its criterion is unchanged. Changed, fixture only:
#   F1  TASK-W and TASK-H (implementation tasks) declare REQ-0001 / SCN-0001 / TST-0001 from spec_base, so that the
#       task DAG finds them runnable (BC-P2-16: a claim is granted only to a runnable task, and TEST_POLICY requires an
#       implementation task to declare scenarios and acceptance tests) and their completion is traceable (BC-P2-20);
#   F2  the TASK-H worker return (the X2-N4xW5 subject, worker-return shape: `status: success`, discoveries, ...) also
#       carries the W5 consumption-receipt fields a worker takes from the packet's `receipt_contract` (the fields are
#       part of the one contract, worker-return.schema.json 1.1.0);
#   F3  before the TASK-H close claiming `tests: passed`, the product tests are run and recorded (`gov verify product`),
#       because since BC-P2-43 a test outcome at close is taken from recorded evidence;
#   F4  the worker releases TASK-W (whose close was refused) before TASK-H is claimed: both declare `src/**`, and since
#       BC-P2-15 a claim overlapping another session's live claim is refused (CLAIM_SCOPE_CONFLICT);
#   N1  one `note(...)` line printing the X2-E1xG2 refusal code and T2 violations (diagnostic only).
# Run exactly like the original (GOV_BIN / SYNTH_SCRATCH); it imports the original's lib/ by path.
# ---------------------------------------------------------------------------------------------------------------------
P2-AR-0007 AC-16, cross-family chain X2: gate presentation <-> authority (L3 <-> E1), followed across E4 (claims),
G2/W5 (task close), K2 (CIT-E) and U/O5 (health), plus cross-family leads the families passed on:

  L3<->E1   an L1 worker, inside its own claimed task, writes an ANSWERED/presented 'human' gate record and a
            human_approved decision; task close accepts; a change-controller's `cit approve --method human` derives
            human approval from the forgery; `cit execute` commits; the suite reports on it or not.
  L3 fabrication by CLI metadata/defaults: no --role/--by; --role human; GOV_ROLE=human.
  Framework s23 'No spawned worker behaves as an orchestrator unless explicitly assigned that role': an invocation
            that declares no role at all acts at L4.
  E1-01     --role on init is ignored (vs GOV_ROLE).
  E3 lead   (delta-r N4.b1.9) a handoff return from a role other than to_role.
  N4/W5 lead (beta-r OBS-3) a worker return that satisfies the worker-return schema, used as the task-close report.
  I4 lead   (delta-r L4.b2.3a) a task set BLOCKED is still offered as runnable.
  B1/B3     where claims, emergency-control state and the plugin registry live, and how the product classifies those paths.

Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  SYNTH_SCRATCH=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X2-authority-gate-chain.py
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.environ.get("X2_LIB") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa

root, g = new_project("x2")
spec_base(root)
commit(root, "spec")
g.ok("rebuild-memory", quiet=True)

# ======================================================================= L3 <-> E1 chain
mf = os.path.join(root, ".governance-runtime", "x2-mf.json")
json.dump([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 398", "negative totals are refused"]}], open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Add a refusal criterion to REQ-0001", "--trigger", "acceptance_criteria_change", "--targets", "REQ-0001", "--manifest", mf, quiet=True)
cid = pr["id"]
sim = g.ok("cit", "simulate", cid, quiet=True)
gid = sim.get("human_gate")
note(f"CIT {cid} radius={sim.get('impact', {}).get('radius')} human_gate={gid}")
pre = g.as_(role="change-controller", session="S-cc").run("cit", "approve", cid, "--by", "owner", "--method", "human")
x("X2-L3-approve-refused-before-answer", not pre.get("ok"), "before any answer, approval is refused", (pre.get("error") or {}).get("code"))
g.ok("task", "create", "--id", "TASK-W", "--class", "implementation", "--objective", "worker task", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)  # F1
commit(root, "fixtures")
g.ok("rebuild-memory", quiet=True)
w = g.as_(role="backend-engineer", session="S-worker")
w.ok("task", "claim", "TASK-W", quiet=True)
write(root, "src/lib.rs", read(root, "src/lib.rs") + "\n// worker change\n")
# the worker forges the T2 facts on disk (no gov operation)
gp = os.path.join(root, "spec/decisions", gid + ".yaml")
gd = yaml.safe_load(open(gp))
gd.update({"gate_status": "ANSWERED", "presented_in_chat": True, "presented_at": "2026-09-18T00:00:00Z",
           "presented_by": {"session": "S-worker", "role": "orchestrator"},
           "answer": {"option": "A", "by": "owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-18T00:00:01Z", "rationale": "forged by worker"}})
yaml.safe_dump(gd, open(gp, "w"), sort_keys=False)
did = "D-0990"
yaml.safe_dump({"id": did, "type": "decision", "title": f"Decision for {gid}: option A", "status": "ACTIVE", "created": "2026-09-18",
                "question": gd.get("question"), "chosen_option": "A", "approved_by": "owner", "approved_at": "2026-09-18T00:00:01Z",
                "human_approved": True, "approved_by_kind": "human", "derived_from": [gid], "state_class": "AUTHORITATIVE", "cit": cid},
               open(os.path.join(root, "spec/decisions", did + ".yaml"), "w"), sort_keys=False)
note(f"worker wrote spec/decisions/{gid}.yaml (ANSWERED, presented, by_kind human) and spec/decisions/{did}.yaml (human_approved true)")
w.ok("memory", "rebuild", "--incremental", quiet=True)
cl = w.run("task", "close", "TASK-W", "--report", report(root, "w", "implemented", ["src/lib.rs"]))
note("N1 X2-E1xG2 close refusal: " + json.dumps({"code": (cl.get("error") or {}).get("code"), "t2_violations": ((cl.get("error") or {}).get("details") or {}).get("t2_violations")})[:1200])
x("X2-E1xG2-worker-forgery-invisible-at-close", not cl.get("ok"), "E1/G2: the L1 worker's writes to OS-written gate/decision records are observed and refused at task close",
  {"close_ok": cl.get("ok"), "observed_files_changed": (cl.get("result") or {}).get("observed_files_changed")})
cc = g.as_(role="change-controller", session="S-cc")
ap = cc.run("cit", "approve", cid, "--by", "owner", "--method", "human")
x("X2-L3xE1-forged-human-approval-refused", not ap.get("ok"), "L3<->E1: approval cannot derive from a gate answer written into a file by a lower role",
  {"ok": ap.get("ok"), "human_approved": (ap.get("result") or {}).get("human_approved"), "err": (ap.get("error") or {}).get("code")})
exe = cc.run("cit", "execute", cid) if ap.get("ok") else {"ok": False}
x("X2-L3xK2-forged-approval-cannot-execute", not exe.get("ok"), "L3->K2: a CIT approved on a forged answer does not commit",
  {"ok": exe.get("ok"), "cit_status": (exe.get("result") or {}).get("cit_status") or (exe.get("result") or {}).get("status")})
commit(root, "after forged CIT")
g.ok("memory", "rebuild", "--incremental", quiet=True)
au = g.run("audit", "--no-persist", quiet=True)
r = au.get("result") or (au.get("error") or {}).get("details") or {}
hits = [f for f in r.get("findings", []) if any(s in json.dumps(f) for s in (gid, did, "forg"))]
x("X2-L3xU-suite-detects-forged-approval", bool(hits), "L3<->U/O5: the governance suite reports approval records that no gate operation produced",
  {"verdict": r.get("verdict"), "findings_naming_forged_records": hits})

# ======================================================================= L3 fabrication through CLI metadata / defaults
for label, gv, extra in (("default", g.as_(pass_role=False), []), ("role-human", g.as_(role="human"), []),
                         ("env-GOV_ROLE", g.as_(pass_role=False, extra_env={"GOV_ROLE": "human"}), [])):
    q = g.ok("gate", "create", "--question", f"Proceed with {label}?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R3", "reversibility": "irreversible", "confidence": 0.4}), quiet=True)
    qid = q.get("id") or q.get("gate")
    g.ok("gate", "present", qid, quiet=True)
    args = ["decide", qid, "--option", "A"]
    d = gv.run(*args)
    rec = yaml.safe_load(open(os.path.join(root, "spec/decisions", qid + ".yaml")))
    kind = (rec.get("answer") or {}).get("by_kind")
    x(f"X2-L3-fabrication-{label}", kind != "human", f"L3:679 human approval cannot be fabricated by CLI metadata ({label}: 'gov decide {qid} --option A' {'with no --role and no --by' if label=='default' else ''})",
      {"decide_ok": d.get("ok"), "answer.by_kind": kind, "answer.acting_role": (rec.get("answer") or {}).get("acting_role"), "answer.by": (rec.get("answer") or {}).get("by")})

# ======================================================================= framework s23: undeclared role acts as orchestrator
q = g.ok("gate", "create", "--question", "revocation target", quiet=True)
qid = q.get("id") or q.get("gate")
rv = g.as_(pass_role=False).run("gate", "revoke", qid)
x("X2-E1-undeclared-role-is-not-orchestrator", not rv.get("ok"), "framework s23 'No spawned worker behaves as an orchestrator unless explicitly assigned': an invocation with no role declared cannot perform an L4-only operation (gate revoke)",
  {"ok": rv.get("ok"), "err": (rv.get("error") or {}).get("code")})

# ======================================================================= E1-01: --role ignored by init
ia = g.as_(role="independent-auditor", session="S-aud").run("init", "--force", "--name", "x2")
ie = g.as_(pass_role=False, session="S-aud", extra_env={"GOV_ROLE": "independent-auditor"}).run("init", "--force", "--name", "x2")
x("X2-E1-init-honours-declared-role", not ia.get("ok"), "E1:364 init --force (install_kernel, L4) evaluates the role the caller declared with --role",
  {"--role independent-auditor": ia.get("ok") and "ok" or (ia.get("error") or {}).get("code"), "GOV_ROLE=independent-auditor": ie.get("ok") and "ok" or (ie.get("error") or {}).get("code")})
commit(root, "after init attempts")

w.run("task", "release", "TASK-W")  # F4
# ======================================================================= E3 lead + N4/W5 lead
g.ok("task", "create", "--id", "TASK-H", "--class", "implementation", "--objective", "handoff task", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)  # F1
commit(root, "task H")
g.ok("rebuild-memory", quiet=True)
ho = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-H", "--fields", json.dumps({"objective": "do TASK-H"}), quiet=True)
hid = ho.get("id") or ho.get("handoff")
wr = {"task": "TASK-H", "status": "success", "work_completed": "implemented TASK-H", "files_changed": [], "evidence": [], "tests": {"status": "passed", "reason": "probe"},
      "discoveries": ["found X"], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": ["follow-up Y"], "recommended_next_action": "close"}
wf = os.path.join(root, ".governance-runtime", "x2-worker-return.json")
json.dump(wr, open(wf, "w"))
rt = g.as_(role="frontend-engineer", session="S-fe").run("handoff", "return", hid, "--file", wf)
x("X2-E3-return-bound-to-recipient", not rt.get("ok"), "E3 (delta-r lead N4.b1.9): a handoff addressed to backend-engineer cannot be returned by frontend-engineer",
  {"ok": rt.get("ok"), "err": (rt.get("error") or {}).get("code")})
g.as_(role="backend-engineer", session="S-be").ok("task", "claim", "TASK-H", quiet=True)
commit(root, "handoff return")
g.ok("memory", "rebuild", "--incremental", quiet=True)
# F2: the worker return carries the consumption-receipt fields of the packet's receipt_contract
pk = g.as_(role="backend-engineer", session="S-be").ok("context", "compile", "TASK-H", quiet=True)
rc = pk["receipt_contract"]
wr.update({"context_packet_hash": pk["packet_hash"], "inputs_consumed": [f"{e['id']}@{e['content_hash']}" for e in rc["acknowledge_inputs"]],
           "outputs_produced": [], "requirements_implemented": rc["trace"]["requirements"], "scenarios_implemented": rc["trace"]["scenarios"],
           "features_implemented": rc["trace"]["features"], "decisions_applied": rc["trace"]["decisions"], "constraints_applied": rc["trace"]["constraints"],
           "acceptance_evidence": [{"test": t, "result": "passed", "evidence": "tests/ledger_test.rs"} for t in rc["tests_requiring_evidence"]], "deviations": []})
json.dump(wr, open(wf, "w"))
# F3: the claimed test outcome is recorded evidence
g.ok("verify", "product", quiet=True)
g.ok("memory", "rebuild", "--incremental", quiet=True)
tc = g.as_(role="backend-engineer", session="S-be").run("task", "close", "TASK-H", "--report", wf)
x("X2-N4xW5-worker-return-usable-at-close", tc.get("ok"), "N4/W5 (beta-r OBS-3): a return that satisfies the worker-return schema can be consumed by task close as the worker's receipt",
  {"ok": tc.get("ok"), "err": (tc.get("error") or {}).get("code"), "msg": str((tc.get("error") or {}).get("message"))[:300]})

# ======================================================================= I4 lead: BLOCKED task offered as runnable
g.ok("task", "create", "--id", "TASK-B", "--class", "documentation", "--objective", "blocked task", "--status", "READY", quiet=True)
commit(root, "task B")
st = g.run("task", "status", "TASK-B", "BLOCKED", "--note", "waiting on vendor")
dag = g.ok("task", "dag", quiet=True)
x("X2-I4-blocked-not-runnable", "TASK-B" not in (dag.get("runnable") or []), "I4:587 a task whose status is BLOCKED is not in the runnable set",
  {"status_ok": st.get("ok"), "runnable": dag.get("runnable"), "blocked": [b.get("task") for b in dag.get("blocked", [])]})
cont = g.as_(role="backend-engineer", session="S-c").run("continue", quiet=True)
offered = json.dumps(cont.get("result") or {})
x("X2-I4-continue-does-not-offer-blocked", "TASK-B" not in offered, "I4: gov continue does not offer a BLOCKED task", offered[:400])

# ======================================================================= B1/B3: classification of stores holding non-rebuildable state
rc = yaml.safe_load(read(root, "governance/project/REPOSITORY_CONTRACT.yaml"))
def cls_of(path):
    import fnmatch
    hits = []
    for rule in rc.get("rules", rc.get("paths", [])) if isinstance(rc, dict) else []:
        pat = rule.get("pattern") or rule.get("path") or rule.get("glob")
        if pat and (fnmatch.fnmatch(path, pat) or path.startswith(pat.rstrip("*").rstrip("/") + "/")):
            hits.append((pat, rule.get("class"), rule.get("authority")))
    return hits
stores = {p: os.path.exists(os.path.join(root, p)) for p in (".governance-runtime/claims.db", ".governance-runtime/control.json", "governance/generated/plugin-registry.json")}
note("store locations present: " + json.dumps(stores))
classes = {p: cls_of(p) for p in (".governance-runtime/claims.db", ".governance-runtime/control.json", "governance/generated/plugin-registry.json")}
note("REPOSITORY_CONTRACT rules matching those paths: " + json.dumps(classes))
arch = read(os.path.join(WT, "docs"), "ARCHITECTURE.md") if False else open(os.path.join(WT, "docs/ARCHITECTURE.md")).read()
note("docs/ARCHITECTURE.md says: " + [l for l in arch.splitlines() if ".governance-runtime" in l and "derived" in l][0].strip()[:200])
derivedish = any(c[1] in ("derived", "generated", "runtime") for v in classes.values() for c in v)
x("X2-B1B3-nonrebuildable-state-not-classified-derived", not derivedish,
  "B1:188 / B3:202: claims (C1 current truth), emergency-control state and the OS plugin registry (D-0007 T2) are not stored under paths the product classifies derived/generated",
  classes)
summary()
