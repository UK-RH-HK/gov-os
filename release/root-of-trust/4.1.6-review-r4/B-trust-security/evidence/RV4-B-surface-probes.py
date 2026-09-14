#!/usr/bin/env python3
"""RV4-B surface probes — held-out attacks of review r4 reviewer B (AR-0006). Scratch only; the repository is never written.

Instruments (revision 4, loaded by path, unmodified):
  - the pack's coverage checker `constitutional-surface/csi_check.py` (`run_check`, `run_reductions`) and library `csi_lib.py`;
  - the draft Trust Policy v1 surface `CONSTITUTIONAL_SURFACE_INVENTORY.yaml`;
  - the real legacy 4.1.5 binary as a stand-in consumer (review r3 B RV3-B-A01 and the architect's P1r4 use it the same way:
    the directory-source install path yields a verified policy root carrying the probed kernel content).

Parts
  U  (RV4-B-A09) unknown constitutional keys and new constitutional files, beyond review r3 I01-I09: wildcard-covered keys,
     a new namespace, a new KERNEL key, a new member field, new files, optional-file removal.
  T  (RV4-B-A10) a kernel that changes ONLY leaves classified `project_tunable` (non-security) — checker result, then
     consumption on 4.1.5 with the review-r3 harm battery (authority, confidential indexing, R0 gate) plus archive retrieval.
  P  (RV4-B-A08) pinned content registered with more than one digest (a Trust Policy that keeps an older release's digest
     while registering a fixed one): a higher-sequence kernel that mixes the older registered digest into otherwise new
     content — checker, `reductions`, direction/strength-vector coverage, and consumption on 4.1.5 (a secret the fixed
     pattern detects).

Environment: REVIEW_REPO (worktree), GOV (default legacy 4.1.5), GOV_REVIEW_SCRATCH. GOV_* stripped from children;
HOME and GOV_KERNEL_CACHE point into scratch. Output: JSON on stdout (absolute scratch paths replaced by <scratch>).
"""
import copy, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PACK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
CS = os.path.join(PACK, "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
FW = os.path.join(REPO, "framework")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="rv4b-surface-", dir=os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir())
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
ENV["HOME"] = S + "/home"
os.makedirs(ENV["HOME"], exist_ok=True)
out = {"probe": "RV4-B surface probes (AR-0006)", "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(),
       "checker": "release/root-of-trust/4.1.6/constitutional-surface/csi_check.py (revision 4, unmodified)", "scratch": "<scratch>"}


def ydump(p, d):
    C.ydump(p, d)


def mut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    ydump(p, d)


def kcopy(name, src=FW):
    d = os.path.join(S, "k", name)
    shutil.copytree(src, d)
    return d


def check(kdir, inv=INV):
    r = C.run_check(kdir, inv, quiet=True)
    keep = {"exit": r["exit"]}
    for k in ("unclassified_files", "unclassified_leaves", "required_missing", "violations", "structure", "consistency", "malformed"):
        if r.get(k):
            keep[k] = [str(x)[:220] for x in r[k][:6]]
    return keep


def runtime_readers(token):
    hits = []
    for base in ("runtime/src", "cli/src"):
        for dp, _, fns in os.walk(os.path.join(REPO, base)):
            for fn in fns:
                if fn.endswith(".rs"):
                    p = os.path.join(dp, fn)
                    for i, line in enumerate(open(p, errors="replace"), 1):
                        if token in line:
                            hits.append(f"{os.path.relpath(p, REPO)}:{i}")
    return hits


# ================================================================================================ part U
U = []


def ucase(cid, desc, fn, expect_note, src=FW):
    k = kcopy("U-" + cid, src)
    fn(k)
    row = {"case": cid, "change": desc, "base_kernel": "framework/" if src == FW else "release/releases/4.1.5/kernel", "checker": check(k), "expectation_under_default_deny": expect_note}
    if src != FW:
        base = check(src)
        row["checker_on_unmodified_base"] = base
        row["problems_added_by_change"] = sorted(set(sum([v for kk, v in row["checker"].items() if kk != "exit"], [])) - set(sum([v for kk, v in base.items() if kk != "exit"], [])))
    U.append(row)


