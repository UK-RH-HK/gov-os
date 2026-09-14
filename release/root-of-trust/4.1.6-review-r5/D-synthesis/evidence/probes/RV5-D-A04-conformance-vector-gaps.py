#!/usr/bin/env python3
"""RV5-D-A04 — the two normative executors of admission-predicate/1 disagree, and neither oracle carries the case
(review r5 synthesis D, AR-0014).

`31` §3: `gov trust verify-artifact` and `gov-admit` implement admission-predicate/1 "from one normative specification and
one shared set of conformance vectors ... A difference in result on a shared vector is a release-blocking defect of both."
`12` RT-134 and RT-135 take their shapes from `P4r5-conformance-oracle.json` (running mode) and `FA5-first-admission.json`
(bootstrap mode). This probe executes AP-4 / AP-5 cases on the reference bootstrap executor `gov_admit_reference.py`
(unmodified; real Ed25519 through OpenSSL) and computes the same cases with the running-mode oracle functions of
`P4r5-conformance-oracle.py` (unmodified), then checks whether any committed vector or scenario contains them.

  R0 control: genuine B8.
  R1 AP-4 "the registered final ... not revoked": the selected TSS revokes FINAL8's digest; B8 itself is not revoked.
  R2 AP-4 "the registered ... candidate not revoked": the selected TSS revokes CAND8.
  R3 AP-5 ACCEPTED attestations bound to the registered candidate: the registration names candidate CAND8x (same source
     and inputs) and lists VA8, which the honest verifier issued for CAND8.
  R4 AP-4 "binary version ≥ min_binary_version": the Trust Policy sets `eligibility.min_binary_version` above every binary.

Attribution. Statement builders, keys, world and binaries are FA5's (`FA5-first-admission.py`), executed unmodified up to
its "CONFORMANCE VECTORS" marker; the running-mode world is P4r5's W11.

Environment: REVIEW_REPO (export of cdb4e14), SCRATCH, GOV (legacy 4.1.5, used only by FA5's PH4 scenario).
Output: JSON on stdout.
"""
import copy, importlib.util, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
EV = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5")
SCR = tempfile.mkdtemp(prefix="rv5d-a04-", dir=os.environ["SCRATCH"])
os.environ["FA5_SCRATCH"] = SCR

FA5_PATH = os.path.join(EV, "FA5-first-admission.py")
src = open(FA5_PATH).read()
cut = src.index("# ========== CONFORMANCE VECTORS ==========")
G = {"__file__": FA5_PATH, "__name__": "fa5_prefix"}
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], FA5_PATH, "exec"), G)
GA, envelope, to_stmts, fp = G["GA"], G["envelope"], G["to_stmts"], G["fp"]
V = G["V"]
TARGET, ADM = G["TARGET"], G["ADMITTER_DIGEST"]
ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9, T10 = (G[k] for k in ("ROOT1", "ROOT2", "TPS1", "T1", "T5", "T6", "T7", "T9", "T10"))
VA7, VA8, FINAL7, FINAL8, REG7, REG8 = (G[k] for k in ("VA7", "VA8", "FINAL7", "FINAL8", "REG7", "REG8"))
RP7, RP7x, RP8 = G["RP7"], G["RP7x"], G["RP8"]
B8, B8_D, LINEAGE = G["B8_BYTES"], G["B8_D"], G["LINEAGE"]
SRC8, INP8, CAND8 = G["SRC8"], G["INP8"], G["CAND8"]
canon, sha256d = G["canon"], G["sha256d"]


def admit(label, fps, stmts_list):
    r = GA.accept(B8, fps, to_stmts(stmts_list), TARGET, ADM, verifier=V, workdir=SCR)
    return {"row": label, "result": r["result"]}


def t10_with(tps=TPS1, **changes):
    p = copy.deepcopy(T10["payload"])
    p["references"]["trust_policy"] = {"version": 1, "digest": tps["digest"]}
    p.update(changes)
    t = envelope("trust-state+json", p, ["ts1"])
    return t, fp(LINEAGE, 2, ROOT2["digest"], 1, tps["digest"], 10, t["digest"])


