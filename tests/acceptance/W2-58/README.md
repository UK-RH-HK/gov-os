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
  `<HOME>/.local/bin/claude` that starts no session and records the `--settings` value it was handed. The live cases
  (`local_only`, DEC-873 round) instead start the real CLI;
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

KPI numbers below are the ticket's numbering after DEC-873, which restated success 1 and added success 2. The
launcher cases of rows 1, 3 and 4 and the whole of row 2 come from the DEC-873 round (see "DEC-873 rewrite" below).

| KPI line | Tests | Red today because |
|---|---|---|
| Success 5: the listing and search refusals over `governance/` and `.claude/` are gone; the held-out list's names readable; the settings file's reads follow Policy 2 (DEC-820 (b), DEC-821 item 3, DEC-857 item 3) | `test_w2_58_reads_open.py::test_the_held_out_list_and_the_settings_file_are_readable` (6 roles × Read, `cat`, `grep`, Grep of each file); `::test_searches_and_listings_of_governance_and_claude_are_open` (6 roles × `ls governance/project/`, `ls governance/`, `ls -la .claude/`, Glob `governance/project/*`, Glob in `.claude`, Grep in `governance/project`, `governance`, `.claude`, `grep -rn 'governance/project' src/`, `git grep … -- 'governance/project/*.yaml'`, `grep -rn … .claude/`, `find governance`); `::test_searches_from_the_repository_root_are_open` (every role but the engineer, whose root searches take in T's tests, item 3: Grep with no path or the root as path, `grep -r … .`, `grep -rn …`, `rg`, `git grep`, `find . -name`, Glob `**/*.md`) | "the call reads the settings file or the held-out file, which is refused to every role (DEC-508, DEC-525)"; "the search starts at the folder the settings file or the held-out file lies under and gives no path or glob that keeps both out". `git grep`, `find . -name` and Glob `**/*.md` from the root already pass today. |
| Failure: no write rule widens | `test_w2_58_reads_open.py::test_a_role_that_may_not_write_either_file_still_may_not` (5 roles × Write, Edit of each file, `echo > settings`, `sed -i` of the list); `::test_the_hook_listing_helper_still_lists_the_hook_events` | Pass today (they hold today's behaviour). |
| Success 5 and failure, (a): secrets stay refused, by name, for every role; a search from above is not refused for their sake | `test_w2_58_still_refused.py::test_a_dot_env_file_is_refused_by_every_route_to_every_role` (6 roles × Read, Grep, `cat`, `head`, `sed -n`, `grep`, `git show HEAD:.env`, `cp`); `::test_every_secret_name_is_refused` (8 names × engineer, auditor × Read, `cat`); `::test_a_file_under_the_home_ssh_folder_is_refused`; `::test_the_neighbours_of_secrets_are_readable`; `::test_a_search_that_starts_above_a_secret_is_not_refused_for_its_sake` | The guard has no name rule for secrets: `Read .env` is allowed. The neighbour and search-above cases pass today. |
| Success 5 and failure, (b): the held-out material's contents stay refused; a broken list stops every call (DEC-162, DEC-215, DEC-218) | `test_w2_58_still_refused.py::test_the_held_out_material_stays_refused_by_every_route` (6 roles × Read, Grep, Glob, `cat` absolute, `~`, `$HOME`, `..`, through a symbolic link by Read and `cat`, `ls`, `grep -r`, `cp`); `::test_a_broken_held_out_list_still_stops_every_call` | Pass today (they hold today's behaviour). |
| Success 1 (restated, DEC-873): the engineer on T is refused T's acceptance tests by the guard (no OS-level Read rule for it), and can still run them and see names, results and failure messages (DEC-820 (c)) | `test_w2_58_engineer.py::test_the_engineer_is_refused_its_tickets_acceptance_tests` (content reads: Read, Grep, `cat`, `head`, `sed -n`, `awk`, `grep`, `git show HEAD:<file>`, `cp`; aimed listings: Grep, Glob ×2, `ls` ×2, `find`; searches from above: Grep with no path, `tests`, `tests/acceptance`, `grep -rn … tests/`, `grep -r … .`, `rg`, `git grep`; history: `git log -p`, `git show HEAD`, `git diff HEAD~1`, `git diff w2/integrate...HEAD`); `::test_the_engineer_still_runs_its_tests_and_reads_the_rest` (`python3 -m pytest tests/acceptance/W2-95/ -q`, `pytest tests/acceptance/W2-95/`, another ticket's tests, searches narrowed to `src/`, `git log -p -- src/`, `git show --stat`, `git diff --stat`, `--name-only`, `git log --name-status`, the code, `ls tests/acceptance/`, the held-out list); `::test_the_engineer_on_another_ticket_reads_ts_tests`; `::test_the_pytest_run_shows_names_results_and_failure_messages`; `::test_the_launch_adds_no_read_denial_for_ts_tests_and_keeps_the_held_out_rules` (DEC-873 form); `::test_the_launch_leaves_other_files_to_the_read_tool_and_keeps_the_held_out_rules`; live: `test_w2_58_launched_sessions.py::test_a_launched_engineer_collects_its_own_acceptance_tests`, `::test_a_launched_engineer_runs_its_tests_and_sees_their_results` | Guard cases: green since the implementation. DEC-873 round: the launcher still writes `Read(//…/tests/acceptance/W2-9[5]/**)`, which covers T's tests; in a live session that rule becomes a read denial of the commands and pytest collects nothing. |
| Success 2 (new, DEC-873): the launcher adds no OS-level Read deny rule for (c) or (d); the held-out material's Read rules (b) stay; a launch under a malformed `evaluation_sets` block is refused | Settings, starting nothing: the three launcher cases of rows 1, 3 and 4 (DEC-873 forms); `test_w2_58_launched_sessions.py::test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule` (engineer, test designer: every file `git ls-files` lists); `::test_the_held_out_rules_stay_in_every_launched_role_s_settings` (engineer, test designer, auditor, product-spec, research); `test_w2_58_fails_closed.py::test_a_malformed_evaluation_block_refuses_the_launch` (unchanged). Live: `test_w2_58_launched_sessions.py::test_a_launched_test_designer_imports_the_branch_s_changed_code`; `::test_a_launched_session_shows_no_phantom_deletion` (engineer, test designer: `git status --short` has no ` D` line, `git update-index --refresh` exits 0) | The tracked-file cases: the launcher's Read rules for (c) cover `tests/acceptance/W2-95/*` (engineer) and `src/app/main.py`, `src/app/added.py` (test designer). Live: those rules become read denials of the session's commands (P-W2-58-1): the import fails and git shows the refused files as deleted. The held-out and malformed-block cases pass. |
| Success 3: the test designer on T is refused the files T's branch changes, other than its own tests, and reads the base's version (DEC-820 (c), DEC-826 Q2) | `test_w2_58_test_designer.py::test_the_test_designer_is_refused_the_files_the_branch_changes` (each changed file × Read, Grep, `cat`, `head`, `grep`, `git show HEAD:<file>`, `cp`); `::test_the_test_designer_is_refused_searches_and_history_that_take_in_the_changed_files` (Grep, Glob, `ls`, `find` aimed at `src/app`; Grep with no path or `src`; `grep -rn … src/`, `grep -r … .`, `rg`, `git grep`; `git diff w2/integrate...HEAD`, `git show HEAD`, `git log -p`); `::test_the_test_designer_reads_the_base_its_tests_its_ticket_and_unchanged_code` (`git show w2/integrate:<file>` and by the base's sha, unchanged files, narrowed searches, own tests, the ticket file, `--stat`, `--name-only`, `--name-status`, pytest); `::test_the_base_version_it_reads_is_the_base_s`; `::test_with_no_base_branch_nothing_is_refused_under_this_item`; `::test_another_role_on_t_reads_the_changed_files`; `::test_the_launch_adds_no_read_denial_for_the_changed_files_and_keeps_the_held_out_rules` (DEC-873 form); `::test_the_launch_with_no_base_denies_the_read_tool_no_code` | Guard cases: green since the implementation. DEC-873 round: the launcher still writes `Read(//…/src/app/main.py*)` and `Read(//…/src/app/added.py*)`. |
| Success 4: an evaluation set's hidden part is refused to a measured session; the measurement scores it without showing the answers (DEC-820 (d), DEC-845) | `test_w2_58_evaluation_sets.py::test_a_measured_session_is_refused_the_hidden_part` (measured by role and by ticket × 18 routes); `::test_a_measured_session_reads_the_visible_part_and_runs_the_measurement` (visible part, a path the single-folder `*` leaves out, `python3 eval/score.py`); `::test_a_session_the_set_does_not_measure_reads_the_hidden_part` (product-spec, another engineer ticket, an auditor not listed, the test designer, the ticket lead); `::test_the_scorer_reads_the_hidden_part_and_prints_only_a_score`; `::test_the_launch_of_a_measured_session_adds_no_read_denial_for_the_set_and_keeps_the_held_out_rules` (DEC-873 form; by role and by ticket; red: the launcher still writes `Read(//…/eval/memory/hidde[n]/**)` and `Read(//…/eval/memory/answers-*.yaml)`); `::test_the_launch_of_an_unmeasured_session_leaves_the_hidden_part_to_the_read_tool`; `::test_the_schema_names_the_block`; `::test_a_valid_block_validates`; `::test_an_invalid_block_does_not_validate` (no `hidden`, a path that is not a string in `hidden` or `visible`, `hidden` not a list); `::test_this_repository_declares_a_set_for_w2_61` | The guard has no (d): every read of the hidden part is allowed; the launcher writes no Read rule for it; the schema does not declare the block (its top level is open, so every invalid block validates); this repository's path map has no `evaluation_sets`. Root searches pass today for DEC-557's reason. |
| Success 6: reviewers and auditors read everything (DEC-820 item 3) | `test_w2_58_auditor.py::test_the_auditor_on_t_reads_its_tests_and_its_code`; `::test_secrets_and_held_out_material_still_refuse_the_auditor`; `::test_an_auditor_a_set_lists_as_measured_is_refused_its_hidden_part` | Root searches (Grep with no path, `grep -r … .`) are refused (DEC-557); `.env` is read; (d) is missing. |
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
- **The launcher's read denials (DEC-873 item 2):** a file is denied at the OS level when a `Read` deny rule of the
  settings covers it (the rule matches the file or a folder above it), whatever its form. A wildcard does not keep the
  sandbox out: the CLI turns every Read rule that matches existing files into a read denial of the session's commands
  (P-W2-58-1). A file is also denied when an entry of the settings' sandbox read denials covers it (any list under
  `sandbox.filesystem` whose key names reads and denial: `denyRead`, `read.denyOnly`). Rules are read as the CLI reads
  them: `//abs`, `~/home`, `/` or `./` from the project. A sandbox entry `/abs` is also read as an absolute path.
  *(This replaces the earlier reading that a Read rule binds the sandbox only when it is literal, because the Linux
  sandbox skips a rule with a wildcard. P-W2-58-1 measured that reading to be wrong.)*
