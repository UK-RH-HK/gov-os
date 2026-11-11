# Inventory of the tests and the code (DEC-1039 item 2, the report only)

**By:** the CTO's read-only analyst (session debdb3f7), 2026-11-02 evening, under the emergency (DEC-1033, DEC-1038,
DEC-1039). **Tree read:** the main tree at `w2/integrate` `3630679c74ce` (clean). **Nothing was changed** in any
tree. The helper scripts and raw outputs are in `/tmp/gov-os-emg-inventory/` (`size.py`, `counts.py`, `dups.py`,
`lit.py`, `kpimap.py`, `dead.py`; `collect.txt`, `size.json`, `counts.json`, `funcs.json`, `dups.json`,
`families.json`, `skipped.txt`, `propagation.txt`). An **estimate** is marked as such. Every other figure comes from a
command named beside it.

## Headline

- **Size:** 322,830 lines in the eight groups below, 222,152 of them code lines. Product code `src/` is 18,963 code
  lines. The tests are 175,510 code lines: unit 24,215, acceptance 151,144, other 151. So there are about **7.7
  lines of Python test code for each line of product code** (146,388 to 18,961).
- **Tests:** **19,285 cases collected** (2 deselected): **3,498 unit** in 39 folders and **15,787 acceptance** in 86
  ticket folders. The guard alone accounts for about 9,000 of them: W1-02 3,655, unit/guard about 1,100, W1-47 980,
  W2-58 808, W2-50 636, W2-84 329 and W1-04 336.
- **What is truly repeated is small.** The search found 3 groups of byte-identical test bodies (6 functions), 72
  same-file families that differ only in constants (224 functions), 6 cross-file families, and 162 groups of
  copied test helpers (403 copies, 1,878 repeated lines). Between suites, the guard's inputs overlap little. The
  case count comes from breadth (roles × tools × input forms), not from copies.
- **Proposed for the owner:** **3 deletions** (30 cases), **5 revisions** (two of them are skip-forever cases
  whose deletion is blocked because their KPI line has no other coverage), and **9 merges**. Merging takes 2 more cases out (M1, M2; M3 is optional, and M9 removes 2 or 3 after W2-54's
  revision), folds 152 functions into parametrised tables and moves the copied helpers into shared modules.
- **Nightly seconds saved** (estimate): **about 900 to 1,800 s of case time per nightly**, almost all from one merge
  (M1: W2-54's two "green here" cases each pay for a full `gov check --json` on this repository, in different
  phases). Up to about 2,500 s if the designer also folds W2-54's time-limit run into it (M1b). The deletions save
  about 1 s, because the 28 W1-01 cases are already skipped on every run. Measured case time in total is 32,298 s.
- **Lines saved** (estimate): about 1,070 from the parametrised families, about 1,500 from shared helpers and about
  110 from the deletions. That is roughly 2,700 of the tests' 175,510 code lines (1.5 %).

## Sources and how they were read

| What | Command or source | Result |
|---|---|---|
| Sizes | `python3 -I /tmp/gov-os-emg-inventory/size.py`: tracked files (`git ls-files`) for the repository groups, the files on disk for the untracked `.gov-runtime/scratch/orchestrator/tools/`. Python code lines leave out blank lines, comment-only lines and docstrings (by `ast`). Other files leave out blank lines and `#` lines. Markdown and JSON count non-blank lines. | table 1 |
| Cases | `heavy_slot.sh python3 -m pytest tests --collect-only -q -o tmp_path_retention_policy=failed -p no:cacheprovider`, `PYTHONPATH=<main tree>/src`, through the gate | `19285/19287 tests collected (2 deselected) in 11.65s`, exit 0 |
| Durations | **The nightly `log/nightly/20261102-0400/` holds no JUnit XML** (only `parallel.txt`, `serial.txt`, `run.txt`). In its place: the latest duration of each case across the 24 JUnit files of `log/close-build/*/` (2026-10-30 to 11-01) and `log/nightly/20261021-1743/`. | 19,094 of 19,285 cases have a duration, 32,298 s in total |
| That nightly's totals | `log/nightly/20261102-0400/run.txt` | parallel: 21 failed, 18,943 passed, 35 skipped, 2 errors in 3,567 s. Serial: 3 failed, 171 passed, 8 errors in 5,349 s. Wall time 19,448 s. On 10-21 the same phases took 1,906 s and 1,843 s. |
| Skips | the `<skipped>` elements of the 21 close-build JUnit files after 2026-10-30 16:16, latest result per case | 33 cases skipped: 28 W1-01, 1 W1-26, 1 W2-16, 1 W2-59, 1 W2-66, 1 unit |
| Superseded decisions | `grep -n -iE 'SUPERSEDED\|Replaces\|replaced by' docs/DECISION_REGISTER.md` (162 lines); `ARCHIVE-SUPERSEDED.md`; `packages/SWEEP-2026-10-20.md`; the product's own check `python3 -m gov.decisions.propagation` | 4 findings, all false positives (see §3) |
| Repeats | `dups.py`: an AST hash of every function body (docstring and name left out), exact and with every constant blanked; `lit.py`: string literals shared between suites | §4 |
| Dead code | `dead.py` (a name that appears as a word nowhere but its own definition, across src, tests, template, the tools and the config); module import search by `grep`; `dups.py` over `src/`. No vulture or radon: they are not installed, and nothing was installed. | §6 |

## 1. Size

Table 1. Files and lines per group.

| Group | Files | Lines (total) | Code lines (no blanks, comments, docstrings) | Python files | Python code lines |
|---|---:|---:|---:|---:|---:|
| product code (src/) | 138 | 26,154 | 18,963 | 137 | 18,961 |
| unit tests (tests/unit/) | 189 | 32,543 | 24,215 | 189 | 24,215 |
| acceptance tests (tests/acceptance/) | 1,018 | 229,598 | 151,144 | 923 | 122,022 |
| other tests (tests/ outside unit/acceptance) | 1 | 219 | 151 | 1 | 151 |
| kernel template (template/) | 167 | 14,748 | 11,458 | 6 | 792 |
| CTO tools: governance/project/orchestration/tools/ | 13 | 4,547 | 3,656 | 6 | 3,260 |
| CTO tools: docs/plan/tools/ | 2 | 703 | 586 | 2 | 586 |
| CTO tools: .gov-runtime/scratch/orchestrator/tools/ (untracked scratch) | 197 | 14,318 | 11,979 | 135 | 8,375 |

Readings of table 1:
- Acceptance tests also hold 95 non-Python files (READMEs and data), 34,933 lines. The 923 Python files are 122,022
  code lines, **6.4 times `src/`**.
- The untracked scratch tools hold 11 backup copies (`*.pre-*`, `*.retired`, `*.candidate`; 1,849 lines). They also
  hold about 78 one-off record, brief and ticket-filing scripts (`apply_dec*`, `append_dec*`, `brief_*`,
  `file_*`, `commit_*`, `resume_*` and similar; 4,035 lines). These are archival candidates (§6).


### The 20 largest files of each group

