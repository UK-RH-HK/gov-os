#!/usr/bin/env python3
"""P4r6 — conformance oracle for RoT-1 revision 6 (reference model; PROPOSED architecture instrument, not the implementation).

Loads, unmodified, `../r5/P4r5-conformance-oracle.py` and through it `../P4r4-trust-state-model.py`. Adds the revision-6 rules
and re-runs every P4r5 scenario with them.

Revision-6 rules modelled (normative text in brackets):
  AP-4   registration, registered final and candidate not revoked; binary version >= eligibility.min_binary_version, fail
         closed when the TBM names no version (`25` AP-4; RV5-M9 R1, R2, R4).
  AP-5   counted attestations name exactly the registered candidate AND the registered kernel tree digest; the registered final
         is promoted from the registered candidate and carries the registered kernel tree (`34` R-CON-2; RV5-M9 R3).
  AP-5r  a REJECTED attestation or a conflicting reproduction is removed as a restrictor only by a revocation issued under the
         registration authority (statement kind `rrev`); a trust-state or revocation-key revocation only lowers positive
         counts (`30` R-REP-5′; CR5-B-01).
  E7     policy-root eligibility applies AP-5's restrictors: registration referenced by the effective TSS and not revoked;
         the registered final and candidate held, verifying, not revoked, promoted from the registered candidate, both with
         the registered kernel tree and source; OP-8 ACCEPTED attestations for exactly that candidate and kernel; no REJECTED
         (`34` R-CON-3, `19` E7).
  CER    registration ceremony: custodians derive kernel tree and unit map from the fetched source and sign only an equal
         proposal with first-hand records for exactly the candidate (`34` R-CON-1).
  KS-14  root threshold >= 2 (`05` §3; CR5-B-11).
  CLK    a statement refused at ingest as issued in the future makes clock-based currency proofs (P1 window, witnesses)
         unusable for that unit of work (`24` §5.3, §8; CR5-B-08).
Rule of this oracle (unchanged): no row expects an attack to be ACCEPTED; only honest controls expect ACCEPTED. Accepted attack
sets are computed by CS6. Residual demonstrations are reported separately.

Output: JSON on stdout. Scratch-free. Deterministic.
"""
import copy, importlib.util, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
_P5 = os.path.join(HERE, "..", "r5", "P4r5-conformance-oracle.py")
_spec = importlib.util.spec_from_file_location("p4r5_oracle", _P5)
p5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p5)
m = p5.m
m.PURPOSE_OF.update({"rrev": "release-registration"})
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
P6 = dict(p5.P5)
RULES6 = {"ap4_registration_final_candidate": True, "ap4_min_binary_version": True, "ap5_candidate_binding": True, "ap5_kernel_binding": True,
          "ap5r_revocation_authority": True, "e7_restrictors": True, "ks14_root_threshold": True, "clock_future_statements": True}


# ================================================================================================ statement constructors (revision 6 fields)
def rrs6(d, release_id, seq, final, candidate, kernel="K1", **kw):
    r = p5.rrs(d, release_id, seq, final, candidate, **kw)
    r["kernel"] = kernel
    return r


def attest6(d, candidate, kernel="K1", **kw):
    a = m.attest(d, candidate, **kw)
    a["kernel"] = kernel
    return a


def rrev(d, targets, signers=("g1", "g2"), issued_at=0):
    return {"kind": "rrev", "d": d, "targets": set(targets), "signers": list(signers), "issued_at": issued_at}


def upgrade(K):
    """Revision-5 model statements carry no kernel tree on attestations and registrations. The release constructor's default
    kernel tree is "K1"; an attestation or registration without one is read as naming "K1" (the value every P4r5 world uses)."""
    out = []
    for s in K:
        if s.get("kind") in ("att", "rrs") and "kernel" not in s:
            s = dict(s, kernel="K1")
        out.append(s)
    return out


# ================================================================================================ rules
def ftc_violations_r6(rootS):
    v = p5.ftc_violations(rootS)
    if RULES6["ks14_root_threshold"] and rootS["thresholds"].get("root", 0) < 2:
        v.append("root threshold below 2 (KS-14)")
    return v


def registration_authority_revocations(K, rootS):
    out = set()
    for s in K:
        if s["kind"] == "rrev" and m.verifies(s, rootS):
            out |= s["targets"]
    return out


