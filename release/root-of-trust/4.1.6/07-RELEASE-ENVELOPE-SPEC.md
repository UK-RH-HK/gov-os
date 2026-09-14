# Output 7 — Envelope and statement specification

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 changes the statement set:
> - release statement v3 (no `security_critical`; references are release-local);
> - Trust Policy v2 (Constitutional Surface, cumulative chains, historical releases, bootstrap);
> - Trust State v2 (`prior_states`, `artifacts`, resolved references);
> - artefact statement v3 under `release-artifact`, with a Trust Base Manifest;
> - a new build attestation;
> - certification v3;
> - the historical-identity statement withdrawn.
>
> Machine-readable schemas: `schemas/`. Revision-2 examples under `examples/rev2/` are superseded
> (`examples/README.md`).

## 1. Layers

```text
<statement>.dsse.json = DSSE envelope (JSON)
  payloadType         = application/vnd.agentic-engineering-os.<type>.<version>+json      (compiled table: 05 §2)
  payload             = base64( GOV-JCS-1 canonical bytes of the statement object )
  signatures[]        = { keyid: "ed25519:<64 hex>", sig: base64( Ed25519( PAE(payloadType, payload_bytes) ) ) }   (≥ 1)
PAE(type, body)       = "DSSEv1" SP LEN(type) SP type SP LEN(body) SP body
statement_digest      = "sha256:" + hex( SHA-256( payload_bytes ) )
content identity (CI) = ( release statement_digest, kernel.tree_digest )
```

## 2. Canonical serialisation profile GOV-JCS-1

Unchanged from revision 2 (RFC 8785 restrictions):
- ASCII member names, sorted;
- no duplicate names;
- integers only in ±(2^53−1);
- NFC strings;
- depth ≤ 32;
- payload ≤ 4 MiB;
- re-serialisation equality.

**Decimal values.** Values that are fractional in kernel YAML (for example `min_confidence: 0.8`) appear in statements as
decimal strings (`"0.8"`). Pinned-value digests use the canonical form of `23` §3.3.

## 3. Release statement v3

payloadType `release-final.v2+json` (`release-final`) or `release-candidate.v2+json` (`release-candidate`); `_type`
`https://agentic-engineering-os/statement/release/v3`. Schema: `schemas/release-statement.schema.json`.

| Field | Req | Semantics | Checked at |
|---|---|---|---|
| `_type`, `trust_profile`, `trust_root_id`, `framework`, `manifest_version` (const `3`) | ✓ | as revision 2 | V6–V8 |
| `release.{version, release_id, sequence, stage, promoted_from_candidate, release_commit, release_tag, released_at}` | ✓ | as revision 2 | V7, V8, E2, E3, E9, E10 |
| `signing.{purpose, algorithm}` | ✓ | as revision 2 | V7 |
| `trust_references.{root_version, trust_policy_version, trust_state_sequence}` | ✓ | **Release-local requirements** (`17` S7). `trust_policy_version` is the **named TPS** the producer registered the surface under (E7). None of them changes global state. | S7, E7, E8 |
| `compatibility.*` | ✓ | as revision 2 | V11, E5 |
| `kernel.{tree_rules, file_count, files, tree_digest, manifest_digest}` | ✓ | as revision 2 | V9 |
| `components`, `migrations[]`, `update_impact`, `documents`, `profiles[]`, `provenance` | ✓ | as revision 2 | V9, V10, `04` §4 |

**Removed:** `security_critical`. Which content is constitutional is decided by the root-signed Constitutional Surface
(`23`), not by the release signer.

## 4. Other statements

