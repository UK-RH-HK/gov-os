# W2-59 acceptance tests: the pinned judge, the hook lines and the packaging gaps

Ticket: `DAEO-kh9l` (W2-59) · Profile: STANDARD (DEC-221) · Sources: DEC-822 (items 1 to 3, step 2), DEC-835,
DEC-831, DEC-732, DEC-579 · Author: independent test designer (MR-3), written before the implementation, run 1;
run 2 (a fresh test designer, after the implementation, from the CIT-P review's finding as a described behaviour,
DEC-136): the hook lines in a launched worker's environment, section "Run 2" below.

Run:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W2-59 -q -p no:cacheprovider -rs

**44 cases in 5 files. Red run on the base (`c5100159`, before any implementation): 39 failed, 5 passed,
0 skipped, about 7 seconds** (one wheel build per session). The five green cases are named below with the reason.
Four cases are `local_only` (they need this machine's `gitleaks` binary; skipped without it).

**Run 2 adds 11 cases in a sixth file, `test_w2_59_hook_lines_worker_env.py`: 55 cases in 6 files. Red run at
`9b9faac3` (the implementation in place): 9 failed, 46 passed, 0 skipped, about 10 seconds;** the 44 earlier cases
all pass, and the two green new cases are named with the reason.

## How the cases run this worktree's code (DEC-732)

The code under test is this worktree's own `src/`, always; the cases never run the owner's pin, the main tree or an
editable install.

- **The stand-in pin** (fixture `stand_in`, once per session): a wheel built from this worktree by
  `python3 -m pip wheel --no-deps --no-build-isolation --no-index`, with `DIST_EXTRA_CONFIG` moving the `build` and
  `egg-info` folders into the temporary folder (the build writes nothing into the worktree; the fixture fails if a
  `build/`, `dist/` or `src/*.egg-info` appears), installed non-editable with `pip install --no-deps --no-index`
  into `python3 -m venv --system-site-packages` in a short folder directly under `TMPDIR` (so that its `bin/gov`
  names its interpreter in a direct `#!` line, as the owner's pin does). No network. It is removed at the session's
  end. It is reached the way the owner's pin is: a link at `<HOME>/.local/bin/gov` to its `bin/gov`, `HOME` a
  temporary folder. Nothing depends on a pin's versioned path.
- **The project under check**: a temporary git repository built from scratch with `git init`; its files are
  written by the case or are single named files of this worktree (check declarations, hook programs, the template
  path map, the gitleaks configurations). No folder of the repository is copied.
- **`gov --version` from this worktree's code** (KPI 5): `python3 -m gov.cli.main --version` with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set in that one subprocess.
- Every other subprocess runs with `PYTHONPATH` removed, `HOME` temporary and a `PATH` the case writes. Run 2's
  cases then add, on purpose, a worker's `PYTHONPATH` naming a decoy folder of the case (never this worktree's
  `src`): the session's inherited variable under test.

The `gov.__file__` line, as run for this suite:

    $ PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"
    /home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py

**Instrumentation and decoys.** Only the stand-in is instrumented, after its install, never the wheel: a `.pth` file
in its site folder leaves `pin-python-<pid>` when its interpreter starts; its installed `gov/__init__.py` leaves
`pin-gov-<pid>` when its package is imported. Decoys leave markers of their own: a `python3` (which goes on to the
real interpreter) and a `gov` first on `PATH`, a `gov` package under the project's `src/` (its schema check edited to
report `W259_TREE_EDIT` and exit 1), a `gov` package at the project's root. Every marker folder's absolute path is
written into the decoy itself, so no marker depends on an environment variable reaching the process (W2-05's
unmerged `git_env(root)` may change the checks' environment). At the place a lookup from the installed package's
location leads to (three folders above the installed `gov/retrieval/` module: the repository root for a source
checkout, `<venv>/lib/python3.X` for the install), decoys are planted: canary declarations with a query of their
own in both kernel layouts, and a path map and gitleaks configurations that cannot be read.

## KPI lines, cases and red reasons

### KPI success 1 and its failure line: the judge's checks (`test_w2_59_judge_checks.py`, 7 cases)

"The runner runs every declared check with the pinned interpreter and package; only the code under test comes from
the tree [DEC-822 item 3]." Failure: "A check edited in the tree does not change the verdict of the pinned judge."
The project holds every check declaration of this worktree's kernel; the judge is the stand-in's `gov check --json`.

| Case | Red reason seen |
|---|---|
| `test_no_declared_check_imports_the_project_s_own_gov_package` | 19 check processes imported the project's `src/gov` (the runner puts `<root>/src` first on `PYTHONPATH`) |
| `test_a_check_edited_in_the_tree_does_not_change_the_pinned_judge_s_verdict` | in the control project the judge's schema check could not import the judge's own package (`No module named 'gov'`: the declared `python3` is the system's); with the edit, the verdict is the edited check's (`W259_TREE_EDIT`) |
| `test_a_declared_python3_command_does_not_run_the_python3_first_on_path` | 19 checks ran the decoy `python3` first on `PATH` |
| `test_a_declared_gov_command_does_not_run_the_gov_first_on_path` | `fresh-agent-reconstruction` (`gov checkpoint --resume --json`) ran the decoy `gov` first on `PATH` |
| `test_a_declared_check_runs_with_the_judge_s_interpreter_package_and_no_project_pythonpath[template]`, `[installed]` | a probe declared in either kernel layout (DEC-579) ran with `/usr` (`/usr/bin/python3.12`), not the judge's environment; its `PYTHONPATH` names the project's `src` |
| `test_a_gov_package_at_the_project_s_root_is_not_imported_by_the_checks` | 2 check processes imported the project's root `gov/` (a `-m` run puts its working folder, the project root, first on the import path) |

The last case is a key edge this designer adds under "the project supplies only data": a judge that runs
`<pin python> -m gov.check.x` in the project's root still imports a root `gov/` package of the project. A
simulation in a scratch folder (not committed) showed a corrected runner turning all seven green: the judge's
`sys.executable` with `-P` for a declared `python3`, the judge's own `gov` for a declared `gov`, no `PYTHONPATH`.

### KPI success 2: the hook lines (`test_w2_59_hook_lines.py`, 25 cases)

"The hook command lines call the pin's environment [DEC-822 step 2]." Every command entry of this repository's
`.rulesync/hooks.jsonc` is run through `sh -c` in a temporary project holding the kernel's six hook programs, with
`CLAUDE_PROJECT_DIR` set, an engineer's role and a ticket, `<HOME>/.local/bin` (the link to the stand-in) first on
`PATH` and a decoy `python3` next.

| Case | Red reason seen |
|---|---|
| `test_the_source_holds_the_seven_governance_hook_lines` | **green**: a guard that the parametrised cases cover all seven lines |
| `test_the_line_names_no_versioned_pin_path_and_puts_no_project_src_on_the_import_path[...]` × 7 | red × 3 (preToolUse, postToolUse, postToolUseFailure: `PYTHONPATH="$CLAUDE_PROJECT_DIR/src"`); **green × 4** (preCompact, sessionStart, stop, subagentStop name no `PYTHONPATH` and no pin path today; they guard the new lines against a versioned pin path such as `pin-fecb870c`) |
| `test_the_line_starts_its_program_with_the_pin_s_interpreter[...]` × 7 | each line started the decoy `python3` first on `PATH` |
| `test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[...]` × 6 | preToolUse and both after-call lines imported the project's `src/gov`; preCompact, sessionStart and stop did not import the pin's package (the system `python3` has none). subagentStop imports no governance package and has no case here |
| `test_without_a_pin_the_pretooluse_line_blocks_the_call[preToolUse[0]]` | with no pin, the line fell back to the project's `src/gov` and the `python3` on `PATH` (it does exit 2, so the blocking assertion alone would pass) |
| `test_without_a_pin_the_after_call_lines_do_not_end_silently[...]` × 2 | the same fallback |
| `test_the_line_follows_the_owner_s_rollback_to_an_editable_install[preToolUse[0]]` | the line started the `python3` first on `PATH` |

Choices, stated:
- **Fail closed.** With no `gov` link and no `gov` on `PATH`, the preToolUse line must block: exit 2 or a deny
  decision (Claude Code treats any other non-zero exit as a non-blocking error and lets the call proceed). The two
  after-call lines must end with a non-zero exit (never a silent success: the containment check did not run). The
  other four lines are not constrained when the pin is missing (proportion: a SubagentStop or Stop exit 2 would
  hold a session open). In every case no other install stands in for the pin.
- **The rollback.** DEC-605's editable install is `pip install --user -e`: a script at `~/.local/bin/gov` whose
  first line names the system interpreter, the package found through the user site folder. The case writes that
  form in the temporary home (the package is this worktree's `src`) and requires the preToolUse line to start that
  interpreter. A line that looks for an interpreter beside the link's target (`.local/bin/python3`) fails it.
- **preCompact and sessionStart** put the project's `src` on their own import path when the folder exists
  (`template/governance/kernel/hooks/precompact.py`, `sessionstart.py`: outside the ticket's paths). Their line is
  measured in a project without `src/`; see package P-W2-59-1.
- A scratch simulation (not committed), through this suite's own helpers, showed one line form giving the pin's
  interpreter and package for all seven lines, no decoy marker, and exit 2 without a pin for the three guard lines
  (the rollback case was not simulated; the form reads the rollback script's own `#!` line):
  `g=$(command -v gov) || { echo ... >&2; exit 2; }; p=$(sed -n "1s/^#!//p" "$g"); [ -x "$p" ] || { ...; exit 2; }; exec "$p" "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/<program>"`.

### Run 2: the hook lines in a launched worker's environment (`test_w2_59_hook_lines_worker_env.py`, 11 cases)

KPI success 2, "The hook command lines call the pin's environment [DEC-822 step 2]", read with DEC-822 item 3 ("the
per-command `PYTHONPATH` chooses only the code under test, not the judge"). The behaviour, from the CIT-P review
(DEC-136): **a hook line runs the pin's governance package whatever import path the session's environment names.**

Why a worker's session carries `PYTHONPATH`: the committed launch form (`governance/project/briefs/LEAD-w2-common.md`)
sets `PYTHONPATH=<worktree>/src` on the `gov launch` command, and the launcher starts the session with
`{**os.environ, **settings["env"]}` (`src/gov/launch/launcher.py:319`). Claude Code runs a hook's line with the
session's environment. This designer's own session shows it: `printenv PYTHONPATH` gives
`/home/usain/gov-os-worktrees/W2-59/src`.

How the cases run: as the run-1 hook-line cases (`sh -c`, `CLAUDE_PROJECT_DIR` a temporary project holding the
kernel's six hook programs, `HOME` a temporary folder holding the link `.local/bin/gov` to the stand-in pin built
from this worktree, that folder first on `PATH`, a decoy `python3` next, an engineer's role and a ticket), with the
worker's `PYTHONPATH` added to that environment (`w2_59_support.session_env`, `inherited=`). The folder it names
(`worker_import_path_files`) holds a `gov` package standing for an edit of the code under test: **its guard allows
every call**, importing it leaves `tree-gov-<pid>`, and a `sitecustomize.py` beside it leaves `tree-site-<pid>`
whenever an interpreter starts with the folder on its import path. The refused call is an engineer's `Write` to
`<project>/outside-the-ticket/w259.txt` (`refused_write`); the pin's guard denies it ("Write to ... denied for role
'engineer'", seen by a scratch probe of this worktree's guard).

| Case | Behaviour item | Red reason seen at `9b9faac3` |
|---|---|---|
| `test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-worker-pythonpath]` | 1 | **fail-open:** the line imported the project's `src/gov` and its edited guard decided; the refused write was let through (exit 0, nothing on standard output) |
| `...[preToolUse[0]-no-pythonpath]` | 1, the control | **green**: without the inherited variable the pin's guard decides and denies, as KPI 2's run-1 cases already require |
| `test_with_a_worker_s_pythonpath_and_no_pin_the_guard_line_still_blocks[preToolUse[0]]` | 1, never fail open | **green**: with no `gov` to be found the line blocks before it starts any interpreter, so the inherited path is never read; kept as the guard against a fix that falls back |
| `test_after_the_rollback_with_a_worker_s_pythonpath_the_guard_line_runs_the_editable_install[preToolUse[0]]` | 1, the rollback | the line imported the inherited path's `gov`, not the rollback's (DEC-605) package |
| `test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[postToolUse[0]]`, `[postToolUseFailure[0]]`, `[stop[0]]` | 2 | the program imported the inherited path's `gov` (here the project's `src`), not the pin's |
| `...[preCompact[0]]`, `[sessionStart[0]]` | 2 | the program imported the inherited path's `gov` (here a folder outside the project, see below) |
| `...[subagentStop[0]]` | 2 | the pin's interpreter started with the inherited folder on its import path (its `sitecustomize` ran) |
| `test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code[preToolUse[0]]` | 3 | the project's `gov` decided the call (the same cause as the first row); with the simulated fix below the whole case, its second half included, passes |

Choices, stated:
- **Which install's code ran** is shown by markers, as in run 1: `pin-gov-` (the pin's installed package imported),
  `pin-python-` (the pin's interpreter started), `tree-gov-` and `tree-site-` (the inherited path's package, or the
  folder on the import path at all). subagentStop's program imports no governance package, so its case reads the
  import path itself.
- **preCompact and sessionStart** add the project's own `src` to their import path when that folder exists (row
  W2-M389, deferred to W2-10; run 1's package P-W2-59-1). Measured in a project with `src/`, the program would
  import the tree whatever the line does. So their case measures only what the line controls: the project has no
  `src/`, and the worker's `PYTHONPATH` names a folder outside the project holding the same decoy package. Left to
  W2-M389: that these two programs, in a ticket worktree (which has `src/`), import the code under test even when
  the line runs the pin's interpreter without the inherited path.
- **The rollback with a worker's `PYTHONPATH`.** DEC-605's editable install finds its package through the user site
  folder. A line that drops the inherited path by isolating the interpreter (`python -I`, or `-s`) also drops the
  user site folder, and with it the rollback's package; this case and run 1's rollback case then fail. The form of
  the fix is the engineer's; the case requires only the behaviour.
- **Item 3, the variable stays the code under test's.** A line cannot change the session's environment for later
  commands; what it, or a fix in the guard, could do wrongly is refuse a command that sets `PYTHONPATH` itself. The
  case requires the pin's guard to let DEC-732's form through (`PYTHONPATH=<src> python3 -c 'import gov; ...'`)
  and that command, run with the session's environment, to import the tree's package. **Not tested, package
  P-W2-59-5:** `PYTHONPATH=<src> gov <command>` with the bare pin.
- **Proportion (DEC-221):** one case per line, plus the control without the variable, the no-pin case and the
  rollback case for the guard line (the one line that can fail open), and one case for item 3.

A scratch simulation (not committed; a pytest plugin pointing `HOOK_SOURCE_REL` at a generated source, run over this
file and `test_w2_59_hook_lines.py`, 36 cases) with run 1's simulated form and four interpreter calls:
`exec "$p" ...` gave the same 9 reds as the head; `exec env -u PYTHONPATH "$p" ...` and `exec "$p" -E ...` gave
36 passed; `exec "$p" -I ...` gave 34 passed, 2 failed (both rollback cases). (`-E` also ignores every other
`PYTHON*` variable of the session; `env -u PYTHONPATH` drops only this one.)

The `gov.__file__` line, as run for run 2:

    $ PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"
    /home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py

### Run 2: earlier tests checked against a line that ignores an inherited import path

- **`tests/acceptance/W2-59/` (run 1):** none turns red for a line that drops the inherited `PYTHONPATH` with
  `env -u PYTHONPATH` or `-E` (simulated: all 25 run-1 hook-line cases pass). A line that uses `-I` or `-s` turns
  `test_the_line_follows_the_owner_s_rollback_to_an_editable_install[preToolUse[0]]` red (the rollback's package is
  found through the user site folder). That case is right and needs no revision: the fix must keep the user site
  folder. The regular expression of `test_the_line_names_no_versioned_pin_path_and_puts_no_project_src_on_the_import_path`
  does not match `env -u PYTHONPATH`.
- **`tests/acceptance/W1-38/`:** none turns red, and none needs a revision. As run 1 found, its cases read the
  template's source, the kernel template's settings, or settings generated from the template in a temporary project,
  never this repository's `.rulesync/hooks.jsonc` (the one mention in `test_w1_38_rulesync.py` is a generated
  project's). If the template's lines later take the same form, run 1's list applies, and a `-I` or `-s` form would
  also break its live cases, whose stand-in session finds `gov` through a path file in the user site folder
  (`w1_38_hooks_support.make_session_sandbox`).
- **`tests/acceptance/W1-05/`:** none turns red, and none needs a revision. Its live cases run the lines of the
  generated `.claude/settings.json` (which the owner regenerates, DEC-835 item 3) in an environment built from
  scratch with no `PYTHONPATH` (`w1_05_support.command_environment`), so dropping an inherited one changes nothing
  there. A `-E` form also ignores the `PYTHONDONTWRITEBYTECODE=1` that environment sets; the programs run as scripts
  and no W1-05 case fails on an extra untracked file (`bash_call` asserts only that the changed paths are listed).
  This is a reading: W1-05 was not run against a regenerated settings file.

### KPI success 3 and its failure line: the repository from the project root (`test_w2_59_project_root.py`, 5 cases)

"Every module that finds the repository from its own install path finds it from the project root instead (today
`src/gov/retrieval/canary.py:10` and `src/gov/retrieval/retrieve_check.py:16`), proven from an installed wheel."
Failure: "a module that still reads the repository from its install path fails a test." On the base, a search of
`src/gov` for `__file__` and `parents[` finds only these two lookups outside the package (the others,
`cli/main.py`, `retrieval/rerank.py` and `close/command.py`, find files of the package itself). Each is covered by
behaviour, from the stand-in.

| Case | Red reason seen |
|---|---|
| `test_doctor_reads_the_canary_declarations_of_the_project_under_check[template]`, `[installed]` | `gov doctor` read the decoy canary at the install path (`misses: ['w259 decoy canary at the install path']`) |
| `test_doctor_does_not_fall_back_to_the_install_path_when_the_project_declares_no_canary` | the same: the decoy was read for a project with no canary declaration |
| `test_the_retrieval_check_adopts_each_dev_tier_from_the_project_s_own_files[this-repository]`, `[adopted]` (`local_only`) | the check ends first on its missing baseline (KPI 4), before it reads the path map or gitleaks configuration; after that fix, from the install path it reads the decoy path map |

The canary cases need no index: with none built, each declared query is run and missed, so the answer names the
project's query (deterministic). The retrieval cases build a dev tier from scratch (`a-dev`, two files, one
query) in the case's temporary folder and name it by `GOV_DEV_TIERS`; the workbench's dev tiers are not used
(DEC-723; and proportion: the same code path runs in about 4 seconds instead of up to 600). They need `gitleaks`
(the indexing scans for secrets): the binary of the runner's `PATH` is linked alone into a tools folder, so the
owner's `~/.local/bin` (which holds the real pin) is never on the case's `PATH`. **The adopted layout** holds only a
root `.gitleaks.toml`, as an adopted project does (DEC-579): a fix that reads `template/.gitleaks.toml` from the
project root and nothing else leaves the adopted case red (simulated: "no dev tier could be indexed").

### KPI success 4 and its failure line: the baseline as package data (`test_w2_59_baseline.py`, 4 cases)

"`retrieve_baseline.yaml` is shipped as package data, proven from an installed wheel." Failure: "a wheel without
the data file fails the build or its test."

| Case | Red reason seen |
|---|---|
| `test_the_wheel_ships_the_baseline_in_the_retrieval_package` | the wheel has no `gov/retrieval/retrieve_baseline.yaml` (its only non-Python files are the dist-info files) |
| `test_the_installed_package_holds_the_baseline` | the installed package has no such file |
| `test_the_installed_check_does_not_fail_for_want_of_its_baseline` | `FileNotFoundError` on the installed baseline (dev tiers configured, no tier) |
| `test_the_installed_check_reads_its_thresholds_from_the_installed_package` (`local_only`) | the same `FileNotFoundError`; the project's decoy baselines (`hit_at_5: 7`) must not be read; it also needs KPI 3's fix |

### KPI success 5: `gov --version` (`test_w2_59_version.py`, 3 cases)

"`gov --version` names the version and the commit."

| Case | Red reason seen |
|---|---|
| `test_from_this_worktree_s_code_outside_any_project_it_names_the_version_and_head` | exit 2, `the following arguments are required: <command>` |
| `test_inside_another_git_repository_it_names_the_code_s_commit_not_that_repository_s` | the same |
| `test_the_installed_pin_names_its_version_and_never_a_wrong_commit` | the same, from the stand-in |

The version is `pyproject.toml`'s. A commit is any 7 to 40 hexadecimal characters; each must be a prefix of this
worktree's `HEAD`, and the working folder's repository's commit is never named. From the installed wheel the case
requires the version and never a wrong commit, but **not** that it name its commit: package P-W2-59-2.

## W1-38's hook-source tests, checked against the change (DEC-822 step 2, MR-3)

Every test under `tests/acceptance/W1-38/` that reads or runs hook command lines reads **the template's** source,
`template/.rulesync/hooks.jsonc`, the kernel template's `template/governance/kernel/settings.json`, or the settings
that rulesync generates from the template's sources in a temporary project (`w1_38_hooks_support.SOURCE_REL`,
`KERNEL_SETTINGS_REL`; `w1_38_support.TEMPLATE_RULESYNC_REL`). The one use of `PROJECT_SOURCE_REL`
(`.rulesync/hooks.jsonc`), in `test_w1_38_hooks_source.py::TestRulesyncPassesBothThrough`, is the temporary
project's copy of the template's source. No test of the repository reads this repository's own
`.rulesync/hooks.jsonc` (searched in `tests/`).

**Result: the change of `.rulesync/hooks.jsonc` that this ticket allows makes no W1-38 test red, and needs no
revision of one.** This holds while the template's lines (`template/.rulesync/hooks.jsonc`, outside this ticket's
paths) keep DEC-608's form, `python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>"`. If a later change
moves the template's lines to the pin too, these W1-38 cases compare the whole command line and would turn red:
`test_w1_38_hooks_command_line.py` (the 15 cases of "The addition after DEC-608": `TestGeneratedCommandLines` × 7,
the source × 7, the form × 1) and the form-dependent cases of `test_w1_38_hooks_source.py`; they would need DEC-608's
form re-baselined first. Not this ticket.

## Packages

**P-W2-59-1. Two hook programs put the project's `src` on their own import path.**
- Context: KPI success 2 ("the hook command lines call the pin's environment"); the ticket's paths allow
  `.rulesync/hooks.jsonc`, "the hook command lines' interpreter only".
- What happened: `precompact.py` and `sessionstart.py` (under `template/governance/kernel/hooks/`) insert
  `$CLAUDE_PROJECT_DIR/src` first on `sys.path` before importing `gov` when that folder exists. In this repository
  it does, so even under the pin's interpreter those two programs import the code under test, not the pin's
  package. A command line alone cannot prevent it (short of pre-importing `gov` in a `-c` wrapper, which is fragile).
- Why it matters: a ticket that edits `gov.checkpoint` or `gov.context` changes what these two hooks run (the
  failure DEC-822 item 3 closes for the checks). Both fail soft (they never block), so the exposure is a wrong or
  missing checkpoint or context, not a guard bypass.
- Options: (a) widen W2-59's paths to the two programs (remove the insertion; the hook lines then carry the pin);
  cost small (two short edits), risk low, changes the kernel's hook programs (CAP-33, the same CIT-P).
  (b) defer to a follow-up row; cost none now; the two hooks run the tree's code until then. (c) accept as built:
  record that the two hooks may run the code under test.
- Recommendation: (a), confidence medium-high. Blocks nothing in this suite: the two lines are measured in a
  project without `src/`.

**P-W2-59-2. Must the installed pin name its commit?**
- Context: KPI success 5 does not say "proven from an installed wheel", unlike KPI 3 and 4. The owner's pin is a
  wheel built from a `git archive` export (no git metadata), installed non-editable.
- What happened: a commit can be named from an installed wheel only if the build records it (for example
  `export-subst` in `.gitattributes` with a `$Format:%H$` file, or a build step), and none of those paths is in the
  ticket's `allowed_paths` (`pyproject.toml` is "package data only", `cli/main.py` "the version only"). At run time
  the installed package has no repository to ask.
- Why it matters: the owner's purpose for `gov --version` is mostly the pin ("which release judges?"); without the
  commit the pin answers only `0.1.0`. A wrong commit (for example the working folder's `HEAD`) would be worse than
  none, and the suite already refuses it.
- Options: (a) as written here: from the source tree, version and `HEAD`; from the wheel, version and never a wrong
  commit (`unknown` allowed); cost none; the pin's commit stays in the pin's path and the tool registry.
  (b) widen the paths to `.gitattributes` plus one data file substituted by `git archive`; cost small; works only for
  wheels built from an export, so the owner's pin commands must stay as they are. (c) defer to W2-18 (the release
  and its hash-locked install), which owns how a release is built.
- Recommendation: (a) now and (c) for the release, confidence medium. Blocks nothing in this suite.

**P-W2-59-5 (run 2). Does a bare `gov` with a per-command `PYTHONPATH` run the pin or the tree?** (The number is
this README's; the lead numbers its packages.)
- Context: behaviour item 3 ("a test run or a `gov` command that sets `PYTHONPATH` itself still runs the tree's
  code", DEC-732) against DEC-822 item 3 ("chooses only the code under test, not the judge") and the common lead
  brief ("a bare `gov` is the pinned judge").
- What happened: for `PYTHONPATH=<worktree>/src gov <command>` the two readings differ. DEC-732 item 1 says every
  `gov` command used for verification runs the worktree's `src/` with the variable set per command; the pin's own
  script is pip's (`#!<venv>/bin/python`, no `-E`), so today the variable makes the pin's `gov` run the tree's
  code. The brief's verification forms avoid the question (`python3 -m gov.cli.main ...`).
- Options: (a) a command that sets the variable itself is a run of the code under test, whatever its program name;
  only the judge's own entry points (the hook lines, the runner's checks) never take it from the environment; cost
  none (as built). (b) the pin's `gov` always runs its own package (its script ignores the variable); verification
  uses `python3 -m gov.cli.main` only; cost small (the wheel's entry-point script, W2-18's release build).
  (c) defer to W2-18.
- Recommendation: (a), recorded in DEC-732's words, confidence medium. Not tested here; blocks nothing in this suite.

**P-W2-59-6 (run 2). The launch form puts `PYTHONPATH` into every worker session's environment.**
- Context: DEC-732 item 3: "It is set per command, not in a session's environment, so the guard's own hooks keep
  running the code the session started under."
- What happened: the committed launch form sets `PYTHONPATH=<worktree>/src` on the `gov launch` command, and the
  launcher passes its whole environment on to the session (`src/gov/launch/launcher.py:319`). Every launched
  worker therefore runs with the variable in its session environment (this designer's session included), and the
  hook lines inherit it. Run 2's cases close it at the line; the launch remains a second way in for any other
  program that is the judge.
- Options: (a) the launcher drops `PYTHONPATH` from the session's environment (DEC-826 Q5's cleaned environment,
  W2-56), and DEC-732's per-command form stays as it is; cost small; outside this ticket's paths. (b) the line's fix
  alone; cost none. (c) both.
- Recommendation: (c): the line's fix here (this suite requires it) and a row for W2-56, confidence medium.

## Notes for the engineer and the auditor

- The cases need nothing installed: `pip`, `venv`, `setuptools` and PyYAML of the system Python, no network.
- The stand-in's folder must be short enough for a direct `#!` line (pip writes a `/bin/sh` launcher above 127
  characters); the fixture fails with that message if `TMPDIR` is too long.
- The judge's own answers are read from `gov check --json`'s envelope, success or error form (`result.checks` or
  `error.details.checks`), and from `gov doctor --json`'s `canaries` section.
- The probe declaration is a `python3 -c` command: a declared `python3` command that is not a governance module must
  still run, with the judge's interpreter (W1-26 runs declared commands as written).
