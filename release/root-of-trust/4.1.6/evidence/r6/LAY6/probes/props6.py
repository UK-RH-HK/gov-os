#!/usr/bin/env python3
"""AR-0015 lay6: compute LP-1s_restated_rev6 from the matrix summary's writing-rows file.

LP-1s_restated_rev6: among rows whose changed paths include any path under governance/trust/ or any occupation
entry (governance/kernel, governance/project, governance/generated, governance/framework.lock and below,
spec/audits/GOVERNANCE-ADOPTION, .governance-runtime/migration), count rows whose state_after is COMPLETE
and kernel_tampered is not true (counterexamples).

Usage: props6.py <matrix5-summary.json> <writing-rows-file> <out.json>
"""
import gzip, json, os, sys
sys.dont_write_bytecode = True

OCCUPATION_ENTRIES = {"governance/kernel", "governance/project", "governance/generated",
                     "governance/framework.lock", "spec/audits/GOVERNANCE-ADOPTION",
                     ".governance-runtime/migration"}


def path_touches_trust_or_occupation(paths):
    for p in paths:
        if p.startswith("governance/trust/") or p == "governance/trust":
            return True
        if p in OCCUPATION_ENTRIES:
            return True
        if p.startswith("governance/framework.lock/"):
            return True
    return False


def main():
    summary_path = sys.argv[1]
    rows_path = sys.argv[2]
    out_path = sys.argv[3]
    summary = json.load(open(summary_path))
    # load rows from gzipped jsonl
    rows = []
    if rows_path.endswith(".gz"):
        with gzip.open(rows_path, "rt") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    else:
        rows = json.load(open(rows_path))
    # filter to non-skipped rows
    active = [r for r in rows if not r.get("skipped")]
    # find rows that touch trust or occupation entries
    relevant = [r for r in active if path_touches_trust_or_occupation(r.get("paths", []))]
    counterexamples = [r for r in relevant if r.get("state_after") == "COMPLETE" and r.get("kernel_tampered_after") is not True]
    result = {
        "LP-1s_restated_rev6": {
            "description": "rows touching governance/trust/ or occupation entries with state_after=COMPLETE and kernel_tampered!=true",
            "total_active_rows": len(active),
            "rows_touching_trust_or_occupation": len(relevant),
            "counterexamples": len(counterexamples),
            "sample": [
                {"kind": r["kind"], "layout": r["layout"], "position": r["position"],
                 "argv": r["argv"][:4], "state_after": r["state_after"],
                 "kernel_tampered_after": r.get("kernel_tampered_after"),
                 "paths": [p for p in r.get("paths", []) if path_touches_trust_or_occupation([p])][:6]}
                for r in counterexamples[:12]
            ],
        }
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    json.dump(result, open(out_path, "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({"counterexamples": len(counterexamples), "relevant": len(relevant), "active": len(active)}))


if __name__ == "__main__":
    main()
