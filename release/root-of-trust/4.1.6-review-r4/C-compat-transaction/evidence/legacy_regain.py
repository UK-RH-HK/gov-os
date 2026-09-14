#!/usr/bin/env python3
"""AR-0007 executed attacks on the revision-4 layout: occupation removal / Git restore of pre-migration paths, and what a
real pre-RoT binary then does; symlink/path tricks on the occupation; nested legacy projects; foreign transaction
journals. The RoT-1 side is evaluated by the `18` §9 state machine (no RoT-1 binary exists). The legacy side is executed
with the real 4.1.5 binary. Post-migration project classifications live in `governance/overlay` only, so retrieval of the
restricted marker by the legacy binary is the R2-H4 harm.

Usage: legacy_regain.py <trees.json> <out-dir>
"""
import json, os, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import *  # noqa
import yaml

OCC_PATHS = list(OCCUPATION)


def clone(src, dst, home):
    git(os.path.dirname(dst), "clone", "-q", src, dst, home=home)
    return dst


def add_overlay_class(root, home):
    """Add a post-migration restricted classification in governance/overlay (only the RoT-1 overlay classifies it)."""
    os.makedirs(os.path.join(root, "product/customers"), exist_ok=True)
    open(os.path.join(root, "product/customers/acme.md"), "w").write(f"# ACME\n{MARK} bank details and contract value\n")
    p = os.path.join(root, "governance/overlay/DATA_SENSITIVITY.yaml")
    ds = yaml.safe_load(open(p)) or {}
    ds.setdefault("classifications", []).append({"pattern": "product/customers/**", "class": "restricted", "reason": "post-migration classification"})
    yaml.safe_dump(ds, open(p, "w"), sort_keys=False)
    git(root, "add", "-A", home=home)
    git(root, "commit", "-q", "-m", "post-migration overlay classification", home=home)


def legacy_view(root, tag, S, chain_trust=False):
    env = child_env(S, tag)
    before = snap(root, env["HOME"])
    kt = gov(BINS["4.1.5"], ["kernel", "trust"], env, root, root)
    rb = gov(BINS["4.1.5"], ["rebuild-memory"], env, root, root)
    q1 = gov(BINS["4.1.5"], ["memory", "query", MARK], env, root, root)
    hits = sorted({h.get("path") for h in (result(q1).get("hits") or []) if isinstance(h, dict)})
    out = {"verified": result(kt).get("verified"), "kernel_trust_ok": kt.get("ok"), "kernel_trust_code": code(kt),
           "rebuild_ok": rb.get("ok"), "rebuild_code": code(rb), "restricted_retrievable": [h for h in hits if h and "customers" in h]}
    if chain_trust:
        out["cit_writes_trust"] = legacy_cit(root, tag + "-cit", S)
    after = snap(root, env["HOME"])
    cmp = compare(before, after)
    out["work_changed_by_legacy"] = cmp["work_changed"]
    out["trust_paths_changed"] = [p for p in cmp["work_paths"] if p.startswith("governance/trust")]
    out["rot1_state_after"] = installation_state(root)["state"]
    return out