- **"No phantom deletion"** is read for every tracked file. The session is refused the stand-in secrets too (a), and
  they are tracked in the fixture, so `test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule` would also
  go red if a launcher added an OS-level Read rule for them. DEC-873 does not ask for one.

## Earlier cases rewritten (DEC-821 item 3, DEC-857 item 3)

In `tests/acceptance/W1-02/`: every refusal case of `test_w1_02_protected_reads.py` (6 functions, 190 cases) and the
refusal cases of `test_w1_02_root_searches.py` (7 functions, 122 cases), each now held as allowed for the same actor
in the same form; the engineer's search from the root stays refused, now for (c). Before the implementation they
are red (today's guard refuses them); the unchanged cases of both files stay green. The full list, with the 920 W1-02
cases in 83 functions not rewritten (package P-W2-58-TD-1) and W2-50's 91 second-name cases, is in
[`EARLIER_CASES.md`](EARLIER_CASES.md).

Second round (the lead's answers to TD-1 (a), TD-2, TD-3): 12 more W1-02 files rewritten. Reads and searches of the
two files, of their copies and of the user-level settings file are now allowed. Second names stay refused, with the
read rule's wording no longer asked. The engineer's content search from the root stays refused for (c) (DEC-821
item 1). The bounded-time cases are kept. The table, the cases kept and the three items left for the resume are in
`EARLIER_CASES.md`, "Second round".

Third round (TD-4 (b), TD-5): the 20 within-the-bound cases became "allowed within the bound". The subagent case is
allowed when its ticket's tests do not exist, and a twin is refused when they do. W2-50's 91 second-name cases keep
their verdict, without the read rule's wording. A sweep found 5 earlier "allowed" cases that (c) turns red (W1-02 ×4,
W1-50 ×1), each rewritten to refused (DEC-821 item 1) and named in `EARLIER_CASES.md`, "Third round". This suite's own
cases agree with TD-2, TD-4 and TD-5, so none was changed.

## DEC-873 rewrite (fourth round, after the implementation; `Rewrite-Reason: DEC-873`, DEC-491)

DEC-873 (owner, 2026-10-20, P-W2-58-1 (a)) re-baselines DEC-821's sandbox clause for (c) and (d). The guard alone
enforces them, and the launcher adds no OS-level Read rule for them. The held-out rules (b) stay, and a malformed
`evaluation_sets` block still refuses the launch. No guard case changes. The test count goes from 563 to 576.

**Rewritten in place** (old name → new name; the old expectation is the wrong belief that the Linux sandbox skips a
wildcard rule):

| Old case | Old expectation | New case | New expectation |
|---|---|---|---|
| `test_w2_58_engineer.py::test_the_launch_denies_the_read_tool_ts_tests_without_binding_the_sandbox` | A wildcard Read rule covers each file of T's acceptance folder; no literal Read rule or `sandbox.filesystem.denyRead` entry binds it | `::test_the_launch_adds_no_read_denial_for_ts_tests_and_keeps_the_held_out_rules` | No Read deny rule and no sandbox read denial covers a file of T's acceptance folder; the held-out material is still covered |
| `test_w2_58_test_designer.py::test_the_launch_denies_the_read_tool_the_changed_files_without_binding_the_sandbox` | A wildcard Read rule covers each changed file, without binding the sandbox; no Read rule covers its own test, its ticket or unchanged code | `::test_the_launch_adds_no_read_denial_for_the_changed_files_and_keeps_the_held_out_rules` | No Read deny rule and no sandbox read denial covers a changed file, its own test, its ticket or unchanged code; the held-out material is still covered |
| `test_w2_58_evaluation_sets.py::test_the_launch_of_a_measured_session_denies_the_read_tool_the_hidden_part` (measured by ticket) | A wildcard Read rule covers the hidden part, without binding the sandbox; no Read rule covers the visible part, the file beside it or the scorer | `::test_the_launch_of_a_measured_session_adds_no_read_denial_for_the_set_and_keeps_the_held_out_rules` (by ticket, and added: by role) | No Read deny rule and no sandbox read denial covers the hidden part, the visible part, the file beside it or the scorer; the held-out material is still covered |

Kept unchanged: `test_the_launch_leaves_other_files_to_the_read_tool_and_keeps_the_held_out_rules`,
`test_the_launch_with_no_base_denies_the_read_tool_no_code`,
`test_the_launch_of_an_unmeasured_session_leaves_the_hidden_part_to_the_read_tool`,
`test_a_malformed_evaluation_block_refuses_the_launch`. Their expectations hold under DEC-873. The support module's
`read_tool_denial_faults` (and its literal or wildcard helpers) is replaced by `read_denial_faults`,
`sandbox_read_denials`, `held_out_faults` and `tracked_files`. The engineer's and test designer's module descriptions
are corrected.

**Added** (`test_w2_58_launched_sessions.py`, KPI success 2 and the "can still run" half of success 1):

| Case | Starts | Expected red today because |
|---|---|---|
| `test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule[engineer, independent-test-designer]` | nothing (stand-in CLI) | The launcher's Read rules for (c) cover tracked files (T's tests; `src/app/main.py`, `src/app/added.py`) |
| `test_the_held_out_rules_stay_in_every_launched_role_s_settings[5 roles]` | nothing | Green: the held-out Read rule is in every role's settings |
| `test_a_launched_engineer_collects_its_own_acceptance_tests` (`local_only`) | a real engineer session on T | The Read rule over `tests/acceptance/W2-95/` becomes a read denial of the session's commands: "no tests collected" |
| `test_a_launched_engineer_runs_its_tests_and_sees_their_results` (`local_only`) | the same session | The same: the run shows no "1 failed, 1 passed" and no failure message |
| `test_a_launched_test_designer_imports_the_branch_s_changed_code` (`local_only`) | a real test-designer session on T | `import app.main, app.added` fails (the files are unreadable to its commands) |
| `test_a_launched_session_shows_no_phantom_deletion[engineer, independent-test-designer]` (`local_only`) | both sessions | `git status --short` shows the refused files as ` D` and `git update-index --refresh` exits 1 |

