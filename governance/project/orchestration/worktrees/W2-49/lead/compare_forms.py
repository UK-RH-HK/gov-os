"""Read-only: compare the Contract's two forms on waves and providers (P-B evidence, DEC-825 item 3).

Usage: python3 compare_forms.py <CONTRACT_v4.md> <contract.yaml>
"""
import re
import sys

import yaml


def from_md(path):
    caps, cur = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^### (CAP-\d+) ", line)
        if m:
            cur = m.group(1)
            caps[cur] = {"wave": None, "prov": []}
            continue
        if cur and line.startswith("- **Wave:**"):
            caps[cur]["wave"] = line.split("**Wave:**")[1].strip().split()[0]
        if cur and line.startswith("- **Provider:**"):
            caps[cur]["prov"] = sorted(p.strip() for p in line.split("**Provider:**")[1].split(","))
        m = re.match(r"^\s+- `(CAP-\d+\.[a-z]+)` \[(\w+)\](.*)$", line)
        if m:
            tail = m.group(3)
            prov = []
            if "· delivered by" in tail:
                prov = sorted(p.strip() for p in tail.rsplit("· delivered by", 1)[1].split(","))
            caps[m.group(1)] = {"wave": m.group(2), "prov": prov}
    return caps


def from_yaml(path):
    data = yaml.safe_load(open(path, encoding="utf-8"))
    caps = {}
    for cap in data.get("capabilities", []):
        caps[cap["id"]] = {"wave": str(cap.get("wave")), "prov": sorted(str(p) for p in cap.get("provider") or [])}
        for item in cap.get("covers") or []:
            prov = item.get("delivered_by") or item.get("provider") or []
            if isinstance(prov, str):
                prov = [prov]
            caps[item["id"]] = {"wave": str(item.get("wave")), "prov": sorted(str(p) for p in prov)}
    return caps


md, ym = from_md(sys.argv[1]), from_yaml(sys.argv[2])
print(f"ids: md {len(md)}, yaml {len(ym)}; md only {sorted(set(md) - set(ym))}; yaml only {sorted(set(ym) - set(md))}")
n = 0
for cid in sorted(set(md) & set(ym)):
    a, b = md[cid], ym[cid]
    if a["wave"] != b["wave"]:
        n += 1
        print(f"WAVE {cid} md={a['wave']} yaml={b['wave']}")
    if a["prov"] != b["prov"]:
        n += 1
        print(f"PROV {cid} md-only={sorted(set(a['prov']) - set(b['prov']))} yaml-only={sorted(set(b['prov']) - set(a['prov']))}")
print(f"differences: {n}")
