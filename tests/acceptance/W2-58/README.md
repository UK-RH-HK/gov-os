# W2-58 acceptance tests: Policy 2 in the guard and the launcher

Ticket `DAEO-5j8b` (W2-58, STANDARD). Written by the independent test designer (MR-3) from the ticket's KPI lines,
its card (`docs/plan/WAVE_2_WBS.md` §2) and its sources (DEC-820, DEC-821, DEC-826 Q2, DEC-845, DEC-849, DEC-857,
DEC-864 item 5; the history in DEC-162, DEC-215, DEC-218, DEC-508, DEC-525, DEC-548, DEC-553, DEC-557, DEC-562,
DEC-570), before the implementation exists (`git diff --name-only w2/integrate...HEAD` was empty when they were
written). Proportion: STANDARD (DEC-221): every KPI line's success and failure, and the key edge cases.

## What the tests drive

Public interfaces only:

- **the guard**: the kernel's PreToolUse hook `template/governance/kernel/hooks/pretooluse.py`, copied as one file into a
  temporary project at `governance/kernel/hooks/` and run as the harness runs it (the call on stdin, `GOV_ROLE`,
  `GOV_TICKET`, `CLAUDE_PROJECT_DIR`);
- **`gov launch <role> <ticket>`**, through the `gov` console entry point, with a stand-in CLI at
  `<HOME>/.local/bin/claude` that starts no session and records the `--settings` value it was handed;
