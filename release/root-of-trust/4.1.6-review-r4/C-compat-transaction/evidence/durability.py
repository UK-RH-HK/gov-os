#!/usr/bin/env python3
"""AR-0007 layout durability: does the revision-4 occupation layout survive every way a project reaches a machine or is
changed by ordinary Git tooling and legacy remedies, and is the loss detected before harm?

For each delivery/mutation, the occupation entry types are recorded, the `18` §9 installation state is computed, and the
"untrack ignored files" idiom is exercised. Where the occupation is intact, a real legacy 4.1.5 `init --force` is run and
its write set + verified view captured. Everything runs in scratch; children have GOV_* stripped.

Two ignore-rule variants of the migrated project are tested:
  R4     `.gitignore` = `/.governance-runtime/*` + `!/.governance-runtime/migration`  (the pack's REPLACE reading)
  R4APP  `.gitignore` = legacy `.governance-runtime/` line kept, rule APPENDED (the non-destructive reading of `26` §7)

Usage: durability.py <trees.json> <out-dir>
"""
import json, os, shutil, subprocess, sys, tarfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import *  # noqa

OCC = list(OCCUPATION) + ["governance/trust", "governance/trust/kernel", "governance/overlay", "governance/kernel/KERNEL_MANIFEST.json"]


def types(root):
    return {p: kind(os.path.join(root, p)) for p in OCC}


def idiom(root, home):
    """git ls-files -ci --exclude-standard then git rm --cached; commit; fresh clone; report occupation in the clone."""
    listed = [x for x in git(root, "ls-files", "-ci", "--exclude-standard", check=False, home=home).stdout.split() if x]
    for f in listed:
        git(root, "rm", "-q", "--cached", f, check=False, home=home)
    c = git(root, "commit", "-q", "-m", "untrack ignored files", check=False, home=home)
    clone = root + "__idiomclone"
    git(os.path.dirname(root), "clone", "-q", root, clone, home=home)
    return {"listed_by_idiom": listed, "commit_made": c.returncode == 0,
            "migration_occupation_in_fresh_clone": kind(os.path.join(clone, ".governance-runtime/migration")),
            "clone_state": installation_state(clone)["state"]}


def legacy_initforce(S, root, tag):
    d = os.path.join(S, "dur-if-" + tag)
    copy_tree(root, d)
    env = child_env(S, "if-" + tag)
    before = snap(d, env["HOME"])
    r = gov(BINS["4.1.5"], ["init", "--force", "--source", REL["4.1.5"], "--skip-index"], env, d, d)
    after = snap(d, env["HOME"])
    cmp = compare(before, after)
    harm = legacy_harm(BINS["4.1.5"], env, d, d) if cmp["work_changed"] else {"skipped": "no work change"}
    return {"init_force_ok": r.get("ok"), "init_force_code": code(r), "work_changed": cmp["work_changed"], "work_paths": cmp["work_paths"][:20],
            "trust_paths_written": [p for p in cmp["work_paths"] if p.startswith("governance/trust")], "state_after": installation_state(d)["state"], "legacy_harm": harm}


