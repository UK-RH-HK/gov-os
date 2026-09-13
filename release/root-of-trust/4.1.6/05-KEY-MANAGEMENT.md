# Output 5 — Key-purpose and key-management model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Replaces the rev 1 role model. Addresses RV-H4 (CD-3), the key-custody parts of RV-M5 (CD-9) and RV-L1/RV-L2.

## 1. Purposes

A **purpose** is the authority a key exercises when it signs. Every statement type maps to exactly one purpose, fixed
in the binary. Root metadata grants purposes to keys.

| Purpose | Signs (payloadType suffix) | May assert | May never assert | Default keys / threshold | Default custody (`21` OP-1, OP-2) | Impact if this key alone is stolen |
|---|---|---|---|---|---|---|
| `root` | `trust-root.v2` | key set, purpose grants, thresholds, key revocation | anything about releases, certification or state | 3 keys, threshold 2 | offline hardware-backed, independent custodians | none below threshold |
| `trust-policy` | `trust-policy.v1` | security floors, eligibility policy, install-authority floor, gating mode (OP-3), explicit lowering, unrevocation | release authenticity, certification | root keys, root threshold (mandatory, KS-2) | as root | as root |
| `release-final` | `release-final.v1`, `artifact-final.v1`, `historical-identity.v1` (compiled source only) | authenticity of final release content, binaries and historical identities | certification, verification result, eligibility, trust state | 1 active + 1 standby, threshold 1 (OP-2 may choose 2) | hardware token on an isolated signing host; standby held with **equal** custody | authentic finals can be forged. Eligibility floors, the install gate (OP-3 mode A) and certification (two other keys plus the trust-state reference) still apply. |
| `release-candidate` | `release-candidate.v1`, `artifact-candidate.v1` | authenticity of candidate content | final stage, certification | 1, threshold 1 (OP-4) | signing-host key | candidates only; never production-eligible |
| `verification-attestation` | `verification-attestation.v1` | the independent verifier's verdict for one candidate statement digest | certification, authenticity | 1, threshold 1 | verification operator | a verdict alone certifies nothing |
| `certification-status` | `certification-status.v1` | CERTIFIED / REJECTED / WITHDRAWN for one final statement digest | authenticity; CERTIFIED without an ACCEPTED attestation | 1 + standby, threshold 1 | owner hardware token, separate from `release-final` | CERTIFIED also needs an attestation and a trust-state reference to be visible |
| `revocation` | `revocation.v2` | `refuse_install` / `refuse_operation` for named digests | new trust; unrevocation | 1, threshold 1 | owner | denial of service only |
| `trust-state` | `trust-state.v1` | which signed statements form the published state at a sequence; optional expiry | any fact that is not itself separately signed | 1, threshold 1 | owner, offline | withholding (freeze) only; regressions rejected (`17` S4) |
| `retrieval-profile` | `retrieval-profile.v1` | provenance and integrity of a reference retrieval profile | authorisation; release authenticity | 1, threshold 1 | release owner | profile integrity only |

The **test** lineage is a trust *profile*, not a purpose. Its committed public test keys are valid only in the separate
test-profile binary (§10).

## 2. Compiled statement-type table (T0)

| payloadType (`application/vnd.agentic-engineering-os.` …) | `_type` (`https://agentic-engineering-os/statement/` …) | Purpose | Accepted from |
|---|---|---|---|
| `trust-root.v2+json` | `trust-root/v2` | `root` | compiled; bundle, PTR, VTS, refresh (chain-verified) |
| `trust-policy.v1+json` | `trust-policy/v1` | `trust-policy` | any source |
| `trust-state.v1+json` | `trust-state/v1` | `trust-state` | any source |
| `release-final.v1+json` | `release/v2`, `release.stage = final` | `release-final` | any source |
| `release-candidate.v1+json` | `release/v2`, `release.stage = candidate` | `release-candidate` | any source |
| `artifact-final.v1+json` | `artifact/v2`, `stage = final` | `release-final` | any source |
| `artifact-candidate.v1+json` | `artifact/v2`, `stage = candidate` | `release-candidate` | any source |
| `verification-attestation.v1+json` | `verification-attestation/v1` | `verification-attestation` | any source |
| `certification-status.v1+json` | `certification/v2` | `certification-status` | any source |
| `revocation.v2+json` | `revocation/v2` | `revocation` | any source |
| `historical-identity.v1+json` | `historical-identity/v1` | `release-final` | **compiled copy only**; any other source → `STATEMENT_SOURCE_NOT_PERMITTED` |
| `retrieval-profile.v1+json` | `retrieval-profile/v1` | `retrieval-profile` | any source |

No revision-2 binary accepts the revision-1 payloadTypes. None was ever issued.

## 3. Grants and separation constraints

Root metadata (`schemas/trust-root.schema.json`) lists, per purpose, `key_ids`, `threshold` and optionally
`require_algorithms`. A key id listed under several purposes is an explicit **grant**. The binary checks every root
version against compiled constraints; a violation invalidates that root version (`PURPOSE_SEPARATION_VIOLATION`).

