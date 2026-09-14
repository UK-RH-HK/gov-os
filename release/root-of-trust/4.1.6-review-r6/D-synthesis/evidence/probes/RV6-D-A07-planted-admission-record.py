#!/usr/bin/env python3
"""RV6-D-A07 — can pre-admission same-account code turn a first admission into a re-admission? (review r6 synthesis D,
AR-0018). Executed (reference executor `write_admission_record`, `is_first_admission`, `accept`, `gov_run`) + design.
Scratch only.

`31` R-ADM-8′: "First admission is the case where no verifier trust store exists for the lineage, or the store holds no
admission record ever written. Only at first admission is a pre-existing store moved aside and never read (AD-2)."
`31` §9 AD-2: "Same-account code executed before the first admission | fresh store at first admission (R-ADM-8′)".
The admission record is unsigned (`31` R-ADM-7′). `24` §8 places the verifier trust store in the account home.
Attack: before the first admission, same-account code creates `vts-<lineage>/admissions/<any>.json` together with the
monotonic records it wants kept (an anchor on an older genuine state, a per-project record with a weak strength vector and a
low sequence, a trust-gate confirmation). The operator then performs a genuine first admission.
Control: the same planted content without the planted record file.
Relation: reviewer C's RV6-C-M5 (design: two incompatible store specifications) — this executes the reading in which the
record lives in the account store.
Environment: REVIEW_REPO, SCRATCH, GOV. Output: JSON on stdout.
"""
import hashlib, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6world as W

SCR = tempfile.mkdtemp(prefix="da07-", dir=os.environ["SCRATCH"])
G, D1, ADM_BYTES = W.load(SCR)
GA = G["GA"]
g = lambda n: G[n]
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = g("TARGET"), g("LINEAGE"), g("ADMITTER_DIGEST")
NOW = "2026-09-14T00:00:00Z"
gm = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 10, g("T10")["digest"], {TARGET: ADM_D}, "2026-09-13T00:00:00Z")
code = GA.first_contact_code(gm)


def plant(rec_dir, with_record):
    st = GA.store_dir(rec_dir, LINEAGE)
    os.makedirs(os.path.join(st, "projects"))
    os.makedirs(os.path.join(st, "confirmations"))
    json.dump([{"sequence": 7, "digest": g("T7")["digest"], "method": "human", "operator": "planted"}], open(os.path.join(st, "anchors.json"), "w"))
    json.dump({"repository_paths": ["/work/project"], "highest_installed_sequence": 1, "strength_vector": {}, "held_registration": None}, open(os.path.join(st, "projects", "ptid-0001.json"), "w"))
    json.dump({"kind": "weakening", "decision_digest": "sha256:" + "ab" * 32, "confirmed_at": NOW, "operator": "planted"}, open(os.path.join(st, "confirmations", "weakening-planted.json"), "w"))
    if with_record:
        os.makedirs(os.path.join(st, "admissions"))
        json.dump({"binary_digest": "sha256:" + "00" * 32, "note": "any JSON file"}, open(os.path.join(st, "admissions", "planted.json"), "w"))
    return st


def first_admission(tag, with_record):
    rec_dir = os.path.join(SCR, tag)
    st = plant(rec_dir, with_record)
    r = GA.accept(g("B8_BYTES"), [code, code], g("to_stmts")(g("FULL")), TARGET, ADM_D, verifier=V, workdir=SCR, first_contact_manifest=GA.fcm_bytes(gm), compiled={"channel_quorum": 2, "lineage": None}, now=NOW)
    first = GA.is_first_admission(rec_dir, LINEAGE)
    inst = GA.install_from_buffer(g("B8_BYTES"), os.path.join(SCR, tag + "-bin", "gov"), g("B8_D"))
    rec = {"schema": "governance-os.admission-record/2", "binary_digest": g("B8_D"), "target": TARGET, "release_id": "R8", "lineage": LINEAGE, "first_contact_code": code,
           "admitted_at": NOW, "admitter_digest": ADM_D, "valid_until": None, "location_protected": inst["location_protected"]}
    _, store, moved = GA.write_admission_record(rec, rec_dir, LINEAGE)
    kept = sorted(os.path.relpath(os.path.join(dp, f), store) for dp, dn, fn in os.walk(store) for f in fn)
    return {"admission": r["result"], "is_first_admission": first, "moved_aside": moved is not None, "files_in_store_after_admission": kept,
            "planted_anchor_kept": "anchors.json" in kept, "planted_project_record_kept": "projects/ptid-0001.json" in kept, "planted_confirmation_kept": "confirmations/weakening-planted.json" in kept,
            "gov_run_C2": GA.gov_run(os.path.join(SCR, tag + "-bin", "gov"), "C2", rec_dir, NOW, [], "C0_C2")["result"]}


out = {"probe": "RV6-D-A07 planted admission record converts first admission into re-admission (AR-0018)", "executor_sha256": hashlib.sha256(open(W.R6_PATH, "rb").read()).hexdigest(),
       "attack_planted_record": first_admission("attack", True), "control_no_planted_record": first_admission("control", False)}
t31, t24, t17 = W.pack("31-INDEPENDENT-ADMISSION.md"), W.pack("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md"), W.pack("17-MONOTONIC-TRUST-STATE.md")
out["design"] = {"31_R_ADM_8_prime": W.lines(t31, lambda l: l.startswith("| **R-ADM-8′**")), "31_AD_2": W.lines(t31, lambda l: l.startswith("| AD-2")),
                 "31_R_ADM_7_prime_unsigned_record_fields": W.lines(t31, lambda l: l.startswith("| **R-ADM-7′**")),
                 "24_s8_location": W.lines(t24, lambda l: l.startswith("**Location:**")),
                 "any_rule_authenticating_the_record_used_for_the_first_admission_test": bool(re.search(r"record[^.\n]*(?:signed|MAC|authenticat)[^.\n]*first admission|first admission[^.\n]*(?:signed|authenticat)", t31, re.I))}
a, c = out["attack_planted_record"], out["control_no_planted_record"]
out["verdicts"] = {
    "genuine_admission_accepted_in_both": a["admission"] == c["admission"] == "ACCEPTED",
    "control_first_admission_moves_planted_store_aside": c["is_first_admission"] and c["moved_aside"] and not c["planted_anchor_kept"],
    "attack_planted_record_suppresses_move_aside": (not a["is_first_admission"]) and not a["moved_aside"],
    "attack_planted_anchor_project_record_and_confirmation_survive_first_admission": a["planted_anchor_kept"] and a["planted_project_record_kept"] and a["planted_confirmation_kept"],
    "no_rule_authenticates_the_record_that_decides_first_admission": not out["design"]["any_rule_authenticating_the_record_used_for_the_first_admission_test"],
}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>").replace(W.REPO, "<export>"))
