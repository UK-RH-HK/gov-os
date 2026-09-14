#!/usr/bin/env python3
"""ADM7 — admission stores, records and the OP-7 (a) decision rule under CP-1 (RV6-M6, RV6-L9, RV6-D-A07; OP-14 (b), OP-15 (a),
OP-12 (a) exclusions) (AR-0019). Scratch only.

Against `gov_admit_reference_r7.py`:
  A07  RV6-D-A07: same-account code plants, before a genuine first admission, an admission record, an anchor, a per-project record and a
       trust-gate confirmation in the account verifier trust store. First admission is decided by the protected admission store only;
       the account store is moved aside. Mutant `first_admission_from_account_store` (the revision-6 reading).
  A08  crash between install-from-buffer and the record: C0 only.
  A09  re-admission keeps both stores; floors never decrease (a lower floor written later changes nothing).
  A11  eight concurrent first admissions of one lineage: one protected-store marker; every record present; the account store moved aside at
       most once.
  A15  records outside the protected store (beside the binary; in the account store; in a moved-aside store) are not honoured.
  EX02 a record naming an admitter the authority record does not list (helper machine, script): RECORD_ADMITTER_NOT_LISTED.
  L9   store names use the full 64-hex lineage; a record of another lineage is not honoured for this lineage.
  X14  OP-14 (b): workstation records expire after 90 days, CI image records after 7 days.
  X15  OP-15 (a): a revoked genuine binary runs C0-R diagnostics only.
  X7   OP-7 (a): unanchored -> C0; workstation anchor 90 d, CI anchor 7 d; C3 needs currency within 24 h; a user-writable executable never
       reaches C3 or ceremonies.
Attribution: question shapes follow reviewer C `admtx6.py` (AR-0017) and the synthesis's RV6-D-A07 (AR-0018); code re-typed.
Environment: ADM7_SCRATCH. Output: JSON on stdout.
"""
import json, os, re, sys, tempfile, threading

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gov_admit_reference_r7 as GA  # noqa: E402

S = tempfile.mkdtemp(prefix="adm7-", dir=os.environ["ADM7_SCRATCH"])
LIN = "sha256:" + "7" * 64
OTHER_LIN = "sha256:" + "8" * 64
NOW = "2026-09-14T06:00:00Z"
ADM = "sha256:" + "a" * 64
TARGET = "x86_64-unknown-linux-musl"
BIN1, BIN2 = b"#!/bin/sh\n# gov r1\n", b"#!/bin/sh\n# gov r2\n"
D1, D2 = GA.sha256d(BIN1), GA.sha256d(BIN2)
FLOORS = {"state_sequence": 11, "state_digest": "sha256:" + "b" * 64, "root_version": 2, "policy_version": 2, "fca_sequence": 2, "negatives": [], "accepted_tbm": {"root": 2, "policy": 1, "state": 10},
          "security_minimum": 9}
ANCH = lambda cls, at, cur=None: {"class": cls, "anchored_at": at, "names_effective_state": True, "currency_at": cur or at}
res = {}


def rec(d, now=NOW, path="workstation", admitter=ADM, kind="compiled-gov-admit", lineage=LIN):
    r = GA.make_record(d, TARGET, "R", lineage, "gov-fct:x", "gov-fcs:y", admitter, now, path)
    r["admitter_kind"] = kind
    return r


def plant_account_store(root):
    acc = GA.account_store(root, LIN)
    for sub in ("admissions", "projects", "confirmations"):
        os.makedirs(os.path.join(acc, sub), exist_ok=True)
    json.dump(rec(D2), open(os.path.join(acc, "admissions", "planted.json"), "w"))
    json.dump([{"sequence": 5, "digest": "sha256:" + "5" * 64, "method": "human"}], open(os.path.join(acc, "anchors.json"), "w"))
    json.dump({"strength": "weak"}, open(os.path.join(acc, "projects", "P1.json"), "w"))
    json.dump({"gate_kind": "framework_update"}, open(os.path.join(acc, "confirmations", "c1.json"), "w"))
    return acc


