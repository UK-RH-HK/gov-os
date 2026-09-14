#!/usr/bin/env python3
"""RV4-B-arch-functions — held-out binary attacks recomputed with the ARCHITECT'S OWN rule functions (review r4 B, AR-0006).

Loads `release/root-of-trust/4.1.6/evidence/P4r4-trust-state-model.py` by path, unmodified (as the pack's own VA4 does).
The helpers `world()` and `anchored()` below re-implement, with attribution, the two small builders of
`VA4-verify-artifact-source-scenarios.py` (VA4 prints on import, so it is not imported). No files, no subprocesses.

Questions
  AF1 (RV4-B-A01) Route B with honest downstream custodians. 05 §7 rule 6 and 25 §9 give the release-artifact custodians
      and the trust-state publisher a check (A1, A3, A4a, A4b, A6 on the draft) and no rebuild. With ONE stolen
      build-attestation key and the release pipeline's input (the binary handed to custodians), do honest custodians'
      checks pass and does verify-artifact accept? VA4's "route B" row is compared object-for-object.
  AF2 (RV4-B-A02) Route S with honest release signers. 05 §7 rule 2 has release signers reproduce the payload from
      `release.source` (reproduction, not legitimacy); R-REL-6 has promotion require an ACCEPTED attestation. With ONE
      stolen verification-attestation key, the pipeline's commit, and the honest verifier's REJECTED verdict not held by
      the publisher, does verify-artifact accept? And with the REJECTED verdict held?
  AF3 (RV4-B-A03) First binary by independent tooling (06 §2 step 6 (b): A2–A6). A revoked genuine binary served by a
      transport/repository adversary with the revocation withheld.
"""
import importlib.util, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("REVIEW_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
P4 = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "P4r4-trust-state-model.py")
spec = importlib.util.spec_from_file_location("p4r4_model", P4)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
GOOD = ("commit-good", "tree-good", "inputs-good")
EVIL = ("commit-evil", "tree-evil", "inputs-good")
PRIOR10 = [(1, "t1"), (5, "t5"), (9, "t9"), (10, "t10")]


def anchored(seq, d):  # as VA4 `anchored`
    mach = m.human(seq, d, 0)
    mach["vts"]["accepted_tbm"] = {"root": 1, "tps": 2, "tss": 5}
    return mach


def world(release_stmts, attestations, artifact_stmt, build_atts, extra=(), root_stmt=None):  # as VA4 `world` (honest trust-state publisher signs t11 with ts1)
    t11 = m.tss(11, "t11", prior=PRIOR10, pol=(2, "TPS2"), revs=["R7"], atts=[a["d"] for a in attestations], arts=[artifact_stmt["digest"]], issued_at=NOW - HOUR)
    base = [root_stmt or m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7]
    return base + list(release_stmts) + list(attestations) + list(build_atts) + [artifact_stmt, t11] + list(extra)


def stage(art, K_all, stage_name, with_publication=False):
    """The custodial pre-check of 25 §9 on a DRAFT (before the artefact is signed or referenced), composed from P4r4's own
    primitives: A3 (final verifies), A4a (build attestation for this digest, TBM and source; custodian and publisher stages),
    A4b without the TSS reference (candidate verifies, V8 tree and source equality, ACCEPTED attestation naming the source,
    no REJECTED attestation), A6 (TBM components resolve). A1 is the digest of the bytes the custodian was given."""
    K, refused, hw = m.ingest(K_all, {"vts": {}}, NOW)
    rootS = m.eff_root_stmt(K)
    F = next((s for s in K if s["kind"] == "release-final" and s["d"] == art["release"]), None)
    if F is None:
        return "A3 ARTIFACT_IDENTITY_MISMATCH"
    t = art["tbm"]
    if stage_name in ("custodian", "publisher"):
        bas = {k for b in K if b["kind"] == "build-att" and b["artifact"] == art["digest"] and b["tbm"] == t["d"] and b["source"] == t["source"] for k in m.valid_signers(b, rootS)}
        if len(bas) < max(rootS["thresholds"].get("build-attestation", 1), 1):
            return "A4a ARTIFACT_BUILD_UNATTESTED"
    C = next((s for s in K if s["kind"] == "release-candidate" and s["d"] == F["promoted_from"]), None)
    if C is None or C["tree"] != F["tree"] or C["source"] != F["source"]:
        return "A4b RELEASE_IDENTITY_MISMATCH(source)"
    if t["source"] != C["source"]:
        return "A4b ARTIFACT_SOURCE_UNVERIFIED"
    atts = [a for a in K if a["kind"] == "att" and a["candidate"] == C["d"]]
    if any(a["verdict"] == "REJECTED" for a in atts):
        return "A4b ARTIFACT_SOURCE_REJECTED"
    if not [a for a in atts if a["verdict"] == "ACCEPTED" and a["source"] == C["source"]]:
        return "A4b ARTIFACT_SOURCE_UNVERIFIED"
    held = {("tps", s["v"]): s["d"] for s in K if s["kind"] == "tps"}
    held.update({("tss", s["seq"]): s["d"] for s in K if s["kind"] == "tss"})
    if held.get(("tps", t["tps_v"])) != t["tps_d"] or held.get(("tss", t["tss_seq"])) != t["tss_d"] or t["embedded_release"] != F["d"]:
        return "A6 BINARY_T0_UNVERIFIED"
    return "PASS"


