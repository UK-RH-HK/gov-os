#!/usr/bin/env python3
"""BR-AR-0016: aggregate the per-item measurement (anchors.public.json) and the must_state classification table
(must_state_classes.yaml, keys only) into category counts, per-gate/per-class/per-control summaries and a
counterfactual ("what if this cause were removed") recall table.

Reads the QUARANTINED grade report and oracle at runtime only to obtain each failing query's required-item COUNT
(for the counterfactual recall); it prints no oracle value. Output is keys, counts and recalls only."""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys

import yaml

DOM = "release/orchestration/phase-2-context-bridge"


def quarantined(path):
    r = subprocess.run(["git", "show", f"bridge/grade-0012:{DOM}/{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    return yaml.safe_load(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--must-state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--capture", required=True)
    args = ap.parse_args()

    anchors = json.load(open(args.anchors))
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import measure_anchors as M
    cap = json.load(open(args.capture))
    compiled = {r["id"] for rows in cap["queries_log"].values() for r in rows}
    for r in anchors:  # always re-derive the class from the measured fields with the CURRENT rules
        r["class"], r["cause"], r["bridge_signals"] = M.classify(r, compiled)
    ms = yaml.safe_load(open(args.must_state))["items"]
    grade = quarantined("DEMONSTRATION/grading/run-1.yaml")
    oracle = quarantined("DEMONSTRATION/oracle/oracle.yaml")
    n_req = {q["query_id"]: len(q.get("required") or []) for q in oracle["queries"] + oracle["controls"]}

    # ---- G4 stage-level [D] items: one key per stage, from its any_of alternatives
    stage_d = {}
    for r in anchors:
        if r["key"].startswith("G4."):
            stage = ".".join(r["key"].split(".")[:3]) + ".D"
            stage_d.setdefault(stage, []).append(r)
    order = ["GRADER_DEFECT", "ORACLE_STRICTNESS", "AGENT_BEHAVIOUR", "BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE",
             "BRIDGE_NOT_RETRIEVABLE"]
    items = []
    for stage, alts in sorted(stage_d.items()):
        best = sorted(alts, key=lambda r: order.index(r["class"]))[0]
        items.append({"key": stage, "gate": "G4", "type": "anchor(any_of)", "class": best["class"],
                      "cause": best["cause"], "alternatives": {a["key"].split(".")[-1]: a["class"] for a in alts}})
    for r in anchors:
        if r["key"].startswith("G4."):
            continue
        gate = r["key"].split(".")[0]
        alt = None
        if r["cause"] == "GD-8":
            # re-classify as if GD-8 were resolved "a whole-document citation does NOT match a sectioned anchor"
            alt = "/".join(M.classify({**r, "doc_level_citation_this_answer": False}, compiled)[:2])
        items.append({"key": r["key"], "gate": gate, "type": "anchor", "kind": r["kind"], "class": r["class"],
                      "cause": r["cause"], "signals": r["bridge_signals"], "alt_if_gd8_resolved_strict": alt})
    for m in ms:
        items.append({"key": m["key"], "gate": m["key"].split(".")[0], "type": "must_state", "class": m["class"],
                      "cause": m["basis"]})

    gated = [i for i in items if i["gate"] in ("G4", "G5", "G6", "G8")]
    info = [i for i in items if i["gate"] == "G3i"]

    def tally(rows):
        c = collections.Counter(i["class"] for i in rows)
        return {k: c.get(k, 0) for k in order}

    def tally_cause(rows):
        return dict(sorted(collections.Counter(f'{i["class"]}/{i["cause"]}' for i in rows).items()))

    out = {"totals_gated": {"items": len(gated), "by_class": tally(gated), "by_cause": tally_cause(gated)},
           "totals_gated_anchors": tally([i for i in gated if i["type"] != "must_state"]),
           "totals_gated_must_state": tally([i for i in gated if i["type"] == "must_state"]),
           "informational_auth": {"items": len(info), "by_class": tally(info)},
           "per_gate": {g: tally([i for i in gated if i["gate"] == g]) for g in ("G4", "G5", "G6", "G8")}}

    # ---- per query class (G5) and per control (G8)
    per_class = collections.defaultdict(list)
    for i in gated:
        if i["gate"] == "G5":
            qid = i["key"].split(".")[1]
            per_class[qid.split("-")[1]].append(i)
    out["per_query_class"] = {k: {"items": len(v), "by_class": tally(v)} for k, v in sorted(per_class.items())}
    per_ctrl = collections.defaultdict(list)
    for i in gated:
        if i["gate"] == "G8":
            per_ctrl[i["key"].split(".")[1]].append(i)
    out["per_control"] = {k: {"items": len(v), "by_class": tally(v)} for k, v in sorted(per_ctrl.items())}

    # ---- counterfactual [D] recall per failing query (G5/G8): remove one cause family at a time
    G = grade["gates"]
    fails = [q for q in G["G5_query_classes"]["per_query"] + G["G8_controls"]["per_query"] if q["result"] == "FAIL"]
    by_q = collections.defaultdict(list)
    for r in anchors:
        if r["key"].startswith(("G5.", "G8.")):
            by_q[r["key"].split(".")[1]].append(r)
    cf = {}
    fam = {"grader": {"GRADER_DEFECT"}, "agent": {"AGENT_BEHAVIOUR"},
           "bridge_retrievable": {"BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE"}}
    for q in fails:
        qid, n = q["query_id"], n_req[q["query_id"]]
        missed = by_q.get(qid, [])
        base = (n - len(missed)) / n if n else 1.0
        row = {"recall": round(base, 3)}
        for name, classes in fam.items():
            fixed = sum(1 for r in missed if r["class"] in classes)
            row[f"recall_if_{name}_fixed"] = round((n - len(missed) + fixed) / n, 3)
        row["recall_if_grader_and_agent_fixed"] = round(
            (n - len(missed) + sum(1 for r in missed if r["class"] in fam["grader"] | fam["agent"])) / n, 3)
        row["must_state_missing"] = sum(1 for m in ms if m["key"].split(".")[1] == qid)
        cf[qid] = row
    ms_by_q = collections.defaultdict(list)
    for m in ms:
        if m["key"].startswith(("G5.", "G8.")):
            ms_by_q[m["key"].split(".")[1]].append(m["class"])
    for qid, row in cf.items():
        cls_ms = ms_by_q.get(qid, [])
        for name, classes in (("grader_oracle", {"GRADER_DEFECT", "ORACLE_STRICTNESS"}),
                              ("grader_oracle_agent", {"GRADER_DEFECT", "ORACLE_STRICTNESS", "AGENT_BEHAVIOUR"}),
                              ("bridge", {"BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE", "BRIDGE_NOT_RETRIEVABLE"})):
            missed = by_q.get(qid, [])
            n = n_req[qid]
            rec_ = (n - sum(1 for r in missed if r["class"] not in classes)) / n if n else 1.0
            row[f"passes_if_{name}_fixed"] = bool(rec_ >= 0.8 - 1e-9 and all(c in classes for c in cls_ms))
    out["counterfactual_d_recall"] = cf
    thr = 0.8

    def passes(col):
        return sorted(q for q, r in cf.items() if r[col] >= thr - 1e-9)
    out["counterfactual_summary"] = {
        "failing_queries": len(cf),
        "d_recall_ok_now": passes("recall"),
        "d_recall_ok_if_grader_fixed": passes("recall_if_grader_fixed"),
        "d_recall_ok_if_grader_and_agent_fixed": passes("recall_if_grader_and_agent_fixed"),
        "d_recall_ok_if_bridge_fixed_only": passes("recall_if_bridge_retrievable_fixed"),
    }
    for name in ("grader_oracle", "grader_oracle_agent", "bridge"):
        out["counterfactual_summary"][f"queries_passing_if_{name}_fixed"] = sorted(
            q for q, r in cf.items() if r[f"passes_if_{name}_fixed"])
    # ---- class-level counterfactual (G5: a class passes with >= 2 of 3 subjects; QC9 needs all 3)
    passing_now = {q["query_id"] for q in G["G5_query_classes"]["per_query"] if q["result"] == "PASS"}

    def classes(passq):
        res = {}
        for c in range(1, 11):
            n = sum(1 for s_ in (1, 2, 3) if f"S{s_}-QC{c}" in passq)
            res[f"QC{c}"] = (n == 3) if c == 9 else (n >= 2)
        return sorted(k for k, v in res.items() if v)
    out["counterfactual_g5_classes"] = {
        "now": classes(passing_now),
        "grader_oracle_fixed": classes(passing_now | set(out["counterfactual_summary"]["queries_passing_if_grader_oracle_fixed"])),
        "grader_oracle_agent_fixed": classes(passing_now | set(
            out["counterfactual_summary"]["queries_passing_if_grader_oracle_agent_fixed"])),
        "bridge_fixed": classes(passing_now | set(out["counterfactual_summary"]["queries_passing_if_bridge_fixed"])),
        "all_fixed_except_bridge_not_retrievable": classes(passing_now | set(cf)),
    }
    out["items"] = items
    json.dump(out, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("items", "counterfactual_d_recall")}, indent=1))


if __name__ == "__main__":
    main()
