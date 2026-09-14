#!/usr/bin/env python3
"""FA7 — first-contact authority, excluded first-contact modes, executed minima and shared vectors under CP-1 (AR-0019).

EVIDENCE ONLY. Executed: real Ed25519 through the platform OpenSSL CLI, `sha256sum`, the revision-7 reference executor
`gov_admit_reference_r7.py`, the world `w7world.py`. Computed: CS7 loaded by path.

Sections
  S1  Honest control and the operator procedure FC-1′…FC-3′ (both sources, trust code, state code, procedure digest).
  S2  BC6-1 (RV6-H1) re-run against CP-1:
      P   RV6-B-A01 part P: the trust-state publication process composes an authority record naming a substituted admitter, or an
          attacker lineage, and hands it to both source custodians; with and without two stolen trust-state keys.
      D   RV6-D-A01 part P: the operator is directed to attacker pages (one, both, weakened steps).
      S   RV6-B-A01 part S: a platform package submitter (excluded mode).
      X   all seven revision-6 OP-13 answers and the witness-reliant runner: CP-1 implements (b); each other answer is refused by a
          named mechanism (EX-04, EX-05, EX-17, EX-18, EX-01).
  S3  Executed minimal first-contact capability sets (over src1, src2, desig1, desig2, op1src, fcpub, carrier) against CS7's FA root.
  S4  Shared vectors R1…R16 (RV5-M9 extended to CP-1).
  S5  Restrictor revocation (AP-5r) and root-lineage shapes.
  S7  Single-rule mutants of the revision-7 bootstrap rules: each must change at least one vector.
Environment: FA7_SCRATCH. Output: JSON on stdout.
"""
import copy, importlib.util, itertools, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w7world as W  # noqa: E402

GA = W.GA
SCR = tempfile.mkdtemp(prefix="fa7-", dir=os.environ["FA7_SCRATCH"])
V = GA.Verifier(SCR)
NOW, TARGET, LIN = W.NOW, W.TARGET, W.LINEAGE
st = W.to_stmts
acc = lambda x: isinstance(x, str) and x.startswith("ACCEPTED")


def admit(binary, fca, tss, bundle, **kw):
    return W.admit(binary, fca, tss, bundle, verifier=V, workdir=SCR, **kw)["result"]


def procedure(pages, fca_env, admitter):
    return GA.fc_procedure(pages, W.canon(fca_env["payload"]), admitter, TARGET, os.path.join(SCR, "plat"))["result"]


out = {"probe": "FA7 first-contact authority under CP-1 (AR-0019)", "executor_sha256": W.sha256d(W.ADMITTER_BYTES), "profile": GA.PROFILE_ID, "now": NOW}
GEN_PAGES = W.pages(W.FCA2, W.T11)

# ================================================================================================ S1
S1 = {
    "honest_workstation": admit(W.R9.binary, W.FCA2, W.T11, W.FULL),
    "honest_ci_image": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, path="ci-image"),
    "procedure_genuine": procedure(GEN_PAGES, W.FCA2, W.ADMITTER_BYTES),
    "procedure_one_source": procedure(GEN_PAGES[:1], W.FCA2, W.ADMITTER_BYTES),
    "procedure_state_codes_disagree": procedure([GEN_PAGES[0], dict(GEN_PAGES[1], state_code=W.codes(W.FCA2, W.T10)[1])], W.FCA2, W.ADMITTER_BYTES),
    "procedure_procedure_digest_disagrees": procedure([GEN_PAGES[0], dict(GEN_PAGES[1], procedure_digest=W.sha256d(b"other"))], W.FCA2, W.ADMITTER_BYTES),
    "procedure_substituted_admitter_bytes": procedure(GEN_PAGES, W.FCA2, W.SUB_ADM),
    "admission_uncertified_target": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, target=W.UNCERTIFIED_TARGET),
}
out["S1_honest_and_procedure"] = S1

