"""Reconcile the derived contract views against the owner source for family delta (J1-J2, K1-K4, L1-L4, M1-M4, N1-N4).

Owner source (defines the universe): Governance_OS_Capability_Acceptance_Contract_v3.md lines 594-747.
Derived views: framework/contracts/governance-capability-acceptance.yaml (compiled), tests/governance/capability-evidence-map.yaml
(evidence map), docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md (generated view).

Run:  python3 DERIVED-VIEWS-JKLMN.py > DERIVED-VIEWS-JKLMN.out 2>&1
"""
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import WT, check, observe, summary  # noqa: E402

src = open(os.path.join(WT, "Governance_OS_Capability_Acceptance_Contract_v3.md")).read().splitlines()
caps = {}
cur = None
for i, line in enumerate(src, 1):
    if not (594 <= i <= 747):
        continue
    m = re.match(r"^## ([JKLMN]\d)\. (.*)$", line)
    if m:
        cur = m.group(1)
        caps[cur] = {"title": m.group(2).strip(), "line": i, "bullets": []}
        continue
    b = re.match(r"^- \[ \] (.*)$", line)
    if b and cur:
        caps[cur]["bullets"].append((i, b.group(1)))
print("---- owner-source universe (family delta) ----")
for c, d in caps.items():
    print(f"{c} (line {d['line']}) {d['title']}: {len(d['bullets'])} bullets -> " + "; ".join(f"L{n}: {t}" for n, t in d["bullets"]))
total = sum(len(d["bullets"]) for d in caps.values())
check("DV.universe", len(caps) == 18 and total == 93, "owner source defines 18 capabilities and 93 checklist bullets for family delta", {"capabilities": len(caps), "bullets": total})

comp = yaml.safe_load(open(os.path.join(WT, "framework/contracts/governance-capability-acceptance.yaml")))
cmap = {c["id"]: c for c in comp["capabilities"]}
for c, d in caps.items():
    e = cmap.get(c)
    ok = e is not None and e["title"] == d["title"] and e["source_reference"].endswith(f":{d['line']}")
    check(f"DV.compiled.{c}.heading", ok, f"compiled YAML carries {c} with the owner title and source line", e)
keys = sorted({k for c in caps for k in (cmap.get(c) or {}).keys()})
observe("DV.compiled.keys", "fields the compiled form carries per capability", keys)
check("DV.compiled.bullets", any(k in keys for k in ("bullets", "checklist", "items", "requirements")), "the compiled (machine-executable) form carries the checklist bullets of each capability", {"keys": keys})
req_fields = ["severity", "applicability", "evidence_class", "automated_checks", "freshness_triggers", "health_scheduler_tiers", "qualification_challenge_ids", "adoption_obligation"]
check("DV.compiled.fields", any(k in keys for k in req_fields), "the compiled form carries any of the Contract v3 'required contract fields per capability' (lines 53-73)", {"keys": keys})
emap = yaml.safe_load(open(os.path.join(WT, "tests/governance/capability-evidence-map.yaml")))
em = {e["capability"]: e for e in emap["capabilities"]}
rows = {c: {k: em.get(c, {}).get(k) for k in ("automated_checks", "evidence_class")} for c in caps}
observe("DV.map", "evidence-map rows for family delta", rows)
check("DV.map.1", all(em.get(c, {}).get("automated_checks") for c in caps), "every family-delta capability has at least one automated check/evidence owner in the evidence map", {c: r for c, r in rows.items() if not r["automated_checks"]})
gen = open(os.path.join(WT, "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md")).read()
check("DV.gen.1", all(f"`{c}`" in gen for c in caps), "the generated view lists every family-delta capability", None)
observe("DV.gen.2", "the generated view is a heading table only (no bullets)", {"mentions_first_bullet": caps["L3"]["bullets"][4][1] in gen})
summary()
