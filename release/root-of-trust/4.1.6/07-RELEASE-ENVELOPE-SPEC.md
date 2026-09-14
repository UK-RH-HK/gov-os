# Output 7 — Envelope and statement specification

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 changes the statement set:
> - release statement v3 gains `release.source` (schema 3.0.0; CD3-3);
> - verification attestation v2 names the verified `source` and, for a lift, the negative it lifts (CR-01);
> - build attestation v2 names a `source` object;
> - freshness witness v1 is new (purpose `freshness-witness`, OP-7 (c) only);
> - Trust Policy v2 (schema 2.0.0) carries `floor_schema_version` 3, a surface with presence, exact precedence, Overlay
>   Surface and owner-domain slots, `eligibility.production_sources`, the bootstrap parameters and `clock_reset`;
> - Trust Base Manifest v2 names `binary.source`;
> - state pin v2 (`valid_until` mandatory), decision pin v1, and trust-gate confirmation v2 (`state_fingerprint`).
>
> Machine-readable schemas: `schemas/`. Instances: `examples/rev4/`, validated in `examples/rev4/validation.json`.
> Revision-2 and revision-3 examples are kept as history (`examples/README.md`).

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
| **`release.source {release_commit, source_tree_digest, build_inputs_digest}`** | ✓ | The reproducible source identity. `release_commit` equals `release.release_commit`. `source_tree_digest` is the SHA-256 of `git archive` of the commit. `build_inputs_digest` names the published build inputs (toolchain, lockfiles). A final's `source` equals its candidate's. | **V8** source equality; `25` A4b; custodial rules (`05` §7) |
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
| Trust root v2 | `trust-root.v2+json` | `root` | `version`, `lineage.trust_root_id`, `keys{}`, `purposes{}` for all **twelve** purposes (adds `freshness-witness`), `revoked_keys[]` | `trust-root.schema.json` (3.0.0) |
| **Trust Policy v2** | `trust-policy.v2+json` | `trust-policy` | `policy_version`, `supersedes_policy_digest`, `prior_policies[]`, `floor_schema_version` (**3**), `surface` (Constitutional Surface Inventory schema 2: presence, exact precedence, **`overlay_surface`**, **`owner_domain`**; `23`), `eligibility` (with `historical_releases[]` and **`production_sources[]`**), `install_authority`, `gating` (with `local_terminal_only[]`), `bootstrap` (**`op6_mode`, `op7_mode`, `pin_max_validity_days`, `c3_currency_window_hours`, `max_anchor_age_days`, `witness_max_validity_hours`, `freshness_witness_threshold`, `clock_reset`**), `sensitivity_order`, `lowering_history[]`, `unrevokes[]`, `state_chain_reset` | `trust-policy-statement.schema.json` (2.0.0), `constitutional-surface-inventory.schema.json` (2.0.0) |
| Trust State v2 | `trust-state.v2+json` | `trust-state` | `sequence`, `previous_state_digest`, `prior_states[]`, `references{root_version, root_digest, trust_policy{policy_version, statement_digest}}`, `revocations[]`, `certifications[]`, `attestations[]`, `artifacts[]`, `expires_at` (informational; **never a currency proof in revision 4**) | `trust-state-statement.schema.json` |
| **Verification attestation v2** | `verification-attestation.v2+json` | `verification-attestation` | as v1, plus **`source {release_commit, source_tree_digest, build_inputs_digest}`** and optional **`lifts_negative_statement_digest`** | `verification-attestation.schema.json` (2.0.0) |
| **Certification v3** | `certification-status.v2+json` | `certification-status` | as revision 2, plus optional `artifact_statement_digests[]` (informational in mode A) | `certification-statement.schema.json` |
| Revocation v2 | `revocation.v2+json` | `revocation` | as revision 2; `kind` includes `artifact` and `build-attestation` | `revocation-statement.schema.json` |
| **Artefact v3** | `artifact-final.v2+json` / `artifact-candidate.v2+json` | **`release-artifact`** / `release-candidate` | `stage`, `release_id`, `release_statement_digest`, `artifacts[]{name, target, digest, size, trust_profile, tbm_digest, tbm}`, `build{toolchain, build_inputs_digest, reproducible: true}` | `artifact-statement.schema.json`, `trust-base-manifest.schema.json` |
| **Build attestation v2** | `build-attestation.v2+json` | `build-attestation` | `artifact{name, target, digest, size}`, **`source {release_commit, source_tree_digest, build_inputs_digest}`**, `tbm_digest`, `reproduced` (const true), `rebuilder_label`, `method` | `build-attestation.schema.json` (2.0.0) |
| **Freshness witness v1** | `freshness-witness.v1+json` | `freshness-witness` | `witnessed_state{sequence, statement_digest}`, `issued_at`, `expires_at`, `witness_label` (`24` §3.3) | `freshness-witness.schema.json` |
| Retrieval profile | `retrieval-profile.v1+json` | `retrieval-profile` | `10` §3 | `profile-statement.schema.json` |
| ~~Historical identity~~ | withdrawn | — | now TPS `eligibility.historical_releases[]` | `legacy-identity-statement.schema.json` (withdrawn; kept for history) |

