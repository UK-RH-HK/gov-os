# W2-56 acceptance tests: `gov launch` usable for every worker

Ticket DAEO-wnnz (W2-56), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI lines,
before any implementation, reading only the integrated code (DEC-963).

- **The first half (DEC-1099 (1)),** base `3e41b223ab86`: only the tests whose outcome was the same under set-up A
  or B of the sandbox experiment.
- **The second half (DEC-1112 (1)),** on integrate merged at `ca9c3c580`: the owner chose the path-map guard alone,
  with today's launcher sandbox for workers unchanged (not generated from the path map; set-up B a Wave 3 row). The
  lines the first half held back are tested now: S1's sandboxed part, S2, S3, S8, S9, S11 (W2-145's form), S13, F1,
  F2's sandbox refusals, F4, F5, S7's lock failure; S10 is the CTO's measurement. The section "The second half: what
  this round did with each line" replaces the first half's "After the experiment" table.

The KPI lines are numbered in the ticket's order: S1 to S15 (success), F1 to F6 (failure).

## How they run

    env PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-56 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

No GPU, model, network, real `claude` session or real code-graph daemon. About 3 minutes; the signal cases wait up
to the launcher's END_WAIT_S (5 s) and a margin each.

- **W2-20's resource gate** (merged into integrate after the first half) is shut in a planted `HOME` (no
  `gate.json`), and refused every launch of the first half's cases on `ca9c3c580`. Every launch here now passes
  `--gate-override DEC-1112` before `--`, written only to the planted `HOME`'s launch log: the gate is W2-20's, not
  under test here. The real cases keep the machine's own gate (no override).
- **`gov launch`** runs as a child process through gov's console entry point (no install), from a fixture project
  built from scratch under the test's `tmp_path` (`w2_56_support.make_project`: tickets, a `.claude/settings.json`
  that wires the guard, this worktree's own `.gitignore`, git's identity in the repository's own config). `HOME`,
  the launcher's `TMPDIR`, the stand-in's records and the pycache are disjoint folders under `tmp_path`.
- **The stand-in CLI** at `<HOME>/.local/bin/claude` starts no session. It records its arguments, its `--settings`
  value, its whole process environment, cwd, pid, process group and session, then runs the steps of a plan file the
  test writes (plant files, run git, start a grandchild, wait for a file, end with a code or by SIGKILL). The plan's
  path is written into the stand-in itself: it needs nothing from the environment the launcher cleans.
- **S1's suite half** runs `w2_56_daemon_probe.py` (not collected by an ordinary run: no `test_` prefix) as two
  pytest sessions of its own from the repository's root, so every `conftest.py` on the way applies, with the
  caller's PATH and a stand-in code-graph tool that records each `CBM_RUNTIME_DIR` it is given.

## The interface these tests assume (for the engineer)

- **A refusal** exits non-zero, its output (stdout or stderr) says `LAUNCH_REFUSED` and names the refused argument
  as written before any `=` (for example `--mcp-config`), starts no session and leaves no `gov-launch-*` folder in
  the launcher's temp root. The refused arguments are refused in every position after `--`, alone, with a spaced
  value and in the `=` form; a prompt that only names one inside a longer word list is no argument and starts.
- **The environment** the launcher passes to the CLI process, and the `env` block of `--settings`: PATH (every
  entry of the parent's kept), HOME, LANG, LC_ALL, USER and LOGNAME as the parent's; TMPDIR and CLAUDE_CODE_TMPDIR
  one folder, the launcher's own, not the parent's TMPDIR; GOV_ROLE and GOV_TICKET, where present, the launched
  role and ticket (in `--settings` they must be, as today); no other parent CLAUDE* or GOV* variable, no
  PYTHONPATH, and no parent value under any other name. A parent variable that is none of the listed kinds does not
  pass either (`test_s5_an_unrelated_parent_variable_is_not_passed`: S5 read as the list of what passes). No test
  sets a sign-in variable.
- **The start lock** (or another way, S7) lets three launches made at once from three worktrees of one repository
  all start, lets their sessions run at the same time (a lock held for a session's whole life fails the test after
  25 s) and is gone afterwards (a fourth launch starts).
- **Signals:** the launcher, sent SIGTERM, SIGINT or SIGHUP at its own pid, ends the session's whole process group
  (a grandchild of the CLI is gone within END_WAIT_S + 5 s; one that ignores the signal is gone after the kill
  that follows END_WAIT_S), and still ends with 130 (DEC-392).
- **The session's temp folder** (its TMPDIR) is gone after every ending (exit 0, exit 3, the CLI killed by SIGKILL,
  each ending signal, a CLI that cannot be started), even when it holds folders its owner may not write (mode 0500,
  as a module cache leaves them), a fifo and a link to a file outside (removed as a link; the target is untouched).
- **Placeholders:** the names in `w2_56_support.PLACEHOLDERS`, planted as empty files while a session runs, are
  neither staged nor committed by `git add -A` or `git add .` and `git commit`, both by the worker inside the
  session (its environment) and by the caller in the same worktree while the session runs (the caller's
  environment); an ordinary new file beside them is committed, and so is `docs/gitconfig-notes.md`.
