You are a fresh independent test designer (MR-3). Ticket: DAEO-ye2a (W2-72), profile FULL. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-72` on branch `w2/W2-72`. You are a fresh session of the test designer's
role, asked for one test-design batch after the ticket's first review: the review found behaviours the acceptance
tests miss, and you write the tests for them before the engineer changes anything. Your time budget is about 90
minutes.

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
  that is the files `git diff --name-only w2/integrate...HEAD` names other than the acceptance tests and the
  checkpoint records: `src/gov/guard/containment.py`, `src/gov/guard/containment_merge.py`,
  `tests/unit/guard/test_w2_72_merge_rule.py`, and the engineer's commit `e45aecc6dde6` (no Read, cat, grep, diff,
  `git show` or `git log -p` of them, and no import of them to inspect their source). You may import and call the
  public interfaces your tests already use (`judge_commits`, `read_merge`, the kernel hooks), as before; (d) the
  hidden half of any evaluation set, by whoever is measured by it.
- **Protected material:** never read, print, search, diff or copy the held-out file under `governance/project/`, and
  never type its path (DEC-525). Never read or name the qualification oracle. Never write in `~/gov-os-workbench`,
  and never list or search it.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a
  folder of it. Tests that need a repository build a temporary one from scratch. Nothing is ever put under a
  `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or
  not a flag exists: conclude nothing from it.
- The guard refuses here-documents, inline scripts it cannot read, and unresolvable variables in Bash write targets:
  write files with the Write and Edit tools and literal absolute paths; put a probe in a script file. No subagents
  that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`.
- **Temp folder:** do not set `TMPDIR` yourself; keep the one your launched session already has. Keep pytest's own
  temp retention (never `--basetemp`).
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the
  tracked tree. **Your share is 5 GB and 250,000 files and folders.** Remove what you make by hand when done; never
  run the whole project's suite (the collection below is not a run). If you would pass your share, stop and say so.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never
  write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
  The test files write no full commit id of this repository.
- **Memory used (DEC-836, DEC-860, DEC-859):** for what you need to know, use `gov retrieve` first
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m gov.cli.main retrieve "<question>" --json`) before
  reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`,
  then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own
  traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in
  your return whether you used `gov retrieve`.
- Never ask the owner anything and never notify anyone; a question is a package in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- The git hooks are uninstalled: before your commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks`
  holds no `pre-commit` file (only `*.sample`); if one is there, stop and say so. Never `--no-verify`, never
  `core.hooksPath`.

## What you read

- `.tickets/DAEO-ye2a.md` (read-only): its KPI lines, above all KPI 1, KPI 2 and the two failure lines "A file that
  differs from git's own merge passes, in the live check or at the close" and "A merge-back file equal to git's own
  merge is restored, refused or flagged".
- DEC-918 (item 1: "neither reverted, refused nor counted as a change, by the live hook or by the close's gate"),
  DEC-912, DEC-410, DEC-266, DEC-143 (the restore after a call), DEC-750 and DEC-754, DEC-491 in
  `docs/DECISION_REGISTER.md`.
- This ticket's acceptance tests, all of `tests/acceptance/W2-72/` (README, support module, cases); W1-50's support
  (`tests/acceptance/W1-50/w1_50_support.py`, `w1_50_own_change_support.py`) and W1-03's
  (`tests/acceptance/W1-03/w1_03_support.py`), which drive the kernel's PreToolUse and PostToolUse hooks around one
  Bash call.

## The behaviours to test (found by the review, described; DEC-136)

Every merge in the suite today is made in one Bash call. The review drove merges over **two Bash calls**, each between
the kernel's PreToolUse and PostToolUse hooks, in an orchestrator session's own call (as the suite's merges are made:
`GOV_ROLE=orchestrator`, a ticket, the merge commit carrying `Task:` and `Role: orchestrator`).

1. **A merge-back over two calls keeps git's own merge (F1; KPI 1, DEC-918 item 1; ordinary work, loses work today).**
   - (a) Call 1: `git merge --no-ff --no-commit <side>` stops on a conflict in a source file both sides' engineers
     changed (as in the real merge-back `03f470a5`), while git cleanly combines an acceptance test both sides changed
     and brings a new acceptance test only the merged side added. Call 2: the source file is resolved, staged, and
     the merge committed with the trailers.
   - (b) The same with no conflict at all: call 1 `git merge --no-ff --no-commit <side>`, call 2 `git commit` with
     the trailers.
   - Today, after call 1, the live hook reports "Acceptance test restored from HEAD" for both tests: it sets the
     combined test back to the first parent's version and deletes the new one; the commit then holds the first
     parent's versions, is flagged, and `judge_commits` refuses it; the drop is permanent (a second merge of the same
     side answers "Already up to date").
   - Expected: neither call restores, flags or reports either test; after call 2 the merge commit holds git's own
     merge of both tests (the combined test as `git merge-tree --write-tree` writes it, the new test present), the
     working tree and index equal it, and `judge_commits` returns no finding for the merge commit. Show both calls'
     agent-facing text and the finding records.
   - **Still caught (KPI 2):** in the same two-call flow, a hand write to an acceptance test between call 1 and the
     commit, or in call 1 itself after the merge (content that differs from git's own merge of HEAD and the merge
     being made), is restored or flagged exactly as an acceptance-test write is today, and the committed merge, if it
     holds the hand write, is a finding of the live check and of `judge_commits`. A conflict in an acceptance test
     itself (git reports the test as conflicted) stays caught as today, whatever is staged for it. The same two-call
     flow in a non-orchestrator session's call keeps today's behaviour (DEC-266).
