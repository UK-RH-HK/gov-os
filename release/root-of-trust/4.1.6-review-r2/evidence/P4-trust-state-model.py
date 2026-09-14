#!/usr/bin/env python3
"""P4 — Reference model of the RoT-1 revision 2 trust-state and eligibility rules, used to falsify their stated bounds.

This is not an implementation of Governance OS. It encodes the normative text of `17` §5 (S2–S9), `17` §6 and
`19` §5, §6 and §10 step 6 as literally as possible. Signatures are assumed valid, so only the decision logic is tested.
Each scenario prints the value the text produces, the pack's claim, and whether they agree.
"""
import json

MAX = 2 ** 53 - 1


# ---------------------------------------------------------------- statements (already verified; purpose = signing purpose)
def rel(d, seq, purpose="release-final", tss=1, tps=1, root=1, stage="final", floors=None):
    return {"kind": "release", "digest": d, "purpose": purpose, "sequence": seq, "stage": stage,
            "trust_references": {"trust_state_sequence": tss, "trust_policy_version": tps, "root_version": root}, "floors": floors or {}}


def cert(d, target, status, cseq, tss=1, att=None):
    return {"kind": "certification", "digest": d, "purpose": "certification-status", "release": target, "status": status,
            "certification_sequence": cseq, "issued_under": {"trust_state_sequence": tss}, "attestation": att}


def revo(d, target, effect="refuse_install"):
    return {"kind": "revocation", "digest": d, "purpose": "revocation", "targets": [{"digest": target, "effect": effect}]}


def tss(d, seq, prev=None, revs=(), certs=(), atts=(), root=1, tps=1):
    return {"kind": "tss", "digest": d, "purpose": "trust-state", "sequence": seq, "previous_state_digest": prev, "revocations": list(revs),
            "certifications": list(certs), "attestations": list(atts), "references": {"root_version": root, "trust_policy": {"policy_version": tps}}}


def tpsm(v, floors, min_seq, lowers=(), min_bin="4.1.6"):
    return {"kind": "tps", "digest": f"tps{v}", "purpose": "trust-policy", "policy_version": v, "floors": floors,
            "eligibility": {"min_release_sequence": min_seq, "min_binary_version": min_bin}, "lowers": list(lowers), "unrevokes": []}


# ---------------------------------------------------------------- 17 §5
def admissible(T, K):
    """S4 (a)-(f)."""
    by_digest = {s["digest"]: s for s in K}
    for L in (s for s in K if s["kind"] == "tss" and s["sequence"] < T["sequence"]):
        if not set(T["revocations"]) >= set(L["revocations"]):
            return False, "a:revocations"
        tc = {c[0]: by_digest.get(c[1], {}).get("certification_sequence", -1) for c in T["certifications"]}
        for rd, cd in L["certifications"]:
            if tc.get(rd, -1) < by_digest.get(cd, {}).get("certification_sequence", -1):
                return False, "b:certification_sequence"
        if T["references"]["root_version"] < L["references"]["root_version"]:
            return False, "c:root_version"
        if T["references"]["trust_policy"]["policy_version"] < L["references"]["trust_policy"]["policy_version"]:
            return False, "d:policy_version"
        if not set(T["attestations"]) >= set(L["attestations"]):
            return False, "e:attestations"
    if T["previous_state_digest"] in by_digest and by_digest[T["previous_state_digest"]]["sequence"] != T["sequence"] - 1:
        return False, "f:chain"
    return True, None


