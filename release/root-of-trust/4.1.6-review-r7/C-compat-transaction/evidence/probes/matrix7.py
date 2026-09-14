#!/usr/bin/env python3
"""AR-0021 independent pre-RoT command-register matrix on the RoT-1 revision-7 layout (real legacy 4.1.2–4.1.5).

Every leaf of each binary's own register (registers7.json, derived by AR-0021 from --help and from source, cross-checked), each
optional option and positional as a separate variant, plus stateful combinations, on fresh copies of the revision-7 trees:
  P-ROOT             --root <project>: full register on R7; base + combinations on R7RES, R7CRASH, R7OPEN, R7V, R7WT, L0 (control)
  P-CWD:<dir>        no --root, every depth: inside governance/trust/**, the occupation directory, the transaction area and its
                     done/ archive, the legacy quarantine, snapshots, overlay and views, .git (full register on R7)
  P-OPEN:<dir>       no --root, inside an honoured OPEN transaction's trust.next, trust.prev, trust.prev/kernel, overlay.prev (R7OPEN)
  P-WT:<dir>         no --root, inside a git worktree of the project (R7WT; the common directory is outside the worktree)
  P-ENV:<set>@<dir>  no --root, user environment variables, including a kernel cache pointed into the account verifier trust store
                     and a kernel source pointed at the installed RoT-1 kernel (R7)
  P-VEND:<dir>       no --root, in and above a committed legacy sub-project (R7V)
  P-GIT:<op>@<pos>   --root and product/ on the trees gitops7.py produced
  P-TXN:<case>       --root on post-recovery trees txn7.py produced
Each row: whole-tree before/after maps of the entire slot (project work tree, .governance-runtime, .git, and for a worktree the
base repository and its worktree administration), git plumbing, child HOME and kernel cache; `state_r7` before and after under
every reading; kernel-tampered against the release content set; classifications; honoured-journal contents for R7OPEN.
The whole-tree digest decides "no write". Usage: matrix7.py <trees.raw.json> <registers7.json> <gitops7-trees.json|-> <txn7.json|-> <out>
       [--workers N] [--only P-ROOT,...]
"""
import argparse, collections, concurrent.futures as cf, gzip, json, os, shutil, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa

OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}
CWD = [".", "product", "product/customers", "docs", "spec", "spec/audits", "spec/audits/ADOPTION", "spec/now", "tools", "governance", "governance/overlay",
       "governance/overlay/plugins", "governance/views", "governance/trust", "governance/trust/kernel", "governance/trust/kernel/policies", "governance/trust/state",
       "governance/trust/root", "governance/trust/lineage", "governance/trust/profiles", "governance/framework.lock", ".governance-runtime",
       ".governance-runtime/trust-tx", ".governance-runtime/trust-tx/done", ".governance-runtime/trust-tx/done/" + "TX-" + "d0" * 16,
       ".governance-runtime/legacy-quarantine", ".governance-runtime/legacy-quarantine/update/4.1.5", ".governance-runtime/snapshots/sha256-" + "b" * 16 + "/overlay",
       ".git", ".git/info"]
OPEN = [".governance-runtime/trust-tx/" + "TX-" + "0e" * 16 + x for x in ("", "/trust.next", "/trust.prev", "/trust.prev/kernel", "/overlay.prev/overlay")]
VEND = ["vendor", "vendor/legacypkg", "vendor/legacypkg/product", "vendor/legacypkg/governance/project"]
LIN64 = "7" * 64


def env_sets(S, proj):
    home = "<HOME>"
    return {"KSRC": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"]}, "KSRC_ROT1_INSTALLED": {"GOV_KERNEL_SOURCE": proj + "/governance/trust/kernel"},
            "CANON_EXPORT": {"GOV_CANONICAL_ROOT": L.EXPORT}, "CANON_PROJECT": {"GOV_CANONICAL_ROOT": proj},
            "PLUGDIR": {"GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir")}, "ROLESESS": {"GOV_ROLE": "owner", "GOV_SESSION": "S-env", "GOV_DISABLE_PLUGINS": "1"},
            "CACHE_IN_PROJECT": {"GOV_KERNEL_CACHE": proj + "/.cache/gov"}, "CACHE_IN_ACCOUNT_STORE": {"GOV_KERNEL_CACHE": home + "/.local/state/gov/trust/" + LIN64},
            "XDGCACHE_STATE": {"XDG_CACHE_HOME": home + "/.local/state/gov/trust", "GOV_KERNEL_CACHE": None}, "TRACE": {"GOV_TRACE_ID": "ar21"},
            "ALL": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"], "GOV_CANONICAL_ROOT": proj, "GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir"), "GOV_ROLE": "owner", "GOV_SESSION": "S"}}


