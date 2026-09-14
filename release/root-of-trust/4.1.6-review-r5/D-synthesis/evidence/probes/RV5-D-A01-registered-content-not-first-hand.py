#!/usr/bin/env python3
"""RV5-D-A01 — constitutional content registered without first-hand establishment (review r5 synthesis D, AR-0014).

Question. Revision 5 makes the release registration the selector of every non-join constitutional unit (`23` §12, `29` §4
"Policy root eligibility ... selector: the registration of R"). Who establishes, first-hand, that the unit map and kernel
tree digest the registration signs are the content of the source the verifiers accepted?

Pack text relied on (design, cdb4e14):
  * `30` R-REG-3 (d): verification records "each ACCEPTED for exactly this `source` and `inputs_manifest_digest`" (no
    candidate binding); (e) `content_digest` recomputed by each custodian; no rule derives the unit map or kernel tree
    digest from the fetched source.
  * `23` §12.5: "`gov release build`, canonical CI: `csi_check.py derive-registration` produces the unit map"; the ceremony
    "lists every unit that differs from the previous registration".
  * `04` V8: a final's candidate verifies under `release-candidate`; kernel tree digest and source equal in final and
    candidate.
  * `19` E7 / `23` §12.3: registration referenced by the effective TSS, names R's final, units and kernel tree digest equal.
    No verification-record condition, no candidate binding.

Attack. Honest verifiers accept genuine candidate C (kernel K_fix, source S). The attacker holds the `release-candidate`
and `release-final` keys (one everyday key under OP-4 "no") and the release pipeline. It signs candidate C' and final F'
with kernel K_weak and the same source S, and hands F', C' and the CI-derived unit map to the registration ceremony.
Honest custodians run R-REG-3 as written; the honest publisher references the first-hand registration.

Parts.
  A (computed): the architect's P4r5 functions, loaded unmodified: E7 as written, V8 as written, the ceremony checks as
    written; E7 with a source-bound verification restrictor (reviewer B's H3 correction as worded) and with a
    candidate-bound restrictor plus final/candidate/registration consistency (P4r5 `accept_binary` semantics).
  B (executed): the pack checker (unmodified) in registration mode on real kernels, and the real legacy 4.1.5 binary as
    consumer. The CI-derived registration of K_weak is eligible; a registration derived first-hand from the fetched source
    (K_fix) refuses K_weak; on 4.1.5 the `ASIA…` key file is indexed and served under K_weak only.

Attribution. Part B's `INV2`, `kcopy`, `ymut`, `set_patterns`, `check`, `reductions`, `gov`, `git`, `rel_copy`, `db_paths`
and `consume` follow review r5 reviewer B `RV5-B-A09-floor-class-kernels.py`, which follows the architect's REG5 and review
r4 reviewer B part P. Part A uses the P4r5/P4r4 constructors unmodified.

Environment: REVIEW_REPO (export of cdb4e14), GOV (legacy 4.1.5), SCRATCH. GOV_* stripped from children; HOME and
GOV_KERNEL_CACHE in scratch. Output: JSON on stdout.
"""
import copy, importlib.util, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
GOV = os.environ["GOV"]
EV = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5")
_spec = importlib.util.spec_from_file_location("p4r5_oracle", os.path.join(EV, "P4r5-conformance-oracle.py"))
P5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P5)
m = P5.m
NOW, HOUR = P5.NOW, P5.HOUR

out = {"probe": "RV5-D-A01 registered constitutional content not established first-hand (AR-0014)"}

