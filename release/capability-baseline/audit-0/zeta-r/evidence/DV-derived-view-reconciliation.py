"""Derived-view reconciliation for Gate W (frozen gate contract section 1: the owner source defines the universe; the
compiled YAML, evidence map and generated view are derived views to be reconciled against it).
Runs `gov contract verify` on the candidate repository, then compares, for W1-W12, what the owner source says with what
each derived view carries: checklist bullets, the W10 hard-invariant text, the Gate W advanced-qualification challenge,
evidence classes / automated checks.
"""
import sys, os, json, re, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

src_path = os.path.join(WT, "Governance_OS_Capability_Acceptance_Contract_v3.md")
src = open(src_path).read().splitlines()
log(f"owner source sha256={hashlib.sha256(open(src_path, 'rb').read()).hexdigest()}")
g = Gov(WT, session="S-dv")
cv = g.run("contract", "verify", "--root", WT, limit=3000) if False else g.run("contract", "verify", limit=3000)
obs("DV-contract-verify-binds", cv.get("ok") and "CONTRACT_SOURCE_BOUND" in json.dumps(cv.get("result")), f"gov contract verify -> ok={cv.get('ok')}")

# owner-source W structure
caps, cur = {}, None
for i, line in enumerate(src, 1):
    m = re.match(r"^## (W\d+)\. (.*)$", line)
    if m:
        cur = m.group(1); caps[cur] = {"title": m.group(2), "line": i, "bullets": []}
        continue
    if line.startswith("# ") and cur:
        cur = None
    if cur and line.strip().startswith("- [ ]"):
        caps[cur]["bullets"].append((i, line.strip()[6:]))
hard_inv = next(i for i, l in enumerate(src, 1) if l.startswith("> Mandatory task inputs are resolved"))
challenge = next(i for i, l in enumerate(src, 1) if l.startswith("**Advanced qualification challenge:** intentionally omit current specs"))
log("owner source Gate W: " + json.dumps({k: {"line": v["line"], "bullets": len(v["bullets"])} for k, v in caps.items()}))
log(f"W10 hard invariant at line {hard_inv}; Gate W advanced-qualification challenge at line {challenge}")
total_bullets = sum(len(v["bullets"]) for v in caps.values())

comp = yaml.safe_load(open(os.path.join(WT, "framework/contracts/governance-capability-acceptance.yaml")))
cw = {c["id"]: c for c in comp["capabilities"] if c["id"].startswith("W")}
log("compiled W entries: " + json.dumps(cw, indent=1))
obs("DV-compiled-has-all-W-ids", set(cw) == set(caps), f"compiled ids {sorted(cw)} vs source {sorted(caps)}")
obs("DV-compiled-source-lines-match", all(cw[k]["source_reference"].endswith(f":{caps[k]['line']}") for k in caps), "compiled source_reference lines equal owner-source heading lines")
carried = sum(1 for k in caps for _, b in caps[k]["bullets"] if b[:40] in json.dumps(cw.get(k, {})))
obs("DV-compiled-carries-W-bullets", carried == total_bullets, f"owner-source W checklist bullets carried by the compiled form: {carried}/{total_bullets}")
obs("DV-compiled-carries-W10-hard-invariant", "Mandatory task inputs are resolved" in json.dumps(cw), "W10 hard-invariant text present in the compiled form")
obs("DV-compiled-carries-W-advanced-challenge", "omit current specs" in json.dumps(comp), "Gate W advanced-qualification challenge present in the compiled form")
req_fields = ["severity", "applicability", "evidence_class", "automated_checks", "freshness_triggers", "health_scheduler_tiers", "qualification_challenge_ids", "adoption_obligation"]
present = {f: any(f in c for c in cw.values()) for f in req_fields}
obs("DV-compiled-carries-required-contract-fields(lines 53-73)", all(present.values()), f"required per-capability fields present in compiled W entries: {present}")

em = yaml.safe_load(open(os.path.join(WT, "tests/governance/capability-evidence-map.yaml")))
ew = {c["capability"]: c for c in em["capabilities"] if c["capability"].startswith("W")}
log("evidence-map W rows: " + json.dumps(ew, indent=1))
obs("DV-evidence-map-W-has-evidence-owner", all(c.get("automated_checks") for c in ew.values()), f"W rows with >=1 automated check: {[k for k, c in ew.items() if c.get('automated_checks')]}; evidence_class values: {sorted(set(c.get('evidence_class') for c in ew.values()))}")
gen = open(os.path.join(WT, "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md")).read()
wrows = [l for l in gen.splitlines() if re.match(r"^\| `W\d+` ", l)]
log("generated view W rows: " + json.dumps(wrows, indent=1))
obs("DV-generated-view-lists-all-W", len(wrows) == len(caps), f"{len(wrows)} W rows in the generated view")
summary()
