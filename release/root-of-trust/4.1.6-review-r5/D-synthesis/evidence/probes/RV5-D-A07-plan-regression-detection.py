#!/usr/bin/env python3
"""RV5-D-A07 — can the implementation plan detect the defects found in this review? (review r5 synthesis D, AR-0014)

For each defect confirmed by this review, the probe asks whether an implementation that carries it would fail any
acceptance test of `12-ACCEPTANCE-TEST-PLAN.md` as written, or the mechanical instruments the plan names (RT-128 decision
register rows of `29` §4; RT-131 derivation calculator on its own honest-party model; RT-134/RT-135 shapes of the P4r5 and
FA5 oracles; RT-138; RT-139). Computed from the committed text and instruments: the calculator module (`CS5`) is loaded
unmodified and its goals and atoms are read; plan rows and register rows are matched by the facts each defect needs.

Environment: REVIEW_REPO (export of cdb4e14). Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
spec = importlib.util.spec_from_file_location("cs5", os.path.join(PK, "evidence", "r5", "CS5-tcb-capability-sets.py"))
CS5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS5)
plan = open(os.path.join(PK, "12-ACCEPTANCE-TEST-PLAN.md")).read()
reg = open(os.path.join(PK, "29-FACT-DERIVATION-AND-SELECTION-AUTHORITY.md")).read()
rt = {m.group(1): m.group(0) for m in re.finditer(r"^\| (RT-\d+)[^\n]*", plan, re.M)}
register_rows = re.findall(r"^\| \*\*?[^|]*\|[^\n]*", reg.split("## 4. Decision register")[1].split("## 5.")[0], re.M)


def rows_matching(*pats):
    return sorted(k for k, v in rt.items() if all(re.search(p, v, re.I) for p in pats))


goals = sorted(CS5.GOAL_ATOMS)
atoms = sorted({a for v in CS5.GOAL_ATOMS.values() for a in v})
defects = {
    "RV5-H1 channel shows an attacker lineage's fingerprint (FA)": {
        "calculator_can_express": "H-CH: 'ch_k shows t_x's' (a descendant in the genuine lineage) only" if "ch_k" in CS5.__doc__ else None,
        "plan_rows_naming_fact": rows_matching(r"attacker lineage"),
        "note": "RT-135 names 'attacker lineage' from FA5 CH2, where the genuine fingerprint is typed (refused); no row types the attacker lineage's fingerprint",
        "register_row_for_lineage_or_evaluator_selection": [r for r in register_rows if re.search(r"lineage|evaluator", r, re.I)],
    },
    "RV5-H2 build image selects bytes": {
        "calculator_goal_or_atom_for_image": [x for x in goals + atoms if "image" in x],
        "plan_rows_substituting_image": rows_matching(r"image", r"substitut|malicious|swap"),
        "register_row_for_image_record": [r for r in register_rows if re.search(r"image", r, re.I)],
    },
    "RV5-H3 registered constitutional content not established first-hand": {
        "calculator_goal_for_constitutional_content": [g for g in goals if re.search(r"CONTENT|POLICY|UNIT|KERNEL", g)],
        "plan_rows_final_or_candidate_kernel_differs_from_verified_source": rows_matching(r"candidate", r"kernel|unit", r"verif"),
        "plan_rows_first_hand_unit_map": rows_matching(r"unit map|derive-registration|first-hand"),
        "register_selector_row": [r for r in register_rows if "Policy root eligibility" in r],
    },
    "RV5-D-A04 R1/R2 revoked registered final or candidate at admission": {
        "plan_rows": rows_matching(r"gov-admit|verify-artifact", r"revok", r"final|candidate"),
    },
    "RV5-D-A04 R3 ACCEPTED attestation for another candidate": {
        "plan_rows": rows_matching(r"attestation", r"another candidate|different candidate|other candidate"),
    },
    "RV5-D-A04 R4 min_binary_version at admission": {
        "plan_rows": rows_matching(r"min_binary_version"),
    },
    "RV5-D-A03 user-writable install reachable classes": {
        "RT-138_expected": rt.get("RT-138"),
    },
    "RV5-B-M3 re-admission discards the store": {
        "RT-139_expected": rt.get("RT-139"),
        "plan_rows_re_admission": rows_matching(r"re-admission|re-run .*gov-admit|second admission"),
    },
}
p4r5_ids = sorted(json.load(open(os.path.join(PK, "evidence", "r5", "P4r5-conformance-oracle.json")))["scenarios"])
fa5_src = open(os.path.join(PK, "evidence", "r5", "FA5-first-admission.py")).read()
defects["RV5-H1 channel shows an attacker lineage's fingerprint (FA)"].update({
    "register_rows_naming_lineage_selection": [r for r in register_rows if re.search(r"lineage", r, re.I)],
    "register_rows_naming_channel_quorum": [r for r in register_rows if re.search(r"channel.quorum|quorum of channels", r, re.I)],
    "FA5_rows_typing_an_attacker_lineage_fingerprint": re.findall(r'run\("(CH2[^"]*)"', fa5_src),
    "FA5_CH2_types_genuine_fingerprint": bool(re.search(r'r_ch2 = run\("CH2", B8x_BYTES, \[FP10, FP10\]', fa5_src)),
})
defects["RV5-D-A04 R1/R2 revoked registered final or candidate at admission"].update({
    "P4r5_rows_revoking_registered_final": [i for i in p4r5_ids if re.search(r"final_revoked", i)],
    "P4r5_rows_revoking_registered_candidate": [i for i in p4r5_ids if re.search(r"candidate_revoked", i)],
    "FA5_revokes_final_or_candidate": bool(re.search(r"revocations\"\s*:\s*[^\n]*(FINAL\d|CAND\d)", fa5_src)),
    "note": "keyword rows RT-92 (revision-4 artefact matrix), RT-134 (P4r5 shapes) and RT-135 (FA5 shapes) are matched by words only; their shape sources are listed above",
})
defects["RV5-H3 registered constitutional content not established first-hand"]["note"] = "RT-115 is the revision-4 source-identity row (a final naming another source); it does not vary the kernel under an identical source"
verdicts = {
    "H1_undetectable_by_plan": not defects["RV5-H1 channel shows an attacker lineage's fingerprint (FA)"]["register_rows_naming_lineage_selection"]
        and not defects["RV5-H1 channel shows an attacker lineage's fingerprint (FA)"]["register_rows_naming_channel_quorum"]
        and defects["RV5-H1 channel shows an attacker lineage's fingerprint (FA)"]["FA5_CH2_types_genuine_fingerprint"],
    "A04_R1_final_revocation_untested_in_both_oracles": not defects["RV5-D-A04 R1/R2 revoked registered final or candidate at admission"]["P4r5_rows_revoking_registered_final"]
        and not defects["RV5-D-A04 R1/R2 revoked registered final or candidate at admission"]["FA5_revokes_final_or_candidate"],
    "A04_R2_candidate_revocation_untested_in_bootstrap_oracle": not defects["RV5-D-A04 R1/R2 revoked registered final or candidate at admission"]["FA5_revokes_final_or_candidate"],
    "H2_undetectable_by_plan": not defects["RV5-H2 build image selects bytes"]["calculator_goal_or_atom_for_image"] and not defects["RV5-H2 build image selects bytes"]["plan_rows_substituting_image"],
    "H3_undetectable_by_plan": not defects["RV5-H3 registered constitutional content not established first-hand"]["calculator_goal_for_constitutional_content"]
        and not defects["RV5-H3 registered constitutional content not established first-hand"]["plan_rows_first_hand_unit_map"],
    "A04_R4_min_binary_version_untested": not defects["RV5-D-A04 R4 min_binary_version at admission"]["plan_rows"],
    "A04_R3_untested": not defects["RV5-D-A04 R3 ACCEPTED attestation for another candidate"]["plan_rows"],
    "A03_RT138_expects_unreachable_outcome": bool(re.search(r"C0–C2 still available", rt.get("RT-138", ""))),
    "M3_no_re_admission_row": not defects["RV5-B-M3 re-admission discards the store"]["plan_rows_re_admission"],
}
print(json.dumps({"probe": "RV5-D-A07 plan regression detection (AR-0014)", "calculator_goals": goals, "calculator_atoms": atoms,
                  "plan_rt_rows": len(rt), "register_rows_in_29_s4": len(register_rows), "defects": defects, "verdicts": verdicts}, indent=1))
