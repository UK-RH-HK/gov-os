#!/usr/bin/env python3
"""AR-0013: derive trees that ordinary Git operations produce from the revision-5 layout, evaluate the `18` §9/§9.1 state on
each, and record the facts. The pre-RoT matrix (matrix5.py) then runs the legacy registers on every derived tree.

Operations (real Git 2.43): fresh clone; shallow clone (--depth 1); partial clone (--filter=blob:none); cone sparse
checkout of `governance`; non-cone sparse checkout omitting two occupation entries; stash -u of a dirtied tree; clean -fdx;
checkout of the pre-migration commit and back; `git archive` extraction; clone with core.autocrlf=true; clone into a
repository whose .gitattributes says `* text=auto` with core.eol=crlf; `git worktree add`; checkout of the pre-migration
commit (LR-1); `git restore --source <pre> -- governance` (LR-2 trigger); the "untrack ignored files" idioms on R5 and on
R5NOSURG followed by a fresh clone; a user-level core.excludesFile listing `.governance-runtime/` followed by the
`git rm -r --cached . && git add .` idiom and a fresh clone.

Usage: gitops5.py <trees.json> <out-dir>   (writes <out-dir>/gitops.json and derived trees under <out-dir>/t/)
"""
import json, os, shutil, subprocess, sys, tarfile, io
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c5lib as L  # noqa


def facts(root, rcs, note=""):
    st = L.state_r5(root)
    occ = {p: L.kind(os.path.join(root, p)) for p in L.OCCUPATION}
    return {"state": st["state"], "reasons": st["reasons"], "reports": st["reports"], "occupation": occ,
            "kernel_tampered": L.kernel_tampered(root, rcs) if L.kind(os.path.join(root, "governance/trust/kernel")) == "dir" else None,
            "note": note}


