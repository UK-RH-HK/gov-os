# W2-157 acceptance tests: the GPU backstop in the product

Ticket DAEO-ozyt (W2-157), profile STANDARD, class C2. Designed by the independent test designer (MR-3) from the
ticket's KPI lines S1-S5 and F1-F4 and the Interface the lead fixed (L1-L9, in the brief); the engineer's work on this
ticket was never read. Sources: DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-1119, DEC-1109.

## How the tests reach the code

Every case runs `python3 -m gov.cli.main resources --backstop <pgid> ... --root <project> --json` in a **child process**
whose `PYTHONPATH` is the `src/` of the working tree these files are in (the first run of a session fails the test
if `gov` would import from anywhere else). Nothing imports `gov` in the test process, so a missing `--backstop` makes
the suite red by failing, not by an import error at collection. Each case is judged by the exit code, the envelope's
`result` (L8, its key set checked exactly), the backstop's log (L6), the inbox item (L7) and the state of the planted
processes in `/proc/<pid>/stat` (`T` is stopped).

The poll period in the planted file is 0.1 s (`gpu_backstop_every_s`), so a case takes about a second. Every wait has a
deadline and ends at once if the command ends first; no bare sleep.

## What is planted (all under pytest's `tmp_path`; nothing real is touched)

| Planted | How |
|---|---|
| `HOME` and `$HOME/.gov-os/machine/gate.json` | a whole valid W2-20 file (the backstop reads none of its other keys) plus `gpu_backstop_limit_mib` 15872, `gpu_backstop_every_s` 0.1, `gpu_backstop_embedders` `[]`, each dated and sourced; a case changes the dict before the start |
| the project (`--root`) | an empty folder; the inbox folder is absent until a trip |
| `nvidia-smi` | a script first on `PATH`: asked exactly `--query-gpu=memory.used,memory.total --format=csv,noheader,nounits` it answers `<used>, <total>` from a planted sequence, one entry per call, the last repeating; asked anything else it prints nothing and exits 0; it records every call (arguments, time). A sequence entry can be gated (it answers only when the test releases it), which holds the watch between two polls so the test can look at the job, or change a log or a server, at a known moment; or fail (exit 9) or print garbage |
| the job and the unrelated process | children started with `start_new_session=True` (each its own group). Same script and same command line, so only the group tells them apart. They catch every catchable signal and record it in `<pid>.signals`; a SIGSTOP shows in the state. Modes: `run`, `child` (a child in the same group), `orphan` (the leader exits, a member keeps the group alive) |
| the embedding servers | small HTTP servers in the test on free ports (never 11434 or 11435) answering `GET /api/ps` from a planted body; every request is recorded; planted logs at `$HOME/.ollama/serve-<port>.log` |
| teardown | SIGCONT then SIGKILL to every group the test started (jobs and the command itself), then a wait; the servers are shut down |

## The map (KPI line, cases, expected red reason today)

