---
id: EXP-W2-66-scoped-close
type: research
status: ACTIVE
state_class: EVIDENCE
---

# Evidence record: the path-scoped close of W2-66, timed against the full close, its catch rate on lens H's planted faults, and the ladder's fixture trial

- **Ticket:** `DAEO-c1uz` (W2-66), its KPI "Measured and reported in docs/research/W2-66-scoped-close.md, on a quiet
  machine" [DEC-889 item 11 e], and the ladder's fixture trial [DEC-884 item 4].
- **Run:** 2026-10-24, by W2-66's engineer, on this machine (20 processors), in the worktree
  `/home/usain/gov-os-worktrees/W2-66` at `c9686606`. Every run used this worktree's `src/`
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src`; `gov.__file__` is
  `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`) and `TMPDIR=/tmp/gov-os-lead-W2-66`.
- **Nothing of the repository was changed** but this file. The selection was computed for given changed paths and the
  close's own test-run functions were called for it; the fixture trial ran `gov close` only in a fixture project built
  from nothing under `/tmp/gov-os-lead-W2-66/eng-3/` (removed afterwards).

## Questions

1. How long does a typical scoped close (one module outside the shared core, with its tests) take on this repository,
   against the full close?
2. What is the selection's catch rate on lens H's planted faults, the three widest-reaching modules included?
3. What does W2-66 alone give towards DEC-880's target of a typical close under about 15 minutes?
4. Does a real `gov close` of this worktree's code, on a fixture project, run everything for a change in the shared core,
   the module's suites for a change in one module, and the record-reading set for a record-only change?

## Verdict

- **Time.** The typical scoped close's test runs took **687 s (11.5 min)**: the acceptance run 9.2 s, the regression's
  parallel run 676.6 s, the red's judgement 1.4 s. **No serial-only case was selected, so no serial run was made.**
  The full close's tests take 44.1 min for the parallel run alone (the lead's run of 2026-10-23) and 60 min with the
  serial-only tests (DEC-883: 31 + 29 min). So the scoped close runs **21 % of the cases** (3,348 of 15,649) in
  **about 26 % of the parallel run's time** and about 19 % of the test time of DEC-883's close.
- **One case is 611 s of the 677.** W2-54's `test_gov_check_gives_context_reproducibility_green_here` (a record-reading
  case) runs a whole `gov check` on the live tree. Every other case of the run ended within 71 s. So the record-reading
  set, not the module's own suites, sets the length of a typical scoped close here (see "What the time shows").
- **Catch rate: 32 of 32 (100 %)** of lens H's planted faults. 24 faults are in modules outside the shared core: each
  scoped selection reaches at least one whole catching suite. The 8 in the shared core (the six of the three
  widest-reaching modules and the two in `src/gov/cli/main.py`) run the full regression, so every catching suite runs.
  Lens H's declared map caught 22 of 22 (its report) and 32 of 32 (its rest run of 2026-10-22).
- **The 15-minute target** is not reached by W2-66 alone. A typical close under about 15 minutes is reached by **W2-66
  together with W2-68** (batching and same-code reuse), **W2-57's serial rework** and **worksteal** (after W2-70 and
  W2-67) [DEC-889 item 11 e]. W2-66 alone takes a typical close's tests from about 60 min to 11.5 min, as measured here;
  the close's other parts and the queue's rebuild and `gov check` stay as they are.
- **The fixture trial held:** three real closes of this worktree's `gov close`, each green, each evidence block as the
  KPIs state it: `scope: full` with `why_full: SHARED_CORE` for the shared core; `scope: scoped` with the overlapping
  ticket's suite and `tests/unit` for one module; the record-reading set with the others left out for a record-only
  change.

## 1. The typical scoped close on this repository

### Method

- **The change:** `src/gov/status/command.py`, the file of lens H's first planted fault, outside the shared core. Its
  owning ticket is W1-32 (`DAEO-8goq`), so the close is W1-32's: its acceptance suite `tests/acceptance/W1-32/` is the
  acceptance run and is left out of the regression run.
- **The base:** the code (`gov.close.select.base`) **finds no recorded base here**: no full close record under
  `docs/close/` and no green night under `docs/close/nightly/` names a commit of this branch, so a close here would
  run the full regression with `why_full: BASE_UNKNOWN`. **The selection was therefore computed for the given changed
  path directly:** `gov.close.select.plan(root, "W1-32")` with its `base()` given `HEAD` and its `changed()` given
  `["src/gov/status/command.py"]`; every other rule (the test map, the tickets, the helpers, the couplings, the
  record-reading set, the form) is the code's own.
- **The runs:** the close's own functions, in the close's order and form (`gov.close.command._check_acceptance`, then
  `_check_tests` on `tests/` with the acceptance folder ignored, then `_check_reds`), with the selection as the scope:
  `-n auto`, `--dist load`, the serial-only plugin, `--timeout=900 --timeout_method=signal`,
  `-o tmp_path_retention_policy=failed`, `-p no:cacheprovider`, the `--ignore=`/`--deselect=` form, JUnit XML for each
  run. The path map's `load_sensitive` list is in force, so each run told its results to the ratchet as in a close.
  The close's gates (commit gates, the pre-close collection and `gov check`, the context, the records) were not run.
- **The machine:** no `CLOSE-RUNNING` file; the 1-minute load waited under 20; the run held `flock
  /tmp/gov-os-verify.lock` (no wait).

Command (one, foreground of its shell, waited on by an exit file):

    flock /tmp/gov-os-verify.lock sh -c 'cat /proc/loadavg …; PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src
      TMPDIR=/tmp/gov-os-lead-W2-66 python3 timed_scoped.py /home/usain/gov-os-worktrees/W2-66 W1-32
      /tmp/gov-os-lead-W2-66/eng-3/junit timed.json src/gov/status/command.py; …; cat /proc/loadavg …'

### The selection

`scope: scoped`, `why_full: []`, base and head `c9686606`, changed `src/gov/status/command.py`.

| Selected | Why |
|---|---|
| `tests/acceptance/W1-32/` | `OWN` (the acceptance run) and `OVERLAP` (`DAEO-8goq`'s `allowed_paths`) |
| `tests/unit` | `UNIT` |
| W1-07's three contract files (`test_w1_07_envelope.py`, `test_w1_07_read_act.py`, `test_w1_07_registry.py`) | `EVERY_CLOSE` |
| the 26 targets of the record-reading set, in 14 suites: the whole of `W1-42/` and `W1-48/`, three single cases, the rest whole files (W1-07's envelope file is also every-close) | `RECORD_READING` |

**Left out:** 185 targets, each `NOT_REACHED`:
- 43 whole acceptance suites (among them W1-09, W1-16, W1-19, W1-46 and W2-58);
- 142 test files of the 12 suites some target reaches in part.

Also 31 `--deselect=` for the other top-level tests of the three files named by a single case (W1-01's history file,
W1-10's register and completeness files). **Serial-only:** none of the list's 54 entries is inside the selection
(`gov.close.select.runs` is false for each), so the close makes no serial-afterwards run.

### Results

| Phase | Form | Wall time | pytest's time | Cases | Passed | Failed | Skipped |
|---|---|---|---|---|---|---|---|
| acceptance (W1-32) | parallel, `-n auto` | 9.2 s | 9.09 s | 81 | 81 | 0 | 0 |
| regression | parallel, `-n auto`, `--dist load` | 676.6 s | 616.97 s | 3,267 | 3,265 | 1 | 1 |
| regression | serial-only cases afterwards | none selected, not run | — | 0 | — | — | — |
| the reds judged (`_check_reds`) | — | 1.4 s | — | — | — | — | — |
| **total** | | **687.2 s (11.5 min)** | | **3,348** | 3,346 | 1 | 1 |

- **Load:** `12.29 46.56 52.85` at the start (09:06:54 UTC), `65.47 71.07 61.56` at the end (09:18:23 UTC). The rise is
  the run's own: 20 workers and the `gov` and gitleaks processes its cases start. The 5- and 15-minute figures at the
  start still carried the busy hour before; the machine was quiet by the brief's rule (1-minute load under 20, no
  close running, the lock held) but not idle.
- **The red:** `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`,
  "context-reproducibility is RED here: … `.tickets/DAEO-9nys.md` is a file of the ticket folder that the store holds no
  record of (… or the store was loaded before it)": this worktree's store predates ticket files on the branch. It is a
  record-reading case, so the full regression runs it too; it is not a miss of the selection.
- **The skip:** `tests/unit/retrieval/test_lexical.py::test_the_chunking_is_the_carried_one` ("could not import
  'govbridge.core.chunking'"). The evidence block names it with its reason; skip count 1.
- **Summed case time** 2,021.8 s, of which W1-07's every-close files 1,038.8 s (209 cases), W2-54's green-here file
  611.2 s (4 cases), `tests/unit` 175.8 s (2,604 cases), W1-27's record-reading files 149.3 s (56 cases).
- **The slowest cases:** W2-54's context-reproducibility case 611.2 s; then W1-07's `check` and `status` cases,
  60 to 71 s each.

### The full close, for comparison (measured figures, not re-run here)

| Run | Where | Wall time | Cases | Load |
|---|---|---|---|---|
| the lead's full parallel run, close's form, no retention option, serial-only run not made | this worktree at `a384480a`, 2026-10-23 | **2,648.76 s (44.1 min)** | 15,613 passed, 6 failed, 30 skipped | — |
| the retention trial's full parallel run, with the option (DEC-905) | a clone of `de2b5bf1` | **2,459 s** | 15,464 passed, 30 skipped, 3 failed, 1 error | about 25 |
| the register's measured close (DEC-883) | the close queue, 2026-10-21 | **72 min** `gov close`: the parallel regression 31 min, the serial-only tests 29 min, the ticket's own suite 24 s | — | — |

The lead's verification run of this round, made after this report, is added by the lead's return.

### What the time shows

- **W2-66 cuts the test runs, not the close's other parts.** The typical scoped close's tests took 11.5 min, against
  44.1 min (the lead's full parallel run alone) or about 60 min (DEC-883's parallel and serial runs).
- **The serial-only half falls away** for this change: DEC-883's 29 min of serial-only tests are of suites the
  selection leaves out (W1-16's 35 entries, W1-50's 3, W1-09's 2, and so on).
- **The record-reading set sets the length.** W2-54's context-reproducibility case is 611 s of the parallel run's 617 s
  of pytest time; it runs `gov check --json` on the live tree. The KPI has it read the pre-close gate's own `gov check`
  result instead (`GOV_CLOSE_CHECK_RESULT`, given by `gov close --check-result`). W2-54's suite does not read that
  variable yet: no file under `tests/acceptance/W2-54/` names it. Until it does, every scoped close here pays for one
  full `gov check` inside its regression.
- **Without that one case** the rest of the run is 1,410.6 s of summed case time over 20 workers, with no case over
  71 s. That would put the parallel run at about 1.5 to 3 minutes. This is an estimate from the JUnit XML, not a
  measurement.

## 2. The catch rate on lens H's planted faults

### Method

- **The faults:** lens H's archived analysis `governance/project/orchestration/main/evidence/lens-H/analysis_b2.json`
  on the branch `record/w2` (`git show record/w2:<path>`). It has 32 entries, one per planted fault, each with its
  `file` and `F_suites`, the suites whose tests failed with it (`unit` is `tests/unit`). Lens H's report ran 23 of
  them (22 valid); its rest run of 2026-10-21 and 2026-10-22 (`rest.log` beside it) ran the other nine, the six of
  the three widest-reaching modules among them. The README beside these files describes `analysis_a6.json` and
  `analysis_b2.json` the wrong way round. The `B2:` ids show that `analysis_b2.json` holds the planted faults.
- **The selection:** for each fault, `gov.close.select.plan` for a change to the fault's `file` alone, computed as in
  §1, for a ticket with no acceptance suite of its own, so that no ticket's own suite adds to what is caught.
- **Caught:** the selection runs at least one of the fault's catching suites whole (a full regression runs them all).
  A suite the selection reaches only in part (record-reading files) is not counted.

### Results

| # | Fault | Catching suites (`F_suites`) | What W2-66's selection runs (whole suites; with the every-close and record-reading targets) | Catching suites it runs | Caught | Lens H's declared-map recall |
|---|---|---|---|---|---|---|
| 1 | `src/gov/status/command.py:65` compare-flip | W1-32, unit | scoped: unit, W1-32 | W1-32, unit | yes | 1.0 |
| 2 | `src/gov/status/command.py:105` negate-condition | W1-32 | scoped: unit, W1-32 | W1-32 | yes | 1.0 |
| 3 | `src/gov/checkpoint/record.py:169` return-none | W1-25, W1-30, unit | scoped: unit, W1-25, W1-30, W1-31 | W1-25, W1-30, unit | yes | 0.6 |
| 4 | `src/gov/checkpoint/record.py:139` or-and | W1-25, W1-29, W1-30, W2-01, W2-02, W2-53, unit | scoped: unit, W1-25, W1-30, W1-31 | W1-25, W1-30, unit | yes | 0.1 |
| 5 | `src/gov/tasks/claims.py:37` negate-condition | W1-09, W1-28, W1-32, unit | scoped: unit, W1-30, W1-09 | W1-09, unit | yes | 0.1 |
| 6 | `src/gov/adapters/portability.py:114` return-none | unit | scoped: unit, W1-38, W1-15, W1-26, W1-30 | unit | yes | 1.0 |
| 7 | `src/gov/decisions/checker.py:222` return-none | W1-11, unit | scoped: unit, W1-11, W1-26, W1-30 | W1-11, unit | yes | 1.0 |
| 8 | `src/gov/cli/main.py:121` return-none | unit | full (`SHARED_CORE`) | unit | yes | 1.0 |
| 9 | `src/gov/doctor/command.py:217` negate-condition | unit | scoped: unit, W1-39, W1-41, W1-27 | unit | yes | 1.0 |
| 10 | `src/gov/pause/command.py:288` return-none | W1-50, unit | scoped: unit, W1-28, W1-50 | W1-50, unit | yes | 1.0 |
| 11 | `src/gov/context/__init__.py:196` and-or | W1-24, unit | scoped: unit, W2-54, W1-30, W1-41, W1-24, W1-26, W1-31 | W1-24, unit | yes | 1.0 |
| 12 | `src/gov/tasks/claims.py:73` and-or | W1-09 | scoped: unit, W1-30, W1-09 | W1-09 | yes | 1.0 |
| 13 | `src/gov/pause/command.py:157` compare-flip | W1-28, W1-50, unit | scoped: unit, W1-28, W1-50 | W1-28, W1-50, unit | yes | 1.0 |
| 14 | `src/gov/launch/launcher.py:244` negate-condition | W1-28, W1-46, unit | scoped: unit, W2-58, W1-32, W1-28, W1-46, W2-50, W1-50 | W1-28, W1-46, unit | yes | 1.0 |
| 15 | `src/gov/telemetry/counter.py:102` drop-not | W1-30, W1-31 | scoped: unit, W1-30, W1-31, W2-07 | W1-30, W1-31 | yes | 1.0 |
| 16 | `src/gov/lock/__init__.py:123` compare-flip | W1-39, unit | scoped: unit, W1-39 | W1-39, unit | yes | 1.0 |
| 17 | `src/gov/telemetry/counter.py:74` or-and | W1-30, W1-31, unit | scoped: unit, W1-30, W1-31, W2-07 | W1-30, W1-31, unit | yes | 1.0 |
| 18 | `src/gov/readiness/checker.py:108` compare-flip | W1-13, W1-14, W1-32, unit | scoped: unit, W1-30, W1-13, W1-26 | W1-13, unit | yes | 0.56 |
| 19 | `src/gov/readiness/checker.py:140` and-or | W1-13, W1-14, W1-32, unit | scoped: unit, W1-30, W1-13, W1-26 | W1-13, unit | yes | 0.56 |
| 20 | `src/gov/lock/__init__.py:94` return-none | W1-39, unit | scoped: unit, W1-39 | W1-39, unit | yes | 1.0 |
| 21 | `src/gov/cli/main.py:184` negate-condition | W1-07, W1-13, W1-20, W1-25, W1-28, W1-32, W1-33, W1-39, W1-40, W1-46, W1-50 | full (`SHARED_CORE`) | all 11 | yes | 0.59 |
| 22 | `src/gov/doctor/command.py:159` drop-not | W1-27, unit | scoped: unit, W1-39, W1-41, W1-27 | W1-27, unit | yes | 1.0 |
| 23 | `src/gov/adapters/portability.py:50` return-none | W1-38, unit | scoped: unit, W1-38, W1-15, W1-26, W1-30 | W1-38, unit | yes | 1.0 |
| 24 | `src/gov/launch/launcher.py:227` negate-condition | W1-28, W1-32, W1-33, W1-38, W1-46, W1-50, W2-50, unit | scoped: unit, W2-58, W1-32, W1-28, W1-46, W2-50, W1-50 | W1-28, W1-32, W1-46, W1-50, W2-50, unit | yes | 0.99 |
| 25 | `src/gov/store/loader.py:116` return-none | W1-10, unit | full (`SHARED_CORE`) | all 2 | yes | 1.0 |
| 26 | `src/gov/context/__init__.py:358` return-none | W1-24, W1-30, W1-41, W2-01, W2-02, W2-53, W2-54, unit | scoped: unit, W2-54, W1-30, W1-41, W1-24, W1-26, W1-31 | W1-24, W1-30, W1-41, W2-54, unit | yes | 0.83 |
| 27 | `src/gov/decisions/checker.py:227` return-none | W1-11, W1-26, W1-30, W2-01, W2-02, W2-53, unit | scoped: unit, W1-11, W1-26, W1-30 | W1-11, W1-26, W1-30, unit | yes | 0.28 |
| 28 | `src/gov/config/loader.py:111` negate-condition | 16 suites and unit | full (`SHARED_CORE`) | all 17 | yes | 0.1 |
| 29 | `src/gov/tasks/tickets.py:22` return-none | 16 suites and unit | full (`SHARED_CORE`) | all 17 | yes | 0.46 |
| 30 | `src/gov/tasks/tickets.py:19` compare-flip | 16 suites and unit | full (`SHARED_CORE`) | all 17 | yes | 0.46 |
| 31 | `src/gov/config/loader.py:214` negate-condition | W1-07, W1-25, W1-27 | full (`SHARED_CORE`) | all 3 | yes | 0.5 |
| 32 | `src/gov/store/loader.py:197` return-none | 19 suites and unit | full (`SHARED_CORE`) | all 20 | yes | 0.33 |

- **The rate: 32 of 32.** Over the 24 faults outside the shared core: 24 of 24, each reaching a whole catching suite.
  Over the 22 valid faults of lens H's report (rows 1 to 22; rows 8 and 21 are now full): 22 of 22, as lens H's
  declared map (22 of 22). Row 23 is the fault its report set aside and its rest run re-ran.
- **`tests/unit` carries three:** rows 6 and 9 are caught only by `tests/unit` in the scoped selection (row 8 is now
  full). This is lens H's point 2: the rule must keep `tests/unit`, and it does (`UNIT`, on every scoped close).
- **The thin margins stay thin:** in rows 4, 5 and 27 the selection runs one or two of the catching suites and leaves
  out others (W1-29, W2-01, W2-53, W1-28, W1-32). A scoped close sees the red; the nightly full run sees the rest.
- **The three widest-reaching modules** (`src/gov/config/loader.py`, `src/gov/tasks/tickets.py`,
  `src/gov/store/loader.py`; rows 25 and 28 to 32) are in the shared core (DEC-892 c). For a change to any of them the
  selection is the full regression (`scope: full`, `why_full: SHARED_CORE`), so **all six faults are caught, with every
  catching suite run** (recall 1.0, against the declared map's 0.10 to 0.46). Lens H's report never ran them. The
  catch rests on two things. First, lens H's rest run of 2026-10-22 (`rest.log`: the six faults ran at 00:28 to 01:08
  and each failed tests of its catching suites). Second, the full regression holding every one of those suites. It
  does not rest on the selection's mapping: these six say nothing about how well a narrower mapping would catch them.
- **The two `src/gov/cli/main.py` faults** are full for the same reason: `src/gov/cli/main.py` and
  `src/gov/cli/errors.py` are in the shared core until a planted-fault measurement narrows them (DEC-903 item 2).

## 3. The 15-minute target

- **DEC-880 item 2's target**, a typical close under about 15 minutes, is reached by **W2-66 together with W2-68,
  W2-57's serial rework and worksteal** [DEC-889 item 11 e]:
  - W2-68: batching and same-code reuse, so the queue's rebuild, `gov check` and full regression run once per head;
  - W2-57: the serial-only rework;
  - worksteal, once W2-70 and W2-67 have removed the nested reruns (DEC-892 a).
  **W2-66 alone does not reach it.**
- **What W2-66 alone gives, measured here:** a typical scoped close's tests in **11.5 min**, against about 60 min
  (DEC-883) or 44.1 min for the full parallel run alone. Of the 11.5 min, 10.2 are the one W2-54 case that runs
  `gov check` again.
- **What it leaves:**
  - the rest of `gov close`: DEC-883's 72 min less its 60 min of tests, about 12 min of gates, context and records;
  - the queue's rebuild (about 6 min) and `gov check` (about 7 min), outside `gov close` (DEC-883);
  - by that arithmetic a scoped close in today's queue is still about 25 min of `gov close` and about 37 min with the
    rebuild and check. This is derived from DEC-883's figures, not measured here.

## 4. The fixture trial (the ladder, DEC-884 item 4)

### Method

- **The project:** built from nothing by W1-30's support (`w1_30_support.Project`: a fresh `git init`, this worktree's
  `src/`, the kernel's check declarations and schemas, a path map with `close_workers: 2`) under
  `/tmp/gov-os-lead-W2-66/eng-3/fixture/`, with W1-07's sandbox. `gov close` ran through W1-30's `run_close`, so it was
  this worktree's `gov` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src`), with W1-50's judgement of the commits.
