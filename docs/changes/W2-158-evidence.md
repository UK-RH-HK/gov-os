# W2-158 evidence: `gov check --structural` (DAEO-8a3f, engineer)

## What was built

- `src/gov/check/structural.py` (about 280 lines with its docstring): `run_structural(tree, base, timeout, out) -> int`.
  Reads the tree's own declarations, starts every declared command at once (a thread and a process group each),
  kills a group at the bound, prints one line per family, then portability, links and the last line.
- `src/gov/check/command.py`: `--structural`, `--timeout <s>` and the optional positional `<base>`; the module
  docstring names the option; `CHILD_EXIT_CODE = True`; `EXIT_CODES` keeps `{3: "checks failed"}`. `--list` and the
  plain `gov check` take the same path as before.
- `tests/unit/check/test_w2_158_structural.py`: 44 cases (29 in a default run: `tests/optin-lifted-breadth.txt`
  keeps one row per parametrised function; `--optin=breadth` runs all 44), planted git trees with stand-in commands.

## KPI lines and the unit tests that show them

| line | tests (all in `tests/unit/check/test_w2_158_structural.py`) |
|---|---|
| S1 eight processes at once, each within the bound | `test_s1_eight_processes_start_together_and_one_line_per_family` (each stand-in waits until all eight have started: it fails if they run in sequence); `test_s1_s2_a_command_past_the_bound_is_killed_with_its_group_and_reads_not_measured` (a grandchild dies with the group; checked to fail when only the child is killed); `test_fractional_bound_is_named_as_given`; `test_l4_interpreter_environment_cwd_and_stdin` |
| S2 the lines and the last line | `test_output_order_and_last_line`; `test_s2_not_applicable_finding_and_plain_exit`; `test_s2_at_most_three_findings_and_each_shortened`; the timed-out line in the S1 test; `test_skills_family_is_every_declaration_of_the_skill_regression_family`; `test_a_file_that_cannot_be_read_makes_only_its_own_family_a_notice`; `test_a_command_that_cannot_be_started_is_a_notice` |
| S3 exit 0 whatever is found, 2 only when it cannot run, nothing decides on it | `test_s3_a_failing_check_gives_exit_0_and_a_notice_through_the_command_line` (through `gov.cli.main.main`: no envelope); `test_s3_json_flag_changes_nothing`; `test_s3_exit_2_when_the_pass_cannot_run` (no folder, not git, a subfolder of a work tree, no HEAD); `test_l1_a_bad_timeout_is_argparses_usage_error`; `test_l1_other_usage_errors_exit_2_with_nothing_on_stdout`; `test_s3_no_close_launch_or_queue_code_calls_it` |
| S4 portability and links with a base | `test_s4_portability_runs_only_when_the_change_touches_the_kernel` (roles, skills, hooks, `.rulesync/` run; docs and `checks/` do not); `test_s4_portability_runs_when_the_base_does_not_resolve_and_is_left_out_without_a_base`; `test_s4_portability_without_declaration_is_skipped`; `test_s4_links_clean_and_called_as_the_ticket_says`; `test_s4_links_new_findings_are_a_notice_with_the_first_lines`; `test_s4_links_that_cannot_run_or_time_out`; `test_s4_links_skipped_without_the_folder_or_without_a_base` |
| S5 bounded, cheap, writes nothing else | the measurement below; `test_s5_the_pass_writes_no_file_and_leaves_the_index_alone` (file sizes and mtimes of the whole planted tree including `.git`, the index bytes, no `__pycache__`) |
| F1 no refusal, no non-zero exit | the S3 tests above (exit 0 with a NOTICE; killed check gives exit 0) |
| F2 a timed-out family never ok or red | the S1 timeout test and `test_fractional_bound_is_named_as_given` (`NOTICE not measured`) |
| F3 only the tree's own declarations | `test_f3_marker_command_runs_and_a_family_without_declaration_is_skipped`; `test_f3_no_builtin_command_in_the_module`; `test_declarations_of_the_installed_layout_are_read_and_the_template_one_wins` |
| F4 no change outside the paths | `test_f4_the_pass_is_two_product_files_only`; `git diff --name-only c8e9c236c..HEAD` lists `src/gov/check/command.py`, `src/gov/check/structural.py`, `tests/unit/check/test_w2_158_structural.py` (and this file once committed) |

## The lead's readings L1-L10 as applied

