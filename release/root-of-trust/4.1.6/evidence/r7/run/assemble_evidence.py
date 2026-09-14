#!/usr/bin/env python3
"""AR-0019: assemble the revision-7 evidence into the work-product tree from the final scratch runs.

- verifies that the export's instruments, register, schemas, profile and pack text equal the work-product tree (so every
  output corresponds to the committed code and text);
- copies the final revision-7 outputs (paths scrubbed), the unmodified review-probe outputs, the DA07r6 re-run on the
  revision-7 plan and reviewer C's matrix summaries;
- records comparisons (determinism passes, retained instruments versus committed, review probes versus committed, reviewer
  C's outputs versus committed) and writes evidence/r7/EVIDENCE-RUN-LOG-r7.json.
Usage: assemble_evidence.py <subset-determinism-log> [<later subset log> ...] (later logs supersede earlier ones)
"""
import datetime, glob, gzip, hashlib, json, os, re, shutil, subprocess, sys

sys.dont_write_bytecode = True
SP = "<scratchpad>"
S = SP + "/ar-0019"
F = S + "/final"
X = F + "/export"
XP = X + "/release/root-of-trust/4.1.6"
WT = SP + "/wt/arch-r7"
RT = WT + "/release/root-of-trust"
P = RT + "/4.1.6"
E7 = P + "/evidence/r7"
SUBSET_LOGS = sys.argv[1:]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def scrub(t):
    for a, b in ((X, "<export>"), (WT, "<worktree>"), (S, "<scratch>"), (SP, "<scratchpad>"), ("<home>", "<home>")):
        t = t.replace(a, b)
    return t


def leaves(x, pre=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, pre + "/" + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, pre + "/" + str(i))
    else:
        yield pre, x


def compare_json(committed, rerun, norm=None):
    a, b = open(committed, "rb").read(), open(rerun, "rb").read()
    if a == b:
        return {"byte_identical": True}
    try:
        ja, jb = json.loads(a), json.loads(b)
    except Exception as e:  # noqa: BLE001
        return {"byte_identical": False, "json": False, "error": str(e)[:200]}
    la, lb = dict(leaves(ja)), dict(leaves(jb))
    n = norm or (lambda v: v)
    diff = sorted(k for k in set(la) | set(lb) if n(la.get(k, "<absent>")) != n(lb.get(k, "<absent>")))
    va, vb = ja.get("verdicts", {}) if isinstance(ja, dict) else {}, jb.get("verdicts", {}) if isinstance(jb, dict) else {}
    flips = {k: [va.get(k, "<absent>"), vb.get(k, "<absent>")] for k in set(va) | set(vb) if isinstance(va, dict) and isinstance(vb, dict) and va.get(k, "<absent>") != vb.get(k, "<absent>")}
    return {"byte_identical": False, "differing_leaves": len(diff), "leaf_paths": [scrub(k) for k in diff[:12]], "verdict_flips": flips}


def read_log(path):
    rows = []
    for line in open(path):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4 and parts[0] != "DONE":
            rows.append(parts)
    return rows


log = {"run_id": "AR-0019", "role": "rot-architect", "profile": "governance-os.rot1/CP-1",
       "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "worktree_base_commit": subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "path_placeholders": {"<export>": "copy of the work-product tree used by every final run", "<worktree>": "the work-product worktree",
                             "<scratch>": "this run's scratch root", "<scratchpad>": "the session scratchpad", "<home>": "the account home (read-only toolchain)",
                             "<ar17>": "reviewer C's scratch placeholder, written by reviewer C's harness"},
       "hygiene": "env -i; GOV_* stripped; HOME, XDG_* and GOV_KERNEL_CACHE in scratch; PYTHONDONTWRITEBYTECODE=1; legacy binaries read-only; no helper sessions"}
env = {}
for name, cmd in (("python3", ["python3", "--version"]), ("openssl", ["openssl", "version"]), ("git", ["git", "--version"])):
    r = subprocess.run(cmd, capture_output=True, text=True)
    env[name] = (r.stdout or r.stderr).strip()
log["environment"] = env

# ---------------------------------------------------------------- 1. the export equals the work-product tree
checked, mismatched = 0, []
for rel in sorted(set(glob.glob(P + "/*.md") + glob.glob(P + "/evidence/r7/*.py") + glob.glob(P + "/evidence/r7/LAY7/*.py") + glob.glob(P + "/decision-register/*")
                  + glob.glob(P + "/schemas/*.json") + glob.glob(P + "/schemas/withdrawn-non-production/*") + glob.glob(P + "/profile/*") + glob.glob(P + "/examples/rev7/*.py"))):
    if os.path.isdir(rel):
        continue
    x = XP + rel[len(P):]
    checked += 1
    if not os.path.exists(x) or sha(x) != sha(rel):
        mismatched.append(rel[len(P) + 1:])
