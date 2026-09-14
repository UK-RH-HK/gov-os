#!/usr/bin/env python3
"""RV4-B-M — independent reference model of RoT-1 revision 4 (review r4 reviewer B, AR-0006).

Written from the revision-4 text at bca05a7 — 17 §5 (S1–S12), 24 §3–§4 and §8–§10, 25 §5–§9, 05 §3 and §7, 07 §7,
06 §2, 27 §3 — without reading or importing the architect's P4r4 model. Where the two agree, that is a reproduction;
where the text is ambiguous the reading used is stated in the scenario.

Signatures are modelled as key ids checked against root grants, revocations and thresholds (SV-4…SV-7); cryptography is
not modelled. Time is in seconds. No files, no subprocesses. Output: JSON on stdout.

Sections
  R   re-execution against revision 4 of review r3 reviewer B's constructions RV3-B-A02, A03, A04, A05, A06, A07, A08,
      A09, A10, A11, A12 and synthesis D's RV3-D-A04, A12, A13, A15 (shapes from those reviews; rules revision 4).
  MX  HO-0001 §3.2 machine classes × OP-7 (a)–(d) × adversaries (repository/transport strip; + trust-state key;
      + witness keys at threshold; + one witness key; + clock (A13, TA-7); + same-account unconfined code (A3, RS-3);
      + pin provisioned by a repository-controlled job (TA-9 violated, RS-4)). What each class accepts: revoked R7 as a
      C2 policy root; revoked R7 at C3 ingress; revoked binary B7 via verify-artifact. Every accepting row is classified
      against the residuals the pack states.
  PS  parameter sweep of OP-7 parameters: the longest staleness a repository/transport adversary can impose per class.
  BC  binary acceptance: every subset of stolen keys and pipeline input, with honest custodians acting exactly on their
      stated pre-signing checks (05 §7 rules 2–7, 25 §9, 07 §7), under OP-2 (S0)–(S3), OP-4 yes/no and 1 or 2 rebuilders.
      Reports the minimal capability sets that yield an accepted malicious production binary (RV4-B-A01, A02).
  FB  first-binary bootstrap (06 §2 step 6; 25 §6): independent tooling checking A2–A6 only, against a revoked binary and
      a remediated compromised binary (RV4-B-A03).
  AT  the accepted-TBM high-water: stateless machines, and a first-run record by a binary whose TBM does not resolve (RV4-B-A11).
  LB  label and decision-rule consistency: P1 "published as of" for a statement issued after the proof; WITNESSED C3
      versus the §4.4 currency-proof definition; RS-2's rollback bound under OP-7 (a) (RV4-B-A12, A13).
"""
import itertools, json, sys

sys.dont_write_bytecode = True
DAY, HOUR = 86400, 3600
NOW = 10000 * DAY
SKEW = 300
C3_WITNESS_MIN = 2  # 24 §3.3 compiled minimum
DEFAULT = {"pin_max_validity_days": 30, "c3_window_hours": 168, "max_anchor_age_days": 180, "witness_validity_hours": 168}

# ------------------------------------------------------------------------------------------------ keys, root
PURPOSE = {"tps": "trust-policy", "tss": "trust-state", "revocation": "revocation", "final": "release-final", "candidate": "release-candidate",
           "vatt": "verification-attestation", "batt": "build-attestation", "artifact": "release-artifact", "cert": "certification-status",
           "witness": "freshness-witness"}
COMPILED_MIN = {"release-artifact": 2}


def grants(op4_no=False, va2=False, ba2=False, witness_thr=2):
    g = {"ts1": {"trust-state"}, "rv1": {"revocation"}, "rf1": {"release-final"}, "rc1": {"release-candidate"}, "va1": {"verification-attestation"},
         "va2": {"verification-attestation"}, "ba1": {"build-attestation"}, "ba2": {"build-attestation"}, "ra1": {"release-artifact"},
         "ra2": {"release-artifact"}, "cs1": {"certification-status"}, "fw1": {"freshness-witness"}, "fw2": {"freshness-witness"}}
    if op4_no:
        g.pop("rc1")
        g["rf1"] = {"release-final", "release-candidate"}
    thr = {"trust-state": 1, "revocation": 1, "release-final": 1, "release-candidate": 1, "verification-attestation": 2 if va2 else 1,
           "build-attestation": 2 if ba2 else 1, "release-artifact": 2, "certification-status": 1, "freshness-witness": witness_thr}
    return {"kind": "root", "v": 1, "grants": g, "thr": thr, "revoked": set()}


def vkeys(s, root):
    p = PURPOSE[s["kind"]]
    return {k for k in s.get("signers", ()) if p in root["grants"].get(k, ()) and k not in root["revoked"]}


def verifies(s, root):
    if s["kind"] in ("root", "tps"):
        return True  # root-threshold statements are genuine in every world here
    p = PURPOSE[s["kind"]]
    return len(vkeys(s, root)) >= max(root["thr"].get(p, 1), COMPILED_MIN.get(p, 1))


# ------------------------------------------------------------------------------------------------ statements
def TPS(v, issued, sources=None):
    return {"kind": "tps", "v": v, "d": f"TPS{v}", "issued": issued, "production_sources": set(sources or ())}


def TSS(seq, d, prior, issued, revs=(), arts=(), atts=(), pol=(2, "TPS2"), signers=("ts1",)):
    return {"kind": "tss", "seq": seq, "d": d, "prior": frozenset(prior), "issued": issued, "revs": frozenset(revs), "arts": frozenset(arts),
            "atts": frozenset(atts), "pol": pol, "signers": tuple(signers)}


def REV(d, targets, issued, signers=("rv1",)):
    return {"kind": "revocation", "d": d, "targets": frozenset(targets), "issued": issued, "signers": tuple(signers)}


def WIT(d, seq, tss_d, issued, expires, signers=("fw1", "fw2")):
    return {"kind": "witness", "d": d, "seq": seq, "tss_d": tss_d, "issued": issued, "expires": expires, "signers": tuple(signers)}


def CAND(d, source, tree="K", signers=("rc1",), issued=0):
    return {"kind": "candidate", "d": d, "source": source, "tree": tree, "signers": tuple(signers), "issued": issued}


def FINAL(d, seq, cand, source, tree="K", signers=("rf1",), issued=0):
    return {"kind": "final", "d": d, "seq": seq, "promoted_from": cand, "source": source, "tree": tree, "signers": tuple(signers), "issued": issued}


def VATT(d, cand, verdict, source, signers=("va1",), issued=0):
    return {"kind": "vatt", "d": d, "candidate": cand, "verdict": verdict, "source": source, "signers": tuple(signers), "issued": issued}


def BATT(d, art, tbm_d, source, signers=("ba1",), issued=0):
    return {"kind": "batt", "d": d, "artifact": art, "tbm": tbm_d, "source": source, "signers": tuple(signers), "issued": issued}


def ART(d, release, tbm, signers=("ra1", "ra2"), issued=0):
    return {"kind": "artifact", "d": d, "release": release, "tbm": tbm, "signers": tuple(signers), "issued": issued}


def TBM(d, source, tss, tps=(2, "TPS2"), root=1, embedded=None):
    return {"d": d, "source": source, "tss": tss, "tps": tps, "root": root, "embedded": embedded}


