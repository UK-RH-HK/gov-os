#!/usr/bin/env python3
# COPIED for re-execution by review r3 B (AR-0002) from release/root-of-trust/4.1.6-review-r2/evidence/P1-floor-coverage.py (commit e5a6b8a),
# unmodified except: REPO points at the reviewer worktree (read-only source of release payloads) and GOV defaults to the legacy 4.1.5 binary.
"""P1 — Trust Policy floor coverage (RoT-1 revision 2, `19` §4–§6). Scratch only; the repository is never written.

Question: does "authenticity (+ eligibility) never confers weaker constitutional policy" hold for every constitutional
input, or only for the 145 keys the pack registers as floors?

Part 1 (static). Regenerate TPS v1 floors exactly as `examples/make_example.py` lines 293-311 derive them from the
4.1.5 kernel. Enumerate every leaf of the constitutional files named by asset AS-1 (`01` §1) and report which leaves no
floor key covers.

Part 2 (reference evaluation). Build a kernel that changes ONLY unfloored leaves (ROLES level, SECURITY_POLICY secret
patterns, HUMAN_GATE_POLICY.agent_resolvable_when) and evaluate all 145 TPS v1 floors against it with the `19` §4
operators. If every floor holds, the pack's floor would accept this kernel content as a policy root once it is
authentic and eligible (a future release, an older eligible release restored by Git/rollback, or a release-final key
thief).

Part 3 (consumption, 4.1.5 binary). Show that the same unfloored leaves decide authority, secret exclusion and agent gate
answering at use time. The tampered kernel is installed through the V-H3 path only as a stand-in for "a policy root whose
registered floors all hold"; `kernel trust` must report verified:true for both consumers so the comparison is between
two policy roots, not between trusted and untrusted.
"""
import copy, json, os, shutil, sqlite3, subprocess, tempfile
import yaml

