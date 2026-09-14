# Output 5 — Key-purpose and key-management model

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 5 changes (rule FD-1, `29`; BC4-1 and BC4-4):
> - adds **`release-registration`** and **`reproducer`**; **withdraws `release-artifact` and `build-attestation`**
>   (`30` §3); `verification-attestation` and `release-final` become restrictors;
> - replaces KS-9 and KS-10 with **KS-9′** and **KS-10′**, adds **KS-12** and **KS-13**, and adds the **Fact Threshold
>   Check** to SV-4 (`29` §5.2);
> - re-derives every minimum-capability statement from the derivation calculator (§3; FD-3), with pipeline input counted;
> - rotation never re-signs reproductions (§8); playbooks cover the new purposes (§9);
> - the source identity uses the canonical content digest (§11).
>
> Retained (review r4 CD4-0): the compiled whitelist principle, KS-1…KS-8, KS-11, SV-1…SV-11, purpose-bound DSSE.

## 1. Purposes

A **purpose** is the authority a key exercises when it signs. Every statement type maps to exactly one purpose, fixed in the
binary. Root metadata grants purposes to keys under compiled constraints (§3).

| Purpose | Signs | May assert | May never assert | Keys / threshold (owner option) | Impact if this key alone is stolen |
|---|---|---|---|---|---|
| `root` | `trust-root.v4` | key set, grants, thresholds, the reproducer quorum, key revocation | releases, state | OP-1 | none below threshold |
| `trust-policy` | `trust-policy.v3` | Constitutional Surface classification, floors, precedence registration, Overlay Surface, owner-domain slots and binding groups, eligibility, install authority, gating, bootstrap and registration parameters, lowering history, unrevocation, chain reset | authenticity, registrations of releases (except under OP-2 (a) through `release-registration`) | root keys at root threshold (KS-2) | as root |
| **`release-registration`** | **`release-registration.v1`** (`30` §5) | that release *R* is registered with this source identity, input manifest, final, targets, verification records, constitutional unit map and kernel tree digest (and, under OP-9 (d), binary digests) — only after the ceremony checks of `30` R-REG-3 | anything about other releases; trust state; currency | OP-2: root keys at root threshold, or a delegated quorum ≥ 2 (KS-10′) | **one key: nothing** (threshold ≥ 2). At the threshold: registers malicious source, inputs or non-orderable content for a new release; accepted only with OP-8 verification statements and publication (`30` §10) |
| **`reproducer`** | **`binary-reproduction.v1`** (`30` §7), one signature per statement | that this reproducer built the registered source with the registered inputs for a target and obtained this binary and TBM digest | release authenticity; source legitimacy; state | OP-9: n keys, compiled quorum ≥ 2 (KS-9′) | **one key: nothing**; it can block one release by conflict (AV-S1) |
| `trust-state` | `trust-state.v3` | the published set at a sequence: registrations, published binaries, revocations, prior states and policies | legitimacy of a release or binary; currency (a TSS is never a witness) | OP-4 | **Anchored machine:** a statement that does not descend from the anchor is never effective. A descendant issued after a pin or confirmation carries **no C3** there (`24` §4.4 revision 5). A descendant dropping a held revocation or reference is non-admissible. **First admission:** never selected unless its fingerprint is typed. **Never:** register a release, create reproductions, lift a negative, witness currency. |
| `release-final` | `release-final.v3` | authenticity of final release content | binaries, source legitimacy, eligibility, registration | OP-4 | **nothing becomes effective**: a final is a policy root or the source of a binary only if a registration names its digest (restrictor); `release-final` appears in no minimal set (CS5 INV-RF) |
| `release-candidate` | `release-candidate.v3`, `artifact-candidate.v3` | candidates for gated evaluation projects | final stage, production binaries | OP-4 | forged evaluation candidates in gated evaluation projects only |
| `verification-attestation` | **`verification-attestation.v3`** | the verifier's verdict for one candidate over its source identity and input manifest, and the negative a new verdict lifts | certification, authenticity, registration | OP-8 | **ACCEPTED selects nothing** without the registration; REJECTED refuses (denial of service) |
| `certification-status` | `certification-status.v3` | CERTIFIED / REJECTED / WITHDRAWN for a final | authenticity | OP-4 | negatives take effect (denial of service); CERTIFIED stays unreferenced and cannot lift a negative |
| `revocation` | `revocation.v2` | refusal of named digests | new trust; unrevocation | OP-4 | denial of service only |
| `retrieval-profile` | `retrieval-profile.v1` | provenance of a reference retrieval profile | authorisation | OP-4 | profile integrity only |
| `freshness-witness` (OP-7 (c)) | `freshness-witness.v1` | that an existing TSS was the latest as of `issued_at`, for a TSS taken from the owner's ceremony or channel (CR4-B-02) | any state | OP-7; C3 needs ≥ 2 keys under ≥ 2 custodians | one key at threshold 2: nothing; keys at the C3 threshold: stale selection of genuine TSSs on witness-reliant machines until rotation (RS-5) |
| ~~`release-artifact`~~ | **withdrawn** | — | — | — | never granted (KS-13) |
| ~~`build-attestation`~~ | **withdrawn** | — | — | — | never granted (KS-13) |

