# Audit 4: the ticket disposition and the rubric, from the data

- **Date:** 2026-11-17 · **Commit:** `a246f72b2` (w2/integrate) · **Auditor:** fresh read-only session for the CTO (EMERGENCY-2 §9 row 4)
- **Sources read:** EMERGENCY-2.md (v3); HANDOVER.md §1, §6; `.tickets/*.md` (29 not closed); `docs/plan/WAVE_3_PARKING.md`; `docs/audit/emergency-2026-11/` retro-P2-lifecycle.md with retro-P2-perticket.csv, rubric-research.md (RR), context/provisional-rubric.md; DEC-1120, DEC-1159, DEC-1208, DEC-1209; `governance/project/criticality.yaml`; `packages/USAGE-RUBRIC-2.md`; git: each worktree's `log w2/integrate..HEAD`, the first-parent merges and non-merge commits of w2/integrate 2026-10-16..11-16.
- **Memory:** 2 retrieves. The first helped (DEC-1120's table and RUBRIC-2-APPLY in one bundle). The second gave the ticket bodies and DEC-1209 but nothing the files did not.
- **Per-item classification:** `docs/emergency-2/audits/04-classification.csv` (2,129 rows: 141 tickets, 1,988 direct commits; columns: class, rule, why, criticality, lines, cost, route then and now).

Rule codes used below: **4.1** a new capability with spec and KPIs; **4.6b** new KPI lines on an existing feature (a new ticket, so a feature); **4.2a** a known bug in an existing feature; **4.2b** a test wrong against the current spec or decision; **4.6r** records, evidence or data; **4.6k** kernel or instruction text (3.5: the CTO's call); **4.6c** configuration; **4.6t** tidy-up, tests unchanged and green.

## Table 1: each open, in-progress and Wave 3 ticket

### 1a. Tickets not closed (`.tickets/`, HANDOVER §1)

| Ticket | Status, step | Disposition | Why (E-2 §6, §4) | Left open | Source |
|---|---|---|---|---|---|
| W2-145 DAEO-2tfd | in_progress; merged | **decided: finish (A-4)** | built, merged | Worktree and tests worktree 0 commits ahead (`1be3e47de`, `aadce89d6`). Only the close is left. It waits for S7 (the re-pin plus a day), so it closes after the 0.1.2 re-pin. | HO:10; E-2:244 |
| W2-155 DAEO-ar89 | in_progress; merged | **decided: finish (A-4)**. By 4.2 it is a fix (a missed 0.5 s budget) | DEC-1159 (2): option 1, else option 5 | The branch is 3 commits ahead with a net diff of zero. Option 1 was tried and reverted (`8da607e3d`: p95 0.76 s against 0.55 s). So option 5 applies: the warm p95 stays a named red. To close: one record line, and keep the `accepted_reds` entry (ACT-ACCEPTED-REDS-1). Delete the branch. | HO:11; DEC-1159; E-2:244 |
| W2-156 DAEO-ylsh | in_progress; built, stopped as auditor started | **decided: finish (A-4)**; feature (4.1) | the spend brake (A-1) | 6 commits ahead, 1,980 lines (`5e7fb0572`). No review under 3.6. Merge integrate, run `gov accept`, land. `W2-156-tests` is an empty folder; remove it. | HO:13; E-2:241, 244 |
| W2-186 DAEO-sq3a | in_progress; built, stopped | **decided: retired (6.1)** | the reranker into the sandbox, and the sandbox is gone | The branch and tests worktree hold 5 and 3 commits (3,342 lines). That includes revised W1-33, W1-46 and W1-28 loopback cases, and those assert the sandbox. Do not land them. Delete the branch and both worktrees. | HO:14; E-2:218 |
| W2-191 DAEO-v6pf | in_progress; round 1 fixes merged | **decided: finish (A-4)**. By 4.2 it is a fix (F-023) to gov close's test-map selection | built; no review round 2 (3.6) | 15 commits ahead (`a1cdb91f7`, 30 cases). The kernel schema bytes need no CIT-P now (3.5). Land if green. Record it as a fix in W2-66's or W2-115's record. | HO:15; E-2:244 |
| W2-192 DAEO-mpq2 | in_progress; built, accept 30/30, PACKAGES | **decided: finish (6.1)** | DEC-1200 | 9 commits ahead (`62a038daa`). Left: the path case (two support helpers run A3 after A2; 65 reds). The kernel CIT-P part A becomes the CTO's own call (3.5). Then land. | HO:16; E-2:231 |
| W2-195 DAEO-d8df | in_progress; built 45/45, CIT-P, PACKAGES | **decided: finish, trimmed to 3.4 (A-13)** | DEC-1204 (6) | 5 commits ahead (`67a36b9e4`). Left: trim the skill text to 3.4. The CIT-P becomes the CTO's own approval (3.5). Triage the 173 lead_verify reds; they are elsewhere, and one product defect sits outside its paths, which is a fix for its owning ticket (4.2). S3 adds a launch refusal, `LAUNCH_JUDGING_RULE_MISSING`; whether it stays is the CTO's call. | HO:17; E-2:110, 233 |
| W2-81 DAEO-l78m | in_progress; re-run stopped | **decided: close on its record (A-4)** | its six repositories become the release's proving run | 0 commits ahead. JOB-13 (the read step) is not needed. Close with a record line. The run repositories under `~/gov-os-runs/W2-81/run-0.1.1/` stay for §8.2 (2). | HO:12, 29-30; E-2:252 |
| W2-82 DAEO-4k3l | open; not started | **decided: fold into the templates (A-4)** | READY by code | No worktree. Its KPI lines go to audit 1's template work; close the ticket as folded. | HO:18; E-2:248 |
| W2-193 DAEO-7jln | open; filed | **decided: build (6.1)**. By 4.2 it is a fix (F-028) to gov close | DEC-1203 | No branch. The failing tests are written first, as a launched fix under W2-115's record (the TD, then the engineer), with no ticket loop. | HO:19; E-2:232 |
| W2-194 DAEO-kq8b | open; filed | **decided: build (6.1)**. By 4.2 it is a fix (F-030, F-031) to gov close | DEC-1203, DEC-1206 | As W2-193. EXAMIN's close needs it (P2 §4). | HO:20; E-2:232 |
| W2-46 DAEO-nn1s | open | **decided: replaced by the release acceptance (A-4)** | F-8 | Close as superseded by §8.2. | HO:21; E-2:251 |
| W2-47 DAEO-jip3 | open | **decided: replaced (A-4)** | F-8 | Same as W2-46. | HO:22; E-2:251 |
| W2-15b DAEO-swdu | open | **decided: retire, unless the first fresh 80 is below 95 % (A-4)** | 5.1, 5.3 | Waits on JOB-17 (queued, not run). Retire when the first fresh 80 reads 95 % or more. | HO:23, 143; E-2:249 |
| W2-00 DAEO-sdxk | open | **decided: retire (A-4)** | no role in §4 | Its records stay in git. The 659 direct commits that carry `Task: DAEO-sdxk` (Table 2) need a new trailer: `Class: chore` or `Fixes:`. | HO:24; E-2:250 |
| W2-17 DAEO-sdhj | deferred (Wave 3 tag) | **decided: build for the release (6.1)**; feature (4.1) | F-7 | No branch. Set the status back to open and the tag back to wave-2. C3 (an update that loses files if wrong). | E-2:225; W3P:51 |
| W2-18 DAEO-057v | deferred | **decided: build with W2-17 (A-4)** | `gov update` installs a pinned release | Fold into W2-17's ticket as its KPI lines, or keep it as a sibling ticket; the CTO picks. | E-2:246; W3P:52 |
| W2-19 DAEO-jzvg | deferred | **decided: Wave 3 (6.1)** | O-3 | Its paths were cleared to a placeholder (DND 273). Nothing is left. | E-2:235; W3P:53 |
| W2-34 DAEO-yadm | deferred | **decided: fold into W2-36 (A-4)** | DEC-1047 | Move its KPI lines to W2-36 and close it as folded. | E-2:247; W3P:54 |
| W2-35 DAEO-2keg | deferred | **decided: Wave 3, driven by friction (A-4)** | O-end | — | E-2:253; W3P:55 |
| W2-36 DAEO-w19l | deferred | **decided: build (6.1)**; feature | O-3 | Set it back to open, with W2-34's lines added. | E-2:226; W3P:56 |
| W2-42 DAEO-fau3 | deferred | **decided: retired (6.1)** | the guard is retired | Close as retired. | E-2:218; W3P:57 |
| W2-115b DAEO-j9z6 | deferred | **decided: build for the release (A-4)**; feature, C3 | the landing in adopted repos | Set it back to open. W3-P32 goes. | E-2:245; W3P:38, 58 |
| W2-121c DAEO-5rgj | deferred | **decided: build, as the run-time tool (6.1)** | O-3, O-6 | Its KPI lines predate RT-1 to RT-8. Re-spec it against A-5 before the TD starts. | E-2:227, 263-274 |
| W2-121d DAEO-6w5n | deferred | **decided: build, as the run-time tool (6.1)** | O-3, O-6 | As W2-121c. W3-P35's plan fix folds in here. | E-2:227 |
| W2-27 DAEO-h4rh, W2-28 DAEO-csj8, W2-29 DAEO-b926, W2-30 DAEO-60rw | moved (EXAMIN Wave 0, DEC-1201 (4)) | **retire as Gov OS tickets** (follows from 7.2 and 8.2; not named in §6) | Wave 0 is direct work with no tickets (7.2). EXAMIN on the release is §8.2 (3), (4) | Their records stay. EXAMIN's own `exa-*` tickets are audit 6's. | W3P:62; E-2:282, 309-310 |
| W2-196 (withdrawn) | removed (DEC-1209 (1)) | **replaced by Table 3** | 4.5 | The class check by code goes into the deterministic landing (6.1). | DEC-1209; E-2:143-148 |

### 1b. Wave 3 parking rows (`docs/plan/WAVE_3_PARKING.md`)

| Row | Idea | Disposition | Why | Source |
|---|---|---|---|---|
| W3-P09 | hierarchical orchestration, trialled on EXAMIN | keep parked (Wave 3, friction) | Partly in force: 4.3 names a senior engineer per stream. The measured trial is still open. | W3P:7; E-2:131, 314 |
| W3-P01 | ticket templates per class | fold into the deterministic templates (6.1) | only features are tickets (4.1) | W3P:8 |
| W3-P02 | brief gaps in the kernel | fold into memory by construction and `gov brief` (5.4) | the brief comes out whole | W3P:9 |
| W3-P03 | the nightly in the judge | fold into the run-time tool | A-1 keeps the nightly until then | W3P:10; E-2:241 |
| W3-P04 | skill for the morning package, emergencies and ACT files | retire | the ACTs retire (2.10) | W3P:11 |
| W3-P05 | progress line and weekly numbers by gov status | fold into the weekly measures (10.2) and the daily digest line (A-2) | — | W3P:12 |
| W3-P06 | `Implements:` ids resolved at commit time | fold into the deterministic landing | the landing already checks trailers (4.4) | W3P:13 |
| W3-P07 | stale-probe check at merge | retire | no review per ticket (3.6) | W3P:14 |
| W3-P08 | containment for claims on unready tickets | fold with W2-82 (READY by code) | — | W3P:15 |
| W3-P10 | gov context packet per stream | retire | `gov context` is switched off (5.5) | W3P:16 |
| W3-P11 | tree-rooting gap in the guard's `parts()` | retire | the guard is retired | W3P:17 |
| W3-P12 | machine-agnostic planning (W2-20) | **decided:** build, as RT-3 | 6.1, 6.3 | W3P:18 |
| W3-P13, P14 | guard hardening, rule 1 | retire | the guard is retired | W3P:19-20 |
| W3-P15 | secrets cache hardening | retire | no gitleaks while private (2.11) | W3P:21 |
| W3-P16 | the dead-man as a product feature | fold into the run-time tool (RT-2, RT-7) | A-1 keeps the dead-man until then | W3P:22 |
| W3-P17 | W2-81 judge: refuse, do not drop | keep parked; becomes a fix (4.2) if the release proving run hits it | §8.2 (2) uses the judge | W3P:23 |
| W3-P18 | export refusal by namespace policy | keep parked (friction) | — | W3P:24 |
| W3-P19 | impossible-task canaries | keep parked (friction) | — | W3P:25 |
| W3-P20 | weekly sample of the orchestrator's commits | fold into Table 3's class check by code | catch by code, not by audit (2.1) | W3P:26 |
| W3-P21 | reviewer recall per model | retire | no review per ticket (3.6) | W3P:27 |
| W3-P22 | W2-32 R2-F1, nested parents (strict xfail) | fix (4.2a) in W2-32's record; the failing test already exists | the weekly maintenance (5.9) takes it | W3P:28 |
| W3-P23 | role files for the CTO and the senior engineer | retire: done | `template/governance/kernel/roles/senior-engineer.md` exists (W2-33) | W3P:29; HO:122 |
| W3-P24 | typed handoff record | fold into the run-time tool (RT-5) | checkpoints are kept (6.1) | W3P:30 |
| W3-P25 | undefined roles drafted | retire | roles are set by 4.3 | W3P:31 |
| W3-P26 | `_KEY` drops other id keys | keep as a fix-when-hit (4.2a) in W2-134's record | a row, not ordinary work | W3P:32 |
| W3-P27 | a kept run names its commit | fold into the fresh-80 measure | 5.3 asks for a pinned snapshot | W3P:33 |
| W3-P28, P30 | already retired | remove the rows | — | W3P:34, 36 |
| W3-P29 | sandbox git lock placeholders | retire | the sandbox is retired | W3P:35 |
| W3-P31 | W2-181 | remove: closed (it is in the 141) | — | W3P:37 |
| W3-P32 | W2-115b | **decided:** build (A-4) | — | W3P:38 |
| W3-P33, P34 | W2-121c, W2-121d | **decided:** build, as the run-time tool | — | W3P:39-40 |
| W3-P35 | plan check treats a merged dependency as met | fix (4.2a) in W2-136's record, done inside W2-121d | `plan_override: DEC-1157` is the workaround | W3P:41 |

## Table 2: the 141 tickets and the 1,988 direct commits, classed

**Population.**
- Tickets: the 141 worked tickets in P2's CSV.
- Direct commits: all first-parent non-merge commits on w2/integrate from 2026-10-16 to 2026-11-16, which is **1,988**. By role trailer: 1,810 orchestrator, 94 owner, 57 none, 17 operator, 13 other. 659 carry `Task: DAEO-sdxk` and 432 carry `Task: decision-record`. 1,731 (87 %) touch three files or fewer.
- RR M3's 335 was one week (11-09..16) and `DAEO-sdxk` only.

| Class | Tickets (141) | by rule | Direct commits (1,988) | by rule |
|---|---|---|---|---|
| feature | **64** (45 %) | 54 × 4.1, 10 × 4.6b | **30** | 24 × 4.1, 6 × 4.6b. The dispatcher v4.2 to v4.6, the dead-man, merge queue speed-ups, new guard rules: feature work done without a ticket |
| fix | **50** (35 %) | 31 × 4.2a, 19 × 4.2b | **24** | 19 × 4.2a (ACT-GUARD-FIX-1 to 8 are 7 of them), 5 × 4.2b (path cases) |
| chore | **27** (19 %) | 13 × 4.6r, 11 × 4.6k, 2 × 4.6c, 1 × 4.6t | **1,934** (97 %) | 1,843 × 4.6r (records only), 75 × 4.6c (configuration, re-pins, path-map entries), 16 × 4.6k (instruction text, generated copies) |

What each class cost as a ticket (P2 lead plus worker list cost; 30 tickets have no worker data, so these are low):

| Class | Profiles then (L / S / F) | Median claim to merge | Reviewer runs | Reopened | Lead + workers |
|---|---|---|---|---|---|
| feature (64) | 0 / 36 / 28 | 0.68 d | 111 | 8 | $2,458 |
| fix (50) | 17 / 15 / 18 | 0.39 d | 55 | 4 | $1,334 |
| chore (27) | 2 / 21 / 4 | 0.80 d | 40 | 4 | $505 |

**Sample, 10 per class.** Each class has 7 tickets and 3 commits, drawn at random (seed 4) from the CSV.

| Class | Item | Then | Rule applied | Why |
|---|---|---|---|---|
| feature | W2-121 | FULL | 4.1 | `gov dispatch`, a new command |
| feature | W2-121b | FULL | 4.1 | the dispatcher's landing hand-off, new behaviour |
| feature | W2-16 | FULL | 4.1 | hash-pinned releases |
| feature | W2-172 | FULL | 4.1 | the memory audit's driver and schedule |
| feature | W2-116 | STANDARD | 4.1 | the designers' store |
| feature | W2-13 | FULL | 4.1 | a ranked lexical route (BM25) |
| feature | W2-58 | STANDARD | 4.1 | Policy 2 in the guard; the surface is now retired |
| feature | 6c0824aad | direct | 4.1 | ACT-DISPATCH-1: the dispatcher enforces max_leads; new behaviour, no ticket |
| feature | d5b5cfff2 | direct | 4.1 | ACT-DEADMAN-INBOX-1: the dead-man wakes on inbox items |
| feature | b7a373cf9 | direct | 4.6b | ACT-GUARD-CALLLOG-1: a new guard rule (a log line per decision) |
| fix | W2-63 | LITE | 4.2b | W1-49's window tests wrong after DEC-838 (owning: W1-49) |
| fix | W2-179 | LITE | 4.2b | W2-170's F3 case miscounted (owning: W2-170) |
| fix | W2-05 | FULL | 4.2a | the git environment leaked into checks (owning: W1 checks); 626 product lines, 19 areas |
| fix | W2-67 | FULL | 4.2b | test hygiene: copies, nested runs, temp folders |
| fix | W2-134 | STANDARD | 4.2a | line-cited gold went stale (owning: W2-61) |
| fix | W2-90b | LITE | 4.2b | live-wiring tests still tied to this repo (owning: W2-90) |
| fix | W2-146 | STANDARD | 4.2a | the id reader missed declared id forms (owning: retrieve) |
| fix | c09f9b66d | direct | 4.2a | ACT-IDLE-GUARD-2: false idle items, slow plan |
| fix | fa6135903 | direct | 4.2a | ACT-GUARD-FIX-6 |
| fix | ba7ba093f | direct | 4.2b | the CTO's path case in W2-111's tests |
| chore | W2-94 | STANDARD | 4.6r | EXAMIN's question set: data by an independent writer, not code ($63 as a ticket) |
| chore | W2-88b | STANDARD | 4.6r | the record of a smoke run on two public repositories |
| chore | W1-43 | FULL | 4.6r | the exit audit record |
| chore | W2-15a | FULL | 4.6r | research baseline record |
| chore | W2-105 | STANDARD | 4.6k | template install block removed (kernel text) |
| chore | W2-100 | STANDARD | 4.6k | domain skills A (kernel text; 3.5) |
| chore | W2-188 | STANDARD | 4.6k | the adopt skill's step 6 text |
| chore | 32d10098b | direct | 4.6r | records only (a claim line and a status line) |
| chore | 96b4a31fe | direct | 4.6r | records only (DECIDED-NOT-DONE row) |
| chore | 178f9bc05 | direct | 4.6r | records only |

Findings the table cannot show:
- **Size does not separate the classes.** Fixes have a median of 0 product lines (p75 95), but 10 of 50 exceed 150 lines. W2-42a is 2,778 lines and W2-05 is 626 lines across 19 areas. Features have a median of 492. So the rubric routes by what the change does, and uses size only to choose who does a fix (row 3a or 3b below).
- **Tests outweigh code 6.2 to 1.** The 141 tickets merged 51,902 product lines and 323,216 test and fixture lines (git numstat of each ticket's merges).
- **25 of the 141 tickets ($1,024, 24 % of the cost) built surfaces now retired or switched off.** These are the guard, the sandbox, the walls, `gov context`, gitleaks, the operator and its ACTs, and the probe gate (CSV column `retired_surface`).
- **The path list alone decides little.** It routed 22 of the 141 rightly and 15 wrongly. Two examples of the wrong ones: question sets live under `tests/` but are data, and skills carry their own check tests. The other 104 need the yes/no answers. So the table asks its questions first and uses the path list to spot chores and to set the criticality.
- **Classing is one auditor's judgement on titles, diffs and KPIs.** The rule column in the CSV lets the CTO re-check any row. Eight tickets have no merge on the first-parent line (for example W2-01, W2-53, W2-131), so their line counts read 0.

## Table 3: the rubric (first matching row wins)

Inputs:
- the path list: files to change, or a ticket's allowed paths;
- an estimate of product lines and minutes;
- the yes/no answers in the table.

Find the KPI line with `gov retrieve` first (5.4).

| # | Question | Yes: route | Who, and what it needs | Source |
|---|---|---|---|---|
| 0 | A release, re-pin, push, sudo, or the owner's machine settings? | **the owner's**; not routed | the owner, in his own terminal | 2.4-2.6 |
| 1 | Does the path list hold only records, docs, configuration values or kernel/instruction text? That means no `src/**`, no `tests/**`, no `fixtures/**` and no run-time tool code, and the affected tests stay green. | **chore** | A direct commit by the CTO or a senior engineer, plus a digest line. Kernel text goes in on the CTO's own approval (3.5), with its generated copies in the same commit. Contract text waits for the owner's yes. | 4.6; 3.5; P2 §3 (12 copy ACTs) |
| 2 | Does it leave behaviour unchanged (a refactor or tidy-up, tests unchanged and green)? | **chore**, landed | It goes through the landing, which runs the selected tests. | 4.6 |
| 3 | Does an existing KPI line, spec or decision already state the behaviour it restores? That covers a red, a regression, a wrong test and a known bug. | **fix** in the owning ticket's record | The owner is the ticket whose allowed paths hold the code, or the feature the KPI belongs to. Add a `Fixes: <ticket>` trailer and one line in that record. No new ticket, no review. | 4.2; DEC-1088 lifted for fixes |
| 3a | ...and is it about 50 product lines or fewer, in one area, and about 30 minutes? | direct fix | By the CTO, a senior engineer or the engineer. The failing test is written first, and the test and the fix go in one commit. | 4.2; RR §7.2 |
| 3b | ...otherwise | launched fix | The TD writes the failing acceptance case when the KPI's case is missing or wrong (G-1 checks the author). The engineer works to green, then `gov accept`, then the landing. | 4.2; 4.3 |
| 4 | Otherwise: new behaviour (a new command, interface, rule or KPI line, including one on a closed feature) | **feature ticket** | Spec and KPIs (product-spec), then the TD's tests red on the base, then the engineer until `gov accept` is green, then the landing, which closes the ticket. No reviewer. Model and effort come from the table below. | 4.1; 4.3; 4.6; 3.6 |

**Guardrails.**
1. **Time box.** Stop when a row 1, 2 or 3a item passes 30 minutes, needs a second commit, or turns a test red. Revert what is half done and re-enter the table at row 3b or 4 (RR §7.3, the circuit breaker).
2. **When in doubt between 3 and 4:** if no KPI line states the behaviour, it is a feature (4.1).
3. **Checked by code at the landing.** It flags; it never refuses (2.1).
   - A commit outside a feature ticket that changes `src/**` with no test change in the same commit.
   - A chore commit that touches `src/**`, `tests/**` or run-time tool code.
   - For records-only commits, the class is computed, so no trailer is needed (RR M4: 0 of 8 hand trailers were set).
   - Flags go to the daily digest line.
4. **Review** happens only for a red landing, a failed merge, or a feature that does not work as intended; batch it where you can (3.6).

**Criticality, for model and effort** (from the path list, highest match). This revises `criticality.yaml` now that the guard, hooks, permissions and operator are retired:
- **C3:** the kernel and the Contract (`template/governance/kernel/**`, `docs/contract/**`); the landing and close (`src/gov/close/**`, `src/gov/accept/**`, `land.py`, the landing check, the merge queue); the memory measure and sets (`src/gov/memaudit/**`, `fixtures/evaluation/**`); release, update and pin (`src/gov/release/**`, `src/gov/update/**`, `src/gov/lock/**`); the path map.
- **C2:** all other `src/**`, schemas, the test map, run-time tool code.
- **C1:** records, docs, scratch tools.

**Model and effort per role.** This is DEC-1120 (2)-(3) with the reviewer rows removed (3.6) and the landing auditor added (O-5). Max only with a recorded reason (DEC-1120 (3)). RT-8 reads this table. **Note, DEC-1225 (2026-11-22):** the table below replaces DEC-1214 K1's. Opus runs only the orchestrating sessions (each app's CTO and the senior engineer); every other agent runs Sonnet, high, at every class, C3 and C0 included; no session runs Fable. The one exception is a wide, comprehensive audit the owner asks for, which runs on Opus through the exceptions file (`governance/project/model-exceptions.yaml`); a reviewer called after a failed landing or for a bug runs Sonnet. A class no longer picks a model.

| Role | C3 | C2 | C1 |
|---|---|---|---|
| CTO, senior engineer | Opus, high | Opus, high | Opus, high |
| Ticket lead (features) | Sonnet, high | Sonnet, high | not ticketed |
| Independent test designer | Sonnet, high | Sonnet, high | Sonnet, high |
| Engineer (feature or launched fix) | Sonnet, high | Sonnet, high | Sonnet, high |
| Quality auditor on a red landing or failed merge | Sonnet, high | Sonnet, high | Sonnet, high |
| Batched review (3.6) | Sonnet, high | Sonnet, high | — |
| Product-spec, research | Sonnet, high | Sonnet, high | Sonnet, high |
| Question writers / their checkers / the memory reader | Sonnet, high / Sonnet, high / Sonnet, high, no tools (DEC-1098, DEC-1225 (4)) | | |
| Watchers, C0 helpers | Sonnet | Sonnet | Sonnet |

**Measured against the 141 (estimate; method below).**

| | Count | Then | Under the rubric |
|---|---|---|---|
| Not a ticket at all | **77** (27 chores, 50 fixes) | 77 tickets: 19 LITE, 36 STANDARD, 22 FULL; 95 reviewer runs; $1,839 | 27 direct commits; 50 fixes, 3a or 3b; ~$841 |
| Feature, review dropped | **39** | 111 reviewer runs; part of $2,458 | no per-ticket review |
| Feature, same route | **25** | — | the model and effort differ only |
| **Routed differently** | **116 of 141 (82 %)** | **$4,297** (lead plus workers) | **$2,434 to $2,869: saves $1,428 to $1,863 (33 to 43 %)** |

**How the cost was estimated.** It uses P2's per-ticket `lead_cost` and `*_cost` columns.
- **Chore:** the work (the engineer's and product-spec's cost) plus one lead run, which stands in for the CTO's own time.
- **Fix:** the TD and the engineer (failing test and fix) plus one directing session.
- **Feature, high end:** the actual cost minus the reviewer cost.
- **Feature, low end:** also caps the lead at two runs. The extra runs were PACKAGES relays and review rounds: 45 % of lead runs ended in PACKAGES (P2 §3).
- **What it leaves out:** the CTO's per-ticket coordination (about 46 % of spend, not attributable; P2 §2); the median of 6 to 11 CTO commits per ticket (P2 §1); and the 30 tickets with no worker data. So the saving is likely understated.
- **Time:** chores and fixes took a median of 0.80 and 0.39 days from claim to merge. As direct work under the 30-minute box they take minutes to an hour (estimate).
- **Model routing alone** (RUBRIC-2) re-priced one week at 8 to 14 % (`packages/USAGE-RUBRIC-2.md:38`). Not ticketing chores and fixes is the larger lever.

**Against the earlier designs.**
- **Provisional rubric:** its "protected means FULL" would have made 90 of the 141 FULL (RR M2). Here, protected paths only raise the TD and the engineer to Opus (26 C3 features). They never add a review.
- **RR §7.3:** Q maps to chore and direct fix. L, S and F collapse into one feature route, with criticality setting the model and effort. RR's emergency lane E is not needed: an urgent repair is a row 3 fix, done at once and recorded after.

## Decisions for the owner

1. **The rubric (4.5, "agree on the rubrics").**
   - (a) Approve Table 3 with its model and effort table. Cost: nothing; the CTO puts it in the orchestration skill (3.5).
   - (b) As (a), plus a size gate: a fix over 150 product lines or more than one area becomes a feature ticket. Cost: about 10 of the month's 50 fixes back into tickets.
   - (c) Keep the provisional rubric until audit 1's landing exists. Cost: the 82 % misroute goes on.
   - **Recommend (a).**
2. **Does each feature ticket still need the owner's approval (DEC-974)?**
   - (a) Yes, per ticket. Cost: one owner line per ticket.
   - (b) One approval per batch. Cost: one line per batch.
   - (c) None for the items already on §6.1's build list; the owner approves only new features outside it. Cost: none for the release.
   - **Recommend (c).**

## The CTO decides (under 3.5, 4.2, 4.6)

- **Record W2-191, W2-193, W2-194 and W2-155 as fixes** in their owning records (W2-115 or W2-66 for the close; retrieve for W2-155). Run W2-193 and W2-194 as launched fixes (row 3b), not ticket loops. Recommend: yes.
- **Apply Table 1's Wave 3 parking dispositions.** That is: retire 11 rows (one of them because it is done), fold 10, turn 3 into fixes (P22, P26, P35), remove 3, and keep 4 parked; 4 more are already decided. Also retire W2-27 to W2-30 as Gov OS tickets. Each follows from a decided row (6.1, 7.2, 8.2). Recommend: yes.
- **Delete W2-186's and W2-155's branches and worktrees, and the empty `W2-156-tests` folder.** Leftover worktrees of closed tickets are audit 5's. Recommend: yes, after audit 5's list.
- **Revise `criticality.yaml`** to Table 3's C3 list (a configuration chore). Recommend: yes, with RT-8.
- **Build the class check by code into the deterministic landing.** It replaces W3-P20 and RR's weekly auditor sample. Recommend: yes.
- **Run DEC-1120 (3)'s trial of Sonnet-high leads** on two C2 features (leads were 23 % of spend, P2 §2). Recommend: yes, after the 0.1.2 re-pin.
- **Decide whether W2-195's launch refusal `LAUNCH_JUDGING_RULE_MISSING` stays** when it is trimmed to 3.4. Recommend: keep it as a `gov brief` flag, not a launch refusal (2.1).
