#!/usr/bin/env python3
"""AR-0021 design evidence: the exact pack sentences each design-class finding rests on, extracted mechanically from the
`git archive` of d07d200, plus the decision-record state fields the handoff requires. Every check prints the matched line(s) so a
reader can verify the quote; a check whose pattern does not match is reported as NOT_FOUND (never silently true).
Usage: design7.py <export-root>   (JSON on stdout)
"""
import json, os, re, sys
import yaml
sys.dont_write_bytecode = True
X = os.path.abspath(sys.argv[1])
PK = os.path.join(X, "release/root-of-trust/4.1.6")


def lines(rel, pat, flags=0):
    p = os.path.join(X, rel) if rel.startswith(("spec/", "docs/")) else os.path.join(PK, rel)
    out = [("%s:%d" % (rel, i + 1), l.strip()[:600]) for i, l in enumerate(open(p, encoding="utf-8").read().splitlines()) if re.search(pat, l, flags)]
    return out or "NOT_FOUND"


checks = {
    "M1_absent_row_names_only_overlay_and_views": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"^\| `ABSENT`"),
    "M1_R_INIT_9": lines("09-INTEGRATION-REQUIREMENTS.md", r"^\| R-INIT-9"),
    "M1_19_s9_item6": lines("19-ELIGIBILITY-AND-SECURITY-FLOOR.md", r"^6\. \*\*RoT-1 `init` over an existing overlay"),
    "M1_19_s9_item5_pre_transaction_overlay": lines("19-ELIGIBILITY-AND-SECURITY-FLOOR.md", r"^5\. \*\*No record"),
    "M1_D0008_rule10": lines("spec/decisions/D-0008.yaml", r"\(10\) \[O6\]|RoT-1 init never runs over an existing overlay"),
    "M1_R_UPD_15_layout_migration_only_for_legacy_project": lines("09-INTEGRATION-REQUIREMENTS.md", r"^\| R-UPD-15"),
    "M1_LMI_row": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"^\| `LAYOUT_MIGRATION_INCOMPLETE`"),
    "M1_occupation_is_regular_file_governance_project": lines("26-LEGACY-BINARY-CONTAINMENT.md", r"project\s+OCCUPIED: regular file"),
    "M2_honouring_rule": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"A journal is honoured \*\*only if\*\*|project_trust_id`, repository path and locally recorded repository identity"),
    "M2_foreign_state_computed_as_if_absent": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"A foreign transaction artefact .* is reported and ignored"),
    "M2_registry_before_install_tx_and_record_update_at_end": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"open-transaction registry: TX registered|VTS per-project record updated; TX deregistered"),
    "M2_18_s5_3_phase_list": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"layout-intent`, `layout-quarantine-residue`"),
    "M2_26_s7_each_step_is_a_phase": lines("26-LEGACY-BINARY-CONTAINMENT.md", r"Each step above is a journal phase"),
    "M2_ARO_in_memory_only": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"in memory only"),
    "M2_migrations_after_exchange": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"migrations from ARO buffers"),
    "M2_crashmig7_claim_in_22": lines("22-REVIEW-RESPONSE-MATRIX.md", r"A-11 and B-11 roll forward"),
    "M3_identity_text": lines("20-ROLLBACK-AND-RECOVERY.md", r"Git common-directory identity"),
    "M3_RT_196": lines("12-ACCEPTANCE-TEST-PLAN.md", r"^\| RT-196"),
    "M3_lock_is_per_working_tree": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"flock` on `.governance-runtime/trust-tx/LOCK`|holds the exclusive lock from `prepared`"),
    "M4_R_ADM_8": lines("31-INDEPENDENT-ADMISSION.md", r"^\| \*\*R-ADM-8″\*\*"),
    "M4_store_table": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*(Protected admission store|Account verifier trust store)\*\*"),
    "M4_first_admission_moves_account_store": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"\*\*First admission\*\* is decided only"),
    "M4_pending_obligations_cleared_only_by_gates": lines("19-ELIGIBILITY-AND-SECURITY-FLOOR.md", r"cleared only by their gates"),
    "M4_AD_2_bound": lines("31-INDEPENDENT-ADMISSION.md", r"^\| \*\*AD-2′\*\*"),
    "M4_owner_OP7_high_water": lines("35-CERTIFIED-PROFILE.md", r"OP-14 \(b\)\*\* all admission records expire"),
    "M5_same_digest_reinstall_no_freshness": lines("20-ROLLBACK-AND-RECOVERY.md", r"same-digest reinstall needs no freshness"),
    "M5_RT_123": lines("12-ACCEPTANCE-TEST-PLAN.md", r"^\| RT-123"),
    "M5_C3_list_reinstall_with_another_envelope": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*C3\*\* trust ingress"),
    "M5_decision_rule_unanchored": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| `UNANCHORED` \(R-ANC-1\)|^\| `ANCHOR_EXPIRED`"),
    "M5_EX08_profile": lines("profile/CP-1.yaml", r"unanchored governed mutation|every C1–C3 row for an unanchored machine"),
    "M5_reinstall_no_gate": lines("20-ROLLBACK-AND-RECOVERY.md", r"^\| Same statement digest as the VTS per-project record"),
    "M6_order_at_process_start": lines("31-INDEPENDENT-ADMISSION.md", r"Order at process start|measures its own executable once at start"),
    "M6_VU_11_generation": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"^\| \*\*VU-11\*\*"),
    "M6_generation_tuple": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"with its generation `\(CI, TSS sequence"),
    "M6_R_USE_9": lines("09-INTEGRATION-REQUIREMENTS.md", r"^\| R-USE-9"),
    "L3_uninstall_leaves_ABSENT": lines("20-ROLLBACK-AND-RECOVERY.md", r"leaves the result `ABSENT`"),
    "L4_RT173_extension_no_override": lines("12-ACCEPTANCE-TEST-PLAN.md", r"repo-root `.gitattributes` \(no override\)"),
    "L4_member_scope": lines("26-LEGACY-BINARY-CONTAINMENT.md", r"\*\*Stated\s+condition:\*\*|\.git/info/attributes` has the highest attribute precedence"),
    "L5_clock_high_water_sources": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"the time of the anchoring event and of the currency proof in use|bootstrap.clock_reset \{reset_to, reason\}"),
    "L6_record_atomic_floors_unstated": lines("31-INDEPENDENT-ADMISSION.md", r"atomically, one file per admitted binary"),
    "L8_done_scan_scope": lines("18-VERIFY-AND-USE-TRANSACTION.md", r"\*\*Scan scope"),
}
d8 = yaml.safe_load(open(os.path.join(X, "spec/decisions/D-0008.yaml")))
d7 = yaml.safe_load(open(os.path.join(X, "spec/decisions/D-0007.yaml")))
a2 = yaml.safe_load(open(os.path.join(X, "spec/architecture/ARCH-0002.yaml")))
records = {"D-0008": {k: d8.get(k) for k in ("status", "proposal_state", "approval_state", "review_state", "in_effect", "human_approved", "revision")} | {"chosen_option_present": "chosen_option" in d8},
           "D-0007": {"status": d7.get("status")}, "ARCH-0002": {k: a2.get(k) for k in ("status", "proposal_state", "in_effect")}}
records["handoff_requirement_met"] = (d8.get("status") == "PROVISIONAL" and d8.get("proposal_state") == "PROPOSED" and d8.get("human_approved") is False and d8.get("in_effect") is False
                                      and "chosen_option" not in d8 and d7.get("status") == "ACTIVE")
nf = sorted(k for k, v in checks.items() if v == "NOT_FOUND")
print(json.dumps({"probe": "design7 (AR-0021) text evidence at d07d200", "checks": checks, "not_found": nf, "decision_records": records}, indent=1, ensure_ascii=False))