def val(n, path, ids, S, v, proj):
    fx = os.path.join(S, "fixtures")
    grp = path[0] if path else ""
    if n == "ID":
        return {"cit": ids["CIT"], "gate": ids["GATE"], "handoff": ids["HANDOFF"], "task": ids["TASK"]}.get(grp, ids["TASK"])
    if n == "DESCRIPTOR":
        return ids["PLUGIN_DESCRIPTOR"] if grp == "plugins" else ids["TOOL_DESCRIPTOR"]
    t = {"SOURCE": L.REL[v], "DIR": L.REL[v], "BATCH": "1", "STATUS": "IN_PROGRESS", "OPTION": "A", "BY": "owner", "METHOD": "human", "REASON": "ar21", "NAME": "ar21",
         "ALIAS": "ar21a", "QUERY": L.MARK1, "TEXT": "create a documentation task", "OBJECTIVE": "ar21", "TITLE": "ar21", "CLASS": "documentation", "QUESTION": "ar21?",
         "FIELDS": "{}", "PROPOSAL": "ar21", "TRIGGER": "editorial", "TARGETS": ids["TASK"], "MANIFEST": ids["MANIFEST"], "TASK": ids["TASK"], "TO_ROLE": "backend-engineer",
         "REPORT": ids["REPORT"], "FILE": ids["RETURN"], "LESSON": "L-0001", "PACKET": ids["PACKET"], "DESTINATION": os.path.join(fx, "upstream-dest"), "APPROVED_BY": "owner",
         "PLUGIN": "p-probe", "PLUGIN_ID": "p-probe", "INPUTS": "{}", "CAPABILITY": "code_intel", "POLICY": "SECURITY_POLICY", "WHAT": "governance",
         "VERDICT": "MIGRATION_PLAN_APPROVED", "RATIONALE": "ar21", "NOTES": "ar21", "NOTE": "ar21", "RADIUS": "R1", "OUT": os.path.join(fx, "release-out"),
         "CANONICAL": os.path.join(fx, "canon"), "INBOX": os.path.join(fx, "inbox"), "PROPOSALS": os.path.join(fx, "proposals"), "CANDIDATE": "hashed-ngram",
         "CANDIDATES": "hashed-ngram", "FEATURE": "FEAT-0001", "NODE": ids["TASK"], "SEEDS": ids["TASK"], "K": "8", "DEPTH": "1", "ROUTE": "lexical", "STEP": "ar21", "OPS": "9",
         "UTILISATION": "0.5", "TESTS_STATUS": "passed", "RECORD": "{}", "ATTRS": "{}", "EVIDENCE": "ar21", "INTENT": "ar21", "DEPS": ids["TASK"], "ALLOWED": "docs/**",
         "REVIEWER_SESSION": "S-rev", "REVIEWER_ROLE": "migration-reviewer", "VERIFIER_ROLE": "migration-verifier", "GATE_ANSWER": "yes", "HELDOUT": "governance/tests/memory/heldout.yaml",
         "CERTIFICATION": "READY_FOR_INDEPENDENT_OS_VERIFICATION", "RESEARCH": "RES-0001", "OP": "serve", "NEXT_ACTION": "continue", "FAMILY": "layout", "GATE": ids["GATE"]}
    return t.get(n, "ar21")


def invocations(leaf, ids, S, v, proj, full):
    base = list(leaf["path"])
    for p in leaf["positionals"]:
        if p["required"]:
            base.append(val(p["name"], leaf["path"], ids, S, v, proj))
    for o in leaf["options"]:
        if o["required"]:
            base += [o["long"], val(o["value"], leaf["path"], ids, S, v, proj)]
    out = [base]
    if full:
        for p in leaf["positionals"]:
            if not p["required"]:
                out.append(base + [val(p["name"], leaf["path"], ids, S, v, proj)])
        for o in leaf["options"]:
            if not o["required"]:
                out.append(base + ([o["long"]] if o["value"] is None else [o["long"], val(o["value"], leaf["path"], ids, S, v, proj)]))
    return out


