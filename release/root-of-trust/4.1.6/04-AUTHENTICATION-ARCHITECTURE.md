# Output 4 — Canonical release-authentication architecture (RoT-1)

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 keeps the anchor the independent review confirmed sound and moves currency, freshness, byte binding and
> purpose checks into dedicated models: `17` trust state, `18` verify-and-use, `19` eligibility and floor, `20` rollback
> and recovery, `05` purposes.

## 1. Alternatives evaluated

| Option | Description | Non-circular | Offline | Extensible after ship | Provider-neutral | Rotation / recovery | Verdict |
|---|---|---|---|---|---|---|---|
| O1 | Harden hashes only (verify a source against its shipped manifest) | **no** (E1) | yes | yes | yes | n/a | rejected: circular |
| O2 | Binary-embedded digest registry only | yes | yes | **no** | yes | via new binary only | kept as components: compiled root, TPS, TSS, historical-identity registry, embedded statement |
| **O3** | **Signed statements under trust roots compiled into the binary (RoT-1)** | yes | yes | yes | yes | root-signed rotation, revocation, re-attestation | **recommended** |
| O4 | Keyless signing with an identity provider and transparency log | yes | partially | yes | **no** | provider-managed | rejected as root; optional additional attestation later |
| O5 | Signed Git tags or commits | partially | yes | yes | yes | tied to developer identities | rejected as root: authenticates commits, not delivered bytes |
| O6 | Full TUF including an online timestamp role | yes | **no** for freshness | yes | yes | strongest | not adopted wholesale. Revision 2 adopts TUF's root rotation, thresholds, role separation, snapshot-style trust state and monotonic counters. It replaces the online timestamp role with sticky negative facts plus “no relaxation without freshness”, and offers optional expiring trust state (OP-3 mode B). |

## 2. Components

| Component | Proposed location (4.1.6) | Responsibility |
|---|---|---|
| Trust context (T0) | `runtime/src/trust/root.rs`, `purposes.rs`; data compiled from `trust/production/` | root chain, purpose table and separation constraints, compiled TPS, TSS and historical registry |
| Canonical JSON | `trust/jcs.rs` | GOV-JCS-1 |
| DSSE | `trust/dsse.rs` | strict envelope parse; PAE; Ed25519 strict verification |
| Statements | `trust/statement.rs` | typed statements validated with compiled schemas (`07` §4) |
| Knowledge and trust state | `trust/state.rs` | knowledge set, effective root, TPS, TSS, negative set, views, staleness (`17` §5) |
| Floor and eligibility | `trust/floor.rs`, `trust/eligibility.rs` | floor operators, effective floor, eligibility predicate, install-authority floor (`19`) |
| Secure reader | `trust/secure_fs.rs` | `SecureDir`, read-once VerifiedBlobs, no-follow opens (`18` §3) |
| Governed filesystem | `trust/governed_fs.rs` | the only mutation API; Protected Path Set guard (`18` §8) |
| Authentication boundary | `trust/authenticate.rs` | the only constructor of `AuthenticatedRelease` (§3) |
| Authorisation | `trust/authorise.rs` | gates, authority floor, computed weakenings, downgrade policy (§4) |
| Install transaction | `trust/install_tx.rs` | journal, staging, read-back, exchange, lock commit, uninstall, recovery (`18` §5, `20` §5) |
| Use-time snapshot | `kernel_trust.rs` v2 + `trust/snapshot.rs` | installation state, KernelSnapshot, EmbeddedSnapshot, verdict (`18` §6, §9) |
| Format boundary | `trust/format.rs` | `FORMAT`, lock sentinels, tombstone (`13` §3) |
| Producer tools | `release.rs` (`build`, `attach-signature`, `promote`, `verify`), `trust/publish.rs` (`draft-policy`, `publish`) | unsigned payloads; verification before attaching |

Dependencies:
- one pure-Rust Ed25519 implementation with strict verification (choice recorded in ARCH-0002; replaceable);
- `sha2` (already present);
- platform secure-open primitives through a thin OS layer;
- D-0002's single self-contained binary is preserved.

## 3. Normative authentication algorithm

`authenticate(source: SourceRef, ctx: &TrustContext, req: &AdoptionRequest) -> Result<AuthenticatedRelease, TrustError>`

Every failure returns `ok: false`, the code below, and `details.stage` set to the step ID. **No byte is written to any
Protected Path before step V12 completes and authorisation (§4) succeeds.**