# ================================================================================================ S2 P: the publication process composes
atk = W.attacker_lineage_world(admitter_digest=W.SUB_ADM_D)
FCA_TS = W.envelope("first-contact-authority+json", W.fca_payload(3, {TARGET: W.SUB_ADM_D}, root_version=2, issued="2026-09-14T00:00:00Z"), ["ts1", "ts2"])
FCA_ONE_ROOT = W.envelope("first-contact-authority+json", W.fca_payload(3, {TARGET: W.SUB_ADM_D}, root_version=2, issued="2026-09-14T00:00:00Z"), ["r1"])
FCA_ATK_LIN = atk["fca"]


def tss_naming(fca_env, signers=("ts1", "ts2"), seq=12, revs=None):
    p = copy.deepcopy(W.T11["payload"])
    return W.tss(seq, "2026-09-14T03:00:00Z", W.ROOT2, 2, W.TPS2, fca_env, W.PRIOR11 + [{"sequence": 11, "digest": W.T11["digest"]}], p["registrations"], p["published_binaries"],
                 p["revocations"] if revs is None else revs, signers=signers, revocation_statements=p["revocation_statements"])


P = {}
for label, fca_env, signers in (("authority_signed_by_two_trust_state_keys", FCA_TS, ("ts1", "ts2")), ("authority_signed_by_one_root_key", FCA_ONE_ROOT, ("ts1", "ts2")),
                                ("authority_of_attacker_lineage", FCA_ATK_LIN, ("ts1", "ts2")), ("genuine_authority_state_signed_by_one_trust_state_key", W.FCA2, ("ts1",))):
    t = tss_naming(fca_env, signers=signers)
    bundle = W.FULL + [fca_env, t] + ([atk["root1"], atk["tps"]] if fca_env is FCA_ATK_LIN else [])
    cust = GA.custodian_publish(V, st(bundle), LIN, fca_env["digest"], t["digest"], W.T11)
    row = {"source_custodian_publishes": cust["published"], "custodian_reason": cust.get("reason")}
    # what the operator then reads: the sources keep showing the genuine codes; a download host presents the substituted admitter
    row["operator_procedure_with_substituted_admitter_bytes"] = procedure(GEN_PAGES, W.FCA2, W.SUB_ADM)
    row["genuine_admitter_given_the_composed_codes_directly"] = admit(W.R9.binary, fca_env, t, bundle)
    P[label] = row
# a thief descendant that drops a held revocation (two stolen trust-state keys and the publication process)
t_drop = tss_naming(W.FCA2, revs=[r for r in W.T11["payload"]["revocations"] if r != W.R8.D])
P["two_trust_state_keys_descendant_drops_revocation"] = {"source_custodian": GA.custodian_publish(V, st(W.FULL + [t_drop]), LIN, W.FCA2["digest"], t_drop["digest"], W.T11)}
# revision-6 control: sources that carry whatever the publisher hands them, and an admitter that does not verify the authority
P["control_r6_carrying_sources_and_unverified_authority"] = {
    "substituted_evaluator_selected": procedure([{"trust_code": W.codes(FCA_TS, tss_naming(FCA_TS))[0], "state_code": W.codes(FCA_TS, tss_naming(FCA_TS))[1], "procedure_digest": W.PROCEDURE_DIGEST}] * 2, FCA_TS, W.SUB_ADM),
    "genuine_admitter_mutant_fca_unsigned_ok": admit(W.R9.binary, FCA_TS, tss_naming(FCA_TS), W.FULL + [FCA_TS, tss_naming(FCA_TS)], flags={"fca_unsigned_ok": True, "skip_evaluator_binding": True})}
out["S2_P_publication_process_composes"] = P

