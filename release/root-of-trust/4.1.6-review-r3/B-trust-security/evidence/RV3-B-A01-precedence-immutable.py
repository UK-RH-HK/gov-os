#!/usr/bin/env python3
"""RV3-B-A01 — held-out attack by review r3 B (AR-0002). Scratch only; the repository is never written.

Question: the revision-3 precedence lattice (`23` §4) treats `immutable` as at least as strong as every other mode, and
the join of incomparable rules as `immutable`. For the project layer, `immutable` refuses *every* override, including a
strengthening (runtime/src/policy_precedence.rs `evaluate`, unchanged by revision 3, which keeps the "project layer may
only strengthen" model). Can a kernel that changes nothing but precedence modes toward `immutable`:
  (1) pass the architect's coverage checker (E7 reference, exit 0) and be surface-eligible;
  (2) have an effective per-key precedence rule (the `23` §4 join) of `immutable`;
  (3) when consumed, discard project-owned strengthening of authority, indexing exclusion and gate resolution;
  (4) escape the revision-3 weakening detectors, whose inputs are the overlay (`19` §9 computed weakening, `26` §6 vector)?

Part A evaluates (1), (2) and (4) with the pack's own reference library (`constitutional-surface/csi_lib.py`,
`csi_check.py`) and inventory. Part B consumes the kernel on the real 4.1.5 binary. Because every floor, pinned, member
and precedence check passes and every floor leaf is unchanged, the revision-3 effective kernel (`19` §5.2: root kernel,
floor leaves joined, precedence joined per key) is byte-identical in content to the tampered kernel; this is checked
explicitly (part A `effective_rules_equal_tampered_rules`). The 4.1.5 directory-source install path (review r2 P1 V-H3
note) is used only to obtain a verified policy root carrying that content.

Environment: GOV (default legacy 4.1.5), REVIEW_REPO (worktree), GOV_REVIEW_SCRATCH. GOV_* stripped from children;
GOV_KERNEL_CACHE and HOME in scratch.
"""
import copy, hashlib, json, os, shutil, sqlite3, subprocess, sys, tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("REVIEW_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PACK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
sys.path.insert(0, os.path.join(PACK, "constitutional-surface"))
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
INV = yaml.safe_load(open(os.path.join(PACK, "constitutional-surface", "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="rv3b-a01-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
ENV["HOME"] = S + "/home"
os.makedirs(ENV["HOME"], exist_ok=True)

# The only change: three precedence rules move to `immutable` (a "strengthening" under the 23 §4 lattice).
TO_IMMUTABLE = {
    "AUTHORITY_POLICY.authority_levels_required.*": "floor",          # project raises of required levels
    "SECURITY_POLICY.never_index_classes": "additive",                  # project additions of never-index classes
    "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "ceiling",    # project narrowing of agent gate resolution
}
# Project-owned strengthening, each permitted by the genuine registered precedence.
OVERRIDES = {
    "AUTHORITY_POLICY.authority_levels_required.resume_control": "L5",
    "SECURITY_POLICY.never_index_classes": ["secret", "restricted", "confidential"],
    "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "R0",
}
CLASSIFICATIONS = [{"pattern": "product/customers/**", "class": "confidential", "reason": "customer data (project-owned classification)"}]
MARK = "RV3BA01CUSTOMERMARKER"

out = {"attack": "RV3-B-A01", "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "scratch": "<scratch>",
       "kernel_change": {k: f"{v} -> immutable" for k, v in TO_IMMUTABLE.items()}, "project_overrides": OVERRIDES, "project_classifications": CLASSIFICATIONS}


def ydump(p, d):
    with open(p, "w") as fh:
        yaml.safe_dump(d, fh, sort_keys=False)


# ------------------------------------------------------------------------------------------------ part A: revision-3 reference checks
T = S + "/src-tampered-precedence"
shutil.copytree(REL, T)
pp = os.path.join(T, "kernel", "policies", "POLICY_PRECEDENCE.yaml")
doc = yaml.safe_load(open(pp))
changed = []
for r in doc["rules"]:
    if r["key"] in TO_IMMUTABLE:
        assert r["mode"] == TO_IMMUTABLE[r["key"]], (r["key"], r["mode"])
        r["mode"] = "immutable"
        for k in ("kind", "order", "strict_value"):
            r.pop(k, None)
        changed.append(r["key"])
ydump(pp, doc)

partA = {"rules_changed": changed}
for label, kd in (("genuine_4.1.5", REL + "/kernel"), ("tampered_precedence", T + "/kernel")):
    rep = C.run_check(kd, INV, quiet=True)
    ev = L.evaluate(INV, kd)
    partA[label] = {"csi_check_exit": rep["exit"], "surface_ok": ev["surface_ok"], "eligible_surface": ev["eligible_surface"],
                    "violations": ev["violations"][:5], "precedence_weaker_key_count": len(ev.get("precedence_weaker_keys", []))}

reg = INV["precedence"]
kr = [L.rule_tuple(r) for r in doc["rules"]]
join = {}
for key in list(OVERRIDES) + ["AUTHORITY_POLICY.authority_levels_required.update_apply"]:
    a = L.effective_rule(kr, doc.get("default_mode", "immutable"), key)
    b = L.effective_rule(reg["rules"], reg["default_mode"], key)
    join[key] = {"kernel_rule": a["mode"], "registered_rule": b["mode"], "lattice_kernel_ge_registered": L.rule_ge(a, b),
                 "lattice_registered_ge_kernel": L.rule_ge(b, a), "effective_join": L.rule_join(a, b)["mode"]}
partA["per_key_join_23_s4"] = join
# 19 §5.2: the effective precedence rule of every rule key is the join; check it equals the tampered kernel rule (so the
# materialised effective kernel equals the tampered kernel for precedence), and floor leaves equal genuine.
eq = True
for r in kr:
    probe_key = r["key"].replace("*", "p3probe")
    j = L.rule_join(L.effective_rule(kr, doc.get("default_mode"), probe_key), L.effective_rule(reg["rules"], reg["default_mode"], probe_key))
    if j["mode"] != L.effective_rule(kr, doc.get("default_mode"), probe_key)["mode"]:
        eq = False
partA["effective_rules_equal_tampered_rules"] = eq
g_eff = L.evaluate(INV, REL + "/kernel")["effective"]
t_eff = L.evaluate(INV, T + "/kernel")["effective"]
floor_keys = [l["key"] for f in INV["files"] if f.get("mode") == "structured" for l in f["leaves"] if l["class"] == "floor"]
partA["floor_effective_values_equal_genuine"] = all(json.dumps(g_eff.get(k), sort_keys=True, default=str) == json.dumps(t_eff.get(k), sort_keys=True, default=str) for k in g_eff if not k.startswith("POLICY_PRECEDENCE"))
# Lattice direction check: the reverse change (immutable -> floor) is reported as a weakening.
partA["lattice_reports_immutable_to_floor_as_weaker"] = not L.rule_ge({"key": "x", "mode": "floor", "kind": "level", "order": None, "strict_value": None, "exception_relaxable": False},
                                                                     {"key": "x", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False})
out["partA_revision3_reference"] = partA


# ------------------------------------------------------------------------------------------------ part B: consumption on the real 4.1.5 binary
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv3b-a01", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")


def overlay_digest(root):
    h = hashlib.sha256()
    od = os.path.join(root, "governance", "project")
    for dp, dns, fns in sorted(os.walk(od)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            h.update(os.path.relpath(p, od).encode() + b"\0" + open(p, "rb").read())
    return "sha256:" + h.hexdigest()


def consume(label, src):
    root = f"{S}/consumer-{label}"
    os.makedirs(root)
    git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "rv3ba01", "--skip-index")
    ppath = os.path.join(root, "governance", "project", "PROJECT_POLICY.yaml")
    pdoc = yaml.safe_load(open(ppath))
    pdoc["policy_overrides"] = dict(OVERRIDES)
    ydump(ppath, pdoc)
    dpath = os.path.join(root, "governance", "project", "DATA_SENSITIVITY.yaml")
    ddoc = yaml.safe_load(open(dpath))
    ddoc["classifications"] = list(CLASSIFICATIONS)
    ydump(dpath, ddoc)
    os.makedirs(root + "/product/customers", exist_ok=True)
    open(root + "/product/customers/acme.md", "w").write(f"# ACME account notes {MARK}\n\nRenewal terms and contact list for ACME.\n")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "project strengthening and material")
    ov_before = overlay_digest(root)
    trust = gov(root, "orchestrator", "kernel", "trust")
    effs = {n: gov(root, "orchestrator", "policy", "effective", n) for n in ("AUTHORITY_POLICY", "SECURITY_POLICY", "HUMAN_GATE_POLICY")}

    def eff_value(res, dotted):
        r = res.get("result") or {}
        pol = r.get("effective") or r.get("policy") or {}
        cur = pol
        for part in dotted.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        return cur

    refused = []
    for n, res in effs.items():
        r = res.get("result") or {}
        for x in (r.get("refused_overrides") or []):
            refused.append({"policy": x.get("policy"), "key": x.get("key"), "reason": (x.get("reason") or "")[:160]})
    # (a) authority: project raised resume_control to L5; orchestrator is L4
    pause = gov(root, "orchestrator", "pause", "--reason", "rv3b-a01")
    resume = gov(root, "orchestrator", "resume")
    if not resume.get("ok"):
        gov(root, "human", "resume")
    # (b) indexing: project added `confidential` to never_index_classes and classified product/customers/** confidential
    rb = gov(root, "orchestrator", "rebuild-memory")
    con = sqlite3.connect(root + "/.governance-runtime/state.db")
    indexed = [x[0] for x in con.execute("select path from artifacts") if x[0].endswith("customers/acme.md")]
    try:
        excluded = [list(x) for x in con.execute("select path, reason from excluded") if x[0].endswith("customers/acme.md")]
    except sqlite3.Error:
        excluded = "no excluded table"
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("customers/acme.md")]
    # (c) gates: project narrowed agent resolution to R0; an L3 agent answers an R1, 0.85, reversible gate
    g = gov(root, "orchestrator", "gate", "create", "--question", "Pick the low-risk option?", "--fields",
            json.dumps({"impact_radius": "R1", "confidence": 0.85, "reversibility": "reversible", "options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}]}))
    gid = (g.get("result") or {}).get("id")
    gov(root, "change-controller", "gate", "present", gid or "?")
    dec = gov(root, "change-controller", "decide", gid or "?", "--option", "A", "--by", "change-controller")
    ov_after = overlay_digest(root)
    return {"init_ok": init.get("ok"), "init_code": code(init), "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
            "effective_values": {"resume_control": eff_value(effs["AUTHORITY_POLICY"], "authority_levels_required.resume_control"),
                                 "never_index_classes": eff_value(effs["SECURITY_POLICY"], "never_index_classes"),
                                 "agent_resolvable_when.max_radius": eff_value(effs["HUMAN_GATE_POLICY"], "agent_resolvable_when.max_radius")},
            "refused_overrides": refused,
            "a_orchestrator_L4_resume_with_project_raise_L5": {"ok": resume.get("ok"), "code": code(resume), "pause_ok": pause.get("ok")},
            "b_project_confidential_file": {"rebuild_ok": rb.get("ok"), "indexed": indexed, "excluded": excluded, "retrievable": hits},
            "c_agent_answers_R1_gate_with_project_R0": {"gate": gid, "ok": dec.get("ok"), "code": code(dec)},
            "overlay_digest_unchanged_during_run": ov_before == ov_after, "overlay_digest": ov_after}


gen = consume("genuine", REL)
tam = consume("tampered-precedence", T)
out["partB_consumption_4_1_5"] = {"genuine": gen, "tampered_precedence_only": tam}
# (4) revision-3 weakening detectors take the overlay as input (19 §9: computed from overlay changes made by a migration or
# overlay.prev restore; 26 §6: "the current overlay is compared with the recorded vector"). The overlay bytes are identical
# in both consumers and unchanged by the kernel swap, so both detectors compute an empty weakening list.
same_overlay_content = gen["overlay_digest"] == tam["overlay_digest"]
out["partC_revision3_detectors"] = {"overlay_identical_between_genuine_and_tampered_consumers": same_overlay_content,
                                    "computed_weakening_19_s9_input_changed": False, "strength_vector_26_s6_input_changed": False,
                                    "note": "neither detector evaluates effective policy, so neither reports PROJECT_STRENGTH_WEAKENED or a weakening gate"}
out["verdicts"] = {
    "passes_E7_reference_checker": partA["tampered_precedence"]["csi_check_exit"] == 0 and partA["tampered_precedence"]["eligible_surface"],
    "effective_join_is_immutable_for_all_three_keys": all(join[k]["effective_join"] == "immutable" for k in OVERRIDES),
    "a_authority_strengthening_discarded": gen["a_orchestrator_L4_resume_with_project_raise_L5"]["code"] == "AUTHORITY_DENIED" and tam["a_orchestrator_L4_resume_with_project_raise_L5"]["ok"] is True,
    "b_indexing_strengthening_discarded": (not gen["b_project_confidential_file"]["indexed"]) and bool(tam["b_project_confidential_file"]["indexed"]) and bool(tam["b_project_confidential_file"]["retrievable"]),
    "c_gate_strengthening_discarded": gen["c_agent_answers_R1_gate_with_project_R0"]["code"] == "AUTHORITY_DENIED" and tam["c_agent_answers_R1_gate_with_project_R0"]["ok"] is True,
    "both_policy_roots_verified": gen["kernel_trust_verified"] is True and tam["kernel_trust_verified"] is True,
    "revision3_detectors_silent": same_overlay_content,
}
print(json.dumps(out, indent=1, default=str))