def combos(v, ids, proj):
    s, o = L.REL[v], L.REL[OLDER[v]]
    rot1k = proj + "/governance/trust/kernel"
    snapk = proj + "/.governance-runtime/legacy-quarantine/update/4.1.5/kernel"
    return [["update", "--apply", "--approve", "--source", s, "--by", "owner"], ["update", "--apply", "--approve", "--source", o, "--by", "owner"],
            ["update", "--apply", "--approve", "--source", rot1k, "--by", "owner"], ["update", "--rollback", "--approve", "--reason", "ar21", "--by", "owner"],
            ["init", "--force", "--skip-index"], ["init", "--force", "--source", s, "--skip-index"], ["init", "--force", "--source", rot1k, "--skip-index"],
            ["init", "--source", o, "--name", "ar21", "--skip-index"], ["kernel", "reinstall", "--source", s], ["kernel", "reinstall", "--source", snapk],
            ["adopt", "migrate", "--batch", "0", "--source", s, "--name", "ar21", "--alias", "ar21a"], ["adopt", "rollback", "--batch", "0"],
            ["migrate", "migrate", "--batch", "0", "--source", s], ["migrate", "rollback", "--batch", "0"], ["cit", "execute", ids["CIT"]], ["cit", "rollback", ids["CIT"], "--reason", "ar21"],
            ["decide", ids["GATE"], "--option", "A", "--by", "owner"], ["tools", "install", "--descriptor", ids["TOOL_DESCRIPTOR"], "--execute"],
            ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"], ["recover"], ["rebuild-memory"],
            ["verify", "product"], ["adapters", "generate"], ["checkpoint", "create", "--next-action", "x"]]


_W = {}


def winit(S):
    _W["dir"] = os.path.join(S, "m7w", str(os.getpid()))
    os.makedirs(_W["dir"], exist_ok=True)
    _W["n"] = 0


def slot_copy(spec, dst):
    """spec: {"kind": "dir", "path": p} or {"kind": "worktree", "base": b, "wt": w}. Returns (slot_root, project_root)."""
    os.makedirs(dst)
    if spec["kind"] == "dir":
        p = os.path.join(dst, "p")
        shutil.copytree(spec["path"], p, symlinks=True)
        return dst, p
    b, w = os.path.join(dst, "base"), os.path.join(dst, "wt")
    shutil.copytree(spec["base"], b, symlinks=True)
    shutil.copytree(spec["wt"], w, symlinks=True)
    name = os.path.basename(spec["wt"])
    open(os.path.join(w, ".git"), "w").write("gitdir: %s\n" % os.path.join(b, ".git", "worktrees", name))
    open(os.path.join(b, ".git", "worktrees", name, "gitdir"), "w").write(os.path.join(w, ".git") + "\n")
    return dst, w


def plumbing(root, home):
    if L.kind(os.path.join(root, ".git")) == "absent":
        return {"no_git": True}
    q = lambda *a: L.git(root, *a, home=home, check=False).stdout
    return {"head": q("rev-parse", "HEAD").strip(), "refs": L.sha(q("for-each-ref", "--format=%(refname) %(objectname)").encode()),
            "status": L.sha(q("status", "--porcelain", "--ignored").encode()), "stash": q("stash", "list").strip()}


def rebind_record(rec, proj, orig_root):
    if rec is None:
        return None, None
    r = json.loads(json.dumps(rec))
    try:
        c = L.git(proj, "rev-parse", "--git-common-dir", check=False).stdout.strip()
        c = c if os.path.isabs(c) else os.path.join(proj, c)
        st = os.stat(os.path.realpath(c))
        ident = [st.st_dev, st.st_ino]
    except Exception:
        ident = None
    r["identity"] = ident
    r["paths"] = [os.path.realpath(proj)]
    return r, ident


def open_tx_digest(proj):
    t = os.path.join(proj, ".governance-runtime/trust-tx", "TX-" + "0e" * 16)
    return L.dmap(L.tmap(t)) if os.path.isdir(t) else None


def run(job):
    try:
        return run_inner(job)
    except Exception as e:  # noqa: BLE001  (a row that breaks the harness is recorded, never dropped)
        kind, layout, spec, rec, v, pos, argv = job[:7]
        return {"kind": kind, "layout": layout, "binary": v, "position": pos, "argv": argv, "harness_error": repr(e)[:300], "work_n": 1, "paths": ["<harness-error>"],
                "partition": {"harness_error": 1}, "plumbing_changed": True, "home_changed": [], "home_n": 0, "cache_n": 0, "state_before": "?", "state_after": "HARNESS_ERROR",
                "by_reading_before": {}, "by_reading_after": {"error": "HARNESS_ERROR"}, "reasons_after": [], "reports_after": [], "kernel_tampered_after": None,
                "classifications_after": {}, "open_tx_changed": None, "honoured_after": False, "rc": None, "ok": None, "code": None}


