#!/usr/bin/env python3
"""DA04r7 — would the revision-7 plan, register and instruments detect the defects found by review r6? Review r6 synthesis D's
RV6-D-A04 (AR-0018) re-expressed for revision 7 (AR-0019). Computed from committed text and instrument outputs.

Criterion (copied from RV6-D-A04 with attribution): a defect counts as detected when (a) at least one plan RT row names its
distinguishing fact, (b) the register (or, for the statement renderer, `29` §5.5) names the selector, party or field, and (c) an
executed or reference instrument output exercises it with a passing verdict. The fifteen defects are RV6-D-A04's list. Separately:
RV6-D-A04 found that RT-159, RT-162 and RT-183 had no input independent of the register; this probe checks whether their revision-7
successors (RT-184, RT-186, RT-192, RT-193) are distinguishing scenarios ([D]) whose input is held-out vectors or mutations.
Inputs: `12`, `29`, `decision-register/DECISION_REGISTER.yaml`, and the committed outputs under `evidence/r7/`.
Output: JSON on stdout.
"""
import json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.abspath(os.path.join(HERE, "..", ".."))
plan = open(os.path.join(PK, "12-ACCEPTANCE-TEST-PLAN.md")).read()
rt = {m.group(1): m.group(0) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", plan, re.M)}
regtext = open(os.path.join(PK, "decision-register", "DECISION_REGISTER.yaml")).read()
t29 = open(os.path.join(PK, "29-FACT-DERIVATION-AND-SELECTION-AUTHORITY.md")).read()


def load(rel):
    p = os.path.join(HERE, rel)
    return json.load(open(p)) if os.path.exists(p) else None


INST = {"FA7": load("FA7-first-contact-authority.json"), "CUR7": load("CUR7-first-contact-currency.json"), "ADM7": load("ADM7-admission-stores.json"),
        "ENV7": load("ENV7-environment-authority.json"), "CRASH7": load("LAY7/crashmig7.json"), "PPR7": load("PPR7-project-records.json"),
        "REGISTER-CHECK": load("REGISTER-CHECK.json"), "STATEMENTS-CHECK": load("STATEMENTS-CHECK.json"), "DA09r7": load("DA09r7-schema-fields-versus-register.json"),
        "RV6-D-A03": load("r6-probes/RV6-D-A03.json")}


def rows(*pats):
    return sorted((k for k, v in rt.items() if all(re.search(p, v, re.I) for p in pats)), key=lambda x: int(x.split("-")[1]))


def reg(pat, also29=False):
    hits = []
    if re.search(pat, regtext, re.I | re.M):
        hits.append("DECISION_REGISTER.yaml")
    if also29 and re.search(pat, t29, re.I):
        hits.append("29")
    return hits


def verdict(inst, key):
    d = INST.get(inst)
    if not d:
        return None
    v = d.get("verdicts", {}).get(key)
    return v


def ref(inst, key, expect=True):
    v = verdict(inst, key)
    return ["%s:%s" % (inst, key)] if v == expect else []


def ref_path(inst, path, expect):
    d = INST.get(inst)
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return []
        d = d[p]
    return ["%s:%s" % (inst, "/".join(path))] if d == expect else []


D = {
    "RV6-B-H1 first-contact manifest composed by the trust-state publisher": {
        "plan_rows": rows(r"First contact", r"trust-state keys"), "register": reg(r"trust-state publication process"),
        "reference": ref("FA7", "S2_P_custodians_never_publish_a_composed_or_below_threshold_authority_or_state") + ref("FA7", "S2_P_genuine_admitter_refuses_composed_codes")},
    "RV6-D-A01 source designation and procedure printed by an unadmitted binary or carrier": {
        "plan_rows": rows(r"fc-procedure|source names or steps"), "register": reg(r"designation of the two first-contact sources"),
        "reference": ref("FA7", "S2_D_one_attacker_page_disagreement_and_weakened_steps_refused") + ref("FA7", "S2_D_attacker_lineage_refused_by_genuine_admitter")},
    "RV6-B-H2 platform package submitter selects the admitter": {
        "plan_rows": rows(r"package submitter"), "register": reg(r"package submitter"), "reference": ref("FA7", "S2_X_only_b_accepted_every_other_answer_refused")},
    "RV6-B-H2 / D-A08 replayed or stored first-contact value without a mandatory age bound": {
        "plan_rows": rows(r"FIRST_CONTACT_STATE_TOO_OLD"), "register": reg(r"stored first-contact codes"),
        "reference": ref("CUR7", "A08_stored_values_older_than_ceiling_refused") + ref("CUR7", "R_replayed_old_values_refused_by_age")},
    "RV6-B-H3 environment recipe or component selection authored by an unassigned party": {
        "plan_rows": rows(r"ENVIRONMENT_MANIFEST_NOT_DERIVED"), "register": reg(r"environment manifest author"),
        "reference": ref("ENV7", "A07a_refused_before_registration") + ref("ENV7", "A07b_pipeline_selection_refused")},
    "RV6-B-H3 supplier class by label; upstream key named by the manifest": {
        "plan_rows": rows(r"two labels", r"ENVIRONMENT_COMPONENT_UNVERIFIED"), "register": reg(r"supplier provenance registry"),
        "reference": ref("ENV7", "A08_label_diversity_refused") + ref("ENV7", "A09_pinned_keys_refuse")},
    "RV6-B-M1 / D-A02 re-admission does not apply the kept store": {
        "plan_rows": rows(r"READMISSION_STATE_BELOW_HELD"), "register": reg(r"AP-R1"), "reference": ref("CUR7", "A02_store_applied") + ref("CUR7", "A04_R_ART_2_at_use")},
    "RV6-B-M2 renderer merges atoms of different classes": {
        "plan_rows": rows(r"merges atom classes"), "register": reg(r"atom level", also29=True),
        "reference": ref_path("STATEMENTS-CHECK", ["S3_renderer", "sensitivity", "mutated_renderer_detected"], True)},
    "RV6-B-M3 / D-A09 register completeness over rule ids, not inputs": {
        "plan_rows": rows(r"schema field"), "register": reg(r"^inputs:"), "reference": ref("DA09r7", "every_held_out_mutation_fails_the_register_check") + ref("DA09r7", "every_certified_schema_field_covered")},
    "RV6-C-M2 crash inside the first-install layout migration": {
        "plan_rows": rows(r"crash after each first-install layout-migration step"), "register": reg(r"CRASH7"),
        "reference": ref("CRASH7", "never_ABSENT_or_PARTIAL_after_recovery") + ref("CRASH7", "rot1_init_never_over_overlay")},
    "RV6-C-M3 per-project record identity under worktree, fork or second clone": {
        "plan_rows": rows(r"worktree", r"fork"), "register": reg(r"project_trust_id"),
        "reference": ref("PPR7", "worktree_move_bindmount_keep_E10") + ref("PPR7", "clone_and_fork_reported_fail_closed_and_never_overwrite")},
    "RV6-C-M4 a remedy re-records strength or clears a pending gate": {
        "plan_rows": rows(r"remedy", r"pending"), "register": reg(r"strength"), "reference": ref("PPR7", "remedies_keep_strength_report_and_pending_gate") + ref("PPR7", "remedy_rerecord_mutant_detected")},
    "RV6-C-M5 admission store versus account verifier trust store": {
        "plan_rows": rows(r"protected admission store"), "register": reg(r"R-STORE-2"), "reference": ref("ADM7", "A07_first_admission_decided_by_protected_store_only")},
    "RV6-D-A03 R-CON-5 listing of a new security-relevant constitutional file": {
        "plan_rows": rows(r"security_classified"), "register": reg(r"R-CON-5"),
        "reference": ["RV6-D-A03:verdicts"] if INST.get("RV6-D-A03") and INST["RV6-D-A03"].get("verdicts", {}).get("unlisted_path_change_listed_with_data_flag") is True else []},
    "RV6-D-A07 planted admission record suppresses the first-admission move-aside": {
        "plan_rows": rows(r"plants an admission record"), "register": reg(r"planted admission records"), "reference": ref("ADM7", "A07_mutant_detected")},
}
for k, v in D.items():
    v["detected"] = bool(v["plan_rows"]) and bool(v["register"]) and bool(v["reference"])
succ = {}
for r in ("RT-184", "RT-186", "RT-192", "RT-193"):
    t = rt.get(r, "")
    succ[r] = {"text": t[:300], "distinguishing": "[D]" in t, "input_is_held_out_vectors_or_mutations": bool(re.search(r"held-out|mutation|removed|merges|substituted|attacker|pipeline-supplied|planted|relabelled", t, re.I))}
out = {"probe": "DA04r7 plan regression detection for review r6 defects (AR-0019; after RV6-D-A04)", "plan_rt_rows": len(rt), "instruments_present": {k: v is not None for k, v in INST.items()},
       "defects": D, "successors_of_self_referential_tests": succ,
       "summary": {"defects": len(D), "detected": sum(v["detected"] for v in D.values()), "not_detected": [k for k, v in D.items() if not v["detected"]]}}
out["verdicts"] = {"every_review_r6_defect_detected": not out["summary"]["not_detected"],
                   "successor_tests_have_independent_inputs": all(v["distinguishing"] and v["input_is_held_out_vectors_or_mutations"] for v in succ.values())}
print(json.dumps(out, indent=1, ensure_ascii=False))