# ================================================================================================ S2 D: designation
atk_pages = W.pages(FCA_ATK_LIN, W.T11)
D = {
    "one_attacker_page_one_genuine_page": procedure([atk_pages[0], GEN_PAGES[1]], FCA_ATK_LIN, W.SUB_ADM),
    "weakened_steps_one_attacker_page_only": procedure(atk_pages[:1], FCA_ATK_LIN, W.SUB_ADM),
    "both_pages_attacker_substituted_evaluator (stated first-contact root: desig1+desig2)": "ACCEPTED_BY_SUBSTITUTED_EVALUATOR" if procedure(atk_pages, FCA_ATK_LIN, W.SUB_ADM) == "OK" else procedure(atk_pages, FCA_ATK_LIN, W.SUB_ADM),
    "both_pages_attacker_lineage_genuine_admitter": admit(W.R9.binary, FCA_ATK_LIN, W.T11, W.FULL + [atk["root1"], atk["tps"], FCA_ATK_LIN]),
    "genuine_admitter_one_code_typed (weakened steps)": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, k=1),
    "command_register_has_no_fc_procedure": "fc_procedure" not in [n for n in dir(GA) if n.startswith("cmd_")],
}
out["S2_D_designation"] = D

# ================================================================================================ S2 S and X: excluded answers
X = {
    "b (CP-1)": admit(W.R9.binary, W.FCA2, W.T11, W.FULL),
    "a_one_owner_source": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, k=1),
    "c_all_platform_signature_offered": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, offered={"platform_code_signature"}),
    "c_either_platform_path_only": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, k=0, offered={"platform_code_signature", "compiled_first_contact_manifest"}),
    "c_either_procedure_platform_only": GA.fc_procedure([], None, W.ADMITTER_BYTES, TARGET, os.path.join(SCR, "plat"), offered={"platform_code_signature"})["result"],
    "d_media_as_the_only_source": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, k=1),
    "WR_witness_statement_offered": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, offered={"freshness_witness"}),
    "S_package_submitter_signed_package": GA.fc_procedure(GEN_PAGES, W.canon(W.FCA2["payload"]), W.SUB_ADM, TARGET, os.path.join(SCR, "plat"), offered={"platform_code_signature"})["result"],
}
ROOT_WITNESS = W.envelope("root+json", dict(W.root_payload(1, None, W.V1_KEYS + ["wk1", "wk2"], dict(W.grants(), **{"freshness-witness": {"keys": [W.kid("wk1"), W.kid("wk2")], "threshold": 2}}))), ["r1", "r2"])
X["root_granting_freshness_witness"] = GA.root_chain(V, st([ROOT_WITNESS]), ROOT_WITNESS["digest"], {})[1]
out["S2_X_excluded_first_contact_modes"] = X

# ================================================================================================ S3 executed minima vs CS7
UNIVERSE = ["src1", "src2", "desig1", "desig2", "op1src", "fcpub", "carrier"]


def attempt(caps):
    """The strongest strategy for the capabilities. Sources show the attacker's codes only if compromised (src) or impersonated
    (desig); the operator reads both unless op1src; fcpub can hand anything to the honest custodians, who verify first-hand; a
    carrier's printed source list is not an input of the CP-1 procedure (V_DESIGNATION_OUT_OF_BAND)."""
    # composer route
    if "fcpub" in caps:
        t = tss_naming(FCA_TS)
        c = GA.custodian_publish(V, st(W.FULL + [FCA_TS, t]), LIN, FCA_TS["digest"], t["digest"], W.T11)
        if c["published"]:
            return "ACCEPTED_BY_SUBSTITUTED_EVALUATOR"
    view = []
    for i in (1, 2):
        view.append(atk_pages[0] if ("src%d" % i in caps or "desig%d" % i in caps) else GEN_PAGES[0])
    if "op1src" in caps and any(p is atk_pages[0] for p in view):
        view = [atk_pages[0], atk_pages[0]]
    admitter = W.SUB_ADM if all(p is atk_pages[0] for p in view) else W.ADMITTER_BYTES
    fca = FCA_ATK_LIN if admitter is W.SUB_ADM else W.FCA2
    r = procedure(view, fca, admitter)
    if r != "OK":
        return r
    if admitter is W.SUB_ADM:
        return "ACCEPTED_BY_SUBSTITUTED_EVALUATOR"
    return admit(W.R7X.binary, W.FCA2, W.T11, W.FULL)          # genuine admitter: the attacker's candidate is refused


