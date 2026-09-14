#!/usr/bin/env python3
"""P4 (RoT-1 revision 3) — reference model of the revision-3 trust-state, anchoring, lowering, purpose-separation and
binary-acceptance rules, run against the review's six falsification scenarios and the new-machine list of HO-0001 §3.2.

Attribution: scenario shapes B1–B6 are taken from review-r2 `evidence/P4-trust-state-model.py`. The rules are re-encoded
from revision 3 as written: `17` S1–S12 and §7, `24` (freshness anchoring, OP-7), `19` §10 (computed lowering), `05` §3
(compiled purpose whitelist, KS-1…KS-10) and `06` §2 (verify-artifact). Signatures are assumed valid: only decision logic
is modelled. This is not the Governance OS implementation.

Every scenario prints the computed outcome, the revision-3 claim it is compared with, and `agrees`. For B1–B6 the
review-r2 result is recorded as `r2_agrees: false`; revision 3 must flip each one.
"""
import json

MAX = 2 ** 53 - 1
DAY = 86400


# ================================================================================================ statements
def tps(v, d, prior=(), floors=None, min_seq=1, min_bin="4.1.6", lowering_history=(), unrevokes=()):
    return {"kind": "tps", "purpose": "trust-policy", "version": v, "digest": d, "prior_policies": list(prior), "floors": floors or {},
            "min_release_sequence": min_seq, "min_binary_version": min_bin, "lowering_history": list(lowering_history), "unrevokes": list(unrevokes)}


def tss(seq, d, prior=(), root=1, policy=(1, "P1"), revs=(), certs=(), atts=(), arts=(), expires_at=None, issued_at=0):
    return {"kind": "tss", "purpose": "trust-state", "sequence": seq, "digest": d, "prior_states": list(prior), "root_version": root,
            "policy": tuple(policy), "revocations": list(revs), "certifications": list(certs), "attestations": list(atts), "artifacts": list(arts),
            "expires_at": expires_at, "issued_at": issued_at}


def rel(d, seq, purpose="release-final", stage="final", refs=None):
    return {"kind": "release", "purpose": purpose, "digest": d, "sequence": seq, "stage": stage, "references": refs or {"state_sequence": 1, "policy_version": 1, "root_version": 1}}


def cert(d, release, status, cseq, att=None, issued_under=1):
    return {"kind": "cert", "purpose": "certification-status", "digest": d, "release": release, "status": status, "cseq": cseq, "attestation": att, "issued_under": issued_under}


def att(d, candidate, verdict="ACCEPTED"):
    return {"kind": "att", "purpose": "verification-attestation", "digest": d, "candidate": candidate, "verdict": verdict}


def revo(d, targets):
    return {"kind": "revocation", "purpose": "revocation", "digest": d, "targets": list(targets)}


def root(v):
    return {"kind": "root", "purpose": "root", "version": v, "digest": f"R{v}"}


# ================================================================================================ 17 S2–S9 (revision 3)
def eff_root(K):
    return max([s["version"] for s in K if s["kind"] == "root"] + [1])


def policy_state(K):
    """S3: highest TPS; equal versions with different digests, or a highest TPS whose prior_policies omits a held lower TPS, is equivocation."""
    ps = sorted((s for s in K if s["kind"] == "tps"), key=lambda s: s["version"])
    by_v = {}
    for p in ps:
        by_v.setdefault(p["version"], set()).add(p["digest"])
    eq = [v for v, ds in by_v.items() if len(ds) > 1]
    if eq:
        return {"status": "EQUIVOCATION", "versions": eq, "effective": None}
    eff = None
    for p in ps:
        lower = [q for q in ps if q["version"] < p["version"]]
        if all((q["version"], q["digest"]) in [tuple(x) for x in p["prior_policies"]] for q in lower):
            eff = p
        else:
            return {"status": "EQUIVOCATION", "versions": [p["version"]], "reason": "prior_policies omits a held lower policy", "effective": eff}
    return {"status": "OK", "effective": eff}


