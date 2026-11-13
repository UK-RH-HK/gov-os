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