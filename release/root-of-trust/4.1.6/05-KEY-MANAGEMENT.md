# Output 5 — Key-purpose and key-management model (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises the key model to CP-1 (`35`) under the owner selections OP-1, OP-2 (b), OP-4 and "First-contact
> composer/signer" (OWNER-DESIGN-REQUIREMENTS-0001):
> - every purpose has one exact shape (key count, threshold) checked on every root version (§3; `PROFILE_NONCONFORMANT`);
> - new purpose **`first-contact-authority`** on the root keys at root threshold (KS-18; `32` §3);
> - the compiled whitelist is reduced to three pairs, all among root-held purposes (§3); release-registration, release-candidate,
>   release-final, trust-state, revocation, certification-status and retrieval-profile keys each hold one purpose;
> - `release-final` threshold ≥ 2 (KS-15), `trust-state` and `revocation` exactly 2 of 3 (KS-16, KS-17);
> - the witness purpose is removed by exclusion (EX-01); registration at root threshold is excluded (EX-09);
> - §1 and §2 list the revision-7 payload versions and name the first-contact codes (RV6-L2, CR6-B-05).
> Retained: SV-1…SV-11, purpose-bound DSSE, the Fact Threshold Check, KS-3…KS-9′, KS-12…KS-14, rotation without re-signing
> reproductions. Revision-6 text is history at `4106885`.

## 1. Purposes

A **purpose** is the authority a key exercises when it signs. Every statement type maps to exactly one purpose, fixed in the
binary. Root metadata grants purposes to keys; the CP-1 shape of every grant is compiled (§3).

| Purpose | Signs | May assert | May never assert | CP-1 keys / threshold | Impact if one key alone is stolen |
|---|---|---|---|---|---|
| `root` | `trust-root.v5` | key set, grants, the reproducer quorum, key revocation, `profile_id` | releases, state | exactly 3 keys, threshold 2; custodial roles: product-owner root custodian, independent security root custodian, recovery root custodian; offline hardware-backed devices (OP-1) | none |
| `trust-policy` | `trust-policy.v4` | Constitutional Surface classification, floors, precedence, Overlay Surface, owner-domain slots and binding groups, eligibility, install authority, gating (always gate), admission ceilings (lower only), the supplier and toolchain registry, certified targets, lowering history, unrevocation, chain reset | authenticity; registrations of releases | the root keys at root threshold (KS-2) | none |
| **`first-contact-authority`** | **`first-contact-authority.v1`** (`32` §3) | lineage, the admitter digest per certified target, the two first-contact sources, the procedure digest, the admitter's evidence | state; releases other than the admitter | the root keys at root threshold (KS-18) | none |
| `release-registration` | `release-registration.v3` (`30` §5); `registration-revocation.v1` (`30` R-REG-11) | that release *R* is registered with this source identity, input manifest, environment lock, environments, toolchains, final, targets, verification records, binary digests, constitutional unit map and kernel tree digest, each established first-hand (`30` R-REG-3); that a named restricting statement is forged | anything about other releases; trust state; currency | exactly 3 single-purpose keys, threshold 2 (OP-2 (b); KS-10″) | nothing |
| `reproducer` | `binary-reproduction.v3` (`30` §7) and `environment-reproduction.v2` (`33` R-BENV-7″), one signature per statement | that this reproducer built or assembled the registered input and obtained this digest | release authenticity; source legitimacy; state | exactly 3 single-purpose keys (three reproducer roles); compiled quorum 2 (OP-9 (b); KS-9′) | nothing; it can block one release by conflict (AV-S1) |
| `trust-state` | `trust-state.v4` | the published set at a sequence: registrations, published binaries, revocations and their statements, prior states, the root, policy and first-contact authority in force | legitimacy of a release or binary; currency; any first-contact value | exactly 3 single-purpose keys, threshold 2 (OP-4; KS-17) | nothing: one key signs no Trust State. The **state code** a machine types is published by the two sources only for a Trust State they verified at threshold (`32` R-FCS-2) |
| `release-final` | `release-final.v3` | authenticity of final release content | binaries, source legitimacy, eligibility, registration | at least 2 single-purpose keys, threshold ≥ 2 (OP-4; KS-15) | nothing: a final is effective only when a registration names it, promoted from the registered candidate with the registered kernel, with two verification records bound to them (`34`) |
| `release-candidate` | `release-candidate.v3`, `artifact-candidate.v3` | candidates for gated evaluation projects | final stage, production binaries, certification | one single-purpose key (OP-4 "separate candidate key: YES"; KS-15) | forged evaluation candidates in gated evaluation projects only |
| `verification-attestation` | `verification-attestation.v5` | one verifier's verdict for one candidate over its source identity, input manifest, kernel tree, environments and toolchains, with its execution id and report digest | certification, authenticity, registration | one key per independent verifier; each attestation one verifier; production eligibility needs two from distinct keys, executions and reports (OP-8) | ACCEPTED selects nothing without the registration; REJECTED refuses (denial of service) |
| `certification-status` | `certification-status.v3` | CERTIFIED / REJECTED / WITHDRAWN for a final | authenticity | at least 2 single-purpose keys, threshold ≥ 2 (OP-4; KS-16) | nothing |
| `revocation` | `revocation.v3` (`authority`: `revocation-quorum` or `root-emergency`) | refusal of named digests | new trust; unrevocation; removal of a restrictor (AP-5r) | exactly 3 single-purpose keys, threshold 2; the root threshold may sign an emergency revocation (OP-4; KS-16) | nothing |
| `retrieval-profile` | `retrieval-profile.v1` | provenance of a reference retrieval profile | kernel, release, trust-state or any other material | single-purpose key (OP-4; KS-16) | profile integrity only |
| ~~`release-artifact`~~, ~~`build-attestation`~~ | withdrawn (revision 5) | — | — | never granted (KS-13) | — |
| ~~`freshness-witness`~~ | removed by exclusion (EX-01) | — | — | a root granting it is `PROFILE_NONCONFORMANT` | — |

