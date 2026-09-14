#!/usr/bin/env python3
"""CS7 — derivation calculator for the RoT-1 revision-7 certified profile CP-1 (rule FD-3, `29` §5.3). PROPOSED architecture
instrument; decides nothing.

What it computes. For the ONE production configuration of CP-1 (`profile/CP-1.yaml`) and every victim class and attack goal, the
MINIMAL capability sets with which some attacker strategy makes a victim accept a malicious production binary, admit a revoked
binary, or make malicious non-orderable constitutional content effective. Exact minimal true sets through minimal transversals
(no size bound; transversals maintained incrementally and checked against the recomputing reference, `enumeration_reference_checks`); monotonicity spot-checked. Method and honest-party style follow CS6 (AR-0015); the code is revision 7's.

No option tree. The production configuration is fixed: registration 2-of-3 delegated (OP-2 (b)), separate candidate key and a
release-final threshold of 2 (OP-4), two verification records (OP-8), three reproducer roles with quorum 2 and registered binary
digests after the custodians' own reproduction (OP-9 (b) + (d)), two independent toolchain lineages (OP-10 (b)), two first-contact
sources with a compiled quorum (OP-13 (b)), two independent supplier classes (OP-16 (b)), anchored-only currency (OP-7 (a)).
Excluded modes have no atom and no branch here. `PROFILE_R6_CONTROL` switches off exactly the revision-7 rules and must reproduce
review r6's findings (controls, labelled non-production; they are not choices).

Atoms: ATOMS; each atom's class is given explicitly by ATOM_CLASS (no prefix matching; the renderer is injective, RV6-M1).
Victims: P1 (anchored by a confirmation or pin naming the state, made before the compromise), P1A (the same anchoring event made
after the compromise), P2 (in-gate state code typed from both sources), CIR (CI runner with a record and pin), FA (first admission),
RA_held (re-admission, the store holds the revocation), RA_unheld (re-admission, the store predates the revocation), USE, ING_P1,
ING_P2 (content). Goals: G_SRC, G_INPUTS, G_BYTES, G_MIRROR, G_TOOLCHAIN, G_ENV, G_CONTENT, G_REVOKED.

Output: JSON on stdout; per-configuration records gzipped (mtime 0) to $CS7_RESULTS_GZ when set. Deterministic. No subprocesses.
"""
import gzip, hashlib, itertools, json, os, random, sys
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True

IMPLIES = {"vp1": ("va1",), "vp2": ("va2",), "rp1": ("repk1",), "rp2": ("repk2",), "rp3": ("repk3",), "cust1": ("regk1",), "cust2": ("regk2",)}
ATOMS = {
    "process": ["vp1", "vp2", "cust1", "cust2", "rp1", "rp2", "rp3"],
    "key": ["va1", "va2", "regk1", "regk2", "repk1", "repk2", "repk3", "tsk1", "tsk2", "rck", "rfk1", "rfk2"],
    "infrastructure": ["pipeline", "transport", "repo", "mirror", "fcpub", "carrier"],
    "first_contact": ["src1", "src2", "desig1", "desig2"],
    "stored": ["stored_old"],
    "residual": ["insider", "toolchain_up", "diverse_tc", "tc_src", "env_up_a", "env_up_b", "env_common", "op1src", "pinprov", "win", "clockback", "store_admin"],
}
ATOM_CLASS = {"vp1": "verification process", "vp2": "verification process", "va1": "verification key", "va2": "verification key",
              "cust1": "registration custodian", "cust2": "registration custodian", "regk1": "registration key", "regk2": "registration key",
              "rp1": "reproducer process", "rp2": "reproducer process", "rp3": "reproducer process", "repk1": "reproducer key", "repk2": "reproducer key", "repk3": "reproducer key",
              "tsk1": "trust-state key", "tsk2": "trust-state key", "rfk1": "release-final key", "rfk2": "release-final key"}
PLURAL = {"verification process": "verification processes", "verification key": "verification keys", "registration custodian": "registration custodians",
          "registration key": "registration keys", "reproducer process": "reproducer processes", "reproducer key": "reproducer keys", "trust-state key": "trust-state keys",
          "release-final key": "release-final keys"}
CLASS_ORDER = ["registration custodian", "registration key", "verification process", "verification key", "reproducer process", "reproducer key", "trust-state key", "release-final key"]
RESIDUAL_LABEL = {
    "insider": "TB-4 route I: an insider change accepted by honest verification",
    "toolchain_up": "TA-12 upstream binary toolchain lineage compromised",
    "diverse_tc": "TA-12 independently bootstrapped toolchain lineage compromised",
    "tc_src": "TA-12″ compiler source compromised (common to every bootstrap lineage)",
    "env_up_a": "TA-12′ supplier class A compromised", "env_up_b": "TA-12′ supplier class B compromised",
    "env_common": "TA-12″ hidden common provenance between the registered supplier classes",
    "op1src": "TA-5″ operator reads one source and types its values for both",
    "pinprov": "RS-4 pin provisioned by a party the repository writer controls",
    "win": "CUR-R1 a revocation newer than the state both sources show, within the 24 h admission ceiling",
    "clockback": "RS-2 local clock set back on a machine without a store (A13)",
    "store_admin": "an administrator-level local attacker rewrites the protected admission store (outside TA-9)",
}
ATOM_DESCRIPTION = dict(RESIDUAL_LABEL, **{
    "vp1": "verification process 1 compromised", "vp2": "verification process 2 compromised", "va1": "verification key 1 stolen", "va2": "verification key 2 stolen",
    "cust1": "registration custodian 1 compromised", "cust2": "registration custodian 2 compromised", "regk1": "registration key 1 stolen", "regk2": "registration key 2 stolen",
    "rp1": "reproducer process 1", "rp2": "reproducer process 2", "rp3": "reproducer process 3", "repk1": "reproducer key 1", "repk2": "reproducer key 2", "repk3": "reproducer key 3",
    "tsk1": "trust-state key 1", "tsk2": "trust-state key 2", "rck": "release-candidate key", "rfk1": "release-final key 1", "rfk2": "release-final key 2",
    "pipeline": "release pipeline (CI) input", "transport": "withholding at the victim", "repo": "repository writer delivers a release (A2)", "mirror": "input mirror",
    "fcpub": "the trust-state publication process (composes nothing in CP-1)", "carrier": "download host or the unadmitted candidate presenting source names or procedure steps",
    "src1": "first-contact source 1 (authenticated private release channel) content", "src2": "first-contact source 2 (immutable release mirror) content",
    "desig1": "operator directed to a look-alike of source 1", "desig2": "operator directed to a look-alike of source 2",
    "stored_old": "first-contact codes stored or replayed from earlier than the 24 h ceiling (image codes, media, cached pages)"})
PROCESS, KEYS = set(ATOMS["process"]), set(ATOMS["key"])
FC_ATOMS = {"src1", "src2", "desig1", "desig2", "op1src"}