accepting = []
for r_ in range(0, len(UNIVERSE) + 1):
    for sub in itertools.combinations(UNIVERSE, r_):
        if any(set(a) <= set(sub) for a in accepting):
            continue
        if acc(attempt(set(sub))):
            accepting.append(sorted(sub))
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
cs_fc = sorted(sorted(s) for s in CS7.minimal_sets("G_BYTES", {"victim": "FA"}, CS7.R7)["minimal_sets"] if set(s) <= CS7.FC_ATOMS | {"fcpub", "carrier"})
out["S3_executed_minima_vs_CS7"] = {"executed_minimal_sets": sorted(accepting), "cs7_first_contact_sets": cs_fc, "cs7_declared_root": CS7.declared_fc_root(), "equal": sorted(accepting) == cs_fc,
                                    "fcpub_in_any_executed_set": any("fcpub" in s for s in accepting), "carrier_in_any_executed_set": any("carrier" in s for s in accepting)}

# ================================================================================================ S4 shared vectors
T = W.T11


def world_variant(replace=None, add=()):
    replace = replace or {}
    return [replace.get(id(e), e) for e in W.FULL] + list(add)


def tss11(**changes):
    p = copy.deepcopy(T["payload"])
    p.update(changes)
    return W.envelope("trust-state+json", p, ["ts1", "ts2"])


R = {}
R["R0_control"] = admit(W.R9.binary, W.FCA2, T, W.FULL)
rv_final = W.envelope("revocation+json", {"revokes": [W.R9.final["digest"]], "reason": "R1"}, ["rv1", "rv2"])
t = tss11(revocations=sorted(T["payload"]["revocations"] + [W.R9.final["digest"]]), revocation_statements=T["payload"]["revocation_statements"] + [rv_final["digest"]])
R["R1_registered_final_revoked"] = admit(W.R9.binary, W.FCA2, t, W.FULL + [t, rv_final])
t = tss11(revocations=sorted(T["payload"]["revocations"] + [W.R9.cand]))
R["R2_registered_candidate_revoked"] = admit(W.R9.binary, W.FCA2, t, W.FULL + [t])
att_other = W.envelope("verification-attestation+json", dict(W.R9.atts[0]["payload"], candidate_statement_digest=W.sha256d(b"another-candidate")), ["v1"])
reg_r3 = W.R9._registration(verification_records=[att_other["digest"], W.R9.atts[1]["digest"]])
t = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_r3["digest"]])
R["R3_attestation_for_another_candidate_same_source"] = admit(W.R9.binary, W.FCA2, t, [e for e in W.FULL if e is not W.R9.reg] + [t, reg_r3, att_other])
TPS_MBV = W.envelope("trust-policy+json", W.tps_payload(version=3, min_seq=9, eligibility={"min_release_sequence": 9, "min_binary_version": "99.0.0"}), ["r1", "r2"])
t = tss11(references=dict(T["payload"]["references"], trust_policy={"version": 3, "digest": TPS_MBV["digest"]}))
R["R4_binary_below_min_binary_version"] = admit(W.R9.binary, W.FCA2, t, W.FULL + [t, TPS_MBV])
att_k = W.envelope("verification-attestation+json", dict(W.R9.atts[0]["payload"], kernel_tree_digest=W.sha256d(b"kernel-weak")), ["v1"])
reg_r5 = W.R9._registration(verification_records=[att_k["digest"], W.R9.atts[1]["digest"]])
t = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_r5["digest"]])
R["R5_attestation_other_kernel"] = admit(W.R9.binary, W.FCA2, t, [e for e in W.FULL if e is not W.R9.reg] + [t, reg_r5, att_k])
att_same = W.envelope("verification-attestation+json", dict(W.R9.atts[1]["payload"], verifier_execution_id=W.R9.atts[0]["payload"]["verifier_execution_id"],
                                                             verification_report_digest=W.R9.atts[0]["payload"]["verification_report_digest"]), ["v2"])
reg_r6 = W.R9._registration(verification_records=[W.R9.atts[0]["digest"], att_same["digest"]])
t = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_r6["digest"]])
R["R6_two_signatures_over_one_verification_execution (OP-8)"] = admit(W.R9.binary, W.FCA2, t, [e for e in W.FULL if e is not W.R9.reg] + [t, reg_r6, att_same])