- **S1's suite half** holds in a plain `python3 -m pytest` session started at the repository's root (a conftest or
  the code index itself), not only under a runner: in a suite other than W1-16 and W1-20 `codebase-memory-mcp` is
  not on PATH at test time; the daemon folders of one session lie in one folder of its own, apart from another
  session's, gone when the session ends, and each is short enough for the tool's socket (107 bytes, DEC-338).
- **The template:** `template/governance/kernel/settings.json`'s `permissions.allow` is exactly
  `["Bash(gov launch:*)"]`, and its hooks stay.

### The second half's interface (DEC-1112 (1))

- **The sandbox block** of a worker's `--settings` (every worker role; a path entry is read with one leading `/`,
  so today's `//<absolute path>` and `/<absolute path>` are the same):
  - `sandbox` keys only from today's: `enabled` (true), `failIfUnavailable` (true), `allowUnsandboxedCommands`
    (false), `network`, `filesystem`; never `excludedCommands`, `enableWeakerNestedSandbox` or any other key.
  - `network` keys only `strictAllowlist` (true), `allowedDomains` (today's: empty, the research allowlist for
    research) and `allowUnixSockets`: exactly one entry, `<HOME>/.cache/gov-os/rerank.sock`, where `HOME` is the
    launcher's and the rest is `gov.retrieval.rerank`'s `CACHE_REL` and `SOCKET` (the service's own setting); no
    pattern, never the folder. No `allowAllUnixSockets`, `allowLocalBinding` or port key.
  - `filesystem` keys only `allowWrite` (and the narrowing `denyWrite`, `denyRead`). `allowWrite`: the session's
    temp folder (the `TMPDIR` the CLI is handed), exactly one run folder under `<HOME>/gov-os-runs`, and **S11's
    one log file** `<HOME>/.cache/gov-os/rerank.log` (`CACHE_REL` and `LOG`), nothing else: no entry from the
    ticket's allowed paths, none in the worktree, never `/tmp/gov-cbm-<uid>`. The settings are the same for two
    tickets whose allowed paths differ (but for the two folders), and name none of the allowed paths.
  - `permissions.deny` keeps today's literal rules: `Edit(//<root>/.gov-runtime/<name>)` for each entry of
    `.gov-runtime/` but `scratch` that exists at launch, none for `scratch`, and `Edit(//<root>/tests/acceptance)`
    for every role but the test designer.
- **Links (fail open if followed):** a `rerank.log` that is a link puts neither the link nor its target on the write
  list (and the target is untouched); a `rerank.sock` that is a link allows neither. The launch may refuse instead.
- **S11 (choice: one log file):** the log is a regular file when the session starts (the launcher makes it if it is
  missing: the sandbox cannot bind a file that is not there). A search in the session that the service does not
  answer leaves one FALLBACK line that `gov.retrieval.rerank.status()` (what `gov status` shows as `reranker`)
  counts. The decision package D-11 weighs the other way.
- **`sandbox_faults`:** `from gov.launch.launcher import sandbox_faults` still works; `sandbox_faults(settings)`
  returns a list of reasons, empty for the settings the launcher built, and non-empty for each of: `enabled` false,
  `failIfUnavailable` false, `allowUnsandboxedCommands` true, `strictAllowlist` false, `excludedCommands`,
  `allowAllUnixSockets`, a second Unix socket, another socket in the reranker's place, a socket pattern, the socket's
  folder, `allowLocalBinding`, `httpProxyPort`, `enableWeakerNestedSandbox`. It is called in a process whose `HOME`
  is the launcher's (the reranker's socket is read from it).
- **The guard** (`template/governance/kernel/hooks/pretooluse.py`, copied into the fixture project, event JSON on
  stdin, `GOV_ROLE` and `GOV_TICKET` set): for every worker role, a `Write` or `Edit` outside the ticket's paths and a
  Bash write it names (`>`, `tee`, `cp`, `touch`, `mv`, `sed -i`, a path in another worktree) are refused; a write
  inside each role's scope is allowed. A name pattern `tests/unit/test_batch*` lets `tests/unit/test_batch_one.py`
  through and refuses `tests/unit/test_other.py`, `tests/unit/sub/test_batch_four.py` and `tests/test_batch_five.py`
  (one `*` holds within one folder). A script's write the guard cannot name is the gap the CIT-E names: not tested.
