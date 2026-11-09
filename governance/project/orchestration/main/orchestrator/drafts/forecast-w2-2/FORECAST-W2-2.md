# FORECAST-W2-2: the re-estimate at today's measured pace (for the owner)

Written for the CTO by a read-only agent on 2026-11-09 at 22:50 GMT, at `w2/integrate` `cf23e9f8d`. Its predecessor is
FORECAST-W2-1 (this morning, at `b7b3f4b8`). Nothing was run except git and `gov plan` (read-only). **M** means measured,
with the source named. **E** means estimated, with the basis named. Times are GMT. Today is Monday.

## 1. Headline

| date | FORECAST-W2-1 (old) | (a) today's measured pace | (b) lead-hour method, refreshed | which I trust → plan on |
|---|---|---|---|---|
| **The lift** (the re-pin) | 11-15 (11-14 to 11-18) | **11-11** (11-10 to 11-13) E | **11-13** (11-12 to 11-15) E | (a) → **11-11** E |
| **EXAMIN's copy** (W2-27 starts) | 11-21 (11-19 to 11-26) | **11-14** (11-13 to 11-17) E | **11-17** (11-16 to 11-20) E | between them → **11-15** E |
| **Wave 2's end** (W2-47) | 11-28 (11-25 to 12-05) | **11-19** (11-17 to 11-24) E | **11-24** (11-22 to 12-01) E | closer to (b) → **11-22** E |

**Which I trust, and why.** For **the lift**, I trust (a). What is left before it is the same kind of small, tests-first
round that the sample measures. The lead-hour method was too slow on exactly this work: FORECAST-W2-1 gave item 8,
W2-139/W2-140 and D-6 part 2 the whole week, and they merged within 22 hours (M, git). For **EXAMIN** and **the end**, I
would not take (a) at face value. The tickets left are 2 to 3 times larger than the sample (W2-115, W2-88, W2-121,
W2-23) (E). The milestones take calendar time and wait on your verdicts. And the weekly usage limit caps (a)'s pace: it
ran out last week, at 100 % on 11-08 08:17 (M, `log/usage.txt`; §5).

**Every date moves for the same two reasons:** your answers overnight, and the usage limit.

## 2. Share done

**(i) By tickets.** `.tickets/` holds **217 files (M)**: 160 Wave 2, 51 Wave 1 and 6 with no wbs id.
- **The total is 161, not 155: 160 Wave 2 tickets plus W1-01b, the one Wave 1 ticket carried (M).** FORECAST-W2-1
  counted 151 at `b7b3f4b8`. Nine tickets were filed since: W2-66c and W2-146 to W2-153. 155 matches no count I can find.

