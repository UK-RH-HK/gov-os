#!/usr/bin/env python3
"""P2-AR-0045: author the labelled FORMAT_SAMPLE corpus used to attack the Qualification Oracle format.

Nothing here is an oracle. Every document carries purpose: FORMAT_SAMPLE, describes no qualification
repository (all paths are placeholders under sample/), and contains no hidden fault. The base documents
are written from Contract v3 Gate V and the format definition; the invalid variants are mechanical
mutations of them, one attack per file.
"""
import copy, hashlib, json, os, subprocess, sys

OUT = "release/capability-baseline/verify-1/oracle-format/samples"
FMT_SHA = subprocess.run(
    ["target/release/gov", "--json", "oracle", "format"], capture_output=True, text=True
)
FMT = json.loads(FMT_SHA.stdout)
FSHA = FMT["result"]["format_sha256"]
REPO_COMMIT = "1111111111111111111111111111111111111111"
CAND_COMMIT = "2222222222222222222222222222222222222222"
CUSTODY = {
    "owner_role": "FRESH_INDEPENDENT_VERIFIER",
    "owner_run_id": "P2-AR-0045",
    "authored_independently_of_implementation": True,
    "created_at": "2026-09-20T00:00:00Z",
}


def oracle():
    return {
        "format": "governance-os.qualification-oracle",
        "format_version": 1,
        "format_sha256": FSHA,
        "kind": "qualification-oracle",
        "purpose": "FORMAT_SAMPLE",
        "oracle_id": "P2AR0045-SAMPLE-ORACLE-A",
        "custody": dict(CUSTODY),
        "visibility": "HIDDEN",
        "repository": {
            "id": "sample-repo-b",
            "adoption_mode": "BROWNFIELD",
            "commit": REPO_COMMIT,
            "label": "format sample, brownfield shape",
        },
        "separation": {
            "public_qualification_suite": "sample/public-suite",
            "qualification_repository": "sample/repo-b",
            "oracle_storage": "sample/verifier-custody",
        },
        "fault_manifest": {
            "faults": [
                {
                    "fault_id": "SMP-F-001",
                    "class": {
                        "id": "SAMPLE_STALE_MANDATORY_INPUT",
                        "capabilities": ["W6", "W9"],
                        "challenge_ids": ["AQC-W12"],
                    },
                    "hidden_authoritative_truth": {
                        "statement": "sample/spec/current.md at version 3 is the only authoritative input for sample/task/T-1",
                        "authoritative_refs": ["sample/spec/current.md"],
                    },
                    "injected_repository_state": {
                        "description": "the superseded spec is left in the active tree and the task manifest still names it",
                        "changes": [
                            {"path": "sample/spec/old.md", "change": "MODIFIED"},
                            {"path": "sample/spec/current.md", "change": "MOVED", "from_path": "sample/draft/current.md"},
                        ],
                    },
                    "expected_detection": {
                        "tiers": ["G2", "G5"],
                        "signals": ["MANDATORY_INPUT_STALE", "close refused with a typed result"],
                        "must_detect_before": "task close",
                    },
                    "expected_severity": "HIGH",
                    "expected_impacted": [
                        {"ref": "sample/task/T-1", "ref_kind": "TASK", "relation": "DIRECT"},
                        {"ref": "sample/src/handler.rs", "ref_kind": "PATH", "relation": "TRANSITIVE"},
                        {"ref": "sample/context/CP-1", "ref_kind": "CONTEXT_PACKET", "relation": "TRANSITIVE"},
                    ],
                    "expected_governed_action": [
                        {"action": "BLOCK_CLOSE", "target": "sample/task/T-1", "description": "close refused until the current input version is consumed"},
                        {"action": "MARK_EVIDENCE_STALE", "target": "sample/context/CP-1", "description": "the context packet built on the superseded spec is stale"},
                    ],
                    "forbidden_outcomes": [
                        {"outcome": "the superseded spec silently satisfies the mandatory input", "observable": "the task closes with a consumption receipt citing sample/spec/old.md"}
                    ],
                    "artifact_flow": {
                        "required_inputs": [{"artefact_id": "sample/spec/current.md", "version": "3", "reason": "the only authoritative specification"}],
                        "expected_propagation": [
                            {"ref": "sample/task/T-1", "expected_state": "BLOCKED"},
                            {"ref": "sample/context/CP-1", "expected_state": "INVALIDATED"},
                        ],
                    },
                },
                {
                    "fault_id": "SMP-F-002",
                    "class": {"id": "SAMPLE_SENSITIVE_MATERIAL_INDEXED", "capabilities": ["A3", "C3"], "challenge_ids": ["AQC-A3"]},
                    "hidden_authoritative_truth": {
                        "statement": "sample/ops/credentials.env is sensitive and must never reach any index or context packet",
                        "authoritative_refs": ["sample/policy/DATA_SENSITIVITY.yaml"],
                    },
                    "injected_repository_state": {
                        "description": "a credential file is added inside an indexed directory",
                        "changes": [{"path": "sample/ops/credentials.env", "change": "ADDED"}],
                    },
                    "expected_detection": {"tiers": ["G1"], "signals": ["SENSITIVE_MATERIAL_EXCLUDED"], "must_detect_before": "the next index build completes"},
                    "expected_severity": "CRITICAL",
                    "expected_impacted": [{"ref": "sample/ops/credentials.env", "ref_kind": "PATH", "relation": "DIRECT"}],
                    "expected_governed_action": [{"action": "QUARANTINE", "target": "sample/ops/credentials.env", "description": "excluded from every retrieval route"}],
                    "forbidden_outcomes": [{"outcome": "the credential is retrievable", "observable": "any retrieval result cites sample/ops/credentials.env"}],
                },
            ]
        },
        "path_map_oracle": {
            "entries": [
                {
                    "current_artefact": {"path": "sample/spec/current.md"},
                    "correct_classification": "authoritative specification",
                    "authority": "AUTHORITATIVE",
                    "expected_target_paths": ["sample/spec/current.md"],
                    "action": "KEEP",
                    "expected_references": ["sample/src/handler.rs"],
                    "expected_consumers": ["sample/task/T-1"],
                    "sensitivity": "internal",
                    "indexing_expectation": "INDEX_CURRENT",
                },
                {
                    "current_artefact": {"path": "sample/spec/old.md"},
                    "correct_classification": "superseded specification",
                    "authority": "SUPERSEDED_BY sample/spec/current.md",
                    "expected_target_paths": ["sample/archive/old.md"],
                    "action": "MOVE",
                    "expected_references": [],
                    "expected_consumers": [],
                    "sensitivity": "internal",
                    "indexing_expectation": "INDEX_HISTORICAL",
                },
                {
                    "current_artefact": {"path": "sample/ops/credentials.env"},
                    "correct_classification": "operational secret",
                    "authority": "NON_AUTHORITATIVE",
                    "expected_target_paths": [],
                    "action": "DELETE_FROM_ACTIVE_TREE",
                    "expected_references": [],
                    "expected_consumers": [],
                    "sensitivity": "secret",
                    "indexing_expectation": "NEVER_INDEX",
                },
            ]
        },
        "memory_oracle": {
            "must_be_indexed": [
                {"ref": "sample/spec/current.md", "routes": ["STRUCTURED", "SEMANTIC", "LEXICAL"]},
                {"ref": "sample/src/handler.rs", "routes": ["CODE", "GRAPH"]},
            ],
            "must_never_be_indexed": [{"ref": "sample/ops/credentials.env", "reason": "operational secret"}],
            "expected_authority_namespaces": [{"ref": "sample/spec/current.md", "namespace": "authoritative/specification"}],
            "expected_status": [
                {"ref": "sample/spec/current.md", "status": "CURRENT"},
                {"ref": "sample/spec/old.md", "status": "SUPERSEDED", "superseded_by": "sample/spec/current.md"},
            ],
            "expected_graph_relationships": [{"from": "sample/src/handler.rs", "relation": "IMPLEMENTS", "to": "sample/spec/current.md"}],
            "expected_code_symbols": [{"path": "sample/src/handler.rs", "symbol": "handle_request", "symbol_kind": "function", "language": "rust"}],
            "expected_retrieval_results": [
                {"query_id": "SMP-Q1", "query": "current specification for the sample handler", "route": "FUSED", "top_k": 5,
                 "must_include": ["sample/spec/current.md"], "must_not_include": ["sample/spec/old.md", "sample/ops/credentials.env"]}
            ],
        },
    }


