#!/usr/bin/env python3
"""AR-0017 independent pre-RoT command-register matrix on the RoT-1 revision-6 layout.

Every leaf of each real legacy binary's own register (registers6.json, derived twice and cross-checked by AR-0017), with
argument synthesis, run against fresh copies of the revision-6 trees, in these positions:
  P-ROOT            --root <project>                                   (R6 full register + combos; R6RES/R6CRASH/R6V/L0 base+combos)
  P-CWD:<dir>       no --root, every depth incl. inside the PPS (governance/trust/**, occupation, transaction area) (R6)
  P-ENV:<set>@<dir> no --root, user environment variables a user might set (R6)
  P-VEND:<dir>      no --root, inside/above a committed legacy sub-project (R6V)
  P-GIT:<op>@<pos>  --root / product on trees produced by ordinary Git operations (gitops6.py)
Each row: whole-tree before/after digests (work tree, .governance-runtime, .git files and plumbing, child HOME, kernel
cache — every entry by type/mode/size/sha/nlink), changed paths partitioned, the `18` §9/§9.1 state before and after
(c6lib.state_r6, encoded from the text by AR-0017), the `18` §6.1 kernel-tampered check against RCS(D), nested markers, and
the overlay classifications. No named-path digest is trusted for "no write": the whole-tree digest decides.

Written for AR-0017; argument synthesis is AR-0017's, not copied from P3r3/ST5/LAY6.
Usage: matrix6.py <trees.json> <registers6.json> <gitops-trees.json|-> <out-dir> [--workers N] [--focus] [--only ...]
"""
import argparse, collections, concurrent.futures as cf, gzip, json, os, shutil, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c6lib as L  # noqa
import yaml

OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}
CWD_POSITIONS = [".", "product", "product/customers", "docs", "spec", "spec/audits", "spec/now", "governance",
                 "governance/overlay", "governance/views", "governance/trust", "governance/trust/kernel",
                 "governance/trust/kernel/policies", "governance/trust/state", "governance/trust/root",
                 "governance/trust/lineage", "governance/trust/profiles", "governance/framework.lock",
                 ".governance-runtime", ".governance-runtime/trust-tx", ".governance-runtime/trust-tx/done",
                 ".governance-runtime/legacy-quarantine/update", ".governance-runtime/snapshots"]
VEND_POSITIONS = ["vendor", "vendor/legacypkg", "vendor/legacypkg/product", "vendor/legacypkg/governance/project"]


def env_sets(S, WT, proj):
    return {"KSRC": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"]},
            "CANON": {"GOV_CANONICAL_ROOT": WT},
            "PLUGDIR": {"GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir")},
            "ROLESESS": {"GOV_ROLE": "owner", "GOV_SESSION": "S-env", "GOV_DISABLE_PLUGINS": "1"},
            "CACHE_IN_PROJECT": {"GOV_KERNEL_CACHE": "<PROJ>/.cache/gov"},
            "TRACE": {"GOV_TRACE_ID": "ar17trace"},
            "ALL": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"], "GOV_CANONICAL_ROOT": WT, "GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir"),
                    "GOV_ROLE": "owner", "GOV_SESSION": "S-env"}}


