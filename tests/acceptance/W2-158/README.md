# W2-158 acceptance tests: `gov check --structural`

Ticket DAEO-8a3f (W2-158), profile STANDARD, class C2. Designed by the independent test designer (MR-3) from the ticket's
KPI lines S1-S5 and F1-F4 and the Interface the lead fixed (the ticket's Interface line and the readings L1-L10, in the
brief td-1); the engineer's work on this ticket was never read. Sources: DEC-1052, DEC-1073, DEC-1119, DEC-1109,
DAEO-q7lk (`gov links`), DAEO-neam.

## How the tests reach the code

Every case runs `python3 -m gov.cli.main check --structural [<base>] [--timeout <s>] --root <planted tree>` in a **child
process** whose `PYTHONPATH` is the `src/` of the working tree these files are in (the first run of a session fails the
test if `gov` would import from anywhere else). Nothing imports `gov` or `gov.check.structural` in the test process (one case
imports `gov.check.command` in a child, to read its two declarations), so a missing option makes the suite red by failing, not
by an import error at collection. Each case is judged by the exit code, the standard output lines (L2, L5, L7), standard error
(L8's reason) and the records the stand-in checks left. The caller's environment is built from scratch (no
`PYTHONDONTWRITEBYTECODE`, so the pass's own setting of it for its children is what is observed; `gov`'s standard input is a
pipe that stays open, so a check that inherited it would see no end of file). Every wait has a bound; `--timeout` is 2 s in
planted cases (`BOUND`), and a timing assertion is "bound + 8 s" (`SLACK_S`), never tight.

## What is planted (all under pytest's `tmp_path`; nothing real is touched except by the one `real` case)

| Planted | How |
|---|---|
| a git tree | `git init`, commits with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, a planted HOME (empty) |
| the declarations | `template/governance/kernel/checks/<id>.yaml` (and `governance/kernel/checks/` for F3) with the five fields id, family, tier, severity, command; the command is `python3 checks/marker.py <records folder> <name> <mode> [<delay>]` |
| the stand-in check `checks/marker.py` | writes `<name>.start.json` (pid, process group, session, start time, working folder, `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE`, the `GIT_*` variables it saw, whether its stdin is at its end, the interpreter) and, when it ends on its own, `<name>.end.json`. Modes: `ok` (sleep a delay, exit 0), `find` (a JSON list of `{"message"}` items, exit 1), `findobj` (`{"findings": [...]}`, exit 1), `first` (two stdout lines, exit 5), `stderr` (one stderr line, exit 7), `na` (`{"not_applicable": true, "reason": ...}`, exit 2), `sleep` (120 s, far past the bound), `grandchild` (starts a grandchild in the same group that sleeps 120 s, records its pid, then sleeps) |
| the records folder | `marks/` next to the tree (outside the tree and the HOME), so the filesystem spy sees only what the pass itself writes |
| the tree's own `gov links` (S4) | stand-in `src/gov/__init__.py`, `src/gov/cli/__init__.py`, `src/gov/cli/main.py`, `src/gov/links/__init__.py`; the `main.py` records its start/end, working folder, `PYTHONPATH`, arguments; writes `.gov-runtime/links/mark`; answers `gov links: 0 new since <rev>, 4 standing (...)` exit 0, or `2 new` plus two finding lines exit 1, or exit 2 with its reason on stderr only, or a first line of another form, or sleeps |
| built-in stand-ins (F3) | `src/gov/check/{schema,graph,claims,mutation,authority,pathmap,audit_validator,skill_validator}.py` and `src/gov/adapters/portability.py`, each recording `builtin-<module>.json` if run as `python3 -m gov.<package>.<module>`: what the reference tool's built-in list would start |
| a program on PATH | `bin/w2158-tool`, which runs the marker (L4: a first word other than `python3` is looked up on PATH) |
| teardown | every `gov` process group started, every recorded check's group, pid and grandchild is sent SIGKILL, then waited for |

## The map (KPI line, cases, expected red reason today)

Each case is named by its full node id (`test_<file>.py::test_<name>`); a parametrised case names the function (every
parameter runs). Today `--structural` is an unrecognised argument of `gov check` (`gov: error: unrecognized arguments:
--structural ...`, exit 2, nothing on stdout), so every case below is red for that reason unless the last column says otherwise.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (eight families, a process of its own each, all at once; one line per family; a stray declaration is no check) | `test_w2_158_run.py::test_s1_eight_families_each_in_a_process_of_its_own_all_at_once_one_line_each` (eight markers sleeping 3 s: eight pids in eight sessions and groups, all started before any ended, whole run under 18 s; eleven lines in L2's order; `index-freshness` never ran; last line says all ok) | exit 2, "unrecognized arguments: --structural" |
| S1 (killed at the bound, the whole group) | `test_w2_158_run.py::test_s1_a_check_past_the_bound_is_killed_at_the_bound_with_what_it_started` (a sleeper and a process with a grandchild at `--timeout 2`: the run ends in 2 s to 10 s, both processes and the grandchild gone) | same |
| S1 (`--timeout` changes the bound) | `test_w2_158_run.py::test_s1_timeout_changes_the_bound` (a 2.5 s check: `--timeout 1` not measured, `--timeout 8` ok), `test_w2_158_run.py::test_s1_a_fraction_of_a_second_is_a_valid_bound` (`--timeout 0.5`) | same |
| S1 (L4: how a declared command runs) | `test_w2_158_run.py::test_s1_a_check_runs_in_the_tree_with_the_environment_l4_states` (cwd the tree, `PYTHONPATH=<tree>/src`, `PYTHONDONTWRITEBYTECODE=1`, no `GIT_*`, stdin at its end, own group, `python3` is gov's interpreter), `test_w2_158_run.py::test_s1_a_first_word_other_than_python3_is_looked_up_on_path`, `test_w2_158_run.py::test_s1_the_tree_is_the_working_directory_when_root_is_not_given` | same |
| S2 (each line as stated) | `test_w2_158_run.py::test_s2_each_state_reads_as_stated` (ok; finding list; stderr-only failure; timed out; no declaration; not applicable; first stdout line; one skill check finding an object), `test_w2_158_run.py::test_s2_more_than_three_findings_show_three_joined_with_a_bar_then_the_number_left`, `test_w2_158_run.py::test_s2_a_very_long_finding_is_shortened_on_the_one_line`, `test_w2_158_run.py::test_s2_a_command_that_cannot_be_started_is_a_notice_naming_it`, `test_w2_158_run.py::test_s2_skills_runs_every_declaration_whose_family_is_exactly_skill_regression`, `test_w2_158_run.py::test_s2_json_changes_nothing_on_standard_output` | same |
| S3 / F1 (exit 0 whatever the checks find) | `test_w2_158_exit.py::test_s3_a_failing_planted_check_gives_exit_0_and_a_notice`, `test_w2_158_exit.py::test_f1_every_check_failing_in_every_way_still_gives_exit_0` | same |
| S3 (exit 2 only when it could not run; the reason on stderr) | `test_w2_158_exit.py::test_s3_a_folder_that_is_no_git_work_tree_gives_exit_2_with_the_reason_on_stderr`, `test_w2_158_exit.py::test_s3_a_path_that_does_not_exist_gives_exit_2`, `test_w2_158_exit.py::test_s3_a_folder_inside_a_work_tree_but_not_its_top_gives_exit_2`, `test_w2_158_exit.py::test_s3_a_work_tree_with_no_commit_gives_exit_2` | exit 2 already, but the stderr is argparse's "unrecognized arguments", not `gov check: structural pass could not run: ...` |
| S3 (usage errors) | `test_w2_158_exit.py::test_s3_a_timeout_that_is_not_a_number_above_zero_is_a_usage_error` (5: `0`, `-1`, `=-3`, `abc`, empty), `test_w2_158_exit.py::test_s3_structural_with_list_is_a_usage_error`, `test_w2_158_exit.py::test_s3_a_base_without_structural_is_a_usage_error` | exit 2 already; red because the error must not be "unrecognized arguments" (an option's own value error or a refused combination never says it) and, for the base case, `--structural <base>` must run |
| S3 (L8: the module's declarations; the plain command as before) | `test_w2_158_exit.py::test_s3_the_module_declares_a_child_exit_code_and_keeps_its_exit_codes` (`CHILD_EXIT_CODE is True`, `EXIT_CODES == {3: "checks failed"}`), `test_w2_158_exit.py::test_s3_check_list_still_lists_the_declarations_as_before` | the first: `CHILD_EXIT_CODE` missing. The second is **green today** by design (guards `--list`) |
| S3 / F1 (no commit, close, landing or launch code calls it) | `test_w2_158_exit.py::test_s3_and_f1_no_commit_close_landing_or_launch_code_calls_the_pass` (text search of `src/gov/close`, `src/gov/launch`, `src/gov/queue` where they exist, at least one must; patterns `gov.check.structural`, `from gov.check import ... structural`, `import structural`, `--structural`, `run_structural`, `check.structural`) | **green today** by design (nothing calls it yet): it guards the code the engineer adds |
| S4 (portability only on a kernel change, or an unresolved base) | `test_w2_158_base.py::test_s4_a_change_under_the_kernels_roles_skills_hooks_or_rulesync_runs_portability` (4 paths), `test_w2_158_base.py::test_s4_a_change_elsewhere_skips_portability_naming_why` (5: docs, src, `roles-old/`, `kernel/checks/`, `.rulesync-old/`), `test_w2_158_base.py::test_s4_a_kernel_change_in_an_earlier_commit_of_the_range_counts`, `test_w2_158_base.py::test_s4_a_change_before_the_base_does_not_count`, `test_w2_158_base.py::test_s4_a_base_may_be_any_git_revision`, `test_w2_158_base.py::test_s4_a_base_that_does_not_resolve_runs_portability` | same |
| S4 (without a base, both left out and named) | `test_w2_158_base.py::test_s4_without_a_base_portability_and_links_are_left_out_and_named` | same |
| S4 (links: ok, NOTICE, cannot run, not measured, no folder; after the others; the mark) | `test_w2_158_base.py::test_s4_links_with_nothing_new_reads_ok_with_the_standing_count_and_ran_after_the_others` (nine started checks, links started after the latest end; its arguments, working folder, `PYTHONPATH`; the mark), `test_w2_158_base.py::test_s4_links_with_new_findings_is_a_notice_with_the_first_findings_and_exit_0`, `test_w2_158_base.py::test_s4_a_links_that_cannot_run_is_a_notice_with_its_last_line`, `test_w2_158_base.py::test_s4_a_links_past_the_bound_is_not_measured`, `test_w2_158_base.py::test_s4_a_tree_without_src_gov_links_reads_skipped_naming_why` | same |
| S5 (a filesystem spy: only links' mark; the index untouched) | `test_w2_158_nothing_else.py::test_s5_a_pass_with_a_base_and_links_writes_only_links_mark_and_leaves_the_index_alone` (path, size, mtime of every file in the tree, `.git` included, and the HOME: the only new file is `.gov-runtime/links/mark`; nothing changed; no `__pycache__`; the index bytes equal, after a tracked file's mtime was moved on so a `git status` taking the optional lock would rewrite it), `test_w2_158_nothing_else.py::test_s5_a_pass_without_a_base_writes_nothing_at_all` | same |
| S5 (the time on this repository; **name has `real`**) | `test_w2_158_nothing_else.py::test_s5_real_pass_on_this_tree_is_bounded` (`gov check --structural HEAD~1 --root <this tree>`, default bound: exit 0, eleven lines, ends within 60 s; prints the measured time for `docs/changes/W2-158-evidence.md`). Left out of the whole-folder run by `-k "not real"`; `gov accept` runs it | same (run alone: exit 2, "unrecognized arguments: --structural HEAD~1") |
| F2 (a timed-out family reads ok or red) | `test_w2_158_run.py::test_f2_a_timed_out_family_is_a_notice_never_ok_and_never_a_failure_exit`, `test_w2_158_run.py::test_f2_every_family_timing_out_together_ends_within_one_bound_and_exits_0`; also `test_w2_158_run.py::test_s1_a_check_past_the_bound_is_killed_at_the_bound_with_what_it_started`, `test_w2_158_run.py::test_s2_each_state_reads_as_stated`, `test_w2_158_base.py::test_s4_a_links_past_the_bound_is_not_measured` | same |
| F3 (a check run that is not the tree's declaration) | `test_w2_158_declared.py::test_f3_the_declared_marker_runs_and_no_built_in_command_does` (only `core-schema` declared, the nine built-in stand-ins present: the marker ran, seven families and portability `skipped (no declaration)`, no stand-in ran, with and without a base), `test_w2_158_declared.py::test_f3_a_tree_with_no_declaration_at_all_reads_every_family_as_skipped`, `test_w2_158_declared.py::test_f3_a_declaration_under_governance_kernel_checks_is_used_when_the_template_layout_has_none_and_the_templates_wins`, `test_w2_158_declared.py::test_f3_a_declaration_that_cannot_be_read_makes_only_its_own_family_a_notice_naming_the_file` (4: unparsable YAML, no command, a non-string command, a list) | same |
| F4 (any change outside the paths) | `test_w2_158_nothing_else.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths` | **green today**: it guards a clean branch (the diff against the merge-base with `w2/integrate` lists only this folder). It judges only this ticket's own branch: on any branch other than `w2/W2-158` and `w2/W2-158-tests` it **skips**, naming why (DECIDED-NOT-DONE row 171) |

## State today (the base: `w2/W2-158-tests` at its claim commit)

60 cases in the whole-folder run (`-k "not real and not green_here and not time_limit"`): **57 red, 3 green**. The 3 green are
guards: F4, the `--list` case and the static search of close, launch and queue. The `real` case (61st) is red when run alone.
Every other red is `--structural` being an unrecognised argument (exit 2 and nothing on stdout), or, for the exit-2 and usage
cases, the missing message form, and for the module case the missing `CHILD_EXIT_CODE`. The folder runs in about 4 s red and
about 40 s against a working command (a throwaway reading of L1-L10 the designer wrote in a scratch copy outside the repository
to show the cases can pass: 59 of the 59 non-`real`, non-F4 cases passed, twice; 24 mutants of it were each caught: sequential
runs, killing the child only, a timeout read as ok, exit 1 on a notice, portability always or on a path-prefix match, no
`PYTHONDONTWRITEBYTECODE`, `GIT_*` kept, stdin inherited, a wrong working folder, a `git status` taking the optional lock, links
run with the others, a built-in fallback, the governance folder before the template one, a substring match of the skills
family, all findings shown, no shortening, `--timeout 0` accepted, a base without `--structural` accepted, 13 sha characters, a
work tree with no commit or a sub-folder accepted, links run with no `src/gov/links/`, a stray file written).

## Readings of the Interface the tests rely on (small points L1-L10 do not fully settle)

- A family's NOTICE text: the findings' text joined with ` | ` in their order, at most three, then `(+k more)` at the end of
  the line; a finding is shortened to far under 3,000 characters (the width is not fixed: the case needs under 1,500 for the
  line); a line break in a finding does not make a second line.
- The last line: `structural pass at <head12>` then free text. With a NOTICE it holds `not a refusal` and names each family
  with a NOTICE (`links` included); with none it holds ` ok` and neither `NOTICE` nor `not a refusal`; both hold a time
  (`<number> s`). A tree where no family ran is not asked what its last line says beyond the start.
- A timed-out family's text holds `not measured` and the declaration's id; a command that cannot be started holds
  `<id> could not run`; any other exit holds `<id> exit <code>: <first line>` (stdout first, else stderr).
- `links:` with new findings starts `links: NOTICE N new` and holds the first finding line (a second is not required);
  a links that cannot run reads `links: NOTICE gov links could not run (exit <code>): <its last line>` (the last line of
  what it printed on stderr, else stdout: the stand-in prints one line on one stream only); `links: ok (0 new since <base>,
  M standing)` repeats the base as it was given, and the stand-in is called with `--since <base>` exactly as given (the cases
  give a full sha).
- With a `<base>` that would run portability but no `adapter-portability` declaration in the tree the line is
  `portability: skipped (no declaration)`. The Interface does not say what a tree with neither a declaration nor a kernel change
  reads; no case asks.
- A declaration file that cannot be read makes `<family>: NOTICE ...` holding the file's name (`core-mutation.yaml`), whatever
  else the line says.
- A root that is a file, a missing path, a sub-folder of a work tree, a plain folder and a work tree with no commit are each
  exit 2 with `gov check: structural pass could not run: ` on stderr and nothing on stdout; usage errors are exit 2 without
  that text (argparse's own).
- The pass makes no write at all in the tree or the HOME beyond links' mark (the stand-ins' own records are outside both),
  and its git reads leave `.git/index` byte-equal.

## Not tested (and why)

The default bound of 50 s (waiting for it would take a minute; the `real` case runs the default bound on this repository, and
`--timeout` is tested at 0.5, 1, 2, 8 and 30 s); the real `gov links` (the cases use the tree's own stand-in, as the Interface
reads, and the `real` case exercises the real one); that the CTO's `land.py` calls the pass after the fact (outside this
repository's product code); behaviour under `kill -STOP` of the pass; a declaration's own `timeout-seconds` being ignored (L1
says it is not used; no case plants one).

## Running

```
env HOME=<repo>/.gov-runtime/scratch/empty-home TMPDIR=<a folder outside the repository> PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=<repo>/src bash <orchestrator>/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-158 -q \
  -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```

No case is marked `local_only`; the exclusion leaves out only `test_s5_real_pass_on_this_tree_is_bounded` (run by
`gov accept`, or alone with `-k real`). F4 needs the ref `w2/integrate` (a worktree of this repository has it), fails naming
that where it does not resolve, and skips off the ticket's own branches.
