#!/usr/bin/env python3
"""AR-0021 held-out transaction attacks on the revision-7 first-install layout migration and recovery (real legacy 4.1.5, real Git).

Text under test (d07d200):
  `26` §7: steps 1 quarantine, 2 move kernel, overlay, views and adoption evidence, 3 write governance/trust/**, 4 occupation,
  5 ignore rule, 6 strength vector, 7 ledger; "Each step above is a journal phase ... with an idempotent redo record and an undo
  record written before the step, including where the legacy kernel, lock and residue were moved; an intent phase precedes
  RENAME_EXCHANGE; recovery rolls the layout forward only when every redo record is complete and the exchange happened, and
  otherwise undoes to exactly the pre-transaction legacy layout. No recovered prefix is ABSENT or PARTIAL."
  `18` §5.3: phases layout-intent, layout-quarantine-residue, layout-move-kernel, layout-move-lock, layout-occupation,
  layout-ignore-rule; exchange-intent. (No phase names the overlay, views or adoption-evidence moves.)
  `18` §5.1: a journal is honoured only if the per-project record lists the TX for this project_trust_id, repository path and
  locally recorded repository identity, and it is untracked.
  `18` §9: IN_TRANSACTION precedence; LAYOUT_MIGRATION_INCOMPLETE; ABSENT requires no governance/overlay, no governance/views.
  `20` §6: uninstall "moves governance/trust and the occupation entries into trust-tx/<TX>/removed/ ... and leaves the result ABSENT".
  `09`/`26` R-INIT-9: RoT-1 init refuses (or evaluates) only on a tree holding governance/overlay or governance/views.

The architect's crashmig7 crashes only AFTER each step on an untouched tree, and models roll-forward without changing the tree. This
probe adds (i) a crash between the phase write and the step, (ii) ordinary and legacy operations between the crash and `gov recover`,
(iii) the honouring condition for a first install, (iv) two literal recovery readings: L = rename-based undo that skips a step whose
source is gone (the reading crashmig7 implements) and S = undo that refuses when a destination exists or differs (a precondition
check the text does not state), (v) trees that reach ABSENT with classified content under a legacy name, (vi) uninstall's result,
(vii) a shared per-project record updated by two worktrees' transactions without a lock.
Usage: txn7.py <trees.raw.json> <out-dir>
"""
import copy, json, os, shutil, sys, tempfile, threading, fcntl
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa

T = json.load(open(sys.argv[1]))
OUT = os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
S = T["scratch"]
BASE = tempfile.mkdtemp(prefix="txn7-", dir=S)
L0, R7, rcs = T["trees"]["L0"], T["trees"]["R7"], T["rcs"]
TXN = "TX-" + "f1" * 16
GH = os.path.join(BASE, "githome")
os.makedirs(GH)
g = lambda cwd, *a, **k: L.git(cwd, *a, home=GH, **k)
G5 = L.BINS["4.1.5"]

STEPS = [("layout-intent", None), ("layout-quarantine-residue", "quarantine"), ("layout-move-kernel", "kernel"), ("layout-move-lock", "lock"),
         ("(26 §7 step 2, no 18 §5.3 phase) move-overlay", "overlay"), ("(26 §7 step 2) move-views", "views"), ("(26 §7 step 2) move-adoption-evidence", "evidence"),
         ("layout-occupation", "occupation"), ("layout-ignore-rule", "ignore"), ("exchange-intent", None), ("RENAME_EXCHANGE", "exchange")]


def identity(root):
    c = g(root, "rev-parse", "--git-common-dir", check=False).stdout.strip()
    c = c if os.path.isabs(c) else os.path.join(root, c)
    st = os.stat(os.path.realpath(c))
    return [st.st_dev, st.st_ino]


def mv(src, dst):
    if L.kind(src) == "absent":
        return "skip_src_absent"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)
    return "done"