out = {"instrument": "P4r4-trust-state-model.py rule functions (architect, unmodified, loaded by path)", "rows": []}

# ------------------------------------------------------------------------------------------------ AF1 route B with honest custodians
C11 = m.release("C11", 0, stage="candidate", source=GOOD)
A11 = m.attest("a11", "C11", source=GOOD)
F11 = m.release("F11", 11, promoted_from="C11", source=GOOD)
T_B = m.tbm("tbm-b", 2, "TPS2", 10, "t10", "F11", source=GOOD)
draft = m.artifact("A-malicious-bytes", "F11", T_B, signers=[])
forged_ba = m.build_att("A-malicious-bytes", "tbm-b", GOOD, signers=["ba1"])  # the ONLY stolen key
pre = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, C11, A11, F11, forged_ba]
st_cust = stage(draft, pre, "custodian")
signed = m.artifact("A-malicious-bytes", "F11", T_B, signers=["ra1", "ra2"])  # honest custodians sign after their check passed
st_pub = stage(signed, pre + [signed], "publisher")
K_AF1 = world([C11, F11], [A11], signed, [forged_ba])  # honest publisher's t11 (ts1)
res_AF1 = m.verify_artifact(signed, K_AF1, anchored(11, "t11"), NOW, "a")
# VA4's route B row, rebuilt exactly as VA4 builds it (K5, ART_B)
ART_B = m.artifact("A-malicious-bytes", "F11", T_B, signers=["ra1", "ra2"])
K5 = world([C11, F11], [A11], ART_B, [m.build_att("A-malicious-bytes", "tbm-b", GOOD, signers=["ba1"])])
out["rows"].append({
    "id": "AF1", "attack": "RV4-B-A01: one stolen build-attestation key + release-pipeline input (malicious bytes handed to the custodians for the genuine attested source); every other custodian honest",
    "attacker_keys": ["ba1 (build-attestation)"], "honest_signers": {"release-artifact": ["ra1", "ra2"], "trust-state": ["ts1"], "release-candidate": ["rc1"], "release-final": ["rf1"], "verification-attestation": ["va1"]},
    "custodian_stage_on_draft (release-artifact custodians, 25 §9)": st_cust, "publisher_stage (trust-state publisher, 25 §9)": st_pub,
    "verify_artifact_on_anchored_machine_with_currency": res_AF1,
    "identical_to_VA4_route_B_world": json.dumps(K5, sort_keys=True, default=str) == json.dumps(K_AF1, sort_keys=True, default=str),
    "VA4_route_B_result": m.verify_artifact(ART_B, K5, anchored(11, "t11"), NOW, "a"),
    "VA4_route_B_label": "stolen release-artifact x2, build-attestation and trust-state keys (4 keys over 3 purposes)",
})

