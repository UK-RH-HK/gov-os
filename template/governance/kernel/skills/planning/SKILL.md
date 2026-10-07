---
name: planning
version: "1.0.0"
description: Method for emitting schema-valid tickets, gap tickets and readiness rows during planning.
---
# Planning

This skill describes how to plan work by emitting tickets and tracking readiness. It follows the Contract and the decision register; it does not grant permissions or set rules on its own authority.

## Order of specification work

Per DEC-103 (CAP-30.f), planning follows the same order as discovery:

1. Discovery and research: confirm that the area is sufficiently understood before writing tickets (DEC-103).
2. Scenarios: each ticket's scope traces back to one or more scenarios (DEC-103).
3. Representative data: scenarios reference the data samples they exercise (DEC-103, CAP-30.f).
4. UX for a feature with a user interface: the owner reviews scenarios and UX designs, not test code (DEC-103).
5. Acceptance tests: each ticket carries or links to its acceptance tests (DEC-103).
6. Implementation: tickets are sequenced so that implementation can begin once tests exist (DEC-103, CAP-30.f).

## Schema-valid tickets

Per CAP-30.b, planning emits tickets that validate against the ticket schema. Each ticket carries the fields the schema requires — id, title, class, priority, dependencies, allowed paths, KPIs and acceptance test path. Use `gov check` to confirm that emitted tickets pass schema validation (CAP-30.b).

## Gap tickets and readiness

Per DEC-089 (CAP-30.b), every required open readiness row produces one linked gap ticket. The gap ticket's class matches the kind of work the row calls for — discovery, data, research or test-design — and its completion closes the readiness row (DEC-089).

### Method

1. Run `gov readiness` to list open readiness rows for the current wave (DEC-089, CAP-30.b).
2. For each required open row, emit one gap ticket with a class from: discovery, data, research or test-design (DEC-089).
3. Link the gap ticket to the readiness row it addresses (DEC-089, CAP-30.b).
4. A required open readiness row with no linked gap ticket is a planning failure (DEC-089).

## Ticket classes

Planning assigns each ticket a class. The classes relevant to gap tickets are:

- **discovery**: the row needs further investigation or an experiment (DEC-089).
- **data**: the row needs representative data samples (DEC-089).
- **research**: the row needs background research or a literature review (DEC-089, CAP-30.b).
- **test-design**: the row needs acceptance tests written by the independent test designer (DEC-089).

Other ticket classes (task, skill, standard, integration) are used for implementation work and follow the same schema (CAP-30.b).