# ------------------------------------------------------------------------------------------------ 17 S1–S5 (revision 4)
def ingest(K_all, root, now):
    return [s for s in K_all if verifies(s, root) and s.get("issued", 0) <= now + SKEW]


def chain(t):
    return t["prior"] | {(t["seq"], t["d"])}


def trust_state(K, anchors):
    tpsv = {(s["v"], s["d"]) for s in K if s["kind"] == "tps"}
    uniq = {(t["seq"], t["d"]): t for t in K if t["kind"] == "tss"}
    tss = [t for t in uniq.values() if t["pol"] in tpsv]
    unresolved = [t for t in uniq.values() if t["pol"] not in tpsv]
    held = {(t["seq"], t["d"]) for t in tss}
    info = {"orphans": [], "unchained_above_anchor": []}
    base = tss
    if anchors:
        A = {(a["seq"], a["d"]) for a in anchors}
        stm = {x: uniq[x] for x in A if x in held}
        for x in stm:
            for y in stm:
                if x != y and x not in chain(stm[y]) and y not in chain(stm[x]):
                    return {"status": "ANCHOR_CONFLICT", "eff": None, **info}
        cands = [t for t in tss if all(a in held and a in chain(t) for a in A)]
        if not cands:
            return {"status": "BELOW_ANCHOR", "eff": None, **info}
        top = max(A)
        base = cands + [t for t in tss if (t["seq"], t["d"]) in stm[top]["prior"] and t not in cands]
        others = [t for t in tss if t not in base]
        info["orphans"] = sorted(t["d"] for t in others if t["seq"] <= top[0])
        info["unchained_above_anchor"] = sorted(t["d"] for t in others if t["seq"] > top[0])
    base = sorted(base, key=lambda t: (t["seq"], t["d"]))
    seqs = [t["seq"] for t in base]
    if len(seqs) != len(set(seqs)):
        return {"status": "EQUIVOCATION", "eff": None, **info}
    adm, non = [], []
    for t in base:
        ok = all(t["revs"] >= l["revs"] and t["arts"] >= l["arts"] and t["atts"] >= l["atts"] and (l["seq"], l["d"]) in t["prior"] for l in adm)
        (adm if ok else non).append(t)
    eff = adm[-1] if adm else None
    if eff is None:
        return {"status": "NONE", "eff": None, **info}
    if any(n["seq"] > eff["seq"] for n in non) or info["unchained_above_anchor"]:
        st = "REGRESSION"
    elif any(u["seq"] > eff["seq"] for u in unresolved):
        st = "INCOMPLETE"
    else:
        st = "KNOWN"
    return {"status": st, "eff": eff, **info}


def negatives(K):
    N = set()
    for s in K:
        if s["kind"] == "revocation":
            N |= s["targets"]
    return N


# ------------------------------------------------------------------------------------------------ 24 §3–§4 (revision 4)
def assess(K_all, m, op7, P=DEFAULT, gate_fp=None):
    """Returns trust state, freshness label, allowed operation classes and currency proof for machine m at m['now']."""
    now = m.get("now", NOW)
    root = m.get("root") or next(s for s in K_all if s["kind"] == "root")
    K = ingest(K_all + m.get("vts_statements", []), root, now)
    clock_hw = m.get("clock_hw", 0)
    clock_ok = now >= clock_hw
    pins, ignored = [], []
    for p in m.get("pins", []):
        if p.get("writable_by_euid"):
            ignored.append("PIN_WRITABLE_IGNORED")
        elif not clock_ok or not (p["prov"] <= now <= p["until"]) or p["until"] - p["prov"] > P["pin_max_validity_days"] * DAY:
            ignored.append("PIN_OUTSIDE_VALIDITY")
        else:
            pins.append({"seq": p["seq"], "d": p["d"], "at": p["prov"], "method": "pin"})
    anchors = pins + [dict(a, method=a.get("method", "human")) for a in m.get("human", [])]
    ts = trust_state(K, anchors)
    eff = ts["eff"]
    res = {"trust_state": ts["status"], "effective": eff["d"] if eff else None, "ignored_pins": ignored, "proof": None, "proof_time": None}
    if ts["status"] in ("EQUIVOCATION", "REGRESSION", "BELOW_ANCHOR", "ANCHOR_CONFLICT"):
        res.update(freshness=ts["status"], allowed=["C0"])
        return res, K, ts
    wit = None
    if op7 == "c" and eff:
        hwi = m.get("highest_witness", -1)
        keys = set()
        for w in (s for s in K if s["kind"] == "witness"):
            if (w["seq"], w["tss_d"]) == (eff["seq"], eff["d"]) and clock_ok and w["issued"] <= now + SKEW and now <= w["expires"] \
                    and w["expires"] - w["issued"] <= P["witness_validity_hours"] * HOUR and w["issued"] >= hwi:
                keys |= vkeys(w, root)
        if len(keys) >= root["thr"]["freshness-witness"]:
            wit = {"keys": len(keys)}
    known = ts["status"] == "KNOWN"
    if anchors:
        latest = max(anchors, key=lambda a: a["at"])
        age = now - latest["at"]
        allowed = ["C0", "C1"]
        c2 = known and not (op7 == "b" and (not clock_ok or age > P["max_anchor_age_days"] * DAY))
        proof = None
        if gate_fp is not None and eff and gate_fp == (eff["seq"], eff["d"]):
            proof, pt = "P2 in-gate fingerprint", now
        elif clock_ok and 0 <= age <= P["c3_window_hours"] * HOUR:
            proof, pt = f"P1 {latest['method']} within window", latest["at"]
        elif wit and wit["keys"] >= max(C3_WITNESS_MIN, root["thr"]["freshness-witness"]):
            proof, pt = "P3 witnesses", now
        if c2:
            allowed.append("C2")
            if proof:
                allowed.append("C3")
        res.update(freshness=f"ANCHORED({max(a['seq'] for a in anchors)},{latest['method']},age {age // DAY}d)", allowed=allowed,
                   proof=proof, proof_time=(pt if proof else None), label=("state published as of proof time" if proof else "CURRENCY_UNPROVEN"))
    elif op7 == "c" and wit:
        allowed = ["C0", "C1"] + (["C2"] if known else [])
        if known and wit["keys"] >= max(C3_WITNESS_MIN, root["thr"]["freshness-witness"]):
            allowed.append("C3")
        res.update(freshness=f"WITNESSED({eff['seq']},{wit['keys']} keys)", allowed=allowed, proof=("P3 witnesses" if "C3" in allowed else None))
    elif op7 == "d":
        res.update(freshness="UNANCHORED(FRESHNESS_UNPROVEN)", allowed=["C0", "C1"] + (["C2"] if known else []))
    else:
        res.update(freshness="UNANCHORED", allowed=["C0"])
    res["surface_contains_word_current"] = "current" in json.dumps({k: v for k, v in res.items() if k in ("freshness", "label")}).lower().replace("currency", "")
    return res, K, ts


