#!/usr/bin/env python3
"""BA11r7 — HO-0001 §3.2 machine classes × adversaries under the CP-1 anchoring parameters (reviewer B's RV6-B-A11, AR-0016, re-expressed)
(AR-0019). Computed; scratch-free.

Reviewer B's probe (adapted from RV5-B-A12, AR-0012) evaluates machine classes under revision-6 rules through `../r6/P4r6-conformance-oracle.py`
for OP-7 (a)–(d). CP-1 implements OP-7 (a) only. This re-expression loads the same oracle unmodified, sets the retained model's parameters to the
CP-1 ceilings (pin validity 7 days for CI pins, C3 currency window 24 hours), evaluates only OP-7 (a), and applies the CP-1 anchor-validity rule
(a workstation anchor older than 90 days, or a CI anchor older than 7 days, leaves C0 only; `24` §4.3), R-CLK-1 (a clock earlier than the
machine's recorded high water or its anchor time leaves C0-R only; `24` §4.5; executed in ADM7 CLK) and the CP-1 currency rule (a C3 currency
proof consists of the state codes both first-contact sources publish, which name only the latest state they verified first-hand, R-FCS-2;
`24` §4.4). The rules are applied on top of the oracle's decision; the unmodified oracle decision is kept per row. The machine list, world, adversary
deliveries and questions are reviewer B's (copied with attribution); the witness machine M2-witness is removed by exclusion (EX-01).
Environment: none. Output: JSON on stdout.
"""
import copy, importlib.util, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("p4r6", os.path.join(HERE, "..", "r6", "P4r6-conformance-oracle.py"))
p6 = importlib.util.module_from_spec(s)
s.loader.exec_module(p6)
p5, m = p6.p5, p6.m
NOW, DAY, HOUR = m.NOW, m.DAY, m.HOUR
m.P["pin_max_validity_days"] = 7
m.P["c3_currency_window_hours"] = 24
R7 = next(x for x in p5.W11 if x.get("d") == "R7") if any(x.get("d") == "R7" for x in p5.W11) else m.release("R7", 7)
R7 = dict(R7, units={})
ST = {s_["d"]: s_ for s_ in p5.W11 if s_.get("kind") == "tss"}
BASE = [x for x in p5.W11 if x.get("kind") != "tss"]
T12x = m.tss(12, "t12x", prior=p5.PRIOR11, pol=(2, "TPS2"), revs=["R7"], arts=["g11", "B11"], issued_at=NOW - 60)
TSS_BY = {"A5-strip": ["t1", "t5"], "A5-t9": ["t1", "t5", "t9"], "A2/A5-full": ["t1", "t5", "t9", "t10", "t11"], "TS-thief": ["t1", "t5", "t9", "t10", "t11"],
          "CLOCK-back-newer-delivered": ["t1", "t5", "t9", "t10", "t11"], "CLOCK-back-later-withheld": ["t1", "t5"], "PIN-writable": ["t1", "t5", "t9", "t10", "t11"]}
SKEW = getattr(p5, "P5", {}).get("clock_skew_seconds", 300)
ANCHOR_AGE_DAYS = {"M1": 0, "M1s": 0, "M3": 400, "M4": 20, "M6-A": 2, "M6-B": 2, "M7": 1095, "M8-readmitted-store-kept": 30}
PIN_AGE_DAYS = {"M2-pin1d": 1, "M2-pin5d": 5, "M2-pin20d": 20, "M2-pin100d": 100, "M9-record-expired": 1}


def deliver(adv):
    w = BASE + [ST[d] for d in TSS_BY[adv] if d in ST]
    return w + [T12x] if adv == "TS-thief" else w


def machine(cls, adv):
    table = {"M1": lambda: p5.anchored(11, "t11", 0), "M1s": lambda: p5.anchored(5, "t5", 0), "M2-pin1d": lambda: {"pins": [m.pin(11, "t11", 1)]}, "M2-pin5d": lambda: {"pins": [m.pin(11, "t11", 5)]},
             "M2-pin20d": lambda: {"pins": [m.pin(11, "t11", 20)]}, "M2-pin100d": lambda: {"pins": [m.pin(11, "t11", 100)]}, "M5": lambda: {},
             "M3": lambda: p5.anchored(5, "t5", 400), "M4": lambda: p5.anchored(5, "t5", 20), "M6-A": lambda: p5.anchored(11, "t11", 2), "M6-B": lambda: p5.anchored(5, "t5", 2),
             "M7": lambda: p5.anchored(5, "t5", 1095), "M8-readmitted-store-kept": lambda: p5.anchored(11, "t11", 30), "M9-record-expired": lambda: {"pins": [m.pin(11, "t11", 1)]}}
    mach = copy.deepcopy(table[cls]())
    if adv == "PIN-writable":
        for p in mach.get("pins", []):
            p["writable_by_euid"] = True
    return mach


