**Sandbox check (Step 0):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6lid` failed with "Read-only file system", and no file was created. (b) `git hash-object -w` returned 1ae28402a109 and `git update-index --refresh` exited 0. Pass.
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

task: DAEO-6lid
status: PACKAGES
work_completed: Round 1 review of W2-159 at 2a67c4a63da0, read-only. I read the ticket and its Interface, every module in src/gov/session_watch, the main.py and commands.py diffs, the acceptance support file and README, both reference hooks, and the dispatcher's status and plan ready-list writers. I reproduced two findings in a planted project under the sandbox's `$TMPDIR` (since deleted), using `GOV_SESSION_WATCH_PS`, `GOV_SESSION_WATCH_NOW` and `GOV_SESSION_WATCH_GOV`, never a live session, never a hook in any `.claude/`.
files_changed: none
evidence: identity is GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-6lid, HEAD 2a67c4a63da0. FR-1 output: with a pid file 2 days old and its pid now held by an unrelated process started 10 minutes ago, the idle check answered `{"systemMessage": "...let through, something of yours is running: pid 812 (.gov-runtime/jobs/old/job.pid)."}`. The control run with the pid dead answered a block naming DAEO-u001. FR-2 output: with both checks run side by side on one Stop, state.json held only `{"idle": ...}`. A third waiter call in the same turn without `stop_hook_active` blocked again. The control, with the checks run one after the other, kept both records, and the third call said nothing. `git status --porcelain` is empty at the end.
tests: no pytest run. The reproductions were direct runs of `python3 -B -m gov.cli.main session-watch stop-check ...` against planted roots. I re-ran nothing the lead ran.
discoveries: the engineer's `docs/changes/W2-159-evidence.md` does not exist at 2a67c4a63da0. It is in allowed_paths and the launch rules ask for it, but no KPI line covers it. This repository has 6 leftover pid files with no `.exit` right now (5 in the main tree, 1 in this worktree), and pid_max is 4194304. The reference hook's own comment says "pid_max wraps here in days".
risks: FR-1 lets an idle turn end while unblocked work waits, for as long as a reused pid's new process is under 3 h old.
lessons: a port of a reference can drop a guard the reference added after an incident. FR-1 is the reference's "a reused pid is not counted" rule, which did not survive the port. A diff of the port against the reference's documented rules would catch this.
proposed_decisions: none
unresolved: whether `gov plan --ready`'s batch 1 lists in_progress tickets that are waiting on review. If it does, the default dispatcher source names them as unblocked (FR-4).
recommended_next_action: resume the engineer for FR-1 only: skip a pid file whose process started later than the file was written, with the reference's slack, plus one unit case. FR-2 to FR-5 ride along or land as rows (DEC-802). This is round 2 of at most 2.
guard_refusals: none

---
task: DAEO-6lid
decisions: [DEC-1110, DEC-1109, DEC-1027, DEC-936, DEC-801, DEC-808, DEC-1010, DEC-802, DEC-1014]

## Probe record: W2-159 reviewer, round 1, head 2a67c4a63da0

### Probed and found sound
- **No trap.** The command always exits 0 and prints at most one JSON object. Any exception inside `run` becomes a `systemMessage` plus a log line. An unreadable or malformed state file is named and the turn ends. A block is written to the state file before it is answered, so a failed write ends the turn instead of blocking it. Gov's own failures (a faulty module, a config error) exit 1, which does not block. Exit 2 comes only from a mistyped hook command, which is an install-time error and the owner's ACT.
- **The once-a-turn bound (S3), one check at a time.** `stop_hook_active` always means nothing is said. The state is keyed by check, session and turn. The turn is the last real prompt, or a scheduled wakeup. IDLE-REASON is read only from this turn's assistant text and `last_assistant_message`, never from user text. It is checked before the bound and logged. Neither a block nor a reason carries into the next turn.
- **S1.** Only the registered session gets an answer. A missing, unreadable or empty session file says nothing. A stand-by note younger than its limit says nothing. A zombie waiter does not count as armed. The block names the configured `waiter_arm`.
- **S2 and S4.** The idle check ignores the stand-by note. A status older than 300 s is not used, and the check says so. The field names match W2-121's `run.py` (`gate.open`, `gate.disk.open`, `outcome`, `running`, `running_jobs`, `pending_starts`). A task held only by the configured waiter or by a bare `sleep` is not counted. Anything over 3 h is named as stale and not counted.
- **S5 and F3.** Items come from the config (dispatcher default, `lines` reader or a module reader), and every reader failure is named. Searching src/gov/session_watch for this repository's file, folder, ticket and tool names finds none. The only hits are a decision id and the word "landings" in the waiter's reason.
- **F4.** `git diff --name-only e84e6c9cf..2a67c4a63da0` lists src/gov/session_watch/**, src/gov/check/commands.py, src/gov/cli/main.py and tests/unit/session_watch/**, all in allowed_paths, plus tests/acceptance/W2-159/**, which is the test designer's path. The `_known` change renames no existing command: session_watch is the only underscore folder with a command module.

### Findings

**FR-1 (S2): a reused pid counts as running work.**
- **What was done:** the project has a leftover pid file from a worker that ended without writing its exit file. The file was written two days ago, and its number now belongs to an unrelated process started 10 minutes ago. One unblocked item is listed and nothing else runs.
- **What happened:** the idle check let the turn end with "something of yours is running: pid 812 (...)".
- **What should have happened:** a block naming the item. S2 counts a pid file "whose process is alive", and that process is gone. The reference skips a pid whose process started after the file was written; the port dropped that rule.
- Ordinary work: yes, because workers that are killed or that end with the machine routinely leave pid files with no exit file (6 exist here now), the default glob `.gov-runtime/**/*.pid` takes in all of them, and the reference notes the pid space wraps in days. No construction is needed.
- Consequence: fails open
- Scope: in
- **What would reverse it:** a CTO ruling that S2's "a pid file whose process is alive" means any live process with that number. Or evidence that every launcher the product supports removes its pid file, or writes `.exit`, on every way a run ends, including a kill or a machine stop.

**FR-2 (S3): the two checks overwrite each other's once-a-turn record.**
- **What was done:** both checks are installed, as the design intends. They run side by side on one Stop, and both block: the waiter is unarmed and an item is unblocked.
- **What happened:** the idle check reads the shared state file at its start and writes it back after `gov plan` returns. That wipes out the record the waiter wrote in between. A later stop in the same turn, without `stop_hook_active`, got a second waiter block.
- **What should have happened:** S3 says "never twice for the same turn". Each check should keep the other's record, for example by re-reading the file just before writing, or by writing one file per check.
- Ordinary work: yes, because Claude Code runs a Stop event's hooks side by side, and the idle check's read-then-write spans the plan's run.
- Consequence: other. It is one extra reminder in a turn; the next stop carries `stop_hook_active`, so there is no trap, nothing fails open and no work is lost.
- Scope: in
- **What would reverse it:** evidence that Claude Code runs a Stop event's hooks one after another, or that a stop in the same turn without `stop_hook_active` cannot happen after a block.

**FR-3 (S2): other standing watchers count as running work.**
- **What was done:** a background task that is a standing watcher but not the configured waiter is running, for example a helper watch or a sentinel.
- **What happened:** the idle check counts it as running work and lets idle turns end for up to 3 h. After that it is named as stale.
- **What should have happened:** the Interface says to read tasks "as the reference reads them". The reference excludes its standing watchers; the port has no setting to list them.
- Ordinary work: yes, because orchestrators re-arm standing watchers routinely.
- Consequence: fails open, bounded at 3 h and named in the systemMessage.
- Scope: out. S2's text counts any live background task, and a configurable watcher list is a new setting. It belongs with W2-160, the helper watch.
- **What would reverse it:** a CTO reading that "as the reference reads them" in the Interface puts the watcher exclusion inside S2.

**FR-4 (S2): with the default dispatcher source, everything in batch 1 is unblocked.**
- **What was done:** the idle check runs with the default source while the dispatcher's tick has stopped, or while a ticket in batch 1 is in progress outside the dispatcher.
- **What happened:** every ticket in the plan's batch 1 is treated as unblocked, including tickets that leads are running and ones in progress waiting on review. The dispatcher's leads have no pid files, and its status is not used after 5 minutes.
- **What should have happened:** those tickets are not idle work. The reference left its own coordination ticket out of the list.
- Ordinary work: yes, because the dispatcher's tick can stop while its leads run.
- Consequence: other. It is an extra block once a turn, and an `IDLE-REASON` line ends it. It does not fail open.
- Scope: out. S5 fixes the dispatcher's ready list as the default.
- **What would reverse it:** evidence that `gov plan`'s batch 1 never holds in-progress tickets.

**FR-5 (S1): the waiter is matched machine-wide by text.**
- **What was done:** a waiter command string is configured, and some other process's command line contains it. That could be another project's waiter, a `tail -f` of the waiter's log, or an editor open on the script.
- **What happened:** the waiter check treats the waiter as armed and says nothing.
- **What should have happened:** S1's text asks only that "no process of any configured waiter command is running". The reference behaves the same way.
- Ordinary work: yes, but only for the seconds those other processes live, unless another project runs the same waiter.
- Consequence: fails open
- Scope: out. The implementation matches S1's wording and the reference. A Wave 3 row.
- **What would reverse it:** a ruling that S1 means this project's waiter only.

**Classification:** 1 blocking (FR-1: in scope, ordinary work, fails open); 4 rows (FR-2 in/yes/other; FR-3 out/yes/fails open; FR-4 out/yes/other; FR-5 out/yes/fails open).

**Recommendation:** resume the engineer for FR-1 in round 2. FR-2 rides along if cheap (DEC-802); FR-3 to FR-5 become rows (FR-3 for W2-160).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "S2", "verdict": "fail", "findings": [{"id": "FR-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "FR-3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "FR-4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "fail", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}]}
```