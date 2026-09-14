#!/usr/bin/env python3
"""CON6 — registered constitutional content established first-hand, bound to the registered candidate (BC5-3), against the
revision-6 rules (AR-0015). RV5-D-A01 parts A and B, RV5-D-A05 N3/N4, RV5-B-A06, RV5-B-A09 and RV5-B-A10 re-run.

Parts
  A (computed)  the revision-6 oracle P4r6 (`P4r6-conformance-oracle.py`): the D-A01 part A rows under E7 revision 6, the OP-4
                "no" row, the variant naming the attested candidate, the ceremony's first-hand derivation, the B-A06 registration
                with no verification record, and the genuine control.
  B (executed)  the pack checker as amended in revision 6 (`constitutional-surface/csi_check.py`, `csi_lib.py`) on real kernels:
                R-CON-1 `verify-registration` (the custodian derives the registration from the kernel payload of the fetched
                source), E7 in registration mode, `registration-changes` (CR5-B-04 (b)), `registration-reductions --verifier`
                (CR5-B-04 (a)); and the real legacy 4.1.5 binary as the consumer of the content a refusal keeps out.
  N             D-A05 N3 and N4 (a Capability Acceptance Contract YAML weakened in the final handed to the ceremony).

Attribution. Part B's kernel helpers, `set_patterns`, `consume`, `rel_copy` and `db_paths` follow review r5 synthesis D's
`RV5-D-A01-registered-content-not-first-hand.py` (which follows reviewer B's `RV5-B-A09-floor-class-kernels.py`, REG5 and
review r4 B part P); the contract fixtures follow `RV5-D-A05-forward-compat-new-constitutional-file.py`; the tool-command change
follows `RV5-B-A09`. Code re-typed; the rules applied are revision 6.

Environment: REVIEW_REPO (an export holding the revision-6 pack), GOV (legacy 4.1.5), SCRATCH, P4R6_JSON (P4r6 output). GOV_*
stripped from children; HOME and GOV_KERNEL_CACHE in scratch. Output: JSON on stdout.
"""
import copy, hashlib, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
GOV = os.environ["GOV"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as Cc  # noqa: E402

FW = os.path.join(REPO, "framework")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="con6-", dir=os.environ["SCRATCH"])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = os.path.join(S, "cache")
ENV["HOME"] = os.path.join(S, "home")
os.makedirs(ENV["HOME"], exist_ok=True)
out = {"probe": "CON6 first-hand constitutional content (AR-0015)"}

# ====================================================================================== Part A (computed, P4r6)
p4 = json.load(open(os.environ["P4R6_JSON"]))
rows = {k: {"computed": v["computed"], "holds": v["holds"], "claim": v["claim"]} for k, v in p4["scenarios"].items() if k.startswith(("R6-E7", "R6-CER"))}
out["partA_computed_P4r6"] = rows

# ====================================================================================== Part B (executed, checker + 4.1.5)
OLD_RE, FIX_RE, FIX2_RE = "AKIA[0-9A-Z]{16}", "(AKIA|ASIA)[0-9A-Z]{16}", "(AKIA|ASIA|ABIA)[0-9A-Z]{16}"
WEAK_RE, VARIANT_RE = "(?:AKIA|ABIA)[0-9A-Z]{16}", "(?:AKIA)[0-9A-Z]{16}"
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
NEW_MEMBER_KEY = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"
TOOL_ID = "TOOL-GIT-001"


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
    Cc.ydump(p, d)


