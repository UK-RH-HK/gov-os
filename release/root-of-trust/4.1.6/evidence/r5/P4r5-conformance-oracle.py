#!/usr/bin/env python3
"""P4r5 — conformance oracle for RoT-1 revision 5 (reference model; PROPOSED architecture instrument, not the implementation).

Scope.
  * Retained trust-state, anchoring, currency, lifting, clock, OP-7 and trust-gate rules: the revision-4 functions of
    `P4r4-trust-state-model.py`, loaded by path and NOT modified. Its scenarios that do not call its superseded
    `verify_artifact` are part of this oracle ("retained_p4r4_scenarios").
  * Binary acceptance: admission-predicate/1 running mode (`25` §5) — registration (`release-registration`), a quorum of
    one-signature reproductions (`reproducer`), publication, TBM, the accepted-TBM high-water, negatives and currency,
    with the Fact Threshold Check on root versions (`05` §3). Revision 4's `release-artifact` / `build-attestation`
    acceptance is superseded; every VA4 row and every P4r4 binary scenario is re-expressed below.
  * Release eligibility under exact per-release registration (`23` §12, `19` E7): model level. The executed checker
    evidence is REG5.
  * Carried rules made normative in revision 5: CR4-B-07 option 1 (a P1 proof covers only the TSS it names), CR4-B-08
    (first-run accepted-TBM recording), CR4-B-09 (decision-pin maximum validity), CR4-B-10 (revoked attestations and
    reproductions never count), RV4-M4 (stateful clock high-water raised by every ingested non-future statement).
  * A distinguishing scenario for each of review r4 D-A03's twenty single-line mutants (RV4-M7): the thirteen on retained
    P4r4 lines, and the seven revision-4 `verify_artifact` rules re-expressed as the named lines of `accept_binary` here.
Rule of this oracle (review r4 §7 criterion 4): no row expects an attack to be ACCEPTED. The only ACCEPTED expectations
are honest controls (`attack: false`). Accepted attack sets (the stated minima) are computed by CS5, and residual
demonstrations below are reported separately and are not oracle rows.

Attribution. Retained functions and constructors: revision-4 architect P4r4 (unmodified). Distinguishing constructions for
the eleven D-A03 mutants P4r4 missed follow `4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A03b-distinguishing-scenarios.py`.
VA4 row shapes follow `evidence/VA4-verify-artifact-source-scenarios.py`. The revision-5 rules are this revision's.
Scratch-free. Output: JSON on stdout.
"""
import copy, importlib.util, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
_P4R4 = os.path.join(HERE, "P4r4-trust-state-model.py")
if not os.path.exists(_P4R4):
    _P4R4 = os.path.join(HERE, "..", "P4r4-trust-state-model.py")
_spec = importlib.util.spec_from_file_location("p4r4_model", _P4R4)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

m.PURPOSE_OF.update({"rrs": "release-registration", "repro": "reproducer"})
m.COMPILED_MIN_THRESHOLD.update({"release-registration": 2})  # per statement; the reproducer quorum is counted across one-signature statements
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
GOOD = ("commit-good", "tree-good", "inputs-good")
EVIL = ("commit-evil", "tree-evil", "inputs-good")
OTHER = ("commit-other", "tree-other", "inputs-good")
TARGET = "x86_64-linux"
P5 = {"min_verification_records": 1, "q": 2, "decision_pin_max_validity_days": 90, "clock_skew_seconds": 300}
WITHDRAWN = {"release-artifact", "build-attestation"}
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]
PRIOR11 = PRIOR10 + [(11, "t11")]


# ================================================================================================ revision-5 statements
def grants5(extra=None, drop=()):
    g, t = m.grants_v1()
    g = {k: v for k, v in g.items() if k not in ("ra1", "ra2", "ba1") and k not in drop}
    g.update({"g1": ["release-registration"], "g2": ["release-registration"], "g3": ["release-registration"],
              "p1": ["reproducer"], "p2": ["reproducer"], "p3": ["reproducer"], "va2": ["verification-attestation"]})
    g.update(extra or {})
    t = {k: v for k, v in t.items() if k != "release-artifact"}
    t.update({"release-registration": 2})
    return g, t


def root5(v=1, extra=None, drop=(), quorum=2, revoked=()):
    r = m.root(v, *grants5(extra=extra, drop=drop), revoked=revoked)
    r["quorums"] = {"reproducer": quorum}
    return r


ROOT5 = root5()


def rrs(d, release_id, seq, final, candidate, source=GOOD, targets=(TARGET,), vrecs=("a11",), signers=("g1", "g2"), binary=None, units=None):
    return {"kind": "rrs", "d": d, "release_id": release_id, "seq": seq, "final": final, "candidate": candidate, "source": tuple(source),
            "targets": list(targets), "vrecs": set(vrecs), "signers": list(signers), "binary": binary, "units": dict(units or {}), "issued_at": 0}


def repro(d, release_id, binary_d, tbm_d, source=GOOD, target=TARGET, signers=("p1",)):
    return {"kind": "repro", "d": d, "release_id": release_id, "binary": binary_d, "tbm": tbm_d, "source": tuple(source), "target": target,
            "signers": list(signers), "issued_at": 0}


def binary(digest, release_id, tbm, target=TARGET):
    return {"digest": digest, "release_id": release_id, "tbm": tbm, "target": target}


# ================================================================================================ 05 §3 Fact Threshold Check (FTC)
def ftc_violations(rootS):
    g, t = rootS["grants"], rootS["thresholds"]
    by = {}
    for k, ps in g.items():
        for p in ps:
            by.setdefault(p, set()).add(k)
    v = []
    if any(p in WITHDRAWN for p in by):
        v.append("withdrawn purpose granted")
    rep, reg, ver, root_keys = by.get("reproducer", set()), by.get("release-registration", set()), by.get("verification-attestation", set()), by.get("root", set())
    if rep and (rootS.get("quorums", {}).get("reproducer", 0) < 2 or any(len(g[k]) > 1 for k in rep)):
        v.append("reproducer threshold below 2 or reproducer key holds another purpose")
    if reg and t.get("release-registration", 1) < 2:
        v.append("release-registration threshold below 2")
    if reg and not (reg <= root_keys and t.get("release-registration", 1) >= t.get("root", 2)) and any(len(g[k]) > 1 for k in reg):
        v.append("release-registration keys neither root keys at root threshold nor single-purpose")
    if ver & (rep | reg):
        v.append("verification key also reproducer or registration key")
    return v


