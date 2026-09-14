#!/usr/bin/env python3
"""RV5-B-A04 / A06 / A07 — the derivation calculator (FD-3) against revision 5 as written (review r5 reviewer B, AR-0012).

Scratch-free (pure computation). Loads the architect's instruments by path, NOT modified:
  * `evidence/r5/CS5-tcb-capability-sets.py` (module functions `accepted`, `minimal_sets`, `configs`, `expand`);
  * `evidence/r5/P4r5-conformance-oracle.py` (`eligible_release_r5`, `accept_binary`, world constructors) and, through it,
    `evidence/P4r4-trust-state-model.py`.

Part L  (A04) Channel-selected lineage at first admission. CS5's H-CH lets a compromised channel show only a descendant of
        the genuine lineage (`t_x`, needs `ts`). `31` R-ADM-3 makes the typed fingerprint the only selector of the root
        chain, and `gov-admit` has no compiled root (executed in RV5-B-A01). The strategy "the channel shows a lineage the
        attacker generated" is added to CS5's `accepted` by wrapping it (the original function is still called for every
        other strategy), and CS5's `minimal_sets` is re-run for every FA1/FA2 configuration. Variant FA2-q: the quorum is
        read from the Trust Policy the typed fingerprint selects, and the operator types the one value the compromised channel
        instructs (executed in RV5-B-A01 A01c).
Part R  (A07) Restrictor revocation by a stolen trust-state key. When the victim selects the thief's `t_x` (P2 with ch1; FA1
        with ch1; FA2 with ch1+ch2), `t_x` may list honest conflicting reproductions and REJECTED attestations in
        `revocations`, which the predicate then ignores (`25` AP-4, `30` R-REP-6; executed in RV5-B-A01 A03). CS5 models the
        removal of those restrictors only through `transport`. The wrapper grants the effect of withholding in exactly that
        situation; `minimal_sets` re-run for P2/FA1/FA2.
Part P  (A06) Policy-root (T1-E) goal, which CS5 does not compute. An independent enumeration of the revision-5 rules for a
        release carrying malicious non-orderable constitutional content (secret patterns, tool descriptors): registration
        (`30` §5), honest ceremony (R-REG-3), honest final signer (`05` §7 rule 2, R-REL-6), honest publisher (R-PUB-1:
        registrations need only first-hand receipt), E7 as written (`19` §6, `23` §12.3: no verification-record condition),
        anchoring and currency (`24` §4.3–§4.4). Victims: use (C1–C2) of a Git-delivered release on an anchored or pinned
        machine; ingress (C3) with a P1 proof; ingress with a P2 typed fingerprint. Variant E7+V: E7 also requires OP-8
        ACCEPTED verification records listed by the registration (the correction). Plus computed rows with the architect's
        P4r5 `eligible_release_r5` / `accept_binary`.
Part I  (A08) Build-image selector (G_IMAGE), which CS5 does not model: the image digest is checked by the ceremony against
        "the owner's image record" (`30` R-REG-3 (c)); no rule names who produces that record, and verifiers check
        toolchain archives against upstream checksums only (R-VER-1). Executed mechanism: RV5-B-A08.
Part C  Victim classes CS5 enumerates.

Output: JSON on stdout. Deterministic.
"""
import copy, importlib.util, itertools, json, os, sys
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
R5 = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5")


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


cs5 = load("cs5", os.path.join(R5, "CS5-tcb-capability-sets.py"))
ORIG_ACCEPTED = cs5.accepted
COMMITTED = json.load(open(os.path.join(R5, "CS5-tcb-capability-sets.json")))


# ================================================================================================ part L and part R wrappers
def wrapped_accepted(goal, caps, cfg):
    C = cs5.expand(caps)
    v = cfg["victim"]
    mode = cfg.get("rv5b_mode")
    if mode == "lineage" and v in ("FA1", "FA2"):
        need = {"ch1"} if (v == "FA1" or cfg.get("rv5b_fa2_quorum_from_selected_state")) else {"ch1", "ch2"}
        if need <= C:
            return True
    if mode == "restrictor_revocation" and "ts" in C and "transport" not in C:
        selects_tx = (v in ("P2", "FA1") and "ch1" in C) or (v == "FA2" and {"ch1", "ch2"} <= C)
        if selects_tx:
            return ORIG_ACCEPTED(goal, list(caps) + ["transport"], cfg)
    return ORIG_ACCEPTED(goal, caps, cfg)


cs5.accepted = wrapped_accepted