RULES = {
    "H_VER_UPSTREAM": "R-VER-1: verifiers check toolchain archives and environment components against pinned supplier keys",
    "H_VER_BINDS_CANDIDATE": "R-VER-1 / R-CON-2: an honest verifier attests exactly the candidate and kernel it reproduced",
    "H_REG_RECORDS_FIRST_HAND": "R-REG-3 (d): the ceremony counts only first-hand verification records for exactly the candidate",
    "H_REG_UPSTREAM": "R-REG-3 (a), (c″): the ceremony checks toolchain archives and components against pinned supplier keys",
    "H_REG_ENV_QUORUM": "33 R-BENV-7″: an environment is authoritative only with agreeing environment reproductions and the registration over its exact identity, never a pipeline record",
    "H_REP_ENV_REASSEMBLE": "R-BENV-4″: honest reproducers re-assemble the registered environment and refuse a mismatch",
    "H_REG_CONTENT_FIRST_HAND": "R-CON-1: custodians derive kernel tree, unit map and migrations first-hand",
    "H_REG_OWN_REPRODUCTION": "R-REG-3 (f): custodians register only digests of their own reproduction (OP-9 (d))",
    "H_REP_BY_DIGEST": "R-REP-2: reproducers obtain every input by digest",
    "H_REP_FIRST_HAND": "R-REP-3: reproducers confirm first-hand to the publisher",
    "H_SIGN_REPRODUCE": "05 §7 rule 2: candidate and final signers sign only what they rebuilt",
    "H_PUB_REGISTRATION_RESTRICTORS": "R-PUB-1′: the publisher references a registration only when E7's restrictors hold",
    "V_QUORUM": "AP-6: at least 2 distinct reproducer keys",
    "V_CONFLICT": "AP-6 / R-REP-5′: a visible conflicting reproduction refuses",
    "V_REJECTED": "AP-5: a held REJECTED attestation refuses",
    "V_VERIFICATION_COUNT": "AP-5: two ACCEPTED attestations from distinct keys and executions",
    "V_CANDIDATE_BINDING": "AP-5 / R-CON-2: counted attestations name the registered candidate and kernel",
    "V_E7_RESTRICTORS": "E7 / R-CON-3: policy-root eligibility applies AP-5's restrictors",
    "V_REVOCATION_AUTHORITY": "AP-5r: restrictors removed only under the registration authority",
    "V_FC_COMPILED_QUORUM": "FC-4′: compiled first-contact quorum 2 over both sources",
    "V_FC_LINEAGE": "FC-6 / FC-7′: lineage compiled into every admitter build",
    "V_FC_EVALUATOR": "FC-1′…FC-3′ / FC-8′: evaluator selected through the authority record both sources show",
    "V_P1_NAMES_STATE": "24 §4.4: a P1 proof covers only the Trust State it names",
    "V_ENV_DIVERSITY": "R-BENV-5″: matching reproductions from two independent supplier classes",
    "V_OP9D_DIGEST": "AP-6: the digest equals the registered binary digest",
    "V_PUBLISHED": "AP-7: the selected Trust State publishes the digest",
    "V_REGISTRATION_REFERENCED": "AP-5: the registration is referenced by the selected Trust State",
    # revision 7
    "H_FCA_ROOT_THRESHOLD": "32 R-FCA-1 / FC-5′: lineage, admitter and designation fixed by the first-contact authority record at root threshold; sources refuse any other",
    "H_SOURCE_FIRST_HAND": "32 R-FCS-1…3: each source custodian derives codes from statements it verified first-hand and publishes only admissible descendants",
    "V_TS_THRESHOLD": "05 KS-17: trust-state statements need 2 of 3 dedicated keys",
    "V_DESIGNATION_OUT_OF_BAND": "32 R-FCD-1…3: the source identities come from the root ceremony and onboarding, never from a carrier or unadmitted binary",
    "V_FC_MAX_AGE": "32 FC-9: the admission state is at most 24 h old (compiled)",
    "V_READMISSION_STORE": "31 AP-R1…R6: re-admission applies the held store",
    "H_ENV_LOCK_IN_SOURCE": "33 R-BENV-2″, R-BENV-3″: the environment lock is registered source; the manifest is derived, never authored",
    "V_SUPPLIER_PINNED_KEYS": "33 R-BENV-1″: component checksums verify only under keys pinned in the root-signed supplier registry",
    "V_SUPPLIER_PROVENANCE": "33 R-BENV-5″: supplier-class independence computed from provenance, never labels",
    "V_TOOLCHAIN_DIVERSITY": "33 R-BENV-6″ / OP-10 (b): matching reproductions from two independent toolchain lineages",
    "V_FINAL_THRESHOLD_2": "05 KS-15: release-final needs 2 signatures",
}
R7 = {k: True for k in RULES}
PROFILE_R6_CONTROL_OFF = ["H_FCA_ROOT_THRESHOLD", "H_SOURCE_FIRST_HAND", "V_TS_THRESHOLD", "V_DESIGNATION_OUT_OF_BAND", "V_FC_MAX_AGE", "V_READMISSION_STORE",
                          "H_ENV_LOCK_IN_SOURCE", "V_SUPPLIER_PINNED_KEYS", "V_SUPPLIER_PROVENANCE", "V_FINAL_THRESHOLD_2"]
R6C = dict(R7, **{k: False for k in PROFILE_R6_CONTROL_OFF})
N_REP, Q = 3, 2
V = 2
CLASSES, LINEAGES = ("A", "B"), ("up", "boot")


def expand(C):
    out = set(C)
    for a in C:
        out.update(IMPLIES.get(a, ()))
    return out


# ------------------------------------------------------------------------------------------------ first contact
def seen(C, i, R):
    """The operator, reading source i as the procedure requires, sees an attacker value."""
    if R["V_DESIGNATION_OUT_OF_BAND"]:
        return ("src%d" % i) in C or ("desig%d" % i) in C
    return ("src%d" % i) in C or ("desig%d" % i) in C or "carrier" in C


def pages_agree_on_attacker_value(C, R):
    s1, s2 = seen(C, 1, R), seen(C, 2, R)
    if not R["V_FC_COMPILED_QUORUM"]:
        return s1 or s2
    return (s1 and s2) or ((s1 or s2) and "op1src" in C)


def ts_quorum(C, R):
    return len({"tsk1", "tsk2"} & C) >= (2 if R["V_TS_THRESHOLD"] else 1) or ("fcpub" in C and not R["V_TS_THRESHOLD"])


def composer_selects(C, R):
    """Revision-6 shape: the publication process composes the first-contact value the honest sources carry."""
    return "fcpub" in C and not R["H_FCA_ROOT_THRESHOLD"]


def fc_eval_sub(C, R):
    if pages_agree_on_attacker_value(C, R):
        return True
    return composer_selects(C, R)


def fc_lineage_sub(C, R):
    if R["V_FC_LINEAGE"]:
        return False
    return fc_eval_sub(C, R)


def sources_publish_thief_state(C, R, drops_revocation=False):
    """A descendant Trust State signed by the attacker reaches both sources' codes."""
    if not R["H_SOURCE_FIRST_HAND"]:
        return "fcpub" in C and (ts_quorum(C, R) or not R["V_TS_THRESHOLD"])
    if drops_revocation:
        return False                                          # custodians refuse a descendant that drops a revocation
    return ts_quorum(C, R) and "fcpub" in C


