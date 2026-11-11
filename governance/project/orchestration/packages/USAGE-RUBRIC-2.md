---
decisions: [DEC-1120]
sources: [DEC-1120, DEC-1118, DEC-1115, DEC-1073]
---
# USAGE-RUBRIC-2: this week's work re-priced under RUBRIC-2 (for the owner's next report)

Written by a read-only research helper (Sonnet, high) for the CTO, 2026-11-10 ~16:30 UTC. Question: how does usage change for
work like this week's under DEC-1120? Stop rule: the measured logs and USAGE-1's method, one pass. Scripts and data (not
committed): `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/412a4e37-2f72-42fc-8da2-6310c385f8f1/scratchpad/u2/`.
M = measured, E = estimated. $ = list price; pt = a meter point = $27.5 (USAGE-1; refit to 16:00 today: $27.3, miss 0.56 pt).

## 1 Headline
- **Saving this week re-priced (11-08 09:00 to 11-10 16:00; $1,606 = 58.4 pt modelled, meter 60 %): with DEC-1120 (4) (engineers
  on C2/C1 stay Opus) $133-191 = 4.8-6.9 pt (8-12 %); without (4), after the lift, $161-231 = 5.9-8.4 pt (10-14 %).**
  Low end = Sonnet sessions need 30 % more tokens and reviewers stay at max on FULL tickets; high end = same tokens.
  Of it $37-53 (1.3-1.9 pt) is DEC-1118 C (ACT-preparation helpers), already decided.
- **Projected end** (pace of the last 24 h, 1.78 pt/h; the week resets 11-15 09:00): without RUBRIC-2 the meter passes 80 % at
  11-11 03:14 and 100 % at 11-11 14:29; with it 80 % at 04:20-05:18 and 100 % at 16:41-18:36, so 1-2 h and 2-4 h later. No
  scenario reaches the reset: it needs an average of 0.35 pt/h, a fifth of today's pace, and RUBRIC-2 cuts 9-15 %.
- **Confidence: medium on the size, high on the direction.** Spend and prices are measured; the Sonnet token ratio, the
  meter's weight for Sonnet and my class tags are not (§6). The CTO and the leads (31 % of spend) are not touched.

## 2 By role (spend M from 17,615 calls in 485 transcripts, plus the fresh 80's $109 M; band as in §1)
| role (tag E) | spend $ (pt) | RUBRIC-2 model | re-priced saving $ (pt), with (4) | without (4) |
|---|---|---|---|---|
| CTO session (ad44f5fe and the new one) | 126 (4.6) | Opus high | 0 | 0 |
| Leads: sub-orchestrator helpers (19: 8 orchestrator-type, 11 general-purpose lead tasks) | 375 (13.6) | Opus high | 0 | 0 |
| Auditor helpers (8) | 25 (0.9) | Opus high | 0 | 0 |
| Fresh 80 (reader, graders; a one-off) | 109 (4.0) | Opus (C3 verdict) | 0 | 0 |
| Other interactive sessions (3 Opus top-level, 1 operator folder) | 25 (0.9) | not classified | 0 | 0 |
| Test designers (83 sessions; C3 $161 Opus, C2/C1 $107 Sonnet) | 268 (9.7) | C3 Opus, else Sonnet | 37-53 (1.4-1.9) | same |
| Reviewers (79; C3 $188 and C2-FULL $36 Opus, C2-STANDARD/C1 $63 Sonnet) | 287 (10.4) | see class | model 22-32 (0.8-1.2) | same |
| Reviewers, effort max to high (2,035 calls at max; E: output halves) | in the row above | high | 22-32 (0.8-1.2) | same |
| Engineers and product-spec (59; C3 $158 Opus, C2 $81) | 239 (8.7) | C3 Opus; C2/C1 Opus under (4), else Sonnet | 0 | 28-41 (1.0-1.5) |
| ACT-preparation helpers (DEC-1118 C) | 107 (3.9) | Sonnet high | 37-53 (1.3-1.9) | same |
| Research, product-spec, other helpers; worker helpers; the writer | 42 (1.5) | Sonnet high | 15-21 (0.5-0.8) | same |
| Haiku/Sonnet small jobs (sentinel, tests, dead-man, 2 Sonnet preparers) | 4 (0.1) | already Haiku/Sonnet | 0 | 0 |
| **Total** | **1,606 (58.4)** | | **133-191 (4.8-6.9)** | **161-231 (5.9-8.4)** |
Re-price (M arithmetic): the same tokens at Sonnet 5.5 list prices (half of Opus on every kind, USAGE-1 §8); the low end
multiplies the Sonnet cost by 1.3. Break-even is +100 % tokens. Effort: 50 % less output on max-effort reviews (E: thinking
share 76 % at max against 52 % at high, USAGE-1 §6 F); $22 on STANDARD tickets, $11 more on FULL ones whose probes may keep max.
Sensitivity to my tags: if W2-56, W2-96 and W2-149 were C2, not C3, up to +$90 (with 4) or +$130 (without); no more Opus than that.