The twins in settings of the three live conditions: "pytest collects" ↔ the engineer's rewritten launcher case; "the
import succeeds" ↔ the test designer's rewritten launcher case; "no phantom deletion" ↔
`test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule`.

## Review cases (fifth round, after the implementation; DEC-136)

An independent review found five behaviours the suite missed (KPI failure: "each of (a) to (d) still refuses, by
every read route an honest agent takes in ordinary work (DEC-801); no write rule widens"; DEC-873 item 1). They are
in `test_w2_58_review.py`, written by a fresh test designer without reading the implementation (only the guard's
answers and `gov launch`'s hand-off to the stand-in CLI). No existing case changed. The test count goes from 576 to
754 (178 added: 117 red, 61 green).

A **protected part** is (c)'s acceptance folder for an engineer on T, (c)'s changed files for a test designer on T,
and (d)'s hidden part for a session an evaluation set measures.

| Behaviour | Tests | Red today because |
|---|---|---|
| 1. File names given at run time: a read or search whose file names come from another command's output (a pipe into `xargs`, `$(...)`, backticks, a `while read` loop over a listing) is judged as a search from the folder the listing starts at | Refused: `::test_the_engineer_is_refused_file_names_given_at_run_time_that_take_in_ts_tests` (7 forms: `git ls-files \| xargs grep`, `find . -name '*.py' \| xargs grep`, `grep … $(git ls-files '*.py')`, `cat $(find tests -name …)`, both with backticks, `find . -print \| while read f; do grep -H … "$f"; done`); `::test_the_test_designer_is_refused_file_names_given_at_run_time_that_take_in_the_changed_files` (7: the same from `.`, `git ls-files src \| xargs cat`, `cat $(find src -name main.py)` and backticks); `::test_a_measured_session_is_refused_file_names_given_at_run_time_that_take_in_the_hidden_part` (6 forms over `eval` or `.` × by role, by ticket). Allowed: `::test_the_engineer_s_narrowed_run_time_listings_and_test_runs_stay_allowed` (6 forms narrowed to `src`, and `python3 -m pytest tests/acceptance/W2-95/ -q … \| tail` ×2); `::test_the_test_designer_s_narrowed_run_time_listings_stay_allowed` (5, narrowed to `src/other` or `docs`); `::test_a_measured_session_s_run_time_listings_of_the_visible_part_stay_allowed` (4 × 2); `::test_a_session_with_no_protected_part_runs_the_same_forms` (the engineer's 7 refused forms × the ticket lead on T, the auditor on T, product-spec, an engineer whose ticket W2-93 has no acceptance folder) | The guard allows each refused form (`decision=allow`): it does not take the names a listing gives at run time as a search from the listing's start. The allowed cases pass. |
| 2. A subagent's reads: at least what its session's role is refused on the session's ticket, and what its own type is refused | Refused: `::test_a_subagent_of_an_engineer_session_is_refused_ts_tests` (subagent `independent-auditor`, `orchestrator`, `research`, `product-spec`, `independent-test-designer` × Read, `cat` of T's test); `::test_a_subagent_of_a_test_designer_session_is_refused_the_changed_files` (subagent `engineer`, `independent-auditor` × Read of `src/app/main.py`); `::test_an_engineer_subagent_of_the_ticket_lead_is_refused_ts_tests`. Allowed: `::test_an_untyped_or_explore_subagent_of_the_ticket_lead_reads_ts_tests` (`general-purpose`, `Explore`) | The guard judges a subagent's read by its type alone: a typed subagent of an engineer or test-designer session reads what its session is refused. The engineer-subagent and untyped cases pass. |
| 3. A ticket named by its WBS id | At the guard (`GOV_TICKET=W2-95`, `W2-93`): `::test_an_engineer_whose_ticket_is_given_by_its_wbs_id_is_refused_ts_tests` (Read, `cat`, Grep); `::test_a_session_measured_by_a_ticket_given_by_its_wbs_id_is_refused_the_hidden_part` (Read, `cat`); allowed: `::test_an_engineer_given_by_wbs_id_reads_its_code_and_another_ticket_s_engineer_reads_ts_tests`. Through `gov launch <role> <wbs_id>` with a stand-in CLI that also records the `GOV_*` environment: `::test_gov_launch_accepts_a_ticket_named_by_its_wbs_id_and_its_session_is_refused_ts_tests`, `::test_gov_launch_by_wbs_id_of_a_measured_ticket_hands_on_a_ticket_the_guard_measures` (the launch starts one session and hands on `GOV_TICKET=<wbs_id>`; the guard is then asked with it) | `gov launch engineer W2-95` already starts and hands on `GOV_TICKET=W2-95`, but the guard does not resolve a WBS id to its ticket: it allows the engineer T's tests and the measured session the hidden part. |
| 4. Secrets by the repository's credential names: `*.env` at any depth, any file under a `.secrets` folder at any depth | `::test_a_credential_file_is_refused` (`deepseek.env`, `services/api/provider.env`, `.secrets/token.txt`, `ops/deploy/.secrets/api.json` × Read, `cat`, `cp` × engineer, auditor); `::test_every_role_is_refused_each_credential_file_by_the_read_tool` (6 roles); allowed: `::test_the_neighbours_of_credential_files_are_readable` (`docs/provider.env.md`, `docs/secrets/README.md`). A search from above is not asserted (the owner's) | The guard's name rule covers `.env` and `.env.<anything>`, not a name ending in `.env`, and no `.secrets` folder: every such read is allowed. The neighbours pass. |
| 5. No write rule widens: writes naming the held-out list or `.claude/settings.json` stay refused to the engineer, the test designer and research | `::test_a_write_to_the_held_out_list_or_the_settings_file_stays_refused` (`dd of=`, `truncate -s 0`, `sort -o`, `rsync`, `patch`, `git checkout --`, `git restore` × 2 files × 3 roles); allowed: `::test_reading_the_held_out_list_or_the_settings_file_stays_allowed` (Read, `cat`) | Each write is allowed. On the base (`git show w2/integrate:src/gov/guard/protected.py`, `_command_reads`) a word of a Bash command that took in either file was a read refused to every role unless it was a write target of its own command, which the allow-list then refused for these roles: opening the reads let through every write the write extractor does not know. The reads pass. |