# ================================================================================================ 24 §4.4 revision 5: a P1 proof covers the TSS it names
def currency_covers_effective(ts, fr, machine, now):
    proof = fr.get("proof") or ""
    if "anchored within the C3 currency window" not in proof:
        return True
    eff = ts.get("eff")
    pins, _ = m.honoured_pins(machine, now, True)
    anchors = [dict(a) for a in machine.get("vts", {}).get("anchors", [])] + pins
    window = m.P["c3_currency_window_hours"] * HOUR
    return any((a["seq"], a["digest"]) == (eff["seq"], eff["d"]) and 0 <= now - a["at"] <= window for a in anchors)


# ================================================================================================ 25 §5 admission-predicate/1, running mode
def accept_binary(b, K_all, machine, now, op7="a", gate_fingerprint=None):
    K, ts, fr, info = m.evaluate_machine(K_all, machine, now, op7, gate_fingerprint)
    rootS = m.eff_root_stmt(K)
    if ftc_violations(rootS):
        return "ROOT_VERSION_INVALID"
    tpsS = m.tps_state(K)
    eff = ts.get("eff")
    N = m.negative_set(K, ts, tpsS["eff"])
    t = b["tbm"]
    if b["digest"] in N:
        return "BINARY_REVOKED"
    regs = [r for r in K if r["kind"] == "rrs" and r["release_id"] == b["release_id"] and r["d"] not in N]
    if len({r["d"] for r in regs}) > 1:
        return "REGISTRATION_EQUIVOCATION"
    Rg = regs[0] if regs else None
    if Rg is None:
        return "RELEASE_UNREGISTERED"
    if not eff or Rg["d"] not in eff["arts"]:
        return "RELEASE_UNREGISTERED"
    if b["target"] not in Rg["targets"]:
        return "TARGET_NOT_REGISTERED"
    F = next((s for s in K if s["kind"] == "release-final" and s["d"] == Rg["final"]), None)
    if F is None or F["source"] != Rg["source"] or F["promoted_from"] != Rg["candidate"]:
        return "RELEASE_FINAL_UNVERIFIED"
    if F["d"] in N or Rg["candidate"] in N:
        return "BINARY_REVOKED"
    atts = [a for a in K if a["kind"] == "att" and a["candidate"] == Rg["candidate"] and a["d"] not in N]
    if any(a["verdict"] == "REJECTED" for a in atts):
        return "ARTIFACT_SOURCE_REJECTED"
    acc = {k for a in atts if a["verdict"] == "ACCEPTED" and a["source"] == Rg["source"] and a["d"] in Rg["vrecs"] for k in m.valid_signers(a, rootS)}
    if len(acc) < P5["min_verification_records"]:
        return "VERIFICATION_RECORDS_BELOW_MINIMUM"
    reps = [x for x in K if x["kind"] == "repro" and x["release_id"] == Rg["release_id"] and x["target"] == b["target"] and x["d"] not in N and len(m.valid_signers(x, rootS)) == 1]
    mine = {k for x in reps if x["binary"] == b["digest"] and x["source"] == Rg["source"] and x["tbm"] == t["d"] for k in m.valid_signers(x, rootS)}
    if len(mine) < max(P5["q"], rootS.get("quorums", {}).get("reproducer", 2)):
        return "REPRODUCTION_QUORUM_NOT_MET"
    if any(x["binary"] != b["digest"] for x in reps):
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
    if "C3" not in fr["allowed"] or not currency_covers_effective(ts, fr, machine, now):
        ax = fr["axis"]
        return "TRUST_STATE_UNANCHORED" if ax.startswith("UNANCHORED") else "TRUST_STATE_BELOW_ANCHOR" if ax.startswith("BELOW") else "TRUST_STATE_REGRESSION" if ax.startswith("REGRESSION") else "TRUST_STATE_CURRENCY_UNPROVEN"
    return "ACCEPTED"


# ================================================================================================ 25 §5 first-run recording (CR4-B-08)
def first_run_record(vts, tbm_, build, resolves):
    hw = dict(vts.get("accepted_tbm", {"root": 0, "tps": 0, "tss": 0}))
    if build == "release" and resolves:
        hw = {"root": max(hw["root"], tbm_["root_v"]), "tps": max(hw["tps"], tbm_["tps_v"]), "tss": max(hw["tss"], tbm_["tss_seq"])}
    return dict(vts, accepted_tbm=hw)


# ================================================================================================ 24 §8 revision 5: stateful clock high-water (RV4-M4)
def persist_clock_high_water(machine, K_all, now):
    hw = machine.get("vts", {}).get("clock_high_water", 0)
    rootS = m.eff_root_stmt(K_all)
    for s in K_all:
        if m.verifies(s, rootS) and s.get("issued_at", 0) <= now + P5["clock_skew_seconds"]:
            hw = max(hw, s.get("issued_at", 0))
    mach = copy.deepcopy(machine)
    mach.setdefault("vts", {})["clock_high_water"] = hw
    return mach


# ================================================================================================ 27 §3.2 revision 5: decision-pin maximum validity (CR4-B-09)
def trust_gate_authorised_r5(kind, digests, project, confirmations, decision_pins, tps_eff, now):
    kept = []
    for p in decision_pins:
        if p.get("expires_at") is not None and p.get("provisioned_at") is not None and p["expires_at"] - p["provisioned_at"] > P5["decision_pin_max_validity_days"] * DAY:
            continue
        kept.append(p)
    return m.trust_gate_authorised(kind, digests, project, confirmations, kept, tps_eff, now)


# ================================================================================================ 19 E7 revision 5 (model level): exact per-release registration
def eligible_release_r5(Rl, K_all, machine, now, op7="a"):
    K, ts, fr, info = m.evaluate_machine(K_all, machine, now, op7)
    tpsS = m.tps_state(K)
    eff = ts.get("eff")
    regs = [r for r in K if r["kind"] == "rrs" and r["release_id"] == Rl["release_id"]]
    Rg = regs[0] if len(regs) == 1 else None
    if Rg is None or not eff or Rg["d"] not in eff["arts"]:
        return {"eligible": False, "reason": "release_unregistered"}
    if Rg["units"] != Rl["units"] or Rg["final"] != Rl["d"]:
        return {"eligible": False, "reason": "surface_unregistered_for_release"}
    use = m.eligible_use(Rl, K, ts, tpsS)
    return {"eligible": use["eligible"], "reason": ",".join(use["reasons"]) or None}