## 3 The CTO's share, and what stays Opus
CTO session $126 (4.6 pt, 7.9 %): untouched, Opus high (DEC-1120 (2)). With the leads, **$501 (18.2 pt, 31 %)** is long-context
Opus that no tier change reaches; USAGE-1 §6 A (fresh sessions at ~200k, est. $172 there) is the lever for it and is not
counted here (it overlaps the lead rows). Opus-priced tokens left after RUBRIC-2: $1,289 (80 %) with (4), $1,208 (75 %) without.

## 4 The projection (meter readings, `log/usage.txt`; 60 % at 16:00:07 on 11-10; 113 h to the reset)
| pace (pt/h) | no RUBRIC-2: 80 % / 100 % | with (4), 8.9-12.7 %: 80 % / 100 % | without (4), 10.8-15.5 %: 80 % / 100 % |
|---|---|---|---|
| **1.78 last 24 h** (base) | 11-11 03:14 / 14:29 | 04:20-04:52 / 16:41-17:45 | 04:36-05:18 / 17:12-18:36 |
| 2.31 last 6 h (day shift) | 11-11 00:39 / 09:18 | 01:30-01:55 / 11:00-11:49 | 01:42-02:14 / 11:24-12:29 |
| 1.09 week average | 11-11 10:20 / 11-12 04:40 | 12:07-13:00 / 08:15-10:00 | 12:33-13:41 / 09:06-11:23 |
The saving fraction is the table's total over the $1,497 of transcripts (fresh 80 left out: it does not repeat) and is applied to the
pace, so the remaining days keep this week's mix by role (E). Before the lift use the with-(4) column, after it the other. To
arrive at the reset below 80 % the pace must average 0.18 pt/h. **RUBRIC-2 buys hours, not days; DEC-1115 (4)'s priority rule
decides the week.** Not in the pace: set-up A's sandbox run (a no-transcript run like the fresh 80, about $100 or 4 pt, E) and
any cost after 16:00. If the remaining work is lead- and CTO-heavy (closes, waiting), the saving is below the band.

## 5 Method and assumptions
- Data: USAGE-1's `collect.py` and `workers.py` re-run to the 16:00:07 reading in my own scratch (copies; log/ untouched);
  tokens by kind and model per call. `spend.jsonl` not used: it holds 39 % of spend (USAGE-1 §7). Roles from the result file
  name (designer, review, engineer, product-spec) and the Agent call's type and description; leads = orchestrator type or
  "tests first", "second half", "batch", "red-fix" tasks; two doubtful helpers ($5) kept as leads (dearer tier).
- Classes (DEC-1120 (1)) are mine, from each ticket's subject and paths; the tickets' own `class` field names a kind
  (implementation, tool, skill), not C0-C3. C3: W2-05, 56, 58, 96, 128, 141, 142, 148, 149, 151, 153 and every ACT-named or
  pinned-gov task; C1: W2-130; the rest C2. A C2 reviewer is FULL (Opus) if the ticket is FULL or its profile is unknown
  (W2-13, 129, 139, 140, 145, 66, D-6), STANDARD (Sonnet) otherwise. Doubt always went to the dearer tier.