def thief_selectable(C, cfg, R):
    v = cfg["victim"]
    if v in ("P1", "ING_P1"):
        return not R["V_P1_NAMES_STATE"] and ts_quorum(C, R)
    if v == "P1A":
        return sources_publish_thief_state(C, R) or (ts_quorum(C, R) and pages_agree_on_attacker_value(C, R))
    if v in ("P2", "ING_P2"):
        return ts_quorum(C, R) and (sources_publish_thief_state(C, R) or pages_agree_on_attacker_value(C, R))
    if v == "CIR":
        return ts_quorum(C, R) and ("pinprov" in C or sources_publish_thief_state(C, R))
    if v == "USE":
        return ts_quorum(C, R)
    if v in ("FA", "RA_held", "RA_unheld"):
        return ts_quorum(C, R) and (sources_publish_thief_state(C, R) or pages_agree_on_attacker_value(C, R))
    return False


# ------------------------------------------------------------------------------------------------ release process
K_OF = {"S_good": "K_good", "S_evil": "K_evil", "S_ins": "K_ins"}


def releases(goal, C, R):
    good = {"S": "S_good", "I": "I_good", "E": "E_good", "K": "K_good", "genuine": True}
    if goal in ("G_BYTES", "G_TOOLCHAIN", "G_MIRROR", "G_REVOKED"):
        return [good]
    if goal == "G_SRC":
        out = [{"S": "S_evil", "I": "I_good", "E": "E_good", "K": "K_evil", "genuine": False}]
        if "insider" in C:
            out.append({"S": "S_ins", "I": "I_good", "E": "E_good", "K": "K_ins", "genuine": False})
        return out
    if goal == "G_INPUTS":
        return [{"S": "S_good", "I": "I_evil", "E": "E_good", "K": "K_good", "genuine": False}]
    if goal == "G_ENV":
        out = [good, {"S": "S_good", "I": "I_good", "E": "E_pipe", "K": "K_good", "genuine": False},
               {"S": "S_good", "I": "I_good", "E": "E_sub", "K": "K_good", "genuine": False},
               {"S": "S_lock", "I": "I_good", "E": "E_lock", "K": "K_lock", "genuine": False}]
        if not R["H_ENV_LOCK_IN_SOURCE"]:
            out.append({"S": "S_good", "I": "I_good", "E": "E_man", "K": "K_good", "genuine": False})
        if not R["V_SUPPLIER_PINNED_KEYS"]:
            out.append({"S": "S_good", "I": "I_good", "E": "E_key", "K": "K_good", "genuine": False})
        return out
    if goal == "G_CONTENT":
        out = [{"S": "S_good", "I": "I_good", "E": "E_good", "K": "K_weak", "genuine": False},
               {"S": "S_evil", "I": "I_good", "E": "E_good", "K": "K_evil", "genuine": False}]
        if "insider" in C:
            out.append({"S": "S_ins", "I": "I_good", "E": "E_good", "K": "K_ins", "genuine": False})
        return out
    raise ValueError(goal)


K_OF.update({"S_lock": "K_lock"})
SOURCE_SELECTED = ("S_evil", "S_ins", "S_lock")


def can_build(rel, R):
    if rel["E"] in ("E_pipe", "E_sub"):
        return not R["H_REP_ENV_REASSEMBLE"]
    return True


def build(rel, j, c, t, C, R):
    """Honest reproducer j's output in supplier class c with toolchain lineage t."""
    if t == "up":
        tc_evil = "toolchain_up" in C or "tc_src" in C
    else:
        tc_evil = ("diverse_tc" in C or "tc_src" in C) if R["V_TOOLCHAIN_DIVERSITY"] else ("toolchain_up" in C or "tc_src" in C)
    if not R["V_SUPPLIER_PROVENANCE"]:
        env_evil = "env_up_a" in C or "env_common" in C                          # class B is a relabelled class A
    else:
        env_evil = (c == "A" and "env_up_a" in C) or (c == "B" and "env_up_b" in C) or "env_common" in C
    env_evil = env_evil or rel["E"] in ("E_pipe", "E_sub", "E_man", "E_key", "E_lock")
    mirror_evil = "mirror" in C and not R["H_REP_BY_DIGEST"]
    return ("B", rel["S"], rel["I"], tc_evil, env_evil, mirror_evil)


def target(goal, rel):
    if goal in ("G_BYTES",):
        return "B_evil"
    if goal == "G_REVOKED":
        return "B_revoked"
    if goal == "G_TOOLCHAIN":
        return ("B", "S_good", "I_good", True, False, False)
    if goal == "G_ENV":
        return ("B", rel["S"] if rel["S"] != "S_lock" else "S_lock", "I_good", False, True, False)
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


def registration_routes(rel, C, R):
    proposal = rel["genuine"] or "pipeline" in C or (rel["S"] == "S_ins" and "insider" in C)
    if rel["E"] in ("E_man", "E_key"):
        proposal = "pipeline" in C
    out = []
    if proposal:
        recs_ok = all((f"vp{i}" in C) or honest_accepts(rel, R) or (not R["H_REG_RECORDS_FIRST_HAND"] and f"va{i}" in C) for i in range(1, V + 1))
        up_ok = not R["H_REG_UPSTREAM"] or (rel["I"] == "I_good" and rel["E"] != "E_sub")
        env_ok = True
        if rel["E"] in ("E_pipe", "E_sub") and R["H_REG_ENV_QUORUM"]:
            env_ok = all(f"rp{j}" in C for j in range(1, N_REP + 1))
        content_ok = not R["H_REG_CONTENT_FIRST_HAND"] or rel["K"] == K_OF.get(rel["S"], "K_good")
        if recs_ok and up_ok and env_ok and content_ok:
            rej = R["H_REG_RECORDS_FIRST_HAND"] and any(f"vp{i}" not in C and not honest_accepts(rel, R) for i in range(1, V + 1))
            out.append(("honest", True, rej))
    if {"cust1", "cust2"} <= C:
        out.append(("cust", True, False))
    if {"regk1", "regk2"} <= C:
        out.append(("key", False, False))
    return out


def final_ok(rel, C, R):
    if rel["genuine"]:
        return True
    keys = {"rfk1", "rfk2", "rck"} if R["V_FINAL_THRESHOLD_2"] else {"rfk1", "rck"}
    if keys <= C:
        return True
    proposal = "pipeline" in C or (rel["S"] == "S_ins" and "insider" in C)
    return proposal and (rel["K"] == K_OF.get(rel["S"], "K_good") or not R["H_SIGN_REPRODUCE"])


def ver_keys(rel, route, C, R):
    keys = set()
    for i in range(1, V + 1):
        if f"vp{i}" in C or f"va{i}" in C:
            keys.add(i)
        elif honest_accepts(rel, R) and (route == "honest" or rel["genuine"]):
            keys.add(i)
        elif not R["V_CANDIDATE_BINDING"] and rel["S"] == "S_good" and rel["I"] == "I_good" and rel["E"] != "E_sub":
            keys.add(i)
    return keys


def combos():
    return [(c, t) for c in CLASSES for t in LINEAGES]


