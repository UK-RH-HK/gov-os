"""W8 Forward and reverse lineage (Contract v3 lines 1146-1152).
 l1 outcome/feature -> scenario -> requirement -> decision -> architecture -> task -> code -> test -> evidence -> release
 l2 reverse impact from changed requirement/decision/spec to affected implementation/tests/release evidence
 l3 missing lineage link detection      l4 stale lineage link detection
 l5 cross-language/cross-repository relationships where in scope
A complete chain is authored with the product's own relation fields, the task is executed and closed through the product,
then the product's lineage surfaces (gov memory graph / gov memory impact / gov audit / gov doctor) are queried.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

root, g = new_project("w8")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "decisions": ["D-0001"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Store money as i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001", "ARCH-0001"]})
write_record(root, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Ledger crate owns totals", "status": "ACTIVE", "derived_from": ["D-0001"]})
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Totals HTTP API", "status": "ACTIVE", "contract": {"path": "/totals"}, "producers": ["TASK-0001"]})
commit(root, "chain spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**,tests/**,web/**,py/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "decisions": ["D-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"], "interfaces": ["API-0001"]}), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)
g.ok("context", "compile", "TASK-0001", quiet=True)
g.ok("task", "claim", "TASK-0001", quiet=True)
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\n// implements REQ-0001 (D-0001)\npub fn total_cents_w8() -> i64 { 0 }\n")
write_text(root, "src/web/client.ts", "// consumes API-0001 /totals\nimport { fmt } from './fmt';\nexport async function totals() { return fetch('/totals').then(r => r.json()).then(fmt); }\n")
write_text(root, "src/web/fmt.ts", "export function fmt(x: any) { return x; }\n")
write_text(root, "src/py/server.py", "# produces API-0001 /totals (implements REQ-0001)\nimport util\n\ndef totals():\n    return util.cents()\n")
write_text(root, "src/py/util.py", "def cents():\n    return 0\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
cl = g.ok("task", "close", "TASK-0001", "--report", write_report(root, "r", "implemented totals across rust/ts/python", ["src/lib.rs", "src/web/client.ts", "src/web/fmt.ts", "src/py/server.py", "src/py/util.py"]), quiet=True)
rpt = cl["report"]
commit(root, "closed")
g.ok("memory", "rebuild", "--incremental", quiet=True)

# l1 forward lineage from the feature
fw = g.ok("memory", "graph", "F-0001", "--depth", "10", quiet=True)
reach = {r["node"]: r for r in fw}
chain = ["SCN-0001", "REQ-0001", "D-0001", "ARCH-0001", "TASK-0001", "file:src/lib.rs", "file:tests/ledger_test.rs", rpt]
log("graph(F-0001, depth 10) reaches: " + json.dumps(sorted(reach.keys())))
for n in chain:
    obs(f"W8-l1-forward-reaches:{n}", n in reach, f"{n} reachable from F-0001: {n in reach} via {reach.get(n, {}).get('via')}")
obs("W8-l1-forward-reaches:release", any("release" in k.lower() or k.startswith("REL") for k in reach), "any release artefact in the lineage from F-0001")
# l2 reverse impact from a changed requirement and a changed decision
for seed in ("REQ-0001", "D-0001"):
    imp = g.ok("memory", "impact", seed, "--depth", "6", quiet=True)
    nodes = {r["node"] for r in imp}
    log(f"impact({seed}, depth 6): " + json.dumps(sorted(nodes)))
    obs(f"W8-l2-reverse-impact({seed})->task", "TASK-0001" in nodes, f"TASK-0001 in impact({seed}): {'TASK-0001' in nodes}")
    obs(f"W8-l2-reverse-impact({seed})->implementation", "file:src/lib.rs" in nodes, f"file:src/lib.rs in impact({seed}): {'file:src/lib.rs' in nodes}")
    obs(f"W8-l2-reverse-impact({seed})->tests", "file:tests/ledger_test.rs" in nodes or "TST-0001" in nodes, f"test artefacts in impact({seed}): {[n for n in nodes if 'test' in n.lower() or n.startswith('TST')]}")
    obs(f"W8-l2-reverse-impact({seed})->evidence", rpt in nodes, f"closing report {rpt} in impact({seed}): {rpt in nodes}")
# l3 missing lineage link detection
write_record(root, "spec/features/F-0002.yaml", {"id": "F-0002", "type": "feature", "title": "Refunds (no scenarios, no tests)", "status": "ACTIVE", "readiness": readiness_all_present()})
write_record(root, "spec/tasks/TASK-0002.yaml", {"id": "TASK-0002", "type": "task", "title": "Implement refunds", "status": "ACTIVE", "class": "implementation", "task_status": "READY", "objective": "refunds", "feature": "F-0002", "requirements": ["REQ-4040"]})
commit(root, "missing links")
g.ok("memory", "rebuild", "--incremental", quiet=True)
au = g.run("audit", "--no-persist", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
msgs = [f"{f['severity']} {f['family']}: {f['message']}" for f in ares.get("findings", [])]
log("audit findings: " + json.dumps(msgs, indent=1))
obs("W8-l3-missing-target-link-detected", any("REQ-4040" in m for m in msgs), f"TASK-0002 -> REQ-4040 (absent) reported: {[m for m in msgs if 'REQ-4040' in m]}")
obs("W8-l3-missing-feature-scenario-link-detected", any("F-0002 has no scenarios" in m for m in msgs), f"F-0002 without scenarios reported: {[m for m in msgs if 'F-0002' in m]}")
obs("W8-l3-missing-task-to-code-link-detected", any("TASK-0001" in m and ("code" in m or "lineage" in m) for m in msgs), "DONE TASK-0001 has no task->code lineage edge (files_changed is not a relation); reported by audit")
# l4 stale lineage link detection
write_record(root, "spec/requirements/REQ-0009.yaml", {"id": "REQ-0009", "type": "requirement", "title": "Old refund rule", "status": "SUPERSEDED", "superseded_by": "REQ-0001", "feature": "F-0002"})
write_record(root, "spec/tasks/TASK-0003.yaml", {"id": "TASK-0003", "type": "task", "title": "Implement old refund rule", "status": "ACTIVE", "class": "implementation", "task_status": "READY", "objective": "refunds", "feature": "F-0002", "requirements": ["REQ-0009"], "scenarios": ["SCN-0001"]})
commit(root, "stale link")
g.ok("memory", "rebuild", "--incremental", quiet=True)
au = g.run("audit", "--no-persist", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
msgs = [f"{f['severity']} {f['family']}: {f['message']}" for f in ares.get("findings", [])]
dr = g.run("doctor", quiet=True)
dres = dr.get("result") or (dr.get("error") or {}).get("details") or {}
dm = [f"{c['id']}: {c['message']}" for c in dres.get("checks", []) if not c.get("ok")]
obs("W8-l4-stale-link-to-superseded-detected", any("REQ-0009" in m or "TASK-0003" in m for m in msgs + dm), f"TASK-0003 -> SUPERSEDED REQ-0009: audit/doctor mentions: {[m for m in msgs + dm if 'REQ-0009' in m or 'TASK-0003' in m]}")
# l5 cross-language: rust / typescript / python artefacts joined only through API-0001
gw = g.ok("memory", "graph", "file:src/web/client.ts", "--depth", "1", quiet=True)
gp = g.ok("memory", "graph", "file:src/py/server.py", "--depth", "1", quiet=True)
log("graph(web/client.ts): " + json.dumps([(r["node"], r["via"]) for r in gw]))
log("graph(py/server.py): " + json.dumps([(r["node"], r["via"]) for r in gp]))
obs("W8-l5-intra-language-edges(ts)", any(r["node"] == "file:src/web/fmt.ts" for r in gw), f"src/web/client.ts -> src/web/fmt.ts edge(s): {[r['via'] for r in gw if r['node']=='file:src/web/fmt.ts']}")
obs("W8-l5-intra-language-edges(py)", any(r["node"] == "file:src/py/util.py" for r in gp), f"src/py/server.py -> src/py/util.py edge(s): {[r['via'] for r in gp if r['node']=='file:src/py/util.py']}")
cross = g.ok("memory", "graph", "API-0001", "--depth", "3", quiet=True)
cn = {r["node"] for r in cross}
obs("W8-l5-cross-language-through-interface", "file:src/web/client.ts" in cn and "file:src/py/server.py" in cn, f"API-0001 neighbourhood (depth 3) contains TS consumer / Python producer: ts={'file:src/web/client.ts' in cn} py={'file:src/py/server.py' in cn}")
summary()
