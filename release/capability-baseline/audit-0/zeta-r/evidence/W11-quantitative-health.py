"""W11 Artifact-flow quantitative health (Contract v3 lines 1173-1183).
A project with real artefact-flow activity is built (tasks closed, a superseded spec, a CIT, a stale DONE task, orphans,
a held-out retrieval set). Then EVERY product reporting surface is captured in full and searched for each metric:
 gov telemetry summary | gov audit | gov doctor | gov status | gov memory verify | gov task dag
 m1 required-input delivery accuracy   m2 current-version selection accuracy   m3 superseded-input leakage rate
 m4 missing-required-input detection   m5 staleness propagation accuracy       m6 requirement->code traceability coverage
 m7 requirement->test traceability coverage   m8 orphan-output detection recall/false positives
 m9 fresh-agent reconstruction correctness
"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("w11")
base_spec(root, req_ids=("REQ-0002",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals round half up", "status": "SUPERSEDED", "superseded_by": "REQ-0002", "feature": "F-0001"})
write_record(root, "spec/requirements/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Totals use banker's rounding", "status": "ACTIVE", "supersedes": ["REQ-0001"], "feature": "F-0001"})
write_record(root, "spec/requirements/REQ-0003.yaml", {"id": "REQ-0003", "type": "requirement", "title": "Orphan requirement", "status": "ACTIVE"})
commit(root, "spec")
for tid, reqs in (("TASK-0001", ["REQ-0002"]), ("TASK-0002", ["REQ-0001"]), ("TASK-0003", ["REQ-9999"])):
    g.ok("task", "create", "--id", tid, "--class", "implementation", "--objective", f"Implement totals {tid}", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
         "--fields", json.dumps({"requirements": reqs, "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}), quiet=True)
commit(root, "tasks")
g.ok("rebuild-memory", quiet=True)
g.run("memory", "heldout-starter", quiet=True)  # init already seeds a held-out set; non-fatal
for tid in ("TASK-0001", "TASK-0002"):
    g.ok("context", "compile", tid, quiet=True)
    g.ok("task", "claim", tid, quiet=True)
    write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + f"\npub fn f_{tid.replace('-', '_').lower()}() {{}}\n")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    g.ok("task", "close", tid, "--report", write_report(root, tid, f"implemented {tid}", ["src/lib.rs"]), quiet=True)
    commit(root, f"{tid} done")
g.ok("memory", "rebuild", "--incremental", quiet=True)

surfaces = {}
for name, args in (("telemetry summary", ("telemetry", "summary")), ("audit", ("audit", "--no-persist")), ("doctor", ("doctor",)),
                   ("status", ("status",)), ("memory verify", ("memory", "verify")), ("task dag", ("task", "dag"))):
    r = g.run(*args, quiet=True)
    res = r.get("result") if r.get("ok") else (r.get("error") or {}).get("details")
    surfaces[name] = res
    log(f"\n===== {name} (ok={r.get('ok')}) full output =====\n" + json.dumps(res, indent=1, sort_keys=True)[:12000])

blob = json.dumps(surfaces).lower()
def keys_matching(*pats):
    found = set()
    def walk(v, path=""):
        if isinstance(v, dict):
            for k, x in v.items():
                p = f"{path}.{k}" if path else k
                if any(re.search(pt, k.lower()) for pt in pats):
                    found.add(p)
                walk(x, p)
        elif isinstance(v, list):
            for x in v[:50]:
                walk(x, path + "[]")
    walk(surfaces)
    return sorted(found)

M = {
    "m1-required-input-delivery-accuracy": [r"delivery", r"required_input", r"input_accuracy"],
    "m2-current-version-selection-accuracy": [r"current_version", r"version_selection"],
    "m3-superseded-input-leakage-rate": [r"superseded.*(rate|leak)", r"leak"],
    "m4-missing-required-input-detection": [r"missing_(required_)?input", r"missing_inputs"],
    "m5-staleness-propagation-accuracy": [r"staleness", r"propagation_accuracy", r"stale_propagation"],
    "m6-requirement-to-code-traceability-coverage": [r"requirement.*code", r"req.*code_cov", r"code_traceab"],
    "m7-requirement-to-test-traceability-coverage": [r"requirement.*test", r"test_traceab"],
    "m8-orphan-detection-recall-fp": [r"orphan.*(recall|precision|false)", r"orphan"],
    "m9-fresh-agent-reconstruction-correctness": [r"reconstruction", r"fresh_agent"],
}
# keys whose NAME matches a metric pattern but whose MEANING is a different quantity; each is judged in its own line below
PROXIES = {
    "audit.families.secrets_sensitivity_indexing.detail.leaked_chunks": "secret-pattern chunks in the index (security), not superseded-input leakage",
    "memory verify.superseded_hit_rate": "held-out RETRIEVAL leakage of superseded artefacts (W11-m3-proxy line)",
    "memory verify.thresholds.max_superseded_hit_rate": "threshold for the retrieval proxy above",
    "audit.families.graph_integrity.detail.orphans": "count of records with no edge at all (W11-m8-proxy line)",
    "audit.families.fresh_agent_reconstruction": "read-count vs read-budget family (W11-m9-proxy line)",
    "status.fresh_agent_reads": "list of files a fresh agent should read (W11-m9-proxy line)",
}
log("documented name-matching proxies: " + json.dumps(PROXIES, indent=1))
for mid, pats in M.items():
    ks = keys_matching(*pats)
    real = [k for k in ks if k not in PROXIES]
    log(f"{mid}: keys matching {pats}: {ks}")
    obs(f"W11-{mid}", bool(real), f"metric keys (excluding documented proxies): {real}; proxies matched: {[k for k in ks if k in PROXIES]}")
# the nearest proxies, reported for fairness and judged individually:
mv = surfaces.get("memory verify") or {}
obs("W11-m3-proxy-retrieval-superseded-hit-rate", "superseded_hit_rate" in mv, f"memory verify superseded_hit_rate={mv.get('superseded_hit_rate')} (held-out RETRIEVAL leakage of superseded artefacts; not leakage into mandatory task inputs: TASK-0002 received SUPERSEDED REQ-0001 as a governing requirement and is DONE)")
pt = ((surfaces.get("audit") or {}).get("families") or {}).get("product_traceability") or {}
obs("W11-m6-proxy-task-traceability", "task_traceability" in json.dumps(pt), f"audit product_traceability.detail={pt.get('detail')} (fraction of tasks naming a feature; not requirement->code coverage)")
gi = ((surfaces.get("audit") or {}).get("families") or {}).get("graph_integrity") or {}
obs("W11-m8-proxy-orphan-count", "orphans" in json.dumps(gi), f"audit graph_integrity.detail.orphans={((gi.get('detail') or {}).get('orphans'))} (count only: no recall, no false-positive rate)")
fa = ((surfaces.get("audit") or {}).get("families") or {}).get("fresh_agent_reconstruction") or {}
obs("W11-m9-proxy-fresh-agent-read-budget", "reads" in json.dumps(fa), f"audit fresh_agent_reconstruction.detail={fa.get('detail')} (read-count vs budget; correctness of reconstructed inputs not measured)")
summary()