log["export_equals_worktree"] = {"files_checked": checked, "mismatched": mismatched}
if mismatched:
    print("MISMATCH", mismatched)
    sys.exit(2)

# ---------------------------------------------------------------- 2. revision-7 outputs
OUT7 = ["CS7-derivation-calculator.json", "CS7-results.json.gz", "FA7-first-contact-authority.json", "CUR7-first-contact-currency.json", "ADM7-admission-stores.json",
        "ENV7-environment-authority.json", "BA11r7-machine-classes.json", "BA12r7-key-subsets-below-threshold.json", "PPR7-project-records.json",
        "DA05r7-combinations-under-CP1.json", "DA06r7-rendering-and-classifier-vocabulary.json", "LAY7/crashmig7.json", "STATEMENTS-CHECK.json",
        "PROF7-profile-conformance.json", "REGISTER-CHECK.json", "DA09r7-schema-fields-versus-register.json", "DA04r7-plan-regression-detection.json",
        "r6-probes/RV6-D-A03.json"]
outputs = {}
for rel in OUT7:
    src, dst = XP + "/evidence/r7/" + rel, E7 + "/" + rel
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if rel.endswith(".gz"):
        shutil.copyfile(src, dst)
        scrubbed = False
    else:
        t = open(src, encoding="utf-8").read()
        s2 = scrub(t)
        scrubbed = s2 != t
        open(dst, "w", encoding="utf-8").write(s2)
    outputs[rel] = {"sha256_run_output": sha(src), "sha256_committed": sha(dst), "paths_scrubbed": scrubbed}
for p in sorted(glob.glob(XP + "/examples/rev7/*.json")):
    dst = P + "/examples/rev7/" + os.path.basename(p)
    shutil.copyfile(p, dst)
    outputs["examples/rev7/" + os.path.basename(p)] = {"sha256_committed": sha(dst)}
log["revision_7_outputs"] = outputs

# ---------------------------------------------------------------- 3. run logs
def rows_to_steps(rows, fields=("id", "exit", "seconds", "sha256", "output")):
    out = []
    for r in rows:
        d = dict(zip(fields, r))
        if "output" in d:
            d["output"] = scrub(d["output"])
        out.append(d)
    return out


log["runs"] = {
    "first_final_run": {"script": "run/run_r7_evidence.sh", "steps": rows_to_steps(read_log(F + "/log.tsv")),
                        "superseded": {"crashmig7": "exit 1: fixed scratch directory existed (instrument now uses a fresh directory per run)",
                                       "REGISTER-CHECK": "exit 1: read the empty crashmig7 output", "DA09r7": "control invalid for the same reason; detection rule tightened",
                                       "EXAMPLES-rev7": "exit 1: generator run from a copied directory; now run in place",
                                       "FA7-run1/FA7-run2": "one leaf differed (whitelist-pair report in set order); the executor now iterates sorted"}},
    "rerun_of_invalidated_steps": {"script": "run/rerun_dependent.sh", "steps": rows_to_steps(read_log(F + "/log-rerun.tsv"))},
    "determinism_full_two_passes": {"script": "run/determinism.sh", "steps": rows_to_steps(read_log(F + "/det/determinism-full-pass.tsv"), ("pass", "id", "exit", "seconds", "sha256", "output"))},
    "determinism_text_subsets_two_passes": [{"script": "run/determinism.sh <ids>", "steps": rows_to_steps(read_log(l), ("pass", "id", "exit", "seconds", "sha256", "output"))} for l in SUBSET_LOGS],
    "review_probes_final": {"script": "run/rerun_probes.sh", "steps": rows_to_steps(read_log(F + "/log-probes-final.tsv"))},
    "reviewer_C_chain": {"script": "run/run_C_chain_final.sh", "steps": rows_to_steps(read_log(F + "/C/log.tsv"), ("id", "exit", "seconds", "sha256"))},
    "reviewer_C_on_rebuilt_trees": {"script": "run/run_C2_rebuilt.sh", "steps": rows_to_steps(read_log(F + "/C2/log.tsv"), ("id", "exit", "seconds", "sha256"))},
}


def pairs(rows):
    a = {r[1]: r[4] for r in rows if r[0] == "a"}
    b = {r[1]: r[4] for r in rows if r[0] == "b"}
    return {k: a[k] == b.get(k) for k in a}


full_pairs = pairs(read_log(F + "/det/determinism-full-pass.tsv"))
subset_pairs = {}
for l in SUBSET_LOGS:
    subset_pairs.update({k + " (" + os.path.basename(l) + ")": v for k, v in pairs(read_log(l)).items()})
