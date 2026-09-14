#!/usr/bin/env python3
"""DA03r6 — oracle regression sensitivity of the revision-6 conformance oracle P4r6 (RV4-M7 lineage; review r5 §7 2(d)/(e)).

Method (as review r4 D-A03 and DA03r5): a mutant is a copy of one model file with exactly one text replacement (asserted to occur
exactly once). Each mutant directory holds `P4r4-trust-state-model.py`, `r5/P4r5-conformance-oracle.py` and
`r6/P4r6-conformance-oracle.py`, one of them mutated; P4r6 is run from its directory. A mutant is DETECTED iff at least one row
that holds on the unmodified oracle stops holding: a revision-6 scenario, or a P4r5 scenario re-run under revision-6 rules
(refusal or control preserved, and holding with its unchanged expectation). A crash is reported, never counted.

Sections.
  1. Review r4 D-A03's twenty mutants verbatim on P4r4: thirteen retained trust-state rules (detected through the P4r5 scenarios
     P4r6 re-runs), seven `verify_artifact` rules superseded since revision 5 (unreachable by design).
  2. Those seven rules re-expressed on the line of `accept_binary_r6` that carries each in revision 6.
  3. The revision-5 rules, re-expressed on the revision-6 functions (registration, quorum, conflict, FTC, E7 lookup) and on the
     P4r5 functions P4r6 still uses (currency naming the state, decision-pin validity, first-run record, clock high-water).
  4. Mutants of the rules revision 6 adds.
Attribution: section 1's MUTANTS table is read verbatim from `4.1.6-review-r4/D-synthesis/evidence/probes/
RV4-D-A03-oracle-regression-sensitivity.py`; the harness follows it and DA03r5 (AR-0011).
Usage: DA03r6-oracle-regression-sensitivity.py <repository export> <scratch-dir>
"""
import json, os, subprocess, sys

sys.dont_write_bytecode = True
WT, SCR = sys.argv[1], sys.argv[2]
EV = os.path.join(WT, "release/root-of-trust/4.1.6/evidence")
SRC4 = open(os.path.join(EV, "P4r4-trust-state-model.py")).read()
SRC5 = open(os.path.join(EV, "r5", "P4r5-conformance-oracle.py")).read()
SRC6 = open(os.path.join(EV, "r6", "P4r6-conformance-oracle.py")).read()
_t = open(os.path.join(WT, "release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence/probes/RV4-D-A03-oracle-regression-sensitivity.py")).read()
_ns = {}
exec(_t[_t.index("MUTANTS = ["):_t.index("]\n\n\ndef run_py")] + "]", _ns)
SECTION1 = _ns["MUTANTS"]
VERIFY_ARTIFACT_RULES = {"D-A8-omits-candidate", "D-A4b-ignores-REJECTED", "D-A4a-source-not-compared", "D-A4b-attestation-not-TSS-referenced",
                         "D-A5-reference-not-required", "D-A7-disabled", "D-A9-not-applied-to-binaries"}

