#!/usr/bin/env python3
"""AR-0013 independent pre-RoT matrix on the RoT-1 revision-5 layout.

Every leaf of each real legacy binary's own register (registers5.json: --help recursion cross-checked with source), with
argument synthesis, run against fresh copies of the revision-5 trees in these positions:
  P-ROOT            --root <project>                                   (R5, R5RES, R5NOSURG, R5V, control L0)
  P-CWD:<dir>       no --root, working directory <dir>, every depth incl. inside the PPS and the transaction area (R5)
  P-VEND:<dir>      no --root, inside or above a committed legacy sub-project (R5V)
  P-ENV:<set>@<dir> no --root, user environment variables (R5)
  P-GIT:<op>@<pos>  --root / product on trees produced by ordinary Git operations (gitops5.py)
Each row: whole-tree before/after (work tree, .governance-runtime, .git files and plumbing, child HOME, kernel cache),
changed paths partitioned, `18` §9/§9.1 state before and after (c5lib.state_r5, encoded from the text), the `18` §6.1
kernel check against the release content set, nested legacy markers, and the overlay classifications.

Written for AR-0013; argument synthesis is independent of P3r3, review r4 C and ST5.
Usage: matrix5.py <trees.json> <registers5.json> <gitops-trees.json|-> <out-dir> [--workers N] [--only KIND,...]
"""
import argparse, collections, concurrent.futures as cf, gzip, hashlib, json, os, re, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c5lib as L  # noqa
import yaml

OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}
CWD_POSITIONS = [".", "product", "product/customers", "docs", "spec", "spec/audits", "spec/now", "governance",
                 "governance/overlay", "governance/overlay/plugins", "governance/views", "governance/trust",
                 "governance/trust/kernel", "governance/trust/kernel/policies", "governance/trust/state",
                 "governance/trust/lineage", "governance/trust/root", "governance/framework.lock", ".governance-runtime",
                 ".governance-runtime/trust-tx", ".governance-runtime/trust-tx/done/TX-" + "0f" * 16,
                 ".governance-runtime/legacy-quarantine/update", ".governance-runtime/snapshots/ci-previous"]
VEND_POSITIONS = ["vendor", "vendor/legacypkg", "vendor/legacypkg/product", "vendor/legacypkg/governance/project"]


def env_sets(S, WT, proj):
    return {"KSRC": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"]},
            "CANON": {"GOV_CANONICAL_ROOT": WT},
            "PLUGDIR": {"GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir")},
            "ROLESESS": {"GOV_ROLE": "owner", "GOV_SESSION": "S-env"},
            "CACHE_IN_PROJECT": {"GOV_KERNEL_CACHE": os.path.join(proj, ".cache", "gov")},
            "ALL": {"GOV_KERNEL_SOURCE": L.REL["4.1.5"], "GOV_CANONICAL_ROOT": WT, "GOV_PLUGINS_DIR": os.path.join(S, "fixtures", "plugins-dir"),
                    "GOV_ROLE": "owner", "GOV_SESSION": "S-env"}}