def main():
    T = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    S = T["scratch"]
    home = os.path.join(S, "homes", "dur")
    os.makedirs(home, exist_ok=True)
    res = {}
    for variant in ("R4", "R4APP"):
        src = T["trees"][variant]
        base = os.path.join(S, "dur-" + variant)
        os.makedirs(base, exist_ok=True)
        v = {}
        v["source_gitignore"] = open(os.path.join(src, ".gitignore")).read()

        # 1 fresh full clone
        c1 = os.path.join(base, "clone_full"); git(base, "clone", "-q", src, c1, home=home)
        v["1_fresh_clone"] = {"types": types(c1), "state": installation_state(c1)["state"], **({"legacy_init_force": legacy_initforce(S, c1, variant + "1")} if installation_state(c1)["state"] == "COMPLETE" else {})}

        # 2 shallow clone depth 1
        c2 = os.path.join(base, "clone_shallow"); git(base, "clone", "-q", "--depth", "1", "file://" + src, c2, home=home)
        v["2_shallow_clone"] = {"types": types(c2), "state": installation_state(c2)["state"]}

        # 3 git archive tarball (no .git); is_installed still checked on extracted tree
        tar = os.path.join(base, "arch.tar")
        with open(tar, "wb") as f:
            subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=src, stdout=f, check=True, env=git_env(home))
        ex = os.path.join(base, "archive_extract"); os.makedirs(ex)
        with tarfile.open(tar) as t:
            t.extractall(ex)
        v["3_git_archive"] = {"types": types(ex), "state": installation_state(ex)["state"], "note": "no .git present"}

        # 4 git clean -fdx on a fresh clone (occupation tracked → survives; untracked runtime removed)
        c4 = os.path.join(base, "clone_clean"); git(base, "clone", "-q", src, c4, home=home)
        git(c4, "clean", "-fdx", check=False, home=home)
        v["4_git_clean_fdx"] = {"types": types(c4), "state": installation_state(c4)["state"]}

        # 5 stash: dirty the occupation, stash, pop
        c5 = os.path.join(base, "clone_stash"); git(base, "clone", "-q", src, c5, home=home)
        open(os.path.join(c5, "governance/kernel"), "a").write("dirty\n")
        st = git(c5, "stash", check=False, home=home)
        after_stash = types(c5)
        git(c5, "stash", "pop", check=False, home=home)
        v["5_stash_pop"] = {"stash_rc": st.returncode, "types_after_stash": {k: after_stash[k] for k in OCCUPATION}, "types_after_pop": {k: types(c5)[k] for k in OCCUPATION}, "state": installation_state(c5)["state"]}

        # 6 sparse-checkout cone mode default (modern git): does the top-level occupation survive?
        c6 = os.path.join(base, "clone_sparse_cone"); git(base, "clone", "-q", "--no-checkout", src, c6, home=home)
        git(c6, "sparse-checkout", "set", "governance", check=False, home=home)
        git(c6, "checkout", "-q", "main", check=False, home=home)
        v["6_sparse_cone_governance"] = {"types": types(c6), "state": installation_state(c6)["state"], "note": "cone sparse-checkout of governance/"}

        # 7 sparse non-cone omitting occupation but keeping governance/trust
        c7 = os.path.join(base, "clone_sparse_omit"); git(base, "clone", "-q", "--no-checkout", src, c7, home=home)
        git(c7, "sparse-checkout", "init", "--no-cone", check=False, home=home)
        open(os.path.join(c7, ".git", "info", "sparse-checkout"), "w").write("/*\n!/governance/kernel\n!/governance/project\n!/governance/generated\n!/.governance-runtime/migration\n")
        git(c7, "checkout", "-q", "main", check=False, home=home)
        v["7_sparse_omit_occupation"] = {"types": types(c7), "state": installation_state(c7)["state"], **({"legacy_init_force": legacy_initforce(S, c7, variant + "7")} if os.path.isdir(os.path.join(c7, "governance/trust")) else {})}

        # 8 checkout across the migration commit and back
        c8 = os.path.join(base, "clone_checkout"); git(base, "clone", "-q", src, c8, home=home)
        git(c8, "checkout", "-q", "HEAD~1", home=home)
        legacy_types = types(c8)
        lif = legacy_initforce(S, c8, variant + "8legacy")
        git(c8, "checkout", "-q", "main", home=home)
        v["8_checkout_across_migration"] = {"at_legacy_types": {k: legacy_types[k] for k in OCCUPATION}, "at_legacy_state": installation_state(os.path.join(S, "dur-if-" + variant + "8legacy"))["state"],
                                            "legacy_init_force_at_pre_migration": {"ok": lif["init_force_ok"], "state_after": lif["state_after"]}, "back_to_r4_types": types(c8), "back_state": installation_state(c8)["state"]}

        # 9 git worktree add of the migration commit
        c9wt = os.path.join(base, "wt_extra")
        wa = git(src, "worktree", "add", "-q", c9wt, "main", check=False, home=home)
        v["9_worktree_add"] = {"rc": wa.returncode, "types": types(c9wt) if os.path.isdir(c9wt) else "n/a", "state": installation_state(c9wt)["state"] if os.path.isdir(c9wt) else "n/a"}
        git(src, "worktree", "remove", "--force", c9wt, check=False, home=home)

        # 10 the untracking idiom on a fresh clone
        c10 = os.path.join(base, "clone_idiom"); git(base, "clone", "-q", src, c10, home=home)
        v["10_untrack_idiom"] = idiom(c10, home)

        # 11 revert of the migration commit (full downgrade)
        c11 = os.path.join(base, "clone_revert"); git(base, "clone", "-q", src, c11, home=home)
        rv = git(c11, "revert", "--no-edit", "HEAD", check=False, home=home)
        v["11_git_revert"] = {"rc": rv.returncode, "types": {k: types(c11)[k] for k in OCCUPATION}, "state": installation_state(c11)["state"]}

        # 12 case-insensitive collision enumeration in the tracked tree
        files = git(src, "ls-tree", "-r", "--name-only", "HEAD", home=home).stdout.split()
        seen, coll = {}, []
        for f in files:
            lf = f.lower()
            if lf in seen and seen[lf] != f:
                coll.append([seen[lf], f])
            seen[lf] = f
        v["12_case_collisions"] = coll

        res[variant] = v
    with open(os.path.join(out_dir, "durability.json"), "w") as f:
        f.write(scrub(json.dumps(res, indent=1, sort_keys=True, default=str), S))
    # concise summary to stdout
    summ = {}
    for var, v in res.items():
        summ[var] = {k: (v[k].get("state") if isinstance(v[k], dict) else v[k]) for k in v if k[0].isdigit()}
        summ[var]["idiom_listed"] = v["10_untrack_idiom"]["listed_by_idiom"]
        summ[var]["idiom_clone_state"] = v["10_untrack_idiom"]["clone_state"]
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
