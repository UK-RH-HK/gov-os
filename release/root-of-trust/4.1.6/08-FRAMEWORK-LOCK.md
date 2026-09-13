# Output 8 — `framework.lock` and the project trust record

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 adds the trust-format boundary (RV-M4, CD-8), signed-reference hints (RV-H2), removes `set_lock_field` from
> migrations (RV-M8), and renames identity fields so pre-RoT binaries cannot read them as verified.

## 1. Principle

The lock **records** the identity that authentication and eligibility established, plus evidence of the installation.
It is written last, as the commit point of the install transaction (`18` §5). No component reads the lock as a source of
trust:
- identity fields are cross-checked against the installed, verified statement; disagreement → `LOCK_IDENTITY_MISMATCH`
  (doctor CRITICAL; mutations refused as for `KERNEL_UNAUTHENTICATED`);
- reference fields are **hints** (`17` S8): they can only produce `HINT_MISMATCH`, never relax anything.

## 2. Consumer layout (Git-tracked; entirely inside the Protected Path Set, `18` §8)

```text
governance/
├── kernel/                        installed payload (verified per process into a KernelSnapshot)
│   └── KERNEL_MANIFEST.json       compatibility tombstone for pre-RoT binaries (13 §3); never read by RoT-1 binaries
├── trust/
│   ├── FORMAT                     {"minimum_reader":"4.1.6","trust_format":"rot-1"}  (GOV-JCS-1 bytes)
│   ├── release.dsse.json          exact bytes of the installed release-final (or candidate, evaluation projects) envelope
│   ├── lineage/                   candidate statement named by promoted_from_candidate (needed for V8 promotion check)
│   ├── state/                     Project Trust Record: TSS chain, TPS versions, certification, attestation and
│   │                              revocation statements known at install or refresh (17 §4)
│   ├── root/<version>.dsse.json   root links newer than version 1 known at install or refresh
│   └── development.json           ONLY for DEVELOPMENT_UNSIGNED installs: unsigned record + acknowledgement
├── .tx/                           install transaction area (18 §5.1); normally empty
├── project/  generated/           project state (not protected; written through GovernedFs)
└── framework.lock
```

Why tracked: a second machine authenticates without network access (G5). Every file except `FORMAT` and
`development.json` is signed. Deleting files produces `PARTIAL`, `STALE` or `HINT_MISMATCH`, never trust.

## 3. Lock schema 2.0.0 (`schemas/framework-lock-2.0.0.schema.json`)

| Field | 1.1.0 | 2.0.0 | Written from | Use-time check |
|---|---|---|---|---|
| `lock_schema_version` | 1.1.0 | const `2.0.0` | constant | = `FORMAT` reader expectations |
| `trust_format` | — | const `rot-1` | constant | = `governance/trust/FORMAT` |
| `kernel_manifest_hash` | hex hash | **const sentinel** `ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project` | constant | ignored by RoT-1 binaries; makes pre-RoT binaries fail closed (`13` §3) |
| `release_hash` | hex hash | **const sentinel** (same string) | constant | same |
| `framework` | ✓ | ✓ | statement | = statement |
| `version` | ✓ | ✓ | statement `release.version` | = statement |
| `release_id`, `release_sequence`, `release_stage` | — | ✓ | statement | = statement |
| `release_commit` | from manifest.json or `git rev-parse` | ✓ statement only | statement | = statement |
| `kernel.tree_digest`, `kernel.manifest_digest` | — (were `release_hash`, `kernel_manifest_hash`) | ✓ `sha256:` prefixed | statement | = statement |
| `release_statement_digest` | — | ✓ | ARO | = SHA-256 of the installed envelope payload |
| `signer {purpose, algorithm, key_ids}` | — | ✓ | ARO (keys with valid signatures) | informational; re-derived |
| `trust_root {profile, id, version_min, confirmation}` | — | ✓ | T0 + VTS at install | `id` = binary lineage (else `TRUST_ROOT_LINEAGE_MISMATCH`); `version_min` hint |
| `trust_references {trust_policy_version_min, trust_state_sequence_min}` | — | ✓ | effective state at install | hints (`17` S8) |
| `project_trust_id` | — | ✓ random 128-bit id created at first install | install transaction | key of the VTS per-project record (`20` §9) |
| `verdict_at_install {authenticity, eligibility, certification_view, trust_state}` | — | ✓ | verdict at commit | informational; recomputed per process; a lock claiming a better verdict than recomputed → `LOCK_IDENTITY_MISMATCH` |
| `source`, `source_reference` | label | label + logical reference | `SourceRef` | informational; never a path |
| `installed_at`, `installed_at_commit` | ✓ | ✓ | clock, consumer HEAD | informational |
| `installed_by {gov_version, trust_profile, session, role, authority_level}` | — | ✓ | runtime | informational |
| `install_evidence {transaction_id, ledger_entry, gate}` | — | ✓ | transaction | ledger entry written idempotently from the journal (`18` §4) |
| `informational {…}` | — | ✓ | migration outputs on a compiled allowlist | informational only |
| `cli_version`, `schema_versions` | ✓ | ✓ | statement compatibility | = statement |

