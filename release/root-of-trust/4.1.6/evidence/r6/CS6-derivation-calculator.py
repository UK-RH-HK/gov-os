#!/usr/bin/env python3
"""CS6 — derivation calculator for RoT-1 revision 6 (rule FD-3, `29` §5.3). PROPOSED architecture instrument; decides nothing.

What it computes. For every configuration (owner answers × victim class × attack goal) the MINIMAL capability sets with which
some attacker strategy makes a victim accept a malicious production binary, or makes malicious non-orderable constitutional
content effective. The enumeration is exact for a monotone acceptance function: minimal true sets are found incrementally
through the minimal transversals of the sets already found (no size bound), and monotonicity is spot-checked.

Why a new calculator. Review r5 found that CS5's strategy set omitted selectors: channel-selected lineage and evaluator at first
admission (RV5-H1), the build environment (RV5-H2), registered constitutional content (RV5-H3), restrictor revocation
(RV5-M1), and victim classes (RV5-L5). CS6 derives its strategies from the complete decision register
(`decision-register/DECISION_REGISTER.yaml`): every selector substitution named there is a strategy below, and every
restrictor is a rule in RULES that can be switched off (mutation analysis, section "mutations").

Attribution. Method and honest-party style follow revision-5 CS5 (AR-0011), review r4 reviewer B's reference model, review r5
reviewer B's calculator extensions (parts L, I, P, R, C of `RV5-B-A04-calculator-extensions.py`) and synthesis D-A01. No code
is copied; the rules are revision 6.

Atoms (capabilities): see ATOMS. `op1src` is the operator typing one source's value where the procedure names more (TA-5/A10);
`pinprov` is a CI pin provisioner the repository writer controls (RS-4); `alt` is the OP-13 (c) second authentication path;
`media` is the OP-13 (d) provisioning media custody; `wk1`,`wk2` witness keys (OP-7 (c)).

Honest-party and verifier rules: RULES (id -> the pack rule it encodes). A rule switched off reverts to the weaker behaviour
named in its text. PROFILE_R5 switches off exactly the revision-6 additions: with it, CS6 must reproduce the review r5 minima
(controls section).

Output: JSON on stdout (summary, invariant failures, self-checks, mutation analysis, generated statements and the minimal-set
tables of every configuration). The per-configuration records (atoms, minimal sets, labels, invariant results) are written
gzipped (mtime 0) to $CS6_RESULTS_GZ when that variable is set; their count and SHA-256 are in the stdout JSON. Deterministic.
No subprocesses.
"""
import itertools, json, random, sys
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True

IMPLIES = {"vp1": ("va1",), "vp2": ("va2",), "rp1": ("rep1",), "rp2": ("rep2",), "rp3": ("rep3",), "cust1": ("regk1",), "cust2": ("regk2",)}
ATOMS = {
    "process": ["vp1", "vp2", "cust1", "cust2", "rp1", "rp2", "rp3"],
    "key": ["va1", "va2", "regk1", "regk2", "rep1", "rep2", "rep3", "ts", "rc", "rf", "kc", "wk1", "wk2"],
    "infrastructure": ["pipeline", "transport", "repo", "mirror"],
    "first_contact": ["ch1", "ch2", "alt", "media"],
    "residual": ["insider", "toolchain_up", "diverse_tc", "owner_tc", "env_up_a", "env_up_b", "owner_env", "op1src", "pinprov"],
}
RESIDUAL_LABEL = {"insider": "TB-4 route I (insider change accepted by honest verification)", "toolchain_up": "TA-12 / TB-S2 upstream toolchain release",
                  "diverse_tc": "OP-10 (b) diverse compiler compromised", "owner_tc": "OP-10 (c) owner-built toolchain compromised",
                  "env_up_a": "TA-12' upstream environment supplier (class A)", "env_up_b": "TA-12' second environment supplier (class B)",
                  "owner_env": "OP-16 (c) owner-built environment or its upstream sources", "op1src": "TA-5 / A10 operator types one source's value for every required source",
                  "pinprov": "RS-4 pin provisioned by a party the repository writer controls"}
ATOM_DESCRIPTION = {
    "vp1": "verification process 1 compromised (lies first-hand)", "vp2": "verification process 2 compromised", "va1": "verification-attestation key 1 stolen",
    "va2": "verification-attestation key 2 stolen", "cust1": "registration custodian 1 compromised", "cust2": "registration custodian 2 compromised",
    "regk1": "registration key 1 stolen", "regk2": "registration key 2 stolen", "rp1": "reproducer process 1", "rp2": "reproducer process 2", "rp3": "reproducer process 3",
    "rep1": "reproducer key 1", "rep2": "reproducer key 2", "rep3": "reproducer key 3", "ts": "trust-state key", "rc": "release-candidate key", "rf": "release-final key",
    "kc": "one everyday key holding release-candidate and release-final (OP-4 'no')", "wk1": "freshness-witness key 1", "wk2": "freshness-witness key 2",
    "pipeline": "release pipeline (CI) input", "transport": "withholding at the victim", "repo": "repository writer delivers a release (A2)", "mirror": "input mirror",
    "ch1": "first-contact / independent channel 1", "ch2": "first-contact / independent channel 2", "alt": "OP-13 (c) second authentication path (platform signing)",
    "media": "OP-13 (d) provisioning media custody", **{k: v for k, v in RESIDUAL_LABEL.items()}}
PROCESS = set(ATOMS["process"])
KEYS = set(ATOMS["key"])
FC_ATOMS = set(ATOMS["first_contact"]) | {"op1src"}

