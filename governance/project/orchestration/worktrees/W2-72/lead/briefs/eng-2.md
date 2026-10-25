You are a fresh engineer. Ticket: DAEO-ye2a (W2-72), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-72` on branch `w2/W2-72`. An earlier engineer implemented the ticket (commit
`e45aecc6dde6`); its review found behaviours to fix, and a test designer has since written acceptance tests for them.
You make those tests pass. Your time budget is about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ye2a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ye2a`) and
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
  started in the background is ever read. Commit your work before you run any long suite. Return only after your
  commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one
  (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads that Policy 2 opened (searches
  that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look
  for another spelling, search named folders instead, and count the refusals you met in your return.
- **Policy 2 (DEC-820):** you read freely: the whole repository, git history, other worktrees. Only four things are
  refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file
  names may be seen); (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-72/`**, by any
  tool (no Read, cat, ls, grep, diff, `git show` or `git log -p` of it), nor the lines this ticket's test designer
  changed in `tests/acceptance/W1-50/` or elsewhere (its commits `704b3cafbb81`, `c9983293b646` and `7a1aca6a1edc`);
  you may run those tests and see their names, results and failure messages; (d) the hidden half of any evaluation
  set, by whoever is measured by it.
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
  run the whole project's suite. If you would pass your share, stop and say so.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never
  write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Memory used (DEC-836, DEC-860, DEC-859):** for what you need to know, use `gov retrieve` first
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m gov.cli.main retrieve "<question>" --json`) before
  reading files at random; this worktree has a store. Never one giant query or context: a large question is taken in
  batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the
  code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of
  the whole graph. Say in your return whether you used `gov retrieve`, and if not, why.
- Never ask the owner anything and never notify anyone; a question is a package in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses
  something you needed, do not work around it: return it as a package.
- The git hooks are uninstalled: before your commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks`
  holds no `pre-commit` file (only `*.sample`); if one is there, stop and say so. Never `--no-verify`, never
  `core.hooksPath`.

## What you read

- `.tickets/DAEO-ye2a.md` (read-only): KPI lines and `allowed_paths`.
- DEC-918, DEC-912, DEC-410, DEC-421, DEC-572, DEC-453, DEC-266, DEC-143, DEC-124, DEC-750, DEC-754, DEC-135 in
  `docs/DECISION_REGISTER.md`.
- The code: `src/gov/guard/containment.py` (as it stands at HEAD, with the first engineer's `_git_merged` and its call
  at the top of `_judge_commit`; `check_containment`, the live post-command check, with its working-tree restore of
  acceptance tests; `judge_commits`), `src/gov/guard/containment_merge.py`, the first engineer's builder tests
  `tests/unit/guard/test_w2_72_merge_rule.py`, and the kernel hooks under `template/governance/kernel/hooks/` that call
  the check.

## What the review found (described; DEC-136) and what to build

The first review probed the head `6aaa404d5c48` and found:

1. **F1 (ordinary work: yes; loses work).** A merge-back made over **two Bash calls** in an orchestrator session's own
   call loses git's own merge. Call 1: `git merge --no-ff --no-commit <side>` (it stops on a conflict in a source
   file, as the real merge-back `03f470a5` did, or simply does not commit). After call 1 the live hook reports
   "Acceptance test restored from HEAD" for every acceptance file the merge brought: a test both sides changed is set
   back to the first parent's version and a test only the merged side added is deleted. Call 2 commits the merge,
   which then holds the first parent's versions and is flagged; `judge_commits` refuses it; git records the side as
   merged, so the drop is permanent. The same history merged in one call is silent and judges clean. DEC-918 item 1:
   such a file is "neither reverted, refused nor counted as a change, by the live hook or by the close's gate".
   - **Build:** while a merge is in progress (the repository has a `MERGE_HEAD`, with one other commit) in an
     orchestrator session's own call, a changed acceptance path whose index entry and working-tree content equal the
     entry git's own merge of `HEAD` and `MERGE_HEAD` writes for it (`git merge-tree --write-tree`, with no conflict on
     it, the two commits having one merge base) is neither restored nor flagged nor reported. In the call that then
     commits the merge, the paths that were dirty before and are clean now because the allowed merge commit holds them
     are no breach either ("already dirty, not restored" must not be reported for them). Everything else stays as it
     is: a hand write to an acceptance test during a merge (content that differs from git's own merge) is restored or
     flagged exactly as today; a conflicted acceptance file stays caught; a non-orchestrator call keeps today's
     behaviour (DEC-266); any failure to compute git's own merge gives no allowance (fail closed). One merge-tree run
     per call at most.
2. **F2 (no; fails open; opened by the first change).** With a rename on one side: the first parent renames an
   acceptance test and the merged side edits it. If the merge commit holds the renaming parent's file whole (the
   other side's edit dropped), whether git's own merge was clean or conflicted at the new name, both checks pass
   silently. The kept file is read by `read_merge` as brought by the renaming parent, so it is never compared with git's
   merge; the old path, absent from both git's merge and the merge commit, is then left out as git's own merge.
3. **F3 (no; fails open; opened by the first change).** One side replaces an acceptance test by a directory of the same
   name; the other side edits the test. Git reports the conflict only under the moved-aside name (`<path>~<commit>`).
   A merge commit that keeps the directory and drops the moved-aside edited copy passes silently, in both directions.
4. **F4 (no; other; ride-along).** The first parent edits an acceptance test and the merged side renames it; git's own
   merge is clean and the merge commit holds it exactly. The new path is still flagged and refused, because the
   allowance is limited to paths both parents changed by name. DEC-912's rule (W1-01) passes it.

- **Build for F2 to F4, the lead's design decision:** compare the merge commit with git's own merge of its two parents
  over the whole of `tests/acceptance/`, not only on the merge commit's own paths. Let D be the acceptance paths where
  the merge commit's tree differs from git's merged tree (content, mode or presence), together with every acceptance
  path git reports as conflicted (a moved-aside name included). If D holds any path that `read_merge` does not count
  as the merge commit's own, give the merge no allowance at all (it is judged as before DEC-918). Otherwise every own
  acceptance path not in D is not the merge commit's own change (this replaces the "both parents changed it"
  precondition, which is what makes F4 pass). The fail-closed rules stay: octopus, several merge bases or none, a
  merge-tree that fails or cannot be read, a spent budget give no allowance. Ticket files and every other path keep
  their rules; `read_merge`'s answers and the approval check stay unchanged.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/guard/containment.py`, `src/gov/guard/containment_merge.py`, and
  builder tests `tests/unit/guard/test_w2_72_*.py` (the existing `test_w2_72_merge_rule.py` may be extended, or a new
  `test_w2_72_*.py` added). Nothing else in `tests/unit/guard/` (W2-67, in flight, holds it), never
  `tests/acceptance/**`, never `.tickets/`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked
  around.
- Proportion (DEC-135): code for the four findings above and nothing more. Never make a guard or gate decision fail
  open: every failure KPI must still refuse. Update the docstrings you change.

## Tests to run (foreground, each to its end, never `-x`), after your commit

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W2-72 tests/acceptance/W1-50 tests/acceptance/W1-03 tests/acceptance/W1-45 tests/acceptance/W1-47 tests/acceptance/W1-05 tests/acceptance/W1-02 tests/acceptance/W1-01/test_w1_01_integration_merges.py tests/unit/containment tests/unit/guard/test_w2_72_*.py -n 8 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed

All of `tests/acceptance/W2-72` must pass, and nothing that passed before may fail. Two W1-50 freeze cases
(`test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays` and
`test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`) launch a real
session and fail inside a sandbox for want of network; latency cases of W1-02 and W1-05 may fail under parallel load
inside your sandbox: re-run those alone and report both results. A fix after a run is a new commit (never amend).

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-ye2a" --trailer "Role: engineer" --trailer "Implements: DEC-918" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -3` and `git status --short` in your return.

## Return

Your commits' hashes (12 digits); the files changed; the design in a few lines (F1's place and conditions, D and the
whole-merge condition, how each fail-closed case is met, the process counts against the budgets, whether `read_merge`
changed); the tests you ran with their counts; the lines added and removed in `src/gov/guard/` (cumulative against
`w2/integrate` too); the sandbox check's result; the `gov.__file__` line; whether you used `gov retrieve`; the read
refusals you met; your scratch use; anything you were refused or could not settle, as a package (question, why now,
options, impact, reversibility, cost, recommendation, confidence).

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
