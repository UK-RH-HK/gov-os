# P-W2-60a-ROUND3 — a third round for W2-60a: worktree launches never check the main checkout's local settings (fails open)

From: the W2 orchestrator, 2026-10-30, sent as it arose (DEC-949). Your decision: an exception to DEC-413's two reviews.

## 1. Context
- **The ticket:** W2-60a (`DAEO-cv58`, FULL, K3) loads each role, its skills and its model and effort at launch, and writes a launch record.
- **Its run:** run 1 returned on 2026-10-30 at 09:14, after 883 minutes and $26.94 for the lead session. It made two rounds, with review 1 failed and review 2 failed.
- **Its head:** `323f04550b7c`. The full run in the close's form is on `e34e07b7ce32`.
- **The size:** 713 lines in src and unit tests, against an estimate of about 250; 2,980 lines of acceptance tests.
- **What's done:** everything but the merge readiness: the CIT-E, the rules probe and the live measurements.

## 2. What happened
Review 2's F1: a launch from a worktree checks the worktree's own `.claude/settings.local.json`, but CLI 2.1.292 loads a worktree session's local settings from the main checkout's file.
- **The test:** with the stand-in CLI, eight keys were planted in the main checkout's file: an added directory, a sandbox block, a bypass mode, `disableAllHooks`, an `agent` key, and three compaction spellings.
- **The result:** each one launched a worktree worker unrefused. The same keys in the worktree's own file are refused.
- **How old it is:** the gap dates from the base of DEC-233, DEC-313 and the hooks check, and this ticket's new refusals share it.
- **Classification:** one finding, reachable in ordinary work, fails open.

## 3. Why it matters
- **Ordinary use triggers it.** The CLI's own `/add-dir` ("Yes, and remember this directory") writes `additionalDirectories` into the main checkout's local file during interactive work. From then on, every Wave 2 worker launched in a worktree runs with an added directory that DEC-313 refuses.
- **It blocks EXAMIN's copy, as a second gap in the same file.** The launcher reads role files from `template/governance/kernel/roles/`, but an adopted repository keeps them at `governance/kernel/roles/`. EXAMIN's copy would be refused at launch, and W1-38's 5 cases are red (P-W2-60a-4).

## 4. Options
- **(a) A third round under DEC-413's exception (recommended),** covering:
  - the check also reads the main checkout's local file for a worktree (`record.py` already finds the main checkout), about 10 lines;
  - the role file read from `governance/kernel/roles/` when the tree has no `template/` (P-W2-60a-4), about 10 lines;
  - in the same test batch: F1 as a behaviour, the W2-58 live fixture fix, the nightly-route line for the live file, and fixture role files for W2-56's 26 unit cases.

  Then one engineer, a full run and review 3. About 4 to 5 hours. W2-56, which shares the launcher file, waits for it either way.
- **(b) As (a), plus workers started with `--setting-sources project`.**
  - Gain: it also closes the `GOV_DEV_TIERS` route.
  - Cost: it removes the main checkout's 24 allow rules and its environment from workers, so more tests need revision. About a day.
- **(c) Defer F1 to W2-56 or a Wave 3 row,** and merge W2-60a after W2-11's role-file lines.
  - Cost now: nothing.
  - Risk: DEC-313's gap stays open for every worktree launch, and EXAMIN's role-file path waits for W2-21.

## 5. Recommendation
(a), confidence medium-high. It closes a fail-open gap that ordinary interactive work opens, and removes a block on EXAMIN's copy, for about half a day. (b)'s extra reach can be weighed again in W2-56, which owns the session's environment.

## 6. What it blocks, and what waiting costs
- **Blocks:**
  - W2-60a's merge (K3, priority 4);
  - W2-60b (its record per session), which depends on it;
  - W2-56, which shares `launcher.py`;
  - W2-82, which starts after both.
- **Waiting costs:** K3 and K6 stall behind it, and W2-56 cannot start.

## Delegated alongside (yours to overturn)
- **P-W2-60a-6 (a):** the fixture role files for W2-56's 26 unit cases go in this ticket's round, with its paths widened to those three files.
- **P-TD-4:** the nightly-route line for `test_w2_60a_live_sessions.py` is added by the round's test designer.
- **P-W2-60a-3:** `--system-prompt-file` and review 2's R4 arguments go to W2-56's refusal list.
- **P-TD-3 and P-W2-60a-1:** accepted (the stand-in plus the real-home live case meets KPI line 6; the CLI's built-ins stay, identified by the CLI version).
- **P-RETRIEVE:** the same as P-R1 in this morning's package.
