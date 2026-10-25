You are a fresh independent test designer (MR-3). Ticket: DAEO-ye2a (W2-72), profile FULL. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-72` on branch `w2/W2-72`. You are a fresh session of the test designer's
role, asked for one small batch on this ticket's own acceptance tests, after the implementation began. Your time
budget is about 60 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ye2a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ye2a`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-72` and `w2/W2-72`).
If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used
  for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src` set **per
  command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned
  judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one
  (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads that Policy 2 opened (searches
  that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look
  for another spelling, search named folders instead, and count the refusals you met in your return.
- **Policy 2 (DEC-820):** you read freely: the whole repository, git history, other worktrees. Only four things are
  refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file
  names may be seen); (c) the counterpart's work on this ticket: **you never read this ticket's implementation**,
  that is the files `git diff --name-only w2/integrate...HEAD` names other than the acceptance tests:
  `src/gov/guard/containment.py`, `src/gov/guard/containment_merge.py`, `tests/unit/guard/test_w2_72_merge_rule.py`,
  and the engineer's commit `e45aecc6dde6` (no Read, cat, grep, diff, `git show` or `git log -p` of them); (d) the
  hidden half of any evaluation set, by whoever is measured by it.
- **Protected material:** never read, print, search, diff or copy the held-out file under `governance/project/`, and
  never type its path (DEC-525). Never read or name the qualification oracle. Never write in `~/gov-os-workbench`,
  and never list or search it.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a
  folder of it. Nothing is ever put under a `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze`
  shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents, inline scripts it cannot read, and unresolvable variables in Bash write targets:
  write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No
  push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Temp folder:** do not set `TMPDIR` yourself; keep the one your launched session already has. Keep pytest's own
  temp retention (never `--basetemp`).
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the
  tracked tree. **Your share is 3 GB and 150,000 files and folders.** Remove what you make by hand when done; never
  run the whole project's suite (the collection below is not a run). If you would pass your share, stop and say so.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never
  write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
  The test files keep writing no full commit id.
- **Memory used (DEC-836, DEC-860, DEC-859):** for what you need to know, use `gov retrieve` first
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m gov.cli.main retrieve "<question>" --json`; this
  worktree now has a store) before reading files at random. Never one giant query or context: a large question is
  taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question
  uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a
  load of the whole graph. Say in your return whether you used `gov retrieve`.
- Never ask the owner anything and never notify anyone; a question is a package in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- The git hooks are uninstalled: before your commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks`
  holds no `pre-commit` file (only `*.sample`); if one is there, stop and say so. Never `--no-verify`, never
  `core.hooksPath`.

## Why this batch

The lead's full verification in the close's form found one red that this ticket causes, in an earlier ticket's
regression case:

    tests/acceptance/W2-66/test_w2_66_lead_verification.py::test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes
    AssertionError: the ticket changes what a plain pytest run reads: ['tests/acceptance/W2-72/conftest.py']

That case (W2-66's KPI 12, DEC-880 item 2 (b)) refuses any `conftest.py` that a ticket's branch adds against
`w2/integrate` outside `tests/acceptance/W2-66/`. You do not touch it or argue it here (the lead reports its scope to
the orchestrator). This ticket's tests must simply hold without a `conftest.py` of their own.

## What you read

- `.tickets/DAEO-ye2a.md` (read-only); DEC-918, DEC-880 and DEC-491 in `docs/DECISION_REGISTER.md`.
- This ticket's acceptance tests, all of `tests/acceptance/W2-72/` (they are this ticket's own tests), and the failing
  case above, `tests/acceptance/W2-66/test_w2_66_lead_verification.py`.
- How other acceptance folders share fixtures without a conftest of their own, if you need an example.

## What you do

- Remove `tests/acceptance/W2-72/conftest.py`: move what it holds (its fixtures, the import path it sets up, its
  helpers) into `tests/acceptance/W2-72/w2_72_support.py` or into the test modules, so that every W2-72 test finds the
  same fixtures and runs exactly as before. A plain `pytest tests` in one process must still collect with no error
  (no module-name clash: the support module keeps its unique name).
- Change no expectation, no case, no parameter and no test name. The test count stays 53. Update the README's "How
  the tests are run" and "Files" sections to say where the fixtures now live, and add a "Revisions" heading with one
  line: the conftest folded into the support module, Rewrite-Reason: DEC-880 (W2-66's KPI 12 case), no expectation
  changed.
- Write only inside `tests/acceptance/W2-72/`. Nothing else.

## Tests to run (foreground, each to its end, never `-x`)

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W2-72 -n 8 -q -p no:cacheprovider -rs
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header

and, after your commit (it reads committed history):

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W2-66/test_w2_66_lead_verification.py -q -p no:cacheprovider -rs

All 53 W2-72 tests pass (the implementation is in place); the collection ends with no error (quote its last line); the
W2-66 case passes. If a W2-72 test fails after the move, the move is wrong: fix the move, never the test. If you need
a correction after your commit, make it a new commit (never amend).

## Commit

Commit only `tests/acceptance/W2-72/`, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "DAEO-ye2a (W2-72): acceptance tests hold without a conftest of their own (W2-66's KPI 12 case)" --trailer "Task: DAEO-ye2a" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-918" --trailer "Rewrite-Reason: DEC-880 (W2-66's KPI 12 case: no conftest.py a plain run reads is added)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short` in your return.

## Return

Your commit's hash (12 digits); the test count before and after; where the fixtures now live; the three runs with
their counts and the collection's last line; confirmation that no expectation changed; the sandbox check's result; the
`gov.__file__` line; whether you used `gov retrieve`; the read refusals you met; your scratch use; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Refused twice for the same call: stop and say so.

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
