#!/usr/bin/env python3
"""CUR7 — first-contact currency and re-admission under CP-1 (BC6-2: RV6-H2; RV6-L5) (AR-0019).

EVIDENCE ONLY. Executed: revision-7 reference executor, real Ed25519 through OpenSSL, `w7world.py`.

Re-runs, against the revision-7 rules, the executed attacks behind RV6-H2 and RV6-L5:
  R   RV6-B-A01 part R: a replayed old first-contact value (the revision-6 package shape): the T7 state, where the genuine B7 and the
      malicious B7x are published and not yet revoked, with root v2 withheld.
  A02 RV6-D-A02: re-admission over a store that holds newer state (anchor, revocations, accepted-TBM high-water, security minimum).
  A08 RV6-D-A08: stored first-contact values on media and in CI images older than the admission ceiling.
  S2  RV6-D-A01 S2: attacker-designated pages showing a genuine old state code.
  A04 RV6-B-A04 / RV6-L5: an older genuine binary below the accepted-TBM high-water at re-admission and at use (R-ART-2 in gov_run).
  W   the stated residual inside the window (CUR-R1): both sources show a state 18 h old that predates a revocation issued 6 h ago.
Each attack row has a control that shows the refusing rule is load-bearing (the rule reverted by a mutant flag).
Environment: CUR7_SCRATCH. Output: JSON on stdout.
"""
import copy, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w7world as W  # noqa: E402

GA = W.GA
SCR = tempfile.mkdtemp(prefix="cur7-", dir=os.environ["CUR7_SCRATCH"])
V = GA.Verifier(SCR)
NOW = W.NOW
acc = lambda x: isinstance(x, str) and x.startswith("ACCEPTED")


def admit(binary, fca, tss, bundle, **kw):
    return W.admit(binary, fca, tss, bundle, verifier=V, workdir=SCR, **kw)["result"]


OLD = [W.ROOT1, W.TPS1, W.FCA1, W.T5, W.T7] + W.R7.all() + W.R7X.all()       # root v2 and later states withheld
FLOORS_T11 = W.floors_from(W.T11, 2, 2, 2, {"root": 2, "policy": 1, "state": 10}, security_minimum=9)
FLOORS_T10 = W.floors_from(W.T10, 2, 1, 2, {"root": 2, "policy": 1, "state": 9})
out = {"probe": "CUR7 first-contact currency and re-admission under CP-1 (AR-0019)", "now": NOW,
       "world": {"T7_issued_at": W.T7["payload"]["issued_at"], "T10_issued_at": W.T10["payload"]["issued_at"], "T11_issued_at": W.T11["payload"]["issued_at"],
                 "B7x_revoked_at_T9": W.R7X.D in W.T9["payload"]["revocations"], "B8_revoked_at_T11": W.R8.D in W.T11["payload"]["revocations"]}}

R = {
    "R1_replayed_T7_value_malicious_B7x": admit(W.R7X.binary, W.FCA1, W.T7, OLD),
    "R2_replayed_T7_value_genuine_revoked_B7": admit(W.R7.binary, W.FCA1, W.T7, OLD),
    "R3_same_on_a_CI_image_path": admit(W.R7X.binary, W.FCA1, W.T7, OLD, path="ci-image"),
    "R4_control_rule_off_skip_state_age": admit(W.R7X.binary, W.FCA1, W.T7, OLD, flags={"skip_state_age": True}),
    "R5_control_current_codes_B7x": admit(W.R7X.binary, W.FCA2, W.T11, W.FULL),
    "R6_platform_package_route (excluded)": admit(W.R7X.binary, W.FCA1, W.T7, OLD, offered={"platform_code_signature", "compiled_first_contact_manifest"}),
}
out["R_replayed_value"] = R

