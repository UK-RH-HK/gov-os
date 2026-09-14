# Output 7 — Envelope and statement specification

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 6 amendments: `release.source` is source identity v2 `{release_commit, git_tree, content_digest}` with
> `inputs_manifest_digest` (`30` §4.1; RV5-L4 aligned); verification attestation v4 (kernel tree digest), release registration
> v2 (environments), registration revocation v1, binary reproduction v2 (environment id), environment reproduction v1; the
> revision-4 artefact and build-attestation rows are marked withdrawn; first-contact and environment manifests are
> schema-bound documents; the producer interface gains environment reproduction and the first-hand ceremony.
> Revision 5 amendments: statement types per `05` §2 (new `release-registration.v1`, `binary-reproduction.v1`,
> `verification-attestation.v3`, `trust-state.v3`, `trust-root.v4`, `trust-policy.v3`; withdrawn `artifact-final.v2`,
> `build-attestation.v2`). Release statement v3 `release.source` is `{release_commit, content_digest}` with
> `inputs_manifest_digest` (`30` §4). Bundle layout adds `registrations/`, `reproductions/<release_id>/<target>/`,
> `manifests/`. Producer interface adds `gov trust draft-registration` (`30` R-REG-3) and `gov trust draft-policy
> --derivation` (`29` §5.3); publisher interface follows `30` R-PUB-1…4.
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
| **`release.source {release_commit, git_tree, content_digest}`** and **`inputs_manifest_digest`** (revision 6; revision 5 without `git_tree`) | ✓ | The reproducible source identity (`30` §4.1, source identity v2). `release_commit` equals `release.release_commit`. `content_digest` is computed from Git objects with length-prefixed records; `git_tree` is the commit's tree id. `inputs_manifest_digest` names the input manifest v2 (toolchain, lockfile, environments). A final's source, inputs and kernel tree equal its candidate's. | **V8**; `25` AP-5, AP-8; `05` §7 |
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
| **Verification attestation v4** (revision 6) | `verification-attestation.v4+json` | `verification-attestation` | `candidate_statement_digest`, `verdict`, `source {release_commit, git_tree, content_digest}`, `inputs_manifest_digest`, **`kernel_tree_digest`** (reproduced by the verifier), optional `lifts_negative_statement_digest` | `verification-attestation.schema.json` (4.0.0) |
| **Release registration v2** (revision 6) | `release-registration.v2+json` | `release-registration` | `30` §5 (with `environments[]` and the first-hand `constitution` block) | `release-registration.schema.json` (2.0.0) |
| **Registration revocation v1** (revision 6) | `registration-revocation.v1+json` | `release-registration` | `revokes[]` statement digests, `reason` (`30` R-REG-11) | `registration-revocation.schema.json` |
| **Binary reproduction v2** (revision 6) | `binary-reproduction.v2+json` | `reproducer` | `30` §7 (with `environment_id`) | `binary-reproduction.schema.json` (2.0.0) |
| **Environment reproduction v1** (revision 6) | `environment-reproduction.v1+json` | `reproducer` | `environment_id`, `environment_tree_digest`, `reproduced_at` (`33` R-BENV-2) | `environment-reproduction.schema.json` |
| **Certification v3** | `certification-status.v2+json` | `certification-status` | as revision 2, plus optional `artifact_statement_digests[]` (informational in mode A) | `certification-statement.schema.json` |
| Revocation v2 | `revocation.v2+json` | `revocation` | as revision 2; `kind` includes `artifact` and `build-attestation` | `revocation-statement.schema.json` |
| ~~Artefact v3~~ | withdrawn (revision 5; `release-artifact` never granted, KS-13) | — | — | `artifact-statement.schema.json` (history) |
| ~~Build attestation v2~~ | withdrawn (revision 5; replaced by the reproduction quorum, KS-13) | — | — | `build-attestation.schema.json` (history) |
| **Freshness witness v1** | `freshness-witness.v1+json` | `freshness-witness` | `witnessed_state{sequence, statement_digest}`, `issued_at`, `expires_at`, `witness_label` (`24` §3.3) | `freshness-witness.schema.json` |
| Retrieval profile | `retrieval-profile.v1+json` | `retrieval-profile` | `10` §3 | `profile-statement.schema.json` |
| ~~Historical identity~~ | withdrawn | — | now TPS `eligibility.historical_releases[]` | `legacy-identity-statement.schema.json` (withdrawn; kept for history) |

**Not statements, but schema-bound records:**
- Trust Base Manifest v2, compiled into binaries, with `binary.source` (`trust-base-manifest.schema.json`, 2.0.0);
- state pin v2, with mandatory `valid_until` (`trust-state-pin.schema.json`, 2.0.0);
- operator decision pin, with mandatory `expires_at` and `approved_under_state` (`trust-decision-pin.schema.json`);
- trust-gate confirmation v2, with `state_fingerprint` (`trust-gate-confirmation.schema.json`, 2.0.0);
- lock 3.0.0 (`framework-lock-3.0.0.schema.json`);
- (revision 6) first-contact manifest (`first-contact-manifest.schema.json`, `32` §3), environment manifest
  (`environment-manifest.schema.json`, `33` §3), input manifest v2 (`input-manifest.schema.json` 2.0.0), admission record v2
  (`admission-record.schema.json` 2.0.0);
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
├── trust/registrations/<release_id>.dsse.json            # release registration (revision 5)
├── trust/reproductions/<release_id>/<target>/<key id>.dsse.json
├── trust/environments/<environment_id>/<key id>.dsse.json # environment reproductions (revision 6)
├── trust/manifests/<digest>.json          # input manifests v2, environment manifests (revision 6)
├── trust/first-contact/<sequence>.json    # first-contact manifest of each Trust State (revision 6; the code is in the channels)
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
| 10 | (revision 6) environment reproducers assemble each registered environment from pinned components | `environment-reproduction.dsse.json` per reproducer (`33`) | `reproducer` |
| 11 | (revision 6) registration ceremony: each custodian checks R-REG-3 (a)–(g), including `csi_check.py verify-registration` on its own kernel build | `release-registration.dsse.json` (v2) | `release-registration` |
| 12 | (revision 5–6) at least q reproducers build from the registered source in re-assembled registered environments and confirm first-hand to the publisher | `binary-reproduction.dsse.json` (v2) per reproducer | `reproducer` |
| 13 | external signer (owner) | `certification-status.dsse.json` | `certification-status` |
| 14 | `gov trust publish --previous <TSS> --stage publisher` | unsigned TSS: admissible; full `prior_states[]`; never drops a lower `artifacts[]` reference; references the certification, attestations and artefacts whose binaries pass A4a/A4b | — |
| 15 | external signer | `trust-state.dsse.json`; the **first-contact manifest and code** of the new state (`32` §3) and the state fingerprint published in the independent channels (`06` §2) | `trust-state` |
| 16 | OP-7 (c) only: scheduled witness service | `freshness-witness.dsse.json` naming the newest TSS, within `witness_max_validity_hours` | `freshness-witness` (≥ 2 keys for C3) |
| 17 | `gov release verify DIR` / `gov trust verify-artifact` | report mode | — |

A lift of a negative needs a new verification attestation naming the negative statement's digest in
`lifts_negative_statement_digest` (`17` MS-2).

A rejected candidate is never promoted. Its attestation, and any revocation, are published in the next TSS.