- **S1, the daemon's place:** `gov.codeintel.daemon_dir(root)` stays public and names the daemon folder of `root` as
  the calling process sees it. In a launched session, with `TMPDIR` and `CLAUDE_CODE_TMPDIR` set to
  `<session temp>/claude-<uid>` (as the CLI sets them for its commands; seen in a launched session on 2026-11-09),
  and with `TMPDIR` a folder deeper under that (as a test session inside sets it), it lies under the session's temp
  folder, and with the launcher's temp root taken as `/tmp` the folder plus the tool's 50-byte socket tail is at most
  107 bytes. W1-27's W2-67 cases read the place through `daemon_dir` and through the `CBM_RUNTIME_DIR` the code index
  hands the tool (D-2's revision).
- **The stand-in's `run` step** (added to `w2_56_support`): runs a command with the session's own environment and
  the step's overrides (`{tmpdir}`, `{cwd}`, `{uid}` filled), recording its exit code and output.
- **The real cases:** skipped unless `GOV_W2_56_REAL=1`; `GOV_W2_56_REAL_MODEL` names the model (default `haiku`,
  empty for no `--model`). They use the real `HOME` and `~/.local/bin/claude`, and need a machine whose resource
  gate is open.

## KPI lines, tests, and the outcome on `w2/integrate`

**The second half, on `ca9c3c580`** (integrate merged in), the whole folder in the launch sandbox through the heavy
slot with the mandated exclusion (`-m "not local_only" -k "not real and not green_here and not time_limit"`, which
leaves out the four `real_sandbox` cases): **256 run, 123 failed, 132 passed, 1 skipped** (217 s). The first half's
157 give their earlier 99 failed and 58 passed once the gate is passed (above); the second half's 99 give 24 failed,
74 passed and 1 skipped (the planted-service case: this sandbox refuses Unix sockets). Every new red fails on its own
label: S1 (`/tmp/gov-cbm-1000/…`, not under the session's temp folder), S8 (no socket allowed, `[]`), S9 (eight
widenings `sandbox_faults` accepts), S11 (the log not on the write list).

`gov accept W2-56` (no exclusion: the real cases skip without `GOV_W2_56_REAL`) reads 20 lines, 0 unmapped cases,
132 passed, 123 failed, 5 skipped (exit 3). Passing on integrate: S2, S3, S7, F1, F2 (each a line that says
today's behaviour stays: their cases are guards, red only if it changes). Failing: S1 (5/9/1 passed/failed/skipped),
S4 (0/3), S5 (10/28), S6 (2/56), S8 (0/6/1), S9 (15/8/1), S11 (1/5), S12 (3/6), S14 (1/1), S15 (4/2), F3 (3/30), F4
(11/8/1), F5 (1/5/1), F6 (0/1) on their labels, and S13 (0/0/1), whose one case is a real case and skips here (the
CTO's). Passing lines: S2 36/0/1, S3 8/0, S7 2/0/1, F1 27/0, F2 43/0. S10 is unmapped by design (`—`, the CTO's
measurement).

**The first half, on `3e41b223ab86`:** run in the launch sandbox through the heavy slot: **157 tests, 99 failed, 58
passed** (95 s). Every red fails on
the label its KPI line names; none fails on a premise. Where the run was in this sandbox matters for S1 only: the
code index's daemon place `/tmp/gov-cbm-1000` is read-only here, so S1's three folder cases are red on that (which is
today's fault: no daemon folder of the session's own); outside a sandbox two of them are red on their own labels and
the length guard is green.

`gov accept W2-56` reads this map: 11 lines (S1, S4, S5, S6, S7, S12, S14, S15, F2, F3, F6), 0 unmapped cases,
58 passed and 99 failed; S7 and F2 pass, the other nine fail (exit 3).

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_56_suite_daemon.py::test_s1_the_code_graph_tool_is_off_path_in_a_suite_other_than_w1_16_and_w1_20` | red | `codebase-memory-mcp` is on PATH in the probe's suite (`~/.local/bin`) |
| S1 | `test_w2_56_suite_daemon.py::test_s1_each_test_session_uses_one_daemon_folder_of_its_own` | red | here: no build reaches the tool (`Read-only file system: '/tmp/gov-cbm-1000/…'`); outside a sandbox: both sessions' folders lie in the shared `/tmp/gov-cbm-<uid>` |
| S1 | `test_w2_56_suite_daemon.py::test_s1_no_daemon_folder_is_left_after_the_test_session_ends` | red | here as above; outside a sandbox the folders stay (nothing removes them) |
| S1 | `test_w2_56_suite_daemon.py::test_s1_guard_each_daemon_folder_is_short_enough_for_the_tools_socket` | red here, green outside a sandbox | guard (DEC-338): here no build reaches the tool; today's folder is 34 bytes |
| S1 | `test_w2_56_session_daemon.py::test_s1_inside_a_launched_session_the_daemon_folder_is_under_the_sessions_temp_folder` | red (5 roles) | `daemon_dir` gives `/tmp/gov-cbm-1000/<16 hex>` for the session's commands and a suite inside, not under the session's temp folder |
| S1 | `test_w2_56_session_daemon.py::test_s1_inside_a_launched_session_the_daemon_folder_leaves_room_for_the_tools_socket` | green (guard, 5 roles) | today's folder is 34 bytes; a folder under the session's temp folder that is too long for the socket (D-12) fails it |
| S1, S13 | `test_w2_56_real_sandbox.py::test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox` | skipped here (real) | the CTO's; expected red today: the suite's build cannot write `/tmp/gov-cbm-<uid>` inside the sandbox |
| S2 | `test_w2_56_sandbox_block.py::test_s2_the_write_list_is_the_temp_folder_the_run_folder_and_at_most_the_reranker_log` | green (guard, 5 roles) | today's list: the temp folder and the run folder; an entry from the allowed paths, the worktree or `/tmp/gov-cbm-<uid>` fails it |
| S2 | `test_w2_56_sandbox_block.py::test_s2_the_literal_deny_rules_for_gov_runtime_and_the_acceptance_tests_stay` | green (guard, 5 roles) | today's literal rules; dropping one fails it |
| S2 | `test_w2_56_guard_scope.py::test_s2_premise_a_write_inside_the_roles_scope_is_allowed` | green (premise, 5 roles) | a guard that refuses everything fails it |
| S2 | `test_w2_56_guard_scope.py::test_s2_the_guard_refuses_a_file_tool_write_outside_the_tickets_paths` | green (guard, 10) | Write and Edit, five roles: the guard refuses today (DEC-820 (4)) |
| S2 | `test_w2_56_guard_scope.py::test_s2_the_guard_refuses_a_bash_write_it_names_outside_the_tickets_paths` | green (guard, 11) | seven forms for the engineer, a redirect for the other four roles |
| S2 | `test_w2_56_real_sandbox.py::test_s2_real_sandbox_a_script_write_into_another_worktree_or_a_denied_name_is_refused` | skipped here (real) | the CTO's; expected green today (the OS refuses both) |
| S3 | `test_w2_56_guard_scope.py::test_s3_a_name_pattern_is_held_by_the_guards_match` | green (guard, 7) | `_match_pattern`: one `*` within a folder |
| S3 | `test_w2_56_sandbox_block.py::test_s3_no_sandbox_entry_is_made_from_any_allowed_path` | green (guard) | the settings are the same for `src/app/**` and for a ticket with `test_batch*` |
| S4 | `test_w2_56_placeholders.py::test_s4_no_placeholder_is_staged_or_committed_inside_the_session` | red (2) | `git add -A` and `git add .` in the session stage all 13 sandbox names (`.bashrc` … `.claude/agents`); the `.gov-runtime/` names are ignored already |
| S4 | `test_w2_56_placeholders.py::test_s4_no_placeholder_is_committed_beside_a_running_session` | red | the caller's `git add -A` beside the running session stages the same 13 |
| S5 | `test_w2_56_environment.py::test_s5_no_parent_claude_gov_or_pythonpath_value_reaches_the_session` | red (5 roles) | every planted CLAUDE*, GOV* and PYTHONPATH value reaches the process environment (`env = {**os.environ, …}`) |
| S5 | `test_w2_56_environment.py::test_s5_each_parent_variable_set_alone_is_kept_from_the_session` | red (22), green (3) | each alone reaches the session; CLAUDE_CODE_TMPDIR, GOV_ROLE and GOV_TICKET are already replaced by the launcher's own |
| S5 | `test_w2_56_environment.py::test_s5_an_unrelated_parent_variable_is_not_passed` | red | an unrelated parent variable passes (S5 read as the list of what passes; see D-3) |
| S5 | `test_w2_56_environment.py::test_s5_the_session_keeps_path_home_the_locale_and_its_identity` | green (guard) | PATH, HOME, LANG, LC_ALL, USER and LOGNAME pass; a cleaning that drops them fails it |
| S5 | `test_w2_56_environment.py::test_s5_tmpdir_and_claude_code_tmpdir_are_the_launchers_own_temp_folder` | green (guard) | both are the session's own folder today |
| S5 | `test_w2_56_environment.py::test_s5_the_launched_role_and_ticket_replace_the_parents` | green (guard, 5 roles) | `--settings` env names the launched role and ticket |
| S6 | `test_w2_56_refused_arguments.py::test_s6_a_new_refused_argument_refuses_the_launch` | red (21) | each of the seven, spaced, `=` and after a prompt, starts a session |
| S6 | `test_w2_56_refused_arguments.py::test_s6_every_worker_role_is_refused_each_new_argument` | red (35) | the same for each of the five worker roles |
| S6 | `test_w2_56_refused_arguments.py::test_s6_guard_arguments_that_are_not_refused_start_the_session` | green (guard, 2) | a prompt naming them, and ordinary arguments, start |
| S6 | — | auditor | the CIT-E's weighing of an accepted-arguments list (lens E R6) is a document, the auditor's |
| S7 | `test_w2_56_start_together.py::test_s7_three_launches_at_once_in_worktrees_sharing_one_git_all_start_run_together_and_commit` | green (guard) | no lock today: all three start, run at once and commit; a lock held for a whole session fails it |
| S7 | `test_w2_56_start_together.py::test_s7_a_launch_after_three_at_once_still_starts` | green (guard) | a lock left behind fails it |
| S7 | `test_w2_56_real_sandbox.py::test_s7_real_sandbox_three_sessions_at_once_in_worktrees_sharing_one_git_start_and_commit` | skipped here (real) | the CTO's: the `.git/*.lock` failure needs bubblewrap |
| S8 | `test_w2_56_sandbox_block.py::test_s8_the_sandbox_block_allows_the_reranker_socket_and_no_other` | red (5 roles) | the block allows no Unix socket (`[]`) |
| S8 | `test_w2_56_sandbox_block.py::test_s8_the_socket_path_follows_the_services_setting_under_another_home` | red | as above, under a HOME with a space |
| S8, F5 | `test_w2_56_session_reranker.py::test_s8_a_search_in_the_launched_session_reaches_the_planted_service_and_is_ranked` | skipped here | this sandbox refuses Unix sockets; outside it expected green (guard: the session's environment keeps what the search needs) |
| S9 | `test_w2_56_sandbox_block.py::test_s9_nothing_else_widens_in_the_sandbox_block` | green (guard, 5 roles) | today's keys and values |
| S9 | `test_w2_56_sandbox_block.py::test_s9_sandbox_faults_accepts_the_built_settings` | green (premise, 5 roles) | a `sandbox_faults` that refuses the built settings fails it |
| S9 | `test_w2_56_sandbox_block.py::test_s9_sandbox_faults_refuses_any_other_change` | red (8), green (5) | today's five refusals hold; all sockets, a second socket, another socket, a pattern, the folder, local binding, a proxy port and a weaker nested sandbox are accepted |
| S9, F4 | `test_w2_56_real_sandbox.py::test_s9_real_sandbox_a_second_unix_socket_is_refused` | skipped here (real) | the CTO's; expected green today (no socket allowed) |
| S10 | — | the CTO | measured outside the sandbox, against the live service (`docs/changes/W2-127-evidence.md`) |
| S11 | `test_w2_56_sandbox_block.py::test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it` | red (5 roles) | the log is not on the write list (D-11's choice) |
| S11, F5 | `test_w2_56_session_reranker.py::test_s11_an_unranked_search_in_the_launched_session_is_counted_where_gov_status_counts` | green (guard) | without the OS's sandbox the line lands in the log; a session environment that sends it elsewhere fails it |
| S12 | `test_w2_56_endings.py::test_s12_an_ending_signal_to_the_launcher_reaches_the_sessions_process_group` | red (3) | SIGTERM, SIGINT, SIGHUP: the launcher signals the CLI's pid alone; its grandchild runs on |
| S12 | `test_w2_56_endings.py::test_s12_a_process_of_the_group_that_ignores_the_ending_signal_is_killed_after_the_wait` | red | the grandchild that ignores SIGTERM still runs 13 s later |
| S12 | `test_w2_56_endings.py::test_s12_the_temp_folder_is_removed_when_the_launcher_is_signalled` | green (guard, 3) | the folder goes on each ending signal today |
| S12, S15 | `test_w2_56_endings.py::test_s15_a_temp_folder_holding_folders_the_owner_may_not_write_is_removed` | red (2) | exit 0 and SIGTERM: `shutil.rmtree` cannot empty a 0500 folder, the folder stays with one line on stderr |
| S13 | `test_w2_56_real_sandbox.py::test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox` | skipped here (real) | as S1's row |
| S14 | `test_w2_56_template.py::test_s14_the_template_carries_one_allow_rule_bash_gov_launch` | red | the template has no `permissions.allow` |
| S14 | `test_w2_56_template.py::test_s14_guard_the_template_keeps_its_hooks` | green (guard) | the PreToolUse hook stays |
| S15 | `test_w2_56_endings.py::test_s15_the_temp_folder_is_removed_whatever_the_sessions_exit` | green (guard, 3) | exit 0, exit 3, killed by SIGKILL: removed today |
| S15 | `test_w2_56_endings.py::test_s15_a_cli_that_cannot_be_started_leaves_no_temp_folder` | green (guard) | removed today |
| F1 | `test_w2_56_sandbox_block.py::test_s2_the_write_list_is_the_temp_folder_the_run_folder_and_at_most_the_reranker_log` | green (guard, 5) | as S2 |
| F1 | `test_w2_56_guard_scope.py::test_s2_the_guard_refuses_a_file_tool_write_outside_the_tickets_paths` | green (guard, 10) | as S2 |
| F1 | `test_w2_56_guard_scope.py::test_s2_the_guard_refuses_a_bash_write_it_names_outside_the_tickets_paths` | green (guard, 11) | as S2 |
| F1 | `test_w2_56_sandbox_block.py::test_f1_a_reranker_log_that_is_a_link_widens_nothing` | green (guard) | no log on the list today; following the link fails it |
| F2 | `test_w2_56_refused_arguments.py::test_f2_todays_refused_argument_still_refuses` | green (guard, 11) | DEC-313's and the other CLI arguments refused today |
| F2 | `test_w2_56_todays_refusals.py::test_f2_todays_refusal_still_refuses` | green (guard, 18) | tickets, roles, repository settings, held-out list, evaluation sets, store, research allowlist and folder |
| F2 | `test_w2_56_todays_refusals.py::test_f2_a_missing_cli_still_refuses` | green (guard) |  |
| F2 | `test_w2_56_todays_refusals.py::test_f2_a_cli_that_cannot_be_started_still_refuses_and_leaves_no_temp_folder` | green (guard) |  |
| F2 | `test_w2_56_todays_refusals.py::test_f2_premise_the_unchanged_project_starts_every_worker_role` | green (premise, 5) | the fixture project launches |
| F2 | `test_w2_56_sandbox_block.py::test_f2_a_sandbox_that_cannot_be_built_stops_the_session` | green (guard, 5 roles) | `enabled` and `failIfUnavailable` true |
| F2 | `test_w2_56_sandbox_block.py::test_f2_a_repository_settings_file_carrying_a_sandbox_key_still_refuses` | green (guard, 2) | DEC-233 |
| F3 | `test_w2_56_placeholders.py::test_s4_no_placeholder_is_staged_or_committed_inside_the_session` | red (2) | as S4 |
| F3 | `test_w2_56_placeholders.py::test_s4_no_placeholder_is_committed_beside_a_running_session` | red | as S4 |
| F3 | `test_w2_56_environment.py::test_s5_no_parent_claude_gov_or_pythonpath_value_reaches_the_session` | red (5) | as S5 |
| F3 | `test_w2_56_environment.py::test_s5_each_parent_variable_set_alone_is_kept_from_the_session` | red (22), green (3) | as S5 |
| F4 | `test_w2_56_sandbox_block.py::test_s9_nothing_else_widens_in_the_sandbox_block` | green (guard, 5) | as S9 |
| F4 | `test_w2_56_sandbox_block.py::test_f4_a_reranker_socket_path_that_is_a_link_is_not_allowed` | green (guard) | no socket allowed today; allowing a link fails it |
| F4 | `test_w2_56_sandbox_block.py::test_s9_sandbox_faults_refuses_any_other_change` | red (8), green (5) | as S9: all sockets, a second socket, another socket, a socket pattern or folder, local binding and a proxy port pass `sandbox_faults` |
| F5 | `test_w2_56_sandbox_block.py::test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it` | red (5) | as S11 |
| F6 | `test_w2_56_template.py::test_f6_the_template_admits_gov_launch_and_no_raw_claude_launch` | red | no allow rule admits `gov launch …` (D-7 on the line's wording) |

## The second half: what this round did with each line (DEC-1112 (1))

| Line (part) held back by the first half | This round |
|---|---|
| S1: inside a launched, sandboxed worker, the daemon folder under its own temp folder and the suite run there | settings level: `test_w2_56_session_daemon.py` (place and length, five roles); the OS's part: `test_s13_real_sandbox_…` (the suite inside a real session); D-12 on the length budget |
| S2 (changed) | today's write list and literal deny rules from `--settings`; the guard refuses file-tool and named Bash writes outside the ticket's paths, per role (`test_w2_56_guard_scope.py`); the OS's refusal of a script's write into another worktree or a denied name: `test_s2_real_sandbox_…`; the script write inside the worktree is the CIT-E's named gap (the auditor's) |
| S3 (changed) | the guard's match holds `test_batch*` (seven cases); no sandbox entry from any allowed path |
| S7: the failure on a missing `.git/*.lock` source path | `test_s7_real_sandbox_…` (three real sessions at once) |
| S8 | the one socket from the service's setting (settings level, two HOMEs); a search in the session reaches a planted stand-in service; the link edge; D-13 and D-14 |
| S9 | nothing else widens (settings level); `sandbox_faults` refuses 13 changes; a second socket refused by the OS: `test_s9_real_sandbox_…` |
| S10 | no case: the CTO's measurement, outside the sandbox (mapped `—`) |
| S11 (changed to W2-145's form) | interface chosen (D-11: one log file); the log on the write list; an unranked search in the session counted where `gov status` counts |
| S13 | `test_s13_real_sandbox_…`: gov check, gov rebuild and a code-graph suite in a real session, after a rebuild made outside |
| F1 (changed) | as S2, S3 and S11; the log-link edge; `/tmp/gov-cbm-<uid>` never on the list |
| F2: the sandbox's refusals | `enabled` and `failIfUnavailable` true for every role; a sandbox key in either repository settings file still refuses; `sandbox_faults`'s five refusals of today |
| F4 | as S8 and S9; the socket-link edge |
| F5 (changed) | its first half: the planted-service case (and S10); its second half: S11's cases |

## Notes and decisions to take

- **D-1. S1 needs a file outside the engineer's paths, or a change in the code index.** "One daemon folder per test
  session" and "the tool off PATH elsewhere" are a conftest's work (P1-PLAN T-8 names the engineer's conftest);
  `tests/conftest.py` is not in W2-56's paths (a package, as the ticket's note says). The cases hold whichever way:
  they run the probe as a plain pytest session from the root.
- **D-2. Clash with W1-27's W2-67 cases:** `tests/acceptance/W1-27/test_w2_67_codegraph_folders.py`,
  `w2_67_codegraph.py` and `w2_67_codegraph_probe.py` fix `BASE = /tmp/gov-cbm-<uid>`; a moved `DAEMON_BASE` turns
  them red for a reason that is not theirs (a test designer's revision of W1-27, MR-3). `tests/unit/codeintel/
  test_codeintel.py:117` asserts the same place (the engineer's own unit test).
- **D-3. S5's list.** Read as the list of what passes, an unrelated parent variable does not reach the session
  (`test_s5_an_unrelated_parent_variable_is_not_passed`). "What the CLI needs to sign in" is not named: no test sets a
  sign-in variable. If the CLI's sign-in needs a CLAUDE* variable (for example an OAuth token variable), it is the one
  CLAUDE* exception the CIT-E names.
- **D-4. Leads are not driven here.** A lead launch passes the plan's check first; S5's cleaned environment and S6's
  refusals are tested on the five worker roles. `_check_cli_args` already serves leads too today.
- **D-5. S12's kill reaches the group.** A grandchild that ignores the ending signal is taken as still "reached":
  the launcher's kill after END_WAIT_S must reach the group too, not only a leader that already ended.
- **D-6. S11 against W2-145.** W2-145 removes the private fallback S11 counts; S11 and F5 wait for both the
  experiment and W2-145's form.
- **D-7. F6's wording.** "A raw claude launch stays unallowed in the template" is read with DEC-715: the failure is a
  template whose only launch is an unallowed raw `claude`; the test asks that `gov launch …` is admitted and no raw
  `claude` launch is.
- **D-8. Placeholders.** The names are the CLI sandbox's fixed write denials (shell and git start-up files, editor
  folders, the CLI's command and agent folders) and the launcher's literal `.gov-runtime/` prefixes of `scratch`.
  `docs/source`, seen once in W1 (bootstrap.md, row W2-I012), has no known origin and is not planted. A placeholder
  file named `.vscode` is not caught by the ignore line `.vscode/` (folders only). Inside a real sandbox the
  placeholders are character devices; whether `git add -A` then fails on them is for after the experiment.
- **D-9. A launcher killed by SIGKILL** cannot remove its folder; S15's "whatever its exit" is read as the session's
  exit, and the weekly sweep (DEC-902) takes the rest.
- **D-11. S11's interface (choice): one log file on the write list.** (a) `<HOME>/.cache/gov-os/rerank.log` on
  `allowWrite`, made by the launcher if missing, never a link: the count is immediate, the change is W2-56's own
  (`launcher.py`/`sandbox.py`), and the cost is one file a session can also truncate or rewrite (it holds the
  service's REFUSED lines too). (b) The session's lines in its own run or temp folder, carried into `rerank.log` by
  the launcher at the session's end: no widening, but `rerank.py` must write there in a sandbox (outside W2-56's
  paths), the count waits for the end, and a launcher killed by SIGKILL loses them. (c) `gov status` also reads
  the run folders: outside the paths (`gov.status`), and a run folder outlives its session. **Recommendation (a)**,
  confidence medium; the five `test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it` cases are
  (a)'s, the end-to-end count case holds under all three.
- **D-12. S1's daemon folder against the socket's 107 bytes.** The tool's names under its folder take 50 bytes, so
  the daemon folder may hold 57. The CLI hands its commands `TMPDIR=<launcher temp>/claude-<uid>`: for the test
  designer `/tmp/gov-launch-independent-test-designer-XXXXXXXX/claude-1000`, 62 bytes, already past 57 (the
  launcher's folder alone is 50; the auditor 44 and 56, product-spec 37 and 49, the engineer and research 33 and
  45: under `claude-<uid>` only the last three leave room for a folder name). S1's
  sandboxed part is unreachable for the long roles with today's folder name. **Recommendation:** a shorter launcher
  temp folder, keeping the `gov-launch-` prefix the first half's cases and the weekly sweep key on (for example
  `/tmp/gov-launch-XXXXXXXX`, 24 bytes, the role left out of the name or a two-letter code), and the daemon folders
  at the launcher's folder rather than under `claude-<uid>` (found from `CLAUDE_CODE_TMPDIR`, which a test session
  inside does not change). Confidence high on the arithmetic, medium on the remedy. The first half's
  `test_s1_guard_each_daemon_folder_is_short_enough_for_the_tools_socket` meets the same budget inside a sandbox.
- **D-13. S8 on Linux.** The launch sandbox refuses the `socket(AF_UNIX)` call itself (`PermissionError: [Errno 1]`,
  shown in this session), a call that carries no path. Whether the CLI lifts that per path for
  `network.allowUnixSockets` on Linux is not known here; a path-only allow may be macOS's alone. If it is not
  lifted, S8 cannot hold without `allowAllUnixSockets`, which S9 and F4 refuse. **Recommendation:** the CTO runs
  `test_s9_real_sandbox_a_second_unix_socket_is_refused` and S10's measurement before the engineer builds S8; if a
  path-only allow does not work, a DEC-105 choice: apply now with all sockets (against DEC-1035 (2), not
  recommended), defer S8 and F5's first half to a proxied socket in Wave 3, or re-baseline S8 to DEC-1035 (c)
  (unranked, named, counted: S11 holds it). Confidence medium.
- **D-14. `rerank.py` changes a mode before it connects.** `gov.retrieval.rerank._connect` runs
  `folder.chmod(0o700)` on `~/.cache/gov-os` before every connect (`src/gov/retrieval/rerank.py:139-140`). In the
  sandbox that folder is read-only, and a chmod there fails with `EROFS` even when the mode is already 0700 (shown
  in this session on a read-only folder), so a sandboxed search falls back before it tries the allowed socket: S8
  fails even with D-13 settled. `rerank.py` is outside W2-56's paths. **Recommendation:** add those two lines to
  W2-56's paths (chmod only when the mode differs, the folder made only when missing), or a W2-145 follow-up
  before S10 is measured. Confidence high on the refusal.
- **D-10. A launch-time sandbox probe.** If B makes the launcher check that a sandbox can be built (for example by
  running bubblewrap), these cases' stand-in harness needs a revision so the launch still reaches the stand-in.

### The CTO's settled points (2026-11-09)

- **D-11 settled (a):** `<HOME>/.cache/gov-os/rerank.log` on the write list, made by the launcher if missing, never a
  link. The five `test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it` cases stand as written.
- **D-12 settled as recommended:** a shorter launcher temp folder keeping the `gov-launch-` prefix; the daemon folders
  at the launcher's folder, found from `CLAUDE_CODE_TMPDIR`.
- **D-13 measured by the CTO** (2026-11-09, `claude -p` with haiku, a planted Unix socket server): with
  `network.allowUnixSockets: [<the one path>]` the sandboxed command's connect is refused `PermissionError [Errno 1]`,
  exactly as with no allow; with `allowAllUnixSockets: true` it connects. On Linux a one-path allow does not open the
  socket. S8's settings-level form (the one path, nothing wider) is still built: inert on Linux, honoured where the
  CLI supports it. S8's reach and S10 on Linux go to the owner as a DEC-105 choice. The S8 cases stay as written.
- **D-14:** not added to W2-56's paths now (it matters only once a socket can be reached); carried with D-13.

## Files

- `w2_56_support.py`: the fixture project, the stand-in CLI and its plan steps, the launch helpers, the planted
  parent variables (S5) and the placeholder names (S4).
- `w2_56_daemon_probe.py`: the suite S1 runs as a pytest session of its own.
- `test_w2_56_suite_daemon.py` (S1), `test_w2_56_placeholders.py` (S4, F3), `test_w2_56_environment.py` (S5, F3),
  `test_w2_56_refused_arguments.py` (S6, F2), `test_w2_56_start_together.py` (S7), `test_w2_56_endings.py` (S12,
  S15), `test_w2_56_template.py` (S14, F6), `test_w2_56_todays_refusals.py` (F2).
- The second half: `w2_56_sandbox_support.py` (the sandbox block's readers, the reranker's setting and a stand-in
  service, the guard asker, the in-session command step, `sandbox_faults` in a child);
  `test_w2_56_sandbox_block.py` (S2, S3, S8, S9, S11, F1, F2, F4), `test_w2_56_guard_scope.py` (S2, S3, F1),
  `test_w2_56_session_daemon.py` (S1), `test_w2_56_session_reranker.py` (S8, S11, F5),
  `test_w2_56_real_sandbox.py` (S2, S7, S9, S13 in real sessions; skipped unless `GOV_W2_56_REAL=1`).

## The real cases: what each costs and proves

Each starts real `claude -p` sessions (model `haiku` unless `GOV_W2_56_REAL_MODEL` says otherwise) that run one Bash
command; one session is roughly 20-60 s and a few cents of tokens (mostly the cached system prompt). Run them outside
the launch sandbox, with the machine's resource gate open, by
`GOV_W2_56_REAL=1 TMPDIR=$(mktemp -d /tmp/w56r.XXXX) PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-56/test_w2_56_real_sandbox.py`.

**They need a short `TMPDIR`** (for example `/tmp/w56r.XXXX`). The CLI's sandbox makes its bridge sockets under the
temp folder it inherits; under a long `TMPDIR` their paths pass the Unix socket limit (107 bytes) and the sandbox
cannot start ("Failed to create bridge sockets after 5 attempts"), so every case fails for a reason not its own. S9's
planted socket lies in its own short folder under `/tmp` (made and removed by the test), so it does not skip under a
long `TMPDIR` either.

**The CTO's run (2026-11-09, outside the sandbox, `TMPDIR=/tmp/w56r.XXXX`, on integrate's code):**

| Case | Outcome | Reading |
|---|---|---|
| `test_s2_real_sandbox_a_script_write_into_another_worktree_or_a_denied_name_is_refused` | passed | the OS refuses both writes |
| `test_s7_real_sandbox_three_sessions_at_once_in_worktrees_sharing_one_git_start_and_commit` | red, product | in the sandbox the placeholder `.bash_profile` is a character device: `git add -A` fails "can only add regular files" (D-8); kept |
| `test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox` | red, product | `gov rebuild` cannot remove `.gov-runtime/rebuild/stores.json` (read-only); kept |
| `test_s9_real_sandbox_a_second_unix_socket_is_refused` | red, test bug (fixed) | the planted script was `elsewhere/socket.py`, which shadowed Python's `socket` module, so the command exited 1 before it tried to connect. Now `w56_unix_connect_probe.py`, run with `python3 -I`, its socket under a short `/tmp` folder; the claim is unchanged. Not yet re-run |

| Case | Sessions | What it proves that the settings-level cases cannot |
|---|---|---|
| `test_s2_real_sandbox_a_script_write_into_another_worktree_or_a_denied_name_is_refused` | 1 | that the CLI turns today's write list and literal deny rules into the OS's refusal of a script's write (the guard cannot name it) into another worktree and into `tests/acceptance/` |
| `test_s9_real_sandbox_a_second_unix_socket_is_refused` | 1 | that a socket the block does not allow is refused by the OS while the reranker's one is allowed; with S10 it settles D-13 |
| `test_s7_real_sandbox_three_sessions_at_once_in_worktrees_sharing_one_git_start_and_commit` | 3 at once | the `.git/*.lock` source-path failure exists only when bubblewrap binds the lock files |
| `test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox` | 1, plus a `gov rebuild --no-embeddings` outside first | that the daemon folder is writable inside the sandbox, short enough for the real socket, and that the literal deny rules on an existing `.gov-runtime/` leave `gov rebuild` working |

They write what `gov launch` writes under the real `HOME` (a run folder under `~/gov-os-runs`, the registry entry
while each session runs); the fixture's guard is a no-op, so only the OS fences; they never touch the live
reranker's socket.