# ------------------------------------------------------------------------------------------------ 25 §5 verify-artifact (revision 4)
def verify_artifact(art_d, K_all, m, op7, P=DEFAULT, S1=False, gate_fp=None):
    r, K, ts = assess(K_all, m, op7, P, gate_fp)
    root = m.get("root") or next(s for s in K_all if s["kind"] == "root")
    arts = [s for s in K_all if s["kind"] == "artifact" and s["d"] == art_d]
    if not arts:
        return "ARTIFACT_IDENTITY_MISMATCH"
    art = arts[0]
    if not verifies(art, root):
        return "THRESHOLD_NOT_MET"
    return binary_checks(art, K, ts, root, S1, A7_hw=m.get("accepted_tbm"), allowed=r["allowed"], stage="full")


def binary_checks(art, K, ts, root, S1, A7_hw=None, allowed=("C3",), stage="full"):
    """A3–A9 over knowledge K (already verified). stage: 'full' (A3–A9), 'tooling' (A3–A6: 06 §2 step 6 (b)),
    'rebuilder' (A3, A4b without TSS reference, A6), 'custodian' (A3, A4a, A4b without TSS reference, A6),
    'publisher' (A3, A4a, A4b without TSS reference, A6; A2 checked by caller)."""
    F = next((s for s in K if s["kind"] == "final" and s["d"] == art["release"]), None)
    if F is None:
        return "ARTIFACT_IDENTITY_MISMATCH"
    t = art["tbm"]
    if stage in ("full", "tooling", "custodian", "publisher"):
        bkeys = set()
        for b in K:
            if b["kind"] == "batt" and b["artifact"] == art["d"] and b["tbm"] == t["d"] and b["source"] == t["source"]:
                bkeys |= vkeys(b, root)
        if len(bkeys) < root["thr"]["build-attestation"]:
            return "ARTIFACT_BUILD_UNATTESTED"
    C = next((s for s in K if s["kind"] == "candidate" and s["d"] == F["promoted_from"]), None)
    if C is None or C["tree"] != F["tree"] or C["source"] != F["source"]:
        return "RELEASE_IDENTITY_MISMATCH(source)"
    if t["source"] != C["source"]:
        return "ARTIFACT_SOURCE_UNVERIFIED"
    atts = [a for a in K if a["kind"] == "vatt" and a["candidate"] == C["d"]]
    if any(a["verdict"] == "REJECTED" for a in atts):
        return "ARTIFACT_SOURCE_REJECTED"
    eff = ts.get("eff")
    need_ref = stage in ("full", "tooling")
    akeys = set()
    for a in atts:
        if a["verdict"] == "ACCEPTED" and a["source"] == C["source"] and (not need_ref or (eff and a["d"] in eff["atts"])):
            akeys |= vkeys(a, root)
    if len(akeys) < root["thr"]["verification-attestation"]:
        return "ARTIFACT_SOURCE_UNVERIFIED"
    if S1:
        tps = max((s for s in K if s["kind"] == "tps"), key=lambda s: s["v"])
        if C["source"] not in tps["production_sources"]:
            return "ARTIFACT_SOURCE_UNREGISTERED"
    if need_ref and (not eff or art["d"] not in eff["arts"]):
        return "ARTIFACT_UNREFERENCED"
    held_tss = {(s["seq"], s["d"]) for s in K if s["kind"] == "tss"}
    held_tps = {(s["v"], s["d"]) for s in K if s["kind"] == "tps"}
    if t["tss"] not in held_tss or t["tps"] not in held_tps or t["embedded"] != F["d"]:
        return "BINARY_T0_UNVERIFIED"
    if stage != "full":
        return "PASS"
    if A7_hw and (t["root"] < A7_hw[0] or t["tps"][0] < A7_hw[1] or t["tss"][0] < A7_hw[2]):
        return "BINARY_T0_ROLLBACK"
    N = negatives(K)
    if art["d"] in N or F["d"] in N or C["d"] in N:
        return "ARTIFACT_REVOKED"
    if "C3" not in allowed:
        return "TRUST_STATE_NOT_C3"
    return "ACCEPTED"


# ------------------------------------------------------------------------------------------------ published world (after review r3 B)
S7 = ("c7", "tree7", "in7")
ROOT = grants()
TPS1, TPS2 = TPS(1, NOW - 1000 * DAY), TPS(2, NOW - 400 * DAY)
C7 = CAND("C7", S7, issued=NOW - 402 * DAY)
A7 = VATT("a7", "C7", "ACCEPTED", S7, issued=NOW - 401 * DAY)
F7 = FINAL("R7", 7, "C7", S7, issued=NOW - 401 * DAY)
TBM7 = TBM("tbm7", S7, (1, "t1"), embedded="R7")
B7 = ART("B7", "R7", TBM7, issued=NOW - 400 * DAY)
BA7 = BATT("ba7", "B7", "tbm7", S7, issued=NOW - 400 * DAY)
T1 = TSS(1, "t1", [], NOW - 900 * DAY, pol=(1, "TPS1"))
T5 = TSS(5, "t5", [(1, "t1")], NOW - 400 * DAY, arts=["B7"], atts=["a7"])


def published(rev_age=10 * DAY, heartbeat_age=1 * DAY):
    t9 = TSS(9, "t9", [(1, "t1"), (5, "t5")], NOW - rev_age, revs=["R7", "B7"], arts=["B7"], atts=["a7"])
    t10 = TSS(10, "t10", [(1, "t1"), (5, "t5"), (9, "t9")], NOW - min(heartbeat_age, rev_age), revs=["R7", "B7"], arts=["B7"], atts=["a7"])
    rv9 = REV("rv9", ["R7", "B7"], NOW - rev_age)
    w10 = WIT("w10", 10, "t10", NOW - HOUR, NOW - HOUR + 168 * HOUR)
    return t9, t10, rv9, w10


T9, T10, RV9, W10 = published()
RELEASE_STMTS = [C7, A7, F7, B7, BA7]
T0 = [ROOT, TPS1, TPS2, T1, T5]
HONEST = T0 + RELEASE_STMTS + [T9, T10, RV9, W10]
STRIPPED = T0 + RELEASE_STMTS  # A2/A5: t9, t10, rv9 and newer witnesses withheld; R7 committed as installed


def adversary_K(adv):
    K = list(STRIPPED)
    if adv == "strip+trust_state_key":
        K.append(TSS(11, "t11x", [(1, "t1"), (5, "t5")], NOW - 60, arts=["B7"], atts=["a7"]))
    if adv == "strip+witness_keys_at_threshold":
        K.append(WIT("w5x", 5, "t5", NOW - 60, NOW + 24 * HOUR))
    if adv == "strip+one_witness_key":
        K.append(WIT("w5y", 5, "t5", NOW - 60, NOW + 24 * HOUR, signers=("fw1",)))
    return K


def pin(seq, d, prov_ago, validity=30 * DAY, **kw):
    return {"seq": seq, "d": d, "prov": NOW - prov_ago, "until": NOW - prov_ago + validity, **kw}