def reps_variant(plan, envs=((W.ENV_A, "sup-A"), (W.ENV_B, "sup-B")), toolchains=("tc-up", "tc-boot")):
    rel = W.Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True, envs=envs, toolchains=toolchains, rep_plan=plan)
    t_ = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [rel.reg["digest"]])
    bundle = [e for e in W.FULL if e not in W.R9.all()] + rel.all() + [t_]
    return admit(rel.binary, W.FCA2, t_, bundle)


R["R7_reproductions_from_one_supplier_class"] = reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_A, "tc-boot")])
R["R8_second_class_is_a_relabelled_first_supplier"] = reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_AM, "tc-boot")], envs=((W.ENV_A, "sup-A"), (W.ENV_AM, "sup-A-mirror")))
R["R9_second_toolchain_is_a_relabelled_upstream_lineage"] = reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_B, "tc-up-relabelled")], toolchains=("tc-up", "tc-up-relabelled"))
reg_nodig = W.R9._registration(binary_digests={TARGET: W.sha256d(b"custodians-other-digest")})
t = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_nodig["digest"]])
R["R10_registered_binary_digest_differs (OP-9 (d))"] = admit(W.R9.binary, W.FCA2, t, [e for e in W.FULL if e is not W.R9.reg] + [t, reg_nodig])
t = tss11(references=dict(T["payload"]["references"], trust_policy={"version": 1, "digest": W.TPS1["digest"]}), revocations=W.T10["payload"]["revocations"],
          revocation_statements=W.T10["payload"]["revocation_statements"])
R["R11_release_below_computed_security_minimum (OP-11 (b); Trust Policy minimum 1)"] = admit(W.R8.binary, W.FCA2, t, W.FULL + [t])
R["R12_root_granting_freshness_witness"] = X["root_granting_freshness_witness"]
TPS_B = W.envelope("trust-policy+json", W.tps_payload(version=3, min_seq=9, gating={"mode": "fresh_certified_may_skip_update_gate"}), ["r1", "r2"])
t = tss11(references=dict(T["payload"]["references"], trust_policy={"version": 3, "digest": TPS_B["digest"]}))
R["R13_trust_policy_mode_B"] = admit(W.R9.binary, W.FCA2, t, W.FULL + [t, TPS_B])
g_a = W.grants(**{"release-registration": {"keys": [W.kid(x) for x in W.ROOT_KEYS], "threshold": 2}})
ROOT_2A = W.envelope("root+json", W.root_payload(1, None, W.V1_KEYS, g_a), ["r1", "r2"])
R["R14_registration_on_root_keys (OP-2 (a))"] = GA.root_chain(V, st([ROOT_2A]), ROOT_2A["digest"], {})[1]
g_f = W.grants(**{"release-final": {"keys": [W.kid("f1"), W.kid("f2")], "threshold": 1}})
ROOT_F1 = W.envelope("root+json", W.root_payload(1, None, W.V1_KEYS, g_f), ["r1", "r2"])
R["R15_release_final_threshold_1"] = GA.root_chain(V, st([ROOT_F1]), ROOT_F1["digest"], {})[1]
g_s = W.grants(**{"release-final": {"keys": [W.kid("c1"), W.kid("f2")], "threshold": 2}})
ROOT_S = W.envelope("root+json", W.root_payload(1, None, W.V1_KEYS, g_s), ["r1", "r2"])
R["R15b_candidate_and_final_share_a_key (OP-4 no)"] = GA.root_chain(V, st([ROOT_S]), ROOT_S["digest"], {})[1]
t16 = tss_naming(FCA_TS)
R["R16_authority_signed_by_trust_state_keys"] = admit(W.R9.binary, FCA_TS, t16, W.FULL + [FCA_TS, t16])
out["S4_shared_vectors"] = R