def report(oracle_sha):
    return {
        "format": "governance-os.qualification-oracle",
        "format_version": 1,
        "format_sha256": FSHA,
        "kind": "qualification-score-report",
        "purpose": "FORMAT_SAMPLE",
        "report_id": "P2AR0045-SAMPLE-REPORT-A",
        "custody": dict(CUSTODY),
        "binding": {
            "oracle_id": "P2AR0045-SAMPLE-ORACLE-A",
            "oracle_sha256": oracle_sha,
            "repository": {"id": "sample-repo-b", "commit": REPO_COMMIT},
            "candidate": {"commit": CAND_COMMIT, "product_code_digest": "3" * 64},
            "run_id": "P2-AR-0045-SAMPLE-RUN",
            "scored_at": "2026-09-20T01:00:00Z",
        },
        "metrics": {
            "injected_defect_detection_recall": {"numerator": 1, "denominator": 2, "value": 0.5},
            "false_positives": {"count": 2, "findings": ["SMP-FP-1", "SMP-FP-2"]},
            "severity_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
            "impact_map_accuracy": {"numerator": 2, "denominator": 4, "value": 0.5},
            "path_map_accuracy": {"numerator": 2, "denominator": 3, "value": 2 / 3},
            "missed_authoritative_artefacts": {"count": 1, "refs": ["sample/spec/current.md"]},
            "wrong_indexing_count": {"count": 1, "refs": ["sample/ops/credentials.env"]},
            "stale_index_count": {"count": 0, "refs": []},
            "retrieval_metrics": {"k": 5, "queries": 1, "recall_at_k": 1.0, "mrr": 1.0, "precision_at_k": 0.2, "stale_hit_rate": 0.0, "superseded_hit_rate": 0.0, "latency_ms_p50": 12.0, "latency_ms_p95": 30.0},
            "recovery_chaos_pass_rate": {"numerator": 3, "denominator": 4, "value": 0.75},
            "human_gate_correctness": {"numerator": 2, "denominator": 2, "value": 1.0},
            "task_readiness_correctness": {"numerator": 5, "denominator": 5, "value": 1.0},
        },
        "per_fault_outcomes": [
            {"fault_id": "SMP-F-001", "detected": True, "detected_at_tier": "G2", "detection_signal": "MANDATORY_INPUT_STALE",
             "observed_severity": "HIGH", "severity_correct": True, "impacted_expected": 3, "impacted_found": 2,
             "governed_action_correct": True, "forbidden_outcomes_observed": []},
            {"fault_id": "SMP-F-002", "detected": False, "detected_at_tier": None, "detection_signal": None,
             "observed_severity": None, "severity_correct": False, "impacted_expected": 1, "impacted_found": 0,
             "governed_action_correct": False, "forbidden_outcomes_observed": ["the credential is retrievable"]},
        ],
        "notes": "labelled format sample authored by P2-AR-0045 to exercise V4; no qualification run took place",
    }


