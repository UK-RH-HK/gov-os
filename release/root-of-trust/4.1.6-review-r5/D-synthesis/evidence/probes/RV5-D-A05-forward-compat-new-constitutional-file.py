#!/usr/bin/env python3
"""RV5-D-A05 — forward-compatibility constraint (HO-0001 §4): a new constitutional file set shipped in a release kernel
(review r5 synthesis D, AR-0014).

The 4.1.6 candidate will add a Capability Acceptance Contract (hash-bound normative Markdown plus compiled executable YAML).
Question 1 (classification): is a new file default-denied until a root-signed Trust Policy classifies it, and classifiable
with the existing vocabulary? Question 2 (release-scoped content): once classified `pinned_file`, whose selection makes its
content effective in a release — does RV5-D-A01's registration path apply to it unchanged?

Executed with the pack checker (unmodified) in registration mode:
  N1  kernel carries the two new files; inventory has no rule for them                → default deny expected (exit 2)
  N2  inventory classifies both as `pinned_file` (a root-signed TPS change)           → genuine kernel under a registration
      derived from itself: exit 0
  N3  attacker kernel: compiled YAML altered (acceptance threshold lowered); registration derived by CI from that kernel
      (`23` §12.5)                                                                     → E7 result
  N4  the same attacker kernel under a registration derived first-hand from the verified source's kernel → E7 result
  N5  registration-reductions over [4.1.7, attacker 4.1.8]                              → reductions reported?

Attribution: checker helpers follow review r5 B `RV5-B-A09-floor-class-kernels.py`.
Environment: REVIEW_REPO (export of cdb4e14), SCRATCH. Output: JSON on stdout.
"""
import copy, hashlib, json, os, re, shutil, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as Cc  # noqa: E402

FW = os.path.join(REPO, "framework")
REL_TOOLS = os.path.join(REPO, "release", "releases", "4.1.5", "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="rv5d-a05-", dir=os.environ["SCRATCH"])
MD = "contracts/CAPABILITY_ACCEPTANCE_CONTRACT.md"
YML = "contracts/CAPABILITY_ACCEPTANCE_CONTRACT.yaml"
MD_TEXT = "# Capability Acceptance Contract\n\nA capability is accepted only when every acceptance criterion passes with independent evidence.\n"
YML_GENUINE = {"contract_version": 1, "source_markdown_sha256": "sha256:" + hashlib.sha256(MD_TEXT.encode()).hexdigest(),
               "acceptance": {"min_independent_evidence": 2, "require_all_criteria": True}}
YML_ATTACKER = copy.deepcopy(YML_GENUINE)
YML_ATTACKER["acceptance"] = {"min_independent_evidence": 0, "require_all_criteria": False}


def kernel(name, yml):
    d = os.path.join(S, "k", name)
    shutil.copytree(FW, d)
    if not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    os.makedirs(os.path.join(d, "contracts"), exist_ok=True)
    open(os.path.join(d, MD), "w").write(MD_TEXT)
    Cc.ydump(os.path.join(d, YML), yml)
    return d


def fdigest(kdir, rel):
    return "sha256:" + hashlib.sha256(open(os.path.join(kdir, rel), "rb").read()).hexdigest()


def check(kdir, inv, regs=None, rid=None):
    r = Cc.run_check(kdir, inv, quiet=True, registrations=regs, release_id=rid)
    return {"exit": r["exit"], "violations": [str(v)[:180] for v in (r.get("violations") or [])[:3]],
            "unclassified": [str(x)[:160] for x in (r.get("unclassified_files") or [])[:3]]}


K417 = kernel("4.1.7", YML_GENUINE)
Kg = kernel("4.1.8-genuine", YML_GENUINE)
Kx = kernel("4.1.8-attacker", YML_ATTACKER)
INV3 = copy.deepcopy(INV)
for rel in (MD, YML):
    INV3["files"].append({"path": rel, "mode": "pinned_file", "digests": {rel: [fdigest(Kg, rel)]},
                          "rationale": "owner Capability Acceptance Contract shipped in the kernel (RV5-D-A05 fixture)"})

out = {"probe": "RV5-D-A05 forward compatibility: new constitutional file set in the kernel (AR-0014)"}
out["N1_unclassified_new_files"] = check(Kg, INV)
R417 = L.registration_record(INV3, K417, "4.1.7", 1700, "sha256:final-4.1.7")
Rg = L.registration_record(INV3, Kg, "4.1.8", 1800, "sha256:final-4.1.8")
Rx_ci = L.registration_record(INV3, Kx, "4.1.8", 1800, "sha256:final-4.1.8x")
out["N2_classified_genuine_under_own_registration"] = check(Kg, INV3, [R417, Rg], "4.1.8")
out["registration_units_for_new_files"] = sorted(u for u in Rg["units"] if "CAPABILITY_ACCEPTANCE_CONTRACT" in u)
out["N3_attacker_kernel_under_CI_derived_registration"] = check(Kx, INV3, [R417, Rx_ci], "4.1.8")
out["N4_attacker_kernel_under_first_hand_registration"] = check(Kx, INV3, [R417, Rg], "4.1.8")
rr = Cc.run_registration_reductions([R417, Rx_ci], quiet=True, inv=INV3)
out["N5_registration_reductions_417_to_attacker"] = {"exit": rr["exit"], "reductions": [{k: v for k, v in x.items() if k in ("subject", "kind")} for x in rr.get("reductions", [])]}
out["verdicts"] = {
    "N1_default_deny": out["N1_unclassified_new_files"]["exit"] == 2,
    "N2_classifiable_with_existing_vocabulary": out["N2_classified_genuine_under_own_registration"]["exit"] == 0,
    "N3_attacker_contract_eligible_under_CI_registration": out["N3_attacker_kernel_under_CI_derived_registration"]["exit"] == 0,
    "N4_attacker_contract_refused_under_first_hand_registration": out["N4_attacker_kernel_under_first_hand_registration"]["exit"] != 0,
    "N5_no_reduction_reported": out["N5_registration_reductions_417_to_attacker"]["exit"] == 0 and not out["N5_registration_reductions_417_to_attacker"]["reductions"],
}
txt = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(REPO, "<repo>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
