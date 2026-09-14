#!/usr/bin/env python3
"""VA4 — CD3-3 `verify-artifact` built-source scenarios against the revision-4 rules (BC-3, RV3-H3).

The rule functions are those of `P4r4-trust-state-model.py` in this directory (loaded by path, not copied), so the source
binding evaluated here is the one the conformance oracle mutates. Scenario shapes: RV3-B-A08 and its REJECTED-candidate
variant (review r3 B `04` acceptance cases), RV3-D-A03 (OP-4 "no"), and the minimum-capability routes restated in `25` §7.

Each row names the adversary's capabilities, the expected revision-4 result and the observed one. Rows marked
`documents_minimum_set` are expected to be ACCEPTED: they state the true minimum capability set for an accepted malicious
production binary under the corrected rules (CD3-3 (3)). No files, no subprocesses. Output: JSON on stdout.
"""
import importlib.util, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p4r4_model", os.path.join(HERE, "P4r4-trust-state-model.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
GOOD = ("commit-good", "tree-good", "inputs-good")
EVIL = ("commit-evil", "tree-evil", "inputs-good")
GEN = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7]
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]


def anchored(seq, d):
    mach = m.human(seq, d, 0)
    mach["vts"]["accepted_tbm"] = {"root": 1, "tps": 2, "tss": 5}
    return mach


def world(release_stmts, attestations, artifact_stmt, build_atts, extra=(), root_stmt=None, tps2=None):
    """Honest downstream publication: the trust-state publisher references the attestations and the artefact in t11."""
    t11 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], atts=[a["d"] for a in attestations], arts=[artifact_stmt["digest"]], issued_at=NOW - HOUR)
    base = [root_stmt or m.ROOT1, m.TPS1, tps2 or m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7]
    return base + list(release_stmts) + list(attestations) + list(build_atts) + [artifact_stmt, t11] + list(extra)


def run(label, adversary, expected, K, art, documents_minimum_set=False, params=None, rules=None):
    saved_p, saved_r = dict(m.P), dict(m.R)
    m.P.update(params or {})
    m.R.update(rules or {})
    try:
        got = m.verify_artifact(art, K, anchored(11, "t11"), NOW, "a")
    finally:
        m.P.clear(); m.P.update(saved_p)
        m.R.clear(); m.R.update(saved_r)
    return {"scenario": label, "adversary_capabilities": adversary, "expected_revision_4": expected, "observed": got,
            "as_expected": got == expected, "documents_minimum_set": documents_minimum_set}


rows = []
C11 = m.release("C11", 0, stage="candidate", source=GOOD)
A11 = m.attest("a11", "C11", source=GOOD)

# 1. RV3-B-A08: release-final thief names C' while promoting from the genuine attested candidate (identical kernel tree)
F_EVIL = m.release("F-evil", 12, promoted_from="C11", source=EVIL, signers=["rf1"])
T_E = m.tbm("tbm-e", 2, "TPS2", 10, "t10", "F-evil", source=EVIL)
ART_E = m.artifact("A-evil", "F-evil", T_E)
K1 = world([C11, F_EVIL], [A11], ART_E, [m.build_att("A-evil", "tbm-e", EVIL)])
rows.append(run("RV3-B-A08 final names commit-evil, promoted from the genuine attested candidate C11",
                ["release-final key", "release pipeline input (A5/A6)", "honest rebuilder, artefact custodians and trust-state publisher"], "RELEASE_IDENTITY_MISMATCH(source)", K1, ART_E))
rows.append(run("RV3-B-A08 under the revision-3 rule (source taken from the final's release_commit) — reproduction of the defect",
                ["as above"], "ACCEPTED", K1, ART_E, rules={"source_binding": False}))

