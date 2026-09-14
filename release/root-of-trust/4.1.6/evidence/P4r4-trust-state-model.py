#!/usr/bin/env python3
"""P4r4 — reference model of the RoT-1 revision-4 trust-state, anchoring, currency, OP-7, lifting, clock, purpose-separation,
trust-gate and binary-acceptance rules. Independent of P4r3: written from the revision-4 text (`17`, `24`, `25`, `05`, `27`,
`19` §10), not by editing the revision-3 model.

Attribution. Scenario shapes are taken from: review r2 `evidence/P4-trust-state-model.py` (B1–B6); the revision-3 architect
model `evidence/P4r3-trust-state-model.py` (M1–M7, R1–R6, E1–E3, K1–K3, A27–A29); review r3 reviewer B
`B-trust-security/evidence/RV3-B-M-reference-model.py` (the published world t1→t5→t9→t10, RV3-B-A02…A13 and the 132-row
machine × OP-7 × adversary matrix); review r3 synthesis D `D-synthesis/evidence/RV3-D-oracle-anchor-artifact.py`
(RV3-D-A11, A12, A13, A15). The rules are revision 4. Signatures are modelled as signer key ids checked against root
grants and thresholds (SV-6/SV-7); cryptography is not modelled.

Every scenario records `computed`, the revision-4 `claim`, and `holds`. The **conformance oracle** (RV3-M9, CR-12) re-runs
every scenario under eight single-rule mutants that re-introduce a review-r3 defect (for example sequence-number anchors).
Each mutant must make at least one scenario fail; the output lists which. No scenario uses a hash-cyclic construction: an
artefact is always referenced by a Trust State Statement later than the one its Trust Base Manifest names (RV3-M8).

Scratch-free: no files, no subprocesses. Output: JSON on stdout.
"""
import copy, json, sys

sys.dont_write_bytecode = True
DAY, HOUR = 86400, 3600
NOW = 3000 * DAY
MAX = 2 ** 53 - 1

# Owner parameters (OP-7, `21`); values assumed for the model, none decided.
PARAMS = {"pin_max_validity_days": 30, "c3_currency_window_hours": 168, "max_anchor_age_days": 180, "witness_max_validity_hours": 168,
          "witness_c3_min_threshold": 2, "clock_skew_seconds": 300, "root_registered_source": False}
# Revision-4 rules; each mutant flips exactly one back to a review-r3 defect.
RULES = {"anchor_semantics": "inclusion", "pin_validity": True, "pin_integrity": True, "witness_purpose": "freshness-witness",
         "c3_requires_currency": True, "a7_high_water": "accepted_tbm", "source_binding": True, "lift_post_dating": True,
         "clock_high_water_witness_only": True}
MUTANTS = {
    "M-sequence-anchor": {"anchor_semantics": "sequence"},                   # RV3-H2 (1): anchor met by a sequence number
    "M-pin-without-currency-bound": {"pin_validity": False},                 # RV3-H2 (2): pins without validity
    "M-threshold-1-trust-state-witness": {"witness_purpose": "trust-state"}, # RV3-H2 (3): witness = threshold-1 trust-state TSS
    "M-c3-without-currency-proof": {"c3_requires_currency": False},          # RV3-H2: C3 / binary acceptance on an aged anchor
    "M-pins-writable-by-governed-account": {"pin_integrity": False},         # RV3-M2
    "M-a7-against-tss-high-water": {"a7_high_water": "tss"},                 # RV3-M8
    "M-source-from-release-commit": {"source_binding": False},               # RV3-H3
    "M-lift-reuses-pre-negative-attestation": {"lift_post_dating": False},   # RV3-M1
    "M-any-issued-at-raises-clock": {"clock_high_water_witness_only": False},  # RV3-M3
}
PURPOSE_OF = {"root": "root", "tps": "trust-policy", "tss": "trust-state", "release-final": "release-final", "release-candidate": "release-candidate",
              "artifact": "release-artifact", "build-att": "build-attestation", "att": "verification-attestation", "cert": "certification-status",
              "revocation": "revocation", "witness": "freshness-witness"}
COMPILED_MIN_THRESHOLD = {"release-artifact": 2, "root": 2, "trust-policy": 2}
WHITELIST = {frozenset(p) for p in [("root", "trust-policy"), ("release-final", "release-candidate"), ("revocation", "certification-status"),
                                     ("revocation", "trust-state"), ("retrieval-profile", "release-final")]}
LOCAL_TERMINAL_ONLY = {"downgrade", "policy_lowering", "adopt_lineage", "override_kernel_integrity"}
R, P = dict(RULES), dict(PARAMS)


# ================================================================================================ statements
def grants_v1(extra=None, witness_threshold=2):
    g = {"r1": ["root", "trust-policy"], "r2": ["root", "trust-policy"], "r3": ["root", "trust-policy"], "ts1": ["trust-state", "revocation"],
         "rf1": ["release-final"], "rc1": ["release-candidate"], "ra1": ["release-artifact"], "ra2": ["release-artifact"], "ba1": ["build-attestation"],
         "va1": ["verification-attestation"], "cs1": ["certification-status"], "fw1": ["freshness-witness"], "fw2": ["freshness-witness"],
         "rp1": ["retrieval-profile"]}
    g.update(extra or {})
    thr = {"root": 2, "trust-policy": 2, "release-artifact": 2, "freshness-witness": witness_threshold}
    return g, thr


def root(v, grants=None, thresholds=None, revoked=()):
    g, t = grants_v1() if grants is None else (grants, thresholds or {})
    return {"kind": "root", "v": v, "d": f"ROOT{v}", "grants": g, "thresholds": t, "revoked": set(revoked), "signers": ["r1", "r2"], "issued_at": 0}


def tps(v, prior=(), min_seq=1, lowering_history=(), unrevokes=(), fields=None, production_sources=(), clock_reset=None):
    f = {"min_release_sequence": min_seq, "historical_releases": {"4.1.2", "4.1.3", "4.1.4", "4.1.5"}, "install_authority": {"install_kernel": 4},
         "gating_mode": "always_gate", "local_terminal_only": set(LOCAL_TERMINAL_ONLY), "op7_mode": "a", "pin_max_validity_days": 30,
         "max_anchor_age_days": 180, "witness_max_validity_hours": 168, "c3_currency_window_hours": 168, "freshness_witness_threshold": 2}
    f.update(fields or {})
    return {"kind": "tps", "v": v, "d": f"TPS{v}", "prior": set(prior), "fields": f, "lowering_history": list(lowering_history), "unrevokes": set(unrevokes),
            "production_sources": set(production_sources), "clock_reset": clock_reset, "signers": ["r1", "r2"], "issued_at": 0}


def tss(seq, d, prior=(), root_v=1, pol=(1, "TPS1"), revs=(), certs=(), atts=(), arts=(), issued_at=0, expires_at=None, signers=("ts1",)):
    return {"kind": "tss", "seq": seq, "d": d, "prior": set(prior), "root_v": root_v, "pol": tuple(pol), "revs": set(revs), "certs": set(certs),
            "atts": set(atts), "arts": set(arts), "issued_at": issued_at, "expires_at": expires_at, "signers": list(signers)}


def witness(d, tss_seq, tss_d, issued_at, expires_at, signers=("fw1", "fw2")):
    return {"kind": "witness", "d": d, "seq": tss_seq, "tss_d": tss_d, "issued_at": issued_at, "expires_at": expires_at, "signers": list(signers)}


def release(d, seq, stage="final", source=("commit-good", "tree-good", "inputs-good"), kernel_tree="K1", promoted_from=None, refs=(1, 1, 1), signers=None, issued_at=0):
    kind = "release-final" if stage == "final" else "release-candidate"
    return {"kind": kind, "d": d, "seq": seq, "stage": stage, "source": tuple(source), "tree": kernel_tree, "promoted_from": promoted_from,
            "refs": {"state": refs[0], "policy": refs[1], "root": refs[2]}, "signers": list(signers or (["rf1"] if stage == "final" else ["rc1"])), "issued_at": issued_at}


def attest(d, candidate, verdict="ACCEPTED", source=("commit-good", "tree-good", "inputs-good"), lifts_negative=None, signers=("va1",), issued_at=0):
    return {"kind": "att", "d": d, "candidate": candidate, "verdict": verdict, "source": tuple(source), "lifts_negative": lifts_negative, "signers": list(signers), "issued_at": issued_at}


def cert(d, rel, status, cseq, att=None, signers=("cs1",), issued_at=0):
    return {"kind": "cert", "d": d, "rel": rel, "status": status, "cseq": cseq, "att": att, "signers": list(signers), "issued_at": issued_at}


def revocation(d, targets, signers=("ts1",), issued_at=0):
    return {"kind": "revocation", "d": d, "targets": set(targets), "signers": list(signers), "issued_at": issued_at}


def build_att(artifact, tbm_d, source, signers=("ba1",)):
    return {"kind": "build-att", "d": f"BA-{artifact}", "artifact": artifact, "tbm": tbm_d, "source": tuple(source), "signers": list(signers), "issued_at": 0}


def artifact(digest, release_d, tbm, signers=("ra1", "ra2")):
    return {"kind": "artifact", "d": f"AS-{digest}", "digest": digest, "release": release_d, "tbm": tbm, "signers": list(signers), "issued_at": 0}


def tbm(d, tps_v, tps_d, tss_seq, tss_d, embedded, source=("commit-good", "tree-good", "inputs-good"), root_v=1):
    return {"d": d, "root_v": root_v, "tps_v": tps_v, "tps_d": tps_d, "tss_seq": tss_seq, "tss_d": tss_d, "embedded_release": embedded, "source": tuple(source)}


# ================================================================================================ SV-6/SV-7 and ingest (17 S1; CR-06)
def eff_root_stmt(K):
    rs = [s for s in K if s["kind"] == "root"]
    return max(rs, key=lambda s: s["v"]) if rs else root(1)


