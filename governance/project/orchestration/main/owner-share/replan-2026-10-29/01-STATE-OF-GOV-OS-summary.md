# The state of the Gov OS, 2026-10-29 (draft; delivered with the re-plan package)

From: the W2 orchestrator (`orchestrator DAEO-sdxk`), at the owner's request of 2026-10-29 (DEC-940, to be recorded).

**How this was made:**
- Five read-only research sessions gathered the evidence: capabilities (annex A), progress (B), stalls and slips (C), standing practices (D) and the weekly numbers (E).
- I checked the headline numbers against their sources, corrected two (noted where they occur), and wrote parts 1 to 7 from them.
- Every claim cites a commit (at most 12 hex digits), a file with its line or section, a close record, a ticket or a decision; the annexes carry the full tables.
- An auditor will sample these claims. Where I am unsure, or the evidence is thin, I say so.

**Abbreviations:**
- `REG` = `docs/DECISION_REGISTER.md`
- `LOG` = `.gov-runtime/scratch/orchestrator/log/`
- `PKG` = `governance/project/orchestration/packages/`
- `Q-<stamp>` = a close queue's log, `LOG/close-queue-<stamp>/queue.txt`

---

## 1. One page

**Where the Gov OS is solid**
- **The judge path holds.** gov runs from a pinned, non-editable wheel, re-pinned twice by hand with a verified sha256 and a smoke test each time: `6a4696eb` (DEC-922) and `5c401220` (DEC-935, registry `bc37c419`). Every hook line and declared check runs the pinned interpreter. The guard allows, refuses, and fails closed with no judge reachable, as tested on re-pin 2 (DEC-935).
- **When a close fails, the cause has never been the ticket's own code.** None of the 18 refused closes since 2026-10-16 names the closing ticket's work as a cause (B §4; lens H found the same, `docs/assessment/2026-10/H-test-strategy.md` line 416). The judge, its 16,500-test regression and the leads' red-first test design find faults before the close does.
- **Scoped closes work.** A scoped close runs about 5 minutes of tests against 65 minutes for a full one (B §2.2: 302 s against 3,918 s on average). On 2026-10-27 seven tickets closed in 3 h 54 min (`Q-20261027-1957`). W2-66's trial caught 32 of 32 planted faults (`docs/research/W2-66-scoped-close.md` line 39).
- **The gates moved failures earlier, where they are cheap.** Since gates (d), (e) and (h) went into the queue and the pin, no close has been refused for an uncommitted tree, a missing trailer or work without a task. The success rate rose from 5 of 20 attempts (10-17 to 10-22) to 8 of 11 (10-26 to 10-28) (B §3).
- **The nightly runs on a schedule and its length is measured.** It was green on its first scheduled night: 16,478 passed, 0 failed, estimate within 8 % (B §5).

**Where it is weak**
- **Memory is not proven, and its known defects are open.** There is no W2-61 measure and no EXP-003 result. The context packet runs 42 to 168 times over its ceiling. Any edit turns the index off silently. The superseded-decision filter fails open. Lens B measured 65 % semantic hit@5 against DEC-833's 85 % floor (A, CAP-10, CAP-15, CAP-17, CAP-01; `docs/assessment/2026-10/B-memory-retrieval.md` lines 413, 436, 480). Keystone 4 has barely started, and three of its tickets have no ticket file (W2-55, W2-61, W2-64).
- **The keystones are far from done.** Of 9, none is done and all are partial (A §3). Of 62 capabilities, 25 are built, pinned and proven, but only 3 at Wave 2 grade (CAP-24, 31, 38); the other 22 rest on Wave 1's `tk close`, behind a Wave 1 exit verdict of FAIL (A §1; `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` line 443).
- **Nine held tickets are 10 or more days stale:** W2-03, 05, 16, 20, 26, 37, 49, 51 and 52. Keystones 4, 5, 7 and 9 wait on them (A §0.2).
- **The hard boundary is off.** No git hook is installed, and CI cannot pass (A, CAP-39; K8).
- **Leads run unsandboxed, and no role, skill or model is loaded at launch.** W2-60 has neither a card nor a ticket; W2-56 has no ticket (A, CAP-22, CAP-61).
- **Close throughput is poor, and I am its largest single cause.**
  - 55 % of the close queue's wall time produced no close (C §1.1: 15.45 of 28.1 h).
  - My tooling or process is a cause in 14 of the 18 refused closes and the only cause in 6 (B §4). I made 42 slips in two weeks, of which 11 are not yet prevented (C §2.1).
  - 39 of the 80 standing practices live only in my prompt, briefs or tools, so an adopted product would not inherit them (D).

