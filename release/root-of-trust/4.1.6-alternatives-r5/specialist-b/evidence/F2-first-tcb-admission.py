#!/usr/bin/env python3
"""F2 - anchored, non-circular first TCB admission on every machine (BC4-2) under specialist B's alternative (01 M2).

Computed; no files, no subprocesses. Loads, by path and unmodified:
  * F1-tcb-fact-derivation.py (this directory): the Admission Predicate AP and the release-cycle model;
  * through F1, review r4 reviewer B's reference model (anchors, inclusion, currency, negative set; reproduced
    byte-identical by synthesis D and by this run).

What is modelled
  * `admit`   - the independent admitter (gov-admit): AP evaluated with the independent channel's lineage id and state
                fingerprint (both channels must agree) as the inclusion anchor and currency, over digests it measures itself;
                evaluator identity must differ from the candidate; first admission starts a fresh Verifier Trust Store.
  * `gov_run` - a GENUINE RoT-1 binary: refuses trusted operations and every TA-5 ceremony without a protected Admission
                Record naming its own digest (BINARY_NOT_ADMITTED), refuses when an image record has expired, and refuses
                when the effective negative set it holds names its own digest. A malicious binary ignores all of this
                (stated: TB-1').
  * scenarios   RV4-B-A03 (revoked; remediated compromise), RV4-B-A04 (moved tag, self-report), Phase 4, CI image,
                RV4-D-A04 (ceremonies), channel and admitter substitution, retained review-r3 anchor probes through AP.
  * mutation self-check: each of 12 single-rule mutants of AP/admit must be detected by at least one scenario (RV4-M7 class
    applied to this proposal's new rules).
Output: JSON on stdout.
"""
import importlib.util, itertools, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("f1", os.path.join(HERE, "F1-tcb-fact-derivation.py"))
f1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f1)
bm = f1.bm
NOW, DAY, HOUR = bm.NOW, bm.DAY, bm.HOUR
LINEAGE = "sha256:lineage-genuine"
ADMITTER_DIGEST = "sha256:gov-admit-1.0"
Q = 2

# ------------------------------------------------------------------------------------------------ published world (honest)
SG, SE = f1.SG, f1.SE
ROOT_V1 = f1.make_root()
ROOT_V2 = dict(ROOT_V1, v=2, revoked={"ba1", "ba2"}, grants=dict(ROOT_V1["grants"]))
C20 = bm.CAND("Cg", SG)
AG = [bm.VATT("ag1", "Cg", "ACCEPTED", SG, signers=("va1",)), bm.VATT("ag2", "Cg", "ACCEPTED", SG, signers=("va2",))]
F20 = bm.FINAL("Fg", 20, "Cg", SG)
RAS20 = f1.RAS("ras20", 20, SG, "Fg", signers=("root1", "root3"))
GOOD = "BIN(commit-good)"
TBM_GOOD = bm.TBM("tbm-commit-good", SG, (10, "t10"), embedded="Fg")
BATT_GOOD = [f1.batt("b-ba1", GOOD, TBM_GOOD["d"], SG, "ba1"), f1.batt("b-ba2", GOOD, TBM_GOOD["d"], SG, "ba2")]
EVIL = "BIN(malicious-bytes)"
TBM_EVIL = bm.TBM("tbm-evil", SG, (10, "t10"), embedded="Fg")
BATT_EVIL = [f1.batt("bx-ba1", EVIL, TBM_EVIL["d"], SG, "ba1"), f1.batt("bx-ba2", EVIL, TBM_EVIL["d"], SG, "ba2")]
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]
BASE = [bm.TPS1, bm.TPS2, bm.T1, bm.T5, bm.T9, bm.T10, bm.RV9]
REL20 = [C20, F20, RAS20] + AG


def tss(seq, d, prior, arts, atts, revs=("R7", "B7"), root_ref=1, issued=None):
    t = bm.TSS(seq, d, prior, NOW - (issued if issued is not None else HOUR), revs=list(revs), arts=list(arts), atts=list(atts))
    t["root_ref"] = root_ref
    return t


