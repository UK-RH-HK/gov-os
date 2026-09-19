#!/usr/bin/env python3
"""P2-AR-0042 (BC-P2-02): write the builder-authored owner mapping (owner-spec.yaml) into the governed fields of
tests/governance/capability-evidence-map.yaml.

It writes only governed values: each capability's `automated_checks` and `independent_verification` owners, each
checklist item's `automated_checks` (owner ids) and the top-level `freshness_invalidation`. It derives nothing the
product derives: `gov contract compile` afterwards resolves every owner against the product, derives evidence_class,
health_scheduler_tiers, freshness_triggers, the adoption/operational-audit obligations and the remediation rule, and
binds the result in the source lock; `gov contract verify` re-checks all of it. The one value copied here is each
check/doctor owner's `tiers`, read from runtime/src/scheduler/catalogue.rs; verify refuses any that differ.

Usage: apply_owner_spec.py <repo-root>
"""
import re
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
here = Path(__file__).resolve().parent
spec = yaml.safe_load((here / "owner-spec.yaml").read_text())
map_path = root / "tests/governance/capability-evidence-map.yaml"
m = yaml.safe_load(map_path.read_text())

cat = (root / "runtime/src/scheduler/catalogue.rs").read_text()
tiers = {}
for mm in re.finditer(r'id: "([a-z_]+)",\s*surface: Surface::Family,.*?tiers: &\[([^\]]*)\]', cat, re.S):
    tiers["check:" + mm.group(1)] = [t.strip() for t in mm.group(2).split(",") if t.strip()]
for mm in re.finditer(r'doctor\(\s*"(D\d{3})"', cat):
    tiers["doctor:" + mm.group(1)] = ["G1", "G5"]

DEFAULT_CLASS = {
    "check": "governance health check",
    "doctor": "governance health check",
    "g0": "automated invariant/guard",
    "test": "unit/integration/system test",
    "human-gate": "human-gate evidence",
    "release": "clean-clone/release evidence",
    "heldout": "independent held-out test",
}


def owner(o):
    oid = o["id"]
    kind = oid.split(":", 1)[0]
    if kind == "obligation":
        cls = o.get("class") or ("independent held-out test" if oid == "obligation:AC-14" else "independent audit evidence")
    else:
        cls = o.get("class") or DEFAULT_CLASS[kind]
    out = {"id": oid, "class": cls}
    if kind in ("check", "doctor"):
        if oid not in tiers:
            sys.exit(f"{oid}: not in the scheduler catalogue")
        out["tiers"] = tiers[oid]
    if kind == "g0":
        out["tiers"] = ["G0"]
    if "record" in o:
        out["record"] = o["record"]
    if "tests" in o:
        out["tests"] = o["tests"]
    if o.get("ex"):
        out["exercises"] = o["ex"]
    return out


mapped = 0
for row in m["capabilities"]:
    cap = row["capability"]
    s = spec["capabilities"].get(cap)
    for it in row["checklist"]:
        it["automated_checks"] = []
    if not s:
        row["automated_checks"] = []
        row["independent_verification"] = []
        continue
    mapped += 1
    row["automated_checks"] = [owner(o) for o in s.get("owners", [])]
    row["independent_verification"] = [owner(o) for o in s.get("independent", [])]
    by_n = {i + 1: it for i, it in enumerate(row["checklist"])}
    for o in s.get("owners", []) + s.get("independent", []):
        for n in o.get("items", []) or []:
            if n not in by_n:
                sys.exit(f"{cap}: owner {o['id']} names item {n}; {cap} has {len(by_n)} items")
            if o["id"] not in by_n[n]["automated_checks"]:
                by_n[n]["automated_checks"].append(o["id"])
m["freshness_invalidation"] = spec["freshness_invalidation"]
map_path.write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=100000))
print(f"mapped {mapped} of {len(m['capabilities'])} capabilities; catalogue tiers for {len(tiers)} checks")