def run_inner(job):
    kind, layout, spec, rec, v, pos, argv, extra, rootflag, cwd_rel, S, ids, rcs, orig_root = job
    _W["n"] += 1
    slot = os.path.join(_W["dir"], "s%06d" % _W["n"])
    home = os.path.join(_W["dir"], "h%06d" % _W["n"])
    cache = os.path.join(_W["dir"], "k%06d" % _W["n"])
    os.makedirs(cache)
    sroot, proj = slot_copy(spec, slot)
    cwd = os.path.join(proj, cwd_rel)
    row = {"kind": kind, "layout": layout, "binary": v, "position": pos, "argv": argv}
    if not os.path.isdir(cwd):
        shutil.rmtree(slot, ignore_errors=True)
        return dict(row, skipped="cwd_absent")
    r7rec, ident = rebind_record(rec, proj, orig_root)
    st0 = L.state_r7(proj, r7rec, ident, rcs)
    tx0 = open_tx_digest(proj)
    ex = {}
    for k, x in (extra or {}).items():
        ex[k] = None if x is None else x.replace("<HOME>", home)
    envx = {k: x for k, x in ex.items() if x is not None}
    env = L.env_child(home, cache, envx)
    for k, x in ex.items():
        if x is None:
            env.pop(k, None)
    before = L.tmap(sroot)
    hb, cb = L.tmap(home), L.tmap(cache)
    pb = plumbing(proj, os.path.join(_W["dir"], "gh"))
    argv2 = [a.replace(orig_root, proj) if isinstance(a, str) else a for a in argv]
    r = L.gov(L.BINS[v], argv2, env, cwd, proj if rootflag else None)
    after = L.tmap(sroot)
    ch = L.changed(before, after)
    pa = plumbing(proj, os.path.join(_W["dir"], "gh"))
    rel_prefix = os.path.relpath(proj, sroot) + "/"
    chp = [c[len(rel_prefix):] if c.startswith(rel_prefix) else "<slot>/" + c for c in ch]
    st1 = L.state_r7(proj, r7rec, ident, rcs)
    homech = L.changed(hb, L.tmap(home))
    row.update({"rc": r["_rc"], "ok": r.get("ok"), "code": L.ecode(r), "work_n": len(ch), "paths": chp[:60], "partition": L.part(chp), "plumbing_changed": pb != pa,
                "digest_before": L.dmap(before)[:20], "digest_after": L.dmap(after)[:20], "home_changed": homech[:20], "home_n": len(homech), "cache_n": len(L.changed(cb, L.tmap(cache))),
                "state_before": st0["state"], "state_after": st1["state"], "by_reading_before": st0["by_reading"], "by_reading_after": st1["by_reading"],
                "reasons_after": st1["reasons"], "reports_after": st1["reports"], "kernel_tampered_after": st1.get("kernel_tampered"), "classifications_after": L.classifications(proj),
                "open_tx_changed": (tx0 != open_tx_digest(proj)) if tx0 else None, "honoured_after": bool(st1["honoured"])})
    shutil.rmtree(slot, ignore_errors=True)
    shutil.rmtree(home, ignore_errors=True)
    shutil.rmtree(cache, ignore_errors=True)
    return row