log["determinism"] = {"full_two_passes_identical": full_pairs, "text_subsets_two_passes_identical": subset_pairs,
                      "all_identical": all(full_pairs.values()) and all(subset_pairs.values()),
                      "note": "pass a: hash seed random; pass b: PYTHONHASHSEED=12345; the final text subset re-ran the text-dependent instruments after the last pack-text edits"}
committed_sha = {k: v["sha256_run_output"] for k, v in outputs.items() if "sha256_run_output" in v}
subset_a = {}
for l in SUBSET_LOGS:
    subset_a.update({r[1]: r[4] for r in read_log(l) if r[0] == "a"})
full_a = {r[1]: r[4] for r in read_log(F + "/det/determinism-full-pass.tsv") if r[0] == "a"}
log["determinism"]["committed_outputs_are_pass_a"] = {
    "subset": {k: v for k, v in subset_a.items()}, "full": {k: v for k, v in full_a.items() if k not in subset_a}}

# ---------------------------------------------------------------- 4. retained instruments versus committed
retained = {}
for p in sorted(glob.glob(F + "/out/retained/*.json")):
    n = os.path.basename(p)
    cands = [c for c in (P + "/evidence/r6/" + n, P + "/evidence/r5/" + n, P + "/evidence/" + n) if os.path.exists(c)]
    if n == "FA5-first-admission.stdout.json":
        cands = [P + "/evidence/r5/FA5-first-admission.json"]
    if not cands:
        continue
    retained[n] = dict(compare_json(cands[0], p, norm=lambda v: re.sub(r"^(<export>|/tmp/\S*?/export)", "<export>", str(v))), committed=cands[0][len(P) + 1:])
os.makedirs(E7 + "/retained", exist_ok=True)
open(E7 + "/retained/DA07r6-plan-regression-detection.on-revision-7-plan.json", "w").write(scrub(open(F + "/out/retained/DA07r6-plan-regression-detection.json").read()))
log["retained_instruments_versus_committed"] = retained

# ---------------------------------------------------------------- 5. unmodified review probes
probes = {}
for d, rev, dst in (("r6-probes-final", "4.1.6-review-r6", "r6-probes"), ("r5-probes-final", "4.1.6-review-r5", "r5-probes")):
    os.makedirs(E7 + "/" + dst, exist_ok=True)
    not_runnable = {}
    for p in sorted(glob.glob(F + "/out/" + d + "/*.json")):
        n = os.path.basename(p)[:-5]
        cands = [c for c in glob.glob(RT + "/" + rev + "/*/evidence/outputs/" + n + "-*.json") if "first-run" not in c]
        try:
            json.load(open(p))
            ok = True
        except Exception:  # noqa: BLE001
            ok = False
        if not ok:
            err = [l for l in open(p + ".stderr").read().splitlines() if l.strip()]
            not_runnable[n] = {"exit": 1, "last_error": scrub(err[-1]) if err else ""}
            continue
        open(E7 + "/" + dst + "/" + n + ".json", "w").write(scrub(open(p).read()))
        probes[n] = dict(compare_json(cands[0], p), committed=cands[0][len(RT) + 1:]) if cands else {"committed": None}
    json.dump(not_runnable, open(E7 + "/" + dst + "/NOT-RUNNABLE.json", "w"), indent=1, sort_keys=True)
    log.setdefault("review_probes_not_runnable", {}).update(not_runnable)
log["review_probes_versus_committed"] = probes

# ---------------------------------------------------------------- 6. reviewer C
C_OUT = RT + "/4.1.6-review-r6/C-compat-transaction/evidence/outputs/"
cmp_c = {}
for n, src in (("registers6.json", F + "/C/registers6.json"), ("struct6.json", F + "/C/struct6.json"), ("attrprec6.json", F + "/C/attrprec6.json"),
               ("admtx6.json", F + "/C/admtx6.json"), ("crashmig6.json", F + "/C/crashmig6.json")):
    cmp_c[n] = compare_json(C_OUT + n, src)
cmp_c["gitops6.json (earlier trees)"] = compare_json(C_OUT + "gitops6.json", F + "/C/gitops/gitops6.json", norm=lambda v: str(v).replace(S + "/c/", "<ar17>/"))
cmp_c["matrix6-summary.json (earlier trees)"] = compare_json(C_OUT + "matrix6-summary.json", F + "/C/matrix/matrix6-summary.json")
cmp_c["gitops6.json (rebuilt trees)"] = compare_json(C_OUT + "gitops6.json", F + "/C2/gitops/gitops6.json", norm=lambda v: str(v).replace("<ar17>/trees2-rebuild/", "<ar17>/trees2/"))
cmp_c["matrix6-summary.json (rebuilt trees)"] = compare_json(C_OUT + "matrix6-summary.json", F + "/C2/matrix/matrix6-summary.json")
log["reviewer_C_versus_committed"] = cmp_c
os.makedirs(E7 + "/C", exist_ok=True)
for tag, src in (("earlier-trees", F + "/C/matrix/matrix6-summary.json"), ("rebuilt-trees", F + "/C2/matrix/matrix6-summary.json")):
    open(E7 + "/C/matrix6-summary." + tag + ".json", "w").write(scrub(open(src).read()))