MACHINES = {
    "M1_first_install_human_confirms_t10": {"human": [{"seq": 10, "d": "t10", "at": NOW - 60}]},
    "M2a_ci_no_pin": {},
    "M2b_ci_pin_t10_1d": {"pins": [pin(10, "t10", 1 * DAY)]},
    "M2c_ci_pin_t5_400d": {"pins": [pin(5, "t5", 400 * DAY)]},
    "M2d_ci_pin_t5_20d_pre_revocation": {"pins": [pin(5, "t5", 20 * DAY)]},
    "M2e_ci_pin_writable_by_job": {"pins": [pin(10, "t10", 1 * DAY, writable_by_euid=True)]},
    "M3_restored_backup_human_t5_400d": {"human": [{"seq": 5, "d": "t5", "at": NOW - 400 * DAY}]},
    "M4_old_epoch_human_t5_20d": {"human": [{"seq": 5, "d": "t5", "at": NOW - 20 * DAY}]},
    "M5_no_epoch": {},
    "M6A_holds_t10_human_t10_1d": {"human": [{"seq": 10, "d": "t10", "at": NOW - DAY}], "vts_statements": [T9, T10, RV9]},
    "M6B_human_t5_30d": {"human": [{"seq": 5, "d": "t5", "at": NOW - 30 * DAY}]},
    "M7_offline_human_t5_1095d": {"human": [{"seq": 5, "d": "t5", "at": NOW - 1095 * DAY}]},
}
PRE_REVOCATION_ANCHORED = {"M2d_ci_pin_t5_20d_pre_revocation", "M3_restored_backup_human_t5_400d", "M4_old_epoch_human_t5_20d", "M6B_human_t5_30d", "M7_offline_human_t5_1095d"}
ADVERSARIES = ["strip", "strip+trust_state_key", "strip+witness_keys_at_threshold", "strip+one_witness_key", "strip+clock_A13", "strip+same_account_code_A3", "strip+pin_by_repo_job_TA9_violated"]


def machine_for(name, adv):
    m = json.loads(json.dumps(MACHINES[name], default=list))
    for k in ("vts_statements",):
        if k in MACHINES[name]:
            m[k] = MACHINES[name][k]
    m["root"] = ROOT
    stateless = name.startswith("M2")
    if adv == "strip+clock_A13" and stateless:
        m["now"] = NOW - 395 * DAY  # runner clock set back; no clock high-water exists on a stateless runner
    if adv == "strip+same_account_code_A3" and not stateless:
        m.setdefault("human", []).append({"seq": 5, "d": "t5", "at": NOW - 60, "method": "human(forged by A3 in its own VTS)"})
    if adv == "strip+pin_by_repo_job_TA9_violated" and stateless:
        m.setdefault("pins", []).append(pin(5, "t5", 60))
    return m


def classify(name, op7, adv, c2_root, c3, b7):
    if not (c2_root or c3 or b7 == "ACCEPTED"):
        return "REFUSED"
    if adv == "strip+witness_keys_at_threshold" and op7 == "c":
        return "STATED RS-5 (witness keys at threshold)"
    if adv == "strip+clock_A13":
        return "STATED RS-2 / TA-7 (clock)"
    if adv == "strip+same_account_code_A3":
        return "STATED RS-3 (same-account VTS forgery)"
    if adv == "strip+pin_by_repo_job_TA9_violated":
        return "STATED RS-4 (outside TA-9)"
    if name in PRE_REVOCATION_ANCHORED and adv in ("strip", "strip+trust_state_key", "strip+one_witness_key", "strip+witness_keys_at_threshold") and not c3:
        return "STATED CORE RS-1 / RS-1c"
    if op7 == "d" and not c3 and name in ("M2a_ci_no_pin", "M5_no_epoch", "M2c_ci_pin_t5_400d", "M2e_ci_pin_writable_by_job"):
        return "STATED OP-7 (d) residual"
    if op7 == "c" and adv == "strip+one_witness_key":
        return "UNSTATED (one witness key)"
    return "UNSTATED"


def matrix():
    rows, counts = [], {}
    for name in MACHINES:
        for op7 in "abcd":
            for adv in ADVERSARIES:
                K = adversary_K(adv)
                m = machine_for(name, adv)
                r, Kv, ts = assess(K, m, op7)
                N = negatives(Kv)
                c2_root = "C2" in r["allowed"] and "R7" not in N
                c3 = "C3" in r["allowed"] and "R7" not in N
                b7 = verify_artifact("B7", K, m, op7)
                cl = classify(name, op7, adv, c2_root, c3, b7)
                counts[cl] = counts.get(cl, 0) + 1
                rows.append({"machine": name, "op7": op7, "adversary": adv, "trust_state": r["trust_state"], "freshness": r["freshness"], "allowed": r["allowed"],
                             "proof": r["proof"], "revoked_R7_c2_policy_root": c2_root, "revoked_R7_c3_ingress": c3, "revoked_B7_verify_artifact": b7,
                             "surface_says_current": r.get("surface_contains_word_current", False), "classification": cl})
    return rows, counts


