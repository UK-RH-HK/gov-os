# Output 4 — Canonical release-authentication architecture (RoT-1)

## 1. Alternatives evaluated

| Option | Description | Non-circular | Offline | Extensible after ship (new releases, certification, revocation) | Provider-neutral | Rotation / recovery | Verdict |
|---|---|---|---|---|---|---|---|
| O1 | Harden hashes only (4.1.5 report §12: verify source against shipped manifest; declared vs recomputed hash) | **No** (E1) | yes | yes | yes | n/a | Rejected — circular |
| O2 | Binary-embedded release registry (digest allowlist compiled into `gov`) | yes | yes | **No** — every new release, certification or revocation needs a new binary, and the binary's own distribution still needs authentication | yes | via new binary only | Kept as a **component**: compiled-in trust root, revocation floor, embedded statement, legacy-identity statement |
| **O3** | **Signed statements; trust-root keys compiled into the binary (RoT-1)** | yes | yes | yes | yes (Ed25519, DSSE, RFC 8785 are open standards) | root-signed rotation, revocation, re-attestation | **Recommended** |
| O4 | Keyless signing with an identity provider + public transparency log | yes | partially (log inclusion/revocation checks typically online) | yes | **No** — binds trust to an OIDC identity provider, often the same hosting provider that must not be the root | provider-managed | Rejected as root; optional future *additional* attestation |
| O5 | Signed Git tags/commits (SSH or OpenPGP) | partially | yes | yes | yes | tied to developer identities | Rejected as root — authenticates commits, not payload bytes delivered through bundles, caches, snapshots or consumer repositories; requires Git history on every consumer. Optional supplementary provenance |
| O6 | Full TUF deployment (root, targets, snapshot, timestamp roles) | yes | **No** for freshness (timestamp role must be online) | yes | yes | strongest | Not adopted wholesale; RoT-1 adopts TUF's root-rotation rule, thresholds, role separation and monotonic counters, and documents the freshness residual |

## 2. Components

| Component | Proposed location (4.1.6) | Responsibility |
|---|---|---|
| Trust context (T0) | `runtime/src/trust/root.rs`; data in canonical repo `trust/production/` (public), compiled via `include_bytes!` | parse and chain-verify trust-root metadata; key/role lookup; compiled revocation floor; trust profile (`production`/`test`) |
| Canonical JSON | `trust/jcs.rs` | RFC 8785 serialisation under the GOV-JCS-1 profile; canonical-bytes check |
| DSSE | `trust/dsse.rs` | strict envelope parse; PAE; signature verification (Ed25519 strict) |
| Statements | `trust/statement.rs` | typed release, certification, revocation, artifact, profile, legacy-identity statements; validation against **compiled-in** schemas |
| Quarantine | `trust/quarantine.rs` | source adapters (release dir, bundle archive, canonical checkout, embedded, snapshot, downloaded file) → single read into a private 0700 directory or memory; tree rules |
| Authentication boundary | `trust/authenticate.rs` | the only constructor of `AuthenticatedRelease` |
| Authorisation layer | `trust/authorise.rs` | certification policy, gates bound to statement digest, authority, minimum trust level, downgrade rules |
| Install transaction | `trust/install_tx.rs` | journaled stage/swap/migrate/commit; interrupted-install recovery |
| Use-time trust | `kernel_trust.rs` v2 + `trust/kernel_fs.rs` | `TrustedKernel` read handle over installed dir or embedded in-memory map |
| Producer tools | `release.rs` (`gov release build`, `attach-signature`, `verify`), external signer | unsigned statement generation, signature attachment with verification, report-only authentication |

Dependency: one pure-Rust Ed25519 implementation with strict verification (implementation choice recorded in ARCH-0002,
replaceable; D-0002 single self-contained binary preserved; `sha2` already present).

## 3. Normative authentication algorithm

`authenticate(source: SourceRef, ctx: &TrustContext, req: &AdoptionRequest) -> Result<AuthenticatedRelease, TrustError>`

Every failure returns `ok: false`, the error code below, and `details.stage` set to the step ID. No byte is written to
any trust location before V14 completes.

