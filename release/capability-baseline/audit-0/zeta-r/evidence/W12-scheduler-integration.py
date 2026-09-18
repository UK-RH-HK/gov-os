"""W12 Health-scheduler integration (Contract v3 lines 1185-1192) and AC-16 W12 <-> O5.
The candidate has no G0-G6 scheduler object (no tier identifiers in runtime/ or cli/; see static-scan line below). Each
tier's Gate-W duty is therefore exercised at the product hook point that plays that tier's role:
 G0 guard  = control::guard_write + authority::require + CIT gate re-validation on privileged commands
 G1 mutation = incremental index freshness / rebuild after mutations
 G2 task close = orchestration::tasks::close
 G3 checkpoint/handoff = checkpoints::create / handoffs::create
 G4 milestone = CIT-E propagation
 G5 full suite = gov audit (all families) + gov doctor
 G6 qualification = (none in product; Phase-4 execution)
"""
import sys, os, json, re, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

# static supporting scan (not behavioural evidence): tier identifiers / health states in product source
hits = []
for base in ("runtime/src", "cli/src"):
    for dp, _, fs in os.walk(os.path.join(WT, base)):
        for f in fs:
            if f.endswith(".rs"):
                t = open(os.path.join(dp, f)).read()
                for pat in (r'"G[0-6]"', r"\bG[0-6] ", r"YELLOW", r"health_scheduler", r"impacted_tests"):
                    for m in re.finditer(pat, t):
                        hits.append(f"{os.path.relpath(os.path.join(dp, f), WT)}:{pat}")
log(f"[static supporting scan] tier/health-state identifiers in runtime/ and cli/: {sorted(set(hits))}")