props = {}
for tag, src in (("earlier_trees", F + "/C/matrix/matrix6-summary.json"), ("rebuilt_trees", F + "/C2/matrix/matrix6-summary.json")):
    d = json.load(open(src))
    pr = d["properties"]
    props[tag] = {"rows": d["rows"], "active": d["active"], "skipped": d["skipped"],
                  "R2-H4_violations": pr["R2-H4_trust_or_occupation_change_left_COMPLETE"]["violations"],
                  "LP-1r_rows": pr["LP-1r_root_anchored_no_project_write"]["rows"], "LP-1r_violations": pr["LP-1r_root_anchored_no_project_write"]["violations"],
                  "classification_lost_rows": pr["classification_lost"]["rows"], "gitop_write_into_COMPLETE_rows": pr["gitop_write_into_COMPLETE"]["rows"],
                  "pps_write_left_COMPLETE_incl_txarea_rows": pr["pps_write_left_COMPLETE_incl_txarea"]["rows"], "binaries_sha256": d.get("binaries_sha256")}
log["matrix6_properties"] = props
ta = open(S + "/c/trees2/trees.json").read().replace(S + "/c/trees2", "<T>")
tb = open(S + "/cf/trees2-rebuild/trees.json").read().replace(S + "/cf/trees2-rebuild", "<T>")
ja, jb = json.loads(ta), json.loads(tb)
log["reviewer_C_trees"] = {"earlier_trees_equal_rebuilt_after_prefix_mapping": ta == tb,
                           "differing_keys": {k: {"earlier": ja[k], "rebuilt": jb.get(k)} for k in ja if ja[k] != jb.get(k) and k in ("sizes", "entries")},
                           "other_differing_keys": [k for k in ja if ja[k] != jb.get(k) and k not in ("sizes", "entries")],
                           "note": "the trees differ only in build-time artefacts: Git object ids (commit times), a random project_trust_id, and file sizes that carry the scratch path length; the pack inputs build6 reads (examples/rev2, rev3, rev6) are unchanged since the base commit. matrix6 was run on both."}

# ---------------------------------------------------------------- 7. scripts
os.makedirs(E7 + "/run", exist_ok=True)
scripts = {}
for src, name in ((F + "/run_r7_evidence.sh", "run_r7_evidence.sh"), (F + "/rerun_dependent.sh", "rerun_dependent.sh"), (F + "/determinism.sh", "determinism.sh"),
                  (F + "/rerun_probes.sh", "rerun_probes.sh"), (F + "/run_C_chain_final.sh", "run_C_chain_final.sh"), (F + "/run_C2_rebuilt.sh", "run_C2_rebuilt.sh"),
                  (F + "/tools/assemble_evidence.py", "assemble_evidence.py")):
    open(E7 + "/run/" + name, "w").write(scrub(open(src).read()))
    scripts[name] = sha(E7 + "/run/" + name)
log["scripts_sha256_committed"] = scripts
log["instruments_sha256"] = {os.path.relpath(p, P): sha(p) for p in sorted(glob.glob(E7 + "/*.py") + glob.glob(E7 + "/LAY7/*.py") + glob.glob(P + "/decision-register/*.py"))}
log["corrections_during_final_run"] = [
    "gov_admit_reference_r7.py: whitelist-pair report iterated in set order (same refusal code, run-dependent detail); now sorted",
    "LAY7/crashmig7.py: fixed scratch directory; now a fresh directory per run",
    "DA09r7: a crashed register check counted as a detected mutation; now a named failing check is required",
    "statements_check.py S2: a brace set mixing class phrases with unknown members was skipped; now it fails (found by the unmodified RV6-B-A03 re-run)",
    "19 §9 coverage sentence omitted init; the overlay rule reused R-INIT-1 of 09; now R-INIT-9 in 09 and 26 and RT-195 names an existing overlay (found by the unmodified RV6-D-A10 re-run)",
    "12 §4g added: a named test for every carried item (RT-200...RT-202 new)",
]
json.dump(log, open(E7 + "/EVIDENCE-RUN-LOG-r7.json", "w"), indent=1, sort_keys=True, ensure_ascii=False)
print(json.dumps({"export_equals_worktree": log["export_equals_worktree"], "determinism_all_identical": log["determinism"]["all_identical"],
                  "matrix6_properties": props, "not_runnable": sorted(log["review_probes_not_runnable"]),
                  "retained_non_identical": {k: v.get("differing_leaves") for k, v in retained.items() if not v["byte_identical"]}}, indent=1))