**Not statements, but schema-bound records:**
- Trust Base Manifest v2, compiled into binaries, with `binary.source` (`trust-base-manifest.schema.json`, 2.0.0);
- state pin v2, with mandatory `valid_until` (`trust-state-pin.schema.json`, 2.0.0);
- operator decision pin, with mandatory `expires_at` and `approved_under_state` (`trust-decision-pin.schema.json`);
- trust-gate confirmation v2, with `state_fingerprint` (`trust-gate-confirmation.schema.json`, 2.0.0);
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
| 1 | `gov trust draft-policy` | unsigned TPS draft: surface, precedence registration, Overlay Surface, bootstrap and, under OP-2 (S1), production sources; the change list, including computed reductions in both directions (`23` §6.2, `19` §10.6) | — |
| 2 | root ceremony | `trust-policy.dsse.json` | `trust-policy` (root threshold) |
| 3 | `gov release build --version V --trust-policy <TPS>` | payload; unsigned candidate statement naming the TPS, with `release.source` from the reproducible build inputs. Refuses unless the surface checker exits 0 against that TPS (presence, YAML profile, exact precedence, migration whitelist). Refuses private key material. | — |
| 4 | external signer (reproduces step 3 from `release.source`) | `release-candidate.dsse.json` | `release-candidate` |
| 5 | `gov release attach-signature` | verified placement | — |
| 6 | independent verifier (reproduces the candidate payload from `release.source`) | report, verdict, harness digests | — |
| 7 | external signer (verifier custody) | `verification-attestation.dsse.json` (v2), naming `source` | `verification-attestation` |
| 8 | `gov release promote --attestation A` | unsigned final statement; refuses unless the tree digest **and `release.source`** equal the attested candidate's | — |
| 9 | external signer (checks V8 source equality) | `release-final.dsse.json` | `release-final` |
| 10 | reproducible binary build from `release.source` | binaries with a compiled TBM v2 naming `binary.source` and a TSS that already exists | — |
| 11 | independent rebuilder: `verify-artifact --stage rebuilder`, then rebuild | `build-attestation.dsse.json` (v2) per binary | `build-attestation` |
| 12 | two release-artifact custodians: `verify-artifact --stage custodian` | `artifact-final.dsse.json` | `release-artifact` ×2 |
| 13 | external signer (owner) | `certification-status.dsse.json` | `certification-status` |
| 14 | `gov trust publish --previous <TSS> --stage publisher` | unsigned TSS: admissible; full `prior_states[]`; never drops a lower `artifacts[]` reference; references the certification, attestations and artefacts whose binaries pass A4a/A4b | — |
| 15 | external signer | `trust-state.dsse.json`; the **state fingerprint published in the independent channels** (`06` §2) | `trust-state` |
| 16 | OP-7 (c) only: scheduled witness service | `freshness-witness.dsse.json` naming the newest TSS, within `witness_max_validity_hours` | `freshness-witness` (≥ 2 keys for C3) |
| 17 | `gov release verify DIR` / `gov trust verify-artifact` | report mode | — |

A lift of a negative needs a new verification attestation naming the negative statement's digest in
`lifts_negative_statement_digest` (`17` MS-2).

A rejected candidate is never promoted. Its attestation, and any revocation, are published in the next TSS.
