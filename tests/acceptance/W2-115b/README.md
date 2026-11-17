# W2-115b acceptance tests: gov queue, the product's deterministic landing (DAEO-j9z6)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines (9 success, 2 failure, rewritten
2026-11-17; success 9 added at dda23bd2e) and the ticket lead's interface naming (command, settings, answer keys, error and exit codes, close record,
what a planted project needs), never from the implementation. EMERGENCY-2 §4.3 step 3.

## How the suite runs

- **Public interfaces only:** `python3 -m gov.cli.main queue <ticket>[=<branch>] ... [--onto <branch>] --root
  <project> --json` with this worktree's `src/` on `PYTHONPATH`; its envelope, stderr and exit code; the git state of
  the planted repository (refs, parents, trailers, the paths each commit changes, files at a revision); the files the
  queue writes (the close record `docs/close/<id>/CL-<id>.md`, the queue's record
  `.gov-runtime/queue/<stamp>/queue.json`, the run's JUnit files under `.gov-runtime/`).
- **Planted projects under pytest's temp folders** (`w2_115b_support.Planted`): a git repository each with a package
  `app` under `src/` (`widget`, `helper`, `gadget`, `gizmo`, one module per extra ticket), tickets in `.tickets/`
  (`status: open`, `wbs_id`, `allowed_paths`, `acceptance_tests.path`), an acceptance suite per ticket that imports
  and guards the ticket's modules, three unit tests (`tests/unit/test_uses_widget.py`, `test_uses_helper.py`,
  `test_gizmo.py`), the test map `governance/project/test-map.yaml` (valid against the kernel's schema), a path map,
  `.gitignore` holding `.gov-runtime/`, and **the kernel's ticket tool copied to `governance/kernel/bin/tk`** (committed;
  `PATH` is not changed). Work branches hold commits with `Task:` and `Role:` trailers. A machine-like git identity is
  set in the sandbox home's `.gitconfig` and in the planted repository's own config.
- **Telling tests:** every planted test appends a JSON line per run to its own file outside the project (the tree it
  ran in, what it saw of the modules it watches, whether it passed). "Ran once", "ran again without the culprit" are
  read from these lines.
- **The fixtures check themselves:** before `gov queue` runs, each build runs the planted suites with plain pytest in a
  scratch clone at the base and at the branch tips it depends on (green where the case needs green, red where it needs
  red; the telling tests keep quiet there), validates the test map against the kernel's schema, and closes a ticket
  with the planted `tk close` in a scratch copy. A broken fixture fails with `fixture: ...`, never as a red.
- **Each planted run is built once per session** (`conftest._shared`), under a file lock in pytest's shared base
  folder, so xdist workers and modules read the same run; a build that fails is reported by every case that reads it.
- **No network, no model:** the embedding endpoint is a dead local address and its program a stand-in. Deterministic.
  No wall-clock bound is asserted; only the record's figures (success line 8).
- Run: `TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-115b -q -p no:cacheprovider
  -n 6`, or `gov accept W2-115b`. On the base it ends in about half a minute (every command is refused at once); with
  the queue built, about ten landings run, each a few seconds.

## The planted runs

| run | project and branches | command |
|---|---|---|
| green | `develop` checked out at the root, no `queue.yaml`; A's branch `topic/aa`: A's commit (the widget) and an honest slip without `Task:` (the helper) | `PROJ-aaaa=topic/aa` |
| red | `main`; A's branch breaks the widget | `PROJ-aaaa=topic/aa` |
| batch | `main`; A green (widget), B red (breaks the gadget its own suite guards); A's suite also watches the gadget | `PROJ-aaaa=topic/aa PROJ-bbbb=topic/bb` |
| authors | `main`; C (engineer commit to its suite under `tests/acceptance/`), D (the test designer's commit), E (the owner's commit), G (a clean merge of the designer's branch), H (a merge whose resolution edits the designer's new test), K (engineer commit to its `acceptance_tests.path`, `tests/checks/F-kk/`) | all six, each `=<branch>` |
| authors_alone | `main`; C alone | `PROJ-cccc=topic/cc` |
| notices | `main`; A: a commit inside its allowed paths (the widget), one outside (`governance/project/notes.yaml`) | `PROJ-aaaa=topic/aa` |
| feature | `main`; `queue.yaml`: `integration: main`, `work_branch: "feature/{wbs}"`; branch `feature/F-aa` | `PROJ-aaaa` |
| onto | `main` checked out; `queue.yaml`: `integration: main`, `work_branch: "work/{ticket}"`; branch `work/PROJ-aaaa`; a branch `release` | `PROJ-aaaa --onto release` |
| unexplained | `main`; `tests/unit/test_known_red.py` red on the base, importing the widget; A changes the widget | `PROJ-aaaa=topic/aa` |
| moved | `main` checked out; M's suite holds a test that commits once to the root (its path written in at plant time) while the run runs | `PROJ-mmmm=topic/mm` |
| refusals | a fresh project per case: a detached root with no `--onto` and no `queue.yaml`; no branch form, a named branch that names no commit, a `queue.yaml` form naming no branch | see the cases |