RULES = {
    "H_VER_UPSTREAM": "R-VER-1: verifiers check toolchain archives and environment components against upstream signed checksums",
    "H_VER_BINDS_CANDIDATE": "R-VER-1 / R-CON-2: an honest verifier attests exactly the candidate and the kernel tree it reproduced from the source",
    "H_REG_RECORDS_FIRST_HAND": "R-REG-3 (d): the ceremony counts only first-hand verification records for exactly the candidate",
    "H_REG_UPSTREAM": "R-REG-3 (a), (c'): the ceremony checks toolchain archives and environment components against upstream signatures",
    "H_REG_ENV_QUORUM": "R-BENV-2: the registered image digest is established by a first-hand environment reproduction quorum",
    "H_REP_ENV_REASSEMBLE": "R-BENV-4: honest reproducers re-assemble the registered environment from pinned components and refuse a mismatch",
    "H_REG_CONTENT_FIRST_HAND": "R-CON-1: custodians derive kernel tree, unit map and migrations from the fetched source",
    "H_REG_OWN_REPRODUCTION": "R-REG-3 (f): under OP-9 (d) custodians name their own reproduction",
    "H_REP_BY_DIGEST": "R-REP-2: reproducers obtain every input by digest",
    "H_REP_FIRST_HAND": "R-REP-3: reproducers confirm first-hand to the publisher",
    "H_SIGN_REPRODUCE": "05 §7 rule 2: candidate and final signers sign only the payload they rebuilt from the source",
    "H_PUB_REGISTRATION_RESTRICTORS": "R-PUB-1': the publisher references a registration only when E7's restrictors hold on the statements it holds",
    "V_QUORUM": "AP-6: at least q distinct reproducer keys",
    "V_CONFLICT": "AP-6 / R-REP-5: a visible conflicting reproduction refuses",
    "V_REJECTED": "AP-5: a held REJECTED attestation refuses",
    "V_VERIFICATION_COUNT": "AP-5: at least OP-8 ACCEPTED attestations",
    "V_CANDIDATE_BINDING": "AP-5 / R-CON-2: counted attestations name the registered candidate and kernel tree (not only the source)",
    "V_E7_RESTRICTORS": "E7 / R-CON-3: policy-root eligibility applies AP-5's restrictors",
    "V_REVOCATION_AUTHORITY": "AP-5r / R-REP-5' (CR5-B-01): restrictors are removed only under the registration authority",
    "V_FC_COMPILED_QUORUM": "FC-4: compiled first-contact quorum, never read from the state the typed value selects",
    "V_FC_LINEAGE": "FC-6 / FC-7: lineage from the typed value; compiled lineage under OP-13 (c)",
    "V_FC_EVALUATOR": "FC-1…FC-3 / FC-8: evaluator selected through the manifest bound by the agreed first-contact code",
    "V_P1_NAMES_STATE": "24 §4.4 (CR4-B-07 option 1): a P1 proof covers only the Trust State it names",
    "V_ENV_DIVERSITY": "R-BENV-5: under OP-16 (b) acceptance needs matching reproductions from two supplier classes",
    "V_OP9D_DIGEST": "AP-6 under OP-9 (d): the digest equals the registered digest",
    "V_PUBLISHED": "AP-7: the selected Trust State publishes the digest",
    "V_REGISTRATION_REFERENCED": "AP-5: the registration is referenced by the selected Trust State",
}
R6 = {k: True for k in RULES}
PROFILE_R5_OFF = ["H_VER_BINDS_CANDIDATE", "H_REG_CONTENT_FIRST_HAND", "H_REG_ENV_QUORUM", "H_REP_ENV_REASSEMBLE", "H_PUB_REGISTRATION_RESTRICTORS",
                  "V_CANDIDATE_BINDING", "V_E7_RESTRICTORS", "V_REVOCATION_AUTHORITY", "V_FC_COMPILED_QUORUM", "V_FC_LINEAGE", "V_FC_EVALUATOR", "V_ENV_DIVERSITY"]
R5 = dict(R6, **{k: False for k in PROFILE_R5_OFF})

REPRO = {"n2q2": (2, 2, False), "n3q2": (3, 2, False), "n3q3": (3, 3, False), "d_n2q2": (2, 2, True), "d_n3q2": (3, 2, True), "d_n3q3": (3, 3, True)}
FC_OPTS = {"a": (1, None), "b": (2, None), "c_all_1": (1, "all"), "c_all_2": (2, "all"), "c_either_1": (1, "either"), "c_either_2": (2, "either"), "d": (1, "media")}


def expand(C):
    out = set(C)
    for a in C:
        out.update(IMPLIES.get(a, ()))
    return out


# ------------------------------------------------------------------------------------------------ first contact and state selection
def srcs(C, k):
    """k agreeing first-contact sources, or one source whose value the operator types for every required input (TA-5/A10)."""
    return "ch1" in C and (k == 1 or "ch2" in C or "op1src" in C)


def fc_lineage_sub(C, opt, R):
    """The victim's admitter selects a lineage the attacker generated (every statement valid within it)."""
    k, mode = FC_OPTS[opt]
    if mode == "media":
        return "media" in C
    if mode is None:
        return srcs(C, k) if R["V_FC_COMPILED_QUORUM"] else "ch1" in C
    if mode == "all":
        return srcs(C, k) and ("alt" in C or not R["V_FC_LINEAGE"])
    return srcs(C, k) or "alt" in C


def fc_eval_sub(C, opt, R):
    """The operator runs a substituted evaluator, which admits anything."""
    k, mode = FC_OPTS[opt]
    kk = k if R["V_FC_EVALUATOR"] else 1
    if mode == "media":
        return "media" in C
    if mode is None:
        return srcs(C, kk)
    if mode == "all":
        return srcs(C, kk) and "alt" in C
    return srcs(C, kk) or "alt" in C


def fc_state_root(C, opt):
    k, mode = FC_OPTS[opt]
    if mode == "media":
        return "media" in C
    if mode == "either":
        return srcs(C, k) or "alt" in C
    return srcs(C, k)


def thief_selectable(C, cfg, R):
    """A descendant t_x signed with a stolen trust-state key is the Trust State the victim uses."""
    v = cfg["victim"]
    if "ts" not in C:
        return False
    if v in ("P1", "ING_P1"):
        return not R["V_P1_NAMES_STATE"]
    if v == "CIR":
        return "pinprov" in C or not R["V_P1_NAMES_STATE"]
    if v in ("P2k1", "ING_P2k1"):
        return srcs(C, 1)
    if v in ("P2k2", "ING_P2k2"):
        return srcs(C, 2)
    if v in ("WR", "ING_WR"):
        return {"wk1", "wk2"} <= C
    if v == "USE":
        return True
    if v == "FA":
        return fc_state_root(C, cfg["fc"])
    return False


# ------------------------------------------------------------------------------------------------ release process
K_OF = {"S_good": "K_good", "S_evil": "K_evil", "S_ins": "K_ins"}


def releases(goal, C):
    good = {"S": "S_good", "I": "I_good", "E": "E_good", "K": "K_good", "genuine": True}
    if goal in ("G_BYTES", "G_TOOLCHAIN", "G_MIRROR"):
        return [good]
    if goal == "G_SRC":
        out = [{"S": "S_evil", "I": "I_good", "E": "E_good", "K": "K_evil", "genuine": False}]
        if "insider" in C:
            out.append({"S": "S_ins", "I": "I_good", "E": "E_good", "K": "K_ins", "genuine": False})
        return out
    if goal == "G_INPUTS":
        return [{"S": "S_good", "I": "I_evil", "E": "E_good", "K": "K_good", "genuine": False}]
    if goal == "G_ENV":
        return [good, {"S": "S_good", "I": "I_good", "E": "E_pipe", "K": "K_good", "genuine": False},
                {"S": "S_good", "I": "I_good", "E": "E_sub", "K": "K_good", "genuine": False}]
    if goal == "G_CONTENT":
        out = [{"S": "S_good", "I": "I_good", "E": "E_good", "K": "K_weak", "genuine": False},
               {"S": "S_evil", "I": "I_good", "E": "E_good", "K": "K_evil", "genuine": False}]
        if "insider" in C:
            out.append({"S": "S_ins", "I": "I_good", "E": "E_good", "K": "K_ins", "genuine": False})
        return out
    raise ValueError(goal)