| ID | Mandatory constraint (production profile) | Reason |
|---|---|---|
| KS-1 | `root` keys may additionally hold only `trust-policy` | root keys stay offline and single-purpose |
| KS-2 | `trust-policy` key ids ⊆ `root` key ids, and `trust-policy.threshold` ≥ `root.threshold` | floors are constitutional |
| KS-3 | `release-final` ∩ `certification-status` = ∅ | authenticity is not certification |
| KS-4 | `release-final` ∩ `verification-attestation` = ∅ | release signer is not verifier |
| KS-5 | `certification-status` ∩ `verification-attestation` = ∅ | certifier is not verifier |
| KS-6 | `release-candidate` ∩ (`certification-status` ∪ `verification-attestation`) = ∅ | same |
| KS-7 | every threshold is ≥ 1 and ≤ the purpose's key count; no key in `revoked_keys` is granted any purpose; no public key appears under two key ids | well-formedness |

**Permitted only by explicit grant** (owner choice, `21`):
- `release-candidate` with `release-final` (OP-4 “no separate candidate key”);
- `revocation` with `certification-status`;
- `trust-state` with `revocation`;
- `retrieval-profile` with `release-final`.

Key separation is not people separation. One owner may hold several purposes on distinct tokens. The constraints
guarantee that a single stolen key never spans authenticity and certification; they do not guarantee that different
humans act.

## 4. Signature verification rules (normative; every statement; every source)

| ID | Rule | Failure code |
|---|---|---|
| SV-1 | Strict envelope: exactly `payloadType`, `payload`, `signatures`; no duplicate members; strict padded base64; decoded payload ≤ 4 MiB; ≥ 1 signature | `STATEMENT_MALFORMED` |
| SV-2 | payloadType is in the compiled table and permitted for the source context (historical identity: compiled copy only) | `STATEMENT_TYPE_UNKNOWN` / `STATEMENT_SOURCE_NOT_PERMITTED` |
| SV-3 | Payload bytes equal their GOV-JCS-1 re-serialisation | `STATEMENT_MALFORMED` |
| SV-4 | The effective root chain is built (`17` S2). Every key id in each root version is recomputed from `public_key` and must match; duplicate public keys are refused; KS-1…KS-7 hold | `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` |
| SV-5 | Purpose = the compiled mapping of the payloadType (never a field chosen by the envelope or payload) | — |
| SV-6 | For each signature: key id present in the effective root, granted the purpose, not revoked. The algorithm is taken from the key record. Ed25519 is verified strictly over `PAE(payloadType, payload)`. | `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` |
| SV-7 | Distinct keys with valid signatures ≥ purpose threshold; if `require_algorithms` is present, at least one valid signature per listed algorithm | `THRESHOLD_NOT_MET` |
| SV-8 | Payload validates against the compiled schema for the payloadType | `STATEMENT_MALFORMED` |
| SV-9 | Payload `_type` equals the mapping; `signing.purpose` (where present) equals the purpose; `stage` is consistent with the payloadType | `STATEMENT_TYPE_MISMATCH` |
| SV-10 | Payload `trust_profile` equals the binary profile; payload `trust_root_id` equals the binary lineage | `TRUST_PROFILE_MISMATCH` / `STATEMENT_LINEAGE_MISMATCH` |

Consequences:
- A certification-status key signing under the `release-final` payloadType fails SV-6 with `PURPOSE_NOT_GRANTED`.
- A release payload wrapped in a certification payloadType fails SV-8 or SV-9.
- A historical-identity envelope found in a bundle or `governance/trust/` fails SV-2.

## 5. Authority questions answered

| Authority | Held by | Can another purpose exercise it? |
|---|---|---|
| Release authenticity (final) | `release-final` | Only by explicit root grant, and never to a key that holds `certification-status` or `verification-attestation` (KS-3, KS-4). |
| Release-candidate identity | `release-candidate` | `release-final` only if granted (OP-4). |
| Independent verification result | `verification-attestation` | No (KS-4…KS-6). |
| Certification state | `certification-status`. A CERTIFIED view additionally requires an ACCEPTED attestation and a trust-state reference (`17` §6). | No. |
| Revocation | release level: `revocation`. Key level: `root`. Unrevocation: `trust-policy`. | Revocation cannot unrevoke. |
| Retrieval profile | `retrieval-profile` | No. |
| Legacy/historical release identity | `release-final`, accepted **only** from the compiled copy. It confers `HISTORICAL_IDENTIFIED`, which is never eligible as a production policy root (`19` §7). | No. |
| Root | `root` threshold | No. |
| Floors, eligibility, install-authority floor | `trust-policy` (root keys, root threshold) | No. |
| Current install eligibility | nobody signs it; it is computed (`19` §6) | — |

## 6. Representation

- Key id: `ed25519:` followed by the 64 lowercase hex digits of SHA-256 over the raw public key. It is recomputed on
  every use (SV-4).
