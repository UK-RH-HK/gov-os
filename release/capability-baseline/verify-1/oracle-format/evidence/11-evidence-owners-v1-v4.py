#!/usr/bin/env python3
"""P2-AR-0045 — AC-10 slice for Gate V: do V1-V4 still have zero evidence owners (iteration-0 A0-V1-01)?"""
import yaml, json
d = yaml.safe_load(open('tests/governance/capability-evidence-map.yaml'))
rows = d.get('capabilities') or d
bad = []
for r in rows:
    if r.get('capability') not in ('V1', 'V2', 'V3', 'V4'):
        continue
    ec = r.get('evidence_class')
    iv = r.get('independent_verification')
    tiers = r.get('health_scheduler_tiers')
    print(f"{r['capability']:3s} evidence_class={json.dumps(ec)} tiers={json.dumps(tiers)}")
    print(f"    independent_verification={json.dumps(iv)[:200]}")
    for item in r.get('checklist', []):
        owners = (item.get('automated_checks') or []) + (item.get('independent_verification') or [])
        if not owners:
            bad.append(f"{item['id']} (line {item['line']}) has zero evidence owners")
        else:
            print(f"    {item['id']:6s} {len(owners)} owner(s)")
print()
print("bullets with zero evidence owners:", len(bad))
for b in bad:
    print(" -", b)
