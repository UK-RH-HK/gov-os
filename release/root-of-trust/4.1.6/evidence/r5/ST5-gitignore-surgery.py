#!/usr/bin/env python3
"""ST5 gitignore surgery (RV4-M6 reference): apply install-transaction surgery on R4APP's gitignore,
verify idempotence, fresh-clone state.

Origin: NEW (not copied from any reviewer script).

Usage: ST5-gitignore-surgery.py <trees.json> <out-dir>
"""
import importlib.util, json, os, re, shutil, subprocess, sys
sys.dont_write_bytecode = True

C_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
R5_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6/evidence/r5")
sys.path.insert(0, C_EV)
from c4lib import (installation_state, git, git_env, copy_tree, scrub, sha, kind) # noqa

# Import r5 functions
_r5_spec = importlib.util.spec_from_file_location("st5_r5", os.path.join(R5_EV, "ST5-installation-state-r5.py"))
_r5_mod = importlib.util.module_from_spec(_r5_spec)
_r5_spec.loader.exec_module(_r5_mod)
installation_state_r5 = _r5_mod.installation_state_r5
_pristine_kernel_content_set = _r5_mod._pristine_kernel_content_set


def apply_surgery(gitignore_path):
    """Apply the install-transaction surgery:
    1. Remove every pre-existing .governance-runtime/ or .governance-runtime directory-ignore line
       (with or without leading slash or trailing slash)
    2. Ensure /.governance-runtime/* and !/.governance-runtime/migration exist once.
    Returns (new_text, changes_made).
    """
    text = open(gitignore_path).read()
    lines = text.splitlines()
    out = []
    removed = []
    pattern = re.compile(r'^/?\.governance-runtime/?$')
    for line in lines:
        stripped = line.strip()
        if pattern.match(stripped):
            removed.append(line)
        else:
            out.append(line)
    # Ensure the new rules exist once
    new_rules = ["/.governance-runtime/*", "!/.governance-runtime/migration"]
    for rule in new_rules:
        if rule not in out:
            out.append(rule)
    new_text = "\n".join(out) + "\n"
    changed = new_text != text
    return new_text, changed, removed