def row(cls, adv):
    w = deliver(adv)
    mach = machine(cls, adv)
    if cls in ANCHOR_AGE_DAYS:
        at = NOW - ANCHOR_AGE_DAYS[cls] * DAY
        mach = p5.persist_clock_high_water(mach, [x for x in w if x.get("issued_at", 0) <= at], at)
    now = NOW - 395 * DAY if adv.startswith("CLOCK-back") else NOW
    K, ts, fr, info = p6.evaluate_machine_r6(w, mach, now, "a")
    allowed = list(fr["allowed"])
    oracle_allowed = list(allowed)
    anchor_expired = (cls in ANCHOR_AGE_DAYS and ANCHOR_AGE_DAYS[cls] > 90) or cls == "M9-record-expired"
    if anchor_expired:
        allowed = ["C0"]
    vts = mach.get("vts", {})
    high_water = max([vts.get("clock_high_water", 0)] + [a.get("at", 0) for a in vts.get("anchors", [])])
    clock_below = bool(high_water) and now + SKEW < high_water
    if clock_below:
        allowed = ["C0"]
    eff = ts.get("eff")
    tpsS = m.tps_state(K)
    r7 = m.eligible_use(R7, K, ts, tpsS)
    oracle_c3 = "C3" in allowed and p6.currency_covers_effective_r6(ts, fr, mach, now)
    sources_latest = "t12x" if adv == "TS-thief" else "t11"
    c3 = oracle_c3 and bool(eff) and eff["d"] == sources_latest
    return {"effective_tss": eff["d"] if eff else None, "allowed": allowed, "oracle_allowed": oracle_allowed, "revoked_R7_eligible_for_use": r7["eligible"] and ("C1" in allowed),
            "C3_with_currency_naming_effective": c3, "oracle_C3_with_currency_naming_effective": oracle_c3, "label_says_current": "current" in fr["axis"].lower().replace("currency", ""),
            "cp1_anchor_expired_C0": anchor_expired, "cp1_clock_below_high_water_C0_R": clock_below, "sources_latest_state": sources_latest}


CLASSES = ["M1", "M1s", "M2-pin1d", "M2-pin5d", "M2-pin20d", "M2-pin100d", "M3", "M4", "M5", "M6-A", "M6-B", "M7", "M8-readmitted-store-kept", "M9-record-expired"]
rows = {}
for cls in CLASSES:
    for adv in TSS_BY:
        if adv == "PIN-writable" and not cls.startswith(("M2-pin", "M9")):
            continue
        try:
            rows["%s|OP-7 (a)|%s" % (cls, adv)] = row(cls, adv)
        except Exception as e:  # noqa: BLE001
            rows["%s|OP-7 (a)|%s" % (cls, adv)] = {"error": repr(e)[:200]}
summary = {
    "rows": len(rows), "errors": [k for k, v in rows.items() if "error" in v],
    "rows_saying_current": [k for k, v in rows.items() if v.get("label_says_current")],
    "rows_where_C3_is_allowed_on_the_thief_descendant": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") == "t12x"],
    "rows_where_C3_is_allowed_on_a_state_below_t9": [k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") in ("t1", "t5")],
    "rows_where_revoked_R7_is_eligible_for_use": [k for k, v in rows.items() if v.get("revoked_R7_eligible_for_use")],
    "unanchored_rows_above_C0": [k for k, v in rows.items() if k.startswith("M5|") and v.get("allowed") != ["C0"]],
    "expired_anchor_rows_above_C0": [k for k, v in rows.items() if v.get("cp1_anchor_expired_C0") and v.get("allowed") != ["C0"]],
    "pin_rows_beyond_7_days_above_C0": [k for k, v in rows.items() if k.startswith(("M2-pin20d", "M2-pin100d")) and v.get("allowed") != ["C0"]],
    "clock_below_high_water_rows_above_C0": [k for k, v in rows.items() if v.get("cp1_clock_below_high_water_C0_R") and v.get("allowed") != ["C0"]],
    "oracle_only_rows_revoked_R7_eligible (removed by R-CLK-1)": [k for k, v in rows.items() if v.get("cp1_clock_below_high_water_C0_R") and "C1" in v.get("oracle_allowed", [])],
    "oracle_only_rows_C3_on_a_state_the_sources_do_not_publish (removed by the CP-1 currency rule)": [k for k, v in rows.items() if v.get("oracle_C3_with_currency_naming_effective") and not v.get("C3_with_currency_naming_effective")],
}
verdicts = {"no_row_says_current": not summary["rows_saying_current"], "no_C3_on_thief_descendant": not summary["rows_where_C3_is_allowed_on_the_thief_descendant"],
            "unanchored_C0_only": not summary["unanchored_rows_above_C0"], "expired_anchors_C0_only": not summary["expired_anchor_rows_above_C0"],
            "pins_beyond_7_days_not_anchors": not summary["pin_rows_beyond_7_days_above_C0"], "no_errors": not summary["errors"],
            "no_C3_on_a_state_below_t9": not summary["rows_where_C3_is_allowed_on_a_state_below_t9"], "revoked_R7_never_eligible_for_use": not summary["rows_where_revoked_R7_is_eligible_for_use"],
            "clock_below_high_water_C0_only": not summary["clock_below_high_water_rows_above_C0"]}
print(json.dumps({"probe": "BA11r7 machine classes under CP-1 anchoring (AR-0019; after RV6-B-A11)", "params": {"pin_max_validity_days": 7, "c3_currency_window_hours": 24, "workstation_anchor_days": 90},
                  "summary": summary, "verdicts": verdicts, "rows": rows}, indent=1, sort_keys=True, default=str))