A02 = {
    "readmission_T7_value_B7x_store_holds_T11": admit(W.R7X.binary, W.FCA1, W.T7, OLD, store=FLOORS_T11, flags={"skip_state_age": True}),
    "readmission_T7_value_B7x_store_holds_T11_age_rule_on": admit(W.R7X.binary, W.FCA1, W.T7, OLD, store=FLOORS_T11),
    "readmission_T10_value_B8_store_holds_T11 (within 24 h, state below held)": admit(W.R8.binary, W.FCA2, W.T10, W.FULL, store=FLOORS_T11),
    "control_readmission_ignores_store_mutant": admit(W.R8.binary, W.FCA2, W.T10, W.FULL, store=FLOORS_T11, flags={"readmission_ignores_store": True}),
    "readmission_current_T11_B9_store_T11": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, store=FLOORS_T11),
}
# held negative not listed by the selected state (a revocation the store learned from a state the attacker withholds)
fl_neg = dict(FLOORS_T10, negatives=sorted(FLOORS_T10["negatives"] + [W.R9.D]))
A02["readmission_T11_B9_store_holds_a_revocation_the_selected_state_lacks"] = admit(W.R9.binary, W.FCA2, W.T11, W.FULL, store=fl_neg)
fl_adm = dict(FLOORS_T10, negatives=sorted(FLOORS_T10["negatives"] + [W.ADM_D]))
A02["readmission_store_holds_the_admitter_revoked"] = admit(W.R9.binary, W.FCA2, W.T11, W.FULL, store=fl_adm)
fl_fca = dict(FLOORS_T10, fca_sequence=3)
A02["readmission_authority_below_held"] = admit(W.R9.binary, W.FCA2, W.T11, W.FULL, store=fl_fca)
fl_sec = dict(FLOORS_T10, security_minimum=10)
A02["readmission_release_below_held_security_minimum"] = admit(W.R9.binary, W.FCA2, W.T11, W.FULL, store=fl_sec)
out["A02_readmission_applies_store"] = A02

A08 = {
    "media_prepared_at_T7_used_now": admit(W.R7X.binary, W.FCA1, W.T7, OLD, k=2),
    "ci_image_codes_provisioned_at_T10_image_built_48h_later": admit(W.R9.binary, W.FCA2, W.T10, W.FULL, path="ci-image", now="2026-09-15T12:00:00Z"),
    "control_media_prepared_within_ceiling": admit(W.R9.binary, W.FCA2, W.T11, W.FULL, now="2026-09-14T23:00:00Z"),
    "stored_codes_with_clock_set_back (RS-2, no store)": admit(W.R7X.binary, W.FCA1, W.T7, OLD, now="2026-05-01T06:00:00Z"),
}
out["A08_stored_values"] = A08

S2 = {"designated_pages_show_genuine_T7_codes_genuine_admitter": admit(W.R7X.binary, W.FCA1, W.T7, OLD),
      "designated_pages_show_genuine_T10_codes_B8_revoked_at_T11 (within window)": admit(W.R8.binary, W.FCA2, W.T10, W.FULL)}
out["S2_designated_stale_pages"] = S2

# A04 / RV6-L5: an older genuine binary below the accepted-TBM high-water
floors_b9 = W.floors_from(W.T11, 2, 2, 2, {"root": 2, "policy": 1, "state": 10}, security_minimum=0)
A04 = {"readmission_older_genuine_R8_tbm_below_high_water (T10 state, store T10 with high-water from B9)": admit(W.R8.binary, W.FCA2, W.T10, W.FULL,
                                                                                                            store=dict(W.floors_from(W.T10, 2, 1, 2, {"root": 2, "policy": 1, "state": 10})))}
rd = os.path.join(SCR, "a04")
rec9 = GA.make_record(W.R9.D, W.TARGET, "R9", W.LINEAGE, *W.codes(W.FCA2, W.T11), W.ADM_D, NOW, "workstation")
GA.write_admission(rec9, floors_b9, rd, W.LINEAGE)
rec8 = GA.make_record(W.R8.D, W.TARGET, "R8", W.LINEAGE, *W.codes(W.FCA2, W.T10), W.ADM_D, "2026-09-10T00:00:00Z", "workstation")
os.makedirs(os.path.join(GA.protected_store(rd, W.LINEAGE), "admissions"), exist_ok=True)
json.dump(rec8, open(os.path.join(GA.protected_store(rd, W.LINEAGE), "admissions", W.R8.D.split(":", 1)[1] + ".json"), "w"))
anchor = {"class": "workstation", "anchored_at": "2026-09-14T01:00:00Z", "names_effective_state": True}
A04["rollback_to_admitted_R8_runs_C2 (R-ART-2)"] = GA.gov_run(W.R8.binary, "C2", rd, W.LINEAGE, NOW, [], [W.ADM_D], anchor=anchor)["result"]
A04["rollback_to_admitted_R8_C0_diagnostics"] = GA.gov_run(W.R8.binary, "status", rd, W.LINEAGE, NOW, [], [W.ADM_D], anchor=anchor)["result"]
A04["control_mutant_skip_r_art_2"] = GA.gov_run(W.R8.binary, "C2", rd, W.LINEAGE, NOW, [], [W.ADM_D], anchor=anchor, flags={"skip_r_art_2": True})["result"]
A04["R9_runs_C2"] = GA.gov_run(W.R9.binary, "C2", rd, W.LINEAGE, NOW, [], [W.ADM_D], anchor=anchor)["result"]
out["A04_accepted_tbm_high_water"] = A04