def valid_signers(s, rootS):
    purpose = PURPOSE_OF[s["kind"]]
    return sorted({k for k in s.get("signers", []) if purpose in rootS["grants"].get(k, []) and k not in rootS["revoked"]})


def verifies(s, rootS):
    if s["kind"] == "root":
        return True
    purpose = PURPOSE_OF[s["kind"]]
    thr = max(rootS["thresholds"].get(purpose, 1), COMPILED_MIN_THRESHOLD.get(purpose, 1))
    return len(valid_signers(s, rootS)) >= thr


def ingest(K_all, machine, now):
    """Only verified statements enter knowledge. A statement issued in the future beyond the compiled skew is refused and
    never raises the clock high-water; only freshness-witness statements raise it (CR-06); a root-signed TPS clock_reset lowers it."""
    rootS = eff_root_stmt(K_all)
    K, refused = [], []
    for s in K_all:
        if not verifies(s, rootS):
            refused.append({"d": s.get("d"), "reason": "SIGNATURE_OR_PURPOSE"})
            continue
        if R["clock_high_water_witness_only"] and s.get("issued_at", 0) > now + P["clock_skew_seconds"]:
            refused.append({"d": s.get("d"), "reason": "STATEMENT_ISSUED_IN_FUTURE"})
            continue
        K.append(s)
    hw = machine.get("vts", {}).get("clock_high_water", 0)
    sources = [s for s in K if s["kind"] == "witness"] if R["clock_high_water_witness_only"] else K
    hw = max([hw] + [s.get("issued_at", 0) for s in sources])
    resets = [t["clock_reset"] for t in K if t["kind"] == "tps" and t.get("clock_reset") is not None]
    if resets and R["clock_high_water_witness_only"]:
        hw = min(hw, max(resets))
    return K, refused, hw


# ================================================================================================ 17 S2–S5 revision 4
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


def _chain(t):
    return t["prior"] | {(t["seq"], t["d"])}


def trust_state(K, anchors=()):
    """S4 revision 4. With anchors (inclusion semantics): only resolved TSSs whose cumulative chain contains every anchored
    (sequence, digest), where each anchored statement is held, can be effective. Held TSSs at or below the top anchor outside
    that chain are orphans; those above it are unchained (a key-compromise signal, reported, never effective)."""
    er = eff_root_stmt(K)["v"]
    pol = tps_state(K)
    if pol["status"] == "EQUIVOCATION":
        return {"status": "EQUIVOCATION", "eff": None, "seq": 0, "effective_tss": None, "below_anchor": False, "orphans": [], "unchained_above_anchor": []}
    held_pol = {(s["v"], s["d"]) for s in K if s["kind"] == "tps"}
    uniq = {}
    for t in (s for s in K if s["kind"] == "tss"):
        uniq[(t["seq"], t["d"])] = t
    ts = sorted(uniq.values(), key=lambda t: (t["seq"], t["d"]))
    resolved = [t for t in ts if t["root_v"] <= er and t["pol"] in held_pol]
    unresolved = [t for t in ts if t not in resolved]
    held = {(t["seq"], t["d"]) for t in resolved}
    orphans, unchained, below = [], [], False
    base = resolved
    if anchors:
        top = max(anchors, key=lambda a: a["seq"])
        if R["anchor_semantics"] == "inclusion":
            top_stmt = next((t for t in resolved if (t["seq"], t["d"]) == (top["seq"], top["digest"])), None)
            cands = [t for t in resolved if all((a["seq"], a["digest"]) in held and (a["seq"], a["digest"]) in _chain(t) for a in anchors)]
            ancestors = [t for t in resolved if top_stmt is not None and (t["seq"], t["d"]) in top_stmt["prior"]] if cands else []
            in_chain = ancestors + [t for t in cands if t not in ancestors]
            others = [t for t in resolved if t not in in_chain]
            orphans = [t["d"] for t in others if t["seq"] <= top["seq"]]
            unchained = [t["d"] for t in others if t["seq"] > top["seq"]]
            below = not cands
            base = sorted(in_chain, key=lambda t: (t["seq"], t["d"]))
        else:  # revision-3 reading: orphans only when the anchored TSS is held; satisfaction by sequence number (freshness())
            at = next((t for t in resolved if (t["seq"], t["d"]) == (top["seq"], top["digest"])), None)
            if at:
                orphans = [t["d"] for t in resolved if t["seq"] <= at["seq"] and (t["seq"], t["d"]) not in _chain(at)]
                base = [t for t in resolved if t["d"] not in orphans]
    byseq = {}
    for t in base:
        byseq.setdefault(t["seq"], set()).add(t["d"])
    if any(len(v) > 1 for v in byseq.values()):
        return {"status": "EQUIVOCATION", "eff": None, "seq": 0, "effective_tss": None, "below_anchor": below, "orphans": orphans, "unchained_above_anchor": unchained}
    adm, non = [], []
    for t in base:
        ok = all(t["revs"] >= l["revs"] and t["atts"] >= l["atts"] and t["arts"] >= l["arts"] and t["root_v"] >= l["root_v"] and t["pol"][0] >= l["pol"][0]
                 and (l["seq"], l["d"]) in t["prior"] for l in adm)
        (adm if ok else non).append(t)
    eff = adm[-1] if adm else None
    status = "KNOWN"
    if eff and (any(n["seq"] > eff["seq"] for n in non) or unchained):
        status = "REGRESSION"
    inc = [u["seq"] for u in unresolved if eff is None or u["seq"] > eff["seq"]]
    if status == "KNOWN" and inc:
        status = "INCOMPLETE"
    return {"status": status, "eff": eff, "seq": eff["seq"] if eff else 0, "effective_tss": eff["d"] if eff else None, "below_anchor": below,
            "non_admissible": [n["d"] for n in non], "incomplete": inc, "orphans": orphans, "unchained_above_anchor": unchained}


def negative_set(K, ts, tps_eff):
    """S5 + MS-2 revision 4 (CR-01): a negative certification is lifted only by a higher CERTIFIED referenced by the effective
    TSS whose ACCEPTED attestation is referenced by the same TSS AND names the latest negative statement (post-dates it)."""
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
        latest_neg = {c["d"] for c in negs if c["cseq"] == top}
        Rl = next((s for s in K if s["kind"] == "release-final" and s["d"] == rel_d), None)
        lifted = False
        for c in cs:
            if c["status"] == "CERTIFIED" and c["cseq"] > top and eff and (rel_d, c["d"]) in eff["certs"]:
                a = next((x for x in K if x["kind"] == "att" and x["d"] == c["att"] and x["verdict"] == "ACCEPTED"), None)
                if a and a["d"] in eff["atts"] and (Rl is None or Rl["promoted_from"] is None or a["candidate"] == Rl["promoted_from"]):
                    if not R["lift_post_dating"] or a.get("lifts_negative") in latest_neg:
                        lifted = True
        if not lifted:
            N.add(rel_d)
    return N


# ================================================================================================ 24 anchors, currency, OP-7 (revision 4)
def honoured_pins(machine, now, clock_ok):
    out, ignored = [], []
    for p in machine.get("pins", []):
        if R["pin_integrity"] and p.get("writable_by_euid") and not p.get("read_only_mount"):
            ignored.append({"pin": p["seq"], "reason": "PIN_WRITABLE_BY_GOVERNED_ACCOUNT"})
            continue
        if R["pin_validity"]:
            vu = p.get("valid_until")
            if vu is None or not clock_ok or not (p["provisioned_at"] <= now <= vu) or vu - p["provisioned_at"] > P["pin_max_validity_days"] * DAY:
                ignored.append({"pin": p["seq"], "reason": "PIN_OUTSIDE_VALIDITY"})
                continue
        out.append({"seq": p["seq"], "digest": p["digest"], "at": p["provisioned_at"], "method": "pin"})
    return out, ignored


def witness_for(K, ts, machine, now, clock_ok):
    eff = ts.get("eff")
    if not eff or not clock_ok:
        return None
    hwi = machine.get("vts", {}).get("highest_witness_issued_at", -1)
    if R["witness_purpose"] == "trust-state":  # revision-3 defect: the effective TSS with expires_at is its own witness
        if eff.get("expires_at") and eff["expires_at"] > now and eff["issued_at"] >= hwi and eff["expires_at"] - eff["issued_at"] <= P["witness_max_validity_hours"] * HOUR:
            return {"seq": eff["seq"], "valid_signers": 99, "expires_at": eff["expires_at"], "by": "trust-state (threshold 1)"}
        return None
    rootS = eff_root_stmt(K)
    best = None
    for w in (s for s in K if s["kind"] == "witness"):
        if (w["seq"], w["tss_d"]) != (eff["seq"], eff["d"]):
            continue
        if not (w["issued_at"] <= now + P["clock_skew_seconds"] and now <= w["expires_at"] and w["expires_at"] - w["issued_at"] <= P["witness_max_validity_hours"] * HOUR):
            continue
        if w["issued_at"] < hwi:
            continue
        cand = {"seq": w["seq"], "valid_signers": len(valid_signers(w, rootS)), "expires_at": w["expires_at"], "by": "freshness-witness"}
        if best is None or cand["valid_signers"] > best["valid_signers"]:
            best = cand
    return best