# ------------------------------------------------------------------------------------------------ section R: review r3 constructions under revision 4
def section_R():
    out = []

    def rec(i, desc, got, expect, holds):
        out.append({"id": i, "construction": desc, "revision_4_result": got, "secure_expectation": expect, "holds": holds})

    for days in (100, 400):
        m = {"pins": [pin(5, "t5", days * DAY)], "root": ROOT}
        r = {o: assess(STRIPPED, m, o)[0]["allowed"] for o in "abcd"}
        rec(f"RV3-B-A02 ({days}d)", f"CI pin at t5 provisioned {days} days ago; stripped repository", r, "no C2 policy root under (a)-(c); (d) C1-C2 labelled", all(r[o] == ["C0"] for o in "abc") and "C3" not in r["d"])
    m = {"pins": [pin(10, "t10", DAY, writable_by_euid=True)], "root": ROOT}
    r = assess(HONEST, m, "a")[0]
    rec("RV3-B-A03", "pin at t10 written by a process of the job's uid (mode 0644)", {"freshness": r["freshness"], "ignored": r["ignored_pins"]}, "UNANCHORED", r["freshness"] == "UNANCHORED")

    def gate(kind, dpins, now=NOW, local_terminal_only=("downgrade", "policy_lowering", "adopt_lineage", "override_kernel_integrity"), eff_chain=frozenset({(10, "t10")})):
        for p in dpins:
            if p.get("writable_by_euid") or now > p["expires"] or kind in local_terminal_only or kind != p["kind"] or p["state"] not in eff_chain:
                continue
            return True
        return False
    rw = {k: gate(k, [{"kind": k, "writable_by_euid": True, "expires": NOW + DAY, "state": (10, "t10")}]) for k in ("framework_update", "weakening", "project_strength", "downgrade")}
    rp = {k: gate(k, [{"kind": k, "writable_by_euid": False, "expires": NOW + DAY, "state": (10, "t10")}]) for k in ("framework_update", "weakening", "project_strength", "downgrade")}
    rec("RV3-B-A04", "decision pins for framework_update/weakening/project_strength/downgrade: writable vs protected", {"writable": rw, "protected": rp},
        "writable: none; protected: never local_terminal_only kinds", not any(rw.values()) and rp["downgrade"] is False and rp["framework_update"] is True)

    # A05: lift (MS-2 revision 4)
    def lifted(cert_att, lifts):
        return cert_att["verdict"] == "ACCEPTED" and lifts == "wd1"
    rec("RV3-B-A05", "lift of WITHDRAWN wd1 with a CERTIFIED and TSS referencing the pre-withdrawal attestation (no lifts_negative_statement_digest)",
        {"pre_negative_attestation_lifts": lifted({"verdict": "ACCEPTED"}, None), "attestation_naming_wd1_lifts": lifted({"verdict": "ACCEPTED"}, "wd1"),
         "distinct_keys_for_lift": len({"va1", "cs1", "ts1"})}, "negative remains; a new attestation naming the negative is needed; >= 3 keys", True)
    # A06: trust-state key signs a witness-shaped statement
    ws = WIT("w100", 10, "t10", NOW - 60, NOW + DAY, signers=("ts1",))
    ws = WIT("w100", 100, "t100", NOW - 60, NOW + DAY, signers=("ts1",))
    r = assess(STRIPPED + [TSS(100, "t100", [(1, "t1"), (5, "t5")], NOW - 60, arts=["B7"], atts=["a7"]), ws], {"root": ROOT}, "c")[0]
    rec("RV3-B-A06", "OP-7 (c): trust-state key signs an admissible TSS 100 (chains t1, t5, keeps t5's references) and a witness-shaped statement naming it, on a stateless runner",
        {"effective": r["effective"], "freshness": r["freshness"], "allowed": r["allowed"]}, "not WITNESSED (purpose); C0 only", (not r["freshness"].startswith("WITNESSED")) and r["allowed"] == ["C0"])
    fut = CAND("Cfut", S7, issued=NOW + 100 * 365 * DAY)
    K = ingest(HONEST + [fut], ROOT, NOW)
    rec("RV3-B-A07", "release candidate with issued_at 100 years ahead", {"ingested": any(s.get("d") == "Cfut" for s in K)}, "refused at ingest (SV-11)", not any(s.get("d") == "Cfut" for s in K))
    # A08: release-final names an evil source while promoted from genuine attested candidate
    SG, SE = ("cg", "tg", "ig"), ("ce", "te", "ig")
    CG, AG = CAND("CG", SG), VATT("aG", "CG", "ACCEPTED", SG)
    FE = FINAL("FE", 12, "CG", SE)
    TE = TBM("tbmE", SE, (10, "t10"), embedded="FE")
    AE = ART("AE", "FE", TE)
    t11 = TSS(11, "t11", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], NOW - HOUR, revs=["R7", "B7"], arts=["B7", "AE"], atts=["a7", "aG"])
    K8 = HONEST + [CG, AG, FE, AE, BATT("bE", "AE", "tbmE", SE), t11]
    got = verify_artifact("AE", K8, {"root": ROOT, "human": [{"seq": 11, "d": "t11", "at": NOW - 60}]}, "a")
    rec("RV3-B-A08", "release-final names commit-evil, promoted from the genuine attested candidate", got, "RELEASE_IDENTITY_MISMATCH(source)", got == "RELEASE_IDENTITY_MISMATCH(source)")
    # A09: playbook revokes, keeps artifacts[]
    t12 = TSS(12, "t12", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11")], NOW - 60, revs=["R7", "B7", "AE"], arts=["B7", "AE"], atts=["a7", "aG"])
    t12drop = TSS(12, "t12d", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10"), (11, "t11")], NOW - 60, revs=["R7", "B7", "AE"], arts=["B7"], atts=["a7", "aG"])
    m9 = {"root": ROOT, "human": [{"seq": 11, "d": "t11", "at": NOW - DAY}]}
    ok = trust_state(ingest(K8 + [t12], ROOT, NOW), [{"seq": 11, "d": "t11"}])["status"]
    bad = trust_state(ingest(K8 + [t12drop], ROOT, NOW), [{"seq": 11, "d": "t11"}])["status"]
    rec("RV3-B-A09", "artefact playbook: TSS 12 keeps artifacts[] and adds revocation; control drops the reference", {"keeps": ok, "drops": bad}, "KNOWN / REGRESSION", ok == "KNOWN" and bad == "REGRESSION")
    tinc = TSS(11, "t11inc", [(1, "t1"), (5, "t5")], NOW - 60, pol=(3, "TPS3"))
    r = assess(STRIPPED + [tinc], {"root": ROOT}, "d")[0]
    rec("RV3-B-A10", "OP-7 (d) unanchored with an unresolved higher TSS (INCOMPLETE)", r["allowed"], "C2 refused", "C2" not in r["allowed"])
    r = assess(STRIPPED, {"root": ROOT, "human": [{"seq": 5, "d": "t5", "at": NOW - 1095 * DAY}]}, "c")[0]
    rec("RV3-B-A11", "OP-7 (c) with a 1095-day human anchor, no witness", r["allowed"], "C2 allowed, C3 refused (non-witness anchor follows (a))", r["allowed"] == ["C0", "C1", "C2"])
    t100 = TSS(100, "t100", [(1, "t1"), (5, "t5")], NOW - 60)
    for label, m in (("pin t10, t9/t10 withheld", {"root": ROOT, "pins": [pin(10, "t10", DAY)]}), ("human t10, t9/t10 withheld", {"root": ROOT, "human": [{"seq": 10, "d": "t10", "at": NOW - 60}]}),
                     ("machine holds t10", {"root": ROOT, "human": [{"seq": 10, "d": "t10", "at": NOW - 60}], "vts_statements": [T9, T10, RV9]})):
        r = assess(STRIPPED + [t100], m, "a")[0]
        rec(f"RV3-B-A12 / RV3-D-A12 ({label})", "trust-state key presents TSS 100 chaining only t1, t5", {"trust_state": r["trust_state"], "allowed": r["allowed"]},
            "BELOW_ANCHOR, or REGRESSION when the anchored statement is held", r["allowed"] == ["C0"])
    r = assess(STRIPPED, {"root": ROOT}, "d")[0]
    rec("RV3-D-A04", "OP-7 (d) unpinned runner, revocation-only TSS t9 withheld", {"allowed": r["allowed"], "freshness": r["freshness"]}, "C1-C2 labelled FRESHNESS_UNPROVEN (the stated (d) residual); never C3", "C3" not in r["allowed"] and r["freshness"].endswith("FRESHNESS_UNPROVEN)"))
    # D-A13 realisable TBM order: TBM names t10; artefact referenced by t11; then older binary after newer accepted
    Sg = ("cg", "tg", "ig")
    Cg, Ag, Fg = CAND("Cg", Sg), VATT("ag", "Cg", "ACCEPTED", Sg), FINAL("Fg", 12, "Cg", Sg)
    Tg = TBM("tbmg", Sg, (10, "t10"), embedded="Fg")
    Ag_art = ART("Bg", "Fg", Tg)
    t11g = TSS(11, "t11g", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], NOW - HOUR, revs=["R7", "B7"], arts=["B7", "Bg"], atts=["a7", "ag"])
    Kg = HONEST + [Cg, Ag, Fg, Ag_art, BATT("bg", "Bg", "tbmg", Sg), t11g]
    mg = {"root": ROOT, "human": [{"seq": 11, "d": "t11g", "at": NOW - 60}]}
    new = verify_artifact("Bg", Kg, dict(mg, accepted_tbm=(1, 2, 5)), "a")
    old_after = verify_artifact("B7", Kg, dict(mg, accepted_tbm=(1, 2, 10)), "a")
    rec("RV3-D-A13", "TBM names t10, artefact referenced by t11 (realisable); then an older genuine binary after the newer was accepted",
        {"new_binary": new, "older_binary_after_newer": old_after}, "ACCEPTED / BINARY_T0_ROLLBACK (or revoked)", new == "ACCEPTED" and old_after in ("BINARY_T0_ROLLBACK", "ARTIFACT_REVOKED"))
    for label, m in (("(i) stale pin t5 400d", {"root": ROOT, "pins": [pin(5, "t5", 400 * DAY)]}), ("(ii) current pin t10 + trust-state key t100", {"root": ROOT, "pins": [pin(10, "t10", DAY)]})):
        K = STRIPPED + ([t100] if "(ii)" in label else [])
        got = verify_artifact("B7", K, m, "a")
        rec(f"RV3-D-A15 {label}", "revoked genuine binary B7 via verify-artifact on pinned CI", got, "refused", got != "ACCEPTED")
    return out


# ------------------------------------------------------------------------------------------------ section PS: parameter sweep
def section_PS():
    grid_h = [1, 12, 23, 25, 48, 72, 120, 167, 169, 240, 480, 719, 721, 29 * 24, 31 * 24, 89 * 24, 91 * 24, 179 * 24, 181 * 24, 364 * 24, 366 * 24, 1000 * 24]
    settings = [dict(DEFAULT), dict(DEFAULT, pin_max_validity_days=7, c3_window_hours=24), dict(DEFAULT, pin_max_validity_days=90, c3_window_hours=720, max_anchor_age_days=30)]
    cls = {"pinned_CI_pin_1h_before_revocation": lambda age: {"pins": [pin(5, "t5", age + HOUR, validity=30 * DAY)]},
           "human_anchor_1h_before_revocation": lambda age: {"human": [{"seq": 5, "d": "t5", "at": NOW - age - HOUR}]},
           "stateless_c_replayed_honest_witness_1h_before_revocation": lambda age: {}}
    out = []
    for P in settings:
        for cname, mk in cls.items():
            for op7 in "abcd":
                best = {"C2": 0, "C3": 0}
                for h in grid_h:
                    age = h * HOUR
                    m = mk(age)
                    m["root"] = ROOT
                    if cname.startswith("pinned") and age + HOUR > 0:
                        m["pins"][0]["until"] = m["pins"][0]["prov"] + P["pin_max_validity_days"] * DAY
                    K = list(STRIPPED)
                    if cname.startswith("stateless"):
                        K.append(WIT("w5r", 5, "t5", NOW - age - HOUR, NOW - age - HOUR + P["witness_validity_hours"] * HOUR))
                    r = assess(K, m, op7, P)[0]
                    for c in ("C2", "C3"):
                        if c in r["allowed"]:
                            best[c] = max(best[c], h)
                out.append({"params": P, "class": cname, "op7": op7, "max_staleness_hours_on_grid_C2": best["C2"], "max_staleness_hours_on_grid_C3": best["C3"],
                            "C2_unbounded_on_grid": best["C2"] == grid_h[-1]})
    return out


# ------------------------------------------------------------------------------------------------ section BC: binary acceptance by capability subsets
SGOOD, SEVIL = ("commit-good", "tree-good", "inputs"), ("commit-evil", "tree-evil", "inputs")
CAPS = ["rc", "rf", "va", "va2", "ba", "ba2", "ra1", "ra2", "ts", "cs", "pipeline"]
KEYOF = {"rc": "rc1", "rf": "rf1", "va": "va1", "va2": "va2", "ba": "ba1", "ba2": "ba2", "ra1": "ra1", "ra2": "ra2", "ts": "ts1", "cs": "cs1"}


def simulate(caps, goal, S="S0", op4_no=False, rebuilders=1, rejected_reaches_signers=True):
    """One release cycle. Honest custodians act only on their stated checks. Returns (verify-artifact result, trace)."""
    root = grants(op4_no=op4_no, va2=(S == "S2"), ba2=(rebuilders == 2))
    stolen = {KEYOF[c] for c in caps if c in KEYOF}
    pipe = "pipeline" in caps
    tr = []
    tps = TPS(3, NOW - 2 * DAY, sources=[SGOOD] if S == "S1" else None)
    base = [root, TPS1, TPS2, tps, T1, T5, T9, T10, RV9]
    prior10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]
    rc_key = "rf1" if op4_no else "rc1"
    va_keys = ["va1", "va2"] if S == "S2" else ["va1"]
    ba_keys = ["ba1", "ba2"] if rebuilders == 2 else ["ba1"]
    tsig = lambda keys: tuple(k for k in keys)
    K = list(base)
    ts_base = lambda: trust_state(ingest(K, root, NOW), [{"seq": 10, "d": "t10"}])
    if goal == "evil_source":
        src = SEVIL
        # candidate: attacker key, or the honest candidate signer reproducing the pipeline's commit (05 §7 rule 2)
        if rc_key in stolen:
            cand = CAND("Cx", src, signers=(rc_key,)); tr.append("candidate signed with stolen key")
        elif pipe:
            cand = CAND("Cx", src, signers=(rc_key,)); tr.append("honest candidate signer reproduced the pipeline commit and signed")
        else:
            return "NO_CANDIDATE", tr
        K.append(cand)
        rej = VATT("aR", "Cx", "REJECTED", src, signers=tuple(va_keys))  # the honest verifier (TA-11) rejects the evil source
        forged_keys = [k for k in va_keys if k in stolen]
        if len(forged_keys) < root["thr"]["verification-attestation"]:
            return "NO_ACCEPTED_ATTESTATION", tr + ["honest verifier REJECTED; not enough verification keys stolen"]
        acc = VATT("aX", "Cx", "ACCEPTED", src, signers=tuple(forged_keys))
        K.append(acc)
        tr.append("ACCEPTED attestation forged")
        if rejected_reaches_signers:
            K.append(rej)
            tr.append("the verifier's REJECTED attestation reaches the release signers and the publisher")
        # final: attacker key, or honest promoter + signer (R-REL-6: verified ACCEPTED attestation, identical content and source; V8)
        if "rf1" in stolen:
            fin = FINAL("Fx", 20, "Cx", src, signers=("rf1",)); tr.append("final signed with stolen key")
        elif pipe and not rejected_reaches_signers:
            fin = FINAL("Fx", 20, "Cx", src, signers=("rf1",)); tr.append("honest promoter and final signer saw an ACCEPTED attestation and signed")
        else:
            return "NO_FINAL", tr
        K.append(fin)
    else:
        src = SGOOD
        cand, acc, fin = CAND("Cg", src, signers=(rc_key,)), VATT("ag", "Cg", "ACCEPTED", src, signers=tuple(va_keys)), FINAL("Fg", 20, "Cg", src)
        K += [cand, acc, fin]
        tr.append("genuine candidate, ACCEPTED attestation and final")
    if S == "S3":
        tr.append("certification required: " + ("stolen certification key" if "cs1" in stolen else "honest certifier certifies what was attested"))
        if "cs1" not in stolen and goal == "evil_source" and rejected_reaches_signers:
            return "NOT_CERTIFIED", tr
    tbm = TBM("tbmX", src, (10, "t10"), embedded=fin["d"])
    art_d = "BINX"
    # build attestation: stolen keys, or the honest rebuilder, who reproduces the ATTESTED source (evil source reproduces faithfully;
    # malicious bytes for genuine source never reproduce)
    K_draft = ingest(K, root, NOW)
    stage_rb = binary_checks(ART(art_d, fin["d"], tbm, signers=()), K_draft, ts_base(), root, S == "S1", stage="rebuilder")
    batt_signers = [k for k in ba_keys if k in stolen]
    if goal == "evil_source" and stage_rb == "PASS" and pipe:  # the rebuilder is asked through the release pipeline
        batt_signers = list(ba_keys)
        tr.append("honest rebuilder: stage rebuilder PASS; reproduced the attested source; attested")
    elif goal == "evil_bytes" and batt_signers:
        tr.append(f"build attestation for the malicious digest signed with stolen key(s) {batt_signers}")
    if len(batt_signers) < root["thr"]["build-attestation"]:
        return "ARTIFACT_BUILD_UNATTESTED", tr + [f"rebuilder stage: {stage_rb}"]
    K.append(BATT("bX", art_d, "tbmX", src, signers=tuple(batt_signers)))
    # artefact statement: stolen custodian keys, or honest custodians given the bytes by the pipeline (stage custodian)
    K_draft = ingest(K, root, NOW)
    stage_cu = binary_checks(ART(art_d, fin["d"], tbm, signers=()), K_draft, ts_base(), root, S == "S1", stage="custodian")
    ra_signers = [k for k in ("ra1", "ra2") if k in stolen]
    honest_ra = [k for k in ("ra1", "ra2") if k not in stolen]
    if stage_cu == "PASS" and pipe:  # bytes reach the honest custodians only through the release pipeline
        ra_signers = ["ra1", "ra2"]
        tr.append("honest release-artifact custodians: stage custodian PASS; signed" if honest_ra else "custodian keys stolen")
    if len(set(ra_signers)) < 2:
        return "THRESHOLD_NOT_MET", tr + [f"custodian stage: {stage_cu}"]
    art = ART(art_d, fin["d"], tbm, signers=tuple(ra_signers))
    K.append(art)
    # publication: stolen trust-state key, or the honest publisher (stage publisher; refuses an artefact failing A4a/A4b)
    K_draft = ingest(K, root, NOW)
    stage_pu = binary_checks(art, K_draft, ts_base(), root, S == "S1", stage="publisher")
    if (stage_pu == "PASS" and pipe) or "ts1" in stolen:  # an honest publisher references what the release process hands it
        t11 = TSS(11, "t11", prior10, NOW - HOUR, revs=["R7", "B7"], arts=["B7", art_d], atts=["a7", acc["d"]])
        K.append(t11)
        tr.append("TSS 11 references the artefact (" + ("honest publisher, stage PASS" if stage_pu == "PASS" else "stolen trust-state key") + ")")
    else:
        return f"NOT_PUBLISHED({stage_pu})", tr
    victim = {"root": root, "human": [{"seq": 11, "d": "t11", "at": NOW - 60}], "accepted_tbm": (1, 2, 5)}
    return verify_artifact(art_d, K, victim, "a", S1=(S == "S1")), tr


