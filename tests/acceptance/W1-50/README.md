# W1-50 — Containment attribution by commit trailers: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-xnbx` (W1-50) and the items it
cites: DEC-255, DEC-253, DEC-254, DEC-182, DEC-235, DEC-076, CAP-58 with its covers item `CAP-58.h`. Written before
implementation (DEC-256). Profile FULL (DEC-221).

## Run

```sh
python3 -m pytest tests/acceptance/W1-50 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. The suite takes about 15 seconds.

## How the tests drive the check

The tests use the public interface the W1-03 suite uses, and its support module
(`tests/acceptance/W1-03/w1_03_support.py`, imported by `w1_50_support.py`):

- a throw-away git project under pytest's temporary directory, with both kernel hooks installed and the fixture
  tickets in progress;
- one Bash call as the harness runs it: the PreToolUse hook, the command for real, the PostToolUse hook;
- the result read from outside: the hook's exit code and output, the working tree, `HEAD`, and
  `.gov-runtime/findings.jsonl` (DEC-122).

No test imports `gov.guard.containment` or reads a snapshot file.

The fixture project:

| Name | What |
|---|---|
| `DAEO-zz90` (W1-90) | engineer ticket, in progress: `src/gov/guard/**`, `tests/unit/guard/**`, `pyproject.toml`, the PreToolUse hook |
| `DAEO-zz91` | orchestrator ticket, in progress |
| `DAEO-zz95` | engineer ticket, in progress: `docs/**` |
| `README.md` | outside every engineer ticket's paths; the orchestrator may write it (DEC-156) |
| `tests/acceptance/W1-90/**` | the test designer's paths only |

Commits get their trailers with `git commit --trailer`, in the final trailer block (DEC-182):
`Task: DAEO-zz90` and `Role: engineer`, `Role: independent-test-designer` or `Role: orchestrator`. A commit "without
trailers" carries neither.

Two fixtures in `conftest.py`:

- `call`: one whole Bash call that moves `HEAD` on the same branch and leaves a clean tree.
- `during_a_call`: a Bash call of one actor that changes nothing itself (`true`), with another actor's work between
  its PreToolUse hook and its end. This is a ticket lead's call that waits for its worker (DEC-254).

"Silent" is: exit code 0, nothing reaches the agent, no line is added to `findings.jsonl`. "Flagged" is: reported to
the agent with the path named, and recorded with action `flagged` and that path. In every test the check leaves
`HEAD`, the branch, `git status` and the files as the call left them (DEC-129: committed content is never reverted).

## KPI → tests → red reason

43 test cases in 12 test functions. Red run on `w1/W1-50`: **26 failed, 17 passed, 0 skipped**.

The red reason is the same throughout: the check still judges a `HEAD` move against the caller
(`src/gov/guard/containment.py`), and flags every move that holds a merge commit.

| KPI line | Test function(s) | Expected red reason today |
|---|---|---|
| **Success 1** [CAP-58.h]. A forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit, by each commit's own `Role` and `Task` trailers, not against the caller | `test_commits_inside_the_paths_of_their_own_trailers_are_silent` · `test_each_commit_is_judged_by_its_own_trailers_not_the_move_as_a_whole` · `test_one_commit_outside_its_paths_among_commits_inside_theirs_is_the_only_finding` · `test_a_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it` · `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged` | A test designer's commit in an orchestrator's call is flagged "committed path(s) outside allowed paths". A commit outside its own trailers' paths is silent when the caller may write the path. The two ends of the move are compared, not each commit. A merge is flagged "HEAD moved (not a forward move on the same branch)" with no path |
| **Success 2** [CAP-58.h]. A merge commit itself is not a finding when every commit it brings passes | `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` (4 cases) · `test_a_merged_commit_without_trailers_inside_the_caller_s_paths_is_silent` | The merge is flagged "HEAD moved (not a forward move on the same branch)" |
| **Success 3** [CAP-58.h]. A worker's commit made during another actor's call is judged by its own trailers | `test_a_test_designer_s_commit_during_the_lead_s_call_is_silent` · `test_a_worker_s_commit_inside_its_own_paths_is_silent_in_the_waiting_call` · `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` | The lead's check flags the test designer's commit; it is silent on a worker's commit of a path the lead may write |
| **Success 4** [CAP-58.h]. A commit with no `Role` or `Task` trailer is judged against the caller, as today | `test_a_commit_without_trailers_is_judged_against_the_caller` (green now) · `test_a_commit_without_trailers_made_during_another_actor_s_call_is_judged_against_that_caller` (green now) · `test_in_one_move_only_the_commit_without_trailers_is_judged_against_the_caller` · `test_a_merged_commit_without_trailers_inside_the_caller_s_paths_is_silent` · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged[commit-without-trailers-of-an-acceptance-test]` | In a mixed move the test designer's commit is flagged with the one without trailers. A merge is flagged without a path |
| **Failure 1.** An integration merge whose commits each stay inside their own trailers' paths raises a finding | `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` | As success 2 |
| **Failure 2.** A commit outside its own trailers' paths raises no finding, whoever the caller is | `test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is` (3 commits × 3 callers) · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged` · `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` · `test_each_commit_is_judged_by_its_own_trailers_not_the_move_as_a_whole` | Silent when the caller may write the path itself |
| **Failure 3.** A commit with no `Role` or `Task` trailer is judged by anything other than the caller | The tests of success 4 | As success 4 |
| **Covers `CAP-58.h`** | Every test of the suite; the four success lines carry the id | As above |

## Green in the red run (17 cases)

These describe behaviour that holds today and must hold after W1-50. They guard against a regression.

| Test | Cases | Why green now |
|---|---|---|
| `test_a_commit_without_trailers_is_judged_against_the_caller` | all 8 | KPI success 4 keeps today's rule |
| `test_a_commit_without_trailers_made_during_another_actor_s_call_is_judged_against_that_caller` | 1 | The same |
| `test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is` | 5 of 9 | The caller may not write the path either, so today's rule gives the same finding |
| `test_commits_inside_the_paths_of_their_own_trailers_are_silent` | `an-engineer-commit-of-another-ticket` | The orchestrator may write `docs/notes.md` itself |
| `test_a_worker_s_commit_inside_its_own_paths_is_silent_in_the_waiting_call` | `engineer-commit` | The orchestrator may write the source file itself |
| `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` | `engineer-commit-of-an-acceptance-test` | The orchestrator may not write an acceptance test either |

## What the suite takes as given

- **Not changed by W1-50.** The KPIs speak of a forward `HEAD` move. A reset, a checkout of another branch or
  revision, a rebase, an amended commit, and a commit on a new branch stay flagged as W1-03 tests them. An uncommitted
  change is still judged against the caller. The suite repeats none of these.
- **"Commit by commit".** A commit that leaves its paths is a finding also when a later commit of the same move undoes
  it (`test_a_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it`).
- **Allowed paths of a commit's trailers** are what the guard allows that role on that ticket (CAP-58.a): the ticket's
  `allowed_paths` for its own role, `tests/acceptance/**` for the test designer, everything outside
  `tests/acceptance/**` for the orchestrator (DEC-156). Every fixture ticket is in progress.
- **The merge commit's own trailers** do not decide whether an integration merge passes: a merge commit with
  `Role: orchestrator` and one without trailers are both silent when every commit they bring passes.
- **Callers.** A worker's call is used only where the expected result is a finding. Where the expected result is "no
  finding because the commit's trailers allow the path", the caller is the orchestrator, as in the two cases the owner
  decided (an integration merge, a lead waiting for its worker). See DP-5.

## Decision packages: cases the KPIs leave open

No test fixes an answer to these. Each is returned to the orchestrator with the batch.

| Id | Question | Recommendation |
|---|---|---|
| DP-1 | A merge commit made in a call of a caller other than the orchestrator | Stays flagged as today |
| DP-2 | A commit with only one of the two trailers; trailer lines outside the final trailer block | Judged against the caller |
| DP-3 | Trailers that name an unknown role or ticket, a role that is not the ticket's, or several different values | No allowed paths: every path of the commit is a finding |
| DP-4 | Trailers that name a ticket that is closed or not started | Owner's choice; see the package |
| DP-5 | A worker's call that makes a commit carrying another role's trailers | A finding when the `Role` trailer is not the caller's acting role |
| DP-6 | A merge commit that changes a path beyond what its parents hold | Those paths are judged by the merge commit's own trailers, or the caller without them |
| DP-7 | `role` and `ticket` of the finding record for a commit judged by its trailers | The caller's, with the commit and its trailers named in `reason` |

## Earlier suites

One test of an earlier suite asserts today's behaviour and depends on DP-1:
`tests/acceptance/W1-03/test_w1_03_head_defaults.py::test_a_merge_that_is_not_a_fast_forward_is_flagged` (an engineer
merges commits without trailers). It is unchanged in this batch. No test of W1-03, W1-45 or W1-47 makes a commit with
trailers or a merge by the orchestrator, so no other test of those suites is touched by the KPIs.
