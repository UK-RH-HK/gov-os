# W2-206 acceptance tests: gov queue becomes the landing-and-close, part 2 (DAEO-l2b2)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines (7 success, 4 failure), from
`docs/emergency-2/L2-COMMANDS.md` §2 and §3 (items A6 and A8; DEC-1214 L2, DEC-1216 (5)) and the lead's interface
naming (flags, `queue.json`'s keys, the runner's keyword), never from the implementation.

## How the suite runs

- **Public interfaces only:** `python3 -m gov.cli.main queue <ticket>[=<branch>] ... --root <project>` with `--json`
  (and `--dry-run [--out <dir>]`, `--full`, `--timeout`) or without it (`--select`), and `gov wait`, `gov close
  --select`, `gov check --structural`, `gov rebuild --integration`, `gov retrieve`, `gov accept`, with this worktree's
  `src/` on `PYTHONPATH`; the envelope, stdout, stderr and exit code; the planted repository's git state; the close
  record; `.gov-runtime/queue/<stamp>/queue.json`; the files under a dry run's `--out`. Fix 1 is read where its line
  names it: `gov.accept.runner.accept(..., keep_report=<path>)` and `gov.queue.acceptance.run`, called in the test's
  own process.
- **It stands on W2-202's support** (`tests/acceptance/W2-202/w2_202_support.py`, and through it W2-115b's planted
  project kit) and, for the integration store, on W2-116's stand-in embedding endpoints
  (`tests/acceptance/W2-116/w2_116_support.py`).
- **The fixtures check themselves:** before `gov queue` runs, each build runs the planted tests with plain pytest in a
  scratch clone at the commits the case depends on, and asks the product what the case stands on: `gov close --select`
  answers and refuses as planted, `gov accept` fails or errors the planted folders with no failed test, `gov rebuild
  --integration` builds the planted store (or cannot), `gov check --structural` is ok, notices or exits 2 as planted.
  A broken fixture fails as `fixture: ...`, never as a red.
