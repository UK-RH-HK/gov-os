# Lens I, area 2: `gov close`, the checks and the ratchet — a test review against the specifications in force

Independent assessment of the Gov OS, October 2026 (DEC-889 item 16).

## In brief

- **What was reviewed.** Area 2 holds 2,264 test cases in 1,459 functions: nine acceptance suites and six builder-test folders. They take a quarter of the regression's case time (3,864 of 15,260 case-seconds in the rehearsal). I gave a verdict to 418 functions (733 cases, 31 % of the area's case time):
  - every test on the ratchet's two lists, the serial-only list and the Wave 2 failure records of the area;
  - lens H's duplicate candidates;
  - every suite whose feature a later decision changed;
  - every case a static scan showed as possibly unable to fail;
  - a seeded sample of 86 of the rest.
  27 planted faults (23 changes, 4 of them run again over a whole suite) in my clone tested whether the suspect cases can fail.
- **Most of the area is sound.** 306 of the reviewed functions are valid and needed, among them 78 of the 86 sampled. The later rounds of W1-30, the W2-01 and W2-53 suites and the builder tests hold each gate of the close with a project built to show it. Of the 23 faults, 16 were caught by them.
- **The lists' entries cannot all leave** (findings 1 and 12; P-I2-1).
  - The two accepted reds read the frozen Wave 1 exit record, which their fix tickets W2-13 and W2-14 cannot reach.
  - W2-57, which 28 of the 32 `load_sensitive` entries wait for, cannot reach the fix of four of them as planned.
  - Once W2-19 lands, those tickets cannot close while the entries remain.
- **58 weak tests** (findings 2, 3 and 7), almost all in the first rounds of W1-30 and W1-26:
  - ten W1-30 round-1 cases are refused for a missing checkpoint, or assert only `ok`, whatever the gate they name does;
  - W1-26's base project is red before any defect is planted (R1). So its 26 planted-defect cases that assert only `gov check`'s overall exit pass with the very check silenced (PF20), and so do eight derived-scope cases, five whose assertion is always true, and one whose own declaration is invalid YAML, so its check never runs;
  - they hid a real fail-open: the path-map check measures nothing on every real path map (row W2-M214). That row is triaged to W2-23, which cannot reach the check (P-I2-4, an entry criterion of W2-27).
- **Seven faults are caught by nothing in area 2:**
  - the owner disposition dropped, and a refusal that no longer says the context failed;
  - the path-map check measuring nothing, and the ratchet's field rule dropped (lens H's finding 19);
  - a constant packet hash (PF9b: none of W1-30's 512 cases or `tests/unit/close`'s 386 catches it);
  - the runner ignoring the readiness check's answer or error.
- **16 outdated**, each naming its decision (findings 4 and 9):
  - W2-53's load-sensitive cases (DEC-762, for W2-19);
  - W1-30's serial-list cases (W2-57);
  - the acceptance-folder and collection-error cases (W2-07);
  - the regression-scope case (W2-66);
  - the hooks case (W2-08, already in its card).
