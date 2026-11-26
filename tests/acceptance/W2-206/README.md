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

## Fix: one selection for many branches, SEL-4 (plan item 1-0)

Written by the independent test designer from the ticket's section "Fix: one selection for many branches, SEL-4", before
any implementation, in `test_w2_206_sel4.py`. The line is numbered after the ticket's own (success-8; failure-5, the line's
refusal half; the ids are labels of this table). Public interface: `python3 -m gov.cli.main queue <T>=<branch> ... --select
--root <project>` (without `--json`): one JSON object on stdout, or the refusal on stderr; the planted repository's state and
the planted tests' run logs. Each planted project is built once per session (a file lock in pytest's shared folder); the
fixture checks that every branch forks at the green head and that the conflicting pair really conflicts (`fixture: ...`).

**What is planted:** a green nightly record naming the first commit, then direct commits of the base that no branch has (a
moved `src/app/gizmo.py`, which `tests/unit/test_gizmo.py` imports; `repin.sh`; a document outside `record_only`); branches
forked at the green head:

| project | branches | commands |
|---|---|---|
| pair | A changes the widget (`topic/aa`), B the gadget (`topic/bb`) | `A=topic/aa B=topic/bb --select`; each alone |
| conflict | A and B each rewrite the widget differently | `A=topic/aa B=topic/bb --select` |
| same | A, closed, with two fix branches (the widget; the helper), each commit with `Task:`, `Role:` and `Fix:` | `A=fix/one A=fix/two --select`; each alone |
| merge | A's branch `topic/merged` merges two branches (the widget; the helper) | `A=topic/merged --select`; each part alone |

| KPI id | tests | expected red reason |
|---|---|---|
| success-8 (SEL-4: one object, one union, the same ticket twice, a merge) | `test_w2_206_sel4.py::test_sel4_two_branches_print_one_object_naming_both_tickets`, `test_w2_206_sel4.py::test_sel4_suites_are_the_union_of_each_branch_s_own_selection_and_none_of_the_base_s`, `test_w2_206_sel4.py::test_sel4_the_same_ticket_given_twice_with_two_branches_is_accepted_and_gives_one_list`, `test_w2_206_sel4.py::test_sel4_a_branch_that_is_the_merge_of_several_gives_one_list` | `tests/unit/test_gizmo.py`, which only the base's commit reaches, is among the suites (each branch counts the base's range): the first case is a guard, green on the base (one object naming both tickets exists); the same ticket twice is accepted on the base too, its case is red for the gizmo alone |
| failure-5 (SEL-4: branches that do not merge together are refused as a whole, nothing run) | `test_w2_206_sel4.py::test_sel4_a_pair_that_conflicts_is_refused_as_a_whole`, `test_w2_206_sel4.py::test_sel4_the_refused_pair_runs_nothing_and_moves_nothing` | none: guards, green on the base (the refusal exists); they must stay green |

**Readings this fix's cases take.**

1. **"The union, never the sum of two ranges"** is the explicit list the planted branches reach (each ticket's own suite and
   the importers of the module it changes) and equal to the union of each branch's `--select` alone; the base's gizmo suite
   is in neither.
2. **The same ticket twice** (`A=fix/one A=fix/two`, a closed ticket landed as fixes) is accepted by the current code, so the
   case pins it: exit 0, one object, `tickets` holding A (once or twice is not fixed), `suites` the union of each branch alone.
3. **A branch that is the merge of several** is one branch whose change is its diff from the merge base to its tip; its
   `suites` equal the union of its parts' alone.
4. **A refused pair** exits non-zero with `CANDIDATE_NOT_ISOLATED` on stderr and no object on stdout; every ref, `HEAD`, the
   status and the tracked files are as before, and no planted test ran (the exit code is not fixed here).

## Fix: the landing proves the path map's coverage, PM-1 to PM-3 (plan item 1-11 (c))

Written by the independent test designer from the ticket's section "Fix: the landing proves the path map holds every path a
change adds exactly once", before any implementation, in `test_w2_206_pathmap.py`. The lines are numbered after SEL-4's
(failure-6: PM-1's refusals; success-9: what PM-1 lets through; success-10: PM-2; success-11: PM-3; the ids are labels of
this table). Public interface: `python3 -m gov.cli.main queue <T>=<branch> ... [--select | --dry-run [--out <dir>]]
[--full] --root <project>`; the answer, stderr and exit code, `queue.json`, a dry run's `select.json`, the close record,
the planted repository's git state.

