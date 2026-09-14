#!/usr/bin/env python3
"""RV7-D-A07 (AR-0022, synthesis reviewer D, held-out) — forward compatibility (HO-0001 §4) for the shapes the capability-contract and
Gate W phases are most likely to take, beyond the new-file cases review r5/r6 already ran (RV5-D-A05, RV6-D-A03, re-run by B):

  K1  a new constitutional policy file `policies/ARTIFACT_FLOW_POLICY.yaml` and a normative Markdown source
      `constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md` with its compiled `policies/CAPABILITY_ACCEPTANCE_CONTRACT.yaml`;
  K2  a new authority-bearing key inside an existing subtree the inventory classifies by WILDCARD as `informational`
      (`ROLES.authority_levels.*.*`): `L5.artifact_consumption: unreceipted_allowed` and a new level `L6`;
  K3  a new security-looking member key inside an existing keyed collection member (`ROLES.roles[id=orchestrator].consume_unreceipted`);
  K4  the producer tool `csi_derive.py` run over K1 and K2: which class does the drafted inventory give the new keys, and does the
      checker then pass (the default-deny boundary moves to the root-ceremony review, residual CS-1)?
Checker and deriver are the pack's, unmodified (`constitutional-surface/`). Kernels are scratch copies of `framework/` at d07d200.
Usage: RV7-D-A07-...py <export-root> <scratch>   (JSON on stdout)
"""
import json, os, re, shutil, subprocess, sys
import yaml
sys.dont_write_bytecode = True
X = os.path.abspath(sys.argv[1])
S = os.path.abspath(sys.argv[2])
CSI = os.path.join(X, "release/root-of-trust/4.1.6/constitutional-surface")
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "PYTHONDONTWRITEBYTECODE": "1"}
os.makedirs(ENV["HOME"], exist_ok=True)


def kernel(name):
    """A repository-shaped scratch copy: <name>/framework (copied) beside the export's tools/ and migrations/ (the deriver reads
    "../tools/registry/TOOLS.yaml" relative to the kernel)."""
    base = os.path.join(S, name)
    os.makedirs(base)
    for sib in ("tools", "migrations"):
        if os.path.exists(os.path.join(X, sib)):
            os.symlink(os.path.join(X, sib), os.path.join(base, sib))
    k = os.path.join(base, "framework")
    shutil.copytree(os.path.join(X, "framework"), k)
    return k


def check(k, inv=None):
    cmd = ["python3", "-B", os.path.join(CSI, "csi_check.py"), "check", k, "--json"] + (["--inventory", inv] if inv else [])
    p = subprocess.run(cmd, capture_output=True, text=True, env=ENV, cwd=CSI)
    try:
        j = json.loads(p.stdout)
    except Exception:
        j = {"raw": p.stdout[-800:]}
    probs = j.get("problems") or j.get("coverage") or j.get("failures") or j
    return {"exit": p.returncode, "detail": json.dumps(probs, sort_keys=True)[:1500]}


def derive(k):
    p = subprocess.run(["python3", "-B", os.path.join(CSI, "csi_derive.py"), k], capture_output=True, text=True, env=ENV, cwd=CSI)
    path = k + ".inventory.yaml"
    open(path, "w").write(p.stdout)
    return p.returncode, path, p.stderr[-400:]


def classes_for(inv_path, pats):
    raw = open(inv_path).read()
    inv = None
    for loader in (json.loads, yaml.safe_load):
        try:
            inv = loader(raw)
            if isinstance(inv, dict):
                break
        except Exception:
            inv = None
    if not isinstance(inv, dict):
        return {"error": "derived inventory unreadable", "head": raw[:300]}
    out = {}
    for f in inv.get("files", []):
        for l in f.get("leaves", []) or []:
            if any(re.search(p, l.get("key", "")) for p in pats):
                out[l["key"]] = l.get("class")
        if any(re.search(p, f.get("path", "") or f.get("glob", "")) for p in pats):
            out["file:" + (f.get("path") or f.get("glob"))] = f.get("mode")
    return out


