#!/usr/bin/env python3
"""RV5-B-A12 — HO-0001 §3.2 machine classes x OP-7 x adversaries against the revision-5 trust-state rules
(review r5 reviewer B, AR-0012). Pure computation; scratch-free.

Instruments (loaded by path, NOT modified): the architect's `evidence/r5/P4r5-conformance-oracle.py` (revision-5 currency
naming the TSS, `eligible_release_r5`, `accept_binary`, `persist_clock_high_water`, world W11) and, through it, the retained
revision-4 functions of `evidence/P4r4-trust-state-model.py` (`evaluate_machine`, `eligible_use`, anchors, pins, witnesses).
The harness (machine constructions, adversary deliveries, the questions asked of each row) is this review's.

World (P4r5 W11): t1, t5, t9 (revokes release R7), t10, t11 (publishes registration g11 and binary B11); release R7 is
revoked at t9. Question per row: what is effective, which operation classes are allowed, is the revoked R7 an eligible policy
root for use, is C3 allowed with a currency proof that names the effective state, and is the label ever `current`.

Adversaries: A5-strip (the machine receives nothing newer than t5), A5-t9 (up to t9), A2/A5-full (everything), TS-thief (a
descendant t12x issued after the anchor, dropping nothing), CLOCK-back (local clock 395 days earlier), PIN-writable.
Machine classes: M1 first install (after gov-admit; human confirm-state of the fingerprint then published), M1s first install
typing a stale channel page (t5) (RS-B1), M2 clean CI runner (pin at t11 1 day / 20 days / 100 days; OP-7 (c) witnesses),
M3 restored from backup (human anchor t5, 400 days), M4 old epoch (t5, 20 days), M5 no epoch, M6 two machines (t5 and t11),
M7 offline long (t5, 1095 days), M8 a machine after a second `gov-admit` run with R-ADM-8 applied to its existing verifier
trust store (reference executor behaviour: every run moves the store aside), M9 CI runner with an expired admission record.

Output: JSON on stdout.
"""
import copy, importlib.util, json, os, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
R5 = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r5")
s = importlib.util.spec_from_file_location("p4r5", os.path.join(R5, "P4r5-conformance-oracle.py"))
p5 = importlib.util.module_from_spec(s)
s.loader.exec_module(p5)
m = p5.m
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR

R7 = next(x for x in p5.W11 if x.get("d") == "R7") if any(x.get("d") == "R7" for x in p5.W11) else m.release("R7", 7)
R7 = dict(R7, units={})
ST = {s_["d"]: s_ for s_ in p5.W11 if s_.get("kind") == "tss"}
BASE = [x for x in p5.W11 if x.get("kind") != "tss"]
T12x = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 60)
REG_R7 = p5.rrs("g7", "4.1.7", 7, "R7", "C7", units={})


def deliver(adv):
    tss_by = {"A5-strip": ["t1", "t5"], "A5-t9": ["t1", "t5", "t9"], "A2/A5-full": ["t1", "t5", "t9", "t10", "t11"], "TS-thief": ["t1", "t5", "t9", "t10", "t11"],
              "CLOCK-back": ["t1", "t5", "t9", "t10", "t11"], "PIN-writable": ["t1", "t5", "t9", "t10", "t11"]}[adv]
    w = BASE + [ST[d] for d in tss_by if d in ST]
    if adv == "TS-thief":
        w = w + [T12x]
    return w


def machine(cls, adv):
    if cls == "M1":
        mach = p5.anchored(11, "t11", 0)
    elif cls == "M1s":
        mach = p5.anchored(5, "t5", 0)
    elif cls == "M2-pin1d":
        mach = {"pins": [m.pin(11, "t11", 1)]}
    elif cls == "M2-pin20d":
        mach = {"pins": [m.pin(11, "t11", 20)]}
    elif cls == "M2-pin100d":
        mach = {"pins": [m.pin(11, "t11", 100)]}
    elif cls in ("M2-witness", "M5", "M8-readmitted"):
        mach = {}
    elif cls == "M3":
        mach = p5.anchored(5, "t5", 400)
    elif cls == "M4":
        mach = p5.anchored(5, "t5", 20)
    elif cls == "M6-A":
        mach = p5.anchored(11, "t11", 2)
    elif cls == "M6-B":
        mach = p5.anchored(5, "t5", 2)
    elif cls == "M7":
        mach = p5.anchored(5, "t5", 1095)
    elif cls == "M9-record-expired":
        mach = {"pins": [m.pin(11, "t11", 1)]}
    else:
        raise KeyError(cls)
    mach = copy.deepcopy(mach)
    if adv == "PIN-writable":
        for p in mach.get("pins", []):
            p["writable_by_euid"] = True
    return mach


