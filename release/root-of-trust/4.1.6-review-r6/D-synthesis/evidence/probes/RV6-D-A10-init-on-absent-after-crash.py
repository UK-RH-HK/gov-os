#!/usr/bin/env python3
"""RV6-D-A10 — class interaction R2-H4 (legacy containment and transactions) x R2-H1 (floors): after reviewer C's executed
crash prefix that recovers to `ABSENT` with the project's classified overlay still present (RV6-C-A15, order A), does the pack
state what RoT-1 `init` does with an existing `governance/overlay`? (review r6 synthesis D, AR-0018). Design (pack text), with
reviewer C's reproduced executed row cited by the synthesis report.

Questions: (i) does the `ABSENT` condition exclude a present overlay or views directory; (ii) is `init` inside the coverage of
the `19` §9 computed-weakening evaluation and of item 5 (no record); (iii) does any R-INIT rule preserve, refuse over or
re-classify an existing overlay; (iv) does any RT exercise `init` on a tree that holds an overlay; (v) does the recovery text
return a half-migrated tree to the pre-transaction legacy layout.
Environment: REVIEW_REPO. Output: JSON on stdout.
"""
import json, os, re, sys

sys.dont_write_bytecode = True
PK = os.path.join(os.environ["REVIEW_REPO"], "release", "root-of-trust", "4.1.6")
rd = lambda n: open(os.path.join(PK, n)).read()
t18, t19, t09, t26, t20, t12 = rd("18-VERIFY-AND-USE-TRANSACTION.md"), rd("19-ELIGIBILITY-AND-SECURITY-FLOOR.md"), rd("09-INTEGRATION-REQUIREMENTS.md"), rd("26-LEGACY-BINARY-CONTAINMENT.md"), rd("20-ROLLBACK-AND-RECOVERY.md"), rd("12-ACCEPTANCE-TEST-PLAN.md")
absent = [l for l in t18.splitlines() if l.startswith("| `ABSENT`")]
cover = [l.strip() for l in t19.splitlines() if l.strip().startswith("This covers")]
item5 = [l for l in t19.splitlines() if l.startswith("5. **No record")]
rinit = [l for l in t09.splitlines() if l.startswith("| R-INIT-")]
out = {"probe": "RV6-D-A10 init on ABSENT with an existing overlay (AR-0018)", "18_ABSENT_row": absent, "19_s9_coverage_sentence": cover, "19_s9_item5": item5, "09_R_INIT_rows": rinit,
       "20_recovery_phase_rows": [l for l in t20.splitlines() if re.search(r"prepared|verified-staged|abandon", l)][:6],
       "12_rows_init_over_existing_overlay": [m.group(1) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", t12, re.M) if re.search(r"\binit\b", m.group(0)) and re.search(r"existing (?:governance/)?overlay|overlay (?:present|already)|classified overlay", m.group(0), re.I)]}
out["verdicts"] = {
    "ABSENT_condition_ignores_overlay_and_views": bool(absent) and "overlay" not in absent[0] and "views" not in absent[0],
    "init_not_in_19_s9_coverage_list": bool(cover) and "init" not in cover[0],
    "no_R_INIT_rule_on_existing_overlay": not any(re.search(r"overlay", l, re.I) for l in rinit),
    "no_RT_for_init_over_existing_overlay": not out["12_rows_init_over_existing_overlay"],
}
print(json.dumps(out, indent=1, ensure_ascii=False))