def trust_state(K, anchor=None):
    """S4–S9 revision 3: references must resolve; equivocation among resolved statements; admissibility and chain by prior_states; minimums only from the trust-state lineage.
    S4(e): when an independent anchor (pin, human confirmation, witness) names a held TSS, resolved statements at or below the anchor that are not in the anchored
    chain are orphans: reported (TRUST_STATE_FORK_ORPHANS, doctor CRITICAL), never effective and never a constraint."""
    er = eff_root(K)
    pol = policy_state(K)
    if pol["status"] != "OK":
        return {"status": "EQUIVOCATION", "reason": "trust policy", "effective_tss": None, "tps": None}
    held_pol = {(s["version"], s["digest"]) for s in K if s["kind"] == "tps"}
    tsses = sorted((s for s in K if s["kind"] == "tss"), key=lambda s: s["sequence"])
    resolved = [t for t in tsses if t["root_version"] <= er and tuple(t["policy"]) in held_pol]
    unresolved = [t for t in tsses if t not in resolved]
    orphans = []
    if anchor:
        at = next((t for t in resolved if t["sequence"] == anchor["sequence"] and t["digest"] == anchor.get("digest")), None)
        if at:
            chain = {tuple(x) for x in at["prior_states"]} | {(at["sequence"], at["digest"])}
            orphans = [t for t in resolved if t["sequence"] <= at["sequence"] and (t["sequence"], t["digest"]) not in chain]
            resolved = [t for t in resolved if t not in orphans]
    by_seq = {}
    for t in resolved:
        by_seq.setdefault(t["sequence"], set()).add(t["digest"])
    eq = sorted(s for s, ds in by_seq.items() if len(ds) > 1)
    if eq:
        return {"status": "EQUIVOCATION", "sequences": eq, "effective_tss": None, "tps": pol["effective"]}
    admissible, regression = [], []
    for t in resolved:
        ok = True
        for l in admissible:
            if not (set(t["revocations"]) >= set(l["revocations"]) and set(t["attestations"]) >= set(l["attestations"]) and set(t["artifacts"]) >= set(l["artifacts"])
                    and t["root_version"] >= l["root_version"] and t["policy"][0] >= l["policy"][0]
                    and (l["sequence"], l["digest"]) in [tuple(x) for x in t["prior_states"]]):
                ok = False
        (admissible if ok else regression).append(t)
    eff = admissible[-1] if admissible else None
    status = "KNOWN"
    if regression and eff and max(r["sequence"] for r in regression) > eff["sequence"]:
        status = "REGRESSION"
    incomplete = [t["sequence"] for t in unresolved if not eff or t["sequence"] > eff["sequence"]]
    return {"status": status, "effective_tss": eff["digest"] if eff else None, "effective_sequence": eff["sequence"] if eff else 0,
            "tps": pol["effective"], "incomplete": incomplete, "unresolved_ignored": [t["digest"] for t in unresolved if t["sequence"] not in incomplete],
            "regressions": [r["digest"] for r in regression], "fork_orphans": [o["digest"] for o in orphans]}


def negative_set(K, ts):
    """S5 revision 3: revocations accumulate; a REJECTED/WITHDRAWN fact is lifted only by a higher CERTIFIED that the effective TSS references and that references a verified ACCEPTED attestation the TSS also references."""
    eff = next((s for s in K if s["kind"] == "tss" and s["digest"] == ts.get("effective_tss")), None)
    tpsd = ts.get("tps") or {"unrevokes": []}
    N = set()
    for s in K:
        if s["kind"] == "revocation":
            N |= set(s["targets"])
    N -= set(tpsd.get("unrevokes", []))
    for r in {c["release"] for c in K if c["kind"] == "cert"}:
        cs = sorted((c for c in K if c["kind"] == "cert" and c["release"] == r), key=lambda c: c["cseq"])
        neg = [c for c in cs if c["status"] in ("REJECTED", "WITHDRAWN")]
        if not neg:
            continue
        top_neg = max(c["cseq"] for c in neg)
        lifted = False
        for c in cs:
            if c["status"] == "CERTIFIED" and c["cseq"] > top_neg and eff and (r, c["digest"]) in [tuple(x) for x in eff["certifications"]]:
                a = next((x for x in K if x["kind"] == "att" and x["digest"] == c["attestation"] and x["verdict"] == "ACCEPTED"), None)
                if a and a["digest"] in eff["attestations"]:
                    lifted = True
        if not lifted:
            N.add(r)
    return N


def release_local_requirement(release, ts):
    """S7 revision 3: references carried by non-trust-state purposes constrain only the ingress of that statement's own release."""
    need = release["references"]["state_sequence"]
    return {"required_state_sequence": need, "have": ts.get("effective_sequence", 0), "ingress_of_this_release_allowed": ts.get("effective_sequence", 0) >= need}


# ================================================================================================ 24 freshness anchoring and OP-7
OPS = ["C0_diagnostics", "C1_governed_read", "C2_governed_mutation", "C3_trust_ingress"]


def freshness(ts, vts, now, op7, max_age_days=180, clock_ok=True):
    """Returns the freshness axis and which operation classes may run. vts = {anchor: {sequence, digest, at, method} | None, highest_witness_issued_at}."""
    anchor = (vts or {}).get("anchor")
    seq = ts.get("effective_sequence", 0)
    eff_digest = ts.get("effective_tss")
    witness = ts.get("_witness")
    if ts["status"] in ("EQUIVOCATION", "REGRESSION"):
        return {"axis": ts["status"], "allowed": ["C0_diagnostics"]}
    if anchor and anchor.get("digest_at_sequence") and anchor["sequence"] <= seq:
        pass
    if anchor:
        if seq < anchor["sequence"]:
            return {"axis": f"BELOW_ANCHOR(have {seq} < anchor {anchor['sequence']})", "allowed": ["C0_diagnostics"]}
        if anchor.get("digest") and seq == anchor["sequence"] and eff_digest != anchor["digest"]:
            return {"axis": "EQUIVOCATION(anchor digest)", "allowed": ["C0_diagnostics"]}
        age_days = (now - anchor["at"]) / DAY
        label = f"ANCHORED(anchor {anchor['sequence']} by {anchor['method']}, age {int(age_days)}d; held {seq})"
        if op7 == "b" and (not clock_ok or age_days > max_age_days):
            return {"axis": label + " ANCHOR_EXPIRED", "allowed": ["C0_diagnostics", "C1_governed_read"]}
        if op7 == "c" and anchor["method"] == "witness" and (not clock_ok or now > anchor.get("expires_at", 0)):
            return {"axis": label + " WITNESS_EXPIRED", "allowed": ["C0_diagnostics", "C1_governed_read"]}
        allowed = list(OPS) if not ts.get("incomplete") else ["C0_diagnostics", "C1_governed_read"]
        return {"axis": label + (f" INCOMPLETE{ts['incomplete']}" if ts.get("incomplete") else ""), "allowed": allowed}
    if op7 == "c" and witness and clock_ok and witness["expires_at"] >= now:
        return {"axis": f"WITNESSED(sequence {witness['sequence']}, expires in {int((witness['expires_at'] - now) / DAY)}d)", "allowed": list(OPS)}
    if op7 == "d":
        return {"axis": f"UNANCHORED(FRESHNESS_UNPROVEN; compiled epoch {seq})", "allowed": ["C0_diagnostics", "C1_governed_read", "C2_governed_mutation"]}
    return {"axis": f"UNANCHORED(held {seq})", "allowed": ["C0_diagnostics"]}


