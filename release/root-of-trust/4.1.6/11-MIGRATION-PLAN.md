# Output 11 — Migration plan from 4.1.5

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> 4.1.5 stays immutable and REJECTED. Nothing in `release/releases/4.1.2…4.1.5` or any verifier or review directory is
> edited. No phase below starts before a fresh independent review accepts revision 2 and the owner answers the D-0008
> gate.

## Phase 0 — Review, approval, key ceremony (before any code)

1. A **fresh** independent architecture review of revision 2. The reviewer of revision 1 authored this amendment's
   inputs, so it cannot review it.
2. Present D-0008 as a Human Decision Gate. The owner answers OP-1…OP-6 (`21`).
3. **Root ceremony** (offline), per OP-1/OP-2:
   - root keys with threshold;
   - keys for `release-final` (+ standby), `release-candidate`, `verification-attestation`, `certification-status`
     (+ standby), `revocation`, `trust-state` and `retrieval-profile`, with grants satisfying KS-1…KS-7;
   - root v1 signed; trust-root id computed;
   - public ceremony record under `spec/`;
   - fingerprint published in at least two channels independent of the release host (`06` §2 step 2).
4. **TPS v1.** `gov trust draft-policy` output generated from the 4.1.6 kernel constitutional files (`19` §4), with
   `eligibility.min_release_sequence` = the sequence assigned to the first 4.1.6 candidate, `min_binary_version: 4.1.6`,
   and `gating` per the OP-3 answer. Reviewed and signed at root threshold.
5. **TSS 1.** References TPS v1; no certifications; revocations of nothing (historical releases are excluded by
   eligibility, not revocation).
6. **Test lineage** generated for fixtures (`tests/fixtures/trust/`) covering all nine purposes, compiled only into
   `gov-test-profile`.

**Exit:** D-0008 ACTIVE (human-approved) with rules (1)–(18); D-0007 SUPERSEDED; ARCH-0002 ACTIVE; public trust data
committed under `trust/production/`; the record schema gains a `PROPOSED` status (RV-L4). The design commits are placed
on the branch the owner chooses; revision 1 was committed on the rejected `release/4.1.5-rc1` branch (RV-L3).

## Phase 1 — Historical-identity registry

1. Independently reproduce the 4.1.2, 4.1.3, 4.1.4 and 4.1.5 payloads from their recorded release commits and confirm the
   tree digests: `9964830b…` (`f709834`), `6bebfdbb…` (`78f6853`), `e5e2f2c7…` (`c6b594b`), `962f9848…` (`25dac6e`).
   The independent review reproduced these (`../4.1.6-review/evidence/continuity-check-4.1.2-4.1.5.txt`).
2. Sign `historical-identity.dsse.json` under `release-final` with status `REJECTED` and verifier report digests.
3. Commit under `trust/production/`. It is compiled into binaries only (`05` §2).
4. These releases are **never eligible** (`19` §7). This replaces rev 1's claim that their defects were binary-only,
   which the review disproved.

## Phase 2 — Implementation on `release/4.1.6-rc1` (builder)

