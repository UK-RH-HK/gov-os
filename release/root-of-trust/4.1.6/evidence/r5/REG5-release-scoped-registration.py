#!/usr/bin/env python3
"""REG5 — release-scoped registration of non-join constitutional content (BC4-3 / RV4-H3; `23` §12) against revision 5.

RoT-1 revision 5, PROPOSED architecture instrument (executed). Not the implementation.

What runs.
  * The pack checker as amended in revision 5 (`constitutional-surface/csi_check.py`, `csi_lib.py`): E7 with
    `--registrations/--release-id` (exact per-release registration), the single-valued lint, the append-only set lint and
    `registration-reductions`.
  * Review r4 reviewer B's part P shape (RV4-B-A08): a Trust Policy that keeps the superseded `aws-access-key` regex beside
    the fix; a higher-sequence final carrying 4.1.7's content except the superseded regex.
  * Review r4 synthesis D-A02 T1–T4 shapes: tool descriptor member, hard-invariant member, schema file, skill file.
  * Specialist-found variants (A: gap sequence, sequence inflation, stale Trust Policy; B: rewrite, reversion).
  * Consumption on the real legacy 4.1.5 binary of the content revision 5 makes effective (the fixed release) and, as the
    revision-4 control, of the mixed content revision 4 made effective: is the `ASIA…` key file indexed and retrievable?

Attribution. Target fixes (`fix_tool`, `fix_invariant`, `fix_schema`, `fix_skill`) and `kcopy` follow
`4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A02-pinned-retention-breadth.py`; `set_patterns`, the consumer set-up
(`consume`, `rel_copy`, `db_paths`) and the secret marker follow `4.1.6-review-r4/B-trust-security/evidence/RV4-B-surface-probes.py`
part P. Code re-typed and trimmed; the rules applied are revision 5.

Environment: REVIEW_REPO (worktree), GOV (legacy 4.1.5), GOV_REVIEW_SCRATCH (scratch). GOV_* stripped from children;
HOME and GOV_KERNEL_CACHE in scratch. Output: JSON on stdout, scratch paths replaced by <scratch>.
"""
import copy, glob, json, os, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ["GOV"]
FW = os.path.join(REPO, "framework")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="reg5-", dir=os.environ["GOV_REVIEW_SCRATCH"])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = os.path.join(S, "cache")
ENV["HOME"] = os.path.join(S, "home")
os.makedirs(ENV["HOME"], exist_ok=True)

KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"
OLD_RE = "AKIA[0-9A-Z]{16}"
NEW_RE = "(AKIA|ASIA)[0-9A-Z]{16}"
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
NEW_MEMBER_KEY = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"


def kcopy(name, src=FW):
    d = os.path.join(S, "k", name)
    shutil.copytree(src, d)
    if not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    return d


def ymut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    C.ydump(p, d)


SCHEMA = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "schemas/*.schema.json")))[0]
SKILL = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "skills/SKL-*.yaml")))[0]