- **Its test map**, small and stated:

      version: 1
      shared_core: ["src/core/**", "governance/project/test-map.yaml"]
      record_only: [".tickets/**.md", "docs/**.md", "docs/close/nightly/*.json"]
      record_reading: ["tests/acceptance/RR/test_records.py"]   # reads every .tickets/*.md
      every_close: []
      couplings: [{paths: ["src/beta/data.txt"], suites: ["tests/acceptance/FB/"], why: "text read"}]
      per_test_timeout: 120
      distribution: load

- **Its code and suites:**
  - `src/core/`, `src/alpha/` and `src/beta/`;
  - `tests/unit/`;
  - the record-reading suite `RR`;
  - two other tickets with their own acceptance suites: `PROJ-alfa` (FA, `src/alpha/**`) and `PROJ-beta` (FB,
    `src/beta/**`);
  - three closing tickets: `PROJ-xone` (FX1, `src/core/**`), `PROJ-xtwo` (FX2, `docs/notes/**`) and `PROJ-xthr`
    (FX3, `src/alpha/**`).
  Each is committed as a project commits it: the ticket file by the orchestrator, the acceptance test by the test
  designer, the change by the engineer (`Task:`, `Role: engineer`, `Implements: DEC-000`), the checkpoint by the
  orchestrator, and each close's record by the orchestrator after the close.
