# P2-ADJ-0003 — Orchestrator adjudication: H4 authoring gaps degrade suite health; green-baseline probes use contract-valid fixtures

| Field | Value |
|---|---|
| Record | P2-ADJ-0003 (orchestrator adjudication of a question a builder raised; **not** an owner decision; the owner may override) |
| Date | 2026-09-19 |
| Raised by | P2-AR-0033 (WS-2 round 3), report `release/capability-baseline/repair-1/r3-ws02/00-REPAIR-REPORT.md` §7 (on branch `phase2/repair-1-r3-ws02`) |
| Classes touched | BC-P2-03 (governance-suite currency, O4/W6) × WS-10's H4 scenario-chain findings (IP-WS10-06) × BC-P2-44 (Gate U / HEALTHY) |

## The question

1. WS-10's H4 lifecycle findings (`SCENARIO_DATA_UNDECLARED`, `SCENARIO_WITHOUT_INDEPENDENT_TEST`, severity `medium`) now reach
   the governance suite, as IP-WS10-06 specified. A repository whose scenario chain is incomplete therefore audits DEGRADED
   and takes no green record. The audit-of-record probe zeta-r `FR-baseline-green-current` uses a fixture scenario with such
   gaps, so its green-baseline precondition no longer holds and its currency rows pass vacuously. Should H4 gaps degrade
   suite health?
2. AC16-X1 `X1-O4-green-stale-after-direct-spec-change` needs a green record that is current right after a CIT that
   invalidated DONE work. In the same chain `X1-UxO5` (BC-P2-44) requires that state not to be HEALTHY. Both cannot pass.

## Ruling

**1. Yes — H4 gaps degrade suite health, and refuse nothing.** Keep the round-3 behaviour.

- Contract v3 H3/H4 (lines 517–527) make FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS the
  required chain, and a missing cell generates work. H2 (line 515): a silent N/A is invalid.
- Contract v3 HEALTHY (lines 995–1008) holds only when "feature readiness explicit" and "tests/traceability satisfy policy".
  A scenario with undeclared data or no independent test does not satisfy test policy, so the repository is not HEALTHY and
  the suite is not green.
- Availability is not traded away, so this is not an owner question:
  - no hard-block rule fires below `high` (`scheduler/catalogue.rs` on `phase2/repair-1-r3-ws02`);
  - the close gate accepts a complete, current suite result whatever its verdict (`verification/currency.rs`
    `enforce_close_with`, WS-5 O-R2-1: "a close is never refused by the incomplete specification it is completing").
  An H4 gap makes health DEGRADED, generates its remedy work (H3), and blocks no work, including its own remedy.
- No new product requirement, no security-policy or cost trade-off, no change to an accepted boundary, and no unresolved
  normative conflict: the behaviour follows from the lines above.

**2. Probe preconditions are not normative; the contract is.** For verification iteration 1 and later:

- BC-P2-03 currency (O4 lines 787–789; W6 lines 1128–1136) is judged on the property. A probe that needs a green baseline
  must build one that is legitimately green under Contract v3 (e.g. an H4-complete scenario, as WS-2's labelled derived copy
  `evidence/derived/FR-freshness-invalidation.h4-complete.P2-AR-0033.py` does). A vacuous pass is not a pass. A precondition
  the contract itself makes false is not a product defect.
- X1-O4's precondition contradicts Contract v3:1136 ("stale evidence cannot remain green merely because the original task
  closed successfully"): after a CIT invalidates DONE work, green must not hold. The O4 property in that chain is tested once
  revalidation has cleared the invalidation and the suite is legitimately green: a direct spec change then makes that green
  record stale, and closing governance-affecting work on it is refused. `X1-UxO5` stands as written.
- Where a failing precondition exposes a real defect, it is still a defect. Here WS-2 found one: the generated revalidation
  task's `revalidates`→`TESTS` edge is `ill_typed` under `memory::integrity` (IP-R3-WS02-07), routed to integration-3.

Independent verifiers author their own held-out tests and are not bound by the audit-of-record probes; this ruling only
fixes how a green-baseline precondition is read.
