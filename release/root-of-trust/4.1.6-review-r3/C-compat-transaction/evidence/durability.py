#!/usr/bin/env python3
"""Layout durability: does the occupation layout survive every way a project reaches a machine / is changed, and is a
legacy binary ever presented an 'installed' RoT-1 project it will mutate? Whole-tree digests + legacy is_installed probe."""
import json, os, shutil, subprocess, sys, tarfile
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

OCC = ["governance/kernel", "governance/project", "governance/generated",
       "governance/framework.lock", "governance/framework.lock/ROT-1-TRUST-FORMAT",
       "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration"]


def entry_types(root):
    t = {}
    for p in OCC + ["governance/trust", "governance/trust/kernel", "governance/trust/framework.lock",
                    "governance/overlay", "governance/kernel/KERNEL_MANIFEST.json"]:
        fp = os.path.join(root, p)
        if os.path.islink(fp): t[p] = "link"
        elif os.path.isdir(fp): t[p] = "dir"
        elif os.path.isfile(fp): t[p] = "file"
        else: t[p] = "absent"
    return t


def legacy_installed_view(scratch, root, tag):
    """Emulate legacy is_installed()=lock_path().exists() && kernel/KERNEL_MANIFEST.json exists; then actually run a
    destructive legacy command and record writes."""
    lock = os.path.join(root, "governance/framework.lock")
    km = os.path.join(root, "governance/kernel/KERNEL_MANIFEST.json")
    installed_pred = os.path.exists(lock) and os.path.exists(km)
    env = child_env(scratch, tag)
    before = {"tree": file_map(root), "trust": file_map(root + "/governance/trust", False) if os.path.isdir(root + "/governance/trust") else {}}
    # exercise the two worst legacy remedies
    outs = {}
    for name, args in (("update_rollback", ["update", "--rollback", "--reason", "d"]),
                       ("init_force", ["init", "--force", "--name", "d", "--skip-index"]),
                       ("kernel_reinstall", ["kernel", "reinstall"])):
        cc = os.path.join(scratch, "dcopy", tag + "-" + name)
        shutil.copytree(root, cc, symlinks=True)
        b2 = {"tree": file_map(cc), "trust": file_map(cc + "/governance/trust", False) if os.path.isdir(cc + "/governance/trust") else {}}
        r = gov(BINS["4.1.5"], cc, args, child_env(scratch, tag + "-" + name))
        a2 = {"tree": file_map(cc), "trust": file_map(cc + "/governance/trust", False) if os.path.isdir(cc + "/governance/trust") else {}}
        outs[name] = {"ok": r.get("ok"), "code": code(r),
                      "tree_changed": digest(b2["tree"]) != digest(a2["tree"]),
                      "trust_changed": digest(b2["trust"]) != digest(a2["trust"]),
                      "changed": changed(b2["tree"], a2["tree"])[:12]}
    return {"legacy_is_installed_pred": installed_pred, "remedies": outs}


def clone(scratch, src, name, *extra):
    dst = os.path.join(scratch, name)
    git(scratch, "clone", "-q", *extra, src, dst)
    return dst


def main():
    scratch = os.path.abspath(sys.argv[1])
    L3 = sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    res = {}

    # 1. Fresh full clone
    d = clone(scratch, L3, "clone_full")
    res["1_fresh_clone"] = {"types": entry_types(d), **legacy_installed_view(scratch, d, "clone_full")}

    # 2. git archive (tarball distribution)
    tarp = os.path.join(scratch, "arch.tar")
    with open(tarp, "wb") as f:
        subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=L3, stdout=f, check=True, env={"PATH": CLEANPATH, "HOME": L3})
    ex = os.path.join(scratch, "archive_extract"); os.makedirs(ex)
    with tarfile.open(tarp) as t: t.extractall(ex)
    res["2_git_archive"] = {"types": entry_types(ex), "note": "no .git; is_installed pred still checked",
                            "legacy_is_installed_pred": os.path.exists(ex + "/governance/framework.lock") and os.path.exists(ex + "/governance/kernel/KERNEL_MANIFEST.json")}

    # 3. checkout HEAD~1 (legacy) then back to HEAD
    d3 = clone(scratch, L3, "clone_checkout")
    git(d3, "checkout", "-q", "HEAD~1")
    legacy_types = entry_types(d3)
    legacy_run = legacy_installed_view(scratch, d3, "at_legacy_commit")
    git(d3, "checkout", "-q", "main")  # back to rot-1
    res["3_checkout_across_migration"] = {"at_legacy_commit_types": legacy_types, "at_legacy_run": legacy_run,
                                          "back_to_rot1_types": entry_types(d3)}

    # 4. case-insensitive collision enumeration (paths differing only by case in the RoT-1 tree)
    files = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=L3, capture_output=True, text=True, env={"PATH": CLEANPATH, "HOME": L3}).stdout.split()
    lower = {}
    collisions = []
    for f in files:
        lf = f.lower()
        if lf in lower and lower[lf] != f:
            collisions.append((lower[lf], f))
        lower[lf] = f
    res["4_case_collisions"] = collisions

    # 5. dir/file merge conflict: legacy branch (kernel=dir, framework.lock=file) merged into rot-1 branch
    d5 = clone(scratch, L3, "clone_merge")
    # legacy branch = the commit before migration
    git(d5, "branch", "-q", "legacy", "HEAD~1")
    git(d5, "checkout", "-q", "main")
    m = git(d5, "merge", "--no-edit", "legacy", check=False)
    res["5_dirfile_merge"] = {"merge_rc": m.returncode, "merge_out": (m.stdout + m.stderr)[-400:],
                              "types_after_merge": entry_types(d5),
                              "legacy_run_after_merge": legacy_installed_view(scratch, d5, "after_merge")}

    # 6. sparse checkout that omits the occupation files but keeps governance/trust
    d6 = clone(scratch, L3, "clone_sparse", "--no-checkout")
    git(d6, "sparse-checkout", "init", "--no-cone", check=False)
    # include everything, then exclude occupation
    sc = "/*\n!/governance/kernel\n!/governance/project\n!/governance/generated\n!/.governance-runtime/migration\n"
    open(os.path.join(d6, ".git", "info", "sparse-checkout"), "w").write(sc)
    git(d6, "checkout", "-q", "main", check=False)
    res["6_sparse_omit_occupation"] = {"types": entry_types(d6), **legacy_installed_view(scratch, d6, "sparse")}

    # 7. git clean -fdx on a fresh clone (occupation is tracked, should survive)
    d7 = clone(scratch, L3, "clone_clean")
    git(d7, "clean", "-fdx", check=False)
    res["7_git_clean_fdx"] = {"types": entry_types(d7), **legacy_installed_view(scratch, d7, "clean")}

    # 8. reverting the migration commit (a legacy remedy: "undo the RoT-1 change")
    d8 = clone(scratch, L3, "clone_revert")
    rv = git(d8, "revert", "--no-edit", "HEAD", check=False)
    res["8_git_revert_migration"] = {"revert_rc": rv.returncode, "revert_out": (rv.stdout + rv.stderr)[-300:],
                                     "types": entry_types(d8), **legacy_installed_view(scratch, d8, "revert")}

    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
