#!/usr/bin/env python3
"""DA05r7 — review r6 synthesis D's RV6-D-A05 (owner-option combinations that change security) re-expressed for the certified profile
CP-1 (AR-0019). Computed (CS7 loaded unmodified) + design (pack text). Scratch-free.

  E1  The environment selected by the pipeline (review r6's pipeline-authored manifest). Under CP-1 the production rules are on:
      is {pipeline} a minimal set of G_ENV for victims P1, FA, CIR? Control: the revision-6 control rules (CS7 `R6C`) with the same
      victims, where review r6 found {pipeline} minimal.
  E2  The toolchain under CP-1 (the only OP-10 x OP-16 combination, (b) with (b)): is {toolchain_up} alone minimal? Control:
      `V_TOOLCHAIN_DIVERSITY` off (the upstream-only toolchain of an excluded answer).
  E3  Design: `21` states the one combination and the exclusion of every other pair (RV6-L12); `35` names the exclusions.
Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.abspath(os.path.join(HERE, "..", ".."))
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
E1 = {}
for victim in ("P1", "FA", "CIR"):
    row = {}
    for label, R in (("CP-1", CS7.R7), ("revision_6_control", CS7.R6C)):
        sets = CS7.minimal_sets("G_ENV", {"victim": victim}, R)["minimal_sets"]
        inv = CS7.invariants("G_ENV", {"victim": victim}, sets) if label == "CP-1" else {}
        row[label] = {"pipeline_alone_minimal": ["pipeline"] in sets, "minimal_sets": len(sets), "invariant_failures": sorted(k.split(" ")[0] for k, v in inv.items() if not v["holds"])}
    E1[victim] = row
E2 = {}
for label, R in (("CP-1", CS7.R7), ("control_V_TOOLCHAIN_DIVERSITY_off", dict(CS7.R7, V_TOOLCHAIN_DIVERSITY=False))):
    sets = CS7.minimal_sets("G_TOOLCHAIN", {"victim": "P1"}, R)["minimal_sets"]
    E2[label] = {"toolchain_up_alone_minimal": ["toolchain_up"] in sets, "rendered": CS7.uniq_render(CS7.undominated(sets))}
t21 = open(os.path.join(PK, "21-OWNER-OPTIONS.md")).read()
t35 = open(os.path.join(PK, "35-CERTIFIED-PROFILE.md")).read()
E3 = {"21_states_the_one_OP10_OP16_combination": bool(re.search(r"one combination of OP-10 and OP-16: \(b\) with \(b\)", t21)),
      "21_states_every_other_pair_excluded": bool(re.search(r"Every other pair is excluded \(EX-15,\s*EX-21\)", t21)),
      "21_cites_RV6_L12": "RV6-L12" in t21,
      "35_exclusion_rows_EX15_EX21": "| EX-15 |" in t35 and "| EX-21 |" in t35}
out = {"probe": "DA05r7 combinations under CP-1 (AR-0019; after RV6-D-A05)", "E1_pipeline_selected_environment": E1, "E2_toolchain": E2, "E3_design": E3}
out["verdicts"] = {
    "E1_pipeline_never_minimal_under_CP1": not any(v["CP-1"]["pipeline_alone_minimal"] for v in E1.values()),
    "E1_CP1_invariants_hold": not any(v["CP-1"]["invariant_failures"] for v in E1.values()),
    "E1_control_reproduces_review_r6_pipeline_selection": all(v["revision_6_control"]["pipeline_alone_minimal"] for k, v in E1.items() if k == "P1"),
    "E2_toolchain_up_alone_not_minimal_under_CP1": not E2["CP-1"]["toolchain_up_alone_minimal"],
    "E2_control_toolchain_up_alone_minimal": E2["control_V_TOOLCHAIN_DIVERSITY_off"]["toolchain_up_alone_minimal"],
    "E3_design_states_the_combination": all(E3.values()),
}
print(json.dumps(out, indent=1, sort_keys=True))
