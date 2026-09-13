# Output 5 — Key-management model

## 1. Roles

| Role | Signs (payloadType) | Keys / threshold (OP-1, OP-2 defaults) | Custody | May never |
|---|---|---|---|---|
| `root` | trust-root metadata; emergency key revocation (via new root version) | 3 keys, threshold 2 | three named human custodians; offline hardware-backed keys or an air-gapped machine with encrypted storage; geographically separated | sign releases, certifications or profiles |
| `release` | release statements; artifact statements (binary digests) | 1 active + 1 standby, threshold 1 | hardware token used only on an isolated signing host | sign certification statements |
| `certification` | certification statements; release revocation statements; legacy-identity statement | 1 active + 1 standby, threshold 1 | release owner / product owner — a person different from the release builder | sign release statements |
| `profile` | reference retrieval profile statements | 1, threshold 1 | release owner | sign release or certification statements |
| `test` | test-profile statements (only in test-profile binaries) | generated keys committed under `tests/fixtures/trust/test-keys/` (deliberately public) | none — treated as compromised by publication | be accepted by a production-profile binary |

Role key sets are **disjoint** (a key id may appear in exactly one role); the trust-root verifier refuses metadata that
violates this (`TRUST_ROOT_INVALID`). The payloadType → role binding is fixed in the binary:

| payloadType | Role |
|---|---|
| `application/vnd.agentic-engineering-os.trust-root.v1+json` | root |
| `application/vnd.agentic-engineering-os.release-statement.v1+json` | release |
| `application/vnd.agentic-engineering-os.artifact-statement.v1+json` | release |
| `application/vnd.agentic-engineering-os.certification-statement.v1+json` | certification |
| `application/vnd.agentic-engineering-os.revocation-statement.v1+json` | certification (releases only); key revocation is only by a new trust-root version |
| `application/vnd.agentic-engineering-os.legacy-identity.v1+json` | certification |
| `application/vnd.agentic-engineering-os.profile-statement.v1+json` | profile |

## 2. Representation

- **Key id**: `<alg>:<lowercase hex SHA-256 of the raw public key bytes>`, e.g. `ed25519:9c1f…` (64 hex). The algorithm
  prefix must equal the key record's `alg`.
- **Trust-root metadata** (`schemas/trust-root.schema.json`): `trust_profile` (`production`|`test`), `framework`,
  `version` (integer, monotonic), `keys` (key id → `{alg, public_key (base64 of raw 32 bytes), label, added_in_version}`),
  `roles` (role → `{key_ids, threshold}`), `revocation_floor_sequence`, `issued_at`. Signed as a DSSE envelope by the
  root role.
- **Trust-root id**: `sha256:` + SHA-256 of the canonical payload bytes of the **first** (version 1) root of the profile;
  it names the trust lineage and is the fingerprint compared at bootstrap. `root_version` identifies the current link.
- **Canonical repository layout** (public data only):
  `trust/production/root/1.json … N.json` (DSSE), `trust/production/revocations.dsse.json`,
  `trust/production/legacy-identity.dsse.json`; test: `tests/fixtures/trust/test-root/…`, `tests/fixtures/trust/test-keys/`.
  The binary compiles in the full chain. Trust anchors are **never** part of the kernel payload (a kernel cannot carry the
  root that authenticates it).

## 3. Signing-key separation and ceremony rules

1. Private keys never exist in: the canonical repository or its history, any consumer repository, release bundles,
   CI logs, CI secrets of the building pipeline, developer machines holding a canonical clone, or `.governance-runtime/`.
2. **Sign what you reproduced.** The release signer, on the isolated signing host, rebuilds the candidate from the tagged
   `release_commit` (`gov release build` from `git archive`), compares the resulting *unsigned statement payload* byte for
   byte with the candidate's, and signs only if identical. The signer never signs a payload produced elsewhere without
   reproducing it.
3. **Two-person rule.** The certification key holder is not the builder of the release; certification is signed only
   after an independent verifier's verdict and references the verifier report digest.
4. **Producer hygiene.** `gov release build` refuses (`PRIVATE_KEY_MATERIAL_DETECTED`) when the tree contains private
   key material outside `tests/fixtures/trust/test-keys/`: PEM `PRIVATE KEY` blocks, `openssh-key-v1`, JWK `"d"` members,
   files named `*.key`, `*.sec`, `*.ed25519` outside the allowlist, or 32/64-byte raw seeds in `trust/`. The same scan runs
   as a conformance test over the repository and every payload.
5. **Ceremony record.** Each key ceremony produces a governed record (public keys, key ids, trust-root id, custodians,
   date, root version) under `spec/decisions/` or `spec/reports/`; secret material is never recorded.

## 4. Multiple keys and thresholds

