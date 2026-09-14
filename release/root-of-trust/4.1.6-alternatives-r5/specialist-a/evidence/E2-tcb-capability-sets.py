#!/usr/bin/env python3
"""E2 (AR-0009, specialist A) — BC4-1: which capability sets yield an accepted malicious production binary?

Computed, symbolic model (signatures are key ids checked against grants; no cryptography). No files, no subprocesses.
Output: JSON on stdout.

Three rule sets are evaluated with the same enumeration, and honest actors act ONLY on the checks their design states:

  R4   revision 4 as written (bca05a7): 05 §7 rules 2-7, 25 §5/§9, 07 §7. Reproduces reviewer B's `BC` result as a control
       (B's own model is not imported here; E0 re-runs it unmodified).
  RID  "review-invariant design": revision 4 plus the literal CD4-1 closure — compiled build-attestation threshold 2 with
       two rebuilders, and verification-attestation threshold 2 (OP-2 S2) or root-registered production sources (OP-2 S1).
       Tests whether the r4 review's stated invariant is sufficient.
  SAM  this proposal (01-ALTERNATIVE §2): the release registration authority (root threshold, Q1, or a delegated quorum,
       Q2) selects source AND build inputs; a reproducer quorum q >= 2 of first-person reproductions observes the bytes;
       reproduction conflicts refuse; reproducers submit to the owner's statement store outside the release pipeline;
       the trust-state reference is a restrictor; the victim's state is selected by a typed fingerprint (bootstrap-P2) or
       by anchor + P1 pin currency (running-P1).

Readings (stated, because the r4 text does not fix them):
  inputs_fetch = "digest"  : rebuilders/reproducers obtain every build input by digest and refuse a mismatch;
  inputs_fetch = "mirror"  : they fetch the toolchain/dependencies from the mirror the release CI configuration names
                             (a lower-trust selector), as the r4 rules neither require nor forbid it.
  verifier_checks_inputs   : whether the honest independent verifier establishes the legitimacy of the named build inputs
                             (r4 05 §7 rule 3 says it "reproduces the candidate payload from release.source with the named
                             build inputs"; the payload is the kernel tree, which a toolchain does not change).

Goals: evil_bytes (bytes that are not a faithful build of the genuine source+inputs), evil_source (a malicious tree),
evil_toolchain (genuine tree built with malicious build inputs NAMED by the release process), evil_mirror (genuine tree and
named inputs, but every builder fetches the toolchain from a poisoned mirror).
"""
import itertools, json, sys

sys.dont_write_bytecode = True

B_GOOD, B_EVIL, B_EVIL_SRC, B_EVIL_TC = "B-good", "B-evil-bytes", "B-evil-source", "B-evil-toolchain"


def build(tree, inputs):
    """Deterministic honest build."""
    if tree == "good" and inputs == "good":
        return B_GOOD
    if tree == "evil":
        return B_EVIL_SRC
    return B_EVIL_TC


def minimal_sets(fn, caps, **opt):
    acc = []
    for n in range(len(caps) + 1):
        for combo in itertools.combinations(caps, n):
            s = set(combo)
            if any(a <= s for a in acc):
                continue
            if fn(s, **opt) == "ACCEPTED":
                acc.append(s)
    return [sorted(a) for a in acc]


