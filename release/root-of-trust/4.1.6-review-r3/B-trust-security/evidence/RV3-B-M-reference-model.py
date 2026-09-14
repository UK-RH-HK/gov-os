#!/usr/bin/env python3
"""RV3-B-M — independent reference model of RoT-1 revision 3 (review r3 B, AR-0002).

Written by this reviewer from the pack text at ca77a43, not from the architect's `evidence/P4r3-trust-state-model.py`
(which was re-run separately and is byte-identical to its committed output). Signatures are assumed valid: only decision
logic is modelled. Rules encoded, with the text they come from:

  17 S2 root; S3 TPS equivocation and prior_policies; S4 (a) resolution, (b) anchored orphans, (c) equivocation,
     (d) admissibility incl. prior_states, supersets of revocations/attestations/artifacts, (e) effective/REGRESSION/INCOMPLETE;
  17 S5 + MS-2 negative set and lifting; S7 release-local references; §13 freshness proof clauses (b)-(d);
  24 §3 anchors (pin, human, witness, retained), §4.3 decision table, §8 monotonic high-water, §9 OP-7 (a)-(d);
  19 §6 E1, E3, E4, E8, E10 (the parts that decide the scenarios);
  25 §5 verify-artifact A2-A9; 05 §3 purposes and the "minimum distinct keys" table; 05 §9 compromise playbook;
  27 §3 trust-gate authorisation (local confirmations; operator decision pins; local_terminal_only).

Assumed parameters the pack leaves to the owner: max_anchor_age_days = 180 (OP-7 b), witness_max_validity_days = 7 (OP-7 c).

Each scenario records `computed`, the pack `claim` it tests, and `claim_holds` (True = the pack statement holds as written).
"""
import json

DAY = 86400
NOW = 3000 * DAY
MAX = 2 ** 53 - 1
PARAMS = {"max_anchor_age_days": 180, "witness_max_validity_days": 7}
LOCAL_TERMINAL_ONLY_DEFAULT = {"downgrade", "policy_lowering", "adopt_lineage", "override_kernel_integrity"}


# ============================================================================================== statements
def root(v):
    return {"kind": "root", "v": v, "d": f"ROOT{v}", "issued_at": 0}


def tps(v, prior=(), min_seq=1, lowering_history=(), unrevokes=(), floors=None, lto=None):
    return {"kind": "tps", "v": v, "d": f"TPS{v}", "prior": set(prior), "min_seq": min_seq, "lowering_history": list(lowering_history),
            "unrevokes": set(unrevokes), "floors": dict(floors or {}), "local_terminal_only": set(lto) if lto is not None else set(LOCAL_TERMINAL_ONLY_DEFAULT), "issued_at": 0}


def tss(seq, d, prior=(), root_v=1, pol=(1, "TPS1"), revs=(), certs=(), atts=(), arts=(), expires_at=None, issued_at=0):
    return {"kind": "tss", "seq": seq, "d": d, "prior": set(prior), "root_v": root_v, "pol": tuple(pol), "revs": set(revs), "certs": set(certs),
            "atts": set(atts), "arts": set(arts), "expires_at": expires_at, "issued_at": issued_at}


def release(d, seq, purpose="release-final", stage="final", refs=(1, 1, 1), commit="commit-good", promoted_from=None, issued_at=0):
    return {"kind": "release", "d": d, "seq": seq, "purpose": purpose, "stage": stage, "refs": {"state": refs[0], "policy": refs[1], "root": refs[2]},
            "release_commit": commit, "promoted_from": promoted_from, "issued_at": issued_at}


def candidate(d, commit, issued_at=0):
    return {"kind": "release", "d": d, "seq": 0, "purpose": "release-candidate", "stage": "candidate", "refs": {"state": 1, "policy": 1, "root": 1},
            "release_commit": commit, "promoted_from": None, "issued_at": issued_at}


def cert(d, rel, status, cseq, att=None, issued_at=0):
    return {"kind": "cert", "d": d, "rel": rel, "status": status, "cseq": cseq, "att": att, "issued_at": issued_at}


def attest(d, cand, verdict="ACCEPTED", issued_at=0):
    return {"kind": "att", "d": d, "candidate": cand, "verdict": verdict, "issued_at": issued_at}


def revocation(d, targets, issued_at=0):
    return {"kind": "revocation", "d": d, "targets": set(targets), "issued_at": issued_at}


# ============================================================================================== 17 S2-S5
def eff_root(K):
    return max([s["v"] for s in K if s["kind"] == "root"] + [1])


def tps_state(K):
    ps = {}
    for p in (s for s in K if s["kind"] == "tps"):
        ps.setdefault(p["v"], {})[p["d"]] = p
    if any(len(x) > 1 for x in ps.values()):
        return {"status": "EQUIVOCATION", "eff": None}
    if not ps:
        return {"status": "NONE", "eff": None}
    vs = sorted(ps)
    top = next(iter(ps[vs[-1]].values()))
    lower = {(v, next(iter(ps[v]))) for v in vs[:-1]}
    if not lower <= top["prior"]:
        return {"status": "EQUIVOCATION", "eff": None, "reason": "prior_policies omits a held lower TPS"}
    return {"status": "OK", "eff": top}


def _cert_seq(K, cd):
    c = next((x for x in K if x["kind"] == "cert" and x["d"] == cd), None)
    return c["cseq"] if c else -1


def _certs_nondecreasing(T, L, K):
    for rel, cd in L["certs"]:
        have = max([_cert_seq(K, c2) for r2, c2 in T["certs"] if r2 == rel] + [-1])
        if have < _cert_seq(K, cd):
            return False
    return True


