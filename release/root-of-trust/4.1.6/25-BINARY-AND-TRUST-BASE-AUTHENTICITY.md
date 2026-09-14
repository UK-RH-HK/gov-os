# Output 25 — Binary, built-source and trust-base authenticity: admission-predicate/1 (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** amends admission-predicate/1 for CP-1 (`35`) and review r6:
> - AP-1…AP-3 take lineage and evaluator from the First-Contact Authority record at root threshold and the state from both
>   sources' state codes, at most 24 hours old (`32` FC-4′…FC-10; BC6-1, BC6-2);
> - AP-3 in bootstrap mode applies the stores' floors (`31` AP-R1…AP-R6; RV6-H2, RV6-L5);
> - AP-5 requires two verification records from distinct keys, executions and reports that name the registered environments
>   (OP-8; `33` R-BENV-8);
> - AP-6 requires the 2-of-3 reproducer quorum from two independent supplier classes and two independent toolchain lineages,
>   and the registered binary digest (OP-9 (b) + (d), OP-10 (b), OP-16 (b); BC6-3);
> - AP-SEC applies the computed security minimum (OP-11 (b));
> - the Trust Base Manifest names `profile_id`; §7 is restated from CS7 for CP-1 only.
> Registration and reproduction: `30`. First admission: `31`, `32`. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

The `gov` binary carries T0; it is the trusted computing base. Revision 5 changed **who selects**: the registration selects source
and inputs, a first-hand reproduction quorum establishes the bytes, and an evaluator other than the candidate decides. Review r5
and review r6 found selectors still unassigned: the build environment (RV5-H2, then its manifest author, RV6-H3), constitutional
content derived by CI (RV5-H3), and first-contact values chosen by a channel page, a composer, a designation or a submitter
(RV5-H1, RV6-H1), without a bound on their age (RV6-H2). Revision 7 assigns each of them within CP-1.

## 2. Mechanisms (HO-0001 §3.3)

| Mechanism | CP-1 position |
|---|---|
| Threshold root signature | the First-Contact Authority record and the Trust Policy at root threshold (2 of 3); never a release registration (EX-09) |
| Delegated registration | 2-of-3 single-purpose registration keys (OP-2 (b)); custodians' own reproduction (OP-9 (d)) |
| Separate binary attestation | first-person reproduction statements, quorum 2 of 3 reproducer roles, under derived environments of two independent supplier classes and two independent toolchain lineages (`30` §7, `33`) |
| Certification binding | not a selector; negatives only |
| Reproducible-build and provenance evidence | **mandatory**: source identity v2, input manifest v3, environment lock in source, derived environment manifests, normative build profile with static self-contained linking (`30` §4, `33`, CC-4) |
| Compiled trust-state digest; binary trust-policy digest | kept in the TBM as restrictors (AP-8), never selectors |
| Multi-signature | exact CP-1 shapes (`05` §3) |
| Platform or distribution code signing | not a root and not a selector (EX-05) |

## 3. Purposes

As `05` §1 and `30` §3: `release-registration` (with `registration-revocation`), `reproducer` (with `environment-reproduction`),
`verification-attestation` v5 and `release-final` as restrictors; `first-contact-authority` on the root keys.

## 4. Trust Base Manifest v4

Schema: `schemas/trust-base-manifest.schema.json` 4.0.0.

| Field | Content |
|---|---|
| `binary` | name, version (required; AP-4), target, `build` (`release` or `development`), `source {release_commit, git_tree, content_digest}`, `toolchain`, `inputs_manifest_digest` |
| `lineage` | `trust_root_id` |
| `root_chain[]` | `{version, statement_digest}` |
| `trust_policy` | `{policy_version, statement_digest}` |
| `trust_state` | `{sequence, statement_digest}` of a TSS that exists before the build |
| `embedded_release` | `{final_statement_digest, kernel_tree_digest}` |
| `compiled_rules` | `floor_schema_version` 3; purpose-table digest; statement-schema-set digest; decision-register digest (`29` R-SEL-1); format readers; command-register digest; **`profile_id`** `governance-os.rot1/CP-1` |

The TBM cannot name the registration digest (the registration names the binary). Nothing is hash-cyclic.

## 5. admission-predicate/1 (normative; both executors, `31` §3)

Inputs: the candidate's bytes (read once, never executed), the statements held (any source), the target, and the selector of
state. In **running mode** that selector is the machine's anchors and a currency proof. In **bootstrap mode** (`gov-admit`) it
is the two trust codes and two state codes read from both sources, with the stores' floors (`32`, `31` §4.1).

