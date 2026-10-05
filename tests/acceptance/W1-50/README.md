# W1-50 — Containment attribution by commit trailers: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-xnbx` (W1-50) and the items it
cites: DEC-255, DEC-253, DEC-254, DEC-182, DEC-235, DEC-076, CAP-58 with its covers item `CAP-58.h`. Written before
implementation (DEC-256). Profile FULL (DEC-221).

Second batch, also before implementation: the seven packages of the first batch are decided (DEC-266 to DEC-270,
DEC-318, DEC-319). One existing case is revised and 45 cases are added.

Third batch, also before implementation: the three packages of the second batch are decided (DEC-327, DEC-358,
DEC-359) and the ticket has a fifth success line (DEC-360). One existing case is revised and 25 cases are added. Three
new packages are open (DP-11 to DP-13). W1-50 can be implemented on decided ground; no package blocks it.

Fourth batch, **added after implementation**: the ticket was implemented and the 113 cases passed. The independent
review after green (DEC-137) found two behaviours the suite did not hold. They came to the test designer as described
behaviours, never as code (DEC-136). 25 cases are added in 8 test functions; no existing case is changed. 15 of them
fail on the implementation as it stands. One new package is open (DP-14). See "Added after implementation".

Fifth batch, **added after implementation**: the fourth batch's cases were implemented and the 138 cases passed. A
second independent review after green (DEC-137) found four more behaviours the suite did not hold. They came to the
test designer as described behaviours, never as code (DEC-136). 30 cases are added in 11 test functions; no existing
case is changed. 23 of them fail on the implementation as it stands. One new package is open (DP-15); the fix of the
third behaviour of that review (a merge commit with a parent that is not new in the move) depends on it. See "Added
after implementation, second review".

## Run

