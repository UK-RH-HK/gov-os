# Brief: product-spec worker, DAEO-zpdj (W2-105), run 2, the acceptance run through `gov accept`

You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-zpdj (W2-105), profile STANDARD. You work only in
the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105` (head `fa653609cc93`). The ticket's change
is committed (`b868b60a2a56`: the template's `npm install*` and `pip install*` deny rules removed from
`template/.rulesync/permissions.jsonc`, DEC-966 item 1), and the independent test designer's acceptance tests are
merged. KPI 2 was re-baselined by the owner (DEC-971 item 4): in a generated project an install reaches the guard's
install rule (nothing denies it before the guard is asked); the product's CTO-only install rule is W2-110's, not this
ticket's. Your task: run the ticket's acceptance tests once, through `gov accept`, and report the result per KPI line.
**You change nothing and commit nothing** in this run: if a line fails, you report it; the lead decides what follows.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zpdj','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-zpdj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-105` and `w2/W2-105`)
  and `git rev-parse --short=12 HEAD` (expect `fa653609cc93`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another (no command longer than about nine minutes; `gov
  accept` takes `--timeout 540`).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no commit, no
  push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m gov.cli.main retrieve "<question>" --json`. This
  worktree's store is being rebuilt by the lead now; if it answers STORE_MISSING or hangs, retrieve from the
  integration branch's store instead, a read: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve
  "<question>" --json`; if that hangs too (the sandbox blocks the network), stop it and say so. Never one giant query
  (DEC-860): batches with `--batch-size`, then `--continue <token>`. A code question (DEC-859) uses the code-graph
  tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole
  graph. This task needs little knowledge: one or two queries at most (for example, what `gov accept` reports).
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read this ticket's acceptance tests: nothing under `tests/acceptance/W2-105/`, by any tool (not its
  README either). You run them through `gov accept` and read only what it reports.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name
  only.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces. Your sandbox mounts `tests/` and `.gov-runtime/scratch/`
  read-only: write no file there.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it. No clone, copy or programme file under any `.gov-runtime/` folder
  (DEC-673). `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it. Install nothing
  (an install is a P1 in your return).
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits, never the full 40, and never write the keywords
  of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 2 GB and
  100,000 files and folders. `TMPDIR` is set by the launcher's sandbox: keep it. Remove anything you make as soon as
  it is no longer needed; name in your return any file you could not remove.

## What you do

1. Read the ticket `.tickets/DAEO-zpdj.md` (its KPI lines) and `git log --oneline -5`.
2. The import check (above), quoted.
3. Run the acceptance tests once, to their end, through `gov accept` only (never `pytest` on `tests/acceptance/`):
   `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src python3 -m gov.cli.main accept DAEO-zpdj --json --timeout 540`
   Note its exit code and the time it took.
4. Report its whole output (it carries no test content: pass or fail per KPI line and the counts). If it reports an
   error kind instead of results (for example a tool missing inside the sandbox), say so, with the kind; do not try
   another way of running the tests.

## Return

The sandbox check; the `gov.__file__` line; `gov accept`'s exit code, time and whole output; the `gov retrieve`
queries you ran and whether they helped; the refusals you met.

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