def run_one(args):
    goal, cfg = args
    r = cs5.minimal_sets(goal, cfg)
    return goal, cfg, r["minimal_sets"], r["monotonicity_violations"]


def key_of(goal, c):
    return f"{goal}|OP-2={c['reg']}|OP-8={c['V']}|OP-9={c['repro']}|OP-10={c['toolchain']}|{c['victim']}"


def part_L_R():
    main_cfgs, _ = cs5.configs()
    jobs = []
    for goal, cfg in main_cfgs:
        if cfg["victim"] in ("FA1", "FA2") and goal != "G_TOOLCHAIN":
            jobs.append((goal, dict(cfg, rv5b_mode="lineage")))
            if cfg["victim"] == "FA2":
                jobs.append((goal, dict(cfg, rv5b_mode="lineage", rv5b_fa2_quorum_from_selected_state=True)))
        if cfg["victim"] in ("P2", "FA1", "FA2") and goal in ("G_BYTES", "G_SRC", "G_INPUTS"):
            jobs.append((goal, dict(cfg, rv5b_mode="restrictor_revocation")))
    with ProcessPoolExecutor(max_workers=12) as ex:
        res = list(ex.map(run_one, jobs, chunksize=4))
    L_rows, R_rows = {}, {}
    mono = 0
    for goal, cfg, sets, mv in res:
        mono += mv
        k = key_of(goal, cfg)
        committed = COMMITTED["minimal_sets_table"][k]
        disp = [" + ".join(s) for s in sets]
        if cfg["rv5b_mode"] == "lineage":
            kk = k + ("|quorum-from-selected-state" if cfg.get("rv5b_fa2_quorum_from_selected_state") else "")
            L_rows[kk] = {"committed": committed, "with_channel_selected_lineage": disp}
        else:
            R_rows[k] = {"committed": committed, "with_tss_revocation_of_restrictors": disp,
                         "sets_that_lose_transport": sorted({c for c in committed if "transport" in c.split(" + ")} - set(disp))}
    L_summary = {
        "configurations": len(L_rows),
        "FA1_minimum_is_ch1_alone": sum(1 for k, v in L_rows.items() if k.endswith("|FA1") and ["ch1"] == [s for s in v["with_channel_selected_lineage"] if "rp" not in s and "insider" not in s and "cust" not in s and "vp" not in s and "pipeline" not in s and "mirror" not in s][:1]),
        "FA1_configurations": sum(1 for k in L_rows if k.endswith("|FA1")),
        "FA2_two_typed_minimum_is_ch1_ch2": sum(1 for k, v in L_rows.items() if k.endswith("|FA2") and "ch1 + ch2" in v["with_channel_selected_lineage"]),
        "FA2_two_typed_configurations": sum(1 for k in L_rows if k.endswith("|FA2")),
        "FA2_quorum_from_selected_state_minimum_is_ch1": sum(1 for k, v in L_rows.items() if k.endswith("quorum-from-selected-state") and "ch1" in v["with_channel_selected_lineage"]),
        "committed_FA_sets_containing_a_key_atom_that_the_channel_alone_supersedes": sum(1 for k, v in L_rows.items() for s in v["committed"] if "ch1" in s.split(" + ") and len(s.split(" + ")) > (1 if k.endswith("|FA1") or k.endswith("quorum-from-selected-state") else 2)),
    }
    R_summary = {"configurations": len(R_rows), "configurations_where_a_committed_set_needed_transport_and_no_longer_does": sum(1 for v in R_rows.values() if v["sets_that_lose_transport"])}
    return {"L_summary": L_summary, "L_examples": {k: L_rows[k] for k in sorted(L_rows) if "OP-8=2|OP-9=d_n3q3" in k or "OP-8=1|OP-9=n2q2" in k and "OP-2=root" in k},
            "R_summary": R_summary, "R_examples": {k: R_rows[k] for k in sorted(R_rows) if "OP-2=root|OP-8=1|OP-9=n2q2" in k or "OP-2=delegated|OP-8=2|OP-9=n3q2" in k},
            "monotonicity_violations": mono}


# ================================================================================================ part P: policy-root goal
P_ATOMS = ["insider", "pipeline", "vp1", "vp2", "va1", "va2", "rf", "cust1", "cust2", "regk1", "regk2", "ts", "ch1", "repo"]
P_IMPLIES = {"vp1": ("va1",), "vp2": ("va2",), "cust1": ("regk1",), "cust2": ("regk2",)}