- **What the planted projects tell:** each planted test tells every run of it (W2-115b's telling tests); in the
  `--full` projects a `tests/conftest.py` tells every pytest the run starts (its command line) and the xdist pool each
  test ran in (`PYTEST_XDIST_WORKER_COUNT`); the planted schema check tells the tree it ran in and where `main` stood
  at the planted root at that moment.
- **Each planted run is built once per session** (`conftest._shared`, a file lock in pytest's shared base folder).
- **No network, no model; deterministic; no wall-clock bound.** The store's endpoints are loopback stand-ins.
- Run: `TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-206 -q -p no:cacheprovider
  -n auto`, or `gov accept W2-206`. Ten planted projects, 19 `gov queue` calls (3 of them `--select`, 3 `--dry-run`, 4 `--full`).

## The planted runs

| run | project and branches | commands |
|---|---|---|
| dry | A changes the widget (green); B breaks the gadget (its own suite and a unit test fail); C adds `tools/extra.txt`, which nothing maps to a suite | `--select A`; `--select A B`; `--select C`; `A --dry-run --out <folder outside the project>`; `A B --dry-run`; `PROJ-zzzz --dry-run` (no such ticket); then `A` itself. `gov wait <out>/verify.exit` after each of the two dry runs |
| full_red | A changes the widget; `tests/unit/test_far.py` imports the gizmo and reads the widget's file: outside A's selection, green on the base, red with the change | `A --full`; then `A` |
| full_green | A changes the helper (the unrelated test stays green); the path map names `close_workers: 12`; the queue's environment holds `GOV_HEAVY_CPUS=0-1` and `PYTEST_XDIST_AUTO_NUM_WORKERS=2` | `A --full` |
| full_plain | A changes the helper; outside its selection `test_known_far.py` (red on the base, a bare assert) and `test_once.py` (red the first time it runs, green after); no workers in the path map, neither variable in the environment | `A --full` |
| full_timeout | A changes the helper; outside its selection `test_slow.py` never ends inside the limit (the test map's per-test limit is 120 s) | `A --full --timeout 30` |
| after_store | `rebuild.yaml` names an integration store (a link outside the project), built at the base by `gov rebuild --integration main`; A changes the widget | `A`; then `gov retrieve --root <link>` |
| after_plain | `rebuild.yaml` names no store; a declared schema check (`governance/kernel/checks/core-schema.yaml`) notices a changed widget and tells; A changes the widget | `A`; then `gov check --structural <old head>` in a scratch clone at the landed head |
| after_failing | `rebuild.yaml` names a store whose place is a plain file (no link: it cannot be built); the `git` first on the queue's `PATH` fails the structural pass's first question, so the pass exits 2; B breaks the gadget, A changes the widget | `B` (a culprit only); then `A` |
| unnamed | P's acceptance folder holds its README alone on the base, mapping `failure-1` to a test that does not exist; P's branch brings the folder's one (green) test and its module's change; B changes the gadget (clean) | `P B`; then `P` |
| unnamed_crash | as unnamed, with Q, whose test file crashes at collection | `Q B` |

## KPI map

The ticket's lines are numbered in the order of the ticket file; the line each one is stands beside it.

| KPI id | line | tests | expected red reason |
|---|---|---|---|
| success-1 | A6 S1 | `test_w2_206_dry_run.py::test_a_dry_run_of_a_green_ticket_answers_and_exits_as_its_landing_does`, `test_w2_206_dry_run.py::test_a_dry_run_runs_the_acceptance_folder_and_the_selection_on_the_merged_result`, `test_w2_206_dry_run.py::test_a_dry_run_moves_no_branch_and_writes_no_close_commit_and_no_close_record`, `test_w2_206_dry_run.py::test_the_dry_run_writes_its_five_files_under_out_with_verify_exit_last`, `test_w2_206_dry_run.py::test_gov_wait_on_verify_exit_returns_the_dry_run_s_exit_code`, `test_w2_206_dry_run.py::test_a_planted_culprit_gives_exit_3_in_the_answer_and_in_verify_exit`, `test_w2_206_dry_run.py::test_a_dry_run_refused_as_a_whole_exits_1_as_the_landing_would` | the base's queue has no `--dry-run`: `gov: error: unrecognized arguments: --dry-run`, exit 2 ("no JSON envelope on stdout") |
| success-2 | A6 S2 | `test_w2_206_select.py::test_select_prints_one_ticket_s_selection_as_gov_close_select_does_on_the_same_tree`, `test_w2_206_select.py::test_select_of_two_tickets_prints_the_union_of_their_selections`, `test_w2_206_select.py::test_select_runs_no_test_and_leaves_the_integration_branch_where_it_was`, `test_w2_206_select.py::test_a_ticket_changing_a_path_the_test_map_does_not_map_is_selection_refused_on_stderr_with_exit_2` | the base's queue has no `--select`: exit 2 with nothing on stdout ("gov queue --select exited 2, not 0"; for the refusal "stderr does not name SELECTION_REFUSED") |
| success-3 | A6 S3 | `test_w2_206_full.py::test_with_full_a_candidate_that_breaks_a_test_outside_its_selection_is_a_culprit_and_nothing_lands`, `test_w2_206_full.py::test_without_full_the_same_candidate_lands_and_the_unrelated_test_is_not_run`, `test_w2_206_full.py::test_with_the_unrelated_test_green_full_lands_and_the_close_record_s_selection_says_full`, `test_w2_206_full.py::test_the_full_run_runs_the_whole_tests_folder_of_the_tested_merge`, `test_w2_206_full.py::test_queue_json_holds_the_full_run_its_runs_its_workers_and_its_cpus`, `test_w2_206_full.py::test_full_writes_no_nightly_record_into_the_project_tree`, `test_w2_206_full.py::test_a_red_outside_the_selection_that_is_red_at_the_base_is_a_known_base_red_and_full_lands`, `test_w2_206_full.py::test_a_red_of_the_full_run_that_is_green_alone_is_flaky_named_and_not_blocking` | the base's queue has no `--full`: `unrecognized arguments: --full`, exit 2 ("no JSON envelope on stdout") |
| success-4 | A6 S4 | `test_w2_206_full.py::test_with_cpus_0_1_auto_workers_2_and_a_path_map_naming_12_the_full_run_s_pool_is_2`, `test_w2_206_full.py::test_with_the_planted_settings_queue_json_names_workers_2`, `test_w2_206_full.py::test_no_command_the_full_run_starts_asks_for_auto_or_for_more_than_the_cap`, `test_w2_206_full.py::test_with_neither_variable_the_pool_is_one_slot_s_workers_not_the_machine_s_cpu_count` | as success-3: "the run started no pytest in the planted project", or no envelope |
| success-5 | A8 S1 | `test_w2_206_after.py::test_after_the_move_queue_json_holds_the_store_s_rebuild_at_the_landed_head`, `test_w2_206_after.py::test_gov_retrieve_s_store_line_names_the_new_head_and_no_stale_store`, `test_w2_206_after.py::test_a_project_whose_rebuild_yaml_names_no_store_is_not_configured_and_no_rebuild_is_run` | the base lands and runs no after-step: "queue.json holds no after-step"; the store line still names the old head |
| success-6 | A8 S2 | `test_w2_206_after.py::test_queue_json_holds_the_structural_pass_s_exit_code_and_its_lines`, `test_w2_206_after.py::test_the_structural_pass_ran_once_after_the_move_with_the_landing_s_base` | "queue.json holds no after-step"; "the planted check ran 0 time(s) in the landing, not once" |
| success-7 | W2-202 fix 1 | `test_w2_206_fixes.py::test_accept_takes_keep_report_and_its_default_is_none`, `test_w2_206_fixes.py::test_accept_with_keep_report_leaves_the_junit_report_at_the_path_and_answers_as_without_it`, `test_w2_206_fixes.py::test_the_queue_s_acceptance_run_replaces_nothing_in_the_runner_before_during_or_after` | the base's `accept` takes no `keep_report` (`TypeError: unexpected keyword argument`), and `gov.queue.acceptance` stands in for `runner.read_cases` while its run runs ("replaced a name of gov.accept.runner while its run ran") |
| failure-1 | A6 F1 | `test_w2_206_dry_run.py::test_a_dry_run_leaves_the_root_clean_and_creates_no_branch_no_ref_and_no_commit`, `test_w2_206_dry_run.py::test_a_dry_run_leaves_the_warm_clone_at_the_base`, `test_w2_206_select.py::test_select_leaves_the_root_clean_and_creates_no_ref_no_commit_and_no_record` | as success-1 and success-2 (each first reads the command's answer, so none is green by nothing having run) |
| failure-2 | A6 F2 | `test_w2_206_full.py::test_a_full_run_that_reaches_its_time_limit_is_run_incomplete_with_exit_3`, `test_w2_206_full.py::test_the_full_run_that_did_not_complete_lands_nothing` | as success-3: exit 2 and no envelope, not `RUN_INCOMPLETE` with exit 3 |
| failure-3 | A8 F1 | `test_w2_206_after.py::test_a_store_that_cannot_be_built_is_a_notice_and_the_landing_stands`, `test_w2_206_after.py::test_a_structural_pass_that_exits_2_is_a_notice_and_the_landing_stands`, `test_w2_206_after.py::test_a_landing_that_landed_nothing_runs_neither_after_step` | "queue.json holds no after-step" (the third first reads the landed run's after-step) |
| failure-4 | W2-202 fix 2 | `test_w2_206_fixes.py::test_a_ticket_whose_readme_maps_a_line_to_a_test_that_does_not_exist_is_the_batch_s_culprit`, `test_w2_206_fixes.py::test_the_batch_s_other_ticket_lands_and_closes`, `test_w2_206_fixes.py::test_the_same_ticket_alone_is_a_culprit_with_exit_3_and_nothing_lands`, `test_w2_206_fixes.py::test_a_ticket_whose_acceptance_folder_crashes_at_collection_is_the_batch_s_culprit` | the base refuses the batch `BATCH_UNEXPLAINED` (it names the clean ticket the culprit, then finds the rest not green) and the ticket alone `BATCH_UNEXPLAINED` ("the queue's answer is not ok"); the crash case is a guard, green on the base |

The ticket file's `failure` list holds four lines (the test designer's brief counted five): failure-1 A6 F1,
failure-2 A6 F2, failure-3 A8 F1, failure-4 W2-202 fix 2.

Every case is an acceptance test. One case is green on the base by design, a guard under failure-4: a suite that
crashes at collection is already the batch's culprit on the base (its folder cannot run without its branch, and is
red again with its branch alone); the line's other planted form, the mapped test that does not exist, is the red one.

## Readings this suite takes

1. **A dry run's answer** (success-1) is the landing's envelope (`ok: true`, `command: queue`) with the landing's exit
   code. It is read against the landing of the same ticket made afterwards in the same project: `candidates`,
   `culprits`, `refused`, `reds`, `base_reds`, `flaky` and `selection` are equal; the dry run's `head` is null and its
   `closes` empty. What key names the tickets a dry run would land is not fixed here.
2. **"The five files"** are `select.json`, `summary.txt`, `verify.exit` and the run files: at least two JUnit files
   (`*.xml`, as `gov close --verify`'s `parallel.xml` and `serial.xml`; their names are not fixed) which hold the
   selection's run. `verify.exit` holds the exit code and a newline, no `*.tmp` is left, and no file under `--out` is
   newer than it. `select.json` is one JSON object whose `suites` name the selection; `summary.txt` is not empty.
3. **The default `--out`** is read for two tickets: `.gov-runtime/queue/dry/PROJ-aaaa+PROJ-bbbb/`.
4. **A dry run refused as a whole** (no such ticket) answers `TICKET_UNKNOWN` with exit 1 and moves nothing. Whether
   `verify.exit` is written for it is not asserted (the line does not say; proposed decision 1).
5. **"No close record in the warm clone's tested commit":** no commit any ref of the warm clone names holds a path
   under `docs/close/`, and the commit the answer names as `tested`, where the root or the clone holds it, has no
   `docs/close/<T>/`.
6. **`--select`** (success-2) is run without `--json` and prints exactly one JSON object. For one ticket its `ticket`,
   `suites` and `pytest_options` equal `gov close --select <T>`'s in a scratch clone at the branch tip (the tree the
   landing would test), and `tickets` is `[<T>]`. For two tickets there is no `ticket`, `tickets` holds both in the
   order given, and `suites` is the union of the two `gov close --select` answers, each named once. The line says "as
   the run would have chosen" and "equals `gov close --select`'s": the run leaves each ticket's own acceptance folder
   to the acceptance runner, `gov close --select` names it; the Verify is followed (proposed decision 2).
7. **Failure-1** compares, around each command: `git status --porcelain` (empty after), `git for-each-ref` (so no
   `refs/gov-queue/land` and no `refs/gov-close/land` either), what `HEAD` is, `git log --all`, every tracked file
   and every file under `.tickets/` and `docs/`; after a dry run the warm clone's `HEAD` is the base and its status
   empty. `--select` need not make a clone; where it does, the clone is at the base.
8. **"Outside every ticket's selection"** (success-3): the unrelated test imports only the gizmo, which no case
   changes, and reads the widget's file; the landing without `--full` lands and does not run it (asserted).
9. **"The close record's `selection` says `full`":** `selection` is the word `full`, or a mapping one of whose values
   is the word `full`, or whose `full` is true. A landing without `--full` does not say it.
10. **"The whole `tests/` runs":** every planted unit test, the one no selection reaches among them, told a green run
    on the merged tree. Whether the ticket's own acceptance folder runs a second time inside the full run is not
    asserted (W2-202's A3 F1 says no test runs twice in a landing; this line says the whole `tests/`; proposed
    decision 3).
11. **`queue.json`'s `full`** holds `runs` (a list of the full run's runs, each a mapping), `workers` and `cpus`;
    the form of a run and of `cpus` is not fixed here.
12. **The pool** (success-4) is read where the full run alone reaches: the pool size the unrelated gizmo test saw in
    each of its runs, and the `-n` values on the command lines of the pytest processes the run started in the planted
    project (xdist's own workers aside). With the planted settings the pool is 2, a command asks for `-n 2` and
    `full.workers` is 2. With neither variable and no number in the path map, the pool and `full.workers` are one
    slot's workers as the product sizes them in the queue's own environment: `gov.dispatch.admission.sized()`'s
    `workers_per_slot`, or `gov.dispatch.limits.workers_for` for `gov.resources.slots.slot_count` (the two agree on a
    machine with no configuration; either is accepted), and not the machine's CPU count where that differs. No
    command asks for `auto` or for more than the cap. The Verify's second case does not say whether the path map
    still names 12 workers; it is planted with none, the case the line's own rule makes unambiguous (proposed
    decision 4).
13. **`RUN_INCOMPLETE`** (failure-2) is the queue's refusal as built: `ok: false`, the code in the envelope and on
    stderr, exit 3; every branch, the tracked files and the ticket as before, no close record.
14. **`after.rebuild`** (success-5) is a mapping with `ok: true` and `head`, the landed head; the store line is the
    first `store: ` line `gov retrieve --root <link> "<question>"` prints: it starts `store: <landed head, 12
    digits>` and names no other head and no stale count. With no store named, `after.rebuild` is the word
    `not_configured` (or a mapping holding that word) and the root holds no `.gov-runtime/store.db`.
15. **`after.structural`** (success-6) holds `exit` (0 for a pass that ran), `ok` (a boolean; its value for a pass
    that ran and gave a notice is not asserted) and `lines`: the pass's own lines, equal, the seconds aside, to those
    of `gov check --structural <old head>` in a scratch clone at the landed head, the planted `schema: NOTICE` among
    them. "The landing adds a file the pass notices" is planted as the landing's change to the widget, which the
    declared check reads. "Once, after the move": the planted check told one run, in a tree whose head is the landed
    head, while `main` at the planted root stood at the landed head. "With the landing's base": the lines equal those
    of the pass given the old head, `portability: skipped (no such change)` among them (with no base it reads `no base
    given`).
16. **Failure-3** plants both failures in one landing: exit 0, the ticket closed, `main` at its close commit,
    `after.rebuild` and `after.structural` each `ok: false` with a `reason`, `after.structural.exit` 2. The culprit-only
    run of the same project (exit 3, nothing landed) has no `after` in its `queue.json`.
17. **Fix 1** (success-7): `accept`'s `keep_report` defaults to None; with a path, a JUnit file naming the folder's
    one test is there and the answer and exit code equal those without it. "Replaces nothing": every name of
    `gov.accept.runner` is the same object before `gov.queue.acceptance.run(clone, ticket, folder, timeout, junit)`
    (its signature on the base), at every call of a function of the runner's module while it runs (a profile probe in
    the test's process), and after; the run still keeps its JUnit file at `junit` and passes.
18. **Fix 2** (failure-4): the batch answers `ok: true`, exit 3, `culprits` the ticket whose acceptance run failed
    unnamed, `landed` the other, which is closed through its own close commit; neither stdout nor stderr names
    `BATCH_UNEXPLAINED`. Alone, the ticket is the culprit with exit 3 and nothing moves. "A test failing by name is
    still attributed by the batch's own search" is kept by W2-115b's and W2-202's cases, and here by the dry run's
    culprit (B's own suite fails by name).

## For the engineer

- `gov queue --select` is called without `--json`; `--dry-run` and `--full` with it.
- A dry run must leave no ref at the root: the batch's own `refs/gov-close/land` counts.
- The `--full` projects hold a `tests/conftest.py`; the queue's environment for full_green holds only the two
  variables named above beside the kit's clean environment (no `GOV_HEAVY_ADMITTED`, no machine configuration).
- The planted structural check is run with the pass's own environment; it tells unless `W2_115B_SELF_CHECK` is set.

## Not tested here

- A2, A7 and every B item (the ticket's non-goals).
- "The existing W2-202 and `tests/unit/accept` cases stay green" (success-7's last clause): the lead's green run.
- A `--full` run that cannot complete by a crash or a missing runner (failure-2 names the time limit in its Verify).
- A time limit as the unnamed failure of an acceptance run (failure-4's Verify names the two forms planted).
