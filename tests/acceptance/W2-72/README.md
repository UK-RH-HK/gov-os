# W2-72 acceptance tests: containment's merge rule matches DEC-912

Ticket `DAEO-ye2a` (W2-72, FULL), from DEC-918 (P-W2-L437-B (a1)). Written by the independent test designer
(MR-3) from the ticket's KPI lines and its sources (DEC-918, DEC-912, DEC-410, DEC-421, DEC-572, DEC-453,
DEC-266), before the implementation. No part of an implementation was read to learn what a test should expect;
the tests work through the public interfaces only.

**The rule (DEC-918 item 1, (a1)).** Under `tests/acceptance/`, a path both parents of a merge commit changed
against their merge base is not the merge commit's own change when the merge holds exactly git's own merge of that
file: the blob `git merge-tree --write-tree <first parent> <other parent>` writes for it, with no conflict on that
file. Then the live post-command check neither restores, refuses nor flags it, and `judge_commits` returns no
finding for it. Any file that differs from git's own merge is caught as before. Not (a2): the commits that brought
the edits are not made a condition (item 2).

## How the tests are run

Every run uses this worktree's own `src/` (DEC-732), with `PYTHONPATH` set on the command itself:

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-72/src python3 -m pytest tests/acceptance/W2-72 -q -p no:cacheprovider -rs
```

- The live check runs as the harness runs it: the kernel's PreToolUse and PostToolUse hooks from
  `template/governance/kernel/hooks/`, copied into a throw-away project, with this repository's `src/` on the
  hooks' `PYTHONPATH` (`tests/acceptance/W1-03/w1_03_support.py`, which W1-50's suite uses too).
- The folder has no `conftest.py` of its own (DEC-880, W2-66's KPI 12 case). The fixtures (`hook`, `guard_hook`,
  `sandbox`, `project`, `call`, `judge`, `read_merge`) are defined at the end of `w2_72_support.py`. Each test
  module puts its own folder first on `sys.path`, then imports `w2_72_support` and the fixtures it uses by name,
  as W1-50's freeze cases import theirs.
- `judge_commits` and `read_merge` are imported in the test process from this repository's `src/`
  (`monkeypatch.syspath_prepend`). Each fixture asserts that the module came from there. The fail-closed
  `judge_commits` case runs `judge_commits` in a new Python process with `PYTHONPATH` set to that `src/` and
  asserts the module's file is under it.
- `GOV_ROLE`, `GOV_TICKET` and `CLAUDE_PROJECT_DIR` are removed from the judging process. The hooks' environment
  is built from scratch.
- Repositories are made from scratch (`git init` in pytest's `tmp_path`). Nothing is copied from this repository,
  and there is no network. The four cases of KPI 4 read this repository's own objects, read-only.
- The suite takes about 15 seconds with `-n 8` and about a minute without it (60 seconds measured, before the
  implementation). Nothing in it depends on timing or on a live session.

## Files

| File | What it holds |
|---|---|
| `w2_72_support.py` | The histories (one builder per merge), the guards from git's own answers (`assert_shape`, `git_s_own_merge`), the failing `git` of the fail-closed cases, `judge_in_a_process`, and the fixtures: the hooks, the throw-away project, `call` (one Bash call between the two hooks; `check_environment` replaces variables of the PostToolUse hook's environment only), `judge` and `read_merge` |
| `test_w2_72_clean_merge_of_an_acceptance_file.py` | KPI 1 |
| `test_w2_72_file_that_differs_from_git_s_merge.py` | KPI 2, every shape except merge-tree that cannot run |
| `test_w2_72_merge_tree_that_cannot_run.py` | KPI 2, fail closed |
| `test_w2_72_nothing_else_changes.py` | KPI 3 |
| `test_w2_72_the_two_merge_backs.py` | KPI 4 |
| `test_w2_72_merge_over_two_calls.py` | review 1, F1: KPI 1 and KPI 2 over two Bash calls |
| `test_w2_72_drop_behind_a_rename_or_a_directory.py` | review 1, F2 and F3: KPI 2 |
| `test_w2_72_clean_merge_across_a_rename.py` | review 1, F4: KPI 1 |

KPI 5 is the revision of W1-50's cases (below). The last three files are review 1's batch, written after the
implementation (section "Review 1's batch").

**The merges.** Each is made as a ticket lead merges `w2/integrate` back:

- a forward move of the checked-out branch (`main` in the fixture project, the first parent) to a merge commit of
  the merged side (`w1/W1-90`, the second parent);
- made in an orchestrator session's own call (`GOV_ROLE=orchestrator`, `GOV_TICKET=DAEO-zz90`; DEC-266);
- the merge commit carries `Task: DAEO-zz90` and `Role: orchestrator` in its final trailer block.

The commits on the two sides are a test designer's (acceptance tests) or an engineer's (`pyproject.toml`, the
source file) inside their own trailers' paths, unless a case says otherwise.

Every history is checked by `assert_shape` from git's own answers before anything is expected of it:

- the number of parents and of merge bases;
- that both parents changed the path against their one merge base;
- which paths `git merge-tree --write-tree --name-only` reports as conflicted;
- whether the merge commit holds exactly the entry (mode and blob) of git's own merge for the path.

## KPI lines and their tests

The first batch: 53 tests, of which 14 were red before the implementation and 39 passed. Review 1's batch adds
20 (below): 73 in all.

### KPI 1: a merge-back acceptance file equal to git's own merge is no change

`test_w2_72_clean_merge_of_an_acceptance_file.py`, 8 tests, **all red now**.

| Test | Cases | Expected | Red now because |
|---|---|---|---|
| `test_the_live_check_neither_restores_refuses_nor_flags_an_acceptance_file_equal_to_git_s_own_merge` | `a-clean-combination-of-two-sides-edits`, `the-same-edit-on-both-sides`, `a-conflict-on-another-file-resolved-by-hand` | silent (exit 0, no text for the agent, no finding), and HEAD, the index and the tree as the call left them | the check flags the test: "a merge commit's own change to a ticket file or an acceptance test" (DEC-410 DP-24) |
| `test_judge_commits_returns_no_finding_for_an_acceptance_file_equal_to_git_s_own_merge` | the same three | `judge_commits([merge])` is `[]` | it returns that finding |
| `test_the_live_check_names_the_engineer_s_commit_and_not_the_merge_commit` | the merged side's edit of the test is an engineer's commit | the engineer's commit has a finding naming the test, as before; no finding is the merge commit's | the merge commit has the DP-24 finding too |
| `test_judge_commits_finds_nothing_in_the_merge_commit_and_still_judges_the_engineer_s_commit` | the same | `judge_commits([engineer])` names the test (passes now); `judge_commits([merge])` is `[]` | the second half: the DP-24 finding |

The three cases:

- *A clean combination:* a test designer changed line 2 of a twenty-line acceptance test on the merged side and
  line 19 on `main`. Git combines the two without a conflict, and the result equals neither parent.
- *The same edit:* both sides made the same edit of line 2, so the result equals both parents.
- *Per file:* as in `03f470a5`. Git reports a conflict on `src/gov/guard/decide.py`, which engineers changed on
  both sides and the merge commit resolves by hand. The acceptance test is merged cleanly. The hand resolution is
  an orchestrator's own change outside `tests/acceptance/` and `.tickets/`, inside the ticket's paths: silent
  today and after (DEC-269). Today's report names the test alone.

The engineer cases carry out "not (a2)": the merge commit is no change of the file whoever made the edits, and the
bringing commit is still judged by its own trailers wherever it is judged.

### KPI 2: any file that differs from git's own merge is still caught

`test_w2_72_file_that_differs_from_git_s_merge.py`, 18 tests, **all pass now** and must keep passing.

| Test | Expected |
|---|---|
| `test_the_live_check_still_flags_an_acceptance_file_that_differs_from_git_s_own_merge` | reported and recorded as `flagged`, in a finding for the merge commit (its `reason` begins `commit <12 digits>`) that names the test; nothing moved |
| `test_judge_commits_still_finds_an_acceptance_file_that_differs_from_git_s_own_merge` | `judge_commits([merge])` is one finding, for the merge commit, naming the test |

Each runs these nine cases:

| Case | The history |
|---|---|
| `a-hand-edit-on-top-of-a-clean-merge` | the clean combination with line 10 changed by hand before the commit |
| `git-s-content-in-another-mode` | git's own blob, committed `100755` (git's merge writes `100644`) |
| `a-conflict-in-the-file-resolved-by-hand` | both sides changed line 2 their own way; resolved to content neither side holds |
| `a-conflict-in-the-file-the-merged-side-s-version-whole` | the same conflict; `git checkout --theirs` |
| `a-conflict-in-the-file-the-first-parent-s-version-whole` | the same conflict; `git checkout --ours` |
| `a-conflict-in-the-file-held-as-git-writes-it-with-its-markers` | the same conflict; the merge commit holds exactly the blob `git merge-tree --write-tree <first parent> <other parent>` writes for the file, with its conflict markers |
| `an-octopus-merge-of-clean-edits` | three parents; lines 2, 10 and 19 changed on the three sides, combined by git without a conflict |
| `a-criss-cross-history-with-two-merge-bases` | two merge bases; the merge commit holds git's own clean merge of the test |
| `unrelated-histories-with-no-merge-base` | no merge base; the merge commit holds git's own clean merge (`--allow-unrelated-histories`) of an acceptance test the other history adds |

### KPI 2: a merge-tree run that cannot run gives no allowance (fail closed)

`test_w2_72_merge_tree_that_cannot_run.py`, 4 tests, **all red now**.

**The seam.** `failing_merge_tree` writes a `git` script into the test's own temporary folder, and that folder is
put first on `PATH`:

- any call whose words hold `merge-tree` is refused, and every other call goes to the real git unchanged;
- it is refused either as `a-fatal-error` (exit 128, a `fatal:` line) or as `a-git-without-write-tree` (exit 129,
  a usage line, as a git older than 2.38 answers);
- each refused call appends one line to a log file next to the script.

The history is the clean combination of KPI 1, which without the seam is no change of the test.

| Test | Expected | Red now because |
|---|---|---|
| `test_the_live_check_still_flags_the_file_when_git_merge_tree_cannot_run` | with the failing `git` on the PostToolUse hook's `PATH` only (the call itself and the PreToolUse hook use the real git): the log holds at least one refused `merge-tree` call, and the test is flagged in a finding for the merge commit | the log is empty: today's check asks no `merge-tree`. The flag is already there |
| `test_judge_commits_still_finds_the_file_when_git_merge_tree_cannot_run` | `judge_commits` in a new process of this `src/` with the failing `git` first on `PATH`: the log holds at least one refused call; the process exits 0; one finding, for the merge commit, names the test | the log is empty. The finding is already there |

**How each case shows that the check met the failure.** The log of refused calls must hold at least one line
written while the check under test ran, either the PostToolUse hook or the judging process. A check that never asks
git's own merge leaves it empty and the case fails, since it would show nothing about failing closed.

`judge_commits` runs in a new process so that nothing a module resolved earlier in the run, such as a path to
git, gets past the seam. "The path stays caught" is read as a finding that names the path. A `ContainmentError`
raised instead fails the case: the KPI line says the path stays the merge commit's own change, as before.

### KPI 3: nothing else changes

`test_w2_72_nothing_else_changes.py`, 19 tests, **all pass now** and must keep passing.

| Test | Cases | Expected |
|---|---|---|
| `test_the_live_check_still_flags_a_clean_merge_of_a_path_outside_the_acceptance_tests` | `a-clean-combination-of-two-sides-edits-of-a-ticket-file` (DEC-421: orchestrator's commits changed `.tickets/DAEO-zz94.md` on both sides and git combined them cleanly); `a-clean-combination-of-another-path-under-an-engineer-s-trailers` (read_merge's rule with DEC-269: git combined two sides' orchestrator edits of `README.md`; the merge commit carries an engineer's trailers whose ticket does not allow it) | flagged, in a finding for the merge commit, naming the path; the brought `pyproject.toml` not named |
| `test_judge_commits_still_finds_a_clean_merge_of_a_path_outside_the_acceptance_tests` | the same two | one finding for the merge commit naming the path |
| `test_read_merge_reads_every_merge_of_this_suite_as_it_does_today` | every merge of this suite (15) | `read_merge`'s `(own, brought)` exactly as DEC-410 and DEC-403 give them today. The cleanly merged acceptance test is still in `own`. With no merge base, every path of the tree is in `own` (DP-23) |

A fix that lifts git's own merge for every path, not only under `tests/acceptance/`, fails the `README.md` cases.
A fix that changes `read_merge` instead of containment's use of it fails the reading cases, and with them the
approval check's reading (`src/gov/decisions/checker.py`, DEC-918 item 4).

The other half of the ticket files' rule is DEC-572's lift for a ticket file held exactly as one parent has it,
when every commit that brought that version passes. W1-50's cases show it and stay unchanged:
`test_w1_50_merge_commit_file_that_equals_one_parent_s_version.py`, which runs in the W1-50 folder.

### KPI 4: the two merge-backs judge clean

`test_w2_72_the_two_merge_backs.py`, 4 tests.

| Test | Cases | Expected | Now |
|---|---|---|---|
| `test_judge_commits_returns_no_finding_for_the_merge_back` | `W2-66-s-merge-back` (`03f470a5`), `W2-65-s-merge-back` (`4ef3293a`) | `judge_commits(<this repository's root>, [<full id>])` is `[]` | **red**: one finding each, "a merge commit's own change to a ticket file or an acceptance test", naming `tests/acceptance/W1-30/test_w1_30_close.py` (`03f470a5`) and `tests/acceptance/W1-26/README.md` with `tests/acceptance/W1-26/test_w1_26_planted_defects.py` (`4ef3293a`) |
| `test_read_merge_still_holds_the_cleanly_merged_acceptance_tests_in_own` | the same two | those acceptance tests are in `read_merge`'s `own` | passes; must keep passing |

The 8-digit forms are written in the test. The full ids are obtained with `git rev-parse --verify <form>^{commit}`
and are not written anywhere in this folder. A repository that does not hold the objects fails the test; it is not
skipped.

The premise guard checks each merge from git's own answers:

- two parents with one merge base, and `Role: orchestrator` with one `Task` in the final trailer block;
- acceptance tests changed by both parents, each held exactly as git's own merge writes it, with no conflict on it;
- for `03f470a5`, a conflict git reports outside `tests/acceptance/` (`src/gov/close/command.py`, resolved by
  hand).

### KPI 5: W1-50's DP-24 cases are revised (Rewrite-Reason: DEC-918)

The W1-50 cases that read git's own clean merge of an acceptance test both sides changed as the merge commit's own,
through the check, are revised to DEC-918's rule. No other expectation is lowered.

| Case | Before | Now |
|---|---|---|
| `test_w1_50_acceptance_test_changed_on_both_sides.py::test_a_clean_combination_of_two_sides_edits_of_one_test_is_silent` (was `..._is_flagged`) | DEC-410 DP-26, "stays flagged, as built": the orchestrator's merge in its own call is a finding that names the test | silent, nothing moved: the merge commit holds git's own clean combination of the two edits |
| `test_w1_50_merge_that_takes_each_side_s_change.py::test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_silent` (was `..._is_flagged`; before DEC-410 it was `..._is_silent`) | DEC-410 DP-24 by its words: the test is named | silent, nothing moved: the merge commit holds git's own merge, which is both parents' content |

Each revised case's docstring states what it expected before, what it expects now, and "Rewrite-Reason: DEC-918".
Both are red now, because the check flags the test, and turn green with the implementation.

Docstring lines only, no expectation changed:

- the module docstrings of the two files (the shapes the revision concerns);
- the DP-24 bullet of `w1_50_own_change_support.py`, which now notes DEC-918's change.

**Kept, not lowered:**

- the cases that read `read_merge` directly
  (`test_read_merge_puts_a_clean_combination_of_two_sides_edits_of_one_test_in_own`,
  `test_read_merge_puts_a_test_both_sides_changed_in_the_same_way_in_own`, and the other helper cases). The
  approval check's reading is unchanged;
- every case where the merge takes one side whole after a conflict, resolves a conflict, hand-edits, or `-X theirs`
  sets a conflict aside (`ONE_SIDE_WHOLE`, `test_the_same_merge_with_a_test_designer_s_trailers_on_the_merge_commit_is_flagged`,
  `test_w1_50_merge_commit_own_changes.py`, `test_w1_50_merge_read_by_the_merge_base.py`). Git's own merge of such
  a file reports a conflict, so it is no clean merge;
- the ticket-file cases (DEC-421, DEC-572).

No other W1-50 case reads git's own clean merge of a both-changed acceptance test through the check or through
`judge_commits`.

## Review 1's batch (tests added after the implementation; Rewrite-Reason: DEC-918)

The ticket's first review drove merges the first batch does not make. These tests come from its findings F1 to F4,
written by a fresh test designer before the engineer changes anything. No part of the implementation was read;
the tests use the hooks around each call, `judge_commits` and git's own answers only.

20 tests: **13 are red now** and **7 pass now** (the "still caught" cases, which must keep passing).

**The flow over several calls** (`bash_call` in `w2_72_support.py`). Each call is one Bash call of a session:

- the PreToolUse hook runs, then the command for real, then the containment check;
- the check runs as PostToolUse, or as PostToolUseFailure when the command failed (`git merge` exits 1 on a
  conflict), as the harness sends it;
- the call returns its exit code, what the agent was told, the findings recorded, `MERGE_HEAD` and the unmerged
  paths, and two snapshots, one before the check and one after it. A snapshot holds HEAD, `git status` with every
  file, the watched files and `git ls-files -s`;
- "the check moved nothing" means the two snapshots are equal.

A failure message shows every call's agent-facing text and finding records.

### F1: a merge-back over two calls keeps git's own merge (KPI 1, DEC-918 item 1)

`test_w2_72_merge_over_two_calls.py`. The merges are made in an orchestrator session's own calls
(`GOV_ROLE=orchestrator`, `GOV_TICKET=DAEO-zz90`), and the merge commit carries `Task: DAEO-zz90` and
`Role: orchestrator`.

| Test | Cases | Expected | Now |
|---|---|---|---|
| `test_a_merge_back_over_two_calls_keeps_git_s_own_merge_of_the_acceptance_tests` | `a-conflict-on-the-source-file-resolved-in-the-second-call` (as `03f470a5`). Call 1, `git merge --no-ff --no-commit w1/W1-90`, stops on a conflict in `src/gov/guard/decide.py`, which both sides' engineers changed, while git combines `test_merged.py` (both sides' test designers changed it) and brings `test_new.py` (only the merged side added it). Call 2 resolves the source file, stages it and commits. `no-conflict-and-the-commit-in-the-second-call`: call 1 is the same merge with no conflict; call 2 is `git commit` with the trailers | neither call's check restores, flags or reports (silent, and nothing moved). The merge commit holds git's own merge of both tests: the combined test as `git merge-tree --write-tree` writes it, and the new test present. The tree and the index equal the merge commit. `judge_commits([merge])` is `[]` | **red**: after call 1 the check reports "Acceptance test restored from HEAD" for both tests (recorded `reverted`). The combined test is set back to the first parent's version and the new one is deleted, in the tree and in the index. Call 2's merge commit holds the first parent's versions: it is flagged ("a merge commit's own change to a ticket file or an acceptance test"), and `judge_commits` returns that finding |
| `test_a_hand_write_of_an_acceptance_test_in_a_merge_over_two_calls_stays_caught` | the history of the no-conflict case, with line 10 of `test_merged.py` changed by hand: `in-the-first-call-after-the-merge` (call 1 merges, then writes); `in-a-call-of-its-own-between` (three calls); `in-the-commit-s-call-before-the-commit` | KPI 2: the check of the call that makes the hand write reports it and records a finding that names the test (restored or flagged). When the committed merge's test differs from git's own merge (it holds the hand write, or a restore that is not git's merge), the commit's check has a finding for the merge commit that names the test, and so has `judge_commits` | passes; must keep passing |
| `test_a_conflict_in_an_acceptance_test_over_two_calls_stays_caught` | both sides changed line 2 of `test_merged.py`, and git reports the test as conflicted (call 1 exits 1). Call 2 stages the first parent's version whole, the merged side's version whole, or the blob git's own merge writes with its markers, then commits | KPI 2: call 1's check catches the conflicted test. The commit's check and `judge_commits` each have a finding for the merge commit that names it | passes; must keep passing |
| `test_the_same_merge_over_two_calls_in_an_engineer_s_session_keeps_today_s_behaviour` | the no-conflict case in an engineer's session (`GOV_ROLE=engineer` on `DAEO-zz90`), committed with the engineer's trailers | DEC-266, today's behaviour. Call 1's check reports both tests and records them as `reverted`, and both are as `HEAD` holds them in the tree and the index. Call 2's merge is flagged with nothing reverted (W1-03's default for a merge that is not a fast-forward) | passes; must keep passing |