# A07
for label, flags in (("r7", {}), ("mutant_first_admission_from_account_store (revision-6 reading)", {"first_admission_from_account_store": True})):
    root = os.path.join(S, "a07-" + re.sub(r"\W+", "_", label))
    acc = plant_account_store(root)
    first = GA.is_first_admission(root, LIN, flags)
    w = GA.write_admission(rec(D1), FLOORS, root, LIN, flags)
    res["A07_planted_account_record_" + label] = {"is_first_admission": first, "account_store_moved_aside": w["account_store_moved_aside"] is not None,
                                                  "planted_anchor_survives_in_account_store": os.path.exists(os.path.join(acc, "anchors.json")),
                                                  "planted_project_record_survives": os.path.exists(os.path.join(acc, "projects", "P1.json")),
                                                  "planted_confirmation_survives": os.path.exists(os.path.join(acc, "confirmations", "c1.json"))}
# A08
root = os.path.join(S, "a08")
inst = GA.install_from_buffer(BIN1, os.path.join(root, "bin", "gov"), D1) if hasattr(GA, "install_from_buffer") else None
res["A08_installed_without_record"] = {"C0_status": GA.gov_run(BIN1, "status", root, LIN, NOW, [], [ADM])["result"], "C1": GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"]}
# A09
root = os.path.join(S, "a09")
GA.write_admission(rec(D1), FLOORS, root, LIN)
lower = dict(FLOORS, state_sequence=5, root_version=1, security_minimum=1, negatives=["sha256:" + "c" * 64])
w2 = GA.write_admission(rec(D2), lower, root, LIN)
fl = GA.read_floors(root, LIN)
res["A09_readmission"] = {"first_admission_second_run": w2["first_admission"], "both_records": sorted(os.listdir(os.path.join(GA.protected_store(root, LIN), "admissions"))),
                          "floors_after_lower_write": {k: fl[k] for k in ("state_sequence", "root_version", "security_minimum")}, "negatives_union": fl["negatives"]}
# A11
root = os.path.join(S, "a11")
plant_account_store(root)
errors, results = [], []


def one(i):
    try:
        results.append(GA.write_admission(rec(GA.sha256d(b"bin-%d" % i)), FLOORS, root, LIN))
    except Exception as e:  # noqa: BLE001
        errors.append(repr(e))


th = [threading.Thread(target=one, args=(i,)) for i in range(8)]
[t.start() for t in th]
[t.join() for t in th]
ps = GA.protected_store(root, LIN)
res["A11_concurrent_first_admissions"] = {"errors": errors, "first_admission_count": sum(1 for r in results if r["first_admission"]), "records": len(os.listdir(os.path.join(ps, "admissions"))),
                                          "account_store_moved_aside_count": sum(1 for r in results if r["account_store_moved_aside"]), "markers": int(os.path.isfile(os.path.join(ps, "admission-store.json")))}
# A15
root = os.path.join(S, "a15")
os.makedirs(os.path.join(root, "bin"), exist_ok=True)
json.dump(rec(D1), open(os.path.join(root, "bin", "admission-beside-binary.json"), "w"))
acc = GA.account_store(root, LIN)
os.makedirs(os.path.join(acc, "admissions"), exist_ok=True)
json.dump(rec(D1), open(os.path.join(acc, "admissions", D1.split(":", 1)[1] + ".json"), "w"))
moved = GA.protected_store(root, LIN) + ".pre-admission-0"
os.makedirs(os.path.join(moved, "admissions"), exist_ok=True)
json.dump(rec(D1), open(os.path.join(moved, "admissions", D1.split(":", 1)[1] + ".json"), "w"))
res["A15_records_outside_protected_store"] = GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"]
# EX02 / EX03 / L9
root = os.path.join(S, "ex02")
GA.write_admission(rec(D1, admitter="sha256:" + "d" * 64), FLOORS, root, LIN)
res["EX02_helper_machine_admitter_not_listed"] = GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"]
root = os.path.join(S, "ex03")
GA.write_admission(rec(D1, kind="auditable-script"), FLOORS, root, LIN)
res["EX03_script_admission_record"] = GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"]
root = os.path.join(S, "l9")
GA.write_admission(rec(D1, lineage=OTHER_LIN), FLOORS, root, OTHER_LIN)
res["L9_store_name_is_full_lineage"] = {"protected_store_basename_length": len(os.path.basename(GA.protected_store(root, LIN))),
                                        "record_of_other_lineage_for_this_lineage": GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"]}
# X14, X15, X7
root = os.path.join(S, "x")
GA.write_admission(rec(D1, now="2026-09-01T00:00:00Z", path="ci-image"), FLOORS, root, LIN)
GA.write_admission(rec(D2, now="2026-06-01T00:00:00Z", path="workstation"), FLOORS, root, LIN)
res["X14_record_expiry"] = {"ci_image_record_13_days_old": GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("ci-image", NOW))["result"],
                            "workstation_record_105_days_old": GA.gov_run(BIN2, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW))["result"],
                            "workstation_record_within_90_days": (lambda r: (GA.write_admission(rec(D2, now="2026-06-01T00:00:00Z", path="workstation"), FLOORS, r, LIN),
                                                                             GA.gov_run(BIN2, "C1", r, LIN, "2026-08-20T00:00:00Z", [], [ADM], anchor=ANCH("workstation", "2026-08-19T00:00:00Z"))["result"])[1])(os.path.join(S, "x14b"))}
