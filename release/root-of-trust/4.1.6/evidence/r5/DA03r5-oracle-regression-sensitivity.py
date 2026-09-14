#!/usr/bin/env python3
"""DA03r5 — review r4 synthesis D-A03 (with its D-A03b constructions) re-run against the revision-5 conformance oracle
(`P4r5-conformance-oracle.py`), plus single-line mutants of every revision-5 acceptance rule (RV4-M7; review r4 §7
criterion 4).

Method (as D-A03): a mutant is a copy of the model source with exactly one text replacement (asserted to occur exactly once).
Each mutant directory holds a P4r4 copy and a P4r5 copy (one of them mutated); the unmodified P4r5 is run from that directory
(it loads P4r4 from its own directory). A mutant is DETECTED iff at least one scenario that holds on the unmodified oracle —
revision-5 scenarios or retained P4r4 scenarios — stops holding. A mutant that crashes the oracle is reported, never counted.

Sections.
  1. D-A03's twenty mutants applied VERBATIM to P4r4. Thirteen change retained trust-state rules. Seven change the body of
     P4r4's `verify_artifact`, which revision 5 supersedes; they are expected to be unreachable from the revision-5 oracle.
  2. Those seven rules re-expressed: the same single-line regression applied to the line of P4r5 `accept_binary` that carries
     the rule in revision 5.
  3. Mutants of the rules revision 5 adds (registration, quorum, conflict, FTC, currency coverage, carried CR4-B rules, E7).
Attribution: MUTANTS table of section 1 copied verbatim from
`4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A03-oracle-regression-sensitivity.py`; harness logic follows that probe.
Usage: DA03r5-oracle-regression-sensitivity.py <worktree> <scratch-dir>
"""
import json, os, shutil, subprocess, sys

sys.dont_write_bytecode = True
WT, SCR = sys.argv[1], sys.argv[2]
EV = os.path.join(WT, "release/root-of-trust/4.1.6/evidence")
SRC4 = open(os.path.join(EV, "P4r4-trust-state-model.py")).read()
SRC5 = open(os.path.join(EV, "r5", "P4r5-conformance-oracle.py")).read()
D_A03 = os.path.join(WT, "release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A03-oracle-regression-sensitivity.py")
_t = open(D_A03).read()
_ns = {}
exec(_t[_t.index("MUTANTS = ["):_t.index("]\n\n\ndef run_py")] + "]", _ns)
SECTION1 = _ns["MUTANTS"]
VERIFY_ARTIFACT_RULES = {"D-A8-omits-candidate", "D-A4b-ignores-REJECTED", "D-A4a-source-not-compared", "D-A4b-attestation-not-TSS-referenced",
                         "D-A5-reference-not-required", "D-A7-disabled", "D-A9-not-applied-to-binaries"}

SECTION2 = [  # (name, D-A03 mutant it re-expresses, rule, old, new) — applied to P4r5
    ("R5-A8-omits-candidate", "D-A8-omits-candidate", "25 AP-4: the registered candidate is in the negative-set check",
     'if F["d"] in N or Rg["candidate"] in N:', 'if F["d"] in N:'),
    ("R5-A4b-ignores-REJECTED", "D-A4b-ignores-REJECTED", "25 AP-5: a REJECTED attestation of the registered candidate refuses",
     'if any(a["verdict"] == "REJECTED" for a in atts):', 'if False:'),
    ("R5-A4a-source-not-compared", "D-A4a-source-not-compared", "25 AP-6: reproductions count only for the registered source",
     'x["binary"] == b["digest"] and x["source"] == Rg["source"] and x["tbm"] == t["d"]', 'x["binary"] == b["digest"] and x["tbm"] == t["d"]'),
    ("R5-A4b-attestation-not-registered", "D-A4b-attestation-not-TSS-referenced", "25 AP-5: only attestations listed by the TSS-referenced registration count",
     ' and a["d"] in Rg["vrecs"]', ''),
    ("R5-A5-publication-not-required", "D-A5-reference-not-required", "25 AP-7: the selected TSS publishes the digest",
     'if b["digest"] not in eff["arts"]:', 'if not eff:'),
    ("R5-A7-disabled", "D-A7-disabled", "25 AP-8: TBM below the accepted-TBM high-water refuses",
     'if t["root_v"] < hwm["root"] or t["tps_v"] < hwm["tps"] or t["tss_seq"] < hwm["tss"]:', 'if False:'),
    ("R5-A9-not-applied", "D-A9-not-applied-to-binaries", "25 AP-3: binary acceptance needs C3 and a currency proof covering the selected TSS",
     'if "C3" not in fr["allowed"] or not currency_covers_effective(ts, fr, machine, now):', 'if False:'),
]