# ================================================================================================ S5 restrictors
conflict = W.R9.reproduction("p3", W.ENV_B, "tc-up", digest=W.sha256d(b"forged-other-digest"))
S5 = {"conflicting_reproduction_refuses": admit(W.R9.binary, W.FCA2, T, W.FULL + [conflict])}
t = tss11(revocations=sorted(T["payload"]["revocations"] + [conflict["digest"]]))
S5["trust_state_revocation_of_the_conflict_does_not_clear_it"] = admit(W.R9.binary, W.FCA2, t, W.FULL + [conflict, t])
rrev = W.envelope("registration-revocation+json", {"revokes": [conflict["digest"]], "reason": "forged_reproduction"}, ["g3", "g4"])
S5["registration_authority_revocation_clears_it"] = admit(W.R9.binary, W.FCA2, T, W.FULL + [conflict, rrev])
g1 = W.grants(root={"keys": [W.kid(x) for x in W.ROOT_KEYS], "threshold": 1})
ROOT_T1 = W.envelope("root+json", W.root_payload(1, None, W.V1_KEYS, g1), ["r1"])
S5["root_threshold_1"] = GA.root_chain(V, st([ROOT_T1]), ROOT_T1["digest"], {})[1]
S5["bundle_order_attacker_root_first"] = admit(W.R9.binary, W.FCA2, T, [atk["root1"], atk["tps"]] + W.FULL)
out["S5_restrictors_and_shapes"] = S5

# ================================================================================================ S7 mutants
MUT = {
    "quorum_one": lambda fl: admit(W.R9.binary, W.FCA2, T, W.FULL, k=1, flags=fl),
    "fca_unsigned_ok": lambda fl: admit(W.R9.binary, FCA_TS, t16, W.FULL + [FCA_TS, t16], flags=dict(fl, skip_evaluator_binding=True)),
    "skip_evaluator_binding": lambda fl: admit(W.R9.binary, W.FCA2, T, W.FULL, evaluator=W.SUB_ADM_D, flags=fl),
    "skip_fca_state_binding": lambda fl: admit(W.R9.binary, W.FCA1, T, W.FULL, flags=fl),
    "trust_state_threshold_1": lambda fl: (lambda t1: admit(W.R9.binary, W.FCA2, t1, W.FULL + [t1], flags=fl))(tss_naming(W.FCA2, signers=("ts1",))),
    "skip_state_age": lambda fl: admit(W.R9.binary, W.FCA2, T, W.FULL, now="2026-09-16T06:00:00Z", flags=fl),
    "supplier_class_by_label": lambda fl: admit(*_r8(), flags=fl) if False else _variant_flag(fl, "R8"),
    "toolchain_class_by_label": lambda fl: _variant_flag(fl, "R9tc"),
    "count_attestation_signatures": lambda fl: admit(W.R9.binary, W.FCA2, tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_r6["digest"]]),
                                                     [e for e in W.FULL if e is not W.R9.reg] + [tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg_r6["digest"]]), reg_r6, att_same], flags=fl),
    "skip_security_minimum": lambda fl: (lambda t_: admit(W.R8.binary, W.FCA2, t_, W.FULL + [t_], flags=fl))(tss11(references=dict(T["payload"]["references"], trust_policy={"version": 1, "digest": W.TPS1["digest"]}), revocations=W.T10["payload"]["revocations"],
                                                                                                                  revocation_statements=W.T10["payload"]["revocation_statements"])),
    "skip_verification_environment": lambda fl: _env_mismatch(fl),
}


def _r8():
    return ()


