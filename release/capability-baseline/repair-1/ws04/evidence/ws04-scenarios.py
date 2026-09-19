"""P2-AR-0017 (WS-4 repair builder) — builder REGRESSION evidence (Contract v3 O3), not acceptance evidence.

Drives `gov` against disposable projects (fixtures/greenfield) through the surfaces WS-4 owns, for BC-P2-17/19/20/21:
  S1 manifest   (BC-P2-17) `gov context manifest` / packet delivery_state for absent, wrong-type, superseded,
                non-authoritative, constraint-violating and complete manifests; reasons; supplementary context.
  S2 delivery   (BC-P2-19) normative content + version/hash per input; hash tracks content; packet history resolves a
                recorded hash; `gov context verify` detects stale supply; index deleted / corrupted degrades only the
                supplementary block.
  S3 receipt    (BC-P2-20) `gov context receipt` refuses missing fields, fabricated trace, stale consumption, claims
                outside the manifest, missing test evidence; accepts the receipt the packet's receipt_contract asks
                for, in worker-return shape; handoff return records the verdict; receipt fields become lineage.
  S4 identity   (BC-P2-21) `gov artefact show` (nine W1 attributes), `gov artefact check` (misplaced record, stale
                link), edge direction for consumers/producers/report.task/human_gate/required_data/influences.

Reuses the zeta-r audit harness read-only (release/capability-baseline/audit-0/zeta-r/evidence/lib/zprobe.py).
Negative control: WS04_GOV=<base gov> WS04_ROOT=<base checkout> runs the same observations against cap2-candidate-0.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT_HERE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT_HERE, "release", "capability-baseline", "audit-0", "zeta-r", "evidence", "lib"))
import zprobe  # noqa: E402
from zprobe import obs, log, write_record, write_text, read_text, commit, summary, db  # noqa: E402

if os.environ.get("WS04_GOV"):
    zprobe.GOV = os.environ["WS04_GOV"]
if os.environ.get("WS04_ROOT"):
    zprobe.WT = os.environ["WS04_ROOT"]
log(f"gov under test: {zprobe.GOV}; canonical root: {zprobe.WT}")


def spec(root):
    zprobe.base_spec(root, req_ids=("REQ-0002",))
    R = lambda i, t, st="ACTIVE", **kw: write_record(root, f"spec/requirements/{i}.yaml", dict({"id": i, "type": "requirement", "title": t, "status": st, "feature": "F-0001", "kind": "functional"}, **kw))
    R("REQ-0001", "Totals round half up (legacy)", st="SUPERSEDED", superseded_by="REQ-0002")
    R("REQ-0002", "Totals use banker's rounding", supersedes=["REQ-0001"], statement="The ledger SHALL use banker's rounding.")
    R("REQ-0003", "Musing about totals", state_class="NARRATIVE")
    write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001"]})
    write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger API", "status": "ACTIVE", "version": "2.3.1", "contract": {"sig": "total()"}, "consumers": ["TASK-0001"], "producers": ["TASK-0009"]})
    write_record(root, "spec/data/DATA-0001.yaml", {"id": "DATA-0001", "type": "data", "title": "Orders dataset", "status": "ACTIVE"})
    write_record(root, "spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "Rounding research", "status": "ACTIVE", "question": "which?", "conclusion": "bankers", "influences": ["D-0001"]})


def create(g, tid, fields, cls="implementation"):
    return g.run("task", "create", "--id", tid, "--class", cls, "--objective", f"Work {tid}", "--feature", "F-0001", "--status", "DRAFT", "--allowed", "src/**,tests/**", "--fields", json.dumps(fields), quiet=True)


def manifest(g, tid):
    r = g.run("context", "manifest", tid, quiet=True)
    return r.get("result") if r.get("ok") else None


def codes(m, i):
    for e in (m or {}).get("inputs", []):
        if e["id"] == i:
            return [p["code"] for p in e["problems"] if p["blocking"]] or ([e["resolution"]] if e["resolution"] != "RESOLVED" else [])
    return ["NOT_DECLARED"]


G = {}

# ============================================================ S1 manifest (BC-P2-17)
def s1():
    global root, g, pk, rc, rid, p1, p2
    root, g = zprobe.new_project("ws04s1")
    spec(root)
    commit(root, "spec")
    create(g, "TASK-0001", {"requirements": ["REQ-0002"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"], "interfaces": ["API-0001"], "required_data": ["DATA-0001"], "derived_from": ["RES-0001"]})
    create(g, "TASK-0002", {"requirements": ["REQ-0001", "REQ-0003", "REQ-9999", "RES-0001"], "scenarios": ["SCN-0001"]})
    create(g, "TASK-0003", {"required_inputs": [{"id": "API-0001", "version": ">=3.0.0", "reason": "needs the v3 contract"}, {"id": "REQ-0002", "content_hash": "0" * 64, "reason": "pinned rule"}], "scenarios": ["SCN-0001"]})
    create(g, "TASK-0004", {"relations": [{"type": "GOVERNED_BY", "target": "REQ-0002", "note": "the rounding rule this task implements"}], "supplementary_context": ["RES-9999", {"id": "RES-0001", "reason": "background"}], "scenarios": ["SCN-0001"]})
    commit(root, "tasks")
    g.ok("rebuild-memory", quiet=True)
    m1 = manifest(g, "TASK-0001")
    obs("S1-complete-manifest-satisfied", m1 is not None and m1["delivery_state"] == "COMPLETE", f"TASK-0001 manifest delivery_state={(m1 or {}).get('delivery_state')} counts={(m1 or {}).get('counts')}")
    m2 = manifest(g, "TASK-0002")
    obs("S1-superseded-blocks", codes(m2, "REQ-0001") == ["SUPERSEDED"] or "SUPERSEDED" in codes(m2, "REQ-0001"), f"REQ-0001 (SUPERSEDED by REQ-0002): {codes(m2, 'REQ-0001')}")
    obs("S1-non-authoritative-blocks", "AUTHORITY_CLASS" in codes(m2, "REQ-0003"), f"REQ-0003 (NARRATIVE) as requirement: {codes(m2, 'REQ-0003')}")
    obs("S1-absent-blocks", codes(m2, "REQ-9999") == ["ABSENT"], f"REQ-9999: {codes(m2, 'REQ-9999')}")
    obs("S1-wrong-type-blocks", codes(m2, "RES-0001") == ["TYPE_MISMATCH"], f"RES-0001 declared as requirement: {codes(m2, 'RES-0001')}")
    obs("S1-blocked-state", (m2 or {}).get("delivery_state") == "BLOCKED" and {x["id"] for x in m2["missing_inputs"]} == {"REQ-9999", "RES-0001"}, f"delivery_state={(m2 or {}).get('delivery_state')} missing={[x['id'] for x in (m2 or {}).get('missing_inputs', [])]} violations={[x['id'] for x in (m2 or {}).get('input_violations', [])]}")
    m3 = manifest(g, "TASK-0003")
    obs("S1-version-constraint", "VERSION_MISMATCH" in codes(m3, "API-0001"), f"API-0001 at 2.3.1 vs >=3.0.0: {codes(m3, 'API-0001')}")
    obs("S1-hash-pin", "HASH_MISMATCH" in codes(m3, "REQ-0002"), f"REQ-0002 pinned to 000..0: {codes(m3, 'REQ-0002')}")
    m4 = manifest(g, "TASK-0004")
    e4 = [e for e in (m4 or {}).get("inputs", []) if e["id"] == "REQ-0002"]
    obs("S1-relations-note-is-reason", bool(e4) and "the rounding rule this task implements" in (e4[0]["reason"] or "") and "task.relations[GOVERNED_BY]" in e4[0]["declared_in"] and e4[0]["required"], f"relations[] declaration (merged with the feature-inherited declaration of the same id): {e4}")
    obs("S1-supplementary-separate-and-non-blocking", (m4 or {}).get("delivery_state") == "COMPLETE" and {s["id"] for s in m4["supplementary_context"]} == {"RES-9999", "RES-0001"}, f"supplementary={(m4 or {}).get('supplementary_context')}")



# ============================================================ S2 delivery (BC-P2-19)
def s2():
    global root, g, pk, rc, rid, p1, p2
    p1 = g.ok("context", "compile", "TASK-0001", quiet=True)
    det = p1["deterministic_authority"]
    req = [r for r in det["governing_requirements"] if r["id"] == "REQ-0002"]
    obs("S2-normative-content-and-hash", bool(req) and "banker's rounding" in json.dumps(req[0]["content"]) and len(req[0]["content_hash"]) == 64, f"REQ-0002 delivered with content keys={sorted(req[0]['content'].keys()) if req else None} hash={req[0]['content_hash'][:16] if req else None}")
    api = [r for r in det["interfaces"] if r["id"] == "API-0001"]
    obs("S2-version-delivered", bool(api) and api[0]["version"] == "2.3.1", f"API-0001 version={api[0]['version'] if api else None}")
    obs("S2-every-declared-type-delivered", {"DATA-0001"} == {x["id"] for x in det["datasets"]} and "RES-0001" in {x["id"] for x in det["evidence_inputs"]} and "TST-0001" in {x["id"] for x in det["test_designs"]}, f"datasets={[x['id'] for x in det['datasets']]} evidence={[x['id'] for x in det['evidence_inputs']]} tests={[x['id'] for x in det['test_designs']]}")
    obs("S2-input-hashes-and-provenance", p1["input_hashes"].get("REQ-0002") == req[0]["content_hash"] and len(p1["provenance"]["repo_commit"]) == 40, f"input_hashes[REQ-0002]={p1['input_hashes'].get('REQ-0002', '')[:16]} provenance={p1['provenance']}")
    d = json.loads(read_text(root, "spec/requirements/REQ-0002.yaml")); d["statement"] = "The ledger SHALL round half to even, per currency."
    write_record(root, "spec/requirements/REQ-0002.yaml", d); commit(root, "REQ-0002 statement changed")
    v = g.ok("context", "verify", "TASK-0001", quiet=True)
    obs("S2-verify-detects-stale-supply", v["ok"] is False and any(s["id"] == "REQ-0002" for s in v["stale_inputs"]), f"verify after change: ok={v['ok']} stale={[s['id'] for s in v['stale_inputs']]}")
    p2 = g.ok("context", "compile", "TASK-0001", quiet=True)
    obs("S2-hash-tracks-content", p2["deterministic_hash"] != p1["deterministic_hash"] and p2["input_hashes"]["REQ-0002"] != p1["input_hashes"]["REQ-0002"], f"deterministic_hash {p1['deterministic_hash'][:12]} -> {p2['deterministic_hash'][:12]}")
    old = g.run("context", "show", "TASK-0001", "--hash", p1["packet_hash"][:16], quiet=True)
    obs("S2-recorded-hash-resolves", old.get("ok") and old["result"]["input_hashes"]["REQ-0002"] == p1["input_hashes"]["REQ-0002"], f"gov context show --hash {p1['packet_hash'][:16]} -> ok={old.get('ok')}")
    pb = g.ok("context", "compile", "TASK-0002", quiet=True)
    obs("S2-missing-inputs-block-the-packet", pb["delivery_state"] == "BLOCKED" and "REQ-9999" in json.dumps(pb["input_manifest"]["missing_inputs"]), f"TASK-0002 packet delivery_state={pb['delivery_state']}")
    for f in os.listdir(os.path.join(root, ".governance-runtime")):
        if f.startswith("state.db"):
            os.remove(os.path.join(root, ".governance-runtime", f))
    o1 = g.run("context", "compile", "TASK-0001", quiet=True)
    obs("S2-index-deleted-degrades-only-supplementary", o1.get("ok") and o1["result"]["supplementary_state"] == "DEGRADED" and o1["result"]["delivery_state"] == "COMPLETE" and o1["result"]["deterministic_hash"] == p2["deterministic_hash"], f"ok={o1.get('ok')} supplementary={(o1.get('result') or {}).get('supplementary_state')} degraded={(o1.get('result') or {}).get('retrieved_intelligence', {}).get('degraded', {}).get('reasons')}")
    for f in os.listdir(os.path.join(root, ".governance-runtime")):
        if f.startswith("state.db"):
            os.remove(os.path.join(root, ".governance-runtime", f))
    open(os.path.join(root, ".governance-runtime", "state.db"), "wb").write(b"not a database" * 64)
    o2 = g.run("context", "compile", "TASK-0001", quiet=True)
    obs("S2-index-corrupted-degrades-only-supplementary", o2.get("ok") and o2["result"]["deterministic_hash"] == p2["deterministic_hash"], f"ok={o2.get('ok')} error={(o2.get('error') or {}).get('code')} degraded={(o2.get('result') or {}).get('retrieved_intelligence', {}).get('degraded', {}).get('reasons')}")
    os.remove(os.path.join(root, ".governance-runtime", "state.db"))
    g.ok("rebuild-memory", quiet=True)



# ============================================================ S3 receipt (BC-P2-20)
def s3():
    global root, g, pk, rc, rid, p1, p2
    pk = g.ok("context", "compile", "TASK-0001", quiet=True)
    rc = pk["receipt_contract"]
    rdir = os.path.join(root, ".governance-runtime")
    def receipt(name, body):
        f = os.path.join(rdir, f"{name}.json"); json.dump(body, open(f, "w")); return g.run("context", "receipt", "TASK-0001", "--file", f, quiet=True)
    def errs(r):
        return [e["code"] for e in ((r.get("result") or {}).get("errors") or [])]
    bare = receipt("bare", {"work_completed": "x", "files_changed": ["src/lib.rs"], "tests": {"status": "passed"}})
    obs("S3-bare-report-refused", "RECEIPT_FIELDS_MISSING" in errs(bare) and "TRACEABILITY_MISSING" in errs(bare) and "TEST_EVIDENCE_MISSING" in errs(bare), f"bare report errors={errs(bare)}")
    fab = receipt("fab", {"context_packet_hash": pk["packet_hash"], "inputs_consumed": ["REQ-0001@deadbeef"], "files_changed": ["src/lib.rs"], "requirements_implemented": ["REQ-9999"], "decisions_applied": ["D-4242"], "deviations": [], "unresolved": []})
    obs("S3-fabricated-trace-refused", "UNKNOWN_REFERENCE" in errs(fab), f"fabricated receipt errors={errs(fab)} ids={[e['ids'] for e in (fab.get('result') or {}).get('errors', []) if e['code'] == 'UNKNOWN_REFERENCE']}")
    ack = [f"{a['id']}@{a['content_hash']}" for a in rc["acknowledge_inputs"]]
    good = {"task": "TASK-0001", "status": "success", "work_completed": "x", "files_changed": ["src/lib.rs"], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "none",
            "context_packet_hash": pk["packet_hash"], "inputs_consumed": ack, "requirements_implemented": rc["trace"]["requirements"], "scenarios_implemented": rc["trace"]["scenarios"], "decisions_applied": rc["trace"]["decisions"],
            "acceptance_evidence": [{"test": t, "result": "passed", "evidence": "cargo test"} for t in rc["tests_requiring_evidence"]], "deviations": []}
    ok = receipt("good", good)
    obs("S3-contract-receipt-accepted-in-worker-return-shape", (ok.get("result") or {}).get("ok") is True, f"receipt built from receipt_contract (worker-return shape, status=success): ok={(ok.get('result') or {}).get('ok')} errors={errs(ok)} warnings={[w['code'] for w in (ok.get('result') or {}).get('warnings', [])]}")
    outside = dict(good, requirements_implemented=rc["trace"]["requirements"] + ["REQ-0003"])
    r_out = receipt("outside", outside)
    obs("S3-claim-outside-manifest-refused", "CLAIM_OUTSIDE_MANIFEST" in errs(r_out), f"errors={errs(r_out)}")
    stale = dict(good, inputs_consumed=[a.split("@")[0] + "@" + "1" * 64 if a.startswith("REQ-0002") else a for a in ack])
    r_st = receipt("stale", stale)
    obs("S3-stale-consumption-refused", "STALE_CONSUMPTION" in errs(r_st), f"errors={errs(r_st)}")
    h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001", quiet=True)
    wr = os.path.join(rdir, "wr.json"); json.dump({k: good[k] for k in ["task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks", "lessons", "proposed_decisions", "unresolved", "recommended_next_action"]}, open(wr, "w"))
    hr = g.run("handoff", "return", h["id"], "--file", wr, quiet=True)
    hv = (hr.get("result") or {}).get("receipt_validation") or {}
    obs("S3-handoff-return-records-receipt-verdict", hr.get("ok") and hv.get("ok") is False and "INPUT_NOT_ACKNOWLEDGED" in hv.get("errors", []), f"handoff return (schema-valid worker return without receipt fields) receipt_validation={hv}")
    # receipt fields persisted on a report become lineage (the close path persists the report object as given)
    g.ok("task", "status", "TASK-0001", "READY", quiet=True)
    g.ok("task", "claim", "TASK-0001", quiet=True)
    write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn ws04() -> i64 { 0 }\n")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    rep = os.path.join(rdir, "report.json"); json.dump({k: v for k, v in good.items() if k != "status"} | {"outcome": "success", "tests": {"status": "passed", "reason": "ws04"}}, open(rep, "w"))
    cl = g.run("task", "close", "TASK-0001", "--report", rep, quiet=True)
    rid = (cl.get("result") or {}).get("report")
    commit(root, "closed"); g.ok("memory", "rebuild", "--incremental", quiet=True)
    up = g.run("artefact", "lineage", "file:src/lib.rs", "--direction", "up", "--depth", "4", quiet=True)
    upn = {x["node"] for x in ((up.get("result") or {}).get("reach") or [])}
    obs("S3-output-traces-back-to-inputs", cl.get("ok") and {"REQ-0002", "D-0001", rid} <= upn, f"close ok={cl.get('ok')} report={rid}; upstream(file:src/lib.rs)={sorted(upn)}")
    dn = g.run("memory", "impact", "REQ-0002", "--depth", "4", quiet=True)
    dnn = {x["node"] for x in (dn.get("result") or [])}
    obs("S3-input-reaches-outputs", {rid, "file:src/lib.rs", "TASK-0001"} <= dnn, f"impact(REQ-0002)={sorted(dnn)}")



# ============================================================ S4 identity and edges (BC-P2-21)
def s4():
    global root, g, pk, rc, rid, p1, p2
    a = g.run("artefact", "show", "REQ-0002", quiet=True)
    ar = a.get("result") or {}
    nine = ["id", "type", "canonical_dir", "authoritative_status", "lifecycle_state", "content_hash", "provenance", "supersedes", "expected_consumers"]
    obs("S4-nine-w1-attributes", a.get("ok") and all(k in ar for k in nine) and ar["supersedes"] == ["REQ-0001"] and (ar["provenance"]["version_control"].get("introduced_by") or {}).get("commit"), f"artefact show REQ-0002 keys={sorted(ar.keys())} provenance={ar.get('provenance')}")
    a1 = g.run("artefact", "show", "REQ-0001", quiet=True)
    obs("S4-superseded-by-derived", (a1.get("result") or {}).get("superseded_by") == "REQ-0002", f"REQ-0001 superseded_by={(a1.get('result') or {}).get('superseded_by')}")
    write_record(root, "spec/scenarios/REQ-0007.yaml", {"id": "REQ-0007", "type": "requirement", "title": "Misplaced", "status": "ACTIVE", "feature": "F-0001"})
    write_record(root, "spec/tasks/TASK-0008.yaml", {"id": "TASK-0008", "type": "task", "title": "Stale", "status": "ACTIVE", "class": "implementation", "task_status": "READY", "objective": "x", "requirements": ["REQ-0001"], "human_gate": "HDG-0001"})
    commit(root, "misplaced + stale")
    chk = g.run("artefact", "check", quiet=True)
    cr = chk.get("result") or {}
    obs("S4-misplaced-record-reported", any(x["id"] == "REQ-0007" for x in cr.get("misplaced", [])), f"misplaced={cr.get('misplaced')}")
    obs("S4-stale-link-reported", any(x["record"] == "TASK-0008" and x["stale_target"] == "REQ-0001" for x in cr.get("stale_links", [])), f"stale_links={[(x['record'], x['stale_target']) for x in cr.get('stale_links', [])]}")
    g.ok("rebuild-memory", quiet=True)
    def imp(node):
        r = g.run("memory", "impact", node, "--depth", "1", quiet=True)
        return {x["node"]: x["via"] for x in (r.get("result") or [])}
    i_api, i_t1 = imp("API-0001"), imp("TASK-0001")
    obs("S4-consumers-direction", "TASK-0001" in i_api and "API-0001" not in i_t1, f"impact(API-0001)={i_api}; impact(TASK-0001) contains API-0001: {'API-0001' in i_t1}")
    obs("S4-producers-direction", "API-0001" in imp("TASK-0009"), f"impact(TASK-0009, the declared producer)={imp('TASK-0009')}")
    obs("S4-required-data-reaches-task", "TASK-0001" in imp("DATA-0001"), f"impact(DATA-0001)={imp('DATA-0001')}")
    obs("S4-influences-reaches-decision", "D-0001" in imp("RES-0001"), f"impact(RES-0001)={imp('RES-0001')}")
    gr = g.run("memory", "graph", "TASK-0008", "--depth", "1", quiet=True)
    obs("S4-human-gate-blocks-task", any(x["node"] == "HDG-0001" and x["via"] == "←BLOCKS" for x in (gr.get("result") or [])), f"graph(TASK-0008)={[(x['node'], x['via']) for x in (gr.get('result') or [])]}")


root = g = pk = rc = rid = p1 = p2 = None
for fn in (s1, s2, s3, s4):
    try:
        fn()
    except Exception as e:  # a missing surface (negative control) is a FAIL, not a crash
        obs(f"{fn.__name__}-completed", False, f"section aborted: {e!r}")
summary()
