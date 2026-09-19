#!/usr/bin/env python3
"""P2-AR-0014 supplementary check (builder evidence, not an audit probe).

beta-r DERIVED-views-reconciliation tests `bullet in json.dumps(compiled_entry)` and zeta-r DV-derived-view-reconciliation
tests `bullet[:40] in json.dumps(compiled_W_entry)`. json.dumps escapes every non-ASCII character by default
(ensure_ascii=True), so a bullet containing U+2192 '→' can never match, however faithfully it is carried. This script
repeats exactly those two comparisons with ensure_ascii=False, lists the bullets whose outcome depends on the escaping,
and additionally checks every owner-source checklist line (all 713 + 9) against the compiled form's reconstructed items.
"""
import json, os, re, sys
import yaml

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
src = open(os.path.join(WT, "Governance_OS_Capability_Acceptance_Contract_v3.md"), encoding="utf-8").read().splitlines()
comp = yaml.safe_load(open(os.path.join(WT, "framework/contracts/governance-capability-acceptance.yaml"), encoding="utf-8"))
cc = {c["id"]: c for c in comp["capabilities"]}

# beta-r's parse (C/D/R), verbatim logic
own, cur = {}, None
for i, l in enumerate(src, 1):
    m = re.match(r"^## ([CDR]\d+)\. (.*)$", l)
    if m:
        cur = m.group(1); own[cur] = []; continue
    if l.startswith("#"):
        cur = None
    if cur and re.match(r"^- \[ \] ", l):
        own[cur].append((i, l[6:]))
esc = noesc = total = 0
for cid, bl in own.items():
    for n, b in bl:
        total += 1
        a = b in json.dumps(cc[cid]); u = b in json.dumps(cc[cid], ensure_ascii=False)
        esc += a; noesc += u
        if a != u:
            print(f"[beta-r scope] {cid} L{n} {b!r}: carried (ensure_ascii=False) but escaped by json.dumps default")
print(f"[beta-r scope] bullets={total} matched with json.dumps default={esc} matched with ensure_ascii=False={noesc}")

# zeta-r's parse (W), verbatim logic
caps, cur = {}, None
for i, line in enumerate(src, 1):
    m = re.match(r"^## (W\d+)\. (.*)$", line)
    if m:
        cur = m.group(1); caps[cur] = []; continue
    if line.startswith("# ") and cur:
        cur = None
    if cur and line.strip().startswith("- [ ]"):
        caps[cur].append((i, line.strip()[6:]))
esc = noesc = total = 0
for k, bl in caps.items():
    for n, b in bl:
        total += 1
        a = b[:40] in json.dumps(cc[k]); u = b[:40] in json.dumps(cc[k], ensure_ascii=False)
        esc += a; noesc += u
        if a != u:
            print(f"[zeta-r scope] {k} L{n} {b!r}: carried (ensure_ascii=False) but escaped by json.dumps default")
print(f"[zeta-r scope] W bullets={total} matched with json.dumps default={esc} matched with ensure_ascii=False={noesc}")

# every checklist line of the owner source, reconstructed from the compiled form
carried = {}
for c in comp["capabilities"]:
    for it in c["checklist"]:
        carried[it["line"]] = (f"{it['number']}. [ ] " if "number" in it else "- [ ] ") + it["text"]
for s in comp["preamble"] + comp["closing"]:
    for it in s["checklist"]:
        carried[it["line"]] = (f"{it['number']}. [ ] " if "number" in it else "- [ ] ") + it["text"]
lines = [(i, l) for i, l in enumerate(src, 1) if re.match(r"^\s*(-|\d+\.) \[ \] ", l)]
bad = [(i, l) for i, l in lines if carried.get(i) != l]
print(f"[all] owner-source checklist lines={len(lines)} carried verbatim by the compiled form={len(lines) - len(bad)} differing={bad}")
alpha = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "S1", "S2", "S3", "S4", "S5", "S6", "T1", "T2", "T3"]
print(f"[alpha-r scope] bullets carried in compiled 'checklist' for {len(alpha)} capabilities: {sum(len(cc[a]['checklist']) for a in alpha)} (alpha-r's C0 summary line prints a literal '0', it does not count)")
sys.exit(1 if bad else 0)
