"""Reconcile the derived contract views against the owner source for family beta (frozen contract §1: the owner
source defines the universe; a derived view that omits or distorts anything in scope is itself a finding).
Runs `gov contract verify` (the product's own binding check) and compares, per C/D/R capability, the owner-source
checklist bullets with what the compiled YAML, the evidence map and the generated view carry."""
import json, os, re, subprocess, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
env = dict(os.environ, GOV_CANONICAL_ROOT=str(WT))
p = subprocess.run([str(GOV), "--json", "--root", str(WT), "contract", "verify"], capture_output=True, text=True, env=env, cwd=WT)
log("$ gov --json --root <candidate> contract verify ->", p.stdout.strip()[:1500])
src = (WT / "Governance_OS_Capability_Acceptance_Contract_v3.md").read_text().splitlines()
own, cur = {}, None
for i, l in enumerate(src, 1):
    m = re.match(r"^## ([CDR]\d+)\. (.*)$", l)
    if m:
        cur = m.group(1); own[cur] = []; continue
    if l.startswith("#"):
        cur = None
    if cur and re.match(r"^- \[ \] ", l):
        own[cur].append((i, l[6:]))
comp = {c["id"]: c for c in yaml.safe_load((WT / "framework/contracts/governance-capability-acceptance.yaml").read_text())["capabilities"]}
emap = {c["capability"]: c for c in yaml.safe_load((WT / "tests/governance/capability-evidence-map.yaml").read_text())["capabilities"]}
gen = (WT / "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md").read_text()
total = 0
for cid, bl in own.items():
    total += len(bl)
    c = comp.get(cid, {})
    carried = [k for k in c.keys()]
    in_comp = sum(1 for _, b in bl if b in json.dumps(c))
    in_gen = sum(1 for _, b in bl if b in gen)
    e = emap.get(cid, {})
    log(f"{cid:<4} owner bullets={len(bl):>2} | compiled fields={carried} bullets carried={in_comp} | evidence map: class={e.get('evidence_class')} "
        f"checks={len(e.get('automated_checks', []))} | generated view bullets={in_gen}")
log("owner-source bullets in scope:", total)
check("DERIVED-compiled", all(sum(1 for _, b in bl if b in json.dumps(comp.get(cid, {}))) == len(bl) for cid, bl in own.items()),
      "the compiled executable form carries every in-scope checklist bullet")
check("DERIVED-evidence-map", all(emap.get(cid, {}).get("automated_checks") for cid in own), "the evidence map names at least one automated check per in-scope capability")
summary()