def do_step(d, key, aside):
    gd, rt = os.path.join(d, "governance"), os.path.join(d, ".governance-runtime")
    if key == "quarantine":
        return mv(os.path.join(rt, "update"), os.path.join(rt, "legacy-quarantine", "update"))
    if key == "kernel":
        return mv(os.path.join(gd, "kernel"), os.path.join(aside, "legacy-kernel"))
    if key == "lock":
        return mv(os.path.join(gd, "framework.lock"), os.path.join(aside, "legacy-framework.lock"))
    if key == "overlay":
        return mv(os.path.join(gd, "project"), os.path.join(gd, "overlay"))
    if key == "views":
        return mv(os.path.join(gd, "generated"), os.path.join(gd, "views"))
    if key == "evidence":
        return mv(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(d, "spec/audits/ADOPTION"))
    if key == "occupation":
        for p in ("governance/kernel", "governance/project", "governance/generated", "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration"):
            if L.kind(os.path.join(d, p)) == "absent":
                os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True)
                open(os.path.join(d, p), "w").write(L.SENTINEL + "\n")
        fl = os.path.join(gd, "framework.lock")
        if L.kind(fl) == "absent":
            os.makedirs(fl)
            open(os.path.join(fl, L.OCC_DIR_SENTINEL), "w").write(L.SENTINEL + "\n")
        return "done"
    if key == "ignore":
        gi = os.path.join(d, ".gitignore")
        open(gi, "w").write("/.governance-runtime/*\n!/.governance-runtime/migration\n")
        return "done"
    if key == "exchange":
        return mv(os.path.join(rt, "trust-tx", TXN, "trust.next"), os.path.join(gd, "trust"))
    return "journal_only"


UNDO = {"quarantine": ("mv", ".governance-runtime/legacy-quarantine/update", ".governance-runtime/update"), "kernel": ("mv", "<aside>/legacy-kernel", "governance/kernel"),
        "lock": ("mv", "<aside>/legacy-framework.lock", "governance/framework.lock"), "overlay": ("mv", "governance/overlay", "governance/project"),
        "views": ("mv", "governance/views", "governance/generated"), "evidence": ("mv", "spec/audits/ADOPTION", "spec/audits/GOVERNANCE-ADOPTION"),
        "occupation": ("rm_occ",), "ignore": ("restore_gitignore",), "exchange": ("none",)}


def build(order_n, crash, what="NONE", aside_in_tx=True):
    """Tree after steps[:n] with phase n-1 recorded; crash='mid' means the last phase was written but its step not performed."""
    n = order_n
    d = os.path.join(BASE, "p%02d-%s-%s-%s" % (n, crash, what, "intx" if aside_in_tx else "outside"))
    shutil.copytree(L0, d, symlinks=True)
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TXN)
    os.makedirs(tx)
    shutil.copytree(os.path.join(R7, "governance", "trust"), os.path.join(tx, "trust.next"), symlinks=True)
    aside = os.path.join(tx, "aside") if aside_in_tx else os.path.join(BASE, "aside-" + os.path.basename(d))
    os.makedirs(aside, exist_ok=True)
    gi = os.path.join(d, ".gitignore")
    j = {"operation": "update", "first_install_layout_migration": True, "aside": os.path.relpath(aside, d) if aside_in_tx else aside, "saved_gitignore": open(gi).read() if os.path.exists(gi) else None, "phases": []}
    for i, (phase, key) in enumerate(STEPS[:n]):
        j["phases"].append({"phase": phase, "key": key, "performed": False})
        j["phase"] = phase
        json.dump(j, open(os.path.join(tx, "journal.json"), "w"))
        if crash == "mid" and i == n - 1:
            break
        r = do_step(d, key, aside)
        j["phases"][-1]["performed"] = r
    json.dump(j, open(os.path.join(tx, "journal.json"), "w"))
    rec = {"project_trust_id": "first-install-ptid", "identity": identity(d), "paths": [os.path.realpath(d)], "open_tx": [TXN], "done_tx": []}
    return d, rec