ucase("U01", "ROLES.authority_levels.L2.may_answer_trust_gates: true (new key under the wildcard informational rule ROLES.authority_levels.*.*)",
      lambda k: mut(k, "roles/ROLES.yaml", lambda d: d["authority_levels"]["L2"].__setitem__("may_answer_trust_gates", True)), "unclassified (exit 2) unless a rule classifies it")
ucase("U02", "ROLES.authority_levels.L6: {name: super-orchestrator, mutation: all} (new authority level under the same wildcard)",
      lambda k: mut(k, "roles/ROLES.yaml", lambda d: d["authority_levels"].__setitem__("L6", {"name": "super-orchestrator", "mutation": "all"})), "unclassified (exit 2) unless a rule classifies it")
ucase("U03", "MEMORY_POLICY.namespaces.customers: {sensitivity: public, roles: [all], export: allowed, embed: true} (new namespace)",
      lambda k: mut(k, "policies/MEMORY_POLICY.yaml", lambda d: d["namespaces"].__setitem__("customers", {"sensitivity": "public", "roles": ["all"], "export": "allowed", "embed": True})), "exit 2")
ucase("U04", "KERNEL.trust_bypass: true (new key in KERNEL.yaml)", lambda k: mut(k, "KERNEL.yaml", lambda d: d.__setitem__("trust_bypass", True)), "exit 2")
ucase("U05", "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].flags: 'x' (new field of a registered member)",
      lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: [p.__setitem__("flags", "x") for p in d["secret_content_patterns"] if p["id"] == "aws-access-key"]), "exit 2")
ucase("U06", "new member of the additive secret_content_patterns collection {id: never-matches, regex: 'a^'}",
      lambda k: mut(k, "policies/SECURITY_POLICY.yaml", lambda d: d["secret_content_patterns"].append({"id": "never-matches", "regex": "a^"})), "exit 0 (additive; adds a pattern)")
ucase("U07", "new constitutional file contracts/CAPABILITY_ACCEPTANCE_CONTRACT.md", lambda k: (os.makedirs(os.path.join(k, "contracts")), open(os.path.join(k, "contracts/CAPABILITY_ACCEPTANCE_CONTRACT.md"), "w").write("# contract\n")), "exit 2")
ucase("U08", "new constitutional file constitution/AMENDMENTS.yaml", lambda k: open(os.path.join(k, "constitution/AMENDMENTS.yaml"), "w").write("amendments: [{id: A1, text: agents may self-approve}]\n"), "exit 2")