T11 = tss(11, "t11", PRIOR10, ["B7", GOOD], ["a7", "ag1", "ag2", "ras20"], issued=20 * DAY)
PRIOR11 = PRIOR10 + [(11, "t11")]
T12_REVOKES_GOOD = tss(12, "t12", PRIOR11, ["B7", GOOD], ["a7", "ag1", "ag2", "ras20"], revs=["R7", "B7", GOOD], issued=2 * DAY)
REV_GOOD = bm.REV("rv-good", [GOOD], NOW - 2 * DAY)
# remediated compromise (05 §9 shape): EVIL was once referenced (t11e), then root v2 revokes ba1/ba2 and t12e revokes EVIL
T11E = tss(11, "t11e", PRIOR10, ["B7", EVIL], ["a7", "ag1", "ag2", "ras20"], issued=20 * DAY)
T12E = tss(12, "t12e", PRIOR10 + [(11, "t11e")], ["B7", EVIL], ["a7", "ag1", "ag2", "ras20"], revs=["R7", "B7", EVIL], root_ref=2, issued=2 * DAY)
REV_EVIL = bm.REV("rv-evil", [EVIL], NOW - 2 * DAY)


def fp(t):
    return (t["seq"], t["d"])


# ------------------------------------------------------------------------------------------------ AP with mutant switches (identical to F1 when mutant is None)
def ap(binary_d, tbm, K_all, victim, root, legit="L1", q=Q, mutant=None):
    plain = [s for s in K_all if s["kind"] != "ras"]
    r, K, ts = bm.assess(plain, dict(victim, root=root), "a")
    eff = ts.get("eff")
    if mutant != "no_root_ref_resolution" and eff and eff.get("root_ref", 1) > root["v"]:
        return "TRUST_STATE_INCOMPLETE(root_reference_unresolved)"
    if mutant == "no_anchor_inclusion":
        r, K, ts = bm.assess(plain, dict(victim, root=root, human=[], pins=[]), "d")   # the tooling path of revision 4: no anchor
        eff = ts.get("eff")
        r = dict(r, allowed=["C0", "C1", "C2", "C3"])
    if ts["status"] in ("EQUIVOCATION", "REGRESSION", "BELOW_ANCHOR", "ANCHOR_CONFLICT"):
        return "TRUST_STATE_" + ts["status"]
    F = next((s for s in K if s["kind"] == "final" and s["d"] == tbm["embedded"]), None)
    if F is None:
        return "ARTIFACT_IDENTITY_MISMATCH"
    C = next((s for s in K if s["kind"] == "candidate" and s["d"] == F["promoted_from"]), None)
    if mutant != "no_V8" and (C is None or C["source"] != F["source"] or C["tree"] != F["tree"]):
        return "RELEASE_IDENTITY_MISMATCH(source)"
    if C is None:
        C = {"d": F["promoted_from"], "source": F["source"], "tree": F["tree"]}
    if mutant != "no_tbm_source" and tbm["source"] != C["source"]:
        return "ARTIFACT_SOURCE_MISMATCH"
    bk = f1.keys_of([b for b in K if b["kind"] == "batt" and b["artifact"] == binary_d and b["tbm"] == tbm["d"] and b["source"] == tbm["source"]], root)
    if len(bk) < (1 if mutant == "quorum_1" else q):
        return "ARTIFACT_BUILD_QUORUM_NOT_MET"
    if mutant != "no_single_valued":
        others = {b["artifact"] for b in K if b["kind"] == "batt" and b["artifact"] != binary_d
                  and len(f1.keys_of([x for x in K if x["kind"] == "batt" and x["artifact"] == b["artifact"]], root)) >= q}
        if others:
            return "ARTIFACT_EQUIVOCATION"
    if any(a for a in K if a["kind"] == "vatt" and a["candidate"] == C["d"] and a["verdict"] == "REJECTED") and mutant != "no_rejected":
        return "ARTIFACT_SOURCE_REJECTED"
    ras_all = [s for s in K_all if s["kind"] == "ras" and f1.ras_valid(s)]
    if legit == "L1" and mutant != "no_legitimacy":
        ras = [s for s in ras_all if s["source"] == C["source"] and s["final"] == F["d"]]
        if not ras:
            return "ARTIFACT_SOURCE_NOT_ADMITTED"
        if not eff or not any(s["d"] in eff["atts"] for s in ras):
            return "ARTIFACT_ADMISSION_UNREFERENCED"
    if mutant != "no_reference" and (not eff or binary_d not in eff["arts"]):
        return "ARTIFACT_UNREFERENCED"
    N = bm.negatives(K)
    if mutant != "no_negative_set" and (binary_d in N or F["d"] in N or C["d"] in N):
        return "ARTIFACT_REVOKED"
    if mutant != "no_currency" and "C3" not in r["allowed"]:
        return "TRUST_STATE_NOT_C3(" + str(r.get("freshness")) + ")"
    return "ACCEPTED"