| Work package | Content | Governing sections |
|---|---|---|
| WP-1 trust core | `trust/{root, purposes, jcs, dsse, statement}.rs`; purpose table; KS-1…KS-7; Ed25519 strict dependency | `05`, `07` |
| WP-2 trust state | `trust/state.rs`: knowledge set, admissibility, negative set, views, staleness, VTS (account-database location), PTR | `17` |
| WP-3 floor and eligibility | `trust/floor.rs`, `trust/eligibility.rs`: operators, effective floor, E1–E10, install-authority floor, computed weakenings | `19` |
| WP-4 secure filesystem and snapshot | `trust/secure_fs.rs`, `trust/snapshot.rs`, `kernel_trust.rs` v2: `SecureDir`, VerifiedBlob, KernelSnapshot, EmbeddedSnapshot, installation state machine; every reader in `02` I-17 rewired to the snapshot | `18` §1–§3, §6–§7, §9 |
| WP-5 governed filesystem | `trust/governed_fs.rs`; every mutation site in `02` §4 rewired, including CIT operations, adoption executor, recovery, indexer, adapters, tools, upstream, lessons | `18` §8, `20` §6–§7 |
| WP-6 install transaction and recovery | `trust/install_tx.rs`: journal, staging, read-back, exchange, lock commit, uninstall, snapshot writes, recovery | `18` §5, `20` |
| WP-7 ingress rewiring | init, init --force, adopt batch 0, update check/apply, rollback, reinstall, recover, profile install, trust refresh | `09` §2 |
| WP-8 format boundary | `FORMAT`, lock 2.0.0 with sentinels, tombstone manifest | `08`, `13` §3 |
| WP-9 producer and publisher | `release build`, `attach-signature`, `promote`, `verify`; `trust draft-policy`, `trust publish`, `trust export`; floor registration checks; deterministic inputs | `07` §7 |
| WP-10 schemas and kernel policy | `framework/schemas/` gains the revision 2 statement, lock and FORMAT schemas (drafts in `schemas/`); `AUTHORITY_POLICY` gains `rollback_apply`, `trust_refresh`, `trust_confirm_root`, `allow_unsigned_development`, `install_evaluation_candidate`; POLICY_PRECEDENCE rules for them | `19` §8 |
| WP-11 conformance | `release_ingress` family; filesystem interception across all commands; private-key scan; floor-regression pipeline check; separate `gov-test-profile` binary with `compile_error!` guard | `02` §5, `05` §10 |
| WP-12 documentation | `docs/ARCHITECTURE.md` §4.4a (integrity, authenticity, eligibility); `docs/RELEASE.md`; release/distribution protocol amendment (statements, promotion, trust state, bootstrap channels, OP-6); `.gitattributes` | `06`, `07` |
| WP-13 migration | `migrations/M-4.1.5-4.1.6.yaml`: notes and `regenerate_adapters`, plus `require_index_rebuild` if the index format changes. No lock operation. Trust files and lock are written by the install transaction. | `08` §4 |
| WP-14 profiles (may slip to a MINOR) | `gov profile install`, CAS store, host verification | `10` |

## Phase 3 — Candidate, verification, promotion, certification, publication

1. `gov release build --version 4.1.6` → unsigned candidate payload (floors registered in TPS v1).
2. Owner reproduces on the signing host and signs under `release-candidate`; `gov release attach-signature`; commit; tag
   `v4.1.6-rc1`.
3. Independent verification on the production binary and `gov-test-profile`, per `12`.
4. Verifier signs a `verification-attestation` (ACCEPTED or REJECTED).
5. If ACCEPTED: `gov release promote` → owner reproduces and signs under `release-final` → `certification-status`
   CERTIFIED referencing the attestation → `gov trust publish` → TSS 2 signed.
   If REJECTED: the attestation (and a `refuse_install` revocation, per OP-4) is referenced in TSS 2; the candidate is
   never promoted; a new candidate follows.
6. Binaries built from the final tag compile TPS v1 and the newest TSS.

## Phase 4 — Consumer transition

| Consumer state | With a 4.1.6 binary | Path |
|---|---|---|
| lock 1.1.0, legacy kernel | `PARTIAL` + `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)`, read-only | confirm lineage (OP-6) → `gov update --apply --source <signed final 4.1.6>` through the gate → lock 2.0.0 and trust record |
| lock 1.1.0, unknown kernel | `PARTIAL`, read-only | same |
| 4.1.6 eligible | normal | — |
| rollback 4.1.6 → 4.1.5 | **refused** (`SNAPSHOT_INELIGIBLE(historical)`) | recover with a newer eligible release or `kernel reinstall` of 4.1.6 |
| 4.1.5 binary used on a 4.1.6 project | fails closed (`13` §3) | use a ≥ 4.1.6 binary |

Revision 1's rollback path from 4.1.6 to 4.1.5 through a gate is removed (`13` §6).

## Phase 5 — Deprecations and follow-ups

- **Removed:** `GOV_KERNEL_SOURCE`, `GOV_KERNEL_CACHE`, path-string source labelling, `stage_payload` parent fallback on
  consumer paths, any decision read from `manifest.json`, the migration `set_lock_field` operation, and
  `load_migrations(&Path)`.
- **Retained:** `GOV_CANONICAL_ROOT` (source selection only); the fingerprint-bound override.
- **Later MINOR releases:** `gov release fetch` for private GitHub; reference profile statements and `gov profile install`
  (if WP-14 slips); optional supplementary transparency attestation.
