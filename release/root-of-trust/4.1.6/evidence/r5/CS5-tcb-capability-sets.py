#!/usr/bin/env python3
"""CS5 — derivation calculator for the revision-5 TCB decision (BC4-1 / RV4-H1; `25` §3–§7, `29` §4).

RoT-1 revision 5, PROPOSED architecture instrument. Not the implementation; decides nothing.

What it computes. For every owner answer set of OP-2 (registration authority), OP-8 (independent verification records),
OP-9 (reproducer set) and OP-10 (common-mode toolchain), every victim class, and every attack goal, the MINIMAL capability
sets that yield an accepted malicious production binary. Enumeration is exhaustive over subsets of the goal's atoms, in
increasing size, with superset pruning, up to MAX_SIZE; the simulation is checked monotone on every enumerated subset pair
it prunes (see `monotonicity`). Pipeline input is an atom on every route (review r4 CD4-1 (3)).

Why a model at all. Revision 4 argued its minimum capability sets by hand ("route B needs 4 keys over 3 purposes"); the
review found {one build-attestation key, pipeline} by enumeration. Revision 5 makes the enumeration the source of every
minimum-set statement in `25` §7, `05` §3 and `21` (rule FD-3 of `29`). Owners re-run it for their real process.

Attribution. Method: review r4 reviewer B `RV4-B-M-reference-model.py` section BC (capability subsets with honest actors
acting only on stated checks); specialist A `E2-tcb-capability-sets.py` (build inputs, mirror, toolchain, submission route);
specialist B `F1-tcb-fact-derivation.py` (first-hand establishers, verification-process compromise). No code is copied;
the rules below are revision 5.

HONEST-PARTY RULES ENCODED (each is a normative rule of the pack; the atom that breaks it is named):
  H-PIPE  The release pipeline proposes the candidate source identity and build-input manifest to verification and to the
          registration ceremony. Honest: the genuine (S_good, I_good). `pipeline`: any proposal; with the via_pipeline
          control it also carries reproductions to the publisher. `insider`: the honest pipeline proposes S_ins, a
          malicious change honest verification accepts (route I, TB-4).
  H-VER   Verifier i reproduces the candidate from the proposed source and inputs, checks the input manifest against the
          upstream release's signed checksums (R-REG-3 (a)), and returns its record FIRST-HAND to the ceremony (not via the
          pipeline) and signs a verification attestation: ACCEPTED iff S in {S_good, S_ins} and I = I_good, else REJECTED.
          `vp_i` (process compromise): ACCEPTED record and statement for anything. `va_i` (key theft only): signed statements
          for anything, no first-hand record.
  H-REG   Registration custodians sign a Release Registration Statement (RRS) for a proposal only with all OP-8 first-hand
          ACCEPTED records, no REJECTED record, and inputs whose toolchain digests match upstream signed checksums; they
          deliver it first-hand to reproducers and the trust-state publisher. Under OP-9 (d) they also reproduce the binary
          themselves and name its digest. `cust1`+`cust2` (custodian compromise at the threshold of 2): a ceremony with any
          content. `regk1`+`regk2` (key theft at threshold): a signed RRS with any content, never first-hand. Under OP-2 (a)
          the custodians are the root custodians, so `cust1`+`cust2` is root threshold compromise (A8, outside TA-4).
  H-REP   Reproducer j fetches every input BY DIGEST from the registered manifest (R-REP-2), builds, and confirms its own
          digest FIRST-HAND to the publisher (R-REP-3) and signs a one-signature reproduction statement. Toolchain effect:
          `toolchain_up` makes the upstream toolchain release malicious (TA-12); under OP-10 (b) reproducer 1 uses a diversely
          bootstrapped compiler (`diverse_tc` compromises it); under OP-10 (c) every reproducer uses the owner-built
          toolchain (`owner_tc` compromises it). `rp_j` (process): confirms and signs any digest. `rep_j` (key): signs any
          digest, no first-hand confirmation. Honest reproducers reproduce only first-hand registrations.
  H-PUB   The trust-state publisher references a first-hand RRS and a binary digest only if: OP-8 ACCEPTED verification
          statements by distinct keys exist and no REJECTED is visible; at least q distinct reproducers confirmed that
          digest first-hand; no reproducer confirmed another digest (conflict refuses); under (d) the digest equals the RRS
          digest. It publishes the state fingerprint in the independent channels. `ts` (key theft): signs a Trust State
          Statement t_x descending from the newest honest one and referencing anything.
  H-CH    Channel k shows the fingerprint of the newest honest TSS; `ch_k` shows t_x's.
  VICTIM  Runs admission-predicate/1 (`25` §5): P1 = running binary anchored at the pre-release TSS with a P1 currency
          proof (a trust-state thief's descendant t_x is effective); P2 = running binary with an in-gate typed fingerprint
          from channel 1; FA1 = first admission typing one channel (OP-13 (a)); FA2 = first admission requiring two agreeing
          channels (OP-13 (b)). Registration referenced by the selected TSS; OP-8 ACCEPTED statements by distinct keys; no
          visible REJECTED; >= q distinct reproducer keys on the measured digest; no visible conflicting reproduction; digest
          published; under (d) digest = RRS digest. The attacker delivers any statement it holds (A5 delivery is free);
          withholding honest statements needs `transport`.
GOALS  G_SRC malicious source faithfully built; G_INPUTS malicious toolchain named in the registration; G_BYTES malicious
       bytes for a genuine registration; G_MIRROR bytes from a poisoned input mirror; G_TOOLCHAIN common-mode compromised
       upstream toolchain.
Output: JSON on stdout. Deterministic. No files, no subprocesses.
"""
import itertools, json, sys
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True
MAX_SIZE = 10