def p_accepted(C, cfg):
    V, victim, e7v = cfg["V"], cfg["victim"], cfg["e7_checks_verification"]
    vers = range(1, V + 1)
    if "repo" not in C:                          # the release reaches the victim by Git (use) or by the bundle the victim applies
        return False
    insider = "insider" in C
    all_ver_accept = insider or all(f"vp{i}" in C or f"va{i}" in C for i in vers)          # ACCEPTED statements exist for the malicious candidate
    all_ver_firsthand = insider or all(f"vp{i}" in C for i in vers)                        # first-hand ACCEPTED records (process compromise)
    proposes = insider or "pipeline" in C
    final_ok = "rf" in C or (proposes and all_ver_accept)                                    # honest promoter signs with ACCEPTED attestations present
    routes = []
    if proposes and all_ver_firsthand:
        routes.append("honest-ceremony")                                                    # R-REG-3 (d) satisfied first-hand
    if {"regk1", "regk2", "cust1", "cust2"} <= C:
        routes.append("custodians")
    if {"regk1", "regk2"} <= C:
        routes.append("keys")
    for route in routes:
        first_hand = route in ("honest-ceremony", "custodians")
        published_by_owner = first_hand                                                    # R-PUB-1: first-hand registrations are referenced
        if not final_ok:
            continue
        if e7v and not all_ver_accept:
            continue
        if victim == "use_anchored":                                                       # C1–C2: any admissible descendant is effective
            if published_by_owner or "ts" in C:
                return True
        elif victim == "ingress_P1":                                                       # C3 needs a proof naming the TSS used
            if published_by_owner:
                return True
        elif victim == "ingress_P2":
            if published_by_owner or ("ts" in C and "ch1" in C):
                return True
    return False


def p_minimal(cfg):
    atoms = P_ATOMS
    found = []
    for size in range(0, len(atoms) + 1):
        for combo in itertools.combinations(atoms, size):
            C = set(combo)
            for a in combo:
                C.update(P_IMPLIES.get(a, ()))
            if any(f <= C for f in found):
                continue
            if p_accepted(C, cfg):
                found.append(frozenset(combo))
    disp = []
    for f in found:
        implied = {b for a in f for b in P_IMPLIES.get(a, ())}
        disp.append(sorted(a for a in f if a not in implied))
    return sorted(set(tuple(x) for x in disp), key=lambda s: (len(s), s))


def part_P():
    rows = {}
    for reg in ("root", "delegated"):
        for V in (1, 2):
            for victim in ("use_anchored", "ingress_P1", "ingress_P2"):
                for e7v in (False, True):
                    cfg = {"reg": reg, "V": V, "victim": victim, "e7_checks_verification": e7v}
                    sets = [list(s) for s in p_minimal(cfg)]
                    ver = lambda s: len({a[-1] for a in s if a.startswith(("va", "vp"))})
                    no_ver = [s for s in sets if "insider" not in s and ver(s) < V]
                    rf_sets = [s for s in sets if "rf" in s]
                    rows[f"G_POLICY|OP-2={reg}|OP-8={V}|{victim}|E7={'as-written' if not e7v else 'with-verification-records'}"] = {
                        "minimal_sets": [" + ".join(s) for s in sets],
                        "sets_with_fewer_than_OP8_verification_compromises (declared: `21` OP-2 (b) and `05` §1 'accepted only with OP-8 verification statements')": [" + ".join(s) for s in no_ver],
                        "sets_containing_release_final (declared INV-RF: in no minimal set)": [" + ".join(s) for s in rf_sets],
                        "labels": {"cust1+cust2 / regk1+regk2": "root threshold (A8)" if reg == "root" else "delegated registration quorum"},
                    }
    return rows


