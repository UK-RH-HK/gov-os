# Brief: engineer, DAEO-neam (W2-45), run 1 (batch 1: implement to the Interface, with unit tests)

You are a fresh engineer. Ticket `DAEO-neam` (W2-45), `gov check` runner semantics and scale, profile STANDARD, class
C2. You work only in `/home/usain/gov-os-worktrees/W2-45` on branch `w2/W2-45`. You implement the ticket's
`## Interface` (DEC-1052, accepted by the CTO) exactly; you never change it. A gap or contradiction in it comes back as
a package, never a guess.

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-neam`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-45`, `w2/W2-45`). If
  anything differs, stop and say so.
- Everything in the foreground, one command after another; return only after your commit exists.
- No `git checkout` of another commit, `reset`, `clean`, amend, rebase, merge, push or tag.
- **Allowed paths (write only these):** `src/gov/check/runner.py`, `src/gov/check/commands.py` (W2-159's line kept;
  touch it only if a module list needs it), `src/gov/decisions/checker.py` (speed only: no change of what it finds),
  `tests/unit/check/**`. Never write `tests/acceptance/`; the independent test designer writes
  `tests/acceptance/W2-45/` in parallel, and you do not read their worktree `/home/usain/gov-os-worktrees/W2-45-tests`.
- **Code under test (DEC-732):** every test run and every `gov` command runs this tree's `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src` per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest goes through the heavy-job slot**, with a TMPDIR outside the repository and outside `~/gov-os-runs`,
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, e.g. in
  `/home/usain/gov-os-worktrees/W2-45`:
  `env TMPDIR=/tmp/gov-os-lead-W2-45-eng PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/check -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (`mkdir -p /tmp/gov-os-lead-W2-45-eng` first). A whole-folder run adds `-m "not local_only" -k "not real and not
  green_here and not time_limit"` and `HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home`.
  Never `--basetemp`. Do not name a test with the substrings `real`, `green_here` or `time_limit` (it would be skipped
  in whole-folder runs).
- **Reads (DEC-820):** open, except secrets and keys (never printed), the held-out qualification material's contents
  (never read, search or type its path under `governance/project/`), the counterpart's work on this ticket (the tests
  worktree above, until the lead merges the tests into your tree), the hidden half of any evaluation set.
- **Search (DEC-1065):** no `gov retrieve`, no `gov context` in the sandbox; use Read and Grep, and search again once
  in different words if the first answer is thin. Grep the register only by id. No search from the repository root,
  `governance/project/` or `.claude/`; name folders.
- **Command forms:** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long
  inline `python3 -c`. Write files with Write/Edit at literal absolute paths; anything longer than a line goes in a
  script under `/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/eng/` that you run.
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another command, form or file
  (DEC-1142 (9)); return it as a package.
- Never copy the repository or a folder of it. Install nothing. No subagents that write. Write nothing under
  `.gov-runtime/` outside `.gov-runtime/scratch/`. Never ask the owner. Commit hashes: 12 digits, never 40.
- Scratch: at most 4 GB / 200,000 files outside the tracked tree; remove what you made when done; give `du -sh` and
  `du -s --inodes` of `/tmp/gov-os-lead-W2-45-eng` and your scratch at the end.

## What you read

- The ticket `.tickets/DAEO-neam.md` (read-only): KPI lines S1 to S5 and the `## Interface`, items 1 to 8. That is the
  specification; implement every item as written.
- DEC-729 (source), DEC-595 (TIMEOUT_S), DEC-612 (the success form), DEC-620 (`enforces`) in
  `docs/DECISION_REGISTER.md`, by id.
- `src/gov/check/runner.py` (all of it), `src/gov/cli/checks.py` (declarations), `src/gov/check/command.py`,
  `src/gov/check/authority.py` (core-authority wraps the decision checker), `src/gov/decisions/checker.py`, and the
  existing `tests/unit/check/` (keep them green).

## The work (batch 1)

1. **runner.py, Interface items 1, 2, 4, 5, 6, 7.** `elapsed_s` and `time_limit_s` on every check result (built-ins
   too) and top-level `time_limit_s` = `TIMEOUT_S`; `CHECK_UNMEASURED` (all three forms of item 4, with its `reason`
   where given); `CHECK_TOOL_ABSENT` (exit 127 or OSError on start, naming the command's first word as written in
   the declaration, RED when hard-block, YELLOW when warning) and `OPENSPEC_ABSENT` RED; `POLICY_TIER_TOO_LOW` (item
   6's exact fields); the process-group stop (`start_new_session=True`, `os.killpg` on timeout, then collect) with
   `CHECK_TIMED_OUT` carrying `time_limit_s`. Item 8 stays unchanged (roll-up, exit rule, exit-2 not-applicable path).
2. **S1, the decision checker's speed (item 3).** Build a benchmark script in your scratch (not committed) that plants
   under your TMPDIR a repository of 200 decision records and 20,000 commits with `git fast-import` (many commits
   touching decision files, some setting a decision ACTIVE with and without a `Role: owner` trailer), holding
   `template/governance/kernel/checks/core-authority.yaml`; run `gov check --json --root <it>` and read core-authority's
   `elapsed_s`. If it is not well under 60 s (aim < 20 s on this loaded machine), make `src/gov/decisions/checker.py`
   faster without changing its findings (e.g. one `git log` pass instead of one git process per file or commit), and
   show the before/after times and that `tests/unit/decisions/` (if present) and the decision checker's existing
   tests still pass. Report the numbers either way.
3. **Unit tests in `tests/unit/check/`** (file names `test_w2_45_*.py`): S5 as item 7 states (a planted check
   `sleep 30` with `timeout-seconds: 1` -> `CHECK_TIMED_OUT`, `time_limit_s` 1 in the result, ends in < 10 s; also a
   grandchild holding the pipe), and the S2, S3, S4 rules at the runner level (`run_checks` on a planted tmp project).
   Run `tests/unit/check` and `tests/unit/decisions` (if it exists) to green, through the slot.
4. **This repository's own `gov check` under the new rules.** Once done, run
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src python3 -m gov.cli.main check --json --root /home/usain/gov-os-worktrees/W2-45`
   (output to a file in your scratch) and list every check that is now RED or not green because of S2/S3 (a check
   printing "unmeasured" with exit 0, an absent tool, or a tier too low) with its check id and finding code. Do not
   change any declaration or other path to hide one: name each in `discoveries`.

Commit when the unit tests pass (one or more commits), then return: the lead merges the acceptance tests into your
tree between batches and starts batch 2 to bring them to green.

## Commit

Only your paths:

    git commit -m "W2-45: <subject>" --trailer "Task: DAEO-neam" --trailer "Role: engineer" --trailer "Implements: DEC-729" -- <your paths>

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: (DONE | PACKAGES | ESCALATION ...) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include: the sandbox check first in `evidence`; your commits' 12-digit hashes with trailers; each suite's counts; the
S1 benchmark numbers (before/after, elapsed_s vs 60); the `gov.__file__` line; this repository's own `gov check` reds
under S2/S3/S4 by check id; read refusals met; scratch figures; any package (question, options with cost,
recommendation, confidence, what it blocks).