## KPI map

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 | `test_w2_115b_land.py::test_the_green_ticket_lands_and_exits_0`, `test_w2_115b_land.py::test_the_tested_merge_s_parents_are_the_old_head_and_the_branch_tip`, `test_w2_115b_land.py::test_the_head_reaches_the_tested_merge_through_one_close_commit_per_ticket`, `test_w2_115b_land.py::test_the_run_s_junit_holds_the_own_suite_and_the_importer_and_no_unreached_suite`, `test_w2_115b_land.py::test_the_branch_s_own_commit_without_a_task_trailer_counts_in_the_change`, `test_w2_115b_land.py::test_the_root_s_working_tree_follows_the_integration_branch` | `gov queue` is not a command on the base: argparse exits 2 with a usage line, "no JSON envelope on stdout" |
| success-2 | `test_w2_115b_land.py::test_the_close_record_holds_the_queue_s_keys`, `test_w2_115b_land.py::test_the_close_record_names_the_tested_merge_the_run_s_counts_and_the_queue_s_record`, `test_w2_115b_land.py::test_the_ticket_is_closed_at_the_new_head_in_the_same_landing`, `test_w2_115b_land.py::test_only_the_queue_s_run_ran_the_planted_tests` | as success-1 |
| success-3 | `test_w2_115b_red.py::test_a_red_ticket_is_not_landed_and_is_named_the_culprit_with_exit_3`, `test_w2_115b_red.py::test_the_answer_names_the_failing_test_s_node_id`, `test_w2_115b_red.py::test_the_integration_branch_the_work_branch_and_the_ticket_file_are_as_they_were` | as success-1 |
| success-4 | `test_w2_115b_batch.py::test_the_culprit_is_sent_back_named_with_its_failing_test`, `test_w2_115b_batch.py::test_the_culprit_s_branch_is_not_merged_and_its_ticket_stays_open`, `test_w2_115b_batch.py::test_the_other_lands_and_closes`, `test_w2_115b_batch.py::test_the_other_s_close_record_names_the_culprit_and_the_merge_without_it`, `test_w2_115b_batch.py::test_the_rest_was_run_again_without_the_culprit` | as success-1 |
| success-5 | `test_w2_115b_authors.py::test_an_engineer_commit_to_the_acceptance_tests_is_refused_with_its_id`, `test_w2_115b_authors.py::test_an_engineer_commit_to_the_ticket_s_acceptance_path_is_refused`, `test_w2_115b_authors.py::test_the_test_designer_s_and_the_owner_s_commits_land`, `test_w2_115b_authors.py::test_a_clean_merge_of_the_test_designer_s_branch_lands`, `test_w2_115b_authors.py::test_a_merge_that_edits_an_acceptance_test_in_its_resolution_is_refused`, `test_w2_115b_authors.py::test_the_rest_of_the_batch_lands_through_close_commits_with_exit_3`, `test_w2_115b_authors.py::test_a_ticket_refused_alone_is_named_and_nothing_moves` | as success-1 |
| success-6 | `test_w2_115b_notices.py::test_a_commit_outside_the_allowed_paths_is_a_notice_and_the_ticket_lands_and_closes`, `test_w2_115b_notices.py::test_the_close_record_lists_the_notice`, `test_w2_115b_notices.py::test_a_path_inside_the_allowed_paths_is_not_listed` | as success-1 |
| success-7 | `test_w2_115b_settings.py::test_the_queue_s_code_names_no_project`, `test_w2_115b_settings.py::test_queue_yaml_on_main_with_feature_branches_lands`, `test_w2_115b_settings.py::test_onto_and_the_ticket_form_land_on_the_named_branch`, `test_w2_115b_settings.py::test_a_detached_root_with_no_onto_and_no_queue_yaml_is_integration_unknown`, `test_w2_115b_settings.py::test_a_ticket_without_a_work_branch_is_branch_unknown` | as success-1; the grep case: "there is no src/gov/queue/" |
| success-8 | `test_w2_115b_land.py::test_the_queue_s_record_is_written_and_holds_the_answer`, `test_w2_115b_land.py::test_the_seconds_of_each_step_and_the_total` | as success-1 |
| success-9 | `test_w2_115b_dod.py::test_the_project_s_facts_hold_exactly_three_dod_lines`, `test_w2_115b_dod.py::test_the_facts_gov_adopt_writes_hold_exactly_three_dod_lines`, `test_w2_115b_dod.py::test_no_kernel_template_or_generated_copy_quotes_the_dropped_lines`, `test_w2_115b_dod.py::test_the_ticket_template_s_done_when_is_the_three_ids`, `test_w2_115b_dod.py::test_each_claude_templates_copy_is_its_kernel_template_with_three_lines` | the base's facts files (the project's and the one `gov adopt --facts` writes) hold DOD-1 to DOD-6; `role-lead.md` (kernel and `.claude/templates/` copy), `ticket.md` and the orchestrator agent files (`.claude/agents/`, both `.rulesync/subagents/`) quote DOD-4..6 or "DOD-1 to DOD-6"; `ticket.md`'s `done_when` lists six ids |
| failure-1 | `test_w2_115b_unmoved.py::test_a_red_run_does_not_move_the_integration_branch`, `test_w2_115b_unmoved.py::test_a_red_on_the_base_too_is_batch_unexplained_and_moves_nothing`, `test_w2_115b_unmoved.py::test_a_g1_refusal_moves_nothing`, `test_w2_115b_unmoved.py::test_a_head_moved_during_the_run_is_head_moved_and_stays_as_moved` | as success-1 |
| failure-2 | `test_w2_115b_land.py::test_green_closed_exactly_when_merged`, `test_w2_115b_red.py::test_red_closed_exactly_when_merged`, `test_w2_115b_batch.py::test_batch_closed_exactly_when_merged`, `test_w2_115b_authors.py::test_authors_closed_exactly_when_merged`, `test_w2_115b_authors.py::test_authors_alone_closed_exactly_when_merged`, `test_w2_115b_notices.py::test_notices_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_feature_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_onto_closed_exactly_when_merged`, `test_w2_115b_unmoved.py::test_unexplained_closed_exactly_when_merged`, `test_w2_115b_unmoved.py::test_moved_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_a_detached_root_with_no_onto_and_no_queue_yaml_is_integration_unknown`, `test_w2_115b_settings.py::test_a_ticket_without_a_work_branch_is_branch_unknown` | as success-1 (each first reads the queue's envelope, so none is green on the base by nothing having landed) |

Every case is an acceptance test but four of success 9's, which are **repository-state** cases (they read this
repository's own files: `facts.yaml`, the kernel templates and the generated copies) and belong to the record-reading
set; `test_w2_115b_dod.py::test_the_facts_gov_adopt_writes_hold_exactly_three_dod_lines` is an acceptance case on a
planted repository. No case is green on the base.

## Readings this suite takes

1. **The run's JUnit** (success-1) is every JUnit XML file the queue leaves under the project's `.gov-runtime/`, the warm
   clone's own tree (`.gov-runtime/close/clone/`) aside; a case is named by its `file` attribute (xunit1), else its
   class name. The telling tests' run logs corroborate it.
2. **"The change counted as the branch's own commits"** (success-1) is tested with an honest slip: a commit on the
   branch without a `Task:` trailer changes `src/app/helper.py`, which only `tests/unit/test_uses_helper.py` imports
   beside the ticket's own suite; that test must be in the run and in `selection.suites` (a folder holding it counts).
3. **A close commit** (success-1) is one commit on the one below it, the first on the tested merge, carrying exactly one
   `Task: <id>` trailer of a landed ticket (the interface's trailer), changing only `.tickets/<id>.md`,
   `docs/close/<id>/` and `docs/checkpoints/<id>/` and at least the ticket file and the close record; the answer's
   `closes` name the same commits, and its `head` is the last.
4. **"The run log shows only the queue's run"** (success-2): in the green landing each reached planted test ran
   exactly once, on the merged result; an unreached one never.
5. **"The same result as the answer"** (success-8): the queue record's JSON equals the answer's `result`, or its
   `result` member does. The record's place is exactly `.gov-runtime/queue/<stamp>/queue.json`, its path relative to
   the root in the answer's `record` and the close record's `queue`.
6. **"Status open" / "stays open"** is the planted `status: open`; "the ticket file unchanged" is byte for byte at the
   integration head and in the root's working tree.
7. **"Run again there"** (success-4): A's own suite watches the gadget (B breaks it) without guarding it; it must have
   a run that saw B's change (the batch's one run) and a passing run that did not (the rest's run). Its close
   record's `commit` is the merge of A alone onto the old head (parents: the old head, A's tip).
8. **G-1** (success-5): an offending commit is named by its full id in `refused[].commits`; "nothing of it landed" is
   its branch tip not under the head and its suite file at the head as on the old head. The two merges (G's, H's)
   carry the engineer's trailers (`Task:`, `Role: engineer`), so only the resolution decides. A run whose every
   candidate is refused answers `ok: true`, `landed: []`, exit 3 (the interface's exit table).
9. **"Changes nothing"** (success-7) is: every ref, what `HEAD` is, `git status --porcelain` and every tracked file's
   bytes as before, and no `docs/close/`; the ignored `.gov-runtime/` is not read.
10. **The grep** (success-7) is case-sensitive and literal, over every file under `src/gov/queue/` but `__pycache__/`;
    `integrate` also matches `integrated`, so the queue's code must not use that word.
11. **`HEAD_MOVED`** (failure-1) is planted as a test in M's suite that, the first time it runs, makes an empty commit on
    the branch checked out at the root (`main`, the integration branch); `main` must end at that commit, whose parent is
    the head the run merged onto.
12. **Failure-2's "branch's tip"** is the tip as planted (the queue never moves a work branch); a planted ticket with no
    work branch must not be closed.
13. **Success 9's places** are those the orchestrator's message names: the kernel templates
    (`template/governance/kernel/templates/`), `.claude/templates/`, `src/gov/_shipped/template/governance/kernel/templates/`,
    `template/.rulesync/subagents/`, `.rulesync/subagents/` and `.claude/agents/`, every file in each, read from this
    worktree's tree; a folder that is absent is not read (the kernel templates must exist). A dropped line is
    `DOD-4`, `DOD-5` or `DOD-6` (not followed by a digit) or the text `DOD-1 to DOD-6`. "Names the close" is a word
    beginning `close` (any case) in DOD-3's line; DOD-1 names `gov accept` or `{CMD:accept}`; DOD-2 names `gov queue`
    literally. The facts `gov adopt` writes are those `gov adopt --facts --root <planted repository> --json` writes in
    a fresh git repository with an empty `.tickets/`.
14. **Each `.claude/templates/` copy equals its kernel template** is checked together with that copy holding no
    dropped line, in one case: byte equality alone holds on the base already (the copies are regenerated today), so
    the case is red on the base through `role-lead.md`'s "DOD-1 to DOD-6" and guards that the copy is regenerated
    with the kernel template's new text.

## For the engineer

- The ticket tool is the kernel's `tk`, committed in each planted project at `governance/kernel/bin/tk`; nothing on
  `PATH` is changed.
- The planted runs need `pytest-timeout` in the interpreter (the test map's `per_test_timeout: 120`, which
  `select.scoped`'s options pass as `--timeout`), as the close's runs do.
- The planted package is `app` (under `src/`), not `gov`; `gov` comes from this worktree's `src/` on `PYTHONPATH`.
- No `GOV_ROLE` is set in the queue's environment; the close commits' `Role:` is not asserted.
- The sandbox home's `.gitconfig` and the planted repository's config carry a git identity, as a user's machine does;
  the warm clone has only the home's.

## Not tested here

- `TICKET_UNKNOWN`, `TICKET_CLOSED`, `CANDIDATE_NOT_ISOLATED`, `SELECTION_REFUSED`, `RUN_INCOMPLETE`,
  `CLOSE_CLONE_FAILED`: the interface's codes no KPI line names.
- The non-goals: the close itself, Gov OS's own landing tools, `merge_queue.py`'s speed-ups, a chore's run, other
  languages.
