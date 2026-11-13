---
type: probe
task: DAEO-fd0p
reviewer_session: 4d84e10e-d2b1-4380-a236-c36ba5f0e2b0
implementer_session: "eng-1 81ed5bbb-9c52-4b3a-9da9-c392927f48e5 (eb6d0cc07643)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: eb6d0cc076435ca12cac6d8a4cab47f236b82d69
decisions_applied: [DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1153, DEC-1010]
---

# Probe record: W2-160 (DAEO-fd0p) `gov wait` and the helper watch, STANDARD review, round 1 of 2 (DEC-1010)

- **Round 1** (reviewer session 4d84e10e-d2b1-4380-a236-c36ba5f0e2b0, independent-auditor, Opus high, read-only)
  probed head `eb6d0cc07643`: **pass**, 0 blocking. Every KPI line S1-S4 and F1-F4 passes. The findings are R1-1 and
  R1-3 to R1-10. The reviewer used no R1-2, so there are nine findings, though its return says ten. None of them
  fails open or loses work. R1-10 is out of scope (the ticket text). No second round is needed.
- **The lead's triage** (each row is non-blocking and is recorded as a residual, not fixed on this branch):
  - R1-1: two overlapping passes on one root write each condition twice (F3). The caller arms one watcher per root.
    Worth a follow-up fix that writes nothing beyond the three files S4 names.
  - R1-3: a zero or negative `--every` in loop mode spins or ends in a traceback. Worth a follow-up usage check.
  - R1-4: each action ignores the other action's stray arguments. A usability row.
  - R1-5: the helper's meta `description` label and single-word code fields are copied into items, as I2 and the
    reference do. Message text never is. It is the owner's call whether the label counts as a message's text under
    S4.
  - R1-6: the worker check does not read the exit file again before reporting "gone". A false alarm is possible
    in a window of microseconds, and the real code is still reported later.
  - R1-7: the digits of a pid file are joined across lines, as in the reference. `launch_worker.sh` writes one
    line.
  - R1-8: a fractional `<max-s>` exits 2, as in the reference. The wait fails closed.
  - R1-9: a worker's item names its log and the error flags, not a description of the log's last line. S4 forbids
    copying that line's text.
  - R1-10: I2 cites DEC-1140 (1)(a) for "the state file only grows". DEC-1140 does not say that. The rule stands
    by DEC-1153 (2). The CTO's decision record corrects the citation.
- **The lead's checks of the probed head `eb6d0cc07643`:**
  - `gov accept W2-160`: pass, 66 passed, 0 failed. success-1 21, success-2 9, success-3 25, success-4 11,
    failure-1, failure-2 and failure-3 3 each. F4 is the lead's check, below.
  - F4: `git diff --name-only b42bcff9e35e..eb6d0cc07643` lists 18 paths. Each one is in the ticket's
    allowed_paths or in its acceptance folder `tests/acceptance/W2-160/`.
  - The scoped verification (`lead_verify.sh`, after `rebuild_slot.sh`): 5187 tests in the parallel phase, 2 failed,
    7 skipped. The serial phase selected no entries. Both reds are outside this ticket's paths, and the lead has
    returned each to the CTO as a package:
    - `tests/unit/session_watch/test_route.py::test_the_command_is_declared_by_its_module` pins W2-159's
      single-path `ACT_PATHS`. DEC-1153 (2) adds `.gov-runtime/dispatch/inbox/**` (PKG-W2-160-ROUTE-1: a one-line
      test change on a widened path).
    - `tests/acceptance/W2-159/test_f4_scope.py::test_f4_the_branch_changes_only_the_tickets_allowed_paths`
      compares any branch with W2-159's own allowed_paths. It is green on w2/integrate and red on every other
      ticket's branch (PKG-W2-160-KNOWN-1: name it in skip_known.json).
  - `gov.__file__`: /home/usain/gov-os-worktrees/W2-160/src/gov/__init__.py.
