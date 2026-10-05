# W1-28 acceptance tests: `gov pause`

Ticket `DAEO-9279`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
51 cases in 7 files. Eight decision packages are open (below); 2 cases cannot pass from the ticket's paths (DP-1).

```
python3 -m pytest tests/acceptance/W1-28 -q -p no:cacheprovider
```

## How the tests run

- **No test pauses this repository.** Every project is a temporary git repository: W1-02's fixture project (four
  tickets in progress, `.gitignore` with `.gov-runtime/`, the guard hook installed). Every command gets the temporary
  project as `--root` and as its working directory; `w1_28_support.gov` refuses a project inside this repository.
  `conftest.py` checks before and after every test that this worktree has no `.gov-runtime/freeze`, and never
  removes one. A project left frozen is deleted with pytest's temporary directory.
- Through public interfaces only: `gov pause ... --json` (W1-07's console-script stand-in), its API-0002 envelope and
  exit code; the guard's PreToolUse hook as a process (W1-02's `run_hook`); `gov.tasks.claim` and `gov.tasks.holder`
  (W1-09), each in a new process; `git`; the files a KPI names. The code under test is this worktree's `src/`.
- Deterministic, no network, no dev tier. `HOME`, `TMPDIR` and the bytecode cache are temporary directories.
- **The caller's role** is given twice with the same value, `--role <role>` and `GOV_ROLE=<role>`; the owner is the
  role `owner` (DP-3). It is set in one place, `w1_28_support.pause`.

## KPI lines and covers ids

| KPI line | File | Cases | Red reason |
|---|---|---|---|
| **Success 1.** `gov pause` sets the freeze flag and the next write by any role is denied; `gov pause --off` clears it **[CAP-05.a]** | `test_w1_28_freeze.py` | `test_pause_sets_the_flag_in_the_runtime_directory` · `test_the_next_write_by_each_role_is_denied_until_pause_is_lifted[5]` · `test_a_bash_write_is_denied_while_paused[2]` · `test_reads_stay_open_while_paused` · `test_git_status_is_unchanged_by_the_denied_writes` | `built` fixture: `gov pause is not built yet: it returns NOT_IMPLEMENTED` |
| | `test_w1_28_command.py` | `test_gov_pause_is_no_longer_answered_as_not_implemented` · `test_help_names_each_option[3]` · `test_rollback_without_a_ticket_is_a_usage_error` | The command answers `NOT_IMPLEMENTED`; `--help` names no option; exit code 1, not 2 |
| **Success 2.** Pause state appears in `gov status` | `test_w1_28_status.py` | `test_gov_status_shows_a_paused_project_as_paused` · `test_gov_status_shows_the_pause_lifted` | `built` fixture. **After the command is built: `gov status --json reports no pause state` (DP-1)** |
| **Success 3a.** `gov pause --cancel-agents` releases every claim and records the cancelled sessions **[CAP-05.b]** | `test_w1_28_cancel.py` | `test_cancel_agents_releases_every_claim` · `test_a_released_ticket_can_be_claimed_again` · `test_the_result_names_each_cancelled_session` · `test_each_cancelled_session_is_recorded_in_its_ticket` · `test_cancel_agents_with_no_claim_succeeds_and_releases_nothing` | `built` fixture |
| **Success 3b.** `gov pause --rollback <ticket>` reverts the ticket's commits with `git revert` and records it **[CAP-05.c]** | `test_w1_28_rollback.py` | `test_rollback_reverts_the_commits_of_the_ticket_and_no_other` · `test_rollback_only_adds_commits` · `test_rollback_leaves_no_uncommitted_change_outside_the_tickets` · `test_the_result_names_each_reverted_commit` · `test_the_rollback_is_recorded_in_the_ticket` · `test_rollback_finds_a_commit_made_before_the_trailer_rule_by_its_message_body` · `test_rollback_with_nothing_to_revert_changes_nothing[2]` · `test_rollback_does_not_lose_uncommitted_work` | `built` fixture |
| **Success 4.** Pause, cancel and rollback run only on the owner's or the orchestrator's invocation, give the same result on repeat, and each writes a record in the ticket **[CAP-05.d]** | `test_w1_28_roles.py` | `test_a_worker_cannot_pause[5]` · `test_a_role_nobody_knows_cannot_pause` · `test_a_worker_cannot_lift_a_pause` · `test_a_worker_cannot_cancel_agents` · `test_a_worker_cannot_roll_back` · `test_the_orchestrator_can_pause` · `test_the_orchestrator_can_cancel_agents` · `test_the_orchestrator_can_roll_back` | `built` fixture |
| | `test_w1_28_repeat.py` | `test_pause_on_a_paused_project_succeeds_and_stays_paused` · `test_one_off_lifts_however_many_pauses` · `test_off_on_a_project_that_is_not_paused_succeeds_and_changes_nothing` · `test_off_twice_gives_the_same_result` | `built` fixture |
| | `test_w1_28_cancel.py`, `test_w1_28_rollback.py` | `test_cancel_agents_gives_the_same_result_on_repeat` · `test_rollback_gives_the_same_result_on_repeat` · the two "recorded in the ticket" cases above | `built` fixture |
| **Failure 1.** A write succeeds while paused | `test_w1_28_freeze.py` | `test_the_next_write_by_each_role_is_denied_until_pause_is_lifted[5]` · `test_a_bash_write_is_denied_while_paused[2]` · `test_pause_on_a_paused_project_succeeds_and_stays_paused` (repeat file) | `built` fixture |
| **Failure 2.** The flag lives outside the repository runtime directory | `test_w1_28_freeze.py` | `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` · `test_the_flag_is_not_seen_by_git` · `test_pause_sets_the_flag_in_the_runtime_directory` | `built` fixture |

