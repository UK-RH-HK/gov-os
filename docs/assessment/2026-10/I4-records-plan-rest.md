# Lens I, area 4: records, the plan, tickets and the remaining suites

Independent assessment of the Gov OS, October 2026: the test review against the specifications in force (DEC-889
item 16), area 4. Read-only auditor's report; it changes no test.

## 1. Header

### 1.1 Scope, date, what was read

- **Area.** Acceptance suites W1-06, W1-07, W1-08, W1-09, W1-11, W1-12, W1-13, W1-14, W1-27, W1-32, W1-33, W1-34,
  W1-35, W1-36, W1-37, W1-38, W1-39, W1-41, W1-44 and W2-02; builder tests `tests/unit/{records, tasks, decisions,
  readiness, bridge, doctor, status, cli, adopt, adapters, lock}`. 149 test files, 1,420 test functions, 2,418 cases.
- **Date.** 2026-10-22, 09:32 to about 20:15 (BST), in two sessions of the same auditor's brief. The first session (09:32 to
  about 15:00) read every test, wrote the drafts and made the alone runs and most of the suites' parallel runs. Its
  turn ended while runs were still pending, and in this launch form that ends the session. The second session (from
  16:48) made the outstanding parallel runs and every planted fault, decided the verdicts that rested on them, and
  wrote this report. "I" below is the auditor of either session; the run log says which session made each run.
- **Head assessed.** `w2/integrate` at `4166d8d9` (2026-10-22 00:16, DEC-891), cloned at 09:37. The head moved during
  the review, read only:
  - `8d625805` (DEC-892's record) and `49c24ac9` (the owner's commit of W1-38's third `load_sensitive` entry);
  - `0a75ac72` (W2-50's checkpoint);
  - `da3d77e1` (11:52, DEC-893 and DEC-894) and `bddd22f6` (12:05, W2-58's checkpoint);
  - `365f1307` (13:35, DEC-895) and `2b20aa27` (13:44, W2-62's checkpoint);
  - `c4f2b303` (14:16, DEC-896) and `89e760fb` (15:10, DEC-897);
  - `1a58eddd` (15:21, W2-62's checkpoint) and `d7daf01b` (16:44, W2-62 closed);
  - `466c63ae` (16:53) and `89f043e2` (17:14, W2-69's ticket), still the head when I last checked, at 20:06.

  None changes code, tests or the kernel: `git diff --stat 4166d8d9 89f043e2 -- src tests template` is empty. I read
  the register's DEC-892 to DEC-897 and the path map's entries from them. DEC-895 and DEC-896 overtake most of what
  findings 14 and 17 proposed, and those findings say so.
- **Branches read.**
  - `w2/integrate` (the clone; the head above);
  - `w2/W2-49` for Contract v4.2;
  - `record/w2` (the orchestration record since DEC-887: packages, the sweep of DEC-866);
  - `w2/W2-16` (W1-39's rewritten case, `adbeea77`);
  - the tree of W2-02's refused closes, `f46b1ff9` (10,286 files), as a worktree of my clone;
  - read only in the main tree: the close queue's, the nightly's and the tool trials' logs
    (`.gov-runtime/scratch/orchestrator/log/`, through the close queue of 15:11 to 16:44), and the queue and
    record-check scripts (`…/tools/`).
- **Contract read.** v4.2, from `w2/W2-49` (`w2/integrate` holds v4.1; v4.2's changes are CAP-43.b and d, CAP-44.f,
  h, k and l, CAP-45.a). Decisions read in force: superseded entries and "Changed by" parts set aside; five entries a
  later decision changed but did not mark are listed in finding 8.
- **Lens H's report** (`docs/assessment/2026-10/H-test-strategy.md`) and its logs (`/tmp/gov-os-assessment-H/logs/`,
  read only) gave the coverage map, the duplicate scan and the never-failing class.

### 1.2 What I ran

**Where and how.**
- Every run was in my own folder, `/tmp/gov-os-assessment-I4/`:
  - the clone `repo/` (a `git clone --no-hardlinks` of the repository);
  - two worktrees of the clone: `wt-fat/` (`f46b1ff9`) and `wt-plant/` (`4166d8d9`, for planted faults).
- Each run used the clone's own code (`PYTHONPATH=<tree>/src`) inside `scripts/inenv.sh`:
  - an environment built from scratch: HOME and TMPDIR in my folder, the git identity by environment variables;
  - a private `/tmp` (bubblewrap);
  - every place the brief forbids me to write bound read-only: the repository, the worktrees, the workbench,
    `~/gov-os-runs`, `~/.local`, `~/.claude`, `~/.cache`, `~/.config`, `~/.npm` and `~/.nvm`.
- The pinned `gov` was not used for any run.

**The gate.** Before each run that loads the machine, `scripts/gate.sh` (and, in the second session,
`scripts/gate2.sh`, the same gate with a time limit so that no call outlived ten minutes) waited until:
- the 1-minute load was under 20;
- MemAvailable was at least 6,710,886 kB;
- neither `CLOSE-RUNNING` nor `NIGHTLY-RUNNING` existed.

**The close queue held the machine four times, and no loading run of mine overlapped any of them:**
- 09:52 to 11:40:23, queue run 7: W2-50's close, refused (finding 14);
- 11:53:12 to 13:28:18, queue run 8: W2-58's close, refused on untracked work (finding 17);
- 13:35 to 13:56: W2-62's queue, stopped at its gate (b), the secrets check (DEC-897);
- 15:11 to 16:44:41: W2-62's close, passed. The regression ran 15,408 cases, 2 failed (the accepted reds' count) and
  31 skipped, with 263 serial cases passing and no area-4 red.

The other three lens-I reviews kept the 1-minute load between about 15 and 58 for much of the afternoon, so my runs
waited at the gate often. Every loading run started below 20, at loads from 0.9 to 19.9. The peaks during my own
suite runs reached 47.1.

**The runs, in order** (`notes/runlog.md`, `runs/phase1.log` and `runs/plant/results.jsonl` in my folder hold them
all). "When" is the start for the clone, the rebuilds, the collection and the planted-fault groups, and the end (the
time the log line was written) for the alone and suite runs:

| When | What | Where | Load at the start | Result |
|---|---|---|---|---|
| 09:37 | `git clone --no-hardlinks` of the repository | `repo/` | 1.0 | `4166d8d9` |
| 09:44 to about 09:59 | `python3 -m gov.cli.main rebuild --json` (the full rebuild, first attempt) | `repo/` | 12.9 | stopped by the shell's limit on a background call, unfinished; the close queue set its lock at 09:52 |
| 09:50 | `pytest tests --ignore=<every other suite> --collect-only` | `repo/` | 6.2 | 2,418 cases, 1,420 functions, 149 files |
| 11:42:07 | `rulesync --version` timed every 10 s, six times (the probe's own call) | my sandbox | 6.6 to 19.3 | 0.46 to 1.60 s |
| 11:42:12 | doctor's slow sections timed (`scripts/doctor_timing.py`) | `repo/` | 19.44 | tools 4.62 s, Claude Code 0.57 s, canaries 0.13 s |
| 11:45 to 11:57 | the full rebuild, second attempt | `repo/` | 19.9 | stopped by the first session 12 minutes in (store at 154 MB): its embedding calls kept the shared embedding server busy while the close queue waited for five quiet minutes; not restarted (1.3) |
| 11:44:58 | alone ×3: `test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | `repo/` | 17.7 to 19.4 | 3 of 3 passed (19.0, 6.7, 6.3 s) |
| 11:48:33 | alone ×3: `test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-blo` | `repo/` | 16.8 to 19.9 | 3 of 3 passed (5.8, 6.1, 1.8 s) |
| 11:48:41 | alone ×3: `test_w1_07_help.py::test_help_answers_in_under_300_ms` | `repo/` | 16.3 to 16.8 | 3 of 3 passed (2.5, 2.4, 2.5 s) |
| 11:48:42 | alone ×3: `test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace` | `repo/` | 16.0 to 16.3 | 3 of 3 passed (0.4, 0.4, 0.5 s) |
| 11:48:43 | alone ×3: `test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner` | `repo/` | 16.0 to 16.0 | 3 of 3 passed (0.3, 0.3, 0.5 s) |
| 11:49:21 | alone ×3: `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale` | `repo/` | 16.0 to 19.1 | 3 of 3 passed (14.3, 9.8, 13.3 s) |
| 13:57:08 | alone ×3: `test_w1_33_agent_definitions.py::test_the_research_definition_is_the_generated_one` | `repo/` | 3.9 to 3.9 | 3 of 3 skipped (0.8, 0.6, 4.1 s) |
| 14:17:14 | alone ×3 again, with my sandbox's HOME linked to the real rulesync and Node (1.3): the same W1-33 case | `repo/` | 16.2 to 16.3 | 3 of 3 passed (2.3, 1.9, 2.2 s) |
| 13:57:26 | alone ×3: `test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated` | `repo/` | 3.8 to 4.4 | 3 of 3 passed (3.5, 6.3, 8.0 s) |
| 13:57:45 | alone ×3: `test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-lev` | `repo/` | 7.0 to 9.6 | 3 of 3 passed (5.8, 4.9, 8.6 s) |
| 13:58:04 | alone ×3: `by-hand.md]` | `repo/` | 9.8 to 14.1 | 3 of 3 passed (6.3, 6.0, 6.1 s) |
| 13:59:38 | alone ×3: `test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder` | `repo/` | 15.1 to 19.6 | 3 of 3 passed (8.9, 7.1, 10.5 s) |
| 14:02:18 | alone ×3: `test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_anoth` | `repo/` | 17.5 to 18.3 | 3 of 3 passed (8.0, 9.4, 8.4 s) |
| 14:06:29 | alone ×3: `test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | `wt-fat/` | 19.3 to 19.6 | 3 of 3 passed (21.3, 12.9, 14.8 s) |
| 14:15:41 | alone ×3: `test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-blo` | `wt-fat/` | 18.9 to 19.9 | 3 of 3 passed (4.5, 6.4, 8.2 s) |
| 14:18:59 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `repo/` | 17.84 (peak 23.13) | exit 0: 223 passed in 84.48s (0:01:24) |
| 14:21:56 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `wt-fat/` | 19.43 (peak 23.82) | exit 0: 223 passed in 98.54s (0:01:38) |
| 14:28:50 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-09` | `repo/` | 19.82 (peak 19.82) | exit 0: 87 passed in 9.47s |
| 14:30:22 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-38` | `repo/` | 19.16 (peak 22.88) | exit 0: 201 passed in 37.24s |
| 14:38:04 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `repo/` | 12.99 (peak 25.60) | exit 0: 223 passed in 88.00s (0:01:27) |
| 14:42:32 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `wt-fat/` | 19.13 (peak 28.19) | exit 1: 1 failed, 218 passed, 4 errors in 118.66s (0:01:58) |
| 14:45:12 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-09` | `repo/` | 19.81 (peak 19.81) | exit 0: 87 passed in 11.32s |
| 14:47:38 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-38` | `repo/` | 18.45 (peak 47.10) | exit 0: 201 passed in 91.88s (0:01:31) |
| 14:55:41 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `repo/` | 16.76 (peak 37.87) | exit 0: 223 passed in 117.02s (0:01:57) |
| 15:00:49 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-07` | `wt-fat/` | 16.69 (peak 27.36) | exit 1: 222 passed, 1 error in 157.41s (0:02:37) |
| 17:00:05 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-09` | `repo/` | 19.00 (peak 19.00) | exit 0: 87 passed in 8.80s |
| 17:03:15 | the suite's parallel run (`-n auto --dist worksteal`): `tests/acceptance/W1-38` | `repo/` | 15.31 (peak 39.58) | exit 0: 201 passed in 76.37s (0:01:16) |
| 17:04 on | planted faults, plan `plans/plant-batch2.json` (`scripts/plant2.py`): 13 runs, 1,686 cases in all | `wt-plant/` | 15.7 to 19.7 | 8 of 13 runs with a red case; the worktree clean after each: yes (2.4) |
| 17:28 on | planted faults, plan `plans/plant-batch4.json` (`scripts/plant2.py`): 2 runs, 192 cases in all | `wt-plant/` | 15.9 to 19.8 | 2 of 2 runs with a red case; the worktree clean after each: yes (2.4) |
| 17:28 on | planted faults, plan `plans/plant-skills.json` (`scripts/plant2.py`): 6 runs, 6,163 cases in all | `wt-plant/` | 16.4 to 19.8 | 3 of 6 runs with a red case; the worktree clean after each: yes (2.4) |
| 17:37 on | planted faults, plan `plans/plant-w1-07-32.json` (`scripts/plant2.py`): 3 runs, 25 cases in all | `wt-plant/` | 15.1 to 15.1 | 2 of 3 runs with a red case; the worktree clean after each: yes (2.4) |
| 17:37 on | planted faults, plan `plans/plant-w1-27.json` (`scripts/plant2.py`): 11 runs, 2,490 cases in all | `wt-plant/` | 8.0 to 19.8 | 4 of 11 runs with a red case; the worktree clean after each: yes (2.4) |
| 18:25 on | planted faults, plan `plans/plant-w1-09.json` (`scripts/plant2.py`): 19 runs, 619 cases in all | `wt-plant/` | 13.8 to 19.9 | 18 of 19 runs with a red case; the worktree clean after each: yes (2.4) |
| 19:10 on | planted faults, plan `plans/plant-late.json` (`scripts/plant2.py`): 10 runs, 5,793 cases in all | `wt-plant/` | 3.0 to 19.0 | 4 of 10 runs with a red case; the worktree clean after each: yes (2.4) |
| 19:13 on | planted faults, plan `plans/plant-rerun.json` (`scripts/plant2.py`): 6 runs, 772 cases in all | `wt-plant/` | 9.2 to 17.6 | 4 of 6 runs with a red case; the worktree clean after each: yes (2.4) |
| 19:18 on | planted faults, plan `plans/plant-batch3.json` (`scripts/plant2.py`): 3 runs, 240 cases in all | `wt-plant/` | 8.3 to 16.9 | 2 of 3 runs with a red case; the worktree clean after each: yes (2.4) |
| 19:49 on | planted faults, plan `plans/plant-rerun2.json` (`scripts/plant2.py`): 1 run, 249 cases in all | `wt-plant/` | 0.9 to 0.9 | 1 of 1 runs with a red case; the worktree clean after each: yes (2.4) |

**A check of this report itself.** With this report placed, untracked, at the path the orchestrator will copy it to
(`docs/assessment/2026-10/`), in a scratch worktree of my clone, the record-reading files ran
(`scripts/report_check.sh`, finished at 20:04, load 0.3):
- W1-06's approvals, W1-07's envelope, W1-08's path map, W1-27's path compliance, W1-33's definitions and W2-02's
  green-here: 118 cases, all passed;
- W1-49's CLI case failed only because my sandbox's HOME has no `~/.local/bin/claude`, which the report cannot affect.

The report's path falls in exactly one namespace (`docs`) by DEC-225's matcher. The report also carries none of the
placeholder patterns the record checks refuse (DEC-893; `scripts/ph_scan.py` uses their pattern).

### 1.3 Limits

- **Refusals: twelve, none retried in its refused form, and none stopped a read the review needed.** The first
  session's nine are listed in `notes/runlog.md` in my folder.
  - Seven were the guard misreading a command:
    - five times "the command cannot be read" (DEC-409): on inline Python here-documents, and on three grep
      patterns with backticks (the third in the second session, at 20:08, a check of this report);
    - once a `>2` inside a quoted script, read as a write to a file named `2`;
    - once a redirection whose target held a variable ("unresolvable").

    Each piece of work was redone with my own script files or the Grep tool.
  - One was DEC-820 (a)'s secret-path refusal, on an existence test whose list named a key folder. The folder was
    left out. It is the only read refusal of either session.
  - One was the Monitor tool, "not known to the guard" (DEC-685). A Bash loop watched the locks instead.
  - Three were the session's own permission for `rm`, not the guard:
    - once on a draft of mine (the first session);
    - twice in the second session, on the per-run test folders described next.

    The files stay.
- **My runs exhausted the shared disk's inodes for a few minutes, and one result was lost and later re-run.** From
  18:31 to 19:04 I gave each planted-fault run its own pytest base folder. That skips pytest's clean-up of older
  folders, about 90 seconds per run. But it left every run's whole-tree copies on the disk: about 5.3 million files,
  46 GB, under `tmp/bt/` in my folder.
  - The shared disk's inodes reached 98 % use.
  - At about 19:04 the result file of one run (P27-10) could not be written (ENOSPC).
  - At 19:08 I went back to pytest's default handling, which keeps three folders. Free inodes were 4.5 to 5.7
    million from then on, and P27-10 was run again at 19:49.
  - My `rm` of `tmp/bt/` was refused twice (above), so the folder stays until the orchestrator removes mine.
  - It should be removed first: by my count at about 19:00 it is, after another review's folder (8.9 million), the
    largest single holder of inodes on the disk. At 20:11 my whole folder held 7.0 million files and folders (61 GB
    on disk), and the disk had 4.5 million inodes free (94 % used).
  - I know of no other session that failed on it, but I could not check.
- **Not done:**
  - the area-wide parallel runs (×3). The brief's "under load" is the suite's own parallel run, which was made three
    times for every suite whose flaky verdict rests on it (W1-07 on two trees, W1-09, W1-38);
  - the gc-race script. The race was reproduced inside W1-07's own parallel runs on the large tree instead (2.1,
    finding 5);
  - the clone's full rebuild. The first session started it twice and stopped it twice: the shell's limit at about
    09:59, then by its own choice at 11:57, to keep the shared embedding server free while the close queue waited
    for quiet. I did not restart it, because the load and the disk's inodes were high. No area case I ran needed the
    clone's store: every case passed or failed for its own measured reason without one. So `gov retrieve` answered
    none of this review's questions, and the code-graph tool was not asked any. Every question was answered by
    reading the register, the records and the code directly (Grep, Read, git).
- **Suites never run here:** W1-12, W1-14, W1-37, unit/bridge, unit/cli, unit/lock and unit/status. Their verdicts
  rest on reading and on the closes, which have run them green since 2026-10-20 (the rehearsal too).
  - W1-32, W1-33 and W1-41 were run in part (the files their verdicts needed).
  - Every other suite of the area was run whole at least once, most of them with one planted fault in place, whose
    other cases stayed green.
- **The first session's planted-fault runner did not pass the close's dev-tier setting.** So W1-11's five dev-tier
  cases (`test_w1_11_b_dev.py`) were skipped in P11-1's and P11-2's runs, and W1-10's in PR-1's. No verdict rests on
  those cases.
- **The coverage map is lens H's,** measured with its coverage shim across child processes (it attributed the
  child's lines for 97.9 % of the tests that start `gov` in a child, `H-test-strategy.md:45, 122`). I did not
  re-measure it, and it counts imports as execution.
- **The close keeps no failure text,** so a red case's cause in a past close is read from its code and from the
  close's own check output, and re-run here.
- **Skips:**
  - No area-4 case skips in the close's form: the rehearsal's 30 skips are W1-01's 28 retired-guardrail cases, one of
    W1-26 and one retrieval builder test (`scripts/skips.py` on its JUnit file), and W2-62's close skipped 31.
  - In my runs, the skips were W1-33's research case before my sandbox's HOME was linked (below), the dev-tier cases
    above, and the 182 cases of the stand-in run RS-any, which skips them by design (2.4).
- **My sandbox's HOME is my folder,** while the close runs with the real HOME. Five area suites look tools up under
  HOME: W1-06's and W1-12's Node, W1-38's node, W1-33's rulesync and W1-27's real-home doctor case.
  - From 14:16 that HOME holds two links to the real places, `.nvm` and `.local/bin/rulesync`, both bound read-only.
  - Before then, only W1-33's research case looked a tool up there. It skipped 3 of 3 without the link (2.1) and was
    rerun with it.
- **Nothing installed, no setting changed.** pytest-timeout, rerunfailures and randomly are not installed here, so my
  runs have no per-test limit. DEC-892 a defers worksteal for the close, the nightly and the leads; my under-load runs
  use it because the brief defines "under load" that way (the close itself runs `--dist load`).
- **Network:** one source, read 2026-10-22: https://git-scm.com/docs/git-gc (`gc.auto`, `gc.autoDetach`).

### 1.4 Terms

- **Gov OS:** this repository's governance system; `gov` is its command line.
- **Ticket, WBS id:** a unit of work. Its file is `.tickets/DAEO-<4 letters>.md`; its plan id is `W1-nn` (Wave 1)
  or `W2-nn` (Wave 2). Every ticket in this area is closed.
- **Acceptance suite:** the tests an independent test designer wrote for one ticket before it was built, in
  `tests/acceptance/<WBS id>/`. **Builder tests:** the engineer's own, in `tests/unit/`.
- **Function, case:** a *function* is one `def test_…`; a *case* is one run of it (a parametrised function has one
  case per parameter set). A verdict covers a function and all its cases, unless a row names one case.
- **`gov close`, the regression:** the command that closes a ticket. It runs the ticket's suite, then every other test
  in parallel (the **regression**), then the **serial-only** cases one at a time. A red test that is not on an owner
  list **refuses** the close: about 75 to 85 minutes lost, and a count towards escalation.
- **Serial-only list** (`tests/acceptance/serial-only.txt`): cases the close runs alone after the parallel run.
- **`load_sensitive`:** an owner-only list in the path map: a listed case that fails in a close is re-run alone in
  the same close and counts only if it fails again.
- **`accepted_reds`:** an owner-only list of known red tests that do not refuse a close.
- **Path map** (`governance/project/path-map.yaml`): every tracked path's namespace, and the close's settings and the
  two lists.
- **The rehearsal:** the orchestrator's first nightly full run in the close's form, on `dbd3cc53` (2026-10-21 17:49
  to 19:00); its case times are the costs in this report.
- **Record-reading test:** a test whose result depends on the repository's own records or settings (the register,
  the path map, the tool registry, ticket files, reports), so a record commit can turn it red.
- **Planted fault:** a deliberate one-line change to product code, a kernel file or a record, in a scratch copy, to
  see whether the tests that claim to catch it fail. **Weak:** a test that stays green with the fault it claims to
  catch.
- **Stand-in rulesync:** a small script of mine placed first on the PATH that waits 11 seconds and then runs the real
  `rulesync`; it shows by running what the checks' 10-second limit does (2.4, finding 2).
- **The fat tree:** the tree of W2-02's two refused closes, `f46b1ff9` (10,286 files, before the orchestration record
  left the tree); its code, tests and kernel are byte-identical to the head's.
- **Under load, alone:** as the brief defines them: inside the suite's parallel run in my clone (`-n auto --dist
  worksteal`, 20 workers here), and as one pytest process with the one case.
- **Whole-tree copy:** a fixture that copies every tracked and untracked file of the working tree into a temporary
  folder and commits it.
- **The close queue, the pre-close gates:** the orchestrator's script that runs closes one after another in a quiet
  window (`tools/close_queue.sh`), holding the lock `CLOSE-RUNNING`. Before each close it runs gates that stop the
  queue, uncounted, on the first failure (DEC-868). DEC-896 item 4 names them (a) to (h): the collection, `gov
  check`, a fresh checkpoint, the tree and the trailers as the close reads them, **gate (f)** (the record-reading test
  files), the network, and the work-without-a-task gate with the pinned code.
- **The ratchet:** the close's reading of the two owner lists (`src/gov/close/ratchet.py`): an entry counts only when
  its decision is an ACCEPTED owner entry whose text names the test with its file, and the commits that added it carry
  `Role: owner`.
- **A lead, a probe:** a lead is the orchestrator's session for one ticket; a FULL ticket's probe is an independent
  review record that its close checks (`PROBE_INVALID` when the code it judged has changed).
- **The orchestration record:** the orchestrator's and the leads' working files. In the tree from DEC-819; on the
  branch `record/w2` since DEC-887 (2026-10-21 17:42, `dbd3cc53`), when the tree went from 10,286 to 2,060 files.
- **W2-57, W2-66, W2-67:** open tickets: load out of the close and the serial list (W2-57); path-scoped selection of
  the regression (W2-66); test hygiene (W2-67).
- **Lens H:** the assessment of the test strategy (`docs/assessment/2026-10/H-test-strategy.md`), whose findings this
  review builds on.

### 1.5 How I reviewed

**The area.** 20 acceptance suites and 11 builder-test folders: 149 test files, 1,420 test functions, 2,418 cases at
`4166d8d9` (collected in the full run's form, `pytest tests --ignore=<every other suite>`, 1.7 s). In the rehearsal
(the nightly run in the close's form on `dbd3cc53`) the area's 2,415 parallel cases took 4,421.6 s of summed case
time: **33 % of the parallel run's case time** (13,417.4 s for 15,499 cases), about **10.5 minutes of a close's
31.8-minute parallel wall time** on a proportional estimate. Five suites hold 87 % of it: W1-41 1,777 s, W1-27 835 s,
W1-07 661 s, W1-38 324 s, W1-39 250 s.

**The order the brief sets, and what each step covered.**
1. **Failing or questionable tests first:**
   - the accepted reds: W1-42's two are not in this area (area 2 holds W1-42); none of area 4's tests is on the list;
   - every `load_sensitive` entry of the area: four (W1-07's `doctor` envelope case, DEC-886; W1-38's three rulesync
     cases, DEC-871 and DEC-892, the third committed by the owner on 2026-10-22 at 09:49, `49c24ac9`);
   - every serial-only entry of the area: three (W1-07's 300 ms help case; W1-09's two race cases);
   - every test of the area that was red in a Wave 2 close, the rehearsal, a recorded run or on the head (the closes'
     results, `log/close-queue-*/close-*.json`; the rehearsal's and the trials' JUnit files; lens H's three runs):
     W1-07's `[hard-block]` declaration case (W2-53's close of 2026-10-20 08:38, W2-02's of 2026-10-21 16:11, lens
     H's third run) and its `doctor` envelope case (W2-02's two closes of 2026-10-21); W1-08's tracked-path case
     (W2-02's first); W1-38's two DEC-871 cases (W2-53's close of 2026-10-20 12:30) and its DEC-892 case (W2-63's of
     2026-10-22 00:11, then its entry in W2-50's of 11:40); W1-06's approvals case and W1-27's old-path case (lens H's
     run and W2-58's lead, 2026-10-21); and from Wave 1's closes W1-33's research-definition case (W1-31b) and
     W1-38's settings hand-edit case (W1-30K). No area case was red in the rehearsal or the five tool trials;
   - the tests lens H found duplicated (its static scan): every pair that touches area 4. Lens H's "never failing"
     class is 99 % of the estate; I reviewed it as the rest of the area (below), with planted faults on the classes
     where a test can be green for the wrong reason.
2. **Then every suite of a closed ticket whose feature a later decision changed.** Every one of the 20 tickets is
   closed, and every suite has at least one later decision in its feature (the record types, the record's place, the
   read rules, the launcher, the owner's records, the context window, Contract v4.2's adoption items). So every one
   of the 1,420 functions was reviewed, not a sample: each got a first-pass line (what it asserts, what it rests on,
   what live state it reads, what it runs, any sign of an old rule, weakness, duplication or flakiness) from one of
   nine read-only helper sessions working from one brief (`/tmp/gov-os-assessment-I4/briefs/helper-common.md`), and
   I decided every flagged function myself, against the register and Contract v4.2, with the code open. One function
   had no first-pass line (W1-33's `test_a_definition_without_one_required_field_is_found`); a final check of every
   row against the collection found it, and I read and decided it myself.
3. **Then a sample, to check the first pass:** 54 functions the helpers marked "nothing found", drawn at random
   (seed 4, two per suite of 10 or more functions, one per smaller suite). I read each myself. I agreed with 53; the
   54th (W1-09's claims race) is decided by its planted faults below. A second sample, 30 functions drawn at random
   from the rest of the "valid" ones (seed 11), agreed in 30. Its closest call, W1-35's
   `test_discovery_sandbox_requirement` (the word "sandbox" anywhere), led me to decide every word check of W1-35 and
   W1-36 by one counted rule (`scripts/word_lines.py`, `verdicts/ov_wordchecks.py`): a word check is weak when the
   rule's own line can go while the checked word stays on another line of the skill, and valid, with its limit noted,
   when the word stands on the rule's line only. By that count 13 word checks the helpers had marked valid are weak,
   and 3 I had marked weak are valid. So the helpers' first pass was sound on behaviour checks and too kind to word
   checks.
4. **Then a check of my own coverage.** A script listed the flagged functions that had no row of mine and so stood
   at the default "valid" (`scripts/undecided.py`): 99. I read and decided each (`verdicts/ov_late.py`): 16 weak, 13
   duplicates, the rest valid with their limits stated. I did the same for the 27 text checks still at the default in
   the text-reading suites (`scripts/text_checks.py`): one weak, 26 valid (citations, or a statement read in place).
   After it, no flagged function and no text check stands at the default. A third sample, drawn after this pass,
   checked the rest: 24 functions (seed 21, at most two per suite) of the 1,037 still at the default and in neither
   earlier sample (`scripts/sample3.py`, `logs/sample-valid-3.txt`). All 24 agreed. Its nearest call, W1-38's
   `test_rule_the_held_out_file_does_not_give_is_red_on_the_settings`, requires the finding to name the settings
   file. So a probe timeout turns it red, not green: finding 2's red-on-timeout class.

**Planted faults.** A weak verdict needs evidence that the test stays green with the fault it claims to catch. 48
faults were planted in a scratch worktree of my clone (`wt-plant/`, at `4166d8d9`), each in the product code, a
kernel template or a record. For each, the tests that claim to catch it were run and the file restored
(`scripts/plant2.py`, a runner that restores the file even when it is stopped; results in `runs/plant/results.jsonl`).
The worktree was clean after every run.
- Each fault is one replacement, except PS-11: two edits in one file, removing both lines that state a rule the
  retrieval skill states twice.
- Three faults are controls that the tests should catch (P07-2, P27-10, PL202-2). Two runs had no edit (P27-0,
  P08-1c).
- Races need repeats. Two W1-09 faults ran five times alone and three times inside the parallel run of W1-09 and
  unit/tasks; the third ran three times.
- Two faults also ran against the guard's own suites (PG-1b, PG-2b), to see whether any test holds the rule.
- Two were run again: PS-4, whose first run named W1-35 and W1-36 together and stopped at collection (W1-36's conftest
  shadowed W1-35's), so it measured nothing; and P08-1, to print doctor's path-map section in full.
- Three runs change no file but the PATH: a stand-in `rulesync` that answers after 11 seconds, one second past the
  10-second limit of the portability check, W1-38's session fixture and W1-33's probe (RS-gen, RS-ver, RS-any).

That makes 74 runs in eleven plans (`plans/plant-*.json`), all in the second session, between 17:04 and 19:52;
section 2.4 gives one row per fault. The results:
- **The weak verdicts put to a fault: 49 rows.** 46 held:
  - 43 stayed green with the fault in place;
  - 3 went red only by the side effect their verdict names (P27-6: they pass today on the real CLI's drift).

  3 did not hold:
  - W1-27's `test_stale_path_section_counts_excluded_historical` (P27-5) and
    `test_tool_at_registered_location_wrong_version_fails` (P27-10) went red, so they are valid now, with their
    limits stated;
  - W1-33's `test_only_the_test_designer_may_write_the_acceptance_tests` went red through its [orchestrator] case
    (PG-2), so the function is valid and only its [engineer] and [product-spec] cases are weak.
- **The 7 valid verdicts put to a fault all went red**, and so did the 3 controls.
- **Of the weak cases whose fault no case of their own suite catches, 8 rules are held elsewhere:**
  - W1-02, W1-45 and the guard's unit tests (PG-1, PG-2);
  - another W1-41 case (PU-c);
  - builder tests (P27-2, P38-1, P09-3, P13-b);
  - W1-30 (P02-2).
- **And 7 behaviours no test I ran catches at all:**
  - doctor's moved-path references (P27-1), unclassified paths (P27-4), path matcher (P27-8) and isolation (P27-9);
  - rebuild's digest (P27-7);
  - A8's retirement guard (P41-c);
  - the decision checker's final-block rule (P11-1).

  Findings 1 and 4 weigh them.

**Flaky verdicts** rest on runs:
- each case alone three times, and inside its suite's parallel run (`-n auto --dist worksteal`) three times, with the
  load recorded at each run;
- for W1-07, also on the fat tree (`f46b1ff9`, 10,286 files), whose code, tests and kernel are byte-identical to the
  head's (`git diff --stat f46b1ff9 4166d8d9 -- src/ tests/ template/` is empty);
- for W1-38 and W1-33, also the three stand-in runs, which show by running what the probe's limit does.

The other three lens-I reviews ran on the machine at the same time, so "alone" means one pytest process with one
case, not a quiet machine. The 1-minute load at my runs' starts ranged from 0.9 to 19.9, and every run started only
through the gate (load under 20, no lock).

## 2. Verdicts

One verdict per test function (or per case, where a row names one case):
- **valid:** valid and needed;
- **outdated:** the expected behaviour changed; the decision is named;
- **obsolete:** the feature was removed or replaced;
- **duplicate:** the test it repeats is named;
- **weak:** it cannot fail for the fault it claims to catch, shown by a planted fault where one was run;
- **flaky:** red and green on the same code, with the cause found by running it, alone and under load;
- **not reproducible:** red in a recorded run, green in every run here, cause not found.

The sections:
- 2.1: the questionable tests the brief puts first;
- 2.2: every other test whose verdict is not "valid";
- 2.3: every valid one;
- 2.4: the planted faults, one row each, which the weak and valid verdicts cite.

No test is changed by this review. Each proposed revision goes to an independent test designer, in the carrier named,
with the `Rewrite-Reason:` given. A "small test-revision ticket" closes on another ticket's acceptance folder only
once W2-07's close by ticket class lands (DEC-892 item 1; DEC-896 item 3 brings W2-07 into the first re-pin). Until
then a revision rides most easily in an open ticket that already holds the files:
- W2-11 (the kernel's skills, roles and briefs);
- W2-23 (the path map's checks);
- W2-34 (the tasks and the bridge);
- W2-57 (the probe);
- W2-64 (the record types);
- W2-67 (test hygiene).

### 2.1 The questionable tests

The brief's first step covers four groups:
- the accepted reds (none in this area);
- every `load_sensitive` and serial-only entry of the area;
- every area test that was red in a Wave 2 close, the rehearsal, a recorded run or on the head;
- lens H's duplicate pairs (below the tables).

Table A gives the runs, table B the verdicts. In my own runs, too, some area cases went red: five W1-07 cases (six times) in
W1-07's parallel runs on the fat tree, on the copy race of finding 5. They carry flaky verdicts in 2.2 (and the envelope
duplicate's `[check]` case a note), and none was red on the head.

**Table 2.1 A, the runs.** Each case alone in one pytest process (`head` = the clone at `4166d8d9`; `linked` = the same, with my sandbox's HOME linked to the real tools, as the close finds them (1.3); `fat` = the tree of W2-02's refused closes, `f46b1ff9`), and inside its suite's parallel run in my clone (`-n auto --dist worksteal`, 20 workers; the run labels name the tree and the run). Loads are the 1-minute load average; the machine was shared with three other reviews, so 'alone' means one pytest process with one case, not a quiet machine.

| Test | Alone ×3 (outcome; case seconds; load before) | In-suite runs (outcome; seconds; load at start, peak) |
|---|---|---|
| `test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | head: 3/3 passed; 5.9 to 14.6 s; load 17.7 to 19.4; fat: 3/3 passed; 11.4 to 17.3 s; load 19.3 to 19.6 | 6/6 passed (W1-07-fat-1, W1-07-fat-2, W1-07-fat-3, W1-07-head-1, W1-07-head-2, W1-07-head-3); 5.7 to 12.8 s; load 13.0 to 19.4, peak 23.1 to 37.9 |
| `test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-block]` | head: 3/3 passed; 1.3 to 5.4 s; load 16.8 to 19.9; fat: 3/3 passed; 3.9 to 5.9 s; load 18.9 to 19.9 | 6/6 passed (W1-07-fat-1, W1-07-fat-2, W1-07-fat-3, W1-07-head-1, W1-07-head-2, W1-07-head-3); 0.8 to 7.2 s; load 13.0 to 19.4, peak 23.1 to 37.9 |
| `test_w1_07_help.py::test_help_answers_in_under_300_ms` | head: 3/3 passed; 2.0 to 2.1 s; load 16.3 to 16.8 | 6/6 passed (W1-07-fat-1, W1-07-fat-2, W1-07-fat-3, W1-07-head-1, W1-07-head-2, W1-07-head-3); 1.5 to 7.4 s; load 13.0 to 19.4, peak 23.1 to 37.9 |
| `test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace` | head: 3/3 passed; 0.09 to 0.10 s; load 16.0 to 16.3 | — (not planned: no flaky verdict rests on it) |
| `test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner` | head: 3/3 passed; 0.04 to 0.05 s; load 16.0 | — (not planned: no flaky verdict rests on it) |
| `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale` | head: 3/3 passed; 9.2 to 12.4 s; load 16.0 to 19.1 | — (not planned: no flaky verdict rests on it) |
| `test_w1_33_agent_definitions.py::test_the_research_definition_is_the_generated_one` | head: 3/3 skipped; 0.00 s; load 3.9; linked: 3/3 passed; 1.1 to 1.4 s; load 16.2 to 16.3 | — (not planned: no flaky verdict rests on it) |
| `test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` | head: 3/3 passed; 3.3 to 7.3 s; load 3.8 to 4.4 | 3/3 passed (W1-38-head-1, W1-38-head-2, W1-38-head-3); 6.1 to 10.3 s; load 15.3 to 19.2, peak 22.9 to 47.1 |
| `test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` | head: 3/3 passed; 4.4 to 5.2 s; load 7.0 to 9.6 | 3/3 passed (W1-38-head-1, W1-38-head-2, W1-38-head-3); 4.4 to 9.2 s; load 15.3 to 19.2, peak 22.9 to 47.1 |
| `test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]` | head: 3/3 passed; 5.3 to 5.6 s; load 9.8 to 14.1 | 3/3 passed (W1-38-head-1, W1-38-head-2, W1-38-head-3); 1.7 to 8.7 s; load 15.3 to 19.2, peak 22.9 to 47.1 |
| `test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder` | head: 3/3 passed; 6.5 to 7.5 s; load 15.1 to 19.6 | 3/3 passed (W1-09-head-1, W1-09-head-2, W1-09-head-3); 6.5 to 7.0 s; load 19.0 to 19.8, peak 19.0 to 19.8 |
| `test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim` | head: 3/3 passed; 7.5 to 8.9 s; load 17.5 to 18.3 | 3/3 passed (W1-09-head-1, W1-09-head-2, W1-09-head-3); 6.5 to 7.0 s; load 19.0 to 19.8, peak 19.0 to 19.8 |

**Table 2.1 B, the verdicts.**

| Test | Suite (ticket) | On which list | Recorded reds | Verdict | Cause and evidence | Rests on | Proposed change; carrier |
|---|---|---|---|---|---|---|---|
| `test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | W1-07 (DAEO-drvn) | `load_sensitive` (DEC-886) | W2-02's two closes, 2026-10-21 14:01 and 16:11 (failed) | **not reproducible** | red (failed) in W2-02's two closes of 2026-10-21 (14:01, 16:11) on the 10,286-file tree; load_sensitive since DEC-886. Green in all 12 runs here: alone 3 of 3 at the head (14.6, 6.4, 5.9 s, load 17.7 to 19.4) and 3 of 3 on that tree (17.3, 11.5, 14.1 s, load 19.3 to 19.6); inside the suite's parallel run 3 of 3 at the head (5.7 to 12.8 s, load at start 13.0 to 17.8, peak 37.9) and 3 of 3 on that tree (6.8 to 7.8 s, peak 28.2), the last two of those runs while the copy race hit other cases. Doctor's slow sections took 4.6 s and 0.6 s at load 19 (scripts/doctor_timing.py) against the case's 180 s limit. The close keeps no failure text, so the cause is not found; the code narrows it to an exception gov doctor does not catch (main.py:224 catches GovError only; finding 5) | W1-07 KPI S1, F2; API-0002; DEC-186, DEC-554 point 2, DEC-886 | keep on load_sensitive until W2-57; the close keeps JUnit XML with failure text (DEC-889 item 12); W2-57 |
| `test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-block]` | W1-07 (DAEO-drvn) | none | W2-53's close, 2026-10-20 08:38, and W2-02's second, 2026-10-21 16:11 (error, at setup); lens H's third run, 2026-10-21 12:45 | **flaky** | errored at setup in W2-53's close (2026-10-20 08:38, about 8,300 files) and W2-02's second (2026-10-21 16:11, 10,286 files), beside W1-25's copy case; lens H's third run shows this very case's error: shutil.Error on .git/objects/03 of the session copy. Green alone here 3 of 3 at the head and 3 of 3 on that tree, and inside the suite's parallel run 3 of 3 on each; but in the same parallel runs on that tree the same error struck 6 times on 5 other W1-07 cases (14:40: 5; 14:57: 1), and never on the head (finding 5). Cause: the `project` fixture copies the session copy while git's background gc, started by that copy's first commit above gc.auto's 6,700 loose objects, packs its objects away (w1_07_support.py:144-152); dormant at 2,071 files | W1-07 KPI S4; DEC-186 | a copy that does not race git's background gc (gc.auto=0 in the session copy, or the working files only); W2-67 (per-test copies); Rewrite-Reason: the copy races git's background gc |
| `test_w1_07_help.py::test_help_answers_in_under_300_ms` | W1-07 (DAEO-drvn) | serial-only (latency) | none | **valid** | serial-only (latency: the median of nine `gov --help` runs under 300 ms, help.py:17-28); green alone 3 of 3 at the head (2.0 to 2.2 s for the case, load 16.3 to 16.8), inside the suite's parallel run 6 of 6 (head and the 10,286-file tree, 1.5 to 7.4 s, peak load 37.9), and in W2-62's close (serial, 16:44); a latency case stays alone (DEC-889 item 5) | W1-07 KPI S3b; DEC-372, DEC-554 point 2 | keep serial-only |
| `test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace` | W1-08 (DAEO-uudf) | gate (f) | W2-02's close, 2026-10-21 14:01 (a true catch, DEC-885) | **valid** | red in W2-02's close of 2026-10-21 14:01 for a real fault: two record copies in no namespace (DEC-885, the sync's slip, fixed in the sync); alone at the head 3 of 3 passed, 0.11 to 0.14 s, load 16.0 to 16.3 (runs/alone). It is the only check of DEC-225's rule that works on this repository: with the planted P08-1 (tests/unit/ in no namespace, 127 paths) it went red while `python3 -m gov.check.pathmap` exited 0 with no finding and doctor's path_map section said pass, unclassified_count 0 (runs/plant/P08-1b-*.xml; finding 3); record-reading, in gate (f) | W1-08 KPI S2b, CAP-06.a; DEC-225 | keep; in the record-reading set (it is) |
| `test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner` | W1-06 (DAEO-ipqy) | gate (f) | lens H's run and W2-58's lead, 2026-10-21 (a true catch, DEC-882) | **valid** | red on 2026-10-21 from b772b2fe (08:30) to 9d8c1887 (14:00) for a real inconsistency: DEC-843, still the approval of two installed tools, was marked SUPERSEDED; DEC-882 restored it with a 'Changed by' note; alone at the head 3 of 3 passed, 0.05 to 0.07 s, load 16.0; with the planted P06 (DEC-822, the gov pin's approval, marked SUPERSEDED) it went red (runs/plant/P06-mark-dec-822-superseded.xml); record-reading, in gate (f) | W1-06 KPI F1, CAP-25.a; DEC-083, DEC-197 | keep |
| `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale` | W1-27 (DAEO-xw3k) | gate (f) | lens H's run and W2-58's lead, 2026-10-21 (a lead log named its fixture file) | **valid** | red on 2026-10-21 (lens H's run; W2-58's lead) because a committed lead log named the fixture's file: the case copies the whole tree and doctor greps every file for moved paths; green once that file left the tree (DEC-887); alone at the head 3 of 3 passed, 9.2 to 12.5 s, load 16.0 to 22.8; it holds a real rule (DEC-456) but any tracked text naming its fixture file turns it red, so this report does not name it | W1-27 KPI S3; DEC-456 point 3 | a project of its own instead of the whole-tree copy (W2-67's per-test copies); W2-67; Rewrite-Reason: the result depends on every tracked file's text |
| `test_w1_33_agent_definitions.py::test_the_research_definition_is_the_generated_one` | W1-33 (DAEO-xog0) | record checks (DEC-889 item 2) | W1-31b's close, 2026-10-13 (DEC-665, rewritten 9dd9c052) | **weak** | red in W1-31b's close (2026-10-13) under its old name, from DEC-665's apply block, and rewritten the same day (9dd9c052). Since then any answer short of the binary's version, a timeout included, is a silent skip: its probe returns None after 10 s (w1_33_support.py:166-176) and the case skips as 'rulesync is not installed' (test:100-102). Measured: alone at the head with my sandbox's HOME lacking the binary, 3 of 3 skipped, load 3.9; with HOME's link to the real binary, as the close finds it, 3 of 3 passed, 1.1 to 1.4 s, load 16.2 to 16.3; with a stand-in rulesync whose `--version` answers after 11 s, skipped, beside 181 W1-38 cases, and the run exited 0 (runs/plant/RS-any-slow-every-version.xml). The close counts a skip without refusing it (DEC-500), so it does not run where W1-38's cases fail | W1-33 KPI S5; DEC-163, DEC-665 | a probe timeout fails or counts as load-sensitive, never a skip; W2-57 (its rulesync-probe item, DEC-892); Rewrite-Reason: a timeout is no absent tool |
| `test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` | W1-38 (DAEO-3ef2) | `load_sensitive` (DEC-871) | W2-53's close, 2026-10-20 12:30 | **flaky** | red in W2-53's close (2026-10-20 12:30), whose check output names the cause: RULESYNC_FAILED, 'rulesync --version: no answer within 10 seconds; the generated files were not compared' (close-queue-20261020-1212/close-DAEO-7rr2.json); load_sensitive since DEC-871. Green here alone 3 of 3 (3.3 to 7.4 s, load 3.8 to 4.4) and inside the suite's parallel run 3 of 3 (6.1 to 10.3 s, peak load 47.1); the probe's own `rulesync --version`, timed every 10 s beside my runs, took 0.33 to 2.81 s in 42 samples at loads 6.6 to 47.1 (runs/rulesync-*.txt), never near its 10 s limit. The cause, shown by running it: with a stand-in rulesync that answers the portability check after 11 s, the case went red with RULESYNC_FAILED 'no answer within 10 seconds', whether the slow call was the check's `--version` (30 W1-38 cases red, 19 functions) or its `generate` (28 cases, 17 functions) (runs/plant/RS-ver-*.xml, RS-gen-*.xml; finding 2) | W1-38 KPI S3, CAP-38.b; DEC-186, DEC-871 | keep on load_sensitive until W2-57's probe fix (P-I4-5); W2-57 |
| `test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` | W1-38 (DAEO-3ef2) | `load_sensitive` (DEC-871) | W2-53's close, 2026-10-20 12:30; W1-30K in Wave 1 (DEC-646) | **flaky** | red in W2-53's close (2026-10-20 12:30), whose output names 'rulesync generate: no answer within 10 seconds' (RULESYNC_FAILED), and once under load in Wave 1 (W1-30K, DEC-646, judged load by DEC-647); load_sensitive since DEC-871. Green here alone 3 of 3 (4.4 to 5.2 s, load 7.0 to 9.6) and inside the suite's parallel run 3 of 3 (4.4 to 9.2 s); the probe's own `rulesync --version`, timed every 10 s beside my runs, took 0.33 to 2.81 s in 42 samples at loads 6.6 to 47.1 (runs/rulesync-*.txt), never near its 10 s limit. The cause, shown by running it: with a stand-in rulesync that answers the portability check after 11 s, the case went red with RULESYNC_FAILED 'no answer within 10 seconds', whether the slow call was the check's `--version` (30 W1-38 cases red, 19 functions) or its `generate` (28 cases, 17 functions) (runs/plant/RS-ver-*.xml, RS-gen-*.xml; finding 2); the function's four other cases went red with it | W1-38 KPI F2; DEC-471, DEC-871 | keep on load_sensitive until W2-57's probe fix (P-I4-5); W2-57 |
| `test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]` | W1-38 (DAEO-3ef2) | `load_sensitive` (DEC-892, counted from DEC-894) | W2-63's close, 2026-10-22 00:11 | **flaky** | red in W2-63's close (2026-10-22 00:11), whose findings carry the failure's RULESYNC_FAILED (close-queue-20261021-2241/close-DAEO-pl6k.json); load_sensitive since DEC-892, its entry counted only from DEC-894 (11:52, finding 14). Green here alone 3 of 3 (5.4 to 5.7 s, load 9.8 to 14.1) and inside the suite's parallel run 3 of 3 (1.7 to 8.7 s); the probe's own `rulesync --version`, timed every 10 s beside my runs, took 0.33 to 2.81 s in 42 samples at loads 6.6 to 47.1 (runs/rulesync-*.txt), never near its 10 s limit. The cause, shown by running it: with a stand-in rulesync that answers the portability check after 11 s, the case went red with RULESYNC_FAILED 'no answer within 10 seconds', whether the slow call was the check's `--version` (30 W1-38 cases red, 19 functions) or its `generate` (28 cases, 17 functions) (runs/plant/RS-ver-*.xml, RS-gen-*.xml; finding 2); the function's other case (settings.local.json) went red with it | DEC-050, DEC-063, DEC-471; DEC-892 | keep on load_sensitive until W2-57's probe fix (P-I4-5); W2-57 |
| `test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder` | W1-09 (DAEO-topz) | serial-only (race) | none | **valid** | eight processes race one claim, four rounds; exactly one holds it and the seven losers are told who (test_w1_09_claims.py:97-112). Under the planted P09-1 (a check-then-create lock, claims.py's O_EXCL dropped while the lock is absent) it was red in 4 of 5 runs alone and in 3 of 3 runs inside the parallel run of W1-09 and unit/tasks (runs/plant/P09-1-*.xml): it catches a broken claim lock. Under the planted P09-3 (no wait for the winner's line) it stayed green 3 of 3: the losers' 'told who' half is held instead by tests/unit/tasks/test_tasks.py::test_a_holder_still_being_written_is_waited_for (red 3 of 3). Unplanted it passed 3 of 3 alone and 3 of 3 inside the suite's parallel run, and in W2-62's close (serial, 16:44) | W1-09 KPI F1, CAP-23.a; DEC-292 | keep; W2-57 may move it to the parallel run (it caught P09-1 there 3 of 3) |
| `test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim` | W1-09 (DAEO-topz) | serial-only (race) | none | **valid** | releases and claims raced from separate processes; no release removes another holder's claim (test_w1_09_review.py:48; README:127-136). Under the planted P09-2 (the release reads the holder and removes the lock without the folder lock) it was red in 5 of 5 runs alone and 3 of 3 inside the parallel run (runs/plant/P09-2-*.xml). Unplanted it passed 3 of 3 alone and 3 of 3 inside the suite's parallel run | W1-09 KPI F1, CAP-23.a; DEC-292 | keep; W2-57 may move it to the parallel run (it caught P09-2 there 3 of 3) |

**Lens H's duplicate pairs touching area 4** (its static scan, `H-test-strategy.md:281-284`, `scripts/dupes.py`):
- **Class 1 (identical bodies).** W1-06's `test_ccusage_is_recorded_in_the_registry` and W1-48's
  `test_claude_code_is_recorded_in_the_registry` bind different registry entries, so they are no pair. The W1-06 one
  is a duplicate inside W1-06 (2.2).
- **Class 2 (the same name in two files): 13 names touch the area.**
  - Two are duplicates: W1-27's `test_namespaces_of_the_wrong_type_names_the_key` of W1-07's namesake; W1-06's
    `test_the_recorded_install_command_…`, held inside W1-06.
  - The other 11 hold the same rule with another input, command, interface or level (a builder test beside an
    acceptance case), and are valid.
- **Class 3 (the same shape with other strings): 21 groups**, different checks by construction, with these
  exceptions:
  - one pair is a duplicate: W1-35's `test_body_over_2500_tokens_would_fail` repeats `test_body_within_2500_tokens`'s
    assertion on the same text;
  - W1-06's `test_superpowers_is_recorded_at_v6_4_2` is a duplicate of a third test, not of its partner;
  - many members are weak word checks (W1-27's `mentions_*` family, W1-35's skill-text family).

All are in 2.2.

### 2.2 Every test whose verdict is not "valid and needed"

Ordered by suite. A row with `[...]` is one case of a parametrised function; the function's other cases keep the function's own verdict. Cost: seconds of case time in the rehearsal's parallel run.


**W1-06**: W1-06 (DAEO-ipqy)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_06_install_approvals.py::test_the_ccusage_install_command_is_the_approved_one` | weak | does not require the PATH prefix DEC-202 added to DEC-192's command (register line 1865; README.md:82-84 records the gap), so an install command without it, the fault DEC-202 is about, passes; planted fault P06-c; measured: under P06-c the case was green (runs/plant/P06-c-ccusage-path-prefix-gone.xml) | DEC-192 as corrected by DEC-202 | revise: require the PATH prefix | a small test-revision ticket for W1-06; Rewrite-Reason: DEC-202 | 0.0 |
| `test_w1_06_install_approvals.py::test_the_ccusage_uninstall_command_uses_the_same_npm` | weak | the same DEC-202 gap for the uninstall command | DEC-192, DEC-202 | revise as above | as above | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_carries_a_sha256_digest` | duplicate | the same regex as test_w1_06_registry.py::test_every_sha256_is_a_sha256_digest, over every entry (registry.py:57-62) | CAP-25.a; DEC-196 | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_is_installed_on_this_machine` | duplicate | test_the_installed_ccusage_is_the_pinned_version asserts the same path first (ccusage.py:113-115); local_only | KPI S1; DEC-192 (reading 10) | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_is_pinned_to_one_exact_version` | duplicate | implied by test_w1_06_install_approvals.py::test_an_install_of_this_ticket_is_recorded_at_the_approved_version[ccusage], which requires 20.0.26 exactly (norm_version strips only a leading v, w1_06_support.py:75-78) | KPI S1; DEC-083 (reading 9) | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_is_recorded_in_the_registry` | duplicate | asserts only that the registry holds one ccusage entry (ccusage.py:38-39), the lookup every other ccusage case opens with (_entry, :34-35); lens H's identical-body pair with W1-48's test_claude_code_is_recorded_in_the_registry is no duplicate: that one binds the Claude Code entry | CAP-25.a, DEC-192 | keep (cost nil; its failure message is the clearest) | — | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_was_approved_by_an_owner_decision_of_the_register` | duplicate | the three approvals cases of test_w1_06_approvals.py, restricted to ccusage (ccusage.py:72-80); record-reading like them (ccusage's approval is DEC-192) | KPI S1, F1; DEC-083 | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_ccusage_was_not_installed_before_its_approval` | duplicate | identical to test_w1_06_install_approvals.py::test_an_install_of_this_ticket_is_not_dated_before_its_approval[ccusage] (ccusage.py:83-93 vs install_approvals.py:94-103) | DEC-083 | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_the_recorded_install_command_installs_the_pinned_version` | duplicate | the install command names ccusage and the registry's version (ccusage.py:50-56); held together by test_the_ccusage_install_command_is_the_approved_one (ccusage@20.0.26 exactly, install_approvals.py:106-117) and test_an_install_of_this_ticket_is_recorded_at_the_approved_version[ccusage]; lens H's same-name pair with W1-48 checks the Claude Code entry | DEC-192 | keep (cost nil) | — | 0.0 |
| `test_w1_06_ccusage.py::test_the_recorded_uninstall_command_removes_ccusage` | duplicate | 'ccusage' in the uninstall command, which test_the_ccusage_uninstall_command_uses_the_same_npm asserts too, case-sensitively (install_approvals.py:126-128) | KPI F2; DEC-083 (reading 11) | keep (cost nil) | — | 0.0 |
| `test_w1_06_digests.py::test_gitleaks_is_recorded_with_a_sha256_digest` | duplicate | test_every_sha256_is_a_sha256_digest holds the form for every entry; the value is held by the [gitleaks] binary case | KPI S2; DEC-195 | keep (cost nil) | — | 0.0 |
| `test_w1_06_pins.py::test_superpowers_is_recorded_at_v6_4_2` | duplicate | identical to test_an_install_of_this_ticket_is_recorded_at_the_approved_version[superpowers] (pins.py:61-64) | DEC-193 | keep (cost nil) | — | 0.0 |
| `test_w1_06_pins.py::test_superpowers_is_recorded_with_a_sha256_digest` | duplicate | test_every_sha256_is_a_sha256_digest holds the form for every entry; the vendor_digest cases hold the value | KPI S2; DEC-196 | keep (cost nil) | — | 0.0 |
| `test_w1_06_registry.py::test_every_entry_has_an_uninstall_command` | duplicate | the same predicate is inside test_every_entry_states_all_seven_facts (REQUIRED holds 'uninstall', w1_06_support.py:26; registry.py:40-48) | KPI F2 | keep (cost nil) | — | 0.0 |
| `test_w1_06_registry.py::test_the_registry_is_committed` | duplicate | the same check as tests/acceptance/W1-48/test_w1_48_registry.py::test_the_registry_as_read_is_the_committed_one (w1_48_support.py:146-152) | CAP-25.a; DEC-127 | keep (cost nil) | — | 0.1 |
| `test_w1_06_registry.py::test_the_registry_records_at_least_one_tool` | duplicate | the assertion every registry case opens with (approvals.py:26, 33, 41; registry.py:99) | CAP-25.a | keep (cost nil; its failure message is the clearest) | — | 0.0 |

**W1-07**: W1-07 (DAEO-drvn)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_07_config_details.py::test_a_file_level_error_carries_file_and_key_in_details[not-yaml]` | flaky | errored at setup in my parallel run of 14:40 on f46b1ff9; the shared `project` fixture copies the session's whole-tree copy (w1_07_support.py:144-152) while git's background gc, started by that copy's first commit above gc.auto's 6,700 loose objects, packs its loose objects away; in my parallel runs of W1-07 on the tree of W2-02's refused closes (f46b1ff9, 10,286 files, code, tests and kernel identical to the head's) it struck 6 times on 5 cases in 3 runs (14:40: 4 errors at setup and 1 failure; 14:57: 1 error; 14:20: none), each `shutil.Error: … .git/objects/NN: No such file or directory` in the session copy, the signature of the closes' reds and of lens H's third run; on the head (2,071 files) 0 in 3 runs: dormant until the tree passes about 6,700 objects again (finding 5) | S3a; DEC-189 | a copy that does not race git's background gc (gc.auto=0 in the session copy, or a copy of the working files without .git): one fix in the fixture for every W1-07 case | W2-67 (its per-test copies task); Rewrite-Reason: the copy races git's background gc | 2.2 |
| `test_w1_07_config_details.py::test_namespaces_of_the_wrong_type_names_the_key[a-string-status]` | flaky | errored at setup in my parallel run of 14:40 on f46b1ff9; the shared `project` fixture copies the session's whole-tree copy (w1_07_support.py:144-152) while git's background gc, started by that copy's first commit above gc.auto's 6,700 loose objects, packs its loose objects away; in my parallel runs of W1-07 on the tree of W2-02's refused closes (f46b1ff9, 10,286 files, code, tests and kernel identical to the head's) it struck 6 times on 5 cases in 3 runs (14:40: 4 errors at setup and 1 failure; 14:57: 1 error; 14:20: none), each `shutil.Error: … .git/objects/NN: No such file or directory` in the session copy, the signature of the closes' reds and of lens H's third run; on the head (2,071 files) 0 in 3 runs: dormant until the tree passes about 6,700 objects again (finding 5) | S3a; DEC-189, DEC-228 | a copy that does not race git's background gc (gc.auto=0 in the session copy, or a copy of the working files without .git): one fix in the fixture for every W1-07 case | W2-67 (its per-test copies task); Rewrite-Reason: the copy races git's background gc | 2.1 |
| `test_w1_07_help.py::test_help_prints_usage_and_ends_with_exit_code_0` | flaky | errored at setup in my parallel run of 14:40 on f46b1ff9; otherwise it holds the exit code and a non-empty usage (help.py:12-14); the shared `project` fixture copies the session's whole-tree copy (w1_07_support.py:144-152) while git's background gc, started by that copy's first commit above gc.auto's 6,700 loose objects, packs its loose objects away; in my parallel runs of W1-07 on the tree of W2-02's refused closes (f46b1ff9, 10,286 files, code, tests and kernel identical to the head's) it struck 6 times on 5 cases in 3 runs (14:40: 4 errors at setup and 1 failure; 14:57: 1 error; 14:20: none), each `shutil.Error: … .git/objects/NN: No such file or directory` in the session copy, the signature of the closes' reds and of lens H's third run; on the head (2,071 files) 0 in 3 runs: dormant until the tree passes about 6,700 objects again (finding 5) | S3b | a copy that does not race git's background gc (gc.auto=0 in the session copy, or a copy of the working files without .git): one fix in the fixture for every W1-07 case | W2-67 (its per-test copies task); Rewrite-Reason: the copy races git's background gc | 0.7 |
| `test_w1_07_recorded_commands.py::test_a_recorded_gov_command_is_offered_and_answers_its_help[ci]` | flaky | errored at setup in my parallel runs of 14:40 and 14:57 on f46b1ff9; the shared `project` fixture copies the session's whole-tree copy (w1_07_support.py:144-152) while git's background gc, started by that copy's first commit above gc.auto's 6,700 loose objects, packs its loose objects away; in my parallel runs of W1-07 on the tree of W2-02's refused closes (f46b1ff9, 10,286 files, code, tests and kernel identical to the head's) it struck 6 times on 5 cases in 3 runs (14:40: 4 errors at setup and 1 failure; 14:57: 1 error; 14:20: none), each `shutil.Error: … .git/objects/NN: No such file or directory` in the session copy, the signature of the closes' reds and of lens H's third run; on the head (2,071 files) 0 in 3 runs: dormant until the tree passes about 6,700 objects again (finding 5) | DEC-542, DEC-569 (L6145) | a copy that does not race git's background gc (gc.auto=0 in the session copy, or a copy of the working files without .git): one fix in the fixture for every W1-07 case | W2-67 (its per-test copies task); Rewrite-Reason: the copy races git's background gc | 1.6 |
| `test_w1_07_envelope.py::test_an_error_envelope_carries_the_session_given` | outdated | written when gov check was NOT_IMPLEMENTED until W1-26 (DEC-186; README.md:82-84); since W1-26 it runs all 20 checks on the whole copy and is an error only because the copy has no derived state; it never asserts ok false (envelope.py:88-91), so it would pass on a success envelope | DEC-186's planned revision, W1-26 | revise: a cheap governance error (gov adopt --json --session ...) and ok false | a small test-revision ticket for W1-07 (or W2-67); Rewrite-Reason: gov check is built (DEC-190 'planned: command implemented') | 18.3 |
| `test_w1_07_registry.py::test_help_names_every_reserved_command` | weak | a word search over the whole help text (registry.py:35-36); 'readiness' and 'pause' also occur in status's help line ('tickets, gates, readiness, share, pause state', src/gov/cli/main.py:94), so a help without the readiness or pause entry is not seen; planted fault P07-1 (the parser skips pause), P07-2 (it skips doctor) the control; measured: under P07-1 the case was green (runs/plant/P07-1-help-without-pause.xml); measured: under the control P07-2 the case was red (runs/plant/P07-2-help-without-doctor-control.xml) | W1-07 KPI S5, CAP-28.b | revise: parse the command column | a small test-revision ticket for W1-07; Rewrite-Reason: word search | 2.3 |
| `test_w1_07_check_declarations.py::test_check_list_succeeds` | duplicate | the same call and the same assertions (_listed, check_declarations.py:44-49) as the first _listed of test_the_list_follows_the_declaration_files (:66-69), which then asserts more; record-reading like it (one malformed declaration in the tree refuses the whole list, src/gov/cli/checks.py:30-50) | S4, S1; DEC-186 (L1732) | keep (cheap; no retirement proposed); a test designer may fold it under W2-67 | — | 1.6 |
| `test_w1_07_envelope.py::test_a_governance_error_has_exit_code_1_and_its_code_in_the_json` | duplicate | the same call (gov adopt --json) and the same assert_error as test_w1_07_registry.py::test_a_reserved_command_not_yet_built_returns_not_implemented (registry.py:63-66) | W1-07 KPI S1 | keep (cheap; no retirement proposed) | — | 0.6 |
| `test_w1_07_envelope.py::test_an_unknown_command_is_a_usage_error` | duplicate | exit 2 for gov no-such-command --json, as test_a_name_outside_the_registry_is_not_answered_as_not_implemented; its envelope branch (envelope.py:62-64) never runs because argparse writes to stderr | W1-07 KPI S1 | keep (cheap; no retirement proposed) | — | 0.6 |
| `test_w1_07_envelope.py::test_the_envelope_has_no_field_outside_the_interface` | duplicate | assert_envelope (w1_07_support.py:439-457), which test_every_command_returns_the_envelope calls on the same 13 invocations, already checks the field set and the error keys; this function runs every command again on a whole-tree copy (gov check runs its 20 checks, doctor hashes the real tools); its [check] case also failed in my parallel run of 14:40 on f46b1ff9, on the copy race of finding 5 (another reason to retire it) | W1-07 KPI F2 | retire (owner package P-I4-1) | owner (P-I4-1) | 34.5 |
| `test_w1_07_read_act.py::test_a_read_command_leaves_git_status_empty` | duplicate | its 8 --json sets run the same commands as test_a_read_command_changes_no_file_and_no_ref, which compares the porcelain too (_state, read_act.py:22-28, 32-33) and more; the 8 plain sets are its own and stay; the 8 --json sets cost 24.9 s of the function's 60.2 s | W1-07 KPI S2, CAP-27.a | narrow to the plain form (owner package P-I4-3) | owner (P-I4-3) | 60.2 |
| `test_w1_07_registry.py::test_each_wave_1_operation_is_a_gov_command` | duplicate | its 12 runs are 12 of the 13 invocations of test_every_command_returns_the_envelope (EVERY_INVOCATION, w1_07_support.py:115), with the same assert_envelope(command=...); its one extra assertion, exit code not 2, fails only on argparse's usage error, which prints no envelope, so assert_envelope fails on it too (w1_07_support.py:396-399) | W1-07 KPI S5, CAP-28.b | merge its CAP-28.b label into the envelope case and retire the runs (owner package P-I4-2) | owner (P-I4-2) | 34.1 |

**W1-08**: W1-08 (DAEO-uudf)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_08_frontmatter.py::test_the_state_classes_are_written_in_one_schema_file_only` | weak | scans only W1-08's eight schemas (SCHEMA_TYPES, w1_08_support.py:35-46; frontmatter.py:79), so the 11 other kernel schemas of the 20 (probe, close, audit-report, adoption-verdict, register-entry, plan, specification, capability, the two change records, tool-registry; DEC-441, DEC-565, DEC-872) are never read; planted fault P08-3 (close.schema.json writes its own state classes); measured: under P08-3 the case was green (runs/plant/P08-3-state-class-in-a-later-schema.xml) | W1-08 KPI S6, DEC-229 | revise: every kernel schema file | W2-64 (the record-type widening) or a small test-revision ticket; Rewrite-Reason: the record types grew after W1-08 | 0.0 |
| `test_w1_08_id_grammar.py::test_no_record_schema_writes_an_id_pattern_of_its_own` | weak | iterates only W1-08's eight schemas (id_grammar.py:93); planted fault P08-4 (close.schema.json writes its own id pattern); measured: under P08-4 the case was green (runs/plant/P08-4-id-pattern-in-a-later-schema.xml) | W1-08 KPI F2, DEC-227 | revise: every kernel schema file | as above | 0.0 |

**W1-09**: W1-09 (DAEO-topz)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_09_create.py::test_a_created_ticket_is_the_ticket_the_script_writes` | weak | for failure 2 (README:101) it asserts only 'not in ready' (test:32-33), which any hold or an unreadable ticket satisfies; NO_ACCEPTANCE_TESTS is not checked | DEC-229, DEC-295, W1-09 KPI F2 | revise: blocked with exactly [NO_ACCEPTANCE_TESTS] | W2-34 (holds src/gov/tasks/**) or a small test-revision ticket | 0.4 |
| `test_w1_09_unloaded_package.py::test_a_package_that_loads_and_is_closed_does_not_block` | weak | tries ACCEPTED, REJECTED and SUPERSEDED; REJECTED and SUPERSEDED are not package statuses (DEC-328 line 3240; decision-package.schema.json:9), and DECLINED, REVOKED and STALE, the real ones, are never tried | DEC-308, DEC-328 | revise: the five statuses of DEC-328 | W2-34; Rewrite-Reason: statuses outside DEC-328 | 0.4 |
| `test_w1_09_unloaded_package.py::test_a_package_that_loads_and_is_open_gives_the_reason_of_today` | duplicate | the same file (spec/gates/DP-0001.md), record, ticket and interface as test_w1_09_decisions.py::test_a_ticket_waiting_on_an_open_decision_package_is_blocked | DEC-308 | keep (cheap) | — | 0.4 |

**W1-11**: W1-11 (DAEO-be7u)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_11_approval.py::test_the_owner_named_in_the_message_body_of_an_agent_commit_is_no_approval` | weak | the commit also carries the agent's own final trailer block, Role: engineer (w1_11_support.py:212, 263-264), so the owner-only rule (checker.py:359) refuses it even when the whole message is read: the final-block rule the case is named for is never isolated; planted fault P11-1 (the final block ignored); measured: under P11-1 the case was green (runs/plant/P11-1-final-block-ignored.xml) | S2; DEC-182, DEC-360 | revise: a commit whose only Role trailer is the owner's, in a non-final paragraph | a small test-revision ticket for W1-11; Rewrite-Reason: the final-block rule is never isolated | 0.4 |
| `test_w1_11_hazards.py::test_a_register_without_a_hazard_raises_no_hazard_finding` | duplicate | the same clean register (CLEAN by OWNER) as test_w1_11_approval.py::test_a_register_the_owner_approved_passes_the_whole_check, which asserts found == [] (approval.py:110) | DEC-329 | keep (cheap) | — | 0.1 |
| `test_w1_11_hazards.py::test_a_supersession_recorded_on_both_sides_is_not_flagged` | duplicate | the same input checked(api, project, {}) (hazards.py:29); implied by the line above | DEC-277 | keep (cheap) | — | 0.2 |

**W1-14**: W1-14 (DAEO-w9l3)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_14_refusals.py::test_no_ticket_is_derived_without_a_profile_or_a_class` | outdated | written while DP-2 was open: it accepts a refusal or a stated default (test:75-86, 'if not outcome.ok: ... return'); DEC-355 (register lines 3618-3623) decided refusal: 'A task that lacks one, profile and class included, refuses the whole derivation'; a bridge that silently defaults passes | DEC-355 | revise: refusal only | W2-34 (holds the bridge); Rewrite-Reason: DEC-355 decided DP-2 | 0.3 |

**W1-27**: W1-27 (DAEO-xw3k)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_27_adoption.py::test_completed_stages_raise_adoption_level` | weak | its pytest.fail is reached only without any of five words, and the result always holds the key 'healthy' (command.py:848); planted fault P27-3; measured: under P27-3 the case was green (runs/plant/P27-3-level-always-healthy.xml) | W1-27 KPI S5 | revise: compare the levels before and after the stages | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 1.2 |
| `test_w1_27_adoption.py::test_doctor_report_mentions_adoption_level` | weak | asserts 'adopt' or 'level' anywhere; the key adoption_level is always there (command.py:836); planted fault P27-3 (ADOPTED_HEALTHY for any project); measured: under P27-3 the case was green (runs/plant/P27-3-level-always-healthy.xml) | W1-27 KPI S5, CAP-54.a | revise: the level's value | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 6.7 |
| `test_w1_27_adoption.py::test_minimal_kernel_passes_at_minimal_level` | weak | asserts 'minimal', 'kernel' or 'level' in the result, and 'level' is a key of every adoption section (command.py:680); planted fault P27-3; measured: under P27-3 the case was green (runs/plant/P27-3-level-always-healthy.xml) | W1-27 KPI S5, CAP-54.a | revise: result.adoption_level.level == the lowest level | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 1.5 |
| `test_w1_27_doctor.py::test_doctor_real_registry_every_entry_reported` | weak | its 'not ok with a reason' half (doctor.py:159-174) is met by pinned_version, which every entry carries (doctor/command.py:471-478, 496-497): an entry that says nothing about why passes; planted fault P27-11 (a tool doctor cannot find reported with its pinned version only); the 'every entry reported' half holds; measured: under P27-11 the case was green (runs/plant/P27-11-not-found-without-reason.xml) | S1; CAP-25.a; DEC-452 | revise: a not-ok entry names its cause (found_version, sha256_match or reason) | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 7.8 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_canaries` | weak | asserts 'canar'; the key canaries is always there | W1-27 KPI S1 | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.1 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_framework_lock` | weak | asserts 'framework' or 'lock'; the key framework_lock is always there; MATCH or DRIFT is never read | W1-27 KPI S1, CAP-02.a | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 6.7 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_hooks` | weak | asserts 'hook' anywhere; gov doctor emits every section key on every run (src/gov/doctor/command.py:824-848), and in the copied project doctor is unhealthy (the real registry's pytest-xdist and pytest-testmon are looked for as binaries), so result is {} and every section sits in error.details | W1-27 KPI S1 | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.0 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_index_freshness` | weak | asserts 'index' or 'fresh'; the key index_freshness is always there | W1-27 KPI S1 | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.0 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_isolation` | weak | asserts 'isolat'; the key isolation is always there (isolation_r2.py:10-14 says so itself) | W1-27 KPI S1 | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.2 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_path_map_coverage` | weak | asserts 'path' or 'unclassified' anywhere; the keys path_map and path_compliance are always there; planted fault P27-4 (doctor never reports an unclassified path); measured: under P27-4 the case was green (runs/plant/P27-4-never-unclassified.xml) | W1-27 KPI S1, S3, CAP-06.a | revise with the structural case | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 4.8 |
| `test_w1_27_doctor.py::test_doctor_report_mentions_tool_versions` | weak | asserts 'tool' anywhere (doctor.py:185); gov doctor emits every section key on every run (src/gov/doctor/command.py:824-848), and in the copied project doctor is unhealthy (the real registry's pytest-xdist and pytest-testmon are looked for as binaries), so result is {} and every section sits in error.details; no version is read | W1-27 KPI S1, CAP-25.a | revise into one structural case per section: the section's typed fields (versions, sha256_match) | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.0 |
| `test_w1_27_doctor_r5.py::test_stale_path_in_live_document_is_reported` | weak | the same always-true alternative (r5:423); planted fault P27-1; measured: under P27-1 the case was green (runs/plant/P27-1-stale-never-reported.xml) | DEC-448, CAP-06.d | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.7 |
| `test_w1_27_doctor_r7.py::test_home_tool_wrong_sha256_not_ok` | weak | places no vec0.so, model manifest, venv python or model file (r7:497-501), so every branch returns 'not found' before any hash is compared (command.py:308-311, 327-330, 345-363, 391-395) | DEC-452, DEC-425 | revise: create the file each branch reads | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the planted input is not where doctor reads it | 5.9 |
| `test_w1_27_drift.py::test_cli_and_extension_different_versions_is_drift` | weak | its fake extension lies under tmp_path/extensions (drift.py:38-42), not under HOME/.vscode-server or .vscode where doctor looks (command.py:720-722); 'drift' always present | DEC-210 | revise: the extension where doctor reads it | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the planted input is not where doctor reads it | 3.2 |
| `test_w1_27_drift.py::test_cli_at_recorded_version_different_sha256_is_failure` | weak | the real CLI is 2.1.292, so the recorded-version sha256 rule (command.py:759-764) never runs; it passes on the real CLI's drift: under the planted P27-6 (that drift removed) doctor passed and the case went red (runs/plant/P27-6-no-newer-cli-drift.xml) | DEC-214 | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the fake CLI is never read | 1.2 |
| `test_w1_27_drift.py::test_cli_below_minimum_is_failure` | weak | the fake is never read; the case is green only because this machine's real CLI (2.1.292) is newer than the case's pin 2.1.288 (command.py:775-782). Shown by the planted P27-6 (that drift removed, command.py:778): doctor then passed and the case went red, as did the sha256 and extension-below-minimum cases (runs/plant/P27-6-no-newer-cli-drift.xml); removing the below-minimum rule it names (command.py:752-754) would leave it green | DEC-210 | revise: put the fake first on the PATH doctor sees | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the fake CLI is never read | 2.7 |
| `test_w1_27_drift.py::test_cli_newer_than_registry_is_drift` | weak | its fake CLI lies in sandbox.bin (drift.py:28), which is not on the doctor process's PATH (w1_27_support.py:80), and the key 'drift' is always in the claude_code section (command.py:804); under the planted P27-6 (the newer-than-registry drift removed, command.py:778) it stayed green (runs/plant/P27-6-no-newer-cli-drift.xml) | W1-27 KPI S6, DEC-210 | revise: put the fake first on the PATH doctor sees | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the fake CLI is never read | 2.0 |
| `test_w1_27_drift.py::test_extension_below_minimum_is_failure` | weak | the extension is never read; it passes on the real CLI's newer-than-registry drift: under the planted P27-6 (that drift removed) doctor passed and the case went red (runs/plant/P27-6-no-newer-cli-drift.xml) | DEC-210 | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the fake extension is never read | 1.4 |
| `test_w1_27_drift.py::test_extension_bundled_binary_different_sha256_is_drift` | weak | the same two reasons | DEC-214 | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the planted input is not where doctor reads it | 3.5 |
| `test_w1_27_held_out.py::test_missing_held_out_yaml_is_reported` | weak | asserts 'held' anywhere (held_out.py:38); the key held_out is always emitted, missing or not; planted fault P27-2 (the held-out check inverted); measured: under P27-2 the case was green (runs/plant/P27-2-held-out-inverted.xml) | W1-27 KPI S7, DEC-223 | revise: held_out.missing is true (in result or error.details) | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 6.1 |
| `test_w1_27_held_out.py::test_present_held_out_yaml_is_not_reported` | weak | reads only result (held_out.py:56), which is {} whenever doctor is unhealthy (main.py:225), so no check runs; planted fault P27-2; measured: under P27-2 the case was green (runs/plant/P27-2-held-out-inverted.xml) | W1-27 KPI S7, DEC-223 | revise: read error.details when doctor is unhealthy | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the case reads result, which is empty when doctor is unhealthy | 5.3 |
| `test_w1_27_isolation_r2.py::test_doctor_isolation_is_measured_not_constant` | weak | rejects one exact stub only (r2:48-53); the copy has no .gov-runtime, so the measured branch (command.py:637-650) is never reached; planted fault P27-9 (isolated = True); measured: under P27-9 the case was green (runs/plant/P27-9-isolation-constant.xml) | DEC-425 | revise: a project with .gov-runtime, both outcomes | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.2 |
| `test_w1_27_path_compliance.py::test_full_coverage_is_healthy` | weak | reads only result (empty when doctor is unhealthy) and only top-level int or list values, while unclassified_count is nested (pc:42-53); the count stays 0 whatever doctor says | W1-27 KPI S3, CAP-06.a | revise: path_map.unclassified_count == 0 | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the case reads result, which is empty when doctor is unhealthy | 5.3 |
| `test_w1_27_path_compliance.py::test_moved_path_reference_is_reported` | weak | no file names the old path at all (pc:75-84), and 'moved' is the key moved_references; planted fault P27-1 (doctor never reports a moved-path reference); measured: under P27-1 the case was green (runs/plant/P27-1-stale-never-reported.xml) | W1-27 KPI S3, CAP-06.d | revise: write a referencing file and read moved_references | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 7.9 |
| `test_w1_27_path_compliance.py::test_unclassified_path_is_reported` | weak | ok is false on every machine for the tools section alone, and 'path' is a key name (pc:62-66); planted fault P27-4 (doctor never reports an unclassified path); measured: under P27-4 the case was green (runs/plant/P27-4-never-unclassified.xml) | W1-27 KPI S3, CAP-06.d | revise: path_map.unclassified names the path | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 6.4 |
| `test_w1_27_path_compliance_r2.py::test_old_path_standalone_is_stale_when_new_path_elsewhere` | weak | the same always-true alternative (pc_r2:262); planted fault P27-1; measured: under P27-1 the case was green (runs/plant/P27-1-stale-never-reported.xml) | DEC-456 | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 5.8 |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_live_document_not_sources_is_reported` | weak | asserts the fixture's name, 'moved' or 'stale' (pc_r2:100); 'moved' is always there (moved_references); planted fault P27-1; measured: under P27-1 the case was green (runs/plant/P27-1-stale-never-reported.xml) | DEC-456, CAP-06.d | revise: moved_references holds the live document | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 7.9 |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_src_gov_cli_is_reported` | weak | the same always-true alternative (pc_r2:175); planted fault P27-1; measured: under P27-1 the case was green (runs/plant/P27-1-stale-never-reported.xml) | DEC-456 | revise as above | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 11.2 |
| `test_w1_27_rebuild.py::test_fresh_clone_doctor_rebuild` | weak | makes no clone (rebuild.py:95) and does not assert doctor's verdict (98-99) | CAP-46.a | revise: git clone of a committed project, then doctor and rebuild | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 17.8 |
| `test_w1_27_rebuild.py::test_rebuild_digest_matches_store_loader` | weak | compares the digests only if the envelope's session is a dict, and it is a string (API-0002.yaml:19; main.py:129, 180), so rebuild.py:151-158 never compares; planted fault P27-7 (a reversed digest); measured: under P27-7 the case was green (runs/plant/P27-7-rebuild-digest-reversed.xml) | W1-27 KPI S2, CAP-07.a | revise: compare with gov.store.load's digest | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 14.6 |
| `test_w1_27_rebuild.py::test_rebuild_is_an_act_command` | weak | accepts any envelope, REBUILD_FAILED included (rebuild.py:36-37); the act class and the write scope are not checked | W1-27 KPI S2, CAP-27.a | revise: CLASS act and writes only under .gov-runtime | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 26.0 |
| `test_w1_27_rebuild.py::test_rebuild_needs_only_git` | weak | the folder it deletes never exists in the tiny project (rebuild.py:123-126), and it runs with gitleaks and codebase-memory-mcp present; otherwise the same as test_rebuild_recreates_derived_stores | W1-27 KPI F2, CAP-20.a | revise: a PATH with git alone | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 15.8 |
| `test_w1_27_rebuild.py::test_rebuild_recreates_derived_stores` | weak | checks that .gov-runtime exists only (rebuild.py:53-55); the round-2 file says so itself (r2:12-16) | W1-27 KPI S2, CAP-07.a | keep; a test designer may fold it into r2's table cases (no retirement proposed) | W2-67 | 21.9 |
| `test_w1_27_rebuild_r2.py::test_rebuild_result_names_unreconstructed_stores` | weak | stores.semantic is always present in the result (rebuild/command.py:85-108) | CAP-07.a | revise: the status and reason of each store not rebuilt | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 12.1 |
| `test_w1_27_rebuild_r3.py::test_rebuild_result_names_derived_stores_with_measured_status` | weak | computes has_status_per_store and has_constant_only and never asserts them (r3:176-195); only r3:199 runs | DEC-416, DEC-425 | revise: assert the computed facts | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 11.4 |
| `test_w1_27_rebuild_r4.py::test_rebuild_codeintel_reason_is_measured` | weak | any reason other than one fixed text passes (r4:282) | DEC-440 | revise: the measured status and reason | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 11.8 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime` | weak | snapshots sandbox.elsewhere, which nothing uses (r8:272-277), not the home nor /tmp/gov-cbm-<uid> where codeintel writes (codeintel/__init__.py:35) | DEC-530 | revise: snapshot the home and the daemon folder | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 14.9 |
| `test_w1_27_recovery_check_r2.py::test_recovery_rebuild_check_reports_unmeasured_when_no_store` | weak | 'unmeasured' is not asserted (r2:145-153); a non-zero exit of any cause passes | DEC-425 | revise: the unmeasured wording | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 5.9 |
| `test_w1_27_recovery_check_r2.py::test_recovery_rebuild_command_exits_nonzero_on_tampered_store` | weak | a crash also exits non-zero; the mismatch is not read and no case holds a clean store green (r2:120-126) | CAP-38.b, CAP-20.a | revise: the mismatch named, and a green control | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 13.5 |
| `test_w1_27_recovery_check_r2.py::test_recovery_rebuild_command_not_unconditionally_exit_zero` | weak | the declared command is python3 -m gov.rebuild.check (recovery-rebuild.yaml:7) and never holds 'exit(0)', so r2:85-88 holds whatever check.py does | CAP-38.b | revise: run it on a clean store (green) and a tampered one (red) | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 0.3 |
| `test_w1_27_doctor_r5.py::test_doctor_does_not_modify_path` | duplicate | its PATH half compares the parent's own PATH, which no child can change (r5:318-328); its snapshot half repeats test_doctor.py::test_doctor_is_a_read_command | DEC-448, CAP-27.a | keep or merge (one doctor run, about 6 s) | — | 1.4 |
| `test_w1_27_doctor_unmeasured_r3.py::test_healthy_false_when_measurement_error` | duplicate | the same corrupt-store input as test_doctor_index_freshness_error_is_fail (r3:89-96 vs 265-272); the verdict follows from that section (command.py:843-846) | DEC-425 | keep or merge (one doctor run) | — | 2.7 |
| `test_w1_27_rebuild_r2.py::test_rebuild_does_not_silently_drop_lexical_tables` | duplicate | the same table-presence check as test_rebuild_recreates_lexical_index (r2:114 vs 73-78); the planted row's fate is not checked | CAP-07.a | revise: check the planted row is gone after the rebuild | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion does not read what the case's name claims | 26.1 |
| `test_w1_27_rebuild_r5.py::test_rebuild_owner_raises_not_complete` | duplicate | returns green when no envelope is printed, its own red reason (r5:269-272); otherwise implied by test_rebuild_owner_raises_gives_error_envelope (r5:245) | DEC-440 | keep (tiny project, cheap) | — | 0.5 |
| `test_w1_27_schema.py::test_code_intelligence_disabled_languages_optional` | duplicate | the same document as test_valid_w1_08_path_map_loads (the minimal map is disabled, no languages), with a weaker assertion | DEC-265 | keep (cheap; no retirement proposed); a test designer may fold the pair under W2-67 | — | 10.1 |
| `test_w1_27_schema.py::test_missing_namespaces_names_the_key` | duplicate | W1-07 test_a_missing_namespaces_names_the_key[status] holds the same input shape and command, stricter | DEC-189 | keep (cheap; no retirement proposed); a test designer may fold the pair under W2-67 | — | 1.5 |
| `test_w1_27_schema.py::test_namespaces_of_the_wrong_type_names_the_key` | duplicate | W1-07's namesake [a-number-status] holds the same input and command with key == namespaces | DEC-189 | keep (cheap; no retirement proposed); a test designer may fold the pair under W2-67 | — | 1.4 |
| `test_w1_27_schema.py::test_valid_w1_08_path_map_is_not_reported_as_invalid` | duplicate | W1-07 test_a_valid_path_map_is_not_reported_as_invalid_by_any_command covers the same invocations and document | DEC-228 | keep (cheap; no retirement proposed); a test designer may fold the pair under W2-67 | — | 23.9 |
| `test_w1_27_schema.py::test_valid_w1_08_path_map_loads` | duplicate | W1-07 test_w1_07_config_details.py::test_a_valid_path_map_loads runs the same command on a near-identical document (config_details:74, 149-153) | DEC-185, DEC-228 | keep (cheap; no retirement proposed); a test designer may fold the pair under W2-67 | — | 5.7 |

**W1-32**: W1-32 (DAEO-8goq)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_32_command_set.py::test_status_has_no_sub_command_and_no_argument_that_acts` | weak | filters option names against seven words (command_set.py:71-73): an acting option under another name passes | W1-32 KPI S4, F1 | revise: the module's CLASS and ACT_PATHS, or a run that shows nothing written | a small test-revision ticket for W1-32; Rewrite-Reason: name filter | 0.4 |
| `test_w1_32_status_parts.py::test_the_plain_form_shows_the_same_parts` | weak | a substring test (status_parts.py:212) on the plain form's JSON text (main.py:187): [tickets] passes from the 'tickets' keys of packages and the share (status/command.py:84-85, 130-131) with the part itself missing; planted fault P32-1 (the tickets part dropped), test_the_answer_has_the_six_parts the control; measured: under P32-1 the case was green (runs/plant/P32-1-status-without-tickets-part.xml) | W1-32 KPI S2 | revise: parse the plain output's top-level keys | with the case above | 7.2 |
| `test_w1_32_command_set.py::test_status_is_one_of_the_wave_1_operations` | duplicate | the same gov --help parse as test_the_command_set_is_the_twelve_and_the_three_recorded_ones, which holds all twelve (command_set.py:60) | W1-32 KPI S5 | keep (cheap) | — | 0.5 |
| `test_w1_32_status_parts.py::test_an_answered_package_is_not_listed_as_open` | duplicate | implied by the equality at status_parts.py:99 on the same run | W1-32 KPI S2 | keep (cheap) | — | 1.1 |
| `test_w1_32_status_parts.py::test_the_open_decision_packages_are_listed` | duplicate | the same project, call and id equality as test_w1_32_added_cases.py::test_a_project_whose_records_all_load_keeps_its_clean_list_of_packages (added_cases.py:132-137) | W1-32 KPI S2 | keep (cheap) | — | 1.3 |
| `test_w1_32_status_read_only.py::test_git_status_porcelain_is_unchanged` | duplicate | its json set is inside test_status_writes_nothing_anywhere[json] (the same project and call; the porcelain compared in assert_unchanged, w1_32_support.py:308-316); the plain set is its own | W1-32 KPI S4, CAP-27.a | keep (cheap) | — | 2.3 |

**W1-33**: W1-33 (DAEO-xog0)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_33_guard_and_launcher.py::test_only_the_test_designer_may_write_the_acceptance_tests[engineer]` | weak | green under the planted PG-2: the engineer's ticket names no acceptance path (tests/acceptance/W1-03/w1_03_support.py:109-114), so the Write is stopped as outside the ticket whatever the acceptance rule says; the fixture's engineer ticket that names tests/acceptance/** (:250-253) is not used; README:36 claims this case as the guard half of failure line 2 | S2, F2, MR-3, DEC-069 | run the case under the ticket that names tests/acceptance/**, and correct README:36 | a small test-revision ticket for W1-33 (or W2-65); Rewrite-Reason: the rule is never reached | 0.1 |
| `test_w1_33_guard_and_launcher.py::test_only_the_test_designer_may_write_the_acceptance_tests[product-spec]` | weak | green under the planted PG-2, for the same reason: the product-spec ticket names no acceptance path (w1_03_support.py:244-249) | S2, F2, MR-3, DEC-069 | as the [engineer] case | a small test-revision ticket for W1-33 (or W2-65); Rewrite-Reason: the rule is never reached | 0.2 |
| `test_w1_33_guard_and_launcher.py::test_the_auditor_writes_only_the_report_path_of_its_own_ticket` | weak | the other ticket (DAEO-zz90) does not cover docs/audit/** (test:60-62), so a guard that ignores the ticket's role passes: under the planted PG-1 (decide.py:154, the role test removed) it stayed green (runs/plant/PG-1-ticket-role-ignored.xml). The rule itself is held elsewhere: under PG-1b, the same fault against the guard's own suites, 30 cases went red (W1-02 25, W1-45 3, the guard's unit tests 2) | DEC-112, CAP-58.b | revise: give the other ticket an independent-auditor role with the same report path | W2-65 (the next guard ticket) or a small test-revision ticket; Rewrite-Reason: the other ticket cannot tell the role rule | 0.6 |
| `test_w1_33_kernel_role_files.py::test_a_launched_worker_names_the_launcher_s_empty_network_profile` | weak | words only (w1_33_support.py:439-443): 'is not empty' passes | DEC-158 | revise: the field's value | W2-11 | 0.0 |
| `test_w1_33_kernel_role_files.py::test_no_other_pattern_includes_the_acceptance_tests` | weak | every sentence naming tests/acceptance must hold an excluding word, and the words include 'no' and 'not' (w1_33_support.py:121-122): 'may write tests/acceptance/**, not only src' passes | MR-3, W1-33 KPI F2 | revise: parse the Allowed paths field's patterns | W2-11 (holds the role files) | 0.0 |
| `test_w1_33_agent_definitions.py::test_the_orchestrator_definition_states_its_write_scope` | duplicate | role_faults already runs this check in test_the_definition_states_what_the_kpis_require_of_the_role[orchestrator] (w1_33_support.py:452-453) | DEC-156 | keep (cost nil) | — | 0.0 |
| `test_w1_33_kernel_role_files.py::test_no_other_role_may_install` | duplicate | in class_faults (w1_33_support.py:421-423) | DEC-083, DEC-157 | keep (cost nil) | — | 0.0 |
| `test_w1_33_kernel_role_files.py::test_the_orchestrator_may_install_only_after_owner_approval` | duplicate | the same check is in class_faults (w1_33_support.py:418-419), run by test_the_role_maps_the_classes_as_the_contract_says | DEC-083 | keep (cost nil) | — | 0.0 |
| `test_w1_33_kernel_role_files.py::test_the_role_maps_every_permission_class` | duplicate | covered by class_faults' 'is not mapped' (w1_33_support.py:405-407) | CAP-58.b | keep (cost nil) | — | 0.0 |

**W1-34**: W1-34 (DAEO-egm9)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_34_decision_package.py::test_the_routing_rule_classes_a_contradiction` | weak | the template's routing rule is one paragraph (decision-package template :16-20): 'package' is met by 'raise no package' (:18) without 'Raise it as a package' (:20), and 'precedence' by :19; planted fault P34-1 (the routing sentence gone); measured: under P34-1 the case was green (runs/plant/P34-1-routing-sentence-gone.xml) | S5 [CAP-34.a] | revise: read the human-resolvable sentence itself | a small test-revision ticket for W1-34; Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |

**W1-35**: W1-35 (DAEO-0i6h)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_35.py::TestFailureTestDesignReadsImpl::test_test_design_states_restriction` | outdated | KPI F2 as written before DEC-820 (c); also weak: 'no' matches inside 'not' or 'know' (test_w1_35.py:508); planted fault PS-1; measured: under PS-1 the case was green (runs/plant/PS-1-test-designer-reads-the-code.xml) | DEC-820 (c) | revise with the cases above | W2-11; Rewrite-Reason: DEC-820 (c) | 0.0 |
| `test_w1_35.py::TestReferencedCommands::test_referenced_commands_are_known` | outdated | accepts only the twelve reserved commands (test_w1_35.py:656); since DEC-542 (line 5896) the product records fifteen (src/gov/check/commands.py:14-18), so a correct skill naming gov launch or gov ci would be refused; also skips spans with arguments | DEC-542, DEC-546 | revise: the product's command list (GOV_COMMANDS), not a copy | W2-11; Rewrite-Reason: DEC-542 | 0.0 |
| `test_w1_35.py::TestTestDesignConstraints::test_test_design_no_implementation_files` | outdated | the same rule as above (DEC-820 (c)); also weak: met by test-design:4 or 'not as code' (:32); planted fault PS-1 (the skill told to read the implementation); measured: under PS-1 the case was green (runs/plant/PS-1-test-designer-reads-the-code.xml) | DEC-820 (c) | revise with the case above | W2-11; Rewrite-Reason: DEC-820 (c) | 0.0 |
| `test_w1_35.py::TestTestDesignConstraints::test_test_design_reads_only_spec_and_kpis` | outdated | holds the test-design skill to 'reads only the ticket's specification and its KPIs' (test-design/SKILL.md:13); DEC-820 (c) (line 8976): the designer works 'from the specification, the KPIs and the existing code they must work with' and never reads that ticket's implementation; W2-11's supersession KPI does not name this rule (finding 7) | DEC-820 (c) | revise to DEC-820 (c): never the ticket's implementation; the existing code allowed | W2-11 (add DEC-820 (c) to its supersession KPI); Rewrite-Reason: DEC-820 (c) | 0.0 |
| `test_w1_35.py::TestTestDesignReadRestrictionProxy::test_test_design_declares_read_restriction` | outdated | proxy of the same KPI line (any 'only', test_w1_35.py:781); DEC-820 (c); planted fault PS-1; measured: under PS-1 the case was red (runs/plant/PS-1-test-designer-reads-the-code.xml) | DEC-820 (c) | revise with the cases above | W2-11; Rewrite-Reason: DEC-820 (c) | 0.0 |
| `test_w1_35_orchestration.py::TestBriefTemplates::test_the_brief_carries_the_standing_sentences_word_for_word` | outdated | standing sentence 3, word for word in the five brief templates (support:60-66): 'Run no glob, no search and no listing over governance/project/ ... (DEC-508). Never read .claude/settings.json'; DEC-820 (line 8969-8981) replaces DEC-508's listing refusals and every read restriction beyond four; sentences 1 and 2 stay valid | DEC-820, DEC-821 item 3 | revise sentence 3 to Policy 2's read rule; keep sentences 1 and 2 | W2-11 (its supersession KPI, .tickets/DAEO-k7hz.md:46-48, already names these cases); Rewrite-Reason: DEC-820 | 0.0 |
| `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_every_gov_command_the_skill_names_is_a_known_one` | outdated | the twelve commands (test_w1_35_orchestration.py:100) against the product's fifteen (DEC-542); it blocks W2-11's KPI W2-L257 (the launcher stated as a command) | DEC-542 | revise: the product's command list | W2-11; Rewrite-Reason: DEC-542 | 0.0 |
| `test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated[temp hygiene and protected files]` | outdated | the row requires 'no glob, search or listing over the project's governance folder' and 'the settings file ... never read' (support:286-290); DEC-820 (line 8970, Replaces DEC-508's listing refusals) opened reads; DEC-821 item 3 (line 8988) narrowed the rest; W2-58 built it (merged 4845b9b8) | DEC-820, DEC-821 item 3 | revise: the four refusals of DEC-820 instead of the listing and settings bans | W2-11 (its supersession KPI, .tickets/DAEO-k7hz.md:46-48, already names these cases); Rewrite-Reason: DEC-820 | 0.0 |
| `test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated[the ticket loop]` | outdated | the row's clause list holds 'the return form LEAD_CHECKPOINT' (w1_35_orchestration_support.py:165); retired by DEC-838 item 2 (line 9141); the skill still says it (orchestration/SKILL.md:34) | DEC-838 item 2 | revise: drop the LEAD_CHECKPOINT clause | W2-11 (its supersession KPI, .tickets/DAEO-k7hz.md:46-48, already names these cases); Rewrite-Reason: DEC-838 item 2 | 0.0 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_returns` | outdated | requires LEAD_CHECKPOINT among the lead's return forms (test_w1_35_orchestration.py:238-241); DEC-838 item 2 (register line 9141): 'LEAD_CHECKPOINT is no longer a lead's status'; the role file still says it (orchestrator.md:20, 60), so the test passes on stale kernel text | DEC-838 item 2 (changes DEC-236) | revise: the return forms are DONE, PACKAGES, ESCALATION | W2-11 (its supersession KPI, .tickets/DAEO-k7hz.md:46-48, already names these cases); Rewrite-Reason: DEC-838 item 2 | 0.0 |
| `test_w1_35.py::TestAuditTicketOnCITE::test_change_audit_on_cit_e_closed_spine` | weak | reduces to 'audit' being present | CAP-47.d | revise: audit, CIT-E and closed spine in one statement | W2-11 | 0.0 |
| `test_w1_35.py::TestCITWorkflow::test_change_skill_cit_steps_present` | weak | six of the seven step words stand on other lines of the change skill too (evidence 6 lines, corroboration 3, proposal 9, cit-p 5, independent review 4, owner approval 4; only 'versioned promotion' on its own step, :30), so a step can go and the case stays green; planted fault PS-7 (the evidence step gone); measured: under PS-7 the case was green (runs/plant/PS-7-cit-evidence-step-gone.xml) | CAP-33.a | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestCITWorkflow::test_change_skill_cites_cap33d` | weak | 'CAP-33' alone satisfies it, and it stands on 16 lines of the change skill (CAP-33.d, .e, .f), as for its two siblings already weak | CAP-33.d | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestChangeSkillLifecycle::test_change_skill_documents_lifecycle` | weak | the five lifecycle words anywhere (test:171-175); all five sit in the description line (change/SKILL.md:3) and on 4 to 9 lines each, so the body's lifecycle can go and the case stays green (planted fault PS-2 shows it for its order sibling); measured: under PS-2 the case was green (runs/plant/PS-2-version-step-first.xml) | CAP-24.c | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestChangeSkillLifecycle::test_change_skill_lifecycle_order` | weak | orders the first occurrences of the five words, which all sit in the description line (change/SKILL.md:3), so the body's steps (:15-19) can be reordered unnoticed (test:180-189); planted fault PS-2 (the version step first); measured: under PS-2 the case was green (runs/plant/PS-2-version-step-first.xml) | CAP-24.c | revise: read the order of the numbered steps in the body | W2-11 (holds the kernel skills); Rewrite-Reason: the order is read from the description line | 0.0 |
| `test_w1_35.py::TestDecisionPackages::test_discovery_mentions_cap_of_five` | weak | accepts any '5' in the text (test:403), e.g. inside DEC-105 | CAP-34.c | revise: 'five' or 'at most 5' as a phrase | W2-11 | 0.0 |
| `test_w1_35.py::TestDecisionPackages::test_discovery_mentions_decision_packages` | weak | 'decision package' stands on 6 lines of the discovery skill, the description (:4) among them, so the section can go and the case stays green | DEC-093, CAP-34.c | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_evidence_record` | weak | 'evidence' and 'record' read apart; they stand on 5 and 3 lines of the discovery skill | CAP-32 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_mentions_experiments` | weak | 'experiment' stands on 7 lines of the discovery skill, the description (:4) among them, so the Experiments section can go and the case stays green | CAP-32 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestDiscoveryRetrievalProxy::test_discovery_mentions_retrieval` | weak | 'context' is generic and satisfies it | CAP-16 | revise: 'gov retrieve' or 'retrieval' | W2-11 | 0.0 |
| `test_w1_35.py::TestEvidenceTriggeredChange::test_change_cit_p_on_contradiction` | weak | 'contradict' or 'conflict'; 'contradict' stands on 2 lines of the change skill; CIT-P is not tied to it | CAP-33.e, DEC-105 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestEvidenceTriggeredChange::test_change_cites_dec105_or_cap33e` | weak | 'CAP-33' alone satisfies it, and the skill holds CAP-33.d; a skill without DEC-105 and CAP-33.e passes | CAP-33.e | revise: the exact ids | W2-11 | 0.0 |
| `test_w1_35.py::TestEvidenceTriggeredChange::test_change_versions_kept` | weak | 'version' is a frontmatter key of every skill; 'kept' anywhere completes it | CAP-33.e | revise: the sentence that keeps every version | W2-11 | 0.0 |
| `test_w1_35.py::TestImpactAssessment::test_change_cites_dec167_or_cap33f` | weak | 'CAP-33' alone satisfies it, as above | CAP-33.f | revise: the exact ids | W2-11 | 0.0 |
| `test_w1_35.py::TestImpactAssessment::test_change_mentions_gov_closure` | weak | 'closure' alone; it stands on 3 lines of the change skill; the command is not read | CAP-33.f | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestImpactAssessment::test_change_mentions_impact_assessment` | weak | 'impact' alone; it stands on 6 lines of the change skill | CAP-33.f | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestImpactAssessment::test_change_mentions_openspec` | weak | 'openspec' stands on 3 lines of the change skill (:27, the CIT proposal; :48, the impact method's own step; :58, the tools), so the impact step can go and the case stays green; planted fault PS-13 (that step gone); measured: under PS-13 the case was green (runs/plant/PS-13-impact-openspec-step-gone.xml) | DEC-167, CAP-33.f | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestPlanningGapTickets::test_planning_mentions_gap_tickets` | weak | 'gap' or 'linked'; they stand on 7 and 2 lines of the planning skill | CAP-30.b | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestPlanningGapTickets::test_planning_mentions_readiness_rows` | weak | 'readiness' alone; it stands on 7 lines of the planning skill; the rows are not read | CAP-30.b | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestPlanningGapTickets::test_planning_mentions_schema_valid_tickets` | weak | checks the word 'ticket', true of any planning text | CAP-30.b | revise: 'schema-valid' and the ticket schema | W2-11 | 0.0 |
| `test_w1_35.py::TestPlanningGapTickets::test_planning_mentions_ticket_classes` | weak | two of four class words are enough (test_w1_35.py:440-447), and the work-order list alone gives three (discovery, research :15; data :17), so both class lines (:28, :33) can go | DEC-089, CAP-30.b | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestPlanningSchemaProxy::test_planning_mentions_schema` | weak | 'ticket' satisfies it (any planning text) | CAP-30.b | revise: 'schema' | W2-11 | 0.0 |
| `test_w1_35.py::TestProbeFindings::test_test_design_described_behaviours_not_code` | weak | 'not' anywhere completes it | CAP-38.e | revise: 'described behaviour, never code' as one statement | W2-11 | 0.0 |
| `test_w1_35.py::TestProbeFindings::test_test_design_mentions_probe_findings` | weak | 'orchestrator' alone satisfies it | CAP-38.e | revise: the probe-finding sentence | W2-11 | 0.0 |
| `test_w1_35.py::TestRoutingBatchingState::test_discovery_carries_routing_rules` | weak | 'rout' as a substring (test:675); it stands on 2 lines of the discovery skill; no rule is read | CAP-34 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestSpecificationWorkOrder::test_discovery_states_work_order` | weak | four of the five step words stand outside their own step line (discovery on 8 lines, the name among them; scenario 5; data :17 and :19; acceptance test :19 and :20); only 'implementation' is on its step alone; planted fault PS-5 (step 1 moved last); measured: under PS-5 the case was green (runs/plant/PS-5-discovery-step-1-last.xml) | DEC-103, CAP-30.f | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestSpecificationWorkOrder::test_owner_reviews_scenarios_and_ux_not_tests` | weak | checks only 'owner' and 'scenario'; 'UX' and 'not test code' are not read (test:375-376) | CAP-30.f | revise: all three parts of the rule | W2-11 | 0.0 |
| `test_w1_35.py::TestSpecificationWorkOrder::test_planning_states_work_order` | weak | every step word stands on more than one line of the planning skill (discovery 5, scenario 3, data 4, acceptance test 3, implementation 2); planted fault PS-6 (the scenario step gone); measured: under PS-6 the case was green (runs/plant/PS-6-planning-scenario-step-gone.xml) | DEC-103, CAP-30.f | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestSpecificationWorkOrder::test_work_order_correct_sequence_discovery` | weak | compares first occurrences (test_w1_35.py:357-370), and 'discovery' first occurs in the frontmatter's name (:2), so the discovery step can move anywhere; planted fault PS-5 (step 1 moved last); measured: under PS-5 the case was green (runs/plant/PS-5-discovery-step-1-last.xml) | DEC-103 | revise: read the numbered list's order | W2-11 (holds the kernel skills); Rewrite-Reason: the check reads the first occurrence of a word | 0.0 |
| `test_w1_35.py::TestTestDesignConstraints::test_change_covers_audit_ticket` | weak | 'audit' and 'ticket' read apart; they stand on 2 and 4 lines of the change skill | CAP-47.d | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_35.py::TestCITUsesOpenSpec::test_change_cit_p_uses_openspec` | duplicate | identical check to TestImpactAssessment::test_change_mentions_openspec (test:621-625) | CAP-33.f | keep (cost under 0.01 s; no retirement proposed) | — | 0.0 |
| `test_w1_35.py::TestFailureBodyExceeds::test_body_over_2500_tokens_would_fail` | duplicate | the same assertion on the same text as TestFrontmatterAndSize::test_body_within_2500_tokens (test:94-98 equals 79-83); no over-limit input is tried, so it is also weak | W1-35 KPI F1 | merge: give it an over-limit body (TestSkillRegressionRedBodyTooLong already does, through gov check) | W2-11 | 0.0 |
| `test_w1_35.py::TestFailureMissingGapTicket::test_planning_states_gap_ticket_requirement` | duplicate | its first condition is test_planning_mentions_gap_tickets's (test:529 vs 430), the second generic | CAP-30.b | keep (cost under 0.01 s; no retirement proposed) | — | 0.0 |
| `test_w1_35.py::TestPlannedVsMisspeltCommands::test_misspelt_command_is_rejected` | duplicate | the same fault and the same check path as TestSkillRegressionRedUnknownCommand (an unknown gov word gives the family RED), on another skill file; each runs gov check on a whole-tree copy | W1-35 KPI S8 | keep (12.4 s); a test designer may merge the two into one run under W2-67; no retirement proposed | — | 12.4 |

**W1-36**: W1-36 (DAEO-skiy)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_agreed_fixes_become_tickets` | weak | 'ticket' anywhere (test:104-106); it stands on 2 lines of the audit skill | W1-36 KPI S2 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_owner_finding_requires_decision_package_before_ticket` | weak | 'owner' and 'package' are both in audit/SKILL.md:47; planted fault PS-3 (an owner-level finding becomes a ticket at once, without a decision package); measured: under PS-3 the case was green (runs/plant/PS-3-owner-finding-straight-to-ticket.xml) | W1-36 KPI F3, MR-4 | revise: read the ordering rule's own sentence | a small test-revision ticket (W1-36's skills have no open owner; W2-11 holds the kernel skills); Rewrite-Reason: the rule's sentence is not read | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_owner_level_findings_become_decision_packages` | weak | checks 'owner', always present in the audit skill | W1-36 KPI S2 | revise: the owner-level finding sentence | with the case above | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_inputs_are_context_pack_and_repository` | weak | 'repo' matches inside 'report' (test:58) | CAP-47.b | revise: word boundaries | with the case above | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_report_states_pack_hash` | weak | 'hash' anywhere (test:65-67); it stands on 2 lines of the audit skill; the report's pack hash is not read | CAP-47.b, DEC-441 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_has_rows_per_contract_item_and_decision` | weak | 'line' and 'cap' match inside other words (test:29-30) | CAP-47.d | revise: word boundaries | with the case above | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_names_its_milestone` | weak | 'milestone' anywhere; it stands on 2 lines of the audit skill | CAP-47.d | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_36_audit_skill.py::TestAuditReportDEC441Form::test_mentions_commit_as_report_field` | weak | 'frontmatter' or '`commit`' (test:155-158): 'frontmatter' alone passes | DEC-441 | revise: the commit field | with the case above | 0.0 |
| `test_w1_36_retrieval_skill.py::TestRetrievalFailure::test_the_skill_addresses_the_main_context_boundary` | weak | 'caller' is enough (retrieval_skill.py:49-54) and stands on :9, a sentence about the guard, so the boundary rule (:15's last sentence, :27) can go and the case stays green; planted fault PS-11 (both lines gone); measured: under PS-11 the case was green (runs/plant/PS-11-disposable-subagent-rule-gone.xml) | DEC-032, CAP-56 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_mentions_facets` | weak | 'facet' stands on 4 body lines of the retrieval skill (:15, 17, 19, 27); the two that state the rule that facets run in disposable subagents (:15, :27) can go and it stays on :17 and :19; planted fault PS-11 (both lines gone); measured: under PS-11 the case was green (runs/plant/PS-11-disposable-subagent-rule-gone.xml) | DEC-032, CAP-16 | revise: read the statement itself (its phrase or its own line), not a word anywhere in the skill | W2-11 (holds the kernel skills); Rewrite-Reason: the check finds a word that stays when the rule goes | 0.0 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_says_only_the_validated_bundle_returns` | weak | checks 'bundle' and 'return'; 'only' and 'validated', the claim, are not read. With both lines that state the rule removed (the planted PS-11) it went red, because the word 'bundle' went with them (runs/plant/PS-11-disposable-subagent-rule-gone.xml); a line that keeps 'bundle' and drops 'only' or 'validated' would leave it green | CAP-56.a | revise: the 'only the validated bundle' statement | with the case above | 0.0 |
| `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_allows_not_applicable_is_present` | duplicate | covered by test_allows_not_applicable_value_is_true | DEC-447 | keep (cost nil) | — | 0.0 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_at_least_one_declaration_exists` | duplicate | the fixture already fails when there is none (conftest.py:75-79) | CAP-38.b | keep (cost nil) | — | 0.0 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_at_least_one_declaration_exists` | duplicate | the fixture already fails when there is none (conftest.py:62-66) | CAP-38.b | keep (cost nil) | — | 0.0 |

**W1-38**: W1-38 (DAEO-3ef2)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_38_rulesync.py::TestToolAbsentOrHanging::test_timeout_handling` | weak | asserts only returncode != 0 (test_w1_38_rulesync.py:806): an uncaught TimeoutExpired also exits 1 at 10 s, though its docstring promises no traceback (l.792-793); planted fault P38-1 (the timeout no longer caught, portability.py:68); it also uses 11.3 to 12.6 s of its 15 s; measured: under P38-1 the case was green (runs/plant/P38-1-timeout-not-caught.xml) | DEC-425 | revise: no traceback and a RULESYNC_FAILED 'no answer' finding | W2-57 (its rulesync-probe item, DEC-892); Rewrite-Reason: exit code alone | 11.3 |
| `test_w1_38_heldout_step.py::TestProjectWithoutAHeldOutFile::test_generated_settings_are_green` | duplicate | the same input, command and verdict as the direct half of test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project (README l.599-601 cites both); only its absence assertion is its own; it runs the real probe (exposed to DEC-871's cause) | DEC-641 | keep (1.9 s); after W2-57's probe fix it is a cheap duplicate; a test designer may fold its absence assertion into the other case later | — | 1.9 |
| `test_w1_38_heldout_step.py::TestStepRepeated::test_project_is_still_green_after_the_second_run` | duplicate | with the previous case's byte-identical settings, its input equals test_generated_then_the_step_is_green's, through the same command; it runs the real probe | DEC-641 | keep (1.9 s); after W2-57's probe fix it is a cheap duplicate; no retirement proposed | — | 1.9 |
| `test_w1_38_test_folder_rule.py::TestALaunchedSessionInAProjectMadeFromTheTemplate::test_no_settings_of_a_launched_test_designer_close_the_folder` | duplicate | the conjunction of the any-list case (the same generated settings) and the first assertion of test_the_launchers_settings_leave_the_folder_to_the_test_designer (the same built settings) | DEC-664 | keep (cheap) | — | 1.2 |
| `test_w1_38_test_folder_rule.py::TestTheRuleIsGone::test_the_generated_settings_hold_no_deny_rule_on_the_acceptance_test_folder` | duplicate | subsumed by test_the_generated_settings_hold_no_rule_of_a_write_tool_on_the_folder_in_any_list (Edit deny is one of every write tool in every list, on the same generated settings) | DEC-664 | keep (shares the generated project; cheap) | — | 2.7 |

**W1-39**: W1-39 (DAEO-5ylr)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured` | outdated | deletes both files from an installed project and expects 'unmeasured', exit 0 (l.281-282); DEC-761 item 1 (register line 8346, owner) orders its rewrite with W2-16 (W2-H029: an installed kernel with neither file fails); the rewrite exists only on unmerged w2/W2-16 (adbeea77, with its Rewrite-Reason) | DEC-761 item 1, W2-H029 | merge adbeea77 with W2-16 | W2-16 (already written there) | 3.0 |
| `test_w1_39_copy.py::test_copy_installs_the_hooks_and_keeps_them_executable` | weak | its executable half runs only if the template hook is executable (l.43-44), and all six hooks are mode 100644 in git and in the tree (git ls-files -s), so 'keeps them executable' can never fail; the installs half is sound | W1-39 KPI S1, CAP-44.a | revise: compare the modes, or drop the clause | a small test-revision ticket for W1-39; Rewrite-Reason: no hook is executable in the template | 0.0 |
| `test_w1_39_copy.py::test_copy_writes_the_lock_where_the_product_layout_places_it` | duplicate | subsumed by test_the_manifest_lists_every_installed_kernel_file_with_its_sha256 (the same lock, read as a map) | CAP-02.a | keep (cheap) | — | 0.0 |

**W1-41**: W1-41 (DAEO-cdoi)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_41_dev_tier.py::test_b_devs_legacy_rule_files_are_retired_and_everything_else_is_kept` | weak | dev_tier.py:62 holds for any edit of each rule file and :63 for any file under .rulesync/, even one already tracked; the imported text is never checked | W1-41 KPI S3, F3; CAP-42.a | revise: the imported text under .rulesync/ and each rule file gone | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: the retirement is not read | 0.0 |
| `test_w1_41_legacy.py::test_a_chat_database_that_cannot_be_read_is_not_retired` | weak | the same: the dirty-tree refusal comes first | DEC-449 | revise as above | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: as above | 18.7 |
| `test_w1_41_legacy.py::test_a_legacy_rule_file_that_cannot_be_read_is_not_retired` | weak | git shows the chmod-0 file as modified, so the clean-tree refusal (src/gov/adopt/project.py:86-95) comes before retire()'s read (legacy.py:214-219); the readability rule it names is never reached; the suite's README says so itself: 'the refusal may be the dirty tree's; the case holds only that the file is named and not retired' (README:717-719) | DEC-449 | revise: commit the unreadable state or make the file unreadable another way | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: the refusal comes from the dirty tree | 17.2 |
| `test_w1_41_legacy.py::test_the_dependency_proof_is_recorded` | weak | asserts citers [] and that the proof's JSON contains 'record' and 'rule' (legacy.py:231-233); the key names records_read and rules_read (legacy.py:158) satisfy it with empty lists | W1-41 KPI S5; DEC-449 | revise: the records and rules read are the project's | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: key names satisfy it | 0.0 |
| `test_w1_41_path_map.py::test_the_plan_rewrites_or_flags_every_importer_reference_and_consumer` | weak | checks the importer and the citing record (path_map.py:169-176) but never the consumer its name claims; dropping consumers at stages.py:294-296 passes | W1-41 KPI S4; P-7 | revise: the consumer too | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: the consumer is not read | 15.2 |
| `test_w1_41_unknown.py::test_an_unknown_artefact_blocks_retirement_too` | weak | A8 refuses first for the missing A6 record (src/gov/adopt/project.py:150-158), so A8's own guard (legacy.py:207, guard(run): the A5 verdict unchanged, the plan the audited path map's, no unknown artefact, stages.py:347-361) is reached by no case: under the planted P41-c (that call removed) all 93 cases of W1-41's unknown and legacy files and unit/adopt stayed green (runs/plant/P41-c-a8-guard-gone.xml); the guard's other two refusals are tested at A6 only (test_adopt.py:226, 258) | W1-41 KPI F4; CAP-06.c | revise: a project whose A6 passed, then an unknown artefact (and a changed verdict) before A8 | a small test-revision ticket for W1-41 (or W2-52, which reuses w1_41_support); Rewrite-Reason: A8's guard is never reached | 1.2 |
| `test_w1_41_legacy.py::test_the_two_role_sections_of_agents_md_are_both_imported` | duplicate | the same fixture, phrases and helper as the agents-md-roles row of test_each_kind_of_legacy_rule_file_is_imported_into_rulesync (legacy.py:84-86 vs 68-75) | W1-41 KPI S3 | keep (the shared fixture makes it cheap) | — | 0.1 |
| `test_w1_41_path_map.py::test_a_native_package_layout_is_kept_where_nothing_else_is_proposed` | duplicate | a subset of test_every_artefact_has_exactly_one_of_the_eight_actions (same fixture, proposal and stage; path_map.py:69-72 vs 308-312); KEEP is the default for any path not named | W1-41 KPI S7; CAP-44.j | keep or merge (CLI x4) | — | 0.7 |

**W1-44**: W1-44 (DAEO-wqd6)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w1_44_lessons.py::test_retrieve_returns_lessons_for_ticket_in_scope` | weak | the lessons sit in an embedded namespace (lessons.py:93-96) and the semantic route returns its top 30 with no threshold (semantic.py:49, 311): five lessons of about 1,700 tokens in all fit the 6,000-token budget (retrieve.py:33, 148-150) for any query, so the ticket's scope may not be what puts them in; planted fault P44-a (the ticket ignored); measured: under P44-a the case was green (runs/plant/P44-a-ticket-ignored.xml) | KPI S2; DEC-424 (line 4568), CAP-14 | revise: a lesson outside the ticket's scope that must not come ahead, and the order of the evidence | a small test-revision ticket for W1-44; Rewrite-Reason: the bundle holds every lesson for any query | 1.1 |

**W2-02**: W2-02 (DAEO-zflj)

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_w2_02_failure.py::test_a_record_with_an_unknown_type_is_still_refused` | outdated | accepts SCHEMA_UNKNOWN_TYPE or SCHEMA_INVALID_TYPE (failure.py:54-55), the open package P-4 at writing; DEC-746 item 6 (line 8091) fixed SCHEMA_UNKNOWN_TYPE, and W1-30's test_w1_30_r15_record_types.py::test_a_type_nobody_knows_is_still_an_unknown_type pins it; planted fault P02-2 (the code changed) leaves this case green; measured: under P02-2 the case was green (runs/plant/P02-2-unknown-type-code-changed.xml) | DEC-746 item 6 | revise: pin SCHEMA_UNKNOWN_TYPE (no retirement proposed; W1-30's case holds the code too) | W2-64 (record types); Rewrite-Reason: DEC-746 item 6 | 0.1 |
| `test_w2_02_record_types.py::test_one_kernel_schema_is_a_decision_entry_with_id_status_owner_date_and_its_own_span` | outdated | requires a kernel schema with a constant type and required owner and date (record_types.py:101, 108, 121), which register-entry.schema.json gives today (required id, type, status, owner, date, span; type 'register-entry'), so it passes; DEC-755 item 5 (2026-10-17, the day after the schema): a register entry's type stays 'decision' and owner and date are not required, and aligning register-entry.schema.json is a product-spec row; no such row exists in docs/plan (searched), and no code reads that schema (schema.py:33); the alignment DEC-755 orders turns this case red | DEC-755 item 5 | revise with the schema's alignment | the missing product-spec row (finding 7); Rewrite-Reason: DEC-755 item 5 | 0.0 |
| `test_w2_02_unmeasured.py::test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green` | weak | its 'names the type' half (unmeasured.py:44-45; README:94) is met by the record's own path or the schema file's name in the message (schema.py:230-231: docs/research/…, research.schema.json; docs/close/…), so an unmeasured finding without its type passes; planted fault PL202-1 (the type dropped from the finding), PL202-2 (the word 'unmeasured' dropped) the control; measured: under PL202-1 the case was green (runs/plant/PL202-1-unmeasured-without-type.xml); measured: under the control PL202-2 the case was red (runs/plant/PL202-2-control-not-said-unmeasured.xml) | S3 [W2-M260, W2-L177] | revise: require the finding's type field, or a record whose path does not hold its type's name | W2-67, or a small test-revision ticket for W2-02; Rewrite-Reason: the type's name is in the record's own path | 0.1 |
| `test_w2_02_failure.py::test_a_record_whose_type_is_missing_or_no_text_is_still_schema_invalid_type[missing]` | duplicate | a record outside docs/audit/ with no type is SCHEMA_INVALID_TYPE (failure.py:62-76), as tests/acceptance/W2-54/test_w2_54_audit_report.py::test_a_record_outside_the_audit_folder_that_states_no_type_still_fails[docs/notes/report.md] (:190-199), through the same command | F; DEC-626 | keep (cheap; no retirement proposed); a test designer may fold it under W2-67 | — | 0.1 |
| `test_w2_02_failure.py::test_an_audit_report_missing_a_field_of_dec_441_is_refused_on_that_field` | duplicate | the same command and input class (a typeless report under docs/audit/ lacking one of DEC-441's three fields; failure.py:24-33) as tests/acceptance/W2-54/test_w2_54_audit_report.py::test_an_audit_report_lacking_a_required_field_fails_naming_it[folder-*] (:202-221), which also requires that no other field is named | F [W2-M138]; DEC-441, DEC-446, DEC-626 | keep (cheap; no retirement proposed); a test designer may fold it under W2-67 | — | 0.2 |
| `test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository` | duplicate | the declared core-schema in the repository root, no finding and exit 0 (green_here.py:62-66), as tests/acceptance/W2-54/test_w2_54_audit_report.py::test_core_schema_is_green_on_this_repository_with_w1_43_untouched (:224-232) and W2-54's test_gov_check_gives_core_schema_green_here (test_w2_54_green_here.py:31-38); record-reading: a malformed record committed, or an untracked one under docs/ or .tickets/, turns the three red together, so the pair costs one refused close, not two | S2 [W2-L243] | keep (cheap; no retirement proposed); in the record-reading set (finding 6) | — | 0.0 |
| `test_w2_02_green_here.py::test_core_schema_reads_the_w1_43_exit_audit_report_as_valid_here` | duplicate | reads the same core-schema output of the repository root as test_core_schema_is_green_on_this_repository, which asserts no finding at all | W2-02 KPI S2 | keep (core-schema once, cheap) | — | 0.8 |
| `test_w2_02_green_here.py::test_the_a5_adoption_verdict_still_validates_here` | duplicate | covered by test_core_schema_is_green_on_this_repository on the same output | W2-02 KPI S2, W2-M317 | keep (cheap) | — | 0.0 |
| `test_w2_02_record_types.py::test_an_audit_report_in_dec_441_form_passes_core_schema` | duplicate | a typeless DEC-441 report under docs/audit/wave-9/ gets no finding and exit 0 (record_types.py:32-40), as tests/acceptance/W2-54/test_w2_54_audit_report.py::test_a_record_in_the_audit_folder_that_states_no_type_is_held_as_an_audit_report[docs/audit/wave-9/wave-9-exit-audit.md] (:118-126) | S1 [AR-3, W2-M316]; DEC-441, DEC-626 | keep (cheap; no retirement proposed); a test designer may fold it under W2-67 | — | 0.1 |
| `test_w2_02_wbs_grammar.py::test_the_wbs_id_grammar_accepts_one_lower_case_letter_suffix` | duplicate | [W2-15a] is held the same way by tests/unit/check/test_schema_record_types.py::test_the_wbs_id_grammar_is_dec_730s (same file, same re.search) | DEC-730 | keep (cost nil) | — | 0.0 |

**unit/adopt**: builder tests of W1-41

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_adopt.py::test_a_move_out_of_a_native_layout_needs_both_grounds` | weak | tests _native only (test_adopt.py:315-320) and never reaches the both-grounds check (stages.py:185-188): under the planted PU-c (any one ground enough) it stayed green, while W1-41's test_a_justification_that_states_only_one_of_the_two_grounds_is_refused went red in both its cases (runs/plant/PU-c-one-ground-enough.xml): the rule is held there | CAP-44.j | revise: call the classification with one ground, or retire it as covered (a test designer's call) | with the W1-41 revision | 0.0 |

**unit/doctor**: builder tests of W1-27

| Test | Verdict | Evidence | Rests on | Proposed change | Carrier | Cost (s) |
|---|---|---|---|---|---|---|
| `test_doctor.py::test_check_isolation` | weak | only the absent-folder branch; the comparison (command.py:642-650) is held by no case in either suite; planted fault P27-9; measured: under P27-9 the case was green (runs/plant/P27-9-isolation-constant.xml) | DEC-425 | revise: both outcomes | W2-67 (test hygiene, DEC-889 item 7), or a small test-revision ticket for W1-27; Rewrite-Reason: the assertion matches a key name that doctor always emits | 0.0 |
| `test_doctor.py::test_match_pattern` | weak | the fnmatch line (command.py:529) is held only by positive '*' cases; fnmatch lets '*' cross '/', unlike the path-map language, so the real map's root-files ['*'] classifies every path; planted fault P27-8 (every pattern matches); measured: under P27-8 the case was green (runs/plant/P27-8-pattern-always-matches.xml) | CAP-06.a, DEC-225 | revise with the matcher fix (finding 3) | W2-22 (gov doctor green, src/gov/doctor/**); Rewrite-Reason: the matcher is not DEC-225's language | 0.0 |
| `test_doctor.py::TestIsHistorical::test_old_cli_root` | duplicate | the same branch and shape as test_old_cli_tree (test_doctor.py:263-267) | DEC-456 | keep (cost nil) | — | 0.0 |

### 2.3 Every test whose verdict is "valid and needed"

One row per function, by suite: what it holds (from the first-pass read, shortened) and the decision or Contract item it rests on. Each was read by a helper session and, where flagged, by me; 54 were drawn at random and read again by me (53 agreed; the 54th is decided by planted faults); one function, W1-33's test_a_definition_without_one_required_field_is_found, had no first-pass line and was read by me alone.


**W1-06**: W1-06 (DAEO-ipqy); 37 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_06_approvals.py::test_every_approving_decision_is_in_the_register` | 1 | Every approved_by id is a `### DEC-nnn —` heading of the register. | KPI F1; DEC-083, DEC-197 |
| `test_w1_06_approvals.py::test_every_entry_names_one_decision_as_its_approval` | 1 | Every registry entry's approved_by is exactly one DEC-nnn id. | KPI F1; CAP-25.a; DEC-083, DEC-121, DEC-197 |
| `test_w1_06_ccusage.py::test_the_installed_ccusage_is_the_pinned_version` | 1 | The installed ccusage package.json version equals the registry's version. | KPI S1; DEC-192 |
| `test_w1_06_digests.py::test_a_single_file_tool_is_recorded_with_the_sha256_of_its_binary` | 7 | The registry sha256 equals the binary's own for gitleaks, tk, codebase-memory-mcp, rulesync, lefthook, uv and Node 22. | KPI S2; DEC-196 (reading 22), DEC-195 |
| `test_w1_06_digests.py::test_gitleaks_is_recorded_at_8_30_1` | 1 | One gitleaks entry, at version 8.30.1. | KPI S2; DEC-195 |
| `test_w1_06_digests.py::test_the_gitleaks_on_this_machine_is_the_pinned_version` | 1 | gitleaks version` on PATH prints the pinned version. | KPI S2; DEC-195 |
| `test_w1_06_install_approvals.py::test_a_stack_pin_cites_dec_074` | 10 | Each stack pin's approved_by is exactly DEC-074. | DEC-197, DEC-074 |
| `test_w1_06_install_approvals.py::test_an_install_of_this_ticket_cites_a_decision_that_names_the_tool_and_its_version` | 2 | The cited decision's own text names the tool and the registry's exact version. | KPI S1, F1; DEC-197 (readings 15, 16) |
| `test_w1_06_install_approvals.py::test_an_install_of_this_ticket_has_its_own_register_entry` | 2 | No other entry cites the decision that approves ccusage or Superpowers. | DEC-197 |
| `test_w1_06_install_approvals.py::test_an_install_of_this_ticket_is_not_dated_before_its_approval` | 2 | each install dated on or after its approval (install_approvals.py:94-103); its [ccusage] set is repeated by … | DEC-083 |
| `test_w1_06_install_approvals.py::test_an_install_of_this_ticket_is_recorded_at_the_approved_version` | 2 | the owner's approved versions (install_approvals.py:54-58); its [superpowers] set is repeated by … | KPI S1, F1; DEC-192, DEC-193 |
| `test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` | 1 | For the 15 non-stack entries, the cited decision's own text names the entry as a word. | KPI F1; DEC-197 (reading 20) |
| `test_w1_06_install_approvals.py::test_pyyaml_cites_dec_191` | 1 | PyYAML's approved_by is DEC-191. | DEC-197, DEC-191 |
| `test_w1_06_install_approvals.py::test_the_approval_of_an_install_of_this_ticket_is_made_under_dec_083` | 2 | The cited decision is "ACCEPTED (owner" and its status line names DEC-083. | KPI S1; DEC-083, DEC-197 |
| `test_w1_06_install_approvals.py::test_the_superpowers_install_command_fetches_the_approved_source` | 1 | The Superpowers install names github.com/obra/superpowers and v6.4.2. | DEC-193 (reading 19) |
| `test_w1_06_pins.py::test_a_dec_074_pin_is_recorded_at_its_pinned_version` | 10 | Each ADR-0002 §2 pin is one entry at its exact version. | KPI S2; CAP-25.a; DEC-074, DEC-195 |
| `test_w1_06_pins.py::test_a_dec_074_pin_is_recorded_with_the_sha256_of_the_stack_table` | 10 | Each pin's sha256 is 64 hex and begins and ends as the ADR table abbreviates it. | KPI S2; CAP-25.a; DEC-195, DEC-200 |
| `test_w1_06_pins.py::test_pyyaml_is_recorded_at_6_0_1` | 1 | One PyYAML entry, at 6.0.1. | DEC-191 |
| `test_w1_06_registry.py::test_each_tool_is_recorded_once` | 1 | No entry name appears twice (case-insensitive). | CAP-25.a (reading 5) |
| `test_w1_06_registry.py::test_every_date_is_a_calendar_date` | 1 | Each date begins with a valid YYYY-MM-DD. | CAP-25.a |
| `test_w1_06_registry.py::test_every_entry_states_all_seven_facts` | 1 | Each entry's seven facts are non-blank strings. | CAP-25.a; DEC-083 (reading 8) |
| `test_w1_06_registry.py::test_every_sha256_is_a_sha256_digest` | 1 | Each sha256 is 64 hexadecimal characters. | CAP-25.a; DEC-196 |
| `test_w1_06_registry.py::test_no_uninstall_command_is_the_install_command` | 1 | No entry's uninstall equals its install. | KPI F2 (reading 11) |
| `test_w1_06_registry.py::test_the_registry_is_valid_against_the_committed_schema` | 1 | The parsed registry has no error under the committed schema. | CAP-25.a; DEC-121, DEC-127 |
| `test_w1_06_registry.py::test_the_schema_refuses_this_registry_once_an_entry_loses_its_uninstall_command` | 1 | Dropping uninstall from any one entry makes the committed schema report an error. | KPI F2; DEC-121 |
| `test_w1_06_vendor.py::test_a_skill_folder_is_there_with_its_skill_md` | 3 | Each of the three skills has exactly one non-empty SKILL.md in its folder. | KPI S2; DEC-194, DEC-074 Q5 |
| `test_w1_06_vendor.py::test_a_skill_md_declares_the_skill_of_its_folder` | 3 | Each SKILL.md's frontmatter `name` equals its folder name. | DEC-194 (reading 24) |
| `test_w1_06_vendor.py::test_no_hook_is_there` | 1 | No hooks folder, hooks.json or session-start file. | DEC-194 (reading 26) |
| `test_w1_06_vendor.py::test_no_other_skill_is_there` | 1 | No other SKILL.md, and no subagent-driven-development component. | DEC-194, DEC-076 |
| `test_w1_06_vendor.py::test_no_plugin_is_there` | 1 | No plugin.json, marketplace.json or folder named with "plugin". | DEC-194 (reading 26) |
| `test_w1_06_vendor.py::test_nothing_but_the_three_skills_and_the_licence_is_there` | 1 | Every file is in one of the three skill folders or is the licence. | DEC-194 (reading 25) |
| `test_w1_06_vendor.py::test_the_excluded_parts_are_nowhere_in_the_repository` | 1 | No tracked path has a subagent-driven-development or .claude-plugin component. | DEC-194 |
| `test_w1_06_vendor.py::test_the_scratch_clone_is_deleted` | 1 | .gov-runtime/scratch/orchestrator/vendor-src/superpowers/ does not exist. | DEC-194, DEC-193 (reading 28) |
| `test_w1_06_vendor.py::test_the_upstream_licence_is_there` | 1 | A licence file outside the skill folders exists and contains "copyright". | DEC-194 |
| `test_w1_06_vendor.py::test_the_vendor_folder_is_committed` | 1 | Every file under the vendor folder is tracked, and git status shows no change there. | KPI S2; DEC-194 (reading 27) |
| `test_w1_06_vendor_digest.py::test_the_digest_rule_gives_the_value_worked_out_by_hand` | 1 | an oracle check: the suite's folder_digest against a value worked out by hand (vendor_digest.py:52-53), so the digest … | DEC-199 (readings 29-34) |
| `test_w1_06_vendor_digest.py::test_the_superpowers_sha256_is_the_digest_of_the_committed_vendor_folder` | 1 | Superpowers' sha256 equals DEC-199's digest of the files HEAD holds under the vendor folder. | KPI S2; DEC-199 |

**W1-07**: W1-07 (DAEO-drvn); 38 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields` | 2 | An added, committed declaration is listed with id, family, tier, severity and command unchanged | S4; DEC-186 |
| `test_w1_07_check_declarations.py::test_an_uncommitted_declaration_is_listed_and_left_alone` | 1 | An uncommitted declaration is listed; porcelain unchanged | S4, S2; DEC-186 |
| `test_w1_07_check_declarations.py::test_every_declaration_in_the_kernel_template_is_listed` | 1 | Every id the regex finds in the copy's template checks folder is listed with all five fields | S4; DEC-186, DEC-579 (L6232) |
| `test_w1_07_check_declarations.py::test_listing_does_not_run_a_check` | 1 | A declared `touch <marker>` command is not run by `--list | S4, F1; DEC-186 |
| `test_w1_07_check_declarations.py::test_the_list_follows_the_declaration_files` | 1 | Two added declarations appear; one removed disappears, the other stays | S4; DEC-186 |
| `test_w1_07_config.py::test_a_missing_path_map_is_not_an_error` | 13 | Without path-map.yaml each invocation prints a valid envelope whose error code is not CONFIG_INVALID | S3a, S1; DEC-185 (L1724) |
| `test_w1_07_config.py::test_an_invalid_path_map_gives_config_invalid_on_every_command` | 39 | Not-YAML, list or scalar path map: every invocation answers CONFIG_INVALID, exit 1, naming path-map.yaml | S3a; DEC-185, DEC-189 (L1760) |
| `test_w1_07_config.py::test_an_invalid_path_map_gives_exit_code_1_without_json` | 1 | Plain status with a list path map exits 1 and names the file | S3a; DEC-185 |
| `test_w1_07_config.py::test_repairing_the_path_map_clears_the_error` | 1 | A broken file gives CONFIG_INVALID; after deleting it status is ok | S3a; DEC-185 |
| `test_w1_07_config.py::test_root_decides_which_path_map_is_loaded` | 1 | --root` from elsewhere loads that project's invalid map: CONFIG_INVALID naming the file | S3a, S1; DEC-185 |
| `test_w1_07_config.py::test_status_succeeds_without_a_governance_project_folder` | 1 | Status after removing governance/project/: ok true, exit 0 | S3a; DEC-185 |
| `test_w1_07_config.py::test_status_succeeds_without_a_path_map` | 1 | Status without a path map: ok true, exit 0 | S3a; DEC-185 |
| `test_w1_07_config_details.py::test_a_file_level_error_carries_file_and_key_in_details` | 3 | details is an object holding file (ending path-map.yaml) and key, for not-YAML, list and scalar | S3a; DEC-189 |
| `test_w1_07_config_details.py::test_a_missing_namespaces_names_the_key` | 3 | The four other keys without namespaces give details.key == "namespaces" | S3a; DEC-189, DEC-228 |
| `test_w1_07_config_details.py::test_a_namespace_that_is_not_a_map_is_invalid` | 1 | namespaces: {core: 42}: CONFIG_INVALID, with a key that mentions namespaces | S3a; DEC-189 |
| `test_w1_07_config_details.py::test_a_valid_path_map_is_not_reported_as_invalid_by_any_command` | 13 | With a valid path map no invocation answers CONFIG_INVALID; each prints a valid envelope | S3a, S1; DEC-189, DEC-228, DEC-440 |
| `test_w1_07_config_details.py::test_a_valid_path_map_loads` | 1 | A full W1-08 path map loads: status ok, exit 0 | S3a; DEC-189, DEC-228 |
| `test_w1_07_config_details.py::test_details_file_names_the_path_map_of_the_root_given` | 1 | --root` from elsewhere with namespaces: 42 gives details.key == "namespaces" | S3a; DEC-189, DEC-228 (L2139) |
| `test_w1_07_config_details.py::test_namespaces_of_the_wrong_type_names_the_key` | 9 | the stricter of lens H's same-name pair: key == 'namespaces' for three wrong types on status, doctor and check --list … | S3a; DEC-189, DEC-228 |
| `test_w1_07_config_details.py::test_repairing_the_key_clears_the_error` | 1 | namespaces: 42 is refused; the valid file then loads | S3a; DEC-189, DEC-228 |
| `test_w1_07_envelope.py::test_an_unknown_option_is_a_usage_error` | 1 | exit 2 for an unknown option (envelope.py:67-69); its envelope branch (:70-72) never runs, because argparse writes the … | S1; reading 8 |
| `test_w1_07_envelope.py::test_every_command_returns_the_envelope` | 13 | API-0002's envelope on all 13 invocations (envelope.py:20-24); its [doctor] case is decided from the runs (2.1); … | S1, F2; DEC-186, DEC-190 (L1769), DEC-391 … |
| `test_w1_07_envelope.py::test_root_names_the_project_from_another_directory` | 1 | status --root <copy>` run from elsewhere: valid envelope, ok true | S1; reading 3 |
| `test_w1_07_envelope.py::test_status_succeeds_with_exit_code_0` | 1 | gov status --json`: valid envelope, ok true, exit 0, no error | S1; DEC-186 |
| `test_w1_07_envelope.py::test_the_envelope_carries_the_session_given` | 1 | --session <id>` becomes the envelope's session on status | S1; reading 3 |
| `test_w1_07_envelope.py::test_the_exit_code_is_the_same_without_json` | 3 | pins the plain form's exit codes to API-0002's, which are the --json form's (0, 3, 2; envelope.py:75-79); [check] was … | S1; DEC-186; W1-26 (commit 0ebaea14 set check to … |
| `test_w1_07_read_act.py::test_a_command_refused_for_invalid_configuration_writes_nothing` | 13 | With an invalid path map committed, each invocation leaves porcelain, refs, files, HOME and elsewhere unchanged | F1, S3a; DEC-185 |
| `test_w1_07_read_act.py::test_a_read_command_changes_no_file_and_no_ref` | 8 | Porcelain, HEAD and refs, every file hash, HOME and an unrelated folder unchanged by each read command | S2, F1; DEC-187 |
| `test_w1_07_read_act.py::test_a_read_command_leaves_a_dev_tier_clone_clean` | 8 | On a clone of the a-dev tier each read command leaves porcelain empty and state unchanged | S2 [CAP-27.a] |
| `test_w1_07_read_act.py::test_a_read_command_leaves_uncommitted_work_as_it_was` | 8 | Same unchanged state with a modified tracked file and an untracked file present | S2 |
| `test_w1_07_read_act.py::test_a_read_command_with_root_writes_neither_in_the_project_nor_where_it_runs` | 1 | status --root` run elsewhere changes nothing in the project, HOME or elsewhere | S2, F1 |
| `test_w1_07_read_act.py::test_no_command_writes_outside_its_act_paths` | 14 | Every invocation and --help changes nothing outside .gov-runtime; HOME changes only by pause's freeze mirror | F1; DEC-187, DEC-429 (L4633), DEC-440 |
| `test_w1_07_recorded_commands.py::test_a_recorded_gov_command_is_offered_and_answers_its_help` | 3 | gov --help` offers the command; `gov <name> --help` exits 0 and names it | DEC-542, DEC-569 (L6145) |
| `test_w1_07_recorded_commands.py::test_lock_is_recorded_as_the_module_command_and_is_no_gov_command` | 1 | No lock in help; `gov lock` exits 2; `python3 -m gov.lock` outside a project exits 1, names framework.lock, writes … | DEC-542, DEC-499 (L5476) |
| `test_w1_07_recorded_commands.py::test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve` | 1 | checks the suite's own lists against DEC-542 (recorded_commands.py:44-47): an oracle check, the product half is in the … | DEC-542, DEC-546 |
| `test_w1_07_registry.py::test_a_name_outside_the_registry_is_not_answered_as_not_implemented` | 1 | gov no-such-command --json` exits 2 and stdout has no NOT_IMPLEMENTED | S5 |
| `test_w1_07_registry.py::test_a_reserved_command_not_yet_built_returns_not_implemented` | 1 | NOT_BUILT resolves to ('adopt',) (w1_07_support.py:58-111); W1-41 built only `gov adopt --lite`, and the bare form … | S5 [CAP-28.b]; DEC-190 |
| `test_w1_07_registry.py::test_closure_without_its_arguments_is_a_usage_error` | 1 | gov closure --json` exits 2 and prints no NOT_IMPLEMENTED | S5; DEC-391, DEC-190 |

**W1-08**: W1-08 (DAEO-uudf); 82 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_08_floor.py::test_a_capability_is_a_closed_map_with_a_boolean_enabled` | 2 | enabled` true and false accepted; refused: no `enabled`, a string, 1, null, an unknown key, a bare boolean | S5; DEC-251 |
| `test_w1_08_floor.py::test_a_capability_outside_the_two_is_refused` | 1 | A third capability that carries a known capability's value is refused | S5; DEC-238 |
| `test_w1_08_floor.py::test_a_path_map_without_one_of_the_thirteen_policies_is_refused` | 1 | The schema refuses the live map without each of the 13 policies | S5; DEC-230, DEC-238 |
| `test_w1_08_floor.py::test_a_path_map_without_one_of_the_twenty_two_systems_is_refused` | 1 | The schema refuses the live map without each of the 22 systems | S5 [CAP-54.b]; DEC-230 |
| `test_w1_08_floor.py::test_a_path_map_without_one_of_the_two_capabilities_is_refused` | 2 | The map without code_intelligence, or without research_corpus, is refused | S5; DEC-251 |
| `test_w1_08_floor.py::test_a_path_map_without_the_floor_key_is_refused` | 3 | The live path map has capabilities, policies and systems; the schema refuses the map without each | S5 [CAP-06.e]; DEC-224, DEC-230 |
| `test_w1_08_floor.py::test_a_policy_value_that_is_not_a_strength_is_refused` | 2 | off` and null are refused for security and for archive | S5; DEC-230 |
| `test_w1_08_floor.py::test_a_strength_below_the_kernel_minimum_is_refused` | 9 | For each policy whose minimum is above informational, each weaker strength is refused | S5; DEC-230, DEC-238 |
| `test_w1_08_floor.py::test_a_system_is_implemented_or_minimal_with_a_where` | 1 | implemented and minimal are accepted with `where`; refused without `where` and with an empty one | S5 [CAP-54.b]; DEC-230 |
| `test_w1_08_floor.py::test_a_system_without_one_of_the_three_statuses_is_refused` | 2 | Status `planned`, or no status, is refused | S5; DEC-230 |
| `test_w1_08_floor.py::test_an_absent_system_gives_its_reason` | 1 | An absent system is accepted with a `reason` and refused without one | S5; DEC-230 |
| `test_w1_08_floor.py::test_enabled_code_intelligence_lists_its_languages` | 1 | With code intelligence enabled, two languages are accepted; none, an empty list, a string, a number and null are refused | S5; DEC-251 |
| `test_w1_08_floor.py::test_every_strength_at_or_above_the_kernel_minimum_is_accepted` | 1 | Accepted: every policy at its minimum, every policy at hard-block, every policy one step above | S5; DEC-238 |
| `test_w1_08_floor.py::test_the_path_map_gives_each_of_the_thirteen_policies_a_strength_at_or_above_the_kernel_minimum` | 1 | Each of the 13 live policies has a strength at or above the minimum in the test's own table | S5; DEC-230, DEC-238 |
| `test_w1_08_floor.py::test_the_path_map_identifies_each_of_the_twenty_two_constitutional_systems` | 1 | The live map has all 22 systems, each with a valid status and its `where` or `reason | S5 [CAP-54.b]; DEC-230 |
| `test_w1_08_floor.py::test_the_path_map_names_no_capability_outside_the_two` | 1 | The live capabilities are only code_intelligence and research_corpus | S5; DEC-238 |
| `test_w1_08_floor.py::test_the_where_rule_holds_for_every_system` | 1 | For each of the 22 systems, `minimal` with no `where`, or an empty one, is refused | S5 [CAP-54.b]; DEC-230 |
| `test_w1_08_frontmatter.py::test_a_record_without_a_state_class_is_refused` | 7 | Each record schema refuses its template without state_class | S6; DEC-229 |
| `test_w1_08_frontmatter.py::test_a_record_without_id_type_or_status_is_refused` | 7 | Each schema refuses its template without id, without type, and without status | S3 [CAP-50.a]; DEC-239 |
| `test_w1_08_frontmatter.py::test_no_template_stores_what_gov_derives` | 7 | No template stores content_hash, canonical_path or path | S3 [CAP-50.a]; DEC-239 |
| `test_w1_08_frontmatter.py::test_the_optional_identity_fields_are_defined_and_optional` | 7 | true` is refused in each of the six optional identity fields; the template without them is accepted | S3 [CAP-50.a]; DEC-239 |
| `test_w1_08_frontmatter.py::test_the_shared_definitions_file_holds_the_six_state_classes` | 1 | The shared state_class definition accepts the six and refuses OFFICIAL, an empty string and null | S6; DEC-229 |
| `test_w1_08_frontmatter.py::test_the_six_state_classes_are_accepted_and_no_other` | 7 | Each schema accepts the six classes and refuses OFFICIAL, the lower-case form and null | S6; DEC-229 |
| `test_w1_08_frontmatter.py::test_the_template_records_the_state_class_of_its_record_type` | 7 | Each of the seven templates carries its type's default state_class | S6 [CAP-07.b]; DEC-229 |
| `test_w1_08_id_grammar.py::test_a_lesson_id_is_the_letter_l_and_four_or_more_digits` | 1 | lesson_id accepts L-0074, L-0000 and L-12345, and refuses seven near misses | F2; DEC-252 |
| `test_w1_08_id_grammar.py::test_the_five_id_grammars_are_defined_in_one_file_only` | 1 | No kernel JSON file other than common.schema.json defines any of the five id-grammar names | F2; DEC-227 |
| `test_w1_08_id_grammar.py::test_the_id_of_the_record_is_governed_by_the_shared_grammar` | 7 | Each schema refuses a junk id, and accepts it once the shared grammars are loosened in a copy | F2; DEC-227 |
| `test_w1_08_id_grammar.py::test_the_shared_definition_is_a_grammar` | 5 | Each grammar refuses "", two lines, 42 and a junk string; DAEO-uudf, W1-08 and L-0074 are accepted | F2; DEC-227, DEC-252; DEC-730 |
| `test_w1_08_lesson.py::test_a_lesson_without_the_field_is_refused` | 2 | A lesson without scope, or without severity, is refused | S8 [CAP-41.f]; DEC-168 |
| `test_w1_08_lesson.py::test_a_scope_outside_the_three_is_refused` | 4 | PROJECT, galaxy, null and a two-item list are refused | S7; DEC-226 |
| `test_w1_08_lesson.py::test_a_severity_outside_the_four_is_refused` | 4 | HIGH, catastrophic, 3 and null are refused | S8; DEC-168, DEC-226 |
| `test_w1_08_lesson.py::test_each_scope_is_accepted` | 3 | project, product and framework are each accepted | S7 [CAP-41.c]; DEC-226 |
| `test_w1_08_lesson.py::test_each_severity_is_accepted` | 4 | low, medium, high and critical are each accepted | S8 [CAP-41.f]; DEC-168, DEC-226 |
| `test_w1_08_lesson.py::test_the_lesson_schema_accepts_the_carried_lesson_id` | 1 | The lesson schema accepts id L-0074 and refuses L-074 | S7, S8 [CAP-41.a,c,f]; DEC-252 |
| `test_w1_08_lesson.py::test_the_lesson_template_carries_a_lifecycle_state` | 1 | A template field other than scope or severity holds one of the six lifecycle states | S3 [CAP-41.a]; DEC-239 |
| `test_w1_08_lesson.py::test_the_lesson_template_carries_a_scope_and_a_severity_in_lower_case` | 1 | The template's scope and severity are allowed lower-case values | S7, S8; DEC-226 |
| `test_w1_08_lesson.py::test_the_lesson_template_carries_an_id_of_the_lesson_form` | 1 | Every lesson template's id is `L-` followed by four or more digits | S2a, S7, S8; DEC-252 |
| `test_w1_08_lesson.py::test_the_six_lifecycle_states_are_accepted_and_no_other` | 1 | The lifecycle field takes each of the six states, refuses any other word, and is required | S3 [CAP-41.a] |
| `test_w1_08_path_map.py::test_a_namespace_cannot_be_both_or_neither` | 4 | Refused: both as a list, a joined string, "both", and no class at all | S4 [CAP-03.b] |
| `test_w1_08_path_map.py::test_a_namespace_that_declares_nothing_is_refused` | 2 | An added namespace that is {} or 42 is refused | S3 |
| `test_w1_08_path_map.py::test_a_namespace_whose_paths_are_not_a_list_of_patterns_is_refused` | 3 | paths` left out, 42, or [42] in the first namespace is refused | S2b; DEC-225 |
| `test_w1_08_path_map.py::test_a_namespace_without_the_field_is_refused` | 7 | Removing each of the seven fields from the first namespace makes the schema refuse the map | S3 [CAP-03.c] |
| `test_w1_08_path_map.py::test_a_path_map_that_is_not_a_map_is_refused` | 1 | A list, and the map without namespaces, are refused | S3 |
| `test_w1_08_path_map.py::test_each_memory_class_is_accepted` | 1 | governance and product are each accepted on the first namespace | S4 |
| `test_w1_08_path_map.py::test_every_namespace_is_governance_memory_or_product_data` | 1 | Every live namespace's memory_class is governance or product | S4 [CAP-03.b]; DEC-225 |
| `test_w1_08_path_map.py::test_every_namespace_lists_its_paths` | 1 | Every live namespace has a non-empty list of non-empty pattern strings | S2b; DEC-225 |
| `test_w1_08_path_map.py::test_every_namespace_of_the_path_map_declares_the_field` | 7 | Every live namespace holds a key containing each of the seven KPI words, at any depth | S3 [CAP-03.a, CAP-03.c] |
| `test_w1_08_path_map.py::test_the_gov_cli_loads_the_committed_path_map` | 1 | gov status --json` in a project holding only the live map exits 0 with no CONFIG_INVALID | S2b; DEC-185, DEC-228 |
| `test_w1_08_path_map.py::test_the_path_map_records_its_state_class` | 1 | The live map's state_class is AUTHORITATIVE | S6; DEC-229 |
| `test_w1_08_path_map.py::test_the_path_map_schema_takes_the_six_state_classes_and_no_other` | 1 | The six are accepted; OFFICIAL and a missing state_class are refused | S6; DEC-229 |
| `test_w1_08_path_map.py::test_the_path_map_validates_against_the_path_map_schema` | 1 | The live map, as parsed, validates against path-map.schema.json | S2b; DEC-225, DEC-845 |
| `test_w1_08_path_map.py::test_the_path_map_validates_as_it_is_written` | 1 | The map's YAML text validates as the validator's own reader reads it | S2b |
| `test_w1_08_path_map.py::test_this_repository_has_a_committed_path_map_with_namespaces` | 1 | The live path map has a non-empty namespaces map and is tracked | S2b [CAP-06.a]; DEC-185, DEC-189 |
| `test_w1_08_path_map_tool_keys.py::test_a_path_map_with_all_five_keys_validates` | 1 | The five keys together validate | as above |
| `test_w1_08_path_map_tool_keys.py::test_a_path_map_without_the_optional_keys_validates_as_before` | 1 | The fixture map without the five keys validates | as above |
| `test_w1_08_path_map_tool_keys.py::test_a_top_level_key_the_schema_does_not_know_is_no_finding_as_before` | 1 | An unknown top-level key validates: the top level stays open | as above |
| `test_w1_08_path_map_tool_keys.py::test_an_optional_key_in_a_valid_shape_validates` | 5 | Each valid shape of each key validates | as above |
| `test_w1_08_path_map_tool_keys.py::test_an_optional_key_in_a_wrong_shape_is_refused` | 5 | Each wrong shape of each key is refused, after a valid shape is accepted | as above |
| `test_w1_08_path_map_tool_keys.py::test_no_optional_key_is_required` | 1 | None of the five keys is among the schema's required keys | as above |
| `test_w1_08_path_map_tool_keys.py::test_the_path_map_schema_names_the_optional_key` | 5 | The schema names each of the five tool keys as a top-level property with a description | DEC-554 point 6, DEC-479, DEC-482, DEC-549, … |
| `test_w1_08_probe.py::test_the_kernel_has_one_schema_for_the_probe_record` | 1 | Exactly one kernel schema has "probe" in its name, and it is a JSON object | DEC-565, DEC-569 |
| `test_w1_08_probe.py::test_the_probe_schema_accepts_a_well_formed_record` | 1 | Accepted: the nine-field record, the same with the shared fields, and with the other judgement words | DEC-565, DEC-490 |
| `test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records` | 1 | The frontmatter of every `docs/probes/*/*.md` in the working tree validates | DEC-565, DEC-733 |
| `test_w1_08_probe.py::test_the_probe_schema_is_a_valid_json_schema` | 1 | probe.schema.json passes the metaschema check | DEC-565 |
| `test_w1_08_probe.py::test_the_probe_schema_names_no_path_of_a_project` | 1 | probe.schema.json's text contains no `docs/` and no `.tickets | DEC-565 |
| `test_w1_08_probe.py::test_the_probe_schema_refuses_a_field_of_a_wrong_type_or_value` | 1 | Fifteen single wrong values are each refused | DEC-565, DEC-490 |
| `test_w1_08_probe.py::test_the_probe_schema_refuses_a_record_without_a_required_field` | 1 | Each of the nine required fields, left out, is refused on its own | DEC-565 |
| `test_w1_08_schemas_exist.py::test_a_committed_schema_file_exists_for_the_record_type` | 8 | Exactly one tracked `*.schema.json` per type word, and it is a JSON object | S1 [CAP-31.a, CAP-53.a] |
| `test_w1_08_schemas_exist.py::test_a_committed_shared_definitions_file_exists` | 1 | Exactly one tracked kernel JSON file defines all five id grammars | S1; DEC-227 |
| `test_w1_08_schemas_exist.py::test_each_record_type_has_its_own_schema_file` | 1 | The eight types resolve to eight distinct files | S1 |
| `test_w1_08_schemas_exist.py::test_the_schema_is_a_valid_json_schema` | 8 | Each of the eight schemas passes `--check-metaschema | S1 |
| `test_w1_08_schemas_exist.py::test_the_shared_definitions_file_is_a_valid_json_schema` | 1 | common.schema.json passes the metaschema check | S1; DEC-227 |
| `test_w1_08_templates.py::test_a_committed_template_exists_for_the_record_type` | 7 | Each type has a tracked template with non-empty frontmatter | S2a [CAP-06.a] |
| `test_w1_08_templates.py::test_the_schema_refuses_a_record_that_is_not_a_map` | 7 | Each schema refuses a list in place of a record | S2a |
| `test_w1_08_templates.py::test_the_template_validates_against_its_schema` | 7 | Every template of the type validates against its schema | S2a |
| `test_w1_08_templates.py::test_the_template_validates_as_it_is_written` | 7 | Each template's frontmatter text validates as the validator's YAML reader reads it | S2a |
| `test_w1_08_ticket.py::test_a_ticket_without_kpis_role_and_allowed_paths_is_refused` | 1 | A ticket without all three is refused | F1 |
| `test_w1_08_ticket.py::test_a_ticket_without_the_field_is_refused` | 3 | A ticket without kpis, role or allowed_paths, or with null in its place, is refused | F1 |
| `test_w1_08_ticket.py::test_the_committed_tickets_validate_against_the_ticket_schema` | 1 | The frontmatter of every tracked `.tickets/*.md` validates against ticket.schema.json, in one call | S1; DEC-229 |
| `test_w1_08_ticket.py::test_the_three_profiles_are_accepted_and_no_other` | 1 | LITE, STANDARD and FULL are accepted; MEDIUM, `standard` and "" are refused | S1 [CAP-53.a] |
| `test_w1_08_ticket.py::test_the_ticket_schema_defines_the_field` | 9 | The schema refuses each field set to a value of no plausible kind | S1 [CAP-31.a] |
| `test_w1_08_ticket.py::test_the_ticket_template_carries_the_nine_fields` | 1 | The ticket template has the nine contract fields and a LITE, STANDARD or FULL profile | S1 [CAP-31.a, CAP-53.a] |

**W1-09**: W1-09 (DAEO-topz); 64 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_09_claims.py::test_a_claim_is_a_lock_file_in_the_claims_folder` | 1 | The claim adds exactly .tickets/.claims/<id>, a regular file naming the holder, and nothing else. | KPI S2 [CAP-23.a]; DEC-292 L2906-2907 |
| `test_w1_09_claims.py::test_a_claim_on_a_free_ticket_names_the_ticket_and_its_holder` | 1 | A claim on a free ticket succeeds and returns {"ticket": id, "holder": holder}. | KPI S2 [CAP-23.a]; DEC-291 L2897-2900 |
| `test_w1_09_claims.py::test_a_claim_on_a_ticket_that_does_not_exist_fails_and_leaves_no_lock` | 1 | Claiming an unknown id raises TICKET_NOT_FOUND naming it and writes nothing (an empty claims folder is tolerated). | DEC-291 |
| `test_w1_09_claims.py::test_a_closed_ticket_cannot_be_claimed` | 1 | Claiming a closed ticket raises TICKET_CLOSED naming it and leaves no lock. | DEC-292 L2910 |
| `test_w1_09_claims.py::test_a_failed_claim_leaves_the_first_claim_as_it_was` | 1 | After a refused second claim, the holder and the lock bytes are unchanged. | KPI F1; DEC-292 |
| `test_w1_09_claims.py::test_a_lock_file_that_exists_is_a_held_claim_whatever_it_holds` | 1 | A pre-existing empty lock makes a claim CLAIM_HELD, and the lock is not written into. | KPI F1; DEC-292 L2906 (O_EXCL) |
| `test_w1_09_claims.py::test_a_release_by_another_than_the_holder_fails_and_the_claim_stays` | 1 | A release naming another holder raises CLAIM_NOT_HELD with the real holder; the claim stays. | KPI F1; DEC-292 L2908 |
| `test_w1_09_claims.py::test_a_release_of_a_ticket_nobody_holds_fails` | 1 | Releasing a free ticket raises CLAIM_NOT_HELD. | DEC-291 L2899-2900 |
| `test_w1_09_claims.py::test_a_released_ticket_can_be_claimed_again` | 1 | The holder's release succeeds, removes the lock and clears the holder; another holder can then claim. | KPI S2; DEC-292 L2908 |
| `test_w1_09_claims.py::test_a_second_claim_on_a_held_ticket_fails_with_the_holder_named` | 1 | A second claim raises CLAIM_HELD; details name ticket and holder; the message names the holder. | KPI S2 [CAP-23.a], CAP-23 acceptance; DEC-291, … |
| `test_w1_09_claims.py::test_a_ticket_id_with_a_path_separator_is_no_ticket` | 4 | Ids containing "/" raise TICKET_NOT_FOUND even where a file answers the path; nothing is written in or beside the … | W1-08 ticket id grammar; DEC-291 |
| `test_w1_09_claims.py::test_claims_on_different_tickets_do_not_collide` | 1 | Claims on two tickets both succeed, each with its own holder. | KPI S2; DEC-292 |
| `test_w1_09_claims.py::test_one_holder_may_hold_several_tickets` | 1 | One holder can claim a second ticket. | KPI S2; DEC-292 |
| `test_w1_09_claims.py::test_the_holder_of_a_ticket_is_reported` | 1 | holder() is None before the claim and the claimer after it; another ticket stays None. | KPI S2; DEC-291 |
| `test_w1_09_create.py::test_a_created_ticket_carries_state_class` | 1 | create() runs the project's vendored tk; the new ticket file exists with state_class: AUTHORITATIVE. | DEC-229 L2168, DEC-295 L2928-2931; DAEO-topz KPI … |
| `test_w1_09_decisions.py::test_a_record_of_another_type_that_constrains_a_ticket_does_not_block_it` | 1 | A PROPOSED record of type decision that constrains A leaves A READY. | DEC-308 L3068 |
| `test_w1_09_decisions.py::test_a_ticket_that_depends_on_the_blocked_ticket_waits_for_it_as_for_any_dependency` | 1 | B (which depends on A) gets only DEPENDENCY_OPEN; A gets DECISION_OPEN; C is READY. | KPI S5, CAP-31.c; DEC-308 |
| `test_w1_09_decisions.py::test_a_ticket_waiting_on_an_open_decision_package_is_blocked` | 1 | A PROPOSED decision-package constraining A leaves A not READY, with exactly [DECISION_OPEN]. | KPI S5 [CAP-34.e]; DEC-308 L3068-3069 |
| `test_w1_09_decisions.py::test_a_ticket_waiting_on_two_packages_is_blocked_while_one_is_open` | 1 | One ACCEPTED and one PROPOSED package: A is held by DECISION_OPEN alone. | KPI S5; DEC-308 |
| `test_w1_09_decisions.py::test_an_open_package_that_names_no_ticket_of_the_project_blocks_nothing` | 1 | PROPOSED packages constraining an unknown id, or nothing, hold no ticket. | KPI S5 [CAP-34.e] |
| `test_w1_09_decisions.py::test_the_ticket_is_ready_again_when_the_package_is_answered` | 1 | Moving the package from PROPOSED to ACCEPTED makes A READY with nothing blocked. | KPI S5; DEC-308, DEC-328 L3240 |
| `test_w1_09_decisions.py::test_tickets_that_do_not_depend_on_the_package_stay_ready` | 1 | Only the constrained ticket is held; the two others are READY. | KPI S5 [CAP-34.e]; DEC-308 |
| `test_w1_09_inputs.py::test_a_bad_input_holds_only_the_ticket_that_names_it` | 1 | A gets INPUT_ABSENT and INPUT_SUPERSEDED; B, which names the successor, stays READY. | KPI S4, CAP-34.e; DEC-294 |
| `test_w1_09_inputs.py::test_a_ticket_becomes_not_ready_when_its_input_is_superseded_later` | 1 | A READY ticket stops being READY once a successor of its input is added. | KPI S4; DEC-294 |
| `test_w1_09_inputs.py::test_a_ticket_whose_mandatory_input_is_absent_is_not_ready` | 1 | An input naming no record: not READY, exactly [INPUT_ABSENT]. | KPI S4 [CAP-31.d]; DEC-294 |
| `test_w1_09_inputs.py::test_a_ticket_whose_mandatory_input_is_superseded_is_not_ready` | 1 | A record whose supersedes names the input gives exactly [INPUT_SUPERSEDED]. | KPI S4; DEC-294, DEC-277 L2728 |
| `test_w1_09_inputs.py::test_a_ticket_whose_mandatory_inputs_are_all_present_is_ready` | 1 | Two inputs that are records: A is READY and nothing is blocked. | KPI S4 [CAP-31.d]; DEC-294 L2921-2922 |
| `test_w1_09_inputs.py::test_an_input_that_names_its_own_successor_is_superseded` | 1 | The input's own superseded_by gives [INPUT_SUPERSEDED]. | KPI S4; DEC-277, DEC-294 |
| `test_w1_09_inputs.py::test_one_absent_input_among_several_is_enough` | 1 | One absent input out of two holds A with INPUT_ABSENT only. | KPI S4; DEC-294 |
| `test_w1_09_inputs.py::test_the_successor_of_a_superseded_input_is_a_good_input` | 1 | An input that supersedes another is good: A is READY. | KPI S4; DEC-294 |
| `test_w1_09_inputs.py::test_the_ticket_becomes_ready_when_the_absent_input_arrives` | 1 | Adding the missing record makes A READY. | KPI S4; DEC-294 |
| `test_w1_09_ready.py::test_a_claimed_ticket_is_not_in_the_ready_queue` | 1 | A lock takes A out of the queue with exactly [CLAIMED]; B stays READY. | KPI S3, CAP-23 acceptance; DEC-292 L2910 |
| `test_w1_09_ready.py::test_a_closed_ticket_is_neither_ready_nor_blocked` | 1 | A closed ticket is in neither list. | README interface (README:78) |
| `test_w1_09_ready.py::test_a_file_in_place_of_the_acceptance_tests_folder_does_not_count` | 1 | A file at tests/acceptance/W9-01 gives [NO_ACCEPTANCE_TESTS]. | KPI F2; DEC-293 ("must be a directory") |
| `test_w1_09_ready.py::test_a_specification_that_is_no_record_is_not_closed` | 1 | An unknown specification id gives [SPEC_NOT_CLOSED]. | DEC-307 L3063 |
| `test_w1_09_ready.py::test_a_ticket_in_progress_is_not_in_the_ready_queue` | 1 | status in_progress with no lock gives [CLAIMED]. | DEC-116 L1054, DEC-292 L2910 |
| `test_w1_09_ready.py::test_a_ticket_is_not_ready_before_its_dependencies_are_closed` | 1 | In a chain A←B←C plus D, A and D are READY; B and C get exactly [DEPENDENCY_OPEN]. | KPI S3 [CAP-31.c]; README reading 1 |
| `test_w1_09_ready.py::test_a_ticket_that_names_no_folder_needs_the_folder_of_its_own_id` | 1 | With no path and no wbs_id, tests/acceptance/<ticket id>/ is required. | DEC-293 L2917 |
| `test_w1_09_ready.py::test_a_ticket_whose_dependency_is_only_claimed_is_not_ready` | 1 | A dependency that is in_progress (not closed) holds B with [DEPENDENCY_OPEN]. | CAP-31.c; DEC-292 |
| `test_w1_09_ready.py::test_a_ticket_whose_specification_is_closed_is_ready` | 1 | DEC-307 (owner) is the rule in force: a specification is closed when its record says CLOSED; DEC-348 names its trust of … | DEC-307 |
| `test_w1_09_ready.py::test_a_ticket_whose_specification_is_not_closed_is_not_ready` | 1 | the same rule (DEC-307); B's hand-set CLOSED record has no rows (ready.py:153-158) | DEC-307 |
| `test_w1_09_ready.py::test_a_ticket_with_one_of_two_dependencies_open_is_not_ready` | 1 | C, with one closed and one open dependency, is not READY; B is. | CAP-31.c |
| `test_w1_09_ready.py::test_a_ticket_without_its_acceptance_tests_folder_is_not_ready` | 1 | With no tests folder, A gets exactly [NO_ACCEPTANCE_TESTS]; B is READY. | KPI F2; DEC-293 L2916-2917; MR-3 |
| `test_w1_09_ready.py::test_closing_a_dependency_makes_the_next_ticket_ready` | 1 | Closing A makes B READY; C stays DEPENDENCY_OPEN. | CAP-31.c |
| `test_w1_09_ready.py::test_every_open_ticket_is_either_ready_or_blocked` | 1 | Open and in_progress tickets split into ready and blocked with no overlap; the closed ticket is in neither. | README interface; DEC-292 |
| `test_w1_09_ready.py::test_every_reason_that_holds_a_ticket_is_reported` | 1 | A ticket that is claimed, has an open dependency and no folder gets all three reasons. | README reading 3; DEC-292, DEC-293 |
| `test_w1_09_ready.py::test_reading_the_queue_changes_nothing_in_the_project` | 1 | ready() and blocked() leave the tree outside .git and .gov-runtime byte-identical. | README reading 4 |
| `test_w1_09_ready.py::test_the_acceptance_tests_of_another_ticket_do_not_count` | 1 | Folders W9-010/ and W9-02/ do not make W9-01 READY. | KPI F2; DEC-293 |
| `test_w1_09_ready.py::test_the_folder_is_the_one_the_ticket_names` | 1 | The ticket's acceptance_tests.path is used, not the WBS folder. | DEC-293 L2916-2917; DEC-892 item 1 (live L10081) … |
| `test_w1_09_ready.py::test_the_ticket_becomes_ready_when_its_acceptance_tests_folder_exists` | 1 | Creating tests/acceptance/<wbs>/ makes A READY. | KPI F2; DEC-293 |
| `test_w1_09_ready.py::test_the_ticket_becomes_ready_when_its_specification_closes` | 1 | the same rule (DEC-307; ready.py:162-167) | DEC-307 |
| `test_w1_09_ready.py::test_tickets_with_nothing_in_their_way_are_all_ready` | 1 | Three independent tickets are all READY and nothing is blocked. | KPI S3 [CAP-31.c] |
| `test_w1_09_review.py::test_a_claim_in_a_claims_folder_that_cannot_be_read_still_holds_the_ticket` | 1 | With .tickets/.claims at mode 000, the locked ticket is not READY, exactly [CLAIMED]. | KPI S3 [CAP-31.c]; DEC-301 L2999 |
| `test_w1_09_review.py::test_a_folder_that_is_not_below_the_projects_acceptance_tests_does_not_count` | 11 | Eleven named folders (absolute, ., ./, .., ../elsewhere, src, .git, tests/acceptance/, wbs . and ../.., a link out) … | KPI F2; DEC-300 L2992-2993 |
| `test_w1_09_review.py::test_a_named_folder_below_the_projects_acceptance_tests_counts` | 2 | A named folder below tests/acceptance/, with or without the trailing slash, makes the ticket READY. | DEC-293, DEC-300 |
| `test_w1_09_unloaded_package.py::test_a_file_the_store_could_not_load_that_constrains_nothing_blocks_nothing` | 1 | Files the store did not load, with no constrains or an empty one, hold nothing. | DEC-579 (settlement 4) |
| `test_w1_09_unloaded_package.py::test_a_package_the_store_could_not_load_blocks_the_ticket_it_names` | 4 | A file the store did not load (no status, a list status, no type, no id) holds A with only "DECISION_NOT_LOADED: … | DEC-544 L5909, DEC-569 L6145, DEC-579 L6236; … |
| `test_w1_09_unloaded_package.py::test_a_package_whose_frontmatter_cannot_be_read_holds_every_ticket` | 2 | Invalid YAML or an unclosed frontmatter holds both tickets, each naming the file. | DEC-579 L6236 (P-10.2 (a)) |
| `test_w1_09_unloaded_package.py::test_the_ticket_is_ready_again_when_the_package_loads_and_is_closed` | 1 | Repairing the file into a loaded ACCEPTED package releases A. | DEC-544, DEC-579 |
| `test_w1_09_vendoring.py::test_the_ticket_script_is_vendored_into_the_kernel_template` | 1 | template/governance/kernel/bin/tk is a regular file, not a link. | KPI S1; DEC-074 L488; ADR-0002 §3, §5 |
| `test_w1_09_vendoring.py::test_the_vendored_script_has_the_pinned_sha256` | 1 | The file's sha256 equals the v0.3.2 pin 408f2c11…902b. | KPI S1; DEC-074, DEC-296 L2935 |
| `test_w1_09_vendoring.py::test_the_vendored_script_is_executable` | 1 | The file has the execute bit, and the git index records mode 100755. | KPI S1 |
| `test_w1_09_vendoring.py::test_the_vendored_script_matches_the_tool_registry` | 1 | The registry's ticket entry says v0.3.2 and carries the file's sha256. | KPI S1; DEC-074, DEC-296 |
| `test_w1_09_vendoring.py::test_the_vendored_script_works_without_the_installed_one` | 1 | The template's tk, with no tk on PATH, creates a ticket and lists it in tk ready. | KPI S1; ADR-0002 §5 |

**W1-11**: W1-11 (DAEO-be7u); 100 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_11_approval.py::test_a_commit_without_any_trailer_that_sets_a_decision_active_fails` | 1 | A commit with no trailer that sets ACTIVE is flagged | S2; DEC-360, DEC-182 |
| `test_w1_11_approval.py::test_a_later_owner_commit_that_does_not_set_active_approves_nothing_earlier` | 2 | After an agent sets ACTIVE, a later owner commit (editing it, or another file) approves nothing | S2; DEC-360 |
| `test_w1_11_approval.py::test_a_project_file_cannot_manufacture_the_approval` | 1 | Approval claims in frontmatter, body and governance/project/approvals.yaml do not stop ACTIVE_UNAPPROVED | S2; CAP-01.b, DEC-360 |
| `test_w1_11_approval.py::test_a_register_the_owner_approved_passes_the_whole_check` | 1 | The clean register committed by the owner gives an empty list | S2, interface; DEC-360 |
| `test_w1_11_approval.py::test_an_agent_commit_made_before_the_trailer_rule_is_no_approval` | 1 | An agent commit before 2026-10-03 with `Role: engineer` in its body is flagged | S2; DEC-182, DEC-360 |
| `test_w1_11_approval.py::test_an_agent_commit_that_adds_a_proposed_decision_passes` | 1 | An agent adding a PROPOSED decision raises no ACTIVE_UNAPPROVED for it | S2 control; DEC-360 |
| `test_w1_11_approval.py::test_an_agent_commit_that_adds_an_active_decision_fails` | 1 | An agent commit (Role: engineer) adding ADR-0010 ACTIVE gives ACTIVE_UNAPPROVED naming id and path | S2; DEC-360, DEC-182 |
| `test_w1_11_approval.py::test_an_agent_commit_that_changes_a_status_to_active_fails` | 1 | An agent commit changing PROPOSED to ACTIVE is flagged | S2; DEC-360 |
| `test_w1_11_approval.py::test_an_agent_edit_that_leaves_an_approved_decision_active_passes` | 1 | An agent body edit keeping an owner-approved decision ACTIVE raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_approval.py::test_an_agent_that_sets_an_approved_decision_active_again_fails` | 1 | Owner sets ACTIVE, agent sets PROPOSED, then agent sets ACTIVE again: flagged | S2; DEC-360 |
| `test_w1_11_approval.py::test_an_owner_commit_that_sets_a_decision_active_passes` | 1 | The owner's Role: owner commit setting ACTIVE raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_approval.py::test_every_unapproved_active_decision_is_flagged` | 1 | Two ACTIVE decisions added by one agent commit are both flagged | S2, F1; DEC-360 |
| `test_w1_11_approval.py::test_the_owner_name_and_email_on_an_agent_commit_are_no_approval` | 1 | The owner's name and email with an agent's Role trailer is flagged: identity is no fact | S2; CAP-21.a, DEC-360 |
| `test_w1_11_approval.py::test_the_owner_role_in_the_message_body_of_a_commit_made_before_the_trailer_rule_approves` | 1 | An owner commit before 2026-10-03 with `Role: owner` only in its body approves | S2; DEC-182, DEC-360 |
| `test_w1_11_approval_fail_closed.py::test_an_agent_merge_of_two_crossed_lines_that_both_hold_the_approved_file_passes` | 1 | Crossed lines that both hold the owner's file: an agent merge gives [] | S2 control; DEC-398 |
| `test_w1_11_approval_fail_closed.py::test_an_agent_merge_that_cannot_be_judged_against_one_merge_base_fails` | 4 | With two merge bases or none, an agent merge holding the decision ACTIVE is ACTIVE_UNAPPROVED (accepted false alarms) | S2; DEC-398, DEC-403, DEC-410, DEC-418 |
| `test_w1_11_approval_fail_closed.py::test_an_agent_merge_with_too_many_parents_that_sets_active_again_does_not_pass` | 1 | A 25-parent agent merge that sets ACTIVE again gives ACTIVE_UNAPPROVED or GovError, never a pass | S2; DEC-398, DEC-410 |
| `test_w1_11_approval_fail_closed.py::test_an_owner_merge_that_cannot_be_judged_against_one_merge_base_passes` | 4 | The same four merges made by the owner raise no ACTIVE_UNAPPROVED | S2 control; DEC-398, DEC-360 |
| `test_w1_11_approval_history.py::test_a_commit_message_that_imitates_an_owner_log_entry_is_no_approval` | 2 | Separator-laden text imitating a log entry with `Role: owner`, in subject or body, approves nothing | S2; DEC-360, CAP-01.b |
| `test_w1_11_approval_history.py::test_a_control_character_in_a_commit_message_does_not_break_the_check` | 1 | A unit separator in an unrelated commit message: the check returns [] and does not raise | interface; DEC-329 |
| `test_w1_11_approval_history.py::test_a_later_owner_commit_on_a_merged_branch_approves_nothing_earlier` | 1 | An earlier-dated owner edit that descends from the agent's activation, merged by an agent, is flagged (ancestry, not … | S2; DEC-360 |
| `test_w1_11_approval_history.py::test_an_agent_decision_kept_by_a_merge_over_the_owner_file_at_the_same_path_fails` | 1 | Both sides add the file; resolved to the agent's file: flagged | S2; DEC-360, CAP-01.b |
| `test_w1_11_approval_history.py::test_an_owner_commit_on_a_branch_that_sets_active_approves_after_the_merge` | 1 | The owner sets ACTIVE on a branch; the agent's merge sets nothing: no ACTIVE_UNAPPROVED | S2 control; DEC-360, DEC-398 |
| `test_w1_11_approval_history.py::test_an_owner_commit_that_only_renames_the_file_approves_nothing_earlier` | 1 | The owner's pure rename after an agent's activation approves nothing: flagged at the new path | S2; DEC-360, DEC-387 |
| `test_w1_11_approval_merge_base.py::test_a_second_merge_that_keeps_the_owner_file_does_not_hide_an_agent_reactivation` | 1 | A second merge restoring the owner's file over an agent's re-activation is flagged | S2; DEC-398, DEC-360 |
| `test_w1_11_approval_merge_base.py::test_an_agent_integration_merge_of_a_branch_where_the_owner_added_a_decision_passes` | 1 | An ordinary integration merge of a decision the owner added gives [] | S2 control; DEC-398, DEC-394 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_of_a_branch_that_only_moved_an_approved_decision_passes` | 1 | An agent merge of a branch that only moved the file gives [] | S2 control; DEC-398, DEC-387 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_that_brings_nothing_about_decisions_passes` | 1 | A merge that touches no decision gives [] | S2 control; DEC-394 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_that_keeps_a_moved_active_file_over_a_demotion_at_the_old_path_fails` | 2 | A moved ACTIVE file kept over a demotion or removal at the old path is flagged at the moved path | S2; DEC-398, DEC-387 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_that_keeps_active_fails_although_the_demoted_line_merged_an_old_branch` | 2 | The demoted line merged an old branch; an agent merge keeping ACTIVE is still flagged | S2; DEC-398, DEC-418, DEC-360 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_that_keeps_active_over_a_concurrent_owner_demotion_fails` | 2 | An agent merge keeping ACTIVE over a concurrent owner demotion or removal is flagged | S2; DEC-398, DEC-418 |
| `test_w1_11_approval_merge_base.py::test_an_agent_merge_that_keeps_the_owner_file_over_an_agent_file_at_the_same_path_fails` | 1 | Both sides add the file; an agent merge keeps the owner's file: flagged | S2; DEC-398 |
| `test_w1_11_approval_merge_base.py::test_an_old_branch_merged_late_into_a_line_where_the_owner_approved_passes` | 2 | A branch cut before the approval (PROPOSED or no file), merged late by an agent, gives [] | S2 control; DEC-398 |
| `test_w1_11_approval_merge_base.py::test_an_owner_merge_that_keeps_active_over_a_concurrent_demotion_passes` | 1 | The same merge by the owner raises no ACTIVE_UNAPPROVED | S2 control; DEC-398, DEC-360 |
| `test_w1_11_approval_merge_base.py::test_an_owner_merge_that_keeps_active_over_the_demoted_line_passes` | 1 | The owner's merge over the demoted line raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_approval_merge_base.py::test_an_owner_merge_that_keeps_the_moved_file_over_the_demotion_passes` | 1 | The owner's merge keeping the moved file over the demotion raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_approval_merge_base.py::test_the_main_line_merged_back_into_a_ticket_branch_and_the_branch_merged_passes` | 1 | A merge back into the branch, then the branch's merge, both give [] | S2 control; DEC-398, DEC-394 |
| `test_w1_11_approval_merge_base.py::test_the_same_merge_fails_without_the_old_branch` | 2 | a paired control, kept on purpose (README:373): the same history without the old-branch merge is flagged, which shows … | S2; DEC-360 |
| `test_w1_11_approval_merges.py::test_an_agent_merge_that_brings_in_the_owner_commit_that_set_active_again_passes` | 1 | An agent merge that brings in the owner's later re-activation raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_approval_merges.py::test_an_agent_merge_that_sets_active_again_a_decision_the_owner_demoted_fails` | 4 | Four agent two-parent commits that re-activate an owner-demoted decision are each flagged | S2; DEC-360, DEC-398 |
| `test_w1_11_approval_merges.py::test_an_owner_merge_that_sets_active_again_a_demoted_decision_passes` | 1 | The same merge by the owner raises no ACTIVE_UNAPPROVED | S2 control; DEC-360 |
| `test_w1_11_b_dev.py::test_a_supersession_cycle_between_the_two_directories_is_flagged` | 1 | ADR-003 and DEC-003 superseding each other give SUPERSESSION_CYCLE | S1; DEC-329 |
| `test_w1_11_b_dev.py::test_adr_003_is_flagged_as_active_while_superseded_once_dec_003_names_it` | 1 | After DEC-003 gains `supersedes: [ADR-003]`, ADR-003 is ACTIVE_SUPERSEDED | S1; DEC-329, DEC-277 |
| `test_w1_11_b_dev.py::test_one_id_in_both_decision_directories_is_flagged` | 1 | dec-001 given the id ADR-001: DUPLICATE_ID names both files | S1; DEC-329 |
| `test_w1_11_b_dev.py::test_the_overlapping_ids_of_the_two_decision_directories_are_flagged` | 1 | On b-dev as planted, OVERLAPPING_ID names ADR-00N, DEC-00N and both files for N=001..006 | S1, F1; DEC-329 |
| `test_w1_11_b_dev.py::test_the_tier_is_byte_identical_after_the_check` | 1 | A check of the b-dev clone flags something and changes no file, HEAD, ref, index or status | S3, F2 |
| `test_w1_11_citing_files.py::test_a_citing_file_without_an_id_is_authorised_by_an_answered_gate_of_its_cit` | 1 | The same file citing an ACCEPTED gate of its CIT gets no GATE_NOT_AUTHORISING for that gate | S4 control; DEC-331 |
| `test_w1_11_citing_files.py::test_a_citing_file_without_an_id_is_not_authorised_by_a_declined_gate` | 2 | A ticket or change with `approval` but no `id`, citing a DECLINED gate: GATE_NOT_AUTHORISING names the gate and file | S4; DEC-331 |
| `test_w1_11_citing_files.py::test_a_citing_ticket_whose_frontmatter_cannot_be_read_does_not_pass` | 1 | A citing ticket with broken YAML gives FRONTMATTER_UNREADABLE naming it | S4; DEC-331 |
| `test_w1_11_citing_files.py::test_a_second_empty_approval_key_does_not_take_the_first_out_of_the_check` | 1 | approval` written twice gives GATE_NOT_AUTHORISING or FRONTMATTER_UNREADABLE naming the file | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_cited_id_that_is_no_record_does_not_authorise` | 1 | A cited id with no record is flagged, naming the id as written | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_cited_record_that_is_no_decision_package_does_not_authorise` | 1 | An ACCEPTED decision record with the same `cit` is no gate: flagged | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_citing_record_without_a_cit_is_not_authorised` | 1 | A citing ticket with no `cit` is flagged | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_closed_ticket_named_by_a_dead_package_is_not_failed` | 1 | A closed ticket named by a STALE package gets no finding | S4; DEC-330 |
| `test_w1_11_gates.py::test_a_declined_revoked_or_stale_gate_does_not_authorise` | 6 | A ticket or change citing a DECLINED, REVOKED or STALE gate is flagged, naming citer, gate and file | S4; DEC-331, DEC-328 |
| `test_w1_11_gates.py::test_a_gate_answered_for_another_cit_does_not_authorise` | 2 | An ACCEPTED gate of another CIT does not authorise: flagged | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_gate_answered_for_the_same_cit_authorises` | 2 | An ACCEPTED gate of the same CIT gives the citer no GATE_NOT_AUTHORISING | S4 control; DEC-331 |
| `test_w1_11_gates.py::test_a_gate_without_a_cit_does_not_authorise` | 1 | A gate with no `cit` does not authorise: flagged | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_record_without_approval_is_not_checked` | 1 | A ticket with `cit` but no `approval`, beside dead, open and other-CIT gates, gets no GATE_NOT_AUTHORISING at all | S4; DEC-331 |
| `test_w1_11_gates.py::test_a_ticket_that_waits_on_a_declined_revoked_or_stale_package_fails` | 3 | An open ticket in a dead package's `constrains` gives TICKET_WAITS_ON_DEAD_GATE | S4; DEC-330 |
| `test_w1_11_gates.py::test_a_ticket_that_waits_on_an_open_or_answered_package_is_not_failed_by_the_checker` | 2 | A PROPOSED or ACCEPTED package gives no TICKET_WAITS_ON_DEAD_GATE | S4 control; DEC-330, DEC-308 |
| `test_w1_11_gates.py::test_an_open_gate_does_not_authorise` | 1 | A PROPOSED gate does not authorise: flagged | S4; DEC-331, DEC-308 |
| `test_w1_11_gates.py::test_one_dead_gate_among_the_cited_gates_fails_the_ticket` | 1 | Of two cited gates, the REVOKED one is flagged and the ACCEPTED one is not | S4; DEC-331 |
| `test_w1_11_gates.py::test_only_the_record_that_cites_the_dead_gate_fails` | 1 | Only the ticket citing the DECLINED gate is flagged | S4; DEC-331 |
| `test_w1_11_gates.py::test_two_missing_cits_are_not_the_same_cit` | 1 | When neither side has a `cit`, the citer is flagged | S4; DEC-331 |
| `test_w1_11_git_environment.py::test_git_dir_does_not_make_a_folder_that_is_no_repository_pass` | 1 | A plain folder with GIT_DIR set raises GovError | interface |
| `test_w1_11_git_environment.py::test_git_dir_does_not_make_a_subfolder_of_a_repository_pass` | 1 | A subfolder root with GIT_DIR set gives a finding or GovError, never a pass | interface |
| `test_w1_11_git_environment.py::test_git_dir_naming_another_repository_does_not_hide_the_findings_of_the_root` | 1 | With GIT_DIR naming a clean repository, the root's agent decision is flagged, or GovError | interface |
| `test_w1_11_git_files_and_settings.py::test_a_file_that_hides_a_parent_does_not_turn_a_flagged_agent_merge_into_a_pass` | 2 | A hand-written shallow file or an edited commit-graph gives a finding or GovError, never a pass | S2; DEC-387, DEC-398 |
| `test_w1_11_git_files_and_settings.py::test_a_git_setting_does_not_make_another_line_the_owner_trailer` | 3 | trailer.separators or trailer.<name>.key (repository or user config) does not make "Role# owner" or "Approved: owner" … | S2; DEC-360, DEC-182 |
| `test_w1_11_git_files_and_settings.py::test_a_grafts_file_does_not_turn_a_flagged_agent_merge_into_a_pass` | 1 | Flagged both before and after `.git/info/grafts` re-parents K | S2; DEC-387, DEC-398, DEC-360 |
| `test_w1_11_git_files_and_settings.py::test_an_owner_merge_passes_with_a_commit_graph_git_wrote` | 1 | The owner's merge with an ordinary commit-graph gives [] | S2 control; DEC-360 |
| `test_w1_11_git_files_and_settings.py::test_an_owner_merge_passes_with_a_grafts_file_in_place` | 1 | The owner's merge with a grafts file in place gives [] | S2 control; DEC-360 |
| `test_w1_11_git_files_and_settings.py::test_the_owner_trailer_still_approves_with_the_setting_in_place` | 2 | The owner's real `Role: owner` still approves with such a setting in .git/config: [] | S2 control; DEC-360 |
| `test_w1_11_hazards.py::test_a_cycle_closed_through_superseded_by_is_flagged` | 1 | A cycle closed by a `superseded_by` edge is flagged | S1; DEC-277 |
| `test_w1_11_hazards.py::test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass` | 1 | A plain folder raises GovError with a code and map details | interface |
| `test_w1_11_hazards.py::test_a_supersession_cycle_is_flagged_with_its_members` | 3 | Self, two- and three-member cycles each give a SUPERSESSION_CYCLE naming exactly the members | S1; CAP-51.a |
| `test_w1_11_hazards.py::test_a_supersession_stated_only_in_prose_is_not_read` | 1 | A supersession written only in prose raises no hazard | S1; DEC-329 |
| `test_w1_11_hazards.py::test_an_active_decision_that_another_supersedes_is_flagged` | 1 | ACTIVE ADR-0010 superseded by ADR-0011: ACTIVE_SUPERSEDED for ADR-0010 only | S1; DEC-277, DEC-329 |
| `test_w1_11_hazards.py::test_an_active_decision_that_names_its_own_successor_is_flagged` | 1 | An ACTIVE decision with `superseded_by` is flagged | S1; DEC-277 |
| `test_w1_11_hazards.py::test_every_active_superseded_decision_is_flagged_not_only_the_first` | 1 | Two ACTIVE decisions superseded by one decision are both flagged | F1; DEC-329 |
| `test_w1_11_hazards.py::test_every_hazard_planted_together_is_flagged` | 1 | Four hazard classes planted together are each flagged | F1; DEC-329 |
| `test_w1_11_hazards.py::test_ids_with_one_number_in_two_directories_are_flagged_as_overlapping` | 1 | ADR-0010 and DEC-0010 in two directories: OVERLAPPING_ID and no DUPLICATE_ID | S1; DEC-227 |
| `test_w1_11_hazards.py::test_one_id_in_two_directories_is_flagged` | 1 | One id in two directories gives DUPLICATE_ID naming both files | S1; DEC-329 |
| `test_w1_11_hazards.py::test_one_id_in_two_files_of_one_directory_is_flagged` | 1 | One id in two files of docs/adr/ gives DUPLICATE_ID naming both | S1; DEC-329 |
| `test_w1_11_hazards.py::test_the_same_tree_gives_the_same_findings_twice` | 1 | Two load-and-check runs give the same non-empty list | interface |
| `test_w1_11_no_id_and_replace_refs.py::test_a_replace_ref_that_gives_an_agent_commit_the_owner_role_is_no_approval` | 1 | A replace ref swapping in an owner-role copy does not approve the agent's commit | S2; DEC-387, DEC-360 |
| `test_w1_11_no_id_and_replace_refs.py::test_an_active_decision_without_an_id_set_by_an_agent_fails` | 1 | An ACTIVE `type: decision` file with no `id`: some finding names the file | F1; DEC-387 |
| `test_w1_11_object_store.py::test_a_check_leaves_every_file_under_git_as_it_was` | 1 | No file under root, .git/ included, differs after a check (finding or GovError) | S3, F2 |
| `test_w1_11_object_store.py::test_a_check_of_a_partial_clone_fetches_nothing_and_writes_nothing` | 1 | A blob:none clone: no file changes, absent objects unchanged, never a pass | S3, F2, S2 |
| `test_w1_11_object_store.py::test_a_check_of_a_partial_clone_whose_remote_is_out_of_reach_does_not_pass` | 1 | With the remote moved away: no writes, and a finding or GovError | S3, S2; DEC-360 |
| `test_w1_11_object_store.py::test_a_missing_object_does_not_make_a_later_owner_commit_the_approval` | 1 | A deleted loose blob of the agent's version gives a finding or GovError, never a pass | S2; DEC-360 |
| `test_w1_11_read_only.py::test_a_check_that_finds_every_hazard_leaves_every_file_byte_identical` | 1 | its no-change half is also in test_a_second_check_leaves_every_file_byte_identical_too (read_only.py:79-86), but its … | S3, F2 |
| `test_w1_11_read_only.py::test_a_check_that_finds_nothing_leaves_every_file_byte_identical` | 1 | Clean register: tree bytes, HEAD, refs, index and status unchanged | S3, F2 |
| `test_w1_11_read_only.py::test_a_second_check_leaves_every_file_byte_identical_too` | 1 | Two checks give equal results and change nothing | S3 |
| `test_w1_11_read_only.py::test_decision_files_a_rewrite_would_not_reproduce_stay_byte_identical` | 1 | CRLF, BOM, no-final-newline, odd-spacing and broken decision files stay byte-identical | F2 |
| `test_w1_11_read_only.py::test_uncommitted_work_in_the_tree_is_left_as_it_is` | 1 | Modified, staged and untracked decision files are left as they are | S3 |
| `test_w1_11_unreadable.py::test_a_decision_file_that_cannot_be_read_does_not_pass_in_silence` | 7 | Broken YAML, unclosed, BOM, blank line, `--- # c`, CR-only or UTF-16 head: FRONTMATTER_UNREADABLE names the file | F1; DEC-329, DEC-387 |
| `test_w1_11_unreadable.py::test_a_markdown_file_without_frontmatter_is_not_unreadable` | 1 | A file that opens with a heading and has a later `---` rule gives [] | F1 control; DEC-274 |
| `test_w1_11_unreadable.py::test_an_ordinary_file_is_not_unreadable` | 1 | A CRLF decision, prose opening with a BOM or blank line, and a `-----` rule give [] | F1 control; DEC-387 |

**W1-12**: W1-12 (DAEO-lc4q); 21 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_12_capability_types.py::test_each_capability_type_marks_the_rows_of_the_yaml` | 1 | For each type, the schema marks the YAML's rows. | KPI S3; CAP-30.e; DEC-085 |
| `test_w1_12_capability_types.py::test_the_schema_states_the_governed_change_rule` | 1 | the schema carries the YAML's rule text and names CIT-E (capability_types.py:44-49): what DEC-309 gives W1-12; … | KPI S3 (second half); CAP-30.e; DEC-309 |
| `test_w1_12_capability_types.py::test_the_table_has_the_capability_types_of_the_yaml` | 1 | The schema's extra_rows_for_standard has exactly the YAML's capability types. | KPI S3; CAP-30.e; DEC-085, DEC-302 |
| `test_w1_12_capability_types.py::test_the_table_marks_only_rows_the_schema_carries` | 1 | Every row number in the schema's table is a row the schema carries. | KPI S3 |
| `test_w1_12_default_schema.py::test_a_change_made_without_the_schema_option_gets_the_readiness_record` | 1 | the default schema gives the readiness artifact (default_schema.py:26-32); it skips where openspec is absent … | DEC-303 |
| `test_w1_12_default_schema.py::test_the_project_config_names_the_forked_schema` | 1 | template/openspec/config.yaml says schema: feature-readiness. | DEC-303 |
| `test_w1_12_rows_and_states.py::test_every_row_is_carried_by_its_id_in_order` | 1 | The schema carries the YAML's 26 (n, key) rows in order, none missing or extra. | KPI S1, F1; CAP-30.a; DEC-085 |
| `test_w1_12_rows_and_states.py::test_every_row_name_is_the_name_in_the_yaml` | 1 | Each row's name equals the YAML's, character by character. | KPI F1; CAP-30.a |
| `test_w1_12_rows_and_states.py::test_fork_keeps_the_base_workflow_and_adds_the_readiness_record` | 1 | The fork keeps proposal, specs, design and tasks and adds one readiness artifact. | KPI S1; DEC-302 |
| `test_w1_12_rows_and_states.py::test_schema_is_where_openspec_looks_for_it` | 1 | schema.yaml in the feature-readiness folder names itself feature-readiness. | KPI S1; CAP-30.a |
| `test_w1_12_rows_and_states.py::test_the_five_states_are_carried_exactly` | 1 | The schema's state names equal the YAML's five, in order. | KPI S1, F1; CAP-30.a |
| `test_w1_12_rows_and_states.py::test_the_only_not_applicable_state_needs_a_reason` | 1 | N/A_WITH_REASON requires a reason, and no bare N/A state exists. | KPI S1; CAP-30.a; MR-1 |
| `test_w1_12_rows_and_states.py::test_the_readiness_record_template_fills_no_cell` | 1 | Every row of the fresh template is MISSING. | KPI S1; CAP-30.a; DEC-085 |
| `test_w1_12_rows_and_states.py::test_the_readiness_record_template_lists_every_row` | 1 | The readiness template lists each of the 26 rows exactly once. | KPI S1; CAP-30.a; DEC-305 |
| `test_w1_12_templates.py::test_a_fresh_change_from_the_templates_passes_validate_strict` | 1 | validate --strict on first use (templates.py:47-50); the same skip | KPI S2; DEC-087 |
| `test_w1_12_templates.py::test_a_template_that_breaks_the_delta_format_fails_validate_strict` | 1 | the negative control of the strict validation: the forked template with its scenario lines removed fails … | KPI F2 |
| `test_w1_12_templates.py::test_every_artifact_has_its_template_in_the_schema_folder` | 1 | Each artifact's template exists in templates/ and is not empty. | KPI S2 |
| `test_w1_12_templates.py::test_first_use_of_the_unforked_templates_fails_validate_strict` | 1 | the premise of the fork: OpenSpec's stock templates fail validate --strict (templates.py:67-69); only an OpenSpec … | KPI F2 (control) |
| `test_w1_12_templates.py::test_openspec_accepts_the_forked_schema` | 1 | openspec's own validation of the fork (templates.py:27-28); the same skip where openspec is absent | KPI S1; DEC-302 |
| `test_w1_12_templates.py::test_the_project_resolves_the_schema_and_its_templates` | 1 | the schema and every template resolve from the project (templates.py:34-41); the same skip | KPI S2 |
| `test_w1_12_templates.py::test_validating_everything_in_the_fresh_project_passes` | 1 | validate --all --strict after first use (templates.py:56-58); the same skip | KPI S2; DEC-087 |

**W1-13**: W1-13 (DAEO-w616); 67 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_13_close.py::test_a_closed_specification_with_its_audit_ticket_passes_the_command` | 1 | After closing, `gov readiness --specification` passes. | KPI S2, S5 |
| `test_w1_13_close.py::test_a_specification_is_not_closed_when_its_audit_ticket_cannot_be_created` | 1 | Without tk, close fails, the record is not CLOSED and no ticket exists. | KPI F3; DEC-349 |
| `test_w1_13_close.py::test_a_specification_with_a_required_row_open_is_not_closed` | 3 | With row 5 MISSING, close refuses SPEC_NOT_CLOSED and changes nothing. | KPI F1; DEC-349 |
| `test_w1_13_close.py::test_a_specification_with_a_silent_na_is_not_closed` | 1 | Row 12 N/A_WITH_REASON with no reason is refused READINESS_INVALID; nothing changes. | KPI F2; DEC-085 |
| `test_w1_13_close.py::test_a_spine_complete_only_for_the_profile_that_opened_it_is_not_closed` | 1 | A LITE-opened spine with only the LITE rows satisfied is refused SPEC_NOT_CLOSED. | KPI F1, F3; DEC-085 |
| `test_w1_13_close.py::test_closing_a_lite_feature_specification_creates_no_audit_ticket` | 1 | A complete LITE feature closes with no ticket and audit_ticket null. | KPI S5; DEC-088 |
| `test_w1_13_close.py::test_closing_changes_the_record_and_adds_the_ticket_and_nothing_else` | 1 | Only proposal.md changes and one ticket file is added; HEAD and refs are unchanged. | KPI S5; DEC-349 |
| `test_w1_13_close.py::test_closing_marks_the_record_closed_and_creates_one_audit_ticket` | 3 | Closing a complete FULL, STANDARD or LITE-opened spine sets CLOSED and creates exactly one ticket, which it returns. | KPI S5, F3; CAP-47.d; DEC-088, DEC-349 |
| `test_w1_13_close.py::test_closing_twice_creates_one_audit_ticket` | 1 | A second close of the closed specification adds no ticket. | KPI F3; DEC-088 |
| `test_w1_13_close.py::test_the_audit_ticket_carries_what_the_ticket_schema_requires` | 1 | The ticket has a non-empty allowed_paths and kpis with success and failure lists. | KPI S5; ticket.schema.json |
| `test_w1_13_close.py::test_the_audit_ticket_is_an_open_ticket_nobody_holds` | 1 | The ticket is open, AUTHORITATIVE and unclaimed. | KPI S5; DEC-349 |
| `test_w1_13_close.py::test_the_audit_ticket_is_for_an_independent_auditor_and_names_the_milestone` | 3 | The ticket has role independent-auditor, class audit, and a title naming the specification. | KPI S5; CAP-47.d; DEC-088 |
| `test_w1_13_command.py::test_a_specification_that_does_not_exist_does_not_pass` | 1 | An unknown specification id gives ok false and a non-zero exit. | KPI F1; DEC-353 |
| `test_w1_13_command.py::test_an_unknown_argument_is_a_usage_error` | 1 | An unknown option exits 2. | API-0002; DEC-351 |
| `test_w1_13_command.py::test_help_names_the_two_selectors` | 1 | --help` exits 0 and names --specification and --ticket. | DEC-351, DEC-307 |
| `test_w1_13_command.py::test_readiness_no_longer_returns_not_implemented` | 1 | The bare `--json` run gives a valid envelope, not NOT_IMPLEMENTED, and its exit is not 2. | CAP-28.b; DEC-190, DEC-317 |
| `test_w1_13_command.py::test_without_arguments_nothing_is_written` | 1 | The bare command leaves files, git status and refs unchanged. | CAP-27.a; DEC-317 |
| `test_w1_13_determinism.py::test_open_rows_are_listed_in_row_order_whatever_the_order_in_the_file` | 1 | Shuffled rows (seed 13) are reported in row order 1 to 26. | KPI S3, S1 |
| `test_w1_13_determinism.py::test_the_bare_command_is_the_same_on_repeated_runs` | 1 | Three bare runs over three specifications are identical. | KPI S3; DEC-351 |
| `test_w1_13_determinism.py::test_the_plain_form_names_the_open_cells` | 1 | The plain output names the open keys, the gap ticket and UNLINKED; exit 3. | MR-1; KPI S4 |
| `test_w1_13_determinism.py::test_three_runs_print_the_same_bytes_and_end_with_the_same_code` | 6 | Three runs (open, complete, invalid; JSON and plain) give identical output and exit code. | KPI S3 |
| `test_w1_13_gap_tickets.py::test_a_fresh_full_record_lists_all_26_rows_unlinked` | 1 | A fresh FULL record lists all 26 rows UNLINKED. | KPI S4; DEC-089 |
| `test_w1_13_gap_tickets.py::test_a_required_open_row_is_listed_with_its_gap_ticket` | 1 | A required MISSING row is reported with its gap_ticket id. | KPI S4; CAP-30.b; DEC-089, DEC-305 |
| `test_w1_13_gap_tickets.py::test_a_required_open_row_with_no_gap_ticket_is_unlinked` | 3 | A null, empty or blank gap_ticket is reported UNLINKED. | KPI S4; DEC-089 |
| `test_w1_13_gap_tickets.py::test_a_row_whose_gap_ticket_key_is_absent_is_unlinked` | 1 | A required open row without a gap_ticket key is UNLINKED. | KPI S4; DEC-089 |
| `test_w1_13_gap_tickets.py::test_every_required_open_row_is_listed_linked_or_not` | 1 | Required MISSING, PROVISIONAL and BLOCKED rows are all listed, linked or UNLINKED. | KPI S4; DEC-089 (line 821), DEC-085 |
| `test_w1_13_gap_tickets.py::test_rows_that_are_satisfied_or_not_required_are_not_listed` | 1 | At LITE only required open row 5 is listed. | KPI S4; DEC-089 |
| `test_w1_13_gate.py::test_a_ticket_is_ready_once_its_specification_is_complete_and_closed` | 1 | Blocked before closing, ready after closing a complete LITE specification. | KPI S2; DEC-307, DEC-349 |
| `test_w1_13_gate.py::test_a_ticket_stays_out_of_ready_while_its_specification_has_a_required_row_open` | 1 | Close refuses; the ticket naming the specification is blocked SPEC_NOT_CLOSED, the other is ready. | KPI S2; CAP-30 acceptance; MR-1; DEC-307 |
| `test_w1_13_gate.py::test_the_command_writes_nothing` | 4 | Held, complete-spine, invalid and by-ticket runs change no file, ref, ticket or status. | CAP-27.a; DEC-317 |
| `test_w1_13_gate.py::test_the_gate_is_open_when_no_required_row_is_open` | 1 | A complete specification exits 0 in both forms. | KPI S2; DEC-348 |
| `test_w1_13_gate.py::test_the_gate_is_shut_on_an_invalid_record` | 1 | An empty reason on row 12 exits 1 in both forms. | KPI S2, F2; DEC-351 |
| `test_w1_13_gate.py::test_the_gate_is_shut_while_a_required_row_is_open` | 1 | With row 7 MISSING, the command exits 3 in both forms. | KPI S2; DEC-348 |
| `test_w1_13_gate.py::test_the_gate_judges_each_specification_on_its_own` | 1 | An open and a complete specification exit 3 and 0. | KPI S2 |
| `test_w1_13_gate.py::test_the_gate_opens_when_the_last_open_row_is_settled` | 1 | Exits 3, then 0 once row 7 is satisfied. | KPI S2 |
| `test_w1_13_gate.py::test_the_gate_reads_the_rows_and_not_the_status` | 1 | A record marked CLOSED with row 7 MISSING exits 3. | KPI S2, F1; DEC-348 |
| `test_w1_13_na.py::test_a_present_row_that_cites_nothing_does_not_pass` | 1 | A PRESENT row with no evidence does not pass. | KPI F1; DEC-353 |
| `test_w1_13_na.py::test_a_reason_written_by_an_agent_is_accepted_on_every_optional_row` | 1 | The same 16 rows with a reason pass. | KPI F2 (control); DEC-085 |
| `test_w1_13_na.py::test_a_record_that_defaults_every_optional_row_to_na_does_not_pass` | 1 | The 16 optional rows defaulted to N/A with no reason are all rejected. | KPI F2; DEC-085 |
| `test_w1_13_na.py::test_a_record_that_drops_a_row_does_not_pass` | 1 | A record without row 12 does not pass. | KPI F2 |
| `test_w1_13_na.py::test_a_silent_na_on_a_required_row_is_rejected` | 7 | Each of seven silent forms on row 12 gives READINESS_INVALID, exit 1, naming only row 12. | KPI S1, F2; CAP-30.a; DEC-085 |
| `test_w1_13_na.py::test_a_silent_na_on_a_row_the_profile_does_not_require_is_rejected` | 2 | A null or empty reason on row 12 at LITE is rejected anyway. | KPI F2; DEC-085 |
| `test_w1_13_na.py::test_every_rejected_row_is_named` | 1 | Rows 3, 12 and 22 are all named in error.details.invalid. | KPI F2; DEC-351 |
| `test_w1_13_report.py::test_a_capability_type_outside_the_taxonomy_does_not_pass` | 1 | A STANDARD specification declaring "blockchain" does not pass. | CAP-30.e; DEC-350 |
| `test_w1_13_report.py::test_a_fresh_record_has_every_row_its_profile_requires_open` | 5 | For five profiles, a fresh record's open rows are exactly that profile's required rows. | KPI S1; CAP-30.a, CAP-53.a; DEC-085 |
| `test_w1_13_report.py::test_a_record_marked_closed_by_hand_with_a_required_row_missing_is_not_reported_closed` | 1 | A hand-set CLOSED with row 7 MISSING is held with [7] open. | KPI F1; DEC-348 |
| `test_w1_13_report.py::test_a_record_with_every_required_row_satisfied_passes` | 5 | For five profiles, satisfying only the required rows passes. | KPI S1; CAP-53.a; DEC-085 |
| `test_w1_13_report.py::test_a_required_row_in_a_state_that_does_not_satisfy_is_open` | 3 | Row 7 MISSING, PROVISIONAL or BLOCKED is the one open row, with its state. | KPI S1; DEC-085 |
| `test_w1_13_report.py::test_a_row_that_is_not_applicable_with_its_reason_is_satisfied` | 1 | Rows 12 and 17 N/A_WITH_REASON with a reason pass. | KPI S1; DEC-085 |
| `test_w1_13_report.py::test_a_specification_with_no_profile_does_not_pass` | 1 | A specification that declares no profile does not pass. | DEC-350 |
| `test_w1_13_report.py::test_a_spine_is_judged_and_reported_at_full` | 1 | A LITE-opened spine reports FULL with its 16 non-mandatory rows open. | KPI S1; DEC-085 |
| `test_w1_13_report.py::test_a_standard_specification_holds_only_the_rows_of_its_declared_types` | 1 | STANDARD backend with row 13 MISSING has exactly [13] open. | KPI S1; CAP-53.a, CAP-30.e |
| `test_w1_13_report.py::test_a_ticket_whose_specification_is_complete_passes` | 1 | --ticket on a complete specification passes. | KPI S2; DEC-307 |
| `test_w1_13_report.py::test_each_open_row_carries_its_number_key_and_state` | 1 | Each open row's key matches the YAML for its number and its state is MISSING. | KPI S1; DEC-351 |
| `test_w1_13_report.py::test_one_required_missing_row_is_enough` | 3 | Row 1, 7 or 26 MISSING alone is the one open row. | KPI F1; CAP-30 acceptance |
| `test_w1_13_report.py::test_the_open_cells_of_a_tickets_specification_are_named` | 1 | --ticket reports the ticket's specification with rows 7 and 20 open. | MR-1; DEC-307, DEC-351 |
| `test_w1_13_report.py::test_the_report_names_the_specification_and_its_profile` | 1 | A passing STANDARD report names the specification and STANDARD. | KPI S1; DEC-351 |
| `test_w1_13_schema.py::test_a_weakened_schema_does_not_let_a_specification_be_closed` | 5 | The same five edits: close refuses, status DRAFT, no ticket, project unchanged. | KPI F1, F3; DEC-136, DEC-349 |
| `test_w1_13_schema.py::test_a_weakened_schema_does_not_let_a_specification_pass` | 5 | Five weakening edits of the project's schema copy still leave the command failing. | KPI F1; CAP-30.a, CAP-53.a; DEC-136, DEC-350 |
| `test_w1_13_unreadable.py::test_a_change_with_a_readiness_record_and_no_proposal_does_not_pass` | 1 | readiness.yaml without proposal.md is refused. | KPI F1; DEC-351 |
| `test_w1_13_unreadable.py::test_a_project_with_no_change_passes` | 1 | A project with no change passes the bare command. | control; DEC-351 |
| `test_w1_13_unreadable.py::test_a_proposal_that_is_not_of_type_specification_does_not_pass` | 1 | No `type`, then `type: note`: each is refused, naming the change. | KPI F1; DEC-350 |
| `test_w1_13_unreadable.py::test_a_proposal_whose_frontmatter_is_not_yaml_does_not_pass` | 1 | Frontmatter that is not YAML is refused. | KPI F1; DEC-350 |
| `test_w1_13_unreadable.py::test_a_proposal_with_no_frontmatter_does_not_pass` | 1 | A change with the template's frontmatter-less proposal makes the bare command READINESS_INVALID, exit 1, naming it. | KPI F1; DEC-136, DEC-350, DEC-351 |
| `test_w1_13_unreadable.py::test_a_proposal_with_no_id_does_not_pass` | 1 | No id, then an empty id: each is refused. | KPI F1; DEC-350 |
| `test_w1_13_unreadable.py::test_one_unreadable_change_beside_a_complete_specification_does_not_pass` | 1 | An unreadable change beside a complete specification makes the bare run fail. | KPI F1; DEC-351 |
| `test_w1_13_unreadable.py::test_the_archive_folder_is_not_a_change` | 1 | An unreadable change under changes/archive/ is ignored. | control; DEC-351 |

**W1-14**: W1-14 (DAEO-w9l3); 35 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_14_acceptance_paths.py::test_an_engineer_task_whose_paths_cover_the_acceptance_tests_gives_no_ticket` | 11 | Eleven covering spellings in an engineer task give TASKS_INVALID naming 1.1, and nothing is written. | KPI F2; MR-3, DEC-156 L1429, DEC-355 |
| `test_w1_14_acceptance_paths.py::test_no_role_but_the_test_designer_gets_the_acceptance_tests` | 3 | product-spec, orchestrator and independent-auditor tasks naming tests/acceptance/W9-01/** are refused. | KPI F2; MR-3 (Contract v4.2), DEC-156 |
| `test_w1_14_acceptance_paths.py::test_one_covering_engineer_task_refuses_the_whole_derivation` | 1 | One covering task among three refuses everything, naming only 1.3; nothing is written. | KPI F2; DEC-355 L3622-3623 |
| `test_w1_14_acceptance_paths.py::test_paths_that_only_look_like_the_acceptance_tests_are_derived` | 1 | Four look-alike paths are derived as written. | KPI F2 |
| `test_w1_14_acceptance_paths.py::test_the_test_designers_task_may_name_the_acceptance_tests` | 1 | The test designer's task is derived, keeping its role and paths. | MR-3; DEC-355 |
| `test_w1_14_derive.py::test_a_derived_ticket_carries_the_task_contract_of_its_task` | 1 | kpis, role, allowed_paths, profile and class equal the task's own. | KPI S1 [CAP-31.a]; DEC-355 L3621 |
| `test_w1_14_derive.py::test_a_derived_ticket_names_the_specification_of_its_change` | 1 | Each ticket's specification key holds the change's record id. | KPI S1; DEC-307, DEC-350 L3528 |
| `test_w1_14_derive.py::test_a_derived_ticket_says_what_its_task_says` | 1 | The ticket file contains the task's description. | KPI S1 |
| `test_w1_14_derive.py::test_a_task_that_names_inputs_gives_a_ticket_with_those_inputs` | 1 | A task's inputs are copied to its ticket. | CAP-31.a; DEC-294 |
| `test_w1_14_derive.py::test_derivation_writes_tickets_and_nothing_else_and_commits_nothing` | 1 | Only files under .tickets/ change, and HEAD is unchanged. | DEC-349 L3518-3524, DEC-355 L3620 |
| `test_w1_14_derive.py::test_every_task_of_the_change_becomes_one_ticket` | 1 | Three tasks give three tickets in file order and no others; the result names the change and the specification. | KPI S1 [CAP-31.a]; DEC-355 L3618-3619 |
| `test_w1_14_derive.py::test_two_changes_with_the_same_task_numbers_get_their_own_tickets` | 1 | The same task numbers in two changes give three distinct tickets, each with its own specification. | DEC-356 L3635 |
| `test_w1_14_refusals.py::test_a_change_that_does_not_exist_is_refused` | 1 | An unknown change folder gives a GovError (any code), and nothing is written. | README interface (README:38) |
| `test_w1_14_refusals.py::test_a_change_without_a_specification_record_is_refused` | 1 | A proposal.md from the delivered template (no frontmatter) gives a GovError, and nothing is written. | DEC-350 |
| `test_w1_14_refusals.py::test_a_change_without_tasks_is_refused` | 1 | A change with no tasks.md gives a GovError (any code), and nothing is written. | README interface |
| `test_w1_14_refusals.py::test_a_specification_closed_by_hand_with_a_required_row_open_gives_no_ticket` | 1 | CLOSED with a mandatory row MISSING gives SPEC_NOT_CLOSED, and nothing is written. | DEC-348 L3510-3512, DEC-356 L3630 |
| `test_w1_14_refusals.py::test_a_specification_that_is_not_closed_gives_no_ticket` | 2 | Status DRAFT, with rows open or complete, gives SPEC_NOT_CLOSED, and nothing is written. | MR-2; DEC-307, DEC-356 L3630 |
| `test_w1_14_refusals.py::test_a_task_that_lacks_kpis_allowed_paths_or_role_gives_no_ticket` | 11 | Eleven missing or malformed kpis, allowed_paths or role give TASKS_INVALID naming 1.1, and nothing is written. | KPI F1; DEC-355 L3621-3623 |
| `test_w1_14_refusals.py::test_a_task_with_no_block_gives_no_ticket` | 1 | A task without a YAML block refuses the derivation and is named. | KPI F1; DEC-355 |
| `test_w1_14_refusals.py::test_closing_the_specification_lets_its_tickets_be_derived` | 1 | Refused while DRAFT; derived once the status is CLOSED. | MR-2; DEC-356 L3630 |
| `test_w1_14_refusals.py::test_one_lacking_task_refuses_the_whole_derivation` | 1 | Two lacking tasks out of four refuse everything, naming exactly 1.2 and 2.1. | KPI F1; DEC-355 L3622-3623 |
| `test_w1_14_refusals.py::test_the_tasks_template_as_delivered_gives_no_ticket` | 1 | holds DEC-355's recorded residual: W1-12's tasks.md template does not show the YAML block, so a change written from it … | DEC-355 |
| `test_w1_14_rerun.py::test_a_refused_second_run_leaves_the_first_runs_tickets_alone` | 1 | A lacking new task refuses the second run and leaves the tree unchanged. | DEC-356 L3634-3635 |
| `test_w1_14_rerun.py::test_a_second_run_creates_no_duplicate_ticket` | 1 | A second run returns the same map and leaves every ticket file byte-identical. | KPI S2; DEC-356 L3634-3635 |
| `test_w1_14_rerun.py::test_a_second_run_does_not_reopen_work_and_derives_only_the_new_task` | 1 | The closed ticket stays untouched; only 1.3 gets a ticket, with deps and specification; the DAG is clean. | DEC-356 L3634-3635 |
| `test_w1_14_schema_and_dag.py::test_a_cycle_between_tasks_is_refused_and_no_ticket_is_written` | 3 | A cycle of two tasks, a task on itself, or a cycle of three gives TASKS_INVALID naming them, and nothing is written. | KPI S2; DEC-356 L3632-3633 |
| `test_w1_14_schema_and_dag.py::test_a_cycle_through_tickets_that_already_exist_is_refused` | 1 | Depending on an existing X↔Y cycle is refused, naming 1.2. | DEC-356 L3632-3633 |
| `test_w1_14_schema_and_dag.py::test_a_dependency_that_names_nothing_is_refused` | 2 | An unknown task or ticket as a dependency is refused, naming 1.2. | DEC-356 L3632 |
| `test_w1_14_schema_and_dag.py::test_a_derived_ticket_is_an_open_ticket` | 1 | A derived ticket's status is open. | KPI S2 |
| `test_w1_14_schema_and_dag.py::test_a_task_may_depend_on_a_ticket_that_already_exists` | 1 | A dependency on an existing ticket id is kept as written. | DEC-356 L3631-3632 |
| `test_w1_14_schema_and_dag.py::test_a_task_number_written_as_a_yaml_number_is_refused` | 1 | An unquoted 1.10 dependency is refused, naming 2.1. | DEC-356 L3632 |
| `test_w1_14_schema_and_dag.py::test_derived_tickets_are_held_when_their_specification_is_reopened` | 1 | Reopening the specification gives the ticket exactly [SPEC_NOT_CLOSED]. | DEC-307 L3062-3063 |
| `test_w1_14_schema_and_dag.py::test_derived_tickets_move_through_the_ready_rule` | 1 | Derived tickets go from NO_ACCEPTANCE_TESTS to DEPENDENCY_OPEN to READY as folders appear and 1.1 closes. | KPI S2; DEC-293, DEC-307 |
| `test_w1_14_schema_and_dag.py::test_derived_tickets_pass_the_ticket_schema` | 1 | Every derived ticket passes ticket.schema.json, checked by hand and through jsonschema. | KPI S2; W1-08 schemas |
| `test_w1_14_schema_and_dag.py::test_task_dependencies_become_ticket_dependencies` | 1 | depends_on becomes deps of ticket ids, a forward reference included; the graph is acyclic. | KPI S2; DEC-356 L3631-3632 |

**W1-27**: W1-27 (DAEO-xw3k); 72 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_27_doctor.py::test_doctor_does_not_pass_with_wrong_tool_version` | 1 | node pinned 0.0.1-fake, no prefix: envelope ok is not true | F1; CAP-25.a |
| `test_w1_27_doctor.py::test_doctor_envelope_is_valid_on_healthy_project` | 1 | fake-tool registry and minimal map: envelope ok=true, exit 0 | S1; CAP-25.a, CAP-06.a; DEC-452 |
| `test_w1_27_doctor.py::test_doctor_exit_nonzero_on_any_failure` | 1 | one absent fake tool: valid envelope, non-zero exit | S1; CAP-25.a |
| `test_w1_27_doctor.py::test_doctor_is_a_read_command` | 1 | valid envelope; project snapshot (minus .git, .gov-runtime) unchanged after doctor | S1; CAP-27.a; DEC-317, DEC-452 |
| `test_w1_27_doctor_r5.py::test_stale_path_in_historical_record_is_not_reported` | 4 | moved module's old path in each DEC-448 historical place: "old_historical_module" absent from doctor JSON | S3; CAP-06.d; DEC-448 (standing part) |
| `test_w1_27_doctor_r5.py::test_stale_path_section_counts_excluded_historical` | 1 | under the planted P27-5 (historical_excluded dropped from the stale-path section) it went red … | DEC-448 |
| `test_w1_27_doctor_r5.py::test_tool_at_empty_registered_location_fails` | 1 | nothing at the prefix: envelope not ok; entry location is the empty prefix | S1; CAP-25.a; DEC-448 |
| `test_w1_27_doctor_r5.py::test_tool_at_registered_location_passes` | 1 | fake tool under its install PATH prefix: entry ok, found_version 1.2.3, location is the prefix | S1; CAP-25.a; DEC-448 (standing part), DEC-202 |
| `test_w1_27_doctor_r5.py::test_tool_at_registered_location_wrong_version_fails` | 1 | under the planted P27-10 (a tool at the wrong version counted ok, command.py) it went red, with three other … | F1; CAP-25.a; DEC-448 |
| `test_w1_27_doctor_r5.py::test_tool_without_registered_location_found_on_path` | 1 | python3 entry with no prefix has a found_version | S1; CAP-25.a; DEC-448 |
| `test_w1_27_doctor_r6.py::test_own_prefix_wins_over_other_entrys_prefix` | 1 | tool-c under both prefixes: own prefix's 3.0.0 is ok, found and named | DEC-452 |
| `test_w1_27_doctor_r6.py::test_tool_absent_from_all_prefixes_found_on_path` | 1 | python3 999.999.999 under no prefix: found_version from PATH, entry not ok | S1, F1; DEC-452 |
| `test_w1_27_doctor_r6.py::test_tool_found_under_another_entrys_prefix` | 1 | prefix-less python3 found under tool-a's prefix at 42.42.42: ok, found_version, location | S1; CAP-25.a; DEC-448, DEC-452 |
| `test_w1_27_doctor_r6.py::test_tool_no_version_hash_match_ok` | 1 | exit-1 fake, matching sha: ok and sha256_match true | DEC-452 |
| `test_w1_27_doctor_r6.py::test_tool_no_version_no_hash_not_ok` | 1 | exit-1 fake, wrong sha: not ok, has reason, tools status not pass | F1; DEC-440, DEC-452 |
| `test_w1_27_doctor_r6.py::test_tool_version_mismatch_fails_despite_hash_match` | 1 | fake 9.9.9 pinned 1.0.0, matching sha: not ok, sha256_match true | F1; DEC-440 |
| `test_w1_27_doctor_r6.py::test_tool_version_raises_no_hash_not_ok` | 1 | self-killing fake, wrong sha: entry not ok | DEC-440, DEC-452 |
| `test_w1_27_doctor_r7.py::test_distribution_package_sha256_match_not_true` | 1 | pyyaml 6.0.1 with the .deb hash: ok true, sha256_match not true | DEC-425, DEC-452 |
| `test_w1_27_doctor_r7.py::test_python_package_right_version_ok` | 1 | pyyaml pinned 6.0.1: entry ok | DEC-452 |
| `test_w1_27_doctor_r7.py::test_python_package_wrong_version_not_ok` | 1 | pyyaml pinned 99.99.99: not ok; tools status not pass | F1; DEC-452 |
| `test_w1_27_doctor_r7.py::test_vendored_folder_absent_not_ok` | 1 | vendor folder removed: not ok, sha256_match not true | DEC-452 |
| `test_w1_27_doctor_r7.py::test_vendored_folder_right_content_passes` | 1 | pin = the case's own DEC-199 digest: sha256_match and ok true | DEC-199, DEC-452 |
| `test_w1_27_doctor_r7.py::test_vendored_folder_wrong_content_has_reason` | 1 | same input: entry gives a reason | DEC-452 |
| `test_w1_27_doctor_r7.py::test_vendored_folder_wrong_content_sha256_match_false` | 1 | superpowers folder replaced, pin 000…: sha256_match not true, not ok | F1; DEC-452, DEC-425, DEC-199 |
| `test_w1_27_doctor_unmeasured_r3.py::test_doctor_canary_error_is_fail` | 1 | copy's canary module raises on import: canaries status "fail" | S1; DEC-425, DEC-440 |
| `test_w1_27_doctor_unmeasured_r3.py::test_doctor_index_freshness_error_is_fail` | 1 | corrupt .gov-runtime/store.db: index_freshness status "fail" | S1; DEC-416, DEC-425, DEC-440 |
| `test_w1_27_doctor_unmeasured_r3.py::test_doctor_isolation_broken_git_is_fail` | 1 | _check_isolation` on a folder with .gov-runtime, no git: status "fail" | S1; DEC-425 |
| `test_w1_27_doctor_unmeasured_r3.py::test_unmeasured_absence_prevents_adopted_healthy` | 1 | all systems minimal, a capability on, registry removed: an unmeasured section and level not ADOPTED_HEALTHY | S5; CAP-54.a; DEC-416 |
| `test_w1_27_path_compliance_r2.py::test_historical_excluded_nonzero_when_historical_holds_old_path` | 1 | register, SOURCES.md and a cli/ file name the old path: historical_excluded ≥ 3 | DEC-456, DEC-448 |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_old_cli_tree_is_not_reported` | 1 | reference under cli/: "old_cli_mod" absent | DEC-456 |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_sources_md_is_not_reported` | 1 | moved module named in docs/SOURCES.md: "old_sources_mod" absent from doctor JSON | S3; CAP-06.d; DEC-456 |
| `test_w1_27_rebuild.py::test_two_rebuilds_give_the_same_digest` | 1 | two rebuilds ok with equal result digests | S2; CAP-20.a, CAP-46.a |
| `test_w1_27_rebuild_r2.py::test_rebuild_recreates_lexical_index` | 1 | rebuild exit 0; store.db holds the three lexical tables | S2; CAP-07.a; DEC-440 |
| `test_w1_27_rebuild_r3.py::test_rebuild_does_not_hold_lexical_schema_copy` | 1 | rebuild/command.py has no _LEXICAL_SCHEMA and no CREATE TABLE lexical_ line | S2; DEC-416 |
| `test_w1_27_rebuild_r3.py::test_rebuild_lexical_index_is_fresh` | 1 | after rebuild, freshness(root) is "fresh" | S2; CAP-07.a; DEC-416 |
| `test_w1_27_rebuild_r3.py::test_rebuild_lexical_search_finds_tracked_text` | 1 | after rebuild, a search for a unique marker is available with hits | S2; CAP-07.a; DEC-416 |
| `test_w1_27_rebuild_r4.py::test_rebuild_codeintel_is_recreated_when_tool_answers` | 1 | with codebase-memory-mcp and gitleaks on PATH, codeintel status "recreated" | DEC-440 |
| `test_w1_27_rebuild_r4.py::test_rebuild_lexical_digest_matches_owner_refresh` | 1 | lexical digest after rebuild equals the digest after the owner's refresh on an identical project | S2; DEC-440 |
| `test_w1_27_rebuild_r4.py::test_rebuild_secret_file_not_in_lexical_index` | 1 | planted secret: no lexical hit; secret_holder.py not indexed | S2; CAP-03.a; DEC-440 |
| `test_w1_27_rebuild_r4.py::test_rebuild_stores_hold_no_secret` | 1 | stores_with_secrets finds nothing after rebuild | S2; DEC-440, DEC-853 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_idempotent_digest` | 1 | two rebuilds without a map: equal digests | CAP-20.a; DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_lexical_not_built` | 1 | lexical not_recreated with a reason naming path map, indexable or classification | DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_no_traceback` | 1 | no "Traceback" on stderr | DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_record_store_outcome` | 1 | result digest is a non-empty string | DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_returns_envelope` | 1 | written against a KeyError crash (r5:73-81); its ok true and exit 0 (:84-90) follow W1-07's 'a missing path map is not … | DEC-440, DEC-185 |
| `test_w1_27_rebuild_r5.py::test_rebuild_no_path_map_writes_only_act_paths` | 1 | tree, sandbox home and elsewhere unchanged after rebuild | CAP-27.a; DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_owner_raises_gives_error_envelope` | 1 | corrupt store.db: error envelope, non-zero exit, an error code | DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_owner_raises_no_traceback` | 1 | no "Traceback" on stderr | DEC-440 |
| `test_w1_27_rebuild_r5.py::test_rebuild_owner_raises_writes_only_act_paths` | 1 | corrupt store: tree, home, elsewhere unchanged | DEC-440 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_a_rebuild_without_the_argument_asks_the_endpoint_as_today` | 1 | full rebuild asks the stand-in; semantic not_recreated; no mode named; requested not false | DEC-530; CAP-46.a; DEC-798 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_a_retrieval_on_a_store_rebuilt_without_embeddings_says_so` | 1 | the facet not available, the stopping reason, no semantic route (_honest_bundle, r8:284-302); the README's 'the … | DEC-530 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_a_retrieval_on_a_store_whose_vectors_could_not_be_built_says_so` | 1 | full rebuild at a model-less stand-in, then retrieve: semantic unavailable with reason, lexical cites the note | DEC-530, DEC-342, DEC-798 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_asks_the_endpoint_nothing_and_starts_no_program` | 1 | --no-embeddings: no request reaches the stand-in; its program never starts | DEC-530 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_builds_everything_else_a_rebuild_builds` | 1 | twin clone: full vs mode give same digest, lexical recreated, same codeintel status and stores, no vectors | DEC-530; CAP-46.a |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_says_the_semantic_store_was_not_built_because_it_was_not_asked_for` | 1 | semantic not_recreated, requested false, reason names --no-embeddings, not unavailable/ollama | DEC-530 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_starts_no_program_when_the_endpoint_is_down` | 1 | stand-in closed: the mode does not start the program | DEC-530 |
| `test_w1_27_rebuild_r8_no_embeddings.py::test_two_rebuilds_in_the_mode_give_the_same_digest` | 1 | two mode rebuilds give equal digests | DEC-530; CAP-46.a |
| `test_w1_27_recovery_check.py::test_derived_state_deleted_and_rebuilt_gives_same_digest` | 1 | rebuild, delete .gov-runtime, rebuild: equal digests | S4; CAP-38.b, CAP-20.a |
| `test_w1_27_recovery_check.py::test_recovery_rebuild_check_declaration_exists` | 1 | a recovery-rebuild* file exists under template/governance/kernel/checks | S4; CAP-38.b |
| `test_w1_27_recovery_check.py::test_recovery_rebuild_check_has_correct_family` | 1 | family line normalises to recovery-rebuild | S4; CAP-38.b; DEC-436 |
| `test_w1_27_recovery_check.py::test_recovery_rebuild_check_has_id` | 1 | declaration has an id line | S4 |
| `test_w1_27_recovery_check.py::test_recovery_rebuild_check_is_listed` | 1 | gov check --list --json` envelope contains "recovery-rebuild" | S4; CAP-38.b |
| `test_w1_27_schema.py::test_absent_system_without_reason_is_invalid` | 1 | absent system without reason: CONFIG_INVALID mentioning reason, constitution or system | S8 |
| `test_w1_27_schema.py::test_code_intelligence_enabled_without_languages_is_invalid` | 1 | enabled without languages: CONFIG_INVALID mentioning languages or code_intelligence | S8; DEC-265 |
| `test_w1_27_schema.py::test_missing_policy_key_is_invalid` | 1 | security removed: CONFIG_INVALID mentioning security or policies | S8 |
| `test_w1_27_schema.py::test_missing_required_top_level_key_names_the_key` | 4 | each of state_class/capabilities/policies/systems removed: CONFIG_INVALID, exit 1, key named | S8; DEC-189, DEC-228 |
| `test_w1_27_schema.py::test_missing_system_is_invalid` | 1 | skills removed: CONFIG_INVALID mentioning skills or systems | S8 |
| `test_w1_27_schema.py::test_namespace_missing_required_field_is_invalid` | 1 | deletion_rebuild removed: CONFIG_INVALID mentioning namespace or the field | S8 |
| `test_w1_27_schema.py::test_repairing_the_key_clears_the_error` | 1 | invalid map, then valid map: CONFIG_INVALID, then status ok | S8; DEC-189 |
| `test_w1_27_schema.py::test_valid_w1_08_path_map_with_code_intelligence_loads` | 1 | code_intelligence enabled with languages: status ok | S8; DEC-265 |
| `test_w1_27_schema_compat_r2.py::test_doctor_does_not_crash_on_minimal_path_map` | 1 | a namespaces-only map gives no CONFIG_INVALID (schema_compat_r2.py:69-77): DEC-228's rule that a minimal map loads for … | DEC-228 |
| `test_w1_27_schema_compat_r2.py::test_status_accepts_minimal_path_map_with_only_namespaces` | 1 | namespaces-only map: if status errs, the code is not CONFIG_INVALID | DEC-185, DEC-228; DEC-499 P-B (line 5481) |

**W1-32**: W1-32 (DAEO-8goq); 56 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_32_added_cases.py::test_a_failed_removal_keeps_the_sessions_exit_code_when_stderr_cannot_be_written` | 3 | With stderr closed or its reader gone, a failed removal still ends with the session's code (7 or 0) | S1; DEC-392 (L4056), DEC-332 (L3312) |
| `test_w1_32_added_cases.py::test_a_placeholder_device_at_the_flags_path_is_never_a_plain_not_paused` | 1 | A device at the flag's path: pause says paused, or holds a read:false entry | S3, F2; DEC-402 (L4190), DEC-311 (L3085), DEC-449 … |
| `test_w1_32_added_cases.py::test_a_placeholder_device_is_not_reported_as_an_empty_file_is` | 1 | The pause part for a device differs from the part for an empty file | S3; DEC-402 |
| `test_w1_32_added_cases.py::test_a_project_whose_records_all_load_keeps_its_clean_list_of_packages` | 1 | When every record loads: no read:false in packages, and they are DP-9101 and DP-9102 | S2, F2; DEC-308 |
| `test_w1_32_added_cases.py::test_a_record_the_load_cannot_take_is_not_hidden_behind_a_clean_list_of_packages` | 2 | A committed package the load lists as invalid makes the packages part hold read:false and name the file | F2; DEC-239 (L2286), DEC-308 (L3066), DEC-449 |
| `test_w1_32_added_cases.py::test_a_store_without_its_records_or_edges_leaves_the_ready_and_blocked_tickets_not_read` | 2 | With the records or edges table dropped, ready and blocked are read:false with reasons | S2, F2; DEC-449, DEC-454 (L4964) |
| `test_w1_32_added_cases.py::test_the_mirror_still_answers_beside_a_placeholder` | 1 | After `gov pause`, then a device at the flag path, status never says not paused | S3; DEC-429 |
| `test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` | 1 | The help's commands are exactly the twelve plus ci, launch and telemetry; lock is not among them | S5 [CAP-28.a]; DEC-542, DEC-546, DEC-569 |
| `test_w1_32_launch.py::test_a_failed_removal_keeps_the_sessions_exit_code` | 2 | A session that leaves a read-only folder ends 0 or 7; `gov launch` ends with that same code | S1; DEC-392, DEC-332 |
| `test_w1_32_launch.py::test_a_failed_removal_prints_no_envelope` | 1 | No LAUNCH_REFUSED, empty stdout, exactly one session | S1; DEC-332 |
| `test_w1_32_launch.py::test_a_failed_removal_writes_one_line_to_stderr_that_names_the_folder` | 2 | No traceback; exactly one non-empty stderr line, and it names the folder that stayed | S1; DEC-392 |
| `test_w1_32_launch.py::test_an_interrupt_of_the_launcher_alone_ends_the_session` | 1 | SIGINT to the launcher ends the session and removes the folder | S1; DEC-392 |
| `test_w1_32_launch.py::test_the_exit_code_after_the_signal_is_130` | 3 | After SIGINT, SIGTERM or SIGHUP the launcher's exit code is 130 | S1; DEC-392 |
| `test_w1_32_launch.py::test_the_signal_ends_the_session` | 2 | SIGTERM or SIGHUP to the launcher alone: the session's process is gone within 5 s | S1; DEC-392 |
| `test_w1_32_launch.py::test_the_signal_removes_the_temp_folder` | 2 | After SIGTERM or SIGHUP the temp folder is gone and TMPDIR lists as before | S1; DEC-392, DEC-386 (L3906) |
| `test_w1_32_status_not_read.py::test_a_change_that_holds_no_specification_record_is_shown` | 1 | A change with no specification record appears in the readiness text | S2, F2 |
| `test_w1_32_status_not_read.py::test_a_flag_that_cannot_be_read_is_never_reported_as_not_paused` | 2 | A directory or an unreadable file at the flag's path: paused true or read:false | S3; DEC-402 |
| `test_w1_32_status_not_read.py::test_a_package_opened_after_the_store_was_loaded_is_not_hidden` | 1 | a store older than HEAD makes the packages part not read (status/command.py, _store_fault and _packages), so the … | F2; DEC-308, DEC-449 |
| `test_w1_32_status_not_read.py::test_a_specification_whose_readiness_cannot_be_read_is_shown_as_such` | 1 | A spec with non-YAML readiness is listed, not closed, with a reason; the other spec stays closed | S2, F2; DEC-449 |
| `test_w1_32_status_not_read.py::test_a_store_that_is_no_database_is_not_read_either` | 1 | A store file that is no database: packages and ready are read:false | F2; DEC-449 |
| `test_w1_32_status_not_read.py::test_a_ticket_file_that_cannot_be_read_is_reported_and_not_left_out` | 1 | A ticket with broken frontmatter is named with a read:false entry and is not ready | S2, F2; DEC-449, DEC-454 |
| `test_w1_32_status_not_read.py::test_an_open_specification_shows_every_open_row_linked_or_not` | 1 | SPEC-zs02 shows rows 7 and 20 open, with TST-g101 and UNLINKED | S2, F2; DEC-089 |
| `test_w1_32_status_not_read.py::test_every_open_package_is_listed_however_many` | 1 | Twelve open packages are all listed, in order | S2; CAP-34.c |
| `test_w1_32_status_not_read.py::test_the_parts_that_can_be_read_are_still_given_without_the_store` | 1 | Without the store: both specs listed, paused false, doctor has healthy | S2, F2 |
| `test_w1_32_status_not_read.py::test_without_the_store_the_decision_packages_are_not_read` | 1 | Without the store, packages is read:false and its reason names the store | F2; DEC-308, DEC-449 |
| `test_w1_32_status_not_read.py::test_without_the_store_the_ready_tickets_are_not_read` | 1 | Without the store, tickets or its ready list is read:false with a reason | S2, F2; DEC-449 |
| `test_w1_32_status_parts.py::test_a_claimed_ticket_is_listed_with_its_holder` | 1 | TST-s006 is claimed by engineer:w1-32-session-a | S2; DEC-292 |
| `test_w1_32_status_parts.py::test_a_ready_ticket_is_not_listed_as_blocked_and_a_closed_ticket_nowhere` | 1 | TST-s001 is not blocked; closed TST-s007 is in no list | S2 |
| `test_w1_32_status_parts.py::test_a_ticket_in_progress_is_listed_as_claimed` | 1 | In-progress TST-s005 is claimed; TST-s001 is not | S2 |
| `test_w1_32_status_parts.py::test_an_empty_project_is_answered_too` | 1 | On an empty project the ticket lists, packages and readiness are empty lists | S2 |
| `test_w1_32_status_parts.py::test_an_open_package_names_the_tickets_that_wait_on_it` | 1 | DP-9101's entry names TST-s003 | S2, F2; DEC-308 |
| `test_w1_32_status_parts.py::test_an_unhealthy_doctor_is_shown_with_the_part_that_failed` | 1 | A path map that classifies nothing: the summary is unhealthy, names path_map, and ready stays non-empty | S2 |
| `test_w1_32_status_parts.py::test_every_specification_is_listed_with_its_verdict` | 1 | SPEC-zs01 is closed and SPEC-zs02 is not | S2 |
| `test_w1_32_status_parts.py::test_every_ticket_that_is_not_closed_is_in_a_list` | 1 | The union of the three lists is every ticket that is not closed | S2 |
| `test_w1_32_status_parts.py::test_the_answer_has_the_six_parts` | 1 | Status succeeds with exit 0 and names the six parts | S2 |
| `test_w1_32_status_parts.py::test_the_blocked_tickets_are_listed_each_with_its_reasons` | 1 | Every READY-rule blocked ticket is listed; TST-s003 and TST-s004 carry their reasons | S2; DEC-308 |
| `test_w1_32_status_parts.py::test_the_doctor_summary_gives_doctors_verdict` | 1 | Status's doctor.healthy equals a separate `gov doctor --json` verdict | S2; W1-27 |
| `test_w1_32_status_parts.py::test_the_doctor_summary_names_every_part_that_did_not_pass` | 1 | Every doctor part that did not pass, and each such state, appears in the summary | S2 |
| `test_w1_32_status_parts.py::test_the_governance_share_is_not_measured_and_says_why` | 1 | Telemetry refuses with "not measured"; the share says it, carries that reason, holds no number | S2; DEC-491 (L5384), DEC-540 (L5885) |
| `test_w1_32_status_parts.py::test_the_ready_tickets_are_those_of_the_ready_rule` | 1 | ready equals gov.tasks' READY list, pinned to TST-s001 and TST-s002 | S2; W1-09 |
| `test_w1_32_status_parts.py::test_the_verdict_is_the_readiness_checkers` | 1 | Per spec, closed, profile and open rows equal `gov readiness --specification | S2; W1-13 |
| `test_w1_32_status_pause.py::test_a_flag_removed_by_hand_with_its_mirror_left_is_not_reported_as_not_paused` | 1 | Paused, flag deleted, mirror left: paused not false | S3; DEC-429 |
| `test_w1_32_status_pause.py::test_a_paused_project_names_who_paused_it` | 2 | A pause by the owner or the orchestrator: the pause part names who | S3; DEC-404 (L4249) |
| `test_w1_32_status_pause.py::test_a_paused_project_says_so` | 1 | After the owner's `gov pause`: paused true | S3; DEC-364, DEC-429 |
| `test_w1_32_status_pause.py::test_a_paused_project_still_reports_its_other_parts` | 1 | Ready and packages ids are the same before and after a pause | S3, S2 |
| `test_w1_32_status_pause.py::test_a_project_that_is_not_paused_says_so` | 1 | No flag: paused false | S3; DEC-364 (L3707) |
| `test_w1_32_status_pause.py::test_an_empty_file_at_the_flags_path_is_no_pause` | 1 | An empty flag file: paused false | S3; DEC-402 |
| `test_w1_32_status_pause.py::test_the_pause_state_is_the_projects_own` | 1 | With one of two projects paused, each `--root` status run from elsewhere answers its own state | S3; DEC-429 |
| `test_w1_32_status_read_only.py::test_repeated_status_gives_the_same_answer_and_writes_nothing` | 1 | Two runs give equal answers; state unchanged | S4, F1 |
| `test_w1_32_status_read_only.py::test_status_leaves_a_dev_tier_clone_clean` | 1 | On a clone of the dev tier: six parts, porcelain empty, state unchanged | S4 [CAP-27.a] |
| `test_w1_32_status_read_only.py::test_status_leaves_uncommitted_work_as_it_was` | 1 | With uncommitted edits present, the full state is unchanged | S4, F1 |
| `test_w1_32_status_read_only.py::test_status_of_a_paused_project_changes_neither_the_flag_nor_its_mirror` | 1 | A paused project reads paused; flag, mirror and all state unchanged | S4, S3 |
| `test_w1_32_status_read_only.py::test_status_takes_no_claim_and_releases_none` | 1 | Claim locks and the holder are unchanged by status | S4; DEC-292 |
| `test_w1_32_status_read_only.py::test_status_with_root_writes_neither_in_the_project_nor_where_it_runs` | 1 | --root` run from elsewhere: state unchanged | S4, F1 |
| `test_w1_32_status_read_only.py::test_status_writes_no_store_where_none_is` | 1 | Without .gov-runtime/, status creates none and changes nothing | S4, F1 |
| `test_w1_32_status_read_only.py::test_status_writes_nothing_anywhere` | 2 | Porcelain, ignored files, refs, every file including .gov-runtime, HOME, TMPDIR and elsewhere unchanged | S4, F1 [CAP-27.a] |

**W1-33**: W1-33 (DAEO-xog0); 30 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_33_agent_definitions.py::test_a_definition_without_one_required_field_is_found` | 5 | an oracle check of the suite's reader on each role's definition: with each of the six fields taken out in turn, the … | W1-33 KPI F1, on the definition; DEC-066 |
| `test_w1_33_agent_definitions.py::test_the_definition_agrees_with_its_kernel_role_file` | 5 | AG and RF hold the same labelled fields with the same text | S4, DEC-066 (DP-1) |
| `test_w1_33_agent_definitions.py::test_the_definition_has_the_six_fields` | 5 | AG has the six required fields, each with text | S1 [CAP-22.a], MR-5, DEC-066 |
| `test_w1_33_agent_definitions.py::test_the_definition_is_no_longer_the_minimal_one` | 5 | an absence check: no definition is still W1-05's minimal one (agent_definitions.py:40-41) | S4 [CAP-22.a], DEC-119, DEC-154 |
| `test_w1_33_agent_definitions.py::test_the_definition_keeps_the_subagent_type_name_of_the_role` | 5 | name equals the role (agent_definitions.py:47-48), what the case is named for; its description half (:49) cannot fail … | S4, DEC-117 |
| `test_w1_33_agent_definitions.py::test_the_definition_states_what_the_kpis_require_of_the_role` | 5 | role_faults on AG: fields, acceptance pattern, classes, scope, read-only auditor, network | S1-S3, CAP-58.b, DEC-083, DEC-156, DEC-158 |
| `test_w1_33_agent_definitions.py::test_there_is_one_definition_per_role_and_the_research_one` | 1 | the names under .claude/agents are exactly the five and research, once each | S4, DEC-163 |
| `test_w1_33_guard_and_launcher.py::test_an_install_asks_for_the_orchestrator_and_is_denied_to_every_other_role` | 5 | pip install requests` gives ask for the orchestrator, deny for the other four | S2, DEC-083, DEC-120 |
| `test_w1_33_guard_and_launcher.py::test_only_the_test_designer_may_write_the_acceptance_tests` | 5 | under the planted PG-2 (the acceptance rule removed from decide.py's allowed paths and path check) its [orchestrator] … | S2, F2, MR-3, DEC-069 |
| `test_w1_33_guard_and_launcher.py::test_the_launcher_gives_the_role_an_empty_network_profile` | 3 | the settings built for engineer, designer and auditor hold allowedDomains [] | S3 [CAP-58.b], DEC-158 |
| `test_w1_33_guard_and_launcher.py::test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker` | 1 | gov launch orchestrator` is refused with "worker role" and starts no CLI | S3, DEC-161 |
| `test_w1_33_guard_and_launcher.py::test_the_orchestrator_may_write_anywhere_else_in_the_repository` | 1 | the orchestrator's Writes to README, decide.py, docs/notes.md and RO are allowed | S4, DEC-156, DEC-178 |
| `test_w1_33_kernel_role_files.py::test_a_required_field_with_no_text_is_found` | 5 | an oracle check of the same reader (:175-176) | F1 |
| `test_w1_33_kernel_role_files.py::test_a_role_file_without_one_required_field_is_found` | 5 | an oracle check of the suite's own reader (kernel_role_files.py:165-170), which the six-fields cases stand on | F1 |
| `test_w1_33_kernel_role_files.py::test_an_implementer_pattern_that_covers_the_acceptance_tests_is_found` | 4 | an oracle check of the suite's checker (:189-192), which test_no_other_pattern_includes_the_acceptance_tests applies to … | F2 |
| `test_w1_33_kernel_role_files.py::test_the_auditor_is_read_only_except_its_ticket_s_report_path` | 1 | the field says read-only and names report and ticket | S2, DEC-112 |
| `test_w1_33_kernel_role_files.py::test_the_orchestrator_role_file_states_its_write_scope` | 1 | anywhere, except tests/acceptance/** | S4, DEC-156 |
| `test_w1_33_kernel_role_files.py::test_the_research_exception_is_stated_by_the_research_role_file_alone` | 1 | research's Tools field says "experiment folder" and DEC-163 | S2, DEC-163 |
| `test_w1_33_kernel_role_files.py::test_the_research_role_file_is_read_in_this_form` | 1 | the suite's reader finds six fields in research.md | S1 (form) |
| `test_w1_33_kernel_role_files.py::test_the_research_role_file_is_unchanged` | 1 | research.md is the file W1-46 placed (kernel_role_files.py:151-155); the revised plan widens W2-11 to the role files' … | S5, DEC-163 |
| `test_w1_33_kernel_role_files.py::test_the_research_role_file_names_the_research_allowlist` | 1 | research's Network field names launcher and allowlist | S3, DEC-163 |
| `test_w1_33_kernel_role_files.py::test_the_role_has_a_kernel_role_file_with_the_six_fields` | 5 | RF exists with the six fields, each with text | S1 [CAP-22.a] |
| `test_w1_33_kernel_role_files.py::test_the_role_maps_the_classes_as_the_contract_says` | 5 | each class has the disposition CAP-58.b and DEC-083 give; network/db/cloud/CI/deploy denied for launched workers | S3, DEC-083, DEC-074 Q9, DEC-158 |
| `test_w1_33_kernel_role_files.py::test_the_test_designer_pattern_includes_the_acceptance_tests` | 1 | the designer's Allowed paths field contains tests/acceptance/** | S2, MR-3 |
| `test_w1_33_roster.py::test_a_launched_worker_s_entry_names_its_session_and_the_empty_profile` | 3 | session `gov launch <role> <ticket>`; profile holds "empty" | S3, DEC-158 |
| `test_w1_33_roster.py::test_a_role_the_launcher_does_not_start_has_no_launched_session` | 1 | the orchestrator entry names no `gov launch` session | S3, DEC-161, DEC-386 |
| `test_w1_33_roster.py::test_every_ticket_s_role_is_in_the_roster` | 1 | every ticket's role is a roster key | S1, MR-5 |
| `test_w1_33_roster.py::test_the_entry_names_the_role_s_kernel_role_file_and_its_definition` | 5 | role_file and agent paths as expected; the role file exists | S1 |
| `test_w1_33_roster.py::test_the_research_entry_is_unchanged` | 1 | the research entry and its five lines are W1-46's | S5, DEC-163 |
| `test_w1_33_roster.py::test_the_roster_holds_the_five_roles_and_research_and_no_other` | 1 | the roles keys are exactly the six | S1, DEC-066, DEC-163 |

**W1-34**: W1-34 (DAEO-egm9); 7 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_34_decision_package.py::test_a_package_cannot_be_rendered_without_a_recommendation_or_confidence` | 1 | the LITE design has no renderer (README:95-98, reading 1): the template's own sections and their 'required' wording are … | F1; DEC-220 (the scale) |
| `test_w1_34_decision_package.py::test_an_answer_cannot_be_recorded_without_a_date` | 1 | every ACCEPTED (…) form has a date slot and the Answer section says the date is required (:118-127), the LITE form of … | F2 |
| `test_w1_34_decision_package.py::test_an_answer_maps_to_a_decision_record_with_accepted_and_who` | 1 | The Answer section names a DEC or ADR id and an `ACCEPTED (who, …)` form; so does the record template | S3; DEC-220 |
| `test_w1_34_decision_package.py::test_batching_allows_at_most_five_open_packages_and_p1_may_bypass` | 1 | reads the cap's own paragraph ('at most five', with 'open' in the same block) and a P1 paragraph that says bypass … | S2 [CAP-34.c]; DEC-093 |
| `test_w1_34_decision_package.py::test_the_gate_record_carries_a_state_and_its_cit` | 1 | the template's status and constrains in its frontmatter, the gate states named, a cit key in a gate record's … | S4 [CAP-34.d]; DEC-308 |
| `test_w1_34_decision_package.py::test_the_gate_state_lives_in_status_alone_and_the_cit_key_is_cit` | 1 | Each status value stands next to its state word; no second state key; the CIT key is `cit | S4; DEC-328 |
| `test_w1_34_decision_package.py::test_the_template_has_the_ten_fields_and_a_rank` | 1 | reads the template's headings, its frontmatter rank and the ranks named (decision_package.py:17-25) | S1 [CAP-34.b]; MR-6, DEC-065 |

**W1-35**: W1-35 (DAEO-0i6h); 76 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_35.py::TestCITWorkflow::test_change_skill_mentions_cit_p_and_cit_e` | 1 | a mention is all it claims (test_w1_35.py:211-214); the CIT steps are other cases' | S7 [CAP-33.d] |
| `test_w1_35.py::TestCITWorkflow::test_change_skill_refuses_archive_without_records` | 1 | a word check ('rejects' and 'cit-e'); the word stands on one line of the skill only, the rule's own, so removing the … | CAP-33.d |
| `test_w1_35.py::TestCheckDeclaration::test_check_declaration_exists` | 1 | skill-regression-a*.yaml exists | S8 [CAP-38.b] |
| `test_w1_35.py::TestCheckDeclaration::test_check_declaration_family_is_skill_regression` | 1 | family is "skill regression" | S8, DEC-436 |
| `test_w1_35.py::TestCheckDeclaration::test_check_declaration_has_five_fields` | 1 | the five fields are strings | S8, DEC-439 |
| `test_w1_35.py::TestCheckDeclaration::test_check_declaration_severity_valid` | 1 | severity hard-block or warning | S8 |
| `test_w1_35.py::TestCheckDeclaration::test_check_declaration_valid_yaml` | 1 | it is a YAML mapping | S8 |
| `test_w1_35.py::TestCitations::test_skill_cites_at_least_one_reference` | 4 | at least one CAP/DEC/MR id | S5 |
| `test_w1_35.py::TestDecisionPackages::test_discovery_cites_dec093_or_cap34` | 1 | a citation check: the skill cites the decision, which is all it claims | S2 |
| `test_w1_35.py::TestDecisionPackages::test_discovery_mentions_p1_p3_ranking` | 1 | P1, P2 and P3 stand(s) on the rule's own line only, so the rule cannot go and leave them; a reversal that keeps the … | S2 |
| `test_w1_35.py::TestDecisionPackages::test_discovery_p1_bypass` | 1 | a word check ('bypass' or 'override'); the word stands on one line of the skill only, the rule's own, so removing the … | CAP-34.c |
| `test_w1_35.py::TestDeclarationCommand::test_command_has_no_fallback` | 1 | no "\ | \ |
| `test_w1_35.py::TestDeclarationCommand::test_command_is_not_true` | 1 | command is not "true" | S8, DEC-425 |
| `test_w1_35.py::TestDeclarationCommand::test_command_referenced_paths_exist` | 1 | the named folders exist | S8 |
| `test_w1_35.py::TestDeclarationCommand::test_command_references_all_four_skill_folders` | 1 | the four folders are named | S8 |
| `test_w1_35.py::TestDeclarationCommand::test_command_runs_skill_validator` | 1 | the command runs gov.check.skill_validator | S8, DEC-439 |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_cit_p_for_closed_spec` | 1 | a word check ('CIT-P'); the word stands on one line of the skill only, the rule's own, so removing the rule fails the … | CAP-32.c, CAP-33.e |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_cites_dec102_or_cap32` | 1 | a citation check: the skill cites the decision, which is all it claims | S9 |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_normal_cycle_promotion` | 1 | a word check ('promoted' or 'normal cycle'); the word stands on one line of the skill only, the rule's own, so removing … | CAP-32 |
| `test_w1_35.py::TestDiscoveryExperiments::test_discovery_sandbox_requirement` | 1 | a word check ('sandbox'); the word stands on one line of the skill only, the rule's own, so removing the rule fails the … | CAP-32 |
| `test_w1_35.py::TestEvidenceTriggeredChange::test_change_mentions_three_options` | 1 | apply, defer, re-baseline | S11 [CAP-33.e], DEC-105 |
| `test_w1_35.py::TestFrontmatterAndSize::test_body_within_2500_tokens` | 4 | body at most 2,500 tokens by the test's own counter | S1 |
| `test_w1_35.py::TestFrontmatterAndSize::test_description_within_60_tokens` | 4 | description at most 60 tokens | S1 |
| `test_w1_35.py::TestFrontmatterAndSize::test_frontmatter_has_required_fields` | 4 | name, version and description present | S1 |
| `test_w1_35.py::TestFrontmatterAndSize::test_frontmatter_is_valid_yaml` | 4 | the frontmatter of the four skills parses as a mapping | S1 [CAP-24.a] |
| `test_w1_35.py::TestFrontmatterAndSize::test_version_is_present_and_nonempty` | 4 | version non-empty | S1 |
| `test_w1_35.py::TestImpactAssessment::test_change_impact_triggered_by_question` | 1 | 'what is the impact' stand(s) on the rule's own line only, so the rule cannot go and leave it; a reversal that keeps … | S13 |
| `test_w1_35.py::TestNoPermissionGrants::test_no_permission_granting_language` | 4 | an absence check: no permission phrase without an id on its line; nothing matches today, so a new uncited phrase is … | S5 [CAP-24.b] |
| `test_w1_35.py::TestNoPermissionGrants::test_procedural_statements_cite_policy` | 4 | list lines with authority words cite an id (test_w1_35.py:131-151); only an item's first line is read | S5 |
| `test_w1_35.py::TestPlannedVsMisspeltCommands::test_planned_command_is_valid` | 1 | gov close draws no SKILL_UNKNOWN_COMMAND (test_w1_35.py:1003-1013); it passes without the skill-regression-a entry, a … | S8 |
| `test_w1_35.py::TestPlanningGapTickets::test_planning_cites_dec089_or_cap30` | 1 | a citation check: the skill cites the decision, which is all it claims | S3 |
| `test_w1_35.py::TestProbeFindings::test_test_design_cites_dec136_or_cap38` | 1 | a citation check: the skill cites the decision, which is all it claims | S12 |
| `test_w1_35.py::TestProbeFindings::test_test_design_specification_gap_reporting` | 1 | 'specification gap' stands only on the two lines that state the rule (test-design/SKILL.md:34, 40) | S12 |
| `test_w1_35.py::TestRoutingBatchingState::test_discovery_carries_batching_rules` | 1 | a word check ('batch'); the word stands on one line of the skill only, the rule's own, so removing the rule fails the … | CAP-34 |
| `test_w1_35.py::TestRoutingBatchingState::test_discovery_carries_state_rules` | 1 | a word check ('states'); the word stands on one line of the skill only, the rule's own, so removing the rule fails the … | CAP-34 |
| `test_w1_35.py::TestSkillRegressionGreen::test_skill_regression_green_with_well_formed_skills` | 1 | in an FT, GC reports the skill-regression family GREEN | S8 [CAP-38.b], DEC-439, DEC-521 |
| `test_w1_35.py::TestSkillRegressionRedBodyTooLong::test_red_when_body_exceeds_2500_tokens` | 1 | SKILL_BODY_TOO_LONG is the file's one finding (skill_validator.py:129-136); under the planted PS-4 (the bound raised to … | S8, F1 |
| `test_w1_35.py::TestSkillRegressionRedDescriptionTooLong::test_red_when_description_exceeds_60_tokens` | 1 | the same reasoning (skill_validator.py:120-127) | S8 |
| `test_w1_35.py::TestSkillRegressionRedMissingFolder::test_red_when_skill_folder_missing` | 1 | a removed folder gives RED (unmeasured) | S8, DEC-425 |
| `test_w1_35.py::TestSkillRegressionRedMissingFrontmatter::test_red_when_frontmatter_removed` | 1 | the family status only (test_w1_35.py:870-874), but the validator's one finding for that file … | S8 |
| `test_w1_35.py::TestSkillRegressionRedMissingVersion::test_red_when_version_missing` | 1 | the same reasoning: SKILL_MISSING_VERSION is the file's one finding (skill_validator.py:96-102), the green control the … | S8 |
| `test_w1_35.py::TestSkillRegressionRedUnknownCommand::test_red_when_unknown_gov_command` | 1 | the same reasoning (skill_validator.py:138-146) | S8 |
| `test_w1_35.py::TestTestDesignConstraints::test_change_audit_on_closed_spine` | 1 | DEC-088 and CAP-47 stand(s) on the rule's own line only, so the rule cannot go and leave them; a reversal that keeps … | S4 [CAP-47.d] |
| `test_w1_35_orchestration.py::TestBriefTemplates::test_no_brief_is_named_like_a_record_template` | 1 | no record word in names; no `type` in frontmatter | W1-08, W1-34 |
| `test_w1_35_orchestration.py::TestBriefTemplates::test_the_brief_has_a_placeholder_for_each_thing_it_is_filled_in_with` | 5 | placeholders for ticket, profile, paths, sources, decisions | S14 |
| `test_w1_35_orchestration.py::TestBriefTemplates::test_the_test_designers_brief_states_behaviour_and_sources_only` | 1 | reads one statement holding behaviour, source and only (statements_with) and the citation … | DEC-462 |
| `test_w1_35_orchestration.py::TestOrchestrationCheck::test_gov_check_runs_the_check_under_the_skill_regression_family` | 1 | GREEN under skill regression in a minimal project; RED without the skill | S14 |
| `test_w1_35_orchestration.py::TestOrchestrationCheck::test_the_declaration_has_the_form_of_the_existing_one` | 1 | family/tier/severity as skill-regression-a; its own id | S14 |
| `test_w1_35_orchestration.py::TestOrchestrationCheck::test_the_declared_command_runs_the_generic_validator_over_the_new_skill` | 1 | the validator runs over the folder; no "\ | \ |
| `test_w1_35_orchestration.py::TestOrchestrationCheck::test_the_delivered_skill_passes_the_generic_validator` | 1 | exit 0, no findings | S14 |
| `test_w1_35_orchestration.py::TestOrchestrationCheck::test_the_delivered_skill_with_a_body_over_the_bound_does_not_pass` | 1 | a grown copy gives exactly SKILL_BODY_TOO_LONG | F1 |
| `test_w1_35_orchestration.py::TestOrchestrationSkillAuthority::test_every_rule_in_a_list_is_stated_with_what_it_follows` | 1 | list items with authority words cite an id | CAP-24.b |
| `test_w1_35_orchestration.py::TestOrchestrationSkillAuthority::test_no_permission_is_granted_without_the_decision_it_follows` | 1 | permission-like lines carry an id | CAP-24.b |
| `test_w1_35_orchestration.py::TestOrchestrationSkillAuthority::test_the_skill_cites_a_policy_or_a_decision` | 1 | at least one id | S14 [CAP-24.b] |
| `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_the_body_is_within_2500_tokens` | 1 | at most 2,500 tokens | S14, DEC-539 |
| `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_the_description_is_within_60_tokens` | 1 | at most 60 tokens | S14 |
| `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_the_skill_has_a_versioned_frontmatter` | 1 | name orchestration; version and description non-empty strings | S14 [CAP-24.a] |
| `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_the_skill_names_the_five_brief_templates` | 1 | the five file names appear | S14 |
| `test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated` | 11 | the eight other rows hold rules in force; [the ticket loop] and [temp hygiene and protected files] are outdated and … | S14, DEC-537, DEC-539 and the row ids |
| `test_w1_35_orchestration.py::TestRulesyncSources::test_the_orchestrator_roles_rulesync_source_carries_the_role_files_body` | 1 | the template subagent body equals RF | S14 |
| `test_w1_35_orchestration.py::TestRulesyncSources::test_the_skills_rulesync_source_is_the_kernel_skill` | 1 | the template rulesync copy equals the kernel skill | S14 |
| `test_w1_35_orchestration.py::TestStatusRoute::test_a_part_marked_not_read_is_said_not_to_be_read` | 1 | "not read" there | S15 |
| `test_w1_35_orchestration.py::TestStatusRoute::test_a_skill_without_the_route_is_found` | 1 | the reader's negative control on a sample without the route (test_w1_35_orchestration.py:403-407), then the delivered … | S15 (failure) |
| `test_w1_35_orchestration.py::TestStatusRoute::test_a_status_question_is_routed_to_the_command` | 1 | reads the statement (_sections) and a citation (test_w1_35_orchestration.py:371-376) | S15 [CAP-28.a] |
| `test_w1_35_orchestration.py::TestStatusRoute::test_the_answer_is_never_given_from_recall` | 1 | recall with a never-word | S15 |
| `test_w1_35_orchestration.py::TestStatusRoute::test_the_route_names_the_parts_the_answer_is_given_from` | 1 | the seven parts named there | S15 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_roster_stays_at_the_same_roles` | 1 | six role files and six template subagents | S14 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_adds_no_labelled_field_to_the_role` | 1 | no bold-label item in the section | S14 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_cites_what_it_follows` | 1 | at least one id | S14 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_does` | 1 | starts workers or runs the loop | S14 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_is` | 1 | orchestrator, one ticket, worktree | S14, DEC-236 |
| `test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_may_not_do` | 1 | never merges, never edits tickets or the register, never pushes | S14 |
| `test_w1_35_orchestration.py::TestWave2Items::test_the_four_wave_2_items_stand_in_that_passage` | 1 | the four Wave 2 items are named there | DEC-537 |
| `test_w1_35_orchestration.py::TestWave2Items::test_the_skill_says_which_rules_no_mechanism_enforces_yet` | 1 | reads the passage itself (_passages) and the citation (test_w1_35_orchestration.py:184-189) | DEC-537 |
| `test_w1_35_orchestration.py::TestWording::test_tests_are_named_without_a_language_or_a_runner` | 1 | no pytest/python/.py/conftest/tests/acceptance | DEC-534 |
| `test_w1_35_orchestration.py::TestWording::test_this_repositorys_own_values_are_not_the_rule` | 1 | no repository ids, paths, model names or x.y.z versions | DEC-539 |

**W1-36**: W1-36 (DAEO-skiy); 52 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_contested_findings_become_decision_packages` | 1 | a word check ('contested' and 'package'); the word stands on one line of the skill only, the rule's own, so removing … | MR-4 |
| `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_references_cap_47` | 1 | a citation check: the skill cites the decision, which is all it claims | S6 |
| `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_the_session_is_fresh` | 1 | a word check ('fresh'); the word stands on one line of the skill only, the rule's own, so removing the rule fails the … | CAP-47.b |
| `test_w1_36_audit_skill.py::TestAuditReadOnly::test_the_skill_says_it_does_not_edit_audited_files` | 1 | 'read-only' and 'does not edit' stand(s) on the rule's own line only, so the rule cannot go and leave them; a reversal … | F2, MR-4 |
| `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_uses_the_six_classes` | 1 | the six class names | S2, DEC-070 |
| `test_w1_36_audit_skill.py::TestAuditReport::test_the_skill_cites_dec_088` | 1 | a citation check: the skill cites the decision, which is all it claims | S2 |
| `test_w1_36_audit_skill.py::TestAuditReportDEC441Form::test_describes_no_evidence_as_dash` | 1 | 'written as `-`' stand(s) on the rule's own line only, so the rule cannot go and leave it; a reversal that keeps the … | DEC-441 |
| `test_w1_36_audit_skill.py::TestAuditReportDEC441Form::test_describes_table_columns` | 1 | a word check ('evidence' and a table word); the word stands on one line of the skill only, the rule's own, so removing … | DEC-441 |
| `test_w1_36_audit_skill.py::TestAuditReportDEC441Form::test_mentions_pack_sha256_field` | 1 | 'pack_sha256' stand(s) on the rule's own line only, so the rule cannot go and leave it; a reversal that keeps the words … | DEC-441, DEC-446 |
| `test_w1_36_audit_skill.py::TestAuditWaveExit::test_wave_exit_covers_every_lite_feature_spec` | 1 | a word check ('wave exit' and 'lite'); the word stands on one line of the skill only, the rule's own, so removing the … | CAP-47 |
| `test_w1_36_check_declarations.py::TestAuditReproCommandValidation::test_command_calls_audit_validator` | 1 | calls gov.check.audit_validator | S5 |
| `test_w1_36_check_declarations.py::TestAuditReproCommandValidation::test_no_conditional_bypass_in_command` | 1 | no bypass words | DEC-439 |
| `test_w1_36_check_declarations.py::TestAuditReproCommandValidation::test_no_or_fallback_in_command` | 1 | no "\ | \ |
| `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_allows_not_applicable_value_is_true` | 1 | value "true" | DEC-447 |
| `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_severity_stays_hard_block` | 1 | severity hard-block | DEC-447 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_command_is_non_empty` | 1 | non-empty | S5 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_each_has_required_fields` | 1 | five keys | S5 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_family_is_a_known_family` | 1 | the same, for the audit-reproducibility declaration | DEC-436 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_family_normalises_to_audit_reproducibility` | 1 | normalises correctly | DEC-436 |
| `test_w1_36_check_declarations.py::TestAuditReproducibilityCheck::test_tier_is_g1` | 1 | G1 | S5 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_command_is_non_empty` | 1 | command non-empty | S5 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_each_has_required_fields` | 1 | five keys | S5, DEC-439 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_family_is_a_known_family` | 1 | the declaration's family is one of DEC-436's (w1_36 support :62-71): a misspelt family is seen | DEC-436 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_family_normalises_to_skill_regression` | 1 | normalises to skill-regression | DEC-436 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_tier_is_g1` | 1 | tier G1 | S5 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCommandValidation::test_command_calls_skill_validator` | 1 | calls gov.check.skill_validator | S5 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCommandValidation::test_no_conditional_bypass_in_command` | 1 | no if/test/importlib/find_spec/which | DEC-439 |
| `test_w1_36_check_declarations.py::TestSkillRegressionCommandValidation::test_no_or_fallback_in_command` | 1 | no "\ | \ |
| `test_w1_36_check_declarations.py::TestSkillRegressionNotApplicableAbsent::test_skill_regression_has_no_allows_not_applicable` | 1 | b* declarations lack the key | DEC-447 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_green_with_valid_report` | 1 | a valid DEC-441 report gives GREEN | S5, DEC-441 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_class_unknown` | 1 | an unknown class gives RED | DEC-441 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_commit_does_not_resolve` | 1 | an unknown commit gives RED | DEC-441 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_evidence_path_absent` | 1 | an absent evidence path gives RED | DEC-441 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_ok_row_has_no_evidence` | 1 | an OK row with `-` gives RED | DEC-441 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_one_valid_and_one_invalid_report` | 1 | one bad report gives RED and a hard block | DEC-447 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_alone_does_not_make_gov_check_fail` | 1 | run_checks reports no hard-block red | DEC-447 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_reason_says_not_applicable` | 1 | the reason holds "not applicable" | DEC-447 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_when_no_audit_report_folder_empty` | 1 | an empty folder gives YELLOW | DEC-447 |
| `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_when_no_audit_report_folder_missing` | 1 | no docs/audit gives YELLOW | DEC-447 |
| `test_w1_36_check_integration.py::TestSkillRegressionGovCheck::test_green_with_valid_skills` | 1 | the four live skills + b1 give a GREEN family | S5 |
| `test_w1_36_check_integration.py::TestSkillRegressionGovCheck::test_red_when_skill_broken` | 1 | retrieval without frontmatter gives RED | S5 |
| `test_w1_36_check_integration.py::TestSkillRegressionGovCheck::test_red_when_skills_missing` | 1 | no skills gives RED (unmeasured) | DEC-425 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_cites_dec_032` | 1 | a citation check: the skill cites the decision, which is all it claims | S1 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_references_cap_16` | 1 | a citation check: the skill cites the decision, which is all it claims | S1 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_references_cap_56` | 1 | a citation check: the skill cites the decision, which is all it claims | S1 |
| `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_says_subagents_are_disposable` | 1 | 'subagent' and 'disposable' stand only on the two body lines that state the rule (retrieval/SKILL.md:15, 27); planted … | S1, DEC-032 |
| `test_w1_36_skill_form.py::TestSkillAuthority::test_cites_at_least_one_governing_source` | 4 | at least one id | S4 |
| `test_w1_36_skill_form.py::TestSkillAuthority::test_no_permission_keys_in_frontmatter` | 4 | no role-only keys in the frontmatter | S4 [CAP-24.b] |
| `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_description_in_frontmatter` | 4 | description is a non-empty string | S3 |
| `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_name_in_frontmatter` | 4 | name is a non-empty string | S3 |
| `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_version_in_frontmatter` | 4 | the version key (skill_form.py:32-34); an empty version is the validator's SKILL_MISSING_VERSION … | S3 |
| `test_w1_36_skill_form.py::TestSkillTokenLimit::test_body_at_most_2500_tokens` | 4 | body at most 2,500 tokens | S3 |

**W1-37**: W1-37 (DAEO-yvzh); 4 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_37_skills.py::test_no_other_superpowers_skill_or_hook_is_present` | 1 | only the three SKILL.md files; only the record or LICENSE at the top | F1 |
| `test_w1_37_skills.py::test_no_vendored_file_differs_from_its_recorded_hash` | 1 | the record's sha256 equals the copy's digest by DEC-199's rule (test_w1_37_skills.py:104-112); its second half … | F2, DEC-199 |
| `test_w1_37_skills.py::test_the_three_skills_are_copied_from_v6_4_2_into_the_namespace_with_the_source_hash_recorded` | 1 | the copies are byte-identical to the vendor folder, no symlinks, v6.4.2, source digest matches | S1, DEC-244, DEC-245, DEC-246, DEC-199 |
| `test_w1_37_skills.py::test_the_token_sizes_are_measured_and_within_the_figures_and_no_plugin_hook_or_excluded_skill_is_there` | 1 | sizes within the ceilings and equal to the record; no plugin, hook or excluded skill | S2, DEC-247, DEC-074 Q5, DEC-076 |

**W1-38**: W1-38 (DAEO-3ef2); 93 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_38_heldout_step.py::TestBrokenHeldOutFile::test_broken_file_is_not_green_and_no_path_is_printed` | 7 | Seven broken held-out forms: check exits non-zero with at least one finding, no stand-in path on stdout or stderr | DEC-218, DEC-641, DEC-604 |
| `test_w1_38_heldout_step.py::TestHeldOutStepThroughGovCheck::test_gov_check_is_green_after_the_apply_procedure` | 1 | After the apply procedure gov check --json shows check and family GREEN, no stand-in path printed | DEC-635, DEC-641; CAP-38.b |
| `test_w1_38_heldout_step.py::TestHeldOutStepThroughGovCheck::test_gov_check_is_red_when_a_rule_is_lost` | 1 | One step rule removed: gov check RED/RED, findings name only the settings file, no path printed | DEC-635, DEC-641 |
| `test_w1_38_heldout_step.py::TestProjectWithoutAHeldOutFile::test_stray_read_deny_rule_is_red_on_the_settings` | 1 | The step's rules kept after the held-out file is removed: not green, only settings named | DEC-641, DEC-471 |
| `test_w1_38_heldout_step.py::TestSettingsAfterTheHeldOutStep::test_generated_then_the_step_is_green` | 1 | After rulesync generate and the held-out generator, the declared check exits 0, no finding, no stand-in path printed | KPI S3 [CAP-38.b]; DEC-162, DEC-218, DEC-635, … |
| `test_w1_38_heldout_step.py::TestSettingsAfterTheHeldOutStep::test_one_rule_lost_is_red_on_the_settings` | 1 | One of the step's two Read deny rules removed by hand: not green, only the settings file named | DEC-162, DEC-635, DEC-641 |
| `test_w1_38_heldout_step.py::TestSettingsAfterTheHeldOutStep::test_rule_the_held_out_file_does_not_give_is_red_on_the_settings` | 1 | A third Read deny rule in the generator's form, for a path the file does not name: not green, only settings named | DEC-162, DEC-635, DEC-641 |
| `test_w1_38_heldout_step.py::TestSettingsAfterTheHeldOutStep::test_step_never_run_is_red_on_the_settings` | 1 | Held-out file present, settings as rulesync alone writes them: not green, findings name only .claude/settings.json, no … | KPI S3 [CAP-38.b]; DEC-162, DEC-635, DEC-641 |
| `test_w1_38_heldout_step.py::TestStepRepeated::test_second_run_of_the_step_leaves_the_settings_as_they_are` | 1 | The held-out generator run twice leaves .claude/settings.json byte for byte the same | DEC-218, DEC-641 |
| `test_w1_38_heldout_step.py::TestStepRepeated::test_whole_procedure_repeated_is_still_green` | 1 | generate, step, generate, step: settings byte-identical to the first pass and the check green | DEC-641 |
| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_a_call_the_guard_refuses_from_the_root_is_refused_in_a_subfolder_too` | 1 | An out-of-scope write is refused by the guard's own answer (exit 0, deny) from root and src/app; file unchanged | DEC-603 |
| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded` | 1 | From src/app, a failed command changing ../../README.md: allowed, failed-call commands exit 0, report and findings name … | DEC-603, DEC-596, DEC-607 |
| `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked` | 1 | An in-scope write from src/app is allowed, runs, its PostToolUse commands exit 0, no report, no finding | DEC-603 |
| `test_w1_38_hooks_any_folder.py::TestAProjectFolderWithASpace::test_the_registered_command_starts_from_a_subfolder` | 7 | The same from src/app of a project whose folder path holds spaces | DEC-603, DEC-608, DEC-609 |
| `test_w1_38_hooks_any_folder.py::TestEveryEntryStartsFromAnyFolder::test_the_registered_command_starts_its_program` | 28 | Each generated command, run from root, subfolder, deep subfolder or outside, gives its program's own answer, never an … | DEC-603, DEC-607, DEC-608 |
| `test_w1_38_hooks_any_folder.py::test_the_events_started_are_the_events_rulesync_generates_guard_entries_under` | 1 | Generated settings register guard entries under exactly the source's seven events | DEC-603, DEC-607 |
| `test_w1_38_hooks_any_folder.py::test_the_source_holds_the_seven_entries_the_cases_start` | 1 | template/.rulesync/hooks.jsonc holds entries under exactly the seven events the cases start | DEC-603, DEC-607 |
| `test_w1_38_hooks_command_line.py::TestAProductPackageNamedGov::test_a_call_the_guard_lets_through_is_let_through_by_its_own_answer` | 1 | With a product src/gov, an in-scope write is allowed by exit 0, runs, the after-check exits 0 silently, nothing recorded | DEC-608 |
| `test_w1_38_hooks_command_line.py::TestAProductPackageNamedGov::test_a_call_the_guard_refuses_is_refused_by_its_written_refusal` | 1 | With a product src/gov, an out-of-scope write is refused by exit 0 and a written deny; file unchanged; nothing recorded | DEC-608 |
| `test_w1_38_hooks_command_line.py::TestAProductPackageNamedGov::test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded` | 1 | With a product src/gov, a failed out-of-scope write from root: allowed by exit 0, after-commands exit 0, README.md … | DEC-608, DEC-601 |
| `test_w1_38_hooks_command_line.py::TestAProductPackageNamedGov::test_the_fixture_holds_a_product_package_and_the_installed_governance_package` | 1 | the fixture's shape, which the next three cases stand on (README l.371); it needs rulesync, so it skips when the probe … | DEC-608 |
| `test_w1_38_hooks_command_line.py::TestGeneratedCommandLines::test_the_generated_command_line_has_the_kernel_template_s_form` | 4 | For SessionStart, Stop, PreCompact and SubagentStop the generated string is the kernel form with the entry's own program | DEC-608 |
| `test_w1_38_hooks_command_line.py::TestGeneratedCommandLines::test_the_generated_command_line_is_the_kernel_template_s` | 3 | For PreToolUse, PostToolUse and PostToolUseFailure the generated command string equals the kernel template's | DEC-608 |
| `test_w1_38_hooks_command_line.py::test_the_kernel_template_s_command_lines_share_one_form` | 1 | The kernel template's three guard command lines share one form with the program name out; three kernel events, four … | DEC-607, DEC-608 |
| `test_w1_38_hooks_command_line.py::test_the_source_s_command_line_is_the_kernel_template_s_form` | 7 | Each of the source's seven command strings, as written, is the kernel template's line or form | DEC-608 |
| `test_w1_38_hooks_source.py::TestFailedCommandInAGeneratedProject::test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded` | 1 | From the root, a failed command changing README.md: failed-call commands exit 0, README.md reported and recorded | DEC-596 |
| `test_w1_38_hooks_source.py::TestFailedCommandInAGeneratedProject::test_a_failed_command_that_stays_in_scope_is_left_alone` | 1 | A failed command changing only src/app/main.py: no report, no finding, change kept | DEC-596 |
| `test_w1_38_hooks_source.py::TestFailedCommandInAGeneratedProject::test_an_acceptance_test_changed_by_a_failed_command_is_restored` | 1 | The engineer's failed command changing an acceptance test: the file is restored from HEAD and named to the agent | DEC-596, MR-3 |
| `test_w1_38_hooks_source.py::TestGeneratedGuardHooks::test_every_guard_hook_entry_of_the_generated_settings_carries_the_time_limit` | 1 | Every generated guard hook entry holds timeout 60, in W1-47's words | DEC-596, DEC-580 |
| `test_w1_38_hooks_source.py::TestGeneratedGuardHooks::test_the_generated_settings_register_what_the_kernel_template_s_settings_register` | 3 | Per event, the generated (matcher, program, timeout) of the guard entries equals the kernel template's | DEC-596, DEC-607 |
| `test_w1_38_hooks_source.py::TestGeneratedGuardHooks::test_the_generated_settings_run_the_containment_program_after_a_failed_bash_call` | 1 | Generated PostToolUseFailure, for Bash, runs the program the kernel template registers there (posttooluse.py) | DEC-596 |
| `test_w1_38_hooks_source.py::TestGeneratedGuardHooks::test_the_three_events_compared_are_the_kernel_template_s_guard_events` | 1 | The kernel template registers guard entries under exactly PreToolUse, PostToolUse and PostToolUseFailure | DEC-596 |
| `test_w1_38_hooks_source.py::TestRulesyncPassesBothThrough::test_a_limit_and_a_failed_tool_call_entry_of_the_source_reach_the_generated_settings` | 1 | rulesync 24.0.0 carries timeout 60 and a postToolUseFailure Bash entry from a changed project source into the settings | DEC-596, DEC-600 |
| `test_w1_38_hooks_source.py::test_a_limit_written_as_a_fraction_in_the_source_file_is_found` | 1 | an oracle check of the suite's comment-tolerant reader (:115-124) | DEC-592 |
| `test_w1_38_hooks_source.py::test_a_source_entry_that_runs_no_kernel_hook_is_left_as_it_is` | 1 | an oracle check of the same reading (:127-134) | DEC-592 |
| `test_w1_38_hooks_source.py::test_every_guard_hook_entry_of_the_source_carries_the_time_limit` | 1 | Every entry of template/.rulesync/hooks.jsonc that runs a kernel hook program holds timeout as the integer 60 | DEC-596, DEC-592, DEC-580 |
| `test_w1_38_hooks_source.py::test_one_source_entry_without_the_whole_number_60_is_found` | 5 | an oracle check of the suite's own reading of the hook source (hooks_source.py:105-112; README l.214, 'keep the reading … | DEC-592, DEC-596 |
| `test_w1_38_rulesync.py::TestClaudeMdAndAgentsMd::test_agents_md_carries_the_root_rule` | 1 | AGENTS.md ends with the root rule's body | KPI S1 [CAP-52.a] |
| `test_w1_38_rulesync.py::TestClaudeMdAndAgentsMd::test_agents_md_token_limit` | 1 | ceil(len/4) of generated AGENTS.md is at most 1,500 | KPI S1 |
| `test_w1_38_rulesync.py::TestClaudeMdAndAgentsMd::test_claude_md_is_the_root_rule` | 1 | CLAUDE.md equals the body of the one root rule source, byte for byte | KPI S1 [CAP-52.a] |
| `test_w1_38_rulesync.py::TestDeleteProtection::test_delete_preserves_openspec_commands` | 1 | After generate --delete every OpenSpec command is there with OpenSpec's body | KPI F1; DEC-074 |
| `test_w1_38_rulesync.py::TestDeleteProtection::test_delete_preserves_openspec_skills` | 1 | After generate --delete every OpenSpec skill file is there as shipped | KPI F1; DEC-468 |
| `test_w1_38_rulesync.py::TestDeleteProtection::test_delete_preserves_vendored_skills` | 1 | The three vendored SKILL.md files exist after generate and after generate --delete | KPI F1; DEC-244 |
| `test_w1_38_rulesync.py::TestFindings::test_findings_name_exactly_the_edited_file` | 4 | After one hand edit gov check's findings name exactly that file | KPI F2; CAP-38.b |
| `test_w1_38_rulesync.py::TestFindings::test_one_hand_edit_is_one_finding` | 1 | One AGENTS.md edit gives exactly one finding | KPI F2 |
| `test_w1_38_rulesync.py::TestFindings::test_rulesync_failure_without_a_file_is_reported_with_its_reason` | 1 | A stand-in rulesync fails naming no file: the check fails, repeats its reason, names no project file | KPI F2; DEC-425 |
| `test_w1_38_rulesync.py::TestGenerateCheck::test_check_clean_after_generate` | 1 | rulesync generate --check exits 0 after a fresh generation | KPI S2 |
| `test_w1_38_rulesync.py::TestHandEditDetected::test_hand_edit_agents_md` | 1 | rulesync generate --check exits non-zero after AGENTS.md is overwritten | KPI F2 |
| `test_w1_38_rulesync.py::TestHandEditDetected::test_hand_edit_claude_md` | 1 | rulesync generate --check exits non-zero after CLAUDE.md is overwritten | KPI F2 |
| `test_w1_38_rulesync.py::TestHandEditDetected::test_hand_edit_role_file` | 1 | rulesync generate --check exits non-zero after the first .claude/agents file is overwritten | KPI F2; CAP-52.b |
| `test_w1_38_rulesync.py::TestHandEditDetected::test_hand_edit_skill_file` | 1 | rulesync generate --check exits non-zero after the first generated SKILL.md is overwritten | KPI F2 |
| `test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` | 1 | Every script path in the generated hook commands is a file of the project | KPI S2 |
| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_kernel_role_changed_without_its_source` | 1 | Kernel engineer role changed alone: gov check RED/RED, findings name the source and nothing outside the pair | KPI S3; DEC-066, DEC-471 |
| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_kernel_skill_changed_without_its_source` | 1 | Kernel planning skill changed alone: RED/RED, the source named | KPI S3; DEC-066, DEC-471 |
| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_role_source_changed_without_its_kernel_role` | 1 | Role source changed and regenerated: RED/RED, the source named, nothing outside the pair | KPI S3; DEC-066, DEC-471 |
| `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource::test_skill_source_changed_without_its_kernel_skill` | 1 | Planning skill source changed and regenerated: RED/RED, the source named | KPI S3; DEC-066, DEC-471 |
| `test_w1_38_rulesync.py::TestMissingFileDetected::test_missing_agents_md_fails_check` | 1 | rulesync generate --check exits non-zero after AGENTS.md is deleted | KPI F2 |
| `test_w1_38_rulesync.py::TestMissingFileDetected::test_portability_check_fails_on_missing_agents_md` | 1 | The declared check is not green and names AGENTS.md when it is deleted | CAP-38.b |
| `test_w1_38_rulesync.py::TestOpenSpecCommands::test_generated_command_is_the_one_openspec_ships` | 6 | Each opsx command is generated with OpenSpec 1.13.2's body and frontmatter mapping | KPI S1; DEC-074, DEC-469 |
| `test_w1_38_rulesync.py::TestOpenSpecCommands::test_no_opsx_command_that_openspec_does_not_ship` | 1 | No generated opsx command outside the six OpenSpec writes | KPI S1; DEC-074 |
| `test_w1_38_rulesync.py::TestOpenSpecSkills::test_generated_skill_is_the_one_openspec_ships` | 6 | Each OpenSpec skill's files are generated as openspec init writes them (SKILL.md by body and mapping) | KPI S1, F1; DEC-468 |
| `test_w1_38_rulesync.py::TestOpenSpecSkills::test_no_openspec_skill_that_openspec_does_not_ship` | 1 | No generated openspec-* skill outside OpenSpec's six | DEC-468 |
| `test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_red_after_a_hand_edit` | 1 | After a CLAUDE.md hand edit the declared command fails and gov check shows RED/RED | KPI S3, F2 |
| `test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family` | 1 | gov check --list --json lists exactly one check of the adapter/model-portability family | KPI S3 [CAP-38.b]; DEC-186, DEC-436, DEC-438 |
| `test_w1_38_rulesync.py::TestRoleFieldAgreement::test_role_fields_match_kernel` | 6 | Each labelled field of the generated .claude/agents/<role>.md equals the kernel role's, whitespace collapsed; no extra … | KPI S1 [CAP-52.b]; DEC-066, DEC-352 |
| `test_w1_38_rulesync.py::TestRoleToolsAgainstKernel::test_source_tools_are_the_kernel_role_s` | 6 | Each role source's claudecode.tools equals, as a set, the tool names of the kernel role's Tools field, read by the case | KPI S3 [CAP-52.b]; DEC-471 |
| `test_w1_38_rulesync.py::TestRoleToolsAgainstKernel::test_source_with_a_tool_the_kernel_role_does_not_name` | 1 | NotebookEdit added to the engineer source and regenerated: RED/RED, source named, nothing outside the pair | DEC-471 |
| `test_w1_38_rulesync.py::TestRoleToolsAgainstKernel::test_source_without_a_tool_the_kernel_role_names` | 1 | The kernel's last tool (alphabetically) removed from the source and regenerated: RED/RED, source named | DEC-471 |
| `test_w1_38_rulesync.py::TestRulesyncVersion::test_gov_check_is_red_when_the_version_cannot_be_read` | 1 | Without a registry gov check shows check and family RED | CAP-38.b; DEC-127, DEC-425 |
| `test_w1_38_rulesync.py::TestRulesyncVersion::test_installed_rulesync_of_another_version_is_not_green` | 1 | A stand-in answering 99.0.0: not green, names 99.0.0 and the registered version | DEC-127 |
| `test_w1_38_rulesync.py::TestRulesyncVersion::test_project_expecting_another_version_is_not_green` | 1 | Registry expects 23.0.0: not green, the output names 23.0.0 and the installed version | DEC-127 |
| `test_w1_38_rulesync.py::TestRulesyncVersion::test_registry_file_absent_is_not_green` | 1 | Without a tool registry the declared check is not green and names tool-registry.yaml | KPI S1; DEC-127, DEC-040 |
| `test_w1_38_rulesync.py::TestRulesyncVersion::test_registry_without_a_rulesync_entry_is_not_green` | 1 | A registry holding only uv: not green, names tool-registry.yaml | DEC-127 |
| `test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named` | 5 | An added allow rule, defaultMode, Notification hook, env or sandbox key: RED/RED, only settings.json named | KPI F2; DEC-471; DEC-871 |
| `test_w1_38_rulesync.py::TestSettingsHandEdit::test_rule_removed_by_hand_is_found_and_named` | 1 | One generated deny rule removed: RED/RED, only settings.json named | KPI F2; DEC-471 |
| `test_w1_38_rulesync.py::TestSkillGeneration::test_skill_body_matches_source` | 8 | The generated SKILL.md body of eight kernel method skills equals the kernel's, byte for byte after the frontmatter | KPI S1 [CAP-52.a]; DEC-066 |
| `test_w1_38_rulesync.py::TestSourceChangeDetected::test_source_change_fails_check` | 1 | rulesync generate --check exits non-zero after a rule source changed without regenerating | KPI S2 |
| `test_w1_38_rulesync.py::TestToolAbsentOrHanging::test_rulesync_absent_not_green` | 1 | PATH /usr/bin:/bin and a nonexistent RULESYNC_BIN: not green, output says not found, missing or absent | DEC-425 |
| `test_w1_38_rulesync.py::TestToolAbsentOrHanging::test_rulesync_bin_missing_file` | 1 | RULESYNC_BIN naming a missing file: not green, output says not found or missing | DEC-425 |
| `test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding` | 2 | With .claude/settings.local.json or a file under .claude/worktrees/ added, the declared check exits 0 | DEC-063, DEC-050, DEC-471; DEC-892 |
| `test_w1_38_rulesync.py::TestUnsourcedFile::test_file_without_a_source_is_found_and_named` | 4 | A hand-written file in .claude/agents, skills, a generated skill or commands: RED/RED, findings name exactly it | KPI F2; DEC-471, DEC-074, ADR-0002 |
| `test_w1_38_rulesync.py::TestVendoredSkillRegistration::test_vendored_skill_is_the_kernel_copy` | 3 | Every file of the kernel's superpowers/<skill>/ is generated under .claude/skills/<skill>/ (SKILL.md by body, others by … | KPI S1; DEC-244, DEC-074 |
| `test_w1_38_test_folder_rule.py::TestALaunchedSessionInAProjectMadeFromTheTemplate::test_the_launchers_settings_close_the_folder_for_every_other_role` | 3 | Settings gov launch builds for engineer, product-spec and auditor cover all five folder paths with Edit deny | DEC-315, DEC-664 |
| `test_w1_38_test_folder_rule.py::TestALaunchedSessionInAProjectMadeFromTheTemplate::test_the_launchers_settings_leave_the_folder_to_the_test_designer` | 1 | The test designer's built Edit denies cover no folder path and still close a ticket file and .claude/settings.json | DEC-315, DEC-664 |
| `test_w1_38_test_folder_rule.py::TestEveryOtherRuleStays::test_the_four_other_deny_rules_are_still_generated_and_nothing_else` | 1 | Generated permissions hold exactly those four deny rules, each once, and no other list | DEC-664 |
| `test_w1_38_test_folder_rule.py::TestEveryOtherRuleStays::test_the_generated_settings_still_close_the_ticket_folder` | 1 | A generated Edit deny rule covers an existing and a new ticket file | DEC-664, DEC-315 |
| `test_w1_38_test_folder_rule.py::TestEveryOtherRuleStays::test_the_templates_source_gives_the_four_other_rules_and_nothing_else` | 1 | The source's other rules are exactly the .tickets/** edit deny and the npm install, pip install and sudo bash denies | DEC-664 |
| `test_w1_38_test_folder_rule.py::TestTheGuardInAProjectMadeFromTheTemplate::test_every_other_role_is_refused_a_write_under_the_folder` | 5 | Engineer, product-spec, research, auditor and orchestrator are each refused by the program under the folder; no file … | MR-3, DEC-069, DEC-664 |
| `test_w1_38_test_folder_rule.py::TestTheGuardInAProjectMadeFromTheTemplate::test_the_engineer_is_let_through_inside_its_ticket` | 1 | The engineer's Write and Edit on src/app/main.py are allowed | DEC-664 |
| `test_w1_38_test_folder_rule.py::TestTheGuardInAProjectMadeFromTheTemplate::test_the_test_designer_is_still_refused_outside_the_folder` | 1 | The test designer's Write and Edit on src/app/main.py, a unit test and its ticket file are refused by the program | MR-3, DEC-664 |
| `test_w1_38_test_folder_rule.py::TestTheGuardInAProjectMadeFromTheTemplate::test_the_test_designer_on_its_ticket_is_allowed_a_write_under_the_folder` | 1 | Through the generated PreToolUse commands the guard allows the test designer's Write, Edit and Bash writes under the … | MR-3, DEC-069, DEC-664, DEC-820 |
| `test_w1_38_test_folder_rule.py::TestTheRuleIsGone::test_the_generated_settings_hold_no_rule_of_a_write_tool_on_the_folder_in_any_list` | 1 | No Edit, Write, MultiEdit or NotebookEdit rule in the deny, ask or allow list covers the folder | DEC-664 |
| `test_w1_38_test_folder_rule.py::TestTheRuleIsGone::test_the_templates_source_holds_no_edit_rule_on_the_acceptance_test_folder` | 1 | No permission.edit rule of template/.rulesync/permissions.jsonc, whatever its value, covers a path under … | DEC-664, DEC-315, MR-3 |

**W1-39**: W1-39 (DAEO-5ylr); 59 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_39_copy.py::test_a_created_project_ignores_the_runtime_folder_and_bytecode_folders` | 1 | git ignores .gov-runtime/ and __pycache__/ files at any depth and shows two other files untracked | DEC-493 |
| `test_w1_39_copy.py::test_a_freshly_created_project_is_at_the_minimal_adoption_level` | 1 | Doctor reports adoption level MINIMAL and exits 0 | CAP-54; DEC-499 |
| `test_w1_39_copy.py::test_copy_creates_the_overlay` | 1 | governance/project/ of the project holds exactly path-map.yaml | KPI S1; DEC-493 |
| `test_w1_39_copy.py::test_copy_installs_the_kernel_exactly_as_the_template_holds_it` | 1 | The created project's governance/kernel/ holds every plain template kernel file byte for byte, and no unexplained file | KPI S1 [CAP-44.a]; ADR-0002 §5; DEC-023 |
| `test_w1_39_copy.py::test_copy_installs_the_rulesync_sources` | 1 | The project's .rulesync/ holds every plain adapter source of the template byte for byte | KPI S1 [CAP-44.a]; W1-38 |
| `test_w1_39_copy.py::test_copy_into_a_folder_that_has_a_path_map_keeps_it` | 1 | An existing path map is not replaced by the copy | DEC-493 |
| `test_w1_39_copy.py::test_copy_into_a_folder_that_has_an_overlay_file_keeps_it` | 1 | A folder already holding governance/project/notes/local.md keeps the project's text after the copy | KPI S1; DEC-023 |
| `test_w1_39_copy.py::test_copy_succeeds_where_rulesync_and_node_are_absent` | 1 | With rulesync, node, nodejs, npx and npm off PATH, the copy writes kernel and manifest, nothing generated | DEC-488 |
| `test_w1_39_copy.py::test_copy_writes_nothing_that_rulesync_generates` | 1 | No .claude/, CLAUDE.md or AGENTS.md after the copy | DEC-488 |
| `test_w1_39_copy.py::test_copy_writes_the_answers_file_that_names_the_release` | 1 | .copier-answers.yml exists and names v0.1.0 | DEC-023, DEC-493 |
| `test_w1_39_copy.py::test_doctor_passes_on_a_freshly_created_project` | 1 | Doctor exits 0 with ok, no part fail or drift, and its lock part is a measured MATCH | KPI S1 [CAP-44.a]; CAP-02.a |
| `test_w1_39_copy.py::test_doctor_reads_the_lock_and_leaves_it_as_it_was` | 1 | The lock and the kernel files are byte-identical after doctor ran | CAP-02.a |
| `test_w1_39_copy.py::test_every_manifest_entry_is_a_file_of_the_project_with_that_sha256` | 1 | Every manifest entry is an existing file whose lower-case sha256 is recorded | CAP-02.a |
| `test_w1_39_copy.py::test_the_ignore_file_hides_no_installed_kernel_file` | 1 | Every installed kernel file is tracked once the project is committed | DEC-493 |
| `test_w1_39_copy.py::test_the_manifest_leaves_out_the_overlay_and_the_lock_itself` | 1 | The manifest lists no governance/project/ file, and neither the lock nor the answers file | CAP-02.a; DEC-488 |
| `test_w1_39_copy.py::test_the_manifest_lists_every_installed_kernel_file_with_its_sha256` | 1 | Every file under governance/kernel/ is in the manifest with its sha256 | CAP-02.a; DEC-023 |
| `test_w1_39_copy.py::test_the_path_map_of_a_fresh_project_is_one_doctors_path_map_part_accepts` | 1 | Doctor's path_map part on the committed fresh project: pass, unclassified_count 0 | DEC-493; CAP-44.a |
| `test_w1_39_drift.py::test_a_file_in_a_bytecode_folder_inside_the_kernel_is_not_drift` | 1 | .pyc files in __pycache__/ folders inside the kernel: MATCH, pass, not named | DEC-488 |
| `test_w1_39_drift.py::test_a_file_the_project_adds_outside_the_kernel_is_not_drift` | 3 | Files added under governance/project/, src/ or .tickets/: MATCH, no drift, not named | CAP-02.a; ADR-0002 §5 |
| `test_w1_39_drift.py::test_a_kernel_file_hidden_from_git_by_an_ignore_rule_is_still_drift_naming_it` | 1 | An unlisted kernel file that the project's ignore rule hides: still DRIFT naming it | DEC-488 |
| `test_w1_39_drift.py::test_a_kernel_file_struck_from_the_manifest_is_drift_naming_it` | 1 | A hook's manifest entry removed: DRIFT naming it | DEC-488 |
| `test_w1_39_drift.py::test_a_kernel_file_the_manifest_does_not_list_is_drift_naming_it` | 1 | A file added under governance/kernel/hooks: DRIFT naming it | DEC-488; CAP-43 |
| `test_w1_39_drift.py::test_a_kernel_folder_that_cannot_be_listed_is_not_passed_over` | 2 | A kernel folder of mode 0 or 0100: no traceback, not MATCH, folder or a reason named, exit non-zero | DEC-488 |
| `test_w1_39_drift.py::test_a_listed_file_that_cannot_be_read_is_reported_by_name` | 1 | A listed hook without read permission: not MATCH, named, exit non-zero | DEC-488 |
| `test_w1_39_drift.py::test_a_listed_file_that_is_missing_is_reported_by_name` | 1 | A listed hook deleted: DRIFT naming it | DEC-488, DEC-449, DEC-454 |
| `test_w1_39_drift.py::test_a_lock_that_is_not_readable_as_a_map_is_not_a_match` | 1 | A lock that is a YAML list: not MATCH, exit non-zero | DEC-488 |
| `test_w1_39_drift.py::test_a_lock_without_manifest_entries_is_not_a_match` | 2 | An empty or absent manifest: not MATCH, exit non-zero | DEC-488 |
| `test_w1_39_drift.py::test_a_one_byte_edit_of_a_kernel_file_is_drift_naming_it` | 2 | One byte appended to a hooks/ or skills/ kernel file: DRIFT naming it, not MATCH, doctor exits non-zero, ok false | KPI S2 [CAP-02.a] |
| `test_w1_39_drift.py::test_a_project_without_any_installed_kernel_file_is_not_a_match` | 1 | Kernel removed, manifest listing only .gitignore with its true hash: not MATCH | DEC-488 |
| `test_w1_39_drift.py::test_an_installed_project_whose_lock_was_deleted_fails_the_lock_part` | 1 | Answers file kept, lock deleted: lock part fail, names framework.lock, exit non-zero, ok false | DEC-499 |
| `test_w1_39_drift.py::test_deleting_the_lock_does_not_silence_an_edited_kernel_file` | 1 | An edited kernel file and a deleted lock: the lock part fails | DEC-499 |
| `test_w1_39_drift.py::test_doctor_without_json_exits_non_zero_and_names_the_lock_when_it_was_deleted` | 1 | Plain gov doctor after the lock was deleted: no traceback, exit non-zero, prints framework.lock | DEC-499 |
| `test_w1_39_drift.py::test_drift_names_the_edited_file_and_no_other` | 1 | The drift report names the edited kernel file and not an untouched one | CAP-02.a |
| `test_w1_39_drift.py::test_the_edit_taken_back_is_a_match_again` | 1 | DRIFT after the edit; once the bytes are restored, MATCH, no drift, exit 0 | CAP-02.a |
| `test_w1_39_hook_time_limit.py::test_a_created_project_has_the_time_limit_on_every_guard_hook_entry` | 1 | After copier copy every guard entry of governance/kernel/settings.json carries timeout 60 | DEC-580 |
| `test_w1_39_hook_time_limit.py::test_a_project_of_an_earlier_release_gets_the_time_limit_by_an_update` | 1 | A project of a release without limits has them after copier update to the shipped settings | DEC-580; DEC-023 |
| `test_w1_39_hook_time_limit.py::test_a_project_that_had_settings_of_its_own_gets_the_time_limit_on_the_guard_s_entries` | 1 | The same where .claude/settings.json existed before the copy | DEC-580 |
| `test_w1_39_hook_time_limit.py::test_copy_leaves_a_project_s_own_settings_as_they_were` | 1 | The folder's own .claude/settings.json is byte-identical after the copy; the kernel settings are installed beside it | DEC-580, DEC-488 |
| `test_w1_39_layout.py::test_a_created_project_holds_none_of_the_gov_os_repositorys_own_trees` | 1 | The created project holds no copier.yml, template, src, cli, fixtures, docs or pyproject.toml | KPI S3 [CAP-43.a] |
| `test_w1_39_layout.py::test_a_created_project_holds_only_the_product_layout` | 1 | Every top-level entry of the created project is in the copied product layout; the answers file is there | KPI S3; ADR-0002 §5; DEC-488 |
| `test_w1_39_layout.py::test_governance_of_a_created_project_is_the_kernel_the_overlay_and_the_lock` | 1 | governance/ holds kernel/, project/ and framework.lock, and nothing else | KPI S3; ADR-0002 §5 |
| `test_w1_39_layout.py::test_the_template_tree_holds_nothing_but_what_a_product_receives` | 1 | Every top-level entry of template/ in the real listing (suffix stripped) belongs to the copied product layout | KPI S3 [CAP-43.a]; DEC-488 |
| `test_w1_39_layout.py::test_this_repository_is_a_copier_template_whose_subdirectory_is_the_kernel_template_tree` | 1 | copier.yml declares _subdirectory: template; seven trees (kernel template, src/gov, tests/acceptance, fixtures, … | KPI S3 [CAP-43.a]; ADR-0002 §5; DEC-023 |
| `test_w1_39_lock_identity.py::test_doctor_fails_when_the_locks_tag_or_commit_disagrees_with_the_install` | 2 | Tag or commit changed in the lock: not MATCH, doctor exits non-zero | CAP-43; DEC-488 |
| `test_w1_39_lock_identity.py::test_the_lock_names_the_template_commit` | 1 | The lock's text holds the full commit id of the tag | KPI F2; CAP-43 |
| `test_w1_39_lock_identity.py::test_the_lock_names_the_template_tag` | 1 | The lock's text holds the release tag v0.1.0 | KPI F2; CAP-43; DEC-023 |
| `test_w1_39_lock_identity.py::test_the_lock_of_an_untagged_template_commit_still_names_the_commit` | 1 | Copied from an untagged later commit: the lock names that commit and not the tag's | KPI F2; CAP-43 |
| `test_w1_39_lock_identity.py::test_the_lock_refers_to_the_answers_file` | 1 | Outside its comment header the lock names .copier-answers.yml | DEC-023 |
| `test_w1_39_update.py::test_after_an_update_doctor_reports_a_match` | 1 | After the update the lock part is MATCH and pass, with no drift | CAP-02.a; DEC-488 |
| `test_w1_39_update.py::test_after_an_update_the_lock_names_the_second_release_and_its_files` | 1 | The lock names v0.2.0 and its commit; the manifest holds current hashes and the added file | CAP-02.a; DEC-023 |
| `test_w1_39_update.py::test_copier_prints_the_update_procedure_after_a_copy` | 1 | What copier copy printed (progress lines dropped) names copier update, .copier-answers.yml, gov doctor and rulesync | KPI S2; DEC-488, DEC-499 |
| `test_w1_39_update.py::test_copier_prints_the_update_procedure_after_an_update` | 1 | What copier update printed names the same four words | KPI S2; DEC-488 |
| `test_w1_39_update.py::test_the_generated_lock_states_the_update_procedure_in_its_comment_header` | 1 | The lock's comment header names the four procedure words, and the lock still has a manifest | KPI S2; DEC-488 |
| `test_w1_39_update.py::test_the_lock_keeps_its_comment_header_after_an_update` | 1 | After the update the lock's header still names the four words | DEC-488 |
| `test_w1_39_update.py::test_update_brings_the_kernel_of_the_second_release` | 1 | The changed and the added kernel files of v0.2.0 arrive | KPI F1 |
| `test_w1_39_update.py::test_update_keeps_an_overlay_file_the_project_wrote` | 2 | A project-written overlay file survives copier update to a release that ships its own text there | KPI F1; DEC-023 |
| `test_w1_39_update.py::test_update_keeps_an_overlay_file_the_template_shipped_and_the_project_edited` | 2 | A shipped overlay file the project edited keeps the edit; no .rej or .orig files | KPI F1; DEC-023 |
| `test_w1_39_update.py::test_update_keeps_the_path_map_when_the_release_ships_a_different_one` | 2 | The path map, edited or as created, is byte-identical after update; no reject files | DEC-493 |
| `test_w1_39_update.py::test_update_leaves_every_file_the_project_added_as_it_was` | 1 | A ticket, a decision, code and an overlay file are unchanged by the update | KPI F1 |

**W1-41**: W1-41 (DAEO-cdoi); 127 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_41_baseline.py::test_a0_records_the_clean_tree_and_a_backup_ref` | 1 | A0 commits its record; baseline_commit is HEAD; new full backup_ref resolves to it, also in result. | S1; CAP-44.b |
| `test_w1_41_baseline.py::test_a0_refuses_a_dirty_tree_and_writes_nothing` | 3 | A0 refuses an untracked, modified or staged path, naming it; files, HEAD, refs, porcelain unchanged. | S1; CAP-44.b |
| `test_w1_41_baseline.py::test_a1_inventory_lists_every_tracked_artefact` | 1 | A1 lists every path tracked before A0 and nothing untracked. | S1; CAP-44.b |
| `test_w1_41_baseline.py::test_a2_classifies_every_inventoried_artefact` | 1 | A2 gives every artefact namespace `harbour`; `unknown: []`. | S1; CAP-44.b, CAP-06.c |
| `test_w1_41_baseline.py::test_a_folder_that_is_no_git_repository_is_refused` | 1 | A0 outside a repository is the tool's own refusal (exit 1/3/4); folder holds only README.md. | S1; CAP-44.b; DEC-449 |
| `test_w1_41_baseline.py::test_a_project_without_a_path_map_is_not_classified` | 1 | Without a path map A0–A2 do not all pass; first refusal is the tool's, naming "path map". | S1; DEC-449 |
| `test_w1_41_baseline.py::test_a_stage_without_the_record_of_the_stage_before_it_refuses` | 6 | On a fresh project A1, A2, A3, A4, A6, A8 each refuse (any reason) and write nothing. | README interface 5; DEC-090 |
| `test_w1_41_baseline.py::test_adopt_without_lite_is_still_reserved` | 1 | gov adopt --json answers NOT_IMPLEMENTED, exit 1, valid envelope; files, HEAD, refs, porcelain unchanged. | README interface 1, P-9; DEC-090; CAP-44 wave note |
| `test_w1_41_baseline.py::test_lite_without_a_stage_is_a_usage_error` | 1 | --lite without --stage exits 2 and changes no file, HEAD, ref or porcelain. | README interface 2 |
| `test_w1_41_baseline.py::test_stages_a0_to_a4_each_leave_their_own_evidence_record` | 1 | A0–A4 with the legacy proposal pass; five distinct record paths and ids. | S1; CAP-44.b |
| `test_w1_41_dev_tier.py::test_the_eight_stages_each_leave_an_evidence_record_on_b_dev` | 1 | On a b-dev clone through A8: eight distinct records, complete A1, `unknown: []`, backup ref resolves. | S1 "on b-dev"; CAP-44.b |
| `test_w1_41_embedding_policy.py::test_a_corrected_path_map_committed_after_the_refusal_goes_on` | 1 | After the refusal, a committed corrected map lets A3 and A4 pass. | DEC-694 |
| `test_w1_41_embedding_policy.py::test_a_namespace_with_another_value_is_refused_at_a3` | 4 | A3 refused with an ADOPT_ code naming `papers`, both values quoted; nothing written, clean. | DEC-694 (7331), DEC-700 |
| `test_w1_41_embedding_policy.py::test_a_namespace_without_the_field_is_refused_at_a3` | 1 | Same refusal for a namespace lacking the field. | DEC-700 (7377), DEC-701 (7388) |
| `test_w1_41_embedding_policy.py::test_a_path_map_where_every_namespace_says_not_embedded_is_refused_at_a3` | 2 | A3 refused; message says "no namespace is embedded"; nothing written. | DEC-694 |
| `test_w1_41_embedding_policy.py::test_a_path_map_whose_namespaces_each_state_a_valid_value_goes_on` | 3 | A0–A4 pass when every namespace is valid and one or more is `embedded`. | DEC-694 |
| `test_w1_41_embedding_policy.py::test_a_value_that_is_no_text_is_refused_before_a3_goes_on` | 3 | A stage up to A3 refuses naming `papers`, writing nothing; A3 never records the map. | DEC-694, DEC-700 |
| `test_w1_41_embedding_policy.py::test_neither_says_it_where_a_namespace_is_embedded` | 6 | With one `embedded` namespace, no rebuild mode or doctor prints the words. | DEC-694 |
| `test_w1_41_embedding_policy.py::test_the_adopt_skill_names_the_two_valid_embedding_policies` | 1 | the field name and both values between quotes or backticks (embedding_policy.py:112-115) | DEC-694 (7330) |
| `test_w1_41_embedding_policy.py::test_the_adopt_skill_says_every_namespace_states_one` | 1 | both words on the rule's own line only (adopt/SKILL.md:32); the same limit | DEC-694, DEC-700 |
| `test_w1_41_embedding_policy.py::test_the_adopt_skill_says_what_embedded_means` | 1 | the words stand on the rule's own lines only (adopt/SKILL.md:32 and :34), so the rule cannot go and leave them; a … | DEC-694 |
| `test_w1_41_embedding_policy.py::test_the_doctor_says_no_namespace_is_embedded_and_adds_no_failure` | 4 | Doctor says the words under `semantic`; exit, ok, healthy, section statuses and canary equal the reference's. | DEC-694 |
| `test_w1_41_embedding_policy.py::test_the_rebuild_says_no_namespace_is_embedded` | 8 | gov rebuild ok, lexical recreated, store statuses equal the reference's; semantic part says the words. | DEC-694 (7332) |
| `test_w1_41_embedding_policy.py::test_two_namespaces_at_fault_are_both_named` | 1 | A3's message names `papers` and `attic`, quotes both values; nothing written. | DEC-694, DEC-700 |
| `test_w1_41_external_follow_up.py::test_a_defect_of_the_working_trees_file_alone_blocks_no_ticket` | 1 | An uncommitted defective file leaves a records-only packet unchanged. | DEC-552 9a; DEC-551 (5984) |
| `test_w1_41_external_follow_up.py::test_a_listed_id_of_a_form_the_repository_holds_is_refused` | 7 | A listed CAP/CAP-item/MR/ADR/L-/W-id blocks the declaring ticket; BLOCKED names the file and id. | DEC-552 9b; DEC-551 P-12 |
| `test_w1_41_external_follow_up.py::test_a_listed_id_of_such_a_form_blocks_a_ticket_that_does_not_declare_it` | 1 | A file listing CAP-13 blocks a records-only ticket, naming file and id. | DEC-551 P-11 |
| `test_w1_41_external_follow_up.py::test_an_id_of_a_form_outside_sources_share_is_still_accepted` | 4 | ISO-9001, RFC-2119.b, CAPE-13, S0a-CAP-13 are reported as the external item. | DEC-552 9b; P-15 |
| `test_w1_41_external_follow_up.py::test_an_uncommitted_change_of_the_file_does_not_unblock_a_mandatory_source` | 4 | A written or staged, uncommitted entry or file leaves the context BLOCKED, missing id named. | DEC-552 9a (5992), DEC-569 (6145); CAP-15.c |
| `test_w1_41_external_follow_up.py::test_the_commit_read_is_the_head_of_the_checkout` | 1 | Listed earlier and in the working tree but not at HEAD: BLOCKED as missing. | DEC-552 9a |
| `test_w1_41_external_follow_up.py::test_the_same_change_committed_makes_the_id_an_external_reference` | 2 | Committed, the id becomes the packet's only external item. | DEC-552 9a |
| `test_w1_41_external_follow_up.py::test_what_the_working_tree_does_to_the_committed_file_changes_nothing` | 3 | Deleting, breaking or shortening the committed file in the working tree leaves the packet and hash unchanged. | DEC-552 9a |
| `test_w1_41_external_references.py::test_a_change_of_the_listed_entry_changes_the_packets_hash` | 2 | A committed change of location or reason changes the hash; mandatory items unchanged. | S9; CAP-15.e |
| `test_w1_41_external_references.py::test_a_defective_file_blocks_a_ticket_whose_ids_are_all_records_too` | 2 | A defective file blocks a records-only ticket, file named. | DEC-551 P-11 |
| `test_w1_41_external_references.py::test_a_file_that_cannot_be_read_blocks_and_is_named` | 2 | Committed non-UTF-8 bytes or a symlink block, file named. | DEC-552 f9 |
| `test_w1_41_external_references.py::test_a_file_that_is_not_of_the_stated_shape_blocks_and_is_named` | 13 | Each malformed file: BLOCKED naming governance/project/external-references.yaml. | DEC-449, DEC-454, DEC-551 |
| `test_w1_41_external_references.py::test_a_file_the_ticket_names_nothing_of_leaves_its_packet_as_it_was` | 2 | A file listing nothing the ticket declares leaves its packet and hash unchanged. | DEC-520 |
| `test_w1_41_external_references.py::test_a_listed_id_of_the_decision_registers_form_is_refused` | 2 | Listing DEC-086 blocks, naming file and id. | DEC-519, DEC-521, DEC-551 P-12 |
| `test_w1_41_external_references.py::test_a_listed_id_that_is_a_record_is_the_stores_record` | 1 | A listed record stays in mandatory with its file sha256; only the non-record is external. | DEC-520 |
| `test_w1_41_external_references.py::test_a_listed_id_that_is_a_superseded_record_still_blocks` | 1 | A listed superseded record still blocks, ADR-H9-OLD named. | DEC-520 |
| `test_w1_41_external_references.py::test_a_missing_id_blocks_in_a_project_without_the_file` | 1 | Without the file, function and command block the missing ids, named. | W1-24 |
| `test_w1_41_external_references.py::test_a_project_without_the_file_gives_the_packet_it_gave_before` | 1 | Without the file the packet has exactly W1-24's eight keys and its two records. | DEC-520 |
| `test_w1_41_external_references.py::test_a_ticket_whose_declared_ids_are_all_external_is_refused` | 2 | All-external ticket BLOCKED naming ticket and ids; message says "external"/"read"; sibling ticket builds. | S9; DEC-551, DEC-568 (6132); P-13 |
| `test_w1_41_external_references.py::test_a_ticket_whose_sources_are_all_external_is_refused_beside_dependencies` | 3 | With dependencies that are read, command and function still refuse BLOCKED, "external"/"read". | DEC-552 f8; DEC-568; P-14 |
| `test_w1_41_external_references.py::test_a_ticket_with_a_source_that_was_read_is_built_beside_dependencies` | 3 | One record source: packet lists externals in order, charter with its file sha256; function agrees. | DEC-552 f8 |
| `test_w1_41_external_references.py::test_an_external_reference_adds_nothing_to_the_packets_tokens` | 1 | Tokens and budget equal the twin ticket's without the external id. | S9 |
| `test_w1_41_external_references.py::test_an_external_reference_is_not_among_the_items_read_as_records` | 1 | Id in no mandatory/authority/supplementary block; its item has no sha256, authority, lifecycle, text, tokens or path. | S9 |
| `test_w1_41_external_references.py::test_an_id_that_is_neither_a_record_nor_listed_stays_blocked` | 1 | The function refuses BLOCKED naming GONE-H9-404. | W1-24; DEC-520 |
| `test_w1_41_external_references.py::test_an_unlisted_id_blocks_a_ticket_that_also_declares_a_listed_one` | 1 | BLOCKED naming the unlisted id beside a listed one. | DEC-520 |
| `test_w1_41_external_references.py::test_the_brief_says_that_the_external_source_was_not_read` | 1 | Brief summary names the id with "not read"; the brief file's `external` holds it. | S9 |
| `test_w1_41_external_references.py::test_the_context_of_a_ticket_that_declares_a_listed_id_is_built` | 1 | Packet built; mandatory ids are exactly the two records. | S9; CAP-15.c; DEC-511 (5589), DEC-520 (5710) |
| `test_w1_41_external_references.py::test_the_function_names_the_defective_file_in_its_message` | 1 | The function's BLOCKED message names the file. | DEC-449 |
| `test_w1_41_external_references.py::test_the_function_refuses_a_ticket_whose_declared_ids_are_all_external` | 1 | The function refuses the same, ticket and both ids in the message. | same |
| `test_w1_41_external_references.py::test_the_function_reports_the_same_external_reference` | 1 | The function's `external` equals the command's: one id, `read: false`. | S9 |
| `test_w1_41_external_references.py::test_the_packet_reports_each_listed_id_as_external_with_where_it_lives` | 1 | external` lists ids in ticket order with location, reason, `read: false`; unnamed entries absent. | S9; DEC-520 |
| `test_w1_41_external_references.py::test_the_same_project_gives_the_same_hash_twice` | 1 | Two runs give equal packets and hashes. | S9; CAP-15.e |
| `test_w1_41_legacy.py::test_a_chat_database_with_nothing_extracted_is_not_retired` | 1 | Without an extraction, A8 names the DB and it stays. | S3; P-4 |
| `test_w1_41_legacy.py::test_a_citation_the_proof_sees_today_is_refused_and_the_citer_named` | 4 | A8 refuses bare-path/bare-id rule citations and ACTIVE-record citations, naming the citer (checked in the fixture). | DEC-552 f1, f6 (5992) |
| `test_w1_41_legacy.py::test_a_file_deleted_from_the_active_tree_stays_reachable_too` | 1 | notes.txt's disposition resolves to a commit with its original blob. | S6; CAP-42.c |
| `test_w1_41_legacy.py::test_a_kept_rule_file_cites_the_store_however_it_writes_the_path` | 5 | Path behind ./, /, ../, a folder, or id behind a folder: same refusal as bare, file named; store unchanged. | DEC-552 f1 |
| `test_w1_41_legacy.py::test_a_legacy_rule_file_that_cannot_be_parsed_is_not_retired` | 1 | Non-JSON tools file: A8 refuses (1/3/4) naming it; it stays. | S3; DEC-449 |
| `test_w1_41_legacy.py::test_a_longer_path_or_id_that_only_contains_the_stores_is_no_citation` | 3 | Same-named file elsewhere, old-prefix or LEG-0011: store retired through A8, kept file unchanged. | DEC-552 f1 |
| `test_w1_41_legacy.py::test_a_memory_store_a_kept_legacy_rule_file_cites_is_not_retired` | 2 | A kept legacy rule file citing the store keeps it and itself unchanged, is named; on exit 0 citers non-empty. | S5; DEC-449 |
| `test_w1_41_legacy.py::test_a_memory_store_a_rule_cites_is_not_retired` | 1 | A .rulesync rule citing the store keeps it; A8 names the rule. | S5 |
| `test_w1_41_legacy.py::test_a_memory_store_an_active_record_cites_is_not_retired` | 1 | An ACTIVE citing record keeps the store; A8 names DEC-400. | S5 |
| `test_w1_41_legacy.py::test_a_memory_store_nothing_cites_is_retired` | 1 | The three store files are gone from HEAD and disk. | S5; CAP-42.b |
| `test_w1_41_legacy.py::test_a_record_that_cannot_be_read_is_no_proof_of_no_dependency` | 1 | A broken-frontmatter record keeps the store; A8 names dec-402.md. | DEC-449 |
| `test_w1_41_legacy.py::test_a_record_that_no_longer_stands_does_not_keep_the_store` | 3 | SUPERSEDED/RETIRED/REJECTED citers do not: A8 passes, store gone. | DEC-568 |
| `test_w1_41_legacy.py::test_a_record_that_still_stands_keeps_the_store` | 6 | ACCEPTED/PROPOSED/DRAFT/DEPRECATED/no status/LINGERING citers keep the store, named; four rows match the ACTIVE refusal. | DEC-552 f6; DEC-568 (6132) |
| `test_w1_41_legacy.py::test_adapter_generation_is_run_or_named` | 1 | CLAUDE.md exists or A8's result or record names `rulesync generate`. | DEC-488 (5334) |
| `test_w1_41_legacy.py::test_an_extraction_from_another_content_of_the_database_does_not_count` | 1 | An extraction with another hash does not retire the DB; named, stays. | S3; P-4 |
| `test_w1_41_legacy.py::test_each_kind_of_legacy_rule_file_is_imported_into_rulesync` | 5 | Each kind's phrases are in a committed file under .rulesync/. | S3; CAP-42.a, CAP-44.e; P-3 |
| `test_w1_41_legacy.py::test_no_legacy_rule_file_stays_where_an_agent_tool_loads_instructions` | 1 | Five legacy files gone from HEAD and disk; no .mdc left; AGENTS.md not the legacy text. | F3; CAP-42.a |
| `test_w1_41_legacy.py::test_nothing_left_the_tree_without_a_recorded_disposition` | 1 | notes.txt left; every leaver has a disposition; nothing unplanned left. | S6; CAP-42.c |
| `test_w1_41_legacy.py::test_retired_material_stays_reachable_as_it_was` | 1 | Each retired path's `reachable_at` resolves to a commit holding its original blob. | S6; CAP-42.c |
| `test_w1_41_legacy.py::test_retired_systems_contribute_no_active_decision` | 1 | no record of the retired memory store is ACTIVE at HEAD (legacy.py:484-499); a file whose frontmatter cannot be read is … | S3; CAP-42.a |
| `test_w1_41_legacy.py::test_the_a8_record_names_what_each_legacy_rule_file_was_imported_into` | 1 | A8's `imported` names all six files, each `into` committed .rulesync paths. | S3 |
| `test_w1_41_legacy.py::test_the_chat_database_is_marked_non_authoritative` | 1 | The chat DB's A3 entry says non_authoritative. | S3; CAP-42.b |
| `test_w1_41_legacy.py::test_the_chat_database_is_retired_after_its_knowledge_is_in_records` | 1 | DB left HEAD and disk; extraction stayed; disposition names EXT-0001. | S3; CAP-42.b |
| `test_w1_41_legacy.py::test_the_imported_mcp_server_keeps_its_command` | 1 | A .rulesync file holds "ledger" with ledger-mcp. | S3 |
| `test_w1_41_legacy.py::test_the_index_is_refreshed_after_the_retirement` | 1 | Doctor reports index_freshness `fresh`. | S5 |
| `test_w1_41_legacy.py::test_the_retirement_of_the_memory_store_is_a_cit_e` | 1 | cit_e` is a committed change-execution-record naming each store file. | S5; CAP-42.b |
| `test_w1_41_legacy.py::test_what_the_path_map_keeps_is_untouched_by_the_retirement` | 1 | Every unplanned path outside .rulesync/ keeps its blob. | S6 |
| `test_w1_41_migration.py::test_a_backup_ref_that_no_longer_resolves_stops_the_migration` | 1 | Backup ref deleted: A6 refuses naming it; no origin moved. | S2; DEC-449 |
| `test_w1_41_migration.py::test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay` | 1 | Read-only target folder: A6 refuses; batch 1 stays; tree equals batch 2's point. | S2; CAP-44.d |
| `test_w1_41_migration.py::test_a_tree_that_is_dirty_at_a6_is_not_migrated` | 1 | Untracked file: A6 refuses naming it; nothing moved. | S2 |
| `test_w1_41_migration.py::test_every_moved_file_is_byte_for_byte_what_it_was` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_migration.py::test_no_other_tracked_file_changes_content_during_a_move_batch` | 1 | Three batches done with own commits; only planned origins gone, planned targets or records added. | F1; CAP-44.d |
| `test_w1_41_migration.py::test_the_index_refresh_follows_the_moves` | 1 | Doctor index not fresh before A6, fresh after. | S2; CAP-44.d |
| `test_w1_41_migration.py::test_the_rollback_points_are_the_ones_the_plan_recorded` | 1 | A6's rollback points equal A4's. | S1, S2; CAP-44.b, CAP-44.d |
| `test_w1_41_path_map.py::test_a_code_graph_that_cannot_be_read_refuses_and_records_no_importers` | 1 | Tool off PATH: A3 refuses naming the code graph; HEAD unchanged. | S4; DEC-449 |
| `test_w1_41_path_map.py::test_a_justification_that_states_only_one_of_the_two_grounds_is_refused` | 2 | One ground only: refused, file named. | S7; CAP-44.j |
| `test_w1_41_path_map.py::test_a_justified_move_out_of_a_native_layout_is_recorded_with_both_grounds` | 1 | Both grounds: MOVE recorded showing both texts. | S7 |
| `test_w1_41_path_map.py::test_a_move_among_retirements_is_refused_as_a_whole_where_code_intelligence_is_off` | 1 | Retirements plus one MOVE: refused whole; nothing moved or retired. | DEC-517 |
| `test_w1_41_path_map.py::test_a_move_onto_an_artefact_that_stays_is_refused` | 1 | MOVE onto the kept guide is refused, named. | CAP-06.b |
| `test_w1_41_path_map.py::test_a_move_out_of_a_native_layout_without_a_justification_is_refused` | 1 | MOVE of src/app/core.py without justification is refused, named. | S7; CAP-44.j |
| `test_w1_41_path_map.py::test_a_move_where_code_intelligence_is_off_is_refused_and_writes_nothing` | 3 | Code intelligence off: MOVE/RENAME refused, naming artefact, "code intelligence", "importer"; nothing written. | DEC-517 (5678), DEC-523 |
| `test_w1_41_path_map.py::test_a_move_without_a_target_is_refused` | 1 | MOVE without a target is refused, named. | CAP-06.b |
| `test_w1_41_path_map.py::test_a_path_the_inventory_does_not_hold_is_refused` | 1 | A path absent from the inventory is refused, named. | CAP-44.b |
| `test_w1_41_path_map.py::test_a_proposal_that_cannot_be_read_is_refused` | 1 | An invalid-YAML proposal is refused; HEAD unchanged. | DEC-449 |
| `test_w1_41_path_map.py::test_a_proposal_that_moves_nothing_is_recorded_where_code_intelligence_is_off` | 1 | Code intelligence off: the legacy proposal is recorded as proposed, else KEEP. | DEC-517 |
| `test_w1_41_path_map.py::test_a_split_a_merge_or_an_extract_where_code_intelligence_is_off_is_refused_and_writes_nothing` | 3 | SPLIT/MERGE/EXTRACT refused the same way; no target exists. | DEC-535 (5835) |
| `test_w1_41_path_map.py::test_an_action_outside_the_eight_is_refused` | 4 | A3 refuses ARCHIVE/COPY/move/empty, naming the guide; nothing written. | CAP-06.b |
| `test_w1_41_path_map.py::test_an_artefact_given_two_actions_is_refused` | 1 | Two actions for notes.txt refused, named. | CAP-06.b |
| `test_w1_41_path_map.py::test_each_of_the_eight_actions_is_recorded_as_proposed` | 1 | All eight actions recorded with targets. | S1; CAP-06.b |
| `test_w1_41_path_map.py::test_every_artefact_has_exactly_one_of_the_eight_actions` | 1 | Each artefact has one of the eight actions: the proposed one, else KEEP. | S1; CAP-06.b |
| `test_w1_41_path_map.py::test_every_artefact_to_be_moved_carries_importers_references_and_consumers` | 1 | Moved entries have the three keys as lists. | S4; CAP-06.d |
| `test_w1_41_path_map.py::test_no_later_stage_moves_what_was_refused_where_code_intelligence_is_off` | 1 | After the refusal, A4 and A6 refuse and move nothing. | DEC-517 |
| `test_w1_41_path_map.py::test_the_importer_of_a_moved_module_is_read_from_the_code_graph` | 1 | lib/util.py's importers name scripts/run.py. | S4 |
| `test_w1_41_path_map.py::test_the_plan_has_the_proposed_batches_each_with_its_own_rollback_point` | 1 | A4 batches 1–3 in order, own refs/ points, proposed paths; nothing moved. | S1; CAP-44.b |
| `test_w1_41_path_map.py::test_the_references_and_consumers_of_a_moved_record_are_read_from_the_record_graph` | 1 | dec-300's references name DEC-301; consumers name scripts/run.py. | S4 |
| `test_w1_41_unknown.py::test_a2_names_the_unknown_artefact` | 1 | A2 `unknown` is exactly vault/ledger.bin, with no namespace. | F4; CAP-06.c |
| `test_w1_41_unknown.py::test_a_path_map_that_moves_or_deletes_the_unknown_artefact_is_refused` | 4 | Any destructive action on the unknown artefact is refused, named; its bytes stay. | F4; CAP-06.c |
| `test_w1_41_unknown.py::test_a_project_without_unknown_artefacts_raises_no_package_about_one` | 1 | No unknowns: `packages: []`. | S1 |
| `test_w1_41_unknown.py::test_an_unknown_artefact_blocks_the_whole_destructive_migration` | 1 | Artefact kept and A5 passed: A6 refuses naming it; nothing moved. | F4; P-5 |
| `test_w1_41_unknown.py::test_the_unknown_artefact_becomes_a_decision_package_for_the_customer` | 1 | A committed PROPOSED decision package in the kernel form names the artefact. | S1; DEC-093 (846), DEC-308 |
| `test_w1_41_verdict.py::test_a5_names_a_verdict_file_that_does_not_exist` | 1 | A5 refuses naming the missing file; A6 refuses; nothing moved. | F2; DEC-449 |
| `test_w1_41_verdict.py::test_a6_without_any_verdict_moves_nothing` | 1 | A6 without A5 refuses naming A5 or verdict; nothing moved. | F2; CAP-44.c |
| `test_w1_41_verdict.py::test_a_passing_verdict_of_the_independent_auditor_is_recorded_by_a5` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_path_map_that_changes_after_a5_passed_is_not_executed` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_plan_that_is_not_the_audited_path_maps_plan_is_not_executed` | 2 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_about_a_path_map_that_changed_afterwards_moves_nothing` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_from_the_session_that_made_the_path_map_moves_nothing` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_not_committed_by_the_independent_auditor_moves_nothing` | 3 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_that_cannot_be_read_moves_nothing` | 4 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_that_is_not_a_pass_moves_nothing` | 3 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_w1_41_verdict.py::test_a_verdict_written_and_not_committed_moves_nothing` | 1 | Uncommitted verdict: A5 refuses naming its path; nothing moved. | F2 |

**W1-44**: W1-44 (DAEO-wqd6); 4 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w1_44_lessons.py::test_anti_snowball_lesson_states_one_disposition_rule` | 1 | The first lesson mentioning anti-snowball states all six dispositions. | KPI S3; CAP-59.c; DEC-433 |
| `test_w1_44_lessons.py::test_every_lesson_has_scope_severity_and_source` | 1 | its scope and severity half is also schema-required (the case above); its source reference (DEC-168, … | KPI F1; CAP-41.f; DEC-168 |
| `test_w1_44_lessons.py::test_lessons_exist_and_are_schema_valid` | 1 | every lesson schema-valid, L-0074 present, at least five (lessons.py:50-63); there are exactly five … | KPI S1; CAP-41.d, CAP-41.f; DEC-168 |
| `test_w1_44_lessons.py::test_no_lesson_restates_policy_as_authority` | 1 | no lesson is AUTHORITATIVE (lessons.py:184-188): the machine-readable form of CAP-41.b's rule; a body that restates … | KPI F2; CAP-41.b |

**W2-02**: W2-02 (DAEO-zflj); 20 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_w2_02_code_under_test.py::test_the_processes_the_suite_starts_run_this_worktrees_code` | 1 | an oracle check of the suite's own environment (w2_02_support.py:55-69): a child process imports this worktree's gov … | DEC-732, DEC-822 item 3 |
| `test_w2_02_failure.py::test_a_record_whose_type_is_missing_or_no_text_is_still_schema_invalid_type` | 2 | [a-list] (a type that is a list) is its own; [missing] repeats a W2-54 case (its row) | F; DEC-626 |
| `test_w2_02_failure.py::test_an_audit_report_missing_both_milestone_and_pack_hash_names_both` | 1 | A report lacking both fields gets findings naming each | F; DEC-441 |
| `test_w2_02_green_here.py::test_core_schema_reads_the_w1_43_report_as_valid_in_a_project_of_its_own` | 1 | The real W1-43 report, copied into a TP, gets no finding; exit 0 | S2; DEC-441, DEC-626 |
| `test_w2_02_green_here.py::test_core_schema_reads_the_wave_1_exit_report_as_valid_here` | 1 | a 'still green' guard (README:86): the exit report has no frontmatter, which core-schema skips (schema.py:198-200); it … | S2 [W2-M309] |
| `test_w2_02_record_types.py::test_a_close_record_that_names_no_ticket_is_refused` | 1 | The same record without `task` gets a finding naming task; exit ≠ 0 | S1; DEC-872 |
| `test_w2_02_record_types.py::test_a_verdict_record_without_one_of_the_three_verdicts_is_refused` | 4 | ADOPTED, pass, lower case or missing: a finding names the verdict field; exit ≠ 0 | S1; DEC-741 |
| `test_w2_02_record_types.py::test_each_of_the_three_verdicts_is_a_well_formed_verdict` | 3 | A verdict record with each verdict and agreeing named conditions gets no finding; exit 0 | S1; DEC-741 I (ii), DEC-749 |
| `test_w2_02_record_types.py::test_one_kernel_schema_states_the_three_verdicts_of_cap_44_h` | 1 | Exactly one kernel schema has a property whose values are the three CAP-44.h verdicts, and a constant type | S1 [AR-9, W2-M317]; DEC-722, DEC-741 |
| `test_w2_02_record_types.py::test_the_close_record_gov_close_writes_passes_core_schema` | 1 | The close record a real `gov close` wrote gets no finding in a TP; exit 0 | S1; DEC-872 (reg. 9524) |
| `test_w2_02_record_types.py::test_the_kernel_has_one_schema_of_the_close_type` | 1 | Exactly one kernel schema's type constant is `close | S1 [AR-9]; DEC-872 |
| `test_w2_02_unmeasured.py::test_a_project_with_no_schema_file_at_all_is_not_green` | 1 | With no schema file at all, a research record gives an "unmeasured" finding; exit ≠ 0 | S3 |
| `test_w2_02_unmeasured.py::test_a_type_whose_schema_file_is_present_is_not_reported_unmeasured` | 1 | With every schema present, a research record gets no "unmeasured" finding; exit 0 | S3 |
| `test_w2_02_verdict_conditions.py::test_a_condition_missing_its_name_source_item_or_state_is_refused` | 3 | A condition without its name, source or state is refused on conditions | S1; DEC-741, DEC-749 |
| `test_w2_02_verdict_conditions.py::test_a_condition_whose_state_is_not_one_of_the_three_words_is_refused` | 3 | The states `waived`, `not_met` and `Met` are refused | S1; DEC-741 |
| `test_w2_02_verdict_conditions.py::test_a_verdict_record_without_its_list_of_conditions_is_refused` | 2 | Missing conditions, or a text in their place, is refused on the conditions field, beside a clean twin record | S1; DEC-741 I (ii), DEC-749 |
| `test_w2_02_verdict_conditions.py::test_an_accepted_condition_without_its_owner_entry_is_refused` | 2 | An accepted condition with no owner entry, or one that is not a DEC id, is refused | S1; DEC-741 answer F, DEC-749 |
| `test_w2_02_verdict_conditions.py::test_the_verdict_schema_types_its_list_of_named_conditions` | 1 | The verdict schema has the conditions list (state, name, source, owner entry) and requires it | S1; DEC-741 I (ii), DEC-746 item 4 |
| `test_w2_02_wbs_grammar.py::test_the_ticket_schema_takes_its_wbs_id_grammar_from_the_one_definition` | 1 | the $ref and no wbs pattern elsewhere (wbs_grammar.py:45-56); W1-08's two id-grammar cases hold the kernel half, its … | S4; DEC-730, DEC-227 |
| `test_w2_02_wbs_grammar.py::test_the_wbs_id_grammar_still_refuses_every_other_form` | 8 | eight refused forms (wbs_grammar.py:37-42); [W2-15ab] is also in a builder test outside the area … | S4; DEC-730, DEC-746 item 3 (reg. 8088), DEC-750 … |

**unit/adapters**: builder tests of W1-38; 60 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_portability.py::TestExpectedVersion::test_absent_registry_is_a_reason` | 1 | Without a registry the version is None and the reason names the registry path | DEC-127 |
| `test_portability.py::TestExpectedVersion::test_reads_the_rulesync_entry` | 1 | _expected_version returns ("24.0.0", "") for a registry naming rulesync 24.0.0 | DEC-127 |
| `test_portability.py::TestExpectedVersion::test_registry_without_rulesync_is_a_reason` | 1 | A registry naming only uv gives None and "no rulesync entry" | DEC-127 |
| `test_portability.py::TestExpectedVersion::test_unreadable_registry_is_a_reason` | 4 | Unparsable text, a list, a non-list tools value or an empty file: version None | DEC-127, DEC-425 |
| `test_portability.py::TestFindRulesync::test_named_binary` | 1 | RULESYNC_BIN naming an existing file is returned | DEC-425 |
| `test_portability.py::TestFindRulesync::test_named_binary_that_is_no_file` | 1 | RULESYNC_BIN naming no file gives None | DEC-425 |
| `test_portability.py::TestGeneratedFindings::test_changed_file_is_one_finding_naming_it` | 5 | Each generated file with one byte changed gives exactly one GENERATED_DIFFERS naming it | KPI F2 |
| `test_portability.py::TestGeneratedFindings::test_failing_exit_is_a_failure_although_the_files_were_written` | 1 | Exit 1 with every file written: RULESYNC_FAILED, nothing counted | DEC-425, DEC-449 |
| `test_portability.py::TestGeneratedFindings::test_failure_is_reported_with_rulesync_s_reason_and_no_file` | 1 | A failing stand-in naming CLAUDE.md in its reason: RULESYNC_FAILED with no file, reason kept | DEC-425 |
| `test_portability.py::TestGeneratedFindings::test_file_outside_the_generated_folders_is_not_judged` | 4 | settings.local.json, a worktree file, .claude/other.json and docs/: no finding | DEC-063, DEC-050, DEC-471 |
| `test_portability.py::TestGeneratedFindings::test_file_without_a_source_is_one_finding_naming_it` | 5 | A hand-written file in agents, skills, a generated skill, commands or a deep commands folder: GENERATED_WITHOUT_SOURCE | DEC-471 |
| `test_portability.py::TestGeneratedFindings::test_long_reason_is_reported_by_its_end` | 1 | A 5,000-character reason is reported by its end, in under 600 characters | DEC-425 |
| `test_portability.py::TestGeneratedFindings::test_missing_file_is_a_finding` | 1 | CLAUDE.md missing: GENERATED_DIFFERS for CLAUDE.md | KPI F2 |
| `test_portability.py::TestGeneratedFindings::test_no_root_rule_is_a_finding_and_nothing_is_counted` | 3 | No root rule (none, a plain rule, root false): ROOT_RULE_ABSENT, nothing counted | CAP-52.a |
| `test_portability.py::TestGeneratedFindings::test_project_holding_what_rulesync_writes` | 1 | A project holding exactly what the stand-in writes: no finding, five files compared | CAP-38.b; KPI S3 |
| `test_portability.py::TestGeneratedFindings::test_rulesync_is_given_the_project_s_sources_and_writes_nothing_in_the_project` | 1 | rulesync is called with generate … --input-roots <project>/.rulesync, without --delete; the project is untouched | DEC-471, DEC-641 |
| `test_portability.py::TestGeneratedFindings::test_rulesync_that_writes_nothing_is_a_failure_not_a_match` | 1 | A generation that writes nothing: RULESYNC_FAILED with "0 files written" | DEC-449, DEC-425 |
| `test_portability.py::TestGeneratedFindings::test_settings_key_added_or_removed_by_hand` | 5 | Four added keys or a removed deny rule in settings.json: one GENERATED_DIFFERS for it | DEC-471 |
| `test_portability.py::TestHeldOutStep::test_broken_held_out_file_is_one_finding_without_a_path_and_nothing_is_compared` | 5 | Five broken held-out texts: one HELD_OUT_STEP_FAILED, nothing counted, no path in the findings | DEC-218, DEC-641 |
| `test_portability.py::TestHeldOutStep::test_folder_in_place_of_the_held_out_file_is_a_finding` | 1 | A folder at the held-out file's place: HELD_OUT_STEP_FAILED | DEC-641 |
| `test_portability.py::TestHeldOutStep::test_generated_then_the_step_has_no_finding` | 1 | Settings after write_read_rules (two rules) match the check's own step: no finding | DEC-635, DEC-641 |
| `test_portability.py::TestHeldOutStep::test_generation_without_settings_is_a_finding_not_a_match` | 1 | A generation without settings.json: HELD_OUT_STEP_FAILED | DEC-641 |
| `test_portability.py::TestHeldOutStep::test_main_is_not_green_and_prints_no_path` | 1 | main() with a broken held-out file: exit 1, only HELD_OUT_STEP_FAILED, no path printed | DEC-641, DEC-604 |
| `test_portability.py::TestHeldOutStep::test_one_rule_lost_is_a_finding` | 1 | One step rule removed: GENERATED_DIFFERS for settings | DEC-635 |
| `test_portability.py::TestHeldOutStep::test_rules_without_a_held_out_file_are_a_finding` | 1 | Step rules kept, held-out file removed: GENERATED_DIFFERS for settings | DEC-641 |
| `test_portability.py::TestHeldOutStep::test_settings_without_the_step_are_a_finding_and_no_path_is_carried` | 1 | A held-out file without the step: GENERATED_DIFFERS for settings, no invented path in the findings | DEC-635, DEC-641, DEC-162 |
| `test_portability.py::TestHeldOutStep::test_the_step_writes_nothing_in_the_project` | 1 | The check leaves every project file's bytes unchanged | DEC-641 |
| `test_portability.py::TestKernelFindings::test_agreeing_project_has_no_finding_and_counts_what_it_compared` | 1 | An agreeing kernel and sources give no finding and count four compared files | DEC-471; CAP-38.b |
| `test_portability.py::TestKernelFindings::test_kernel_role_changed` | 1 | A changed kernel role gives one finding naming the source, with the kernel file in its message | DEC-471, DEC-066 |
| `test_portability.py::TestKernelFindings::test_kernel_role_without_a_tools_field_is_a_finding` | 1 | No Tools field in the kernel role: SOURCE_TOOLS_DIFFER, "no Tools field" | DEC-471, DEC-066 |
| `test_portability.py::TestKernelFindings::test_role_source_changed` | 1 | A changed role-source body gives one SOURCE_DIFFERS naming the source | DEC-471 |
| `test_portability.py::TestKernelFindings::test_role_source_frontmatter_is_not_part_of_the_pair` | 1 | Other frontmatter in a role source, with the same tools set, gives no finding | DEC-471 |
| `test_portability.py::TestKernelFindings::test_role_source_with_other_tools_names_the_source_and_the_difference` | 3 | An extra tool, a missing tool or a lower-case bash: SOURCE_TOOLS_DIFFER stating the difference | DEC-471 (equal, not within) |
| `test_portability.py::TestKernelFindings::test_role_source_without_a_tools_list_is_a_finding` | 3 | No claudecode, tools as a string, or no frontmatter: SOURCE_TOOLS_DIFFER naming claudecode.tools | DEC-471 |
| `test_portability.py::TestMain::test_green_says_what_was_compared` | 1 | Exit 0 and compared = version true, four kernel files, five generated files | CAP-38.b; DEC-449 |
| `test_portability.py::TestMain::test_kernel_is_compared_also_without_rulesync` | 1 | No binary and a changed kernel role: RULESYNC_ABSENT, then SOURCE_DIFFERS | DEC-425 |
| `test_portability.py::TestMain::test_other_version_stops_before_the_generated_files` | 1 | 99.0.0: exit 1, only RULESYNC_VERSION_DIFFERS saying not compared, no generated file counted | DEC-127, DEC-449 |
| `test_portability.py::TestMain::test_rulesync_failure_is_not_counted_as_compared` | 1 | A failing generation: exit 1, generated_files 0 | DEC-449 |
| `test_portability.py::TestSplit::test_blank_lines_after_frontmatter_are_dropped` | 1 | Blank lines after the frontmatter are dropped; quoting does not change the parsed frontmatter | DEC-471; W1-38 README "the one tolerated … |
| `test_portability.py::TestSplit::test_file_without_frontmatter` | 1 | A file without frontmatter splits into (None, its text) | DEC-471 |
| `test_portability.py::TestSplit::test_nothing_else_is_tolerated` | 1 | A trailing blank line in the body makes two splits differ | DEC-471 |
| `test_portability.py::TestToolsDifference::test_empty_kernel_is_a_finding` | 1 | A kernel with neither role nor skill: KERNEL_EMPTY, nothing counted | DEC-425 |
| `test_portability.py::TestToolsDifference::test_empty_list_is_compared_not_skipped` | 1 | An empty tools list is compared, and its difference reported | DEC-471 |
| `test_portability.py::TestToolsDifference::test_field_is_read_to_the_end_of_its_indented_lines_by_whole_words` | 5 | Five bodies naming Read and Edit in the field, other tools outside it or inside words: no difference | DEC-471 |
| `test_portability.py::TestToolsDifference::test_kernel_of_this_repository` | 1 | A kernel under template/governance/kernel is found and compared: ([], 4) | DEC-186, DEC-579 |
| `test_portability.py::TestToolsDifference::test_no_kernel_is_a_finding` | 1 | No kernel folder: KERNEL_ABSENT, nothing counted | DEC-425 |
| `test_portability.py::TestToolsDifference::test_order_and_repetition_are_free` | 1 | Order and repetition in claudecode.tools do not matter | DEC-471 |
| `test_portability.py::TestToolsDifference::test_skill_body_changed_on_either_side` | 2 | A kernel or a source SKILL.md changed: one finding naming the source | DEC-471 |
| `test_portability.py::TestToolsDifference::test_skill_frontmatter_changed` | 1 | A changed source frontmatter value is a finding | DEC-471 |
| `test_portability.py::TestToolsDifference::test_source_file_the_kernel_does_not_hold` | 1 | An extra skill source file and an extra role source: SOURCE_WITHOUT_KERNEL for each | DEC-471 |
| `test_portability.py::TestToolsDifference::test_source_skill_that_is_no_kernel_skill_is_left_alone` | 1 | An openspec-* source skill without a kernel skill is no finding | DEC-468 |
| `test_portability.py::TestToolsDifference::test_supporting_file_changed` | 1 | A supporting file whose bytes differ is a finding naming the source file | DEC-244, DEC-471 |
| `test_portability.py::TestToolsDifference::test_supporting_file_without_source` | 1 | A kernel supporting file without its source: SOURCE_MISSING | DEC-244 |
| `test_portability.py::TestToolsDifference::test_tool_named_on_a_continuation_line_counts` | 1 | WebSearch on an indented continuation line counts as named | DEC-471 |
| `test_portability.py::TestVersionFinding::test_no_binary_is_a_finding` | 1 | No binary: RULESYNC_ABSENT with "not found" | DEC-425 |
| `test_portability.py::TestVersionFinding::test_no_registry_is_a_finding_even_with_rulesync` | 1 | No registry, with a stand-in present: RULESYNC_VERSION_UNKNOWN | DEC-127, DEC-425 |
| `test_portability.py::TestVersionFinding::test_none_when_installed_is_expected` | 1 | A stand-in answering 24.0.0 against registry 24.0.0 gives no finding | DEC-127 |
| `test_portability.py::TestVersionFinding::test_other_installed_version_names_both` | 1 | A stand-in answering 99.0.0: RULESYNC_VERSION_DIFFERS naming both versions | DEC-127 |
| `test_portability.py::TestVersionFinding::test_rulesync_without_answer_is_a_finding` | 1 | A stand-in sleeping 30 s, TIME_LIMIT patched to 1: RULESYNC_FAILED with "no answer" | DEC-425; DEC-871 |
| `test_portability.py::TestVersionFinding::test_version_is_compared_whole` | 1 | Registry 4.0.0 against installed 24.0.0 is a difference, not a substring match | DEC-127 |

**unit/adopt**: builder tests of W1-41; 16 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_adopt.py::test_a3_records_no_path_map_whose_namespace_states_another_policy_or_none_embedded` | 3 | A3 raises EMBEDDING_POLICY with both values and "no namespace is embedded"; nothing recorded. | DEC-694, DEC-700 |
| `test_adopt.py::test_a_backup_ref_that_no_longer_resolves_stops_the_migration` | 1 | Deleted backup ref: A6 raises BACKUP_REF; origin stays. | S2; DEC-449 |
| `test_adopt.py::test_a_batch_that_fails_is_rolled_back_and_the_batches_after_it_do_not_run` | 1 | Batch 2 fails: BATCH_FAILED, done [1], HEAD at batch 1, no A6 record. | CAP-44.d |
| `test_adopt.py::test_a_memory_store_a_kept_legacy_rule_file_cites_is_not_retired` | 7 | Five citation forms and two citing records: A8 raises STORE_STILL_CITED with exact citers. | CAP-42.b; DEC-552, DEC-568 |
| `test_adopt.py::test_a_plan_changed_after_a4_is_not_the_audited_path_maps_plan_and_is_not_executed` | 3 | Changed A4 plus a passing A5: A6 raises PLAN_NOT_THE_PATH_MAPS; A8 raises STAGE_MISSING. | F2 |
| `test_adopt.py::test_a_record_changed_after_the_next_stage_stood_on_it_breaks_the_chain` | 1 | An edited A0 record makes A2 raise CHAIN_BROKEN at A1. | README interface 5 |
| `test_adopt.py::test_a_stage_refuses_without_the_stage_before_it_and_on_a_dirty_tree` | 1 | A1 raises STAGE_MISSING (A0); A0 with an untracked file raises TREE_NOT_CLEAN listing it. | CAP-44.b |
| `test_adopt.py::test_a_verdict_does_not_hold_for_a_path_map_or_a_verdict_that_changed_after_it` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_adopt.py::test_agents_md_is_imported_one_section_at_a_time` | 1 | _sections` splits AGENTS.md, dropping a heading-only section. | S3; CAP-42.a |
| `test_adopt.py::test_an_unknown_artefact_gets_a_decision_package_and_is_only_kept` | 1 | A2 lists the unknown with a package; deleting it at A3 raises PROPOSAL_REFUSED. | CAP-06.c |
| `test_adopt.py::test_no_move_is_recorded_where_code_intelligence_is_off` | 1 | MOVE with code intelligence off raises CODE_INTELLIGENCE_OFF; nothing recorded. | DEC-517 |
| `test_adopt.py::test_nothing_moves_without_an_accepted_verdict` | 6 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_adopt.py::test_the_migration_moves_what_the_audited_map_says_and_changes_no_content` | 1 | valid for A5's rule as built (src/gov/adopt/stages.py:315-338); its fixture writes the A5 review as type … | CAP-44.c, DEC-490, DEC-454; the type: DEC-741 I … |
| `test_adopt.py::test_the_plan_flags_the_importer_and_refuses_what_changes_content` | 1 | A4 rollback refs and the stubbed importer flagged; SPLIT makes A4 raise CONTENT_CHANGE. | S4, F1; P-7 |
| `test_adopt.py::test_the_tools_own_import_of_an_mdc_keeps_its_body_and_globs_in_plain_yaml` | 1 | _mdc` keeps body and globs in plain YAML; bad globs raise ValueError. | CAP-42.a; DEC-517 |
| `test_adopt.py::test_without_lite_the_command_stays_reserved_and_lite_needs_a_stage` | 1 | In-process: no --lite raises NOT_IMPLEMENTED; --lite without --stage exits 2. | DEC-090; DEC-136 |

**unit/bridge**: builder tests of W1-14; 4 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_bridge.py::test_a_checkbox_line_that_is_no_task_refuses_the_derivation` | 3 | No number, no description or a repeated number gives TASKS_INVALID and no ticket. | DEC-355 |
| `test_bridge.py::test_a_ticket_records_its_task_and_a_second_run_finds_it` | 1 | The ticket records task, specification and title; a second run returns the same result. | DEC-356 L3635; DEC-136 (builder test) |
| `test_bridge.py::test_a_ticket_script_that_fails_leaves_no_ticket` | 1 | tk refusing a title that starts with "-x" gives TICKET_FAILED, and the first task's ticket is removed. | bridge.py docstring ("a refusal writes nothing"); … |
| `test_bridge.py::test_what_covers_the_acceptance_tests` | 6 | _covers judges six patterns as the guard reads them. | MR-3; DEC-156 |

**unit/cli**: builder tests of W1-07; 7 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_cli.py::test_a_usage_error_ends_with_exit_code_2` | 1 | In-process `status --no-such-option --json` raises SystemExit(2) with empty stdout | W1-07 S1 |
| `test_cli.py::test_a_valid_path_map_loads` | 1 | In-process status with a minimal map plus an unknown key: exit 0, ok, config_files == [path-map.yaml] | W1-07 S3a; DEC-185, DEC-189 |
| `test_cli.py::test_an_invalid_check_declaration_is_refused_not_listed` | 4 | A non-map, a missing field, an unknown severity or a non-string field gives CHECK_DECLARATION_INVALID with file and key | W1-07 S4; DEC-186 |
| `test_cli.py::test_config_invalid_names_the_file_and_the_key` | 3 | Missing, non-map or value-non-map namespaces: exit 1, CONFIG_INVALID, details == {file, key}, message names both | W1-07 S3a; DEC-185, DEC-189 |
| `test_cli.py::test_one_check_id_declared_differently_in_the_two_layouts_is_refused` | 1 | One id declared differently in the two layouts is refused, naming the differing key | DEC-579 |
| `test_cli.py::test_the_declarations_of_both_layouts_are_listed_each_check_once` | 1 | One declared alike in both layouts is one check; an installed-only file is listed | DEC-579 (L6232) |
| `test_cli.py::test_the_read_commands_are_those_of_cap_27` | 1 | the read set equals CAP-27's seven (test_cli.py:93-95); its third line (:96) cannot fail: the static COMMANDS never … | W1-07 S2; CAP-27; DEC-187 |

**unit/decisions**: builder tests of W1-11; 20 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_decisions.py::test_a_commit_with_the_owner_s_role_and_another_is_no_approval` | 1 | A commit carrying both `Role: engineer` and `Role: owner` is ACTIVE_UNAPPROVED | DEC-360; DEC-861 item 6 ("Role: owner alone", … |
| `test_decisions.py::test_a_decision_file_removed_and_added_again_needs_its_own_approval` | 1 | The owner removes ADR-0001 and an agent re-adds it ACTIVE: flagged | DEC-360 |
| `test_decisions.py::test_a_folder_inside_a_repository_is_not_checked_as_a_project` | 1 | A subfolder raises GovError DECISIONS_NOT_A_REPOSITORY with details {"root": …} | builder; interface |
| `test_decisions.py::test_a_head_that_looks_like_frontmatter_and_a_decision_without_an_id_are_findings` | 6 | Blank-line, `--- \t# c` and UTF-16BE heads are unreadable; `----` and `---x` are not; a decision with no id gives … | DEC-387 |
| `test_decisions.py::test_a_key_written_twice_cannot_be_read` | 1 | status` written twice gives FRONTMATTER_UNREADABLE and nothing else | DEC-387 |
| `test_decisions.py::test_a_merge_that_holds_the_file_of_every_parent_is_not_read_at_all` | 1 | read_merge is never called when every parent holds the file: [] | DEC-398 |
| `test_decisions.py::test_a_merge_that_keeps_a_moved_file_over_a_removal_at_the_old_path_is_the_commit_that_set_it` | 2 | A move on one side and a removal on the other: the engineer's merge is flagged, the owner's gives [] | DEC-398, DEC-418 |
| `test_decisions.py::test_a_merge_that_keeps_active_over_a_demotion_made_beside_it_is_the_commit_that_set_it` | 2 | Owner edit on one side, demotion on the other: the engineer's merge is flagged, the owner's gives [] | DEC-398 |
| `test_decisions.py::test_a_merge_that_keeps_the_owner_s_file_over_an_agent_s_is_the_commit_that_set_it` | 2 | a builder test beside W1-11's merge-base case of the same shape (2.1's rule); its [owner] half is its own; its … | DEC-398 |
| `test_decisions.py::test_a_merge_the_helper_cannot_read_approves_nothing_and_the_check_writes_nothing` | 1 | When read_merge refuses, even the owner's merge is flagged, and no file changes | DEC-398, DEC-410 |
| `test_decisions.py::test_a_partial_clone_is_read_as_it_is_and_nothing_is_fetched` | 1 | A blob:none clone raises GovError and gains no new path | builder; S3 |
| `test_decisions.py::test_a_replace_ref_is_not_read` | 1 | a builder test beside W1-11's replace-ref case, the same function called in-process (2.1's rule) | DEC-387 |
| `test_decisions.py::test_a_ticket_whose_frontmatter_cannot_be_read_still_waits_on_a_dead_package` | 1 | An unreadable ticket named by a STALE package gives FRONTMATTER_UNREADABLE and TICKET_WAITS_ON_DEAD_GATE | DEC-330 |
| `test_decisions.py::test_an_agent_commit_that_only_moves_a_decision_the_owner_approved_sets_nothing` | 1 | An agent's pure move of an owner-approved decision gives [] | DEC-360, DEC-387 |
| `test_decisions.py::test_an_agent_merge_of_a_decision_the_owner_edited_or_added_on_a_branch_sets_nothing` | 1 | An agent's merge of the owner's branch edit and addition gives [] | DEC-398, DEC-418 |
| `test_decisions.py::test_an_object_the_repository_does_not_hold_is_an_error` | 4 | Deleting a loose blob, tree or commit makes the check raise GovError | builder; DEC-360 |
| `test_decisions.py::test_git_dir_of_the_caller_names_no_other_repository` | 1 | a builder test beside the three git_environment.py cases, and stricter (it also refuses a subfolder as the root, … | DEC-387 |
| `test_decisions.py::test_one_of_two_records_with_the_cited_id_that_is_no_accepted_gate_does_not_authorise` | 1 | Two DP-1 records, one REVOKED: GATE_NOT_AUTHORISING | DEC-331 |
| `test_decisions.py::test_the_check_reads_head_and_needs_no_store` | 1 | Gives [] at HEAD; an uncommitted `superseded_by` is ignored; no .gov-runtime is created | builder regression (DEC-136); DEC-329 |
| `test_decisions.py::test_the_decision_id_grammar_is_the_kernel_s` | 1 | The checker's DECISION_ID equals the decision_id pattern in common.schema.json | DEC-227 |

**unit/doctor**: builder tests of W1-27; 35 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_doctor.py::TestHasStandaloneOldPath::test_multiple_new_path_occurrences_hide_old` | 1 | only new-path occurrences: False | DEC-456 |
| `test_doctor.py::TestHasStandaloneOldPath::test_no_old_path_at_all` | 1 | no old path: False | DEC-456 |
| `test_doctor.py::TestHasStandaloneOldPath::test_old_path_between_new_paths` | 1 | standalone old path between new ones: True | DEC-456 |
| `test_doctor.py::TestHasStandaloneOldPath::test_old_path_not_suffix_of_new` | 1 | unrelated old name: True | DEC-456 |
| `test_doctor.py::TestHasStandaloneOldPath::test_old_path_only_inside_new_path` | 1 | old path only inside its new path: False | DEC-456 point 3 |
| `test_doctor.py::TestHasStandaloneOldPath::test_old_path_standalone` | 1 | standalone old path: True | DEC-456 |
| `test_doctor.py::TestHasStandaloneOldPath::test_old_path_standalone_alongside_new_path` | 1 | standalone old path beside the new: True | DEC-456 |
| `test_doctor.py::TestIsHistorical::test_archived_sources` | 1 | a docs/source/ file is historical | DEC-448 |
| `test_doctor.py::TestIsHistorical::test_bootstrap` | 1 | bootstrap.md is historical | DEC-448 |
| `test_doctor.py::TestIsHistorical::test_cit_records` | 1 | a docs/changes/ file is historical | DEC-448 |
| `test_doctor.py::TestIsHistorical::test_decision_register` | 1 | the register is historical | DEC-448 |
| `test_doctor.py::TestIsHistorical::test_live_file` | 1 | src/gov/doctor/command.py is not historical | DEC-448 |
| `test_doctor.py::TestIsHistorical::test_nested_cli_is_not_historical` | 1 | src/gov/cli/sub/module.py is not historical | DEC-456 |
| `test_doctor.py::TestIsHistorical::test_old_cli_tree` | 1 | cli/commands.py is historical | DEC-456 |
| `test_doctor.py::TestIsHistorical::test_sources_md` | 1 | docs/SOURCES.md is historical | DEC-456 |
| `test_doctor.py::TestIsHistorical::test_src_gov_cli_is_not_historical` | 1 | src/gov/cli/commands.py is not historical | DEC-456 |
| `test_doctor.py::test_check_adoption_level_minimal` | 1 | no path map: level MINIMAL | S5; CAP-54.a |
| `test_doctor.py::test_check_framework_lock_fails_an_installed_project_without_its_lock` | 1 | answers file without lock: fail, UNLOCKED, reason names framework.lock | CAP-02.a; DEC-499 |
| `test_doctor.py::test_check_framework_lock_missing` | 1 | no lock, no answers: MISSING, unmeasured | CAP-02.a; DEC-488 |
| `test_doctor.py::test_check_framework_lock_reports_the_answer_of_gov_lock` | 6 | each lock verdict maps to its status with reason and drifted files | CAP-02.a; DEC-488, DEC-493, DEC-499 |
| `test_doctor.py::test_check_held_out_missing` | 1 | no file: missing true, status report | S7; DEC-223 |
| `test_doctor.py::test_check_held_out_present` | 1 | empty file present: missing false, status pass | S7; DEC-223 |
| `test_doctor.py::test_check_hooks_no_config` | 1 | no lefthook.yml: config_present false | S1 |
| `test_doctor.py::test_failed_parts_names_each_failed_or_drifted_part_with_its_reason` | 1 | _failed_parts` names failed and drifted parts with string reasons | S1 |
| `test_doctor.py::test_home_uses_env` | 1 | _home()` follows HOME | DEC-452 |
| `test_doctor.py::test_parse_version_list` | 1 | pinned package list parses to name→version | DEC-452 |
| `test_doctor.py::test_pyyaml_sha256_match_always_false` | 1 | pin = yaml.__version__: ok true, sha256_match false | DEC-425 |
| `test_doctor.py::test_pyyaml_version_compared` | 1 | pin 99.99.99: not ok, sha256_match not true, a reason | DEC-452 |
| `test_doctor.py::test_read_dist_version` | 1 | METADATA version read with name normalisation; unknown gives None | DEC-452 |
| `test_doctor.py::test_sha256_file` | 1 | _sha256_file` equals hashlib's digest | CAP-25.a |
| `test_doctor.py::test_sha256_file_missing` | 1 | missing file gives None | CAP-25.a |
| `test_doctor.py::test_the_semantic_canary_says_where_no_namespace_is_embedded_and_adds_no_failure` | 3 | all checks mocked to pass: healthy; the note appears exactly when no policy equals "embedded" | DEC-694 (line 7327), DEC-381 |
| `test_doctor.py::test_vendored_folder_digest` | 1 | DEC-199 digest of a committed folder equals an independent computation | DEC-199 |
| `test_doctor.py::test_version_comparison` | 1 | three orderings of parsed versions | DEC-210 |
| `test_doctor.py::test_version_tuple` | 1 | _version_tuple` turns three version strings into int tuples | S6; DEC-210 |

**unit/lock**: builder tests of W1-39; 16 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_lock.py::test_a_governance_folder_that_cannot_be_searched_is_not_taken_for_no_lock` | 1 | governance/ at mode 0 gives ERROR, not MISSING. | DEC-499 L5479 |
| `test_lock.py::test_a_kernel_folder_that_cannot_be_listed_is_an_error_naming_it_and_no_lock_is_written` | 2 | A kernel folder that cannot be listed (mode 0 or 0o100) gives ERROR naming it; write() refuses and the lock is … | DEC-488 |
| `test_lock.py::test_a_lock_that_is_no_file_is_an_error_with_or_without_an_answers_file` | 2 | A lock that is a folder or a dangling link gives ERROR naming framework.lock. | DEC-488, DEC-499 |
| `test_lock.py::test_a_lock_that_is_not_a_map_is_an_error` | 1 | A lock that is a YAML list gives ERROR. | DEC-488 |
| `test_lock.py::test_a_lock_without_manifest_or_identity_is_an_error` | 4 | An empty or absent manifest, or an absent tag or commit, gives ERROR with a reason. | DEC-488 |
| `test_lock.py::test_a_manifest_that_lists_no_installed_kernel_file_is_an_error` | 1 | A manifest listing only a file outside the kernel gives ERROR, with an empty kernel folder and with none. | DEC-488 L5337 |
| `test_lock.py::test_a_missing_file_listed_without_a_hash_is_drift` | 1 | A missing file listed with a null hash is drift. | DEC-488 |
| `test_lock.py::test_an_answers_file_absent_unreadable_or_without_the_commit_is_an_error` | 3 | With a lock present, an absent, invalid or commit-less answers file gives ERROR. | DEC-488 |
| `test_lock.py::test_edited_missing_and_unreadable_files_are_named` | 1 | an edited, an unreadable and a deleted hook are each drift (test_lock.py:111-121); the unreadable half is skipped … | DEC-488 L5337 |
| `test_lock.py::test_identity_that_differs_from_the_answers_file_is_drift` | 2 | A tag or commit that differs from the answers file gives DRIFT naming the key, with no files. | DEC-488 L5337 |
| `test_lock.py::test_no_lock_beside_an_answers_file_is_unlocked_and_names_the_lock` | 1 | An answers file with no lock gives UNLOCKED naming both and no drifted files; removing the answers file too gives … | DEC-499 L5479 |
| `test_lock.py::test_no_lock_beside_any_entry_named_as_the_answers_file_is_unlocked` | 4 | An answers entry that is empty, not a map, a folder or a dangling link still gives UNLOCKED. | DEC-499 (lock/__init__.py:51-63) |
| `test_lock.py::test_no_lock_is_missing` | 1 | No lock and no answers file give MISSING, "no framework.lock". | DEC-499 L5479 |
| `test_lock.py::test_unlisted_kernel_file_is_drift_and_pycache_is_not` | 1 | __pycache__ files and files outside the kernel leave MATCH; an unlisted kernel file is drift. | DEC-488 L5338 |
| `test_lock.py::test_write_gives_header_identity_answers_reference_and_manifest` | 1 | write() gives the header, tag, commit, answers_file and a manifest of both kernel files; compare() then answers MATCH. | CAP-02.a; DEC-023 L200, DEC-488 L5337 |
| `test_lock.py::test_write_refuses_without_the_commit_or_without_a_kernel` | 1 | write() raises LockError without _template_commit, or with no kernel files. | DEC-488 |

**unit/readiness**: builder tests of W1-13; 7 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_readiness.py::test_a_change_with_no_specification_record_is_invalid_and_the_archive_is_not_a_change` | 1 | The archive is ignored; an empty change folder gives READINESS_INVALID with exit 1, named in the message. | DEC-351, DEC-136 |
| `test_readiness.py::test_a_project_without_the_schema_does_not_pass` | 1 | It passes with the schema, then raises READINESS_INVALID once the schemas folder is removed. | CAP-30.a; DEC-085 |
| `test_readiness.py::test_a_schema_that_adds_a_row_or_a_type_does_not_pass` | 1 | An extra row 27 or an extra type makes check raise READINESS_INVALID. | CAP-30.e; DEC-085 |
| `test_readiness.py::test_a_specification_closed_by_hand_still_gets_its_one_audit_ticket` | 1 | Two closes of a hand-CLOSED complete specification return one audit ticket and leave one ticket file. | DEC-088, DEC-356 |
| `test_readiness.py::test_a_standard_specification_with_no_capability_type_does_not_pass` | 1 | STANDARD with no capability type raises READINESS_INVALID. | DEC-353 |
| `test_readiness.py::test_the_bare_command_does_not_pass_while_one_specification_is_open` | 1 | check_all on an all-MISSING FULL record raises SPEC_NOT_CLOSED with exit 3. | DEC-351 |
| `test_readiness.py::test_the_mandatory_rows_and_the_shipped_schema_are_the_contracts` | 1 | The checker's constants and the shipped schema's rows equal readiness-dimensions.yaml. | CAP-30.a, CAP-53.a; DEC-085, DEC-136 |

**unit/records**: builder tests of W1-10; 1 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_records.py::test_a_register_entry_carries_its_heading_and_title_and_a_file_record_neither` | 1 | records() returns a register entry with heading and title, a file record with neither, and the type and status filters … | DEC-521, DEC-579, DEC-473, DEC-136; CAP-08 |

**unit/status**: builder tests of W1-32; 13 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_status.py::test_a_device_at_the_flags_path_is_a_flag_not_read_and_only_the_mirror_can_say_paused` | 1 | An empty file reads unmarked; a device gives read:false with no paused key; a mirror makes it paused | W1-32 S3; DEC-402, DEC-429 |
| `test_status.py::test_a_doctor_that_gives_no_verdict_or_no_state_is_not_read` | 1 | A raising doctor, or one without states, is read:false; DOCTOR_UNHEALTHY gives healthy false and its parts | W1-32 S2 |
| `test_status.py::test_a_file_the_load_could_not_take_is_listed_with_the_packages_as_not_read` | 2 | An unloadable DP-1.md is listed by its path as read:false beside DP-2 | W1-32 F2; DEC-239, DEC-308 |
| `test_status.py::test_a_flag_that_cannot_be_read_is_paused_and_who_paused_is_not_read` | 1 | absent gives not paused; a directory gives paused with by and since unread; a marker gives by owner and since | W1-32 S3; DEC-402, DEC-404 |
| `test_status.py::test_a_reader_that_fails_is_a_part_not_read_with_its_reason` | 1 | _part` turns a PermissionError into read:false carrying its message | W1-32 F2; DEC-449, DEC-454 |
| `test_status.py::test_a_status_with_a_part_not_read_names_every_such_place` | 1 | run() keys are root, config_files, the six parts, not_read; without the store not_read names ready, blocked, packages | W1-32 S2, F2 |
| `test_status.py::test_a_store_without_its_records_or_edges_does_not_answer` | 2 | Dropping records or edges: the fault names the table; ready and blocked are unread | W1-32 F2; DEC-449 |
| `test_status.py::test_a_ticket_file_that_cannot_be_read_is_listed_as_not_read` | 1 | An unparseable ticket is a blocked read:false entry; the other ticket keeps its reasons | W1-32 F2 |
| `test_status.py::test_a_ticket_folder_that_cannot_be_listed_is_not_no_ticket` | 1 | A file where .tickets/ should be makes the tickets part read:false | W1-32 F2 |
| `test_status.py::test_the_share_is_never_a_figure` | 1 | Share and each ticket's share are "not measured" with a reason; unread tickets make the share unread | W1-32 S2; DEC-491, DEC-540 |
| `test_status.py::test_the_store_answers_only_for_a_history_that_holds_head` | 1 | The store fault is None after the load, "older than HEAD" after a commit, "was not read" without the store | W1-32 F2; DEC-449 |
| `test_status.py::test_what_was_not_read_is_found_at_any_depth_with_its_place` | 1 | _unread_in` gives "tickets.blocked.0: why" | W1-32 S2; DEC-454 |
| `test_status.py::test_without_the_store_ready_blocked_and_packages_are_not_read_and_the_claimed_tickets_are` | 1 | With a fault, ready, blocked and packages are read:false with it; claimed still lists the in-progress ticket | W1-32 S2, F2 |

**unit/tasks**: builder tests of W1-09; 6 functions

| Test | Cases | Holds | Rests on |
|---|---|---|---|
| `test_tasks.py::test_a_constraining_file_the_store_holds_no_record_of_holds_its_tickets` | 1 | The unloaded constraining file is named; an unreadable frontmatter holds every ticket; loaded paths are left out; with … | DEC-544 L5909, DEC-579 L6236 |
| `test_tasks.py::test_a_holder_still_being_written_is_waited_for` | 1 | A losing claim waits for the winner's line, written 0.2 s later, and names that holder. | DEC-292; README:80-83 |
| `test_tasks.py::test_a_release_reads_the_holder_and_removes_the_lock_in_one_step` | 1 | A release waits for the flock on the claims folder, then refuses with CLAIM_NOT_HELD naming the next holder. | DEC-292 L2908-2909; README:133-136 |
| `test_tasks.py::test_a_ticket_file_that_cannot_be_read_is_not_ready` | 1 | An unparsable ticket is blocked and the readable one is READY (store calls patched). | queue.py:5-6 |
| `test_tasks.py::test_a_ticket_id_with_a_path_separator_releases_nothing` | 1 | holder() is None and release raises CLAIM_NOT_HELD for "../../outside"; the outside file stays. | DEC-291 |
| `test_tasks.py::test_no_ticket_is_ready_while_the_store_cannot_be_read` | 1 | With no store, nothing is READY and the ticket is listed as blocked. | queue.py:5-6 (the rule fails closed); DEC-136 |

### 2.4 The planted faults, one row each

Each fault is one edit to the product code, a kernel template or a record in a scratch worktree of my clone
(`wt-plant/`, at `4166d8d9`). The tests that claim to catch the fault were run, and then the file was restored. The
worktree was clean after every run (`git status --porcelain` empty, recorded per run). The last three rows change no
file: they put a stand-in `rulesync` first on the PATH, one that answers after 11 seconds, one second past the 10-second
limit of the portability check, W1-38's session fixture and W1-33's probe.

Results are in `runs/plant/results.jsonl` and the JUnit file of each run, `runs/plant/<id>.xml`, in my folder.
"Claimed by" is the test whose verdict rests on the fault; "green" means it stayed green with the fault in place.

| Fault | What it breaks | Run (cases, load at start) | Claimed by: outcome | What else went red | So |
|---|---|---|---|---|---|
| P11-1 | `src/gov/decisions/checker.py`: the Role trailer read from the whole message, not the final block (DEC-182) | W1-11 and unit/decisions (173, 19.0) | W1-11 `…_owner_named_in_the_message_body_of_an_agent_commit_is_no_approval`: green | nothing | weak (2.2); not ordinary work (2.2's row) |
| P11-2 | the same file: a later owner commit that does not set ACTIVE approves an earlier agent activation (DEC-360) | the same (173, 17.7) | — | 5 W1-11 approval cases | the suite holds the rule |
| P34-1 | `template/…/decision-package.md`: the routing sentence (CAP-34.a) removed | W1-34 (8, 17.7) | `test_the_routing_rule_classes_a_contradiction`: green | nothing | weak |
| P34-2 | the same template: the answer's date rule removed | W1-34 (8, 17.7) | `test_an_answer_cannot_be_recorded_without_a_date`: red | — | valid |
| P08-1 | `governance/project/path-map.yaml`: `tests/**` narrowed to `tests/acceptance/**` (127 tracked paths in no namespace) | W1-08's case, then the product's two checks (1, 17.7 and 17.4) | W1-08 `test_every_tracked_path_matches_exactly_one_namespace`: red | `python3 -m gov.check.pathmap`: exit 0, no finding; `gov doctor`'s `path_map`: pass, `unclassified_count` 0 (P08-1b; the same on the clean tree, P08-1c) | the test is the only working guard (finding 3) |
| P08-3 | `template/…/schemas/close.schema.json`: a state-class enum of its own | W1-08, W2-02, unit/check (418, 17.0) | W1-08 `test_the_state_classes_are_written_in_one_schema_file_only`: green | nothing | weak |
| P08-4 | the same schema: an id pattern of its own | the same (418, 17.2) | W1-08 `test_no_record_schema_writes_an_id_pattern_of_its_own`: green | nothing | weak |
| P02-2 | `src/gov/check/schema.py`: an unknown type reported as SCHEMA_INVALID_TYPE (DEC-746 item 6) | W2-02 and W1-30's record-type file (71, 15.7) | W2-02 `test_a_record_with_an_unknown_type_is_still_refused`: green | W1-30 `test_a_type_nobody_knows_is_still_an_unknown_type` | outdated (2.2); W1-30 holds the rule |
| PR-1 | `src/gov/records/queries.py`: an inner join drops file records (CAP-08) | unit/records and W1-10 (102, 19.7) | — | 20 cases | the suites hold the rule |
| P06-b | the tool registry: ccusage approved by the install rule, not by a decision that names it | W1-06 (96, 19.4) | — | 4 cases | the suite holds the rule |
| P06 (DEC-822) | the register: DEC-822, the gov pin's approval, marked SUPERSEDED | W1-06 (96, 19.4) | `test_every_approving_decision_is_accepted_by_the_owner`: red | — | valid (record-reading) |
| P13-b | `src/gov/readiness/checker.py`: the schema comparison with the Contract's rows skipped (CAP-30.a) | W1-13 and unit/readiness (117, 19.4) | — | 2 builder tests only | the builder tests hold it; no W1-13 case does |
| P44-a | `src/gov/retrieval/retrieve.py`: `--ticket` ignored (CAP-14, DEC-424) | W1-44 (5, 17.2) | `test_retrieve_returns_lessons_for_ticket_in_scope`: green | nothing | weak |
| P41-a | `src/gov/adopt/legacy.py`: a citation behind `./`, `/`, `../` or a folder not counted | W1-41 legacy and unit/adopt (84, 8.3) | — | 9 cases | the suites hold the rule |
| P41-c | `legacy.py:207`: A8's `guard(run)` removed (CAP-06.c) | W1-41 unknown and legacy, unit/adopt (93, 14.5) | W1-41 `test_an_unknown_artefact_blocks_retirement_too`: green | nothing | weak; no test holds A8's guard (finding 4) |
| PU-c | `src/gov/adopt/stages.py`: one ground enough for a move out of a native layout (CAP-44.j) | W1-41 path map and unit/adopt (63, 16.9) | unit `test_a_move_out_of_a_native_layout_needs_both_grounds`: green | W1-41 `test_a_justification_that_states_only_one_of_the_two_grounds_is_refused` (2) | weak; W1-41 holds the rule |
| P38-1 | `src/gov/adapters/portability.py`: a rulesync timeout no longer caught | W1-38's hanging-tool class and unit/adapters (96, 15.9) | W1-38 `test_timeout_handling`: green | unit `test_rulesync_without_answer_is_a_finding` | weak; the builder test holds the rule |
| P06-c | the tool registry: the ccusage install command loses DEC-202's PATH prefix | W1-06 (96, 19.8) | `test_the_ccusage_install_command_is_the_approved_one`: green | only `test_the_registry_is_committed` (the working file differs from the commit) | weak |
| PL202-1 | `src/gov/check/schema.py`: the unmeasured finding no longer names the type | W2-02 unmeasured file (4, 3.1) | `test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green`: green | nothing | weak |
| PL202-2 (control) | the same: the finding no longer says unmeasured | the same (4, 3.1) | the same case: red | 2 more | the control is caught |
| P27-0 (control) | no edit | W1-27, unit/doctor, W1-39 (249, 15.8) | — | nothing | the baseline is green |
| P27-1 | `src/gov/doctor/command.py`: a moved-path reference never reported (CAP-06.d) | the same three (249, 18.3) | five moved-path cases: all green | nothing | weak; no test holds it (finding 1) |
| P27-2 | doctor: the held-out file reported missing when present, and the reverse (DEC-223) | the same (249, 19.8) | W1-27's two held-out cases: green | 2 doctor builder tests | weak; the builder tests hold it |
| P27-3 | doctor: ADOPTED_HEALTHY for every project (CAP-54.a) | the same (249, 11.9) | W1-27's three adoption-level cases: green | W1-27 `test_unmeasured_absence_prevents_adopted_healthy`; W1-39 `test_a_freshly_created_project_is_at_the_minimal_adoption_level` | weak; two other cases hold it |
| P27-4 | doctor: never an unclassified path (CAP-06.d) | the same (249, 8.0) | W1-27's two unclassified-path cases: green | nothing | weak; no test holds it |
| P27-5 | doctor: the historical count dropped from the stale-path section (DEC-448) | the same (249, 12.9) | `test_stale_path_section_counts_excluded_historical`: red | — | valid, overturning the first verdict (its limit in 2.2) |
| P27-6 | doctor: no drift for a CLI newer than the registry (DEC-210) | the same (249, 9.0) | `test_cli_newer_than_registry_is_drift`: green | the below-minimum, extension-below-minimum and sha256 cases | weak; the three red cases pass today only on that drift (2.2) |
| P27-7 | `src/gov/rebuild/command.py`: a reversed digest (CAP-20.a) | the same (249, 8.5) | `test_rebuild_digest_matches_store_loader`: green | nothing | weak; no test holds it |
| P27-8 | doctor's path matcher matches every pattern (CAP-06.a) | the same (249, 8.4) | unit `test_match_pattern`: green | nothing | weak; no test holds it |
| P27-9 | doctor: isolation reported whatever the runtime folder's parent (DEC-425) | the same (249, 9.2) | `test_doctor_isolation_is_measured_not_constant` and unit `test_check_isolation`: green | nothing | weak; no test holds it |
| P27-10 (control) | doctor: a tool at the wrong version counts as ok (CAP-25.a) | the same (249, 0.9; a first run at 19:03, load 9.2, could not write its result file: the shared disk had no free inode, ENOSPC) | `test_tool_at_registered_location_wrong_version_fails`: red | 3 more wrong-version cases | the control is caught; that case is valid, overturning the first verdict |
| P27-11 | doctor: a tool it cannot find reported with nothing that says why | W1-27's doctor file and unit/doctor (46, 3.1) | `test_doctor_real_registry_every_entry_reported`: green | nothing | weak |
| PG-1 | `src/gov/guard/decide.py:154`: a ticket of another role gives its paths (DEC-112) | W1-33's guard file (16, 16.9) | `test_the_auditor_writes_only_the_report_path_of_its_own_ticket`: green | — | weak |
| PG-1b | the same fault | the guard's own suites: W1-01, W1-02, W1-45, W2-58, unit/guard (5,699, 16.4) | — | 30 cases (W1-02 25, W1-45 3, unit 2) | the rule is held |
| PG-2 | `decide.py`: the acceptance-tests rule removed (DEC-113) | W1-33's guard file (16, 3.3) | `test_only_the_test_designer_may_write_the_acceptance_tests`: [orchestrator] red; [engineer], [product-spec] green | — | the function is valid; two cases weak |
| PG-2b | the same fault | the guard's own suites (5,699, 3.5) | — | 26 cases (W1-02 9, W1-45 12, unit 5) | the rule is held |
| PS-1 | `skills/test-design/SKILL.md`: the designer told to read the implementation | W1-35 (166, 19.8) | two read-restriction cases: green; `test_test_design_declares_read_restriction`: red | — | the three are outdated anyway (DEC-820 (c)) |
| PS-2 | `skills/change/SKILL.md`: the version step first, the evidence step gone (CAP-24.c) | W1-35's main file (112, 18.4) | the two lifecycle cases: green | nothing | weak |
| PS-3 | `skills/audit/SKILL.md`: an owner-level finding straight to a ticket | W1-36 (84, 18.1) | `test_owner_finding_requires_decision_package_before_ticket`: green | nothing | weak |
| PS-4, PS-4b | `src/gov/check/skill_validator.py`: the body bound raised to 25,000 (DEC-539) | PS-4: W1-35 with W1-36, stopped at collection (W1-36's conftest shadowed W1-35's), so no measure; PS-4b: W1-35 alone (166, 17.6) | `test_red_when_body_exceeds_2500_tokens`: red | W1-35's orchestration bound case | valid |
| PS-5 | `skills/discovery/SKILL.md`: the work order starts with scenarios, discovery last (DEC-103) | the work-order cases (4, 18.0) | two work-order cases: green | nothing | weak |
| PS-6 | `skills/planning/SKILL.md`: the scenario step gone | the same (4, 18.0) | `test_planning_states_work_order`: green | nothing | weak |
| PS-7 | `skills/change/SKILL.md`: the CIT evidence step gone (CAP-33.a) | the CIT cases (4, 18.0) | `test_change_skill_cit_steps_present`: green | nothing | weak |
| PS-11 | `skills/retrieval/SKILL.md`: both statements of disposable subagents and the returned bundle gone | the retrieval-subagent cases (7, 18.0) | `test_the_skill_says_subagents_are_disposable`: red; `test_the_skill_mentions_facets`, `test_the_skill_addresses_the_main_context_boundary`: green | 2 more | one valid, two weak |
| PS-13 | `skills/change/SKILL.md`: the impact method's OpenSpec step gone (DEC-167) | the impact cases (5, 19.0) | `test_change_mentions_openspec`: green | nothing | weak |
| P07-1 | `src/gov/cli/main.py`: `pause` left out of `gov --help` | W1-07's help-names case (1, 15.1) | `test_help_names_every_reserved_command`: green ("pause" occurs elsewhere in the help) | — | weak |
| P07-2 (control) | the same: `doctor` left out | the same (1, 15.1) | the same case: red | — | the control is caught |
| P32-1 | `src/gov/status/command.py`: the tickets part dropped | W1-32's status-parts file (23, 15.1) | `test_the_plain_form_shows_the_same_parts`: green | 17 JSON cases | weak; the JSON cases hold it |
| P09-1 | `src/gov/tasks/claims.py`: a check-then-create claim lock (DEC-292) | the race case alone ×5 (17.6 to 19.7); W1-09 and unit/tasks in parallel ×3 (18.9 to 19.9) | the claims race: red 4 of 5 alone, 3 of 3 in parallel | — | valid; it can run in parallel (4.2) |
| P09-2 | `claims.py`: a release without the folder lock (DEC-292) | the review race alone ×5 (18.6 to 19.9); in parallel ×3 (18.5 to 19.0) | the review race: red 5 of 5 alone, 3 of 3 in parallel | — | valid; it can run in parallel (4.2) |
| P09-3 | `claims.py`: no wait for the winner's line | the claims race with unit/tasks ×3 (13.8 to 17.7) | the claims race: green 3 of 3 | unit `test_a_holder_still_being_written_is_waited_for` 3 of 3 | the builder test holds it |
| RS-gen | a stand-in rulesync whose `generate` in the check's temporary folder answers after 11 s | W1-38 in parallel (201, 14.1) | the three `load_sensitive` cases: red | 28 cases in 17 functions in all, each RULESYNC_FAILED "no answer within 10 seconds" | the cause of the three entries, shown (finding 2) |
| RS-ver | a stand-in whose `--version` in the project answers after 11 s | the same (201, 9.2) | the three: red | 30 cases in 19 functions | the same |
| RS-any | a stand-in whose every `--version` answers after 11 s | W1-38 and W1-33's research case in parallel (202, 12.3) | W1-33's research case: skipped | none red; 182 skipped (181 W1-38 cases), 20 passed, exit 0 | a silent pass (finding 2) |

## 3. Counts, and the close time each class costs

**How the time is counted.**
- Case time is summed from the rehearsal's parallel run: the close's form, on `dbd3cc53`
  (`logs/rehearsal-times.json`, from its JUnit file).
- A close's wall time is estimated at 0.142 s per case-second there: 31.8 minutes for 13,417 s of case time on 20
  workers.
- The area's 2,415 parallel cases took 4,421.6 s there. That is 33 % of the parallel run's case time, about 10.5
  minutes of a close. Three serial-only cases run outside it.

**Rows and cases.** A row counts as a function; a single case with its own verdict counts only in the "Cases" column,
under its own verdict. 2 whole functions and 6 single cases are flaky (8 cases), and 1 single case is not
reproducible. The 125 weak cases include 2 single cases of a valid function (W1-33's [engineer] and [product-spec]).

| Verdict | Functions | Cases | Case time (s) | Share of the area | About this much of a close's wall time | What acting on it changes |
|---|---|---|---|---|---|---|
| valid | 1235 | 2140 | 3,743.8 | 84.7 % | 8.9 min | keep |
| weak | 109 | 125 | 384.4 | 8.7 % | 0.9 min | revise (test designers, `Rewrite-Reason:`); about the same time after |
| duplicate | 61 | 121 | 233.0 | 5.3 % | 0.6 min | 93.5 s proposed for retirement (P-I4-1 to P-I4-3); the rest kept |
| outdated | 13 | 23 | 21.7 | 0.5 % | 0.1 min | revise to the decision named; the time stays |
| flaky | 2 | 8 | 25.4 | 0.6 % | 0.1 min | fix the cause (W2-57, W2-67); the time stays, the refused closes go |
| not reproducible | 0 | 1 | 8.6 | 0.2 % | 0.0 min | keep on `load_sensitive` until W2-57; the close keeps failure text |
| all | 1420 | 2418 | 4,416.9 | | 10.5 min | |

**By suite** (functions; a parametrised function whose single cases carry their own verdict is counted under its own
verdict, and those cases are listed in the last column):

| Suite | valid | weak | duplicate | outdated | flaky | not reproducible | Case time (s) | Single cases with their own verdict |
|---|---|---|---|---|---|---|---|---|
| W1-06 | 38 | 2 | 14 |  |  |  | 0.7 | — |
| W1-07 | 39 | 1 | 6 | 1 | 1 |  | 660.5 | 4 flaky, 1 not reproducible |
| W1-08 | 83 | 2 |  |  |  |  | 111.8 | — |
| W1-09 | 66 | 2 | 1 |  |  |  | 40.7 | — |
| W1-11 | 100 | 1 | 2 |  |  |  | 31.5 | — |
| W1-12 | 21 |  |  |  |  |  | 6.3 | — |
| W1-13 | 67 |  |  |  |  |  | 73.3 | — |
| W1-14 | 35 |  |  | 1 |  |  | 26.6 | — |
| W1-27 | 73 | 40 | 9 |  |  |  | 835.1 | — |
| W1-32 | 56 | 2 | 4 |  |  |  | 115.0 | — |
| W1-33 | 30 | 4 | 4 |  |  |  | 6.6 | 2 weak |
| W1-34 | 7 | 1 |  |  |  |  | 0.0 | — |
| W1-35 | 76 | 30 | 4 | 8 |  |  | 139.2 | 2 outdated, 1 valid |
| W1-36 | 52 | 11 | 3 |  |  |  | 1.3 | — |
| W1-37 | 4 |  |  |  |  |  | 0.0 | — |
| W1-38 | 93 | 1 | 4 |  | 1 |  | 323.5 | 2 flaky |
| W1-39 | 59 | 1 | 1 | 1 |  |  | 250.0 | — |
| W1-41 | 127 | 6 | 2 |  |  |  | 1,776.3 | — |
| W1-44 | 4 | 1 |  |  |  |  | 1.1 | — |
| W2-02 | 20 | 1 | 6 | 2 |  |  | 4.6 | 1 duplicate |
| unit/adapters | 60 |  |  |  |  |  | 1.3 | — |
| unit/adopt | 16 | 1 |  |  |  |  | 7.6 | — |
| unit/bridge | 4 |  |  |  |  |  | 0.3 | — |
| unit/cli | 7 |  |  |  |  |  | 0.5 | — |
| unit/decisions | 20 |  |  |  |  |  | 2.2 | — |
| unit/doctor | 35 | 2 | 1 |  |  |  | 0.0 | — |
| unit/lock | 16 |  |  |  |  |  | 0.0 | — |
| unit/readiness | 7 |  |  |  |  |  | 0.2 | — |
| unit/records | 1 |  |  |  |  |  | 0.0 | — |
| unit/status | 13 |  |  |  |  |  | 0.2 | — |
| unit/tasks | 6 |  |  |  |  |  | 0.5 | — |

**What the classes cost beyond their run time.**
- **The flaky and not-reproducible cases cost refused closes, not seconds.** An area-4 case, or its list entry, was
  among the causes of seven refused closes since 2026-10-20 (the queue's close results, `log/close-queue-*/`):
  - W2-53's two;
  - W2-02's two;
  - W2-63's;
  - two on 2026-10-22: W2-50's, refused on its W1-38 entry (finding 14), and W2-58's, on the entries' own commits
    (finding 17).

  How the reds sat in those closes:
  - In W2-02's second (2026-10-21 16:11 to 17:26, 75 minutes) every red was of this kind: W1-07's `[hard-block]`
    (the copy race), `[doctor]` (not reproduced) and area 3's W1-25 case (the same copy race).
  - In W2-02's first, `[doctor]` stood beside W1-08's true catch.
  - In the other four they stood beside other causes.

  A refusal costs its full run, 75 to 85 minutes, and a count towards escalation. On the head the copy race is
  dormant (0 of 3 parallel runs), and the probe's limit was never reached in my runs (the probe took at most 2.81 s);
  both come back with the tree's size and the close's load (findings 2 and 5).
- **The weak class costs its run time, 384.4 s (about 0.9 minutes of a close), and does not protect what it claims.**
  80 % of it is W1-27's (306.7 s): doctor runs on whole-tree copies whose assertions read a key name.
  - Revising the class costs test-design time, not close time: a structural doctor case can read one doctor run's
    sections, as the word checks read one run each now.
  - The planted faults show what the class leaves uncaught: five doctor and rebuild behaviours, and A8's guard, that
    no case of the suites I ran catches (2.4; findings 1 and 4).
- **The duplicate class:** 233.0 s of case time, of which 93.5 s (about 13 s of a close) is proposed for retirement
  (P-I4-1 to P-I4-3). The rest costs under a second per function and stays.
- **The outdated class:** 21.7 s. Its cost is the replaced rule it enforces, not the time; and for W1-35's
  command-list case, a false red in W2-11's own close (finding 7).
- **The serial-only cases of the area cost little:** W1-07's help case (about 2 s) and W1-09's two races (about 7 s
  each). W2-62's close ran its 263 serial cases in 1,799 s, so the area's three are under 1 % of that run.

## 4. What this changes for W2-66's map, W2-57's serial list and the two owner lists

### 4.1 W2-66's path-to-suite map

W2-66 runs, at a close, the ticket's own suite, the unit tests, and the suites of every ticket whose allowed paths
overlap the change; a change under the shared core runs everything (DEC-880 item 2 (a); DEC-892 c adds
`src/gov/config/loader.py`, `src/gov/tasks/tickets.py` and `src/gov/store/loader.py`). Since DEC-896 item 2 the
test-selection lists (the shared core, the record-only paths) go into their own file, for example
`governance/project/test-map.yaml`, owned by W2-66 and W2-68; the proposals below are lines for that file. I compared the tickets'
declared paths with who executes what, from lens H's measured coverage (`/tmp/gov-os-assessment-H/logs/cov_map.json`,
lens H's child-process shim; read by me, not re-measured). Execution counts include module imports, so they show
reach, not dependence; the items below are the ones where I also found the dependence in the test code.

1. **W1-07's suite is a contract suite over every command.** Its envelope, read-act and registry files run all
   twelve reserved commands (`EVERY_INVOCATION`, `READ_COMMANDS`). It executes 94 product modules; 86 are outside
   its declared paths, and 45 of those outside the shared core as DEC-880 and DEC-892 c word it, in 20 packages:
   adapters, adopt, checkpoint, ci, closure, codeintel, context, decisions, doctor, launch, lock, pause, readiness,
   rebuild, retrieve, secrets, status, store, tasks and telemetry (`scripts/reach.py`). A ticket that changes `src/gov/status/` selects
   W1-32's suite, not W1-07's, though W1-07's envelope case runs `gov status`. **Proposal:** map W1-07's three
   contract files to every command module (`src/gov/*/command.py`), or put them in the always-run set: 138 s + 250 s
   + 40 s of case time in the rehearsal, about 335 s once P-I4-1 to P-I4-3 are applied, under a minute of a close's
   wall time.
2. **`src/gov/cli/` is executed by most suites but is not in the shared core.** Counting suite folders (acceptance
   and builder tests together), `src/gov/cli/main.py` runs under 30, `errors.py` under 59, `cli/__init__.py` under 42
   and `src/gov/__init__.py` under 53: every suite that runs `gov` as a child. A change to the envelope, the exit
   codes or the module loader selects only W1-07 and W1-46, the tickets that declare them. **Proposal:** measure these modules as lens H measured DEC-892 c's three (planted faults, then the share of
   catching tests the declared map selects); until then treat `main.py` and `errors.py` as shared core.
3. **W1-38 reads kernel files outside its declared paths.** Its fixture copies the kernel's roles and skills into
   every generated project and compares the generated subagents and skills with them
   (`tests/acceptance/W1-38/w1_38_support.py:39-41, 342-343, 740-747`); its ticket declares only `template/.rulesync/**`,
   `.rulesync/**`, `src/gov/adapters/**`, its unit tests and the portability check (`.tickets/DAEO-3ef2.md:24-29`).
   W2-11, which edits the orchestrator role file and the orchestration skill, would select W1-33 and W1-35 but not
   W1-38. The kernel hooks are in the shared core already. **Proposal:** add
   `template/governance/kernel/roles/**` and `template/governance/kernel/skills/**` to W1-38's map entry.
4. **The record-reading set** (finding 6): start it with the area's files listed there, so a record-only commit runs
   them on every head.
5. **Two dead modules.** `src/gov/cli/commands/status.py` and `check.py` are never loaded: the loader takes
   `src/gov/<name>/command.py` first (`src/gov/cli/main.py:117-122`), and both commands have one now.
   `check.py` still says that running checks is not built (W1-26, DEC-186); `main.py:16` still says those two live
   there; and `gov --help` itself still says of `check` "running them is not built yet" (`main.py:95`), though
   W1-26 built it. Only `tests/unit/launch/test_command_modules.py` copies the two files as fixtures. They need no
   suite in the map; their removal and the help line are a cleanup (W2-67, or the next ticket in `src/gov/cli/`).
6. **The suites that select themselves well.** W1-06, W1-12, W1-34, W1-37 execute no product module (they read
   records and templates only); W1-09, W1-11 and W1-13 reach outside their paths only through the command line's
   own modules (item 2) and `src/gov/tasks/` (imports).

### 4.2 W2-57's serial list

- **W1-07's help case stays serial** (`test_help_answers_in_under_300_ms`). It measures the median of nine
  `gov --help` runs against 300 ms.
  - It passed 3 of 3 alone (2.0 to 2.2 s for the case), 6 of 6 inside the suite's parallel run (two trees, loads up
    to 37.9) and in W2-62's close (serial).
  - So on this machine it survived the suite's parallel load. But its budget is the help's own time, which the full
    regression's heavier load can push over, and DEC-889 item 5 keeps a latency case alone.
  - No change.
- **W1-09's two race cases can leave the serial list.** DEC-889 item 5 asks W2-57 to try them in parallel; I did.
  - Unplanted, both passed 3 of 3 inside the suite's parallel run (6.5 to 7.0 s each), as well as 3 of 3 alone.
  - They keep their power in parallel. With a check-then-create claim lock (P09-1), the claims race went red in 3 of
    3 parallel runs (4 of 5 alone). With a release that skips the folder lock (P09-2), the review race went red in 3
    of 3 parallel runs (5 of 5 alone).
  - My parallel runs were W1-09's own suite with unit/tasks (87 to 93 cases), not the full regression at a close's
    load. So: W2-57 moves both into the parallel run after one nightly in which they run there green. That saves
    about 14 s of the serial run per close.
- **No entry is missing.** No area case needs to run alone:
  - W1-38's probe cases fail on the probe's limit, not on running beside others (finding 2), and W2-57's first item
    fixes that limit;
  - W1-07's copy race happens inside the suite's own parallel run and alone alike (finding 5).

### 4.3 `load_sensitive`

| Entry | Verdict here | Cause found | What changes |
|---|---|---|---|
| W1-07 `test_every_command_returns_the_envelope[doctor]` (DEC-886) | not reproducible | not found: green in all 12 runs here (alone and in the suite's parallel run, on the head and on the fat tree), and the close keeps no failure text; the code points to an exception `gov doctor` does not catch (finding 5) | keep until W2-57; the close's JUnit XML with failure text (DEC-889 item 12) would name the cause next time |
| W1-38 `TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` (DEC-871) | flaky | the probe's 10-second limit: named in the close's own output, and shown by running a stand-in rulesync slowed past it (red under RS-ver and RS-gen); green here 3 of 3 alone and 3 of 3 in the suite's parallel run, the probe at most 2.81 s | keep until W2-57's probe fix (P-I4-5) |
| W1-38 `TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` (DEC-871) | flaky | the same; the function's four other cases went red with it under the stand-in | keep |
| W1-38 `TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[...by-hand.md]` (DEC-892) | flaky | the same; the entry covered nothing until 11:52 (DEC-892's text lacked the test's file; it refused W2-50's close, finding 14); DEC-894 fixed the text, DEC-893 the placeholder's handling | keep |

**No addition is proposed.** The same cause reaches more W1-38 cases than the three listed. The stand-in runs turned
30 cases red (19 functions) with the check's `--version` slow, and 28 (17 functions) with its `generate` slow; the
three listed cases were red in both. P-I4-5 recommends fixing the probe rather than listing those cases one by one.

**Two costs of changing the lists, both now decided in part:**
- **Their entry text.** DEC-895 has every entry validated with the pinned judge's readers before it is sent. What
  remains is an entry that stops counting later because its decision's status or text changes; finding 14 proposes
  the ratchet's reading as a pre-close gate.
- **Their commits.** DEC-896 counts a decision-record commit under an ACCEPTED decision as measured (a W2-07 KPI).
  Until the re-pin, gate (h) predicts a work-without-a-task refusal before a close is spent (finding 17). W2-57's
  removal of the four entries is the next such commit.

### 4.4 `accepted_reds`

None of area 4's tests is on the list, and none should be: W1-42's two entries are area 2's.
- No area-4 case was red at the head in my runs: the suites' parallel runs, the alone runs, the controls P27-0 and
  P08-1c, and every case that stayed green beside a planted fault.
- None was red in W2-62's close of 16:44 (2 failed: the accepted reds' count).
- The red cases on the fat tree are the copy race (finding 5), not a known red.

## 5. Findings

Each finding is judged against ADR-0001's threat model (DEC-801; `governance/project/briefs/JUDGEMENT.md`): the Gov
OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate
adversary with the owner's privileges. Its two questions, word for word: "Can an honest agent hit this in ordinary
work?" and "Does it fail open or lose work?" (DEC-808). Each finding carries the two lines that answer them; only
"yes" with "fails open" or "loses work" fails the item.

Severity scale used here. **High:** an honest agent can hit it in ordinary work, and it fails open or loses work, so
DEC-801 counts it. **Medium:** ordinary work, with a measured cost of another kind (a refused close, a replaced rule
served as in force, a check that blocks the wrong thing). **Low:** cost in close time or upkeep only, or not reachable
in ordinary work.

### Finding 1. W1-27's doctor suite cannot fail for most of the faults it names (high)

- **What.** 40 of W1-27's 122 functions are weak (2.2), and 2 doctor builder tests. Most pass on words that
  `gov doctor` always prints; the others read less than they claim (the real-registry case's "not ok with a reason"
  is met by the pinned version every entry carries). Two that the first pass marked weak went red under their planted
  faults and are valid now, with their limits stated: the historical count (P27-5) and the wrong version at its
  registered location (P27-10).
- **Why they cannot fail.**
  - Doctor emits every section key on every run (`src/gov/doctor/command.py:824-848`). So a test that searches the
    JSON text for "held", "path", "moved", "drift", "adopt" or "isolat" finds the key name, whatever the section says.
  - In every project these cases copy from the working tree, which carries the real registry, doctor is unhealthy:
    the registry's `pytest-xdist` and `pytest-testmon` are looked for as binaries (`command.py:24-35, 446-449`; known
    for pytest-xdist as row W2-M287). An unhealthy
    doctor raises `DOCTOR_UNHEALTHY` and the envelope's `result` is `{}` (`src/gov/cli/main.py:224-225`), with every
    section in `error.details`. A case that reads only `result`, such as
    `test_present_held_out_yaml_is_not_reported` and `test_full_coverage_is_healthy`, therefore checks nothing.
  - Three more causes: the drift cases' fake CLI sits on a PATH doctor never sees (`test_w1_27_drift.py:28`,
    `w1_27_support.py:80`); `test_rebuild_digest_matches_store_loader` compares only if the envelope's `session` is a
    dict, and it is a string; and `test_home_tool_wrong_sha256_not_ok` places none of the files whose hash it claims
    to compare.
- **Planted faults** (2.4; each run took W1-27, W1-39 and the doctor builder tests together, 249 cases, against a
  green control run, P27-0).
  - Five of the eleven doctor and rebuild faults left all 249 cases green, so no test of the three suites holds
    these behaviours:
    - a moved-path reference never reported (P27-1);
    - an unclassified path never reported (P27-4);
    - rebuild's digest reversed (P27-7);
    - doctor's path matcher matching every pattern (P27-8);
    - isolation reported whatever the runtime folder (P27-9).
  - A sixth, a tool doctor cannot find reported with nothing that says why (P27-11), left the 46 cases it was run
    with green.
  - Three were caught only off their own cases:
    - the held-out file reported the wrong way round (P27-2), by two builder tests only;
    - every project reported ADOPTED_HEALTHY (P27-3), by one W1-27 case and one W1-39 case, while W1-27's three
      adoption-level cases stayed green;
    - the newer-CLI drift (P27-6), whose own case stayed green, by three drift cases that went red only because they
      pass today on the real CLI's drift (2.2).
  - Two were caught by their own cases: P27-5 and P27-10.
- **Why it matters now.** Contract v4.2's lite adoption verdict lists "gov doctor green (exit 0)" among its conditions
  (CAP-44.h; DEC-741 G). A doctor that stops reporting a missing held-out file or a moved-path reference would pass
  every close and count towards an adoption's health.
- **Proposed change.** One structural case per doctor section that reads the section's typed fields wherever they
  are (in `result` or in `error.details`), with a planted input for each outcome, in place of the word checks.
  Carrier: W2-67 (test hygiene) or a small test-revision ticket for W1-27. `Rewrite-Reason:` the assertion matches a
  key name doctor always emits.
- Ordinary work: yes, because three open tickets change doctor's code in Wave 2 (W2-22 "gov doctor green",
  `src/gov/doctor/**`; W2-18, `doctor/install*`; W2-09, `doctor/tools_list*`), and these cases are what their closes
  run against it.
- Consequence: fails open (a broken doctor check passes the suite and the close).

### Finding 2. The rulesync probe's 10-second limit reaches 40 cases, not three, and one fixture turns it into a silent skip (high)

- **What.** Lens H found load the commonest cause of test refusals (its finding 9); here is one mechanism, in full.
  The adapter-portability check runs a real `rulesync --version` and then a real `rulesync generate`, each with a
  10-second limit (`src/gov/adapters/portability.py:38, 63-72, 84, 173`). DEC-871 and DEC-892 put three
  W1-38 cases on `load_sensitive` for this cause. The same probe reaches:
  - **30 W1-38 cases (19 functions) that turn red** when the `--version` limit is passed, 28 of them (17 functions)
    also when the `generate` limit is (measured, below). Three are on the list; 27 are not, and each of those, red in
    a close, refuses it. The list names single parameters of functions whose every
    parameter runs the probe: four more of `TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named` (one
    of which was red under load in Wave 1, DEC-646, judged load by DEC-647) and the `settings.local.json` case of
    `TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding`.
  - **9 W1-38 cases (3 functions) that turn green** when the limit is passed, because `RULESYNC_FAILED` also satisfies
    their red assertion. Under load they pass without comparing anything. Example:
    `TestBrokenHeldOutFile::test_broken_file_is_not_green_and_no_path_is_printed` (7 cases).
  - **W1-38's session fixture** `rulesync_bin` runs `rulesync --version` once per worker with the same 10-second
    limit and, on a timeout, skips every rulesync case of that worker as "rulesync is not installed"
    (`tests/acceptance/W1-38/conftest.py:21-27`, `w1_38_support.py:215-227`). 181 of the suite's 201 cases depend on
    it, spread over the close's 20 workers. `gov close` counts a skip and does not refuse it
    (`src/gov/close/command.py:792`, DEC-500).
  - **W1-33's** `test_the_research_definition_is_the_generated_one` does the same: a 10-second timeout returns None and
    the case skips as "not installed" (`w1_33_support.py:171-174`).
- **Measured, under load.** In my runs the probe never came near its limit:
  - `rulesync --version` took 0.33 to 2.81 s in 42 samples, at loads of 6.6 to 47.1;
  - the three listed cases passed 3 of 3 alone and 3 of 3 inside the suite's parallel run;
  - the whole suite passed 3 of 3 (201 cases each).
- **Measured, by running the cause** (2.4). A stand-in `rulesync`, put first on the PATH, answered after 11 seconds:
  - **RS-ver**, the check's `--version` slow: 30 W1-38 cases in 19 functions went red, each with RULESYNC_FAILED "no
    answer within 10 seconds", the three listed cases among them.
  - **RS-gen**, the check's `generate` slow: 28 cases in 17 functions went red.
  - In both, the 9 masked cases stayed green.
  - **RS-any**, every `--version` slow: 181 W1-38 cases and W1-33's research case were skipped as "rulesync is not
    installed", none failed, and pytest exited 0, a silent pass.
- **The rehearsal and the closes.**
  - In the rehearsal the 30 red-on-timeout cases took a median 2.4 s and at most 8.3 s each, the probe's two calls
    included, and the 9 masked cases at most 5.5 s. So the closes' timeouts are spikes of load, not the usual case.
  - The skip has not fired in any recorded run: every close's regression since 2026-10-20 skipped exactly 31 cases (9
    closes, W2-62's of 16:44 the last), and the rehearsal 30. None of the 201 W1-38 cases was skipped or red in the
    rehearsal or the five tool trials.
- **Proposed change.** W2-57's first item (DEC-892 item 2) should name all four parts, not only the probe:
  (a) the probe's two calls; (b) the session fixture's skip, which should fail instead (a timeout is not an absent
  tool); (c) the 9 masked cases, which should assert the finding code they expect, not just "not green"; (d) W1-33's
  skip. `Rewrite-Reason:` a probe timeout is not an absent tool and not the fault under test.
- Ordinary work: yes, because every close runs W1-38 under the regression's parallel load, where three cases have
  already timed out (W2-53's close, 2026-10-20; W2-63's close, 2026-10-22).
- Consequence: fails open (a fixture timeout skips that worker's rulesync cases, up to all 181, and the close passes;
  9 cases pass without comparing).

### Finding 3. W1-08's case is the only working path-map guard, and a W2-M214 fix done as its row reads would turn a hard-block check red on every close (high)

- **What.** DEC-225's rule, every tracked path in exactly one namespace, has three checks. Two of them can never fail
  on this repository:
  - **core-pathmap** (a hard-block check) reads `namespaces` as a list and returns no finding for the map form this
    path map uses (`src/gov/check/pathmap.py:47-49`). This is known: row W2-M214, triaged to W2-23, and lens H's
    finding 1 named it.
  - **gov doctor's path-map section** matches with `fnmatch` (`command.py:518-529`), whose `*` crosses `/`. The map's
    own header says "`*` stays inside one folder", and its first namespace is `root-files: ["*"]`. Measured on the
    clone's 2,071 tracked paths: `fnmatch`'s `*` holds all 2,071, so doctor can never report an unclassified path
    here. It never checks "more than one namespace" either. Its builder test `test_match_pattern` holds only positive
    `*` cases.
  - W1-08's `test_every_tracked_path_matches_exactly_one_namespace` is the only check that works. It caught the real
    fault of 2026-10-21 (two record copies in no namespace, DEC-885).
- **Measured by planting it** (P08-1, P08-1b; 2.4). With `tests/**` narrowed to `tests/acceptance/**`, 127 tracked
  paths fell in no namespace.
  - W1-08's case went red, naming them.
  - `python3 -m gov.check.pathmap` exited 0 with no finding.
  - `gov doctor`'s `path_map` section said `pass`, `unclassified_count` 0, as it does on the clean tree (P08-1c).

  And with doctor's matcher planted to match every pattern (P27-8), all 249 cases of W1-27, W1-39 and the doctor
  builder tests stayed green, `test_match_pattern` among them.
- **The forward risk, measured.** core-pathmap's own matcher is `fnmatch` too (`pathmap.py:27-31`). Fed the map form,
  as row W2-M214's fix reads ("core-pathmap reads the map form"), it puts **2,063 of the 2,071 tracked paths in two
  namespaces**: `root-files` and their own (`scripts/pathmap_matchers.py`). That is a hard-block check red on every
  close. With DEC-225's matcher, the same tree gives 0 and 0.
- **Proposed change.** One matcher in DEC-225's language for both checks, with a planted unclassified path and a
  planted double match as cases. Carriers: W2-23 for core-pathmap (W2-M214's triage; its allowed paths do not yet hold
  `src/gov/check/pathmap.py`, so the card needs that line) and W2-22, "gov doctor green" (`src/gov/doctor/**`), for
  doctor's matcher and its builder test. `Rewrite-Reason:` the matcher is not DEC-225's language.
- Ordinary work: yes, because a new top-level folder before its namespace (DEC-845's `experiments/`, for one) is
  ordinary work, and W2-23 will take W2-M214 as written.
- Consequence: fails open for core-pathmap and doctor today (W1-08 holds the gate at close); other (a red on every
  close) if W2-M214 lands with `fnmatch`.

### Finding 4. A8's retirement guard is held by no test; four other weak cases guard rules that other suites hold (high for A8, low for the four)

The first pass named five weak cases in the guard, adoption and race rules. The planted faults (2.4) sorted them.

**A8's guard is held nowhere.**
- W1-41's `test_an_unknown_artefact_blocks_retirement_too` claims that A8, the retirement stage, refuses while an
  artefact is unknown. But A8 refuses first for the missing A6 record (`src/gov/adopt/project.py:150-158`). So A8's
  own guard is reached by no case: the call `guard(run)` in `retire()` (`legacy.py:207`), which checks three things
  (`stages.py:347-361`):
  - the accepted A5 verdict still holds;
  - the plan is the audited path map's;
  - no artefact is unknown.
- With that call removed (P41-c), all 93 cases of W1-41's unknown and legacy files and the adoption builder tests
  stayed green.
- The builder tests check the guard's VERDICT_CHANGED and PLAN_NOT_THE_PATH_MAPS refusals at A6 only
  (`tests/unit/adopt/test_adopt.py:226, 258`).
- So A8 could retire legacy files after the reviewed verdict or plan changed, or with an unknown artefact in the
  tree, and no test would see it.

**Four weak cases whose rule is held elsewhere.** Each adds no protection of its own; whether to revise or retire it
is a test designer's call.
- **W1-33's `test_the_auditor_writes_only_the_report_path_of_its_own_ticket`.** The other ticket in the fixture
  (DAEO-zz90) does not cover `docs/audit/**` (`test_w1_33_guard_and_launcher.py:60-62`). So the case stayed green with
  the guard's role test removed (PG-1, `src/gov/guard/decide.py:154`). The same fault run against the guard's own
  suites (PG-1b) turned 30 cases red: W1-02 25, W1-45 3, the guard's unit tests 2.
- **W1-33's `test_only_the_test_designer_may_write_the_acceptance_tests`.** With the acceptance-tests rule removed
  from the guard (PG-2), its [orchestrator] case went red, so the function holds the rule.
  - Its [engineer] and [product-spec] cases stayed green, though its README names them as the guard half of failure
    line 2 (README:36).
  - Their tickets name no acceptance path (`tests/acceptance/W1-03/w1_03_support.py:109-114, 244-249`), so the write
    is stopped as outside the ticket whatever the rule says.
  - Against the guard's own suites (PG-2b), 26 cases went red: W1-02 9, W1-45 12, unit 5.
- **The adoption builder test `test_a_move_out_of_a_native_layout_needs_both_grounds`.** It tests `_native` only
  (`test_adopt.py:315-320`). With one ground made enough (PU-c) it stayed green, while W1-41's
  `test_a_justification_that_states_only_one_of_the_two_grounds_is_refused` went red in both its cases.
- **W1-38's `TestToolAbsentOrHanging::test_timeout_handling`.** With the probe's timeout no longer caught (P38-1) it
  stayed green, while the builder test `test_rulesync_without_answer_is_a_finding` went red.

**W1-09's two race cases are valid** (2.1).
- A check-then-create claim lock (P09-1) turned the claims race red in 4 of 5 runs alone and 3 of 3 inside the
  parallel run.
- A release without the folder lock (P09-2) turned the review race red in 5 of 5 and 3 of 3.
- The claims race did not catch a loser that reads the lock before the winner has written it (P09-3, green 3 of 3).
  The builder test `test_a_holder_still_being_written_is_waited_for` did, 3 of 3.

**Not counted here: W1-11's `test_the_owner_named_in_the_message_body_of_an_agent_commit_is_no_approval`.**
- It stayed green with the checker reading the whole message instead of the final block (P11-1), and so did all 173
  cases of W1-11 and the decision builder tests.
- The fail-open path needs both that regression and an agent commit with no Role trailer of its own and `Role: owner`
  at the start of a body line.
- No git hook refuses such a commit here (none is installed). But every brief's commit rule gives an agent commit its
  own trailer, and the close queue checks the trailers again before each close (DEC-896 gate (e)). So I count it as
  not ordinary work: a row for the Wave 3 hardening pass (2.2 carries it).

**Proposed change.**
- For A8: a case whose project passed A6 and then meets an unknown artefact, and one whose A5 verdict changed, before
  A8, so that `retire()`'s guard is reached.
- For the four others: the revisions in 2.2.
- Carriers: a small test-revision ticket for W1-41 (or W2-52, which reuses `w1_41_support`); W2-65 or a small
  test-revision ticket for W1-33. `Rewrite-Reason:` the fixture cannot reach the rule.

**A8's guard:**
- Ordinary work: yes, because W2-52 changes adoption now and EXAMIN's adoption (W2-26 to W2-28) runs A8; a refactor
  that drops or reorders the guard's call is an honest slip, and no test would catch it.
- Consequence: fails open (A8 retires legacy files past a changed verdict or plan, or with an unknown artefact). I
  count no lost work: retired files stay reachable at an archive ref (`legacy.py:3`).

**The four others:**
- Ordinary work: yes, because W2-58, W2-65 and W2-09 change the guard now.
- Consequence: other (no rule goes unguarded: another suite catches each fault; the cases cost run time and their
  READMEs claim more than they hold).

### Finding 5. W1-07's two red cases in three refused closes had two different causes (medium)

- **What.** Two refused closes name the same pair, W1-07's `[hard-block]` and W1-25's
  `test_gov_check_list_names_the_family_check`, as red **(error)**: W2-53's (2026-10-20 08:38, a tree of about 8,300
  files; `log/close-queue-2026-10-20/close-DAEO-7rr2.json`) and W2-02's second (2026-10-21 16:11, 10,286 files;
  `log/close-queue-20261021-1550/close-DAEO-zflj.json`). An error there means the fixture failed before the test ran.
  W2-02's two closes also name `[doctor]` as red **(failed)**: inside the test, a different cause.
- **`[hard-block]` and W1-25's case: git's background gc.** Each W1-07 test copies a session copy of the tree whose
  first commit leaves one loose object per file and folder. `git gc --auto` packs them in the background above 6,700
  loose objects (git-scm.com/docs/git-gc, read 2026-10-22: `gc.auto` default 6700, `gc.autoDetach` default true), and
  the suite's own `git()` sets `HOME` to the project and `GIT_CONFIG_NOSYSTEM=1` (`w1_07_support.py:144-152`), so
  those defaults hold on every machine. On the tree of the refused closes (10,286 files) the next test's
  `shutil.copytree` meets files being packed away. Lens H's third run, on that tree (2026-10-21 12:45, `-n 8`), shows
  it on this very case: `[hard-block]` errored at setup with `shutil.Error: [('…/w1-07-live0/repo/.git/objects/03',
  '…/test_a_declared_check_is_liste0/repo/.git/objects/03', "[Errno 2] No such file or directory …` (its
  `logs/p3.xml`; `H-test-strategy.md:425, 975`, its finding 2); P-W2-02-C3 named the race.
- **Reproduced here.** I made W1-07's own parallel run three times on the fat tree (14:20, 14:40, 14:57).
  - The same error struck six times, on five cases, in two of the three runs:
    - 14:40, four errors at setup and one failure: `[not-yaml]`, the help-usage case, `[a-string-status]`, `[ci]`
      and the envelope duplicate's `[check]`;
    - 14:57, one error: `[ci]` again.
  - Each was `shutil.Error: … .git/objects/NN: No such file or directory` in the session copy.
  - On the head, 0 in three runs.
  - `[hard-block]` itself happened to pass all six parallel runs and six alone runs. The race is the shared
    `project` fixture's, so every W1-07 case that takes the fixture is exposed: the 5 hit here, and `[hard-block]`
    in the closes, are those the race happened to reach.
  - The cause is dormant at 2,071 files (DEC-887); it returns when the tree passes roughly 6,700 objects again.
- **`[doctor]`: not reproduced.** It passed all 12 runs here: alone 3 of 3 on the head and 3 of 3 on the fat tree
  (5.9 to 17.3 s), and inside the suite's parallel run 3 of 3 on each (5.7 to 12.8 s, peak load 37.9), two of those
  while the copy race hit other cases. In six
  recorded parallel runs on the slim tree it took 5.4 to 10.7 s of its 180-second limit and passed, and in lens H's
  two runs on the fat tree under load it passed in 8.5 and 6.3 s (`logs/p1.xml`, `p3.xml`). The close keeps
  no failure text, so its cause stays unmeasured. The code narrows it. `gov status` runs the same doctor `run`
  (`_doctor`, `src/gov/status/command.py:154-166`) behind a catch-all (`_part`, :26-31) that turns any other exception
  into "not read", in about 20 W1-07 cases, and none of them was red in
  either close; `gov doctor` itself catches only `GovError` (`main.py:224`), so an exception doctor raises prints a
  traceback and no envelope. Doctor's slow sections took 4.6 s (the tools' hashes and version probes) and 0.6 s
  (Claude Code) at load 19 here (`scripts/doctor_timing.py`), far from the 180-second limit. So the evidence points to
  an exception that `gov doctor` does not catch on that tree under load (the routes: a decode error from `_git`'s
  `text=True`, an error from an unguarded read, the lock comparison), not to the time limit.
- **Proposed change.** (a) Keep the `[doctor]` entry on `load_sensitive` until W2-57, as DEC-886 says, and have the
  close keep JUnit XML with failure text (DEC-889 item 12 already orders it for the close). (b) W2-67's per-test copies
  task names the gc race as a case: a copy from a committed tree must not depend on git's background gc (for example
  `gc.auto=0` in the copy, or a copy of the working files instead of `.git`). (c) W1-38's third `load_sensitive`
  entry gives the time of its alone run with the minute's last digit left open
  (`governance/project/path-map.yaml:397`), a placeholder; DEC-893 (owner, standing, `da3d77e1`) has since decided
  it: the real time goes into the owner's next ratchet commit or W2-57's removal, and a placeholder scan now runs in
  the record checks.
- Ordinary work: yes, because every close runs these suites, and the tree grows in ordinary work.
- Consequence: other (a false red refuses a close: about 75 to 85 minutes and a count towards escalation).

### Finding 6. The declared record-reading set misses most of the area's record readers (medium)

- **What.** DEC-889 item 2 declares a set of record-reading tests that runs on every head: gate (f)'s four files
  (W1-06's approvals, W1-08's path map, W1-27's path compliance, W1-07's envelope), with W2-54's green-here cases,
  W1-33's definitions and W1-49's window (`tools/close_queue.sh:41-48`, `tools/record_checks.sh:18-28`). In area 4,
  these test files also turn red on a record commit, and are outside it:

  | Suite and file | Record read | Functions |
  |---|---|---|
  | W2-02 `test_w2_02_green_here.py` | every `*.md` with frontmatter under `.tickets/` and `docs/`, untracked included (625 files) | 5 |
  | W1-08 `test_w1_08_ticket.py`, `test_w1_08_probe.py` | the 112 ticket files; the 29 probe records | 2 |
  | W1-08 `test_w1_08_floor.py` | the path map's floor and strengths | 17 |
  | W1-06 the other six files (registry, pins, digests, ccusage, install approvals, vendor digest) | the tool registry, and the register for the approvals | 37 |
  | W1-07 `test_w1_07_config.py`, `test_w1_07_config_details.py` | the tool registry, the tickets | 6 |
  | W1-09 `test_w1_09_vendoring.py` | the registry's `tk` entry | 2 |
  | W1-27 the doctor files on whole-tree copies, other than `path_compliance_r2` | the whole tree's text (moved-path greps) and the registry | 25 |
  | W1-33 `test_w1_33_roster.py` | `governance/project/roster.yaml` | 6 |
  | W1-44 `test_w1_44_lessons.py` | `docs/lessons/` | 5 |
  | W1-38 and W1-39 | the registry's rulesync and copier entries | 89 and 57 |

- **Why it matters.** Under W2-66, a record-only commit selects no suite but the set. A red in these files would
  first show in the nightly, as a P1 package (DEC-880 (c)), or in the next full close. The three record reds of
  2026-10-21 all came from inside today's set (W1-06, W1-08, W1-27).
- **Proposed change.** W2-66's draft starts the set with these files, or marks them with the `repository_state` marker
  lens H proposed, so the set is declared up front, not grown from the nightly's misses.
- Ordinary work: yes, because record commits land every day.
- Consequence: other (a red found late: a P1 package or a refused close, not a silent pass, because the nightly stays).

### Finding 7. Thirteen outdated tests, and three groups of them have no carrier (medium)

- **What.** 13 functions, and 2 cases of a fourteenth (23 cases in all), assert a behaviour a later decision changed.
  Each has a named carrier except:
  - **W1-35's four test-design read cases** hold the skill to "reads only the ticket's specification and its KPIs".
    DEC-820 (c) lets the designer read the existing code and refuses only that ticket's implementation. W2-11's
    supersession KPI (`.tickets/DAEO-k7hz.md`) names DEC-838, DEC-820's listing rule, DEC-847 and DEC-861, not
    DEC-820 (c).
  - **W1-35's two command-list cases** accept only the twelve reserved commands (`test_w1_35.py:656`,
    `test_w1_35_orchestration.py:100`, through W1-07's copy). The product's validator accepts the fifteen of DEC-542
    (`src/gov/check/skill_validator.py:25, 142`). W2-11's own KPI W2-L257, the launcher stated as a command, will
    turn the orchestration case red.
  - **W2-02's decision-entry case** requires a kernel schema with owner and date required. DEC-755 item 5
    (2026-10-17) says owner and date are not required, and orders a product-spec row to align
    `register-entry.schema.json`. No row in `docs/plan` cites DEC-755, and W2-02's card still says "id, status, owner,
    date" (`docs/plan/WAVE_2_WBS.md:227`). No code reads that schema yet (`src/gov/check/schema.py:33`), so the
    conflict waits for W2-03 or W2-64.
- **The others, with carriers:** W1-35's LEAD_CHECKPOINT, temp-hygiene and standing-sentence cases (W2-11, named in
  its KPI; W1-35's ceiling clause, which the sweep also routed to W2-11, asks only for a stated ceiling, which DEC-847
  keeps, and is valid); W2-02's unknown-type case (DEC-746 item 6; W2-64); W1-14's profile-or-class case (DEC-355;
  W2-34); W1-07's error-envelope session case (written when `gov check` was not built; a small revision); W1-39's
  neither-file case (DEC-761 item 1; already rewritten on unmerged `w2/W2-16`, `adbeea77`).
- **Proposed change.** Add DEC-820 (c) and DEC-542's command list to W2-11's supersession KPI; add the DEC-755 item 5
  row to the Wave 2 list, with W2-02's KPI line and case revised in it.
- Ordinary work: yes, because W2-11's own KPI will hit the command-list case, and W2-03 will read register entries
  as records.
- Consequence: other (a replaced rule enforced; a false red in W2-11's close).

### Finding 8. Five entries a later decision changed are not marked, against DEC-866 item 1 (medium)

- **What.** DEC-866 item 1: "The old entry is marked at once". In this area's sources, five entries carry no mark:
  - **DEC-236** defines `LEAD_CHECKPOINT` as a lead's return (register lines 2267, 2276); DEC-838 item 2 removed it.
  - **DEC-508** and **DEC-525**: DEC-820 "Replaces: the listing refusals on `governance/` and `.claude/` (DEC-508),
    and every other read restriction beyond the four" (the settings-file read refusal of DEC-525 among them).
  - **DEC-723**: the same line of DEC-820 names its listing refusal.
  - **DEC-090**: DEC-741 E "amends DEC-090 in part" (A7, A10 and the verdict come into Wave 2, lite).
- DEC-866's sweep (`packages/SWEEP-2026-10-20.md` §2) marked only DEC-838's family. It routed the tests and texts
  citing DEC-508 and DEC-525 to W2-11 and W2-58, but did not mark the entries. The adopt skill still says the verdict
  is Wave 3 (`template/governance/kernel/skills/adopt/SKILL.md:41`, citing DEC-090).
- **Proposed change.** Mark the five status lines ("Changed by DEC-820" and so on) in the orchestrator's next
  decision record, under DEC-866's standing order (no new owner decision is needed), and add them to the sweep's list;
  add the adopt skill's line to W2-52's or W2-11's supersession list.
- Ordinary work: yes, because every test designer and lead reads the register to know what is in force, and
  retrieval serves an unmarked entry as in force.
- Consequence: other (a replaced rule served as in force).

### Finding 9. One record type, two incompatible meanings: W1-41's A5 verdict and CAP-44.h's lite verdict (medium)

- **What.** A5, the independent review of the path map before any move, accepts a record only if
  `verdict: pass` (`src/gov/adopt/stages.py:318`). W1-41's fixture writes it as `type: adoption-verdict`
  (`w1_41_support.py:624-636`). Since W2-02, that type is CAP-44.h's lite adoption verdict: its schema allows only
  ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY and requires `conditions`
  (`template/governance/kernel/schemas/adoption-verdict.schema.json`; DEC-741 I (ii), DEC-746 item 4).
- So an A5 record that A5 accepts fails core-schema (a hard-block check) wherever core-schema reads it (`.tickets/`
  and `docs/`). A record core-schema accepts is refused by A5. The cases stay green only because A5 never reads
  `type`, and the fixture's `audit/` folder is outside core-schema's paths. W2-52's unmerged suite reuses the fixture.
- **Proposed change.** An owner decision (package P-I4-4). The 12 functions that rest on the fixture keep their
  "valid" verdict; their fixture follows the decision.
- Ordinary work: yes, because an adopter, EXAMIN's included (W2-26 to W2-28), writes the A5 verdict as the README
  says and may keep it under `docs/`.
- Consequence: other (a hard-block red, or a refused A5, in an adoption: it fails closed).

### Finding 10. Three duplicated whole-tree runs in W1-07 cost 93.5 s of case time per close (low)

- **What.** 61 functions and one more case (121 cases) duplicate another test. Most cost under a second and stay: no
  retirement is proposed for them. They include 14 of W1-06's 54 functions, which repeat registry facts another W1-06
  case already holds, and four W2-02 cases that repeat W2-54's: the two tickets tested the same DEC-626 change (a
  typeless report under `docs/audit/` is an audit report), and both suites' "core-schema is green here" cases read the
  same records, so a bad record commit turns both red in the same close. Three W1-07 groups are expensive, because each
  case runs `gov` on its own whole-tree copy:
  - `test_the_envelope_has_no_field_outside_the_interface` (13 cases, 34.5 s) and
    `test_each_wave_1_operation_is_a_gov_command` (12 cases, 34.1 s) repeat the invocations of
    `test_every_command_returns_the_envelope`, whose `assert_envelope` already checks the field set, the error's keys,
    the exit code and the command field (`w1_07_support.py:436-465`). Packages P-I4-1 and P-I4-2.
  - The 8 `--json` cases of `test_a_read_command_leaves_git_status_empty` (24.9 s) are held by
    `test_a_read_command_changes_no_file_and_no_ref`, which compares the porcelain and more on the same commands
    (`test_w1_07_read_act.py:22-39`). Package P-I4-3.
  - Together: 93.5 s of case time, about 13 s of a close's wall time, and 33 fewer copies exposed to the gc race of
    finding 5.
- Two W1-38 duplicates (1.9 s each) run the real rulesync probe, and W1-35's `test_misspelt_command_is_rejected`
  (12.4 s) repeats another whole-tree `gov check` run. They are kept: after W2-57's probe fix the first two are cheap,
  and the third can be merged by a test designer under W2-67.
- Ordinary work: yes, because every close runs them.
- Consequence: other (close time).

### Finding 11. Three corrections to lens H's report (low)

- **W1-39 does not copy the working tree.** It copies `copier.yml` and `template/` (166 of 2,071 files,
  `w1_39_support.py:211-244`). Lens H counts it among the 13 whole-tree suites whose case time is 48.4 % of the total
  (`H-test-strategy.md:235, 970`); W1-39's 250 s (rehearsal) comes out of that share, and W1-39 is exposed neither to
  the record's size nor to git's gc.
- **The commit that turned W1-06's approvals case red** on 2026-10-21 is `b772b2fe` (08:30:58), which rewrote DEC-843's
  status to "SUPERSEDED by DEC-880". Lens H names `6cce71bb` (`H-test-strategy.md:1178`), which did not touch the
  register. DEC-882 restored the status with a "Changed by" note (`9d8c1887`).
- **W1-31b's three reds of 2026-10-13** (W1-33's research definition, W1-49's window ×2) came from DEC-665, the owner's
  apply block of 2026-10-11, and were rewritten in `9dd9c052` the same day. Lens H's table names DEC-838
  (`H-test-strategy.md:390`), which came six days later. The class (a test asserting a setting a later decision
  changed) is right.
- Ordinary work: no, because these are statements in a report, not behaviour.
- Consequence: other (a wrong measure feeds W2-67's sizing and the lessons).

### Finding 12. W2-66's map: W1-07's suite is a whole-product contract suite, `src/gov/cli/` runs under most suites, and W1-38 reads kernel files it does not declare (medium)

See section 4.1. W1-07's suite runs every command and executes 45 modules outside its declared paths and outside the
shared core. `src/gov/cli/main.py` and `errors.py` run under 30 and 59 suite folders and are not in the shared core
(DEC-880 item 2 (a), DEC-892 c). W1-38 compares generated projects with the kernel's roles and skills, which its
ticket does not declare, so W2-11's role and skill edits would not select it.
- Ordinary work: yes, because a scoped close of a ticket that changes, say, `src/gov/status/` would not select W1-07,
  whose envelope cases run `gov status`, and W2-11 is the next ticket to edit the kernel's roles and skills.
- Consequence: other (a red found by the nightly, a P1 package under DEC-880 (c), not by the close).

### Finding 13. A note for area 2: the gate drops the decision checker's ACTIVE_UNAPPROVED (high by this report's scale, latent; area 2's to confirm)

- **What.** The decision checker reports `ACTIVE_UNAPPROVED`: a decision record set ACTIVE by a commit without the
  owner's `Role: owner` (DEC-360; `src/gov/decisions/checker.py:362-367`). core-authority, the declared check that
  runs it in `gov check`, drops that code (`src/gov/check/authority.py:64-65`), with no comment and no register entry
  (added in `935d9c99`, 2026-10-06, W1-26's source restore). `gov close` reads the code itself, for escalation lifts
  only (`tests/unit/close/test_state.py:268`).
- W1-11's suite and the decision builder tests hold the checker in-process, so they are valid and cannot see the drop.
- **Measured:** the checker finds nothing on the clone at `4166d8d9` (`scripts/unapproved.py`), so no record is
  affected today.
- Ordinary work: yes, because a lead's or the orchestrator's commit that sets a decision file ACTIVE is the slip
  DEC-360 guards against.
- Consequence: fails open (`gov check` stays green), latent. It belongs to area 2 (the checks); I count no test
  verdict for it.

### Finding 14. W1-38's third `load_sensitive` entry covered nothing and refused W2-50's close; DEC-894 fixed its text, DEC-895 now validates every entry before it is sent, and one gap remains (low)

- **What.** The close counts a `load_sensitive` entry only when its decision is an ACCEPTED owner entry "whose text
  names the test (its own name, with its parameter set, as a whole word, and its file)" (`src/gov/close/ratchet.py:1-7`,
  the check at :100-103). As committed with the entry (`49c24ac9`), DEC-892 item 2 named the case as "W1-38's
  `TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[…]`" (register line 10082), without its file
  `tests/acceptance/W1-38/test_w1_38_rulesync.py`. DEC-871 (line 9513) and DEC-886 (line 9835) name their files, and
  their entries count.
- **What happened.** W2-50's close (`gov close DAEO-kl5e`, 2026-10-22 10:28 to 11:40) was refused on two findings: a
  probe finding of W2-50's own, and "the load_sensitive entry tests/acceptance/W1-38/test_w1_38_rulesync.py::
  TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[…] (DEC-892) is refused: DEC-892 does not name the
  test …; it covers nothing" (`log/close-queue-20261022-0952/close-DAEO-kl5e.json`; repair ticket DAEO-h8r2). The case
  itself was not red: the regression had 2 failures, the accepted reds' count, and 14,830 passes. The queue stopped
  there, before W2-58 and W2-62. The same entry also gives its alone run's time with a digit left open (finding 5).
- **What followed.**
  - At 11:52 the orchestrator recorded DEC-894 (`da3d77e1`, delegated). DEC-892's text now names the test in full,
    and the owner's entry (`49c24ac9`) is unchanged.
  - DEC-893 (owner, standing) added a placeholder scan to the record checks.
  - The queue restarted at 11:53. W2-58's close was refused on other grounds (finding 17). W2-62's queue stopped at
    its secrets gate at 13:56 (DEC-897), and its close passed at 16:44 with the entry counted.
  - At 13:35, DEC-895 (owner, standing) made the step this finding first proposed a standing rule, at the source:
    before sending the owner any ratchet or accepted-history entry, the orchestrator validates it with the pinned
    judge's own readers (the ratchet and the close's history reader) against the register as it will stand, and says
    so in the ACT. The orchestrator's `validate_entry.py` refuses the DEC-892 entry as committed at `49c24ac9`, with
    the close's own message.
  - I ran the close's own reading (`gov.close.ratchet.counted_entries`) on a worktree of my clone at `da3d77e1`: all
    32 `load_sensitive` entries and both `accepted_reds` entries count, and none is refused
    (`scripts/ratchet_check.py`).
- **What remains.** An entry valid when it was sent can stop counting later, without anyone touching the list:
  - its decision's status line changes ("SUPERSEDED by", or a "Changed by" note on the part that names the test);
  - or its text is edited.

  DEC-866 has decision records mark old entries at once, so this is ordinary record work. None of DEC-896's pre-close
  gates (a) to (h) runs the ratchet's reading of the two lists, so such a change would be found by a close that has
  already been spent.
- **Proposed change.** Add the ratchet's reading of both lists (`gov.close.ratchet` with the pinned code, as
  `validate_entry.py` does) to the pre-close gates. It takes seconds. No owner decision is needed if the
  orchestrator puts it under DEC-895's standing rule; otherwise it is one line of the next decision record.
- Ordinary work: yes, because a decision record that marks an older decision in a list's chain is ordinary under
  DEC-866.
- Consequence: other (it fails closed: a refused close, about 75 minutes, until the entry is fixed).


### Finding 15. More than a fifth of the kernel skills' checks find a word that stays when the rule goes (medium)

- **What.** W1-35 and W1-36 hold the kernel's method skills (discovery, planning, test design, change, orchestration;
  retrieval, audit, checkpoint, adopt). 41 of their 184 functions are weak: W1-35 30 of 118, W1-36 11 of 66. Each
  passes on a word that stands on another line of the skill too, so the rule's own line can go and the case stays
  green. Examples:
  - "rout" (2 lines of the discovery skill) for the routing rules;
  - "ticket" (2 lines of the audit skill) for "agreed fixes become tickets";
  - "hash" (2) for "the report states the pack hash";
  - "CAP-33" (16 lines) for three different CAP-33 items;
  - the five lifecycle words, which all sit in the change skill's description line;
  - six of the seven CIT step words;
  - four of the five work-order step words. The order case reads first occurrences, and "discovery" first occurs in
    the skill's own name.
- **Evidence: eight planted faults in five skills** (2.4). Each removed or reversed a rule's own line, and the cases
  that claim it stayed green:
  - the change skill's lifecycle starting with the version step (PS-2: both lifecycle cases);
  - its CIT evidence step gone (PS-7);
  - its OpenSpec impact step gone (PS-13);
  - the audit skill sending an owner-level finding straight to a ticket (PS-3);
  - the discovery skill's work order with discovery last (PS-5: two cases);
  - the planning skill's scenario step gone (PS-6);
  - the retrieval skill's statements of disposable subagents gone (PS-11), which left the facets and main-context
    cases green but turned the valid "subagents are disposable" case red;
  - the test-design skill telling the designer to read the implementation (PS-1), which left two of the three
    read-restriction cases green (those three are outdated anyway, finding 7).

  The other verdicts rest on the counted lines (`scripts/word_lines.py`, `word_lines3.py`, `word_lines4.py`) and the
  test lines quoted in 2.2. One template case has the same flaw: W1-34's routing rule, where "raise no package"
  satisfies "package"; with the routing sentence removed (P34-1) it stayed green.
- **How I found the extent.** My second random sample of the valid verdicts drew a close call
  (`test_discovery_sandbox_requirement`, the word "sandbox" anywhere; it stands on the rule's line only, so it stays
  valid). Deciding every word check of both suites by one counted rule then moved 13 that the helpers had marked
  valid to weak, and 3 I had marked weak back to valid (`verdicts/ov_wordchecks.py`). A last pass added 10 more
  (`verdicts/ov_late.py`). It covered every flagged function the first pass had left at "valid", and every text check
  of these suites and of W1-33, W1-34 and W1-41 still at the default. Citation checks and checks that read the
  statement in place were valid.
- **Why it matters.** The skills are the method every adopted project inherits (CAP-24); W2-11 is rewriting them now
  for DEC-820, DEC-838, DEC-847 and DEC-861. A rule dropped in that rewrite, or a later one, passes these suites as
  long as its word survives elsewhere. The suites' own behaviour checks (the skill validator through `gov check`, the
  frontmatter, the token limits, the cited ids) are sound.
- **Proposed change.** W2-11's test designer reads each rule's statement (its phrase or its numbered step) in place of
  the word, for the 41 named in 2.2, with `Rewrite-Reason: the check finds a word that stays when the rule goes`.
- Ordinary work: yes, because W2-11 edits these skills in ordinary work now.
- Consequence: fails open (a rule removed from a kernel skill passes the suite).

### Finding 16. Six valid cases pin behaviour that two planned tickets and a Wave 3 row will change, and none of the three names them (medium)

- **What.** These cases hold the rule in force today, so they are valid. But an approved ticket or the revised plan
  changes that behaviour, and the carrier's ticket does not say that it revises them. They would go red in the
  carrier's own close:
  - **W2-34** (DAEO-yadm, open). Two KPI lines reverse W1-09's three READY cases (`test_w1_09_ready.py:146-167`),
    whose CLOSED specification records have no readiness rows and are closed by hand:
    - "A MISSING required row keeps production tickets out of READY [W2-M274]";
    - "a hand-set status does not bypass readiness [W2-H015]".

    A third line reverses W1-14's `test_the_tasks_template_as_delivered_gives_no_ticket` (`test_w1_14_refusals.py:64-71`,
    the residual DEC-355 recorded): "The delivered tasks.md template is accepted by the bridge [W2-H051]"
    (`.tickets/DAEO-yadm.md:29-31`). W2-34's paths hold neither suite, and the ticket names no revision.
  - **W2-11** (DAEO-k7hz, open). The revised plan widens it to the role files' default lines, with
    `template/governance/kernel/roles/**` added to its paths (`docs/plan/WAVE_2_REVISED_PLAN.md:236-237`; DEC-839 item
    5). W1-33's `test_the_research_role_file_is_unchanged` pins `research.md`'s sha256 (`kernel_role_files.py:151-155`).
    The ticket's paths still hold only `orchestrator.md` (`.tickets/DAEO-k7hz.md:20-38`). Its supersession line names
    W1-35's cases, not this pin.
  - **Row W2-M357** (Wave 3). W1-27's `test_rebuild_no_path_map_returns_envelope` asserts ok true and exit 0 on a
    project without a path map. DEC-735 item 3 rules that a defect. The row's fix "exits non-zero, or warns by name"
    (`docs/plan/WAVE_2_LIST.md:609`); only the first choice turns the case red.
- **Why it matters.** A red in the carrier's own regression refuses its close: about 75 to 85 minutes, and a repair
  ticket. DEC-866's sweep looked for texts and tests that enforce a replaced rule. It did not look for tests that a
  planned change will turn red.
- **Proposed change.** Add one line to each ticket, W2-34 and W2-11, naming these cases, so that its test designer
  revises them in the same change. The `Rewrite-Reason:` lines are W2-M274, W2-H015 and W2-H051 for W2-34, and DEC-839
  item 5 for W2-11. Row W2-M357 names W1-27's case. These are the orchestrator's ticket edits; no owner decision is
  needed.
- Ordinary work: yes, because both tickets are in this wave's plan.
- Consequence: other (a refused close and a repair ticket; nothing fails open).

### Finding 17. The owner's commits to the two lists refused W2-58's close; DEC-896 has since decided the cause, and nothing more is proposed (low)

- **What happened.** W2-58's close (`gov close DAEO-5j8b`, queue run 8) ran from 12:17:35 to 13:28:18 and was refused
  with `WORK_WITHOUT_TASK` (exit 3; `log/close-queue-20261022-1153/close-DAEO-5j8b.json`; repair ticket DAEO-aneq).
  - It named seven commits since the ticket's trailers base, each "names no task and changes
    governance/project/path-map.yaml: work on DAEO-5j8b that no ticket measured". One changes the ticket file instead.
  - Three are the owner's own decision-record commits (`Task: decision-record`, `Role: owner`), and they are exactly the
    `load_sensitive` entries this review weighs: `8dfd54e9` (DEC-871's two W1-38 entries), `cf8219a8` (DEC-886's W1-07
    entry) and `49c24ac9` (DEC-892's third W1-38 entry).
  - The other four are the orchestrator's decision records (`Role: orchestrator`, two of them decided by the owner in
    the chat): DEC-876 `65039414`, DEC-880 `b772b2fe` (the ticket file), DEC-887 `dbd3cc53` and DEC-891 `4166d8d9`.
  - No test refused it: the regression had 14,658 passes, 2 failures (the accepted reds' count) and 31 skips. The
    serial run had 263 passes. No area-4 case was red.
- **Why.** The two owner lists live in `governance/project/path-map.yaml`, and W2-58's allowed paths hold that file
  (`.tickets/DAEO-5j8b.md`), as do W2-66's (DAEO-c1uz, open). A decision-record commit carries no ticket's task, so
  the close counts its change to a ticket's path as untracked work. DEC-891's standing rule (register line 10058) lets
  the orchestrator record an accepted-history entry for a record-only commit. But its list of records leaves out the
  path map, and an entry for "any other path that is not a record" stays the owner's own `Role: owner` commit. So each
  list commit costs:
  - the next close of every ticket that holds the path map;
  - one more owner commit to clear it.
- **Why it mattered for the lists.** W2-57's planned removal of the four `load_sensitive` entries (DEC-889 item 5) is
  another owner commit to the same file, and so is any new entry. Here the close was spent before the finding
  appeared: 71 minutes.
- **What the owner has since decided.** DEC-896 (owner, 2026-10-22 14:16, on package P-W2-58-C1) covers each part the
  first draft of this finding proposed:
  - item 1, a W2-07 KPI: a decision-record commit that changes only governance records, under an ACCEPTED decision,
    counts as measured for the work-without-a-task gate;
  - item 2: the test-selection lists move into their own file, and the path map stays a shared record that no
    ticket's allowed paths name (for W2-66's and W2-68's drafts);
  - item 4: until the re-pin carries W2-07, no close starts unless the pre-close gates (a) to (h) predict a pass, (e)
    the trailers and (h) the work-without-a-task gate with the pinned code among them;
  - W2-58 waits for that re-pin.
- **What is left.** W2-58's own ticket still names the path map, for its `evaluation_sets` block
  (`.tickets/DAEO-5j8b.md:24`). Gate (h) now finds the refusal before a close is spent, and W2-07's KPI clears it
  after the re-pin, so nothing more is proposed. W2-57's removal of the four entries, an owner commit to the path map,
  is the next commit this applies to.
- Ordinary work: yes, because the owner's list commits are ordinary.
- Consequence: other (it failed closed: one refused close of 71 minutes; gate (h) now stops the queue first).

## 6. Owner packages

Five packages, in DEC-818's six parts: three proposed retirements (P-I4-1 to P-I4-3) and two other owner decisions
(P-I4-4, P-I4-5). Each stands alone, and none blocks this audit or any part of it: the verdicts above stand whatever
the owner decides.

The other changes this review proposes need no new owner decision:
- the test revisions go to test designers with a `Rewrite-Reason:` (section 2);
- the plan and map changes go to the orchestrator's drafts at DEC-889's review point (section 4);
- the five unmarked entries of finding 8 go to the orchestrator's next record, under DEC-866's standing order;
- finding 14's gate step can go under DEC-895's standing rule.

Times are case time in the rehearsal's parallel run (the close's form,
`dbd3cc53`, 2026-10-21); a close's wall time is about 0.14 s per case-second there (31.8 minutes for 13,417 s on 20
workers).

### P-I4-1. Retire W1-07's `test_the_envelope_has_no_field_outside_the_interface`

1. **Context.** W1-07 (DAEO-drvn, closed) built the command line's JSON envelope, whose fields and exit codes
   `docs/interfaces/API-0002.yaml` defines. Its acceptance suite holds the envelope with
   `test_every_command_returns_the_envelope`: 13 invocations (the twelve reserved commands and `check --list`), each
   in the test's own whole-tree copy, each checked by `assert_envelope` (`tests/acceptance/W1-07/w1_07_support.py:436-465`).
   This test review (DEC-889 item 16) found a second function that runs the same 13 invocations. W1-07's README
   already says of its KPI Failure 2 that it is held by this function "· every test that calls `assert_envelope`
   (all files)" (`tests/acceptance/W1-07/README.md:45`).
2. **What happened, with the evidence.** `test_the_envelope_has_no_field_outside_the_interface`
   (`test_w1_07_envelope.py:28-38`) runs the same `EVERY_INVOCATION` list with the same fixture choice, and asserts
   that the envelope holds the required fields and no others, and that an error has exactly the interface's keys.
   `assert_envelope` asserts all of that and more: no field outside the interface (:439-441), each required field
   present with its type (:442-445), the exit code (:446), `ok` against the exit code and the error (:449-454), the
   error's exact keys (:455-457), the code's form, the message, and the command field. So every fault this function
   can catch, the envelope case catches on the same run. Cost: 13 `gov` runs on 13 whole-tree copies, 34.5 s in the
   rehearsal.
3. **Why it matters.** Each close spends that time, and each copy is one more exposure to the copy race of finding 5.
   This function's own `[check]` case was one of the five the race hit in my parallel runs on the fat tree.
   The Gov OS's test suite should hold each rule once, so its cost stays proportional to what it protects.
4. **Options.**
   - (a) Retire the function. Saves 34.5 s of case time (about 5 s of a close's wall time). Risk: none found; the rule
     stays held by the envelope case. No Contract, specification, skill or brief change; W1-07's README names the
     case and would be updated by the test designer.
   - (b) Keep it. Cost: 34.5 s per close and per lead verification. Risk: none to safety.
   - (c) Merge: fold its docstring's KPI label into the envelope case. The same saving as (a).
5. **Classification (DEC-809):** ordinary work yes; other (close time only).
   **Recommendation:** (a), or (c) if the KPI's traceability matters to the owner. Confidence: high (both bodies read
   and compared line by line).
6. **What it blocks, what waiting costs.** It blocks nothing. Waiting costs 34.5 s of case time per close. If
   accepted, a test designer removes it under W2-67 with `Rewrite-Reason: duplicate of
   test_every_command_returns_the_envelope (assert_envelope)`.

### P-I4-2. Retire W1-07's `test_each_wave_1_operation_is_a_gov_command`

1. **Context.** W1-07 (DAEO-drvn, closed) built the command line and its JSON envelope (`docs/interfaces/API-0002.yaml`).
   CAP-28.b asks that each Wave 1 operation be a `gov` command; W1-07 wrote this function for that KPI line (S5).
   Its envelope case, `test_every_command_returns_the_envelope`, already runs every reserved command, each in the
   test's own whole-tree copy, and checks it with `assert_envelope` (`tests/acceptance/W1-07/w1_07_support.py:436-465`).
2. **What happened, with the evidence.** This function (`test_w1_07_registry.py:41-49`) runs `invocation(name)` for
   each of the twelve reserved commands with the same fixture choice. Those are 12 of the envelope case's 13
   invocations (`EVERY_INVOCATION`, `w1_07_support.py:115`). It then asserts the exit code is not 2 and calls the same
   `assert_envelope(run, interface, command=name)`. Exit 2 is argparse's usage error, which prints no envelope, so
   `assert_envelope` already fails on it (`run.envelope()`, :396-399). Cost: 12 `gov` runs on 12 whole-tree copies,
   34.1 s of case time in the rehearsal (about 5 s of a close's wall time).
3. **Why it matters.** Each close and each lead's verification spends that time for no fault the envelope case misses,
   and each copy is one more exposure to the copy race of finding 5.
4. **Options.** (a) Retire; saves 34.1 s. (b) Keep; no risk to safety, the time stays. (c) Merge: move its CAP-28.b
   label into the envelope case's docstring and README row, and retire the runs; the same saving. None changes the
   Contract, a specification, a skill or a brief.
5. **Classification (DEC-809):** ordinary work yes; other (close time only).
   **Recommendation:** (c): the label keeps CAP-28.b's trace, and the runs go. Confidence: high (both bodies read).
6. **What it blocks, what waiting costs.** It blocks nothing; waiting costs 34.1 s of case time per close. If accepted,
   a test designer makes the change under W2-67 with `Rewrite-Reason: duplicate of
   test_every_command_returns_the_envelope`.

### P-I4-3. Retire the eight `--json` cases of W1-07's `test_a_read_command_leaves_git_status_empty`

1. **Context.** CAP-27.a: a read command changes nothing. W1-07 (DAEO-drvn, closed) holds it with two functions over
   the same eight read commands (`READ_COMMANDS`), each case in the test's own whole-tree copy.
2. **What happened, with the evidence.** `test_a_read_command_leaves_git_status_empty` runs each read command with
   `--json` and without (16 cases) and compares `git status --porcelain` before and after
   (`tests/acceptance/W1-07/test_w1_07_read_act.py:43-53`). `test_a_read_command_changes_no_file_and_no_ref` (:55-59)
   runs the same eight commands with `--json` and compares the porcelain, HEAD and the refs, every file of the project,
   the home and a folder outside (`_state`, :22-28; `_assert_unchanged`, :31-39). So the eight `--json` cases of the
   first are held by the second on the same commands. The eight plain cases are not, and stay. Cost of the eight:
   24.9 s of case time in the rehearsal (`json-check` 8.7 s, `json-status` 6.3 s, `json-doctor` 5.7 s), about 3.5 s
   of a close's wall time.
3. **Why it matters.** Each close and each lead's verification spends that time for no fault the other function
   misses, and each copy is one more exposure to the copy race of finding 5.
4. **Options.** (a) Narrow the parametrisation to the plain form; saves 24.9 s; the README's row changes from 16 cases
   to 8. (b) Keep both forms; no risk to safety, the time stays. Neither changes the Contract, a specification, a skill
   or a brief.
5. **Classification (DEC-809):** ordinary work yes; other (close time only).
   **Recommendation:** (a). Confidence: high (both bodies and the helpers read).
6. **What it blocks, what waiting costs.** It blocks nothing; waiting costs 24.9 s of case time per close. If accepted,
   a test designer narrows it under W2-67 with `Rewrite-Reason: the --json sets duplicate
   test_a_read_command_changes_no_file_and_no_ref`.

### P-I4-4. The A5 verdict and CAP-44.h's lite verdict share one record type (DEC-105)

1. **Context.** Adoption stage A5 is an Independent Auditor's review of the path map before any file moves (CAP-44.c,
   DEC-090, DEC-490). W1-41 (DAEO-cdoi, closed) built it: A5 accepts a record only if its `verdict` is `pass`
   (`src/gov/adopt/stages.py:318`), and W1-41's fixture writes that record as `type: adoption-verdict`
   (`tests/acceptance/W1-41/w1_41_support.py:624-636`; the unit fixture `tests/unit/adopt/test_adopt.py:88-93`).
   Later, Contract v4.2 brought CAP-44.h's lite adoption verdict into Wave 2 (DEC-741 E and I (ii)), and W2-02
   (closed) gave it the record type `adoption-verdict`: the verdict is ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS
   or NOT_ADOPTED_HEALTHY, and `conditions` is required
   (`template/governance/kernel/schemas/adoption-verdict.schema.json`; DEC-746 item 4).
2. **What happened, with the evidence.** The two meanings now share one type.
   - A record A5 accepts (`verdict: pass`, no `conditions`) fails core-schema, a hard-block check, wherever
     core-schema reads it: everything with frontmatter under `.tickets/` and `docs/` (`src/gov/check/schema.py:12, 37,
     43`).
   - A record core-schema accepts is refused by A5 (`VERDICT_NOT_PASS`).
   - The 12 functions that rest on the fixture (W1-41's 8 verdict cases and 1 migration case; 3 builder tests) stay
     green only because A5 never reads `type`, the store checks required keys only, and the fixture's `audit/` folder
     is outside core-schema's paths.
   - W2-52's unmerged suite reuses the fixture. The adopt skill still says the final verdict is Wave 3
     (`template/governance/kernel/skills/adopt/SKILL.md:41`, citing DEC-090), which DEC-741 E changed.
3. **Why it matters.** Adoption is how the Gov OS reaches another repository, EXAMIN's first (W2-26 to W2-28). An
   adopter who follows W1-41's README and keeps the A5 record under `docs/` meets a hard-block red; one who follows
   the schema meets a refused A5. Either stops the adoption at the review step.
4. **Options** (DEC-105).
   - (a) **Apply now:** give the A5 review its own record type (for example `path-map-review`, with `verdict: pass |
     fail | inconclusive | pass_with_findings`), have A5 read the type, and revise W1-41's two fixtures and its
     README with `Rewrite-Reason: DEC-741 I (ii) gave adoption-verdict to CAP-44.h`. Cost: a small engineer and test
     designer round (A5's reader, one schema, the two fixtures that 12 functions use), before W2-52 merges. Risk:
     low; it is a rename where nothing reads the old type. Changes: one kernel schema added; CAP-44's text unchanged.
   - (b) **Defer:** make it an entry criterion of W2-52, the ticket that switches the lite verdict on (DEC-803), with
     the same fix there. Cost: none now; W2-52's scope grows a little. Risk: an adoption run before W2-52 (EXAMIN's)
     can meet it.
   - (c) **Re-baseline:** let A5 write CAP-44.h's form (one record type for both). Cost: A5's four review outcomes
     (pass, fail, inconclusive, pass_with_findings) must map onto the three health verdicts, which mixes a review before
     any move with a health verdict after them; CAP-44.c's wording would change. Risk: the meanings stay mixed.
5. **Classification (DEC-809):** ordinary work yes; other (it fails closed: a hard-block red or a refused A5).
   **Recommendation:** (b), with the rename of (a) as W2-52's entry criterion, unless EXAMIN's adoption reaches A5
   before W2-52 merges; then (a). Confidence: medium (the collision is read from code and schema, not met in a run).
6. **What it blocks, what waiting costs.** It blocks nothing today. Waiting costs nothing until an adoption keeps an
   A5 record under `docs/` or W2-52 lands; then it costs a stopped adoption and a repair round.

### P-I4-5. The rulesync probe's limit: keep the four entries, widen W2-57's first item to the probe's four effects, and do not grow the list case by case

1. **Context.**
   - `load_sensitive` (in `governance/project/path-map.yaml`) is the owner's list of cases a close re-runs alone when
     they fail in the parallel run; only the owner grows it (DEC-766) and commits it (DEC-862 (a)).
   - Area 4 holds four entries, all `fixed_by: W2-57`: W1-07's `doctor` envelope case (DEC-886) and three W1-38
     rulesync cases (DEC-871, DEC-892).
   - DEC-892 item 2 makes the rulesync probe W2-57's first item.
   - Two parts of this package's first draft have since been decided: DEC-895 (13:35) has every list entry validated
     before it is sent, and DEC-896 (14:16) handles the lists' own commits (findings 14 and 17). What remains is the
     probe.
2. **What happened, with the evidence.**
   - **The cause of the three W1-38 entries is the portability check's 10-second limit** on `rulesync --version` and
     `generate` (`src/gov/adapters/portability.py:38, 63-72, 84, 173`). The closes printed `RULESYNC_FAILED`, "no
     answer within 10 seconds": W2-53's of 2026-10-20 12:30 (two cases) and W2-63's of 2026-10-22 00:11 (one).
   - **Measured under load:** in my runs the probe took 0.33 to 2.81 s (42 samples, loads up to 47.1), and the three
     cases passed 3 of 3 alone and 3 of 3 in the suite's parallel run. So the closes' timeouts are spikes of a close's
     load, not the usual case.
   - **Measured by running the cause** (2.4): a stand-in `rulesync` answered after 11 seconds.
     - With the check's `--version` slow, 30 W1-38 cases in 19 functions went red; with its `generate` slow, 28 cases
       in 17 functions. The three entries were red in both, and the 9 masked cases stayed green in both.
     - With every `--version` slow, 181 W1-38 cases and W1-33's research case were skipped as "rulesync is not
       installed", none failed, and pytest exited 0.
   - **So the list's three entries are 3 of the 30 cases the same limit can turn red.**
     - 27 more can refuse a close.
     - 9 cases pass without comparing when the limit is hit.
     - The fixture's own 10-second probe turns the limit into a silent skip of up to 181 cases; the close counts
       skips without refusing them (DEC-500).
   - **W1-07's `doctor` entry is not reproducible:** green in all 12 runs here, and the close keeps no failure text
     (finding 5). It stays until W2-57, as DEC-886 says.
3. **Why it matters.**
   - Growing the list one case per refused close costs, for a cause already known, each time:
     - a refused close (75 to 85 minutes, and a count towards escalation);
     - an owner decision and commit.
   - The skip fails open: a close whose workers' fixture probes time out passes with W1-38's rulesync cases never
     run, and W1-33's research case with them.
4. **Options.**
   - (a) **Keep the four entries until W2-57, and widen W2-57's first item** (DEC-892 item 2) to the probe's four
     effects:
     - the check's two calls and their limit;
     - the session fixture's skip, which should fail instead (a timeout is not an absent tool);
     - the 9 masked cases, which should assert the finding they expect, not only "not green";
     - W1-33's skip.

     Cost: a larger first item for W2-57 (the check's limit, one fixture, one W1-33 helper, and the assertions of 3
     functions with 9 cases). Risk: until W2-57 lands, any of the 27 others can refuse a close, as three cases did in
     two closes since 2026-10-20.
   - (b) **As (a), and add the 27 red-on-timeout cases to the list now.**
     - Cost: one owner commit naming each case in full with its file (the ratchet's rule), validated under DEC-895
       before it is sent.
     - Risk: 27 more cases whose failure is re-run alone before it counts (a re-run alone still catches a real
       fault), and a list that grows past what W2-57 will remove.
   - (c) **Keep everything as it is:** W2-57's first item as DEC-892 wrote it, the probe only. Cost: none now; a
     refused close at each further timeout, and the skip and the 9 masked cases stay.
5. **Classification (DEC-809):** ordinary work yes; fails open (the fixture's skip, the 9 masked cases); other
   (refused closes on timeouts).
   **Recommendation: (a).** Confidence: high: the cause was shown by running it, the closes' own output names it, and
   the code reads the same.
6. **What it blocks, what waiting costs.**
   - It blocks nothing.
   - Waiting costs a refused close each time one of the 27 meets the limit, and leaves the silent skip in place.
   - A related step needs no owner decision: the ratchet's reading of both lists as a pre-close gate (finding 14's
     remaining gap) can go under DEC-895's standing rule.
