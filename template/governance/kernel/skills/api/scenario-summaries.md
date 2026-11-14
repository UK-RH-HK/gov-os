# api: scenario summaries

These summaries were written by hand from the replies of the lead's real `gov skilleval` runs; the `--json` envelope carries no reply text, so the lead captured each reply from run 2 on with a pass-through `claude`, and run 1's replies (before 01:35 UTC) were not kept. Run 5 ran the skills at 1.0.1 (the generated-copy line reworded, commit `121c99a44`).

## Scenario 1: A new endpoint with no contract
- verdict: pass
- run_at: 2026-11-14T01:28:18+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 2: A rename in a published response
- verdict: fail
- run_at: 2026-11-14T01:28:56+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was fail, with the cause "judged FAIL against the pass line".
  A later entry of the same scenario holds a kept reply, and it passed.

## Scenario 3: A contract that is silent on one error
- verdict: pass
- run_at: 2026-11-14T01:29:32+00:00
- summary:
  The reply to this entry was not kept, because it ran in run 1, before the capture.
  The record holds only the judgement, which was pass with no cause.
  A later entry of the same scenario holds a kept reply.

## Scenario 1: A new endpoint with no contract
- verdict: pass
- run_at: 2026-11-14T01:36:46+00:00
- summary:
  The session found no ticket, contract or handler in its workspace, so it wrote nothing and returned the plan the skill sets for `POST /v1/exports`.
  The plan adds the endpoint to the OpenAPI file first with its 202 response and every error, then writes the unit tests from the contract, then the handler, and runs acceptance only through `gov accept`.
  It meets the pass line because the contract comes before the code and the tests follow the contract before the handler is written.

## Scenario 2: A rename in a published response
- verdict: pass
- run_at: 2026-11-14T01:37:22+00:00
- summary:
  The session classed replacing `total` with `total_cents` in published `v1` as a breaking change, changed no contract or code, and escalated it as a P2.
  Its package gave three options: add `total_cents` and keep `total` (recommended), a new `/v2`, or an in-place rename (rejected), and it asked whether the spec needs `total` gone.
  It meets the pass line because it does not break the published response in place and sets out a compatible way, although it escalated instead of making the change.

## Scenario 3: A contract that is silent on one error
- verdict: pass
- run_at: 2026-11-14T01:38:04+00:00
- summary:
  The session treated the missing 409 body as a P3, took the simplest reading, which is the contract's shared error shape with a code, and did not ask the owner.
  It wrote the contract addition as text because no contract file existed, logged the choice in `discoveries`, and listed the tests still needed.
  It meets the pass line because the open point is settled in the contract and logged, though no test was run.

## Scenario 1: A new endpoint with no contract
- verdict: pass
- run_at: 2026-11-14T02:34:47+00:00
- summary:
  The session ran the api skill at 1.0.1, found no ticket, contract file, handler or tests in its workspace, wrote nothing and returned the plan after `gov --help` was refused.
  It drafted the OpenAPI fragment for `POST /v1/exports` first (202 with an `id`, the shared error shape for 400, 401, 403, 429 and 500) and then the tests it would write from that contract before the handler.
  It meets the pass line because it orders the work contract first, tests from the contract second, and the tests match the drafted contract.

## Scenario 2: A rename in a published response
- verdict: pass
- run_at: 2026-11-14T02:35:29+00:00
- summary:
  The session ran the skill at 1.0.1, judged the rename of `total` to `total_cents` in the published `v1` response a breaking change for mobile apps, and escalated it as a P2 with no file changed.
  It laid out three options (additive in `v1`, a new `/v2`, a rename in place), recommended adding `total_cents` and keeping `total` marked deprecated, and gave the contract fragment and the unit tests for it.
  It meets the pass line because it refuses the in-place rename, names a test for the new field, and says removal of `total` is a separate later change.

## Scenario 3: A contract that is silent on one error
- verdict: pass
- run_at: 2026-11-14T02:36:10+00:00
- summary:
  The session ran the skill at 1.0.1 and ranked the missing body of the 409 response as a P3 that is reversible, inside the ticket and changes no KPI, so it did not ask the owner.
  It took the simplest reading, the contract's shared error shape with the code `name_taken`, wrote the OpenAPI fragment and the tests to write first, and logged the reading in its return; no file changed because none was present.
  It meets the pass line because it settles the point in the contract itself, in the same change as the code, and records the reading where the owner can see it.
