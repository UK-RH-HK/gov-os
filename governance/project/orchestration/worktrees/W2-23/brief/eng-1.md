# Brief: engineer, DAEO-kmcr (W2-23), FULL — adoption safety on a real repository (build run, eng-1)

Budget: projection 8 USD. Class C3 (the guard against losing a programme's own files). Keep your context short: read
the parts named below, cut long outputs to head and tail (the week's usage is near its brake, DEC-1126).

You are the engineer for ticket DAEO-kmcr (W2-23), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-23` on branch `w2/W2-23` (DEC-963). An independent test designer is writing the
acceptance tests in parallel on another branch; the lead merges them after your session. You build to the ticket's KPI
lines and its `## Interface`, never to tests.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file whole (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23`, `w2/W2-23`). If
  anything differs, stop and say so.
- **Writes:** only `src/gov/adopt/**`, `src/gov/adapters/**`, `template/governance/project/path-map.yaml`,
  `tests/unit/adopt/**`, `tests/unit/adapters/**`, `fixtures/adopt/**`, `CLAUDE.md`, `AGENTS.md`, and your scratch
  `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/eng/`. Nothing else; never `git add -A`. This repository's
  own `.claude/settings.json` is out of your paths (DEC-315).
- **`src/gov/adopt/stages.py` (the CTO's delegated decision P-W2-23-1 (a), in the ticket):** call sites only, in `a0`,
  `a3` (and its helper `_entry` if the call lands there), `_batch` and `a6`, about 20 lines; the logic goes in a new
  `src/gov/adopt/safety.py`. **Never touch `run()` or `STAGE`** (W2-52 changes them; no hunk may overlap). State the
  stages.py diff's line count in your return.
- **You never read this ticket's acceptance tests** (`tests/acceptance/W2-23/**`, DEC-820, DEC-1063), nor the
  `w2/W2-23-tests` branch or `/home/usain/gov-os-worktrees/W2-23-tests`.
- **Code under test (DEC-732):** every run uses this worktree's `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src`, per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -c "import gov; print(gov.__file__)"`.
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox. Use the Read and Grep tools, naming
  the folder a search starts at; if a search does not answer, search again once in different words, then answer from
  what you read or say "not found". Grep the decision register only by id.
- **Never touch `~/EXAMIN APP` or `~/gov-os-workbench`** (DEC-723): a repository whose path holds a space is one you
  make under your scratch or a test's `tmp_path` (a folder named `EXAMIN APP`).
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/eng/` written with the Write tool, then run. Foreground
  only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal.** Count refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-23` on every run (make it first); pytest's own retention, never
  `--basetemp`. Give `du -sh` of your scratch at the end. Under `.gov-runtime/`, commit hashes as 12 digits.
- On an authentication error return `AUTH_REQUIRED`.

## What you read (in this order)

1. **The ticket, authoritative, in its current text:**
   `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/ticket-DAEO-kmcr.md` (the copy in `.tickets/` of this
   worktree is older and lacks the Interface). Its KPI lines S1–S7 and F1, and `## Interface` items 1–7: **fixed**; a
   gap or clash goes into your return as a package, never a guess.
2. **The context packet:** `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/context-eng.json`; the
   source decisions by id in `docs/DECISION_REGISTER.md`: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112.
3. **The rows:** `governance/project/bootstrap.md` lines 2344–2400 (the adoption residuals each KPI closes) and rows
   `W2-H035`, `W2-H036`, `W2-H050`, `W2-M216`–`W2-M229`, `W2-M232`, `W2-M307`, `W2-M312` in
   `docs/plan/WAVE_2_LIST.md` (Grep by row id; W2-M229 names the auto-compact `env` entry).
4. **The code:** `src/gov/adopt/` (`stages.py` `a0`, `a3`, `_entry`, `_batch`, `a6`; `project.py` `restore`, `commit`,
   `dirty`, `classify`; `legacy.py` `_proof` and `GENERATE`); `src/gov/cli/main.py` (command-module discovery);
   `src/gov/adapters/portability.py`; `template/.gitleaks.toml`; `tests/unit/adopt/test_adopt.py` (its planting
   helpers). `rulesync` 24.0.0 is at `~/.local/bin/rulesync`.

## What you build (Interface items; est. 220 lines of code)

- **S1 / F1 (item 1):** `project.restore` deletes only the paths the caller names as written by the tool; every other
  untracked path (file or directory) stays byte for byte; an untracked directory never raises. Update its callers
  (`project.commit`, `_batch`) to name what they wrote.
- **S4 (item 2):** in `_batch`/`a6` (logic in `safety.py`): per-run rollback refs
  `refs/gov/adoption/rollback/<run-id>/batch-<n>`; a failed batch commits the A6 record with `status: failed`,
  `failed_batch: <n>`, the batches done with commits and dispositions; refusal stays `ADOPT_BATCH_FAILED`; nothing is
  left staged. Running `gov adopt --lite --stage A6` again resumes at the failed batch (done batches are not "not at
  origin"). A killed batch (moves staged, no commit): the next A6 run finds the staged set equal to a recorded
  in-progress batch, unstages it to its rollback point and continues; anything else staged is refused naming the paths,
  never reset. (So an in-progress marker must exist before a batch's moves start; you choose where, and say so.)
- **S5 (item 3):** A0 writes `.gitleaks.toml` (the template's text) when absent and adds `.gov-runtime/` to
  `.gitignore` when not ignored, both in A0's record commit; an existing `.gitleaks.toml` is never touched.
- **S7 (item 4):** A3 refuses `ADOPT_TARGET_UNHELD`, naming each target no namespace holds, before its record is
  written (tree unchanged); A6 refuses the same before any batch.
- **S2 (item 5):** `gov adapters generate` in `src/gov/adapters/command.py` (found by folder; no change to
  `src/gov/cli/main.py`): `rulesync generate` into a temporary folder, then merge `CLAUDE.md`, `AGENTS.md` (programme
  lines in order, then one marked block `<!-- gov:generated begin -->` … `<!-- gov:generated end -->`, replaced in place
  on the next run) and `.claude/settings.json` (key by key, programme keys and list entries first in their order,
  generated keys and hook entries after, an `env` block with the auto-compact entry). A planted fixture repository for
  it may live in `fixtures/adopt/` (own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, untracked files).
- **S3 (item 6):** A8's dependency proof (`legacy._proof`) finds every listed form: a word character or `-` directly
  before the path or id; backslashes; URL-encoding; another letter case; a path split across lines; a citation of only
  the store's folder or a glob; `../` followed by only the tail of the path; an id cited in a record's prose. Each
  found citation printed as found. Do not widen it beyond the list (a form outside it stays not found).
- **S6 (item 7):** make a repository at a path with a space under your scratch; run every `gov` command (`--help` and
  the read invocations item 7 lists) and the six kernel hooks through the settings' hook command lines with
  `CLAUDE_PROJECT_DIR` holding the space. Fix what fails inside your paths. **A failure whose fix lies outside your
  paths** (P-W2-23-3 (a)): do not fix it; return it as a package naming the file and line and the failing output.
- Unit tests for each item in `tests/unit/adopt/` and `tests/unit/adapters/` (planted repositories under `tmp_path`;
  fast; no network). Known limit: "A3 with a move needs `/tmp/gov-cbm-<uid>` writable", so A3 move cases may not run in
  your session; say which, and how they failed.

## Check and commit

1. Your unit tests:
   `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src TMPDIR=/tmp/gov-os-lead-W2-23 python3 -m pytest tests/unit/adopt tests/unit/adapters -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (no test, class, parametrize id or file name of yours may contain `real`, `green_here` or `time_limit`). Quote the
   last line; the existing cases there must stay green.
2. `python3 -m gov.cli.main adapters generate --help` and `adopt --help` exit 0.
3. Commit only your paths, in batches as you go:

       git commit -m "<subject>" --trailer "Task: DAEO-kmcr" --trailer "Role: engineer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

   `Implements:` lists only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.
   Then quote `git log --oneline -5`, `git status --short`, `git diff --stat 219307d1d HEAD -- src/gov/adopt/stages.py`
   and `git diff --name-only 219307d1d HEAD` (only your allowed paths).

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `gov.__file__` line, the unit last line, the `--help` exits, each commit hash with
its trailers, the stages.py diff stat, the S6 run (commands and hooks tried, exits with and without the space),
`du -sh` of your scratch. In `tests`: unit cases per KPI line. Also the refusals met (time, form, reason), every
Interface gap, and where the in-progress marker of item 2 lives.