def env_class(cfg, j):
    e = cfg.get("env", "a")
    if e == "a":
        return "A"
    if e == "c":
        return "O"
    return "A" if (j == 0 or j % 2 == 1) else "B"


def can_build(rel, R):
    return rel["E"] not in ("E_pipe", "E_sub") or not R["H_REP_ENV_REASSEMBLE"]


def build(rel, j, C, cfg, R):
    tcm = cfg.get("tc", "accept")
    if tcm == "owner_built":
        tc_evil = "owner_tc" in C
    elif tcm == "diverse" and j == 1:
        tc_evil = "diverse_tc" in C
    else:
        tc_evil = "toolchain_up" in C
    cls = env_class(cfg, j)
    env_evil = rel["E"] in ("E_pipe", "E_sub") or (cls == "A" and "env_up_a" in C) or (cls == "B" and "env_up_b" in C) or (cls == "O" and "owner_env" in C)
    mirror_evil = "mirror" in C and not R["H_REP_BY_DIGEST"]
    return ("B", rel["S"], rel["I"], tc_evil, env_evil, mirror_evil)


def target(goal, rel):
    if goal == "G_BYTES":
        return "B_evil"
    if goal == "G_TOOLCHAIN":
        return ("B", "S_good", "I_good", True, False, False)
    if goal == "G_ENV":
        return ("B", "S_good", "I_good", False, True, False)
    if goal == "G_MIRROR":
        return ("B", "S_good", "I_good", False, False, True)
    return ("B", rel["S"], rel["I"], False, False, False)


def honest_accepts(rel, R):
    if rel["S"] not in ("S_good", "S_ins") or rel["I"] != "I_good":
        return False
    if rel["E"] == "E_sub" and R["H_VER_UPSTREAM"]:
        return False
    if rel["K"] != K_OF[rel["S"]] and R["H_VER_BINDS_CANDIDATE"]:
        return False
    return True


def registration_routes(rel, C, cfg, R):
    V = cfg["V"]
    n, q, d = REPRO[cfg["repro"]]
    proposal = rel["genuine"] or "pipeline" in C or (rel["S"] == "S_ins" and "insider" in C)
    out = []
    if proposal:
        recs_ok = all((f"vp{i}" in C) or honest_accepts(rel, R) or (not R["H_REG_RECORDS_FIRST_HAND"] and f"va{i}" in C) for i in range(1, V + 1))
        up_ok = not R["H_REG_UPSTREAM"] or (rel["I"] == "I_good" and rel["E"] != "E_sub")
        env_ok = True
        if rel["E"] in ("E_pipe", "E_sub") and R["H_REG_ENV_QUORUM"]:
            env_ok = all(f"rp{j}" in C for j in range(1, n + 1))
        content_ok = not R["H_REG_CONTENT_FIRST_HAND"] or rel["K"] == K_OF[rel["S"]]
        if recs_ok and up_ok and env_ok and content_ok:
            rej = R["H_REG_RECORDS_FIRST_HAND"] and any(f"vp{i}" not in C and not honest_accepts(rel, R) for i in range(1, V + 1))
            out.append(("honest", True, rej))
    if {"cust1", "cust2"} <= C:
        out.append(("cust", True, False))
    if {"regk1", "regk2"} <= C:
        out.append(("key", False, False))
    return out


def final_ok(rel, C, cfg, R):
    if rel["genuine"]:
        return True
    if (cfg.get("op4") == "shared" and "kc" in C) or (cfg.get("op4", "sep") == "sep" and {"rf", "rc"} <= C):
        return True
    proposal = "pipeline" in C or (rel["S"] == "S_ins" and "insider" in C)
    return proposal and (rel["K"] == K_OF[rel["S"]] or not R["H_SIGN_REPRODUCE"])


def ver_keys(rel, route, C, cfg, R):
    keys = set()
    for i in range(1, cfg["V"] + 1):
        if f"vp{i}" in C or f"va{i}" in C:
            keys.add(i)
        elif honest_accepts(rel, R) and (route == "honest" or rel["genuine"]):
            keys.add(i)
        elif not R["V_CANDIDATE_BINDING"] and rel["S"] == "S_good" and rel["I"] == "I_good" and rel["E"] != "E_sub":
            keys.add(i)
    return keys


def custodian_digest(rel, X, C, cfg, R):
    if not R["H_REG_OWN_REPRODUCTION"] and "pipeline" in C:
        return X
    return build(rel, 0, C, cfg, R) if can_build(rel, R) else None


def published_by_owner(goal, rel, route, first_hand, rej, X, C, cfg, R):
    if not first_hand:
        return False
    n, q, d = REPRO[cfg["repro"]]
    vk = ver_keys(rel, route, C, cfg, R)
    if R["H_PUB_REGISTRATION_RESTRICTORS"] and not rel["genuine"] and (len(vk) < cfg["V"] or rej):
        return False
    if goal == "G_CONTENT":
        return True
    if len(vk) < cfg["V"] or rej:
        return False
    if not R["H_REP_FIRST_HAND"] and "pipeline" in C:
        confirms = {j: X for j in range(1, n + 1) if f"rep{j}" in C}
    else:
        confirms = {}
        for j in range(1, n + 1):
            if f"rp{j}" in C:
                confirms[j] = X
            else:
                confirms[j] = build(rel, j, C, cfg, R) if can_build(rel, R) else "ENVIRONMENT_NOT_REPRODUCED"
    if set(confirms.values()) != {X} or len(confirms) < q:
        return False
    if cfg.get("env") == "b" and R["V_ENV_DIVERSITY"] and not {env_class(cfg, j) for j in confirms} >= {"A", "B"}:
        return False
    if d and R["V_OP9D_DIGEST"] and route == "honest" and custodian_digest(rel, X, C, cfg, R) != X:
        return False
    return True


def binary_accepted(goal, C, cfg, R):
    if cfg["victim"] == "FA" and (fc_lineage_sub(C, cfg["fc"], R) or fc_eval_sub(C, cfg["fc"], R)):
        return True
    n, q, d = REPRO[cfg["repro"]]
    thief = thief_selectable(C, cfg, R)
    withhold = "transport" in C
    ra = {"cust1", "cust2"} <= C or {"regk1", "regk2"} <= C
    for rel in releases(goal, C):
        X = target(goal, rel)
        if goal in ("G_SRC", "G_INPUTS") and not final_ok(rel, C, cfg, R):
            continue
        for route, first_hand, rej in registration_routes(rel, C, cfg, R):
            pub = published_by_owner(goal, rel, route, first_hand, rej, X, C, cfg, R)
            sels = (["honest"] if pub else []) + (["thief"] if thief else [])
            for sel in sels:
                if sel == "honest" and route == "key" and R["V_REGISTRATION_REFERENCED"]:
                    continue
                vk = ver_keys(rel, route, C, cfg, R)
                if R["V_VERIFICATION_COUNT"] and len(vk) < cfg["V"]:
                    continue
                thief_rev = sel == "thief" and not R["V_REVOCATION_AUTHORITY"]
                if rej and R["V_REJECTED"] and not (withhold or ra or thief_rev):
                    continue
                honest_js = [j for j in range(1, n + 1) if f"rp{j}" not in C] if (first_hand and can_build(rel, R)) else []
                keys = {j for j in range(1, n + 1) if f"rep{j}" in C} | {j for j in honest_js if build(rel, j, C, cfg, R) == X}
                if R["V_QUORUM"] and len(keys) < q:
                    continue
                if R["V_CONFLICT"] and any(build(rel, j, C, cfg, R) != X for j in honest_js) and not (withhold or ra or thief_rev):
                    continue
                if cfg.get("env") == "b" and R["V_ENV_DIVERSITY"] and not {env_class(cfg, j) for j in keys} >= {"A", "B"}:
                    continue
                if d and R["V_OP9D_DIGEST"] and route == "honest" and custodian_digest(rel, X, C, cfg, R) != X:
                    continue
                return True
    return False