WIN = {"CUR-R1_first_install_both_sources_show_T10_B8_revoked_6h_ago": admit(W.R8.binary, W.FCA2, W.T10, W.FULL),
       "CUR-R1_bound_same_value_after_the_ceiling": admit(W.R8.binary, W.FCA2, W.T10, W.FULL, now="2026-09-14T13:00:00Z"),
       "CUR-R1_on_a_machine_whose_store_holds_T11": admit(W.R8.binary, W.FCA2, W.T10, W.FULL, store=FLOORS_T11)}
out["W_stated_window_residual"] = WIN

out["verdicts"] = {
    "R_replayed_old_values_refused_by_age": R["R1_replayed_T7_value_malicious_B7x"] == "FIRST_CONTACT_STATE_TOO_OLD" and R["R2_replayed_T7_value_genuine_revoked_B7"] == "FIRST_CONTACT_STATE_TOO_OLD"
                                            and R["R3_same_on_a_CI_image_path"] == "FIRST_CONTACT_STATE_TOO_OLD",
    "R_control_age_rule_load_bearing": acc(R["R4_control_rule_off_skip_state_age"]),
    "R_current_codes_refuse_B7x": not acc(R["R5_control_current_codes_B7x"]),
    "R_platform_package_route_excluded": R["R6_platform_package_route (excluded)"] == "PROFILE_MODE_EXCLUDED",
    "A02_store_applied": A02["readmission_T7_value_B7x_store_holds_T11"] == "READMISSION_STATE_BELOW_HELD" and A02["readmission_T10_value_B8_store_holds_T11 (within 24 h, state below held)"] == "READMISSION_STATE_BELOW_HELD"
                         and A02["readmission_T11_B9_store_holds_a_revocation_the_selected_state_lacks"] == "BINARY_REVOKED_IN_HELD_STATE" and A02["readmission_store_holds_the_admitter_revoked"] == "ADMITTER_REVOKED_IN_HELD_STATE"
                         and A02["readmission_authority_below_held"] == "FIRST_CONTACT_AUTHORITY_BELOW_HELD" and A02["readmission_release_below_held_security_minimum"] == "RELEASE_BELOW_SECURITY_MINIMUM",
    "A02_control_store_rule_load_bearing": acc(A02["control_readmission_ignores_store_mutant"]),
    "A02_current_value_readmission_accepted": A02["readmission_current_T11_B9_store_T11"] == "ACCEPTED",
    "A08_stored_values_older_than_ceiling_refused": A08["media_prepared_at_T7_used_now"] == "FIRST_CONTACT_STATE_TOO_OLD" and A08["ci_image_codes_provisioned_at_T10_image_built_48h_later"] == "FIRST_CONTACT_STATE_TOO_OLD",
    "A08_within_ceiling_control_accepted": A08["control_media_prepared_within_ceiling"] == "ACCEPTED",
    "A08_clock_set_back_is_the_stated_RS2_residual": acc(A08["stored_codes_with_clock_set_back (RS-2, no store)"]),
    "S2_designated_old_pages_refused_by_age": S2["designated_pages_show_genuine_T7_codes_genuine_admitter"] == "FIRST_CONTACT_STATE_TOO_OLD",
    "A04_readmission_below_high_water_refused": A04["readmission_older_genuine_R8_tbm_below_high_water (T10 state, store T10 with high-water from B9)"] == "BINARY_T0_ROLLBACK",
    "A04_R_ART_2_at_use": A04["rollback_to_admitted_R8_runs_C2 (R-ART-2)"] == "BINARY_T0_ROLLBACK" and A04["rollback_to_admitted_R8_C0_diagnostics"] == "ALLOWED" and A04["control_mutant_skip_r_art_2"] == "ALLOWED"
                        and A04["R9_runs_C2"] == "ALLOWED",
    "W_window_residual_exactly_as_stated": acc(WIN["CUR-R1_first_install_both_sources_show_T10_B8_revoked_6h_ago"]) and WIN["CUR-R1_bound_same_value_after_the_ceiling"] == "FIRST_CONTACT_STATE_TOO_OLD"
                                           and WIN["CUR-R1_on_a_machine_whose_store_holds_T11"] == "READMISSION_STATE_BELOW_HELD",
}
out["openssl_verifications"] = V.calls
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