def evaluate_machine_r6(K_all, machine, now, op7, gate_fingerprint=None):
    K, ts, fr, info = m.evaluate_machine(K_all, machine, now, op7, gate_fingerprint)
    future = [r for r in info["refused_at_ingest"] if r["reason"] == "STATEMENT_ISSUED_IN_FUTURE"]
    if RULES6["clock_future_statements"] and future and fr.get("proof") and "in-gate" not in fr["proof"]:
        fr = dict(fr, allowed=[c for c in fr["allowed"] if c != "C3"], proof=None, axis=fr["axis"] + " CLOCK_BEHIND_HELD_STATEMENTS")
    return K, ts, fr, info


def currency_covers_effective_r6(ts, fr, machine, now):
    if not fr.get("proof"):
        return False
    return p5.currency_covers_effective(ts, fr, machine, now)


def _version_lt(bv, mbv):
    return tuple(bv) < tuple(mbv)


def accept_binary_r6(b, K_all, machine, now, op7="a", gate_fingerprint=None):
    K_all = upgrade(K_all)
    K, ts, fr, info = evaluate_machine_r6(K_all, machine, now, op7, gate_fingerprint)
    rootS = m.eff_root_stmt(K)
    if ftc_violations_r6(rootS):
        return "ROOT_VERSION_INVALID"
    tpsS = m.tps_state(K)
    eff = ts.get("eff")
    N = m.negative_set(K, ts, tpsS["eff"])
    RA = registration_authority_revocations(K, rootS)
    t = b["tbm"]
    if b["digest"] in N:
        return "BINARY_REVOKED"
    regs = [r for r in K if r["kind"] == "rrs" and r["release_id"] == b["release_id"]]
    if len({r["d"] for r in regs}) > 1:
        return "REGISTRATION_EQUIVOCATION"
    Rg = regs[0] if regs else None
    if Rg is None or not eff or Rg["d"] not in eff["arts"]:
        return "RELEASE_UNREGISTERED"
    if RULES6["ap4_registration_final_candidate"] and Rg["d"] in N:
        return "BINARY_REVOKED"
    if b["target"] not in Rg["targets"]:
        return "TARGET_NOT_REGISTERED"
    F = next((s for s in K if s["kind"] == "release-final" and s["d"] == Rg["final"]), None)
    if F is None or F["source"] != Rg["source"] or F["promoted_from"] != Rg["candidate"]:
        return "RELEASE_FINAL_UNVERIFIED"
    if RULES6["ap5_kernel_binding"] and F["tree"] != Rg["kernel"]:
        return "RELEASE_FINAL_UNVERIFIED"
    if F["d"] in N or Rg["candidate"] in N:
        return "BINARY_REVOKED"
    fields = (tpsS["eff"] or {}).get("fields", {})
    if RULES6["ap4_min_binary_version"] and fields.get("min_binary_version") is not None:
        if t.get("version") is None or _version_lt(t["version"], fields["min_binary_version"]):
            return "BINARY_BELOW_TRUST_POLICY"
    restr_atts = [a for a in K if a["kind"] == "att" and a["candidate"] == Rg["candidate"] and
                  (a["d"] not in RA if RULES6["ap5r_revocation_authority"] else (a["d"] not in RA and a["d"] not in N))]
    if any(a["verdict"] == "REJECTED" for a in restr_atts):
        return "ARTIFACT_SOURCE_REJECTED"
    acc = set()
    for a in K:
        if a["kind"] != "att" or a["verdict"] != "ACCEPTED" or a["d"] in N or a["d"] in RA or a["d"] not in Rg["vrecs"] or a["source"] != Rg["source"]:
            continue
        if RULES6["ap5_candidate_binding"] and a["candidate"] != Rg["candidate"]:
            continue
        if RULES6["ap5_kernel_binding"] and a.get("kernel") != Rg["kernel"]:
            continue
        acc |= set(m.valid_signers(a, rootS))
    if len(acc) < P6["min_verification_records"]:
        return "VERIFICATION_RECORDS_BELOW_MINIMUM"
    one = lambda x: len(m.valid_signers(x, rootS)) == 1
    reps_count = [x for x in K if x["kind"] == "repro" and x["release_id"] == Rg["release_id"] and x["target"] == b["target"] and x["d"] not in N and x["d"] not in RA and one(x)]
    reps_restr = [x for x in K if x["kind"] == "repro" and x["release_id"] == Rg["release_id"] and x["target"] == b["target"] and one(x) and
                  (x["d"] not in RA if RULES6["ap5r_revocation_authority"] else (x["d"] not in RA and x["d"] not in N))]
    mine = {k for x in reps_count if x["binary"] == b["digest"] and x["source"] == Rg["source"] and x["tbm"] == t["d"] for k in m.valid_signers(x, rootS)}
    if len(mine) < max(P6["q"], rootS.get("quorums", {}).get("reproducer", 2)):
        return "REPRODUCTION_QUORUM_NOT_MET"
    if any(x["binary"] != b["digest"] for x in reps_restr):
        return "REPRODUCTION_CONFLICT"
    if Rg.get("binary") is not None and Rg["binary"] != b["digest"]:
        return "BINARY_NOT_REGISTERED"
    if b["digest"] not in eff["arts"]:
        return "BINARY_NOT_PUBLISHED"
    held = {("tps", s["v"]): s["d"] for s in K if s["kind"] == "tps"}
    held.update({("tss", s["seq"]): s["d"] for s in K if s["kind"] == "tss"})
    if held.get(("tps", t["tps_v"])) != t["tps_d"] or held.get(("tss", t["tss_seq"])) != t["tss_d"] or t["embedded_release"] != F["d"] or t["source"] != Rg["source"]:
        return "BINARY_T0_UNVERIFIED"
    hwm = machine.get("vts", {}).get("accepted_tbm", {"root": 0, "tps": 0, "tss": 0})
    if t["root_v"] < hwm["root"] or t["tps_v"] < hwm["tps"] or t["tss_seq"] < hwm["tss"]:
        return "BINARY_T0_ROLLBACK"
    if "C3" not in fr["allowed"] or not currency_covers_effective_r6(ts, fr, machine, now):
        ax = fr["axis"]
        return "TRUST_STATE_UNANCHORED" if ax.startswith("UNANCHORED") else "TRUST_STATE_BELOW_ANCHOR" if ax.startswith("BELOW") else "TRUST_STATE_REGRESSION" if ax.startswith("REGRESSION") else "TRUST_STATE_CURRENCY_UNPROVEN"
    return "ACCEPTED"