# ====================================================================================== Part A (computed, P4r5 functions)
C12 = m.release("C12", 0, stage="candidate", kernel_tree="K12-fixed")                       # genuine candidate
A12 = m.attest("a12", "C12")                                                                # honest verifier, ACCEPTED, source GOOD
C12x = m.release("C12x", 0, stage="candidate", kernel_tree="K12-weak")                     # attacker candidate (stolen rc1), same source
F12x = m.release("F12x", 12, promoted_from="C12x", kernel_tree="K12-weak", refs=(11, 2, 1))  # attacker final (stolen rf1)
G12x = P5.rrs("g12x", "4.1.12", 12, "F12x", "C12x", vrecs=("a12",), units={"leaf:aws": "d-weak"})  # honest custodians g1, g2
T12 = m.tss(12, "t12", prior=P5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g12x"], issued_at=NOW - HOUR)  # honest publisher
REL12x = {"kind": "release-final", "d": "F12x", "release_id": "4.1.12", "seq": 12, "stage": "final", "units": {"leaf:aws": "d-weak"},
          "refs": {"state": 11, "policy": 2, "root": 1}}
AN12 = P5.anchored(12, "t12")
W = P5.W11 + [C12, A12, C12x, F12x, G12x, T12]


def ceremony_as_written(reg, K, fetched_source):
    """`30` R-REG-3 (d), (e) as written; (a)–(c) assumed honest (genuine inputs)."""
    recs = [a for a in K if a["kind"] == "att" and a["d"] in reg["vrecs"]]
    d_ok = bool(recs) and all(a["verdict"] == "ACCEPTED" and a["source"] == reg["source"] for a in recs)
    no_rejected = not any(a["kind"] == "att" and a["verdict"] == "REJECTED" and a["source"] == reg["source"] for a in K)
    e_ok = tuple(fetched_source) == tuple(reg["source"])
    return {"R-REG-3(d)_records_accepted_for_source_and_inputs": d_ok, "R-REG-3(d)_no_rejected": no_rejected, "R-REG-3(e)_content_digest": e_ok,
            "rule_requiring_unit_map_from_fetched_source": None, "signs": d_ok and no_rejected and e_ok}


def v8_as_written(final, K, rootS):
    cand = next((s for s in K if s["kind"] == "release-candidate" and s["d"] == final["promoted_from"]), None)
    if cand is None:
        return {"holds": False, "why": "candidate not held"}
    return {"candidate_verifies_under_release_candidate": m.verifies(cand, rootS), "final_verifies_under_release_final": m.verifies(final, rootS),
            "kernel_tree_equal": cand["tree"] == final["tree"], "source_equal": cand["source"] == final["source"],
            "holds": m.verifies(cand, rootS) and m.verifies(final, rootS) and cand["tree"] == final["tree"] and cand["source"] == final["source"]}


def e7_with_restrictor(Rl, K_all, machine, mode):
    base = P5.eligible_release_r5(Rl, K_all, machine, NOW)
    if not base["eligible"]:
        return base
    K, ts, fr, info = m.evaluate_machine(K_all, machine, NOW, "a")
    rootS = m.eff_root_stmt(K)
    Rg = next(r for r in K if r["kind"] == "rrs" and r["release_id"] == Rl["release_id"])
    F = next(s for s in K if s["kind"] == "release-final" and s["d"] == Rg["final"])
    if mode == "source_bound":      # reviewer B CR5-B H3 correction as worded: ACCEPTED, listed, for its source
        atts = [a for a in K if a["kind"] == "att" and a["d"] in Rg["vrecs"] and a["verdict"] == "ACCEPTED" and a["source"] == Rg["source"]]
    elif mode == "candidate_bound":  # P4r5 accept_binary semantics, plus final/registration candidate consistency
        if F["promoted_from"] != Rg["candidate"]:
            return {"eligible": False, "reason": "final_not_promoted_from_registered_candidate"}
        atts = [a for a in K if a["kind"] == "att" and a["candidate"] == Rg["candidate"] and a["d"] in Rg["vrecs"] and a["verdict"] == "ACCEPTED" and a["source"] == Rg["source"]]
    keys = {k for a in atts for k in m.valid_signers(a, rootS)}
    if len(keys) < P5.P5["min_verification_records"]:
        return {"eligible": False, "reason": "verification_records_below_minimum"}
    return {"eligible": True, "reason": None}


rootS = m.eff_root_stmt(W)
partA = {
    "world": "W11 (P4r5) + genuine candidate C12 with ACCEPTED attestation a12; attacker candidate C12x and final F12x (same source, weakened kernel) signed by rc1/rf1; registration g12x by honest custodians g1+g2 naming F12x/C12x and a12; t12 by the honest publisher; human anchor at t12 today",
    "ceremony_R-REG-3_as_written": ceremony_as_written(G12x, W, P5.GOOD),
    "V8_as_written": v8_as_written(F12x, W, rootS),
    "E7_as_written": P5.eligible_release_r5(REL12x, W, AN12, NOW),
    "E7_with_source_bound_verification_restrictor": e7_with_restrictor(REL12x, W, AN12, "source_bound"),
    "E7_with_candidate_bound_restrictor_and_consistency": e7_with_restrictor(REL12x, W, AN12, "candidate_bound"),
}
# Variant: the ceremony names the attested candidate C12 (a careful tool), the final still promotes from C12x.
G12y = P5.rrs("g12x", "4.1.12", 12, "F12x", "C12", vrecs=("a12",), units={"leaf:aws": "d-weak"})
Wy = P5.W11 + [C12, A12, C12x, F12x, G12y, T12]
partA["variant_registration_names_attested_candidate"] = {
    "E7_as_written": P5.eligible_release_r5(REL12x, Wy, AN12, NOW),
    "E7_with_source_bound_verification_restrictor": e7_with_restrictor(REL12x, Wy, AN12, "source_bound"),
    "E7_with_candidate_bound_restrictor_and_consistency": e7_with_restrictor(REL12x, Wy, AN12, "candidate_bound"),
}
# OP-4 "no": one everyday key holds release-final and release-candidate (whitelisted pair).
ROOT_OP4NO = P5.root5(extra={"kc": ["release-final", "release-candidate"]})
C12k = dict(C12x, signers=["kc"])
F12k = dict(F12x, signers=["kc"])
Wk = [ROOT_OP4NO] + P5.W11[1:] + [C12, A12, C12k, F12k, G12x, T12]
partA["op4_no_one_everyday_key"] = {
    "ftc_violations_of_root": P5.ftc_violations(ROOT_OP4NO),
    "V8_as_written": v8_as_written(F12k, Wk, m.eff_root_stmt(Wk)),
    "E7_as_written": P5.eligible_release_r5(REL12x, Wk, AN12, NOW),
}
# Control: the genuine release (units as derived from the verified source) is eligible; the weakened kernel under the
# first-hand registration is not.
G12g = P5.rrs("g12x", "4.1.12", 12, "F12x", "C12x", vrecs=("a12",), units={"leaf:aws": "d-fixed"})
Wg = P5.W11 + [C12, A12, C12x, F12x, G12g, T12]
partA["control_registration_derived_first_hand_from_source"] = P5.eligible_release_r5(REL12x, Wg, AN12, NOW)

# ====================================================================================== Part B (executed, checker + 4.1.5)
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as Cc  # noqa: E402

FW = os.path.join(REPO, "framework")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="rv5d-a01-", dir=os.environ["SCRATCH"])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = os.path.join(S, "cache")
ENV["HOME"] = os.path.join(S, "home")
os.makedirs(ENV["HOME"], exist_ok=True)