def set_patterns(kdir, aws_re, with_member):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == NEW_MEMBER["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(NEW_MEMBER))
    ymut(kdir, "policies/SECURITY_POLICY.yaml", f)


def fix_pattern(k):
    set_patterns(k, NEW_RE, True)


def fix_tool(k):
    ymut(k, "tools/registry/TOOLS.yaml", lambda d: [t.__setitem__("probe_fixed_note", "4.1.7 fix: health command hardened") for t in d["tools"] if t["tool_id"] == "TOOL-GIT-001"])


def fix_invariant(k):
    ymut(k, "constitution/HARD_INVARIANTS.yaml", lambda d: [i.__setitem__("statement", str(i.get("statement", "")) + " (4.1.7 clarification)") for i in d["invariants"] if i["id"] == "INV-001"])


def fix_schema(k):
    p = os.path.join(k, SCHEMA)
    j = json.load(open(p))
    j["$comment"] = "4.1.7 fix: additionalProperties tightened"
    json.dump(j, open(p, "w"), indent=2)


def fix_skill(k):
    ymut(k, SKILL, lambda d: d.__setitem__("probe_fixed_note", "4.1.7 fix: instruction corrected") if isinstance(d, dict) else None)


FIXES = {"P_aws_regex_secret_pattern": fix_pattern, "T1_tool_descriptor_member": fix_tool, "T2_hard_invariant_member": fix_invariant,
         "T3_schema_pinned_file": fix_schema, "T4_skill_pinned_file": fix_skill}


def mixed_pattern(k):
    """4.1.7's secret-pattern change set except the superseded regex (the new member stays)."""
    set_patterns(k, OLD_RE, True)


# Trust Policy v2 surface: classifies the member 4.1.7 introduces (a root-signed classification change, not a registration)
INV2 = copy.deepcopy(INV)
fr_sec = next(f for f in INV2["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
if not any(l["key"] == NEW_MEMBER_KEY for l in fr_sec["leaves"]):
    # The surface keeps the unchanged revision-4 lint (a pinned rule carries a digests map). Under --registrations the
    # projection replaces every pinned digest with the single value registered for the release under test (23 §12.3).
    fr_sec["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "note": "member introduced in 4.1.7 (TPS v2 classification)", "digests": {NEW_MEMBER_KEY: [L.vdigest(NEW_MEMBER["regex"])]}})


def check(kdir, regs, release_id, inv=INV2):
    r = C.run_check(kdir, inv, quiet=True, registrations=regs, release_id=release_id)
    return {"exit": r["exit"], "violations": [str(v)[:220] for v in (r.get("violations") or [])[:4]], "malformed": [str(m)[:220] for m in (r.get("malformed") or [])[:3]]}


out = {"probe": "REG5 release-scoped registration (revision 5)", "checker": "csi_check.run_check with registrations (revision 5)",
       "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()}

# ---------------------------------------------------------------------------------------------- releases and registrations
K416 = kcopy("4.1.6")
K417 = kcopy("4.1.7")
for fx in FIXES.values():
    fx(K417)
REG416 = L.registration_record(INV2, K416, "4.1.6", 1600, "sha256:final-4.1.6")
REG417 = L.registration_record(INV2, K417, "4.1.7", 1700, "sha256:final-4.1.7")
SET_V1, SET_V2 = [REG416], [REG416, REG417]
out["registrations"] = {"4.1.6": {"units": len(REG416["units"]), "kernel_tree_digest": REG416["kernel_tree_digest"]},
                        "4.1.7": {"units": len(REG417["units"]), "kernel_tree_digest": REG417["kernel_tree_digest"]},
                        "units_differing_4.1.6_to_4.1.7": sorted(u for u in set(REG416["units"]) | set(REG417["units"]) if REG416["units"].get(u) != REG417["units"].get(u))}

# ---------------------------------------------------------------------------------------------- part P and D-A02 T1–T4
mix = {}
for name in FIXES:
    k = kcopy("mix-" + name)
    for other, fx in FIXES.items():
        if other != name:
            fx(k)
    if name == "P_aws_regex_secret_pattern":
        mixed_pattern(k)
    mix[name] = k
rows = {}
for name, k in mix.items():
    rows[name] = {
        "mixed_release_as_unregistered_4.1.8 (RV4-B-A08 / D-A02 trigger)": check(k, SET_V2, "4.1.8"),
        "mixed_release_claiming_4.1.7": check(k, SET_V2, "4.1.7"),
        "mixed_release_claiming_4.1.6": check(k, SET_V2, "4.1.6"),
    }
legit = {"installed_4.1.6_at_its_own_registration_under_set_v2": check(K416, SET_V2, "4.1.6"),
         "fixed_4.1.7_at_its_own_registration": check(K417, SET_V2, "4.1.7")}

# revision-4 retention form (two digests for one unit) under the revision-5 lint
INV_RETAIN = copy.deepcopy(INV)
for f in INV_RETAIN["files"]:
    for lr in f.get("leaves") or []:
        if KEY in (lr.get("digests") or {}):
            lr["digests"][KEY] = sorted(set(lr["digests"][KEY]) | {L.vdigest(NEW_RE)})
retain = {"revision_4_RETAIN_inventory_on_the_mixed_kernel": C.run_check(mix["P_aws_regex_secret_pattern"], INV_RETAIN, quiet=True)["exit"],
          "revision_4_RETAIN_inventory_on_the_fixed_kernel": C.run_check(K417, INV_RETAIN, quiet=True)["exit"]}

# ---------------------------------------------------------------------------------------------- ranges that exact registration excludes (specialist A, E4)
gap = {"4.1.6_content_as_unregistered_gap_release_seq_1650": check(K416, SET_V2, "4.1.6-gap"),
       "4.1.7_content_as_inflated_release_seq_1e9": check(K417, SET_V2, "4.1.7-inflated"),
       "stale_machine_holding_only_4.1.6_registration: forged 4.1.8 with 4.1.6 content": check(K416, SET_V1, "4.1.8"),
       "stale_machine_holding_only_4.1.6_registration: genuine 4.1.7 (availability until the registration is held)": check(K417, SET_V1, "4.1.7"),
       "same_machine_after_receiving_the_4.1.7_registration": check(K417, SET_V2, "4.1.7")}

# ---------------------------------------------------------------------------------------------- append-only, rewrite, reversion
REWRITE = copy.deepcopy(REG416)
REWRITE["units"]["leaf:" + KEY] = L.vdigest(NEW_RE)
REG418 = L.registration_record(INV2, mix["P_aws_regex_secret_pattern"], "4.1.8", 1800, "sha256:final-4.1.8")
hist = {"subject": "registration:4.1.8:leaf:" + KEY, "in_policy_version": 3, "reason": "owner restores the 4.1.6 regex (probe)"}
REG418_DECL = dict(copy.deepcopy(REG418), lowering_history=[hist])
history = {
    "rewrite_of_registered_4.1.6_in_the_set: check": check(K416, [REG416, REG417, REWRITE], "4.1.6"),
    "rewrite_of_registered_4.1.6_in_the_set: registration-reductions": C.run_registration_reductions([REG416, REG417, REWRITE], quiet=True)["exit"],
    "owner_registers_superseded_regex_for_4.1.8_without_lowering_history": {k: v for k, v in C.run_registration_reductions([REG416, REG417, REG418], quiet=True).items() if k in ("exit", "undeclared")},
    "same_with_lowering_history": C.run_registration_reductions([REG416, REG417, REG418_DECL], quiet=True)["exit"],
    "mixed_kernel_once_registered_as_4.1.8 (root-threshold registration; per-project policy_lowering gate for projects holding 4.1.7)": check(mix["P_aws_regex_secret_pattern"], [REG416, REG417, REG418_DECL], "4.1.8"),
    "revision_4_reductions_tool_on_the_retention_inventory (control)": C.run_reductions(INV, INV_RETAIN, [], quiet=True)["exit"],
}

# ---------------------------------------------------------------------------------------------- migrations registered per release (RV4-M5 selector)
M_OK = "id: M-017\nfrom_version: 4.1.6\nto_version: 4.1.7\noperations:\n  - {op: note, text: tighten template}\n"
M_WEAK = "id: M-017\nfrom_version: 4.1.6\nto_version: 4.1.7\noperations:\n  - {op: note, text: weakened template}\n"
Km = kcopy("4.1.7-mig")
for fx in FIXES.values():
    fx(Km)
os.makedirs(os.path.join(Km, "migrations"), exist_ok=True)
open(os.path.join(Km, "migrations/M-017.yaml"), "w").write(M_OK)
REG417M = L.registration_record(INV2, Km, "4.1.7", 1700)
Kw = kcopy("4.1.7-mig-weak")
for fx in FIXES.values():
    fx(Kw)
os.makedirs(os.path.join(Kw, "migrations"), exist_ok=True)
open(os.path.join(Kw, "migrations/M-017.yaml"), "w").write(M_WEAK)
migr = {"registered_migration": check(Km, [REG416, REG417M], "4.1.7"), "different_migration_under_the_same_release": check(Kw, [REG416, REG417M], "4.1.7")}


# ---------------------------------------------------------------------------------------------- consumption on real 4.1.5 (reviewer B part P set-up)
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-reg5", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": ENV["HOME"], "GIT_CONFIG_NOSYSTEM": "1"})


def rel_copy(name, kernel_mutator):
    d = os.path.join(S, "src", name)
    shutil.copytree(REL, d)
    kernel_mutator(os.path.join(d, "kernel"))
    return d


def db_paths(root, suffix):
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        return [x[0] for x in con.execute("select path from artifacts") if x[0].endswith(suffix)]
    except sqlite3.Error as e:
        return f"db error {e}"


SECRET = "ASIAQ3EGUH7X4MPLE2Z9"
MARK = "REG5SECRETMARK"


def consume(label, src):
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "reg5", "--skip-index")
    os.makedirs(os.path.join(root, "product", "notes"), exist_ok=True)
    open(os.path.join(root, "product", "notes", "deploy.md"), "w").write(f"# Deploy notes {MARK}\n\naws key used by the job: {SECRET}\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    rb = gov(root, "orchestrator", "rebuild-memory")
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("notes/deploy.md")]
    return {"init_ok": init.get("ok"), "rebuild_ok": rb.get("ok"), "indexed": db_paths(root, "notes/deploy.md"), "retrievable_by_query": hits}


fixed_src = rel_copy("fixed", lambda k: set_patterns(k, NEW_RE, True))
mixed_src = rel_copy("mixed", lambda k: set_patterns(k, OLD_RE, True))
consumption = {"revision_5_effective_content (the forged mixed release is ineligible; the registered fixed release stays the policy root)": consume("r5-effective-fixed", fixed_src),
               "revision_4_effective_content (control: the mixed release was eligible under the retaining TPS)": consume("r4-effective-mixed", mixed_src)}

out.update({"legitimate_releases": legit, "part_P_and_D_A02": rows, "revision_4_retention_form": retain, "ranges_excluded": gap,
            "append_only_and_reversion": history, "migrations": migr, "consumption_4_1_5": consumption})
fx_r5 = consumption["revision_5_effective_content (the forged mixed release is ineligible; the registered fixed release stays the policy root)"]
fx_r4 = consumption["revision_4_effective_content (control: the mixed release was eligible under the retaining TPS)"]
out["verdicts"] = {
    "legitimate_4.1.6_and_4.1.7_eligible": all(v["exit"] == 0 for v in legit.values()),
    "every_mixed_release_refused_by_E7_for_every_claimed_identity (5 targets x 3 identities)": all(v["exit"] == 3 for r in rows.values() for v in r.values()),
    "revision_4_retention_form_malformed": all(v == 5 for v in retain.values()),
    "gap_inflation_stale_refused_and_genuine_accepted_once_registered": gap["4.1.6_content_as_unregistered_gap_release_seq_1650"]["exit"] == 3 and gap["4.1.7_content_as_inflated_release_seq_1e9"]["exit"] == 3
        and gap["stale_machine_holding_only_4.1.6_registration: forged 4.1.8 with 4.1.6 content"]["exit"] == 3 and gap["same_machine_after_receiving_the_4.1.7_registration"]["exit"] == 0,
    "rewrite_malformed": history["rewrite_of_registered_4.1.6_in_the_set: check"]["exit"] == 5 and history["rewrite_of_registered_4.1.6_in_the_set: registration-reductions"] == 5,
    "reversion_is_a_computed_reduction": history["owner_registers_superseded_regex_for_4.1.8_without_lowering_history"]["exit"] == 6 and history["same_with_lowering_history"] == 0,
    "revision_4_reductions_tool_silent_on_retention (control)": history["revision_4_reductions_tool_on_the_retention_inventory (control)"] == 0,
    "migration_registered_per_release": migr["registered_migration"]["exit"] == 0 and migr["different_migration_under_the_same_release"]["exit"] == 3,
    "r5_effective_content_keeps_ASIA_key_file_out_of_index": not fx_r5["indexed"] and not fx_r5["retrievable_by_query"],
    "r4_control_indexes_and_serves_ASIA_key_file": bool(fx_r4["indexed"]) and bool(fx_r4["retrievable_by_query"]),
}
print(json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(REPO, "<worktree>"))