### F2 and F3: a drop hidden behind a rename or a file replaced by a directory (KPI 2)

`test_w2_72_drop_behind_a_rename_or_a_directory.py`, 8 tests, **all red now**.

| Test | Expected |
|---|---|
| `test_the_live_check_flags_a_drop_behind_a_rename_or_a_directory` | reported, and recorded as `flagged` in a finding for the merge commit that names a path of the test (its old or new name, the directory's file, or a moved-aside name `<path>~<commit>`). Nothing moved |
| `test_judge_commits_finds_a_drop_behind_a_rename_or_a_directory` | `judge_commits([merge])` returns one finding, for the merge commit, that names such a path |

Each test runs four cases:

| Case | Finding | The history |
|---|---|---|
| `a-clean-rename-the-first-parent-s-renamed-file-whole` | F2 (a) | a test designer renamed `test_merged.py` to `test_renamed.py` on `main` (`git mv`) and changed its line 2 on the merged side. Git's own merge is clean, with the edit at the new name. The merge commit holds `main`'s renamed file whole, so the merged side's edit is dropped |
| `a-conflict-at-the-new-name-the-first-parent-s-version-whole` | F2 (b) | `main`'s rename also changed line 2, so git reports the conflict at the new name. It is resolved with `git checkout --ours` |
| `a-directory-on-main-the-merged-side-s-edit-dropped` | F3 | `main` deleted the test and added a directory of the same name holding `test_inner.py`; the merged side changed line 2. Git reports the conflict only as `test_merged.py~<commit>`. The merge commit keeps the directory and drops the moved-aside copy (`git rm`) |
| `a-directory-on-the-merged-side-the-first-parent-s-edit-dropped` | F3 | the same with the sides swapped, so `main`'s edit is dropped |

`assert_moved_shape` checks each history from git's own answers:

- two parents and one merge base;
- the conflicts git's own merge reports: none, the new name, or one moved-aside name;
- that the merge commit does not hold git's own merge of the folder `tests/acceptance/W1-90/`;
- that it holds one side's version of that folder whole.

**Red now because** both checks are silent on all four: the drop passes as git's own merge.

### F4: git's own clean merge across a rename passes (KPI 1, DEC-918 item 1, DEC-912)

`test_w2_72_clean_merge_across_a_rename.py`, 3 tests, **all red now**.

The history: `main` changed line 2 of `test_merged.py` (a test designer's commit), and the merged side renamed it to
`test_renamed.py` (`git mv`, a test designer's commit). Git's own merge is clean: `main`'s edit at the new name and
the old path gone. The merge commit holds that merge exactly, and the content at the new name is held by neither
parent.

| Test | Expected | Red now because |
|---|---|---|
| `test_the_live_check_is_silent_on_git_s_own_merge_across_a_rename` | one call: silent, and nothing moved | `test_renamed.py` is flagged: "a merge commit's own change to a ticket file or an acceptance test" |
| `test_judge_commits_returns_no_finding_for_git_s_own_merge_across_a_rename` | `judge_commits([merge])` is `[]` | it returns that finding |
| `test_git_s_own_merge_across_a_rename_over_two_calls_is_kept` | F1 (b)'s form, over two calls: as F1's first test expects | after call 1 the check restores both names from `HEAD`, and call 2's merge is flagged |

### Earlier cases that assert the opposite of F1

None of the earlier cases leaves a merge in progress between two calls:

- W1-03 and W1-50 make every merge in one call (`git merge ... && git commit`);
- W1-45, W1-47 and W1-38 make no merge through the hooks.

No earlier case expects a working-tree restore of an acceptance file that a merge in progress holds as git's own
merge, so none is revised.

## Revisions

- `conftest.py` folded into the support module: its fixtures and helpers into `w2_72_support.py`, the import path it set up into the top of each test module. Rewrite-Reason: DEC-880 (W2-66's KPI 12 case). No expectation changed.
- Review 1's batch: 20 tests added after the implementation, from the ticket's first review (F1 to F4). These are three new modules and helpers at the end of `w2_72_support.py`'s merge section (`bash_call`, the two-call histories, the rename and directory histories, and `assert_moved_shape`). The first batch's cases, helpers and expectations are unchanged. Rewrite-Reason: DEC-918.
