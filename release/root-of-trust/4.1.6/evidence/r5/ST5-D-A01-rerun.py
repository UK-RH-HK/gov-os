#!/usr/bin/env python3
"""ST5 D-A01 rerun: revision-5 state/reasons/nested diagnostics and discovery added to each case.

Origin: copied from RV4-D-A01-nested-root-escalation.py
  Origin path: release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A01-nested-root-escalation.py
  Origin SHA-256: 4bea5e09f13b99c071e45666fba9b9a402b054ac0d790fa5a857aa97cae44e05
Changes from origin:
  - Added r5 state, reasons, nested diagnostics and discovery for each case (N1, N1b, N2, N3, C0)
  - Removed LR2/strength analysis (only r4 and r5 state used)
  - Output file renamed to ST5-D-A01-rerun.json
  - rot1_view extended with r5 fields

Usage: ST5-D-A01-rerun.py <reviewer-C trees.json> <out-dir> <worktree>
"""
import importlib.util, json, os, sys

sys.dont_write_bytecode = True
TREES, OUT, WT = sys.argv[1], sys.argv[2], sys.argv[3]
C_EV = os.path.join(WT, "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
R5_EV = os.path.join(WT, "release/root-of-trust/4.1.6/evidence/r5")
sys.path.insert(0, C_EV)
os.environ["AR7_WT"] = WT
import c4lib as c4  # noqa: E402

# Import LR2 (the original D-A01 uses it)
spec_lr2 = importlib.util.spec_from_file_location("lr2", os.path.join(WT, "release/root-of-trust/4.1.6/evidence/LR2-installation-state-and-strength-reference.py"))
LR2 = importlib.util.module_from_spec(spec_lr2)
spec_lr2.loader.exec_module(LR2)

# Import r5 functions
_r5_spec = importlib.util.spec_from_file_location("st5_r5", os.path.join(R5_EV, "ST5-installation-state-r5.py"))
_r5_mod = importlib.util.module_from_spec(_r5_spec)
_r5_spec.loader.exec_module(_r5_mod)
installation_state_r5 = _r5_mod.installation_state_r5
rot1_root_discovery = _r5_mod.rot1_root_discovery
_pristine_kernel_content_set = _r5_mod._pristine_kernel_content_set

T = json.load(open(TREES))
S = T["scratch"]
R4 = T["trees"]["R4"]
os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(OUT, "trees")
os.makedirs(BASE, exist_ok=True)
GOV = c4.BINS["4.1.5"]
REF_KERNEL = _pristine_kernel_content_set(R4)


def rot1_view(root):
    st_c = c4.installation_state(root)
    st_a = LR2.installation_state(root)
    r5 = installation_state_r5(root, pristine_kernel_ref=REF_KERNEL)
    recorded = LR2.overlay_docs_head(root)
    current = LR2.overlay_docs_worktree(root)
    reqs = LR2.L.strength_requirements(LR2.INV, recorded, {}, {})
    fails = LR2.L.strength_failures(LR2.INV, reqs, current, {})
    return {"state_18_s9_reviewer_C_encoding": st_c["state"],
            "state_18_s9_architect_LR2_encoding": st_a["state"],
            "not_examined_by_18_s9": st_c["diagnostics_not_in_18_s9"],
            "recorded_machine_PROJECT_STRENGTH_WEAKENED": bool(fails),
            "strength_failures": fails[:6],
            "state_r5": r5["state"],
            "r5_reasons": r5.get("reasons", []),
            "r5_nested_inside_governance": r5.get("nested_inside_governance", []),
            "r5_nested_legacy_projects": r5.get("nested_legacy_projects", [])}


def rot1_discovery_for_subdir(root, sub):
    cwd = os.path.join(root, sub)
    os.makedirs(cwd, exist_ok=True)
    return rot1_root_discovery(cwd)


def fresh(tag):
    dst = os.path.join(BASE, tag)
    c4.copy_tree(R4, dst)
    return dst


def run(root, cwd_rel, argv, tag):
    env = c4.child_env(S, "st5-d-a01-" + tag)
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
    """Legacy CIT from a nested root (no --root)."""
    import re
    env = c4.child_env(S, "st5-d-a01-cit-" + tag)
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


out = {"probe": "ST5-D-A01-rerun", "binary_sha256": c4.sha(open(GOV, "rb").read()), "cases": {}}
OVERLAY_WIPE = "schema_version: 1.0.0\nclassifications: []\n"

# N1: working directory governance/
r = fresh("N1-governance")
disc_before = rot1_discovery_for_subdir(r, "governance")
row = {"init": run(r, "governance", ["init", "--skip-index"], "n1-init"),
       "discovery_before_init": disc_before}
row["nested_status_from_governance_views"] = run(r, "governance/views", ["kernel", "trust"], "n1-trust")
row["cit_from_nested_root_governance"] = cit(r, "governance", [
    {"op": "write_file", "path": "overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE},
    {"op": "write_file", "path": "trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
    {"op": "delete_file", "path": "trust/framework.lock"}], "n1")
row["rot1_after"] = rot1_view(r)
row["discovery_after"] = rot1_discovery_for_subdir(r, "governance")
out["cases"]["N1_cwd_governance_then_cit"] = row

# N1b: overlay-only CIT
r = fresh("N1b-governance-overlay-only")
disc_before = rot1_discovery_for_subdir(r, "governance")
row = {"init": run(r, "governance", ["init", "--skip-index"], "n1b-init"),
       "discovery_before_init": disc_before,
       "cit_overlay_only": cit(r, "governance", [{"op": "write_file", "path": "overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE}], "n1b")}
row["rot1_after"] = rot1_view(r)
row["discovery_after"] = rot1_discovery_for_subdir(r, "governance")
out["cases"]["N1b_cwd_governance_then_overlay_only_cit"] = row

# N2: working directory governance/trust
r = fresh("N2-trust")
disc_before = rot1_discovery_for_subdir(r, "governance/trust")
row = {"init": run(r, "governance/trust", ["init", "--skip-index"], "n2-init"),
       "discovery_before_init": disc_before}
row["status_from_governance_trust_kernel_policies"] = run(r, "governance/trust/kernel/policies", ["status"], "n2-status")
row["rebuild_memory_from_governance_trust_state"] = run(r, "governance/trust/state", ["rebuild-memory"], "n2-rebuild")
row["cit_from_nested_root_governance_trust"] = cit(r, "governance/trust", [
    {"op": "write_file", "path": "kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"}], "n2")
row["rot1_after"] = rot1_view(r)
row["discovery_after"] = rot1_discovery_for_subdir(r, "governance/trust")
out["cases"]["N2_cwd_governance_trust_then_cit"] = row

# N3: working directory governance/trust/kernel
r = fresh("N3-kernel")
disc_before = rot1_discovery_for_subdir(r, "governance/trust/kernel")
row = {"init": run(r, "governance/trust/kernel", ["init", "--skip-index"], "n3-init"),
       "discovery_before_init": disc_before}
row["rot1_after"] = rot1_view(r)
row["discovery_after"] = rot1_discovery_for_subdir(r, "governance/trust/kernel")
out["cases"]["N3_cwd_governance_trust_kernel"] = row

# C0: Control — intact R4, same CIT from the project root (no nested install)
r = fresh("C0-control")
disc_before = rot1_discovery_for_subdir(r, ".")
row = {"cit_from_project_root": cit(r, ".", [{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": OVERLAY_WIPE}], "c0"),
       "discovery_before_cit": disc_before}
row["rot1_after"] = rot1_view(r)
row["discovery_after"] = rot1_discovery_for_subdir(r, ".")
out["cases"]["C0_control_intact_project_root_cit"] = row

text = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(OUT, "<out>").replace(WT, "<worktree>")
open(os.path.join(OUT, "ST5-D-A01-rerun.json"), "w").write(text)
print(text)