SECTION3 = [  # (name, rule, old, new) — applied to P4r5
    ("R5-registration-not-referenced", "25 AP-5: registration referenced by the selected TSS", 'if not eff or Rg["d"] not in eff["arts"]:', 'if not eff:'),
    ("R5-registration-equivocation", "23 §12.2: two registrations for one release refuse", 'if len({r["d"] for r in regs}) > 1:', 'if False:'),
    ("R5-target", "25 AP-5: target registered", 'if b["target"] not in Rg["targets"]:', 'if False:'),
    ("R5-final-restrictor", "25 AP-5: registered final verifies with the registered source and candidate",
     'if F is None or F["source"] != Rg["source"] or F["promoted_from"] != Rg["candidate"]:', 'if F is None:'),
    ("R5-single-signature", "25 AP-6: one-signature reproductions only", 'and len(m.valid_signers(x, rootS)) == 1]', 'and len(m.valid_signers(x, rootS)) >= 1]'),
    ("R5-count-statements", "25 AP-6: quorum counts distinct keys", 'and x["tbm"] == t["d"] for k in m.valid_signers(x, rootS)}', 'and x["tbm"] == t["d"] for k in [x["d"]]}'),
    ("R5-conflict", "25 AP-6: conflicting reproduction refuses", 'if any(x["binary"] != b["digest"] for x in reps):', 'if False:'),
    ("R5-revoked-reproduction-counted", "25 AP-4: revoked reproductions never count",
     'and x["target"] == b["target"] and x["d"] not in N and', 'and x["target"] == b["target"] and'),
    ("R5-revoked-attestation-counted", "25 AP-4: revoked attestations never count",
     'and a["candidate"] == Rg["candidate"] and a["d"] not in N]', 'and a["candidate"] == Rg["candidate"]]'),
    ("R5-tbm-source", "25 AP-8: TBM source equals the registration", ' or t["source"] != Rg["source"]:', ':'),
    ("R5-ftc", "05 §3 FTC on every root version", '    if ftc_violations(rootS):\n        return "ROOT_VERSION_INVALID"', '    if False:\n        return "ROOT_VERSION_INVALID"'),
    ("R5-descendant-proof", "24 §4.4 (CR4-B-07 option 1): a P1 proof covers only the TSS it names",
     '    return any((a["seq"], a["digest"]) == (eff["seq"], eff["d"]) and 0 <= now - a["at"] <= window for a in anchors)', '    return True'),
    ("R5-decision-pin-max-validity", "27 §3.2 (CR4-B-09): decision-pin maximum validity", '> P5["decision_pin_max_validity_days"] * DAY:', '> 10 ** 12 * DAY:'),
    ("R5-first-run-record", "25 AP-8 (CR4-B-08): only resolving release builds are recorded", 'if build == "release" and resolves:', 'if True:'),
    ("R5-clock-high-water", "24 §8 (RV4-M4): every ingested non-future statement raises the stateful clock high-water",
     'if m.verifies(s, rootS) and s.get("issued_at", 0) <= now + P5["clock_skew_seconds"]:', 'if s["kind"] == "witness" and s.get("issued_at", 0) <= now + P5["clock_skew_seconds"]:'),
    ("R5-E7-referenced", "19 E7 revision 5: registration referenced by the effective TSS", 'if Rg is None or not eff or Rg["d"] not in eff["arts"]:', 'if Rg is None:'),
    ("R5-E7-units", "19 E7 revision 5: units and final equal the release's registration", 'if Rg["units"] != Rl["units"] or Rg["final"] != Rl["d"]:', 'if False:'),
]


def run_oracle(d):
    env = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-B", os.path.join(d, "P4r5-conformance-oracle.py")], capture_output=True, text=True, env=env, cwd=d, timeout=600)
    if r.returncode != 0:
        return {"error": r.stderr[-600:]}
    o = json.loads(r.stdout)
    holds = {("r5", k): v["holds"] for k, v in o["scenarios"].items()}
    holds.update({("p4r4", k): v["holds"] for k, v in o["retained_p4r4_scenarios"].items()})
    return {"holds": holds, "summary": o["summary"]}


