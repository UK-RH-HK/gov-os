---
type: probe
task: DAEO-p8tv
reviewer_session: 05bd8c31-ea62-49a0-be0c-4e9b18491d2d
implementer_session: 597ca8ec-0479-44c5-a089-f687a1e9ff61
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f706a77f5b7e0a641f29a90fda05ef05e2d30dc8
decisions_applied: [DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073]
---

# Probe record: W2-172 (DAEO-p8tv), the memory audit's driver and schedule, review round 1

- **What was probed.** Head `f706a77f5b7e` of `w2/W2-172`: the change from `80da3fbcca0d` (the merged red tests). That is
  the engineer's `bf21edd96` (`run`, `due`, `baseline`, `status`, `figures` in `src/gov/memaudit/driver.py`,
  `schedule.py`, `digest.py`, `__main__.py`, and `governance/project/orchestration/tools/memaudit_cron.sh`), the engineer's
  `f989ca89b` (unit tests and `docs/changes/W2-172-evidence.md`), and the test designer's revision `5193add39` for
  PKG-W2-172-TESTS-1, merged at `f706a77f5`. It was judged against the ticket's KPI lines S1-S9 and F1-F5, its Interface
  items 1-12 with O1-O4, and the CTO's decision PKG-W2-172-TESTS-1 (GATE-1 (a), TD-1 (b), TD-2 (b)).
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus high, class C2, session
  `05bd8c31-ea62-49a0-be0c-4e9b18491d2d`, 2026-11-12. It was started through `gov launch` under its OS sandbox. The
  ticket lead (an orchestrator-role session) commissioned and judged it. It wrote nothing in the repository: its tripwire
  shows no change in this worktree, and `git status --porcelain` is empty at the head.
- **Step 0.** A write outside the worktree was refused (read-only file system). `git hash-object -w` and
  `git update-index --refresh` worked. No local model server was running. `gov.__file__` =
  `/home/usain/gov-os-worktrees/W2-172/src/gov/__init__.py`.
- **Threat model (DEC-801, DEC-808).** Honest mistakes and plausible accidents in ordinary work. A finding fails the
  probe only when it is "Ordinary work: yes" with "Consequence: fails open | loses work".
- **Verdict: pass, 0 blocking.** All 14 lines pass. There are 6 findings, none of them "yes" with "fails open" or
  "loses work". The lead's judgement agrees. R1-1, R1-2, R1-3 and R1-5 are residuals for the CTO, and R1-4 and R1-6 are
  rows.
- **The verification beside it.** `gov accept W2-172`: pass, 163 passed, 0 failed, 0 skipped. `tests/unit/memaudit`:
  230 passed. `lead_verify` over the selected suites (4934 tests): 4 red, none this ticket's:
  - W2-171's F5 path case judges the branch it runs on, so it fails on any later branch (the brief: a path case judges
    only its own ticket's branch).
  - Two W2-157 backstop cases were green when run alone (load).
  - One W2-112 reranker case is red at the base `80da3fbcc` as well (the base-red rule).

## Findings

### R1-1: the cron wrapper reads an interpreter that cannot import `gov` as "not due" (S9, item 8, O4; non-blocking)
- **What happened:** with the wrapper's defaults (`/usr/bin/python3`, cwd not the repository), `-m gov.memaudit due`
  exits 1 with "No module named 'gov'". The wrapper takes that 1 as "not due", logs
  `{"due": false, ..., "started": false, "exit": 0}` and exits 0. On this machine `gov` imports only from the pinned
  virtual environment. The wrapper does not change to the repository itself.
- **What should happen:** a run counts as "not due" only when `due` printed `DUE no`, and any other result is logged with
  its real code. The repository is the cwd. The ACT that installs the crontab line names a `GOV_MEMAUDIT_PYTHON` that
  imports `gov` and changes to the repository first (an entry criterion of ACT-MEMORY-AUDIT-CRON-1).
- Ordinary work: yes (the drafted crontab line plus the O4 default hits it at the first firing).
- Consequence: other. No audit runs, and the wrapper misreports it as "not due". It fails closed at the release check:
  `status` answers `not audited`.

