# Brief: engineer, DAEO-drhj (W2-104), run 2 — one line (P-W2-104-CMDLIST (a), DEC-1020)

You are a fresh engineer. Ticket: `DAEO-drhj` (W2-104), profile STANDARD. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-104` on branch `w2/W2-104`. The ticket's harness (`gov skilleval`, in
`src/gov/skilleval/`) is built and committed. Your whole task: record the new command in the code's command list.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-drhj','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-drhj`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104` and `w2/W2-104`),
  and `git rev-parse --short=12 HEAD` (expect `4ee33fec` at its start) with `git status --short` (expect nothing).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Reads (DEC-820, Policy 2):** you read freely, except: (a) secrets and keys, never read or printed; (b) the
  contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under
  `governance/project/`, never type its path; never read or name the qualification oracle); **(c) the counterpart's
  work on this ticket: you never read `tests/acceptance/W2-104/`** by any tool; you may run those tests only through
  `gov accept` and see names, results and failure messages, never their source; **(d) the hidden half of any
  evaluation set** is never read by whoever is measured by it. Never write in `~/gov-os-workbench`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m gov.cli.main retrieve "<question>" --json` (for
  example, "DEC-747 recorded gov commands"). **Never one giant query (DEC-860):** a large question goes in batches
  (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal
  (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. This task
  needs little: the file below is short.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders
  instead. Count the refusals you met and report them.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- Never copy the repository or a folder of it. Install nothing (an install is a P1 package in your return). No
  subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never
  write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders, outside the tracked tree. `gov
  launch`'s sandbox sets your session's own `TMPDIR`: keep it, never set it yourself. Keep pytest's own temp
  retention (never `--basetemp`); add `-o tmp_path_retention_policy=failed`. Measure your session's `TMPDIR` at the
  end (`du -s --inodes` and `du -sh`) and give the figures.

## The change (DEC-747, DEC-1020)

In `/home/usain/gov-os-worktrees/W2-104/src/gov/check/commands.py`, add `"skilleval"` to the tuple
`RECORDED_GOV_COMMANDS` (keep the existing entries and their order; append it at the end). **Nothing else in that
file, and no other file.** Your allowed paths take this file for this one line only (DEC-1020).

Check it, to the end, never `-x`:
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "from gov.check.commands import RECORDED_GOV_COMMANDS, GOV_COMMANDS; print(RECORDED_GOV_COMMANDS)"`
- `cd /home/usain/gov-os-worktrees/W2-104 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m gov.check.commands; echo exit=$?` (exit 0: no command lacks its module)
- `cd /home/usain/gov-os-worktrees/W2-104 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -m pytest tests/unit/check/test_check.py tests/unit/check/test_kernel_followup.py tests/unit/accept/test_w2_96_run2.py tests/unit/skilleval -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
- `git diff --stat` must show one file, one line added (one changed if the tuple stays on one line).

Your lead runs the wider suites (W1-26, the scoped selection) after you return; you do not.

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only
`*.sample`); if one is there, stop and return. Never `--no-verify`. Then commit only that file:

    git add src/gov/check/commands.py
    git commit -m "W2-104: record skilleval in RECORDED_GOV_COMMANDS (DEC-747, DEC-1020)" --trailer "Task: DAEO-drhj" --trailer "Role: engineer" --trailer "Implements: DEC-747,DEC-1020" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short` (nothing).

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start
of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them.
Include: the sandbox check's result first in `evidence`; your commit's 12-digit hash and trailers; the diff stat; the
tests you ran with their counts; the `gov.__file__` line; whether you used `gov retrieve`; the read refusals you
met; your scratch figures; anything you were refused or could not settle, as a package. Refused twice for the same
call: stop and say so.

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