def admit(candidate_bytes_digest, tbm, served, channels, root_served, evaluator=ADMITTER_DIGEST, admitter_channel_digest=ADMITTER_DIGEST,
          now=NOW, mutant=None):
    """Independent admitter: channels = [{'lineage':..., 'fingerprint': (seq, d), 'admitter': digest}, ...] (>= 2 channels)."""
    if mutant != "no_admitter_check" and evaluator != admitter_channel_digest:
        return "ADMITTER_DIGEST_MISMATCH", None
    if mutant != "self_evaluation_allowed" and evaluator == candidate_bytes_digest:
        return "SELF_EVALUATION_REFUSED", None
    if mutant != "single_channel" and len({(c["lineage"], c["fingerprint"]) for c in channels}) != 1:
        return "CHANNEL_DISAGREEMENT", None
    ch = channels[0]
    if ch["lineage"] != root_served.get("lineage", LINEAGE):
        return "TRUST_ROOT_LINEAGE_MISMATCH", None
    seq, d = ch["fingerprint"]
    victim = {"human": [{"seq": seq, "d": d, "at": now}]}                     # fresh VTS; anchor and P2-equivalent currency from the channel read now
    res = ap(candidate_bytes_digest, tbm, served, victim, root_served, mutant=mutant)
    record = {"binary": candidate_bytes_digest, "fingerprint": ch["fingerprint"], "lineage": ch["lineage"], "admitted_at": now, "admitter": evaluator} if res == "ACCEPTED" else None
    return res, record


def gov_run(binary_digest, genuine, action, records, negatives_held=(), now=NOW, record_protected=True, mutant=None):
    """What the binary does when started. `action` in {'C0', 'C1', 'C2', 'C3', 'confirm-root', 'confirm-state'}."""
    if not genuine:
        return "RUNS (malicious binary ignores every rule; TB-1')"
    if action == "C0" and mutant != "C0_gated":
        return "RUNS"
    recs = [r for r in records if r and r["binary"] == binary_digest and (record_protected or mutant == "writable_record_ok")]
    if mutant != "no_admission_record_rule":
        if not recs:
            return "BINARY_NOT_ADMITTED"
        if all(r.get("valid_until") is not None and now > r["valid_until"] for r in recs):
            return "ADMISSION_RECORD_EXPIRED"
    if mutant != "no_self_revocation" and binary_digest in set(negatives_held):
        return "BINARY_REVOKED_SELF"
    return "RUNS"


CH_GOOD_T12 = [{"lineage": LINEAGE, "fingerprint": fp(T12_REVOKES_GOOD), "admitter": ADMITTER_DIGEST}] * 2
CH_GOOD_T11 = [{"lineage": LINEAGE, "fingerprint": fp(T11), "admitter": ADMITTER_DIGEST}] * 2
CH_T12E = [{"lineage": LINEAGE, "fingerprint": fp(T12E), "admitter": ADMITTER_DIGEST}] * 2
ROOT_V1L = dict(ROOT_V1, lineage=LINEAGE)
ROOT_V2L = dict(ROOT_V2, lineage=LINEAGE)


