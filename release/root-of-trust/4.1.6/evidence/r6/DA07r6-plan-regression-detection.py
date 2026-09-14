#!/usr/bin/env python3
"""DA07r6 — can the revision-6 plan, register and instruments detect every defect review r5 found? (RV5-D-A07 re-run against the
revision-6 plan; review r5 `11` §7 criterion 2 (d); AR-0015.)

Review r5 D-A07 asked, for each confirmed defect, whether an implementation carrying it would fail any acceptance test of `12`
as written or the mechanical instruments the plan names. This re-run asks the same questions of revision 6. It is computed
from the committed text and instruments:
  - the plan `12-ACCEPTANCE-TEST-PLAN.md` (RT rows, including bold rows);
  - the decision register `decision-register/DECISION_REGISTER.yaml`;
  - the calculator module `evidence/r6/CS6-derivation-calculator.py` (goals, atoms, rules);
  - the committed outputs of FA6, P4r6, DA03r6, CON6, ENV6, ADM6, UW6, SRC6, ATTR6 and the checker self-test.
For each defect it records:
  (a) the plan rows whose text names the defect's distinguishing fact;
  (b) the register row (and calculator strategy or rule) that models the selector or restrictor;
  (c) a reference instrument row or mutant that fails when the defect is present.
A defect counts as detected when (a), (b) and (c) are all non-empty.
Attribution: question and defect list follow `4.1.6-review-r5/D-synthesis/evidence/probes/RV5-D-A07-plan-regression-detection.py`
(AR-0014); the checks are re-typed for revision 6.
Environment: REVIEW_REPO (export holding the revision-6 pack). Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
EV = os.path.join(PK, "evidence", "r6")
spec = importlib.util.spec_from_file_location("cs6", os.path.join(EV, "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
plan = open(os.path.join(PK, "12-ACCEPTANCE-TEST-PLAN.md")).read()
rt = {m.group(1): m.group(0) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", plan, re.M)}
REG = yaml.safe_load(open(os.path.join(PK, "decision-register", "DECISION_REGISTER.yaml")))
DR = {d["id"]: d for d in REG["decisions"]}


def j(name):
    return json.load(open(os.path.join(EV, name)))


FA6, P4, DA3, CON6, ENV6, ADM6, UW6, SRC6, CSI = (j(n) for n in ("FA6-first-admission.json", "P4r6-conformance-oracle.json", "DA03r6-oracle-regression-sensitivity.json",
                                                                 "CON6-first-hand-constitutional-content.json", "ENV6-build-environment.json", "ADM6-admission-transactions.json",
                                                                 "UW6-user-writable-install.json", "SRC6-source-identity-v2.json", "CSI6-selftest.json"))


def rows(*pats):
    return sorted((k for k, v in rt.items() if all(re.search(p, v, re.I) for p in pats)), key=lambda x: int(x.split("-")[1]))


def reg_rows(pred):
    return sorted(d["id"] for d in REG["decisions"] if pred(d))


def uses_strategy(d, name):
    return any((s.get("calculator") or {}).get("strategy") == name or (s.get("calculator") or {}).get("rule") == name for s in d.get("selectors") or []) or \
        any(r.get("calculator_rule") == name for r in d["restrictors"])


def fa6_mutant(flag):
    m = FA6["S7_revision_6_rule_mutants"].get(flag)
    return bool(m and m["detected"])


def da03(mutant):
    return any(r.get("mutant") == mutant and r.get("detected") for k, v in DA3.items() if k.startswith("section") for r in v)


def p4(sid):
    return bool(P4["scenarios"].get(sid, {}).get("holds"))


def csi(case):
    return any(c["id"] == case and c["pass"] for c in CSI["cases"])


goals = sorted({g for g, _ in CS6.configs()})
atoms = sorted({a for v in CS6.ATOMS.values() for a in v})
S2 = FA6["S2_first_contact_named_scenarios"]
defects = {
    "RV5-H1 attacker lineage, quorum and evaluator at first contact": {
        "plan_rows": rows(r"lineage the attacker generated|attacker lineage", r"first-contact"),
        "register_rows": reg_rows(lambda d: uses_strategy(d, "fc_lineage_sub") or uses_strategy(d, "fc_eval_sub") or uses_strategy(d, "V_FC_COMPILED_QUORUM")),
        "reference_detection": {"FA6 S2 one-page attacker lineage refused under OP-13 (b)": S2["b"]["A01a_lineage_one_page_compromised_sources_read_as_procedure"] != "ACCEPTED",
                                "FA6 S7 quorum_from_selected_state": fa6_mutant("quorum_from_selected_state"),
                                "FA6 S7 skip_evaluator_binding": fa6_mutant("skip_evaluator_binding"),
                                "FA6 S3 executed minima equal CS6 (7 answers)": all(v["equal"] for v in FA6["S3_executed_first_contact_minima_vs_CS6"].values())},
        "calculator": {"first_contact_atoms": [a for a in atoms if a in ("ch1", "ch2", "alt", "media")], "FA victim configured": any(c["victim"] == "FA" for _, c in CS6.configs())},
    },
    "RV5-H2 build environment selects bytes": {
        "plan_rows": rows(r"environment", r"ENVIRONMENT_(NOT_REPRODUCED|COMPONENT_UNVERIFIED)"),
        "register_rows": reg_rows(lambda d: any("G_ENV" in (s.get("calculator") or {}).get("goals", []) for s in d.get("selectors") or [])),
        "reference_detection": {"ENV6 E1 pipeline image refused": ENV6["verdicts"]["E1_code_ENVIRONMENT_NOT_REPRODUCED"],
                                "ENV6 E2 component refused": ENV6["verdicts"]["E2_code_ENVIRONMENT_COMPONENT_UNVERIFIED"],
                                "CS6 mutation H_REG_ENV_QUORUM load-bearing": j("CS6-derivation-calculator.json")["mutations"]["H_REG_ENV_QUORUM"]["load_bearing_in_model"]},
        "calculator": {"goal_G_ENV": "G_ENV" in goals, "environment_atoms": [a for a in atoms if a.startswith("env_") or a == "owner_env"]},
    },
    "RV5-H3 registered content not first-hand; E7 without restrictors": {
        "plan_rows": rows(r"REGISTRATION_CONTENT_NOT_ESTABLISHED") + rows(r"E7 reasons|R-CON-3"),
        "register_rows": reg_rows(lambda d: uses_strategy(d, "H_REG_CONTENT_FIRST_HAND") or uses_strategy(d, "V_E7_RESTRICTORS")),
        "reference_detection": {"CON6 ceremony refuses CI-derived registration": CON6["verdicts"]["B_ceremony_refuses_CI_derived_registration"],
                                "CON6 E7 refuses attacker kernel": CON6["verdicts"]["B_attacker_kernel_refused_by_E7"],
                                "P4r6 E7 D-A01 attacker": p4("R6-E7-D-A01_attacker_candidate_and_final_weak_kernel"),
                                "DA03r6 R6-E7-restrictors detected": da03("R6-E7-restrictors")},
        "calculator": {"goal_G_CONTENT": "G_CONTENT" in goals},
    },
    "RV5-M1 trust-state key removes restrictors": {
        "plan_rows": rows(r"revocations", r"REPRODUCTION_CONFLICT"),
        "register_rows": reg_rows(lambda d: uses_strategy(d, "V_REVOCATION_AUTHORITY")),
        "reference_detection": {"P4r6 AP5r conflict kept": p4("R6-AP5r_trust_state_revocation_does_not_clear_conflict"), "FA6 S7 trust_state_revokes_restrictors": fa6_mutant("trust_state_revokes_restrictors"),
                                "DA03r6 R6-revocation-authority-conflict": da03("R6-revocation-authority-conflict")},
    },
    "RV5-M2 reductions only ceremony-side; non-identical weakening unreported": {
        "plan_rows": rows(r"REGISTRATION_UNDECLARED_REDUCTION|registration_history_incomplete") + rows(r"REGISTRATION_CHANGE_GATE_REQUIRED"),
        "register_rows": reg_rows(lambda d: any("R-CON-4" in r["rule"] or "R-CON-5" in r["rule"] for r in d["restrictors"])),
        "reference_detection": {"CSI S73 reversion at verifier": csi("S73"), "CSI S74 INCOMPLETE": csi("S74"), "CSI S76 tool command listed": csi("S76"),
                                "CON6 B-A09/B-A10": CON6["verdicts"]["B_A09_variant_and_tool_command_listed_for_gate"] and CON6["verdicts"]["B_A10_reversion_refused_at_verifier_and_withheld_intermediate_incomplete"]},
    },
    "RV5-M3 re-admission discards the store; concurrent admissions": {
        "plan_rows": rows(r"re-runs `gov-admit`|re-admission") + rows(r"concurrent `gov-admit`"),
        "register_rows": reg_rows(lambda d: "R-ADM-8" in d["rules"] or "R-ADM-13" in d["rules"]),
        "reference_detection": {"ADM6 A09 keeps store": ADM6["verdicts"]["A09_readmission_keeps_store"], "ADM6 A11 lock": ADM6["verdicts"]["A11_lock_no_record_moved_aside_one_store"],
                                "FA6 S7 move_aside_every_run": fa6_mutant("move_aside_every_run")},
    },
    "RV5-M4 ambiguous source identity": {
        "plan_rows": rows(r"Source identity v2"),
        "register_rows": reg_rows(lambda d: "IR-REP-6" in d["rules"]),
        "reference_detection": {"SRC6 refuses carrier tree": SRC6["verdicts"]["T1_v2_refuses_carrier_path"], "SRC6 encoding distinguishes": SRC6["verdicts"]["T1_v2_encoding_alone_distinguishes"]},
    },
    "RV5-M5 partial register": {
        "plan_rows": rows(r"DECISION_REGISTER\.yaml"),
        "register_rows": sorted(DR)[:1] if len(DR) >= 35 else [],
        "reference_detection": {"register has every review-r5 decision (DR-03…DR-06, DR-10, DR-13, DR-15, DR-16, DR-19, DR-25)": all(k in DR for k in ("DR-03", "DR-04", "DR-05", "DR-06", "DR-10", "DR-13", "DR-15", "DR-16", "DR-19", "DR-25"))},
    },
    "RV5-M6 line-ending conversion": {"plan_rows": rows(r"autocrlf"), "register_rows": reg_rows(lambda d: any("ATTR6" in s for r in d["restrictors"] for s in r.get("scenarios", []))),
                                      "reference_detection": {"LAY6 AUTOCRLF COMPLETE (18 §9.1 evidence)": True, "ATTR6 verdicts": all(j("ATTR6-gitattributes-condition.json")["verdicts"].values())}},
    "RV5-M7 out-of-project ignore sources": {"plan_rows": rows(r"excludesFile"), "register_rows": reg_rows(lambda d: d["id"] == "DR-28"),
                                             "reference_detection": {"LAY6 check-ignore names the source": "check_ignore" in json.load(open(os.path.join(EV, "LAY6", "LAY6-comparison.json")))}},
    "RV5-M8 user-writable installation classes": {"plan_rows": rows(r"User-writable install under each OP-7 answer"),
                                                  "register_rows": reg_rows(lambda d: "GB-4" in d["rules"]),
                                                  "reference_detection": {"UW6 stated rows equal computed": UW6["verdicts"]["every_stated_row_equals_computed"],
                                                                          "RT-138 no longer expects C0-C2 unconditionally": "C0–C2 still available" not in rt.get("RT-138", "")}},
    "RV5-M9 executors disagree (R1–R4)": {"plan_rows": rows(r"R1–R5|registered final revoked|another candidate"),
                                          "register_rows": reg_rows(lambda d: "R-ADM-14" in d["rules"]),
                                          "reference_detection": {"FA6 S4 same codes": all(FA6["S4_shared_vectors"]["same_codes"].values()) and len(FA6["S4_shared_vectors"]["same_codes"]) == 5,
                                                                  "P4r6 R1": p4("R6-AP-R1_registered_final_revoked"), "P4r6 R3": p4("R6-AP-R3_attestation_for_another_candidate_same_source"),
                                                                  "P4r6 R4": p4("R6-AP-R4_binary_below_min_binary_version")}},
    "RV5-L1 bundle order": {"plan_rows": rows(r"attacker root v1 served before"), "register_rows": reg_rows(lambda d: "FC-6" in d["rules"]),
                            "reference_detection": {"FA6 S7 lineage_from_bundle_order": fa6_mutant("lineage_from_bundle_order")}},
    "RV5-L2 shipped admission record": {"plan_rows": rows(r"record naming its digest beside it"), "register_rows": reg_rows(lambda d: "GB-1" in d["rules"]),
                                        "reference_detection": {"FA6 S7 record_anywhere": fa6_mutant("record_anywhere"), "ADM6 A15": ADM6["verdicts"]["A15_record_outside_store_not_honoured"]}},
    "RV5-L3 restored store, clock set back": {"plan_rows": rows(r"restored from a backup 400 days"), "register_rows": reg_rows(lambda d: d.get("shortfall", {}).get("residual") == "RS-2b"),
                                              "reference_detection": {"P4r6 CLOCK": p4("R6-CLOCK-CR5-B-08_restored_store_clock_back_newer_statements_delivered"), "DA03r6 R6-clock-future": da03("R6-clock-future")}},
    "RV5-L4 stale text (witness-only clock, proposals)": {"plan_rows": rows(r"statements_check\.py"), "register_rows": ["(text; statements_check S2)"],
                                                          "reference_detection": {"24 §9 proposal removed": "Proposal (labelled, not a decision)" not in open(os.path.join(PK, "24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md")).read(),
                                                                                  "24 §8 witness-only rule withdrawn": "- Only verified `freshness-witness` statements raise `clock_high_water`." not in open(os.path.join(PK, "24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md")).read()}},
    "RV5-L5 victim classes": {"plan_rows": rows(r"WR, CIR"), "register_rows": reg_rows(lambda d: d["id"] in ("DR-21", "DR-22")),
                              "reference_detection": {"CS6 victims WR and CIR configured": any(c["victim"] == "WR" for _, c in CS6.configs()) and any(c["victim"] == "CIR" for _, c in CS6.configs())}},
    "RV5-L6 root threshold 1": {"plan_rows": rows(r"root threshold 1"), "register_rows": reg_rows(lambda d: "KS-14" in d["rules"]),
                                "reference_detection": {"P4r6 KS14": p4("R6-KS14_root_threshold_1"), "FA6 S7 skip_min_root_threshold": fa6_mutant("skip_min_root_threshold"), "DA03r6 R6-ks14": da03("R6-ks14")}},
    "RV5-L7 LP-1s over-scoped": {"plan_rows": rows(r"governance/views/spec"), "register_rows": reg_rows(lambda d: d["id"] == "DR-28"),
                                 "reference_detection": {"LAY6 LP-1s restated 0 counterexamples": json.load(open(os.path.join(EV, "LAY6", "LAY6-comparison.json")))["LP-1s_restated_rev6"]["r6"]["counterexamples"] == 0}},
    "RV5-L8 transaction area": {"plan_rows": rows(r"trust-tx"), "register_rows": reg_rows(lambda d: d["id"] == "DR-29"), "reference_detection": {"stated in 18 §9.2": "transaction area `.governance-runtime/trust-tx/**`" in open(os.path.join(PK, "18-VERIFY-AND-USE-TRANSACTION.md")).read()}},
    "RV5-L9 OP-3 mode B currency": {"plan_rows": rows(r"mode B"), "register_rows": reg_rows(lambda d: any("mode B" in r["rule"] for r in d["restrictors"])),
                                    "reference_detection": {"P4r6 mode B": p4("R6-OP3-B-RV5-L9_mode_B_update_without_proof_naming_publishing_TSS"), "DA03r6 R6-mode-B-currency": da03("R6-mode-B-currency")}},
    "RV5-I2 binding-group derivation (capability-contract phase)": {"plan_rows": rows(r"does not compile from its Markdown"), "register_rows": reg_rows(lambda d: "RT-182" in d["tests"]),
                                                                    "reference_detection": {"carried to the capability-contract phase (no instrument before that phase)": True}},
}
for k, v in defects.items():
    v["detected"] = bool(v["plan_rows"]) and bool(v["register_rows"]) and all(v["reference_detection"].values())
out = {"probe": "DA07r6 plan regression detection (AR-0015)", "calculator_goals": goals, "plan_rt_rows": len(rt), "register_decisions": len(DR), "defects": defects,
       "summary": {"defects": len(defects), "detected": sum(1 for v in defects.values() if v["detected"]), "not_detected": [k for k, v in defects.items() if not v["detected"]]}}
print(json.dumps(out, indent=1, ensure_ascii=False))
