"""W2 Typed output -> input contracts (Contract v3 lines 1082-1090), one demonstration per bullet.
 b1 relationship type explicit            b2 required vs optional explicit     b3 authority semantics preserved
 b4 research cannot silently become decision b5 lessons cannot silently become policy
 b6 historical/retrieved cannot replace current authoritative input
 b7 output schemas define what downstream may consume   b8 relationship types machine-usable
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("w2")
base_spec(root, req_ids=("REQ-0002",))
R = lambda i, t, st="ACTIVE", **kw: write_record(root, f"spec/requirements/{i}.yaml", dict({"id": i, "type": "requirement", "title": t, "status": st, "feature": "F-0001", "kind": "functional"}, **kw))
R("REQ-0001", "Ledger totals are exact integer cents rounding half up legacy", st="SUPERSEDED", superseded_by="REQ-0002")
R("REQ-0002", "Ledger totals use banker's rounding", supersedes=["REQ-0001"])
R("REQ-0003", "Narrative musing about totals", state_class="NARRATIVE")
R("REQ-0004", "Historical totals rule", st="HISTORICAL")
write_record(root, "spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "Research: rounding modes", "status": "ACTIVE", "question": "which rounding?", "conclusion": "use banker's rounding", "affects": ["F-0001"], "influences": ["TASK-0001"]})
write_record(root, "spec/lessons/L-0001.yaml", {"id": "L-0001", "type": "lesson", "title": "Lesson: set CONTEXT_POLICY max_packet_chars to 100", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "scope": "PROJECT", "problem_statement": "policy: CONTEXT_POLICY.max_packet_chars = 100 and forbidden_paths none", "affects": ["TASK-0001"]})
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger API", "status": "ACTIVE", "version": "1.0.0", "contract": {"sig": "total()"}, "consumers": ["TASK-0001"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Half-up rounding", "status": "ACTIVE", "chosen_option": "A"})
write_record(root, "spec/decisions/D-0002.yaml", {"id": "D-0002", "type": "decision", "title": "Banker's rounding", "status": "ACTIVE", "chosen_option": "B", "supersedes": ["D-0001"]})
write_record(root, "spec/decisions/D-0003.yaml", {"id": "D-0003", "type": "decision", "title": "Provisional currency choice", "status": "PROVISIONAL", "chosen_option": "EUR"})
commit(root, "w2 spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement ledger rounding for totals", "--feature", "F-0001", "--status", "READY",
     "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0002", "REQ-0003", "RES-0001", "SCN-0001"], "decisions": ["D-0003", "RES-0001", "L-0001"], "scenarios": ["SCN-0001"], "interfaces": ["API-0001"]}), quiet=True)
g.ok("task", "create", "--id", "TASK-0002", "--class", "implementation", "--objective", "Implement ledger rounding half up legacy", "--feature", "F-0001", "--status", "READY",
     "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001", "REQ-0004"], "decisions": ["D-0001"], "scenarios": ["SCN-0001"]}), quiet=True)
commit(root, "tasks")
g.ok("rebuild-memory", quiet=True)

# b1 relationship types explicit (typed edges produced from record fields)
gr = g.ok("memory", "graph", "TASK-0001", "--depth", "1", quiet=True)
log("TASK-0001 typed neighbours: " + json.dumps([(r["node"], r["via"]) for r in gr]))
obs("W2-b1-typed-edges", all(r["via"][1:] in ("GOVERNED_BY", "VALIDATED_BY", "REALISES", "USES", "CONSUMES", "AFFECTS", "LEARNED_FROM", "DEPENDS_ON", "PRODUCES") for r in gr) and len(gr) >= 4, "every upstream link of TASK-0001 surfaces as a typed edge")

c1 = g.ok("context", "compile", "TASK-0001", quiet=True)
d1 = c1["deterministic_authority"]
log("TASK-0001 deterministic governing_requirements: " + json.dumps(d1["governing_requirements"]))
log("TASK-0001 deterministic active_decisions: " + json.dumps(d1["active_decisions"]))
log("TASK-0001 deterministic conflicting_decisions: " + json.dumps(d1["conflicting_decisions"]))
pk = json.dumps(c1)

# b2 required vs optional explicit: declared inputs carry no required/optional marker; a declared input of the wrong
# type is silently dropped (so 'required' is not enforced), and nothing in the packet says which declared inputs were optional
marker = any(("required" in r or "optional" in r or "mandatory" in r) for r in d1["governing_requirements"])
obs("W2-b2-required-optional-marker", marker, f"per-input required/optional marker in delivered inputs: {marker}")
dropped = [x for x in ["RES-0001", "SCN-0001"] if x not in [r["id"] for r in d1["governing_requirements"]]]
obs("W2-b2-declared-input-drop-is-explicit", ("RES-0001" in json.dumps(d1.get("missing_inputs", []))) or ("dropped" in pk), f"declared requirement inputs not delivered as requirements: {dropped}; any 'missing/dropped' marker in packet: {'missing_inputs' in d1 or 'dropped' in pk}")

# b3 authority semantics preserved: NARRATIVE requirement placed into the deterministic AUTHORITY block unmarked
narr = [r for r in d1["governing_requirements"] if r["id"] == "REQ-0003"]
obs("W2-b3-non-authoritative-not-promoted", not narr or "state_class" in narr[0], f"REQ-0003 (state_class NARRATIVE) delivered in deterministic_authority.governing_requirements as: {narr}")
prov = [d for d in d1["active_decisions"] if d["id"] == "D-0003"]
obs("W2-b3-provisional-decision-marked", bool(prov) and prov[0].get("status") == "PROVISIONAL", f"PROVISIONAL D-0003 delivered in active_decisions carrying status: {prov}")

# b4 research cannot silently become a decision
obs("W2-b4-research-not-decision", "RES-0001" not in [d["id"] for d in d1["active_decisions"]], f"RES-0001 listed in task.decisions; active_decisions ids={[d['id'] for d in d1['active_decisions']]}")
rq = g.ok("memory", "query", "which rounding banker", quiet=True)
obs("W2-b4-research-stays-evidence", all(h["state_class"] != "AUTHORITATIVE" for h in rq["hits"] if h["artifact_id"] == "RES-0001"), f"RES-0001 retrieval hits state_class={[h['state_class'] for h in rq['hits'] if h['artifact_id']=='RES-0001']}")

# b5 lessons cannot silently become authoritative policy
pe = g.ok("policy", "effective", "CONTEXT_POLICY", quiet=True)
log("effective CONTEXT_POLICY: " + json.dumps(pe)[:800])
mpc = json.dumps(pe)
obs("W2-b5-lesson-not-policy", '"max_packet_chars": 60000' in mpc or "60000" in mpc, "effective CONTEXT_POLICY.max_packet_chars unaffected by ACTIVE/AUTHORITATIVE lesson L-0001")
obs("W2-b5-lesson-not-in-authority-block", "L-0001" not in json.dumps(d1), f"L-0001 absent from deterministic_authority (listed in task.decisions): {'L-0001' not in json.dumps(d1)}")

# b6 historical/retrieved cannot replace current authoritative input
ret_ids = [h["artifact_id"] for h in c1["retrieved_intelligence"]["ranked_evidence"]]
obs("W2-b6-retrieval-excludes-superseded", "REQ-0001" not in ret_ids and "REQ-0004" not in ret_ids, f"TASK-0001 retrieved ranked_evidence ids={ret_ids}")
c2 = g.ok("context", "compile", "TASK-0002", quiet=True)
d2 = c2["deterministic_authority"]
log("TASK-0002 governing_requirements: " + json.dumps(d2["governing_requirements"]))
log("TASK-0002 conflicting_decisions: " + json.dumps(d2["conflicting_decisions"]) + " active: " + json.dumps(d2["active_decisions"]))
stale_req = [r for r in d2["governing_requirements"] if r["id"] in ("REQ-0001", "REQ-0004")]
obs("W2-b6-stale-requirement-cannot-replace-current", not stale_req or all(r.get("authority_flag") for r in stale_req), f"TASK-0002 (declares superseded REQ-0001, historical REQ-0004) receives them as governing requirements: {[(r['id'], r['status'], r.get('authority_flag')) for r in stale_req]}; current REQ-0002 delivered: {'REQ-0002' in [r['id'] for r in d2['governing_requirements']]}")
obs("W2-b6-stale-decision-flagged", any(d["id"] == "D-0001" and d.get("authority_flag") for d in d2["conflicting_decisions"]), f"superseded D-0001 flagged in conflicting_decisions: {d2['conflicting_decisions']}")

# b7 output schemas define what downstream stages may consume
schema_dir = os.path.join(WT, "framework", "schemas")
hits = []
for f in sorted(glob.glob(os.path.join(schema_dir, "*.schema.json"))):
    txt = open(f).read()
    for kw in ("may_consume", "consumable", "downstream", "consumed_by", "output_contract"):
        if kw in txt:
            hits.append((os.path.basename(f), kw))
log(f"[static supporting check] schema keywords defining downstream consumption in framework/schemas: {hits}")
obs("W2-b7-output-schema-consumption-rules", bool(hits), f"schema-defined consumption rules found: {hits}; a scenario declared as a requirement input is silently discarded by a hard-coded type filter (SCN-0001 in governing_requirements: {'SCN-0001' in [r['id'] for r in d1['governing_requirements']]})")

# b8 machine-usable relationships: impact traversal over typed edges; direction of CONSUMES from `consumers:` field
imp_req = g.ok("memory", "impact", "REQ-0002", "--depth", "2", quiet=True)
obs("W2-b8-impact-uses-typed-edges", any(r["node"] == "TASK-0001" for r in imp_req), f"impact(REQ-0002) -> {[(r['node'], r['via']) for r in imp_req]}")
imp_api = g.ok("memory", "impact", "API-0001", "--depth", "2", quiet=True)
obs("W2-b8-consumer-reached-from-producer-change", any(r["node"] == "TASK-0001" for r in imp_api), f"API-0001 declares consumers:[TASK-0001]; impact(API-0001) -> {[(r['node'], r['via']) for r in imp_api]}")
imp_task = g.ok("memory", "impact", "TASK-0001", "--depth", "1", quiet=True)
obs("W2-b8-consumes-direction-not-inverted", not any(r["node"] == "API-0001" and "CONSUMES" in r["via"] for r in imp_task), f"impact(TASK-0001) -> {[(r['node'], r['via']) for r in imp_task]} (a change to the CONSUMER propagates to the interface it consumes when the edge is inverted)")
summary()