def val(name, path, ids, S, v):
    n = (name or "").upper()
    grp = path[0] if path else ""
    if n == "ID":
        return {"cit": ids["CIT"], "gate": ids["GATE"], "handoff": ids["HANDOFF"], "task": ids["TASK"]}.get(grp, ids["TASK"])
    if n == "DESCRIPTOR":
        return ids["PLUGIN_DESCRIPTOR"] if grp == "plugins" else ids["TOOL_DESCRIPTOR"]
    fx = os.path.join(S, "fixtures")
    table = {"SOURCE": L.REL[v], "DIR": L.REL[v], "BATCH": "1", "STATUS": "IN_PROGRESS", "OPTION": "A", "BY": "owner", "METHOD": "human",
             "REASON": "ar17", "NAME": "ar17", "ALIAS": "ar17-alias", "QUERY": "AR0017RESTRICTEDMARKER", "TEXT": "create a documentation task",
             "OBJECTIVE": "ar17", "TITLE": "ar17", "CLASS": "documentation", "QUESTION": "ar17?", "FIELDS": "{}", "PROPOSAL": "ar17 proposal",
             "TRIGGER": "editorial", "TARGETS": ids["TASK"], "MANIFEST": ids["MANIFEST"], "TASK": ids["TASK"], "TO_ROLE": "backend-engineer",
             "REPORT": ids["REPORT"], "FILE": ids["RETURN"], "LESSON": "L-0001", "PACKET": ids["PACKET"], "DESTINATION": os.path.join(fx, "upstream-dest"),
             "APPROVED_BY": "owner", "PLUGIN": "p-probe", "PLUGIN_ID": "p-probe", "INPUTS": "{}", "CAPABILITY": "code_intel",
             "POLICY": "SECURITY_POLICY", "WHAT": "governance", "VERDICT": "MIGRATION_PLAN_APPROVED", "RATIONALE": "ar17", "NOTES": "ar17",
             "NOTE": "ar17", "RADIUS": "R1", "OUT": os.path.join(fx, "release-out"), "CANONICAL": os.path.join(fx, "canon"),
             "INBOX": os.path.join(fx, "inbox"), "PROPOSALS": os.path.join(fx, "proposals"), "CANDIDATE": "hashed-ngram",
             "FEATURE": "FEAT-0001", "NODE": ids["TASK"], "SEEDS": ids["TASK"], "K": "8", "DEPTH": "1", "ROUTE": "lexical", "STEP": "ar17",
             "OPS": "9", "UTILISATION": "0.5", "TESTS_STATUS": "passed", "RECORD": "{}", "ATTRS": "{}", "EVIDENCE": "ar17", "INTENT": "ar17 intent",
             "DEPS": ids["TASK"], "ALLOWED": "docs/**", "REVIEWER_SESSION": "S-rev", "REVIEWER_ROLE": "migration-reviewer",
             "VERIFIER_ROLE": "migration-verifier", "GATE_ANSWER": "yes", "VERSION": "4.1.6",
             "HELDOUT": "governance/tests/memory/heldout.yaml", "CERTIFICATION": "READY_FOR_INDEPENDENT_OS_VERIFICATION",
             "RESEARCH": "RES-0001", "OP": "serve", "NEXT_ACTION": "continue", "FAMILY": "layout", "GATE": ids["GATE"]}
    return table.get(n, "ar17")


def invocations(leaf, ids, S, v, full):
    base = list(leaf["path"])
    for p in leaf["positionals"]:
        if p["required"]:
            base.append(val(p["name"], leaf["path"], ids, S, v))
    for o in leaf["options"]:
        if o["required"]:
            base += [o["long"], val(o["value"], leaf["path"], ids, S, v)]
    out = [("base", base)]
    if full:
        for p in leaf["positionals"]:
            if not p["required"]:
                out.append(("pos:" + p["name"], base + [val(p["name"], leaf["path"], ids, S, v)]))
        for o in leaf["options"]:
            if o["required"]:
                continue
            out.append((("flag:" if o["value"] is None else "opt:") + o["long"],
                        base + ([o["long"]] if o["value"] is None else [o["long"], val(o["value"], leaf["path"], ids, S, v)])))
    return out


def combos(v, ids, S):
    s, o, n5 = L.REL[v], L.REL[OLDER[v]], L.REL["4.1.5"]
    return [["update", "--apply", "--approve", "--source", s, "--by", "owner"], ["update", "--apply", "--approve", "--source", o, "--by", "owner"],
            ["update", "--apply", "--approve", "--source", n5], ["update", "--rollback", "--approve", "--reason", "ar17", "--by", "owner"],
            ["init", "--force", "--skip-index"], ["init", "--force", "--source", s, "--skip-index"], ["init", "--source", o, "--name", "ar17", "--skip-index"],
            ["kernel", "reinstall", "--source", s], ["adopt", "migrate", "--batch", "0", "--source", s, "--name", "ar17", "--alias", "ar17a"],
            ["adopt", "rollback", "--batch", "0"], ["migrate", "migrate", "--batch", "0", "--source", s], ["migrate", "rollback", "--batch", "0"],
            ["cit", "execute", ids["CIT"]], ["cit", "rollback", ids["CIT"], "--reason", "ar17"],
            ["decide", ids["GATE"], "--option", "A", "--by", "owner"], ["tools", "install", "--descriptor", ids["TOOL_DESCRIPTOR"], "--execute"],
            ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"],
            ["recover"], ["rebuild-memory"], ["verify", "product"], ["adapters", "generate"], ["checkpoint", "create", "--next-action", "x"]]


