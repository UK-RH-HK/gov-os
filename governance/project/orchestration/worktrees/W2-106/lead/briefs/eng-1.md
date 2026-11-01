# Brief: engineer, DAEO-0mtg (W2-106), run 1

You are a fresh engineer. Ticket: DAEO-0mtg (W2-106), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-106` on branch `w2/W2-106`. You implement the ticket to its specification and KPIs
(never to the tests).

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0mtg','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0mtg`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-106` and `w2/W2-106`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Commit your work before you run any long suite.
  Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag. The only
  merge you make is the one below (TESTS-READY), with `--no-ff`.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src` set per
  command (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -m gov.cli.main retrieve "<question>" --json`. This
  worktree's store is not built yet (the shared rebuild lock is held by the nightly): if that answers STORE_MISSING,
  retrieve from the integration branch's store instead, a read: `cd /home/usain/gov-os-worktrees/W2-00-store && gov
  retrieve "<question>" --json` (it holds `w2/integrate`; nothing of this ticket is in it yet). Never run a rebuild
  yourself. Never one
  giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked
  and stacked. A code question (DEC-859) uses the code-graph tool's own traversal (`trace_path`, `search_graph`,
  `query_graph`), small and targeted, never a load of the whole graph.
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read `tests/acceptance/W2-106/`, by any tool (and never anything in
  `/home/usain/gov-os-worktrees/W2-106-tests`); you may run those tests and see their names, results and failure
  messages, never their source.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name
  only and clone into a temporary folder.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal you
  meet and list it in your return.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; put anything longer in a script file under
  `/home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/eng/` with the Write tool and run it.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); copy
  single named files only, never `governance/project/`. A test that needs a project builds a temporary one. Inside a
  launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it. Never write
  `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Install nothing (raise it as a P1 in your return). A throwaway wheel and venv built from this worktree's code in a
  temporary folder with no network (as W2-59's suite does) is not an install.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 6 GB and
  300,000 files and folders outside the tracked tree. `TMPDIR` is set by the launcher's sandbox: keep it. Keep
  pytest's own retention (never `--basetemp`); use `-o tmp_path_retention_policy=failed`. Clean up every temp tree
  you made. Give `du -sh` and `du -s --inodes` of your scratch at the end.
- **Machine load (DEC-847):** before a suite run, wait while both the 1- and 15-minute loads are at or above the
  CPU count.

## What you read

- The ticket `.tickets/DAEO-0mtg.md` (read-only): its KPI lines and `allowed_paths`.
- In `docs/DECISION_REGISTER.md`: DEC-966 (item 2), DEC-822 (items 1 to 3), DEC-957, DEC-965, DEC-801, DEC-616,
  DEC-917 (the four lifecycle lines keep DEC-608's plain form), DEC-880 item 3 and DEC-913 item 1 (the exit-mapping
  form), DEC-732.
- `governance/project/orchestration/packages/P-W2-90-1.md` (P1-B).
- **The pinned form:** this repository's own guard lines in `.rulesync/hooks.jsonc` (the `preToolUse` entry) — the
  form the KPI asks for. (Do not read `.claude/settings.json`; the rulesync source holds the same line.)
- The two files you change: `template/governance/kernel/settings.json` and `template/.rulesync/hooks.jsonc`.
- How a product is generated and its lines run: `tests/acceptance/W2-90/README.md`, W1-38's and W1-39's suites and
  support modules (you may read these; they are not this ticket's tests).

## What you build (the KPI lines)

Success:
1. Each of the template's three guard hook lines (pre-tool, and the two post-tool lines: PostToolUse and
   PostToolUseFailure on Bash), in `template/governance/kernel/settings.json` and in their rulesync source
   `template/.rulesync/hooks.jsonc`, takes this repository's pinned form (DEC-822, W2-59): it finds the installed gov
   (`$HOME/.local/bin/gov`, else `gov` on PATH), reads the interpreter its first line names, and runs the hook with
   that interpreter and `-E`; the line's exit codes are kept (0 and 2 pass through; any other ends in a refusal).
   The program path stays the product's: `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>.py`.
2. Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2)
   with a message naming what is missing; it never falls back to a bare `python3`.
3. A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing
   at an edited copy of gov that would allow a refused write, the hook still refuses it.
4. A generated project's hook lines equal the template's source after `rulesync generate` (the two sources stay in
   step), and the template's own suites (W1-38, W1-39) pass.

Failure: a template guard line that runs a bare `python3` or has no `-E`; a missing or broken gov that lets the hook
pass or falls back to another interpreter; an edited gov on PYTHONPATH that lets a refused write through; the
settings and the rulesync source out of step, or W1-38 or W1-39 red.

Scope (lead's reading, P3): the three guard lines only. The four lifecycle lines of `template/.rulesync/hooks.jsonc`
(sessionStart, stop, preCompact, subagentStop) keep DEC-608's plain form by DEC-917 (W1-38 holds them to it): do not
change them. Nothing under `src/gov/adopt/` changes (the ticket: no adoption step; if you find a reason for one, it is
a package). Never make a guard decision fail open: each failure KPI must still refuse. Proportion (DEC-135): no code
for edge cases beyond the KPIs.

## What you write

- Only inside the ticket's `allowed_paths`: `template/governance/kernel/settings.json`,
  `template/.rulesync/hooks.jsonc`, and your builder tests at `tests/unit/hooks/test_w2_106*.py` (regression
  evidence only, test-driven: write them first, see them red, then change the lines). Never `tests/acceptance/**`.
- Run, to their end (never `-x`), each in the foreground, after you commit:
  - your builder tests;
  - the template's own suites, which KPI 4 names: `tests/acceptance/W1-38` and `tests/acceptance/W1-39`;
  - the other suites that read or run the template's guard lines, to see what your change does to them:
    `tests/acceptance/W1-47`, `tests/acceptance/W2-65`, `tests/acceptance/W1-05`, and the W2-59 files
    `test_w2_59_hook_lines.py` and `test_w2_59_hook_lines_worker_env.py`.
  Use `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
  A red there that your change causes and that your change can fix inside your paths, fix. A red that needs another
  ticket's test revised (its harness gives the line no pinned gov to find, or it asserts the old bare `python3`
  form) is **not edited by you**: name it in your return with its failure message, as a package. A red that also
  fails on the base (`git stash` is forbidden; judge by the failure message, or say you could not tell) is named.
- **TESTS-READY (DEC-963):** the test designer works in parallel in its own worktree. When
  `/home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/TESTS-READY` exists — at your next step, or when you
  have built and committed — run `git merge --no-ff w2/W2-106-tests -m "W2-106: merge the acceptance tests" --trailer "Task: DAEO-0mtg" --trailer "Role: engineer"`
  (if your git has no `--trailer` on merge, put the two trailer lines in the message's last paragraph), then run the
  acceptance tests once, reading results only:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -m pytest tests/acceptance/W2-106 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
  If any fail, fix the implementation to the spec (never to a test's internals, which you never read); a test you
  think is wrong is returned as a package, never edited. If TESTS-READY does not exist when you are done, say so and
  return (the lead merges them and starts a fresh engineer to run them).

## Commit

Before each commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only
`*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only your paths, with the trailers in the
final block:

    git commit -m "W2-106: the template's guard hook lines run the installed gov's interpreter with -E, fail closed" --trailer "Task: DAEO-0mtg" --trailer "Role: engineer" --trailer "Implements: DEC-966" --trailer "Implements: DEC-822" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After every commit: `git log --oneline -2` and `git status --short`.

## Return

Your commit hashes (12 digits); the files changed; lines added and removed (estimate: about 60); every suite you ran
with its counts; the `gov.__file__` line; the acceptance result once merged (names of any failing cases with their
messages); every other ticket's case your change turned red, with its message; the `gov retrieve` queries you ran;
the guard refusals you met; anything refused or unsettled, as a package (question, why now, options, impact,
reversibility, cost, recommendation, confidence).

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
