---
type: probe
id: PR-DAEO-neam
status: DONE
task: DAEO-neam
reviewer_session: a607cb8c-b495-4e97-bf47-c13942b164c8
implementer_session: "eng-1 f411cfb1-92de-421c-b00c-07b984efb44b (3ed6f53118d1); eng-2 3e856fea-3521-42a0-a57a-df5f7372c6b8 (6e69ebbc524a); eng-3 bac9659d-e10f-493b-a10d-ab4c3d86e3dd (fbb137dd3515, a95790aa9ca0)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: b13789476a9ca2b085c08ab4cb58619b91bd3ce6
decisions_applied: [DEC-729, DEC-1052, DEC-1148, DEC-1153, DEC-1010, DEC-136]
---

# Probe record: W2-45 (DAEO-neam) gov check runner semantics and scale, STANDARD review, rounds 1 and 2 of 2 (DEC-1010)

- **Round 1** (reviewer session 01b0efe2-418e-4758-a456-d034153475f9, independent-auditor, Opus high, read-only)
  probed head `0653dc01086e`: **fail**. F1 was major (S1, fails closed): on a planted 200-decision, 20,000-commit
  history with one merge in six, the decision checker took 132.8 s against the 60 s budget. One-parent commits were
  passed over, but every merge was read for every decision. F2 and F3 were minor (S5): an interrupted runner, or a
  limit too large for `communicate`, left the check's process group running. F4 to F6 were minor and are rows.
- **The repair** (P-W2-45-3 (a), the CTO): the lead gave F1 to F3 as described behaviours (DEC-136).
  - The independent test designer (td-4, session d0e78ac5-dc9e-451f-aea0-996d7d1b63f1, `100015249`) added 6
    acceptance cases. Three were red at the base for the stated reasons: S1 on a 3,300-merge history
    (`CHECK_TIMED_OUT`, 60.07 s), and the S5 group left running after SIGINT and after a huge limit. Three are guards.
  - In the same batch the test designer revised the W1-40 file (DEC-1153 (1), `11f2e8165`).
  - A fresh engineer (eng-3) made two commits:
    - `fbb137dd3`: `checker.py` also passes over a merge whose path is in none of its per-parent diffs, using one
      `git log --diff-merges=separate` pass.
    - `a95790aa9`: `runner.py` stops the check's group on any exception.
  - The lead merged the tests at `b13789476`. lead_verify was GREEN: 5,044 tests, 0 failed. `gov accept W2-45`
    passed, 38/38.
- **Round 2** (reviewer session a607cb8c-b495-4e97-bf47-c13942b164c8, independent-auditor, Opus high, read-only, a
  fresh session) probed head `b13789476a9c`: **pass**. S1 to S5 all pass, and F1 to F3 are fixed. On the 3,300-merge
  history core-authority's `elapsed_s` was 16.344 against `time_limit_s` 60; the checker took 151.9 s with merges read
  as before the fix. Findings were identical in all three modes, on a planted history at scale and on an adversarial
  15-merge history. No finding is blocking or major. There is no third round (DEC-1010).
- **Rows** (both minor):
  - **N1** (S5, `src/gov/check/runner.py:109-125`): SIGTERM to `gov check` (or `timeout -s TERM`, a terminal hangup,
    `slots._stop_group`) ends the runner, but the check's shell and grandchild keep running. The check runs in its own
    session (Interface item 7), so a group stop no longer reaches it. No result is reported, so nothing shows green.
    Fix: about 10 lines, a SIGTERM/SIGHUP handler in `run_checks` that raises, so the existing exception path stops
    the group.
  - **N2** (S1, `tests/unit/check/test_w2_45_checker_speed.py:189`): no case covers a merge that keeps the file as
    its first parent has it but differs from another parent (`-s ours`). The mutation `--diff-merges=first-parent`
    passes all 32 unit cases but loses a finding. The shipped code is correct.
  - Round 1's F4 to F6 also stay rows.
- **Discoveries outside the paths** (rows for their owners):
  - `src/gov/check/authority.py` drops every `ACTIVE_UNAPPROVED` from the decision checker, and every `GovError` it
    raises, so core-authority shows GREEN where the checker reports.
  - `src/gov/ci/command.py:48` `TOOL_ABSENT` knows neither `CHECK_TOOL_ABSENT` nor `CHECK_UNMEASURED` (round 1).
  - `tests/acceptance/W1-21/test_w1_21_merge.py` has 2 rerank-cap cases red at this head and at the base `0098b58d5`.
- **Reviewer's verdict block, as returned:**

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "N2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "N1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

```
verdict: PASS
head: b13789476a9c
findings: 2
- N1 | minor | S5 | src/gov/check/runner.py:109-125 | gov check stopped by SIGTERM keeps no hold on its check: the check's shell and grandchild are still running 5 s later
- N2 | minor | S1 | tests/unit/check/test_w2_45_checker_speed.py:189 (SCENARIOS) | no case of a merge that keeps the file as its first parent has it and differs from another parent; the shipped code is correct
```

- **Records:** briefs and logs are under the lead's `.gov-runtime/scratch/lead/` (`briefs/rev-1.md`, `briefs/rev-2.md`,
  `log/rev-1.json`, `log/rev-2.json`, `log/rev-2.result.md`, `log/verify/`, `log/accept-4.json`). Each reviewer's
  tripwire showed no change in this worktree that was its own.