def summarise(rows):
    act = [r for r in rows if not r.get("skipped")]
    rot1 = [r for r in act if r["layout"] != "L0"]
    wrote = lambda r: bool(r["work_n"]) or r["plumbing_changed"]
    anycomplete = lambda r: any(s == "COMPLETE" for s in r["by_reading_after"].values())
    props = {}
    lp = [r for r in rot1 if r["kind"] == "P-ROOT"]
    props["LP-1r_root_anchored_no_write"] = {"rows": len(lp), "violations": sum(1 for r in lp if wrote(r)), "sample": [(r["layout"], r["binary"], r["argv"][:4], r["paths"][:5]) for r in lp if wrote(r)][:10]}
    h4 = [r for r in rot1 if (r["partition"].get("pps_trust") or r["partition"].get("pps_occupation")) and anycomplete(r) and not r["kernel_tampered_after"]]
    props["R2-H4_trust_or_occupation_change_left_COMPLETE_any_reading"] = {"violations": len(h4), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["paths"][:6]) for r in h4][:10]}
    el = [r for r in rot1 if wrote(r) and not any(s == "COMPLETE" for s in r["by_reading_before"].values()) and anycomplete(r)]
    props["write_moved_a_non_COMPLETE_tree_to_COMPLETE_any_reading"] = {"rows": len(el), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["state_before"], r["by_reading_after"]) for r in el][:10]}
    absn = [r for r in rot1 if wrote(r) and any(s == "ABSENT" for s in r["by_reading_after"].values()) and not any(s == "ABSENT" for s in r["by_reading_before"].values())]
    props["write_produced_ABSENT_any_reading"] = {"rows": len(absn), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["by_reading_after"], r["classifications_after"]) for r in absn][:10]}
    cl = [r for r in rot1 if r["classifications_after"] and not any(r["classifications_after"].values()) and (anycomplete(r) or any(s == "ABSENT" for s in r["by_reading_after"].values()))]
    props["classification_absent_on_COMPLETE_or_ABSENT_tree"] = {"rows": len(cl), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3]) for r in cl][:10]}
    tx = [r for r in rot1 if r["partition"].get("pps_txarea")]
    props["transaction_area_writes"] = {"rows": len(tx), "states_after": dict(collections.Counter(r["state_after"] for r in tx)),
                                        "open_tx_contents_changed_rows": sum(1 for r in tx if r.get("open_tx_changed")), "honoured_after_open_tx_changed": sum(1 for r in tx if r.get("open_tx_changed") and r["honoured_after"])}
    hs = [r for r in act if any(".local/state/gov" in p for p in r["home_changed"])]
    props["writes_under_account_store_path"] = {"rows": len(hs), "sample": [(r["kind"], r["position"], r["argv"][:3], r["home_changed"][:4]) for r in hs][:10]}
    he = [r for r in act if r.get("harness_error")]
    props["harness_error_rows"] = {"rows": len(he), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:6], r["harness_error"][:160]) for r in he][:10]}
    props["home_writes"] = {"rows": sum(1 for r in act if r["home_n"]), "by_argv": dict(collections.Counter(" ".join(r["argv"][:2]) for r in act if r["home_n"]).most_common(12))}
    div = [r for r in act if len(set(r["by_reading_after"].values())) > 1]
    props["reading_divergence_after"] = {"rows": len(div), "patterns": dict(collections.Counter(json.dumps(r["by_reading_after"], sort_keys=True) for r in div).most_common(6))}
    agg = collections.defaultdict(collections.Counter)
    for r in act:
        a = agg["%s|%s|%s" % (r["kind"], r["layout"], r["position"])]
        a["rows"] += 1
        a["writing"] += wrote(r)
        a["state_" + r["state_after"]] += 1
    return {"rows": len(rows), "active": len(act), "skipped": len(rows) - len(act), "by_binary": dict(collections.Counter(r["binary"] for r in rows)),
            "by_kind": dict(collections.Counter(r["kind"] for r in rows)), "writing_rows_rot1": sum(1 for r in rot1 if wrote(r)), "properties": props,
            "aggregate": {k: dict(v) for k, v in sorted(agg.items())}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trees"); ap.add_argument("registers"); ap.add_argument("gitops"); ap.add_argument("txn"); ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--only", default="P-ROOT,P-CWD,P-OPEN,P-WT,P-ENV,P-VEND,P-GIT,P-TXN")
    a = ap.parse_args()
    T = json.load(open(a.trees)); R = json.load(open(a.registers))
    S, ids, rcs, recs = T["scratch"], T["ids"], T["rcs"], T["records"]
    for d in ("upstream-dest", "release-out", "canon", "inbox", "proposals", "plugins-dir"):
        os.makedirs(os.path.join(S, "fixtures", d), exist_ok=True)
    only = set(a.only.split(","))
    jobs = []

    def add(kind, layout, spec, rec, pos, rootflag, cwd_rel, full, extra=None, orig_root=None):
        orig_root = orig_root or (spec.get("path") or spec.get("wt"))
        for v in L.VERSIONS:
            seen = set()
            for leaf in R[v]["leaves"]:
                for argv in invocations(leaf, ids, S, v, orig_root, full):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv))
                        jobs.append((kind, layout, spec, rec, v, pos, argv, extra, rootflag, cwd_rel, S, ids, rcs, orig_root))
            for argv in combos(v, ids, orig_root):
                if tuple(argv) not in seen:
                    seen.add(tuple(argv))
                    jobs.append((kind, layout, spec, rec, v, pos, argv, extra, rootflag, cwd_rel, S, ids, rcs, orig_root))

    D = lambda k: {"kind": "dir", "path": T["trees"][k]}
    WTS = {"kind": "worktree", "base": T["trees"]["R7WTBASE"], "wt": T["trees"]["R7WT"]}
    if "P-ROOT" in only:
        add("P-ROOT", "R7", D("R7"), recs["R7"], "P-ROOT", True, ".", True)
        for lay in ("R7RES", "R7CRASH", "R7OPEN", "R7V", "L0"):
            add("P-ROOT", lay, D(lay), recs.get(lay), "P-ROOT", True, ".", False)
        add("P-ROOT", "R7WT", WTS, recs["R7WT"], "P-ROOT", True, ".", False)
    if "P-CWD" in only:
        for c in CWD:
            add("P-CWD", "R7", D("R7"), recs["R7"], "P-CWD:" + c, False, c, True)
    if "P-OPEN" in only:
        for c in OPEN:
            add("P-OPEN", "R7OPEN", D("R7OPEN"), recs["R7OPEN"], "P-OPEN:" + c, False, c, False)
    if "P-WT" in only:
        for c in (".", "product", "governance/trust", "governance/overlay"):
            add("P-WT", "R7WT", WTS, recs["R7WT"], "P-WT:" + c, False, c, False)
    if "P-ENV" in only:
        for name, e in env_sets(S, T["trees"]["R7"]).items():
            for c in (".", "product", "governance/trust"):
                add("P-ENV", "R7", D("R7"), recs["R7"], "P-ENV:%s@%s" % (name, c), False, c, False, e)
    if "P-VEND" in only:
        for c in VEND:
            add("P-VEND", "R7V", D("R7V"), recs["R7V"], "P-VEND:" + c, False, c, True)
    if "P-GIT" in only and a.gitops != "-":
        for op, p in sorted(json.load(open(a.gitops))["trees"].items()):
            add("P-GIT", op, {"kind": "dir", "path": p}, None, "P-GIT:%s@root" % op, True, ".", False)
            add("P-GIT", op, {"kind": "dir", "path": p}, None, "P-GIT:%s@product" % op, False, "product", False)
    if "P-TXN" in only and a.txn != "-":
        X = json.load(open(a.txn))
        for name, p in sorted(X.get("matrix_trees", {}).items()):
            add("P-TXN", name, {"kind": "dir", "path": p}, None, "P-TXN:" + name, True, ".", False)
    OUT = os.path.abspath(a.out)
    os.makedirs(OUT, exist_ok=True)
    print("jobs=%d" % len(jobs), file=sys.stderr, flush=True)
    t0, rows = time.time(), []
    with gzip.open(os.path.join(OUT, "matrix7-rows.jsonl.gz"), "wt") as fo, cf.ProcessPoolExecutor(max_workers=a.workers, initializer=winit, initargs=(S,)) as ex:
        for row in ex.map(run, jobs, chunksize=2):
            rows.append(row)
            fo.write(L.scrub(json.dumps(row, sort_keys=True, default=str)) + "\n")
            if len(rows) % 2000 == 0:
                print("%d/%d %.0fs" % (len(rows), len(jobs), time.time() - t0), file=sys.stderr, flush=True)
    s = summarise(rows)
    s["elapsed_s"] = round(time.time() - t0)
    s["binaries_sha256"] = {v: L.fsha(L.BINS[v]) for v in L.VERSIONS}
    L.dump(s, os.path.join(OUT, "matrix7-summary.json"))
    wr = [r for r in rows if not r.get("skipped") and (r["work_n"] or r["plumbing_changed"]) and r["layout"] != "L0"]
    with gzip.open(os.path.join(OUT, "matrix7-writing-rows.json.gz"), "wt") as f:
        f.write(L.scrub(json.dumps(wr, sort_keys=True, default=str)))
    print(L.scrub(json.dumps({k: s[k] for k in ("rows", "active", "skipped", "by_binary", "by_kind", "writing_rows_rot1", "properties")}, indent=1, default=str)))


if __name__ == "__main__":
    main()
