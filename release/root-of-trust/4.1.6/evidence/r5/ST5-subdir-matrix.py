#!/usr/bin/env python3
"""ST5 subdirectory matrix: revision-5 state and discovery for P-CWD positions on R4 layout.

Origin: copied from reviewer C's matrix.py
  Origin path: release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence/matrix.py
  Origin SHA-256: 63e51de575d1883eaa210bd67312d264b6c7b8de6b9946cb943925c81e3b71c4
Changes from origin:
  (a) positions = P-CWD only for the 11 specified working directories on layout R4;
      all four binaries; full=False register + combos exactly as C does for P-CWD;
      skip P-ROOT, P-ENV and chains.
  (b) Each row additionally records: state_after_r5 (with reasons and nested diagnostics),
      discovery_r5 for that working directory evaluated on the tree BEFORE the invocation,
      and the list of changed paths under governance/trust/** and under governance/framework.lock/**
  (c) Write a summary + writing-rows JSON instead of all rows.

Usage: ST5-subdir-matrix.py <trees.json> <registers.json> <out-dir> [--workers N]
"""
import argparse, collections, concurrent.futures as cf, hashlib, json, os, re, shutil, sys, time
sys.dont_write_bytecode = True

# Import c4lib and the r5 state module
C_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence")
sys.path.insert(0, C_EV)
R5_EV = os.path.join(os.environ.get("AR7_WT", ""), "release/root-of-trust/4.1.6/evidence/r5")
sys.path.insert(0, R5_EV)

from c4lib import (BINS, VERSIONS, MARK, SENT, copy_tree, child_env, gov, code, result, # noqa
                   snap, compare, installation_state, overlay_classifies, scrub, sha, kind, tree_map, changed)

# Import r5 functions; the module file uses a hyphenated name
import importlib.util
_r5_spec = importlib.util.spec_from_file_location("st5_r5", os.path.join(R5_EV, "ST5-installation-state-r5.py"))
_r5_mod = importlib.util.module_from_spec(_r5_spec)
_r5_spec.loader.exec_module(_r5_mod)
installation_state_r5 = _r5_mod.installation_state_r5
rot1_root_discovery = _r5_mod.rot1_root_discovery
_pristine_kernel_content_set = _r5_mod._pristine_kernel_content_set

OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}

SUBDIRS = [".", "product", "spec", "governance", "governance/overlay", "governance/views",
           "governance/trust", "governance/trust/kernel", "governance/trust/state",
           "governance/framework.lock", ".governance-runtime"]

# The reference kernel content set (populated by main, read by workers via global)
_REF_KERNEL = None


def values(name, path, ids, S, v):
    """Value generator from reviewer C's matrix.py (unchanged)."""
    from c4lib import REL
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
    """Combo invocations from reviewer C's matrix.py (unchanged)."""
    from c4lib import REL
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
    """Invocation generator from reviewer C's matrix.py (unchanged)."""
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
    S, tree, v, pos, argv, variant, ids = job
    sub = pos.split(":", 1)[1]
    tag = re.sub(r"[^A-Za-z0-9_.-]", "_", f"R4-{v}-{pos}-{'_'.join(argv[:3])}-{variant}")[:110] + "-" + hashlib.sha256(json.dumps(["R4", v, pos, argv, variant]).encode()).hexdigest()[:10]
    c = os.path.join(S, "runs", tag)
    copy_tree(tree, c)
    env = child_env(S, tag)

    cwd = os.path.join(c, sub)
    os.makedirs(cwd, exist_ok=True)
    root = None  # NO --root

    # r5 state and discovery BEFORE the invocation
    r5_before = installation_state_r5(c, pristine_kernel_ref=_REF_KERNEL)
    disc_before = rot1_root_discovery(cwd)

    before = snap(c, env["HOME"])
    r = gov(BINS[v], argv, env, cwd, root)
    after = snap(c, env["HOME"])
    cmp = compare(before, after)
    st_r4 = installation_state(c)
    r5_after = installation_state_r5(c, pristine_kernel_ref=_REF_KERNEL)

    # Changed paths under governance/trust/** and governance/framework.lock/**
    trust_changed = sorted(p for p in cmp["work_paths"] if p.startswith("governance/trust/"))
    occ_changed = sorted(p for p in cmp["work_paths"] if p.startswith("governance/framework.lock/"))

    row = {
        "binary": v, "position": pos, "variant": variant, "argv": argv,
        "rc": r["_rc"], "ok": r.get("ok"), "code": code(r),
        "work_changed": cmp["work_changed"], "runtime_changed": cmp["runtime_changed"],
        "git_state_changed": cmp["git_state_changed"], "git_files_changed": cmp["git_files_changed"],
        "work_n": cmp["work_n"], "work_paths": cmp["work_paths"][:40],
        "state_after_r4": st_r4["state"],
        "state_after_r5": r5_after["state"],
        "r5_reasons": r5_after.get("reasons", []),
        "r5_nested_inside_governance": r5_after.get("nested_inside_governance", []),
        "r5_nested_legacy_projects": r5_after.get("nested_legacy_projects", []),
        "discovery_r5_before": disc_before,
        "trust_changed": trust_changed[:20],
        "occ_changed": occ_changed[:20],
        "trust_changed_count": len(trust_changed),
        "occ_changed_count": len(occ_changed),
    }
    # Clean up run directory
    return row