def claims(rel, X, C, R, first_hand):
    """Reproduction statements visible for this release: (j, class, lineage, digest, honest)."""
    out = []
    for j in range(1, N_REP + 1):
        for c, t in combos():
            if f"rp{j}" in C:
                out.append((j, c, t, X, False))
            else:
                if first_hand and can_build(rel, R):
                    out.append((j, c, t, build(rel, j, c, t, C, R), True))
                if f"repk{j}" in C:
                    out.append((j, c, t, X, False))
    return out


def coverage_ok(matching, R):
    cls = {c for _, c, _, _, _ in matching}
    lin = {t for _, _, t, _, _ in matching}
    if R["V_ENV_DIVERSITY"] and not set(CLASSES) <= cls:
        return False
    if R["V_TOOLCHAIN_DIVERSITY"] and not set(LINEAGES) <= lin:
        return False
    return True


def custodian_digest(rel, X, C, R):
    if not R["H_REG_OWN_REPRODUCTION"] and "pipeline" in C:
        return X
    if not can_build(rel, R):
        return None
    outs = {build(rel, 0, c, t, C, R) for c, t in combos()}
    return outs.pop() if len(outs) == 1 else "CUSTODIAN_BUILDS_DISAGREE"


def published_by_owner(goal, rel, route, first_hand, rej, X, C, R):
    if not first_hand:
        return False
    vk = ver_keys(rel, route, C, R)
    if R["H_PUB_REGISTRATION_RESTRICTORS"] and not rel["genuine"] and (len(vk) < V or rej):
        return False
    if goal == "G_CONTENT":
        return True
    if len(vk) < V or rej:
        return False
    if not R["H_REP_FIRST_HAND"] and "pipeline" in C:
        conf = [(j, c, t, X) for j in range(1, N_REP + 1) for c, t in combos() if f"repk{j}" in C]
    else:
        conf = [(j, c, t, d) for (j, c, t, d, h) in claims(rel, X, C, R, True) if h or f"rp{j}" in C]
    if not conf or {d for *_, d in conf} != {X}:
        return False
    if len({j for j, *_ in conf}) < Q or not coverage_ok([(j, c, t, d, True) for j, c, t, d in conf], R):
        return False
    if R["V_OP9D_DIGEST"] and route == "honest" and custodian_digest(rel, X, C, R) != X:
        return False
    return True


def binary_accepted(goal, C, cfg, R):
    v = cfg["victim"]
    if v in ("FA", "RA_held", "RA_unheld") and (fc_lineage_sub(C, R) or fc_eval_sub(C, R)):
        return True
    thief = thief_selectable(C, cfg, R)
    withhold = "transport" in C
    ra = {"cust1", "cust2"} <= C or {"regk1", "regk2"} <= C
    for rel in releases(goal, C, R):
        X = target(goal, rel)
        if goal in ("G_SRC", "G_INPUTS") and not final_ok(rel, C, R):
            continue
        if goal == "G_ENV" and rel["S"] == "S_lock" and not final_ok(rel, C, R):
            continue
        for route, first_hand, rej in registration_routes(rel, C, R):
            pub = published_by_owner(goal, rel, route, first_hand, rej, X, C, R)
            for sel in (["honest"] if pub else []) + (["thief"] if thief else []):
                if sel == "honest" and route == "key" and R["V_REGISTRATION_REFERENCED"]:
                    continue
                vk = ver_keys(rel, route, C, R)
                if R["V_VERIFICATION_COUNT"] and len(vk) < V:
                    continue
                thief_rev = sel == "thief" and not R["V_REVOCATION_AUTHORITY"]
                if rej and R["V_REJECTED"] and not (withhold or ra or thief_rev):
                    continue
                cl = claims(rel, X, C, R, first_hand)
                matching = [x for x in cl if x[3] == X]
                if R["V_QUORUM"] and len({x[0] for x in matching}) < Q:
                    continue
                if not coverage_ok(matching, R):
                    continue
                conflicts = [x for x in cl if x[3] != X]
                if R["V_CONFLICT"] and conflicts and not (withhold or ra or thief_rev):
                    continue
                if R["V_OP9D_DIGEST"] and route == "honest" and custodian_digest(rel, X, C, R) != X:
                    continue
                return True
    return False


def revoked_admitted(C, cfg, R):
    """G_REVOKED: a binary genuinely registered, reproduced and published earlier, revoked in the newest state, is admitted."""
    v = cfg["victim"]
    if fc_eval_sub(C, R) or fc_lineage_sub(C, R):
        return True
    if v == "RA_held" and R["V_READMISSION_STORE"]:
        return "store_admin" in C and old_state_selected(C, R)
    return old_state_selected(C, R)


def old_state_selected(C, R):
    if pages_agree_on_attacker_value(C, R):
        return True
    if "win" in C:
        return True
    if "stored_old" in C and (not R["V_FC_MAX_AGE"] or "clockback" in C):
        return True
    if sources_publish_thief_state(C, R, drops_revocation=True):
        return True
    return False


def content_accepted(C, cfg, R):
    v = cfg["victim"]
    if v == "FA" and (fc_lineage_sub(C, R) or fc_eval_sub(C, R)):
        return True
    thief = thief_selectable(C, cfg, R)
    ra = {"cust1", "cust2"} <= C or {"regk1", "regk2"} <= C
    for rel in releases("G_CONTENT", C, R):
        if not final_ok(rel, C, R):
            continue
        for route, first_hand, rej in registration_routes(rel, C, R):
            pub = published_by_owner("G_CONTENT", rel, route, first_hand, rej, None, C, R)
            for sel in (["honest"] if pub else []) + (["thief"] if thief else []):
                if sel == "honest" and route == "key" and R["V_REGISTRATION_REFERENCED"]:
                    continue
                if v == "USE" and sel == "thief" and "repo" not in C:
                    continue
                if R["V_E7_RESTRICTORS"]:
                    if len(ver_keys(rel, route, C, R)) < V:
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
    if goal == "G_REVOKED":
        return revoked_admitted(C, cfg, R)
    return binary_accepted(goal, C, cfg, R)


# ------------------------------------------------------------------------------------------------ atoms per configuration
def atoms_for(goal, cfg, R=None):
    v = cfg["victim"]
    a = ["pipeline", "transport"]
    if goal in ("G_SRC", "G_INPUTS", "G_BYTES", "G_MIRROR", "G_TOOLCHAIN", "G_ENV", "G_CONTENT"):
        a += ["vp1", "vp2", "va1", "va2", "cust1", "cust2", "regk1", "regk2"]
    if goal != "G_CONTENT" and goal != "G_REVOKED":
        a += ["rp1", "rp2", "rp3", "repk1", "repk2", "repk3"]
    if goal in ("G_SRC", "G_INPUTS", "G_CONTENT", "G_ENV"):
        a += ["rck", "rfk1", "rfk2"]
    if goal in ("G_SRC", "G_CONTENT"):
        a.append("insider")
    if goal == "G_MIRROR":
        a.append("mirror")
    if goal == "G_TOOLCHAIN":
        a += ["toolchain_up", "diverse_tc", "tc_src"]
    if goal == "G_ENV":
        a += ["env_up_a", "env_up_b", "env_common"]
    if goal == "G_CONTENT":
        a.append("repo")
    if v not in ("P1",) or goal == "G_CONTENT":
        a += ["tsk1", "tsk2"]
    elif v == "P1":
        a += ["tsk1", "tsk2"]
    if v in ("P1A", "P2", "ING_P2", "CIR", "FA", "RA_held", "RA_unheld"):
        a.append("fcpub")
    if v in ("P2", "ING_P2", "FA", "RA_held", "RA_unheld", "P1A"):
        a += ["src1", "src2", "desig1", "desig2", "op1src", "carrier"]
    if v == "CIR":
        a.append("pinprov")
    if goal == "G_REVOKED":
        a += ["stored_old", "win", "clockback"]
        if v == "RA_held":
            a.append("store_admin")
    seen_, out = set(), []
    for x in a:
        if x not in seen_:
            seen_.add(x)
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