def content_accepted(C, cfg, R):
    v = cfg["victim"]
    if v == "FA" and (fc_lineage_sub(C, cfg["fc"], R) or fc_eval_sub(C, cfg["fc"], R)):
        return True
    thief = thief_selectable(C, cfg, R)
    ra = {"cust1", "cust2"} <= C or {"regk1", "regk2"} <= C
    for rel in releases("G_CONTENT", C):
        if not final_ok(rel, C, cfg, R):
            continue
        for route, first_hand, rej in registration_routes(rel, C, cfg, R):
            pub = published_by_owner("G_CONTENT", rel, route, first_hand, rej, None, C, cfg, R)
            sels = (["honest"] if pub else []) + (["thief"] if thief else [])
            for sel in sels:
                if sel == "honest" and route == "key" and R["V_REGISTRATION_REFERENCED"]:
                    continue
                if v == "USE" and sel == "thief" and "repo" not in C:
                    continue
                if R["V_E7_RESTRICTORS"]:
                    vk = ver_keys(rel, route, C, cfg, R)
                    if len(vk) < cfg["V"]:
                        continue
                    withhold = "transport" in C or (v == "USE" and "repo" in C)
                    thief_rev = sel == "thief" and not R["V_REVOCATION_AUTHORITY"]
                    if rej and not (withhold or ra or thief_rev):
                        continue
                return True
    return False


def accepted(goal, caps, cfg, R):
    C = expand(caps)
    if goal == "G_CONTENT":
        return content_accepted(C, cfg, R)
    return binary_accepted(goal, C, cfg, R)


# ------------------------------------------------------------------------------------------------ atoms per configuration
def atoms_for(goal, cfg):
    n, q, d = REPRO[cfg["repro"]]
    V = cfg["V"]
    a = ["pipeline", "transport", "ts"] + [f"vp{i}" for i in range(1, V + 1)] + [f"va{i}" for i in range(1, V + 1)] + ["cust1", "cust2", "regk1", "regk2"]
    if goal != "G_CONTENT":
        a += [f"rp{j}" for j in range(1, n + 1)] + [f"rep{j}" for j in range(1, n + 1)]
    if goal in ("G_SRC", "G_INPUTS", "G_CONTENT"):
        a += ["kc"] if cfg.get("op4") == "shared" else ["rc", "rf"]
    if goal in ("G_SRC", "G_CONTENT"):
        a.append("insider")
    if goal == "G_MIRROR":
        a.append("mirror")
    if goal == "G_TOOLCHAIN":
        a += ["toolchain_up"] + (["diverse_tc"] if cfg.get("tc") == "diverse" else []) + (["owner_tc"] if cfg.get("tc") == "owner_built" else [])
    if goal == "G_ENV":
        a += {"a": ["env_up_a"], "b": ["env_up_a", "env_up_b"], "c": ["owner_env"]}[cfg.get("env", "a")]
    if goal == "G_CONTENT":
        a.append("repo")
    v = cfg["victim"]
    if v in ("P2k1", "ING_P2k1"):
        a += ["ch1"]
    if v in ("P2k2", "ING_P2k2"):
        a += ["ch1", "ch2", "op1src"]
    if v in ("WR", "ING_WR"):
        a += ["wk1", "wk2"]
    if v == "CIR":
        a += ["pinprov"]
    if v == "FA":
        k, mode = FC_OPTS[cfg["fc"]]
        a += ["ch1"] + (["ch2", "op1src"] if k == 2 else []) + (["alt"] if mode in ("all", "either") else []) + (["media"] if mode == "media" else [])
    seen, out = set(), []
    for x in a:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ------------------------------------------------------------------------------------------------ exact minimal-set enumeration
def minimal_transversals(family):
    T = [frozenset()]
    for M in family:
        nxt = []
        for t in T:
            if t & M:
                nxt.append(t)
            else:
                nxt.extend(t | {x} for x in M)
        nxt = sorted(set(nxt), key=lambda s: (len(s), sorted(s)))
        mins = []
        for s in nxt:
            if not any(m <= s for m in mins):
                mins.append(s)
        T = mins
    return T


def minimal_sets(goal, cfg, R):
    atoms = atoms_for(goal, cfg)
    A = frozenset(atoms)
    order = {x: i for i, x in enumerate(atoms)}
    calls = [0]

    def f(S):
        calls[0] += 1
        return accepted(goal, S, cfg, R)

    found = []
    if not f(A):
        return {"atoms": atoms, "minimal_sets": [], "calls": calls[0]}
    failing = []
    while True:
        progress = False
        for t in minimal_transversals(found):
            if any(fl <= t for fl in failing):
                continue
            cand = A - t
            if f(cand):
                cur = set(cand)
                for x in sorted(cand, key=lambda z: -order[z]):
                    if f(frozenset(cur - {x})):
                        cur.discard(x)
                found.append(frozenset(cur))
                progress = True
                break
            failing.append(t)
        if not progress:
            break
    disp = []
    for s in found:
        implied = {b for x in s for b in IMPLIES.get(x, ())}
        disp.append(sorted((x for x in s if x not in implied), key=lambda z: order[z]))
    disp = sorted({tuple(s) for s in disp}, key=lambda s: (len(s), [order[x] for x in s]))
    return {"atoms": atoms, "minimal_sets": [list(s) for s in disp], "calls": calls[0]}


def monotonicity_spot_checks(goal, cfg, R, n=60, seed=7):
    atoms = atoms_for(goal, cfg)
    rnd = random.Random(seed + len(atoms) + len(goal))
    viol = 0
    for _ in range(n):
        S = frozenset(x for x in atoms if rnd.random() < 0.35)
        T = S | frozenset(x for x in atoms if rnd.random() < 0.3)
        if accepted(goal, S, cfg, R) and not accepted(goal, T, cfg, R):
            viol += 1
    return n, viol