def effective(K, compiled_root=1):
    tsses = sorted((s for s in K if s["kind"] == "tss"), key=lambda s: s["sequence"])
    adm = [(t, admissible(t, K)) for t in tsses]
    ok = [t for t, (a, _) in adm if a]
    regress = [(t["digest"], why) for t, (a, why) in adm if not a and ok and t["sequence"] > max(x["sequence"] for x in ok)]
    top_seq = max((t["sequence"] for t in ok), default=0)
    eff_tss = [t["digest"] for t in ok if t["sequence"] == top_seq]  # "the highest admissible": may be more than one
    tps = max((s for s in K if s["kind"] == "tps"), key=lambda s: s["policy_version"])
    root = compiled_root
    # S5 negative set
    N = set()
    for s in K:
        if s["kind"] == "revocation":
            N |= {t["digest"] for t in s["targets"]}
    top = {}
    for c in (s for s in K if s["kind"] == "certification"):
        if c["release"] not in top or c["certification_sequence"] > top[c["release"]]["certification_sequence"]:
            top[c["release"]] = c
    N |= {r for r, c in top.items() if c["status"] in ("REJECTED", "WITHDRAWN")}
    # S7 signed required minimums (every release statement and certification statement in K contributes)
    RM_state = max([t["sequence"] for t in tsses] + [s["trust_references"]["trust_state_sequence"] for s in K if s["kind"] == "release"]
                   + [s["issued_under"]["trust_state_sequence"] for s in K if s["kind"] == "certification"] + [0])
    RM_root = max([s["trust_references"]["root_version"] for s in K if s["kind"] == "release"] + [t["references"]["root_version"] for t in tsses] + [0])
    RM_policy = max([s["trust_references"]["trust_policy_version"] for s in K if s["kind"] == "release"] + [t["references"]["trust_policy"]["policy_version"] for t in tsses] + [0])
    stale = (top_seq < RM_state) or (tps["policy_version"] < RM_policy) or (root < RM_root)
    status = "REGRESSION" if regress else ("STALE" if stale else f"CURRENT_KNOWN({top_seq})")
    return {"effective_tss": eff_tss, "tps": tps["policy_version"], "N": sorted(N), "status": status, "regressions": regress,
            "RM": {"state": RM_state, "policy": RM_policy, "root": RM_root}, "highest_cert": {r: (c["status"], c["certification_sequence"]) for r, c in top.items()}}


def effective_floor(tps, kernel):
    out = {}
    for k, v in tps["floors"].items():
        out[k] = max(v, kernel.get(k, v))  # level_at_least over integers for the model
    return out


def eligible(R, tps, N):
    return R["purpose"] in ("release-final", "release-candidate") and R["stage"] == "final" and R["sequence"] >= tps["eligibility"]["min_release_sequence"] and R["digest"] not in N


results = {}
TPS1 = tpsm(1, {"AUTH.update_apply": 4, "ROLE_FLOOR.x": 4}, min_seq=5)

# B1 — a release-candidate key (lowest custody, "candidates only" blast radius) inflates a signed minimum
K = [TPS1, tss("t1", 1), tss("t2", 2, "t1"), rel("R6", 6, tss=2), rel("C999", 7, purpose="release-candidate", stage="candidate", tss=MAX)]
e1 = effective(K)
K_revoked = K + [revo("rv1", "C999")]
e1r = effective(K_revoked)
results["B1_inflated_reference_by_candidate_key"] = {
    "status_after": e1["status"], "RM_state": e1["RM"]["state"], "status_after_revoking_that_candidate": e1r["status"],
    "pack_claim": "05 §1: release-candidate theft = candidates only, never production-eligible; 17 §7: no override for STALE at ingress",
    "agrees": e1["status"] != "STALE" and e1r["status"] != "STALE"}

# B2 — the certification key alone lifts a sticky WITHDRAWN (MS-2 'lifted only by a higher-sequence certification from the owner')
K = [TPS1, tss("t1", 1, certs=[("R6", "c1")]), rel("R6", 6), cert("c1", "R6", "CERTIFIED", 1, att="a1"), cert("c2", "R6", "WITHDRAWN", 2)]
before = effective(K)
K2 = K + [cert("c3", "R6", "CERTIFIED", 3)]  # no attestation, not referenced by any TSS
after = effective(K2)
results["B2_certification_key_alone_unwithdraws"] = {
    "R6_in_negative_set_before": "R6" in before["N"], "R6_in_negative_set_after": "R6" in after["N"], "highest_cert_after": after["highest_cert"],
    "pack_claim": "17 MS-2 negative facts sticky; 17 §3 a visible CERTIFIED needs three signatures; refuse_known_withdrawn refuses",
    "agrees": "R6" in after["N"]}

# B3 — trust-state equivocation: two TSS with the same sequence (fork)
K = [TPS1, tss("t1", 1, revs=["rv1"]), revo("rv1", "R5"), tss("t2a", 2, "t1", revs=["rv1", "rv2"]), revo("rv2", "R6"), tss("t2b", 2, "t1", revs=["rv1"])]
e3 = effective(K)
results["B3_same_sequence_fork"] = {
    "effective_tss": e3["effective_tss"], "status": e3["status"], "fork_reported": False,
    "pack_claim": "17 §3 hash-chained trust state; S4 'Effective TSS = the highest admissible' (singular)",
    "agrees": len(e3["effective_tss"]) == 1}