SECTION2 = [  # (name, D-A03 rule re-expressed, rule, target, old, new)
    ("R6-A8-omits-candidate", "D-A8-omits-candidate", "25 AP-4: the registered candidate is in the negative-set check", "r6", 'if F["d"] in N or Rg["candidate"] in N:', 'if F["d"] in N:'),
    ("R6-A4b-ignores-REJECTED", "D-A4b-ignores-REJECTED", "25 AP-5: a REJECTED attestation of the registered candidate refuses", "r6", '    if any(a["verdict"] == "REJECTED" for a in restr_atts):', '    if False:'),
    ("R6-A4a-source-not-compared", "D-A4a-source-not-compared", "25 AP-6: reproductions count only for the registered source", "r6",
     'x["binary"] == b["digest"] and x["source"] == Rg["source"] and x["tbm"] == t["d"]', 'x["binary"] == b["digest"] and x["tbm"] == t["d"]'),
    ("R6-A4b-attestation-not-registered", "D-A4b-attestation-not-TSS-referenced", "25 AP-5: only attestations the registration lists count", "r6",
     ' or a["d"] not in Rg["vrecs"] or a["source"] != Rg["source"]:', ' or a["source"] != Rg["source"]:'),
    ("R6-A5-publication-not-required", "D-A5-reference-not-required", "25 AP-7: the selected TSS publishes the digest", "r6", 'if b["digest"] not in eff["arts"]:', 'if not eff:'),
    ("R6-A7-disabled", "D-A7-disabled", "25 AP-8: TBM below the accepted-TBM high-water refuses", "r6",
     'if t["root_v"] < hwm["root"] or t["tps_v"] < hwm["tps"] or t["tss_seq"] < hwm["tss"]:', 'if False:'),
    ("R6-A9-not-applied", "D-A9-not-applied-to-binaries", "25 AP-3: binary acceptance needs C3 and a currency proof covering the selected TSS", "r6",
     '    if "C3" not in fr["allowed"] or not currency_covers_effective_r6(ts, fr, machine, now):\n        ax = fr["axis"]', '    if False:\n        ax = fr["axis"]'),
]
SECTION3 = [  # (name, rule, target, old, new)
    ("R6-registration-not-referenced", "25 AP-5: registration referenced by the selected TSS", "r6",
     '    if Rg is None or not eff or Rg["d"] not in eff["arts"]:\n        return "RELEASE_UNREGISTERED"', '    if Rg is None or not eff:\n        return "RELEASE_UNREGISTERED"'),
    ("R6-registration-equivocation", "23 §12.2: two registrations for one release refuse", "r6", '    if len({r["d"] for r in regs}) > 1:', '    if False:'),
    ("R6-target", "25 AP-5: target registered", "r6", '    if b["target"] not in Rg["targets"]:', '    if False:'),
    ("R6-final-restrictor", "25 AP-5: registered final with the registered source and candidate", "r6",
     'if F is None or F["source"] != Rg["source"] or F["promoted_from"] != Rg["candidate"]:', 'if F is None:'),
    ("R6-single-signature", "25 AP-6: one-signature reproductions only", "r6", 'one = lambda x: len(m.valid_signers(x, rootS)) == 1', 'one = lambda x: len(m.valid_signers(x, rootS)) >= 1'),
    ("R6-count-statements", "25 AP-6: quorum counts distinct keys", "r6", 'and x["tbm"] == t["d"] for k in m.valid_signers(x, rootS)}', 'and x["tbm"] == t["d"] for k in [x["d"]]}'),
    ("R6-conflict", "25 AP-6: a conflicting reproduction refuses", "r6", '    if any(x["binary"] != b["digest"] for x in reps_restr):', '    if False:'),
    ("R6-revoked-reproduction-counted", "25 AP-4: revoked reproductions never count", "r6",
     'and x["target"] == b["target"] and x["d"] not in N and x["d"] not in RA and one(x)]', 'and x["target"] == b["target"] and one(x)]'),
    ("R6-revoked-attestation-counted", "25 AP-4: revoked attestations never count", "r6",
     'if a["kind"] != "att" or a["verdict"] != "ACCEPTED" or a["d"] in N or a["d"] in RA or', 'if a["kind"] != "att" or a["verdict"] != "ACCEPTED" or'),
    ("R6-tbm-source", "25 AP-8: TBM source equals the registration", "r6", ' or t["source"] != Rg["source"]:', ':'),
    ("R6-ftc", "05 §3 FTC on every root version", "r6", '    if ftc_violations_r6(rootS):\n        return "ROOT_VERSION_INVALID"', '    if False:\n        return "ROOT_VERSION_INVALID"'),
    ("R6-descendant-proof", "24 §4.4 (CR4-B-07 option 1): a P1 proof covers only the TSS it names", "r5",
     '    return any((a["seq"], a["digest"]) == (eff["seq"], eff["d"]) and 0 <= now - a["at"] <= window for a in anchors)', '    return True'),
    ("R6-decision-pin-max-validity", "27 §3.2 (CR4-B-09)", "r5", '> P5["decision_pin_max_validity_days"] * DAY:', '> 10 ** 12 * DAY:'),
    ("R6-first-run-record", "25 AP-8 (CR4-B-08)", "r5", 'if build == "release" and resolves:', 'if True:'),
    ("R6-clock-high-water", "24 §8 (RV4-M4)", "r5", 'if m.verifies(s, rootS) and s.get("issued_at", 0) <= now + P5["clock_skew_seconds"]:',
     'if s["kind"] == "witness" and s.get("issued_at", 0) <= now + P5["clock_skew_seconds"]:'),
    ("R6-E7-referenced", "19 E7: registration referenced by the effective TSS", "r6",
     'if Rg is None or not eff or Rg["d"] not in eff["arts"]:\n        return no("release_unregistered")', 'if Rg is None:\n        return no("release_unregistered")'),
    ("R6-E7-units", "19 E7: units and final equal the release's registration", "r6", 'if Rg["units"] != Rl["units"] or Rg["final"] != Rl["d"]:', 'if False:'),
]
SECTION4 = [  # revision-6 rules
    ("R6-registration-revocation", "25 AP-4 r6: the registration is not revoked", "r6", '    if RULES6["ap4_registration_final_candidate"] and Rg["d"] in N:', '    if False:'),
    ("R6-final-revocation", "25 AP-4 r6: the registered final is not revoked", "r6", 'if F["d"] in N or Rg["candidate"] in N:', 'if Rg["candidate"] in N:'),
    ("R6-candidate-binding", "25 AP-5 / 34 R-CON-2: attestations for exactly the registered candidate", "r6", '        if RULES6["ap5_candidate_binding"] and a["candidate"] != Rg["candidate"]:', '        if False:'),
    ("R6-kernel-binding", "25 AP-5 / 34 R-CON-2: attestations for the registered kernel tree", "r6", '        if RULES6["ap5_kernel_binding"] and a.get("kernel") != Rg["kernel"]:', '        if False:'),
    ("R6-final-kernel", "25 AP-5 r6: the registered final carries the registered kernel tree", "r6", '    if RULES6["ap5_kernel_binding"] and F["tree"] != Rg["kernel"]:', '    if False:'),
    ("R6-min-binary-version", "25 AP-4: binary version >= min_binary_version", "r6", '    if RULES6["ap4_min_binary_version"] and fields.get("min_binary_version") is not None:', '    if False:'),
    ("R6-revocation-authority-conflict", "30 R-REP-5' (CR5-B-01 (i))", "r6",
     '(x["d"] not in RA if RULES6["ap5r_revocation_authority"] else (x["d"] not in RA and x["d"] not in N))]', '(x["d"] not in RA and x["d"] not in N)]'),
    ("R6-revocation-authority-REJECTED", "25 AP-5r (CR5-B-01 (ii))", "r6",
     '(a["d"] not in RA if RULES6["ap5r_revocation_authority"] else (a["d"] not in RA and a["d"] not in N))]', '(a["d"] not in RA and a["d"] not in N)]'),
    ("R6-ks14", "05 §3 KS-14 (CR5-B-11)", "r6", '    if RULES6["ks14_root_threshold"] and rootS["thresholds"].get("root", 0) < 2:', '    if False:'),
    ("R6-E7-restrictors", "34 R-CON-3: E7 applies AP-5's restrictors", "r6", '    if RULES6["e7_restrictors"]:', '    if False:'),
    ("R6-E7-verification-count", "34 R-CON-3: OP-8 attestations for the registered candidate and kernel", "r6",
     '        if len(acc) < P6["min_verification_records"]:\n            return no("verification_records_below_minimum")', '        if False:\n            return no("verification_records_below_minimum")'),
    ("R6-E7-candidate-held", "34 R-CON-3: the registered candidate held and verifying (mutant: the registered final stands in for an absent candidate)", "r6",
     's["kind"] == "release-candidate" and s["d"] == Rg["candidate"]), None)', 's["kind"] == "release-candidate" and s["d"] == Rg["candidate"]), F)'),
    ("R6-E7-final-promoted", "34 R-CON-3: the final promoted from the registered candidate", "r6", '        if F["promoted_from"] != Rg["candidate"]:', '        if False:'),
    ("R6-E7-REJECTED", "34 R-CON-3: a held REJECTED attestation refuses", "r6", '        if any(a["verdict"] == "REJECTED" for a in restr):', '        if False:'),
    ("R6-clock-future", "24 §8 r6 (CR5-B-08): future-refused statements make clock-based proofs unusable", "r6",
     '    if RULES6["clock_future_statements"] and future and fr.get("proof") and "in-gate" not in fr["proof"]:', '    if False:'),
    ("R6-ceremony-first-hand-content", "34 R-CON-1: custodians derive content first-hand", "r6", '    if derived["kernel"] != proposal["kernel"] or derived["units"] != proposal["units"]:', '    if False:'),
    ("R6-ceremony-first-hand-records", "30 R-REG-3 (d) r6: first-hand records for exactly the candidate", "r6",
     '    if len(ok_records) < P6["min_verification_records"] or any(r["verdict"] == "REJECTED" and r["candidate"] == proposal["candidate"] for r in records):', '    if False:'),
    ("R6-mode-B-currency", "21 OP-3 mode B (RV5-L9): a proof naming the publishing TSS per update", "r6",
     '    if "C3" not in fr["allowed"] or not currency_covers_effective_r6(ts, fr, machine, now):\n        return "TRUST_STATE_CURRENCY_UNPROVEN"', '    if False:\n        return "TRUST_STATE_CURRENCY_UNPROVEN"'),
]


