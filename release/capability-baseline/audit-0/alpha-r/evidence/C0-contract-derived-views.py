#!/usr/bin/env python3
"""Derived-view reconciliation for the alpha scope (frozen contract §1: the owner source defines the universe; P2-HO-0001:
an omission or distortion in a derived view within scope is itself a finding).
Runs `gov contract verify` (read-only) against this worktree, then compares, per alpha capability, the owner source's
checklist bullets / advanced-qualification challenge lines with the compiled YAML, the evidence map and the generated view.
Run: PROBE_TMP=<scratch> python3 C0-contract-derived-views.py
"""
import os, sys, json, re, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml
sb = Sandbox("c0")
v = sb.gov("contract", "verify", "--root", REPO, cwd=sb.home, quiet=True)
print("[C0] gov contract verify ->", json.dumps(v.get("result") or v.get("error"))[:600])
src = open(os.path.join(REPO, "Governance_OS_Capability_Acceptance_Contract_v3.md")).read().splitlines()
ALPHA = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "S1", "S2", "S3", "S4", "S5", "S6", "T1", "T2", "T3"]
caps = {}; cur = None
for i, line in enumerate(src, 1):
    m = re.match(r"^## ([A-Z][0-9]+)\. (.*)$", line)
    if m:
        cur = m.group(1); caps[cur] = {"line": i, "bullets": [], "challenge": None}; continue
    if line.startswith("# ") or line.startswith("---"):
        cur = None if line.startswith("# ") else cur
    if cur and re.match(r"^\s*(\d+\. )?- \[ \]|^\s*\d+\. \[ \]", line):
        caps[cur]["bullets"].append(i)
    if cur and line.startswith("**Advanced qualification challenge:**"):
        caps[cur]["challenge"] = i
comp = {c["id"]: c for c in yaml.safe_load(open(os.path.join(REPO, "framework/contracts/governance-capability-acceptance.yaml")))["capabilities"]}
emap = {c["capability"]: c for c in yaml.safe_load(open(os.path.join(REPO, "tests/governance/capability-evidence-map.yaml")))["capabilities"]}
gen = open(os.path.join(REPO, "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md")).read()
tot = 0
for c in ALPHA:
    s = caps[c]; tot += len(s["bullets"])
    cc = comp.get(c, {}); em = emap.get(c, {})
    print(f"[C1] {c:3s} owner line {s['line']:4d} bullets={len(s['bullets']):2d} ({s['bullets'][0]}-{s['bullets'][-1]}) challenge_line={s['challenge']} | compiled keys={sorted(cc)} status={cc.get('status')} src_ref={cc.get('source_reference','').split(':')[-1]} | evidence_map class={em.get('evidence_class')} automated_checks={em.get('automated_checks')} | generated view row={('`'+c+'`') in gen}")
print("[C1] alpha bullets in the owner source:", tot, "| bullets represented in the compiled form: 0 (no bullet/checklist key exists in any compiled entry)")
print("[C1] per-capability fields required by Contract v3 lines 53-73 present in the compiled form:",
      [k for k in ("severity", "applicability", "evidence_classes", "automated_checks", "independent_verification", "freshness_triggers", "health_scheduler_tiers", "qualification_challenges", "adoption_obligation") if any(k in comp[c] for c in ALPHA)])
print("[C1] alpha capabilities with >=1 automated check or evidence owner in the evidence map:", [c for c in ALPHA if emap[c].get("automated_checks")])
print("\nDONE")
