# W2-106 acceptance tests: the template's guard lines pinned

Ticket: `DAEO-0mtg` (W2-106) · Profile: FULL · Sources: DEC-966 item 2, DEC-822 (items 1 to 3), DEC-957, DEC-965,
DEC-801, DEC-616; the exit-mapping form of DEC-880 item 3 and DEC-913 item 1; DEC-917 (the four lifecycle lines keep
DEC-608's plain form and are not tested here) · Author: independent test designer (MR-3), written from the ticket's
KPI lines and its sources, in parallel with the engineer, without reading the implementation (DEC-959 item 7,
DEC-963).

Run (from the root of the worktree the tests sit in):

    PYTHONPATH=<that worktree>/src python3 -m pytest tests/acceptance/W2-106 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

Nothing else is needed on `PATH`: `copier` is found at `~/.local/bin/copier` or on `PATH` (W1-39's
`require_copier`), `rulesync` at `RULESYNC_BIN` or `~/.local/bin/rulesync` (W1-38's support; a standalone binary, no
node). Nothing is installed by a test and nothing reaches the network.

**88 cases in 4 files. Red run on the base (`1f0bf283`, the template's lines as on `w2/integrate` before this
ticket): 58 failed, 30 passed, 0 skipped, 15.5 s** (one wheel build and one generated project per session). The red
reason throughout is the one the ticket states: the template's three guard lines run a bare `python3 "$h"`, so the
decoy `python3` first on `PATH` starts the program, no installed gov is looked for, nothing refuses when it is
missing, and a planted `PYTHONPATH` decides which guard code runs (the refused write let through, exit 0). The 30
green cases guard what already holds, each named below with its reason (24 exit-mapping cases, 6 "in step" cases).

## How the cases run the code of the worktree they sit in (DEC-732)

Every path is taken relative to this file: `REPO_ROOT = Path(__file__).resolve().parents[3]`
(`w2_106_support.py`). Merged into the ticket's worktree, the cases read that worktree's
`template/governance/kernel/settings.json`, `template/.rulesync/hooks.jsonc`, `.rulesync/hooks.jsonc` (the
reference form) and `template/governance/kernel/hooks/`, and build the stand-in pin from that worktree's `src/`.

- **The stand-in pin** (W2-59's `make_stand_in`, `tests/acceptance/W2-59/README.md`; fixture `stand_in`, once per
  session): a wheel of this worktree built with `pip wheel --no-deps --no-build-isolation --no-index` (the build
  writes nothing into the worktree), installed non-editable with `pip install --no-deps --no-index` into
  `python3 -m venv --system-site-packages` in a short folder under `TMPDIR`, so that its `bin/gov` names its
  interpreter in a direct `#!` line, as the owner's pin does. It is instrumented after its install: a `.pth` file
  leaves `pin-python-<pid>` when its interpreter starts, its installed `gov/__init__.py` leaves `pin-gov-<pid>`. It is
  reached as the owner's pin is: a link at `<HOME>/.local/bin/gov` (or a `gov` on `PATH`), `HOME` a temporary folder.
  Removed at the session's end.
- **A line runs as Claude Code runs a hook's command**: `sh -c <line>` in the project's root, the event's JSON on
  standard input, `CLAUDE_PROJECT_DIR` set, `GOV_ROLE=engineer`, a ticket, a temporary `HOME`, a `PATH` the case
  writes and no `PYTHONPATH` unless the case plants one. A decoy `python3` and `python` are first on `PATH`; each
  leaves `path-python3-<pid>` (`path-python-<pid>`) and goes on to the real interpreter.
- **The generated project** (KPI 3 and 4; W2-90's `generate_project`): `copier.yml` and `template/` assembled file by
  file into a temporary template source (W1-39's `assemble_source`), `copier copy --defaults --trust`, then
  `rulesync generate` writes `.claude/settings.json` (W1-38's `run_rulesync_generate`). No folder of the repository is
  copied; this repository is never Copier's source or destination.

The `gov.__file__` line, as run for this suite in the tests worktree:

    $ PYTHONPATH=/home/usain/gov-os-worktrees/W2-106-tests/src python3 -c "import gov; print(gov.__file__)"
    /home/usain/gov-os-worktrees/W2-106-tests/src/gov/__init__.py

In the ticket's worktree the same command, with that worktree's `src`, must name that worktree.

## The lines under test

The three guard lines, in both template files (6 lines; ids `settings-<Event>` and `source-<Event>`):

| Event | Program | `template/governance/kernel/settings.json` | `template/.rulesync/hooks.jsonc` |
|---|---|---|---|
| PreToolUse | `pretooluse.py` | `hooks.PreToolUse[].hooks[].command` | `hooks.preToolUse[].command` |
| PostToolUse (Bash) | `posttooluse.py` | `hooks.PostToolUse[].hooks[].command` | `hooks.postToolUse[].command` |
| PostToolUseFailure (Bash) | `posttooluse.py` | `hooks.PostToolUseFailure[].hooks[].command` | `hooks.postToolUseFailure[].command` |

The four lifecycle lines (sessionStart, stop, preCompact, subagentStop) keep DEC-608's plain form by DEC-917, which
W1-38 holds them to; they are not tested here (the lead's scope note, P3).

## KPI map after D-4's cut (DEC-1061)

Regenerated in round 2 of the cut (DEC-1061; the review's F3, F4): each line of the ticket's `kpis:` is placed
by its own words (or by the designer, or by part A's row for that line), never by the README's layout; each
case named here runs in the full run, with every row of a class the line names; tier 2's cap then cut only
the rest. The rest stay built: `breadth` (`tests/optin-lifted*breadth*.txt`, `--optin=breadth`) and, for the
switched-off features, `lifted` (the other `tests/optin-lifted*.txt`, `--optin=lifted`). The placement is data
(`placement.json`, with the designer's `overrides.json`), checked by code against the default collection.

Cases: 26 in the full run, 4 in `breadth`, 58 in `lifted`.

| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |
|---|---|---|
| S1: Each of the template's hook lines (pre-tool and the two post-tool lines, in `template/governance/kernel/settings.json` and their rulesync sourc... | `test_w2_106_form.py::test_the_line_takes_this_repository_s_pinned_form` (2 of 6) | part A's row, by its words |
| S2: Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2) with a message naming what is mi... | `test_w2_106_fail_closed.py::test_a_home_gov_whose_interpreter_is_missing_is_refused` (2 of 6) | part A's row, by its words |
| S3: A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing at an edited copy of gov that... | `test_w2_106_generated_project.py::test_a_planted_pythonpath_to_an_edited_gov_does_not_let_a_refused_write_through` | part A's row, by its words |
| S4: A generated project's hook lines equal the template's source after `rulesync generate` (the two sources stay in step), and the template's own s... | `test_w2_106_form.py::test_the_settings_and_the_rulesync_source_hold_the_same_guard_line` (1 of 3), `test_w2_106_generated_project.py::test_the_generated_settings_hold_the_template_s_guard_line` (1 of 3) | part A's row, by its words |
| F1: A template hook line that runs a bare `python3`, or one without `-E`. | `test_w2_106_form.py::test_the_line_runs_no_bare_python3_and_passes_minus_e_to_its_interpreter` (2 of 6) | part A's row, by its words |
| F2: A missing or broken gov lets the hook pass, or falls back to another interpreter. | `test_w2_106_fail_closed.py::test_a_broken_home_gov_does_not_fall_back_to_the_gov_on_path` (2 of 6) | part A's row, by its words |
| F3: An edited gov on PYTHONPATH lets a refused write through. | `test_w2_106_generated_project.py::test_a_planted_pythonpath_to_an_edited_gov_does_not_let_a_refused_write_through` | part A's row, by its words |
| F4: The settings and the rulesync source out of step, or W1-38 or W1-39 red. | `test_w2_106_form.py::test_the_settings_and_the_rulesync_source_hold_the_same_guard_line` (1 of 3), `test_w2_106_generated_project.py::test_the_generated_settings_hold_the_template_s_guard_line` (1 of 3) | part A's row, by its words |

## KPI lines, cases and red reasons

### KPI success 1 and its failure line: the pinned form (`test_w2_106_form.py`, `test_w2_106_interpreter.py`)

"Each of the template's hook lines ... takes this repository's pinned form (DEC-822, W2-59): it finds the installed
gov (`$HOME/.local/bin/gov`, else `gov` on PATH), reads the interpreter its first line names, and runs the hook with
that interpreter and `-E`; the line's exit codes are kept (0 and 2 pass through; any other ends in a refusal)."
Failure: "A template hook line that runs a bare `python3`, or one without `-E`."

| Case (× 6 lines unless said) | What it holds | Red reason on the base |
|---|---|---|
| `test_the_line_takes_this_repository_s_pinned_form` | the line is `.rulesync/hooks.jsonc`'s `preToolUse` line exactly, with `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>` in the place of its program path | the line is `h=...; python3 "$h"; r=$?; ...`, not the pinned form |
| `test_the_line_runs_no_bare_python3_and_passes_minus_e_to_its_interpreter` | no bare `python3` or `python` command word; a `-E` argument | the line runs a bare `python3` |
| `test_the_line_starts_its_program_with_the_interpreter_the_home_gov_names_and_minus_e` | with only `$HOME/.local/bin/gov` (a link to the stand-in; `PATH` holds no gov), the program runs under the stand-in's interpreter (`sys.prefix` is its environment; `pin-python-` marker), with `sys.flags.ignore_environment == 1`, exit 0; the decoy never starts | the decoy `python3` first on `PATH` started the program |
| `test_without_the_home_gov_the_line_uses_the_gov_on_path` | no home gov; a `gov` on `PATH` (link to the stand-in): its interpreter runs the program | the same |
| `test_the_home_gov_comes_before_the_gov_on_path` | home gov (stand-in) and another `gov` first on `PATH` naming an interpreter of its own: that interpreter never starts | the same |
| `test_the_line_keeps_its_exit_codes[<ending>]` × 4 endings × 6 lines (24) | program exit 0 with a deny decision on standard output: 0, output unchanged; exit 2 with a refusal on standard error: 2, refusal delivered; exit 1: 2 with a message naming the program; killed by SIGKILL (a crash): 2 with a message naming the program | **green on the base** (24): W2-65's exit mapping is already in the lines (DEC-913 item 1); these cases guard that the pinned form keeps it (a form ending in `exec`, for example, would lose it) |

The form is given by reference (the brief and the KPI: "this repository's pinned form (DEC-822, W2-59)"), and the
first case holds it exactly, as DEC-608 and DEC-917 hold "forms" (the program's path aside). The behaviour of the
form is held by the run cases, which read no text of the line.

### KPI success 2 and its failure line: fail closed (`test_w2_106_fail_closed.py`, 24 cases)

"Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2) with
a message naming what is missing; it never falls back to a bare `python3`." Failure: "A missing or broken gov lets the
hook pass, or falls back to another interpreter."

The project's program is a stand-in that would allow the call (exit 0) if it ran, so any fallback lets the call
through. Each case asks: exit 2 (the only exit, with a deny decision on exit 0, that Claude Code blocks on), the
program never ran, the decoy `python3`/`python` never started.

| Case (× 6 lines) | Setting | Message asked for | Red reason on the base |
|---|---|---|---|
| `test_with_no_gov_found_the_line_refuses_and_says_so` | no `$HOME/.local/bin/gov`, no `gov` on `PATH` (checked) | names `.local/bin/gov` and `PATH` | exit 0: the line ran the decoy `python3` and the program allowed |
| `test_a_home_gov_whose_first_line_names_no_interpreter_is_refused` | home gov with no `#!` line | names that gov's path | the same |
| `test_a_home_gov_whose_interpreter_is_missing_is_refused` | home gov naming `/nonexistent/w2106/bin/python3` | names that interpreter | the same |
| `test_a_broken_home_gov_does_not_fall_back_to_the_gov_on_path` | home gov naming a missing interpreter, a working `gov` (the stand-in) on `PATH` | (exit 2; the stand-in's interpreter never starts) | the same |

### KPI success 3 and its failure line: a planted PYTHONPATH (`test_w2_106_generated_project.py`, 4 cases)

"A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing at
an edited copy of gov that would allow a refused write, the hook still refuses it (the measurement of P-W2-90-1 P1-B,
now refused)." Failure: "An edited gov on PYTHONPATH lets a refused write through."

The generated project's `src/` holds an edited `gov` whose guard allows every call (W2-59's
`worker_import_path_files`: `tree-gov-<pid>` when imported, `tree-site-<pid>` from a `sitecustomize.py` whenever an
interpreter starts with the folder on its import path). The session's `PYTHONPATH` names it (a ticket worktree's
shape). The refused write is an engineer's `Write` outside the ticket's paths (W2-59's `refused_write`). The lines are
the generated `.claude/settings.json`'s; the kernel's real programs run; the home gov links to the stand-in.

| Case | What it holds | Red reason on the base |
|---|---|---|
| `test_a_planted_pythonpath_to_an_edited_gov_does_not_let_a_refused_write_through` | refused (exit 2 or a deny decision with exit 0), the pin's package decided (`pin-gov-`), no `tree-` marker | **fail-open**: the line's bare `python3` imported the edited gov, which allowed the write (exit 0, nothing on standard output): P1-B's measurement |
| `test_without_the_planted_pythonpath_the_pin_s_guard_refuses_the_same_write` (the control) | the same write with no `PYTHONPATH` is refused by the pin's guard | refused, but not by the pin: the bare `python3` found no `gov` and the program failed closed; `pin-gov-` absent |
| `test_a_planted_pythonpath_does_not_reach_the_containment_program[PostToolUse]`, `[PostToolUseFailure]` | the containment program imports the pin's package, no `tree-` marker, no decoy | the program imported the edited gov (`tree-gov-`, `tree-site-`) through the bare `python3` |

### KPI success 4 and its failure line: the sources in step; W1-38 and W1-39 (`test_w2_106_form.py`, `test_w2_106_generated_project.py`)

"A generated project's hook lines equal the template's source after `rulesync generate` (the two sources stay in
step), and the template's own suites (W1-38, W1-39) pass." Failure: "The settings and the rulesync source out of
step, or W1-38 or W1-39 red."

| Case | What it holds | On the base |
|---|---|---|
| `test_the_settings_and_the_rulesync_source_hold_the_same_guard_line` × 3 events | the kernel template's settings and the template's rulesync source hold the same string under each guard event | **green** (3): both hold the exit-mapping form today; they guard that the change moves both |
| `test_the_generated_settings_hold_the_template_s_guard_line` × 3 events | after `rulesync generate`, the generated settings hold that same string | **green** (3): the same |

W1-38 and W1-39 are run as their own suites (the lead's verification), not from here. See "W1-38 revised" below.

## Checked against the form asked for (a scratch simulation, not committed)

A pytest plugin in a scratch folder answered reads of the two template files (through `open`, so Copier's assembled
source took them too) with copies whose three guard lines are `.rulesync/hooks.jsonc`'s `preToolUse` line with the
template's program path. Nothing tracked was touched. Results:

- the reference form: **88 passed** (11.9 s);
- the reference form without `-E` (`"$p" "$h"`): 21 failed (the form × 6, the `-E` case × 6, the
  interpreter-and-`-E` run × 6, and the three KPI 3 cases with the planted `PYTHONPATH`);
- the reference form falling back to `python3 "$h"` when no gov is found: 18 failed (the form × 6, the bare-`python3`
  case × 6, the no-gov refusal × 6);
- W1-38's `test_w1_38_hooks_command_line.py` (its 15 form cases and its 4 live cases through the stand-in session),
  with the W1-38 revision below: **19 passed**, also with `~/.local/bin` (the owner's pin) taken off `PATH`; without
  the revision and with no `gov` on `PATH`: 3 of the 4 live cases red (the guard's line refused every call).
  On the base the revision's 4 live cases pass (8.4 s). The rest of W1-38 and W1-39 was not run here (see the return:
  the machine's load held the run).

## W1-38 revised (Rewrite-Reason: DEC-966 item 2)

KPI 4 asks that W1-38 pass, and DEC-732 that it judge the code of the worktree it runs in. Once the template's guard
lines take the pinned form, W1-38's live cases (every case on the stand-in session of
`w1_38_hooks_support.make_session_sandbox`: in `test_w1_38_hooks_any_folder.py`, `test_w1_38_hooks_command_line.py`,
`test_w1_38_hooks_source.py`, `test_w1_38_test_folder_rule.py`) run the generated lines with a stand-in `HOME` that
held only a path file naming this worktree's `src` in its user site folder, and the runner's own `PATH`. The pinned
line finds no `$HOME/.local/bin/gov` there, so it takes the `gov` on the runner's `PATH`: on this machine the owner's
pin (`~/.local/bin/gov`), whose interpreter, `--system-site-packages` with `-E`, imports **its own installed
package**, not the path file's (measured in a scratch probe with a stand-in pin: `gov.__file__` was the
environment's own `site-packages/gov`). W1-38's guard-line cases would then judge the owner's pin, not this worktree;
on a machine with no `gov` on `PATH` every call would be refused.

The revision: `make_session_sandbox` also writes the editable install's `gov` script at `<home>/.local/bin/gov`, its
first line naming the test's own interpreter, as `pip install --user -e` leaves it (DEC-605, the owner's rollback; the
same form as W2-59's `install_rollback` and W2-65's box). The pinned line finds it, starts that interpreter with `-E`
(which keeps the user site folder), and the path file gives this worktree's package, as before. No expectation is
changed; on the base the lines run a bare `python3` and never read the script.

## Other suites the pinned form affects (named, not edited: W2-90's next round)

Each runs the template's (or a generated project's) guard lines with a stand-in `HOME` that has no
`.local/bin/gov`, giving the package by a user-site path file or by `PYTHONPATH`. Once the lines are pinned, those
lines take the `gov` on the runner's `PATH` (the owner's pin here; `-E` drops `PYTHONPATH`, and the pin's own package
wins over a path file), so the cases judge the owner's pin instead of the worktree's code (DEC-732), or refuse every
call where no `gov` is on `PATH`:

- through W2-90's `install_gov_for` (a path file only): `tests/acceptance/W1-05/` (`kernel_sandbox`:
  `test_w1_05_live_hooks.py`, `test_w1_05_role_subagents.py`), `tests/acceptance/W1-46/` (`kernel_sandbox`: the
  `kernel_guard` cases), `tests/acceptance/W1-28/test_w1_28_launch_product_spec.py`,
  `tests/acceptance/W1-47/test_w1_47_failed_commands.py`;
- through `PYTHONPATH`: `tests/acceptance/W1-47/test_w1_47_kernel_template.py` (`w1_47_support.installed_environment`
  runs the kernel template's own settings with `PYTHONPATH` naming the repository's `src`), and the real-session cases
  launched with `PYTHONPATH` naming the project's `src` (`tests/acceptance/W1-46/test_w1_46_live_sessions.py`,
  `tests/acceptance/W1-50/test_w1_50_freeze_launcher.py`); their sessions inherit the runner's `HOME`, so the pinned
  line takes the owner's pin at `~/.local/bin/gov`.

The fix for each is the one made in W1-38: the stand-in home gets the editable install's `gov` script beside its
path file (for W2-90's helper, in `install_gov_for`). Not affected: W2-65 (its box already holds `.local/bin/gov`
naming its interpreter; its missing-interpreter case is refused with the program named), W2-59's seven-lines case (a
count), W1-49 (a registration case, nothing run), W1-39 (no case runs a hook line; its time-limit case reads the
entries' `timeout`).

## Packages

None. The one reading stated rather than asked: "takes this repository's pinned form" is held exactly, the program's
path aside (`test_the_line_takes_this_repository_s_pinned_form`), as the register holds forms (DEC-608, DEC-917); a
line that behaves alike in other words passes every other case and fails that one alone.
