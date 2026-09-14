# Output 25 — Binary, built-source and trust-base authenticity: admission-predicate/1

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 6** amends admission-predicate/1 for review r5:
> - AP-1…AP-3 take lineage, state, quorum and evaluator from the first-contact code (`32`; BC5-1);
> - AP-4 adds the registration's revocation and fails closed without a binary version (RV5-M9);
> - AP-5 binds counted attestations to exactly the registered candidate and kernel (`34` R-CON-2; BC5-3), and AP-5r lets only
>   the registration authority remove restrictors (CR5-B-01);
> - AP-6 counts reproductions only under registered environments (`33`; BC5-2);
> - §7 is restated from the calculator (BC5-4).
>
> Rewritten in revision 5 for BC4-1 and BC4-2 under rule FD-1 (`29`). Registration and reproduction: `30`. First admission:
> `31`, `32`. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

The `gov` binary carries T0; it is the trusted computing base. Revisions 3 and 4 added signers. Revision 5 changed **who
selects**: the registration selects source and inputs, a first-hand reproduction quorum establishes the bytes, and an
evaluator other than the candidate decides. Review r5 found three selectors revision 5 had not assigned. Revision 6 assigns
them:
- the build environment every reproducer used (RV5-H2);
- the constitutional content the registration signed but CI derived (RV5-H3);
- at first contact, the lineage, quorum and evaluator one channel page chose (RV5-H1).

## 2. Options evaluated (HO-0001 §3.3)

| Option | Revision 6 position |
|---|---|
| Threshold root signature | the release registration at root threshold (OP-2 (a)), or a root-granted quorum ≥ 2 (OP-2 (b)); OP-9 (d) adds the custodians' own reproduction |
| Separate binary or root-bundle attestation | first-person reproduction statements at a compiled quorum ≥ 2 (`30` §7) under registered environments (`33`) |
| Certification binding | not a selector; not required |
| Reproducible-build or provenance evidence | **mandatory**: source identity v2, digest-addressed input manifest v2 with registered environments, normative remapping profile (`30` §4, `33`, IR-REP-1…6) |
| Compiled trust-state digest; binary trust-policy digest | kept in the TBM as restrictors (AP-8), never selectors |
| Multi-signature | quorums across first-hand statements; root threshold ≥ 2 (KS-14); the Fact Threshold Check enforces the minima (`05` §3) |
| Platform or distribution code signing | an owner option for the **first-contact root** only (OP-13 (c), `32` §7); never a selector of production binaries |

## 3. Purposes

As `30` §3 and `05` §1: `release-registration` (with `registration-revocation`), `reproducer` (with
`environment-reproduction`), `verification-attestation` v4 and `release-final` as restrictors; `release-artifact` and
`build-attestation` withdrawn.

## 4. Trust Base Manifest v3

Schema: `schemas/trust-base-manifest.schema.json`, `x-schema-version` 3.0.0. Revision 6 adds `binary.version` as required and
`source.git_tree`.

| Field | Content |
|---|---|
| `binary` | name, **version** (required; AP-4), target, `trust_profile`, `build` (`release` or `development`), `source {release_commit, git_tree, content_digest}`, `inputs_manifest_digest` |
| `lineage` | `trust_root_id` |
| `root_chain[]` | `{version, statement_digest}` |
| `trust_policy` | `{policy_version, statement_digest}` |
| `trust_state` | `{sequence, statement_digest}` of a TSS that exists before the build |
| `embedded_release` | `{final_statement_digest, kernel_tree_digest}` |
| `compiled_rules` | `floor_schema_version` 3; purpose-table digest; statement-schema-set digest; **decision-register digest** (`29` R-SEL-1; `decision-register/DECISION_REGISTER.yaml`); format readers; command-register digest; in `gov-admit`, the compiled OP-13 answer and, under (c)/(d), the lineage (`32` FC-4, FC-7) |

The TBM cannot name the registration digest (under OP-9 (d) the registration names the binary). Nothing is hash-cyclic.

## 5. admission-predicate/1 (normative; both executors, `31` §3)