| Step | Action | Failure code |
|---|---|---|
| V0 | Resolve the source to a `SourceRef` {kind, logical reference}. Environment variables may only select the source. | `KERNEL_SOURCE_NOT_FOUND` |
| V1 | Materialise into quarantine by **reading each file exactly once**. Tree rules (`07-RELEASE-ENVELOPE-SPEC.md` §5): regular files only; no symlink, device, FIFO; relative POSIX paths, NFC, no `.`/`..`/empty segments, no case-fold collisions; size/count limits; archives extracted with the same rules. The kernel tree is staged with the same `payload_dirs` rules as the producer, entirely inside the source root (no parent-directory fallback). | `RELEASE_TREE_INVALID` |
| V2 | Locate the release statement (`release.dsse.json` at bundle root; `release/releases/<version>/release.dsse.json` for a canonical checkout; embedded statement for the embedded payload). **Absent** → production profile: `UNSIGNED_SOURCE_REFUSED` unless the explicit development path applies (§7). **Present but failing any later step → never falls back to the development path.** | `RELEASE_STATEMENT_MISSING` / `UNSIGNED_SOURCE_REFUSED` |
| V3 | Parse DSSE strictly: exactly `payloadType`, `payload`, `signatures`; no duplicate keys; payloadType in the allowlist for the requested statement kind; base64 strict; payload ≤ 4 MiB; payload bytes must equal `JCS(parse(payload))`. | `RELEASE_STATEMENT_MALFORMED` |
| V4 | Build the trust context: compiled-in root chain; accept a newer root version only if chain-verified (§5 of key management) and ≥ the compiled-in and locally recorded high-water mark; accept a newer revocation statement only if verified and its sequence ≥ floor. | `TRUST_ROOT_INVALID` / `TRUST_ROOT_ROLLBACK` / `TRUST_ROOT_THRESHOLD_NOT_MET` / `REVOCATION_LIST_ROLLBACK` |
| V5 | Signatures: for each entry, look up `keyid` in the effective root; the key's role set must include the role bound to the payloadType; algorithm is taken **from the root key record** (an envelope cannot select it); verify strictly over `PAE(payloadType, payload)`; count distinct valid keys; require ≥ role threshold. A production binary refuses any key, root or statement whose trust profile is `test`. | `RELEASE_SIGNER_UNKNOWN` / `RELEASE_SIGNER_NOT_AUTHORISED` / `RELEASE_SIGNATURE_INVALID` / `RELEASE_ALGORITHM_MISMATCH` / `RELEASE_THRESHOLD_NOT_MET` / `TRUST_PROFILE_MISMATCH` |
| V6 | Revocation: any counted signer key revoked → reduce count (may fail threshold); release_id or statement digest revoked with `refuse_install` → fail. | `RELEASE_SIGNER_REVOKED` / `RELEASE_REVOKED` |
| V7 | Validate the statement payload against the **compiled-in** statement schema (never a schema from the material under authentication). `statement.signing.role` and `statement.signing.algorithm` must match V5. | `RELEASE_STATEMENT_MALFORMED` |
| V8 | Identity: `framework` equals the compiled framework name; `release.version` equals quarantine `KERNEL.yaml` `version`; `release.release_id` equals `<framework>@<version>#<tree_digest[0:16]>` recomputed; if the request names a version or statement digest, they must match; for reinstall, statement digest must equal the installed statement digest. | `RELEASE_IDENTITY_MISMATCH` / `RELEASE_REPLAY_DETECTED` |
| V9 | Content: recompute the file map over the quarantine tree; compare with `kernel.files` (report `modified`, `missing`, `added`); recompute `kernel.tree_digest`, `kernel.manifest_digest` and every `components.*` digest from the recomputed map and compare. A source `KERNEL_MANIFEST.json` is excluded and ignored. | `RELEASE_DIGEST_MISMATCH` |
| V10 | Migrations: every `migrations/*.yaml` in the tree appears in `migrations[]` with identical `path`, `digest`; each file's `id`, `from_version`, `to_version` equals its entry; no migration outside the tree is ever loaded. | `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` |
| V11 | Compatibility: running CLI version inside `compatibility.cli`; `kernel_contract_version` supported by this binary; for update, the installed version is in `compatibility.supported_from_versions` and a complete migration path exists **using statement data only**. | `RELEASE_INCOMPATIBLE` |
| V12 | Downgrade and replay, against the **installed authenticated identity** (installed statement, never the lock): lower version, or same version with a different statement digest, or lower `release.sequence` → refuse, except a governed rollback to the ledger-recorded previous identity (`09` R-RB). | `RELEASE_DOWNGRADE_REFUSED` / `RELEASE_REPLAY_DETECTED` |
| V13 | Certification: collect certification statements for this statement digest (bundle `certification/`, embedded, `governance/trust/`); verify each under the certification role; highest `sequence` wins; mismatching digest → ignore with warning, forged → error. | `CERTIFICATION_STATEMENT_INVALID` / `CERTIFICATION_MISMATCH` |
| V14 | Produce `AuthenticatedRelease` { statement, statement_bytes, statement_digest, signer key ids, trust_root_id + version, revocation sequence, certification, trust_level, recomputed digests, quarantine handle }. | — |

