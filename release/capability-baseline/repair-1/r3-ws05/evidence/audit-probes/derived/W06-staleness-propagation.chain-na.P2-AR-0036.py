"""W6 Upstream-change staleness propagation (Contract v3 lines 1128-1136).
When an authoritative upstream artefact changes:
 s1 dependent task evidence becomes stale   s2 implementation/release/test evidence invalidated by impact
 s3 affected context packets invalidated     s4 graph/CIT computes impacted downstream nodes
 s5 revalidation/rework tasks generated      s6 COMPLETE does not imply permanently valid
 s7 stale evidence cannot remain green merely because the original task closed
Path A: the change goes through a Change-Impact Transaction (propose -> simulate -> human gate -> approve -> execute).
Path B: the same kind of change is made directly to the authoritative file (no CIT).
"""
# P2-AR-0036 DERIVED COPY of release/capability-baseline/audit-0/zeta-r/evidence/W06-staleness-propagation.py (P2-AR-0012).
# Changes, and nothing else: (1) the zprobe library is imported from the audit-of-record directory (this copy lives
# elsewhere); (2) the fixture feature states its two scenario-chain cells the probe's fixture does not evidence
# (representative_test_data: the scenario declares no data; independent_acceptance_tests: TST-0001 has no
# independent authorship) as N/A_WITH_REASON, so the implementation tasks are not blocked by the computed readiness
# chain (Contract v3 H3/H4, WS-10 / WS-5 R2-5) before the W6 staleness scenario starts; (3) in B1 the claim of the
# stale task is run with g.run instead of g.ok and recorded as observation DERIVED-W6-B1-claim-of-stale-task (always
# marked PASS: it records the outcome, it does not judge it); B1's remaining steps run only when that claim succeeds.
# Everything else W6 observes is unchanged.

import sys, os, json, glob
sys.path.insert(0, os.path.join(os.environ["WT_AUDIT0_ZETA"], "lib"))
from zprobe import *
import yaml

