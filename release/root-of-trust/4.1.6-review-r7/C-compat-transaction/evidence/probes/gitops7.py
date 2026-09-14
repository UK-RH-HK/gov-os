#!/usr/bin/env python3
"""AR-0021 layout durability on the revision-7 layout (real Git 2.43.0). Every way a project reaches a machine or is changed by an
ordinary tool, then `state_r7` (all readings), the kernel-tampered check, the overlay classifications, and whether the migration
occupation is still tracked. Each resulting tree is kept for the matrix (P-GIT).

Carried from earlier reviews (re-asked on revision 7, own code): clone, shallow, partial, cone and non-cone sparse, archive,
clean -fdx, stash -u/pop, worktree, checkout across the migration and back, checkout and restore of pre-migration paths, the
untracking idiom under the project surgery / a retained legacy line / core.excludesFile / .git/info/exclude, autocrlf,
text=auto+eol=crlf, text eol=crlf, .git/info/attributes override (with and without conversion), core.ignorecase.
New (held-out, not in the pack's plan): bundle clone; zip archive; clean -fdx on the installed machine (transaction area and
snapshots are ignored); stash without -u; worktree at the pre-migration commit; reset --hard to pre-migration and back;
non-cone sparse keeping only governance/project and product on a legacy commit; the `git rm -r --cached . && git add .`
idiom under core.excludesFile; skip-worktree; a user core.attributesFile with eol=crlf; working-tree-encoding from
.git/info/attributes, from core.attributesFile and from a committed root .gitattributes; ident; export-ignore from a committed
root .gitattributes and from .git/info/attributes; a smudge filter on the overlay configured locally; core.symlinks=false;
core.fileMode=false; copying the checkout without dot-entries; merging a legacy branch that added a classification to
governance/project; cherry-picking the migration onto a diverged legacy branch; format-patch/am of the migration; a superproject
with the RoT-1 project as a submodule.
Usage: gitops7.py <trees.raw.json> <out-dir>
"""
import json, os, shutil, subprocess, sys, zipfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa
import yaml