# ============================================================================================ R4 and RID (same code path)
def r4_like(caps, goal, S="S0", rebuilders=1, ba_thr=1, va_thr=1, op4_no=False, inputs_fetch="digest",
            verifier_checks_inputs=False, rejected_held=True):
    """Honest actors act only on the checks revision 4 states. `pipeline` = the attacker controls what the release
    pipeline hands to signers, custodians and the publisher. Without `pipeline`, the release process is the owner's."""
    pipe = "pipeline" in caps
    mirror = "input_mirror" in caps
    stolen = lambda k: k in caps
    rc_key = "rf" if op4_no else "rc"
    tree, named_inputs = "good", "good"
    if goal == "evil_source":
        tree = "evil"
    if goal == "evil_toolchain":
        named_inputs = "evil"
    fetched = lambda named: "evil" if (mirror and inputs_fetch == "mirror") else named
    non_genuine_release = (tree, named_inputs) != ("good", "good")
    # --- candidate: stolen key, or the honest candidate signer reproducing the payload of the pipeline's commit (05 §7 r2)
    if non_genuine_release and not (stolen(rc_key) or pipe):
        return "NO_CANDIDATE"
    # --- verification attestation (TA-11): the honest verifier rejects an evil tree; evil inputs only if it checks them
    honest_rejects = tree == "evil" or (named_inputs == "evil" and verifier_checks_inputs)
    thr_va = va_thr if S == "S2" else 1
    if honest_rejects:
        if sum(1 for k in ("va", "va2")[:thr_va] if stolen(k)) < thr_va:
            return "NO_ACCEPTED_ATTESTATION"
        if rejected_held and not stolen("rf"):
            return "NO_FINAL"
    # --- S1: the honest root ceremony registers the source record of the owner's verification
    if S == "S1" and honest_rejects:
        return "ARTIFACT_SOURCE_UNREGISTERED"
    # --- final
    if non_genuine_release and not (stolen("rf") or pipe):
        return "NO_FINAL"
    # --- the binary handed to rebuilders/custodians/publisher
    if goal == "evil_bytes":
        if not pipe:
            return "NO_BYTES_DELIVERED"
        handed = B_EVIL
    else:
        handed = build(tree, fetched(named_inputs))
    # --- honest rebuilders, custodians and the publisher act on a NON-genuine release only when the attacker's pipeline
    # hands it to them (reviewer B's reading); otherwise the attacker needs their keys.
    honest_acts = (not non_genuine_release and goal != "evil_bytes") or pipe
    # --- build attestations: honest rebuilders reproduce the attested source with inputs obtained per the reading
    honest_digest = build(tree, fetched(named_inputs))
    signers = {k for k in ("ba", "ba2")[:rebuilders] if (honest_digest == handed and honest_acts) or stolen(k)}
    if len(signers) < ba_thr:
        return "ARTIFACT_BUILD_UNATTESTED"
    # --- release-artifact custodians (stage custodian) and publisher (stage publisher): re-check, do not rebuild.
    # A genuine release process hands them `handed`; an attacker pipeline hands them whatever it chose.
    if not honest_acts and not (stolen("ra1") and stolen("ra2")):
        return "THRESHOLD_NOT_MET"
    if not honest_acts and not stolen("ts"):
        return "NOT_PUBLISHED"
    if handed == B_GOOD:
        return "BINARY_NOT_MALICIOUS"
    return "ACCEPTED"


R4_CAPS = ["rc", "rf", "va", "va2", "ba", "ba2", "ra1", "ra2", "ts", "pipeline", "input_mirror"]


# ============================================================================================ SAM (this proposal)
def sam(caps, goal, reg="Q2", n_rep=3, q=2, victim="running-P1", submission="independent"):
    pipe, transport, channel = "pipeline" in caps, "transport" in caps, "channel" in caps
    upstream = "toolchain_upstream" in caps
    reg_keys = ["root1", "root2"] if reg == "Q1" else ["reg1", "reg2"]
    reg_quorum_stolen = all(k in caps for k in reg_keys)
    rep_keys = ["rep1", "rep2", "rep3"][:n_rep]
    stolen_rep = [k for k in rep_keys if k in caps]
    # ---- registrations. The owner registers R9 (genuine tree; input manifest checked against upstream-signed toolchain
    # releases and the lockfile in the tree, R-REG-2). A compromised UPSTREAM toolchain release is not detectable (TA-12).
    regs = {"R9": ("good", "evil" if upstream else "good", "owner")}
    if goal in ("evil_source", "evil_toolchain") and reg_quorum_stolen:
        regs["R9x"] = ("evil", "good", "attacker") if goal == "evil_source" else ("good", "evil", "attacker")
    # ---- reproductions. Inputs are fetched by digest from the registered manifest (R-REP-2): a poisoned mirror yields a
    # digest mismatch and no reproduction, so `input_mirror` changes nothing.
    repro = []  # (release, digest, signer, origin)
    for k in rep_keys:
        t, i, _ = regs["R9"]
        repro.append(("R9", build(t, i), k, "honest"))
        if "R9x" in regs and pipe:
            t, i, _ = regs["R9x"]
            repro.append(("R9x", build(t, i), k, "honest"))
    if goal in ("evil_bytes", "evil_mirror"):
        target_release, attacker_digest = "R9", B_EVIL if goal == "evil_bytes" else B_EVIL_TC
    elif goal == "evil_toolchain" and upstream:
        target_release, attacker_digest = "R9", B_EVIL_TC
    else:
        target_release = "R9x"
        attacker_digest = B_EVIL_SRC if goal == "evil_source" else B_EVIL_TC
    if goal in ("evil_bytes", "evil_mirror") or target_release == "R9x":
        for k in stolen_rep:
            repro.append((target_release, attacker_digest, k, "attacker"))
    # ---- owner store: honest submissions reach it outside the pipeline (R-REP-3) unless submission == via_pipeline and
    # the attacker controls the pipeline; attacker-signed statements reach it only through the pipeline.
    def in_owner_store(r):
        if r[3] == "honest":
            return not (submission == "via_pipeline" and pipe)
        return pipe
    store = [r for r in repro if in_owner_store(r)]
    owner_published = set()
    for rel in [r for r, v in regs.items() if v[2] == "owner"]:
        digests = {r[1] for r in store if r[0] == rel}
        for d in digests:
            if len({r[2] for r in store if r[0] == rel and r[1] == d}) >= q and len(digests) == 1:
                owner_published.add(d)
    # ---- state selection
    attacker_tss = "ts" in caps
    if victim == "bootstrap-P2":
        selected = "attacker" if (channel and attacker_tss) else "owner"
    else:  # anchored machine with a P1 pin proof: any admissible descendant of the anchor within the window
        selected = "attacker" if (attacker_tss and transport) else "owner"
    published = set(owner_published) | ({attacker_digest} if selected == "attacker" else set())
    visible_regs = {r for r, v in regs.items() if v[2] == "owner" or selected == "attacker"}
    # ---- what the victim holds: the owner's published store, plus what a transport attacker adds or withholds
    def visible(r):
        if r in store and not (transport and r[1] != attacker_digest):
            return True
        return transport and (r[3] == "attacker" or r[1] == attacker_digest)
    vis = [r for r in repro if visible(r)]
    rel = target_release
    if rel not in visible_regs:
        return "RELEASE_UNREGISTERED"
    digests = {r[1] for r in vis if r[0] == rel}
    if len({r[2] for r in vis if r[0] == rel and r[1] == attacker_digest}) < q:
        return "REPRODUCTION_QUORUM_NOT_MET"
    if len(digests) > 1:
        return "REPRODUCTION_CONFLICT"
    if attacker_digest not in published:
        return "BINARY_NOT_PUBLISHED"
    return "ACCEPTED"