def setup(tag):
    root, g = new_project(tag)
    base_spec(root, req_ids=("REQ-0001",), extra_feature={"readiness": {**readiness_all_present(),
        "representative_test_data": {"status": "N/A_WITH_REASON", "reason": "probe fixture: literal order values inside the test; no dataset"},
        "independent_acceptance_tests": {"status": "N/A_WITH_REASON", "reason": "probe fixture: the W6 staleness scenario does not exercise test independence"}}})
    write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["2 x 199 = 398"]})
    write_record(root, "spec/data/DATA-0001.yaml", {"id": "DATA-0001", "type": "data", "title": "Representative orders", "status": "ACTIVE"})
    commit(root, "spec")
    for tid in ("TASK-0001", "TASK-0002"):
        g.ok("task", "create", "--id", tid, "--class", "implementation", "--objective", f"Implement totals {tid}", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**,tests/**",
             "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"], "required_data": ["DATA-0001"]}), quiet=True)
    commit(root, "tasks")
    g.ok("rebuild-memory", quiet=True)
    # TASK-0002 is completed (DONE) against the current REQ-0001
    g.ok("context", "compile", "TASK-0002", quiet=True)
    g.ok("task", "claim", "TASK-0002", quiet=True)
    write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_w6() -> i64 { 398 }\n")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    cl = g.ok("task", "close", "TASK-0002", "--report", write_report(root, "r", "implemented totals", ["src/lib.rs"]), quiet=True)
    commit(root, "TASK-0002 done")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    pk1 = g.ok("context", "compile", "TASK-0001", quiet=True)
    pk2 = read_json(root, ".governance-runtime/context/TASK-0002.json")
    au = g.run("audit", quiet=True)
    commit(root, "audit")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    return root, g, cl["report"], pk1, pk2

def snapshot(root, g):
    tasks = {t["id"]: t for t in g.ok("task", "list", quiet=True)}
    tst = yaml.safe_load(read_text(root, "spec/tasks/TST-0001.yaml"))
    scn = yaml.safe_load(read_text(root, "spec/scenarios/SCN-0001.yaml"))
    return tasks, tst, scn

# ------------------------------------------------------------------ Path A: CIT
root, g, rpt, pk1, pk2 = setup("w6a")
pk1 = read_json(root, ".governance-runtime/context/TASK-0001.json"); pk2 = read_json(root, ".governance-runtime/context/TASK-0002.json")
n_tasks_before = len(g.ok("task", "list", quiet=True))
man = [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400 (rounded to whole units)"]}]
mf = os.path.join(root, ".governance-runtime", "cit-manifest.json"); json.dump(man, open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Change REQ-0001 totals to round to whole units", "--trigger", "acceptance_criteria_change", "--targets", "REQ-0001", "--manifest", mf, limit=3000)
cid = pr["id"]
imp = (pr.get("simulation") or {}).get("impact") or {}
log("CIT-P impact: " + json.dumps({k: imp.get(k) for k in ("radius", "affected_tasks", "tests_required", "features", "other")}))
obs("W6-s4-cit-computes-impacted-nodes", "TASK-0001" in (imp.get("affected_tasks") or []) and "TASK-0002" in (imp.get("affected_tasks") or []), f"CIT-P affected_tasks={imp.get('affected_tasks')} tests_required={imp.get('tests_required')}")
gid = (pr.get("simulation") or {}).get("human_gate")
g.ok("gate", "present", gid, quiet=True)
g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", "--rationale", "w6 probe", quiet=True)
g.ok("cit", "approve", cid, "--by", "owner", "--method", "human", quiet=True)
ex = g.run("cit", "execute", cid, limit=3000)
obs("W6-A-cit-executed", ex.get("ok"), f"cit execute -> ok={ex.get('ok')} propagation={(ex.get('result') or {}).get('propagation')}")
commit(root, "after CIT")
tasks, tst, scn = snapshot(root, g)
log("tasks after CIT: " + json.dumps({k: {"task_status": v["task_status"], "retest_required": v["retest_required"]} for k, v in tasks.items()}))
obs("W6-s1-open-dependent-task-stale(CIT)", tasks["TASK-0001"]["retest_required"] is True, f"open TASK-0001 retest_required={tasks['TASK-0001']['retest_required']}")
obs("W6-s6-completed-task-revalidated(CIT)", tasks["TASK-0002"]["retest_required"] is True or tasks["TASK-0002"]["task_status"] != "DONE", f"DONE TASK-0002 after its governing requirement changed: task_status={tasks['TASK-0002']['task_status']} retest_required={tasks['TASK-0002']['retest_required']}")
rdoc = yaml.safe_load(read_text(root, f"spec/reports/{rpt}.yaml"))
obs("W6-s7-closed-task-evidence-not-green(CIT)", bool(rdoc.get("staleness")) or rdoc.get("status") != "ACTIVE", f"closing report {rpt} of TASK-0002: status={rdoc.get('status')} staleness={rdoc.get('staleness')}")
obs("W6-s2-test-evidence-invalidated(CIT)", bool((tst.get("staleness") or {}).get("stale")) or bool((scn.get("staleness") or {}).get("stale")), f"TST-0001 staleness={tst.get('staleness')} SCN-0001 staleness={scn.get('staleness')}")
pk1_after = read_json(root, ".governance-runtime/context/TASK-0001.json")
pk2_after = read_json(root, ".governance-runtime/context/TASK-0002.json")
marker = lambda pk: any(k in pk for k in ("stale", "staleness", "invalidated", "superseded_by"))
obs("W6-s3-context-packets-invalidated(CIT)", marker(pk1_after) and marker(pk2_after), f"TASK-0001 packet byte-identical after CIT: {pk1_after == pk1}, invalidation marker: {marker(pk1_after)}; TASK-0002 packet identical: {pk2_after == pk2}, marker: {marker(pk2_after)}; packets still carry the pre-change acceptance criterion: {'2 x 199 = 398' in json.dumps(pk1_after)}")
ck = g.ok("checkpoint", "latest", quiet=True)
obs("W6-s3-checkpoint-packet-ref-flagged(CIT)", "stale" in json.dumps(ck).lower(), f"latest checkpoint {ck.get('id')} context_packet_hash={str(ck.get('context_packet_hash'))[:12]} (no staleness marker)")
n_tasks_after = len(g.ok("task", "list", quiet=True))
obs("W6-s5-rework-tasks-generated(CIT)", n_tasks_after > n_tasks_before, f"task count before CIT={n_tasks_before} after={n_tasks_after}")
dg = g.ok("task", "dag", quiet=True)
b1 = [b for b in dg["blocked"] if b["task"] == "TASK-0001"]
obs("W6-s1-stale-open-task-blocked(CIT)", bool(b1) and "retest" in json.dumps(b1), f"TASK-0001 in DAG: blocked={b1}")

# ------------------------------------------------------------------ Path A2: CIT at radius R2 (behaviour_change) - test evidence within depth 2
root, g, rpt, pk1, pk2 = setup("w6a2")
man = [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400"]}]
mf = os.path.join(root, ".governance-runtime", "cit-manifest.json"); json.dump(man, open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Totals behaviour: round to whole units", "--trigger", "behaviour_change", "--targets", "REQ-0001", "--manifest", mf, quiet=True)
cid = pr["id"]; imp = (pr.get("simulation") or {}).get("impact") or {}
log("CIT-P (behaviour_change) impact: " + json.dumps({k: imp.get(k) for k in ("radius", "affected_tasks", "tests_required", "features")}))
gid = (pr.get("simulation") or {}).get("human_gate")
if gid:
    g.ok("gate", "present", gid, quiet=True)
    g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", quiet=True)
g.ok("cit", "approve", cid, "--by", "owner", "--method", "human" if gid else "auto", quiet=True)
ex = g.run("cit", "execute", cid, limit=1500)
tasks, tst, scn = snapshot(root, g)
obs("W6-s2-test-evidence-invalidated(CIT,R2)", bool((tst.get("staleness") or {}).get("stale")) and bool((scn.get("staleness") or {}).get("stale")), f"radius={imp.get('radius')} tests_required={imp.get('tests_required')}; TST-0001 staleness={tst.get('staleness')} SCN-0001 staleness={scn.get('staleness')}")
obs("W6-s6-completed-task-revalidated(CIT,R2)", tasks["TASK-0002"]["retest_required"] is True or tasks["TASK-0002"]["task_status"] != "DONE", f"DONE TASK-0002: task_status={tasks['TASK-0002']['task_status']} retest_required={tasks['TASK-0002']['retest_required']}")
dg = g.ok("task", "dag", quiet=True)
obs("W6-s2-stale-test-evidence-blocks-consumers(CIT,R2)", "TASK-0001" not in dg["runnable"], f"TASK-0001 runnable after its acceptance test was marked stale: {'TASK-0001' in dg['runnable']} (blocked reasons: {[b['reasons'] for b in dg['blocked'] if b['task']=='TASK-0001']})")

# ------------------------------------------------------------------ Path B: direct edit, no CIT
def d021(g):
    r = g.run("doctor", quiet=True)
    res = r.get("result") or (r.get("error") or {}).get("details") or {}
    return [c for c in res.get("checks", []) if c.get("id") == "D021"]

def edit_req(root, value):
    d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["acceptance_criteria"] = [value]
    write_record(root, "spec/requirements/REQ-0001.yaml", d)

# ---- B1: ungoverned change BEFORE the worker claims; worker uses the packet compiled before the change
root, g, rpt, pk1, pk2 = setup("w6b1")
pk1 = read_json(root, ".governance-runtime/context/TASK-0001.json")
d021_before = d021(g)
edit_req(root, "2 x 199 = 400 (rounded to whole units)")
commit(root, "direct edit of REQ-0001 (no CIT)")
fr = g.ok("memory", "freshness", quiet=True)
log("freshness after direct edit: " + json.dumps({k: fr.get(k) for k in ("fresh", "stale", "added", "removed")}))
obs("AC16-W6xD1-content-hash-detects-upstream-change", fr.get("fresh") is False and "spec/requirements/REQ-0001.yaml" in json.dumps(fr.get("stale")), f"index freshness after direct edit: fresh={fr.get('fresh')} stale={fr.get('stale')}")
tasks, tst, scn = snapshot(root, g)
obs("W6-s1-open-dependent-task-stale(direct)", tasks["TASK-0001"]["retest_required"] is True, f"open TASK-0001 after an ungoverned change to its governing requirement: task_status={tasks['TASK-0001']['task_status']} retest_required={tasks['TASK-0001']['retest_required']}")
obs("W6-s6-completed-task-revalidated(direct)", tasks["TASK-0002"]["retest_required"] is True or tasks["TASK-0002"]["task_status"] != "DONE", f"DONE TASK-0002: task_status={tasks['TASK-0002']['task_status']} retest_required={tasks['TASK-0002']['retest_required']}")
obs("W6-s2-test-evidence-invalidated(direct)", bool((tst.get("staleness") or {}).get("stale")), f"TST-0001 staleness={tst.get('staleness')}")
c0 = g.run("task", "claim", "TASK-0001")
obs("DERIVED-W6-B1-claim-of-stale-task", True, f"claim of TASK-0001 after the ungoverned change to its governing requirement -> ok={c0.get('ok')} {(c0.get('error') or {}).get('code')}: {str((c0.get('error') or {}).get('message'))[:400]}")
if c0.get("ok"):
    write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_w6b() -> i64 { 398 }\n")
    c_before = g.run("task", "close", "TASK-0001", "--report", write_report(root, "rb", "implemented per packet (2 x 199 = 398)", ["src/lib.rs"]))
    obs("AC16-W6xD1-stale-index-blocks-close", (c_before.get("error") or {}).get("code") == "INDEX_STALE", f"close while index is stale -> {(c_before.get('error') or {}).get('code')}")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    pk1_now = read_json(root, ".governance-runtime/context/TASK-0001.json")
    obs("W6-s3-context-packets-invalidated(direct)", any(k in pk1_now for k in ("stale", "staleness", "invalidated")), f"TASK-0001 packet byte-identical to the pre-change packet: {pk1_now == pk1}; carries pre-change criterion: {'2 x 199 = 398' in json.dumps(pk1_now)}; invalidation marker: {any(k in pk1_now for k in ('stale', 'staleness', 'invalidated'))}")
    c_after = g.run("task", "close", "TASK-0001", "--report", write_report(root, "rb2", "implemented per packet (2 x 199 = 398)", ["src/lib.rs"]))
    ck = g.ok("checkpoint", "latest", quiet=True)
    obs("AC16-W6xD1-rebuild-does-not-license-stale-consumption", not c_after.get("ok"), f"after an index rebuild the dependent task closes on work done against the pre-change packet: ok={c_after.get('ok')}; close checkpoint context_packet_hash={str(ck.get('context_packet_hash'))[:12]} == pre-change packet hash {pk1['packet_hash'][:12]}: {ck.get('context_packet_hash') == pk1['packet_hash']}")
    obs("W6-s1-direct-change-forces-cit", not c_after.get("ok"), "an ungoverned change to an authoritative requirement did not have to pass CIT-E propagation before dependent work closed")
    d021_after = d021(g)
    log(f"D021 before={d021_before} after={d021_after}")
    obs("AC16-W6xO4-green-goes-stale-on-requirement-change", bool(d021_after) and d021_after[0].get("ok") is False, f"governance green record currency (D021) after the authoritative requirement changed: before={[(c['ok'], c['message']) for c in d021_before]} after={[(c['ok'], c['message']) for c in d021_after]}")
    aud = g.run("audit", "--no-persist", quiet=True)
    ares = aud.get("result") or (aud.get("error") or {}).get("details") or {}
    msgs = [f["message"] for f in ares.get("findings", [])]
    log("audit findings after direct edit + rebuild + close: " + json.dumps(msgs))
    obs("W6-s7-stale-evidence-surfaced(direct)", any("REQ-0001" in m or "TASK-0002" in m or "TASK-0001" in m or "stale" in m.lower() for m in msgs), f"audit findings naming the changed requirement / the dependent tasks / staleness: {[m for m in msgs if 'REQ-0001' in m or 'TASK-000' in m or 'stale' in m.lower()]}")

else:
    log("B1 remainder (close on the pre-change packet) not reached: the claim of the stale task is refused until its context is re-delivered at the current inputs")

# ---- B2: ungoverned change DURING the worker's claim (incidental detection)
root, g, rpt, pk1, pk2 = setup("w6b2")
g.ok("task", "claim", "TASK-0001", quiet=True)
edit_req(root, "2 x 199 = 400 (rounded to whole units)")
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_w6b2() -> i64 { 398 }\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
c = g.run("task", "close", "TASK-0001", "--report", write_report(root, "r", "implemented per packet", ["src/lib.rs"]))
err = c.get("error") or {}
obs("W6-B2-concurrent-upstream-change-detected-at-close", not c.get("ok"), f"close after the governing requirement changed during the claim -> {err.get('code')}: undeclared={err.get('details', {}).get('undeclared')} out_of_scope={err.get('details', {}).get('out_of_scope')} (reported as the worker's own undeclared/out-of-scope mutation, not as upstream staleness)")

# ---- B3: CIT change DURING the worker's claim; can close clear the retest flag without retest?
root, g, rpt, pk1, pk2 = setup("w6b3")
g.ok("task", "claim", "TASK-0001", quiet=True)
man = [{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400"]}]
mf = os.path.join(root, ".governance-runtime", "cit-manifest.json"); json.dump(man, open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Totals behaviour: round to whole units", "--trigger", "behaviour_change", "--targets", "REQ-0001", "--manifest", mf, quiet=True)
cid = pr["id"]; gid = (pr.get("simulation") or {}).get("human_gate")
g.ok("gate", "present", gid, quiet=True)
g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", quiet=True)
g.ok("cit", "approve", cid, "--by", "owner", "--method", "human", quiet=True)
g.ok("cit", "execute", cid, quiet=True)
t1 = {t["id"]: t for t in g.ok("task", "list", quiet=True)}["TASK-0001"]
log(f"TASK-0001 after CIT during claim: task_status={t1['task_status']} retest_required={t1['retest_required']}")
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_w6b3() -> i64 { 398 }\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
c = g.run("task", "close", "TASK-0001", "--report", write_report(root, "r", "implemented per the pre-change packet (398)", ["src/lib.rs"]))
t1b = {t["id"]: t for t in g.ok("task", "list", quiet=True)}["TASK-0001"]
obs("W6-s7-retest-flag-not-cleared-by-close", not c.get("ok"), f"TASK-0001 marked retest_required={t1['retest_required']} by CIT-E, then closed with no retest evidence -> close ok={c.get('ok')}; afterwards task_status={t1b['task_status']} retest_required={t1b['retest_required']}")

# ------------------------------------------------------------------ s4 graph impact incl. non-task consumers
imp = g.ok("memory", "impact", "REQ-0001", "--depth", "3", quiet=True)
obs("W6-s4-graph-impact(REQ)", {"TASK-0001", "TASK-0002"} <= {r["node"] for r in imp}, f"impact(REQ-0001) -> {[(r['node'], r['via']) for r in imp]}")
imp_d = g.ok("memory", "impact", "DATA-0001", "--depth", "3", quiet=True)
obs("W6-s4-graph-impact(dataset consumed via task.required_data)", {"TASK-0001", "TASK-0002"} <= {r["node"] for r in imp_d}, f"impact(DATA-0001) -> {[(r['node'], r['via']) for r in imp_d]}")
summary()
