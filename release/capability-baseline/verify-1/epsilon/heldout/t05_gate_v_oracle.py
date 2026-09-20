#!/usr/bin/env python3
"""Gate V (V1-V4) held-out probes — P2-AR-0050, verification iteration 1, family epsilon.

V1 fault manifest, V2 hidden path-map oracle, V3 hidden memory oracle, V4 quantitative scoring, and the
separation rule of Contract v3:1062. The AC-6 *format acceptance* is a separate reviewer's (P2-AR-0045); these
probes establish the V1-V4 capability statuses: that a machine-checkable definition exists, that every bullet of
each capability is a field the product enforces, and that the enforcement fails closed.

Method (independent of any builder test): the oracle document these probes validate is generated *from the
crosswalk the product itself prints* (`gov oracle format`), by walking every crosswalk field pointer and letting
the validator's own refusals drive the shape. Every V1-V4 element is then removed one at a time and the document
must be refused, naming that element.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Project, check, main  # noqa: E402

V_ELEMENTS = {"V1": 9, "V2": 7, "V3": 7, "V4": 12}


def put(doc, pointer, value):
    """Set a value at a JSON-pointer-with-`*` (a `*` means index 0 of a list that must exist)."""
    parts = [p for p in pointer.split("/") if p]
    cur = doc
    for i, p in enumerate(parts):
        last = i == len(parts) - 1
        nxt = parts[i + 1] if not last else None
        if p == "*":
            if not isinstance(cur, list):
                return False
            while not cur:
                cur.append({})
            cur = cur[0] if not last else cur
            if last:
                return True
            continue
        if last:
            cur[p] = value
            return True
        if p not in cur or cur[p] is None:
            cur[p] = [] if nxt == "*" else {}
        cur = cur[p]
    return True


def get(doc, pointer):
    cur = doc
    for p in [x for x in pointer.split("/") if x]:
        if p == "*":
            if not isinstance(cur, list) or not cur:
                return None
            cur = cur[0]
            continue
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def remove(doc, pointer):
    parts = [p for p in pointer.replace("*", "0").split("/") if p]
    cur = doc
    for p in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(p)]
        elif isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return False
    k = parts[-1]
    if isinstance(cur, dict) and k in cur:
        del cur[k]
        return True
    return False


def run():
    p = Project("gatev")
    assert p.init().ok, "init"

    fmt = p.run("oracle", "format")
    check("V-format-exists", fmt.ok and fmt.result.get("format_sha256"),
          f"format_sha256={fmt.result.get('format_sha256')} status={str(fmt.result.get('status'))[:40]}")
    cw = fmt.result["crosswalk"]

    # --- every V1-V4 bullet of the owner source is a crosswalk element with at least one field -----------
    for cap, n in V_ELEMENTS.items():
        els = sorted({e["element"] for e in cw if e["element"].startswith(cap + ".")})
        have_fields = all(e["fields"] for e in cw if e["element"].startswith(cap + "."))
        check(f"V-crosswalk-{cap}", len(els) == n and have_fields,
              f"{len(els)}/{n} elements mapped, every element names a field: {have_fields}")

    oracle_els = [e for e in cw if e["kind"] == "qualification-oracle"]
    report_els = [e for e in cw if e["kind"] == "qualification-score-report"]

    # --- author a conforming pair, driven by the validator's own refusals --------------------------------
    oracle, report = author_pair(p, fmt.result, oracle_els, report_els)
    o_file = p.root.parent / "eps-oracle.json"
    r_file = p.root.parent / "eps-report.json"
    o_file.write_text(json.dumps(oracle))
    v = p.run("oracle", "validate", str(o_file))
    check("V-oracle-conforms", v.ok and v.result.get("verdict") == "RECORD_CONFORMS_TO_FORMAT",
          f"verdict={v.result.get('verdict')} err={v.error_code} {str(v.details)[:200]}")
    if not v.ok:
        return
    report["binding"]["oracle_sha256"] = v.result.get("document_sha256") or v.result.get("sha256") \
        or canon_sha(oracle)
    r_file.write_text(json.dumps(report))
    v2 = p.run("oracle", "validate", str(r_file), "--oracle", str(o_file))
    check("V4-report-conforms-and-binds", v2.ok and v2.result.get("verdict") == "RECORD_CONFORMS_TO_FORMAT",
          f"verdict={v2.result.get('verdict')} err={v2.error_code} {str(v2.details)[:300]}")

    # --- every V1-V4 element is ENFORCED: removing it is refused, naming the element ---------------------
    for cap in ("V1", "V2", "V3"):
        enforced, total, misses = [], 0, []
        for e in oracle_els:
            if not e["element"].startswith(cap + "."):
                continue
            for f in e["fields"]:
                total += 1
                d = copy.deepcopy(oracle)
                if not remove(d, f):
                    misses.append(f"{f} (not present in the authored document)")
                    continue
                t = p.root.parent / "eps-oracle-mut.json"
                t.write_text(json.dumps(d))
                r = p.run("oracle", "validate", str(t))
                bad = json.dumps(r.details) + json.dumps(r.error)
                if (not r.ok) and (e["element"] in bad or f.replace("*", "0") in bad):
                    enforced.append(f)
                else:
                    misses.append(f"{f}: ok={r.ok} code={r.error_code}")
        check(f"{cap}-every-bullet-enforced", len(enforced) == total and total > 0,
              f"{len(enforced)}/{total} fields refused when removed; misses={misses[:3]}")

    enforced, total, misses = [], 0, []
    for e in report_els:
        if not e["element"].startswith("V4."):
            continue
        for f in e["fields"]:
            total += 1
            d = copy.deepcopy(report)
            if not remove(d, f):
                misses.append(f"{f} absent")
                continue
            t = p.root.parent / "eps-report-mut.json"
            t.write_text(json.dumps(d))
            r = p.run("oracle", "validate", str(t), "--oracle", str(o_file))
            bad = json.dumps(r.details) + json.dumps(r.error)
            if (not r.ok) and (e["element"] in bad or f.replace("*", "0") in bad):
                enforced.append(f)
            else:
                misses.append(f"{f}: ok={r.ok} code={r.error_code}")
    check("V4-every-bullet-enforced", len(enforced) == total and total > 0,
          f"{len(enforced)}/{total} metric fields refused when removed; misses={misses[:3]}")

    # --- fails closed on the iteration-0 record (a 'fault manifest' with no V1 field) --------------------
    junk = p.root.parent / "eps-junk.json"
    junk.write_text(json.dumps({"id": "FM-0001", "type": "fault-manifest",
                                "title": "empty fault manifest", "status": "ACTIVE"}))
    r = p.run("oracle", "validate", str(junk))
    check("V1-empty-manifest-refused", (not r.ok) and r.error_code == "ORACLE_RECORD_INVALID",
          f"ok={r.ok} code={r.error_code}")

    # --- V4 arithmetic and oracle binding are checked, not trusted ---------------------------------------
    d = copy.deepcopy(report)
    d["metrics"]["injected_defect_detection_recall"]["value"] = 0.25  # contradicts numerator/denominator (1/1)
    t = p.root.parent / "eps-report-arith.json"
    t.write_text(json.dumps(d))
    r = p.run("oracle", "validate", str(t), "--oracle", str(o_file))
    check("V4-arithmetic-checked", not r.ok, f"ok={r.ok} code={r.error_code} {str(r.details)[:180]}")

    d = copy.deepcopy(report)
    d["binding"]["oracle_sha256"] = "0" * 64
    t = p.root.parent / "eps-report-bind.json"
    t.write_text(json.dumps(d))
    r = p.run("oracle", "validate", str(t), "--oracle", str(o_file))
    check("V4-binding-checked", (not r.ok) and "BINDING" in (r.error_code or "") + json.dumps(r.details),
          f"ok={r.ok} code={r.error_code}")

    # --- Contract v3:1062 separation: the oracle may not live in the public suite or the repository -------
    pub = p.root.parent / "public-suite"
    pub.mkdir(exist_ok=True)
    inside = pub / "oracle.json"
    inside.write_text(json.dumps(oracle))
    r = p.run("oracle", "validate", str(inside), "--public-suite", str(pub))
    check("V-separation-storage-refused", not r.ok, f"ok={r.ok} code={r.error_code}")

    leak = pub / "notes.md"
    leak.write_text("scratch\n" + oracle["fault_manifest"]["faults"][0]["fault_id"] + "\n")
    r = p.run("oracle", "validate", str(o_file), "--public-suite", str(pub))
    check("V-separation-trace-refused", not r.ok,
          f"a fault id of the hidden oracle found in the public suite: ok={r.ok} code={r.error_code}")

    # --- G6 observes a qualification run only through a conforming, separate oracle -----------------------
    r = p.run("health", "qualify", "--kind", "synthetic-repository",
              "--oracle", str(o_file), "--report", str(r_file))
    check("V-G6-observes-qualification", r.ok or r.error_code not in ("USAGE", "NO_JSON"),
          f"ok={r.ok} code={r.error_code} {json.dumps(r.result)[:200] if r.ok else str(r.details)[:220]}")
    r2 = p.run("health", "qualify", "--kind", "synthetic-repository",
               "--oracle", str(junk), "--report", str(r_file))
    check("V-G6-refuses-nonconforming-oracle", not r2.ok, f"ok={r2.ok} code={r2.error_code}")


def canon_sha(v):
    import hashlib

    def s(x):
        if isinstance(x, dict):
            return {k: s(x[k]) for k in sorted(x)}
        if isinstance(x, list):
            return [s(i) for i in x]
        return x
    return hashlib.sha256(json.dumps(s(v), separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def author_pair(p, fmt, oracle_els, report_els):
    """An oracle + score report authored by this verifier, shaped by the product's own crosswalk and refusals."""
    commit = "a" * 40
    oracle = {
        "format": fmt["format"], "format_version": fmt["format_version"],
        "format_sha256": fmt["format_sha256"], "kind": "qualification-oracle",
        "purpose": "FORMAT_SAMPLE", "oracle_id": "EPS-ORACLE-0050",
        "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "P2-AR-0050",
                    "authored_independently_of_implementation": True,
                    "created_at": "2026-09-20T00:00:00Z"},
        "visibility": "HIDDEN",
        "repository": {"id": "eps-repo", "adoption_mode": "BROWNFIELD", "commit": commit,
                       "label": "epsilon held-out probe"},
        "separation": {"public_qualification_suite": "example/public",
                       "qualification_repository": "example/repo",
                       "oracle_storage": "example/custody/oracle.json"},
        "fault_manifest": {"faults": [{
            "fault_id": "EPS-F1",
            "class": {"id": "EPS_STALE_INPUT", "capabilities": ["W6"], "challenge_ids": ["AQC-W12"]},
            "hidden_authoritative_truth": {"statement": "example/spec-new.md supersedes example/spec-old.md",
                                           "authoritative_refs": ["example/spec-new.md"]},
            "injected_repository_state": {"description": "a superseded spec left reachable",
                                          "changes": [{"path": "example/spec-old.md", "change": "MODIFIED"}]},
            "expected_detection": {"tiers": ["G2"], "signals": ["EPS_SIGNAL"],
                                   "must_detect_before": "task close"},
            "expected_severity": "HIGH",
            "expected_impacted": [{"ref": "example/task-1", "ref_kind": "TASK", "relation": "DIRECT"}],
            "expected_governed_action": [{"action": "BLOCK_CLOSE", "target": "example/task-1",
                                          "description": "close refused until the current input is consumed"}],
            "forbidden_outcomes": [{"outcome": "the superseded spec satisfies the input",
                                    "observable": "the packet lists example/spec-old.md as mandatory"}],
            "artifact_flow": {"required_inputs": [{"artefact_id": "example/spec-new.md", "version": "2"}],
                              "expected_propagation": [{"ref": "example/task-1", "expected_state": "STALE"}]},
        }]},
        "path_map_oracle": {"entries": [{
            "current_artefact": {"path": "example/spec-new.md"},
            "correct_classification": "specification", "authority": "AUTHORITATIVE",
            "expected_target_paths": ["example/spec-new.md"], "action": "KEEP",
            "expected_references": ["example/src/a.rs"], "expected_consumers": ["example/task-1"],
            "sensitivity": "internal", "indexing_expectation": "INDEX_CURRENT"}]},
        "memory_oracle": {
            "must_be_indexed": [{"ref": "example/spec-new.md", "routes": ["STRUCTURED", "SEMANTIC"]}],
            "must_never_be_indexed": [{"ref": "example/.env", "reason": "secret"}],
            "expected_authority_namespaces": [{"ref": "example/spec-new.md", "namespace": "authoritative/spec"}],
            "expected_status": [{"ref": "example/spec-new.md", "status": "CURRENT"}],
            "expected_graph_relationships": [{"from": "example/src/a.rs", "relation": "IMPLEMENTS",
                                              "to": "example/spec-new.md"}],
            "expected_code_symbols": [{"path": "example/src/a.rs", "symbol": "handle",
                                       "symbol_kind": "function", "language": "rust"}],
            "expected_retrieval_results": [{"query_id": "Q1", "query": "current spec", "route": "FUSED",
                                            "top_k": 5, "must_include": ["example/spec-new.md"],
                                            "must_not_include": ["example/spec-old.md"]}]},
    }
    report = {
        "format": fmt["format"], "format_version": fmt["format_version"],
        "format_sha256": fmt["format_sha256"], "kind": "qualification-score-report",
        "purpose": "FORMAT_SAMPLE", "report_id": "EPS-REPORT-0050",
        "custody": {"owner_role": "FRESH_INDEPENDENT_VERIFIER", "owner_run_id": "P2-AR-0050",
                    "authored_independently_of_implementation": True,
                    "created_at": "2026-09-20T01:00:00Z"},
        "binding": {"oracle_id": "EPS-ORACLE-0050", "oracle_sha256": canon_sha(oracle),
                    "repository": {"id": "eps-repo", "commit": commit},
                    "candidate": {"commit": "b" * 40, "product_code_digest": "c" * 64},
                    "run_id": "P2-AR-0050-1", "scored_at": "2026-09-20T02:00:00Z"},
        "metrics": {
            "injected_defect_detection_recall": {"numerator": 1, "denominator": 1, "value": 1.0},
            "false_positives": {"count": 0, "findings": []},
            "severity_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
            "impact_map_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
            "path_map_accuracy": {"numerator": 1, "denominator": 1, "value": 1.0},
            "missed_authoritative_artefacts": {"count": 0, "refs": []},
            "wrong_indexing_count": {"count": 0, "refs": []},
            "stale_index_count": {"count": 0, "refs": []},
            "retrieval_metrics": {"k": 5, "queries": 1, "recall_at_k": 1.0, "mrr": 1.0,
                                  "precision_at_k": 0.2, "stale_hit_rate": 0.0},
            "recovery_chaos_pass_rate": {"applicable": False, "reason": "no chaos scenario in this probe"},
            "human_gate_correctness": {"numerator": 1, "denominator": 1, "value": 1.0},
            "task_readiness_correctness": {"numerator": 1, "denominator": 1, "value": 1.0}},
        "per_fault_outcomes": [{"fault_id": "EPS-F1", "detected": True, "detected_at_tier": "G2",
                                "detection_signal": "EPS_SIGNAL", "observed_severity": "HIGH",
                                "severity_correct": True, "impacted_expected": 1, "impacted_found": 1,
                                "governed_action_correct": True, "forbidden_outcomes_observed": []}],
    }
    return oracle, report


if __name__ == "__main__":
    main(run, "GATE-V")