REPO = os.environ.get("REVIEW_REPO", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r3-b")
GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = REPO + "/release/releases/4.1.5"
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="p1-floor-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
out = {"scratch": S, "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip()}


def y(kdir, rel):
    return yaml.safe_load(open(os.path.join(kdir, rel)))


# ---------------------------------------------------------------- part 1: floors exactly as make_example.py derives them
kdir = REL + "/kernel"
auth, sec, hg, tool, prec = (y(kdir, f"policies/{n}.yaml") for n in ["AUTHORITY_POLICY", "SECURITY_POLICY", "HUMAN_GATE_POLICY", "TOOL_POLICY", "POLICY_PRECEDENCE"])
inv = y(kdir, "constitution/HARD_INVARIANTS.yaml")
floors = [{"key": f"AUTHORITY_POLICY.authority_levels_required.{op}", "op": "level_at_least", "value": lv} for op, lv in auth["authority_levels_required"].items()]
floors += [{"key": "SECURITY_POLICY.never_index_classes", "op": "set_superset", "value": sec["never_index_classes"]},
           {"key": "SECURITY_POLICY.never_export_classes", "op": "set_superset", "value": sec["never_export_classes"]},
           {"key": "SECURITY_POLICY.on_secret_in_export_payload", "op": "equals", "value": sec["on_secret_in_export_payload"]},
           {"key": "SECURITY_POLICY.agent_read_default_for_secret_class", "op": "equals", "value": sec["agent_read_default_for_secret_class"]},
           {"key": "HUMAN_GATE_POLICY.raise_for", "op": "set_superset", "value": hg["raise_for"]},
           {"key": "HUMAN_GATE_POLICY.must_be_presented_in_chat", "op": "bool_required", "value": hg["must_be_presented_in_chat"]},
           {"key": "TOOL_POLICY.plugins.min_authority", "op": "level_at_least", "value": tool["plugins"]["min_authority"]},
           {"key": "TOOL_POLICY.plugins.elevated_permission_classes", "op": "set_superset", "value": tool["plugins"]["elevated_permission_classes"]},
           {"key": "TOOL_POLICY.plugins.registration_binds", "op": "set_superset", "value": tool["plugins"]["registration_binds"]},
           {"key": "TOOL_POLICY.plugins.refuse_on_pin_drift", "op": "bool_required", "value": tool["plugins"]["refuse_on_pin_drift"]},
           {"key": "TOOL_POLICY.plugins.require_valid_descriptor", "op": "bool_required", "value": tool["plugins"]["require_valid_descriptor"]},
           {"key": "POLICY_PRECEDENCE.default_mode", "op": "equals", "value": prec["default_mode"]},
           {"key": "HARD_INVARIANTS.invariants[*].id", "op": "set_superset", "value": sorted(str(i["id"]) for i in inv["invariants"])}]
floors += [{"key": f"POLICY_PRECEDENCE.rules[key={r['key']}]", "op": "rule_mode_at_least", "value": r["mode"]} for r in prec["rules"]]
out["tps_v1_floor_count"] = len(floors)

AS1 = {"SECURITY_POLICY": "policies/SECURITY_POLICY.yaml", "AUTHORITY_POLICY": "policies/AUTHORITY_POLICY.yaml",
       "POLICY_PRECEDENCE": "policies/POLICY_PRECEDENCE.yaml", "HUMAN_GATE_POLICY": "policies/HUMAN_GATE_POLICY.yaml",
       "TOOL_POLICY": "policies/TOOL_POLICY.yaml", "HARD_INVARIANTS": "constitution/HARD_INVARIANTS.yaml", "ROLES": "roles/ROLES.yaml"}
# other kernel policies that decide gating, retrieval access, export or execution (not in AS-1, reported separately)
OTHER = {n: f"policies/{n}.yaml" for n in ["CHANGE_POLICY", "MEMORY_POLICY", "CONTEXT_POLICY", "ARCHIVE_POLICY", "TEST_POLICY", "CHECKPOINT_POLICY", "ENFORCEMENT_MAP"]}


def leaves(v, path):
    if isinstance(v, dict) and v:
        for k, x in v.items():
            yield from leaves(x, f"{path}.{k}")
    elif isinstance(v, list) and v and all(isinstance(e, dict) for e in v):
        yield path + "[*]", v  # a list of objects is reported as one leaf (e.g. ROLES.roles[*], rules[*])
    else:
        yield path, v


fkeys = [f["key"] for f in floors]


def covered(leaf):
    if leaf.startswith("POLICY_PRECEDENCE.rules[*]"):
        return "partially (mode of each rule only)"
    if leaf.startswith("HARD_INVARIANTS.invariants[*]"):
        return "partially (ids only; statements, enforcement and scope are not floored)"
    return any(leaf == k or leaf.startswith(k + ".") for k in fkeys)


coverage = {}
for name, rel in {**AS1, **OTHER}.items():
    doc = y(kdir, rel)
    ls = [p for p, _ in leaves(doc, name) if not p.endswith((".policy", ".version"))]
    cov = {p: covered(p) for p in ls}
    coverage[name] = {"asset_AS1": name in AS1, "leaves": len(ls), "floored": sum(1 for c in cov.values() if c is True),
                      "partially": sorted(p for p, c in cov.items() if isinstance(c, str)),
                      "unfloored": sorted(p for p, c in cov.items() if c is False)}
out["part1_static_coverage"] = coverage

# ---------------------------------------------------------------- part 2: evaluate floors against a kernel changing only unfloored leaves
LV = lambda s: int(str(s)[1:]) if str(s).startswith("L") else -1


def get(kd, key):
    pol, _, rest = key.partition(".")
    rel = AS1.get(pol) or f"policies/{pol}.yaml"
    doc = y(kd, rel)
    if key.startswith("POLICY_PRECEDENCE.rules[key="):
        rk = key[len("POLICY_PRECEDENCE.rules[key="):-1]
        return next((r.get("mode") for r in doc["rules"] if r["key"] == rk), None)
    if key == "HARD_INVARIANTS.invariants[*].id":
        return [str(i["id"]) for i in doc["invariants"]]
    cur = doc
    for part in rest.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def holds(f, v):
    op, fv = f["op"], f["value"]
    if op == "level_at_least":
        return v is None or LV(v) >= LV(fv)  # a missing key takes the floor value (19 §5)
    if op == "set_superset":
        return v is not None and set(map(str, fv)) <= set(map(str, v))
    if op in ("equals", "bool_required"):
        return v == fv
    if op == "rule_mode_at_least":
        return v == fv or v == "immutable"
    return False


def tamper(dst):
    shutil.copytree(REL, dst)
    k = dst + "/kernel"
    roles = y(k, "roles/ROLES.yaml")
    for r in roles["roles"]:
        if r["id"] == "backend-engineer":
            r["level"] = "L4"  # an L1 worker becomes an orchestrator-level role
    yaml.safe_dump(roles, open(k + "/roles/ROLES.yaml", "w"), sort_keys=False)
    s = y(k, "policies/SECURITY_POLICY.yaml")
    s["secret_path_patterns"] = []
    s["secret_content_patterns"] = [{"id": "none", "regex": "ZZZ_NEVER_MATCHES_ZZZ"}]  # empty lists fall back to built-ins
    yaml.safe_dump(s, open(k + "/policies/SECURITY_POLICY.yaml", "w"), sort_keys=False)
    h = y(k, "policies/HUMAN_GATE_POLICY.yaml")
    h["agent_resolvable_when"] = {"max_radius": "R5", "min_confidence": 0.0, "reversible": False}
    yaml.safe_dump(h, open(k + "/policies/HUMAN_GATE_POLICY.yaml", "w"), sort_keys=False)
    return dst


T = tamper(S + "/tampered-source-4.1.5")
evals = {}
for label, kd in (("genuine_4.1.5", kdir), ("tampered_unfloored_only", T + "/kernel")):
    failed = [f["key"] for f in floors if not holds(f, get(kd, f["key"]))]
    evals[label] = {"floors_evaluated": len(floors), "floors_violated": failed}
out["part2_floor_evaluation"] = evals
out["part2_tampered_leaves"] = ["ROLES.roles[id=backend-engineer].level L1->L4", "SECURITY_POLICY.secret_path_patterns -> []",
                                "SECURITY_POLICY.secret_content_patterns -> [never-matching]", "HUMAN_GATE_POLICY.agent_resolvable_when -> R5 / 0.0 / irreversible allowed"]


# ---------------------------------------------------------------- part 3: consumption on the 4.1.5 binary
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-p1", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")
MARK = "P1SECRETMARKER"
part3 = {}
for label, src in (("genuine", REL), ("tampered", T)):
    root = f"{S}/consumer-{label}"
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "p1", "--skip-index")
    os.makedirs(root + "/product", exist_ok=True)
    open(root + "/product/aws-credentials.md", "w").write(f"# Deploy notes {MARK}\n\naws_access_key_id = AKIAABCDEFGHIJKLMNOP\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    eff = gov(root, "orchestrator", "policy", "effective", "AUTHORITY_POLICY")
    auth_req = ((eff.get("result") or {}).get("effective") or (eff.get("result") or {}).get("policy") or {})
    # a) authority: an L1 role performing an L4 operation while every AUTHORITY_POLICY floor is unchanged
    pause = gov(root, "orchestrator", "pause", "--reason", "p1")
    resume = gov(root, "backend-engineer", "resume")
    if not resume.get("ok"):
        gov(root, "orchestrator", "resume")  # control consumer: lift the pause so (b) and (c) run on an unpaused project
    # b) secrets: is the credentials file excluded as secret or indexed and retrievable?
    rb = gov(root, "orchestrator", "rebuild-memory")
    con = sqlite3.connect(root + "/.governance-runtime/state.db")
    indexed = [r[0] for r in con.execute("select path from artifacts") if r[0].endswith("aws-credentials.md")]
    excluded = [list(r) for r in con.execute("select path, reason from excluded") if r[0].endswith("aws-credentials.md")]
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("aws-credentials.md")]
    # c) gates: an L3 agent answering an R5, low-confidence, irreversible gate as an agent
    g = gov(root, "orchestrator", "gate", "create", "--question", "Approve irreversible R5 change?", "--fields",
            json.dumps({"impact_radius": "R5", "confidence": 0.1, "reversibility": "irreversible", "options": [{"id": "A", "description": "approve"}, {"id": "B", "description": "refuse"}]}))
    gid = ((g.get("result") or {}).get("id")) or ((g.get("result") or {}).get("gate") or {}).get("id")
    pres = gov(root, "change-controller", "gate", "present", gid or "?")
    dec = gov(root, "change-controller", "decide", gid or "?", "--option", "A", "--by", "change-controller")
    part3[label] = {
        "init_ok": init.get("ok"),
        "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
        "a_L1_backend_engineer_resume": {"ok": resume.get("ok"), "code": code(resume), "pause_ok": pause.get("ok")},
        "b_secret_file": {"rebuild_ok": rb.get("ok"), "indexed": indexed, "excluded": excluded, "retrievable_by_query": hits},
        "c_agent_answers_R5_gate": {"gate": gid, "present_ok": pres.get("ok"), "decide_ok": dec.get("ok"), "code": code(dec),
                                    "answered_by_kind": (((dec.get("result") or {}).get("answered_by_kind")))},
    }
out["part3_consumption_4_1_5"] = part3
print(json.dumps(out, indent=2))