def main():
    T = json.load(open(sys.argv[1]))
    OUT = os.path.abspath(sys.argv[2])
    os.makedirs(OUT, exist_ok=True)
    D = os.path.join(T["scratch"], "gitops7")
    os.makedirs(D)
    rcs, R7, L0 = T["rcs"], T["trees"]["R7"], T["trees"]["L0"]
    HEAD, PRE = T["R7"]["head"], T["R7"]["pre_migration"]
    gh = os.path.join(D, "githome")
    os.makedirs(gh)
    g = lambda cwd, *a, **k: L.git(cwd, *a, home=gh, **k)
    trees, facts = {}, {}

    def kernel_crlf(p):
        kd = os.path.join(p, "governance/trust/kernel")
        return any(b"\r\n" in open(os.path.join(dp, n), "rb").read() for dp, dn, fn in os.walk(kd) for n in fn) if os.path.isdir(kd) else None

    def record(name, p, note="", record=None):
        st = L.state_r7(p, record, None, rcs)
        occ_tracked = None
        if L.kind(os.path.join(p, ".git")) != "absent":
            occ_tracked = ".governance-runtime/migration" in g(p, "ls-files", ".governance-runtime", check=False).stdout.split()
        trees[name] = p
        facts[name] = {"state": st["state"], "by_reading": st["by_reading"], "reasons": st["reasons"], "reports": st["reports"], "kernel_tampered": st.get("kernel_tampered"),
                       "classifications": L.classifications(p), "occupation_tracked": occ_tracked, "kernel_crlf": kernel_crlf(p), "note": note}

    def op(name, fn):
        try:
            fn(name)
        except Exception as e:  # noqa: BLE001
            facts[name] = {"error": repr(e)[:400]}

    P = lambda n: os.path.join(D, n)

    op("CLONE", lambda n: (g(D, "clone", "-q", R7, P(n)), record(n, P(n))))
    op("SHALLOW", lambda n: (g(D, "clone", "-q", "--depth", "1", "file://" + R7, P(n)), record(n, P(n))))
    op("PARTIAL_CLONE", lambda n: (g(D, "clone", "-q", "--filter=blob:none", "file://" + R7, P(n)), record(n, P(n))))

    def bundle(n):
        b = P("r7.bundle"); g(R7, "bundle", "create", b, "--all"); g(D, "clone", "-q", b, P(n)); record(n, P(n))
    op("BUNDLE_CLONE", bundle)

    def archive_tar(n):
        os.makedirs(P(n)); g(R7, "archive", "--format=tar", "-o", P("a.tar"), "HEAD"); subprocess.run(["tar", "-xf", P("a.tar"), "-C", P(n)], check=True); record(n, P(n), "no .git")
    op("ARCHIVE_TAR", archive_tar)

    def archive_zip(n):
        os.makedirs(P(n)); g(R7, "archive", "--format=zip", "-o", P("a.zip"), "HEAD")
        with zipfile.ZipFile(P("a.zip")) as z:
            z.extractall(P(n))
        record(n, P(n), "zip extracted with python zipfile")
    op("ARCHIVE_ZIP", archive_zip)

    def sparse_cone(n):
        g(D, "clone", "-q", "--no-checkout", R7, P(n)); g(P(n), "sparse-checkout", "init", "--cone"); g(P(n), "sparse-checkout", "set", "governance"); g(P(n), "checkout", "-q"); record(n, P(n))
    op("SPARSE_CONE", sparse_cone)

    def sparse_noncone(n):
        g(D, "clone", "-q", "--no-checkout", R7, P(n)); g(P(n), "sparse-checkout", "init", "--no-cone")
        open(os.path.join(P(n), ".git/info/sparse-checkout"), "w").write("/*\n!/spec/audits/GOVERNANCE-ADOPTION\n!/.governance-runtime/migration\n")
        g(P(n), "checkout", "-q", check=False); record(n, P(n))
    op("SPARSE_NONCONE", sparse_noncone)

    def noncone_legacy_project(n):
        g(D, "clone", "-q", "--no-checkout", R7, P(n)); g(P(n), "sparse-checkout", "init", "--no-cone")
        open(os.path.join(P(n), ".git/info/sparse-checkout"), "w").write("/governance/project/\n/product/\n/docs/\n/spec/\n/.gitignore\n")
        g(P(n), "checkout", "-q", PRE, check=False)
        record(n, P(n), "legacy (pre-migration) commit, only governance/project, product, docs, spec checked out")
    op("NONCONE_LEGACY_PROJECT_ONLY", noncone_legacy_project)

    def clean_clone(n):
        g(D, "clone", "-q", R7, P(n)); g(P(n), "clean", "-fdx"); record(n, P(n))
    op("CLEAN_FDX_CLONE", clean_clone)

    def clean_machine(n):
        shutil.copytree(R7, P(n), symlinks=True); g(P(n), "clean", "-fdx")
        record(n, P(n), "clean -fdx on the installed machine (ignored transaction area, snapshots, legacy quarantine removed)")
    op("CLEAN_FDX_MACHINE", clean_machine)

    def stash_u(n):
        g(D, "clone", "-q", R7, P(n)); open(os.path.join(P(n), "governance/trust/STRAY"), "w").write("x")
        g(P(n), "stash", "-u", check=False); g(P(n), "stash", "pop", check=False)
        if L.kind(os.path.join(P(n), "governance/trust/STRAY")) == "file":
            os.unlink(os.path.join(P(n), "governance/trust/STRAY"))
        record(n, P(n))
    op("STASH_U_POP", stash_u)

    def stash_plain(n):
        g(D, "clone", "-q", R7, P(n)); open(os.path.join(P(n), "governance/project"), "w").write("edited occupation\n")
        g(P(n), "stash", check=False); record(n, P(n), "occupation edited then stashed (no pop)")
    op("STASH_PLAIN", stash_plain)

    def worktree(n):
        b = P("WTB"); g(D, "clone", "-q", R7, b); g(b, "worktree", "add", "-q", P(n), "HEAD"); record(n, P(n))
    op("WORKTREE", worktree)

    def worktree_pre(n):
        b = P("WTB2"); g(D, "clone", "-q", R7, b); g(b, "worktree", "add", "-q", "--detach", P(n), PRE); record(n, P(n), "worktree of the pre-migration commit beside a RoT-1 checkout")
    op("WORKTREE_PREMIGRATION", worktree_pre)

    def checkout_back(n):
        g(D, "clone", "-q", R7, P(n)); g(P(n), "checkout", "-q", PRE); g(P(n), "checkout", "-q", HEAD); record(n, P(n))
    op("CHECKOUT_BACK", checkout_back)
    op("CHECKOUT_PRE", lambda n: (g(D, "clone", "-q", R7, P(n)), g(P(n), "checkout", "-q", PRE), record(n, P(n))))
    op("RESTORE_PRE_GOV", lambda n: (g(D, "clone", "-q", R7, P(n)), g(P(n), "restore", "--source", PRE, "--", "governance", check=False), record(n, P(n))))

    def reset_back(n):
        g(D, "clone", "-q", R7, P(n)); g(P(n), "reset", "-q", "--hard", PRE); os.makedirs(os.path.join(P(n), "governance/kernel/local"), exist_ok=True)
        open(os.path.join(P(n), "governance/kernel/local/untracked.md"), "w").write("untracked in legacy kernel dir\n")
        g(P(n), "reset", "-q", "--hard", HEAD, check=False); record(n, P(n), "reset --hard to pre-migration, untracked file under governance/kernel/, reset --hard back")
    op("RESET_HARD_PRE_BACK_UNTRACKED", reset_back)

    def idiom(work, home=None, env_extra=None):
        listed = L.git(work, "ls-files", "-ci", "--exclude-standard", home=home or gh, env_extra=env_extra).stdout.split()
        for x in listed:
            L.git(work, "rm", "-q", "--cached", x, home=home or gh, check=False)
        L.git(work, "commit", "-q", "--allow-empty", "-m", "untrack ignored", home=home or gh)
        return listed

    def untrack(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); l = idiom(w); g(D, "clone", "-q", w, P(n)); record(n, P(n), "idiom listed %s" % l)
    op("UNTRACK", untrack)

    def untrack_nosurg(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".gitignore"), "a").write(".governance-runtime/\n"); g(w, "commit", "-qam", "legacy line")
        l = idiom(w); g(D, "clone", "-q", w, P(n)); record(n, P(n), "idiom listed %s" % l)
    op("UNTRACK_NOSURG", untrack_nosurg)

    gx = os.path.join(D, "githome-excl"); os.makedirs(gx)
    open(os.path.join(gx, "excl"), "w").write(".governance-runtime/\n")
    open(os.path.join(gx, ".gitconfig"), "w").write("[core]\n\texcludesFile = %s\n" % os.path.join(gx, "excl"))

    def globalexcl(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); l = idiom(w, home=gx); g(D, "clone", "-q", w, P(n)); record(n, P(n), "idiom listed %s" % l)
    op("GLOBALEXCL", globalexcl)

    def infoexcl(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".git/info/exclude"), "a").write(".governance-runtime/\n")
        l = idiom(w); g(D, "clone", "-q", w, P(n)); record(n, P(n), "idiom listed %s" % l)
    op("INFOEXCL", infoexcl)

    def rm_cached_add_all(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w)
        L.git(w, "rm", "-r", "-q", "--cached", ".", home=gx); L.git(w, "add", ".", home=gx); L.git(w, "commit", "-q", "--allow-empty", "-m", "renormalise index", home=gx)
        g(D, "clone", "-q", w, P(n)); record(n, P(n), "`git rm -r --cached . && git add .` under core.excludesFile .governance-runtime/")
    op("RM_CACHED_ADD_ALL_GLOBALEXCL", rm_cached_add_all)

    def skip_worktree(n):
        g(D, "clone", "-q", R7, P(n)); g(P(n), "update-index", "--skip-worktree", ".governance-runtime/migration")
        os.unlink(os.path.join(P(n), ".governance-runtime/migration")); st = g(P(n), "status", "--porcelain").stdout
        record(n, P(n), "skip-worktree then local deletion; status shows %r" % st.strip())
    op("SKIP_WORKTREE_DELETE", skip_worktree)

    def persisted(p, **kv):
        for k, v in kv.items():
            g(p, "config", k, v)

    def autocrlf(n):
        g(D, "clone", "-q", "--no-checkout", R7, P(n)); persisted(P(n), **{"core.autocrlf": "true"}); g(P(n), "checkout", "-q", "HEAD", "--", "."); record(n, P(n))
    op("AUTOCRLF", autocrlf)

    def textauto(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".gitattributes"), "w").write("* text=auto\n"); g(w, "add", ".gitattributes"); g(w, "commit", "-qm", "ta")
        g(D, "clone", "-q", "--no-checkout", w, P(n)); persisted(P(n), **{"core.eol": "crlf"}); g(P(n), "checkout", "-q", "HEAD", "--", "."); record(n, P(n))
    op("TEXTAUTO_EOLCRLF", textauto)

    def texteol(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".gitattributes"), "w").write("* text eol=crlf\n"); g(w, "add", ".gitattributes"); g(w, "commit", "-qm", "te")
        g(D, "clone", "-q", w, P(n)); record(n, P(n))
    op("TEXTEOL_CRLF", texteol)

    def infoattr(n, text="* text\n", conv=True):
        g(D, "clone", "-q", "--no-checkout", R7, P(n))
        if conv:
            persisted(P(n), **{"core.autocrlf": "true"})
        os.makedirs(os.path.join(P(n), ".git/info"), exist_ok=True); open(os.path.join(P(n), ".git/info/attributes"), "w").write(text)
        g(P(n), "checkout", "-q", "HEAD", "--", ".", check=False); record(n, P(n), repr(text))
    op("INFOATTR", lambda n: infoattr(n))
    op("INFOATTR_NOCONV", lambda n: infoattr(n, conv=False))
    op("INFOATTR_WTE", lambda n: infoattr(n, "*.yaml working-tree-encoding=UTF-16LE\n*.md working-tree-encoding=UTF-16LE\n", conv=False))
    op("INFOATTR_IDENT", lambda n: infoattr(n, "* ident\n", conv=False))

    def global_attr(n, text):
        home = os.path.join(D, "home-" + n); os.makedirs(home)
        open(os.path.join(home, "attrs"), "w").write(text)
        open(os.path.join(home, ".gitconfig"), "w").write("[core]\n\tattributesFile = %s\n\tautocrlf = true\n" % os.path.join(home, "attrs"))
        L.git(D, "clone", "-q", R7, P(n), home=home); record(n, P(n), "core.attributesFile %r + autocrlf" % text)
    op("GLOBAL_ATTRFILE_EOLCRLF", lambda n: global_attr(n, "* text eol=crlf\n"))
    op("GLOBAL_ATTRFILE_WTE", lambda n: global_attr(n, "*.yaml working-tree-encoding=UTF-16LE\n"))

    def root_attr_wte(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".gitattributes"), "w").write("*.yaml working-tree-encoding=UTF-16LE\n"); g(w, "add", ".gitattributes"); g(w, "commit", "-qm", "wte")
        g(D, "clone", "-q", w, P(n)); record(n, P(n), "committed root .gitattributes *.yaml working-tree-encoding=UTF-16LE")
    op("ROOT_ATTR_WTE", root_attr_wte)

    def export_ignore_root(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w)
        open(os.path.join(w, ".gitattributes"), "w").write("governance/kernel export-ignore\n.governance-runtime/migration export-ignore\ngovernance/trust/state/** export-ignore\n")
        g(w, "add", ".gitattributes"); g(w, "commit", "-qm", "export-ignore"); os.makedirs(P(n))
        g(w, "archive", "--format=tar", "-o", P(n + ".tar"), "HEAD"); subprocess.run(["tar", "-xf", P(n + ".tar"), "-C", P(n)], check=True); record(n, P(n), "archive after committed export-ignore")
    op("EXPORT_IGNORE_ROOT_ARCHIVE", export_ignore_root)

    def export_ignore_info(n):
        w = P(n + "_W"); g(D, "clone", "-q", R7, w); open(os.path.join(w, ".git/info/attributes"), "w").write("governance/trust/** export-ignore\n")
        os.makedirs(P(n)); g(w, "archive", "--format=tar", "-o", P(n + ".tar"), "HEAD"); subprocess.run(["tar", "-xf", P(n + ".tar"), "-C", P(n)], check=True)
        record(n, P(n), ".git/info/attributes governance/trust/** export-ignore, then archive")
    op("EXPORT_IGNORE_INFO_ARCHIVE", export_ignore_info)

    def smudge(n):
        g(D, "clone", "-q", "--no-checkout", R7, P(n))
        open(os.path.join(P(n), ".git/info/attributes"), "w").write("governance/overlay/DATA_SENSITIVITY.yaml filter=ar21strip\n")
        persisted(P(n), **{"filter.ar21strip.smudge": "grep -v restricted", "filter.ar21strip.clean": "cat"})
        g(P(n), "checkout", "-q", "HEAD", "--", ".", check=False); record(n, P(n), "locally configured smudge filter on the overlay")
    op("SMUDGE_FILTER_OVERLAY", smudge)

    op("IGNORECASE", lambda n: (g(D, "clone", "-q", "--no-checkout", R7, P(n)), persisted(P(n), **{"core.ignorecase": "true"}), g(P(n), "checkout", "-q", "HEAD", "--", "."), record(n, P(n))))
    op("SYMLINKS_FALSE", lambda n: (g(D, "clone", "-q", "--no-checkout", R7, P(n)), persisted(P(n), **{"core.symlinks": "false", "core.fileMode": "false"}), g(P(n), "checkout", "-q", "HEAD", "--", "."), record(n, P(n))))

    def cp_nodot(n):
        os.makedirs(P(n))
        for e in os.listdir(R7):
            if not e.startswith("."):
                s = os.path.join(R7, e)
                (shutil.copytree(s, os.path.join(P(n), e), symlinks=True) if os.path.isdir(s) else shutil.copy2(s, os.path.join(P(n), e)))
        record(n, P(n), "cp -r proj/* dest (no dot-entries at the top level)")
    op("CP_NO_DOTFILES", cp_nodot)

    def merge_legacy_branch(n):
        g(D, "clone", "-q", R7, P(n)); p = P(n)
        g(p, "checkout", "-q", "-b", "legacy-feature", PRE)
        dsp = os.path.join(p, "governance/project/DATA_SENSITIVITY.yaml"); ds = yaml.safe_load(open(dsp)) or {}
        ds.setdefault("classifications", []).append({"pattern": "docs/guide.md", "class": "restricted", "reason": "added on a legacy branch"})
        yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
        os.makedirs(os.path.join(p, "governance/project/plugins"), exist_ok=True); open(os.path.join(p, "governance/project/plugins/new.yaml"), "w").write("plugin_id: new\n")
        g(p, "add", "-A"); g(p, "commit", "-qm", "legacy branch adds a classification and a plugin descriptor")
        g(p, "checkout", "-q", "main" if g(p, "rev-parse", "--verify", "main", check=False).returncode == 0 else "master", check=False)
        g(p, "checkout", "-q", HEAD, check=False)
        m = g(p, "merge", "--no-edit", "legacy-feature", check=False)
        status = g(p, "status", "--porcelain").stdout
        conflicted = bool(m.returncode)
        if conflicted:
            g(p, "checkout", "--ours", "--", ".", check=False); g(p, "add", "-A", check=False); g(p, "commit", "-qm", "resolve keeping ours", check=False)
        ov = os.path.join(p, "governance/overlay/DATA_SENSITIVITY.yaml")
        added = L.kind(ov) == "file" and "docs/guide.md" in open(ov).read()
        record(n, p, "merge rc=%d conflicted=%s status=%r; branch classification in governance/overlay after merge=%s; plugin in overlay=%s" % (
            m.returncode, conflicted, status.strip()[:300], added, L.kind(os.path.join(p, "governance/overlay/plugins/new.yaml")) == "file"))
        facts[n]["branch_classification_reached_overlay"] = added
    op("MERGE_LEGACY_BRANCH", merge_legacy_branch)

    def cherry(n):
        g(D, "clone", "-q", R7, P(n)); p = P(n); g(p, "checkout", "-q", "-b", "legacy-diverged", PRE)
        open(os.path.join(p, "governance/project/NOTES.md"), "w").write("legacy change\n"); g(p, "add", "-A"); g(p, "commit", "-qm", "legacy change")
        c = g(p, "cherry-pick", HEAD, check=False)
        record(n, p, "cherry-pick of the migration commit onto a diverged legacy branch rc=%d %r" % (c.returncode, g(p, "status", "--porcelain").stdout.strip()[:200]))
    op("CHERRY_PICK_MIGRATION", cherry)

    def am(n):
        g(D, "clone", "-q", R7, P(n)); p = P(n); g(p, "checkout", "-q", "-b", "legacy", PRE)
        pd = P(n + "_patch"); os.makedirs(pd); g(R7, "format-patch", "-q", "--binary", "-o", pd, "-1", HEAD)
        a = g(p, "am", "-q", *sorted(os.path.join(pd, x) for x in os.listdir(pd)), check=False)
        record(n, p, "format-patch/am of the migration commit rc=%d" % a.returncode)
    op("FORMAT_PATCH_AM", am)

    def submodule(n):
        sup = P(n + "_SUPER"); os.makedirs(sup); g(sup, "init", "-q")
        g(sup, "-c", "protocol.file.allow=always", "submodule", "add", "-q", R7, "proj", check=False); g(sup, "commit", "-qm", "add submodule", check=False)
        g(D, "clone", "-q", "--recurse-submodules", sup, P(n))
        record(n, os.path.join(P(n), "proj"), "superproject clone --recurse-submodules; the RoT-1 project is a submodule")
        trees[n] = os.path.join(P(n), "proj")
    op("SUBMODULE_RECURSIVE", submodule)

    L.dump({"trees": trees, "facts": facts}, os.path.join(OUT, "gitops7.json"))
    json.dump({"trees": trees}, open(os.path.join(OUT, "gitops7-trees.json"), "w"))
    for k in sorted(facts):
        f = facts[k]
        print(k, f.get("state"), f.get("reasons"), "KT" if f.get("kernel_tampered") else "", f.get("classifications"), f.get("occupation_tracked"), (f.get("note") or f.get("error") or "")[:160])


if __name__ == "__main__":
    main()
