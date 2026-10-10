---
id: CAP-58.e
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Orchestrator write scope: the orchestrator may write anywhere in the repository except `tests/acceptance/**`; the guard enforces only that exclusion for it; the containment check still records its changes; its session is not sandboxed; an orchestrator change outside the active ticket''s `allowed_paths` is a record, not a containment finding, while a change under `tests/acceptance/**` stays a finding (DEC-171)'
depends_on:
- CAP-58
---

# CAP-58.e: Orchestrator write scope: the orchestrator may write anywhere in the repository except `tests/acceptance/**`; the guard enforces only that exclusion for it; the containment check still records its changes; its session is not sandboxed; an orchestrator change outside the active ticket's `allowed_paths` is a record, not a containment finding, while a change under `tests/acceptance/**` stays a finding (DEC-171)

A covers item of CAP-58 (Path guards as default-deny allow-lists). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Orchestrator write scope: the orchestrator may write anywhere in the repository except `tests/acceptance/**`; the guard enforces only that exclusion for it; the containment check still records its changes; its session is not sandboxed; an orchestrator change outside the active ticket's `allowed_paths` is a record, not a containment finding, while a change under `tests/acceptance/**` stays a finding (DEC-171)
- **Wave:** W1