def tss_state(K, anchor=None):
    er = eff_root(K)
    held_pol = {(s["v"], s["d"]) for s in K if s["kind"] == "tps"}
    uniq = {}
    for t in (s for s in K if s["kind"] == "tss"):
        uniq[(t["seq"], t["d"])] = t
    ts = sorted(uniq.values(), key=lambda t: (t["seq"], t["d"]))
    resolved = [t for t in ts if t["root_v"] <= er and t["pol"] in held_pol]
    unresolved = [t for t in ts if t not in resolved]
    orphans = []
    if anchor and anchor.get("digest"):
        a = next((t for t in resolved if t["seq"] == anchor["seq"] and t["d"] == anchor["digest"]), None)
        if a:
            chain = a["prior"] | {(a["seq"], a["d"])}
            orphans = [t for t in resolved if t["seq"] <= a["seq"] and (t["seq"], t["d"]) not in chain]
            resolved = [t for t in resolved if t not in orphans]
    byseq = {}
    for t in resolved:
        byseq.setdefault(t["seq"], set()).add(t["d"])
    if any(len(v) > 1 for v in byseq.values()):
        return {"status": "EQUIVOCATION", "eff": None, "seq": 0, "orphans": [o["d"] for o in orphans]}
    adm, non = [], []
    for t in resolved:
        ok = all(t["revs"] >= l["revs"] and t["atts"] >= l["atts"] and t["arts"] >= l["arts"] and _certs_nondecreasing(t, l, K)
                 and t["root_v"] >= l["root_v"] and t["pol"][0] >= l["pol"][0] and (l["seq"], l["d"]) in t["prior"] for l in adm)
        (adm if ok else non).append(t)
    eff = adm[-1] if adm else None
    status = "KNOWN"
    if eff and any(n["seq"] > eff["seq"] for n in non):
        status = "REGRESSION"
    inc = [u["seq"] for u in unresolved if eff is None or u["seq"] > eff["seq"]]
    if status == "KNOWN" and inc:
        status = "INCOMPLETE"
    return {"status": status, "eff": eff, "seq": eff["seq"] if eff else 0, "effective_tss": eff["d"] if eff else None,
            "non_admissible": [n["d"] for n in non], "incomplete": inc, "orphans": [o["d"] for o in orphans]}


def negative_set(K, ts, tps_eff):
    eff = ts.get("eff")
    N = set()
    for s in K:
        if s["kind"] == "revocation":
            N |= s["targets"]
    if tps_eff:
        N -= tps_eff["unrevokes"]
    for rel_d in {c["rel"] for c in K if c["kind"] == "cert"}:
        cs = [c for c in K if c["kind"] == "cert" and c["rel"] == rel_d]
        negs = [c for c in cs if c["status"] in ("REJECTED", "WITHDRAWN")]
        if not negs:
            continue
        top = max(c["cseq"] for c in negs)
        R = next((s for s in K if s["kind"] == "release" and s["d"] == rel_d), None)
        lifted = []
        for c in cs:
            if c["status"] == "CERTIFIED" and c["cseq"] > top and eff and (rel_d, c["d"]) in eff["certs"]:
                a = next((x for x in K if x["kind"] == "att" and x["d"] == c["att"] and x["verdict"] == "ACCEPTED"), None)
                if a and a["d"] in eff["atts"] and (R is None or R["promoted_from"] is None or a["candidate"] == R["promoted_from"]):
                    lifted.append({"cert": c["d"], "attestation": a["d"], "attestation_issued_at": a["issued_at"], "negative_issued_at": max(n["issued_at"] for n in negs)})
        if not lifted:
            N.add(rel_d)
    return N


# ============================================================================================== 24 freshness and OP-7
OPS = ["C0", "C1", "C2", "C3"]


def freshness(K, ts, vts, pins, now, op7, params=PARAMS):
    hw_issued = max([vts.get("highest_issued_at", 0)] + [s.get("issued_at", 0) for s in K])  # 24 §8: highest verified issued_at, monotonic
    clock_ok = now >= hw_issued                                                               # 17 §13 (c)
    if ts["status"] in ("EQUIVOCATION", "REGRESSION"):
        return {"axis": ts["status"], "allowed": ["C0"], "current_label_permitted": False, "clock_ok": clock_ok}
    anchors = []
    if vts.get("anchor"):
        anchors.append(dict(vts["anchor"]))
    for p in pins:
        anchors.append({"seq": p["seq"], "digest": p["digest"], "at": p["provisioned_at"], "method": "pin"})
    for a in anchors:
        held = [t for t in K if t["kind"] == "tss" and t["seq"] == a["seq"]]
        if held and a.get("digest") and all(h["d"] != a["digest"] for h in held):
            return {"axis": "EQUIVOCATION(anchor digest)", "allowed": ["C0"], "current_label_permitted": False, "clock_ok": clock_ok}
    witness = None
    e = ts.get("eff")
    if op7 == "c" and e and e["expires_at"] and clock_ok:
        within = (e["expires_at"] - e["issued_at"]) <= params["witness_max_validity_days"] * DAY
        if e["expires_at"] > now and e["issued_at"] >= vts.get("highest_witness_issued_at", -1) and within:
            witness = e
    seq = ts["seq"]
    if anchors:
        top = max(anchors, key=lambda a: a["seq"])
        if seq < top["seq"]:
            return {"axis": f"BELOW_ANCHOR(have {seq} < {top['seq']})", "allowed": ["C0"], "current_label_permitted": False, "clock_ok": clock_ok}
        age = int((now - top["at"]) / DAY)
        label = f"ANCHORED({top['seq']}, {top['method']}, {age}d; held {seq})"
        if ts["status"] == "INCOMPLETE":
            return {"axis": label + " INCOMPLETE", "allowed": ["C0", "C1"], "current_label_permitted": True, "clock_ok": clock_ok}
        if op7 == "b" and (not clock_ok or age > params["max_anchor_age_days"]):
            return {"axis": label + " ANCHOR_EXPIRED", "allowed": ["C0", "C1"], "current_label_permitted": False, "clock_ok": clock_ok}
        return {"axis": label, "allowed": list(OPS), "current_label_permitted": True, "clock_ok": clock_ok}
    if witness:
        return {"axis": f"WITNESSED({witness['seq']}, expires {int((witness['expires_at'] - now) / DAY)}d)", "allowed": list(OPS), "current_label_permitted": True, "clock_ok": clock_ok}
    if op7 == "d":
        return {"axis": f"UNANCHORED(FRESHNESS_UNPROVEN, held {seq})", "allowed": ["C0", "C1", "C2"], "current_label_permitted": False, "clock_ok": clock_ok}
    return {"axis": f"UNANCHORED(held {seq})", "allowed": ["C0"], "current_label_permitted": False, "clock_ok": clock_ok}