```sh
python3 -m pytest tests/acceptance/W1-50 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. The suite takes 30 to 60 seconds.

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
| `DAEO-zz92` | product-spec ticket, in progress: `docs/spec/**` |
| `DAEO-zz95` | engineer ticket, in progress: `docs/**` |
| `DAEO-zz97` (W1-97) | engineer ticket, closed by the fixture `closed_ticket`: `lib/closed/**` |
| `DAEO-zz98` (W1-98) | engineer ticket with `status: open`, never started: `lib/open/**` |
| `README.md` | outside every engineer ticket's paths; the orchestrator may write it (DEC-156) |
| `tests/acceptance/W1-90/**` | the test designer's paths only |

Commits get their trailers with `git commit --trailer`, in the final trailer block (DEC-182):
`Task: DAEO-zz90` and `Role: engineer`, `Role: independent-test-designer` or `Role: orchestrator`. A commit "without
trailers" carries neither. `Role: owner` is the owner's trailer (DEC-360); `owner` is no agent role and the guard
knows no such role. `Task: decision-record` names no ticket (DEC-359).

Two fixtures in `conftest.py`:

- `call`: one whole Bash call that moves `HEAD` on the same branch and leaves a clean tree.
- `during_a_call`: a Bash call of one actor that changes nothing itself (`true`), with another actor's work between
  its PreToolUse hook and its end. This is a ticket lead's call that waits for its worker (DEC-254).

A third fixture, for the fourth batch: `call_leaving_changes` is `call` for a Bash call that moves `HEAD` and leaves
named paths changed in the working tree and not committed.

"Silent" is: exit code 0, nothing reaches the agent, no line is added to `findings.jsonl`. "Flagged" is: reported to
the agent with the path named, and recorded with action `flagged` and that path. In every test the check leaves
`HEAD`, the branch, `git status` and the files as the call left them (DEC-129: committed content is never reverted).

An **orchestrator session's own call** has `GOV_ROLE=orchestrator` and no subagent. A **worker's call** is a session
of another role, or a subagent of another role inside an orchestrator session (DEC-117).

## The ticket's close commit

DEC-318 judges a closed ticket's commit by whether it is an ancestor of "the ticket's close commit". DEC-358 (owner)
says which commit that is: "the latest commit in HEAD's history in which the ticket's status becomes `closed`. When
no such commit is found for a ticket whose status is `closed`, that is a finding." What the repository's history
holds:

- A ticket is closed when its file in `.tickets/` holds `status: closed`. The guard reads that field
  (`src/gov/guard/decide.py`: a ticket gives paths only with `status: in_progress`).
- The WBS rule "Parallel tickets" (DEC-235): the main orchestrator merges the ticket's branch, re-runs the suites, and
  "only then is the ticket closed".
- The history. Every one of the 15 closed tickets has a commit in which its file's `status` becomes `closed`. For
  the nine latest closes that commit changes only the ticket's file and carries `Task: <ticket id>` and
  `Role: orchestrator` in its final trailer block (for example `bbf71cc9` "W1-15 closed: …", `f912799d`
  "Close W1-07: …").
- The same history also holds what no rule covers: five early closes are part of a larger commit whose trailers are
  the work's (`57631ec9` W1-01, `cd233578` W1-02, `fe6a8884` W1-03, `48ccac7e` W1-04, `442e9c3c` W1-05); one close
  has no trailers in its final block (`3a960dba` W1-45); and two tickets were closed, reopened and closed again
  (W1-02, W1-03). `gov close` (W1-30) is not built.

The fixture `closed_ticket` builds the plain form: exactly one commit in the ticket's history sets `status: closed`;
it changes only `.tickets/DAEO-zz97.md`, from `status: in_progress`; its subject is "W1-97 closed: …"; it carries
`Task: DAEO-zz97` and `Role: orchestrator`; it is in the history of the checked `HEAD`; and the working tree holds
`status: closed`. A test recognises "ancestor of the close commit" with
`git merge-base --is-ancestor <commit> <that commit>`.

The forms DEC-358 decides are in `test_w1_50_close_commit.py`:

- **Closed, reopened and closed again.** Work done after the reopening is no ancestor of the first close commit and
  is an ancestor of the second. It passes inside the ticket's paths, because the latest close commit counts. A commit
  made after the second close is a finding.
- **A close inside a larger commit.** The commit that sets `status: closed` also changes another file. It is the
  close commit: work before it passes, a commit after it is a finding. The fixture's larger commit carries
  `Role: orchestrator` and changes nothing under `tests/acceptance/**`, so the commit itself is allowed (DEC-359).
- **`status: closed` with no close commit.** The ticket's file comes into the history already holding
  `status: closed`, in the commit that adds it, and is never changed. A later commit with a worker's trailers that
  names the ticket, inside the ticket's paths, is a finding. The suite reads "that is a finding" as: the commit that
  names such a ticket is a finding, with its paths. It does not read it as a finding on every call made while such a
  ticket exists.

That last form is the only one a committed history can hold: a `closed` status at `HEAD` always has a commit that
brought it, either as a change of the status or as the file's first version. Whether the file's first version counts
as a commit in which the status "becomes" closed is not said. The test holds under both readings, because the
commit it judges comes after that first version: with a close commit it is no ancestor, without one there is none.
The case that tells the readings apart is package DP-13.

Every status change in the fixtures is committed, and the status in the working tree and at `HEAD` agree. "In HEAD's
history" is the history of `HEAD` as the PostToolUse hook finds it, after the move. The one exception is
`test_w1_50_uncommitted_ticket_state.py` (fourth batch), where the two disagree on purpose.

## "Made during an agent session's call" (KPI success 5, DEC-360)

What the check can know, from the code (`src/gov/guard/containment.py` and the two hooks):

- The PreToolUse hook, when the guard lets a Bash call through, writes a before-snapshot for that call
  (`take_snapshot`): the commit id and branch of `HEAD`, with the status of the working tree. It is stored under the
  call's `tool_use_id`.
- The PostToolUse hook (also on a failed call) loads that snapshot (`check_containment`), reads `HEAD` again and
  compares. When the two commit ids differ, `HEAD` moved during the call. The commits of the move are those in
  `<HEAD before>..<HEAD after>`.
- Nothing else is recorded. The check does not know which process made a commit, nor when: it sees only that a
  commit is in `HEAD`'s history after the call and was not before it. A commit by another session, or by a person at
  a terminal, between the two hooks of a call looks the same as the caller's own (DEC-254 describes this for a
  worker's commit in its lead's call).
- A `HEAD` move between two calls is not seen: each call's snapshot is taken at its own start.

So the suite reads "a commit made during an agent session's call" as: a commit that is new in the repository
between the call's PreToolUse hook and its PostToolUse hook, and is in the history of `HEAD` after the call and not
before it. "Any agent session" is every caller: an orchestrator session's own call, a worker session's call, a
subagent's call. "Carrying a `Role: owner` trailer" is `Role: owner` in the commit's final trailer block (DEC-182),
with or without a `Task` trailer next to it.

Tested (`test_w1_50_owner_commit.py`), each with a path the caller may write itself:

- a `Role: owner` commit created in an orchestrator's call, in an engineer's call and in an engineer subagent's
  call, with and without a `Task` trailer: a finding that names the commit's path;
- such a commit among commits inside their own paths: the only finding;
- such a commit created by someone else while a lead's call waits: a finding in the lead's call. This is the
  literal reading of "during any agent session's call". It also holds when the owner commits from the operator
  console while an agent's call runs, because the check cannot tell who made the commit;
- a `Role: owner` commit that `HEAD` was already on when the call began: no finding, in an orchestrator's call and
  in a worker's call.

Not tested: an owner commit that existed before the call on another branch and **arrives** in the call's move by a
merge or a fast-forward. It was not made during the call, and it is new to `HEAD`'s history in the call, which is all
the check observes. That has happened here: `0f8b0d29` (`Task: DAEO-xog0`, `Role: owner`), made on the integration
branch, came into ticket branches through the leads' merges of that branch. No decision settles it (package DP-11),
and no test fixes an answer: every flagged case above creates the commit inside the call, and the silent case has
the commit in `HEAD`'s history before the call.

## The commits of `gov pause --rollback` (DEC-366, DEC-367)

W1-28 will write two kinds of commit. Under the decisions as they stand W1-50 judges them as follows. The suite
holds no test with a `Reverts-Task` trailer.

- **A revert commit**: `Role: <role>` and `Reverts-Task: <ticket>`, no `Task`. Its final trailer block does not hold
  both `Role` and `Task`, so it is judged against the caller (KPI success 4, DEC-267). `Reverts-Task` is no trailer
  the check reads.
  - Run from the owner's console between agent calls: no hook runs and no call's check sees the move. No finding.
  - Run in an orchestrator session's own call: every path outside `tests/acceptance/**` passes (DEC-156). A revert
    of a test designer's commit changes paths under `tests/acceptance/**`, which the orchestrator may not write:
    **a finding** for each such revert. Every implementation ticket has test designer commits.
  - Run in a worker's call: judged against that worker; paths outside its ticket's paths are findings.
  - With `Role: owner`, in any agent's call: a finding (KPI success 5).
- **The record commit**: `Task: <ticket>` and `Reverts-Task: <ticket>`, changing the ticket's file. DEC-367 names
  no `Role` for it.
  - With `Role: orchestrator`: judged as the orchestrator, allowed outside `tests/acceptance/**` whatever the
    ticket's state (DEC-156, DEC-359). The ticket's file is outside. No finding in an orchestrator's own call.
  - Without a `Role` trailer: judged against the caller (DEC-267). No finding in an orchestrator's own call; a
    finding in a worker's call, where `.tickets/` is outside the caller's paths.
  - With `Role: owner`, in any agent's call: a finding (KPI success 5).

So a permitted rollback, run on the orchestrator's invocation (W1-28 KPI: "only on the owner's or the orchestrator's
invocation"), raises findings for the reverts of the ticket's acceptance-test commits. Whether that stands is
package DP-12.

## KPI and decision → tests → red reason

This section and the next describe the first three batches, written before implementation: 113 test cases in 53
test functions. Red run on `w1/W1-50` before implementation: **74 failed, 39 passed, 0 skipped**. After
implementation all 113 pass.

With the fourth batch the suite held 138 test cases in 61 test functions. The 25 cases of the fourth batch are in
"Added after implementation". Run on the implementation as it stood when they were written: 15 failed, 123 passed,
0 skipped. After their implementation all 138 pass.

The suite now holds **168 test cases in 72 test functions**. The 30 cases of the fifth batch are in "Added after
implementation, second review". Run on the implementation as it stood when they were written: **23 failed, 145
passed, 0 skipped**.

The red reason is the same throughout: the check still judges a `HEAD` move against the caller
(`src/gov/guard/containment.py`), compares only the two ends of the move, reads no trailer and no ticket state, and
flags every move that holds a merge commit with no path named.

| KPI line or decision | Test function(s) | Expected red reason today |
|---|---|---|
| **Success 1** [CAP-58.h]. A forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit, by each commit's own `Role` and `Task` trailers, not against the caller | `test_commits_inside_the_paths_of_their_own_trailers_are_silent` · `test_each_commit_is_judged_by_its_own_trailers_not_the_move_as_a_whole` · `test_one_commit_outside_its_paths_among_commits_inside_theirs_is_the_only_finding` · `test_a_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it` · `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged` | A test designer's commit in an orchestrator's call is flagged "committed path(s) outside allowed paths". A commit outside its own trailers' paths is silent when the caller may write the path. The two ends of the move are compared, not each commit. A merge is flagged "HEAD moved (not a forward move on the same branch)" with no path |
| **Success 2** [CAP-58.h]. A merge commit itself is not a finding when every commit it brings passes | `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` (4 cases) · `test_a_merged_commit_without_trailers_inside_the_caller_s_paths_is_silent` · `test_a_lead_s_merge_of_the_integration_branch_into_its_ticket_branch_is_silent` | The merge is flagged "HEAD moved (not a forward move on the same branch)" |
| **Success 3** [CAP-58.h]. A worker's commit made during another actor's call is judged by its own trailers | `test_a_test_designer_s_commit_during_the_lead_s_call_is_silent` · `test_a_worker_s_commit_inside_its_own_paths_is_silent_in_the_waiting_call` · `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` | The lead's check flags the test designer's commit; it is silent on a worker's commit of a path the lead may write |
| **Success 4** [CAP-58.h]. A commit with no `Role` or `Task` trailer is judged against the caller, as today | `test_a_commit_without_trailers_is_judged_against_the_caller` (green now) · `test_a_commit_without_trailers_made_during_another_actor_s_call_is_judged_against_that_caller` (green now) · `test_in_one_move_only_the_commit_without_trailers_is_judged_against_the_caller` · `test_a_merged_commit_without_trailers_inside_the_caller_s_paths_is_silent` · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged[commit-without-trailers-of-an-acceptance-test]` | In a mixed move the test designer's commit is flagged with the one without trailers. A merge is flagged without a path |
| **Success 5** [CAP-58.h]. A commit carrying a `Role: owner` trailer that is made during any agent session's call is a finding (DEC-360) | `test_a_role_owner_commit_made_in_an_agent_s_call_is_flagged` (3 callers × 2 trailer forms) · `test_among_commits_inside_their_paths_only_the_role_owner_commit_is_a_finding` · `test_a_role_owner_commit_made_by_someone_else_during_an_agent_s_call_is_flagged` · `test_a_role_owner_commit_already_in_the_history_before_the_call_is_no_finding` (2 cases, 1 green now) | Silent: the caller may write the path itself, and no trailer is read. In the history case the orchestrator's call is flagged for the test designer's commit it makes |
| **Failure 1.** An integration merge whose commits each stay inside their own trailers' paths raises a finding | `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` | As success 2 |
| **Failure 2.** A commit outside its own trailers' paths raises no finding, whoever the caller is | `test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is` (3 commits × 3 callers) · `test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged` · `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` · `test_each_commit_is_judged_by_its_own_trailers_not_the_move_as_a_whole` | Silent when the caller may write the path itself |
| **Failure 3.** A commit with no `Role` or `Task` trailer is judged by anything other than the caller | The tests of success 4 | As success 4 |
| **DEC-266.** Only a merge in an orchestrator session's own call is judged commit by commit | `test_a_merge_in_any_other_caller_s_call_stays_flagged` (3 callers, green now) · `test_a_lead_s_merge_of_the_integration_branch_into_its_ticket_branch_is_silent` · the orchestrator's merges of success 1 and 2 · W1-03's `test_a_merge_that_is_not_a_fast_forward_is_flagged` (unchanged) | The lead's merge is flagged as every merge is |
| **DEC-267.** Own-trailer judging needs both trailers in the final block | `test_a_commit_without_both_trailers_in_the_final_block_is_judged_against_the_caller` (5 cases, green now) · `test_both_trailers_in_the_final_block_next_to_other_trailers_are_the_commit_s_own` | The test designer's commit with `Implements:` and a co-author line next to its two trailers is flagged against the orchestrator |
| **DEC-268.** Trailers that name nothing valid allow nothing; a ticket is found by `id` or `wbs_id` | `test_trailers_that_name_nothing_valid_allow_nothing` (5 cases) · `test_among_valid_commits_only_the_one_with_invalid_trailers_is_a_finding` · `test_a_ticket_named_by_its_wbs_id_is_found` · `test_a_ticket_named_by_its_wbs_id_gives_that_ticket_s_paths_and_no_more` | Silent, because the orchestrator may write the path itself. With `Task: W1-90` the test designer's commit is flagged against the caller |
| **DEC-269.** A path the merge commit itself changes is judged by the merge commit's trailers, or against the caller without them | `test_a_merge_commit_s_own_change_outside_its_trailers_paths_is_flagged` (3 cases) · `test_an_orchestrator_s_own_change_in_a_merge_commit_outside_acceptance_tests_is_silent` (2 cases) · `test_an_orchestrator_s_conflict_resolution_under_acceptance_tests_is_flagged` · `test_an_orchestrator_s_conflict_resolution_outside_acceptance_tests_is_silent` · `test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change` | The merge is flagged with no path: the finding does not name the path the merge commit changed, and the silent cases are not silent |
| **DEC-270.** The finding keeps the caller's `role` and `ticket`; `reason` names the commit id and its trailers | `test_the_finding_holds_the_caller_s_role_and_ticket_and_names_the_commit_and_its_trailers` · `test_each_of_two_commits_outside_their_paths_is_named_with_its_own_id_and_trailers` · `test_the_finding_for_a_merged_commit_names_that_commit_not_the_merge_commit` · `test_the_finding_in_a_waiting_lead_s_call_holds_the_lead_s_role_and_ticket` | No finding for the commit: the orchestrator may write `README.md`; the merge is flagged with no path |
| **DEC-318.** A closed ticket's commit is judged by the ticket only as an ancestor of the close commit; a never-started ticket's commit is a finding | `test_a_closed_ticket_s_commits_before_its_close_commit_pass_inside_that_ticket_s_paths` (revised: the move that brings the close commit is silent) · `test_a_closed_ticket_s_commit_before_its_close_commit_is_flagged_outside_that_ticket_s_paths` · `test_a_commit_made_after_the_close_commit_that_names_the_closed_ticket_is_flagged` (2 cases) · `test_a_merged_commit_that_is_not_in_the_close_commit_s_history_is_flagged` · `test_a_commit_that_names_a_ticket_that_was_never_started_is_flagged` (2 cases) | The closed ticket's test designer commit is flagged against the orchestrator. The engineer's commits that name a closed or an open ticket are silent, because the orchestrator may write the path. The merge is flagged with no path |
| **DEC-319.** In a worker's call another role's `Role` trailer is a finding; own-trailer judging only in an orchestrator session's own call | `test_in_a_worker_s_call_a_commit_with_another_role_s_trailer_is_a_finding` (4 cases) · `test_the_same_commit_in_an_orchestrator_session_s_own_call_is_judged_by_its_trailers` (3 cases) · `test_a_worker_s_commit_with_its_own_role_s_trailer_is_judged_against_the_caller` (green now) · the worker callers of `test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is` | An engineer's call with a `Role: orchestrator` commit of its own source file is silent. The orchestrator's call with a test designer's commit is flagged |
| **DEC-327.** In a worker's call a forward move is judged commit by commit against the caller, not by its two ends | `test_a_worker_s_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it` (2 cases: the worker's own trailers, no trailers) · `test_a_worker_s_commit_with_its_own_role_s_trailer_is_judged_against_the_caller` (green now) | Silent: the two ends of the move hold the same files |
| **DEC-358.** The close commit is the latest commit in `HEAD`'s history in which the status becomes `closed`; none found for a closed ticket is a finding | `test_work_between_two_closes_is_judged_by_the_ticket_because_the_latest_close_commit_counts` · `test_a_commit_made_after_the_second_close_that_names_the_ticket_is_flagged` · `test_a_close_inside_a_larger_commit_is_the_close_commit` · `test_a_commit_made_after_a_close_inside_a_larger_commit_is_flagged` · `test_a_commit_that_names_a_closed_ticket_with_no_close_commit_is_flagged` · the DEC-318 tests, whose fixture has one close commit | The moves that bring a closed ticket's work are flagged for the test designer's path. The engineer's commits that name the closed ticket are silent, because the orchestrator may write the path |
| **DEC-359.** An orchestrator commit whose `Task` names a closed ticket, one never started, or no ticket is allowed outside `tests/acceptance/**` and a finding inside | `test_an_orchestrator_commit_with_such_a_task_is_silent_outside_the_acceptance_tests` (3 cases, green now) · `test_an_orchestrator_commit_with_such_a_task_is_flagged_inside_the_acceptance_tests` (3 cases, green now) · `test_a_merge_that_brings_such_orchestrator_commits_is_silent` · `test_a_merge_that_brings_such_an_orchestrator_commit_of_an_acceptance_test_is_flagged` · the close commits and status commits in the moves of the DEC-318 and DEC-358 tests that assert silence | The merge is flagged with no path |
| **Covers `CAP-58.h`** | Every test of the suite; the five success lines carry the id | As above |

## Green in the red run (39 cases)

These describe behaviour that holds today and must hold after W1-50. They guard against a regression. Where a case is
green only because today's rule (the caller) happens to give the decided result, the table says so and names the
case that tells the two rules apart.

| Test | Cases | Why green now |
|---|---|---|
| `test_a_commit_without_trailers_is_judged_against_the_caller` | all 8 | KPI success 4 keeps today's rule |
| `test_a_commit_without_trailers_made_during_another_actor_s_call_is_judged_against_that_caller` | 1 | The same |
| `test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is` | 5 of 9 | The caller may not write the path either, so today's rule gives the same finding. The other 4 tell the rules apart |
| `test_commits_inside_the_paths_of_their_own_trailers_are_silent` | `an-engineer-commit-of-another-ticket` | The orchestrator may write `docs/notes.md` itself |
| `test_a_worker_s_commit_inside_its_own_paths_is_silent_in_the_waiting_call` | `engineer-commit` | The orchestrator may write the source file itself |
| `test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call` | `engineer-commit-of-an-acceptance-test` | The orchestrator may not write an acceptance test either |
| `test_a_merge_in_any_other_caller_s_call_stays_flagged` | all 3 | DEC-266 keeps today's rule for these callers |
| `test_a_commit_without_both_trailers_in_the_final_block_is_judged_against_the_caller` | all 5 | DEC-267 keeps today's rule for these commits. They fail if an implementation reads one trailer, or body lines, as the commit's own |
| `test_a_worker_s_commit_with_its_own_role_s_trailer_is_judged_against_the_caller` | 1 | DEC-319 leaves a worker's own commits to today's rule |
| `test_in_a_worker_s_call_a_commit_with_another_role_s_trailer_is_a_finding` | `engineer-session-test-designer-commit`, `test-designer-session-engineer-commit` | The caller may not write the path either. They do not tell DEC-319 from today's rule; the two `…-orchestrator-commit` cases do, and are red |
| `test_the_same_commit_in_an_orchestrator_session_s_own_call_is_judged_by_its_trailers` | `engineer-commit-of-a-source-file`, `orchestrator-commit-of-a-source-file` | The orchestrator may write the source file itself. The test designer's case tells the rules apart, and is red |
| `test_a_commit_made_after_the_close_commit_that_names_the_closed_ticket_is_flagged` | `test-designer-commit-of-an-acceptance-test` | The orchestrator may not write an acceptance test. The engineer's case tells the rules apart, and is red |
| `test_a_commit_that_names_a_ticket_that_was_never_started_is_flagged` | `test-designer-commit-of-an-acceptance-test` | The same |
| `test_an_orchestrator_commit_with_such_a_task_is_silent_outside_the_acceptance_tests` | all 3 | The caller is the orchestrator, which may write `README.md`; today's rule gives the decided result. After W1-50 they check DEC-359: an implementation that applies DEC-318 or DEC-268 to a `Role: orchestrator` commit fails them. Today they do not tell the rules apart; `test_a_merge_that_brings_such_orchestrator_commits_is_silent` does, and is red |
| `test_an_orchestrator_commit_with_such_a_task_is_flagged_inside_the_acceptance_tests` | all 3 | The orchestrator may not write an acceptance test. After W1-50 they fail if DEC-359 is built without its MR-3 limit. `test_a_merge_that_brings_such_an_orchestrator_commit_of_an_acceptance_test_is_flagged` is the red case |
| `test_a_role_owner_commit_already_in_the_history_before_the_call_is_no_finding` | `engineer-call-with-its-own-commit` | The engineer may write the source file. After W1-50 it fails if the check reads `Role: owner` from commits outside the move. The orchestrator's case is red |

## Added after implementation (fourth batch; DEC-136, DEC-137)

These 25 cases are **tests added after implementation**. The review after green found two behaviours the 113 cases
did not hold; each came to the test designer as a described behaviour. The cases go through the same public interface
as the rest of the suite. The payloads were chosen by running candidate commits through the hooks and reading the
result from outside; no test reads the check's code.

Run when they were written: 15 failed, 10 passed.

### Behaviour 1: bytes a commit's author chooses (`test_w1_50_author_chosen_bytes.py`, 20 cases)

The check judges each commit of a forward move by that commit's own id, parents, `Role` and `Task` trailer values
and changed paths. Trailer values and file names are chosen by whoever makes the commit. Git accepts control
characters in both (not 0x00, and no newline inside a trailer's line).

**What a commit's author puts in a trailer value or a file name never makes the check see another commit, another
role, another ticket or other paths than the commit really has. A commit whose trailer values or paths the check
cannot read unambiguously is a finding, never silence.** This holds for every byte git lets a commit's author put
there. The suite tests four pairs of characters, so that no case rests on one way of separating values and commits:
0x02 with 0x01, 0x01 with 0x03, 0x03 with 0x02, and 0x1f with 0x1e. Git refused none of these bytes, in a trailer
value or in a file name.

Each commit carries, after an ordinary beginning, the two characters and between them text shaped like the record
of a commit that does not exist: a 40-character hexadecimal id, a role and a ticket id. The suite reads "flagged" as
everywhere else: the finding and the report name the path. With the bytes in a trailer value the commit names no
known role or ticket, and every path it changes is a finding (DEC-268). With the bytes in a file name the
acceptance test's own name is an ordinary path of an engineer's commit.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| KPI failure 2, KPI success 1; DEC-268 | `test_a_commit_of_an_acceptance_test_is_flagged_whatever_bytes_its_trailers_or_file_names_hold`: an orchestrator's integration merge, or fast-forward, brings a commit that changes an existing acceptance test with `Role: engineer`-style trailers; the bytes are in the `Role` value, the `Task` value, or the name of a second file inside the engineer ticket's paths | 12 | **10 red, 2 green.** The five cases with 0x02 and 0x01 (`Role` value by merge and by fast-forward, `Task` value by merge, file name by merge and by fast-forward) are **silent**: nothing reported, nothing recorded. The five cases with 0x01 and 0x03, and with 0x03 and 0x02, are reported as "HEAD moved (not a forward move, flagged)" with no path: the move is forward, and the acceptance test is not named. The two cases with 0x1f and 0x1e pass: the acceptance test is named |
| KPI success 5 (DEC-360); DEC-268 | `test_a_role_value_that_begins_with_owner_is_a_finding_whatever_bytes_follow`: a commit of `README.md` made in the orchestrator's own call, `Role` value `owner` followed by the bytes and a record that names the orchestrator's role | 2 | **2 red.** With 0x02 and 0x01 the finding says "a Role: owner commit made during an agent's call: no path": `README.md` is not named. With 0x03 and 0x02 the call is reported as not a forward move, with no path |
| The other side: a path like any other | `test_a_file_with_an_unusual_name_inside_the_commit_s_own_paths_is_silent` and `test_a_file_with_an_unusual_name_outside_the_commit_s_own_paths_is_flagged_by_its_name`: an engineer's commit with ordinary trailers adds a file whose name holds a space, a non-ASCII letter or a tab | 3 + 3 | **6 green.** The behaviour holds today and must hold after the fix: a fix that turns every unusual name into a finding, or that names the path in another spelling, fails them. For the tab the report may write the character as it is or as `\t`; the record's `paths` hold the name as it is |

The two green cases with 0x1f and 0x1e hold now and after the fix for the same reason as the red ones: they fail
if a fix moves the weakness to other bytes.

Not tested: whether a commit that stays inside its own paths and adds a file whose name holds a control character is
silent or a finding. The behaviour allows both ("cannot read unambiguously is a finding").

### Behaviour 2: a ticket's state when the working tree and `HEAD` disagree (`test_w1_50_uncommitted_ticket_state.py`, 5 cases)

DEC-318 and DEC-358 judge a commit that names a closed ticket by the ticket's close commit in `HEAD`'s history.
**An uncommitted edit of a ticket's file does not reopen a closed ticket for the check.** The ticket is `closed` in
the committed file at `HEAD`, with its close commit in `HEAD`'s history; its file is set to `status: in_progress` in
the working tree only; a commit with a worker's trailers that names the ticket is made after the close commit. That
commit names a closed ticket and is no ancestor of its close commit: a finding (DEC-318, DEC-358). The edit of the
ticket's file is the orchestrator's own uncommitted change outside `tests/acceptance/**`; it is no finding and stays
in the working tree.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DEC-318, DEC-358 | `test_a_ticket_reopened_only_in_the_working_tree_stays_closed_for_a_commit_of_the_same_call`: one call edits the ticket's file and makes the commit; an engineer's commit inside the ticket's paths, and a test designer's commit of an acceptance test | 2 | **2 red.** Silent: the commit is judged as a commit of a ticket in progress |
| DEC-318, DEC-358 | `test_a_ticket_reopened_only_in_the_working_tree_before_the_call_stays_closed`: the file was already edited when the call began | 1 | **1 red.** Silent, for the same reason |
| DEC-318 (a ticket in progress is no closed ticket) | `test_commits_made_after_a_committed_reopening_pass_inside_the_ticket_s_paths` · `test_a_commit_made_after_a_committed_reopening_is_flagged_outside_the_ticket_s_paths`: the reopening is a commit, so the ticket is in progress at `HEAD` and in the working tree | 1 + 1 | **2 green.** The behaviour holds today and must hold after the fix: a fix that treats every ticket with a close commit in its history as closed fails the first; the second guards the ticket's paths |

Not tested, because no decision settles them (package DP-14): a ticket in progress at `HEAD` and `closed` only in
the working tree; a ticket `open` at `HEAD` and `in_progress` only in the working tree; `allowed_paths` that differ
between the two; a ticket file that exists only in the working tree.

## Added after implementation, second review (fifth batch; DEC-136, DEC-137)

These 30 cases are **tests added after implementation**. A second review after green found four behaviours the 138
cases did not hold; each came to the test designer as a described behaviour. The cases go through the same public
interface as the rest of the suite. Each case found was first run through the hooks and read from outside; no test
reads the check's code. Git settings are written only into the throw-away project's local configuration.

Run when they were written: 23 failed, 7 passed. Every red case fails on its behaviour assertion, with the fixture's
own guards passed: the check is **silent** (exit code 0, nothing reported, nothing recorded) where a finding is
expected, except the one case noted below.

What a commit really holds is read from the object itself: `final_block` reads the last paragraph of the message
from `git --no-replace-objects cat-file commit`, and the trees are read with `git --no-replace-objects`.

### Behaviour 1: the repository's own git settings and replacement refs (`test_w1_50_repository_settings.py`, 16 cases)

Whoever makes a commit can also write the repository's local git configuration and replacement refs, in the same
call or an earlier one. **The check judges a move's commits as git reads the real objects with default settings,
whatever the repository's local configuration and `refs/replace/` hold.** In every case the call's own command
writes the setting or the replacement ref, after its commits.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| KPI success 5 (DEC-360) | `test_a_role_owner_commit_is_a_finding_whatever_the_repository_s_settings_for_trailers`: `trailer.separators` `=`, `core.commentChar` `R`, `trailer.role.key` another word; a `Role: owner` commit in the orchestrator's own call (`README.md`, `Role: owner` alone) and in an engineer's call (its source file, `Task` and `Role: owner`) | 3 × 2 | **6 red.** Silent |
| DEC-319 | `test_another_role_s_trailer_in_a_worker_s_call_is_a_finding_whatever_the_comment_character`: `core.commentChar` `R`; an engineer's call commits its source file with `Role: orchestrator` | 1 | **1 red.** Silent |
| KPI success 1: the other side | `test_commits_inside_their_own_paths_stay_silent_whatever_the_settings`: all five settings; a test designer's commit of an acceptance test and an engineer's commit of its source file, in the orchestrator's own call | 1 | **1 red.** The test designer's commit is reported as "(Role: none; Task: none): committed path(s) outside allowed paths": its trailers are not read and it is judged against the caller |
| KPI failure 2 | `test_a_merged_root_commit_that_adds_an_acceptance_test_is_flagged`: the orchestrator merges, with unrelated histories allowed, a commit without a parent that adds an acceptance test; `log.showRoot` `false` with engineer trailers and with none; default settings with engineer trailers | 3 | **2 red, 1 green.** With `log.showRoot` `false` silent. With default settings the path is named: the case holds now and after the fix, and no earlier case had a commit without a parent |
| KPI failure 2 | `test_a_commit_that_adds_a_submodule_entry_under_acceptance_tests_is_flagged`: an engineer's commit, in the orchestrator's own call, adds a submodule entry (mode 160000) under `tests/acceptance/**`; `diff.ignoreSubmodules` `all`, and default settings | 2 | **1 red, 1 green.** With the setting silent. With default settings the entry's path is named: holds now and after the fix, and no earlier case had a submodule entry |
| KPI failure 2 | `test_a_replacement_ref_does_not_hide_a_commit_s_change_of_an_acceptance_test`: an engineer's commit changes an existing acceptance test; `git replace` maps the commit's `tests/acceptance` tree to the one before it; the orchestrator's own call and an engineer's call | 2 | **2 red.** Silent |
| KPI success 5 (DEC-360) | `test_a_replacement_ref_does_not_hide_a_role_owner_trailer`: a `Role: owner` commit of `README.md` in the orchestrator's own call; `git replace` maps the commit to a twin with the same tree and parent and no trailers | 1 | **1 red.** Silent |

All the settings and both replacement forms named by the review could be reproduced. One form was left out because
the fixture cannot hold it: a replacement of the **commit** by a twin with another **tree** leaves `git status` with
staged changes (the index no longer matches what git reads as `HEAD`), and the fixture `call` requires a clean tree.
The replacement of the tree object hides the same change and leaves `git status` empty.

### Behaviour 2: a merge commit with a parent that is not new in the move (`test_w1_50_merge_with_an_earlier_parent.py`, 3 cases)

The case the review found: in the orchestrator's own call a merge commit is made with `git commit-tree`, first
parent the current `HEAD`, second parent an earlier commit of `HEAD`'s own history, with that earlier commit's
tree; the branch is moved forward to it. The move holds one new commit. Its tree undoes later test designer's
commits under `tests/acceptance/**`. Run through the hooks, the call is **silent** with orchestrator trailers,
engineer trailers and none.

The behaviour passed to the test designer: when a parent of a merge commit is not itself among the commits new in
the move, what the merge commit changes against its first parent is judged as the merge commit's own change.

**That reading is not the only one DEC-269 allows, so no test fixes an answer for the case found** (package DP-15).
DEC-269 judges a path a merge commit changes "beyond what its parents hold (a conflict resolution, a hand edit)". In
the case found every path of the merge commit holds content one of its parents holds, so by its words DEC-269 finds
no own change; KPI success 2 ("not a finding when every commit it brings passes") finds no commit brought at all.
This suite has read DEC-269 that way since the second batch ("content of `path` that none of its parents holds";
`test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change`). Against it stand MR-3
and DEC-156 (the orchestrator writes nothing under `tests/acceptance/**`), DEC-253 (a merge commit passes when
every change it brings there comes from test designer's commits on the merged side) and the result itself: the same
undoing as a revert commit or as a reset is a finding.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DEC-269, under every reading | `test_a_hand_edit_in_a_merge_commit_whose_second_parent_is_an_earlier_commit_is_flagged`: the same merge commit, its tree `HEAD`'s tree with a hand edit of an existing acceptance test, which neither parent holds; orchestrator trailers, engineer trailers, none | 3 | **3 green.** The behaviour holds today and must hold after any fix: a merge commit's own change is judged also when a parent is an earlier commit |

The other side, an ordinary integration merge whose second parent is new in the move and brings a test designer's
commit, is held by `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent` (4 cases); none is added.

### Behaviour 3: `Role: owner` followed by characters that do not show (`test_w1_50_role_owner_unseen_characters.py`, 9 cases)

**A `Role` value that reads as `owner` once whitespace and control characters around it are removed is a
`Role: owner` commit, and a finding** (KPI success 5, read fail-closed). Each commit is made in the orchestrator's
own call, changes `README.md` and has the `Role` line as its only trailer.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| KPI success 5 (DEC-360) | `test_role_owner_with_characters_around_it_that_do_not_show_is_a_finding`: `owner` followed by a form feed, a vertical tab, a no-break space, a zero-width space, the byte 0x01, the byte 0x7f; and a no-break space before `owner` | 7 | **7 red.** Silent: the commit is judged against the caller |
| KPI success 5 (DEC-360) | `test_role_owner_in_other_letter_case_is_a_finding`: `Role: Owner`, `Role: OWNER` | 2 | **2 green.** The check already takes both for the owner's trailer; no earlier case held them |

### Behaviour 4: a committed path is judged by its name in the commit (`test_w1_50_committed_path_names.py`, 2 cases)

**A path a commit changes is judged by its name in the commit, not by where the working tree leads today.** The
call makes an engineer's commit that changes an existing acceptance test, then marks the committed files under
`tests/acceptance` skip-worktree, replaces that directory in the working tree by a symbolic link to
`src/gov/guard` (inside the engineer ticket's paths) and writes the link's name to `.git/info/exclude`. `git status`
is empty after the call: the hidden swap could be built through the suite's public interface.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| KPI failure 2 | `test_a_committed_acceptance_test_is_flagged_although_its_directory_is_then_a_link_into_the_ticket_s_paths`: the orchestrator's own call and an engineer's call | 2 | **2 red.** Silent. Without the swap the same commit is flagged (`test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is`, `engineer-commit-of-an-acceptance-test`) |

## What the suite takes as given

- **Not changed by W1-50.** The KPIs speak of a forward `HEAD` move. A reset, a checkout of another branch or
  revision, a rebase, an amended commit, and a commit on a new branch stay flagged as W1-03 tests them. An uncommitted
  change is still judged against the caller. The suite repeats none of these.
- **"Commit by commit".** In an orchestrator session's own call, a commit that leaves its paths is a finding also
  when a later commit of the same move undoes it
  (`test_a_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it`). The same holds in a worker's
  call, against the caller (DEC-327; the test of the same name in `test_w1_50_callers.py`).
- **Allowed paths of a commit's trailers** are what the guard allows that role on that ticket (CAP-58.a): the ticket's
  `allowed_paths` for its own role, `tests/acceptance/**` for the test designer on any ticket, everything outside
  `tests/acceptance/**` for the orchestrator on any ticket in progress (DEC-156; DEC-269 says so for a merge commit's
  own change) and, by DEC-359, also on a closed ticket, a ticket never started and a `Task` that names no ticket.
  "A role that is not the ticket's" (DEC-268) is therefore a worker role other than the test designer named with a
  ticket of another role; the case is `Role: engineer` with a product-spec ticket.
- **DEC-359 and DEC-268.** DEC-359 amends DEC-318 and also takes the `Role: orchestrator` commit out of DEC-268's
  "unknown ticket". The DEC-268 cases of the suite carry a worker's role or an unknown role (`Role: engineer` with
  `Task: DAEO-none`, `Role: wizard`), so none is changed. Several different `Task` values on an orchestrator commit
  are not tested: DEC-359 speaks of one `Task` trailer.
- **`Role: owner`.** The suite asserts on a `Role: owner` commit only where KPI success 5 decides: made during the
  call, a finding; in the history before the call, none. It does not rest on reading `owner` as DEC-268's "unknown
  role" (DP-11).
- **A finding names the commit's paths.** DEC-268 says "every path it changes is a finding". DEC-318 and DEC-319 say
  "is a finding"; the suite reads that the same way: the record's `paths` and the report hold the paths the commit
  changes.
- **The merge commit's own trailers** do not decide whether the commits it brings pass. They decide only the paths
  the merge commit itself changes beyond what its parents hold (DEC-269). A conflict resolved to one side's content
  is not such a change. Every merge of the first four batches has a second parent that is new in the move; a merge
  commit whose parent is an earlier commit of `HEAD`'s own history is package DP-15.
- **Callers (DEC-319).** A commit is judged by its own trailers only in an orchestrator session's own call. In a
  worker's call a commit with the worker's own role, or without trailers, is judged against the caller, and a commit
  with another role's `Role` trailer is a finding.
- **The finding record (DEC-270).** "Named in `reason`" is: `reason` holds the commit's id, in full or abbreviated to
  at least seven characters, and the values of its `Role` and `Task` trailers. One finding per commit and one
  finding for several commits both pass.
- **Ticket state (DEC-318).** A ticket's state is its file's `status` as committed and in the working tree, which
  agree in every fixture of the first three batches. Where a closed ticket is reopened only in the working tree, it
  stays closed (fourth batch); the other disagreements are package DP-14. "Never started" is `status: open` on a ticket whose file never held another status. The
  DEC-318 cases judge commits with a worker's `Role` trailer; the orchestrator's are DEC-359's. The move that brings
  a close commit is silent, the close commit included (DEC-359).
- **Callers and a closed ticket.** The DEC-318, DEC-358 and DEC-359 cases are all an orchestrator session's own
  call: only there is a commit judged by its own trailers (DEC-319).

## Decision packages

The ten packages of the first two batches are decided:

| Id | Question | Decision |
|---|---|---|
| DP-1 | A merge commit made in a call of a caller other than the orchestrator | DEC-266: stays flagged |
| DP-2 | A commit with only one of the two trailers; trailer lines outside the final trailer block | DEC-267: judged against the caller |
| DP-3 | Trailers that name an unknown role or ticket, a role that is not the ticket's, or several different values | DEC-268: no allowed paths |
| DP-4 | Trailers that name a ticket that is closed or not started | DEC-318 (owner): by the ticket only as an ancestor of its close commit; never started is a finding |
| DP-5 | A worker's call that makes a commit carrying another role's trailers | DEC-319 (owner): a finding; own-trailer judging only in an orchestrator session's own call |
| DP-6 | A merge commit that changes a path beyond what its parents hold | DEC-269: by the merge commit's own trailers, or the caller without them |
| DP-7 | `role` and `ticket` of the finding record for a commit judged by its trailers | DEC-270: the caller's; commit id and trailers in `reason` |
| DP-8 | How the check finds "the ticket's close commit" | DEC-358 (owner): the latest commit in `HEAD`'s history in which the status becomes `closed`; none found is a finding |
| DP-9 | A commit with `Role: orchestrator` whose `Task` names a closed ticket, one never started, or no ticket | DEC-359 (owner, amends DEC-318): allowed outside `tests/acceptance/**`, a finding inside |
| DP-10 | In a worker's call, is a forward move judged commit by commit against the caller, or by its two ends | DEC-327: commit by commit; an undone commit outside the caller's paths is a finding |

Five packages are open. No test fixes an answer to them. Each is returned to the orchestrator with the batch, in
full. DP-11 to DP-14 do not block the implementation of W1-50: it can be built on decided ground, and each
package's cases wait. DP-14 comes from the fourth batch; the fix of its Behaviour 2 does not depend on it. DP-15
comes from the fifth batch: the fix of its Behaviour 2 **depends on it**; the fixes of its Behaviours 1, 3 and 4 do
not.

| Id | Question | Recommendation | Cases that wait |
|---|---|---|---|
| DP-11 | A `Role: owner` commit that existed before the call and arrives in the call's move by a merge or a fast-forward (as `0f8b0d29` did): a finding or not | The fail-closed reading: a finding, in every caller's call. It marks every lead's merge of the integration branch, and every fast-forward, that brings an owner commit; those findings are then records of a permitted action, as under DEC-254 | An owner commit brought by an orchestrator's merge; by a lead's merge of the integration branch; by a fast-forward in an orchestrator's and in a worker's call |
| DP-12 | A permitted `gov pause --rollback` in an orchestrator's call: its revert commits (`Role` and `Reverts-Task`, no `Task`) are judged against the caller, so each revert of an acceptance-test commit is a finding | Leave W1-50 as decided: the reverts are judged against the caller, and the findings of a permitted rollback are records, noted with the rollback's record commit | A revert commit of a source file and of an acceptance test in an orchestrator's call; the record commit with and without a `Role` trailer |
| DP-13 | Two edges of the close commit: a ticket file whose first version already holds `status: closed`; and whether the close commit itself, when it carries a worker's trailers, counts as "an ancestor of the close commit" | Fail-closed in both: the file's first version is no close commit, so every commit that names the ticket is a finding; the close commit is not its own ancestor | A commit that names the ticket and is older than the ticket's file; the work paths of a close commit with a worker's trailers |
| DP-14 | Which version of a ticket's file gives the ticket's state and `allowed_paths` for a commit judged by its trailers, when the file committed at `HEAD` and the file in the working tree differ, in the cases the decisions do not settle: in progress at `HEAD` and `closed` only in the working tree; `open` at `HEAD` and `in_progress` only in the working tree; different `allowed_paths`; a ticket file only in the working tree | The fail-closed reading: a commit passes only when both the file committed at `HEAD` and the file in the working tree allow it; a ticket file that is not committed names no ticket | A worker's commit that names a ticket closed only in the working tree; one that names a ticket started only in the working tree; a commit inside paths only the working tree's file allows, and inside paths only the committed file allows |
| DP-15 | A merge commit made in an orchestrator session's own call, one of whose parents is not new in the move (an earlier commit of `HEAD`'s own history), and whose tree holds for every path content one of its parents holds: is what it changes against its first parent the merge commit's own change (DEC-269), or no change at all | The fail-closed reading: when a parent of a merge commit is not among the commits new in the move, every path the merge commit changes against its first parent is judged by the merge commit's trailers, or against the caller without them. An ordinary integration merge is not touched | The case found, with orchestrator trailers, engineer trailers and none: flagged, with the acceptance tests named; the same merge commit with a test designer's trailers; one that undoes only paths outside `tests/acceptance/**` |

## Earlier suites

`tests/acceptance/W1-03/test_w1_03_head_defaults.py::test_a_merge_that_is_not_a_fast_forward_is_flagged` makes four
merges in an engineer's call, of commits without trailers, and expects each flagged and nothing reverted. Under
DEC-266 a merge in any caller's call other than an orchestrator session's own stays flagged, so the test is right as
it stands and is unchanged. No test of W1-03, W1-45 or W1-47 makes a commit with trailers or a merge by the
orchestrator, so no other test of those suites is touched by the KPIs or the decisions. None makes a commit with
`Role: owner` either, so KPI success 5 touches none.