- Trust-root id (lineage): `sha256:` of the canonical version-1 root payload. Later root versions carry it as
  `lineage.trust_root_id`, and every statement carries it as `trust_root_id`.
- Canonical repository layout (public data only):
  - `trust/production/root/<version>.dsse.json`
  - `trust/production/policy/<policy_version>.dsse.json`
  - `trust/production/state/<sequence>.dsse.json`
  - `trust/production/statements/<digest>.dsse.json` (certification, attestation, revocation)
  - `trust/production/historical-identity.dsse.json`
  - test lineage under `tests/fixtures/trust/`

## 7. Ceremony and signing rules

1. **No private keys outside custody.** Private keys never exist in:
   - the canonical repository or any consumer repository, or their history;
   - release bundles, CI logs or CI secrets;
   - `.governance-runtime/`;
   - any machine used to build candidates.
2. **Sign what you reproduced** (`release-final`, `release-candidate`). The signer rebuilds from `git archive` of
   `release_commit` on the signing host and compares the unsigned payload byte for byte. Payload inputs are
   deterministic:
   - `released_at` is the committer time of `release_commit` (UTC);
   - `provenance.builder` is the fixed string `gov release build <version>`;
   - no clock or host data is included.
3. **Attest what you verified** (`verification-attestation`). The verifier attests the candidate digest it tested,
   with report and harness digests.
4. **Certify only what was attested** (`certification-status` CERTIFIED). Allowed only for a final whose
   `promoted_from_candidate` equals the candidate digest of an ACCEPTED attestation.
5. **Publish admissible state** (`trust-state`). `gov trust publish` refuses to produce a TSS that is not admissible
   against the previous published TSS (`17` S4).
6. **Producer hygiene.** `gov release build` refuses private key material (`PRIVATE_KEY_MATERIAL_DETECTED`),
   unchanged from rev 1.
7. **Ceremony record.** Public keys, grants, thresholds, trust-root id, custodians and date. Never secrets.

## 8. Rotation, revocation, re-attestation

- **Purpose rotation:** root version N+1 changes grants (signed by the threshold of both version N and version N+1).
- **Key revocation:** root version N+1 removes the key and lists it in `revoked_keys`.
- **Re-attestation:** payload digests do not depend on signatures. A genuine statement is re-signed by a current key
  without changing its digest, certification references, lock or trust-state entries.
- **Durability:** a verifier is protected by a rotation or revocation once it holds the new root version (compiled into
  patched binaries, bundles, PTR, VTS, refresh). Before that, residual `17` RS-1 applies.

## 9. Compromise and loss playbooks

| Event | Actions | Protection is durable once the verifier holds |
|---|---|---|
| `release-final` key stolen | Root N+1 removes the key. Revoke known malicious digests. Issue a TPS raising `min_release_sequence` above the highest possibly forged sequence. Re-attest genuine finals. Ship a patched binary compiling the new root, TPS and TSS. | root N+1 or the TPS |
| `release-candidate` key stolen | Root removes the key; revoke malicious candidate digests. | root N+1 (candidates were never production-eligible) |
| `verification-attestation` key stolen | Root removes the key; the certification holder reviews certifications that reference that key's attestations. | root N+1 |
| `certification-status` key stolen | Root removes the key; the trust-state publisher stops referencing forged certifications; revoke forged certification digests. | a TSS without the forged references |
| `revocation` key stolen | Root removes the key; a TPS `unrevokes` the forged revocations. | the TPS |
| `trust-state` key stolen | Root removes the key; a new key continues the sequence with an admissible TSS. | admissibility (regressions already rejected) |
| `retrieval-profile` key stolen | Root removes the key; forged profiles fail at the next rebuild. | root N+1 |
| One root key stolen or lost | The remaining custodians sign N+1. | immediately |
| Root threshold stolen or lost | New lineage; re-bootstrap (`06`). | reconfirmation |

## 10. Test, development and production separation

1. **Test profile is a separate binary.** The test lineage and keys compile only into a separate target `gov-test-profile`
   (its own crate), never into `gov`. The `gov` crate carries a `compile_error!` guard against the test-profile
   feature, so workspace feature unification cannot enable it (closes RV-L2). The release pipeline asserts that
   `gov version --trust` reports `production`, and the artifact statement records the profile.
2. **Production refuses test material.** Production binaries compile a deny-list of test key ids and refuse
   `trust_profile: test` in every statement, root, lock and trust record.
3. **Development builds.** A development binary built from a checkout compiles that checkout's production root. Its
   embedded kernel is `DEVELOPMENT_UNSIGNED` unless the compiled statement verifies. Lineage pinning (`06`) exposes a
   substituted root.

## 11. Algorithms

Ed25519 (RFC 8032, pure, strict verification) and SHA-256 are the only approved algorithms in revision 2. Algorithm
migration is expressible: a purpose may list `require_algorithms` (SV-7), so a root version can require one signature
per algorithm during a transition. This resolves the rev 1 claim the schema could not represent.
