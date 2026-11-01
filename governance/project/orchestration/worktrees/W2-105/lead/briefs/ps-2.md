# Brief: product-spec worker, DAEO-zpdj (W2-105), run 1, the acceptance run

You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-zpdj (W2-105), profile STANDARD. You work only in
the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105`. The ticket's change is committed
(`b868b60a2a56`: the template's `npm install*` and `pip install*` deny rules removed from
`template/.rulesync/permissions.jsonc`, DEC-966 item 1), and the independent test designer's acceptance tests are
merged (`be944228`). Your task: run the ticket's acceptance tests once and report the results; if any fails, fix the
ticket's file to its specification (never to the tests), within its path.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zpdj','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-zpdj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-105` and `w2/W2-105`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another (no command longer than about nine minutes).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This
  worktree's store is not built yet, so retrieve from the integration branch's store, a read:
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (stdout only). Never one giant
  query (DEC-860): batches with `--batch-size`, then `--continue <token>`. A code question (DEC-859) uses the
  code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted. If it hangs
  (the sandbox blocks the network), stop it and say so.
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read this ticket's acceptance tests: nothing under `tests/acceptance/W2-105/`, and not the two files
  of `tests/acceptance/W1-38/` the test designer revised (`test_w1_38_test_folder_rule.py`, `README.md`), by any
  tool. You run them and read their results (names, pass or fail, failure messages), never their source.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces. Your sandbox mounts `tests/` and `.gov-runtime/scratch/`
  read-only: write no script there (use your session's own `TMPDIR` if you need one).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). A refusal you needed for the ticket is
  returned as a package, never worked around.
- Never copy the repository or a folder of it. No clone, copy or programme file under any `.gov-runtime/` folder
  (DEC-673). `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it. Install nothing
  (a P1 in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 4 GB and
  200,000 files and folders. `TMPDIR` is set by the launcher's sandbox: keep it. Keep pytest's own retention (never
  `--basetemp`); use `-o tmp_path_retention_policy=failed`.
- **Machine load (DEC-847):** before the run, wait while both the 1- and 15-minute loads are at or above the CPU
  count (`python3 -c "import os; print(os.getloadavg(), os.cpu_count())"`, checked every minute).

## What you do

1. Read the ticket `.tickets/DAEO-zpdj.md` (its KPI lines) and `git log --oneline -5`.
2. Run the acceptance tests once, to their end (never `-x`):
   `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m pytest tests/acceptance/W2-105 tests/acceptance/W1-38/test_w1_38_test_folder_rule.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
3. If every case passes, commit nothing and return.
4. If a case fails, read its failure message only, decide whether the ticket's file falls short of its specification
   and KPIs; if it does, fix `template/.rulesync/permissions.jsonc` (your only path), check the hooks folder
   `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file, commit with
   `git commit -m "<subject>" --trailer "Task: DAEO-zpdj" --trailer "Role: product-spec" --trailer "Implements: DEC-966" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`,
   and run step 2 once more. If you think a test is wrong, return it as a package; never edit or work round it.

## Return

The `gov.__file__` line; the run's counts and time; each failing case's name and failure message; any commit's hash
(12 digits); the `gov retrieve` queries you ran and whether they helped; the refusals you met; any package.

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