def part_P_computed():
    """The architect's P4r5 functions, unmodified: a registration with no verification record and a release-final signature,
    referenced by a trust-state thief's descendant t12x of the anchored t11."""
    p5 = load("p4r5", os.path.join(R5, "P4r5-conformance-oracle.py"))
    m = p5.m
    units = {"leaf:SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex": "sha256:weak"}
    F12 = dict(m.release("F12", 12, promoted_from="C12", refs=(11, 2, 1)), release_id="4.1.12", units=units)
    G12 = p5.rrs("g12", "4.1.12", 12, "F12", "C12", vrecs=(), units=units)
    T12x = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g12"], issued_at=m.NOW - 60)
    W = p5.W11 + [F12, G12, T12x]
    out = {}
    for label, mach, op7 in (("human anchor at t11 (today)", p5.anchored(11, "t11", 0), "a"), ("human anchor at t11 (40 days)", p5.anchored(11, "t11", 40), "a"),
                             ("pin at t11 provisioned 1 day ago", {"pins": [m.pin(11, "t11", 1)]}, "a"), ("unanchored CI runner, OP-7 (d)", {}, "d")):
        K, ts, fr, _ = m.evaluate_machine(W, mach, m.NOW, op7)
        el = p5.eligible_release_r5(F12, W, mach, m.NOW, op7)
        out[label] = {"effective_tss": (ts.get("eff") or {}).get("d"), "allowed_classes": fr["allowed"], "currency_axis": fr["axis"][:120],
                      "eligible_release_r5(F12)": el, "C3_currency_covers_t12x": p5.currency_covers_effective(ts, fr, mach, m.NOW)}
    B12 = p5.binary("B12", "4.1.12", m.tbm("tbm-f12", 2, "TPS2", 11, "t11", "F12"))
    RP12 = [p5.repro("rp12a", "4.1.12", "B12", "tbm-f12", signers=("p1",)), p5.repro("rp12b", "4.1.12", "B12", "tbm-f12", signers=("p2",))]
    T12xb = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11", "g12", "B12"], issued_at=m.NOW - 60)
    Wb = p5.W11 + [F12, G12, T12xb] + RP12
    out["control: a binary of the same registration (accept_binary, in-gate fingerprint naming t12x)"] = p5.accept_binary(B12, Wb, p5.anchored(11, "t11", 0), m.NOW, "a", gate_fingerprint=(12, "t12x"))
    return out


# ================================================================================================ part I: build-image selector
I_ATOMS = ["pipeline", "image_up", "cust1", "cust2", "va1", "vp1", "rp1", "rp2", "rp3", "rep1", "rep2", "rep3", "ts", "ch1", "transport"]


def i_accepted(C, cfg):
    rec = cfg["image_record"]
    image_evil = (rec == "produced_by_release_pipeline" and "pipeline" in C) or (rec == "owner_built_from_upstream_images_or_packages" and "image_up" in C)
    if rec == "registered_input_reproduced_from_pinned_upstream_digests":
        image_evil = False                     # correction variant: the image is itself a digest-pinned, independently reproduced input
    if not image_evil:
        return False
    # every honest reproducer (including an OP-10 (b) diverse reproducer, which must match bit-for-bit) builds with the registered
    # image: identical malicious bytes, quorum met, no conflict; the honest publisher publishes; every victim accepts.
    return True


def part_I():
    rows = {}
    for rec in ("produced_by_release_pipeline", "owner_built_from_upstream_images_or_packages", "registered_input_reproduced_from_pinned_upstream_digests"):
        for victim in ("P1", "P2", "FA1"):
            found = []
            for size in range(0, 4):
                for combo in itertools.combinations(I_ATOMS, size):
                    C = set(combo)
                    if any(f <= C for f in found):
                        continue
                    if i_accepted(C, {"image_record": rec, "victim": victim}):
                        found.append(frozenset(combo))
            rows[f"G_IMAGE|image_record={rec}|{victim}|any OP-2, OP-8, OP-9, OP-10"] = [" + ".join(sorted(f)) for f in found]
    rows["CS5 atoms and goals containing an image atom"] = sorted({a for g in cs5.GOAL_ATOMS.values() for a in g if "image" in a})
    return rows


def main():
    LR = part_L_R()
    main_cfgs, _ = cs5.configs()
    out = {
        "probe": "RV5-B-A04/A06/A07/A08 calculator extensions (AR-0012)",
        "instruments": {"CS5": "evidence/r5/CS5-tcb-capability-sets.py (unmodified; `accepted` wrapped, original called)", "P4r5": "evidence/r5/P4r5-conformance-oracle.py (unmodified)"},
        "part_L_channel_selected_lineage": {k: LR[k] for k in ("L_summary", "L_examples")},
        "part_R_restrictor_revocation_by_trust_state_key": {k: LR[k] for k in ("R_summary", "R_examples")},
        "monotonicity_violations_in_rerun": LR["monotonicity_violations"],
        "part_P_policy_root_goal": part_P(),
        "part_P_computed_with_P4r5": part_P_computed(),
        "part_I_build_image_selector": part_I(),
        "part_C_victim_classes_in_CS5": sorted({c["victim"] for _, c in main_cfgs}),
    }
    print(json.dumps(out, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
