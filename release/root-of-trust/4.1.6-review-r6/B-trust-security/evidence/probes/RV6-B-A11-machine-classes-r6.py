#!/usr/bin/env python3
"""RV6-B-A11 — HO-0001 §3.2 machine classes × OP-7 × adversaries against the revision-6 trust-state rules (review r6
reviewer B, AR-0016). Computed; scratch-free.

Adapted from review r5 reviewer B `RV5-B-A12-machine-classes.py` (AR-0012), with attribution: the world (P4r5 W11: t1, t5, t9
revoking R7, t10, t11), machine constructions, adversary deliveries and questions are that probe's. Changes: the revision-6
rules are applied through the architect's `evidence/r6/P4r6-conformance-oracle.py` (loaded unmodified): `evaluate_machine_r6`
(a statement refused as issued in the future disables clock-based proofs for the unit of work, CR5-B-08) and
`currency_covers_effective_r6`; R-ADM-8′ is applied to M8 (re-admission keeps the store, so the per-project record is kept);
CLOCK-back is split into "newer statements delivered" (A2/A5-full) and "every later statement withheld" (A5-strip, RS-2b).
Row added: M8b re-admitted machine offered an older genuine binary (bootstrap mode applies no accepted-TBM high-water; the
executed evidence is RV6-B-A04) — reported from that probe's verdict, not recomputed here.

Environment: REVIEW_REPO (export of 4106885). Output: JSON on stdout.
"""
import copy, importlib.util, json, os, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
R6 = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r6")
s = importlib.util.spec_from_file_location("p4r6", os.path.join(R6, "P4r6-conformance-oracle.py"))
p6 = importlib.util.module_from_spec(s)
s.loader.exec_module(p6)
p5, m = p6.p5, p6.m
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR

R7 = next(x for x in p5.W11 if x.get("d") == "R7") if any(x.get("d") == "R7" for x in p5.W11) else m.release("R7", 7)
R7 = dict(R7, units={})
ST = {s_["d"]: s_ for s_ in p5.W11 if s_.get("kind") == "tss"}
BASE = [x for x in p5.W11 if x.get("kind") != "tss"]
T12x = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 60)
TSS_BY = {"A5-strip": ["t1", "t5"], "A5-t9": ["t1", "t5", "t9"], "A2/A5-full": ["t1", "t5", "t9", "t10", "t11"], "TS-thief": ["t1", "t5", "t9", "t10", "t11"],
          "CLOCK-back-newer-delivered": ["t1", "t5", "t9", "t10", "t11"], "CLOCK-back-later-withheld": ["t1", "t5"], "PIN-writable": ["t1", "t5", "t9", "t10", "t11"]}


def deliver(adv):
    w = BASE + [ST[d] for d in TSS_BY[adv] if d in ST]
    if adv == "TS-thief":
        w = w + [T12x]
    return w


def machine(cls, adv):
    table = {"M1": lambda: p5.anchored(11, "t11", 0), "M1s": lambda: p5.anchored(5, "t5", 0), "M2-pin1d": lambda: {"pins": [m.pin(11, "t11", 1)]},
             "M2-pin20d": lambda: {"pins": [m.pin(11, "t11", 20)]}, "M2-pin100d": lambda: {"pins": [m.pin(11, "t11", 100)]}, "M2-witness": lambda: {}, "M5": lambda: {},
             "M3": lambda: p5.anchored(5, "t5", 400), "M4": lambda: p5.anchored(5, "t5", 20), "M6-A": lambda: p5.anchored(11, "t11", 2), "M6-B": lambda: p5.anchored(5, "t5", 2),
             "M7": lambda: p5.anchored(5, "t5", 1095), "M8-readmitted-store-kept": lambda: p5.anchored(11, "t11", 30), "M9-record-expired": lambda: {"pins": [m.pin(11, "t11", 1)]}}
    mach = copy.deepcopy(table[cls]())
    if adv == "PIN-writable":
        for p in mach.get("pins", []):
            p["writable_by_euid"] = True
    return mach


ANCHOR_AGE_DAYS = {"M1": 0, "M1s": 0, "M3": 400, "M4": 20, "M6-A": 2, "M6-B": 2, "M7": 1095, "M8-readmitted-store-kept": 30}