# ================================================================================================ world
GEN5 = [ROOT5, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7]
C11 = m.release("C11", 0, stage="candidate")
A11 = m.attest("a11", "C11")
F11 = m.release("F11", 11, promoted_from="C11", refs=(9, 2, 1))
G11 = rrs("g11", "4.1.11", 11, "F11", "C11")
TBM9 = m.tbm("tbm-f11", 2, "TPS2", 9, "t9", "F11")
B11 = binary("B11", "4.1.11", TBM9)
RP11 = [repro("rp11a", "4.1.11", "B11", "tbm-f11", signers=("p1",)), repro("rp11b", "4.1.11", "B11", "tbm-f11", signers=("p2",))]
T11 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 2 * HOUR)
W11 = GEN5 + [C11, A11, F11, G11, T11] + RP11


def anchored(seq=11, d="t11", days_ago=0, tbm_hw=(1, 2, 5)):
    mach = m.human(seq, d, days_ago)
    mach["vts"]["accepted_tbm"] = {"root": tbm_hw[0], "tps": tbm_hw[1], "tss": tbm_hw[2]}
    return mach


def world(replace=None, add=(), drop=()):
    out = []
    for s in W11:
        if s.get("d") in drop:
            continue
        out.append((replace or {}).get(s.get("d"), s))
    return out + list(add)


def t11_with(**kw):
    base = dict(prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 2 * HOUR)
    base.update(kw)
    return m.tss(11, "t11", **base)