OLD_RE = "AKIA[0-9A-Z]{16}"
FIX_RE = "(AKIA|ASIA)[0-9A-Z]{16}"
FIX2_RE = "(AKIA|ASIA|ABIA)[0-9A-Z]{16}"      # the genuine 4.1.8 change to the same unit
WEAK_RE = "(?:AKIA|ABIA)[0-9A-Z]{16}"         # the attacker's 4.1.8 value: drops ASIA; not a reversion of any registered value
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
NEW_MEMBER_KEY = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"
KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"


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


INV2 = copy.deepcopy(INV)
fr_sec = next(f for f in INV2["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
if not any(l["key"] == NEW_MEMBER_KEY for l in fr_sec["leaves"]):
    fr_sec["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "note": "member introduced in 4.1.7 (TPS v2 classification)", "digests": {NEW_MEMBER_KEY: [L.vdigest(NEW_MEMBER["regex"])]}})


def check(kdir, regs, release_id, inv=INV2):
    r = Cc.run_check(kdir, inv, quiet=True, registrations=regs, release_id=release_id)
    return {"exit": r["exit"], "violations": [str(v)[:200] for v in (r.get("violations") or [])[:3]], "malformed": [str(x)[:200] for x in (r.get("malformed") or [])[:2]]}


def reductions(regs, inv=INV2):
    r = Cc.run_registration_reductions(regs, quiet=True, inv=inv)
    return {"exit": r["exit"], "reductions": [{k: v for k, v in x.items() if k in ("subject", "kind")} for x in r.get("reductions", [])], "undeclared": len(r.get("undeclared", []))}


K416 = kcopy("4.1.6"); set_patterns(K416, OLD_RE, with_member=False)
K417 = kcopy("4.1.7"); set_patterns(K417, FIX_RE)
K418g = kcopy("4.1.8-genuine-source"); set_patterns(K418g, FIX2_RE)     # kernel of the source the verifiers accepted
K418x = kcopy("4.1.8-attacker-final"); set_patterns(K418x, WEAK_RE)     # kernel of the attacker's candidate and final
REG416 = L.registration_record(INV2, K416, "4.1.6", 1600, "sha256:final-4.1.6")
REG417 = L.registration_record(INV2, K417, "4.1.7", 1700, "sha256:final-4.1.7")
REG418_ci = L.registration_record(INV2, K418x, "4.1.8", 1800, "sha256:final-4.1.8x")          # unit map derived by CI from the final handed over
REG418_firsthand = L.registration_record(INV2, K418g, "4.1.8", 1800, "sha256:final-4.1.8x")   # correction: derived from the fetched source's kernel


def changed(a, b):
    return sorted(u for u in set(a["units"]) | set(b["units"]) if a["units"].get(u) != b["units"].get(u))


partB = {
    "ceremony_diff_list_genuine_4.1.8_vs_4.1.7": changed(REG417, L.registration_record(INV2, K418g, "4.1.8", 1800, "sha256:final-4.1.8")),
    "ceremony_diff_list_attacker_4.1.8_vs_4.1.7": changed(REG417, REG418_ci),
    "registration_reductions_attacker_set": reductions([REG416, REG417, REG418_ci]),
    "E7_attacker_kernel_under_CI_derived_registration": check(K418x, [REG416, REG417, REG418_ci], "4.1.8"),
    "E7_attacker_kernel_under_first_hand_registration": check(K418x, [REG416, REG417, REG418_firsthand], "4.1.8"),
    "E7_genuine_kernel_under_first_hand_registration": check(K418g, [REG416, REG417, REG418_firsthand], "4.1.8"),
}


def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv5d", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True,
                   env={"PATH": "/usr/bin:/bin", "HOME": ENV["HOME"], "GIT_CONFIG_NOSYSTEM": "1"})


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
MARK = "RV5DSECRETMARK"


def consume(label, src):
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "rv5d", "--skip-index")
    os.makedirs(os.path.join(root, "product", "notes"), exist_ok=True)
    open(os.path.join(root, "product", "notes", "deploy.md"), "w").write(f"# Deploy notes {MARK}\n\naws key used by the job: {SECRET}\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    rb = gov(root, "orchestrator", "rebuild-memory")
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("notes/deploy.md")]
    return {"init_ok": init.get("ok"), "rebuild_ok": rb.get("ok"), "ASIA_file_indexed": db_paths(root, "notes/deploy.md"), "ASIA_file_retrievable": hits}


partB["binary"] = subprocess.run([GOV, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()
partB["consumption_4_1_5"] = {
    "genuine_4.1.8_kernel": consume("418-genuine", rel_copy("418g", lambda k: set_patterns(k, FIX2_RE))),
    "attacker_4.1.8_kernel": consume("418-attacker", rel_copy("418x", lambda k: set_patterns(k, WEAK_RE))),
}

out["partA_computed"] = partA
out["partB_executed"] = partB
cons = partB["consumption_4_1_5"]
out["verdicts"] = {
    "A_ceremony_as_written_signs": partA["ceremony_R-REG-3_as_written"]["signs"],
    "A_V8_as_written_holds": partA["V8_as_written"]["holds"],
    "A_E7_as_written_eligible": partA["E7_as_written"]["eligible"],
    "A_E7_source_bound_restrictor_still_eligible": partA["E7_with_source_bound_verification_restrictor"]["eligible"],
    "A_E7_candidate_bound_restrictor_refuses": not partA["E7_with_candidate_bound_restrictor_and_consistency"]["eligible"],
    "A_variant_E7_as_written_eligible": partA["variant_registration_names_attested_candidate"]["E7_as_written"]["eligible"],
    "A_variant_candidate_bound_refuses": not partA["variant_registration_names_attested_candidate"]["E7_with_candidate_bound_restrictor_and_consistency"]["eligible"],
    "A_op4_no_one_key_root_valid_and_eligible": partA["op4_no_one_everyday_key"]["ftc_violations_of_root"] == [] and partA["op4_no_one_everyday_key"]["E7_as_written"]["eligible"],
    "B_attacker_diff_list_names_only_units_the_genuine_release_also_changes_plus_none_distinguishable": partB["ceremony_diff_list_attacker_4.1.8_vs_4.1.7"] == partB["ceremony_diff_list_genuine_4.1.8_vs_4.1.7"],
    "B_no_reduction_reported_for_attacker_set": partB["registration_reductions_attacker_set"]["exit"] == 0 and not partB["registration_reductions_attacker_set"]["reductions"],
    "B_E7_attacker_kernel_eligible_under_CI_registration": partB["E7_attacker_kernel_under_CI_derived_registration"]["exit"] == 0,
    "B_E7_attacker_kernel_refused_under_first_hand_registration": partB["E7_attacker_kernel_under_first_hand_registration"]["exit"] != 0,
    "B_E7_genuine_kernel_eligible_under_first_hand_registration": partB["E7_genuine_kernel_under_first_hand_registration"]["exit"] == 0,
    "B_4.1.5_genuine_kernel_excludes_ASIA_file": not cons["genuine_4.1.8_kernel"]["ASIA_file_indexed"],
    "B_4.1.5_attacker_kernel_indexes_ASIA_file": bool(cons["attacker_4.1.8_kernel"]["ASIA_file_indexed"]),
    "B_4.1.5_attacker_kernel_serves_ASIA_file": bool(cons["attacker_4.1.8_kernel"]["ASIA_file_retrievable"]),
}
txt = json.dumps(out, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
txt = txt.replace(S, "<scratch>").replace(REPO, "<repo>").replace(os.path.dirname(GOV), "<legacy-bin>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