def run_oracle(d):
    env = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-B", os.path.join(d, "r6", "P4r6-conformance-oracle.py")], capture_output=True, text=True, env=env, cwd=os.path.join(d, "r6"), timeout=900)
    if r.returncode != 0:
        return {"error": r.stderr[-600:]}
    o = json.loads(r.stdout)
    holds = {("r6", k): v["holds"] for k, v in o["scenarios"].items()}
    holds.update({("p4r5_under_r6", k): (v["refusal_or_control_preserved"] and v["r6_holds_with_r5_expectation"]) for k, v in o["p4r5_under_r6"]["rows"].items()})
    return {"holds": holds, "summary": o["summary"]}


def materialise(name, src4, src5, src6):
    d = os.path.join(SCR, "mutants", name)
    os.makedirs(os.path.join(d, "r5"), exist_ok=True)
    os.makedirs(os.path.join(d, "r6"), exist_ok=True)
    open(os.path.join(d, "P4r4-trust-state-model.py"), "w").write(src4)
    open(os.path.join(d, "r5", "P4r5-conformance-oracle.py"), "w").write(src5)
    open(os.path.join(d, "r6", "P4r6-conformance-oracle.py"), "w").write(src6)
    return d


base = run_oracle(materialise("BASE", SRC4, SRC5, SRC6))
if "error" in base:
    print(json.dumps({"error": "unmodified oracle failed", "detail": base}))
    sys.exit(2)