res = {}
# K1 new files
k1 = kernel("K1")
open(os.path.join(k1, "policies/ARTIFACT_FLOW_POLICY.yaml"), "w").write(
    "policy: ARTIFACT_FLOW_POLICY\nversion: 1.0.0\nconsumption_receipts_required: true\nunreceipted_input_classes_allowed: []\nlineage_retention_days: 365\n")
open(os.path.join(k1, "constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md"), "w").write("# Capability Acceptance Contract\n\nNormative source (owner-supplied).\n")
open(os.path.join(k1, "policies/CAPABILITY_ACCEPTANCE_CONTRACT.yaml"), "w").write("policy: CAPABILITY_ACCEPTANCE_CONTRACT\nversion: 1.0.0\nsource_digest: sha256:" + "0" * 64 + "\nacceptance:\n  - {id: CAP-1, requires_evidence: true}\n")
res["K1_new_files_committed_inventory"] = check(k1)
# K2 new key under the informational wildcard subtree
k2 = kernel("K2")
rp = os.path.join(k2, "roles/ROLES.yaml")
t = open(rp).read()
t = t.replace("  L5: {name: human/product owner, mutation: final authority at defined gates}",
              "  L5: {name: human/product owner, mutation: final authority at defined gates, artifact_consumption: unreceipted_allowed}\n  L6: {name: automation super-user, mutation: any state without gates}")
assert "L6:" in t
open(rp, "w").write(t)
res["K2_authority_levels_wildcard_new_keys_committed_inventory"] = check(k2)
# K3 new key inside a keyed collection member
k3 = kernel("K3")
rp = os.path.join(k3, "roles/ROLES.yaml")
t = open(rp).read()
old = "  - {id: orchestrator, name: CTO / Senior Full-Stack Orchestrator, level: L4, minimum_tier: T3, default_reasoning: high}"
assert old in t
open(rp, "w").write(t.replace(old, old[:-1] + ", consume_unreceipted: true}"))
res["K3_keyed_member_new_key_committed_inventory"] = check(k3)
# K0 control
res["K0_control_unmodified_kernel"] = check(kernel("K0"))
# K4 producer tool
rc1, inv1, err1 = derive(k1)
rc2, inv2, err2 = derive(k2)
res["K4_derive_K1"] = {"derive_exit": rc1, "stderr": err1, "classes": classes_for(inv1, [r"ARTIFACT_FLOW", r"CAPABILITY_ACCEPTANCE"]), "check_with_derived_inventory": check(k1, inv1)}
res["K4_derive_K2"] = {"derive_exit": rc2, "stderr": err2, "classes": classes_for(inv2, [r"authority_levels"]), "check_with_derived_inventory": check(k2, inv2)}
consumers = [l for l in open(os.path.join(X, "release/root-of-trust/4.1.6/23-CONSTITUTIONAL-SURFACE.md")).read().splitlines() if re.search(r"informational", l)][:8]
out = {"probe": "RV7-D-A07 forward compatibility: capability contract and artifact-flow shapes (AR-0022)", "results": res, "text_informational_class": consumers,
       "verdicts": {"K0_control_passes": res["K0_control_unmodified_kernel"]["exit"] == 0,
                    "K1_new_files_default_deny": res["K1_new_files_committed_inventory"]["exit"] != 0,
                    "K2_new_authority_keys_under_informational_wildcard_default_deny": res["K2_authority_levels_wildcard_new_keys_committed_inventory"]["exit"] != 0,
                    "K3_new_key_in_keyed_member_default_deny": res["K3_keyed_member_new_key_committed_inventory"]["exit"] != 0}}
print(json.dumps(out, indent=1, sort_keys=True).replace(S, "<s>").replace(X, "<export>"))