The test lineage is a trust profile, not a purpose; it exists only in the separate test-profile binary (§10).

## 2. Compiled statement-type table (T0), revision 7

| payloadType (`application/vnd.agentic-engineering-os.` …) | Purpose | Schema (`schemas/`) |
|---|---|---|
| `trust-root.v5+json` | `root` | `trust-root.schema.json` 5.0.0: exact purpose shapes; `quorums.reproducer` const 2; `profile_id` |
| `trust-policy.v4+json` | `trust-policy` | `trust-policy-statement.schema.json` 4.0.0: `gating.mode` const `always_gate`; `bootstrap {clock_reset, accepted_tbm_reset, admission_ceilings}`; `registration.min_verification_records` const 2; `supply_chain`; `certified_targets`; `profile_id` |
| `first-contact-authority.v1+json` | `first-contact-authority` | `first-contact-authority.schema.json` 1.0.0 |
| `release-registration.v3+json` | `release-registration` | `release-registration.schema.json` 3.0.0 |
| `registration-revocation.v1+json` | `release-registration` | `registration-revocation.schema.json` |
| `binary-reproduction.v3+json` | `reproducer` | `binary-reproduction.schema.json` 3.0.0 (`environment_id`, `toolchain_id`) |
| `environment-reproduction.v2+json` | `reproducer` | `environment-reproduction.schema.json` 2.0.0 (`lock_digest`, `supplier_id`) |
| `trust-state.v4+json` | `trust-state` | `trust-state-statement.schema.json` 4.0.0 (`references.first_contact_authority`, `revocation_statements`) |
| `release-final.v3+json`, `release-candidate.v3+json`, `artifact-candidate.v3+json` | `release-final`, `release-candidate` | release statements |
| `verification-attestation.v5+json` | `verification-attestation` | `verification-attestation.schema.json` 5.0.0 (`environment_ids`, `toolchain_ids`, `verifier_execution_id`, `verification_report_digest`) |
| `certification-status.v3+json`, `revocation.v3+json`, `retrieval-profile.v1+json` | as named | `revocation-statement.schema.json` 3.0.0 (`authority`) |

**First-contact codes** (not signed documents; digests of signed statements, `32` §4): trust code `gov-fct:…` over the FCA
payload; state code `gov-fcs:…` over the Trust State.