def set_patterns(kdir, aws_re, with_member=True):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == NEW_MEMBER["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(NEW_MEMBER))
    ymut(kdir, "policies/SECURITY_POLICY.yaml", f)


def set_tool_command(kdir, command):
    ymut(kdir, "tools/registry/TOOLS.yaml", lambda d: [t.__setitem__("health_check", {"kind": "command", "command": command, "expect_exit": 0}) for t in d["tools"] if t["tool_id"] == TOOL_ID])


INV2 = copy.deepcopy(INV)
fr_sec = next(f for f in INV2["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
if not any(l["key"] == NEW_MEMBER_KEY for l in fr_sec["leaves"]):
    fr_sec["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "note": "member introduced in 4.1.7 (TPS v2 classification)", "digests": {NEW_MEMBER_KEY: [L.vdigest(NEW_MEMBER["regex"])]}})


def check(kdir, regs, rid, inv=INV2):
    r = Cc.run_check(kdir, inv, quiet=True, registrations=regs, release_id=rid)
    return {"exit": r["exit"], "violations": [str(v)[:160] for v in (r.get("violations") or [])[:2]], "malformed": [str(x)[:160] for x in (r.get("malformed") or [])[:2]]}


def verify(reg, source_kernel, inv=INV2):
    r = Cc.run_verify_registration(reg, source_kernel, inv, quiet=True)
    return {"exit": r["exit"], "problems": [{k: v for k, v in p.items() if k in ("problem", "unit", "field")} for p in r["problems"][:4]], "problem_count": r["problem_count"]}


def changes(held, new, inv=INV2):
    r = Cc.run_registration_changes(held, new, inv=inv, quiet=True)
    return {"exit": r["exit"], "security_classified_changes": [c["unit"] for c in r["security_classified_changes"]][:6], "changes": len(r["changes"])}


def vreductions(referenced, held, inv=INV2):
    r = Cc.run_registration_reductions_verifier(referenced, held, quiet=True, inv=inv)
    return {"exit": r["exit"], "result": r.get("result"), "missing": r.get("missing"), "reductions": [x.get("kind") for x in r.get("reductions", [])]}


K416 = kcopy("4.1.6"); set_patterns(K416, OLD_RE, with_member=False)
K417 = kcopy("4.1.7"); set_patterns(K417, FIX_RE)
K418g = kcopy("4.1.8-source"); set_patterns(K418g, FIX2_RE)            # kernel payload built from the source the verifiers accepted
K418x = kcopy("4.1.8-attacker-final"); set_patterns(K418x, WEAK_RE)    # kernel of the attacker's candidate and final
REG416 = L.registration_record(INV2, K416, "4.1.6", 1600, "sha256:final-4.1.6")
REG417 = L.registration_record(INV2, K417, "4.1.7", 1700, "sha256:final-4.1.7")
REG418_ci = L.registration_record(INV2, K418x, "4.1.8", 1800, "sha256:final-4.1.8x")
REG418_fh = L.registration_record(INV2, K418g, "4.1.8", 1800, "sha256:final-4.1.8")
partB = {
    "D-A01_B1_ceremony_R-CON-1_on_CI_derived_proposal (custodian derives from the fetched source)": verify(REG418_ci, K418g),
    "D-A01_B2_ceremony_R-CON-1_on_first_hand_proposal": verify(REG418_fh, K418g),
    "D-A01_B3_E7_attacker_kernel_under_the_only_registration_the_ceremony_signs": check(K418x, [REG416, REG417, REG418_fh], "4.1.8"),
    "D-A01_B4_E7_genuine_kernel_under_first_hand_registration": check(K418g, [REG416, REG417, REG418_fh], "4.1.8"),
    "D-A01_B5_gate_package_lists_the_genuine_4.1.8_regex_change (CR5-B-04 (b))": changes(REG417, REG418_fh),
}

# ---- B-A09: non-identical weakening registered by the registration authority itself; tool command change
K418v = kcopy("4.1.8-variant"); set_patterns(K418v, VARIANT_RE)
REG418v = L.registration_record(INV2, K418v, "4.1.8", 1800, "sha256:final-4.1.8v")
K418t = kcopy("4.1.8-tool"); set_patterns(K418t, FIX_RE); set_tool_command(K418t, ["sh", "-c", "touch $HOME/con6-tool-command-ran"])
REG418t = L.registration_record(INV2, K418t, "4.1.8", 1800, "sha256:final-4.1.8t")
K418r = kcopy("4.1.8-reversion"); set_patterns(K418r, OLD_RE)
REG418r = L.registration_record(INV2, K418r, "4.1.8", 1800, "sha256:final-4.1.8r")
partB.update({
    "B-A09_variant_regex_listed_for_recorded_projects": changes(REG417, REG418v),
    "B-A09_variant_regex_verifier_reductions (not an exact reversion; the change is listed, not computed)": vreductions(["4.1.6", "4.1.7", "4.1.8"], [REG416, REG417, REG418v]),
    "B-A09_tool_command_listed_for_recorded_projects": changes(REG417, REG418t),
    "B-A10_i_undeclared_exact_reversion_at_the_verifier": vreductions(["4.1.6", "4.1.7", "4.1.8"], [REG416, REG417, REG418r]),
    "B-A10_ii_intermediate_registration_withheld": vreductions(["4.1.6", "4.1.7", "4.1.8"], [REG416, REG418r]),
})

# ====================================================================================== N: D-A05 N3/N4 (forward-compatibility content)
MD, YML = "contracts/CAPABILITY_ACCEPTANCE_CONTRACT.md", "contracts/CAPABILITY_ACCEPTANCE_CONTRACT.yaml"
MD_TEXT = "# Capability Acceptance Contract\n\nA capability is accepted only when every acceptance criterion passes with independent evidence.\n"
YML_G = {"contract_version": 1, "source_markdown_sha256": "sha256:" + hashlib.sha256(MD_TEXT.encode()).hexdigest(), "acceptance": {"min_independent_evidence": 2, "require_all_criteria": True}}
YML_X = copy.deepcopy(YML_G)
YML_X["acceptance"] = {"min_independent_evidence": 0, "require_all_criteria": False}


def contract_kernel(name, yml):
    d = kcopy(name)
    os.makedirs(os.path.join(d, "contracts"), exist_ok=True)
    open(os.path.join(d, MD), "w").write(MD_TEXT)
    Cc.ydump(os.path.join(d, YML), yml)
    return d


Kc417, Kcg, Kcx = contract_kernel("c-4.1.7", YML_G), contract_kernel("c-4.1.8-source", YML_G), contract_kernel("c-4.1.8-attacker", YML_X)
INV3 = copy.deepcopy(INV)
for rel in (MD, YML):
    INV3["files"].append({"path": rel, "mode": "pinned_file", "digests": {rel: ["sha256:" + hashlib.sha256(open(os.path.join(Kcg, rel), "rb").read()).hexdigest()]},
                          "rationale": "owner Capability Acceptance Contract shipped in the kernel (RV5-D-A05 fixture)"})
Rc417 = L.registration_record(INV3, Kc417, "4.1.7", 1700, "sha256:final-4.1.7")
Rcg = L.registration_record(INV3, Kcg, "4.1.8", 1800, "sha256:final-4.1.8")
Rcx = L.registration_record(INV3, Kcx, "4.1.8", 1800, "sha256:final-4.1.8x")
partN = {
    "N3_ceremony_R-CON-1_on_CI_derived_contract_registration": verify(Rcx, Kcg, inv=INV3),
    "N4_E7_attacker_contract_under_first_hand_registration": check(Kcx, [Rc417, Rcg], "4.1.8", inv=INV3),
    "N2_control_genuine_contract_under_first_hand_registration": check(Kcg, [Rc417, Rcg], "4.1.8", inv=INV3),
}


# ====================================================================================== consumption on real 4.1.5
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-con6", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": ENV["HOME"], "GIT_CONFIG_NOSYSTEM": "1"})


def rel_copy(name, mutator):
    d = os.path.join(S, "src", name)
    shutil.copytree(REL, d)
    mutator(os.path.join(d, "kernel"))
    return d


def db_paths(root, suffix):
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        return [x[0] for x in con.execute("select path from artifacts") if x[0].endswith(suffix)]
    except sqlite3.Error as e:
        return f"db error {e}"


SECRET, MARK = "ASIAQ3EGUH7X4MPLE2Z9", "CON6SECRETMARK"


def consume(label, src):
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "con6", "--skip-index")
    os.makedirs(os.path.join(root, "product", "notes"), exist_ok=True)
    open(os.path.join(root, "product", "notes", "deploy.md"), "w").write(f"# Deploy notes {MARK}\n\naws key used by the job: {SECRET}\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    rb = gov(root, "orchestrator", "rebuild-memory")
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("notes/deploy.md")]
    return {"init_ok": init.get("ok"), "rebuild_ok": rb.get("ok"), "ASIA_file_indexed": db_paths(root, "notes/deploy.md"), "ASIA_file_retrievable": hits}


partB["binary"] = subprocess.run([GOV, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()
partB["consumption_4_1_5"] = {"content_revision_6_makes_effective (registered genuine 4.1.8)": consume("418-genuine", rel_copy("418g", lambda k: set_patterns(k, FIX2_RE))),
                              "content_the_ceremony_refuses (attacker 4.1.8; harm control)": consume("418-attacker", rel_copy("418x", lambda k: set_patterns(k, WEAK_RE)))}
out["partB_executed"] = partB
out["partN_executed"] = partN
cons = partB["consumption_4_1_5"]
g_ = lambda k: partB[k]
out["verdicts"] = {
    "A_E7_D-A01_attacker_release_ineligible": rows["R6-E7-D-A01_attacker_candidate_and_final_weak_kernel"]["holds"],
    "A_E7_variant_naming_attested_candidate_ineligible": rows["R6-E7-D-A01_variant_registration_names_attested_candidate"]["holds"],
    "A_E7_OP4_no_one_everyday_key_ineligible": rows["R6-E7-D-A01_op4_no_one_everyday_key"]["holds"],
    "A_B-A06_registration_without_verification_record_ineligible": rows["R6-E7-B-A06_registration_without_verification_record"]["holds"],
    "A_genuine_release_eligible": rows["R6-E7-control_genuine_release_eligible"]["holds"],
    "A_ceremony_refuses_non_first_hand_content": rows["R6-CER-D-A01_ceremony_derives_content_first_hand"]["holds"],
    "B_ceremony_refuses_CI_derived_registration": g_("D-A01_B1_ceremony_R-CON-1_on_CI_derived_proposal (custodian derives from the fetched source)")["exit"] == 3,
    "B_ceremony_signs_first_hand_registration": g_("D-A01_B2_ceremony_R-CON-1_on_first_hand_proposal")["exit"] == 0,
    "B_attacker_kernel_refused_by_E7": g_("D-A01_B3_E7_attacker_kernel_under_the_only_registration_the_ceremony_signs")["exit"] == 3,
    "B_genuine_kernel_eligible": g_("D-A01_B4_E7_genuine_kernel_under_first_hand_registration")["exit"] == 0,
    "B_A09_variant_and_tool_command_listed_for_gate": g_("B-A09_variant_regex_listed_for_recorded_projects")["exit"] == 8 and g_("B-A09_tool_command_listed_for_recorded_projects")["exit"] == 8,
    "B_A10_reversion_refused_at_verifier_and_withheld_intermediate_incomplete": g_("B-A10_i_undeclared_exact_reversion_at_the_verifier")["exit"] == 6 and g_("B-A10_ii_intermediate_registration_withheld")["exit"] == 7,
    "N3_attacker_contract_registration_refused_by_ceremony": partN["N3_ceremony_R-CON-1_on_CI_derived_contract_registration"]["exit"] == 3,
    "N4_attacker_contract_refused_by_E7": partN["N4_E7_attacker_contract_under_first_hand_registration"]["exit"] == 3,
    "N2_genuine_contract_eligible": partN["N2_control_genuine_contract_under_first_hand_registration"]["exit"] == 0,
    "consumption_genuine_excludes_ASIA_file": not cons["content_revision_6_makes_effective (registered genuine 4.1.8)"]["ASIA_file_indexed"],
    "consumption_control_refused_content_would_index_ASIA_file": bool(cons["content_the_ceremony_refuses (attacker 4.1.8; harm control)"]["ASIA_file_indexed"]),
}
txt = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(REPO, "<repo>").replace(os.path.dirname(GOV), "<legacy-bin>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