def witness_from(K, vts, now):
    """OP-7 (c): the highest unexpired resolved TSS with expires_at is a witness; a witness older than one already seen is not accepted as newer."""
    ws = sorted((s for s in K if s["kind"] == "tss" and s["expires_at"] and s["expires_at"] >= now), key=lambda s: s["sequence"])
    if not ws:
        return None
    w = ws[-1]
    if (vts or {}).get("highest_witness_issued_at", -1) > w["issued_at"]:
        return None
    return w


# ================================================================================================ 19 §10 computed lowering (revision 3)
def accept_policy(strongest_held, arriving, held_version):
    reductions = [k for k, v in strongest_held.items() if arriving["floors"].get(k, v) < v]
    explained = {h["key"] for h in arriving["lowering_history"] if h["in_policy_version"] > held_version}
    unexplained = [k for k in reductions if k not in explained]
    if unexplained:
        return {"accepted": False, "code": "TRUST_POLICY_UNDECLARED_LOWERING", "keys": unexplained}
    return {"accepted": True, "computed_reductions": reductions, "per_project_trust_gate_required": bool(reductions)}


# ================================================================================================ 05 §3 compiled purpose whitelist (revision 3)
PURPOSES = ["root", "trust-policy", "trust-state", "release-final", "release-candidate", "release-artifact", "build-attestation", "verification-attestation", "certification-status", "revocation", "retrieval-profile"]
WHITELIST = {frozenset(p) for p in [("root", "trust-policy"), ("release-final", "release-candidate"), ("revocation", "certification-status"),
                                     ("revocation", "trust-state"), ("retrieval-profile", "release-final")]}


def separation(grants):
    viol = []
    for key, ps in grants.items():
        ps = sorted(set(ps))
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if frozenset((ps[i], ps[j])) not in WHITELIST:
                    viol.append({"key": key, "pair": [ps[i], ps[j]]})
    return {"ok": not viol, "violations": viol}


def visible_certified_distinct_keys(grants):
    """Minimum distinct keys that must sign for a visible CERTIFIED: attestation, certification and trust-state purposes."""
    need = ["verification-attestation", "certification-status", "trust-state"]
    holders = {p: {k for k, ps in grants.items() if p in ps} for p in need}
    for k in grants:
        if sum(k in holders[p] for p in need) > 1:
            return {"min_distinct_keys": "<3", "shared_key": k}
    return {"min_distinct_keys": 3}


# ================================================================================================ 06 §2 verify-artifact (revision 3)
def verify_artifact(a, K, ts, vts_high, thresholds, key_purposes):
    signers = a["signers"]
    valid = [k for k in signers if "release-artifact" in key_purposes.get(k, [])]
    if not valid:
        return "PURPOSE_NOT_GRANTED"
    if len(set(valid)) < thresholds["release-artifact"]:
        return "THRESHOLD_NOT_MET"
    ba = [b for b in K if b["kind"] == "build-att" and b["artifact"] == a["digest"] and b["tbm"] == a["tbm"]["digest"] and "build-attestation" in key_purposes.get(b["signer"], [])]
    if len(ba) < thresholds["build-attestation"]:
        return "ARTIFACT_BUILD_UNATTESTED"
    eff = next((s for s in K if s["kind"] == "tss" and s["digest"] == ts.get("effective_tss")), None)
    if not eff or a["digest"] not in eff["artifacts"]:
        return "ARTIFACT_UNREFERENCED"
    held = {("tps", s["version"]): s["digest"] for s in K if s["kind"] == "tps"}
    held.update({("tss", s["sequence"]): s["digest"] for s in K if s["kind"] == "tss"})
    tbm = a["tbm"]
    for comp, ver, dig in (("tps", tbm["tps_version"], tbm["tps_digest"]), ("tss", tbm["tss_sequence"], tbm["tss_digest"])):
        if held.get((comp, ver)) != dig:
            return "BINARY_T0_UNVERIFIED"
    if tbm["root_version"] < vts_high["root"] or tbm["tps_version"] < vts_high["tps"] or tbm["tss_sequence"] < vts_high["tss"]:
        return "BINARY_T0_ROLLBACK"
    if a["digest"] in negative_set(K, ts):
        return "ARTIFACT_REVOKED"
    return "ACCEPTED"