Inputs: the candidate's bytes (read once, never executed), the statements held (any source), the target, and the selector of
state. In **running mode** that selector is the machine's anchors and a currency proof. In **bootstrap mode** (`gov-admit`)
it is the first-contact codes typed now from the OP-13 sources, with the first-contact manifest (`32` §3).

| Step | Check | Refusal |
|---|---|---|
| AP-0 | The evaluator is not the candidate (digest comparison). | `SELF_EVALUATION_REFUSED` |
| AP-1 | Measure: SHA-256 of the buffer read once. **Bootstrap:** all typed codes identical, and at least the compiled first-contact quorum of them (`32` FC-4). | `CHANNEL_DISAGREEMENT` / `CHANNEL_QUORUM_NOT_MET` |
| AP-2 | Root chain from root v1 by dual-threshold links; the Fact Threshold Check (KS-1…KS-14) on every version. **Lineage, bootstrap:** root v1 is the root whose digest is the `lineage_id` of the first-contact manifest bound by the code (FC-5, FC-6), and under OP-13 (c)/(d) it must equal the compiled lineage (FC-7). Bundle order never matters. **Lineage, running:** the compiled lineage. A root v1 that fails the FTC leaves no lineage; a later version that fails it is invalid. | `FIRST_CONTACT_MANIFEST_MISMATCH` / `FIRST_CONTACT_LINEAGE_NOT_COMPILED` / `ROOT_CHAIN_INVALID` (root v1) / `ROOT_VERSION_INVALID` (later version) |
| AP-3 | **Select the Trust State.** **Bootstrap:** the verified TSS whose epoch `(root version and digest, policy version and digest, state sequence and digest)` equals the manifest's `state_epoch`. Its root and Trust Policy verify. That policy's `bootstrap.channel_quorum` may only raise the compiled quorum. The evaluator binding holds (FC-8: own digest listed and not revoked; manifest admitters equal the list). **Running:** the effective TSS by inclusion anchors (`24` §3.4), with a currency proof that **names that TSS** (P1 naming it within the window, P2 typed fingerprint, P3 witnesses at threshold; `24` §4.4). | `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` / `CHANNEL_QUORUM_NOT_MET` / `ADMITTER_NOT_LISTED` / `ADMITTER_REVOKED` / `FIRST_CONTACT_MANIFEST_INCONSISTENT` / `TRUST_STATE_UNANCHORED` / `…_BELOW_ANCHOR` / `…_REGRESSION` / `…_CURRENCY_UNPROVEN` |
| AP-4 | **Negatives** of the selected state: the binary digest, its release, **the registration**, the registered final and the registered candidate are not revoked. Revoked reproductions, attestations and keys count for nothing below. **Binary floor:** when the selected Trust Policy sets `eligibility.min_binary_version`, the TBM's `binary.version` MUST be present and ≥ it; a TBM without a version then fails closed. | `BINARY_REVOKED` / `BINARY_BELOW_TRUST_POLICY` |
| AP-5 | **Registration and verification:** exactly one verified `release-registration` for the release id (else `REGISTRATION_EQUIVOCATION`), at the registration threshold, referenced by the selected TSS, not revoked; the target registered; the registered final statement held, verifying under `release-final`, with the registered source, **promoted from the registered candidate and carrying the registered kernel tree digest**; no held REJECTED attestation for the registered candidate (subject to AP-5r); ≥ OP-8 ACCEPTED attestations by distinct keys that the registration lists, each naming **exactly the registered candidate, source, inputs and kernel tree digest** (`34` R-CON-2). | `RELEASE_UNREGISTERED` / `REGISTRATION_EQUIVOCATION` / `TARGET_NOT_REGISTERED` / `RELEASE_FINAL_UNVERIFIED` / `ARTIFACT_SOURCE_REJECTED` / `VERIFICATION_RECORDS_BELOW_MINIMUM` |
| **AP-5r** | **Restrictor revocation** (revision 6; CR5-B-01). A REJECTED attestation, and a conflicting reproduction (AP-6), stops restricting only when a verified `registration-revocation` at the registration threshold names it (`30` R-REG-11). A `revocations` entry of the selected TSS, or a `revocation`-key statement, removes the statement from positive counts only. | as AP-5, AP-6 |
| AP-6 | **Reproduction quorum:** at least max(2, OP-9 quorum) distinct unrevoked `reproducer` keys. Each is on a one-signature statement naming the measured digest, the registered source and input manifest, **an environment registered for the target**, the target and the TBM digest. Under OP-16 (b), the keys come from at least two supplier classes (`33` R-BENV-5). No valid reproduction of another digest exists for the same release and target (subject to AP-5r). Under OP-9 (d), the digest equals the registered digest. | `REPRODUCTION_QUORUM_NOT_MET` / `REPRODUCTION_CONFLICT` / `ENVIRONMENT_DIVERSITY_NOT_MET` / `BINARY_NOT_REGISTERED` |
| AP-7 | **Publication:** the selected TSS lists the digest in `published_binaries[]`. | `BINARY_NOT_PUBLISHED` |
| AP-8 | **TBM:** parsed from the bytes without execution; `build: release`; lineage, source and inputs equal the registration; every component resolves to a verified statement with an identical digest; `embedded_release` equals the registered final and kernel tree digest. Running mode only: root version, policy version and state sequence ≥ the accepted-TBM high-water of this verifier trust store. | `BINARY_T0_UNVERIFIED` / `BINARY_T0_ROLLBACK` |
| AP-9 | Accept. Show the selected state's `issued_at` and age, and in bootstrap mode the first-contact sources used. Never show `current`. | — |
| AP-10 | Install from the measured buffer and write the admission record in the store (`31` R-ADM-6, R-ADM-7′, R-ADM-13). Record the accepted TBM components in `accepted_tbm`. | — |

