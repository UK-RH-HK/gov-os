# Brief: independent test designer, DAEO-kmcr (W2-23), FULL — adoption safety on a real repository (build run, td-1)

Budget: projection 4 USD. Class C3 (the guard against losing a programme's own files). Keep your context short: read
the parts named below, cut long outputs to head and tail (the week's usage is near its brake, DEC-1126).

You are a fresh independent test designer (MR-3). Ticket: DAEO-kmcr (W2-23), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-23-tests` on branch `w2/W2-23-tests` (DEC-963). You never read or write the ticket's
own worktree, `/home/usain/gov-os-worktrees/W2-23` (an engineer is building there now). You write the acceptance tests
**before** the implementation, from the ticket's KPI lines and its `## Interface` section; they must run red now for the
right reason (the behaviour is missing), never by a collection error.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23-tests`,
  `w2/W2-23-tests`). If anything differs, stop and say so.
- **Writes:** only `tests/acceptance/W2-23/**` (and your scratch `.gov-runtime/scratch/td/`). Nothing else.
- **Code under test (DEC-732):** every test run uses this worktree's own `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src`, set per command. Quote in your return
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src python3 -c "import gov; print(gov.__file__)"`. Every child
  process a test starts gets the repository's `src` first on its `PYTHONPATH`, taken from the test file's own location
  (never a hard-coded worktree path), and a planted empty `HOME` under `tmp_path`.
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox. Use the Read and Grep tools, naming
  the folder a search starts at; if a search does not answer, search again once in different words, then answer from
  what you read or say "not found". Grep the decision register only by id.
- **Policy 2 (DEC-820):** reads are open except secrets, the held-out material's contents, this ticket's implementation
  (never anything in `/home/usain/gov-os-worktrees/W2-23`) and the hidden half of any evaluation set.
- **Never touch `~/EXAMIN APP` or `~/gov-os-workbench`** (DEC-723): the path with a space is a folder named
  `EXAMIN APP` that a test makes under its own `tmp_path`.
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/td/` written with the Write tool, then run.
  Foreground only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal.** Count refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-23` on every run (make it first); pytest's own retention
  (`-o tmp_path_retention_policy=failed`), never `--basetemp`. Give `du -sh` of your scratch at the end.
- Under `.gov-runtime/`, commit hashes as 12 digits, never 40 (DEC-911). On an authentication error return
  `AUTH_REQUIRED`.

## What you read (in this order)

1. **The ticket, authoritative, in its current text:**
   `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/ticket-DAEO-kmcr.md` (the copy in `.tickets/`
   of this worktree is older and lacks the Interface: use the scratch copy). Its `kpis` (seven `success` lines S1–S7,
   one `failure` line F1, each with a `Verify:` clause) and its `## Interface` (items 1–7). **The Interface is fixed:**
   you write tests to it, never change or reinterpret it. A gap or clash you find (between two items, or with a KPI
   line) goes into your return as a package (`proposed_decisions`: question, options with cost, recommendation,
   confidence, what it blocks); write the test to the Interface's words where they are clear and leave the unclear
   point untested and named.
2. **The context packet:** `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/context-td.json`. Read
   each source decision by id in `docs/DECISION_REGISTER.md`: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112.
3. **The rows behind the KPIs:** `governance/project/bootstrap.md` lines 2344–2400 (the residuals of the adoption
   build and probe: S1's line 2393, S3's line 2362, S4's lines 2352–2357, S5 and S7's lines 2344–2347), and the rows
   `W2-H035`, `W2-H036`, `W2-H050`, `W2-M216`–`W2-M229`, `W2-M232`, `W2-M307`, `W2-M312` in `docs/plan/WAVE_2_LIST.md`
   (Grep by row id).
4. **Today's interfaces you drive and plant for** (read the shapes only, to plant inputs they accept): `src/gov/adopt/`
   (`command.py` the CLI, `stages.py` the stages and `_batch`, `project.py` `restore`/`commit`/`classify`,
   `legacy.py` `_proof` for A8's dependency proof); the adoption skill
   `template/governance/kernel/skills/adopt/` and the existing adoption acceptance helpers
   (`tests/acceptance/W1-41/w1_41_support.py`, `tests/acceptance/W2-81/w2_81_run.py`: reuse their way of planting a
   project and running stages A0–A8);
   `src/gov/cli/main.py` (`COMMANDS` and the command-module discovery, for S6 and for `gov adapters generate`);
   `template/governance/kernel/hooks/` (six hooks) and the hook command lines in
   `template/governance/kernel/settings.json` / `template/.rulesync/hooks.jsonc`; `template/.gitleaks.toml`;
   `rulesync` 24.0.0 is installed at `~/.local/bin/rulesync`.
5. **The form of an acceptance folder:** `tests/acceptance/conftest.py`, `tests/acceptance/serial-only.txt`, one recent
   folder's README map (e.g. `tests/acceptance/W2-112/README.md`); `gov accept` reads the map with
   `gov.accept.runner.parse_map` (`src/gov/accept/runner.py`): it must list every KPI line (`S1`..`S7`, `F1`) against
   its cases.

## What you write

`tests/acceptance/W2-23/`: a README (what the tests reach, how to run them, the KPI map in the runner's form, the
expected-red table), a conftest and a support module that **plant everything under pytest's `tmp_path`**: a git
repository with the programme's own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json` (each holding its own distinct
lines), tracked and **untracked** files (and an untracked directory), a path map, no `.gitleaks.toml` and a `.gitignore`
without `.gov-runtime/` where a case needs that; and the same repository inside a folder named `EXAMIN APP`.

Drive the tool the way its callers do: `python3 -m gov.cli.main adopt --lite --stage A<n> ...` and
`python3 -m gov.cli.main adapters generate ...` as child processes (exit codes, refusal codes and printed lines per the
Interface), importing Python only where an Interface item names a function (`project.restore`). **Collection must
succeed while the new code does not exist** (`gov.adopt.safety`, `gov.adapters.command`): import inside the test or go
through the child process.

Cover every KPI line by its own `Verify:` clause and the Interface item it names, at least:
- **S1 (item 1):** one untracked file the user made before the batch and one the batch made (and an untracked user
  directory): after the restore that a failed stage or batch runs, the user's file is byte for byte present (or the
  run refuses naming it) and the batch's file is gone; an untracked directory does not raise.
- **S2 (item 5):** after `gov adapters generate`, each of `CLAUDE.md` and `AGENTS.md` holds every programme line in its
  original order, then one block between `<!-- gov:generated begin -->` and the end marker; a second run replaces the
  block in place (one block, programme lines unchanged); `.claude/settings.json` keeps the programme's keys and list
  entries in their order with generated keys and hook entries after, and an `env` block with the auto-compact entry;
  none of the three is the generated file alone.
- **S3 (item 6):** a planted set with one citation of each listed form (eight forms in item 6); A8's proof prints each
  as found; one planted citation of an unlisted form of your choice (named in the test and README) is the only one
  not found. Find where A8 prints the proof (`legacy.py`) and drive it through A8 or the entry point the output shows.
- **S4 (item 2):** a plan whose third batch fails (e.g. a planted commit hook that refuses it, or a target made taken):
  the A6 record is committed with `status: failed`, `failed_batch: 3`, batches 1–2 with commits and dispositions,
  rollback refs under `refs/gov/adoption/rollback/<run-id>/batch-<n>`, refusal `ADOPT_BATCH_FAILED`; `git status`
  shows nothing staged; running `gov adopt --lite --stage A6` again continues at batch 3. And a killed batch (moves
  staged, no commit — plant that state or kill the process between steps; your choice, stated): the next A6 run
  unstages to the rollback point and continues there; anything else staged is refused naming the paths and left as is.
- **S5 (item 3):** a project with neither `.gitleaks.toml` nor the ignore line: A0's record commit adds
  `.gitleaks.toml` (the template's text) and `.gov-runtime/` to `.gitignore`; an existing `.gitleaks.toml` is untouched
  byte for byte; A3 with a move and A8 then do not refuse for either.
- **S6 (item 7):** in the `EXAMIN APP` repository, every name in `gov.cli.main` `COMMANDS` plus the discovered command
  modules, each with `--help`, and the read invocations item 7 lists, exit as they do in the same repository at a path
  without a space, and no output holds a word-splitting or path error; the six kernel hooks, fed a minimal event JSON
  through the settings' own hook command lines with `CLAUDE_PROJECT_DIR` holding the space, exit as they do without it.
- **S7 (item 4):** A3 with a move to a target no namespace holds refuses `ADOPT_TARGET_UNHELD` naming the target, before
  its record is written (the tree and HEAD unchanged); A6 refuses the same before any batch.
- **F1:** sha256 of the instruction files and every untracked file listed before an adoption run that ends in a
  rollback (a failed batch) and after: equal; a difference is named in the assertion message.

**Known limit:** "A3 with a move needs `/tmp/gov-cbm-<uid>` writable, so the move cases cannot run in a launched
session" (bootstrap.md). Write those cases normally (no skip, no `local_only`); say in the README and your return which
cases cannot run in your session and how they failed there; the lead runs `gov accept` outside the sandbox.

**Naming (DEC-1065):** whole-folder runs deselect `-m "local_only"` and `-k "real or green_here or time_limit"`. So
**no test name, class name, parametrize id or file name may contain `real`, `green_here` or `time_limit`** (write
"actual", "true", not "real"), or the case silently never runs. Mark `local_only` only a case that cannot run in CI,
and name it in the README. Keep the whole folder well under three minutes; no network; no GPU.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src TMPDIR=/tmp/gov-os-lead-W2-23 python3 -m pytest tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`:
   it must collect every case with no collection error and run red; quote the last line and the count collected
   (`--collect-only -q` with the same filters, last line). Say which cases, if any, pass on today's code and why (S6
   may in part).
2. Check the README map with a small script under `.gov-runtime/scratch/td/` calling `gov.accept.runner.parse_map`:
   every one of S1–S7 and F1 maps to at least one case; quote its output.
3. Commit only `tests/acceptance/W2-23/**`:

       git commit -m "W2-23 acceptance: adoption safety on a real repository, S1-S7 and F1 from the KPI lines and the Interface" --trailer "Task: DAEO-kmcr" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-23

   `Implements:` lists only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.
   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why.
In `evidence`: the sandbox check's result, the `gov.__file__` line, the collect and run last lines, the map check's
output, the commit hash with its trailers, `du -sh` of your scratch. In `tests`: cases per KPI line and the expected-red
table in short, and the cases your session could not run. Also say the refusals met (time, form, reason) and every
Interface gap you found.