IMPLIES = {"vp1": ("va1",), "vp2": ("va2",), "rp1": ("rep1",), "rp2": ("rep2",), "rp3": ("rep3",), "cust1": ("regk1",), "cust2": ("regk2",)}
KEY_ATOMS = {"va1", "va2", "rep1", "rep2", "rep3", "regk1", "regk2", "ts", "rf", "rc"}
PROCESS_ATOMS = {"vp1", "vp2", "rp1", "rp2", "rp3", "cust1", "cust2"}
INFRA_ATOMS = {"pipeline", "transport", "mirror", "ch1", "ch2"}
RESIDUAL_ATOMS = {"insider": "TB-4 (route I: insider change accepted by honest verification)", "toolchain_up": "TA-12 / TB-S2 (compromised upstream toolchain release)",
                  "diverse_tc": "OP-10 (b) diverse bootstrap compromised", "owner_tc": "OP-10 (c) owner-built toolchain compromised"}

REPRO = {"n2q2": (2, 2, False), "n3q2": (3, 2, False), "n3q3": (3, 3, False), "d_n2q2": (2, 2, True), "d_n3q2": (3, 2, True), "d_n3q3": (3, 3, True)}


def expand(caps):
    out = set(caps)
    for a in caps:
        out.update(IMPLIES.get(a, ()))
    return out


def tc_effect(C, cfg, j):
    """Toolchain outcome for honest reproducer j (1-based); j = 0 means the registration custodians under OP-9 (d)."""
    mode = cfg["toolchain"]
    if mode == "owner_built":
        return "evil" if "owner_tc" in C else "good"
    if mode == "diverse" and j == 1:
        return "evil" if "diverse_tc" in C else "good"
    return "evil" if "toolchain_up" in C else "good"


def build(src, inp, tc, fetch_mirror=False, C=()):
    if fetch_mirror and "mirror" in C:
        return f"B({src},{inp},mirror)"
    return f"B({src},{inp},{tc})"


def goal_contents(goal, C):
    if goal == "G_SRC":
        return [("S_evil", "I_good")] + ([("S_ins", "I_good")] if "insider" in C else [])
    if goal == "G_INPUTS":
        return [("S_good", "I_evil")]
    return [("S_good", "I_good")]


def is_malicious(goal, content, X):
    s, i = content
    if goal in ("G_SRC",):
        return s in ("S_evil", "S_ins")
    if goal == "G_INPUTS":
        return i == "I_evil"
    if goal == "G_BYTES":
        return X == "B_evil"
    if goal == "G_MIRROR":
        return X.endswith(",mirror)")
    if goal == "G_TOOLCHAIN":
        return X.endswith(",evil)")
    return False


