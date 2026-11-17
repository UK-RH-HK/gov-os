# Audit 09: the owner's usage audit of the last two days

Date: 2026-11-17 (data to 22:33 UTC; window 2026-11-15 00:00 to 22:33 UTC, 62.6 h)  
Commit: `a246f72b2` (w2/integrate)  
Sources read: `docs/emergency-2/EMERGENCY-2.md` (in full), `docs/audit/emergency-2026-11/retro-P1-usage.md` and its scripts, all Claude Code transcripts under `~/.claude/projects/` (main tree, 102 CTO subagents typed by `*.meta.json`, worktrees, `gov-os-runs`, the operator's folder, the EXAMIN run folder, live-test folders), 158 lead/worker/adopter result logs with `total_cost_usd`, `log/spend.jsonl`, `log/usage.txt`, the role files, `~/.claude/settings.json`, DEC-838, DEC-1118 to DEC-1120, DEC-1141, DEC-1171, DEC-1183.

Memory first: 2 `gov retrieve` calls, both helped. The first returned USAGE-1, USAGE-RUBRIC-2 and DEC-1118 (the $ per plan point, the fresh-80 cost, the savings A to F). The second returned DEC-1120's model table, DEC-1171's compaction trial and MODEL-TIERS-1's finding that helper Opus comes from an environment line; I confirmed that line in `~/.claude/settings.json:3`. Each was followed by a search in my own words (register greps for DEC-1183, DEC-1141; transcript scans).

## The answer in ten lines

1. The two days used **$1,616 at the CLI's own rates, 4.16 billion tokens, and 65 % of the weekly plan** (0 % at the 11-15 09:00 reset; 61 of the week's 168 hours gone). One plan point is $23.6.
2. **78 % of it ($1,254, 51 plan points) was spent on 11-16.** Three hours (15:00 to 18:00 UTC) took $436, 27 % of the window.
3. **By who:** the CTO's own apparatus (main session plus its subagents) spent 64 %. The CTO's 35 `fork` helpers alone spent 30 %. All ticket trees together (leads, test designers, engineers, reviewers) spent 19 %. Engineers and test designers, who write the code and tests, spent 8 %. Ticket leads spent more than engineers and test designers together ($143 against $132).
4. **By activity (P1's categories):** coordination 31 %, security 25 %, product work (EXAMIN, W2-81 proving run) 18 %, ceremony 15 %, the emergency's own work 6 %, Gov OS product development 5 %.
5. **Against EMERGENCY-2:** 39 % ($635) went into machinery that EMERGENCY-2 retires (guard, sandbox, box, permissions, ACTs, the operator job runner). 8.5 % ($138) went to turns woken by the inbox waiter and the idle-check Stop hook. 15 % went to the build and finish list, 17 % to the proving run and EXAMIN.
6. **By model:** Opus 95.4 % of USD, Sonnet 4.5 %, Haiku and Fable 0. DEC-1120's own table asks for Sonnet in more places than it got.
7. **Why:** the cost is the context, not the answers. 52 % of the USD was spent on messages that carried more than 300k tokens of context, and 30 % on messages above 600k. Only the CTO's main session, its forks and the EXAMIN CTO ever got that large.
8. **What to change, in short:** stay off the retired machinery (up to 39 %); no `fork` helpers and no watcher wake-ups (about 7 % more); review only red work (3 %); follow DEC-1120's table for models (3 to 4 %, and 2 to 3 % more if leads move to Sonnet). Together about 55 to 57 % of this window's USD, so the same work would have cost about $690 to $730. The ranked list is below.
9. The week is at 65 % with 4.4 days left. That leaves about 35 points, about $830, about $185 a day. On 11-16 the day's spend was $1,254.
10. No session in the window built or measured EXAMIN's memory. Its Wave 0 took 3.7 % ($59, the EXAMIN CTO). The two fresh-80 measures E2 needs cost about 4 points each (USAGE-RUBRIC-2 §2) and are not in these figures.

## Method, and checks

- **Cost.** I priced every de-duplicated assistant message by its four token counts at the rates the CLI itself recorded. I fitted those rates to 441 per-model rows of the logs' `modelUsage`, and the fit is exact: Opus 5.5 $4 input, $20 output, $8 cache write (1-hour tier), $0.20 cache read per million tokens; Sonnet 5.5 half of that; Haiku 5.5 $0.10 and $0.50 (cache rates scaled; the amounts are under $1). P1 used list-type rates times 0.52; this is the exact replacement.
- **Check.** For 158 headless sessions that have a result log with `total_cost_usd`, my transcript cost matches the log (median ratio 1.000; $501 mine, $485 logged; the one outlier is the EXAMIN CTO, whose log covers only its last resume).
- **Plan.** `usage.txt` readings (81 between the 11-15 reset and now) against my cumulative USD fit at $23.6 a point (a through-origin fit; USAGE-1 had $27.5 at list price). Opus is 95 % of the spend, so the meter's model weights do not matter here.
- **Skipped.** Nothing under the walls: the walls are gone, so `~/gov-os-operator`'s project folder is in. There are no evaluation, hidden or held-out project folders in `~/.claude/projects/`; I opened none.
- **Classification** is P1's rule (`rules.py`: security, ceremony, product, build, coordination, in that order), with a sixth category added for the emergency's own work. The CTO's main sessions are classed per message from the tool calls, as in P1 (P1 checked 85 % agreement on a sample of 40; I did not repeat it). Subagents and worktree sessions are classed per session from their description or ticket.
- **Scripts** are in my scratch folder `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/036b4433-fcd4-48f3-bb08-6f78d034d878/scratchpad/u/` (`scan2.py`, `build.py`, `act.py`, `theme.py`, `msgs.py`, `trig2.py`, `trig4.py`, `gen.py`, `gen2.py`, `extra.py`, `mem.py`).

## Table 1: by session

Top 25 of 357 sessions that made at least one call, by USD (rank by tokens in its own column). The top 25 spent 58.1 % of the window. Two more sessions are in the top 25 by tokens but not by USD: the fork "Record DEC-1200, file two tickets, rehearse (b)" (38M tokens, $9, starting context 795k) and W2-186's test designer (28M, $6). Active hours are the sum of gaps of 5 minutes or less inside the session; concurrent sessions overlap, so the column does not add to wall time.

| # | session | role | what it did | model | active h | tokens (M) | tok rank | USD | share | msgs | median ctx (k) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `acd80751` | CTO main tree | the retiring CTO session (11-15 00:05 to 11-17 00:12) | Opus | 12.7 | 1118 | 1 | 320 | 19.8% | 2081 | 543 |
| 2 | `afd1e60e` | CTO sub: fork | Build operator job runner | Opus | 5.5 | 184 | 2 | 105 | 6.5% | 379 | 470 |
| 3 | `a10858a2` | CTO sub: fork | Build P-JOBS-USER-1 (B) session sandbox | Opus | 1.2 | 131 | 5 | 90 | 5.6% | 186 | 754 |
| 4 | `9d3404b0` | product CTO (EXAMIN) | EXAMIN CTO run (W2-27) | Opus | 2.1 | 166 | 3 | 50 | 3.1% | 410 | 401 |
| 5 | `a6705640` | CTO sub: fork | Build ACT-GUARD-FIX-7 bundle | Opus | 5.2 | 138 | 4 | 47 | 2.9% | 301 | 432 |
| 6 | `a8e97078` | CTO sub: fork | Build ACT-DEADMAN-INBOX-1 bundle | Opus | 0.6 | 46 | 12 | 36 | 2.2% | 74 | 614 |
| 7 | `80b7a1ca` | operator | Owner instructions: EXAMIN's setup, messages 2 to 4 below, in order, with GOV_RO | Opus | 1.4 | 58 | 9 | 31 | 1.9% | 236 | 232 |
| 8 | `a8e5e960` | CTO sub: fork | Build the 0.1.1 re-pin bundle | Opus | 3.5 | 71 | 7 | 29 | 1.8% | 205 | 338 |
| 9 | `6542ebab` | ticket leads | lead of W2-111 | Opus | 1.3 | 95 | 6 | 27 | 1.6% | 333 | 292 |
| 10 | `ab1eecda` | CTO sub: fork | Build ACT-BOX-LAUNCH-1 bundle | Opus | 0.6 | 58 | 10 | 22 | 1.4% | 123 | 464 |
| 11 | `a6e2e7e7` | CTO sub: fork | Build (O) ACT runner change | Opus | 0.3 | 41 | 15 | 15 | 0.9% | 65 | 623 |
| 12 | `ab5add6d` | CTO sub: fork | Fresh-80 measure rule: amendments, cost, job | Opus | 0.3 | 41 | 14 | 15 | 0.9% | 96 | 426 |
| 13 | `aa9cb9e6` | engineers | W2-111 engineer: r5: the hook's fixed cost cut, and the live hook's diff for ACT-GUARD- | Opus | 1.0 | 43 | 13 | 15 | 0.9% | 161 | 282 |
| 14 | `c96a5899` | ticket leads | lead of W2-60b | Opus | 0.7 | 40 | 16 | 13 | 0.8% | 187 | 217 |
| 15 | `a268e2ab` | CTO sub: general-purpose | Review ACT-GUARD-FIX-6 build 2 | Opus | 1.0 | 29 | 24 | 13 | 0.8% | 137 | 217 |
| 16 | `a062bcf4` | CTO sub: fork | Guard FP package, legacy-docs, ACT follow-ups | Opus | 0.3 | 52 | 11 | 12 | 0.8% | 81 | 638 |
| 17 | `036b4433` | CTO main tree | the fresh CTO session (from 11-17 21:54) | Opus | 0.6 | 36 | 18 | 12 | 0.8% | 147 | 238 |
| 18 | `a9909ba2` | CTO sub: general-purpose | Build live-hook ACT-GUARD-FIX-6 | Sonnet | 1.5 | 63 | 8 | 12 | 0.7% | 117 | 545 |
| 19 | `403b846f` | adopters (W2-81 runs) | W2-81 run 0-1-0 typescript-monorepo | Opus | 0.7 | 34 | 19 | 12 | 0.7% | 184 | 183 |
| 20 | `ac462eb6` | CTO sub: fork | Triage the 11-16 nightly's 10 reds | Opus | 0.7 | 33 | 20 | 11 | 0.7% | 82 | 407 |
| 21 | `3de68e5b` | adopters (W2-81 runs) | W2-81 run 0-1-0 secret-history | Opus | 0.8 | 33 | 21 | 11 | 0.7% | 180 | 187 |
| 22 | `544cbe6b` | adopters (W2-81 runs) | W2-81 run 0-1-0 python-app-clean | Opus | 0.7 | 31 | 22 | 11 | 0.7% | 181 | 174 |
| 23 | `489da3cf` | adopters (W2-81 runs) | W2-81 run 0-1-0 legacy-docs | Opus | 0.7 | 29 | 23 | 10 | 0.6% | 170 | 174 |
| 24 | `a7228a9a` | CTO sub: fork | Build ACT-GUARD-FIX-9 bundle | Opus | 0.6 | 24 | 31 | 10 | 0.6% | 77 | 317 |
| 25 | `2bd720c1` | adopters (W2-81 runs) | W2-81 run 0-1-0 rust-workspace | Opus | 0.7 | 26 | 27 | 10 | 0.6% | 157 | 161 |
| | top 25 together | | | | | 2618 | | 938 | 58.1% | | |

Source: transcripts `~/.claude/projects/<folder>/<session>.jsonl`; subagents `<parent>/subagents/agent-<id>.jsonl` with `agentType` and `description` from the `.meta.json` beside them. Eleven of the 25 are CTO forks. Thirteen of the 25 build or review guard, ACT, re-pin or sandbox machinery (rows 2, 3, 5, 6, 8, 10, 11, 15, 16, 18, 24) or are the lead and an engineer of W2-111, the guard-hook ticket (rows 9, 13).

## Table 2: by role

| role | sessions | tokens (B) | USD | share | active h | messages | Opus share of USD | median of sessions' median ctx (k) |
|---|---|---|---|---|---|---|---|---|
| CTO subagents: fork | 35 | 1.16 | 484 | 30.0% | 22.6 | 2394 | 100% | 604 |
| CTO main tree (retiring CTO) | 1 | 1.12 | 320 | 19.8% | 12.7 | 2081 | 100% | 543 |
| CTO subagents: general-purpose | 57 | 0.38 | 182 | 11.3% | 12.1 | 2468 | 83% | 120 |
| adopters (W2-81 runs) | 65 | 0.38 | 175 | 10.8% | 10.9 | 3161 | 99% | 79 |
| ticket leads | 31 | 0.36 | 143 | 8.8% | 8.8 | 2346 | 100% | 111 |
| engineers | 28 | 0.22 | 81 | 5.0% | 6.6 | 1383 | 80% | 106 |
| product CTO (EXAMIN) | 9 | 0.18 | 59 | 3.7% | 2.5 | 554 | 98% | 63 |
| test designers | 32 | 0.13 | 51 | 3.2% | 4.2 | 900 | 53% | 90 |
| reviewers/auditors | 20 | 0.06 | 38 | 2.4% | 2.6 | 674 | 100% | 85 |
| CTO subagents: independent-auditor | 9 | 0.06 | 33 | 2.1% | 1.8 | 507 | 100% | 112 |
| operator | 7 | 0.06 | 31 | 1.9% | 1.4 | 249 | 100% | 232 |
| CTO main tree (fresh CTO, today) | 1 | 0.04 | 12 | 0.8% | 0.6 | 147 | 100% | 238 |
| CTO subagents: research | 1 | 0.01 | 3 | 0.2% | 0.1 | 52 | 100% | 106 |
| other (live tests, rehearsals, probes) | 114 | 0.00 | 2 | 0.1% | 0.2 | 171 | 37% | 30 |
| sentinel/watchers | 1 | 0.01 | 1 | 0.0% | 0.1 | 114 | 0% | 114 |
| other | 59 | 0.00 | 0 | 0.0% | 0.1 | 0 | 0% | - |
| **total** | 470 | 4.16 | 1616 | 100% | 87.4 | 17201 | | |

Notes. "Median ctx" is the median over sessions of each session's median context size (input, cache write and cache read) per call. The `fork` type inherits the CTO's whole context at start (first call median 578k tokens, range 108k to 953k); `general-purpose` helpers start at 34k to 41k. Source: `*.meta.json` agentType; the first user message of each worktree session (role from "You are a fresh …"); `log/spend.jsonl` for launched workers (77 of 304 non-subagent sessions); role defaults in `template/governance/kernel/roles/*.md`.

Compared with P1's month (CTO main 31 %, CTO subagents 23 %, leads 15 %, test designers 13 %, engineers 7 %): the CTO's main session fell to 20.5 %, its subagents rose to 43 %, leads fell to 9 %, and test designers and engineers together fell from 20 % to 8 %.

## Table 3: by activity

P1's five categories plus (f), the emergency's own work: the retros (P1 to P5, the short list), the permissions audit, the rubric research, the context pack, the handover, the switch-off job, and the audits running now. Everything is USD at CLI rates.

| category | tokens (B) | output (M) | USD | share of USD | active h |
|---|---|---|---|---|---|
| (a) Gov OS product development (engineers, test designers, CTO edits to src/tests/template) | 0.19 | 1.5 | 78 | 4.8% | 7 |
| (b) coordination (leads, dispatch, briefs, waits, status, operator) | 1.27 | 3.4 | 497 | 30.8% | 27 |
| (c) ceremony candidates (reviews, ACT bundles, register, packages) | 0.61 | 2.4 | 246 | 15.2% | 11 |
| (d) security work (guard, sandbox, box, walls, permissions) | 1.09 | 3.2 | 409 | 25.3% | 22 |
| (e) product work (EXAMIN, W2-81 proving run) | 0.77 | 3.3 | 290 | 18.0% | 16 |
| (f) the emergency's own work (retros, audits, switch-off, strategy) | 0.23 | 1.4 | 96 | 5.9% | 4 |
| **total** | 4.16 | 15.2 | 1616 | 100% | 87 |

Who spent each category, USD (CTO main tree and its subagents are 64 % of the total):

| role | (a) | (b) | (c) | (d) | (e) | (f) | total |
|---|---|---|---|---|---|---|---|
| CTO subagents: fork | - | 216 | 52 | 199 | 6 | 12 | 484 |
| CTO main tree (retiring CTO) | - | 120 | 91 | 58 | 42 | 8 | 320 |
| CTO subagents: general-purpose | - | 22 | 73 | 50 | - | 38 | 182 |
| adopters (W2-81 runs) | - | - | - | - | 175 | - | 175 |
| ticket leads | - | 101 | - | 39 | 3 | - | 143 |
| engineers | 47 | - | - | 34 | - | - | 81 |
| product CTO (EXAMIN) | - | - | - | - | 59 | - | 59 |
| test designers | 31 | - | - | 16 | 4 | - | 51 |
| reviewers/auditors | - | - | 30 | 7 | 1 | - | 38 |
| CTO subagents: independent-auditor | - | - | - | 3 | - | 31 | 33 |
| operator | - | 31 | - | - | - | - | 31 |
| CTO main tree (fresh CTO) | - | 7 | 1 | 1 | - | 3 | 12 |
| CTO subagents: research | - | - | - | - | - | 3 | 3 |
| other (live tests, rehearsals, probes) | - | - | - | 2 | - | - | 2 |

Ceremony (c) is made of: review rounds and audits $102, ACT bundles and jobs $86, packages and register $36, checkpoints and restarts $6, other $15. Security (d) and the ACT bundles overlap in kind: most of the ACT bundles are guard fixes.

**The same money against EMERGENCY-2's lists.** This view is mine, not P1's. A ticket's sessions are assigned by the ticket (W2-111, W2-186, W2-56 are guard or sandbox tickets that E2 retires; W2-88, 189, 190, 191, 192, 195, 156, 174, 153, 15a, 138, 145, 155, 60b are on the build and finish list; W2-81 and W2-94 are the proving run and EXAMIN). The CTO's subagents are assigned by their description. The CTO's own main-session messages are assigned by keyword and by what woke the turn, so that line is the least exact (about ±15 %).

| where it went, against EMERGENCY-2 | tokens (B) | USD | share |
|---|---|---|---|
| retired by E2 (guard, sandbox, box, permissions, ACTs) | 1.49 | 635 | 39.3% |
| proving run and EXAMIN | 0.70 | 275 | 17.0% |
| on E2 build/finish list | 0.58 | 241 | 14.9% |
| coordination and other CTO helper work | 0.42 | 139 | 8.6% |
| watching: inbox waiter and idle-check wake-ups | 0.47 | 138 | 8.5% |
| decisions, packages, reviews of other work | 0.27 | 92 | 5.7% |
| emergency work (retros, audits, switch-off, strategy) | 0.23 | 96 | 5.9% |

What each line is made of: "retired" is $393 forks, $95 general-purpose helpers, $46 CTO main-session messages, $39 leads, $34 engineers, $16 test designers, $7 reviewers. "Build and finish list" is $101 leads, $47 engineers, $31 test designers, $30 reviewers, $27 forks. "Watching" is only the CTO's main session. "Proving run and EXAMIN" is $175 adopters (0.1.0 run $108, 0.1.1 re-run $67), $59 EXAMIN CTO, $27 CTO main-session messages.

**What woke the CTO's main session.** For the retiring CTO's main session (2,081 calls, $320; the fresh CTO's session is $12), I attributed every call to the record that started its turn:

| what started the turn | turns | calls | USD | share of the session | USD per turn |
|---|---|---|---|---|---|
| inbox waiter finished (background command) | 131 | 652 | 116 | 36.5 % | 0.89 |
| the owner's message | 57 | 480 | 75 | 23.5 % | 1.32 |
| a subagent finished or is waiting | 87 | 285 | 45 | 14.0 % | 0.51 |
| another background command finished | 35 | 222 | 25 | 7.7 % | 0.70 |
| Stop hook (idle check) | 106 | 158 | 23 | 7.3 % | 0.22 |
| cross-session message (leads, operator) | 31 | 106 | 19 | 6.0 % | 0.62 |
| scheduled digest, package, release prompt | 10 | 67 | 9 | 2.8 % | 0.88 |
| compaction continuation | 3 | 111 | 7 | 2.3 % | 2.44 |

Machine-woken turns were 76 % of the session. Of the 131 waiter turns, 70 ($49) did only bookkeeping (move the inbox file, list, re-arm the waiter) and 61 ($68) spawned, wrote, committed, tested or launched something. Of the 106 idle-check turns, 101 ($19) were bookkeeping only. Bookkeeping-only wake-ups cost $68, 4.2 % of the window. Source: `acd80751-….jsonl` records with `<task-notification>` summaries, `Stop hook feedback: Idle check (ACT-IDLE-GUARD-1 …)`, and `origin` kinds.

**Owner messages.** 58 to the retiring CTO in the window (17 on 11-15, 40 on 11-16, 1 on 11-17; 29 a day against P1's 18), 22 of them relays of a job the owner ran and 6 yes lines; 38 more to the operator session and 13 to EXAMIN and adopter runs. E2 §10.2's weekly measures for this window: product share 18.0 % (baseline 4 % and 13 %), governance share (b) plus (c) 46.0 % (baseline 56 %), security 25.3 % (month 19 %).

## Table 4: by model

| model | tokens (B) | share of tokens | USD | share of USD | assistant messages |
|---|---|---|---|---|---|
| Opus (5.5; 2 helper sessions ran `claude-opus-4-8`, priced as 5.5) | 3.88 | 93.3% | 1541 | 95.4% | 15318 |
| Sonnet 5.5 | 0.26 | 6.3% | 73 | 4.5% | 1635 |
| Haiku (5.5; 4.5 in the live-test probes) | 0.02 | 0.4% | 1 | 0.0% | 244 |
| Fable | 0 | 0% | 0 | 0% | 0 |

Source: the `message.model` field. The two `opus-4-8` messages are in "Fresh review of runner round 5" and "round 7"; the Haiku 4.5 sessions are pytest's live-test probes (they ran again on 11-17). I priced both as the 5.5 models; the amounts are about $4.5 and under $0.2.

Which role ran on which model (USD):

| role | Opus USD | Sonnet USD | Sonnet share |
|---|---|---|---|
| CTO subagents: fork | 484 | 0 | 0% |
| CTO main tree | 332 | 0 | 0% |
| CTO subagents: general-purpose | 152 | 30 | 17% |
| adopters (W2-81 runs) | 174 | 1 | 1% |
| ticket leads | 143 | 0 | 0% |
| engineers | 65 | 16 | 20% |
| product CTO (EXAMIN) | 58 | 1 | 2% |
| test designers | 27 | 24 | 47% |
| reviewers/auditors | 38 | 0 | 0% |
| CTO subagents: independent-auditor | 33 | 0 | 0% |
| operator | 31 | 0 | 0% |
| CTO subagents: research | 3 | 0 | 0% |

**Did it fit "Sonnet where it is enough, Opus where it matters"?** DEC-1120 (2) sets: leads, senior engineers, auditors Opus; engineers Sonnet (C3 Opus); test designers Sonnet except C3; reviewers C3 Opus, C2 Opus only on FULL, else Sonnet; "product-spec, research, ACT preparers and other helpers" Sonnet; "the operator agent" Sonnet; watchers Haiku. Against that:

- **Fits:** leads and auditors on Opus; the sentinel on Haiku; test designers 47 % Sonnet; engineers 20 % Sonnet.
- **Does not fit:**
  - The CTO's helpers. `~/.claude/settings.json:3` sets `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5`, so a spawn that names no model gets Opus. Of the CTO's 93 spawns, 5 named Sonnet, 19 named Opus, 35 were `fork` (inherits the CTO's Opus) and 34 named nothing. The "research" helper (a Sonnet role) ran on Opus.
  - C2 launches. In `log/spend.jsonl`, 27 of 66 C2 engineer and test designer launches ran on Opus ($48 recorded: 14 of 30 engineers, 13 of 36 test designers). DEC-1120 (4) kept C2 engineers on Opus only "through D-10". The 25 C2 auditor launches all ran on Opus ($38); that fits only where the ticket is FULL, and the spend log does not record the profile.
  - The operator session ran Opus throughout ($31); DEC-1120 (2) says Sonnet.
- **Opus that matters, correctly placed:** the CTO main session, the C3 workers (11 C3 engineer launches $74, 14 C3 test designer launches $33), the audits.

## Table 5: the plan limit over the two days

From `usage.txt` ("week (all models)"). It stopped at 11-17 03:03 when the watchers went off; two lines were added at 22:23, and I used them. Fable stays at 0 % throughout.

| period (UTC) | USD (transcripts) | plan % at start, at end | points | requests in the last 24 h at the end (sessions) |
|---|---|---|---|---|
| 11-15 00:00 to 08:59 (old week) | 66 | 80, 86 | +6 | 8,809 at 09:07 (163) |
| 11-15 09:00 to 24:00 (new week) | 212 | 0, 12 | +12 | 5,272 at 00:09 (121) |
| 11-16, 24 h | 1,254 | 12, 63 | +51 | 12,746 at 23:58 (212); peak 14,742 at 18:11 |
| 11-17 00:00 to 03:03 | 7 | 63, 63 | 0 | 9,495 at 03:03 (148) |
| 11-17 03:03 to 22:23 | 64 | 63, 65 | +2 | 952 at 22:23 (17) |

- The previous week reached 97 % (usage.txt; P1 gives 100 % and 97 % for the two weeks before). The current week is at 65 % after 61.4 of 168 hours: 1.8 times the pace that would end exactly at the reset.
- At the two-day average (1.06 points an hour) the week would run out on about 11-19 07:40 UTC, 3 days before the 11-22 09:00 reset. At 11-16's pace (2.1 an hour) it would run out in 16 hours.
- The two peaks: 11-16 00:00 to 02:00 ($280, 17 % of the window: the operator job runner, ACT-DEADMAN-INBOX-1 and the (O) change, with their reviews, and the 0.1.0 adopter runs, 22:46 to 01:41) and 15:00 to 18:00 ($436, 27 %: the P-JOBS-USER-1 session sandbox fork ($90 over 12:17 to 17:21), ACT-BOX-LAUNCH-1, the 0.1.1 adopter re-run, the leads of W2-111, W2-60b and others, and the retros starting at 17:04).
- The 22 hours before the owner's stop (11-16 21:57) cost $1,236, $56 an hour. The 24 hours after it, until the fresh CTO started at 21:54, cost $32, $1.3 an hour. The fresh CTO's first 40 minutes, with 18 audit and triage helpers, cost $70.

## Why: three mechanisms the tables show

1. **Context is the bill.** Cache reads are 49 % of the USD, cache writes 34 %, output 17 %, new input under 1 %. The CTO main session pays 69 % in cache reads; forks 47 % reads plus 42 % writes.

| context at the message | messages | share of messages | USD | share of USD |
|---|---|---|---|---|
| <50k | 1171 | 7% | 63 | 4% |
| 50-150k | 7238 | 42% | 396 | 25% |
| 150-300k | 4446 | 26% | 319 | 20% |
| 300-600k | 2540 | 15% | 351 | 22% |
| >600k | 1806 | 10% | 486 | 30% |

   The 4,346 messages above 300k tokens (25 % of the messages) cost $838, 52 % of the window. Only three kinds of session ever reached that size: forks (795 messages above 600k, $268), the CTO's main session (912 messages above 600k, $203) and the EXAMIN CTO (82, $14). Leads, workers, reviewers and adopters never passed 600k and rarely 300k (median 80k to 120k).
2. **A fork re-reads the CTO's whole context on every call.** 35 forks, $484, median $4.48 each against $2.47 for a `general-purpose` helper; the first call of a fork costs about $0.2 on average, so the price is paid on every later call, at cache-read rates. Re-reading the inherited part alone (start context minus 36k, at $0.20 per million, calls after the first) is a lower bound of $163, 10.2 % of the window. 16 of the 35 forks built ACT, sandbox or job-runner machinery, which a written brief and a fresh engineer could have done: the CTO's own spawn prompts for forks have a median of 3.4k characters.
3. **The CTO's session was driven by machines.** See the trigger table: 76 % of its calls started with something other than the owner. The loop (waiter finishes, CTO moves the file, re-arms the waiter) cost $0.89 per wake, and the idle-check Stop hook woke it 106 times.

Also: the job-runner family (a fork build, the (O) change and ten fresh independent reviews) cost $166. DEC-1204 allows at most two review rounds. Brief size is not a driver: the median brief is 4k tokens for a lead and 5k for an engineer (maxima 20k), against contexts of 100k to 300k, so I propose no change there.

Memory use in the window (counts of Bash commands containing the words; an upper bound, since a command may only mention them): `gov retrieve` 102, `gov brief` 183, `gov context` 117 (now switched off), against 6,320 `grep` or `rg` commands. By role: CTO main 11 retrieves and 771 greps; forks 10 and 1,216; general-purpose helpers 33 and 1,068; adopters 25 and 926; leads 7 and 791; engineers 2 and 470; the EXAMIN CTO 0 and 158. Source: `mem.py` over the transcripts.

## What to change, ranked

"Share freed" is the share of this window's USD (the window's $1,616), estimated as the amount spent on the thing, less what remains afterwards. Where two changes overlap, the second is given net of the first. Estimates say how they were made.

| # | change | concrete step | share freed | evidence (source) | who decides |
|---|---|---|---|---|---|
| 1 | Stay off the machinery EMERGENCY-2 retires | No new work on the guard, sandbox, box, permissions, ACTs, the operator job runner or re-pin ACTs. Close W2-111, W2-186 and W2-56 on their records. Update or retire the 29 reds with what they assert. | **up to 39.3 %** ($635) | Table 3, "against E2": 16 forks $398, general-purpose helpers $95, W2-111/186/56 trees $97 (W2-111 alone $74); the job-runner family $166; EMERGENCY-2 §2.2, §2.10, §6.1; the owner's stop at 11-16 21:57 | CTO (already ordered) |
| 2 | Models by DEC-1120's table, by default | (a) C2 engineer and test designer launches on Sonnet (27 of 66 ran Opus). (b) Remove or change the helper default so a spawn without a model runs Sonnet, and name Opus on the spawn that needs it. (c) The operator session on Sonnet. | **about 3 to 4 %**: (a) 1.0 to 1.5 % on $48, (b) 1.5 to 2.2 % on $71 of non-retired Opus helper spend, (c) 0.7 to 1.0 % on $31 | `log/spend.jsonl` C2 launches ($48 recorded); `~/.claude/settings.json:3`; 93 spawns; DEC-1120 (2) (4); estimate: Sonnet costs exactly half per token (rates above), and USAGE-RUBRIC-2 §6 says no Sonnet-to-Opus token ratio is measured, so I use a 35 to 50 % saving (0 to 30 % more tokens) | (a) CTO; (b) and (c) owner (his settings, his session) |
| 3 | Wake the CTO by files and one daily digest, not by watchers | Drop the inbox waiter and the idle-check Stop hook now; the CTO reads its inbox at its own pace; one digest line a day (A-2, RT-2, RT-7). | **4.2 % firm** ($68: 171 turns that only moved a file or re-armed); **up to 8.5 %** ($138) if the other wake turns are batched | Table 3, trigger table; `trig4.py` (turns with and without spawn, write, commit, test or launch) | CTO (A-2 approved) |
| 4 | No `fork` for helper work | A helper is a fresh `general-purpose` or role session from a written brief, on the model the rubric names. A fork only for a question that needs the CTO's whole context. | **3.2 % net** ($52 of non-retired forks); 10.2 % gross ($163, of which 7 % overlaps item 1) | 35 forks, median start 578k; 795 calls above 600k cost $268; $4.48 against $2.47 per session; briefs are already 3.4k characters | CTO |
| 5 | Review only red work, two rounds at most | EMERGENCY-2 §3.4 and §3.6: no reviewer for green; one batched review after the nightly. | **3.1 % net** ($50 of review rounds outside item 1; gross $102, 6.3 %) | 36 CTO review helpers $112, 20 worktree reviewers $38; ten rounds on one runner bundle; DEC-1204 two rounds | CTO |
| 6 | Leads on Sonnet for LITE and STANDARD tickets, as a DEC-1120 (3) trial | Two tickets, judged by an Opus reviewer; C3 and FULL stay Opus. Under E2's deterministic landing the lead's job shrinks further. | **2.2 to 3.2 %** (35 to 50 % of $104 of non-retired lead spend) | Leads are 100 % Opus, $143 (more than engineers and test designers together, $132); all 31 leads' median context 111k; DEC-1120 (2) puts leads on Opus, so this needs the owner | owner (changes his rubric) |
| 7 | Cap the CTO's context (checkpoint and memory-first instead of the full window) | Compact the CTO's main session near 300k with the checkpoint hooks that E2 §6.1 keeps. | **2.8 % net** (7.5 % gross: read cost above 300k is $109 in the CTO main session, $12 in the EXAMIN CTO) | Table in "Why"; the owner's own trial, DEC-1183 (4): it saved about 7 % of a day and was ended because lessons were lost across compactions; E2 §6.1 keeps "full window" | owner |
| 8 | Check the 5-minute cache for launched workers | Verify the setting on this CLI (DEC-1118 (2) D), then apply it to engineers, test designers and reviewers. | **up to 1.3 %** ($21: 37.5 % off the write price of the workers' $57 of cache writes) | All 24.7M cache-write tokens in the 158 headless logs are the 1-hour tier; the 5-minute tier at 1.25 times input against 2 times is the standard price structure and is not verified on this CLI | CTO (verify first) |
| 9 | Fewer decisions, packages and register entries | E2 §10.1: a basis line for every new rule, checked by code. | not estimated; the line holds $92 (5.7 %), about half of it in the CTO's own main session | Table 3, "decisions, packages, reviews of other work" | CTO |
| 10 | One plan reading an hour, no model | Restore the usage reading as one cron line in the run-time tool and set a daily budget (about 35 points, $185 a day, for the rest of the week). | none (protects the rest) | `usage.txt` is the only measure of the plan; it stopped at 03:03, and the week went from 63 to 65 % unobserved | CTO |

**What the stack frees.** Items 1 to 6 together: 39.3 + 4.2 + 3.2 + 3.1 + (3 to 4) + (2.2 to 3.2) = about 55 to 57 % of this window's USD. With item 7, about 58 to 60 %. The same work would then cost about $690 to $730, or 28 to 29 plan points, in place of 65. This is an estimate: the changes are summed net of overlap, the CTO main session's share of item 1 is by keyword, and the Sonnet savings assume the same tokens for half the price (a 35 to 50 % band).

**Not a lever:** brief size (median 4k to 5k tokens against contexts of 100k to 300k); the lead, worker and reviewer sessions' own compaction (none reached 600k).

## Where the freed capacity should go

The build list is EMERGENCY-2 §6.1 and §6.2, and EXAMIN's memory is §7. In this window they got 15 % (the build list's tickets) plus 17 % (proving run and EXAMIN's Wave 0), and no session built or measured EXAMIN's memory (the EXAMIN CTO made 0 `gov retrieve` calls; its Wave 0 ran adopt stages and a file audit). A sizing for the 35 points left (about $830), for the CTO to adjust:

| use | proposed points | basis |
|---|---|---|
| The first build: `gov launch` without the guard and the sandbox, release 0.1.2 (E2 §6.1, "build first"), then W2-17, W2-18, W2-36, W2-115b, W2-192, W2-193, W2-194, W2-195 | 12 to 14 | engineers and test designers at the rubric's models; the window's engineers plus test designers cost $132 in all |
| The run-time tool (W2-121c and d, messages, RT-1 to RT-8) and memory by construction (5.4) with the memory-use log | 7 to 9 | one engineer and one test designer per item; no leads for LITE tickets |
| Two fresh-80 measures (Gov OS, EXAMIN) | 8 | about 4.0 points each, USAGE-RUBRIC-2 §2 ($109 each); a first one decides W2-15b |
| The release's proving run (six synthetic repositories) | 3 to 5 | measured: 0.1.0 run $108, 0.1.1 re-run $67 on Opus |
| EXAMIN Wave 0 steps 3 to 6 and its memory after the release | the rest | E2 §7 |

These come to 30 to 36 of the 35 points left, so EXAMIN's later steps wait for next week's allowance unless the ranked changes hold. Coordination and review should sit under 15 % of what is spent (this window: 46 %).

## What could not be measured, and how big the unknown is

1. **The window is open.** Today's audits and the fresh CTO's session are still running (about $84 on 11-17 so far). The totals will rise by a few dollars.
2. **A fresh-80 measure has not run** in the window (JOB-15 has no figure, JOB-17 is queued), so about 4 points that the next one costs are not here.
3. **Cross-file duplicates**: 35 messages (about 20M tokens, 0.5 %) appear in two files; I counted both.
4. **Classification error.** The CTO main session's messages are classed by keyword (about 15 % of messages move between coordination and ceremony; P1's sample). The "against E2" line for the CTO's main session is the least exact. Subagents and tickets are classed by their own description.
5. **The Sonnet token ratio** (how many more tokens Sonnet needs for the same task) has no measurement here or in USAGE-RUBRIC-2; items 2 and 6 and the stack's range rest on a 0 to 30 % band.
6. **Active hours** are summed over concurrent sessions (87 h in 62.6 h of wall time); wall time per session is not additive.
7. **Opus 4.8 and Haiku 4.5** rates are assumed equal to the 5.5 models.
8. **The meter's per-model weights** are not published; the $23.6 a point holds within about ±2 points across 81 readings only because the window is 95 % Opus.
9. **Owner time** (reading, terminal work outside Claude Code) is not measured; only messages are counted.

## Decisions for the owner

1. **Cap the CTO's main-session context?** (a) Keep the full window (DEC-838, E2 §6.1). (b) Compact near 300k with the checkpoint and memory-first lines. (c) A fresh CTO session each morning (DEC-1140 (4), earlier). Cost: (a) none; (b) frees 2.8 % net (7.5 % gross), but your own trial (DEC-1183 (4)) lost lessons across compactions; (c) similar saving, one restart a day. **Recommend (a)** for now; revisit once memory-first is built into every brief (5.4), because that is what makes a shorter context safe.
2. **The helper default model in `~/.claude/settings.json`** (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5`, line 3). (a) Set it to Sonnet; the CTO names Opus on the spawns that need it. (b) Remove the line and make each spawn name its model (DEC-1120 (3)). (c) Keep. Cost: (a) frees about 1.5 to 2.2 % with a risk of a helper that needed Opus getting Sonnet; (b) the same, with one more argument per spawn; (c) none. **Recommend (a)**.
3. **Your operator session on Sonnet?** It ran Opus ($31); DEC-1120 (2) says Sonnet for the operator agent. (a) Sonnet. (b) Keep Opus. Cost: (a) frees 0.7 to 1.0 % and a Sonnet operator may need clearer commands. **Recommend (a)**.
4. **Leads on Sonnet for LITE and STANDARD tickets as a trial** (DEC-1120 (3); your rubric says Opus). (a) Keep Opus. (b) Trial on two tickets, an Opus reviewer judging. (c) Sonnet for all leads. Cost: (b) frees 2.2 to 3.2 % if it passes and costs two tickets' extra review if it does not; (c) frees the same without the check. **Recommend (b)**.
5. **The release's proving run** (six synthetic repositories, E2 §8.2): which model? Today's adopters ran Opus (99 %; $108 for 0.1.0, $67 for the 0.1.1 re-run). (a) Opus once, at release acceptance (about $70 to $110, 3 to 5 points). (b) Sonnet for trial runs, Opus once at acceptance. (c) Sonnet throughout. Cost: (b) saves about $25 to $55 a trial run; (c) proves the flow only for Sonnet users. **Recommend (b)**.

## The CTO decides

Each is under EMERGENCY-2 §3.5, §4.2 or §4.6 or the CTO's practice. Recommendation in each line.

- **Item 1: stay off the retired machinery** and close W2-111, W2-186, W2-56 on their records. Recommend yes; it is the largest line (39 %).
- **Item 3: no waiter, no idle-check Stop hook; files and a daily digest.** Recommend yes, now (A-2 is approved); do not wait for the run-time tool.
- **Item 4: no `fork` for helper work.** Recommend a standing rule in the CTO's template: a fresh helper from a written brief; a fork only when the question needs the CTO's whole context.
- **Item 5: review only red work, two rounds at most.** Recommend yes (E2 §3.4, §3.6).
- **Item 2 (a): C2 launches on Sonnet** through the rubric (RT-8: the launcher states and picks the model). Recommend yes, with DEC-1120 (3)'s promotion to Opus after two failed reviews.
- **Item 8: check the 5-minute cache** on a one-off launch before applying it; apply to worker roles only (a lead that waits on a long test run would pay a full rewrite after five idle minutes). Recommend check first.
- **Item 10: restore one plan reading an hour and a daily budget**, and reserve points for the two fresh-80 measures and the proving run before spending on anything else. Recommend yes.
- **Item 9: a basis line for every new rule** (A-8) and no new register entry for work the landing already records. Recommend yes.