The test lineage is a trust profile, not a purpose; it exists only in the separate test-profile binary (§10).

## 2. Compiled statement-type table (T0)

| payloadType (`application/vnd.agentic-engineering-os.` …) | Purpose | Revision 5 |
|---|---|---|
| `trust-root.v4+json` | `root` | purposes of §1; `quorums {reproducer}` |
| `trust-policy.v3+json` | `trust-policy` | `registration {min_verification_records, binary_digests_registered}`; `bootstrap {…, channel_quorum, admitter_digests, workstation_record_max_validity_days, revoked_self_scope, accepted_tbm_reset}`; `eligibility.production_sources[]` withdrawn |
| **`release-registration.v1+json`** | `release-registration` | new (`schemas/release-registration.schema.json`) |
| **`binary-reproduction.v1+json`** | `reproducer` | new (`schemas/binary-reproduction.schema.json`) |
| `trust-state.v3+json` | `trust-state` | `registrations[]`, `published_binaries[]`; `artifacts[]` withdrawn |
| `release-final.v3+json`, `release-candidate.v3+json` | `release-final`, `release-candidate` | `release.source {release_commit, content_digest}`, `inputs_manifest_digest` |
| `artifact-candidate.v3+json` | `release-candidate` | evaluation only |
| **`verification-attestation.v3+json`** | `verification-attestation` | source identity and input manifest |
| `certification-status.v3+json`, `revocation.v2+json`, `retrieval-profile.v1+json`, `freshness-witness.v1+json` | as named | unchanged shapes |

**Withdrawn** (never issued, refused by every revision-5 binary): `artifact-final.v2+json`, `build-attestation.v2+json`,
`verification-attestation.v2+json`, `trust-state.v2+json`, `historical-identity.v1+json`. Unsigned documents with registered
digests: `input-manifest.v1+json` (`30` §4.2). Local records (never signed): the admission record (`31` R-ADM-7).

## 3. Grants, separation and the Fact Threshold Check (compiled)

Root metadata lists, per purpose, `key_ids`, `threshold` and optionally `require_algorithms`, plus `quorums.reproducer`
(`schemas/trust-root.schema.json`, `x-schema-version` 4.0.0). The binary checks every root version; a violation invalidates
that version (`PURPOSE_SEPARATION_VIOLATION` or `ROOT_VERSION_INVALID`).

**Compiled whitelist.** A key may hold two or more purposes only if every pair is listed:

| Permitted pair | Why | Owner choice |
|---|---|---|
| `root` + `trust-policy` | floors are constitutional (KS-2) | mandatory |
| `root` + `release-registration`, `trust-policy` + `release-registration` | registration at root threshold | OP-2 (a) only |
| `release-final` + `release-candidate` | stage separation still holds | OP-4 |
| `revocation` + `certification-status` | both only add negatives or unreferenced positives | OP-4 |
| `revocation` + `trust-state` | revocation adds negatives; trust-state references them | OP-4 |
| `retrieval-profile` + `release-final` | profile integrity only | OP-4 |

**Named constraints:**

| ID | Constraint | Reason |
|---|---|---|
| KS-1′ | `root` keys may additionally hold only `trust-policy` and, under OP-2 (a), `release-registration` | root keys stay offline |
| KS-2 | `trust-policy` key ids ⊆ `root` key ids; threshold ≥ root threshold | constitutional content |
| KS-3…KS-8 | unchanged (release-final ∩ certification = ∅; release-final ∩ verification = ∅; certification ∩ verification = ∅; release-candidate ∩ (certification ∪ verification) = ∅; well-formedness, no revoked key granted; trust-state ∩ (certification ∪ verification) = ∅) | as revision 4 |
| **KS-9′** | `reproducer` keys hold no other purpose; `quorums.reproducer` ≥ 2 | bytes need two first-hand establishers (BC4-1) |
| **KS-10′** | `release-registration` threshold ≥ 2; its keys are root keys with threshold ≥ root threshold (OP-2 (a)) or hold no other purpose (OP-2 (b)) | the selector of source, inputs and content is never one key |
| KS-11 | `freshness-witness` keys hold no other purpose; C3 needs ≥ 2 distinct witness keys | currency not from a key that chooses state |
| **KS-12** | `verification-attestation` ∩ (`reproducer` ∪ `release-registration`) = ∅ | the verifier neither registers nor reproduces |
| **KS-13** | `release-artifact` and `build-attestation` are never granted | withdrawn pass-through purposes |