# B4 — a trust-state key thief inflates references; every later honest TSS becomes a 'regression' (use-time mutation freeze)
K = [TPS1, tss("t1", 1), tss("t2x", 2, "t1", root=999, tps=999), tss("t3", 3, "t2x")]
e4 = effective(K)
results["B4_trust_state_key_inflates_references"] = {
    "status": e4["status"], "regressions": e4["regressions"],
    "pack_claim": "05 §1: trust-state theft = withholding (freeze) only; regressions rejected",
    "agrees": e4["status"] != "REGRESSION" and "STALE" not in e4["status"]}

# B5 — fresh verifier with an older binary (compiled TPS v1) on a project last installed under TPS v3, after A2 swaps in an
#      older authentic eligible release and removes governance/trust/state (RR-2 / RS-1)
TPS3 = tpsm(3, {"AUTH.update_apply": 4, "ROLE_FLOOR.x": 5}, min_seq=8, min_bin="4.1.8")
K_honest = [TPS1, TPS3, tss("t1", 1), tss("t9", 9, root=1, tps=3), rel("R8", 8, tss=9, tps=3, floors={"ROLE_FLOOR.x": 5})]
K_fresh_after_A2 = [TPS1, tss("t1", 1), rel("R6", 6, tss=1, tps=1, floors={"ROLE_FLOOR.x": 4})]  # PTR, TPS v3 and R6's revocation stripped
h = effective(K_honest); f = effective(K_fresh_after_A2)
tps_f = max((s for s in K_fresh_after_A2 if s["kind"] == "tps"), key=lambda s: s["policy_version"])
tps_h = max((s for s in K_honest if s["kind"] == "tps"), key=lambda s: s["policy_version"])
results["B5_fresh_old_binary_after_A2_swap"] = {
    "honest_project": {"tps": h["tps"], "floor_ROLE_FLOOR.x": effective_floor(tps_h, {"ROLE_FLOOR.x": 5})["ROLE_FLOOR.x"], "min_binary_version": tps_h["eligibility"]["min_binary_version"], "R6_eligible": eligible(rel("R6", 6), tps_h, set())},
    "fresh_verifier_after_swap": {"tps": f["tps"], "status": f["status"], "R6_eligible_policy_root": eligible(rel("R6", 6), tps_f, set(f["N"])),
                                  "floor_ROLE_FLOOR.x": effective_floor(tps_f, {"ROLE_FLOOR.x": 4})["ROLE_FLOOR.x"], "min_binary_version_enforced": tps_f["eligibility"]["min_binary_version"], "gate_at_use": False},
    "pack_claim": "20 RR-2: 'Floors and install authority are unaffected'; 19 §10: restoring an older eligible kernel yields floors at least as strong as the newest registered ones; 17 RS-1 bound: 'cannot produce a relaxation (mode A)'",
    "agrees": False}
results["B5_fresh_old_binary_after_A2_swap"]["agrees"] = (
    results["B5_fresh_old_binary_after_A2_swap"]["fresh_verifier_after_swap"]["floor_ROLE_FLOOR.x"] >= 5
    and not results["B5_fresh_old_binary_after_A2_swap"]["fresh_verifier_after_swap"]["R6_eligible_policy_root"])

# B6 — lowering across a skipped policy version (19 §10 step 6 keys the gate on the lowering TPS's own lowers[])
TPS2 = tpsm(2, {"AUTH.update_apply": 4}, min_seq=5)
TPS3L = tpsm(3, {"AUTH.update_apply": 3}, min_seq=5, lowers=["AUTH.update_apply"])
TPS4 = tpsm(4, {"AUTH.update_apply": 3, "NEW.k": 4}, min_seq=6, lowers=[])
known, arriving = TPS2, TPS4
lowered = [k for k, v in known["floors"].items() if arriving["floors"].get(k, v) < v]
declared = [k for k in arriving["lowers"]]
results["B6_lowering_across_skipped_version"] = {
    "verifier_holds": 2, "arrives": 4, "computed_lowered_keys": lowered, "declared_lowers_in_arriving_tps": declared,
    "gate_required_by_text": bool(declared), "pack_claim": "19 §10 step 6: a project holding the stronger policy keeps it until a gate bound to the lowering TPS digest",
    "agrees": bool(declared) or not lowered}

print(json.dumps(results, indent=2))
