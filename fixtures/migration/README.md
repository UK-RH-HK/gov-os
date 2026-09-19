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

**First-run path: provision, then install (OWNER-DECISION-P2-0002).** The harness provisions each scenario machine with the certification suite's throw-away test root (`tests/certification/common.rs::provision`, published-seed keys — never a production root) and installs a release signed under it (`gov init --source <signed release>`; `common::signed_source`). A machine with no trust anchor refuses kernel material from any external source; only the `gov` binary's own embedded payload may be installed there, as a marked bootstrap installation that is never presented as current, verified or certified.

Adoption installs its kernel at A6 batch 0 through the same ingress, from the signed release (`gov adopt migrate --source <signed release>`).
