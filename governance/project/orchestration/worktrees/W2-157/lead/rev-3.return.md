**Sandbox check (Step 0):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ozyt` failed with `OSError: [Errno 30] Read-only file system`, and no file was made. (b) `git hash-object -w --stdin` worked (1ae28402…) and `git update-index --refresh` worked (exit 0). `GOV_TICKET=DAEO-ozyt`. **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, at the start and at the end. **Identity:** HEAD is 21cc8215c4e8bee7e84f56064689d1c849fcb48b and `git status --porcelain` is empty at the end.

task: DAEO-ozyt (W2-157), C2 review of the reopened fix's diff, 13ab2c9fe..21cc8215c
status: DONE
work_completed: I read the ticket, its "Reopened for one fix" section, DEC-1144 (2) and the earlier probe record (FR-1 to FR-13). I read the code diff, the test diff and the evidence diff in full. I ran live probes of the zombie rule and the bound against my own process groups, using the command and `watch()` with a planted HOME, a stand-in `nvidia-smi` and a 1 s period. I ran an S5 filesystem spy, a planted `/proc` with an unreadable member, a fork-relay race test, and a forced-failure test of the rig's reaping (one 4-test pytest file through heavy_slot.sh). I re-ran no suite.
files_changed: none
evidence: `git diff --name-only 5d915dc6c 21cc8215c` lists only `docs/changes/W2-157-evidence.md`, `src/gov/resources/backstop.py` and `tests/unit/resources/test_w2_157_backstop.py`. 5d915dc6c is also `merge-base HEAD w2/integrate`. The ticket, `tests/acceptance/` and `command.py` have no diff in the fix. Probe outputs are under "What was probed".
tests: one pytest file of my own in `$TMPDIR/rv/t`, which imports the real `rig`. It held three forced failures and one demonstration. Result: 3 failed (as forced), 1 passed, in 30.14 s. Every group planted by the three failing tests was reaped. Flags: `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`, `HOME` set to an empty folder, run through heavy_slot.sh. It ran no folder, so the `-m/-k` real-model exclusion did not apply: no real-model case was in scope.
discoveries: (1) The rig's teardown signals through `os.killpg`, which several tests replace for the whole process (`backstop.os` is the global `os`). This is the same class of fault as the `time.sleep` one the second engineer fixed (FR-16). (2) The zombie scan treats a `/proc/<pid>/stat` it may not read the same as one that vanished (FR-14).
risks: All four findings are low or info. None is reachable in ordinary work, fails open there, or loses work.
lessons: Under `HOME=<empty>`, pytest from `~/.local` disappears. Pass its site-packages on `PYTHONPATH`. Also, `python3 -I` ignores `PYTHONDONTWRITEBYTECODE`. I checked: no `.pyc` in the tree is newer than this session.
proposed_decisions: none
unresolved: none
recommended_next_action: Land the fix as is (ready). Record FR-14 to FR-17 as rows. FR-14's hardening is one line: skip only a vanished process (FileNotFoundError or ProcessLookupError) and count a PermissionError as live.

**What was probed:**
- **Setup:** `$TMPDIR/rv`, with a planted `home/.gov-os/machine/gate.json` (limit 15872, every_s 1, no embedders) and a stand-in `bin/nvidia-smi` that cats a reading file. `src/` was on `PYTHONPATH`. Every group was started with `start_new_session` and cleaned up with SIGCONT then SIGKILL, then a wait. The sandbox has its own pid namespace and its own `/proc`, which I checked.
- **P1, only member an unreaped zombie, command with no bound (run):** exit 0, untripped. The start line says `skipped (ended) 7`, then `end: every watched group has ended (7)`.
- **P5, a group that turns all-zombie mid-watch, command with no bound (run):** the job was killed and not reaped after 2.5 s. The command ended 3.1 s after starting, untripped, with the end line.
- **P2, zombie leader with a live child (run):** members were `{Z, S}` and `_live` was True. The watch stayed running. At 15900 MiB it tripped, `paused [23]`, and the members became `{Z, T}`.
- **P3, zombie leader whose other thread runs (run):** the main thread was ended with `syscall(SYS_exit)`, leaving tasks `{Z, S}`. `_live` was True. On the trip the running thread went to `T`.
- **P4, a SIGSTOPped group (run):** live. With `max_polls=2` it logged `end: the bound of 2 polls reached; no trip; groups still live 51`.
- **P8, a command name holding `)` and spaces, real `/proc` (run):** a name of `) Z 1 2 3 4` on a sleeping process parsed as `('S', 59)` and counted live. A zombie named `x) Z 1 <pgid>` counted ended.
- **D state (read):** `D` is not in `ZXx`, so the member is live. The test's planted `["Z","D"]` case gives live. I did not produce a real D-state process.
- **Unreadable stat (run, planted `/proc`):** with one zombie member and one live member whose stat is mode 0, `_live` is False. With the stat readable again it is True. The real `/proc/<pid>/stat` is 0444. (FR-14)
- **Fork-relay race (run):** a zombie leader with a member that forks its successor and exits in a loop. `_live` was False in 0 of 2000 calls. (FR-15)
- **The bound (run):**
  - `max_polls` 1 and 3 each returned the unchanged untripped dict and wrote one bound line.
  - A trip on the last allowed poll (the third) is a trip with no bound line.
  - 0, -1, True, False, 2.5 and "3" each refuse with `RESOURCE_ARGUMENTS_INVALID`.
  - A very large bound is accepted and runs as unbounded. That is expected: in my probe it looped until my own timeout stopped it, so it is not a finding.
- **The bound for the command (read):** `command.py:80` calls `watch(args.backstop, root)` and is unchanged, so the command has no bound line and the same L6 log and L8 result as before.
- **The tests (read, AST):**
  - 55 `watch()` calls. The only one without `max_polls` is the default-behaviour test, which raises after 50 polls.
  - The `gov()` subprocess calls have `timeout=60`, and the shared-group test has 40 s deadlines.
  - The patched names are `backstop._pause`, `PROC`, `_live`, `os.getpgrp`, `os.kill` and `os.killpg`. `time.sleep` is never patched and there is no busy loop.
  - Every child goes through `Rig.spawn`.
- **The S3 order test (read):** it now trips deterministically. The first two calls trip on the first poll (limit, then spill), and the third trips at once on `/api/ps`. In the fourth, port 9 gives no answer and the log offset starts at its current size. The replaced pause appends a whole line, so the second poll trips whatever the earlier calls left.
- **Reaping on failure (run):** three cases: a failure after planting (a paused job, a killed-but-unreaped job, a zombie and a body-spawned sleeper), a failure after a trip that paused a group, and a KeyboardInterrupt raised from the replaced pause and turned into a failure. No planted pid was left in any case. The demonstration case, with `os.killpg` replaced by one that refuses while a job lives, left that job running (pid 29, `S`). (FR-16)
- **S5 with `/proc` read (run):** a command run that ended by the zombie rule changed only `home/.gov-os/machine/gpu-backstop.log` across the whole planted tree.
- **F4 and KPI lines (run):** no change outside allowed_paths, no KPI line changed, no acceptance test changed.
- **The earlier rows:** I raised none again. The fix does not change FR-10 or FR-12: with the own group named, gov itself is a live member, so it still never ends on its own, as recorded.

**Findings:**
Classification: 4 findings. Not one is in scope, reachable in ordinary work and fails open or loses work. None blocks, and all four land as rows. No round is proposed.

- **FR-14 (low): a group counts as ended when its only readable member is a zombie and a live member's `/proc/<pid>/stat` cannot be read.**
  - What was done: a planted `/proc` with one zombie member and one live member whose stat is mode 0.
  - What happened: the group counted as ended, so the watch would log its end and stop watching a running job.
  - What should have happened: an unreadable member should count as live. Only a member that vanished should be skipped.
  - New. Decisions: DEC-1144 (2), DEC-1073, DEC-801.
  - Ordinary work: no, because `/proc/<pid>/stat` is 0444 on this machine. It needs a non-default `/proc` mount (hidepid) and a group with members of another user beside a zombie leader we own.
  - Consequence: fails open.
  - What would reverse it: an ordinary launch on this machine in which a group member's stat is unreadable to the backstop's user.
- **FR-15 (info): the end is decided on one scan of `/proc`.**
  - What was done: a group whose only live member forks its successor and exits, over and over.
  - What happened: 0 of 2000 scans called it ended. In principle, a successor born after the listing while its parent exits during the scan could be missed.
  - What should have happened: either nothing more (accept the race), or two scans in a row before ending.
  - New. Decisions: DEC-1144 (2), DEC-801.
  - Ordinary work: no, because it needs a zombie leader plus a fork-and-exit relay that happens inside a scan of a few milliseconds.
  - Consequence: fails open.
  - What would reverse it: one observed false end in an ordinary job's structure.
- **FR-16 (low): the rig's teardown signals through the process-wide `os.killpg` that tests replace.**
  - What was done: a test that plants a live job, then replaces `backstop.os.killpg` with one that refuses.
  - What happened: teardown could not signal the job, waited 30 s, and left it running (the planted sleeper ends on its own after 120 s).
  - What should have happened: the rig should keep a reference to the real `os.killpg` taken at import, as it does with `REAL_SLEEP`.
  - New. No test in the file today combines a refusing `killpg` with a live job: the one refusing test plants only a reaped short job. Decisions: DEC-1144 (2) item (3).
  - Ordinary work: no, because it needs a new test of that shape.
  - Consequence: other (a leftover process for up to 120 s, plus a slow teardown).
  - What would reverse it: a teardown that keeps the real `killpg`, or a rule that tests never patch `backstop.os`.
- **FR-17 (info): the evidence file's readings were not brought up to date with the fix.**
  - What was done: I read the evidence file's readings after the fix.
  - What happened: L8 still names the seam `watch(groups, root, env=None)`, and L6's forms do not list the bound line. Also, a bounded untripped result cannot be told apart from an "every group ended" result except through the log.
  - What should have happened: L8 should name `*, max_polls=None`, and L6 should name the bound line as a test-only form.
  - New. Decisions: DEC-1144 (2).
  - Ordinary work: yes, because a reader of L8 sees the old signature.
  - Consequence: other (the command never passes a bound).
  - What would reverse it: L8 and L6 already stating the bound somewhere I missed.

```verdict
{"ready": true, "kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": [
   {"id": "FR-14", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "FR-15", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
   {"id": "FR-16", "scope": "out", "ordinary_work": "no", "consequence": "other"},
   {"id": "FR-17", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []}]}
```

guard_refusals: 16:47 | Monitor command that set a shell variable (`f=…; until grep … $f`) | "A variable set in this command can't be checked before it runs" | true (a form rule; re-formed with the path written out, accepted). The heavy slot also made me wait about 10 min with "all 3 slots taken". That was a gate wait, not a refusal.