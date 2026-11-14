---
id: effort-20261113
role: research
ticket: owner's question of 2026-11-13, via the Wave 2 CTO (no ticket id given)
decisions: [none yet; it feeds the owner's decision on where to cut effort, 2026-11-13]
sources: [DEC-1089, DEC-1120, DEC-1157, USAGE-1]
generated: 2026-11-13 16:14 UTC
---
# Where the effort went, since the lift and in the last 24 hours

**Question.** Where did the effort go, as 100 %, in USD, usage points and lead-hours, in nine buckets; since the lift (2026-11-11 13:31 UTC) and in the last 24 hours (to 2026-11-13 16:14 UTC).
**Decision it feeds.** What the owner and the CTO cut or change in how work is run (the "what I would cut" lines).
**Stop rule.** Records that exist only; no suite run; every figure marked M (measured from a record) or E (estimated, with the rule); stop when both windows are filled and the sums tie to a measured total.

Legend: **M** measured from a record (a cost, a time, a count); **E** estimated by a stated rule; **M/E n% est.** a measured total of which n % is placed in its bucket by a rule; a bare **E** means everything in the cell is placed or split by a rule even where the inputs (tokens, costs) are measured. USD is at list price (Opus 5.5 / Sonnet 5.5 / Haiku 5.5) or the session's own `total_cost_usd`. `lead-h` = hours a ticket lead's session was alive (the lead ledger); `other-h` = hours of the CTO's active turns, in-session helpers, directly launched workers and the machine hours of the landing queue and the nightly (a worker inside a lead's run is not counted twice). Waiting rows count ticket-hours and idle hours, so they are not additive with working hours.

**Headline.** Window A (since the lift, 2026-11-11 13:31 to 2026-11-13 16:14): **$1,715**, **71 points** of the weekly meter (M), 33 tickets landed CLOSED by the queue. Window B (last 24 h): **$740**, **31 points**, 20 CLOSED. Spend per ticket landed CLOSED: $52 (A), $37 (B). One meter point is $23.9 (A) and $23.8 (B) at list price, spend up to the last meter reading (2026-11-13 16:01); USAGE-1 fitted $27.5 on 11-08..11-10, so the meter may weigh models or kinds differently from list price, or this set misses spend (see Gaps).
By kind of session (A): cto $553 (4 units), worker $518 (287 units), lead $343 (133 units), helper $299 (118 units), ambient $0 (3 units).
The largest single block is **the CTO's own turns plus its in-session helpers: 50 % of A** ($853); launched leads and workers together are 50 %.

## Window A: since the lift (2026-11-11 13:31 to 2026-11-13 16:14 UTC)
| bucket | share USD % | USD | usage pts | lead-h | other-h | produced |
|---|---|---|---|---|---|---|
| 1 Product work by phase | 31.1 | 533.2 M | 22.1 E | 90.5 E | 2.6 E | 33 tickets landed CLOSED by the queue (70 close records in all, bulk closes included); 231 sessions (leads and workers) |
| 2 Reviews and narrow checks | 11.0 | 188.2 M/E 19% est. | 7.9 E | 6.8 E | 4.4 M/E 67% est. | 26 review/probe records added; 130 review sessions, runs and helpers |
| 3 ACTs | 17.4 | 299.1 M/E 84% est. | 12.7 E | 0 | 34.4 M/E 18% est. | 26 distinct ACTs applied or committed (50 ACT commits); 73 ACT sessions |
| 4 CIT-Ps, records, packages | 5.2 | 88.7 E | 3.9 E | 0 | 5.8 M/E 79% est. | 48 package files and 50 commits naming a CIT-P added; 70 close records |
| 5 CTO session (orchestration, reports, decisions) | 18.8 | 321.7 E | 12.0 E | 0 | 18.0 E | 41 register versions (0.510 to 0.550, DEC-1126 to DEC-1170); 817 commits on the branch (all roles) |
| 6 Helpers (in-session, not placed above) | 6.5 | 111.6 E | 4.6 E | 0 | 16.2 M | 54 helper sessions (research, briefs, tools, sweeps); no countable close |
| 7 Landing queue and nightly | 2.6 | 43.8 E | 2.6 E | 0 | 21.5 M/E 10% est. | 43 landing runs, 34 CLOSED outcomes; 2 nightly run(s); 47 merge commits on the branch |
| 8 Rework | 7.5 | 128.0 M/E 85% est. | 5.2 E | 7.3 M | 4.4 M/E 33% est. | 9 ejections and 3 no-outcome landings; 119 failed or redone sessions |
| 9 Waiting | 0.0 | 0.0 M | 0.0 E | 23.1 M | 199.5 M/E 9% est. | nothing: the time in which no session was working |
| Unplaced | 0.0 | 0.2 M | 0.0 E | 0 | 0 |  |
| **Total** | 100.0 | 1714.6 M | 71.0 (meter: 71.0 M) | 104.6 (waiting excluded) | 107.4 (waiting excluded) | 817 commits |

