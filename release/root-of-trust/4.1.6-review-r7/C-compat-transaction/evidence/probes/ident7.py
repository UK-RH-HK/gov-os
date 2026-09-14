#!/usr/bin/env python3
"""AR-0021 held-out RV7-C-A05: what can "the Git common-directory identity recorded by the first install on this machine" be?

Text under test (d07d200): `20` §9 "keyed by project_trust_id and a locally recorded repository identity (the Git common-directory
identity recorded by the first install on this machine, never committed) ... A known id at a new path with the same identity
(worktree, moved checkout, bind-mount) inherits ... the same id with another identity (second clone, fork, template copy) is
reported (PROJECT_IDENTITY_MISMATCH)". `18` §5.1 binds honoured journals to it. RT-196 lists the same five cases. PPR7 models the
identity as opaque labels ("git-A", "git-B").

Method (real Git 2.43.0, real filesystems). One repository carrying a lock with a fixed project_trust_id, then every duplication
and relocation an ordinary user performs. For each resulting checkout, compute every identity a conforming implementation could
record from "the Git common directory" without committing anything:
  I1 realpath of `git rev-parse --git-common-dir`
  I2 (st_dev, st_ino) of the common directory
  I3 a random id written by the first install into the common directory (a file under .git/, never committed)
  I4 the root commit id (derivable from the repository, not "recorded"; included as a control)
and compare "same as the original" with the classification `20` §9 requires. Output: per identity candidate, the cases where
it contradicts `20` §9 (a case the text calls same that the candidate calls different: availability/fail closed; a case the text
calls different that the candidate calls same: shared record = the review r6 id-only failure).
Usage: ident7.py <scratch-dir>   (JSON on stdout)
"""
import json, os, shutil, subprocess, sys, uuid
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa

S = os.path.abspath(sys.argv[1])
os.makedirs(S, exist_ok=True)
GH = os.path.join(S, "githome")


def g(cwd, *a, check=True):
    return L.git(cwd, *a, home=GH, check=check)


def common(p):
    r = g(p, "rev-parse", "--git-common-dir", check=False)
    if r.returncode:
        return None
    c = r.stdout.strip()
    return os.path.realpath(c if os.path.isabs(c) else os.path.join(p, c))


def ident(p):
    c = common(p)
    if c is None:
        return {"I1": None, "I2": None, "I3": None, "I4": None}
    st = os.stat(c)
    rid = os.path.join(c, "gov-repository-identity")
    root = g(p, "rev-list", "--max-parents=0", "HEAD", check=False).stdout.split()
    return {"I1": c, "I2": [st.st_dev, st.st_ino], "I3": open(rid).read().strip() if os.path.isfile(rid) else None, "I4": root[0] if root else None,
            "ptid": (json.load(open(os.path.join(p, "governance/trust/framework.lock"))).get("project_trust_id") if os.path.isfile(os.path.join(p, "governance/trust/framework.lock")) else None)}


orig = os.path.join(S, "work", "proj")
os.makedirs(os.path.join(orig, "governance", "trust"))
json.dump({"project_trust_id": "ptid-ar21-fixed"}, open(os.path.join(orig, "governance/trust/framework.lock"), "w"))
open(os.path.join(orig, "README.md"), "w").write("x\n")
g(orig, "init", "-q"); g(orig, "add", "-A"); g(orig, "commit", "-q", "-m", "c1")
open(os.path.join(common(orig), "gov-repository-identity"), "w").write(str(uuid.UUID(int=0x21)))   # I3 recorded by the "first install"
base = ident(orig)
cases, facts = {}, {}
# pack says SAME
wt = os.path.join(S, "work", "proj-wt"); g(orig, "worktree", "add", "-q", wt, "HEAD"); cases["worktree"] = ("same", wt)
lnk = os.path.join(S, "work", "proj-symlinked-path"); os.symlink(orig, lnk); cases["same_checkout_via_symlinked_path"] = ("same", lnk)
# moved checkout (same filesystem): done on a copy made by rename of a fresh clone so that `orig` stays
mv_src = os.path.join(S, "work", "tomove"); g(os.path.join(S, "work"), "clone", "-q", orig, mv_src)
open(os.path.join(common(mv_src), "gov-repository-identity"), "w").write(str(uuid.UUID(int=0x77)))
before_move = ident(mv_src)
mv_dst = os.path.join(S, "moved", "tomove"); os.makedirs(os.path.dirname(mv_dst)); os.rename(mv_src, mv_dst)
after_move = ident(mv_dst)
facts["moved_same_fs"] = {"before": before_move, "after": after_move}
# moved across filesystems (/dev/shm tmpfs when available)
xfs = None
if os.path.isdir("/dev/shm") and os.access("/dev/shm", os.W_OK) and os.stat("/dev/shm").st_dev != os.stat(S).st_dev:
    xs = os.path.join(S, "work", "toxfs"); g(os.path.join(S, "work"), "clone", "-q", orig, xs)
    open(os.path.join(common(xs), "gov-repository-identity"), "w").write(str(uuid.UUID(int=0x78)))
    b = ident(xs)
    xd = os.path.join("/dev/shm", "ar21-ident7-%d" % os.getpid(), "toxfs")
    os.makedirs(os.path.dirname(xd))
    shutil.move(xs, xd)
    a = ident(xd)
    facts["moved_cross_fs"] = {"before": b, "after": a}
    shutil.move(xd, os.path.join(S, "work", "toxfs-back"))
    os.rmdir(os.path.dirname(xd))
    xfs = True
