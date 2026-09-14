# Output 25 — Binary, built-source and trust-base authenticity: admission-predicate/1

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Rewritten in revision 5 for blocking classes **BC4-1** (RV4-H1) and **BC4-2** (RV4-H2), under rule FD-1 (`29`). Revision
> 4's acceptance by `release-artifact` ×2, one build attestation and one attested source is **superseded**; its evidence
> (`evidence/VA4-*`, the P4r4 binary scenarios) is kept as history and re-expressed under these rules in
> `evidence/r5/P4r5-conformance-oracle.json`. Registration and reproduction: `30`. First admission: `31`. Normative
> keywords: MUST, MUST NOT, SHOULD.

## 1. The class

The `gov` binary carries T0; it is the trusted computing base. Revision 3 required that the authentication of a binary be
at least as strong as the authority the binary carries. Revisions 3 and 4 tried to meet that by adding signers:
- revision 3 added `release-artifact` ×2, a build attestation and a trust-state reference, but every signer checked the
  bytes against a commit that threshold-1 `release-final` named (RV3-H3);
- revision 4 took the source from one ACCEPTED verification attestation and added custodial pre-check stages, but the
  custodians' threshold-2 statement asserted nothing they established, so one `build-attestation` key plus pipeline input
  (or one `verification-attestation` key) yielded an accepted malicious binary (RV4-H1), and the first binary on a machine
  was accepted outside the rules altogether (RV4-H2).

**Revision 5 changes who selects, not how many sign** (`29` §6): the registration authority selects source, inputs and
content; a first-hand reproduction quorum establishes the bytes; the selected Trust State selects publication and
negatives; an evaluator other than the candidate decides, over bytes it measured.

## 2. Options evaluated (HO-0001 §3.3)

| Option | Revision 5 position |
|---|---|
| Threshold root signature | the release registration at root threshold (OP-2 (a)), or a root-granted quorum ≥ 2 (OP-2 (b)); OP-9 (d) adds the custodians' own reproduction |
| Separate binary or root-bundle attestation | first-person reproduction statements at a compiled quorum ≥ 2 (`30` §7); `release-artifact` withdrawn |
| Certification binding | not a selector; certification establishes neither build nor source; not required |
| Reproducible-build or provenance evidence | **mandatory**: canonical content digest, digest-addressed input manifest, normative remapping profile (`30` §4, IR-REP-1…3) |
| Compiled trust-state digest; binary trust-policy digest | kept in the TBM as restrictors (AP-8), never selectors |
| Multi-signature | quorums across first-hand statements; root threshold; the Fact Threshold Check enforces the minima (`05` §3) |

## 3. Purposes

`release-registration` and `reproducer` are added; `release-artifact` and `build-attestation` are withdrawn;
`verification-attestation` and `release-final` become restrictors (`30` §3, `05` §1).

## 4. Trust Base Manifest v3

Schema: `schemas/trust-base-manifest.schema.json`, `x-schema-version` 3.0.0.

| Field | Content |
|---|---|
| `binary` | name, version, target, `trust_profile`, `build` (`release` or `development`), **`source {release_commit, content_digest}`**, **`inputs_manifest_digest`** |
| `lineage` | `trust_root_id` |
| `root_chain[]` | `{version, statement_digest}` |
| `trust_policy` | `{policy_version, statement_digest}` |
| `trust_state` | `{sequence, statement_digest}` of a TSS that exists before the build |
| `embedded_release` | `{final_statement_digest, kernel_tree_digest}` of the final whose kernel is embedded; its registration is checked at AP-8 |
| `compiled_rules` | `floor_schema_version` 3; `floor-ops/3`; purpose-table digest (twelve purposes of revision 5); statement-schema-set digest; decision-register digest (`29` R-SEL-1); format readers; command-register digest |

The TBM cannot name the registration digest: under OP-9 (d) the registration names the binary digest, so it exists after the
build. Nothing is hash-cyclic.

## 5. admission-predicate/1 (normative; both executors, `31` §3)

Inputs: the candidate's bytes (read once, never executed), the statements held (any source), the target, and the selector of
state — **running mode:** the machine's anchors and a currency proof; **bootstrap mode (`gov-admit`):** the fingerprint(s)
typed now from the independent channels.

