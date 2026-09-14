#!/usr/bin/env python3
"""RV6-D-A05 — owner-option combinations that change security, and whether `21` states them (review r6 synthesis D, AR-0018).
Computed (CS6 loaded unmodified; wrappers call the originals) + design (pack text) + references to executed rows of D-A01,
D-A02, D-A08. Scratch only.

Computed parts
  E1  Build environment authored by the pipeline (reviewer B's RV6-B-A02 wrapper `w_releases_ctx`/`w_build`/`w_binary_accepted`,
      copied with attribution) under combinations B did not compute: OP-9 (d) (custodians' own reproduction), OP-8 = 2, victims
      FA (OP-13 (b)) and CIR. Question: does any other answer remove {pipeline}?
  E2  OP-16 (b) with OP-10 (a): G_TOOLCHAIN minimal sets under the toolchain answer, which environment diversity does not
      change, against `21` §17's combination table.
Design part: a table of combinations with the executed or computed row that shows the change and the `21` text that states it
(or its absence).
Environment: REVIEW_REPO. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
spec = importlib.util.spec_from_file_location("cs6", os.path.join(PK, "evidence", "r6", "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)

# ---- reviewer B RV6-B-A02 computed wrapper (AR-0016), copied
O_rel, O_build = CS6.releases, CS6.build
MODE = {"manifest": False}


def w_releases_ctx(goal, C, cfg_env):
    r = list(O_rel(goal, C))
    if MODE["manifest"] and goal == "G_ENV" and "pipeline" in C and cfg_env in ("a", "b"):
        r.append({"S": "S_good", "I": "I_good", "E": "E_man", "K": "K_good", "genuine": False})
    return r


def w_build(rel, j, C, cfg, R):
    b = O_build(rel, j, C, cfg, R)
    if rel["E"] == "E_man":
        return (b[0], b[1], b[2], b[3], True, b[5])
    return b


O_bin = CS6.binary_accepted


def w_binary_accepted(goal, C, cfg, R):
    CS6.releases = lambda g_, C_: w_releases_ctx(g_, C_, cfg.get("env", "a"))
    try:
        return O_bin(goal, C, cfg, R)
    finally:
        CS6.releases = O_rel


CS6.build, CS6.binary_accepted = w_build, w_binary_accepted
E1 = {}
for label, over in (("OP-9 d_n2q2, victim P1", {"repro": "d_n2q2"}), ("OP-8 = 2, victim P1", {"V": 2}), ("victim FA, OP-13 (b)", {"victim": "FA", "fc": "b"}),
                    ("victim CIR", {"victim": "CIR"}), ("OP-2 (b) delegated, victim P1", {"reg": "delegated"})):
    for env in ("a", "b", "c"):
        cfg = dict({"reg": "root", "V": 1, "repro": "n2q2", "victim": "P1", "fc": "-", "op4": "sep", "tc": "accept", "env": env}, **over)
        row = {}
        for mode in (False, True):
            MODE["manifest"] = mode
            sets = CS6.minimal_sets("G_ENV", cfg, CS6.R6)["minimal_sets"]
            inv = CS6.invariants("G_ENV", cfg, sets)
            row["pipeline_authored_manifest" if mode else "control"] = {"pipeline_alone_minimal": ["pipeline"] in sets,
                                                                         "invariant_failures": sorted(k.split(" ")[0] for k, v in inv.items() if not v["holds"])}
        E1["%s | OP-16 (%s)" % (label, env)] = row
MODE["manifest"] = False
CS6.build, CS6.binary_accepted = O_build, O_bin

E2 = {}
for tc in ("accept", "diverse", "owner_built"):
    cfg = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "P1", "fc": "-", "op4": "sep", "tc": tc, "env": "b"}
    E2["OP-10=%s with OP-16 (b)" % tc] = CS6.uniq_render(CS6.minimal_sets("G_TOOLCHAIN", cfg, CS6.R6)["minimal_sets"])
t21 = open(os.path.join(PK, "21-OWNER-OPTIONS.md")).read()
s17 = t21[t21.index("## 17."):]
design = {
    "s17_rows": [l for l in s17.splitlines() if l.startswith("| OP-")],
    "s17_states_OP10a_with_OP16b": bool(re.search(r"OP-10 \(a\) \+ OP-16 \(b\)|OP-16 \(b\) \+ OP-10 \(a\)", s17)),
    "s17_readmission_row_states_store_not_applied": bool(re.search(r"OP-14 \(b\) or OP-15 \(a\)[^\n]*(?:not applied|ignor|older|stale|revok)", s17)),
    "OP13_d_states_media_age": bool(re.search(r"\(d\)[^\n]*(?:\bage\b|\bstale\b|valid_until|re-prepar|\bexpir)", t21[t21.index("## OP-13"):t21.index("## OP-14")])),
    "OP13_states_designation_source": bool(re.search(r"fc-procedure|designation of (?:the )?sources|obtains? (?:the )?(?:source list|procedure)|where the operator (?:learns|obtains)", t21[t21.index("## OP-13"):t21.index("## OP-14")], re.I)),
    "OP16_states_manifest_author": bool(re.search(r"\bauthor(?:ed|s)?\b|who writes|proposes the manifest", t21[t21.index("## OP-16"):t21.index("## 17.")], re.I)),
    "OP7_c_states_witness_input_composer": bool(re.search(r"witness[^\n]*(?:publisher|compos)", t21[t21.index("## OP-7"):t21.index("## OP-8")], re.I)),
    "OP9_d_states_environment_author": bool(re.search(r"\(d\)[^\n]*(?:environment|manifest)", t21[t21.index("## OP-9"):t21.index("## OP-10")], re.I)),
}
combos = [
    {"combination": "OP-13 (a)/(b)/(c) any + who designates the sources and prints the procedure", "change": "desig selects the evaluator (a), (b), (c) either; the state (and with weakened steps the evaluator) under (c) all", "evidence": "RV6-D-A01 P, C", "stated_in_21": design["OP13_states_designation_source"]},
    {"combination": "OP-13 (d) + media prepared earlier than the newest revocation", "change": "revoked (including malicious) binaries admitted as first TCB; no age bound", "evidence": "RV6-D-A08", "stated_in_21": design["OP13_d_states_media_age"]},
    {"combination": "OP-14 (b) or OP-15 (a) + any OP-13 answer + an older first-contact value at re-admission", "change": "a binary revoked in the kept store is admitted; the store's anchors are ignored", "evidence": "RV6-D-A02", "stated_in_21": design["s17_readmission_row_states_store_not_applied"]},
    {"combination": "OP-7 (c) + a compromised trust-state publisher", "change": "witness-reliant runners accept {2 reproducer keys, transport, fcpub} (witness keys not needed)", "evidence": "RV6-D-A01 C WR", "stated_in_21": design["OP7_c_states_witness_input_composer"]},
    {"combination": "OP-16 (a)/(b) + OP-9 (d), OP-8 = 2, OP-2 (b), victims FA and CIR + a pipeline-authored environment manifest", "change": "{pipeline} stays minimal under each (computed E1)", "evidence": "RV6-D-A05 E1", "stated_in_21": design["OP16_states_manifest_author"] or design["OP9_d_states_environment_author"]},
    {"combination": "OP-16 (b) + OP-10 (a)", "change": "{toolchain_up} alone still yields malicious bytes; environment diversity does not cover the toolchain archive", "evidence": "RV6-D-A05 E2", "stated_in_21": design["s17_states_OP10a_with_OP16b"]},
]
out = {"probe": "RV6-D-A05 owner-option combinations (AR-0018)", "E1_pipeline_authored_manifest_under_other_answers": E1, "E2_toolchain_under_OP16_b": E2, "design": design, "combinations": combos}
out["verdicts"] = {
    "E1_control_pipeline_never_minimal": not any(v["control"]["pipeline_alone_minimal"] for v in E1.values()),
    "E1_pipeline_minimal_under_OP16_a_b_for_every_listed_answer": all(v["pipeline_authored_manifest"]["pipeline_alone_minimal"] for k, v in E1.items() if "OP-16 (c)" not in k),
    "E1_OP16_c_unaffected": not any(v["pipeline_authored_manifest"]["pipeline_alone_minimal"] for k, v in E1.items() if "OP-16 (c)" in k),
    "E2_toolchain_up_alone_under_OP10_accept_with_OP16_b": "{toolchain_up}" in E2["OP-10=accept with OP-16 (b)"],
    "combinations_not_stated_in_21": [c["combination"] for c in combos if not c["stated_in_21"]],
}
print(json.dumps(out, indent=1, sort_keys=True))