**Unsigned documents with registered digests:** `input-manifest.v3`, `environment-lock.v1` (registered source), the derived
`environment-manifest.v2` (`33` §4). **Local records (never signed):** admission record v3 (`31` R-ADM-7″), trust-state pin v3,
trust-gate confirmation v3, trust decision pin v4.

**Withdrawn** (refused by every CP-1 binary): `freshness-witness.v1` (EX-01), the first-contact manifest of revision 6 (EX-23),
`artifact-final.v2`, `build-attestation.v2`, `verification-attestation.v2`…`v4`, `trust-state.v2`…`v3`, `release-registration.v1`…`v2`,
`binary-reproduction.v1`…`v2`, `environment-reproduction.v1`, `historical-identity.v1`.

## 3. Grants, separation and the Fact Threshold Check (compiled)

Root metadata lists, per purpose, `key_ids` and `threshold`, plus `quorums.reproducer` and `profile_id`
(`schemas/trust-root.schema.json` 5.0.0). The binary checks every root version; a violation invalidates that version
(`PROFILE_NONCONFORMANT`, `PURPOSE_SEPARATION_VIOLATION` or `ROOT_VERSION_INVALID`).

**Compiled whitelist (CP-1).** A key may hold two purposes only if the pair is listed:

| Permitted pair | Why |
|---|---|
| `root` + `trust-policy` | floors are constitutional (KS-2) |
| `root` + `first-contact-authority` | the first-contact root is approved at root threshold (KS-18) |
| `trust-policy` + `first-contact-authority` | both held only by the root keys |