def _display(found, order):
    disp = []
    for s in found:
        implied = {b for x in s for b in IMPLIES.get(x, ())}
        disp.append(sorted((x for x in s if x not in implied), key=lambda z: order[z]))
    return [list(s) for s in sorted({tuple(s) for s in disp}, key=lambda s: (len(s), [order[x] for x in s]))]


def minimal_sets_reference(goal, cfg, R):
    """Revision-6 enumeration (transversals recomputed from scratch after every new set). Kept as the reference that
    `minimal_sets` must equal (self-check `enumeration equals reference`); quadratic in the number of minimal sets."""
    atoms = atoms_for(goal, cfg, R)
    A = frozenset(atoms)
    order = {x: i for i, x in enumerate(atoms)}
    found, failing = [], []
    if not accepted(goal, A, cfg, R):
        return {"atoms": atoms, "minimal_sets": []}
    while True:
        progress = False
        for t in minimal_transversals(found):
            if any(fl <= t for fl in failing):
                continue
            cand = A - t
            if accepted(goal, cand, cfg, R):
                cur = set(cand)
                for x in sorted(cand, key=lambda z: -order[z]):
                    if accepted(goal, frozenset(cur - {x}), cfg, R):
                        cur.discard(x)
                found.append(frozenset(cur))
                progress = True
                break
            failing.append(t)
        if not progress:
            break
    return {"atoms": atoms, "minimal_sets": _display(found, order)}


def _add_edge(T, M):
    """Minimal transversals of family ∪ {M}, from the minimal transversals T of family (Berge step, incremental)."""
    keep = [t for t in T if t & M]
    ext = sorted({t | {x} for t in T if not t & M for x in M}, key=lambda s: (len(s), sorted(s)))
    out = list(keep)
    for e in ext:
        if not any(k <= e for k in out):
            out.append(e)
    return sorted(out, key=lambda s: (len(s), sorted(s)))


def minimal_sets(goal, cfg, R):
    """Exact enumeration of the minimal accepting capability sets (monotone predicate; hypergraph dualisation). A set S is
    found by shrinking the complement of a minimal transversal t of the sets found so far; when the complement of every
    minimal transversal is refused, every minimal accepting set has been found. Revision 7 maintains the transversals
    incrementally and remembers refused complements (a transversal that stays minimal keeps its refused complement)."""
    atoms = atoms_for(goal, cfg, R)
    A = frozenset(atoms)
    order = {x: i for i, x in enumerate(atoms)}
    calls = [0]
    cache = {}

    def f(S):
        if S not in cache:
            calls[0] += 1
            cache[S] = accepted(goal, S, cfg, R)
        return cache[S]

    found = []
    if not f(A):
        return {"atoms": atoms, "minimal_sets": [], "calls": calls[0]}
    T, refused = [frozenset()], set()
    while True:
        new = None
        for t in T:
            if t in refused:
                continue
            cand = A - t
            if f(cand):
                cur = set(cand)
                for x in sorted(cand, key=lambda z: -order[z]):
                    if f(frozenset(cur - {x})):
                        cur.discard(x)
                new = frozenset(cur)
                break
            refused.add(t)
        if new is None:
            break
        found.append(new)
        T = _add_edge(T, new)
    return {"atoms": atoms, "minimal_sets": _display(found, order), "calls": calls[0]}


def monotonicity_spot_checks(goal, cfg, R, n=60, seed=7):
    atoms = atoms_for(goal, cfg, R)
    rnd = random.Random(seed + len(atoms) + len(goal))
    viol = 0
    for _ in range(n):
        S = frozenset(x for x in atoms if rnd.random() < 0.35)
        T = S | frozenset(x for x in atoms if rnd.random() < 0.3)
        if accepted(goal, S, cfg, R) and not accepted(goal, T, cfg, R):
            viol += 1
    return n, viol


# ------------------------------------------------------------------------------------------------ rendering (injective; RV6-M1)
def class_counts(s):
    counts = {}
    implied = {b for x in s for b in IMPLIES.get(x, ())}
    for a in s:
        if a in implied:
            continue
        c = ATOM_CLASS.get(a)
        if c:
            counts[c] = counts.get(c, 0) + 1
    return counts


def compact(s):
    """Render a minimal set: counts per explicit ATOM_CLASS (indices of interchangeable parties not shown); every other atom by
    its own name. A key implied by a process of the same party is not counted twice."""
    counts = class_counts(s)
    parts = ["%d %s" % (counts[c], c if counts[c] == 1 else PLURAL[c]) for c in CLASS_ORDER if c in counts]
    implied = {b for x in s for b in IMPLIES.get(x, ())}
    parts += [a for a in s if a not in ATOM_CLASS and a not in implied]
    return "{" + ", ".join(parts) + "}"


def parse_rendered(text):
    """Inverse of `compact` (used by statements_check S1 at atom-class level)."""
    inner = text.strip()[1:-1]
    counts, names = {}, []
    for tok in [t.strip() for t in inner.split(",") if t.strip()]:
        head, _, rest = tok.partition(" ")
        if head.isdigit():
            cls = rest if rest in PLURAL else next((k for k, pl in PLURAL.items() if pl == rest), None)
            if cls is None:
                return None
            counts[cls] = counts.get(cls, 0) + int(head)
        else:
            names.append(tok)
    return {"classes": counts, "atoms": sorted(names)}


def canonical(s):
    implied = {b for x in s for b in IMPLIES.get(x, ())}
    return {"classes": class_counts(s), "atoms": sorted(a for a in s if a not in ATOM_CLASS and a not in implied)}


def renderer_injective():
    """No two atoms of different classes render to the same token; no named atom equals a class word."""
    names = {a for v in ATOMS.values() for a in v if a not in ATOM_CLASS}
    words = set(PLURAL) | set(PLURAL.values())
    clash = sorted(names & words)
    tokens = {}
    for a in (x for v in ATOMS.values() for x in v):
        tok = ATOM_CLASS.get(a, a)
        tokens.setdefault(tok, set()).add(ATOM_CLASS.get(a, "named:" + a))
    merged = {t: sorted(c) for t, c in tokens.items() if len(c) > 1}
    return {"injective": not clash and not merged, "named_atoms_equal_to_class_words": clash, "tokens_with_several_classes": merged,
            "every_atom_classified_or_named": all(a in ATOM_CLASS or a in names for v in ATOMS.values() for a in v)}


