---
type: probe
task: DAEO-6lid
reviewer_session: 80cdbed1-ea87-4363-ac20-a1ca2a066aad
implementer_session: "eng-1 11f69ffa-2adb-4261-8caa-1b6b21376c9f (ab2f0d223f22); eng-2 872133fc-eade-48ea-a3f0-ac0e869841d0 (680bdce1f526); eng-3 f77d63a4-59db-454b-bf2d-a974a57710d7 (d25c7f171467)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: da85fe5bcd88cc15be39dda82b7d27eae830973b
decisions_applied: [DEC-1110, DEC-1109, DEC-1027, DEC-1010, DEC-136, DEC-802, DEC-801, DEC-808]
---

# Probe record: W2-159 (DAEO-6lid) the orchestrator's two Stop checks in the product, STANDARD review, rounds 1 and 2 of 2 (DEC-1010)

- **Round 1** (reviewer session b586cef3-a81c-4993-bdae-c2b3534abb21, independent-auditor, Opus high, read-only)
  probed head `2a67c4a63da0`: **fail**. S2 was marked fail with FR-1 blocking (in scope, ordinary work, fails open).
  FR-1: a leftover pid file whose number now belongs to an unrelated, newer process counted as running work, so an
  idle turn ended. S3 was marked fail with FR-2 (in scope, ordinary work, other): the two checks run side by side
  overwrote each other's once-a-turn record. FR-3, FR-4 and FR-5 were out of scope.
- **The repair:** the lead gave FR-1 and FR-2 as behaviours B1 and B2 (DEC-136). B1: a pid file's process counts only
  when it started no later than 900 s after the file was written [lead]. B2: after both checks end, the state file
  holds both records for the turn. FR-2 rode along (DEC-802). The independent test designer added 9 acceptance cases
  (`29b7a2c335fb`). Run without the fix they gave 5 red (exactly B1 and B2) and 89 green. They were merged at
  `da85fe5bcd88`, for 94 cases. A fresh engineer fixed the code with its own unit cases (`d25c7f171467`):
  `running.py` adds the start slack, and `state.py`'s `record()` re-reads and merges under a lock.
- **Round 2** (reviewer session 80cdbed1-ea87-4363-ac20-a1ca2a066aad, independent-auditor, Opus high, read-only, a
  fresh session) probed head `da85fe5bcd88`: **pass**. Every KPI line S1-S5 and F1-F4 passes, FR-1 and FR-2 are
  fixed, and no finding is in scope, ordinary work and fails open or loses work. Rows: FR-3, FR-4, FR-5 (holding, out
  of scope), FR-6 (in scope, other), FR-7 and FR-8 (out of scope, other). There is no third round (DEC-1010).
- **The lead's checks of the probed head `da85fe5bcd88`:**
  - `gov accept W2-159`: pass, 94 passed, 0 failed, every line. S1 15, S2 35, S3 22, S4 11, S5 9, F1 16, F2 6, F3 1,
    F4 1.
  - The scoped verification (`lead_verify.sh`): 4868 tests in the parallel phase, 10 failed, 7 skipped; the serial
    phase had 1 test, green. All 10 reds are outside this ticket: the W2-96 signal family. They also fail on
    w2/integrate f7962d3661d1 (`.gov-runtime/scratch/lead/base_reds.sh`), and integrate has not changed the W2-96 code
    or tests since. They are shared base reds, and W2-177 fixes them.
  - An earlier step, at `680bdce1f526`: `gov accept` read failure-4 as fail because F4 had no case (the README called it
    the lead's check). The test designer added F4's case (`9254a220dfbc`, merged at `2a67c4a63da0`).
- **Residual rows the lead names:**
  - FR-3: standing watchers other than the configured waiter count as running, bounded at 3 h and named. For W2-160's
    helper watch.
  - FR-4: the default dispatcher source takes in-progress tickets in batch 1 as unblocked. An extra block, with
    IDLE-REASON as a way out.
  - FR-5: the waiter is matched machine-wide by command-line text, as S1's wording and the reference do.
  - FR-6: after a host sleep of more than 15 min, a live worker may read as a reused pid. An extra block; unmeasured on
    WSL2; the reference behaves the same.
  - FR-7: `docs/changes/W2-159-evidence.md` was not written. No KPI line covers it.
  - FR-8: the messages cite this register's DEC ids. F3 covers file names, folders and tickets only.

The two reviewers' returns follow verbatim, round 1 first. The last verdict block (round 2's) decides.

## Round 1 (2a67c4a63da0): the reviewer's return

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

## Round 2 (da85fe5bcd88, the last): the reviewer's return

Round 2 passes on all nine KPI lines (S1–S5, F1–F4): both round-1 fixes hold and nothing new blocks. I ran no tests and changed no files; the tree is clean at da85fe5bcd88.

