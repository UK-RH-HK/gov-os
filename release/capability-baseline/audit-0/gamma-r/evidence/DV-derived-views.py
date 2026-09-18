#!/usr/bin/env python3
"""P2-AR-0010 — reconcile the derived views against the owner source for family gamma (E1-E4, F1-F5, G1-G2, H1-H4, I1-I4).
Run from the worktree root: python3 release/capability-baseline/audit-0/gamma-r/evidence/DV-derived-views.py
Also runs `gov contract verify` (the product's own binding check)."""
import hashlib, json, re, subprocess, sys, os
import yaml

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
os.chdir(WT)
IDS = ["E1","E2","E3","E4","F1","F2","F3","F4","F5","G1","G2","H1","H2","H3","H4","I1","I2","I3","I4"]
src = open("Governance_OS_Capability_Acceptance_Contract_v3.md").read().split("\n")
print("owner source sha256:", hashlib.sha256(open("Governance_OS_Capability_Acceptance_Contract_v3.md","rb").read()).hexdigest())
print("canonical import sha256:", hashlib.sha256(open("framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md","rb").read()).hexdigest())

# owner-source headings, classes and bullets (checkbox lines) per capability
own, cur = {}, None
for i, l in enumerate(src, 1):
    m = re.match(r"^## ([A-Z]\d+)\. (.*?)( \*\*\[(.*)\]\*\*)?$", l)
    if m:
        cur = m.group(1)
        cls = "ORIGINAL"
        if m.group(4) and "POST-VERIFICATION" in m.group(4): cls = "POST_VERIFICATION_HARDENING"
        elif m.group(4) and "REFINEMENT" in m.group(4): cls = "EXECUTION_REFINEMENT"
        own[cur] = {"line": i, "title": m.group(2).strip(), "class": cls, "bullets": []}
        continue
    if l.startswith("# GATE") or l.startswith("# PRE-ADV"): cur = None
    if cur and re.match(r"^(\d+\. )?\s*-? ?\[ \] ", l):
        own[cur]["bullets"].append((i, re.sub(r"^(\d+\. )?\s*-? ?\[ \] ", "", l).strip()))

comp = {c["id"]: c for c in yaml.safe_load(open("framework/contracts/governance-capability-acceptance.yaml"))["capabilities"]}
emap = {r["capability"]: r for r in yaml.safe_load(open("tests/governance/capability-evidence-map.yaml"))["capabilities"]}
gen = open("docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md").read()
total = 0
print("\n%-4s %-5s %-5s %-6s %-9s %-7s %-10s %-24s %s" % ("cap", "line", "cline", "title", "class", "bullets", "compiled", "evidence_map", "generated_view"))
for cid in IDS:
    o, c, e = own[cid], comp.get(cid, {}), emap.get(cid, {})
    cline = int(c.get("source_reference", ":0").rsplit(":", 1)[1])
    total += len(o["bullets"])
    compiled_bullets = [k for k in c if k not in ("id", "title", "requirement_class", "source_reference", "family", "status")]
    in_gen = f"`{cid}` | {o['title']} |" in gen or f"`{cid}` |" in gen
    print("%-4s %-5d %-5d %-6s %-9s %-7d %-10s %-24s %s" % (
        cid, o["line"], cline, "same" if c.get("title") == o["title"] else "DIFF:" + str(c.get("title")),
        "same" if c.get("requirement_class") == o["class"] else "DIFF", len(o["bullets"]),
        "no-bullets" if not compiled_bullets else ",".join(compiled_bullets),
        f"{e.get('evidence_class')}/{len(e.get('automated_checks', []))}chk", "row present" if in_gen else "ABSENT"))
print("\ntotal owner-source checklist lines in scope:", total, "(H2 includes 26 dimensions + 5 statuses; the 'silent N/A is invalid' clause at line 515 is not a checkbox)")
print("compiled entry keys (all capabilities):", sorted({k for c in comp.values() for k in c}))
print("evidence map row keys:", sorted({k for r in emap.values() for k in r}))
print("\n$ gov contract verify --root", WT)
r = subprocess.run([os.path.join(WT, "target/release/gov"), "--json", "contract", "verify", "--root", WT], capture_output=True, text=True)
e = json.loads(r.stdout)
print("  ok=", e["ok"], json.dumps(e.get("result", e.get("error")))[:600])