# ------------------------------------------------------------------------------------------------ invariants
def label(s, cfg):
    tags = [RESIDUAL_LABEL[a] for a in s if a in RESIDUAL_LABEL]
    ss = set(s)
    if len({a[-1] for a in ss if a.startswith(("cust", "regk"))}) >= 2:
        tags.append("registration authority at threshold: " + ("root threshold (A8)" if cfg.get("reg") == "root" else "delegated registration quorum (OP-2 (b))"))
    if any(a.startswith("vp") for a in ss):
        tags.append("verification-process compromise (TA-11; TB-4')")
    if any(a.startswith("rp") for a in ss):
        tags.append("reproducer-process compromise (TB-S1)")
    if ss and ss <= FC_ATOMS:
        tags.append("first-contact root (OP-13)")
    return tags


def declared_fc_root(opt):
    k, mode = FC_OPTS[opt]
    ch = [["ch1"]] if k == 1 else [["ch1", "ch2"], ["ch1", "op1src"]]
    if mode is None:
        return ch
    if mode == "media":
        return [["media"]]
    if mode == "all":
        return [["ch1", "alt"] if c == ["ch1"] else c[:1] + c[1:] + ["alt"] for c in ch]
    return [["alt"]] + ch


def invariants(goal, cfg, sets):
    n, q, d = REPRO[cfg["repro"]]
    V = cfg["V"]
    out = {}
    residual = lambda s: any(a in RESIDUAL_LABEL for a in s)
    reg_pair = lambda s: len({a[-1] for a in s if a.startswith(("cust", "regk"))}) >= 2
    ver = lambda s: len({a[-1] for a in s if a.startswith(("va", "vp"))})
    vp = lambda s: len({a[-1] for a in s if a.startswith("vp")})
    rep = lambda s: len({a[-1] for a in s if a.startswith(("rep", "rp"))})
    fc_only = lambda s: set(s) <= FC_ATOMS
    fa = cfg["victim"] == "FA"
    body = [s for s in sets if not (fa and fc_only(s))]
    if fa:
        dec = sorted(sorted(x) for x in declared_fc_root(cfg["fc"]))
        got = sorted(sorted(s) for s in sets if fc_only(s))
        out["INV-FC every first-contact-only minimal set is the declared first-contact root of the OP-13 answer, and every declared set is minimal"] = {"holds": got == dec, "declared": dec, "computed": got}
    if goal == "G_BYTES":
        bad = [s for s in body if rep(s) < q and not residual(s)]
        out["INV-BYTES every other minimal set contains >= q reproducer compromises"] = {"holds": not bad, "counterexamples": bad}
    if goal in ("G_SRC", "G_INPUTS"):
        bad = [s for s in body if not residual(s) and not (ver(s) >= V and (reg_pair(s) or (goal == "G_SRC" and "pipeline" in s)))]
        out["INV-SRC every non-residual minimal set contains >= OP-8 verification compromises and (the registration threshold, or pipeline input for a malicious source)"] = {"holds": not bad, "counterexamples": bad}
    if goal == "G_ENV":
        env_res = {"a": {"env_up_a"}, "b": {"env_up_a", "env_up_b"}, "c": {"owner_env"}}[cfg.get("env", "a")]
        bad = [s for s in body if not ((env_res & set(s)) or rep(s) >= q or (reg_pair(s) and ver(s) >= V))]
        out["INV-ENV every minimal set contains an OP-16 environment residual atom, >= q reproducer compromises, or the registration threshold with OP-8 verification compromises"] = {"holds": not bad, "counterexamples": bad}
        if cfg.get("env") == "b":
            single = [s for s in sets if set(s) & env_res and len(set(s) & env_res) == 1 and not any(a.startswith("rp") or a.startswith("rep") for a in s)]
            out["INV-ENV-B under OP-16 (b) no minimal set holds one environment supplier compromise without a second supplier or a reproducer of the other class"] = {"holds": not single, "counterexamples": single}
        pipe = [s for s in body if set(s) <= {"pipeline", "transport", "ts", "ch1", "ch2", "repo", "mirror"}]
        out["INV-ENV-PIPELINE the pipeline, with or without infrastructure and the trust-state key, never selects the environment"] = {"holds": not pipe, "counterexamples": pipe}
    if goal == "G_CONTENT":
        bad = [s for s in body if not residual(s) and not ((reg_pair(s) and ver(s) >= V) or ("pipeline" in s and vp(s) >= V))]
        out["INV-CONTENT every non-residual minimal set contains the registration threshold with >= OP-8 verification compromises, or pipeline input with >= OP-8 verification processes (TB-4')"] = {"holds": not bad, "counterexamples": bad}
        weak = [s for s in body if not residual(s) and set(s) <= {"pipeline", "rc", "rf", "kc", "ts", "transport", "repo", "ch1", "ch2", "op1src", "wk1", "wk2"}]
        out["INV-RF release-candidate and release-final keys, pipeline, trust-state key and delivery never select content"] = {"holds": not weak, "counterexamples": weak}
    if goal == "G_MIRROR":
        bad = [s for s in body if "mirror" in s]
        out["INV-MIRROR inputs by digest: the mirror appears in no minimal set"] = {"holds": not bad, "counterexamples": bad}
    one = [s for s in body if not residual(s) and not any(a in PROCESS for a in s) and len([a for a in s if a in KEYS]) <= 1]
    out["INV-ONE no key-theft-only minimal set with at most one key (residual and first-contact root sets excepted)"] = {"holds": not one, "counterexamples": one}
    return out


# ------------------------------------------------------------------------------------------------ configurations
BIN_VICTIMS = ["P1", "P2k1", "P2k2", "WR", "CIR", "FA"]
CONTENT_VICTIMS = ["USE", "ING_P1", "ING_P2k1", "ING_P2k2", "ING_WR", "FA"]


def cfg_key(goal, c):
    parts = [goal, "OP-2=" + c["reg"], "OP-4=" + c.get("op4", "sep"), "OP-8=%d" % c["V"], "OP-9=" + c["repro"]]
    if goal == "G_TOOLCHAIN":
        parts.append("OP-10=" + c["tc"])
    if goal == "G_ENV":
        parts.append("OP-16=" + c["env"])
    parts.append(c["victim"] + ("(OP-13=" + c["fc"] + ")" if c["victim"] == "FA" else ""))
    return "|".join(parts)


