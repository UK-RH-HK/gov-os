# D-10's red-fix list: the review of W2-96's planted launches reaping their process groups (W2-96, DAEO-ouet)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-96-review.md`; branch `w2/W2-96-d10-tests` at `65fa76dc3`; reviewer log `/home/usain/gov-os-worktrees/W2-96-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-96-review.json`.
- verdict.py: READY (no blocking finding; F1-F5 rows, none in ordinary work).

**Sandbox check (Step 0, `EMG-d4b-launched.md`): passed.**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-96','w').write('x')"` failed as required: `OSError: [Errno 30] Read-only file system`.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. Each Bash command here runs in its own PID namespace, so this only sees that namespace.

- **task:** independent review of W2-96's D-10 red-fix (DAEO-ouet), `16f4958c5..65fa76dc3` (round 1 `6bcbbcdd5`, round 2 `65fa76dc3`). KPI `w2-96-reap`.
- **status:** DONE. Verdict **pass**: five findings, none blocking (all Wave 3 rows).
- **work_completed:** I read the diff, `w2_96_reap.py`, the four changed test files and round 1's version. I also read gov's runner (`src/gov/accept/runner.py:155-377`), the entry point (`src/gov/cli/main.py:263-264`) and the incident record. I checked the trailers with git's trailer parser and ran all 98 cases with 4 workers and serially.
- **files_changed:** none. The only write was step 0's git blob.
  - Every run used `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`.
  - The ignored `__pycache__` folders in the worktree are dated 01:01–01:20 UTC, before my runs.
- **evidence:**
  - Changed files (`git diff --stat`): 5 files, 374 insertions, 65 deletions.
  - `/proc/sys/kernel/pid_max` is 4194304.
  - gov strips `PYTHON*` variables from its pytest's environment (`runner.py:333`).
  - The subreaper is set before pytest starts (`runner.py:338`).
  - pytest is started through `subprocess.Popen` looked up at call time (`runner.py:339`).
  - Scratch usage: 1.6 MB and 389 inodes, then removed.
- **tests:**
  - **First run (environment, not the revision):** with the brief's recipe (empty HOME plus `PYTHONUSERBASE`), 29 failed and 29 passed out of 58.
    - Every gov run reported `error_kind: crash`, because gov strips `PYTHONUSERBASE` and the inner pytest could not import pytest.
    - Only 58 of 98 cases were collected (see discoveries).
  - **Corrected runs:** with a scratch HOME exposing only `~/.local/lib` (no reranker environment) and `--optin breadth`:
    - 4 workers: **98 passed in 24.00 s**.
    - Serial (`-p no:xdist`): **98 passed in 84.21 s**.
  - The real-model exclusion flags (`-m "not local_only" -k "not real and not green_here and not time_limit"`) left nothing out (98 of 98).
  - "Nothing left over" is judged by the cases' own checks: every teardown asserts the reaper exited 0, and the three proof cases check directly. My runs' leftovers can't be seen from outside their namespace.
- **discoveries:**
  1. The brief's HOME recipe can't work for gov-accept tests: gov drops `PYTHON*` variables before starting its pytest, so `PYTHONUSERBASE` never arrives. A scratch HOME with `.local/lib` linked to the user site works.
  2. Without `--optin breadth` only 58 of the 98 W2-96 builder cases are collected (`tests/optin-lifted-breadth.txt:1185`, `rep: tests/unit/accept/`). A default landing run skips the other parametrised rows.
  3. Cases that run gov inside the worker are not under the reaping. This revision didn't touch them. If the worker dies mid-run, their pytest group lingers up to 60 s (the planted tests' longest sleep).
  4. `w2_96_reap` lists `/proc` outside any `try`, so on a system without `/proc` every reaped case errors at teardown. CI is `ubuntu-24.04` only, so this doesn't arise in practice.
  5. The ignored caches still hold bytecode of the designer's deleted mutation files (`test_w2_96_zz_mut`, `zz_orig`). Harmless.
- **risks:** F1–F5 below, none blocking.
- **lessons:** compare the number of collected cases with the designer's count. The opt-in rule quietly removed 40 of 98.
- **proposed_decisions:** none.
- **unresolved:** none.
- **recommended_next_action:**
  - READY: take the revision as it is.
  - File F1–F5 as Wave 3 rows.
  - Fix the gov-accept test recipe in the EMG briefs (discovery 1).

## Answers to the checks

**1. What the cases test is unchanged: yes.**
- **Signals:** every signal a case sends still goes to gov's pid alone: `gov.send_signal` in r2, r9/r12, r11, r14 and r16, and `os.kill(gov.pid, SIGSTOP)` in the new case. No case calls `killpg` on gov.
- **gov's own handling still decides.**
  - On the accept path gov reads only signal dispositions, its own children, its subreaper flag and its pytest's own group.
  - It reads no session, process-group or terminal state. Those calls appear only in `gov launch`, `pause` and `release`.
  - So a new session changes nothing gov does.
- **Inherited ignores (r11):** CPython calls `setsid()` before `preexec_fn`, and an ignored signal stays ignored across exec, so r11 is unchanged.
- **SIGHUP:** gov now leads its own session but has no controlling terminal, so its exit sends no SIGHUP.
- **A terminal's ctrl-c:**
  - No case asserts one. The ctrl-c case sends SIGINT to gov's pid, which is exactly what a terminal would deliver to gov.
  - Only the test harness changes: a ctrl-c at the outer run no longer reaches the planted gov directly. Teardown still runs after KeyboardInterrupt, and if the process dies the reaper acts.