def eligible_release_r6(Rl, K_all, machine, now, op7="a"):
    K_all = upgrade(K_all)
    K, ts, fr, info = evaluate_machine_r6(K_all, machine, now, op7)
    rootS = m.eff_root_stmt(K)
    tpsS = m.tps_state(K)
    eff = ts.get("eff")
    N = m.negative_set(K, ts, tpsS["eff"])
    RA = registration_authority_revocations(K, rootS)
    regs = [r for r in K if r["kind"] == "rrs" and r["release_id"] == Rl["release_id"]]
    Rg = regs[0] if len(regs) == 1 else None
    no = lambda reason: {"eligible": False, "reason": reason}
    if Rg is None or not eff or Rg["d"] not in eff["arts"]:
        return no("release_unregistered")
    if Rg["units"] != Rl["units"] or Rg["final"] != Rl["d"]:
        return no("surface_unregistered_for_release")
    if RULES6["e7_restrictors"]:
        if Rg["d"] in N:
            return no("registration_revoked")
        F = next((s for s in K if s["kind"] == "release-final" and s["d"] == Rg["final"]), None)
        if F is None:
            return no("release_final_unverified")
        if F["promoted_from"] != Rg["candidate"]:
            return no("final_not_promoted_from_registered_candidate")
        if F["tree"] != Rg["kernel"] or F["source"] != Rg["source"]:
            return no("kernel_tree_digest_mismatch")
        C = next((s for s in K if s["kind"] == "release-candidate" and s["d"] == Rg["candidate"]), None)
        if C is None:
            return no("registered_candidate_unverified")
        if C["tree"] != Rg["kernel"] or C["source"] != Rg["source"]:
            return no("candidate_kernel_or_source_mismatch")
        if F["d"] in N or C["d"] in N:
            return no("revoked")
        restr = [a for a in K if a["kind"] == "att" and a["candidate"] == Rg["candidate"] and a["d"] not in RA]
        if any(a["verdict"] == "REJECTED" for a in restr):
            return no("artifact_source_rejected")
        acc = set()
        for a in K:
            if a["kind"] == "att" and a["verdict"] == "ACCEPTED" and a["candidate"] == Rg["candidate"] and a.get("kernel") == Rg["kernel"] and a["source"] == Rg["source"] \
                    and a["d"] in Rg["vrecs"] and a["d"] not in N and a["d"] not in RA:
                acc |= set(m.valid_signers(a, rootS))
        if len(acc) < P6["min_verification_records"]:
            return no("verification_records_below_minimum")
    use = m.eligible_use(Rl, K, ts, tpsS)
    return {"eligible": use["eligible"], "reason": ",".join(use["reasons"]) or None}


