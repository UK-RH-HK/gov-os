# W2-202 acceptance tests: gov queue becomes the landing-and-close, part 1 (DAEO-l2bd)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines (9 success, 5 failure), from
`docs/emergency-2/L2-COMMANDS.md` §2 and §3 (items A1, A3, A4, A5; DEC-1214 L2, Q-CLOSE) and the lead's interface
naming (codes, answer and record keys), never from the implementation.

## How the suite runs

- **Public interfaces only:** `python3 -m gov.cli.main queue <ticket>[=<branch>] ... --root <project> --json` (and
  `gov pause`, `gov accept`, `gov adopt --facts`) with this worktree's `src/` on `PYTHONPATH`; the envelope, stderr and
  exit code; the planted repository's git state; the close record `docs/close/<id>/CL-<id>.md`; the queue's record
  `.gov-runtime/queue/<stamp>/queue.json`; the JUnit files under `.gov-runtime/`.
- **It stands on W2-115b's support** (`tests/acceptance/W2-115b/w2_115b_support.py`, imported as `kit` by
  `w2_202_support.py`): the planted project (a package `app`, tickets, a suite per ticket, unit tests, the test map,
  the kernel's `tk`), the telling tests (one JSON line per run: the tree, what the test saw, whether it passed), the
  answer and refusal readers. Each planted acceptance folder's README holds a KPI map (two lines on the suite's test).
- **The fixtures check themselves:** before `gov queue` runs, each build runs the planted tests with plain pytest in a
  scratch clone at the commits the case depends on (red where it needs red, green where it needs green), reads the
  freeze flag back as `gov.util.freeze.freeze_state` reads it, asks the close's own gates (`check_evidence`,
  `check_specification`) of each planted record, and runs `gov accept` at the branch tip. A broken fixture fails as
  `fixture: ...`, never as a red.
- **Each planted run is built once per session** (`conftest._shared`, a file lock in pytest's shared base folder); a
  build that fails is reported by every case that reads it.
- **No network, no model; deterministic; no wall-clock bound.**
- Run: `TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-202 -q -p no:cacheprovider`,
  or `gov accept W2-202`. Seventeen planted `gov queue` runs and three `gov adopt --facts` runs.

## The planted runs

| run | project and branches | command |
|---|---|---|
| base_red | `main`; `tests/unit/test_known_red.py` red in the first commit (a bare assert), importing the widget; A changes the widget | `PROJ-aaaa=topic/aa` |
| untrailered | as base_red, but the test (it guards the gizmo) goes red by a second commit on `main` with no trailer at all, which breaks the gizmo | `PROJ-aaaa=topic/aa` |
| each_breaks | `tests/unit/test_both.py`, green on the base, red when the widget or the gadget says CHANGED; A changes the widget, B the gadget (each own suite green) | A and B |
| another_way | the known red fails with a bare assert on the base and with a `ValueError` once the widget is changed; A changes the widget | `PROJ-aaaa=topic/aa` |
| mixed | the known red (base, reached by A, clean) and B, which breaks the gadget that `tests/unit/test_uses_gadget.py` and its own suite guard | A and B |
| no_tests | N, a feature ticket whose acceptance folder holds a README and no test (its module is reached by a unit test); A green | N alone; then N and A |
| classes | R (research), U (audit), O (coordination), S (specification): no acceptance folder, each a record on its branch that its class's gate accepts; N as above; X, a research ticket whose record is no `type: research` record; a record-reading set `tests/records/` | R, U, O, S, N; then X alone |
| accepted | A green; `gov accept PROJ-aaaa` run on a scratch clone at the tested merge after the landing | `PROJ-aaaa=topic/aa` |
| merged | A's branch merged into `main` by hand (`--no-ff`), the ticket open | `PROJ-aaaa=topic/aa`, twice |
| merged_refused | C's branch (a code commit and an engineer's commit to its suite) merged by hand | `PROJ-cccc=topic/cc` |
| paused | `main` at the root, neither `queue.yaml` nor `close.yaml`; A green; `gov pause`, queue, the freeze lifted, queue | `PROJ-aaaa=topic/aa`, twice |
| paused_detached | as paused, the root detached | `PROJ-aaaa=topic/aa`, twice |

