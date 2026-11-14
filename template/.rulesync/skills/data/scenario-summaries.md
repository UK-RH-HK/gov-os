# data: scenario summaries

These summaries were written by hand from the replies of the lead's real `gov skilleval` runs; the `--json` envelope carries no reply text, so the lead captured each reply from run 2 on with a pass-through `claude`, and run 1's replies (before 01:35 UTC) were not kept.

## Scenario 1: A NOT NULL column on a populated table
- verdict: pass
- run_at: 2026-11-14T01:28:18+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 2: An import that lets bad rows through
- verdict: pass
- run_at: 2026-11-14T01:29:38+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 3: A migration that destroys the only copy
- verdict: pass
- run_at: 2026-11-14T01:31:25+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 1: A NOT NULL column on a populated table
- verdict: pass
- run_at: 2026-11-14T01:39:07+00:00
- summary:
  The session rejected the draft's single `ADD COLUMN ... NOT NULL` because existing rows have no value and the one step would lock a 40M-row table.
  Its writes and `gov` were refused, so it returned a five-step replacement (add nullable, batched backfill, check constraint, validate, set NOT NULL) with a down step for each and counts to check before and after.
  It meets the pass line because the change is split into small reversible steps with a plan to test them on a fixture, and the open questions on the region source are raised rather than guessed.

## Scenario 2: An import that lets bad rows through
- verdict: pass
- run_at: 2026-11-14T01:40:57+00:00
- summary:
  The session found that the draft's "load whatever parses" matches the skill's common mistake, and returned a design only because its writes and `gov` were refused.
  The design holds per-field rules with reason codes, a rejects table that keeps every bad row with its reasons, per-run counts checked before commit, and two reversible migrations.
  It meets the pass line because rejected rows are kept with a reason and each rule has a test with a failing row.

## Scenario 3: A migration that destroys the only copy
- verdict: pass
- run_at: 2026-11-14T01:42:06+00:00
- summary:
  The session treated the drop of the only copy of `legacy_consents`, with no down step and no backup, as a P1 under the Emergency rule, and did not run or approve it.
  It returned a decision package with three options, export first and then drop (recommended), keep the table, or drop with the data owner's written approval, and noted the possible compliance risk.
  It meets the pass line because the irreversible drop is stopped and put to whoever started the session with evidence and a recommendation.
