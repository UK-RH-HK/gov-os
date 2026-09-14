#!/usr/bin/env python3
"""P1r4 — constitutional-surface soundness for project-owned strength and for absence (blocking class BC-1, RV3-H1), with
executed consumption on the real 4.1.5 binary.

Attribution. The consumer set-up and the three harm tests are those of review r3 reviewer B
`B-trust-security/evidence/RV3-B-A01-precedence-immutable.py` (project raise of `resume_control` to L5; project
`confidential` never-index class with `product/customers/**` classified confidential; project `max_radius` R0). The
materialisation method (write the kernel a revision would enforce and consume it on 4.1.5 through its directory-source
path, which only supplies a verified policy root carrying that content) is the architect's `P1r3`. The revision-3
precedence order and join are quoted from `constitutional-surface/csi_lib.py` at `ca77a43` for comparison only.

Part A  reference (revision-4 `csi_lib.py`):
        A1 soundness of the two-directional order over every mode pair and strength direction, and the five pairs review r3
           found unsound (RV3-D-A01) under the revision-3 and revision-4 orders;
        A2 checker results for every attack kernel; A3 the RV3-D-A10 R01-R09 removals; A4 computed reductions of a Trust
           Policy tightening (RV3-D-A02) with and without a lowering_history entry.
Part B  executed consumption on the real 4.1.5 binary: for each attack, the effective kernel revision 3 enforces and the
        effective kernel revision 4 enforces, consumed with the same project overlay. Harm assertions (a) authority,
        (b) indexing and retrieval, (c) gate answering; `policy effective` values for every overridden key, including
        shrink_only and a constructed strengthen_only_bool registration. The revision-4 reference effective values are
        compared with what the binary reports.
Part C  project-owned strength over effective policy (`26` §6): the vector recorded on the genuine consumer is evaluated
        against every revision-3 and revision-4 consumer; release-signed migration cases (RV3-B-A18, CR-02) against the
        Overlay Surface whitelist and the vector.
Part D  composition: a Trust Policy raises the never-index floor while the project added `confidential`; revision-3
        replacement semantics lose the project class, the revision-4 directed join keeps it (executed).

Scratch only: consumers under $GOV_REVIEW_SCRATCH; GOV_* removed from children; GOV_KERNEL_CACHE and HOME in scratch.
The repository is never written. Output: JSON on stdout with scratch, repository and binary paths replaced by placeholders.
"""
import concurrent.futures as cf, copy, hashlib, json, os, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.environ.get("P1_REPO") or os.path.abspath(os.path.join(PACK, "..", "..", ".."))
sys.path.insert(0, os.path.join(PACK, "constitutional-surface"))
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
INV = yaml.safe_load(open(os.path.join(PACK, "constitutional-surface", "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
os.makedirs(SCRATCH, exist_ok=True)
S = tempfile.mkdtemp(prefix="p1r4-", dir=SCRATCH)
BASE_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
MARK = "P1R4CUSTOMERMARKER"
WORKERS = int(os.environ.get("P1_WORKERS", "6"))

OVERRIDES = {
    "AUTHORITY_POLICY.authority_levels_required.resume_control": "L5",          # floor
    "SECURITY_POLICY.never_index_classes": ["secret", "restricted", "confidential"],  # additive
    "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "R0",                 # ceiling
    "TOOL_POLICY.approved_licences": ["MIT", "Apache-2.0"],                     # shrink_only
    "LEARNING_POLICY.upstream.allowed_payload": ["synthetic_fixture"],           # shrink_only
}
BOOL_KEY = "HUMAN_GATE_POLICY.continue_independent_work"
BOOL_OVERRIDE = {BOOL_KEY: False}                                               # strengthen_only_bool (constructed registration)
CLASSIFICATIONS = [{"pattern": "product/customers/**", "class": "confidential", "reason": "customer data (project-owned classification)"}]
POLS = ["AUTHORITY_POLICY", "SECURITY_POLICY", "HUMAN_GATE_POLICY", "TOOL_POLICY", "LEARNING_POLICY"]
OBSERVED = list(OVERRIDES) + [BOOL_KEY]


class _D(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def ydump(p, d):
    with open(p, "w") as fh:
        yaml.dump(d, fh, Dumper=_D, sort_keys=False)


def set_dotted(doc, dotted, val):
    cur = doc
    parts = dotted.split(".")
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = val


def same(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return sorted(json.dumps(L.canon(x)) for x in a) == sorted(json.dumps(L.canon(x)) for x in b)
    return json.dumps(L.canon(a), sort_keys=True) == json.dumps(L.canon(b), sort_keys=True)


# ------------------------------------------------------------------------------------------------ stand-in kernel for reference checks
# The 4.1.5 payload's historical migrations carry `set_lock_field`, which revision 4 refuses (R-MIG-3; checker exit 3). The
# reference E7 evaluation therefore uses a stand-in with those lock operations removed (re-issued migrations of 4.1.6).
STANDIN = os.path.join(S, "src-standin")
shutil.copytree(REL, STANDIN)
for fn in sorted(os.listdir(os.path.join(STANDIN, "kernel", "migrations"))):
    if fn.startswith("M-") and fn.endswith(".yaml"):
        p = os.path.join(STANDIN, "kernel", "migrations", fn)
        d = yaml.safe_load(open(p))
        d["operations"] = [o for o in d["operations"] if o.get("op") != "set_lock_field"]
        ydump(p, d)
GEN_PREC_DOC = L.load_doc(os.path.join(STANDIN, "kernel", "policies", "POLICY_PRECEDENCE.yaml"))
BASE_VALUES = L.evaluate(INV, os.path.join(STANDIN, "kernel"))["effective"]
out = {"binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "binary_sha256": hashlib.sha256(open(GOV, "rb").read()).hexdigest(),
       "inventory_floor_schema_version": INV["floor_schema_version"], "stand_in": "release/releases/4.1.5 with set_lock_field removed from its historical migrations (reference checks only)",
       "project_overrides": OVERRIDES, "constructed_bool_override": BOOL_OVERRIDE, "project_classifications": CLASSIFICATIONS}


# ------------------------------------------------------------------------------------------------ revision-3 order (quoted from ca77a43, comparison only)
def r3_rule_ge(a, b):
    if a["mode"] not in L.MODES or b["mode"] not in L.MODES:
        return False
    if a["exception_relaxable"] and not b["exception_relaxable"]:
        return False
    if a["mode"] == "immutable" or b["mode"] == "overridable":
        return True
    if a["mode"] != b["mode"]:
        return False
    if a["mode"] in ("floor", "ceiling"):
        return a["kind"] == b["kind"] and (a["order"] or None) == (b["order"] or None)
    if a["mode"] == "strengthen_only_bool":
        return a["strict_value"] == b["strict_value"]
    return True


def r3_rule_join(a, b):
    if r3_rule_ge(a, b):
        return a
    if r3_rule_ge(b, a):
        return b
    return {"key": "<join>", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}


# ------------------------------------------------------------------------------------------------ rule helpers
def rules_with(inv, changes):
    res = []
    for r in inv["precedence"]["rules"]:
        r = dict(r)
        if r["key"] in changes:
            ch = changes[r["key"]]
            r.update({"mode": ch, "kind": None, "order": None, "strict_value": None} if isinstance(ch, str) else ch)
        res.append(r)
    return res


def inv_with(inv, rules=None, leaf_values=None):
    i = copy.deepcopy(inv)
    if rules is not None:
        i["precedence"]["rules"] = copy.deepcopy(rules)
    for f in i["files"]:
        for l in f.get("leaves", []):
            if leaf_values and l["key"] in leaf_values:
                l["value"] = leaf_values[l["key"]]
    return i


def prec_doc(rules, default_mode):
    d = copy.deepcopy(GEN_PREC_DOC)
    d["default_mode"] = default_mode
    d["rules"] = [{k: v for k, v in r.items() if v is not None and not (k == "exception_relaxable" and v is False)} for r in rules]
    return d


def r3_effective_rules(kernel_rules, kernel_default, reg_rules, reg_default):
    return [dict(r3_rule_join(L.effective_rule(kernel_rules, kernel_default, r["key"].replace("*", "p3probe")),
                              L.effective_rule(reg_rules, reg_default, r["key"].replace("*", "p3probe"))), key=r["key"]) for r in reg_rules]


def r4_effective_rules(eff_inv, held_inv=None):
    return [dict(L.effective_project_rule(eff_inv, r["key"].replace("*", "p3probe"), held_inv), key=r["key"]) for r in eff_inv["precedence"]["rules"]]


def check_kernel(tag, inv, rules=None, delete_prec=False, removed=None):
    k = os.path.join(S, "check-" + tag)
    shutil.copytree(os.path.join(STANDIN, "kernel"), k)
    pp = os.path.join(k, "policies", "POLICY_PRECEDENCE.yaml")
    if delete_prec:
        shutil.move(pp, os.path.join(S, "aside-check-" + tag + "-POLICY_PRECEDENCE.yaml"))
    elif rules is not None:
        ydump(pp, prec_doc(rules, inv["precedence"]["default_mode"]))
    if removed:
        shutil.move(os.path.join(k, removed), os.path.join(S, "aside-check-" + tag + "-" + removed.replace("/", "__")))
    rep = C.run_check(k, inv, quiet=True)
    return {"exit": rep["exit"], "required_missing": rep.get("required_missing", [])[:4], "violations": [v.get("reason") or v.get("class") for v in (rep.get("violations") or [])][:4],
            "precedence_unregistered_count": rep.get("precedence_unregistered_count")}


assert L.precedence_mismatches(prec_doc(INV["precedence"]["rules"], INV["precedence"]["default_mode"]), INV["precedence"]) == []

# ------------------------------------------------------------------------------------------------ part A: reference
modes, dirs = sorted(L.MODES), ["up", "down", "add", "remove", "strict_true", "strict_false", "none"]
unsound, join_drops = [], []
for d in dirs:
    for a in modes:
        for b in modes:
            ra = {"key": "K", "mode": a, "kind": "level" if a in ("floor", "ceiling") else None, "order": None, "strict_value": (d != "strict_false") if a == "strengthen_only_bool" else None, "exception_relaxable": False}
            rb = dict(ra, mode=b, kind="level" if b in ("floor", "ceiling") else None, strict_value=(d != "strict_false") if b == "strengthen_only_bool" else None)
            A, B = L.admitted(ra, d), L.admitted(rb, d)
            if L.rule_ge(ra, rb, d) and (("s" in B and "s" not in A) or ("w" in A and "w" not in B)):
                unsound.append([d, a, b])
            J = L.admitted(L.rule_join(ra, rb, d), d)
            if ("s" in (A | B) and "s" not in J) or ("w" in J and not ("w" in A and "w" in B)):
                join_drops.append([d, a, b])
d_a01 = {}
for mode in ("floor", "ceiling", "additive", "shrink_only", "strengthen_only_bool"):
    reg = {"key": "K", "mode": mode, "kind": "level" if mode in ("floor", "ceiling") else None, "order": None, "strict_value": True if mode == "strengthen_only_bool" else None, "exception_relaxable": False}
    imm = {"key": "K", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}
    d_a01[f"immutable_vs_{mode}"] = {"revision_3_order_immutable_ge_registered": r3_rule_ge(imm, reg), "revision_4_order_immutable_ge_registered": L.rule_ge(imm, reg),
                                     "revision_4_is_a_computed_reduction_registered_to_immutable": not L.rule_ge(imm, reg), "revision_4_join_mode": L.rule_join(imm, reg)["mode"]}
partA = {"A1_order_soundness": {"combinations": len(dirs) * len(modes) ** 2, "unsound_pairs": unsound, "joins_dropping_strengthening_or_adding_weakening": join_drops, "RV3-D-A01_pairs": d_a01}}
removals = {}
for tag, rel in (("R01", "policies/SECURITY_POLICY.yaml"), ("R02", "constitution/HARD_INVARIANTS.yaml"), ("R03", "policies/ENFORCEMENT_MAP.yaml"),
                 ("R04", "schemas/adapter-manifest.schema.json"), ("R05", "roles/ROLES.yaml"), ("R06", "adapters/generic/template.md"), ("R07", "policies/POLICY_PRECEDENCE.yaml"),
                 ("R08", "policies/HUMAN_GATE_POLICY.yaml"), ("R09", "policies/AUTHORITY_POLICY.yaml")):
    removals[f"{tag} {rel}"] = check_kernel("removal-" + tag, INV, removed=rel)
partA["A3_RV3-D-A10_removals"] = removals

# ------------------------------------------------------------------------------------------------ scenarios
INV_SB = inv_with(INV, rules=rules_with(INV, {BOOL_KEY: {"mode": "strengthen_only_bool", "strict_value": False}}))
W0 = {"id": "genuine registration", "inv": INV, "overrides": OVERRIDES}
WSB = {"id": "constructed registration: continue_independent_work strengthen_only_bool(false)", "inv": INV_SB, "overrides": {**OVERRIDES, **BOOL_OVERRIDE}}
THREE = {"AUTHORITY_POLICY.authority_levels_required.*": "immutable", "SECURITY_POLICY.never_index_classes": "immutable", "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "immutable"}
SCEN = [
    {"id": "RV3-B-A01/floor->immutable", "world": W0, "kind": "kernel", "changes": {"AUTHORITY_POLICY.authority_levels_required.*": "immutable"}, "keys": ["AUTHORITY_POLICY.authority_levels_required.resume_control"], "harm": ["a"]},
    {"id": "RV3-B-A01/ceiling->immutable", "world": W0, "kind": "kernel", "changes": {"HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "immutable"}, "keys": ["HUMAN_GATE_POLICY.agent_resolvable_when.max_radius"], "harm": ["c"]},
    {"id": "RV3-B-A01/additive->immutable", "world": W0, "kind": "kernel", "changes": {"SECURITY_POLICY.never_index_classes": "immutable"}, "keys": ["SECURITY_POLICY.never_index_classes"], "harm": ["b"]},
    {"id": "RV3-B-A01/shrink_only->immutable", "world": W0, "kind": "kernel", "changes": {"TOOL_POLICY.approved_licences": "immutable", "LEARNING_POLICY.upstream.allowed_payload": "immutable"},
     "keys": ["TOOL_POLICY.approved_licences", "LEARNING_POLICY.upstream.allowed_payload"], "harm": []},
    {"id": "RV3-B-A01/strengthen_only_bool->immutable", "world": WSB, "kind": "kernel", "changes": {BOOL_KEY: "immutable"}, "keys": [BOOL_KEY], "harm": []},
    {"id": "RV3-B-A01/review_example_three_rules", "world": W0, "kind": "kernel", "changes": THREE, "keys": ["AUTHORITY_POLICY.authority_levels_required.resume_control", "SECURITY_POLICY.never_index_classes", "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius"], "harm": ["a", "b", "c"]},
    {"id": "RV3-D-A10-R07/POLICY_PRECEDENCE_deleted", "world": W0, "kind": "delete", "keys": list(OVERRIDES), "harm": ["a", "b", "c"]},
    {"id": "RV3-D-A02/TPS_tightening_never_index_classes_honest_owner", "world": W0, "kind": "tps", "changes": {"SECURITY_POLICY.never_index_classes": "immutable"}, "keys": ["SECURITY_POLICY.never_index_classes"], "harm": ["b"]},
    {"id": "RV3-D-A02/TPS_tightening_authority_levels_root_ceremony", "world": W0, "kind": "tps", "changes": {"AUTHORITY_POLICY.authority_levels_required.*": "immutable"}, "keys": ["AUTHORITY_POLICY.authority_levels_required.resume_control"], "harm": ["a"]},
]

MAT = {}


def materialise(rules, default_mode, delete_prec=False, kernel_values=None):
    key = hashlib.sha256(json.dumps({"r": rules, "dm": default_mode, "del": delete_prec, "kv": sorted((f"{a}:{b}", v) for (a, b), v in (kernel_values or {}).items())}, sort_keys=True, default=str).encode()).hexdigest()[:16]
    if key in MAT:
        return MAT[key]
    dst = os.path.join(S, "src-" + key)
    shutil.copytree(REL, dst)
    pp = os.path.join(dst, "kernel", "policies", "POLICY_PRECEDENCE.yaml")
    if delete_prec:
        shutil.move(pp, os.path.join(S, "aside-" + key + "-POLICY_PRECEDENCE.yaml"))
    elif rules is not None:
        ydump(pp, prec_doc(rules, default_mode))
    for (rel, dotted), val in (kernel_values or {}).items():
        p = os.path.join(dst, "kernel", rel)
        doc = yaml.safe_load(open(p))
        set_dotted(doc, dotted, val)
        ydump(p, doc)
    MAT[key] = dst
    return dst


plans, jobs = [], {}


def job(src, overrides):
    k = hashlib.sha256(json.dumps([src, overrides], sort_keys=True).encode()).hexdigest()[:12]
    jobs[k] = (k, src, overrides)
    return k


for sc in SCEN:
    winv, ov = sc["world"]["inv"], sc["world"]["overrides"]
    reg = winv["precedence"]
    plan = {"sc": sc, "genuine": job(materialise(reg["rules"], reg["default_mode"]) if winv is not INV else REL, ov)}
    if sc["kind"] == "kernel":
        krules = rules_with(winv, sc["changes"])
        plan["checker"] = {"attack_kernel_against_its_registration": check_kernel(hashlib.sha256(json.dumps(krules, sort_keys=True).encode()).hexdigest()[:10], winv, rules=krules)}
        r3 = r3_effective_rules(krules, reg["default_mode"], reg["rules"], reg["default_mode"])
        r4 = r4_effective_rules(winv)
        plan["ref"] = (winv, None)
    elif sc["kind"] == "delete":
        plan["checker"] = {"attack_kernel_against_its_registration": check_kernel("delete-precedence", winv, delete_prec=True)}
        r3 = r3_effective_rules([], "immutable", reg["rules"], reg["default_mode"])
        r4 = r4_effective_rules(winv)
        plan["ref"] = (winv, None)
    else:
        # a Trust Policy that registers `immutable` must also classify the affected leaves `equals` (inventory lint, 23 §5.1)
        v2 = inv_with(winv, rules=rules_with(winv, sc["changes"]))
        for f in v2["files"]:
            for l in f.get("leaves", []):
                if l.get("class") == "floor" and "[" not in l["key"] and any(L.precedence_key_matches(ck, l["key"]) for ck in sc["changes"]):
                    l.update({"op": "equals", "value": BASE_VALUES.get(l["key"], l.get("value"))})
                    for x in ("kind", "order", "strict"):
                        l.pop(x, None)
        subject = "POLICY_PRECEDENCE:" + next(iter(sc["changes"])).replace("*", "p3probe")
        plan["checker"] = {"release_registered_under_TPS_v2": check_kernel("tps-" + hashlib.sha256(json.dumps(sc["changes"]).encode()).hexdigest()[:8], v2, rules=v2["precedence"]["rules"]),
                           "reductions_v1_to_v2_without_lowering_history": {k: v for k, v in C.run_reductions(winv, v2, [], quiet=True).items() if k in ("exit", "undeclared")},
                           "reductions_v1_to_v2_with_lowering_history": {k: v for k, v in C.run_reductions(winv, v2, [r["subject"] for r in C.run_reductions(winv, v2, [], quiet=True)["reductions"]], quiet=True).items() if k in ("exit", "undeclared")},
                           "declared_subject_example": subject}
        r3 = r3_effective_rules(v2["precedence"]["rules"], reg["default_mode"], v2["precedence"]["rules"], reg["default_mode"])
        r4 = r4_effective_rules(v2, held_inv=winv)
        plan["r4_after_gate"] = job(materialise(r4_effective_rules(v2), reg["default_mode"]), ov)
        plan["ref"] = (v2, winv)
        plan["ref_after_gate"] = (v2, None)
    plan["r3_modes"] = {k: next(r["mode"] for r in r3 if L.precedence_key_matches(r["key"], k)) for k in sc["keys"]}
    plan["r4_modes"] = {k: next(r["mode"] for r in r4 if L.precedence_key_matches(r["key"], k)) for k in sc["keys"]}
    plan["r3_rules_changed_to_immutable"] = sum(1 for a, b in zip(r3, reg["rules"]) if a["mode"] == "immutable" and b["mode"] != "immutable")
    plan["r3"] = job(materialise(r3, reg["default_mode"]), ov)
    plan["r4"] = job(materialise(r4, reg["default_mode"]), ov)
    plans.append(plan)

# part D composition: a Trust Policy raises the never-index floor by one class the project did not list
sens = yaml.safe_load(open(os.path.join(REL, "kernel", "policies", "SECURITY_POLICY.yaml")))["sensitivity_classes"]
gen_never = BASE_VALUES["SECURITY_POLICY.never_index_classes"]
extra = next(c for c in sens if c not in gen_never and c not in ("confidential", "public"))
raised = list(gen_never) + [extra]
inv_raise = inv_with(INV, leaf_values={"SECURITY_POLICY.never_index_classes": raised})
base_raise = dict(BASE_VALUES, **{"SECURITY_POLICY.never_index_classes": raised})
eff_raise, ap_raise, rf_raise = L.project_effective(inv_raise, base_raise, OVERRIDES)
comp = {"raised_floor": raised, "revision_4_reference_effective": eff_raise["SECURITY_POLICY.never_index_classes"], "applied": ap_raise, "refused": rf_raise,
        "r3": job(materialise(None, None, kernel_values={("policies/SECURITY_POLICY.yaml", "never_index_classes"): raised}), OVERRIDES),
        "r4": job(materialise(None, None, kernel_values={("policies/SECURITY_POLICY.yaml", "never_index_classes"): eff_raise["SECURITY_POLICY.never_index_classes"]}), OVERRIDES)}


# ------------------------------------------------------------------------------------------------ part B: consumption on the real 4.1.5 binary
def gov(root, env, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-p1r4", "--role", role, *a], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p1r4", "-c", "user.email=p1r4@x", *a], cwd=root, check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": root})


def code(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def eff_value(res, dotted):
    r = res.get("result") or {}
    cur = r.get("effective") or r.get("policy") or {}
    for part in dotted.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def consume(j):
    label, src, overrides = j
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    env = dict(BASE_ENV)
    env.update({"HOME": os.path.join(S, "home-" + label), "GOV_KERNEL_CACHE": os.path.join(S, "cache-" + label)})
    os.makedirs(env["HOME"], exist_ok=True)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, env, "orchestrator", "init", "--source", src, "--name", "p1r4", "--skip-index")
    ov = os.path.join(root, "governance", "project")
    pdoc = yaml.safe_load(open(ov + "/PROJECT_POLICY.yaml"))
    pdoc["policy_overrides"] = dict(overrides)
    ydump(ov + "/PROJECT_POLICY.yaml", pdoc)
    ddoc = yaml.safe_load(open(ov + "/DATA_SENSITIVITY.yaml"))
    ddoc["classifications"] = list(CLASSIFICATIONS)
    ddoc["identifiers_to_strip"] = ["acme"]
    ydump(ov + "/DATA_SENSITIVITY.yaml", ddoc)
    os.makedirs(root + "/product/customers", exist_ok=True)
    open(root + "/product/customers/acme.md", "w").write(f"# ACME account notes {MARK}\n\nRenewal terms and contact list for ACME.\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project strengthening and material")
    trust = gov(root, env, "orchestrator", "kernel", "trust")
    effs = {n: gov(root, env, "orchestrator", "policy", "effective", n) for n in POLS}
    values = {k: eff_value(effs[k.split(".")[0]], k.split(".", 1)[1]) for k in OBSERVED}
    # 4.1.5 `policy effective` reports `effective`, `kernel` and `policy`; the outcome of each override is derived from them
    outcomes = {}
    for k, ov_value in overrides.items():
        res_ = effs[k.split(".")[0]].get("result") or {}
        kernel_doc = res_.get("kernel") if isinstance(res_.get("kernel"), dict) else {}
        kv = eff_value({"result": {"effective": kernel_doc}}, k.split(".", 1)[1]) if kernel_doc else None
        outcomes[k] = "applied" if same(values.get(k), ov_value) else ("not_applied_kernel_value_in_force" if kernel_doc and same(values.get(k), kv) else "not_applied")
    pause = gov(root, env, "orchestrator", "pause", "--reason", "p1r4")
    resume = gov(root, env, "orchestrator", "resume")
    if not resume.get("ok"):
        gov(root, env, "human", "resume")
    rb = gov(root, env, "orchestrator", "rebuild-memory")
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        indexed = bool([x[0] for x in con.execute("select path from artifacts") if x[0].endswith("customers/acme.md")])
        con.close()
    except sqlite3.Error as e:
        indexed = f"sqlite: {e}"
    q = gov(root, env, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("customers/acme.md")]
    g = gov(root, env, "orchestrator", "gate", "create", "--question", "Pick the low-risk option?", "--fields",
            json.dumps({"impact_radius": "R1", "confidence": 0.85, "reversibility": "reversible", "options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}]}))
    gid = (g.get("result") or {}).get("id")
    gov(root, env, "change-controller", "gate", "present", gid or "?")
    dec = gov(root, env, "change-controller", "decide", gid or "?", "--option", "A", "--by", "change-controller")
    overlay_docs = {}
    for dp, dns, fns in os.walk(ov):
        for fn in sorted(fns):
            if fn.endswith(".yaml"):
                overlay_docs[os.path.relpath(os.path.join(dp, fn), ov).replace(os.sep, "/")] = yaml.safe_load(open(os.path.join(dp, fn)))
    return label, {"init_ok": init.get("ok"), "init_code": code(init), "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
                   "effective_values": values, "override_outcomes": outcomes,
                   "a_orchestrator_L4_resume_under_project_L5": {"ok": resume.get("ok"), "code": code(resume), "pause_ok": pause.get("ok")},
                   "b_project_confidential_file": {"rebuild_ok": rb.get("ok"), "indexed": indexed, "retrievable": bool(hits)},
                   "c_L3_agent_answers_R1_gate_under_project_R0": {"ok": dec.get("ok"), "code": code(dec)}, "_overlay_docs": overlay_docs}


with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
    RES = dict(ex.map(consume, list(jobs.values())))


def harm(res, t):
    if t == "a":
        return res["a_orchestrator_L4_resume_under_project_L5"]["ok"] is True
    if t == "b":
        return res["b_project_confidential_file"]["indexed"] is True or res["b_project_confidential_file"]["retrievable"] is True
    return res["c_L3_agent_answers_R1_gate_under_project_R0"]["ok"] is True


def public(res):
    return {k: v for k, v in res.items() if not k.startswith("_")}


partB, partC = {}, {}
for plan in plans:
    sc = plan["sc"]
    winv, ov = sc["world"]["inv"], sc["world"]["overrides"]
    g, r3, r4 = RES[plan["genuine"]], RES[plan["r3"]], RES[plan["r4"]]
    eff_inv, held = plan["ref"]
    ref, ap, rf = L.project_effective(eff_inv, BASE_VALUES, ov, held)
    row = {"world": sc["world"]["id"], "checker": plan["checker"], "precedence_mode_for_project_layer": {"revision_3": plan["r3_modes"], "revision_4": plan["r4_modes"]},
           "revision_3_rules_turned_immutable": plan["r3_rules_changed_to_immutable"],
           "consumption": {"genuine": public(g), "revision_3_effective_kernel": public(r3), "revision_4_effective_kernel": public(r4)},
           "revision_4_reference_effective": {k: ref.get(k) for k in sc["keys"]},
           "verdicts": {"genuine_consumer_verified": g["kernel_trust_verified"] is True,
                        "revision_3_loses_project_strengthening": any(not same(r3["effective_values"][k], g["effective_values"][k]) for k in sc["keys"]),
                        "revision_4_keeps_project_strengthening": all(same(r4["effective_values"][k], g["effective_values"][k]) for k in sc["keys"]),
                        "revision_4_reference_matches_binary": all(same(ref.get(k), r4["effective_values"][k]) for k in sc["keys"]),
                        "harm_present_under_revision_3": {t: harm(r3, t) for t in sc["harm"]},
                        "harm_absent_under_revision_4": {t: not harm(r4, t) for t in sc["harm"]},
                        "harm_absent_on_genuine": {t: not harm(g, t) for t in sc["harm"]}}}
    if "r4_after_gate" in plan:
        ra = RES[plan["r4_after_gate"]]
        row["consumption"]["revision_4_after_per_project_policy_lowering_gate"] = public(ra)
        row["note_after_gate"] = "accepted reduction: the per-project policy_lowering trust gate presented the lost strengthening and the vector is re-recorded; not a harm assertion"
    # part C: project-owned strength recorded on the genuine consumer, evaluated over each consumer's effective policy
    reqs = L.strength_requirements(winv, g["_overlay_docs"], {k: g["effective_values"][k] for k in OBSERVED if g["effective_values"][k] is not None}, BASE_VALUES)
    fail3 = L.strength_failures(winv, reqs, r3["_overlay_docs"], r3["effective_values"])
    fail4 = L.strength_failures(winv, reqs, r4["_overlay_docs"], r4["effective_values"])
    row["verdicts"]["strength_vector_reports_revision_3_loss"] = bool(fail3)
    row["verdicts"]["strength_vector_quiet_under_revision_4"] = not fail4
    partC[sc["id"]] = {"recorded_requirements": [r for r in reqs if r["source"] == "effective_policy"], "failures_on_revision_3_consumer": fail3, "failures_on_revision_4_consumer": fail4}
    partB[sc["id"]] = row

c3, c4 = RES[comp["r3"]], RES[comp["r4"]]
partD = {"raised_never_index_floor": comp["raised_floor"], "revision_4_reference_effective": comp["revision_4_reference_effective"], "reference_applied": comp["applied"], "reference_refused": comp["refused"],
         "revision_3_effective_kernel": public(c3), "revision_4_effective_kernel": public(c4),
         "verdicts": {"revision_3_replacement_semantics_drop_project_class": harm(c3, "b") and "confidential" not in (c3["effective_values"]["SECURITY_POLICY.never_index_classes"] or []),
                      "revision_4_directed_join_keeps_project_class": not harm(c4, "b") and "confidential" in (c4["effective_values"]["SECURITY_POLICY.never_index_classes"] or [])}}

# part C (continued): release-signed migrations against the Overlay Surface whitelist and the vector (RV3-B-A18, CR-02)
gW0 = RES[plans[0]["genuine"]]
reqs0 = L.strength_requirements(INV, gW0["_overlay_docs"], {k: gW0["effective_values"][k] for k in OVERRIDES}, BASE_VALUES)


def apply_ops(docs, ops):
    docs = copy.deepcopy(docs)
    for op in ops:
        f = op.get("file")
        if f not in docs:
            continue
        if op["op"] == "set_overlay_key":
            cur = docs[f]
            parts = op["key"].split(".")
            for part in parts[:-1]:
                cur = cur.setdefault(part, {})
            cur[parts[-1]] = op["value"]
        elif op["op"] == "set_overlay_rule":
            for el in docs[f].get(op.get("list_key", "paths"), []):
                if all(el.get(k) == v for k, v in op["match"].items()):
                    el.update(op["set"])
    return docs


MIG = {
    "M1 set_overlay_key TOOL_PERMISSIONS install_authority_roles widened": [{"op": "set_overlay_key", "file": "TOOL_PERMISSIONS.yaml", "key": "install_authority_roles", "value": ["tooling-engineer", "orchestrator", "backend-engineer"]}],
    "M2 set_overlay_key TOOL_PERMISSIONS roles.backend-engineer gains SECRET_READ": [{"op": "set_overlay_key", "file": "TOOL_PERMISSIONS.yaml", "key": "roles.backend-engineer", "value": ["READ_REPO", "WRITE_REPO_SCOPED", "RUN_TESTS", "PACKAGE_INSTALL", "SECRET_READ"]}],
    "M3 set_overlay_key PROJECT_EXCEPTIONS exception added": [{"op": "set_overlay_key", "file": "PROJECT_EXCEPTIONS.yaml", "key": "exceptions", "value": [{"id": "EXC-0099", "policy": "MEMORY_POLICY", "key": "freshness.on_stale_close", "value": "degrade", "decision": "D-0007", "expires": "2099-12-31", "reason": "m"}]}],
    "M4 set_overlay_key DATA_SENSITIVITY identifiers_to_strip emptied": [{"op": "set_overlay_key", "file": "DATA_SENSITIVITY.yaml", "key": "identifiers_to_strip", "value": []}],
    "M5 set_overlay_rule REPOSITORY_CONTRACT **/.env* semantic_index true (registered target, weakening)": [{"op": "set_overlay_rule", "file": "REPOSITORY_CONTRACT.yaml", "list_key": "paths", "match": {"pattern": "**/.env*"}, "set": {"semantic_index": True}}],
    "M6 set_overlay_key ../../spec/decisions/HDG-0001.yaml": [{"op": "set_overlay_key", "file": "../../spec/decisions/HDG-0001.yaml", "key": "status", "value": "ANSWERED"}],
    "M7 set_overlay_key PROJECT_POLICY policy_overrides drops the project never-index class": [{"op": "set_overlay_key", "file": "PROJECT_POLICY.yaml", "key": "policy_overrides", "value": {k: v for k, v in OVERRIDES.items() if k != "SECURITY_POLICY.never_index_classes"}}],
    "M8 control: set_overlay_rule REPOSITORY_CONTRACT archive/** lexical_index false (registered target, strengthening)": [{"op": "set_overlay_rule", "file": "REPOSITORY_CONTRACT.yaml", "list_key": "paths", "match": {"pattern": "archive/**"}, "set": {"lexical_index": False}}],
}
migrations = {}
for name, ops in MIG.items():
    docs = apply_ops(gW0["_overlay_docs"], ops)
    vals = dict(gW0["effective_values"])
    po = (docs.get("PROJECT_POLICY.yaml") or {}).get("policy_overrides") or {}
    if po != OVERRIDES:
        eff_m, _, _ = L.project_effective(INV, BASE_VALUES, po)
        vals.update({k: eff_m.get(k) for k in OBSERVED})
    probs = L.migration_op_problems(INV, {"operations": ops})
    fails = L.strength_failures(INV, reqs0, docs, vals)
    migrations[name] = {"refused_before_any_write": bool(probs), "whitelist_problems": probs, "computed_weakenings": fails, "weakening_trust_gate_required": bool(fails)}
partC["release_signed_migrations"] = migrations

out["partA_reference"] = partA
out["partB_consumption_4_1_5"] = partB
out["partC_project_strength"] = partC
out["partD_composition"] = partD
v = {sid: row["verdicts"] for sid, row in partB.items()}
out["summary"] = {
    "order_unsound_pairs": len(unsound), "joins_dropping_strengthening": len(join_drops),
    "removal_checker_exits": {k: r["exit"] for k, r in removals.items()},
    "attack_checker_exits": {sid: {kk: (vv.get("exit") if isinstance(vv, dict) else vv) for kk, vv in row["checker"].items()} for sid, row in partB.items()},
    "revision_3_loses_strengthening": {sid: x["revision_3_loses_project_strengthening"] for sid, x in v.items()},
    "revision_4_keeps_strengthening": {sid: x["revision_4_keeps_project_strengthening"] for sid, x in v.items()},
    "revision_4_reference_matches_binary": {sid: x["revision_4_reference_matches_binary"] for sid, x in v.items()},
    "harm_flips": {sid: {t: x["harm_present_under_revision_3"][t] and x["harm_absent_under_revision_4"][t] for t in x["harm_present_under_revision_3"]} for sid, x in v.items()},
    "strength_vector": {sid: {"reports_revision_3_loss": x["strength_vector_reports_revision_3_loss"], "quiet_under_revision_4": x["strength_vector_quiet_under_revision_4"]} for sid, x in v.items()},
    "composition": partD["verdicts"],
    "migrations": {k: {"refused_before_any_write": m["refused_before_any_write"], "weakening_trust_gate_required": m["weakening_trust_gate_required"]} for k, m in migrations.items()},
    "consumers_run": len(RES), "all_consumers_initialised": all(r["init_ok"] for r in RES.values())}
text = json.dumps(out, indent=1, default=str)
text = text.replace(S, "<scratch>").replace(REPO, "<repo>").replace(os.path.dirname(GOV), "<legacy-bin>")
print(text)