def recover(d, rec, reading):
    """`20` §5 revision 7. reading L: rename-based undo, skip when the source is gone (crashmig7's reading). reading S: refuse when a
    destination exists (or, for the ignore rule, when the file differs from what the step wrote)."""
    st = L.state_r7(d, rec, identity(d) if L.kind(os.path.join(d, ".git")) != "absent" else None, rcs)
    if not st["honoured"]:
        return {"action": "not_honoured", "state": st["state"]}
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TXN)
    j = json.load(open(os.path.join(tx, "journal.json")))
    exchanged = L.kind(os.path.join(d, "governance/trust")) == "dir" and L.kind(os.path.join(tx, "trust.next")) == "absent"
    if exchanged:
        return {"action": "roll_forward_required", "needs": ["migrations from ARO buffers (the ARO is in memory only, 18 §1)", "C3 currency (24 §4.3)",
                                                           "weakening gate for 19 §9 item 5", "per-project record", "ledger"], "tree_changed_by_model": False}
    log = []
    for ph in reversed(j["phases"]):
        key = ph["key"]
        if key is None:
            continue
        u = UNDO[key]
        try:
            if u[0] == "mv":
                src = u[1].replace("<aside>", j["aside"] if os.path.isabs(j["aside"]) else os.path.join(d, j["aside"])) if u[1].startswith("<aside>") else os.path.join(d, u[1])
                dst = os.path.join(d, u[2])
                if key in ("kernel", "lock") and L.kind(dst) != "absent":
                    # occupation removal is undone by the 'occupation' record; anything else at dst was not written by this transaction
                    if reading == "S":
                        return {"action": "refused_precondition", "at": ph["phase"], "dst_kind": L.kind(dst), "log": log}
                if L.kind(src) == "absent":
                    log.append([ph["phase"], "skip_src_absent"])
                    continue
                if L.kind(dst) != "absent":
                    if reading == "S":
                        return {"action": "refused_precondition", "at": ph["phase"], "dst_kind": L.kind(dst), "log": log}
                    if L.kind(dst) == "file" and L.kind(src) == "file":
                        os.rename(src, dst)
                        log.append([ph["phase"], "replaced_existing_file"])
                        continue
                    if L.kind(dst) == "dir" and L.kind(src) == "dir" and not os.listdir(dst):
                        os.rmdir(dst)
                    elif L.kind(dst) == "dir":
                        return {"action": "aborted_ENOTEMPTY", "at": ph["phase"], "log": log}
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.rename(src, dst)
                log.append([ph["phase"], "undone"])
            elif u[0] == "rm_occ":
                for p in ("governance/kernel", "governance/project", "governance/generated", "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration"):
                    q = os.path.join(d, p)
                    if L.kind(q) == "file" and open(q).read().strip() == L.SENTINEL:
                        os.unlink(q)
                fl = os.path.join(d, "governance/framework.lock")
                if L.kind(fl) == "dir" and L.kind(os.path.join(fl, L.OCC_DIR_SENTINEL)) == "file":
                    os.unlink(os.path.join(fl, L.OCC_DIR_SENTINEL))
                    if not os.listdir(fl):
                        os.rmdir(fl)
                log.append([ph["phase"], "undone"])
            elif u[0] == "restore_gitignore":
                gi = os.path.join(d, ".gitignore")
                cur = open(gi).read() if os.path.exists(gi) else None
                if reading == "S" and cur not in (None, "/.governance-runtime/*\n!/.governance-runtime/migration\n", j["saved_gitignore"]):
                    return {"action": "refused_precondition", "at": ph["phase"], "log": log}
                if j["saved_gitignore"] is None:
                    if cur is not None:
                        os.unlink(gi)
                else:
                    open(gi, "w").write(j["saved_gitignore"])
                log.append([ph["phase"], "undone"])
        except OSError as e:
            return {"action": "aborted_oserror", "at": ph["phase"], "error": e.strerror, "log": log}
    q = os.path.join(d, ".governance-runtime", "legacy-quarantine")
    if L.kind(q) == "dir" and not os.listdir(q):
        os.rmdir(q)
    ab = os.path.join(d, ".governance-runtime", "trust-tx", "abandoned")
    os.makedirs(ab, exist_ok=True)
    os.rename(tx, os.path.join(ab, TXN))
    rec["open_tx"] = [x for x in rec["open_tx"] if x != TXN]
    return {"action": "rolled_back", "log": log}