def with_clock_high_water(cls, mach, w):
    if cls not in ANCHOR_AGE_DAYS:
        return mach
    at = NOW - ANCHOR_AGE_DAYS[cls] * DAY
    return p5.persist_clock_high_water(mach, [x for x in w if x.get("issued_at", 0) <= at], at)


def row(cls, op7, adv):
    w = deliver(adv)
    mach = with_clock_high_water(cls, machine(cls, adv), w)
    now = NOW - 395 * DAY if adv.startswith("CLOCK-back") else NOW
    if cls == "M2-witness" and op7 == "c":
        w = w + ([m.witness("w11", 11, "t11", NOW - 2 * HOUR, NOW + 100 * HOUR)] if adv not in ("A5-strip", "A5-t9", "CLOCK-back-later-withheld") else [m.witness("w5", 5, "t5", NOW - 200 * DAY, NOW - 190 * DAY)])
    K, ts, fr, info = p6.evaluate_machine_r6(w, mach, now, op7)
    eff = ts.get("eff")
    tpsS = m.tps_state(K)
    r7 = m.eligible_use(R7, K, ts, tpsS)
    c3 = "C3" in fr["allowed"] and p6.currency_covers_effective_r6(ts, fr, mach, now)
    res = {"effective_tss": eff["d"] if eff else None, "allowed": fr["allowed"], "axis": fr["axis"][:120],
           "revoked_R7_eligible_for_use": r7["eligible"] and ("C1" in fr["allowed"]), "C3_with_currency_naming_effective": c3,
           "label_says_current": "current" in fr["axis"].lower().replace("currency", "")}
    if cls == "M9-record-expired":
        res["allowed_after_GB"] = ["C0"]
    if cls == "M8-readmitted-store-kept":
        res["downgrade_detection_E10_with_kept_record"] = m.eligible_use(dict(R7, seq=7), K, ts, tpsS, project_record_seq=11)["reasons"]
    return res


CLASSES = ["M1", "M1s", "M2-pin1d", "M2-pin20d", "M2-pin100d", "M2-witness", "M3", "M4", "M5", "M6-A", "M6-B", "M7", "M8-readmitted-store-kept", "M9-record-expired"]
ADVS = list(TSS_BY)
rows = {}
for cls in CLASSES:
    for op7 in ("a", "b", "c", "d"):
        for adv in ADVS:
            if adv == "PIN-writable" and not cls.startswith(("M2-pin", "M9")):
                continue
            try:
                rows["%s|OP-7 (%s)|%s" % (cls, op7, adv)] = row(cls, op7, adv)
            except Exception as e:  # noqa: BLE001
                rows["%s|OP-7 (%s)|%s" % (cls, op7, adv)] = {"error": repr(e)[:200]}
summary = {
    "rows": len(rows),
    "errors": [k for k, v in rows.items() if "error" in v],
    "rows_saying_current": [k for k, v in rows.items() if v.get("label_says_current")],
    "rows_where_revoked_R7_is_eligible_for_use": [k for k, v in rows.items() if v.get("revoked_R7_eligible_for_use")],
    "rows_where_C3_is_allowed_on_a_state_below_t9": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") in ("t1", "t5")],
    "rows_where_C3_is_allowed_on_the_thief_descendant": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") == "t12x"],
    "rows_where_C1_C2_run_on_the_thief_descendant": len([k for k, v in rows.items() if v.get("effective_tss") == "t12x" and "C1" in v.get("allowed", [])]),
    "M3_M4_M7_clock_back_newer_delivered_C3_rows": [k for k, v in rows.items() if k.split("|")[0] in ("M3", "M4", "M7") and "newer-delivered" in k and v.get("C3_with_currency_naming_effective")],
    "M3_M4_M7_clock_back_later_withheld_C3_rows (RS-2b)": [k for k, v in rows.items() if k.split("|")[0] in ("M3", "M4", "M7") and "later-withheld" in k and v.get("C3_with_currency_naming_effective")],
    "M8_store_kept_E10_detects_downgrade": all("downgrade_without_transaction" in v.get("downgrade_detection_E10_with_kept_record", []) for k, v in rows.items() if k.startswith("M8")),
}
print(json.dumps({"probe": "RV6-B-A11 machine classes under revision-6 rules (AR-0016; adapted from RV5-B-A12, AR-0012)", "summary": summary, "rows": rows}, indent=1, sort_keys=True, default=str))