# ------------------------------------------------------------------------------------------------ AF2 route S with honest release signers
C_S = m.release("C-s", 0, stage="candidate", source=EVIL, signers=["rc1"])        # honest candidate signer reproduced the pipeline's commit
A_S = m.attest("a-s", "C-s", verdict="ACCEPTED", source=EVIL, signers=["va1"])     # the ONLY stolen key
A_R = m.attest("a-rej", "C-s", verdict="REJECTED", source=EVIL, signers=["va1"])   # what the honest verifier would have attested (same key id: the verifier's)
F_S = m.release("F-s", 15, promoted_from="C-s", source=EVIL, signers=["rf1"])       # honest promoter/signer: ACCEPTED attestation present, V8 holds
T_S = m.tbm("tbm-s", 2, "TPS2", 10, "t10", "F-s", source=EVIL)
BA_S = m.build_att("A-s", "tbm-s", EVIL, signers=["ba1"])                          # honest rebuilder reproduced the attested source
draft_s = m.artifact("A-s", "F-s", T_S, signers=[])
pre_s = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, m.T9, m.T10, m.RV7, C_S, A_S, F_S]
st_rb = stage(draft_s, pre_s, "rebuilder")
st_cu = stage(draft_s, pre_s + [BA_S], "custodian")
ART_S = m.artifact("A-s", "F-s", T_S, signers=["ra1", "ra2"])
K_AF2 = world([C_S, F_S], [A_S], ART_S, [BA_S])
out["rows"].append({
    "id": "AF2", "attack": "RV4-B-A02: one stolen verification-attestation key + pipeline commit; honest candidate and final signers, rebuilder, custodians and publisher; the honest verifier's REJECTED verdict not held by the publisher",
    "attacker_keys": ["va1 (verification-attestation)"],
    "rebuilder_stage": st_rb, "custodian_stage": st_cu,
    "verify_artifact": m.verify_artifact(ART_S, K_AF2, anchored(11, "t11"), NOW, "a"),
    "verify_artifact_when_REJECTED_attestation_is_also_held": m.verify_artifact(ART_S, K_AF2 + [A_R], anchored(11, "t11"), NOW, "a"),
    "verify_artifact_under_OP-2_S1_root_registered_source": (lambda: (m.P.update({"root_registered_source": True}), m.verify_artifact(ART_S, K_AF2, anchored(11, "t11"), NOW, "a"))[1])(),
})
m.P["root_registered_source"] = False

# ------------------------------------------------------------------------------------------------ AF3 first binary via A2–A6 tooling
C7 = m.release("C7g", 0, stage="candidate", source=GOOD)
A7 = m.attest("a7g", "C7g", source=GOOD)
F7 = m.release("F7g", 7, promoted_from="C7g", source=GOOD)
TB7 = m.tbm("tbm-7", 2, "TPS2", 5, "t5", "F7g", source=GOOD)
B7 = m.artifact("B7", "F7g", TB7)
BA7 = m.build_att("B7", "tbm-7", GOOD)
T6 = m.tss(6, "t6", prior=[(1, "t1"), (5, "t5")], pol=(2, "TPS2"), atts=["a7g"], arts=["B7"], issued_at=NOW - 300 * DAY)
T9b = m.tss(9, "t9b", prior=[(1, "t1"), (5, "t5"), (6, "t6")], pol=(2, "TPS2"), revs=["B7"], atts=["a7g"], arts=["B7"], issued_at=NOW - 10 * DAY)
T10b = m.tss(10, "t10b", prior=[(1, "t1"), (5, "t5"), (6, "t6"), (9, "t9b")], pol=(2, "TPS2"), revs=["B7"], atts=["a7g"], arts=["B7"], issued_at=NOW - DAY)
RVB7 = m.revocation("rvB7", ["B7"], issued_at=NOW - 10 * DAY)
served = [m.ROOT1, m.TPS1, m.TPS2, m.T1, m.T5, T6, C7, A7, F7, B7, BA7]   # t9b, t10b and the revocation withheld


def tooling_A2_A6(art, K_all):
    K, _, _ = m.ingest(K_all, {"vts": {}}, NOW)
    rootS = m.eff_root_stmt(K)
    if not m.verifies(art, rootS):
        return "A2 THRESHOLD_NOT_MET"
    s = stage(art, K_all, "publisher")
    if s != "PASS":
        return s
    ts = m.trust_state(K, ())
    eff = ts.get("eff")
    if not eff or art["digest"] not in eff["arts"] or "a7g" not in eff["atts"]:
        return "A5 ARTIFACT_UNREFERENCED"
    return "PASS (A2–A6)"


out["rows"].append({
    "id": "AF3", "attack": "RV4-B-A03: a genuine binary revoked for a security defect (t9b); a transport/repository adversary serves it with t6 and withholds t9b, t10b and the revocation to a machine obtaining its FIRST binary",
    "path_b_independent_tooling_A2_A6": tooling_A2_A6(B7, served),
    "path_iii_verify_artifact_machine_holding_t10b": m.verify_artifact(B7, served + [T9b, T10b, RVB7], anchored(10, "t10b"), NOW, "a"),
    "path_iii_verify_artifact_machine_anchored_by_channel_fingerprint_t10b_while_stripped": m.verify_artifact(B7, served, anchored(10, "t10b"), NOW, "a"),
})
out["summary"] = {r["id"]: {k: v for k, v in r.items() if k.startswith(("verify_artifact", "path_", "custodian", "publisher", "rebuilder", "identical", "VA4_route_B_result"))} for r in out["rows"]}
print(json.dumps(out, indent=1, default=str))