def ceremony_r6(proposal, fetched_source, derive, records):
    """R-CON-1 and R-REG-3 (d) revision 6: each custodian derives kernel tree and unit map from the source it fetched and signs
    only when they equal the proposal, with first-hand ACCEPTED records for exactly the proposed candidate and kernel."""
    derived = derive(fetched_source)
    reasons = []
    if tuple(fetched_source) != tuple(proposal["source"]):
        reasons.append("content_digest_mismatch")
    if derived["kernel"] != proposal["kernel"] or derived["units"] != proposal["units"]:
        reasons.append("REGISTRATION_CONTENT_NOT_ESTABLISHED")
    ok_records = [r for r in records if r["verdict"] == "ACCEPTED" and r["candidate"] == proposal["candidate"] and r["kernel"] == proposal["kernel"] and r["first_hand"]]
    if len(ok_records) < P6["min_verification_records"] or any(r["verdict"] == "REJECTED" and r["candidate"] == proposal["candidate"] for r in records):
        reasons.append("VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE")
    return {"signs": not reasons, "reasons": reasons}


def ingress_update_r6(Rl, K_all, machine, now, op7="a", gate_fingerprint=None):
    """Release ingress (C3; OP-3 mode B skips only the human gate): E7 revision 6, C3 and a currency proof naming the effective TSS."""
    el = eligible_release_r6(Rl, K_all, machine, now, op7)
    if not el["eligible"]:
        return "RELEASE_INELIGIBLE(%s)" % el["reason"]
    K, ts, fr, info = evaluate_machine_r6(upgrade(K_all), machine, now, op7, gate_fingerprint)
    if "C3" not in fr["allowed"] or not currency_covers_effective_r6(ts, fr, machine, now):
        return "TRUST_STATE_CURRENCY_UNPROVEN"
    return "PROCEED"


# ================================================================================================ revision-6 scenarios
W11 = upgrade(p5.W11)
AN = p5.anchored()


def world(replace=None, add=(), drop=()):
    return upgrade(p5.world(replace=replace, add=add, drop=drop))