**Count.** KPI lines with tests: 6 of 6 (4 success, 2 failure). Covers ids with tests: 4 of 4 (CAP-05.a, .b, .c, .d).
Not tested, because no source decides it: a record in a ticket for the plain pause and for `--off` (DP-6), a call
with no role (DP-3), the orchestrator lifting a pause (DP-2).

## Red before implementation

Observed 2026-10-05: `5 failed, 46 errors`.

- The 46 errors stop at the `built` fixture: `gov pause is not built yet: it returns NOT_IMPLEMENTED`.
- The 5 failures, in `test_w1_28_command.py`: `gov pause --json` answers `NOT_IMPLEMENTED`; `gov pause --help` names
  none of `--off`, `--cancel-agents`, `--rollback` (3 cases); `gov pause --rollback` with no ticket ends with exit
  code 1 (`NOT_IMPLEMENTED`), not 2.

Checked once against a throwaway stand-in of about 80 lines, in a copy outside the repository (never committed):
51 passed with a one-line change to `gov status` in the copy, and 49 passed, 2 failed (`test_w1_28_status.py`)
without it. So 49 cases can be passed from `src/gov/pause/**` alone; the other 2 are DP-1.

## Planned revision in W1-07 (DEC-190)

`tests/acceptance/W1-07/w1_07_support.py`: `pause` joins `BUILT_LATER`, so
`test_a_reserved_command_not_yet_built_returns_not_implemented[pause]` leaves the parametrisation. Reason: "planned:
command implemented". As for `checkpoint` and `readiness`, the case is removed, not inverted: W1-07's suite stays
green (225 passed), and the red counterpart is `test_gov_pause_is_no_longer_answered_as_not_implemented` here.

W1-07 still runs a bare `gov pause --json`, with no role, in its own copy of the working tree
(`EVERY_INVOCATION`): `test_no_command_writes_outside_its_act_paths[pause]` expects nothing to change outside
`.gov-runtime/`. A bare pause that writes a record into a ticket file would turn that case red (DP-3, DP-6).

## What the sources settle

| Point | Settled by | Tested as |
|---|---|---|
| The flag | DEC-109: the file `.gov-runtime/freeze`; `FREEZE_FLAG` at `src/gov/guard/decide.py:19`, read at `:573`; its content is not read (W1-02) | the file exists after `gov pause`, is gone after `--off` |
| "Any role is denied", the orchestrator included | `decide.py:616-617` denies every write target before it looks at the role (`:619`); nothing more is needed from this ticket than the file | the guard is asked for each of W1-02's five roles |
| How `--off` can run while writes are denied | The guard judges tool calls by their write targets; `gov pause --off` in a Bash call names none (`decide.py:598-599`), and the command is its own process. In a launched worker session the launcher's literal `Edit` deny rule on the flag stops it at the OS level (DEC-311); in an unsandboxed orchestrator session nothing does (DEC-181) | `--off` clears the flag of a paused project |
| The command module | DEC-317; `src/gov/cli/main.py:11-57`: `run`, `add_arguments`, `ACT_PATHS`, `EXIT_CODES`; a refusal is a `GovError` (exit 1, or a declared code from 3); a usage error is argparse's 2 | envelope by API-0002; a refusal is `ok: false`, not exit 0 or 2 |
| What a claim is | DEC-292, `src/gov/tasks/claims.py`: the lock `.tickets/.claims/<id>` naming its holder, `<role>:<session>`; `gov.tasks` has `claim`, `holder`, `release` and nothing that changes a ticket's status | no lock is left; `holder` is None; the ticket can be claimed again |
| A ticket's commits | DEC-182: the `Task:` trailer in the final block; before 2026-10-03 the whole message (as `src/gov/store/loader.py:13-14, 32` reads them) | both forms are reverted |
| `git revert` only | KPI line, CAP-05.c | HEAD before is an ancestor of HEAD after; no reset, rebase or amend in the reflog |
| The W1-07 case | DEC-190 | see above |