def main():
    T = json.load(open(sys.argv[1]))
    OUT = os.path.abspath(sys.argv[2])
    D = os.path.join(OUT, "t")
    os.makedirs(D, exist_ok=False)
    R5, NOS = T["trees"]["R5"], T["trees"]["R5NOSURG"]
    rcs = T["rcs"]
    pre = T["R5"]["pre_migration"]
    home = os.path.join(OUT, "githome")
    os.makedirs(home, exist_ok=True)
    g = lambda cwd, *a, **k: L.git(cwd, *a, home=home, **k)
    res, trees = {}, {}

    def add(name, path, note=""):
        trees[name] = path
        res[name] = facts(path, rcs, note)

    p = os.path.join(D, "CLONE"); g(D, "clone", "-q", R5, p); add("CLONE", p)
    p = os.path.join(D, "SHALLOW"); g(D, "clone", "-q", "--depth", "1", "file://" + R5, p); add("SHALLOW", p)
    p = os.path.join(D, "PARTIAL_CLONE"); g(D, "clone", "-q", "--filter=blob:none", "file://" + R5, p); add("PARTIAL_CLONE", p)
    p = os.path.join(D, "SPARSE_CONE"); g(D, "clone", "-q", R5, p); g(p, "sparse-checkout", "set", "--cone", "governance"); add("SPARSE_CONE", p)
    p = os.path.join(D, "SPARSE_NONCONE"); g(D, "clone", "-q", R5, p)
    g(p, "sparse-checkout", "set", "--no-cone", "/*", "!/governance/kernel", "!/.governance-runtime/migration")
    add("SPARSE_NONCONE", p)
    p = os.path.join(D, "STASH"); L.copy_tree(R5, p)
    open(os.path.join(p, "governance/overlay/NOTE.md"), "w").write("dirty\n")
    open(os.path.join(p, "product/readme.md"), "a").write("dirty\n")
    g(p, "stash", "push", "-u", "-q"); add("STASH", p, "after git stash push -u")
    p = os.path.join(D, "CLEAN"); L.copy_tree(R5, p); r = g(p, "clean", "-fdxq", check=False); add("CLEAN", p, "git clean -fdx rc=%d" % r.returncode)
    p = os.path.join(D, "CHECKOUT_BACK"); L.copy_tree(R5, p); g(p, "checkout", "-q", pre); g(p, "checkout", "-q", "main"); add("CHECKOUT_BACK", p)
    p = os.path.join(D, "ARCHIVE"); os.makedirs(p)
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=R5, capture_output=True, env=L.git_env(home)).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(p, filter="tar")
    add("ARCHIVE", p, "git archive HEAD | tar -x (no .git, no untracked runtime)")
    p = os.path.join(D, "AUTOCRLF"); g(D, "-c", "core.autocrlf=true", "clone", "-q", R5, p); add("AUTOCRLF", p, "clone with core.autocrlf=true (Git for Windows default)")
    # repository that carries `* text=auto` (common) checked out with core.eol=crlf
    p0 = os.path.join(D, "TEXTAUTO_SRC"); L.copy_tree(R5, p0)
    open(os.path.join(p0, ".gitattributes"), "w").write("* text=auto\n")
    g(p0, "add", ".gitattributes"); g(p0, "commit", "-q", "-m", "gitattributes text=auto")
    p = os.path.join(D, "TEXTAUTO_EOLCRLF"); g(D, "-c", "core.eol=crlf", "clone", "-q", p0, p)
    g(p, "config", "core.eol", "crlf"); g(p, "rm", "-q", "--cached", "-r", "."); g(p, "reset", "-q", "--hard")
    add("TEXTAUTO_EOLCRLF", p, "* text=auto + core.eol=crlf")
    p = os.path.join(D, "WORKTREE"); L.copy_tree(R5, os.path.join(D, "WT_BASE"))
    g(os.path.join(D, "WT_BASE"), "worktree", "add", "-q", "--detach", p, "HEAD"); add("WORKTREE", p)
    p = os.path.join(D, "CHECKOUT_PRE"); L.copy_tree(R5, p); g(p, "checkout", "-q", pre); add("CHECKOUT_PRE", p, "LR-1: working copy on the pre-migration commit")
    p = os.path.join(D, "RESTORE_PRE_GOV"); L.copy_tree(R5, p)
    r = g(p, "restore", "--source", pre, "--", "governance", check=False); add("RESTORE_PRE_GOV", p, "LR-2 trigger rc=%d %s" % (r.returncode, r.stderr[-200:]))
    # untracking idioms
    for name, src in (("UNTRACK_R5", R5), ("UNTRACK_NOSURG", NOS)):
        w = os.path.join(D, name + "_WORK"); L.copy_tree(src, w)
        listed = g(w, "ls-files", "-ci", "--exclude-standard").stdout.split()
        for x in listed:
            g(w, "rm", "-q", "--cached", x)
        g(w, "commit", "-q", "--allow-empty", "-m", "untrack ignored files")
        p = os.path.join(D, name); g(D, "clone", "-q", w, p); add(name, p, "idiom listed %s" % listed)
    # user global excludes + `git rm -r --cached . && git add .`
    gh = os.path.join(OUT, "githome-excl")
    os.makedirs(gh, exist_ok=True)
    open(os.path.join(gh, "excl"), "w").write(".governance-runtime/\n.DS_Store\n")
    w = os.path.join(D, "GLOBALEXCL_WORK"); L.copy_tree(R5, w)
    ge = {"GIT_CONFIG_GLOBAL": os.path.join(gh, "gitconfig")}
    open(ge["GIT_CONFIG_GLOBAL"], "w").write("[core]\n\texcludesFile = %s\n" % os.path.join(gh, "excl"))
    listed = L.git(w, "ls-files", "-ci", "--exclude-standard", home=gh, extra_env=ge).stdout.split()
    L.git(w, "rm", "-r", "-q", "--cached", ".", home=gh, extra_env=ge)
    L.git(w, "add", ".", home=gh, extra_env=ge)
    L.git(w, "commit", "-q", "--allow-empty", "-m", "re-apply ignore rules", home=gh, extra_env=ge)
    p = os.path.join(D, "GLOBALEXCL"); g(D, "clone", "-q", w, p); add("GLOBALEXCL", p, "user excludesFile has .governance-runtime/; ls-files -ci listed %s" % listed)
    # the pack's rule written into .git/info/exclude by a tool, then the idiom
    w = os.path.join(D, "INFOEXCL_WORK"); L.copy_tree(R5, w)
    open(os.path.join(w, ".git/info/exclude"), "a").write(".governance-runtime/\n")
    listed = g(w, "ls-files", "-ci", "--exclude-standard").stdout.split()
    for x in listed:
        g(w, "rm", "-q", "--cached", x)
    g(w, "commit", "-q", "--allow-empty", "-m", "untrack ignored")
    p = os.path.join(D, "INFOEXCL"); g(D, "clone", "-q", w, p); add("INFOEXCL", p, ".git/info/exclude has .governance-runtime/; idiom listed %s" % listed)
    L.dump({"trees": trees, "facts": res}, os.path.join(OUT, "gitops.json"))
    json.dump({"trees": trees}, open(os.path.join(OUT, "gitops-trees.json"), "w"))
    for k, v in res.items():
        print(k, v["state"], v["reasons"], v["note"][:90])


if __name__ == "__main__":
    main()
