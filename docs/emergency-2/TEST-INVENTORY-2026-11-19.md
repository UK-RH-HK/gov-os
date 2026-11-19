# The test suite: what the numbers count, an inventory, and what to keep and retire

`docs/emergency-2/TEST-INVENTORY-2026-11-19.md` · the CTO, 2026-11-19 13:17 · research only: nothing is deleted or moved before the owner's yes

Counted at `76bd725f5` by collecting every test id (`pytest --collect-only`, with and without the opt-in suites) and by reading each test function's source. Run times are from the full suite of 05:18 to 07:01 on `712c71cba` (3 workers).

## 1. The numbers reconciled

A **test function** is one `def test_...`. A **case** is one run of it: a parameterised function gives one case per parameter set. The **default run** leaves out two opt-in suites.

| Number | What it counted | When |
|---|---|---|
| about 5,000 | test functions in the repository: 5,017 on 10 October, 5,617 on 20 October | Wave 1's end |
| 7,184 | cases in one **scoped selection** after a direct commit (the landing's impact-selected run), not the full suite | 16 November 17:16 |
| 21,120 | I did not find this figure verbatim. The full suite ran 21,260 cases on 16 November (21,081 parallel, 179 serial) and 21,626 on 17 November | 16 to 17 November |
| 18,273 | cases in the full suite's parallel phase after the guard's tests were retired | 18 November 23:06 |
| 18,639 | cases in the full suite's parallel phase; with the 75 serial cases, 18,714 | 19 November 05:18 |
| 18,651 | cases the default run collects now | 19 November, about 13:12 |
| 24,471 | every case that exists now, the two opt-in suites included | 19 November, about 13:12 |
| 13,649 | test functions now | 19 November, about 13:12 |

How it grew: 5,017 functions on 10 October; 7,264 on 1 November; 13,649 now. The default run was 15,500 cases on 21 October, fell to 9,650 on 10 November when the opt-in suites were cut out, then rose by 11,800 cases in one week (10 to 17 November).

## 2. The inventory

**Totals.** 24,471 cases from 13,649 functions, in 168 acceptance folders (one per ticket; 16,677 cases) and 55 unit folders (7,794 cases).

| Suite | Cases | What it is |
|---|---|---|
| default | 18,651 | what every full suite and every scoped selection draws from |
| opt-in `lifted` | 2,220 | features built but switched off here: the strict close, the secrets scan (gitleaks), the probe gate, trailers, the ratchet, the batch close. Not run by default |
| opt-in `breadth` | 3,600 | extra parameter cases of live features, cut from the default run for speed |

**Parameterised cases.** 13,635 of the 24,471 cases come from 2,813 parameterised functions; the other 10,836 functions are one case each. 67 functions have 20 or more cases each and hold 2,032 cases; 7 have 50 or more and hold 550. The largest is one W2-94 test with 130 cases.

**Duplicates.** Six groups of test functions have identical bodies in different files: 7 redundant functions in all (W2-157, W2-159 and W2-170 share two; W2-100 and W2-101 share one). Duplication is not what makes the suite large.

**By area.** Grouped by each folder's ticket title with keyword rules, then corrected by hand for three folders; a folder-by-folder reading would move some rows.

| Area | Folders | Cases | In the default run | Seconds |
|---|---|---|---|---|
| Memory and retrieval (the store, rebuild, retrieval, the measure, links, impact) | 54 | 6,068 | 4,583 | 5,986 |
| Tickets, landing and checks (close, queue, accept, launch, brief, check, plan) | 74 | 8,092 | 5,760 | 3,415 |
| Adoption, update, install, release, secrets | 28 | 2,574 | 1,535 | 1,340 |
| The run-time tool (dispatch, resources, messages, checkpoints) | 20 | 1,913 | 1,841 | 1,025 |
| Kernel text: roles, skills, templates, hooks | 13 | 1,576 | 1,501 | 227 |
| This repository's own records and evaluation sets (the Contract's validators, the register's clean-up, question sets, the walls launcher, the CTO's scratch tools) | 26 | 3,778 | 3,143 | 1,524 |
| Retired or switched-off surfaces, by folder | 8 | 470 | 288 | 305 |

