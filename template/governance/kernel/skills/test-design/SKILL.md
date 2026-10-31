---
name: test-design
version: "1.1.0"
description: Method for independent test design from the specification and KPIs, in parallel with the implementer and never reading its work.
---

# Test design

This skill describes how the independent test designer writes acceptance tests. It follows the Contract and the decision register; it does not grant permissions or set rules on its own authority (CAP-24.b). Test kinds, run-time cost and the README map in detail: [test-kinds.md](test-kinds.md).

## The work order

- The designer works from the specification and the KPIs at the same time as the implementer builds the code from the same specification, in a worktree of its own; neither waits for the other (DEC-959 item 7, DEC-963).
- It never reads the implementation: no file the ticket's branch changes against its base, other than its own tests; a retrieval or search result under those paths is dropped unread and named in its return (DEC-820 (c)). Its retrieval uses the integration branch's store, never the ticket worktree's (DEC-963 item 2). Everything else is open to it, the existing code it must work with included.
- When its tests are committed, the lead merges them and the implementer runs them once, reading results only, through the project's opaque acceptance runner where it has one (DEC-959 item 6).

## Inputs

1. The ticket: its specification, its KPIs (success and failure lines) and its acceptance test path (CAP-38.b).
2. The public interfaces the ticket must work with, as they stand on the integration branch.
3. Probe or QA findings, when present, as described behaviours (DEC-136, CAP-38.e).

## Writing acceptance tests

For each KPI success and failure line, the test designer:

1. Derives test cases from the specification and the KPI wording with the black-box technique that fits the line: equivalence partitions (one case per class of input that behaves alike), boundary values (each edge and its neighbours), decision tables (each combination of conditions the line names) or state transitions (each allowed and refused move) (CAP-38.b).
2. Asserts observable behaviour through public interfaces, never internals; deterministic, no network (CAP-38.b, DEC-136).
3. Keeps each assertion traceable to one KPI line (CAP-38.b).

## How much is enough

- The minimum that shows each KPI line and each failure line, in proportion to the profile: FULL thorough; STANDARD every line's success and failure plus the key edge cases; LITE one test per line. No combinatorial expansion beyond what a KPI demands (DEC-221).
- A measured example of too much: 2,980 lines of acceptance tests for 713 lines of code. Tests far larger than the change they test are cut back to what the lines need (DEC-951 item 5).

## Kinds and cost

- Each test is one kind: unit, acceptance, live or harness, dev-tier, load-sensitive or repository-state; every kind but acceptance is declared, and each kind has a run-time limit, measured from the runner's own per-test durations (DEC-889 item 11 c). The table: [test-kinds.md](test-kinds.md).
- A test never copies the whole working tree where a minimal fixture will do: it builds a temporary repository holding only what the case needs.
- A test that asserts the live repository's own state (its records, not the code) is declared as such: it belongs to the record-reading set, which runs after record changes.

## Red against the ticket's base

Run the tests in the designer's own worktree, which holds no implementation, to the end of the suite: each fails for the reason the README states. A test green on the base either tests nothing new or finds the line already met: it is fixed or reported, never left.

## The README map

The README maps each KPI line to the tests under it and the expected red reason of each, in the table form the project's acceptance runner reads, so the implementer sees pass or fail per line and never a test's content (DEC-959 item 6). The form: [test-kinds.md](test-kinds.md).

## Handling probe findings

1. Each finding is taken as a described behaviour, not as code (DEC-136, CAP-38.e).
2. The test designer decides from the specification whether each finding becomes an acceptance test, red before its fix (DEC-136, DEC-430).
3. A finding that reveals a specification gap is reported to the orchestrator so the specification can be amended before testing proceeds (DEC-136, CAP-38.e).

## What the test designer produces

- Test modules under the ticket's acceptance test path, and a conftest if shared fixtures are needed (CAP-38.b).
- The README with its map, each test's kind where it is not acceptance, and the red reasons.
- A report of any specification gaps found during test design (DEC-136, CAP-38.e).

## Sources

CAP-24.b, CAP-38.b, CAP-38.e, DEC-136, DEC-221, DEC-430, DEC-820, DEC-889, DEC-951, DEC-959, DEC-963.
