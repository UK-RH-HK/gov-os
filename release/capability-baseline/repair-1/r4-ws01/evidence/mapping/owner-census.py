#!/usr/bin/env python3
"""P2-AR-0042 (BC-P2-02) — census of the committed evidence map for the report: per capability, its owners by kind,
evidence class and tier; capabilities with no G-tier owner; capabilities whose running owners are only builder tests;
checklist items that name no owner. Reads tests/governance/capability-evidence-map.yaml as committed (after `gov
contract verify` bound it); derives nothing the map does not state. Usage: owner-census.py <repo-root>
"""
import collections
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
m = yaml.safe_load((root / "tests/governance/capability-evidence-map.yaml").read_text())
rows = m["capabilities"]
kinds = collections.Counter()
per_cap = []
no_tier, tests_only, no_items = [], [], []
for r in rows:
    owners = (r.get("automated_checks") or []) + (r.get("independent_verification") or [])
    k = collections.Counter(o["id"].split(":", 1)[0] for o in owners)
    kinds.update(k)
    running_kinds = {x for x in k if x != "obligation"}
    if not r.get("health_scheduler_tiers"):
        no_tier.append(r["capability"])
    if running_kinds and running_kinds <= {"test"}:
        tests_only.append(r["capability"])
    for it in r["checklist"]:
        if not it.get("automated_checks"):
            no_items.append((r["capability"], it["id"], it["text"]))
    per_cap.append((r["capability"], r["gate"], len(owners), dict(k), r.get("evidence_class"),
                    r.get("health_scheduler_tiers"), sum(1 for it in r["checklist"] if it.get("automated_checks")),
                    len(r["checklist"])))
print("# owners by kind:", dict(kinds), "total", sum(kinds.values()))
print("# capabilities with no G-tier owner (%d): %s" % (len(no_tier), ", ".join(no_tier)))
print("# capabilities whose only running owners are builder tests (%d): %s" % (len(tests_only), ", ".join(tests_only)))
print("# checklist items naming no owner: %d of %d" % (len(no_items), sum(len(r["checklist"]) for r in rows)))
print("\n| Capability | Gate | Owners | By kind | Evidence classes | Tiers | Items with an owner |")
print("|---|---|---|---|---|---|---|")
for cap, gate, n, k, ec, tiers, owned, items in per_cap:
    kk = ", ".join(f"{a} {b}" for a, b in sorted(k.items()))
    ecs = ", ".join(ec) if isinstance(ec, list) else str(ec)
    print(f"| {cap} | {gate} | {n} | {kk} | {ecs} | {', '.join(tiers or []) or '—'} | {owned}/{items} |")
print("\n## Checklist items that name no owner\n")
for cap, iid, text in no_items:
    print(f"- `{iid}` {text}")