**Fact Threshold Check (FTC).** SV-4 applies KS-9′, KS-10′, KS-12 and KS-13 to every root version, in `gov`, in `gov-admit`
and in `gov trust draft-policy`. Owner options can raise the quorum and thresholds, never lower them. Evidence:
P4r5 `AP-R5_ftc_reproducer_key_shared`, `AP-R5_ftc_withdrawn_purpose_granted` (both `ROOT_VERSION_INVALID`); DA03r5 mutant
`R5-ftc` detected.

**Minimum capability sets (FD-3: calculator output, `evidence/r5/CS5-tcb-capability-sets.json`; `30` §10 gives every
OP-9 row).**

| Consequence | Minimal sets (processes / key theft) | Owner options that change it |
|---|---|---|
| accepted malicious bytes for a genuine release | q reproducer processes; or q reproducer keys + trust-state key + the victim's channel(s) + transport (or + registration keys); never on pinned machines by key theft | OP-9, OP-13 |
| accepted malicious source, faithfully built | route I (TB-4); OP-8 verification processes + pipeline (TB-4′); registration custodians at threshold + OP-8 verification keys; key theft: registration keys + OP-8 verification keys + q reproducer keys + trust-state key + channel(s) | OP-2, OP-8, OP-9, OP-13 |
| accepted malicious named build inputs | registration custodians at threshold + OP-8 verification keys; key theft as above | OP-2, OP-8 |
| poisoned input mirror | none (inputs by digest) | — |
| compromised upstream toolchain | TA-12 under OP-10 (a) | OP-10 |
| visible CERTIFIED | 3 (verification-attestation, certification-status, trust-state) | — |
| lift of WITHDRAWN/REJECTED | 3, with an attestation issued for the lift naming the negative | — |
| C3 currency on a witness-reliant machine | 2 witness keys (compiled) under 2 custodians (CR4-B-02) | OP-7 |
| new floor, surface classification, precedence registration, lowering, clock reset, reproducer quorum | root threshold | OP-1 |

No single key of any purpose, and no key together with pipeline or transport input, yields an accepted production binary,
registers a release, lifts a negative, witnesses C3 currency or changes constitutional classification (CS5: 0 failures of
INV-ONE over 408 configurations).

## 4. Signature verification rules (every statement, every source)

SV-1…SV-11 are unchanged from revision 4, with two amendments:
- **SV-4** also applies the Fact Threshold Check (§3).
- **SV-7** counts a threshold per statement for every purpose **except `reproducer`**, whose statements carry exactly one
  signature each; the reproducer quorum is counted across statements by distinct keys (`25` AP-6).

## 5. Authority questions answered

| Authority | Held by | Can another purpose exercise it? |
|---|---|---|
| Source identity, input manifest, final, targets and constitutional units of a release | the release registration (OP-2) | no; `release-final`, `verification-attestation` and the pipeline select none of them |
| Faithful build of a registered release | ≥ q first-person reproductions (OP-9); under (d) also the registration | no |
| Publication and negatives | `trust-state` within an anchored, currency-proven chain; `revocation` | no |
| Production binary acceptance | admission-predicate/1 by an evaluator other than the candidate (`25` §5, `31`) | no |
| Verification result | `verification-attestation` (restrictor) | no |
| Certification state | `certification-status`; a visible CERTIFIED also needs an attestation and a trust-state reference | no |
| Currency on a machine | proven locally (P1 naming the TSS, P2, P3) | never `trust-state` |
| Current install eligibility | computed (`19` §6) | — |

## 6. Representation

Key id: `ed25519:` + 64 lowercase hex of SHA-256(raw public key), recomputed on every use. Trust-root id: `sha256:` of the
canonical v1 root payload. Canonical repository layout (public data only): `trust/production/root/<version>.dsse.json`,
`policy/<version>.dsse.json`, `state/<sequence>.dsse.json`, `registrations/<release_id>.dsse.json`,
`reproductions/<release_id>/<target>/<key id>.dsse.json`, `manifests/<digest>.json`, `statements/<digest>.dsse.json`,
`fingerprints.txt` (convenience copy, not a channel). Test lineage: `tests/fixtures/trust/`.

## 7. Ceremony and signing rules

1. **No private keys outside custody** (unchanged).
2. **Sign what you reproduced** (`release-final`, `release-candidate`): the signer rebuilds the unsigned payload from the
   source identity and checks `content_digest` and `inputs_manifest_digest`; a final's signer checks V8.