# ============================================================================================== 19 §6 (parts used)
def eligible_use(R, K, ts, tpsS, project_record_seq=None, historical=()):
    N = negative_set(K, ts, tpsS["eff"])
    why = []
    if R["d"] in historical:
        why.append("historical")
    if R["stage"] != "final":
        why.append("candidate")
    if tpsS["eff"] and R["seq"] < tpsS["eff"]["min_seq"]:
        why.append("below_min_release_sequence")
    if R["d"] in N:
        why.append("revoked")
    if project_record_seq is not None and R["seq"] < project_record_seq:
        why.append("downgrade_without_transaction")
    return {"eligible": not why, "reasons": why}


def ingress_ok(R, K, ts, tpsS, fr):
    u = eligible_use(R, K, ts, tpsS)
    why = list(u["reasons"])
    if ts["status"] != "KNOWN":
        why.append("trust_state_" + ts["status"].lower())
    if "C3" not in fr["allowed"]:
        why.append("freshness:" + fr["axis"])
    if R["refs"]["state"] > ts["seq"]:
        why.append("references_unknown_state")
    return {"freshness_and_eligibility_ok": not why, "reasons": why, "trust_gate_still_required": True}


# ============================================================================================== 25 §5 verify-artifact
def verify_artifact(art, K, ts, tpsS, vts_high, key_purposes, thresholds, fresh_allowed, require_attested_source=False):
    rel = next((s for s in K if s["kind"] == "release" and s["d"] == art["release_statement_digest"]), None)
    signers = {k for k in art["signers"] if "release-artifact" in key_purposes.get(k, ())}
    if not signers:
        return "PURPOSE_NOT_GRANTED"
    if len(signers) < thresholds["release-artifact"]:
        return "THRESHOLD_NOT_MET"
    bas = {b["signer"] for b in K if b["kind"] == "build-att" and b["artifact"] == art["digest"] and b["tbm"] == art["tbm"]["d"]
           and "build-attestation" in key_purposes.get(b["signer"], ()) and rel and b["source_commit"] == rel["release_commit"]}
    if len(bas) < thresholds["build-attestation"]:
        return "ARTIFACT_BUILD_UNATTESTED"
    if not ts.get("eff") or art["digest"] not in ts["eff"]["arts"]:
        return "ARTIFACT_UNREFERENCED"
    held = {("tps", s["v"]): s["d"] for s in K if s["kind"] == "tps"}
    held.update({("tss", s["seq"]): s["d"] for s in K if s["kind"] == "tss"})
    t = art["tbm"]
    if held.get(("tps", t["tps_v"])) != t["tps_d"] or held.get(("tss", t["tss_seq"])) != t["tss_d"] or not rel or rel["purpose"] != "release-final":
        return "BINARY_T0_UNVERIFIED"
    if t["root_v"] < vts_high["root"] or t["tps_v"] < vts_high["tps"] or t["tss_seq"] < vts_high["tss"]:
        return "BINARY_T0_ROLLBACK"
    if art["digest"] in negative_set(K, ts, tpsS["eff"]):
        return "ARTIFACT_REVOKED"
    if "C3" not in fresh_allowed:
        return "TRUST_STATE_UNANCHORED"
    if require_attested_source:  # review r2 CD2-3 requirement, not in revision 3
        cand = next((s for s in K if s["kind"] == "release" and s["d"] == rel.get("promoted_from")), None)
        a = next((x for x in K if x["kind"] == "att" and cand and x["candidate"] == cand["d"] and x["verdict"] == "ACCEPTED"), None)
        if not (cand and a and cand["release_commit"] == rel["release_commit"]):  # attested source must be the source that is built
            return "ARTIFACT_SOURCE_UNVERIFIED"
    return "ACCEPTED"


# ============================================================================================== 27 §3 trust gates
def trust_gate_authorised(kind, digests, project, confirmations, decision_pins, tps_eff, repo_record=None):
    for c in confirmations:
        if c["kind"] == kind and tuple(c["digests"]) == tuple(digests) and c["project"] == project and not c.get("consumed"):
            return {"authorised": True, "by": c["method"]}
    if kind not in tps_eff["local_terminal_only"]:
        for p in decision_pins:
            if p["kind"] == kind and tuple(p["digests"]) == tuple(digests) and p["project"] in (project, "*"):
                return {"authorised": True, "by": "operator_decision_pin", "pin_writer": p.get("writer")}
    return {"authorised": False, "code": "TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED", "repository_record_consulted": False if repo_record else None}