2. **A drop hidden behind a rename stays caught (F2; KPI 2; opened by this change).** The first parent renamed an
   acceptance test (`git mv`, a test designer's commit) and the merged side changed one of its lines. (a) Git's own
   merge is clean, with the edit at the new name; the merge commit instead holds the first parent's renamed file whole
   (the other side's edit dropped). (b) The first parent also changed the same line, so git reports a conflict at the
   new name; it is resolved by taking the first parent's version. Today both pass the live check and `judge_commits`
   silently. Expected: each stays the merge commit's own change, flagged and a `judge_commits` finding (naming at least
   one acceptance path of the test).
3. **A drop hidden behind a file replaced by a directory stays caught (F3; KPI 2; opened by this change).** The base
   holds an acceptance test; one side deletes it and adds a directory of the same name holding one file; the other
   side changes one of its lines. Git reports the conflict only under the moved-aside name (`<path>~<commit>`). The
   merge commit keeps the directory and drops the moved-aside edited copy. Try it in both directions (each side's edit
   dropped). Today both pass silently. Expected: flagged and a `judge_commits` finding.
4. **Git's own clean merge across a rename passes (F4; DEC-918 item 1, DEC-912).** The first parent changed one line of
   an acceptance test; the merged side renamed it (`git mv`). Git's own merge is clean (the edit at the new name, the
   old path gone) and the merge commit holds it exactly. Today the new path is flagged ("a merge commit's own change
   ... an acceptance test") and `judge_commits` returns that finding. Expected: silent, and no finding, in one call (and
   the two-call form of item 1 (b) for the same history).

Keep every existing case and expectation of the suite. Before you write the new cases, check by reasoning and by
running them which existing cases of earlier tickets assert the opposite of item 1 (a working-tree restore of an
acceptance file that a merge in progress holds exactly as git's own merge): if a W1-50 case does so for that reason
alone, revise it with `Rewrite-Reason: DEC-918` as the ticket body allows; if a case in any other folder does, do not
touch it: name it in your return as a package.

## What you write

- New cases in `tests/acceptance/W2-72/` (new test modules, helpers in `w2_72_support.py`; no `conftest.py`: W2-66's
  KPI 12 case refuses one). Update the README: map each new case to the KPI line and the review finding it covers
  (F1 to F4), give each one's expected red reason now, and add to "Revisions" a line for this batch (tests added after
  implementation, from the ticket's first review, Rewrite-Reason: DEC-918).
- FULL, so thorough on the four behaviours above, with no combinatorial expansion beyond them.
- Behaviour through the public interfaces (the hooks around each call, `judge_commits`, `read_merge`), never internals.
- **Red first:** run the new cases to their end: items 1, 2, 3 and 4's main cases fail now for the reasons stated
  above; the "still caught" cases of item 1 pass now and must keep passing. Then the whole W2-72 folder and W1-50
  folder, and W1-03, to their ends, to show nothing else turned red because of your edits.

## Tests to run (foreground, each to its end, never `-x`)

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W2-72 -n 8 -q -p no:cacheprovider -rs
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W1-50 tests/acceptance/W1-03 -n 8 -q -p no:cacheprovider -rs
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header

Two W1-50 freeze cases (`test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays`
and `test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`) launch a real
session and fail inside a sandbox for want of network; they are not yours.

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "DAEO-ye2a (W2-72): acceptance tests for two-call merge-backs, renames and a file replaced by a directory (review 1, DEC-918)" --trailer "Task: DAEO-ye2a" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-918" --trailer "Rewrite-Reason: DEC-918 (tests added after implementation from the ticket's first review: F1 to F4)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short` in your return.

## Return

Your commit's hash (12 digits); the new test count and the total; each behaviour (1 to 4) with its tests; the red
reason as you saw it, with the counts; every earlier test you revised, with its reason, and any you name as a package;
the collection's last line; the sandbox check's result; the `gov.__file__` line; whether you used `gov retrieve`; the
read refusals you met; your scratch use; any package.

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