Removed semantics:
- `release_commit` never comes from `manifest.json` or `git rev-parse`;
- `source` is never derived from path text;
- the hashes previously under `release_hash`/`kernel_manifest_hash` moved to `kernel.*` so no pre-RoT binary can match them.

## 4. Writes

1. Only the install transaction writes the lock: temp file in `.tx/<TX>/`, `fsync`, atomic rename, `fsync` of
   `governance/`.
2. Migrations have **no** lock operation. Rev 1's `set_lock_field` is removed. A migration may emit values for a compiled
   allowlist of informational keys; the transaction places them under `informational`. Any other key →
   `MIGRATION_FAILED` (`details.reason: lock_key_not_allowed`) and rollback.
3. Rollback and recovery restore the lock, `governance/kernel/` and `governance/trust/` as one transaction (`20`).
4. `gov trust refresh` may add verified statements to `governance/trust/state/` and `root/` through the transaction
   area. It never changes identity fields.

## 5. Legacy locks (1.1.0)

A 1.1.0 lock has no statement, no FORMAT file and no trust record. The installation state is `PARTIAL`
(`18` §9), and a legacy tree digest is reported as `HISTORICAL_IDENTIFIED`, never eligible (`19` §7). The project runs
read-only with the EmbeddedSnapshot ⊔ floor. The only path forward is an install transaction to an eligible release,
which writes lock 2.0.0 and the trust record. The lock is never upgraded in place.

## 6. Example (2.0.0)

```yaml
lock_schema_version: 2.0.0
trust_format: rot-1
kernel_manifest_hash: "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project"
release_hash: "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project"
framework: agentic-engineering-os
version: 4.1.6
release_id: agentic-engineering-os@4.1.6#<first 16 hex of the tree digest>
release_sequence: 6
release_stage: final
release_commit: <40 hex from the statement>
kernel: {tree_digest: "sha256:<64 hex>", manifest_digest: "sha256:<64 hex>"}
release_statement_digest: "sha256:<64 hex>"
signer: {purpose: release-final, algorithm: ed25519, key_ids: ["ed25519:<64 hex>"]}
trust_root: {profile: production, id: "sha256:<64 hex>", version_min: 1, confirmation: human}
trust_references: {trust_policy_version_min: 1, trust_state_sequence_min: 3}
project_trust_id: "<32 hex>"
verdict_at_install: {authenticity: AUTHENTICATED, eligibility: ELIGIBLE, certification_view: "CERTIFIED_AS_OF(3)", trust_state: "CURRENT_KNOWN(3)"}
source: release:agentic-engineering-os@4.1.6
source_reference: github-release:<owner>/<repo>@v4.1.6
installed_at: "2026-10-01T09:00:00Z"
installed_at_commit: <consumer HEAD>
installed_by: {gov_version: 4.1.6, trust_profile: production, session: S-…, role: orchestrator, authority_level: L4}
install_evidence: {transaction_id: TX-…, ledger_entry: "spec/reports/framework-updates.jsonl#<n>", gate: HG-…}
informational: {}
cli_version: 4.1.6
schema_versions: {framework-lock: 2.0.0, release-statement: 2.0.0}
```