def main():
    T = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    S = T["scratch"]
    R4APP = T["trees"]["R4APP"]
    R4 = T["trees"]["R4"]
    WT = os.environ.get("AR7_WT", "")

    # Build reference kernel
    ref_kernel = _pristine_kernel_content_set(R4)

    results = {}

    # === SURGERY TEST ===
    # Fresh copy of R4APP
    surg = os.path.join(S, "gitignore-surgery", "surgery")
    os.makedirs(os.path.dirname(surg), exist_ok=True)
    copy_tree(R4APP, surg)

    gi_path = os.path.join(surg, ".gitignore")
    results["original_gitignore"] = open(gi_path).read()

    # Apply surgery (pass 1)
    new_text, changed1, removed1 = apply_surgery(gi_path)
    open(gi_path, "w").write(new_text)
    results["pass1"] = {"changed": changed1, "removed_lines": removed1, "gitignore_after": new_text}

    # Apply surgery (pass 2 — idempotence)
    new_text2, changed2, removed2 = apply_surgery(gi_path)
    open(gi_path, "w").write(new_text2)
    results["pass2_idempotent"] = {"changed": changed2, "removed_lines": removed2, "idempotent": not changed2}

    # Commit
    git(surg, "add", "-A")
    git(surg, "commit", "-q", "-m", "gitignore surgery: replace legacy runtime ignore with RoT-1 rules")

    # Check git ls-files -ci --exclude-standard (expect empty after surgery)
    ci = git(surg, "ls-files", "-ci", "--exclude-standard", check=False)
    results["ls_files_ci_after_surgery"] = ci.stdout.strip().split() if ci.stdout.strip() else []

    # Untracking idiom: git rm -r --cached of whatever ls-files -ci lists
    if results["ls_files_ci_after_surgery"]:
        for f in results["ls_files_ci_after_surgery"]:
            git(surg, "rm", "-r", "--cached", f, check=False)
        rc = git(surg, "commit", "-q", "-m", "untrack ignored files", check=False)
        results["untrack_commit"] = {"returncode": rc.returncode, "stderr": rc.stderr[:200]}
    else:
        results["untrack_commit"] = {"returncode": None, "note": "nothing to untrack"}

    # Fresh clone
    clone_surg = os.path.join(S, "gitignore-surgery", "clone-surgery")
    home = os.path.join(S, "homes", "gi-surg")
    os.makedirs(home, exist_ok=True)
    git(os.path.dirname(clone_surg), "clone", "-q", surg, clone_surg, home=home)

    # Evaluate r4 and r5 state on clone
    r4_surg = installation_state(clone_surg)
    r5_surg = installation_state_r5(clone_surg, pristine_kernel_ref=ref_kernel)
    results["clone_surgery_state_r4"] = r4_surg["state"]
    results["clone_surgery_state_r5"] = r5_surg["state"]
    results["clone_surgery_r5_reasons"] = r5_surg.get("reasons", [])
    results["clone_surgery_occupation"] = r4_surg["occupation"]

    # === CONTROL (no surgery) ===
    ctrl = os.path.join(S, "gitignore-surgery", "control")
    copy_tree(R4APP, ctrl)

    results["control_gitignore"] = open(os.path.join(ctrl, ".gitignore")).read()

    # ls-files -ci on the control (R4APP as-is)
    ci_ctrl = git(ctrl, "ls-files", "-ci", "--exclude-standard", check=False)
    results["control_ls_files_ci"] = ci_ctrl.stdout.strip().split() if ci_ctrl.stdout.strip() else []

    # Untracking idiom on control
    if results["control_ls_files_ci"]:
        for f in results["control_ls_files_ci"]:
            git(ctrl, "rm", "-r", "--cached", f, check=False)
        rc = git(ctrl, "commit", "-q", "-m", "untrack ignored files", check=False)
        results["control_untrack_commit"] = {"returncode": rc.returncode, "stderr": rc.stderr[:200]}
    else:
        results["control_untrack_commit"] = {"returncode": None, "note": "nothing to untrack"}

    # Fresh clone of control
    clone_ctrl = os.path.join(S, "gitignore-surgery", "clone-control")
    git(os.path.dirname(clone_ctrl), "clone", "-q", ctrl, clone_ctrl, home=home)

    r4_ctrl = installation_state(clone_ctrl)
    r5_ctrl = installation_state_r5(clone_ctrl, pristine_kernel_ref=ref_kernel)
    results["clone_control_state_r4"] = r4_ctrl["state"]
    results["clone_control_state_r5"] = r5_ctrl["state"]
    results["clone_control_r5_reasons"] = r5_ctrl.get("reasons", [])
    results["clone_control_occupation"] = r4_ctrl["occupation"]
    results["clone_control_migration_kind"] = kind(os.path.join(clone_ctrl, ".governance-runtime", "migration"))

    with open(os.path.join(out_dir, "ST5-gitignore-surgery.json"), "w") as f:
        f.write(scrub(json.dumps(results, indent=1, sort_keys=True, default=str), S))
    print(json.dumps({
        "surgery_idempotent": results["pass2_idempotent"]["idempotent"],
        "surgery_ls_ci_empty": results["ls_files_ci_after_surgery"] == [],
        "surgery_clone_r4": results["clone_surgery_state_r4"],
        "surgery_clone_r5": results["clone_surgery_state_r5"],
        "control_ls_ci": results["control_ls_files_ci"],
        "control_clone_r4": results["clone_control_state_r4"],
        "control_clone_r5": results["clone_control_state_r5"],
        "control_migration": results["clone_control_migration_kind"],
    }, indent=1))


if __name__ == "__main__":
    main()