## KPI map

The ticket's lines are numbered in the order of the ticket file; the L2 line each one is stands beside it.

| KPI id | L2 line | tests | expected red reason |
|---|---|---|---|
| success-1 | A1 S1 | `test_w2_202_base_reds.py::test_a_batch_with_a_red_that_is_red_at_the_base_lands_and_exits_0`, `test_w2_202_base_reds.py::test_the_close_record_lists_the_base_red_with_its_type_and_the_base_commit`, `test_w2_202_base_reds.py::test_the_answer_and_the_queue_s_record_name_the_base_red`, `test_w2_202_base_reds.py::test_the_base_red_ran_on_the_merged_result_and_the_green_tests_too` | the base refuses the batch: `BATCH_UNEXPLAINED`, exit 3 ("the queue's answer is not ok") |
| success-2 | A1 S2 | `test_w2_202_base_reds.py::test_a_red_made_by_a_commit_without_a_trailer_is_a_base_red_and_the_ticket_lands`, `test_w2_202_base_reds.py::test_the_commit_without_a_trailer_is_under_the_landed_head_and_nothing_names_it_a_culprit` | as success-1 |
| success-3 | A1 S3 | `test_w2_202_base_reds.py::test_a_red_green_at_the_base_that_no_single_candidate_explains_is_batch_unexplained`, `test_w2_202_base_reds.py::test_the_refused_batch_leaves_the_integration_branch_and_both_tickets_as_they_were`, `test_w2_202_base_reds.py::test_a_red_at_the_base_that_fails_another_way_with_the_change_is_not_a_base_red` | the first: the base never runs the red at the base ("the red was not run once at the base (green there): 0 run(s)"); the other two are guards, green on the base by design (the refusal stays) |
| success-4 | A3 S1 | `test_w2_202_acceptance.py::test_a_feature_ticket_whose_acceptance_folder_holds_no_test_is_refused_alone_and_nothing_moves`, `test_w2_202_acceptance.py::test_the_refusal_comes_before_any_run`, `test_w2_202_acceptance.py::test_in_a_batch_the_ticket_without_tests_is_out_and_the_other_lands` | the base's queue has no such check: the ticket lands, exit 0 ("exit 0, not 3") |
| success-5 | A3 S2 | `test_w2_202_acceptance.py::test_a_ticket_judged_on_its_record_lands_without_a_test_folder_where_a_feature_ticket_is_refused`, `test_w2_202_acceptance.py::test_each_class_judged_on_a_record_lands_and_closes`, `test_w2_202_acceptance.py::test_a_ticket_whose_record_its_class_s_gate_refuses_does_not_land` | the base judges no ticket by its class: the feature ticket without tests lands beside the four (exit 0, not 3), and the ticket whose record the gate refuses lands |
| success-6 | A3 S3 | `test_w2_202_acceptance.py::test_the_close_record_holds_the_acceptance_folder_and_each_kpi_line_s_result`, `test_w2_202_acceptance.py::test_the_record_s_lines_equal_gov_accept_s_own_answer_on_the_tested_merge` | "the close record holds no acceptance" |
| success-7 | A4 S1 | `test_w2_202_merged.py::test_a_ticket_merged_by_hand_is_closed_by_the_queue_with_exit_0`, `test_w2_202_merged.py::test_the_queue_makes_no_merge_commit_only_the_close_commit_on_the_head`, `test_w2_202_merged.py::test_the_close_record_is_written_for_the_hand_merged_ticket`, `test_w2_202_merged.py::test_the_run_ran_on_the_head_and_the_root_follows`, `test_w2_202_merged.py::test_the_checks_still_run_for_a_branch_already_merged` | the base refuses `CANDIDATE_NOT_ISOLATED` ("already merged"), exit 3 |
| success-8 | A5 S1 | `test_w2_202_pause.py::test_while_the_project_is_paused_the_queue_refuses_with_project_paused_and_exit_1`, `test_w2_202_pause.py::test_while_paused_nothing_is_written_and_the_branch_and_the_ticket_are_as_they_were`, `test_w2_202_pause.py::test_after_the_freeze_is_lifted_the_queue_lands` | the base's queue does not read the freeze flag: it lands while paused ("the queue did not refuse") |
| success-9 | A5 S2 | `test_w2_202_pause.py::test_gov_adopt_facts_writes_queue_yaml_with_the_integration_branch_and_the_work_branch_form`, `test_w2_202_pause.py::test_gov_adopt_facts_writes_no_close_yaml_and_leaves_a_present_queue_yaml_as_it_is` | "gov adopt --facts wrote no governance/project/queue.yaml" |
| failure-1 | A1 F1 | `test_w2_202_base_reds.py::test_the_candidate_that_breaks_a_green_test_is_the_culprit_and_does_not_land`, `test_w2_202_base_reds.py::test_the_red_the_candidate_causes_is_never_recorded_as_a_base_red` | the batch holds a base red beside the culprit: the base refuses it whole, `BATCH_UNEXPLAINED` |
| failure-2 | A1 F2 | `test_w2_202_base_reds.py::test_a_base_red_creates_no_ticket_file_and_no_line_under_docs_outside_the_close_s_places`, `test_w2_202_base_reds.py::test_the_root_and_the_clone_hold_no_untracked_ticket_or_docs_path_after_the_base_red` | as success-1 (each first reads the landing's answer, so none is green by nothing having landed) |
| failure-3 | A3 F1 | `test_w2_202_acceptance.py::test_no_test_of_the_acceptance_folder_ran_twice_in_the_landing`, `test_w2_202_acceptance.py::test_the_selection_s_run_still_ran_the_tests_the_change_reaches` | as success-6 (the acceptance run must have happened: the record holds its lines) |
| failure-4 | A4 F1 | `test_w2_202_merged.py::test_a_closed_ticket_is_still_ticket_closed_after_its_hand_merged_landing` | as success-7 (the ticket is first closed by the queue from its hand-merged branch) |
| failure-5 | A5 F1 | `test_w2_202_pause.py::test_with_neither_settings_file_and_the_root_on_main_the_queue_lands_onto_main`, `test_w2_202_pause.py::test_with_no_setting_and_no_branch_the_queue_is_integration_unknown_as_before` | as success-8 (each first reads the paused refusal) |

Every case is an acceptance test. Two cases are green on the base by design, as guards of a refusal that stays (both
under success-3): the batch refused `BATCH_UNEXPLAINED` leaves everything as it was, and a red at the base that fails
another way with the change is not a base red.

## Readings this suite takes

1. **A known base red** (success-1): the close record's `reds` holds exactly one entry for the test, with `test` (its
   node id), `verdict: base`, `failure_type` (`AssertionError` for the planted bare assert) and `base` (the full id of
   the integration head the run merged onto); `base_reds` is the list of the base reds' node ids; the answer's and
   `queue.json`'s `base_reds` hold the same ids (ids, or entries holding `test`). The answer is `ok: true`, exit 0.