def configs():
    out = []
    for reg in ("root", "delegated"):
        for V in (1, 2):
            for repro in REPRO:
                for victim in BIN_VICTIMS:
                    for fc in (FC_OPTS if victim == "FA" else ["-"]):
                        base = {"reg": reg, "V": V, "repro": repro, "victim": victim, "fc": fc, "op4": "sep", "tc": "accept", "env": "a"}
                        for goal in ("G_SRC", "G_INPUTS", "G_BYTES", "G_MIRROR"):
                            out.append((goal, dict(base)))
                        if repro in ("n2q2", "n3q2", "d_n2q2") and victim in ("P1", "P2k1", "FA", "CIR"):
                            for env in ("a", "b", "c"):
                                out.append(("G_ENV", dict(base, env=env)))
                for op4 in ("sep", "shared"):
                    for victim in CONTENT_VICTIMS:
                        for fc in (FC_OPTS if victim == "FA" else ["-"]):
                            out.append(("G_CONTENT", {"reg": reg, "V": V, "repro": "n2q2", "victim": victim, "fc": fc, "op4": op4, "tc": "accept", "env": "a"}))
                out.append(("G_SRC", {"reg": reg, "V": V, "repro": "n2q2", "victim": "P2k1", "fc": "-", "op4": "shared", "tc": "accept", "env": "a"}))
    for tc in ("accept", "diverse", "owner_built"):
        for repro in ("n2q2", "n3q2", "n3q3", "d_n2q2"):
            for victim, fc in (("P1", "-"), ("FA", "a"), ("FA", "b")):
                out.append(("G_TOOLCHAIN", {"reg": "root", "V": 1, "repro": repro, "victim": victim, "fc": fc, "op4": "sep", "tc": tc, "env": "a"}))
    seen, uniq = set(), []
    for g, c in out:
        k = cfg_key(g, c)
        if k not in seen:
            seen.add(k)
            uniq.append((g, c))
    return uniq


def run_cfg(args):
    goal, cfg, profile = args
    R = R6 if profile == "r6" else R5
    r = minimal_sets(goal, cfg, R)
    checks, viol = monotonicity_spot_checks(goal, cfg, R)
    res = {"goal": goal, "config": cfg, "key": cfg_key(goal, cfg), "profile": profile, "atoms": r["atoms"], "minimal_sets": r["minimal_sets"], "calls": r["calls"],
           "monotonicity_spot_checks": checks, "monotonicity_violations": viol}
    if profile == "r6":
        res["labels"] = [{"set": s, "labels": label(s, cfg)} for s in r["minimal_sets"]]
        res["invariants"] = invariants(goal, cfg, r["minimal_sets"])
    return res


# ------------------------------------------------------------------------------------------------ self-checks (sentences of the pack, fixed before the run)
def self_checks():
    base = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "P1", "fc": "-", "op4": "sep", "tc": "accept", "env": "a"}
    ex = []

    def chk(label_, goal, caps, cfg, want, R=R6):
        got = accepted(goal, frozenset(caps), cfg, R)
        ex.append({"check": label_, "goal": goal, "caps": caps, "config": cfg_key(goal, cfg), "profile": "r6" if R is R6 else "r5", "expected": want, "observed": got, "ok": got == want})

    fa = lambda opt: dict(base, victim="FA", fc=opt)
    # CS5's self-checks, re-expressed
    chk("no capability: nothing accepted", "G_BYTES", [], fa("b"), False)
    chk("RV4-B-A01 shape: one reproducer key + pipeline", "G_BYTES", ["rep1", "pipeline"], fa("b"), False)
    chk("RV4-B-A02 shape: one verification key + pipeline", "G_SRC", ["va1", "pipeline"], fa("b"), False)
    chk("release-final + release-candidate + pipeline, binary", "G_SRC", ["rf", "rc", "pipeline"], fa("b"), False)
    chk("route I (insider) is the stated residual", "G_SRC", ["insider"], base, True)
    chk("verification process + pipeline, OP-8 = 1 (TB-4')", "G_SRC", ["vp1", "pipeline"], base, True)
    chk("verification process + pipeline, OP-8 = 2", "G_SRC", ["vp1", "pipeline"], dict(base, V=2), False)
    chk("two reproducer processes, n=2 q=2 (TB-S1)", "G_BYTES", ["rp1", "rp2"], base, True)
    chk("two reproducer processes, n=3 q=2: the third honest reproducer conflicts", "G_BYTES", ["rp1", "rp2"], dict(base, repro="n3q2"), False)
    chk("pipeline names a malicious toolchain", "G_INPUTS", ["pipeline"], base, False)
    chk("poisoned mirror, inputs by digest", "G_MIRROR", ["mirror"], base, False)
    chk("compromised upstream toolchain, OP-10 (a)", "G_TOOLCHAIN", ["toolchain_up"], base, True)
    chk("compromised upstream toolchain, OP-10 (b)", "G_TOOLCHAIN", ["toolchain_up"], dict(base, tc="diverse"), False)
    chk("delegated custodians + verification key register a malicious source", "G_SRC", ["cust1", "cust2", "va1", "pipeline"], dict(base, reg="delegated"), True)
    # BC5-1 first contact (RV5-B-A01, RV5-D-A02)
    chk("RV5-B-A01 A01a: OP-13 (a) one channel page selects the lineage (stated first-contact root)", "G_BYTES", ["ch1"], fa("a"), True)
    chk("RV5-B-A01 A01c / RV5-D-A02: OP-13 (b) one compromised channel", "G_BYTES", ["ch1"], fa("b"), False)
    chk("RV5-B-A01 A01b: OP-13 (b) both channels (stated first-contact root)", "G_BYTES", ["ch1", "ch2"], fa("b"), True)
    chk("OP-13 (b) operator types one page's value twice (TA-5/A10 residual)", "G_BYTES", ["ch1", "op1src"], fa("b"), True)
    chk("OP-13 (c) all-must-agree: channel alone", "G_BYTES", ["ch1"], fa("c_all_1"), False)
    chk("OP-13 (c) all-must-agree: platform path alone", "G_BYTES", ["alt"], fa("c_all_1"), False)
    chk("OP-13 (c) either-suffices: platform path alone", "G_BYTES", ["alt"], fa("c_either_1"), True)
    chk("OP-13 (d): provisioning media custody", "G_BYTES", ["media"], fa("d"), True)
    chk("OP-13 (d): a channel does not select the first TCB on a media-provisioned machine", "G_BYTES", ["ch1", "ch2"], fa("d"), False)
    chk("revision-5 control: OP-13 (b) one channel, quorum read from the selected state", "G_BYTES", ["ch1"], fa("b"), True, R5)
    # BC5-2 environment (RV5-B-H2)
    chk("RV5-B-A08: pipeline-produced image", "G_ENV", ["pipeline"], base, False)
    chk("revision-5 control: pipeline-produced image record", "G_ENV", ["pipeline"], base, True, R5)
    chk("OP-16 (a): upstream environment supplier (stated residual)", "G_ENV", ["env_up_a"], base, True)
    chk("OP-16 (b): one environment supplier conflicts with the other class", "G_ENV", ["env_up_a"], dict(base, env="b"), False)
    chk("OP-16 (b): both suppliers (stated residual)", "G_ENV", ["env_up_a", "env_up_b"], dict(base, env="b"), True)
    chk("OP-16 (c): owner-built environment (stated residual)", "G_ENV", ["owner_env"], dict(base, env="c"), True)
    # BC5-3 content (RV5-D-A01, RV5-B-H3)
    cing = dict(base, victim="ING_P1")
    chk("RV5-D-A01: pipeline + release-candidate + release-final keys", "G_CONTENT", ["pipeline", "rc", "rf"], cing, False)
    chk("RV5-D-A01 OP-4 'no': pipeline + one everyday key", "G_CONTENT", ["pipeline", "kc"], dict(cing, op4="shared"), False)
    chk("revision-5 control: RV5-D-A01 pipeline + candidate + final keys", "G_CONTENT", ["pipeline", "rc", "rf"], cing, True, R5)
    chk("RV5-B-A06: two delegated custodians + release-final + release-candidate (no verification compromise)", "G_CONTENT", ["cust1", "cust2", "rf", "rc"], dict(cing, reg="delegated"), False)
    chk("revision-5 control: RV5-B-A06 custodians + final + candidate keys", "G_CONTENT", ["cust1", "cust2", "rf", "rc"], dict(cing, reg="delegated"), True, R5)
    chk("custodians + final + candidate + verification key (stated: registration authority + OP-8 verification)", "G_CONTENT", ["cust1", "cust2", "rf", "rc", "va1"], dict(cing, reg="delegated"), True)
    # RV5-M1 / CR5-B-01 restrictor revocation (RV5-B-A03, A07)
    p2 = dict(base, victim="P2k1")
    chk("RV5-B-A03: two reproducer keys + trust-state key + channel, no transport", "G_BYTES", ["rep1", "rep2", "ts", "ch1"], p2, False)
    chk("revision-5 control: RV5-B-A03 trust-state revocation removes the conflict", "G_BYTES", ["rep1", "rep2", "ts", "ch1"], p2, True, R5)
    return ex