**What blocks EXAMIN's copy** (the owner's minimum, DEC-930 item 1):
1. **Memory proven.** W2-61's measure exists, and the K4 fixes land: W2-03, W2-04, W2-05 and W2-06, W2-55, W2-64, W2-13 and W2-15a. None is closed. W2-03 and W2-05 are built but held and stale.
2. **Agents load their role, skills and model at launch** (K3). W2-60 is unfiled; W2-11 is open; W2-58 is merged but not closed.
3. **The leads' sandbox.** W2-56 is unfiled; W2-21 is open; W2-20 is held.
4. **Adoption readiness on a proving ground.** Nothing has started: the proving ground is a new requirement (DEC-936 item 3.6). W2-26 and W2-52 are held, and W2-27 to W2-30 are open.
5. **Fast closes.** Scoped closes work, but W2-68's batch stays off until W2-77 lands and is pinned. P-SCOPE-RECORDS-1 is not delivered, so record edits still widen closes to full (DEC-929).

**My three most important recommendations**
1. **Make memory the critical path now, starting from a measure.**
   - File W2-55, W2-61 and W2-64 this week.
   - Run W2-61's 20-question measure on today's pinned stores as the baseline.
   - Merge back and resume the held K4 tickets (W2-03, W2-05, W2-37) in parallel, behind the resource gate.
   
   Without a baseline we cannot tell whether a K4 ticket helps. Memory is the longest chain to EXAMIN.
2. **Move my practices into the product, starting with the costliest.**
   - Add the guard's command-form rules to the lead brief: about 45 of 74 lead returns relearned them (C, S-8).
   - Add a rule that a known close-breaking row is fixed before the full closes it would hit (C, S9: one such row cost 15 h of held queue).
   - Switch on batched closes as soon as W2-77 is pinned.
   - Move the nightly and the merge-time stale-probe check into the judge (D: five priorities).
   
   This turns my process from the largest cause of refusals into the product's own checks, which adopted products then inherit.
3. **Clear the stale backlog with a parallel merge-back sweep.**
   - Merge back and re-verify the 9 held tickets in parallel, as many at once as the resource gate allows (about 4 to 6 leads beside the nightly window).
   - Then close them in batches once W2-77 is pinned.
   - File the missing K3 and K6 tickets (W2-60, W2-56) and start them beside the memory tickets: they share no code paths.

---

## 2. Capabilities and keystones (full matrix: annex A)

**Counts** (A §1; Contract text still v4.1, `docs/contract/contract.yaml`; v4.2 rides W2-49, held):

| Status | Capabilities (62) | Keystones (9) | v4.2 lite rows (2) |
|---|---|---|---|
| built, pinned and proven | 25 (3 at W2 grade: CAP-24, 31, 38; 22 at W1 grade only) | 0 | 0 |
| built and merged, not pinned | 0 | 0 | 0 |
| built and held | 0 | 0 | 1 (CAP-43.b, W2-16) |
| partial | 29 | 9 | 1 (CAP-44.h) |
| not started | 6, plus 2 dropped by design (CAP-26, CAP-60) | 0 | 0 |

**Keystones, one line each** (A §3):

| K | State | What it waits on |
|---|---|---|
| 1 Pinned judge | Closest to done: three pins, W2-59 and W2-65 closed | W2-07's close, in today's queue |
| 2 Close queue | Scoped closes work; 8 clean closes on 10-27 | The batch (W2-68 merged, off until W2-77); the closes of W2-57, W2-67 and W2-68; 9 stale held closes |
| 3 Agents know what to do | Policies 1 and 2, CLAUDE.md and ADR-0001 in; W2-62 closed | W2-60 (unfiled), W2-11, W2-09, W2-33; W2-58's close |
| 4 Memory | Barely started: W2-02 and W2-54 closed; W2-03, 05 and 37 held | W2-61's measure; W2-55 and W2-64 (unfiled); W2-04, 06, 10, 13, 15a, 32 |
| 5 Decision pipeline | W2-49 held | W2-55, W2-49's close, W2-12 |
| 6 Sandbox per role | W2-50 closed; W2-20 held; the disk gate is a hand rule | W2-56 (unfiled), W2-21, W2-42, W2-40 |
| 7 Releases | W2-16 held; three hand re-pins; no release cut | W2-49 then W2-16, the first release (DEC-772), W2-18, W2-17 |
| 8 Hooks and CI | Hooks off since 10-16; CI cannot pass; W2-05 held | W2-05, W2-06, W2-08, W2-43, W2-22, W2-45 |
| 9 Gate run, then EXAMIN | In name only: W2-26 and W2-52 held | Everything; last by design (DEC-828) |