def run_scenarios():
    S = {}

    def rec(sid, computed, claim, expected, attack, section, **extra):
        holds = computed == expected if not callable(expected) else bool(expected(computed))
        S[sid] = {"section": section, "computed": computed, "expected": expected if not callable(expected) else "predicate (see claim)", "claim": claim,
                  "attack": attack, "holds": bool(holds), **extra}

    AN = anchored()
    # ---------------------------------------------------------------- A. admission-predicate/1: honest controls
    rec("AP-00_honest_registered_reproduced_published", accept_binary(B11, W11, AN, NOW), "25 §5: an honest release binary is accepted", "ACCEPTED", False, "A")
    TBM10 = m.tbm("tbm-f11b", 2, "TPS2", 10, "t10", "F11")
    B11b = binary("B11b", "4.1.11", TBM10)
    rec("AP-00b_stateless_witnessed_runner_op7c", accept_binary(B11, W11 + [m.witness("w11", 11, "t11", NOW - HOUR, NOW + DAY)], {"vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 5}}}, NOW, "c"),
        "24 §4.4 revision 5 (CR4-B-06): WITNESSED at the C3 threshold is a currency proof (P3), as the decision table states", "ACCEPTED", False, "A")
    # ---------------------------------------------------------------- A. carried revision-4 rules re-expressed (D-A03 verify_artifact mutants)
    rec("AP-A8_candidate_revoked", accept_binary(B11, world(replace={"t11": t11_with(revs=["R7", "C11"])}, add=[m.revocation("rvC11", ["C11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4 (D-A03 A8): a revoked candidate refuses the binary", "BINARY_REVOKED", True, "A", mutant="R5-A8-omits-candidate")
    rec("AP-A4b_rejected_attestation_held", accept_binary(B11, world(add=[m.attest("a11r", "C11", verdict="REJECTED", signers=("va2",))]), AN, NOW),
        "25 AP-5 (D-A03 A4b REJECTED): a REJECTED verification attestation for the registered candidate refuses", "ARTIFACT_SOURCE_REJECTED", True, "A", mutant="R5-A4b-ignores-REJECTED")
    C13, A13, F13 = m.release("C13", 0, stage="candidate"), m.attest("a13", "C13"), m.release("F13", 13, promoted_from="C13", refs=(9, 2, 1))
    G13 = rrs("g13", "4.1.13", 13, "F13", "C13", vrecs=("a13",))
    TBM13 = m.tbm("tbm-f13", 2, "TPS2", 9, "t9", "F13")
    B13 = binary("B13", "4.1.13", TBM13)
    T13 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], arts=["g13", "B13"], issued_at=NOW - 2 * HOUR)
    W13_other = GEN5 + [C13, A13, F13, G13, T13, repro("rp13a", "4.1.13", "B13", "tbm-f13", source=OTHER, signers=("p1",)), repro("rp13b", "4.1.13", "B13", "tbm-f13", source=OTHER, signers=("p2",))]
    rec("AP-A4a_reproductions_name_another_source", accept_binary(B13, W13_other, AN, NOW),
        "25 AP-6 (D-A03 A4a): reproductions count only for the registered source", "REPRODUCTION_QUORUM_NOT_MET", True, "A", mutant="R5-A4a-source-not-compared")
    G13v = rrs("g13", "4.1.13", 13, "F13", "C13", vrecs=("a13-listed",))
    W13_unlisted = GEN5 + [C13, m.attest("a13x", "C13", signers=("va2",)), F13, G13v, T13, repro("rp13a", "4.1.13", "B13", "tbm-f13", signers=("p1",)), repro("rp13b", "4.1.13", "B13", "tbm-f13", signers=("p2",))]
    rec("AP-A4b_attestation_not_listed_by_registration", accept_binary(B13, W13_unlisted, AN, NOW),
        "25 AP-5 (D-A03 A4b reference): only attestations the TSS-referenced registration lists count", "VERIFICATION_RECORDS_BELOW_MINIMUM", True, "A", mutant="R5-A4b-attestation-not-registered")
    rec("AP-A5_registered_reproduced_not_published", accept_binary(B11, world(replace={"t11": t11_with(arts=["g11"])}), AN, NOW),
        "25 AP-7 (D-A03 A5): the selected TSS must publish the digest", "BINARY_NOT_PUBLISHED", True, "A", mutant="R5-A5-publication-not-required")
    rec("AP-A7_older_binary_after_newer_accepted", accept_binary(B11, W11, anchored(tbm_hw=(1, 2, 10)), NOW),
        "25 AP-8 (D-A03 A7): TBM below the accepted-TBM high-water refuses", "BINARY_T0_ROLLBACK", True, "A", mutant="R5-A7-disabled")
    rec("AP-A9_no_currency_proof_aged_anchor", accept_binary(B11, W11, anchored(days_ago=30), NOW),
        "25 AP-3 (D-A03 A9): binary acceptance needs C3 with a currency proof", "TRUST_STATE_CURRENCY_UNPROVEN", True, "A", mutant="R5-A9-not-applied")
    # ---------------------------------------------------------------- A. revision-5 rules
    rec("AP-R5_registration_not_referenced_by_tss", accept_binary(B11, world(replace={"t11": t11_with(arts=["B11"])}), AN, NOW),
        "25 AP-5: the registration must be referenced by the selected TSS", "RELEASE_UNREGISTERED", True, "A", mutant="R5-registration-not-referenced")
    rec("AP-R5_registration_one_key", accept_binary(B11, world(replace={"g11": dict(G11, signers=["g1"])}), AN, NOW),
        "05 §3: release-registration threshold >= 2; one stolen key registers nothing", "RELEASE_UNREGISTERED", True, "A")
    G11x = rrs("g11x", "4.1.11", 11, "F11", "C11", source=EVIL)
    rec("AP-R5_registration_equivocation", accept_binary(B11, world(add=[G11x]), AN, NOW),
        "23 §12.2: two registrations for one release refuse", "REGISTRATION_EQUIVOCATION", True, "A", mutant="R5-registration-equivocation")
    rec("AP-R5_target_not_registered", accept_binary(binary("B11arm", "4.1.11", TBM9, target="aarch64-linux"),
                                                     world(replace={"t11": t11_with(arts=["g11", "B11arm"])}, add=[repro("rparm1", "4.1.11", "B11arm", "tbm-f11", target="aarch64-linux", signers=("p1",)),
                                                                                                                   repro("rparm2", "4.1.11", "B11arm", "tbm-f11", target="aarch64-linux", signers=("p2",))]), AN, NOW),
        "25 AP-5: the target must be registered", "TARGET_NOT_REGISTERED", True, "A", mutant="R5-target")
    F11s = m.release("F11s", 11, promoted_from="C11", source=OTHER, refs=(9, 2, 1))
    G11s = rrs("g11", "4.1.11", 11, "F11s", "C11")
    TBM9s = m.tbm("tbm-f11", 2, "TPS2", 9, "t9", "F11s")
    rec("AP-R5_final_source_differs_from_registration", accept_binary(binary("B11", "4.1.11", TBM9s), world(replace={"g11": G11s}, add=[F11s]), AN, NOW),
        "25 AP-5: the registered final must verify with the registered source and candidate (restrictor)", "RELEASE_FINAL_UNVERIFIED", True, "A", mutant="R5-final-restrictor")
    rec("AP-R5_one_statement_two_reproducer_signatures", accept_binary(B11, world(drop=("rp11a", "rp11b"), add=[repro("rp11ab", "4.1.11", "B11", "tbm-f11", signers=("p1", "p2"))]), AN, NOW),
        "25 AP-6: a reproduction is first-person; a statement with two signatures counts for none", "REPRODUCTION_QUORUM_NOT_MET", True, "A", mutant="R5-single-signature")
    rec("AP-R5_one_key_two_statements", accept_binary(B11, world(drop=("rp11b",), add=[repro("rp11a2", "4.1.11", "B11", "tbm-f11", signers=("p1",))]), AN, NOW),
        "25 AP-6: the quorum counts distinct keys, not statements", "REPRODUCTION_QUORUM_NOT_MET", True, "A", mutant="R5-count-statements")
    rec("AP-R5_conflicting_reproduction", accept_binary(B11, world(add=[repro("rp11c", "4.1.11", "B11x", "tbm-f11", signers=("p3",))]), AN, NOW),
        "25 AP-6: any valid reproduction of another digest for the same release and target refuses (availability, not acceptance)", "REPRODUCTION_CONFLICT", True, "A", mutant="R5-conflict")
    rec("AP-R5_revoked_reproduction_not_counted", accept_binary(B11, world(replace={"t11": t11_with(revs=["R7", "rp11b"])}, add=[m.revocation("rvrp", ["rp11b"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4 (CR4-B-10): a revoked reproduction counts for nothing", "REPRODUCTION_QUORUM_NOT_MET", True, "A", mutant="R5-revoked-reproduction-counted")
    rec("AP-R5_revoked_attestation_not_counted", accept_binary(B11, world(replace={"t11": t11_with(revs=["R7", "a11"])}, add=[m.revocation("rva", ["a11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4 (CR4-B-10, RV4-L6): a revoked verification attestation counts for nothing", "VERIFICATION_RECORDS_BELOW_MINIMUM", True, "A", mutant="R5-revoked-attestation-counted")
    TBMo = m.tbm("tbm-f11", 2, "TPS2", 9, "t9", "F11", source=OTHER)
    rec("AP-R5_tbm_source_differs", accept_binary(binary("B11", "4.1.11", TBMo), W11, AN, NOW),
        "25 AP-8: the TBM source must equal the registration", "BINARY_T0_UNVERIFIED", True, "A", mutant="R5-tbm-source")
    rec("AP-R5_tbm_policy_digest_forged", accept_binary(binary("B11", "4.1.11", dict(TBM9, tps_d="TPS2-forged")), W11, AN, NOW),
        "25 AP-8 (P4r4 A27e): every TBM component resolves", "BINARY_T0_UNVERIFIED", True, "A")
    rec("AP-R5_binary_revoked", accept_binary(B11, world(replace={"t11": t11_with(revs=["R7", "B11"])}, add=[m.revocation("rvB", ["B11"], issued_at=NOW - HOUR)]), AN, NOW),
        "25 AP-4: a revoked binary refuses", "BINARY_REVOKED", True, "A")
    G11d = dict(G11, binary="B11-other")
    rec("AP-R5_op9d_registration_names_other_digest", accept_binary(B11, world(replace={"g11": G11d}), AN, NOW),
        "25 AP-6 under OP-9 (d): the digest must equal the registered digest", "BINARY_NOT_REGISTERED", True, "A")
    ROOT_SHARED = root5(extra={"p1": ["reproducer", "verification-attestation"]})
    rec("AP-R5_ftc_reproducer_key_shared", accept_binary(B11, [ROOT_SHARED] + W11[1:], AN, NOW),
        "05 §3 FTC: a reproducer key holding another purpose invalidates the root version", "ROOT_VERSION_INVALID", True, "A", mutant="R5-ftc")
    ROOT_WD = root5(extra={"ra1": ["release-artifact"], "ra2": ["release-artifact"]})
    rec("AP-R5_ftc_withdrawn_purpose_granted", accept_binary(B11, [ROOT_WD] + W11[1:], AN, NOW),
        "05 §3 FTC: granting a withdrawn purpose invalidates the root version", "ROOT_VERSION_INVALID", True, "A")
    # CR4-B-07 option 1: a P1 proof covers only the TSS it names
    T12x = m.tss(12, "t12x", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 60)
    rec("AP-R5_p1_proof_does_not_cover_later_descendant", accept_binary(B11, W11 + [T12x], {"pins": [m.pin(11, "t11", 2)], "vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 5}}}, NOW),
        "24 §4.4 revision 5 (CR4-B-07 option 1): C3 on a descendant issued after the P1 proof needs P2 or P3", "TRUST_STATE_CURRENCY_UNPROVEN", True, "A", mutant="R5-descendant-proof")
    rec("AP-R5_p2_in_gate_fingerprint_covers_descendant", accept_binary(B11, W11 + [T12x], {"pins": [m.pin(11, "t11", 2)], "vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 5}}}, NOW, "a", (12, "t12x")),
        "24 §4.4: an in-gate typed fingerprint of the descendant is a currency proof for it (honest owner-published descendant)", "ACCEPTED", False, "A")
    # ---------------------------------------------------------------- B. VA4 rows re-expressed under revision 5
    F_EVIL = m.release("F-evil", 12, promoted_from="C11", source=EVIL, refs=(11, 2, 1))
    TBM_E = m.tbm("tbm-evil", 2, "TPS2", 11, "t11", "F-evil", source=EVIL)
    B_E12, B_E11 = binary("B-evil", "4.1.12", TBM_E), binary("B-evil", "4.1.11", TBM_E)
    T12e = m.tss(12, "t12", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "B-evil"], issued_at=NOW - HOUR)
    AN12 = anchored(12, "t12")
    WE = W11 + [F_EVIL, T12e]
    rec("VA5-01_RV3-B-A08_final_names_commit_evil_as_new_release", accept_binary(B_E12, WE, AN12, NOW), "VA4 row 1: a release-final key names another source: no registration", "RELEASE_UNREGISTERED", True, "B")
    rec("VA5-01b_RV3-B-A08_binary_claims_the_registered_release", accept_binary(B_E11, WE, AN12, NOW), "VA4 row 1 variant: claiming the registered release: no reproduction quorum for the malicious digest", "REPRODUCTION_QUORUM_NOT_MET", True, "B")
    rec("VA5-03_candidate_rejected", accept_binary(B11, world(add=[m.attest("a11r", "C11", verdict="REJECTED", signers=("va2",))]), AN, NOW), "VA4 row 3", "ARTIFACT_SOURCE_REJECTED", True, "B")
    W_src = world(drop=("a11",), add=[m.attest("a11", "C11", source=OTHER)])
    rec("VA5-04_attestation_names_different_source", accept_binary(B11, W_src, AN, NOW), "VA4 row 4: the listed attestation names another source", "VERIFICATION_RECORDS_BELOW_MINIMUM", True, "B")
    Cp, Fp = m.release("C-prime", 0, stage="candidate", source=EVIL, signers=["kc"]), m.release("F-prime", 14, promoted_from="C-prime", source=EVIL, signers=["kc"])
    ROOT_OP4NO = root5(extra={"kc": ["release-final", "release-candidate"]})
    TBM_P = m.tbm("tbm-p", 2, "TPS2", 11, "t11", "F-prime", source=EVIL)
    WP = [ROOT_OP4NO] + W11[1:] + [Cp, Fp, m.tss(12, "t12", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "B-prime"], issued_at=NOW - HOUR)]
    rec("VA5-05_RV3-D-A03_op4_no_everyday_key", accept_binary(binary("B-prime", "4.1.14", TBM_P), WP, AN12, NOW), "VA4 row 5", "RELEASE_UNREGISTERED", True, "B")
    Fp2 = m.release("F-prime2", 14, promoted_from="C11", source=EVIL, signers=["kc"])
    rec("VA5-06_RV3-D-A03_final_promoted_from_genuine_candidate", accept_binary(binary("B-prime", "4.1.11", m.tbm("tbm-p", 2, "TPS2", 11, "t11", "F-prime2", source=EVIL)), WP + [Fp2], AN12, NOW),
        "VA4 row 6", "REPRODUCTION_QUORUM_NOT_MET", True, "B")
    Cs, As, Fs = m.release("C-s", 0, stage="candidate", source=EVIL, signers=["rc1"]), m.attest("a-s", "C-s", source=EVIL, signers=("va1",)), m.release("F-s", 15, promoted_from="C-s", source=EVIL, signers=["rf1"])
    TBM_S = m.tbm("tbm-s", 2, "TPS2", 11, "t11", "F-s", source=EVIL)
    WS = W11 + [Cs, As, Fs, m.tss(12, "t12", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], atts=["a-s"], arts=["g11", "B11", "B-s"], issued_at=NOW - HOUR)]
    for rid, label in (("VA5-07_route_S_verification_candidate_final_keys", "VA4 row 7 (was a documented ACCEPTED minimum)"),
                       ("VA5-08_route_S_root_registered_source", "VA4 row 8"), ("VA5-09_route_S_verification_threshold_2_one_key", "VA4 row 9"),
                       ("VA5-10_route_S_op4_no", "VA4 row 10 (was a documented ACCEPTED minimum)")):
        rec(rid, accept_binary(binary("B-s", "4.1.15", TBM_S), WS, AN12, NOW), label + ": source selection needs the registration authority", "RELEASE_UNREGISTERED", True, "B")
    T12b = m.tss(12, "t12", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "A-malicious-bytes"], issued_at=NOW - HOUR)
    TBM_B = m.tbm("tbm-b", 2, "TPS2", 11, "t11", "F11", source=GOOD)
    WB = W11 + [T12b, m.artifact("A-malicious-bytes", "F11", TBM_B, signers=["ra1", "ra2"]), m.build_att("A-malicious-bytes", "tbm-b", GOOD, signers=("ba1",))]
    for rid, label in (("VA5-11_route_B_artifact_x2_build_attestation_trust_state", "VA4 row 11 (was a documented ACCEPTED minimum)"),
                       ("VA5-12_route_B_one_artifact_key", "VA4 row 12"), ("VA5-13_route_B_no_build_attestation", "VA4 row 13")):
        rec(rid, accept_binary(binary("A-malicious-bytes", "4.1.11", TBM_B), WB, AN12, NOW), label + ": withdrawn purposes count for nothing; no reproduction quorum", "REPRODUCTION_QUORUM_NOT_MET", True, "B")
    WB1 = W11 + [m.tss(12, "t12", prior=PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "B-bad"], issued_at=NOW - HOUR), repro("rpbad", "4.1.11", "B-bad", "tbm-b", signers=("p3",))]
    rec("VA5-B-prime_one_reproducer_key_trust_state_key_honest_statements_held", accept_binary(binary("B-bad", "4.1.11", TBM_B), WB1, AN12, NOW),
        "RV4-B-A01 re-expressed: one stolen reproducer key", "REPRODUCTION_QUORUM_NOT_MET", True, "B")
    WB2 = WB1 + [repro("rpbad2", "4.1.11", "B-bad", "tbm-b", signers=("p1",))]
    rec("VA5-B-prime2_two_reproducer_keys_honest_reproductions_held", accept_binary(binary("B-bad", "4.1.11", TBM_B), WB2, AN12, NOW),
        "CS5 G_BYTES: two stolen reproducer keys with the honest reproductions visible", "REPRODUCTION_CONFLICT", True, "B")
    # ---------------------------------------------------------------- B. P4r4 binary scenarios re-expressed (RV3-D-A13, RV3-D-A15)
    rec("RV3-D-A13r5_realisable_order_new_binary", accept_binary(B11, W11, AN, NOW), "25 AP-8 realisable construction: TBM names t9; t11 publishes", "ACCEPTED", False, "B")
    rec("RV3-D-A13r5_older_binary_after_newer", accept_binary(B11, W11, anchored(tbm_hw=(1, 2, 10)), NOW), "RV3-M8 / A7", "BINARY_T0_ROLLBACK", True, "B")
    T4b = m.tss(4, "t4", prior=[(1, "t1")], pol=(2, "TPS2"))
    T5b = m.tss(5, "t5", prior=[(1, "t1"), (4, "t4")], pol=(2, "TPS2"), arts=["g7", "B7x"])
    T9b = m.tss(9, "t9", prior=[(1, "t1"), (4, "t4"), (5, "t5")], pol=(2, "TPS2"), arts=["g7", "B7x"], revs=["rvA"])
    T10b = m.tss(10, "t10", prior=[(1, "t1"), (4, "t4"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), arts=["g7", "B7x"], revs=["rvA"])
    T100b = m.tss(100, "t100", prior=[(1, "t1"), (4, "t4"), (5, "t5")], pol=(2, "TPS2"), arts=["g7", "B7x"])
    C7, F7 = m.release("C7x", 0, stage="candidate"), m.release("F7x", 7, promoted_from="C7x")
    G7 = rrs("g7", "4.1.7", 7, "F7x", "C7x", vrecs=("a7x",))
    TBMx = m.tbm("tbmx", 2, "TPS2", 4, "t4", "F7x")
    B7x = binary("B7x", "4.1.7", TBMx)
    base15 = [ROOT5, m.TPS1, m.TPS2, m.tss(1, "t1"), T4b, T5b, C7, F7, m.attest("a7x", "C7x"), G7, repro("r7a", "4.1.7", "B7x", "tbmx", signers=("p1",)), repro("r7b", "4.1.7", "B7x", "tbmx", signers=("p2",))]
    a15 = {"honest_current_pin_t10": accept_binary(B7x, base15 + [T9b, T10b, m.revocation("rvA", ["B7x"])], {"pins": [m.pin(10, "t10", 1)]}, NOW),
           "stale_pin_t5_200d_withheld": accept_binary(B7x, base15, {"pins": [m.pin(5, "t5", 200)]}, NOW),
           "valid_pin_t5_20d_withheld": accept_binary(B7x, base15, {"pins": [m.pin(5, "t5", 20)]}, NOW),
           "current_pin_t10_withheld_plus_t100": accept_binary(B7x, base15 + [T100b], {"pins": [m.pin(10, "t10", 1)]}, NOW)}
    rec("RV3-D-A15r5_revoked_binary_pinned_ci", a15, "CD3-2 under AP: a revoked genuine binary is never accepted by an aged, expired or bypassed anchor",
        lambda c: c["honest_current_pin_t10"] == "BINARY_REVOKED" and all(v != "ACCEPTED" for v in c.values()), True, "B")
    # ---------------------------------------------------------------- C. release eligibility under exact per-release registration
    REL11 = {"kind": "release-final", "d": "F11", "release_id": "4.1.11", "seq": 11, "stage": "final", "units": {"leaf:aws": "d-new"}, "refs": {"state": 9, "policy": 2, "root": 1}}
    G11u = dict(G11, units={"leaf:aws": "d-new"})
    WU = world(replace={"g11": G11u})
    rec("E7-00_registered_release_eligible", eligible_release_r5(REL11, WU, AN, NOW), "23 §12: the registered release is eligible", {"eligible": True, "reason": None}, False, "C")
    FORGED12 = dict(REL11, d="F12x", release_id="4.1.12", seq=12, units={"leaf:aws": "d-old"})
    rec("E7-D-A06_git_delivered_forged_final_unregistered", eligible_release_r5(FORGED12, WU + [dict(F11, d="F12x", seq=12)], AN, NOW),
        "D-A06: a Git-delivered higher-sequence final without a registration is ineligible at use", {"eligible": False, "reason": "release_unregistered"}, True, "C", mutant="R5-E7-referenced")
    FORGED11 = dict(REL11, units={"leaf:aws": "d-old"})
    rec("E7-RV4-B-A08_superseded_unit_under_the_registered_release_id", eligible_release_r5(FORGED11, WU, AN, NOW),
        "RV4-H3: content differing from the release's registration is ineligible", {"eligible": False, "reason": "surface_unregistered_for_release"}, True, "C", mutant="R5-E7-units")
    STALE = WU[:]
    STALE = [s for s in STALE if s.get("d") != "t11"]
    rec("E7-stale_machine_without_the_registration", eligible_release_r5(REL11, STALE, anchored(10, "t10"), NOW),
        "23 §12.3 rule 7: knowledge of registrations follows state; the genuine release is ineligible until the referencing TSS is held", {"eligible": False, "reason": "release_unregistered"}, False, "C")
    # ---------------------------------------------------------------- D. carried rules
    tps_eff = m.tps(2)
    long_pin = [{"kind": "framework_update", "digests": ["d1", "d2"], "project": "p1", "provisioned_at": NOW - DAY, "expires_at": NOW + 3650 * DAY}]
    rec("GATE-CR4-B-09_decision_pin_beyond_maximum_validity", trust_gate_authorised_r5("framework_update", ["d1", "d2"], "p1", [], long_pin, tps_eff, NOW)["authorised"],
        "27 §3.2 (CR4-B-09): a decision pin whose validity exceeds the maximum authorises nothing", False, True, "D", mutant="R5-decision-pin-max-validity")
    DEV = m.tbm("tbm-dev", 2, "TPS2", 1000000, "t-dev", "F11")
    vts_after_dev = first_run_record({"accepted_tbm": {"root": 1, "tps": 2, "tss": 5}}, DEV, "development", False)
    rec("A7-CR4-B-08_development_binary_does_not_poison_high_water", accept_binary(B11, W11, dict(anchored(), vts=dict(anchored()["vts"], **vts_after_dev)), NOW),
        "25 AP-8 (CR4-B-08): development builds and non-resolving TBMs are never recorded; a later genuine binary is accepted", "ACCEPTED", False, "D", mutant="R5-first-run-record")
    fake_now = NOW - 395 * DAY
    old_world, true_world = clock_worlds()
    stateful = persist_clock_high_water({"vts": {}}, true_world, NOW)
    mach_fake = {"pins": [dict(m.pin(5, "t5c", 0), provisioned_at=fake_now - 5 * DAY, valid_until=fake_now + 25 * DAY)],
                 "vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 4}, "clock_high_water": stateful["vts"]["clock_high_water"]}}
    rec("CLOCK-RV4-B-A13_stateful_machine_clock_set_back", accept_binary(CLOCK_B7, old_world, mach_fake, fake_now),
        "24 §8 revision 5 (RV4-M4): on a machine with a verifier trust store every ingested non-future statement raises the clock high-water; a clock set back below it fails closed", "TRUST_STATE_UNANCHORED", True, "D", mutant="R5-clock-high-water")
    # ---------------------------------------------------------------- E. distinguishing scenarios for the thirteen retained P4r4 rules (D-A03)
    thief = m.tss(11, "t11x", prior=PRIOR10, pol=(2, "TPS2"), revs=[], issued_at=NOW - HOUR)
    Ki = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.R7, thief]
    _, tsi, fri, _ = m.evaluate_machine(Ki, {"pins": [m.pin(10, "t10", 1)], "vts": {}}, NOW, "a")
    rec("RET-D-inclusion-without-held", {"trust_state": tsi["status"], "allowed": fri["allowed"]}, "24 §3.4 rule 1: the anchored statement must be held",
        {"trust_state": tsi["status"], "allowed": ["C0"]} if fri["axis"].startswith("BELOW") else {"trust_state": "unexpected", "allowed": []}, True, "E", mutant="D-inclusion-without-held")
    t12u = m.tss(12, "t12u", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - HOUR)
    tsu = m.trust_state(m.ingest([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, t12u], {}, NOW)[0], [{"seq": 10, "digest": "t10"}])
    rec("RET-D-unchained-above-anchor-not-regression", tsu["status"], "24 §3.4 rule 4: unchained statements above the anchor make the state REGRESSION", "REGRESSION", True, "E", mutant="D-unchained-above-anchor-not-regression")
    _, tsb, frb, _ = m.evaluate_machine([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.R7], {"vts": {"anchors": [{"seq": 10, "digest": "t10", "at": NOW - DAY, "method": "human"}]}}, NOW, "a")
    rec("RET-D-below-anchor-allows-C1", frb["allowed"], "24 §4.3: BELOW_ANCHOR allows C0 only", ["C0"], True, "E", mutant="D-below-anchor-allows-C1")
    _, tsp, frp, _ = m.evaluate_machine([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.R7], {"pins": [m.pin(5, "t5", 100, validity_days=400)], "vts": {}}, NOW, "a")
    rec("RET-D-pin-validity-cap-not-checked", frp["allowed"], "24 §3.2: a pin beyond pin_max_validity_days is not an anchor", ["C0"], True, "E", mutant="D-pin-validity-cap-not-checked")
    _, tsw, frw, _ = m.evaluate_machine([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, m.witness("w5", 5, "t5", NOW - HOUR, NOW + DAY)], {"vts": {}}, NOW, "c")
    rec("RET-D-witness-for-any-tss", frw["allowed"], "24 §3.3: a witness counts only when it names the effective TSS", ["C0"], True, "E", mutant="D-witness-for-any-tss")
    _, tsr, frr, _ = m.evaluate_machine([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, m.witness("w10", 10, "t10", NOW - 2 * HOUR, NOW + DAY)], {"vts": {"highest_witness_issued_at": NOW - HOUR}}, NOW, "c")
    rec("RET-D-witness-replay-not-refused", frr["allowed"], "24 §3.3: a witness older than the newest accepted witness is refused", ["C0"], True, "E", mutant="D-witness-replay-not-refused")
    t11i = m.tss(11, "t11i", prior=PRIOR10, root_v=2, pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - HOUR)
    _, tsn, frn, _ = m.evaluate_machine([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, t11i], m.human(10, "t10", 1), NOW, "a")
    rec("RET-D-c2-on-incomplete", {"state": tsn["status"], "allowed": frn["allowed"]}, "24 §4.3: INCOMPLETE refuses C2", {"state": "INCOMPLETE", "allowed": ["C0", "C1"]}, True, "E", mutant="D-c2-on-incomplete")
    t10a = m.tss(10, "t10a", prior=[(1, "t1"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), revs=["R7"], arts=["B7"], issued_at=NOW - 2 * DAY)
    t11d = m.tss(11, "t11d", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10a")], pol=(2, "TPS2"), revs=["R7"], arts=[], issued_at=NOW - DAY)
    tsa = m.trust_state([m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, t10a, t11d, m.RV7], ())
    rec("RET-D-admissibility-ignores-artifacts", {"trust_state": tsa["status"], "effective_tss": tsa["effective_tss"]}, "17 S4 (d): a TSS never drops a published reference (registrations[], published_binaries[])",
        {"trust_state": "REGRESSION", "effective_tss": "t10a"}, True, "E", mutant="D-admissibility-ignores-artifacts")
    s3 = m.tps_state([m.ROOT1, m.TPS1, m.TPS2, m.tps(3, prior=[(1, "TPS1")], min_seq=1)])
    rec("RET-D-tps-prior-chain-not-checked", s3["status"], "17 S3: a top TPS must chain every held lower TPS", "EQUIVOCATION", True, "E", mutant="D-tps-prior-chain-not-checked")
    Fl = m.release("F20", 20, promoted_from="C20", source=GOOD)
    Kl = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, Fl, m.attest("a20", "C20"), m.cert("wd20", "F20", "WITHDRAWN", 2, att="a20"), m.attest("a20b", "C20", lifts_negative="wd20"),
          m.cert("c20b", "F20", "CERTIFIED", 3, att="a20b"), m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], certs=[("F20", "c20b")], atts=["a20"], issued_at=NOW - HOUR)]
    tsl = m.trust_state(Kl, ())
    rec("RET-D-lift-attestation-not-TSS-referenced", "F20" in m.negative_set(Kl, tsl, m.tps_state(Kl)["eff"]), "17 MS-2: the lifting attestation must be referenced by the effective TSS", True, True, "E", mutant="D-lift-attestation-not-TSS-referenced")
    rec("RET-D-op7-order-c-above-a", m.accept_policy(m.tps(3, fields={"op7_mode": "a"}), m.tps(4, fields={"op7_mode": "c"}), 3)["accepted"], "19 §10.6: op7_mode (a) -> (c) is a computed reduction", False, True, "E", mutant="D-op7-order-c-above-a")
    rec("RET-D-decision-pin-expiry-not-checked", m.trust_gate_authorised("framework_update", ["d1", "d2"], "p1", [], [{"kind": "framework_update", "digests": ["d1", "d2"], "project": "p1", "expires_at": NOW - DAY}], tps_eff, NOW)["authorised"],
        "27 §3.2: an expired decision pin authorises nothing", False, True, "E", mutant="D-decision-pin-expiry-not-checked")
    rec("RET-D-local-terminal-only-ignored", m.trust_gate_authorised("downgrade", ["d1", "d2"], "p1", [], [{"kind": "downgrade", "digests": ["d1", "d2"], "project": "p1", "expires_at": NOW + DAY}], tps_eff, NOW)["authorised"],
        "27 §3.2: a decision pin never approves a local_terminal_only kind", False, True, "E", mutant="D-local-terminal-only-ignored")
    return S


def clock_worlds():
    """RV4-B-A13 shape: a genuine binary B7c published at t5c, revoked at t9c (issued 10 days before true time). The attacker
    sets the clock back 395 days and delivers only the pre-revocation statements."""
    C7c, F7c, A7c = m.release("C7c", 0, stage="candidate", issued_at=NOW - 900 * DAY), m.release("F7c", 7, promoted_from="C7c", issued_at=NOW - 900 * DAY), m.attest("a7c", "C7c", issued_at=NOW - 900 * DAY)
    G7c = dict(rrs("g7c", "4.1.7c", 7, "F7c", "C7c", vrecs=("a7c",)), issued_at=NOW - 900 * DAY)
    t4c = m.tss(4, "t4c", prior=[(1, "t1")], pol=(2, "TPS2"), issued_at=NOW - 900 * DAY)
    t5c = m.tss(5, "t5c", prior=[(1, "t1"), (4, "t4c")], pol=(2, "TPS2"), arts=["g7c", "B7c"], issued_at=NOW - 800 * DAY)
    t9c = m.tss(9, "t9c", prior=[(1, "t1"), (4, "t4c"), (5, "t5c")], pol=(2, "TPS2"), arts=["g7c", "B7c"], revs=["rvB7c"], issued_at=NOW - 10 * DAY)
    reps = [dict(repro("r7c1", "4.1.7c", "B7c", "tbm7c", signers=("p1",)), issued_at=NOW - 850 * DAY), dict(repro("r7c2", "4.1.7c", "B7c", "tbm7c", signers=("p2",)), issued_at=NOW - 850 * DAY)]
    old = [ROOT5, m.TPS1, m.TPS2, dict(m.T1, issued_at=NOW - 950 * DAY), t4c, t5c, C7c, F7c, A7c, G7c] + reps
    return old, old + [t9c, m.revocation("rvB7c", ["B7c"], issued_at=NOW - 10 * DAY)]


CLOCK_B7 = binary("B7c", "4.1.7c", m.tbm("tbm7c", 2, "TPS2", 4, "t4c", "F7c"))


RETAINED_EXCLUDED = {"A27_release_final_key_signs_artifact", "A27b_one_release_artifact_key", "A27c_no_build_attestation", "A27d_not_referenced_by_trust_state",
                     "A27e_compiled_policy_digest_not_signed_policy", "A28_genuine_older_binary_below_accepted_tbm", "A29_op4_no_candidate_final_key_signs_artifact",
                     "A_valid_realisable_TBM_t9_reference_t11", "RV3-B-A08_final_names_unverified_source", "RV3-D-A13_realisable_tbm_order", "RV3-D-A15_revoked_binary_pinned_ci",
                     "K2_release_artifact_with_release_final"}


def residual_demonstrations():
    """Not oracle rows: stated residuals whose accepted outcome is the residual itself (`24` §10 RS-2)."""
    fake_now = NOW - 395 * DAY
    old_world, _ = clock_worlds()
    stateless = {"pins": [dict(m.pin(5, "t5c", 0), provisioned_at=fake_now - 5 * DAY, valid_until=fake_now + 25 * DAY)], "vts": {"accepted_tbm": {"root": 1, "tps": 2, "tss": 4}}}
    return {"RS-2_stateless_runner_clock_set_back_pin_honoured": {"accept_revoked_binary_on_stateless_runner": accept_binary(CLOCK_B7, old_world, stateless, fake_now),
                                                                   "note": "TA-7 residual restated (CR4-B-03): without a verifier trust store only the local clock bounds pin validity and the C3 window"}}


def main():
    new = run_scenarios()
    retained = m.run_scenarios()
    ret = {k: {"holds": v["holds"], "claim": v["claim"]} for k, v in retained.items() if k not in RETAINED_EXCLUDED}
    attack_accepted = [k for k, v in new.items() if v["attack"] and v["expected"] == "ACCEPTED"]
    summary = {"retained_p4r4_scenarios": len(ret), "retained_holding": sum(v["holds"] for v in ret.values()), "retained_failing": sorted(k for k, v in ret.items() if not v["holds"]),
               "superseded_p4r4_binary_scenarios": sorted(RETAINED_EXCLUDED),
               "revision_5_scenarios": len(new), "revision_5_holding": sum(v["holds"] for v in new.values()), "revision_5_failing": sorted(k for k, v in new.items() if not v["holds"]),
               "expected_ACCEPTED_rows_that_are_attacks": attack_accepted, "honest_controls": sorted(k for k, v in new.items() if not v["attack"]),
               "scenarios_naming_a_mutant": sum(1 for v in new.values() if v.get("mutant")), "params": P5}
    print(json.dumps({"summary": summary, "scenarios": new, "retained_p4r4_scenarios": ret, "residual_demonstrations_not_oracle_rows": residual_demonstrations()},
                     indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))


if __name__ == "__main__":
    main()