def drop(d, ptr):
    node = d
    segs = [s for s in ptr.split("/") if s]
    for s in segs[:-1]:
        node = node[int(s)] if isinstance(node, list) else node[s]
    last = segs[-1]
    if isinstance(node, list):
        node.pop(int(last))
    else:
        node.pop(last)
    return d


def setv(d, ptr, val):
    node = d
    segs = [s for s in ptr.split("/") if s]
    for s in segs[:-1]:
        node = node[int(s)] if isinstance(node, list) else node[s]
    last = segs[-1]
    if isinstance(node, list):
        node[int(last)] = val
    else:
        node[last] = val
    return d


def write(name, doc):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=False)
        f.write("\n")
    return p


os.makedirs(OUT, exist_ok=True)
base = oracle()
write("valid/oracle.json", base)

# --- V1: one "missing required field" sample per checklist bullet -----------------------------
V1 = ["fault_id", "class", "hidden_authoritative_truth", "injected_repository_state",
      "expected_detection", "expected_severity", "expected_impacted",
      "expected_governed_action", "forbidden_outcomes"]
for i, f in enumerate(V1, 1):
    write(f"invalid/v1-{i:02d}-missing-{f.replace('_','-')}.json",
          drop(oracle(), f"/fault_manifest/faults/0/{f}"))

V2 = ["current_artefact", "correct_classification", "authority", "expected_target_paths",
      "action", "expected_references", "expected_consumers", "sensitivity", "indexing_expectation"]
for i, f in enumerate(V2, 1):
    write(f"invalid/v2-{i:02d}-missing-{f.replace('_','-')}.json",
          drop(oracle(), f"/path_map_oracle/entries/0/{f}"))

V3 = ["must_be_indexed", "must_never_be_indexed", "expected_authority_namespaces", "expected_status",
      "expected_graph_relationships", "expected_code_symbols", "expected_retrieval_results"]
for i, f in enumerate(V3, 1):
    write(f"invalid/v3-{i:02d}-missing-{f.replace('_','-')}.json",
          drop(oracle(), f"/memory_oracle/{f}"))

