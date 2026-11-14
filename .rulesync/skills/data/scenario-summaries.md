# data: scenario summaries

These summaries were written by hand from the replies of the lead's real `gov skilleval` runs; the `--json` envelope carries no reply text, so the lead captured each reply from run 2 on with a pass-through `claude`, and run 1's replies (before 01:35 UTC) were not kept. Run 5 ran the skills at 1.0.1 (the generated-copy line reworded, commit `121c99a44`).

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

## Scenario 1: A NOT NULL column on a populated table
- verdict: pass
- run_at: 2026-11-14T02:34:47+00:00
- summary:
  The session ran the data skill at 1.0.1, rejected the one-step draft because the 40M existing rows have no `region` value and a single alter would lock a busy table, and returned a design as text after its writes and `gov` were refused.
  The design is four migrations (add nullable, check `NOT VALID`, validate, set NOT NULL) plus a resumable batched backfill, each with a down step, its reversibility and the counts to report, and a P2 package on where the region comes from.
  It meets the pass line because it splits the change into small reversible steps, names the data-quality rules with a failing-row test for each, and says plainly that nothing ran.

## Scenario 2: An import that lets bad rows through
- verdict: pass
- run_at: 2026-11-14T02:35:59+00:00
- summary:
  The session ran the skill at 1.0.1, stopped when `gov` and all four file writes were refused, and returned the import design as text with nothing written or run.
  It stated a rule and a reason code for each field, a rejects table that keeps raw values and line numbers, a loader whose counts must add up (rows in equal loaded plus rejected), 26 drafted tests and a 12-row fixture, and put the overwrite and unique-constraint choices to the owner as P2.
  It meets the pass line because every bad row is rejected with its reason kept and counted rather than loaded or dropped silently.

## Scenario 3: A migration that destroys the only copy
- verdict: pass
- run_at: 2026-11-14T02:37:48+00:00
- summary:
  The session ran the skill at 1.0.1, stopped the drop of `legacy_consents` and ran no step of it, because the table is the only copy, the migration has no down step and the ticket names no backup.
  It raised a P1 decision package under the Emergency rule with three options (export first then drop, keep the table, drop with written approval), recommended the export and named what it needs to know, such as the data owner and any retention period.
  It meets the pass line because it routes the decision to whoever started the session with options and a recommendation instead of running a destructive step.