# 2. RV3-B-A08 variant: the candidate naming C' was REJECTED by the independent verifier
C13 = m.release("C13", 0, stage="candidate", source=EVIL, signers=["rc1"])
A13 = m.attest("a13", "C13", verdict="REJECTED", source=EVIL)
F13 = m.release("F13", 13, promoted_from="C13", source=EVIL, signers=["rf1"])
T13 = m.tbm("tbm-13", 2, "TPS2", 10, "t10", "F13", source=EVIL)
ART13 = m.artifact("A-13", "F13", T13)
K2 = world([C13, F13], [A13], ART13, [m.build_att("A-13", "tbm-13", EVIL)])
rows.append(run("RV3-B-A08 variant: final promoted from a candidate the verifier REJECTED",
                ["release-candidate key", "release-final key", "pipeline input"], "ARTIFACT_SOURCE_REJECTED", K2, ART13))
K2b = world([C13, F13, A11, C11], [A11, m.attest("a13acc", "C13", verdict="ACCEPTED", source=GOOD)], ART13, [m.build_att("A-13", "tbm-13", EVIL)])
rows.append(run("variant: an ACCEPTED attestation exists for the candidate digest but names a different source",
                ["verification-attestation for other source", "release keys", "pipeline input"], "ARTIFACT_SOURCE_UNVERIFIED", K2b, ART13))

# 3. RV3-D-A03 (OP-4 "no"): one everyday key holds release-candidate and release-final
G_OP4, THR = m.grants_v1({"kc": ["release-final", "release-candidate"]})
ROOT_OP4 = m.root(1, G_OP4, THR)
C_P = m.release("C-prime", 0, stage="candidate", source=EVIL, signers=["kc"])
F_P = m.release("F-prime", 14, promoted_from="C-prime", source=EVIL, signers=["kc"])
T_P = m.tbm("tbm-p", 2, "TPS2", 10, "t10", "F-prime", source=EVIL)
ART_P = m.artifact("A-prime", "F-prime", T_P)
K3 = world([C_P, F_P], [], ART_P, [m.build_att("A-prime", "tbm-p", EVIL)], root_stmt=ROOT_OP4)
rows.append(run("RV3-D-A03 OP-4 'no': the everyday candidate/final key signs C' and F' naming commit-evil",
                ["release-candidate + release-final (one key under OP-4 'no')", "pipeline input"], "ARTIFACT_SOURCE_UNVERIFIED", K3, ART_P))
F_P2 = m.release("F-prime2", 14, promoted_from="C11", source=EVIL, signers=["kc"])
T_P2 = m.tbm("tbm-p2", 2, "TPS2", 10, "t10", "F-prime2", source=EVIL)
ART_P2 = m.artifact("A-prime2", "F-prime2", T_P2)
K3b = world([C11, F_P2], [A11], ART_P2, [m.build_att("A-prime2", "tbm-p2", EVIL)], root_stmt=ROOT_OP4)
rows.append(run("RV3-D-A03 variant: F' promoted from the genuine attested C11 but naming commit-evil",
                ["one OP-4 'no' key", "pipeline input"], "RELEASE_IDENTITY_MISMATCH(source)", K3b, ART_P2))

# 4. Route S: malicious source through a stolen verification-attestation key (true minimum under the architecture minimum)
C_S = m.release("C-s", 0, stage="candidate", source=EVIL, signers=["rc1"])
A_S = m.attest("a-s", "C-s", verdict="ACCEPTED", source=EVIL, signers=["va1"])
F_S = m.release("F-s", 15, promoted_from="C-s", source=EVIL, signers=["rf1"])
T_S = m.tbm("tbm-s", 2, "TPS2", 10, "t10", "F-s", source=EVIL)
ART_S = m.artifact("A-s", "F-s", T_S)
K4 = world([C_S, F_S], [A_S], ART_S, [m.build_att("A-s", "tbm-s", EVIL)])
rows.append(run("route S: stolen verification-attestation, release-candidate and release-final keys; honest downstream custodians",
                ["verification-attestation key", "release-candidate key", "release-final key", "pipeline input (A5/A6)"], "ACCEPTED", K4, ART_S, documents_minimum_set=True))
rows.append(run("route S under owner option OP-2 'root-registered production source' (TPS production_sources lists only the attested genuine source)",
                ["as route S"], "ARTIFACT_SOURCE_UNREGISTERED", K4, ART_S, params={"root_registered_source": True}))
