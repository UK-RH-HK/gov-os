# USAGE-1: where the week's usage went (for the owner)

Draft, 2026-11-10. Period: the reset (2026-11-08 09:00 UTC) to the meter reading of 2026-11-10 11:36:43 UTC (50.6 h).
M = measured (source named); E = estimated (basis named). $ = at Anthropic's list price (prices in §8).
pt = a point of the weekly meter ("week (all models)" in log/usage.txt).

## 1 Headline
- **The meter went 0 → 51 % in 50.6 h. Measured spend at list price: $1,385** (M: $1,276 from 429 transcripts plus
  $109 for the fresh 80, which kept no transcript). **One point of the week ≈ $27.5 at list price** (M: fit over 94
  readings, typical miss 0.5 pt). On that basis the whole week is worth about $2,750 at list price (E).
- **Where it went:** launched workers 49.5 % (24.9 pt), the CTO's in-session helpers 33.6 % (16.9 pt), the CTO's own
  session 7.9 % (4.0 pt), the fresh 80 7.9 % (4.0 pt), everything else 1.1 % (0.6 pt). The sentinel, dead-man, usage
  recorder and operator agent together cost **$3.2, 0.1 pt** (M).
- **Why:** 99.7 % of the transcript spend is Opus 5.5 and 97 % runs at effort high or max (M), and most of the bill is the context, not the answers:
  cache reads $575 (42 %), cache writes $389 (28 %), output $308 (22 %), the fresh 80 $109 (8 %) (M). The CTO and its
  lead-type helpers run long sessions whose median context is 250k-460k tokens (M), so each step re-reads that much.
- **Pace:** the last 24 h used 38 pt (M, 13 → 51 %). At that pace the week runs out on about **11-11 evening (UTC)**,
  three and a half days before the reset (E: linear).
- **Savings that keep quality:** the recommended set (§6) is worth about **$250, 9 pt (≈ 18 %)** over the same period
  (E), with no quality gate moved off Opus.

