---
id: MR-3
type: specification
status: PROPOSED
state_class: DERIVED
title: KPIs; the builder never writes its own acceptance tests
depends_on:
- CONTRACT-v5
---

# MR-3: KPIs; the builder never writes its own acceptance tests

A master rule of the Charter (v6, §4). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves.

- **Text:** architecture v0.3 §1A (Charter v6 §4)
- **Acceptance:** The landing refuses a commit that changes `tests/acceptance/` without `Role: independent-test-designer` (or the owner's `Role: owner`), naming the commit, in the Gov OS repository and in an adopted repository (`gov queue`); a feature ticket is not READY until `tests/acceptance/<ticket-id>/` exists and its tests are red on the base; a breach is a forbidden outcome.
