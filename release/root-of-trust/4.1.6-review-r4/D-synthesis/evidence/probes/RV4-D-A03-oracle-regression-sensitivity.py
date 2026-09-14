#!/usr/bin/env python3
"""RV4-D-A03 (review r4 synthesis D, AR-0008) — can the pack's mandated conformance instruments detect plausible single-rule
implementation regressions OTHER than the nine review-r3 defects they were built to catch?

`12` §8 and RT-72 (vi) make the architect's P4r4 scenarios (54) and VA4 rows (16) the conformance oracle, and require a
distinguishing scenario only for the nine listed mutants. This probe writes further single-line mutants of the architect's
own rule functions (P4r4, unmodified except for the one line each mutant changes), each a regression an implementer could
plausibly make in a rule the pack declares normative, and re-runs the unmodified P4r4 scenario suite and the unmodified VA4
script against each. A mutant is DETECTED iff at least one scenario or row that holds on the unmodified model stops holding.

No files outside the scratch directory given; subprocesses are the pack's own Python scripts. Output: JSON on stdout.
Usage: RV4-D-A03-oracle-regression-sensitivity.py <worktree> <scratch-dir>
"""
import json, os, shutil, subprocess, sys

sys.dont_write_bytecode = True
WT, SCR = sys.argv[1], sys.argv[2]
EV = os.path.join(WT, "release/root-of-trust/4.1.6/evidence")
SRC = open(os.path.join(EV, "P4r4-trust-state-model.py")).read()
VA4 = os.path.join(EV, "VA4-verify-artifact-source-scenarios.py")

# (name, normative rule regressed, exact old text, new text)
MUTANTS = [
    ("D-A8-omits-candidate", "25 A8: the candidate is in the negative set check",
     'if art["digest"] in N or F["d"] in N or (C and C["d"] in N):', 'if art["digest"] in N or F["d"] in N:'),
    ("D-A4b-ignores-REJECTED", "25 A4b: a REJECTED attestation of the candidate refuses",
     '        if any(a["verdict"] == "REJECTED" for a in atts):\n            return "ARTIFACT_SOURCE_REJECTED"',
     '        if False:\n            return "ARTIFACT_SOURCE_REJECTED"'),
    ("D-A4a-source-not-compared", "25 A4a: the build attestation's source equals the TBM source",
     'b["tbm"] == t["d"] and b["source"] == t["source"] for k in valid_signers(b, rootS)}', 'b["tbm"] == t["d"] for k in valid_signers(b, rootS)}'),
    ("D-A4b-attestation-not-TSS-referenced", "25 A4b: the ACCEPTED attestation is referenced by the effective TSS",
     'a["source"] == C["source"] and eff and a["d"] in eff["atts"]]', 'a["source"] == C["source"]]'),
    ("D-A5-reference-not-required", "25 A5: the effective TSS references the artefact",
     'if not eff or art["digest"] not in eff["arts"]:', 'if not eff:'),
    ("D-A7-disabled", "25 A7: TBM below the accepted-TBM high-water refuses",
     'if t["root_v"] < hwm["root"] or t["tps_v"] < hwm["tps"] or t["tss_seq"] < hwm["tss"]:', 'if False:'),
    ("D-A9-not-applied-to-binaries", "25 A9: binary acceptance needs C3 (anchor + currency proof)",
     'if "C3" not in fr["allowed"]:\n        ax = fr["axis"]', 'if "C0" not in fr["allowed"]:\n        ax = fr["axis"]'),
    ("D-inclusion-without-held", "24 §3.4 rule 1: the anchored statement must be held",
     'all((a["seq"], a["digest"]) in held and (a["seq"], a["digest"]) in _chain(t) for a in anchors)', 'all((a["seq"], a["digest"]) in _chain(t) for a in anchors)'),
    ("D-unchained-above-anchor-not-regression", "24 §3.4 rule 4: unchained statements above the anchor make the state REGRESSION",
     'if eff and (any(n["seq"] > eff["seq"] for n in non) or unchained):', 'if eff and any(n["seq"] > eff["seq"] for n in non):'),
    ("D-below-anchor-allows-C1", "24 §4.3: BELOW_ANCHOR allows C0 only",
     'not held in the effective chain)", "allowed": ["C0"]', 'not held in the effective chain)", "allowed": ["C0", "C1", "C2"]'),
    ("D-pin-validity-cap-not-checked", "24 §3.2: valid_until - provisioned_at <= pin_max_validity_days",
     ' or vu - p["provisioned_at"] > P["pin_max_validity_days"] * DAY', ''),
    ("D-witness-for-any-tss", "24 §3.3: a witness is honoured only when it names the effective TSS",
     '        if (w["seq"], w["tss_d"]) != (eff["seq"], eff["d"]):\n            continue', '        pass'),
    ("D-witness-replay-not-refused", "24 §3.3: a witness older than the newest accepted witness is refused",
     '        if w["issued_at"] < hwi:\n            continue', '        pass'),
    ("D-c2-on-incomplete", "24 §4.3: INCOMPLETE refuses C2",
     'c2 = ts["status"] == "KNOWN" and', 'c2 = ts["status"] in ("KNOWN", "INCOMPLETE") and'),
    ("D-admissibility-ignores-artifacts", "17 S4 (d): a TSS never drops a lower artifacts[] reference",
     ' and t["arts"] >= l["arts"]', ''),
    ("D-tps-prior-chain-not-checked", "17 S3: a top TPS must chain every held lower TPS",
     'if not lower <= top["prior"]:', 'if False:'),
    ("D-lift-attestation-not-TSS-referenced", "17 MS-2: the lifting attestation is referenced by the effective TSS",
     'if a and a["d"] in eff["atts"] and', 'if a and'),
    ("D-op7-order-c-above-a", "19 §10.6: op7_mode order (b) > (a) > (c) > (d)",
     '_OP7_STRENGTH = ["d", "c", "a", "b"]', '_OP7_STRENGTH = ["d", "a", "c", "b"]'),
    ("D-decision-pin-expiry-not-checked", "27 §3.2: an expired decision pin authorises nothing",
     '            if R["pin_validity"] and (p.get("expires_at") is None or now > p["expires_at"]):\n                continue', '            pass'),
    ("D-local-terminal-only-ignored", "27 §3.2: a decision pin never approves a local_terminal_only kind",
     'if kind not in tps_eff["fields"]["local_terminal_only"]:', 'if True:'),
]