def freshness(K, ts, machine, now, op7, clock_hw=0, gate_fingerprint=None):
    """Freshness axis and permitted operation classes (24 §4 revision 4). No surface ever says `current`: anchored machines
    show the anchor, its method, as-of time and age, and a currency proof or CURRENCY_UNPROVEN."""
    clock_ok = now >= clock_hw
    if ts["status"] in ("EQUIVOCATION", "REGRESSION"):
        return {"axis": ts["status"], "allowed": ["C0"], "proof": None}
    vts_anchors = [dict(a) for a in machine.get("vts", {}).get("anchors", [])]
    pins, ignored = honoured_pins(machine, now, clock_ok)
    anchors = vts_anchors + pins
    eff, seq = ts.get("eff"), ts["seq"]
    wit = witness_for(K, ts, machine, now, clock_ok) if op7 == "c" else None
    if anchors:
        top = max(anchors, key=lambda a: a["seq"])
        if R["anchor_semantics"] == "inclusion":
            if ts.get("below_anchor"):
                return {"axis": f"BELOW_ANCHOR(anchored ({top['seq']},{top['digest']}) not held in the effective chain)", "allowed": ["C0"], "proof": None, "ignored_pins": ignored}
        else:
            if seq < top["seq"]:
                return {"axis": f"BELOW_ANCHOR(have {seq} < {top['seq']})", "allowed": ["C0"], "proof": None, "ignored_pins": ignored}
            if any(t["kind"] == "tss" and t["seq"] == top["seq"] and t["d"] != top["digest"] for t in K):
                return {"axis": "EQUIVOCATION(anchor digest)", "allowed": ["C0"], "proof": None}
        latest = max(anchors, key=lambda a: a["at"])
        age = now - latest["at"]
        proof = None
        if not R["c3_requires_currency"]:
            proof = "anchor (revision-3 rule: any anchor)"
        elif gate_fingerprint and eff and gate_fingerprint == (eff["seq"], eff["d"]):
            proof = "in-gate state fingerprint (TA-5, clockless)"
        elif clock_ok and 0 <= age <= P["c3_currency_window_hours"] * HOUR:
            proof = f"{latest['method']} anchored within the C3 currency window"
        elif wit and wit["valid_signers"] >= P["witness_c3_min_threshold"]:
            proof = "freshness witness at the C3 threshold"
        allowed = ["C0", "C1"]
        c2 = ts["status"] == "KNOWN" and not (op7 == "b" and (not clock_ok or age > P["max_anchor_age_days"] * DAY))
        if c2:
            allowed.append("C2")
            if proof:
                allowed.append("C3")
        label = f"ANCHORED({top['seq']}, {top['method']}, as-of {int(latest['at'] / DAY)}, age {int(age / DAY)}d; held {seq})" + (f" CURRENCY({proof})" if proof else " CURRENCY_UNPROVEN")
        if ts["status"] == "INCOMPLETE":
            label += " INCOMPLETE"
        return {"axis": label, "allowed": allowed, "proof": proof, "ignored_pins": ignored}
    if op7 == "c" and wit:
        allowed = ["C0", "C1"] + (["C2"] if ts["status"] == "KNOWN" else [])
        if ts["status"] == "KNOWN" and wit["valid_signers"] >= P["witness_c3_min_threshold"]:
            allowed.append("C3")
        return {"axis": f"WITNESSED({wit['seq']}, by {wit['by']}, {wit['valid_signers']} signer(s), expires in {int((wit['expires_at'] - now) / HOUR)}h)", "allowed": allowed,
                "proof": "freshness witness" if "C3" in allowed else None, "ignored_pins": ignored}
    if op7 == "d":
        return {"axis": f"UNANCHORED(FRESHNESS_UNPROVEN; held {seq})", "allowed": ["C0", "C1"] + (["C2"] if ts["status"] == "KNOWN" else []), "proof": None, "ignored_pins": ignored}
    return {"axis": f"UNANCHORED(held {seq})", "allowed": ["C0"], "proof": None, "ignored_pins": ignored}


def evaluate_machine(K_all, machine, now, op7, gate_fingerprint=None):
    K, refused, hw = ingest(K_all, machine, now)
    clock_ok = now >= hw
    pins, _ = honoured_pins(machine, now, clock_ok)
    anchors = [dict(a) for a in machine.get("vts", {}).get("anchors", [])] + pins
    ts = trust_state(K, anchors)
    fr = freshness(K, ts, machine, now, op7, hw, gate_fingerprint)
    return K, ts, fr, {"refused_at_ingest": refused, "clock_high_water": hw}


# ================================================================================================ 19 §6 eligibility (parts used)
def eligible_use(Rl, K, ts, tpsS, project_record_seq=None):
    N = negative_set(K, ts, tpsS["eff"])
    why = []
    if Rl["stage"] != "final":
        why.append("candidate")
    if tpsS["eff"] and Rl["seq"] < tpsS["eff"]["fields"]["min_release_sequence"]:
        why.append("below_min_release_sequence")
    if Rl["d"] in N:
        why.append("revoked")
    if project_record_seq is not None and Rl["seq"] < project_record_seq:
        why.append("downgrade_without_transaction")
    return {"eligible": not why, "reasons": why}


def ingress_ok(Rl, K, ts, tpsS, fr):
    why = list(eligible_use(Rl, K, ts, tpsS)["reasons"])
    if ts["status"] != "KNOWN":
        why.append("trust_state_" + ts["status"].lower())
    if "C3" not in fr["allowed"]:
        why.append("freshness:" + fr["axis"])
    if Rl["refs"]["state"] > ts["seq"]:
        why.append("references_unknown_state")
    return {"freshness_and_eligibility_ok": not why, "reasons": why}


# ================================================================================================ 19 §10.6 computed reductions (CR-10)
_OP7_STRENGTH = ["d", "c", "a", "b"]


def accept_policy(held, arriving, held_version):
    reds = []
    hf, af = held["fields"], arriving["fields"]
    if af["min_release_sequence"] < hf["min_release_sequence"]:
        reds.append("eligibility.min_release_sequence")
    if not af["historical_releases"] >= hf["historical_releases"]:
        reds.append("eligibility.historical_releases")
    if any(af["install_authority"].get(k, 0) < v for k, v in hf["install_authority"].items()):
        reds.append("install_authority")
    if hf["gating_mode"] == "always_gate" and af["gating_mode"] != "always_gate":
        reds.append("gating.mode")
    if not af["local_terminal_only"] >= hf["local_terminal_only"]:
        reds.append("gating.local_terminal_only")
    if _OP7_STRENGTH.index(af["op7_mode"]) < _OP7_STRENGTH.index(hf["op7_mode"]):
        reds.append("bootstrap.op7_mode")
    for k in ("pin_max_validity_days", "max_anchor_age_days", "witness_max_validity_hours", "c3_currency_window_hours"):
        if af[k] > hf[k]:
            reds.append("bootstrap." + k)
    if af["freshness_witness_threshold"] < hf["freshness_witness_threshold"]:
        reds.append("bootstrap.freshness_witness_threshold")
    explained = {h["subject"] for h in arriving["lowering_history"] if h["in_policy_version"] > held_version}
    un = [r for r in reds if r not in explained]
    if un:
        return {"accepted": False, "code": "TRUST_POLICY_UNDECLARED_LOWERING", "subjects": un}
    return {"accepted": True, "computed_reductions": reds, "per_project_policy_lowering_gate_required": bool(reds)}


# ================================================================================================ 05 §3 whitelist (KS-11)
def separation(grants):
    viol = []
    for key, ps in grants.items():
        ps = sorted(set(ps))
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if frozenset((ps[i], ps[j])) not in WHITELIST:
                    viol.append({"key": key, "pair": [ps[i], ps[j]]})
    return {"ok": not viol, "violations": viol}


# ================================================================================================ 25 §5 verify-artifact (revision 4)
def verify_artifact(art, K_all, machine, now, op7, gate_fingerprint=None):
    K, ts, fr, info = evaluate_machine(K_all, machine, now, op7, gate_fingerprint)
    rootS = eff_root_stmt(K)
    tpsS = tps_state(K)
    if not verifies(art, rootS):
        return "PURPOSE_NOT_GRANTED" if not valid_signers(art, rootS) else "THRESHOLD_NOT_MET"
    F = next((s for s in K if s["kind"] == "release-final" and s["d"] == art["release"]), None)
    if F is None:
        return "ARTIFACT_IDENTITY_MISMATCH"
    t = art["tbm"]
    bthr = max(rootS["thresholds"].get("build-attestation", 1), 1)
    if R["source_binding"]:
        bas = {k for b in K if b["kind"] == "build-att" and b["artifact"] == art["digest"] and b["tbm"] == t["d"] and b["source"] == t["source"] for k in valid_signers(b, rootS)}
    else:
        bas = {k for b in K if b["kind"] == "build-att" and b["artifact"] == art["digest"] and b["tbm"] == t["d"] and b["source"][0] == F["source"][0] for k in valid_signers(b, rootS)}
    if len(bas) < bthr:
        return "ARTIFACT_BUILD_UNATTESTED"
    eff = ts.get("eff")
    C = next((s for s in K if s["kind"] == "release-candidate" and s["d"] == F["promoted_from"]), None)
    if R["source_binding"]:
        if C is None or C["tree"] != F["tree"] or C["source"] != F["source"]:
            return "RELEASE_IDENTITY_MISMATCH(source)"
        if t["source"] != C["source"]:
            return "ARTIFACT_SOURCE_UNVERIFIED"
        atts = [a for a in K if a["kind"] == "att" and a["candidate"] == C["d"]]
        if any(a["verdict"] == "REJECTED" for a in atts):
            return "ARTIFACT_SOURCE_REJECTED"
        if not [a for a in atts if a["verdict"] == "ACCEPTED" and a["source"] == C["source"] and eff and a["d"] in eff["atts"]]:
            return "ARTIFACT_SOURCE_UNVERIFIED"
        if P["root_registered_source"] and (not tpsS["eff"] or C["source"] not in tpsS["eff"]["production_sources"]):
            return "ARTIFACT_SOURCE_UNREGISTERED"
    if not eff or art["digest"] not in eff["arts"]:
        return "ARTIFACT_UNREFERENCED"
    held = {("tps", s["v"]): s["d"] for s in K if s["kind"] == "tps"}
    held.update({("tss", s["seq"]): s["d"] for s in K if s["kind"] == "tss"})
    if held.get(("tps", t["tps_v"])) != t["tps_d"] or held.get(("tss", t["tss_seq"])) != t["tss_d"] or t["embedded_release"] != F["d"]:
        return "BINARY_T0_UNVERIFIED"
    if R["a7_high_water"] == "accepted_tbm":
        hwm = machine.get("vts", {}).get("accepted_tbm", {"root": 0, "tps": 0, "tss": 0})
    else:
        hwm = {"root": rootS["v"], "tps": tpsS["eff"]["v"] if tpsS["eff"] else 0, "tss": ts["seq"]}
    if t["root_v"] < hwm["root"] or t["tps_v"] < hwm["tps"] or t["tss_seq"] < hwm["tss"]:
        return "BINARY_T0_ROLLBACK"
    N = negative_set(K, ts, tpsS["eff"])
    if art["digest"] in N or F["d"] in N or (C and C["d"] in N):
        return "ARTIFACT_REVOKED"
    if "C3" not in fr["allowed"]:
        ax = fr["axis"]
        return "TRUST_STATE_UNANCHORED" if ax.startswith("UNANCHORED") else "TRUST_STATE_BELOW_ANCHOR" if ax.startswith("BELOW") else "TRUST_STATE_REGRESSION" if ax.startswith("REGRESSION") else "TRUST_STATE_CURRENCY_UNPROVEN"
    return "ACCEPTED"


