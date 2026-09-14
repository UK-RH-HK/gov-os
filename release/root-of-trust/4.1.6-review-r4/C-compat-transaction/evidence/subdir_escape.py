#!/usr/bin/env python3
"""AR-0007 held-out attack RV4-C-A01: subdirectory escape of the occupation defence.

The occupation layout (`26` §2) occupies named entries at the RoT-1 PROJECT ROOT. But legacy `init`, `adopt baseline`
and `migrate baseline` root at `current_dir()` (cli/src/main.rs: `cli.root.clone().unwrap_or(std::env::current_dir()?)`),
not at `find_root()`, and do not call `require_installed()`. Run from a SUBDIRECTORY of an intact RoT-1 project with no
`--root`, they install a fresh legacy governance project rooted at that subdirectory — a path the occupation does not
cover. Two consequences are measured, on the INTACT revision-4 layout:

  (1) EXPOSURE. `gov init` in a content subdirectory (e.g. `product/`) creates a nested legacy install whose fresh overlay
      has none of the RoT-1 project's classifications. It indexes and retrieves the project's restricted material that the
      RoT-1 overlay classifies `restricted` (and that the OUTER legacy binary, carrying that classification, refuses).

  (2) PPS WRITE. `gov init` / `adopt baseline` / `migrate baseline` run from inside the RoT-1 governance tree
      (`governance/overlay`, `governance/views`, `governance/trust`, `governance/trust/state`, `governance/framework.lock`)
      write a nested `governance/` INSIDE the Protected Path Set (`18` §8: `governance/trust/**`), while the RoT-1
      installation-state machine (`18` §9) still reports COMPLETE.

Executed with the real 4.1.5 binary on the R4 tree. Scratch only; GOV_* stripped from children.
Usage: subdir_escape.py <trees.json> <out-dir>
"""
import json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import *  # noqa

PACK_MARK = MARK


def run(root, sub, argv, tag, S, query=True):
    env = child_env(S, tag)
    cwd = os.path.join(root, sub)
    os.makedirs(cwd, exist_ok=True)
    before = snap(root, env["HOME"])
    r = gov(BINS["4.1.5"], argv, env, cwd, None)  # NO --root: legacy root discovery / current_dir
    after = snap(root, env["HOME"])
    cmp = compare(before, after)
    out = {"argv": argv, "cwd_sub": sub, "ok": r.get("ok"), "code": code(r),
           "work_changed": cmp["work_changed"], "n_work_writes": cmp["work_n"],
           "nested_governance_created": kind(os.path.join(cwd, "governance/framework.lock")),
           "writes_inside_PPS_governance_trust": sorted([p for p in cmp["work_paths"] if p.startswith("governance/trust/")])[:12],
           "writes_inside_governance_overlay": sorted([p for p in cmp["work_paths"] if p.startswith("governance/overlay/")])[:6],
           "outer_rot1_state_after": installation_state(root)["state"],
           "outer_occupation_intact": installation_state(root)["occupation_wrong"] == {}}
    if query and out["nested_governance_created"] == "file":
        # nested install: index and query it for the RoT-1 project's restricted marker
        rb = gov(BINS["4.1.5"], ["rebuild-memory"], env, cwd, None)
        q = gov(BINS["4.1.5"], ["memory", "query", PACK_MARK], env, cwd, None)
        hits = sorted({h.get("path") for h in (result(q).get("hits") or []) if isinstance(h, dict)})
        out["nested_rebuild_ok"] = rb.get("ok")
        out["nested_restricted_retrievable"] = [h for h in hits if h and "restricted" in h]
    return out


def main():
    T = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    S = T["scratch"]
    src = T["trees"]["R4"]
    home = os.path.join(S, "homes", "subesc")
    os.makedirs(home, exist_ok=True)
    res = {"binary_sha256": sha(open(BINS["4.1.5"], "rb").read()), "note": "intact revision-4 R4 layout; legacy 4.1.5; no --root"}

    # control: OUTER legacy binary with the RoT-1-classified overlay refuses to retrieve restricted (classification works)
    ctl = os.path.join(S, "subesc", "control"); os.makedirs(os.path.dirname(ctl), exist_ok=True)
    git(os.path.dirname(ctl), "clone", "-q", src, ctl, home=home)
    envc = child_env(S, "subesc-control")
    res["control_outer_intact"] = {"state": installation_state(ctl)["state"], "outer_legacy": legacy_harm(BINS["4.1.5"], envc, ctl, ctl)}

    # (1) EXPOSURE via product/ (and spec/)
    ex = {}
    for sub in ("product", "spec"):
        d = os.path.join(S, "subesc", "exp_" + sub); git(os.path.dirname(d), "clone", "-q", src, d, home=home)
        ex[sub] = run(d, sub, ["init", "--skip-index"], "exp-" + sub, S)
    res["1_exposure_subdir_init"] = ex

    # (2) PPS WRITE from inside the governance tree
    pps = {}
    for sub in ("governance/overlay", "governance/views", "governance/trust", "governance/trust/state", "governance/framework.lock"):
        for cmd, argv in (("init", ["init", "--skip-index"]), ("adopt_baseline", ["adopt", "baseline"]), ("migrate_baseline", ["migrate", "baseline"])):
            d = os.path.join(S, "subesc", "pps_" + sub.replace("/", "_") + "_" + cmd); git(os.path.dirname(d), "clone", "-q", src, d, home=home)
            pps[f"{sub}::{cmd}"] = run(d, sub, argv, "pps-" + sub.replace("/", "_") + "-" + cmd, S, query=False)
    res["2_pps_write_from_inside_governance"] = pps

    with open(os.path.join(out_dir, "subdir_escape.json"), "w") as f:
        f.write(scrub(json.dumps(res, indent=1, sort_keys=True, default=str), S))
    summ = {"control_outer_refuses_restricted": res["control_outer_intact"]["outer_legacy"]["restricted_hits"] == [] and res["control_outer_intact"]["outer_legacy"]["verified"] in (None, False),
            "exposure": {k: {"nested_install": v["nested_governance_created"], "restricted_retrievable": v.get("nested_restricted_retrievable"), "outer_state": v["outer_rot1_state_after"]} for k, v in ex.items()},
            "pps_writes": {k: {"n_writes_in_PPS_trust": len(v["writes_inside_PPS_governance_trust"]), "sample": v["writes_inside_PPS_governance_trust"][:3], "outer_state_after": v["outer_rot1_state_after"], "outer_occ_intact": v["outer_occupation_intact"]} for k, v in pps.items()}}
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