def accepted(goal, caps, cfg):
    """True iff some attacker strategy using only `caps` yields a victim ACCEPTED on a malicious binary."""
    C = expand(caps)
    V = cfg["V"]
    n, q, d_mode = REPRO[cfg["repro"]]
    passthrough = cfg.get("passthrough", False)
    via_pipeline = cfg.get("submission") == "via_pipeline"
    fetch_mirror = cfg.get("fetch") == "mirror"
    victim = cfg["victim"]
    honest_prop = ("S_ins", "I_good") if "insider" in C else ("S_good", "I_good")
    reps = range(1, n + 1)
    vers = range(1, V + 1)

    def honest_verdict(content):
        s, i = content
        return "ACCEPTED" if s in ("S_good", "S_ins") and i == "I_good" else "REJECTED"

    for content in goal_contents(goal, C):
        acceptable = honest_verdict(content) == "ACCEPTED"
        for route in ("honest", "cust", "key"):
            if route == "cust" and not {"cust1", "cust2"} <= C:
                continue
            if route == "key" and not {"regk1", "regk2"} <= C:
                continue
            if route == "honest" and content != honest_prop and "pipeline" not in C:
                continue
            # which verification statements exist, and whether honest verifiers produced REJECTED for this content
            routed_to_honest = route == "honest"
            honest_acc = acceptable and (routed_to_honest or content == ("S_good", "I_good"))  # the genuine release was verified anyway
            rejected_exists = routed_to_honest and not acceptable and any(f"vp{i}" not in C for i in vers)
            acc_keys = {i for i in vers if (honest_acc and f"vp{i}" not in C) or f"va{i}" in C}
            # the honest ceremony needs every first-hand record ACCEPTED and genuine upstream inputs
            if route == "honest":
                if content[1] != "I_good":
                    continue
                if not all(f"vp{i}" in C or acceptable for i in vers):
                    continue
            first_hand = route in ("honest", "cust")
            # registered binary digest under OP-9 (d)
            custodian_digest = None
            for X_choice in candidate_binaries(goal, content, C, cfg, fetch_mirror):
                if d_mode:
                    if route == "honest":
                        custodian_digest = ("PIPE:" + X_choice) if (passthrough and "pipeline" in C) else build(content[0], content[1], tc_effect(C, cfg, 0), fetch_mirror, C)
                        if passthrough and "pipeline" not in C:
                            custodian_digest = build(content[0], content[1], tc_effect(C, cfg, 0), fetch_mirror, C)
                        reg_digest = custodian_digest.replace("PIPE:", "")
                    else:
                        reg_digest = X_choice
                else:
                    reg_digest = None
                X = X_choice
                if not is_malicious(goal, content, X):
                    continue
                # reproductions: honest reproducers reproduce first-hand registrations only
                honest_digests = {j: build(content[0], content[1], tc_effect(C, cfg, j), fetch_mirror, C) for j in reps if f"rp{j}" not in C} if first_hand else {}
                attacker_signed = {j for j in reps if f"rep{j}" in C}           # rp_j implies rep_j
                attacker_confirm = {j for j in reps if f"rp{j}" in C}
                # -------- publication by the honest publisher (first-hand registrations only)
                published_by_owner = False
                if first_hand and len(acc_keys) >= V and not (rejected_exists and True):
                    confirmations = {}
                    if via_pipeline and "pipeline" in C:
                        for j in attacker_signed:                      # the pipeline injects signed confirmations and suppresses honest ones
                            confirmations[j] = X
                    else:
                        for j, dg in honest_digests.items():
                            confirmations[j] = dg
                        for j in attacker_confirm:
                            confirmations[j] = X
                    vals = set(confirmations.values())
                    if vals == {X} and len(confirmations) >= q and (reg_digest is None or reg_digest == X):
                        published_by_owner = True
                # -------- trust-state selection by the victim
                honest_fp_names_release = published_by_owner
                sel = None
                if victim == "P1":
                    # revision 5 (24 §4.4, CR4-B-07 option 1): a pin or confirmation proves currency only for the TSS it
                    # names; C3 on a descendant issued after the proof needs P2 or P3, so a trust-state thief's t_x never
                    # carries C3 on a pinned machine. The pin names the honest TSS that published the binary.
                    sel = "th" if published_by_owner else None
                elif victim == "P1_relaxed_control":
                    sel = "tx" if "ts" in C else ("th" if published_by_owner else None)
                elif victim in ("P2", "FA1"):
                    sel = "tx" if ("ch1" in C and "ts" in C) else ("th" if honest_fp_names_release else None)
                elif victim == "FA2":
                    # two channels must agree (OP-13 (b)); a single compromised channel showing t_x only yields
                    # CHANNEL_DISAGREEMENT, so the attacker gains nothing from using it alone
                    if "ch1" in C and "ch2" in C and "ts" in C:
                        sel = "tx"
                    else:
                        sel = "th" if honest_fp_names_release else None
                if sel is None:
                    continue
                # an honest TSS selected by a typed fingerprint must be held: withholding it needs transport, which the
                # attacker never uses against itself here; t_x is always deliverable.
                withhold = "transport" in C
                # -------- admission predicate at the victim
                if len(acc_keys) < V:
                    continue
                if rejected_exists and not withhold:
                    continue
                if reg_digest is not None and reg_digest != X:
                    continue
                # control only: reproductions that travel through a compromised pipeline are suppressed before publication
                visible_honest = {} if (via_pipeline and "pipeline" in C) else honest_digests
                vis_counts = set(attacker_signed) | ({j for j, dg in visible_honest.items() if dg == X})
                if len(vis_counts) < q:
                    continue
                conflicting = any(dg != X for dg in visible_honest.values())
                if conflicting and not withhold:
                    continue
                return True
    return False


