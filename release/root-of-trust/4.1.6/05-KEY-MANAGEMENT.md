# Output 5 — Key-purpose and key-management model

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 makes these changes:
> - adds `release-artifact` and `build-attestation` (R2-H3, `25`);
> - withdraws the threshold-1 historical-identity statement (historical releases move into the root-signed Trust Policy);
> - makes separation a compiled whitelist with KS-8…KS-10 (R2-M6);
> - corrects the single-key blast radius (R2-H3, R2-M2, R2-M3).

## 1. Purposes

A **purpose** is the authority a key exercises when it signs. Every statement type maps to exactly one purpose, fixed in
the binary. Root metadata grants purposes to keys under compiled constraints (§3).

| Purpose | Signs | May assert | May never assert | Default keys / threshold (`21`) | Impact if this key alone is stolen |
|---|---|---|---|---|---|
| `root` | `trust-root.v2` | key set, grants, thresholds, key revocation | anything about releases or state | 3 keys, threshold 2 | none below threshold |
| `trust-policy` | `trust-policy.v2` | Constitutional Surface (`23`), eligibility including historical releases, install authority, gating, bootstrap (OP-6, OP-7), lowering history, unrevocation, chain reset | authenticity, certification | root keys at root threshold (KS-2) | as root |
| `trust-state` | `trust-state.v2` | the published set of separately signed statements at a sequence, including artefact statements; optional expiry | any fact not itself separately signed | 1, threshold 1 | freezes C2/C3 on verifiers that receive an unresolvable, forked or regressive statement above their effective state, until superseded or rotated out (`17` §15); cannot lift negatives, create certification or regress honest successors |
| `release-final` | `release-final.v2` | authenticity of final release content | binaries, certification, verification, eligibility, trust state, surface registration | 1 active + 1 standby, threshold 1 (OP-2 may choose 2) | Authentic finals can be forged, but only content whose whole surface a root-signed TPS registers can become a policy root (E7). Ingress needs a local trust gate. No binary can be signed. |
| `release-candidate` | `release-candidate.v2`, `artifact-candidate.v2` | candidate content; candidate binaries for evaluation | final stage, production binaries, certification | 1, threshold 1 (OP-4) | candidates only; their references constrain only their own ingress (`17` S7) |
| **`release-artifact`** | `artifact-final.v2` | production binary digests, each bound to its Trust Base Manifest digest (`25` §3–§4) | release authenticity, certification, trust state, reproduction | **≥ 2 keys, threshold 2** (compiled minimum; OP-2 may add a root co-signature) | nothing (threshold) |
| **`build-attestation`** | `build-attestation.v1` | independent reproduction of a binary and its TBM from the tagged source | authenticity, certification | 1, threshold 1 (OP-2 may choose 2 rebuilders) | nothing alone (a binary also needs `release-artifact` ×2 and a trust-state reference) |
| `verification-attestation` | `verification-attestation.v1` | the verifier's verdict for one candidate digest | certification, authenticity | 1, threshold 1 | a verdict alone certifies nothing |
| `certification-status` | `certification-status.v2` | CERTIFIED / REJECTED / WITHDRAWN for a final (optionally naming artefact statements) | authenticity; CERTIFIED without an ACCEPTED attestation | 1 + standby, threshold 1 | Negatives take effect (denial of service). CERTIFIED stays unreferenced: invisible, and it cannot lift a negative (`17` MS-2). |
| `revocation` | `revocation.v2` | refusal of named digests | new trust; unrevocation | 1, threshold 1 | denial of service only |
| `retrieval-profile` | `retrieval-profile.v1` | provenance and integrity of a reference retrieval profile | authorisation; release authenticity | 1, threshold 1 | profile integrity only |

The **test** lineage is a trust profile, not a purpose. It exists only in the separate test-profile binary (§10).

## 2. Compiled statement-type table (T0)