# ================================================================================================ scenarios
R = {}


def record(name, computed, claim, agrees, **extra):
    R[name] = {"computed": computed, "revision_3_claim": claim, "agrees": bool(agrees), **extra}


P1 = tps(1, "P1")
P2 = tps(2, "P2", prior=[(1, "P1")])
P3 = tps(3, "P3", prior=[(1, "P1"), (2, "P2")], floors={"ROLE_FLOOR.x": 5}, min_seq=8, min_bin="4.1.8")

# ---- B1: release-candidate key inflates a reference
K = [P1, tss(1, "t1", policy=(1, "P1")), tss(2, "t2", prior=[(1, "t1")], policy=(1, "P1")), rel("R6", 6, refs={"state_sequence": 2, "policy_version": 1, "root_version": 1}),
     rel("C999", 7, purpose="release-candidate", stage="candidate", refs={"state_sequence": MAX, "policy_version": 1, "root_version": 1})]
ts = trust_state(K)
record("B1_inflated_reference_by_candidate_key", {"trust_state": ts["status"], "ingress_R6": release_local_requirement(K[3], ts), "ingress_C999": release_local_requirement(K[4], ts)},
       "17 S7 r3: references outside the trust-state lineage are release-local; no global STALE; only the inflated candidate's own ingress is refused",
       ts["status"] == "KNOWN" and release_local_requirement(K[3], ts)["ingress_of_this_release_allowed"] and not release_local_requirement(K[4], ts)["ingress_of_this_release_allowed"], r2_agrees=False)

# ---- B2: certification key alone tries to lift WITHDRAWN
K = [P1, tss(1, "t1", policy=(1, "P1"), certs=[("R6", "c1")], atts=["a1"]), rel("R6", 6), att("a1", "C6"), cert("c1", "R6", "CERTIFIED", 1, "a1"), cert("c2", "R6", "WITHDRAWN", 2),
     cert("c3", "R6", "CERTIFIED", 3)]
ts = trust_state(K)
N = negative_set(K, ts)
K_lift = K + [tss(2, "t2", prior=[(1, "t1")], policy=(1, "P1"), certs=[("R6", "c1"), ("R6", "c4")], atts=["a1"]), cert("c4", "R6", "CERTIFIED", 4, "a1")]
N2 = negative_set(K_lift, trust_state(K_lift))
record("B2_certification_key_alone_unwithdraws", {"R6_negative_with_c3_alone": "R6" in N, "R6_negative_after_referenced_attested_c4": "R6" in N2},
       "17 S5/MS-2 r3: lifting needs a higher CERTIFIED referenced by the effective TSS and an ACCEPTED attestation it also references", "R6" in N and "R6" not in N2, r2_agrees=False)

# ---- B3: same-sequence fork
K = [P1, tss(1, "t1", policy=(1, "P1")), tss(2, "t2a", prior=[(1, "t1")], policy=(1, "P1"), revs=["rv2"]), tss(2, "t2b", prior=[(1, "t1")], policy=(1, "P1"))]
ts = trust_state(K)
record("B3_same_sequence_fork", ts, "17 S4(d) r3: TRUST_STATE_EQUIVOCATION; governed mutations and ingress refused (C0 only)", ts["status"] == "EQUIVOCATION", r2_agrees=False)

# ---- B4: trust-state key thief inflates references; honest successor
K = [P1, root(1), tss(1, "t1", policy=(1, "P1")), tss(2, "t2x", prior=[(1, "t1")], root=999, policy=(999, "P999")), tss(3, "t3", prior=[(1, "t1")], policy=(1, "P1"))]
ts = trust_state(K)
record("B4_trust_state_key_inflates_references", ts, "17 S4(a) r3: unresolvable TSS is ignored and constrains nothing; honest successor effective; status KNOWN",
       ts["status"] == "KNOWN" and ts["effective_tss"] == "t3" and not ts["incomplete"], r2_agrees=False)
K_top = K + [tss(9, "t9x", prior=[(1, "t1"), (3, "t3")], root=999, policy=(999, "P999"))]
ts_top = trust_state(K_top)
record("B4b_unresolvable_statement_above_effective", {"trust_state": ts_top, "freshness": freshness(ts_top, {"anchor": {"sequence": 3, "digest": "t3", "at": 0, "method": "human"}}, 10 * DAY, "a")},
       "24 §6 r3: an unresolvable higher TSS is INCOMPLETE: trust ingress and governed mutation refused until resolved or the key is rotated out (stated trust-state blast radius)",
       ts_top["incomplete"] == [9] and "C3_trust_ingress" not in freshness(ts_top, {"anchor": {"sequence": 3, "digest": "t3", "at": 0, "method": "human"}}, 10 * DAY, "a")["allowed"])

