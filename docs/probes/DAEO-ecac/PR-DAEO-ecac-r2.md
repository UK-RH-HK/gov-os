---
type: probe
task: DAEO-ecac
round: r2
status: final
reviewer_session: 32ee08c6-6be9-4318-945d-56ade1392398
implementer_session: "2a98f1db-a61a-4254-8d28-de4e40732d06"
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: high
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: 7bc20ff4aba580480aa93a419893a3990d386361
reviewed_range: "2d1e751d4cca7a7a0323f78d4a5be800350db055..7bc20ff4aba580480aa93a419893a3990d386361"
previous_round: PR-DAEO-ecac-r1 (2d1e751d4, fail, F1)
decisions_applied: [DEC-847, DEC-963, DEC-983, DEC-1156, DEC-392, DEC-1010, DEC-1154, DEC-801, DEC-802, DEC-808, DEC-809, DEC-136, DEC-820]
scope: "Narrow re-check (DEC-1154) of round 1's F1 fix: the one-writer check under the start lock and the start record written before the lock is released; plus anything the range breaks (signals, lock release, reviewer, S5, exit codes, the signal unit cases)."
---

# PR-DAEO-ecac-r2: review round 2 of W2-60b (DAEO-ecac)

## Summary

This is a fresh independent auditor session, read-only, at head `7bc20ff4a`. It re-checked one thing: the fix for round 1's blocking finding F1 ("the one-writer check runs before the start lock, so two writing launches that start together both get in"). It also looked for anything else the range breaks.

The range holds three commits:
- `253b064f5` and `692331d1d` by en-3b (session `2a98f1db-a61a-4254-8d28-de4e40732d06`);
- the lead's merge `7bc20ff4a` of the test designer's round-1 cases (td-2, `fbf7273f2`).

The earlier implementers were en-1 (`9a33f460-887a-43be-bf58-a0ad509d9c34`) and en-2 (`cf1bcaf5-3742-4921-9f69-0441c697c055`). Round 1 was `2d1e751d4`, auditor session `49a21e81-476d-4a84-a42f-dbd1d9d05a83`.

**Verdict: pass. F1 is reversed, and the round finds no new finding.**

Round 1 named what would reverse F1: the second launch refused at gaps 0.0, 0.05 and 0.1 s and under a held start lock. My own probe on planted repositories and homes shows exactly that, at the head, every time:
- 20 of 20 gap trials (0.0, 0.05, 0.1 and 0.2 s, 5 runs each) passed;
- 5 of 5 held-lock trials passed.

The same probe against the pre-fix code fails as F1 described, so the probe can tell the two apart. Every lock-release path and every signal timing I probed fails closed. The reviewer exemption, S5 and the exit codes are unchanged.

## Step 0 (EMG-d4b-launched.md), reported first

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-60b','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there. As required.
- (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0). `git update-index --refresh` exited 0. As required.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing, both at the start and at the end.
- Identity: `GOV_ROLE=independent-auditor`; `git rev-parse HEAD` = `7bc20ff4aba580480aa93a419893a3990d386361`; branch `w2/W2-60b`.
- The harness's task path shows this session as `32ee08c6-6be9-4318-945d-56ade1392398`.

**Walls, reported as they happened.** My first command to find the step-0 brief was `find / -name 'EMG-d4b-launched.md' -not -path '*/gov-os-eval/*'`. A `-not -path` filter does not stop `find` from going into a folder, so before I stopped it (TaskStop, within its first 120 s) it may have listed or stat'ed folders under `/home/usain/gov-os-eval/`. That breaks the brief's wall against listing or stat'ing the evaluation root.
- It printed no path, matched no file and read no file contents.
- The sandbox's read-deny list covers `gov-os-eval/.../memory-retrieval/hidden`, `memory-verdict` and `memory-verdict-2`.
- I found the brief afterwards with Glob in the repository's scratch folders.
- No other call touched the walled paths. Nothing was refused.

## The range, read

