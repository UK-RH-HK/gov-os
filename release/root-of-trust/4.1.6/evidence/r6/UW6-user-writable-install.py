#!/usr/bin/env python3
"""UW6 — operation classes reachable on a user-writable installation, against the revision-6 statement of RV5-M8 option (a)
(`31` GB-4, `24` §4.2, `21` OP-7/OP-12/OP-14, `12` RT-138). RV5-D-A03 re-run on the revision-6 reference executor.

Revision 6 chooses RV5-M8 option (a) (restatement; no rule change): on an installation whose executable or admission record is
writable by the governed account, every anchoring ceremony and C3 are refused (GB-4), and account-location pins fail the
integrity predicate. The reachable classes are therefore:
    OP-7 (a) anchored only                 C0
    OP-7 (b) maximum anchor age            C0
    OP-7 (c) witnesses, none held          C0
    OP-7 (c) witnesses at threshold held   C0–C2   (C3 refused by GB-4)
    OP-7 (d) compiled epoch                C0–C2
    administrator-protected pin (any OP-7) C0–C2   (C3 refused by GB-4 on the user-writable executable)
The burden named in `21`: governed use (C1–C2) on a workstation needs, under (a)/(b)/(c)-without-witnesses, an
administrator-protected installation or system pin; C3 always needs a protected installation.
Phase 4 path of a legacy consumer on a user-writable workstation: `gov-admit` installs into the user location and writes the
record; the admitted binary's C3 (`update --apply`) and `confirm-state` are refused; the project stays `LEGACY` until an
administrator-protected installation exists (`11` Phase 4, revision 6).

Computation: `gov_run` of `gov_admit_reference_r6.py` (executed) for every action on an admitted binary installed in a user-owned
directory, and on one installed under a directory this uid cannot write when available; the retained P4r4 decision rule
(`evaluate_machine`, loaded through P4r6) for the anchoring options such a machine has under OP-7 (a)–(d), with and without
witnesses. Attribution: questions follow `4.1.6-review-r5/D-synthesis/evidence/probes/RV5-D-A03-user-writable-install-anchoring.py`
(AR-0014); code re-typed.
Environment: SCRATCH. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = tempfile.mkdtemp(prefix="uw6-", dir=os.environ["SCRATCH"])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GA = load("gov_admit_reference_r6", os.path.join(HERE, "gov_admit_reference_r6.py"))
P6 = load("p4r6", os.path.join(HERE, "P4r6-conformance-oracle.py"))
p5, m = P6.p5, P6.m
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
LIN = "sha256:" + "1" * 64
ACTIONS = ("C0", "C1", "C2", "C3", "confirm-root", "confirm-state", "trust-gate-confirm")


def admitted(exe_dir, rec_dir):
    exe = os.path.join(exe_dir, "gov")
    data = b"#!/bin/sh\n# genuine admitted binary stand-in\n"
    inst = GA.install_from_buffer(data, exe, GA.sha256d(data))
    rec = {"binary_digest": GA.sha256d(data), "target": "x86_64-linux", "release_id": "R8", "lineage": LIN, "state_fingerprint": "gov-fc:11111111:10:" + "0" * 64,
           "admitted_at": 0, "admitter_digest": "sha256:adm", "valid_until": None, "location_protected": inst["location_protected"]}
    GA.write_admission_record(rec, rec_dir, LIN)
    return exe, inst["location_protected"]


exe, prot = admitted(os.path.join(SCR, "home", ".local", "bin"), os.path.join(SCR, "home", ".local", "state", "gov", "trust"))
gb_user = {a: GA.gov_run(exe, a, os.path.join(SCR, "home", ".local", "state", "gov", "trust"), 1, [], "C0_only")["result"] for a in ACTIONS}

W = P6.W11
WIT = [m.witness("w11", 11, "t11", NOW - 2 * HOUR, NOW + 20 * HOUR, signers=("fw1", "fw2"))]
machines = {
    "fresh_store_no_anchor": (W, {"vts": {"anchors": []}}),
    "account_location_pin_writable_by_euid": (W, {"pins": [m.pin(11, "t11", 1, writable_by_euid=True)], "vts": {"anchors": []}}),
    "witnesses_at_threshold_held": (W + WIT, {"vts": {"anchors": []}}),
    "administrator_protected_system_pin": (W, {"pins": [m.pin(11, "t11", 1)], "vts": {"anchors": []}}),
}
decision = {}
for name, (K, mach) in machines.items():
    decision[name] = {}
    for op7 in ("a", "b", "c", "d"):
        _, ts, fr, _ = m.evaluate_machine(K, mach, NOW, op7)
        decision[name][op7] = {"axis": fr["axis"].split("(")[0].strip(), "allowed": fr["allowed"]}


def reach(rows, op7):
    allowed = set()
    for r in rows:
        allowed |= set(decision[r][op7]["allowed"])
    if gb_user["C3"] != "ALLOWED":
        allowed.discard("C3")
    return sorted(allowed)


computed = {
    "OP-7 (a)": reach(["fresh_store_no_anchor", "account_location_pin_writable_by_euid"], "a"),
    "OP-7 (b)": reach(["fresh_store_no_anchor", "account_location_pin_writable_by_euid"], "b"),
    "OP-7 (c) no witnesses held": reach(["fresh_store_no_anchor", "account_location_pin_writable_by_euid"], "c"),
    "OP-7 (c) witnesses at threshold held": reach(["witnesses_at_threshold_held"], "c"),
    "OP-7 (d)": reach(["fresh_store_no_anchor", "account_location_pin_writable_by_euid"], "d"),
    "administrator-protected system pin, OP-7 (a)": reach(["administrator_protected_system_pin"], "a"),
}
STATED = {  # the revision-6 table (`31` GB-4, `24` §4.2 note, `21` OP-7)
    "OP-7 (a)": ["C0"], "OP-7 (b)": ["C0"], "OP-7 (c) no witnesses held": ["C0"], "OP-7 (c) witnesses at threshold held": ["C0", "C1", "C2"],
    "OP-7 (d)": ["C0", "C1", "C2"], "administrator-protected system pin, OP-7 (a)": ["C0", "C1", "C2"],
}
phase4 = {"gov-admit installs into the user location": prot is False,
          "update --apply (C3) by the admitted binary": gb_user["C3"], "confirm-state": gb_user["confirm-state"],
          "stated outcome": "project stays LEGACY; C0 only under OP-7 (a)/(b); remedy: administrator-protected installation or system pin"}
out = {"probe": "UW6 user-writable installation classes (AR-0015)", "euid": os.geteuid(), "install_location_protected": prot,
       "gov_run_on_admitted_user_writable_binary": gb_user, "decision_rule_by_anchoring_option": decision, "classes_reachable": computed,
       "stated_revision_6": STATED, "phase4_legacy_consumer_user_writable": phase4}
out["verdicts"] = {
    "every_stated_row_equals_computed": all(computed[k] == STATED[k] for k in STATED),
    "ceremonies_refused_on_user_writable_install": all(gb_user[a] == "TCB_WRITABLE_BY_GOVERNED_ACCOUNT" for a in ("C3", "confirm-root", "confirm-state", "trust-gate-confirm")),
    "C0_C2_not_refused_by_GB_rules": all(gb_user[a] == "ALLOWED" for a in ("C0", "C1", "C2")),
    "phase4_C3_refused_on_user_writable_install": phase4["update --apply (C3) by the admitted binary"] == "TCB_WRITABLE_BY_GOVERNED_ACCOUNT",
}
txt = json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
