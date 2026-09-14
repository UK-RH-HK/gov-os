#!/usr/bin/env python3
"""RV5-D-A03 — genuine-binary rule GB-4 against anchoring on a user-writable install (review r5 synthesis D, AR-0014).

Pack statements under test (design, cdb4e14):
  * `31` GB-4: "C3 and every ceremony additionally require that the executable, the admission record and every ancestor
    directory satisfy the TCB-location predicate ... A user-writable install is therefore C0–C2 only."
  * `31` GB-1 lists the ceremonies: `confirm-root`, `confirm-state`, in-gate fingerprints, trust-gate confirmations.
  * `24` §3.2: anchoring events are pins (system pin directory, or the account location only under the integrity
    predicate), human confirmation (`gov trust confirm-state`), in-gate confirmation (C3 transitions), witnesses (OP-7 (c)),
    retained anchors. `31` R-ADM-8 moves any pre-admission verifier trust store aside, so no retained anchor survives.
  * `24` §4.3: `UNANCHORED` under OP-7 (a) or (b) → C0 only.
  * `24` §4.2 lists `trust confirm-root`/`confirm-state` in C0; `12` RT-138 expects "C0–C2 still available".

Computation: the reference executor's `gov_run` (unmodified) for every action on an admitted binary installed in a
user-owned directory; the retained P4r4 decision rule (`evaluate_machine`, unmodified) for the anchoring options such a
machine has, under OP-7 (a)–(d).

Environment: REVIEW_REPO (export of cdb4e14), SCRATCH. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
EV = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence")
SCR = tempfile.mkdtemp(prefix="rv5d-a03-", dir=os.environ["SCRATCH"])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GA = load("gov_admit_reference", os.path.join(EV, "r5", "gov_admit_reference.py"))
P5 = load("p4r5_oracle", os.path.join(EV, "r5", "P4r5-conformance-oracle.py"))
m = P5.m
NOW, DAY = P5.NOW, P5.DAY

# ------------------------------------------------------------------ admitted binary in a user-owned location
exe = os.path.join(SCR, "home", ".local", "bin", "gov")
data = b"#!/bin/sh\n# genuine admitted binary stand-in\n"
inst = GA.install_from_buffer(data, exe, GA.sha256d(data))
rec_dir = os.path.join(SCR, "home", ".local", "state", "gov", "trust")
rec = {"binary_digest": GA.sha256d(data), "target": "x86_64-linux", "release_id": "R8", "lineage": "sha256:" + "1" * 64,
       "state_fingerprint": "gov-state:11111111:10:" + "0" * 32, "admitted_at": 0, "admitter_digest": "sha256:adm", "valid_until": None,
       "location_protected": inst["location_protected"]}
GA.write_admission_record(rec, rec_dir, rec["lineage"])
gb = {a: GA.gov_run(exe, a, rec_dir, 1, [], "C0_only")["result"] for a in ("C0", "C1", "C2", "C3", "confirm-root", "confirm-state", "trust-gate-confirm")}

# ------------------------------------------------------------------ anchoring options on that machine (P4r4 decision rule)
W = P5.W11
machines = {
    "fresh_store_after_admission_no_anchor": {"vts": {"anchors": []}},
    "account_location_pin_writable_by_euid": {"pins": [m.pin(11, "t11", 1, writable_by_euid=True)], "vts": {"anchors": []}},
    "control_system_pin_not_writable (admin-provisioned)": {"pins": [m.pin(11, "t11", 1)], "vts": {"anchors": []}},
    "control_human_anchor (what confirm-state would record)": {"vts": {"anchors": [{"seq": 11, "digest": "t11", "at": NOW, "method": "human"}]}},
}
decision = {}
for name, mach in machines.items():
    decision[name] = {}
    for op7 in ("a", "b", "c", "d"):
        K, ts, fr, info = m.evaluate_machine(W, mach, NOW, op7)
        decision[name][op7] = {"axis": fr["axis"].split("(")[0], "allowed": fr["allowed"]}

reachable = {}
for op7 in ("a", "b", "c", "d"):
    # a non-root user can create neither a non-writable system pin nor run confirm-state (GB-4); no witness assumed
    allowed = set(decision["fresh_store_after_admission_no_anchor"][op7]["allowed"]) | set(decision["account_location_pin_writable_by_euid"][op7]["allowed"])
    reachable[op7] = sorted(allowed - ({"C3"} if gb["C3"] != "ALLOWED" else set()))

pack = open(os.path.join(REPO, "release", "root-of-trust", "4.1.6", "31-INDEPENDENT-ADMISSION.md")).read()
plan = open(os.path.join(REPO, "release", "root-of-trust", "4.1.6", "12-ACCEPTANCE-TEST-PLAN.md")).read()
fresh = open(os.path.join(REPO, "release", "root-of-trust", "4.1.6", "24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md")).read()
out = {
    "probe": "RV5-D-A03 user-writable install: GB-4 versus anchoring (AR-0014)",
    "install_location_protected": inst["location_protected"],
    "gov_run_on_admitted_user_writable_binary": gb,
    "decision_rule_by_anchoring_option": decision,
    "classes_reachable_without_admin_or_witness": reachable,
    "pack_text": {
        "31_GB-4_claims_C0-C2": "A user-writable install is therefore C0–C2 only" in pack,
        "12_RT-138_expects_C0-C2": bool(re.search(r"RT-138[^\n]*C0–C2 still available", plan)),
        "24_4.2_lists_confirm-state_in_C0": bool(re.search(r"\*\*C0\*\*[^\n]*confirm-state", fresh)),
    },
}
out["verdicts"] = {
    "confirm_state_refused_on_user_writable_install": gb["confirm-state"] == "TCB_WRITABLE_BY_GOVERNED_ACCOUNT",
    "C2_not_refused_by_GB_rules_alone": gb["C2"] == "ALLOWED",
    "account_pin_ignored": decision["account_location_pin_writable_by_euid"]["a"]["allowed"] == ["C0"],
    "op7_a_reachable_C0_only": reachable["a"] == ["C0"],
    "op7_b_reachable_C0_only": reachable["b"] == ["C0"],
    "op7_d_reachable_C0_C2": reachable["d"] == ["C0", "C1", "C2"],
    "pack_claim_C0_C2_false_under_a_b": reachable["a"] == ["C0"] and out["pack_text"]["31_GB-4_claims_C0-C2"],
}
txt = json.dumps(out, indent=1, default=str).replace(SCR, "<scratch>").replace(REPO, "<repo>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