_W = {}


def worker_init(S):
    _W["dir"] = os.path.join(S, "w", str(os.getpid()))
    os.makedirs(_W["dir"], exist_ok=True)
    _W["n"] = 0


def run_job(job):
    kind, layout, tree, v, pos, argv, variant, extra_env, root_flag, cwd_rel, S, ids, rcs = job
    _W["n"] += 1
    c = os.path.join(_W["dir"], "run")
    if os.path.exists(c):
        shutil.rmtree(c, ignore_errors=True)
    shutil.copytree(tree, c, symlinks=True)
    home = os.path.join(_W["dir"], "home")
    if os.path.exists(home):
        shutil.rmtree(home, ignore_errors=True)
    cache = os.path.join(_W["dir"], "cache-" + v)
    ee = {k: val.replace("<PROJ>", c) for k, val in (extra_env or {}).items()}
    env = L.child_env(home, cache, ee)
    cwd = os.path.join(c, cwd_rel)
    if not os.path.isdir(cwd):
        shutil.rmtree(c, ignore_errors=True)
        return {"kind": kind, "layout": layout, "binary": v, "position": pos, "argv": argv, "variant": variant, "skipped": "cwd_absent"}
    githome = os.path.join(_W["dir"], "githome")
    st_before = L.state_r6(c)
    before = {"work": L.tree_map(c), "home": L.tree_map(home), "cache": L.tree_map(cache)}
    dig_before = L.digest_map(before["work"])
    gp_before = git_plumbing(c, githome)
    r = L.gov(L.BINS[v], argv, env, cwd, c if root_flag else None)
    after = {"work": L.tree_map(c), "home": L.tree_map(home), "cache": L.tree_map(cache)}
    gp_after = git_plumbing(c, githome)
    changed = L.diff(before["work"], after["work"])
    part = L.partition(changed)
    st_after = L.state_r6(c, rcs=rcs)
    ktamp = st_after.get("kernel_tampered")
    cls = L.classifications(c)
    row = {"kind": kind, "layout": layout, "binary": v, "position": pos, "variant": variant, "argv": argv,
           "rc": r["_rc"], "ok": r.get("ok"), "code": L.errcode(r),
           "dig_before": dig_before[:24], "dig_after": L.digest_map(after["work"])[:24],
           "work_n": len(changed), "git_plumbing_changed": gp_before != gp_after,
           "home_n": len(L.diff(before["home"], after["home"])), "cache_n": len(L.diff(before["cache"], after["cache"])),
           "paths": changed[:60], "partition": part,
           "state_before": st_before["state"], "state_after": st_after["state"], "reasons_after": st_after["reasons"],
           "reports_after": st_after["reports"], "kernel_tampered_after": ktamp, "classifications_ok": cls}
    shutil.rmtree(c, ignore_errors=True)
    shutil.rmtree(home, ignore_errors=True)
    return row


def git_plumbing(root, home):
    if not os.path.isdir(os.path.join(root, ".git")):
        return {"no_git": True}
    def g(*a):
        return L.git(root, *a, check=False, home=home).stdout
    return {"head": g("rev-parse", "HEAD").strip(), "refs": L.sha(g("for-each-ref", "--format=%(refname) %(objectname)").encode()),
            "status": L.sha(g("status", "--porcelain").encode()), "stash": g("stash", "list").strip()}