def candidate_binaries(goal, content, C, cfg, fetch_mirror):
    if goal == "G_BYTES":
        return ["B_evil"]
    if goal == "G_MIRROR":
        return [build(content[0], content[1], "good", True, C | {"mirror"})]
    if goal == "G_TOOLCHAIN":
        return [build(content[0], content[1], "evil")]
    return [build(content[0], content[1], "good")]


GOAL_ATOMS = {
    "G_SRC": ["insider", "pipeline", "ts", "transport", "rf", "rc", "cust1", "cust2", "regk1", "regk2"],
    "G_INPUTS": ["pipeline", "ts", "transport", "cust1", "cust2", "regk1", "regk2"],
    "G_BYTES": ["pipeline", "ts", "transport", "cust1", "cust2", "regk1", "regk2"],
    "G_MIRROR": ["mirror", "pipeline", "ts", "transport"],
    "G_TOOLCHAIN": ["toolchain_up", "ts", "transport"],
}


def atoms_for(goal, cfg):
    n, q, d = REPRO[cfg["repro"]]
    a = list(GOAL_ATOMS[goal])
    if goal in ("G_SRC", "G_INPUTS", "G_BYTES"):
        a += [f"vp{i}" for i in range(1, cfg["V"] + 1)] + [f"va{i}" for i in range(1, cfg["V"] + 1)]
    a += [f"rp{j}" for j in range(1, n + 1)] + [f"rep{j}" for j in range(1, n + 1)]
    if goal == "G_TOOLCHAIN":
        if cfg["toolchain"] == "diverse":
            a.append("diverse_tc")
        if cfg["toolchain"] == "owner_built":
            a.append("owner_tc")
    if cfg["victim"] in ("P2", "FA1"):
        a.append("ch1")
    if cfg["victim"] == "FA2":
        a += ["ch1", "ch2"]
    return a


def closure_mask(atoms):
    idx = {a: i for i, a in enumerate(atoms)}
    imp = []
    for a in atoms:
        m = 1 << idx[a]
        for b in IMPLIES.get(a, ()):
            if b in idx:
                m |= 1 << idx[b]
        imp.append(m)
    return idx, imp


def minimal_sets(goal, cfg):
    atoms = atoms_for(goal, cfg)
    idx, imp = closure_mask(atoms)
    found, checked, mono_viol = [], 0, 0
    for size in range(0, min(MAX_SIZE, len(atoms)) + 1):
        for combo in itertools.combinations(range(len(atoms)), size):
            m = 0
            for i in combo:
                m |= imp[i]
            if any((m & f) == f for f in found):
                # pruned superset: monotonicity spot check on the first pruned sets of each size
                if checked < 400:
                    checked += 1
                    if not accepted(goal, [atoms[i] for i in range(len(atoms)) if m >> i & 1], cfg):
                        mono_viol += 1
                continue
            caps = [atoms[i] for i in range(len(atoms)) if m >> i & 1]
            if accepted(goal, caps, cfg):
                # keep only closure-minimal representatives
                if not any((m & f) == f for f in found):
                    found = [f for f in found if (f & m) != m] + [m]
    sets = sorted((sorted(atoms[i] for i in range(len(atoms)) if f >> i & 1) for f in found), key=lambda s: (len(s), s))
    # remove implied atoms from the display (rp1 implies rep1, etc.)
    disp = []
    for s in sets:
        implied = {b for a in s for b in IMPLIES.get(a, ())}
        disp.append([a for a in s if a not in implied])
    uniq = []
    for s in sorted(disp, key=lambda s: (len(s), s)):
        if s not in uniq:
            uniq.append(s)
    return {"atoms": atoms, "minimal_sets": uniq, "monotonicity_spot_checks": checked, "monotonicity_violations": mono_viol,
            "complete_up_to_size": min(MAX_SIZE, len(atoms))}