**Uncertainty:**
- The 22 W1-grade "proven" rows rest on `tk close` and Wave 1's audit, whose verdict was FAIL.
- Ten capabilities have had no independent look since 10-16: CAP-05, 09, 13, 14, 27, 28, 42, 46, 57 and 62.
- No held branch has been re-verified against today's head.
- CAP-49 was not examined, under the held-out rule (A §5).

---

## 3. Progress since Wave 2 started (2026-10-16; details: annex B)

**Tickets** (B §1): of 70 Wave 2 ticket files, 15 are closed, 17 in progress (7 of them merged but not closed) and 38 open.
- Of the 15 closed, 13 closed with a clean `gov close` (exit 0). W2-01 was closed by owner decision (DEC-757, `f15ac648`); W2-48 was withdrawn (DEC-880, `6cce71bb`).
- Of the 52 tickets in the original plan (`4190c39e`), `gov close` has closed only W2-02 and W2-50. The other 11 clean closes are tickets added after the plan.
- That says something about how much of this fortnight went to making closes work at all, rather than to the plan's keystones.

**Close times** (B §2; queue logs give wall times):

| Kind of close | n | Test time, mean | Wall time, mean |
|---|---|---|---|
| Full, passed | 7 | 65.3 min | 73.5 min |
| Scoped, passed (W2-69 excluded) | 5 | 5.0 min | 10.2 min |
| Batched | 0 | the batch is not switched on | — |

- The queue's own gates take 10 to 14 minutes before each close: 6.1 h over 30 passes (C §1.1).
- A scoped close's whole slot is about 22 minutes, against about 85 for a full one (B §2.2).
- **The measured close times after re-pin 3 will be added here at delivery.**

**Close success rate** (B §3):
- 31 attempts finished and 13 passed (42 %).
- The second half was better than the first: 5 of 20 from 10-17 to 10-22, then 8 of 11 from 10-26 to 10-28.
- The refused full runs used 13.7 machine-hours of tests.

**Refusal causes by kind** (B §4; a refusal can carry several kinds):

| Kind | Present in | Sole cause in |
|---|---|---|
| (a) the ticket's own work | 0 of 18 | 0 |
| (b) the judge: gov's code and tests | 8 | 0 |
| (c) the environment, mostly load | 9 | 1 |
| (d) my tooling or process | 14 | 6 |

**The nightly** (B §5):

| Date | Head | Verdict | Wall | Estimate against actual |
|---|---|---|---|---|
| 10-21 | `dbd3cc53` | red 2 | 4,249 s | — |
| 10-25 | `45a6dfd5` | red 1 | 5,189 s | — |
| 10-28 (by day) | `5c40122014da` | 1 flaky candidate | 5,707 s | — |
| 10-29 (first scheduled run) | `8fa67ec8468a` | green | 5,623 s | 5,214 against 5,623 s (+7.8 %) |

The three earlier reds each named a test that has since been fixed, or is a flaky candidate.

---

## 4. Where things stall, and why (details: annex C)

**Ranked by measured time cost** (C §1.3):

1. **The close drought and the re-pin waits.**
   - No clean close from 10-22 22:17 to 10-27 17:12: 4 days 19 hours 55 minutes. This was mostly the wait for re-pin 1, which DEC-884 held until W2-66 was built, reviewed, merged and trialled.
   - The owner's terminal act for re-pin 1 came 25 h 40 min after its ACT, and 6 h 43 min after the ACT for re-pin 2.
   - **Removed by:** the re-pin cadence (DEC-933 item 1). Re-pins are now small and frequent, never held for a bundle.
2. **Refused closes.**
   - 14.7 h of queue wall time and 13.7 h of test time.
   - My tooling or process is present in 10.5 h of that test time and the only cause of 3.1 h.
   - 165.6 ticket-hours passed from a refusal to the clean close (C S-1).
   - **Removed by:** the gates (d), (e) and (h), with no recurrence since, and the merge-time stale-probe rule (DEC-895).
3. **The queue sat idle after two base reds.**
   - 16 h 28 min after the unswept settings regeneration (DEC-925).
   - 15 h 14 min after the green-here timeout (DEC-937; row W2-L429 had named the fix on 10-24).
   - **Removed by:** the first by DEC-925 item 2 (a full run on a clone first). The second is **not prevented yet**: no rule ranks a known close-breaking row ahead of the queue (C S9).