def summarise(rows):
    active = [r for r in rows if not r.get("skipped")]
    agg = collections.defaultdict(collections.Counter)
    for r in active:
        a = agg["%s|%s|%s" % (r["kind"], r["layout"], r["position"])]
        a["rows"] += 1
        wrote = r["work_n"] or r["git_plumbing_changed"]
        a["writing"] += bool(wrote)
        a["state_" + r["state_after"]] += 1
        for k in r["partition"]:
            a["part_" + k] += 1
    props = {}
    lp1r = [r for r in active if r["kind"] == "P-ROOT" and r["layout"] in ("R6", "R6RES", "R6CRASH", "R6V")]
    v = [r for r in lp1r if r["work_n"] or r["git_plumbing_changed"]]
    props["LP-1r_root_anchored_no_project_write"] = {"rows": len(lp1r), "violations": len(v),
                                                     "sample": [(r["layout"], r["binary"], r["argv"][:4], r["paths"][:6]) for r in v[:12]]}
    # R2-H4 class: a change under governance/trust/** or an occupation entry must never leave COMPLETE without KERNEL_TAMPERED
    v3 = [r for r in active if r["layout"] != "L0" and (r["partition"].get("pps_trust") or r["partition"].get("pps_occupation"))
          and r["state_after"] == "COMPLETE" and not r["kernel_tampered_after"]]
    props["R2-H4_trust_or_occupation_change_left_COMPLETE"] = {"violations": len(v3),
                                                              "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["paths"][:8]) for r in v3[:15]]}
    # any write to trust/occupation and the state stays COMPLETE at all (broader, includes txarea)
    v3b = [r for r in active if r["layout"] != "L0" and (r["partition"].get("pps_trust") or r["partition"].get("pps_occupation") or r["partition"].get("pps_txarea"))
           and r["state_after"] == "COMPLETE"]
    props["pps_write_left_COMPLETE_incl_txarea"] = {"rows": len(v3b),
                                                    "by_partition": dict(collections.Counter("+".join(sorted(k for k in r["partition"] if k.startswith("pps_"))) for r in v3b)),
                                                    "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], [p for p in r["paths"] if p.startswith("governance/trust") or p.startswith(".governance-runtime/trust-tx") or p in L.OCCUPATION][:6]) for r in v3b[:15]]}
    # classification loss
    v6 = [r for r in active if r["layout"] != "L0" and r["classifications_ok"] is False]
    props["classification_lost"] = {"rows": len(v6), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3]) for r in v6[:12]]}
    # nested markers all reported
    v5 = [r for r in active if r["layout"] != "L0" and r["work_n"] and (r["reports_after"] or "nested_legacy_install" in r["reasons_after"])]
    props["nested_marker_rows"] = {"rows": len(v5), "by_state": dict(collections.Counter(r["state_after"] for r in v5))}
    # git-op trees written from non-COMPLETE into COMPLETE
    v8 = [r for r in active if r["kind"] == "P-GIT" and r["state_before"] != "COMPLETE" and r["work_n"] and r["state_after"] == "COMPLETE"]
    props["gitop_write_into_COMPLETE"] = {"rows": len(v8), "sample": [(r["layout"], r["position"], r["argv"][:3]) for r in v8[:12]]}
    wc = collections.Counter()
    for r in active:
        if r["work_n"] and r["layout"] != "L0":
            wc[(r["kind"], " ".join(r["argv"][:2]))] += 1
    return {"rows": len(rows), "active": len(active), "skipped": len(rows) - len(active),
            "by_kind_layout_position": {k: dict(a) for k, a in sorted(agg.items())}, "properties": props,
            "writing_commands_rot1": {"%s|%s" % k: n for k, n in sorted(wc.items())}}