def value(name, path, ids, S, v):
    n = (name or "").upper()
    grp = path[0] if path else ""
    if n in ("ID",):
        return {"cit": ids["CIT"], "gate": ids["GATE"], "handoff": ids["HANDOFF"], "task": ids["TASK"]}.get(grp, ids["TASK"])
    if n == "DESCRIPTOR":
        return ids["PLUGIN_DESCRIPTOR"] if grp == "plugins" else ids["TOOL_DESCRIPTOR"]
    fx = os.path.join(S, "fixtures")
    table = {"SOURCE": L.REL[v], "DIR": L.REL[v], "BATCH": "1", "STATUS": "IN_PROGRESS", "OPTION": "A", "BY": "owner", "METHOD": "human",
             "REASON": "ar13", "NAME": "ar13", "ALIAS": "ar13-alias", "QUERY": L.MARK, "TEXT": "create a documentation task", "OBJECTIVE": "ar13",
             "TITLE": "ar13", "CLASS": "documentation", "QUESTION": "ar13?", "FIELDS": "{}", "PROPOSAL": "ar13 proposal", "TRIGGER": "editorial",
             "TARGETS": ids["TASK"], "MANIFEST": ids["MANIFEST"], "TASK": ids["TASK"], "TO_ROLE": "backend-engineer", "REPORT": ids["REPORT"],
             "FILE": ids["RETURN"], "LESSON": "L-0001", "PACKET": ids["PACKET"], "DESTINATION": os.path.join(fx, "upstream-dest"),
             "APPROVED_BY": "owner", "PLUGIN": "p-probe", "PLUGIN_ID": "p-probe", "INPUTS": "{}", "CAPABILITY": "code_intel",
             "POLICY": "SECURITY_POLICY", "WHAT": "governance", "VERDICT": "MIGRATION_PLAN_APPROVED", "RATIONALE": "ar13", "NOTES": "ar13",
             "NOTE": "ar13", "RADIUS": "R1", "OUT": os.path.join(fx, "release-out"), "CANONICAL": os.path.join(fx, "canon"),
             "INBOX": os.path.join(fx, "inbox"), "PROPOSALS": os.path.join(fx, "proposals"), "CANDIDATE": "hashed-ngram",
             "CANDIDATES": "hashed-ngram", "FEATURE": "FEAT-0001", "NODE": ids["TASK"], "SEEDS": ids["TASK"], "K": "8", "DEPTH": "1",
             "ROUTE": "lexical", "STEP": "ar13", "OPS": "9", "UTILISATION": "0.5", "TESTS_STATUS": "passed", "RECORD": "{}", "ATTRS": "{}",
             "EVIDENCE": "ar13", "INTENT": "ar13 intent", "DEPS": ids["TASK"], "ALLOWED": "docs/**", "REVIEWER_SESSION": "S-rev",
             "REVIEWER_ROLE": "migration-reviewer", "VERIFIER_ROLE": "migration-verifier", "GATE_ANSWER": "yes",
             "HELDOUT": "governance/tests/memory/heldout.yaml", "CERTIFICATION": "READY_FOR_INDEPENDENT_OS_VERIFICATION",
             "RESEARCH": "RES-0001", "OP": "serve", "NEXT_ACTION": "continue", "FAMILY": "layout", "GATE": ids["GATE"]}
    return table.get(n, "ar13")


def invocations(leaf, ids, S, v, full):
    path = leaf["path"]
    base = list(path)
    for p in leaf["positionals"]:
        if p["required"]:
            base.append(value(p["name"], path, ids, S, v))
    for o in leaf["options"]:
        if o["required"]:
            base += [o["long"], value(o["value"], path, ids, S, v)]
    out = [("base", base)]
    if full:
        for p in leaf["positionals"]:
            if not p["required"]:
                out.append(("pos:" + p["name"], base + [value(p["name"], path, ids, S, v)]))
        for o in leaf["options"]:
            if o["required"]:
                continue
            if o["value"] is None:
                out.append(("flag:" + o["long"], base + [o["long"]]))
            else:
                out.append(("opt:" + o["long"], base + [o["long"], value(o["value"], path, ids, S, v)]))
    return out