**What is planted:** W2-115b's kit with a narrow path map (the kit's own maps `**`): `src`, `tests`, tickets, close
records, checkpoints, `governance`, `README.md` and `.gitignore` are mapped; of `docs/` only `docs/mapped/**` and the one
file `docs/mixed/placed.md` (namespace `reference-docs`); `shared-notes` holds `docs/mapped/shared-*` too. Each build
first asks `python3 -m gov.check.pathmap`, in a scratch clone at each planted tip, for exactly the findings it plants
(`fixture: ...` otherwise). An "invalid" map is a namespace without `paths`: the path map check refuses it, the
configuration loader every command runs reads it.

| run | project and branches | commands |
|---|---|---|
| main | A adds two files under `docs/newfolder/` (`topic/aa`), B a document under `docs/mapped/` (`topic/bb`), C a file under `docs/elsewhere/` (`topic/cc`); further branches of A: a root file; a file beside `docs/mixed/placed.md`; a file both namespaces hold; a rename into `docs/moved/`; the new folder with its line added to the map; the map deleted; the map made invalid | `--select` of each, and of `A B`; `A B --dry-run --out <dir>`; `C --full`; `A B` |
| debt | the base holds `legacy/old.md` (in none) and `docs/mapped/shared-old.md` (in two); A changes both and the widget; B adds `legacy/new.md` | `--select B`; `A` |
| unusable | the base's map is invalid; branches adding a path, changing the map, changing code only | `--select` of each |
| no_project | no `governance/project/` at all | `A --dry-run --full --out <dir>` |

| KPI id | line | tests | expected red reason |
|---|---|---|---|
| failure-6 | PM-1, refused | `test_w2_206_pathmap.py::test_pm1_select_refuses_an_added_path_under_no_namespace_naming_it_and_the_folder_s_line`, `test_w2_206_pathmap.py::test_pm1_a_root_file_s_line_to_add_is_the_path_itself`, `test_w2_206_pathmap.py::test_pm1_in_a_folder_holding_placed_files_the_line_to_add_is_the_path_itself`, `test_w2_206_pathmap.py::test_pm1_an_added_path_two_namespaces_hold_is_refused_naming_both_and_their_patterns`, `test_w2_206_pathmap.py::test_pm1_a_rename_into_an_unmapped_folder_is_refused`, `test_w2_206_pathmap.py::test_pm1_select_of_two_branches_names_the_ticket_that_adds_the_path_and_moves_and_runs_nothing`, `test_w2_206_pathmap.py::test_pm1_the_landing_lists_the_candidate_under_refused_with_its_code_paths_and_the_line`, `test_w2_206_pathmap.py::test_pm1_the_batch_s_clean_candidate_lands_and_the_refused_one_stays_out`, `test_w2_206_pathmap.py::test_pm1_a_dry_run_refuses_it_too_and_moves_nothing`, `test_w2_206_pathmap.py::test_pm1_with_full_the_candidate_is_refused_and_nothing_lands`, `test_w2_206_pathmap.py::test_pm1_a_branch_that_deletes_the_path_map_is_refused_path_map_missing`, `test_w2_206_pathmap.py::test_pm1_a_branch_that_makes_the_path_map_invalid_is_refused_path_map_invalid`, `test_w2_206_pathmap.py::test_pm1_under_a_map_already_unusable_a_branch_that_adds_a_path_or_changes_the_map_is_refused`, `test_w2_206_pathmap.py::test_pm1_an_added_unmapped_path_is_refused_without_naming_the_paths_already_in_none_or_two` | the base asks the path map nothing: `--select` exits 0 and prints the object ("exit 0, not 2"); the landing, the dry run and `--full` land the candidate ("exit 0, not 3") |
| success-9 | PM-1, what it lets through | `test_w2_206_pathmap.py::test_pm1_a_branch_that_adds_the_line_with_its_path_is_selected`, `test_w2_206_pathmap.py::test_pm1_changing_paths_already_in_none_or_two_refuses_nothing_and_lands`, `test_w2_206_pathmap.py::test_pm1_under_a_map_already_unusable_a_branch_that_only_changes_code_is_not_refused`, `test_w2_206_pathmap.py::test_pm1_the_batch_s_clean_candidate_lands_and_the_refused_one_stays_out` | the batch's clean-candidate case is red as above (both land, exit 0, not 3); the other three are guards, green on the base |
| success-10 | PM-2 | `test_w2_206_pathmap.py::test_pm2_select_of_a_record_inside_a_mapped_folder_exits_0_with_the_notice`, `test_w2_206_pathmap.py::test_pm2_the_landing_lands_the_record_inside_a_mapped_folder_with_the_notice` | none: guards, green on the base (`RECORD_PLACED` exists, DEC-1239 (2)); they must stay green |
| success-11 | PM-3 | `test_w2_206_pathmap.py::test_pm3_the_select_object_holds_the_counts_of_the_merged_tree`, `test_w2_206_pathmap.py::test_pm3_the_landing_s_answer_and_queue_json_hold_the_counts_of_the_tested_merge`, `test_w2_206_pathmap.py::test_pm3_the_close_record_holds_the_counts`, `test_w2_206_pathmap.py::test_pm3_a_dry_run_s_answer_and_select_json_hold_the_counts`, `test_w2_206_pathmap.py::test_pm3_a_project_with_a_path_already_in_none_and_one_in_two_lands_and_counts_them`, `test_w2_206_pathmap.py::test_pm3_a_project_with_no_project_folder_has_no_path_map` | no `path_map` anywhere ("path_map None"); the dry run's case fails first on "exit 0, not 3"; the project with no `governance/project/` is a guard, green on the base |

