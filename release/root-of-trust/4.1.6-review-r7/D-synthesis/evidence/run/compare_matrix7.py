#!/usr/bin/env python3
"""AR-0022: compare reviewer C's committed matrix7 summary with this review's re-run, composed of the full run (every position
except P-TXN, whose rows recorded HARNESS_ERROR because txn7's JSON carries scrubbed paths) and the P-TXN-only run over the
resolved paths. Output: JSON on stdout. AR0022_SCRATCH names the scratch root."""
import json, os

S = os.environ.get("AR0022_SCRATCH", "<scratch>")
O = S + "/out/C"
C = S + "/export/release/root-of-trust/4.1.6-review-r7/C-compat-transaction/evidence/outputs/matrix7-summary.json"
full = json.load(open(O + "/matrix7/matrix7-summary.json"))
ptxn = json.load(open(O + "/matrix7-ptxn/matrix7-summary.json"))
com = json.load(open(C))
is_txn = lambda k: k.startswith("P-TXN|")
agg = {k: v for k, v in full["aggregate"].items() if not is_txn(k)}
agg.update({k: v for k, v in ptxn["aggregate"].items() if is_txn(k)})
diff = sorted(k for k in set(agg) | set(com["aggregate"]) if agg.get(k) != com["aggregate"].get(k))
props = {}
for name in sorted(set(com["properties"]) | set(full["properties"]) | set(ptxn["properties"])):
    f, p, c = full["properties"].get(name, {}), ptxn["properties"].get(name, {}), com["properties"].get(name, {})
    props[name] = {"full_run_without_valid_P-TXN": {k: v for k, v in f.items() if k != "sample"},
                   "P-TXN_run": {k: v for k, v in p.items() if k != "sample"},
                   "committed": {k: v for k, v in c.items() if k != "sample"}}
out = {"positions": len(agg), "position_aggregates_equal_to_committed": not diff, "position_aggregates_differing": diff,
       "rows": [sum(v["rows"] for v in agg.values()), sum(v["rows"] for v in com["aggregate"].values())],
       "by_binary_full_run_equal": full.get("by_binary") == com.get("by_binary"), "binaries_sha256_equal": full.get("binaries_sha256") == com.get("binaries_sha256"),
       "writing_rows_rot1": {"full_run": full.get("writing_rows_rot1"), "P-TXN_run": ptxn.get("writing_rows_rot1"), "committed": com.get("writing_rows_rot1")},
       "decisive_properties": {n: props[n] for n in props if n.startswith(("R2-H4", "LP-1r", "write_moved", "write_produced"))},
       "other_properties": {n: props[n] for n in props if not n.startswith(("R2-H4", "LP-1r", "write_moved", "write_produced"))}}
print(json.dumps(out, indent=1, sort_keys=True))