## Window B: the last 24 hours (2026-11-12 16:14 to 2026-11-13 16:14 UTC)
| bucket | share USD % | USD | usage pts | lead-h | other-h | produced |
|---|---|---|---|---|---|---|
| 1 Product work by phase | 27.8 | 205.9 M | 8.6 E | 33.9 E | 0 | 20 tickets landed CLOSED by the queue (36 close records in all, bulk closes included); 102 sessions (leads and workers) |
| 2 Reviews and narrow checks | 12.9 | 95.2 M/E 26% est. | 3.7 E | 3.7 E | 3.1 M/E 58% est. | 2 review/probe records added; 69 review sessions, runs and helpers |
| 3 ACTs | 15.1 | 111.5 E | 5.1 E | 0 | 12.7 M/E 15% est. | 8 distinct ACTs applied or committed (10 ACT commits); 25 ACT sessions |
| 4 CIT-Ps, records, packages | 7.1 | 52.2 E | 2.4 E | 0 | 3.2 M/E 72% est. | 10 package files and 17 commits naming a CIT-P added; 36 close records |
| 5 CTO session (orchestration, reports, decisions) | 19.0 | 140.8 E | 4.8 E | 0 | 7.7 E | 22 register versions (0.529 to 0.550, DEC-1147 to DEC-1170); 284 commits on the branch (all roles) |
| 6 Helpers (in-session, not placed above) | 6.2 | 46.0 E | 1.8 E | 0 | 4.3 M | 18 helper sessions (research, briefs, tools, sweeps); no countable close |
| 7 Landing queue and nightly | 2.5 | 18.9 E | 1.8 E | 0 | 10.5 M/E 6% est. | 26 landing runs, 20 CLOSED outcomes; 1 nightly run(s); 23 merge commits on the branch |
| 8 Rework | 9.4 | 69.7 M/E 80% est. | 2.7 E | 5.8 M | 2.8 M/E 26% est. | 3 ejections and 3 no-outcome landings; 63 failed or redone sessions |
| 9 Waiting | 0.0 | 0.0 M | 0.0 E | 23.1 M | 138.8 M/E 7% est. | nothing: the time in which no session was working |
| Unplaced | 0.0 | 0.1 M | 0.0 E | 0 | 0 |  |
| **Total** | 100.0 | 740.3 M | 30.8 (meter: 30.8 M) | 43.3 (waiting excluded) | 44.3 (waiting excluded) | 284 commits |

