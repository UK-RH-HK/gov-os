# Output 8 — Project layout, `framework.lock` and the project trust record

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 keeps the legacy-path-occupation layout; review r3 recorded R2-H4 as CLOSED as a class. It changes the
> ignore rule, so the tracked migration occupation is not listed by `git ls-files -ci --exclude-standard` (RV3-L7). The
> held registration, the project-strength vector and the accepted-TBM high-water are VTS records, not lock fields
> (`24` §8).

## 1. Principle

The lock **records** the identity that authentication, the surface check and eligibility established, plus evidence of
the installation. It is written last inside the staged trust tree, and it is the commit point of the install transaction
(`18` §5). No component reads the lock as a source of trust:
- identity fields are cross-checked against the installed, verified statement; disagreement gives
  `LOCK_IDENTITY_MISMATCH`;
- reference fields are **hints**: warnings only (`17` S8).

## 2. Consumer layout (`rot-1/legacy-path-occupation-v1`)

```text
governance/
├── trust/                              Protected Path Set (18 §8); read and written only by kernel_trust / install_tx
│   ├── FORMAT                          {"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}
│   ├── framework.lock                  lock 3.0.0 (§3)
│   ├── kernel/**                       installed kernel payload (no KERNEL_MANIFEST.json)
│   ├── release.dsse.json               exact installed release envelope
│   ├── lineage/                        candidate statement named by promoted_from_candidate
│   ├── state/                          Project Trust Record: TSS chain, TPS versions, certification, attestation, revocation,
│   │                                   build-attestation and artefact statements; always a union (18 §5.2)
│   ├── root/<version>.dsse.json        root links newer than v1
│   ├── profiles/<profile_id>.dsse.json retrieval profile statements (10)
│   └── development.json                ONLY for DEVELOPMENT_UNSIGNED installs
├── overlay/                            project overlay (formerly governance/project); GovernedFs; strength vector (26 §6)
├── views/                              generated views (formerly governance/generated); bound to CI and policy digest
├── kernel                              occupation: regular file (sentinel)
├── project                             occupation: regular file
├── generated                           occupation: regular file
└── framework.lock/ROT-1-TRUST-FORMAT   occupation: directory with sentinel file
spec/audits/ADOPTION/                   RoT-1 adoption evidence;  spec/audits/GOVERNANCE-ADOPTION = occupation (regular file)
.governance-runtime/migration           occupation: tracked regular file, not ignored (.gitignore: /.governance-runtime/* and !/.governance-runtime/migration)
.governance-runtime/trust-tx/           install transaction area: untracked; journals honoured only if registered in the VTS (18 §5.1)
```

**Why tracked.** A second machine authenticates without network access (G5). Every file under `governance/trust/` except
`FORMAT`, `framework.lock` and `development.json` is signed. Deleting files produces `PARTIAL`, `INCOMPLETE` or
`BELOW_ANCHOR`, never trust.

**Ignore rule (RV3-L7).** The install transaction writes two `.gitignore` lines: `/.governance-runtime/*` and
`!/.governance-runtime/migration`. Every other runtime path stays ignored. The occupation file is therefore tracked and not
ignored, and the common "untrack ignored files" idiom does not list it. Revision 3 ignored the whole directory and
force-added the file, which that idiom removed from later clones. Evidence:
`evidence/RV3-D-A05-A07-rerun-r4-layout.json` (`tracked_but_ignored_listed: []`; occupation present in a fresh clone).

## 3. Lock schema 3.0.0 (`schemas/framework-lock-3.0.0.schema.json`)

| Field | Written from | Use-time check |
|---|---|---|
| `lock_schema_version` | const `3.0.0` | = FORMAT reader expectations |
| `trust_format`, `layout` | const `rot-1`, `legacy-path-occupation-v1` | = `governance/trust/FORMAT` |
| `framework`, `version`, `release_id`, `release_sequence`, `release_stage`, `release_commit` | statement | = statement |
| `kernel {tree_digest, manifest_digest}` | statement | = statement |
| `release_statement_digest` | ARO | = SHA-256 of the installed envelope payload |
| `surface {trust_policy_version, trust_policy_digest, result}` | the E7 evaluation at install | informational; recomputed per process |
| `signer {purpose, algorithm, key_ids}` | ARO | informational |
| `trust_root {profile, id, version_min, confirmation}` | TBM + VTS | `id` = binary lineage |
| `trust_references {trust_policy_version_min, trust_state_sequence_min}` | effective state at install | hints |
| `anchor_at_install {state_sequence, method}` | VTS | informational (never an anchor for other machines) |
| `project_trust_id` | random 128-bit at first install | key of the VTS per-project record (`20` §9) |
| `verdict_at_install {authenticity, eligibility, surface, certification_view, trust_state, freshness}` | verdict at commit | informational; a lock claiming a better verdict than recomputed gives `LOCK_IDENTITY_MISMATCH` |
| `source`, `source_reference` | `SourceRef` | informational; never a path |
| `installed_at`, `installed_at_commit`, `installed_by {gov_version, tbm_digest, trust_profile, session, role, authority_level}` | runtime | informational |
| `install_evidence {transaction_id, ledger_entry, trust_gate_confirmation_digest}` | transaction | informational |
| `layout_migration {from_layout, moved[], quarantined[]}` | first RoT-1 install on a legacy project (`26` §7) | informational |
| `informational {…}` | migration outputs on a compiled allowlist | informational |
| `cli_version`, `schema_versions` | statement compatibility | = statement |