def combos(v, ids, S):
    s, o, n5 = L.REL[v], L.REL[OLDER[v]], L.REL["4.1.5"]
    return [["update", "--apply", "--approve", "--source", s, "--by", "owner"], ["update", "--apply", "--approve", "--source", o, "--by", "owner"],
            ["update", "--apply", "--approve", "--source", n5], ["update", "--rollback", "--approve", "--reason", "ar13", "--by", "owner"],
            ["init", "--force", "--skip-index"], ["init", "--force", "--source", s, "--skip-index"], ["init", "--source", o, "--name", "ar13", "--skip-index"],
            ["kernel", "reinstall", "--source", s], ["adopt", "migrate", "--batch", "0", "--source", s, "--name", "ar13", "--alias", "ar13a"],
            ["adopt", "rollback", "--batch", "0"], ["migrate", "migrate", "--batch", "0", "--source", s], ["migrate", "rollback", "--batch", "0"],
            ["cit", "execute", ids["CIT"]], ["cit", "rollback", ids["CIT"], "--reason", "ar13"],
            ["decide", ids["GATE"], "--option", "A", "--by", "owner"], ["tools", "install", "--descriptor", ids["TOOL_DESCRIPTOR"], "--execute"],
            ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"],
            ["memory", "heldout-starter", "--force"], ["lessons", "cluster", "--write"], ["recover"], ["rebuild-memory"],
            ["upstream", "submit", ids["PACKET"], "--destination", os.path.join(S, "fixtures", "upstream-dest"), "--approved-by", "owner"],
            ["verify", "product"], ["adapters", "generate"], ["checkpoint", "create", "--next-action", "x"]]


def classifications_ok(root):
    for ov in ("governance/overlay", "governance/project"):
        p = os.path.join(root, ov, "DATA_SENSITIVITY.yaml")
        if L.kind(p) == "file":
            try:
                d = yaml.safe_load(open(p)) or {}
                pats = {c.get("pattern") for c in (d.get("classifications") or []) if isinstance(c, dict)}
                return {"product/restricted-plan.md", "product/customers/**"} <= pats
            except Exception:
                return False
    return None


OCC_FILES = set(L.OCCUPATION)


def partition(paths):
    c = collections.Counter()
    for p in paths:
        if p.startswith("governance/trust/") or p == "governance/trust":
            c["pps_trust"] += 1
        elif p in OCC_FILES or p.startswith("governance/framework.lock/"):
            c["pps_occupation"] += 1
        elif p.startswith(".governance-runtime/trust-tx"):
            c["pps_txarea"] += 1
        elif p.startswith("governance/overlay/") or p == "governance/overlay":
            c["overlay"] += 1
        elif p.startswith("governance/"):
            c["governance_other"] += 1
        elif p.startswith(".governance-runtime"):
            c["runtime_other"] += 1
        elif p.startswith("spec/"):
            c["spec"] += 1
        else:
            c["other"] += 1
    return dict(c)


_W = {}


def worker_init(S):
    _W["dir"] = os.path.join(S, "w", str(os.getpid()))
    os.makedirs(_W["dir"], exist_ok=True)
    _W["n"] = 0


def run_job(job):
    kind, layout, tree, v, pos, argv, variant, extra_env, root_flag, cwd_rel, S, ids, rcs = job
    _W["n"] += 1
    tag = "%s-%d" % (os.getpid(), _W["n"])
    c = os.path.join(_W["dir"], "run-" + str(_W["n"]))
    L.copy_tree(tree, c)
    home = os.path.join(_W["dir"], "home-" + str(_W["n"]))
    cache = os.path.join(_W["dir"], "cache-" + v)
    ee = {}
    for k, val in (extra_env or {}).items():
        ee[k] = val.replace("<PROJ>", c)
    env = L.child_env(home, cache, ee)
    cwd = os.path.join(c, cwd_rel)
    if not os.path.isdir(cwd):
        return {"kind": kind, "layout": layout, "binary": v, "position": pos, "argv": argv, "variant": variant, "skipped": "cwd_absent"}
    githome = os.path.join(_W["dir"], "githome")
    st_before = L.state_r5(c)
    before = L.snap(c, home, cache, githome)
    r = L.gov(L.BINS[v], argv, env, cwd, c if root_flag else None)
    after = L.snap(c, home, cache, githome)
    cmp = L.compare(before, after)
    st_after = L.state_r5(c)
    work = cmp["work"]
    rt = cmp["runtime"]
    # free disk immediately: this row keeps only digests and changed-path lists, never the tree
    import shutil as _sh
    _sh.rmtree(c, ignore_errors=True)
    _sh.rmtree(home, ignore_errors=True)
    ch_all = work + rt
    ktamp = L.kernel_tampered(c, rcs) if (layout != "L0" and L.kind(os.path.join(c, "governance/trust/kernel")) == "dir") else None
    row = {"kind": kind, "layout": layout, "binary": v, "position": pos, "variant": variant, "argv": argv,
           "rc": r["_rc"], "ok": r.get("ok"), "code": L.code(r), "secs": r["_secs"],
           "tree_digest_before": L.digest_map({k: before[k] for k in ("work", "runtime", "git_files")})[:24],
           "tree_digest_after": L.digest_map({k: after[k] for k in ("work", "runtime", "git_files")})[:24],
           "work_n": len(work), "runtime_n": len(rt), "git_files_n": len(cmp["git_files"]), "git_plumbing_changed": cmp["git_plumbing_changed"],
           "git_index_stat_only": cmp["git_index_stat_only"], "home_n": len(cmp["home"]), "cache_n": len(cmp["cache"]),
           "paths": ch_all[:40], "home_paths": cmp["home"][:8], "partition": partition(ch_all),
           "state_before": st_before["state"], "state_after": st_after["state"], "reasons_after": st_after["reasons"],
           "reports_after": st_after["reports"], "kernel_tampered_after": ktamp, "classifications_ok_after": classifications_ok(c)}
    return row


