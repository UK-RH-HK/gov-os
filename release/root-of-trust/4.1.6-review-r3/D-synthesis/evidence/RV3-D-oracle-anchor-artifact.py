#!/usr/bin/env python3
"""AR-0004 (review r3 synthesis D) held-out probes on the ARCHITECT'S OWN reference model.

Loads release/root-of-trust/4.1.6/evidence/P4r3-trust-state-model.py unmodified (exec of its text) and uses its functions.
Nothing in the pack or the review directories is edited. No subprocesses. Output: JSON on stdout.

RV3-D-A11  Conformance-oracle sensitivity. `12` RT-72(vi) and `13` §8 require the implementation's trust-state module to
           reproduce P4r3 (34 of 34). Re-run all 34 scenarios with freshness() replaced by chain-inclusion anchor
           semantics (anchor satisfied only if the anchored (sequence, digest) is the effective TSS or in its
           prior_states). If both semantics pass all 34, the oracle cannot detect the RV3-B-H2(b) defect.
RV3-D-A12  RV3-B-A12 re-derived with the architect's functions (independent of reviewer B's model): current pin at t10,
           t9/t10/rv7 withheld, trust-state key presents t100 chaining t1,t5 only.
RV3-D-A13  verify-artifact A7 with a realisable (non-circular) construction. A TBM cannot name the TSS that references
           its own artefact (TSS digest -> artefact statement digest -> tbm_digest -> TSS digest is a hash cycle). P4r3's
           A_valid uses exactly that circular construction. With the accepting TSS strictly after the TBM's TSS, compare
           A7 against the TSS high-water vs against the accepted-TBM high-water.
"""
import contextlib, io, json, os, sys

W = os.environ.get("REVIEW_REPO") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
SRC = os.path.join(W, "release/root-of-trust/4.1.6/evidence/P4r3-trust-state-model.py")
text = open(SRC).read()
MARK = "\nP1 = tps(1, \"P1\")"
defs, scen = text.split(MARK, 1)
scen = MARK + scen


def run_model(chain_semantics):
    ns = {"__name__": "p4r3_probe", "__file__": SRC}
    exec(compile(defs, SRC, "exec"), ns)
    if chain_semantics:
        orig_ts, orig_fr = ns["trust_state"], ns["freshness"]

        def trust_state(K, anchor=None):
            r = orig_ts(K, anchor)
            eff = next((s for s in K if s.get("kind") == "tss" and s.get("digest") == r.get("effective_tss")), None)
            r["_eff_chain"] = ({tuple(x) for x in eff["prior_states"]} | {(eff["sequence"], eff["digest"])}) if eff else set()
            return r

        def freshness(ts, vts, now, op7, max_age_days=180, clock_ok=True):
            anchor = (vts or {}).get("anchor")
            if anchor and anchor.get("digest") and ts.get("status") not in ("EQUIVOCATION", "REGRESSION"):
                if (anchor["sequence"], anchor["digest"]) not in ts.get("_eff_chain", set()):
                    seq = ts.get("effective_sequence", 0)
                    if seq == anchor["sequence"]:
                        return orig_fr(ts, vts, now, op7, max_age_days, clock_ok)  # digest mismatch branch
                    return {"axis": f"BELOW_ANCHOR(anchored ({anchor['sequence']},{anchor['digest']}) not held in effective chain; held {seq})",
                            "allowed": ["C0_diagnostics"]}
            return orig_fr(ts, vts, now, op7, max_age_days, clock_ok)

        ns["trust_state"], ns["freshness"] = trust_state, freshness
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(scen, SRC, "exec"), ns)
    out = json.loads(buf.getvalue())
    return ns, out


ns_seq, out_seq = run_model(False)
ns_chain, out_chain = run_model(True)
agree_seq = {k for k, v in out_seq["scenarios"].items() if v["agrees"]}
agree_chain = {k for k, v in out_chain["scenarios"].items() if v["agrees"]}
A11 = {
    "scenarios": len(out_seq["scenarios"]),
    "sequence_semantics_agree": len(agree_seq),
    "chain_inclusion_semantics_agree": len(agree_chain),
    "scenarios_that_distinguish_the_two": sorted(agree_seq ^ agree_chain),
    "verdict": "P4r3 cannot detect the anchor-satisfaction defect: an implementation with sequence-only anchors passes 34/34"
    if agree_seq == agree_chain and len(agree_seq) == len(out_seq["scenarios"]) else "P4r3 distinguishes the semantics",
}