- **The first base:** a green night recorded on the fixture's head (`docs/close/nightly/2026-10-24.json`), so close 1
  has a base. After it the base is close 1's full record, since a scoped close names no base.
- **Two earlier tries were refused, rightly, for faults of the fixture, not of the code:**
  - the engineer's `Implements: CAP-01` resolved to no record (W2-07's in-close `gov check`, product traceability);
  - close 1's record was left uncommitted and swept into the next engineer commit, which W1-50's containment refused.
  The trial below is the third, built again from nothing.

### Results

The load was `35.02 57.73 56.64` at the trial's start and `29.79 55.86 56.05` at its end.

| Close | Planted change | Exit | Wall time of `gov close` | Evidence: scope | Ran | Left out, and why |
|---|---|---|---|---|---|---|
| 1, `PROJ-xone` | `src/core/base.py` (shared core) | 0 | 3.7 s | `full`; `why_full: [{reason: SHARED_CORE, paths: [src/core/base.py]}]`; base the green night's head | acceptance FX1: 1 passed (0.49 s); regression `tests` (`FULL`): 4 passed (unit, RR, FA, FB; 0.50 s) | none |
| 2, `PROJ-xtwo` | `docs/notes/note.md` (record only) | 0 | 2.9 s | `scoped`; `why_full: []`; base close 1's head | acceptance FX2 (`OWN`, `OVERLAP` `PROJ-xtwo`, `TEST_CHANGED`): 1 passed; regression: `tests/unit` (`UNIT`) and `tests/acceptance/RR/test_records.py` (`RECORD_READING`): 2 passed (0.48 s) | FA, FB, FX1: each `NOT_REACHED` |
| 3, `PROJ-xthr` | `src/alpha/mod.py` (one module) | 0 | 3.1 s | `scoped`; `why_full: []`; base close 1's head | acceptance FX3 (`OWN`, `OVERLAP`, `TEST_CHANGED`): 1 passed; regression: `tests/unit` (`UNIT`), FA (`OVERLAP` `PROJ-alfa`, `src/alpha/mod.py`), FX2 (`OVERLAP` `PROJ-xtwo` and `TEST_CHANGED`, close 2's work since the base), RR (`RECORD_READING`): 4 passed (0.46 s) | FB, FX1: each `NOT_REACHED` |