- **r2 now goes through the wrapper** instead of `python -m gov.cli.main`. It runs the same `main(argv)`, and the recording patch only appends pids.
- **review3's file-removal patch** now applies before gov is imported. It only changes calls that pass `dir_fd`, so imports are unaffected.
- **No assertion was removed or changed.** The removed lines are imports, the old per-file launchers, launch lines, signatures and docstrings. The fixture adds one assertion (the reaper exits 0).

**2. The reaping is sound in ordinary work.**
- **Can it miss a group?**
  - A start race exists, a few milliseconds wide (F1).
  - A pytest gov has started but not yet recorded is still found by walking gov's descendants. gov is alive at that point because it doesn't die with the case.
  - A double-forked process that stays in a known group is reached by `killpg` wherever it was reparented.
  - Descendants that start their own session are found while they or gov (the subreaper) live. I traced the third proof case and it is red against round 1's direct-children walk.
  - The reaper misses only groups that appear after gov has died or after the kill sweep (F4).
- **Can it kill something not its own?**
  - Every target is a recorded pid, or the group of a descendant of one, read from `/proc` (`task/*/children`, `stat`) and `getpgid`. Nothing is matched by name.
  - The reaper skips its own group.
  - A descendant of gov can't join the worker's group, and other workers' processes are never in this tree.
  - Pid reuse isn't checked (F3), but can't happen in practice here.
- **If the reaper itself is killed:**
  - Killed on its own while the case goes on: the case errors at teardown, and the fallback kills gov by pid only (F5).
  - A group or session stop misses it, since it's in its own session.
  - A whole-tree stop takes gov's run with it.

**3. No new hang, and one bounded new leak.**
- **The reaper is bounded:** SIGTERM, up to 3 s, SIGKILL, up to 20 s more, with a deadline checked every pass, then exit 1 if anything is still alive.
- **The finaliser is bounded:** it waits at most 53 s for the reaper, then kills it, and at most 10 s per gov, then kills gov. It never waits on a group itself.
- **A group that never empties** (stuck in disk wait, or not signallable) makes the reaper exit 1 and the case fails. Nothing hangs.
- **The pipe:** no child inherits the pipe's write end, and nothing in these files forks without exec.
- **Cost:** about one extra Python process and three `/proc` scans per case.
- **Leak:** the one new leak is F2.

**4. Trailers and paths: correct.**
- Both commits carry `Task: DAEO-ouet`, `Implements: DEC-1109, DEC-866`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-866: …` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. git parses all five as trailers.
- Only `tests/unit/accept/test_w2_96*.py` and `w2_96_reap.py` changed.

## Findings

**F1 – gov's pid is recorded only after the launch call returns** (`w2_96_reap.py:151-156`).
- If the case's process dies, or a KeyboardInterrupt lands, between gov's fork and that write, gov is never recorded. The reaper then finds nothing.
- gov keeps running with its pytest group for up to its default 1800 s timeout, which is the incident's shape.
- Possible hardening: record the pid in the child before exec, and have the reaper re-read the record during its grace period.

Ordinary work: no, because the case must die inside a window of a few milliseconds per launch. A failing case, the incident's actual trigger, goes through the finaliser.
Consequence: other
Scope: in

**F2 – the SIGKILL proof case's holder is not reaped** (`test_w2_96_run2.py:256-269, 318-326`).
- The holder is a plain child in the worker's own process group and ends in `time.sleep(600)`.
- xdist kills busy workers by pid at teardown, which is how the incident's govs were orphaned. If that happens in the 2–3 s the holder lives, the holder survives up to about 10 minutes, and so do its gov and blocked pytest.
- A failing case does kill the holder in its `finally`.
- Possible hardening: `PR_SET_PDEATHSIG` in the holder, or a stdin pipe from the case instead of the sleep.

Ordinary work: no, because the worker must be killed by pid in those 2–3 s.
Consequence: other
Scope: in

**F3 – recorded pids are trusted without an identity check** (the reaper's `groups()`).
- A pid that has exited and been reused would have its group signalled.
- Possible hardening: record each pid with its start time from `/proc/<pid>/stat` and skip a mismatch.

Ordinary work: no, because `pid_max` is 4,194,304 with sequential allocation. Reuse within a case plus 23 s would take about 4 million process creations.
Consequence: loses work
Scope: in

**F4 – groups that appear late or detached are missed.**
- Groups first seen after the SIGKILL sweep are waited on but never signalled. The reaper exits 1, so the case fails visibly.
- A descendant that started its own session and was moved under init after gov died isn't found at all.

Ordinary work: no, because W2-96's forkers stay in their own group, the one-off new-session processes start early, and gov keeps every orphan in view while it lives.
Consequence: other
Scope: in

**F5 – the finaliser's fallback signals only gov's pid** (`w2_96_reap.py:195-200`).
- If the reaper has died or overrun, `gov.kill()` leaves gov's pytest group behind. The `code == 0` assertion still reports it.
- Possible hardening: use `os.killpg`.

Ordinary work: no, because the reaper must be killed on its own while the case continues.
Consequence: other
Scope: in

```verdict
{"kpis": [{"kpi": "w2-96-reap", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