| Step | Check | Refusal |
|---|---|---|
| AP-0 | The evaluator is not the candidate; no excluded input is offered (platform signature, witness, package submitter); the path class is `workstation` or `ci-image`. | `SELF_EVALUATION_REFUSED` / `PROFILE_MODE_EXCLUDED` |
| AP-1 | Measure: SHA-256 of the buffer read once. **Bootstrap:** two identical trust codes and two identical state codes (`32` FC-4′). | `FIRST_CONTACT_SOURCES_BELOW_QUORUM` / `FIRST_CONTACT_DISAGREEMENT` |
| AP-2 | Root chain from root v1 by dual-threshold links; the Fact Threshold Check and CP-1 shapes on every version. **Lineage:** the compiled lineage, in both modes; bootstrap also checks the FCA's lineage and the trust code's prefix (FC-6, FC-7′). Bundle order never matters. | `ROOT_CHAIN_INVALID` / `PROFILE_NONCONFORMANT` / `FIRST_CONTACT_LINEAGE_NOT_COMPILED` / `ROOT_VERSION_INVALID` |
| AP-3 | **Select the Trust State.** **Bootstrap:** the FCA whose digest the trust code names, verified at root threshold (FC-5′); the certified target and the evaluator binding (FC-8′); the Trust State whose digest the state code names, verified at 2 of 3 trust-state keys, referencing that FCA (FC-10), at most 24 hours old (FC-9); its root and Trust Policy verify and conform to CP-1; the stores' floors AP-R1…AP-R4 hold. **Running:** the effective TSS by inclusion anchors within validity (`24` §3.4, §4.3), with a currency proof of at most 24 hours that **names that TSS** (`24` §4.4). | `FIRST_CONTACT_AUTHORITY_UNVERIFIED` / `FIRST_CONTACT_AUTHORITY_MISMATCH` / `TARGET_NOT_CERTIFIED` / `ADMITTER_NOT_LISTED` / `ADMITTER_REVOKED` / `STATE_NOT_HELD` / `TRUST_STATE_UNVERIFIED` / `FIRST_CONTACT_STATE_TOO_OLD` / `PROFILE_NONCONFORMANT:trust_policy` / `READMISSION_*_BELOW_HELD` / `TRUST_STATE_UNANCHORED` / `TRUST_ANCHOR_EXPIRED` / `…_BELOW_ANCHOR` / `…_CURRENCY_UNPROVEN` |
| AP-4 | **Negatives** of the selected state (its `revocations` and the revocation statements it lists, at the revocation or root threshold) and, in bootstrap mode, of the stores (AP-R4): the binary digest, its registration, the registered final and candidate, and the admitter are not revoked. Revoked reproductions, attestations and keys count for nothing below. **Binary floor:** when the Trust Policy sets `eligibility.min_binary_version`, the TBM's version MUST be present and at least it. | `BINARY_REVOKED` / `BINARY_REVOKED_IN_HELD_STATE` / `ADMITTER_REVOKED_IN_HELD_STATE` / `BINARY_BELOW_TRUST_POLICY` |
| AP-5 | **Registration and verification:** exactly one verified 2-of-3 `release-registration` for the release id, referenced by the selected TSS, not revoked; the target registered; the registered final held and verifying at threshold 2, with the registered source, promoted from the registered candidate and carrying the registered kernel tree digest; no held REJECTED attestation for the registered candidate (subject to AP-5r); **two** ACCEPTED attestations listed by the registration, from distinct keys, distinct `verifier_execution_id` and distinct report digests, each naming exactly the registered candidate, source, inputs and kernel tree digest and every registered environment of the target. | `RELEASE_UNREGISTERED` / `REGISTRATION_EQUIVOCATION` / `TARGET_NOT_REGISTERED` / `RELEASE_FINAL_UNVERIFIED` / `ARTIFACT_SOURCE_REJECTED` / `VERIFICATION_RECORDS_BELOW_MINIMUM` |
| **AP-5r** | **Restrictor revocation.** A REJECTED attestation, and a conflicting reproduction (AP-6), stops restricting only when a verified `registration-revocation` at the registration threshold names it (`30` R-REG-11). A trust-state or revocation-key entry removes the statement from positive counts only. | as AP-5, AP-6 |
| **AP-SEC** | **Computed security minimum** (OP-11 (b); `19` E3′). The release's sequence is at least the maximum of the Trust Policy's `min_release_sequence`, the sequence of every registration the selected TSS references with `security_relevant_change`, and in bootstrap mode the held minimum (AP-R5). No grace period exists (EX-07). | `RELEASE_BELOW_SECURITY_MINIMUM` |
| AP-6 | **Reproduction quorum:** at least 2 distinct unrevoked `reproducer` keys, each on a one-signature statement naming the measured digest, the registered source and input manifest, an environment and a toolchain registered for the target, the target and the TBM digest; among those, environments of at least two supplier classes independent by provenance and toolchains of at least two lineages independent by provenance (`33` R-BENV-5″, R-BENV-6″); no valid reproduction of another digest for the same release and target (subject to AP-5r); the digest equals the registered `binary_digests[target]`. | `REPRODUCTION_QUORUM_NOT_MET` / `ENVIRONMENT_DIVERSITY_NOT_MET` / `TOOLCHAIN_DIVERSITY_NOT_MET` / `REPRODUCTION_CONFLICT` / `BINARY_NOT_REGISTERED` |
| AP-7 | **Publication:** the selected TSS lists the digest in `published_binaries[]`. | `BINARY_NOT_PUBLISHED` |
| AP-8 | **TBM:** parsed from the bytes without execution; `build: release`; `profile_id` CP-1; lineage, source and inputs equal the registration; every component resolves to a verified statement with an identical digest; `embedded_release` equals the registered final and kernel tree digest. Root version, policy version and state sequence ≥ the accepted-TBM high-water of the stores (running mode; bootstrap AP-R6). | `BINARY_T0_UNVERIFIED` / `BINARY_T0_ROLLBACK` |
| AP-9 | Accept. Show the selected state's `issued_at` and age, the OP-5 age warning when due, and in bootstrap mode both sources and the FCA sequence. Never show `current`. | — |
| AP-10 | Install from the measured buffer and write the admission record in the protected store (`31` R-ADM-6, R-ADM-7″, R-ADM-13). Record the accepted TBM components. | — |