def run_py(dirpath, script):
    env = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-B", os.path.join(dirpath, script)], capture_output=True, text=True, env=env, cwd=dirpath, timeout=600)
    if r.returncode != 0:
        return {"error": r.stderr[-800:]}
    return json.loads(r.stdout)


def materialise(name, src):
    d = os.path.join(SCR, "mutants", name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "P4r4-trust-state-model.py"), "w").write(src)
    shutil.copy(VA4, os.path.join(d, "VA4-verify-artifact-source-scenarios.py"))
    return d


def outcomes(d):
    p4 = run_py(d, "P4r4-trust-state-model.py")
    va = run_py(d, "VA4-verify-artifact-source-scenarios.py")
    if "error" in p4 or "error" in va:
        return {"p4": p4 if "error" in p4 else None, "va4": va if "error" in va else None}
    rows = va if isinstance(va, list) else va.get("rows", va.get("scenarios", []))
    return {"p4_holds": {k: v["holds"] for k, v in p4["scenarios"].items()},
            "va4_as_expected": {r["scenario"]: r["as_expected"] for r in rows},
            "p4_oracle_killed": p4["summary"]["mutants_killed"]}


base = outcomes(materialise("BASE", SRC))
res = {"instrument": "architect P4r4 (54 scenarios, 9 oracle mutants) and VA4 (16 rows), run unmodified against single-line mutants of P4r4",
       "base": {"p4_scenarios": len(base["p4_holds"]), "p4_holding": sum(base["p4_holds"].values()), "va4_rows": len(base["va4_as_expected"]),
                "va4_as_expected": sum(base["va4_as_expected"].values()), "p4_oracle_killed": base["p4_oracle_killed"]},
       "mutants": []}
for name, rule, old, new in MUTANTS:
    n = SRC.count(old)
    if n != 1:
        res["mutants"].append({"mutant": name, "rule": rule, "error": f"expected exactly one occurrence, found {n}"})
        continue
    o = outcomes(materialise(name, SRC.replace(old, new)))
    if "p4_holds" not in o:
        res["mutants"].append({"mutant": name, "rule": rule, "crashed": True, "detail": o})
        continue
    p4_fail = sorted(k for k, v in o["p4_holds"].items() if base["p4_holds"].get(k) and not v)
    va_fail = sorted(k for k, v in o["va4_as_expected"].items() if base["va4_as_expected"].get(k) and not v)
    res["mutants"].append({"mutant": name, "rule": rule, "p4r4_scenarios_that_fail": p4_fail, "va4_rows_that_fail": va_fail,
                           "detected": bool(p4_fail or va_fail)})
res["summary"] = {"mutants": len(MUTANTS), "detected": sum(1 for m in res["mutants"] if m.get("detected")),
                  "not_detected": [m["mutant"] for m in res["mutants"] if "detected" in m and not m["detected"]],
                  "errors": [m["mutant"] for m in res["mutants"] if "detected" not in m]}
print(json.dumps(res, indent=1))
