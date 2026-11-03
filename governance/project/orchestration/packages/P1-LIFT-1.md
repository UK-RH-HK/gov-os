# P1-LIFT-1 — What to lift: the investigation's one list (DEC-1047), for the owner first

Written 2026-11-02 22:09 by the CTO (session debdb3f7). The list: `INVESTIGATION-1-COMBINED.md` beside this file
(75 distinct rows in 8 themes, every row citing its sources); the seven part reports in `INVESTIGATION-1-parts/`.
Nothing is lifted before the owner decides (DEC-1047). DEC-1010 stays, whatever is decided.

1. **Context.** DEC-1047 raised the emergency one level and ordered a harsh, read-only investigation of what to lift,
   judged by DEC-1010's test against the Gov OS's aim (memory that extends the agents; spec and KPIs developed by
   research and discovery agents and executed by others; roles that keep conflicting work apart; the WBS and tickets'
   launching and closing governed: the traffic, not a city). Seven parts ran in parallel (A1, A2: the owner's ten named
   practices and their kind; B1: the product's gates, checks, close and records; B2: the guard, the kernel, the
   Contract; C: the CTO's tools and practices; D: the WBS and tickets; E: a fresh repository or not), one combiner.
2. **What was found** (the list's §1). The protection the aim needs is small and mostly built (the five guard rules'
   core, independent test design and review, the dispatcher and Load Balancer, the memory tools, the checkpoints). The
   cost is in habits around it: the same full checks run again and again (`gov check` up to three times per lead
   verification plus a hidden one inside every scoped run; leads run the nightly-routed cases; each red re-run 3+3
   times against a clone built from the nightly); gates for mistakes an honest agent does not make (79 of 86 guard
   refusals false; the strict close passed 0 of 30 direct runs; a context ceiling refusing packets that carry no text,
   its 1.6 M tokens a counting bug); paperwork that grows by itself (the lead brief 22k to 54k characters in 14 days, the
   CTO prompt 115 KB, the register 1.66 MB growing about 55 KB a day; each CTO practice a product KPI the same day); the
   owner interrupted (131 permission prompts on 1-2 Nov, 122 of them `rm`; 21 to 28 pings and 21 to 25 packages a day);
   the CTO watching from inside a $100-150 a day session (est.).
3. **Why it matters.** Two weeks went into fighting the machine instead of building the product the aim names. Each
   lift returns machine time, tokens and the owner's attention to tests and code that match the KPIs and pass green.
4. **Options.** Per row: lift / scope to the change / move to the nightly / keep (the list's §3), with the floor that
   stays (§4), the ticket fates (§5: keep 21, re-scope 23, merge 11, close formally 6, retire 22, Wave 3 9; about 146
   KPI lines lifted) and the order of lifting (§6: configuration and text first, then code with tests, then the owner's
   ACTs, then one Contract re-baseline, DEC-105). What lifting saves, in orders of size (the items overlap): about 12
   machine-hours a day (up to about 16 with incremental rebuilds, est.); about $55-110 a day of tokens (est.) plus about
   165 lead-hours and $300 from the ticket fates; the owner's interruptions from several hundred a week to a few dozen
   (est.). **The fresh-repository question: keep this repository and lift here** (part E, confidence about 80 %): the
   bureaucracy is configuration and practice, not the repository's shape; memory imports 18,063 of the product's ~26,000
   lines, gates included; a copy loses 18,360 decision citations, W2-61's measure and the evidence; fresh costs about
   8-14 working days and delays EXAMIN by 7-12, keeping costs about 2-4 (est.).
5. **Recommendation** (the CTO's, confidence high for the first set): approve the twelve "decide first" rows (§2) now:
   (1) T-5 leads' serial phase only what the product selects; (2) T-4 the hidden `gov check` and the always-added lists
   to the nightly; (3) T-1 leads stop the full `gov check`; (4) Q-1 attribution once each way against the head without
   the batch; (5) T-12/O-10 the nightly's needless preconditions and the load-average gate (when the nightly returns,
   DEC-1049); (6) G-10/G-11 the guard harvest nightly or on demand; (7) R-1 to R-5 the lead brief to 15k characters or
   less; (8) O-7 `rm` in throw-away paths without asking (an owner ACT); (9) R-8/R-11 pings only for what gates work,
   two digests, delegated decisions out of the register; (10) O-1/O-2/O-4 the CTO prompt to 10 KB or less, waking only
   for decisions; (11) G-12 review effort by risk; (12) G-1/G-2 rules 1 and 5 stop reading Bash heuristically, with a
   landing check on `Role:` trailers for `tests/acceptance/` first. Then the rest of §3 row by row, the ticket fates and
   the K9 amendment, and keep this repository. Already done under DEC-1045, so not to decide: T-13 (the nightly's full
   scan, fixed `22fdf687`). Questions for the owner from the list: the measured tickets for G-3 (rule 2's hidden half);
   W2-04 once under DEC-1010's two-round cap; whether the aim's "the builder never reads its own tests" is met by
   procedure (`gov accept` and the two worktrees, G-14).
6. **What it blocks, and what waiting costs.** It blocks DEC-1039's steps 2 (the refactor), 3b (the WBS refactor and the
   new estimate for EXAMIN's copy) and the restart of ticket work; waiting keeps every cost above while the freeze holds.

## Addendum (2026-11-02 22:18, the CTO)
- **O-A1, the dispatcher's older memory admission double-counts** (found by the Load Balancer's first T1 incident, `log/incidents/2026-11-02-2217-T1.md`): the "slots rule" reserves each heavy slot's peak on top of the memory the running slot jobs already hold, so at 22:17 it refused W2-112's lead with "-2580 MB of room" while 15.9 GB was free and the forecast admitted it. Recommendation: lift the slots rule; the Load Balancer's forecast (memory above the floor, per-phase peaks) is the admission. Cost to lift: a few lines and their tests in the dispatcher. W2-112 was started past it on the owner's DEC-1048 order (`tools/start_owner_order.sh`, 22:17:55).
