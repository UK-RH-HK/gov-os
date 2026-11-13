# Brief eng-4: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2: the reopened fix (a hanging unit test)

You are a fresh engineer for ticket DAEO-ozyt (W2-157: the GPU backstop, `gov resources --backstop <pgid>...`). The
code is built, reviewed and merged with w2/integrate (head 13ab2c9fe of w2/W2-157). The owner reopened the ticket for
one fix (DEC-1144 (2), P1-B (a)): read the ticket's last section "Reopened for one fix" first. You make that fix and
nothing else. No KPI line changes; you never read or change `tests/acceptance/` (an independent test designer's; it
runs `gov` as a subprocess with its own timeouts and is not touched by this fix).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md (command.py and config.py are in the ticket's paths but this fix does not need them) |
| the ticket (S4: "when every named group has ended on its own, the watch logs it and ends") | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the code | src/gov/resources/backstop.py (`_live`, `watch`) |
| the unit tests | tests/unit/resources/test_w2_157_backstop.py (the `Rig` class, the `rig` fixture, about 45 calls of `backstop.watch`) |
| the readings L1-L9 as applied | docs/changes/W2-157-evidence.md |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The fault
`test_w2_157_backstop.py::test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log` hung two
merge-queue runs (1 h 45 min, then 77 min). The test replaces the backstop's sleep, then calls `watch()` on planted
process groups; a call that does not trip polls forever (a busy loop), because a group whose members are all zombies
(the planted child exited but pytest has not reaped it) or paused still passes `os.killpg(g, 0)` in `_live`.

The lead's reading of why that test's fourth call may never trip (check it; do not take it on trust): the replaced
sleep is `lambda s: log.write_text("offloaded 1/2 layers to GPU\n")`, which overwrites the log with the same 28
bytes each time. If any earlier call in the same test slept once (under load: the stand-in `nvidia-smi` or the
stand-in `/api/ps` server answering late, 3 s `PS_TIMEOUT_S`, so the first poll found no reason), the log already
holds those 28 bytes when the fourth call starts, its offset starts at 28, every later write keeps the size at 28, and
`_partial_offload` never sees a new line. Then the planted job (`sleep(120)`) ends after 120 s, stays an unreaped
zombie, its group still answers signal 0, and `watch()` spins for ever.

## The fix (all three; the ticket's last section)
1. **A group whose live members are all zombies counts as ended.** In `backstop.py`, `_live(g)`: after
   `os.killpg(g, 0)` succeeds, read `/proc/<pid>/stat` of the processes whose process group (field 5) is `g`, and
   if every member found is a zombie (state `Z`, or `X` dead) the group has ended. Parse the state and pgrp after the
   last `)` (the command name may hold spaces or parentheses). Nothing by name, no `ps`, no pattern: group ids only.
   A paused member (`T`/`t`) is live. No `/proc` (or no member found though signal 0 succeeded) keeps today's answer
   (live). A process that vanishes while you read it is skipped. Keep `PermissionError` = live and
   `ProcessLookupError`/`OverflowError` = ended as now.
2. **`watch()` takes a bound.** A keyword-only argument (e.g. `max_polls: int | None = None`; or seconds — your
   choice, say which and why in the evidence), whose default (`None`) keeps the command's behaviour exactly
   (`command.py` calls `watch(args.backstop, root)` and is unchanged). When the bound is reached without a trip and
   with a group still live, the watch writes one log line naming it (e.g. `end: the bound of <n> polls reached; no
   trip`) and returns the result untripped. Check what the existing tests assert on the result's keys before you add
   a key; prefer adding none. Every unit test that calls `watch()` passes a bound (a small number fitting that test:
   the polls it needs plus a margin). A bound that cannot hang the run is the point: a test that needs more polls than
   its bound fails with a clear assertion, it never spins.
3. **Each test reaps the groups it plants.** The `rig` fixture already calls `close()` after `yield`; make the reaping
   certain: a `try`/`finally` so a failing test still kills (SIGCONT then SIGKILL to the group) and waits for every
   child it planted, including processes started outside `rig.job()` (e.g. the `other` same-name process in
   `test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on`, the `short_job` children, any `Popen`
   in a test body): register them with the rig, or reap them in the test's own `finally`.
4. **Make that test deterministic too**, inside its own assertions (no assertion weakened, the order limit, spill,
   embedder, log still proven): e.g. reset the log before each call, or have the replaced sleep append a new line
   rather than overwrite the same bytes, so the fourth call trips at its second poll whatever the earlier calls did.
   Look for the same overwrite-with-equal-size pattern in the other tests (`test_s3_a_partial_offload_line_...`,
   `test_s3_an_equal_offload_...`, `test_a_trip_without_a_reading_logs_none`) and fix it where it can bite.

Unit tests first, red on the present code, then the fix: at least (a) a group whose only member is an unreaped zombie
ends the watch untripped with the "every watched group has ended" line; (b) a group with a paused (SIGSTOP) member is
still live; (c) a group with a zombie and a live member is live; (d) `watch(..., max_polls=n)` on readings that never
trip returns untripped after exactly n polls (count the stand-in `nvidia-smi` calls) and logs the bound line;
(e) the default (no bound) still polls past a few polls (stop it with a group that ends, as
`test_s4_a_job_that_ends_first_ends_the_watch_without_a_trip` does).

## Proof (run each; put the outputs' summary lines in `evidence`)
Every pytest goes through the heavy-slot tool, with a TMPDIR outside the repository and outside ~/gov-os-runs:
`mkdir -p /tmp/w2-157-eng4` once, then each run as
`env TMPDIR=/tmp/w2-157-eng4 HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(pytest-randomly is not installed, so no `-p no:randomly`).
1. The backstop file 20 times in a row, each run under `timeout 120` (a shell loop in a script file under
   /tmp/w2-157-eng4, `timeout 120 env ... bash heavy_slot.sh python3 -m pytest tests/unit/resources/test_w2_157_backstop.py ...`),
   recording each run's exit code and summary line; none may hang (exit 124) or fail.
2. Then `tests/unit/resources` and `tests/acceptance/W2-157` and `tests/acceptance/W2-20` once each (the form above).
Check after every run that no planted process is left: no process of yours from the tests may outlive the run.

## Safety
Your unit tests plant their own process groups only (children started with `start_new_session=True` or `setsid`) and
stand-ins under `tmp_path`; never signal a process you did not start; never run `--backstop` against a real group, the
real GPU or the real HOME's gate.json. A hang you meet is stopped by its pid (`kill <pid>`), never by a name match
(`pkill`, `killall` are refused).

## Rules
- Add to `docs/changes/W2-157-evidence.md` one short section "Reopened fix (DEC-1144 (2))": the cause, the three
  changes as applied (the zombie rule, the bound's name and default, the reaping), the unit tests, and the 20-run
  proof's line.
- Anything longer than one line goes in a script file under /tmp/w2-157-eng4, run with `bash <file>`. Literal paths
  only. No merge, no push, no edit outside your paths. A refused call is reported, never worked around; refused twice
  for the same action, stop and say so. For a new file, `git add <path>` before `git commit -- <paths>`.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the 20 runs' exit codes and summary lines; the pytest summary lines of
tests/unit/resources, tests/acceptance/W2-157 and tests/acceptance/W2-20) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context (gov context DAEO-ozyt --role engineer)
