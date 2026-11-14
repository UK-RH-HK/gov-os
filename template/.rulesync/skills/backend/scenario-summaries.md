# backend: scenario summaries

These summaries were written by hand from the replies of the lead's real `gov skilleval` runs; the `--json` envelope carries no reply text, so the lead captured each reply from run 2 on with a pass-through `claude`, and run 1's replies (before 01:35 UTC) were not kept. Run 5 ran the skills at 1.0.1 (the generated-copy line reworded, commit `121c99a44`). Run 5's sessions had this file in their skill folder and could read earlier replies (the independent auditor's finding F1), so its passes are not clean evidence. From run 6 on, the file was moved out of the skill folder for each run (clean runs).

## Scenario 1: A handler that a retry runs twice
- verdict: pass
- run_at: 2026-11-14T01:28:18+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 2: A column rename on a table a running service reads
- verdict: pass
- run_at: 2026-11-14T01:29:54+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 3: A fix that needs another stream's shared module
- verdict: pass
- run_at: 2026-11-14T01:30:52+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 1: A handler that a retry runs twice
- verdict: pass
- run_at: 2026-11-14T01:39:07+00:00
- summary:
  The session listed each state-changing step and what a second run does, and found the duplicate invoice on every redelivery and the bare `except` that hides a failed write.
  Its file writes and `gov` were refused, so it stopped and returned the unique-key design, the ack-after-commit handler and its planned tests as text.
  It meets the pass line because it states the mechanism that makes a second run safe and names the test that proves it.

## Scenario 2: A column rename on a table a running service reads
- verdict: pass
- run_at: 2026-11-14T01:40:49+00:00
- summary:
  The session found that a one-step rename would break the old version that runs side by side for an hour, and stopped because no ticket or code was in its workspace.
  It planned the rename as add a column and write both, back-fill, switch reads, stop the old write and drop later, each step compatible with the version before it.
  It meets the pass line because the plan gives an order of releases and a down step for the column add, though the way back for the code-only steps is only implied.

## Scenario 3: A fix that needs another stream's shared module
- verdict: pass
- run_at: 2026-11-14T01:41:38+00:00
- summary:
  The session classed the fix as a P2 because the shared retry helper lies outside the ticket's paths and other streams' tickets use it, and it edited nothing there.
  It returned a package with the problem, the proposed three-line fix, the blast radius, the tests the owner should add and a recommendation to wait for the shared fix.
  It meets the pass line because it says honestly what it did inside its paths (nothing, as no code was present) and routes the package to whoever started the session.

## Scenario 1: A handler that a retry runs twice
- verdict: pass
- run_at: 2026-11-14T02:34:47+00:00
- summary:
  The session ran the backend skill at 1.0.1, listed each state-changing step and what a second run does, and found the duplicate invoice on every redelivery and the bare `except` that hides a failed write.
  Its writes and `gov` were refused, so it stopped and returned an `order_id` unique-key migration, an ack-after-commit handler and its planned tests as text, with the existing-duplicates question raised as a P1.
  It meets the pass line because it states the mechanism that makes a second run safe (the unique key with `ON CONFLICT DO NOTHING`) and names the test that proves it (the same message delivered twice leaves one invoice).

## Scenario 2: A column rename on a table a running service reads
- verdict: pass
- run_at: 2026-11-14T02:36:29+00:00
- summary:
  The session ran the skill at 1.0.1, found that a one-step rename would break the old version that runs side by side for an hour, and stopped because no ticket or code was in its workspace and `gov` was refused twice.
  It returned a six-step plan (add the column with a trigger, write both, back-fill in batches, switch reads, stop the old write, drop in a separate P1 ticket) with a way back for each step.
  It meets the pass line because the plan orders the releases so each works beside the one before it and gives a down step for each, including the column add.

## Scenario 3: A fix that needs another stream's shared module
- verdict: pass
- run_at: 2026-11-14T02:37:17+00:00
- summary:
  The session ran the skill at 1.0.1 and classed the fix as a P2 because the shared retry helper lies outside the ticket's paths and three other streams' tickets use it, and it edited nothing there.
  It returned an escalation package with the problem, the proposed three-line fix, who else is affected, the tests the owner should add and three options, recommending that the owner fixes the helper and this ticket waits.
  It meets the pass line because it says what it did inside its paths (nothing, as no code was present), rejects a local workaround and routes the package to whoever started the session.

## Scenario 1: A handler that a retry runs twice
- verdict: pass
- run_at: 2026-11-14T03:17:54+00:00
- summary:
  The session ran the backend skill at 1.0.1 in a clean run (no summaries in the skill folder), listed the insert on every delivery and the bare `except` as the two steps that change state, and had its writes and `gov` refused.
  It returned as text an `order_id` unique-key design with `ON CONFLICT DO NOTHING`, a handler that acks only after commit and a drafted 30-test suite, with a P1 flag for duplicates already in a real table.
  It meets the pass line because it states the mechanism that makes a second run safe (the unique key) and names the test that proves it (two or ten deliveries of one message leave one row).

## Scenario 2: A column rename on a table a running service reads
- verdict: pass
- run_at: 2026-11-14T03:19:26+00:00
- summary:
  The session ran the skill at 1.0.1 in a clean run (no summaries in the skill folder), found that a one-step rename would break the old version that runs beside the new one for an hour, and stopped because the workspace held no ticket or code and `gov` needed approval.
  It returned a six-step plan (add the column, write both, back-fill in batches, switch reads, stop the old write, drop in a later P1 ticket) with a way back for each step.
  It meets the pass line because the plan orders the releases so each works beside the one before it and gives a down step for each, including the column add.

## Scenario 3: A fix that needs another stream's shared module
- verdict: pass
- run_at: 2026-11-14T03:20:12+00:00
- summary:
  The session ran the skill at 1.0.1 in a clean run (no summaries in the skill folder) and classed the fix as a P2 because the shared retry helper lies outside the ticket's paths and three other streams' tickets use it, and it left the helper unchanged.
  It returned a package with the cause, the three-line fix to make, the tests the helper's owner should add and the open question whether this ticket waits or ships a call-site guard, which it left to whoever started the session.
  It meets the pass line because it says what it did inside its paths (nothing, as no code was present) and routes the package with evidence and a recommendation to whoever started the session, and the judge noted the missing local guard did not fail it.