def setup(tag):
    root, g = new_project(tag)
    base_spec(root, req_ids=("REQ-0002",))
    write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals round half up", "status": "SUPERSEDED", "superseded_by": "REQ-0002", "feature": "F-0001"})
    write_record(root, "spec/requirements/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Totals use banker's rounding", "status": "ACTIVE", "supersedes": ["REQ-0001"], "feature": "F-0001", "acceptance_criteria": ["2.5 -> 2"]})
    write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001"]})
    write_record(root, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Ledger crate owns totals", "status": "ACTIVE", "derived_from": ["D-0001"], "affects": ["F-0001"]})
    commit(root, "spec")
    return root, g

def mk(g, tid, reqs, status="READY", decisions=()):
    g.ok("task", "create", "--id", tid, "--class", "implementation", "--objective", f"Implement totals {tid}", "--feature", "F-0001", "--status", status, "--allowed", "src/**",
         "--fields", json.dumps({"requirements": list(reqs), "decisions": list(decisions), "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)

# ---------------- G0
root, g = setup("w12g0")
mk(g, "TASK-0001", ["REQ-0001"])   # current-version substitution: task consumes the superseded requirement
commit(root, "t"); g.ok("rebuild-memory", quiet=True)
cl = g.run("task", "claim", "TASK-0001")
obs("W12-G0-current-version-substitution-blocked(claim)", not cl.get("ok"), f"privileged claim of a task whose mandatory input is SUPERSEDED REQ-0001 -> ok={cl.get('ok')}")
mf = os.path.join(root, ".governance-runtime", "m.json"); json.dump([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["half up, revised"]}], open(mf, "w"))
pr = g.run("cit", "propose", "--proposal", "Revise the superseded requirement as if it were current", "--trigger", "editorial", "--targets", "REQ-0001", "--manifest", mf, quiet=True)
cid = (pr.get("result") or {}).get("id")
sim = g.run("cit", "simulate", cid, quiet=True)
ap = g.run("cit", "approve", cid, "--by", "agent", "--method", "auto", quiet=True)
ex = g.run("cit", "execute", cid, quiet=True)
obs("W12-G0-superseded-target-substitution-blocked(cit)", not ex.get("ok"), f"CIT editing SUPERSEDED REQ-0001: propose ok={pr.get('ok')} simulate ok={sim.get('ok')} approve ok={ap.get('ok')} execute ok={ex.get('ok')} {(ex.get('error') or {}).get('code')}")
# authority substitution: approval's decision superseded after approval -> execute must refuse
mf2 = os.path.join(root, ".governance-runtime", "m2.json"); json.dump([{"op": "set_field", "target": "REQ-0002", "field": "acceptance_criteria", "value": ["2.5 -> 2 (EUR)"]}], open(mf2, "w"))
pr = g.ok("cit", "propose", "--proposal", "Clarify REQ-0002 acceptance", "--trigger", "acceptance_criteria_change", "--targets", "REQ-0002", "--manifest", mf2, quiet=True)
cid = pr["id"]; gid = pr["simulation"]["human_gate"]
g.ok("gate", "present", gid, quiet=True)
dec = g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", quiet=True)
g.ok("cit", "approve", cid, "--by", "owner", "--method", "human", quiet=True)
dpath = glob.glob(os.path.join(root, "spec/decisions", f"{dec['decision']}*.yaml"))[0]
d = yaml.safe_load(open(dpath)); d["status"] = "SUPERSEDED"; d["superseded_by"] = "D-9000"; yaml.safe_dump(d, open(dpath, "w"))
ex = g.run("cit", "execute", cid, quiet=True)
obs("W12-G0-authority-substitution-blocked(cit execute)", not ex.get("ok") and (ex.get("error") or {}).get("code") in ("GATE_REVOKED", "APPROVAL_STALE"), f"approval decision {dec['decision']} superseded after approval -> execute {(ex.get('error') or {}).get('code')}")

# ---------------- G1
root, g = setup("w12g1")
mk(g, "TASK-0001", ["REQ-0002"]); commit(root, "t"); g.ok("rebuild-memory", quiet=True)
g.ok("context", "compile", "TASK-0001", quiet=True)
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0002.yaml")); d["acceptance_criteria"] = ["2.5 -> 3"]
write_record(root, "spec/requirements/REQ-0002.yaml", d); commit(root, "material mutation of REQ-0002")
fr = g.ok("memory", "freshness", quiet=True)
g.ok("memory", "rebuild", "--incremental", quiet=True)
t = {x["id"]: x for x in g.ok("task", "list", quiet=True)}["TASK-0001"]
pk = read_json(root, ".governance-runtime/context/TASK-0001.json")
obs("W12-G1-mutation-detected(index)", fr.get("fresh") is False, f"index freshness after the mutation: stale={fr.get('stale')}")
marker = any(k in pk for k in ("stale", "staleness", "invalidated"))
obs("W12-G1-dependency-evidence-invalidated", t["retest_required"] or marker, f"top-level invalidation marker on the packet: {marker}; after mutation + incremental rebuild: TASK-0001 retest_required={t['retest_required']}; its packet still carries '2.5 -> 2': {'2.5 -> 2' in json.dumps(pk)}")

# ---------------- G2
root, g = setup("w12g2")
mk(g, "TASK-0001", ["REQ-9999"]); commit(root, "t"); g.ok("rebuild-memory", quiet=True)
g.ok("task", "claim", "TASK-0001", quiet=True)
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn g2() {}\n"); g.ok("memory", "rebuild", "--incremental", quiet=True)
cl = g.run("task", "close", "TASK-0001", "--report", write_report(root, "r", "done", ["src/lib.rs"]), quiet=True)
obs("W12-G2-input-consumption-traceability-verified-at-close", not cl.get("ok"), f"close of a task whose mandatory input REQ-9999 never existed, with no consumption receipt or traceability -> ok={cl.get('ok')}")

# ---------------- G3
root, g = setup("w12g3")
mk(g, "TASK-0001", ["REQ-0002"]); mk(g, "TASK-0002", ["REQ-9999"]); commit(root, "t"); g.ok("rebuild-memory", quiet=True)
g.ok("context", "compile", "TASK-0001", quiet=True)
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0002.yaml")); d["acceptance_criteria"] = ["2.5 -> 3"]
write_record(root, "spec/requirements/REQ-0002.yaml", d); commit(root, "REQ-0002 changed after packet"); g.ok("memory", "rebuild", "--incremental", quiet=True)
h1 = g.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001", quiet=True)
h2 = g.run("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0002", quiet=True)
ck = g.run("checkpoint", "create", "--next-action", "resume TASK-0002", "--task", "TASK-0002", quiet=True)
obs("W12-G3-continuity-verified(stale packet handoff)", not h1.get("ok") or "degraded" in json.dumps(h1.get("result")), f"handoff of TASK-0001 on a stale packet -> ok={h1.get('ok')}")
obs("W12-G3-continuity-verified(missing input handoff)", not h2.get("ok") or "degraded" in json.dumps(h2.get("result")), f"handoff of TASK-0002 (REQ-9999 absent) -> ok={h2.get('ok')}")
obs("W12-G3-continuity-verified(checkpoint)", not ck.get("ok") or "missing" in json.dumps(ck.get("result")), f"checkpoint of TASK-0002 (REQ-9999 absent) -> ok={ck.get('ok')} keys={sorted((ck.get('result') or {}).keys())}")

# ---------------- G4
root, g = setup("w12g4")
mk(g, "TASK-0001", ["REQ-0002"], decisions=["D-0001"]); commit(root, "t"); g.ok("rebuild-memory", quiet=True)
mf = os.path.join(root, ".governance-runtime", "m.json"); json.dump([{"op": "set_field", "target": "D-0001", "field": "chosen_option", "value": "B"}], open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Change money representation decision", "--trigger", "architecture_change", "--targets", "D-0001", "--manifest", mf, quiet=True)
imp = pr["simulation"]["impact"]; gid = pr["simulation"]["human_gate"]
log("G4 CIT-P impact: " + json.dumps({k: imp.get(k) for k in ("radius", "affected_tasks", "tests_required", "features", "other")}))
g.ok("gate", "present", gid, quiet=True); g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", quiet=True)
g.ok("cit", "approve", cid := pr["id"], "--by", "owner", "--method", "human", quiet=True)
ex = g.ok("cit", "execute", cid, quiet=True)
obs("W12-G4-cit-wider-propagation", "TASK-0001" in ex["propagation"]["retest_required"] and len(ex["propagation"]["stale_tests"]) > 0, f"architecture_change radius={imp.get('radius')}: propagation={ex['propagation']}")
root, g = setup("w12g4b")
mk(g, "TASK-0001", ["REQ-0002"], decisions=["D-0001"]); commit(root, "t"); g.ok("rebuild-memory", quiet=True)
a = yaml.safe_load(read_text(root, "spec/architecture/ARCH-0001.yaml")); a["title"] = "Ledger crate no longer owns totals (moved to service)"
write_record(root, "spec/architecture/ARCH-0001.yaml", a); commit(root, "architecture change outside CIT"); g.ok("memory", "rebuild", "--incremental", quiet=True)
t = {x["id"]: x for x in g.ok("task", "list", quiet=True)}["TASK-0001"]
obs("W12-G4-propagation-after-noncit-architecture-change", t["retest_required"], f"architecture record changed without CIT; TASK-0001 retest_required={t['retest_required']}")

# ---------------- G5 and W12 <-> O5: does the health verdict see Gate-W violations?
def g5_project(tag, reqs_for_done, extra_ready=None):
    root, g = setup(tag)
    mk(g, "TASK-0001", reqs_for_done)
    if extra_ready:
        mk(g, "TASK-0002", extra_ready)
    commit(root, "t"); g.ok("rebuild-memory", quiet=True)
    g.ok("context", "compile", "TASK-0001", quiet=True); g.ok("task", "claim", "TASK-0001", quiet=True)
    write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn g5() {}\n"); g.ok("memory", "rebuild", "--incremental", quiet=True)
    g.ok("task", "close", "TASK-0001", "--report", write_report(root, "r", "implemented half-up rounding", ["src/lib.rs"]), quiet=True)
    commit(root, "done"); g.ok("memory", "rebuild", "--incremental", quiet=True)
    au = g.run("audit", quiet=True)
    ares = au.get("result") or (au.get("error") or {}).get("details") or {}
    dr = g.run("doctor", quiet=True)
    dres = dr.get("result") or (dr.get("error") or {}).get("details") or {}
    msgs = [f"{f['severity']} {f['family']}: {f['message']}" for f in ares.get("findings", [])]
    log(f"{tag}: audit verdict={ares.get('verdict')} findings={json.dumps(msgs, indent=1)}; doctor verdict={dres.get('verdict')} failed={[c['id'] for c in dres.get('checks', []) if not c.get('ok')]}")
    return ares, dres, msgs
# (i) ONLY violation: a DONE task whose mandatory input was the SUPERSEDED requirement
ares, dres, msgs = g5_project("w12g5a", ["REQ-0001"])
obs("W12-G5-audits-superseded-consumption", any("TASK-0001" in m or "REQ-0001" in m for m in msgs), f"audit findings naming TASK-0001 / REQ-0001: {[m for m in msgs if 'TASK-0001' in m or 'REQ-0001' in m]}")
obs("AC16-W12xO5-health-state-reflects-superseded-consumption", ares.get("verdict") != "HEALTHY", f"audit verdict={ares.get('verdict')} doctor verdict={dres.get('verdict')} with a DONE task built on a SUPERSEDED requirement as the only Gate-W violation")
# (ii) ONLY violation: a READY task whose mandatory input does not exist
ares, dres, msgs = g5_project("w12g5b", ["REQ-0002"], extra_ready=["REQ-9999"])
obs("W12-G5-audits-missing-input", any("REQ-9999" in m for m in msgs), f"audit findings naming REQ-9999: {[m for m in msgs if 'REQ-9999' in m]}")
obs("AC16-W12xO5-health-state-reflects-missing-input", ares.get("verdict") != "HEALTHY", f"audit verdict={ares.get('verdict')} doctor verdict={dres.get('verdict')} with a READY task whose mandatory input is absent")
obs("W12-G5-audits-end-to-end-lineage", any("lineage" in m.lower() or "untraced" in m.lower() for m in msgs), "an end-to-end lineage audit (requirement->code->test->evidence) appears among the audit families' findings")
obs("AC16-W12xO5-tier-scheduler-present", bool(hits), f"tier/health-state identifiers found in product source: {sorted(set(hits))}")
# G6: execution of hidden artifact-flow fault injection is Phase 4; recorded, not asserted
log("G6: no product surface injects hidden artifact-flow failures; execution belongs to Phase 4 (frozen gate contract section 7) - recorded as N/A_WITH_REASON in capability-audit.yaml, not as an observation")
summary()