def summarise(rows):
    s = {"rows": len(rows), "skipped": sum(1 for r in rows if r.get("skipped"))}
    rows = [r for r in rows if not r.get("skipped")]
    agg = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        k = f"{r['kind']}|{r['layout']}|{r['position']}"
        a = agg[k]
        a["rows"] += 1
        wrote = r["work_n"] or r["runtime_n"] or r["git_files_n"] or r["git_plumbing_changed"]
        a["rows_writing_project"] += bool(wrote)
        a["rows_writing_work"] += bool(r["work_n"])
        a["rows_writing_git"] += bool(r["git_files_n"] or r["git_plumbing_changed"])
        a["rows_writing_home"] += bool(r["home_n"])
        for p, n in r["partition"].items():
            a["rows_" + p] += 1
        a["state_after_" + r["state_after"]] += 1
        a["classification_lost"] += (r["classifications_ok_after"] is False)
    s["by_kind_layout_position"] = {k: dict(v) for k, v in sorted(agg.items())}
    props = {}
    # LP-1r: root-anchored rows on intact revision-5 trees write nothing to the project (work tree, runtime, .git)
    lp1r = [r for r in rows if r["kind"] == "P-ROOT" and r["layout"] in ("R5", "R5RES", "R5NOSURG", "R5V")]
    viol = [r for r in lp1r if r["work_n"] or r["runtime_n"] or r["git_files_n"] or r["git_plumbing_changed"]]
    props["LP-1r_root_anchored_no_project_write"] = {"rows": len(lp1r), "violations": len(viol), "sample": [(r["layout"], r["binary"], r["argv"][:4], r["paths"][:5]) for r in viol[:10]]}
    # LP-1s as stated in 26 §4: every write under governance/** other than the overlay files leaves a state that is not COMPLETE
    subrows = [r for r in rows if r["kind"] in ("P-CWD", "P-ENV", "P-VEND")]
    v2 = [r for r in subrows if any(p.startswith("governance/") and not p.startswith("governance/overlay/") for p in r["paths"]) and r["state_after"] == "COMPLETE"]
    props["LP-1s_as_stated_26_s4"] = {"rows": len(subrows), "counterexamples": len(v2),
                                     "sample": sorted({(r["position"], " ".join(r["argv"][:2]), tuple(p for p in r["paths"] if p.startswith("governance/"))[:3]) for r in v2})[:12]}
    # R2-H4 class on kernel/trust/lock/occupation: any change there leaves a state that is not COMPLETE, or KERNEL_TAMPERED
    v3 = [r for r in rows if r["layout"] != "L0" and (r["partition"].get("pps_trust") or r["partition"].get("pps_occupation")) and r["state_after"] == "COMPLETE" and not r["kernel_tampered_after"]]
    props["R2-H4_trust_kernel_occupation_change_not_left_COMPLETE"] = {"violations": len(v3), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["paths"][:6]) for r in v3[:10]]}
    # PPS transaction area (18 §8) written by a legacy binary
    v4 = [r for r in rows if r["partition"].get("pps_txarea")]
    props["legacy_writes_in_transaction_area_18_s8"] = {"rows": len(v4), "states_after": dict(collections.Counter(r["state_after"] for r in v4)),
                                                        "sample": [(r["layout"], r["position"], r["argv"][:3], r["paths"][:4]) for r in v4[:6]]}
    # nested legacy installs: every new marker is PARTIAL (under governance/) or reported
    v5 = [r for r in rows if r["layout"] != "L0" and (r["reports_after"] or "nested_legacy_install" in r["reasons_after"])]
    props["nested_marker_rows_reported"] = {"rows": len(v5), "by_state": dict(collections.Counter(r["state_after"] for r in v5))}
    v6 = [r for r in rows if r["layout"] != "L0" and r["classifications_ok_after"] is False]
    props["classification_lost_on_rot1_layouts"] = {"rows": len(v6), "sample": [(r["kind"], r["layout"], r["position"], r["argv"][:3], r["state_after"]) for r in v6[:10]]}
    # writes on Git-op trees while the tree was COMPLETE before the invocation
    v7 = [r for r in rows if r["kind"] == "P-GIT" and r["state_before"] == "COMPLETE" and (r["work_n"] or r["git_files_n"])]
    props["gitop_trees_writes_while_COMPLETE_before"] = {"rows": len(v7), "sample": [(r["layout"], r["position"], r["argv"][:3], r["paths"][:5], r["state_after"]) for r in v7[:12]]}
    v8 = [r for r in rows if r["kind"] == "P-GIT" and r["state_before"] != "COMPLETE" and (r["work_n"] or r["git_files_n"]) and r["state_after"] == "COMPLETE"]
    props["gitop_trees_writes_leaving_COMPLETE"] = {"rows": len(v8), "sample": [(r["layout"], r["position"], r["argv"][:3]) for r in v8[:12]]}
    s["properties"] = props
    wc = collections.Counter()
    for r in rows:
        if (r["work_n"] or r["git_files_n"]) and r["layout"] != "L0":
            wc[(r["kind"], " ".join(r["argv"][:2]))] += 1
    s["writing_commands_rot1_layouts"] = {f"{k[0]}|{k[1]}": n for k, n in sorted(wc.items())}
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trees"); ap.add_argument("registers"); ap.add_argument("gitops"); ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--only", default="P-ROOT,P-CWD,P-VEND,P-ENV,P-GIT")
    ap.add_argument("--focus", action="store_true",
                    help="restrict each register to the mutating command families (init/adopt/migrate) plus a fixed control "
                         "sample of non-mutating commands; the full-register no-write property is corroborated separately")
    a = ap.parse_args()
    SAMPLE = {("status",), ("doctor",), ("version",), ("audit",), ("recover",), ("rebuild-memory",), ("update",),
              ("kernel", "trust"), ("kernel", "verify"), ("kernel", "reinstall"), ("kernel", "override"),
              ("memory", "query"), ("cit", "execute"), ("cit", "rollback"), ("decide",), ("plugins", "register"),
              ("tools", "install"), ("verify",), ("adapters", "generate"), ("upstream", "submit"), ("context", "compile")}

    def keep(leaf):
        if not a.focus:
            return True
        p = tuple(leaf["path"])
        return p[:1] in {("init",), ("adopt",), ("migrate",)} or p in SAMPLE
    T = json.load(open(a.trees)); R = json.load(open(a.registers))
    G = json.load(open(a.gitops))["trees"] if a.gitops != "-" else {}
    S = T["scratch"]; ids = T["ids"]; rcs = T["rcs"]
    OUT = os.path.abspath(a.out)
    os.makedirs(OUT, exist_ok=True)
    only = set(a.only.split(","))
    for d in ("upstream-dest", "release-out", "canon", "inbox", "proposals", "plugins-dir"):
        os.makedirs(os.path.join(S, "fixtures", d), exist_ok=True)
    jobs = []

    def reg_jobs(kind, layout, tree, pos, root_flag, cwd_rel, full, extra_env=None):
        for v in L.VERSIONS:
            seen = set()
            for leaf in R[v]["leaves"]:
                if not keep(leaf):
                    continue
                for name, argv in invocations(leaf, ids, S, v, full):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv))
                        jobs.append((kind, layout, tree, v, pos, argv, name, extra_env, root_flag, cwd_rel, S, ids, rcs))
            for i, argv in enumerate(combos(v, ids, S)):
                if tuple(argv) not in seen:
                    seen.add(tuple(argv))
                    jobs.append((kind, layout, tree, v, pos, argv, "combo:%d" % i, extra_env, root_flag, cwd_rel, S, ids, rcs))

    if "P-ROOT" in only:
        # full register (every option variant) on R5 and the L0 control — the LP-1r no-write claim; base+combos elsewhere
        for lay in ("R5", "L0"):
            reg_jobs("P-ROOT", lay, T["trees"][lay], "P-ROOT", True, ".", True)
        for lay in ("R5RES", "R5NOSURG", "R5V"):
            reg_jobs("P-ROOT", lay, T["trees"][lay], "P-ROOT", True, ".", False)
    if "P-CWD" in only:
        for sub in CWD_POSITIONS:
            reg_jobs("P-CWD", "R5", T["trees"]["R5"], "P-CWD:" + sub, False, sub, True)
    if "P-VEND" in only:
        for sub in VEND_POSITIONS:
            reg_jobs("P-VEND", "R5V", T["trees"]["R5V"], "P-VEND:" + sub, False, sub, True)
    if "P-ENV" in only:
        for name, e in env_sets(S, L.WT, "<PROJ>").items():
            for sub in (".", "product", "governance/trust"):
                reg_jobs("P-ENV", "R5", T["trees"]["R5"], f"P-ENV:{name}@{sub}", False, sub, False, e)
    if "P-GIT" in only:
        for op, tree in sorted(G.items()):
            reg_jobs("P-GIT", op, tree, f"P-GIT:{op}@root", True, ".", False)
            reg_jobs("P-GIT", op, tree, f"P-GIT:{op}@product", False, "product", False)
    print(f"jobs={len(jobs)}", file=sys.stderr, flush=True)
    t0 = time.time()
    rows = []
    rows_path = os.path.join(OUT, "matrix5-rows.jsonl.gz")
    with gzip.open(rows_path, "wt") as fo, cf.ProcessPoolExecutor(max_workers=a.workers, initializer=worker_init, initargs=(S,)) as ex:
        for row in ex.map(run_job, jobs, chunksize=2):
            rows.append(row)
            fo.write(L.scrub(json.dumps(row, sort_keys=True, default=str)) + "\n")
            if len(rows) % 1000 == 0:
                print(f"{len(rows)}/{len(jobs)} ({time.time()-t0:.0f}s)", file=sys.stderr, flush=True)
    s = summarise(rows)
    s["elapsed_seconds"] = round(time.time() - t0, 1)
    s["binaries_sha256"] = {v: L.sha_file(L.BINS[v]) for v in L.VERSIONS}
    L.dump(s, os.path.join(OUT, "matrix5-summary.json"))
    writing = [r for r in rows if not r.get("skipped") and (r["work_n"] or r["runtime_n"] or r["git_files_n"] or r["git_plumbing_changed"]) and r["layout"] != "L0"]
    L.dump(writing, os.path.join(OUT, "matrix5-writing-rows-rot1-layouts.json"))
    print(json.dumps({"rows": len(rows), "writing_rot1": len(writing), "elapsed": s["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
