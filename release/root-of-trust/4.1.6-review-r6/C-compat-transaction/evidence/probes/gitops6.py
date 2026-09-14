#!/usr/bin/env python3
"""AR-0017 layout durability on the revision-6 layout (real Git). Every way a project reaches a machine or is modified by
ordinary tools and legacy remedies, then the revision-6 installation state (`18` §9.1, incl. the `.gitattributes` member) and
the `18` §6.1 kernel-tampered check. Each op keeps its resulting tree for the matrix (P-GIT) and records its state.

Operations: fresh clone; shallow (--depth 1); partial (--filter=blob:none); cone and non-cone sparse checkout; git archive
round-trip; clean -fdx; stash -u then pop; worktree add; checkout across the migration commit and back; checkout of the
pre-migration commit; git restore --source <pre> -- governance; the untracking idiom under the project .gitignore surgery
(control), under a retained legacy directory-ignore line, under a user core.excludesFile, and under .git/info/exclude, each
carrying `.governance-runtime/`; a `.git/info/attributes` `* text` override under autocrlf; core.autocrlf=true clone; a
project `* text=auto` + core.eol=crlf clone; a project `* text eol=crlf` clone; case-insensitive emulation
(core.ignorecase=true) of an occupation-vs-kernel name collision.
Usage: gitops6.py <trees.json> <out-dir>
"""
import json, os, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c6lib as L  # noqa