def materialise(name, src4, src5):
    d = os.path.join(SCR, "mutants", name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "P4r4-trust-state-model.py"), "w").write(src4)
    open(os.path.join(d, "P4r5-conformance-oracle.py"), "w").write(src5)
    return d


base = run_oracle(materialise("BASE", SRC4, SRC5))
if "error" in base:
    print(json.dumps({"error": "unmodified oracle failed", "detail": base}))
    sys.exit(2)


def judge(name, src4, src5):
    o = run_oracle(materialise(name, src4, src5))
    if "error" in o:
        return {"crashed": True, "detail": o["error"][-300:]}
    fail = sorted(f"{k[0]}:{k[1]}" for k, v in o["holds"].items() if base["holds"].get(k) and not v)
    return {"scenarios_that_fail": fail, "detected": bool(fail)}


out = {"instrument": "revision-5 conformance oracle P4r5 (loads P4r4 retained functions)", "base": base["summary"], "section1_D_A03_verbatim_on_P4r4": [],
       "section2_verify_artifact_rules_re_expressed_on_P4r5": [], "section3_revision_5_rules": []}
for name, rule, old, new in SECTION1:
    n = SRC4.count(old)
    row = {"mutant": name, "rule": rule, "target": "P4r4", "occurrences": n}
    if n != 1:
        row["error"] = "expected exactly one occurrence"
    else:
        row.update(judge("S1-" + name, SRC4.replace(old, new), SRC5))
        row["superseded_function"] = name in VERIFY_ARTIFACT_RULES
    out["section1_D_A03_verbatim_on_P4r4"].append(row)
for name, orig, rule, old, new in SECTION2:
    n = SRC5.count(old)
    row = {"mutant": name, "re_expresses": orig, "rule": rule, "target": "P4r5", "occurrences": n}
    if n != 1:
        row["error"] = "expected exactly one occurrence"
    else:
        row.update(judge("S2-" + name, SRC4, SRC5.replace(old, new)))
    out["section2_verify_artifact_rules_re_expressed_on_P4r5"].append(row)
for name, rule, old, new in SECTION3:
    n = SRC5.count(old)
    row = {"mutant": name, "rule": rule, "target": "P4r5", "occurrences": n}
    if n != 1:
        row["error"] = "expected exactly one occurrence"
    else:
        row.update(judge("S3-" + name, SRC4, SRC5.replace(old, new)))
    out["section3_revision_5_rules"].append(row)
s1, s2, s3 = out["section1_D_A03_verbatim_on_P4r4"], out["section2_verify_artifact_rules_re_expressed_on_P4r5"], out["section3_revision_5_rules"]
retained_detected = [r["mutant"] for r in s1 if not r.get("superseded_function") and r.get("detected")]
reexpressed_detected = [r["re_expresses"] for r in s2 if r.get("detected")]
out["summary"] = {
    "D_A03_mutants": len(s1),
    "retained_rule_mutants_detected": f"{len(retained_detected)}/{sum(1 for r in s1 if not r.get('superseded_function'))}",
    "superseded_verify_artifact_mutants_detected_on_P4r4_copy": f"{sum(1 for r in s1 if r.get('superseded_function') and r.get('detected'))}/{sum(1 for r in s1 if r.get('superseded_function'))}",
    "re_expressed_verify_artifact_rules_detected": f"{len(reexpressed_detected)}/{len(s2)}",
    "D_A03_normative_rules_with_a_detecting_scenario": f"{len(set(retained_detected) | set(reexpressed_detected))}/20",
    "revision_5_rule_mutants_detected": f"{sum(1 for r in s3 if r.get('detected'))}/{len(s3)}",
    "not_detected": [r["mutant"] for r in s1 + s2 + s3 if "detected" in r and not r["detected"] and not r.get("superseded_function")],
    "errors_or_crashes": [r["mutant"] for r in s1 + s2 + s3 if "error" in r or r.get("crashed")],
}
print(json.dumps(out, indent=1).replace(SCR, "<scratch>").replace(WT, "<worktree>"))