| state | tickets | share | which (M, `.tickets/` statuses, `report-state.json`, git merges) |
|---|---:|---:|---|
| closed | 74 | 46 % | status `closed` |
| merged, not closed (they close at the lift) | 34 | 21 % | `report-state.json`'s 27, plus W2-139, 140, 149, 150, 151, W2-56 (merged 22:48), and W2-15a (pass 1 merged 11-03, status open) |
| in flight now | 4 | 2 % | W2-128 (round 1 merged; 2a READY), W2-152 (READY), W2-153 (review READY with three preconditions), W2-130 (D-10's fix merged; batches left) |
| built or partly built, idle | 13 | 8 % | W2-11, 37, 42a, 52, 60a, 66b, 81, 90b, 104, 105, 110, 116; W1-01b (closes at D-10's green run) |
| not started | 26 | 16 % | W2-15b, 23, 27, 28, 29, 30, 33, 40, 45, 46, 47, 60b, 66c, 82, 88, 90c, 93, 94, 98, 111, 113, 115, 120, 121, 124, 146 |
| leave for Wave 3 | 9 | 6 % | W2-17, 18, 19, 34, 35, 36, 42, 100, 101 (D9-FATES) |
| W2-00, the coordination ticket | 1 | 1 % | closes with the wave |

- **Closed or merged: 108 of 161, which is 67 % (M).** Leave out the 9 leaving and W2-00, and it is **108 of 151, 72 %**.
- **EXAMIN's path:** W2-27's `depends_on` closure holds 39 tickets that are not closed. **18 of them are merged.** After
  W2-152 and W2-153 merge, **19 are left, W2-27 included (M)**: 8 built or partly built, 10 not started, and W2-27.

**(ii) By what the lift needs.** There are 14 items. **6 are done, 4 are partly done and 4 are not started (M)**. They
are listed in §3.

## 3. Before the lift: item by item, and the critical path

| # | item | state now (M) | what is left | who |
|---|---|---|---|---|
| 1 | Item 8: W2-141, 142, 145, 147, W2-20 | **DONE**, merged 11-09 | — | — |
| 2 | Q07 and Q14 re-worded | **DONE** (`55d1c029`) | — | — |
| 3 | W2-130's sitting | **DONE** (`c4420040`) | — | — |
| 4 | W2-139 and W2-140, one batch | **DONE** (`fa273777`) | — | — |
| 5 | ADR-0002 refreshed and accepted | **DONE** | re-read at the re-pin (item 14) | — |
| 6 | The operator agent: W2-148 and ACT-OPERATOR-1 | **DONE** (`511a4a17`, `2a646265`) | ACT-OPERATOR-2 follows; it is not a gate | agents |
| 7 | D-6 part 2 | 7 of 8 sub-items: A to F merged; F3 found nothing | F2 (W2-55 S9). Only its KPI line is placed (`27aaab38`); the tests, engineer and review are still to run | agents |
| 8 | D-5, the templates | round 1 merged; round 2a and W2-152 READY; W2-153's review READY | merge 2a and W2-152; ACT-CLAUDE-COPIES-1; merge W2-153; ACT-CLAUDE-COPIES-2; round 2b (F1-F4) | agents; **you**: two ACT yeses, TEMPLATES-APPROVAL-1, TPL-6's Appendix A |
| 9 | W2-56 | **merged 22:48** (`cf23e9f8d`; S8's reach and S10 to Wave 3, DEC-1114) | R3 and R5 follow-ups before its close | agents |
| 10 | ACT-SETS-GLOBS-1, then W2-141's hook rebuilt on it (row 78) | re-rehearsed, 0 failures (`328d40f5`); class (b) | **your yes**, the operator, then about 1 h for the hook | **you**, then agents |
| 11 | D-10's red-fix list (10 items) | 4 settled: W1-06 and test_fusion merged, W2-66 green, the three red-by-design cases decided (DEC-1111, DEC-1112). 1 waits on the green run (W1-01b, W2-66b) | 5 open: `core.bare`'s half; W1-19 under `-n auto`; D-6's five base reds; the validator's 5 FAILs; W2-54's `shared_gpu` case | agents |
| 12 | A fresh CTO session before D-10 (DEC-1110 (3)) | not started | about 0.5 h | agents |
| 13 | D-10: the full run, the fixes, green | not started | **your word**; then 2 rounds of about 1.8 h a run plus fixes (E, D4-LIST) | **you**, then agents |
| 14 | The lift | not started | the re-pin ACT (W2-136, 137, 138, 141 with its hook, 142 with its copies, 145, 147, 20, 56); ADR-0002 re-read; **your re-pin and push**; about 36 formal closes at 10-20 min each, so 6-13 h (M per close, PLAN-W2-DEC953 §2) | agents, **you** |

**Not gates, run beside them:** the set-up A sandbox experiment (after W2-149's install ACT, which follows item 10);
ACT-OPERATOR-2; W2-149's F11; W2-20's sample day (the first working day after the re-pin).

**The critical path (E).** D-10 waits on D-5 and D-6 (P1-PLAN), so the D-5 chain leads. Your steps are in brackets:
merge 2a and W2-152 → COPIES-1 rebuilt and reviewed (about 1 h) → [**yes**] → merge W2-153 → COPIES-2 → [**yes**,
the approval, Appendix A] → the fresh session (0.5 h) → [**D-10's word**] → run 1 (about 1.8 h) → fixes (1-3 h) →
run 2 (about 1.8 h) → the re-pin ACT (about 1 h) → [**re-pin, push**] → the closes (6-13 h).
Beside the chain: the five red fixes (1-3 h, in parallel), F2 (1-2 h) and item 10.

**In total: about 9-14 agent hours to the re-pin (E, from §5's per-round pace), with 5 of your steps in series and 2
beside them.**

## 4. What waits on you

**Your turnaround (M, git):**

| measure | n | median | range | source |
|---|---:|---:|---|---|
| package committed → its `Decided-by: owner (chat, …)` DEC committed (DEC-1083 to DEC-1114) | 21 | **0.4 h** | 0.0-3.4 h (mean 0.9 h) | the package's last commit before the DEC record's commit |
| ACT rehearsed → applied with `Role: owner`, by daytime | 7 | **0.4 h** | 0.15-1.1 h | ACT-GATE-CONFIG-1/2, D4-RESTORE-1, PATHMAP-NS-1, GUARD-CALLLOG-1, OPERATOR-1, STOP-IDLE-1 |
| the same, when it fell overnight | 3 | **10.8 h** | 9.9-10.8 h | ACT-GUARD-SETS-1 (11-08), SELECT-FIXES-1 and INDEP-WALLS-1 (rehearsed about 02:15, applied 12:16 and 13:06) |
| agents idle on you, 11-09 | 1 day | **9.0 h of 22** | — | 04:44-13:42: no merge, usage flat at 13 % (`usage.txt`), waiting on the gate-file ACT and DEC-1103 |

You answer quickly by day. What costs time is a gate that falls in your night.

**Your share of each date (E):** 0.4 h for each step of yours on the path, plus one night (about 0.4 day) for each
night the path crosses with its next step being yours.

| date | your steps on the path | your share | of the time from now (plan-on date) |
|---|---|---|---|
| the lift | 7: two COPIES yeses, the templates' approval, Appendix A, SETS-GLOBS-1, D-10's word, the re-pin and push | **0.5-0.8 day**, plus whenever you choose to give D-10's word | about 1.5 days |
| EXAMIN's copy | plus: the release cut (DEC-772), the fixed briefs for W2-88's verdict set, the re-pins after the lift, class (b) ACTs | **1-1.8 days** in total | about 5.5 days |
| Wave 2's end | plus: the W2-28 and W2-30 verdicts, W2-29 on the real repository, the W2-47 audit; the weekends of 11-14/15 and 11-21/22 | **2-3.5 days** in total | about 13 days |

**Waiting on you right now:**
1. ACT-SETS-GLOBS-1, a class (b) yes. W2-141's hook rebuild, W2-149's install ACT and the sandbox experiment wait on it.
2. TEMPLATES-APPROVAL-1 and TPL-6's Appendix A (D-5).
3. ACT-CLAUDE-COPIES-1, once rebuilt tonight; then COPIES-2.
4. **D-10's word**, after the red fixes and the fresh session.
5. The re-pin and the push (yours only).

Not waiting on you: everything else in §3 is agent work.

## 5. Method and data

**Window:** 11-06 11:12 to 11-09 22:48, the tickets built tests first by an independent designer. The 11-03 to 11-05 merges
were emergency memory rounds (W2-32 and W2-13 S-lines, labels), so they are left out.

**Per ticket:** from its "in progress: its test designer starts" (or "filed") commit to its merge into `w2/integrate`
(M, git):

| ticket | h | ticket | h | ticket | h | ticket | h |
|---|---:|---|---:|---|---:|---|---:|
| W2-131 | 0.5 | W2-138 | 2.1 | W2-147 | 3.35 | W2-149 | 2.0 |
| W2-133 | 0.75 | W2-137 | 2.25 | W2-20 | 15.9¹ | W2-150 | 2.1 |
| W2-134 | 0.6 | W2-136 | 1.3 | W2-148 | 3.0² | W2-151 | 0.15 |
| W2-129 | 1.6 | W2-145 | 4.2 | W2-139+140 | 1.4 | W2-56 | 21.8³ |
| W2-116 p1 | 1.5 | W2-141 | 4.2 | W2-142 | 4.2 | W2-135 | 1.65 |

1. W2-20: 6.9 h without the 9.0 h wait on the gate-file ACT.
2. W2-148: three review rounds; F21 and the replay round took another 1.0 h.
3. W2-56: about 3.7 h active; it waited on DEC-1112's re-plan.

**From the sample (M):**
- **Median per ticket: 2.0 h (n = 20); middle half 1.3-3.4 h; range 0.15-21.8 h.** Part-ticket rounds (D-6 items,
  D-10 fixes, W2-128 rounds): median about 0.6 h.
- **Throughput:** 21 tickets in 3.95 days, **5.3 a day**. 11-08 merged none: the limit was out until 09:00, then the
  fresh-80 GPU run (no commits during a GPU measure).
- **On 11-09:** 12 tickets and 10 part-ticket rounds in 13 active hours, with **5-6 helpers at once** (overlapping
  spans in git).

**How (a) projects (E):** agent time is about 0.4 × lead-h (n = 3, weak: W2-20 took 6.9 h for 3.5-5.3 lead-h;
W2-56 3.7 h for 17-20, with part of its scope cut; W2-128 about 5 h for two-thirds of 9.2-18.4). EXAMIN's 123-180
lead-h (b's figure) become 50-72 helper-hours. At about 3 effective helpers that is 17-24 active hours; the chain
W2-81 → W2-88 → W2-27 takes 14-19 h. With 13 active hours a day (M) and your steps, that is 2-3 days after the lift.
The milestones take about 0.5 day each, plus your verdicts.

**How (b) is refreshed (E):** W2-56 is merged; W2-82 comes after W2-27 (DEC-1099 (3)); W2-88's 2-day practice run is
now EXAMIN's copy itself (DEC-1099 (2)), about −2 days on the near-critical chain; W2-128 is about half done.
- The lift: about 1 day of capacity, plus 2 D-10 rounds, plus your steps.
- EXAMIN: the 19 tickets need 164-225 lead-h at the medians, less 20-25 %, so **123-180 lead-h**: 2.2-4.5 days at
  40-55 a day. The chain W2-81 → W2-88 → W2-27 takes about 4 days.
- The end: 7 days after the copy (WBS §4).

**The usage limit.** "week (all models)" is at **33 % at 22:41** and resets **Sunday 11-15 09:00** (M). It rose 27 pts
on 11-09, 20 of them in the 9 active hours after 13:36 (M): about 0.5 pt per helper-hour (E).
- **Projected (E):** at that pace the 67 pts left last 30-55 hours, so the limit runs out **about 11-11 to 11-12**.
- The lift needs about 10-15 pts and EXAMIN's path about 30 (E). They fit only if little else runs; the sandbox
  experiment costs tokens too.
- If it runs out, the agents stop until 11-15 09:00, and (a)'s EXAMIN date becomes about 11-16. Usage stays
  record-only (DEC-1091).

**Caveats:**
- The sample is small tickets.
- Merges went in batches (4 at 04:43, 4 at 21:38), so some wait between READY and the merge is counted in.
- The start is the record commit; a designer may begin minutes later.
- (a) assumes the helper way continues after the lift, or that the three-layer trial runs on the same tickets.
- D-10 is assumed green in 2 rounds. Each extra round adds about 0.5 day under (a) and 1 day under (b).

**Sources:** git (`w2/integrate`, ticket and tests branches); `.tickets/*.md`; `gov plan` (read-only);
`log/report-state.json`; `log/usage.txt`; `log/spend.jsonl`; P1-PLAN's D-10 row; D5-STATUS; D6-PART2; D10-REDS;
DECIDED-NOT-DONE rows 1-82; START-NEXT-SESSION; `docs/DECISION_REGISTER.md` (DEC-1083 to DEC-1114); FORECAST-W2-1.