Every other pair is refused. The revision-6 pairs for registration at root threshold, a shared candidate and final key, and
negative-only or profile keys sharing with other purposes are not part of CP-1 (EX-09, EX-10; OP-4 "domain-separated and
mechanically enforced").

**Named constraints:**

| ID | Constraint | Reason |
|---|---|---|
| **KS-1″** | `root` keys may additionally hold only `trust-policy` and `first-contact-authority` | root keys stay offline and never register releases |
| KS-2 | `trust-policy` key ids equal the `root` key ids; threshold ≥ root threshold | constitutional content |
| KS-3…KS-8 | release-final ∩ certification = ∅; release-final ∩ verification = ∅; certification ∩ verification = ∅; release-candidate ∩ (certification ∪ verification) = ∅; well-formedness, no revoked key granted; trust-state ∩ (certification ∪ verification) = ∅ | as revision 4 (implied by the CP-1 whitelist) |
| **KS-9′** | `reproducer`: exactly 3 keys holding no other purpose; `quorums.reproducer` = 2 | bytes need two first-hand establishers (OP-9 (b)) |
| **KS-10″** | `release-registration`: exactly 3 keys holding no other purpose; threshold 2 | the selector of source, inputs and content is never one key and never the root keys (OP-2 (b)) |
| **KS-12** | `verification-attestation` ∩ (`reproducer` ∪ `release-registration`) = ∅ | the verifier neither registers nor reproduces |
| **KS-13** | `release-artifact` and `build-attestation` are never granted | withdrawn pass-through purposes |
| **KS-14** | `root`: exactly 3 keys, threshold 2, in every root version | OP-1; one root key never signs a Trust Policy, an FCA or a root version |
| **KS-15** | `release-candidate` shares no key with any purpose; `release-final` has at least 2 keys and threshold ≥ 2 | OP-4: no threshold-1 key mints a production identity |
| **KS-16** | `revocation`: exactly 3 keys, threshold 2; `certification-status`: ≥ 2 keys, threshold ≥ 2; `retrieval-profile` keys hold no other purpose | OP-4 purpose separation |
| **KS-17** | `trust-state`: exactly 3 keys holding no other purpose, threshold 2 | OP-4 |
| **KS-18** | `first-contact-authority` key ids equal the `root` key ids; threshold ≥ root threshold | owner "First-contact composer/signer": ordinary release or trust-state keys never redefine the first-contact root |

A root granting a purpose outside this table (for example the excluded witness purpose) is `PROFILE_NONCONFORMANT`.

**Fact Threshold Check (FTC).** SV-4 applies KS-1″…KS-18 to every root version, in `gov`, in `gov-admit` and in
`gov trust draft-policy`. CP-1 shapes are exact: no Trust Policy or root field raises or lowers them. Evidence: FA7 S4 R12, R14,
R15, R15b, R16 and S5 `root_threshold_1` (each `PROFILE_NONCONFORMANT` or `FIRST_CONTACT_AUTHORITY_UNVERIFIED`); PROF7 EX-01,
EX-09, EX-10, EX-23.

**Minimum capability sets.** Every consequence statement is a block generated by `evidence/r7/CS7-derivation-calculator.py` for
CP-1, placed in `30` §10 (bytes, source, inputs), `33` §6 (environment, toolchain), `34` §4 (content) and `32` §8–§9 (first
admission, revoked binaries). No single key of any purpose, and no key together with pipeline, transport or publication input,
yields an accepted production binary, registers a release, lifts a negative or changes constitutional classification
(invariant INV-ONE, 0 failures; BA12r7 brute force over key subsets below the thresholds: no accepting set with at most one key).

## 4. Signature verification rules (every statement, every source)

SV-1…SV-11 are unchanged from revision 4, with two amendments:
- **SV-4** also applies the Fact Threshold Check and the CP-1 shapes (§3).
- **SV-7** counts a threshold per statement for every purpose **except `reproducer`**, whose statements carry exactly one
  signature each; the reproducer quorum is counted across statements by distinct keys (`25` AP-6).

## 5. Authority questions answered

| Authority | Held by | Can another purpose exercise it? |
|---|---|---|
| Lineage, first-contact admitter and sources | `first-contact-authority` at root threshold | no |
| Source identity, input manifest, environments, toolchains, final, targets, binary digests and constitutional units of a release | the 2-of-3 release registration | no; `release-final`, `verification-attestation` and the pipeline select none of them |
| Faithful build of a registered release | ≥ 2 first-person reproductions from independent supplier classes and toolchain lineages, and the custodians' own reproduction | no |
| Publication and negatives | `trust-state` at 2 of 3 within an anchored, currency-proven chain; `revocation` at 2 of 3 or the root threshold | no |
| Production binary acceptance | admission-predicate/1 by an evaluator other than the candidate (`25` §5, `31`) | no |
| Verification result | `verification-attestation` (restrictor; two records) | no |
| Certification state | `certification-status` (negatives only) | no |
| Currency on a machine | proven locally from both sources' state codes (`24` §4.4) | never `trust-state` alone |

## 6. Representation

Key id: `ed25519:` + 64 lowercase hex of SHA-256(raw public key), recomputed on every use. Trust-root id: `sha256:` of the
canonical v1 root payload. Canonical repository layout (public data only): `trust/production/root/<version>.dsse.json`,
`policy/<version>.dsse.json`, `first-contact/<fca_sequence>.dsse.json`, `state/<sequence>.dsse.json`,
`registrations/<release_id>.dsse.json`, `reproductions/<release_id>/<target>/<key id>.dsse.json`, `manifests/<digest>.json`,
`statements/<digest>.dsse.json`. Repository copies are carriers, never sources. Test lineage: `tests/fixtures/trust/`.

## 7. Ceremony and signing rules

1. **No private keys outside custody.** Root keys live on offline hardware-backed devices under the three custodial roles, in
   physically separate custody; never in a repository, CI, cloud build environment or ordinary development workstation (OP-1).
   The same holds for registration, trust-state, revocation, release-final and certification keys (hardware-backed,
   single-purpose).
2. **Sign what you reproduced** (`release-final`, `release-candidate`): the signer rebuilds the unsigned payload from the source
   identity and checks `content_digest` and `inputs_manifest_digest`; a final's signer checks V8.
3. **Attest what you verified** (`verification-attestation`, `30` R-VER-1): reproduce the candidate in the derived environments
   and registered toolchain lineages, and return the record first-hand to the registration ceremony.
4. **Certify only what was attested.**
5. **Register before you release** (`30` R-REG-3 (a)–(h)); `gov trust draft-registration` refuses without the evidence.
6. **Reproduce first-hand** (`30` R-REP-1…R-REP-4).
7. **Publish only quorum-reproduced, registered binaries** (`30` R-PUB-1′…R-PUB-4).
8. **Approve the first-contact root at root threshold** (`32` R-FCA-1): only after the admitter's registration, reproduction
   and two verification records, each checked by every signing root custodian.
9. **Register suppliers and toolchain lineages at root threshold** (`33` R-BENV-1″, R-BENV-6″): provenance attributes and
   checksum keys are recorded from the custodians' own inspection, never from a pipeline.
10. **Producer hygiene:** `gov release build` refuses private key material and runs the surface checker with the release's
    registration.
11. **Ceremony record:** public keys, grants, thresholds, quorum, lineage id, custodial roles, the two first-contact sources and
    their custody domains, reproducer and verifier identities, supplier and toolchain provenance, date; never secrets.

## 8. Rotation, revocation, re-signing and re-reproduction

- **Purpose rotation:** root N+1, signed by the thresholds of N and N+1. **Key revocation:** root N+1 removes the key and lists it
  in `revoked_keys`.
- **Re-signing (retained):** before publishing a root N+1 that removes a key, the owner re-signs retained honest statements of
  that key with a successor key: the trust-state history, finals and candidates, attestations, certifications, registrations and
  FCAs (payload digests unchanged, so anchors, codes and references hold).
- **Reproductions are never re-signed** (`30` R-REP-7).

## 9. Compromise and loss playbooks

Every row that publishes root N+1 includes §8.

| Event | Actions | Durable once the verifier holds |
|---|---|---|
| `release-final` or `release-candidate` key stolen | root N+1 removes the key; re-sign genuine finals | root N+1 |
| one `release-registration` key stolen | root N+1 replaces it (threshold 2 of 3) | root N+1 |
| registration keys at threshold stolen | root N+1 removes them; revoke every registration they signed that the owner did not issue; the next TSS keeps every `registrations[]` reference and adds the revocations | root N+1 and the TSS |
| one `reproducer` key stolen | root N+1 replaces it; the registration authority revokes its forged reproductions with a `registration-revocation` (R-REG-11); re-reproduce its honest ones | root N+1 and the registration revocation |
| reproducer processes at the quorum compromised | root N+1 removes the keys; revoke the published malicious digests; advise re-admission | root N+1 and the TSS |
| `verification-attestation` key stolen | root N+1 removes the key; revoke attestations the verifier did not issue; review registrations that listed them | root N+1 and revocations |
| `certification-status`, `revocation`, `retrieval-profile` key stolen | root N+1 replaces it | root N+1 |
| one `trust-state` key stolen | root N+1 replaces it (threshold 2 of 3) | root N+1 |
| `trust-state` keys at threshold stolen | root N+1 removes them and re-signs the retained history; a TPS `state_chain_reset` if histories forked; the sources refuse descendants that drop published revocations (`32` R-FCS-2) | root N+1 / the TPS |
| one root key stolen or lost | remaining custodians sign N+1 | immediately |
| root threshold stolen or lost | new lineage; first admission everywhere (`31`, `32`) | first admission |
| an upstream environment component or supplier found malicious | revoke affected binaries; the root threshold removes or re-provenances the supplier in the Trust Policy registry; register a new release with a corrected lock | the TPS and revocations |
| a toolchain lineage found compromised | revoke affected binaries; the root threshold updates the toolchain registry; re-register | the TPS and revocations |
| a first-contact source compromised | publish the incident through the other source and the ceremony record; rotate the source in a new FCA at root threshold; machines admitted meanwhile re-admit (stores kept) | the next FCA |
| a defective admitter version | a new FCA at root threshold without its digest; revoke the digest in the next Trust State; genuine admitters refuse themselves (`ADMITTER_NOT_LISTED`, `ADMITTER_REVOKED`) | the FCA and Trust State |

## 10. Test, development and production separation

Unchanged: the test lineage compiles only into `gov-test-profile`; production refuses test material; development binaries have
TBM `build: development`, are never admitted, never record an accepted TBM, and their embedded kernel is `DEVELOPMENT_UNSIGNED`
unless its registration verifies.

## 11. Algorithms

Ed25519 (RFC 8032, strict) and SHA-256 only. The source identity binds `content_digest` v2 (`30` §4.1) and the Git tree id, so it
does not rest on SHA-1 commit ids alone and does not depend on archive tools or time (`evidence/r6/SRC6-source-identity-v2.json`,
retained).