- **Facts for the record:** S2's "as `gov launch` writes it" means `launch_worker.sh`'s `<base>.pid`, `.exit`
  and `.json` (the ticket's own facts line). `gov launch` in this tree writes no pid file.

The reviewer's return follows verbatim. Its verdict block decides.

## Round 1 (eb6d0cc07643): the reviewer's return

```verdict
ticket: DAEO-fd0p
head: eb6d0cc07643
round: 1
verdict: PASS
blocking: 0
```

**Step 0 (sandbox check):**
- **(a)** Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-fd0p` failed with `OSError: [Errno 30] Read-only file system`. No file was created.
- **(b)** `git hash-object -w --stdin` returned `1ae28402…` and `git update-index --refresh` exited 0.
- **Identity:** `GOV_TICKET=DAEO-fd0p`. HEAD is `eb6d0cc076435ca12cac6d8a4cab47f236b82d69`, which matches the brief. `git status --porcelain` was empty at the start and is empty now.
- **ps check:** nothing of mine matches ollama or llama-server, and no `gov.cli.main` process of mine is left running.

**Classification:** 10 findings. 0 are blocking. 9 are in scope (S1–S4 and the Interface) and 1 is out of scope (R1-10, the ticket text). For 5 an honest agent can hit it in ordinary work, and 5 need an unusual setup. None fails open and none loses work. Recommendation: PASS. Record the rows below; no round is needed.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "R1-8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1-7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R1-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R1-3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "R1-4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R1-6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R1-9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R1-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": [{"id": "R1-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F3", "verdict": "pass", "findings": [{"id": "R1-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "F4", "verdict": "pass", "findings": [{"id": "R1-10", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}
]}
```

## Findings

**R1-1: two passes at the same moment write every condition twice**
- **Severity:** non-blocking. In scope (F3; I2 "once each").
- **Where:** `src/gov/session_watch/helper_watch.py:208-221`.
- **Probe:** `p_conc.py` reset the state and the inbox, then started two `helper-watch --once` passes together on one planted root, 8 times. Six trials gave 5 items; trials 2 and 3 gave 10 items (every condition twice).
- **What happens:** each pass reads the state file, writes its items, then rewrites the whole state file. Nothing stops two passes that overlap from both treating every condition as new.
- **Right behaviour:** a condition is written once even when two passes overlap, and nothing beyond the three named files is written (S4 rules out a lock file).
- **Ordinary work: no**, because it needs two watchers on the same root whose passes overlap within the few milliseconds a pass takes. The caller arms one watcher per root.
- **Consequence: other** (a duplicate inbox item).
- **What would reverse it:** evidence that a session restart routinely leaves the old loop running beside a new one with their passes in step.

**R1-3: a zero or negative `--every` in loop mode**
- **Severity:** non-blocking. In scope (I2 `--every`).
- **Where:** `helper_watch.py:250`.
- **Probe:**
  - `--every -5 --max 2` ended with a `ValueError: sleep length must be non-negative` traceback and exit 1, with no named message.
  - `--every 0 --max 1` added 1583 lines to `helper-watch.log` in one second.
- **Right behaviour:** a non-positive `--every` is refused as a usage error, named, before any pass runs.
- **Ordinary work: no**, because the default is 300 and getting there takes a typo. **Consequence: other.**
- **What would reverse it:** a caller or brief that passes `--every 0`.

**R1-4: stray arguments are accepted and ignored**
- **Severity:** non-blocking. In scope (I2; the brief's probe 6).
- **Where:** `src/gov/session_watch/command.py:27-30`.
- **Probe:**
  - `helper-watch waiter --once` exited 0, and `waiter` was ignored.
  - `echo '{}' | stop-check idle --once --every 5` exited 0, and the helper-watch options were ignored.
- **Right behaviour:** each action refuses the other action's arguments with exit 2.
- **Ordinary work: yes**, because a mistyped command line is easy. **Consequence: other.** `stop-check`'s behaviour on a correct command line is unchanged.
- **What would reverse it:** none needed; this is a usability row.

**R1-5: free text in `description`, and single-word values in code fields, are copied into items**
- **Severity:** non-blocking. In scope (S4, F2).
- **Where:** `helper_watch.py:123-124` (description), `:31-39` (`_name`), `:186` (the exit file's first word).
- **Probe:** `p_hw.py` planted the canary `CANARYzz9` in a helper's meta `description` (several words), and as single words in `apiError`, `error`, a tool name, a block's `type`, `agentType`, `timestamp` and the exit file's first line.
  - The items carried `helper e1 (CANARYzz9 desc words, CANARYzz9-type)`, `API error CANARYzz9-apierror-token/CANARYzz9-error-token`, `tool_use CANARYzz9-toolname`, `assistant at CANARYzz9-ts` and `ended with exit CANARYzz9-exitcode`.
  - Canary text with spaces never got through: message content as a string or as blocks, a tool_use's `input`, an `error` object, a worker's `result`, and `is_error` / `api_error_status` (shown only as `set`).
- **Why this is not a block:** `description` is the task label from the helper's meta, not a message's text. I2 names it, and the reference does the same. Single-word values are the names and codes I2 asks for.
- **Ordinary work: yes**, because the description is always copied, by design. **Consequence: other.**
- **What would reverse it:** the owner ruling that the `description` label counts as a message's text under S4 / DEC-495.

**R1-6: the worker check has no grace re-check**
- **Severity:** non-blocking. In scope (S3 "worker gone").
- **Where:** `helper_watch.py:168-178`.
- **What happens:** the watch reads the exit file first and asks liveness second. Unlike `gov wait` (`command.py:148-150`), it does not look again after seeing the pid gone. `launch_worker.sh` moves `<base>.exit` into place and then exits (line 67). If both happen in the moment between the watch's two reads, the watch writes a false "worker gone" item. The real code is still reported later as its own condition.
- **Probe:** reasoning from the code only. The window is microseconds, so I did not try to time it.
- **Right behaviour:** before reporting a worker gone, read the exit file once more.
- **Ordinary work: yes**, but rarely. **Consequence: other** (one false alarm).
- **What would reverse it:** a measured window short enough to be negligible.

**R1-7: the digits of a pid file are joined across lines**
- **Severity:** non-blocking. In scope (S2, I1 liveness).
- **Where:** `src/gov/wait/liveness.py:28-35`.
- **Probe:** `p_wait.py` wrote a pid file holding `12\n34\n`. The wait read pid 1234 and returned `125 GONE (1234)` after 0.3 s. `pid=13` and `-13` were read as 13 and treated as alive. The reference `wait_for.sh` (`tr -dc 0-9`) does the same.
- **Right behaviour:** only the first whole number counts as the pid.
- **Ordinary work: no**, because `launch_worker.sh` writes one line with `>` (lines 52 and 185). **Consequence: other.**
- **What would reverse it:** a launcher that appends to the pid file instead of overwriting it.

**R1-8: a fractional or padded `<max-s>` is refused as "not a number"**
- **Severity:** non-blocking. In scope (S1, I1).
- **Where:** `src/gov/wait/command.py:133`.
- **Probe:** `1.5` and `" 3"` both gave `wait: <max-s> is not a number` and exit 2.
- **Why this is not a block:** I1 makes "not a number" exit 2, and 1.5 is a number. The reference does the same, and the wait fails closed.
- **Ordinary work: yes. Consequence: other.**
- **What would reverse it:** I1 read as "whole seconds only".

**R1-9: a worker's item does not describe the log's last line**
- **Severity:** non-blocking. In scope (S3 "names the worker's log and its last line").
- **Where:** `helper_watch.py:175-187`.
- **What happens:**
  - The "gone" item names the log path only: `no exit file; its log: …`.
  - The "error" item gives only the error flags from the last JSON object (`is_error set, api_error_status set`), or `no error in its JSON result`.
  - Nothing names the log's last line.
- **Probe:** the R1-5 run's `-5.txt` item.
- **Why this is not a block:** that line usually holds the result's text, which S4 forbids copying. The names-only form matches S4 and the reference.
- **Right behaviour (optional):** the last line's type and subtype, as names.
- **Ordinary work: yes. Consequence: other.**
- **What would reverse it:** the owner reading S3 as requiring a description of the last line.

**R1-10: I2 cites the wrong decision for the state file's rule**
- **Severity:** non-blocking. Out of scope (the ticket text, not the code).
- **What is wrong:** I2 says the state file "only grows (DEC-1140 (1)(a))". DEC-1140 (1)(a) is about usage and RUBRIC-2 (register line 14608), and DEC-1140 says nothing about a state file. The rule itself stands, because DEC-1153 (2) accepted I2 word for word.
- **Right behaviour:** the decision record fixes the citation.
- **Ordinary work: no. Consequence: other.**
- **What would reverse it:** another DEC-1140 text that does state the rule.

## Probes and results

- **F4:** the merge base with `w2/integrate` is `b42bcff9e`. `git diff --name-only` lists 18 paths. All are inside the ticket's `allowed_paths`, except `tests/acceptance/W2-160/*`, which belongs to the test designer. Pass.
- **`gov wait`, exit-file contents (with `<max-s>` 1):**

  | exit file | exit code | line printed |
  |---|---|---|
  | `abc` | 2 | `holds no exit code: 'abc'` |
  | empty line | 2 | |
  | two blank lines | 2 | |
  | `-1` | 2 | |
  | `256` | 0 | `DONE exit 256` (code % 256, as I1 says) |
  | `3` | 3 | |
  | ` 7 ` | 7 | |
  | `1 2` | 12 | (spaces removed, as in the reference) |

  A trailing newline is handled. No case printed `invalid choice`.
- **`gov wait`, `<max-s>` values:**
  - `0` gave 124 at once.
  - `-1`, `x`, `1.5` and `" 3"` gave exit 2.
  - `9999` printed `wait: <max-s> 9999 capped at 570` on stderr straight away. It then waited the full 570 s, and I stopped that run through TaskStop.
  - `2` against a live pid gave `124 RUNNING after 2s` in 2.04 s.
- **`gov wait`, liveness:**
  - A killed and reaped job, with a second `sleep 300` of the same name still running, gave `125 GONE` in 0.29 s (poll period 0.5 s).
  - A zombie (state `Z`) gave 125 in 0.29 s.
  - A job that wrote its exit file and exited at once gave `0 DONE` (the grace re-check works).
- **`gov wait`, pid-file forms:** a pid file holding no number, an empty one, or 99999999 (above 2^22) each counted as no pid, and the wait ran to its bound (124).
- **`gov wait`, a pid reused by an unrelated live process:** the wait holds to the bound and returns 124, never GONE. I1 settles this: liveness is by pid alone, and the 570 cap still ends the wait.
- **Tail:** checked against the code and the acceptance cases. `GOV_WAIT_LOG` comes first, then the first of `.log`, `.json`, `.txt` that exists. A JSON log gives `session_id`, `is_error`, `turns` and the last 4000 characters of `result`, then `.summary`.
- **No process-name match:** a grep for `pgrep|pkill|killall|pidof|psutil|proc.sh|/cmdline|/comm|"ps"|ps -|subprocess` over `src/gov/wait/*.py` and `helper_watch.py` found nothing.
- **Helper watch, conditions, once only and footprint:**
  - Five planted conditions gave five items, named `-helper-watch.txt` and then `-2` to `-5`, each opened with `x`.
  - A second pass in a new process (the restart case) wrote no item. Only the state file and the log changed; the state's content stayed the same.
  - The filesystem snapshot covered the root, HOME, the helpers folder and the workers. Only the inbox items, `helper-watch-state.json` and `helper-watch.log` were new or changed.
- **Truncated state file:** an empty state file made the next pass send all 5 items again (the lead's known item, confirmed).
- **Loop:**
  - `--every 1 --max 3` printed `HELPER_WATCH ended after 3 s; 0 item(s) written; re-arm it` after 3.1 s, exit 0. With `GOV_SESSION_WATCH_NOW` set, `--every` and `--max` still sleep real time.
  - `--max 0` gives one pass, then the ended line.
  - `pid_globs: 5` gave exit 1 with `governance/project/session-watch.yaml: pid_globs: a list of non-empty texts is needed, not 5`, and wrote nothing.
- **stop-check:**
  - W2-159's acceptance suite and `tests/unit/session_watch` gave 151 passed and 2 failed, both the lead's known items.
  - `stop-check` with no check still exits 2 (now with a named message).
  - The extra `ACT_PATHS` entry only declares a path. Nothing in `src/gov` enforces it at run time, so `stop-check`'s behaviour is unchanged.
- **Robustness, from the code:**
  - A transcript that cannot be read is skipped.
  - A meta file that cannot be read counts as `{}`, which means not finished, so the helper can be reported stalled.
  - A line that is not JSON is skipped.
  - An empty exit file with a gone pid is reported as "worker gone", consistent with I2.
- **Sound:** no message text with spaces reached any output; the `<synthetic>` exception works; the inbox, state and log paths are exactly I2's; the helpers folder follows I2's naming rule; with no session file, no helper is looked at; the window applies to both transcripts and pid files; the exit file's mtime rule applies only to the error condition.

## The lead's known items

- **`test_route.py:19` red:** confirmed. The only cause is the decided extra entry in `ACT_PATHS`. Sending the one-line change to the CTO as a package is the right route. Not blocking.
- **W2-159's `test_f4_scope` red:** confirmed. It checks W2-160's paths against W2-159's own `allowed_paths`, so it fails structurally on any later branch. Not blocking.
- **State file written in place, and a corrupt file read as empty:** confirmed by probe (5 items re-sent once). The same weakness lies behind R1-1. Not blocking.
- **An empty exit file counts as not written:** consistent with S1 ("non-empty") and I2. Correct.
- **The `**` glob does not enter hidden folders:** confirmed in the code. `launch_worker.sh` writes under `.gov-runtime/scratch/lead/log/`, which has no hidden folder below `.gov-runtime`, so nothing is missed in practice. Not blocking.
- **A pid above 2^22 counts as no pid:** 2^22 is Linux's highest possible pid. Correct.

task: DAEO-fd0p
status: done. Round-1 review complete: PASS, 0 blocking.
work_completed: sandbox and identity checks; read the ticket, I1/I2, the diff, the acceptance README and support code, the reference scripts and `cli/main.py`; probed `gov wait` (exit-file and `<max-s>` inputs, liveness, zombie, pid-file forms, the cap) and the helper watch (canary in fields beyond the acceptance plant, a second pass and a restart, filesystem snapshot, concurrent passes, a truncated state file, the loop, the configuration error, parser edges); ran W2-159's acceptance and unit suites.
files_changed: none (all probes ran under `$TMPDIR/rev`; the tree is clean)
evidence: probe scripts `$TMPDIR/rev/{w.sh,p_wait.py,p_hw.py,p_conc.py}`; outputs quoted above.
tests: W2-159 acceptance plus `tests/unit/session_watch`: 151 passed, 2 failed (the two known items). The filter `-m "not local_only" -k "not real and not green_here and not time_limit"` was used; `test_f4_scope` was re-run alone to read its message. W2-160's own suite was not re-run (the lead ran it).
discoveries: two overlapping passes duplicate items (R1-1); a non-positive `--every` crashes or spins (R1-3); I2 cites the wrong decision for the "only grows" rule (R1-10).
risks: duplicate inbox items if two watchers run on one root, or after a crash during the state write; the helper's `description` label is copied into items (R1-5).
lessons: a `<max-s>` probe above 570 waits the full cap; probe the cap's stderr line with a short timeout, or do not wait for it to end.
proposed_decisions: none
unresolved: whether the owner reads the meta `description` label as a message's text under S4 (R1-5); fixing the DEC-1140 citation in I2 (R1-10).
recommended_next_action: land on PASS once the CTO's `test_route.py` package is applied; record R1-1 to R1-10 as rows (R1-1 and R1-3 are the ones worth a follow-up fix); the decision record fixes R1-10.
guard_refusals: none