- **23 flaky, with the cause measured** (findings 8 and 10, §2.3): the `secrets` package's three files (its name shadows the standard library's: 3 of 3 collection errors with the import first, 26 passed without); W1-30's r13 case (its 5-second limit is shorter than a loaded start: failed alone once in three); W1-15's bound case (a 15-second latency bound: failed in its suite's parallel run 3 times in 4, and alone once when the load rose to 82). **10 not reproducible** (finding 5, §2.2): the nine nested-run unit cases that failed in the trials' worksteal runs passed my six runs, and the unit follow-up case passed all six.
- **Duplicates:** 4, one of them AST-identical. **Obsolete:** 1. **Not reproducible:** 10.
- **Of today's four finished closes, three were refused, each for a reason inside area 2** (findings 9, 10, 11 and 13). The fourth, W2-62's re-close (16:44), passed with no list entry needed.
  - W2-63's close (00:11) was refused for three reasons, which led to DEC-892:
    - it had no acceptance folder: a test-revision ticket, whose declared path W2-07 is to read (DEC-892 item 1, finding 9);
    - W1-38's third rulesync case;
    - W1-46's `[static.crates.io]` case.
  - The owner's new `load_sensitive` entry counted for nothing in W2-50's close, because its decision did not name the test's file. No test reads the real lists against the register.
  - W2-58's close was refused for seven decision-record commits on the path map, which its allowed paths name.
  - Both were knowable from the commits before a test ran, yet each close spent about 70 minutes first.
- **For W2-68,** area 2's record-reading tests are missing from DEC-889's declared set. Under same-code reuse they would fail open (finding 6, P-I2-2, an entry criterion).
- **For W2-66,** §4.1 maps each suite's measured reach against its owner's paths.
  - W1-26 runs every check's module, and W1-30 the checkpoint, decision and closure code.
  - W1-42 and W1-48 run no code at all.
  - `tests/unit/validate` names no package.
- **Seven owner packages** (§6): the lists' route out (P-I2-1), the record-reading set (P-I2-2), where the revisions go (P-I2-3), a carrier for W2-M214 (P-I2-4), and three retirements (P-I2-5 to P-I2-7).

## 1. Header

| | |
|---|---|
| **Area** | 2: `gov close`, the checks and the ratchet. Acceptance suites W1-26, W1-30, W1-31, W1-40, W1-42, W1-15, W1-48, W2-01, W2-53; builder tests `tests/unit/close`, `check`, `secrets`, `ci`, `telemetry`, `validate`: 2,264 cases, 1,459 test functions (my collection in the clone) |
| **Author** | an independent auditor (`GOV_ROLE=independent-auditor`, Opus 5.5, effort max), started by the Wave 2 orchestrator on the owner's order (DEC-889 item 16). I wrote none of the work assessed. I did not read the other three areas' work (their folders under `/tmp` were not opened) |
| **Date** | 2026-10-22, from 09:34 (my first file) to 19:05 BST (the report written) |
| **Head assessed** | `w2/integrate` at `4166d8d9ca0b6f7450a961d121eb69095375f491` (2026-10-22 00:16, DEC-891), the head when I started; every run used that commit. The head moved during my session; I read these later commits read-only: `8d625805` (DEC-892, 09:48), `49c24ac9` (the owner's `load_sensitive` entry of DEC-892, 09:49), `0a75ac72` (W2-50's checkpoint before its close, 10:14), `da3d77e1` (DEC-893 and DEC-894, 11:52), `bddd22f6` (W2-58's checkpoint before its close, 12:05) |
| **Branches read** | `w2/integrate`; `w2/W2-49` at `19d45246` (Contract v4.2); `record/w2` at `75604472` (the raw orchestration record: the close-queue logs, which I read in their scratch copies under `.gov-runtime/scratch/orchestrator/log/` and checked against the branch) |
| **Contract** | v4.2, read on `w2/W2-49` (not yet merged into `w2/integrate`, which holds v4.1). For the 18 capabilities of area 2 (CAP-01, 03, 04, 13, 23, 24, 25, 28, 30, 31, 38, 39, 40, 50, 53, 58, 59, 61) the two versions are identical in `contract.yaml`; the capability files differ only in their version line |
| **Decisions** | `docs/DECISION_REGISTER.md` at `4166d8d9` (887 entries, to DEC-891), DEC-892 at `8d625805`, and DEC-893 and DEC-894 at `da3d77e1` (11:52). An entry marked SUPERSEDED, or "Changed by" for a part, was judged by the newer entry |
| **The `gov` I used** | none of the pinned `gov` on PATH (`~/.local/bin/gov`, wheel of `fecb870c`) for any measure. Every run and every reading of code is **my clone's own code**: `PYTHONPATH=/tmp/gov-os-assessment-I2/repo/src` |

**What I read.**
- **Code:** `src/gov/close/` (all of it), `src/gov/check/pathmap.py`, `schema.py`, `graph.py`, `src/gov/secrets/__init__.py` (the reuse of DEC-853), `src/gov/rebuild/command.py`, the parts of `src/gov/retrieval/` a full rebuild calls.
- **Tests:** every README, conftest and support module of the nine suites; every test function named in §2 in full; the remaining functions by name, docstring and assertion through static scans of my own (`scripts/weak_scan.py`, `cond_scan.py`, `no_checkpoint_scan.py`, `dupes_area.py`, `repo_state.py`).
- **Records:** the three close records under `docs/close/`; every close log of the orchestrator (`log/close-*.json`, `close-queue-*/`, `W2-01-close.json`, `sweep-close-DAEO-7rr2.json`); the rehearsal (`log/nightly/20261021-1743/`, with JUnit XML); the orchestrator's tool trials of 2026-10-22 (`log/tooltrials/20261022-0017/`, with JUnit XML, and its report in `8d625805`); DEC-866's sweep (`governance/project/orchestration/packages/SWEEP-2026-10-20.md`); the ticket files of W2-07, W2-08, W2-12, W2-13, W2-14, W2-19, W2-23, W2-66; the Wave 2 WBS, list and triage rows named here; lens H's report and its evidence folder (`/tmp/gov-os-assessment-H/`: the ever-failed list, the duplicate scan, the measured who-tests-what map, the allowed-paths map, the mutation results).
- **Decisions:** DEC-042, 372, 416, 425, 436, 447, 454, 463, 470, 479, 480, 482, 483, 487, 490, 492, 495, 497, 500 to 502, 505, 507, 512, 514, 516, 527, 549, 554, 566, 567, 581, 595, 612, 613, 627, 628, 655, 663, 665, 677, 704, 706, 709, 712 to 714, 717, 718, 724, 726, 734, 736, 739, 746, 750, 754, 757, 760, 762, 766, 768, 780, 801 to 803, 808, 809, 813, 818, 822, 823, 825, 835, 843, 844, 852, 853, 861, 862, 864, 866 to 894, 897 (the evidence note of W2-62's re-run).

**Every command, by kind.**
- **Reads of the repository and the records** (any load, no gate): `git` `log`, `show`, `status`, `diff`, `rev-parse`, `ls-files` and `clone --no-hardlinks` (into my folder), the file, Grep and Glob tools, and `ls`, `stat`, `grep`, `sed`, `cut`, `tail`, `ps`. Python scripts of my own, run with `python3 -I`, read the JUnit files, the close logs and the register (`scripts/`, `dec.py`).
- **Runs in my clone**, each behind my gate (below):
  - one full `gov rebuild` (09:35:46 to 10:06:24, with embeddings);
  - 31 pytest runs of suites and cases (the table below);
  - 27 planted-fault runs through `scripts/plant.py` (the table below; a lock stopped one once, and it ran again);
  - `gov check --json` in three fixture projects of W1-26 (R1), and `python3 -m gov.secrets` in one of them;
  - six `gov retrieve` questions and one `--continue`;
  - six one-process runs of `tests/unit/secrets`.
- **No `gov` command that writes ran on the repository.** No tool was installed and no setting changed.

**What I ran, and where.** Every run: in my clone (`git clone --no-hardlinks` of the repository into `/tmp/gov-os-assessment-I2/repo`), from an empty environment (`env -i`), with `HOME` and `TMPDIR` in my folder, git's identity by variables, and a private `/tmp` (`bwrap --dev-bind / / --bind <mine>/faketmp /tmp --bind <mine> <mine>`), so nothing was written outside `/tmp/gov-os-assessment-I2/` (`run.sh`). Each test run started behind my gate (1-minute load under 20, `MemAvailable` at least 6,710,886 kB, neither `CLOSE-RUNNING` nor `NIGHTLY-RUNNING`), checked in the same command (`gate.sh`), and from 10:07 on was also stopped if a lock appeared while it ran (`runsuite.sh`). Every run kept JUnit XML (`logs/<label>.xml`) and its start and end load (`logs/<label>.meta`).

The test runs, in the order they started (`scripts/run_table.py` over `logs/*.meta`):

| Run | What ran | Start | End | Wall s | Load at start, end | Result | Gate waits (34 s each) |
|---|---|---|---|---|---|---|---|
| `unit-par1` | unit/close unit/check unit/secrets unit/ci unit/telemetry unit/validate, parallel | 09:48:48 | 09:48:59 | 12 | 12.59, 13.03 | 639 passed in 11.34s | 0 |
| `w1-42-alone1` | W1-42 | 09:49:08 | 09:49:09 | 0 | 12.78, 12.78 | 2 failed, 22 passed in 0.09s | 0 |
| `w2-53-par1` | W2-53, parallel | 09:51:04 | 09:51:33 | 29 | 6.53, 10.72 | 57 passed in 25.20s | 0 |
| `w2-01-par1` | W2-01, parallel | 09:51:39 | 09:52:25 | 46 | 10.22, 13.79 | 88 passed in 42.17s | 0 |
| `w1-30-par1` | W1-30, parallel | 09:52:29 | 09:56:36 | 248 | 13.09, 18.95 | 512 passed in 223.98s (0:03:43) | 0 |
| `w1-26-par1` | W1-26, parallel | 11:40:42 | 11:42:01 | 79 | 5.22, 18.35 | 412 passed, 1 skipped in 71.37s (0:01:11) | 0 |
| `w1-31-par1` | W1-31, parallel | 11:42:01 | 11:42:19 | 18 | 18.35, 19.44 | 161 passed in 13.43s | 0 |
| `w1-40-par1` | W1-40, parallel | 11:42:19 | 11:42:43 | 24 | 19.44, 31.95 | 74 passed in 22.78s | 0 |
| `w1-15-par1` | W1-15, parallel | 11:44:57 | 11:45:49 | 52 | 18.71, 55.84 | 1 failed, 123 passed in 47.21s | 4 |
| `w1-48-par1` | W1-48, parallel | 11:48:03 | 11:48:09 | 6 | 18.03, 20.35 | 6 failed, 166 passed in 2.87s | 4 |
| `plant-PF1-dispositions-owner-dropped` | W1-30/test_w1_30_disposition.py unit/close, parallel | 11:48:43 | 11:49:08 | 26 | 15.96, 19.15 | 402 passed in 20.08s | 0 |
| `plant-PF2-context-failure-unsaid` | W1-30/test_w1_30_disposition.py W1-30/test_w1_30_receipt.py W1-30/test_w1_30_context_failures.py, parallel | 11:49:08 | 11:49:58 | 50 | 19.15, 31.42 | 47 passed in 44.62s | 0 |
| `plant-PF3-pathmap-measures-nothing` | W1-26 unit/check, parallel | 11:51:05 | 11:53:07 | 122 | 17.03, 39.29 | 542 passed, 1 skipped in 106.49s (0:01:46) | 2 |
| `plant-PF4-containment-skipped` | W1-30/test_w1_30_close.py W1-30/test_w1_30_containment_places.py unit/close, parallel | 13:32:05 | 13:33:19 | 74 | 19.27, 59.87 | 16 failed, 410 passed in 64.42s (0:01:04) | 5 |
| `plant-PF5-acceptance-run-skipped` | W1-30/test_w1_30_close.py unit/close, parallel | 13:57:12 | 13:57:38 | 26 | 3.77, 9.80 | 1 failed, 418 passed in 24.67s | 43 |
| `plant-PF6-ratchet-field-rule-dropped` | W2-53 unit/close/test_ratchet.py, parallel | 13:57:38 | 13:58:34 | 55 | 9.80, 28.23 | 63 passed in 45.98s | 0 |
| `plant-PF7-schema-ignores-tickets` | W1-26/test_w1_26_derived.py W1-26/test_w1_26_planted_defects.py W1-26/test_w1_26_dec436.py unit/check, para… | 13:59:41 | 14:00:44 | 63 | 17.47, 30.03 | 1 failed, 170 passed in 55.20s | 2 |
| `plant-PF8-graph-measures-nothing` | W1-26/test_w1_26_derived.py W1-26/test_w1_26_planted_defects.py W1-26/test_w1_26_decisions.py W1-26/test_w1… | 14:02:21 | 14:03:07 | 45 | 19.65, 23.98 | 3 failed, 174 passed in 37.09s | 3 |
| `plant-PF9-packet-hash-constant` | W1-30/test_w1_30_receipt.py, parallel | 14:03:37 | 14:03:56 | 20 | 16.86, 21.68 | 18 passed in 15.59s | 1 |
| `plant-PF10-decision-checker-ignored` | W1-30/test_w1_30_iteration.py W1-30/test_w1_30_r8_escalation.py unit/close/test_state.py, parallel | 14:04:30 | 14:05:29 | 59 | 19.09, 20.28 | 4 failed, 83 passed in 50.44s | 1 |
| `plant-PF11-regression-stops-at-first-failure` | W1-30/test_w1_30_close.py W1-30/test_w1_30_r9_every_finding.py unit/close, parallel | 14:05:59 | 14:06:47 | 47 | 19.44, 23.81 | 15 failed, 414 passed in 38.61s | 1 |
| `plant-PF12-regression-failures-ignored` | W1-30/test_w1_30_close.py unit/close, parallel | 14:07:54 | 14:08:24 | 30 | 18.88, 21.29 | 3 failed, 416 passed in 29.42s | 2 |
| `plant-PF13-trailer-gate-off` | W1-30/test_w1_30_close.py W1-30/test_w1_30_r8_commits.py unit/close, parallel | 14:08:58 | 14:10:35 | 97 | 19.97, 40.70 | 6 failed, 428 passed in 84.83s (0:01:24) | 1 |
| `plant-PF15-task-matched-as-substring` | W1-30/test_w1_30_close.py unit/close/test_repo.py unit/close, parallel | 14:15:03 | 14:15:29 | 26 | 19.63, 21.33 | 1 failed, 418 passed in 24.54s | 8 |
| `plant-PF16-regression-never-run` | W1-30/test_w1_30_close.py unit/close, parallel | 14:16:03 | 14:16:33 | 30 | 18.46, 21.26 | 14 failed, 405 passed in 25.57s | 1 |
| `plant-PF17-schema-measures-nothing` | W1-26/test_w1_26_dec436.py W1-26/test_w1_26_derived.py W1-26/test_w1_26_planted_defects.py unit/check, para… | 14:17:06 | 14:17:52 | 46 | 16.68, 23.39 | 22 failed, 149 passed in 41.69s | 1 |
| `plant-PF18-count-not-reset` | W1-30/test_w1_30_iteration.py, parallel | 14:19:33 | 14:20:16 | 44 | 18.96, 23.28 | 1 failed, 31 passed in 39.70s | 3 |
| `plant-PF19-outcome-reveals-iteration` | W1-30/test_w1_30_iteration.py, parallel | 14:21:24 | 14:22:17 | 53 | 19.68, 23.95 | 1 failed, 31 passed in 43.52s | 2 |
| `plant-PF20-every-check-but-index-freshness-silenced` | W1-26, parallel | 14:22:51 | 14:26:19 | 209 | 18.76, 84.13 | 34 failed, 378 passed, 1 skipped in 190.22s (0:03:10) | 1 |
| `plant-PF21-gov-check-always-fails` | W1-26 unit/check W1-07/test_w1_07_envelope.py, parallel | 14:35:27 | 14:37:38 | 131 | 15.88, 25.60 | 1 failed, 577 passed, 1 skipped in 119.57s (0:01:59) | 0 |
| `plant-PF22-readiness-answer-ignored` | W1-26/test_w1_26_dec436.py unit/check, parallel | 14:39:19 | 14:39:42 | 24 | 18.74, 16.43 | 146 passed in 18.83s | 3 |
| `plant-PF23-readiness-error-swallowed` | W1-26/test_w1_26_dec436.py unit/check, parallel | 14:39:42 | 14:40:16 | 34 | 16.43, 19.31 | 146 passed in 29.44s | 0 |
| `plant-PF24-commands-check-measures-nothing` | W1-26 unit/check, parallel | 14:40:16 | 14:42:09 | 113 | 19.31, 26.21 | 7 failed, 535 passed, 1 skipped in 99.67s (0:01:39) | 0 |
| `plant-PF5b-acceptance-run-skipped-whole-W1-30` | W1-30, parallel | 14:42:43 | 14:47:08 | 266 | 17.98, 42.68 | 88 failed, 421 passed, 3 errors in 238.41s (0:03:58) | 1 |
| `plant-PF12b-regression-failures-ignored-whole-W1-30` | W1-30, parallel | 14:48:16 | 14:56:19 | 483 | 17.41, 33.63 | 8 failed, 504 passed in 430.87s (0:07:10) | 2 |
| `plant-PF16b-regression-never-run-whole-W1-30` | W1-30, parallel | 14:57:56 | 15:04:20 | 384 | 16.23, 46.31 | 28 failed, 484 passed in 343.16s (0:05:43) | 3 |
| `plant-PF9b-packet-hash-constant-whole-W1-30.stopped-1` | W1-30 unit/close, parallel | 15:06:01 | 15:11:20 | 319 | 18.82, 45.42 | **stopped by a lock**; run again | 3 |
| `fl-nested-alone1` | unit/close/test_parallel_runs.py unit/close/test_run_and_record.py unit/close/test_measured.py::test_an_acc… | 16:46:13 | 16:46:49 | 36 | 15.52, 24.27 | 34 passed in 29.92s | 0 |
| `fl-nested-alone2` | unit/close/test_parallel_runs.py unit/close/test_run_and_record.py unit/close/test_measured.py::test_an_acc… | 16:47:56 | 16:48:34 | 38 | 17.22, 32.42 | 34 passed in 33.57s | 2 |
| `fl-nested-alone3` | unit/close/test_parallel_runs.py unit/close/test_run_and_record.py unit/close/test_measured.py::test_an_acc… | 17:00:14 | 17:00:47 | 34 | 16.65, 26.98 | 34 passed in 28.41s | 21 |
| `fl-followup-alone1` | unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it | 17:06:54 | 17:07:01 | 7 | 17.38, 17.67 | 1 passed in 2.07s | 11 |
| `fl-followup-alone2` | unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it | 17:07:01 | 17:07:05 | 4 | 17.67, 18.01 | 1 passed in 2.10s | 0 |
| `fl-followup-alone3` | unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it | 17:07:05 | 17:07:09 | 4 | 18.01, 18.17 | 1 passed in 2.05s | 0 |
| `fl-w115bound-alone1` | W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder | 17:07:09 | 17:07:19 | 10 | 18.17, 22.89 | 1 passed in 8.70s | 0 |
| `fl-w115bound-alone2` | W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder | 17:07:53 | 17:07:59 | 6 | 19.85, 19.78 | 1 passed in 4.59s | 1 |
| `fl-w115bound-alone3` | W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder | 17:07:59 | 17:08:36 | 37 | 19.78, 82.40 | 1 failed in 26.84s | 0 |
| `fl-r13-alone1` | W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_wr… | 17:20:52 | 17:21:12 | 20 | 19.15, 23.99 | 1 passed in 17.95s | 22 |
| `fl-r13-alone2` | W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_wr… | 17:23:27 | 17:23:50 | 24 | 18.41, 19.00 | 1 passed in 17.89s | 4 |
| `fl-r13-alone3` | W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_wr… | 17:23:51 | 17:24:07 | 16 | 19.00, 29.39 | 1 failed in 13.44s | 0 |
| `fl-unitclose-par1` | unit/close, parallel | 17:25:14 | 17:25:40 | 26 | 18.65, 41.30 | 386 passed in 20.44s | 2 |
| `fl-unitclose-par2` | unit/close, parallel | 17:26:47 | 17:27:01 | 14 | 15.65, 29.14 | 386 passed in 13.33s | 2 |
| `fl-unitclose-par3` | unit/close, parallel | 17:28:08 | 17:28:24 | 16 | 15.93, 19.83 | 386 passed in 14.08s | 2 |
| `fl-w115-par1` | W1-15, parallel | 17:28:24 | 17:29:43 | 79 | 19.83, 67.22 | 124 passed in 65.04s (0:01:05) | 0 |
| `fl-w115-par2` | W1-15, parallel | 17:31:21 | 17:32:24 | 63 | 17.71, 56.52 | 1 failed, 123 passed in 53.22s | 3 |
| `fl-w115-par3` | W1-15, parallel | 17:37:23 | 17:39:39 | 136 | 14.69, 137.52 | 1 failed, 123 passed in 118.90s (0:01:58) | 9 |
| `fl-w130-par1` | W1-30, parallel | 17:49:07 | 17:55:45 | 399 | 18.20, 48.60 | 512 passed in 355.76s (0:05:55) | 17 |
| `fl-w130-par2` | W1-30, parallel | 17:59:40 | 18:04:28 | 287 | 16.69, 21.32 | 512 passed in 257.19s (0:04:17) | 7 |
| `fl-w130-par3` | W1-30, parallel | 18:33:56 | 18:39:39 | 343 | 18.67, 26.97 | 512 passed in 305.75s (0:05:05) | 53 |
| `plant-PF9b-packet-hash-constant-whole-W1-30` | W1-30 unit/close, parallel | 18:40:40 | 18:46:59 | 380 | 17.30, 17.65 | 898 passed in 339.54s (0:05:39) | 1 |

The runs outside `runsuite.sh`, each behind the same gate (times from `logs/part_a.log`, `part_c.log`, `rebuild.log`):

| Run | What ran | Start | End | Load at start, end | Result |
|---|---|---|---|---|---|
| rebuild | `gov rebuild`, full, with embeddings, in my clone | 09:35:46 | 10:06:24 | 0.75, 25.60 | exit 0 |
| R1 | `gov check --json` in three W1-26 fixture projects (`scripts/w126_baseline.py`) | 11:40:37 | 11:40:42 | 5.58, 5.22 | each exit 3 (§2.7) |
| R1b | `python3 -m gov.secrets` in R1's base project | 11:48:01 | 11:48:02 | 16.29 | exit 1: no `.gitleaks.toml` |
| secrets 1 | `tests/unit/secrets` after `import secrets`, one process | 14:29:08 | 14:29:09 | 18.73 | 3 errors |
| secrets control 1 | the same without the import | 14:34:11 | 14:34:34 | 17.16 | 26 passed |
| secrets 2, 3 | the same as secrets 1 | 16:44:50, 16:45:38 | 16:45:03, 16:45:38 | about 14 | 3 errors each |
| secrets control 2, 3 | the same as control 1 | 16:45:03, 16:45:38 | 16:45:38, 16:46:13 | about 14 | 26 passed each |
| retrieve ×6 | `gov retrieve <question> --batch-size 8 --json` | 14:34:34 | 14:34:40 | 15.77, 14.91 | exit 0 each; 16 pieces of evidence each |
| retrieve --continue | `load_sensitive`, with the first answer's token | 14:36:56 | 14:36:57 | 19.37 | no evidence: both facets "stale", because a fault was planted in the tree |
| retrieve --continue | the same, on the clean clone | 17:06:31 | 17:06:32 | 18.98 | 16 pieces of evidence |

**Retrieval** (the brief's `gov retrieve`, in batches). Six questions ran on my clone's store (rebuilt in full at 09:35 to 10:06, with embeddings), each with `--batch-size 8`, giving two batches and 16 pieces of evidence. Each stopped with `BUDGET_EXHAUSTED_WITH_GAPS` and named its gaps. One ran on with `--continue <token>`.
- **"W2-M214"** answered: the triage row and W2-23's ticket (`.tickets/DAEO-kmcr.md`). That is the record finding 3 rests on: the row is triaged to a ticket that cannot reach the check.
- **"W2-L373"** and **"W2-57"** answered: the list row, and W2-57's card in the WBS.
- **"accepted_reds"** answered the code and test half: `src/gov/close/ratchet.py`, `command.py`, the four W2-53 files, the unit ratchet test and W2-53's ticket. It left W2-19's ticket as a gap.
- **"load_sensitive"** brought the WBS, the list, the W2-53 test and the ratchet. Its continuation (17:06) gathered W2-19's ticket, CAP-03 and the unit ratchet test.
- **"record-reading"** brought the support modules that read records and one probe record.
- **What retrieval did not answer:** in all eight answers, the register appeared only as DEC-891, its newest entry. DEC-757, DEC-760, DEC-762, DEC-813 and DEC-889, which carry these rules, came from my text search of the register (`dec.py`).
- **A refusal that was right.** My first continuation (14:36) ran while a planted fault was in my clone's tree. Both facets answered "stale", and retrieval gave no evidence rather than answer from a store that no longer matched the tree.

**Limits of this review.**
- **Not run, by rule:**
  - W1-46's 23 `load_sensitive` entries: live Claude sessions spend the owner's usage and write under `~/.claude/`.
  - W1-48's six `local_only` machine cases. They look for the CLI under `HOME`, which in my isolated environment is my folder, and they failed there (`w1-48-par1`: 6 failed, 166 passed). I read the machine instead (`readlink ~/.local/bin/claude`, the VS Code extension index) and took their result from the rehearsal, where all six passed.
  - W1-19's real-model `load_sensitive` case: it loads the shared embedder and reranker that every close and lead uses.
- **Not run, for time.** The close queue's locks and the other auditors' runs left my gate open for short spells only. I left out:
  - the four entries of other areas' suites on `load_sensitive` (W1-02's and W1-05's p95 cases, W1-38's three rulesync cases, W1-07's `doctor` case). They are judged by their records in §2.2;
  - PF10b (PF10 over the whole W1-30 suite);
  - a run of the whole area in parallel. The flaky verdicts use the brief's definition of "under load": the case inside its own suite's parallel run.
- **The machine was shared.** Other auditors ran beside me: their processes showed in `ps`, and I opened none of their folders. Their runs raised the load after my gate had passed several times: up to 82 during an "alone" run of W1-15's bound case, and up to 137 at the end of a W1-15 parallel run. Each such run gives its end load, and every timing verdict names the loads it rests on.
- **My runs and the close queue.** I started nothing while a lock existed. Two runs had started before the queue set its lock at 09:52:43, while it was still waiting for five quiet minutes: my full rebuild (09:35:46 to 10:06:24; it was in its store phase when the lock appeared) and W1-30's parallel run (09:52:29 to 09:56:36). Both overlapped the queue's wait for quiet; neither overlapped a close's own runs (W2-50's started at 10:28:38). From 10:07 every run of mine stops itself when a lock appears.
- **The close queue held the machine for most of the day.** Its lock was set from 09:52:43 to 11:40:23 (W2-50), from about 11:53 to 13:28:18 (W2-58), from about 13:35 to 13:56:51 (W2-62, stopped before its close), and from 15:11:20 to 16:44:41 (W2-62's re-close). Other auditors' runs filled the gaps, often keeping the 1-minute load above 20. So my runs waited at my gate for most of the afternoon:
  - part A was stopped at its two-hour limit at 13:30 while PF4 waited, and I restarted the rest;
  - a lock stopped PF9b once, at 15:11, and it was started again;
  - I stopped part B at 15:22 while it only waited, and ran its rest as part C.
  No run of mine overlapped a close's runs.
- **Time data** come from the rehearsal's JUnit files (2026-10-21, `dbd3cc53`, the close's form), not from a close record: a close records counts per run, not per test.
- **No tool installed**, no setting changed. `gov retrieve` ran on my clone's store (see §1, "Retrieval").
- **Refusals met: 6, all by the guard's Bash hook, none of a read.**
  - Refusal 1 (morning): a here-document whose `>=` the guard read as a write into the repository.
  - Refusal 2 (morning): a here-document the guard could not read: "the command cannot be read, so it is not known to be free of the lift form of gov pause (--off): refused (DEC-409)".
  - Refusal 3 (12:42): a `grep` whose pattern held backticks and escaped brackets, refused with the same words.
  - Refusal 4 (14:35): a here-document, refused by the hook's parser ("Parser skipped input between top-level statements"). The command did not run.
  - Refusal 5 (16:46) and refusal 6 (18:47): an inline `python3 -c` with backticks inside its quotes, refused with refusal 2's words. Refusals 2, 3, 5 and 6 are one kind: the hook does not parse a command whose quotes hold backticks, so it refuses it rather than let through what it cannot read. That is the guard failing closed, as DEC-409 means it to.
  - I took each and did not retry it. I wrote those scripts into my folder with the file tool, and searched and edited with the Grep and Edit tools instead.
  - The guard's root-search refusals (DEC-508, until W2-58 lands): none met.

### Terms used

- **`gov close`, a close.** The Gov OS command that closes a ticket. It checks the ticket's commits (their trailers, their containment, a probe record for a FULL ticket), runs the ticket's own acceptance tests, then every other test of the repository (**the regression**), then the cases of the serial-only list one by one (**the serial run afterwards**), judges every red against the two ratchet lists, and writes a **close record** under `docs/close/<ticket>/`. A **refused close** exits 3, counts one iteration and opens a repair ticket; at three the ticket is escalated and only an owner decision lifts it. "Could not measure" (a tree that is not its commit, a stale store) exits 1 and counts nothing.
- **Acceptance suite.** The tests an independent test designer writes for one ticket, before the code, in `tests/acceptance/<ticket>/`, with a README that maps each KPI line to its tests.
- **Builder or unit tests.** The engineer's own tests, in `tests/unit/`. They are regression evidence only (DEC-042, CAP-38.c).
- **KPI line.** One success or failure line of a ticket's acceptance criteria. A test "claims" what its KPI line, its name and its docstring say it checks.
- **`gov check`, a check, a family.** `gov check` runs every declared governance check (a YAML declaration with a command) and reports each check and each of 17 **families** RED, YELLOW or GREEN. A **hard-block** check that is RED makes `gov check` exit non-zero and refuses a close of a ticket that changed a governance file (DEC-480). **G0 to G6** are the tiers a check belongs to (G1 and G2 at commit, G3 at push; CAP-39.a).
- **Path map.** `governance/project/path-map.yaml`: every tracked path's namespace, the close's settings, the trailers base, the accepted history and the two ratchet lists.
- **The ratchet and its two lists** (DEC-757). **`accepted_reds`**: owner-accepted known reds, each by exact test id with its decision, reason and fixing ticket (`fixed_by`); a listed red does not refuse a close, any other red does, and a listed test that passes refuses until its entry is removed. **`load_sensitive`**: tests that fail under parallel load and pass alone; a listed test that fails is run again alone in the same close and counts only if it then passes. Only an owner's `Role: owner` commit adds an entry (DEC-862 (a)); both lists only shrink (DEC-766); every entry names its fix (DEC-762).
- **Serial-only list.** `tests/acceptance/serial-only.txt`: cases that never run in the parallel regression (latency, real model or daemon, live session, race), but alone afterwards (DEC-372, DEC-527). 55 entries, 263 cases.
- **Pre-close gate.** The orchestrator's checks before each close (DEC-868): collection in one process, a fresh rebuild and `gov check`, a fresh checkpoint, the four record-reading test files (gate (f)), and since DEC-892 a network check. Its script holds the lock file `CLOSE-RUNNING` while a queue of closes runs (**the quiet window**, DEC-780).
- **Rehearsal.** The orchestrator's full run of 2026-10-21 17:43 to 19:00 on the slim tree (`dbd3cc53`), with JUnit XML: the parallel regression and the serial run, the close's form without a ticket (DEC-888). Its per-test durations are the time data of this report.
- **Record-reading set** (DEC-889 item 2). The tests that read the repository's own records (the register, the path map, the tool registry, ticket files, probe records). They must run on every head, because a record-only commit can turn them red while the code is unchanged.
- **W2-66, W2-68.** The two tickets that will change what a close runs: **W2-66** a path-scoped regression (only the suites a change can reach; the **shared core** always runs everything), **W2-68** batched closes and **same-code reuse** (a close on code identical to the last passing run reuses that run; the **code fingerprint** leaves record-only paths out). DEC-880, DEC-883, DEC-889, DEC-890.
- **W2-57.** The planned ticket that takes load out of the close and fixes the load-sensitive entries; it has a card and no ticket file yet.
- **Planted fault.** A one-place change to the product code in my clone, to see whether a test that claims to catch that fault fails. The file is restored byte for byte afterwards (checked by hash).
- **Owner package.** A decision put to the owner in DEC-818's six parts.
- **The two classification lines** (DEC-808): `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work" justifies a round (DEC-801).
- **Fails open, fails closed.** A gate **fails open** when it lets through what it should stop (a check GREEN on a broken rule, a close that cites a passing run on a red head). It **fails closed** when it stops what it should let through (a refused close for a ticket that did nothing wrong). This report writes "Consequence: other (fails closed …)" for the second.
- **A round; an entry criterion.** A **round** is a further iteration of a ticket's work to repair what failed (DEC-801). A risk that is real only once a planned feature is switched on becomes an **entry criterion** of the ticket that switches it on (DEC-803), instead of a round now. A fix that fits a ticket that resumes anyway **rides along** in it (DEC-802).
- **My gate.** Before each of my test runs: the 1-minute load under 20, `MemAvailable` at least 6,710,886 kB, and neither lock file present (`gate.sh`).

### The verdict scale

Each reviewed test gets one of the seven verdicts of the brief:

| Verdict | Meaning in this report |
|---|---|
| **valid and needed** | it checks a behaviour the Contract or a decision in force requires, and it can fail for the fault it names |
| **outdated** | a decision in force changed the expected behaviour; the decision is named. "Outdated when X lands" marks a test that holds today and that a planned, decided change will turn red unless it is revised with that change |
| **obsolete** | the feature it tests was removed or replaced |
| **duplicate** | another test checks the same thing in the same way; that test is named |
| **weak** | it cannot fail for the fault it claims to catch; shown by a planted fault, or by its fixture (a project that is refused for another reason) |
| **flaky** | it fails and passes on the same code; the cause found by running it alone and under load |
| **not reproducible** | it failed in a recorded run, and I could not make it fail |

A test I could not run is marked **not run** with its reason; that is a limit, not a verdict.

## 2. The verdict table

One row per test reviewed; a parametrised test is one row (its parameter sets share its verdict unless the row says otherwise). "Proposal and carrier" is filled for every verdict but "valid and needed". Each run named here ran in my clone with the clone's own code; its time, load and result are in §1's run table.

### 2.1 The accepted reds (W1-42's two)

| Test | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]` | W1-42, DAEO-gjjf (closed, DEC-717) | **valid and needed** (a known red, rightly listed) | red alone in my clone, 0.09 s: "RETR-X-02.json: no named parent expansion (DEC-091)"; red in every Wave 2 close (`CL-DAEO-7rr2`, `CL-DAEO-zflj`, `CL-DAEO-0rfi`, `CL-DAEO-juee` and the refused ones) and in the rehearsal; reads `docs/plan/wave-1-exit/evidence/RETR-X-02.json`, unchanged since `ca426ca9` (2026-10-16) | DEC-713, DEC-714, DEC-718 item 11 (closes on a kept bundle with a named parent expansion, or on the owner's ruling, `EXIT-REPORT.md:37`), DEC-757 | its route out is blocked (finding 1): the owner rules Q-1, and W2-13's KPI names this case for its test designer (P-I2-1) |
| `…::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme` | W1-42 | **valid and needed** (a known red, rightly listed) | red alone: "docs/plan/wave-1-exit/evidence/governance-share.json does not exist"; red in every close and the rehearsal | DEC-713, DEC-718 F-M1 ("… and W1-42's share case green") | W2-14's KPI asks for it green, but its allowed paths cannot reach the two files it reads (finding 1, P-I2-1) |

### 2.2 The load-sensitive entries

`load_sensitive` held 31 entries (43 cases) at `4166d8d9`, and 32 (44 cases) from the owner's commit `49c24ac9` (DEC-892, 09:49). The list is area 2's; the tests on it are mostly other areas'. For each entry I give the test's verdict where I could run it, and the entry's own standing.

| Entry (test) | Owner of the test | Verdict on the test | Evidence (my runs, records) | Rests on | The entry, and what to do |
|---|---|---|---|---|---|
| `tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` (5 cases) | W1-02 (area 1) | not run (limit: the queue's locks left no time for other areas' cases) | never failed in a Wave 2 close (lens H's ever-failed list; the queue logs); it is also on the serial-only list, so the close runs it alone afterwards | DEC-372, DEC-757, fix W2-M332 (Wave 3; target before W2-24, DEC-890) | keep, by the records. On both lists, its `load_sensitive` entry adds nothing while the serial run takes it; the entry can leave with W2-M332 |
| `tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook` (9 cases) | W1-05 (area 1) | not run (the same limit) | failed in W2-01's close (2026-10-17, `[Read-no-role]`) and in Wave 1 (W1-32, W1-02R8); on the serial-only list since, and green in every close since | DEC-372, DEC-757, W2-M332 | keep, by the records; the same remark |
| `tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95` | W1-19 (area 3) | not run | it asks the shared embedder and reranker, which every lead and close uses; I left it out (limit); passed in the rehearsal's serial run and in every Wave 2 close | DEC-372, DEC-757, W2-M332 | entry stays until DEC-889 item 5 moves its file, serial-only too, to the nightly (finding 14, P-I2-1 C); its fix row W2-M332 has the target "before W2-24 starts" (DEC-890) |
| W1-46's 23 entries (`test_w1_46_live_sessions.py`: 6 named cases and 17 allowlist hosts) | W1-46 (area 1) | not run | live Claude sessions: they spend the owner's usage and write under `~/.claude/`, which this audit may not (limit). Records: 23 setup errors under load in W2-03's run 2 (DEC-760); 20 of 23 passed alone in the blocker sweep (2026-10-18), 3 failed alone with the machine not quiet (DEC-780); `[static.crates.io]` failed in the run and alone in W2-63's close (2026-10-22 00:11), traced to the host's reachability (DEC-892 item 3) | DEC-760, DEC-762, DEC-813 (fix W2-M364 → W2-57, before W2-24) | entries stay until W2-57 (DEC-813). The file has been serial-only since 2026-10-08, so each entry is a second try alone, and DEC-889 item 5 moves the file to the nightly (finding 14, P-I2-1 C). `[static.crates.io]`'s stated reason is not its latest cause (finding 10). W2-57 has no ticket file yet |
| `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it` | unit close, W1-30 | **not reproducible** | alone ×3: passed, 2.0 to 2.1 s (17:07, load 17 to 18). In `tests/unit/close`'s parallel run ×3: passed (17:25 to 17:28, load 15 to 41 by the end). Records: failed once in Wave 1 (W1-30 G2) and once in W2-53's review (`-n 8`, DEC-762 item 4) | DEC-762 item 4, fix W2-L352 (Wave 3; target before W2-24) | the entry can stay to W2-L352 at no cost. My six green runs are evidence for removing it with W2-57's list work, a removal the orchestrator may commit (DEC-861) |
| `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project` | W1-30 | **flaky, cause found: its 5-second limit** | alone ×3: passed twice in 17.9 s (17:21, 17:23). Once it failed in 13.3 s (17:24, load 19 at the start, 29 at the end): "the fixture is wrong: the case had not begun when the run was cut". The case gives the close `--timeout 5` (`LIMIT_S = 5`, `:184`). Under load the parallel run's workers start more slowly than that, so the run is cut before the case begins, and the case's own premise fails (`:221`). This is W2-M384's question settled: its timing, not a process the close leaves alive. In W1-30's parallel run ×3 (17:49, 17:59 and 18:33; load 17 to 19 at the start, 21 to 49 at the end): passed each time, in 18.9 to 19.2 s. So it fails on a loaded start of its own close, not on the suite's parallel run as such. Records: failed once in W2-53's re-close (2026-10-19 12:01, load about 25) | DEC-823, fix W2-M384 (W2-57) | keep the entry until W2-57's test designer gives the case a limit and a sleep that a loaded start meets, keeping it a run cut while its case runs (`Rewrite-Reason: W2-M384`) |
| `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` | W1-38 | not run (the same limit as W1-02's) | `RULESYNC_FAILED` in W2-53's close (2026-10-20 12:30); both DEC-871 cases green alone (7 passed in 13.7 s). The cause is recorded: `rulesync --version` gets 10 s (`src/gov/adapters/portability.py:38`) | DEC-871, fix W2-57 | keep until W2-57, whose planned paths do not reach the probe or the tests (finding 12, P-I2-1 B) |
| `…::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` | W1-38 | not run (the same limit) | Wave 1 (W1-30 K, W1-30-final) and W2-53's close (2026-10-20) | DEC-871, W2-57 | the same |
| `…::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]` (added at `49c24ac9`) | W1-38 | not run (the same limit) | `RULESYNC_FAILED` in W2-63's close (2026-10-22 00:11). Its entry was refused by the ratchet in W2-50's close (R-2: DEC-892's text did not name the file, finding 11), and counts since `da3d77e1` | DEC-892 item 2, DEC-894, W2-57 (its first item) | the same |
| `tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | W1-07 (area 4) | not run on its own (the same limit). PF21's run took W1-07's envelope cases in parallel, with a fault planted in `gov check`'s exit, not `gov doctor`'s: `[doctor]` passed in 7.7 s (14:37, load 25 to 28) | red in W2-02's closes (2026-10-21 15:36, 17:26), green alone (DEC-886). `gov doctor` probes tool versions with 5- and 10-second limits (`src/gov/doctor/command.py:136, :143, :204`) | DEC-886, W2-57 | keep until W2-57, whose planned paths do not reach the doctor's probes (finding 12, P-I2-1 B) |

### 2.3 The serial-only entry of area 2

| Test | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `tests/acceptance/W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder` | W1-15, DAEO-7nne | **flaky, cause found: machine load** (a 15-second latency bound) | alone ×3: passed in 8.6 s and 4.6 s (17:07, load 18 to 23), and failed in 26.6 s when other runs raised the load from 20 to 82 during it. In W1-15's parallel run, four times (11:45, 17:29, 17:32, 17:39): failed at 15.9 and 15.8 s and once more, and passed once at 13.5 s, with the load at 56 to 137 by the end. Records: 3.4 s in the rehearsal's serial run, and it never failed in a close | DEC-595, DEC-600 (a bound the scan of one file after another misses); DEC-889 item 5 ("latency tests stay alone") | none: it is rightly serial-only, and it holds only in the close's quiet window (DEC-780). W2-57's serial rework keeps it alone |

### 2.4 Other tests that failed in Wave 2's closes, the rehearsal or the orchestrator's trials

| Test | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `tests/unit/secrets/test_scan_scale.py`, `test_secrets.py`, `test_token_rule.py` (26 cases; collection) | unit secrets (W1-15, W1-16, W2-50) | **flaky** (collection order) | collection errors in W2-53's close of 2026-10-20 08:38 and in all five tool-trial runs. Reproduced in my clone: with the standard library's `secrets` imported before collection, "3 errors in 0.56s", "'secrets' is not a package"; without, "26 passed in 22.15s"; 3 of 3 each way (runs 2 and 3 at 16:45, load 14); green in every other close and in my unit run (639 passed) | CAP-03.a; row W2-L373 | the folder renamed (W2-L373), by the engineer, before plugins that import `secrets` join the nightly (DEC-892 d) |
| The nested-run class of `tests/unit/close` (15 functions start a real nested `pytest` with a 60 s limit, `scripts/nested_scan.py`; 9 failed in the trials: `test_parallel_runs.py::test_a_run_is_parallel_and_states_itself`, `::test_a_declared_case_runs_afterwards_in_no_worker_and_a_case_named_alike_stays_parallel`; `test_run_and_record.py::test_a_passing_run_has_no_finding_and_its_counts`, `::test_every_failing_test_is_a_finding`, `::test_a_collection_error_is_a_finding`, `::test_no_test_collected_is_a_finding_unless_the_run_may_be_empty`, `::test_skipped_tests_are_counted_and_are_no_finding`, `::test_the_switch_that_removes_assertions_does_not_reach_the_run`; `test_measured.py::test_an_acceptance_run_in_which_no_test_passed_is_a_finding`) | unit close, W1-30 | **not reproducible** in my runs (the failure mode is recorded) | tool trials at `4166d8d9`: 5 red under worksteal (b2), 9 under worksteal with pytest-timeout (a-cost), 1 under a shuffled order (d2), each "the test run of tests exceeded the time limit of 60s". My runs: the two files and the third case alone ×3 (34 passed each, 16:46 to 17:00, load 15 to 32 by the end; slowest nested case 10.2 s), and `tests/unit/close` in its own parallel run ×3 (386 passed each, 17:25 to 17:28; slowest nested case 12.4 s). The trials ran them beside the whole regression's heaviest cases under worksteal, which my runs of their suite do not | DEC-527, DEC-549 | bounded nested runs (one worker, or a limit a loaded machine meets), an engineer's builder-test change in W2-67, before worksteal returns (DEC-892 a); no list entry |
| W1-26 `test_w1_26_decision_citations.py::test_a_decision_file_records_its_id[no-type-id-in-grammar]`, `test_w1_26_decision_register_and_base.py::test_a_heading_after_a_closed_fence_records_its_id`, `test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`; unit check `test_check.py::test_schema_clean_record`, four `test_citations.py` cases, `test_schema_audit_report.py::test_the_other_types_of_w2_02_stay_unknown`; unit close `test_every_finding.py::test_a_test_run_with_findings_is_a_finding_of_the_tickets_work`, two `test_gates.py` cases, one `test_measured.py` case | W1-26, W1-30 and their unit folders | valid and needed | red only in leads' runs while their own tickets changed this code (W2-02, W2-03, W2-48, W2-53, W2-59; lens H's `ever_failed.json`, `lead_other`); green in every close since, and in my runs (W1-26: 412 passed and 1 skipped; the six unit folders: 639 passed). The `test_measured.py` case was renamed since; today it is `test_a_merge_of_the_ticket_is_measured_against_gits_own_merge_of_its_parents` | the tickets' own rounds | none |

### 2.5 Lens H's "never failing" and duplicate candidates in area 2

Lens H found 99 % of the estate never failing in any recorded run (A1), and three groups of identical bodies. "Never failing" says nothing about whether a test *can* fail; that is what the planted faults of §2.7 and the sample of §2.8 test. Here are the duplicate candidates in area 2.

| Test | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `tests/acceptance/W1-48/test_w1_48_claude_code.py::test_claude_code_is_recorded_in_the_registry` | W1-48, DAEO-0qs5 | valid and needed | lens H's group of identical bodies with W1-06's `test_ccusage_is_recorded_in_the_registry`: the bodies match, but the module constant `NAMES` differs (`claude code` against `ccusage`), so they check two different entries | CAP-25.d | none |
| `…::test_the_recorded_install_command_installs_the_pinned_version` | W1-48 | valid and needed | the same, against W1-06's ccusage case | CAP-25.d, DEC-197 | none |
| six pairs of one name in W1-30 and `tests/unit/close` (`test_a_change_under_each_governance_prefix_has_the_checks_run`, `test_a_decision_recorded_before_the_escalation_began_lifts_none`, `test_a_decision_that_lifted_one_escalation_lifts_no_second`, `test_a_file_no_commit_holds_lifts_no_escalation`, `test_a_judgement_of_pass_or_passed_is_accepted`, `test_a_ticket_tool_that_fails_on_closing_leaves_nothing_that_says_the_ticket_closed`) | W1-30 and its unit folder | valid and needed | one behaviour held at the two layers DEC-042 separates: the acceptance case through `gov close`, the builder case through the function | DEC-042, CAP-38.c | none |
| `tests/acceptance/W1-30/test_w1_30_close.py::test_close_runs_containment_check` | W1-30, DAEO-2lwj | **duplicate** and weak | its body is AST-identical to `test_close_runs_acceptance_tests` in the same file (`scripts/dupes_area.py`): a green ticket closes; PF4 (containment never judged) passes it, while 16 cases catch PF4 | CAP-13.a | retire (P-I2-5) |
| `tests/acceptance/W1-26/test_w1_26_decisions.py::test_duplicate_id_flagged` | W1-26 | **duplicate** | the same fixture and assertion as `test_w1_26_planted_defects.py::test_planted_graph_defect_duplicate_id` (two records of one id, `assert_red`), other ids | CAP-38.b | the revision of §2.7 rewrites one to assert the graph check's `DUPLICATE_ID` finding; the other may then go with the owner's word |
| `tests/acceptance/W1-26/test_w1_26_command.py::test_gov_check_json_returns_the_api_0002_envelope` | W1-26 | **duplicate** | of W1-07's `test_every_command_returns_the_envelope[check]` (`w1_07_support.py:84, :115`), and of every W1-26 case, each of which parses the envelope through `support.envelope_of`; its skip on NOT_IMPLEMENTED is dead since `gov check` was built | API-0002 | keep: about a second a close. No retirement is proposed; one would be the owner's |
| `tests/acceptance/W1-30/test_w1_30_close.py::test_close_returns_api_0002_envelope` | W1-30 | **duplicate** | of `test_close_succeeds_on_green_standard_ticket` in the same file: the same green project, whose `support.result_of` asserts the envelope, `ok` and exit 0 (`w1_30_support.py:769-774`); dead skip as above | API-0002 | the same |

### 2.6 Suites of closed tickets whose feature a later decision changed

Every suite of area 2 belongs to a closed ticket, and each feature was changed by later decisions. For each change, the tests that encode it:

| Test(s) | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `test_w1_30_r14_probe_later_commits.py::test_a_commit_of_the_tickets_own_side_after_the_probed_one_that_changes_its_ticket_file_refuses` | W1-30 | valid and needed | rewritten `49e4aca0` (`Rewrite-Reason: DEC-757 item 3`): the commit is the engineer's, and the refusal stays; passed in my run | DEC-757 item 3, DEC-581 | none |
| `test_w1_30_r13_owner_decision_register.py` (7 cases) | W1-30 | valid and needed | an escalation lift stays the owner's `Role: owner` commit; DEC-866's sweep kept :164 with that reason | DEC-483, DEC-862 (a) | W2-12 revisits it under DEC-862 (b) |
| `test_w1_30_r13_trailers_base.py` (12), `tests/acceptance/W2-01/test_w2_01_trailers_base.py` (15) | W1-30, W2-01 | valid and needed | the base of the check (DEC-482, DEC-579) and then of the close's gate (DEC-704); W2-01's README: no earlier case reversed | DEC-482, DEC-704 | none |
| `tests/acceptance/W2-01/test_w2_01_accepted_history.py` (25) | W2-01, DAEO-g0ip | valid and needed | the decision's status and text decide (`src/gov/close/history.py:116-146`), not who committed the path-map entry; W2-01's README holds the committer "not held"; DEC-891's standing rule (an entry for a code commit stays the owner's own commit) is held by no test and no code yet | DEC-734, DEC-891 | W2-12 carries DEC-891's class (its ticket file names it) |
| `tests/acceptance/W2-53/test_w2_53_load_sensitive.py` (5 functions, 6 cases) | W2-53, DAEO-7rr2 | **outdated when W2-19 lands** | entries built without `fixed_by` (`w2_53_support.py:181-182`), DEC-757's form; DEC-762 item 1 requires `fixed_by` and W2-19's KPI refuses an entry without it (`.tickets/DAEO-jzvg.md:94`); green today (57 passed) | DEC-762 items 1 and 2 | W2-19's test designer adds `fixed_by` (`Rewrite-Reason: DEC-762 item 1`); P-I2-3 |
| `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py` (5 functions, 29 cases) | W1-30 | valid and needed; **outdated when W2-57 lands** | it holds today's serial-only entries one by one (W1-16's daemon cases, W1-09's races, the live and model files); W2-57 is to move daemon and race cases into the parallel run and live and model cases to the nightly (DEC-889 item 5) | DEC-372, DEC-514, DEC-527; DEC-889 item 5 | W2-57's draft names it for revision (finding 9) |
| `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases) | W1-30 | valid and needed; **outdated when W2-07 lands** | today a ticket without `tests/acceptance/<wbs>/` is refused (`command.py:751-761`); DEC-892 item 1 makes W2-07 read a ticket's declared `acceptance_tests.path` (test-revision tickets such as W2-63) | DEC-480, DEC-892 item 1 | W2-07's card names it (finding 9) |
| `test_w1_30_close.py::test_collection_error_refuses_close`; and the unit `tests/unit/close/test_run_and_record.py::test_a_collection_error_is_a_finding`, whose one verdict is §2.4's (not reproducible), with this note | W1-30 | valid and needed; **outdated when W2-07 lands** | today a collection error is a counted finding after the runs; DEC-868 item 3 makes it a gate refusal before any test that "spends no ratchet attempt" | DEC-868 item 3 | W2-07's card names them (finding 9) |
| `test_w1_30_close.py::test_regression_includes_other_acceptance_folders` | W1-30 | valid and needed; **outdated when W2-66 lands** | it expects another ticket's failing suite to refuse the close; a scoped close runs that suite only if the change reaches it | DEC-880 item 2 | W2-66's card names it (finding 9) |
| `test_w1_30_r11_rebuild_mode.py::test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` | W1-30 | valid and needed | `STORE_STALE` one commit later (a file under `notes/`, which a code fingerprint keeps) | DEC-487, DEC-530; DEC-883 item 4 | W2-68's test designer re-reads it against the two fingerprints (DEC-889 item 2) |
| `test_w1_30_r11_parallel_runs.py` (12) | W1-30 | valid and needed | the parallel form as built; DEC-889 item 11 a's worksteal is deferred by DEC-892 a | DEC-527, DEC-549, DEC-566 | none |
| `tests/acceptance/W1-40/test_w1_40_workflow_text.py::test_no_lefthook_hook_is_installed_in_this_repository` | W1-40, DAEO-fdkq | valid and needed; **outdated when W2-08 lands** | it reads this repository's hooks folder; the hooks are off (DEC-712); DEC-718 F-M4 and W2-08's KPI restate it so that installed hooks are the expected state | DEC-712, DEC-718 F-M4 | already in W2-08's ticket file |
| `test_w1_40_ci_unmeasured.py` (6) | W1-40 | valid and needed | a step whose tool is not on the runner says "unmeasured" and fails; CI's test step is still red by design (W2-43 open, Q-8) | DEC-494, DEC-497 | none |
| `tests/acceptance/W1-26/test_w1_26_installed_kernel.py` (31) | W1-26 | valid and needed | rewritten `c7827891` under DEC-746 (a type with no schema file is unmeasured, never green) | DEC-746 | none |
| `test_w1_26_policy.py::test_…` and W1-30's `test_w1_30_r15_policy_pairs.py`, `test_w1_30_r16_*` | W1-26, W1-30 | valid and needed (but W1-26's `test_a_new_policy_key_with_no_check_and_not_informational_is_red`: see §2.7) | rewritten under DEC-620 and DEC-627 | DEC-613, DEC-620, DEC-627, DEC-628 | none |
| `tests/acceptance/W1-15/test_w1_15_parallel_scan.py` (8), `test_w1_15_check_time_limit.py` (24) | W1-15 | valid and needed | DEC-853's reuse of a clean result by hash (W2-50, merged `98effadc`) does not touch them: each case builds a fresh project with no record of earlier scans; my W1-15 parallel run: 123 passed, and the bound case failed, as a serial-only case may in a parallel run (§2.3) | DEC-595, DEC-600, DEC-853 | none |
| `tests/acceptance/W1-48/test_w1_48_*.py` (172) | W1-48 | valid and needed | the pin is 2.1.292 (DEC-649) and `~/.local/bin/claude` points at 2.1.292 (read by `readlink`, not run); the VS Code extension is 2.1.306, which DEC-210 counts as drift for `gov doctor`, not a failure. The README's "State today" (2.1.288) is stale text | CAP-25.d, CAP-61.e, DEC-210, DEC-214, DEC-649 | none (the README's line is a P3 text fix) |
| `tests/acceptance/W1-31/test_w1_31_fourth_specimen.py` (30) and the counter's other suites | W1-31, DAEO-6mk8 | valid and needed | no version pinned (DEC-655); the forms of four specimens; 161 passed in my parallel run (`w1-31-par1`) | DEC-655, DEC-663, DEC-677 | none |

### 2.7 Weak tests, shown by planted faults

A test is **weak** when it passes while the behaviour it names is broken. I showed each weak verdict by a **planted fault**: one exact text change in my clone's source, the tests that name the behaviour run (`-n auto --dist worksteal`, behind the gate), the file restored byte for byte with its hash checked, and every test's outcome kept (`scripts/plant.py`; the changes in `notes/plan_plant.json` and `plan_plant2.json`; the outcomes in `logs/plant_results.jsonl` and `logs/plant-<id>.xml`). A fault is **caught** when at least one test run fails. PF19 is a control: a fault the named case must catch.

**R1. W1-26's base project is red before any defect is planted.** I built the suite's own fixture (`w1_26_support.Project`, the `project` fixture of every planted-defect case) in my folder, committed it, and ran `gov check --json` as the suite does (`support.run_check`, the suite's sandbox, my clone's code; `scripts/w126_baseline.py`, `logs/r1.out`). The result: exit 3, `ok` false, 23 checks, six hard-block checks RED.
- Five are red because of what the fixture lacks, so they are red in any environment:
  - `adapter-portability`: no `governance/project/tool-registry.yaml`;
  - `context-reproducibility`: no store;
  - `index-freshness`: "the lexical index is missing";
  - `recovery-rebuild`: "unmeasured", no store (`src/gov/rebuild/check.py:14-15`);
  - `secrets-indexing`: no `.gitleaks.toml`, from my direct run of the check's command in the fixture.
- One depends on the environment: `retrieval-regression`, "GOV_DEV_TIERS is not configured".

With a path map added, as the path-map cases do, the result is the same. In the fixture of `test_warning_yellow_does_not_change_exit_code` (the core checks and three more removed, one failing warning added), `gov check` still exits 3, with four hard-block checks red. So that case's `if envelope["ok"]:` is never true and it asserts nothing. No case of W1-26 asserts that its fixture is green before the defect is planted.

**The faults and what caught them.**

| Fault | The change (file) | Tests run | Caught by | The named cases |
|---|---|---|---|---|
| PF1 | `DISPOSITIONS` loses `"owner"` (`close/command.py:42`) | W1-30 disposition file, `tests/unit/close` (402) | nothing | `test_all_six_dispositions_recognized` passes. So does `test_only_six_disposition_names_accepted`, rightly: its claim, that no seventh name is accepted, still holds |
| PF2 | a refusal with a class no longer says the context failed (`details["context"]`, `close/command.py:306`) | W1-30 disposition, receipt and context-failure files (47) | nothing | `test_disposition_with_context_failure` passes |
| PF3 | `core-pathmap` returns before it reads anything (`check/pathmap.py`) | W1-26, `tests/unit/check` (543) | nothing | the two path-map cases and DEC-436's namespace case pass |
| PF4 | the containment judgement returns before it judges (`close/command.py`, `_check_containment`) | W1-30's close file and `containment_places` file, `tests/unit/close` (426) | 16: `test_w1_30_close.py`'s two later containment cases (`…_changing_acceptance_tests`, `…_changing_docs_outside_paths`), all six of `test_w1_30_containment_places.py`, eight of `tests/unit/close/test_gates.py` | `test_close_runs_containment_check` and `test_containment_blocks_close_for_out_of_scope_commit` pass |
| PF5 | the acceptance run is never made and reports one pass (`close/command.py`, `_check_acceptance`) | W1-30's close file, `tests/unit/close` (419) | 1: `tests/unit/close/test_governance_checks.py::test_a_red_check_and_a_failing_test_are_one_refusal` | `test_close_runs_acceptance_tests` and `test_close_refuses_when_acceptance_tests_fail` pass |
| PF6 | the ratchet's field rule is dropped: an entry missing a field counts (`close/ratchet.py:93-95`) | W2-53, `tests/unit/close/test_ratchet.py` (63) | nothing | no case gives an entry with a field missing (lens H's finding 19; DEC-890 item 2 gives the case to W2-19) |
| PF7 | the schema check no longer reads ticket files (`check/schema.py`, `RECORD_PATHS = ("docs",)`) | W1-26's derived, planted-defect and DEC-436 files, `tests/unit/check` (171) | 1: `tests/unit/check/test_check.py::test_schema_missing_fields` | all four pass: `test_adding_a_ticket_is_picked_up_by_schema_check`, `test_schema_check_discovers_all_ticket_files`, `test_removing_a_defective_record_clears_the_finding`, `test_planted_schema_defect_ticket_missing_kpis` |
| PF8 | the graph check reads no record (`check/graph.py`, `RECORD_PATHS = ()`) | W1-26's derived, planted-defect, decisions and DEC-436 files, `tests/unit/check` (177) | 3: `test_w1_26_dec436.py::test_record_in_nested_path_discovered_by_graph_check`, unit `test_graph_dangling_reference`, `test_graph_duplicate_id` | six of seven pass: the two derived graph cases, the three planted graph defects, `test_w1_26_decisions.py::test_duplicate_id_flagged`. DEC-436's nested-path case fails, rightly: it asserts the graph check's own entry |
| PF9 | the close record's `packet_hash` is a constant, not the context's hash (`close/command.py`) | W1-30's receipt file (18) | nothing | `test_close_record_packet_hash_matches_context` and `test_close_record_has_packet_hash` pass; PF9b, over the whole W1-30 suite and `tests/unit/close` (898 cases), is caught by nothing either: no case holds the close record's packet hash (CAP-50.c) |
| PF10 | the decision checker's findings are never read when an owner decision lifts an escalation (`close/state.py`) | W1-30's iteration and r8 escalation files, `tests/unit/close/test_state.py` (87) | 4, all in `tests/unit/close/test_state.py` (the checker cannot run; a decision the checker does not confirm as the owner's, ×2; any finding of the checker) | `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` passes; PF10b, over the whole W1-30 suite, was not run (limit: time, after the queue's locks) |
| PF11 | the regression stops at its first failure (`--maxfail=1` added to the close's pytest options) | W1-30's close and r9 every-finding files, `tests/unit/close` (429) | 15: seven of `test_w1_30_r9_every_finding.py`, four of `test_measured.py`, four of `test_run_and_record.py` | `test_regression_runs_to_end_all_failures_collected` passes |
| PF12 | a failing regression test refuses nothing (`close/command.py`, `if findings and ignore is None`) | W1-30's close file, `tests/unit/close` (419) | 3: `test_regression_includes_other_acceptance_folders` (its project has its checkpoint), unit `test_a_test_run_with_findings_is_a_finding_of_the_tickets_work`, `test_a_red_check_and_a_failing_test_are_one_refusal` | `test_regression_failure_blocks_close` and `test_regression_runs_to_end_all_failures_collected` pass; under PF12b (the whole W1-30 suite) both still pass |
| PF13 | the trailer gate judges nothing (`close/command.py`, `_check_trailers` returns) | W1-30's close and r8 commits files, `tests/unit/close` (434) | 6: `test_w1_30_r8_commits.py::test_a_commit_of_the_ticket_without_a_role_refuses`, five unit cases (`test_every_finding.py` ×2, `test_gates.py`, `test_measured.py` ×2) | `test_close_requires_implements_trailer` and `test_close_requires_task_trailer` pass |
| PF15 | a ticket's commits are matched by substring of their `Task:` (`close/repo.py`) | W1-30's close file, `tests/unit/close` (419) | 1: `tests/unit/close/test_gates.py::test_the_tickets_commits_are_those_whose_task_trailer_is_the_ticket` | `test_task_trailer_exact_match_not_substring` passes |
| PF16 | the regression is never run and counts nothing (`close/command.py`) | W1-30's close file, `tests/unit/close` (419) | 14: `test_regression_includes_other_acceptance_folders`, ten of `test_every_finding.py`, three of `test_governance_checks.py` | `test_close_runs_regression_tests_when_present` and `test_regression_failure_blocks_close` pass; under PF16b both still pass |
| PF17 | the schema check reads no record (`check/schema.py`, `RECORD_PATHS = ()`) | W1-26's DEC-436, derived and planted-defect files, `tests/unit/check` (171) | 22: three of W1-26's planted-defect cases (`…_record_missing_type`, `…_record_type_non_string`, `…_record_type_null`, which assert the check's own finding), 19 unit cases | four pass: `test_record_in_new_directory_discovered_by_schema_check`, `test_planted_schema_defect_ticket_missing_kpis`, `test_planted_schema_defect_decision_missing_status`, `test_removing_a_defective_record_clears_the_finding` |
| PF18 | a successful close keeps the iteration count (`close/command.py`) | W1-30's iteration file (32) | 1: `test_successful_close_resets_count`. Its `if envelope_ok["ok"]` holds: the third close succeeds, so it is **valid** | — |
| PF19 (control) | the escalation outcome shows the iteration count (`close/command.py`) | W1-30's iteration file (32) | 1: `test_escalation_outcome_has_no_iteration_field`, as it must | — |
| PF20 | every check but `index-freshness` reports GREEN with no finding, so the fixture stays red by `index-freshness` alone (`check/runner.py`, after the declared, OpenSpec, skill and readiness results) | the whole of W1-26 (413) | 34. Each catching case asserts a check's or a family's own status, or a finding: `test_w1_26_not_applicable.py` 11, `test_w1_26_planted_defects.py` 6 (the three record-type cases, the decision checker's exception, the claims case by WBS id, the commands case), `test_w1_26_recorded_commands.py` 4, `test_w1_26_decision_citations.py` 3, `test_w1_26_installed_kernel.py` 3, `test_w1_26_command.py` 2 (the family colours), `test_w1_26_dec436.py` 2, `test_w1_26_decision_register_and_base.py` 2, `test_w1_26_decisions.py` 1 | of the 113 functions my scan sees calling the suite's `run_check` (`scripts/pf20_report.py`, `notes/pf20.txt`; nine more reach `gov check` through other helpers, and all nine failed), 90 pass. Those that claim a defect is found are the weak rows below. The rest claim a GREEN, a count, a family list, provenance or an envelope, which PF20 does not refute |
| PF21 | `gov check` fails whatever its checks say (`check/command.py:41`) | W1-26, `tests/unit/check`, W1-07's envelope file (579) | 1: `test_w1_26_installed_kernel.py::test_a_project_with_neither_layout_answers_as_today` (`ok` and exit 0 on a project without a kernel) | `test_exit_0_when_all_checks_green` skips; `test_warning_yellow_does_not_change_exit_code` and `test_exit_nonzero_when_a_hard_block_is_red` pass, the last rightly: its claim, a non-zero exit, still holds |
| PF22 | the runner's readiness check ignores `check_all`'s answer (`check/runner.py:300`) | W1-26's DEC-436 file, `tests/unit/check` (146) | nothing | `test_readiness_check_all_return_value_not_ignored` passes. No case of area 2 holds the runner's reading of the answer (the readiness package's own unit tests are another area's) |
| PF23 | the runner's readiness check swallows an error of `check_all` (`check/runner.py:310-313`) | the same (146) | nothing | `test_readiness_check_all_exception_caught` passes. The same gap |
| PF24 | the commands check measures nothing (`check/commands.py:21`) | W1-26, `tests/unit/check` (543) | 7: `test_planted_commands_defect_reserved_command_no_module`, `test_w1_26_recorded_commands.py` ×4, unit `test_commands_check`, `test_the_recorded_commands_are_held_and_lock_by_its_module_command` | `test_new_command_module_discovered_by_commands_check` passes |
| PF5b | PF5's change, the whole W1-30 suite | W1-30 (512) | 91, in 19 files of the later rounds (r8 test runs, r9 every finding, r10 skips and interpreter, r11 parallel runs, r12 worker setting, r13 probe findings, long findings, owner-decision register and refused runs, the disposition, iteration, repair-ticket and r8 escalation files) | the two round-1 cases pass; every other case that needs a red acceptance test fails, as it should |
| PF12b | PF12's change, the whole W1-30 suite | W1-30 (512) | 8: `test_regression_includes_other_acceptance_folders`, three of `test_w1_30_r11_parallel_runs.py`, four of `test_w1_30_r12_worker_setting.py` | `test_regression_failure_blocks_close` and `test_regression_runs_to_end_all_failures_collected` pass |
| PF16b | PF16's change, the whole W1-30 suite | W1-30 (512) | 28: `test_regression_includes_other_acceptance_folders`, `test_w1_30_r10_skips.py` 1, `test_w1_30_r11_parallel_runs.py` 11, `test_w1_30_r12_worker_setting.py` 12, `test_w1_30_r13_refused_runs.py` 3 | `test_close_runs_regression_tests_when_present` and `test_regression_failure_blocks_close` pass |
| PF9b | PF9's change, the whole W1-30 suite and `tests/unit/close` | 898 | nothing | both receipt cases pass, and no other case of W1-30 or the unit close tests holds the packet hash |
| PF10b | PF10's change, the whole W1-30 suite | not run (limit: time, after the queue's locks; PF10 is already caught by four unit cases) | — | — |

**The weak tests.**

| Test | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|
| `tests/acceptance/W1-30/test_w1_30_disposition.py::test_all_six_dispositions_recognized` | W1-30, DAEO-2lwj | **weak** | it asserts the test support's own tuple (`support.DISPOSITIONS`), not the close's; PF1 (the close refuses `--disposition owner`) passes it, and no test of the 402 run catches it | CAP-59.c, KPI A3 | assert that `gov close --disposition <name>` is accepted for each of the six (`Rewrite-Reason: it read the support's constant`); W2-67 (P-I2-3) |
| `…::test_disposition_with_context_failure` | W1-30 | **weak** | its docstring: "the output must say the context failed, and the repair ticket records the class but without the context hash"; it asserts only that the literal `"context": "whole-system"` is absent, which the close never writes; PF2 passes it. The unit case `test_every_finding.py::test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket` holds the behaviour at the builder layer (it is not in PF2's run) | DEC-454, CAP-59.c | assert the context's failure in the refusal and on the repair ticket; W2-67 |
| `tests/acceptance/W1-26/test_w1_26_planted_defects.py::test_planted_pathmap_defect_file_matches_no_namespace`, `…_file_matches_two_namespaces`; `test_w1_26_dec436.py::test_new_pathmap_namespace_picked_up` | W1-26, DAEO-fygv | **weak** | R1 (the fixture is red before the defect) and PF3 (the check measures nothing: all three pass); the check itself reads the wrong form of the path map (finding 3, W2-M214) | CAP-38.b (path-map compliance), DEC-436 | assert `core-pathmap`'s own entry and finding (`Rewrite-Reason: passed on gov check's overall exit while the check measured nothing`); W2-M214's carrier, with its fix (P-I2-4, DEC-802) |
| W1-30 round 1, `tests/acceptance/W1-30/test_w1_30_close.py`: `test_close_requires_implements_trailer`, `test_close_requires_task_trailer` | W1-30, DAEO-2lwj | **weak** | no checkpoint, so refused whatever the trailer gate does; PF13 passes both | CAP-13.a, KPI S1 | each project gets its checkpoint, and each assertion names its gate's finding (`Rewrite-Reason: refused for the missing checkpoint, not for the gate it names`); W2-67 (P-I2-3) |
| `…::test_close_refuses_when_acceptance_tests_fail`, `…::test_close_runs_acceptance_tests` | W1-30 | **weak** | the first has no checkpoint; the second asserts only `ok`, and passes when the acceptance run is never made; PF5 and PF5b (the whole W1-30 suite) pass both | CAP-13.a, KPI S1 | the same; W2-67 |
| `…::test_containment_blocks_close_for_out_of_scope_commit` | W1-30 | **weak** | no checkpoint; PF4 passes it, while the later rounds' six containment cases fail | CAP-13.a, MWA-04 | the same; W2-67 |
| `…::test_task_trailer_exact_match_not_substring` | W1-30 | **weak** | no checkpoint; PF15 passes it; one unit case catches PF15 | CAP-13.a, DEC-500 | the same; W2-67 |
| `…::test_regression_runs_to_end_all_failures_collected`, `…::test_regression_failure_blocks_close`, `…::test_close_runs_regression_tests_when_present` | W1-30 | **weak** | the first two have no checkpoint; the third asserts only `ok`; PF11, PF12 and PF16 pass them, while `test_regression_includes_other_acceptance_folders` (with a checkpoint) fails under PF12 and PF16; PF12b and PF16b (the whole suite) pass them too | CAP-13.a, KPI A2 | the same; W2-67 |
| `test_w1_30_receipt.py::test_close_record_packet_hash_matches_context` | W1-30 | **weak** | when `gov context` cannot be read it accepts any string of more than 8 characters (`:513-518`); PF9 (a constant hash) passes it; PF9b (898 cases) passes it too | CAP-50.c | compare with the context's hash and fail when it cannot be read; W2-67 |
| `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` | W1-30 | **weak** | its decision file has no readable frontmatter, so the lift is refused before the checker is asked (`src/gov/close/state.py:242-246`); PF10 passes it, and four unit cases of `test_state.py` catch PF10; PF10b was not run (limit) | DEC-454, DEC-487 | a decision file the checker can read, with one finding of the checker (`Rewrite-Reason: refused before the checker was asked`); W2-67 |
| W1-26's **overall-red class**, 26 functions: `test_w1_26_authority.py` (`test_research_cited_as_decision_is_red`, `test_research_cited_as_policy_is_red`, `test_lesson_cited_as_policy_is_red`, `test_superseded_record_satisfying_current_requirement_is_red`); `test_w1_26_decisions.py::test_supersession_cycle_flagged`; `test_w1_26_gap_tickets.py` (`test_required_missing_row_no_gap_ticket_is_red`, `…_with_unlinked_gap_ticket_is_red`, `test_gap_ticket_naming_closed_ticket_is_red`, `test_gap_ticket_naming_nonexistent_ticket_is_red`); `test_w1_26_planted_defects.py` (`test_planted_schema_defect_ticket_missing_kpis`, `…_decision_missing_status`, `test_planted_graph_defect_dangling_depends_on`, `…_duplicate_id`, `…_id_outside_grammar`, `test_planted_authority_defect_active_while_superseded`, `test_planted_mutation_defect_implementer_covers_acceptance`, `…_subpath`, `test_planted_pathmap_defect_file_matches_no_namespace`, `…_two_namespaces`, `test_planted_claims_defect_ticket_dag_cycle`, `…_ticket_missing_required_field`); `test_w1_26_policy.py::test_a_new_policy_key_with_no_check_and_not_informational_is_red`; `test_w1_26_skill.py` (two `…_is_red`); `test_w1_26_taxonomy.py` (two `…_is_red`) | W1-26, DAEO-fygv | **weak** | each plants one defect and asserts only that `gov check` as a whole failed (`support.assert_red`, `w1_26_support.py:462-467`). R1: the fixture is red before the defect. PF20 (every check but `index-freshness` GREEN) passes all of them but the policy case, whose check PF20 does not reach; PF3, PF7, PF8 and PF17 pass the path-map, schema and graph cases with the very check silenced. `test_w1_26_decisions.py::test_duplicate_id_flagged` has the same shape; it is counted as a duplicate (§2.5) | CAP-38.b (each family's G1 check), CAP-39.d | assert the named check's own entry RED with its finding (`Rewrite-Reason: the fixture was red before the defect, so the case could not fail`); the path-map cases with W2-M214's fix (P-I2-4), the rest in W2-67 |
| W1-26's **derived-scope class**: `test_w1_26_derived.py` (`test_adding_a_ticket_is_picked_up_by_schema_check`, `test_adding_a_decision_is_picked_up_by_graph_check`, `test_schema_check_discovers_all_ticket_files`, `test_graph_check_discovers_all_decision_files`, `test_removing_a_defective_record_clears_the_finding`); `test_w1_26_dec436.py` (`test_record_in_new_directory_discovered_by_schema_check`, `test_new_pathmap_namespace_picked_up`, `test_record_with_unknown_type_not_silently_skipped`) | W1-26 | **weak** | two outputs that differ (they always do: the output carries the commit id), an envelope that came back, a removal that "clears" a finding the check never made, or "not silently green" on a fixture that is never green (R1). PF3, PF7, PF8, PF17 and PF20 pass them | CAP-58.a, DEC-436 | assert the check's own entry before and after (`Rewrite-Reason: the outputs always differ`); W2-67, the path-map case with P-I2-4 |
| W2-L379's three: `test_w1_26_dec436.py::test_readiness_check_all_return_value_not_ignored`, `…::test_readiness_check_all_exception_caught`, `…::test_new_command_module_discovered_by_commands_check` | W1-26 | **weak** (known, DEC-877 item 5) | the row's evidence (the plant goes into a module the judge does not import; a family name no family has; a condition always true), and PF20 passes all three; PF22, PF23 and PF24 pass them, each with the very behaviour switched off | DEC-436, W2-L379 | the row's revision (Wave 3 test hygiene, or W2-67 if P-I2-3 (a) is taken) |
| The **always-true assertions**: `test_w1_26_decisions.py::test_gov_check_runs_decision_checker` ("ACTIVE" or "supersed" or "authority" in the output); `test_w1_26_readiness.py::test_readiness_invalid_is_a_finding` ("readiness" in the output); `test_w1_26_openspec.py::test_openspec_present_and_failing_is_red` ("openspec" in the output, or a non-zero exit); `…::test_openspec_absent_reported_by_name` ("openspec" in the output); `…::test_openspec_absent_never_green` (a loop over families whose name holds "openspec": there is none) | W1-26 | **weak** | each word is in every output, because the check ids and family names are (`readiness`, `openspec-validate`, `authority`), and every exit is non-zero (R1); PF20 passes all five | CAP-38.b, CAP-39.d, DEC-425 | assert the check's own entry and finding code; W2-67 |
| `tests/acceptance/W1-26/test_w1_26_command.py::test_warning_yellow_does_not_change_exit_code` | W1-26 | **weak** | `if envelope["ok"]:`, and R1 shows its fixture red, so it asserts nothing; PF21 (`gov check` always fails) passes it | CAP-39.d | rewritten on a fixture of its own declarations only (P-I2-6); W2-67 |
| `…::test_exit_0_when_all_checks_green` | W1-26 | **weak** | skips in every run (finding 7), and under PF21 | CAP-39.d | retire (P-I2-6) |

### 2.8 A sample of the rest

**How it was drawn.** From the 1,459 test functions of area 2 (parameter sets folded into their function), the ones already reviewed above were set aside; from the rest, each suite gave 5 % of its functions, at least 3, drawn at random with the seed 20261022 (`scripts/sample.py`; the list is `notes/sample.txt`). 86 functions. For each I read the test and its support, set its claim (name, docstring, KPI line) against its assertion, checked it against the decisions in force, and took its result from my parallel run of its suite. "Valid and needed" here means: it asserts the behaviour it names on a project built to show it, and nothing I found makes that fail open.

| # | Test (function) | Suite, owner | Verdict | Evidence | Rests on | Proposal and carrier |
|---|---|---|---|---|---|---|
| 1 | `test_w1_15_filter.py::test_a_secret_far_into_a_long_file_is_found` | W1-15, DAEO-7nne | valid and needed | the file with a canary on line 5,322 is left out of what an indexer may read; passed in `w1-15-par1` | CAP-03.a | none |
| 2 | `test_w1_15_gitleaks_rules.py::test_text_about_canaries_and_tokens_is_not_a_finding` (`local_only`) | W1-15 | valid and needed | the rules find no finding in governance prose; passed in `w1-15-par1` | CAP-03.a (no false positive) | none |
| 3 | `test_w1_15_product_data.py::test_the_product_folder_of_this_repository_has_no_special_place` | W1-15 | valid and needed | the map, not a fixed path, decides; passed in `w1-15-par1` | CAP-03.b, failure line 2 | none |
| 4 | `test_w1_26_audit_validator.py::TestEmptyFolder::test_empty_folder_not_applicable` | W1-26, DAEO-fygv | valid and needed | exit non-zero, `not_applicable` true and DEC-447's words; passed in `w1-26-par1` | DEC-447 | none |
| 5 | `…::TestEvidencePathExists::test_multiple_evidence_paths_comma_separated` | W1-26 | valid and needed | a positive control of the validator (exit 0); passed in `w1-26-par1` | DEC-441 | none |
| 6 | `…::TestValidReport::test_valid_report_passes` | W1-26 | valid and needed | positive control; passed in `w1-26-par1` | DEC-441 | none |
| 7 | `test_w1_26_command.py::test_gov_check_json_returns_the_api_0002_envelope` | W1-26 | duplicate | of W1-07's `test_every_command_returns_the_envelope[check]` (both assert the API-0002 envelope of `gov check --json`); its `pytest.skip` on NOT_IMPLEMENTED is dead since `gov check` was built | API-0002 | keep: about a second a close. No retirement is proposed; one would be the owner's |
| 8 | `test_w1_26_dec436.py::test_family_only_red_check_not_green` | W1-26 | valid and needed | asserts the family's own status, not the exit | DEC-436, DEC-425 | none |
| 9 | `test_w1_26_dec436.py::test_family_only_unmeasured_check_not_green` | W1-26 | weak | its own declaration is invalid YAML. The support writes `command: "python3 -c "import json,…"` with the inner quotes unescaped (`w1_26_support.py:273`), so `gov check` exits 1 with `CHECK_DECLARATION_INVALID` and runs no check. The helper then finds no family (`None`), which is "not GREEN", so the case passes. Shown by my run of its fixture with no fault planted, and again under PF20 (`scripts/pf20_row9b.py`) | DEC-425 | the support escapes what it writes, or writes YAML with the YAML library; the case asserts that the family exists and is not GREEN (`Rewrite-Reason: its declaration was invalid YAML, so the check never ran`); W2-67 |
| 10 | `test_w1_26_dec438.py::test_family_green_requires_at_least_one_check` | W1-26 | valid and needed | each uncovered family is not GREEN | DEC-438, DEC-425 | none |
| 11 | `test_w1_26_decision_citations.py::test_outside_a_repository_is_unmeasured` | W1-26 | valid and needed | the check's own answer | DEC-463 | none |
| 12 | `…::test_the_check_is_declared_a_warning` | W1-26 | valid and needed | reads the kernel declaration | DEC-463 ("flags") | none |
| 13 | `…::test_the_declaration_does_not_opt_in_to_not_applicable` | W1-26 | valid and needed | declaration | DEC-447 | none |
| 14 | `test_w1_26_not_applicable.py::TestValidatorNotApplicable::test_not_applicable_exit_code_is_2` | W1-26 | valid and needed | exit 2 | DEC-447 | none |
| 15 | `test_w1_26_probe_records.py::test_a_record_whose_type_is_no_text_is_still_a_finding` | W1-26 | valid and needed | the schema check's own findings | DEC-565 | none |
| 16 | `test_w1_26_skill_checks_layouts.py::test_in_the_template_layout_a_planted_defect_is_a_finding` | W1-26 | valid and needed | asserts a finding naming the broken skill | DEC-439 | none |
| 17 | `…::test_in_the_template_layout_an_absent_skill_is_never_green` | W1-26 | valid and needed | never GREEN | DEC-439 | none |
| 18 | `test_w1_26_skill_validator.py::TestNonTextFields::test_version_integer_is_finding` | W1-26 | valid and needed | non-zero exit (a crash would also pass it; low risk: other cases of the class read the finding) | DEC-439 | none |
| 19 | `test_w1_30_check_blocks.py::test_a_refusal_where_gov_check_blocks_opens_a_dependent_repair_ticket` | W1-30, DAEO-2lwj | valid and needed | refusal names what blocks; dependent repair ticket; 512 passed (09:52, load 13 to 19) | DEC-480 | none |
| 20 | `test_w1_30_context_failures.py::test_the_same_project_closes_once_it_has_a_record_store` | W1-30 | valid and needed | the store is the only reason | DEC-470 | none |
| 21 | `test_w1_30_disposition.py::test_valid_disposition_builds_context_first` | W1-30 | valid and needed | the repair ticket carries a context hash | CAP-59.c, DEC-454 | none |
| 22 | `test_w1_30_disposition.py::test_valid_disposition_records_class` | W1-30 | valid and needed | the class recorded | CAP-59.c | none |
| 23 | `test_w1_30_governance_checks.py::test_a_failing_check_of_severity_warning_refuses_nothing` | W1-30 | valid and needed | a warning refuses nothing; premise asserted | DEC-480 | none |
| 24 | `…::test_the_close_record_names_the_commit_being_closed` | W1-30 | valid and needed | `check_commit` equals HEAD | DEC-480, DEC-454 | none |
| 25 | `test_w1_30_iteration.py::test_count_file_wrong_shape_string_count_refuses` | W1-30 | valid and needed | no traceback, a refusal | DEC-454 | none |
| 26 | `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` | W1-30 | weak (PF10) | its decision file has no readable frontmatter, so the lift is refused before the checker is asked (`src/gov/close/state.py:242-246`); PF10 passes it, and four unit cases of `test_state.py` catch PF10 | DEC-454, DEC-487 | W2-67: the decision file gets readable frontmatter, so the checker is what refuses (`Rewrite-Reason: refused before the checker was asked`) |
| 27 | `test_w1_30_r13_installed_skills.py::test_a_project_with_both_layouts_lists_the_skills_of_both` | W1-30 | valid and needed | the exact list | DEC-569, B4 | none |
| 28 | `test_w1_30_r13_owner_decision_register.py::test_with_no_register_named_an_entry_lifts_nothing` | W1-30 | valid and needed | escalation stays | DEC-483, DEC-862 (a) | none |
| 29 | `test_w1_30_r15_context_tickets.py::test_the_check_is_red_and_names_the_ticket_whose_context_does_not_reproduce` | W1-30 | valid and needed | the check's own status and finding | DEC-628 | none |
| 30 | `test_w1_30_r15_policy_pairs.py::test_a_research_record_cited_as_a_ticket_s_source_turns_the_authority_check_red` | W1-30 | valid and needed | before/after on `core-authority` itself | DEC-613, DEC-627 | none |
| 31 | `test_w1_30_r15_retrieval_limit.py::test_the_declaration_states_a_limit_of_600_seconds_and_nothing_else_of_it_changes` | W1-30 | valid and needed | the declaration (600 s, DEC-612); no later decision changed it | DEC-612 | none |
| 32 | `test_w1_30_r8_last_step.py::test_a_ticket_commit_under_the_installed_kernel_refuses_where_a_hard_block_check_is_red` | W1-30 | valid and needed | names `license-present`; premises asserted | DEC-487 | none |
| 33 | `test_w1_30_r8_probe_record.py::test_a_judgement_of_pass_or_passed_is_accepted` | W1-30 | valid and needed | closes | DEC-487 | none |
| 34 | `…::test_a_probe_record_that_is_written_and_not_committed_refuses` | W1-30 | valid and needed | refusal names the file | DEC-487 | none |
| 35 | `test_w1_30_r9_every_finding.py::test_the_refusal_for_several_findings_is_counted_once` | W1-30 | valid and needed | count 1 | DEC-492 | none |
| 36 | `test_w1_30_r9_ticket_tool.py::test_the_kernels_ticket_tool_is_used_where_path_holds_another` | W1-30 | valid and needed | the PATH tool never started | DEC-492 | none |
| 37 | `test_w1_30_receipt.py::test_close_record_packet_hash_matches_context` | W1-30 | weak (PF9) | if `gov context` cannot be read it accepts any string of more than 8 characters (:513-518); PF9 (a constant hash) passes it | CAP-50.c | W2-67: the case fails when `gov context` cannot be read, and compares the hash exactly |
| 38 | `test_w1_30_test_runner.py::test_without_a_test_runner_nothing_is_closed` | W1-30 | valid and needed | `TEST_RUNNER_ABSENT`, nothing closed | DEC-487 | none |
| 39 | `test_w1_31_fourth_specimen.py::test_a_command_behind_a_cd_that_does_not_run_gov_counts_nothing` | W1-31, DAEO-6mk8 | valid and needed | counts and notes exact; passed in `w1-31-par1` | DEC-655 | none |
| 40 | `…::test_gov_behind_a_cd_the_harness_kept_is_counted_whole` | W1-31 | valid and needed | exact counts | DEC-655 | none |
| 41 | `test_w1_31_measured_and_estimated.py::test_a_form_the_specimen_does_not_show_is_not_measured` | W1-31 | valid and needed | positive count first, then never a number | DEC-495, DEC-501 | none |
| 42 | `…::test_sessionstart_packet_is_what_the_sessionstart_hooks_added` | W1-31 | valid and needed | exact token count; one session named, one packet | DEC-495 | none |
| 43 | `test_w1_31_second_specimen.py::test_the_precompact_gap_is_named_and_is_no_entry_of_not_measured` | W1-31 | valid and needed | the gap's reason says "no hook line", as DEC-502 corrected it and DEC-512 kept | DEC-502, DEC-512 | none |
| 44 | `test_w1_40_ci_installs.py::test_the_gitleaks_step_takes_its_version_address_and_checksum_from_the_registry` | W1-40, DAEO-fdkq | valid and needed | reads the registry (a record-reading case, P-I2-2); passed in `w1-40-par1` | DEC-494 | none |
| 45 | `test_w1_40_evidence_record.py::test_ci_reports_that_no_g3_check_is_declared_and_does_not_fail_for_it` | W1-40 | valid and needed | the words by a step that does not fail; job green | DEC-497 | none |
| 46 | `test_w1_40_pre_push.py::test_the_push_passes_again_once_the_g3_check_passes` | W1-40 | valid and needed | refused, then arrives | DEC-489 | none |
| 47 | `test_w1_42_exit_report.py::test_dev_query_set_mean_hit5_is_remeasured_against_85` | W1-42, DAEO-gjjf | valid and needed | the frozen exit record against itself; 0.1 s for the suite | DEC-414, DEC-718 | none |
| 48 | `…::test_exit_run_was_run_from_the_kernel_skill_and_brief_templates` | W1-42 | valid and needed | also checks that the kernel files the report names exist: a kernel change that moves them turns it red (§4.1) | DEC-537 | none |
| 49 | `…::test_git_worktree_list_shows_no_ticket_worktree_left` | W1-42 | valid and needed | frozen record | CAP-23.c | none |
| 50 | `test_w1_48_claude_code.py::test_the_approval_names_claude_code_and_the_pinned_version` | W1-48, DAEO-0qs5 | valid and needed | registry 2.1.292 approved by DEC-649, which names it; a record-reading case (P-I2-2); passed in `w1-48-par1` | DEC-197, DEC-649 | none |
| 51 | `test_w1_48_drift.py::test_a_newer_binary_with_another_digest_is_drift_by_its_version_alone` | W1-48 | valid and needed | exercises the suite's own rule (`w1_48_support.compare_with_record`), which judges the machine case; no product code runs | DEC-210, DEC-214 | none |
| 52 | `…::test_a_record_written_with_a_leading_v_is_the_same_version` | W1-48 | valid and needed | the same | DEC-210 | none |
| 53 | `test_w2_01_accepted_history.py::test_the_check_of_a_later_commit_is_green_and_lists_the_accepted_commit` | W2-01, DAEO-g0ip | valid and needed | the check's own entry GREEN and the listing; 88 passed (09:51, load 10 to 14) | DEC-734, DEC-891 | none |
| 54 | `test_w2_01_merge_form.py::test_a_merge_of_the_integration_branch_in_the_merge_form_passes_the_trailer_gate` | W2-01 | valid and needed | the merges not named, listed in the record | DEC-436, W2-M165 | none |
| 55 | `test_w2_01_probe_merge_back.py::test_a_later_merge_holding_the_probed_commit_that_leaves_the_probed_code_closes` | W2-01 | valid and needed | boundary guard | DEC-750 | none |
| 56 | `test_w2_53_accepted_reds.py::test_a_red_the_list_does_not_cover_by_its_exact_id_refuses_the_close` | W2-53, DAEO-7rr2 | valid and needed | names the uncovered red; 57 passed (09:51, load 6 to 11) | DEC-757 item 2 | none |
| 57 | `test_w2_53_later_merges.py::test_a_later_merge_on_the_integration_branch_that_is_not_gits_own_merge_refuses_and_names_it` | W2-53 | valid and needed | names the merge | DEC-750, DEC-754 | none |
| 58 | `test_w2_53_ticket_file_edits.py::test_an_orchestrators_integration_side_edit_of_the_ticket_file_on_the_branch_closes` | W2-53 | valid and needed | closes; premises asserted | DEC-757 item 3 | none |
| 59 | `tests/unit/check/test_check.py::test_inputs_hash_length` | unit check, W1-26 | valid and needed | builder test of a detail (regression evidence only) | DEC-042 | none |
| 60 | `…::test_provenance_fields` | unit check | valid and needed | provenance | CAP-39.d | none |
| 61 | `test_citations.py::test_the_two_keys_are_read` | unit check | valid and needed | | DEC-479 | none |
| 62 | `test_kernel_followup.py::test_a_well_formed_probe_record_owes_no_shared_field` | unit check | valid and needed | | DEC-565 | none |
| 63 | `tests/unit/ci/test_ci_command.py::test_a_name_that_is_no_tier_refuses` | unit ci, W1-40 | valid and needed | | DEC-489 | none |
| 64 | `…::test_only_the_tiers_named_run` | unit ci | valid and needed | G3 not run | CAP-39.a | none |
| 65 | `…::test_the_job_gate_refuses_where_no_g2_check_is_declared` | unit ci | valid and needed | | DEC-497 | none |
| 66 | `tests/unit/close/test_every_finding.py::test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket` | unit close, W1-30 | valid and needed | holds what W1-30's `test_disposition_with_context_failure` claims (§2.7) | DEC-454 | none |
| 67 | `test_follow_up.py::test_the_share_is_the_counters_and_nothing_else_of_its_record` | unit close | valid and needed | | DEC-495 | none |
| 68 | `test_governance_checks.py::test_any_red_hard_block_check_is_returned_whatever_the_ticket_changed` | unit close | valid and needed | | DEC-480 | none |
| 69 | `test_measured.py::test_every_probe_record_of_the_ticket_is_asked_everything` | unit close | valid and needed | | DEC-500, W2-M209 | none |
| 70 | `test_parallel_runs.py::test_a_declared_case_runs_afterwards_in_no_worker_and_a_case_named_alike_stays_parallel` | unit close | not reproducible (finding 5) | valid in what it asserts. Its nested run under a 60 s limit failed in the tool trials b2 and a-cost, and passed in my six runs (alone ×3, `tests/unit/close` in parallel ×3) | DEC-527 | W2-67: bounded nested runs (finding 5) |
| 71 | `test_parallel_runs.py::test_the_list_holds_entries_and_comments_and_an_entry_names_at_a_boundary` | unit close | valid and needed | | DEC-527 | none |
| 72 | `test_refuse.py::test_a_refusal_is_counted_and_raised_with_its_finding` | unit close | valid and needed | | CAP-59.a | none |
| 73 | `test_refuse.py::test_an_owner_decision_without_an_escalation_is_refused` | unit close | valid and needed | | DEC-487 | none |
| 74 | `test_repo.py::test_output_of_another_shape_is_an_error_and_never_fewer_commits` | unit close | valid and needed | | DEC-454 | none |
| 75 | `test_run_and_record.py::test_the_close_record_holds_what_it_is_given_and_its_outputs` | unit close | valid and needed | | CAP-50.c | none |
| 76 | `test_run_and_record.py::test_the_environment_of_the_run_is_the_callers_with_the_projects_src_alone_on_the_path` | unit close | valid and needed | | DEC-500 | none |
| 77 | `test_state.py::test_any_finding_of_the_checker_about_the_decision_lifts_none` | unit close | valid and needed | holds what W1-30's checker case claims (row 26) | DEC-487 | none |
| 78 | `tests/unit/secrets/test_scan_scale.py::test_an_unchanged_clean_store_is_reused_and_labelled_a_changed_one_scanned` | unit secrets, W2-50 | flaky (collection order, finding 8) | the case itself is sound; its file fails to import when the standard library's `secrets` was imported first (reproduced, §2.4) | DEC-853 | the folder's rename (W2-L373) |
| 79 | `test_secrets.py::test_big_endian_utf16_text_is_still_scanned` | unit secrets, W1-15 | flaky (collection order, finding 8) | the same | CAP-03.a | the same |
| 80 | `test_token_rule.py::test_the_three_expressions_flag_what_the_requirement_flags` | unit secrets, W1-16 | flaky (collection order, finding 8) | property-style, every place of a 15 and 16 character body; the same | DEC-339 | the same |
| 81 | `tests/unit/telemetry/test_counter.py::test_a_line_no_specimen_shows_is_not_measured_for_its_source` | unit telemetry, W1-31 | valid and needed | | DEC-495, DEC-663 H | none |
| 82 | `…::test_a_log_of_any_version_in_the_specimens_forms_is_read_with_the_versions_its_lines_carry` | unit telemetry | valid and needed | | DEC-655 | none |
| 83 | `…::test_the_estimate_stands_on_the_role_the_caller_names_for_the_session` | unit telemetry | valid and needed | | DEC-507 | none |
| 84 | `tests/unit/validate/test_canary.py::TestEmptyCanaryDeclarations::test_empty_canaries_list_reports_facet_unavailable` | unit validate, W1-22 | valid and needed | | DEC-425 | none |
| 85 | `test_validate.py::test_rejects_absent_text` | unit validate | valid and needed | | W1-22 KPI | none |
| 86 | `test_validate.py::test_rejects_missing_reason` | unit validate | valid and needed | | W1-22 KPI | none |

## 3. Counts per verdict, and the close time each class costs

There is one verdict per test function, and a parametrised function counts once, with all its cases (`notes/verdicts-final.tsv`, built by `scripts/build_verdicts.py` from the tables of §2). The time is the function's cases' case-seconds in the rehearsal (2026-10-21, the close's form; `logs/fn_times.json`).
- A close runs the regression in parallel. The rehearsal's parallel run did 13,417 case-seconds in 1,906 s of wall time, a speed-up of about 7.0. So a class costs a close about its case-seconds divided by 7.
- The serial run's cases cost their full time. In area 2 that is only W1-15's bound case.

| Verdict | Functions | Cases | Case-seconds (rehearsal) | Share of area 2's case time | About this much of a close's wall time |
|---|---|---|---|---|---|
| valid and needed | 306 | 585 | 824.1 | 21.3 % | 117 s |
| weak | 58 | 58 | 213.4 | 5.5 % | 30 s |
| outdated (each names its decision) | 16 | 44 | 74.8 | 1.9 % | 11 s |
| flaky (cause found) | 23 | 28 | 55.0 | 1.4 % | 11 s |
| duplicate | 4 | 4 | 12.0 | 0.3 % | 2 s |
| obsolete | 1 | 1 | 5.4 | 0.1 % | 1 s |
| not reproducible | 10 | 13 | 18.5 | 0.5 % | 3 s |
| **reviewed** | **418** | **733** | **1,203.0** | **31.1 %** | **174 s** |
| not reviewed (outside §2's lists and the sample) | 1,041 | 1,531 | 2,661.0 | 68.9 % | 378 s |
| area 2 in all | 1,459 | 2,264 | 3,864.1 | 100 % | 549 s |

**What the classes cost, and what acting on them saves.**
- **Weak, 58 functions, about 30 s of every close.** W1-30's 13 take 72.9 case-seconds, because each runs a whole fixture close. W1-26's 45 take 140.5, because each runs `gov check` on a fixture. The revisions of P-I2-3 keep the cases and make them able to fail, so the time stays and becomes worth spending. Only the retirements save time.
- **The retirements (P-I2-5 to P-I2-7) save 19.3 case-seconds, about 3 s of every close:** the duplicate containment case 5.1, the always-skipped exit case 8.8, and the obsolete receipt case 5.4. The other three duplicates (12.0 case-seconds with the containment case) are kept: no retirement is proposed for them.
- **Outdated, 16 functions, about 11 s.** They cost nothing extra today. They cost a red regression, and a test designer's round, when the ticket that changes their behaviour lands without naming them (finding 9).
- **Flaky and not reproducible, 33 functions, about 14 s.** Their cost is not their time. It is a refused close of about 70 minutes when one fails in a close:
  - the `secrets` package's collection, under plugins that import `secrets`;
  - W1-30's r13 case, under a loaded start;
  - the nested-run class, under worksteal beside the whole regression;
  - W1-15's bound case, outside the quiet window.
  One avoided refusal saves more close time than the whole area's weak class costs in a week of closes.
- **Not reviewed: 1,041 functions** (68.9 % of the area's case time). The seeded sample of 86 drawn from them found 78 valid and needed, 3 flaky (for the `secrets` package's name), 1 not reproducible (a nested-run case), 3 weak and 1 duplicate. By that sample, about 91 % of the unreviewed rest is sound. The weak cases among it are of the shapes §2.7 names, and of one shape more: sample row 9's fixture, whose declaration is invalid YAML.

## 4. What it changes

### 4.1 For W2-66's path-to-suite map (and W2-68's record-reading set)

W2-66 selects "the ticket's own suite, the unit tests, and the suites of every ticket whose allowed paths overlap the change" (DEC-880 item 2), with the shared core always running everything (since DEC-892 c also `src/gov/config/**`, `src/gov/tasks/tickets.py` and `src/gov/store/**`). The table compares, for each suite of area 2, the source files its tests executed (lens H's measured map across processes, at `21302ae9`: `/tmp/gov-os-assessment-H/logs/cov_map.json`, my script `scripts/reach.py`) with its owner ticket's allowed paths (lens H's `allowed_map.json`).

| Suite (owner) | Owner's paths | Reached outside them (tests reaching each) | Owner's files never reached | What the map needs |
|---|---|---|---|---|
| W1-26 (`gov check`) | `src/gov/check/**`, `tests/unit/check/**`, `template/…/checks/core-*` | 42 files: every module a declared check runs, among them `close/traceability.py` (130), `adapters/portability.py` (130), `secrets/` (129), `retrieval/retrieve_check.py` (130), `context/context_check.py` (130), `rebuild/check.py` (130), `readiness/` (140), `guard/containment*.py` (200), `decisions/checker.py` (201) | none | every module a declaration's command runs maps to W1-26 (and to W1-30's governance-check cases). `src/gov/check` is shared core, but the checks' modules outside it are not: a change to `adapters/portability.py` selects W1-38 and not W1-26's 130 cases that run it |
| W1-30 (`gov close`) | broad: close, rebuild, check, store, readiness, context, telemetry, codeintel, tasks, records, schemas, checks, `cli/checks.py`, `guard/containment.py` | 31 files: `checkpoint/record.py` (373), `decisions/checker.py` (362), `secrets/__init__.py` (361), `closure/` (337), the retrieval modules (337 to 360), `guard/runs.py` (406), `guard/decide.py` (389), `guard/protected.py` (364), `adapters/portability.py` (34) | `readiness/command.py`, `tasks/bridge.py` | `checkpoint/**`, `decisions/**`, `closure/**` and `adapters/**` map to W1-30: every close runs the watchdog, the context and the decision checker |
| W1-31 (governance share) | `src/gov/telemetry/**`, its unit folder | 19 files, each reached by all 161 cases: tasks, store, records, context, config, cli, `checkpoint/` | none | `context/**` and `checkpoint/**` map to W1-31 (`gov telemetry` builds the ticket's context) |
| W1-40 (hooks, CI) | `lefthook.yml`, the workflow files and their templates, `src/gov/ci/**` | 24 files: `check/runner.py` (53), `secrets/` (48), `guard/runs.py` (48), readiness, tasks, store | none | `secrets/**` and `guard/runs.py` map to W1-40 (the hooks run the staged-secrets scan) |
| W1-42 (exit run) | `docs/plan/wave-1-exit/**` | no source file executed; read as text: `src/gov/cli/main.py` (the twelve names), the kernel's orchestration skill and `templates/brief-*.md` named by the report, `.tickets/` (the Wave 1 tickets) | — | `src/gov/cli/main.py`, `template/governance/kernel/templates/**`, `template/governance/kernel/skills/orchestration/**` and `.tickets/` map to W1-42; it belongs to the record-reading set (P-I2-2) |
| W1-15 (secrets) | `src/gov/secrets/**`, the two gitleaks files, the check's declaration, **and** `src/gov/check/**`, `src/gov/cli/checks.py`, `src/gov/adapters/**` | 21 files: config, cli, `guard/runs.py` (72), tasks, store, records | 12: `adapters/` and every `check/*.py` but the runner | the reverse case: W1-15's paths name code its tests never reach, so a change there selects W1-15 for nothing (cost only) |
| W1-48 (Claude Code pin) | `governance/project/tool-registry.yaml` | no source file executed; reads the register (approvals) and `template/governance/kernel/schemas/tool-registry.schema.json`; its 57 drift cases exercise the suite's own rule (`w1_48_support.compare_with_record`) | — | the register and the schema map to W1-48; it belongs to the record-reading set (P-I2-2) |
| W2-01, W2-53 (close traceability, probe gate, ratchet) | `src/gov/close/**` (shared core) | 47 and 41 files: retrieval, guard, checkpoint, decisions, telemetry, closure | W2-53: `close/traceability.py` | covered by the shared core |
| `tests/unit/close` | (`src/gov/close/**`) | `tasks/tickets.py` (124), `store/loader.py` (39), `guard/decide.py` (19), `decisions/checker.py`, `checkpoint/record.py` (8 each) | `close/pytest_plugin/` (exercised only by W2-53's children) | covered by the shared core |
| `tests/unit/check` | (`src/gov/check/**`) | 40 files (one case runs every check) | `check/command.py` | covered by the shared core |
| `tests/unit/validate` | — (no `src/gov/validate`) | `retrieval/validate.py` (10), `retrieval/canary.py` (5) | — | the folder's name names no package: map `src/gov/retrieval/validate.py` and `canary.py` (W1-22's) to it |

Two more rules for the map, from area 2:
- **A test that reads a source file as text is not seen by an import graph or a coverage map.** W1-42 reads `src/gov/cli/main.py`; W1-30's `test_w1_30_r11_declared_here.py` reads `tests/acceptance/serial-only.txt` and collects other suites. The map must name such files explicitly.
- **The record-reading cases of area 2 run on every head** (P-I2-2): W1-48, W1-26's two probe-record cases, W1-40's registry cases, W1-42, W1-30's declared-here cases.

### 4.2 For W2-57's serial list

- **Area 2 has one serial-only entry:** W1-15's `test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder` (latency: 60 small files and one 9 MB SQLite store within 15 s).
  - Alone, on a machine that stayed under a load of 23, it took 8.6 s and 4.6 s. When the load rose to 82 during the run, it took 26.6 s and failed.
  - In W1-15's parallel run it passed once in four (13.5 s), and failed three times at 15.8 to 15.9 s or more.
  - **It cannot run in parallel.** It stays on the list, as DEC-889 item 5 decides for latency tests, and it holds only in the close's quiet window (DEC-780).
- **Missing entries:** none of area 2's latency-shaped cases is missing from both lists. Two time-limit cases are on `load_sensitive` and not on the serial list.
  - W1-30's r13 case failed alone once in three because its 5-second limit is shorter than a loaded start of the parallel run (§2.2). Running it serially would not help, since its close runs in parallel by design. It needs a test revision (W2-57, `Rewrite-Reason: W2-M384`).
  - The unit `test_at_the_time_limit_…` case passed all six of my runs. It needs neither list today.
- **The nested-run unit cases** (finding 5) are not serial-list candidates: their fix is a bounded nested run, not running them alone.
- **The list's own tests:** `test_w1_30_r11_declared_here.py` (29 cases) holds today's entries one by one, so W2-57's change to the list must revise it in the same round (finding 9).

### 4.3 For the two ratchet lists

`accepted_reds` holds 2 entries. `load_sensitive` held 31 entries (43 cases) at `4166d8d9`, and 32 (44 cases) from the owner's commit `49c24ac9`. Each entry below is judged by its recorded evidence, its fix, and my runs (§2.1, §2.2).

| Entries | Decision | `fixed_by`, and can it remove them? | Wave 2 evidence | My runs | Verdict on the entry |
|---|---|---|---|---|---|
| W1-42 RETR-X-02 (accepted red) | DEC-757 | W2-13, open. No: its paths do not reach the case or the kept bundle, and Q-1 is unruled (finding 1) | red in every close and the rehearsal | red alone, 0.09 s | keep. It tracks DEC-718's closing condition, but needs a route out (P-I2-1 A) |
| W1-42 governance share (accepted red) | DEC-757 | W2-14, open. No: its only path is `docs/plan/wave-2/argus-cycle/**` | the same | red alone | keep; P-I2-1 A |
| W1-02 p95 decision (5 cases) | DEC-757 | W2-M332, a Wave 3 row; target "before W2-24 starts" (DEC-890). A row closes no ticket, so W2-19's close check cannot hold it | never red in a Wave 2 close | not run (limit: other areas' cases, and the queue's locks) | keep, by the records. It is also serial-only, so its entry is a second try alone (finding 14); it stays or goes as the owner rules (P-I2-1 C) |
| W1-05 p95 hook wait (9 cases) | DEC-757 | W2-M332, the same | red in W2-01's close (2026-10-17) | not run (the same limit) | the same |
| W1-19 warm query p95 | DEC-757 | W2-M332, the same | green in every close | not run (shared models; limit) | keep until DEC-889 item 5 moves its file to the nightly; its file is serial-only, and the entry leaves then (P-I2-1 C) |
| W1-46 live sessions (23) | DEC-760, DEC-762 | W2-M364 → W2-57 (DEC-813). Yes for the tests: W2-57's paths hold `tests/acceptance/W1-46/**`. If the missing `cd` is the launcher's, `src/gov/launch/**` is not in them | setup errors under load (W2-03 run 2); 20 of 23 green alone in the blocker sweep; `[static.crates.io]` red alone in W2-63's close and traced to the host's reachability (DEC-892 item 3) | not run (live sessions; limit) | keep until W2-57. The file has been serial-only since 2026-10-08, and DEC-889 item 5 moves it to the nightly, so its 23 entries leave then (finding 14, P-I2-1 C). `[static.crates.io]`'s stated reason is not its latest cause (finding 10) |
| unit `test_follow_up` time limit | DEC-762 | W2-L352, a Wave 3 row; target "before W2-24 starts" (DEC-890) | red once in W2-53's review (`-n 8`) | alone ×3 and in `tests/unit/close`'s parallel run ×3: all passed | not reproducible today. It costs a close nothing, and can leave with W2-57's list work, a removal (DEC-861) |
| W1-30 r13 time limit | DEC-823 | W2-M384 → W2-57. Yes as planned: W2-57's paths hold the r13 file and `src/gov/close/**` | red once in W2-53's re-close (load about 25) | alone ×3: failed once, on its 5-second limit, under load (§2.2); in W1-30's parallel run ×3: passed each time | keep until W2-57 revises the case's timing (W2-M384 settled: its timing) |
| W1-38 rulesync (2) | DEC-871 | W2-57. No: its planned paths hold neither `src/gov/adapters/portability.py` nor `tests/acceptance/W1-38/**` (finding 12) | `RULESYNC_FAILED` in W2-53's close; Wave 1 | not run (the same limit as W1-02's) | keep until W2-57, whose paths need the probe and the tests (P-I2-1 B) |
| W1-38 unsourced file (1) | DEC-892 | W2-57, the same | `RULESYNC_FAILED` in W2-63's close. **Refused by the ratchet in W2-50's close** (R-2, finding 11); DEC-892's text names the file since `da3d77e1` | not run (the same limit) | counted since `da3d77e1`: W2-62's close at 16:44 raised no finding about it; keep until W2-57 (P-I2-1 B) |
| W1-07 `doctor` envelope (1) | DEC-886 | W2-57. No: its planned paths hold neither `src/gov/doctor/` nor `tests/acceptance/W1-07/**` | red in W2-02's two closes, green alone | not run (the same limit) | keep until W2-57, whose paths need `src/gov/doctor/` and the W1-07 case (P-I2-1 B) |

**Across the list.**
- 28 of the 32 `load_sensitive` entries wait for W2-57, which has no ticket file yet. Its planned paths reach 24 of them (W1-46's 23 and W1-30's r13) and not the other four (finding 12).
- 26 of the 32 entries name cases the close already runs alone, from the serial-only list (W1-46 ×23, W1-19, W1-02, W1-05). For them the entry is a second try under the same condition, and DEC-889 item 5 moves 24 of them to the nightly (finding 14, P-I2-1 C).
- 4 entries name Wave 3 rows, not tickets (W2-M332 ×3, W2-L352). DEC-762 item 2's check refuses "the close of the ticket an entry names", and a row has no close. So W2-19's check will hold nothing for them. Only DEC-890's target date ("before W2-24 starts") does.
- The list grew once in Wave 2, through an owner package (P-W2-63-C1, DEC-892), as DEC-766 requires. Its first close refused the new entry for its decision's wording (finding 11).
- In the four clean closes of Wave 2 (`CL-DAEO-7rr2`, `CL-DAEO-zflj`, `CL-DAEO-0rfi`, and W2-62's `CL-DAEO-juee` today at 16:44), no entry was needed (`load_sensitive: []`). So the entries cost a close nothing until a listed case fails. Then the close re-runs it alone and counts it only if it passes, which is the purpose the owner gave them (DEC-757).

## 5. Findings

Each finding carries the two lines of DEC-808. Only "yes" with "fails open" or "loses work" fails an item and justifies a round (DEC-801); a feature-gated risk is an entry criterion of the ticket that switches the feature on (DEC-803); fixes ride along in a ticket that resumes anyway (DEC-802).

### Finding 1. The two accepted reds cannot leave the list through the tickets that are meant to fix them

- **What the reds read.** Both W1-42 cases read the frozen Wave 1 exit record: `docs/plan/wave-1-exit/EXIT-REPORT.md` and `docs/plan/wave-1-exit/evidence/*.json` (`tests/acceptance/W1-42/w1_42_support.py:15-17`). No commit has touched that folder since `ca426ca9` (2026-10-16). Run alone in my clone: `2 failed, 22 passed in 0.09s`, "RETR-X-02.json: no named parent expansion (DEC-091)" and "governance-share.json does not exist".
- **What the owner decided closes them.** DEC-718 item 11 accepts DEC-714's exceptions with the closing conditions of the exit report's block: RETR-X-02 closes "on a kept bundle of RETR-X-02 with at least one parent expansion that names its parent, or on the owner's ruling" (`EXIT-REPORT.md:37`); F-M1 closes on a measured share per programme "in `governance-share.json` … and W1-42's share case green".
- **What the fix tickets can do.**
  - **W2-13** (`.tickets/DAEO-zqvn.md`): allowed paths `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/rebuild/lexical*` and two unit folders. Its KPI on RETR-X-02 ("stops with a named reason … or shows a named parent expansion, as the owner rules") names neither W1-42's case nor the kept bundle. The owner's ruling it waits for (Q-1, `docs/plan/WAVE_2_WBS.md:1159`, recommendation "no expansion; W1-42's case is restated by the test designer") is not in the register. A test designer may revise an earlier ticket's tests "only when the KPIs name them for revision" (`template/governance/kernel/roles/independent-test-designer.md:8-11`).
  - **W2-14** (`.tickets/DAEO-7y6v.md`): its KPI says "W1-42's share case is green", but its only allowed path is `docs/plan/wave-2/argus-cycle/**`. The case can only turn green when `docs/plan/wave-1-exit/evidence/governance-share.json` exists and the exit report's Governance-share rows carry the same figures.
- **What follows.**
  - DEC-766 item 1: "an entry leaves when its fix closes". If W2-13 closes as specified, the RETR-X-02 entry leaves while its test is still red, and every later close is refused (`RED_NOT_ACCEPTED`).
  - DEC-762 item 2 and W2-19's KPI (`.tickets/DAEO-jzvg.md:94`): "the close of the ticket an entry names refuses while that entry is still listed". Once W2-19 lands, W2-13 and W2-14 cannot close at all, because their entries can only leave when their tests pass, and neither ticket can make them pass.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because W2-13, W2-14 and W2-19 are planned tickets on the critical path, and closing them is ordinary work.
- Consequence: other (fails closed: either every close after W2-13's is refused, or W2-13 and W2-14 cannot close).
- **Severity:** medium-high. No round: it is a plan correction before W2-13, W2-14 or W2-19 starts (package P-I2-1).

### Finding 2. Seven of the first refusal cases of `gov close` are refused for a missing checkpoint, whatever the gate they name does

- **Evidence.** In `tests/acceptance/W1-30/test_w1_30_close.py` (round 1, 2026-10-06), seven cases expect a refusal and build a project with no checkpoint: `test_close_requires_implements_trailer` (:123), `test_close_requires_task_trailer` (:135), `test_close_refuses_when_acceptance_tests_fail` (:257), `test_containment_blocks_close_for_out_of_scope_commit` (:273), `test_task_trailer_exact_match_not_substring` (:292), `test_regression_runs_to_end_all_failures_collected` (:386), `test_regression_failure_blocks_close` (:421). Since round 1 the watchdog refuses a close with no checkpoint (W1-30's KPI B1 with W1-25's thresholds, DEC-281 and DEC-321; held by `test_w1_30_watchdog.py::test_close_refuses_on_missing_checkpoint`; `src/gov/close/command.py:1092-1101`). So each is refused whatever its gate does. Three success cases of the same file assert only `ok` (`test_close_runs_acceptance_tests`, `test_close_runs_containment_check`, `test_close_runs_regression_tests_when_present`); the first two are AST-identical.
- **The suite's own designers judged this shape a defect before.** Round 6 replaced two cases of this same file because they had "no checkpoint, any refusal accepted", and eight more elsewhere because they "accepted any envelope", "asserted inside three conditions" or "asserted only if the close succeeded" (`tests/acceptance/W1-30/README.md:584-596`). The seven above, and `test_w1_30_iteration.py::test_successful_close_resets_count` (asserted only if the close succeeded), were left.
- **Planted faults** (§2.7). Seven faults switched off, one at a time in my clone, the gates these cases name. Every one of the ten round-1 cases still passed:
  - PF13 (trailer gate off) passed the two trailer cases;
  - PF5 and PF5b (acceptance run never made) passed the two acceptance cases;
  - PF4 (containment never judged) passed the two containment cases;
  - PF15 (task matched as a substring) passed the exact-match case;
  - PF11, PF12, PF12b, PF16 and PF16b (the regression stopped early, ignored or never run) passed the three regression cases.
- **What still holds the gates.** The later rounds and the builder tests caught every one of these faults:
  - PF4: 16 cases, among them all six of `test_w1_30_containment_places.py`;
  - PF5b: 91 cases in 19 files of W1-30's later rounds;
  - PF11: 15, among them seven of r9's every-finding file;
  - PF12b: 8; PF13: 6, among them r8's commits case; PF16b: 28.
  - PF15 only by one unit case, `test_gates.py::test_the_tickets_commits_are_those_whose_task_trailer_is_the_ticket`, which is regression evidence and not acceptance (DEC-042).
  - So the gates are covered. The round-1 cases give false assurance and cost 57 case-seconds of every close in the rehearsal.
- **Two cases I suspected are sound.** `test_w1_30_close.py::test_regression_includes_other_acceptance_folders` has its checkpoint and caught PF12 and PF16. `test_w1_30_iteration.py::test_successful_close_resets_count` asserts only if the close succeeded, but the close does succeed, and it caught PF18.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because an engineer changing a gate reads the cases named after it, and these pass whatever the gate does.
- Consequence: other (no gate is left uncovered while the later rounds stand).
- **Severity:** low-medium. A revision with `Rewrite-Reason:` (each project gets its checkpoint, each assertion names its gate's finding), riding in W2-67 (package P-I2-3).

### Finding 3. Most of W1-26's planted-defect and derived-scope cases pass whatever the check they name does, and they hide that the path-map check measures nothing

- **Evidence.**
  - **R1.** The suite's base project (`w1_26_support.Project`) is red under `gov check` before any defect is planted: exit 3, with six hard-block checks RED. Five of them are red because of what the fixture lacks (no tool registry, no store, no index, no `.gitleaks.toml`), so the project is red in any environment (§2.7).
  - `support.assert_red` asserts only that `gov check` as a whole failed (`tests/acceptance/W1-26/w1_26_support.py:462-467`). 27 cases judge their planted defect by it alone (§2.7). No case asserts that the base project is green.
  - **PF20** forced every check but `index-freshness` GREEN. It passed 26 of the 27, and the 27th tests a check PF20 does not reach. It passed 90 of the 113 functions that call the suite's `run_check`. 34 cases caught it, each by asserting a check's or a family's own status or finding.
  - Four "derived scope" cases assert that the output of two runs differs (`test_w1_26_derived.py:17, :35`; `test_w1_26_dec436.py:237, :364`). The output carries the commit id, so two runs on two commits always differ. Two more assert only that an envelope came back (`test_w1_26_derived.py:66, :79`).
  - `core-pathmap` reads `namespaces` as a list of `{name, paths}` (`src/gov/check/pathmap.py:47-58`). Every path map that follows the kernel schema holds a mapping (`template/governance/kernel/schemas/path-map.schema.json:9-13`), this repository's and W1-26's fixture alike (`w1_26_support.py:349`). So the hard-block G1 check finds nothing on any real path map: known row W2-M214 (triaged to W2-23, open). The two path-map cases of W1-26 and DEC-436's namespace case pass anyway, which is why the suite never showed it.
  - **The named check silenced.**
    - PF3 (`core-pathmap` measures nothing) is caught by none of 543 cases.
    - PF7 (the schema check ignores ticket files) is caught by one unit case. PF17 (it reads no record) is caught by three W1-26 record-type cases and 19 unit cases.
    - PF8 (the graph check reads no record) is caught by DEC-436's nested-path case and two unit cases.
    - Each time, the W1-26 cases named after the silenced check passed: the two path-map cases, the schema and graph planted defects, and the derived-scope cases.
  - **Five more cases assert words that are in every output** ("readiness", "openspec", "authority"), or loop over families that do not exist (§2.7).
  - **One case never runs its check.** `test_w1_26_dec436.py::test_family_only_unmeasured_check_not_green` declares a command with inner double quotes. The suite's writer does not escape them (`w1_26_support.py:273`), so the declaration is invalid YAML, and `gov check` exits 1 with `CHECK_DECLARATION_INVALID` before any check runs. The helper finds no family, `None`, which is "not GREEN", so the case passes (my run of its fixture, with and without PF20: sample row 9).
  - Three of these cases are known since 2026-10-20 as row W2-L379 (DEC-877 item 5); the rest are not on any list.
  - **W2-M214 has no ticket that can fix it.** The triage gives it to W2-23 ("fits W2-23's paths and KPIs", `docs/plan/WAVE_2_TRIAGE.md:313`), and W2-23's ticket lists the row (`.tickets/DAEO-kmcr.md:70`). But W2-23's allowed paths are `src/gov/adopt/**`, `src/gov/adapters/**`, the template path map and their unit folders (`:20-23`, `:96`), and none of its seven KPIs names the check (`:97-104`). `src/gov/check/pathmap.py` and W1-26's path-map cases are outside them.
  - **What covers it today, for this repository only.** W1-08's `test_w1_08_path_map.py` asserts that every tracked path is in a namespace (`:92`). It runs in the pre-close gate's (f) before every close (`tools/close_queue.sh:44-46`) and in every regression. A project adopted from the kernel has no W1-08. Its `gov check` is what it relies on.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because lens H's finding 1 is this case: two record files in no namespace passed `gov check` on 2026-10-21 and refused W2-02's close an hour later.
- Consequence: fails open for the check: CAP-38.b's path-map compliance family is GREEN on a path in no namespace. For the tests, other.
  - This repository is covered by W1-08 in gate (f).
  - For an adopted project the fail-open is feature-gated: it comes into force when W2-27 (EXAMIN adoption on a copy, `.tickets/DAEO-h4rh.md`) first relies on `gov check` in EXAMIN. So it is an **entry criterion of W2-27** (DEC-803), not a round now.
- **Severity:** medium-high for W2-27, low for this repository. The check's fix needs a carrier whose paths reach `src/gov/check/pathmap.py` (package P-I2-4). The three path-map case revisions ride with that fix (DEC-802), and the rest of the class go to W2-67 (package P-I2-3).

### Finding 4. W2-53's load-sensitive cases build entries in the form DEC-762 replaced, and the ratchet's field rule is still untested

- **Evidence.**
  - `w2_53_support.quarantine_entry` writes `{test, decision, reason}` (`tests/acceptance/W2-53/w2_53_support.py:181-182`), DEC-757's form. DEC-762 item 1 requires every `load_sensitive` entry to name its fix in `fixed_by`, and every one of the path map's entries does (31 at `4166d8d9`, 32 at `49c24ac9`). W2-19's KPI makes the ratchet refuse an entry without one (`.tickets/DAEO-jzvg.md:94`).
  - When W2-19 lands, the six cases of `test_w2_53_load_sensitive.py` that expect such an entry to count turn red, unless W2-19's test designer revises them. W2-19's ticket names lens H's field-rule case (DEC-890 item 2) but not these six.
  - No case uses an entry in today's form (with `fixed_by`), so a reader that rejects an unknown field would refuse every real entry and no test would see it.
  - PF6 drops the ratchet's field rule (`src/gov/close/ratchet.py:93-95`): an entry missing a field counts. W2-53's 57 cases and `tests/unit/close/test_ratchet.py` (63 in all) pass. Lens H's finding 19 holds at today's head.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because W2-19 rewrites this check as planned work.
- Consequence: other (fails closed: six red cases; or, if an engineer loosened the check to keep them green, the field rule would fail open).
- **Severity:** medium. It rides in W2-19 (DEC-802): its test designer gives the fixture `fixed_by` (`Rewrite-Reason: DEC-762 item 1`) and adds the field-rule case per list (package P-I2-3).

### Finding 5. A class of unit tests of the close runs a real nested pytest with a 60-second limit; it failed beside the whole regression under worksteal, and not in its own suite

- **Evidence.**
  - 15 functions of `tests/unit/close` start a real nested `pytest` through the close's `_run_tests` or `_check_tests` with a 60-second limit (my scan, `scripts/nested_scan.py`), in `test_run_and_record.py`, `test_parallel_runs.py`, `test_measured.py`, `test_every_finding.py` and `test_follow_up.py`. The nested run starts its own parallel workers (`-n auto` by default) beside the outer run's.
  - In the orchestrator's tool trials at `4166d8d9` (`log/tooltrials/20261022-0017/`), five of them failed in the worksteal run (b2), nine in the worksteal run with pytest-timeout (a-cost) and one in the shuffled run (d2), each with "the test run of tests exceeded the time limit of 60s" (my reading of `b2-worksteal.xml`, `a-cost-timeout.xml`). None failed in a real close or the rehearsal (`--dist load`, file order).
  - **My runs did not reproduce it** (verdict "not reproducible"; the trials hold the failure mode).
    - Alone ×3: 34 passed each time (16:46 to 17:00, load 15 to 32 by the end); the slowest nested case took 10.2 s.
    - In `tests/unit/close`'s own parallel run ×3: 386 passed each time (17:25 to 17:28, load 15 to 41 by the end); the slowest took 12.4 s.
    - The trials ran these cases beside the whole regression's heaviest cases under worksteal. A run of their suite alone does not reach that load, which is the condition worksteal brings (DEC-892 a).
  - None of them is on `load_sensitive` or the serial-only list. In a close, a failure would refuse it.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because any close under heavy load, or any change of order (DEC-889 item 12's glue, DEC-892 a's re-measured worksteal), can put them beside the heaviest cases.
- Consequence: other (fails closed: a refused close of about an hour for a ticket that did nothing wrong).
- **Severity:** medium. DEC-892 a already keeps worksteal out until the nested runs are bounded (W2-67 or W2-57). The fix is a revision of the unit cases (bounded nested runs: one worker, or a limit that a loaded machine meets), by the engineer under W2-67 (builder tests), not a list entry.

### Finding 6. The record-reading set decided in DEC-889 leaves out area 2's record-reading tests

- **Evidence.** DEC-889 item 2 starts the set from gate (f)'s four files and adds W2-54's green-here cases, W1-33's definitions and W1-49's window. Area 2 holds more tests whose outcome depends on records a record-only commit changes:
  - **W1-48** (172 cases, 0.6 s): every case reads `governance/project/tool-registry.yaml`, and the approval cases read the register (`w1_48_support.py:66-74, :180-190`). A register entry marked superseded turns them red, as W1-06's approvals case turned red on 2026-10-21 (lens H finding 1). Lens H's map: W1-48 executes no source file at all.
  - **W1-26**'s two probe-record cases read `docs/probes/*/*.md` of this repository (`test_w1_26_probe_records.py:268-300`). Every FULL ticket's lead commits one there (DEC-733).
  - **W1-40**'s registry cases read the gitleaks entry of the tool registry (`w1_40_support.py:47`).
  - **W1-42** (24 cases) reads the exit record, the Wave 1 ticket files under `.tickets/`, and the kernel's skill and brief templates the report names (`w1_42_support.py:70, :193, :203`; `test_exit_run_was_run_from_the_kernel_skill_and_brief_templates`).
  - **W1-30**'s `test_w1_30_r11_declared_here.py` (29 cases) reads `tests/acceptance/serial-only.txt`.
- **Why it matters.** Under W2-68's same-code reuse, the code fingerprint leaves record-only paths out. DEC-891 names `.tickets/`, `docs/probes/`, the register and the plan files as records. A record-only commit can turn these cases red, and a close would cite a passing run on a red head, as lens H's finding 18 showed for W1-06, W1-08 and W1-27.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because the orchestrator commits register entries, ticket-file edits and probe records every day.
- Consequence: fails open, feature-gated: only once W2-68's reuse is on. So it is an **entry criterion of W2-68** (DEC-803), not a round.
- **Severity:** high for W2-68 (package P-I2-2).

### Finding 7. Of `gov check`'s three exit-code cases, one skips in every run and one asserts nothing; a third case, written for another line, is the one that holds "exit 0"

- **Evidence.** `tests/acceptance/W1-26/test_w1_26_command.py::test_exit_0_when_all_checks_green` copies the whole working tree, runs `gov check`, and skips when it is not green ("the full project does not pass gov check yet", :41-46). A copy of this repository is never green. The rehearsal skipped it after 8.8 s, and my run after 11.8 s.
- **The KPI line's own cases.** The line is "exit code 0 when no hard-block check is red; a warning may be YELLOW without changing the exit code".
  - `test_warning_yellow_does_not_change_exit_code` (the same file) asserts only `if envelope["ok"]:`. R1 shows that fixture red, so it asserts nothing.
  - W1-38's generated-project case asserts its own check and family GREEN, not the exit (`test_w1_38_rulesync.py:348-358`).
- **PF21** (`gov check` fails whatever its checks say; W1-26, `tests/unit/check`, W1-07's envelope cases; 579 cases). One case catches it: `test_w1_26_installed_kernel.py::test_a_project_with_neither_layout_answers_as_today`, which W2-02 wrote under DEC-746. It asserts `ok` and exit 0 on a project without a kernel, where only the three built-in checks run. The two exit-code cases do not catch it: one skipped, one passed.
  - So "exit 0" is held, but by a case written for another KPI line.
  - "A warning does not change the exit code" is held by none.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because any change to `gov check`'s exit mapping (`src/gov/check/command.py:41-49`) or to its family rule is ordinary work.
- Consequence: other. A `gov check` that failed on warnings would refuse closes and be seen in the pre-close gate's (b), so the gap fails closed. And 8.8 case-seconds of every close go to no check.
- **Severity:** low (package P-I2-6: a retirement and a rewrite).

### Finding 8. The test package named `secrets` shadows the standard library, so its collection depends on what was imported first

- **Evidence.** `tests/unit/secrets/` is collected as a package named `secrets`. Any plugin that imports the standard library's `secrets` before collection makes its three files fail to import. That happened in W2-53's close of 2026-10-20 08:38 (lens H, A4) and in all five tool-trial runs (pytest-randomly or pytest-rerunfailures loaded; DEC-892 d). My reproduction, the same code in one process each: with the standard library's `secrets` imported before collection, "3 errors in 0.56s", each "No module named 'secrets.test_token_rule'; 'secrets' is not a package". Without it, "26 passed in 22.15s" (`logs/secrets-imported-first.out`, `logs/secrets-control.out`). The same in runs 2 and 3 of each (16:45 and 16:46, load 14): 3 collection errors each time with the import, 26 passed each time without. Known row W2-L373; DEC-892 makes it a condition of glueing those two plugins into the nightly.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because the plugins are planned glue (DEC-889 item 12), and any new plugin may import `secrets`.
- Consequence: other (fails closed: three collection errors refuse a close).
- **Severity:** low-medium. W2-L373's rename (the engineer's builder-test folder) before that glue.

### Finding 9. Planned changes will turn valid area-2 cases red, and the cards that make them do not name them

- **Evidence**, each case valid today:
  - **W2-57** (DEC-889 item 5: daemon and race cases tried in parallel, live and model cases to the nightly) changes `tests/acceptance/serial-only.txt`, which `test_w1_30_r11_declared_here.py` holds entry by entry (W1-16's daemon cases, W1-09's two races, the live and model files).
  - **W2-07** (DEC-868 item 3: a gate failure "spends no ratchet attempt"; DEC-892 item 1: the close reads a ticket's declared `acceptance_tests.path`) changes what W1-30's collection-error cases (`test_collection_error_refuses_close`, and the unit `test_a_collection_error_is_a_finding`) and `test_w1_30_no_acceptance_tests.py` expect.
  - **W2-66** (a path-scoped regression) changes what `test_regression_includes_other_acceptance_folders` expects: another ticket's failing suite outside the change's reach is not run by a scoped close.
  - **W2-08** (hooks back on) turns `test_no_lefthook_hook_is_installed_in_this_repository` red; its card already names it (F-M4, DEC-718).
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because each of these tickets is planned Wave 2 work that changes the behaviour as decided.
- Consequence: other (a red regression when the ticket lands, or a test designer surprised mid-round).
- **Severity:** low. Each goes into that ticket's card at the review point (DEC-889 item 14), as W2-08's already does.

### Finding 10. Three load-sensitive entries do not match the cause the records and my runs show

- **Evidence.**
  - W1-46's `…[static.crates.io]` entry gives the reason "a live session fails at setup under parallel load and passes alone". In W2-63's close (2026-10-22 00:11) it failed in the run and failed alone too (`close-queue-20261021-2241/close-DAEO-pl6k.json`). The orchestrator traced it to the host's reachability and added a network check to the pre-close gate (DEC-892 item 3).
  - W1-30's r13 entry gives the reason "fails once in the full regression at load about 25 and passes alone". My runs found the cause, and it is not parallel load as such. Alone, at a load of 19 rising to 29, it failed once in three. The close it starts is given `--timeout 5`, and under load the parallel run's workers take longer than that to reach the case, so its own premise fails ("the case had not begun when the run was cut", §2.2). So its entry helps only when the re-run alone finds a quiet machine, and the fix is the case's timing (W2-M384, W2-57), not a list entry.
  - The unit follow-up time-limit case passed in all six of my runs, alone and in its suite's parallel run (§2.2). Its entry's reason is not reproduced today.
  - In the four clean closes of Wave 2 (`CL-DAEO-7rr2`, `CL-DAEO-zflj`, `CL-DAEO-0rfi`, and `CL-DAEO-juee` today) no entry needed a re-run (`load_sensitive: []`).
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because every close re-runs a listed case that fails, and its entry's reason is what the orchestrator acts on.
- Consequence: other (an entry whose stated reason is not the cause does not help the close it is meant to help).
- **Severity:** low. The entries stay the owner's; W2-57's draft records the measured causes (DEC-890 item 2 already asks for dated fixes).

### Finding 11. The owner's new `load_sensitive` entry counted for nothing, and no test reads the real lists against the register

- **Evidence.**
  - The owner's commit `49c24ac9` (09:49) added DEC-892's W1-38 entry. In W2-50's close (10:28 to 11:40, exit 3), the ratchet refused it: "the load_sensitive entry tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md] (DEC-892) is refused: DEC-892 does not name the test …; it covers nothing" (`log/close-queue-20261022-0952/close-DAEO-kl5e.json`). It was one of the two findings that refused the close. The other was `PROBE_INVALID`.
  - The rule (R-2, `src/gov/close/ratchet.py:100-103`): the decision's text must hold the test's file path and its whole name with its parameters. DEC-892's text names "W1-38's `TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[…]`", and the file path appears 0 times in the entry (my count on `49c24ac9`'s register). The decisions behind the other W1-38, W1-07 and W1-30 entries (DEC-871, DEC-886, DEC-823) each name the file.
  - The orchestrator found the cause itself and recorded it as its own slip in DEC-894 (delegated), committed at `da3d77e1` (11:52). DEC-892's text there now names the file (my count: 1), and the orchestrator checks the entry "with the pinned ratchet's own reading before the next close". That is a one-off check. No standing check exists:
    - the record checks of DEC-868 and DEC-893 (`tools/record_checks.sh`) run the path-map, schema, mutation, authority, graph and context checks and the placeholder scan, and none reads a list entry the way the ratchet does;
    - every ratchet test (`tests/acceptance/W2-53/`, `tests/unit/close/test_ratchet.py`) builds its own path map in a fixture project. None reads this repository's two lists.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because the error came from preparing and committing an entry as DEC-862 (a) requires, and every new entry goes the same way.
- Consequence: other (fails closed: a 72-minute close was refused with its count spent, and every later close would have been refused until the text named the test at 11:52; nothing passes that should not).
- **Severity:** medium.
- **Proposal.** A record-reading case: every entry of this repository's `accepted_reds` and `load_sensitive` passes the ratchet's own R-2 and R-3 reading at the head. It is written by W2-19's test designer, which already carries the field-rule case (DEC-890 item 2). It runs in the pre-close gate's (f) and in the record checks, and is one of the record-reading set of P-I2-2. Until it exists, DEC-894's one-off check stays in the orchestrator's record checks as a standing step (P-I2-3).

### Finding 12. W2-57, which 28 of the 32 `load_sensitive` entries wait for, cannot reach the fix of four of them as planned

- **Evidence.**
  - W2-57's planned allowed paths (`docs/plan/WAVE_2_WBS.md:894`; no ticket file exists yet) are `tests/acceptance/W1-46/**`, W1-30's r13 file, `tests/acceptance/W2-57/**`, `src/gov/close/**`, `tests/unit/close/**` and its change record.
  - Four entries name W2-57 as their fix and need other paths:
    - W1-38's three rulesync entries (DEC-871 ×2, DEC-892). Their cause is `src/gov/adapters/portability.py:38` (`TIME_LIMIT = 10`, the probe of `rulesync --version`), and DEC-892 makes the fix "W2-57's first item … a test revision with a `Rewrite-Reason:`" of `tests/acceptance/W1-38/**`. Neither path is W2-57's.
    - W1-07's `doctor` envelope case (DEC-886, row W2-L409). It lives in `tests/acceptance/W1-07/`. The command it runs probes each tool's version with 5- and 10-second limits (`src/gov/doctor/command.py:136, :143, :204`), the same shape as the rulesync probe. Neither path is W2-57's.
  - DEC-883 item 5 and DEC-889 item 5 give W2-57 the serial-only list (`tests/acceptance/serial-only.txt`, 263 cases), and finding 9 shows that `test_w1_30_r11_declared_here.py` must be revised with it. Neither file is in W2-57's paths.
  - With W2-19's planned check (DEC-762 item 2: "the close of the ticket an entry names refuses while that entry is still listed"), W2-57 could not close while those four entries remain. Without that check, the entries would outlive the ticket meant to remove them, which is the shape of finding 1.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because W2-57 is planned Wave 2 work and its card is drafted at the review point (DEC-889 item 14).
- Consequence: other (fails closed, or entries that outlive their fix).
- **Severity:** medium. It is a plan correction before W2-57's ticket file is written (package P-I2-1, part B).

### Finding 13. Two of today's closes were refused after their full runs, for commit findings the close could have given before any test ran

- **Evidence.**
  - **W2-50** (`gov close DAEO-kl5e`, 10:28 to 11:40). The acceptance run, the parallel regression and the serial run all ran: 636, 14,830 and 263 passed. Then the close refused with `PROBE_INVALID` (W2-58's merge into W2-50's branch rewrote its probed files) and the R-2 refusal of finding 11.
  - **W2-58** (`gov close DAEO-5j8b`, 12:17 to 13:28, exit 3, repair ticket DAEO-aneq). The same three runs passed: 808, 14,658 (with W1-42's two accepted reds) and 263. Then the close refused with `WORK_WITHOUT_TASK` for seven commits (`log/close-queue-20261022-1153/close-DAEO-5j8b.json`):
    - each carries `Task: decision-record`, and three are the owner's own `Role: owner` ratchet commits (`49c24ac9`, `cf8219a8`, `8dfd54e9`), which DEC-862 (a) requires;
    - six change `governance/project/path-map.yaml`, and one changes W2-58's ticket file.
  - **Why W2-58 met it.** W2-58's allowed paths name the path map ("an `evaluation_sets` block only", DEC-864). The close reads a `Task:` that names no ticket as no task (DEC-500), and judges files, not blocks (`src/gov/close/command.py:523-537`, DEC-490). So every decision record that touches the path map during W2-58's life counts as W2-58's unmeasured work. The fix the decisions provide is accepted history from an owner decision that names each commit (DEC-734, DEC-891's standing rule).
  - **What the pre-close gate checks.** DEC-868's gate checks collection, `gov check`, the checkpoint, the tree, the trailers (`tools/trailer_gate.py`), the record-reading suites and the network. It does not check the task-less commits, the accepted history, the probe's validity on the head, or the ratchet's reading of its entries. The close checks all of these from the commits alone, but reports them only after it has run every test, because it gathers every finding into one refusal (DEC-492).
  - DEC-894's row W2-M403 asks for this for the probe ("the close could say so before the full regression runs"). The same holds for the other commit gates.
  - The gate's step (e) already shows the gain. On 2026-10-21 at 22:39 it stopped W2-62's first close attempt before any test ran: "commits of DAEO-juee without Implements: and not accepted history" (`log/close-queue-20261021-1924/queue.txt`).
  - No case of area 2 shows a ticket whose allowed paths name a record file that decision records change. W2-53's ticket-file cases and W2-01's accepted-history cases hold the gate's rule. The close behaved as decided.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because both refusals came from ordinary record commits and ordinary merges.
- Consequence: other (fails closed: about 70 minutes of the machine's quiet window and one iteration of the ticket's count spent for each, with nothing let through).
- **Severity:** medium (cost).
- **Proposal.** W2-07, which builds the pre-close gate into `gov close` (DEC-868), first runs the close's commit gates over the commits alone and stops before any test runs when they refuse: trailers, task-less work, accepted history, the probe gate and the ratchet's reading of its entries. It gives the same findings and spends no attempt (DEC-868 item 3), and rides along in W2-07 (DEC-802). Until then, the orchestrator's pre-close gate can run those gates of the pinned close as one more step, as gate (e) does for the trailers.

### Finding 14. 26 of the 32 `load_sensitive` entries name cases the close already runs alone, and W2-57's card contradicts DEC-889 on 24 of them

- **Evidence.**
  - The serial-only list holds W1-02's p95 case (`tests/acceptance/serial-only.txt:18`), W1-05's p95 case (`:19`), W1-46's whole live-session file (`:27`, since W1-30 round 11, `fdf18f7c`, 2026-10-08) and W1-19's whole real-model file (`:34`). The close runs them alone, after the parallel run (W2-58's and W2-62's close records list them under `serial-afterwards`).
  - Their 26 `load_sensitive` entries (W1-46 ×23, W1-19, W1-02, W1-05) give the reason "fails under parallel load and passes alone" (DEC-757, DEC-760, DEC-762).
  - The ratchet re-runs any listed red alone, whichever run it came from (`src/gov/close/command.py:996-1009`). So for these cases the entry is a second try under the same condition as the first, not relief from parallel load.
  - DEC-889 item 5 (owner, 2026-10-21) decides: "latency tests stay alone; live and real-model tests move to the nightly". So W1-46's and W1-19's 24 cases are to leave the close.
  - W2-57's card, drafted under DEC-813 before DEC-889, still asks that "W1-46's 36 live cases pass inside the full regression run under its usual parallel load, three runs in a row" (`docs/plan/WAVE_2_WBS.md:897`). Then "the orchestrator commits the removal of W1-46's 23 entries" (`:901`). The two cannot both hold.
  - The remaining six entries name cases that do run in the parallel run: W1-38 ×3, W1-07's `doctor` case, W1-30's r13 case and the unit follow-up case.
- The two questions (DEC-808): "Can an honest agent hit this in ordinary work?" "Does it fail open or lose work?"
- Ordinary work: yes, because every close applies the entries, and W2-57 is planned work that will act on its card.
- Consequence: other. The entries' recorded reason is not what they do: they let a serial case that failed alone pass on a second try alone. For an intermittent real fault in a latency case, that second try would pass the close, a narrow fail-open that the decisions accepted under another reason. And W2-57's card points away from the owner's later decision.
- **Severity:** medium (plan). W2-57's card follows DEC-889 item 5 at the review point: the live and real-model cases go to the nightly, and their 24 entries leave the list by the orchestrator's commit, a removal (DEC-861, DEC-766). The two latency entries stay or go by the owner's word (P-I2-1, group C).

## 6. Owner packages

Each package is in the six parts of DEC-818. Part 5 states the DEC-809 classification line of its findings first, then the recommendation. None blocks this audit: every item of the brief was measured or is stated as a limit.
- P-I2-1 blocks the clean close of W2-13, W2-14 and W2-57 (and, if deferred, every close after the first of them).
- P-I2-2 is an entry criterion of W2-68, and P-I2-4 one of W2-27.
- P-I2-3 shapes the cards drafted at the review point (DEC-889 item 14).
- P-I2-5, P-I2-6 and P-I2-7 are retirements, which only the owner decides.

### P-I2-1. Each list entry's route out: the fix ticket can reach the test it must turn green

1. **Context.** DEC-766: an entry leaves the ratchet's lists when its fix closes, and the lists only shrink. DEC-762 item 2 and W2-19's KPI: the close of a ticket an entry names refuses while that entry is still listed. Three groups of entries have no working route out:
   - **A, the two accepted reds** (DEC-757). W1-42's RETR-X-02 case is fixed by W2-13 and its governance-share case by W2-14. DEC-718 item 11 and F-M1 make their closing conditions the exit report's: "a kept bundle of RETR-X-02 with at least one parent expansion that names its parent, or the owner's ruling", and a measured share per programme "in `governance-share.json` … and W1-42's share case green".
   - **B, four `load_sensitive` entries that name W2-57**: W1-38's three rulesync cases (DEC-871, DEC-892) and W1-07's `doctor` case (DEC-886).
   - **C, 26 `load_sensitive` entries for cases the close already runs alone** (W1-46 ×23, W1-19, W1-02, W1-05: all on the serial-only list). DEC-889 item 5: "latency tests stay alone; live and real-model tests move to the nightly".
2. **What happened.**
   - **A** (finding 1).
     - The cases read the frozen exit record under `docs/plan/wave-1-exit/` (unchanged since `ca426ca9`) and fail alone, in every Wave 2 close and in the rehearsal.
     - W2-13's KPI does not name W1-42's case for revision, its allowed paths do not reach the kept bundle, and the owner's ruling (Q-1) is not in the register.
     - W2-14's KPI asks for "W1-42's share case green", but its only allowed path is `docs/plan/wave-2/argus-cycle/**`, and the case reads two files under `docs/plan/wave-1-exit/`.
   - **B** (finding 12).
     - W2-57's planned paths (WBS:894) hold neither `src/gov/adapters/portability.py` (the 10-second rulesync probe) nor `tests/acceptance/W1-38/**`, though DEC-892 makes that probe W2-57's first item.
     - They hold neither `src/gov/doctor/` nor `tests/acceptance/W1-07/**` for DEC-886's case.
     - They hold neither `tests/acceptance/serial-only.txt` nor `test_w1_30_r11_declared_here.py` for DEC-883 item 5.
   - **C** (finding 14).
     - The ratchet re-runs a listed red alone, whichever run it came from. For these 26 cases that is a second try under the same condition as the first, not the relief from parallel load their reason states.
     - W2-57's card still asks W1-46's live cases to pass "inside the full regression run under its usual parallel load" (WBS:897), against DEC-889 item 5.
3. **Why it matters.** As written, closing W2-13, W2-14 or W2-57 either removes an entry whose test is still red, so every later close is refused, or, once W2-19 lands, cannot happen at all. W2-13 and W2-14 are FULL tickets on Track A's path. W2-57 must close before W2-24 starts (DEC-813).
4. **Options** (DEC-105).
   - **(a) Apply now, keeping the decided conditions.**
     - A: the owner rules Q-1. W2-13's KPI names W1-42's RETR-X-02 case for its test designer, either restated to the ruling or kept and fed by a new kept bundle under the exit evidence folder. W2-14's allowed paths gain `docs/plan/wave-1-exit/evidence/governance-share.json` and the Governance-share rows of `EXIT-REPORT.md`.
     - B: W2-57's ticket file, when written, gains `src/gov/adapters/portability.py` (the probe only), `tests/acceptance/W1-38/**` (the test designer, with `Rewrite-Reason:`), `src/gov/doctor/command.py` (the probes only), `tests/acceptance/W1-07/**` (the same), `tests/acceptance/serial-only.txt` and `test_w1_30_r11_declared_here.py`, and a KPI per entry that its case passes in three full regressions under load.
     - C: W2-57's card follows DEC-889 item 5. The live and real-model cases move to the nightly, and their 24 entries leave the list by the orchestrator's commit (a removal, DEC-861). The two latency entries stay as a declared second try, or leave, as the owner rules.
     - Cost: three ticket-file edits, one card's paths and KPIs, and one ruling.
     - Risk: low. The Wave 1 record gains a dated Wave 2 addition, as DEC-718 foresaw ("entered for ARGUS in governance-share.json"). W2-57 grows by two small probe fixes, and loses its live-case KPI to the nightly.
   - **(b) Re-baseline.**
     - A: the owner moves both closing conditions to W2-13's and W2-14's own evidence and acceptance tests, and retires W1-42's two cases with their two `accepted_reds` entries in one owner commit.
     - B: the four entries' `fixed_by` moves to a small new ticket that owns the two probes and their tests, through an owner commit, because changing an entry is the owner's (DEC-862 (a)).
     - Cost: one owner decision and commit for each group, and one more small ticket.
     - Risk: low. The Wave 1 record stays as it was decided.
   - **(c) Defer** until W2-13 or W2-57 starts. Cost: nothing now. Risk: W2-19 or a close of W2-13 or W2-57 meets the deadlock unannounced.
5. **Classification (DEC-809):** finding 1: ordinary work yes; other (fails closed). Finding 12: ordinary work yes; other (fails closed). Finding 14: ordinary work yes; other (a narrow fail-open for an intermittent latency fault, under another reason). No round.
   **Recommendation: (a) for all three groups**, confidence medium. It keeps the owner's own closing conditions and makes them reachable. For A, (b) is equally safe and leaves the frozen record alone; it is the owner's call between keeping the Wave 1 report as the place the exceptions close and moving them to Wave 2's own evidence. For B, (a) keeps W2-57 the one place where load leaves the close, as DEC-813 and DEC-892 intend.
6. **What it blocks:** the clean close of W2-13, W2-14 and W2-57, and with option (c) every close after the first of them. Waiting costs nothing until W2-13, W2-14, W2-57 or W2-19 starts.

### P-I2-2. The record-reading set: add area 2's record-reading tests (DEC-889 item 2, for W2-68)

1. **Context.** DEC-883 item 3, as refined by DEC-889 item 2: a declared set of record-reading tests runs on every head, reused or not. It starts from gate (f)'s four files, with W2-54's green-here cases, W1-33's definitions and W1-49's window. W2-68 builds the reuse (DEC-890).
2. **What happened** (finding 6). Area 2 holds further cases whose outcome depends on records that a record-only commit changes (DEC-891 names `.tickets/`, `docs/probes/`, the register and the plan files as records):
   - W1-48, all 172 cases (the tool registry; the register's approvals), 0.6 s;
   - W1-26's two probe-record cases (`docs/probes/*/*.md`), 2.0 s;
   - W1-40's registry cases (the gitleaks entry, `test_w1_40_ci_installs.py`), 3.2 s;
   - W1-42, all 24 cases (the exit record, the Wave 1 ticket files, the kernel templates it names), under 0.1 s;
   - W1-30's `test_w1_30_r11_declared_here.py` (the serial-only list), 29 cases, 2.9 s;
   - the record-reading case of finding 11 once written (every list entry against the ratchet's R-2 and R-3 reading).
   The times are the rehearsal's case-seconds.
3. **Why it matters.** Reused on the code fingerprint alone, a close after a record-only commit would cite a passing run while these cases are red (lens H's finding 18, here for area 2's tests). W1-06's approvals case turned red exactly this way on 2026-10-21.
4. **Options.**
   - **(a)** Add these cases to the declared set in W2-68's card. Cost: about 9 case-seconds per head. Risk: none added.
   - **(b)** Map their record paths to their suites in W2-66's path-to-suite map instead, and let W2-68 widen on those paths. Cost: the same run time, more mapping rules. Risk: a record path missed in the map fails open.
   - **(c)** Leave the set as decided. Risk: fails open under reuse.
5. **Classification (DEC-809):** finding 6: ordinary work yes; fails open, feature-gated, so an entry criterion of W2-68 (DEC-803), not a round. Finding 11: ordinary work yes; other (fails closed).
   **Recommendation: (a)**, confidence high.
6. **What it blocks:** W2-68's test design. Waiting costs nothing if decided before W2-68's tests are written.

### P-I2-3. Where the revisions of this review go

1. **Context.** No test is changed by this review. Revisions go to independent test designers (acceptance tests) or engineers (builder tests), each with a `Rewrite-Reason:`, in the owning ticket or a small new one. DEC-889 item 7 plans W2-67 (test hygiene) after W2-66; DEC-889 item 14 drafts W2-57's, W2-66's, W2-67's and W2-68's cards at a review point.
2. **What happened.** This review found 58 weak, 16 outdated, 23 flaky and 10 not reproducible functions (§2, findings 2 to 5, 7 to 11 and 14). Each needs a home:
   - **W2-19** (resumes anyway):
     - W2-53's six load-sensitive cases gain `fixed_by` (`Rewrite-Reason: DEC-762 item 1`), beside the field-rule case per list it already carries (DEC-890 item 2);
     - a record-reading case that every real list entry passes the ratchet's R-2 and R-3 reading (finding 11).
   - **W2-M214's carrier** (P-I2-4): W1-26's two path-map cases and DEC-436's namespace case assert core-pathmap's own entry (`Rewrite-Reason: the cases passed on gov check's overall exit while the check measured nothing, W2-M214`).
   - **W2-67** (test hygiene):
     - W1-30's 13 weak cases (the ten round-1 cases of finding 2, and the disposition, receipt and checker cases of §2.7);
     - W1-26's other 42 weak cases (finding 3, W2-L379's three among them, `test_warning_yellow_does_not_change_exit_code` of P-I2-6, and the case whose declaration is invalid YAML, with its support's writer);
     - the nested-run unit class of finding 5, whose runs need bounding before worksteal returns (an engineer's builder-test change);
     - the `secrets` folder's rename (W2-L373, finding 8).
   - **W2-57** (its card): W1-30's r13 case's timing (`Rewrite-Reason: W2-M384`), the probe fixes of P-I2-1 B, and the cases of finding 9 that its serial-list work turns red.
   - **W2-07, W2-66, W2-08**: the cases of finding 9, named in their cards at the review point. W2-07 also gets the commit gates of finding 13.
3. **Why it matters.** Without a named home, each revision waits for a red, and a weak case keeps passing.
4. **Options.**
   - **(a)** Widen W2-67's card with the named cases, and add the rest to the cards above at the review point. Cost: W2-67 grows by about 55 revised acceptance cases and 15 builder cases, by my estimate 600 to 900 lines of test code, most of it one fixture line (a checkpoint) and one assertion per case. Risk: low.
   - **(b)** One new small test-revision ticket for area 2's weak cases, beside W2-67. Cost: one more ticket to plan and close. Risk: low.
   - **(c)** Wave 3's test-hygiene pass. Risk: the weak cases keep passing for a wave.
5. **Classification (DEC-809):** findings 2, 4, 5, 7, 8 and 9: ordinary work yes; other. Finding 3: ordinary work yes; other for the tests, and fails open for the check, which is P-I2-4's. No round.
   **Recommendation: (a)**, confidence medium-high.
6. **What it blocks:** nothing. Waiting costs about 30 s of every close on cases that cannot fail, and the risk that a gate change passes on a weak case.

### P-I2-4. A carrier for W2-M214: the path-map check that measures nothing (an entry criterion of W2-27)

1. **Context.** `core-pathmap` is the hard-block G1 check of CAP-38.b's path-map compliance family. The triage gives row W2-M214 ("core-pathmap reads namespaces as a list where path maps hold a map") to W2-23 (`docs/plan/WAVE_2_TRIAGE.md:313`). DEC-425 and DEC-454: what was not measured is never GREEN. DEC-803: a feature-gated risk is an entry criterion of the ticket that switches the feature on.
2. **What happened** (finding 3).
   - `src/gov/check/pathmap.py:36-49` returns no finding, so GREEN, in four cases:
     - no path map;
     - a path map YAML cannot read;
     - a path map that is not a mapping;
     - namespaces held as a mapping, which is the kernel schema's form and every real path map's.
   - PF3, the check made to measure nothing, is caught by none of W1-26's 412 cases or `tests/unit/check`'s.
   - W2-23's allowed paths and KPIs do not reach `src/gov/check/pathmap.py` (`.tickets/DAEO-kmcr.md:20-23, :97-104`).
   - This repository is covered by W1-08's case in the pre-close gate's (f). A project adopted from the kernel is not.
3. **Why it matters.** EXAMIN's `gov check` would show path-map compliance GREEN for any file in no namespace, the very defect that refused W2-02's close here (lens H's finding 1). W2-27 (EXAMIN adoption on a copy) is the first ticket that relies on it.
4. **Options.**
   - **(a) A small new ticket**, before W2-27 starts. STANDARD, engineer: `src/gov/check/pathmap.py` and `tests/unit/check/**`. The check reads the mapping form, and is unmeasured (never GREEN) when the path map is missing, unreadable or of another shape. Its test designer revises W1-26's two path-map cases and DEC-436's namespace case to assert `core-pathmap`'s own entry (`Rewrite-Reason:` as in P-I2-3). Cost: about 30 lines of code and three revised cases, one STANDARD close. Risk: low; it is judged by the pinned judge once W2-59 lands (DEC-822).
   - **(b) Widen W2-23** with `src/gov/check/pathmap.py`, `tests/unit/check/**` and a KPI, and name the three cases for its test designer. Cost: the same work inside a FULL ticket with a broad scope. Risk: W2-23's other work delays the fix past W2-27's start.
   - **(c) Leave it with W2-23 as it stands.** Risk: no ticket can fix it, and W2-27 starts on a check that fails open.
5. **Classification (DEC-809):** finding 3: ordinary work yes; fails open, feature-gated for adopted projects, so an entry criterion of W2-27 (DEC-803), not a round now.
   **Recommendation: (a)**, confidence medium-high.
6. **What it blocks:** W2-27's start, as an entry criterion. Waiting costs nothing until then.

### P-I2-5. Retire `tests/acceptance/W1-30/test_w1_30_close.py::test_close_runs_containment_check`

1. **Context.** W1-30's round-1 case for "gov close runs the containment check" (KPI S1, CAP-13.a).
2. **What happened.** Its body is AST-identical to `test_close_runs_acceptance_tests` in the same file: a green ticket closes (`ok` true). With the containment judgement planted off (PF4), it passed, while 16 cases failed, all six of `test_w1_30_containment_places.py` among them. The containment KPI is held by those six cases and by MWA-04's case once its project gets a checkpoint (P-I2-3).
3. **Why it matters.** It names a gate it cannot check, and duplicates another case. Cost: 5.1 case-seconds per close (the rehearsal), one green close in a fixture project.
4. **Options.** (a) Retire it. (b) Keep it as a duplicate. (c) Rewrite it to assert the containment judgement's own result (then it duplicates `test_w1_30_containment_places.py`).
5. **Classification (DEC-809):** finding 2 (this case): ordinary work yes; other. No round.
   **Recommendation: (a)**, confidence high.
6. **What it blocks:** nothing.

### P-I2-6. Retire `tests/acceptance/W1-26/test_w1_26_command.py::test_exit_0_when_all_checks_green`, and give its KPI line a case that can fail

1. **Context.** W1-26's case for "exit code 0: no hard-block check is RED" (KPI S1, CAP-39.d). DEC-042: acceptance criteria are held by acceptance tests; builder tests are regression evidence only.
2. **What happened.**
   - It copies the whole working tree, runs `gov check`, and skips unless the copy is green ("the full project does not pass gov check yet", `:41-46`). A copy of this repository is never green. It skipped in the rehearsal after 8.8 s, and in my run after 11.8 s ("the full project does not pass gov check yet", `logs/w1-26-par1.xml`).
   - The only other case of the KPI line, `test_warning_yellow_does_not_change_exit_code`, asserts only `if envelope["ok"]:`. R1 shows its fixture exits 3 with four hard-block checks red, so it asserts nothing either.
   - PF21 (`gov check` fails whatever its checks say) is caught by one case of 579: `test_w1_26_installed_kernel.py::test_a_project_with_neither_layout_answers_as_today` (W2-02, DEC-746), which asserts `ok` and exit 0 on a project without a kernel. So "exit 0" is held, by a case written for another line, and "a warning does not change the exit code" is held by none (finding 7).
3. **Why it matters.** Two cases name the KPI line, and neither can fail. One costs a whole-tree copy and a `gov check` per close (8.8 case-seconds).
4. **Options.**
   - **(a)** Retire it, and have W1-26's other case rewritten by a test designer on a fixture whose only declarations are its own: one passing hard-block check and one failing warning, with the kernel's declarations removed, asserting `ok` and exit 0 unconditionally. The installed-kernel case already shows such a project can be green. The rewrite holds both "exit 0" and "a yellow warning does not change the exit code" (`Rewrite-Reason: the fixture was red, so the case asserted nothing`; W2-67, P-I2-3).
   - **(b)** Rewrite this case instead, on the same kind of fixture. Then the two cases duplicate each other.
   - **(c)** Keep both. They stay unable to fail.
5. **Classification (DEC-809):** finding 7: ordinary work yes; other (the gap fails closed). No round.
   **Recommendation: (a)**, confidence medium-high.
6. **What it blocks:** nothing.

### P-I2-7. Retire `tests/acceptance/W1-30/test_w1_30_receipt.py::test_unmeasurable_inputs_listed_with_reason`

1. **Context.** W1-30's round-1 case for KPI B5, "inputs that cannot be measured are listed with a 'not measured' reason". DEC-470 (delegated, 2026-10-07, under DEC-454's rule that nothing is closed or recorded that was not measured): "A ticket naming a source that does not resolve is refused … The older case that expected a close record listing the missing source with a reason gives way and is rewritten to the refusal."
2. **What happened.** The rewritten case exists (`test_unresolvable_source_refuses_the_close`, the same file). This older one was left. On a green project, it loops over the close record's inputs and asserts a reason only for an input with no hash (`test_w1_30_receipt.py:249-260`). Since DEC-470 no written close record holds such an input, so the loop never asserts. It passed in my W1-30 run and under PF9.
3. **Why it matters.** It describes a behaviour the decisions removed, and can never fail. Cost: 5.4 case-seconds per close (the rehearsal), one green close in a fixture project.
4. **Options.** (a) Retire it. (b) Rewrite it to assert that a close record holds no input without a hash, which is a weaker form of `test_unresolvable_source_refuses_the_close`. (c) Keep.
5. **Classification (DEC-809):** this case (an obsolete test, no finding of its own): ordinary work yes; other. No round.
   **Recommendation: (a)**, confidence high.
6. **What it blocks:** nothing.