R = {}


def record(sid, computed, claim, holds, **extra):
    R[sid] = {"computed": computed, "claim": claim, "claim_holds": bool(holds), **extra}


# ============================================================================================== review r2 B1-B6 against revision 3
P1 = tps(1)
K = [root(1), P1, tss(1, "t1"), tss(2, "t2", prior=[(1, "t1")]), release("R6", 6, refs=(2, 1, 1)), release("C999", 7, purpose="release-candidate", stage="candidate", refs=(MAX, 1, 1))]
ts = tss_state(K)
fr = freshness(K, ts, {"anchor": {"seq": 2, "digest": "t2", "at": NOW, "method": "human"}}, [], NOW, "a")
record("B1_r3_candidate_reference_inflation", {"trust_state": ts["status"], "ingress_R6": ingress_ok(K[4], K, ts, tps_state(K), fr), "ingress_C999_refs_ok": K[5]["refs"]["state"] <= ts["seq"]},
       "17 S7/MS-8: references outside the trust-state lineage are release-local; no global effect", ts["status"] == "KNOWN" and ingress_ok(K[4], K, ts, tps_state(K), fr)["freshness_and_eligibility_ok"])

Kb = [root(1), P1, release("R6", 6, promoted_from="C6"), candidate("C6", "commit-good"), attest("a1", "C6", issued_at=10 * DAY), cert("c1", "R6", "CERTIFIED", 1, "a1", issued_at=11 * DAY),
      tss(1, "t1", certs=[("R6", "c1")], atts=["a1"], issued_at=11 * DAY), cert("c2", "R6", "WITHDRAWN", 2, issued_at=20 * DAY), cert("c3", "R6", "CERTIFIED", 3, issued_at=21 * DAY)]
n_alone = "R6" in negative_set(Kb, tss_state(Kb), P1)
record("B2_r3_certification_key_alone", {"R6_negative": n_alone}, "17 MS-2: a certification key alone lifts nothing", n_alone)

# RV3-B-A05: the lift reuses the attestation issued before the withdrawal; only certification-status and trust-state sign anything new
Kl = Kb + [cert("c4", "R6", "CERTIFIED", 4, "a1", issued_at=30 * DAY), tss(2, "t2", prior=[(1, "t1")], certs=[("R6", "c1"), ("R6", "c4")], atts=["a1"], issued_at=30 * DAY)]
tsl = tss_state(Kl)
lifted = "R6" not in negative_set(Kl, tsl, P1)
new_signers = sorted({"certification-status (c4)", "trust-state (t2)"})
record("RV3-B-A05_lift_with_two_keys_reusing_pre_withdrawal_attestation",
       {"R6_negative_after": not lifted, "effective_tss": tsl["effective_tss"], "new_statements_signed_for_the_lift": new_signers,
        "attestation_used": "a1", "attestation_issued_before_withdrawal": True, "distinct_keys_needed": len(new_signers)},
       "05 §3 'lift of WITHDRAWN/REJECTED: 3 distinct keys'; 17 §3 'any lift of a negative fact needs three keys'", lifted is False or len(new_signers) >= 3)

K3 = [root(1), P1, tss(1, "t1"), tss(2, "t2a", prior=[(1, "t1")], revs=["rv2"]), tss(2, "t2b", prior=[(1, "t1")])]
ts3 = tss_state(K3)
record("B3_r3_same_sequence_fork", {"trust_state": ts3["status"], "freshness_a": freshness(K3, ts3, {}, [], NOW, "a")}, "17 S4(c): EQUIVOCATION, C0 only", ts3["status"] == "EQUIVOCATION")

K4 = [root(1), P1, tss(1, "t1"), tss(2, "t2x", prior=[(1, "t1")], root_v=999, pol=(999, "TPS999")), tss(3, "t3", prior=[(1, "t1")])]
ts4 = tss_state(K4)
ts4b = tss_state(K4 + [tss(9, "t9x", prior=[(1, "t1"), (3, "t3")], root_v=999, pol=(999, "TPS999"))])
record("B4_r3_unresolvable_references", {"below": ts4["status"], "effective": ts4["effective_tss"], "above": ts4b["status"]},
       "17 S4(a)/(e): unresolvable TSS never constrains; above the effective sequence it is INCOMPLETE", ts4["status"] == "KNOWN" and ts4["effective_tss"] == "t3" and ts4b["status"] == "INCOMPLETE")

held = {"AUTH.update_apply": 4}


def accept_tps(strongest_held, arriving, held_version):
    red = [k for k, v in strongest_held.items() if arriving["floors"].get(k, v) < v]
    exp = {h["key"] for h in arriving["lowering_history"] if h["in_policy_version"] > held_version}
    un = [k for k in red if k not in exp]
    return {"accepted": not un, "unexplained": un, "gate_required": bool(red) and not un}


v4 = tps(4, prior=[(1, "TPS1"), (2, "TPS2"), (3, "TPS3")], floors={"AUTH.update_apply": 3}, lowering_history=[{"key": "AUTH.update_apply", "in_policy_version": 3}])
v4h = tps(4, prior=[(1, "TPS1"), (2, "TPS2")], floors={"AUTH.update_apply": 3})
record("B6_r3_lowering_across_skipped_version", {"cumulative": accept_tps(held, v4, 2), "hidden": accept_tps(held, v4h, 2)},
       "19 §10.6: computed against the strongest held; cumulative history; undeclared reduction invalidates", accept_tps(held, v4, 2)["gate_required"] and not accept_tps(held, v4h, 2)["accepted"])