| Step | Check | Refusal |
|---|---|---|
| AP-0 | The evaluator is not the candidate (digest comparison). | `SELF_EVALUATION_REFUSED` |
| AP-1 | Measure: SHA-256 of the buffer read once. Bootstrap: all typed fingerprints equal. | `CHANNEL_DISAGREEMENT` |
| AP-2 | Root chain from root v1 by dual-threshold links; the Fact Threshold Check and KS-1…KS-13 on every version. Lineage: bootstrap from the typed fingerprint's epoch; running from the compiled lineage. | `ROOT_CHAIN_INVALID` / `ROOT_VERSION_INVALID` |
| AP-3 | **Select the Trust State.** Bootstrap: the verified TSS whose epoch fingerprint equals the typed value, with its root and Trust Policy verified; then `bootstrap.channel_quorum` ≤ number of agreeing channels typed. Running: the effective TSS by inclusion anchors (`24` §3.4) with a currency proof that **names that TSS** (P1 pin or confirmation naming it within the window, P2 typed fingerprint, P3 witnesses at threshold; `24` §4.4). | `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` / `CHANNEL_QUORUM_NOT_MET` / `TRUST_STATE_UNANCHORED` / `…_BELOW_ANCHOR` / `…_REGRESSION` / `…_CURRENCY_UNPROVEN` |
| AP-4 | **Negatives** of the selected state: the binary digest, its release, the registration, the registered final and candidate are not revoked; revoked reproductions, attestations and keys count for nothing below; binary version ≥ `min_binary_version`. | `BINARY_REVOKED` / `BINARY_BELOW_TRUST_POLICY` |
| AP-5 | **Registration:** exactly one verified `release-registration` for the release id (else `REGISTRATION_EQUIVOCATION`), at the registration threshold, referenced by the selected TSS; the target registered; the registered final statement held, verifying under `release-final`, with the registered source and candidate; no held REJECTED attestation for the registered candidate; ≥ OP-8 ACCEPTED attestations by distinct keys that the registration lists, with the registered source and inputs. | `RELEASE_UNREGISTERED` / `REGISTRATION_EQUIVOCATION` / `TARGET_NOT_REGISTERED` / `RELEASE_FINAL_UNVERIFIED` / `ARTIFACT_SOURCE_REJECTED` / `VERIFICATION_RECORDS_BELOW_MINIMUM` |
| AP-6 | **Reproduction quorum:** ≥ max(2, OP-9 quorum) distinct unrevoked `reproducer` keys, each on a one-signature statement naming the measured digest, the registered source and input manifest, the target and the TBM digest; no valid reproduction of another digest for the same release and target; under OP-9 (d) the digest equals the registered digest. | `REPRODUCTION_QUORUM_NOT_MET` / `REPRODUCTION_CONFLICT` / `BINARY_NOT_REGISTERED` |
| AP-7 | **Publication:** the selected TSS lists the digest in `published_binaries[]`. | `BINARY_NOT_PUBLISHED` |
| AP-8 | **TBM:** parsed from the bytes without execution; `build: release`; lineage, source and inputs equal the registration; every component resolves to a verified statement with an identical digest; `embedded_release` equals the registered final and kernel tree digest. Running mode only: root version, policy version and state sequence ≥ the **accepted-TBM high-water** of this verifier trust store. | `BINARY_T0_UNVERIFIED` / `BINARY_T0_ROLLBACK` |
| AP-9 | Accept; show the selected state's `issued_at` and age, never `current`. | — |
| AP-10 | Install from the measured buffer and write the admission record (`31` R-ADM-6, R-ADM-7); record the accepted TBM components in `accepted_tbm`. | — |

**First-run self-check (CR4-B-08).** A binary records its TBM into `accepted_tbm` only if it is `build: release` and its TBM
resolves (AP-8) against held verified statements; development and test builds never record. A binary whose TBM is below
the high-water refuses trusted operations (`BINARY_T0_ROLLBACK`). A root-signed TPS field `bootstrap.accepted_tbm_reset`
resets the high-water. On machines without a verifier trust store the high-water is absent: an older, unrevoked genuine
binary is refused there only by `min_binary_version` and revocations (RV4-L4 scope).

**Evidence.** Running mode: `evidence/r5/P4r5-conformance-oracle.json` (65 revision-5 scenarios and 42 retained P4r4
scenarios hold; no expected-`ACCEPTED` attack row). Bootstrap mode: `evidence/r5/FA5-first-admission.json`. Mutation
sensitivity: `evidence/r5/DA03r5-oracle-regression-sensitivity.json`.

## 6. Non-circular chain