2. **"Nothing is excused or refused by a trailer"** (success-2): the red-making commit is on the integration branch
   under the base, with no `Task:` and no `Role:`; the landing is as success-1's, the record's `base` is that commit.
3. **"No single candidate explains"** (success-3) is planted as the line states it, with two candidates: each one's
   change turns the same test red, so the test is red with either left out, and green at the base. The line's
   Verify words it "two candidates whose changes fail only together"; under the queue's leave-one-out search such a
   red is green with either candidate left out, so each candidate explains it and both are culprits (exit 3, nothing
   lands, no `BATCH_UNEXPLAINED`). The planted batch is the one the refusal belongs to; the difference is returned to
   the lead as a proposed decision. "Run once at the base" is read from the telling test: exactly one run in a tree
   where neither change is present, and it passed.
4. **"The same failure type"** (success-3's guard) compares how the red fails in the batch's run with how it fails at
   the base: a bare assert at the base and a `ValueError` with the candidate's change are not the same.
5. **A culprit beside a base red** (failure-1): the culprit's red has `verdict: culprit` in the landed ticket's record
   and is in no `base_reds`; the rest (A alone) lands although its run still holds the known base red.
6. **Failure-2's places:** the tree diff of the old head against the landed head changes one path under `.tickets/`
   (the landed ticket's own file, modified) and nothing under `docs/` outside `docs/close/` and `docs/checkpoints/`;
   the folder `.tickets/` at the root holds the files it held; `git status --porcelain` of the root and of the queue's
   warm clone (`.gov-runtime/close/clone`) shows no such path.
7. **"Holds no test"** (success-4): the folder is declared in `acceptance_tests.path` and holds its README alone. A run
   whose every candidate is refused answers `ok: true`, `landed: []`, exit 3, with no run made.
8. **"Judged on its record"** (success-5): each record ticket's file names its class and its record
   (`acceptance_tests.evidence`; `specification` for the specification, whose record is `openspec/changes/first/`
   with every mandatory readiness row PRESENT), and declares no `acceptance_tests.path`. The test map places the
   record folders in `record_only` and names a record-reading set. The ticket whose record the gate refuses must not
   land: any non-zero exit that names the ticket, nothing moved, the ticket open (the code is not fixed here).
9. **The record's `acceptance`** (success-6): `folder` is the declared path (slashes at the ends aside); `lines` holds
   one entry per KPI line of the folder's README map, read as (the line, pass or fail) under the runner's names
   (`kpi`, `outcome`) or `id`, `result`; where it keeps the runner's names, the whole entries equal `gov accept
   PROJ-aaaa --root <a clone at the tested merge> --json`'s `lines`.
10. **"No test runs twice"** (failure-3): the acceptance folder's one test told exactly one run in the whole landing,
    on the merged result; `selection.suites` names no path of the folder; all the JUnit files the landing leaves under
    `.gov-runtime/` (the warm clone aside) name the folder's test at most once (a JUnit file of the acceptance run, if
    one is kept, is that once).
11. **"No merge commit is made by the queue"** (success-7): exactly one commit lies over the hand-merged head, the
    close commit, whose one parent is that head; the answer's `tested` and the record's `commit` are that head; the
    record's `branch.tip` is the work branch's tip. The run on the head ran the ticket's own test and the importer
    of its changed module.
12. **The freeze** (success-8, failure-5) is set by `gov pause --root <project> --json` with no `GOV_ROLE` (the owner).
    It is lifted as `gov pause --off` lifts it: the flag `.gov-runtime/freeze` and its mirror under the sandbox home
    are removed, and `freeze_state` must read `absent`. `--off` itself is not run: it asks for the owner in person at
    a terminal with no Claude Code session among its ancestors (DEC-409), which no test run has. "Nothing written" is:
    every ref, what `HEAD` is, the status and every tracked file as before, and the listing of `.gov-runtime/` as it
    was after the pause.
13. **Failure-5** is tested where the pause meets it: the project with neither settings file and the root on `main`
    lands onto `main` once the freeze is lifted; a detached root is `PROJECT_PAUSED` while frozen (the freeze is read
    first) and `INTEGRATION_UNKNOWN` after. The plain cases stay in W2-115b
    (`test_w2_115b_settings.py::test_a_detached_root_with_no_onto_and_no_queue_yaml_is_integration_unknown`, and its
    landings on `main` with no `queue.yaml`).
14. **Failure-4** is tested on the ticket the queue has just closed from its hand-merged branch (the path A4 changes);
    the plain case stays in `tests/unit/queue/test_queue_land.py::test_an_unknown_or_closed_ticket_is_refused`.

## For the engineer

- Every planted acceptance folder has a README with a KPI map, so the runner `gov accept` uses can read it. What the
  queue does with a folder that holds tests and no map is not tested here.
- The planted test names are told by the tests themselves (`told/<test>.jsonl`), also when the acceptance runner runs
  them: the runner's child keeps the queue's environment but for `PYTEST_*` and `PYTHON*`.
- `gov pause` writes its mirror under the sandbox home (`HOME` of the queue's environment).

## Not tested here

- A2, A6 to A8 and every B item (the ticket's non-goals); the strict close and `accepted_reds`.
- A failing acceptance line as the only sign of a culprit (the selection's run no longer holding the folder): no KPI
  line of this ticket names it; W2-115b's red and batch runs hold a culprit whose own suite fails.
