#!/usr/bin/env python3
"""RV4-D-A03b (review r4 synthesis D, AR-0008) — for each single-line mutant that the pack's oracle did NOT detect
(RV4-D-A03), a distinguishing scenario built only from the architect's own P4r4 constructors and rule functions: the
unmodified model gives the revision-4 result, the mutant gives a different one. This shows each undetected mutant is an
effective security regression (not dead code), and therefore that the oracle's silence is a coverage gap.

Loads the unmodified P4r4 and, per mutant, a copy with exactly one line changed (same replacement strings as A03).
No files outside the scratch directory given. Output: JSON on stdout.
Usage: RV4-D-A03b-distinguishing-scenarios.py <worktree> <scratch-dir>
"""
import importlib.util, json, os, sys

sys.dont_write_bytecode = True
WT, SCR = sys.argv[1], sys.argv[2]
EV = os.path.join(WT, "release/root-of-trust/4.1.6/evidence")
SRC = open(os.path.join(EV, "P4r4-trust-state-model.py")).read()
os.makedirs(SCR, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
A03 = {}
spec = importlib.util.spec_from_file_location("a03", os.path.join(os.path.dirname(os.path.abspath(__file__)), "RV4-D-A03-oracle-regression-sensitivity.py"))
# read the MUTANTS table from A03's source without executing its main body
_src = open(spec.origin).read()
_tbl = _src[_src.index("MUTANTS = ["):_src.index("]\n\n\ndef run_py")] + "]"
ns = {}
exec(_tbl, ns)
MUT = {n: (rule, old, new) for n, rule, old, new in ns["MUTANTS"]}


def load(name, src):
    p = os.path.join(SCR, f"p4r4_{name}.py")
    open(p, "w").write(src)
    s = importlib.util.spec_from_file_location(f"p4r4_{name.replace('-', '_')}", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def both(name, fn):
    rule, old, new = MUT[name]
    assert SRC.count(old) == 1
    base, mut = load("base", SRC), load(name, SRC.replace(old, new))
    b, x = fn(base), fn(mut)
    return {"mutant": name, "rule": rule, "revision_4_model": b, "mutant_model": x, "distinguishes": json.dumps(b, sort_keys=True, default=str) != json.dumps(x, sort_keys=True, default=str)}


GOOD = ("commit-good", "tree-good", "inputs-good")
OTHER = ("commit-other", "tree-other", "inputs-good")
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]


def anchored(m, seq, d):
    mach = m.human(seq, d, 0)
    mach["vts"]["accepted_tbm"] = {"root": 1, "tps": 2, "tss": 5}
    return mach


def binary_world(m, *, cand_revoked=False, ba_source=GOOD, att_referenced=True):
    C11 = m.release("C11", 0, stage="candidate", source=GOOD)
    A11 = m.attest("a11", "C11", source=GOOD)
    F11 = m.release("F11", 11, promoted_from="C11", source=GOOD)
    T = m.tbm("tbm-g", 2, "TPS2", 10, "t10", "F11", source=GOOD)
    ART = m.artifact("A-g", "F11", T)
    BA = m.build_att("A-g", "tbm-g", ba_source)
    revs = ["R7"] + (["C11"] if cand_revoked else [])
    t11 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=revs, atts=(["a11"] if att_referenced else []), arts=["A-g"], issued_at=m.NOW - m.HOUR)
    extra = [m.revocation("rvC11", ["C11"], issued_at=m.NOW - m.HOUR)] if cand_revoked else []
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, C11, A11, F11, BA, ART, t11] + extra
    return ART, K


rows = []
# 1. A8: the final's candidate is revoked (e.g. a candidate later found to carry a defect); final and artefact not individually
rows.append(both("D-A8-omits-candidate", lambda m: (lambda a, K: m.verify_artifact(a, K, anchored(m, 11, "t11"), m.NOW, "a"))(*binary_world(m, cand_revoked=True))))
# 2. A4a: the only build attestation for this digest and TBM names a different source
rows.append(both("D-A4a-source-not-compared", lambda m: (lambda a, K: m.verify_artifact(a, K, anchored(m, 11, "t11"), m.NOW, "a"))(*binary_world(m, ba_source=OTHER))))
# 3. A4b: the ACCEPTED attestation exists but the effective TSS does not reference it
rows.append(both("D-A4b-attestation-not-TSS-referenced", lambda m: (lambda a, K: m.verify_artifact(a, K, anchored(m, 11, "t11"), m.NOW, "a"))(*binary_world(m, att_referenced=False))))


# 4. Inclusion without "held": a trust-state key thief issues t11x whose prior_states NAME the pinned (10, t10) and t9 by
#    digest (copied from the published fingerprint) but carries no revocation; A2 withholds t9, t10 and rv7.
def incl(m):
    thief = m.tss(11, "t11x", prior=PRIOR10, pol=(2, "TPS2"), revs=[], issued_at=m.NOW - m.HOUR)
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.R7, thief]
    mach = {"pins": [m.pin(10, "t10", 1)], "vts": {}}
    _, ts, fr, _ = m.evaluate_machine(K, mach, m.NOW, "a")
    tpsS = m.tps_state(K)
    return {"trust_state": ts["status"], "effective_tss": ts["effective_tss"], "freshness": fr["axis"].split(" CURRENCY")[0], "allowed": fr["allowed"],
            "revoked_R7_eligible_for_use": m.eligible_use(m.R7, m.ingest(K, mach, m.NOW)[0], ts, tpsS)["eligible"]}