**First-run self-check (CR4-B-08).** Unchanged: a binary records its TBM into `accepted_tbm` only if it is `build: release`
and its TBM resolves.

**Evidence.**
- Running mode: `evidence/r6/P4r6-conformance-oracle.json`. The 28 revision-6 scenarios hold. The 65 P4r5 scenarios hold under
  revision-6 rules with unchanged expectations. No expected-`ACCEPTED` attack row exists.
- Bootstrap mode: `evidence/r6/FA6-first-admission.json`.
- Shared vectors R1–R5: identical codes in both (FA6 S4).
- Mutation sensitivity: `evidence/r6/DA03r6-oracle-regression-sensitivity.json`.

## 6. Non-circular chain

```text
first-contact sources (OP-13) ── first-contact code ─► first-contact manifest {lineage, state epoch, admitter digests} ─┐
registration authority (root threshold or root-granted quorum ≥ 2) ─ selects source, inputs, environments, content, final
  ← first-hand verification records for exactly the candidate and kernel (OP-8), upstream checksum checks,
    first-hand environment reproductions, custodians' own source identity and kernel derivation (and, OP-9 (d), own reproduction)
reproducers (≥ q, first-person, inputs by digest, environments re-assembled) ─ observe bytes ─► confirm first-hand to the publisher
trust-state publisher (E7 restrictors on registrations) ─ publishes registration and one quorum digest per release and target ─► TSS m
first binary on a machine:  operator FC-1…FC-3 selects gov-admit ─ AP over measured bytes (FC-4…FC-8) ─► install from buffer
later binaries:              admitted gov N ─ AP with anchors and a currency proof naming TSS m ─► binary N+1
```
- Nothing in a binary authenticates that binary; no value the candidate prints is an input.
- No selector's authority comes from a signature over a fact its signer did not establish.
- The evaluator is never the candidate, including on first install, in CI image builds and in Phase 4.
- The one remainder that no mechanism removes is the first-contact root, stated exactly (`32` §6) and chosen by the owner
  (OP-13).

## 7. What each compromise yields (computed; `evidence/r6/CS6-derivation-calculator.json`)

Every "yes" row below is a minimal set of the calculator for the victim classes named. Every "no" row has no minimal set that
contains only the named capabilities. The sets themselves are in the generated blocks of `30` §10 (bytes, source, toolchain),
`33` §6 (environment), `34` §4 (content) and `32` §6 (first admission).