- `src/gov/launch/launcher.py:1078-1080`: the first `check_one_writer` stays before anything is written (an early refusal of a planted or long-running writer).
- `src/gov/launch/launcher.py:1095-1115`: `StartLock()` is taken (`gate.py:55-93`, an exclusive `flock` on `~/.gov-os/machine/launch.lock`, a 300 s wait), then `check_one_writer` runs again at line 1101, before `_admit_start`. The whole block sits in `try/finally: lock.release()`, and `release` does nothing on a second call.
- `src/gov/launch/launcher.py:1178-1185`: `Keeper.begin()` (the start record, `pid` = the launcher's pid) now runs straight after `_start`, before the relay is built and before `registry.register`. The lock's first release is at 1194-1195, after the record. The other releases are `_run`'s `finally` at 1229-1230 and `launch`'s `finally` at 1115. Each is reached only after the record is written, or with no CLI started (the `_start` failure at 1174-1177, or `state["ended"]` before the start at 1165).
- `session_record.py:396-436`, unchanged in the range: a live writer is a record of this tree, `ended_at` null, a non-reviewer role and a live pid. An unreadable record refuses (fail closed). Temporary files are hidden names and are skipped.
- `docs/changes/W2-60b-CIT-E.md` §2 and §3 describe the above correctly.
- Commit roles: `253b064f5` and `692331d1d` are `Role: engineer` and touch only `src/gov/launch/launcher.py`, `tests/unit/launch/*` and the CIT-E. `fbf7273f2` is `Role: independent-test-designer` and touches only `tests/acceptance/W2-60b/{README.md,test_w2_60b_s10_s12_start_together.py}`. The merge `7bc20ff4a` (parents `692331d1d` and `fbf7273f2`) brings in exactly those two files. No implementer changed acceptance tests (MR-3, DEC-430).

## Probes (all on planted repositories and homes under the sandbox's `$TMPDIR`; head code via `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60b/src`)

**How it was planted.** Each trial gets its own home (`b.make_sandbox`), fixture project (`s.make_project`), planted CLI (`t.install_cli`, no model) and linked tree `W2-zau2` (`t.add_tree`). I used the W2-60a/W2-184/W2-60b acceptance support modules as a library for the planting only. The driver is my own: its timing, lock holder, repetitions and checks. Each `gov launch` runs in a process group of its own (`t.start_launch`).

### P1: F1's reversal probe (`$TMPDIR/au2/probe1.py`)

- **Gaps:** an engineer launch, then a test-designer launch into the same tree after a gap of 0.0, 0.05, 0.1 or 0.2 s. The CLI sleeps 3.5 s. Five runs of each.
- **Held lock:** a third process holds `<home>/.gov-os/machine/launch.lock` (exclusive `flock`) for 4 s. The engineer launch starts, then the test-designer launch 1 s later. Five runs.

Checks each time:
- exactly one CLI start, and none while the lock is held;
- one exit 0 and one non-zero exit;
- the refusal is `LAUNCH_REFUSED`, naming the started session's id and the tree's real path;
- the session-records folder and the launch-records folder each hold only the started session's file;
- the started session's record has ended, with exit code 0.

Results at the head:
- `SUMMARY gaps: 20/20 pass`, `SUMMARY hold: 5/5 pass`.
- The refused side varied (A refused in 5 trials, B in 20), as expected when either can take the lock first.
- A sample refusal: `gov launch: LAUNCH_REFUSED: a writing session is live in the worktree …/hold-r0/home/work/W2-zau2: session 594c7f66-c9d2-47c4-9fe9-3655b6c140a0 (engineer, pid 235); two sessions that write never share a worktree (DEC-847, DEC-963, DEC-1156 (3))`.

**Control: the same probe on `git archive 2d1e751d4 src`, extracted under `$TMPDIR`.**
- gaps 0.0, 0.05 and 0.1: FAIL, 2 CLI starts, both codes 0;
- gap 0.2: pass;
- held lock: FAIL, 2 CLI starts.

So the probe reproduces F1 at the old code and shows it gone at the head.

### P2: no new fail open in the range (`$TMPDIR/au2/probe2.py`, `$TMPDIR/au2/inproc.py`)

| Probe | Result |
|---|---|
| SIGINT while waiting for a held start lock | Was waiting, no CLI. `KeyboardInterrupt` in `StartLock.__init__`; the process dies by signal (exit −2). 0 CLI starts, no session record, no launch record. Once the holder ends the lock is free, and a follow-up writer launch starts (exit 0). |
| SIGTERM while waiting for a held start lock | Exit −15. 0 CLI starts, no records. Lock free; the follow-up writer starts. |
| SIGINT between the CLI's start and the start record (in-process, a wrapper sends the signal at `Keeper.begin` entry) | `launch` returns 130. One record, `exit_code` 130, ended. Lock free right after. The follow-up writer starts. |
| Same with SIGTERM | 130, record 130 ended, lock free, follow-up starts. |
| A refusal under the lock (second `check_one_writer` refuses) | Exit 1, `LAUNCH_REFUSED`. No CLI, no session record, no launch record. Lock free in the same process right after. |
| The CLI cannot start (`_start` raises `OSError`) | `LAUNCH_REFUSED: the CLI … cannot be started (DEC-205)`. No records. Lock free. |
| An exception under the lock (`_admit_start` raises `RuntimeError`) | The exception propagates. Lock free. No CLI, no records. |
| `independent-auditor` launched while an engineer is live in the tree | Both start (2 CLI starts, 2 records); both exit 0. |
| A normal session exiting 5 | Launch exit 5; record `exit_code` 5, ended. |
| SIGINT to a running launch | Launch exit 130; record 130, ended; lock free. |
| S5: `.gov-runtime/sessions` is a file | Launch exit 3 (the session's own); the CLI started; one stderr line naming the record and "the session's exit code is kept (DEC-392)". |

In the two "signal before begin" rows, the planted CLI was ended by DEC-392's SIGTERM before it logged its call. The process had started (`Popen` returned), and its record was written and ended. That is the intended order.

### P3: the ticket's tests, through the heavy slot

`heavy_slot.sh python3 -m pytest tests/unit/launch/test_session_record.py tests/unit/launch/test_session_record_launch.py tests/unit/launch/test_session_record_relay.py tests/unit/telemetry/test_sessionlog_w2_60b.py tests/acceptance/W2-60b -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, with `HOME` set to the empty scratch home.

Result: **201 passed, 2 failed, 3 deselected**.
- The 2 failures are the known `--tests-worktree` cases (`test_s10_tests_worktree_makes_the_tests_worktree_on_its_own_branch_at_the_ticket_s_head`, `test_s10_tests_worktree_refuses_while_its_branch_exists`; `unrecognized arguments: --tests-worktree`), which is round 1's F5.
- The 3 deselected cases are deselected by the repository's own configuration even with no `-m`/`-k`, so the EMG exclusion left out nothing more.
- The new acceptance cases (`test_w2_60b_s10_s12_start_together.py`, all six) and the new unit cases (`[barrier]`, `[held]`, the reviewer case, the SIG_IGN case) pass.

### The signal unit cases (judgement 3)

`_run` keeps a signal its caller ignores ignored (`launcher.py:1148-1149`, from W2-56). A `&` job of a non-interactive shell inherits SIGINT as `SIG_IGN`, so the old case's `raise_signal` never reached the launcher. The stand-in then returned `raise_signal`'s `None`.

The change sets the caller's own handler (`_caller_handles`) and makes the stand-in return an int. A real `Popen.wait()` always returns an int. The new case `test_a_signal_the_caller_ignores_stays_ignored_and_the_session_s_own_code_is_returned` pins the ignored path: the session's own code is returned and recorded, and the caller's `SIG_IGN` is given back.

The relay case's added `_caller_handles(signal.SIGINT)` fixes the same test-side inheritance. The product's handling is unchanged in the range, and P2's real-process SIGINT probe gives 130 with the record at 130. The change fixes the test and hides no product defect.

## Also noted (not a finding, unchanged by the range)

A SIGINT while a launch waits for the start lock ends `gov launch` with a `KeyboardInterrupt` traceback and death by signal, not 130. No CLI starts and nothing is written (fail closed). `StartLock()` sits where it was before the range, and CIT-E §2 states this behaviour.

## Findings of this round

None. F1 is reversed (P1 and the control above).

Classification of findings, on one line: 0 blocking; F1 resolved; rows F2-F8 kept from round 1, unchanged by the range.

## Round 1's rows, kept (the range does not change them)

- F2 (success-10, success-12): a writer whose start record cannot be written is invisible to the one-writer check. Ordinary work: no, because it needs a permission accident on `.gov-runtime/sessions/` alone. Consequence: fails open. A Wave 3 row. The range moves `Keeper.begin` earlier but does not change S5's swallowing.
- F3 (success-7): the role-file reading depends on two headings and a name prefix. Ordinary work: no. Consequence: other. A Wave 3 row (CIT-E §9).
- F4 (success-4): the window is measured only from the result line; an interactive session records `not_measured`. Ordinary work: yes. Consequence: other. A row.
- F5 (success-10): `gov launch --tests-worktree` is not wired (`src/gov/launch/command.py` is outside the ticket's paths; CIT-E §7). Ordinary work: yes. Consequence: other. Known open, with the CTO. Its 2 acceptance cases are still red (P3).
- F6 (success-1): one 429 written in both forms counts twice. Ordinary work: yes. Consequence: other. A row.
- F7 (failure-2, success-1): a sub-agent with no plain model puts a null in `subagents.value.models`. Ordinary work: yes. Consequence: other. A row.
- F8 (success-7, out of scope): a sixth role launches, but the product guard refuses its writes until it joins `KNOWN_ROLES`. Ordinary work: yes. Consequence: other. A row.

**success-10 stays fail; success-12 moves to pass.**
- success-10 keeps `fail` because its `--tests-worktree` half is not delivered (F5, two acceptance cases red), not because of a blocking finding. Under DEC-1010 F5 does not block, since its consequence is "other". With F1 resolved, READY is computed from the findings below and nothing blocks.
- success-12 moves from fail to pass: F1 is resolved, and its remaining row F2 is "ordinary work no".

What would reverse this round's pass:
- a re-run of P1 at this head, or a later one, showing two CLI starts for two writing launches into one tree at any gap or under a held lock;
- any path that gives the start lock back after a CLI has started but before its start record is written;
- a released lock missing on a refusal, an exception or a CLI that cannot start.

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-2", "verdict": "pass", "findings": []}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-5", "verdict": "pass", "findings": []}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "success-9", "verdict": "pass", "findings": []}, {"kpi": "success-10", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-11", "verdict": "pass", "findings": []}, {"kpi": "success-12", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-3", "verdict": "pass", "findings": []}]}
```

task: DAEO-ecac (W2-60b), review round 2 (au-2), the last under DEC-1010
status: done. Judgement pass; F1 reversed; no new finding; 0 blocking.
work_completed: Step 0. Read the range (launcher.py, gate.StartLock, session_record, the CIT-E, the unit and acceptance diffs, the commit roles). P1: 20 gap trials and 5 held-lock trials at the head, plus a control at 2d1e751d4. P2: signals during the lock wait and between the CLI's start and the record; lock release on a refusal, an exception and a CLI that cannot start; the reviewer with a live writer; exit codes 5 and 130; S5. P3: the ticket's unit and acceptance tests through the heavy slot. Judged the signal unit cases' change.
files_changed: none in any worktree. Scratch only under the sandbox's $TMPDIR/au2 (probe1.py, probe1_old.py, probe2.py, inproc.py, outputs, planted runs, an extracted old src). Step 0(b) wrote one blob to the object store and refreshed the index, as step 0 requires.
evidence: launcher.py:1078-1115 and 1165-1230; gate.py:55-93; session_record.py:325-436; P1 "SUMMARY gaps: 20/20 pass", "SUMMARY hold: 5/5 pass"; control at 2d1e751d4: 3 of 4 gaps and the held lock FAIL with 2 CLI starts; the P2 table; P3 "2 failed, 201 passed, 3 deselected".
tests: P3, 201 passed and 2 failed (the known F5 `--tests-worktree` cases). The six new start-together acceptance cases and the four new unit cases pass. Nothing was left out by the EMG exclusion (the 3 deselected are deselected by the repository's own configuration).
discoveries: SIGINT during the start-lock wait ends gov launch by KeyboardInterrupt (death by signal, not 130), with nothing started or written. This is unchanged by the range and stated in the CIT-E. The heavy slot was full for several minutes, so P1 and P2 (two light launches at a time) ran outside it; only pytest took a slot.
risks: My first `find /` (stopped within its first 120 s) may have listed or stat'ed folders under /home/usain/gov-os-eval/. It printed nothing, matched nothing and read no contents; reads of the hidden and memory-verdict folders are denied by the sandbox. Reported here for the lead and the CTO. No product risk found in the range.
lessons: Find a brief with Glob or Grep scoped to the repository's own folders, never a filesystem-wide `find`. A `-not -path` filter does not stop `find` from going into a folder.
proposed_decisions: none.
unresolved: F5 (`--tests-worktree`, command.py outside the ticket's paths) is still open with the CTO; success-10 stays fail on that half only. Rows F2, F3, F4, F6, F7 and F8 go to Wave 3 or stay rows as triaged in round 1.
recommended_next_action: The lead commits this record as docs/probes/DAEO-ecac/PR-DAEO-ecac-r2.md. F5 goes on with the CTO as already planned; this round needs no further review.

```
$ git -C /home/usain/gov-os-worktrees/W2-60b status --short
```
(empty output, exit 0)
