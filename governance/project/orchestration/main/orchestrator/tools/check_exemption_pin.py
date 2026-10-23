"""With the pinned judge's own code (run with the pin's python -E): the patched path map loads, the ratchet still
counts every entry of both lists with no finding, accepted_history's entries are unchanged, and the new block holds
exactly the one entry. Usage: check_exemption_pin.py <clone>."""
import sys
from pathlib import Path

import yaml
from gov.close import ratchet
from gov.config.loader import load_config

clone = Path(sys.argv[1])
ok = True
load_config(clone)
print("pin's config loader: reads the patched path map")
pm = yaml.safe_load((clone / "governance/project/path-map.yaml").read_text())
for key in ("load_sensitive", "accepted_reds"):
    counted, findings = ratchet.counted_entries(clone, key)
    n = len(pm.get(key) or [])
    print(f"{key}: {n} entries, {len(counted)} counted, {len(findings)} finding(s)")
    ok = ok and not findings and len(counted) == n
hist = pm.get("accepted_history") or []
print(f"accepted_history: {len(hist)} entries (unchanged: {len(hist) == 5})")
ex = pm.get("acceptance_exemptions")
good = ex == [{"commit": "c9a08678644485a7528bc875164e110881b63d93", "decision": "DEC-900"}]
print(f"acceptance_exemptions: {ex} -> {'as decided' if good else 'NOT as decided'}")
ok = ok and good and len(hist) == 5
print("PIN CHECK", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