## Decision packages

Each of these is open. Where a case had to follow one option, the table says which. Confidence is the designer's.

### DP-1: how "Pause state appears in `gov status`" is delivered (owner or orchestrator)

- **Question.** `gov status` is `src/gov/cli/commands/status.py` (W1-07), outside `src/gov/pause/**`. Its result today
  is `{root, config_files}`: it reports nothing about the flag. Who makes it report the pause state, and under which
  key?
- **Why now.** KPI success 2 cannot be met from the ticket's paths. W1-32 (`gov status`, STANDARD) depends on W1-28
  and CAP-28's acceptance line lists "pause state" among what `gov status --json` holds.
- **Options.** (a) Move the KPI line to W1-32; W1-28 only makes the state readable (the flag file, and the pause
  result). `test_w1_28_status.py` moves to W1-32's suite. (b) Add `src/gov/cli/commands/status.py` to W1-28's
  `allowed_paths` for a one-key change. (c) Keep the line in W1-28 as "the pause state is readable by `gov status`"
  and test only the flag file.
- **Impact.** (a) W1-28 closes with 49 cases; the line is delivered one ticket later. (b) Two tickets touch
  `status.py`; W1-32 rewrites it soon after. (c) The line as written stays unmet.
- **Reversibility.** High for all three: one key in a read command.
- **Cost.** (a) a KPI edit in two tickets; (b) about 3 lines and a path edit; (c) a KPI edit.
- **Recommendation.** (a), with the key name decided in W1-32. **Confidence:** medium-high.
- **Tests.** The 2 cases of `test_w1_28_status.py` follow (b): they ask `gov status --json` for a key whose name
  contains `pause`, whose value differs when paused and returns after `--off`.

### DP-2: may an orchestrator session set, and lift, the freeze (owner)

- **Question.** KPI success 4 lets the orchestrator run pause. DEC-176 says everything under `.gov-runtime/` outside
  `scratch/` is denied to the orchestrator and "setting or lifting a freeze is the owner's action". Which holds for
  `gov pause` and for `gov pause --off`?
- **Why now.** The command writes the flag as a process, so the guard does not see it; in an unsandboxed
  orchestrator session (DEC-181) the command's own role rule is the only thing between the orchestrator and the
  flag. The KPI line predates DEC-176.
- **Options.** (a) The orchestrator may set and lift (the KPI as written; DEC-176 amended for this command).
  (b) The orchestrator may set, only the owner lifts. (c) Only the owner sets and lifts (the KPI line amended).
- **Impact.** (a) An agent can end a freeze the owner set. (b) An agent can stop work in an emergency and cannot
  restart it. (c) An orchestrator that sees a runaway worker can only tell the owner.
- **Reversibility.** High: a role list in one module.
- **Cost.** A few lines either way; (c) and (b) need the KPI line or DEC-176 reworded.
- **Recommendation.** (b). **Confidence:** medium.
- **Tests.** `test_the_orchestrator_can_pause` follows (a) or (b). No case has the orchestrator lift a pause.
  `--cancel-agents` and `--rollback` by the orchestrator are tested as allowed: releasing a dead session's claim is
  the main orchestrator's job (DEC-292), and it may write anywhere outside the acceptance tests (DEC-156).

### DP-3: how the command learns who calls it (owner)

- **Question.** `main.py` gives every command `args.role` (`--role`, "the role of the caller"); a launched session
  has `GOV_ROLE` (the launcher sets it). `owner` is not one of the guard's roles. Which of the two does `gov pause`
  read, what is the owner's invocation, what is a call with no role, and what if the two disagree?
- **Why now.** "Only on the owner's or the orchestrator's invocation" cannot be built or tested without it. No
  existing command checks a role (W1-25 residual: DEC-320 is not enforced by `gov checkpoint`).
