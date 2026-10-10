---
id: MR-3
type: specification
status: PROPOSED
state_class: DERIVED
title: KPIs; the builder never writes its own acceptance tests
depends_on:
- CONTRACT-v4
---

# MR-3: KPIs; the builder never writes its own acceptance tests

A master rule of the Charter (v5, §4). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves.

- **Text:** architecture v0.3 §1A (verbatim in Charter v5 §4)
- **Acceptance:** An implementer write to `tests/acceptance/**` is refused by the guard and caught by the post-command containment check; an implementation ticket is not READY until `tests/acceptance/<ticket-id>/` exists; a breach is a forbidden outcome. The orchestrator may write anywhere in the repository except `tests/acceptance/**`, which the guard refuses to it as to every role but the Independent Test Designer (DEC-156).
