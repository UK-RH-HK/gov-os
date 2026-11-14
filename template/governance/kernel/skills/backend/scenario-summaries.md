# backend: scenario summaries

These summaries were written by hand from the replies of the lead's real `gov skilleval` runs; the `--json` envelope carries no reply text, so the lead captured each reply from run 2 on with a pass-through `claude`, and run 1's replies (before 01:35 UTC) were not kept.

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