def undominated(sets):
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


def uniq_render(sets):
    out = []
    for x in (compact(s) for s in sets):
        if x not in out:
            out.append(x)
    return out


NOTE_UNDOMINATED = "Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`)."


# ------------------------------------------------------------------------------------------------ invariants
def declared_fc_root():
    x1, x2 = ("src1", "desig1"), ("src2", "desig2")
    out = [sorted([a, b]) for a in x1 for b in x2] + [sorted([a, "op1src"]) for a in x1 + x2]
    return sorted(out)


def invariants(goal, cfg, sets):
    v = cfg["victim"]
    out = {}
    residual = lambda s: any(a in RESIDUAL_LABEL for a in s)
    n = lambda s, cls: sum(1 for a in s if ATOM_CLASS.get(a) == cls)
    reg_pair = lambda s: n(s, "registration custodian") + n(s, "registration key") >= 2
    ver = lambda s: len({a[-1] for a in s if ATOM_CLASS.get(a) in ("verification key", "verification process")})
    vp = lambda s: n(s, "verification process")
    rep = lambda s: len({a[-1] for a in s if ATOM_CLASS.get(a) in ("reproducer key", "reproducer process")})
    tsn = lambda s: n(s, "trust-state key")
    fc_only = lambda s: set(s) <= FC_ATOMS
    fc_victim = v in ("FA", "RA_held", "RA_unheld")
    body = [s for s in sets if not (fc_victim and fc_only(s))]
    if fc_victim and goal in ("G_BYTES", "G_REVOKED", "G_CONTENT"):
        got = sorted(sorted(s) for s in sets if fc_only(s))
        out["INV7-FC every first-contact-only minimal set is a declared first-contact root set of CP-1, and every declared set is minimal"] = {"holds": got == declared_fc_root(), "declared": declared_fc_root(), "computed": got}
    bad = [s for s in sets if "fcpub" in s and tsn(s) < 2]
    out["INV7-NO-COMPOSER the trust-state publication process never selects without two trust-state keys"] = {"holds": not bad, "counterexamples": bad}
    bad = [s for s in sets if "carrier" in s]
    out["INV7-NO-CARRIER no carrier or unadmitted binary designates sources or steps"] = {"holds": not bad, "counterexamples": bad}
    if goal == "G_REVOKED":
        if v == "FA" or v == "RA_unheld":
            bad = [s for s in body if not ("win" in s or {"stored_old", "clockback"} <= set(s))]
            out["INV7-AGE every non-root minimal set admitting a revoked binary at first admission needs a revocation within the 24 h ceiling (win) or stored codes with the clock set back"] = {"holds": not bad, "counterexamples": bad}
        if v == "RA_held":
            bad = [s for s in body if "store_admin" not in s]
            out["INV7-STORE every non-root minimal set admitting a binary the store holds as revoked needs the protected store rewritten"] = {"holds": not bad, "counterexamples": bad}
    if goal == "G_BYTES":
        bad = [s for s in body if rep(s) < Q and not residual(s)]
        out["INV-BYTES every other minimal set contains at least 2 reproducer compromises"] = {"holds": not bad, "counterexamples": bad}
    if goal in ("G_SRC", "G_INPUTS"):
        bad = [s for s in body if not residual(s) and not (ver(s) >= V and (reg_pair(s) or (goal == "G_SRC" and "pipeline" in s)))]
        out["INV-SRC every non-residual minimal set contains 2 verification compromises and (the registration threshold, or pipeline input for a malicious source)"] = {"holds": not bad, "counterexamples": bad}
    if goal == "G_ENV":
        env_res = {"env_up_a", "env_up_b"}
        bad = [s for s in body if not (env_res <= set(s) or "env_common" in s or (env_res & set(s) and rep(s) >= 1) or rep(s) >= Q or (reg_pair(s) and ver(s) >= V) or ("pipeline" in s and vp(s) >= V))]
        out["INV7-ENV every minimal set contains both supplier classes, hidden common provenance, a supplier with a reproducer compromise, 2 reproducer compromises, or source selection (registration threshold with 2 verification compromises, or pipeline with 2 verification processes)"] = {"holds": not bad, "counterexamples": bad}
        pipe = [s for s in body if set(s) <= {"pipeline", "transport", "tsk1", "tsk2", "repo", "mirror", "fcpub", "rck", "rfk1", "rfk2"}]
        out["INV7-ENV-PIPELINE the pipeline, infrastructure, trust-state and release keys never select the environment"] = {"holds": not pipe, "counterexamples": pipe}
        single = [s for s in sets if len(env_res & set(s)) == 1 and rep(s) == 0 and "env_common" not in s]
        out["INV7-ENV-B no minimal set holds one supplier class without the other class, a reproducer compromise or hidden common provenance"] = {"holds": not single, "counterexamples": single}
    if goal == "G_TOOLCHAIN":
        tcr = {"toolchain_up", "diverse_tc"}
        single = [s for s in sets if len(tcr & set(s)) == 1 and rep(s) == 0 and "tc_src" not in s]
        out["INV7-TC no minimal set holds one toolchain lineage without the other, a reproducer compromise or the compiler source"] = {"holds": not single, "counterexamples": single}
    if goal == "G_CONTENT":
        bad = [s for s in body if not residual(s) and not ((reg_pair(s) and ver(s) >= V) or ("pipeline" in s and vp(s) >= V))]
        out["INV-CONTENT every non-residual minimal set contains the registration threshold with 2 verification compromises, or pipeline input with 2 verification processes (TB-4′)"] = {"holds": not bad, "counterexamples": bad}
        weak = [s for s in body if not residual(s) and set(s) <= {"pipeline", "rck", "rfk1", "rfk2", "tsk1", "tsk2", "transport", "repo", "fcpub", "carrier", "src1", "src2", "desig1", "desig2", "op1src"}]
        out["INV-RF release-candidate and release-final keys, pipeline, trust-state keys and delivery never select content"] = {"holds": not weak, "counterexamples": weak}
    if goal == "G_MIRROR":
        bad = [s for s in body if "mirror" in s]
        out["INV-MIRROR inputs by digest: the mirror appears in no minimal set"] = {"holds": not bad, "counterexamples": bad}
    one = [s for s in body if not residual(s) and not any(a in PROCESS for a in s) and len([a for a in s if a in KEYS]) <= 1]
    out["INV-ONE no key-theft-only minimal set with at most one key (residual and first-contact root sets excepted)"] = {"holds": not one, "counterexamples": one}
    return out


# ------------------------------------------------------------------------------------------------ configurations (CP-1 only)
BIN_VICTIMS = ["P1", "P1A", "P2", "CIR", "FA"]
CONTENT_VICTIMS = ["USE", "ING_P1", "ING_P2", "FA"]


def cfg_key(goal, c):
    return "%s|CP-1|%s" % (goal, c["victim"])