# ---- B5: fresh verifier, old binary, A2 swaps in older release and strips the trust record
T0_old = [P1, tss(1, "t1", policy=(1, "P1"))]
K_fresh = T0_old + [rel("R6", 6)]
ts = trust_state(K_fresh)
now = 1000 * DAY
out = {}
for op7 in ("a", "b", "c", "d"):
    out[f"op7_{op7}_no_anchor"] = freshness(ts, {}, now, op7)
pin_vts = {"anchor": {"sequence": 9, "digest": "t9", "at": now - 1 * DAY, "method": "pin"}}
out["op7_a_ci_pin_9"] = freshness(ts, pin_vts, now, "a")
record("B5_fresh_old_binary_after_A2_swap", out,
       "24 r3: without an anchor no governed mutation or ingress under OP-7 (a)/(b)/(c); with a provisioned pin the swap is BELOW_ANCHOR; under OP-7 (d) mutation is allowed only labelled FRESHNESS_UNPROVEN (owner-accepted residual)",
       all("C2_governed_mutation" not in out[f"op7_{o}_no_anchor"]["allowed"] for o in "abc") and "C2_governed_mutation" not in out["op7_a_ci_pin_9"]["allowed"]
       and "BELOW_ANCHOR" in out["op7_a_ci_pin_9"]["axis"] and "FRESHNESS_UNPROVEN" in out["op7_d_no_anchor"]["axis"], r2_agrees=False)

# ---- B6: lowering across a skipped version
held = {"AUTH.update_apply": 4}
v3 = tps(3, "P3L", prior=[(1, "P1"), (2, "P2")], floors={"AUTH.update_apply": 3}, lowering_history=[{"key": "AUTH.update_apply", "in_policy_version": 3}])
v4 = tps(4, "P4", prior=[(1, "P1"), (2, "P2"), (3, "P3L")], floors={"AUTH.update_apply": 3, "NEW.k": 4}, lowering_history=[{"key": "AUTH.update_apply", "in_policy_version": 3}])
v4_hidden = tps(4, "P4h", prior=[(1, "P1"), (2, "P2")], floors={"AUTH.update_apply": 3}, lowering_history=[])
a1, a2 = accept_policy(held, v4, 2), accept_policy(held, v4_hidden, 2)
record("B6_lowering_across_skipped_version", {"v4_with_cumulative_history": a1, "v4_hiding_the_lowering": a2},
       "19 §10 r3: computed against the strongest held values; any reduction needs the per-project trust gate; an unexplained reduction invalidates the TPS",
       a1["accepted"] and a1["per_project_trust_gate_required"] and not a2["accepted"], r2_agrees=False)

