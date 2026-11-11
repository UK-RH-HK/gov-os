"""Every entry of the path map's lists that would not count at <root>'s HEAD (read-only; prints).
Usage: PYTHONPATH=<main tree>/src python3 lists.py <root>
accepted_reds, load_sensitive: gov.close.ratchet.counted_entries. accepted_history: history.accepted_history.
acceptance_exemptions: the same test gates.owner_listed applies (it subtracts the commits the entries name)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from gov.close import gates as G, history as H, ratchet as R

root = Path(sys.argv[1]).resolve()
pm = yaml.safe_load((root / H.PATH_MAP_REL).read_text(encoding="utf-8")) or {}
for key in (R.ACCEPTED_REDS, R.LOAD_SENSITIVE):
    counted, found = R.counted_entries(root, key)
    print(f"{key}: {len(pm.get(key) or [])} entries, {len(counted)} count, {len(found)} refused")
    for f in found:
        print("   REFUSED:", f["message"][:400])
accepted, refused = H.accepted_history(root, pm)
print(f"accepted_history: {len(pm.get('accepted_history') or [])} entries, {len(accepted)} accepted, {len(refused)} refused")
for f in refused:
    print("   REFUSED:", f["message"][:400])
reg = H.register_entries(root, pm.get(H.REGISTER_KEY))
entries = pm.get(G.EXEMPTIONS_KEY) or []
bad = [(e.get("commit"), e.get("decision"), H._refused_because(e.get("commit"), e.get("decision"), reg))
       for e in entries if H._refused_because(e.get("commit"), e.get("decision"), reg)]
print(f"acceptance_exemptions: {len(entries)} entries, {len(bad)} would not clear a commit")
for b in bad:
    print("   NOT CLEARING:", b)
