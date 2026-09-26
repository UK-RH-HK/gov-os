"""BR-AR-0028 check 4 (before/after): the CONTROL-A baseline packet (unrepaired bridge) against the repaired packet.

Usage: $PY int04d_baseline_compare.py <baseline_packet_dir> <new_packet_dir>
For every item of the baseline packet: is the same unit (kind:id) -- or failing that, the same source PATH -- still
delivered by the repaired run, and where: main packet section, an overflow supplementary packet, or an evidence note?
Also: per-section counts before/after, facet coverage notices (FACET_MISSING) of the new packet, and the task inputs
in section I. Nothing is printed from any item body.
"""
import json
import sys
from pathlib import Path

import yaml


def rows(manifest):
    out = []
    for L, sec in (manifest.get("sections") or {}).items():
        items = sec.get("items") or []
        if L == "D":
            items = [r for sub in (sec.get("subblocks") or {}).values() for r in (sub.get("items") or [])]
        for r in items:
            out.append((L, r))
    return out


def key(r):
    u = r.get("unit") or {}
    return f"{u.get('kind')}:{u.get('id')}"


def main():
    base, new = Path(sys.argv[1]), Path(sys.argv[2])
    bm = json.loads((base / "manifest.json").read_text())
    nm = json.loads((new / "manifest.json").read_text())
    new_keys, new_paths = {}, {}
    for L, r in rows(nm):
        new_keys.setdefault(key(r), []).append(f"main:{L}")
        p = (r.get("source") or {}).get("path")
        if p:
            new_paths.setdefault(p, []).append(f"main:{L}")
    sroot = new / "supplementary"
    if sroot.is_dir():
        for q in sorted(p for p in sroot.iterdir() if p.is_dir()):
            sm = json.loads((q / "manifest.json").read_text())
            for L, r in rows(sm):
                new_keys.setdefault(key(r), []).append(f"supplementary/{q.name}")
                for o in (r.get("occurrences") or []):
                    if o.get("path"):
                        new_paths.setdefault(o["path"], []).append(f"supplementary/{q.name}")
                p = (r.get("source") or {}).get("path")
                if p:
                    new_paths.setdefault(p, []).append(f"supplementary/{q.name}")
    nroot = new / "notes"
    if nroot.is_dir():
        for f in sorted(nroot.iterdir()):
            text = f.read_text()
            doc = yaml.safe_load(text) or {}
            for c in (doc.get("claims") or []):
                for s in (c.get("sources") or c.get("citations") or []):
                    p = s.get("path") if isinstance(s, dict) else None
                    if p:
                        new_paths.setdefault(p, []).append(f"notes/{f.name}")
    report = {"baseline_items": 0, "kept_same_unit": 0, "kept_same_path_only": 0, "lost": [], "per_item": []}
    for L, r in rows(bm):
        report["baseline_items"] += 1
        k = key(r)
        p = (r.get("source") or {}).get("path")
        where = new_keys.get(k)
        status = "SAME_UNIT" if where else None
        if not where and p and p in new_paths:
            where, status = new_paths[p], "SAME_PATH"
        if status == "SAME_UNIT":
            report["kept_same_unit"] += 1
        elif status == "SAME_PATH":
            report["kept_same_path_only"] += 1
        else:
            report["lost"].append({"section": L, "unit": k, "path": p})
        report["per_item"].append({"baseline_section": L, "unit": k, "path": p, "status": status or "LOST",
                                   "now_in": sorted(set(where or []))})
    report["section_counts"] = {
        "before": {L: sum(1 for x, _ in rows(bm) if x == L) for L in "ABCDEFGHIJ"},
        "after_main": {L: sum(1 for x, _ in rows(nm) if x == L) for L in "ABCDEFGHIJ"},
    }
    report["facet_missing_after"] = [{"query_id": n.get("query_id"), "facet": n.get("facet"),
                                      "reason": (n.get("reason") or "")[:140]}
                                     for n in nm.get("notices") or [] if n.get("type") == "FACET_MISSING"]
    report["overflow_after"] = [{k: n.get(k) for k in ("query_id", "overflow_item_count", "note_id")}
                                for n in nm.get("notices") or [] if n.get("type") == "EVIDENCE_OVERFLOW"]
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