- L1: `--root` is the tree (the command line's own); `--timeout` is a float above 0 and finite (`nan`, `inf`, 0, negative
  and text are argparse's usage errors, exit 2); default 50, the bound of each check and of links alike (a
  declaration's `timeout-seconds` is not read). `--structural` with `--list`, a `<base>` or `--timeout` without
  `--structural` are usage errors: `run` writes `gov check: error: ...` to stderr and returns 2 (it cannot reach the
  parser from `run`; see unresolved 1).
- L2: lines as stated, in order; the family text carries no count prefix. The last line is
  `structural pass at <head12>: NOTICE in <families> (<k> of <n> ran families ok), <t> s; a notice, not a refusal` or
  `structural pass at <head12>: all <n> ran families ok, <t> s`; `n` counts the families that ran (a skipped one is
  not counted).
- L3: lookup by file stem and by `id`, template layout first, then `governance/kernel/checks/`; skills is every
  declaration with `family: skill regression`, in id order; no built-in command.
- L4: `shlex.split`, `python3` is `sys.executable`, tree as the working directory, no `GIT_*`,
  `PYTHONPATH=<tree>/src`, `PYTHONDONTWRITEBYTECODE=1`, stdin /dev/null, `start_new_session=True`, `os.killpg(SIGKILL)`
  at the bound. After the kill the pass does not read the pipes again, so a process that escaped the group cannot hold
  it past the bound.
- L5: as stated; the findings come from `message` of each item (else the item as JSON).
- L6, L7: as stated; links is run after every family has ended; the base is passed as `--since <base>` as given.
- L8: `run` returns the int 0 or 2 under `--structural`; the reason is on stderr as
  `gov check: structural pass could not run: <why>`; nothing is printed on stdout in that case.
- L9: git reads are `git --no-optional-locks -C <tree> ...` (rev-parse, diff --name-only); no file is written by the pass.
  `src/gov/close/`, `src/gov/launch/` (and `src/gov/queue/`, absent here) do not mention it.
- L10: the code is in `structural.py`; `command.py` gained the arguments, the dispatch and its docstring line.

## S5: measured on this tree (the repository's code at my head)

`PYTHONPATH=<tree>/src python3 -m gov.cli.main check --structural HEAD~1 --root /home/usain/gov-os-worktrees/W2-158`,
2026-11-12, at head `883ebbf548b0` (the commit of the code and unit tests); exit 0; wall time 16.2 s (the pass's own
figure on its last line: 16.2 s), within the 60 s of the brief. Lines:

```
schema: ok
graph: ok
claims: ok
mutation: NOTICE .tickets/DAEO-1k7y.md: implementer allowed_paths pattern 'tests/acceptance/W2-96/w2_96_support.py' covers tests/acceptance/ | .tickets/DAEO-1k7y.md: implementer allowed_paths pattern 'tests/acceptance/W2-56/w2_56_support.py' covers tests/acceptance/ | .tickets/DAEO-kmcr.md: implementer allowed_paths pattern 'tests/acceptance/W1-41/test_w1_41_migration.py' covers tests/acceptance/
authority: ok
pathmap: ok
audit: ok
skills: ok
portability: skipped (no such change)
links: ok (0 new since HEAD~1, 1620 standing)
structural pass at 883ebbf548b0: NOTICE in mutation (8 of 9 ran families ok), 16.2 s; a notice, not a refusal
```

The mutation NOTICE is the repository's own finding about three tickets, not a fault of the pass. The run wrote only
links' mark (`.gov-runtime/links/mark`, ignored by git). The lead re-measures on the main tree.

## S5: the lead's measurement on the repository's main tree (2026-11-12)

The code at 4916311219bd, run on the main tree /home/usain/Dynamic-Agentic-Engineering-OS at 010399309d69 with no
`<base>` (so the main tree's links mark is not moved; links and portability are measured on a clone below):

```
schema: ok
graph: ok
claims: ok
mutation: NOTICE .tickets/DAEO-1k7y.md: implementer allowed_paths pattern 'tests/acceptance/W2-96/w2_96_support.py' covers tests/acceptance/ | ... (+6 more)
authority: ok
pathmap: ok
audit: ok
skills: ok
portability: skipped (no base given)
links: skipped (no base given)
structural pass at 010399309d69: NOTICE in mutation (7 of 8 ran families ok), 9.3 s; a notice, not a refusal
```

Exit 0, wall 9.37 s (limit: the 50 s bound plus 10 s). `git status --porcelain` of the main tree: 0 lines before and
after. With a `<base>` (links and portability included), the reviewer's re-measure on a `--shared` clone of
4916311219bd, base `HEAD~3`: wall 19.66 s, exit 0, the only file written `.gov-runtime/links/mark`.

## Other runs

- `tests/unit/check`: 134 passed, 88 deselected (the opt-in and the real-model exclusions).
- `tests/acceptance/W1-26`: 76 passed, 351 deselected.
- Both with `-m "not local_only" -k "not real and not green_here and not time_limit"`; the exclusion left out the
  cases that start a real embedder, reranker or model, and the opt-in rows (the `rep:` rule), which `--optin=breadth`
  brings back for this ticket's own file (44 passed).

## Readings taken (each also in `unresolved`)

1. A usage error that argparse cannot see (`--list` with `--structural`; `<base>` or `--timeout` without it) is
   reported from `run` as one stderr line and the int 2, not argparse's usage text.
2. An unreadable declaration file belongs to the family its name says (its stem); a skill declaration that cannot be
   read counts as skills only when its name starts `skill-regression`.
3. A declaration with `family` absent and a name starting `skill-regression` counts as skills.
4. The sandbox's `/tmp` is read-only, so the pytest runs used the sandbox's own `$TMPDIR` instead of `/tmp/w2-158-eng`.