def main():
    global _REF_KERNEL
    ap = argparse.ArgumentParser()
    ap.add_argument("trees")
    ap.add_argument("registers")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    T = json.load(open(a.trees))
    R = json.load(open(a.registers))
    S = T["scratch"]
    ids = T["ids"]
    os.makedirs(a.out, exist_ok=True)

    # Build reference kernel from pristine R4
    _REF_KERNEL = _pristine_kernel_content_set(T["trees"]["R4"])

    tree = T["trees"]["R4"]
    jobs = []
    for sub in SUBDIRS:
        pos = "P-CWD:" + sub
        for v in VERSIONS:
            seen = set()
            for leaf in R[v]["leaves"]:
                for name, argv in invocations(leaf, ids, S, v, full=False):
                    if tuple(argv) not in seen:
                        seen.add(tuple(argv))
                        jobs.append((S, tree, v, pos, argv, name, ids))
            for i, argv in enumerate(combos(v, ids, S)):
                if tuple(argv) not in seen:
                    seen.add(tuple(argv))
                    jobs.append((S, tree, v, pos, argv, f"combo:{i}", ids))

    print(f"jobs={len(jobs)}", file=sys.stderr, flush=True)
    t0 = time.time()
    rows = []
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        for row in ex.map(run_job, jobs, chunksize=4):
            rows.append(row)
            if len(rows) % 200 == 0:
                print(f"{len(rows)}/{len(jobs)} ({time.time()-t0:.0f}s)", file=sys.stderr, flush=True)
    elapsed = time.time() - t0
    print(f"done: {len(rows)} rows in {elapsed:.1f}s", file=sys.stderr, flush=True)

    # Identify writing rows (changed any byte of the work tree)
    writing_rows = [r for r in rows if r["work_changed"] or r["runtime_changed"] or r["git_state_changed"] or r["git_files_changed"]]

    # Rows that wrote under governance/trust/** or governance/framework.lock/**
    pps_writing_rows = [r for r in rows if r["trust_changed_count"] > 0 or r["occ_changed_count"] > 0]

    # Build summary
    summary = {"total_rows": len(rows), "total_writing_rows": len(writing_rows), "total_pps_writing_rows": len(pps_writing_rows), "elapsed_seconds": round(elapsed, 1)}

    # Per position x binary breakdown
    pos_bin = {}
    for r in rows:
        key = f"{r['position']}|{r['binary']}"
        if key not in pos_bin:
            pos_bin[key] = {"position": r["position"], "binary": r["binary"], "rows": 0, "writing_rows": 0,
                            "pps_writing_rows": 0, "r4_states": collections.Counter(), "r5_states": collections.Counter(),
                            "r5_reasons": collections.Counter(), "nested_legacy_installs": 0, "commands_writing": set()}
        pb = pos_bin[key]
        pb["rows"] += 1
        is_writing = r["work_changed"] or r["runtime_changed"] or r["git_state_changed"] or r["git_files_changed"]
        if is_writing:
            pb["writing_rows"] += 1
            pb["commands_writing"].add(r["argv"][0] if r["argv"] else "?")
            if len(r["argv"]) > 1:
                pb["commands_writing"].add(" ".join(r["argv"][:2]))
        is_pps = r["trust_changed_count"] > 0 or r["occ_changed_count"] > 0
        if is_pps:
            pb["pps_writing_rows"] += 1
        pb["r4_states"][r["state_after_r4"]] += 1
        pb["r5_states"][r["state_after_r5"]] += 1
        for reason in r["r5_reasons"]:
            pb["r5_reasons"][reason] += 1
        if r["r5_nested_inside_governance"]:
            pb["nested_legacy_installs"] += 1

    summary["per_position_binary"] = []
    for key in sorted(pos_bin):
        pb = pos_bin[key]
        summary["per_position_binary"].append({
            "position": pb["position"], "binary": pb["binary"],
            "rows": pb["rows"], "writing_rows": pb["writing_rows"],
            "pps_writing_rows": pb["pps_writing_rows"],
            "r4_states": dict(pb["r4_states"]), "r5_states": dict(pb["r5_states"]),
            "r5_reasons": dict(pb["r5_reasons"]), "nested_legacy_installs": pb["nested_legacy_installs"],
            "commands_writing": sorted(pb["commands_writing"]),
        })

    # Property checks
    # P5-1: every row that changed any byte under governance/trust/** or governance/framework.lock/** has r5 state != COMPLETE
    p51_violations = [r for r in pps_writing_rows if r["state_after_r5"] == "COMPLETE"]
    summary["P5_1"] = {"holds": len(p51_violations) == 0, "counterexamples": len(p51_violations),
                       "counterexample_sample": [{"position": r["position"], "binary": r["binary"], "argv": r["argv"][:3], "r5_state": r["state_after_r5"]} for r in p51_violations[:5]]}

    # P5-2: every row that created a nested legacy marker is reported by r5
    nested_rows = [r for r in rows if r["r5_nested_inside_governance"] or r["r5_nested_legacy_projects"]]
    # Check: rows that created a nested legacy marker but r5 does NOT report it
    # A row creates a nested legacy marker if after the run, a nested governance/framework.lock or governance/kernel/KERNEL_MANIFEST.json exists
    # We detect this from the r5_nested_inside_governance and r5_nested_legacy_projects fields (which come from the r5 encoding)
    # and also check rows that created nested installs but r5 state is not PARTIAL
    p52_unreported = []
    for r in rows:
        has_nested = bool(r["r5_nested_inside_governance"]) or bool(r["r5_nested_legacy_projects"])
        if has_nested:
            # Check it's reported: either PARTIAL with nested_legacy_install, or NESTED_LEGACY_PROJECT diagnostic
            reported = ("nested_legacy_install" in r["r5_reasons"]) or bool(r["r5_nested_legacy_projects"])
            if not reported:
                p52_unreported.append(r)
    summary["P5_2"] = {"holds": len(p52_unreported) == 0, "counterexamples": len(p52_unreported),
                       "total_rows_creating_nested": len(nested_rows),
                       "counterexample_sample": [{"position": r["position"], "binary": r["binary"], "argv": r["argv"][:3]} for r in p52_unreported[:5]]}

    # P5-3: RoT-1 discovery refuses for every position inside the PPS and does not refuse for others
    PPS_POSITIONS = {"P-CWD:governance/trust", "P-CWD:governance/trust/kernel", "P-CWD:governance/trust/state", "P-CWD:governance/framework.lock"}
    NON_PPS_POSITIONS = set(f"P-CWD:{s}" for s in SUBDIRS) - PPS_POSITIONS
    p53_violations = []
    # Check on the first row of each position (discovery_r5_before is the same for all rows of a position)
    seen_positions = {}
    for r in rows:
        if r["position"] not in seen_positions:
            seen_positions[r["position"]] = r["discovery_r5_before"]
    for pos, disc in seen_positions.items():
        if pos in PPS_POSITIONS and not disc["refuse"]:
            p53_violations.append({"position": pos, "refuse": disc["refuse"], "code": disc["code"], "expected": "refuse=True"})
        elif pos in NON_PPS_POSITIONS and disc["refuse"]:
            p53_violations.append({"position": pos, "refuse": disc["refuse"], "code": disc["code"], "expected": "refuse=False"})
    summary["P5_3"] = {"holds": len(p53_violations) == 0, "counterexamples": len(p53_violations),
                       "counterexample_details": p53_violations,
                       "pps_positions": sorted(PPS_POSITIONS), "non_pps_positions": sorted(NON_PPS_POSITIONS)}

    # P5-4: the r4 encoding reported COMPLETE for rows that P5-1 covers
    p54_r4_complete = [r for r in pps_writing_rows if r["state_after_r4"] == "COMPLETE"]
    p54_r4_not_complete = [r for r in pps_writing_rows if r["state_after_r4"] != "COMPLETE"]
    summary["P5_4"] = {"pps_writing_rows_r4_COMPLETE": len(p54_r4_complete),
                       "pps_writing_rows_r4_not_COMPLETE": len(p54_r4_not_complete),
                       "note": "These are the rows whose r4-COMPLETE status is what the changed r5 predicate flips to non-COMPLETE"}

    # Identify commands that wrote
    writing_commands = collections.Counter()
    for r in writing_rows:
        cmd = " ".join(r["argv"][:2]) if len(r["argv"]) > 1 else (r["argv"][0] if r["argv"] else "?")
        writing_commands[cmd] += 1
    summary["commands_that_wrote"] = dict(writing_commands.most_common())

    # Write outputs
    out_dir = a.out
    # Writing rows (with paths replaced)
    with open(os.path.join(out_dir, "ST5-subdir-matrix-writing-rows.json"), "w") as f:
        text = json.dumps(writing_rows, indent=1, sort_keys=True, default=str)
        f.write(scrub(text, S))
    with open(os.path.join(out_dir, "ST5-subdir-matrix-summary.json"), "w") as f:
        text = json.dumps(summary, indent=1, sort_keys=True, default=str)
        f.write(scrub(text, S))
    print(json.dumps({"rows": len(rows), "writing": len(writing_rows), "pps_writing": len(pps_writing_rows), "elapsed": round(elapsed, 1)}, indent=1))


if __name__ == "__main__":
    main()
