# Output 11 — Migration plan from 4.1.5

4.1.5 stays immutable and REJECTED; nothing in `release/releases/4.1.2…4.1.5` or any verifier directory is edited.

## Phase 0 — Owner approval and key ceremony (before any code)

1. Present D-0008 as a Human Decision Gate; the owner answers, fixing OP-1…OP-6.
2. Root ceremony (offline): 3 root keys, threshold 2; release (active + standby), certification (active + standby) and
   profile keys; trust-root v1 signed; key ids and trust-root id recorded in a governed ceremony record (public data only)
   and published per `06-BOOTSTRAP.md` §2.
3. Test lineage generated for fixtures (`tests/fixtures/trust/`), clearly labelled `trust_profile: test`.

Exit: D-0008 ACTIVE (human-approved), D-0007 SUPERSEDED, ARCH-0002 ACTIVE, public trust root committed under
`trust/production/`.

## Phase 1 — Legacy identity statement

1. Independently reproduce 4.1.2, 4.1.3, 4.1.4 and 4.1.5 payloads from their recorded `release_commit`s (`git archive`,
   as the 4.1.5 verifier did) and confirm the tree digests equal the published `release_hash` values:
   4.1.2 `9964830b…` (`f709834`), 4.1.3 `6bebfdbb…` (`78f6853`), 4.1.4 `e5e2f2c7…` (`c6b594b`), 4.1.5 `962f9848…`
   (`25dac6e`).
2. Certification role signs `legacy-identity.dsse.json` listing version, release id, commit, tree and manifest digests,
   certification status `REJECTED` and verifier report digests.
3. Not revoked: the defects of 4.1.x lie in the binaries' install and use logic, not in kernel content; they are
   installable only as `AUTHENTICATED_REJECTED` under OP-3 policy.

## Phase 2 — Implementation on `release/4.1.6-rc1` (builder)

| Work package | Content | Requirements |
|---|---|---|
| WP-1 trust core | `runtime/src/trust/{root,jcs,dsse,statement,quarantine,authenticate,authorise,revocation,install_tx,kernel_fs}.rs`; Ed25519 dependency (strict verification, pure Rust) | `04`, `07` |
| WP-2 ingress rewiring | init, init --force, adopt batch 0, update check/apply/auto-rollback, rollback, kernel reinstall, recover, release build/verify/attach-signature, `trust show|verify-artifact|refresh`, `release fetch` (transport-only, may be deferred) | `09` §2 |
| WP-3 use-time | kernel_trust v2, `TrustedKernel` for every reader in I-17, D030–D033, context/status surfacing | `04` §5, R-USE |
| WP-4 embedded | build.rs embeds statement bytes; in-memory baseline; cache never trusted | R-EMB |
| WP-5 schemas | `framework/schemas/` gains trust-root, dsse-envelope, release/certification/revocation/artifact/profile/legacy-identity statement schemas and framework-lock 2.0.0 (drafts in `schemas/` here); the runtime compiles the statement schemas in | `07`, `08` |
| WP-6 kernel policy | `SECURITY_POLICY.release_trust {minimum_trust_level, require_certified_for_unattended_update, metadata_freshness_warning_days}` with precedence rules (strengthen only); `AUTHORITY_POLICY` levels for `trust_refresh`, `allow_unsigned_development`; migration `set_lock_field` allowlist | `04` §8, `08` §4 |
| WP-7 conformance | `release_ingress` family, private-key scan, fs-write-before-authentication hook, cross-implementation crypto vectors | `04` §4 |
| WP-8 tests | builder certification suite on the test profile; updated fixtures signed at test time | `12` |
| WP-9 docs/governing | `docs/ARCHITECTURE.md` §4.4a, `docs/RELEASE.md`, release/distribution protocol amendment (§8 manifest → statement, §9 init, §12 update, §16 cross-machine, bootstrap), `.gitattributes` | `06`, `07` |
| WP-10 migration | `migrations/M-4.1.5-4.1.6.yaml`: notes; `set_lock_field lock_schema_version 2.0.0`; `require_index_rebuild` only if the index version changes; `regenerate_adapters`. Trust files and lock identity are written by the install transaction, not by migration ops | `08` |

## Phase 3 — Candidate, verification, certification

1. `gov release build --version 4.1.6` → payload, descriptive manifests, `release.statement.json`.
2. Owner reproduces on the isolated host, signs, runs `gov release attach-signature`; commit; tag `v4.1.6-rc1`.
3. Independent verification with the production-profile binary per `12-ACCEPTANCE-TEST-PLAN.md`.
4. Verdict → certification role signs a certification statement (`CERTIFIED` or `REJECTED`) referencing the report digest;
   committed under `release/releases/4.1.6/certification/`; the descriptive manifest block is transcribed as today.

## Phase 4 — Consumer transition

| Consumer state | With the 4.1.6 binary | Path |
|---|---|---|
| lock 1.1.0, kernel equals a legacy digest | `AUTHENTICATED_REJECTED` (legacy), operates, doctor HIGH | `gov update --apply --source <signed 4.1.6>` through gate → lock 2.0.0 + `governance/trust/` |
| lock 1.1.0, kernel matches no known identity | `UNAUTHENTICATED`, floors from embedded baseline, mutations refused | same update (R-UPD-12) or `kernel reinstall` from the matching legacy release |
| 4.1.6 authenticated | normal | — |
| rollback 4.1.6 → 4.1.5 | snapshot authenticated via legacy identity; gate (trust decrease) | `gov update --rollback` |

## Phase 5 — Deprecations and follow-ups

- Removed: `GOV_KERNEL_SOURCE`; path-string source labelling; `stage_payload` parent fallback on consumer paths;
  any decision read from `manifest.json`.
- Retained: `GOV_CANONICAL_ROOT` (source selection only), `GOV_KERNEL_CACHE` (location only), fingerprint-bound override.
- Later MINOR releases: `gov release fetch` for private GitHub, reference profile statements and `gov profile install`,
  optional supplementary transparency attestation.