# ============================================================================================== published world for B5 and the machine list
TPS1, TPS2, TPS3 = tps(1, min_seq=1), tps(2, prior=[(1, "TPS1")], min_seq=5), tps(3, prior=[(1, "TPS1"), (2, "TPS2")], min_seq=8)
T1 = tss(1, "t1", pol=(1, "TPS1"), issued_at=NOW - 900 * DAY)
T5 = tss(5, "t5", prior=[(1, "t1")], pol=(2, "TPS2"), issued_at=NOW - 400 * DAY, expires_at=NOW - 393 * DAY)
T9 = tss(9, "t9", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - 10 * DAY, expires_at=NOW - 3 * DAY)  # emergency revocation; 17 §8 TPS raise is only SHOULD
T10 = tss(10, "t10", prior=[(1, "t1"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - 1 * DAY, expires_at=NOW + 6 * DAY)  # OP-7 (c) heartbeat
RV7 = revocation("rv7", ["R7"], issued_at=NOW - 10 * DAY)
R6, R7, R8 = release("R6", 6, refs=(5, 2, 1)), release("R7", 7, refs=(5, 2, 1)), release("R8", 8, refs=(9, 2, 1))
ROOT1 = root(1)
PUBLISHED = [ROOT1, TPS1, TPS2, T1, T5, T9, T10, RV7, R6, R7, R8]
T0_OLD = [ROOT1, TPS1, TPS2, T1, T5]                        # binary compiled 400 days ago
STRIPPED = [ROOT1, TPS1, TPS2, T1, T5, R7]                  # A2: installed R7; t9, t10 and rv7 removed
THIEF_WITNESS = tss(100, "t100x", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), issued_at=NOW, expires_at=NOW + 1 * DAY)  # trust-state key thief

# B5 re-executed (stateless runner, old binary, A2 swap), including a stale pin
K5 = T0_OLD + STRIPPED
ts5 = tss_state(K5)
b5 = {}
for label, pins, op7 in (("a_no_pin", [], "a"), ("a_pin_t9_fresh", [{"seq": 9, "digest": "t9", "provisioned_at": NOW - 1 * DAY}], "a"),
                         ("a_pin_t5_stale_400d", [{"seq": 5, "digest": "t5", "provisioned_at": NOW - 400 * DAY}], "a"), ("d_no_pin", [], "d")):
    f = freshness(K5, ts5, {}, pins, NOW, op7)
    b5[label] = {"freshness": f["axis"], "allowed": f["allowed"], "R7_policy_root_for_C2": "C2" in f["allowed"] and eligible_use(R7, K5, ts5, tps_state(K5))["eligible"],
                 "current_label_permitted": f["current_label_permitted"]}
record("B5_r3_fresh_runner_old_binary_A2_swap", b5,
       "24 §5.2/§9, 21 OP-7 (a): 'The review's P4-B5 class is impossible everywhere'; with a pin the stripped runner is BELOW_ANCHOR",
       not b5["a_no_pin"]["R7_policy_root_for_C2"] and not b5["a_pin_t9_fresh"]["R7_policy_root_for_C2"] and not b5["a_pin_t5_stale_400d"]["R7_policy_root_for_C2"],
       note="the claim holds for no pin and for a pin at the current state; it fails for a pin provisioned before t9 (RV3-B-A02)")

# ============================================================================================== machine list x OP-7 x adversary (HO-0002 §3.4)
MACHINES = {
    "M1_first_install_after_ceremony_t10": {"vts": {"anchor": {"seq": 10, "digest": "t10", "at": NOW, "method": "human"}}, "vts_K": [], "pins": []},
    "M2_ci_runner_no_pin": {"vts": {}, "vts_K": [], "pins": []},
    "M2_ci_runner_pin_current_t10": {"vts": {}, "vts_K": [], "pins": [{"seq": 10, "digest": "t10", "provisioned_at": NOW - 1 * DAY}]},
    "M2_ci_runner_pin_t5_image_400d": {"vts": {}, "vts_K": [], "pins": [{"seq": 5, "digest": "t5", "provisioned_at": NOW - 400 * DAY}]},
    "M2_ci_runner_pin_t5_image_100d": {"vts": {}, "vts_K": [], "pins": [{"seq": 5, "digest": "t5", "provisioned_at": NOW - 100 * DAY}]},
    "M3_restored_backup_anchor_t5_400d": {"vts": {"anchor": {"seq": 5, "digest": "t5", "at": NOW - 400 * DAY, "method": "human"}}, "vts_K": [TPS2, T5], "pins": []},
    "M4_old_epoch_anchor_t5_20d": {"vts": {"anchor": {"seq": 5, "digest": "t5", "at": NOW - 20 * DAY, "method": "human"}}, "vts_K": [TPS2, T5], "pins": []},
    "M5_no_epoch": {"vts": {}, "vts_K": [], "pins": []},
    "M6A_anchor_t10": {"vts": {"anchor": {"seq": 10, "digest": "t10", "at": NOW - 1 * DAY, "method": "human"}}, "vts_K": [T9, T10, RV7], "pins": []},
    "M6B_anchor_t5": {"vts": {"anchor": {"seq": 5, "digest": "t5", "at": NOW - 1 * DAY, "method": "human"}}, "vts_K": [TPS2, T5], "pins": []},
    "M7_offline_anchor_t5_1095d": {"vts": {"anchor": {"seq": 5, "digest": "t5", "at": NOW - 1095 * DAY, "method": "human"}}, "vts_K": [TPS2, T5], "pins": []},
}
ADVERSARIES = {
    "A2_A5_repository_or_transport": {"K": STRIPPED, "pins": []},
    "A2_with_same_account_code_execution": {"K": STRIPPED, "pins_replace": [{"seq": 5, "digest": "t5", "provisioned_at": NOW}]},  # rewrites the pin file in the account configuration
    "A2_plus_trust_state_key": {"K": STRIPPED + [THIEF_WITNESS], "pins": []},
}
matrix = []
for mname, m in MACHINES.items():
    for aname, adv in ADVERSARIES.items():
        for op7 in "abcd":
            K = T0_OLD + m["vts_K"] + adv["K"]
            anchor = m["vts"].get("anchor")
            ts = tss_state(K, anchor=anchor)
            pins = adv["pins_replace"] if "pins_replace" in adv else m["pins"] + adv.get("pins", [])
            f = freshness(K, ts, m["vts"], pins, NOW, op7)
            tpsS = tps_state(K)
            use = eligible_use(R7, K, ts, tpsS)
            ing = ingress_ok(R7, K, ts, tpsS, f)
            matrix.append({"machine": mname, "adversary": aname, "op7": op7, "trust_state": ts["status"], "effective_sequence": ts["seq"], "freshness": f["axis"],
                           "allowed": f["allowed"], "current_label_permitted": f["current_label_permitted"],
                           "revoked_R7_as_policy_root_for_C2": "C2" in f["allowed"] and use["eligible"],
                           "revoked_R7_trust_ingress_C3_freshness_and_eligibility": ing["freshness_and_eligibility_ok"]})
R["MATRIX_machine_x_op7_x_adversary"] = {"rows": matrix, "published_state": "t10 (heartbeat of t9); t9 revokes R7 (emergency revocation, no TPS raise); TPS2 min_release_sequence 5",
                                         "stripped_view": "t1, t5, TPS1, TPS2, R7 (A2 removes t9, t10, rv7)", "note": "per-project record absent (fresh clone); E10 would refuse where a record at R8 exists"}


def rows(**kw):
    return [r for r in matrix if all(r[k] == v for k, v in kw.items())]


# RV3-B-A02: stale pin under OP-7 (a)
a02 = rows(machine="M2_ci_runner_pin_t5_image_400d", adversary="A2_A5_repository_or_transport")
record("RV3-B-A02_stale_ci_pin_op7", {r["op7"]: {k: r[k] for k in ("freshness", "revoked_R7_as_policy_root_for_C2", "current_label_permitted")} for r in a02},
       "24 §9 / 21 OP-7 (a): 'makes the review's B5 class impossible on every machine'; 24 §5.2 pins solve the clean CI runner",
       not any(r["revoked_R7_as_policy_root_for_C2"] for r in a02 if r["op7"] == "a"))
# RV3-B-A03: pin written by a same-account process (repository build step, plugin, agent tool call)
a03 = rows(machine="M2_ci_runner_no_pin", adversary="A2_with_same_account_code_execution") + rows(machine="M2_ci_runner_pin_current_t10", adversary="A2_with_same_account_code_execution")
record("RV3-B-A03_pin_written_by_same_account_process", [{k: r[k] for k in ("machine", "op7", "freshness", "revoked_R7_as_policy_root_for_C2")} for r in a03],
       "24 §3.2: a pin is independent of A1, A2, A4, A5 (TA-9)", not any(r["revoked_R7_as_policy_root_for_C2"] for r in a03 if r["machine"] == "M2_ci_runner_no_pin" and r["op7"] in "abc"),
       note="the adversary rewrites the pin file (same account); a VTS-held newer TSS still refuses (M6A); every stateless runner is anchored at the chosen epoch")
# RV3-B-A06: OP-7 (c) witness minted by the trust-state key on a stateless runner
a06 = rows(machine="M2_ci_runner_no_pin", adversary="A2_plus_trust_state_key", op7="c")[0]
a06_anch = rows(machine="M6A_anchor_t10", adversary="A2_plus_trust_state_key", op7="c")[0]
record("RV3-B-A06_trust_state_key_mints_witness_op7_c", {"stateless_runner": a06, "machine_holding_t10": {k: a06_anch[k] for k in ("trust_state", "freshness", "allowed")}},
       "05 §1 and 17 §15: trust-state key alone = freeze only; cannot lift negatives or regress honest successors; 21 OP-7 (c): staleness bounded by the expiry window",
       not a06["revoked_R7_trust_ingress_C3_freshness_and_eligibility"] and not a06["revoked_R7_as_policy_root_for_C2"])

# RV3-B-A07: issued_at high-water poisoning (any purpose; witness issued_at by the trust-state key)
POISON = candidate("CP", "commit-x", issued_at=NOW + 36500 * DAY)  # release-candidate key, lowest custody
KA = T0_OLD + [T9, T10, RV7, R8]
vts_a = {"anchor": {"seq": 10, "digest": "t10", "at": NOW - 1 * DAY, "method": "human"}}
before_b = freshness(KA, tss_state(KA, vts_a["anchor"]), vts_a, [], NOW, "b")
KP = KA + [POISON]
after_b = freshness(KP, tss_state(KP, vts_a["anchor"]), vts_a, [], NOW, "b")
vts_reanchored = {"anchor": {"seq": 10, "digest": "t10", "at": NOW, "method": "human"}, "highest_issued_at": NOW + 36500 * DAY}
after_reanchor_b = freshness(KA, tss_state(KA, vts_reanchored["anchor"]), vts_reanchored, [], NOW, "b")  # statement removed from the repository; VTS high-water persists
w_ok = freshness(KA, tss_state(KA), {}, [], NOW, "c")
w_poison = tss(11, "t11x", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW + 36500 * DAY, expires_at=NOW + 36501 * DAY)
vts_w = {"highest_witness_issued_at": NOW + 36500 * DAY, "highest_issued_at": NOW + 36500 * DAY}
T12 = tss(12, "t12", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11x")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW, expires_at=NOW + 6 * DAY)
honest_after = freshness(KA + [w_poison, T12], tss_state(KA + [w_poison, T12]), vts_w, [], NOW, "c")
record("RV3-B-A07_issued_at_high_water_poisoning", {"op7_b_before": before_b["axis"], "op7_b_after_candidate_with_future_issued_at": {"axis": after_b["axis"], "allowed": after_b["allowed"]},
                                                     "op7_b_after_statement_removed_and_human_reanchor": {"axis": after_reanchor_b["axis"], "allowed": after_reanchor_b["allowed"]},
                                                     "op7_c_honest_witness_before": w_ok["axis"], "op7_c_honest_witness_after_future_witness_seen": {"axis": honest_after["axis"], "allowed": honest_after["allowed"]}},
       "24 §8 high-water monotonic; 17 §15 trust-state theft freezes only until the next honest TSS or a root rotation; 05 §1 release-candidate theft = candidates only",
       "C2" in after_reanchor_b["allowed"] and "C2" in honest_after["allowed"])

# RV3-B-A08: verify-artifact accepts a binary built from a source that no verifier attested
key_purposes = {"kf": ("release-final",), "ka1": ("release-artifact",), "ka2": ("release-artifact",), "kb": ("build-attestation",)}
thr = {"release-artifact": 2, "build-attestation": 1}
C11 = candidate("C11", "commit-good")                                                     # genuine candidate, independently verified
A11 = attest("a11", "C11")
F_EVIL = release("F-evil", 11, commit="commit-evil", promoted_from="C11", refs=(10, 2, 1))  # release-final key thief: identical kernel tree (V8 passes), different release_commit
TBM = {"d": "tbm-evil", "root_v": 1, "tps_v": 2, "tps_d": "TPS2", "tss_seq": 11, "tss_d": "t11"}
ART = {"digest": "A-evil", "release_statement_digest": "F-evil", "signers": ["ka1", "ka2"], "tbm": TBM}
T11 = tss(11, "t11", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=["R7"], atts=["a11"], arts=["A-evil"], issued_at=NOW)
K8 = PUBLISHED + [C11, A11, F_EVIL, T11, {"kind": "build-att", "artifact": "A-evil", "tbm": "tbm-evil", "signer": "kb", "source_commit": "commit-evil", "issued_at": NOW}]
ts8 = tss_state(K8)
fr8 = freshness(K8, ts8, {"anchor": {"seq": 11, "digest": "t11", "at": NOW, "method": "human"}}, [], NOW, "a")
high = {"root": 1, "tps": 2, "tss": 10}
got = verify_artifact(ART, K8, ts8, tps_state(K8), high, key_purposes, thr, fr8["allowed"])
got_cd23 = verify_artifact(ART, K8, ts8, tps_state(K8), high, key_purposes, thr, fr8["allowed"], require_attested_source=True)
record("RV3-B-A08_binary_from_unverified_source", {"verify_artifact_revision3": got, "with_review_r2_CD2-3_attested_source_requirement": got_cd23,
                                                   "who_chose_the_source": "release-final (threshold 1) via release_commit; rebuilder attests reproduction of that commit (25 §3, 05 §7 rule 6); release-artifact custodians' stated check is 'carries at least one build attestation'",
                                                   "final_promoted_from_genuine_attested_candidate_with_identical_tree": True, "candidate_release_commit": "commit-good", "final_release_commit": "commit-evil", "final_certified": False},
       "25 §7: one release-final key cannot mint an accepted malicious binary; HO-0001 §3.3", got != "ACCEPTED")

# RV3-B-A09: compromise playbook 05 §9 'TSS stops referencing them' versus S4(d) artifact supersets
Kp = T0_OLD + [T9, T10, RV7, tss(11, "t11", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=["R7"], arts=["A-bad"]),
               revocation("rvA", ["A-bad"]), tss(12, "t12", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11")], pol=(2, "TPS2"), revs=["R7", "A-bad"], arts=[])]
tsp = tss_state(Kp)
record("RV3-B-A09_playbook_unreference_artifact", {"trust_state": tsp["status"], "effective": tsp["effective_tss"], "non_admissible": tsp["non_admissible"],
                                                   "freshness_a_anchored_t11": freshness(Kp, tsp, {"anchor": {"seq": 11, "digest": "t11", "at": NOW, "method": "human"}}, [], NOW, "a")["allowed"]},
       "05 §9: after release-artifact compromise 'TSS stops referencing them' (durable once the verifier holds a TSS without the references)", tsp["status"] == "KNOWN" and tsp["effective_tss"] == "t12")

# RV3-B-A10: decision table under OP-7 (d) with INCOMPLETE versus 17 §7 (C2 requires KNOWN)
Ki = T0_OLD + [tss(20, "t20u", prior=[(1, "t1"), (5, "t5")], root_v=2, pol=(2, "TPS2"))]
tsi = tss_state(Ki)
fi = freshness(Ki, tsi, {}, [], NOW, "d")
record("RV3-B-A10_op7_d_incomplete_row_conflict", {"trust_state": tsi["status"], "24_s4_3_literal_rows": fi["allowed"], "17_s7_c2_requires_KNOWN": False},
       "24 §4.3 and 17 §7 give one answer for C2 on an unanchored INCOMPLETE machine under OP-7 (d)", "C2" not in fi["allowed"])

# RV3-B-A11: OP-7 (c) with a human (non-witness) anchor: 24 §5.7 text versus the §4.3 table
m7c = rows(machine="M7_offline_anchor_t5_1095d", adversary="A2_A5_repository_or_transport", op7="c")[0]
record("RV3-B-A11_op7_c_non_witness_anchor", {k: m7c[k] for k in ("freshness", "allowed")},
       "24 §5.7: 'under (c), [C2 and C3 refuse] for lack of a fresh witness'", "C2" not in m7c["allowed"],
       note="the §4.3 table and §9 '(c) anchored machine: as (a), plus witnesses' allow C2/C3 on any non-witness anchor of any age")

# RV3-B-A12: anchor satisfaction. 24 §4.1 defines BELOW_ANCHOR as "have n < e"; S4(b) orphans apply only when the anchored TSS is held.
# The architect's P4r3 freshness() uses `if seq < anchor["sequence"]`. A trust-state key thief presents a higher TSS that does not chain
# through the (withheld) anchored statement.
def below_anchor(reading, ts, K, anchor):
    e = ts.get("eff")
    if reading == "state_sequence_only_24_s4_1_literal":
        return ts["seq"] < anchor["seq"]
    if reading == "componentwise_epoch_root_policy_state":
        return ts["seq"] < anchor["seq"] or (e and e["pol"][0] < anchor["policy_version"]) or eff_root(K) < anchor["root_version"]
    if reading == "anchored_statement_held_and_in_effective_chain":
        return not (e and ((e["seq"], e["d"]) == (anchor["seq"], anchor["digest"]) or (anchor["seq"], anchor["digest"]) in e["prior"]))
    raise ValueError(reading)


THIEF_ABOVE = tss(100, "t100x", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), issued_at=NOW)
K12 = T0_OLD + STRIPPED + [THIEF_ABOVE]
ts12 = tss_state(K12)
pin12 = {"seq": 10, "digest": "t10", "policy_version": 2, "root_version": 1, "provisioned_at": NOW - 1 * DAY}
a12 = {}
for reading in ("state_sequence_only_24_s4_1_literal", "componentwise_epoch_root_policy_state", "anchored_statement_held_and_in_effective_chain"):
    below = below_anchor(reading, ts12, K12, pin12)
    a12[reading] = {"below_anchor": bool(below), "R7_policy_root_for_C2_under_op7_a": (not below) and eligible_use(R7, K12, ts12, tps_state(K12))["eligible"],
                    "R7_C3_freshness_and_eligibility": (not below) and ts12["status"] == "KNOWN" and eligible_use(R7, K12, ts12, tps_state(K12))["eligible"]}
record("RV3-B-A12_anchor_bypass_by_higher_unchained_tss", {"machine": "clean CI runner with a CURRENT pin (t10, provisioned 1 day ago) or a first-install human anchor on t10",
                                                          "adversary": "A2/A5 withholds t9, t10, rv7 and presents a TSS 100 signed by the trust-state key (threshold 1) chaining only t1, t5",
                                                          "effective_tss": ts12["effective_tss"], "trust_state": ts12["status"], "readings": a12,
                                                          "architect_P4r3_encoding": "freshness(): `if seq < anchor[\"sequence\"]` (state_sequence_only)"},
       "17 §15 / 05 §1: trust-state key alone = freeze only; 24 §5.1-§5.2: a withheld anchored epoch leaves the machine BELOW_ANCHOR",
       a12["state_sequence_only_24_s4_1_literal"]["below_anchor"] and a12["componentwise_epoch_root_policy_state"]["below_anchor"])

# RV3-B-A04: operator decision pin written by a same-account process; repository record (review r2 P2 shape)
tps_eff = TPS2
confs = []
pins_forged = [{"kind": k, "digests": ["D-cur", "D-target"], "project": "*", "writer": "same-account process (agent tool call, plugin, repository build step)"} for k in ("framework_update", "weakening", "project_strength", "downgrade")]
gate = {k: trust_gate_authorised(k, ["D-cur", "D-target"], "P1", confs, pins_forged, tps_eff) for k in ("framework_update", "weakening", "project_strength", "downgrade")}
p2 = trust_gate_authorised("framework_update", ["D-cur", "D-target"], "P1", [], [], tps_eff, repo_record={"gate_status": "ANSWERED", "answer": {"by_kind": "human"}})
record("P2_r3_repository_gate_record", p2, "27 §4 / rule (18): a repository record is a request", not p2["authorised"])
record("RV3-B-A04_decision_pin_written_by_same_account_process", gate,
       "27 §3.3: 'a trust gate MUST NOT be answerable by gov decide or by any agent path'; 27 §3.2 pins provisioned under TA-9",
       not any(v["authorised"] for v in gate.values()), note="authorised for every kind not in local_terminal_only; the pack declares A3 forging as TG-2")

summary = {"scenarios": len([k for k in R if not k.startswith("MATRIX")]), "claims_holding": sorted(k for k, v in R.items() if not k.startswith("MATRIX") and v["claim_holds"]),
           "claims_failing": sorted(k for k, v in R.items() if not k.startswith("MATRIX") and not v["claim_holds"]),
           "matrix_rows": len(matrix), "matrix_rows_R7_policy_root_for_C2": len([r for r in matrix if r["revoked_R7_as_policy_root_for_C2"]]),
           "matrix_rows_R7_ingress_ok": len([r for r in matrix if r["revoked_R7_trust_ingress_C3_freshness_and_eligibility"]])}
print(json.dumps({"summary": summary, "scenarios": R}, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))