After V14, **authorisation** (§8) and the **install transaction** (`09-INTEGRATION-REQUIREMENTS.md` §3) run. The
transaction re-digests the staged copy before the swap (`SOURCE_CHANGED_DURING_INSTALL` if the quarantine was altered) and
performs a full kernel_trust v2 check after commit; failure triggers automatic journal rollback.

## 4. Making "manufacturing trust from source contents" unrepresentable

1. `AuthenticatedRelease` has private fields, no `Deserialize`, no public constructor, and is not persisted; it is created
   only by `authenticate`.
2. Install API: `install_tx::install(&AuthenticatedRelease, &GovernanceDir, &Authorisation)`; restore API:
   `install_tx::restore(&AuthenticatedSnapshot, …)` where `AuthenticatedSnapshot` is produced by `authenticate` over a
   snapshot source. There is no `install_kernel(Option<&Path>, …)`.
3. `write_lock` takes `&InstalledRelease` returned by the transaction.
4. `load_migrations` takes `&AuthenticatedRelease` or `&TrustedKernel`.
5. `kernel::build_manifest` and `kernel::stage_payload` are private to `release::build` (producer) and
   `trust::quarantine`.
6. The `release_ingress` conformance family asserts 1–5 by source inspection (the style already used in
   `tests/certification/arch.rs`) and by black-box refusal tests over every ingress command.
7. A test filesystem hook asserts that no write under `governance/` occurs before V14 for every failure injection.

## 5. Use-time installed-kernel verification (kernel_trust v2)

Inputs: installed files, `governance/trust/release.dsse.json`, `governance/trust/certification.dsse.json` (optional),
compiled T0, recorded revocation high-water mark. `framework.lock` is read only for cross-checking and display.

| Check | Detects |
|---|---|
| statement verifies under T0 (V3–V7), not revoked | Git-delivered or manual replacement of kernel + statement + lock (E4); revoked releases |
| installed file map ≡ statement `kernel.files` | post-install tampering (V-H2 preserved) |
| `KERNEL_MANIFEST.json` ≡ deterministic derivation from the statement | manifest drift |
| lock identity fields ≡ statement | edited lock (`LOCK_IDENTITY_MISMATCH`) |
| no incomplete install journal | interrupted install (`INSTALL_INTERRUPTED`) |

Verdict fields (superset of 4.1.5 output; `verified` keeps its consumer meaning — *floors may be read from the installed
kernel*):

| Field | Meaning |
|---|---|
| `installed` | a kernel and lock are present |
| `integrity_verified` | installed files ≡ statement map (or the development record map) |
| `authenticated` | statement verified under T0 and not revoked |
| `trust_level` | `CERTIFIED` \| `AUTHENTICATED_UNCERTIFIED` \| `AUTHENTICATED_REJECTED` \| `REVOKED` \| `DEVELOPMENT_UNSIGNED` \| `TEST` \| `UNAUTHENTICATED` \| `TAMPERED` |
| `identity_source` | `statement` \| `legacy-identity` \| `development-record` |
| `verified` | production profile: `integrity_verified ∧ authenticated ∧ trust_level ≠ REVOKED`; test profile additionally admits `DEVELOPMENT_UNSIGNED` and `TEST` |
| `release_id`, `statement_digest`, `signer_key_ids`, `trust_root_id`, `certification`, `lock_consistent`, `substituted_embedded_baseline`, `problems`, `codes[]`, `fingerprint` | diagnostics |