def rm_file(k, rel):
    dst = os.path.join(S, "removed", os.path.basename(k) + "__" + rel.replace("/", "__"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(os.path.join(k, rel), dst)


ucase("U09", "optional file tools/registry/TOOLS.yaml removed", lambda k: rm_file(k, "tools/registry/TOOLS.yaml"), "no problem added (declared optional: absence offers no kernel tools)", src=os.path.join(REL, "kernel"))
ucase("U10", "optional pinned file tools/mcp/registry.yaml removed", lambda k: rm_file(k, "tools/mcp/registry.yaml"), "no problem added (declared optional)", src=os.path.join(REL, "kernel"))
out["U_unknown_keys_and_files"] = {"cases": U, "runtime_readers_of_ROLES_authority_levels_map": [h for h in runtime_readers("authority_levels") if "authority_levels_required" not in open(os.path.join(REPO, h.split(":")[0])).read().splitlines()[int(h.split(":")[1]) - 1]],
                                   "runtime_readers_of_kernel_TOOLS_yaml": runtime_readers("\"TOOLS.yaml\""), "runtime_readers_of_mcp_registry": runtime_readers("\"registry.yaml\"")}

# ================================================================================================ part T
TUNABLE_CHANGES = {
    ("policies/MEMORY_POLICY.yaml", "namespaces.governance.embed"): True,
    ("policies/MEMORY_POLICY.yaml", "namespaces.spec.embed"): True,
    ("policies/MEMORY_POLICY.yaml", "namespaces.product.embed"): True,
    ("policies/MEMORY_POLICY.yaml", "namespaces.archive.embed"): True,
    ("policies/MEMORY_POLICY.yaml", "namespaces.archive.default_retrieval"): True,
    ("policies/MEMORY_POLICY.yaml", "namespaces.archive.retention"): "none",
    ("policies/MEMORY_POLICY.yaml", "retrieval.default_k"): 200,
    ("policies/ARCHIVE_POLICY.yaml", "archive_root"): "product/customers",
    ("policies/ARCHIVE_POLICY.yaml", "unused_code_action"): "delete",
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R0"): 0,
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R1"): 0,
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R2"): 0,
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R3"): 0,
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R4"): 0,
    ("policies/CHANGE_POLICY.yaml", "semantic_candidates_by_radius.R5"): 0,
    ("policies/CONTEXT_POLICY.yaml", "retrieved_fields"): [],
    ("policies/CONTEXT_POLICY.yaml", "packet_blocks"): [],
    ("policies/CONTEXT_POLICY.yaml", "max_retrieved_slices"): 1000,
    ("policies/HUMAN_GATE_POLICY.yaml", "batch_low_priority"): True,
    ("policies/TOOL_POLICY.yaml", "plugins.timeout_seconds"): 1,
    ("policies/TEST_POLICY.yaml", "product_families"): [],
}


def set_dotted(d, dotted, v):
    cur = d
    parts = dotted.split(".")
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = v


def apply_tunables(kdir):
    classes = {}
    for (rel, dotted), v in TUNABLE_CHANGES.items():
        mut(kdir, rel, lambda d, dotted=dotted, v=v: set_dotted(d, dotted, v))
        fr = L.match_file_rule(INV, rel)
        lr = L.match_leaf_rule(fr, fr["name"] + "." + dotted)
        classes[f"{fr['name']}.{dotted}"] = lr.get("class") if isinstance(lr, dict) else str(lr)
    return classes


kt = kcopy("T-tunable-only")
classes = apply_tunables(kt)
partT = {"changed_leaves_and_their_registered_class": classes, "all_changed_leaves_project_tunable": all(c == "project_tunable" for c in classes.values()),
         "checker": check(kt), "runtime_readers": {k: runtime_readers(k.split(".")[-1])[:6] for k in ("retrieved_fields", "packet_blocks", "semantic_candidates_by_radius", "batch_low_priority", "archive_root", "unused_code_action", "product_families", "timeout_seconds")}}


def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv4b-surface", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")
OVERRIDES = {"AUTHORITY_POLICY.authority_levels_required.resume_control": "L5", "SECURITY_POLICY.never_index_classes": ["secret", "restricted", "confidential"],
             "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "R0"}
CLASSIFICATIONS = [{"pattern": "product/customers/**", "class": "confidential", "reason": "customer data (project-owned classification)"}]


def rel_copy(name, kernel_mutator):
    d = os.path.join(S, "src", name)
    shutil.copytree(REL, d)
    kernel_mutator(os.path.join(d, "kernel"))
    return d


def db_paths(root, suffix):
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        ind = [x[0] for x in con.execute("select path from artifacts") if x[0].endswith(suffix)]
        try:
            exc = [list(x) for x in con.execute("select path, reason from excluded") if x[0].endswith(suffix)]
        except sqlite3.Error:
            exc = "no excluded table"
        return ind, exc
    except sqlite3.Error as e:
        return [], f"db error {e}"


def consume(label, src, extra_files, queries):
    root = f"{S}/consumer-{label}"
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "rv4bsurf", "--skip-index")
    pp = os.path.join(root, "governance", "project", "PROJECT_POLICY.yaml")
    pdoc = yaml.safe_load(open(pp))
    pdoc["policy_overrides"] = dict(OVERRIDES)
    ydump(pp, pdoc)
    dp = os.path.join(root, "governance", "project", "DATA_SENSITIVITY.yaml")
    ddoc = yaml.safe_load(open(dp))
    ddoc["classifications"] = list(CLASSIFICATIONS)
    ydump(dp, ddoc)
    for rel, text in extra_files.items():
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        open(os.path.join(root, rel), "w").write(text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    pause = gov(root, "orchestrator", "pause", "--reason", "rv4b")
    resume = gov(root, "orchestrator", "resume")
    if not resume.get("ok"):
        gov(root, "human", "resume")
    rb = gov(root, "orchestrator", "rebuild-memory")
    res = {"init_ok": init.get("ok"), "init_code": code(init), "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
           "a_orchestrator_L4_resume_under_project_L5_raise": {"ok": resume.get("ok"), "code": code(resume), "pause_ok": pause.get("ok")},
           "rebuild_ok": rb.get("ok"), "rebuild_code": code(rb), "files": {}}
    for rel, marker in queries.items():
        ind, exc = db_paths(root, rel)
        q = gov(root, "orchestrator", "memory", "query", marker)
        hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith(rel)]
        res["files"][rel] = {"indexed": ind, "excluded": exc, "retrievable_by_default_query": hits}
    g = gov(root, "orchestrator", "gate", "create", "--question", "Pick the low-risk option?", "--fields",
            json.dumps({"impact_radius": "R1", "confidence": 0.85, "reversibility": "reversible", "options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}]}))
    gid = (g.get("result") or {}).get("id")
    gov(root, "change-controller", "gate", "present", gid or "?")
    dec = gov(root, "change-controller", "decide", gid or "?", "--option", "A", "--by", "change-controller")
    res["c_L3_agent_answers_R1_gate_under_project_R0"] = {"ok": dec.get("ok"), "code": code(dec)}
    return res


FILES_T = {"product/customers/acme.md": "# ACME account notes RV4BCUSTOMERMARK\n\nRenewal terms for ACME.\n",
           "archive/old/legacy-plan.md": "# Old plan RV4BARCHIVEMARK\n\nSuperseded material.\n"}
QUERIES_T = {"customers/acme.md": "RV4BCUSTOMERMARK", "old/legacy-plan.md": "RV4BARCHIVEMARK"}
gen = consume("T-genuine", REL, FILES_T, QUERIES_T)
tun = consume("T-tunable-only", rel_copy("T-tunable-only", apply_tunables), FILES_T, QUERIES_T)
partT["consumption_4_1_5"] = {"genuine": gen, "tunable_only": tun}
partT["verdicts"] = {
    "checker_passes_tunable_only_kernel": partT["checker"]["exit"] == 0,
    "authority_outcome_equal": gen["a_orchestrator_L4_resume_under_project_L5_raise"]["code"] == tun["a_orchestrator_L4_resume_under_project_L5_raise"]["code"],
    "confidential_indexing_outcome_equal": bool(gen["files"]["customers/acme.md"]["indexed"]) == bool(tun["files"]["customers/acme.md"]["indexed"]) and bool(gen["files"]["customers/acme.md"]["retrievable_by_default_query"]) == bool(tun["files"]["customers/acme.md"]["retrievable_by_default_query"]),
    "archive_default_retrieval_outcome_equal": bool(gen["files"]["old/legacy-plan.md"]["retrievable_by_default_query"]) == bool(tun["files"]["old/legacy-plan.md"]["retrievable_by_default_query"]),
    "gate_outcome_equal": gen["c_L3_agent_answers_R1_gate_under_project_R0"]["code"] == tun["c_L3_agent_answers_R1_gate_under_project_R0"]["code"],
}
out["T_tunable_only_kernel"] = partT

# ================================================================================================ part P
KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"
OLD_RE = "AKIA[0-9A-Z]{16}"
NEW_RE = "(AKIA|ASIA)[0-9A-Z]{16}"
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}


def inv_with(digests_for_key, add_member=False):
    inv = copy.deepcopy(INV)
    fr = next(f for f in inv["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
    for lr in fr["leaves"]:
        if lr["key"] == KEY:
            lr["digests"] = {KEY: list(digests_for_key)}
        if add_member and lr["key"] == "SECURITY_POLICY.secret_content_patterns[id]#members":
            lr["registered"] = sorted(set(lr["registered"]) | {NEW_MEMBER["id"]})
    if add_member:
        nk = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"
        fr["leaves"].append({"key": nk, "class": "pinned", "note": "registered member content (probe TPS v2)", "digests": {nk: [L.vdigest(NEW_MEMBER["regex"])]}})
    return inv


d_old, d_new = L.vdigest(OLD_RE), L.vdigest(NEW_RE)
INV_V1 = INV
INV_V2_RETAIN = inv_with([d_old, d_new], add_member=True)   # TPS v2 registers the fix and keeps 4.1.6's digest for installed 4.1.6 releases
INV_V2_ONLY_NEW = inv_with([d_new], add_member=True)        # TPS v2 that drops the superseded digest


def set_patterns(kdir, aws_re, with_member):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == NEW_MEMBER["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(NEW_MEMBER))
    mut(kdir, "policies/SECURITY_POLICY.yaml", f)


def set_version(kdir, v):
    mut(kdir, "KERNEL.yaml", lambda d: d.__setitem__("version", v))


k_fixed = kcopy("P-4.1.7-fixed")
set_patterns(k_fixed, NEW_RE, True)
k_mix = kcopy("P-4.1.7-mixed-old-regex")
set_patterns(k_mix, OLD_RE, True)
fr_sec = next(f for f in INV["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
lr_key = next(l for l in fr_sec["leaves"] if l["key"] == KEY)
partP = {
    "pinned_leaf": KEY, "old_regex": OLD_RE, "fixed_regex": NEW_RE, "digest_old": d_old, "digest_fixed": d_new,
    "draft_v1_registered_digests": lr_key["digests"][KEY],
    "checker": {
        "fixed_kernel_under_v1": check(k_fixed, INV_V1)["exit"],
        "fixed_kernel_under_v2_retaining_old": check(k_fixed, INV_V2_RETAIN)["exit"],
        "mixed_kernel_old_regex_plus_new_member_under_v2_retaining_old": check(k_mix, INV_V2_RETAIN),
        "mixed_kernel_under_v2_only_new": check(k_mix, INV_V2_ONLY_NEW)["exit"],
    },
    "reductions": {
        "v1_to_v2_retaining_old": C.run_reductions(INV_V1, INV_V2_RETAIN, [], quiet=True)["exit"],
        "v2_only_new_to_v2_retaining_old (re-adding a superseded digest)": {k: v for k, v in C.run_reductions(INV_V2_ONLY_NEW, INV_V2_RETAIN, [], quiet=True).items() if k in ("exit", "reductions")},
    },
    "strength_direction_of_pinned_leaf": L.leaf_direction(lr_key),
    "note": "a pinned leaf has no strength direction, so neither the project-strength vector (26 §6) nor computed weakening (19 §9) can report the swap; E10 does not apply to a higher release sequence",
}
SECRET = "ASIAQ3EGUH7X4MPLE2Z9"
FILES_P = {"product/notes/deploy.md": f"# Deploy notes RV4BSECRETMARK\n\naws key used by the job: {SECRET}\n"}
QUERIES_P = {"notes/deploy.md": "RV4BSECRETMARK"}
genP = consume("P-fixed", rel_copy("P-fixed", lambda k: set_patterns(k, NEW_RE, True)), FILES_P, QUERIES_P)
mixP = consume("P-mixed", rel_copy("P-mixed", lambda k: set_patterns(k, OLD_RE, True)), FILES_P, QUERIES_P)
partP["consumption_4_1_5"] = {"fixed_regex_release": genP, "mixed_release_old_regex": mixP}
fx, mx = genP["files"]["notes/deploy.md"], mixP["files"]["notes/deploy.md"]
partP["verdicts"] = {
    "checker_accepts_mixed_kernel_when_v2_retains_old_digest": partP["checker"]["mixed_kernel_old_regex_plus_new_member_under_v2_retaining_old"]["exit"] == 0,
    "reductions_silent_on_retained_or_readded_digest": partP["reductions"]["v1_to_v2_retaining_old"] == 0 and partP["reductions"]["v2_only_new_to_v2_retaining_old (re-adding a superseded digest)"]["exit"] == 0,
    "fixed_release_keeps_secret_out_of_index": not fx["indexed"],
    "mixed_release_indexes_secret": bool(mx["indexed"]),
    "mixed_release_secret_retrievable": bool(mx["retrievable_by_default_query"]),
    "strength_vector_has_no_requirement_for_pinned_leaf": partP["strength_direction_of_pinned_leaf"] == "none",
}
out["P_pinned_registered_digest_mix"] = partP

txt = json.dumps(out, indent=1, default=str)
txt = txt.replace(S, "<scratch>").replace(REPO, "<worktree>").replace(os.path.dirname(GOV), "<legacy-bin>")
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt)
print(txt)
