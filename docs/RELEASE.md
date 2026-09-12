# Releases, manifests and migrations

## Building a release
```bash
bin/gov release build --version 4.1.3 --certification READY_FOR_INDEPENDENT_REVERIFICATION --evidence docs/EVIDENCE.md
bin/gov release verify release/releases/4.1.3
```
`release/releases/<version>/` contains the immutable `kernel/` payload (with `KERNEL_MANIFEST.json`), `manifest.yaml`
and `manifest.json` (schema `release-manifest`), `RELEASE_NOTES.md` and `ROLLBACK.md`. A second build of the same
version is refused (`RELEASE_IMMUTABLE`).

## Release manifest fields
`framework`, `version`, `release_commit`, `release_hash` (= kernel payload hash), `schema_versions`, `cli_version`,
`runtime_version`, `supported_from_versions`, `migration_ids`, `adapter_versions`, `required_index_rebuilds`,
`breaking_changes`, `human_gates`, `file_hashes`, `release_notes`, `rollback_procedure`, `certification`
(`status` ∈ UNCERTIFIED | READY_FOR_INDEPENDENT_OS_VERIFICATION | READY_FOR_INDEPENDENT_REVERIFICATION | CERTIFIED |
REJECTED, `implementer_evidence`, `independent_verifier`, `certified_at`), `built_at`, `immutable: true`.
Only an independent verifier may set CERTIFIED or REJECTED; a rejected release stays immutable and a repaired
candidate that changes the kernel payload gets a new PATCH version (4.1.2 → 4.1.3).

## Consumer lock
`governance/framework.lock`: `framework`, `version`, `release_commit`, `release_hash`, `source`, `installed_at`,
`kernel_manifest_hash`, `cli_version`, `schema_versions`, `lock_schema_version`. `gov doctor` D003/D004 verify the
installed payload against its manifest and the lock; any in-place edit of `governance/kernel/` is CRITICAL (INV-007).

## Repair iterations
`release/verification/<version>/` holds the independent verifier's report, harness and results (never modified by the
implementer). An implementer rerun of the unchanged harness is written next to it (`heldout-rerun/`, via
`GOV_VERIFIER_OUT`), and the repair mapping lives in `release/repair/<new-version>/REPAIR_REPORT.md`.

## Version semantics
PATCH backward-compatible repair · MINOR backward-compatible capability addition · MAJOR breaking governance/schema
contract. `gov update --check` refuses paths not covered by `supported_from_versions` + chained migrations.

## Migrations
Declarative YAML in `migrations/` (validated by `migration.schema.json`), executed by `gov update --apply` inside a
snapshot; they may only touch the overlay, the lock, generated views and derived runtime. `gov update --rollback`
restores kernel, overlay, generated views and lock from `.governance-runtime/update/<version>/`.