# ================================================================================================ HO-0001 §3.2 machine list
genuine_now = [P1, P2, P3, root(1), tss(1, "t1", policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2")),
               tss(9, "t9", prior=[(1, "t1"), (5, "t5")], policy=(3, "P3"), expires_at=now + 7 * DAY, issued_at=now - 1 * DAY)]
stripped_old = [P1, tss(1, "t1", policy=(1, "P1"))]

# M1 first install
ts_b = trust_state(genuine_now)
m1 = {"before_confirmation": freshness(ts_b, {}, now, "a"),
      "after_confirm_state_matching_held_t9": freshness(ts_b, {"anchor": {"sequence": 9, "digest": "t9", "at": now, "method": "human"}}, now, "a")}
ts_withheld = trust_state([P1, P2, tss(1, "t1", policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"))])
m1["channel_fingerprint_t9_but_bundle_withholds_t9"] = freshness(ts_withheld, {"anchor": {"sequence": 9, "digest": "t9", "at": now, "method": "human"}}, now, "a")
record("M1_first_install", m1, "24 §4 r3: C3 refused until anchored; a human fingerprint from an independent channel anchors; if the source withholds it the machine is BELOW_ANCHOR",
       "C3_trust_ingress" not in m1["before_confirmation"]["allowed"] and "C3_trust_ingress" in m1["after_confirm_state_matching_held_t9"]["allowed"]
       and "BELOW_ANCHOR" in m1["channel_fingerprint_t9_but_bundle_withholds_t9"]["axis"])

# M2 clean CI runner
m2 = {"a_no_pin": freshness(trust_state(stripped_old), {}, now, "a"),
      "a_pin_t9_repo_intact": freshness(ts_b, {"anchor": {"sequence": 9, "digest": "t9", "at": now - 30 * DAY, "method": "pin"}}, now, "a"),
      "a_pin_t9_repo_stripped": freshness(trust_state(stripped_old), {"anchor": {"sequence": 9, "digest": "t9", "at": now - 30 * DAY, "method": "pin"}}, now, "a")}
w_ts = dict(ts_b); w_ts["_witness"] = witness_from(genuine_now, {}, now)
m2["c_unexpired_witness_t9"] = freshness(w_ts, {}, now, "c")
old_only = [P1, P2, tss(1, "t1", policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"), expires_at=now - 60 * DAY, issued_at=now - 70 * DAY)]
o_ts = trust_state(old_only); o_ts["_witness"] = witness_from(old_only, {}, now)
m2["c_repo_swapped_to_expired_t5"] = freshness(o_ts, {}, now, "c")
m2["d_no_pin"] = freshness(trust_state(stripped_old), {}, now, "d")
record("M2_clean_ci_runner", m2, "24 §5.2 r3: no pin -> read-only (a); pin -> BELOW_ANCHOR when stripped; unexpired witness admits (c) and an expired one does not; (d) allows only labelled",
       m2["a_no_pin"]["allowed"] == ["C0_diagnostics"] and "C2_governed_mutation" in m2["a_pin_t9_repo_intact"]["allowed"] and "BELOW_ANCHOR" in m2["a_pin_t9_repo_stripped"]["axis"]
       and "C2_governed_mutation" in m2["c_unexpired_witness_t9"]["allowed"] and m2["c_repo_swapped_to_expired_t5"]["allowed"] == ["C0_diagnostics"] and "FRESHNESS_UNPROVEN" in m2["d_no_pin"]["axis"])

# M3 restored from backup (VTS rolled back to an older anchor)
vts_backup = {"anchor": {"sequence": 5, "digest": "t5", "at": now - 400 * DAY, "method": "human"}}
k_backup_stripped = [P1, P2, tss(1, "t1", policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"))]
m3 = {"a_repo_stripped": freshness(trust_state(k_backup_stripped), vts_backup, now, "a"), "b_repo_stripped": freshness(trust_state(k_backup_stripped), vts_backup, now, "b"),
      "a_repo_intact_learns_t9": freshness(ts_b, vts_backup, now, "a")}
record("M3_restored_from_backup", m3, "24 §5.3 r3: safe at the restored anchor (never below it), not fresh; (b) refuses mutation once the anchor age exceeds the limit; intact repository raises knowledge monotonically",
       "C2_governed_mutation" in m3["a_repo_stripped"]["allowed"] and "age 400d" in m3["a_repo_stripped"]["axis"] and "C2_governed_mutation" not in m3["b_repo_stripped"]["allowed"]
       and "held 9" in m3["a_repo_intact_learns_t9"]["axis"])

# M4 old epoch; A2 offers an even older state
vts_old = {"anchor": {"sequence": 5, "digest": "t5", "at": now - 20 * DAY, "method": "human"}}
k_m4 = [P1, P2, tss(1, "t1", policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"))]
m4 = {"repo_offers_only_t1": freshness(trust_state(k_m4), vts_old, now, "a"), "effective_sequence": trust_state(k_m4)["effective_sequence"],
      "repo_offers_t9": freshness(ts_b, vts_old, now, "a")}
record("M4_old_epoch", m4, "24 §5.4 r3: effective state is never below the retained anchor (VTS statements persist); newer genuine state raises it",
       m4["effective_sequence"] == 5 and "held 9" in m4["repo_offers_t9"]["axis"])

# M5 no epoch
m5 = {o: freshness(trust_state(stripped_old), {}, now, o) for o in "abcd"}
record("M5_no_epoch", m5, "24 §5.5 r3: UNANCHORED; C3 never; C1/C2 only under OP-7 (d), labelled", all("C3_trust_ingress" not in m5[o]["allowed"] for o in "abcd") and "C2_governed_mutation" in m5["d"]["allowed"] and "C2_governed_mutation" not in m5["a"]["allowed"])

# M6 two machines at different epochs sharing a repository
vA = {"anchor": {"sequence": 9, "digest": "t9", "at": now - 1 * DAY, "method": "human"}}
vB = {"anchor": {"sequence": 5, "digest": "t5", "at": now - 1 * DAY, "method": "human"}}
m6 = {"A_after_A2_strip": freshness(trust_state(genuine_now), vA, now, "a"), "B_after_A2_strip": freshness(trust_state(k_m4), vB, now, "a"),
      "B_after_pull_with_PTR": freshness(ts_b, vB, now, "a"), "lock_hint_from_A_on_B": {"hint": 9, "effect": "TRUST_STATE_HINT_MISMATCH warning only (lock is A2-writable)"}}
record("M6_two_machines_different_epochs", m6, "24 §5.6 r3: each machine enforces its own anchor; A never accepts lower; B learns 9 when the PTR carries it; hints never refuse or relax",
       "anchor 9" in m6["A_after_A2_strip"]["axis"] and "held 5" in m6["B_after_A2_strip"]["axis"] and "held 9" in m6["B_after_pull_with_PTR"]["axis"])

# M7 offline long absence
vlong = {"anchor": {"sequence": 5, "digest": "t5", "at": now - 1095 * DAY, "method": "human"}}
m7 = {o: freshness(trust_state(k_m4), vlong, now, o) for o in "abcd"}
record("M7_offline_long_absence", m7, "24 §5.7 r3: (a)/(d) allowed at the retained anchor with the age shown (cannot know unseen metadata); (b) refused by age; (c) needs a fresh witness",
       "C2_governed_mutation" in m7["a"]["allowed"] and "age 1095d" in m7["a"]["axis"] and "C2_governed_mutation" not in m7["b"]["allowed"])

# ================================================================================================ replay, gates, pins
honest = [P1, P2, P3, root(1), tss(1, "t1", policy=(1, "P1")), tss(4, "t4", prior=[(1, "t1")], policy=(1, "P1")), tss(5, "t5", prior=[(1, "t1"), (4, "t4")], policy=(2, "P2")),
          tss(9, "t9", prior=[(1, "t1"), (4, "t4"), (5, "t5")], policy=(3, "P3"))]
vts_holds = [s for s in honest if s["kind"] != "tss" or s["sequence"] == 9]
replayed = vts_holds + [s for s in honest if s["kind"] == "tss" and s["sequence"] in (1, 4)] + [P1]
ts_r1 = trust_state(replayed)
record("R1_signed_state_replay", {"effective": ts_r1["effective_tss"], "status": ts_r1["status"]},
       "17 MS-4 r3: replayed older genuine TSS/TPS (part of the published chain) never lower knowledge", ts_r1["effective_tss"] == "t9" and ts_r1["status"] == "KNOWN")
forked = honest + [tss(4, "t4x", prior=[(1, "t1")], policy=(1, "P1"), revs=[])]
ts_e3 = trust_state(forked)
ts_e3a = trust_state(forked, anchor={"sequence": 9, "digest": "t9"})
record("E3_old_sequence_fork_without_and_with_anchor", {"no_anchor": ts_e3, "anchored_t9": ts_e3a},
       "17 S4(d)/(e) r3: an equal-sequence fork is EQUIVOCATION (C0 only) without an anchor; an independent anchor on t9 makes the fork an orphan, reported, not effective",
       ts_e3["status"] == "EQUIVOCATION" and ts_e3a["status"] == "KNOWN" and ts_e3a["effective_tss"] == "t9" and ts_e3a["fork_orphans"] == ["t4x"])

vts_w = {"highest_witness_issued_at": now - 1 * DAY}
K_r2 = [P1, P2, P3, tss(1, "t1", policy=(1, "P1")), tss(8, "t8", prior=[(1, "t1")], policy=(2, "P2"), expires_at=now + 2 * DAY, issued_at=now - 5 * DAY)]
record("R2_witness_replay", {"fresh_runner_accepts_t8": witness_from(K_r2, {}, now) is not None, "runner_that_saw_t9_witness_accepts_t8": witness_from(K_r2, vts_w, now) is not None},
       "24 §5.2 r3 (OP-7 c): an unexpired older witness is accepted only by a verifier that never saw a newer one; staleness is bounded by the expiry window (TA-7)",
       witness_from(K_r2, {}, now) is not None and witness_from(K_r2, vts_w, now) is None)


def trust_gate_authorised(repo_record, vts_confirmations, gate_id, digests):
    """17 §7.2 / 21 r3: a trust gate is authorised only by a local confirmation in the VTS bound to (gate kind, statement digests); the repository record is a request."""
    return any(c["gate"] == gate_id and c["digests"] == digests and c["by_kind"] == "human_local" for c in vts_confirmations)


rr = {"id": "HDG-0001", "status": "ANSWERED", "answer": {"by_kind": "human"}, "digests": ["sha256:X"]}
record("R3_gate_record_from_repository", {"repo_record_only": trust_gate_authorised(rr, [], "HDG-0001", ["sha256:X"]),
                                          "local_confirmation_for_X": trust_gate_authorised(rr, [{"gate": "HDG-0001", "digests": ["sha256:X"], "by_kind": "human_local"}], "HDG-0001", ["sha256:X"]),
                                          "local_confirmation_for_Y_reused_for_X": trust_gate_authorised(rr, [{"gate": "HDG-0001", "digests": ["sha256:Y"], "by_kind": "human_local"}], "HDG-0001", ["sha256:X"])},
       "rule (18) r3: repository records never authorise trust decisions", True)
R["R3_gate_record_from_repository"]["agrees"] = (not R["R3_gate_record_from_repository"]["computed"]["repo_record_only"]) and R["R3_gate_record_from_repository"]["computed"]["local_confirmation_for_X"] and not R["R3_gate_record_from_repository"]["computed"]["local_confirmation_for_Y_reused_for_X"]

f_r4 = freshness(ts_b, {"anchor": {"sequence": 9, "digest": "t9", "at": now, "method": "human"}}, now, "a")
record("R4_lock_hint_inflation", {"freshness": f_r4, "hint": 999, "effect": "warning"}, "17 S8 r3: lock and VTS-record hints are warnings; they neither refuse nor relax", "C2_governed_mutation" in f_r4["allowed"])

f_r5 = freshness(ts_b, {"anchor": {"sequence": 9, "digest": "t9-other", "at": now, "method": "pin"}}, now, "a")
record("R5_pin_digest_mismatch", f_r5, "24 §3 r3: a held TSS at the pinned sequence with a different digest is EQUIVOCATION; C0 only", f_r5["allowed"] == ["C0_diagnostics"])

f_r6 = freshness(ts_b, {}, now, "a")
record("R6_A3_deletes_VTS", f_r6, "RS-3 r3: the machine becomes UNANCHORED; under OP-7 (a) read-only until re-anchored", f_r6["allowed"] == ["C0_diagnostics"])

K_e1 = [P1, tss(1, "t1", policy=(1, "P1")), tss(2, "t2a", prior=[(1, "t1")], policy=(1, "P1")), tss(5, "t5x", prior=[(1, "t1"), (2, "t2b")], policy=(1, "P1"))]
ts_e1 = trust_state(K_e1)
record("E1_fork_across_a_gap", ts_e1, "17 S4(c) r3: a higher TSS whose prior_states omit a held lower TSS is not admissible (REGRESSION): fork detected without the intermediates",
       ts_e1["status"] == "REGRESSION" and ts_e1["effective_tss"] == "t2a")

K_e2 = [tps(3, "P3a", prior=[(1, "P1")]), tps(3, "P3b", prior=[(1, "P1")]), P1]
record("E2_trust_policy_equivocation", policy_state(K_e2), "17 S3 r3: two TPS of one version with different digests -> EQUIVOCATION", policy_state(K_e2)["status"] == "EQUIVOCATION")

# ================================================================================================ purposes (R2-M6) and binary acceptance (R2-H3)
g_bad = {"k1": ["trust-state", "certification-status"], "k2": ["verification-attestation"]}
g_bad2 = {"k1": ["release-artifact", "release-final"]}
g_ok = {"k1": ["revocation", "trust-state"], "k2": ["certification-status"], "k3": ["verification-attestation"], "k4": ["release-final", "release-candidate"],
        "k5": ["release-artifact"], "k6": ["release-artifact"], "k7": ["build-attestation"]}
record("K1_trust_state_with_certification", {"separation": separation(g_bad), "visible_certified": visible_certified_distinct_keys(g_bad)},
       "05 KS-8 r3: forbidden pair; a visible CERTIFIED always needs three distinct keys", not separation(g_bad)["ok"])
record("K2_release_artifact_with_release_final", separation(g_bad2), "05 KS-9 r3: release-artifact shares a key with no other purpose", not separation(g_bad2)["ok"])
record("K3_owner_matrix_whitelist", {"separation": separation(g_ok), "visible_certified": visible_certified_distinct_keys(g_ok)}, "05 §3 r3: whitelisted sharing only; three distinct keys for CERTIFIED",
       separation(g_ok)["ok"] and visible_certified_distinct_keys(g_ok)["min_distinct_keys"] == 3)

key_purposes = {"kf": ["release-final", "release-candidate"], "ka1": ["release-artifact"], "ka2": ["release-artifact"], "kb": ["build-attestation"]}
thr = {"release-artifact": 2, "build-attestation": 1}
TBM = {"digest": "tbm1", "root_version": 1, "tps_version": 3, "tps_digest": "P3", "tss_sequence": 9, "tss_digest": "t9"}
art_ok = {"digest": "A1", "signers": ["ka1", "ka2"], "tbm": TBM}
K_art = genuine_now[:-1] + [tss(9, "t9", prior=[(1, "t1"), (5, "t5")], policy=(3, "P3"), arts=["A1"]), {"kind": "build-att", "artifact": "A1", "tbm": "tbm1", "signer": "kb"}]
ts_art = trust_state(K_art)
high = {"root": 1, "tps": 3, "tss": 9}
cases = {
    "A27_release_final_key_signs_artifact": (dict(art_ok, signers=["kf"]), K_art, "PURPOSE_NOT_GRANTED"),
    "A27b_one_release_artifact_key": (dict(art_ok, signers=["ka1"]), K_art, "THRESHOLD_NOT_MET"),
    "A27c_no_build_attestation": (art_ok, [s for s in K_art if s.get("kind") != "build-att"], "ARTIFACT_BUILD_UNATTESTED"),
    "A27d_not_referenced_by_trust_state": (dict(art_ok, digest="A2", tbm=TBM), K_art + [{"kind": "build-att", "artifact": "A2", "tbm": "tbm1", "signer": "kb"}], "ARTIFACT_UNREFERENCED"),
    "A27e_compiled_policy_digest_not_the_signed_policy": (dict(art_ok, tbm=dict(TBM, tps_digest="P3-forged")), K_art, "BINARY_T0_UNVERIFIED"),
    "A28_genuine_older_binary_below_high_water": (dict(art_ok, tbm=dict(TBM, tps_version=2, tps_digest="P2", tss_sequence=5, tss_digest="t5", digest="tbm1")), K_art, "BINARY_T0_ROLLBACK"),
    "A29_op4_no_candidate_final_key_signs_artifact": (dict(art_ok, signers=["kf", "kf"]), K_art, "PURPOSE_NOT_GRANTED"),
    "A_valid_artifact": (art_ok, K_art, "ACCEPTED"),
}
for n, (a, Kx, exp) in cases.items():
    got = verify_artifact(a, Kx, trust_state(Kx), high, thr, key_purposes)
    record(n, got, f"06 §2 r3 verify-artifact: {exp}", got == exp)

summary = {"scenarios": len(R), "agree": sum(v["agrees"] for v in R.values()), "disagree": [k for k, v in R.items() if not v["agrees"]],
           "review_r2_B1_B6_flipped": all(R[k]["agrees"] for k in R if k.startswith("B") and "r2_agrees" in R[k])}
print(json.dumps({"summary": summary, "scenarios": R}, indent=1, default=str))