def classify(s, cfg):
    tags = []
    ss = set(s)
    for a, t in RESIDUAL_ATOMS.items():
        if a in ss:
            tags.append(t)
    if {"cust1", "cust2"} <= ss:
        tags.append("A8 root threshold compromise (OP-2 (a): outside TA-4)" if cfg["reg"] == "root" else "delegated registration quorum compromise (OP-2 (b) consequence)")
    if {"regk1", "regk2"} <= ss:
        tags.append("root threshold keys (OP-2 (a): A8)" if cfg["reg"] == "root" else "delegated registration keys at threshold (OP-2 (b))")
    if any(a.startswith("vp") for a in ss):
        tags.append("verification-process compromise (TA-11; TB-4')")
    if any(a.startswith("rp") for a in ss):
        tags.append("reproducer-process compromise (TB-S1)")
    return tags


def invariants(goal, cfg, sets):
    n, q, d = REPRO[cfg["repro"]]
    V = cfg["V"]
    out = {}
    def repro_count(s):
        return len({a[-1] for a in s if a.startswith("rep") or a.startswith("rp")})
    def ver_count(s):
        return len({a[-1] for a in s if a.startswith("va") or a.startswith("vp")})
    reg_pair = lambda s: {"cust1", "cust2"} <= set(s) or {"regk1", "regk2"} <= set(s)
    residual = lambda s: any(a in RESIDUAL_ATOMS for a in s)
    if goal == "G_BYTES":
        bad = [s for s in sets if repro_count(s) < q]
        out["INV-BYTES every minimal set contains >= q reproducer compromises"] = {"holds": not bad, "counterexamples": bad}
        if d:
            bad2 = [s for s in sets if not reg_pair(s)]
            out["INV-BYTES-d every minimal set also contains the registration threshold"] = {"holds": not bad2, "counterexamples": bad2}
    if goal == "G_SRC":
        bad = [s for s in sets if not residual(s) and not (ver_count(s) >= V and (reg_pair(s) or "pipeline" in s))]
        out["INV-SRC every non-residual minimal set contains >= OP-8 verification compromises and (the registration threshold or pipeline input)"] = {"holds": not bad, "counterexamples": bad}
        keyonly = [s for s in sets if not residual(s) and not any(a in PROCESS_ATOMS for a in s)]
        bad3 = [s for s in keyonly if not reg_pair(s)]
        out["INV-SRC-KEYS every key-theft-only minimal set contains the registration threshold keys"] = {"holds": not bad3, "counterexamples": bad3}
    if goal == "G_INPUTS":
        bad = [s for s in sets if not (reg_pair(s) and ver_count(s) >= V)]
        out["INV-INPUTS every minimal set contains the registration threshold and >= OP-8 verification compromises"] = {"holds": not bad, "counterexamples": bad}
    if goal == "G_MIRROR" and cfg.get("fetch") != "mirror":
        bad = [s for s in sets if "mirror" in s or repro_count(s) < q]
        out["INV-MIRROR inputs fetched by digest: the mirror appears in no minimal set, and every minimal set contains >= q reproducer compromises"] = {"holds": not bad, "counterexamples": bad}
    one_key = [s for s in sets if not residual(s) and not any(a in PROCESS_ATOMS for a in s) and len([a for a in s if a in KEY_ATOMS]) <= 1]
    out["INV-ONE no key-theft-only minimal set with at most one key (residual atoms excepted)"] = {"holds": not one_key, "counterexamples": one_key}
    single_process = [s for s in sets if not residual(s) and len([a for a in s if a in PROCESS_ATOMS or a in KEY_ATOMS]) == 1]
    out["REPORT sets whose only compromise is one process (owner-option consequence, not a key route)"] = {"holds": True, "sets": single_process}
    rfrc = [s for s in sets if "rf" in s or "rc" in s]
    out["INV-RF release-final and release-candidate keys appear in no minimal set"] = {"holds": not rfrc, "counterexamples": rfrc}
    return out


