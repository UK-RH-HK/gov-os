"""W10 Deterministic mandatory inputs outrank retrieval (Contract v3 lines 1162-1171): the five hard-invariant attacks,
each by construction.
 a1 current spec is delivered even if absent from the semantic index
 a2 superseded but semantically similar spec cannot replace the current required spec
 a3 token pressure drops supplementary context before mandatory authoritative inputs
 a4 retrieval/index outage does not erase deterministic required dependencies
 a5 required-input delivery is independently testable
"""
import sys, os, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

Q_TITLE = "Compute ledger order totals in integer cents"
def setup(tag):
    root, g = new_project(tag)
    base_spec(root, req_ids=("REQ-0002",))
    # REQ-0001: superseded, worded almost exactly like the task query (maximal semantic/lexical similarity)
    write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Compute ledger order totals in integer cents by summing quantity times unit cents", "status": "SUPERSEDED", "superseded_by": "REQ-0002", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["compute ledger order totals in integer cents"]})
    # REQ-0002: the CURRENT required spec, deliberately worded differently from the query
    write_record(root, "spec/requirements/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Monetary aggregation uses banker's rounding per currency", "status": "ACTIVE", "supersedes": ["REQ-0001"], "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["EUR 2.5 -> 2"]})
    commit(root, "spec")
    g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--title", Q_TITLE, "--objective", Q_TITLE, "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
         "--fields", json.dumps({"requirements": ["REQ-0002"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)
    commit(root, "task")
    g.ok("rebuild-memory", quiet=True)
    return root, g

def req_ids(pk):
    return [r["id"] for r in pk["deterministic_authority"]["governing_requirements"]]

# ------------------------------------------------------------------ a1 current spec absent from the semantic index
root, g = setup("w10a1")
base = g.ok("context", "compile", "TASK-0001", quiet=True)
# (i) by policy: repository-contract rule excluding REQ-0002 from semantic AND lexical indexing
rc_path = os.path.join(root, "governance/project/REPOSITORY_CONTRACT.yaml")
rc = yaml.safe_load(open(rc_path))
key = next(k for k, v in rc.items() if isinstance(v, list) and v and isinstance(v[0], dict) and "pattern" in v[0])
rc[key].append({"pattern": "spec/requirements/REQ-0002.yaml", "class": "authoritative", "namespace": "spec", "semantic_index": False, "lexical_index": False, "graph_index": True})
yaml.safe_dump(rc, open(rc_path, "w"), sort_keys=False)
log(f"[probe] appended contract rule to '{key}': REQ-0002 semantic_index=false lexical_index=false")
commit(root, "exclude REQ-0002 from semantic index")
g.ok("rebuild-memory", quiet=True)
con = db(root)
nvec = con.execute("SELECT COUNT(*) FROM vectors WHERE artifact_id='REQ-0002'").fetchone()[0]
nfts = con.execute("SELECT COUNT(*) FROM chunks_fts WHERE artifact_id='REQ-0002'").fetchone()[0]
con.close()
sq = g.ok("memory", "query", "Monetary aggregation uses banker's rounding per currency", "--route", "semantic", "--k", "20", quiet=True)
log(f"after exclusion: vectors for REQ-0002={nvec}, FTS rows={nfts}; semantic query hits={[h['artifact_id'] for h in sq['hits']]}")
obs("W10-a1-precondition-REQ-0002-absent-from-semantic-index", nvec == 0 and "REQ-0002" not in [h["artifact_id"] for h in sq["hits"]], f"vectors(REQ-0002)={nvec}; semantic query for its own title returns it: {'REQ-0002' in [h['artifact_id'] for h in sq['hits']]}")
p = g.ok("context", "compile", "TASK-0001", quiet=True)
obs("W10-a1-current-spec-delivered-when-not-indexed", "REQ-0002" in req_ids(p) and "REQ-0002" not in [h["artifact_id"] for h in p["retrieved_intelligence"]["ranked_evidence"]], f"deterministic governing_requirements={req_ids(p)}; retrieved ids={[h['artifact_id'] for h in p['retrieved_intelligence']['ranked_evidence']]}")
# (ii) by direct removal of its chunks/vectors from the live index (index damaged/partial)
root, g = setup("w10a1b")
con = db(root)
con.execute("DELETE FROM vectors WHERE artifact_id='REQ-0002'"); con.execute("DELETE FROM chunks_fts WHERE artifact_id='REQ-0002'"); con.execute("DELETE FROM chunks WHERE artifact_id='REQ-0002'"); con.commit(); con.close()
p = g.ok("context", "compile", "TASK-0001", quiet=True)
obs("W10-a1-current-spec-delivered-when-chunks-deleted", "REQ-0002" in req_ids(p), f"REQ-0002 chunks/vectors deleted from state.db; deterministic governing_requirements={req_ids(p)}")

# ------------------------------------------------------------------ a2 superseded + more similar cannot replace current
root, g = setup("w10a2")
hq = g.ok("memory", "query", Q_TITLE + " " + Q_TITLE, "--route", "semantic", "--include-historical", "--k", "20", quiet=True)
ranked = [h["artifact_id"] for h in hq["hits"]]
log("semantic ranking incl. historical for the task query: " + json.dumps([(h["artifact_id"], round(h["score"], 4)) for h in hq["hits"]]))
pos = lambda x: ranked.index(x) if x in ranked else 999
obs("W10-a2-precondition-superseded-ranks-higher", pos("REQ-0001") < pos("REQ-0002"), f"rank(REQ-0001 superseded)={pos('REQ-0001')} rank(REQ-0002 current)={pos('REQ-0002')}")
p = g.ok("context", "compile", "TASK-0001", quiet=True)
ret = [h["artifact_id"] for h in p["retrieved_intelligence"]["ranked_evidence"]]
obs("W10-a2-superseded-not-in-authority-block", req_ids(p) and "REQ-0001" not in req_ids(p) and "REQ-0002" in req_ids(p), f"deterministic governing_requirements={req_ids(p)}")
obs("W10-a2-superseded-not-in-retrieved-block", "REQ-0001" not in ret, f"retrieved ranked_evidence={ret}")
# variant: supersession recorded only on the successor (REQ-0001 still status ACTIVE) -> index derives superseded_by
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["status"] = "ACTIVE"; d.pop("superseded_by", None)
write_record(root, "spec/requirements/REQ-0001.yaml", d); commit(root, "REQ-0001 ACTIVE but superseded by REQ-0002.supersedes")
g.ok("rebuild-memory", quiet=True)
p = g.ok("context", "compile", "TASK-0001", quiet=True)
ret = [h["artifact_id"] for h in p["retrieved_intelligence"]["ranked_evidence"]]
obs("W10-a2-variant-successor-only-supersession", "REQ-0001" not in req_ids(p) and "REQ-0001" not in ret, f"deterministic={req_ids(p)} retrieved={ret}")
# variant: the stale id reaches the structured path (the feature still lists REQ-0001) -> is it delivered as governing?
fd = yaml.safe_load(read_text(root, "spec/features/F-0001.yaml")); fd["requirements"] = ["REQ-0001"]
write_record(root, "spec/features/F-0001.yaml", fd); commit(root, "feature still lists superseded REQ-0001")
p = g.ok("context", "compile", "TASK-0001", quiet=True)
sup = [r for r in p["deterministic_authority"]["governing_requirements"] if r["id"] == "REQ-0001"]
obs("W10-a2-variant-stale-structured-reference", not sup or any(r.get("authority_flag") for r in sup), f"feature lists superseded REQ-0001 -> delivered in governing_requirements as {sup} alongside current {[r['id'] for r in p['deterministic_authority']['governing_requirements'] if r['id']=='REQ-0002']}")

# ------------------------------------------------------------------ a3 token pressure
root, g = setup("w10a3")
p0 = g.ok("context", "compile", "TASK-0001", quiet=True)
pp_path = os.path.join(root, "governance/project/PROJECT_POLICY.yaml")
pp = yaml.safe_load(open(pp_path)); pp.setdefault("policy_overrides", {})
det_chars = len(json.dumps(p0["deterministic_authority"], separators=(",", ":")))
for budget in (det_chars + 1500, det_chars + 400, 300):
    pp["policy_overrides"]["CONTEXT_POLICY.max_packet_chars"] = budget
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
    p = g.ok("context", "compile", "TASK-0001", quiet=True)
    ri = p["retrieved_intelligence"]
    obs(f"W10-a3-budget-{budget}", req_ids(p) == req_ids(p0) and p["deterministic_authority"]["scenarios"] == p0["deterministic_authority"]["scenarios"], f"max_packet_chars={budget}: retrieved slices kept={len(ri['ranked_evidence'])}+{len(ri['lessons_failures'])}+{len(ri['code_references'])} (dropped {ri.get('truncated_slices')}); mandatory requirements={req_ids(p)}; warning={p.get('warning')}")

# ------------------------------------------------------------------ a4 retrieval/index outage
def outage(tag, label, breaker):
    root, g = setup(tag)
    ref = g.ok("context", "compile", "TASK-0001", quiet=True)
    breaker(root, g)
    r = g.run("context", "compile", "TASK-0001", limit=800)
    ok = r.get("ok") and req_ids(r["result"]) == req_ids(ref)
    obs(f"W10-a4-{label}", ok, f"compile ok={r.get('ok')} error={(r.get('error') or {}).get('code')} : {str((r.get('error') or {}).get('message'))[:200]}; mandatory inputs delivered={req_ids(r['result']) if r.get('ok') else None}")
    c = g.run("continue", quiet=True)
    obs(f"W10-a4-{label}-continue", c.get("ok"), f"gov continue ok={c.get('ok')} error={(c.get('error') or {}).get('code')}")
    return r

def rm_db(root, g):
    for f in os.listdir(os.path.join(root, ".governance-runtime")):
        if f.startswith("state.db"):
            os.remove(os.path.join(root, ".governance-runtime", f))
outage("w10a4a", "derived-index-deleted(INV-010)", rm_db)
def corrupt_db(root, g):
    rm_db(root, g)
    open(os.path.join(root, ".governance-runtime", "state.db"), "wb").write(b"this is not a sqlite database" * 100)
outage("w10a4b", "derived-index-corrupted", corrupt_db)
def drop_vectors(root, g):
    con = db(root); con.execute("DROP TABLE vectors"); con.commit(); con.close()
outage("w10a4c", "vector-table-lost", drop_vectors)
def repin_embedder(root, g):
    pp_path = os.path.join(root, "governance/project/PROJECT_POLICY.yaml")
    pp = yaml.safe_load(open(pp_path)); pp.setdefault("policy_overrides", {})["MEMORY_POLICY.embedding.dimensions"] = 256
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
outage("w10a4d", "embedder-repinned-before-reindex(profile-change)", repin_embedder)
def missing_reranker(root, g):
    pp_path = os.path.join(root, "governance/project/PROJECT_POLICY.yaml")
    pp = yaml.safe_load(open(pp_path)); pp.setdefault("policy_overrides", {})["MEMORY_POLICY.reranker.provider"] = "rerank-plugin-not-installed"
    yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
outage("w10a4e", "reranker-unavailable", missing_reranker)

# ------------------------------------------------------------------ a5 required-input delivery independently testable
root, g = setup("w10a5")
p = g.ok("context", "compile", "TASK-0001", quiet=True)
det = p["deterministic_authority"]
obs("W10-a5-deterministic-block-separately-observable", "deterministic_hash" in p and isinstance(det.get("governing_requirements"), list), f"packet exposes deterministic_authority + deterministic_hash independently of retrieved_intelligence (keys {sorted(p.keys())})")
au = g.run("audit", "--no-persist", "--family", "context_reproducibility", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
log("product's own context_reproducibility family: " + json.dumps(ares.get("families")))
obs("W10-a5-product-tests-delivery-against-declaration", any("declared" in json.dumps(f).lower() or "missing input" in json.dumps(f).lower() for f in ares.get("findings", [])) or "declared_inputs" in json.dumps(ares), "the product's own governance suite checks delivered inputs against the task's declared inputs (context_reproducibility compares two compiles of the FIRST task only, for hash stability)")
summary()
