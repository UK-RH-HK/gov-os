#!/usr/bin/env python3
"""RV6-D-A04 — would the revision-6 plan, register and instruments detect the defects found by review r6? (review r6 synthesis D,
AR-0018). Computed from committed text and instruments. Mirrors the architect's DA07r6 (AR-0015), which asked the question for
review r5's defects (question and three-part criterion copied with attribution; defect list and patterns are this review's).

For each defect: (a) plan RT rows whose text names the defect's distinguishing fact; (b) register decisions that name the
selector, party or field; (c) a calculator atom or a committed reference-instrument output that exercises it. A defect counts as
detected when (a), (b) and (c) are all non-empty. Separately: RT-159, RT-162 and RT-183 compare the implementation's calculator
or register with executed results or checks derived from the same register; the attack records whether any of them has an
input independent of the register (if not, a selector absent from the register is absent from both sides and they pass).
Environment: REVIEW_REPO. Output: JSON on stdout.
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
regtext = {d["id"]: json.dumps(d, ensure_ascii=False) for d in REG["decisions"]}
atoms = {a for v in CS6.ATOMS.values() for a in v}
inst = {n: open(os.path.join(EV, n), encoding="utf-8").read() for n in ("FA6-first-admission.json", "ENV6-build-environment.json", "ADM6-admission-transactions.json",
                                                                        "P4r6-conformance-oracle.json", "UW6-user-writable-install.json", "CON6-first-hand-constitutional-content.json")}
inst["CSI6-selftest.json"] = open(os.path.join(EV, "CSI6-selftest.json"), encoding="utf-8").read()
inst["STATEMENTS-CHECK.json"] = open(os.path.join(EV, "STATEMENTS-CHECK.json"), encoding="utf-8").read()
inst["LAY6-comparison.json"] = open(os.path.join(EV, "LAY6", "LAY6-comparison.json"), encoding="utf-8").read()


def rows(*pats):
    return sorted((k for k, v in rt.items() if all(re.search(p, v, re.I) for p in pats)), key=lambda x: int(x.split("-")[1]))


def reg(*pats):
    return sorted(k for k, v in regtext.items() if all(re.search(p, v, re.I) for p in pats))


def ref(files, *pats):
    return sorted(f for f in files if all(re.search(p, inst[f], re.I) for p in pats))


D = {
    "RV6-B-H1 first-contact manifest composed by the trust-state publisher; sources carry it": {
        "plan_rows": rows(r"publisher|compos", r"first-contact|gov-admit"), "register": reg(r"DR-0[2-6]", r"publisher|compos"),
        "calculator_atom": [a for a in atoms if a in ("fcpub",)], "reference": ref(["FA6-first-admission.json"], r"publisher|compos")},
    "RV6-D-A01 source designation and procedure text printed by an unadmitted binary or carrier": {
        "plan_rows": rows(r"fc-procedure|designat|printed"), "register": reg(r"designat|fc-procedure|procedure text"),
        "calculator_atom": [a for a in atoms if a in ("desig",)], "reference": ref(["FA6-first-admission.json"], r"designat|fc-procedure")},
    "RV6-B-H2 platform package submitter selects the admitter": {
        "plan_rows": rows(r"submit"), "register": reg(r"submit"), "calculator_atom": [a for a in atoms if a in ("submit",)], "reference": ref(["FA6-first-admission.json"], r"submit")},
    "RV6-B-H2 / D-A08 replayed or stored first-contact value without a mandatory age bound": {
        "plan_rows": rows(r"valid_until|FIRST_CONTACT_MANIFEST_EXPIRED|replay"), "register": reg(r"valid_until|replay|maximum age"),
        "calculator_atom": [a for a in atoms if a in ("replay",)], "reference": ref(["FA6-first-admission.json"], r"FIRST_CONTACT_MANIFEST_EXPIRED")},
    "RV6-B-H3 environment recipe or component selection authored by an unassigned party": {
        "plan_rows": rows(r"recipe"), "register": reg(r"DR-13", r"author|recipe[^\"]*(?:reviewed|registered source|established)"),
        "calculator_atom": [a for a in atoms if a in ("env_author", "recipe")], "reference": ref(["ENV6-build-environment.json"], r"recipe[^\"]*(?:inject|wrapper)|A07")},
    "RV6-B-H3 supplier class by label; upstream key named by the manifest": {
        "plan_rows": rows(r"supplier.class", r"label|pinned|disjoint|key"), "register": reg(r"DR-13", r"pinned upstream key|label|disjoint"),
        "calculator_atom": [], "reference": ref(["ENV6-build-environment.json"], r"label|author-generated key|A08|A09")},
    "RV6-B-M1 / D-A02 re-admission does not apply the kept store (anchors, negatives, TBM high-water)": {
        "plan_rows": rows(r"re-admi|re-runs `gov-admit`", r"stale|older (?:first-contact|code|state|binary)|below (?:the )?(?:store|anchor|high-water)|BINARY_T0_ROLLBACK"),
        "register": reg(r"DR-10", r"anchor|negative|high-water"), "calculator_atom": [], "reference": ref(["ADM6-admission-transactions.json", "FA6-first-admission.json"], r"re-admi", r"BINARY_T0_ROLLBACK|revok")},
    "RV6-B-M2 renderer merges atoms of different classes": {
        "plan_rows": rows(r"statements_check|RT-127", r"atom|render"), "register": [], "calculator_atom": [], "reference": ref(["STATEMENTS-CHECK.json"], r"atom set|atom-level")},
    "RV6-B-M3 / D-A09 register completeness over rule ids, not inputs": {
        "plan_rows": rows(r"register_check|DECISION_REGISTER", r"field|schema|every input"), "register": [], "calculator_atom": [], "reference": []},
    "RV6-C-M2 crash inside the first-install layout migration": {
        "plan_rows": rows(r"crash", r"layout|each (?:migration|layout) step|move"), "register": reg(r"crash|layout migration"), "calculator_atom": [], "reference": ref(["LAY6-comparison.json"], r"crash")},
    "RV6-C-M3 per-project record identity under worktree, fork or second clone": {
        "plan_rows": rows(r"worktree|fork|second clone|moved checkout|bind-mount"), "register": reg(r"project_trust_id", r"path"), "calculator_atom": [], "reference": []},
    "RV6-C-M4 a remedy re-records strength or clears a pending gate": {
        "plan_rows": rows(r"reinstall|remedy", r"STRENGTH|pending|gate"), "register": reg(r"re-record|pending"), "calculator_atom": [], "reference": []},
    "RV6-C-M5 admission store versus account verifier trust store": {
        "plan_rows": rows(r"root-owned (?:admission )?store|non-root|another user"), "register": reg(r"DR-(?:09|10)", r"root-owned|two stores|account"), "calculator_atom": [], "reference": ref(["ADM6-admission-transactions.json"], r"root-owned")},
    "RV6-D-A03 R-CON-5 listing of a new security-relevant constitutional file": {
        "plan_rows": rows(r"REGISTRATION_CHANGE_GATE_REQUIRED|registration_change", r"new constitutional file|Capability Acceptance|security_classified|inventory"),
        "register": reg(r"R-CON-5", r"security_classified|inventory"), "calculator_atom": [], "reference": ref(["CSI6-selftest.json"], r"security_classified")},
    "RV6-D-A07 planted admission record suppresses the first-admission move-aside": {
        "plan_rows": rows(r"planted|forged|any (?:file|record)", r"admission record|store", r"first admission"), "register": reg(r"DR-10", r"authentic|signed|planted"), "calculator_atom": [], "reference": ref(["ADM6-admission-transactions.json"], r"planted")},
}
for k, v in D.items():
    v["detected"] = bool(v["plan_rows"]) and bool(v["register"]) and bool(v["calculator_atom"] or v["reference"])
self_ref = {}
for r in ("RT-159", "RT-162", "RT-183", "RT-128", "RT-131"):
    t = rt.get(r, "")
    self_ref[r] = {"text": t[:400], "input_independent_of_register": bool(re.search(r"independent|not derived from the register|held-out|reviewer", t, re.I))}
out = {"probe": "RV6-D-A04 plan regression detection for review r6 defects (AR-0018)", "plan_rt_rows": len(rt), "register_decisions": len(regtext), "defects": D,
       "self_referential_tests": self_ref,
       "summary": {"defects": len(D), "detected": sum(v["detected"] for v in D.values()), "not_detected": [k for k, v in D.items() if not v["detected"]]}}
out["verdicts"] = {"undetected_defects": len(out["summary"]["not_detected"]), "no_self_referential_test_has_an_independent_input": not any(v["input_independent_of_register"] for v in self_ref.values())}
print(json.dumps(out, indent=1, ensure_ascii=False))