Readings the review cases take:

- "**Untyped**" is a subagent whose `agent_type` is `general-purpose` (the type the harness sends for an Agent call
  that names none). A call with `agent_id` and no `agent_type` is not asserted.
- The run-time forms of item 1 are asserted at the guard only (the guard is asked; nothing runs). An engineer
  session's `git ls-files | xargs grep` also takes in the fixture's stand-in secrets: it is allowed to the sessions
  with no protected part, because a search from above a secret is not refused for its sake (DEC-820 (a)).
- Item 3's launch reads `GOV_TICKET` from the settings' `env` block when it is there, else from the process
  environment the stand-in CLI records (W1-46's rule, DEC-183).

## The narrow extra round (sixth round, after the implementation; DEC-880 item 1, P-W2-58-4 (a))

The second review found two behaviours the suite missed. The ticket file states them as its last two success KPI
lines (DEC-880). The cases are in `test_w2_58_tilde_and_test_runs.py`. They were written by a fresh test designer who
did not read the implementation: only the guard's answers were used. No existing case changed. The test count goes
from 754 to 808 (54 added: 21 red, 33 green). The 5 `local_only` cases are unchanged.

**How `~` is set up.** The guard is run as a program (`w2_58_support.ask_guard`), as in every other case. Its `HOME` is
the test's temporary `home/` folder (`w2_58_support.base_environment`). The fixture project lies inside it, at
`<tmp-home>/gov-os-worktrees/W2-95`, so `~/gov-os-worktrees/W2-95/<path>` and the absolute
`<tmp-home>/gov-os-worktrees/W2-95/<path>` name the same file. The stand-in secret is `<tmp-home>/.ssh/id_ed25519`,
made by the fixture. No real home folder is named. Each case of item 1 asks the guard for **both spellings** of the
same file and asserts both get the case's answer. A failure message shows what the other spelling got.

| Behaviour | Tests | Red today because |
|---|---|---|
| 1. A path with a leading `~` is judged as its expanded form: (a) to (d) refuse it as they refuse the absolute path | `::test_read_judges_a_tilde_path_as_its_absolute_path` (refused: (c) the engineer on T × T's test file; (c) the test designer on T × `src/app/main.py`, `src/app/added.py`; (d) measured by role, by ticket × the hidden file; (a) engineer, auditor × `~/.ssh/id_ed25519`, and × a `.env` file. Allowed: the engineer's own code, the test designer's unchanged code, the visible part, the auditor × T's test); `::test_grep_judges_a_tilde_path_as_its_absolute_path` (refused: the engineer with path T's acceptance folder and path the project root `~/gov-os-worktrees/W2-95`; the test designer with path `src/app`; measured by ticket with path the hidden folder; the engineer with path `~/.ssh/id_ed25519` and `.env`. Allowed: the engineer in `src`, the test designer in `src/other`, measured in the visible folder); `::test_glob_judges_a_tilde_path_as_its_absolute_path` (refused: the engineer, Glob `*` in T's acceptance folder and pattern `<folder>/*` with no path; measured by role and by ticket, Glob `*` in the hidden folder. Allowed: the engineer in `src/app`, measured in the visible folder); `::test_bash_judges_a_tilde_path_as_its_absolute_path` (refused: `cat` of T's test (engineer), `grep -rn … src/app` (test designer), `cat` of the hidden file (measured by ticket), `cat ~/.ssh/id_ed25519` (engineer, auditor), `cat` of `.env`. Allowed: `cat` of own code, `cat` of unchanged code) | 16 red: the Read, Grep and Glob refusals of (a) under `~/.ssh`, (c) and (d). The absolute spelling is refused and the `~` spelling is allowed (`decision=allow`): the guard does not expand `~` for the file tools. Green: Read and Grep of `.env` by `~` (the name rule matches the file's name, whatever its folder); every allowed case (the `~` spelling, not taken as the protected file, is allowed as before); every Bash case (the guard already expands `~` in a command's words). |
| 1. Each write rule judges a `~` path as the absolute path | `::test_write_judges_a_tilde_path_as_its_absolute_path`, `::test_edit_judges_a_tilde_path_as_its_absolute_path` (the engineer on T, allowed paths `src/app/**`: refused T's test file, `governance/project/held-out.yaml`, `.claude/settings.json`, `docs/notes.md` (outside); allowed `src/app/main.py` (inside)) | 2 red: Write and Edit of `~/…/src/app/main.py` are refused, while the absolute path is allowed. The guard joins the unexpanded `~/…` to the project folder (`<project>/~/gov-os-worktrees/W2-95/src/app/main.py`), which is outside the allowed paths. The four refusals are green today, but only because of that join: the `~` path is refused, not judged as its absolute path. They hold the "no write rule widens" half once `~` is expanded. |
| 2. The engineer runs its own tests with `python3 -B -m pytest`, `python3 -m coverage run -m pytest`, `coverage run -m pytest`, as with plain `python3 -m pytest`, and still cannot read their source | `::test_the_engineer_runs_its_tests_with_interpreter_flags_or_under_coverage` (each form, and the plain run in the same case); `::test_the_engineer_still_cannot_read_its_tests_source` (Read, `cat`); `::test_a_test_run_joined_with_a_read_of_the_source_is_refused` (plain run `; cat`, `python3 -B …; cat`, `python3 -m coverage run … && cat`, `coverage run …; head -n 5`) | 3 red: each flagged or coverage run is refused with "the call reads the ticket's acceptance tests … (DEC-820 (c))", while the plain run is allowed. The source and joined cases are green today; they hold the "still cannot read their source" half. |

Readings these cases take:

- **Glob "a pattern under it"** is the folder's full `~` path with `/*` and no `path`. The absolute twin of that pattern
  is refused today.
- **The project-root Grep** (`~/gov-os-worktrees/W2-95`) is item 3's root search: it takes in T's acceptance folder, so
  it is refused to the engineer on T, as the absolute project folder is.
- **Edit's twin of "inside the allowed paths"** is an existing file (`src/app/main.py`). Write's is the same file, so
  that one target serves both tools.

### The live cases

Each live case starts a real session through `gov launch` (the CLI at `~/.local/bin/claude`, the caller's own
credentials, `--model haiku`, at most 6 turns, Bash only) in a fixture project built from scratch
(`w2_58_support.make_project`, with `w2/integrate` as T's base). The session runs one probe script,
`.gov-runtime/scratch/w2-58/probe.sh`, which writes the commands' output there. The test reads those files from
outside. A live case is skipped when `bwrap`, `socat` or `~/.local/bin/claude` is missing (W1-46's conditions). It
fails with "did not run the probe to its end" when the session could not run (no network to the model's API).
Each session runs once per module, and its sandbox, HOME and project are temporary.

A launched test designer cannot run them, because its sandbox refuses the API host. In the designer's run they ended
with `API Error: Couldn't connect through your proxy (ERR_PROXY_TUNNEL)` (2 failed, 3 errors at setup). **The ticket
lead runs them red from an unsandboxed session**, from this worktree:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/acceptance/W2-58/test_w2_58_launched_sessions.py -m local_only -q -p no:cacheprovider -rs

About 2 to 4 minutes per session. Leave them out of any other run with `-m "not local_only"`.

## How the tests exercise this worktree's code

Run from this worktree with `PYTHONPATH` set per command:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests/acceptance/W2-58 -q -p no:cacheprovider -rs

Every child process (the guard, `gov launch`, the helper) gets `PYTHONPATH` from `w2_58_support.python_path()`: the
runner's own value, else the `src/` of the worktree that holds this suite (DEC-732). The guard file run is the
kernel template's, copied from this worktree. `test_w2_58_code_under_test.py` shows which `gov` a child imports.