def digest_without_tx(d):
    m = L.tmap(d)
    return L.dmap({k: v for k, v in m.items() if not k.startswith(".git/") and k != ".git" and not k.startswith(".governance-runtime/trust-tx")})


L0_DIGEST = digest_without_tx(L0)


def legacy_probe(d):
    c = d + "-legacy"
    shutil.copytree(d, c, symlinks=True)
    env = L.env_child(os.path.join(BASE, "home-" + os.path.basename(c)), os.path.join(BASE, "cache"))
    o = {}
    for name, argv in (("status", ["status"]), ("kernel_trust", ["kernel", "trust"]), ("rebuild", ["rebuild-memory"]), ("query", ["memory", "query", L.MARK1]),
                       ("init_force", ["init", "--force", "--skip-index"]), ("rebuild2", ["rebuild-memory"]), ("query_after_init_force", ["memory", "query", L.MARK1])):
        r = L.gov(G5, argv, env, c, c)
        o[name] = {"ok": r.get("ok"), "code": L.ecode(r)}
        if name == "kernel_trust":
            o[name]["verified"] = L.res(r).get("verified")
        if name.startswith("query"):
            o[name]["serves_restricted"] = any(isinstance(h, dict) and "restricted-plan" in str(h.get("path")) for h in (L.res(r).get("hits") or []))
    return o


INTERVENING = ["NONE", "GIT_STASH", "GIT_STASH_U", "GIT_CLEAN_FDX", "GIT_CHECKOUT_DOT", "LEGACY_INIT_FORCE", "MOVE_CHECKOUT", "RECORD_LOST"]


def intervene(d, rec, what):
    note = ""
    if what == "GIT_STASH":
        note = g(d, "stash", check=False).stdout.strip()[:120]
    elif what == "GIT_STASH_U":
        note = g(d, "stash", "-u", check=False).stdout.strip()[:120]
    elif what == "GIT_CLEAN_FDX":
        note = g(d, "clean", "-fdx", check=False).stdout.strip()[:200]
    elif what == "GIT_CHECKOUT_DOT":
        g(d, "checkout", "--", ".", check=False)
    elif what == "LEGACY_INIT_FORCE":
        env = L.env_child(os.path.join(BASE, "home-if-" + os.path.basename(d)), os.path.join(BASE, "cache"))
        r = L.gov(G5, ["init", "--force", "--skip-index"], env, d, d)
        note = "ok=%s code=%s" % (r.get("ok"), L.ecode(r))
    elif what == "MOVE_CHECKOUT":
        nd = d + "-moved"
        os.rename(d, nd)
        return nd, rec, "moved to a new path"
    elif what == "RECORD_LOST":
        return d, None, "per-project record not readable (moved aside by a first admission, `31` R-ADM-8″; or RS-3)"
    return d, rec, note