**First-run self-check.** Unchanged: a binary records its TBM into `accepted_tbm` only if it is `build: release` and its TBM
resolves.

**Evidence.**
- Bootstrap mode: `evidence/r7/FA7-first-contact-authority.json` (S4 R0–R16, S5, S7) and `evidence/r7/CUR7-first-contact-currency.json`.
- Running mode: `evidence/r6/P4r6-conformance-oracle.json` (retained for the rules that did not change) and ADM7 / BA11r7 for the
  CP-1 decision rule.
- Profile conformance: `evidence/r7/PROF7-profile-conformance.json`.

## 6. Non-circular chain

```text
root ceremony (2 of 3) ─ First-Contact Authority record {lineage, admitter per certified target, two sources, procedure}
  ← admitter registered (2 of 3), reproduced (2 of 3 roles), verified by two records
two sources (separate custody) ─ verify FCA and Trust State first-hand ─► trust code, state code (byte-identical)
registration authority (2 of 3 delegated) ─ selects source, inputs, environment lock, environments, toolchains, content, final,
  binary digests ← two first-hand verification records, pinned supplier and toolchain registry, derived environment
    manifests with agreeing environment reproductions, custodians' own source identity, content and reproduction
reproducers (2 of 3 roles, first-person, inputs by digest, two supplier classes, two toolchain lineages) ─► first-hand confirmation
trust-state keys (2 of 3) ─ publish registration and one digest per release and target ─► TSS m
first binary on a machine:  operator FC-1′…FC-3′ selects gov-admit ─ AP over measured bytes (FC-4′…FC-10, AP-R) ─► install
later binaries:              admitted gov N ─ AP with anchors and a currency proof ≤ 24 h naming TSS m ─► binary N+1
```
- Nothing in a binary authenticates that binary; no value the candidate prints is an input.
- No selector's authority comes from a signature over a fact its signer did not establish.
- The evaluator is never the candidate, including on first install, in CI image builds and in Phase 4.
- The one remainder that no mechanism removes is the first-contact root, stated exactly (`32` §9).

## 7. What each compromise yields (computed; `evidence/r7/CS7-derivation-calculator.json`)

Every "yes" row is a minimal set of CS7 for the victim classes named; every "no" row has no minimal set holding only the named
capabilities. The sets are the generated blocks of `30` §10, `33` §6, `34` §4 and `32` §8–§9.