def run_cfg(args):
    goal, cfg = args
    r = minimal_sets(goal, cfg)
    r["classified"] = [{"set": s, "size": len(s), "labels": classify(s, cfg)} for s in r["minimal_sets"]]
    r["invariants"] = invariants(goal, cfg, r["minimal_sets"])
    keyonly = [s for s in r["minimal_sets"] if not any(a in PROCESS_ATOMS or a in RESIDUAL_ATOMS or a == "insider" for a in s)]
    r["smallest_key_theft_and_infrastructure_sets"] = [s for s in keyonly if len(s) == min((len(x) for x in keyonly), default=0)]
    return {"goal": goal, "config": cfg, **r}


def configs():
    main = []
    for reg in ("root", "delegated"):
        for V in (1, 2):
            for repro in ("n2q2", "n3q2", "n3q3", "d_n2q2", "d_n3q2", "d_n3q3"):
                for victim in ("P1", "P2", "FA1", "FA2"):
                    base = {"reg": reg, "V": V, "repro": repro, "toolchain": "accept", "victim": victim, "submission": "first_hand", "fetch": "digest"}
                    for goal in ("G_SRC", "G_INPUTS", "G_BYTES", "G_MIRROR"):
                        main.append((goal, dict(base)))
    for tc in ("accept", "diverse", "owner_built"):
        for repro in ("n2q2", "n3q2", "n3q3", "d_n2q2"):
            for victim in ("P1", "FA2"):
                main.append(("G_TOOLCHAIN", {"reg": "root", "V": 1, "repro": repro, "toolchain": tc, "victim": victim, "submission": "first_hand", "fetch": "digest"}))
    controls = []
    for repro in ("n2q2", "n3q2"):
        controls.append(("G_BYTES", {"reg": "root", "V": 1, "repro": repro, "toolchain": "accept", "victim": "P1_relaxed_control", "submission": "first_hand", "fetch": "digest",
                                     "control": "CR4-B-07 option 2 (relaxed P1 meaning): a P1 proof on the anchored TSS carries C3 to a later descendant"}))
    for victim in ("P1", "FA2"):
        controls.append(("G_BYTES", {"reg": "root", "V": 1, "repro": "n2q2", "toolchain": "accept", "victim": victim, "submission": "via_pipeline", "fetch": "digest", "control": "R-REP-3 violated: reproductions reach the publisher through the pipeline"}))
        controls.append(("G_MIRROR", {"reg": "root", "V": 1, "repro": "n2q2", "toolchain": "accept", "victim": victim, "submission": "first_hand", "fetch": "mirror", "control": "R-REP-2 violated: inputs fetched from the CI-named mirror, not by digest"}))
        controls.append(("G_BYTES", {"reg": "root", "V": 1, "repro": "d_n2q2", "toolchain": "accept", "victim": victim, "submission": "first_hand", "fetch": "digest", "passthrough": True,
                                     "control": "D-A07 analogue: under OP-9 (d) custodians name the digest the pipeline hands them instead of reproducing (pass-through)"}))
    return main, controls