| payloadType (`application/vnd.agentic-engineering-os.` …) | `_type` (`https://agentic-engineering-os/statement/` …) | Purpose | Accepted from |
|---|---|---|---|
| `trust-root.v2+json` | `trust-root/v2` | `root` | compiled; bundle, PTR, VTS, refresh (chain-verified) |
| `trust-policy.v2+json` | `trust-policy/v2` | `trust-policy` | any source |
| `trust-state.v2+json` | `trust-state/v2` | `trust-state` | any source |
| `release-final.v2+json` | `release/v3`, `stage = final` | `release-final` | any source |
| `release-candidate.v2+json` | `release/v3`, `stage = candidate` | `release-candidate` | any source |
| `artifact-final.v2+json` | `artifact/v3`, `stage = final` | **`release-artifact`** | any source |
| `artifact-candidate.v2+json` | `artifact/v3`, `stage = candidate` | `release-candidate` | any source (evaluation only) |
| `build-attestation.v1+json` | `build-attestation/v1` | `build-attestation` | any source |
| `verification-attestation.v1+json` | `verification-attestation/v1` | `verification-attestation` | any source |
| `certification-status.v2+json` | `certification/v3` | `certification-status` | any source |
| `revocation.v2+json` | `revocation/v2` | `revocation` | any source |
| `retrieval-profile.v1+json` | `retrieval-profile/v1` | `retrieval-profile` | any source |

**Withdrawn:** `historical-identity.v1+json`. Historical releases are TPS `eligibility.historical_releases[]`, signed at
root threshold and named by the Trust Base Manifest. No revision-3 binary accepts the revision-1 or revision-2 draft
payloadTypes, none of which was ever issued.

## 3. Grants and separation (compiled)

Root metadata lists, per purpose, `key_ids`, `threshold` and optionally `require_algorithms`
(`schemas/trust-root.schema.json`). A key listed under several purposes is a grant. The binary checks every root version.
A violation invalidates that version (`PURPOSE_SEPARATION_VIOLATION`).

**Compiled whitelist.** A key may hold two or more purposes only if **every pair** of its purposes is listed. Every
unlisted pair is forbidden.

| Permitted pair | Why permitted | Owner choice |
|---|---|---|
| `root` + `trust-policy` | floors are constitutional (KS-2 requires it) | mandatory |
| `release-final` + `release-candidate` | OP-4 "no separate candidate key"; stage separation and E2 still hold | OP-4 |
| `revocation` + `certification-status` | both only add negative facts or unreferenced positives | OP-2 |
| `revocation` + `trust-state` | revocation adds negatives; trust-state references them | OP-2 |
| `retrieval-profile` + `release-final` | profile integrity only | OP-2 |

**Named constraints** (all are consequences of the whitelist, stated for tests and error details):

| ID | Constraint | Reason |
|---|---|---|
| KS-1 | `root` keys may additionally hold only `trust-policy` | root keys stay offline |
| KS-2 | `trust-policy` key ids ⊆ `root` key ids; `trust-policy.threshold ≥ root.threshold` | floors and surface are constitutional |
| KS-3 | `release-final` ∩ `certification-status` = ∅ | authenticity is not certification |
| KS-4 | `release-final` ∩ `verification-attestation` = ∅ | signer is not verifier |
| KS-5 | `certification-status` ∩ `verification-attestation` = ∅ | certifier is not verifier |
| KS-6 | `release-candidate` ∩ (`certification-status` ∪ `verification-attestation`) = ∅ | same |
| KS-7 | every threshold between 1 and the key count; no revoked key granted; no public key under two ids | well-formedness |
| **KS-8** | `trust-state` ∩ (`certification-status` ∪ `verification-attestation`) = ∅ | A visible CERTIFIED, and any lift of a negative, needs three distinct keys (`17` §3; evidence `K1`, `K3`). |
| **KS-9** | `release-artifact` keys hold no other purpose; `threshold ≥ 2` | binaries carry root-threshold authority (`25`) |
| **KS-10** | `build-attestation` ∩ (`release-final` ∪ `release-candidate` ∪ `release-artifact`) = ∅ | the reproducer is not the signer |

