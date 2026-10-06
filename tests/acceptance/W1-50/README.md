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

Sixth batch, **added after implementation**: the fifth batch's cases were implemented and the 168 cases passed. The
five open packages are decided, with one more (DEC-390: DP-11 to DP-16), and a third review found one more behaviour
(`.git/info/grafts`). 45 cases are added in 29 test functions; no existing case is changed, and DEC-390 makes no
existing case wrong. 18 of them fail on the implementation as it stands. One new package is open (DP-17); no fix of
this batch depends on it. See "Added after implementation, DEC-390 and third review".

Seventh batch, **added after implementation**: the sixth batch's cases were implemented and the 213 cases passed. The
closing round's review showed the DP-15 rule of DEC-390 wrong in two ways (F1, F2). DEC-394 (delegated,
stricter-only) replaces it with the three-way rule (DP-18) and decides DP-17; the owner's DEC-398 amends it (several
merge bases, or none, fail closed; one helper reads a merge) and DEC-401 accepts it. 32 cases are added in 13 test
functions; no existing case is changed, and the new rule makes no existing case wrong. 22 of them fail on the
implementation as it stands. One new package is open (DP-19); no fix of this batch depends on it. See "Added after
implementation, DEC-394 and DEC-398".

Eighth batch, **added after implementation**: the seventh batch's cases were implemented and the 245 cases passed. A
review found that a merge commit which keeps its first parent's content of a path, and so drops what another parent
changed, is never judged. DEC-403 (delegated) closes it with the symmetric rule (DP-20) and decides DP-19; the
review's F3 makes the helper's error public and its `commit` argument checked. 43 cases are added in 21 test
functions, and 34 of them fail on the implementation as it stands. Three existing test functions are rewritten after
implementation, reason "delegated decision, DEC-403"; 3 of their 10 cases fail until the rule is built. Three new
packages were open then (DP-21 to DP-23; decided since by DEC-410, tenth batch); no fix of this batch depends on
them. See "Added after implementation, DEC-403".
The suite now holds 288 cases: 251 pass and 37 fail.

Ninth batch, **added after implementation**: the eighth batch's cases were implemented and the 288 cases passed. A
review of the DEC-403 rule found two behaviours the suite did not hold: a move to a merge commit with very many
parents is passed over in silence, because the post-command hook is stopped at the harness's time limit; and
`read_merge` reads a `commit` argument that has a commit id's form and is not the id of a commit. They came to the
test designer as described behaviours, never as code. 8 cases are added in 6 test functions, reason "review finding,
DEC-403"; 5 of them fail on the implementation as it stands. No existing case is changed, and no new package is open.
See "Added after implementation, review of the DEC-403 rule". The suite now holds 296 cases: 291 pass and 5 fail.

Tenth batch, **added after implementation**: the ninth batch's cases were implemented and the 296 cases passed.
DEC-410 (delegated, stricter-only) decides the packages DP-21 to DP-28. Four of its points change behaviour: a merge
commit's own change of a ticket file (DP-21) or of an acceptance test (DP-27) is a finding whatever its trailers; an
acceptance test more than one parent changed is the merge commit's own change whichever side's content it holds
(DP-24, with DP-26); and `brought` is the complement of `own` over every parent (DP-22). 42 cases are added in 22
test functions, reason "delegated decision, DEC-410"; 29 of them fail on the implementation as it stands. Ten
existing test functions (20 cases) are rewritten after implementation, same reason; 14 of their cases fail until the
decision is built. No package is open. See "Added after implementation, DEC-410". The suite now holds 338 cases: 295
pass and 43 fail.

Eleventh batch, **added after implementation**: the tenth batch's cases were implemented and the 338 cases passed. A
review found one behaviour the suite did not hold: DP-28 bounds one merge commit, and nothing bounds the move, so a
move of very many merge commits with 24 parents each is passed over in silence, because the post-command hook is
stopped at the harness's time limit. It came to the test designer as a described behaviour, never as code. 4 cases are
added in 3 test functions, reason "review finding, DEC-410"; 2 of them fail on the implementation as it stands. No
existing case is changed, and no new package is open. See "Added after implementation, review of DEC-410". The suite
now holds 342 cases: 340 pass and 2 fail.

## Run