def configs():
    out = []
    for victim in BIN_VICTIMS:
        for goal in ("G_SRC", "G_INPUTS", "G_BYTES", "G_MIRROR", "G_TOOLCHAIN", "G_ENV"):
            out.append((goal, {"victim": victim}))
    for victim in ("RA_held", "RA_unheld"):
        out.append(("G_BYTES", {"victim": victim}))
    for victim in CONTENT_VICTIMS:
        out.append(("G_CONTENT", {"victim": victim}))
    for victim in ("FA", "RA_held", "RA_unheld"):
        out.append(("G_REVOKED", {"victim": victim}))
    return out


def run_cfg(args):
    goal, cfg, profile = args
    R = R7 if profile == "r7" else R6C
    r = minimal_sets(goal, cfg, R)
    checks, viol = monotonicity_spot_checks(goal, cfg, R)
    res = {"goal": goal, "config": cfg, "key": cfg_key(goal, cfg), "profile": profile, "atoms": r["atoms"], "minimal_sets": r["minimal_sets"], "calls": r["calls"],
           "monotonicity_spot_checks": checks, "monotonicity_violations": viol}
    if profile == "r7":
        res["invariants"] = invariants(goal, cfg, r["minimal_sets"])
        res["labels"] = [{"set": s, "labels": [RESIDUAL_LABEL[a] for a in s if a in RESIDUAL_LABEL]} for s in r["minimal_sets"]]
    return res


def self_checks():
    ex = []

    def chk(label, goal, caps, victim, want, R=R7):
        got = accepted(goal, frozenset(caps), {"victim": victim}, R)
        ex.append({"check": label, "goal": goal, "caps": caps, "victim": victim, "profile": "r7" if R is R7 else "r6-control", "expected": want, "observed": got, "ok": got == want})

    chk("no capability", "G_BYTES", [], "FA", False)
    chk("RV6-B-H1: publication process alone at first admission (CP-1)", "G_BYTES", ["fcpub"], "FA", False)
    chk("RV6-B-H1 control: publication process composes the first-contact value (revision-6 rules)", "G_BYTES", ["fcpub"], "FA", True, R6C)
    chk("RV6-D-A01: a carrier names the sources and steps (CP-1)", "G_BYTES", ["carrier"], "FA", False)
    chk("RV6-D-A01 control (revision-6 rules)", "G_BYTES", ["carrier"], "FA", True, R6C)
    chk("first-contact root: both sources", "G_BYTES", ["src1", "src2"], "FA", True)
    chk("first-contact root: one source and the operator types it twice", "G_BYTES", ["src1", "op1src"], "FA", True)
    chk("one source alone (OP-13 (a) excluded)", "G_BYTES", ["src1"], "FA", False)
    chk("RV6-H2 D-A08: stored codes older than the ceiling (CP-1)", "G_REVOKED", ["stored_old"], "FA", False)
    chk("RV6-H2 control: stored codes of unbounded age (revision-6 rules)", "G_REVOKED", ["stored_old"], "FA", True, R6C)
    chk("RV6-H2 D-A02: re-admission over a store holding the revocation, stale codes within any age (CP-1)", "G_REVOKED", ["stored_old", "clockback"], "RA_held", False)
    chk("RV6-H2 D-A02 control (revision-6 rules)", "G_REVOKED", ["stored_old"], "RA_held", True, R6C)
    chk("CUR-R1: revocation within the 24 h ceiling (stated residual)", "G_REVOKED", ["win"], "FA", True)
    chk("RV6-B-H3: pipeline-authored environment manifest (CP-1)", "G_ENV", ["pipeline"], "P1", False)
    chk("RV6-B-H3 control (revision-6 rules)", "G_ENV", ["pipeline"], "P1", True, R6C)
    chk("RV6-B-A08: one supplier under two labels (CP-1)", "G_ENV", ["env_up_a"], "P1", False)
    chk("RV6-B-A08 control (revision-6 rules)", "G_ENV", ["env_up_a"], "P1", True, R6C)
    chk("both independent supplier classes (stated residual)", "G_ENV", ["env_up_a", "env_up_b"], "P1", True)
    chk("OP-10 (b): upstream binary toolchain alone", "G_TOOLCHAIN", ["toolchain_up"], "P1", False)
    chk("OP-10 (b): both toolchain lineages (stated residual)", "G_TOOLCHAIN", ["toolchain_up", "diverse_tc"], "P1", True)
    chk("one release-final key + candidate key + pipeline (OP-4)", "G_SRC", ["rfk1", "rck", "pipeline"], "P1", False)
    chk("two verification processes + pipeline (TB-4′, OP-8 = 2)", "G_SRC", ["vp1", "vp2", "pipeline"], "P1", True)
    chk("one verification process + pipeline (OP-8 = 2)", "G_SRC", ["vp1", "pipeline"], "P1", False)
    chk("two reproducer processes, the third honest reproducer conflicts", "G_BYTES", ["rp1", "rp2"], "P1", False)
    chk("poisoned input mirror", "G_MIRROR", ["mirror"], "P1", False)
    chk("one trust-state key + publication process, P2 (KS-17)", "G_BYTES", ["tsk1", "fcpub", "repk1", "repk2", "transport"], "P2", False)
    return ex


ENUM_REFERENCE_CONFIGS = [("G_BYTES", "P1", "r7"), ("G_BYTES", "FA", "r7"), ("G_BYTES", "RA_held", "r7"), ("G_BYTES", "CIR", "r7"), ("G_CONTENT", "USE", "r7"),
                          ("G_CONTENT", "ING_P1", "r7"), ("G_CONTENT", "ING_P2", "r7"), ("G_CONTENT", "FA", "r7"), ("G_ENV", "P1", "r7"), ("G_INPUTS", "P1", "r7"),
                          ("G_MIRROR", "CIR", "r7"), ("G_REVOKED", "FA", "r7"), ("G_REVOKED", "RA_held", "r7"), ("G_SRC", "P1", "r7"), ("G_TOOLCHAIN", "P1", "r7"),
                          ("G_TOOLCHAIN", "CIR", "r7"), ("G_TOOLCHAIN", "FA", "r7"), ("G_BYTES", "FA", "r6-control"), ("G_REVOKED", "FA", "r6-control"),
                          ("G_REVOKED", "RA_held", "r6-control"), ("G_ENV", "P1", "r6-control")]


def enumeration_reference_checks():
    """The incremental enumeration of `minimal_sets` equals the revision-6 recomputing enumeration on every configuration whose
    reference run finishes within seconds (the others time out in the reference; AR-0019 scratch timing)."""
    out = []
    for goal, victim, prof in ENUM_REFERENCE_CONFIGS:
        R = R7 if prof == "r7" else R6C
        a = minimal_sets(goal, {"victim": victim}, R)["minimal_sets"]
        b = minimal_sets_reference(goal, {"victim": victim}, R)["minimal_sets"]
        out.append({"goal": goal, "victim": victim, "profile": prof, "minimal_sets": len(a), "equal": a == b})
    return out


def mutation_analysis(pool):
    jobs = [(rule, g, c) for rule in RULES for g, c in configs()]
    res = list(pool.map(_mut_job, jobs, chunksize=4))
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
    a = minimal_sets(goal, cfg, R7)["minimal_sets"]
    b = minimal_sets(goal, cfg, dict(R7, **{rule: False}))["minimal_sets"]
    return rule, cfg_key(goal, cfg), a != b, (a, b)


