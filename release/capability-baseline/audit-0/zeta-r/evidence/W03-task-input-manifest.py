"""W3 Mandatory task-input manifest (Contract v3 lines 1092-1104).
Manifest: m1 required input IDs, m2 required authority/lifecycle state, m3 version/hash constraints, m4 reason per
dependency, m5 supplementary/retrieved context declared separately.
Rules: r1 cannot become READY with an absent mandatory input, r2 superseded input cannot silently satisfy,
r3 conflicting mandatory inputs trigger contradiction handling, r4 required inputs resolved deterministically.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("w3")
base_spec(root, req_ids=("REQ-0002",))
R = lambda i, t, st="ACTIVE", **kw: write_record(root, f"spec/requirements/{i}.yaml", dict({"id": i, "type": "requirement", "title": t, "status": st, "feature": "F-0001", "kind": "functional"}, **kw))
R("REQ-0001", "Totals round half up (legacy)", st="SUPERSEDED", superseded_by="REQ-0002")
R("REQ-0002", "Totals use banker's rounding", supersedes=["REQ-0001"], acceptance_criteria=["2.5 -> 2"])
R("REQ-0005", "Totals are computed per currency")
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Half-up rounding", "status": "ACTIVE", "chosen_option": "A"})
write_record(root, "spec/decisions/D-0002.yaml", {"id": "D-0002", "type": "decision", "title": "Banker's rounding", "status": "ACTIVE", "chosen_option": "B", "supersedes": ["D-0001"]})
commit(root, "w3 spec")
g.ok("rebuild-memory", quiet=True)

def task(tid, fields, status="READY", quiet=True):
    return g.run("task", "create", "--id", tid, "--class", "implementation", "--objective", f"Implement totals {tid}", "--feature", "F-0001",
                 "--status", status, "--allowed", "src/**", "--fields", json.dumps(fields), quiet=quiet)

# m1 required input IDs are declarable and consumed
e = task("TASK-0101", {"requirements": ["REQ-0002"], "decisions": ["D-0002"], "scenarios": ["SCN-0001"], "dependencies": []}, quiet=False)
c = g.ok("context", "compile", "TASK-0101", quiet=True)["deterministic_authority"]
obs("W3-m1-input-ids-declared-and-consumed", "REQ-0002" in [r["id"] for r in c["governing_requirements"]] and "D-0002" in [d["id"] for d in c["active_decisions"]], "declared requirement/decision IDs appear in the compiled deterministic block")

# m2/m3/m4 a manifest carrying required state, hash pin and reason: accepted but inert?
pin = {"required_inputs": [{"id": "REQ-0005", "required_status": "ACTIVE", "content_hash": "0" * 64, "reason": "per-currency totals drive the API"}], "requirements": ["REQ-0005"], "scenarios": ["SCN-0001"]}
e = task("TASK-0102", pin, quiet=False)
obs("W3-m2m3m4-manifest-fields-schema", e.get("ok"), "task schema accepts (does not reject) required_inputs with status/hash/reason (additionalProperties open)")
R("REQ-0005", "Totals are computed per currency (DEPRECATED)", st="DEPRECATED")
commit(root, "REQ-0005 deprecated and content changed (hash pin now violated)")
d = g.ok("task", "dag", quiet=True)
ready = "TASK-0102" in d["runnable"]
obs("W3-m2-required-state-enforced", not ready, f"TASK-0102 requires REQ-0005 ACTIVE; REQ-0005 is now DEPRECATED; TASK-0102 in runnable set: {ready}; blocked entry: {[b for b in d['blocked'] if b['task']=='TASK-0102']}")
obs("W3-m3-hash-pin-enforced", not ready, f"TASK-0102 pins REQ-0005 content_hash 000..0 (never matches); runnable: {ready}")
c = g.ok("context", "compile", "TASK-0102", quiet=True)["deterministic_authority"]
got = [r for r in c["governing_requirements"] if r["id"] == "REQ-0005"]
obs("W3-m4-reason-delivered", any("reason" in r for r in got) or "per-currency totals drive the API" in json.dumps(c), f"dependency reason visible in the compiled packet: {got}")
# m4 via the schema's own relations[].note
e = task("TASK-0103", {"relations": [{"type": "GOVERNED_BY", "target": "REQ-0002", "note": "rounding rule this task implements"}], "scenarios": ["SCN-0001"]})
c = g.ok("context", "compile", "TASK-0103", quiet=True)["deterministic_authority"]
log("TASK-0103 (dependency declared only via relations[] with note) governing_requirements: " + json.dumps(c["governing_requirements"]))
obs("W3-m4-relations-note-dependency-delivered", "rounding rule this task implements" in json.dumps(c), "a dependency declared through the schema's relations[{type,target,note}] reaches the packet with its reason")
# m5 supplementary context declared separately in the task
e = task("TASK-0104", {"requirements": ["REQ-0002"], "supplementary_context": ["RES-9999"], "scenarios": ["SCN-0001"]})
pk = g.ok("context", "compile", "TASK-0104", quiet=True)
obs("W3-m5-supplementary-declared-separately", "RES-9999" in json.dumps(pk["retrieved_intelligence"]), f"task-declared supplementary context reaches retrieved_intelligence: {'RES-9999' in json.dumps(pk)}; packet blocks: {sorted(pk.keys())}")

# r1 cannot become READY with an absent mandatory input (three routes to READY + claim)
e = task("TASK-0201", {"requirements": ["REQ-9999"], "decisions": ["D-9999"], "scenarios": ["SCN-0001"]}, status="READY", quiet=False)
obs("W3-r1-create-READY-with-missing-input", not e.get("ok") or (e["result"].get("task_status") != "READY"), f"task create --status READY with REQ-9999/D-9999 absent -> ok={e.get('ok')} task_status={(e.get('result') or {}).get('task_status')}")
e = task("TASK-0202", {"requirements": ["REQ-9998"], "scenarios": ["SCN-0001"]}, status="BLOCKED")
rp = g.ok("task", "replan", quiet=True)
log("replan changed: " + json.dumps(rp["changed"]))
obs("W3-r1-replan-READY-with-missing-input", not any(ch["task"] == "TASK-0202" and ch["to"] == "READY" for ch in rp["changed"]), f"replan transitions for TASK-0202 (REQ-9998 absent): {[ch for ch in rp['changed'] if ch['task']=='TASK-0202']}")
e = task("TASK-0203", {"requirements": ["REQ-9997"], "scenarios": ["SCN-0001"]}, status="DRAFT")
st = g.run("task", "status", "TASK-0203", "READY")
obs("W3-r1-status-READY-with-missing-input", not st.get("ok"), f"gov task status TASK-0203 READY (REQ-9997 absent) -> ok={st.get('ok')} error={st.get('error')}")
dag = g.ok("task", "dag", quiet=True)
log("dag runnable: " + json.dumps(dag["runnable"]) + " missing_dependencies: " + json.dumps(dag["missing_dependencies"]))
cl = g.run("task", "claim", "TASK-0201")
obs("W3-r1-claim-with-missing-input", not cl.get("ok"), f"gov task claim TASK-0201 (REQ-9999, D-9999 absent) -> ok={cl.get('ok')}")
# contrast: a missing task dependency IS a block reason (task->task only)
e = task("TASK-0204", {"requirements": ["REQ-0002"], "dependencies": ["TASK-9999"], "scenarios": ["SCN-0001"]}, status="BLOCKED")
dag = g.ok("task", "dag", quiet=True)
b = [x for x in dag["blocked"] if x["task"] == "TASK-0204"]
obs("W3-r1-contrast-missing-task-dependency-blocks", bool(b) and "missing" in json.dumps(b), f"TASK-0204 depends on absent TASK-9999: blocked={b}")

# even the task->task rule is bypassed by direct promotion: DRAFT task with an absent task dependency -> status READY -> claim
e = task("TASK-0205", {"requirements": ["REQ-0002"], "dependencies": ["TASK-9998"], "scenarios": ["SCN-0001"]}, status="DRAFT")
st = g.run("task", "status", "TASK-0205", "READY", quiet=True)
cl = g.run("task", "claim", "TASK-0205", quiet=True)
obs("W3-r1-missing-task-dependency-bypass-via-status", not (st.get("ok") and cl.get("ok")), f"TASK-0205 depends on absent TASK-9998: task status READY ok={st.get('ok')}; claim ok={cl.get('ok')} (claim checks task_status only)")

# r2 superseded input cannot silently satisfy a current requirement
e = task("TASK-0301", {"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}, status="BLOCKED")
rp = g.ok("task", "replan", quiet=True)
became_ready = any(ch["task"] == "TASK-0301" and ch["to"] == "READY" for ch in rp["changed"])
c = g.ok("context", "compile", "TASK-0301", quiet=True)["deterministic_authority"]
sup = [r for r in c["governing_requirements"] if r["id"] == "REQ-0001"]
obs("W3-r2-superseded-input-not-silent", (not became_ready) or any(r.get("authority_flag") for r in sup), f"TASK-0301 declares SUPERSEDED REQ-0001: replan->READY={became_ready}; delivered as {[(r['id'], r['status'], r.get('authority_flag')) for r in sup]}")

# r3 conflicting mandatory inputs trigger contradiction handling
e = task("TASK-0401", {"decisions": ["D-0001", "D-0002"], "requirements": ["REQ-0002"], "scenarios": ["SCN-0001"]}, status="BLOCKED")
gates_before = g.ok("gate", "list", quiet=True)
rp = g.ok("task", "replan", quiet=True)
c = g.ok("context", "compile", "TASK-0401", quiet=True)["deterministic_authority"]
gates_after = g.ok("gate", "list", quiet=True)
log("TASK-0401 conflicting_decisions: " + json.dumps(c["conflicting_decisions"]))
became_ready = any(ch["task"] == "TASK-0401" and ch["to"] == "READY" for ch in rp["changed"])
obs("W3-r3-conflict-flagged-in-packet", any(x.get("authority_flag") == "UNKNOWN_OR_CONFLICTING" for x in c["conflicting_decisions"]), "superseded-but-ACTIVE D-0001 flagged UNKNOWN_OR_CONFLICTING in the packet")
obs("W3-r3-conflict-triggers-handling", (not became_ready) or len(gates_after) > len(gates_before), f"TASK-0401 with conflicting mandatory decisions: replan->READY={became_ready}; human gates before={len(gates_before)} after={len(gates_after)}")
# duplicate-ID conflict between two mandatory inputs
write_record(root, "spec/requirements/extra/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Totals round half down (conflicting copy)", "status": "ACTIVE", "feature": "F-0001"})
commit(root, "duplicate REQ-0002 with conflicting content")
e = task("TASK-0402", {"requirements": ["REQ-0002"], "scenarios": ["SCN-0001"]}, status="BLOCKED")
rp = g.ok("task", "replan", quiet=True)
c = g.ok("context", "compile", "TASK-0402", quiet=True)["deterministic_authority"]
became_ready = any(ch["task"] == "TASK-0402" and ch["to"] == "READY" for ch in rp["changed"])
delivered = [(r["id"], r["title"], r["path"]) for r in c["governing_requirements"] if r["id"] == "REQ-0002"]
marked = [r for r in c["governing_requirements"] if r["id"] == "REQ-0002" and (r.get("authority_flag") or r.get("duplicate") or r.get("conflict"))]
obs("W3-r3-duplicate-id-conflict-handled", (not became_ready) or bool(marked), f"two different REQ-0002 records (spec/requirements/ and spec/requirements/extra/): replan->READY={became_ready}; packet delivers {delivered}; entries carrying a conflict/duplicate marker: {marked}")
au = g.run("audit", "--no-persist", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
amsg = [f["message"] for f in ares.get("findings", []) if "REQ-0002" in f["message"] or "D-0001" in f["message"]]
obs("W3-r3-conflicts-detected-by-audit", any("duplicate record id REQ-0002" in m for m in amsg) and any("D-0001" in m for m in amsg), f"gov audit (G5-class) findings naming the conflicting inputs: {amsg}")
dd = g.run("doctor", quiet=True)
dres = dd.get("result") or (dd.get("error") or {}).get("details") or {}
d014 = [c2 for c2 in dres.get("checks", []) if c2.get("id") == "D014"]
obs("W3-r3-conflicts-detected-by-doctor", bool(d014) and d014[0].get("ok") is False, f"gov doctor D014: {d014}")
os.remove(os.path.join(root, "spec/requirements/extra/REQ-0002.yaml")); commit(root, "remove dup")

# r4 deterministic resolution independent of retrieval ranking/index state
h1 = g.ok("context", "compile", "TASK-0101", quiet=True)["deterministic_hash"]
con = db(root); con.execute("DELETE FROM vectors"); con.execute("DELETE FROM chunks_fts"); con.commit(); con.close()
h2 = g.ok("context", "compile", "TASK-0101", quiet=True)["deterministic_hash"]
g.ok("rebuild-memory", quiet=True)
h3 = g.ok("context", "compile", "TASK-0101", quiet=True)["deterministic_hash"]
obs("W3-r4-deterministic-resolution", h1 == h2 == h3, f"deterministic_hash with full index={h1[:12]} / vectors+FTS wiped={h2[:12]} / rebuilt={h3[:12]}")
summary()