- Release and certification roles default to threshold 1 with a registered standby key, so loss of the active token does
  not require a root ceremony to resume signing.
- The root role requires 2 of 3; any root version change needs threshold signatures of **both** the previous and the new
  root key sets (TUF rule), preventing a single new or stolen key from re-rooting trust.
- Future algorithm migration (e.g. adding a post-quantum scheme) is expressed as additional keys with a role policy
  requiring signatures from keys of each listed algorithm; no format change.

## 5. Rotation

| Event | Procedure | Consumer effect |
|---|---|---|
| Routine release/certification/profile key rotation | root signs version N+1 adding the new key (and optionally removing the old after overlap) | new binaries compile N+1; older binaries accept N+1 when it arrives in a bundle or via `gov trust refresh --from <file>` (chain-verified); existing statements stay valid while their signer is not revoked |
| Root key rotation | N+1 signed by ≥2 of old root keys and ≥2 of new | same |
| High-water mark | verifier records the highest accepted root version and revocation sequence in the user trust store (`$XDG_CONFIG_HOME/gov/trust-state.json`) and in `framework.lock` | lower versions refused (`TRUST_ROOT_ROLLBACK`); the compiled-in floor is the hard minimum because both stores are writable |

## 6. Revocation and re-attestation

- **Release revocation** (`schemas/revocation-statement.schema.json`, certification role): entries by `release_id` and
  `statement_digest` with `effect: refuse_install | refuse_operation` and a reason; monotonic `sequence`.
- **Key revocation**: by removing the key in a new root version and listing it under `revoked_keys` there; statements
  whose only valid signatures come from revoked keys fail V5/V6.
- **Re-attestation**: because the statement digest is the SHA-256 of the payload bytes and signatures sit outside the
  payload, a genuine statement can be re-signed by a new key without changing its digest, its `release_id`, any
  certification referencing it, or any consumer lock. Consumers adopt the re-signed envelope with
  `gov kernel reinstall` (identity unchanged) or it arrives with the next update.
- **Distribution**: every new binary compiles the newest revocation statement as its floor; every release bundle
  carries the newest; `gov trust refresh --from <file|url>` accepts a newer one through any transport.

## 7. Compromise and loss playbooks

| Scenario | Actions | Residual |
|---|---|---|
| Release key stolen | (1) root version N+1 removes and revokes the key, adds the standby as active; (2) re-sign every genuine statement signed by the stolen key; (3) revocation statement lists any known malicious statement digests; (4) ship patch binary with N+1 and revocations; (5) consumers: doctor reports `RELEASE_SIGNER_REVOKED`, remedy `gov trust refresh` + `gov kernel reinstall` | offline consumers that never receive N+1 still accept the stolen key (freeze residual) |
| Certification key stolen | same, certification role; forged `CERTIFIED` statements become invalid once the key is revoked; affected releases fall back to `AUTHENTICATED_UNCERTIFIED` (gates return) | as above |
| Profile key stolen | same, profile role; profile plugins re-verified at next rebuild/plugin start | as above |
| One root key stolen or lost (below threshold) | remaining two custodians sign N+1 replacing it | none |
| Threshold root keys stolen | **re-bootstrap**: new root lineage (new trust-root id), new binary, fingerprint republished through independent channels, every consumer re-confirms the fingerprint; the new binary distrusts the old lineage entirely | full reconfirmation cost |
| Threshold root keys lost (no compromise) | same as above; old statements can be re-signed under the new lineage because their payload digests are unchanged | reconfirmation cost |
| Standby release key lost | root rotates in a new standby | none |

## 8. Test keys versus production keys

1. The test trust root and test keys compile only with cargo feature `trust-profile-test`; release builds assert the
   feature is off, and `gov version --trust` prints `trust_profile`.
2. Every statement, trust-root file, lock and `governance/trust/` record carries `trust_profile`; production binaries
   refuse `test` in all of them (`TRUST_PROFILE_MISMATCH`).
3. Test key ids are additionally compiled into production binaries as a deny-list.
4. Test private keys are committed on purpose so that fixtures are reproducible; the producer scan allowlists only that
   directory, and RT-14/RT-24 prove they never validate in production.

## 9. Algorithms

- Signatures: **Ed25519** (RFC 8032, pure, not Ed25519ph), verified with strict rules (reject non-canonical `S`,
  small-order `A`/`R`), 128-bit classical security, deterministic, small keys and signatures, available in pure Rust and in
  standard independent tooling (OpenSSL 3, OpenSSH, common language libraries) for cross-verification and bootstrap.
- Digests: SHA-256 (already the kernel digest function).
- Constitutional wording (not vendor-bound): "an approved signature scheme recorded in the trust root, with at least
  128-bit classical security, verified with strict encoding rules". Ed25519 is the only approved scheme at 4.1.6.