Notes on the tables. (1) Bucket 1 holds the lead's own session cost whole (M); a lead's cost cannot be split by phase from its log, and a time split would charge a sleeping lead (see Method). Its phases show as the workers' cost (tests = designers, build = engineers, product-spec and research workers) and the lead-hours by phase (E, from the workers' intervals in the ledger). Landing as a phase is the lead's own verify/accept/merge time plus the merge workers. (2) Bucket 2 holds every independent auditor session on a ticket (rev-/rv-/au-/probe/check) and the helper auditors on narrow checks; ACT reviews are in bucket 3, package reviews in 4. The "review" phase of bucket 1 is therefore shown only here (counted once). (3) Bucket 8 is split: **8a measured** (a lead or worker that ended in error, a landing that ejected a ticket or ended without outcome) and **8b est.** (an engineer or test-designer round numbered 2 or more, taken as a redo; a review round 2+ is *not* moved, it checks a fix). Fold 8b back and bucket 1 gains $108 (A) / $55 (B). (4) Buckets 3, 4, 5, 7 contain the CTO's own turns placed by artefact timing (E): each turn goes to the next artefact (ACT file, package, close record, review record, register row, merge) written within 30 minutes, else to bucket 5. Sensitivity of the window-A USD to that window (15 min: b2 185, b3 298, b4 83, b5 338, b7 38, 30 min (default): b2 188, b3 299, b4 89, b5 322, b7 44, 60 min: b2 188, b3 301, b4 92, b5 309, b7 52). (5) Bucket 9 costs $0 by definition (no session alive); its rows are time: tickets waiting for the CTO or the owner between lead runs (174 ticket-hours in A, of which 5 are waiting now), tickets waiting on a closed gate, test commands waiting for a heavy slot (23.1 h, carved out of the lead hours of bucket 1 because the log starts 11-12 23:48 and holds them), and the CTO's idle gaps over 10 minutes. (6) Usage points are E everywhere: the meter total is M; each interval between two meter readings is shared by that interval's USD per bucket. Buckets with no LLM session (7's queue and nightly, 9) take none.

## Detail behind the buckets (USD, usage points, lead-hours, other-hours; basis as above)
| bucket | part | A USD | A pts | A lead-h | A other-h | B USD | B pts | B lead-h | B other-h |
|---|---|---|---|---|---|---|---|---|---|
| 1 | lead's own session cost (orchestration, verify, accept, land; all phases) | 326.0 | 14.1 | 0.0 | 0.0 | 137.9 | 5.7 | 0.0 | 0.0 |
| 1 | tests (designers) | 103.6 | 4.3 | 6.6 | 2.2 | 35.7 | 1.5 | 4.6 | 0.0 |
| 1 | build (engineers, product-spec, research) | 94.0 | 3.3 | 17.1 | 0.2 | 27.6 | 1.2 | 8.6 | 0.0 |
| 1 | land: merge and premerge workers | 9.6 | 0.4 | 0.0 | 0.2 | 4.6 | 0.2 | 0.0 | 0.0 |
| 1 | lead own time: verify, accept, merge, reading returns (no worker running) | 0.0 | 0.0 | 66.7 | 0.0 | 0.0 | 0.0 | 20.8 | 0.0 |
| 2 | independent reviews (ticket review rounds) | 131.5 | 5.9 | 6.8 | 0.1 | 63.4 | 2.6 | 3.7 | 0.0 |
| 2 | helper reviews and narrow checks | 23.5 | 1.0 | 0.0 | 2.4 | 19.4 | 0.9 | 0.0 | 2.2 |
| 2 | narrow checks and probes | 21.0 | 0.7 | 0.0 | 1.2 | 7.2 | 0.2 | 0.0 | 0.6 |
| 2 | CTO: narrow checks and review records | 12.2 | 0.3 | 0.0 | 0.6 | 5.2 | 0.1 | 0.0 | 0.2 |
| 3 | ACTs: building | 113.9 | 5.0 | 0.0 | 20.6 | 52.1 | 2.3 | 0.0 | 7.8 |
| 3 | CTO: ACTs (artefact timing) | 105.2 | 4.8 | 0.0 | 6.3 | 38.0 | 1.9 | 0.0 | 1.9 |
| 3 | ACTs: reviewing | 80.0 | 2.9 | 0.0 | 7.5 | 21.5 | 0.9 | 0.0 | 3.1 |
| 4 | CTO: close records | 40.3 | 2.1 | 0.0 | 2.9 | 27.3 | 1.5 | 0.0 | 1.7 |
| 4 | CTO: packages and CIT-Ps | 30.1 | 1.2 | 0.0 | 1.7 | 10.3 | 0.5 | 0.0 | 0.6 |
| 4 | helper: CIT-Ps, records, packages | 18.3 | 0.5 | 0.0 | 1.2 | 14.6 | 0.4 | 0.0 | 0.9 |
| 5 | CTO: orchestration (tickets, tools, notes, briefs) | 273.5 | 10.8 | 0.0 | 15.9 | 119.1 | 4.2 | 0.0 | 6.9 |
| 5 | CTO: decisions (register) | 28.9 | 0.8 | 0.0 | 1.4 | 11.1 | 0.3 | 0.0 | 0.6 |
| 5 | CTO: orchestration (no artefact within the window) | 19.4 | 0.4 | 0.0 | 0.7 | 10.6 | 0.3 | 0.0 | 0.2 |
| 6 | helpers (research, briefs, tools, sweeps) | 111.6 | 4.6 | 0.0 | 16.2 | 46.0 | 1.8 | 0.0 | 4.3 |
| 7 | CTO: merges and lands (hand merges) | 40.6 | 1.6 | 0.0 | 2.1 | 15.9 | 0.8 | 0.0 | 0.6 |
| 7 | CTO: nightly record | 3.3 | 1.0 | 0.0 | 0.2 | 3.0 | 1.0 | 0.0 | 0.0 |
| 7 | nightly (machine hours, no LLM) | 0.0 | 0.0 | 0.0 | 2.3 | 0.0 | 0.0 | 0.0 | 1.4 |
| 7 | landing queue (machine hours, no LLM) | 0.0 | 0.0 | 0.0 | 16.9 | 0.0 | 0.0 | 0.0 | 8.5 |
| 8 | 8b redo rounds: tests round >= 2 (est.) | 68.1 | 2.7 | 0.0 | 1.0 | 42.4 | 1.7 | 0.0 | 0.8 |
| 8 | 8b redo rounds: build round >= 2 (est.) | 40.2 | 1.6 | 0.0 | 0.0 | 13.1 | 0.3 | 0.0 | 0.0 |
| 8 | 8a failed or errored lead run (measured) | 17.4 | 0.8 | 7.3 | 0.0 | 13.3 | 0.7 | 5.8 | 0.0 |
| 8 | 8a failed or errored worker (measured) | 2.4 | 0.1 | 0.0 | 0.6 | 1.0 | 0.0 | 0.0 | 0.6 |
| 8 | 8a ejected or refused landing (measured outcome; hours share est.) | 0.0 | 0.0 | 0.0 | 2.8 | 0.0 | 0.0 | 0.0 | 1.4 |
| 9 | slot waits for a test run (carved out of lead or worker hours) | 0.0 | 0.0 | 23.1 | -0.0 | 0.0 | 0.0 | 23.1 | -0.0 |
| 9 | CTO idle between turns (>10 min; owner, leads or queue: cause not recorded) | 0.0 | 0.0 | 0.0 | 19.0 | 0.0 | 0.0 | 0.0 | 11.3 |
| 9 | ticket waits: on the CTO or the owner (between lead runs) | 0.0 | 0.0 | 0.0 | 174.3 | 0.0 | 0.0 | 0.0 | 127.4 |
| 9 | ticket waits: on the gate or a launch refusal | 0.0 | 0.0 | 0.0 | 6.2 | 0.0 | 0.0 | 0.0 | 0.1 |
| U | unplaced: usage recorder, sentinel, dead-man, side sessions | 0.2 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 |

## The ten largest single consumers
Window A (since the lift). A consumer is one session, one run or one helper; a lead's cost is its own total (workers separate).
| # | USD | hours | what | bucket | basis |
|---|---|---|---|---|---|
| 1 | 390.3 | 22.7 | CTO session b2f0511f (Opus; b5 61%, b3 19%, b4 11%, b7 9%, b2 1%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 2 | 75.5 | 4.9 | CTO session b40cba91 (Opus; b5 55%, b3 19%, b4 10%, b2 8%, b7 8%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 3 | 54.8 | 2.7 | CTO session f3886235 (Opus; b5 42%, b3 23%, b4 22%, b7 10%, b2 4%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 4 | 32.8 | 1.5 | CTO session 8ddb8b14 (Opus; b5 59%, b4 32%, b3 8%, b7 0%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 5 | 11.4 | 0.8 | W2-115 engineer eng-1 | 1 | USD M; hours M |
| 6 | 10.1 | 2.4 | W2-88 engineer eng-1 | 1 | USD M; hours M |
| 7 | 9.9 | 0.8 | W2-88 independent-test-designer td-3 | 8 | USD M; hours M |
| 8 | 9.2 | 0.7 | W2-170 independent-test-designer td-1 | 1 | USD M; hours M |
| 9 | 8.7 | 0.7 | W2-88 independent-test-designer td-1 | 1 | USD M; hours M |
| 10 | 7.9 | 0.9 | in-session helper general-purpose b2f0511f/a7495755 (ACTs: building) | 3 | USD M; bucket by agent type and ACT/package/check keywords E |

Window B (last 24 h).
| # | USD | hours | what | bucket | basis |
|---|---|---|---|---|---|
| 1 | 185.7 | 10.1 | CTO session b2f0511f (Opus; b5 64%, b4 14%, b3 13%, b7 8%, b2 2%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 2 | 54.8 | 2.7 | CTO session f3886235 (Opus; b5 42%, b3 23%, b4 22%, b7 10%, b2 4%) | 5 (split) | USD M; bucket split E; hours = active turns E |
| 3 | 10.1 | 2.4 | W2-88 engineer eng-1 | 1 | USD M; hours M |
| 4 | 9.9 | 0.8 | W2-88 independent-test-designer td-3 | 8 | USD M; hours M |
| 5 | 8.7 | 0.7 | W2-88 independent-test-designer td-1 | 1 | USD M; hours M |
| 6 | 7.9 | 0.9 | in-session helper general-purpose b2f0511f/a7495755 (ACTs: building) | 3 | USD M; bucket by agent type and ACT/package/check keywords E |
| 7 | 7.8 | 0.5 | in-session helper general-purpose b2f0511f/a514d4cb (helpers (research, briefs, tools, sweeps)) | 6 | USD M; bucket by agent type and ACT/package/check keywords E |
| 8 | 7.3 | 4.3 | lead W2-88 run4 (ERROR) | 8 (lead's own cost) | USD M; hours M (ledger) |
| 9 | 6.3 | 0.3 | in-session helper general-purpose b2f0511f/a567439d (helpers (research, briefs, tools, sweeps)) | 6 | USD M; bucket by agent type and ACT/package/check keywords E |
| 10 | 6.2 | 0.8 | in-session helper independent-auditor b2f0511f/aca3bbb2 (helper reviews and narrow checks) | 2 | USD M; bucket by agent type and ACT/package/check keywords E |

Largest landings by wall time (queue machine hours, $0 in LLM, M): A: landing run 20261112-085008 (1 ticket(s)) 3.6 h (bucket 7, machine hours, $0); landing run 20261112-151606 (1 ticket(s)) 1.2 h (bucket 7, machine hours, $0); landing run 20261112-173908 (1 ticket(s)) 1.2 h (bucket 7, machine hours, $0); landing run 20261113-151808 (1 ticket(s)) 0.8 h (bucket 7, machine hours, $0). B: landing run 20261112-173908 (1 ticket(s)) 1.2 h (bucket 7, machine hours, $0); landing run 20261113-151808 (1 ticket(s)) 0.8 h (bucket 7, machine hours, $0); landing run 20261112-202304 (1 ticket(s)) 0.6 h (bucket 7, machine hours, $0); landing run 20261113-015405 (1 ticket(s)) 0.4 h (bucket 7, machine hours, $0).
Below the CTO sessions the biggest single items are a handful of $7-$11 sessions (an engineer or test designer's first round, a helper that built an ACT bundle); the spend is many small sessions, not a few runaway ones: the largest non-CTO session is 11.4 USD, 0.7 % of A.

## What I would cut (each with its saving; E unless marked)
1. **A fresh CTO session at 300k tokens of context instead of running to 460k median / 840k p90.** The CTO's main sessions re-read their context every turn: cache reads are $411 of $553 (74 %, M from tokens); the cache reads above a 300k cap cost $182 (A) / $80 (B). Saving up to **$182 (A) / $80 (B)** minus one handover re-read per restart (a cap at 200k: $248 / $107).
2. **Fewer redo rounds of tests and builds (8b).** 96 sessions in A cost $107 (B: 50, $55); median $0.7 each. A review of the test design before the build starts, or one finding list per round, would remove about half: **$54 (A) / $27 (B)** (E: half is my assumption, not measured).
3. **In-session helpers that inherit Opus run on Sonnet** where they build or research (not the independent reviewers): Opus helpers outside bucket 2 cost $130 (A) / $112 (B); at Sonnet's list price (half of Opus on every token kind) the saving is **about $65 (A) / $56 (B)**, quality unproven on these jobs (USAGE-1 §6 kept gates on Opus; these are not gates).
4. **One review per ACT bundle, and no round 2 for findings that are only P2.** ACT reviews cost $80 (A) / $21 (B): auditor workers' first reviews $32, their round-2-or-later reviews $16 (M, from the log names), helper ACT reviews $32 (A) / $21 (B) (rounds not separable without reading their titles). Saving **$16 measured (A)**, up to about half of the helper reviews (E, $16 A / $11 B) if a second round is dropped for P2-only findings.
5. **Do not start a lead into a shut gate or a task that errors.** Failed or errored lead runs cost $17.4 (A) / $13.3 (B) (M, ledger status ERROR, LAUNCH_BLOCKED, NO_STATUS) and 2.4 in failed workers: saving **$17 (A) / $13 (B)**.
6. **Waiting is free in dollars but not in time:** 23.1 lead-hours blocked on a heavy slot (M) and 174 ticket-hours waiting for the CTO or the owner between lead runs (M, 5 still open): saving **$0**, but the owner's decisions and a second slot pool are what move closes per day.

## Method
Period. A = 2026-11-11 13:31 to 2026-11-13 16:14 UTC (the lift to the run of this report); B = the 24 h before the same instant. A session that straddles a boundary counts by time overlap (cost and hours pro rata); the CTO's turns are cut exactly by timestamp.
Prices (list, USD per million tokens, from USAGE-1 §8, platform.claude.com/docs/en/about-claude/pricing as fetched 2026-11-10; `tools/spend.py` holds none, it logs `total_cost_usd`): Opus 5.5 in 4, 5-min write 5, 1-h write 8, cache read 0.20, out 20; Sonnet 5.5 2 / 2.50 / 4 / 0.10 / 10; Haiku 5.5 0.10 / 0.125 / 0.20 / 0.01 / 0.50 to a 100k prompt, 0.50 / 0.625 / 1 / 0.05 / 2.50 above. **Check:** the same prices applied to a CTO transcript and its subagent transcripts give $122.33 for b40cba91 (the session's own cost-state line: $122.33), $554.56 for b2f0511f ($556.15) and $152.04 for 8ddb8b14 ($148.12; its last cost-state line may predate its end): within 3 %.
Sources and what each gave.
- **Launched workers (M):** `log/spend.jsonl`, 287 workers with cost in A, one row per session; cost from the worktree log's `total_cost_usd` where the log exists (M), else the spend row's own cost; end time from the log file, start = end - `duration_ms`. For 147 workers whose worktree log is gone, the duration (hours only) is E: the role's median seconds per dollar. The total ($517.3 in A) equals the sum of the spend rows in the window ($517.0, pro-rata difference only). Roles and log names decide the bucket (ACT-*: 3; auditor: 2; designer: tests; engineer, product-spec, research: build; *merge*: land); non-zero exit or `is_error`: 8a; `td-/eng-` round >= 2: 8b.
- **Leads (M cost, E phase split):** `log/*-A5-*.json` via `tools/lead_ledger.py` (143 runs; its lead cost sum $339.12 equals the sum of `total_cost_usd` over the lead logs). Lead-hours = the run's wall time; the partition into tests, build, review, verify/land and the lead's own time uses the ledger's worker intervals (E). 5 runs still RUNNING have no final cost yet; their 5.4 lead-hours are counted, their cost is not (undercount est. $14 at the window's $/lead-hour). Cross-check of lead-hours: `tools/measure_week.py daily` gives 11.63 + 75.71 + 38.69 = 126.0 h (the sample-based count, flagged partial on 11-11); the ledger gives 127.7 h.
- **The CTO (M tokens, E bucket):** `message.usage` token counts, model and timestamps only, from the transcripts of 8ddb8b14 (to its end 15:58 on 11-11; only turns after the lift count), b40cba91, b2f0511f and f3886235 (this session, up to the run), de-duplicated by message id. 8ddb8b14 was added by the same marks as the others (same project folder, same entry point, hand-over at 15:58: its stand-by file names it CTO); the owner named b2f0511f, f3886235 and b40cba91 if in the window. No message text was read. Hours = the sum of gaps up to 10 minutes between consecutive turns (E: active time, not session span); gaps over 10 minutes and under 12 h are CTO idle in bucket 9 (E: the cause is not recorded; the CTO stand-by files, which name the owner as the cause, cover only 2.3 h of them).
- **Placing the CTO's turns in buckets 2, 3, 4, 5, 7 (E):** from git (first-parent commits on w2/integrate with their paths: packages/ and closes/ to 4; reviews/ and docs/probes to 2; the register and DECISIONS-IN-FORCE to 5 "decisions"; ACT-* subjects and every file under `acts/` to 3; merge commits to 7; briefs/ and other paths to 5) and file times; each assistant turn goes to the first such artefact written within 30 minutes after it, else to 5. This uses timestamps only. It is the weakest figure in the report (see Gaps): treat bucket 4's and 5's CTO part as plus or minus a third.
- **In-session helpers (M tokens, E bucket):** subagent transcripts under each CTO session (usage and timestamps), classed by `agentType` and the short description key words: an ACT in its title: 3 (build, rehearse or review); an auditor on anything else: 2; package, CIT-P, record: 4; the rest: 6. No transcript text was read; the report names a helper by its id and agent type. The spend log holds no helper line in this window (0 `agent` rows), so helpers are measured here only.
- **Landing queue and nightly (M time, $0):** `dispatch/dispatch.log` land started/finished pairs (43 runs in A); `land-dispatch-*.out` shows no model call (gitleaks, kernel gate, reds traced, merge). A landing that ejected a ticket goes to 8a for the ejected share of its hours (E). The nightly is the `actual_s` of `log/nightly/history.jsonl` for runs ending in the window. The lands' CPU cost is not in USD or points.
- **Waiting (M time):** ledger waits ("waiting on the CTO or the owner", launch refusal, brake), `log/heavy-slot-waits.jsonl` (starts 2026-11-12 23:48: waits before it are not recorded), and the CTO idle gaps above. `log/refused-starts.jsonl` (27 ticks) is inside the ledger's launch refusals.
- **Usage points (M total, E split):** `log/usage.txt` ("week (all models)"), reset-aware (a drop counts as the new value, as `measure_week.py`); the meter reset on 11-12 between the 07:52 reading (94 %) and 09:51 (0 %), so up to about 6 points of the gap are unmeasured (est. 1 to 2 at the neighbouring rate). Each reading-to-reading interval's gain is shared among buckets by that interval's USD; 0.0 points fell in intervals with no priced spend. Buckets 7 and 9 have none by construction.
- **Produced (M):** `dispatch/land-done.txt` (CLOSED outcomes), git subjects and added files (`closes/`, `packages/`, `reviews/`) by commit time, the register's version rows by `git blame` time.
Commands run (read-only): `tools/lead_ledger.py --since 2026-11-11T13:31 --out <here>/lead-ledger-window.jsonl`; `tools/measure_week.py daily` (cross-check); `python3 -I build.py --W 30|15|60`, `python3 -I aggregate.py <units>`, `python3 -I cto_context.py`, `python3 -I make_report.py` (all in this folder; `run_all.sh` runs the chain). `git log`, `git blame` on the register. No pytest, no suite.

## Gaps and what would shake the figures
- **The CTO's split across 2, 3, 4, 5, 7 is E.** It is a timing rule: sensitivity in note (4) shows bucket 5 moves 309 to 338 and bucket 4 83 to 92 (A, USD) across 15 to 60 minutes. The sum of the CTO's USD ($ 553) is M.
- **Lead cost by phase is not recorded:** bucket 1 shows the lead's own cost whole; the phase hours are E.
- **Redo (8b) is a rule,** not a recorded fault: a round 2 may be new scope. Bucket 8 is 7.5 % with it and 1.2 % without.
- **Spend this set does not see:** 5 runs still running (above); the operator agent and rehearsal folders ($0.07 in the operator log, M); sessions of other tools; the points of the 11-12 reset gap; any usage the meter counts that no transcript or log shows. The account's meter also counts what this set cannot name, so $ per point is only a fitted proxy (USAGE-1 §8).
- **Unplaced:** ambient sessions in the project folder that are neither CTO nor helper (usage recorder, sentinel, dead-man, side sessions): $0.24 (A) / $0.13 (B), M, kept apart; nothing else is unplaced.
- **Hours:** worker hours are inside the leads' hours for tickets with a lead; ACT reviewers and directly launched workers count in other-h; the sum of lead-h and other-h is not a headcount of anything (parallel). The ledger's wall time includes a lead waiting on its worker.
- **This session** (the measuring helper, a subagent of f3886235) is counted in bucket 6 up to the run time: $2.71 so far (M), 0.16 % of A.
- **No commit:** this record sits in the scratch folder (not tracked), so there is no commit of its own; the CTO may commit it.


## Verdict
The effort is 50 % the CTO's own turns and in-session helpers (cache reads of a 463k-token median context are 74 % of the CTO's cost), 31 % ticket product work (the leads' own sessions are 19 % of all spend, more than the designers and engineers together at 12 %), and 7.5 % rework with the redo rule (1.2 % measured). Waiting costs no dollars but holds 174 ticket-hours and 23 lead-hours.
The three largest levers, in order, are the CTO's context size (up to $182 in A), the redo rounds (about $54) and Opus helpers (about $65); together about 18 % of A (E).

## Draft KPI lines (each with verify)
- KPI-EFF-1: the CTO's main sessions' median context stays at or under 300k tokens (now 463k in A, 492k in B). verify: `python3 -I .gov-runtime/scratch/orchestrator/drafts/effort-20261113/cto_context.py` and read `ctx_median` in `cto_context.json`.
- KPI-EFF-2: bucket 8 (rework, with the redo rule) at or under 5 % of 24 h spend (now 7.5 % in A, 9.4 % in B). verify: `bash .gov-runtime/scratch/orchestrator/drafts/effort-20261113/run_all.sh && python3 -I .gov-runtime/scratch/orchestrator/drafts/effort-20261113/make_report.py`, then the "8 Rework" row of window B.
- KPI-EFF-3: lead runs ending ERROR, LAUNCH_BLOCKED or NO_STATUS at or under 2 per 24 h (now 4 in B, 7 in A). verify: `python3 -I .gov-runtime/scratch/orchestrator/tools/lead_ledger.py --since <24 h ago> --no-write --md` and count those statuses.
- KPI-EFF-4: spend per ticket landed CLOSED at or under $40 over 24 h (now $37 in B, $52 in A). verify: the headline of this report re-run; CLOSED outcomes from `dispatch/land-done.txt`.

## Residuals
The CTO's placement (E), the phase split of lead cost, the redo rule and the points split are rules, not records (Gaps). Nothing in this report is a decision; the cuts are recommendations to the CTO. Not run: any suite. Proposed runs for the lead: none needed; to tighten the CTO's split, the CTO could tag its own turns by bucket in a log line (cheap, would make bucket 4 and 5 measured).