**product code (src/): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `src/gov/guard/containment.py` | 1,744 | 1,173 |
| 2 | `src/gov/guard/reads.py` | 1,502 | 1,187 |
| 3 | `src/gov/close/command.py` | 1,466 | 1,027 |
| 4 | `src/gov/guard/decide.py` | 1,222 | 886 |
| 5 | `src/gov/doctor/command.py` | 898 | 773 |
| 6 | `src/gov/secrets/__init__.py` | 606 | 403 |
| 7 | `src/gov/guard/protected.py` | 519 | 361 |
| 8 | `src/gov/close/batch.py` | 482 | 340 |
| 9 | `src/gov/close/select.py` | 476 | 326 |
| 10 | `src/gov/accept/runner.py` | 471 | 345 |
| 11 | `src/gov/store/loader.py` | 453 | 336 |
| 12 | `src/gov/adopt/stages.py` | 450 | 361 |
| 13 | `src/gov/check/runner.py` | 450 | 384 |
| 14 | `src/gov/close/nightly.py` | 433 | 335 |
| 15 | `src/gov/decisions/checker.py` | 433 | 302 |
| 16 | `src/gov/rebuild/watch.py` | 407 | 311 |
| 17 | `src/gov/check/schema.py` | 379 | 298 |
| 18 | `src/gov/context/__init__.py` | 368 | 289 |
| 19 | `src/gov/retrieval/semantic.py` | 362 | 251 |
| 20 | `src/gov/launch/launcher.py` | 358 | 256 |

**unit tests (tests/unit/): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `tests/unit/guard/test_decide.py` | 2,241 | 1,726 |
| 2 | `tests/unit/orchestration/test_dispatcher.py` | 2,203 | 1,693 |
| 3 | `tests/unit/guard/test_protected.py` | 1,185 | 990 |
| 4 | `tests/unit/containment/test_w1_50_commit_trailers.py` | 796 | 569 |
| 5 | `tests/unit/install/test_install.py` | 660 | 449 |
| 6 | `tests/unit/containment/test_probe_repairs.py` | 587 | 454 |
| 7 | `tests/unit/containment/test_dec142_and_dec143.py` | 577 | 428 |
| 8 | `tests/unit/close/test_measured.py` | 572 | 411 |
| 9 | `tests/unit/containment/test_review_fixes.py` | 520 | 365 |
| 10 | `tests/unit/orchestration/test_w2_97_merge_queue.py` | 520 | 379 |
| 11 | `tests/unit/adapters/test_portability.py` | 495 | 383 |
| 12 | `tests/unit/accept/test_w2_96_accept.py` | 437 | 340 |
| 13 | `tests/unit/guard/test_reads.py` | 431 | 351 |
| 14 | `tests/unit/release/test_release.py` | 420 | 330 |
| 15 | `tests/unit/orchestration/test_merge_queue_seed.py` | 418 | 322 |
| 16 | `tests/unit/hooks/test_w29_hooks.py` | 392 | 317 |
| 17 | `tests/unit/telemetry/test_counter.py` | 377 | 275 |
| 18 | `tests/unit/containment/test_restore_verify_and_timeout.py` | 355 | 271 |
| 19 | `tests/unit/accept/test_w2_96_review3.py` | 338 | 261 |
| 20 | `tests/unit/check/test_check.py` | 336 | 218 |

**acceptance tests (tests/acceptance/): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `tests/acceptance/W1-02/README.md` | 2,667 | 2,237 |
| 2 | `tests/acceptance/W1-30/README.md` | 2,349 | 1,948 |
| 3 | `tests/acceptance/W2-96/w2_96_support.py` | 1,682 | 1,188 |
| 4 | `tests/acceptance/W2-54/w2_54_support.py` | 1,616 | 1,061 |
| 5 | `tests/acceptance/W1-31/w1_31_support.py` | 1,601 | 1,057 |
| 6 | `tests/acceptance/W1-50/README.md` | 1,534 | 1,264 |
| 7 | `tests/acceptance/W2-69/w2_69_support.py` | 1,307 | 967 |
| 8 | `tests/acceptance/W2-72/w2_72_support.py` | 1,302 | 847 |
| 9 | `tests/acceptance/W1-30/w1_30_support.py` | 1,292 | 789 |
| 10 | `tests/acceptance/W1-29/test_session_hooks.py` | 1,175 | 819 |
| 11 | `tests/acceptance/W2-16/w2_16_support.py` | 1,138 | 789 |
| 12 | `tests/acceptance/W1-35/test_w1_35.py` | 1,033 | 715 |
| 13 | `tests/acceptance/W1-38/test_w1_38_rulesync.py` | 1,027 | 707 |
| 14 | `tests/acceptance/W1-16/w1_16_support.py` | 1,013 | 670 |
| 15 | `tests/acceptance/W1-19/w1_19_support.py` | 986 | 653 |
| 16 | `tests/acceptance/W1-21/w1_21_support.py` | 915 | 625 |
| 17 | `tests/acceptance/W2-71/w2_71_support.py` | 897 | 588 |
| 18 | `tests/acceptance/W1-26/test_w1_26_audit_validator.py` | 881 | 593 |
| 19 | `tests/acceptance/W1-03/w1_03_support.py` | 879 | 591 |
| 20 | `tests/acceptance/W1-38/README.md` | 875 | 733 |

**other tests (tests/ outside unit/acceptance): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `tests/conftest.py` | 219 | 151 |

**kernel template (template/): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `template/governance/kernel/bin/tk` | 1,510 | 1,255 |
| 2 | `template/governance/kernel/hooks/pretooluse.py` | 468 | 331 |
| 3 | `template/.rulesync/skills/openspec-explore/SKILL.md` | 361 | 265 |
| 4 | `template/.rulesync/skills/test-driven-development/SKILL.md` | 330 | 256 |
| 5 | `template/governance/kernel/skills/superpowers/test-driven-development/SKILL.md` | 330 | 256 |
| 6 | `template/governance/kernel/vendor/superpowers/skills/test-driven-development/SKILL.md` | 330 | 256 |
| 7 | `template/openspec/schemas/feature-readiness/schema.yaml` | 322 | 264 |
| 8 | `template/.rulesync/skills/openspec-sync-specs/SKILL.md` | 295 | 224 |
| 9 | `template/.rulesync/commands/opsx/sync.md` | 291 | 220 |
| 10 | `template/.rulesync/skills/systematic-debugging/SKILL.md` | 283 | 211 |
| 11 | `template/governance/kernel/skills/superpowers/systematic-debugging/SKILL.md` | 283 | 211 |
| 12 | `template/governance/kernel/vendor/superpowers/skills/systematic-debugging/SKILL.md` | 283 | 211 |
| 13 | `template/.rulesync/commands/opsx/archive.md` | 258 | 197 |
| 14 | `template/.rulesync/commands/opsx/explore.md` | 247 | 181 |
| 15 | `template/.rulesync/skills/openspec-archive-change/SKILL.md` | 215 | 168 |
| 16 | `template/governance/kernel/hooks/sessionstart.py` | 214 | 152 |
| 17 | `template/.rulesync/skills/openspec-apply-change/SKILL.md` | 207 | 160 |
| 18 | `template/governance/kernel/schemas/path-map.schema.json` | 204 | 204 |
| 19 | `template/.rulesync/commands/opsx/apply.md` | 203 | 156 |
| 20 | `template/.rulesync/skills/test-driven-development/writing-good-tests.md` | 198 | 154 |