BASE = [ROOT1, ROOT2, TPS1, T1, T5, T6, T7, T9]
rows = {}
rows["R0_control_genuine"] = dict(admit("R0", [G["FP10"], G["FP10"]], G["FULL"]), ap_expectation="ACCEPTED")

t, f = t10_with(revocations=sorted(T10["payload"]["revocations"] + [FINAL8["digest"]]))
rows["R1_registered_final_revoked"] = dict(admit("R1", [f, f], BASE + [t, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8),
                                           ap_expectation="refuse (AP-4: the registered final is not revoked)")
t, f = t10_with(revocations=sorted(T10["payload"]["revocations"] + [CAND8]))
rows["R2_registered_candidate_revoked"] = dict(admit("R2", [f, f], BASE + [t, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8),
                                               ap_expectation="refuse (AP-4: the registered candidate is not revoked)")

CAND8x = sha256d(canon({"kind": "candidate", "release_id": "R8", "source": SRC8, "variant": "attacker"}))
FINAL8x = envelope("release-final+json", {"release_id": "R8", "sequence": 8, "promoted_from": CAND8x, "source": SRC8,
                                          "kernel_tree_digest": sha256d(b"kernel-R8-weak")}, ["f1"])
REG8x = envelope("release-registration+json", {"release_id": "R8", "sequence": 8, "final_statement_digest": FINAL8x["digest"],
                                               "candidate_statement_digest": CAND8x, "source": SRC8, "inputs_manifest_digest": INP8,
                                               "targets": [TARGET], "verification_records": [VA8["digest"]], "units": {}}, ["g1", "g2"])
t, f = t10_with(registrations=[REG7["digest"], REG8x["digest"]])
rows["R3_attestation_for_another_candidate_same_source"] = dict(
    admit("R3", [f, f], BASE + [t, VA7, VA8, FINAL7, FINAL8x, REG7, REG8x] + RP7 + RP7x + RP8),
    ap_expectation="refuse under P4r5 semantics (ACCEPTED attestations for the registered candidate)")

TPSm = envelope("trust-policy+json", dict(copy.deepcopy(TPS1["payload"]), eligibility={"min_binary_version": "99.0.0"}), ["r1", "r2"])
t, f = t10_with(tps=TPSm)
rows["R4_min_binary_version_above_binary"] = dict(admit("R4", [f, f], [ROOT1, ROOT2, TPSm, T1, T5, T6, T7, T9, t, VA7, VA8, FINAL7, FINAL8, REG7, REG8] + RP7 + RP7x + RP8),
                                                  ap_expectation="refuse (AP-4: BINARY_BELOW_TRUST_POLICY)")

# ---------------------------------------------------------------------------------------------- running-mode oracle (P4r5)
_spec = importlib.util.spec_from_file_location("p4r5_oracle", os.path.join(EV, "P4r5-conformance-oracle.py"))
P5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P5)
m = P5.m
NOW = P5.NOW
AN = P5.anchored()
T11_F = P5.t11_with(revs=["R7", "F11"])
T11_C = P5.t11_with(revs=["R7", "C11"])
C11x = m.release("C11x", 0, stage="candidate")
F11x = m.release("F11", 11, promoted_from="C11x", refs=(9, 2, 1))
G11x = P5.rrs("g11", "4.1.11", 11, "F11", "C11x", vrecs=("a11",))
# Revocations are modelled as P4r5's AP-A8 row does: the TSS lists the target and a revocation statement is held.
oracle = {
    "R0_control_genuine": P5.accept_binary(P5.B11, P5.W11, AN, NOW),
    "R1_registered_final_revoked": P5.accept_binary(P5.B11, P5.world(replace={"t11": T11_F}, add=[m.revocation("rvF11", ["F11"], issued_at=NOW - P5.HOUR)]), AN, NOW),
    "R2_registered_candidate_revoked": P5.accept_binary(P5.B11, P5.world(replace={"t11": T11_C}, add=[m.revocation("rvC11", ["C11"], issued_at=NOW - P5.HOUR)]), AN, NOW),
    "R3_attestation_for_another_candidate_same_source": P5.accept_binary(P5.B11, P5.world(replace={"g11": G11x, "F11": F11x}, add=[C11x]), AN, NOW),
    "R4_min_binary_version_above_binary": "not modelled (no binary version in the P4r5 TBM or binary constructors; no min_binary_version reference in P4r5, P4r4 or gov_admit_reference)",
}

# ---------------------------------------------------------------------------------------------- coverage in committed vectors
fa5 = json.load(open(os.path.join(EV, "FA5-first-admission.json"))) if os.path.exists(os.path.join(EV, "FA5-first-admission.json")) else {}
p4r5 = json.load(open(os.path.join(EV, "P4r5-conformance-oracle.json")))
fa5_ids = sorted(list((fa5.get("conformance_vectors") or {}).keys()) + list((fa5.get("scenarios") or {}).keys()))
p4r5_ids = sorted(p4r5["scenarios"].keys())
srcs = {n: open(os.path.join(EV, n)).read() for n in ("FA5-first-admission.py", "P4r5-conformance-oracle.py", "gov_admit_reference.py")}
coverage = {
    "FA5_vector_or_scenario_revoking_a_final_or_candidate": [i for i in fa5_ids if re.search(r"final.*revok|candidate.*revok|revok.*(final|candidate)", i, re.I)],
    "FA5_source_revokes_FINAL_or_CAND_digest": bool(re.search(r"revocations\"\s*:\s*[^\n]*(FINAL\d|CAND\d)", srcs["FA5-first-admission.py"])),
    "P4r5_scenarios_revoking_final_or_candidate": [i for i in p4r5_ids if re.search(r"candidate_revoked|final_revoked", i)],
    "P4r5_scenarios_attestation_for_other_candidate": [i for i in p4r5_ids if re.search(r"attestation.*candidate|other_candidate", i)],
    "min_binary_version_mentioned_in": [n for n, t in srcs.items() if "min_binary_version" in t],
    "reference_counts_ACCEPTED_without_candidate_binding": "candidate_statement_digest\") != cand_d or s[\"payload\"].get(\"verdict\") != \"REJECTED\"" in srcs["gov_admit_reference.py"]
        and "sp.get(\"source\") != rp.get(\"source\")" in srcs["gov_admit_reference.py"],
}
out = {"probe": "RV5-D-A04 conformance-vector gaps between the two executors of admission-predicate/1 (AR-0014)",
       "bootstrap_reference_executor_rows": rows, "running_mode_oracle_rows": oracle, "coverage_in_committed_evidence": coverage,
       "openssl_verifications": V.calls}
out["verdicts"] = {
    "control_accepted_by_both": rows["R0_control_genuine"]["result"] == "ACCEPTED" and oracle["R0_control_genuine"] == "ACCEPTED",
    "R1_reference_accepts_revoked_final": rows["R1_registered_final_revoked"]["result"] == "ACCEPTED",
    "R1_oracle_refuses": oracle["R1_registered_final_revoked"] != "ACCEPTED",
    "R2_reference_accepts_revoked_candidate": rows["R2_registered_candidate_revoked"]["result"] == "ACCEPTED",
    "R2_oracle_refuses": oracle["R2_registered_candidate_revoked"] != "ACCEPTED",
    "R3_reference_accepts_attestation_for_other_candidate": rows["R3_attestation_for_another_candidate_same_source"]["result"] == "ACCEPTED",
    "R3_oracle_refuses": oracle["R3_attestation_for_another_candidate_same_source"] != "ACCEPTED",
    "R4_reference_ignores_min_binary_version": rows["R4_min_binary_version_above_binary"]["result"] == "ACCEPTED",
    "no_FA5_vector_for_R1_R2": not coverage["FA5_vector_or_scenario_revoking_a_final_or_candidate"] and not coverage["FA5_source_revokes_FINAL_or_CAND_digest"],
    "no_instrument_models_min_binary_version": not coverage["min_binary_version_mentioned_in"],
}
txt = json.dumps(out, indent=1, default=str).replace(SCR, "<scratch>").replace(REPO, "<repo>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