| Step | Action | Failure code |
|---|---|---|
| V0 | Resolve the source to `SourceRef {kind, logical reference}`. Environment variables may only select a source. | `KERNEL_SOURCE_NOT_FOUND` |
| V1 | **Secure read-once** (`18` §3–§4). Enumerate through `SecureDir`: regular files only; `gov-tree-v2` path rules (`07` §5); limits. Read each file once into a VerifiedBlob candidate (bytes + SHA-256). Archives are streamed into buffers under the same rules. Nothing is extracted to disk. | `RELEASE_TREE_INVALID` (`rule`, `path`) |
| V2 | Locate statements: the release envelope (`release-final.dsse.json` or `release-candidate.dsse.json` at bundle root; `release/releases/<version>/` for a canonical checkout; compiled for the embedded payload), the promoted-from candidate envelope (`lineage/`), and bundle trust metadata (`trust/`). No release envelope → production: `UNSIGNED_SOURCE_REFUSED` unless the explicit development path applies (§8). **A present but failing statement never falls back to the development path.** | `RELEASE_STATEMENT_MISSING` / `UNSIGNED_SOURCE_REFUSED` |
| V3 | Strict envelope and canonical payload for every statement found (`05` SV-1…SV-3). | `STATEMENT_MALFORMED` / `STATEMENT_TYPE_UNKNOWN` / `STATEMENT_SOURCE_NOT_PERMITTED` |
| V4 | Build the knowledge set and effective state (`17` S1–S10): effective root, TPS, admissible TSS, negative set, views, staleness. A compiled root, TPS or registry that does not verify makes the binary refuse every authenticated operation (`TRUST_ROOT_INVALID`); there is no unsigned fallback. | `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` / `TRUST_STATE_REGRESSION` / `BINARY_BELOW_TRUST_POLICY` |
| V5 | Purpose-bound signatures on the release statement (and the candidate, if present) (`05` SV-4…SV-7). | `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` / `THRESHOLD_NOT_MET` |
| V6 | Payload validated with the **compiled** schema for its payloadType (`05` SV-8), never a schema from the material under authentication. | `STATEMENT_MALFORMED` |
| V7 | Type, stage and profile consistency (`05` SV-9, SV-10 profile): `_type`, `signing.purpose`, `release.stage` ↔ payloadType; `trust_profile` = binary profile. | `STATEMENT_TYPE_MISMATCH` / `TRUST_PROFILE_MISMATCH` |
| V8 | **Identity, lineage, promotion.** `trust_root_id` = binary lineage (`STATEMENT_LINEAGE_MISMATCH`). `framework` = compiled name. `release.version` = the version parsed from the `KERNEL.yaml` blob. `release.release_id` = `<framework>@<version>#<first 16 hex characters of the tree-digest hex, without the sha256: prefix>`, recomputed. Requested version or digest (if any) match. For stage `final`: the `promoted_from_candidate` envelope is present, verifies under `release-candidate` (V3–V7), and has an identical `kernel.tree_digest`. For reinstall: the statement digest equals the installed one. | `RELEASE_IDENTITY_MISMATCH` / `RELEASE_REPLAY_DETECTED` / `STATEMENT_LINEAGE_MISMATCH` |
| V9 | **Content.** Compare every VerifiedBlob digest with `kernel.files`: report `modified`, `missing`, `added`. Recompute `tree_digest`, `manifest_digest` and every `components.*` digest from the blob map. A source `KERNEL_MANIFEST.json` is excluded and ignored. | `RELEASE_DIGEST_MISMATCH` |
| V10 | **Migrations.** Every `migrations/*.yaml` blob appears in `migrations[]` with identical `path` and `digest`. `id`, `from_version`, `to_version`, `breaking` and `human_gate` parsed from the blob equal the entry. `from_version` values are unique (a single chain). Nothing outside the blob set is ever loaded. | `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` / `MIGRATION_CHAIN_AMBIGUOUS` |
| V11 | **Compatibility.** CLI version within `compatibility.cli`; binary supports `kernel_contract_version` and `floor_schema_version`; for update, the installed version is in `supported_from_versions` and a complete migration path exists **using statement data only**. | `RELEASE_INCOMPATIBLE` |
| V12 | Produce the `AuthenticatedRelease`: `{P, D, CI, signer key ids, purpose, trust_root_id, root version, blobs, candidate digest, trust_references}`. | — |

## 4. Authorisation (after V12, before any trusted write)

| Decision | Inputs | Defined in |
|---|---|---|
| Is the release eligible for this operation? | ARO, T0, effective TPS, negative set, trust state, VTS per-project record, installed verdict | `19` §6 (E1–E9) |
| Is trust state sufficient? | staleness, hint mismatch, operation class | `17` §7 |
| Which gate is required? | OP-3 mode (TPS `gating`), certification view, computed weakenings, signer-declared breaking changes and gates, downgrade | `17` §7, `19` §9, `20` §4, `21` OP-3 |
| Which gate authorises it? | a presented, answered-A Human Decision Gate whose `release_statement_digest` (and, for downgrade, both digests; for weakenings, the list digest) matches exactly | `09` R-UPD |
| Is the actor authorised? | install-authority floor: TPS ⊔ EmbeddedSnapshot ⊔ current eligible KernelSnapshot ⊔ overlay; **never the target** | `19` §8 |
| Is the transaction possible now? | installation state, transaction lock, platform primitives | `18` §5, §9 |