**CTO tools: governance/project/orchestration/tools/: the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `governance/project/orchestration/tools/dispatch/dispatcher.py` | 2,372 | 1,911 |
| 2 | `governance/project/orchestration/tools/merge_queue.py` | 1,296 | 1,022 |
| 3 | `governance/project/orchestration/tools/deadman.py` | 221 | 181 |
| 4 | `governance/project/orchestration/tools/dispatch/README.md` | 188 | 183 |
| 5 | `governance/project/orchestration/tools/README.md` | 187 | 160 |
| 6 | `governance/project/orchestration/tools/gov_reranker_gpu_slot.py` | 109 | 70 |
| 7 | `governance/project/orchestration/tools/stop_waiter_check.py` | 63 | 44 |
| 8 | `governance/project/orchestration/tools/permission_request.py` | 48 | 32 |
| 9 | `governance/project/orchestration/tools/sentinel-brief.md` | 16 | 14 |
| 10 | `governance/project/orchestration/tools/dispatch/loop.sh` | 14 | 11 |
| 11 | `governance/project/orchestration/tools/dispatch/launch_now.sh` | 13 | 10 |
| 12 | `governance/project/orchestration/tools/dispatch/run_tick.sh` | 12 | 10 |
| 13 | `governance/project/orchestration/tools/win_toast.ps1` | 8 | 8 |

**CTO tools: docs/plan/tools/: the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `docs/plan/tools/validate_s1.py` | 427 | 372 |
| 2 | `docs/plan/tools/validate_w2.py` | 276 | 214 |

**CTO tools: .gov-runtime/scratch/orchestrator/tools/ (untracked scratch): the 20 largest files** (total lines / code lines)

| # | File | Lines | Code |
|---:|---|---:|---:|
| 1 | `.gov-runtime/scratch/orchestrator/tools/tooltrial_grimp_last.json` | 866 | 866 |
| 2 | `.gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py` | 730 | 623 |
| 3 | `.gov-runtime/scratch/orchestrator/tools/close_build.py.pre-reuse` | 612 | 561 |
| 4 | `.gov-runtime/scratch/orchestrator/tools/close_build.py` | 571 | 441 |
| 5 | `.gov-runtime/scratch/orchestrator/tools/close_build.py.pre-dec1001` | 534 | 489 |
| 6 | `.gov-runtime/scratch/orchestrator/tools/test_seed_store.py` | 426 | 344 |
| 7 | `.gov-runtime/scratch/orchestrator/tools/apply_dec954_edits.py` | 375 | 280 |
| 8 | `.gov-runtime/scratch/orchestrator/tools/rebuild_counts.py` | 312 | 257 |
| 9 | `.gov-runtime/scratch/orchestrator/tools/seed_store.py` | 300 | 221 |
| 10 | `.gov-runtime/scratch/orchestrator/tools/file_dec959.py` | 262 | 238 |
| 11 | `.gov-runtime/scratch/orchestrator/tools/land.py` | 251 | 199 |
| 12 | `.gov-runtime/scratch/orchestrator/tools/test_close_build.py` | 197 | 121 |
| 13 | `.gov-runtime/scratch/orchestrator/tools/land.py.pre-dec1001` | 192 | 173 |
| 14 | `.gov-runtime/scratch/orchestrator/tools/lb_measure.py` | 189 | 163 |
| 15 | `.gov-runtime/scratch/orchestrator/tools/file_dec971.py` | 186 | 163 |
| 16 | `.gov-runtime/scratch/orchestrator/tools/te_lib.py` | 167 | 131 |
| 17 | `.gov-runtime/scratch/orchestrator/tools/sweep.py` | 161 | 124 |
| 18 | `.gov-runtime/scratch/orchestrator/tools/guard_refusals.py` | 156 | 123 |
| 19 | `.gov-runtime/scratch/orchestrator/tools/guard4_check.py` | 154 | 144 |
| 20 | `.gov-runtime/scratch/orchestrator/tools/deadman.py` | 147 | 120 |

## 2. The number of tests

**Totals** (from `collect.txt`): 19,285 cases. Unit: 3,498 cases, 512 s measured. Acceptance: 15,787 cases, 31,786 s
measured. The case time is the sum of per-case durations from the latest JUnit file holding each case (it includes
setup). It is not wall time: the nightly runs the parallel phase on several workers.

**The slowest suites** (case time, the latest JUnit file per case):

| # | Suite | Cases | Seconds | Share of all measured seconds |
|---:|---|---:|---:|---:|
| 1 | acceptance/W2-69 | 352 | 4,371 | 13.5 % |
| 2 | acceptance/W2-54 | 101 | 4,216 | 13.1 % |
| 3 | acceptance/W1-30 | 537 | 3,915 | 12.1 % |
| 4 | acceptance/W1-41 | 242 | 2,159 | 6.7 % |
| 5 | acceptance/W2-50 | 636 | 1,056 | 3.3 % |
| 6 | acceptance/W1-27 | 181 | 1,029 | 3.2 % |
| 7 | acceptance/W1-07 | 224 | 1,006 | 3.1 % |
| 8 | acceptance/W1-26 | 418 | 966 | 3.0 % |
| 9 | acceptance/W1-02 | 3,655 | 926 | 2.9 % |
| 10 | acceptance/W1-16 | 167 | 875 | 2.7 % |
| 11 | acceptance/W2-68 | 22 | 715 | 2.2 % |
| 12 | acceptance/W1-04 | 336 | 660 | 2.0 % |
| 13 | acceptance/W1-50 | 685 | 535 | 1.7 % |
| 14 | acceptance/W2-107 | 43 | 512 | 1.6 % |
| 15 | acceptance/W1-47 | 980 | 405 | 1.3 % |
| 16 | acceptance/W2-66 | 170 | 393 | 1.2 % |
| 17 | acceptance/W2-84 | 329 | 390 | 1.2 % |
| 18 | acceptance/W1-35 | 166 | 390 | 1.2 % |
| 19 | acceptance/W2-07 | 69 | 384 | 1.2 % |
| 20 | acceptance/W2-108 | 27 | 381 | 1.2 % |

**The slowest single cases** (26 cases of 60 s or more, 5,894 s together). The top three each run real work over this
whole repository:
- W2-54 `test_gov_check_gives_context_reproducibility_green_here`: 1,800 s.
- W2-54 `test_gov_check_gives_core_schema_green_here`: 1,579 s. On other close builds it took 897 to 1,800 s; 1,800
  looks like the per-test ceiling.
- W2-54 `test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit`: 630 s.
- Then W2-108 `test_this_repositorys_store_is_checked_once` (209 s), W1-21's family check over both dev tiers (132 s),
  W2-68's reuse and batch closes (69 to 104 s each) and W2-77's batch (71 to 72 s).

**The nightly's growth.** On 2026-10-21 the parallel phase took 1,906 s and the serial phase 1,843 s (263 serial
cases). On 2026-11-02 they took 3,567 s and 5,349 s (182 serial cases). The 11-02 serial phase was spent mostly on
W1-19 and W1-21's real-model fixtures failing: `FACET_UNAVAILABLE: Ollama did not embed with qwen3-embedding:0.6b`,
each case rebuilding; red-alone 130 to 1,045 s per case. That is an infrastructure red, not test repetition.

Per-suite tables: unit by folder, then acceptance by ticket.


**Unit tests by folder**