- **Options.** (a) Both are read; the call runs only if every value given is `owner` or `orchestrator`; a call with
  no role is refused (fail closed, in the spirit of DEC-179). (b) As (a), but a call with no role is the owner's:
  the human at a shell types `gov pause` and nothing else (CAP-05: "with one command"). (c) `--role` alone decides.
- **Impact.** (a) The owner types `gov pause --role owner`. (b) Any session without `GOV_ROLE` passes as the owner.
  (c) A worker passes `--role owner`. Under every option the rule is a convention, not a barrier: a worker can give
  any role. The barrier is the launcher's deny rule on the flag (DEC-311), which a headless session does not have.
- **Reversibility.** High.
- **Cost.** About 5 lines.
- **Recommendation.** (a), and a `GOV_ROLE` that names a worker role refuses whatever `--role` says.
  **Confidence:** medium.
- **Tests.** Every case gives the role both ways with the same value; the owner is `owner`. That passes under (a),
  under (c), and under (b) if `owner` is accepted as a value. A call with no role and a call whose two values differ
  are not tested. The error code and exit code of a refusal are not fixed: a refusal is `ok: false` with a
  `GovError` code other than `NOT_IMPLEMENTED`, and an exit code other than 0 and 2.

### DP-4: what `--cancel-agents` changes in a ticket (orchestrator, delegable)

- **Question.** A lock and `status: in_progress` both count as claimed (DEC-292). `gov.tasks` can remove the lock
  (`release`, for the holder it reads with `holder`) and has no function that changes a status. Does "releases
  every claim" also set the ticket back to `open`?
- **Why now.** After a cancel, a ticket without a lock and still `in_progress` is not READY (`CLAIMED`), so a fresh
  session is not started on it.
- **Options.** (a) Locks only; the status stays, and the orchestrator reopens what it wants restarted. (b) Locks,
  and `in_progress` back to `open` through the vendored `tk`.
- **Impact.** (b) changes authoritative ticket state in an emergency command and needs `tk`, which `gov.tasks` does
  not wrap for this. (a) leaves a manual step.
- **Reversibility.** High. **Cost.** (a) none; (b) about 10 lines and a new `gov.tasks` function outside the paths.
- **Recommendation.** (a). **Confidence:** medium-high.
- **Tests.** No case asserts the status. The cases assert no lock, `holder` None, and that the ticket can be claimed
  again.

### DP-5: what `--rollback` does beyond the plain case (owner)

- **Question.** Seven points no source decides: (1) one revert commit per commit, or one for the ticket; (2) the
  message and trailers of a revert commit: DEC-182 asks `Task:` and `Role:` of every commit, but a `Task:` trailer
  makes the revert one of the ticket's own commits, and on a closed ticket it is a containment finding (DEC-318);
  (3) merge commits that carry the ticket's trailer (the integration merges do, with `Role: orchestrator`):
  skipped, or reverted with `-m 1`; (4) a revert that conflicts: abort and report, or stop mid-way; (5) an unknown
  ticket, and a ticket with no commit: an error, or success with nothing reverted; (6) a dirty tree: refused, or
  left to git; (7) on repeat: no new commit, or an error.
- **Why now.** The command rewrites what HEAD holds. Each point changes what the owner finds after an emergency.
- **Options.** (a) One `git revert --no-edit` per commit, newest first, merge commits skipped and named in the
  result; revert commits carry `Role:` and a trailer other than `Task:` (for example `Reverts-Task:`); a conflict
  aborts the whole rollback (`git revert --abort`) with an error; an unknown ticket is an error, a ticket with no
  commit succeeds with an empty list; a dirty tree is refused; a repeat reverts nothing and succeeds. (b) One
  squashed revert commit for the ticket (`git revert --no-commit`, one commit), the rest as (a). (c) As (a), with
  `Task: <ticket>` on the revert commits and the repeat told apart by "This reverts commit" lines.
- **Impact.** (a) keeps one revert per commit, readable in `git log`; the containment check (W1-50) needs to know
  the new trailer. (b) is one commit to undo, and loses the per-commit link. (c) follows DEC-182 to the letter and
  collides with DEC-318 on closed tickets.
- **Reversibility.** Medium: revert commits stay in history; the behaviour is a few lines.
- **Cost.** About 30 lines for any option.
- **Recommendation.** (a). **Confidence:** medium; low on the trailer name.
- **Tests.** The cases hold what every option keeps: HEAD holds none of the ticket's changes and all of the other
  ticket's; history only grows (no reset, rebase or amend); nothing is left uncommitted outside `.tickets/`; the
  result names each reverted commit by at least 7 characters of its hash; after a repeat HEAD holds the same files;
  with nothing to revert no committed file changes; an uncommitted change survives. No case has a merge commit or a
  conflict, and none asserts the count, message or trailers of the revert commits.

