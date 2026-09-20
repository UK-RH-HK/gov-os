#!/usr/bin/env python3
"""P2-AR-0045 — how deeply is each V4 metric bound to the oracle?

For each V4 metric, take the valid score-report sample, replace the metric with a self-serving but
internally arithmetic-consistent value, and ask whether `gov oracle validate --oracle <the oracle>`
still accepts the report. A metric that survives is one a Phase-4 scorer can simply assert.
Run from the repository root.
"""
import copy, json, os, subprocess, sys

GOV = "target/release/gov"
S = "release/capability-baseline/verify-1/oracle-format/samples"
ORACLE = f"{S}/valid/oracle.json"
TMP = "release/capability-baseline/verify-1/oracle-format/samples/probe"
os.makedirs(TMP, exist_ok=True)
base = json.load(open(f"{S}/valid/score-report.json"))


def check(name, doc):
    p = os.path.join(TMP, name + ".json")
    json.dump(doc, open(p, "w"), indent=1)
    env = json.loads(subprocess.run([GOV, "--json", "oracle", "validate", p, "--oracle", ORACLE],
                                    capture_output=True, text=True).stdout)
    if env.get("ok"):
        return "ACCEPTED", ""
    e = env["error"]
    vs = (e.get("details") or {}).get("violations") or []
    return e["code"], (f'{vs[0].get("at","")} :: {vs[0].get("problem","")[:80]}' if vs else e["message"][:80])


cases = []

d = copy.deepcopy(base)
d["metrics"]["path_map_accuracy"] = {"numerator": 3, "denominator": 3, "value": 1.0}
cases.append(("V4.5 path-map accuracy claimed perfect", "v4-05-path-map-claimed-perfect", d))

d = copy.deepcopy(base)
d["metrics"]["recovery_chaos_pass_rate"] = {"numerator": 100, "denominator": 100, "value": 1.0}
cases.append(("V4.10 chaos pass rate claimed 100/100", "v4-10-chaos-claimed-perfect", d))

d = copy.deepcopy(base)
d["metrics"]["human_gate_correctness"] = {"numerator": 500, "denominator": 500, "value": 1.0}
cases.append(("V4.11 human-gate correctness claimed 500/500", "v4-11-human-gate-claimed-perfect", d))

d = copy.deepcopy(base)
d["metrics"]["task_readiness_correctness"] = {"numerator": 999, "denominator": 999, "value": 1.0}
cases.append(("V4.12 task/readiness claimed 999/999", "v4-12-readiness-claimed-perfect", d))

d = copy.deepcopy(base)
d["metrics"]["missed_authoritative_artefacts"] = {"count": 0, "refs": []}
cases.append(("V4.6 missed authoritative artefacts zeroed", "v4-06-missed-zeroed", d))

d = copy.deepcopy(base)
d["metrics"]["wrong_indexing_count"] = {"count": 0, "refs": []}
cases.append(("V4.7 wrong-indexing count zeroed", "v4-07-wrong-indexing-zeroed", d))

d = copy.deepcopy(base)
d["metrics"]["wrong_indexing_count"] = {"count": 1, "refs": ["sample/not/in/the/oracle.txt"]}
cases.append(("V4.7 wrong-indexing refs not in the oracle", "v4-07-wrong-indexing-alien-refs", d))

d = copy.deepcopy(base)
d["metrics"]["retrieval_metrics"] = {"k": 5, "queries": 1, "recall_at_k": 1.0, "mrr": 1.0,
                                     "precision_at_k": 1.0, "stale_hit_rate": 0.0}
cases.append(("V4.9 retrieval metrics claimed perfect", "v4-09-retrieval-claimed-perfect", d))

d = copy.deepcopy(base)
d["metrics"]["false_positives"] = {"count": 0, "findings": []}
cases.append(("V4.2 false positives zeroed", "v4-02-false-positives-zeroed", d))

d = copy.deepcopy(base)
for o in d["per_fault_outcomes"]:
    o["governed_action_correct"] = True
cases.append(("V1.8 governed-action correctness self-asserted", "v1-08-governed-action-self-asserted", d))

d = copy.deepcopy(base)
d["per_fault_outcomes"][1]["forbidden_outcomes_observed"] = []
cases.append(("V1.9 forbidden outcomes silently emptied", "v1-09-forbidden-outcomes-emptied", d))

print(f"{'attack':50s} {'result':32s} detail")
for label, name, doc in cases:
    code, det = check(name, doc)
    print(f"{label:50s} {code:32s} {det}")

print()
print("A score report validated WITHOUT its oracle (no --oracle):")
p = os.path.join(TMP, "v4-05-path-map-claimed-perfect.json")
env = json.loads(subprocess.run([GOV, "--json", "oracle", "validate", p], capture_output=True, text=True).stdout)
print("  ", "ACCEPTED" if env.get("ok") else env["error"]["code"],
      "| binding_verified present:", "binding_verified" in (env.get("result") or {}))