rows = {}
for n in range(1, len(STEPS) + 1):
    for crash in ("post", "mid"):
        for what in INTERVENING:
            d, rec = build(n, crash, what)
            key = "%02d:%s:%s:%s" % (n, STEPS[n - 1][0], crash, what)
            honoured_before = L.state_r7(d, rec, identity(d), rcs)
            d, rec2, note = intervene(d, rec, what)
            idn = identity(d) if L.kind(os.path.join(d, ".git")) != "absent" else None
            st_mid = L.state_r7(d, rec2, idn, rcs)
            row = {"state_at_crash": honoured_before["state"], "intervening_note": note, "state_after_intervening": st_mid["state"], "by_reading_after_intervening": st_mid["by_reading"],
                   "classifications_after_intervening": L.classifications(d)}
            for reading in ("L", "S"):
                c = d + "-rec" + reading
                shutil.copytree(d, c, symlinks=True)
                r2 = copy.deepcopy(rec2)
                if r2 is not None:
                    r2["paths"] = [os.path.realpath(c) if p == os.path.realpath(d) else p for p in r2["paths"]]
                    r2["identity"] = identity(c) if L.kind(os.path.join(c, ".git")) != "absent" else None
                    if what == "MOVE_CHECKOUT":
                        r2["paths"] = [os.path.realpath(c).replace("-moved-rec" + reading, "")]
                out = recover(c, r2, reading)
                st = L.state_r7(c, r2, identity(c) if L.kind(os.path.join(c, ".git")) != "absent" else None, rcs)
                row["recovery_" + reading] = out.get("action")
                row["recovery_detail_" + reading] = {k: v for k, v in out.items() if k != "action"}
                row["state_after_recovery_" + reading] = st["state"]
                row["by_reading_after_recovery_" + reading] = st["by_reading"]
                row["equal_to_legacy_project_" + reading] = digest_without_tx(c) == L0_DIGEST
                row["classifications_after_recovery_" + reading] = L.classifications(c)
                row["rinit9_refuses_" + reading] = L.rinit9_refuses(c)
                row["absent_any_reading_" + reading] = any(v == "ABSENT" for v in st["by_reading"].values())
            rows[key] = row

# legacy behaviour on a representative subset of post-recovery trees (reading L)
legacy = {}
for key, row in rows.items():
    n, phase, crash, what = key.split(":")
    if what in ("NONE", "GIT_STASH", "LEGACY_INIT_FORCE", "GIT_STASH_U") and crash == "post" and int(n) in (3, 5, 8, 10):
        legacy[key] = legacy_probe(os.path.join(BASE, "p%s-%s-%s-intx" % (n, crash, what)) + ("-moved" if what == "MOVE_CHECKOUT" else "") + "-recL")

# commit-and-clone of crash prefixes: what a second machine sees
clones = {}
for n in (3, 4, 5, 8, 10, 11):
    d, rec = build(n, "post", "COMMITSRC")
    g(d, "add", "-A"); g(d, "commit", "-qm", "commit during an interrupted first install", check=False)
    c = os.path.join(BASE, "clone-p%02d" % n)
    g(BASE, "clone", "-q", d, c)
    st = L.state_r7(c, None, None, rcs)
    clones["%02d:%s" % (n, STEPS[n - 1][0])] = {"state": st["state"], "by_reading": st["by_reading"], "classifications": L.classifications(c), "rinit9_refuses": L.rinit9_refuses(c),
                                                 "legacy_named_dirs": st["legacy_named_dirs"], "moved_names": st["moved_names"], "legacy_4.1.5": legacy_probe(c)}

# ABSENT with classified content under a legacy name, reached by ordinary operations on a legacy project
absp = {}
d = os.path.join(BASE, "absp-git-rm"); shutil.copytree(L0, d, symlinks=True); g(d, "rm", "-r", "-q", "governance/kernel", "governance/framework.lock")
st = L.state_r7(d, None, None, rcs)
absp["user_removes_legacy_kernel_and_lock"] = {"state": st["state"], "by_reading": st["by_reading"], "classifications": L.classifications(d), "rinit9_refuses": L.rinit9_refuses(d)}
d = os.path.join(BASE, "absp-sparse"); g(BASE, "clone", "-q", "--no-checkout", L0, d); g(d, "sparse-checkout", "init", "--no-cone")
open(os.path.join(d, ".git/info/sparse-checkout"), "w").write("/governance/project/\n/product/\n/docs/\n/.gitignore\n"); g(d, "checkout", "-q", check=False)
st = L.state_r7(d, None, None, rcs)
absp["non_cone_sparse_checkout_of_a_legacy_project"] = {"state": st["state"], "by_reading": st["by_reading"], "classifications": L.classifications(d), "rinit9_refuses": L.rinit9_refuses(d)}