# ================================================================================================ 27 §3 trust gates (revision 4)
def trust_gate_authorised(kind, digests, project, confirmations, decision_pins, tps_eff, now):
    for c in confirmations:
        if c["kind"] == kind and tuple(c["digests"]) == tuple(digests) and c["project"] == project and not c.get("consumed"):
            return {"authorised": True, "by": c["method"]}
    if kind not in tps_eff["fields"]["local_terminal_only"]:
        for p in decision_pins:
            if R["pin_integrity"] and p.get("writable_by_euid") and not p.get("read_only_mount"):
                continue
            if R["pin_validity"] and (p.get("expires_at") is None or now > p["expires_at"]):
                continue
            if p["kind"] == kind and tuple(p["digests"]) == tuple(digests) and p["project"] in (project, "*"):
                return {"authorised": True, "by": "operator_decision_pin"}
    return {"authorised": False, "code": "TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED"}


# ================================================================================================ published world (review r3 B)
TPS1, TPS2 = tps(1, min_seq=1), tps(2, prior=[(1, "TPS1")], min_seq=5)
T1 = tss(1, "t1", pol=(1, "TPS1"), issued_at=NOW - 900 * DAY)
T5 = tss(5, "t5", prior=[(1, "t1")], pol=(2, "TPS2"), issued_at=NOW - 400 * DAY)
T9 = tss(9, "t9", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - 10 * DAY)
T10 = tss(10, "t10", prior=[(1, "t1"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), revs=["R7"], issued_at=NOW - 1 * DAY)
RV7 = revocation("rv7", ["R7"], issued_at=NOW - 10 * DAY)
R6, R7, R8 = release("R6", 6, refs=(5, 2, 1)), release("R7", 7, refs=(5, 2, 1)), release("R8", 8, refs=(9, 2, 1))
ROOT1 = root(1)
T0_OLD = [ROOT1, TPS1, TPS2, T1, T5]            # binary compiled 400 days ago (compiled TSS t5)
STRIPPED = [ROOT1, TPS1, TPS2, T1, T5, R7]      # A2: installed R7; t9, t10 and rv7 removed
THIEF_T100 = tss(100, "t100x", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), issued_at=NOW, expires_at=NOW + 1 * DAY)  # trust-state key thief


def pin(seq, digest, provisioned_days_ago, validity_days=30, **kw):
    return {"seq": seq, "digest": digest, "provisioned_at": NOW - provisioned_days_ago * DAY, "valid_until": NOW - provisioned_days_ago * DAY + validity_days * DAY, **kw}


def human(seq, digest, days_ago):
    return {"vts": {"anchors": [{"seq": seq, "digest": digest, "at": NOW - days_ago * DAY, "method": "human"}]}}