**Sandbox check (step 0):** (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6lid` failed with "Read-only file system" and no file exists; (b) `git hash-object -w` (blob 1ae28402a109) and `git update-index --refresh` both worked. The `ps` check for ollama or llama-server showed nothing.

task: DAEO-6lid
status: DONE
work_completed: Round 2 of 2, the last (DEC-1010), at da85fe5bcd88. I read the fix diff from 2a67c4a63da0, the whole `src/gov/session_watch/` package, the reference's handling of reused pids, the README map of the acceptance tests and the branch's file list. Both fixes hold (FR-1 for B1, FR-2 for B2). FR-3, FR-4 and FR-5 still hold as rows. Three new rows (FR-6, FR-7, FR-8); none blocks.
files_changed: none. `git status --porcelain` is empty. The only write was the step-0 blob, which the launch protocol requires; it went into the shared object store.
evidence: `git diff 2a67c4a63da0 da85fe5bcd88 -- src/`; `git diff --name-only e84e6c9cf..da85fe5bcd88` (27 paths, all inside allowed_paths or tests/acceptance/W2-159/); reference `stop_idle_check.py:226-245` (the same 900 s slack, plus a launcher exception that the product leaves out); README batch 3 maps 9 cases to B1 and B2.
tests: none run. The lead's results stand: the engineer's 138 passed at d25c7f171; the designer's run at 29b7a2c335fb had exactly 5 red, the B1 and B2 cases. `lead_verify` and `gov accept` at da85fe5bcd88 are the lead's to report.
discoveries: The sandbox has its own pid namespace (4 processes visible), so the start time of a real worker could not be compared with its pid file here. This is why FR-6 is unmeasured.
risks: FR-6, below. It only ever adds a block; it never lets a turn end wrongly.
lessons: The reference already had both fixes (`START_SLACK_S`, and its state written per check). Diffing a port against its reference's guards early would have found FR-1 in round 1.
proposed_decisions: none
unresolved: FR-6 is unmeasured; reversing it needs a reading of WSL2's clocks across a host sleep.
recommended_next_action: READY is computed from the verdict block below: no finding is in scope, ordinary work and fails open or loses work. The lead reports `lead_verify` and `gov accept` at da85fe5bcd88. FR-3 to FR-8 go in as recorded rows: no round and no owner question.
guard_refusals: none

## Probe record (task: DAEO-6lid; head da85fe5bcd88; decisions: DEC-1110, DEC-1109, DEC-1027, DEC-1010, DEC-801, DEC-802, DEC-1088)

**Probed and found sound:**
- **B1 (reused pid):** a live pid counts only when its process started no later than 15 minutes after the pid file was written. A later process is neither counted nor named, the same as a dead pid. A process started earlier, or within the 15 minutes, still counts. A file whose write time cannot be read is skipped, not counted.
- **B2 (shared record):** when a check blocks, it takes a lock, re-reads the state file, sets only its own record and writes the file whole. Whichever check writes last, both records stay, and the later "already blocked this turn" check reads them. If the lock or the folder fails, the error is named to the owner (`systemMessage`) and logged, and the turn ends.
- **Never trapped:**
  - Any exception, a bad config, a missing or unreadable state file and a `gov plan` timeout (10 s) or failure all end the turn with a message and a log line.
  - `stop_hook_active` always lets the turn end.
  - The IDLE-REASON line is read only from this turn's assistant messages, so neither a reason nor a block carries into the next turn.
- **No silent fail-open:**
  - A dispatcher status older than 5 minutes is not used, and that is named.
  - Past 3 hours a job is named as stale and not counted.
  - The idle check ignores the stand-by note.
- **F3:** a search of `src/gov/session_watch` for this repository's file names, folders, ticket ids, tools and paths found none. The decision ids it does find are FR-8.
- **F4:** the diff against e84e6c9cf lists only allowed_paths and the designer's tests.

**Round-1 findings at this head:**
- FR-1: fixed.
- FR-2: fixed.
- FR-3: holds, row; the code is unchanged.
- FR-4: holds, row.
- FR-5: holds, row.

**FR-6 (S2; scope: in): a live worker read as a reused pid after the machine sleeps.**
- Done: a launched worker is running with its pid file. The host machine sleeps for more than 15 minutes, then wakes, and the session then tries to end a turn with unblocked items listed.
- Happened (inferred; not reproducible in the sandbox): process start times are worked out as the wall clock minus the age on the boot clock. If the boot clock stops while the guest is paused, the worker seems to have started more than 15 minutes after its pid file was written. It is then treated as a reused pid, and the idle check blocks, naming items while work runs.
- Should happen: the live worker counts and the turn ends.
- The reference has the same 900 s slack and the same behaviour.
- Ordinary work: yes, because sleeping a WSL2 host while a worker runs is ordinary. Whether the guest's boot clock stops during the sleep is not measured.
- Consequence: other. It is one extra block in the turn, with IDLE-REASON as a way out; nothing fails open and no work is lost.
- Would reverse it: a measurement on WSL2 showing that, after a host sleep of more than 15 minutes, a running process's start time from `/proc` stays within 900 s of its pid file's write time.

**FR-7 (no KPI line; scope: out): the evidence file is missing.**
- Done: the engineer's branch, read at its head.
- Happened: `docs/changes/W2-159-evidence.md` is not there. It is in allowed_paths, and the launch rules ask for one row per KPI line.
- Should happen: the file is present.
- Ordinary work: yes, because it is a step missed in ordinary work.
- Consequence: other. Nothing in the checks' behaviour depends on it.
- Would reverse it: the lead waived the file, or it exists on another branch.
- It is not in the verdict block because it maps to no KPI line.

**FR-8 (F3; scope: out): the messages cite this register's decision ids.**
- Done: an adopted product's orchestrator receives a block or a let-through message.
- Happened: the text cites DEC-1027, DEC-1110 and DEC-1109 from this repository's register. F3 covers file names, folders and tickets, not decision ids.
- Should happen: either text that stands without them, or ids the product's register holds.
- Ordinary work: yes, because every block shows them.
- Consequence: other.
- Would reverse it: confirmation that the Gov OS register ships with adopted products, which would make these the product's own ids.

**Classification:** 0 blocking; 6 rows. FR-3, FR-4, FR-5, FR-7 and FR-8 are out of scope with consequence other. FR-6 is in scope and ordinary work, but its consequence is other: it never fails open.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "FR-3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "FR-4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "FR-6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": [{"id": "FR-8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F4", "verdict": "pass", "findings": []}]}
```