**Removed from revision 2:**
- sentinel values in the 1.1.0 field names (`kernel_manifest_hash`, `release_hash`), because the legacy lock path is now a
  directory;
- the tombstone `KERNEL_MANIFEST.json`.

## 4. Writes

1. Only the install transaction writes `governance/trust/**` and occupation entries: staged in
   `.governance-runtime/trust-tx/<TX>/trust.next/`, read back, atomically exchanged (`18` §5).
2. Migrations have **no** lock operation. Informational keys go through a compiled allowlist. Any other key gives
   `MIGRATION_FAILED(lock_key_not_allowed)` and a rollback.
3. Rollback and recovery restore kernel, release statement and lock as one exchange. `state/` and `root/` are always the
   union (`18` §5.2).
4. `gov trust refresh` adds verified statements to `state/` and `root/` through a transaction and never changes identity
   fields.

## 5. Legacy locks and layouts

- A 1.1.0 lock file at `governance/framework.lock` together with a `governance/kernel/` directory is the `LEGACY` state
  (`18` §9).
- A legacy tree digest is reported as `HISTORICAL_IDENTIFIED` (TPS historical releases).
- The project is read-only with EmbeddedSnapshot ⊔ floor.
- The only path forward is an anchored install transaction to an eligible release. It performs the layout migration
  (`26` §7) and writes lock 3.0.0.

## 6. Example (3.0.0)

```json
{
  "lock_schema_version": "3.0.0", "trust_format": "rot-1", "layout": "legacy-path-occupation-v1",
  "framework": "agentic-engineering-os", "version": "4.1.6",
  "release_id": "agentic-engineering-os@4.1.6#<first 16 hex of the tree digest>", "release_sequence": 6, "release_stage": "final",
  "release_commit": "<40 hex>", "kernel": {"tree_digest": "sha256:<64 hex>", "manifest_digest": "sha256:<64 hex>"},
  "release_statement_digest": "sha256:<64 hex>",
  "surface": {"trust_policy_version": 1, "trust_policy_digest": "sha256:<64 hex>", "result": "REGISTERED"},
  "signer": {"purpose": "release-final", "algorithm": "ed25519", "key_ids": ["ed25519:<64 hex>"]},
  "trust_root": {"profile": "production", "id": "sha256:<64 hex>", "version_min": 1, "confirmation": "human"},
  "trust_references": {"trust_policy_version_min": 1, "trust_state_sequence_min": 3},
  "anchor_at_install": {"state_sequence": 3, "method": "human"},
  "project_trust_id": "<32 hex>",
  "verdict_at_install": {"authenticity": "AUTHENTICATED", "eligibility": "ELIGIBLE", "surface": "REGISTERED", "certification_view": "CERTIFIED_AS_OF(3)", "trust_state": "KNOWN(3)", "freshness": "ANCHORED(3,human,as-of 2026-10-01T09:00:00Z,0d)"},
  "source": "release:agentic-engineering-os@4.1.6", "source_reference": "github-release:<owner>/<repo>@v4.1.6",
  "installed_at": "2026-10-01T09:00:00Z", "installed_at_commit": "<consumer HEAD>",
  "installed_by": {"gov_version": "4.1.6", "tbm_digest": "sha256:<64 hex>", "trust_profile": "production", "session": "S-…", "role": "orchestrator", "authority_level": "L4"},
  "install_evidence": {"transaction_id": "TX-…", "ledger_entry": "spec/reports/framework-updates.jsonl#<n>", "trust_gate_confirmation_digest": "sha256:<64 hex>"},
  "layout_migration": {"from_layout": "legacy-4.1.x", "moved": ["governance/kernel->governance/trust/kernel", "governance/project->governance/overlay", "governance/generated->governance/views"], "quarantined": [".governance-runtime/update/4.1.5"]},
  "informational": {}, "cli_version": "4.1.6", "schema_versions": {"framework-lock": "3.0.0", "release-statement": "3.0.0"}
}
```