# ================================================================================================ scenarios
def run_scenarios():
    S = {}

    def rec(sid, computed, claim, holds, **extra):
        S[sid] = {"computed": computed, "claim": claim, "holds": bool(holds), **extra}

    # ---------------- review r2 B1–B6 under revision 4
    K = [ROOT1, TPS1, tss(1, "t1"), tss(2, "t2", prior=[(1, "t1")]), release("R6", 6, refs=(2, 1, 1)), release("C999", 7, stage="candidate", refs=(MAX, 1, 1))]
    Kv, ts, fr, _ = evaluate_machine(K, human(2, "t2", 0), NOW, "a")
    rec("B1_candidate_reference_inflation", {"trust_state": ts["status"], "R6_ingress": ingress_ok(K[4], Kv, ts, tps_state(Kv), fr), "C999_refs_met": K[5]["refs"]["state"] <= ts["seq"]},
        "17 S7: references outside the trust-state lineage are release-local", ts["status"] == "KNOWN" and ingress_ok(K[4], Kv, ts, tps_state(Kv), fr)["freshness_and_eligibility_ok"] and not K[5]["refs"]["state"] <= ts["seq"])

    Kb = [ROOT1, TPS1, release("R6", 6, promoted_from="C6"), release("C6", 0, stage="candidate"), attest("a1", "C6", issued_at=10 * DAY),
          cert("c1", "R6", "CERTIFIED", 1, "a1"), tss(1, "t1", certs=[("R6", "c1")], atts=["a1"]), cert("c2", "R6", "WITHDRAWN", 2), cert("c3", "R6", "CERTIFIED", 3)]
    Kv, ts, _, _ = evaluate_machine(Kb, {}, NOW, "a")
    rec("B2_certification_key_alone_unwithdraws", {"R6_negative": "R6" in negative_set(Kv, ts, TPS1)}, "17 MS-2: a certification key alone lifts nothing", "R6" in negative_set(Kv, ts, TPS1))

    K3 = [ROOT1, TPS1, tss(1, "t1"), tss(2, "t2a", prior=[(1, "t1")], revs=["rv2"]), tss(2, "t2b", prior=[(1, "t1")])]
    _, ts3, fr3, _ = evaluate_machine(K3, {}, NOW, "a")
    rec("B3_same_sequence_fork", {"trust_state": ts3["status"], "allowed": fr3["allowed"]}, "17 S4(c): EQUIVOCATION, C0 only", ts3["status"] == "EQUIVOCATION" and fr3["allowed"] == ["C0"])

    K4 = [ROOT1, TPS1, tss(1, "t1"), tss(2, "t2x", prior=[(1, "t1")], root_v=999, pol=(999, "TPS999")), tss(3, "t3", prior=[(1, "t1")])]
    _, ts4, _, _ = evaluate_machine(K4, {}, NOW, "a")
    _, ts4b, fr4b, _ = evaluate_machine(K4 + [tss(9, "t9x", prior=[(1, "t1"), (3, "t3")], root_v=999, pol=(999, "TPS999"))], human(3, "t3", 0), NOW, "a")
    rec("B4_unresolvable_references", {"below": ts4["status"], "effective": ts4["effective_tss"], "above": ts4b["status"], "allowed_above": fr4b["allowed"]},
        "17 S4(a)/(e): unresolvable TSS never constrains; above the effective sequence INCOMPLETE refuses C2/C3", ts4["status"] == "KNOWN" and ts4["effective_tss"] == "t3" and ts4b["status"] == "INCOMPLETE" and "C2" not in fr4b["allowed"])

    K5 = T0_OLD + STRIPPED
    b5 = {}
    for label, machine, op7 in (("a_no_pin", {}, "a"), ("a_pin_t9_fresh", {"pins": [pin(9, "t9", 1)]}, "a"), ("a_pin_t5_stale_400d", {"pins": [pin(5, "t5", 400)]}, "a"), ("d_no_pin", {}, "d")):
        Kv, ts, fr, _ = evaluate_machine(K5, machine, NOW, op7)
        b5[label] = {"freshness": fr["axis"], "allowed": fr["allowed"], "R7_policy_root_for_C2": "C2" in fr["allowed"] and eligible_use(R7, Kv, ts, tps_state(Kv))["eligible"]}
    rec("B5_fresh_runner_old_binary_A2_swap", b5, "24 §5.2: no pin, a current pin, and a pin outside validity all refuse R7 as C2 root under (a); (d) is the stated owner residual",
        not b5["a_no_pin"]["R7_policy_root_for_C2"] and not b5["a_pin_t9_fresh"]["R7_policy_root_for_C2"] and not b5["a_pin_t5_stale_400d"]["R7_policy_root_for_C2"] and b5["d_no_pin"]["R7_policy_root_for_C2"])

    held = tps(2, fields={"install_authority": {"install_kernel": 4}})
    v4 = tps(4, prior=[(1, "TPS1"), (2, "TPS2"), (3, "TPS3")], fields={"install_authority": {"install_kernel": 3}}, lowering_history=[{"subject": "install_authority", "in_policy_version": 3}])
    v4h = tps(4, prior=[(1, "TPS1"), (2, "TPS2")], fields={"install_authority": {"install_kernel": 3}})
    rec("B6_lowering_across_skipped_version", {"cumulative": accept_policy(held, v4, 2), "hidden": accept_policy(held, v4h, 2)},
        "19 §10.6: computed against the strongest held; cumulative history; undeclared reduction invalidates", accept_policy(held, v4, 2)["accepted"] and not accept_policy(held, v4h, 2)["accepted"])

    # ---------------- HO-0001 §3.2 machine list M1–M7 (revision 4)
    GEN = [ROOT1, TPS1, TPS2, T1, T5, T9, T10, RV7]
    _, ts, fr_before, _ = evaluate_machine(GEN, {}, NOW, "a")
    _, _, fr_conf, _ = evaluate_machine(GEN, human(10, "t10", 0), NOW, "a")
    _, _, fr_withheld, _ = evaluate_machine([ROOT1, TPS1, TPS2, T1, T5], human(10, "t10", 0), NOW, "a")
    rec("M1_first_install", {"before": fr_before["allowed"], "after_confirm_state_t10": fr_conf, "source_withholds_t10": fr_withheld["axis"]},
        "24 §5.1: C3 refused until anchored; a fresh human confirmation is a currency proof; a withheld anchored epoch is BELOW_ANCHOR",
        fr_before["allowed"] == ["C0"] and "C3" in fr_conf["allowed"] and fr_withheld["axis"].startswith("BELOW_ANCHOR"))
    m2 = {"a_no_pin": evaluate_machine(STRIPPED, {}, NOW, "a")[2]["allowed"],
          "a_pin_t10_2d_intact": evaluate_machine(GEN, {"pins": [pin(10, "t10", 2)]}, NOW, "a")[2],
          "a_pin_t10_2d_stripped": evaluate_machine(STRIPPED, {"pins": [pin(10, "t10", 2)]}, NOW, "a")[2]["axis"],
          "c_witness_2_of_2_on_t10": evaluate_machine(GEN + [witness("w10", 10, "t10", NOW - 2 * HOUR, NOW + 20 * HOUR)], {}, NOW, "c")[2],
          "c_expired_witness": evaluate_machine(GEN + [witness("w10old", 10, "t10", NOW - 9 * DAY, NOW - 2 * DAY)], {}, NOW, "c")[2]["allowed"],
          "d_no_pin": evaluate_machine(STRIPPED, {}, NOW, "d")[2]["axis"]}
    rec("M2_clean_ci_runner", m2, "24 §5.2: no pin C0; a valid pin anchors (C3 within the currency window); stripped + pin BELOW_ANCHOR; witnesses at threshold admit (c); (d) labelled",
        m2["a_no_pin"] == ["C0"] and "C3" in m2["a_pin_t10_2d_intact"]["allowed"] and m2["a_pin_t10_2d_stripped"].startswith("BELOW_ANCHOR")
        and "C3" in m2["c_witness_2_of_2_on_t10"]["allowed"] and m2["c_expired_witness"] == ["C0"] and "FRESHNESS_UNPROVEN" in m2["d_no_pin"])
    KB = [ROOT1, TPS1, TPS2, T1, T5]
    m3 = {o: evaluate_machine(KB, human(5, "t5", 400), NOW, o)[2] for o in "abd"}
    m3["a_repo_intact"] = evaluate_machine(GEN, human(5, "t5", 400), NOW, "a")[2]["axis"]
    rec("M3_restored_from_backup", {k: (v if isinstance(v, str) else {"axis": v["axis"], "allowed": v["allowed"]}) for k, v in m3.items()},
        "24 §5.3: never below the restored anchor; (a)/(d) C2 at the anchor with age, never C3 without a fresh proof; (b) refuses C2 by age; intact repository raises knowledge",
        "C2" in m3["a"]["allowed"] and "C3" not in m3["a"]["allowed"] and "age 400d" in m3["a"]["axis"] and "C2" not in m3["b"]["allowed"] and "held 10" in m3["a_repo_intact"])
    _, ts4m, fr4m, _ = evaluate_machine([ROOT1, TPS1, TPS2, T1, T5], human(5, "t5", 20), NOW, "a")
    rec("M4_old_epoch", {"effective_sequence": ts4m["seq"], "freshness": fr4m["axis"], "allowed": fr4m["allowed"]}, "24 §5.4: effective state never below the retained anchor; no C3 without a fresh proof",
        ts4m["seq"] == 5 and "C3" not in fr4m["allowed"])
    m5 = {o: evaluate_machine(STRIPPED, {}, NOW, o)[2]["allowed"] for o in "abcd"}
    rec("M5_no_epoch", m5, "24 §5.5: UNANCHORED; C3 never; C2 only under (d)", all("C3" not in v for v in m5.values()) and "C2" in m5["d"] and m5["a"] == ["C0"])
    m6 = {"A_t10_after_strip": evaluate_machine(GEN, human(10, "t10", 1), NOW, "a")[2]["axis"], "B_t5_after_strip": evaluate_machine(KB, human(5, "t5", 1), NOW, "a")[2]["axis"],
          "B_after_pull": evaluate_machine(GEN, human(5, "t5", 1), NOW, "a")[2]["axis"]}
    rec("M6_two_machines", m6, "24 §5.6: each machine enforces its own anchor; B learns 10 when the PTR carries it", "held 10" in m6["A_t10_after_strip"] and "held 5" in m6["B_t5_after_strip"] and "held 10" in m6["B_after_pull"])
    m7 = {o: evaluate_machine(KB, human(5, "t5", 1095), NOW, o)[2] for o in "abcd"}
    rec("M7_offline_long_absence", {o: {"axis": v["axis"], "allowed": v["allowed"]} for o, v in m7.items()},
        "24 §5.7: (a)/(c)/(d) C2 at the anchor with age shown, never C3 without a fresh proof; (b) refuses C2 by age",
        "C2" in m7["a"]["allowed"] and "C3" not in m7["a"]["allowed"] and "C2" not in m7["b"]["allowed"] and "C2" in m7["c"]["allowed"])

    ig_ok = evaluate_machine(GEN, human(5, "t5", 1095), NOW, "a", gate_fingerprint=(10, "t10"))[2]
    ig_strip = evaluate_machine(KB, human(5, "t5", 1095), NOW, "a", gate_fingerprint=(10, "t10"))[2]
    rec("INGATE_state_fingerprint_currency", {"repo_intact_fingerprint_t10": {"axis": ig_ok["axis"], "allowed": ig_ok["allowed"]},
                                              "repo_stripped_fingerprint_t10": {"axis": ig_strip["axis"], "allowed": ig_strip["allowed"]}},
        "24 §4.4: a state fingerprint typed into the trust gate that names the effective TSS is a clockless currency proof for that C3 transition; a fingerprint naming a statement the machine does not hold as effective proves nothing",
        "C3" in ig_ok["allowed"] and "C3" not in ig_strip["allowed"])

    # ---------------- replay, forks, gates, hints
    HON = [ROOT1, TPS1, TPS2, tss(1, "t1"), tss(4, "t4", prior=[(1, "t1")]), tss(5, "t5", prior=[(1, "t1"), (4, "t4")], pol=(2, "TPS2")),
           tss(9, "t9", prior=[(1, "t1"), (4, "t4"), (5, "t5")], pol=(2, "TPS2"))]
    _, tsr, _, _ = evaluate_machine(HON + [tss(1, "t1"), tss(4, "t4", prior=[(1, "t1")])], human(9, "t9", 1), NOW, "a")
    rec("R1_signed_state_replay", {"effective": tsr["effective_tss"], "status": tsr["status"]}, "17 MS-4: replayed older genuine statements never lower knowledge", tsr["effective_tss"] == "t9" and tsr["status"] == "KNOWN")
    wmach = {"vts": {"highest_witness_issued_at": NOW - 1 * HOUR}}
    Kw = GEN + [witness("w10a", 10, "t10", NOW - 5 * HOUR, NOW + 10 * HOUR)]
    rec("R2_witness_replay", {"fresh_runner": evaluate_machine(Kw, {}, NOW, "c")[2]["axis"], "runner_saw_newer_witness": evaluate_machine(Kw, wmach, NOW, "c")[2]["allowed"]},
        "24 §6: an older witness is accepted only by a verifier that never saw a newer one", evaluate_machine(Kw, {}, NOW, "c")[2]["axis"].startswith("WITNESSED") and evaluate_machine(Kw, wmach, NOW, "c")[2]["allowed"] == ["C0"])
    rr = trust_gate_authorised("framework_update", ["X"], "P1", [], [], TPS2, NOW)
    rec("R3_gate_record_from_repository", rr, "rule (18): repository records never authorise trust decisions", not rr["authorised"])
    rec("R4_lock_hint_inflation", {"allowed": evaluate_machine(GEN, human(10, "t10", 1), NOW, "a")[2]["allowed"]}, "17 S8: hints never refuse or relax", "C2" in evaluate_machine(GEN, human(10, "t10", 1), NOW, "a")[2]["allowed"])
    fr_r5 = evaluate_machine(GEN, {"pins": [pin(10, "t10-other", 1)]}, NOW, "a")[2]
    rec("R5_pin_digest_mismatch", fr_r5["axis"], "24 §6: an anchored (sequence, digest) not held in the effective chain is BELOW_ANCHOR (C0)", fr_r5["allowed"] == ["C0"])
    rec("R6_A3_deletes_VTS", evaluate_machine(GEN, {}, NOW, "a")[2]["allowed"], "RS-3: UNANCHORED; read-only under (a)", evaluate_machine(GEN, {}, NOW, "a")[2]["allowed"] == ["C0"])
    Ke1 = [ROOT1, TPS1, tss(1, "t1"), tss(2, "t2a", prior=[(1, "t1")]), tss(5, "t5x", prior=[(1, "t1"), (2, "t2b")])]
    ts_e1 = evaluate_machine(Ke1, {}, NOW, "a")[1]
    rec("E1_fork_across_a_gap", {"status": ts_e1["status"], "effective": ts_e1["effective_tss"]}, "17 S4(d): a higher TSS omitting a held lower one is not admissible (REGRESSION)", ts_e1["status"] == "REGRESSION")
    Ke2 = [ROOT1, tps(3, prior=[(1, "TPS1")]), dict(tps(3, prior=[(1, "TPS1")]), d="TPS3b"), TPS1]
    rec("E2_trust_policy_equivocation", tps_state(Ke2)["status"], "17 S3: two TPS of one version -> EQUIVOCATION", tps_state(Ke2)["status"] == "EQUIVOCATION")
    Ke3 = HON + [tss(4, "t4x", prior=[(1, "t1")])]
    ts_e3 = evaluate_machine(Ke3, {}, NOW, "a")[1]
    ts_e3a = evaluate_machine(Ke3, human(9, "t9", 1), NOW, "a")[1]
    rec("E3_fork_without_and_with_anchor", {"no_anchor": ts_e3["status"], "anchored_t9": {"status": ts_e3a["status"], "effective": ts_e3a["effective_tss"], "orphans": ts_e3a["orphans"]}},
        "17 S4: unanchored equal-sequence fork is EQUIVOCATION; an anchor on t9 orphans the fork", ts_e3["status"] == "EQUIVOCATION" and ts_e3a["status"] == "KNOWN" and ts_e3a["orphans"] == ["t4x"])

    # ---------------- purposes
    rec("K1_trust_state_with_certification", separation({"k1": ["trust-state", "certification-status"]}), "05 KS-8: forbidden pair", not separation({"k1": ["trust-state", "certification-status"]})["ok"])
    rec("K2_release_artifact_with_release_final", separation({"k1": ["release-artifact", "release-final"]}), "05 KS-9: release-artifact shares with nothing", not separation({"k1": ["release-artifact", "release-final"]})["ok"])
    rec("K3_whitelisted_owner_matrix", separation(grants_v1()[0]), "05 §3: the default grants satisfy the whitelist", separation(grants_v1()[0])["ok"])
    rec("K4_freshness_witness_with_trust_state", separation({"k1": ["freshness-witness", "trust-state"]}), "05 KS-11: freshness-witness shares with no purpose", not separation({"k1": ["freshness-witness", "trust-state"]})["ok"])

    # ---------------- binary acceptance with realisable constructions (RV3-M8)
    C11 = release("C11", 0, stage="candidate")
    F11 = release("F11", 11, promoted_from="C11", refs=(9, 2, 1))
    A11 = attest("a11", "C11")
    TBM9 = tbm("tbm-f11", 2, "TPS2", 9, "t9", "F11")                      # names t9, which exists before the build
    ART = artifact("A-f11", "F11", TBM9)
    T11 = tss(11, "t11", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=["R7"], atts=["a11"], arts=["A-f11"], issued_at=NOW - 2 * HOUR)
    BIN_WORLD = GEN + [C11, F11, A11, T11, build_att("A-f11", "tbm-f11", C11["source"]), ART]
    anchored_now = human(11, "t11", 0)
    anchored_now["vts"]["accepted_tbm"] = {"root": 1, "tps": 2, "tss": 5}
    bcases = {
        "A27_release_final_key_signs_artifact": (dict(ART, signers=["rf1"]), BIN_WORLD, anchored_now, "PURPOSE_NOT_GRANTED"),
        "A27b_one_release_artifact_key": (dict(ART, signers=["ra1"]), BIN_WORLD, anchored_now, "THRESHOLD_NOT_MET"),
        "A27c_no_build_attestation": (ART, [s for s in BIN_WORLD if s["kind"] != "build-att"], anchored_now, "ARTIFACT_BUILD_UNATTESTED"),
        "A27d_not_referenced_by_trust_state": (ART, [s for s in BIN_WORLD if s is not T11] + [dict(T11, arts=set())], anchored_now, "ARTIFACT_UNREFERENCED"),
        "A27e_compiled_policy_digest_not_signed_policy": (dict(ART, tbm=dict(TBM9, tps_d="TPS2-forged")), BIN_WORLD, anchored_now, "BINARY_T0_UNVERIFIED"),
        "A28_genuine_older_binary_below_accepted_tbm": (ART, BIN_WORLD, {"vts": {"anchors": anchored_now["vts"]["anchors"], "accepted_tbm": {"root": 1, "tps": 2, "tss": 10}}}, "BINARY_T0_ROLLBACK"),
        "A29_op4_no_candidate_final_key_signs_artifact": (dict(ART, signers=["rf1", "rc1"]), BIN_WORLD, anchored_now, "PURPOSE_NOT_GRANTED"),
        "A_valid_realisable_TBM_t9_reference_t11": (ART, BIN_WORLD, anchored_now, "ACCEPTED"),
    }
    for n, (a, Kx, m, exp) in bcases.items():
        got = verify_artifact(a, Kx, m, NOW, "a")
        rec(n, got, f"25 §5 verify-artifact: {exp}", got == exp)

    # ---------------- RV3-B-A02 stale CI pins; A03 pin writable; A04 decision pins
    a02 = {}
    for mname, p_ in (("pin_t5_image_400d", pin(5, "t5", 400)), ("pin_t5_image_100d", pin(5, "t5", 100))):
        for op7 in "abcd":
            Kv, ts, fr, _ = evaluate_machine(STRIPPED, {"pins": [p_]}, NOW, op7)
            a02[f"{mname}/{op7}"] = {"freshness": fr["axis"], "R7_C2_root": "C2" in fr["allowed"] and eligible_use(R7, Kv, ts, tps_state(Kv))["eligible"]}
    rec("RV3-B-A02_stale_ci_pin", a02, "24 §3.2 AM-3: a pin outside its validity is not an anchor; only (d) admits R7 unanchored (stated owner residual)",
        not any(v["R7_C2_root"] for k, v in a02.items() if not k.endswith("/d")))
    a03 = {}
    for label, p_ in (("owned_by_euid_0644", pin(10, "t10", 1, writable_by_euid=True)), ("root_owned_not_writable", pin(5, "t5", 1)), ("read_only_mount", pin(5, "t5", 1, writable_by_euid=True, read_only_mount=True))):
        Kv, ts, fr, _ = evaluate_machine(STRIPPED, {"pins": [p_]}, NOW, "a")
        a03[label] = {"freshness": fr["axis"], "ignored": fr.get("ignored_pins")}
    rec("RV3-B-A03_pin_written_by_governed_account", a03, "CR-03: a pin writable by the effective uid is ignored (UNANCHORED); a non-writable or read-only pin anchors",
        a03["owned_by_euid_0644"]["freshness"].startswith("UNANCHORED") and a03["root_owned_not_writable"]["freshness"].startswith("ANCHORED") and a03["read_only_mount"]["freshness"].startswith("ANCHORED"))
    dp_w = [{"kind": k, "digests": ["D1", "D2"], "project": "*", "writable_by_euid": True, "expires_at": NOW + DAY} for k in ("framework_update", "weakening", "project_strength", "downgrade")]
    dp_ok = [dict(p, writable_by_euid=False) for p in dp_w]
    a04 = {"writable": {p["kind"]: trust_gate_authorised(p["kind"], ["D1", "D2"], "P1", [], dp_w, TPS2, NOW)["authorised"] for p in dp_w},
           "not_writable": {p["kind"]: trust_gate_authorised(p["kind"], ["D1", "D2"], "P1", [], dp_ok, TPS2, NOW)["authorised"] for p in dp_ok}}
    rec("RV3-B-A04_decision_pin_integrity", a04, "CR-03/27 §3.2: a decision pin writable by the effective uid authorises nothing; a protected pin never approves local_terminal_only kinds",
        not any(a04["writable"].values()) and a04["not_writable"]["framework_update"] and not a04["not_writable"]["downgrade"])

    # ---------------- RV3-B-A05 lift (CR-01)
    Kl = Kb + [cert("c4", "R6", "CERTIFIED", 4, "a1"), tss(2, "t2", prior=[(1, "t1")], certs=[("R6", "c1"), ("R6", "c4")], atts=["a1"])]
    Kv, tsl, _, _ = evaluate_machine(Kl, {}, NOW, "a")
    reuse_negative = "R6" in negative_set(Kv, tsl, TPS1)
    Kl2 = Kb + [attest("a2", "C6", lifts_negative="c2"), cert("c4", "R6", "CERTIFIED", 4, "a2"), tss(2, "t2", prior=[(1, "t1")], certs=[("R6", "c1"), ("R6", "c4")], atts=["a1", "a2"])]
    Kv2, tsl2, _, _ = evaluate_machine(Kl2, {}, NOW, "a")
    lifted = "R6" not in negative_set(Kv2, tsl2, TPS1)
    rec("RV3-B-A05_lift_requires_post_dating_attestation", {"reusing_pre_withdrawal_attestation_negative_remains": reuse_negative, "new_attestation_naming_the_withdrawal_lifts": lifted,
                                                            "distinct_keys_for_the_lift": ["va1 (verification-attestation)", "cs1 (certification-status)", "ts1 (trust-state)"]},
        "17 MS-2 / CR-01: a lift needs an attestation that names the negative statement; three distinct keys", reuse_negative and lifted)

    # ---------------- RV3-B-A06 witness authority
    thief_tss_expiring = tss(100, "t100w", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), issued_at=NOW, expires_at=NOW + DAY)
    a06 = {"trust_state_key_alone_expiring_tss": evaluate_machine(STRIPPED + [thief_tss_expiring], {}, NOW, "c")[2],
           "one_freshness_witness_key_stolen_threshold_2": evaluate_machine(STRIPPED + [witness("wx", 5, "t5", NOW, NOW + DAY, signers=("fw1",))], {}, NOW, "c")[2]}
    ROOT_W1 = root(1, *grants_v1(witness_threshold=1))
    w1world = [ROOT_W1] + STRIPPED[1:] + [witness("wx1", 5, "t5", NOW, NOW + DAY, signers=("fw1",))]
    a06["owner_option_witness_threshold_1_one_key_stolen"] = evaluate_machine(w1world, {}, NOW, "c")[2]
    rec("RV3-B-A06_witness_authority", {k: {"axis": v["axis"], "allowed": v["allowed"]} for k, v in a06.items()},
        "24 §3.3 / KS-11: a trust-state key cannot mint currency; one of two witness keys witnesses nothing; under owner threshold 1 a thief reaches C1-C2 only, never C3",
        a06["trust_state_key_alone_expiring_tss"]["allowed"] == ["C0"] and a06["one_freshness_witness_key_stolen_threshold_2"]["allowed"] == ["C0"]
        and "C3" not in a06["owner_option_witness_threshold_1_one_key_stolen"]["allowed"])

    # ---------------- RV3-B-A07 issued_at poisoning (CR-06)
    POISON = release("CP", 0, stage="candidate", issued_at=NOW + 36500 * DAY)
    _, _, fr_b_before, info_b = evaluate_machine(GEN, human(10, "t10", 1), NOW, "b")
    _, _, fr_b_after, info_p = evaluate_machine(GEN + [POISON], human(10, "t10", 1), NOW, "b")
    w_future = witness("wf", 10, "t10", NOW + 36500 * DAY, NOW + 36501 * DAY)
    _, _, fr_c_after, info_w = evaluate_machine(GEN + [w_future, witness("wh", 10, "t10", NOW - HOUR, NOW + 20 * HOUR)], {}, NOW, "c")
    rec("RV3-B-A07_issued_at_high_water", {"b_before": fr_b_before["allowed"], "b_after_future_candidate": fr_b_after["allowed"], "future_candidate_refused": info_p["refused_at_ingest"],
                                           "c_future_witness_then_honest_witness": fr_c_after["axis"], "clock_high_water_after": info_w["clock_high_water"] <= NOW},
        "CR-06: a future issued_at is refused at ingest and never raises the clock high-water; only witnesses raise it; honest witnesses still verify",
        "C2" in fr_b_after["allowed"] and any(r["d"] == "CP" for r in info_p["refused_at_ingest"]) and fr_c_after["axis"].startswith("WITNESSED"))

    # ---------------- RV3-B-A08 (and CD3-3 variants in VA4)
    F_EVIL = release("F-evil", 12, promoted_from="C11", source=("commit-evil", "tree-evil", "inputs-good"), refs=(11, 2, 1))
    TBM_E = tbm("tbm-evil", 2, "TPS2", 11, "t11", "F-evil", source=("commit-evil", "tree-evil", "inputs-good"))
    ART_E = artifact("A-evil", "F-evil", TBM_E)
    T12 = tss(12, "t12", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11")], pol=(2, "TPS2"), revs=["R7"], atts=["a11"], arts=["A-f11", "A-evil"], issued_at=NOW - HOUR)
    K8 = BIN_WORLD + [F_EVIL, T12, build_att("A-evil", "tbm-evil", ("commit-evil", "tree-evil", "inputs-good")), ART_E]
    m8 = human(12, "t12", 0)
    got8 = verify_artifact(ART_E, K8, m8, NOW, "a")
    rec("RV3-B-A08_final_names_unverified_source", got8, "25 §5 A4b / 04 V8: a final whose source differs from its attested candidate is refused", got8 != "ACCEPTED")

    # ---------------- RV3-B-A09 playbook (CR-04)
    Kp = GEN + [tss(11, "t11a", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=["R7"], arts=["A-bad"]), revocation("rvA", ["A-bad"]),
                tss(12, "t12a", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11a")], pol=(2, "TPS2"), revs=["R7", "A-bad"], arts=["A-bad"])]
    Kv, tsp, _, _ = evaluate_machine(Kp, human(11, "t11a", 1), NOW, "a")
    rec("RV3-B-A09_playbook_revokes_never_unreferences", {"status": tsp["status"], "effective": tsp["effective_tss"], "A-bad_negative": "A-bad" in negative_set(Kv, tsp, TPS2)},
        "05 §9 / CR-04: the remedy keeps artifacts[] and adds a revocation: KNOWN(12) and ARTIFACT_REVOKED", tsp["status"] == "KNOWN" and tsp["effective_tss"] == "t12a" and "A-bad" in negative_set(Kv, tsp, TPS2))

    # ---------------- RV3-B-A10 / A11 one decision rule (CR-05)
    Ki = T0_OLD + [tss(20, "t20u", prior=[(1, "t1"), (5, "t5")], root_v=2, pol=(2, "TPS2"))]
    fi = evaluate_machine(Ki, {}, NOW, "d")[2]
    rec("RV3-B-A10_incomplete_refuses_c2_under_d", {"allowed": fi["allowed"]}, "24 §4.3 / CR-05: INCOMPLETE refuses C2 under every option", "C2" not in fi["allowed"])
    fa11 = evaluate_machine(KB, human(5, "t5", 1095), NOW, "c")[2]
    rec("RV3-B-A11_op7_c_non_witness_anchor", {"axis": fa11["axis"], "allowed": fa11["allowed"]},
        "24 §4.3 and §5.7 (one rule): under (c) a non-witness anchor follows (a): C2 at any age, C3 only with a currency proof", "C2" in fa11["allowed"] and "C3" not in fa11["allowed"])

    # ---------------- RV3-B-A12 / RV3-D-A12 anchor satisfaction
    K12 = T0_OLD + STRIPPED + [THIEF_T100]
    Kv, ts12, fr12, _ = evaluate_machine(K12, {"pins": [pin(10, "t10", 1)]}, NOW, "a")
    Kh, tsh, frh, _ = evaluate_machine(K12 + [T9, T10, RV7], {"pins": [pin(10, "t10", 1)]}, NOW, "a")
    first_install = evaluate_machine(K12, human(10, "t10", 0), NOW, "a")[2]
    rec("RV3-B-A12_RV3-D-A12_higher_unchained_tss", {"current_pin_t10": fr12["axis"], "R7_C2_root": "C2" in fr12["allowed"] and eligible_use(R7, Kv, ts12, tps_state(Kv))["eligible"],
                                                    "first_install_human_t10": first_install["axis"], "machine_holding_t10": {"status": tsh["status"], "axis": frh["axis"]}},
        "24 §4.1 inclusion anchors: the anchored statement must be held and in the effective chain; otherwise BELOW_ANCHOR; a machine holding it freezes (REGRESSION)",
        fr12["axis"].startswith("BELOW_ANCHOR") and first_install["axis"].startswith("BELOW_ANCHOR") and tsh["status"] == "REGRESSION")

    # ---------------- RV3-B-A13 matrix (review r3 B shape) + pin-window extension
    MACHINES = {
        "M1_first_install_after_ceremony_t10": {"vts": {"anchors": [{"seq": 10, "digest": "t10", "at": NOW, "method": "human"}]}},
        "M2_ci_runner_no_pin": {},
        "M2_ci_runner_pin_current_t10": {"pins": [pin(10, "t10", 1)]},
        "M2_ci_runner_pin_t5_image_400d": {"pins": [pin(5, "t5", 400)]},
        "M2_ci_runner_pin_t5_image_100d": {"pins": [pin(5, "t5", 100)]},
        "M3_restored_backup_anchor_t5_400d": human(5, "t5", 400),
        "M4_old_epoch_anchor_t5_20d": human(5, "t5", 20),
        "M5_no_epoch": {},
        "M6A_anchor_t10": human(10, "t10", 1),
        "M6B_anchor_t5": human(5, "t5", 1),
        "M7_offline_anchor_t5_1095d": human(5, "t5", 1095),
    }
    MACHINE_VTS_K = {"M3_restored_backup_anchor_t5_400d": [TPS2, T5], "M4_old_epoch_anchor_t5_20d": [TPS2, T5], "M6A_anchor_t10": [T9, T10, RV7], "M6B_anchor_t5": [TPS2, T5],
                     "M7_offline_anchor_t5_1095d": [TPS2, T5]}
    CORE = {"M3_restored_backup_anchor_t5_400d", "M4_old_epoch_anchor_t5_20d", "M6B_anchor_t5", "M7_offline_anchor_t5_1095d"}
    ADV = {"A2_A5_repository_or_transport": (STRIPPED, None), "A2_with_same_account_code_execution": (STRIPPED, "rewrite"), "A2_plus_trust_state_key": (STRIPPED + [THIEF_T100], None)}
    rows = []
    for mname, m in MACHINES.items():
        for aname, (advK, mode) in ADV.items():
            for op7 in "abcd":
                mm = copy.deepcopy(m)
                if mode == "rewrite":  # the adversary rewrites the pin file in the account configuration (CR-03: writable by the effective uid)
                    mm["pins"] = [pin(5, "t5", 0, writable_by_euid=True)]
                K = T0_OLD + MACHINE_VTS_K.get(mname, []) + advK
                Kv, ts, fr, _ = evaluate_machine(K, mm, NOW, op7)
                tpsS = tps_state(Kv)
                use = eligible_use(R7, Kv, ts, tpsS)
                ing = ingress_ok(R7, Kv, ts, tpsS, fr)
                c2 = "C2" in fr["allowed"] and use["eligible"]
                c3 = ing["freshness_and_eligibility_ok"]
                if not (c2 or c3):
                    cls = "refused"
                elif mname in CORE:
                    cls = "stated_core (anchored before the revocation; R7 never received)"
                elif fr["axis"].startswith("UNANCHORED(FRESHNESS_UNPROVEN") and not c3:
                    cls = "stated_owner_residual_OP7_d (unanchored, compiled TSS t5 older than the newest TSS; never C3)"
                else:
                    cls = "UNSTATED"
                rows.append({"machine": mname, "adversary": aname, "op7": op7, "freshness": fr["axis"], "allowed": fr["allowed"], "R7_C2_policy_root": c2, "R7_C3": c3,
                             "classification": cls, "label_says_current": "current" in fr["axis"].lower()})
    unstated = [r for r in rows if r["classification"] == "UNSTATED"]
    rec("RV3-B-A13_matrix_machine_x_op7_x_adversary", {"rows": len(rows), "R7_C2_rows": sum(r["R7_C2_policy_root"] for r in rows), "R7_C3_rows": sum(r["R7_C3"] for r in rows),
                                                      "by_classification": {c: sum(1 for r in rows if r["classification"] == c) for c in sorted({r["classification"] for r in rows})},
                                                      "unstated_rows": unstated, "rows_labelled_current": sum(r["label_says_current"] for r in rows), "matrix": rows},
        "CD3-2: only stated-core rows and the stated OP-7 (d) residual admit revoked state; no row is labelled current", not unstated and not any(r["label_says_current"] for r in rows))
    win = {}
    for label, m in (("pin_t5_provisioned_12d_before_now_valid_30d", {"pins": [pin(5, "t5", 12)]}), ("pin_t9_provisioned_2d_valid_30d", {"pins": [pin(9, "t9", 2)]})):
        Kv, ts, fr, _ = evaluate_machine(STRIPPED, m, NOW, "a")
        win[label] = {"freshness": fr["axis"], "R7_C2_root": "C2" in fr["allowed"] and eligible_use(R7, Kv, ts, tps_state(Kv))["eligible"],
                      "R7_C3": ingress_ok(R7, Kv, ts, tps_state(Kv), fr)["freshness_and_eligibility_ok"]}
    rec("PIN_WINDOW_bound", win, "RS-1b: a valid pin provisioned before a revocation admits the stale descendant for C2 only within its validity (bound pin_max_validity_days); C3 needs a proof within the C3 window",
        win["pin_t5_provisioned_12d_before_now_valid_30d"]["R7_C2_root"] and not win["pin_t5_provisioned_12d_before_now_valid_30d"]["R7_C3"] and win["pin_t9_provisioned_2d_valid_30d"]["freshness"].startswith("BELOW_ANCHOR"))

    # ---------------- RV3-D-A04 (d) scope
    d_old = evaluate_machine(T0_OLD + STRIPPED, {}, NOW, "d")
    T0_NEW = [ROOT1, TPS1, TPS2, T1, T5, T9, T10, RV7]
    d_new = evaluate_machine(T0_NEW + [R7], {}, NOW, "d")
    rec("RV3-D-A04_op7_d_scope", {"binary_compiled_t5": eligible_use(R7, d_old[0], d_old[1], tps_state(d_old[0]))["eligible"] and "C2" in d_old[2]["allowed"],
                                  "binary_compiled_t10_newest_tss": eligible_use(R7, d_new[0], d_new[1], tps_state(d_new[0]))["eligible"] and "C2" in d_new[2]["allowed"]},
        "RV3-L6: the (d) residual exposes binaries whose compiled TSS predates the newest TSS (not the newest TPS)",
        eligible_use(R7, d_old[0], d_old[1], tps_state(d_old[0]))["eligible"] and not eligible_use(R7, d_new[0], d_new[1], tps_state(d_new[0]))["eligible"])

    # ---------------- RV3-D-A13 realisable A7 construction and RV3-D-A15 revoked binary on pinned CI
    rec("RV3-D-A13_realisable_tbm_order", {"new_binary": verify_artifact(ART, BIN_WORLD, anchored_now, NOW, "a"),
                                           "older_binary_after_newer_accepted": verify_artifact(ART, BIN_WORLD, {"vts": {"anchors": anchored_now["vts"]["anchors"], "accepted_tbm": {"root": 1, "tps": 2, "tss": 10}}}, NOW, "a")},
        "25 A7 / RV3-M8: compared with the accepted-TBM high-water; TBM names t9, artefact referenced by t11",
        verify_artifact(ART, BIN_WORLD, anchored_now, NOW, "a") == "ACCEPTED")
    T4b = tss(4, "t4", prior=[(1, "t1")], pol=(2, "TPS2"))
    T5b = tss(5, "t5", prior=[(1, "t1"), (4, "t4")], pol=(2, "TPS2"), arts=["A7x"], atts=["a7x"])
    T9b = tss(9, "t9", prior=[(1, "t1"), (4, "t4"), (5, "t5")], pol=(2, "TPS2"), arts=["A7x"], atts=["a7x"], revs=["rvA"])
    T10b = tss(10, "t10", prior=[(1, "t1"), (4, "t4"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), arts=["A7x"], atts=["a7x"], revs=["rvA"])
    T100b = tss(100, "t100", prior=[(1, "t1"), (4, "t4"), (5, "t5")], pol=(2, "TPS2"), arts=["A7x"], atts=["a7x"])
    C7 = release("C7x", 0, stage="candidate")
    F7 = release("F7x", 7, promoted_from="C7x")
    TBMx = tbm("tbmx", 2, "TPS2", 4, "t4", "F7x")
    ARTx = artifact("A7x", "F7x", TBMx)
    base15 = [ROOT1, TPS1, TPS2, tss(1, "t1"), T4b, T5b, C7, F7, attest("a7x", "C7x"), build_att("A7x", "tbmx", C7["source"]), ARTx]
    a15 = {"honest_current_pin_t10": verify_artifact(ARTx, base15 + [T9b, T10b, revocation("rvA", ["A7x"])], {"pins": [pin(10, "t10", 1)]}, NOW, "a"),
           "stale_pin_t5_200d_withheld": verify_artifact(ARTx, base15, {"pins": [pin(5, "t5", 200)]}, NOW, "a"),
           "valid_pin_t5_20d_withheld": verify_artifact(ARTx, base15, {"pins": [pin(5, "t5", 20)]}, NOW, "a"),
           "current_pin_t10_withheld_plus_t100": verify_artifact(ARTx, base15 + [T100b], {"pins": [pin(10, "t10", 1)]}, NOW, "a")}
    rec("RV3-D-A15_revoked_binary_pinned_ci", a15, "CD3-2: a revoked genuine binary is never accepted by an aged, expired or bypassed anchor",
        a15["honest_current_pin_t10"] == "ARTIFACT_REVOKED" and all(v != "ACCEPTED" for v in a15.values()))

    # ---------------- RV3-D-A16 rotation playbook (L8)
    ROOT2 = root(2, grants={**grants_v1()[0], "ts1": [], "ts2": ["trust-state", "revocation"]}, thresholds=grants_v1()[1], revoked=["ts1"])
    signed_ts1 = [T1, T5, T9, T10]
    resigned = [dict(t, signers=["ts2"]) for t in signed_ts1]
    no_resign = evaluate_machine([ROOT1, ROOT2, TPS1, TPS2] + signed_ts1, human(10, "t10", 1), NOW, "a")[2]["axis"]
    with_resign = evaluate_machine([ROOT1, ROOT2, TPS1, TPS2] + resigned, human(10, "t10", 1), NOW, "a")[2]["axis"]
    rec("RV3-D-A16_rotation_resigns_retained_statements", {"without_resigning": no_resign, "with_resigned_history": with_resign},
        "05 §9 / RV3-L8: the playbook re-signs retained statements (same payload digests) before root N+1; anchors stay satisfied",
        with_resign.startswith("ANCHORED") and no_resign.startswith("BELOW_ANCHOR"))

    # ---------------- CR-10 non-surface TPS reductions
    heldp = tps(3)
    subjects = {"min_release_sequence": {"min_release_sequence": 0}, "historical_releases": {"historical_releases": {"4.1.2"}}, "gating_mode": {"gating_mode": "fresh_certified_may_skip_update_gate"},
                "local_terminal_only": {"local_terminal_only": {"downgrade"}}, "op7_mode": {"op7_mode": "d"}, "pin_max_validity_days": {"pin_max_validity_days": 365},
                "freshness_witness_threshold": {"freshness_witness_threshold": 1}}
    cr10 = {k: accept_policy(heldp, tps(4, fields=v), 3) for k, v in subjects.items()}
    rec("CR-10_non_surface_tps_reductions", cr10, "19 §10.6: every non-surface TPS field lowering needs a lowering_history entry (else TRUST_POLICY_UNDECLARED_LOWERING)",
        all(not v["accepted"] for v in cr10.values()))
    # ---------------- trust-state key blast radius (17 §15 restated)
    thief_drops_revocation = tss(11, "t11thief", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], pol=(2, "TPS2"), revs=[])
    bl = evaluate_machine(GEN + [thief_drops_revocation], human(10, "t10", 1), NOW, "a")
    rec("TS_KEY_BLAST_RADIUS", {"anchored_machine_receives_tss_dropping_revocation": bl[1]["status"], "allowed": bl[2]["allowed"]},
        "17 §15: a trust-state key alone cannot lift a negative on an anchored machine: a descendant dropping a revocation is not admissible (freeze)", bl[1]["status"] == "REGRESSION" and bl[2]["allowed"] == ["C0"])
    return S


def run_with(overrides):
    global R
    saved = dict(R)
    R = dict(RULES)
    R.update(overrides)
    try:
        return run_scenarios()
    finally:
        R = saved


def main():
    base = run_with({})
    oracle = {}
    for name, ov in MUTANTS.items():
        try:
            res = run_with(ov)
            killed = sorted(k for k, v in res.items() if base[k]["holds"] and not v["holds"])
            oracle[name] = {"rule_changed": ov, "scenarios_that_fail": killed, "killed": bool(killed)}
        except Exception as e:  # a mutant that crashes the model is reported, never treated as killed
            oracle[name] = {"rule_changed": ov, "error": repr(e), "killed": False}
    matrix = base["RV3-B-A13_matrix_machine_x_op7_x_adversary"]["computed"]
    summary = {"scenarios": len(base), "holding": sum(v["holds"] for v in base.values()), "failing": sorted(k for k, v in base.items() if not v["holds"]),
               "oracle_mutants": len(MUTANTS), "mutants_killed": sum(o["killed"] for o in oracle.values()),
               "mutants_not_killed": sorted(k for k, o in oracle.items() if not o["killed"]),
               "matrix": {k: matrix[k] for k in ("rows", "R7_C2_rows", "R7_C3_rows", "by_classification", "rows_labelled_current")}, "unstated_matrix_rows": len(matrix["unstated_rows"]),
               "params": PARAMS}
    print(json.dumps({"summary": summary, "conformance_oracle": oracle, "scenarios": base}, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))


if __name__ == "__main__":
    main()