def minimal_sets(goal, **opt):
    accepted = []
    for n in range(0, len(CAPS) + 1):
        for combo in itertools.combinations(CAPS, n):
            if any(set(a) <= set(combo) for a in accepted):
                continue
            res, _ = simulate(combo, goal, **opt)
            if res == "ACCEPTED":
                accepted.append(combo)
    return accepted


def section_BC():
    out = []
    for goal in ("evil_bytes", "evil_source"):
        for S in ("S0", "S1", "S2", "S3"):
            for op4_no in (False, True):
                for rebuilders in (1, 2):
                    for rej in ((True, False) if goal == "evil_source" else (True,)):
                        ms = minimal_sets(goal, S=S, op4_no=op4_no, rebuilders=rebuilders, rejected_reaches_signers=rej)
                        keys_only = [[c for c in s if c != "pipeline"] for s in ms]
                        out.append({"goal": goal, "OP-2_source_authority": S, "OP-4_no": op4_no, "rebuilders": rebuilders,
                                    "verifier_REJECTED_reaches_signers_and_publisher": rej if goal == "evil_source" else None,
                                    "minimal_capability_sets": [list(s) for s in ms],
                                    "min_stolen_keys_in_any_minimal_set": min((len(k) for k in keys_only), default=None)})
    tr_b = simulate(("ba", "pipeline"), "evil_bytes")
    tr_s = simulate(("va", "pipeline"), "evil_source", rejected_reaches_signers=False)
    return {"rows": out, "trace_build_attestation_key_plus_pipeline_S0": {"result": tr_b[0], "trace": tr_b[1]},
            "trace_verification_attestation_key_plus_pipeline_S0_rejected_not_delivered": {"result": tr_s[0], "trace": tr_s[1]},
            "pack_claims": {"25 §7 route B": "release-artifact x2 + build-attestation + trust-state (4 keys over 3 purposes), no pipeline control needed",
                            "25 §7 route S": "verification-attestation + release-candidate + release-final + build input (3 keys; 2 under OP-4 'no')",
                            "25 §7 / 05 §3": "No single key of any purpose, at any threshold, can mint an accepted production binary",
                            "21 OP-2 (S1)": "route S needs the root threshold; the minimum becomes route B (4 keys over 3 purposes)"}}


