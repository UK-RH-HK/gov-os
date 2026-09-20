#!/usr/bin/env python3
"""P2-AR-0045: labelled V4 score-report FORMAT_SAMPLEs, valid and one attack per V4 bullet / binding rule.

The valid report is bound to samples/valid/oracle.json by that document's canonical digest, which the
product reports as `canonical_sha256`. Nothing here is a qualification result.
"""
import copy, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("mk", os.path.join(os.path.dirname(os.path.abspath(__file__)), "03-make-samples.py"))
mk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mk)

OUT = mk.OUT
ORACLE = os.path.join(OUT, "valid/oracle.json")
res = json.loads(subprocess.run(["target/release/gov", "--json", "oracle", "validate", ORACLE],
                                capture_output=True, text=True).stdout)["result"]
DIGEST = res["canonical_sha256"]
print("bound oracle canonical_sha256 =", DIGEST)

base = mk.report(DIGEST)
mk.write("valid/score-report.json", copy.deepcopy(base))

V4 = ["injected_defect_detection_recall", "false_positives", "severity_accuracy", "impact_map_accuracy",
      "path_map_accuracy", "missed_authoritative_artefacts", "wrong_indexing_count", "stale_index_count",
      "retrieval_metrics", "recovery_chaos_pass_rate", "human_gate_correctness", "task_readiness_correctness"]
for i, f in enumerate(V4, 1):
    d = mk.report(DIGEST)
    d["metrics"].pop(f)
    mk.write(f"invalid/v4-{i:02d}-missing-{f.replace('_','-')}.json", d)

def rep(**kw):
    return mk.report(DIGEST)

# arithmetic
d = rep(); d["metrics"]["injected_defect_detection_recall"]["value"] = 0.95
mk.write("invalid/arith-01-recall-value-not-quotient.json", d)
d = rep(); d["metrics"]["injected_defect_detection_recall"] = {"numerator": 2, "denominator": 2, "value": 1.0}
mk.write("invalid/arith-02-recall-numerator-not-from-outcomes.json", d)
d = rep(); d["metrics"]["injected_defect_detection_recall"] = {"numerator": 3, "denominator": 2, "value": 1.5}
mk.write("invalid/arith-03-numerator-exceeds-denominator.json", d)
d = rep(); d["metrics"]["severity_accuracy"] = {"numerator": 2, "denominator": 2, "value": 1.0}
mk.write("invalid/arith-04-severity-accuracy-wrong-denominator.json", d)
d = rep(); d["metrics"]["impact_map_accuracy"] = {"numerator": 4, "denominator": 4, "value": 1.0}
mk.write("invalid/arith-05-impact-map-accuracy-inflated.json", d)
d = rep(); d["metrics"]["false_positives"] = {"count": 0, "findings": ["SMP-FP-1", "SMP-FP-2"]}
mk.write("invalid/arith-06-false-positive-count-mismatch.json", d)
d = rep(); d["metrics"]["wrong_indexing_count"] = {"count": 7, "refs": ["sample/ops/credentials.env"]}
mk.write("invalid/arith-07-count-metric-mismatch.json", d)
d = rep(); d["metrics"]["path_map_accuracy"] = {"applicable": False, "reason": "not measured"}
mk.write("invalid/arith-08-path-map-na-though-oracle-has-one.json", d)
d = rep(); d["metrics"]["severity_accuracy"] = {"applicable": False, "reason": "not measured"}
mk.write("invalid/arith-09-severity-na-though-detections-exist.json", d)
d = rep(); d["metrics"]["retrieval_metrics"]["queries"] = 9
mk.write("invalid/arith-10-retrieval-query-count-not-from-oracle.json", d)
d = rep(); d["metrics"]["path_map_accuracy"] = {"numerator": 2, "denominator": 9, "value": 2 / 9}
mk.write("invalid/arith-11-path-map-denominator-not-entry-count.json", d)

# per-fault outcome integrity
d = rep(); d["per_fault_outcomes"][1]["severity_correct"] = True
mk.write("invalid/outcome-01-undetected-fault-severity-correct.json", d)
d = rep(); d["per_fault_outcomes"][1]["impacted_found"] = 1
mk.write("invalid/outcome-02-undetected-fault-claims-impact.json", d)
d = rep(); d["per_fault_outcomes"][0]["detection_signal"] = None
mk.write("invalid/outcome-03-detected-fault-without-signal.json", d)
d = rep(); d["per_fault_outcomes"][0]["impacted_found"] = 5
mk.write("invalid/outcome-04-impacted-found-exceeds-expected.json", d)
d = rep(); d["per_fault_outcomes"][0]["impacted_expected"] = 1
mk.write("invalid/outcome-05-impacted-expected-not-from-oracle.json", d)
d = rep(); d["per_fault_outcomes"][0]["observed_severity"] = "LOW"
mk.write("invalid/outcome-06-severity-correct-contradicts-oracle.json", d)

# UNSCORED INJECTED FAULT: drop the outcome for SMP-F-002 and make the arithmetic self-consistent,
# so only the oracle cross-check can catch it.
d = rep()
d["per_fault_outcomes"] = [d["per_fault_outcomes"][0]]
d["metrics"]["injected_defect_detection_recall"] = {"numerator": 1, "denominator": 1, "value": 1.0}
d["metrics"]["impact_map_accuracy"] = {"numerator": 2, "denominator": 3, "value": 2 / 3}
mk.write("invalid/bind-01-unscored-injected-fault.json", d)
d = rep(); d["per_fault_outcomes"].append({
    "fault_id": "SMP-F-999", "detected": True, "detected_at_tier": "G5", "detection_signal": "X",
    "observed_severity": "LOW", "severity_correct": True, "impacted_expected": 0, "impacted_found": 0,
    "governed_action_correct": True, "forbidden_outcomes_observed": []})
d["metrics"]["injected_defect_detection_recall"] = {"numerator": 2, "denominator": 3, "value": 2 / 3}
d["metrics"]["severity_accuracy"] = {"numerator": 2, "denominator": 2, "value": 1.0}
mk.write("invalid/bind-02-outcome-for-fault-not-in-oracle.json", d)
d = rep(); d["binding"]["oracle_sha256"] = "4" * 64
mk.write("invalid/bind-03-unbound-wrong-oracle-digest.json", d)
d = rep(); d["binding"]["oracle_id"] = "P2AR0045-SAMPLE-ORACLE-OTHER"
mk.write("invalid/bind-04-unbound-wrong-oracle-id.json", d)
d = rep(); d["binding"]["repository"]["commit"] = "9" * 40
mk.write("invalid/bind-05-unbound-wrong-repository-commit.json", d)
d = rep(); d["binding"].pop("oracle_sha256")
mk.write("invalid/bind-06-report-without-oracle-digest.json", d)
d = rep(); d.pop("binding")
mk.write("invalid/bind-07-report-without-binding.json", d)
d = rep(); d["purpose"] = "QUALIFICATION"
mk.write("invalid/bind-08-qualification-report-against-sample-oracle.json", d)
d = rep(); d["per_fault_outcomes"] = []
mk.write("invalid/bind-09-no-outcomes-at-all.json", d)
print("wrote report samples")