3. **Attest what you verified** (`verification-attestation`, `30` R-VER-1): reproduce the candidate payload, check the input
   manifest against upstream signed checksums, and return the record first-hand to the registration ceremony.
4. **Certify only what was attested** (unchanged).
5. **Register before you release** (`release-registration`, `30` R-REG-3): the ceremony signs only with first-hand
   verification records, upstream checksum evidence, each custodian's own `content_digest` and, under OP-9 (d), each
   custodian's own reproduction; `gov trust draft-registration` refuses without them and lists every unit change and
   computed reduction.
6. **Reproduce first-hand** (`reproducer`, `30` R-REP-1…R-REP-3): inputs by digest; one signature; confirm first-hand to the
   publisher.
7. **Publish only quorum-reproduced, registered binaries** (`trust-state`, `30` R-PUB-1…R-PUB-4): references are cumulative;
   one published digest per release and target; state fingerprint in the channels.
8. **Producer hygiene** (unchanged): `gov release build` refuses private key material and runs the surface checker with the
   release's registration.
9. **Ceremony record:** public keys, grants, thresholds, quorum, lineage id, custodians, reproducer environments, verifier
   identities, date; never secrets.
10. **Witness custody (OP-7 (c), CR4-B-02):** the witness service takes the fingerprint only from the owner's ceremony or
    the channel; the C3 witness threshold is met by keys under at least two custodians, or `gov trust draft-policy` flags
    the one-custody consequence.

## 8. Rotation, revocation, re-signing and re-reproduction

- **Purpose rotation:** root N+1, signed by the thresholds of N and N+1. **Key revocation:** root N+1 removes the key and
  lists it in `revoked_keys`.
- **Re-signing (RV3-L8, retained):** before publishing a root N+1 that removes a key, the owner re-signs retained honest
  statements of that key with a successor key: the trust-state history, finals and candidates, attestations,
  certifications, witnesses and registrations (payload digests unchanged, so anchors and references hold).
- **Reproductions are never re-signed** (`30` R-REP-7): a reproduction by a removed key is replaced by a new reproduction
  under the successor key, or the release is re-reproduced. Re-signing would launder the reproductions a stolen key signed
  (specialist B N19).

## 9. Compromise and loss playbooks (revision 5)

Every row that publishes root N+1 includes §8.

| Event | Actions | Durable once the verifier holds |
|---|---|---|
| `release-final` or `release-candidate` key stolen | root N+1 removes the key; re-sign genuine finals | root N+1 |
| one `release-registration` key stolen | root N+1 replaces it (threshold) | root N+1 |
| registration keys at threshold stolen (OP-2 (b)) | root N+1 removes them; **revoke** every registration they signed that the owner did not issue; the next TSS keeps every `registrations[]` reference and adds the revocations | root N+1 and the TSS |
| one `reproducer` key stolen | root N+1 replaces it; revoke its forged reproductions (clears `REPRODUCTION_CONFLICT`); re-reproduce its honest ones | root N+1 and revocations |
| reproducer keys or processes at the quorum compromised | root N+1 removes the keys; revoke the published malicious digests; the next TSS keeps `published_binaries[]` and adds revocations; advise re-admission; review OP-9 | root N+1 and the TSS |
| `verification-attestation` key stolen | root N+1 removes the key; revoke attestations the verifier did not issue; review registrations that listed them | root N+1 and revocations |
| `certification-status`, `revocation`, `retrieval-profile` key stolen | as revision 4 | root N+1 or the TPS |
| `trust-state` key stolen | root N+1 removes the key and re-signs the retained history; a TPS `state_chain_reset` if histories forked | root N+1 / the TPS |
| `freshness-witness` keys stolen | root N+1 removes them; TPS `bootstrap.clock_reset` if needed; advise re-anchoring | root N+1 and the TPS |
| compromised upstream toolchain discovered | revoke affected binaries; register a new release with a corrected manifest; review OP-10 | revocations |
| one root key stolen or lost | remaining custodians sign N+1 | immediately |
| root threshold stolen or lost | new lineage; re-admission everywhere (`31`) | re-admission |

## 10. Test, development and production separation

Unchanged: the test lineage compiles only into `gov-test-profile`; production refuses test material; development binaries
have TBM `build: development`, are never admitted, never record an accepted TBM (CR4-B-08), and their embedded kernel is
`DEVELOPMENT_UNSIGNED` unless its registration verifies.

## 11. Algorithms

Ed25519 (RFC 8032, strict) and SHA-256 only. The source identity binds `content_digest` (SHA-256 over sorted mode, path and
blob SHA-256 lines), so it does not rest on SHA-1 commit ids and does not depend on archive tools or time
(`evidence/r5/SRC5-source-identity.json`).