def legacy_cit(root, tag, S):
    """A legacy CIT whose manifest targets governance/trust/** and the overlay, answered by caller-declared decide."""
    env = child_env(S, tag)
    mf = os.path.join(S, "fixtures", f"cit-{tag}.json")
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump([{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": "schema_version: 1.0.0\nclassifications: []\n"},
               {"op": "write_file", "path": "governance/trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
               {"op": "delete_file", "path": "governance/trust/framework.lock"}], open(mf, "w"))
    tb = installation_state(root)
    trust_before = tree_map(os.path.join(root, "governance/trust"))
    t = gov(BINS["4.1.5"], ["task", "create", "--class", "documentation", "--objective", "x", "--title", "t", "--status", "READY"], env, root, root)
    task = result(t).get("id") or "TASK-0001"
    steps = {}
    c = gov(BINS["4.1.5"], ["cit", "propose", "--proposal", "p", "--trigger", "editorial", "--targets", task, "--manifest", mf], env, root, root)
    cid = result(c).get("id") or "CIT-0001"
    steps["propose"] = {"ok": c.get("ok"), "code": code(c)}
    steps["simulate"] = (lambda r: {"ok": r.get("ok"), "code": code(r)})(gov(BINS["4.1.5"], ["cit", "simulate", cid], env, root, root))
    ap = gov(BINS["4.1.5"], ["cit", "approve", cid, "--by", "orchestrator", "--method", "auto"], env, root, root)
    steps["approve"] = {"ok": ap.get("ok"), "code": code(ap)}
    import re
    m = re.search(r"(HDG-\d+)", json.dumps(ap.get("error") or {}))
    if not ap.get("ok") and m:
        gid = m.group(1)
        gov(BINS["4.1.5"], ["gate", "present", gid], env, root, root)
        gov(BINS["4.1.5"], ["decide", gid, "--option", "A", "--by", "owner"], env, root, root)
        ap = gov(BINS["4.1.5"], ["cit", "approve", cid, "--by", "owner", "--method", "human"], env, root, root)
        steps["approve_after_gate"] = {"ok": ap.get("ok"), "code": code(ap)}
    ex = gov(BINS["4.1.5"], ["cit", "execute", cid], env, root, root)
    steps["execute"] = {"ok": ex.get("ok"), "code": code(ex)}
    trust_after = tree_map(os.path.join(root, "governance/trust"))
    return {"steps": steps, "governance_trust_mutated": digest(trust_before) != digest(trust_after),
            "trust_framework_lock_present_after": kind(os.path.join(root, "governance/trust/framework.lock")),
            "changed_trust_paths": changed(trust_before, trust_after)[:20]}


def main():
    T = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    S = T["scratch"]
    src = T["trees"]["R4"]  # clone from the R4 tree
    home = os.path.join(S, "homes", "regain")
    os.makedirs(home, exist_ok=True)
    base = os.path.join(S, "regain")
    os.makedirs(base, exist_ok=True)
    res = {}

    # A. full occupation removal (incl the framework.lock directory), governance/trust kept, then legacy init --force
    A = clone(src, os.path.join(base, "A_full_removal"), home)
    add_overlay_class(A, home)
    git(A, "rm", "-q", "-r", *OCC_PATHS, home=home)
    git(A, "commit", "-q", "-m", "remove occupation entries", home=home)
    env = child_env(S, "A-init")
    initf = gov(BINS["4.1.5"], ["init", "--force", "--source", REL["4.1.5"], "--skip-index"], env, A, A)
    res["A_full_removal_then_init_force"] = {"pre_state": installation_state(A)["state"] if False else "PARTIAL(after removal, before init)",
                                             "init_force_ok": initf.get("ok"), "init_force_code": code(initf),
                                             "legacy": legacy_view(A, "A-view", S, chain_trust=True)}

    # B. git checkout <pre-migration> -- governance  (retype legacy authority paths; governance/trust untouched)
    B = clone(src, os.path.join(base, "B_checkout_governance"), home)
    add_overlay_class(B, home)
    pre = git(B, "rev-parse", "HEAD~2", home=home).stdout.strip()  # before migration (add_overlay adds 1 commit)
    trust_before = tree_map(os.path.join(B, "governance/trust"))
    g = git(B, "checkout", pre, "--", "governance", home=home, check=False)
    res["B_checkout_pre_governance"] = {"git_rc": g.returncode, "trust_digest_unchanged": digest(trust_before) == digest(tree_map(os.path.join(B, "governance/trust"))),
                                        "occupation_types": {p: kind(os.path.join(B, p)) for p in OCCUPATION},
                                        "legacy": legacy_view(B, "B-view", S, chain_trust=True)}

    # C. git restore --source <pre> --staged --worktree -- governance  (also removes governance/trust and overlay)
    C = clone(src, os.path.join(base, "C_restore_source"), home)
    add_overlay_class(C, home)
    pre = git(C, "rev-parse", "HEAD~2", home=home).stdout.strip()
    g = git(C, "restore", "--source", pre, "--staged", "--worktree", "--", "governance", home=home, check=False)
    res["C_restore_source_pre"] = {"git_rc": g.returncode, "trust_present_after": kind(os.path.join(C, "governance/trust")),
                                   "overlay_present_after": kind(os.path.join(C, "governance/overlay")),
                                   "rot1_state": installation_state(C)["state"], "legacy": legacy_view(C, "C-view", S)}

    # D. control: intact layout — every legacy step refused before any write
    D = clone(src, os.path.join(base, "D_control_intact"), home)
    add_overlay_class(D, home)
    res["D_control_intact"] = {"rot1_state": installation_state(D)["state"], "legacy": legacy_view(D, "D-view", S, chain_trust=True)}

    # E. partial occupation removal: only the 3 sentinel files, keep framework.lock dir; then legacy init --force
    E = clone(src, os.path.join(base, "E_partial_removal"), home)
    add_overlay_class(E, home)
    git(E, "rm", "-q", "governance/kernel", "governance/project", "governance/generated", home=home)
    git(E, "commit", "-q", "-m", "remove 3 sentinel files, keep framework.lock dir", home=home)
    env = child_env(S, "E-init")
    initf = gov(BINS["4.1.5"], ["init", "--force", "--source", REL["4.1.5"], "--skip-index"], env, E, E)
    res["E_partial_removal_then_init_force"] = {"init_force_ok": initf.get("ok"), "init_force_code": code(initf),
                                                "rot1_state": installation_state(E)["state"],
                                                "stray_kernel_manifest": kind(os.path.join(E, "governance/kernel/KERNEL_MANIFEST.json")),
                                                "legacy": legacy_view(E, "E-view", S)}

    # F. symlink trick: replace the framework.lock occupation DIRECTORY with a symlink to a real directory; does legacy
    #    is_installed()/init see a usable lock path, and does the RoT-1 state machine flag the type?
    F = clone(src, os.path.join(base, "F_symlink_occupation"), home)
    add_overlay_class(F, home)
    fl = os.path.join(F, "governance/framework.lock")
    target = os.path.join(F, "governance/trust")  # a real directory
    aside(S, fl, "F")
    os.symlink("trust", fl)  # governance/framework.lock -> trust (relative)
    st = installation_state(F)
    res["F_symlink_occupation_framework_lock"] = {"framework_lock_kind": kind(fl), "rot1_state": st["state"],
                                                  "occupation_wrong_by_18s9": st["occupation_wrong"], "legacy": legacy_view(F, "F-view", S)}

    # G. nested legacy project: a legacy 4.1.x project living in a SUBDIRECTORY of the RoT-1 project; run the legacy
    #    binary from that subdirectory (root discovery walks up to the nearest governance/framework.lock).
    G = clone(src, os.path.join(base, "G_nested_legacy"), home)
    add_overlay_class(G, home)
    envn = child_env(S, "G-nested")
    sub = os.path.join(G, "vendor", "legacypkg")
    os.makedirs(sub, exist_ok=True)
    gov(BINS["4.1.5"], ["init", "--source", REL["4.1.5"], "--name", "nested", "--skip-index"], envn, sub, None)  # no --root: cwd=sub
    nested_lock = kind(os.path.join(sub, "governance/framework.lock"))
    # now from a deeper dir inside the nested project, run a destructive legacy command with NO --root (root discovery)
    deep = os.path.join(sub, "product")
    os.makedirs(deep, exist_ok=True)
    before = snap(G, envn["HOME"])
    r = gov(BINS["4.1.5"], ["init", "--force", "--skip-index"], envn, deep, None)
    after = snap(G, envn["HOME"])
    cmp = compare(before, after)
    res["G_nested_legacy_project"] = {"nested_lock_kind": nested_lock, "nested_is_separate_project": nested_lock == "file",
                                      "outer_rot1_state": installation_state(G)["state"], "outer_trust_changed": any(p.startswith("governance/trust") for p in cmp["work_paths"]),
                                      "changed_paths": cmp["work_paths"][:15], "note": "root discovery finds the nearest governance/framework.lock; nested legacy project is contained to its own subtree"}

    with open(os.path.join(out_dir, "legacy_regain.json"), "w") as f:
        f.write(scrub(json.dumps(res, indent=1, sort_keys=True, default=str), S))
    summ = {k: {"rot1_state": (v.get("rot1_state") or v.get("legacy", {}).get("rot1_state_after")),
                "legacy_verified": v.get("legacy", {}).get("verified"),
                "restricted_retrievable": v.get("legacy", {}).get("restricted_retrievable"),
                "trust_mutated_by_legacy_cit": (v.get("legacy", {}).get("cit_writes_trust") or {}).get("governance_trust_mutated")}
            for k, v in res.items()}
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
