# Brief: independent test designer, DAEO-neam (W2-45), run 4 (review round 1's fix batch, and the W1-40 revision)

You are a fresh independent test designer (MR-3). Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-45-tests` on branch `w2/W2-45-tests` (DEC-963), head
`0098b58d5`. Review round 1 found that the ticket's work fails two behaviours its KPI lines S1 and S5 name. You write
acceptance cases for those behaviours, red on this head (the base-red rule), and make one revision of an older test
that the owner allowed (DEC-1153 (1)).

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-neam`), `printenv TMPDIR` (call it
  T below; write it out literally in every command), and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect
  `/home/usain/gov-os-worktrees/W2-45-tests`, `w2/W2-45-tests`). If anything differs, stop and say so.
- Everything in the foreground; return only after your commits exist. No `git checkout` of another commit, `reset`,
  `clean`, amend, rebase, merge, push or tag.
- **Write only:** `tests/acceptance/W2-45/**` (new files, and additions to `w2_45_support.py`, `conftest.py` and
  `README.md`; no existing case changes) and the one W1-40 revision below. Nothing else.
- **Never read this ticket's implementation**: `src/gov/check/runner.py`, `src/gov/check/commands.py`,
  `src/gov/decisions/checker.py`, `tests/unit/check/`, nor the worktree `/home/usain/gov-os-worktrees/W2-45`. The
  ticket's Interface and the behaviours below tell you what the code must do. For the decision checker's rules (what
  a finding is), read its other tests and docs: `tests/acceptance/W1-26/`, `tests/unit/decisions/`, the existing
  `tests/acceptance/W2-45/` cases, and `docs/` — not `checker.py`.