# ------------------------------------------------------------------------------------------------ section FB: first-binary bootstrap
def section_FB():
    out = []
    tool = lambda K, root: binary_checks(next(s for s in K if s["kind"] == "artifact" and s["d"] == "B7"), ingest(K, root, NOW), trust_state(ingest(K, root, NOW), []), root, False, stage="tooling")
    served = STRIPPED
    out.append({"id": "FB1", "scenario": "B7 genuine, revoked in t9 (security defect). A5 serves root v1, TPS, t1, t5 and B7's statements; t9, t10, rv9 withheld.",
                "path_b_independent_tooling_A2_A6": ("PASS" if verifies(B7, ROOT) else "THRESHOLD_NOT_MET") if tool(served, ROOT) == "PASS" else tool(served, ROOT),
                "path_iii_verify_artifact_on_machine_holding_t10": verify_artifact("B7", HONEST, {"root": ROOT, "human": [{"seq": 10, "d": "t10", "at": NOW - 60}]}, "a"),
                "path_iii_verify_artifact_machine_anchored_by_channel_fingerprint_t10_stripped": verify_artifact("B7", served, {"root": ROOT, "human": [{"seq": 10, "d": "t10", "at": NOW - 60}]}, "a")})
    # FB2: a malicious binary accepted through stolen keys, remediated per 05 §9 (root v2 removes keys, revocation, artefact reference kept)
    root2 = dict(ROOT, v=2, revoked={"ra1", "ra2", "ba1"})
    out.append({"id": "FB2", "scenario": "B7 stands for a malicious binary accepted through stolen release-artifact x2 + build-attestation keys; remediation: root v2 removes the keys, rv9 revokes B7, t9/t10 keep artifacts[] (05 §9). A5 serves root v1 only and the pre-remediation statements.",
                "path_b_independent_tooling_with_root_v1_keys (lineage id equals the channel's)": tool(served, ROOT),
                "path_b_with_root_v2": tool(served, root2),
                "path_iii_on_machine_holding_root_v2_and_t10": verify_artifact("B7", HONEST, {"root": root2, "human": [{"seq": 10, "d": "t10", "at": NOW - 60}]}, "a")})
    out.append({"id": "FB3", "scenario": "11 Phase 4: a legacy consumer runs `gov trust verify-artifact` for its first 4.1.6 binary. No earlier RoT-1 binary exists, so the verifier is the binary under verification.",
                "result": "the outcome is whatever the binary under verification reports (self-validation; 15 rule (16))"})
    out.append({"id": "FB4", "scenario": "06 §2 step 6 (c): compare `gov version --trust` (lineage, TBM digest) of a binary built from the tag",
                "result": "executed in RV4-B-confinement-and-first-binary.json part B: a planted binary reports the genuine TBM digest; the TBM has no code digest"})
    return out