### DP-6: where "a record in the ticket" is written, and for which ticket (owner)

- **Question.** (1) Is the record a note in `.tickets/<id>.md`, and written how: `gov.tasks` has no note function,
  the vendored `tk add-note` appends a timestamped note. (2) Is it committed? (3) The plain pause and `--off` name
  no ticket: which ticket holds their record? (4) What does a repeat add?
- **Why now.** KPI success 4 asks a record of each of the three; `.tickets/**` is not in the ticket's
  `allowed_paths` (they bind the engineer, not the command), and a launched session cannot write there (DEC-315).
- **Options.** (a) A note appended to the ticket's file, uncommitted: for `--rollback` the named ticket, for
  `--cancel-agents` each ticket whose claim was released; pause and `--off` write no ticket record, their record is
  the flag file's content (who, when). (b) As (a), and pause and `--off` take `--ticket <id>` for their record.
  (c) As (a), and pause and `--off` write a note into every ticket in progress. (d) All records go to one runtime
  file (`.gov-runtime/`), none to tickets (the KPI reworded).
- **Impact.** (a) leaves the KPI's "each" unmet for the plain pause. (c) makes a bare pause change ticket files,
  which turns W1-07's `test_no_command_writes_outside_its_act_paths[pause]` red if a bare call is the owner's
  (DP-3 b). An uncommitted note leaves the tree dirty, which matters to DP-5 point 6 on a repeat.
- **Reversibility.** High for the place; the notes stay in the tickets.
- **Cost.** About 10 lines.
- **Recommendation.** (a), and on a repeat no second note when nothing was done. **Confidence:** medium-low.
- **Tests.** Two cases follow (a) in its weakest form: after `--cancel-agents` each ticket's file has changed and
  names its own holder and not the other's; after `--rollback` the ticket's file has changed and names each
  reverted commit (7 characters), and the other ticket's file has not changed. No case reads a record for the plain
  pause or `--off`, a note's format, whether it is committed, or what a repeat adds.

### DP-7: what "the same result on repeat" means (orchestrator, delegable)

- **Question.** The same state, or the same `result` object field for field (so no timestamp, no "already paused")?
- **Why now.** It decides whether a result may carry a time or a count of what this call did.
- **Options.** (a) State: a repeat succeeds and leaves the project as the first run left it. (b) Also equal
  `result` objects.
- **Impact.** (b) forbids a result that says what this call changed, which DP-5 and DP-6 want to report.
- **Reversibility.** High. **Cost.** None for (a).
- **Recommendation.** (a). **Confidence:** medium-high.
- **Tests.** All six repeat cases follow (a), which also holds under (b).

### DP-8: do `--cancel-agents` and `--rollback` also set the flag (owner)

- **Question.** Is `gov pause --cancel-agents` a pause plus a cancel, or a cancel alone? The same for `--rollback`.
- **Why now.** The command cannot stop a process: a session whose claim was released keeps writing unless the flag
  is set. A rollback while workers still commit can be overtaken.
- **Options.** (a) Both also set the flag; the owner lifts it with `--off`. (b) Neither does; the owner pauses
  first. (c) Both refuse unless the project is paused.
- **Impact.** (a) one command in an emergency, and a freeze the caller may not expect. (b) two commands, and a gap
  between them. (c) safest and the most typing.
- **Reversibility.** High. **Cost.** 2 lines.
- **Recommendation.** (a). **Confidence:** medium.
- **Tests.** No case asserts the flag after `--cancel-agents` or `--rollback`; the cases run on a project that is
  not paused, which (c) would refuse.

## Readings the sources do not spell out

1. **`--rollback <ticket>` takes the ticket id** (`DAEO-…`), the value of the `Task:` trailer. A WBS id is not tried.
2. **A worker's `gov pause` is refused by the command**, not by argparse: `ok: false`, an exit code other than 0
   and 2. API-0002 reserves 4 for "blocked by control state (pause/freeze) or human gate"; whether a refusal uses
   it is the implementer's (it must then be declared in `EXIT_CODES`).
3. **For the builder.** `tests/unit/launch/test_command_modules.py` uses `pause` as a not-yet-built stand-in and
   will break when the command is built (W1-25 residual); it is outside this ticket's paths, so the lead renames
   the stand-in.