def main():
    T = json.load(open(sys.argv[1]))
    OUT = os.path.abspath(sys.argv[2])
    os.makedirs(OUT, exist_ok=True)
    D = os.path.join(T["scratch"], "gitops")
    if os.path.exists(D):
        shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    rcs = T["rcs"]
    R6 = T["trees"]["R6"]
    gh = os.path.join(D, "githome")
    os.makedirs(gh)

    def g(cwd, *a, **k):
        return L.git(cwd, *a, home=gh, **k)

    def setcfg(repo, **kv):
        """Persist config INTO the cloned repo (a command-level `git -c` is not written to the repo and would not reach a
        later checkout). `git config` in the repo writes .git/config."""
        for k, v in kv.items():
            g(repo, "config", k, v)

    trees, facts = {}, {}

    def record(name, path, note=""):
        st = L.state_r6(path, rcs=rcs)
        trees[name] = path
        facts[name] = {"state": st["state"], "reasons": st["reasons"], "reports": st["reports"],
                       "kernel_tampered": st.get("kernel_tampered"), "note": note}

    origin = R6
    # 1 fresh clone
    p = os.path.join(D, "CLONE"); g(D, "clone", "-q", origin, p); record("CLONE", p)
    # 2 shallow
    p = os.path.join(D, "SHALLOW"); g(D, "clone", "-q", "--depth", "1", "file://" + origin, p); record("SHALLOW", p)
    # 3 partial
    p = os.path.join(D, "PARTIAL_CLONE"); g(D, "clone", "-q", "--filter=blob:none", "file://" + origin, p); record("PARTIAL_CLONE", p)
    # 4 cone sparse governance
    p = os.path.join(D, "SPARSE_CONE"); g(D, "clone", "-q", "--no-checkout", origin, p)
    g(p, "sparse-checkout", "init", "--cone"); g(p, "sparse-checkout", "set", "governance"); g(p, "checkout", "-q")
    record("SPARSE_CONE", p, "cone set governance")
    # 5 non-cone sparse excluding occupation roots
    p = os.path.join(D, "SPARSE_NONCONE"); g(D, "clone", "-q", "--no-checkout", origin, p)
    g(p, "sparse-checkout", "init", "--no-cone")
    open(os.path.join(p, ".git/info/sparse-checkout"), "w").write("/*\n!/spec/audits/GOVERNANCE-ADOPTION\n!/.governance-runtime/migration\n")
    g(p, "checkout", "-q", check=False); record("SPARSE_NONCONE", p, "non-cone excludes 2 occupation roots")
    # 6 archive round trip
    p = os.path.join(D, "ARCHIVE"); os.makedirs(p)
    g(R6, "archive", "--format=tar", "-o", os.path.join(D, "a.tar"), "HEAD")
    import subprocess
    subprocess.run(["tar", "-xf", os.path.join(D, "a.tar"), "-C", p], check=True)
    record("ARCHIVE", p, "git archive HEAD | tar -x (no .git)")
    # 7 clean -fdx on a clone
    p = os.path.join(D, "CLEAN"); g(D, "clone", "-q", origin, p); g(p, "clean", "-fdx"); record("CLEAN", p)
    # 8 stash -u then pop, with an untracked stray added
    p = os.path.join(D, "STASH"); g(D, "clone", "-q", origin, p)
    open(os.path.join(p, "governance/trust/STRAY"), "w").write("x")
    g(p, "stash", "-u", check=False); g(p, "stash", "pop", check=False)
    if L.kind(os.path.join(p, "governance/trust/STRAY")) == "file":
        os.unlink(os.path.join(p, "governance/trust/STRAY"))
    record("STASH", p, "stash -u/pop")
    # 9 worktree add
    wtbase = os.path.join(D, "WT_BASE"); g(D, "clone", "-q", origin, wtbase)
    p = os.path.join(D, "WORKTREE"); g(wtbase, "worktree", "add", "-q", p, "HEAD"); record("WORKTREE", p)
    # 10 checkout across migration and back
    p = os.path.join(D, "CHECKOUT_BACK"); g(D, "clone", "-q", origin, p)
    g(p, "checkout", "-q", T["R6"]["pre_migration"]); g(p, "checkout", "-q", T["R6"]["head"]); record("CHECKOUT_BACK", p)
    # 11 checkout pre-migration
    p = os.path.join(D, "CHECKOUT_PRE"); g(D, "clone", "-q", origin, p); g(p, "checkout", "-q", T["R6"]["pre_migration"])
    record("CHECKOUT_PRE", p, "pre-migration legacy layout")
    # 12 git restore --source <pre> -- governance
    p = os.path.join(D, "RESTORE_PRE_GOV"); g(D, "clone", "-q", origin, p)
    g(p, "restore", "--source", T["R6"]["pre_migration"], "--", "governance", check=False); record("RESTORE_PRE_GOV", p, "restore pre governance")
    # 13 untracking idiom control (project .gitignore surgery only)
    def idiom(work, extra_home=None, extra_env=None, cfg=()):
        listed = L.git(work, "ls-files", "-ci", "--exclude-standard", home=extra_home or gh, extra_env=extra_env).stdout.split()
        for x in listed:
            L.git(work, "rm", "-q", "--cached", x, home=extra_home or gh, extra_env=extra_env, check=False)
        L.git(work, "commit", "-q", "--allow-empty", "-m", "untrack ignored", home=extra_home or gh, extra_env=extra_env)
        return listed
    w = os.path.join(D, "UNTRACK_WORK"); g(D, "clone", "-q", origin, w); listed = idiom(w)
    p = os.path.join(D, "UNTRACK"); g(D, "clone", "-q", w, p); record("UNTRACK", p, "surgery only; idiom listed %s" % listed)
    # 14 retained legacy directory-ignore line (no surgery)
    w = os.path.join(D, "NOSURG_WORK"); g(D, "clone", "-q", origin, w)
    open(os.path.join(w, ".gitignore"), "a").write(".governance-runtime/\n")
    g(w, "add", ".gitignore"); g(w, "commit", "-q", "-m", "retain legacy ignore line")
    listed = idiom(w)
    p = os.path.join(D, "UNTRACK_NOSURG"); g(D, "clone", "-q", w, p); record("UNTRACK_NOSURG", p, "legacy dir-ignore retained; idiom listed %s" % listed)
    # 15 user core.excludesFile
    gh2 = os.path.join(D, "githome-excl"); os.makedirs(gh2)
    open(os.path.join(gh2, "excl"), "w").write(".governance-runtime/\n")
    open(os.path.join(gh2, ".gitconfig"), "w").write("[core]\n\texcludesFile = %s\n" % os.path.join(gh2, "excl"))
    w = os.path.join(D, "GLOBALEXCL_WORK"); g(D, "clone", "-q", origin, w)
    ci = L.git(w, "check-ignore", "--no-index", "-v", ".governance-runtime/migration", home=gh2, check=False)
    listed = idiom(w, extra_home=gh2)
    p = os.path.join(D, "GLOBALEXCL"); g(D, "clone", "-q", w, p); record("GLOBALEXCL", p, "core.excludesFile; check-ignore=%r; idiom listed %s" % (ci.stdout.strip(), listed))
    # 16 .git/info/exclude
    w = os.path.join(D, "INFOEXCL_WORK"); g(D, "clone", "-q", origin, w)
    open(os.path.join(w, ".git/info/exclude"), "a").write(".governance-runtime/\n")
    ci = g(w, "check-ignore", "--no-index", "-v", ".governance-runtime/migration", check=False)
    listed = idiom(w)
    p = os.path.join(D, "INFOEXCL"); g(D, "clone", "-q", w, p); record("INFOEXCL", p, ".git/info/exclude; check-ignore=%r; idiom listed %s" % (ci.stdout.strip(), listed))
    def kernel_has_crlf(repo):
        kd = os.path.join(repo, "governance", "trust", "kernel")
        for dp, dns, fns in os.walk(kd):
            for n in fns:
                if b"\r\n" in open(os.path.join(dp, n), "rb").read():
                    return True
        return False

    # 17 autocrlf clone (config persisted into the repo, then re-materialise the working tree)
    p = os.path.join(D, "AUTOCRLF"); g(D, "clone", "-q", "--no-checkout", origin, p); setcfg(p, **{"core.autocrlf": "true"})
    g(p, "checkout", "-q", "HEAD", "--", "."); facts_crlf = kernel_has_crlf(p)
    record("AUTOCRLF", p, "core.autocrlf=true (persisted); kernel_crlf_on_disk=%s" % facts_crlf)
    # 18 project * text=auto + core.eol=crlf
    w = os.path.join(D, "TEXTAUTO_WORK"); g(D, "clone", "-q", origin, w)
    open(os.path.join(w, ".gitattributes"), "w").write("* text=auto\n")
    g(w, "add", ".gitattributes"); g(w, "commit", "-q", "-m", "text=auto")
    p = os.path.join(D, "TEXTAUTO_EOLCRLF"); g(D, "clone", "-q", "--no-checkout", w, p); setcfg(p, **{"core.eol": "crlf"})
    g(p, "checkout", "-q", "HEAD", "--", "."); record("TEXTAUTO_EOLCRLF", p, "* text=auto + core.eol=crlf; kernel_crlf_on_disk=%s" % kernel_has_crlf(p))
    # 19 project * text eol=crlf
    w = os.path.join(D, "TEXTEOL_WORK"); g(D, "clone", "-q", origin, w)
    open(os.path.join(w, ".gitattributes"), "w").write("* text eol=crlf\n")
    g(w, "add", ".gitattributes"); g(w, "commit", "-q", "-m", "text eol=crlf")
    p = os.path.join(D, "TEXTEOL_CRLF"); g(D, "clone", "-q", w, p); record("TEXTEOL_CRLF", p, "* text eol=crlf; kernel_crlf_on_disk=%s" % kernel_has_crlf(p))
    # 20 .git/info/attributes override (stated condition): config persisted, so the override actually converts
    p = os.path.join(D, "INFOATTR"); g(D, "clone", "-q", "--no-checkout", origin, p); setcfg(p, **{"core.autocrlf": "true"})
    os.makedirs(os.path.join(p, ".git/info"), exist_ok=True)
    open(os.path.join(p, ".git/info/attributes"), "w").write("* text\n")
    g(p, "checkout", "-q", "HEAD", "--", "."); record("INFOATTR", p, ".git/info/attributes '* text' + autocrlf (persisted); kernel_crlf_on_disk=%s" % kernel_has_crlf(p))
    # 20b control: same override WITHOUT autocrlf (info/attributes text but no crlf conversion source) — should stay COMPLETE
    p = os.path.join(D, "INFOATTR_NOCONV"); g(D, "clone", "-q", "--no-checkout", origin, p)
    os.makedirs(os.path.join(p, ".git/info"), exist_ok=True)
    open(os.path.join(p, ".git/info/attributes"), "w").write("* text\n")
    g(p, "checkout", "-q", "HEAD", "--", "."); record("INFOATTR_NOCONV", p, "info/attributes '* text' but no crlf conversion; kernel_crlf_on_disk=%s" % kernel_has_crlf(p))
    # 21 case-insensitive emulation
    p = os.path.join(D, "IGNORECASE"); g(D, "clone", "-q", "--no-checkout", origin, p); setcfg(p, **{"core.ignorecase": "true"})
    g(p, "checkout", "-q", "HEAD", "--", "."); record("IGNORECASE", p, "core.ignorecase=true clone")

    L.dump({"trees": trees, "facts": facts}, os.path.join(OUT, "gitops6.json"))
    json.dump({"trees": trees}, open(os.path.join(OUT, "gitops6-trees.json"), "w"))
    for k in sorted(facts):
        print(k, facts[k]["state"], facts[k]["reasons"], ("KT" if facts[k]["kernel_tampered"] else ""), facts[k]["note"][:70])


if __name__ == "__main__":
    main()
