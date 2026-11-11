# FORECAST-W2-3: the re-estimate from the night of 11-10/11, at the measured pace (for the owner)

Written for the owner by a helper for the CTO (Sonnet, high; checked by the CTO) on 2026-11-11 at about 01:30 GMT, at
`w2/integrate` `797495bdf`. Its predecessor is FORECAST-W2-2 (11-09 22:50, at `cf23e9f8d`). Nothing was run except git, a
read of `.tickets/` and a read of `log/usage.txt`. **M** means measured, with the source named. **E** means estimated,
with the basis named. Times are GMT. Today is Wednesday. Under DEC-1125 (3) (iii) b.

## 1. Headline

Old and new side by side (the standing rule: re-estimated with old and new figures together).

| date | FORECAST-W2-2 (11-09) | now: usage rule (A) holds to the reset (11-15 09:00) | now: the owner ends (A) at the lift | plan on |
|---|---|---|---|---|
| **The re-pin** (the lift) | 11-11 (11-10 to 11-13) | **11-11** (11-11 to 11-12) E | same | **11-11** E |
| **The formal closes done** | not dated (6-13 h after the re-pin) | **11-12** (11-11 evening to 11-13) E | same | **11-12** E |
| **EXAMIN's copy** (W2-27 starts) | 11-15 (11-13 to 11-20) | **11-19** (11-17 to 11-23) E | **11-16** (11-14 to 11-19) E | **11-19** E |
| **Wave 2's end** (W2-47) | 11-22 (11-17 to 12-01) | **11-27** (11-24 to 12-04) E | **11-24** (11-21 to 12-01) E | **11-27** E |

**Confidence.** The re-pin: medium-high (about 75 %). Its ACT is built and reviewed tonight, and what is left is your
re-pin in the morning. EXAMIN's copy and the end: medium-low. They depend on one rule that is yours to settle (§4,
point 1), on the week's allowance and on your verdicts.

**Why EXAMIN's copy moved three days (the one change that matters).** FORECAST-W2-2 was written on 11-09. It did not
yet have DEC-1122 (2) (11-10): from now **only the lift's critical path runs, and everything else waits for the weekly
reset on 11-15 09:00**. After the re-pin and the closes, the lift's path ends. The tickets on EXAMIN's path are not on
it. So under the rule as written they start on 11-15 at 09:00, a Sunday, not on 11-12. If you end the rule at the
lift, they start on 11-12 but meet the allowance (§5): about 20-25 points are left for about 30 that the path needs (E).
That gives 11-16, and not FORECAST-W2-2's 11-15, because RUBRIC-2's product work is now on the path (next paragraph).

**What else changed since 11-09 (all in the records, none yet in a ticket):**
- **RUBRIC-2 (DEC-1120) is on EXAMIN's path.** W2-33, W2-60a and W2-60b must land before EXAMIN's copy (DEC-1120 (5),
  DEC-1119 (2)). None of the three tickets carries DEC-1120 yet (checked, `.tickets/`). The chain is W2-33 → W2-60a →
  W2-60b, about 2.5-3.5 days in series with your approval of W2-33's kernel hash and one class (b) yes (E).
- **D-10 is done to the owner's report.** Both runs ran (run 1 11-10 18:10-19:12, run 2 22:22-23:45). Each took about
  half the time FORECAST-W2-2 assumed (§5). One red is named for the re-pin and the lift (DEC-1125 (1)).
- **Two new tickets, both after the lift:** W2-154 (P2) and W2-155 (P4). Neither is on EXAMIN's path.

## 2. Share done

`.tickets/` holds **219 files (M)**: 163 Wave 2 (162 with a Wave 2 id, W2-01 to W2-155, plus W1-01b, the one Wave 1
ticket carried), 50 more Wave 1 and 6 with no wbs id. FORECAST-W2-2 counted 161; the two new ones are W2-154 and W2-155.