- `/tmp` is read-only in the sandbox: scratch goes under T. Every pytest goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, e.g.
  `env TMPDIR=T/w2-45-td4 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-45-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-45 -q -s -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (one command, no `&&`, no pipe; `mkdir -p T/w2-45-td4` first). Never `--basetemp`. A slot, memory or CPU gate
  refusal is a wait: run it again later; it does not count as a refusal.
- No `gov retrieve`, no `gov context`; Read and Grep, and search again once in other words. Grep the register only by
  id. No here-document, no backticks, no `bash -c`, no long inline `python3 -c`; a script longer than a line goes under
  T and you run it with `python3 <file>` / `bash <file>`.
- No test, class or file name holds `real`, `green_here` or `time_limit` (the whole-folder run deselects those words).
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another form (DEC-1142 (9)).
- Install nothing; no subagents that write; never ask the owner. Hashes: 12 digits.

## What the accepted Interface says (the ticket, P-W2-45-1; read the ticket text in `.gov-runtime/scratch/brief/` if copied, else as quoted)

- Item 2: every check result has `elapsed_s` (wall seconds) and `time_limit_s` (its `timeout-seconds`, else 60); the
  runner's result has top-level `time_limit_s` 60.
- Item 3 (S1): the budget of the decision checker is core-authority's time limit, 60 s. A planted repository of 200
  decision records and 20,000 commits holding the real core-authority declaration: `gov check --json` ends, and
  core-authority's entry has `elapsed_s` < `time_limit_s`.
- Item 5: an absent tool of a hard-block check is RED; the built-in `openspec-validate` too (`OPENSPEC_ABSENT` RED).
- Item 7 (S5): a check past its limit is stopped with its whole process group (it runs in its own session) ->
  `CHECK_TIMED_OUT`.
- The existing cases in `tests/acceptance/W2-45/` (td-1, td-2) and `w2_45_support.py` (`Project`, `repo_with_decisions`,
  `Project.check`, `Project.declare`, `make_path`) are yours to reuse. S1's existing fixture is a linear history.

## Batch A: S1 on a history with merges (review finding F1, as a described behaviour)

Behaviour: on a planted repository of 200 decision records and 20,000 commits **where about one commit in six is a
merge** (about 3,300 merges; ordinary branch work: side branches whose commits touch `src/` files and, now and then,
revise a decision, merged back into `main`), `gov check --json` holding the real core-authority declaration ends,
and core-authority's entry has `elapsed_s` below `time_limit_s` (60), both printed in the message; it does not time
out and does not fail (`CHECK_TIMED_OUT`, `CHECK_FAILED`, `DECISION_CHECKER_ERROR`, `DECISIONS_GIT_FAILED` absent).
At this head the reviewer measured 132.8 s for such a history, so the case must be red here (core-authority
`CHECK_TIMED_OUT`). A fixture guard checks the repository's shape (`rev-list --count HEAD` 20000, merges counted
with `rev-list --merges --count HEAD` between 3,000 and 3,700, 200 records).

Findings must not change on that history: if every decision in it is set and revised by owner commits, add one guard
case that the decision checker still reports what it must on a merge history, at a smaller scale, built from the
rules the W1-26 / unit decision tests state (for example a decision whose ACTIVE status is set on a side branch by a
commit those rules do not count as approval, then merged: still reported). Only if you can state the rule from those
tests; otherwise leave it out and say so.

Build the history with `git fast-import` (it takes `merge :<mark>` lines) as a new function beside
`repo_with_decisions` in `w2_45_support.py`; keep the build to a few seconds. Put the cases in a new file
`tests/acceptance/W2-45/test_s1_decision_checker_merges.py`. The case is load-sensitive, like S1's.

## Batch B: S5, the check's group is stopped however the runner ends (findings F2 and F3)

Behaviour F2: when `gov check` is interrupted while a check runs (SIGINT to the `gov check` process, as Ctrl-C sends to
it alone when it is not the terminal's foreground group), the check's whole process group is stopped: no process of
the check (the shell, and a grandchild it started) is left running a few seconds after `gov check` has ended. At this
head the check's shell and grandchild keep running (the check runs in its own session), so the case is red here.

Behaviour F3: a check declared with a huge `timeout-seconds` (3000000) that starts a long grandchild: whatever
`gov check` ends with (at this head an `OverflowError` traceback; that traceback is a known row, W2-L167, so do not
assert the exit form), no process of the check is left running a few seconds after `gov check` has ended. Red here.

How (a suggestion; yours to design): the planted check writes its own pid and its grandchild's pid to files in the
project, then sleeps (e.g. `sleep 300` in the background plus `wait`); the test starts `gov check --json` as a
`subprocess.Popen` with the same env `Project.check` builds, waits until the pid files exist, sends SIGINT (F2),
waits for `gov check` to end (bounded), then polls up to about 5 s that each pid is gone (`os.kill(pid, 0)` raising
`ProcessLookupError`, or `/proc/<pid>` absent / a zombie). The test must clean up anything it started even when it
fails (kill the recorded pids in a `finally`). Put the cases in a new file `tests/acceptance/W2-45/test_s5_group_stopped.py`.

## Batch C: the W1-40 revision (DEC-1153 (1), the owner)

In `tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py`,
`test_the_job_names_the_openspec_check_unmeasured_and_fails_where_openspec_is_not_on_the_runner`:
- line 49 `assert done.returncode == 0 and statuses.get(OPENSPEC_CHECK) == "YELLOW", (` becomes
  `assert done.returncode != 0 and statuses.get(OPENSPEC_CHECK) == "RED", (`, and the f-string message on line 50
  says the same: the fixture does not hold when gov check without openspec is not a non-zero exit with the openspec
  check RED;
- the docstring (lines 46-47) says ``gov check`` itself reports the absent tool as RED and ends with a non-zero exit
  (P-W2-45-1 item 5), keeping its second sentence (the job does not take it for green).
Nothing else in the file changes. Run that file alone through the slot (with `GOV_TESTS_OPTIN=lifted,breadth` in the
env if cases are deselected) and report counts: all its cases should pass at this head.

    git commit -m "W1-40 test: gov check without openspec is a non-zero exit with openspec-validate RED" --trailer "Task: DAEO-neam" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Rewrite-Reason: P-W2-45-1 item 5: OPENSPEC_ABSENT is RED" -- tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py

## README and commits for A and B

Add one map row per new case to `tests/acceptance/W2-45/README.md`'s map (the KPI id S1 or S5 first, then the node id,
then the expected red reason at this head; `gov accept`'s parse_map reads those rows: copy the existing rows' form).
Run `tests/acceptance/W2-45` whole through the slot: the new cases red for the stated reason, every older case as
before (32 passed). Then commit A and B (one commit, or one each):

    git commit -m "W2-45 tests: S1 on a history with merges; S5 the check's group stopped on interrupt and on a huge limit" --trailer "Task: DAEO-neam" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" -- tests/acceptance/W2-45

After all: `git diff --stat 0098b58d5 HEAD` must show only `tests/acceptance/W2-45/` and the W1-40 file; paste it.

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include the sandbox check first in `evidence`; each commit (12 digits); each new case's node id with its red reason
at this head (the failing line); the W1-40 file's counts; the fixture build time and the merge count; the diff stat.

## Context bundle (gov context DAEO-neam, hash ef773753cafd)

Authority: DEC-729 (decision, ACCEPTED); DAEO-g0ip (task, closed). Supplementary: none (the lexical index is stale). The ticket text as the bundle gives it:

    ---
    id: DAEO-neam
    status: in_progress
    deps: [DAEO-g0ip]
    links: []
    created: 2026-10-16T16:35:12Z
    type: task
    priority: 4
    assignee: engineer
    external-ref: W2-45
    tags: [wave-2, implementation, standard]
    wbs_id: W2-45
    title: gov check runner semantics and scale
    class: implementation
    state_class: AUTHORITATIVE
    role: engineer
    depends_on:
    - DAEO-g0ip
    allowed_paths:
    - src/gov/check/runner.py
    - src/gov/check/commands.py
    - src/gov/decisions/checker.py
    - tests/unit/check/**
    - tests/acceptance/W2-95/test_w2_95_adopted_and_gov_check.py  # one test-designer revision: _others() leaves out elapsed_s (Rewrite-Reason: P-W2-45-1 item 2; DEC-1148 (4))
    - tests/unit/ci/test_ci_command.py  # one revision: line 80 == "RED" and line 73's comment (Rewrite-Reason: P-W2-45-1 item 5; DEC-1148 (4))
    - docs/probes/DAEO-neam/**  # the probe record (P-W2-45-5 (a), the CTO, 2026-11-12)
    - tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py  # one test-designer revision: line 49 and its docstring, Rewrite-Reason P-W2-45-1 item 5 (DEC-1153 (1))
    kpis:
      success:
      - 'The decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget''s value printed beside it) [W2-H018].'
      - 'A check that exits 0 with findings, or with "unmeasured" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with "unmeasured" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].'
      - 'An absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].'
      - 'A hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].'
      - 'The time limit is stated and tested Verify: the limit''s value is printed in the runner''s result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].'
      failure: []
    profile: STANDARD
    sources:
    - DEC-729
    est_loc: 160
    acceptance_tests:
      path: tests/acceptance/W2-45/
      author: independent-test-designer (MR-3); written before implementation
    track: C
    closes:
    - W2-H018
    list_rows:
    - W2-H018
    - W2-L096
    - W2-L098
    - W2-L104
    - W2-L118
    - W2-L167
    - W2-L168
    - W2-L169
    - W2-L171
    - W2-L223
    - W2-M063
    - W2-M128
    - W2-M129
    - W2-M130
    - W2-M131
    - W2-M132
    - W2-M144
    - W2-M146
    - W2-M151
    - W2-M170
    - W2-M211
    - W2-M212
    - W2-M259
    - W2-M265
    - W2-M268
    - W2-M315
    ---
    # W2-45 gov check runner semantics and scale
    
    **Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).
    
    Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-45), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).
    
    - **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.
    - **KPIs:**
      - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].
      - A check that exits 0 with findings, or with "unmeasured" in its result, is not green [W2-M129, W2-M212].
      - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].
      - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].
      - The time limit is stated and tested [W2-M151].
    
    ## Interface (DEC-1052; P-W2-45-1 accepted as a whole, item 5 as written: an absent tool of a hard-block check is RED, openspec included; the CTO, 2026-11-12 12:58)
    
    Proposal (all in src/gov/check/runner.py unless named):
    
    1. **Tier = the declaration's `severity`.** "Hard-block tier" means `severity: hard-block`. `tier:` (G0-G5) is not read.
    2. **Time fields (S1, S5).** Every check result gains `elapsed_s` (wall seconds, float) and `time_limit_s` (the limit
       applied: its `timeout-seconds`, else `TIMEOUT_S`). The runner's result gains top-level `time_limit_s` (= `TIMEOUT_S`,
       60, DEC-595). Built-in checks carry both too.
    3. **S1, the budget.** The `gov check` budget of the decision checker is the time limit of the check that runs it,
       core-authority: 60 s (TIMEOUT_S; its declaration states none). Verified by a planted repository of 200 decision
       records and 20,000 commits (built with `git fast-import`) holding the core-authority declaration: `gov check --json`
       exits, and core-authority's entry has `elapsed_s` < `time_limit_s`, both printed. Speed work only in
       `src/gov/decisions/checker.py`.
    4. **S2, not green.** A check is GREEN only when it exits 0 with no finding. Exit 0 also yields findings when: the
       success form `{"ok": true, "result": R}` has a non-empty `R.findings`; or any JSON mapping in the output (top level
       or R) has `"unmeasured": true` -> finding `CHECK_UNMEASURED` with its `reason`; or non-JSON output contains the word
       "unmeasured" -> `CHECK_UNMEASURED`. Status from findings as now: RED if hard-block, YELLOW if warning.
    5. **S3, absent tool.** Exit code 127, or OSError on start -> finding `CHECK_TOOL_ABSENT` naming the command's first
       word; RED when hard-block (never YELLOW), YELLOW when warning. The built-in `openspec-validate` (hard-block) follows
       the same rule: `OPENSPEC_ABSENT` becomes RED. (Cost: a machine without openspec gets a red `gov check`; openspec
       and gitleaks are installed here. Alternative (b): leave openspec YELLOW, named as a residual against S3.)
    6. **S4, tier coverage.** A path-map policy key of strength hard-block whose covering declarations (`enforces`) are all
       of severity warning -> a `policy-<key>` result, severity hard-block, RED, finding `POLICY_TIER_TOO_LOW` with
       `policy`, `checks` (the covering ids) and a message naming the key. "Refused" = that RED result and `gov check`'s
       non-zero exit (unchanged). One hard-block declaration covering it -> no policy result (accepted). An uncovered key
       keeps `POLICY_NOT_COVERED`.
    7. **S5, time limit.** A check past its limit is stopped with its whole process group (`start_new_session=True`,
       `killpg` on timeout, so a grandchild holding the pipe cannot keep the runner waiting) -> finding `CHECK_TIMED_OUT`
       (was `CHECK_FAILED`) carrying `time_limit_s`; status by severity. Unit test in `tests/unit/check/` (engineer): a
       planted check `sleep 30` with `timeout-seconds: 1` -> `CHECK_TIMED_OUT`, `time_limit_s` 1 printed, ends in < 10 s.
    8. **Unchanged:** family roll-up, `gov check`'s exit code rule, the not-applicable (exit 2) path, `commands.py`
       (W2-159's line kept; touched only if a module list needs it).
    
    ## Widened by the owner (DEC-1148 (4), P1-J (a), 2026-11-12)
    
    Two older tests assert what the accepted Interface changed: R1 (W2-95's `_others()`, `elapsed_s` is a wall time) by the test designer; R2 (`test_ci_command.py:80`, OPENSPEC_ABSENT is RED) by the engineer or designer. One revision each, each with its Rewrite-Reason; nothing else in either file changes.
    
    ## Run 3's packages (2026-11-12)
    
    - **P-W2-45-3 (a)** (the CTO, delegated P2): a fix round inside the paths: a test-design batch (a history with one merge in six, an interrupt case), one engineer (`checker.py` passes over merges whose parents hold the decision's file unchanged; `runner.py` stops the group on any exception: F2, F3), then review round 2, the last (DEC-1010). F4 to F6 are rows.
    - **P-W2-45-5 (a)** (the CTO): the probe folder added.
    - **P-W2-45-4** (the W1-40 case, a widening): with the owner.
    
    ## P-W2-45-4 decided (the owner, DEC-1153 (1), 2026-11-12)
    
    (a): `tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py` added for one test-designer revision: line 49 expects a non-zero exit and RED, its docstring (lines 46-47) says so, `Rewrite-Reason: P-W2-45-1 item 5`; nothing else in the file changes. It rides run 4's batch with P-W2-45-3 (a).