# uninstall (`20` §6) result
d = os.path.join(BASE, "uninstall"); shutil.copytree(R7, d, symlinks=True)
rm = os.path.join(d, ".governance-runtime", "trust-tx", "TX-" + "0d" * 16, "removed"); os.makedirs(rm)
os.rename(os.path.join(d, "governance/trust"), os.path.join(rm, "trust"))
for p in list(L.OCC):
    if L.kind(os.path.join(d, p)) != "absent":
        os.makedirs(os.path.dirname(os.path.join(rm, "occ", p)), exist_ok=True)
        os.rename(os.path.join(d, p), os.path.join(rm, "occ", p))
st = L.state_r7(d, None, None, rcs)
uninstall = {"text_20_s6": "leaves the result ABSENT", "state_by_18_s9": st["state"], "by_reading": st["by_reading"], "overlay_or_views_present": st["overlay_or_views"],
             "classifications": L.classifications(d), "rinit9_refuses": L.rinit9_refuses(d)}

# crashmig7's roll-forward: does its recovery change the tree when the exchange happened?
cm7 = open(os.path.join(L.EXPORT, "release/root-of-trust/4.1.6/evidence/r7/LAY7/crashmig7.py")).read()
rf_src = cm7[cm7.index("if exchanged:"):cm7.index("for s in reversed")]
rollforward_model = {"crashmig7_roll_forward_branch": rf_src.strip(), "mutates_tree": any(x in rf_src for x in ("os.rename", "open(", "shutil", "unlink", "makedirs"))}

# first-install honouring: is there a per-project record before the first install commits?
honour = {}
for variant in ("record_created_at_prepared", "record_written_at_end_as_18_s4_orders"):
    d, rec = build(3, "post", "HONOUR-" + variant)
    r = rec if variant == "record_created_at_prepared" else None
    st = L.state_r7(d, r, identity(d), rcs)
    honour[variant] = {"state": st["state"], "by_reading": st["by_reading"], "honoured": bool(st["honoured"]), "foreign": st["foreign"],
                       "recovery": recover(d + "", r, "L")["action"] if r is None else "recoverable"}

# shared per-project record: two worktrees' transactions register open TXs without a lock (read-modify-write)
recfile = os.path.join(BASE, "shared-record.json")


def run_writers(locked, iters=400):
    json.dump({"open_tx": []}, open(recfile, "w"))
    lost = [0]

    def w(tag):
        for i in range(iters):
            tx = "%s-%d" % (tag, i)
            fd = os.open(recfile + ".lock", os.O_CREAT | os.O_RDWR) if locked else None
            if locked:
                fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                d_ = json.load(open(recfile))
                d_["open_tx"].append(tx)
                tmp = recfile + ".%s.tmp" % tag
                json.dump(d_, open(tmp, "w"))
                os.replace(tmp, recfile)
            except Exception:
                lost[0] += 1
            finally:
                if locked:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
    th = [threading.Thread(target=w, args=(t,)) for t in ("worktreeA", "worktreeB")]
    [t.start() for t in th]
    [t.join() for t in th]
    final = json.load(open(recfile))["open_tx"]
    return {"registrations_attempted": 2 * iters, "registrations_present": len(final), "lost_updates": 2 * iters - len(final), "read_errors": lost[0]}


shared = {"unlocked_read_modify_write": run_writers(False), "serialised_with_flock": run_writers(True),
          "text": "`18` §5.4 locks `.governance-runtime/trust-tx/LOCK`, which is per working tree; `20` §9 shares one per-project record between "
                  "worktrees of one repository identity; no rule serialises updates of the record (open transactions, highest sequence, vector)"}

