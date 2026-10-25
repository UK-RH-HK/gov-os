I've finished the probe of 6aaa404d5c48. The judgement is **fail**. F1 is "yes / loses work": a merge-back done over two Bash calls has git's own merge of its acceptance tests reverted by the live hook. That behaviour predates this change, but DEC-918 item 1 and the ticket's second failure line cover it. Two narrower fail-open shapes (F2, F3) were opened by this change; both are "no" on ordinary work, so they are rows.

task: Fresh, read-only probe of DAEO-ye2a (W2-72) at 6aaa404d5c48, looking for behaviour its acceptance tests miss.
status: DONE — probe complete; judgement fail (F1 is "yes" with "loses work"); findings for the lead to pass to a test designer.
work_completed: **Step 0 (sandbox check):** (a) writing /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ye2a failed ("OSError: [Errno 30] Read-only file system"); (b) `git hash-object -w --stdin` and `git update-index --refresh` both exited 0. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-ye2a. Toplevel /home/usain/gov-os-worktrees/W2-72, branch w2/W2-72, HEAD 6aaa404d5c48. The worktree's untracked entries are the sandbox's placeholder device files (character devices 1,3), not files. After Step 0:
- Read the ticket, card W2-72, row W2-L437, ADR-0001, and DEC-918, 912, 410, 421, 572, 453, 266, 269, 403, 750 and 754.
- Read the change (diff against the merge base 92d5c2736268), the W2-72 README and support module, and the W1-50 revision in 704b3cafbb81.
- Ran the W2-72 and W1-50 suites and the builder tests.
- Ran 21 probes in six batches. They used the suite's own kernel hooks and fixtures, imported from a scratch folder outside the repository, on histories built from scratch.
- Showed the rule before DEC-918 by switching the new allowance off inside the test process (no checkout).
- Replayed the live check on both real merge-backs.
files_changed: none
evidence:
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-72/src/gov/__init__.py`.
- **F1 (two calls).** Call 1 (`git merge --no-ff --no-commit w1/W1-90`, exit 1): "Containment: Acceptance test restored from HEAD: tests/acceptance/W1-90/test_brought_new.py, tests/acceptance/W1-90/test_merged.py." Status after it: only `UU src/gov/guard/decide.py`. Call 2 (resolve, add, commit): "Flagged, left in place: commit d1b370bffc8f … a merge commit's own change to a ticket file or an acceptance test: …test_brought_new.py, …test_merged.py"; `judge_commits` returned the same finding. A second merge of the same side: "Already up to date." Merging the branch on (`--no-ff`) left the side with no test_brought_new.py and the first parent's test_merged.py.
- **F1 controls.** The same history in one call was silent, `judge=[]`. With `--no-commit` and no conflict at all, call 1 still restored test_merged.py and call 2 was flagged.
- **F2.** P13a, P13b and P13c were all silent at the merge commit, with `judge_at_head: []`. With the allowance off: `[(['tests/acceptance/W1-90/test_merged.py'], "a merge commit's own change …")]`. `read_merge` gave own=[test_merged.py], brought=[pyproject.toml, test_renamed.py]. P13c's call 1 reported "Acceptance test restored from HEAD: tests/acceptance/W1-90/test_renamed.py"; call 2 was silent.
- **F3.** Git reported only `tests/acceptance/W1-90/test_merged.py~<commit>` as conflicted. The live check was silent with `judge_at_head: []`, in both directions. With the allowance off: a finding naming test_merged.py.
- **KPI 4.** `judge_commits` returned `[]` for 03f470a595d1 (0.04 s) and 4ef3293adef3 (0.05 s). `read_merge` still lists W1-30's test_w1_30_close.py, and W1-26's README.md and test_w1_26_planted_defects.py, in `own`. Replaying each move: 102 and 285 commits, 8 and 21 merge commits, 5 of the 1,000 git processes used; merge-tree took under 0.01 s on each.
- **Unchanged files.** Against the merge base, `read_merge`'s module is identical apart from docstrings (AST comparison) and `src/gov/decisions/checker.py` is byte-identical. The only src files the change touches are those two guard files (+61 −2).
tests:
- `tests/acceptance/W2-72` (-n 4): 53 passed in 2.79 s.
- `tests/acceptance/W1-50` with `tests/unit/guard/test_w2_72_merge_rule.py` (-n 6): 693 passed, 2 failed in 191.96 s. The two failures are `test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays` and `test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`. Both launch a live Claude session, and my sandbox's proxy refuses api.anthropic.com ("ERR_PROXY_TUNNEL"). Rerun alone: the same 2 fail. They come from my sandbox, not the change.
- My probes are observational and all ran to the end: batch 1 had 8 cases, batch 2 had 5, batch 3 had 2, batch 4 had 2, batch 5 had 3, batch 6 had 1.
discoveries:
- **F1.** A merge-back done over two calls has git's own merge of every acceptance file it brings reverted by the live hook (a conflict resolved in a later call, or `--no-commit` committed in the next call). The commit then drops the other side's tests. The drop survives a later merge of the same side and travels when the branch is merged on. It predates this change.
- **F2 and F3.** Two fail-open shapes opened by this change. In each, a merge commit that drops one side's acceptance-test edit passes both checks:
  - a rename on one side;
  - a file replaced by a directory of the same name on one side.
- `w2/integrate` moved during the session (418514f37f1b → 4439c6c9c08b). The comparisons were redone against the merge base.
risks:
- Fixing F1 touches the working-tree restore that keeps orchestrators off acceptance tests (MR-3). Leaving a file in place during a merge must stay limited to git's own merge of HEAD and the merge being made. Otherwise a hand write made during a merge would escape the restore.
- F2 and F3 come from comparing git's merge only on the merge commit's own paths, not on every acceptance path either side touched.
lessons:
- Every merge in the W2-72 and W1-50 suites is made in one Bash call, so what the hook does between a merge's calls is untested.
- Switching the new allowance off inside the test process shows the rule before DEC-918 without checking out another commit.
- Probes can import the suite's fixtures from a scratch folder (PYTHONDONTWRITEBYTECODE=1, a literal --rootdir) and write nothing in the repository.
proposed_decisions: P-DAEO-ye2a-R1. Classification: 1 yes/loses work (F1), 2 no/fails open (F2, F3), 2 no/other (F4, F5), 1 yes/other (F6). Options:
- (a) W2-72 resumes, test designer first. New cases: two-call merge-backs (a conflict elsewhere; `--no-commit` then commit; a test only the merged side added; a test both sides changed), and the rename and file-replaced-by-directory drops as cases that stay caught. The engineer then works inside containment.py. F4 to F6 become rows.
- (b) F1 gets its own ticket after the re-pin. W2-72 closes, with F2 and F3 riding along or as rows. This keeps DEC-918 item 3's re-pin timing.
- (c) Rows only.

I recommend (a), confidence medium. F1 falls under DEC-918 item 1 ("by the live hook") and the ticket's second failure line, and the fix lies within the ticket's paths; F2 and F3 were opened by this change.
unresolved:
- Removing my two temp folders was refused by the permission mode and not retried. probe72 (68 KB) and pytest-of-usain (14 MB) are left in /tmp/gov-os-lead-W2-72/gov-launch-independent-auditor-vx0m1vez/claude-1000/, outside the repository.
- Where F1 goes is the orchestrator's call: it predates this change and KPI 1's text names merge commits only.
- Two W1-50 live-session cases cannot run in my sandbox (network).
recommended_next_action: The orchestrator judges F1 (yes / loses work) and routes it, with F2 and F3 riding along, either to W2-72's resume (test designer first) or to the owner as a package.

---
type: probe
task: DAEO-ye2a
reviewer_session: dccb1bd5-7b40-44f4-b1a5-8c6334b3e2b7
implementer_session: 26fb5c7b-fc73-4f41-9e03-5dde81702bb4
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 6aaa404d5c48
---

# Probe record: DAEO-ye2a (W2-72), head 6aaa404d5c48

## What was probed

- **Head and change.** Head 6aaa404d5c48 on `w2/W2-72`; merge base with `w2/integrate` 92d5c2736268. Ticket commits: 704b3cafbb81 (acceptance tests; W1-50's two DP-24 cases), aa3d11fc142a (checkpoint), e45aecc6dde6 (the change and its builder tests), c9983293b646 (conftest folded into the support module), 6aaa404d5c48 (checkpoint).
  - `src/gov/guard/containment.py` (+58 −2) adds an allowance. A two-parent merge commit's own acceptance test is taken out of its paths before the commit is judged, in the live check and in `judge_commits`, when all of these hold:
    - both parents changed it against their one merge base;
    - the merge commit holds exactly the entry `git merge-tree --write-tree` writes for it;
    - git reports no conflict on it.
  - The allowance is empty for an octopus merge, for several merge bases or none, for any git failure, for a tree id that cannot be read, and when the git-process budget is spent.
  - `src/gov/guard/containment_merge.py` changed in its docstring only.
- **Method.**
  - The suite's own kernel PreToolUse and PostToolUse/PostToolUseFailure hooks and fixtures, imported from a scratch folder outside the repository.
  - Histories built from scratch.
  - `judge_commits` and `read_merge` taken from this worktree's `src` (DEC-732).
  - Multi-call merges driven call by call between the two hooks.
  - The rule before DEC-918 shown by switching the allowance off inside the test process.
  - Both real merge-backs read and replayed in this repository's objects.
- **Sandbox check.**
  - (a) The write outside the worktree failed (read-only file system).
  - (b) `git hash-object -w` and `git update-index --refresh` worked.
  - Role, ticket, toplevel, branch and head were as expected.
- **Session.** The reviewer session id comes from the environment variable `CLAUDE_CODE_SESSION_ID`; the scratchpad path names the same id.
- **Memory.** `gov retrieve` was used first and returned FACET_UNAVAILABLE (lexical and semantic facets stale, no evidence). Named files were read after that. The code-graph tool is not reachable from this session.
- **Refusals.**
  - Guard read refusals (DEC-849): 0.
  - Harness permission refusals: 3, none of them the same call twice:
    - a pytest argument built from `$TMPDIR`;
    - a compound command containing `rm -f`;
    - the final removal of my temp folders.

## Findings

### F1: a merge-back made over two calls has git's own merge of its acceptance tests restored from HEAD by the live hook (medium-high)

- **Done.** In an orchestrator's own call: `git merge --no-ff --no-commit <side>`. Git stopped on a conflict in a source file that both sides' engineers changed (03f470a5's shape). It had cleanly combined an acceptance test both sides changed (lines 2 and 19) and brought a new acceptance test the merged side added. The next call resolved the source file, staged it and committed with `Task:` and `Role: orchestrator`. The second form had no conflict at all: `--no-commit` in one call, `git commit` in the next.
- **Happened.**
  - After the first call, the hook reported "Acceptance test restored from HEAD" for both tests. It set the combined test back to the first parent's version in the index and the tree, and deleted the new test.
  - The commit then held the first parent's versions. It was flagged ("a merge commit's own change to … an acceptance test") and `judge_commits` refused it.
  - A second merge of the same side answered "Already up to date", so the tests do not come back.
  - Merging the branch on deleted the new test from the other branch and set the combined test back there too.
  - The same history merged in one call is silent and judges clean.
- **Should have happened.** By DEC-918 item 1 and the ticket's second failure line, a merge-back file equal to git's own merge is neither reverted, refused nor flagged by the live hook. The commit holds git's own merge and is silent, as the one-call control is.
- **Not introduced by this change.** The working-tree restore is untouched by the diff. The commit's flag is DEC-403/DEC-410's rule for a merge that drops a parent's change. KPI 1's text names "a merge commit", and every merge in the suite is made in one call.
- Ordinary work: yes, because a merge-back that git stops on a conflict elsewhere (03f470a5 itself) is resolved by an agent over several calls (read, edit, commit). A `--no-commit` merge committed in the next call to add its trailers is the same flow with no conflict. No brief or skill asks for one-call merges, and the orchestrator's integration merges are affected the same way.
- Consequence: loses work. The hook itself throws away git's own merge of every acceptance file the merge brings: the other side's new tests are deleted and tests both sides changed are set back to the first parent's version. Once committed, git records the other side as merged, so no later merge brings the tests back, and merging the branch on carries the drop with it. It is recoverable from history. It does not fail open: each step is reported and `judge_commits` refuses the close.

### F2: with a rename on one side, a merge commit that keeps the renaming side's file whole (dropping the other side's edit) passes; this change opened it (medium)

- **Done.** The first parent renamed the acceptance test (`git mv`, a test designer's commit) and the merged side changed its line 2.
  - (a) Git's own merge was clean, with the edit at the new name. The merge commit held the first parent's renamed file whole.
  - (b) The first parent also changed line 2, so git reported a conflict at the new name. It was resolved with `git checkout --ours`.
  - (c) F1's two-call merge over the same rename. Here the hook's own restore made the drop.
- **Happened.** In all three the live check was silent at the merge commit and `judge_commits` returned nothing; the merged side's edit is gone. With the allowance switched off (the rule before DEC-918), each case is a finding naming the old path.
  - `read_merge` reads the kept file as brought by the renaming parent, so it is never compared with git's merge.
  - The old path, absent from both git's merge and the merge commit, is left out as git's own merge.
- **Should have happened.** The merge commit differs from git's own merge of the test, so it stays the merge commit's own change and is flagged and refused, as before this change (KPI 2, first failure line).
- Ordinary work: no, because it needs an acceptance test renamed on one side while the other side edits it. No acceptance test file has been renamed in this repository's history: none of its 178 renames touch `tests/acceptance/`, and only three acceptance files were ever deleted.
- Consequence: fails open. In (c) it also loses work, and the drop passes the close's containment gate.

### F3: with a file replaced by a same-named directory on one side, the merge that drops the other side's edit passes; this change opened it (low)

- **Done.** The base holds the test. One side deleted it and added a directory of the same name holding one file; the other side changed line 19. Git's merge reported the conflict only under `<path>~<commit id>`, the edited file moved aside. The merge commit kept the directory and deleted the moved-aside copy. Tried in both directions: first the ticket side's edit dropped, then the merged side's.
- **Happened.** The live check was silent and `judge_commits` returned nothing, in both directions. With the allowance switched off, it is a finding naming the path.
- **Should have happened.** A file git reports as conflicted (under its moved-aside name) and resolved by dropping one side stays the merge commit's own change (KPI 2).
- Ordinary work: no, because it needs an acceptance test replaced by a directory of the same name, and none of the 806 acceptance files has a name without an extension that could become one.
- Consequence: fails open.

### F4: with a rename on one side, git's own clean merge is still refused (low)

- **Done.** The first parent changed line 19 and the merged side renamed the test. Git's merge was clean (the edit at the new name, the old path gone), and the merge commit holds it exactly.
- **Happened.** The new path is flagged in the live check ("Flagged, left in place … a merge commit's own change to … an acceptance test: …test_renamed.py") and `judge_commits` returns that finding.
- **Should have happened.** Neither flagged nor refused (DEC-918 item 1). W1-01's DEC-912 rule compares every acceptance file the merge changes with git's merge and would pass it. This predates the change (DEC-269).
- Ordinary work: no, because no acceptance test has ever been renamed here (see F2).
- Consequence: other (fails closed).

### F5: a merge in a non-orchestrator call is flagged, and the report still names the git-merged test as the merge commit's own change (low)

- **Done.** The clean combination, merged in an engineer's own call with engineer trailers.
- **Happened.** The move is flagged as not forward (DEC-266, as it should be). The report adds "A merge commit's own change: tests/acceptance/W1-90/test_merged.py", and the finding's paths name it. `judge_commits` for the same merge commit returns nothing. That report reads `read_merge`'s own paths without the new allowance.
- **Should have happened.** The flag stays, but the git-merged test is not named as a change (DEC-918 item 1).
- Ordinary work: no, because workers do not merge branches; merges are the orchestrator's (DEC-266).
- Consequence: other (wording; the move is flagged anyway).

### F6: DEC-572's ticket-file lift now follows DEC-918 through a merge commit that brought the version, with no test (info)

- **Done.** On the branch, an orchestrator's commit changed a ticket file, and a merge commit there held git's own merge of an acceptance test both its sides changed. Main changed the same ticket file. The outer merge took the branch's ticket file whole.
- **Happened.** At the head there is no finding: the bringing merge commit now passes, so the ticket file is lifted. With the allowance switched off: "a merge commit's own change … ; commit 1e1e1d6a7b28 brought the version of .tickets/DAEO-zz94.md and does not pass".
- **Should have happened.** This agrees with DEC-572's words ("every commit that brought that version passes the check"). KPI 3's suite does not pin it either way.
- Ordinary work: yes, because ticket files changed on both sides of a merge-back are ordinary.
- Consequence: other. Nothing fails open: the bringing commit is git's own merge, and every other bringing commit is still judged.

## Found sound

- **The two real merge-backs (KPI 4).**
  - `judge_commits` returns no finding for 03f470a595d1 (0.04 s) or 4ef3293adef3 (0.05 s).
  - `read_merge` still holds their acceptance tests in `own`.
  - Replaying each move's live check: 102 and 285 commits, 8 and 21 merge commits, 5 of the 1,000 git processes used.
  - `merge-tree` took under 0.01 s on each, far from the 10 s limit.
- **Unchanged code.** Against the merge base, `read_merge`'s module is identical apart from docstrings, and `src/gov/decisions/checker.py` (the approval check) is byte-identical.
- **Merge shapes that behave correctly:**
  - one side changes the mode and the other the content: git's own merge is silent and judged clean;
  - both sides delete the test: silent and judged clean;
  - modify/delete, resolved by keeping the edit: flagged and found;
  - a test turned into a symbolic link on one side and edited on the other: git lists the path itself as conflicted, so it stays caught;
  - names with a space, quote, backslash, tab, newline or non-ASCII letters: git's own merge is left out, and a hand edit is caught in both checks;
  - a hand-made merge commit naming a parent twice: read as a two-parent merge holding git's own merge, with no finding; not fail-open.
- **Fail-closed paths, by reading (the suite shows them):** a git failure or timeout, a tree id that cannot be read, a spent process budget, an octopus merge, several merge bases or none.
- **Ticket files.** The allowance takes only paths under `tests/acceptance/`; KPI 3's ticket-file case stays flagged.
- **W1-50's revision.** Only the two named cases changed (`…_is_flagged` → `…_is_silent`, Rewrite-Reason: DEC-918, docstrings stating before and after), plus docstrings. The new assertion is stricter than the one it replaces; no other expectation is lowered.

## Outside this change (not findings of this ticket)

- An acceptance path that is not valid UTF-8 makes `judge_commits` raise `UnicodeDecodeError` while reading the commit, before any code of this change runs. The close's gate catches only its own findings, so the close stops with an error (fails closed).
- A test designer's commit to an acceptance file whose name holds a tab, a newline and a backspace is flagged "outside allowed paths" by the live check.
- Replaying the two merge-backs also flags owner commits the moves bring ("a Role: owner commit made during an agent's call").

## Tests run

- `tests/acceptance/W2-72`: 53 passed.
- `tests/acceptance/W1-50` with the builder tests: 693 passed, 2 failed. The two failing freeze cases launch a live session, which the reviewer's sandbox refuses network access for; rerun alone, they fail the same way. They come from the sandbox, not the change.
- Reviewer probes: 21 cases in six batches, all run to the end.

## Classification (DEC-809)

F1 yes / loses work; F2 no / fails open; F3 no / fails open; F4 no / other; F5 no / other; F6 yes / other.

## Judgement

**fail.** F1 is "yes" with "loses work". F1 predates this change and lies outside KPI 1's literal text (merge commits), but inside DEC-918 item 1 ("by the live hook") and the ticket's second failure line. Where it goes is the orchestrator's call: W2-72's resume (DEC-802) or a package. F2 and F3 are rows by rule, but this change opened them, and they can ride in the same resume. F4 to F6 are rows.