- **`python3 -m gov.guard.hooks`**, the hook-listing helper;
- **the path-map schema** `template/governance/kernel/schemas/path-map.schema.json` (validated with `jsonschema` and a
  local store of the kernel's schemas) and this repository's `governance/project/path-map.yaml`, read as files.

No private name of the implementation is used.

## The fixture

Every project is a git repository built from scratch (`w2_58_support.make_project`) at
`<tmp>/home/gov-os-worktrees/W2-95`, under a temporary `HOME` and `TMPDIR`:

- tickets: **T** = `DAEO-zz58` (engineer, `wbs_id: W2-95`, acceptance folder `tests/acceptance/W2-95/`), another
  engineer ticket `DAEO-zz59` (W2-96, whose tests are in the base), product-spec, auditor and research tickets, and
  `DAEO-zz63` (engineer, W2-93), measured by the evaluation set by its ticket id;
- two commits: the base (on `w2/integrate`, or on `main` for a project with no base), then T's own commit on
  `w2/W2-95`: it changes `src/app/main.py`, adds `src/app/added.py`, adds T's tests and changes T's ticket file;
- stand-in secrets (`.env`, `.env.local`, `services/api/.env`, `services/api/.env.production`, `certs/server.pem`,
  `certs/server.key`, `config/secrets.yaml`, `config/secrets.json`) and a stand-in `~/.ssh/` under the temporary
  `HOME`: made-up words, never a real secret;
- a held-out list `governance/project/held-out.yaml` naming a stand-in folder `<HOME>/held-out-material/`, never the
  real held-out path, which no file of this suite names;
- for (d), the kernel template's path map with an `evaluation_sets` block: set `fixture-questions`, visible
  `eval/memory/visible/**`, hidden `eval/memory/hidden/**` and `eval/memory/answers-*.yaml`, measures
  `roles: [research]`, `tickets: [DAEO-zz63]`; and a throwaway scorer `eval/score.py` that reads the hidden part and
  prints only a score.

Read-only cases of one module share one project (module-scoped fixtures `open_world`, `branch_world`, `eval_world`);
cases that break a file build their own.

## KPI lines, their tests, and the red reason

Red reason today, in one line: the guard still refuses what Policy 2 opened (DEC-508, DEC-525, DEC-557: any read,
search or listing that takes in the two protected files, every search from the root), and has neither the secrets
name rule (a), nor (c), nor (d); the launcher denies the Read tool only the held-out paths; the schema and this
repository's path map have no `evaluation_sets` block.

| KPI line | Tests | Red today because |
|---|---|---|
| Success 4: the listing and search refusals over `governance/` and `.claude/` are gone; the held-out list's names readable; the settings file's reads follow Policy 2 (DEC-820 (b), DEC-821 item 3, DEC-857 item 3) | `test_w2_58_reads_open.py::test_the_held_out_list_and_the_settings_file_are_readable` (6 roles × Read, `cat`, `grep`, Grep of each file); `::test_searches_and_listings_of_governance_and_claude_are_open` (6 roles × `ls governance/project/`, `ls governance/`, `ls -la .claude/`, Glob `governance/project/*`, Glob in `.claude`, Grep in `governance/project`, `governance`, `.claude`, `grep -rn 'governance/project' src/`, `git grep … -- 'governance/project/*.yaml'`, `grep -rn … .claude/`, `find governance`); `::test_searches_from_the_repository_root_are_open` (every role but the engineer, whose root searches take in T's tests, item 3: Grep with no path or the root as path, `grep -r … .`, `grep -rn …`, `rg`, `git grep`, `find . -name`, Glob `**/*.md`) | "the call reads the settings file or the held-out file, which is refused to every role (DEC-508, DEC-525)"; "the search starts at the folder the settings file or the held-out file lies under and gives no path or glob that keeps both out". `git grep`, `find . -name` and Glob `**/*.md` from the root already pass today. |
| Failure: no write rule widens | `test_w2_58_reads_open.py::test_a_role_that_may_not_write_either_file_still_may_not` (5 roles × Write, Edit of each file, `echo > settings`, `sed -i` of the list); `::test_the_hook_listing_helper_still_lists_the_hook_events` | Pass today (they hold today's behaviour). |
| Success 4 and failure, (a): secrets stay refused, by name, for every role; a search from above is not refused for their sake | `test_w2_58_still_refused.py::test_a_dot_env_file_is_refused_by_every_route_to_every_role` (6 roles × Read, Grep, `cat`, `head`, `sed -n`, `grep`, `git show HEAD:.env`, `cp`); `::test_every_secret_name_is_refused` (8 names × engineer, auditor × Read, `cat`); `::test_a_file_under_the_home_ssh_folder_is_refused`; `::test_the_neighbours_of_secrets_are_readable`; `::test_a_search_that_starts_above_a_secret_is_not_refused_for_its_sake` | The guard has no name rule for secrets: `Read .env` is allowed. The neighbour and search-above cases pass today. |
| Success 4 and failure, (b): the held-out material's contents stay refused; a broken list stops every call (DEC-162, DEC-215, DEC-218) | `test_w2_58_still_refused.py::test_the_held_out_material_stays_refused_by_every_route` (6 roles × Read, Grep, Glob, `cat` absolute, `~`, `$HOME`, `..`, through a symbolic link by Read and `cat`, `ls`, `grep -r`, `cp`); `::test_a_broken_held_out_list_still_stops_every_call` | Pass today (they hold today's behaviour). |
| Success 1: the engineer on T is refused T's acceptance tests by the guard and by its sandbox, and can still run them and see names, results and failure messages (DEC-820 (c)) | `test_w2_58_engineer.py::test_the_engineer_is_refused_its_tickets_acceptance_tests` (content reads: Read, Grep, `cat`, `head`, `sed -n`, `awk`, `grep`, `git show HEAD:<file>`, `cp`; aimed listings: Grep, Glob ×2, `ls` ×2, `find`; searches from above: Grep with no path, `tests`, `tests/acceptance`, `grep -rn … tests/`, `grep -r … .`, `rg`, `git grep`; history: `git log -p`, `git show HEAD`, `git diff HEAD~1`, `git diff w2/integrate...HEAD`); `::test_the_engineer_still_runs_its_tests_and_reads_the_rest` (`python3 -m pytest tests/acceptance/W2-95/ -q`, `pytest tests/acceptance/W2-95/`, another ticket's tests, searches narrowed to `src/`, `git log -p -- src/`, `git show --stat`, `git diff --stat`, `--name-only`, `git log --name-status`, the code, `ls tests/acceptance/`, the held-out list); `::test_the_engineer_on_another_ticket_reads_ts_tests`; `::test_the_pytest_run_shows_names_results_and_failure_messages`; `::test_the_launch_denies_the_read_tool_ts_tests_without_binding_the_sandbox`; `::test_the_launch_leaves_other_files_to_the_read_tool_and_keeps_the_held_out_rules` | The guard allows the engineer every read of its tests; the launched settings have no Read rule for them. The three root searches (Grep with no path, `grep -r … .`, `rg`) pass today for DEC-557's reason. The "allowed" cases pass today but the held-out list's Read. |
| Success 2: the test designer on T is refused the files T's branch changes, other than its own tests, and reads the base's version (DEC-820 (c), DEC-826 Q2) | `test_w2_58_test_designer.py::test_the_test_designer_is_refused_the_files_the_branch_changes` (each changed file × Read, Grep, `cat`, `head`, `grep`, `git show HEAD:<file>`, `cp`); `::test_the_test_designer_is_refused_searches_and_history_that_take_in_the_changed_files` (Grep, Glob, `ls`, `find` aimed at `src/app`; Grep with no path or `src`; `grep -rn … src/`, `grep -r … .`, `rg`, `git grep`; `git diff w2/integrate...HEAD`, `git show HEAD`, `git log -p`); `::test_the_test_designer_reads_the_base_its_tests_its_ticket_and_unchanged_code` (`git show w2/integrate:<file>` and by the base's sha, unchanged files, narrowed searches, own tests, the ticket file, `--stat`, `--name-only`, `--name-status`, pytest); `::test_the_base_version_it_reads_is_the_base_s`; `::test_with_no_base_branch_nothing_is_refused_under_this_item`; `::test_another_role_on_t_reads_the_changed_files`; `::test_the_launch_denies_the_read_tool_the_changed_files_without_binding_the_sandbox`; `::test_the_launch_with_no_base_denies_the_read_tool_no_code` | The guard has no (c) for the test designer; the launched settings have no Read rule for the changed files. Root searches pass today for DEC-557's reason; `grep -r … .` with no base fails today for the same reason. |
| Success 3: an evaluation set's hidden part is refused to a measured session; the measurement scores it without showing the answers (DEC-820 (d), DEC-845) | `test_w2_58_evaluation_sets.py::test_a_measured_session_is_refused_the_hidden_part` (measured by role and by ticket × 18 routes); `::test_a_measured_session_reads_the_visible_part_and_runs_the_measurement` (visible part, a path the single-folder `*` leaves out, `python3 eval/score.py`); `::test_a_session_the_set_does_not_measure_reads_the_hidden_part` (product-spec, another engineer ticket, an auditor not listed, the test designer, the ticket lead); `::test_the_scorer_reads_the_hidden_part_and_prints_only_a_score`; `::test_the_launch_of_a_measured_session_denies_the_read_tool_the_hidden_part`; `::test_the_launch_of_an_unmeasured_session_leaves_the_hidden_part_to_the_read_tool`; `::test_the_schema_names_the_block`; `::test_a_valid_block_validates`; `::test_an_invalid_block_does_not_validate` (no `hidden`, a path that is not a string in `hidden` or `visible`, `hidden` not a list); `::test_this_repository_declares_a_set_for_w2_61` | The guard has no (d): every read of the hidden part is allowed; the launcher writes no Read rule for it; the schema does not declare the block (its top level is open, so every invalid block validates); this repository's path map has no `evaluation_sets`. Root searches pass today for DEC-557's reason. |
| Success 5: reviewers and auditors read everything (DEC-820 item 3) | `test_w2_58_auditor.py::test_the_auditor_on_t_reads_its_tests_and_its_code`; `::test_secrets_and_held_out_material_still_refuse_the_auditor`; `::test_an_auditor_a_set_lists_as_measured_is_refused_its_hidden_part` | Root searches (Grep with no path, `grep -r … .`) are refused (DEC-557); `.env` is read; (d) is missing. |
| Failure: a guard error still fails closed | `test_w2_58_fails_closed.py::test_a_malformed_evaluation_block_refuses_the_calls_of_the_sessions_it_could_concern` (by role, by ticket: the hidden path by Read and `cat`, and `README.md`); `::test_a_malformed_evaluation_block_refuses_the_launch`; `::test_an_engineer_s_unparseable_ticket_file_refuses_its_reads_under_c`; `::test_a_test_designer_s_unparseable_ticket_file_refuses_its_reads_under_c`; `::test_a_git_failure_finding_the_changed_files_refuses_the_test_designer_s_reads` (T's branch an orphan: git finds no merge base) | The guard and the launcher read no `evaluation_sets`; the guard has no (c), so it allows these reads. |
| The code under test (DEC-732) | `test_w2_58_code_under_test.py::test_a_child_imports_gov_from_the_code_under_test` | Passes. |

### Readings the tests take, stated

- **The engineer's root searches** are item 3's, not item 1's: from the root they take in T's acceptance folder, so
  they are refused to the engineer, and item 1's root-search cases run for the other five roles.
- **`find . -name …` and a Glob from the root by the engineer** are not asserted either way: they show names, not
  contents, and are not "aimed inside" the folder.
- **The test designer's aimed listings** (Glob `src/app/*`, `ls src/app`, `find src/app`) are asserted refused, as the
  brief says ("aimed listing … as in 3"), although the names are open to it through `git diff --name-only`. See the
  package in the return.
- **A malformed `evaluation_sets` block** refuses every call of a session it could concern (a Read of `README.md`
  included): the guard cannot tell whether a path is hidden.
- **The sandbox:** a Read rule "binds the sandbox's reads" when it is literal (no `*`, `?` or `[`) and names the file,
  a folder above it or a path inside it, or when a `sandbox.filesystem.denyRead` entry holds the file. Rules are read
  as the CLI reads them: `//abs`, `~/home`, `/` or `./` from the project.

## How the tests exercise this worktree's code

Run from this worktree with `PYTHONPATH` set per command:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/acceptance/W2-58 -q -p no:cacheprovider -rs

Every child process (the guard, `gov launch`, the helper) gets `PYTHONPATH` from `w2_58_support.python_path()`: the
runner's own value, else the `src/` of the worktree that holds this suite (DEC-732). The guard file run is the
kernel template's, copied from this worktree. `test_w2_58_code_under_test.py` shows which `gov` a child imports.
