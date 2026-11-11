# Anti-drift audit (b): P1-PLAN and the forecast (DEC-1125 (3) (iii) b)

By a helper for the CTO (Sonnet, high, class C2), 2026-11-11 about 01:40 GMT, at `w2/integrate` `797495bdf`. Read only
except the three paths below. Nothing was run but git, reads of `.tickets/` and of `log/usage.txt`.

## What changed
- `LIFT-1/P1-PLAN.md`: a new state section at the top (the D-steps as they stand, and the true state of §A's P1-0 to
  P1-14, each with its evidence); the old status table's rows for D-4b, D-5, D-6, D-9 and D-10 marked superseded; §A rows
  **P1-15 to P1-25 added** in §A's form; an order line from 11-11; §F, §G and the headline point to FORECAST-W2-3.
- `packages/FORECAST-W2-3.md`: new, in FORECAST-W2-2's form.

## The new rows
P1-15 the re-pin (ACT-REPIN-W5) · P1-16 the formal closes · P1-17 "the three layers" · P1-18 RUBRIC-2 through W2-33 and
W2-60a (and W2-60b) · P1-19 set-up A and its run · P1-20 the E and F trials · P1-21 W2-115's trailers switch · P1-22 the
weekly memory audit · P1-23 W2-155 · P1-24 the emergency's tools · P1-25 the small rows after the lift.
"The three layers" is the CTO as master, a Senior Engineer per stream, with leads and agents (DEC-953 item 8, DEC-954
Q6, Q8 (b), Q13; `SEVEN-ANSWERS.md` §5; brought back to Wave 2 by DEC-1087 (13)).

## Drift found (each is in the plan with its source)
1. **Usage rule (A) (DEC-1122 (2)) moves EXAMIN's copy about three days.** FORECAST-W2-2 predates it. Under (A) the
   tickets on EXAMIN's path start at the reset (11-15 09:00), not at the lift. The owner should say whether (A) ends at
   the lift (FORECAST-W2-3 §1, §4).
2. **W2-115 has no line for the trailers switch** (DEC-1123 (3); row 114 says "W2-115 lands it") and no DEC-1123 in its
   sources. Its paths hold neither the check's declaration (a kernel file) nor `traceability.py`. P1-21.
3. **None of W2-33, W2-60a or W2-60b carries DEC-1120.** W2-60a's ticket names W2-11 as the home of the role files'
   default lines; RUBRIC-2-APPLY §3 names W2-33. P1-18.
4. **W2-33's three lines (CTO and Senior Engineer role files, the typed handoff, undefined roles) are still "moved to
   Wave 3"**, though DEC-1087 (13) reversed that move. P1-17.
5. **The E and F trials (row 102) are overtaken in part by DEC-1120 (2)-(3)**: Sonnet high is already the rule for C2
   and C1 designers and non-FULL reviewers. P1-20.
6. **DEC-1083 (7): W1-01b, W2-66b and W2-90c close "at D-10's green run".** D-10 ended with a named red, so "green" is
   not met as written. P1-16.
7. **GLOSSARY-1's redesign and retest (DEC-1097 (6) (b)) is due and not run** (row 17); `W2-143`/`W2-144` are not filed.
8. **P1-4's tools rows Q-13, O-9, T-12/O-10, R-10, R-13, G-9, O-8 have no evidence in any record I read**; audit (d)
   (EMERGENCY-TOOLS-1) should settle them. R-7's Stop-hook row has none either.
9. **W2-60a's branch is unreviewed against RUBRIC-2** (RUBRIC-2-APPLY residuals); W2-149's A6 amendment and F40's search
   are still to do before set-up A's run.
10. **The weekly audit and W2-155 touch the same measure**: if W2-155 changes retrieval before the first audit, the
    re-pin's change and W2-155's are measured together. P1-22, P1-23.

## Not settled (for the CTO)
- §B's status cells (89 rows) still read PENDING. DEC-1052's block says "§B is to be updated to this". I did not edit
  89 rows; a script from DEC-1052's list could do it.
- The count of closes (about 37, E) stands until LIFT-CLOSES-1 is written. The 40-ticket closure splits into 22 merged
  and 18 left; FORECAST-W2-2 said 19, and its list gave no ids, so I cannot name the difference.
- New ids W2-170..179 and W2-156..169 are named in P1-22 and P1-24 as held (CHECKPOINT); they do not exist yet. If
  `gov links` flags them, reword.
- Four times were written without a record: the re-pin's hour (08:00-09:30 is from the common brief), the closes' hour,
  the helper-hours of the night, and the usage cost of the closes (FORECAST-W2-2's 10-15 points). All are marked E.

## Dates (FORECAST-W2-3 §1; E)
| | FORECAST-W2-2 | now, (A) holds | now, (A) ends at the lift |
|---|---|---|---|
| the re-pin | 11-11 | 11-11 (11-11 to 11-12), about 75 % | same |
| EXAMIN's copy | 11-15 | 11-19 (11-17 to 11-23), medium-low | 11-16 (11-14 to 11-19) |
| Wave 2's end | 11-22 | 11-27 (11-24 to 12-04), medium-low | 11-24 (11-21 to 12-01) |