| Compromised | Accepted malicious production binary or content? | Why |
|---|---|---|
| one `release-final` key, or `release-candidate` + `release-final` (or the OP-4 "no" everyday key), with pipeline | **no** (bytes or content) | no registration names the final; content derived first-hand (R-CON-1); E7 counts attestations only for the registered candidate and kernel (INV-RF; P4r6 section G) |
| one `verification-attestation` key + candidate + final keys + pipeline | no | verification selects nothing (INV-SRC, INV-CONTENT) |
| one reproducer key, with or without pipeline and trust-state key | no; availability only | quorum ≥ 2; conflict (AV-S1), removed only by registration revocation (INV-ONE; FA6 S5) |
| a trust-state key listing honest conflicting reproductions or a REJECTED attestation in `revocations` | no change to any refusal | AP-5r (P4r6 `R6-AP5r_*`; FA6 S5; CS6 mutation `V_REVOCATION_AUTHORITY`) |
| the pipeline supplying the build image or environment record | no | environment established by first-hand reproduction from upstream-checked components (INV-ENV-PIPELINE; ENV6 E1) |
| q reproducer processes | yes, on every victim class | TB-S1; OP-9 |
| q reproducer keys + trust-state key + the victim's currency input (in-gate sources, witness keys, or the pin provisioner) | yes on P2, WR and CIR victims; never on P1 | TB-S1 (`30` §10) |
| OP-8 verification processes + pipeline | yes (source or content) | TB-4′; OP-8 |
| registration custodians at threshold + OP-8 verification compromises | yes (source, inputs, environment or content) | OP-2 (a): root threshold (A8); OP-2 (b): the delegated quorum's consequence |
| a compromised upstream toolchain release, or environment component supplier | yes under OP-10 (a) / OP-16 (a) | TA-12, TA-12′; OP-10, OP-16 |
| the first-contact sources of the OP-13 answer (no key) | yes, on first admission only | the first-contact root (`32` §6; FA6 S3 executed equals computed) |
| a poisoned input mirror | no | inputs by digest (INV-MIRROR) |
| a genuine older binary presented as an upgrade | no | `BINARY_T0_ROLLBACK`; `min_binary_version` (a TBM without a version fails closed when the floor is set) |

The claims hold over the victim classes the calculator enumerates: P1, P2 (one or two sources), witness-reliant runners,
CI-record runners, and first admission under each OP-13 answer (CR5-B-10). They hold under every OP-2, OP-4, OP-8, OP-9, OP-10,
OP-13 and OP-16 answer the calculator enumerates. No single key of any purpose, and no key together with pipeline or
transport input, yields an accepted production binary or effective content (INV-ONE, INV-RF: 0 failures).

## 8. What is protected (HO-0001 §3.3 list)

| Asset | Protection |
|---|---|
| The binary | AP-1, AP-5…AP-7 over measured bytes; installation from the buffer; GB-4′ for C3 |
| Its source, build inputs and build environment | the registration (rank 1 or 2); first-hand verification records for exactly the candidate; upstream checksum checks; first-hand environment reproduction (`33`) |
| Its constitutional content | first-hand derivation (`34` R-CON-1); E7 restrictors (R-CON-3) |
| Compiled trust roots, minimum floors, trust-policy identity, historical-release set, trust state and bootstrap rules | files of the registered source, compiled in a registered environment, covered by the reproduction quorum; AP-8 resolution; accepted-TBM high-water |
| The first TCB on a machine | the first-contact root of the owner's OP-13 answer (`32`), stated with its computed minimum |

## 9. Ceremony and custodial rules

`30` §5 (R-REG-3), §6, §7, §8; `33` §4; `34` §3. The trust-state publisher runs AP-4…AP-8 before referencing any digest and
E7's restrictors before referencing a registration (R-PUB-1′).

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-1′ | A malicious binary run directly, outside admission | GB rules bind genuine binaries (`31` §9) | FA6 S1 |
| AD-1′ | The first-contact root | `32` §6 | FA6 S3 |
| TB-S1, TB-S2, TB-S2′, TB-S3, TB-4, TB-4′, AV-S1 | reproducer quorum; upstream toolchain; upstream environment; common custody; route I; verification processes; conflict denial | `30` §12 | CS6; P4r6; ENV6 |
| TB-L4 | Stateless runners lack an accepted-TBM high-water | `min_binary_version` (a TBM without a version fails closed when the floor is set) and revocations only | RT-116 |