rows.append(both("D-inclusion-without-held", incl))


# 5. Pin whose valid_until is 400 days after provisioning (above pin_max_validity_days 30), provisioned 100 days ago
def pincap(m):
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.R7]
    mach = {"pins": [m.pin(5, "t5", 100, validity_days=400)], "vts": {}}
    _, ts, fr, _ = m.evaluate_machine(K, mach, m.NOW, "a")
    return {"freshness": fr["axis"].split(";")[0], "allowed": fr["allowed"]}


rows.append(both("D-pin-validity-cap-not-checked", pincap))


# 6. Stateless OP-7 (c) runner: witnesses at the C3 threshold name t5, while the machine holds t10 as effective
def wit(m):
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, m.witness("w5", 5, "t5", m.NOW - m.HOUR, m.NOW + m.DAY)]
    _, ts, fr, _ = m.evaluate_machine(K, {"vts": {}}, m.NOW, "c")
    return {"effective_tss": ts["effective_tss"], "freshness": fr["axis"], "allowed": fr["allowed"]}


rows.append(both("D-witness-for-any-tss", wit))


# 7. A TSS that drops a lower artifacts[] reference (the playbook's forbidden remedy) while keeping revocations
def arts(m):
    t10a = m.tss(10, "t10a", prior=[(1, "t1"), (5, "t5"), (9, "t9")], pol=(2, "TPS2"), revs=["R7"], arts=["B7"], issued_at=m.NOW - 2 * m.DAY)
    t11d = m.tss(11, "t11d", prior=[(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10a")], pol=(2, "TPS2"), revs=["R7"], arts=[], issued_at=m.NOW - m.DAY)
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, t10a, t11d, m.RV7]
    ts = m.trust_state(K, ())
    return {"trust_state": ts["status"], "effective_tss": ts["effective_tss"]}


rows.append(both("D-admissibility-ignores-artifacts", arts))


# 8. TPS v3 that omits the held TPS v2 from prior_policies
def tpsprior(m):
    tps3 = m.tps(3, prior=[(1, "TPS1")], min_seq=1)
    K = [m.ROOT1, m.TPS1, m.TPS2, tps3]
    s = m.tps_state(K)
    return {"tps_state": s["status"], "effective_policy_version": s["eff"]["v"] if s["eff"] else None,
            "effective_min_release_sequence": s["eff"]["fields"]["min_release_sequence"] if s["eff"] else None}


rows.append(both("D-tps-prior-chain-not-checked", tpsprior))


# 9. Lift: a later CERTIFIED whose new attestation names the negative, but the effective TSS does not reference that attestation
def lift(m):
    F = m.release("F20", 20, promoted_from="C20", source=GOOD)
    a_old = m.attest("a20", "C20")
    wd = m.cert("wd20", "F20", "WITHDRAWN", 2, att="a20")
    a_new = m.attest("a20b", "C20", lifts_negative="wd20")
    c3 = m.cert("c20b", "F20", "CERTIFIED", 3, att="a20b")
    t11 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], certs=[("F20", "c20b")], atts=["a20"], issued_at=m.NOW - m.HOUR)
    K = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, F, a_old, wd, a_new, c3, t11]
    ts = m.trust_state(K, ())
    return {"F20_in_negative_set": "F20" in m.negative_set(K, ts, m.tps_state(K)["eff"])}


rows.append(both("D-lift-attestation-not-TSS-referenced", lift))


# 10. TPS lowering op7_mode from (a) to (c) without lowering_history
def op7(m):
    held = m.tps(3, fields={"op7_mode": "a"})
    arriving = m.tps(4, fields={"op7_mode": "c"})
    return m.accept_policy(held, arriving, 3)


rows.append(both("D-op7-order-c-above-a", op7))


# 11. Decision pin (protected) whose expires_at passed a day ago, for a non-local-terminal kind
def dpin(m):
    tps_eff = m.tps(2)
    pins = [{"kind": "framework_update", "digests": ["d1", "d2"], "project": "p1", "expires_at": m.NOW - m.DAY}]
    return m.trust_gate_authorised("framework_update", ["d1", "d2"], "p1", [], pins, tps_eff, m.NOW)


rows.append(both("D-decision-pin-expiry-not-checked", dpin))

print(json.dumps({"instrument": "architect P4r4 constructors and rule functions; one-line mutants as RV4-D-A03", "rows": rows,
                  "summary": {"rows": len(rows), "distinguishing": sum(r["distinguishes"] for r in rows),
                              "not_distinguishing": [r["mutant"] for r in rows if not r["distinguishes"]]}}, indent=1, default=str))