| Unit folder | Files | Lines | Code lines | Cases collected | Seconds |
|---|---:|---:|---:|---:|---:|
| accept | 4 | 1,318 | 1,022 | 95 | 95 |
| adapters | 2 | 495 | 383 | 94 | 2 |
| adopt | 2 | 335 | 253 | 32 | 11 |
| bridge | 2 | 78 | 57 | 11 | 0 |
| check | 12 | 1,463 | 1,020 | 178 | 24 |
| checkpoint | 2 | 152 | 104 | 13 | 2 |
| ci | 2 | 196 | 153 | 17 | 0 |
| cli | 3 | 137 | 93 | 14 | 1 |
| close | 29 | 4,033 | 2,930 | 477 | 46 |
| closure | 2 | 99 | 71 | 6 | 0 |
| codeintel | 2 | 268 | 206 | 12 | 4 |
| containment | 11 | 3,700 | 2,685 | 114 | 24 |
| context | 5 | 334 | 240 | 41 | 0 |
| decisions | 4 | 528 | 370 | 41 | 2 |
| doctor | 2 | 292 | 219 | 45 | 0 |
| gitenv | 7 | 936 | 688 | 56 | 3 |
| guard | 16 | 5,856 | 4,584 | 1,103 | 44 |
| hooks | 4 | 867 | 666 | 75 | 2 |
| install | 2 | 660 | 449 | 144 | 18 |
| launch | 7 | 853 | 594 | 138 | 1 |
| lock | 2 | 302 | 242 | 38 | 0 |
| ollama | 2 | 73 | 51 | 3 | 0 |
| orchestration | 8 | 4,089 | 3,129 | 280 | 84 |
| pause | 3 | 328 | 241 | 23 | 1 |
| plan | 2 | 46 | 30 | 3 | 0 |
| readiness | 2 | 110 | 83 | 7 | 0 |
| rebuild | 5 | 458 | 337 | 40 | 4 |
| records | 2 | 38 | 26 | 1 | 0 |
| release | 2 | 420 | 330 | 61 | 6 |
| retrieval | 11 | 1,270 | 931 | 126 | 13 |
| retrieve | 2 | 83 | 59 | 4 | 4 |
| secrets_check | 9 | 1,125 | 830 | 67 | 116 |
| semantic | 4 | 265 | 185 | 11 | 1 |
| status | 2 | 177 | 129 | 15 | 1 |
| store | 4 | 340 | 240 | 20 | 1 |
| synthesis | 2 | 79 | 57 | 7 | 0 |
| tasks | 2 | 128 | 97 | 6 | 1 |
| telemetry | 2 | 377 | 275 | 65 | 1 |
| validate | 3 | 235 | 156 | 15 | 0 |

**Acceptance tests by ticket**

| Ticket folder | Files | Lines | Code lines | Cases collected | Seconds (sum of case durations, latest JUnit) |
|---|---:|---:|---:|---:|---:|
| (top-level) | 2 | 198 | 123 | 0 | 0 |
| W1-01 | 7 | 1,601 | 1,063 | 90 | 58 |
| W1-02 | 54 | 15,290 | 9,648 | 3,655 | 926 |
| W1-03 | 15 | 4,987 | 3,430 | 364 | 307 |
| W1-04 | 10 | 1,658 | 1,141 | 336 | 660 |
| W1-05 | 6 | 1,530 | 1,042 | 98 | 81 |
| W1-06 | 12 | 1,685 | 1,097 | 96 | 2 |
| W1-07 | 11 | 1,767 | 1,163 | 224 | 1,006 |
| W1-08 | 13 | 2,153 | 1,515 | 235 | 238 |
| W1-09 | 11 | 1,881 | 1,315 | 87 | 67 |
| W1-10 | 10 | 1,840 | 1,231 | 101 | 29 |
| W1-11 | 18 | 3,322 | 2,157 | 142 | 36 |
| W1-12 | 7 | 813 | 536 | 21 | 41 |
| W1-13 | 12 | 1,773 | 1,142 | 110 | 95 |
| W1-14 | 8 | 1,222 | 828 | 63 | 30 |
| W1-15 | 11 | 2,350 | 1,605 | 124 | 204 |
| W1-16 | 13 | 3,917 | 2,799 | 167 | 875 |
| W1-17 | 11 | 1,590 | 1,064 | 65 | 142 |
| W1-18 | 7 | 796 | 524 | 15 | 10 |
| W1-19 | 9 | 2,490 | 1,738 | 41 | 151 |
| W1-20 | 8 | 1,495 | 983 | 51 | 149 |
| W1-21 | 14 | 2,488 | 1,638 | 127 | 301 |
| W1-22 | 5 | 1,120 | 742 | 25 | 21 |
| W1-23 | 4 | 601 | 407 | 10 | 2 |
| W1-24 | 13 | 1,890 | 1,258 | 70 | 30 |
| W1-25 | 10 | 1,197 | 775 | 52 | 85 |
| W1-26 | 29 | 8,648 | 5,585 | 418 | 966 |
| W1-27 | 39 | 9,055 | 5,514 | 181 | 1,029 |
| W1-28 | 14 | 3,437 | 2,151 | 154 | 78 |
| W1-29 | 3 | 1,880 | 1,346 | 45 | 7 |
| W1-30 | 61 | 15,045 | 9,692 | 537 | 3,915 |
| W1-31 | 8 | 4,490 | 3,065 | 161 | 98 |
| W1-32 | 11 | 1,951 | 1,170 | 81 | 159 |
| W1-33 | 7 | 1,220 | 753 | 113 | 7 |
| W1-34 | 4 | 516 | 381 | 8 | 0 |
| W1-35 | 5 | 2,436 | 1,778 | 166 | 390 |
| W1-36 | 8 | 1,274 | 907 | 84 | 17 |
| W1-37 | 4 | 393 | 259 | 4 | 0 |
| W1-38 | 10 | 5,212 | 3,543 | 201 | 346 |
| W1-39 | 9 | 2,025 | 1,291 | 71 | 263 |
| W1-40 | 12 | 2,499 | 1,771 | 74 | 143 |
| W1-41 | 13 | 4,270 | 2,954 | 242 | 2,159 |
| W1-42 | 4 | 917 | 651 | 22 | 0 |
| W1-44 | 3 | 277 | 184 | 5 | 3 |
| W1-45 | 7 | 1,273 | 689 | 105 | 41 |
| W1-46 | 23 | 4,637 | 2,735 | 493 | 308 |
| W1-47 | 15 | 2,741 | 1,672 | 980 | 405 |
| W1-48 | 10 | 2,020 | 1,249 | 172 | 1 |
| W1-49 | 9 | 2,626 | 1,787 | 105 | 51 |
| W1-50 | 67 | 16,532 | 10,024 | 685 | 535 |
| W2-01 | 8 | 2,188 | 1,444 | 88 | 370 |
| W2-02 | 10 | 1,297 | 788 | 53 | 45 |
| W2-03 | 8 | 1,049 | 648 | 39 | 8 |
| W2-05 | 11 | 3,418 | 2,328 | 65 | 310 |
| W2-07 | 11 | 1,739 | 1,094 | 69 | 384 |
| W2-16 | 9 | 3,188 | 2,186 | 142 | 198 |
| W2-49 | 10 | 2,156 | 1,414 | 154 | 11 |
| W2-50 | 18 | 6,357 | 4,234 | 636 | 1,056 |
| W2-51 | 8 | 1,167 | 836 | 47 | 6 |
| W2-53 | 9 | 1,745 | 1,076 | 57 | 282 |
| W2-54 | 12 | 4,827 | 3,308 | 101 | 4,216 |
| W2-55 | 8 | 1,450 | 1,022 | 76 | 48 |
| W2-57 | 10 | 1,494 | 978 | 21 | 359 |
| W2-58 | 15 | 3,430 | 2,292 | 808 | 366 |
| W2-59 | 9 | 1,697 | 1,170 | 46 | 29 |
| W2-61 | 12 | 2,240 | 1,553 | 124 | 33 |
| W2-62 | 7 | 1,247 | 822 | 58 | 27 |
| W2-64 | 8 | 1,258 | 805 | 83 | 104 |
| W2-65 | 4 | 492 | 334 | 10 | 4 |
| W2-66 | 18 | 2,911 | 2,049 | 170 | 393 |
| W2-68 | 6 | 1,104 | 758 | 22 | 715 |
| W2-69 | 20 | 5,607 | 3,861 | 352 | 4,371 |
| W2-71 | 12 | 2,967 | 2,033 | 304 | 136 |
| W2-72 | 10 | 2,636 | 1,657 | 73 | 41 |
| W2-76 | 9 | 1,250 | 878 | 22 | 123 |
| W2-77 | 8 | 964 | 624 | 24 | 170 |
| W2-84 | 9 | 1,606 | 1,017 | 329 | 390 |
| W2-86 | 2 | 143 | 106 | 3 | 0 |
| W2-87 | 5 | 711 | 461 | 21 | 55 |
| W2-90 | 2 | 593 | 477 | 0 | 0 |
| W2-95 | 5 | 671 | 470 | 28 | 9 |
| W2-96 | 12 | 3,853 | 2,722 | 109 | 160 |
| W2-97 | 9 | 1,002 | 731 | 19 | 0 |
| W2-106 | 7 | 941 | 611 | 88 | 10 |
| W2-107 | 14 | 1,887 | 1,354 | 43 | 512 |
| W2-108 | 7 | 1,285 | 888 | 27 | 381 |