**Retired surfaces still tested.**
- In the default run, by folder: W2-159 and `tests/unit/session_watch` (159 cases; the Stop checks and session-watch that A-2 retires), W2-54 (78; the context packet), W2-50 (65; the guard's scratch root), W1-42 (22; Wave 1's exit run), W2-65 (1).
- In the opt-in `lifted` suite, not run: the strict close and its gates, about 1,100 cases (W1-30 478, `tests/unit/close` 387, W2-01 88, W2-07 69, W2-53 57, W2-68 22); the secrets scan, about 920 (W2-69 352, W2-71 303, W1-16 92, W1-15 91, `tests/unit/secrets_check` 79); lifted `gov check` families, 130 (W1-26).
- `tests/unit/orchestration` (820 cases, 542 in the default run) tests the CTO's scratch tools: the old dispatcher, the dead-man, the walls launcher. The first two retire at the cut-over.

**Run time.** The tests' own time sums to 13,822 seconds. The full suite took 80 minutes on 4 workers and 103 minutes on 3 workers confined to 6 CPUs. Ten folders hold 41 % of the time and 25 hold 64 %. W2-88 alone (memory for any repository: 325 cases that assess real repositories) is 1,645 seconds, 12 %. Unit tests are 32 % of the cases and 11 % of the time.

## 3. Proposal: what to keep and what to retire

The aim: the suite guards what Gov OS is now, and a full run takes about 50 minutes on 4 workers inside the load gate, against 80 today. Each line is for your yes; nothing is done before it.

| Code | Proposal | Cases | Time saved | Depends on |
|---|---|---|---|---|
| TI-1 | Retire the strict close's tests with the strict close itself (the `lifted` cases of W1-30, `tests/unit/close`, W2-01, W2-07, W2-53, W2-68) | about 1,100 | none today (not run) | your L2-1 and L2-2 |
| TI-2 | Retire the tests of surfaces already decided retired: W2-159, `tests/unit/session_watch`, W2-54, W2-50's guard part, W1-42, W2-65, and the old dispatcher's and dead-man's cases in `tests/unit/orchestration` | about 330, plus the scratch tools' | about 5 minutes of test time | the cut-over (W2-207) for the scratch tools |
| TI-3 | Keep the secrets-scan tests as they are: opt-in, run once before a repository goes public | about 920 | none | — |
| TI-4 | Keep `breadth` opt-in; run it weekly, not nightly | 3,600 | none | — |
| TI-5 | Move the slow, real-repository cases to a weekly tier, keeping one representative each in the default run: W2-88 first, then W1-07, W2-37, W1-41, W2-171, W1-35, W2-57 | about 930 | about 74 minutes of test time, a third of the suite | — |
| TI-6 | Retire the tests that pin this repository's past records, once G5 and the register's exit are settled: W2-130's clean-up marks, W2-49's CIT-P lines, W2-61's line-pinned gold sources. Keep the rules that guard the present (W1-01's authorship rule) | about 330 | small | your G5 answers |
| TI-7 | Thin the largest parameter sets to boundary cases where the cases differ only in a planted string (W2-94, W2-98, W2-153, W2-11, W2-69): a test designer proposes each cut | up to 1,500 | small (these are fast) | — |
| TI-8 | A fresh, read-only audit of the 223 folders, one line each (keep, thin, weekly tier, retire), by an independent auditor, before anything is cut | — | — | your yes to this page's direction |

**What I recommend:** TI-8 first (half a day, one Sonnet auditor), then TI-1, TI-2, TI-5 and TI-6 as one retirement change by a test designer. TI-5 is the one that makes the suite fast; the retirements make it honest. TI-7 changes the count more than the time, so it comes last.

**Limits of this page.** The area table comes from keyword rules on ticket titles, not from reading each folder. "Retired surfaces" counts whole folders only; cases about retired machinery inside live folders are not counted. Run times are one run's.
