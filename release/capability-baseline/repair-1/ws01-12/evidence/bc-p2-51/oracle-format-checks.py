#!/usr/bin/env python3
"""P2-AR-0014 builder regression evidence for BC-P2-51 (not the AC-6 review; a fresh reviewer judges the format).

Drives `target/release/gov oracle format|validate` only. Writes two FORMAT_SAMPLE documents (a brownfield oracle and
a score report against it) to ./samples — synthetic placeholders that describe no qualification repository and are
not hidden faults — then:
  A. both samples validate, and the report validates against the oracle file it names;
  B. for EVERY field the format's own crosswalk maps to a Contract v3 V1-V4 element (read from `gov oracle format`,
     which checks the crosswalk against the approved source bytes), a copy of the sample with that field removed is
     rejected with ORACLE_RECORD_INVALID and a violation at that field tagged with that element;
  C. semantic rules: contradictory / unanchored records are rejected;
  D. binding: a changed oracle or an unscored fault is ORACLE_SCORE_BINDING_MISMATCH;
  E. separation: an oracle stored in, or leaked into, the repository / public suite is ORACLE_SEPARATION_VIOLATED;
  F. the audit's own records (epsilon-r V probe: a "fault-manifest" record lacking every V1 field) are rejected.
usage (worktree root, after `cargo build --release`): python3 <this file> <scratch dir>
"""
import copy, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.path.join(WT, "target/release/gov")
SCR = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="p2ar0014-bc51-")
os.makedirs(SCR, exist_ok=True)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
results = []


def gov(*args):
    r = subprocess.run([GOV, "--json", *args], capture_output=True, text=True, env=ENV)
    return r.returncode, json.loads(r.stdout)


def write(path, doc):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")