SAM_CAPS = ["root1", "root2", "reg1", "reg2", "rep1", "rep2", "rep3", "ts", "rc", "rf", "va", "pipeline", "transport", "channel",
            "input_mirror", "toolchain_upstream"]


def main():
    out = {"model": "E2 BC4-1 capability sets (AR-0009)", "readings": __doc__.split("Readings")[1].split("Goals:")[0].strip()}
    # ---------------- control: R4 as written
    r4 = []
    for goal in ("evil_bytes", "evil_source", "evil_toolchain", "evil_mirror"):
        for S in ("S0", "S1", "S2"):
            for fetch, vci, rh in itertools.product(("digest", "mirror"), (False, True), (True, False)):
                    opt = dict(goal=goal, S=S, rebuilders=1, ba_thr=1, va_thr=2 if S == "S2" else 1, inputs_fetch=fetch,
                               verifier_checks_inputs=vci, rejected_held=rh)
                    ms = minimal_sets(r4_like, R4_CAPS, **opt)
                    r4.append({"goal": goal, "OP-2": S, "inputs_fetch": fetch, "verifier_checks_inputs": vci, "REJECTED_held": rh,
                               "minimal_sets": ms, "min_keys": min((len([c for c in s if c not in ("pipeline", "input_mirror")]) for s in ms), default=None)})
    out["R4_as_written"] = r4
    sel = lambda **kw: next(x["minimal_sets"] for x in r4 if all(x.get(k) == v for k, v in kw.items()))
    out["R4_control_vs_reviewer_B_BC"] = {
        "B_claims": {"evil_bytes_S0_S1_S2_one_rebuilder": [["ba", "pipeline"]], "evil_source_S0_REJECTED_not_held": [["pipeline", "va"]],
                     "evil_source_S1": [], "evil_source_S2_REJECTED_not_held": [["pipeline", "va", "va2"]]},
        "this_model": {"evil_bytes_S0": sel(goal="evil_bytes", **{"OP-2": "S0"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True),
                       "evil_bytes_S1": sel(goal="evil_bytes", **{"OP-2": "S1"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True),
                       "evil_source_S0_REJECTED_not_held": sel(goal="evil_source", **{"OP-2": "S0"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=False),
                       "evil_source_S1_REJECTED_not_held": sel(goal="evil_source", **{"OP-2": "S1"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=False),
                       "evil_source_S2_REJECTED_not_held": sel(goal="evil_source", **{"OP-2": "S2"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=False)},
        "note": "B's model contains no input_mirror capability; B's S2 row uses va threshold 2."}
    # ---------------- review-invariant design (CD4-1 literal closure)
    rid = []
    for goal in ("evil_bytes", "evil_source", "evil_toolchain", "evil_mirror"):
        for S in ("S1", "S2"):
            for fetch, vci, rh in itertools.product(("digest", "mirror"), (False, True), (True, False)):
                    opt = dict(goal=goal, S=S, rebuilders=2, ba_thr=2, va_thr=2, inputs_fetch=fetch, verifier_checks_inputs=vci, rejected_held=rh)
                    ms = minimal_sets(r4_like, R4_CAPS, **opt)
                    rid.append({"goal": goal, "OP-2": S, "build_attestation_threshold": 2, "verification_threshold": 2 if S == "S2" else 1,
                                "inputs_fetch": fetch, "verifier_checks_inputs": vci, "REJECTED_held": rh, "minimal_sets": ms,
                                "min_keys": min((len([c for c in s if c not in ("pipeline", "input_mirror")]) for s in ms), default=None)})
    out["RID_review_invariant_design"] = rid
    # ---------------- SAM
    sam_rows = []
    for goal in ("evil_bytes", "evil_source", "evil_toolchain", "evil_mirror"):
        for reg in ("Q1", "Q2"):
            for n_rep in (2, 3):
                for victim in ("bootstrap-P2", "running-P1"):
                    for sub in ("independent", "via_pipeline"):
                        opt = dict(goal=goal, reg=reg, n_rep=n_rep, q=2, victim=victim, submission=sub)
                        caps = [c for c in SAM_CAPS if not (reg == "Q1" and c in ("reg1", "reg2")) and not (reg == "Q2" and c in ("root1", "root2"))
                                and not (n_rep == 2 and c == "rep3")]
                        ms = minimal_sets(sam, caps, **opt)
                        keys = lambda s: [c for c in s if c not in ("pipeline", "transport", "channel", "input_mirror", "toolchain_upstream")]
                        sam_rows.append({"goal": goal, "registration_authority": reg, "reproducers": n_rep, "quorum": 2, "victim": victim,
                                         "reproduction_submission": sub, "minimal_sets": ms,
                                         "min_keys_excluding_TA12_upstream": min((len(keys(s)) for s in ms if "toolchain_upstream" not in s), default=None),
                                         "sets_without_any_key": [s for s in ms if not keys(s)]})
    out["SAM_proposal"] = sam_rows
    # ---------------- summary
    def pick(rows, **kw):
        return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]
    summ = {}
    summ["R4_evil_bytes_S1_digest"] = pick(r4, goal="evil_bytes", **{"OP-2": "S1"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["R4_evil_toolchain_S1_digest_verifier_does_not_check_inputs"] = pick(r4, goal="evil_toolchain", **{"OP-2": "S1"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_bytes_S2_digest"] = pick(rid, goal="evil_bytes", **{"OP-2": "S2"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_mirror_S2_mirror_fetch"] = pick(rid, goal="evil_mirror", **{"OP-2": "S2"}, inputs_fetch="mirror", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_mirror_S2_digest_fetch"] = pick(rid, goal="evil_mirror", **{"OP-2": "S2"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_toolchain_S1_digest_verifier_does_not_check_inputs"] = pick(rid, goal="evil_toolchain", **{"OP-2": "S1"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_toolchain_S2_digest_verifier_does_not_check_inputs"] = pick(rid, goal="evil_toolchain", **{"OP-2": "S2"}, inputs_fetch="digest", verifier_checks_inputs=False, REJECTED_held=True)[0]["minimal_sets"]
    summ["RID_evil_toolchain_S2_digest_verifier_checks_inputs"] = pick(rid, goal="evil_toolchain", **{"OP-2": "S2"}, inputs_fetch="digest", verifier_checks_inputs=True, REJECTED_held=True)[0]["minimal_sets"]
    for goal in ("evil_bytes", "evil_source", "evil_toolchain", "evil_mirror"):
        for victim in ("bootstrap-P2", "running-P1"):
            for sub in ("independent", "via_pipeline"):
                r = pick(sam_rows, goal=goal, registration_authority="Q2", reproducers=3, victim=victim, reproduction_submission=sub)[0]
                summ[f"SAM_Q2_n3_{goal}_{victim}_{sub}"] = r["minimal_sets"]
    summ["SAM_any_row_accepts_with_one_or_zero_keys_excluding_TA12"] = [
        {k: r[k] for k in ("goal", "registration_authority", "reproducers", "victim", "reproduction_submission", "min_keys_excluding_TA12_upstream")}
        for r in sam_rows if r["min_keys_excluding_TA12_upstream"] is not None and r["min_keys_excluding_TA12_upstream"] < 2]
    out["summary"] = summ
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