def _variant_flag(fl, which):
    if which == "R8":
        rel = W.Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True, envs=((W.ENV_A, "sup-A"), (W.ENV_AM, "sup-A-mirror")),
                        rep_plan=[("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_AM, "tc-boot")])
    else:
        rel = W.Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True, toolchains=("tc-up", "tc-up-relabelled"),
                        rep_plan=[("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_B, "tc-up-relabelled")])
    t_ = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [rel.reg["digest"]])
    return admit(rel.binary, W.FCA2, t_, [e for e in W.FULL if e not in W.R9.all()] + rel.all() + [t_], flags=fl)


def _env_mismatch(fl):
    a0 = W.envelope("verification-attestation+json", dict(W.R9.atts[0]["payload"], environment_ids=[W.ENV_A]), ["v1"])
    reg = W.R9._registration(verification_records=[a0["digest"], W.R9.atts[1]["digest"]])
    t_ = tss11(registrations=[d for d in T["payload"]["registrations"] if d != W.R9.reg["digest"]] + [reg["digest"]])
    return admit(W.R9.binary, W.FCA2, t_, [e for e in W.FULL if e is not W.R9.reg] + [t_, reg, a0], flags=fl)


S7 = {}
for flag, fn in MUT.items():
    base, mut = fn({}), fn({flag: True})
    S7[flag] = {"base": base, "mutant": mut, "detected": base != mut}
out["S7_revision_7_rule_mutants"] = S7

# ================================================================================================ verdicts
out["verdicts"] = {
    "S1_honest_accepted_both_path_classes": S1["honest_workstation"] == "ACCEPTED" and S1["honest_ci_image"] == "ACCEPTED",
    "S1_procedure_refusals": S1["procedure_genuine"] == "OK" and S1["procedure_one_source"] == "FIRST_CONTACT_SOURCES_BELOW_QUORUM" and S1["procedure_state_codes_disagree"] == "FIRST_CONTACT_DISAGREEMENT"
                             and S1["procedure_procedure_digest_disagrees"] == "FIRST_CONTACT_DISAGREEMENT" and S1["procedure_substituted_admitter_bytes"] == "ADMITTER_DIGEST_MISMATCH"
                             and S1["admission_uncertified_target"] == "TARGET_NOT_CERTIFIED",
    "S2_P_custodians_never_publish_a_composed_or_below_threshold_authority_or_state": all(not r["source_custodian_publishes"] for k, r in P.items() if "source_custodian_publishes" in r),
    "S2_P_descendant_dropping_revocation_not_published": not P["two_trust_state_keys_descendant_drops_revocation"]["source_custodian"]["published"],
    "S2_P_genuine_admitter_refuses_composed_codes": all(not acc(r["genuine_admitter_given_the_composed_codes_directly"]) for r in P.values() if "genuine_admitter_given_the_composed_codes_directly" in r),
    "S2_P_control_r6_shape_admits": P["control_r6_carrying_sources_and_unverified_authority"]["substituted_evaluator_selected"] == "OK",
    "S2_D_one_attacker_page_disagreement_and_weakened_steps_refused": D["one_attacker_page_one_genuine_page"] == "FIRST_CONTACT_DISAGREEMENT" and D["weakened_steps_one_attacker_page_only"] == "FIRST_CONTACT_SOURCES_BELOW_QUORUM"
                                                                      and D["genuine_admitter_one_code_typed (weakened steps)"] == "FIRST_CONTACT_SOURCES_BELOW_QUORUM",
    "S2_D_attacker_lineage_refused_by_genuine_admitter": not acc(D["both_pages_attacker_lineage_genuine_admitter"]),
    "S2_X_only_b_accepted_every_other_answer_refused": X["b (CP-1)"] == "ACCEPTED" and all(not acc(v) and v != "OK" for k, v in X.items() if k != "b (CP-1)"),
    "S3_executed_minima_equal_CS7": out["S3_executed_minima_vs_CS7"]["equal"] and not out["S3_executed_minima_vs_CS7"]["fcpub_in_any_executed_set"] and not out["S3_executed_minima_vs_CS7"]["carrier_in_any_executed_set"],
    "S4_every_vector_refused_control_accepted": R["R0_control"] == "ACCEPTED" and all(not acc(v) and v is not None for k, v in R.items() if k != "R0_control"),
    "S5_restrictors": S5["conflicting_reproduction_refuses"] == "REPRODUCTION_CONFLICT" and S5["trust_state_revocation_of_the_conflict_does_not_clear_it"] == "REPRODUCTION_CONFLICT"
                      and S5["registration_authority_revocation_clears_it"] == "ACCEPTED" and S5["bundle_order_attacker_root_first"] == "ACCEPTED" and S5["root_threshold_1"] is not None,
    "S7_every_mutant_detected": all(v["detected"] for v in S7.values()),
}
out["openssl_verifications"] = V.calls
txt = json.dumps(out, indent=1, sort_keys=True, default=str)
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", txt))