rc, fmt = gov("oracle", "format")
F = fmt["result"]
print(f"# gov sha256 {subprocess.run(['sha256sum', GOV], capture_output=True, text=True).stdout.split()[0]}; worktree HEAD {subprocess.run(['git', '-C', WT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
print(f"# format {F['format']} v{F['format_version']} format_sha256 {F['format_sha256']}; crosswalk entries {len(F['crosswalk'])}")
with open(os.path.join(HERE, "gov-oracle-format.json"), "w", encoding="utf-8") as f:
    json.dump(F, f, indent=2, ensure_ascii=False)

P = "FORMAT SAMPLE placeholder"
ORACLE = {
    "format": F["format"], "format_version": F["format_version"], "format_sha256": F["format_sha256"],
    "kind": "qualification-oracle", "purpose": "FORMAT_SAMPLE", "oracle_id": "FORMAT-SAMPLE-ORACLE-1",
    "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "FORMAT-SAMPLE", "authored_independently_of_implementation": True, "created_at": "2026-09-19T00:00:00Z"},
    "visibility": "HIDDEN",
    "repository": {"id": "format-sample-repository", "adoption_mode": "BROWNFIELD", "commit": "0" * 40, "label": P},
    "separation": {"public_qualification_suite": "sample/public-suite", "qualification_repository": "sample/repository", "oracle_storage": "sample/verifier-custody/oracle.json"},
    "fault_manifest": {"faults": [
        {"fault_id": "SAMPLE-F1", "class": {"id": "SAMPLE_CLASS_W", "capabilities": ["W3"], "challenge_ids": ["AQC-W12"]},
         "hidden_authoritative_truth": {"statement": f"{P}: the truth statement of sample fault one", "authoritative_refs": ["sample/a"]},
         "injected_repository_state": {"description": f"{P}: injected state", "changes": [{"path": "sample/a", "change": "MODIFIED"}, {"path": "sample/b", "change": "RENAMED", "from_path": "sample/b0"}]},
         "expected_detection": {"tiers": ["G2"], "signals": ["SAMPLE_SIGNAL"], "must_detect_before": "task close"},
         "expected_severity": "HIGH",
         "expected_impacted": [{"ref": "sample/task", "ref_kind": "TASK", "relation": "DIRECT"}, {"ref": "sample/c", "ref_kind": "PATH", "relation": "TRANSITIVE"}],
         "expected_governed_action": [{"action": "BLOCK_CLOSE", "target": "sample/task", "description": f"{P}: governed action"}],
         "forbidden_outcomes": [{"outcome": f"{P}: forbidden outcome", "observable": f"{P}: how it is observed"}],
         "artifact_flow": {"required_inputs": [{"artefact_id": "sample/a", "version": "2"}], "expected_propagation": [{"ref": "sample/task", "expected_state": "STALE"}]}},
        {"fault_id": "SAMPLE-F2", "class": {"id": "SAMPLE_CLASS_A", "capabilities": ["A3"]},
         "hidden_authoritative_truth": {"statement": f"{P}: the truth statement of sample fault two", "authoritative_refs": []},
         "injected_repository_state": {"description": f"{P}: injected state", "changes": [{"path": "sample/secret", "change": "ADDED"}]},
         "expected_detection": {"tiers": ["G1"], "signals": ["SAMPLE_SIGNAL_2"], "must_detect_before": "the next index build"},
         "expected_severity": "CRITICAL",
         "expected_impacted": [{"ref": "sample/secret", "ref_kind": "PATH", "relation": "DIRECT"}],
         "expected_governed_action": [{"action": "QUARANTINE", "description": f"{P}: governed action"}],
         "forbidden_outcomes": [{"outcome": f"{P}: forbidden outcome", "observable": f"{P}: how it is observed"}]},
    ]},
    "path_map_oracle": {"entries": [
        {"current_artefact": {"path": "sample/a"}, "correct_classification": "sample-class", "authority": "sample-authority", "expected_target_paths": ["sample/a"], "action": "KEEP", "expected_references": ["sample/c"], "expected_consumers": ["sample/task"], "sensitivity": "sample-sensitivity", "indexing_expectation": "INDEX_CURRENT"},
        {"current_artefact": {"path": "sample/old"}, "correct_classification": "sample-class", "authority": "sample-authority", "expected_target_paths": ["sample/archive/old"], "action": "MOVE", "expected_references": [], "expected_consumers": [], "sensitivity": "sample-sensitivity", "indexing_expectation": "INDEX_HISTORICAL"},
    ]},
    "memory_oracle": {
        "must_be_indexed": [{"ref": "sample/a", "routes": ["STRUCTURED"]}],
        "must_never_be_indexed": [{"ref": "sample/secret", "reason": f"{P}: reason"}],
        "expected_authority_namespaces": [{"ref": "sample/a", "namespace": "sample-namespace"}],
        "expected_status": [{"ref": "sample/a", "status": "CURRENT"}, {"ref": "sample/old", "status": "SUPERSEDED", "superseded_by": "sample/a"}],
        "expected_graph_relationships": [{"from": "sample/c", "relation": "IMPLEMENTS", "to": "sample/a"}],
        "expected_code_symbols": [{"path": "sample/c", "symbol": "sample_symbol", "symbol_kind": "function"}],
        "expected_retrieval_results": [{"query_id": "SQ1", "query": f"{P}: query", "top_k": 5, "must_include": ["sample/a"], "must_not_include": ["sample/old"]}],
    },
}
op = write(os.path.join(HERE, "samples", "format-sample.oracle.json"), ORACLE)
rc, v = gov("oracle", "validate", op)
check("A1 the FORMAT_SAMPLE oracle conforms", rc == 0 and v["result"]["verdict"] == "RECORD_CONFORMS_TO_FORMAT", json.dumps(v.get("result", v.get("error")))[:200])
digest = v["result"]["canonical_sha256"]
REPORT = {
    "format": F["format"], "format_version": F["format_version"], "format_sha256": F["format_sha256"],
    "kind": "qualification-score-report", "purpose": "FORMAT_SAMPLE", "report_id": "FORMAT-SAMPLE-REPORT-1",
    "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "FORMAT-SAMPLE", "authored_independently_of_implementation": True, "created_at": "2026-09-19T00:00:00Z"},
    "binding": {"oracle_id": "FORMAT-SAMPLE-ORACLE-1", "oracle_sha256": digest, "repository": {"id": "format-sample-repository", "commit": "0" * 40}, "candidate": {"commit": "1" * 40, "product_code_digest": "2" * 64}, "run_id": "FORMAT-SAMPLE-RUN", "scored_at": "2026-09-19T01:00:00Z"},
    "metrics": {
        "injected_defect_detection_recall": {"numerator": 1, "denominator": 2, "value": 0.5},
        "false_positives": {"count": 0, "findings": []},
        "severity_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
        "impact_map_accuracy": {"numerator": 2, "denominator": 3, "value": 2 / 3},
        "path_map_accuracy": {"numerator": 2, "denominator": 2, "value": 1.0},
        "missed_authoritative_artefacts": {"count": 0, "refs": []},
        "wrong_indexing_count": {"count": 1, "refs": ["sample/secret"]},
        "stale_index_count": {"count": 0, "refs": []},
        "retrieval_metrics": {"k": 5, "queries": 1, "recall_at_k": 1.0, "mrr": 1.0, "precision_at_k": 0.2, "stale_hit_rate": 0.0},
        "recovery_chaos_pass_rate": {"applicable": False, "reason": f"{P}: no chaos scenario"},
        "human_gate_correctness": {"applicable": False, "reason": f"{P}: no gate"},
        "task_readiness_correctness": {"numerator": 1, "denominator": 1, "value": 1.0},
    },
    "per_fault_outcomes": [
        {"fault_id": "SAMPLE-F1", "detected": True, "detected_at_tier": "G2", "detection_signal": "SAMPLE_SIGNAL", "observed_severity": "HIGH", "severity_correct": True, "impacted_expected": 2, "impacted_found": 2, "governed_action_correct": True, "forbidden_outcomes_observed": []},
        {"fault_id": "SAMPLE-F2", "detected": False, "detected_at_tier": None, "detection_signal": None, "observed_severity": None, "severity_correct": False, "impacted_expected": 1, "impacted_found": 0, "governed_action_correct": False, "forbidden_outcomes_observed": []},
    ],
}
rp = write(os.path.join(HERE, "samples", "format-sample.score-report.json"), REPORT)
rc, v = gov("oracle", "validate", rp)
check("A2 the FORMAT_SAMPLE score report conforms", rc == 0, json.dumps(v.get("result", v.get("error")))[:200])
rc, v = gov("oracle", "validate", rp, "--oracle", op)
check("A3 the score report is bound to the oracle file it names", rc == 0 and v["result"]["binding_verified"]["oracle_sha256"] == digest)


def removed(doc, field):
    d = copy.deepcopy(doc)
    parts = [p for p in field.replace("*", "0").split("/") if p]
    cur = d
    for p in parts[:-1]:
        cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    del cur[parts[-1]]
    return d


n = 0
for e in F["crosswalk"]:
    base = ORACLE if e["kind"] == "qualification-oracle" else REPORT
    for field in e["fields"]:
        p = write(os.path.join(SCR, f"missing-{n}.json"), removed(base, field))
        n += 1
        rc, v = gov("oracle", "validate", p)
        err = v.get("error") or {}
        ptr = field.replace("*", "0")
        viol = [x for x in (err.get("details") or {}).get("violations", []) if x.get("at") == ptr]
        tagged = [x for x in viol if x.get("element") == e["element"]]
        check(f"B {e['element']} (Contract v3:{e['source_line']} “{e['text'][:50]}”) — {e['kind']} without {field}",
              rc != 0 and err.get("code") == "ORACLE_RECORD_INVALID" and bool(tagged),
              f"exit={rc} {err.get('code')} violation={viol[0]['problem'] if viol else None}")


def case(name, doc, code, at):
    p = write(os.path.join(SCR, f"case-{len(results)}.json"), doc)
    rc, v = gov("oracle", "validate", p)
    err = v.get("error") or {}
    hit = any(x.get("at") == at for x in (err.get("details") or {}).get("violations", []))
    check(name, rc != 0 and err.get("code") == code and hit, f"exit={rc} {err.get('code')}")


def mut(doc, fn):
    d = copy.deepcopy(doc)
    fn(d)
    return d


case("C1 duplicate fault_id", mut(ORACLE, lambda d: d["fault_manifest"]["faults"][1].__setitem__("fault_id", "SAMPLE-F1")), "ORACLE_RECORD_INVALID", "/fault_manifest/faults/1/fault_id")
case("C2 fault class names a capability the owner source does not have", mut(ORACLE, lambda d: d["fault_manifest"]["faults"][1]["class"].__setitem__("capabilities", ["Z9"])), "ORACLE_RECORD_INVALID", "/fault_manifest/faults/1/class/capabilities/0")
case("C3 expected detection names a tier O5 does not define", mut(ORACLE, lambda d: d["fault_manifest"]["faults"][1]["expected_detection"].__setitem__("tiers", ["G7"])), "ORACLE_RECORD_INVALID", "/fault_manifest/faults/1/expected_detection/tiers/0")
case("C4 a Gate W fault without required input/version and propagation", mut(ORACLE, lambda d: d["fault_manifest"]["faults"][0].pop("artifact_flow")), "ORACLE_RECORD_INVALID", "/fault_manifest/faults/0/artifact_flow")
case("C5 KEEP whose target is another path", mut(ORACLE, lambda d: d["path_map_oracle"]["entries"][0].__setitem__("expected_target_paths", ["sample/elsewhere"])), "ORACLE_RECORD_INVALID", "/path_map_oracle/entries/0/expected_target_paths")
case("C6 material both indexed and never indexed", mut(ORACLE, lambda d: d["memory_oracle"]["must_never_be_indexed"][0].__setitem__("ref", "sample/a")), "ORACLE_RECORD_INVALID", "/memory_oracle/must_be_indexed/0/ref")
case("C7 a retrieval result that returns never-indexed material", mut(ORACLE, lambda d: d["memory_oracle"]["expected_retrieval_results"][0].__setitem__("must_include", ["sample/secret"])), "ORACLE_RECORD_INVALID", "/memory_oracle/expected_retrieval_results/0/must_include")
case("C8 path map NEVER_INDEX contradicts the memory oracle", mut(ORACLE, lambda d: d["path_map_oracle"]["entries"][0].__setitem__("indexing_expectation", "NEVER_INDEX")), "ORACLE_RECORD_INVALID", "/path_map_oracle/entries/0/indexing_expectation")
case("C9 oracle storage inside the public qualification suite", mut(ORACLE, lambda d: d["separation"].__setitem__("oracle_storage", "sample/public-suite/oracle.json")), "ORACLE_RECORD_INVALID", "/separation/oracle_storage")
case("C10 a brownfield oracle without the V2 path-map oracle", mut(ORACLE, lambda d: d.pop("path_map_oracle")), "ORACLE_RECORD_INVALID", "/path_map_oracle")
case("C11 an oracle not in verifier custody", mut(ORACLE, lambda d: d["custody"].__setitem__("owner_role", "BUILDER")), "ORACLE_RECORD_INVALID", "/custody/owner_role")
case("C12 an oracle that is not hidden", mut(ORACLE, lambda d: d.__setitem__("visibility", "PUBLIC")), "ORACLE_RECORD_INVALID", "/visibility")
case("C13 a document written against another format version", mut(ORACLE, lambda d: d.__setitem__("format_sha256", "f" * 64)), "ORACLE_RECORD_INVALID", "/format_sha256")
case("C14 a ratio whose value is not numerator/denominator", mut(REPORT, lambda d: d["metrics"]["injected_defect_detection_recall"].__setitem__("value", 0.9)), "ORACLE_RECORD_INVALID", "/metrics/injected_defect_detection_recall/value")
case("C15 recall that disagrees with the per-fault outcomes", mut(REPORT, lambda d: d["metrics"].__setitem__("injected_defect_detection_recall", {"numerator": 2, "denominator": 2, "value": 1.0})), "ORACLE_RECORD_INVALID", "/metrics/injected_defect_detection_recall")
case("C16 an undetected fault credited with a correct severity", mut(REPORT, lambda d: d["per_fault_outcomes"][1].__setitem__("severity_correct", True)), "ORACLE_RECORD_INVALID", "/per_fault_outcomes/1/severity_correct")

# D. binding
o2 = mut(ORACLE, lambda d: d["fault_manifest"]["faults"][1].__setitem__("expected_severity", "LOW"))
p2 = write(os.path.join(SCR, "changed-oracle.json"), o2)
rc, v = gov("oracle", "validate", rp, "--oracle", p2)
check("D1 an oracle changed after sealing no longer matches the report", rc != 0 and v["error"]["code"] == "ORACLE_SCORE_BINDING_MISMATCH", v.get("error", {}).get("message", "")[:160])
r2 = mut(REPORT, lambda d: d["per_fault_outcomes"].pop())
# keep the report internally consistent, so only the binding to the oracle can fail
r2["metrics"]["injected_defect_detection_recall"] = {"numerator": 1, "denominator": 1, "value": 1.0}
r2["metrics"]["impact_map_accuracy"] = {"numerator": 2, "denominator": 2, "value": 1.0}
rc, v = gov("oracle", "validate", write(os.path.join(SCR, "unscored-standalone.json"), r2))
check("D2a the report without F2 is internally consistent on its own", rc == 0, json.dumps(v.get("error", {}))[:160])
rp2 = write(os.path.join(SCR, "unscored.json"), r2)
rc, v = gov("oracle", "validate", rp2, "--oracle", op)
check("D2 a report that leaves an injected fault unscored", rc != 0 and v["error"]["code"] == "ORACLE_SCORE_BINDING_MISMATCH", v.get("error", {}).get("message", "")[:160])

# E. separation
base = tempfile.mkdtemp(prefix="sep-", dir=SCR)
pub, repo, cust = (os.path.join(base, x) for x in ("public", "repo", "custody"))
for d in (pub, repo, cust):
    os.makedirs(d)
held = write(os.path.join(cust, "oracle.json"), ORACLE)
rc, v = gov("oracle", "validate", held, "--public-suite", pub, "--repository", repo)
check("E1 an oracle held in verifier custody, apart from suite and repository, is separate", rc == 0 and v["result"]["separation"]["findings"] == 0)
inside = write(os.path.join(repo, "oracle.json"), ORACLE)
rc, v = gov("oracle", "validate", inside, "--public-suite", pub, "--repository", repo)
check("E2 an oracle stored inside the qualification repository", rc != 0 and v["error"]["code"] == "ORACLE_SEPARATION_VIOLATED")
os.remove(inside)
shutil.copy(held, os.path.join(pub, "leaked.json"))
rc, v = gov("oracle", "validate", held, "--public-suite", pub, "--repository", repo)
check("E3 a copy of the oracle inside the public qualification suite", rc != 0 and v["error"]["code"] == "ORACLE_SEPARATION_VIOLATED")
os.remove(os.path.join(pub, "leaked.json"))
with open(os.path.join(repo, "notes.md"), "w") as f:
    f.write(ORACLE["fault_manifest"]["faults"][0]["hidden_authoritative_truth"]["statement"] + "\n")
rc, v = gov("oracle", "validate", held, "--public-suite", pub, "--repository", repo)
check("E4 a hidden authoritative truth quoted verbatim inside the repository", rc != 0 and v["error"]["code"] == "ORACLE_SEPARATION_VIOLATED")

# F. the audit's own records (epsilon-r V-oracle-format-and-contract-views.sh section B)
for name, doc in [("FM-0001", {"id": "FM-0001", "type": "fault-manifest", "title": "empty fault manifest", "status": "ACTIVE"}),
                  ("FM-0002", {"id": "FM-0002", "type": "fault-manifest", "title": "nonsense", "status": "ACTIVE", "class": 42, "expected_severity": "purple"})]:
    p = write(os.path.join(SCR, f"{name}.json"), doc)
    rc, v = gov("oracle", "validate", p)
    check(f"F {name} (a fault-manifest record lacking every V1 field) is rejected", rc != 0 and v["error"]["code"] == "ORACLE_RECORD_INVALID", v["error"]["message"][:200])
    for x in v["error"]["details"]["violations"]:
        print(f"      {x}")

print(f"SUMMARY checks={len(results)} pass={sum(results)} fail={len(results) - sum(results)}")
sys.exit(0 if all(results) else 1)