## 2 By source
| source | model | calls | output | cache read | cache write | $ list | pt | basis |
|---|---|---|---|---|---|---|---|---|
| CTO session (ad44f5fe) | opus-5-5 | 630 | 0.52 M | 310.4 M | 4.65 M | 109.69 | 4.0 | M transcript |
| CTO helpers (44 transcripts, 3 of them nested) | opus-5-5 | 5,110 | 4.62 M | 1,280.0 M | 23.4 M | 465.53 | 16.9 | M subagents/*.jsonl |
| Launched workers (190 transcripts, 73 worktree folders) | opus-5-5 | 8,741 | 10.23 M | 1,270.9 M | 28.5 M | 685.99 | 24.9 | M transcripts; own results agree (below) |
| Experiments: fresh 80 + its data runs (11-08 19:32-21:46) | opus reader/grader, sonnet checker | n/a | n/a | n/a | n/a | 109.05 | 4.0 | M FRESH-80-RESULT.md (cost only; `--no-session-persistence`) |
| Experiments: the independent writer's session | opus-5-5 | 1 | 7 | 0.03 M | 0.40 M | 3.24 | 0.1 | M (counts only) |
| Rehearsals in ~/gov-os-runs (6 result JSONs) | sonnet/haiku | 6 | | | | 0.06 | 0.0 | M result JSONs |
| Sentinel (b6a01869) | haiku-5-5 | 122 | 14.6 k | 12.2 M | 2.49 M | 3.14 | 0.11 | M transcript |
| Dead-man pushes (2 runs, cwd /tmp) | haiku-5-5 | 6 | 1.0 k | 0.12 M | 0.03 M | 0.01 | 0.0 | M transcripts |
| Usage recorder (95 `claude -p "/usage"` runs) | none | 0 | 0 | 0 | 0 | 0.00 | 0 | M: transcripts hold the command only, no model call |
| Operator agent wall runs (2) | sonnet-5-5 | | | | | ≈ 0.09 | 0.0 | M one ($0.045, session-output.json); E the other |
| Interactive session in ~/gov-os-operator (11-09) | opus-5-5 | 70 | 32 k | 12.7 M | 0.61 M | 8.09 | 0.3 | M transcript |
| Live tests that start claude (pytest, 90 transcripts) | haiku-5-5 | 194 | 53 k | 4.5 M | 1.64 M | 0.40 | 0.0 | M transcripts |
| **Total measured** | | 14,880 | 15.4 M | 2,891 M | 61.7 M | **1,385.3** | **50.4** | against the meter's 51 |
| Unattributed | | | | | | ≈ 16 | ≈ 0.6 | E: meter minus measured; inside the meter's 1 % rounding |
Input tokens (uncached) are negligible everywhere: 30.7 k in all (M). Fable: none used (M; the meter's Fable line 0 %).
Cross-check: the 188 workers with their own result JSON report total_cost_usd $683.39; priced here $683.11 (M).

## 3 By ticket and by day
| ticket (tree or helper's brief) | $ | pt | split |
|---|---|---|---|
| W2-149 (and -f11, -sgx trees) | 156.30 | 5.7 | workers 94, helpers 62 |
| CTO's own session | 109.69 | 4.0 | |
| W2-88 / K9: the fresh 80 | 109.05 | 4.0 | experiments |
| W2-20 | 95.01 | 3.5 | workers |
| W2-148 | 92.55 | 3.4 | workers 79, helpers 14 |
| W2-56 | 83.30 | 3.0 | workers 64, helpers 19 |
| D-10 red-fix list (lead helper) | 71.96 | 2.6 | helper; **plus $125.82 in thirteen "-d10" trees counted under their tickets: D-10 in all $197.78, 7.2 pt** |
| D-5 templates | 57.44 | 2.1 | helper |
| W2-141 | 52.74 | 1.9 | workers 46, helpers 7 |
| W2-121 ("Item 8") | 44.10 | 1.6 | helper |
| W2-128 | 37.27 | 1.4 | workers |
| Operator agent: ACT-OPERATOR-1 + W2-146 | 66.11 | 2.4 | helpers |
| D-6 | 31.79 | 1.2 | helpers 23, workers 9 |
| W2-145, W2-153, W2-96 | 30.63, 28.52, 27.28 | 3.1 | workers |
| about 40 more rows, each under $25 | 291.54 | 10.6 | incl. helpers with no id $4.86 |
All M (calls.jsonl; ticket from the worktree folder, a helper's description, or its first prompt's id). Full list:
`python3 -I analyze.py tickets`.

| day (UTC) | CTO | helpers | workers | experiments | other | $ total | pt at $27.5 | meter pt | $ per meter pt |
|---|---|---|---|---|---|---|---|---|---|
| 11-08 from 09:00 | 20.37 | 1.99 | 0 | 112.29 | 0.77 | 135.42 | 4.9 | 6 (0→6) | 22.6 |
| 11-09 | 74.82 | 342.86 | 477.38 | 0.06 | 9.77 | 904.89 | 32.9 | ≈ 31 (6→≈37) | 29.2 |
| 11-10 to 11:36 | 14.49 | 120.67 | 208.61 | 0 | 1.18 | 344.95 | 12.5 | ≈ 14 (≈37→51) | 24.6 |
Tokens (transcripts, M): 11-08 output 0.1 M, cache read 52 M, write 2.5 M; 11-09 11.0 M, 2,043 M, 43.6 M; 11-10 4.4 M,
796 M, 15.6 M. Meter at midnight 11-10: E, between 36 % (23:43) and 38 % (00:14).

## 4 Against the weekly meter
How well each measure, summed from the reset, predicts the meter at each of 94 readings (fit through zero):
| measure | one point = | typical miss | worst miss | R² |
|---|---|---|---|---|
| **$ at list price, fresh 80 included** | **$27.5** | **0.52 pt** | **1.6 pt** | **0.999** |
| $ at list price, transcripts only | $24.4 | 2.41 pt | 4.9 pt | 0.979 |
| input + output + cache write tokens | 1.49 M | 2.11 pt | 4.3 pt | 0.984 |
| all tokens (incl. cache reads) | 56.7 M | 2.62 pt | 5.0 pt | 0.975 |
| cache-read tokens | 55.2 M | 2.63 pt | 5.1 pt | 0.975 |
| output tokens | 0.29 M | 2.75 pt | 5.7 pt | 0.973 |
| API calls | 284 | 3.12 pt | 5.5 pt | 0.965 |
All M (`savings.py`, `meterfit2.py`). **Dollars at list price track the meter best**, and only if the fresh 80 is
counted: its 2.1 hours moved the meter 2 → 6 % while transcripts show $3, so runs without transcripts do count.
Per 30-minute interval the meter's 1 % steps give $12-51 a point (median $27.1, M). A two-part fit weighs cache-read
dollars at about 0.74 of other dollars (miss 0.44 pt): a hint, not proof, that the meter discounts cache reads.
Residuals: the worst miss (1.6 pt, 11-08 20:25) falls inside the fresh 80, whose cost is spread evenly over its
window here; the meter stayed about 1 pt ahead until 11-09 morning and has tracked within ±0.9 pt since 06:00 (M).

## 5 The ten largest and why
| # | consumer | $ (pt) | calls · hours | context per call, median / max (input+cache read) | why |
|---|---|---|---|---|---|
| 1 | CTO session | 109.69 (4.0) | 630 · 50 h | 457k / 966k | 134 wake-ups (100 background-task notices); every wake re-reads ~450k ($62 reads); 7 returns after idles > 1 h rewrote the whole context ($26.7); 1 compaction; high |
| 2 | D-10 lead helper (orchestrator) | 67.87 (2.5) | 606 · 12.4 h | 439k / 768k | one prompt then 611 Bash steps in one growing context (10k → 768k); reads $51.5 (76 %) |
| 3 | D-5 templates helper | 57.44 (2.1) | 491 · 15.5 h | 388k / 666k | same shape; 4 cold resumes after waits > 5 min ($10.9 of writes) |
| 4 | W2-121 "Item 8" helper | 44.10 (1.6) | 396 · 15.9 h | 372k / 614k | same shape; 3 cold resumes ($7.9) |
| 5 | ACT-OPERATOR-1 prep helper | 24.86 (0.9) | 164 · 1.9 h | 383k / 531k | large reads fast; thinking 39 % of output; 3 cold resumes ($7.1) |
| 6 | D-6 part 2 helper | 22.92 (0.8) | 299 · 4.3 h | 255k / 408k | 299 Bash steps, 0 Read |
| 7 | W2-146 operator-agent helper | 22.44 (0.8) | 172 · 3.5 h | 201k / 335k | 11 cold resumes after waits > 5 min: writes $13.6, more than its reads |
| 8 | W2-149 set-up A lead helper | 22.14 (0.8) | 208 · 10.7 h | 322k / 460k | long lead; thinking 33 % |
| 9 | W2-149 F11 / install ACT lead helper | 21.99 (0.8) | 242 · 1.7 h | 349k / 497k | dense run, no waits; reads $15.3 |
| 10 | Sets-globs ACT prep helper | 15.61 (0.6) | 169 · 1.9 h | 296k / 440k | reads $9.4; thinking 38 % |
All M (calls.jsonl, sessions.json; `savings.py` top10). All ten are Opus 5.5 at effort high; repeated file reads are
negligible (at most 22 Reads, at most 4 repeats each). The largest launched worker is #11: W2-20 engineer round 2,
$15.04, 131 calls, 333k median. Counted as one batch, the fresh 80 ($109.05) would be #2.
Shape of a worker (M): starts at 49k tokens (brief + system), 41 calls median, effort high (reviews at max: 76 % of
their output is thinking, against 52 % at high). By role: test designers $244 (74 sessions), reviewers $224 (64),
engineers $217 (53). Workers write the 1-hour cache ($226, a third of their cost); helpers the 5-minute one.

## 6 Savings that keep quality (options; nothing changes until the owner decides)
Savings are for this period's work ($1,385, 51 pt); a full week at this pace would be about twice as much.
| # | option | saving | evidence | risk |
|---|---|---|---|---|
| A | **Fresh sessions at a context limit:** a lead or helper hands over through its record and a fresh one continues when context passes ~200k; the CTO clears after a checkpoint at the same limit | **$172, 6.3 pt** (CTO $50, helpers $122; E: replayed on every call, 60k handover) | §5: the top ten are long single contexts; cache reads are 42 % of spend | lost in-context detail; mitigated by the checkpoint skill and records the leads already write |
| B | CTO clears (after its checkpoint) before a planned idle of more than an hour | ≈ $23, 0.8 pt (E: 7 rewrites of ~450k at $8/M become ~60k) | §5 #1: $26.7 of rewrites (M) | slower first step after the idle |
| C | **Sonnet 5.5 for ACT-preparation helpers** (drafting, rehearsing); reviews stay Opus | **$53, 1.9 pt** (E: half of $106, M) | Sonnet costs half of Opus on every token kind; a Sonnet reviewer found two real regressions in ACT-GUARD-FIX-3 | a missed guard edge case; the Opus review and the rehearsal stay as gates |
| D | 5-minute cache for launched workers (`FORCE_PROMPT_CACHING_5M=1`; third-party sources, check on this CLI first) | $52, 1.9 pt (E: replayed, gaps > 5 min rewritten) | workers' 1-hour writes $226 (M) | none to quality; saving smaller if workers wait longer |
| E | Sonnet 5.5 for test designers, **trial first** (two tickets, the Opus reviewer judging the tests) | $122, 4.4 pt (E: half of $244) | test designers are the largest worker role (M) | weaker tests are the main way defects slip through; decide on the trial's evidence |
| F | Reviewers at high, not max | ≈ $26, 0.9 pt (E: thinking share 76 % → 52 %) | §5 shape (M) | shallower reviews; reviews are the last gate; trial only |
| G | Shorter worker start (brief and copied EMG files, 49k at start) | ≈ $26 per 15k trimmed, 0.9 pt (E: 8,741 calls × 15k × $0.20/M) | §5 shape (M) | a brief that drops a needed rule |
| H | Fewer CTO wake-ups (one digest per helper instead of one per background wait) | $20-40, 0.7-1.5 pt (E: $0.82 a wake, 134 wakes) | §5 #1 (M) | slower reaction to a finished worker |
| - | Usage recorder, sentinel, dead-man, operator | nothing to save: $3.2, 0.1 pt in all (M) | §2 | |
Not proposed: smaller tool outputs and fewer re-reads. Read results are 28 M characters in all and repeats are 16 %
of worker Reads (M); the context grows mostly from the sessions' own output and length, which A addresses.
**Recommendation: A, B and C now (≈ $248, 9 pt, about 18 %; E), D once the setting is confirmed on this CLI, E and
F only after a trial.** No independent reviewer, test-design gate or engineer moves off Opus without that evidence.

## 7 The spend log (log/spend.jsonl, normalised today; the original kept as spend.jsonl.orig-20261110)
- **Since the reset: 169 lines; 125 carry a cost ($543.05); 44 carry none** (40 in-session helpers "not measured
  (subscription; no per-run price)", 3 workers, 1 note) (M).
- **Tokens: no line fills the typed token fields; 82 keep a free-text count (`orig_tokens`) in three units** (M):
  launched lines count **output tokens only** (10 of 12 checked equal the result's output_tokens); helper lines carry
  the Agent tool's figure (e.g. 453,515 for "Item 8", whose measured cost is $44.10); and **one W2-149 test designer
  line (11-09 19:45) counts 17,057,921 = 130 input + 200,305 output + 16,508,818 cache read + 348,668 cache write.**
- **Against the measured figures** (M): where a line has a cost it is the session's own total_cost_usd and matches
  (W2-149 designer $10.10 both; the fresh 80 $109.05 both). But the log holds **$543 of the measured $1,385 (39 %)**:
  workers $434 of $686, helpers $0 of $466, the CTO $0 of $110. The brake (spend.py) therefore sees workers only.
- Suggestion (for the owner's decision): log cost in dollars at list price for every session, helpers included, from
  the transcript's usage; never a summed token count.

## 8 Method and gaps
- **Prices (list, USD per million tokens; platform.claude.com/docs/en/about-claude/pricing, fetched 2026-11-10):**
  Opus 5.5 input 4, 5-min write 5, 1-h write 8, cache read 0.20 (0.05×), output 20; Sonnet 5.5 2 / 2.50 / 4 / 0.10 /
  10; Haiku 5.5 0.10 / 0.125 / 0.20 / 0.01 / 0.50 up to 100k prompt, 0.50 / 0.625 / 1 / 0.05 / 2.50 above; Fable 5.1
  10 / 12.50 / 20 / 0.25 (0.025×) / 50. All calls were standard speed, global inference (M). The skill route was not
  available to this session; the page was fetched.
- **Data (M):** every *.jsonl under ~/.claude/projects modified since the reset (429 transcripts), assistant calls
  de-duplicated by message id, calls after 11:36:43 dropped; result JSONs under ~/gov-os-worktrees, ~/gov-os-runs,
  ~/gov-os-operator/log and the scratch tree (333, of which 134 duplicate copies in W2-00-record, de-duplicated by
  session id). Only usage, model, effort, timestamps, ids, cwd, tool names, Read paths as hashes and result lengths
  were read; first prompts only for a regex ticket id. Nothing from held-out material was opened.
- **Re-run:** `python3 -I collect.py; python3 -I workers.py; python3 -I analyze.py > out-all.md; python3 -I
  savings.py > out-savings.md; python3 -I meterfit2.py` in this folder (USAGE_CUTOFF moves the end).
- **Gaps:** the fresh 80's tokens by kind (cost only, M from its record); two rehearsal project folders under the
  held-out path were not opened (they show no transcript since the reset); helpers with no ticket id $4.86; the
  second operator run (E); ≈ 0.6 pt of the meter unattributed (E); the meter's own weights are not published, so
  "$ list" is a fitted proxy, not its formula; savings A-H are replays or proportions (E), not trials.