| Statement | payloadType | Purpose | Key fields | Schema |
|---|---|---|---|---|
| Trust root v2 | `trust-root.v2+json` | `root` | `version`, `lineage.trust_root_id`, `keys{}`, `purposes{}` for all **eleven** purposes, `revoked_keys[]` | `trust-root.schema.json` |
| **Trust Policy v2** | `trust-policy.v2+json` | `trust-policy` | `policy_version`, `supersedes_policy_digest`, **`prior_policies[]`**, `floor_schema_version` (2), **`surface`** (Constitutional Surface Inventory, `23`), `eligibility` (with **`historical_releases[]`**), `install_authority`, `gating` (with **`local_terminal_only[]`**), **`bootstrap`**, `sensitivity_order`, **`lowering_history[]`**, `unrevokes[]`, `state_chain_reset` | `trust-policy-statement.schema.json`, `constitutional-surface-inventory.schema.json` |
| **Trust State v2** | `trust-state.v2+json` | `trust-state` | `sequence`, `previous_state_digest`, **`prior_states[]`**, `references{root_version, root_digest, trust_policy{policy_version, statement_digest}}`, `revocations[]`, `certifications[]`, `attestations[]`, **`artifacts[]`**, `expires_at` | `trust-state-statement.schema.json` |
| Verification attestation | `verification-attestation.v1+json` | `verification-attestation` | as revision 2 | `verification-attestation.schema.json` |
| **Certification v3** | `certification-status.v2+json` | `certification-status` | as revision 2, plus optional `artifact_statement_digests[]` (informational in mode A) | `certification-statement.schema.json` |
| Revocation v2 | `revocation.v2+json` | `revocation` | as revision 2; `kind` includes `artifact` and `build-attestation` | `revocation-statement.schema.json` |
| **Artefact v3** | `artifact-final.v2+json` / `artifact-candidate.v2+json` | **`release-artifact`** / `release-candidate` | `stage`, `release_id`, `release_statement_digest`, `artifacts[]{name, target, digest, size, trust_profile, tbm_digest, tbm}`, `build{toolchain, build_inputs_digest, reproducible: true}` | `artifact-statement.schema.json`, `trust-base-manifest.schema.json` |
| **Build attestation** | `build-attestation.v1+json` | `build-attestation` | `artifact{name, target, digest, size}`, `source_commit`, `build_inputs_digest`, `tbm_digest`, `reproduced` (const true), `rebuilder_label`, `method` | `build-attestation.schema.json` |
| Retrieval profile | `retrieval-profile.v1+json` | `retrieval-profile` | `10` §3 | `profile-statement.schema.json` |
| ~~Historical identity~~ | withdrawn | — | now TPS `eligibility.historical_releases[]` | `legacy-identity-statement.schema.json` (withdrawn; kept for history) |

**Not statements, but schema-bound records:**
- Trust Base Manifest, compiled into binaries (`trust-base-manifest.schema.json`);
- state pin (`trust-state-pin.schema.json`);
- trust-gate confirmation, in the VTS (`trust-gate-confirmation.schema.json`);
- lock 3.0.0 (`framework-lock-3.0.0.schema.json`);
- FORMAT (`trust-format.schema.json`).

## 5. Kernel tree canonical digest (`gov-tree-v2`)

Unchanged from revision 2 (§5.1–§5.5):
- regular files only;
- ASCII paths;
- no case collisions;
- `KERNEL_MANIFEST.json` excluded;
- raw-byte SHA-256;
- limits of 10 000 files, 64 MiB total, 16 MiB per file;
- tree digest byte-identical to 4.1.x `release_hash`.

## 6. Bundle layout

```text
agentic-engineering-os-<version>/
├── release-final.dsse.json             # authoritative (release-candidate.dsse.json for candidate bundles)
├── lineage/release-candidate.dsse.json
├── kernel/**
├── trust/root/<version>.dsse.json
├── trust/policy/<policy_version>.dsse.json
├── trust/state/<sequence>.dsse.json
├── trust/statements/<digest>.dsse.json  # attestations, certifications, revocations, build attestations referenced by the newest TSS
├── artifacts/artifact-final.dsse.json   # release-artifact statement; build attestations under trust/statements
├── manifest.json, manifest.yaml         # descriptive only
└── RELEASE_NOTES.md, ROLLBACK.md
```

## 7. Producer, signer and publisher interface

| Step | Command / actor | Output | Purpose key |
|---|---|---|---|
| 1 | `gov trust draft-policy` (whenever constitutional content, classification, floors or bootstrap change) | unsigned TPS draft with the Constitutional Surface; change list of classifications, registrations and computed reductions (`23` §6.2) | — |
| 2 | root ceremony | `trust-policy.dsse.json` | `trust-policy` (root threshold) |
| 3 | `gov release build --version V --trust-policy <TPS>` | payload; unsigned candidate statement naming the TPS. Refuses unless the surface checker exits 0 against that TPS, and refuses private key material. | — |
| 4 | external signer (reproduces step 3) | `release-candidate.dsse.json` | `release-candidate` |
| 5 | `gov release attach-signature` | verified placement | — |
| 6 | independent verifier | report, verdict, harness digests | — |
| 7 | external signer (verifier custody) | `verification-attestation.dsse.json` | `verification-attestation` |
| 8 | `gov release promote --attestation A` | unsigned final statement | — |
| 9 | external signer | `release-final.dsse.json` | `release-final` |
| 10 | reproducible binary build from the final tag | binaries with compiled TBM | — |
| 11 | independent rebuilder | `build-attestation.dsse.json` per binary | `build-attestation` |
| 12 | two release-artifact custodians (after checking step 11) | `artifact-final.dsse.json` | `release-artifact` ×2 |
| 13 | external signer (owner) | `certification-status.dsse.json` | `certification-status` |
| 14 | `gov trust publish --previous <TSS>` | unsigned TSS: admissible, full `prior_states[]`, references the certification, attestations and artefact statement | — |
| 15 | external signer | `trust-state.dsse.json`; the **state fingerprint published in the independent channels** (`06` §2) | `trust-state` |
| 16 | `gov release verify DIR` / `gov trust verify-artifact` | report mode | — |

A rejected candidate is never promoted. Its attestation, and any revocation, are published in the next TSS.