Enforcement is unchanged in shape: when `verified` is false, constitutional content is read from the authenticated
embedded baseline and mutating operations fail closed (`KERNEL_TAMPERED` for integrity failures,
`KERNEL_UNAUTHENTICATED` for identity failures, `RELEASE_REVOKED` for `refuse_operation` revocations). Exempt remedies
gain `update --apply` **only when its target authenticates** (replacing an untrusted kernel with an authenticated one is
strictly trust-increasing; its gates are evaluated with floors from the embedded baseline).

No cross-process verdict cache: a cache under `.governance-runtime/` is writable by A3 and cannot be authenticated
without a secret. Expected cost per process is one Ed25519 verification plus hashing ~120 files (already done today).

## 6. Embedded baseline

- `runtime/build.rs` embeds kernel bytes, the matching `release/releases/<version>/release.dsse.json` if present, the
  certification statement if present, and the legacy-identity statement. `build.rs` makes no trust decision.
- At first use in a process the embedded statement is authenticated against T0 and the embedded bytes are digested **in
  memory**. The result is the embedded trust level (`gov version --trust` reports it).
- Policy reads for the fail-closed baseline go through `KernelFs::Embedded` (in-memory map). Where a real directory is
  required (e.g. to install from the embedded payload), materialisation writes to a fresh private directory and the
  quarantine step re-digests it. A `.complete` marker is never evidence (`EMBEDDED_BASELINE_CORRUPT`).
- A binary built from a tree with no matching signed statement has embedded trust level `DEVELOPMENT_UNSIGNED`; a
  production-profile development binary therefore cannot install its embedded kernel as authenticated.

## 7. Development and test paths

| Binary profile | Source | Acceptance | Floors read from | Recorded trust level |
|---|---|---|---|---|
| production | signed statement under production root | normal | installed kernel | `CERTIFIED` / `AUTHENTICATED_*` |
| production | no statement present | refused `UNSIGNED_SOURCE_REFUSED`; with `--allow-unsigned-development` installs, writes `governance/trust/development.json` (unsigned record of file map, actor, time) | **authenticated embedded baseline**; mutations need the existing fingerprint-bound L4+ override gate | `DEVELOPMENT_UNSIGNED` |
| production | statement or root with trust profile `test` | refused | — | — |
| test (`--features trust-profile-test`) | test-signed statement | normal | installed kernel | `TEST` |
| test | no statement present | accepted without flag, labelled | installed kernel | `DEVELOPMENT_UNSIGNED` |

A present-but-invalid statement is refused in every profile. No path writes `CERTIFIED` or `AUTHENTICATED_*` for
unsigned or test material, and production binaries refuse locks and `governance/trust/` records whose profile is `test`.

## 8. Authorisation layer (after authentication)

| Decision | Input (all from authenticated objects or T2 records) |
|---|---|
| Is a human gate required for update? | certification ≠ `CERTIFIED` (OP-3), or statement `update_impact.breaking_changes` / `human_gates` non-empty, or trust-level decrease |
| Which gate authorises it? | a presented, answered-A `framework_update` gate whose `release_statement_digest` equals this statement digest (a gate for one digest never approves another, closing a same-version substitution) |
| May `init` proceed on an uncertified or rejected release? | OP-3 policy (default allowed, labelled; overlay may require `CERTIFIED`) |
| Minimum trust level for the project | kernel floor `SECURITY_POLICY.release_trust.minimum_trust_level: AUTHENTICATED_UNCERTIFIED` (production); overlay may raise to `CERTIFIED`, never lower (POLICY_PRECEDENCE) |
| Who may install/update/reinstall/rollback | `AUTHORITY_POLICY` levels read from the authenticated kernel (for first install: from the authenticated target) |
| Revoked | refused regardless of gates |