**Readings this fix's cases take.**

1. **The line to add** is asserted literally in the reason (`- "docs/newfolder/**"`; `- "STRAY.md"`;
   `- "docs/mixed/other.md"`, and then no `- "docs/mixed/**"`). The rest of the reason's words are free.
2. **`--select`'s refusal** is `<code>: <ticket>: <reason>` on stderr, exit 2, no object on stdout; the reason is read from
   there to the end of stderr.
3. **A refused entry** holds `ticket`, `code`, `paths` and `reason`; `paths` is asserted for the path codes, not for the
   map's own codes (`PATH_MAP_MISSING`, `PATH_MAP_INVALID`), whose `paths` the line does not state.
4. **The counts** are those of the tested merge, which holds no refused candidate's paths: in the batch with one refused
   candidate it says `0 in none, 0 in two` with the tested commit's `git ls-tree -r` number. `--select`'s are the branch
   tip's (one branch forked at the head: the merged tree). Whether an answer of a landing that lands nothing holds
   `path_map`, and its words under an unusable map, are not asserted.

**Not tested here:** `PATH_MAP_UNREADABLE`; a candidate whose paths are some in none and some in two (which code is not
stated); `--full`'s own answer for a candidate that lands (its counts); a branch already merged.

## Fix: the impact trace at the landing, IT-1 and IT-2 (plan item 1-9; T-11 (a), DEC-1242; DEC-1244 X-1)

Written by the independent test designer from the ticket's section "Fix: the impact trace at the landing, IT-1 and IT-2",
before any implementation, in `test_w2_206_impact.py` (support: `w2_206_impact_support.py`). The lines are numbered after
PM's (success-12: IT-1's trace; success-13: IT-2; failure-7: a trace that fails or overruns never refuses; the ids are
labels of this table). Public interface: `python3 -m gov.cli.main queue <T>=<branch> ... [--select | --dry-run --out
<dir>] --root <project>`, `GOV_QUEUE_IMPACT_TIMEOUT`; the answer, `queue.json`, `select.json`, the close records, the
planted repository's git state. **The oracle** for a record's `tickets`, `tests` and `complete` is `gov impact <id>
--json` on a scratch clone at the landed head whose record store is loaded from that head (`gov.store.loader.load`).

