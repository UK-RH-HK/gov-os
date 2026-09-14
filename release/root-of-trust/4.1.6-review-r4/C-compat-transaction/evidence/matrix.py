#!/usr/bin/env python3
"""AR-0007 independent pre-RoT matrix on the RoT-1 revision-4 layout.

For every real legacy binary (4.1.2-4.1.5) and every leaf of its own register (register.py), synthesised invocations
(base with required arguments; each optional positional; each flag; each value option; destructive combinations) are run
on a FRESH COPY of a tree, in these positions:
  P-ROOT      --root <project root>                              layouts L0 (control), R4, R4RES, R4APP
  P-CWD:<d>   no --root, working directory <d> inside the project  (legacy default root discovery) on R4
  P-ENV:<e>   no --root, cwd root or product/, with environment variables a user might set          on R4
plus stateful chains at the root and from a subdirectory.
Every run records whole-tree before/after maps of the entire project (work tree, `.governance-runtime/`, `.git/`), Git
state, the child HOME, the root overlay classification, and `18` §9 installation state after the run.

Usage: matrix.py <trees.json> <registers.json> <out-dir> [--workers N] [--limit N] [--only positions]
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, shutil, subprocess, sys, tarfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import *  # noqa

OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}
SUBDIRS = [".", "product", "spec", "governance/overlay", "governance/views", "governance/trust", "governance/trust/state",
           "governance/framework.lock", ".governance-runtime"]


def values(name, path, ids, S, v):
    n = (name or "").upper()
    if n in ("ID", "GATE"):
        return {"cit": ids["CIT"], "gate": ids["GATE"], "handoff": ids["HANDOFF"]}.get(path[0], ids["GATE"] if n == "GATE" else ids["TASK"])
    if n == "DESCRIPTOR":
        return ids["PLUGIN_DESCRIPTOR"] if path and path[0] == "plugins" else ids["TOOL_DESCRIPTOR"]
    t = {"SOURCE": REL[v], "DIR": REL[v], "BATCH": "1", "STATUS": "IN_PROGRESS", "OPTION": "A", "BY": "owner", "METHOD": "human",
         "REASON": "ar7", "NAME": "ar7", "ALIAS": "ar7-alias", "QUERY": MARK, "TEXT": "create a task", "OBJECTIVE": "ar7 objective",
         "TITLE": "ar7", "CLASS": "documentation", "QUESTION": "ar7?", "FIELDS": "{}", "PROPOSAL": "ar7 proposal", "TRIGGER": "editorial",
         "TARGETS": ids["TASK"], "MANIFEST": ids["MANIFEST"], "TASK": ids["TASK"], "TO_ROLE": "backend-engineer", "REPORT": ids["REPORT"],
         "FILE": ids["RETURN"], "LESSON": "L-0001", "PACKET": ids["PACKET"], "DESTINATION": os.path.join(S, "fixtures", "upstream-dest"),
         "APPROVED_BY": "owner", "PLUGIN": "p-probe", "PLUGIN_ID": "p-probe", "INPUTS": "{}", "CAPABILITY": "code_intel",
         "POLICY": "SECURITY_POLICY", "WHAT": "governance", "VERDICT": "MIGRATION_PLAN_APPROVED", "RATIONALE": "ar7", "NOTES": "ar7",
         "NOTE": "ar7", "RADIUS": "R1", "OUT": os.path.join(S, "fixtures", "release-out"), "CANONICAL": os.path.join(S, "canon"),
         "INBOX": os.path.join(S, "fixtures", "inbox"), "PROPOSALS": os.path.join(S, "fixtures", "proposals"), "CANDIDATE": "hashed-ngram",
         "CANDIDATES": "hashed-ngram", "FEATURE": "FEAT-0001", "NODE": ids["TASK"], "SEEDS": ids["TASK"], "K": "8", "DEPTH": "1",
         "ROUTE": "lexical", "STEP": "ar7", "OPS": "9", "UTILISATION": "0.5", "TESTS_STATUS": "passed", "RECORD": "{}", "ATTRS": "{}",
         "EVIDENCE": "ar7", "INTENT": "ar7 intent", "DEPS": ids["TASK"], "ALLOWED": "docs/**", "REVIEWER_SESSION": "S-rev",
         "REVIEWER_ROLE": "migration-reviewer", "VERIFIER_ROLE": "migration-verifier", "GATE_ANSWER": "yes", "HELDOUT": "governance/tests/memory/heldout.yaml",
         "CERTIFICATION": "READY_FOR_INDEPENDENT_OS_VERIFICATION", "RESEARCH": "RES-0001", "OP": "serve", "WINDOW": "7", "ROLE": "owner",
         "LEVEL": "L5", "VERSION": v, "PATH": "product/readme.md", "PATTERN": "product/**", "KIND": "code_intel", "PING": "1"}
    return t.get(n, "ar7")


def combos(v, ids, S):
    s, o, n5 = REL[v], REL[OLDER[v]], REL["4.1.5"]
    return [
        ["update", "--apply", "--approve", "--source", s], ["update", "--apply", "--approve", "--source", o, "--by", "owner"],
        ["update", "--apply", "--approve", "--source", n5, "--by", "owner"], ["update", "--rollback", "--reason", "ar7"],
        ["update", "--rollback", "--approve", "--reason", "ar7", "--by", "owner"], ["update", "--check", "--source", s],
        ["init"], ["init", "--skip-index"], ["init", "--force", "--skip-index"], ["init", "--force", "--source", s, "--skip-index"],
        ["init", "--source", o, "--name", "ar7", "--skip-index"],
        ["kernel", "reinstall"], ["kernel", "reinstall", "--source", s], ["kernel", "override", "--reason", "ar7"], ["kernel", "verify"],
        ["adopt", "baseline"], ["adopt", "migrate", "--batch", "0", "--source", s, "--name", "ar7", "--alias", "ar7a"], ["adopt", "migrate", "--batch", "1"],
        ["adopt", "rollback", "--batch", "0"], ["adopt", "rollback", "--batch", "1"], ["adopt", "rollback", "--batch", "2"],
        ["migrate", "baseline"], ["migrate", "migrate", "--batch", "0", "--source", s], ["migrate", "rollback", "--batch", "1"],
        ["recover"], ["recover", "--dry-run"], ["rebuild-memory"], ["memory", "query", MARK],
        ["cit", "execute", ids["CIT"]], ["cit", "rollback", ids["CIT"], "--reason", "ar7"], ["decide", ids["GATE"], "--option", "A", "--by", "owner"],
        ["tools", "install", "--descriptor", ids["TOOL_DESCRIPTOR"], "--execute"], ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]],
        ["plugins", "unregister", "p-probe"], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"],
        ["memory", "select", "hashed-ngram", "--by", "owner"], ["memory", "heldout-starter", "--force"], ["lessons", "cluster", "--write"],
        ["upstream", "submit", ids["PACKET"], "--destination", os.path.join(S, "fixtures", "upstream-dest"), "--approved-by", "owner"],
        ["adapters", "generate"], ["verify", "product"], ["freeze-writes", "--reason", "ar7"], ["pause", "--reason", "ar7"], ["resume"],
        ["checkpoint", "create"], ["claims", "sweep"], ["task", "create", "--class", "documentation", "--objective", "x", "--title", "t", "--status", "READY"],
        ["doctor"], ["status"], ["audit"],
    ]


def invocations(leaf, ids, S, v, full=True):
    path = leaf["path"]
    base = list(path)
    for p in leaf["positionals"]:
        if p["required"]:
            base.append(values(p["name"], path, ids, S, v))
    for o in leaf["options"]:
        if o["required"]:
            base += [o["long"], values(o["value"], path, ids, S, v)]
    out = [("base", base)]
    if full:
        for p in leaf["positionals"]:
            if not p["required"]:
                out.append(("pos:" + p["name"], base + [values(p["name"], path, ids, S, v)]))
        for o in leaf["options"]:
            if o["required"]:
                continue
            if o["value"] is None:
                out.append(("flag:" + o["long"], base + [o["long"]]))
            else:
                out.append(("opt:" + o["long"], base + [o["long"], values(o["value"], path, ids, S, v)]))
    return out


def run_job(job):
    S, tree, layout, v, pos, argv, variant, extra_env, ids = job
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{layout}-{v}-{pos}-{'_'.join(argv[:3])}-{variant}")[:110] + "-" + hashlib.sha256(json.dumps([layout, v, pos, argv, variant, extra_env]).encode()).hexdigest()[:10]
    c = os.path.join(S, "runs", tag)
    copy_tree(tree, c)
    env = child_env(S, tag, extra_env)
    if pos == "P-ROOT":
        cwd, root = c, c
    else:
        sub = pos.split(":", 1)[1]
        cwd, root = os.path.join(c, sub), None
    before = snap(c, env["HOME"])
    r = gov(BINS[v], argv, env, cwd, root)
    after = snap(c, env["HOME"])
    cmp = compare(before, after)
    st = installation_state(c)
    row = {"layout": layout, "binary": v, "position": pos, "variant": variant, "argv": argv, "env": sorted(extra_env) if extra_env else [],
           "rc": r["_rc"], "ok": r.get("ok"), "code": code(r), **cmp,
           "classification_survives": overlay_classifies(c, overlay="governance/project" if layout == "L0" else "governance/overlay"),
           "state_after": st["state"], "diag_after": st["diagnostics_not_in_18_s9"],
           "plugin_or_tool_executed": os.path.exists(env["AR7_MARKER"])}
    if not (cmp["work_changed"] or cmp["runtime_changed"] or cmp["git_files_changed"] or cmp["git_state_changed"]):
        for k in list(row):
            if k.endswith("_paths"):
                row[k] = []
    if layout != "L0" and cmp["work_changed"]:
        kt = gov(BINS[v], ["kernel", "trust"], env, cwd, root)
        row["legacy_kernel_trust_after"] = {"ok": kt.get("ok"), "code": code(kt), "verified": result(kt).get("verified")}
    shutil.rmtree(c, ignore_errors=True) if os.environ.get("AR7_DISCARD_RUNS") == "1" else None
    return row


CHAIN_STEPS = {
    "adoption": lambda v, ids, S, mf: [["adopt", "baseline"], ["adopt", "inventory"], ["adopt", "classify"], ["adopt", "map"], ["adopt", "plan"], ["adopt", "test-design"],
                                      ["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"], ["adopt", "migrate", "--batch", "0", "--source", REL[v], "--name", "ar7", "--alias", "ar7a"],
                                      ["adopt", "migrate", "--batch", "1"], ["adopt", "migrate", "--batch", "2"], ["adopt", "migrate", "--batch", "3"],
                                      ["adopt", "verify-migration", "--verdict", "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"], ["adopt", "extract-legacy"],
                                      ["adopt", "build-memory"], ["memory", "query", MARK], ["adopt", "rollback", "--batch", "1"], ["adopt", "rollback", "--batch", "0"]],
    "init_then_use": lambda v, ids, S, mf: [["init", "--skip-index"], ["kernel", "trust"], ["rebuild-memory"], ["memory", "query", MARK], ["adapters", "generate"]],
    "init_force_then_use": lambda v, ids, S, mf: [["init", "--force", "--source", REL[v], "--skip-index"], ["kernel", "trust"], ["rebuild-memory"], ["memory", "query", MARK]],
    "update": lambda v, ids, S, mf: [["update", "--check", "--source", REL[v]], ["update", "--apply", "--source", REL[v]], ["gate", "present", "{gate}"],
                                     ["decide", "{gate}", "--option", "A", "--by", "owner"], ["update", "--apply", "--approve", "--source", REL[v]], ["update", "--rollback", "--reason", "ar7"]],
    "cit_rot1_paths": lambda v, ids, S, mf: [["task", "create", "--class", "documentation", "--objective", "c", "--title", "c", "--status", "READY"],
                                             ["cit", "propose", "--proposal", "p", "--trigger", "editorial", "--targets", "{task}", "--manifest", mf], ["cit", "simulate", "{cit}"],
                                             ["cit", "approve", "{cit}", "--by", "orchestrator", "--method", "auto"], ["gate", "present", "{gate}"],
                                             ["decide", "{gate}", "--option", "A", "--by", "owner"], ["cit", "approve", "{cit}", "--by", "owner", "--method", "human"], ["cit", "execute", "{cit}"]],
    "plugins_tools": lambda v, ids, S, mf: [["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], ["capabilities", "invoke", "--plugin", "p-probe", "--inputs", "{}"],
                                            ["tools", "install", "--descriptor", ids["TOOL_DESCRIPTOR"], "--execute"], ["rebuild-memory"]],
    "recover_reinstall": lambda v, ids, S, mf: [["recover"], ["kernel", "reinstall"], ["kernel", "verify"], ["recover"]],
}


def run_chain(job):
    S, tree, layout, v, pos, name, ids = job
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", f"chain-{layout}-{v}-{pos}-{name}")
    c = os.path.join(S, "runs", tag)
    copy_tree(tree, c)
    env = child_env(S, tag)
    mf = os.path.join(S, "fixtures", f"cit-rot1-{tag}.json")
    json.dump([{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": "schema_version: 1.0.0\nclassifications: []\n"},
               {"op": "write_file", "path": "governance/trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
               {"op": "delete_file", "path": "governance/trust/framework.lock"},
               {"op": "write_file", "path": "product/restricted-plan.md", "content": "overwritten\n"}], open(mf, "w"))
    if pos == "P-ROOT":
        cwd, root = c, c
    else:
        cwd, root = os.path.join(c, pos.split(":", 1)[1]), None
    start = snap(c, env["HOME"])
    ctx = {"gate": ids["GATE"], "task": ids["TASK"], "cit": ids["CIT"]}

    def subst(x):
        for k, val in ctx.items():
            x = x.replace("{" + k + "}", val)
        return x
    steps = []
    for st in CHAIN_STEPS[name](v, ids, S, mf):
        argv = [subst(x) for x in st]
        r = gov(BINS[v], argv, env, cwd, root)
        rid = result(r).get("id")
        if argv[:2] == ["task", "create"] and rid:
            ctx["task"] = rid
        if argv[:2] == ["cit", "propose"] and rid:
            ctx["cit"] = rid
        m = re.search(r"(HDG-\d+)", json.dumps(r.get("error") or {})) or re.search(r"(HDG-\d+)", json.dumps(result(r)))
        if m and (argv[0] in ("update", "cit")):
            ctx["gate"] = m.group(1)
        now = snap(c, env["HOME"])
        cmp = compare(start, now)
        hits = [h.get("path") for h in (result(r).get("hits") or []) if isinstance(h, dict)] if argv[:2] == ["memory", "query"] else None
        steps.append({"argv": argv, "ok": r.get("ok"), "code": code(r), "work_changed_since_start": cmp["work_changed"],
                      "runtime_changed_since_start": cmp["runtime_changed"], "git_changed": cmp["git_state_changed"] or cmp["git_files_changed"],
                      "work_paths_n": cmp["work_n"], "work_paths": cmp["work_paths"][:25], "restricted_hits": [h for h in (hits or []) if "restricted" in (h or "")] if hits is not None else None,
                      "verified": result(r).get("verified") if argv[:2] == ["kernel", "trust"] else None})
    st = installation_state(c)
    end = compare(start, snap(c, env["HOME"]))
    return {"layout": layout, "binary": v, "position": pos, "chain": name, "steps": steps, "state_after": st["state"], "diag_after": st["diagnostics_not_in_18_s9"],
            "occupation_after": st["occupation"], "classification_survives": overlay_classifies(c), "work_changed": end["work_changed"], "work_n": end["work_n"],
            "work_paths": end["work_paths"], "runtime_changed": end["runtime_changed"], "git_changed": end["git_state_changed"] or end["git_files_changed"],
            "trust_paths_changed": [p for p in changed(start["work"], snap(c)["work"]) if p.startswith("governance/trust")][:25]}


def make_canon(S):
    d = os.path.join(S, "canon")
    if os.path.isdir(d):
        return d
    os.makedirs(d)
    tar = os.path.join(S, "canon.tar")
    with open(tar, "wb") as f:
        subprocess.run(["git", "archive", "--format=tar", "HEAD", "framework", "release/releases", "fixtures"], cwd=WT, stdout=f, check=True, env=git_env(S))
    with tarfile.open(tar) as t:
        t.extractall(d)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trees")
    ap.add_argument("registers")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="root,cwd,env,chains")
    a = ap.parse_args()
    T = json.load(open(a.trees))
    R = json.load(open(a.registers))
    S = T["scratch"]
    ids = T["ids"]
    os.makedirs(a.out, exist_ok=True)
    canon = make_canon(S)
    pdir = os.path.join(S, "fixtures", "plugins-dir")
    os.makedirs(pdir, exist_ok=True)
    shutil.copy(ids["PLUGIN_DESCRIPTOR"], os.path.join(pdir, "p-env.yaml"))
    only = set(a.only.split(","))
    jobs = []
    if "root" in only:
        for layout in ("L0", "R4", "R4RES", "R4APP"):
            for v in VERSIONS:
                seen = set()
                for leaf in R[v]["leaves"]:
                    for name, argv in invocations(leaf, ids, S, v, full=layout != "R4APP"):
                        if tuple(argv) not in seen:
                            seen.add(tuple(argv)); jobs.append((S, T["trees"][layout], layout, v, "P-ROOT", argv, name, None, ids))
                for i, argv in enumerate(combos(v, ids, S)):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv)); jobs.append((S, T["trees"][layout], layout, v, "P-ROOT", argv, f"combo:{i}", None, ids))
    if "cwd" in only:
        for sub in SUBDIRS:
            for v in VERSIONS:
                seen = set()
                for leaf in R[v]["leaves"]:
                    for name, argv in invocations(leaf, ids, S, v, full=False):
                        if tuple(argv) not in seen:
                            seen.add(tuple(argv)); jobs.append((S, T["trees"]["R4"], "R4", v, "P-CWD:" + sub, argv, name, None, ids))
                for i, argv in enumerate(combos(v, ids, S)):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv)); jobs.append((S, T["trees"]["R4"], "R4", v, "P-CWD:" + sub, argv, f"combo:{i}", None, ids))
    if "env" in only:
        envs = {"KERNEL_SOURCE": lambda v: {"GOV_KERNEL_SOURCE": REL[v]}, "CANONICAL_ROOT": lambda v: {"GOV_CANONICAL_ROOT": canon},
                "PLUGINS_DIR": lambda v: {"GOV_PLUGINS_DIR": pdir}, "ROLE_OWNER": lambda v: {"GOV_ROLE": "owner", "GOV_SESSION": "S-user"},
                "ALL": lambda v: {"GOV_KERNEL_SOURCE": REL[v], "GOV_CANONICAL_ROOT": canon, "GOV_PLUGINS_DIR": pdir, "GOV_ROLE": "owner", "GOV_SESSION": "S-user", "GOV_DISABLE_PLUGINS": "0"}}
        for en, fn in envs.items():
            for sub in (".", "product"):
                for v in VERSIONS:
                    for i, argv in enumerate(combos(v, ids, S)):
                        jobs.append((S, T["trees"]["R4"], "R4", v, "P-CWD:" + sub, argv, f"env:{en}:combo:{i}", fn(v), ids))
    if a.limit:
        jobs = jobs[: a.limit]
    print(f"jobs={len(jobs)}", file=sys.stderr, flush=True)
    rows = []
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        for row in ex.map(run_job, jobs, chunksize=4):
            rows.append(row)
            if len(rows) % 250 == 0:
                print(f"{len(rows)}/{len(jobs)}", file=sys.stderr, flush=True)
    # write the main matrix BEFORE chains so a chain failure never loses it
    with open(os.path.join(a.out, "matrix-rows.jsonl"), "w") as f:
        for r in rows:
            f.write(scrub(json.dumps(r, sort_keys=True), S) + "\n")
    chains = []
    if "chains" in only:
        cj = []
        for layout in ("L0", "R4"):
            for v in VERSIONS:
                for pos in (["P-ROOT"] if layout == "L0" else ["P-ROOT", "P-CWD:.", "P-CWD:product", "P-CWD:governance/trust", "P-CWD:governance/overlay"]):
                    for name in CHAIN_STEPS:
                        cj.append((S, T["trees"][layout], layout, v, pos, name, ids))
        with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
            chains = list(ex.map(run_chain, cj, chunksize=1))
    with open(os.path.join(a.out, "matrix-rows.jsonl"), "w") as f:
        for r in rows:
            f.write(scrub(json.dumps(r, sort_keys=True), S) + "\n")
    with open(os.path.join(a.out, "matrix-chains.json"), "w") as f:
        f.write(scrub(json.dumps(chains, indent=1, sort_keys=True), S))
    print(json.dumps({"jobs": len(rows), "chains": len(chains)}))


if __name__ == "__main__":
    main()
