---
id: DAEO-neam
status: closed
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