## 3. No longer needed

### 3a. Tests that enforce a superseded or replaced decision

- **The product's own check finds none that is real.** `python3 -m gov.decisions.propagation` (W2-55) at
  `3630679c74ce`, with `PYTHONPATH=src`, gives 4 findings, all `DEC-876 → DEC-880` in `tests/acceptance/W2-07/`
  (`README.md:170`, `test_w2_07_decision_records.py:129`, `w2_07_support.py:72, 80`). All four are **false
  positives**: W2-07 copies DEC-876's *status-line form* (`SUPERSEDED by DEC-n (…; it was ACCEPTED …)`) as a fixture
  shape. It does not enforce DEC-876's rule.
- **That check under-reports (a discovery).** `gov.decisions.register.read` sees only **8 superseded entries**:
  DEC-038, 048, 049, 636, 869, 875, 876 and 960. The register's own status lines still say `ACCEPTED` for entries
  that later decisions superseded or replaced:
  - DEC-947 (SUPERSEDED by DEC-953 item 1, per `ARCHIVE-SUPERSEDED.md` §A);
  - DEC-466 (by DEC-953 item 1);
  - DEC-929 items 1 and 2 (by DEC-953 item 4a);
  - **DEC-798** (`Replaces: DEC-798` in DEC-1033).

  DEC-866 item 1 says the old entry is marked at once. Until they are marked, the check cannot see tests that
  enforce them. The register itself is outside this report's write scope; see `proposed_decisions` in the return.
- **By value and by the sweep** (`packages/SWEEP-2026-10-20.md`), re-checked on `HEAD`:

