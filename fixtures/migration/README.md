# Fixture 3 — Path migration

A small mixed repository (Python package `lib/` + TypeScript `web/`) with misplaced specification and test files and
cross-references that must survive a migration:

- `notes/api-spec.md` is an authoritative-looking specification outside `spec/` (target: `spec/interfaces/`), linked
  from `docs/architecture.md` and linking back to it.
- `docs/helpers_test.py` is a test under `docs/` importing `lib.core.helpers` (target: `tests/`).
- `docs/old/legacy_decisions.md` is a legacy decision log (target: extract into `spec/decisions/` + archive).
- `web/src/api/client.ts` imports `../util/http`; unchanged by migration but must still resolve.

Exercised by `tests/certification/migration.rs`: inventory → classification → target path map → plan → independent
review gate → batched execution with link/import rewrites and ledger → independent verification against reality →
rollback of a batch restores a byte-identical tree → memory rebuild after path stabilisation produces an index that
references only canonical paths.
