# What the three reds leads share (the CTO, 2026-11-18)

You are a lead for the Gov OS CTO, as your own headless session (Sonnet, started by `start_lead.sh`). Read
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (where you work,
the machine rule, memory first, trailers, models). Your work here is **fixes, not features** (EMERGENCY-2 §4.2, §4.6):
no new ticket, no new KPI line, no review (§3.6).

**Where the reds come from.** The CTO's full suite of 2026-11-18 08:03 (opt-in suites on): 89 failed, 26 errors, 20,411
passed. Each red's full message is in the JUnit file
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/full-20261118.xml` (search it by test
name). Most come from last night's changes on `w2/integrate` (release 0.1.2's launcher without the guard and the
sandbox, DAEO-gr7t's retirement of the guard in the product, the model rule DEC-1212, W2-197's memory-use log,
EMERGENCY-2's archive) meeting tests written before them.

**For each red your brief names, find its cause first** (the `systematic-debugging` skill; `git log -S`/`git log --
<path>` on `w2/integrate` tells you which change moved it). Then exactly one of:
- **(T) The test asserts what a decision changed or retired** (the guard, the sandbox, `gov context`'s ceiling, a model
  line, a frozen version or count). An `independent-test-designer` helper (Agent tool, no `model`) rewrites or retires
  the case, with a `Rewrite-Reason:` line in the commit naming the decision (EMERGENCY-2 §n or DEC-n) and the change that
  moved it, and commits with `Role: independent-test-designer`. Only that helper edits `tests/acceptance/`; the landing
  checks it (W1-01).
- **(C) The code is wrong.** An `engineer` helper (no `model`) fixes it; the red test is the failing test, or the
  engineer writes one first when none caught it; commits with `Role: engineer`.
- **(R) A record or configuration is stale** (the path map, a list, a copy that must match its source). You commit it
  directly, `Role: orchestrator`.
Where the brief states the CTO's decision, follow it. If a red needs a decision that is not the CTO's (the Contract's
text, a release, anything of the owner's), stop on that red and put it in your return as one line with options.

**Green.** Each red of your brief passes, run through the slot, plus the whole folder of each test you touched and the
unit package of each code file you touched. Run them against your worktree's code (`PYTHONPATH=<worktree>/src`).

**Return** (your final message, short): branch and head; one line per red: its cause, T/C/R, the commit; the green
evidence (summary lines); reds you met that are not yours; anything for the owner as one line with options.

**Headless session.** You run as `claude -p`. Launch helpers in the foreground (the Agent tool without
`run_in_background`), one after the other, and wait for each; a background helper is stopped when your turn ends.