# bind mount (user+mount namespace)
bm = subprocess.run(["unshare", "-rm", "sh", "-c", "mkdir -p %s && mount --bind %s %s && git -C %s rev-parse --git-common-dir && stat -c '%%d %%i' %s/.git" % (
    os.path.join(S, "mnt"), orig, os.path.join(S, "mnt"), os.path.join(S, "mnt"), os.path.join(S, "mnt"))], capture_output=True, text=True,
    env={"PATH": L.CLEANPATH, "HOME": GH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.path.join(GH, ".gitconfig")})
facts["bind_mount"] = {"rc": bm.returncode, "stdout": bm.stdout.strip().splitlines(), "stderr": bm.stderr.strip()[-200:],
                       "orig_I2": base["I2"], "note": "inside the namespace the path differs; (st_dev, st_ino) as printed"}
# pack says DIFFERENT
clone = os.path.join(S, "work", "second-clone"); g(os.path.join(S, "work"), "clone", "-q", orig, clone); cases["second_clone"] = ("different", clone)
fork = os.path.join(S, "work", "fork"); g(os.path.join(S, "work"), "clone", "-q", "--bare", orig, fork + ".git"); g(os.path.join(S, "work"), "clone", "-q", fork + ".git", fork); cases["fork"] = ("different", fork)
tmpl_cp = os.path.join(S, "work", "template-copy-cp-a"); shutil.copytree(orig, tmpl_cp, symlinks=True); cases["template_copy_by_directory_copy"] = ("different", tmpl_cp)
tmpl_tar = os.path.join(S, "work", "backup-restored-elsewhere"); subprocess.run(["sh", "-c", "tar -C %s -cf - . | (mkdir -p %s && tar -C %s -xf -)" % (orig, tmpl_tar, tmpl_tar)], check=True)
cases["tar_copy_to_new_directory"] = ("different", tmpl_tar)
tmpl_new = os.path.join(S, "work", "template-reinit"); shutil.copytree(orig, tmpl_new, symlinks=True, ignore=shutil.ignore_patterns(".git"))
g(tmpl_new, "init", "-q"); g(tmpl_new, "add", "-A"); g(tmpl_new, "commit", "-q", "-m", "from template"); cases["template_reinit_new_history"] = ("different", tmpl_new)
shared = os.path.join(S, "work", "clone-shared"); g(os.path.join(S, "work"), "clone", "-q", "--shared", orig, shared); cases["clone_shared_alternates"] = ("different", shared)
# delete and re-clone a fork at the original's path (a user replacing a checkout)
reuse_parent = os.path.join(S, "reuse"); os.makedirs(reuse_parent)
r1 = os.path.join(reuse_parent, "p"); g(reuse_parent, "clone", "-q", orig, r1)
open(os.path.join(common(r1), "gov-repository-identity"), "w").write(str(uuid.UUID(int=0x99)))
first = ident(r1)
shutil.rmtree(r1)
g(reuse_parent, "clone", "-q", fork + ".git", r1)
second = ident(r1)
facts["delete_and_reclone_other_repository_at_same_path"] = {"first": first, "second": second}

table = {}
for name, (want, path) in cases.items():
    i = ident(path)
    table[name] = {"pack_requires": want, "identity": i, "same_as_original": {k: (i[k] == base[k] and i[k] is not None) for k in ("I1", "I2", "I3", "I4")}}
table["moved_checkout_same_fs"] = {"pack_requires": "same", "identity": after_move,
                                   "same_as_original": {k: after_move[k] == before_move[k] and after_move[k] is not None for k in ("I1", "I2", "I3", "I4")}}
if xfs:
    table["moved_checkout_cross_fs"] = {"pack_requires": "same", "identity": facts["moved_cross_fs"]["after"],
                                        "same_as_original": {k: facts["moved_cross_fs"]["after"][k] == facts["moved_cross_fs"]["before"][k] and facts["moved_cross_fs"]["before"][k] is not None for k in ("I1", "I2", "I3", "I4")}}
f = facts["delete_and_reclone_other_repository_at_same_path"]
table["other_repository_recloned_at_same_path"] = {"pack_requires": "different", "identity": f["second"],
                                                    "same_as_original": {k: f["second"][k] == f["first"][k] and f["first"][k] is not None for k in ("I1", "I2", "I3", "I4")}}
contradictions = {}
for k in ("I1", "I2", "I3", "I4"):
    c = []
    for name, row in table.items():
        same = row["same_as_original"][k]
        if row["pack_requires"] == "same" and not same:
            c.append({"case": name, "effect": "text says same identity; candidate says different -> PROJECT_IDENTITY_MISMATCH (fail closed; E10/strength not inherited)"})
        if row["pack_requires"] == "different" and same:
            c.append({"case": name, "effect": "text says different identity; candidate says same -> one shared per-project record (review r6 id-keyed failure)"})
    contradictions[k] = c
out = {"probe": "ident7 (AR-0021; RV7-C-A05)", "original": base, "cases": table, "facts": facts, "contradictions_by_candidate": contradictions,
       "every_candidate_contradicts_the_text": all(contradictions[k] for k in contradictions),
       "ptid_identical_in_every_copy": all(row["identity"].get("ptid") in ("ptid-ar21-fixed", None) for row in table.values())}
print(L.scrub(json.dumps(out, indent=1, sort_keys=True)).replace(S, "<s>"))
