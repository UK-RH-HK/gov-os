# W2-07 lead checkpoint (DAEO-r9ss, run 1)

## State (2026-10-23)
- Branch w2/W2-07, base head c2d539c6 (verified clean at start).
- Step: 0 (setup). Rebuild 1 running in background (log/rebuild-1.*), gated on load < 20 and disk gate.
- Next: launch the independent test designer (briefs/td-1.md) through gov launch, sandboxed, --effort high, with the tripwire (tripwire-before-1.json).

## Decided / found
- The ticket's named W1-30 revision set (test_w1_30_no_acceptance_tests.py, test_collection_error_refuses_close) looks incomplete:
  tests/acceptance/W1-30/test_w1_30_r9_every_finding.py asserts DEC-492's "every gate asked, tests reached after an early finding,
  counted once", which P-IS-4 (a) / DEC-868 item 3 changes (commit gates stop before any test, spend no attempt).
  Other W1-30 cases (stale checkpoint counted, red gov check counted) may also turn red. The test designer is asked to survey
  and list them (not revise them); expected outcome: a package to the orchestrator to widen the revision batch.
- DEC-492's status line carries no "Changed by" note for that change (DEC-866: name it in the return).
- Ticket classes in use beyond the KPI's named ones: config, skill, schema, template, documentation, ops, role-definition.
  Not named by the KPIs: existing behaviour (acceptance tests) stays; noted for the return.
- Evidence naming for research/integration/coordination tickets is prose only (acceptance_tests.judged_by); the designer picks
  the reading and lists it as an interface assumption; the engineer gets it as specification from the lead.
- W2-M354 (a-dev's repair ticket) is an a-dev product repo item; outside this ticket's reach (no workbench writes).

## Loop
- Iteration count held by the lead (not disclosed).

## Refusals met (DEC-849)
- lead: 0