| state | tickets | share | which (M for `closed` and the total; E for the rest, from FORECAST-W2-2's list and the merges in git) |
|---|---:|---:|---|
| closed | 74 | 45 % | status `closed`; none closed since 11-09 (no `gov close` in the emergency) |
| merged, not closed (they close at the lift) | 37 | 23 % | FORECAST-W2-2's 34, plus W2-128 (rounds 1-2b and 1.0.1), W2-152 and W2-153 |
| built or partly built, idle | 14 | 9 % | W2-11, 37, 42a, 52, 60a, 66b, 81, 90b, 104, 105, 110, 116, W2-130 (D-10's fix merged; batches left) and W1-01b |
| not started | 28 | 17 % | FORECAST-W2-2's 26, plus W2-154 and W2-155 |
| leave for Wave 3 | 9 | 6 % | unchanged (D9-FATES) |
| W2-00, the coordination ticket | 1 | 1 % | closes with the wave |

- **Closed or merged: 111 of 163, which is 68 %.** Leave out the 9 leaving and W2-00, and it is **111 of 153, 73 %**.
  FORECAST-W2-2 gave 67 % and 72 %. Three tickets moved in 26 hours, and the rest of the time went to D-10.
- **EXAMIN's path.** W2-27's `depends_on` closure holds **40 tickets that are not closed (M, read from `.tickets/`
  today)**. Of them 22 are merged (they close at the lift, W2-15a with W2-32, DEC-1099 (3)) and **18 are left, W2-27
  included**: 7 built or partly built (W2-11, 52, 60a, 81, 90b, 105, 110), 10 not started (W2-33, 60b, 88, 93, 94, 98,
  115, 121, 23, 124) and W2-27. FORECAST-W2-2 said 19. I cannot name the difference: its list gave no ids. W2-82 is not
  in the closure (after W2-27, DEC-1099 (3)).
- **By what the lift needs.** FORECAST-W2-2 had 14 items: 6 done, 4 partly, 4 not started. Now **13 of 14 are done or in
  hand (M, DECIDED-NOT-DONE rows 64-69, 78, 94, 110)**. The one left is the lift itself (§3).

## 3. Before and after the lift, step by step

| # | step | state now | what is left | who |
|---|---|---|---|---|
| 1 | D-10, the full runs | **DONE 11-10** (run 1 and run 2; `622e9b741`, row 110) | the named red (W1-19 and W2-13 warm p95 0.54-0.59 s against 0.5 s) goes to W2-155 after the lift (DEC-1125 (1)) | — |
| 2 | The re-pin ACT (ACT-REPIN-W5, row 88) | being built and rehearsed in a clone tonight, then an Opus review (DEC-1125 (3) (i)) | review; the owner's exact commands in the 09:30 digest | agents |
| 3 | The closes prepared (LIFT-CLOSES-1, row 97) | being prepared tonight: each lift ticket's acceptance check on integrate (DEC-1125 (3) (ii)) | the closes themselves, after the re-pin | agents |
| 4 | The anti-drift audit (a-f) | running tonight (DEC-1125 (3) (iii)) | fixes by role; items for an engineer or an ACT listed | agents |
| 5 | The first ready lists after the lift | not started (`gov plan`, several batches deep, DEC-1110 (3)) | after the audit | agents |
| 6 | **The re-pin and the push** | not started | your morning (08:00-09:30, E) | **you** |
| 7 | The formal closes | not started | about 37, at 10-20 min each: 6-12 h (M per close, PLAN-W2-DEC953 §2); less where tonight's checks already ran | agents |
| 8 | After the closes: the three-layer package, W2-154, the performance ticket W2-155, the weekly memory audit's first run, set-up A's run, the E and F trials, W2-66c, W2-20's sample day | not started | **each waits for the reset under (A)**, except what you release | agents, **you** |
| 9 | The RUBRIC-2 chain: W2-33 → W2-60a → W2-60b | not started | KPI edits (RUBRIC-2-APPLY §3), tests revised by a designer, build, C3 reviews; your hash approval and one class (b) yes for the agents' copies | agents, **you** |
| 10 | The other nine tickets of EXAMIN's path | W2-81 built in part; W2-88's six answers decided (DEC-1098 (1)) | W2-81 → W2-88 (the fresh 80's standard is pinned in it); W2-115 (26-34 lead-h; now also the trailers switch, DEC-1123 (3)); W2-121, 23, 93, 94, 98, 124 | agents |
| 11 | W2-27, EXAMIN's copy; then W2-28, 29, 30, 46, 47 | not started | the release cut (DEC-772), your verdicts | agents, **you** |

**The critical path (E).** Re-pin (11-11) → closes (11-11 evening to 11-12) → **the reset (11-15 09:00), if (A) holds**
→ W2-33 (about 1 day with your approval and the yes) → W2-60a (about 0.5-1 day) → W2-60b (about 0.5 day) → W2-27.
Beside it, not longer: W2-81 → W2-88 (14-19 h under (a), about 4 days under (b)) and W2-115 (10-14 h).

**Agent time to the re-pin: the night's work only, about 8-12 helper-hours across eight helpers in parallel (E, from
their briefs' estimates), done by the morning. Your steps before the re-pin: one.**

## 4. What waits on you

**Your turnaround (M, FORECAST-W2-2 §4; no new data since):** 0.4 h median for a package by day; 0.4 h for an ACT by
day; about 10.8 h when the gate falls in your night.

**Waiting on you now, in the order of the dates they move:**
1. **Does usage rule (A) end at the lift?** (DEC-1122 (2) says: until the reset, 11-15 09:00.) This moves EXAMIN's
   copy by three days (§1) and the end by three days. If it ends, the allowance may run out near 11-15 (§5).
2. **The re-pin and the push** (yours only), 11-11 morning.
3. **W2-33's kernel hash and one class (b) yes** for the agents' copies, after the reset (or at the lift, with 1).
4. **The release cut** (DEC-772), after the lift and before W2-81's run.
5. **The memory audit's three fixed briefs** (writer, checker, auditor; DEC-1101 (2), DEC-1125 (2)), once, from the
   audit package that another helper prepares tonight.

| date | your steps on the path | your share |
|---|---|---|
| the re-pin | the re-pin and the push | 0.1 day |
| EXAMIN's copy | plus W2-33's hash, one yes, the release cut, (A)'s answer | about 0.5-1 day in all |
| Wave 2's end | plus the W2-28 and W2-30 verdicts, W2-29 on the real repository, the W2-47 audit; the weekend 11-21/22 | **2-3.5 days in all** (as FORECAST-W2-2) |

## 5. Method and data

**The pace, and where it comes from (M unless marked).**
- **FORECAST-W2-2's sample** (11-06 to 11-09, whole tickets, tests first): median 2.0 h a ticket (n = 20), 5.3 tickets a
  day. That figure is **not used** for the dates after the lift, for the reason below.
- **The window since then** (11-09 22:48 to 11-11 01:20, 26.5 h): **47 merges into `w2/integrate`** (git, first-parent
  merges). Three tickets were finished (W2-152, W2-153, W2-128), which is 2.7 tickets a day. About 40 of the 47 merges
  are D-10's fix rounds, records and follow-ups. So tickets a day fell by half because the work was D-10, not new
  tickets, and because rule (A) started no new ticket.
- **D-10 took less than planned.** Run 1: nightly 3,749 s (1.04 h); run 2: nightly 3,038 s (0.84 h) (row 110, M).
  FORECAST-W2-2 assumed two runs of about 1.8 h (E). From the owner's word to the owner's report: 18:10 to 23:45, 5.6 h,
  with a 0.4 h machine restart (21:29-21:52) in it.
- **The pace I use for what comes after (E):** FORECAST-W2-2's method (a), unchanged: agent time is about 0.4 of the
  lead-hours (n = 3, weak), 13 active hours a day, about 3 helpers at once. It is the only pace measured on tickets of
  this size. The RUBRIC-2 chain and W2-115 add about 7-10 lead-h to EXAMIN's path (E: W2-60a's revised tests and two
  reviews, 5-8; W2-115's trailers line, 2), so **the path is 130-190 lead-h, or 52-76 helper-hours (E)**.
- **Method (b), refreshed:** at 40-55 lead-h a day, 130-190 lead-h is 2.4-4.8 days. The chain W2-81 → W2-88 → W2-27
  stays at about 4 days.
- **From a start day S:** EXAMIN's copy is about S + 3 days under (a) and S + 4.5 days under (b). Plan on the middle.
  With S = 11-15 (rule (A)): (a) 11-18, (b) 11-19 to 11-20, plan 11-19. With S = 11-12 (rule ended), the allowance caps
  the work near 11-15, so 11-16. Wave 2's end is the copy + 5 days under (a) and + 7 under (b) (WBS §4), with the
  weekend 11-21/22 in it.

**The weekly allowance (M, `log/usage.txt`).** "week (all models)" was 33 % at 11-09 22:41, 60 % at 11-10 16:00, **63 %
at 11-11 01:19**; it resets 11-15 09:00. It has been flat at 62-63 % since 11-10 22:52, because D-10's runs used almost
none (M). FORECAST-W2-2 projected the allowance running out on 11-11 to 11-12; that did not happen (E: rule (A) and
D-10's machine time).
- **What is left:** 37 points. Tonight's eight Sonnet helpers and one Opus review: about 2-4 points (E: USAGE-RUBRIC-2
  §2 puts the whole week's ACT-preparation helpers at 3.9 points). The lift and the closes: 10-15 points (E,
  FORECAST-W2-2 §5). That leaves **about 20-25 points at the end of the closes (E)**.
- **EXAMIN's path needs about 30 (E, FORECAST-W2-2 §5), plus set-up A's run, about 4 (E, USAGE-RUBRIC-2 §4).** So the
  path fits only after the reset, or if you add usage (B). That is why ending (A) at the lift buys at most 11-15 to
  11-16, not 11-12.
- RUBRIC-2 buys hours, not days (USAGE-RUBRIC-2 §1): 4.8-6.9 points a week.

**Caveats.**
- The sample is small tickets and one window of D-10 fixes.
- W2-33 is C3 (the kernel): its CIT-P needs your approval of a hash and a class (b) yes. A night in between costs
  10.8 h (M).
- The closes: 37 is from FORECAST-W2-2's 34 plus three; LIFT-CLOSES-1 (prepared tonight) has the count that counts.
- D-10 is treated as done, with the named red. A third D-10 run is not planned.
- The first memory audit may confirm the re-pin's retrieval change. If W2-155 lands before it, the two changes are
  measured together: say so when the audit is dated.

**What would move the dates.**
| what | effect |
|---|---|
| (A) ends at the lift | EXAMIN's copy 3 days earlier (11-16); the end 3 days earlier (11-24) |
| the owner adds usage (B) | the same as (A) ending, and removes the cap near 11-15 |
| the re-pin slips a day (a review finding, a rollback) | every date plus 1 day |
| the closes need 13 h and not 6 (a red at a close) | the closes 11-13; EXAMIN under (A) is not affected |
| W2-33's approval or the class (b) yes falls in a night | plus 0.4 day |
| W2-115 or W2-88 takes the high end | EXAMIN plus 1-2 days (the chain is 4 days under (b)) |
| the memory audit or set-up A's run takes helper hours from the path | plus 0.5 day if run on the same days |
| the three layers' trial (DEC-1087 (13)) runs on the path's tickets | plus 0.5-1 day (FORECAST-W2-1 §5: about 25 % less throughput over 3 days). **Not in the dates above:** no three-layer package exists yet; it comes to you after the lift |
| a failed W2-27 milestone verdict | each milestone plus its verdict wait: 1 day each |

**Sources:** git (`w2/integrate`, merges since 11-09 22:48); `.tickets/` read today (status counts; W2-27's closure);
`log/usage.txt`; DECIDED-NOT-DONE rows 64-69, 85-118; `packages/FORECAST-W2-2.md` and `FORECAST-W2-1.md` (§4's chain);
`packages/RUBRIC-2-APPLY.md` §3; `packages/USAGE-RUBRIC-2.md` §1, §2, §4; `docs/DECISION_REGISTER.md` (DEC-1087 (13),
DEC-1099 (3), DEC-1119 to DEC-1125); START-NEXT-SESSION §00.