## 5. Use-time verification (`kernel_trust` v2)

Algorithm: `18` §6. Inputs: installation state; `governance/trust/release.dsse.json`; the installed tree read once
through the secure reader; T0; the knowledge set; the VTS per-project record. `framework.lock` is read only for record
cross-checks and hints.

| Check | Detects |
|---|---|
| installation state (`18` §9) | partial or interrupted installs; unknown formats |
| statement verifies under T0 for `release-final` or `release-candidate`, lineage and profile | Git-delivered forged or regenerated sets (E4); wrong lineage |
| installed file map ≡ statement `kernel.files` (from snapshot buffers) | post-install tampering (V-H2 preserved) |
| eligibility E1–E7, E10 | legacy, below-policy, revoked, candidate, binary-below-policy, unregistered floors, downgrade without transaction |
| trust-state status | stale or regressed metadata (use continues except on regression) |
| lock identity ≡ statement | edited lock (`LOCK_IDENTITY_MISMATCH`) |

Verdict axes and the definition of `verified`: `19` §6.

Enforcement:
- When `verified` is false, constitutional content comes from the EmbeddedSnapshot joined with the effective floor.
- Mutations fail closed: `KERNEL_TAMPERED` (integrity), `KERNEL_UNAUTHENTICATED` (authenticity), `KERNEL_INELIGIBLE`
  (eligibility), `INSTALL_STATE_PARTIAL`, `INSTALL_IN_PROGRESS`.
- Exempt remedies: read-only diagnostics, `gov recover`, `gov kernel reinstall` (authenticated, same identity), and
  `gov update --apply` to an eligible target (strictly trust-increasing; gates and authority evaluated with the floor).

There is no cross-process verdict cache: anything under `.governance-runtime/` is writable by A3.

## 6. Making “manufacturing trust” unrepresentable (API rules)

1. `AuthenticatedRelease` has private fields, no `Deserialize`, no public constructor, and is never persisted.
2. `install_tx` entry points accept `&AuthenticatedRelease` (or an authenticated, eligibility-checked restore target) and
   `&Authorisation`. They mint the only `InstallTxToken`. No function installs from a `Path`.
3. The lock writer accepts only the transaction's `InstalledRelease`. There is no migration lock operation.
4. Migrations and templates are read from ARO blobs (ingress) or the KernelSnapshot (use); `load_migrations(&Path)` is
   removed.
5. `build_manifest`, `stage_payload` and tree hashing over paths are private to the producer (`release.rs`).
6. `GovernedFs` is the only mutation API; `std::fs` mutation calls outside it fail an architecture test.
7. The `release_ingress` conformance family asserts rules 1–6 by source inspection **and** by filesystem interception
   across every CLI command (`02` §5).
8. A test hook asserts that no Protected Path mutation occurs before V12 and authorisation, for every failure injection.

## 7. Embedded baseline

`18` §7: in-memory EmbeddedSnapshot, verified against its compiled statement at first use; never materialised for trust;
no cache.

A binary built from a tree without a matching signed final statement has an embedded kernel of `DEVELOPMENT_UNSIGNED`.
A production-profile development binary therefore cannot install its own embedded kernel as authenticated or eligible.

## 8. Development and test paths

| Binary | Source | Acceptance | Policy root | Verdict |
|---|---|---|---|---|
| `gov` (production) | signed final under the production lineage | normal (eligibility, gates) | installed snapshot if eligible | `AUTHENTICATED` / `ELIGIBLE` |
| `gov` (production) | signed candidate | only with evaluation flag + gate (TPS permitting) | installed snapshot | `ELIGIBLE_EVALUATION` |
| `gov` (production) | no statement | refused `UNSIGNED_SOURCE_REFUSED`; with `--allow-unsigned-development`: installs and writes `governance/trust/development.json` (unsigned acknowledgement record) | **EmbeddedSnapshot ⊔ floor**; mutations need the fingerprint-bound override gate | `DEVELOPMENT_UNSIGNED`, `verified: false` |
| `gov` (production) | test-profile statement, root or record | refused | — | `TRUST_PROFILE_MISMATCH` |
| `gov-test-profile` | test-signed statement | normal | installed snapshot | `TEST` |
| `gov-test-profile` | no statement, or a historical identity | accepted, labelled | installed snapshot | `DEVELOPMENT_UNSIGNED` / `HISTORICAL_IDENTIFIED` (test) |

A present but invalid statement is refused in every profile. No path writes an `AUTHENTICATED`, `ELIGIBLE` or
certification view for unsigned or test material. Production binaries refuse locks and trust records whose profile is
`test`.

## 9. Producer and signer interface

`07` §7.