def resummarise(out_dir):
    """Recompute the summary from a completed rows file (matrix6-rows.jsonl.gz) without re-running invocations."""
    rows = []
    with gzip.open(os.path.join(out_dir, "matrix6-rows.jsonl.gz"), "rt") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    s = summarise(rows)
    s["resummarised_from_rows_file"] = True
    L.dump(s, os.path.join(out_dir, "matrix6-summary.json"))
    writing = [r for r in rows if not r.get("skipped") and (r["work_n"] or r["git_plumbing_changed"]) and r["layout"] != "L0"]
    with gzip.open(os.path.join(out_dir, "matrix6-writing-rows.json.gz"), "wt") as f:
        f.write(json.dumps(writing, sort_keys=True, default=str))
    print(json.dumps({"rows": len(rows), "writing_rot1": len(writing), "props": s["properties"]}, indent=1))


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--resummarise":
        return resummarise(sys.argv[2])
    ap = argparse.ArgumentParser()
    ap.add_argument("trees"); ap.add_argument("registers"); ap.add_argument("gitops"); ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--only", default="P-ROOT,P-CWD,P-VEND,P-ENV,P-GIT")
    ap.add_argument("--focus", action="store_true")
    a = ap.parse_args()
    SAMPLE = {("status",), ("doctor",), ("version",), ("audit",), ("recover",), ("rebuild-memory",), ("update",),
              ("kernel", "trust"), ("kernel", "verify"), ("kernel", "reinstall"), ("memory", "query"), ("cit", "execute"),
              ("cit", "rollback"), ("decide",), ("plugins", "register"), ("tools", "install"), ("verify",),
              ("adapters", "generate"), ("upstream", "submit"), ("context", "compile"), ("policy", "effective")}

    def keep(leaf):
        if not a.focus:
            return True
        p = tuple(leaf["path"])
        return p[:1] in {("init",), ("adopt",), ("migrate",)} or p in SAMPLE
    T = json.load(open(a.trees)); R = json.load(open(a.registers))
    G = json.load(open(a.gitops))["trees"] if a.gitops != "-" else {}
    S, ids, rcs = T["scratch"], T["ids"], T["rcs"]
    OUT = os.path.abspath(a.out)
    os.makedirs(OUT, exist_ok=True)
    for d in ("upstream-dest", "release-out", "canon", "inbox", "proposals", "plugins-dir"):
        os.makedirs(os.path.join(S, "fixtures", d), exist_ok=True)
    only = set(a.only.split(","))
    jobs = []

    def add(kind, layout, tree, pos, root_flag, cwd_rel, full, extra_env=None):
        for v in L.VERSIONS:
            seen = set()
            for leaf in R[v]["leaves"]:
                if not keep(leaf):
                    continue
                for _, argv in invocations(leaf, ids, S, v, full):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv))
                        jobs.append((kind, layout, tree, v, pos, argv, "x", extra_env, root_flag, cwd_rel, S, ids, rcs))
            for i, argv in enumerate(combos(v, ids, S)):
                if tuple(argv) not in seen:
                    seen.add(tuple(argv))
                    jobs.append((kind, layout, tree, v, pos, argv, "combo:%d" % i, extra_env, root_flag, cwd_rel, S, ids, rcs))

    if "P-ROOT" in only:
        add("P-ROOT", "R6", T["trees"]["R6"], "P-ROOT", True, ".", True)
        for lay in ("R6RES", "R6CRASH", "R6V", "L0"):
            add("P-ROOT", lay, T["trees"][lay], "P-ROOT", True, ".", False)
    if "P-CWD" in only:
        for sub in CWD_POSITIONS:
            add("P-CWD", "R6", T["trees"]["R6"], "P-CWD:" + sub, False, sub, True)
    if "P-VEND" in only:
        for sub in VEND_POSITIONS:
            add("P-VEND", "R6V", T["trees"]["R6V"], "P-VEND:" + sub, False, sub, True)
    if "P-ENV" in only:
        for name, e in env_sets(S, L.WT, "<PROJ>").items():
            for sub in (".", "product", "governance/trust"):
                add("P-ENV", "R6", T["trees"]["R6"], "P-ENV:%s@%s" % (name, sub), False, sub, False, e)
    if "P-GIT" in only:
        for op, tree in sorted(G.items()):
            add("P-GIT", op, tree, "P-GIT:%s@root" % op, True, ".", False)
            add("P-GIT", op, tree, "P-GIT:%s@product" % op, False, "product", False)
    print("jobs=%d" % len(jobs), file=sys.stderr, flush=True)
    t0 = time.time()
    rows = []
    with gzip.open(os.path.join(OUT, "matrix6-rows.jsonl.gz"), "wt") as fo, \
         cf.ProcessPoolExecutor(max_workers=a.workers, initializer=worker_init, initargs=(S,)) as ex:
        for row in ex.map(run_job, jobs, chunksize=2):
            rows.append(row)
            fo.write(L.scrub(json.dumps(row, sort_keys=True, default=str)) + "\n")
            if len(rows) % 2000 == 0:
                print("%d/%d %.0fs" % (len(rows), len(jobs), time.time() - t0), file=sys.stderr, flush=True)
    s = summarise(rows)
    s["elapsed_seconds"] = round(time.time() - t0, 1)
    s["binaries_sha256"] = {v: L.sha_file(L.BINS[v]) for v in L.VERSIONS}
    L.dump(s, os.path.join(OUT, "matrix6-summary.json"))
    writing = [r for r in rows if not r.get("skipped") and (r["work_n"] or r["git_plumbing_changed"]) and r["layout"] != "L0"]
    with gzip.open(os.path.join(OUT, "matrix6-writing-rows.json.gz"), "wt") as f:
        f.write(L.scrub(json.dumps(writing, sort_keys=True, default=str)))
    print(json.dumps({"rows": len(rows), "writing_rot1": len(writing), "elapsed": s["elapsed_seconds"],
                      "props": s["properties"]}, indent=1))


if __name__ == "__main__":
    main()