```text
independent channels ── state fingerprint (typed now), admitter digest ─┐
registration authority (root threshold or root-granted quorum ≥ 2) ─ selects source, input manifest, content, final, targets
  ← first-hand verification records (OP-8), upstream checksum checks, custodians' own content digest (and, OP-9 (d), own reproduction)
reproducers (≥ q, first-person, inputs by digest) ─ observe bytes ─► confirm first-hand to the publisher
trust-state publisher ─ publishes registration and exactly one quorum digest per release and target ─► TSS m
first binary on a machine:  gov-admit (registered, reproduced, digest compared) ─ AP over measured bytes ─► install from buffer
later binaries:              admitted gov N ─ AP with anchors and a currency proof naming TSS m ─► binary N+1
```
- Nothing in a binary authenticates that binary; no value the candidate prints is an input.
- No selector's authority comes from a signature over a fact its signer did not establish.
- The evaluator is never the candidate, including on first install, in CI image builds and in Phase 4.

## 7. What each compromise yields (computed; `evidence/r5/CS5-tcb-capability-sets.json`, `30` §10)

| Compromised | Accepted malicious production binary? | Why |
|---|---|---|
| one `release-final` key (+ pipeline) — RV3-B-A08 | no | no registration names the final (`RELEASE_UNREGISTERED`); P4r5 VA5-01 |
| `release-candidate` + `release-final` (OP-4 "no" everyday key) + pipeline — RV3-D-A03 | no | as above; P4r5 VA5-05, VA5-06 |
| one `verification-attestation` key + candidate + final keys + pipeline — revision-4 route S | no | verification selects nothing; P4r5 VA5-07…VA5-10; CS5 INV-SRC-KEYS |
| `release-artifact` ×2 + `build-attestation` + `trust-state` — revision-4 route B | no | withdrawn purposes count for nothing; no reproduction quorum; P4r5 VA5-11…VA5-13 |
| one `build-attestation`/`reproducer` key + pipeline (+ trust-state key) — RV4-B-A01 | no | quorum ≥ 2 first-hand; P4r5 VA5-B-prime; CS5 INV-ONE |
| one reproducer key | no (availability only) | `REPRODUCTION_CONFLICT` (AV-S1) |
| q reproducer processes | yes, everywhere | stated minimum TB-S1; raised by OP-9 (b)/(c)/(d) |
| q reproducer keys + trust-state key + the channel(s) the victim types (+ transport, or + registration keys) | yes, on P2 and first admission; never on P1 | stated minimum TB-S1 (`24` §4.4 revision 5 removes the trust-state key as a C3 selector on pinned machines) |
| OP-8 verification processes + pipeline | yes (source) | stated minimum TB-4′; raised by OP-8 |
| registration custodians at threshold + OP-8 verification keys | yes (source or inputs) | OP-2 (a): root threshold compromise (A8); OP-2 (b): the delegated quorum's stated consequence |
| a compromised upstream toolchain release | yes under OP-10 (a) | TA-12; OP-10 (b)/(c) |
| a poisoned input mirror | no | inputs by digest (control: {mirror} when fetched from a CI-named mirror) |
| a genuine older binary presented as an upgrade | no | `BINARY_T0_ROLLBACK` on machines with a high-water; `min_binary_version` elsewhere |
| a revoked genuine binary on an aged, expired or bypassed anchor (RV3-D-A15) | no | AP-3/AP-4; P4r5 `RV3-D-A15r5` |
| a revoked or remediated binary served to a first-install machine (RV4-B-A03), a moved tag (RV4-B-A04) | no | typed fingerprint selects state; negatives; quorum; candidate never executed; FA5 |

No single key of any purpose, and no key together with pipeline or transport input, yields an accepted production binary
under any owner answer (CS5: 0 invariant failures over 408 configurations).

## 8. What is protected (HO-0001 §3.3 list)

| Asset | Protection |
|---|---|
| The binary | AP-1, AP-5…AP-7 over measured bytes; installation from the buffer; GB-4 for C3 |
| Its source and build inputs | the registration (rank 1 or 2), first-hand verification records, upstream checksum checks |
| Compiled trust roots, minimum floors, trust-policy identity, historical-release set, trust state and bootstrap rules | files of the registered source, covered by the reproduction quorum; AP-8 resolution; accepted-TBM high-water |

## 9. Ceremony and custodial rules

`30` §5 (R-REG-3), §6, §7, §8 replace revision 4's custodial pre-check stages. The trust-state publisher runs AP-4…AP-8
before referencing any digest (R-PUB-1).

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-1′ | A malicious binary run directly, outside admission | GB rules bind genuine binaries; the procedure never runs candidates (`31` §9) | FA5 |
| TB-S1, TB-S2, TB-S3, TB-4, TB-4′, AV-S1 | reproducer quorum; upstream toolchain; common custody; route I; verification processes; conflict denial | `30` §12 | CS5; P4r5 |
| TB-L4 | Stateless runners lack an accepted-TBM high-water | `min_binary_version` and revocations only | RT-116 (stateless case) |