- Every evidence block also states the head, the tree, the changed paths, skip count 0, no failures, the two JUnit XML
  files (`01-acceptance-parallel.xml`, `02-regression-parallel.xml` under `.gov-runtime/close/<ticket>/<stamp>/`),
  `per_test_timeout: 120`, `distribution: load` and `tmp_path_retention_policy: failed`.
- **Close 3's FX2** is in its selection because the base is the last full close, so close 2's commits are inside close
  3's change (DEC-889 item 1: record-only commits between closes are inside the scope).
- The times are a toy project's. They show the evidence and the selection, not the cost of a close.

## Residuals

- **The typical close was measured once,** on one change, at a 1-minute load of 12 at its start, on a machine whose
  5- and 15-minute loads were still about 50. It is one sample, not a distribution.
- **The close's gates were not timed** (the commit gates, the pre-close collection of every suite, `gov check`, the
  context, the records). §3's arithmetic for them is from DEC-883's figures.
- **This worktree has no recorded base,** so a real close here would run full (`BASE_UNKNOWN`) until a full close
  record or a green night names an ancestor of its head. The selection was computed for the given path, as §1 says.
- **W2-54's context-reproducibility case does not read the close's check result** (`GOV_CLOSE_CHECK_RESULT`), so it
  runs `gov check` in every scoped close (611 s here). The estimate of 1.5 to 3 min without it is not measured.
- **The catch rate rests on lens H's ground truth** (`F_suites`, from the tests that execute each line). Lens H's
  controls found tests that react to a module's text in `config/loader.py` (5), `store/loader.py` (1),
  `cli/main.py` (1) and `doctor/command.py` (1). `analysis_b2.json` does not say whether any `F_suites` entry rests
  on such a test alone.
- **Recall stays low in places:** a scoped close catches the fault but may run only part of what fails (rows 4, 5,
  27). The nightly full run is the backstop (DEC-880 item 2 (c)).
- **The selection's time share per fault** was not computed here; lens H's figures for the declared map are a median
  9 % (22 faults) and 18.2 % (32 faults) of the test time. The typical close here selects 21 % of the cases, more than
  the declared map, because it adds W1-07's every-close files and the record-reading set.

## How to repeat it

The scripts were kept in the engineer's session scratch and are not part of the repository:

- `plan_for.py`: `select.plan` for given changed paths;
- `catch_rate.py`: the per-fault table from `analysis_b2.json`;
- `timed_scoped.py`: the close's own acceptance, regression and reds functions for that selection;
- `fixture_trial.py`: the three-close fixture on W1-30's support.

Each fits in about a page and follows the methods above.
