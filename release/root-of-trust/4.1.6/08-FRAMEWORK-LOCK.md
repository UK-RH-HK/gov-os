# Output 8 — `framework.lock` and `governance/trust/` changes

## 1. Principle

The lock **records** the identity that release authentication established and the evidence of the installation. It is
written last, as the commit point of the install transaction. No component reads the lock as a source of trust: every
identity field is cross-checked against the installed, verified statement, and disagreement is
`LOCK_IDENTITY_MISMATCH` (doctor CRITICAL, mutating operations refused as for `KERNEL_UNAUTHENTICATED`).

## 2. Consumer layout (Git-tracked)

```text
governance/
├── kernel/                        # installed payload; KERNEL_MANIFEST.json derived deterministically from the statement
├── trust/                         # NEW — signed evidence, verified at every use
│   ├── release.dsse.json          # exact bytes of the installed release statement envelope
│   ├── certification.dsse.json    # newest verified certification statement for it (optional)
│   ├── revocations.dsse.json      # newest verified revocation statement seen (optional)
│   ├── root/<version>.json        # newer root chain links seen at install (optional)
│   └── development.json           # ONLY for DEVELOPMENT_UNSIGNED installs: unsigned file map + acknowledgement
├── project/ generated/
└── framework.lock
```

Why tracked: a second machine authenticates without network (G5); all files except `development.json` are signed, so
tampering is detected; deleting them makes the kernel `UNAUTHENTICATED` (fail closed), never trusted.

## 3. Lock schema 2.0.0 (`schemas/framework-lock-2.0.0.schema.json`)

| Field | 1.1.0 | 2.0.0 | Source at install | Use-time check |
|---|---|---|---|---|
| `lock_schema_version` | 1.1.0 | `2.0.0` | constant | — |
| `framework` | ✓ | ✓ | statement | = statement |
| `version` | ✓ | ✓ | statement `release.version` | = statement |
| `release_id` | — | ✓ | statement | = statement |
| `release_sequence` | — | ✓ | statement | = statement |
| `release_commit` | ✓ (from manifest.json / git HEAD) | ✓ (**statement only**) | statement | = statement |
| `release_hash` | ✓ (recomputed payload hash) | ✓ kept, bare hex of `kernel.tree_digest` | statement | = statement |
| `kernel_manifest_hash` | ✓ | ✓ kept, bare hex of `kernel.manifest_digest` | statement | = statement and = derived manifest |
| `release_statement_digest` | — | ✓ `sha256:…` | ARO | = SHA-256 of `governance/trust/release.dsse.json` payload |
| `signer` | — | ✓ `{role, key_ids[], algorithm}` | ARO (keys that produced valid signatures) | informational; re-derived |
| `trust_root` | — | ✓ `{profile, id, version}` | T0 at install | lineage must equal running binary's; version ≤ running high-water mark |
| `trust_level` | — | ✓ | ARO + authorisation | recomputed; a lock claiming a higher level than recomputed → `LOCK_IDENTITY_MISMATCH` |
| `certification` | — | ✓ `{status, statement_digest \| null, sequence \| null}` | V13 | recomputed from `governance/trust/certification.dsse.json` |
| `revocation_sequence_seen` | — | ✓ | V4 | high-water hint (binary floor is authoritative) |
| `source` | ✓ label | ✓ label kept (`release:` \| `embedded:` \| `source:` \| `bundle:` \| `remote:` + `<framework>@<version>`) | `SourceRef.kind` from the resolver, **not** path-string matching | informational |
| `source_reference` | — | ✓ logical, no absolute path, no credentials: `bundle:agentic-engineering-os-4.1.6.tar#sha256:…`, `github-release:<owner>/<repo>@v4.1.6`, `embedded:gov@4.1.6`, `checkout:canonical@<commit>`, `snapshot:<ledger-entry-id>` | resolver | informational |
| `installed_at` | ✓ | ✓ | clock | informational |
| `installed_at_commit` | ✓ | ✓ | consumer HEAD | informational |
| `installed_by` | — | ✓ `{gov_version, trust_profile, session, role, authority_level}` | runtime | informational |
| `install_evidence` | — | ✓ `{transaction_id, ledger_entry, gate \| null}` | transaction | ledger entry must exist in `spec/reports/framework-updates.jsonl` |
| `cli_version`, `schema_versions` | ✓ | ✓ | statement compatibility | = statement |

Removed semantics: `release_commit` is never taken from a descriptive `manifest.json` or from `git rev-parse`; `source` is
never derived from the path text (`/release/releases/`, `/kernels/`, `gov-cache`).

## 4. Writes

1. Only the install transaction writes the lock, via write-to-temp + fsync + atomic rename.
2. Migration `set_lock_field` may set only keys in an allowlist of non-identity fields (`lock_schema_version` and future
   informational keys declared in the kernel `MIGRATION` policy). Attempting `version`, `release_*`, `kernel_manifest_hash`,
   `trust_*`, `signer`, `certification`, `source*`, `install_evidence` → `MIGRATION_FAILED` with
   `details.reason: identity_field`, and the transaction rolls back.
3. Rollback restores the previous lock **and** the previous `governance/trust/` directory together, then re-verifies.

## 5. Legacy locks (1.1.0)

A 1.1.0 lock has no statement. kernel_trust v2 computes the installed tree digest; if it equals an entry of the compiled
legacy-identity statement, the kernel is `AUTHENTICATED_REJECTED` (`identity_source: legacy-identity`), otherwise
`UNAUTHENTICATED`. The lock is upgraded to 2.0.0 only by an install transaction (update or reinstall), never in place.

## 6. Example (2.0.0)

```yaml
lock_schema_version: 2.0.0
framework: agentic-engineering-os
version: 4.1.6
release_id: agentic-engineering-os@4.1.6#<first 16 hex of tree digest>
release_sequence: 5
release_commit: <40 hex from the statement>
release_hash: <64 hex tree digest>
kernel_manifest_hash: <64 hex manifest digest>
release_statement_digest: sha256:<64 hex>
signer: {role: release, algorithm: ed25519, key_ids: ["ed25519:<64 hex>"]}
trust_root: {profile: production, id: "sha256:<64 hex>", version: 1}
trust_level: AUTHENTICATED_UNCERTIFIED
certification: {status: UNCERTIFIED, statement_digest: null, sequence: null}
revocation_sequence_seen: 1
source: release:agentic-engineering-os@4.1.6
source_reference: github-release:<owner>/<repo>@v4.1.6-rc1
installed_at: "2026-10-01T09:00:00Z"
installed_at_commit: <consumer HEAD>
installed_by: {gov_version: 4.1.6, trust_profile: production, session: S-…, role: orchestrator, authority_level: L4}
install_evidence: {transaction_id: TX-…, ledger_entry: "spec/reports/framework-updates.jsonl#<n>", gate: HG-…}
cli_version: 4.1.6
schema_versions: {framework-lock: 2.0.0, release-statement: 1.0.0}
```