```sh
python3 -m pytest tests/acceptance/W1-50 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. The suite takes about a minute and a half; while the two red cases
of the eleventh batch are red, each of them adds about the harness's hook limit (30 s).

## How the tests drive the check

The tests use the public interface the W1-03 suite uses, and its support module
(`tests/acceptance/W1-03/w1_03_support.py`, imported by `w1_50_support.py`):

- a throw-away git project under pytest's temporary directory, with both kernel hooks installed and the fixture
  tickets in progress;
- one Bash call as the harness runs it: the PreToolUse hook, the command for real, the PostToolUse hook;
- the result read from outside: the hook's exit code and output, the working tree, `HEAD`, and
  `.gov-runtime/findings.jsonl` (DEC-122).

No test imports `gov.guard.containment` or reads a snapshot file. The one exception to "no import from `src`" is
`test_w1_50_read_merge_helper.py` (seventh batch) with `test_w1_50_read_merge_every_parent.py` (eighth batch), the
helper cases of `test_w1_50_review_of_the_symmetric_rule.py` (ninth batch) and those of
`test_w1_50_acceptance_test_changed_on_both_sides.py` and `test_w1_50_read_merge_brought.py` (tenth batch):
DEC-398 makes `gov.guard.containment_merge.read_merge` a public name that a second ticket uses, and those cases
call it by that name.

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
The case that tells the readings apart was package DP-13. DEC-390 decides it, with two more edges: the file's first
version is no close commit, the close commit is not "before" itself when it carries a worker's trailers, and a close
made by a merge commit does not count. The three cases are in `test_w1_50_close_commit_edges.py` (sixth batch).

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

An owner commit that existed before the call on another branch and **arrives** in the call's move by a merge or a
fast-forward was not made during the call, and it is new to `HEAD`'s history in the call, which is all the check
observes. That has happened here: `0f8b0d29` (`Task: DAEO-xog0`, `Role: owner`), made on the integration branch, came
into ticket branches through the leads' merges of that branch. This was package DP-11. DEC-390 decides it, "as built
until the owner says otherwise": such a commit is a finding, and the finding is a record of a permitted action
(DEC-254). Tested in `test_w1_50_owner_commit_that_arrives.py` (sixth batch): brought by an orchestrator's `--no-ff`
merge, and by a fast-forward in an orchestrator's and in an engineer's call.

## The commits of `gov pause --rollback` (DEC-366, DEC-367)

W1-28 will write two kinds of commit. Under the decisions as they stand W1-50 judges them as follows. The revert
commit in an orchestrator's call is tested in `test_w1_50_rollback_commits.py` (sixth batch), built by hand; no test
runs `gov pause`.

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
invocation"), raises findings for the reverts of the ticket's acceptance-test commits. Whether that stands was
package DP-12. DEC-390 decides it, "as built until the owner says otherwise": the commits are judged like any other
commit, and where they are findings, the findings are records.

## KPI and decision → tests → red reason

This section and the next describe the first three batches, written before implementation: 113 test cases in 53
test functions. Red run on `w1/W1-50` before implementation: **74 failed, 39 passed, 0 skipped**. After
implementation all 113 pass.

With the fourth batch the suite held 138 test cases in 61 test functions. The 25 cases of the fourth batch are in
"Added after implementation". Run on the implementation as it stood when they were written: 15 failed, 123 passed,
0 skipped. After their implementation all 138 pass.

With the fifth batch the suite held 168 test cases in 72 test functions. The 30 cases of the fifth batch are in
"Added after implementation, second review". Run on the implementation as it stood when they were written: 23
failed, 145 passed, 0 skipped. After their implementation all 168 pass.

With the sixth batch the suite held 213 test cases in 101 test functions. The 45 cases of the sixth batch are in
"Added after implementation, DEC-390 and third review". Run on the implementation as it stood when they were written:
18 failed, 195 passed, 0 skipped. After their implementation all 213 pass.

The suite now holds **245 test cases in 114 test functions**. The 32 cases of the seventh batch are in "Added after
implementation, DEC-394 and DEC-398". Run on the implementation as it stands: **22 failed, 223 passed, 0 skipped**.
The 213 earlier cases all pass.

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

Not tested in this batch, because no decision settled them then (package DP-14): a ticket in progress at `HEAD` and
`closed` only in the working tree; a ticket `open` at `HEAD` and `in_progress` only in the working tree;
`allowed_paths` that differ between the two; a ticket file that exists only in the working tree. DEC-390 decides
them (both must allow); the cases are in `test_w1_50_ticket_file_at_head_and_in_the_tree.py` (sixth batch).

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

**That reading is not the only one DEC-269 allows, so no test of this batch fixes an answer for the case found**
(package DP-15). DEC-390 decided it as the reading above; the case found is tested in
`test_w1_50_merge_that_undoes_earlier_commits.py` (sixth batch). DEC-394, as amended by DEC-398, has since replaced
that rule by the three-way rule (seventh batch), which gives the same finding for the case found. What follows is the ground of the package as it
stood. DEC-269 judges a path a merge commit changes "beyond what its parents hold (a conflict resolution, a hand edit)". In
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

## Added after implementation, DEC-390 and third review (sixth batch; DEC-136, DEC-137)

These 45 cases are **tests added after implementation**. Their reason is "delegated decision, DEC-390" for the
packages DP-11 to DP-16 and "review finding" for `.git/info/grafts`. The behaviours came to the test designer as
described behaviours, never as code. The cases go through the same public interface as the rest of the suite; each
was run through the hooks and read from outside, and no test reads the check's code. Grafts are written only into
the throw-away project.

Run when they were written: **18 failed, 27 passed**. Every red case fails on its behaviour assertion, with the
fixture's own guards passed. 17 of them are **silent** (exit code 0, nothing reported, nothing recorded) where a
finding is expected; one reports a finding where silence is expected (noted below).

### DP-15: a merge commit that undoes earlier commits through a parent that is not new in the move (`test_w1_50_merge_that_undoes_earlier_commits.py`, 11 cases)

DEC-390: "when a merge commit has a parent that is not among the commits new in the move, every path it changes
against its first parent is judged by the merge commit's own trailers, or against the caller without them. An
ordinary integration merge, whose other parent is new in the move, is read as before (DEC-269)."

**That rule is replaced** by DEC-394 (DP-18) as amended by DEC-398: a merge commit's own change is read against the
merge base, and whether a parent is new in the move no longer matters (see "Added after implementation, DEC-394 and
DEC-398"). The 11 cases of this section are unchanged, because each holds under both rules. In the move below the
second parent is the merge base of the two parents, so it changed nothing against that base: every path the merge
commit changes against its first parent is its own change under the three-way rule too. In the two integration
merges of the last row each path comes from the parent that changed it against the merge base. Only the reason the
files give in their docstrings ("a parent that is not new in the move") is the replaced one. The two forms that tell
the rules apart, F1 and F2, are in the seventh batch.

The move is the one of the fifth batch's Behaviour 2, with the tree the review found: the merge commit is made with
`git commit-tree` in the orchestrator's own call, first parent `HEAD`, second parent the commit before some earlier
commits, tree that of the second parent; the branch is moved forward to it with `git merge --ff-only`. The move holds
one new commit, and what it changes against its first parent is the paths of the undone commits.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-15; MR-3 | `test_a_merge_commit_that_undoes_test_designer_commits_through_an_earlier_parent_is_flagged`: the undone commits are a test designer's edit of an existing acceptance test and a test designer's new test; the merge commit carries orchestrator trailers, engineer trailers, none. Both paths are named | 3 | **3 red.** Silent |
| DP-15 ("by the merge commit's own trailers") | `test_the_same_merge_commit_with_a_test_designer_s_trailers_is_judged_by_those_trailers`: the same merge commit with a test designer's trailers on the ticket in progress. Every path it changes is under `tests/acceptance/**`, which those trailers allow: silent, as for any test designer's commit in an orchestrator session's own call | 1 | **1 green.** Holds now and after the fix: a fix that flags every such merge commit whatever its trailers fails it |
| DP-15 | `test_a_test_designer_s_merge_commit_that_also_undoes_a_source_file_is_flagged_for_that_file`: the same, undoing an engineer's commit of a source file as well. The source file is named, the acceptance tests are not | 1 | **1 red.** Silent |
| DP-15: the other side | `test_a_merge_commit_that_undoes_only_paths_its_trailers_or_the_caller_may_write_is_silent`: orchestrator trailers and no trailers undoing orchestrator commits of `README.md` and `docs/notes.md`; engineer trailers undoing engineer commits inside the ticket's paths | 3 | **3 green.** Hold now and after the fix: a fix that flags the form of the commit, not its paths, fails them |
| DP-15 ("own trailers", not the caller) | `test_a_merge_commit_that_undoes_a_path_outside_its_own_trailers_paths_is_flagged`: engineer trailers undoing the orchestrator's commits of `README.md` and `docs/notes.md`, which the caller may write itself | 1 | **1 red.** Silent |
| KPI success 2, DEC-269: the other side | `test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork`: an ordinary `--no-ff` merge of a ticket branch that forked from an earlier commit and brings a test designer's commit and an engineer's; since the fork `main` got a test designer's commit too, so the merge commit differs under `tests/acceptance/**` from each parent. Merge commit with orchestrator trailers and with none | 2 | **2 green.** Hold now and after the fix: a fix that judges every merge commit's difference from its first parent, or from any parent, as its own change fails them |

The ordinary integration merge is also held by two existing cases of
`test_an_integration_merge_of_commits_inside_their_own_paths_is_silent`, each bringing a test designer's commit under
`tests/acceptance/**` and an engineer's commit inside its ticket's paths: `no-ff-merge-of-a-branch-that-is-ahead`
(the merge base is `HEAD`) and `diverged-branches` (the branch forked from an earlier commit of `HEAD`'s history: the
merged side's commits are new in the move, the merge base is old).

A merge commit with a test designer's trailers that undoes acceptance tests is silent in the orchestrator's own call.
That is what DEC-390's words give, and it is the rule every commit already follows there (DEC-319): the check reads
the trailers, it does not know who typed them.

### DP-16: a commit with a worker's `Role` trailer that changes a ticket file (`test_w1_50_worker_commit_of_a_ticket_file.py`, 12 cases)

DEC-390: "a change under `.tickets/**` in a commit that carries a worker's `Role:` trailer is a finding." Found by
review: a commit that rewrites the ticket it is judged by, or adds the ticket it names, leaves `HEAD` and the working
tree agreeing on the widened file, so every later reading of the ticket allows its work.

Each test asserts the finding that names the ticket file. None asserts anything about the work path (`README.md`):
whether it is a finding of its own is not what DP-16 decides. The entry the fixtures add to `allowed_paths` is `"**"`.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-16 | `test_an_engineer_s_commit_of_a_ticket_file_made_in_the_orchestrator_s_call_is_flagged`: one commit adds `**` to its own ticket and changes `README.md`; a first commit widens and a second works under it; one commit creates the ticket `DAEO-zz99` in progress with `**`, names it and changes `README.md` | 3 | **3 red.** Silent |
| DP-16 | `test_an_engineer_s_commit_of_a_ticket_file_brought_by_an_integration_merge_is_flagged`: the same three, on the ticket branch, brought by the orchestrator's `--no-ff` merge | 3 | **3 red.** Silent |
| DP-16 (the trailer decides, not the ticket's paths) | `test_an_engineer_s_commit_of_a_ticket_file_is_flagged_although_the_ticket_s_paths_allow_it`: an orchestrator's commit gave the ticket `**` before the call; the engineer's commit then adds a line to the ticket file and changes `README.md` | 1 | **1 red.** Silent |
| DP-16 (the trailer decides, not the caller) | `test_an_engineer_s_commit_that_widens_its_own_ticket_in_its_own_call_is_flagged`: an engineer session's call makes the widening commit with its own trailers | 1 | **1 red.** Silent |
| DP-16 ("a worker's `Role:`") | `test_a_product_spec_commit_that_widens_its_own_ticket_is_flagged`: `Role: product-spec` on its ticket `DAEO-zz92` | 1 | **1 red.** Silent |
| DP-16 ("a worker's `Role:`") | `test_a_test_designer_s_commit_of_a_ticket_file_is_flagged`: `Role: independent-test-designer`, widening the engineer ticket and adding an acceptance test | 1 | **1 green.** A ticket file is outside the test designer's paths already. It fails if a fix reads the widened ticket for that role too |
| DEC-156, DEC-359: the other side | `test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent`: the same widening commit with `Role: orchestrator` | 1 | **1 green.** Holds now and after the fix |
| DP-14, KPI success 1: the other side | `test_an_engineer_s_commit_under_paths_an_orchestrator_s_commit_gave_the_ticket_is_silent`: in one call the orchestrator's commit widens the ticket and the engineer's commit then changes `README.md` only | 1 | **1 green.** Holds now and after the fix: a fix that makes every commit of a move a finding once the move changes its ticket fails it. It is also the fixtures' guard that the entry `"**"` is read as allowing `README.md` |

An orchestrator's commit of a ticket file that arrives in the call is held by existing cases: the close commits and
status commits in the moves of `test_a_closed_ticket_s_commits_before_its_close_commit_pass_inside_that_ticket_s_paths`,
`test_work_between_two_closes_is_judged_by_the_ticket_because_the_latest_close_commit_counts` and
`test_a_close_inside_a_larger_commit_is_the_close_commit`. Nothing is added for `Role: owner` or for commits without
trailers. A ticket file changed by a commit without trailers in a worker's call was package DP-17; DEC-394 decides it
(seventh batch, `test_w1_50_ticket_file_commit_in_a_worker_s_call.py`).

### Review finding: `.git/info/grafts` (`test_w1_50_grafts.py`, 9 cases)

A repository-local file `.git/info/grafts` tells git that a commit has other parents than its object holds. **The
check judges a move's commits as git reads the real objects, whatever `.git/info/grafts` holds.** This is the fifth
batch's Behaviour 1 for one more repository-local file; DEC-390 notes that it needs no decision.

One call makes two commits, A and then B, and writes the line `<B> <HEAD before the call>` into the grafts file.
Git's history walk then lists B alone for the move, and B seems to change what A and B change together. Each flagged
case has a twin without the grafts file (`without-a-graft`), which is flagged already: the graft alone makes the
case silent today. The tests read the real commits with `GIT_GRAFT_FILE` set to an empty file.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| KPI success 5 (DEC-360) | `test_a_graft_does_not_hide_a_role_owner_commit`: the orchestrator's own call; A is a `Role: owner` commit of `README.md`, B an orchestrator's commit of `docs/notes.md` | 2 | **1 red** (with the graft: silent), **1 green** (the twin) |
| KPI failure 2 | `test_a_graft_does_not_put_an_engineer_s_change_of_an_acceptance_test_under_a_test_designer_s_trailers`: the orchestrator's own call; A is an engineer's commit of an existing acceptance test, B a test designer's commit of a new one, whose trailers would allow both paths | 2 | **1 red** (silent), **1 green** (the twin) |
| KPI failure 2, DEC-327 | `test_a_graft_does_not_hide_an_engineer_s_undone_change_of_an_acceptance_test_in_its_own_call`: an engineer's call; A changes an existing acceptance test, B puts it back and changes the engineer's source file | 2 | **1 red** (silent), **1 green** (the twin) |
| KPI success 1: the other side | `test_commits_inside_their_own_paths_stay_silent_with_a_graft_written_in_the_call`: a test designer's commit then an engineer's in the orchestrator's own call; two engineer commits inside the ticket's paths in an engineer's call | 2 | **1 red, 1 green.** In the orchestrator's call the check **reports a finding that is none**: "commit … (Role: engineer; Task: DAEO-zz90): committed path(s) outside allowed paths: tests/acceptance/W1-90/test_new.py". With the graft the engineer's commit seems to add the test designer's file. The engineer's case passes |
| KPI success 1: the other side | `test_commits_inside_their_own_paths_stay_silent_with_a_graft_from_before_the_call`: the grafts file was written before the call, for an earlier commit | 1 | **1 green.** Holds now and after the fix |

A graft that names the newest commit cannot be written before the call that makes the commit, so the red cases
write it in the call. Probed and not added: `.git/shallow` naming the newest commit. The call is then reported as
"HEAD moved (not a forward move, flagged)" with no path. That is a finding and not silence, so no case is added; the
move is forward, and the report names no path.

### DP-11, DP-12, DP-13, DP-14: as the check already does (13 cases, all green)

DEC-390 fixes, for these four packages, the reading the implementation already has. The cases hold it; a later change
that leaves it fails them.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-11; KPI success 5 | `test_w1_50_owner_commit_that_arrives.py` · `test_a_role_owner_commit_made_before_the_call_that_arrives_in_its_move_is_flagged`: the owner's commit is made before the call, outside any call, on a branch; it is brought by an orchestrator's `--no-ff` merge, by a fast-forward in an orchestrator's call, and by a fast-forward in an engineer's call. The path is one the caller may write itself | 3 | **3 green** |
| DP-13 ("a ticket file whose first version is already `closed` is not a close commit") | `test_w1_50_close_commit_edges.py` · `test_a_commit_older_than_a_ticket_file_that_begins_closed_is_flagged`: an engineer's commit that names the ticket is older than the commit that adds the ticket's file with `status: closed` | 1 | **1 green** |
| DP-13 ("the close commit itself is not "before" itself") | `test_the_work_paths_of_a_close_commit_with_a_worker_s_trailers_are_flagged`: one commit with the engineer's trailers sets `status: closed` and adds a file inside the ticket's paths. The work path is named. (Its ticket-file change is a finding too, by DP-16; this test does not assert it) | 1 | **1 green** |
| DP-13 ("a close made by a merge commit does not count") | `test_a_close_made_by_a_merge_commit_is_no_close_commit`: a merge commit's own hand edit sets `status: closed`; the ticket's earlier work, an ancestor of the merge commit, is a finding | 1 | **1 green** |
| DP-14 | `test_w1_50_ticket_file_at_head_and_in_the_tree.py` · `test_a_ticket_closed_only_in_the_working_tree_is_closed_for_a_commit_that_names_it` · `test_a_ticket_started_only_in_the_working_tree_is_not_started_for_a_commit_that_names_it` · `test_a_path_only_the_working_tree_s_ticket_file_allows_is_flagged` · `test_a_path_only_the_committed_ticket_file_allows_is_flagged` · `test_a_ticket_file_that_is_only_in_the_working_tree_names_no_ticket` | 5 | **5 green** |
| DP-12; KPI success 4, DEC-267 | `test_w1_50_rollback_commits.py` · `test_a_revert_commit_with_role_and_reverts_task_is_judged_against_the_caller`: a revert commit with `Role: orchestrator` and `Reverts-Task`, no `Task`, in the orchestrator's own call: of an engineer's source file (silent) and of a test designer's acceptance test (a finding, a record under DEC-390) | 2 | **2 green** |

The fifth DP-14 form, a ticket closed at `HEAD` and reopened only in the working tree, is the fourth batch's
`test_w1_50_uncommitted_ticket_state.py`. The record commit of a rollback with `Role: orchestrator` is an
orchestrator's commit of a ticket file, held by the cases named under DP-16.

## Added after implementation, DEC-394 and DEC-398 (seventh batch)

These 32 cases are **tests added after implementation**. Their reason is "delegated decision, DEC-394" for the
three-way rule (DP-18) and for DP-17, and "owner decision, DEC-398" for the cases with several merge bases or none
and for the helper. The behaviours came to the test designer as described behaviours, never as code. Apart from the
helper's cases, every case goes through the same public interface as the rest of the suite; each was run through the
hooks and read from outside, and no test reads the check's code. Every history is a real git history built in the
throw-away project with commits, `git merge` and, where a shape needs it, `git commit-tree`.

No existing case is changed: no case of the sixth batch gives another answer under the three-way rule (see the note
under DP-15 above).

Run when they were written: **22 failed, 10 passed**. Every red case fails on its behaviour assertion, or on the
missing module for the helper, with the fixture's own guards passed.

**The rule (DEC-394 DP-18, as amended by DEC-398 and accepted by DEC-401).** A path a merge commit changes against
its first parent is *brought by another parent* only when the merge commit holds that parent's content of the path
and that parent's content of the path differs from the merge base of the first parent and that parent. Otherwise the
change is the merge commit's *own*, judged by the merge commit's trailers, or against the caller when it has none.
Whether a parent is new in the move no longer matters. With several merge bases (a criss-cross history) or none
(unrelated histories) it fails closed: nothing counts as brought, and every path the merge commit changes against
its first parent is its own change, whatever the parents hold.

The histories are built in `w1_50_support.py` ("Seventh batch"). Each builder returns the command that makes the
merge commit, the paths that are the merge commit's own and the paths another parent brought, as literal lists.
`assert_shape` then checks the built history from git's own answers: the parents, the number of merge bases, the
paths changed against the first parent, and the two lists worked out by the words of the rule
(`read_by_the_words`). That is a guard for the fixtures; the expectation each test asserts is the literal list.

### DP-18: the three-way rule through the check (`test_w1_50_merge_read_by_the_merge_base.py`, 19 cases)

Every call is an orchestrator session's own call.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-18, F1; MR-3 | `test_a_merge_commit_that_undoes_test_designer_commits_through_a_new_empty_commit_is_flagged`: `main` holds a test designer's edit of an existing acceptance test and a test designer's new test. The call makes an empty commit on top of the commit before them (new in the move, no change of its own) and a merge commit with the parents `HEAD` and that empty commit and the earlier commit's tree. Merge commit with orchestrator trailers, engineer trailers, none. Both paths are named | 3 | **3 red.** Silent: no parent is "not new in the move", so today's rule reads the tree as content a parent holds |
| DP-18, "consequences accepted" | `test_a_merge_that_sets_a_test_back_to_the_merged_branch_s_unchanged_content_is_flagged`: a branch changed a source file only; `main` got a test designer's change of an acceptance test; a real merge in which that test is set back to the branch's content, which is the merge base's. Orchestrator trailers, none. The test is named, the source file is not | 2 | **2 red.** Silent |
| DP-18, "`-s ours` turned round" | `test_a_merge_commit_that_holds_the_merged_branch_s_whole_tree_is_flagged_for_what_it_drops`: the merge commit's tree is the merged branch's; it puts back a test a test designer edited on `main` and removes one a test designer added there. Both are named, the branch's source file is not | 1 | **1 red.** Silent |
| DP-18, F2; KPI failure 1 | `test_a_merge_back_of_a_ticket_branch_that_earlier_merged_main_into_itself_is_silent`: the branch earlier merged `main` into itself (orchestrator trailers; that merge brought a test designer's commit of another ticket's acceptance test), then got an engineer's commit and a test designer's, and is merged back with `--no-ff`. `main` did not move meanwhile (the merge base is `HEAD`), and `main` moved on (the merge base is an earlier commit) | 2 | **2 red.** A finding that is none: "commit … (Role: orchestrator; Task: DAEO-zz90): committed path(s) outside allowed paths: tests/acceptance/W1-95/test_other.py". The branch's earlier merge is a commit of the move with a parent that is not new in it |
| DP-18: the other side | `test_a_second_merge_of_the_same_branch_is_silent`: the branch was merged before the call, got two more commits, and is merged again | 1 | **1 green.** Holds now and after the fix |
| DP-18: the other side | `test_an_octopus_merge_of_two_branches_with_commits_inside_their_own_paths_is_silent`: one merge commit with three parents; a test designer's new test from one branch, an engineer's source file from the other | 1 | **1 green.** Holds now and after the fix: a fix that reads only the second parent fails it |
| DP-18: the other side | `test_a_merge_that_takes_the_merged_side_s_content_of_paths_both_sides_changed_is_silent`: `-X theirs` on an acceptance test (test designer's commits on both sides) and a source file (engineer's commits on both sides) | 1 | **1 green.** Holds now and after the fix: a fix that takes every path both sides changed for the merge commit's own fails it |
| DEC-398 (several merge bases) | `test_a_criss_cross_merge_that_changes_an_acceptance_test_is_flagged`: `main` and a second branch each made a commit and each merged the other's (two merge bases); the second branch then got a test designer's new test and is merged with `--no-ff`. The merge commit holds the other parent's content of the test, which that parent changed. Orchestrator trailers, none. The test is named | 2 | **2 red.** Silent |
| DEC-398: the other side | `test_a_criss_cross_merge_that_changes_only_paths_its_trailers_or_the_caller_may_write_is_silent`: the same, the second branch's last commit an engineer's of a source file | 2 | **2 green.** Hold now and after the fix: a fix that flags the form of the history, not the paths, fails them |
| DEC-398 (no merge base) | `test_a_merge_of_an_unrelated_history_that_adds_an_acceptance_test_is_flagged`: `--allow-unrelated-histories`; the merged history's one commit has no parent, carries a test designer's trailers and adds an acceptance test. Orchestrator trailers, none. The test is named | 2 | **2 red.** Silent |
| DEC-398: the other side | `test_a_merge_of_an_unrelated_history_that_adds_a_path_the_orchestrator_may_write_is_silent`: the same, the one commit an orchestrator's of a file under `docs/` | 2 | **2 green.** Hold now and after the fix |

Held by existing cases, unchanged:

- **The original DP-15 shape** (the second parent is the earlier commit itself):
  `test_a_merge_commit_that_undoes_test_designer_commits_through_an_earlier_parent_is_flagged` (3 cases:
  `orchestrator-trailers`, `engineer-trailers`, `no-trailers`), with its four neighbours in the same file.
- **An ordinary `--no-ff` integration merge** bringing a test designer's commit under `tests/acceptance/**` and an
  engineer's commit inside its ticket's paths: `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent`
  (4 cases: `diverged-branches`, `no-ff-merge-of-a-branch-that-is-ahead`, `merge-commit-without-trailers`,
  `orchestrator-on-another-ticket`) and
  `test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork` (2 cases).
- **A conflict resolved by hand**: to the merged side's content,
  `test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change` (rewritten in the
  tenth batch as `test_a_conflict_in_an_acceptance_test_resolved_to_the_merged_side_s_content_is_flagged`); to content neither
  parent holds, `test_an_orchestrator_s_conflict_resolution_under_acceptance_tests_is_flagged` and
  `test_an_orchestrator_s_conflict_resolution_outside_acceptance_tests_is_silent`.
- **A merged commit without a parent that itself leaves its paths**:
  `test_a_merged_root_commit_that_adds_an_acceptance_test_is_flagged` (3 cases). Fail closed adds the merge commit's
  own change of the same path; the path is named either way.

A criss-cross merge, or a merge of an unrelated history, whose merge commit carries a test designer's trailers is not
tested. When this was written its own change under `tests/acceptance/**` was judged by those trailers, as in the
sixth batch's `test_the_same_merge_commit_with_a_test_designer_s_trailers_is_judged_by_those_trailers`. Since DEC-410
(DP-27) such a change is a finding whatever the trailers; that case is rewritten (tenth batch).

### DEC-398: the helper that reads a merge (`test_w1_50_read_merge_helper.py`, 8 cases)

```python
from gov.guard.containment_merge import read_merge
reading = read_merge(root, commit)   # root: the repository's path (str); commit: a merge commit's id
reading.own       # sorted list of repository-relative paths the merge commit changed itself
reading.brought   # sorted list of paths another parent brought
```

`own` and `brought` are disjoint; both ends of a rename appear as two paths, and a deleted path is a path. When
these cases were written the two lists together were exactly the paths the merge commit changes against its first
parent; DEC-403 widens that, and the test is rewritten (eighth batch). DEC-410 (DP-22) makes `brought` every path
where the merge commit differs from some parent and that is not its own, and the test compares it exactly (tenth
batch). The helper takes no caller, role or
ticket. With the later batches' helper cases these are the only cases that import from `src`. The helper is imported when the test first calls it, after
the history is built and guarded, so its absence fails these 8 cases and not the collection of the others. The
process holds no `GOV_ROLE`, `GOV_TICKET` or `CLAUDE_PROJECT_DIR`, and no hook runs around any command. What the
helper does for a commit that is no merge is not tested.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DEC-398, DEC-394 | `test_read_merge_says_which_paths_are_the_merge_commit_s_own_and_which_another_parent_brought`: `own` and `brought` equal the sorted lists below; reading leaves `HEAD`, the tree and `findings.jsonl` as they were | 8 | **8 red.** `import gov.guard.containment_merge` fails: the module does not exist |

| History | `own` | `brought` |
|---|---|---|
| an ordinary integration merge | none | the test designer's new test, the engineer's source file |
| F1: a merge that undoes commits through a new empty commit | the edited test, the removed test | none |
| a merge that sets a test back to the merged branch's unchanged content | the test | the branch's source file |
| a conflict resolved by hand to content neither parent holds | the conflicted test | the branch's new test |
| an octopus merge | none | the new test of one branch, the source file of the other |
| a criss-cross merge (two merge bases) | the other parent's new test | none |
| a merge of an unrelated history (no merge base) | the other parent's new test | none |
| a merge of a branch that renamed a file | none | the old name, the new name |

### DP-17: a ticket-file commit in a worker's call (`test_w1_50_ticket_file_commit_in_a_worker_s_call.py`, 5 cases)

DEC-394: "in a worker's call, any commit of the move that changes a path under `.tickets/**` is a finding, with or
without trailers." The commit of these cases adds `**` to the calling session's own ticket and changes `README.md`:
without trailers it is judged against the caller, whose paths are then read from the file the commit has just
written. Each test asserts the finding that names the ticket file, and nothing about `README.md`.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-17 | `test_a_commit_of_a_ticket_file_made_in_a_worker_s_call_is_flagged`: the commit without trailers, in an engineer session's call and in an engineer subagent's call inside an orchestrator session | 2 | **2 red.** Silent |
| DP-17; DEC-319 | the same test: the commit with `Role: orchestrator` and a `Task`, in the same two calls | 2 | **2 green.** Another role's trailer in a worker's call is a finding already (DEC-319), and it names the commit's paths. They fail if a fix of DP-17 loses the ticket file from that finding |
| DEC-156, KPI success 4: the other side | `test_a_commit_without_trailers_of_a_ticket_file_made_in_the_orchestrator_s_own_call_is_silent` | 1 | **1 green.** Holds now and after the fix: DP-17 speaks of a worker's call |

Held by existing cases, unchanged: the same commit with `Role: orchestrator` in an orchestrator session's own call is
silent (`test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent`); with the engineer's own
trailers in an engineer's call it is a finding
(`test_an_engineer_s_commit_that_widens_its_own_ticket_in_its_own_call_is_flagged`, DP-16). A commit without trailers
that changes a ticket file and does not widen the caller's paths was a finding in a worker's call before DP-17, as a
path outside the caller's paths; no case is added for it.

## Added after implementation, DEC-403 (eighth batch)

These 43 cases are **tests added after implementation**; reason: "delegated decision, DEC-403". The behaviours came
to the test designer as described behaviours, never as code. Apart from the helper's cases, every case goes through
the same public interface as the rest of the suite and is read from outside; no test reads the check's code. Every
history is a real git history built in the throw-away project with commits, `git merge` and, where a shape needs it,
`git commit-tree`. "Made in the call" is: between the PreToolUse and the PostToolUse hook of one Bash call.

Run when they were written: **34 failed, 9 passed**. Every red case fails on its behaviour assertion, with the
fixture's own guards passed. With the three rewritten cases that fail (below) the suite's run is 37 failed, 251
passed.

**DEC-403, DP-20 (a): the symmetric rule, in the one helper.** `read_merge` reads every parent the way it reads the
first. A path where the merge commit's content differs from any parent's is the merge commit's own change, unless
another parent brought it by the three-way rule (that parent's content differs from the merge base, and the merge
commit has that parent's content). So `own` also holds the paths where the merge drops a parent's change. With
several merge bases, or none, every path that differs from any parent is the merge commit's own change. This widens
"against its first parent" in DEC-394 and DEC-398; the helper stays the one place that reads a merge.

**DEC-403, DP-19 (a): as built.** An octopus merge in which one other parent has several merge bases, or none, with
the first parent fails closed as a whole. An octopus whose other parents cross only each other is read parent by
parent, as built.

**F3.** `read_merge` raises a public, documented error; a `commit` argument that is not a commit id (for example one
that begins with `-`) is refused, never passed to git as an option; the docstring says exactly what `own` and
`brought` hold.

**How the suite reads the rule for one path**, with the parents P1..Pn: for each parent Pi whose content of the path
differs from the merge commit's, the path is the merge commit's own unless some other parent Pj holds the merge
commit's content of it and that content differs from the one merge base of Pi and Pj. The histories are built in
`w1_50_symmetric_support.py`. Each builder names the dropping merge commit's own changes as a literal list;
`own_by_the_words` works the rule out from git's own answers, as a guard for the fixtures, and
`assert_dropping` also checks that, read against its first parent alone, none of the paths a finding is to name is
the merge commit's own. A tree a merge commit made by plumbing is to hold is prepared before the call, as the tree
of a commit on a branch `prepared` that is never an ancestor of `HEAD`.

### DP-20: a dropped change, through the check (`test_w1_50_merge_that_drops_a_parent_s_change.py`, 20 cases)

Every call is an orchestrator session's own call. `HEAD` is the branch tip before the call and `HEAD~2` the commit
before the two changes that are dropped. Each shape has one case for each of:

- **a test designer's tests**: a commit that edits an existing acceptance test and a commit that adds a new one. The
  dropping merge commit carries the orchestrator's trailers unless the table says otherwise; neither they nor the
  caller allow a path under `tests/acceptance/**`;
- **an orchestrator's ticket files**: a commit that narrows `DAEO-zz94`'s allowed paths and a commit that closes
  `DAEO-zz96`. The dropping merge commit carries an engineer's trailers: a change under `.tickets/**` in a commit
  with a worker's `Role` trailer is a finding (DP-16). With the orchestrator's trailers, or none, the form was not
  tested then (package DP-21); DEC-410 makes it a finding, and the tenth batch tests it.

All 20 cases are **red**. Unless the table says otherwise the check is silent today: against its first parent the
dropping merge commit changes nothing, or only paths its other parent brought.

| Shape | Test function | Cases |
|---|---|---|
| B, the parents turned round: a merge commit with the parents `HEAD~2` and `HEAD` in that order and the tree of `HEAD~2`; `main` moved to it | `test_a_merge_commit_with_its_parents_turned_round_is_flagged_for_what_it_drops`: both dropped paths are named. The tests with orchestrator trailers, engineer trailers, none; the ticket files | 4 |
| C: the same, the first parent a new empty commit on top of `HEAD~2` | `test_a_turned_round_merge_commit_whose_first_parent_is_a_new_empty_commit_is_flagged` | 2 |
| D, plain porcelain: `git checkout -b tmp HEAD~2`, an orchestrator's commit of `README.md`, `git merge -s ours main`, `main` fast-forwarded to it | `test_a_branch_cut_before_the_changes_that_takes_main_with_ours_and_is_fast_forwarded_to_is_flagged`: the dropped paths are named, `README.md` is not. The tests with the merge commit as `git merge -s ours main` makes it, without trailers; the ticket files | 2 |
| E: turned round like B, the tree `HEAD`'s with only the first of the two changes set back | `test_a_turned_round_merge_commit_that_sets_back_one_of_two_changes_is_flagged_for_that_one`: the path set back is named; the path that was kept, which the second parent brought, is not | 2 |
| J2, an octopus turned round: the parents `side`, `HEAD`, `HEAD~1` and the tree of `side`, which forked before the changes and has an orchestrator's commit of `README.md` | `test_an_octopus_merge_commit_that_holds_the_tree_of_a_side_forked_before_the_changes_is_flagged`: both dropped paths are named, `README.md` is not | 2 |
| NB2, no merge base: the first parent a new commit without a parent and with an empty tree, the second `HEAD`; the tree is `HEAD`'s without `tests/acceptance/` (the tests) or without the two ticket files | `test_a_merge_commit_on_an_unrelated_first_parent_is_flagged_for_the_paths_it_deletes`: the deleted paths are named. The ticket case is not silent today: the engineer's merge commit is flagged for the ticket files its tree holds, and the two it deletes are not named | 2 |
| N: a ticket branch takes `main` with `git merge -s ours`, then an ordinary `git merge --no-ff` of the branch into `main` | `test_a_branch_that_took_main_with_ours_and_is_then_merged_ordinarily_is_flagged_for_what_it_dropped`: the dropped paths are named, by a finding whose `reason` names the `-s ours` merge commit; the branch's source file is not named. N1, both merges in the call: the tests with orchestrator trailers on the `-s ours` merge and with none, the ticket files. N2, the `-s ours` merge made before the call: the tests, the ticket files | 5 |
| The review's F2: a turned-round merge commit undoes two tests and a second merge commit on top of it (second parent `HEAD`) holds the second test again, both in one call | `test_a_test_that_stays_undone_is_named_when_a_second_merge_commit_restores_the_other`: the test that stays undone is named. Today the finding names only the restored test, the second merge commit's own change against its first parent. The test says nothing of the restored test | 1 |

**Which merge commit the finding is for in shape N.** By the rule's words it is the `-s ours` merge commit, in N1
and in N2. That commit differs from its second parent (`main`) in the dropped paths, and its first parent, whose
content it holds, never changed them: they are its own change. The final merge commit holds its second parent's
content of those paths, and that content differs from the merge base (`main` as it was): they are brought, and the
final merge commit has no own change. In N2 the `-s ours` merge commit was made before the call, but it is not in
`HEAD`'s history until the call's merge: it is a commit of the move, judged like every commit the merge brings, as
the branch's earlier merge is in the seventh batch's merge-back cases. So N2 is pinned, with the same expectation as
N1.

### DP-20: the other side, through the check (`test_w1_50_merge_that_takes_each_side_s_change.py`, 5 cases)

All 5 cases were **green** when written. The first four must stay green: a fix that takes every path where the merge
commit differs from a parent for the merge commit's own fails them. The fifth is rewritten in the tenth batch
(DEC-410, DP-24) as `test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_flagged`; so are the two
cases of "a merge resolved to the merged side's content" in the list below.

| Test function | Cases |
|---|---|
| `test_a_merge_that_takes_each_parent_s_change_of_its_own_path_is_silent`: the branch changed one path and `main` another since the fork, one of the two a test designer's under `tests/acceptance/**`; the merge commit holds both. The test designer's commit on `main`, and on the branch; as `git merge --no-ff` makes it, and with the same tree and the branch for the first parent | 4 |
| `test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_silent`: a test designer made the same change of an acceptance test on both sides; the branch also brings an engineer's commit | 1 |

Shapes the seventh batch and earlier batches hold silent. Each was worked out again by the words of DEC-403; none
gives another answer, and none is changed:

- an ordinary `--no-ff` integration merge: `test_an_integration_merge_of_commits_inside_their_own_paths_is_silent`
  (4 cases), `test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork` (2 cases);
- a merge-back: `test_a_merge_back_of_a_ticket_branch_that_earlier_merged_main_into_itself_is_silent` (2 cases);
- a re-merge: `test_a_second_merge_of_the_same_branch_is_silent`;
- an octopus merge: `test_an_octopus_merge_of_two_branches_with_commits_inside_their_own_paths_is_silent`;
- a merge resolved to the merged side's content:
  `test_a_merge_that_takes_the_merged_side_s_content_of_paths_both_sides_changed_is_silent` and
  `test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change`;
- a criss-cross merge whose first parent got no commit after the crossing:
  `test_a_criss_cross_merge_that_changes_only_paths_its_trailers_or_the_caller_may_write_is_silent` (2 cases).

### DP-20, DP-19 and F3: the helper (`test_w1_50_read_merge_every_parent.py`, 18 cases)

Through `from gov.guard.containment_merge import read_merge`, imported inside the test when the history is built, as
in the seventh batch. In every case `own` and `brought` are sorted lists of distinct paths with no path in both, and
reading leaves `HEAD`, the tree and `findings.jsonl` as they were.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-20 | `test_read_merge_puts_the_paths_a_turned_round_merge_commit_drops_in_own`: shape B; `own` is the two dropped tests, `brought` is empty | 1 | **red**: `own` is empty |
| DP-20 | `test_read_merge_puts_what_an_ours_merge_drops_in_its_own_and_not_in_the_ordinary_merge_s_after_it`: shape N; for the `-s ours` merge commit `own` is the two dropped tests and `brought` holds neither; for the final merge commit `own` is empty and `brought` holds the two tests and the branch's source file | 1 | **red**: `own` of the `-s ours` merge commit is empty |
| DP-20: the other side | `test_read_merge_finds_no_own_change_in_a_merge_that_takes_each_side_s_change`: each side changed its own path; an ordinary merge, and the parents turned round. `own` is empty; `brought` holds the path the other parent brought against the first parent, and no path where no parent differs | 2 | **green** |
| DP-20, several merge bases | `test_read_merge_with_several_merge_bases_puts_every_path_that_differs_from_any_parent_in_own`: a criss-cross history with the parents turned round and the first parent's tree; `own` is the engineer's file and the test designer's test, both of which differ from the second parent only; `brought` is empty | 1 | **red**: `own` is empty |
| DP-20, no merge base | `test_read_merge_with_no_merge_base_puts_every_path_that_differs_from_any_parent_in_own`: shape NB2; `own` is every path the tree holds and every path it deletes; `brought` is empty | 1 | **red**: `own` lacks the three deleted paths |
| DP-19 | `test_read_merge_fails_closed_for_a_whole_octopus_merge_when_one_parent_has_several_merge_bases_or_none`: an octopus of `HEAD`, an ordinary ticket branch with a test designer's new test, and a branch with two merge bases with `HEAD`, or a history with none. `brought` is empty, the ordinary branch's test included; `own` is every path that differs from any of the three parents | 2 | **red**: `brought` is empty already (as built); `own` holds only the paths that differ from the first parent |
| DP-19 | `test_read_merge_reads_an_octopus_whose_other_parents_cross_only_each_other_parent_by_parent`: each branch has one merge base with `HEAD`, the two cross each other. Pinned: the two paths both branches hold are in `brought`; `own` holds nothing but, at most, the file one branch changed after the crossing | 1 | **green** |
| F3 | `test_read_merge_raises_a_public_error_for_an_unknown_commit_id`: forty hex digits that name no object; forty zeros | 2 | **red**: raises `gov.guard.containment._GitError` |
| F3 | `test_read_merge_raises_a_public_error_for_a_path_that_is_no_repository`: an existing directory outside every repository | 1 | **red**: raises `gov.guard.containment._NotARepo` |
| F3 | `test_the_error_read_merge_raises_is_documented` | 1 | **red**: there is no public error yet |
| F3 | `test_the_docstring_of_read_merge_speaks_of_own_and_brought` | 1 | **green** |
| F3 | `test_read_merge_refuses_a_commit_argument_that_is_no_commit_id`: `--all`, `-1`, `--output=<file>`, the empty string. The public error, the same as for an unknown commit id; no reading; no file written; the repository as it was | 4 | **red**: `--all` returns a reading of `HEAD`; the other three raise `_GitError` with git's own message, after git was given the argument |

**What the cases require of the error**, and no more: the exception `read_merge` raises is an instance of a class
that `gov.guard.containment_merge` holds under a name without a leading underscore, and that class is neither
`Exception` nor `BaseException`. Its name is the engineer's. "Documented": one of those names stands in the
docstring of `read_merge` or of the module, or the class has a docstring of its own. "Refused with that public
error": the error for a refused argument and the error for an unknown commit id share at least one such class.

**Not pinned:** whether a branch name or an abbreviated id is accepted for `commit`; what the helper does for a
commit that is no merge; for an octopus whose other parents cross only each other, whether the file one of them
changed after the crossing is in `own` or in `brought` (DEC-410, DP-25: read as built, "that pair brings nothing
against each other"). What `brought` holds was not pinned when these cases were written (package DP-22); DEC-410
decides it, and four of these cases compare it exactly since the tenth batch.

### Existing cases rewritten after implementation (reason: delegated decision, DEC-403)

| Test | Change | Run when rewritten |
|---|---|---|
| `test_read_merge_says_which_paths_are_the_merge_commit_s_own_and_which_another_parent_brought` (`test_w1_50_read_merge_helper.py`, 8 cases) | It pinned "`own` and `brought` together are exactly the paths changed against the first parent". `own` stays the literal list for seven histories; for the merge of an unrelated history it is now every path the merge commit's tree holds (no merge base: every path `main` holds differs from the other parent). `brought` must hold at least the listed paths, be sorted, hold no path of `own` and no path where no parent differs; it is no longer compared for equality (package DP-22) | 7 green; **1 red** (`a-merge-of-an-unrelated-history`: `own` is only the new test) |
| `test_a_merge_of_an_unrelated_history_that_adds_a_path_the_orchestrator_may_write_is_silent` (`test_w1_50_merge_read_by_the_merge_base.py`, 2 cases), now `test_a_merge_of_an_unrelated_history_is_flagged_for_the_acceptance_tests_its_first_parent_holds` | It expected silence. By DEC-403's words the merge commit, which keeps everything `main` holds, differs from its other parent in all of it, and with no merge base all of it is the merge commit's own: the acceptance test `main` holds is named. The file the merge adds is not named. The history is unchanged. See package DP-23 | **2 red**: silent |

No other existing case gives another answer under DEC-403. The fixture guard `assert_shape` of the seventh batch
still describes each history by its first parent; it reads git, not the check, and is unchanged.

## Added after implementation, review of the DEC-403 rule (ninth batch)

These 8 cases are **tests added after implementation**; reason: "review finding, DEC-403". The behaviours came to the
test designer as described behaviours, never as code; no test reads the check's or the helper's code. They are in
`test_w1_50_review_of_the_symmetric_rule.py`; the histories are built in `w1_50_symmetric_support.py`. Every history
is a real git history built in the throw-away project with commits, `git merge` and `git commit-tree`. "Made in the
call" is: between the PreToolUse and the PostToolUse hook of one Bash call.

Run when they were written: **5 failed, 3 passed**; the suite's run is 5 failed, 291 passed. Every red case fails on
its behaviour (the hook's time limit, the helper's bound, or the assertion that the argument is refused), with the
history built and the fixture's own guards passed. No existing case is changed.

### 1. A merge commit with very many parents is judged, never passed over in silence (5 cases)

DEC-403: a merge that keeps one parent's content and drops what another parent changed is judged. The history: `main`
got a test designer's change of an existing acceptance test. In an orchestrator session's own call, 149 side commits
are made with `git commit-tree` on top of the commit before that change, each with that commit's tree and the
orchestrator's trailers (each changes nothing); a merge commit with the parents `HEAD` and the 149 side commits holds
that same tree; `main` is moved forward to it. By the rule's words the undone test is the merge commit's own change
and its only one: it differs from the first parent, and every other parent holds the merge base's content of it. The
fixture's guard (`assert_very_many_parents`) shows this from git's own answers in a handful of git calls; building
the history takes about a second.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| Through the check | `test_a_move_to_a_merge_commit_with_very_many_parents_that_undoes_a_test_is_a_finding_within_the_hook_s_limit`: the post-command hook ends by itself within the harness's limit (`HOOK_TIMEOUT_S` of the W1-03 support module, 30 s; not raised here) and the call adds a finding. Either form is accepted: one that names the undone test, or one for the move as a whole, as the check records a move it cannot read. The merge commit with the orchestrator's trailers, and with none (the caller decides; the caller is the orchestrator) | 2 | **red**: the hook does not end within 30 s and is stopped; no finding was added. Each case takes about the limit |
| Through the helper | `test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought`: `read_merge` answers within 10 s with a reading whose `own` holds the undone test and whose `brought` does not, or with its public error; never a reading with an empty `own`. Reading leaves `HEAD`, the tree and `findings.jsonl` as they were | 1 | **red**: no answer after 10 s; the call is interrupted |
| The other side, through the check | `test_an_ordinary_octopus_merge_of_eight_branches_with_commits_inside_their_own_paths_is_silent`: one `git merge` of eight branches in the orchestrator's own call (nine parents). Each branch has one commit inside its own trailers' paths; one is a test designer's new acceptance test. Silent, and nothing is moved | 1 | **green** |
| The other side, through the helper | `test_read_merge_finds_no_own_change_in_an_ordinary_octopus_merge_of_eight_branches`: `own` is empty | 1 | **green** |

The two green cases must stay green: a fix that refuses or flags every merge commit with more than two or three
parents fails them.

**The helper's bound of 10 s** is a third of the harness's hook limit. It is safe on a loaded machine because the
work asked for is small: the merge commit has 150 parents, and one git process for each of them, or a refusal before
any, is a fraction of a second on an idle machine (the whole nine-parent case, history and reading, takes half a
second). The bound leaves room for that to be many times slower, and leaves the hook two thirds of its limit for the
rest of its work. The bound is kept in the test's own process with an interval timer that interrupts the call; the
elapsed time is checked as well.

**Not pinned:** a number of parents at which anything changes; a number of git processes; how the check or the helper
keeps the time; which form the finding has, its `action`, and whether the check leaves the move in place; what
`read_merge` puts in `brought` for either merge commit.

### 2. A `commit` argument that has a commit id's form and is not the id of a commit (3 cases)

DEC-403: the helper "refuses a `commit` argument that is not a commit id". The repository holds an ordinary
integration merge on `main`, an annotated tag that points at the merge commit, and a branch at the merge commit whose
name is 64 lower-case hexadecimal digits; it is an ordinary SHA-1 repository, so no object id has 64 digits. The
error is found as in `test_w1_50_read_merge_every_parent.py`: a class `gov.guard.containment_merge` holds under a
public name, shared with the error for an unknown commit id.

| Test function | Cases | Run when written |
|---|---|---|
| `test_read_merge_refuses_a_commit_argument_with_a_commit_id_s_form_that_is_not_the_id_of_a_commit`: the object id of the annotated tag; the 64 hexadecimal digits that are the branch's name. The public error, no reading, the repository as it was | 2 | **red**: each returns the reading of the merge commit the argument resolves to |
| `test_read_merge_still_reads_the_merge_commit_s_own_full_id_beside_a_tag_and_a_hex_named_branch`: the other side. `own` is empty and `brought` holds the two paths the merged branch brought | 1 | **green** |

**Not pinned**, as before: whether a branch name of another form or an abbreviated id is accepted for `commit`, and
what the helper does for the full id of a commit that is no merge.

## Added after implementation, DEC-410 (tenth batch)

DEC-410 (orchestrator, delegated under DEC-220, stricter-only) decides DP-21 to DP-28. These 42 cases are **tests
added after implementation**; reason: "delegated decision, DEC-410". No test reads the check's or the helper's code.
Every history is a real git history built in the throw-away project; the builders are in
`w1_50_own_change_support.py` (new) and `w1_50_symmetric_support.py`. "Own" is
`gov.guard.containment_merge.read_merge(...).own`. Each builder's history is checked from git's own answers before
the behaviour is asserted.

Run when they were written: **29 failed, 13 passed**. With the rewritten cases the suite's run is **43 failed, 295
passed** (338 cases). Every red case fails on its behaviour assertion, with the history built and the fixture's own
guards passed.

### DP-21: a merge commit's own change of a ticket file (`test_w1_50_merge_commit_own_change_of_a_ticket_file.py`, 12 cases)

Every call is an orchestrator session's own call; the merge commit carries `Role: orchestrator` with a `Task`
trailer, or no trailers. The finding names the ticket file.

| Test function | Cases | Run when written |
|---|---|---|
| `test_a_hand_edit_of_a_ticket_file_in_an_orchestrator_s_merge_commit_is_flagged`: an ordinary integration merge whose merge commit also appends a line to a ticket file neither side changed. The ticket file is named, the paths the branch brought are not. Orchestrator trailers; none | 2 | **red**: silent |
| `test_a_conflict_resolution_of_a_ticket_file_in_an_orchestrator_s_merge_commit_is_flagged`: an orchestrator's commit on each side changed the ticket file; resolved to content neither parent holds. Orchestrator trailers; none | 2 | **red**: silent |
| `test_an_orchestrator_s_merge_commit_with_its_parents_turned_round_that_drops_ticket_file_changes_is_flagged`: shape B of DEC-403; a narrowing and a close are dropped, the ticket is in progress again. Both ticket files are named. Orchestrator trailers; none | 2 | **red**: silent |
| `test_an_orchestrator_s_ours_merge_that_sets_a_ticket_s_status_back_is_flagged`: shape D, porcelain only (`git merge -s ours main` on a branch cut before the two commits, `main` fast-forwarded). Both ticket files are named, `README.md` is not. Orchestrator trailers; none | 2 | **red**: silent |
| `test_an_orchestrator_s_merge_commit_that_drops_one_of_two_ticket_file_changes_is_flagged_for_that_one`: shape E; the file set back is named, the file kept as the second parent has it is not | 1 | **red**: silent |
| The other side: `test_an_ordinary_merge_that_brings_an_orchestrator_s_ticket_file_changes_from_one_side_is_silent`: an orchestrator's two ticket-file commits on one side only (the branch, with orchestrator trailers on the merge and with none; `main`), brought by an ordinary `git merge --no-ff` | 3 | **green**; must stay green: a fix that flags every merge commit that differs from a parent in a ticket file fails them |

The orchestrator's ordinary (non-merge) commit of a ticket file in its own call stays silent:
`test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent` and
`test_a_commit_without_trailers_of_a_ticket_file_made_in_the_orchestrator_s_own_call_is_silent`, unchanged.
**Not pinned:** a ticket file both sides changed that the merge commit holds as one side has it; DEC-410 names
`tests/acceptance/**` only for that rule (DP-24).

### DP-27: a merge commit's own change of an acceptance test (`test_w1_50_merge_commit_own_change_of_an_acceptance_test.py`, 9 cases)

| Caller | Test function | Cases | Run when written |
|---|---|---|---|
| Orchestrator's own call, test designer's trailers on the merge commit | `test_a_hand_edit_of_an_acceptance_test_in_a_merge_commit_with_a_test_designer_s_trailers_is_flagged` | 1 | **red**: silent |
| The same | `test_a_conflict_resolution_of_an_acceptance_test_in_a_merge_commit_with_a_test_designer_s_trailers_is_flagged`: resolved to content neither parent holds | 1 | **red**: silent |
| The same | `test_a_turned_round_merge_commit_with_a_test_designer_s_trailers_that_drops_tests_is_flagged`: shape B; both dropped tests are named | 1 | **red**: silent |
| The same | `test_an_ours_merge_with_a_test_designer_s_trailers_that_drops_tests_is_flagged`: shape D; both dropped tests are named, `README.md` is not | 1 | **red**: silent |
| A test designer session's own call | `test_a_hand_edit_of_an_acceptance_test_in_a_merge_commit_made_in_a_test_designer_s_call_is_flagged`: test designer's trailers; none | 2 | **red**: the call is flagged as a move ("HEAD moved (not a forward move, flagged)"); the finding does not name the acceptance test |
| The same | `test_a_turned_round_merge_commit_made_in_a_test_designer_s_call_that_drops_tests_is_flagged`: shape B; test designer's trailers; none | 2 | **red**: flagged as a move; the dropped tests are not named |
| The other side, orchestrator's own call | `test_an_ordinary_merge_whose_merge_commit_carries_a_test_designer_s_trailers_and_changes_nothing_is_silent` | 1 | **green**; must stay green: a fix that flags every merge commit with a test designer's trailers fails it |

**The four cases in a test designer's call** are not silent today: a merge in a worker's call is flagged as a move
(DEC-266). They are red because the finding does not name the acceptance test. The suite reads "is a finding" as
everywhere else: the record's `paths` and the report hold the path ("A finding names the commit's paths"). They
assert nothing about the other commits of the move.

With the orchestrator's trailers, or none, in an orchestrator's own call the change is a finding since DEC-269;
existing cases hold that, unchanged and green: `test_a_merge_commit_s_own_change_outside_its_trailers_paths_is_flagged`
(`orchestrator-trailers-acceptance-test`, `no-trailers-acceptance-test`),
`test_an_orchestrator_s_conflict_resolution_under_acceptance_tests_is_flagged`, and the dropped tests of
`test_w1_50_merge_that_drops_a_parent_s_change.py`. A test designer's ordinary commit under `tests/acceptance/**`
stays silent in its own call, in an orchestrator's call, and brought by an orchestrator's ordinary merge
(`test_a_test_designer_s_commit_during_the_lead_s_call_is_silent`,
`test_commits_inside_the_paths_of_their_own_trailers_are_silent`,
`test_an_integration_merge_of_commits_inside_their_own_paths_is_silent`), unchanged.

### DP-24 with DP-26: an acceptance test both sides changed (`test_w1_50_acceptance_test_changed_on_both_sides.py`, 17 cases)

A test designer's commit on each side changed the same acceptance test against the one merge base; the branch also
brings another path. The merge is made in the orchestrator's own call, as `git merge --no-ff` makes it and with the
parents turned round.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| DP-24, through the check | `test_a_merge_that_takes_one_side_s_content_of_a_test_both_sides_changed_is_flagged`: the merge commit holds the first parent's content of the test whole, or the second parent's; either parent order. The test is named | 4 | **red**: silent, all four |
| DP-24, through the helper | `test_read_merge_puts_a_test_both_sides_changed_in_own_whichever_side_s_content_the_merge_commit_holds`: the same four histories; the test is in `own` and not in `brought` | 4 | **red**: `own` is empty; where the merge commit holds the second parent's content the test is in `brought` |
| DP-24, test designer's trailers on the merge commit (with DP-27) | `test_the_same_merge_with_a_test_designer_s_trailers_on_the_merge_commit_is_flagged`: second parent's content, an ordinary merge | 1 | **red**: silent |
| DP-26, through the check | `test_a_clean_combination_of_two_sides_edits_of_one_test_is_flagged`: the two sides changed different lines of a twenty-line test; git combines them without a conflict | 1 | **green**: flagged as built |
| DP-26, through the helper | `test_read_merge_puts_a_clean_combination_of_two_sides_edits_of_one_test_in_own` | 1 | **green** |
| DP-24, both sides made the same change, through the helper | `test_read_merge_puts_a_test_both_sides_changed_in_the_same_way_in_own`: `own` is the test, `brought` is the branch's source file. Through the check it is the rewritten `test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_flagged` | 1 | **red**: `own` is empty |
| The other side, through the check | `test_a_merge_that_takes_one_side_s_content_of_a_source_file_both_sides_changed_stays_silent`: the same shapes for an engineer's source file, first and second parent's content | 2 | **green**; must stay green |
| The other side, through the helper | `test_read_merge_reads_a_source_file_both_sides_changed_as_before`: `own` is empty; the second parent's changed content is in `brought` | 2 | **green** |
| The other side, through the helper | `test_read_merge_finds_no_own_change_where_each_side_changed_another_acceptance_test`: `own` is empty | 1 | **green** |

**Both sides made the same change** is read by DP-24's words: more than one parent changed the path against the
merge base, so it is the merge commit's own, although the merge commit differs from no parent in it. `own` then holds
a path outside "the paths where the merge commit differs from a parent"; `brought` stays inside them (DP-22).
With several merge bases, or none, nothing changes: every differing path is the merge commit's own already (DP-23).
DEC-421 extends DP-24 to `.tickets/**`; tested in
`test_w1_50_ticket_file_changed_on_both_sides.py`.

### DP-22: what `brought` holds (`test_w1_50_read_merge_brought.py`, 4 cases)

Through the helper only. `brought` is sorted, holds no path twice and no path of `own`, and is exactly the paths
where the merge commit differs from some parent that are not in `own`.

| Test function | Cases | Run when written |
|---|---|---|
| `test_read_merge_puts_what_either_parent_brought_beside_a_hand_edit_in_brought`: an integration merge with a hand edit of `README.md`; `own` is `README.md`, `brought` the branch's two paths and the path `main` changed; together exactly the paths that differ from a parent | 1 | **red**: `brought` lacks the path the first parent brought |
| `test_read_merge_puts_what_the_first_parent_brought_beside_a_dropped_change_in_brought`: shape D; `own` is the two dropped tests, `brought` is `README.md` | 1 | **red**: `brought` is empty |
| `test_read_merge_puts_the_change_a_turned_round_merge_commit_keeps_in_brought`: shape E; `own` is the test set back, `brought` the test kept | 1 | **green** |
| `test_read_merge_brings_nothing_in_a_criss_cross_merge_although_each_parent_holds_a_change_of_its_own`: two merge bases, each parent with a commit after the crossing; `own` is both paths, `brought` is empty | 1 | **green** |

The ordinary two-parent merge where each side changed its own path (both parent orders), the ordinary octopus
merges of two and of eight branches, and the other fail-closed shapes are existing helper cases, rewritten below to
compare `brought` exactly.

### Existing cases rewritten after implementation (reason: delegated decision, DEC-410)

Each keeps its history; the expectation and, where the name said the opposite, the name change.

| Test, as it was | File | It pinned | It pins now | Run when rewritten |
|---|---|---|---|---|
| `test_the_same_merge_commit_with_a_test_designer_s_trailers_is_judged_by_those_trailers`, now `test_the_same_merge_commit_with_a_test_designer_s_trailers_is_flagged_all_the_same` | `test_w1_50_merge_that_undoes_earlier_commits.py` | Silent: a merge commit with a test designer's trailers that undoes two acceptance tests | Flagged; both tests are named (DP-27) | **1 red**: silent |
| `test_a_test_designer_s_merge_commit_that_also_undoes_a_source_file_is_flagged_for_that_file`, now `..._is_flagged_for_every_path_it_undoes` | the same | The source file is named and the two acceptance tests are not recorded | All three paths are named (DP-27) | **1 red**: the tests are not named |
| `test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change`, now `test_a_conflict_in_an_acceptance_test_resolved_to_the_merged_side_s_content_is_flagged` | `test_w1_50_merge_commit_own_changes.py` | Silent: a conflict in an acceptance test resolved to the merged side's content | Flagged; the test is named (DP-24) | **1 red**: silent |
| `test_a_merge_that_takes_the_merged_side_s_content_of_paths_both_sides_changed_is_silent`, now `..._is_flagged_for_the_test_only` | `test_w1_50_merge_read_by_the_merge_base.py` | Silent: `-X theirs` on an acceptance test and a source file both sides changed | The acceptance test is named; the source file is not recorded (DP-24) | **1 red**: silent |
| `test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_silent`, now `..._is_flagged` | `test_w1_50_merge_that_takes_each_side_s_change.py` | Silent: both sides made the same change of an acceptance test | The test is named; the branch's source file is not recorded (DP-24, by its words) | **1 red**: silent |
| `test_read_merge_says_which_paths_are_the_merge_commit_s_own_and_which_another_parent_brought` (8 cases) | `test_w1_50_read_merge_helper.py` | `brought` sorted, holding at least the builder's paths, nothing of `own` | `brought` is exactly the differing paths that are not in `own` (DP-22); empty for the criss-cross merge and the unrelated history | **3 red** (`an-ordinary-integration-merge`, `an-octopus-merge`, `a-merge-of-a-branch-that-renamed-a-file`: `brought` lacks the path the first parent brought); 5 green |
| `test_read_merge_finds_no_own_change_in_a_merge_that_takes_each_side_s_change` (2 cases) | `test_w1_50_read_merge_every_parent.py` | `brought` holds the path brought against the first parent | `brought` is both paths, in either parent order (DP-22) | **2 red**: `brought` lacks the first parent's path |
| `test_read_merge_puts_what_an_ours_merge_drops_in_its_own_and_not_in_the_ordinary_merge_s_after_it` | the same | `brought` of the `-s ours` merge holds no dropped path; of the final merge lacks none of three | `brought` of the `-s ours` merge is the branch's source file; of the final merge exactly the three paths (DP-22) | **1 red**: `brought` of the `-s ours` merge is empty |
| `test_read_merge_reads_an_octopus_whose_other_parents_cross_only_each_other_parent_by_parent` | the same | `brought` holds the two paths both branches hold | `brought` is exactly the differing paths that are not in `own` (DP-22); `own` as before (DP-25 as built) | **1 red**: `brought` lacks the path `main` changed |
| `test_read_merge_finds_no_own_change_in_an_ordinary_octopus_merge_of_eight_branches` | `test_w1_50_review_of_the_symmetric_rule.py` | `own` is empty | Also: `brought` is every path that differs from one of the nine parents (DP-22) | **1 red**: `brought` lacks the path `main` changed |
| `test_read_merge_still_reads_the_merge_commit_s_own_full_id_beside_a_tag_and_a_hex_named_branch` | the same | `brought` holds the branch's two paths | `brought` is exactly the three differing paths (DP-22) | **1 red**: `brought` lacks the path `main` changed |

Of these 20 cases 14 are red. The sections of the earlier batches above name the first five by their old names and
old expectations; they are the record of those batches, and this table is what holds now. Comments and docstrings that called DP-21 or DP-22 open are brought up to date in
`w1_50_symmetric_support.py` and `test_w1_50_merge_that_drops_a_parent_s_change.py`; no case of those two files
changes. The fixture guards `assert_shape` and `assert_taking` still describe a history by the three-way rule
without DP-24; they read git, not the check, and are unchanged.

**Left as it stands:** `test_a_close_made_by_a_merge_commit_is_no_close_commit` (`test_w1_50_close_commit_edges.py`)
makes a merge commit with the orchestrator's trailers that closes a ticket by hand. By DP-21 that ticket file is now
a finding too. The case asserts nothing about it either way, so it does not pin the opposite. The cases of DP-23,
DP-25, DP-26 and DP-28 (as built) stand unchanged.

## Added after implementation, review of DEC-410 (eleventh batch)

These 4 cases are **tests added after implementation**; reason: "review finding, DEC-410". The behaviour came to the
test designer as a described behaviour, never as code; no test reads the check's or the helper's code. They are in
`test_w1_50_move_of_very_many_merge_commits.py`; the histories are built in `w1_50_many_merges_support.py` (new).
Every history is a real git history built in the throw-away project with commits, `git merge` and `git commit-tree`.
"Made in the call" is: between the PreToolUse and the PostToolUse hook of one Bash call. They are the twin of the
ninth batch's cases about one merge commit with very many parents.

Run when they were written: **2 failed, 2 passed**; the suite's run is 2 failed, 340 passed (342 cases). Both red
cases fail on the behaviour (the hook's time limit), with the history built and the fixture's own guard passed. No
existing case is changed.

### A move of very many large merge commits is judged, never passed over in silence (4 cases)

DEC-410 (DP-28): the helper refuses a merge commit with more than 24 distinct parents, so one merge commit cannot
stop the hook. Nothing bounds the move as a whole. The history: before the call `main` gets 23 empty commits (the
fork points) and then a test designer's change of an existing acceptance test. In an orchestrator session's own call
a chain of 95 merge commits is made with `git commit-tree` and `main` is moved forward to its tip. Each merge commit
has 24 parents: the merge commit before it (the first: `HEAD`) and 23 new side commits, one on each of the 23 fork
points, each with the orchestrator's trailers and the tree from before the test designer's change (each changes
nothing). The merge commits before the dropping one hold `HEAD`'s tree, so where they differ from a side commit their
first parent brought it. The dropping merge commit and those after it hold the tree from before the change: by the
words of DEC-403 the undone test is the dropping merge commit's own change and its only one, and the later merge
commits differ from no parent. The fixture's guard (`assert_chain`) shows this from git's own answers in a handful of
git calls; building the 2,280 commits takes about three seconds.

| Holds | Test function | Cases | Run when written |
|---|---|---|---|
| Through the check | `test_a_move_of_very_many_merge_commits_with_24_parents_that_undoes_a_test_is_a_finding_within_the_hook_s_limit`: the post-command hook ends by itself within the harness's limit (`HOOK_TIMEOUT_S` of the W1-03 support module, 30 s; not raised here) and the call adds a finding. Either form is accepted: one that names the undone test, or one for the move as a whole, as the check records a move it cannot read. `orchestrator-trailers-dropped-near-the-newest`: the orchestrator's trailers on the merge commits, the dropping one is number 93 of 95 counted from the oldest. `no-trailers-dropped-near-the-oldest`: no trailers (the caller decides; the caller is the orchestrator), the dropping one is number 3 | 2 | **red**: the hook does not end within 30 s and is stopped; no finding was added. Each case takes about the limit |
| The other side | `test_an_ordinary_move_of_sixty_two_parent_merges_of_commits_inside_their_own_paths_is_silent`: 60 `git merge --no-ff` in one orchestrator call, one branch each; every branch has one commit that adds a new file inside its own trailers' paths (20 are a test designer's new acceptance tests, each another file; 20 an engineer's source files; 20 documents of the docs ticket). Silent, the hook ends in time, nothing is moved | 1 | **green** |
| The other side | `test_an_ordinary_move_of_three_octopus_merges_of_eight_branches_each_is_silent`: three `git merge` of eight branches each in one orchestrator call (three merge commits with nine parents), 24 branches of the same kind. Silent | 1 | **green** |

The two green cases must stay green: a fix that flags a move for the number of its merge commits, or of its commits,
fails them. Their branches are made by plumbing (a blob, a tree from a temporary index, `git commit-tree`); the
merges are `git merge`'s own. Their guard (`assert_ordinary_merges`) shows that every merge commit adds, against its
first parent, exactly its branches' paths, and that no path is changed on more than one side.

**The order in which the check reads a move** is not known to the tests. The dropping merge commit is near the
newest end of the chain in one red case and near the oldest in the other, so in either reading order one case has it
early and one late.

**95 merge commits.** The number is the review's. When these cases were written the hook took 3.1 s for a chain of
5 such merge commits, 6.3 s for 10 and 13.0 s for 20 on this machine (about 0.65 s for each merge commit), so 95 is
about twice the limit. On a machine where a merge commit of this kind is read in less than 0.3 s the red cases need
a longer chain to be red; `VERY_MANY_MERGES` of the support module is the one place to raise it. Once the behaviour
is built the number does not matter.

**Not pinned:** a number of merge commits, of commits or of git processes at which anything changes; how the work is
bounded or the time is kept; which form the finding has, its `action`, and whether the check leaves the move in
place; anything `read_merge` returns for a merge commit of the chain (each has 24 parents and is within DP-28).

## Added after implementation, DEC-421 (twelfth batch)

These 6 cases are **tests added after implementation**; reason: "owner decision, DEC-421". DEC-421 extends the
both-sides rule of DEC-410 DP-24 to `.tickets/**`: a ticket file that more than one parent changed against the merge
base is the merge commit's own change, whichever side's content it holds. The tests are in
`test_w1_50_ticket_file_changed_on_both_sides.py`; the builders are those of `w1_50_own_change_support.py`.

| Holds | Test function | Cases | Expected red reason |
|---|---|---|---|
| DEC-421, through the check | `test_a_merge_that_takes_one_side_s_content_of_a_ticket_file_both_sides_changed_is_flagged`: first or second parent's content | 2 | **red**: `read_merge` applies the both-sides rule only to `tests/acceptance/`; a ticket file both sides changed is in `brought` (second parent's content) or absent from both (first parent's) |
| DEC-421, through the helper | `test_read_merge_puts_a_ticket_file_both_sides_changed_in_own`: the same two histories; the ticket file is in `own` and not in `brought` | 2 | **red**: `own` lacks the ticket file |
| DEC-421, identical change, through the helper | `test_read_merge_puts_a_ticket_file_both_sides_changed_in_the_same_way_in_own`: `own` is the ticket file | 1 | **red**: `own` is empty |
| The other side | `test_a_merge_where_each_side_changed_a_different_ticket_file_is_silent`: each side changed a different ticket file; `own` is empty, the merge is silent | 1 | **green**: must stay green; a fix that flags every merge commit that differs from a parent in a ticket file fails it |

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
  call, a finding; in the history before the call, none; and, by DEC-390 (DP-11), new to `HEAD` in the call although
  made before it, a finding. It does not rest on reading `owner` as DEC-268's "unknown role".
- **A finding names the commit's paths.** DEC-268 says "every path it changes is a finding". DEC-318 and DEC-319 say
  "is a finding"; the suite reads that the same way: the record's `paths` and the report hold the paths the commit
  changes.
- **The merge commit's own trailers** do not decide whether the commits it brings pass. They decide only the paths
  the merge commit itself changes beyond what its parents hold (DEC-269), and since DEC-410 not even those under
  `tests/acceptance/**` and `.tickets/**`: a merge commit's own change there is a finding whatever its trailers
  (DP-27, DP-21). A conflict resolved to one side's content is not such a change, except under `tests/acceptance/**`,
  where a path more than one parent changed against the merge base is the merge commit's own whichever side's
  content it holds (DEC-410, DP-24). Which paths are the merge commit's own is read by the three-way rule (DEC-394 DP-18, as
  amended by DEC-398; it replaces DEC-390's DP-15 rule): a path is brought by another parent only when the merge
  commit holds that parent's content of it and that content differs from the merge base of the first parent and that
  parent; with several merge bases, or none, nothing is brought. "Content" is the file's content with its mode, and
  a path a tree does not hold is content too. By DEC-403 the merge commit is read against every parent in this way,
  not against the first alone: a path where it differs from any parent is its own change unless another parent
  brought it, and with several merge bases, or none, every path that differs from any parent is its own (eighth
  batch).
- **A commit a merge brings and the merge commit's own change are two judgements.** A commit new in the move is
  judged by its own trailers whatever the merge commit holds. In the fail-closed cases the other parent's test
  designer commit passes, and the merge commit's change of the same path is a finding of its own.
- **Ticket files (DEC-390, DP-16; DEC-394, DP-17).** A change under `.tickets/**` in a commit with a worker's `Role`
  trailer is a finding, whatever the ticket's paths say and whoever the caller is. A worker's role is every role
  that is not the orchestrator. In a worker's call every commit of the move that changes a path under `.tickets/**`
  is a finding, with or without trailers. The orchestrator's own ordinary commits of ticket files, in its own call,
  pass (DEC-156, DEC-359); a merge commit's own change of a ticket file does not (DEC-410, DP-21).
- **The helper (DEC-398).** `gov.guard.containment_merge.read_merge(root, commit)` is a public name; `own` and
  `brought` are sorted lists, and `brought` is every path where the merge commit differs from some parent and that
  is not in `own` (DEC-410, DP-22). The suite does not say what it does for a commit that is no merge. By DEC-403 it
  raises a public error for a commit id or a repository it cannot read and for a `commit` argument that is no commit
  id; the error's name is the engineer's.
- **Repository-local files.** The check reads the real objects: the local git configuration, `refs/replace/` and
  `.git/info/grafts` change nothing of what a commit is (fifth and sixth batch).
- **Callers (DEC-319).** A commit is judged by its own trailers only in an orchestrator session's own call. In a
  worker's call a commit with the worker's own role, or without trailers, is judged against the caller, and a commit
  with another role's `Role` trailer is a finding.
- **The finding record (DEC-270).** "Named in `reason`" is: `reason` holds the commit's id, in full or abbreviated to
  at least seven characters, and the values of its `Role` and `Task` trailers. One finding per commit and one
  finding for several commits both pass.
- **Ticket state (DEC-318).** A ticket's state is its file's `status` as committed and in the working tree, which
  agree in every fixture of the first three batches. Where a closed ticket is reopened only in the working tree, it
  stays closed (fourth batch); in every other disagreement both must allow (DEC-390, DP-14; sixth batch). "Never started" is `status: open` on a ticket whose file never held another status. The
  DEC-318 cases judge commits with a worker's `Role` trailer; the orchestrator's are DEC-359's. The move that brings
  a close commit is silent, the close commit included (DEC-359).
- **Callers and a closed ticket.** The DEC-318, DEC-358 and DEC-359 cases are all an orchestrator session's own
  call: only there is a commit judged by its own trailers (DEC-319).

## Decision packages

All twenty-eight packages are decided: the ten of the first two batches, DP-11 to DP-16 by DEC-390 (orchestrator,
delegated under DEC-220, stricter-only), DP-17 and DP-18 by DEC-394 (the same), which also replaces DEC-390's DP-15
rule, DP-19 and DP-20 by DEC-403 (delegated), which widens "against its first parent" in DEC-394 and DEC-398, and
DP-21 to DP-28 by DEC-410 (delegated, stricter-only), which amends DEC-403. The owner's DEC-398 amends DEC-394, and
DEC-401 keeps DP-11 and DP-12 as built and accepts DEC-394.

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
| DP-11 | A `Role: owner` commit that existed before the call and arrives in the call's move by a merge or a fast-forward (as `0f8b0d29` did) | DEC-390, as built until the owner says otherwise: a finding, and a record of a permitted action (DEC-254). Tests: `test_w1_50_owner_commit_that_arrives.py` |
| DP-12 | The revert commits and the record commit of a permitted `gov pause --rollback` in an orchestrator's call | DEC-390, as built until the owner says otherwise: judged like any other commit; where they are findings, the findings are records. Tests: `test_w1_50_rollback_commits.py` |
| DP-13 | Edges of the close commit: a ticket file whose first version is already `closed`; the close commit itself with a worker's trailers; a close made by a merge commit | DEC-390: the first version is no close commit; the close commit is not "before" itself; a close made by a merge commit does not count. Tests: `test_w1_50_close_commit_edges.py` |
| DP-14 | Which version of a ticket's file gives its state and `allowed_paths` when `HEAD` and the working tree differ | DEC-390: both are read, and both must allow. Tests: `test_w1_50_ticket_file_at_head_and_in_the_tree.py`, with the fourth batch's `test_w1_50_uncommitted_ticket_state.py` |
| DP-15 | A merge commit with a parent that is not new in the move, whose tree holds for every path content one of its parents holds | DEC-390: every path it changes against its first parent is judged by the merge commit's own trailers, or against the caller without them; an ordinary integration merge is read as before. **Replaced by DEC-394 (DP-18) as amended by DEC-398**: the review showed the rule flags an ordinary merge-back (F2) and is evaded by one empty commit (F1). The tests of `test_w1_50_merge_that_undoes_earlier_commits.py` hold under both rules and are unchanged |
| DP-16 | A commit with a worker's `Role` trailer that changes a ticket file (review finding) | DEC-390: a finding. Tests: `test_w1_50_worker_commit_of_a_ticket_file.py` |
| DP-17 | A commit without a worker's `Role` trailer that changes a ticket file in a worker's call | DEC-394: in a worker's call, any commit of the move that changes a path under `.tickets/**` is a finding, with or without trailers. Tests: `test_w1_50_ticket_file_commit_in_a_worker_s_call.py` |
| DP-18 | Which paths of a merge commit are its own change, now that "a parent not new in the move" is shown wrong | DEC-394, amended by DEC-398 (owner), accepted by DEC-401 (owner): brought by another parent only when the merge commit holds that parent's content and it differs from the merge base of the first parent and that parent; otherwise the merge commit's own. Several merge bases, or none: nothing is brought. One helper reads a merge, `gov.guard.containment_merge.read_merge`. Tests: `test_w1_50_merge_read_by_the_merge_base.py`, `test_w1_50_read_merge_helper.py` |

| DP-19 | An octopus merge in which the first parent has one merge base with one of the other parents and several, or none, with another | DEC-403 (delegated), option (a), as built: it fails closed as a whole. An octopus whose other parents cross only each other is read parent by parent, as built. Tests: `test_w1_50_read_merge_every_parent.py` |
| DP-20 | A merge commit that keeps its first parent's content of a path and so drops what another parent changed (review finding) | DEC-403 (delegated), option (a): the symmetric rule, in the one helper. A path where the merge commit differs from any parent is its own change unless another parent brought it; with several merge bases, or none, every path that differs from any parent is its own. Tests: `test_w1_50_merge_that_drops_a_parent_s_change.py`, `test_w1_50_merge_that_takes_each_side_s_change.py`, `test_w1_50_read_merge_every_parent.py` |

DP-21 to DP-28 are decided by DEC-410 (orchestrator, delegated under DEC-220, stricter-only). No package is open.

| Id | Question | Decision |
|---|---|---|
| DP-21 | A merge commit with the orchestrator's trailers, or none, made in the orchestrator's own call, whose own change is a ticket file (a dropped narrowing or close, a hand edit, a resolution) | DEC-410, option (b): a finding whatever the merge commit's trailers. Tests: `test_w1_50_merge_commit_own_change_of_a_ticket_file.py` |
| DP-22 | What `brought` holds under the symmetric rule | DEC-410: the complement of `own` over every parent, each path where the merge commit differs from some parent and that is not its own. Tests: `test_w1_50_read_merge_brought.py` and the rewritten helper cases |
| DP-23 | With several merge bases, or none, is a path the merge commit keeps as its first parent has it its own change | DEC-410, option (a): yes; DEC-403's words stand. Tests, unchanged: `test_a_merge_of_an_unrelated_history_is_flagged_for_the_acceptance_tests_its_first_parent_holds` and the helper's fail-closed cases |
| DP-24 | An acceptance test more than one parent changed against the merge base, held as one side has it | DEC-410, option (b): the merge commit's own change, whichever side's content it holds; a resolution of an acceptance test is a finding. Tests: `test_w1_50_acceptance_test_changed_on_both_sides.py` and three rewritten cases |
| DP-25 | An octopus whose other parents cross only each other | DEC-410, option (a): read as built; that pair brings nothing against each other (amends DEC-403's "read parent by parent"). Test, `own` unchanged: `test_read_merge_reads_an_octopus_whose_other_parents_cross_only_each_other_parent_by_parent` |
| DP-26 | Git's own clean combination of two sides' edits of one acceptance test | DEC-410, option (a): stays flagged, as built. Tests: the two clean-combination cases of `test_w1_50_acceptance_test_changed_on_both_sides.py` |
| DP-27 | A merge commit's own change under `tests/acceptance/**` with a test designer's trailers | DEC-410, option (b): a finding whatever its trailers. Tests: `test_w1_50_merge_commit_own_change_of_an_acceptance_test.py` and two rewritten cases |
| DP-28 | A merge commit with very many parents | DEC-410, option (a): the helper refuses a merge commit with more than 24 distinct parents; the move is then a finding as a whole. Tests, unchanged: the ninth batch's cases with 150 parents and with nine. The move as a whole (review finding, eleventh batch): `test_w1_50_move_of_very_many_merge_commits.py` |

## Earlier suites

`tests/acceptance/W1-03/test_w1_03_head_defaults.py::test_a_merge_that_is_not_a_fast_forward_is_flagged` makes four
merges in an engineer's call, of commits without trailers, and expects each flagged and nothing reverted. Under
DEC-266 a merge in any caller's call other than an orchestrator session's own stays flagged, so the test is right as
it stands and is unchanged. No test of W1-03, W1-45 or W1-47 makes a commit with trailers or a merge by the
orchestrator, so no other test of those suites is touched by the KPIs or the decisions. None makes a commit with
`Role: owner` either, so KPI success 5 touches none.