summary = {
    "cases": len(rows),
    "post_recovery_ABSENT_any_reading_L": sorted(k for k, r in rows.items() if r["absent_any_reading_L"]),
    "post_recovery_ABSENT_any_reading_S": sorted(k for k, r in rows.items() if r["absent_any_reading_S"]),
    "post_recovery_COMPLETE_L": sorted(k for k, r in rows.items() if r["state_after_recovery_L"] == "COMPLETE"),
    "post_recovery_PARTIAL_L": sorted(k for k, r in rows.items() if r["state_after_recovery_L"] == "PARTIAL"),
    "recovery_actions_L": {a: sum(1 for r in rows.values() if r["recovery_L"] == a) for a in sorted({r["recovery_L"] for r in rows.values()})},
    "recovery_actions_S": {a: sum(1 for r in rows.values() if r["recovery_S"] == a) for a in sorted({r["recovery_S"] for r in rows.values()})},
    "NONE_rolled_back_not_equal_to_legacy_project_L": sorted(k for k, r in rows.items() if k.endswith(":NONE") and r["recovery_L"] == "rolled_back" and not r["equal_to_legacy_project_L"]),
    "rolled_back_after_intervening_op_not_equal_to_legacy_project_L": sorted(k for k, r in rows.items() if not k.endswith(":NONE") and r["recovery_L"] == "rolled_back" and not r["equal_to_legacy_project_L"]),
    "file_replaced_silently_by_undo_L": sorted(k for k, r in rows.items() if any(x[1] == "replaced_existing_file" for x in r["recovery_detail_L"].get("log", []))),
    "classification_absent_everywhere_after_recovery_L": sorted(k for k, r in rows.items() if r["classifications_after_recovery_L"] and not any(r["classifications_after_recovery_L"].values())),
    "journal_not_honoured_after_intervening": sorted(k for k, r in rows.items() if r["recovery_L"] == "not_honoured"),
    "state_after_not_honoured": {k: r["state_after_recovery_L"] for k, r in rows.items() if r["recovery_L"] == "not_honoured"},
    "absent_with_classified_legacy_named_content_and_rinit9_silent": sorted(k for k, v in absp.items() if any(s == "ABSENT" for s in v["by_reading"].values()) and not v["rinit9_refuses"] and v["classifications"].get("governance/project")),
}
matrix_trees = {}
for key in legacy:
    n, phase, crash, what = key.split(":")
    matrix_trees["rec-%s-%s-%s" % (n, crash, what)] = os.path.join(BASE, "p%s-%s-%s-intx" % (n, crash, what)) + ("-moved" if what == "MOVE_CHECKOUT" else "") + "-recL"
for n in (3, 4, 5, 8, 10, 11):
    matrix_trees["clone-p%02d" % n] = os.path.join(BASE, "clone-p%02d" % n)
matrix_trees["absp-git-rm"] = os.path.join(BASE, "absp-git-rm")
matrix_trees["absp-sparse"] = os.path.join(BASE, "absp-sparse")
matrix_trees["uninstall"] = os.path.join(BASE, "uninstall")
out = {"probe": "txn7 (AR-0021) held-out transaction attacks", "steps": [s[0] for s in STEPS], "rows": rows, "legacy_on_recovered_trees": legacy, "clones_of_committed_crash_prefixes": clones,
       "absent_with_legacy_named_content": absp, "uninstall": uninstall, "rollforward_model": rollforward_model, "first_install_honouring": honour, "shared_record": shared, "summary": summary, "matrix_trees": matrix_trees}
L.dump(out, os.path.join(OUT, "txn7.json"))
print(L.scrub(json.dumps(summary, indent=1, sort_keys=True)))
print(L.scrub(json.dumps({"clones": {k: {kk: vv for kk, vv in v.items() if kk != "legacy_4.1.5"} for k, v in clones.items()}, "absp": absp, "uninstall": uninstall, "honour": honour, "shared": shared,
                          "rollforward_mutates_tree": rollforward_model["mutates_tree"]}, indent=1, sort_keys=True, default=str)))