def a12(ns):
    tps, tss, rel, revo, trust_state, freshness, negative_set, DAY = (ns[k] for k in ("tps", "tss", "rel", "revo", "trust_state", "freshness", "negative_set", "DAY"))
    P1 = tps(1, "P1"); P2 = tps(2, "P2", prior=[(1, "P1")])
    now = 1000 * DAY
    t1 = tss(1, "t1", policy=(1, "P1"))
    t5 = tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"))
    t9 = tss(9, "t9", prior=[(1, "t1"), (5, "t5")], policy=(2, "P2"), revs=["rv7"])
    t10 = tss(10, "t10", prior=[(1, "t1"), (5, "t5"), (9, "t9")], policy=(2, "P2"), revs=["rv7"])
    t100 = tss(100, "t100", prior=[(1, "t1"), (5, "t5")], policy=(2, "P2"))
    R7 = rel("R7", 7); rv7 = revo("rv7", ["R7"])
    pin = {"anchor": {"sequence": 10, "digest": "t10", "at": now - 1 * DAY, "method": "pin"}}
    res = {}
    K_honest = [P1, P2, t1, t5, t9, t10, R7, rv7]
    K_stripped = [P1, P2, t1, t5, R7]
    K_attack = [P1, P2, t1, t5, t100, R7]
    K_vts_holds_t10 = K_attack + [t9, t10, rv7]
    for name, K in (("honest_repo", K_honest), ("A2_strips_t9_t10_rv7", K_stripped), ("A2_strip_plus_trust_state_key_t100", K_attack),
                    ("machine_holding_t10_receives_t100", K_vts_holds_t10)):
        ts = trust_state(K, anchor=pin["anchor"])
        fr = freshness(ts, pin, now, "a")
        N = negative_set(K, ts)
        res[name] = {"trust_state": ts["status"], "effective_sequence": ts.get("effective_sequence"), "freshness": fr["axis"], "allowed": fr["allowed"],
                     "R7_in_negative_set": "R7" in N,
                     "R7_usable_as_C2_policy_root": ("C2_governed_mutation" in fr["allowed"]) and ts["status"] == "KNOWN" and "R7" not in N,
                     "R7_passes_C3_freshness_and_revocation": ("C3_trust_ingress" in fr["allowed"]) and ts["status"] == "KNOWN" and "R7" not in N}
    return res


A12 = {"sequence_semantics_(pack_24_s4.1_and_P4r3)": a12(ns_seq), "chain_inclusion_semantics": a12(ns_chain)}


def a13(ns):
    tps, tss, trust_state, verify_artifact = (ns[k] for k in ("tps", "tss", "trust_state", "verify_artifact"))
    P1 = tps(1, "P1"); P2 = tps(2, "P2", prior=[(1, "P1")]); P3 = tps(3, "P3", prior=[(1, "P1"), (2, "P2")])
    t1 = tss(1, "t1", policy=(1, "P1"))
    t5 = tss(5, "t5", prior=[(1, "t1")], policy=(2, "P2"))
    t9 = tss(9, "t9", prior=[(1, "t1"), (5, "t5")], policy=(3, "P3"))                        # named by the binary's TBM (exists before the build)
    t10 = tss(10, "t10", prior=[(1, "t1"), (5, "t5"), (9, "t9")], policy=(3, "P3"), arts=["A1"])  # published after the build, references the artefact
    ba = {"kind": "build-att", "artifact": "A1", "tbm": "tbm1", "signer": "kb"}
    K = [P1, P2, P3, ns["root"](1), t1, t5, t9, t10, ba]
    key_purposes = {"ka1": ["release-artifact"], "ka2": ["release-artifact"], "kb": ["build-attestation"]}
    thr = {"release-artifact": 2, "build-attestation": 1}
    TBM = {"digest": "tbm1", "root_version": 1, "tps_version": 3, "tps_digest": "P3", "tss_sequence": 9, "tss_digest": "t9"}
    art = {"digest": "A1", "signers": ["ka1", "ka2"], "tbm": TBM}
    ts = trust_state(K)
    tss_high_water_after_ingest = {"root": 1, "tps": 3, "tss": ts["effective_sequence"]}
    previous_binary_tbm_high_water = {"root": 1, "tps": 2, "tss": 5}
    return {
        "effective_tss_holding_the_artifact_reference": ts["effective_tss"],
        "A7_against_TSS_high_water": verify_artifact(art, K, ts, tss_high_water_after_ingest, thr, key_purposes),
        "A7_against_accepted_TBM_high_water": verify_artifact(art, K, ts, previous_binary_tbm_high_water, thr, key_purposes),
        "first_run_self_check_against_TSS_high_water_refuses": TBM["tss_sequence"] < tss_high_water_after_ingest["tss"],
        "P4r3_A_valid_construction": "TBM names t9 and t9 itself references A1 (tbm_digest tbm1): a hash cycle, not realisable",
    }


