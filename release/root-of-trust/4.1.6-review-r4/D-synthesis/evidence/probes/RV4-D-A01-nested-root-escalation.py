#!/usr/bin/env python3
"""RV4-D-A01 (review r4 synthesis D, AR-0008) — does the subdirectory escape (RV4-C-H1) reach a RoT-1 trust or enforcement
fact, or only litter?

Reviewer C showed that legacy `init` / `adopt baseline` / `migrate baseline` root at `current_dir()` and, run from a
subdirectory of an intact revision-4 project, write a nested legacy install (56 invocations inside `governance/trust/**`)
while `18` §9 stays COMPLETE. C did not test (a) `governance/` itself or `governance/trust/kernel/` as the working
directory, (b) whether the nested install then makes EVERY legacy command operational from deeper directories, or (c)
whether a follow-on legacy CIT, rooted at the nested install, can rewrite RoT-1 files through nested-root-relative paths.

This probe answers those, on copies of reviewer C's R4 tree (rebuilt by this review), with the real 4.1.5 binary and
real Git. RoT-1 behaviour is evaluated with two independent re-encodings of `18` §9 (reviewer C's `c4lib.installation_state`
and the architect's `LR2` state machine), the `18` §6.1 kernel check (the installed kernel tree must equal the release
content set: any added, removed or changed file is KERNEL_TAMPERED), and the architect's revision-4 strength vector
(`csi_lib.strength_requirements` / `strength_failures`, via LR2) on a machine that recorded the committed overlay.

Scratch only; GOV_* stripped from children (c4lib.child_env); no forced deletes.
Usage: RV4-D-A01-nested-root-escalation.py <reviewer-C trees.json> <out-dir> <worktree>
"""
import importlib.util, json, os, sys

sys.dont_write_bytecode = True
TREES, OUT, WT = sys.argv[1], sys.argv[2], sys.argv[3]
C_EV = os.path.join(WT, "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
sys.path.insert(0, C_EV)
os.environ["AR7_WT"] = WT
import c4lib as c4  # noqa: E402

spec = importlib.util.spec_from_file_location("lr2", os.path.join(WT, "release/root-of-trust/4.1.6/evidence/LR2-installation-state-and-strength-reference.py"))
LR2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LR2)

T = json.load(open(TREES))
S = T["scratch"]
R4 = T["trees"]["R4"]
os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(OUT, "trees")
os.makedirs(BASE, exist_ok=True)
GOV = c4.BINS["4.1.5"]


def rot1_view(root):
    st_c = c4.installation_state(root)
    st_a = LR2.installation_state(root)
    recorded = LR2.overlay_docs_head(root)
    current = LR2.overlay_docs_worktree(root)
    reqs = LR2.L.strength_requirements(LR2.INV, recorded, {}, {})
    fails = LR2.L.strength_failures(LR2.INV, reqs, current, {})
    return {"state_18_s9_reviewer_C_encoding": st_c["state"], "state_18_s9_architect_LR2_encoding": st_a["state"],
            "not_examined_by_18_s9": st_c["diagnostics_not_in_18_s9"],
            "recorded_machine_PROJECT_STRENGTH_WEAKENED": bool(fails), "strength_failures": fails[:6]}


def fresh(tag):
    dst = os.path.join(BASE, tag)
    c4.copy_tree(R4, dst)
    return dst


def run(root, cwd_rel, argv, tag):
    env = c4.child_env(S, "rv4d-a01-" + tag)
    cwd = os.path.join(root, cwd_rel)
    kern_before = c4.digest(c4.tree_map(os.path.join(root, "governance/trust/kernel")))
    trust_before = c4.tree_map(os.path.join(root, "governance/trust"))
    before = c4.snap(root, env["HOME"])
    r = c4.gov(GOV, argv, env, cwd, None)
    after = c4.snap(root, env["HOME"])
    cmp = c4.compare(before, after)
    trust_after = c4.tree_map(os.path.join(root, "governance/trust"))
    return {"cwd": cwd_rel, "argv": argv, "ok": r.get("ok"), "code": c4.code(r),
            "n_work_writes": cmp["work_n"],
            "trust_paths_changed": ["governance/trust/" + p for p in c4.changed(trust_before, trust_after)][:15],
            "installed_kernel_tree_changed (18 §6.1 KERNEL_TAMPERED)": kern_before != c4.digest(c4.tree_map(os.path.join(root, "governance/trust/kernel"))),
            "result_verified": (c4.result(r) or {}).get("verified") if isinstance(c4.result(r), dict) else None}