def judge(name, s4, s5, s6):
    o = run_oracle(materialise(name, s4, s5, s6))
    if "error" in o:
        return {"crashed": True, "detail": o["error"][-300:]}
    fail = sorted(f"{k[0]}:{k[1]}" for k, v in o["holds"].items() if base["holds"].get(k) and not v)
    return {"scenarios_that_fail": fail[:12], "failing_count": len(fail), "detected": bool(fail)}


def apply(target, old, new):
    src = {"p4r4": SRC4, "r5": SRC5, "r6": SRC6}[target]
    n = src.count(old)
    if n != 1:
        return None, n
    s4, s5, s6 = SRC4, SRC5, SRC6
    if target == "p4r4":
        s4 = src.replace(old, new)
    elif target == "r5":
        s5 = src.replace(old, new)
    else:
        s6 = src.replace(old, new)
    return (s4, s5, s6), 1


out = {"instrument": "revision-6 conformance oracle P4r6 (loads P4r5 and P4r4)", "base": {k: v for k, v in base["summary"].items() if k not in ("rules", "params", "honest_controls")},
       "section1_D_A03_verbatim_on_P4r4": [], "section2_verify_artifact_rules_re_expressed_on_accept_binary_r6": [], "section3_revision_5_rules_on_revision_6_functions": [],
       "section4_revision_6_rules": []}
