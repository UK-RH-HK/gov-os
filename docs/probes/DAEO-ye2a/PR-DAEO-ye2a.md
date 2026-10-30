---
type: probe
task: DAEO-ye2a
reviewer_session: 6063c0b9-5587-472b-8239-3f3f8c43897b
implementer_session: d7a86271-6458-43b0-b622-07ace0803e61
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e9c7b23a21c136e2153b50f603b9d52797a1551e
---

# Probe record: DAEO-ye2a (W2-72), containment's merge rule matches DEC-912: review 2 of 2 (DEC-413)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137).
  The reviewer was a fresh `independent-auditor` session (`6063c0b9-5587-472b-8239-3f3f8c43897b`, 2026-10-25),
  started through `gov launch` under its OS sandbox with the reading tools alone, at effort max. It wrote nothing: the
  lead's tripwire before and after its session shows no change in this worktree.
- **Implementers.** The engineer sessions were `26fb5c7b-fc73-4f41-9e03-5dde81702bb4` (commit `e45aecc6dde6`) and
  `d7a86271-6458-43b0-b622-07ace0803e61` (commit `3e3d71244398`, the fixes for review 1's F1 to F4).
- **The earlier review.** Review 1 (session `dccb1bd5-7b40-44f4-b1a5-8c6334b3e2b7`, head `6aaa404d5c48`) failed on F1
  (a merge-back over two calls had git's own merge of its acceptance tests restored by the live hook; yes / loses
  work) and found F2 and F3 (no / fails open), F4 (no / other), F5 (no / other), F6 (yes / other). Its record stays a
  draft. F1 to F4 were fixed in one round (test designer `7a1aca6a1edc`, engineer `3e3d71244398`); F5 and F6 are rows.
- **The lead's verification** at `3e3d71244398` (the probed head adds only a checkpoint record), after a full rebuild:
  collection 16,514 of 16,516 (2 deselected), no error; `gov check` exit 0; the full parallel run in the close's form
  16,215 passed, 31 skipped, 3 failed, the three being W1-03's `test_w1_03_head_move_and_acceptance_test.py` cases that
  fail at the fixture's own precondition (an amend in the same second does not move HEAD) before the check runs, as
  the same file does on `w2/integrate`'s code; the serial-only cases 265 passed.
- **Verdict: pass.** Classification (DEC-809): 0 findings "yes" with "fails open" or "loses work"; F7 yes / other
  (row); F8 no / loses work, failing closed (row for the Wave 3 hardening pass). The lead's judgement agrees.

## What was probed

- **Head and change.**
  - Head `e9c7b23a21c1` on `w2/W2-72`; its merge base with `w2/integrate` is `92d5c2736268`.
  - Since review 1 (`6aaa404d5c48`): `7a1aca6a1edc` (test designer) added 20 acceptance tests for F1 to F4, and
    `3e3d71244398` (engineer) changed `src/gov/guard/containment.py` only (+190 −37) and added builder tests.
    `e9c7b23a21c1` is a checkpoint record.
  - **The rule for one merge commit.** A two-parent merge commit with one merge base has its own acceptance tests left
    out when two things hold:
    - it holds each of them exactly as git's own merge of its parents (`git merge-tree --write-tree`) writes it;
    - every acceptance path where it differs from git's merge, or that git reports as conflicted, is one of its own
      paths.
    Otherwise nothing is left out.
  - **The live check, in an orchestrator's own call,** now leaves alone (neither restores nor flags) an acceptance test
    in two cases:
    - a merge in progress holds it exactly as git's own merge of HEAD and MERGE_HEAD writes it, both in the index and
      in the working tree;
    - in the call that commits that merge: the test was dirty before the call, is clean after it, and was moved by a
      merge commit of the call that is no finding and equals git's merge on the whole folder.
- **Method.**
  - The suite's own fixtures and kernel PreToolUse and PostToolUse/PostToolUseFailure hooks, imported from a scratch
    folder outside the repository.
  - Histories built from scratch under pytest's temp folder; multi-call merges driven call by call, including in a
    linked worktree of a throw-away repository.
  - `judge_commits` and `read_merge` taken from this worktree's `src` (DEC-732).
  - The rule before DEC-918 shown by switching the allowance off inside the probe process.
  - `judge_commits` run over all 361 merge commits of this repository with the allowance on and off, each difference
    checked against `git merge-tree` computed separately.
  - The two real merge-backs' moves replayed through the live judgement in this repository's objects. No tree was
    copied.
- **Sandbox check.** (a) The write outside the worktree failed (read-only file system). (b) `git hash-object -w` and
  `git update-index --refresh` worked. Role, ticket, toplevel, branch and head were as expected.
- **Session.** The reviewer's id comes from the environment variable `CLAUDE_CODE_SESSION_ID`; the scratchpad path
  names the same id.
- **Memory.** `gov retrieve` was used first and returned FACET_UNAVAILABLE (lexical and semantic facets stale). Named
  files were read after that. The code-graph tool is not reachable from the session.
- **Refusals.** Guard read refusals (DEC-849): 0. Guard write refusals: 1 (a `sed -i` on the reviewer's own scratch
  script through a shell variable; nothing in the repository). Harness permission refusals: 2, both the same removal
  of the reviewer's pytest temp folder; it stopped there (AR-6).

## Findings

### F7: the live check flags git's own merge of acceptance tests when a merge in progress does not end as a merge commit with no finding (low)

- **Done.** In an orchestrator's own calls: `git merge --no-ff --no-commit <side>`, either clean or stopping on a
  conflict in a source file both sides' engineers changed. Then, in the next call, one of these:
  - (a) `git merge --abort`, or `git reset --hard`;
  - (b) the commit of the merge, where the merge commit is a finding for another path: a ticket file both sides
    changed that git combined (DEC-421), or another acceptance test changed by hand before the commit.
- **Happened.**
  - (a) The abort's check records a `flagged` finding, "acceptance test was already dirty, not restored", and tells the
    agent "Containment: Outside allowed paths, left in place:", followed by every acceptance test git's merge had
    written. The abort had already put HEAD's versions back, nothing was written by hand, and `git status` is clean.
  - (b) Besides the merge commit's own finding, the commit's check also flags as "Outside allowed paths, left in place"
    each acceptance test that the merge commit holds exactly as git's own merge writes it. Made in one call, the same
    merge names only the ticket file (run) or the hand-edited test (by reading), and `judge_commits` names only those.
- **Should have happened.** (a) Nothing reported for files that only git's merge wrote and the abort took back. (b)
  Only the merge commit's finding, as in one call (DEC-918 item 1).
- **Not a regression.** Before this change, the first call itself restored those tests from HEAD (F1). This is what
  remains: the second call's allowance applies only when a merge commit with no finding lands.
- Ordinary work: yes, because a lead aborts a merge-back that stopped on a conflict (to ask, or to redo it), or
  commits a merge-back whose ticket file both sides changed, over separate calls in ordinary work.
- Consequence: other. It is a spurious, mislabelled flag in the live record and in what the agent is told. Nothing is
  restored or lost, nothing passes, and the close's gate is unaffected.

### F8: in a merge made over two calls, git's own merge of an acceptance entry is still restored from HEAD when the entry is not a regular file or git's merge cannot be shown (row)

- **Done.** Two-call merges (`git merge --no-ff --no-commit`, then `git commit` with orchestrator trailers) of:
  - (i) a side that adds a symbolic link under `tests/acceptance/` while main edits another test;
  - (ii) the suite's criss-cross history (two merge bases), with git's clean combination of one test.
- **Happened.**
  - The first call's check restores git's merge of the entry from HEAD ("Acceptance test restored from HEAD", recorded
    `reverted`). In (i) the new link is deleted; in (ii) the combined test is set back to the first parent's version.
  - The commit then drops the entry and is flagged as the merge commit's own change; in (i) `judge_commits` refuses it.
  - In one call, (i) is silent and judged clean, and (ii) is flagged and kept.
- **Should have happened.** (i) Kept, as in one call. (ii) Caught (KPI 2), but without the merge's work being taken
  out of the tree.
- Ordinary work: no, because no symbolic link has ever been added under `tests/acceptance/` in this repository, and
  none of its 361 merge commits has several merge bases, none, or more than two parents.
- Consequence: loses work, recoverable from history. It fails closed: flagged at the commit and refused at the close.

## Found sound

- **F1's fix (merge in progress, then the commit call).** Every one of these was silent and moved nothing; the tree
  and index equal the merge commit, and `judge_commits` returns nothing:
  - a conflict on a source file resolved in call 2;
  - no conflict, with the commit in call 2;
  - three calls (merge, resolve, commit);
  - abort, merge again, then commit;
  - `git status`, `git diff --cached`, `git add -A` and a `touch` of a merged test between the merge and its commit;
  - a merge that deletes an acceptance test;
  - a merge that brings an executable test and a mode change;
  - a test whose name holds a tab, a newline, a colon, a space and a non-ASCII letter;
  - the conflict case over two calls and the clean case in one call, both in a linked worktree (MERGE_HEAD under
    `<common>/worktrees/<name>/`).
- **Still caught.**
  - A hand-edited acceptance test committed with the merge is a finding for the merge commit, in the live check and in
    `judge_commits`.
  - Two tests renamed to one name on the two sides, with the merge keeping one side: caught, both with the allowance
    and without it.
  - With 0 to 2 git processes left, the merge stays a finding; with 3 it is allowed.
  - Read in the code: every new function catches git failures, timeouts, decoding errors, unreadable output and system
    errors and then gives no allowance, so no new exception escapes the hook.
- **History differential.** Of 361 merges, 9 change result; every path left out equals git's merge entry and is not
  conflicted; no acceptance path that differs from git's merge passes; 0 new findings; the 4 merges still found at the
  head were found before too.
- **The two real merge-backs (KPI 4).** `judge_commits` returns nothing for `03f470a595d1` or `4ef3293adef3` (one
  finding each without the allowance); `read_merge` still holds their acceptance tests in `own`; in the replayed moves
  the merge commit itself has no finding.
- **Unchanged.** The approval check is byte-identical to `w2/integrate`'s; `read_merge` changed in its docstring only;
  ticket files: git's combination of a ticket file both sides changed stays a finding, in one call and in two calls
  (DEC-421); W1-50's DEC-572 cases pass.
- **Roles.** The engineer's commits stay inside `allowed_paths`, and no acceptance test was changed by the engineer.

## Outside this change (not findings of this ticket)

- The replayed moves still flag brought owner commits ("a Role: owner commit made during an agent's call"), as review 1
  noted.
- A test designer's commit to an acceptance file whose name holds a tab and a newline is flagged "outside allowed
  paths" by the live check (review 1 noted it). The merge commit itself judges clean.
- In a sandboxed session, `git status` lists the sandbox's placeholder device files as untracked.
- Review 1's rows F5 (no / other) and F6 (yes / other) are unchanged at this head.

## Tests run

- `tests/acceptance/W2-72` with the builder tests: 88 passed.
- W1-50 + W1-03 + W1-01: 1,111 passed, 28 skipped, 4 failed: two W1-50 freeze cases launch a live session, which the
  sandbox's network block refuses; two W1-03 head-move cases fail in the fixture's setup (an amend in the same second
  does not move HEAD) before the check runs.
- `tests/unit/guard` + W1-45 + W1-47: 2,156 passed.
- `tests/unit/containment` + close gates + every-finding + decisions: 214 passed.
- Reviewer probes: 18 cases in two scripts, all run to the end; plus the 361-merge differential and the two replays.

## Classification (DEC-809)

F7 yes / other; F8 no / loses work (fails closed).

## Judgement

**pass.** No finding is "yes" with "fails open" or "loses work". F7 is a row that can ride along in any later resume
touching the containment hook (DEC-802). F8 is a row for the Wave 3 hardening pass.