def cit(root, cwd_rel, ops, tag):
    """Legacy CIT from a nested root (no --root): propose → simulate → approve (caller-declared owner decide if gated) → execute."""
    import re
    env = c4.child_env(S, "rv4d-a01-cit-" + tag)
    cwd = os.path.join(root, cwd_rel)
    mf = os.path.join(OUT, "fixtures", f"cit-{tag}.json")
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump(ops, open(mf, "w"))
    kern_before = c4.digest(c4.tree_map(os.path.join(root, "governance/trust/kernel")))
    trust_before = c4.tree_map(os.path.join(root, "governance/trust"))
    ov_before = c4.tree_map(os.path.join(root, "governance/overlay"))
    steps = {}
    t = c4.gov(GOV, ["task", "create", "--class", "documentation", "--objective", "x", "--title", "t", "--status", "READY"], env, cwd, None)
    steps["task_create"] = {"ok": t.get("ok"), "code": c4.code(t)}
    task = (c4.result(t) or {}).get("id") or "TASK-0001"
    p = c4.gov(GOV, ["cit", "propose", "--proposal", "p", "--trigger", "editorial", "--targets", task, "--manifest", mf], env, cwd, None)
    steps["propose"] = {"ok": p.get("ok"), "code": c4.code(p)}
    cid = (c4.result(p) or {}).get("id") or "CIT-0001"
    s = c4.gov(GOV, ["cit", "simulate", cid], env, cwd, None)
    steps["simulate"] = {"ok": s.get("ok"), "code": c4.code(s)}
    ap = c4.gov(GOV, ["cit", "approve", cid, "--by", "orchestrator", "--method", "auto"], env, cwd, None)
    steps["approve"] = {"ok": ap.get("ok"), "code": c4.code(ap)}
    m = re.search(r"(HDG-\d+)", json.dumps(ap.get("error") or {}))
    if not ap.get("ok") and m:
        gid = m.group(1)
        c4.gov(GOV, ["gate", "present", gid], env, cwd, None)
        d = c4.gov(GOV, ["decide", gid, "--option", "A", "--by", "owner"], env, cwd, None)
        steps["decide_by_owner_caller_declared"] = {"ok": d.get("ok"), "code": c4.code(d)}
        ap = c4.gov(GOV, ["cit", "approve", cid, "--by", "owner", "--method", "human"], env, cwd, None)
        steps["approve_after_gate"] = {"ok": ap.get("ok"), "code": c4.code(ap)}
    ex = c4.gov(GOV, ["cit", "execute", cid], env, cwd, None)
    steps["execute"] = {"ok": ex.get("ok"), "code": c4.code(ex)}
    trust_after = c4.tree_map(os.path.join(root, "governance/trust"))
    return {"cwd": cwd_rel, "manifest_ops": ops, "steps": steps,
            "trust_paths_changed": ["governance/trust/" + x for x in c4.changed(trust_before, trust_after)][:15],
            "overlay_paths_changed": ["governance/overlay/" + x for x in c4.changed(ov_before, c4.tree_map(os.path.join(root, "governance/overlay")))][:10],
            "installed_kernel_tree_changed (18 §6.1 KERNEL_TAMPERED)": kern_before != c4.digest(c4.tree_map(os.path.join(root, "governance/trust/kernel"))),
            "governance_trust_framework_lock_after": c4.kind(os.path.join(root, "governance/trust/framework.lock"))}


out = {"probe": "RV4-D-A01", "binary_sha256": c4.sha(open(GOV, "rb").read()), "cases": {}}
OVERLAY_WIPE = "schema_version: 1.0.0\nclassifications: []\n"

# N1: working directory governance/ (not in reviewer C's position list)
r = fresh("N1-governance")
row = {"init": run(r, "governance", ["init", "--skip-index"], "n1-init")}
row["nested_status_from_governance_views"] = run(r, "governance/views", ["kernel", "trust"], "n1-trust")
row["cit_from_nested_root_governance"] = cit(r, "governance", [
    {"op": "write_file", "path": "overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE},
    {"op": "write_file", "path": "trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
    {"op": "delete_file", "path": "trust/framework.lock"}], "n1")
row["rot1_after"] = rot1_view(r)
out["cases"]["N1_cwd_governance_then_cit"] = row

# N1b: overlay-only CIT (the only follow-on that does not touch governance/trust), to separate the state-machine effect
r = fresh("N1b-governance-overlay-only")
row = {"init": run(r, "governance", ["init", "--skip-index"], "n1b-init"),
       "cit_overlay_only": cit(r, "governance", [{"op": "write_file", "path": "overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE}], "n1b")}
row["rot1_after"] = rot1_view(r)
out["cases"]["N1b_cwd_governance_then_overlay_only_cit"] = row

# N2: working directory governance/trust, then every legacy command operational from deeper inside the PPS, then a CIT
r = fresh("N2-trust")
row = {"init": run(r, "governance/trust", ["init", "--skip-index"], "n2-init")}
row["status_from_governance_trust_kernel_policies"] = run(r, "governance/trust/kernel/policies", ["status"], "n2-status")
row["rebuild_memory_from_governance_trust_state"] = run(r, "governance/trust/state", ["rebuild-memory"], "n2-rebuild")
row["cit_from_nested_root_governance_trust"] = cit(r, "governance/trust", [
    {"op": "write_file", "path": "kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"}], "n2")
row["rot1_after"] = rot1_view(r)
out["cases"]["N2_cwd_governance_trust_then_cit"] = row

# N3: working directory governance/trust/kernel (inside the installed kernel)
r = fresh("N3-kernel")
row = {"init": run(r, "governance/trust/kernel", ["init", "--skip-index"], "n3-init")}
row["rot1_after"] = rot1_view(r)
out["cases"]["N3_cwd_governance_trust_kernel"] = row

# Control: intact R4, same CIT from the project root (no nested install)
r = fresh("C0-control")
row = {"cit_from_project_root": cit(r, ".", [{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE}], "c0")}
row["rot1_after"] = rot1_view(r)
out["cases"]["C0_control_intact_project_root_cit"] = row

text = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(OUT, "<out>").replace(WT, "<worktree>")
open(os.path.join(OUT, "RV4-D-A01-nested-root-escalation.json"), "w").write(text)
print(text)