def compact(s):
    """Deterministic rendering of a minimal set by capability class (indices of interchangeable parties are not shown)."""
    ss = set(s)
    parts = []
    n_rp = len({a[-1] for a in ss if a.startswith("rp")})
    n_rep = len({a[-1] for a in ss if a.startswith("rep")} - {a[-1] for a in ss if a.startswith("rp")})
    n_cust = len({a[-1] for a in ss if a.startswith("cust")})
    n_regk = len({a[-1] for a in ss if a.startswith("regk")} - {a[-1] for a in ss if a.startswith("cust")})
    n_vp = len({a[-1] for a in ss if a.startswith("vp")})
    n_va = len({a[-1] for a in ss if a.startswith("va")} - {a[-1] for a in ss if a.startswith("vp")})
    for n, one, many in ((n_cust, "registration custodian", "registration custodians"), (n_regk, "registration key", "registration keys"),
                         (n_vp, "verification process", "verification processes"), (n_va, "verification key", "verification keys"),
                         (n_rp, "reproducer process", "reproducer processes"), (n_rep, "reproducer key", "reproducer keys")):
        if n:
            parts.append("%d %s" % (n, one if n == 1 else many))
    parts += [a for a in s if not a.startswith(("rp", "rep", "cust", "regk", "vp", "va"))]
    return "{" + ", ".join(parts) + "}"


def undominated(sets):
    """Sets shown in consequence statements. A party's process compromise implies its key (IMPLIES). A minimal set is omitted
    when the same set with one or more processes replaced by their keys is also a minimal set: the weaker capability is shown.
    Invariants and minimal-set tables use every minimal set."""
    fam = {frozenset(x) for x in sets}
    out = []
    for s in sets:
        procs = [a for a in s if a in IMPLIES]
        dom = False
        for r in range(1, len(procs) + 1):
            for sub in itertools.combinations(procs, r):
                v = frozenset((set(s) - set(sub)) | {k for p in sub for k in IMPLIES[p]})
                if v != frozenset(s) and v in fam:
                    dom = True
                    break
            if dom:
                break
        if not dom:
            out.append(s)
    return out


NOTE_UNDOMINATED = "Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`)."


def uniq_render(sets):
    out = []
    for x in (compact(s) for s in sets):
        if x not in out:
            out.append(x)
    return out


def statements(results):
    """Generated consequence blocks for `05`, `21`, `25`, `30`, `31`, `32`, `33`, `34` (compared by statements_check.py)."""
    by = {r["key"]: r for r in results if r["profile"] == "r6"}

    def sets_of(goal, **kw):
        c = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "P1", "fc": "-", "op4": "sep", "tc": "accept", "env": "a"}
        c.update(kw)
        return by[cfg_key(goal, c)]["minimal_sets"]

    fmt = compact
    blocks = {}
    rows = []
    for opt in FC_OPTS:
        fs = sets_of("G_BYTES", victim="FA", fc=opt)
        root = [fmt(s) for s in fs if set(s) <= FC_ATOMS]
        rows.append("| %s | %s | %d |" % (opt, "; ".join(root), len([s for s in fs if not set(s) <= FC_ATOMS])))
    blocks["FC-ROOT"] = "| OP-13 answer | First-contact root: minimal sets that admit a malicious first TCB with no key | Other minimal sets (release-process compromises, as for running machines) |\n|---|---|---|\n" + "\n".join(rows)
    rows = []
    for opt in FC_OPTS:
        fs = sets_of("G_BYTES", victim="FA", fc=opt)
        key_sets = uniq_render([s for s in fs if not set(s) <= FC_ATOMS and "ts" in s and not any(a in PROCESS for a in s)])
        rows.append("| %s | %s |" % (opt, "; ".join(key_sets) or "none"))
    blocks["FC-KEY-THEFT"] = "| OP-13 answer | Key-theft minimal sets for malicious bytes of a genuine registration (OP-2 (a), OP-8 = 1, OP-9 (a)) |\n|---|---|\n" + "\n".join(rows)
    rows = []
    for repro in REPRO:
        for victim in ("P1", "P2k1", "P2k2", "WR", "CIR"):
            rows.append("| %s | %s | %s |" % (repro, victim, "; ".join(uniq_render(undominated(sets_of("G_BYTES", repro=repro, victim=victim))))))
    blocks["OP-9-BYTES"] = NOTE_UNDOMINATED + "\n\n| OP-9 | Victim | Minimal sets: malicious bytes for a genuine registration (OP-2 (a), OP-8 = 1) |\n|---|---|---|\n" + "\n".join(rows)
    rows = []
    for V in (1, 2):
        for reg in ("root", "delegated"):
            rows.append("| %d | %s | %s |" % (V, reg, "; ".join(uniq_render(undominated(sets_of("G_SRC", V=V, reg=reg))))))
    blocks["OP-8-SRC"] = NOTE_UNDOMINATED + "\n\n| OP-8 | OP-2 | Minimal sets: malicious source faithfully built (victim P1, OP-9 (a)) |\n|---|---|---|\n" + "\n".join(rows)
    rows = []
    for tc in ("accept", "diverse", "owner_built"):
        rows.append("| %s | %s |" % (tc, "; ".join(uniq_render(undominated(sets_of("G_TOOLCHAIN", tc=tc))))))
    blocks["OP-10-TOOLCHAIN"] = "| OP-10 | Minimal sets: compromised common-mode toolchain (victim P1, OP-9 (a)) |\n|---|---|\n" + "\n".join(rows)
    rows = []
    for env in ("a", "b", "c"):
        for repro in ("n2q2", "n3q2"):
            rows.append("| %s | %s | %s |" % (env, repro, "; ".join(uniq_render(undominated(sets_of("G_ENV", env=env, repro=repro))))))
    blocks["OP-16-ENV"] = NOTE_UNDOMINATED + "\n\n| OP-16 | OP-9 | Minimal sets: malicious build environment (victim P1, OP-2 (a), OP-8 = 1) |\n|---|---|---|\n" + "\n".join(rows)
    rows = []
    for reg in ("root", "delegated"):
        for op4 in ("sep", "shared"):
            for V in (1, 2):
                for victim in ("USE", "ING_P1", "ING_P2k1"):
                    rows.append("| %s | %s | %d | %s | %s |" % (reg, op4, V, victim, "; ".join(uniq_render(undominated(sets_of("G_CONTENT", reg=reg, op4=op4, V=V, victim=victim))))))
    blocks["CONTENT"] = NOTE_UNDOMINATED + "\n\n| OP-2 | OP-4 | OP-8 | Victim | Minimal sets: malicious non-orderable constitutional content effective |\n|---|---|---|---|---|\n" + "\n".join(rows)
    rows = []
    for opt in FC_OPTS:
        fs = sets_of("G_CONTENT", victim="FA", fc=opt)
        rows.append("| %s | %s |" % (opt, "; ".join(fmt(s) for s in fs if set(s) <= FC_ATOMS)))
    blocks["FC-CONTENT"] = "| OP-13 answer | First-contact root sets for content on a first-admission machine |\n|---|---|\n" + "\n".join(rows)
    return blocks


