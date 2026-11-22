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
| base_red | `main`; `tests/unit/test_known_red.py` red on the base, importing the widget; A changes the widget | `PROJ-aaaa=topic/aa` |
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
| failure-1 | `test_w2_115b_unmoved.py::test_a_red_run_does_not_move_the_integration_branch`, `test_w2_115b_unmoved.py::test_a_red_on_the_base_too_is_a_known_base_red_and_the_branch_moves_only_to_the_tested_merge`, `test_w2_115b_unmoved.py::test_a_g1_refusal_moves_nothing`, `test_w2_115b_unmoved.py::test_a_head_moved_during_the_run_is_head_moved_and_stays_as_moved` | as success-1; the base-red case, rewritten in W2-202 (below): on W2-202's base the queue refuses `BATCH_UNEXPLAINED` |
| failure-2 | `test_w2_115b_land.py::test_green_closed_exactly_when_merged`, `test_w2_115b_red.py::test_red_closed_exactly_when_merged`, `test_w2_115b_batch.py::test_batch_closed_exactly_when_merged`, `test_w2_115b_authors.py::test_authors_closed_exactly_when_merged`, `test_w2_115b_authors.py::test_authors_alone_closed_exactly_when_merged`, `test_w2_115b_notices.py::test_notices_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_feature_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_onto_closed_exactly_when_merged`, `test_w2_115b_unmoved.py::test_base_red_closed_exactly_when_merged`, `test_w2_115b_unmoved.py::test_moved_closed_exactly_when_merged`, `test_w2_115b_settings.py::test_a_detached_root_with_no_onto_and_no_queue_yaml_is_integration_unknown`, `test_w2_115b_settings.py::test_a_ticket_without_a_work_branch_is_branch_unknown` | as success-1 (each first reads the queue's envelope, so none is green on the base by nothing having landed) |

Every case is an acceptance test but four of success 9's, which are **repository-state** cases (they read this
repository's own files: `facts.yaml`, the kernel templates and the generated copies) and belong to the record-reading
set; `test_w2_115b_dod.py::test_the_facts_gov_adopt_writes_hold_exactly_three_dod_lines` is an acceptance case on a
planted repository. No case is green on the base.

## Rewritten in W2-202 (DEC-1214 L2, Q-CLOSE)

- `test_a_red_on_the_base_too_is_batch_unexplained_and_moves_nothing` asserted the refusal W2-202's A1 replaces: a red
  that is red on the base too refused the batch (`BATCH_UNEXPLAINED`) and nothing moved. By DEC-1214 L2 and Q-CLOSE
  such a red is a known base red: the ticket lands and its close record holds the red (`reds`: `verdict: base`;
  `base_reds`). The case is now `test_a_red_on_the_base_too_is_a_known_base_red_and_the_branch_moves_only_to_the_tested_merge`
  (the branch still moves only to the tested merge with its close commits, failure line 1's other half); the planted
  run is `base_red` (it was `unexplained`). W2-202's own folder holds the line's full cases.
- The planted acceptance folders' READMEs now hold a KPI map (`w2_115b_support.readme_text`), as a real ticket's
  folder does: W2-202's A3 runs each landed ticket's folder through the runner `gov accept` uses, which refuses a
  folder with no map.

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

## Fix: the base's unplaced paths (L2-4, DEC-1217 (1), DEC-1223 (9))

Written by the independent test designer from the ticket's section "Fix: the queue's selection refuses only the
landing's own unplaced paths" (the fix line and its Verify), before any implementation of the fix. The fix adds no
line to the ticket's `kpis:`, so its clauses are mapped here as lines numbered after the ticket's own (success 10 to
13, one per Verify clause; failure 3, the fix's failure line), so they never merge with success 1 to 9 or failure 1
and 2. Every case is of the acceptance kind. Public interfaces only: `gov queue PROJ-aaaa=topic/aa --select` without
`--json` (one JSON object on stdout, or `SELECTION_REFUSED` on stderr, exit 2), the landing with `--json`, and
`gov close --select PROJ-aaaa` (the selection without a branch's change).

**What is planted** (`test_w2_115b_unwritten_paths.py::_plant`, a fresh project per case, `planted`): A and B on
`main`; a green nightly record `docs/close/nightly/NR-...json` (`verdict: green`, `head`: the first commit) committed
by no ticket; then one direct commit per base-side path on `main` with `Role: orchestrator` and no `Task:`
(`docs/emergency-2/briefs/LEAD-plan.md`, outside the test map's `record_only`; `repin.sh`; or `src/app/gizmo.py`,
which `tests/unit/test_gizmo.py` imports); A's branch `topic/aa` forked at the green head with one commit of A's
changing the widget (mapped: A's suite holds it, `tests/unit/test_uses_widget.py` imports it), plus
`tools/stray.sh` in the refused case.

| KPI id | tests | expected red reason |
|---|---|---|
| success-10 (the fix's clause 1: the base's two paths under `unplaced_base`, exit 0) | `test_w2_115b_unwritten_paths.py::test_select_lists_the_base_s_unplaced_paths_under_unplaced_base_and_exits_0`, `test_w2_115b_unwritten_paths.py::test_the_landing_beside_the_base_s_unplaced_paths_lands_and_closes` | `--select` exits 2, `SELECTION_REFUSED: PROJ-aaaa: 2 changed path(s) nothing maps to a suite ...: docs/emergency-2/briefs/LEAD-plan.md, repin.sh`; the landing is refused the same way (`ok: false`, exit 3, "nothing lands") |
| success-11 (clause 2: the branch's own unplaced path refused, naming it and not the base's) | `test_w2_115b_unwritten_paths.py::test_a_branch_that_writes_an_unplaced_path_is_refused_naming_it_and_not_the_base_s` | the refusal (exit 2) names the base's two paths beside `tools/stray.sh` |
| success-12 (clause 3: a base-side path a test imports still selects that test) | `test_w2_115b_unwritten_paths.py::test_a_base_side_path_a_test_imports_still_selects_that_test` | `--select` exits 2, refused for the base's document |
| success-13 (clause 4: without `change` the base-side path is still refused) | `test_w2_115b_unwritten_paths.py::test_gov_close_select_without_a_change_still_refuses_the_base_s_unplaced_paths` | none: a guard, green on the base; it must stay green (`gov close` does not change) |
| failure-3 (a path the landing wrote that nothing places is no longer refused, or without `change` the base's unmapped path stops being refused) | `test_w2_115b_unwritten_paths.py::test_a_branch_that_writes_an_unplaced_path_is_refused_naming_it_and_not_the_base_s`, `test_w2_115b_unwritten_paths.py::test_gov_close_select_without_a_change_still_refuses_the_base_s_unplaced_paths` | the first as success-11; the second a guard, green on the base |

**Unit tests beside them** (not run by `gov accept`; `tests/unit/queue/test_queue_select_unwritten.py`, the
fix's `select.scoped` with and without `change`, on `queue_support`'s planted project, its map placing
`docs/close/**` as records so `unplaced_base` is compared whole): the base's paths listed under `unplaced_base`
(clause 1); `change=[]` still treats them as base-side; the key present and `[]` when there is none; another ticket's
commit on the base is base-side too (the fix line: neither the ticket's own commits nor `change` wrote it); a
base-side path an import or a coupling reaches still selects its suite (clause 3); a path the ticket's own trailered
commit wrote is refused though the green range holds it, and a path `change` names is refused, each naming only
itself (clause 2, failure 3); without `change` the base's paths are still refused (clause 4, a guard). Red on the
base: all but the guard, each by `SelectionRefused` naming the base's paths, or the missing key.

**Readings this fix's cases take.**

1. **"Base-side"** is a path counted from the green record (the diff from the green head to the merged result)
   that no commit carrying the ticket's `Task:` trailer changed and that the branch's change (`change`, the paths the
   queue passes) does not name. A commit by another ticket is base-side too, as the fix line reads.
2. **`unplaced_base`** is a sorted list of paths, always present in the selection when `change` is given, also when
   given as an empty list; in `--select`'s object for one ticket. A batch's union of it is not tested.
3. **"Without `change` nothing changes"** is read through `gov close --select`: still `SELECTION_REFUSED`, exit 2,
   naming the base's paths. Whether `scoped`'s dict without `change` holds the key is not tested.
4. **The landing case** asserts only that the ticket lands and closes as a green landing does (success 1 and 2's
   checks); what the close record's `selection` holds of `unplaced_base` is not tested.

## Fix: adopted repositories land (D7, DEC-1227)

Written by the independent test designer from the ticket's section "Fix: adopted repositories land; the stage commits
need no trailer and no marker" and its KPI lines (success 14 to 16, failure 4, added at the end of `kpis:`). **The cases
are pins, green on the base by design**: the measurement shows nothing refuses `gov adopt`'s stage commits (they carry no
`Role` and no `Task` trailer, W1-41), so the fix builds nothing and the tests only stop a later change from starting to
ask them for trailers. They are acceptance cases (not repository-state), in
`test_w2_115b_adopted_stage_commits.py`; the whole file skips with a reason when `gitleaks` is not on `PATH` (stage A0
sets up `.gitleaks.toml`). Public interfaces only: `python3 -m gov.cli.main adopt|queue ... --root <project> --json`
(the pytest process's `src/` on `PYTHONPATH`, the sandbox environment of `w2_115b_support.base_env`, which holds the
interpreter's user site so `pytest` is found), the git state of the planted repository.

**What is planted** (three runs, each built once per session under a file lock in pytest's shared folder, as
`conftest._shared`, from helpers in the test file; a `w2_115b_support.Planted` project each, one ticket `PROJ-adop`
whose `allowed_paths` are the widget, its acceptance folder and the adoption ticket's places `governance/adoption/**`,
`.gitleaks.toml`, `.gitignore`):

| run | project and branch | command |
|---|---|---|
| landed | branch `work`: stages A0, A1, A2 **run by the tool** (`gov adopt --lite --stage <A> --role orchestrator`, each committed by `gov adopt`), then one feature commit (the widget) with `Task:` and `Role: engineer` | `gov queue PROJ-adop=work --json` |
| edited | the same branch to A2, then a hand edit of `governance/adoption/A1-inventory.md` committed with `Task: PROJ-adop` and `Role: orchestrator` | `gov adopt --lite --stage AS --role orchestrator --json` |
| stage_subject | branch `topic/ad`: an engineer commit (the widget), then a commit with the subject `gov adopt --lite A0: safety baseline`, no trailer, adding `tests/acceptance/F-ad/test_ad_more.py` | `gov queue PROJ-adop=topic/ad --json` |

| KPI id | tests | expected red reason |
|---|---|---|
| success-14 (the adopted repository lands) | `test_w2_115b_adopted_stage_commits.py::test_the_stage_commits_carry_no_role_and_no_task_trailer`, `test_w2_115b_adopted_stage_commits.py::test_a_branch_of_stage_commits_and_a_feature_commit_lands_and_closes` | none on the base: pins, green by design. They go red when the landing asks the stage commits for a `Role` or `Task` trailer (`TEST_AUTHOR_REFUSED` or another refusal, `landed` empty, exit 3), or when `gov adopt` starts to write trailers (the premise case) |
| success-15 (what the stage commits write outside the places is a notice) | `test_w2_115b_adopted_stage_commits.py::test_a_path_a_stage_commit_wrote_outside_the_ticket_s_places_is_a_notice_and_the_exit_is_0` | none on the base: a pin. Red when A0's coordination ticket or roster stop being told (`path_notices` holds no path of A0's commit) or become a refusal (exit not 0) |
| success-16 (a hand edit of a stage record is caught by `gov adopt`) | `test_w2_115b_adopted_stage_commits.py::test_a_hand_edit_of_a_stage_record_is_refused_by_the_next_stage_as_adopt_chain_broken`, `test_w2_115b_adopted_stage_commits.py::test_the_refused_stage_commits_nothing` | none on the base: a pin. Red when the next stage runs over the edited record (exit 0), or refuses with another code, or moves HEAD or the working tree |
| failure-4 (a stage's subject lets a change to the acceptance tests through) | `test_w2_115b_adopted_stage_commits.py::test_a_stage_subject_commit_that_adds_an_acceptance_test_is_refused_and_nothing_lands` | none on the base: a guard, green. Red when a commit with a stage's subject and no `Role` that adds a file under `tests/acceptance/` is let through (the ticket lands, or the refusal does not name the commit) |

**Readings this fix's cases take.**

1. **"The adopted repository"** is the synthetic one the measurement used (`~/gov-os-runs/d7/`): `gov adopt` runs for
   real on the planted project (so its commit subjects `gov adopt --lite A0: safety baseline`, `... A1: inventory`,
   `... A2: classification` and its trailer-less messages are the tool's, never hand-written); a fixture that cannot
   adopt fails with `fixture: ...`, never as a red.
2. **"No `Role` and no `Task` trailer"** is read twice from git: no line `Role:` or `Task:` in the commit's message and
   no such key among its parsed trailers.
3. **"Lands"** is success 1's checks on this branch: exit 0, `landed == [PROJ-adop]`, `refused` and `culprits` empty, the
   ticket `closed` at the integration head through one close commit (`assert_landed_through_close_commits`), and the
   stage commits and the feature commit under the head.
4. **Success 15 pins "a path of A0's commit", not the paths**: at least one `path_notices` entry names A0's commit and a
   path A0 wrote outside the places (the coordination ticket the tool files, the roster); every notice of that commit
   names a path the commit wrote; the exit is 0 and nothing is refused. The ticket id of the coordination ticket is
   random and never asserted.
5. **Success 16's refusal** is read from the `--json` envelope (`ok: false`, `error.code: ADOPT_CHAIN_BROKEN`, the message
   naming `A2-classification.md`), exit not 0 (it is 1 today); "nothing committed" is HEAD, every ref, the working tree
   and the tracked files' bytes as before the call.
6. **Failure 4's answer** is as G-1's alone case: `ok: true`, exit 3, `refused` holds the ticket once with
   `TEST_AUTHOR_REFUSED` and the offending commit's full id, `landed` empty, `head` null, no branch moved, the ticket
   `open`.

**Controls (run by hand in a throwaway copy, never committed; they prove the cases can go red, they pin nothing).**

- The landing made to demand a `Role` on every commit of the range (the author check without its restriction to the
  acceptance places): success-14's landing case and success-15's case go red (`TEST_AUTHOR_REFUSED` naming the three
  stage commits, exit 3); the premise, success-16 and failure-4 stay green.
- The author check made to skip a commit whose subject starts `gov adopt --lite A`: failure-4's case goes red (the ticket
  lands); the others stay green.
- The same plant with a ticket whose `allowed_paths` do **not** hold `governance/adoption/**` and `.gitleaks.toml`: the
  landing is refused `SELECTION_REFUSED` naming `.gitleaks.toml` and the three records (exit 2, nothing lands). This is the
  ticket's "what stays as it is", told, not pinned here.
- The same chain with no hand edit: `gov adopt --lite --stage AS` runs (exit 0), so success-16's refusal is the edit's.

## Fix: `gov queue` never leaves uncommitted work behind (audit N-01)

Written by the independent test designer from the fix line "`gov queue` refuses a branch whose worktree holds
uncommitted or untracked work in tracked paths, `QUEUE_WORKTREE_DIRTY`, naming the worktree and the files", before any
implementation of it. The fix adds no line to the ticket's `kpis:`, so it is mapped as `success-17` (the refusal, its
forms and that the entry is not poisoned by it) and `failure-5` (honest work is not refused: the controls), numbered
after the ticket's own, the earlier fix's and D7's (success 10 to 16, failure 3 and 4; at its landing it read success-14 and failure-4, before D7's `kpis:` lines took those numbers). Every case is of the acceptance kind, in
`test_w2_115b_dirty_worktree.py`. Public interface only: `gov queue PROJ-aaaa=topic/aa [--onto main] --json`, its
envelope, stderr and exit code, the planted repository's refs and each worktree's `git status --porcelain`.

**What is planted:** a fresh project per case (A and B on `main`, `.gitignore` holding `.gov-runtime/`, `__pycache__/`,
`*.pyc`, `build/`), A's branch `topic/aa` with one commit changing the widget, and a worktree `wt-aa` (a sibling folder of
the project) that holds `topic/aa`, or the project's own main tree switched to `topic/aa` (with `--onto main`).

| KPI id | tests | expected red reason |
|---|---|---|
| success-17 | `test_w2_115b_dirty_worktree.py::test_a_modified_tracked_file_in_the_branch_s_worktree_refuses`, `test_w2_115b_dirty_worktree.py::test_a_staged_change_in_the_branch_s_worktree_refuses`, `test_w2_115b_dirty_worktree.py::test_an_untracked_new_file_in_a_tracked_directory_refuses`, `test_w2_115b_dirty_worktree.py::test_a_deleted_tracked_file_in_the_branch_s_worktree_refuses`, `test_w2_115b_dirty_worktree.py::test_two_dirty_files_are_both_named`, `test_w2_115b_dirty_worktree.py::test_the_main_tree_holding_the_branch_dirty_refuses`, `test_w2_115b_dirty_worktree.py::test_after_the_change_is_discarded_the_same_entry_lands`, `test_w2_115b_dirty_worktree.py::test_after_the_change_is_committed_the_same_entry_lands_with_it` | on the base the queue ignores the worktree and lands: the answer is `ok: true`, exit 0, not `QUEUE_WORKTREE_DIRTY` (the last two fail at their refusal half) |
| failure-5 | `test_w2_115b_dirty_worktree.py::test_a_clean_worktree_holding_the_branch_lands`, `test_w2_115b_dirty_worktree.py::test_a_clean_main_tree_holding_the_branch_lands`, `test_w2_115b_dirty_worktree.py::test_files_the_gitignore_ignores_are_not_dirty`, `test_w2_115b_dirty_worktree.py::test_a_branch_checked_out_in_no_worktree_lands`, `test_w2_115b_dirty_worktree.py::test_another_branch_s_dirty_worktree_does_not_refuse` | none: guards, green on the base; they must stay green |

**Readings this fix's cases take.**

1. **Dirty** is what `git status --porcelain` of the worktree lists (modified, staged, deleted, or untracked and not
   ignored by `.gitignore`). A file the `.gitignore` ignores is not dirty.
2. **The refusal's form:** `ok: false`, `error.code` `QUEUE_WORKTREE_DIRTY` (also on stderr as `QUEUE_WORKTREE_DIRTY:`),
   `error.message` holding the worktree's path and each dirty file's repository-relative path, an exit code of 1 (a
   candidate refused before the run, as `BRANCH_UNKNOWN`) or 3 (the run refused as a whole): either is accepted, 0 and
   2 are not. Nothing moves: every ref, the root's `HEAD`, status and tracked files, no `docs/close/`, the ticket
   still `open`, the branch not merged; the dirty worktree itself is left as it was.
3. **"Not poisoned":** after the change is discarded (`git checkout -- <file>`), or committed in the worktree (the entry
   then lands with the new tip), the same command lands and closes the ticket.
4. **The main tree holding the branch** is planted with the root switched to `topic/aa` and `--onto main`.

## Fix: the selection's deleted test and record-only document (I-1, I-2; DEC-1239)

Written by the independent test designer from the four `Fix,` lines at the end of the ticket's `success:` list, before
any implementation. They are numbered after the ticket's own (the KPI ids below follow the order of the lines, success
18 to 21, after the adoption fix's 14 to 16 and the dirty worktree's 17 there; the ids are labels of this table).
Acceptance cases in `test_w2_115b_select_fixes.py`; public interfaces only: `gov queue PROJ-aaaa=topic/aa --select`
(one JSON object on stdout, or `SELECTION_REFUSED` on stderr, exit 2) and the landing with `--json`.

**What is planted:** A and B on `main`, a suite folder `tests/suite_x/` with two test files (`test_one.py`,
`test_two.py`, the latter importing the widget), `tests/gone/test_gone.py`, a green nightly record, then A's branch
`topic/aa` with one commit of A's changing the widget and, by case, deleting `test_one.py` or `test_gone.py`, or
writing `docs/x.md` (outside `record_only`, placed by nothing), `tools/stray.sh`, `src/app/NOTES.md` or
`template/guide.md`. The map-named case replaces the test map with one whose coupling names `tests/gone/test_gone.py`
for the widget's path.

| KPI id | tests | expected red reason |
|---|---|---|
| success-18 (a deleted test file is no target, I-1) | `test_w2_115b_select_fixes.py::test_a_deleted_test_file_is_listed_under_deleted_not_selected_and_its_folder_still_runs`, `test_w2_115b_select_fixes.py::test_the_landing_beside_a_deleted_test_file_lands_and_closes`, `test_w2_115b_select_fixes.py::test_deleted_is_present_and_empty_when_the_change_deletes_nothing` | `--select` exits 2 `SELECTION_REFUSED ... tests/suite_x/test_one.py (FILE_GONE)`; the landing is refused the same way; the third: the `deleted` key is missing |
| success-19 (a map-named target that is gone still refuses, I-1) | `test_w2_115b_select_fixes.py::test_a_map_named_target_the_branch_deletes_still_refuses_file_gone` | none: a guard, green on the base; it must stay green |
| success-20 (a record-only document is placed with a notice, I-2) | `test_w2_115b_select_fixes.py::test_a_document_nothing_places_is_a_record_with_a_notice_and_select_exits_0`, `test_w2_115b_select_fixes.py::test_the_landing_places_the_record_and_holds_the_notice_in_its_answer_and_the_queue_record` | `--select` exits 2 `SELECTION_REFUSED ... docs/x.md`; the landing is refused the same way (`ok: false`) |
| success-21 (code the branch writes that nothing places still refuses, I-2) | `test_w2_115b_select_fixes.py::test_code_beside_a_record_is_refused_naming_the_code_and_not_the_record`, `test_w2_115b_select_fixes.py::test_a_markdown_file_under_src_or_template_that_nothing_places_still_refuses` (two cases: `src/app/NOTES.md`, `template/guide.md`) | the refusal exits 2 as required but names `docs/x.md` beside the code or Markdown file, which is the base's behaviour; green once only the non-record path is named |

**Readings:** the queue record is read at the answer's `record` path; its top-level `notices` is asserted (the record
equals the answer's result, reading 5 above). `records` is asserted equal to the one planted document; `notices` by
membership. The refusal cases write `docs/x.md` beside the offending path so each is red on the base (the base names
both).