G_VA2, THR_VA2 = m.grants_v1({"va2": ["verification-attestation"]})
THR_VA2["verification-attestation"] = 2
rows.append(run("route S under owner option OP-2 'verification-attestation threshold 2' with one stolen verifier key",
                ["one of two verification-attestation keys", "release keys", "pipeline input"], "ARTIFACT_SOURCE_UNVERIFIED",
                world([C_S, F_S], [A_S], ART_S, [m.build_att("A-s", "tbm-s", EVIL)], root_stmt=m.root(1, G_VA2, THR_VA2)), ART_S))
C_S1 = m.release("C-s1", 0, stage="candidate", source=EVIL, signers=["kc"])
A_S1 = m.attest("a-s1", "C-s1", verdict="ACCEPTED", source=EVIL, signers=["va1"])
F_S1 = m.release("F-s1", 16, promoted_from="C-s1", source=EVIL, signers=["kc"])
T_S1 = m.tbm("tbm-s1", 2, "TPS2", 10, "t10", "F-s1", source=EVIL)
ART_S1 = m.artifact("A-s1", "F-s1", T_S1)
rows.append(run("route S under OP-4 'no': stolen verification-attestation key and the everyday candidate/final key",
                ["verification-attestation key", "one OP-4 'no' release key", "pipeline input"], "ACCEPTED",
                world([C_S1, F_S1], [A_S1], ART_S1, [m.build_att("A-s1", "tbm-s1", EVIL)], root_stmt=ROOT_OP4), ART_S1, documents_minimum_set=True))

# 5. Route B: malicious bytes claimed as a build of genuine attested source (unchanged from revision 3)
F11 = m.release("F11", 11, promoted_from="C11", source=GOOD)
T_B = m.tbm("tbm-b", 2, "TPS2", 10, "t10", "F11", source=GOOD)
ART_B = m.artifact("A-malicious-bytes", "F11", T_B, signers=["ra1", "ra2"])
K5 = world([C11, F11], [A11], ART_B, [m.build_att("A-malicious-bytes", "tbm-b", GOOD, signers=["ba1"])])
rows.append(run("route B: stolen release-artifact x2, build-attestation and trust-state keys; genuine attested source named",
                ["release-artifact key 1", "release-artifact key 2", "build-attestation key", "trust-state key"], "ACCEPTED", K5, ART_B, documents_minimum_set=True))
rows.append(run("route B with one release-artifact key", ["release-artifact key 1", "build-attestation key", "trust-state key"], "THRESHOLD_NOT_MET",
                K5, dict(ART_B, signers=["ra1"])))
rows.append(run("route B without a build attestation", ["release-artifact x2", "trust-state key"], "ARTIFACT_BUILD_UNATTESTED",
                [s for s in K5 if s["kind"] != "build-att"], ART_B))

# 6. Custodial pre-checks (05 §7 rules 6-7): the rebuilder, artefact custodians and TSS publisher run A4 before signing.
#    Modelled as the same check on the draft publication; each refuses the RV3-B-A08 artefact before any signature.
for stage in ("rebuilder (before build-attestation)", "release-artifact custodians (before signing)", "trust-state publisher (before referencing)"):
    rows.append(run(f"custodial pre-check at {stage} on the RV3-B-A08 artefact", ["release-final key", "pipeline input"], "RELEASE_IDENTITY_MISMATCH(source)", K1, ART_E))

minimum = [r for r in rows if r["documents_minimum_set"]]
summary = {"rows": len(rows), "as_expected": sum(r["as_expected"] for r in rows), "not_as_expected": [r["scenario"] for r in rows if not r["as_expected"]],
           "refused_attacks": sum(1 for r in rows if r["expected_revision_4"] != "ACCEPTED" and r["as_expected"]),
           "minimum_capability_sets_accepted": [{"route": r["scenario"], "capabilities": r["adversary_capabilities"]} for r in minimum],
           "single_key_can_mint_accepted_binary": False}
print(json.dumps({"summary": summary, "rows": rows}, indent=1))