### R1-2: "the last audit commit" includes an audit stopped after USED (S5, S7 RETRIEVAL, item 9; non-blocking, a gap)
- **What happened:** `schedule.py` takes the last `HISTORY.jsonl` line's commit, measured or not. A retrieval change made
  before an audit that stopped after USED stops counting as a back-to-weekly trigger, and it drops out of the next
  digest's RETRIEVAL list. Planted: `due` printed `monthly / stable` with the stopped line and `weekly / retrieval`
  without it. `status` answered `not audited` both times.
- **What should happen:** the trigger and the RETRIEVAL line start from the last *measured* audit's commit, or from the
  `AUDITS.log` line S1 names. The CTO chooses.
- Ordinary work: yes (a stop after USED is a planned S3 path). Consequence: other (the schedule can stay monthly for up
  to 28 days; the release check still holds).

### R1-3: a gate-busy stop reads `STOP <step> exit 2` in the digest (S7 line 11, item 8; non-blocking, a gap)
- **What happened:** no child ran, but the digest invents exit 2. That reads the same as a child's own exit 2. Only the
  `STOPPED <step> gate busy` line and `COUNTS.json` (`reason: "gate busy"`) name the gate.
- **What should happen:** the digest names the gate. The Interface's line 11 has no form for this, so the CTO chooses
  one, e.g. `STOP <step> gate busy`.
- Ordinary work: yes. Consequence: other (the owner can misread the cause).

### R1-4: a launch step that exits 0 without a counts line is read as a clean pass (S1, item 2a; non-blocking, a row)
- **What happened:** checker-1's missing counts line was read as `{}`, so round 2 was skipped. W2-170's `void` still
  dropped the marked question.
- **What should happen:** a launch exit 0 without a readable counts object is a stop at that step.
- Ordinary work: no (the real launch script always ends with its counts line). Consequence: other.

### R1-5: after a stop past `void`, QUESTIONS and the other figures print `not reached` (S7; non-blocking, a gap)
- **What happened:** the figures come only from step 12, so a stop after USED leaves the owner's digest without the kept
  and dropped counts, although `DROPS.json` exists.
- **What should happen:** on a stop, the read-only `figures` child runs once. The CTO chooses.
- Ordinary work: yes. Consequence: other.

### R1-6: an unexpected end inside the cycle leaves `COUNTS.json` with `stop: null` and no digest (item 5; non-blocking, a row)
- **What happened:** a line refused by `say` inside the cycle ended the run with exit 4 after the `STARTS.log` line. The
  lock was released and no set was made.
- **What should happen:** an unexpected end still records a stop at the current step.
- Ordinary work: no. Consequence: other.

## Probed and found sound
1. GATE-1 (a): the driver ran `--gate-cmd "<stub> --check"` as its words before measure, judge and pool.
2. A gate-busy stop after USED: exit 2, a HISTORY line with `measured: false, used: true`, and the OWNER line. Under the
   clock seam the polls are counted, not slept.
3. Churn: the denominator excludes the tree-exclude matches, and the 28-day window goes by committer time (planted
   2.94 %, as expected).
4. HISTORY, STARTS and AUDITS.log lines that are not JSON: `due` and `run` complete.
5. The lock is free after a stop and after an unexpected end, and children do not inherit it.
6. The wrapper: `grep -c crontab` is 0, the interpreter follows O4, and the exit codes and log line follow item 8.
7. Read against the code:
   - F1: the driver opens nothing under the sets root.
   - F2: the digest's sources are counts and ids only.
   - Item 3: the checks run in the Interface's order.
   - S3: the USED boundary is decided by step and code, and an unknown measure code counts as after USED.
   - The canary is retried only on 16, only on launch steps, and once.
   - DIGEST.txt and COUNTS.json are written whole by rename.
   - F5: the engineer's commits touch only allowed paths.

## The engineer's readings (evidence file), as the reviewer judged them
- Faithful: RN-NAME by `STARTS.log`; a refusal printed as the digest with line 11 `REFUSED <code>`; no `--force` in the
  digest; the reason-code mapping; polls counted under a fixed clock; the wrapper's default gate
  `$HOME/.local/bin/gov resources --check`; a canary retry's single STEP line.
- Fills a gap sensibly: a brief missing at the audit commit is a stop with code 10.
- Gaps for the CTO:
  - The main line's tip when no store link resolves (`due`, `status`; low risk).
  - `status --store-link`: an extra flag that changes no stated behaviour.
  - The last audit commit (R1-2).
  - The gate-busy digest line (R1-3).
  - The figures on a stop (R1-5).