Each case is named by its full node id; a parametrised case names the function (every parameter runs). Today
`--backstop` is an unrecognised argument of `gov resources` (exit 2, no envelope), so every case below is red for
that reason unless the last column says otherwise.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (the limit, the pause) | `test_w2_157_limit.py::test_s1_the_job_runs_at_the_first_reading_and_is_stopped_at_the_second` (15,800 then 15,900 MiB: running at the first, `T` at the second, TRIP line holds 15900, start line, one TRIP, nvidia-smi asked exactly twice with L3's arguments) | exit 2, "unrecognized arguments: --backstop" |
| S1 (every 5 s, a configured value) | `test_w2_157_limit.py::test_s1_the_period_is_the_files_value` | same |
| S1 (a missing or malformed limit refuses, naming it) | `test_w2_157_limit.py::test_s1_a_missing_or_malformed_limit_refuses_to_start_naming_it` (12: missing, string, 0, negative, float, boolean, null, bare number, no date, bad date, no source, empty source) | exit 2 instead of exit 1 `RESOURCE_CONFIG_INVALID` |
| S1 (L2: the period and the embedders keys, the file, several faults) | `test_w2_157_limit.py::test_s1_a_missing_or_malformed_period_refuses_to_start_naming_it` (7), `test_w2_157_limit.py::test_s1_a_missing_or_malformed_embedders_value_refuses_to_start_naming_it` (15), `test_w2_157_limit.py::test_s1_every_faulty_key_is_named`, `test_w2_157_limit.py::test_s1_no_gate_file_refuses_to_start_naming_it`, `test_w2_157_limit.py::test_s1_a_gate_file_that_is_not_a_json_object_refuses_to_start_naming_it` (3) | same |
| S2 (a spill) | `test_w2_157_readings.py::test_s2_a_reading_at_total_minus_63_trips_and_names_the_spill`, `test_w2_157_readings.py::test_s2_a_reading_at_total_minus_65_does_not_trip` | exit 2, no envelope |
| S3 (`size_vram` below `size`; the log) | `test_w2_157_embedders.py::test_s3_a_model_with_size_vram_below_size_trips_once_naming_port_model_and_ratio`, `test_w2_157_embedders.py::test_s3_a_partial_offload_line_written_since_the_start_trips_once_naming_the_log`, `test_w2_157_embedders.py::test_s3_a_line_with_n_equal_to_m_does_not_trip`, `test_w2_157_embedders.py::test_s3_only_what_was_appended_since_the_start_counts`, `test_w2_157_embedders.py::test_s3_a_log_missing_at_the_start_counts_from_its_first_byte` | the command ends before the first reading |
| S3 (the ports from the file; no answer is no trip; an unreadable GPU; L5's order) | `test_w2_157_embedders.py::test_s3_every_configured_embedder_is_watched_and_the_partial_one_is_named`, `test_w2_157_embedders.py::test_s3_no_answer_or_a_malformed_one_is_no_trip` (6), `test_w2_157_embedders.py::test_s3_an_embedder_trips_it_even_when_the_gpu_cannot_be_read`, `test_w2_157_embedders.py::test_s3_the_checks_run_in_the_stated_order_and_the_first_reason_trips` (3) | same |
| S4 (only the named groups; a trip's inbox item; the watch ends) | `test_w2_157_groups.py::test_s4_an_unrelated_process_of_the_same_name_is_left_running_after_a_trip`, `test_w2_157_groups.py::test_s4_the_whole_named_group_is_paused_and_a_pid_is_not_a_group`, `test_w2_157_groups.py::test_s4_a_group_whose_leader_has_ended_is_live_while_a_member_runs`, `test_w2_157_groups.py::test_s4_a_trip_writes_one_inbox_item_in_the_stated_form_and_the_watch_has_ended` | exit 2, no envelope |
| S4 (a name that is not a group id above 1: exit 2) | `test_w2_157_groups.py::test_s4_a_value_that_is_not_a_group_id_above_1_is_refused_with_exit_2` (8: `abc`, `1`, `0`, `-5`, `1.5`, `0x10`, `12abc`, empty), `test_w2_157_groups.py::test_s4_one_bad_value_among_good_ones_refuses_the_whole_command`, `test_w2_157_groups.py::test_s4_no_group_named_is_a_usage_error` | exit 2 already, but the message says `--backstop` is unrecognised: the cases require the option's own value error naming the value |
| S4 (a group already ended is skipped and named; a job that ends first) | `test_w2_157_groups.py::test_s4_a_group_already_ended_is_skipped_and_named_while_a_live_one_is_watched`, `test_w2_157_groups.py::test_s4_when_every_named_group_has_already_ended_the_watch_ends_at_once`, `test_w2_157_groups.py::test_s4_a_job_that_ends_first_ends_the_watch_with_a_log_line`, `test_w2_157_groups.py::test_s4_the_watch_goes_on_until_the_last_named_group_has_ended`, `test_w2_157_groups.py::test_s4_a_number_no_group_can_have_is_skipped_not_refused` | exit 2, no envelope |
| S5 (a filesystem spy: only its log; a trip adds only the inbox item) | `test_w2_157_nothing_else.py::test_s5_a_run_with_no_trip_writes_only_its_own_log`, `test_w2_157_nothing_else.py::test_s5_a_trip_writes_only_its_log_and_the_one_inbox_item` | exit 2, no envelope |
| S4 / S1 (L5b, round 2: the backstop's own group is paused last; a job sharing gov's group) | `test_w2_157_own_group.py::test_s4_the_own_group_is_paused_last_after_every_other_group_the_trip_line_and_the_item` (3: the shared group named first, between two other groups, last; every other group stopped, the shared job stopped, gov itself `T`, one TRIP line and one item with the `paused:` line naming all three and the `note:` line, the start line's `; own group <g> named: paused last`, no signal received, an unnamed group untouched; then `kill -CONT -- -<own group>`: exit 0, `tripped: true`, `paused` holding all three, the two other groups still stopped, the shared job running), `test_w2_157_own_group.py::test_s4_a_job_sharing_the_backstops_group_and_a_second_group_named_after_it_are_both_paused` (the review's scene: own group first, one second group after it), `test_w2_157_own_group.py::test_s1_the_own_group_named_alone_is_paused_after_the_trip_line_and_the_item`, `test_w2_157_own_group.py::test_s4_a_group_that_has_ended_is_skipped_beside_the_own_group_which_is_still_paused_last`, `test_w2_157_own_group.py::test_s4_when_the_own_group_is_not_named_it_is_not_paused_and_there_is_no_note` (own group not named: nothing changes) | on the base: exit 2, "unrecognized arguments: --backstop" (the command ends before gov is stopped). On the built code (pauses in the order named, then writes): with the own group first or in the middle the first failure is a named group still running when gov is stopped; with the own group last or alone, no TRIP line in the log when gov is stopped; the last case (own group not named) is expected green |
| F1 (a process outside the named groups paused or signalled) | `test_w2_157_groups.py::test_s4_an_unrelated_process_of_the_same_name_is_left_running_after_a_trip` (identical command line, state not `T`, no signal recorded), `test_w2_157_groups.py::test_f1_a_group_not_named_is_never_signalled_whatever_its_state`, `test_w2_157_groups.py::test_s4_the_whole_named_group_is_paused_and_a_pid_is_not_a_group` (a pid that is no group's id) | exit 2, no envelope |
| F2 (a trip on a reading under every limit, or a spill, a partial embedder or offload not tripping) | `test_w2_157_readings.py::test_f2_the_gpu_reading_gives_its_stated_outcome` (8: 15,800 no; 15,872 no; 15,873 yes; 15,900 yes; total-65 no; total-64 yes; total-63 yes; 0 no), `test_w2_157_readings.py::test_f2_an_embedders_model_gives_its_stated_outcome` (4), `test_w2_157_readings.py::test_f2_a_log_line_gives_its_stated_outcome` (4: 33/33 no; 30/33, 32/33, 0/29 yes), `test_w2_157_readings.py::test_f2_a_partial_offload_already_in_the_log_at_the_start_does_not_trip` | the command ends before it polls |
| F3 (a limit from anywhere but the file) | `test_w2_157_limit.py::test_f3_the_trip_happens_at_the_files_value_only` (12,000 in the file; `LIMIT`, `GPU_BACKSTOP_LIMIT_MIB`, `GOV_GPU_BACKSTOP_LIMIT_MIB` hold 20,000; 11,990 then 12,010), `test_w2_157_limit.py::test_f3_a_reading_between_the_files_limit_and_the_built_in_one_trips`, `test_w2_157_limit.py::test_f3_a_reading_between_the_built_in_limit_and_the_files_does_not_trip`, `test_w2_157_limit.py::test_f3_an_environment_variable_is_never_a_fallback_for_a_missing_limit` (3), `test_w2_157_limit.py::test_f3_the_period_is_not_taken_from_the_environment`, `test_w2_157_limit.py::test_f3_no_option_sets_the_limit_or_the_period` (3: `--gpu-backstop-limit-mib`, `--gpu-backstop-every-s`, `--limit`); a file with the limit missing or malformed refuses, naming it: the S1 refusal cases above | exit 2 and no envelope; the option cases are exit 2 already, but the message must come from the option and not from `--backstop` |
| F4 (any change outside the paths; judged only on `w2/W2-157`) | `test_w2_157_nothing_else.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths`, `test_w2_157_nothing_else.py::test_f4_the_planted_paths_are_outside_and_inside_the_ticket_s_paths`, `test_w2_157_nothing_else.py::test_f4_planted_w2_157_branch_with_a_change_outside_its_paths_fails`, `test_w2_157_nothing_else.py::test_f4_planted_w2_157_branch_with_a_change_inside_its_paths_passes`, `test_w2_157_nothing_else.py::test_f4_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason`, `test_w2_157_nothing_else.py::test_f4_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason`, `test_w2_157_nothing_else.py::test_f4_planted_integrate_branch_itself_is_skipped_with_its_reason` | the real case judges only on the branch `w2/W2-157` (there: the diff against the merge-base with `w2/integrate` lists only `allowed_paths` and this folder, else red, naming the path) and is **skipped, with its reason** (`this is the branch <b>` or `this is a detached HEAD`), on any other branch, the merge queue's candidate merge, `w2/integrate` itself, and where `w2/integrate` or the ticket file is absent (a clone). The six planted cases (one `git init` repository each, branch read from the repository, never the cwd) pass today: they assert the judgement's fail (`w2/W2-157` with `src/gov/resources/slots.py`) or pass (`backstop.py`) or skip (`w2/W2-121c`, a detached `--no-ff` candidate merge, `w2/integrate`). Revised by W2-181 (DAEO-ywb5, DEC-866) after DECIDED-NOT-DONE row 171: it judged every branch against W2-157's own paths |

## State today (the base: `w2/W2-157-tests` at its claim commit)

Round 1 (td-1): 108 red, 1 green (F4, which guards "nothing else changes"; now judged only on `w2/W2-157`, with six planted cases, see its row). Round 2 (td-2) adds the seven cases of `test_w2_157_own_group.py` (L5b), red the same way on the base. Every red is `--backstop` being an unrecognised argument
(the command exits 2 with no envelope, or the case waits for the first reading and sees the command end). The whole
folder runs in about 25 s red and about 40 s against a working command (a throwaway reading of L1-L9 the designer
wrote in a scratch tree to show the cases can pass; ten mutants of it were each caught: `>=` on the limit, the spill
window of 63, the log offset ignored, the limit from the environment, `<=` on `size_vram`, a stray file written, `N<=M`,
a pid signalled instead of a group, the watch going on after a trip).

## Readings of the Interface the tests rely on (small points L1-L9 do not fully settle)

- The TRIP reason's text is free except: the spill's reason contains `spill` (any case); an `/api/ps` reason names the
  port, the model and `size_vram/size` as written (`500/1000`); a log reason names the log's path and the matched text;
  when two conditions hold at once the first of L5's order is the reason and the later one is not named.
- The log's lines are L6's, matched by regular expression with a timestamp; the start line's `every` is any number text.
- `nvidia-smi` is asked once per poll with L3's exact arguments (a case counts the calls: one call for a trip at the
  first poll, two for a trip at the second). A start that asks it once more before the first poll would fail those cases.
- The result's keys are exactly L8's seven; `reading` is checked only on a trip (a pair of integers, or `null` when no
  reading could be had); on no trip `reason` and `inbox_item` are null, `paused` empty.
- The inbox item's first three lines and the `paused:` and `skipped (already ended):` lines are exact (in that order);
  the `resume:` and `stop:` lines are compared as a set (any order after the fifth line).
- A value above any pid limit (99999999999) is a valid decimal integer above 1 (L1): it is a group that has ended
  (skipped and named), not a usage error.
- A group named by a pid that is not a group's id (a child's own pid) names no group: it is skipped.
- When every named group has ended the watch ends before any GPU reading is asked; the cases do not count the calls then.
- A group that ends during the watch and is neither paused nor skipped at a later trip is not tested (L5, L7 leave it open).

## L5b: how the own-group cases work (round 2)

L5b: when the process group of `gov` itself is among the named groups, every other live named group is paused first (in
the order named), then the TRIP line and the one inbox item are written, then the own group last of all (which stops gov
too); after `kill -CONT -- -<own group>` the command ends (exit 0, `tripped: true`, `paused` holding every paused group,
the own one included). Each case starts a new session with `sh -c '<job> & echo $! > <file>; exec python3 -m gov.cli.main
resources --backstop $$ <other groups> ...'`, so gov, the shell's pid and the job share the group `$$`; the other jobs are
in groups of their own. The stand-in `nvidia-smi` trips at its first reading, which is held (gated) until the shared job
has installed its handlers. The proof of the order needs no race: once gov is seen stopped (`T`) it can do nothing more,
so every other named group stopped (a 5 s grace for the signal to take effect in the target), the TRIP line and the item
in place, and no catchable signal received, were all done before the own group was paused. Readings the cases rely on:
the `paused:` line, the TRIP line's groups and the result's `paused` are compared as sets (L5b does not fix their order);
the `note:` line is exact and may stand anywhere after the fifth line; the start line is L6's with the suffix at its end.

## Not tested (and why)

The 3 s timeout of an `/api/ps` request (a slow case); that the request goes without a proxy; that the inbox item is
renamed into place (only that no dot-named file is left); a log rotated or truncated while the watch runs; that
`--init-config` writes exactly W2-20's frozen key set and that a gate file without the three keys still opens the gate
(`tests/acceptance/W2-20/test_w2_20_config.py` and the other W2-20 cases freeze both and stay in the engineer's and the
CTO's scoped runs); the real GPU, the real servers and the reranker (never started); a hang of `nvidia-smi` itself.

## Running

```
env HOME=<repo>/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<repo>/src \
  python3 -m pytest tests/acceptance/W2-157 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit"
```

No case is marked `local_only` and none is named with `real`, `green_here` or `time_limit`, so the exclusion leaves out
nothing of this folder. F4 needs the ref `w2/integrate` (a worktree of this repository has it) and the ticket file; where either is absent
(a plain clone) it is skipped, naming that, and on any branch but `w2/W2-157` it is skipped with the branch found.