ANCHOR_AGE_DAYS = {"M1": 0, "M1s": 0, "M3": 400, "M4": 20, "M6-A": 2, "M6-B": 2, "M7": 1095}


def with_clock_high_water(cls, mach, w):
    """Revision 5 (24 §8): on a machine with a verifier trust store every ingested verified non-future statement raised the
    clock high-water. The store was last written when the machine was last online (its anchor time); CI runners, M5 and M8
    have no store content."""
    if cls not in ANCHOR_AGE_DAYS:
        return mach
    at = NOW - ANCHOR_AGE_DAYS[cls] * DAY
    ingested = [x for x in w if x.get("issued_at", 0) <= at]
    return p5.persist_clock_high_water(mach, ingested, at)


def row(cls, op7, adv):
    w = deliver(adv)
    mach = with_clock_high_water(cls, machine(cls, adv), w)
    now = NOW - 395 * DAY if adv == "CLOCK-back" else NOW
    if cls == "M2-witness" and op7 == "c":
        w = w + [m.witness("w11", 11, "t11", NOW - 2 * HOUR, NOW + 100 * HOUR)] if adv not in ("A5-strip", "A5-t9") else w + [m.witness("w5", 5, "t5", NOW - 200 * DAY, NOW - 190 * DAY)]
    K, ts, fr, info = m.evaluate_machine(w, mach, now, op7)
    eff = ts.get("eff")
    tpsS = m.tps_state(K)
    r7 = m.eligible_use(R7, K, ts, tpsS)
    c3 = "C3" in fr["allowed"] and p5.currency_covers_effective(ts, fr, mach, now)
    res = {"effective_tss": eff["d"] if eff else None, "allowed": fr["allowed"], "axis": fr["axis"][:110],
           "revoked_R7_eligible_for_use": r7["eligible"] and ("C1" in fr["allowed"]), "C3_with_currency_naming_effective": c3,
           "label_says_current": "current" in fr["axis"].lower().replace("currency", "")}
    if cls == "M9-record-expired":
        res["genuine_binary_rule"] = "ADMISSION_RECORD_EXPIRED: C0 only (31 GB-2); the remedy is gov-admit, which moves the verifier trust store aside (M8)"
        res["allowed_after_GB"] = ["C0"]
    if cls == "M8-readmitted":
        res["per_project_record_after_R-ADM-8"] = None
        res["downgrade_detection_E10_before"] = m.eligible_use(dict(R7, seq=7), K, ts, tpsS, project_record_seq=11)["reasons"]
        res["downgrade_detection_E10_after"] = m.eligible_use(dict(R7, seq=7), K, ts, tpsS, project_record_seq=None)["reasons"]
    return res


CLASSES = ["M1", "M1s", "M2-pin1d", "M2-pin20d", "M2-pin100d", "M2-witness", "M3", "M4", "M5", "M6-A", "M6-B", "M7", "M8-readmitted", "M9-record-expired"]
ADVS = ["A5-strip", "A5-t9", "A2/A5-full", "TS-thief", "CLOCK-back", "PIN-writable"]
rows = {}
for cls in CLASSES:
    for op7 in ("a", "b", "c", "d"):
        for adv in ADVS:
            if adv == "PIN-writable" and not cls.startswith(("M2-pin", "M9")):
                continue
            try:
                rows[f"{cls}|OP-7 ({op7})|{adv}"] = row(cls, op7, adv)
            except Exception as e:  # noqa: BLE001
                rows[f"{cls}|OP-7 ({op7})|{adv}"] = {"error": repr(e)[:200]}

summary = {
    "rows": len(rows),
    "errors": [k for k, v in rows.items() if "error" in v],
    "rows_saying_current": [k for k, v in rows.items() if v.get("label_says_current")],
    "rows_where_revoked_R7_is_eligible_for_use": [k for k, v in rows.items() if v.get("revoked_R7_eligible_for_use")],
    "rows_where_C3_is_allowed_on_a_state_below_t9": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") in ("t1", "t5")],
    "rows_where_C3_is_allowed_on_the_thief_descendant": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") == "t12x"],
    "rows_where_C1_C2_run_on_the_thief_descendant": [k for k, v in rows.items() if v.get("effective_tss") == "t12x" and "C1" in v.get("allowed", [])],
}
print(json.dumps({"probe": "RV5-B-A12 machine classes under revision-5 rules (AR-0012)", "summary": summary, "rows": rows}, indent=1, sort_keys=True, default=str))
