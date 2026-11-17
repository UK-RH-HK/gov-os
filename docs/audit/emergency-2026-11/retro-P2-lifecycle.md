---
milestone: retro-2026-11 part 2 (ticket lifecycle, 2026-10-16 to 2026-11-16)
commit: 4416b8403a386da14cd2a9f7a631846e4a8e2a1b
pack_sha256: none (no context pack; the brief was the CTO's task message)
task: retro-2026-11-P2
decisions: [DEC-1047, DEC-1204, DEC-953, DEC-1010, DEC-1157, DEC-413, DEC-1203]
---
# P2: the ticket lifecycle, by profile (LITE, STANDARD, FULL), with exa-g6db as the worked example

task: retro-2026-11-P2 · status: DONE (the report sits in the auditor's scratch, not drafts/: see "Refusal") · work_completed: 141 worked tickets measured, the step list costed, exa-g6db traced minute by minute · files_changed: none in any tree · evidence: the scripts and outputs in this folder (`perticket.csv`, `*.py`, `*.json`) · tests: none run (nothing reproduced) · discoveries: below · risks: data gaps listed under "Method" · lessons: below · proposed_decisions: none (the candidates are for the owner) · unresolved: per-ticket CTO cost cannot be attributed · recommended_next_action: the combining auditor reads the tables and the "Steps" section.

**Refusal (one, not retried):** `mkdir` of `.gov-runtime/scratch/orchestrator/drafts/retro-2026-11/` was refused by the live hook ("a reviewer or auditor writes only its own review or audit record … its own scratch, or /tmp", DEC-953 item 2). This report is therefore at
`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/acd80751-ac8f-4230-9bae-15c678a54895/scratchpad/retro-p2/P2-lifecycle.md`; the CTO can copy it to the named path.

## Method and limits
- **Population.** 181 tickets have their last move to `closed` inside the window (from the `status:` history of each `.tickets/*.md` on w2/integrate). 40 of those were never claimed: retired, withdrawn or moved to Wave 3 by D9 fates (11-06) or DEC-954 (10-30). They are left out. **141 worked tickets** remain: 19 LITE, 72 STANDARD, 50 FULL. 93 of them closed in their own loop; 48 were "closed at the lift" by DEC-953's practices (DEC-1132 (1)), often days after their merge.
- **Time.** Claim is the first `in_progress`. Close is the last `closed`. Merge is the first "Merge w2/<W2>" on the first-parent line of w2/integrate. The emergency freeze (11-03 to 11-08) and the lift's batch closes stretch the wall times of the tickets they cover.
- **Cost.** Each lead run's `total_cost_usd`, from 404 lead-run results in `.gov-runtime/scratch/orchestrator/log/` in the window. Each worker's cost, from 803 worker results found in the worktrees, the archive and the `W2-00-record` worktree (td-, en-, rev/rv/au/nc-, ps-). Worker results were found for 111 of the 141 tickets. All figures are list-price API cost. The CTO's interactive sessions are estimated from their transcripts at the rates fitted to the lead results (input $4, output $20, cache read $0.20, cache write $8 per million tokens). That estimate cannot be split by ticket.
- **Refusals.** Counted from each lead return's text: LAUNCH_REFUSED or LAUNCH_BLOCKED, CLOSE REFUSED, gate refusals, and guard refusals the return names. The SDK `permission_denials` are added. Counting guard refusals by the word is an upper bound.
- **Review catches.** A reviewer run counts as a catch when its own verdict marks a finding in scope, "Ordinary work: yes" and "fails open" or "loses work". These are the reviewer's labels before moderation (DEC-1010 / DEC-1204 (3)), so they overstate. Spot-checked examples are given below.
- Per-ticket rows: `perticket.csv` in this folder.

## 1. The per-profile table (141 worked tickets)

| | LITE (n=19) | STANDARD (n=72) | FULL (n=50) |
|---|---|---|---|
| claim to merge, median days [p25, p75] | 0.25 [0.16, 0.60] | 0.58 [0.29, 1.58] | 0.87 [0.37, 2.32] |
| claim to close, median days (all) [p75, max] | 1.51 [4.26, 10.3] | 3.85 [8.0, 26.1] | 3.21 [9.4, 25.9] |
| claim to close, own-loop closes only | 0.65 (n=12) | 0.59 (n=37) | 3.05 (n=29) |
| claim to close, closed at the lift | 1.75 (n=5) | 6.61 (n=27) | 4.25 (n=16) |
| lead runs per ticket, median [max] | 1 [4] | 2 [9] | 4 [15] |
| lead cost, median $ [p75, max] | 3.86 [5.50, 13.4] | 10.44 [14.7, 39.3] | 16.70 [28.7, 90.6] |
| lead + workers, median $ (tickets with both) [p75, max] | 6.71 [14.7, 21.5] (n=12) | 18.88 [27.0, 105] (n=55) | 51.19 [64.1, 202] (n=44) |
| review rounds per ticket, median [p75, max]; tickets with >2 | 0 [0, 2]; 0 | 1 [2, 6]; 11 | 2 [4, 13]; 22 |
| lead runs ending PACKAGES (a relay to the CTO or the owner) | 8 of 23 (35 %) | 75 of 172 (44 %) | 95 of 206 (46 %) |
| refusals per ticket, median [p75, max]; tickets with any | 0 [2, 7]; 8 | 1 [4, 17]; 40 | 3 [8, 23]; 41 |
| of which launch refused or blocked / gate / guard named / SDK denials / close refused | 3 / 1 / 13 / 16 / 0 | 17 / 11 / 55 / 90 / 1 | 24 / 15 / 83 / 142 / 1 |
| reopened tickets (events) | 0 | 6 (11) | 10 (18) |
| CTO commits on integrate naming the ticket, median | 6 | 8 | 11 |
| tickets with path cases (CTO, DEC-1156 (7)) | 2 | 5 | 10 |

Reading:
- The **work itself is fast at every profile.** Claim to merge has a median under one day. Most of the claim-to-close time sits after the merge: waiting for the lift or a batch close, reopening for scope added after the close, and operator runs.
- **LITE in Gov OS is mostly test revisions** (14 of 19, class `test-revision`). There is one lead run, usually no separate engineer, and no review.
- Two tickets show the profile and the class do not match: W2-67 (FULL, test-revision, $160) and W2-81 (FULL, test-design, $127).

## 2. Where the month's money and time went (all roles, the window)

| layer | runs | cost $ (list) | share | hours |
|---|---|---|---|---|
| CTO interactive sessions (estimate; not attributable per ticket) | 28,631 messages | ~3,860 | ~46 % | — |
| ticket leads | 404 | 1,927 | 23 % | sum of lead run durations: FULL 426 h, STANDARD 341 h, LITE 40 h (tickets with worker data) |
| independent test designers | 253 | 928 | 11 % | 71 h |
| reviewers (probe, auditor, narrow check, QA) | 208 | 781 | 9 % | 53 h |
| engineers | 286 | 697 | 8 % | 94 h |
| product-spec (CIT-P and similar) and research | 56 | 67 | <1 % | 5 h |

- **Coordination costs more than the work.** The CTO and the leads together are about 70 % of spend. The builders are 8 %.
- Across FULL tickets, the lead sessions ran 426 h while all their workers ran 149 h. A lead spends about two thirds of its time verifying, merging, waiting on gates and slots, and writing packages.
- Per profile, over tickets with both kinds of record, the lead's share of cost is LITE 62 %, STANDARD 54 %, FULL 38 %.

## 3. The steps: share, catches, and the golden-rule judgement

Shares are of the month's ticket cost (leads plus workers). "Catch" means a defect an honest agent made in ordinary work that would have failed open or lost work.

| step | share / time | what it caught in the month | judgement |
|---|---|---|---|
| claim (`tk start`, interface at claim, DEC-1157) | ~0; one commit | nothing to catch. It is the traffic record DEC-1047 asks for | **earns** (cheap traffic control) |
| brief (`gov context` / `gov brief`, then filled by hand) | inside the lead's 23 %. EXAMIN: 9 unfilled slots per brief (F-014) | 19 recorded brief gaps (10-30 on). CONTEXT_OVER_CEILING and "DEC-n not found" blocks forced briefs by hand (memory notes, 11-15) | **simplify**: the brief should come out whole; slot-filling by hand is ceremony |
| independent test designer | 11 % of cost; 0.28 h per run | It is the oracle every later step depends on. FULL engineers needed a median of 3 runs to get the TD's tests green. exa-g6db's F1 guard proved that a loose fix fails 16 cases | **earns**: the separated role DEC-1047 names |
| engineer | 8 %; 0.33 h per run | (the product) | — |
| `gov accept` | seconds | red on the base, then green, every time | **earns** (cheapest real check) |
| `lead_verify` (full suite on the ticket branch) | 22 to 35 min per run (median 22.5, n=16 durations quoted); many runs per ticket | Of about 444 lines in returns: 144 green, 35 pre-existing, environment or load reds triaged, about 4 reds caused by the change (e.g. W2-185: 2 reds outside the widened paths) | **scope**: the landing re-runs the suite on the merged result. Keep the ticket's import-graph selection here and leave the full regression to the landing and the nightly |
| review / probe (FULL; some STANDARD) | 9 %; 0.15 to 0.21 h per run | FULL: 39 of 123 reviewer runs (32 %), and 20 of 41 tickets, had a reviewer-labelled blocking finding. STANDARD: 16 of 75 runs, 13 of 34 tickets. LITE: 0 of 4. Spot-checked as real and ordinary: W2-42a here-string fail-opens (reopened three times), W2-58 (grep through xargs reads the tests), W2-37 (CIT-E drift), W2-88 (a key after an empty `password:` missed), W2-101 (skilleval re-run) | **earns on FULL and on guard, gate or launch STANDARD work**; candidate to drop for STANDARD work off those surfaces |
| QA engineer (W2-60b, new) | too new | no data | — |
| land (merge queue) | 90 runs; 71 tickets closed | 11 ejections red and 1 conflict. Mostly governance-form tests: allowed paths F4/F5 (W2-157, W2-121b, W2-121, W2-179), probe-record form (W2-171, W2-60a), the path map (W2-40). One was cross-ticket (W2-121b reddened by W2-157's test). 25 runs had "no outcome (refused or stopped)" | **earns** as the only cross-ticket check, and allowed-path drift is in the threat model. The probe-record-form reds are ceremony |
| close (`tk close`, close record, scoped close) | Gov OS: small per ticket, but 48 of 141 waited for the lift (median 4 to 7 days after claim). EXAMIN: about 75 % of exa-g6db | Gov OS: none seen separately from the landing. exa-g6db: one real catch, a stale generated kit copy (7 reds), which EXAMIN's own suite also shows | **simplify**: close at the land (most already do). For adopted projects, compare against the base by default |
| reopen | 16 tickets, 29 events | Real fail-opens: W2-42a R3 to R5, W2-104 (W2-101 review F1). The rest is scope added after the close (W2-88 S27/S29, W2-94 S13 to S15, W2-111 S9/S10), nightly test revisions (W2-56, W2-60a, W2-178) and "kept open" for operator runs | **scope**: add new KPI lines as new tickets. Reopen only for a defect |
| PACKAGES relays | 180 of 404 lead runs (45 %) | Each stops a lead. A resume rereads its context (about $3 to $5 a run), and the CTO reads and answers | **biggest hidden cost**: DEC-1157's interface-at-claim removed one cause. Packages that only ask "may I" are the next to remove |
| ACTs for control paths | 95 distinct ACT ids in the window | GUARD-FIX 1 to 7 change the guard itself (the fail-open surface). CLAUDE-COPIES 1 to 12 copy generated files into `.claude/` from kernel files their ticket already reviewed. OPERATOR-HOURS and MORNING-SEQUENCE were scheduling | **earns** for the guard and hooks. **Ceremony** for regenerated copies (12 ACTs) |
| CIT-P (product-spec) | $57 in total, 52 runs | records the owner's approval of kernel text (CAP-33); no defect caught | **keep cheap**; not for LITE |

Golden-rule lines for the main judgements:
- **Test designer.** Ordinary work: yes, because an honest engineer who writes its own tests passes its own reading of the KPI. Consequence: fails open (without it, every gate after it checks nothing independent).
- **Review on FULL guard, gate or launch work.** Ordinary work: yes, because the spot-checked findings came from everyday inputs (heredocs, xargs grep, YAML slips). Consequence: fails open.
- **Review on STANDARD work off those surfaces.** Ordinary work: yes. Consequence: other (13 of 34 tickets had labelled catches, but the labels predate moderation, and none spot-checked lost work). Candidate to drop.
- **`lead_verify` before the landing.** Ordinary work: yes, because changes do break other suites. Consequence: other, since the landing catches the same red one step later. Candidate to scope.
- **Landing.** Ordinary work: yes, because allowed-path drift and cross-ticket reds happened 11 times. Consequence: fails open if removed (nothing else checks the merged whole).
- **ACT for regenerated `.claude/` copies.** Ordinary work: no defect possible beyond the reviewed source, because the copy is generated. Consequence: other. Ceremony.
- **Batch close at the lift, and reopening for new scope.** Ordinary work: yes. Consequence: other (it loses no work and opens nothing). Ceremony.

## 4. exa-g6db, EXAMIN's first LITE ticket (2026-11-16)
The change: `gen_index.py` reads a quoted outcome as the bare word (F-008). The engineer's fix was +7 −1 lines.

| time (UTC) | step | took | what happened | caught |
|---|---|---|---|---|
| 13:0x to 14:00 | ticket fields by the owner's operator (90d750e; `tk` cannot write them) | ~45 min wait | relay through the owner and the operator | — |
| 14:08 | readiness, `gov brief`, claim (bfec906), tests worktree | 1 min | readiness: SPECIFICATION_NOT_FOUND (F-026). The brief left 9 slots unfilled (F-014) | — |
| 14:09 | first launch of the test designer | — | LAUNCH_REFUSED: `--model` did not match the role. The CTO's own error, fixed at 666798b | an honest CTO error (the refusal was right) |
| 14:11 | test designer, run 1 | 73 s, $0.34 | all 4 writes refused: the session started in the clone, and `LAUNCH_TREE` is not a product variable (F-025) | product gap |
| 14:13 | Gov OS CTO reply | 2 min | route: launch from inside the worktree. F1 green on the base is right | — |
| 14:14 | test designer, run 2 | 83 s, $0.37 | 30 cases (7 red, 23 green by design). F1 proved that a loose fix fails 16 cases. 2 guard refusals (a heredoc, a scratch write) | prevented a loose fix |
| 14:15 to 14:16 | path map namespace and merge (0265079, f349bd3) | 1 min | — | — |
| 14:16 | `gov accept` | <1 s | ACCEPT_NO_TESTS: the ticket lacks `acceptance_tests.path` (F-027) | product gap |
| 14:16 to 14:42 | JOB-20261116-01 (Gov OS CTO writes it, the owner says run, the operator runs it, b17cd5a) | 26 min wait | relay | — |
| 14:42 to 14:44 | accept red, engineer, accept green | engineer 38 s, $0.23 | 30 of 30 green | — |
| 14:44 | `gov close` (scoped) | 67 s | RED_CAUSED, 140 reds | 7 real (the kit copy was not regenerated); about 133 from the harness (F-028) |
| 14:47 to 15:13 | legacy suite at HEAD and at the base; rehearsal; JOB-03 (the operator-queue write refused, F-029); owner line F-028 (a); the operator runs JOB-03 (b5da1fc) | 26 min | 2 relays, 1 owner decision | — |
| 15:14 | engineer, run 2 (regenerates the kit copy) | 38 s, $0.16 | d3148f4; legacy suite alone: 0 new reds | — |
| 15:3x | `gov close --base`, short hash, then full hash | 2.5 s, then 1:55 | BASE_UNKNOWN (F-030 b); RED_CAUSED, 111 `absent` reds counted as the change's although all are red at the base (F-030) | product gap |
| 15:45 to 15:59 | accepted_reds route, its correction, 153 entries drafted and rehearsed | 14 min | `close: scoped` never applies accepted_reds (F-031) | product gap |
| 16:3x | owner EXA-CLOSE (c) | — | W2-27's run closed; exa-g6db's close is a **named exception**, and the ticket stays in progress | — |

**Headline: 2 h 30 min and about $22 for a 7-line fix, and still no close.**
- **Time.** The ticket was created at 14:00 and the fix was green at 14:44. About 3 minutes of that was worker compute; 26 minutes was a relay to the owner's operator. The next 1 h 50 min went to the close and produced no close record.
- **Cost.** Workers cost $1.10 (2 test-designer runs, 2 engineer runs). The EXAMIN CTO cost about $20.8 by estimate, about $15 of it in the close phase. The Gov OS CTO's relays (5 replies, 1 correction, 2 jobs) cannot be priced.
- **Refusals and relays.** 12 refusals: 1 right and caught a real error; the rest were product gaps or guard false positives. 9 relays: 3 operator commits, 5 replies, 2 owner decisions.
- **Catches.** The independent test designer and `gov accept` did their job. The close caught one real drift (the stale kit copy).
- **What it bought.** The ticket's lasting value was as a product probe: seven findings (F-025 to F-031), and product tickets for F-028 and F-030.

Golden rule for the close step on an adopted legacy project: Ordinary work: yes, because every adopted repository has pre-existing reds and a shared-process harness. Consequence: other. The close fails closed, so it loses no work, but it blocks honest work for hours. The fix is product work (compare with the base by default, accepted_reds under `scoped`), not more ceremony.

## 5. Candidates for the owner (nothing lifted; each needs the owner's decision)
1. **Keep:** claim, the independent test designer, `gov accept`, the landing, review on FULL and on STANDARD work that touches the guard, gates or launch, and ACTs for guard and hook changes.
2. **Scope:**
   - `lead_verify`: the selection on the branch, the full suite once at the landing.
   - Review on STANDARD work off the guarded surfaces.
   - Reopen only for defects; new KPI lines become new tickets.
3. **Simplify:**
   - Briefs that come out whole.
   - Close at the land, with no batch close at a lift.
   - For adopted projects: compare against the base by default, and apply accepted_reds under `close: scoped`.
   - Ticket fields that `tk` cannot write, which forced 3 operator jobs on one LITE ticket.
4. **Lift (ceremony):**
   - ACTs for regenerated `.claude/` copies: the copy step should be part of the ticket's own landing.
   - Landing reds on probe-record form.
5. **Relays:** PACKAGES end 45 % of lead runs. Sort them into "the owner must decide" and "the lead may decide under a standing rule", and lift the second kind.

```verdict
{"kpis": [{"kpi": "P2-time-cost-rounds-refusals", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "P2-steps-earn-or-ceremony", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "P2-exa-g6db", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

Findings and their reversal tests:
- **F1:** coordination is about 70 % of spend and engineers 8 %. Reversed if the CTO transcripts turn out to hold headless lead runs or subagents counted twice; recount the per-session origin.
- **F2:** `lead_verify` duplicates the landing. Reversed if lead_verify caught change-caused reds the landing would have missed; check the 35 triaged reds and the 4 caused ones by hand.
- **F3:** review earns on FULL. Reversed if moderation (DEC-1010) downgraded most of the 39 labelled blocking findings to Wave 3 rows; check each ticket's moderated record.
- **F4:** exa-g6db's cost sat in the close. Reversed if the Gov OS CTO's relay time was larger than the EXAMIN CTO's; that needs per-message attribution of session acd80751.