| Compromised | Accepted malicious production binary or content? | Why |
|---|---|---|
| one `release-final` key, or the `release-candidate` key and one `release-final` key, with pipeline | **no** | release-final threshold 2 (KS-15); no registration names the final; content derived first-hand (INV-RF) |
| verification keys, candidate and final keys, and pipeline, without the registration threshold | no | verification selects nothing (INV-SRC, INV-CONTENT) |
| one reproducer key, with or without pipeline and one trust-state key | no; availability only | quorum 2; conflict removed only by registration revocation (INV-ONE; FA7 S5) |
| trust-state keys listing honest conflicting reproductions or a REJECTED attestation in `revocations` | no change to any refusal | AP-5r (FA7 S5 `trust_state_revocation_of_the_conflict_does_not_clear_it`) |
| the pipeline supplying an environment manifest or image record | no | manifests are derived; authority needs agreeing reproductions and the registration (INV7-ENV-PIPELINE; ENV7 A07a/b/c) |
| one supplier class, or one toolchain lineage, or a label over either | no | independence by provenance (INV7-ENV-B, INV7-TC; ENV7 A08, T2) |
| the trust-state publication process, a carrier, or an unadmitted binary at first contact | no | nothing they compose selects (INV7-NO-COMPOSER, INV7-NO-CARRIER; FA7 S2 P, S2 D) |
| the registration custodians at threshold with the three reproducer processes | yes, on every victim class | TB-S1 with OP-9 (d) (CP-BYTES) |
| the registration, reproducer and trust-state thresholds of keys with the publication process or a first-contact root set | yes on the victim classes CP-BYTES and CP-FC-KEY-THEFT list; never on P1 | TB-S1 key theft |
| two verification processes with pipeline input | yes (source or content) | TB-4′ (CP-SRC, CP-CONTENT) |
| the registration custodians at threshold with two verification keys and pipeline input, or with the release-final threshold and the candidate key | yes (source, inputs or content) | the delegated quorum's consequence (CP-SRC, CP-INPUTS, CP-CONTENT) |
| both toolchain lineages or the compiler source; both supplier classes or hidden common provenance | yes | TA-12″, TB-S2″ (CP-TOOLCHAIN, CP-ENV) |
| a first-contact root set (no key) | yes, on first admission only | `32` §9; FA7 S3 executed equals computed |
| a revocation within the 24 hours before admission | a revoked binary admitted on a machine whose store lacks the revocation | CUR-R1 (CP-REVOKED) |
| a poisoned input mirror | no | inputs by digest (INV-MIRROR) |
| a genuine older binary presented as an upgrade or a re-admission | no | `BINARY_T0_ROLLBACK`; security minimum; `min_binary_version` |

No single key of any purpose, and no key together with pipeline, transport or publication input, yields an accepted production
binary or effective content (INV-ONE, INV-RF: 0 failures; BA12r7).

## 8. What is protected (HO-0001 §3.3 list)

| Asset | Protection |
|---|---|
| The binary | AP-1, AP-5…AP-8 over measured bytes; installation from the buffer; GB-4′ for C3 |
| Its source, build inputs, build environment and toolchain | the 2-of-3 registration; two first-hand verification records; pinned supplier and toolchain registry; derived environment manifests; two supplier classes and two toolchain lineages |
| Its constitutional content | first-hand derivation (`34` R-CON-1); E7 restrictors (R-CON-3) |
| Compiled trust roots, floors, trust-policy identity, historical-release set, trust state, profile and bootstrap rules | files of the registered source, compiled in registered environments, covered by the reproduction quorum; AP-8 resolution; accepted-TBM high-water |
| The first TCB on a machine | the First-Contact Authority record at root threshold and the first-contact root of `32`, stated with its computed minimum |

## 9. Ceremony and custodial rules

`30` §5 (R-REG-3), §6, §7, §8; `32` §3, §5; `33` §5; `34` §3. The trust-state publisher runs AP-4…AP-8 before referencing any
digest and E7's restrictors before referencing a registration (R-PUB-1′).

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-1′ | A malicious binary run directly, outside admission | GB rules bind genuine binaries (`31` §9) | FA7 S1 |
| AD-1″ | The first-contact root | `32` §9 | FA7 S3 |
| CUR-R1 | A revocation within the 24-hour admission window | `32` §8 | CUR7 W |
| TB-S1, TB-S2″, TB-S3, TB-4, TB-4′, AV-S1 | reproducer quorum; both toolchain lineages or both supplier classes; common custody; route I; verification processes; conflict denial | `30` §12, `33` §8 | CS7; FA7; ENV7 |
| TB-L4 | A machine without stores lacks an accepted-TBM high-water | `min_binary_version` (a TBM without a version fails closed when the floor is set), the security minimum and revocations | RT-116 |