**Minimum distinct keys, by consequence:**

| Consequence | Distinct keys |
|---|---|
| visible CERTIFIED | 3 (attestation, certification, trust-state) |
| lift of WITHDRAWN/REJECTED | 3 |
| accepted production binary | 4 (release-artifact ×2, build-attestation, trust-state) |
| new floor, surface registration or lowering | root threshold |

Key separation is not people separation. The constraints stop one stolen key, and in the cases above one custodian's
set of keys, from spanning the stated authorities.

## 4. Signature verification rules (every statement, every source)

| ID | Rule | Failure code |
|---|---|---|
| SV-1 | Strict envelope; no duplicate members; strict padded base64; payload ≤ 4 MiB; ≥ 1 signature | `STATEMENT_MALFORMED` |
| SV-2 | payloadType in the compiled table (§2); withdrawn types refused | `STATEMENT_TYPE_UNKNOWN` |
| SV-3 | Payload bytes equal their GOV-JCS-1 re-serialisation | `STATEMENT_MALFORMED` |
| SV-4 | Effective root chain built (`17` S2); key ids recomputed; duplicate public keys refused; whitelist and KS-1…KS-10 hold | `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` |
| SV-5 | Purpose = compiled mapping of the payloadType | — |
| SV-6 | Each signature: key in the effective root, granted the purpose, not revoked; algorithm from the key record; strict Ed25519 over PAE | `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` |
| SV-7 | Distinct valid keys ≥ threshold (compiled minimum 2 for `release-artifact`); `require_algorithms` satisfied | `THRESHOLD_NOT_MET` |
| SV-8 | Payload validates against the compiled schema | `STATEMENT_MALFORMED` |
| SV-9 | `_type`, `signing.purpose` and `stage` consistent with the payloadType | `STATEMENT_TYPE_MISMATCH` |
| SV-10 | `trust_profile` = binary profile; `trust_root_id` = binary lineage | `TRUST_PROFILE_MISMATCH` / `STATEMENT_LINEAGE_MISMATCH` |

## 5. Authority questions answered

| Authority | Held by | Can another purpose exercise it? |
|---|---|---|
| Final release authenticity | `release-final` | `release-candidate` only under OP-4 "no" |
| Production binary acceptance | `release-artifact` (≥ 2) + `build-attestation` + `trust-state` reference (`25` §5) | no |
| Verification result | `verification-attestation` | no |
| Certification state | `certification-status`; a visible CERTIFIED also needs an attestation and a trust-state reference | no |
| Revocation | release level `revocation`; key level `root`; unrevocation `trust-policy` | revocation cannot unrevoke |
| Historical-release set | `trust-policy` (inside the TPS) | no |
| Constitutional Surface and floors | `trust-policy` | no |
| Currency on a machine | nobody signs it; it is anchored locally (`24`) | — |
| Current install eligibility | nobody signs it; it is computed (`19` §6) | — |

## 6. Representation

- Key id: `ed25519:` + 64 lowercase hex of SHA-256(raw public key), recomputed on every use.
- Trust-root id: `sha256:` of the canonical v1 root payload.
- Canonical repository layout (public data only):
  - `trust/production/root/<version>.dsse.json`;
  - `policy/<policy_version>.dsse.json`;
  - `state/<sequence>.dsse.json`;
  - `statements/<digest>.dsse.json` (certification, attestation, revocation, build attestation);
  - `artifacts/<release_id>/artifact-final.dsse.json`;
  - `fingerprints.txt` (root and state fingerprints; convenience copy, not a channel).
- Test lineage: `tests/fixtures/trust/`.

## 7. Ceremony and signing rules

1. **No private keys outside custody.** Never in any repository or its history, bundles, CI logs, CI secrets,
   `.governance-runtime/`, or build machines.
2. **Sign what you reproduced** (`release-final`, `release-candidate`): the signer rebuilds the unsigned payload from
   `git archive` of `release_commit`, byte for byte, with deterministic inputs.