- Meter weight (assumption): **the meter weighs Sonnet at list price, half of Opus per token.** Evidence for: dollar
  measures fit the meter (R² 0.999, miss 0.56 pt) and every token count fits worse (2.0-2.7 pt), so the meter is price-like.
  Evidence against or none: `meterfit2.py`'s "per-model rate" is only each model's list cache-read price (0.20 Opus, 0.01
  Haiku) used to split dollars, not a fitted model weight; 99.7 % of the data is Opus and the non-Opus spend (Haiku $4, Sonnet
  $2) is below one point, so the fit cannot test it. If the meter counts a Sonnet token like an Opus one, the model
  savings in points fall to 0 and only the effort line (0.8-1.2 pt) remains; the dollar savings stand. Third-party pages
  (e.g. inventivehq.com/blog/claude-code-rate-limits-explained) say Opus draws more than Sonnet but give no formula (unverified).
- Not counted: the effect of DEC-1120 (3)'s promotion (a Sonnet round that fails twice goes back to Opus); the 200k handover.

## 6 Confidence, figure by figure, and what could not be measured
| figure | M/E | why |
|---|---|---|
| $1,497 transcripts + $109 fresh 80; 60 % at 16:00 | M | calls.jsonl by message id; FRESH-80-RESULT cost; usage.txt. Model $1,606 vs meter $1,650: $44 unattributed |
| $27.5 a point | M | fit of 95 readings; moves 0.7 % with today's data |
| spend by role | M ($), E (tags) | roles and classes are my reading of names and subjects |
| re-priced saving at same tokens | M arithmetic on E premise | prices fetched by USAGE-1 |
| the +30 % band | E | **no measured Sonnet-to-Opus token ratio exists**: USAGE-1, MODEL-TIERS-1, FRESH-80-RESULT have none; the only Sonnet helpers (ACT-EFFORT-HIGH-1 and ACT-PATHMAP-NS-2 preparers, 38 and 34 calls, $0.93 and $0.69) are two small jobs with no Opus twin |
| effort max to high | E | thinking share only; fewer tokens may mean more rounds |
| points | E | needs the meter weight above |
| projection | E | linear pace; the 1.09-2.31 spread is the real uncertainty, larger than the saving |
Could not be measured: the Sonnet token ratio (baseline for a later check, M, per session median: C2 designer 31 calls, $1.85;
C2 STANDARD reviewer 37 calls, $3.14; C2 engineer 38 calls, $2.34, all Opus; compare the first Sonnet rounds once spawns
record tier and class); the meter's model weights; the remaining work's size; set-up A's cost; 3 unidentified top-level
sessions ($15.6); the fresh 80's split by role.

## 7 Commands run, verdict, draft KPI lines
Run: `collect.py` (cutoff 16:00:07), `workers.py`, `analyze.py meter check`, `meterfit2.py`, the meter fit and `reprice.py`,
`final.py`, `eff.py`, `proj.py` (my copies and scripts, read-only on logs). Nothing else. Verdict: RUBRIC-2 saves about a tenth of the
week's list-price spend (8-12 % with (4), 10-14 % without; $133-231) and moves the 100 % line a few hours, not days; the CTO and leads are the bulk.
- KPI: spend under RUBRIC-2 is at least 8 % below the same work at Opus. `verify`: re-run `reprice.py` on the first full week after W2-60a.
- KPI: spawns record tier, class and promotion (DEC-1120 (3)). `verify`: every spend-log line since the lift names all three.
- KPI: the Sonnet token ratio is measured. `verify`: median calls per session of Sonnet C2 rounds at most 1.3 times the baselines in §6.
Proposed decisions: none; the ratio check above needs no run beyond the scripts.