def scenarios(mutant=None):
    S = {}
    A = lambda *a, **k: admit(*a, mutant=mutant, **k)[0]
    # RV4-B-A03 part 1: genuine binary revoked in t12; transport strips t12 and the revocation
    S["A03_revoked_stripped"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T12, ROOT_V1L), "refuse")
    S["A03_revoked_all_served"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11, T12_REVOKES_GOOD, REV_GOOD], CH_GOOD_T12, ROOT_V1L), "refuse")
    S["control_genuine_current"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "ACCEPTED")
    # RV4-B-A03 part 2: remediated compromise; attacker serves root v1 and pre-remediation state
    S["A03_remediated_root_v1_and_t11e"] = (A(EVIL, TBM_EVIL, BASE + REL20 + BATT_EVIL + [T11E], CH_T12E, ROOT_V1L), "refuse")
    S["A03_remediated_t12e_served_root_v2_withheld"] = (A(EVIL, TBM_EVIL, BASE + REL20 + BATT_EVIL + [T11E, T12E], CH_T12E, ROOT_V1L), "refuse")
    S["A03_remediated_everything_served_revocation_withheld"] = (A(EVIL, TBM_EVIL, BASE + REL20 + BATT_EVIL + [T11E, T12E], CH_T12E, ROOT_V2L), "refuse")
    # RV4-B-A04: binary built from a moved tag (different source) / planted binary reporting a genuine TBM
    moved = "BIN(moved-tag)"
    S["A04_moved_tag_binary"] = (A(moved, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    S["A04_moved_tag_with_TBM_naming_moved_source"] = (A(moved, bm.TBM("tbm-moved", ("commit-moved", "tree-moved", "inputs-good"), (10, "t10"), embedded="Fg"),
                                                     BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    # Phase 4 / self-validation: the candidate as its own evaluator
    S["Phase4_self_evaluation"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L, evaluator=GOOD, admitter_channel_digest=GOOD), "refuse")
    # admitter substitution and channels
    S["admitter_substituted"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L, evaluator="sha256:evil-admitter"), "refuse")
    one_bad = [CH_GOOD_T11[0], {"lineage": LINEAGE, "fingerprint": fp(bm.T10), "admitter": ADMITTER_DIGEST}]
    S["one_channel_serves_stale_fingerprint"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], one_bad, ROOT_V1L), "refuse")
    # retained review-r3 anchor probes through AP (binary acceptance on a machine, not first install)
    rel7 = [bm.CAND("C7g", ("c7", "tree7", "in7")), bm.FINAL("R7g", 7, "C7g", ("c7", "tree7", "in7")), f1.RAS("ras7", 7, ("c7", "tree7", "in7"), "R7g", ("root1", "root3"))]
    b7 = "BIN(r7)"
    tbm7 = bm.TBM("tbm7g", ("c7", "tree7", "in7"), (5, "t5"), embedded="R7g")
    batt7 = [f1.batt("b7-1", b7, "tbm7g", ("c7", "tree7", "in7"), "ba1"), f1.batt("b7-2", b7, "tbm7g", ("c7", "tree7", "in7"), "ba2")]
    t5r = tss(5, "t5", [(1, "t1")], ["B7", b7], ["a7", "ras7"], revs=[], issued=400 * DAY)
    t9r = tss(9, "t9", [(1, "t1"), (5, "t5")], ["B7", b7], ["a7", "ras7"], revs=["R7", "B7", b7], issued=10 * DAY)
    t10r = tss(10, "t10", [(1, "t1"), (5, "t5"), (9, "t9")], ["B7", b7], ["a7", "ras7"], revs=["R7", "B7", b7], issued=DAY)
    t100 = tss(100, "t100", [(1, "t1"), (5, "t5")], ["B7", b7], ["a7", "ras7"], revs=[], issued=HOUR)
    world_strip = [bm.TPS1, bm.TPS2, bm.T1, t5r] + rel7 + batt7
    pin = lambda seq, d, prov_ago, validity=30 * DAY: {"seq": seq, "d": d, "prov": NOW - prov_ago, "until": NOW - prov_ago + validity}
    S["RV3-B-A12_D-A12_trust_state_thief_t100_anchor_t10"] = (ap(b7, tbm7, world_strip + [t100], {"human": [{"seq": 10, "d": "t10", "at": NOW - HOUR}]}, ROOT_V1, mutant=mutant), "refuse")
    S["RV3-D-A15_i_stale_pin_t5_400d"] = (ap(b7, tbm7, world_strip, {"pins": [pin(5, "t5", 400 * DAY)]}, ROOT_V1, mutant=mutant), "refuse")
    S["RV3-D-A15_ii_current_pin_t10_plus_t100"] = (ap(b7, tbm7, world_strip + [t100], {"pins": [pin(10, "t10", HOUR)]}, ROOT_V1, mutant=mutant), "refuse")
    rv7b = bm.REV("rv7b", ["R7", "B7", b7], NOW - 10 * DAY)      # the honest publication carries the revocation statement (17 S5)
    S["RV3-D-A15_control_honest_repository"] = (ap(b7, tbm7, world_strip + [t9r, t10r, rv7b], {"pins": [pin(10, "t10", HOUR)]}, ROOT_V1, mutant=mutant), "refuse")
    # quorum / single-valued / legitimacy / V8 / reference with one mutated input each
    S["one_build_attestation_key"] = (A(EVIL, TBM_EVIL, BASE + REL20 + BATT_EVIL[:1] + [tss(11, "t11", PRIOR10, ["B7", EVIL], ["a7", "ag1", "ag2", "ras20"])],
                                        [{"lineage": LINEAGE, "fingerprint": (11, "t11"), "admitter": ADMITTER_DIGEST}] * 2, ROOT_V1L), "refuse")
    both = tss(11, "t11", PRIOR10, ["B7", EVIL, GOOD], ["a7", "ag1", "ag2", "ras20"])
    S["two_quorum_digests_held"] = (A(EVIL, TBM_EVIL, BASE + REL20 + BATT_EVIL + BATT_GOOD + [both], [{"lineage": LINEAGE, "fingerprint": (11, "t11"), "admitter": ADMITTER_DIGEST}] * 2, ROOT_V1L), "refuse")
    no_ras = [C20, F20] + AG
    S["source_not_root_admitted"] = (A(GOOD, TBM_GOOD, BASE + no_ras + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    F_bad = bm.FINAL("Fg", 20, "Cg", SE)
    S["final_source_differs_from_candidate"] = (A(GOOD, TBM_GOOD, BASE + [C20, F_bad, RAS20] + AG + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    S["tbm_source_differs"] = (A(GOOD, bm.TBM("tbm-commit-good", SE, (10, "t10"), embedded="Fg"), BASE + REL20 + [f1.batt("bq1", GOOD, "tbm-commit-good", SE, "ba1"), f1.batt("bq2", GOOD, "tbm-commit-good", SE, "ba2")] + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    t11u = tss(11, "t11", PRIOR10, ["B7"], ["a7", "ag1", "ag2", "ras20"])
    S["binary_unreferenced"] = (A(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [t11u], [{"lineage": LINEAGE, "fingerprint": (11, "t11"), "admitter": ADMITTER_DIGEST}] * 2, ROOT_V1L), "refuse")
    rej = bm.VATT("aR", "Cg", "REJECTED", SG, signers=("va1",))
    S["rejected_verdict_held"] = (A(GOOD, TBM_GOOD, BASE + REL20 + [rej] + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L), "refuse")
    # genuine binary behaviour (gov_run)
    G = lambda *a, **k: gov_run(*a, mutant=mutant, **k)
    rec = admit(GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11], CH_GOOD_T11, ROOT_V1L)[1]
    S["genuine_revoked_binary_started_without_admitter_C2"] = (G(GOOD, True, "C2", []), "refuse")
    S["D-A04_confirm_state_on_unadmitted_genuine_binary"] = (G(GOOD, True, "confirm-state", []), "refuse")
    S["D-A04_confirm_root_on_unadmitted_genuine_binary"] = (G(GOOD, True, "confirm-root", []), "refuse")
    S["writable_admission_record"] = (G(GOOD, True, "C2", [rec], record_protected=False), "refuse")
    S["admitted_binary_C2"] = (G(GOOD, True, "C2", [rec]), "RUNS")
    S["admitted_binary_C0"] = (G(GOOD, True, "C0", []), "RUNS")
    img = dict(rec, valid_until=NOW + 10 * DAY)
    S["CI_image_record_within_validity_revocation_not_held (RS-1c analogue)"] = (G(GOOD, True, "C2", [img], now=NOW + 5 * DAY), "RUNS")
    S["CI_image_record_expired"] = (G(GOOD, True, "C2", [img], now=NOW + 11 * DAY), "refuse")
    S["CI_image_revocation_held_by_runner"] = (G(GOOD, True, "C2", [img], negatives_held=[GOOD], now=NOW + 5 * DAY), "refuse")
    S["malicious_binary_started_directly (TB-1')"] = (G(EVIL, False, "C3", []), "RUNS (malicious binary ignores every rule; TB-1')")
    return S


def verdict_ok(got, expect):
    if expect == "refuse":
        return got not in ("ACCEPTED", "RUNS")
    return got == expect


MUTANTS = ["no_anchor_inclusion", "no_root_ref_resolution", "no_V8", "no_tbm_source", "quorum_1", "no_single_valued", "no_rejected",
           "no_legitimacy", "no_reference", "no_negative_set", "no_currency", "self_evaluation_allowed", "single_channel", "no_admitter_check",
           "no_admission_record_rule", "writable_record_ok", "no_self_revocation", "C0_gated"]


def main():
    base = scenarios()
    rows = {k: {"observed": v[0], "expected": v[1], "holds": verdict_ok(*v)} for k, v in base.items()}
    # consistency with F1's predicate on the admission rows that do not use F2-only checks
    consistency = []
    for name, args in (("control", (GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11])), ("A03_revoked_all_served", (GOOD, TBM_GOOD, BASE + REL20 + BATT_GOOD + [T11, T12_REVOKES_GOOD, REV_GOOD]))):
        fp_ = fp(T11) if name == "control" else fp(T12_REVOKES_GOOD)
        v = {"human": [{"seq": fp_[0], "d": fp_[1], "at": NOW}]}
        consistency.append({"scenario": name, "F1_predicate": f1.admission_predicate(args[0], args[1], args[2], v, "L1", Q, ROOT_V1), "F2_ap": ap(args[0], args[1], args[2], v, ROOT_V1)})
    mut = []
    for mname in MUTANTS:
        s = scenarios(mname)
        detected = [k for k in s if verdict_ok(*s[k]) != rows[k]["holds"] or s[k][0] != rows[k]["observed"]]
        flipped_to_accept = [k for k in s if rows[k]["holds"] and not verdict_ok(*s[k])]
        mut.append({"mutant": mname, "detected": bool(flipped_to_accept) or bool(detected), "scenarios_now_failing": flipped_to_accept[:6], "observed_changes": len(detected)})
    # first-install capability enumeration (evil bytes): the admitter evaluates the same AP, plus two channels
    caps = ["ba1", "ba2", "ts", "pipeline", "ch1", "ch2"]

    def first_install(combo):
        st = set(combo)
        if {"ch1", "ch2"} <= st:
            return "ACCEPTED"  # attacker lineage and state fingerprint in both channels: TA-5 core
        r, _ = f1.simulate_fe(tuple(c for c in combo if c not in ("ch1", "ch2")), "evil_bytes", legit="L1", q=Q)
        return r
    minimal = []
    for n in range(len(caps) + 1):
        for combo in itertools.combinations(caps, n):
            if any(set(a) <= set(combo) for a in minimal):
                continue
            if first_install(combo) == "ACCEPTED":
                minimal.append(combo)
    out = {"probe": "F2 first TCB admission (AR-0010)", "scenarios": rows,
           "summary": {"scenarios": len(rows), "hold": sum(r["holds"] for r in rows.values()), "failing": [k for k, r in rows.items() if not r["holds"]]},
           "consistency_with_F1_predicate": consistency,
           "mutation_self_check": {"mutants": len(mut), "detected": sum(m["detected"] for m in mut), "undetected": [m["mutant"] for m in mut if not m["detected"]], "rows": mut},
           "first_install_minimal_sets_evil_bytes_L1_q2": [list(x) for x in minimal]}
    print(json.dumps(out, indent=1, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else str(o)))


if __name__ == "__main__":
    main()