def run_r6_scenarios():
    S = {}

    def rec(sid, computed, claim, expected, attack, section, **extra):
        holds = computed == expected if not callable(expected) else bool(expected(computed))
        S[sid] = {"section": section, "computed": computed, "expected": expected if not callable(expected) else "predicate (see claim)", "claim": claim,
                  "attack": attack, "holds": bool(holds), **extra}

    B11 = p5.B11
    rec("R6-AP-00_honest_control", accept_binary_r6(B11, W11, AN, NOW), "25 §5 revision 6: an honest binary is accepted", "ACCEPTED", False, "F")
    # ---- RV5-M9 R1–R4 (RV5-D-A04 shapes on the running-mode oracle)
    rec("R6-AP-R1_registered_final_revoked", accept_binary_r6(B11, world(replace={"t11": p5.t11_with(revs=["R7", "F11"])}, add=[m.revocation("rvF11", ["F11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4: the registered final is not revoked", "BINARY_REVOKED", True, "F", mutant="R6-final-revocation")
    rec("R6-AP-R2_registered_candidate_revoked", accept_binary_r6(B11, world(replace={"t11": p5.t11_with(revs=["R7", "C11"])}, add=[m.revocation("rvC11", ["C11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4: the registered candidate is not revoked", "BINARY_REVOKED", True, "F")
    rec("R6-AP-R2b_registration_revoked", accept_binary_r6(B11, world(replace={"t11": p5.t11_with(revs=["R7", "g11"])}, add=[m.revocation("rvg11", ["g11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4 revision 6: the registration is not revoked", "BINARY_REVOKED", True, "F", mutant="R6-registration-revocation")
    C11x = m.release("C11x", 0, stage="candidate")
    F11x = m.release("F11", 11, promoted_from="C11x", refs=(9, 2, 1))
    G11x = rrs6("g11", "4.1.11", 11, "F11", "C11x", vrecs=("a11",))
    rec("R6-AP-R3_attestation_for_another_candidate_same_source", accept_binary_r6(B11, world(replace={"g11": G11x, "F11": F11x}, add=[C11x]), AN, NOW),
        "25 AP-5 revision 6: counted attestations name exactly the registered candidate", "VERIFICATION_RECORDS_BELOW_MINIMUM", True, "F", mutant="R6-candidate-binding")
    TPS2m = dict(m.TPS2, fields=dict(m.TPS2["fields"], min_binary_version=(4, 1, 99)))
    rec("R6-AP-R4_binary_below_min_binary_version", accept_binary_r6(B11, world(replace={"TPS2": TPS2m}), AN, NOW),
        "25 AP-4: a binary whose TBM names no version, or a lower one, is below min_binary_version", "BINARY_BELOW_TRUST_POLICY", True, "F", mutant="R6-min-binary-version")
    B11v = p5.binary("B11", "4.1.11", dict(p5.TBM9, version=(4, 1, 99)))
    rec("R6-AP-R4c_control_binary_at_min_binary_version", accept_binary_r6(B11v, world(replace={"TPS2": TPS2m}), AN, NOW),
        "control: a binary at the floor is accepted", "ACCEPTED", False, "F")
    # ---- kernel binding
    rec("R6-AP-kernel_attestation_for_other_kernel", accept_binary_r6(B11, world(replace={"a11": attest6("a11", "C11", kernel="K-weak")}), AN, NOW),
        "25 AP-5 revision 6: counted attestations name the registered kernel tree digest", "VERIFICATION_RECORDS_BELOW_MINIMUM", True, "F", mutant="R6-kernel-binding")
    rec("R6-AP-kernel_final_kernel_differs_from_registration", accept_binary_r6(B11, world(replace={"g11": rrs6("g11", "4.1.11", 11, "F11", "C11", kernel="K-weak")}), AN, NOW),
        "25 AP-5 revision 6: the registered final carries the registered kernel tree", "RELEASE_FINAL_UNVERIFIED", True, "F", mutant="R6-final-kernel")
    # ---- CR5-B-01: restrictor revocation authority (RV5-B-A03 shape and its REJECTED variant)
    T12x_rev = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7", "rp11c"], arts=["g11", "B11"], issued_at=NOW - 60)
    W_conf = world(add=[p5.repro("rp11c", "4.1.11", "B11x", "tbm-f11", signers=("p3",)), T12x_rev, m.revocation("rvc", ["rp11c"], issued_at=NOW - 120)])
    rec("R6-AP5r_trust_state_revocation_does_not_clear_conflict", accept_binary_r6(B11, W_conf, AN, NOW, "a", (12, "t12x")),
        "30 R-REP-5 revision 6 (CR5-B-01 (i)): a trust-state revocation of a conflicting reproduction clears no conflict", "REPRODUCTION_CONFLICT", True, "F", mutant="R6-revocation-authority")
    W_confRA = world(add=[p5.repro("rp11c", "4.1.11", "B11x", "tbm-f11", signers=("p3",)), rrev("rrv", ["rp11c"])])
    rec("R6-AP5r_registration_authority_revocation_clears_forged_conflict", accept_binary_r6(B11, W_confRA, AN, NOW),
        "05 §9 playbook: the registration authority revokes a forged conflicting reproduction (AV-S1 remedy)", "ACCEPTED", False, "F")
    T12x_rej = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7", "a11r"], arts=["g11", "B11"], issued_at=NOW - 60)
    W_rej = world(add=[attest6("a11r", "C11", verdict="REJECTED", signers=("va2",)), T12x_rej, m.revocation("rvr", ["a11r"], issued_at=NOW - 120)])
    rec("R6-AP5r_trust_state_revocation_does_not_clear_REJECTED", accept_binary_r6(B11, W_rej, AN, NOW, "a", (12, "t12x")),
        "25 AP-5r (CR5-B-01 (ii)): a trust-state revocation of a REJECTED attestation clears nothing", "ARTIFACT_SOURCE_REJECTED", True, "F")
    # ---- KS-14
    ROOT_T1 = dict(p5.root5(), thresholds=dict(p5.root5()["thresholds"], root=1))
    rec("R6-KS14_root_threshold_1", accept_binary_r6(B11, [ROOT_T1] + W11[1:], AN, NOW), "05 §3 KS-14 (CR5-B-11): a root version with threshold 1 is invalid", "ROOT_VERSION_INVALID", True, "F", mutant="R6-ks14")
    # ---- E7 revision 6 (RV5-D-A01 part A shapes)
    C12 = m.release("C12", 0, stage="candidate", kernel_tree="K12-fixed")
    A12 = attest6("a12", "C12", kernel="K12-fixed")
    C12x = m.release("C12x", 0, stage="candidate", kernel_tree="K12-weak")
    F12x = m.release("F12x", 12, promoted_from="C12x", kernel_tree="K12-weak", refs=(11, 2, 1))
    G12x = rrs6("g12x", "4.1.12", 12, "F12x", "C12x", kernel="K12-weak", vrecs=("a12",), units={"leaf:aws": "d-weak"})
    T12 = m.tss(12, "t12", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g12x"], issued_at=NOW - HOUR)
    REL12x = {"kind": "release-final", "d": "F12x", "release_id": "4.1.12", "seq": 12, "stage": "final", "units": {"leaf:aws": "d-weak"}, "refs": {"state": 11, "policy": 2, "root": 1}}
    AN12 = p5.anchored(12, "t12")
    W = W11 + [C12, A12, C12x, F12x, G12x, T12]
    rec("R6-E7-D-A01_attacker_candidate_and_final_weak_kernel", eligible_release_r6(REL12x, W, AN12, NOW),
        "34 R-CON-3: E7 counts attestations only for the registered candidate and kernel; the honest verifier attested C12/K12-fixed", {"eligible": False, "reason": "verification_records_below_minimum"}, True, "G", mutant="R6-E7-restrictors")
    G12y = rrs6("g12x", "4.1.12", 12, "F12x", "C12", kernel="K12-weak", vrecs=("a12",), units={"leaf:aws": "d-weak"})
    rec("R6-E7-D-A01_variant_registration_names_attested_candidate", eligible_release_r6(REL12x, W11 + [C12, A12, C12x, F12x, G12y, T12], AN12, NOW),
        "34 R-CON-3: the registered final must be promoted from the registered candidate", {"eligible": False, "reason": "final_not_promoted_from_registered_candidate"}, True, "G")
    ROOT_OP4NO = p5.root5(extra={"kc": ["release-final", "release-candidate"]})
    Wk = upgrade([ROOT_OP4NO] + p5.W11[1:]) + [C12, A12, dict(C12x, signers=["kc"]), dict(F12x, signers=["kc"]), G12x, T12]
    rec("R6-E7-D-A01_op4_no_one_everyday_key", eligible_release_r6(REL12x, Wk, AN12, NOW),
        "34: OP-4 'no' changes nothing: one key holding release-final and release-candidate selects no content", {"eligible": False, "reason": "verification_records_below_minimum"}, True, "G")
    C12g = m.release("C12g", 0, stage="candidate", kernel_tree="K12-fixed")
    A12g = attest6("a12g", "C12g", kernel="K12-fixed")
    F12g = m.release("F12g", 12, promoted_from="C12g", kernel_tree="K12-fixed", refs=(11, 2, 1))
    G12g = rrs6("g12g", "4.1.12", 12, "F12g", "C12g", kernel="K12-fixed", vrecs=("a12g",), units={"leaf:aws": "d-fixed"})
    T12g = m.tss(12, "t12", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g12g"], issued_at=NOW - HOUR)
    REL12g = dict(REL12x, d="F12g", units={"leaf:aws": "d-fixed"})
    rec("R6-E7-control_genuine_release_eligible", eligible_release_r6(REL12g, W11 + [C12g, A12g, F12g, G12g, T12g], AN12, NOW),
        "control: the genuine registered release stays eligible", {"eligible": True, "reason": None}, False, "G")
    G12n = rrs6("g12g", "4.1.12", 12, "F12g", "C12g", kernel="K12-fixed", vrecs=(), units={"leaf:aws": "d-fixed"})
    rec("R6-E7-B-A06_registration_without_verification_record", eligible_release_r6(REL12g, W11 + [C12g, F12g, G12n, T12g], AN12, NOW),
        "34 R-CON-3 (RV5-B-A06): a registration with no verification record makes no policy root", {"eligible": False, "reason": "verification_records_below_minimum"}, True, "G")
    rec("R6-E7-REJECTED_held", eligible_release_r6(REL12g, W11 + [C12g, A12g, attest6("a12r", "C12g", kernel="K12-fixed", verdict="REJECTED", signers=("va2",)), F12g, G12g, T12g], AN12, NOW),
        "34 R-CON-3: a held REJECTED attestation for the registered candidate refuses", {"eligible": False, "reason": "artifact_source_rejected"}, True, "G")
    rec("R6-E7-candidate_not_held", eligible_release_r6(REL12g, W11 + [A12g, F12g, G12g, T12g], AN12, NOW),
        "34 R-CON-3: the registered candidate must be held and verify", {"eligible": False, "reason": "registered_candidate_unverified"}, True, "G")
    # ---- ceremony (R-CON-1)
    derive = lambda src: {"kernel": "K12-fixed", "units": {"leaf:aws": "d-fixed"}} if tuple(src) == p5.GOOD else {"kernel": "K-" + src[1], "units": {"leaf:aws": "d-" + src[1]}}
    recs = [{"verdict": "ACCEPTED", "candidate": "C12", "kernel": "K12-fixed", "first_hand": True}]
    rec("R6-CER-D-A01_ceremony_derives_content_first_hand", ceremony_r6({"source": p5.GOOD, "kernel": "K12-weak", "units": {"leaf:aws": "d-weak"}, "candidate": "C12x"}, p5.GOOD, derive, recs),
        "34 R-CON-1: custodians refuse a proposal whose kernel and units differ from what they derive from the fetched source", lambda c: not c["signs"] and "REGISTRATION_CONTENT_NOT_ESTABLISHED" in c["reasons"], True, "G")
    rec("R6-CER-records_for_another_candidate", ceremony_r6({"source": p5.GOOD, "kernel": "K12-fixed", "units": {"leaf:aws": "d-fixed"}, "candidate": "C12x"}, p5.GOOD, derive, recs),
        "30 R-REG-3 (d) revision 6: custodians count only first-hand ACCEPTED records for exactly the proposed candidate (content equal, candidate substituted)",
        lambda c: not c["signs"] and c["reasons"] == ["VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE"], True, "G", mutant="R6-ceremony-first-hand-records")
    rec("R6-CER-REJECTED_record_for_candidate", ceremony_r6({"source": p5.GOOD, "kernel": "K12-fixed", "units": {"leaf:aws": "d-fixed"}, "candidate": "C12"}, p5.GOOD, derive,
                                                           recs + [{"verdict": "REJECTED", "candidate": "C12", "kernel": "K12-fixed", "first_hand": True}]),
        "30 R-REG-3 (d) revision 6: a first-hand REJECTED record for the proposed candidate refuses", lambda c: not c["signs"] and c["reasons"] == ["VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE"], True, "G")
    rec("R6-CER-records_not_first_hand", ceremony_r6({"source": p5.GOOD, "kernel": "K12-fixed", "units": {"leaf:aws": "d-fixed"}, "candidate": "C12"}, p5.GOOD, derive,
                                                    [dict(recs[0], first_hand=False)]),
        "30 R-REG-3 (d): a record not received first-hand from its verifier counts for nothing", lambda c: not c["signs"] and c["reasons"] == ["VERIFICATION_RECORDS_NOT_FIRST_HAND_FOR_CANDIDATE"], True, "G")
    rec("R6-CER-control_genuine_proposal", ceremony_r6({"source": p5.GOOD, "kernel": "K12-fixed", "units": {"leaf:aws": "d-fixed"}, "candidate": "C12"}, p5.GOOD, derive, recs),
        "control: the genuine proposal is signed", lambda c: c["signs"], False, "G")
    # ---- CR5-B-08: clock set back on a restored store while newer statements are delivered
    fake_now = NOW - 395 * DAY
    old_world, true_world = p5.clock_worlds()
    restored = {"vts": {"anchors": [{"seq": 5, "digest": "t5c", "at": fake_now - 5 * DAY, "method": "human"}], "accepted_tbm": {"root": 1, "tps": 2, "tss": 4},
                        "clock_high_water": NOW - 800 * DAY}}
    rec("R6-CLOCK-CR5-B-08_restored_store_clock_back_newer_statements_delivered", accept_binary_r6(p5.CLOCK_B7, true_world, restored, fake_now),
        "24 §8 revision 6 (CR5-B-08): statements refused as issued in the future make clock-based currency proofs unusable", lambda c: c != "ACCEPTED", True, "H", mutant="R6-clock-future")
    # ---- RV5-L9: OP-3 mode B needs a currency proof naming the publishing TSS for each update
    C13, F13 = m.release("C13", 0, stage="candidate"), m.release("F13", 13, promoted_from="C13", refs=(11, 2, 1))
    A13 = attest6("a13", "C13")
    G13 = rrs6("g13", "4.1.13", 13, "F13", "C13", vrecs=("a13",), units={})
    T13 = m.tss(12, "t12", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g13"], issued_at=NOW - HOUR)
    REL13 = {"kind": "release-final", "d": "F13", "release_id": "4.1.13", "seq": 13, "stage": "final", "units": {}, "refs": {"state": 11, "policy": 2, "root": 1}}
    WB = W11 + [C13, A13, F13, G13, T13]
    modeB_machine = {"pins": [m.pin(11, "t11", 1)], "vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 5}}}
    rec("R6-OP3-B-RV5-L9_mode_B_update_without_proof_naming_publishing_TSS", ingress_update_r6(REL13, WB, modeB_machine, NOW),
        "21 OP-3 mode B (RV5-L9): a machine anchored at t11 refuses an update published in t12 without a proof naming t12", "TRUST_STATE_CURRENCY_UNPROVEN", True, "H")
    rec("R6-OP3-B-control_in_gate_fingerprint_names_t12", ingress_update_r6(REL13, WB, modeB_machine, NOW, "a", (12, "t12")),
        "control: a typed fingerprint naming the publishing TSS is a proof", "PROCEED", False, "H")
    return S


# ================================================================================================ P4r5 scenarios under revision-6 rules
def run_p4r5_under_r6():
    """Every P4r5 scenario re-run with accept_binary / eligible_release replaced by the revision-6 functions (statements upgraded
    as `upgrade` states). Refusal preservation: every P4r5 row expected to refuse still refuses; every honest control still
    passes. Exact-code equality is reported separately."""
    spec = importlib.util.spec_from_file_location("p4r5_under_r6", _P5)
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    base = {k: v for k, v in q.run_scenarios().items()}
    q.accept_binary = lambda b, K, mach, now, op7="a", gf=None: accept_binary_r6(b, K, mach, now, op7, gf)
    q.eligible_release_r5 = lambda Rl, K, mach, now, op7="a": eligible_release_r6(Rl, K, mach, now, op7)
    r6 = q.run_scenarios()
    rows, preserved, exact = {}, 0, 0
    for k, v in base.items():
        w = r6[k]
        if v["attack"]:
            refused_r5 = v["computed"] != "ACCEPTED" and not (isinstance(v["computed"], dict) and v["computed"].get("eligible") is True)
            refused_r6 = w["computed"] != "ACCEPTED" and not (isinstance(w["computed"], dict) and w["computed"].get("eligible") is True)
            if isinstance(v["computed"], dict) and "honest_current_pin_t10" in v["computed"]:
                refused_r5 = all(x != "ACCEPTED" for x in v["computed"].values())
                refused_r6 = all(x != "ACCEPTED" for x in w["computed"].values())
            ok = (not refused_r5) or refused_r6
        else:
            ok = w["holds"]
        preserved += ok
        exact += w["holds"]
        rows[k] = {"attack": v["attack"], "r5_computed": v["computed"], "r6_computed": w["computed"], "r6_holds_with_r5_expectation": w["holds"], "refusal_or_control_preserved": ok}
    return {"scenarios": len(rows), "refusal_or_control_preserved": preserved, "holding_with_unchanged_expectation": exact, "rows": rows}


def main():
    new = run_r6_scenarios()
    under = run_p4r5_under_r6()
    attack_accepted = [k for k, v in new.items() if v["attack"] and v["expected"] == "ACCEPTED"]
    summary = {"revision_6_scenarios": len(new), "revision_6_holding": sum(v["holds"] for v in new.values()), "revision_6_failing": sorted(k for k, v in new.items() if not v["holds"]),
               "expected_ACCEPTED_rows_that_are_attacks": attack_accepted, "honest_controls": sorted(k for k, v in new.items() if not v["attack"]),
               "p4r5_scenarios_under_r6": under["scenarios"], "p4r5_refusal_or_control_preserved": under["refusal_or_control_preserved"],
               "p4r5_holding_with_unchanged_expectation": under["holding_with_unchanged_expectation"], "rules": RULES6, "params": P6}
    residual = {"RS-2b_restored_store_clock_back_every_newer_statement_withheld": {
        "result": accept_binary_r6(p5.CLOCK_B7, p5.clock_worlds()[0], {"vts": {"anchors": [{"seq": 5, "digest": "t5c", "at": NOW - 400 * DAY, "method": "human"}],
                                                                             "accepted_tbm": {"root": 1, "tps": 2, "tss": 4}, "clock_high_water": NOW - 800 * DAY}}, NOW - 395 * DAY),
        "note": "24 §10 RS-2b: with every statement issued after the backup withheld and the clock set back into the anchor's window, the machine cannot distinguish the past; bound: A13 on the machine plus withholding; TA-7"}}
    print(json.dumps({"summary": summary, "scenarios": new, "p4r5_under_r6": under, "residual_demonstrations_not_oracle_rows": residual},
                     indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))


if __name__ == "__main__":
    main()