root = os.path.join(S, "x15")
GA.write_admission(rec(D1), FLOORS, root, LIN)
res["X15_revoked_self"] = {a: GA.gov_run(BIN1, a, root, LIN, NOW, [D1], [ADM], anchor=ANCH("workstation", NOW))["result"] for a in ("status", "doctor", "trust-show", "C1", "C2", "C3", "trust-refresh", "confirm-state")}
res["X7_decision_rule"] = {
    "unanchored_C1": GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM])["result"],
    "workstation_anchor_89d_C2": GA.gov_run(BIN1, "C2", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", "2026-06-17T06:00:00Z"))["result"],
    "workstation_anchor_91d_C2": GA.gov_run(BIN1, "C2", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", "2026-06-15T06:00:00Z"))["result"],
    "ci_anchor_8d_C1": GA.gov_run(BIN1, "C1", root, LIN, NOW, [], [ADM], anchor=ANCH("ci-image", "2026-09-06T06:00:00Z"))["result"],
    "C3_currency_23h": GA.gov_run(BIN1, "C3", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", "2026-09-10T06:00:00Z", "2026-09-13T07:00:00Z"))["result"],
    "C3_currency_25h": GA.gov_run(BIN1, "C3", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", "2026-09-10T06:00:00Z", "2026-09-13T05:00:00Z"))["result"],
    "C3_user_writable_executable": GA.gov_run(BIN1, "C3", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW), protected=False)["result"],
    "confirm_state_user_writable_executable": GA.gov_run(BIN1, "confirm-state", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW), protected=False)["result"],
    "C2_user_writable_executable_anchored": GA.gov_run(BIN1, "C2", root, LIN, NOW, [], [ADM], anchor=ANCH("workstation", NOW), protected=False)["result"],
}
# CLK — R-CLK-1 (24 §4.5): a clock earlier than the machine's own recorded high water leaves C0-R only (BA11r7 CLOCK-back rows)
root = os.path.join(S, "clk")
GA.write_admission(rec(D1), FLOORS, root, LIN)
BACK = "2025-08-15T06:00:00Z"
res["CLK_clock_below_high_water"] = {
    "C1_clock_set_back_395_days": GA.gov_run(BIN1, "C1", root, LIN, BACK, [], [ADM], anchor=ANCH("workstation", "2026-09-10T06:00:00Z"))["result"],
    "C2_clock_set_back_anchor_claims_older_time": GA.gov_run(BIN1, "C2", root, LIN, BACK, [], [ADM], anchor=ANCH("workstation", "2025-08-14T06:00:00Z"))["result"],
    "status_clock_set_back": GA.gov_run(BIN1, "status", root, LIN, BACK, [], [ADM], anchor=ANCH("workstation", NOW))["result"],
    "C1_clock_within_skew_of_high_water": GA.gov_run(BIN1, "C1", root, LIN, "2026-09-14T05:57:00Z", [], [ADM], anchor=ANCH("workstation", "2026-09-10T06:00:00Z"))["result"],
    "mutant_skip_clock_high_water_C1_clock_set_back": GA.gov_run(BIN1, "C1", root, LIN, BACK, [], [ADM], anchor=ANCH("workstation", "2025-08-14T06:00:00Z"), flags={"skip_clock_high_water": True})["result"],
}
R = res
res_v = {
    "CLK_clock_below_high_water_C0_R_only": R["CLK_clock_below_high_water"] == {"C1_clock_set_back_395_days": "TRUST_CLOCK_BELOW_HIGH_WATER", "C2_clock_set_back_anchor_claims_older_time": "TRUST_CLOCK_BELOW_HIGH_WATER",
                                                                               "status_clock_set_back": "ALLOWED", "C1_clock_within_skew_of_high_water": "ALLOWED",
                                                                               "mutant_skip_clock_high_water_C1_clock_set_back": "ALLOWED"},
    "A07_first_admission_decided_by_protected_store_only": R["A07_planted_account_record_r7"]["is_first_admission"] and R["A07_planted_account_record_r7"]["account_store_moved_aside"]
                                                           and not R["A07_planted_account_record_r7"]["planted_anchor_survives_in_account_store"],
    "A07_mutant_detected": not R["A07_planted_account_record_mutant_first_admission_from_account_store (revision-6 reading)"]["is_first_admission"],
    "A08_fail_closed": R["A08_installed_without_record"]["C0_status"] == "ALLOWED" and R["A08_installed_without_record"]["C1"] == "BINARY_NOT_ADMITTED",
    "A09_floors_never_lowered": R["A09_readmission"]["first_admission_second_run"] is False and R["A09_readmission"]["floors_after_lower_write"] == {"state_sequence": 11, "root_version": 2, "security_minimum": 9},
    "A11_one_first_admission_all_records": not R["A11_concurrent_first_admissions"]["errors"] and R["A11_concurrent_first_admissions"]["first_admission_count"] == 1 and R["A11_concurrent_first_admissions"]["records"] == 8
                                           and R["A11_concurrent_first_admissions"]["account_store_moved_aside_count"] <= 1,
    "A15_not_honoured": R["A15_records_outside_protected_store"] == "BINARY_NOT_ADMITTED",
    "EX02_EX03_refused": R["EX02_helper_machine_admitter_not_listed"] == "RECORD_ADMITTER_NOT_LISTED" and R["EX03_script_admission_record"] == "RECORD_ADMITTER_NOT_LISTED",
    "L9": R["L9_store_name_is_full_lineage"]["protected_store_basename_length"] == 64 and R["L9_store_name_is_full_lineage"]["record_of_other_lineage_for_this_lineage"] == "BINARY_NOT_ADMITTED",
    "X14_all_records_expire": R["X14_record_expiry"]["ci_image_record_13_days_old"] == "ADMISSION_RECORD_EXPIRED" and R["X14_record_expiry"]["workstation_record_105_days_old"] == "ADMISSION_RECORD_EXPIRED"
                              and R["X14_record_expiry"]["workstation_record_within_90_days"] == "ALLOWED",
    "X15_revoked_self_C0_R_only": all(v == "ALLOWED" for k, v in R["X15_revoked_self"].items() if k in ("status", "doctor", "trust-show")) and all(v == "BINARY_REVOKED_SELF" for k, v in R["X15_revoked_self"].items() if k not in ("status", "doctor", "trust-show")),
    "X7_decision_rule": R["X7_decision_rule"] == {"unanchored_C1": "TRUST_STATE_UNANCHORED", "workstation_anchor_89d_C2": "ALLOWED", "workstation_anchor_91d_C2": "TRUST_ANCHOR_EXPIRED", "ci_anchor_8d_C1": "TRUST_ANCHOR_EXPIRED",
                                                  "C3_currency_23h": "ALLOWED", "C3_currency_25h": "TRUST_STATE_CURRENCY_UNPROVEN", "C3_user_writable_executable": "TCB_WRITABLE_BY_GOVERNED_ACCOUNT",
                                                  "confirm_state_user_writable_executable": "TCB_WRITABLE_BY_GOVERNED_ACCOUNT", "C2_user_writable_executable_anchored": "ALLOWED"},
}
out = {"probe": "ADM7 admission stores, records and the OP-7 (a) decision rule under CP-1 (AR-0019)", "results": res, "verdicts": res_v}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(S, "<scratch>"))