A13 = a13(ns_seq)


def a15(ns):
    """RV3-D-A15: H2 reaching the TCB. A GENUINE production binary A7x (release-artifact x2, build attestation, TSS reference) is
    later revoked (refuse_install) for a security defect in TSS t9. A pinned CI runner upgrades binaries with verify-artifact
    (C3: A9 needs ANCHORED). A2 withholds t9/t10 and the revocation. Evaluate A9 (freshness) + A1-A8 with the architect's
    functions, (i) stale pin at t5 (proposed OP-7 (a)); (ii) current pin at t10 plus a trust-state-key TSS t100 chaining t1,t5."""
    tps, tss, revo, trust_state, freshness, verify_artifact, DAY = (ns[k] for k in ("tps", "tss", "revo", "trust_state", "freshness", "verify_artifact", "DAY"))
    P1 = tps(1, "P1"); P2 = tps(2, "P2", prior=[(1, "P1")])
    now = 1000 * DAY
    t1 = tss(1, "t1", policy=(1, "P1"))
    t4 = tss(4, "t4", prior=[(1, "t1")], policy=(2, "P2"))
    t5 = tss(5, "t5", prior=[(1, "t1"), (4, "t4")], policy=(2, "P2"), arts=["A7x"])
    t9 = tss(9, "t9", prior=[(1, "t1"), (4, "t4"), (5, "t5")], policy=(2, "P2"), arts=["A7x"], revs=["rvA"])
    t10 = tss(10, "t10", prior=[(1, "t1"), (4, "t4"), (5, "t5"), (9, "t9")], policy=(2, "P2"), arts=["A7x"], revs=["rvA"])
    t100 = tss(100, "t100", prior=[(1, "t1"), (4, "t4"), (5, "t5")], policy=(2, "P2"), arts=["A7x"])
    ba = {"kind": "build-att", "artifact": "A7x", "tbm": "tbmx", "signer": "kb"}
    key_purposes = {"ka1": ["release-artifact"], "ka2": ["release-artifact"], "kb": ["build-attestation"]}
    thr = {"release-artifact": 2, "build-attestation": 1}
    TBM = {"digest": "tbmx", "root_version": 1, "tps_version": 2, "tps_digest": "P2", "tss_sequence": 4, "tss_digest": "t4"}
    art = {"digest": "A7x", "signers": ["ka1", "ka2"], "tbm": TBM}
    tbm_high = {"root": 1, "tps": 2, "tss": 4}
    rows = {}
    for name, K, anchor in (("honest_repo_current_pin_t10", [P1, P2, ns["root"](1), t1, t4, t5, t9, t10, ba, revo("rvA", ["A7x"])], {"sequence": 10, "digest": "t10", "at": now - DAY, "method": "pin"}),
                            ("stale_pin_t5_A2_withholds_t9_t10_rvA", [P1, P2, ns["root"](1), t1, t4, t5, ba], {"sequence": 5, "digest": "t5", "at": now - 200 * DAY, "method": "pin"}),
                            ("current_pin_t10_A2_withholds_plus_trust_state_key_t100", [P1, P2, ns["root"](1), t1, t4, t5, t100, ba], {"sequence": 10, "digest": "t10", "at": now - DAY, "method": "pin"})):
        ts = trust_state(K, anchor=anchor)
        fr = freshness(ts, {"anchor": anchor}, now, "a")
        va = verify_artifact(art, K, ts, tbm_high, thr, key_purposes)
        rows[name] = {"freshness": fr["axis"], "A9_C3_allowed": "C3_trust_ingress" in fr["allowed"], "A1_A8_result": va,
                      "revoked_genuine_binary_accepted": ("C3_trust_ingress" in fr["allowed"]) and va == "ACCEPTED"}
    return rows


A15 = {"sequence_semantics_(pack_24_s4.1_and_P4r3)": a15(ns_seq), "chain_inclusion_semantics": a15(ns_chain)}

print(json.dumps({"probe": "RV3-D oracle / anchor / artifact", "model": "release/root-of-trust/4.1.6/evidence/P4r3-trust-state-model.py (unmodified)",
                  "RV3-D-A11_oracle_sensitivity": A11, "RV3-D-A12_anchor_bypass_with_architect_functions": A12,
                  "RV3-D-A13_verify_artifact_A7_non_circular": A13, "RV3-D-A15_revoked_genuine_binary_on_pinned_ci": A15}, indent=1, sort_keys=True, default=str))