3. **Attest what you verified** (`verification-attestation`).
4. **Certify only what was attested** (`certification-status`).
5. **Register before you release** (`trust-policy`). `gov trust draft-policy` lists every surface classification change,
   registration change and computed reduction (`23` §6.2). The root ceremony signs only after reviewing it.
6. **Reproduce before you accept a binary** (`build-attestation`, `release-artifact`).
   - The rebuilder, a different custodian with its own toolchain, rebuilds from `source_commit` with the published build
     inputs, and attests only when the binary digest and TBM digest are identical.
   - The two `release-artifact` custodians sign only binaries that carry at least one build attestation.
7. **Publish admissible state** (`trust-state`). `gov trust publish` refuses a TSS that is not admissible, or whose
   `prior_states[]` is incomplete. The state fingerprint is published in the independent channels (`24` §3.1).
8. **Producer hygiene.** `gov release build` refuses private key material and runs the surface checker (`23` §6).
9. **Ceremony record.** Public keys, grants, thresholds, lineage id, custodians, date; never secrets.

## 8. Rotation, revocation, re-attestation

- **Purpose rotation:** root N+1, signed by the thresholds of N and N+1.
- **Key revocation:** root N+1 removes the key and lists it in `revoked_keys`.
- **Re-attestation:** payload digests do not depend on signatures.
- **Durability:** a verifier is protected once it holds root N+1. Anchored machines receive it through refresh or a
  bundle, and an anchor naming a TSS that references N+1 makes an unrotated machine `BELOW_ANCHOR` or `INCOMPLETE`
  (`17` §9).

## 9. Compromise and loss playbooks

| Event | Actions | Durable once the verifier holds |
|---|---|---|
| `release-final` key stolen | Root N+1 removes the key; revoke known forged digests; TPS raises `min_release_sequence`; re-attest genuine finals; publish TSS and state fingerprint. | root N+1 or the TPS |
| `release-candidate` key stolen | Root removes the key; revoke forged candidates. | root N+1 |
| One `release-artifact` key stolen | Root N+1 replaces it; nothing to revoke (threshold). | root N+1 |
| `release-artifact` ×2 (+ `build-attestation` + `trust-state`) stolen | Root N+1 removes the keys; revoke forged artefact digests; TSS stops referencing them; advise re-verification of installed binaries. | root N+1 plus a TSS without the references |
| `build-attestation` key stolen | Root removes the key; review attestations it signed. | root N+1 |
| `verification-attestation` key stolen | Root removes the key; the certification holder reviews dependent certifications. | root N+1 |
| `certification-status` key stolen | Root removes the key; revoke forged certification statements. Nothing becomes visible or lifted without the other two purposes. | root N+1 |
| `revocation` key stolen | Root removes the key; a TPS `unrevokes` forged revocations. | the TPS |
| `trust-state` key stolen | Root removes the key. If histories forked, a TPS `state_chain_reset`. Anchored machines already orphan forks (`17` S4 b). | root N+1 / the TPS |
| `retrieval-profile` key stolen | Root removes the key. | root N+1 |
| One root key stolen or lost | The remaining custodians sign N+1. | immediately |
| Root threshold stolen or lost | New lineage; re-bootstrap (`06`). | reconfirmation |

## 10. Test, development and production separation

1. **Separate binary.** The test lineage compiles only into `gov-test-profile`, a separate crate with a `compile_error!`
   guard in `gov`. The TBM records `trust_profile`, and the release pipeline and `verify-artifact` require `production`.
2. **Production refuses test material** in every statement, root, lock and trust record.
3. **Development builds.** A development binary has TBM `binary.build: development`. `verify-artifact` never accepts it,
   and its embedded kernel is `DEVELOPMENT_UNSIGNED` unless the compiled statement verifies.

## 11. Algorithms

Ed25519 (RFC 8032, strict) and SHA-256 only. `require_algorithms` allows a transition requiring one signature per
algorithm.