# --- wrong types ------------------------------------------------------------------------------
write("invalid/type-01-severity-free-text.json", setv(oracle(), "/fault_manifest/faults/0/expected_severity", "quite bad"))
write("invalid/type-02-expected-impacted-string.json", setv(oracle(), "/fault_manifest/faults/0/expected_impacted", "the task and the handler"))
write("invalid/type-03-action-free-text.json", setv(oracle(), "/path_map_oracle/entries/0/action", "leave it where it is"))
write("invalid/type-04-tier-not-a-tier.json", setv(oracle(), "/fault_manifest/faults/0/expected_detection/tiers", ["whenever"]))
write("invalid/type-05-indexing-expectation-free-text.json", setv(oracle(), "/path_map_oracle/entries/0/indexing_expectation", "probably index it"))
write("invalid/type-06-visibility-public.json", setv(oracle(), "/visibility", "PUBLIC"))
write("invalid/type-07-custody-not-independent.json", setv(oracle(), "/custody/authored_independently_of_implementation", False))
write("invalid/type-08-custody-builder-role.json", setv(oracle(), "/custody/owner_role", "BUILDER"))
write("invalid/type-09-unknown-capability.json", setv(oracle(), "/fault_manifest/faults/0/class/capabilities", ["ZZ9"]))
write("invalid/type-10-unknown-challenge.json", setv(oracle(), "/fault_manifest/faults/0/class/challenge_ids", ["AQC-NOPE"]))
write("invalid/type-11-unknown-tier-g9.json", setv(oracle(), "/fault_manifest/faults/0/expected_detection/tiers", ["G9"]))
write("invalid/type-12-extra-field.json", setv(oracle(), "/fault_manifest/faults/0/severity_guess", "HIGH"))
d = oracle(); d["format_sha256"] = "0" * 64
write("invalid/type-13-wrong-format-digest.json", d)
d = oracle(); d["kind"] = "fault-manifest"
write("invalid/type-14-unknown-kind.json", d)

# --- semantic / consistency attacks on the oracle ---------------------------------------------
d = oracle(); d["fault_manifest"]["faults"][1]["fault_id"] = "SMP-F-001"
write("invalid/sem-01-duplicate-fault-id.json", d)
write("invalid/sem-02-keep-with-other-target.json", setv(oracle(), "/path_map_oracle/entries/0/expected_target_paths", ["sample/elsewhere/current.md"]))
d = oracle(); setv(d, "/path_map_oracle/entries/1/action", "SPLIT")
write("invalid/sem-03-split-with-one-target.json", d)
d = oracle(); setv(d, "/path_map_oracle/entries/2/expected_target_paths", ["sample/archive/credentials.env"])
write("invalid/sem-04-delete-with-target.json", d)
d = oracle(); d["memory_oracle"]["must_be_indexed"].append({"ref": "sample/ops/credentials.env", "routes": ["SEMANTIC"]})
write("invalid/sem-05-indexed-and-never-indexed.json", d)
d = oracle(); setv(d, "/memory_oracle/expected_retrieval_results/0/must_include", ["sample/ops/credentials.env"])
write("invalid/sem-06-retrieval-returns-never-indexed.json", d)
d = oracle(); setv(d, "/path_map_oracle/entries/0/indexing_expectation", "NEVER_INDEX")
write("invalid/sem-07-v2-v3-indexing-contradiction.json", d)
d = oracle(); setv(d, "/memory_oracle/expected_status/1/superseded_by", "sample/spec/old.md")
write("invalid/sem-08-superseded-by-itself.json", d)
d = oracle(); setv(d, "/fault_manifest/faults/0/class/capabilities", ["W6"]); drop(d, "/fault_manifest/faults/0/artifact_flow")
write("invalid/sem-09-gate-w-fault-without-artifact-flow.json", d)
d = oracle(); setv(d, "/repository/adoption_mode", "BROWNFIELD"); drop(d, "/path_map_oracle")
write("invalid/sem-10-brownfield-without-path-map.json", d)
d = oracle(); setv(d, "/separation/oracle_storage", "sample/public-suite/oracle")
write("invalid/sep-01-storage-inside-public-suite.json", d)
d = oracle(); setv(d, "/separation/oracle_storage", "sample/repo-b/.hidden/oracle")
write("invalid/sep-02-storage-inside-qualification-repo.json", d)
d = oracle(); d["fault_manifest"]["faults"] = []
write("invalid/sem-11-empty-fault-manifest.json", d)

# --- a legitimately GREENFIELD oracle (no path map) is valid ----------------------------------
d = oracle()
d["oracle_id"] = "P2AR0045-SAMPLE-ORACLE-G"
d["repository"] = {"id": "sample-repo-a", "adoption_mode": "GREENFIELD", "commit": REPO_COMMIT, "label": "format sample, greenfield shape"}
d.pop("path_map_oracle")
d["memory_oracle"]["must_be_indexed"] = [x for x in d["memory_oracle"]["must_be_indexed"]]
write("valid/oracle-greenfield.json", d)
print("wrote samples to", OUT)
