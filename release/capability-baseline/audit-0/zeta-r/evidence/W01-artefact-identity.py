"""W1 Stable artefact identity (Contract v3 lines 1068-1080).

For one artefact of every W1-named type, read back from PRODUCT output (index manifest written by `gov rebuild-memory`,
`gov memory graph`, the record the product persisted) whether it has each of the nine W1 attributes:
 b1 stable ID, b2 type, b3 canonical path, b4 authoritative status, b5 lifecycle state, b6 version/content hash,
 b7 producer/provenance, b8 supersedes/superseded-by lineage, b9 expected downstream consumers.
Also: moving a record keeps its ID (challenge "move files while retaining stable IDs"); product-minted artefacts
(task, report, checkpoint, decision from a gate, audit, research from a benchmark, adoption migration plan) are
inspected for producer/provenance and ID stability.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("w1")
base_spec(root)
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Ledger totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["total_cents sums quantity*unit_cents"]})
write_record(root, "spec/requirements/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Ledger totals are exact integer cents with currency", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "supersedes": ["REQ-0001"], "acceptance_criteria": ["total_cents per currency"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "exactness", "affects": ["F-0001"]})
write_record(root, "spec/data/DATA-0001.yaml", {"id": "DATA-0001", "type": "data", "title": "Representative order dataset", "status": "ACTIVE", "consumers": ["TASK-0001"]})
write_record(root, "spec/experiments/EXP-0001.yaml", {"id": "EXP-0001", "type": "experiment", "title": "Rounding experiment", "status": "ACTIVE", "hypothesis": "no drift", "method": "sum", "result": "no drift"})
write_record(root, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Ledger is append-only", "status": "ACTIVE", "summary": "append-only ledger"})
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger API", "status": "ACTIVE", "version": "1.2.0", "contract": {"signature": "fn total_cents() -> i64"}, "consumers": ["TASK-0001"], "producers": ["TASK-0000"]})
commit(root, "spec authored")
t = g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement Ledger totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**,tests/**", "--fields", '{"requirements": ["REQ-0002"], "scenarios": ["SCN-0001"], "decisions": ["D-0001"], "required_data": ["DATA-0001"], "interfaces": ["API-0001"]}')
log("task record as persisted by the product:\n" + read_text(root, "spec/tasks/TASK-0001.yaml"))
reb = g.ok("rebuild-memory", limit=1500)
man = read_json(root, "governance/generated/index-manifest.json")
arts = man.get("artifacts", {})
log("index manifest top-level keys: " + str(sorted(man.keys())))
types = {
    "specification(requirement)": "spec/requirements/REQ-0001.yaml",
    "specification(feature)": "spec/features/F-0001.yaml",
    "scenario": "spec/scenarios/SCN-0001.yaml",
    "decision": "spec/decisions/D-0001.yaml",
    "dataset": "spec/data/DATA-0001.yaml",
    "experiment": "spec/experiments/EXP-0001.yaml",
    "architecture record": "spec/architecture/ARCH-0001.yaml",
    "interface": "spec/interfaces/API-0001.yaml",
    "test design": "spec/tasks/TST-0001.yaml",
    "task": "spec/tasks/TASK-0001.yaml",
}
TYPE_DIR = {"requirement": "spec/requirements", "feature": "spec/features", "scenario": "spec/scenarios", "decision": "spec/decisions", "data": "spec/data", "experiment": "spec/experiments", "architecture": "spec/architecture", "interface": "spec/interfaces", "test-obligation": "spec/tasks", "task": "spec/tasks"}
for label, path in types.items():
    e = arts.get(path)
    log(f"\n--- {label}: manifest entry for {path}: {json.dumps(e)}")
    if not e:
        obs(f"W1-{label}-indexed", False, f"{path} absent from index manifest")
        continue
    obs(f"W1-b1-{label}", bool(e.get("artifact_id")) and not e["artifact_id"].startswith("file:"), f"artifact_id={e.get('artifact_id')}")
    obs(f"W1-b2-{label}", bool(e.get("record_type")), f"record_type={e.get('record_type')}")
    obs(f"W1-b3-{label}", os.path.dirname(path) == TYPE_DIR.get(e.get("record_type"), "?"), f"path={path} canonical_dir_for_type={TYPE_DIR.get(e.get('record_type'))}")
    obs(f"W1-b4-{label}", bool(e.get("state_class")), f"state_class={e.get('state_class')}")
    obs(f"W1-b5-{label}", bool(e.get("status")), f"status={e.get('status')}")
    obs(f"W1-b6-{label}", bool(e.get("content_hash")), f"content_hash={str(e.get('content_hash'))[:16]}...")
    rec_text = read_text(root, path)
    prov_keys = [k for k in ["provenance", "producer", "produced_by", "created_by", "author", "session", "role", "generated_by"] if f'"{k}"' in rec_text or f"\n{k}:" in rec_text]
    obs(f"W1-b7-{label}", bool(prov_keys), f"producer/provenance keys present in persisted record: {prov_keys}")

# b8 lineage
e1, e2 = arts.get("spec/requirements/REQ-0001.yaml", {}), arts.get("spec/requirements/REQ-0002.yaml", {})
obs("W1-b8-superseded_by-computed", e1.get("superseded_by") == "REQ-0002", f"REQ-0001 superseded_by={e1.get('superseded_by')} (REQ-0002 declares supersedes:[REQ-0001])")
gr = g.ok("memory", "graph", "REQ-0002", "--depth", "1")
obs("W1-b8-SUPERSEDES-edge", any(r["node"] == "REQ-0001" and "SUPERSEDES" in r["via"] for r in gr), f"graph REQ-0002 neighbours: {[(r['node'], r['via']) for r in gr]}")
# b9 expected consumers
gi = g.ok("memory", "graph", "API-0001", "--depth", "1")
obs("W1-b9-consumers-recorded", any(r["node"] == "TASK-0001" for r in gi), f"API-0001 graph neighbours: {[(r['node'], r['via']) for r in gi]}")
gd = g.ok("memory", "graph", "DATA-0001", "--depth", "1")
obs("W1-b9-dataset-consumers-recorded", any(r["node"] == "TASK-0001" for r in gd), f"DATA-0001 graph neighbours: {[(r['node'], r['via']) for r in gd]}")

# stable ID across a move (git mv + incremental rebuild)
os.makedirs(os.path.join(root, "spec/requirements/moved"), exist_ok=True)
git(root, "mv", "spec/requirements/REQ-0002.yaml", "spec/requirements/moved/REQ-0002.yaml")
commit(root, "move REQ-0002")
rb = g.ok("rebuild-memory", "--incremental", limit=1500) if False else g.ok("memory", "rebuild", "--incremental", limit=1500)
man2 = read_json(root, "governance/generated/index-manifest.json")["artifacts"]
moved = man2.get("spec/requirements/moved/REQ-0002.yaml", {})
obs("W1-move-keeps-id", moved.get("artifact_id") == "REQ-0002", f"after git mv: manifest entry {moved}; rebuild report moved={rb.get('moved')}")
c = g.ok("context", "compile", "TASK-0001", quiet=True)
reqs = c["deterministic_authority"]["governing_requirements"]
obs("W1-move-still-delivered", any(r["id"] == "REQ-0002" and r["path"].endswith("moved/REQ-0002.yaml") for r in reqs), f"context packet governing_requirements after move: {[(r['id'], r['path']) for r in reqs]}")
# canonical-path discipline: a requirement record placed in the SCENARIOS directory (wrong canonical location for its type)
write_record(root, "spec/scenarios/REQ-0003.yaml", {"id": "REQ-0003", "type": "requirement", "title": "Misplaced requirement", "status": "ACTIVE", "feature": "F-0001"})
commit(root, "misplaced requirement")
g.ok("memory", "rebuild", "--incremental", quiet=True)
dm = g.run("doctor", quiet=True)
dres = dm.get("result") or (dm.get("error") or {}).get("details") or {}
aud = g.run("audit", "--no-persist", quiet=True)
ares = aud.get("result") or (aud.get("error") or {}).get("details") or {}
msgs = [f.get("message", "") for f in ares.get("findings", [])] + [str(c2.get("message", "")) for c2 in dres.get("checks", [])]
log("all audit finding messages: " + json.dumps([f.get("message") for f in ares.get("findings", [])]))
hit = [m for m in msgs if "REQ-0003" in m or "spec/scenarios/REQ-0003" in m]
obs("W1-b3-noncanonical-location-flagged", bool(hit), f"audit/doctor messages naming the misplaced REQ-0003 (requirement stored under spec/scenarios/): {hit}")
os.remove(os.path.join(root, "spec/scenarios/REQ-0003.yaml")); commit(root, "remove misplaced")
# product-minted artefacts: gate-derived decision, report/checkpoint (task close), audit, research (benchmark)
gate = g.ok("gate", "create", "--question", "Adopt integer cents?", "--fields", '{"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "why_now": "w1 probe", "impact": "low", "reversibility": "reversible", "recommendation": "A", "confidence": 0.8, "current_state": "open"}', quiet=True)
gid = gate["id"]
g.ok("gate", "present", gid, quiet=True)
dec = g.with_(role="human").run("decide", gid, "--option", "A", "--by", "owner", "--rationale", "w1 probe")
dec_id = (dec.get("result") or {}).get("decision")
if dec_id:
    drec = [p for p in glob.glob(os.path.join(root, "spec/decisions", f"{dec_id}*"))]
    txt = open(drec[0]).read() if drec else ""
    log(f"gate-derived decision record {dec_id}:\n{txt}")
    obs("W1-b7-gate-decision-provenance", "approved_by" in txt and "derived_from" in txt, "decision minted by `gov decide` carries approved_by/derived_from")
aud1r = g.run("audit", quiet=True)
aud1 = aud1r.get("result") or aud1r["error"]["details"]
aid = aud1["audit"]
atxt = open(glob.glob(os.path.join(root, "spec/audits", f"{aid}*"))[0]).read()
fids1 = [f["id"] for f in aud1["findings"]]
msgs1 = [f["message"] for f in aud1["findings"]]
log(f"audit {aid} finding ids/messages: {list(zip(fids1, msgs1))[:12]}")
obs("W1-b7-audit-provenance", "auditor_role" in atxt and "session" in atxt, f"audit record {aid} carries auditor_role/session")
# introduce one more finding source ahead of existing ones and re-audit: are finding IDs stable?
write_record(root, "spec/requirements/AAA-0001.yaml", {"id": "AAA-0001", "type": "requirement", "title": "x", "status": "BOGUS"})
aud2r = g.run("audit", "--no-persist", quiet=True)
aud2 = aud2r.get("result") or aud2r["error"]["details"]
pairs2 = {f["message"]: f["id"] for f in aud2["findings"]}
shifted = [(m, fid, pairs2.get(m)) for fid, m in zip(fids1, msgs1) if m in pairs2 and pairs2[m] != fid]
obs("W1-b1-audit-finding-id-stable", not shifted, f"same finding message received a different id on the next run: {shifted[:5]}")
os.remove(os.path.join(root, "spec/requirements/AAA-0001.yaml"))
# benchmark results -> research record
hs = g.run("memory", "heldout-starter", quiet=True)
log("heldout-starter: " + jdump(hs, 800))
bm = g.run("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:32", "--record", limit=1500)
rid = (bm.get("result") or {}).get("research_record")
if rid:
    rtxt = open(glob.glob(os.path.join(root, "spec/research", f"{rid}*"))[0]).read()
    log(f"benchmark research record {rid}:\n{rtxt[:1500]}")
    obs("W1-benchmark-result-has-id", True, f"benchmark results persisted as research record {rid}")
    obs("W1-b7-benchmark-provenance", "sources" in rtxt and "method" in rtxt, "research record has sources/method")
    import yaml as _y
    top = sorted((_y.safe_load(rtxt) or {}).keys())
    obs("W1-b6-benchmark-hash-in-record", any(k in top for k in ("version", "content_hash", "hash")), f"top-level keys of the research record (artefact version/hash only via index manifest): {top}")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    rm = read_json(root, "governance/generated/index-manifest.json")["artifacts"]
    ent = [v for k, v in rm.items() if v.get("artifact_id") == rid]
    obs("W1-b6-benchmark-hash-in-manifest", bool(ent) and bool(ent[0].get("content_hash")), f"index-manifest entry for {rid}: {ent}")
else:
    obs("W1-benchmark-result-has-id", False, f"benchmark did not persist a record: {bm.get('error')}")
summary()