for name, rule, old, new in SECTION1:
    srcs, n = apply("p4r4", old, new)
    row = {"mutant": name, "rule": rule, "target": "P4r4", "occurrences": n, "superseded_function": name in VERIFY_ARTIFACT_RULES}
    row.update(judge("S1-" + name, *srcs) if srcs else {"error": "expected exactly one occurrence"})
    out["section1_D_A03_verbatim_on_P4r4"].append(row)
for name, orig, rule, target, old, new in SECTION2:
    srcs, n = apply(target, old, new)
    row = {"mutant": name, "re_expresses": orig, "rule": rule, "target": target, "occurrences": n}
    row.update(judge("S2-" + name, *srcs) if srcs else {"error": "expected exactly one occurrence"})
    out["section2_verify_artifact_rules_re_expressed_on_accept_binary_r6"].append(row)
for sec, rows in (("section3_revision_5_rules_on_revision_6_functions", SECTION3), ("section4_revision_6_rules", SECTION4)):
    for name, rule, target, old, new in rows:
        srcs, n = apply(target, old, new)
        row = {"mutant": name, "rule": rule, "target": target, "occurrences": n}
        row.update(judge(("S3-" if sec.startswith("section3") else "S4-") + name, *srcs) if srcs else {"error": "expected exactly one occurrence"})
        out[sec].append(row)
s1, s2, s3, s4 = (out[k] for k in ("section1_D_A03_verbatim_on_P4r4", "section2_verify_artifact_rules_re_expressed_on_accept_binary_r6", "section3_revision_5_rules_on_revision_6_functions", "section4_revision_6_rules"))
retained = [r["mutant"] for r in s1 if not r["superseded_function"] and r.get("detected")]
reexp = [r["re_expresses"] for r in s2 if r.get("detected")]
out["summary"] = {
    "D_A03_mutants": len(s1),
    "retained_rule_mutants_detected": f"{len(retained)}/{sum(1 for r in s1 if not r['superseded_function'])}",
    "re_expressed_verify_artifact_rules_detected": f"{len(reexp)}/{len(s2)}",
    "D_A03_normative_rules_with_a_detecting_scenario": f"{len(set(retained) | set(reexp))}/20",
    "revision_5_rule_mutants_detected_on_revision_6_oracle": f"{sum(1 for r in s3 if r.get('detected'))}/{len(s3)}",
    "revision_6_rule_mutants_detected": f"{sum(1 for r in s4 if r.get('detected'))}/{len(s4)}",
    "not_detected": [r["mutant"] for r in s1 + s2 + s3 + s4 if "detected" in r and not r["detected"] and not r.get("superseded_function")],
    "errors_or_crashes": [r["mutant"] for r in s1 + s2 + s3 + s4 if "error" in r or r.get("crashed")],
}
print(json.dumps(out, indent=1).replace(SCR, "<scratch>").replace(WT, "<export>"))