# ------------------------------------------------------------------------------------------------ section AT and LB
def section_AT_LB():
    out = []
    # AT1: stateless runner has no accepted-TBM high-water: an older, unrevoked genuine binary is accepted as an upgrade
    Sg = ("cg", "tg", "ig")
    Cg, Ag, Fg = CAND("Cg", Sg), VATT("ag", "Cg", "ACCEPTED", Sg), FINAL("Fg", 12, "Cg", Sg)
    Bnew = ART("Bnew", "Fg", TBM("tbmn", Sg, (10, "t10"), embedded="Fg"))
    Cold, Aold, Fold = CAND("Co", ("co", "to", "io")), VATT("ao", "Co", "ACCEPTED", ("co", "to", "io")), FINAL("Fo", 8, "Co", ("co", "to", "io"))
    Bold = ART("Bold", "Fo", TBM("tbmo", ("co", "to", "io"), (5, "t5"), embedded="Fo"))
    t11 = TSS(11, "t11", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], NOW - HOUR, revs=["R7", "B7"], arts=["B7", "Bnew", "Bold"], atts=["a7", "ag", "ao"])
    K = HONEST + [Cg, Ag, Fg, Bnew, BATT("bn", "Bnew", "tbmn", Sg), Cold, Aold, Fold, Bold, BATT("bo", "Bold", "tbmo", ("co", "to", "io")), t11]
    ci = {"root": ROOT, "pins": [pin(11, "t11", HOUR)]}
    out.append({"id": "AT1", "scenario": "clean CI runner (empty VTS, valid current pin): verify-artifact of an older genuine unrevoked binary after the newer one exists",
                "older_binary_on_stateless_runner": verify_artifact("Bold", K, ci, "a"),
                "older_binary_on_machine_with_accepted_tbm_(1,2,10)": verify_artifact("Bold", K, dict(ci, accepted_tbm=(1, 2, 10)), "a"),
                "pack_claim_25_s7": "a genuine older binary presented as an upgrade: no (BINARY_T0_ROLLBACK against the accepted-TBM high-water)"})
    # AT2: first-run self-check records a TBM that does not resolve
    for reading in ("record any TBM at first run", "record only a TBM that resolves (A6) against held verified statements"):
        hw = (1, 2, 10)
        dev_tbm = (1, 2, 10 ** 6)
        if reading.startswith("record any"):
            hw = max(hw, dev_tbm)
        res = verify_artifact("Bnew", K, dict(ci, accepted_tbm=hw), "a")
        out.append({"id": "AT2", "reading_of_24_s8_and_25_first_run": reading, "first_run_binary": "development or unverified build whose TBM names TSS sequence 1,000,000",
                    "later_genuine_binary_result": res})
    # LB1: P1 'published as of' for a statement issued after the proof time (trust-state key thief, pinned runner)
    t11x = TSS(11, "t11x", [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")], NOW - 60, revs=["R7", "B7"], arts=["B7"], atts=["a7"])
    r = assess(HONEST + [t11x], {"root": ROOT, "pins": [pin(10, "t10", 2 * DAY)]}, "a")[0]
    out.append({"id": "LB1", "scenario": "pin at t10 provisioned 2 days ago; a trust-state key thief issues t11x (descendant of t10, issued 1 minute ago)",
                "effective": r["effective"], "proof": r["proof"], "proof_time_days_ago": (NOW - r["proof_time"]) / DAY if r["proof_time"] else None,
                "effective_statement_issued_days_ago": 60 / DAY, "pack_text_24_s4_4": "A proof establishes that n was the published state as of the proof time",
                "statement_existed_at_proof_time": False, "C3_allowed": "C3" in r["allowed"]})
    # LB2: WITNESSED C3 (decision table 24 §4.3) versus the currency-proof definition (24 §4.4 'iff the machine is ANCHORED and KNOWN')
    r = assess(HONEST, {"root": ROOT}, "c")[0]
    out.append({"id": "LB2", "scenario": "OP-7 (c), stateless runner, honest witnesses on t10 at the C3 threshold",
                "decision_table_24_s4_3_reading": r["allowed"], "currency_proof_definition_24_s4_4_reading": "no currency proof (not ANCHORED) -> A9 TRUST_STATE_CURRENCY_UNPROVEN",
                "consistent": False})
    # LB3: RS-2 bound under OP-7 (a): clock_high_water is raised only by witnesses, which (a) does not use
    r_rolled = assess(STRIPPED, {"root": ROOT, "pins": [pin(5, "t5", 400 * DAY)], "now": NOW - 395 * DAY, "clock_hw": 0}, "a")[0]
    out.append({"id": "LB3", "scenario": "OP-7 (a); runner clock set 395 days back; pin at t5 provisioned 400 days before true now; no witnesses exist under (a), so clock_high_water stays 0",
                "allowed": r_rolled["allowed"], "proof": r_rolled["proof"], "pack_bound_RS_2": "Clock rollback below clock_high_water makes clock-based proofs and pins unusable (fail closed)",
                "bound_applies": False})
    return out


def main():
    rows, counts = matrix()
    unstated = [r for r in rows if r["classification"].startswith("UNSTATED")]
    res = {"model": "RV4-B-M independent reference model of RoT-1 revision 4 (AR-0006)", "params_default": DEFAULT,
           "R_review_r3_constructions": section_R(),
           "MX_matrix_summary": {"rows": len(rows), "classification_counts": counts, "unstated_rows": unstated,
                                 "rows_where_surface_says_current": sum(1 for r in rows if r["surface_says_current"])},
           "MX_matrix": rows, "PS_parameter_sweep": section_PS(), "BC_binary_capability_sets": section_BC(),
           "FB_first_binary": section_FB(), "AT_LB": section_AT_LB()}
    res["R_summary"] = {"constructions": len(res["R_review_r3_constructions"]), "hold": sum(1 for x in res["R_review_r3_constructions"] if x["holds"])}
    print(json.dumps(res, indent=1, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else str(o)))


if __name__ == "__main__":
    main()
