#!/usr/bin/env python3
"""ST5 subdirectory escape: revision-5 state and discovery added to reviewer C's subdir_escape.

Origin: copied from reviewer C's subdir_escape.py
  Origin path: release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence/subdir_escape.py
  Origin SHA-256: b6eb103979153be1166651c18215babd96cd97a57dc86ea61a51ff4a78297abd
Changes from origin:
  - Added r5 state and discovery to each row
  - Added positions governance and governance/trust/kernel (task specifies these)
  - Output file renamed to ST5-subdir-escape.json

Usage: ST5-subdir-escape.py <trees.json> <out-dir>
"""
import importlib.util, json, os, sys
sys.dont_write_bytecode = True

C_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
sys.path.insert(0, C_EV)
R5_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6/evidence/r5")
from c4lib import *  # noqa

# Import r5 functions
_r5_spec = importlib.util.spec_from_file_location("st5_r5", os.path.join(R5_EV, "ST5-installation-state-r5.py"))
_r5_mod = importlib.util.module_from_spec(_r5_spec)
_r5_spec.loader.exec_module(_r5_mod)
installation_state_r5 = _r5_mod.installation_state_r5
rot1_root_discovery = _r5_mod.rot1_root_discovery
_pristine_kernel_content_set = _r5_mod._pristine_kernel_content_set

PACK_MARK = MARK
_REF_KERNEL = None


def run(root, sub, argv, tag, S, query=True):
    global _REF_KERNEL
    env = child_env(S, tag)
    cwd = os.path.join(root, sub)
    os.makedirs(cwd, exist_ok=True)

    # r5 state and discovery BEFORE the invocation
    r5_before = installation_state_r5(root, pristine_kernel_ref=_REF_KERNEL)
    disc_before = rot1_root_discovery(cwd)

    before = snap(root, env["HOME"])
    r = gov(BINS["4.1.5"], argv, env, cwd, None)  # NO --root: legacy root discovery / current_dir
    after = snap(root, env["HOME"])
    cmp = compare(before, after)

    # r5 state AFTER the invocation
    r5_after = installation_state_r5(root, pristine_kernel_ref=_REF_KERNEL)

    out = {"argv": argv, "cwd_sub": sub, "ok": r.get("ok"), "code": code(r),
           "work_changed": cmp["work_changed"], "n_work_writes": cmp["work_n"],
           "nested_governance_created": kind(os.path.join(cwd, "governance/framework.lock")),
           "writes_inside_PPS_governance_trust": sorted([p for p in cmp["work_paths"] if p.startswith("governance/trust/")])[:12],
           "writes_inside_governance_overlay": sorted([p for p in cmp["work_paths"] if p.startswith("governance/overlay/")])[:6],
           "outer_rot1_state_after_r4": installation_state(root)["state"],
           "outer_occupation_intact": installation_state(root)["occupation_wrong"] == {},
           "r5_state_before": r5_before["state"],
           "r5_state_after": r5_after["state"],
           "r5_reasons_after": r5_after.get("reasons", []),
           "r5_nested_inside_governance": r5_after.get("nested_inside_governance", []),
           "r5_nested_legacy_projects": r5_after.get("nested_legacy_projects", []),
           "discovery_r5": disc_before}
    if query and out["nested_governance_created"] == "file":
        # nested install: index and query it for the RoT-1 project's restricted marker
        rb = gov(BINS["4.1.5"], ["rebuild-memory"], env, cwd, None)
        q = gov(BINS["4.1.5"], ["memory", "query", PACK_MARK], env, cwd, None)
        hits = sorted({h.get("path") for h in (result(q).get("hits") or []) if isinstance(h, dict)})
        out["nested_rebuild_ok"] = rb.get("ok")
        out["nested_restricted_retrievable"] = [h for h in hits if h and "restricted" in h]
    return out


def main():
    global _REF_KERNEL
    T = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    S = T["scratch"]
    src = T["trees"]["R4"]
    _REF_KERNEL = _pristine_kernel_content_set(src)
    home = os.path.join(S, "homes", "subesc5")
    os.makedirs(home, exist_ok=True)
    res = {"binary_sha256": sha(open(BINS["4.1.5"], "rb").read()), "note": "intact revision-4 R4 layout; legacy 4.1.5; no --root; r5 state added"}

    # control: OUTER legacy binary with the RoT-1-classified overlay refuses to retrieve restricted
    ctl = os.path.join(S, "subesc5", "control"); os.makedirs(os.path.dirname(ctl), exist_ok=True)
    git(os.path.dirname(ctl), "clone", "-q", src, ctl, home=home)
    envc = child_env(S, "subesc5-control")
    res["control_outer_intact"] = {"state_r4": installation_state(ctl)["state"],
                                   "state_r5": installation_state_r5(ctl, pristine_kernel_ref=_REF_KERNEL)["state"],
                                   "outer_legacy": legacy_harm(BINS["4.1.5"], envc, ctl, ctl)}

    # (1) EXPOSURE via product/, spec/, governance, governance/trust/kernel (new positions)
    ex = {}
    for sub in ("product", "spec", "governance", "governance/trust/kernel"):
        d = os.path.join(S, "subesc5", "exp_" + sub.replace("/", "_")); os.makedirs(os.path.dirname(d), exist_ok=True)
        git(os.path.dirname(d), "clone", "-q", src, d, home=home)
        ex[sub] = run(d, sub, ["init", "--skip-index"], "exp5-" + sub.replace("/", "_"), S)
    res["1_exposure_subdir_init"] = ex

    # (2) PPS WRITE from inside the governance tree (expanded positions)
    pps = {}
    for sub in ("governance", "governance/overlay", "governance/views", "governance/trust",
                "governance/trust/kernel", "governance/trust/state", "governance/framework.lock"):
        for cmd, argv in (("init", ["init", "--skip-index"]), ("adopt_baseline", ["adopt", "baseline"]), ("migrate_baseline", ["migrate", "baseline"])):
            d = os.path.join(S, "subesc5", "pps_" + sub.replace("/", "_") + "_" + cmd); os.makedirs(os.path.dirname(d), exist_ok=True)
            git(os.path.dirname(d), "clone", "-q", src, d, home=home)
            pps[f"{sub}::{cmd}"] = run(d, sub, argv, "pps5-" + sub.replace("/", "_") + "-" + cmd, S, query=False)
    res["2_pps_write_from_inside_governance"] = pps

    with open(os.path.join(out_dir, "ST5-subdir-escape.json"), "w") as f:
        f.write(scrub(json.dumps(res, indent=1, sort_keys=True, default=str), S))
    print(json.dumps({"exposure_subs": list(ex.keys()), "pps_subs": list(pps.keys()),
                       "exposure_r5_states": {k: v["r5_state_after"] for k, v in ex.items()},
                       "pps_r5_states": {k: v["r5_state_after"] for k, v in pps.items()}}, indent=1))


if __name__ == "__main__":
    main()