def self_checks():
    """Expectations fixed before the run; each is a sentence of the pack, checked against the model."""
    c = {"reg": "root", "V": 1, "repro": "n2q2", "toolchain": "accept", "victim": "FA2", "submission": "first_hand", "fetch": "digest"}
    ex = []
    def chk(label, goal, caps, cfg, want):
        ex.append({"check": label, "goal": goal, "caps": caps, "config": {k: cfg[k] for k in ("reg", "V", "repro", "toolchain", "victim")}, "expected": want,
                   "observed": accepted(goal, caps, cfg), "ok": accepted(goal, caps, cfg) == want})
    chk("no capability: nothing accepted", "G_BYTES", [], c, False)
    chk("RV4-B-A01 shape: one reproducer key + pipeline", "G_BYTES", ["rep1", "pipeline"], c, False)
    chk("RV4-B-A02 shape: one verification key + pipeline", "G_SRC", ["va1", "pipeline"], c, False)
    chk("release-final + release-candidate + pipeline (RV3-B-A08 / RV3-D-A03 shapes)", "G_SRC", ["rf", "rc", "pipeline"], c, False)
    chk("route I (insider) is the stated process residual", "G_SRC", ["insider"], c, True)
    chk("verification process + pipeline, OP-8 = 1 (TB-4')", "G_SRC", ["vp1", "pipeline"], c, True)
    chk("verification process + pipeline, OP-8 = 2", "G_SRC", ["vp1", "pipeline"], dict(c, V=2), False)
    chk("two reproducer processes, n=2 q=2 (TB-S1)", "G_BYTES", ["rp1", "rp2"], c, True)
    chk("two reproducer processes, n=3 q=2: third honest reproducer conflicts", "G_BYTES", ["rp1", "rp2"], dict(c, repro="n3q2"), False)
    chk("two reproducer keys + trust-state key, both channels, no transport: honest reproductions conflict", "G_BYTES", ["rep1", "rep2", "ts", "ch1", "ch2"], c, False)
    chk("two reproducer keys + trust-state key + both channels + transport (stated FA2 minimum)", "G_BYTES", ["rep1", "rep2", "ts", "ch1", "ch2", "transport"], c, True)
    chk("two reproducer keys + trust-state key + one channel + transport at FA2: disagreement", "G_BYTES", ["rep1", "rep2", "ts", "ch1", "transport"], c, False)
    chk("pipeline + two reproducer keys (first-hand submission)", "G_BYTES", ["pipeline", "rep1", "rep2"], c, False)
    chk("pipeline + two reproducer keys (control: submission via pipeline)", "G_BYTES", ["pipeline", "rep1", "rep2"], dict(c, submission="via_pipeline"), True)
    chk("pipeline names a malicious toolchain", "G_INPUTS", ["pipeline"], c, False)
    chk("poisoned mirror, inputs by digest", "G_MIRROR", ["mirror"], c, False)
    chk("poisoned mirror (control: CI-named mirror)", "G_MIRROR", ["mirror"], dict(c, fetch="mirror"), True)
    chk("compromised upstream toolchain, OP-10 (a) (TA-12)", "G_TOOLCHAIN", ["toolchain_up"], c, True)
    chk("compromised upstream toolchain, OP-10 (b) diverse reproducer conflicts", "G_TOOLCHAIN", ["toolchain_up"], dict(c, toolchain="diverse"), False)
    chk("delegated registration custodians at threshold + verification key (OP-2 (b))", "G_SRC", ["cust1", "cust2", "va1"], dict(c, reg="delegated"), True)
    chk("delegated registration keys only + verification key, no trust-state key", "G_SRC", ["regk1", "regk2", "va1"], dict(c, reg="delegated"), False)
    return ex


def main():
    checks = self_checks()
    main_cfgs, control_cfgs = configs()
    with ProcessPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(run_cfg, main_cfgs, chunksize=2))
        controls = list(ex.map(run_cfg, control_cfgs, chunksize=1))
    inv_total = sum(len(r["invariants"]) for r in results)
    inv_fail = [(r["goal"], r["config"], k, v["counterexamples"]) for r in results for k, v in r["invariants"].items() if not v["holds"]]
    mono = sum(r["monotonicity_violations"] for r in results + controls)
    summary = {
        "configurations": len(results), "controls": len(control_cfgs), "self_checks": len(checks), "self_checks_ok": sum(c["ok"] for c in checks),
        "invariant_checks": inv_total, "invariant_failures": len(inv_fail), "monotonicity_spot_checks": sum(r["monotonicity_spot_checks"] for r in results + controls),
        "monotonicity_violations": mono, "max_enumerated_size": MAX_SIZE,
        "controls_minimal_sets": [{"control": r["config"]["control"], "victim": r["config"]["victim"], "goal": r["goal"], "minimal_sets": r["minimal_sets"][:6]} for r in controls],
    }
    table = {}
    for r in results:
        c = r["config"]
        key = f"{r['goal']}|OP-2={c['reg']}|OP-8={c['V']}|OP-9={c['repro']}|OP-10={c['toolchain']}|{c['victim']}"
        table[key] = [" + ".join(s) for s in r["minimal_sets"]]
    print(json.dumps({"instrument": "CS5 revision-5 derivation calculator", "honest_party_rules": __doc__.split("HONEST-PARTY RULES ENCODED")[1].split("Output:")[0].strip().splitlines(),
                      "summary": summary, "invariant_failures": inv_fail, "self_checks": checks, "minimal_sets_table": table,
                      "results": results, "control_results": controls}, indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
