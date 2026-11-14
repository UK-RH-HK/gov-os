# Set-up B sweep (DEC-1128 (4)): draft apply script

Source: `governance/project/orchestration/packages/SWITCHED-OFF-1.md` section 5. Lines re-found at HEAD d79c8c939.
Run from the repo root, after the land: `python3 .gov-runtime/scratch/orchestrator/drafts/setup-b-sweep/apply.py [--check]`.
`--check` counts only. Every edit asserts its old string occurs exactly once; no file is written unless all pass. 21 edits in 12 files.
Nothing here is applied or committed. Closing re-grep for "set-up B" / "Wave 3 row" is row 137's last step (not in the script).

## Edits
| Id | File:line (HEAD) | Old -> new |
|---|---|---|
| S1 | docs/plan/WAVE_3_PARKING.md:36 | "W3-P30 \| Set-up B (the sandbox..." -> prefixed "RETIRED 2026-11-14 (DEC-1128 (4): set-up B dropped; the S2 gap stays a named, accepted gap, W2-56 S2/F1): " |
| S5a | docs/DECISION_REGISTER.md:13906 (DEC-1098 Status) | "Changed by: DEC-1179 (7); DEC-1164 (7) (...)" -> appended "; DEC-1128 (4): item (4)'s sandbox experiment loses set-up B ...; set-up A stays" |
| S5b | docs/DECISION_REGISTER.md:13935 (DEC-1099 Status) | "Changed by: DEC-1176" -> appended "; DEC-1128 (4): the experiment as designed loses set-up B ...; set-up A stays" |
| S11b | docs/DECISION_REGISTER.md:14004 (DEC-1103 Status, no existing mark) | adds " · **Changed by:** DEC-1128 (4): item (3)'s "the sandbox added once proven" is withdrawn ..." |
| S15b | docs/DECISION_REGISTER.md:8426 (DEC-769 Status) | "Changed by: DEC-953 (item 2)" -> appended "; DEC-1128 (4): leads are not sandboxed ...; the workers' launcher sandbox stays" |
| S6 | DECISIONS-IN-FORCE.md:456 | "(set-up B a Wave 3 row)" -> "(set-up B dropped, DEC-1128 (4))" |
| S7-25 | packages/DECIDED-NOT-DONE.md:43 | adds " [Re-worded 2026-11-14 by DEC-1128 (4), set-up B dropped: "both results" is set-up A's result only; W2-56 builds on it]" to the What cell |
| S7-29 | DECIDED-NOT-DONE.md:52 | same form, "both results" is set-up A's result only |
| S7-66 | DECIDED-NOT-DONE.md:107 | adds a re-word beside "set-up B a Wave 3 row": dropped entirely, not a Wave 3 row |
| S7-137 | DECIDED-NOT-DONE.md:201 | state "NOT STARTED, trigger met ..." -> "DONE 2026-11-14 except the owner's S2, S14, S18 (asked 11-14) · was: NOT STARTED, trigger met ..." |
| S8 | packages/LIFT-1/P1-PLAN.md:191 (P1-19) | "set-up B a Wave 3 row" -> "set-up B dropped (DEC-1128 (4))" |
| S9-header | packages/SANDBOX-GUARD-EXP-DECLARATION.md:3 | new header bullet "Set-up B: not run, dropped (DEC-1128 (4), note of 2026-11-14)" |
| S9-A1 | SANDBOX-GUARD-EXP-DECLARATION.md:9 | "Set-up B is a Wave 3 row, built by a different route." -> "Set-up B is dropped entirely, not a Wave 3 row [Re-worded 2026-11-14 ...; the amendment first read: ...]" |
| S10 | packages/SANDBOX-GUARD-EXP-1.md:1 | one-line "Note 2026-11-14" under the title: set-up B dropped, never run, text kept as record |
| S11-103 | packages/ACT-INDEP-WALLS-1.md:103 | "Its wall is set-up B's sandbox, once proven" -> "was to be ...; no sandbox will come ...; the wall is the seal and this settings layer, and the residual stays named" |
| S11-204 | ACT-INDEP-WALLS-1.md:204 | "and set-up B's sandbox closes them;" -> "no sandbox will close them (...), so they stay named residuals of 2b and 2c;" |
| S13 | docs/changes/W2-56-CIT-E.md:6 | dated note inserted after the header block (not a rewrite); lines 29 and 214 untouched |
| S15a | docs/plan/WAVE_2_WBS.md:624 | prefix "[RETIRED 2026-11-14, DEC-1128 (4): leads are not sandboxed; W2-21 closed ... no sandbox ...]" before the DEC-769 clause |
| S15c | docs/plan/WAVE_2_REVISED_PLAN.md:294 | RETIRED note under the 4.6 heading; covers the table row at :153 and :353 |
| S15d | WAVE_2_REVISED_PLAN.md:301 | "leads sandboxed under their own role" + "[retired 2026-11-14, DEC-1128 (4): leads are not sandboxed]" |
| S16 | governance/project/prompts/w2-orchestrator.md:143 | "After W2-21 closes: ... sandboxed" -> "Leads and workers (W2-21 is closed; DEC-1128 (4)): ... leads no sandbox; workers sandboxed". The "Your session is not sandboxed" line is at :69 at HEAD (not 68) and is kept |

## Skipped
- **S12 (.tickets/DAEO-wnnz.md): skipped.** Its status is `closed` (closed 2026-11-13, commit 1c02c490f), not open. DEC-1088 (6): "a closed ticket is never edited". Marked KPI-line edits would break that rule; the S13 note in W2-56-CIT-E.md carries the fact. Needs the CTO's call (a reopen under DEC-1164 (18) is for defects in scope, not this).
- S2, S14, S18: the owner's. S3, S4, S17, S19, S20: keep. No listed file was absent at HEAD.

## Doubts
- S7-137 says DONE although S12 is not edited and the closing re-grep is yet to run; the script applies the CTO's wording as given.
- S15 as briefed covers WBS:624 and REVISED_PLAN only; not edited: WAVE_2_WBS.md:612 (DEC-779), REVISED_PLAN.md:153, 353 (covered by the 4.6 note), 495, REPLAN-W2.md:32, WAVE_2_TRIAGE.md and WAVE_2_LIST.md.
- Noticed, not edited: ACT-INDEP-WALLS-1.md:201 ("the sandbox added when proven", answer 1) is the same promise as S11's two lines.
- The register marks use the DEC-1112 form (" · **Changed by:** A; B", appended at the line end).