def statements(results):
    by = {r["key"]: r for r in results if r["profile"] == "r7"}
    ms = lambda goal, victim: by[cfg_key(goal, {"victim": victim})]["minimal_sets"]
    blocks = {}
    fa = ms("G_BYTES", "FA")
    root = [compact(s) for s in fa if set(s) <= FC_ATOMS]
    blocks["CP-FC-ROOT"] = ("| Victim | First-contact root: minimal sets that admit a malicious first TCB with no key | Other minimal sets |\n|---|---|---|\n"
                            "| FA (first admission) | %s | %d |" % ("; ".join(root), len([s for s in fa if not set(s) <= FC_ATOMS])))
    kt = uniq_render([s for s in fa if not set(s) <= FC_ATOMS and not any(a in PROCESS for a in s)])
    blocks["CP-FC-KEY-THEFT"] = "| Victim | Key-theft minimal sets for malicious bytes at first admission |\n|---|---|\n| FA | %s |" % ("; ".join(kt) or "none")
    rows = ["| %s | %s |" % (v, "; ".join(uniq_render(undominated(ms("G_BYTES", v))))) for v in ("P1", "P1A", "P2", "CIR", "FA", "RA_held", "RA_unheld")]
    blocks["CP-BYTES"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: malicious bytes for a genuine registration (CP-1) |\n|---|---|\n" + "\n".join(rows)
    blocks["CP-SRC"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: malicious source faithfully built (CP-1) |\n|---|---|\n| P1 | %s |" % "; ".join(uniq_render(undominated(ms("G_SRC", "P1"))))
    blocks["CP-INPUTS"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: malicious named build inputs (CP-1) |\n|---|---|\n| P1 | %s |" % "; ".join(uniq_render(undominated(ms("G_INPUTS", "P1"))))
    blocks["CP-TOOLCHAIN"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: compromised toolchain (CP-1, two independent lineages) |\n|---|---|\n| P1 | %s |" % "; ".join(uniq_render(undominated(ms("G_TOOLCHAIN", "P1"))))
    blocks["CP-ENV"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: malicious build environment (CP-1, two independent supplier classes) |\n|---|---|\n| P1 | %s |\n| FA | %s |" % (
        "; ".join(uniq_render(undominated(ms("G_ENV", "P1")))), "; ".join(uniq_render(undominated([s for s in ms("G_ENV", "FA") if not set(s) <= FC_ATOMS]))))
    rows = ["| %s | %s |" % (v, "; ".join(uniq_render(undominated(ms("G_CONTENT", v))))) for v in CONTENT_VICTIMS]
    blocks["CP-CONTENT"] = NOTE_UNDOMINATED + "\n\n| Victim | Minimal sets: malicious non-orderable constitutional content effective (CP-1) |\n|---|---|\n" + "\n".join(rows)
    rows = ["| %s | %s |" % (v, "; ".join(uniq_render(ms("G_REVOKED", v)))) for v in ("FA", "RA_held", "RA_unheld")]
    blocks["CP-REVOKED"] = "| Victim | Minimal sets: a binary revoked in the newest state is admitted (CP-1) |\n|---|---|\n" + "\n".join(rows)
    return blocks


def control_statements(controls):
    by = {r["key"]: r for r in controls}
    rows = []
    for goal, victim, what in (("G_BYTES", "FA", "malicious first TCB"), ("G_REVOKED", "FA", "revoked binary at first admission"), ("G_REVOKED", "RA_held", "revoked binary at re-admission over a store holding the revocation"),
                               ("G_ENV", "P1", "malicious build environment"), ("G_BYTES", "P1A", "malicious bytes, anchor made after the compromise")):
        k = cfg_key(goal, {"victim": victim})
        if k in by:
            rows.append("| %s | %s | %s |" % (victim, what, "; ".join(uniq_render(undominated(by[k]["minimal_sets"])))))
    return ("Non-production control: the revision-7 rules %s switched off (the revision-6 shapes review r6 found). These sets are what the CP-1 rules remove; they are not options.\n\n"
            "| Victim | Goal | Minimal sets with the revision-7 rules off |\n|---|---|---|\n" % ", ".join("`%s`" % x for x in PROFILE_R6_CONTROL_OFF)) + "\n".join(rows)


def main():
    checks = self_checks()
    enum_checks = enumeration_reference_checks()
    cfgs = configs()
    with ProcessPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(run_cfg, [(g, c, "r7") for g, c in cfgs], chunksize=1))
        controls = list(pool.map(run_cfg, [(g, c, "r6-control") for g, c in cfgs], chunksize=1))
        mutations = mutation_analysis(pool)
    inv_total = sum(len(r["invariants"]) for r in results)
    inv_fail = [{"key": r["key"], "invariant": k, "detail": v} for r in results for k, v in r["invariants"].items() if not v["holds"]]
    summary = {"profile": "governance-os.rot1/CP-1", "configurations": len(results), "goals": sorted({r["goal"] for r in results}), "victim_classes": sorted({r["config"]["victim"] for r in results}),
               "self_checks": len(checks), "self_checks_ok": sum(c["ok"] for c in checks), "enumeration_reference_checks": len(enum_checks), "enumeration_reference_equal": sum(c["equal"] for c in enum_checks), "invariant_checks": inv_total, "invariant_failures": len(inv_fail),
               "monotonicity_spot_checks": sum(r["monotonicity_spot_checks"] for r in results + controls), "monotonicity_violations": sum(r["monotonicity_violations"] for r in results + controls),
               "rules": len(RULES), "rules_load_bearing_in_model": sorted(k for k, v in mutations.items() if v["load_bearing_in_model"]),
               "rules_not_load_bearing_in_model": sorted(k for k, v in mutations.items() if not v["load_bearing_in_model"]),
               "revision_6_control_configurations": len(controls), "revision_6_control_rules_off": PROFILE_R6_CONTROL_OFF, "renderer": renderer_injective()}
    stm = statements(results)
    stm["CP-R6-CONTROLS"] = control_statements(controls)
    results_bytes = json.dumps({"r7": results, "r6_control": controls}, sort_keys=True, separators=(",", ":")).encode()
    gz = os.environ.get("CS7_RESULTS_GZ")
    if gz:
        with open(gz, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as z:
                z.write(results_bytes)
    print(json.dumps({"instrument": "CS7 revision-7 derivation calculator (certified profile CP-1)", "atoms": ATOMS, "atom_class": ATOM_CLASS, "atom_description": ATOM_DESCRIPTION,
                      "rules": RULES, "summary": summary, "invariant_failures": inv_fail, "self_checks": checks, "enumeration_reference_checks": enum_checks, "mutations": mutations, "statements": stm,
                      "minimal_sets_table": {r["key"]: [" + ".join(s) for s in r["minimal_sets"]] for r in results},
                      "revision_6_control_table": {r["key"]: [" + ".join(s) for s in r["minimal_sets"]] for r in controls},
                      "results": {"count": len(results), "controls": len(controls), "sha256_of_uncompressed_json": hashlib.sha256(results_bytes).hexdigest(), "file": "CS7-results.json.gz"}},
                     indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