**What is planted:** W2-115b's kit with `decision_register: docs/DECISIONS.md` in the path map; on the base a register of
DEC-001, DEC-003 and DEC-002, specifications SPEC-001 and SPEC-003, ticket records PROJ-rec1 to rec3 and test records
TR-0001 and TR-0002 linking them. A's branch changes DEC-001, removes DEC-003 and adds DEC-004 (DEC-002 unchanged),
changes SPEC-001 and PROJ-rec3, adds SPEC-002, deletes SPEC-003, changes a Markdown file with no frontmatter, one with
frontmatter and no `id`, and the widget; B changes the gadget alone. Each build checks itself (`fixture: ...`): the
planted tests by plain pytest; `gov impact` on a scratch merge names a ticket and a test for every present record, refuses
the removed ones, and says the same on the landed head.

| run | project and branches | commands |
|---|---|---|
| main | A (`topic/aa`), B (`topic/bb`) | `A B --select`; `A B --dry-run --out <dir>`; `A B` |
| fix | A closed, no close record; a `Fix:` branch changing SPEC-001 and the widget | `A` |
| no_register | the path map names `docs/NO_SUCH_REGISTER.md`; A changes SPEC-001 | `A B --select`; `A B` |
| limit | as main's register; `GOV_QUEUE_IMPACT_TIMEOUT=0.001` | `A B --select`; `A B` |

| KPI id | line | tests | expected red reason |
|---|---|---|---|
| success-12 | IT-1 | `test_w2_206_impact.py::test_it1_the_answer_and_queue_json_hold_one_entry_for_each_landed_ticket`, `test_w2_206_impact.py::test_it1_each_ticket_s_first_close_record_holds_its_entry`, `test_w2_206_impact.py::test_it1_the_records_listed_are_the_change_s_record_files_and_register_entries_and_nothing_else`, `test_w2_206_impact.py::test_it1_each_record_names_the_tickets_tests_and_completeness_gov_impact_names_on_the_landed_tree`, `test_w2_206_impact.py::test_it1_a_removed_record_and_a_removed_register_entry_are_unavailable_and_not_complete`, `test_w2_206_impact.py::test_it1_the_entry_is_complete_only_where_every_record_is_and_a_change_with_no_record_is_empty`, `test_w2_206_impact.py::test_it1_one_close_commit_per_ticket_holds_the_trace_and_nothing_follows_it`, `test_w2_206_impact.py::test_it1_a_fix_landing_holds_the_trace_in_its_answer_and_queue_json_only` | the landing traces nothing: "the answer holds no impact mapping: impact None" |
| success-13 | IT-2 | `test_w2_206_impact.py::test_it2_select_prints_the_impact_the_landing_then_records`, `test_w2_206_impact.py::test_it2_select_with_the_trace_moves_nothing_and_runs_no_test`, `test_w2_206_impact.py::test_it2_a_dry_run_s_answer_and_select_json_hold_the_same_impact` | no `impact` in `--select`'s object or the dry run's answer ("holds no impact mapping") |
| failure-7 | IT-1, IT-2: a trace that fails or overruns | `test_w2_206_impact.py::test_it1_a_trace_that_fails_or_overruns_lands_with_exit_0_and_says_unavailable`, `test_w2_206_impact.py::test_it2_select_with_a_trace_that_fails_or_overruns_prints_the_string_and_exits_0` | as above (2 cases each: `no_register`, `limit`): exit 0 and the landing stand on the base, but there is no `impact` |

**Readings this fix's cases take.**

1. **Orders** of `records`, `tickets` and `tests` are not fixed. An entry's keys are exactly `records` and `complete`; a
   traced record's exactly `id`, `path`, `tickets`, `tests`, `complete`; an untraced one's exactly `id`, `path`,
   `unavailable`, `complete`. `unavailable (...)` needs a reason between the brackets.
2. **A record's `path`** is its file, or the register for an entry (a removed one too).
3. **`complete`** is `gov impact`'s own word. On a tree with no code index it says false for every record (the code graph
   is not loaded), so only a change with no record is complete here.
4. **A fix landing's** close record keeps exactly X6's keys for a ticket with no record before (no `impact`).
5. **IT-2's equality** is read between `--select` and the close records of the landing made right after, and between the
   dry run and that landing.

**Not tested here:** the default limit of 120 s; that the code graph is never loaded (no public interface shows it without
a code index; a source file not listed is tested); a renamed record file; `--full`'s `impact` (its close record is read
by W2-115b's IT-3 cases only for `evidence`).