| Old decision → new | Where it is still enforced on `HEAD` | State | Proposal |
|---|---|---|---|
| DEC-798 → DEC-1033 (the query embedder on the CPU only) | `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py` (14 cases), `test_w2_54_shared_gpu.py` (2) | **being revised now** by a test designer (the brief) | not listed here. The unit tests are already revised: `tests/unit/retrieval/test_semantic_cpu_embedder.py` and `test_emg_query_device.py` both say "CPU-only rule replaced by DEC-1033" (`75f18d11`). They are a merge candidate later (M9 below). |
| DEC-737, DEC-776, DEC-786 → DEC-847 → DEC-942 (a ceiling of tickets in flight; DEC-942 removed the ceiling) | `tests/acceptance/W1-35/w1_35_orchestration_support.py:110` ("a stated ceiling of tickets in flight"), behind `test_w1_35.py::test_every_clause_of_the_row_is_stated[parallel tickets]` | the sweep sent it to W2-11; still asserted | **R3: revise** (not delete: the row's other clauses stay) |
| DEC-828 item 4 / DEC-833 (CAP-10 floor 85) | `w1_19_support.py:92` and `w1_21_support.py:100`: `HIT_AT_5_PASS_LINE = 80.0` | the sweep: W2-32 raises it to 85; still 80 | **R4: revise** (W2-32) |
| DEC-636 and DEC-665 → DEC-838 (300k) | W1-49 | revised by W2-63; `grep 300000` finds it only in W2-55's own fixtures | none |
| DEC-508, DEC-525 and others → DEC-820 (reads open) | W1-02, W2-50, unit/guard | revised by W2-58 ("allowed under policy 2" cases) | none |

### 3b. Skipped tests that can never run here, and tests of retired code

From the JUnit skips (`skipped.txt`, 33 cases):

| Case(s) | Skip reason (verbatim) | Can it run? | Proposal |
|---|---|---|---|
| 28 cases of W1-01: `test_w1_01_settings_deny.py::test_implementer_write_to_acceptance_tests_is_denied` (2), `::test_acceptance_test_deny_covers_every_depth` (2), `::test_install_command_is_denied` (13), `::test_pipe_to_shell_and_sudo_are_denied` (7), `::test_guardrails_leave_ordinary_implementer_work_alone` (1); `test_w1_01_history.py::test_interim_rule_stays_in_force_once_introduced` (2), `::test_no_install_is_recorded_before_w1_05` (1); and the `interim` fixture in `conftest.py:48` | "W1-05 is closed: the interim guardrail is retired (DEC-084)" | **never**: W1-05 is closed for good | **D1: delete** |
| `tests/unit/retrieval/test_lexical.py::test_the_chunking_is_the_carried_one` | "could not import 'govbridge.core.chunking'" | never: the carried `govbridge` code is retired (DEC-017, S1; `cli/govbridge` is untracked) | **R5: revise**. Drop the comparison with the carried code. Keep its own property asserts (lines 58 to 60: every line in a chunk, size bound, empty text), which today never run because the skip comes first. |
| `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_the_path_map_s_test_inputs_are_in_the_test_map` | "the path map no longer holds test_inputs (the orchestrator's edit is done)" | never as written | **R1: revise** (deletion blocked: its KPI line has no other coverage, §5) |
| `tests/acceptance/W1-26/test_w1_26_command.py::test_exit_0_when_all_checks_green` | "the full project does not pass gov check yet" | it **costs 46 s on every run and then skips** | **R2: revise** (deletion blocked, §5) |
| `tests/acceptance/W2-16/test_w2_16_owner_terminal.py::test_the_command_refuses_on_a_terminal_under_this_suite_s_ancestry` | "this suite's own chain reaches process 1 with no Claude Code session in it … (DEC-772 item 1)" | only under a Claude Code ancestor | **keep**: DEC-772's `gov release` refusal is a feature DEC-953 keeps tested. It runs when the suite runs under a session. |
| `tests/acceptance/W2-59/test_w2_59_hook_lines.py::test_without_a_pin_the_after_call_lines_do_not_end_silently[NOTSET]` | "got empty parameter set" | yes, when the settings hold the after-call lines | keep |

**Tests of retired code:** no other case was found. The collection imports every test module without an error (exit 0,
no collection errors). `grep -rln 'testmon|pushover|govbridge|\.retired|lead_chain2' tests` finds only
`tests/unit/retrieval/test_lexical.py` (R5 above).

**Not proposed** (DEC-953): the cases of features lifted as gates (containment, the ratchet, accepted history, closes,
re-pins and similar) stay built and tested. None is on the list.


## 4. Repeats and merges, even across tickets

How they were found (`dups.py`):
- Every function in `tests/` and `src/` (15,731, of which 7,446 are test functions) is hashed by its body, with the
  docstring and its own name left out. The hash is taken twice: exactly, and with every constant blanked.
- Equal exact hashes mean the same calls and the same expectations. Equal blanked hashes mean the same shape with
  other values: a parametrisable family.
- `lit.py` compares the inputs that the guard suites pass (string literals of shell commands and paths) between
  suites.
- The candidate groups were then read by hand. Groups that the hash put together but that check other things were
  set aside, for example W1-06 and W1-48 `_entry(registry)`: different registries, different tools.

**Repeats that were confirmed by reading:**

| Id | Group (files, case ids) | Same behaviour? | Saving |
|---|---|---|---|
| D2 | `tests/unit/install/test_install.py::test_orchestrator_install_gets_ask` (line 314) and `::test_unfrozen_repo_asks_install_for_orchestrator` (line 525) | **byte-identical**: the same `_run_hook(project, "pip install requests", role="orchestrator", ticket="T-01")`, the same `== "ask"` | 1 case, 6 lines, 0.35 s |
| D3 | `tests/acceptance/W1-24/test_w1_24_family_check.py::test_the_same_ticket_and_commit_give_the_same_packet_hash` and `test_w1_24_packet.py::test_the_hash_is_stable_across_two_runs` | **identical calls and assertion**: `api.context(project, S.TK_NORMAL)[S.K_HASH]` twice, `h1 == h2`; both cite CAP-38.b | 1 case, 5 lines, 0.43 s |
| M1 | `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here` and `::test_gov_check_gives_core_schema_green_here` | **one shared fixture** (`gov_check_here`, `conftest.py:93`, session scope: one `gov check --json` on this tree). But the context case is listed in `serial-only.txt:107` (nightly route) and core-schema is not. So each nightly runs the whole `gov check` twice: once in the parallel phase for core-schema and once in the serial phase for context. Every close runs it for core-schema alone. The evidence: in the close of 2026-10-30 22:54 both ran on one worker, and the second took 0.001 s. In the latest close, core-schema took 1,579 s (897 to 1,800 s across close builds). | **merge into one case** (or route core-schema with context): 1 case, about **900 to 1,800 s per nightly** (estimate, from the close-build durations) |
| M1b | `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` | runs the context check by `sh -c` over this repository again (152 s on 11-02, 630 s on the latest close), a part of the same `gov check` | the designer judges whether `gov check`'s own run can give the measured seconds: up to 150 to 630 s (estimate) |
| M2 | `tests/acceptance/W1-45/test_w1_45_gov_runtime.py::test_scratch_stays_writable_for_orchestrator` and `test_w1_45_orchestrator_scope.py::test_orchestrator_can_write_its_checkpoint` | the same `write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET)` + `assert_allowed`; both write `.gov-runtime/scratch/orchestrator/checkpoint.json` | 1 case, 8 lines, 0.3 s |
| M3 (optional) | `tests/acceptance/W2-02/test_w2_02_code_under_test.py` and `W2-03/test_w2_03_code_under_test.py::test_the_processes_the_suite_starts_run_this_worktrees_code` | byte-identical. Six more suites assert the same `import gov; print(gov.__file__)` in fixtures (W2-16, W2-50, W2-54, W2-57, W2-58, W2-84). On the integration tree they all check the same thing. In a ticket's own worktree each guards that worktree (DEC-732). | 1 case, 0.02 s. Low value: keep unless the designers move the check to `tests/acceptance/conftest.py` |
| M7 | W1-19 (`test_w1_19_real_models.py::_one_pass`) and W1-21 (`test_w1_21_dev_tier.py::_tiers`) | each clones the dev tiers and builds their real-model vectors in its own fixture; 9 helpers are copied between the two supports | one shared session build: about 40 to 80 s per healthy nightly (estimate: on 10-21 the two suites took 87 s and 82 s). More when the embedder fails, because every case rebuilds (130 to 1,045 s per case red-alone on 11-02). |
| M9 (after the W2-54 revision) | `tests/unit/retrieval/test_emg_query_device.py` against `test_semantic_cpu_embedder.py` (both revised to DEC-1033). Overlapping pairs: `test_the_query_server_is_started_without_hiding_the_gpu` ~ `test_the_query_embedder_is_started_at_its_own_address_with_the_gpu_left_as_the_caller_has_it`; `test_a_model_not_reported_loaded_gives_no_vector_named_and_nothing_cached` ~ `test_the_device_is_read_after_the_vector_is_computed_and_a_model_not_listed_gives_no_vector` | the same public calls (`ollama` start, `semantic` query vector) with the same expectation, from two rounds | 2 to 3 cases, about 60 lines, under 1 s (estimate) |

**Parametrisable families** (the same body with other constants; `families.json`):

| Id | Where | Groups | Functions folded | Lines saved (estimate: the group's lines less one body and its table) |
|---|---|---:|---:|---:|
| M4 | 72 same-file families in total | 72 | 152 | about 1,070 |
| | of them `tests/unit/guard/test_decide.py` (for example `TestNonRoleSubagent`, `TestRedirectWithWriteCommand`, `TestCdDashAndDoubleDash`, `TestTargetResolutionDecide`: one `decide(...)` call and `== "deny"`, 3 to 13 per group) | 20 | | about 417 |
| | W1-26 (`test_w1_26_skill_validator.py`, `test_w1_26_audit_validator.py`, `test_w1_26_planted_defects.py`, `test_w1_26_dec436.py`) | 14 | | about 352 |
| | W1-35 (`test_w1_35.py`: the skill-text `TestDiscovery…` and `TestSkillRegressionRed…` classes) | 9 | | about 123 |
| | W1-36, W1-27, W1-29, unit/install, W1-30 and 14 more files | 29 | | about 180 |
| M5 | cross-file: W1-27 `test_w1_27_doctor_r5.py::test_stale_path_in_live_document_is_reported`, `test_w1_27_path_compliance_r2.py::test_stale_path_in_live_document_not_sources_is_reported` and `::test_stale_path_in_src_gov_cli_is_reported` (the same doctor run, another planted path) | 1 | 2 | about 50 |

Folding does not change the number of cases or the seconds; it changes case ids. An acceptance README that names
the functions is updated by the designer with the fold.

**Copied test helpers** (M6; exact body copies of non-test functions in more than one file): **162 groups, 403
copies, 1,878 repeated lines.** About 1,500 lines could be saved with a shared support module (estimate). The
largest:

| Helper | Copies in | Repeated lines |
|---|---|---:|
| `errors` | W1-04, W1-06 supports | 123 |
| `_make_project` | 4 files of `tests/unit/containment/` | 99 |
| `_real_mirror_folder_unchanged` | `tests/unit/{containment,guard,pause}/conftest.py` | 80 |
| `_built` / `built` (store build) | 9 copies in W1-12, W1-15, W1-16, W1-17, W1-19, W1-21, W1-22, W1-23 | 62 |
| `write` | 8 copies in W1-17 to W1-24, W2-108, W2-54; and two more families of 5 each (W1-09 to W2-05; W2-50 to W2-84) | 35 + 20 + 20 |
| `_link_sqlite_vec` | W1-19, W1-21, W1-22, W2-108 | 34 |
| `_decision` | W2-50, W2-58, W2-84 | 30 |
| `_free_port` / `_dead_port` | 7 copies in W1-18 to W2-87 | 25 |
| `commit` | 4 files of `tests/unit/orchestration/` | 24 |

The ticket pairs that share the most helpers: W1-19/W1-21 (9), W1-06/W1-48 (9), W1-21/W1-22 (7), W1-19/W1-22 (6),
W1-22/W1-23 (6), W2-50/W2-58 (5), W2-69/W2-71 (5), W1-07/W1-27 (5), W1-13/W1-14 (5).

**Found but not proposed:**
- **The guard's breadth is not copying.** Inputs shared between guard suites (`lit.py`): of W1-02's 491 literal
  inputs and unit/guard's 627, 41 are shared. W2-58 and unit/guard share 16, W2-50 and unit/guard 11, W1-04 and
  unit/install 30. No three guard suites share more than 19 inputs, mostly the generic `pip install requests` and
  `git status --porcelain`. The large counts are role × tool × form products: for example
  `test_a_listed_tool_is_let_through_for_every_actor` has 187 cases and W1-47
  `test_a_call_that_names_the_oracle_path_is_denied` has 186. Cutting them would be a coverage choice for a
  designer, not a removal of repeats.
- **Unit mirrors of acceptance cases.** 20 test names occur in both a unit file and an acceptance file, for example:
  - `tests/unit/close/test_state.py` and W1-30 `test_w1_30_r8_escalation.py` (3 names);
  - `tests/unit/adopt/test_adopt.py` and W1-41 (2);
  - `tests/unit/guard/test_decide.py` and W1-45 (2);
  - `tests/unit/close/test_measured.py` and W1-30 (2);
  - `tests/unit/check/test_audit_validator.py` and W1-26;
  - `tests/unit/cli/test_cli.py` and W1-07 and W1-26.

  They check the same behaviour at another layer (in-process against the CLI, about 0.1 s each). They are the
  engineers' regression evidence (DEC-136) and are not proposed.
- Same name, other behaviour (set aside after reading): W1-06/W1-48 registry entries; W1-15/W1-17 "registered in the
  kernel template" (two different checks); W1-30 `test_containment_clean_within_paths` against
  `test_close_refuses_on_missing_checkpoint`.

## 5. KPI coverage kept

For each proposed deletion or merge: the KPI lines its cases cover, taken from the folder's README map (its "KPI line
| Test function(s)" table) or the case's docstring, and the test that keeps covering each one.

| Id | KPI line covered (source) | Kept by, after the change |
|---|---|---|
| D1 (W1-01, 28 cases) | **Success 1** (`W1-01/README.md:21`): implementer sessions deny Edit/Write on `tests/acceptance/**` and on secret files | the secret-file part: `test_w1_01_settings_deny.py::test_write_to_secret_file_is_denied` (16 cases, they still run) and `test_w1_01_bootstrap_record.py::test_a_denied_attempt_is_recorded_for_each_path_class` (5). The acceptance-tests part, as W1-05's guard now enforces it: `W1-33/test_w1_33_guard_and_launcher.py::test_only_the_test_designer_may_write_the_acceptance_tests` (5) and `W1-02/test_w1_02_test_independence.py` (73) |
| D1 | **Success 3** (`README.md:23`): the interim install rule recorded, and in force until W1-05 | "recorded": `test_w1_01_bootstrap_record.py::test_interim_install_rule_is_recorded`, `::test_install_rule_lists_every_agent_session_settings_file`, `::test_a_denied_install_attempt_is_recorded` (still run). "In force", as the guard enforces it: `W1-04/test_w1_04_install_rule.py::test_an_install_by_any_other_role_is_denied` (15), `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied` (12), `W1-47/test_w1_47_uv_installs.py::test_engineer_test_designer_and_auditor_are_denied` (123), `W1-04/test_w1_04_sudo.py::test_sudo_is_denied_to_every_role` (30), and W1-04's cases whose ids name a pipe or `curl` (61) |
| D1 | **Failure 3** (`README.md:26`): any install runs before W1-05 | **spent**: the window ended when W1-05 closed (DEC-084). The owner retires the line as DEC-925 item 1 retired W1-01's Failure 2 (`README.md:25`). The README records it. |
| D2 (unit install) | none (unit, DEC-136) | `test_orchestrator_install_gets_ask` (the twin) |
| D3 (W1-24) | CAP-38.b, "same ticket, same commit, same packet hash" (both docstrings; W1-24's README names neither case) | `test_w1_24_family_check.py::test_the_same_ticket_and_commit_give_the_same_packet_hash` (the twin); also W2-54 Success 1 (the same hash under any retrieval order) |
| M1 | W2-54 **S3** (`W2-54/README.md:88`: context-reproducibility green here) and **S4** (`:89`: core-schema green here) | the merged case asserts both checks green from the one envelope; `test_a_red_or_missing_check_in_the_close_s_result_still_fails_the_cases` keeps the failure path |
| M1b | W2-54 **S2** (`:86`: a declared limit that fits the measured run) | the designer's choice; until then the case stays |
| M2 | W1-45 **Success 7** (`W1-45/README.md:15` and `:52`) | the merged case (both paths); `test_orchestrator_checkpoint_works_without_a_ticket` also stays |
| M3 | none (the README notes "green"; DEC-732 practice) | `tests/acceptance/conftest.py` if moved, otherwise not done |
| M4, M5 | unchanged: every folded case stays as one parameter set | the parametrised function (the README rows renamed) |
| M6 | none (helpers) | n/a |
| M7 | W1-19 success 2 / failure 1, W1-21's dev-tier lines | the same cases, from the shared build |
| M9 | none (unit, DEC-136; DEC-1033's lines are W2-54's) | the surviving file's cases |

**Deletions blocked by the rule** ("a KPI line with no other coverage blocks its deletion"):
- **R1:** W2-66 `test_the_path_map_s_test_inputs_are_in_the_test_map`. It covers "`test_inputs` moved" (DEC-896 item 2;
  `W2-66/README.md:78`, `:219`). It skips forever, and no other case asserts that the test map holds `test_inputs`.
  So the KPI line is unproven today. **Revise:** assert the test map's `test_inputs` without the path-map condition.
- **R2:** W1-26 `test_exit_0_when_all_checks_green`. It covers "exit code 0: no hard-block check is RED" (S1, CAP-39.d).
  It costs 46 s and then skips because its `full_project` fixture is not green. No other running case asserts exit
  0 on green. **Revise** the fixture so the case asserts (it then fails or passes, never skips).


## 6. The list for the owner

### 6a. Deletions, merges and revisions (tests)

Seconds are case time per full run (the nightly runs every case once), from the latest JUnit durations. Estimates are
marked "est.".

| Id | Kind | What | Reason | Cases | Lines | Seconds | KPI line kept by |
|---|---|---|---|---:|---:|---:|---|
| D1 | delete | W1-01's 28 interim cases (`test_w1_01_settings_deny.py`: 5 functions; `test_w1_01_history.py`: 2) and the `interim` fixture (`conftest.py:48`) | they enforce the interim guardrail that DEC-084 retired when W1-05 closed; they skip on every run | −28 | about −95 (est.) | about −0.04 | §5: Success 1 and 3 by the running W1-01 record cases and the guard's W1-02, W1-04, W1-05, W1-33 and W1-47 cases; Failure 3 spent (as DEC-925 did) |
| D2 | delete | `tests/unit/install/test_install.py::test_unfrozen_repo_asks_install_for_orchestrator` | byte-identical to `test_orchestrator_install_gets_ask` | −1 | −6 | −0.35 | the twin |
| D3 | delete | `tests/acceptance/W1-24/test_w1_24_packet.py::test_the_hash_is_stable_across_two_runs` | the same calls and assertion as `test_w1_24_family_check.py::test_the_same_ticket_and_commit_give_the_same_packet_hash` | −1 | −5 | −0.43 | the twin (CAP-38.b) |
| M1 | merge | W2-54 `test_gov_check_gives_context_reproducibility_green_here` + `test_gov_check_gives_core_schema_green_here` → one case (or both on one route of `serial-only.txt`) | one `gov check --json` on this repository is paid twice per nightly, once per phase | −1 | about −10 | **about −900 to −1,800 (est.)** | the merged case (S3, S4) |
| M1b | merge (the designer judges) | W2-54 `test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit` reads its seconds from M1's run | the same context check over this repository again | 0 | small | about −150 to −630 (est.) | S2 by the case as changed |
| M2 | merge | W1-45 `test_scratch_stays_writable_for_orchestrator` + `test_orchestrator_can_write_its_checkpoint` | the same writes, same expectation, one path in common | −1 | −8 | −0.3 | Success 7 |
| M3 | merge (optional) | W2-02 / W2-03 `test_the_processes_the_suite_starts_run_this_worktrees_code` | byte-identical; one check of the code under test | −1 | −8 | −0.02 | `tests/acceptance/conftest.py` |
| M4 | fold | 72 same-file families (152 functions) into parametrised tables; 20 in `tests/unit/guard/test_decide.py`, 14 in W1-26, 9 in W1-35 | the same body with other values | 0 (ids change) | about −1,070 (est.) | 0 | unchanged |
| M5 | fold | W1-27's 3 stale-path cases in 2 files | the same doctor run, another planted path | 0 | about −50 (est.) | 0 | CAP-06.d, unchanged |
| M6 | share | 162 copied helper groups (403 copies) into shared support modules | copies of one helper | 0 | about −1,500 (est.) | 0 | n/a |
| M7 | share | W1-19 / W1-21 real-model dev-tier build into one session build | the same build twice | 0 | about −60 (est.) | about −40 to −80 (est.; more when the embedder fails) | unchanged |
| M9 | merge (after W2-54's revision) | `tests/unit/retrieval/test_emg_query_device.py` into `test_semantic_cpu_embedder.py` | two rounds' cases of the same query-embedder calls | −2 to −3 | about −60 (est.) | under −1 | n/a (unit) |
| R1 | revise | W2-66 `test_the_path_map_s_test_inputs_are_in_the_test_map` | skips forever; its KPI line has no other coverage | 0 | ~0 | 0 | itself, once revised |
| R2 | revise | W1-26 `test_exit_0_when_all_checks_green` | 46 s then a skip; its KPI line has no other coverage | 0 | ~0 | up to −46 if the fixture is made small | itself, once revised |
| R3 | revise | W1-35 `test_every_clause_of_the_row_is_stated[parallel tickets]` ("a stated ceiling of tickets in flight", `w1_35_orchestration_support.py:110`) | enforces DEC-737/776/786, replaced by DEC-847 then DEC-942 (the sweep's W2-11 item, not done) | 0 | ~0 | 0 | the row's other clauses |
| R4 | revise | W1-19 / W1-21 `HIT_AT_5_PASS_LINE = 80.0` | DEC-833's CAP-10 floor is 85 (the sweep's W2-32 item) | 0 | ~0 | 0 | the same cases |
| R5 | revise | `tests/unit/retrieval/test_lexical.py::test_the_chunking_is_the_carried_one` | the carried `govbridge` code is retired; its own property asserts never run behind the skip | 0 | about −2 | 0 | itself |
| — | in progress, not listed | W2-54 `test_w2_54_cpu_embedder.py` (14), `test_w2_54_shared_gpu.py` (2) | DEC-798 replaced by DEC-1033 | | | | the designer now revising them |

**Totals proposed:**
- Cases: −32 from D1 to D3, M1 and M2 (−33 with M3, about −35 with M9).
- Lines: about −2,700 (est.) of 175,510 test code lines.
- Seconds: about −900 to −1,800 per nightly from M1 (est.), up to about −2,500 with M1b and M7. Of 32,298 s of
  measured case time, that is 3 to 8 %.

### 6b. The code's own candidates (for the senior engineer)

Found by static search:
- `dups.py`: an AST hash of function bodies over `src/` (exact, and with constants blanked).
- `dead.py`: a name that appears as a word nowhere but its own definition, across src/, tests/, template/, the three
  tool folders, `pyproject.toml`, `copier.yml` and `lefthook.yml`.
- `grep` for module imports and helper names.

No vulture or radon: they are not installed, and nothing was installed.

1. **Frontmatter parsers: 15 definitions in 13 modules.**
   - `_frontmatter` is byte-identical in `src/gov/check/{mutation,authority,claims,runner,graph}.py`, 13 lines each.
   - `_parse_frontmatter` is identical in `check/audit_validator.py:31` and `check/skill_validator.py:40`.
   - Others in `check/schema.py:75`, `store/loader.py:233` (with `frontmatters`), `close/traceability.py:19`,
     `adopt/project.py:121`, `tasks/tickets.py:14`, `guard/decide.py:63`, and the status-only
     `retrieval/retrieve.py:63`.
   - Saving: one shared parser, about 100 lines (est.).
2. **Git wrappers: 14 (`_git` / `git`) in 12 modules**:
   - `decisions/checker.py:76`, `store/loader.py:74`, `retrieval/lexical.py:63`, `close/repo.py:28`,
     `pause/command.py:48`, `adopt/project.py:51`, `doctor/command.py:114`, `ci/command.py:123`,
     `release/__init__.py:49`, `guard/containment.py:98` and `:940`, `checkpoint/record.py:30`, `guard/reads.py:375`
     and `:1086`.
   - `store/loader._git` and `retrieval/lexical._git` have the same shape.
   - These differ in return type (bytes, str, CompletedProcess), so they can be merged only with care: the guard's
     copies are on its hot path.
3. **`_ids`** is byte-identical in `check/authority.py:30`, `check/claims.py:35` and `check/graph.py:31`.
4. **The SQLite `_open`** has the same shape in `retrieval/semantic.py:247` and `retrieval/lexical.py:84`.
5. **sha256 helpers: 3**: `doctor/command.py:99 _sha256_file` (identical to `lock/__init__.py:115 _sha256`) and
   `adopt/project.py:31 sha256`.
6. **Dead by name:** `src/gov/close/evidence.py:22 junit_rel` (3 lines) is referenced nowhere. The other hits were
   pytest hook functions, which pytest calls by name.
7. **Reached only by tests:**
   - `src/gov/retrieval/synthesis.py` (W1-23, CAP-15.f; `synthesize`, `validate_notes`): no `src/` module or CLI
     command imports it. Only `tests/unit/synthesis/` and W1-23 reach it. A built feature: kept under DEC-953 unless
     the owner decides otherwise. It is listed so the engineer knows it is unwired.
   - `src/gov/decisions/backfill.py`: W2-55's one-off backfill, run as `python -m`.
   - `src/gov/accept/command.py` and `src/gov/release/command.py`: imported nowhere by name, but loaded by the CLI's
     `importlib` table (`cli/main.py:162`). Not dead.
8. **CTO tools (not product):** archival candidates in the untracked `.gov-runtime/scratch/orchestrator/tools/`:
   - 11 backup copies (`*.pre-*`, `*.retired`, `*.candidate`; 1,849 lines);
   - about 78 one-off record and brief scripts (4,035 lines).

   `src/` has few exact copies. 4 groups, 84 repeated lines, are identical. With constants blanked there are 5
   groups and 96 lines. The code's cost is the many near-copies of small helpers, not large duplicated blocks.