4. **A 6 h 39 min rebuild** (10-29 04:10 to 10:49). It delayed the queue by 8 h 46 min and the morning package by 3 h 25 min (C S-11).
   - **Root cause not found.** The quiet re-run took 271 s.
   - **Ruled out:** a failure, disk space, memory pressure, and Ollama not answering.
   - **Suspects:** concurrent rebuilds contending for the code-graph daemon or gitleaks.
   - **Removed by:** W2-76 (a rebuild lock and a watchdog; drafted), with `flock /tmp/gov-os-rebuild.lock` until it lands.
5. **The gates themselves.** 6.1 h over 30 passes, longer than the six scoped closes they guarded on 10-27 (68 against 79 minutes).
   - **Removed by:** W2-68's batch (one rebuild, one check, one regression per head), once W2-77 is pinned. P-SCOPE-RECORDS-1 stops record edits from widening closes.
6. **Load-sensitive reds.** Present in 9 of the 18 refusals and in 8.7 h of refused test time.
   - **Removed by:** W2-57's nightly route, which takes 15 serial entries out of the close, and ACT-W2-57-LS-1, which removed 6 load-sensitive entries. ACT-W2-57-LS-2 is to follow.

**The owner's answers are not a bottleneck by day.** The median answer to a daytime package is about 28 minutes (n = 18). Only overnight packages (7 to 13 h) and re-pin ACTs wait long (C S-7). The morning package (DEC-938) now batches the overnight ones.

**My slips, by kind** (C §2; 42 in total):

| Kind | Count | Caught by a check | By a rule only | Partly, or unknown | Not prevented |
|---|---|---|---|---|---|
| Record and commit discipline | 17 | 7 | 2 | 3 | 5 |
| Tool bugs | 9 | 8 | 0 | 1 | 0 |
| Scheduling and process | 10 | 2 | 4 | 1 | 3 |
| Scope and selection | 2 | 0 | 1 | 0 | 1 |
| Environment assumptions | 4 | 1 | 0 | 1 | 2 |
| **Total** | **42** | **18** | **7** | **6** | **11** |

**The 11 not yet prevented**, and what would prevent each:

| Slip | What would prevent it |
|---|---|
| R12: the namespace check runs on untracked files | `record_checks.sh` stages first, or checks `git ls-files` plus new files. A tool fix, mine, this week. |
| R14: rows marked in place instead of moved | A list check. A tool fix. |
| R15: a ticket committed before the decision it cites | The context check catches it, but only after the commit. A pre-commit order check, mine. |
| R16: reports leave tickets out of their totals | A generated progress line, `gov status` (D, I1). |
| R17: stale checkpoint sections | Renewed today. A checkpoint lint, mine. |
| S8: long commands run in the foreground | DEC-939 item 1, decided, to be committed when the queue ends. |
| S9: a known close-breaking row left unscheduled | A new rule, proposed above. |
| S10: the lead brief lacks the guard's command-form rules | A brief fix, to be committed when the queue ends. |
| P2: a brief told a worker to read a file the guard refuses it | The brief builder checks named reads against the role's refusals. |
| E3: cron pings never reach the phone | ACT-PUSHOVER-1 (DEC-939 item 7). |
| E4: run clones under `~/gov-os-runs` are never removed | P-TOOLS-REVIEW-1. |

---

## 5. What still needs building, and in what order

**First, the minimum for EXAMIN's copy**, in this order:

1. **Fast closes.** Everything else passes through them, and today a full close costs 85 minutes of slot.
   - W2-77 (the nightly's clean-up) and re-pin 3 (W2-68 and W2-71), then the batch is switched on and its gain measured.
   - P-SCOPE-RECORDS-1, so record edits stop widening closes to full.
   - W2-76 (the rebuild lock and watchdog).
2. **Memory proven** (K4). This is the longest chain, so it starts at once, with a measure first:
   - W2-61's 20-question baseline on the pinned stores;
   - then W2-03 (merge back), W2-55, W2-64, W2-04 (the packet ceiling), W2-05 and W2-06 (incremental indexing), W2-13 and W2-15a (semantic recall to DEC-833's 85 % floor);
   - W2-61's measure is repeated after each.
3. **Agents load their role, skills and model at launch** (K3), in parallel with 2, since it shares no code paths with it: W2-60 (file it), W2-11, W2-09, W2-33, and W2-58's close.
4. **The leads' sandbox** (K6), also in parallel: W2-56 (file it), W2-21, W2-20 (merge back), W2-42.
5. **Adoption readiness on the proving ground** (new, DEC-936 item 3.6). This follows 2 and 3, because adoption leans on both memory and the launch path. It needs:
   - synthetic repositories with planted problems, and a held-out question set per repository;
   - W2-26 and W2-52 merged back; W2-27 to W2-30.

**Then the rest of Wave 2:**
- K5: W2-49, W2-12, W2-55.
- K7: W2-16, the first release, W2-18, W2-17.
- K8: hooks and CI: W2-05, W2-06, W2-08, W2-43, W2-22, W2-45.
- K9: the gate run, then EXAMIN.

**Then Wave 3:**
- the plan's deferrals (`docs/plan/WAVE_2_REVISED_PLAN.md` §8);
- the re-plan's additions: mutation testing in the nightly window, the full capacity planner, and the reproducible environment with its RunPod trial.

**Why this order:** the re-plan package gives per-keystone estimates and a target date for the copy's start. Here I say only what the order rests on.
- **Measured throughput.** The machine closes 7 tickets in 4 hours when they are scoped (10-27). It closes 1 to 2 a day when they are full and refused often (10-17 to 10-22).
- **The critical path.** Memory's chain is the longest, with 8 or more tickets in sequence. K3 and K6 can run beside it.

**What I do not know yet:** how much the batch saves on this repository. It was measured only on a fixture, at 29 % for three closes (W2-68 run 1). Any date resting on it is a guess until it runs here.

---

## 6. Every standing practice, and where it must live (the full table: annex D)

- **Counts:** 80 practices. 17 are already in the kernel or the judge, so an adopted product inherits them. 24 are partly there. 39 live only in my prompt, briefs or tools. About 25 have no ticket that carries them (D, counts).
- **This repository's habits, not yet part of the Gov OS (the 39):**
  - the nightly's window, estimate, start conditions, locks and morning check;
  - the morning package and its notification;
  - the ACT format;
  - the record-reading gate, the network gate and the stale-probe check at merge;
  - the close lock and the scratch budgets;
  - the sweep and the re-pin ladder;
  - the placeholder scan and commits only after green checks;
  - the rule about rules;
  - the judgement rules, and model and effort per role;
  - the progress line, the weekly numbers and the digest.
- **The five to move first** (D's proposal, which I support):
  1. the nightly into the judge (W2-77, then a ticket for row W2-M407);
  2. the scratch budgets, the sweep and the verification lock into `gov launch` and the resource gate (KPIs on W2-20 and W2-21);
  3. the stale-probe check at merge time, and `Implements:` resolution, into judge commands;
  4. the judgement rules, the review-round limit (DEC-916) and red-first into the kernel, through a wider W2-11;
  5. the placeholder scan, and commits only after green checks, into a commit-time tier (W2-06, W2-08, W2-12).

---

## 7. The weekly numbers so far (DEC-930 item 2; details: annex E)

| ISO week | Clean closes per day | Refused closes caused by my tooling or process (S+E) | Measured cost (USD) | Owner decisions (delegated) |
|---|---|---|---|---|
| W42 (16 to 18 Oct, 3 days) | 0.00 | 0 of 3 (2 unclear) | 258.72 | 66 (17) |
| W43 (19 to 25 Oct) | 0.71 | 7 of 12, plus 1 contributing | 1,621.87 to 1,678.08, of which 1,051.44 is lens assessments | 99 (24) |
| W44 (26 to 29 Oct 13:00, 4 days) | 2.00 | 2 of 3 | 197.84 to 216.57 | 15 (2), plus DEC-939 and DEC-940 to record |

**Cost:** the figure is the Claude CLI's `total_cost_usd` from the leads', workers' and assessments' result files, an API-price figure, not an invoice. **It does not cover:**
- my own session;
- the workers of removed worktrees (most closed tickets);
- probes and auditors outside those logs;
- the owner's sessions.

There is no measured source for those. To make the measure whole from now on, workers' result files should be kept before a worktree is removed.

**Owner decisions** are the register's ACCEPTED entries, dated by their status line.

---

## Annexes (attached in this file at delivery)

- **A.** Capabilities and keystones, one row each, cited (`drafts/state/A-capabilities.md`).
- **B.** Progress: tickets, close times, success rate, refusal causes, the nightly (`drafts/state/B-progress.md`).
- **C.** Stalls, measured, and my 42 slips (`drafts/state/C-stalls-slips.md`).
- **D.** The 80 standing practices and their homes (`drafts/state/D-practices.md`).
- **E.** The weekly numbers (`drafts/state/E-weekly.md`).