def mutation_analysis(pool):
    """For every rule: the configurations whose minimal sets change when it alone is switched off (a register row's restrictor is
    load-bearing in the model iff this list is non-empty)."""
    probe = []
    base = {"reg": "delegated", "V": 1, "op4": "sep", "tc": "accept", "env": "a", "fc": "-"}
    for goal in ("G_SRC", "G_INPUTS", "G_BYTES", "G_MIRROR"):
        for repro in ("n2q2", "n3q2", "d_n2q2"):
            for victim in ("P1", "P2k1", "CIR"):
                probe.append((goal, dict(base, repro=repro, victim=victim)))
            for fc in FC_OPTS:
                probe.append((goal, dict(base, repro=repro, victim="FA", fc=fc)))
    for env in ("a", "b"):
        for victim in ("P1", "P2k1"):
            probe.append(("G_ENV", dict(base, repro="n2q2", victim=victim, env=env)))
    for victim in CONTENT_VICTIMS:
        for fc in (FC_OPTS if victim == "FA" else ["-"]):
            probe.append(("G_CONTENT", dict(base, repro="n2q2", victim=victim, fc=fc)))
    probe.append(("G_TOOLCHAIN", dict(base, reg="root", repro="n2q2", victim="P1", tc="diverse")))
    jobs = [(rule, g, c) for rule in RULES for g, c in probe]
    res = list(pool.map(_mut_job, jobs, chunksize=8))
    out = {}
    for rule, key, changed, ex in res:
        out.setdefault(rule, {"rule": RULES[rule], "changed_configurations": 0, "examples": []})
        if changed:
            out[rule]["changed_configurations"] += 1
            if len(out[rule]["examples"]) < 3:
                out[rule]["examples"].append({"configuration": key, "with_rule": ex[0][:4], "without_rule": ex[1][:4]})
    for rule in out:
        out[rule]["load_bearing_in_model"] = out[rule]["changed_configurations"] > 0
    return out


def _mut_job(args):
    rule, goal, cfg = args
    a = minimal_sets(goal, cfg, R6)["minimal_sets"]
    b = minimal_sets(goal, cfg, dict(R6, **{rule: False}))["minimal_sets"]
    return rule, cfg_key(goal, cfg), a != b, (a, b)


def main():
    checks = self_checks()
    cfgs = configs()
    with ProcessPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(run_cfg, [(g, c, "r6") for g, c in cfgs], chunksize=8))
        r5_controls = list(pool.map(run_cfg, [(g, c, "r5") for g, c in cfgs if (c["victim"] in ("FA", "P1", "P2k1", "ING_P1", "USE") and c["V"] == 1 and c["repro"] == "n2q2" and c["reg"] == "root")], chunksize=8))
        mutations = mutation_analysis(pool)
    inv_total = sum(len(r["invariants"]) for r in results)
    inv_fail = [{"key": r["key"], "invariant": k, "detail": v} for r in results for k, v in r["invariants"].items() if not v["holds"]]
    mono_checks = sum(r["monotonicity_spot_checks"] for r in results + r5_controls)
    mono_viol = sum(r["monotonicity_violations"] for r in results + r5_controls)
    summary = {
        "configurations": len(results), "goals": sorted({r["goal"] for r in results}), "victim_classes": sorted({r["config"]["victim"] for r in results}),
        "self_checks": len(checks), "self_checks_ok": sum(c["ok"] for c in checks), "invariant_checks": inv_total, "invariant_failures": len(inv_fail),
        "monotonicity_spot_checks": mono_checks, "monotonicity_violations": mono_viol, "accepted_calls": sum(r["calls"] for r in results),
        "rules": len(RULES), "rules_load_bearing_in_model": sorted(k for k, v in mutations.items() if v["load_bearing_in_model"]),
        "rules_not_load_bearing_in_model": sorted(k for k, v in mutations.items() if not v["load_bearing_in_model"]),
        "revision_5_profile_controls": len(r5_controls), "revision_5_profile_rules_off": PROFILE_R5_OFF,
    }
    table = {r["key"]: [" + ".join(s) for s in r["minimal_sets"]] for r in results}
    r5_table = {r["key"]: [" + ".join(s) for s in r["minimal_sets"]] for r in r5_controls}
    import gzip, hashlib, os
    results_bytes = json.dumps({"r6": results, "r5_profile_controls": r5_controls}, sort_keys=True, separators=(",", ":")).encode()
    gz_path = os.environ.get("CS6_RESULTS_GZ")
    if gz_path:
        with open(gz_path, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(results_bytes)
    print(json.dumps({"instrument": "CS6 revision-6 derivation calculator", "atoms": ATOMS, "atom_description": ATOM_DESCRIPTION, "rules": RULES,
                      "summary": summary, "invariant_failures": inv_fail, "self_checks": checks, "mutations": mutations, "statements": statements(results),
                      "minimal_sets_table": table, "revision_5_profile_table": r5_table,
                      "results": {"count": len(results), "r5_profile_controls": len(r5_controls), "sha256_of_uncompressed_json": hashlib.sha256(results_bytes).hexdigest(),
                                  "file": "CS6-results.json.gz"}}, indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
