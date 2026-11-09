# ACT-STOP-IDLE-1: the CTO's idle check, a second Stop hook (DEC-1110 (1))

- **For:** the owner's operator, by hand in the main tree, in a plain terminal. A Claude session may also run it, but
  Claude Code's safety check asks for the settings edit. It installs one hook script and its tests (tracked,
  committed with `Role: owner`) and adds one `Stop` entry to `.claude/settings.local.json` (local, untracked).
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09, prepared by a helper agent. Rehearsed in a clone; nothing
  live is changed until the operator runs §6.
- **Under:** DEC-1110 (1) (the check, as an ACT, rehearsed), DEC-1109 (3) and DEC-936 item 2 (unblocked work keeps
  moving while an item waits on the owner), DEC-1027 E (the inbox waiter's Stop hook, the pattern followed),
  OPERATOR-AGENT-1 §2 and §3 (the class).
- **Class: (O).** This is the classifier's vote (§5) and the reviewer's (R8). OPERATOR-AGENT-1's table alone would give
  (b) for a settings hooks block and hook code. But the ACT installs a test file and a hook no rule names, and commits
  with `Role: owner`; each of these is (O). The highest vote applies, so the operator agent would refuse it. It is
  applied by hand with `Role: owner`, and the disagreement ((b) by the table, (O) by the code and the reviewer) goes
  in the digest, as §3 requires.
- **Review:** round 1 NOT READY (`reviews/act-stop-idle-1.md`, three must-fix: F1, F2, F3). All three are fixed tests
  first (§4a). This is round 2, the last.

## 1. What it does
Before the CTO's session ends a turn, `governance/project/orchestration/tools/stop_idle_check.py` answers **block**
when nothing of the CTO's is running while DECIDED-NOT-DONE shows unblocked items, and names them. It lets a
legitimate wait through and names which. In order:

| Step | What it reads | Outcome |
|---|---|---|
| 0. Whose session | `log/cto-session.txt` | another session, or none registered: nothing said, nothing logged |
| 1. The bound | `stop_hook_active`; the turn's id, kept in `log/stop-idle-state.json` (see below); a line `IDLE-REASON: <why>` among the CTO's messages of this turn (from the transcript, or `last_assistant_message`) | at most one block per turn; a stated reason ends the turn and is logged and shown to the owner; a second stop with no reason is let through, named "a second stop this turn, no IDLE-REASON line stated" |
| 2. Running | the four sources in §2, each under its age bound | anything running: let through silently, everything counted named in the log |
| 3. A legitimate wait | the dispatcher's tick: the gate or the disk gate shut; admission refused or the lead forecast refusing | let through, naming "the gate shut (…)" or "the machine full (…)" |
| 4. Unblocked items | DECIDED-NOT-DONE's tracking tables (§3) | none unblocked: let through, naming "every open item waits (N on the owner, M on a running job, K on a trigger)"; otherwise **block**, naming up to 15 items with their states |

**What counts as a turn.** A turn starts at a user entry that is neither a tool result nor meta. It also starts at
any user entry carrying `turnOrigin` or `wakeupSource`: a scheduled wakeup (the 09:00 and 18:00 digests, every
`schedule_wakeup`) is meta but starts a turn (F1). A block, or an `IDLE-REASON` line, covers only the turn it was
given in. Stop-hook feedback and system reminders carry no `turnOrigin`, so they stay inside their turn and the
bound holds.

The block's reason tells the CTO to start the items within the machine's limits (or move each to its true state in
DECIDED-NOT-DONE), or to write one `IDLE-REASON:` line and end the turn. Any task or pid file past the bound is named
in the block, and also in any let-through message.

**It never fails open silently.** Any error (an unreadable or malformed DECIDED-NOT-DONE, bad input, an unreadable
`/proc`) is named to the owner (`systemMessage`: "Idle check (DEC-1110) could not run: …; the turn ends unchecked")
and logged in `log/stop-idle.log`; the turn then ends. The hook always exits 0 and prints at most one JSON object.

If the script file is missing, the settings command exits 1 with a named message, which Claude Code shows as a
non-blocking error. It never exits 2, which Claude Code would read as a block on every turn. Standard library only;
26 to 75 ms on the live state.

**A declared stand-by (`log/cto-standby.txt`) does not let an idle turn end here**, unlike the inbox waiter's check:
DEC-1109 (3) says unblocked items keep moving while one waits on the owner.

## 2. How "running" is read, and why
Each source was checked against the live session on 2026-11-09 between 19:14 and 19:48. The first three come from
the machine's own state, not from any record the CTO writes.

1. **The session's background agents.**
   - Source: `<transcript>/subagents/agent-*.meta.json`. Claude Code writes `"finished": true` there when an agent
     ends.
   - Live check: 51 of 58 were finished, and the 7 unfinished were exactly the 7 agents then running.
   - Bound: an unfinished agent counts only if its transcript was written in the last **30 minutes**. An older one
     is named in the log as stale and not counted.
2. **The session's background Bash tasks.**
   - Source: `/tmp/claude-<uid>/<project>/<session>/tasks/*.output` held open by a live process, read from
     `/proc/*/fd`.
   - Bound: the holder must have started less than **3 hours** ago (F3).
   - Not counted as work: the standing watchers (the inbox waiter, `sentinel_check.sh`, `usage_log.sh`,
     `store_refresh_daily.sh`, `bare_watch.sh`) and a bare `sleep N` timer.
3. **Launched workers, verifications, landing selections and runs.**
   - Source: pid files:
     - `launch_worker.sh`'s `<tree>/.gov-runtime/scratch/lead/log/*.pid`;
     - `lead_verify.sh`'s `verify.pid`;
     - `landing_select.sh`'s `run.pid`;
     - `~/gov-os-runs/*/*.pid`, and one level deeper.
   - Counted when the process is alive, its `<name>.exit` is absent, and it started less than **3 hours** ago (F3).
   - Pid reuse: the process must also have started no more than 15 minutes after the file was written, unless it is
     one of the launchers.
   - Why: `pid_max` is 4,194,304 and the live pids had reached 4,089,492, so pids wrap within days. WSL's boot clock
     drifts against the wall clock by 100 s or more.
   - The dispatcher showed "leads running (0)" while 5 workers were alive; only the pid files saw them.
4. **The dispatcher.**
   - Source: `dispatch/status.json`, written by the same tick as `status.txt`.
   - Counted: leads, pending launches, jobs by phase, a close or a landing.
   - Bound: the status must be at most **5 minutes** old. A stale or unreadable status is named and never relied on.

**The 3-hour bound (F3).** Its purpose is that a loop that never ends cannot keep idle turns passing silently. Over
84 launched workers, the longest took 1.75 h (median 0.13 h), and the CTO's longest bounded wait is 3 h
(`proc.sh wait --max 10800`). Past the bound, a task or pid file is not counted and is named ("over the 3 h bound,
not counted: …"). The check then goes on: one block a turn at most, or a stated reason.

**Anything running lets the turn end.** This follows the decision's words: "if no agent or job is running". A
stricter per-item check is an option, not built, because matching items to jobs by name is unreliable.

## 3. How "unblocked" is read (F2)
The hook reads every `## 0<letter>.` section of `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`. It
finds the `#`, `item` and `state` columns by header. It removes `*` and backticks from the state, then splits the
state at its first WAIT word (any case) into a **head** and **the wait**.

1. **Open (unblocked):** the head holds `NOT STARTED`, `IN PROGRESS` or `DUE NOW` (in capitals, anywhere), or a
   pending step: the word `next`, or `; then` / `: then`.
2. **Else a wait,** when there is a WAIT word: on the owner (the wait names the owner), a running job ("running"), or
   else a trigger.
3. **Else closed,** but only when the state begins DONE, MERGED, APPLIED, STANDING, SUPERSEDED or CLOSED.
4. **Anything else is open:** READY, APPROVED, FILED, ANSWERED, DECIDED, REHEARSED, or an unknown word. A block
   happens at most once a turn, so the check errs toward the reminder.

The review's five rows, live forms, now read open:
- #21 "ANSWERED …; next: the lines into W2-88";
- #32 "Filed …; next: its test designer";
- #38 "Filed DAEO-btcs …; its test designer next";
- #52 "APPROVED …; next: build it";
- #69 "READY 11-09: W1-06 … not merged".

These stay as they were:
- "APPLIED twice …, then ACT-GATE-CONFIG-2" stays closed (a comma, not a pending step);
- "WAITS: W2-20, then D-10 and the owner's word" stays a wait (the `then` is inside the wait);
- "DONE …; K9 now "in progress"" stays closed (prose, not the state in capitals).

**Live at `177bcac37`:** 72 rows: 31 closed, 17 waits on a trigger, 3 on the owner, 21 open.

**A rule for the CTO:** close a row with DONE, MERGED or APPLIED and no `next`; mark a wait with WAITS.

**What counts as a parse error:** a missing or unreadable file; no `## 0` section; a section with no table; a table
without `#` or `state`; a row shorter than its header. Each is named, logged, and never a block.

## 4. The tests, the mutation check and the rehearsal
**The tests** (`test_stop_idle_check.py`, 31 cases on a planted DECIDED-NOT-DONE and a planted `/proc`, task folder,
agent folder, pid files and dispatcher status):
- blocks, naming exactly the open rows;
- every open item waiting (owner, running job and trigger counted);
- a running agent; finished and stale agents;
- a running task; the watchers and timers not counted; an ended task;
- a worker by its pid file; with its exit file; dead; a reused pid (refused, or accepted as a launcher);
- the dispatcher's leads and jobs; the gate shut, the disk gate shut, the machine full; a stale status named and
  ignored;
- once per turn; a new turn checked again; `stop_hook_active`;
- a reason line, in the transcript or in `last_assistant_message`; a reason from an earlier turn refused;
- a stand-by not honoured; another session, or none registered;
- five malformed or missing DECIDED-NOT-DONE files, each named; bad input named;
- the tree's own DECIDED-NOT-DONE parses; the default paths are the tree's own;
- **round 2:**
  - F1: a scheduled wakeup after a block is checked again; a reason does not carry into a wakeup; a meta reminder
    stays in its turn;
  - F2: the review's five live rows, plus the forms that must stay closed or waiting; a state in no known form is
    open; the open words in prose do not count;
  - F3: a task over the bound, and a pid file over the bound, are not counted and are named; a 2-hour task still
    counts.

**Red first:** the 7 new F1, F2 and F3 tests were run on the round-1 hook first. Six failed; the seventh is the bound's
guard and passed, as it should. The prose case was then added red first as well.

**The mutation check** (`mutation.log`): **20 of 20 mutants killed**. The 13 from round 1, plus:
- a scheduled wakeup not read as a turn;
- every meta entry read as a turn;
- tasks unbounded;
- pid files unbounded;
- a next step ignored;
- READY, APPROVED and FILED read as closed;
- the open words matched in prose.

### 4a. Round 1's findings
| Finding | Fix | Test |
|---|---|---|
| F1 a scheduled wakeup read as the turn before it | a user entry with `turnOrigin` or `wakeupSource` starts a turn | `test_f1_*` (3) |
| F2 READY, APPROVED, FILED, ANSWERED with a next step read closed | closed only for DONE, MERGED, APPLIED (and STANDING, SUPERSEDED, CLOSED) with no pending step; anything else open | `test_f2_*` (2), `test_a_state_in_no_known_form_is_open` |
| F3 tasks and pid files with no age bound | 3-hour bound, past it not counted and named | `test_f3_*` (2) |
| R8 the class | (O), head line and message | — |
| R10 the clone's commit | quoted from `rehearsal.log` below | — |
| R1–R7, R9 | rows for the CTO's backlog or Wave 3, as the review classed them; R9 is §5's gap | — |

### 4b. The rehearsal (`drafts/stop-idle/rehearse.sh`, `rehearsal.log`): 2026-11-09 19:48, 0 failures
A clone of `w2/integrate` at `7a3c527c8` (the log's "clone at 7a3c527c8") in
`~/gov-os-runs/STOP-IDLE-1-rehearsal`, with the live `settings.local.json` copied in. `apply.sh` ran with
`STOPIDLE_REPO` set to the clone.

| Step | Result |
|---|---|
| The live files before | 13 paths hashed: both settings files, the three guard hooks, the path map, `stop_waiter_check.py`, `permission_request.py`, the two targets (absent), the hook's log and state (absent), `cto-session.txt` |
| `check`, `apply`, `check`, `apply` | state old; backup `2b8909d236b7`; both files installed by hash; one `Stop` entry added; `verify` shows only that entry differs; 37 tests pass (31 for the idle check, 6 for the waiter); the settings command, as Claude Code runs it, answers nothing for another session; then "state applied"; a second apply "already applied" |
| The live bytes | the same edit on the live file with the live path computes the pinned `d715292711a2…` (computed only, never written) |
| The inbox waiter unaffected | its tests 6 passed before and after; its command byte-identical; its answer on the CTO's real input unchanged |
| End to end on the live state (read only) | through the settings command with the CTO's real session id and transcript: **let through, "running: 24"**, exit 0, 75 ms |
| The same, with the live state planted away | **block**, naming 21 unblocked items from the live DECIDED-NOT-DONE; the second stop of the turn: let through, named; the gate planted shut: "let through: the gate shut (SHUT (planted))"; DECIDED-NOT-DONE removed: "could not run …", logged as `error`, exit 0; the hook file removed: exit 1 with its message, never 2 |
| Planted faults | an edit to the hook after review: `check` refuses; a settings file changed since the rehearsal: `apply` refuses ("re-rehearse") |
| `undo` | the backup put back (`2b8909d236b7`); the two files removed; the clone's tree clean; `check` reads state old; the waiter's tests unchanged |
| The live files after | **the same 13 hashes**; the live tree's `git status` unchanged |
| The guard suites | not run: no guard file is touched (`.claude/hooks/**`, the path map and the guard's code hash as before) |

## 5. The class, by the code (`governance/project/operator/act_class.py`, run read-only on two bundles)
- **Only the settings file:** (b), from the `settings` row (a hooks block). No script hits.
- **The settings, the hook and its test (this ACT):** **(O)**. The new hook and its test fall to the catch-all row as
  unknown paths. `class-rules.yaml`'s guard-hook row names `stop_waiter_check.py` and `permission_request.py` by name,
  but not this hook.

**A gap to close (your change, (O); the rule table is the operator's own file):** add
`governance/project/orchestration/tools/stop_idle_check.py` to the guard-hook row. Until then, the landing check does
not flag a later CTO edit of this hook as a control path (R9).

## 6. The operator's steps: the message
> **ACT-STOP-IDLE-1 (DEC-1110 (1)): the CTO's idle check as a second Stop hook.** Class (O): by hand, in a plain
> terminal in the main tree, about a minute. The inbox waiter's Stop hook and everything else in
> `settings.local.json` stay as they are.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> A=.gov-runtime/scratch/orchestrator/drafts/stop-idle
> bash $A/apply.sh check     # the three files hash as reviewed (hook d56a7aa79331, tests a58027c533fd, edit b9afa575c4ed); 31 tests pass; "state: old (settings 2b8909d236b7)" (exit 0)
> bash $A/apply.sh apply     # backup; hook and tests installed; one Stop entry added (settings d715292711a2); only that entry differs; 37 tests pass; "APPLIED" (exit 0)
> git add governance/project/orchestration/tools/stop_idle_check.py tests/unit/orchestration/test_stop_idle_check.py
> git diff --cached --name-status    # expect exactly 2 A: those two files
> git commit -m "ACT-STOP-IDLE-1: the CTO's idle check as a second Stop hook (DEC-1110 (1)): blocks once a turn when nothing runs while DECIDED-NOT-DONE shows unblocked items, names a legitimate wait or a stated IDLE-REASON; hook d56a7aa79331, tests a58027c533fd; settings.local.json 2b8909d236b7 -> d715292711a2 (local)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1110" --trailer "Role: owner"
> ```
> **Then:** the CTO's running session picks up the new hook after you review it in its `/hooks` menu, or at its next
> start (the fresh session before D-10, DEC-1110 (2)).
>
> **Undo:** `bash $A/apply.sh undo`. If the settings still hash as written, it puts the backup back; otherwise it
> removes only this entry. It removes the two files if they were never committed. If they were committed, revert that
> commit with the same three trailers; the files are inert without the entry.

## 7. Residuals
- **Internal Claude Code layouts.** `subagents/*.meta.json`'s `finished` flag, the `tasks/` folder and the wakeup
  entries' `turnOrigin` are Claude Code internals, checked on 2.1.318 and 2.1.319.
  - If they change, agents or tasks go unseen, and the check errs toward a block (once a turn, passing on a reason).
  - If `turnOrigin` disappears, a wakeup reads as the turn before it (F1 again); the log would show "bound" on a
    wakeup.
- **The watcher list is fixed in the hook.** An unlisted watcher counts for at most 3 hours. After that it is named
  in the block and in every let-through message.
- **The tree's own DECIDED-NOT-DONE is read by one unit test.** A malformed tracking table reds that test, as it
  would break the hook live; the fix is in the file.
- **Rows R1–R7 stay rows,** as the review classed them, for the CTO's backlog or Wave 3:
  - R1: consult the reason only when the check would block, and put a daily count of reasons used in the digest;
  - R2: an agent silent for more than 30 minutes;
  - R3: the WSL clock after a suspend, and the main tree's `verify.pid` glob;
  - R4: the remaining state edges;
  - R5: the waiter's block marks the idle check's record;
  - R6: machine-wide jobs, once the nightly is back;
  - R7: per-item capacity.

## 8. The files (scratch, `drafts/stop-idle/`)
| File | sha256 (first 12) | What |
|---|---|---|
| `stop_idle_check.py` | `d56a7aa79331` | the hook (installed at `governance/project/orchestration/tools/`) |
| `test_stop_idle_check.py` | `a58027c533fd` | 31 tests (installed at `tests/unit/orchestration/`) |
| `settings_edit.py` | `b9afa575c4ed` | the one settings change: expect, add, remove, verify (unchanged since round 1) |
| `apply.sh` | `eb1d3a086a3f` | check, apply, undo; the files' and both settings hashes pinned |
| `rehearse.sh`, `rehearsal.log` | `d8d0bf9f908b`, `2bfb87085175` | the rehearsal and its record |
| `mutation.log` | `717c86af803c` | 20 of 20 mutants killed |

[DEC-1110 (1), DEC-1109 (3), DEC-936 item 2, DEC-1027 E, ACT-STOP-WAITER-1, OPERATOR-AGENT-1 §2, §3 and §5,
`reviews/act-stop-idle-1.md`]
