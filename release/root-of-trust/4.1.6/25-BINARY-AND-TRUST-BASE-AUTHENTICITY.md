# Output 25 — Binary, built-source and trust-base authenticity

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 3 added this file for R2-H3. Revision 4 closes blocking class **BC-3** (review r3 RV3-H3: built-source
> legitimacy of production binaries) and carried RV3-M8, and meets HO-0001 §3.3. Normative keywords: MUST, MUST NOT,
> SHOULD.

## 1. The class

The `gov` binary carries T0. It is the trusted computing base. Revision 3 set the rule that **the authentication of a
binary MUST be at least as strong as the authority the binary carries**, and required:
- `release-artifact` at threshold ≥ 2;
- an independent build attestation;
- a trust-state reference;
- a Trust Base Manifest (TBM) that resolves to root- and trust-state-signed statements.

The review of revision 3 showed that every one of those checks answered one question: **are these bytes a build of the
named source?** None answered the other: **is the named source the source an independent verification accepted?** The
name was `release_commit` in the final release statement, signed by threshold-1 `release-final`.

- **The attack.** The thief promotes a final from a genuine attested candidate with an identical kernel tree, but names
  commit C′. Every downstream signer then faithfully processed C′ (RV3-B-A08).
- **Under OP-4 "no".** The everyday candidate key is that key (RV3-D-A03).
- **The mistaken equivalence.** *reproduced from the named commit ⇒ built from verified source.*

`28` §2.3 explains why the remainder survived.

**Revision 4 removes `release-final` from the choice of source.**
- **Where the source comes from.** The source identity of a production binary is taken from an ACCEPTED verification
  attestation of the candidate. The effective Trust State references that attestation.
- **The final names no source of its own.** It must carry the same source as its candidate (V8).
- **Who checks.** `verify-artifact` and every custodian check both.

## 2. Options evaluated (HO-0001 §3.3; CD3-3)

| Option | What it protects | Cost | Revision 4 |
|---|---|---|---|
| Threshold **root** signature on every binary | everything, if root custodians also check the verification record | offline root keys touched per binary per target | OP-2 option (iii), unchanged |
| Separate binary purpose `release-artifact` (threshold ≥ 2, disjoint) | no single key accepts a binary | a second custodian | **adopted** (unchanged) |
| Independent build attestation | bytes equal a build of the attested source and build inputs | an independent rebuilder | **adopted**; now bound to the attested source (A4a) |
| **Attested-source binding** | the TCB's source is one that an independent verification accepted, not one a release key names | none beyond existing statements | **adopted, architecture minimum** (§5.1) |
| **Root-registered production source** | the TCB's source needs the root threshold | one TPS registration per release that ships binaries (usually merged with the kernel registration of `23` CS-2) | **OP-2 option** (`21`) |
| **Verification-attestation threshold 2** | source legitimacy needs two independent verifiers | a second verifier | **OP-2 option** |
| Certification binding (`CERTIFIED_AS_OF` required for binaries) | adds the certification key | certification before binary announcement | evaluated, not required. Under mode A certification relaxes nothing, and the attestation binding already requires the verification result it certifies. Offered as an OP-2 option. |
| Compiled trust-state and trust-policy digests (TBM) | compiled roots, floors, surface, bootstrap and historical set | — | **adopted** (unchanged) |
| Multi-signature | no single-token compromise | custody | **adopted** |

## 3. Purposes (additions to `05`)

| Purpose | Signs | May assert | May never assert | Compiled constraints |
|---|---|---|---|---|
| `release-artifact` | `artifact-final.v2+json` | that listed binary digests, each bound to its TBM digest, are the production artefacts of a final release | release authenticity, certification, trust state, reproduction, source legitimacy | threshold ≥ 2; KS-9 |
| `build-attestation` | `build-attestation.v2+json` | that an independent rebuild of `source {release_commit, source_tree_digest, build_inputs_digest}` produced the binary digest and TBM digest | release or artefact authenticity; that the source is legitimate | KS-10 |
| `verification-attestation` | `verification-attestation.v2+json` | the independent verdict for one candidate digest **and the source it verified** (`source`), plus the negative statement a fresh verdict supersedes (`lifts_negative_statement_digest`, CR-01) | certification, authenticity | KS-4, KS-5, KS-6, KS-8 |

`artifact-candidate.v2+json` stays under `release-candidate`, for evaluation only. `release-final` signs no artefact
statement.

## 4. Trust Base Manifest (TBM)

Schema: `schemas/trust-base-manifest.schema.json`, `x-schema-version` 2.0.0.

| Field | Content |
|---|---|
| `binary` | name, version, target, `trust_profile`, `build`, toolchain id, and **`source {release_commit, source_tree_digest, build_inputs_digest}`**. `source_tree_digest` is the SHA-256 of `git archive` of the commit, so the binding does not rest on SHA-1. |
| `lineage` | `trust_root_id` |
| `root_chain[]` | `{version, statement_digest}` |
| `trust_policy` | `{policy_version, statement_digest}` |
| `trust_state` | `{sequence, statement_digest}`: a TSS that exists before the build |
| `embedded_release` | `{release_statement_digest, tree_digest}` of the final whose kernel is embedded |
| `compiled_rules` | `floor_schema_version` 3; operator vocabulary `floor-ops/3`; purpose-table digest (twelve purposes); statement-schema-set digest; format readers; command-register digest |

## 5. `gov trust verify-artifact <binary> <artifacts.dsse.json>` (normative)

| Step | Check | Failure code |
|---|---|---|
| A1 | Read the binary once; SHA-256. | `ARTIFACT_DIGEST_MISMATCH` |
| A2 | The artefact statement verifies under the effective root for `release-artifact` at threshold (≥ 2 distinct keys; KS-9). | `PURPOSE_NOT_GRANTED` / `THRESHOLD_NOT_MET` |
| A3 | Entry matches: digest, target, `trust_profile: production`, lineage, stage `final`; the named final release statement verifies under `release-final`. | `ARTIFACT_IDENTITY_MISMATCH` / `TRUST_ROOT_LINEAGE_MISMATCH` |
| **A4a** | At least the threshold of `build-attestation` statements (KS-10 keys) name the same artefact digest, the same TBM digest, and a `source` equal to the TBM `binary.source`. | `ARTIFACT_BUILD_UNATTESTED` |
| **A4b** | **Attested source** (§5.1): the final's candidate verifies; V8 holds with source equality; an ACCEPTED verification attestation of that candidate names the same `source`, and the effective TSS references it; no REJECTED attestation of that candidate is held; and, if OP-2 registered production sources, the source is in the effective TPS `eligibility.production_sources[]`. | `RELEASE_IDENTITY_MISMATCH(source)` / `ARTIFACT_SOURCE_UNVERIFIED` / `ARTIFACT_SOURCE_REJECTED` / `ARTIFACT_SOURCE_UNREGISTERED` |
| A5 | The effective admissible TSS references the artefact statement digest (`artifacts[]`). | `ARTIFACT_UNREFERENCED` |
| A6 | Every TBM component resolves to a verified statement with an identical digest; `embedded_release` is the final of A3. | `BINARY_T0_UNVERIFIED` |
| **A7** | TBM root version, policy version and state sequence are each ≥ the **accepted-TBM high-water** of this VTS (`24` §8). They are **not** compared with the TSS knowledge high-water (RV3-M8). | `BINARY_T0_ROLLBACK` |
| A8 | Neither the artefact, nor the final, nor its candidate is in the negative set (revocation; REJECTED/WITHDRAWN not lifted); binary version ≥ effective `min_binary_version`. | `ARTIFACT_REVOKED` / `BINARY_BELOW_TRUST_POLICY` |
| **A9** | Trust ingress: freshness `ANCHORED` or `WITNESSED`, and a **currency proof** (`24` §4.4). | `TRUST_STATE_UNANCHORED` / `TRUST_STATE_BELOW_ANCHOR` / `TRUST_STATE_CURRENCY_UNPROVEN` |
| A10 | Record the accepted TBM components in the VTS `accepted_tbm` high-water. | — |

**Self-check at first run.** A binary whose compiled TBM is below the VTS **accepted-TBM** high-water MUST refuse trusted
operations (`BINARY_T0_ROLLBACK`). A binary at or above it records its TBM. The self-check is never compared with the TSS
knowledge high-water. A binary compiled at TSS *n* therefore keeps working after TSS *n*+1 is published. Floors and
revocations of later statements still apply through the effective state.

**Realisable construction** (RV3-M8, D-A13).
1. The TBM names TSS *n*, which exists before the build.
2. The build attestation, artefact statement and verification attestation exist after the build.
3. They are referenced by TSS *m* > *n*.

Nothing is hash-cyclic. `evidence/P4r4-trust-state-model.json` `A_valid_realisable_TBM_t9_reference_t11` accepts this order.
`RV3-D-A13_realisable_tbm_order` refuses an older binary after a newer one was accepted. The mutant
`M-a7-against-tss-high-water` fails both.

### 5.1 Attested-source binding (normative; CD3-3 (1), (2))

1. **Candidate statement.** Release statement v3 adds `release.source {release_commit, source_tree_digest,
   build_inputs_digest}` (`07` §3). The producer fills it from the reproducible build inputs.
2. **Verification attestation v2.** Adds `source`, equal to the candidate's. The independent verifier attests ACCEPTED
   only after reproducing the candidate payload from that source with those build inputs (`05` §7 rule 3).
3. **V8** (`04` §3). A final is authentic only if all of these hold:
   - `promoted_from_candidate` names a candidate that verifies under `release-candidate`;
   - `kernel.tree_digest` is equal in final and candidate;
   - **`release.source` is equal in final and candidate**.

   Otherwise `RELEASE_IDENTITY_MISMATCH(source)`. The check runs at every verifier, not only in `gov release promote`.
4. **Acceptance (A4b).** The attested source must equal the TBM source and the build-attested source. The effective TSS
   must reference the attestation. A REJECTED attestation for the candidate, or a negative for final or candidate,
   refuses.
5. **Custodial rules** (§9) apply the same check before each signature. `verify-artifact` does not rely on them.

## 6. Non-circular chain

```text
independent channel ──(human, OP-6)──► trust_root_id ──► compiled root chain of the FIRST binary
   first binary obtained by (i) build from source at the final tag, (ii) independent tooling verifying A2–A6, or (iii) an
   already trusted gov running verify-artifact

candidate C (release-candidate) ── independent verifier reproduces C from source S ──► attestation ACCEPTED(C, S)
final F (release-final) promoted from C with source S (V8)
binary N+1 built from S with the TBM naming TSS n ── rebuilder attests (binary, TBM, S)
release-artifact ×2 sign (binary, TBM) ── TSS m > n references attestation and artefact
binary N (trusted) ──verify-artifact A1–A10──► binary N+1
```

Why it is not circular:
- Nothing in binary N+1 authenticates binary N+1.
- The source is named by the verification attestation, not by any statement that the binary's own build produces.
- Ordinary installs run `verify-artifact`; they never need build internals.

## 7. What each compromise yields (CD3-3 (3): restated from the corrected rules)

Evidence: `evidence/VA4-verify-artifact-source-scenarios.json`. Of its 16 rows, 16 are as expected. Twelve attacks are
refused, and three minimum capability sets are documented as accepted. Routes:
- **S** — malicious source through the verification record;
- **B** — malicious bytes claimed as a build of genuine source;
- **I** — insider source accepted by an honest verifier.

| Compromised (with honest downstream custodians unless stated) | Accepted malicious binary? | Why |
|---|---|---|
| one `release-final` key + pipeline input (RV3-B-A08) | **no** | V8 source equality: `RELEASE_IDENTITY_MISMATCH(source)` |
| `release-candidate` + `release-final` + pipeline input; candidate REJECTED | **no** | `ARTIFACT_SOURCE_REJECTED` |
| OP-4 "no" everyday key (candidate + final) + pipeline input (RV3-D-A03) | **no** | no ACCEPTED attestation for the source: `ARTIFACT_SOURCE_UNVERIFIED` |
| **route S:** `verification-attestation` + `release-candidate` + `release-final` + pipeline input | **yes** | **3 distinct keys over 3 purposes** (KS-4 and KS-6 force distinctness from the verifier) plus control of the build input |
| **route S under OP-4 "no":** `verification-attestation` + the everyday key + pipeline input | **yes** | **2 distinct keys** plus pipeline input |
| route S under OP-2 "root-registered production source" | **no** | `ARTIFACT_SOURCE_UNREGISTERED`; needs the root threshold |
| route S under OP-2 "verification-attestation threshold 2", one verifier key | **no** | `ARTIFACT_SOURCE_UNVERIFIED` |
| **route B:** `release-artifact` ×2 + `build-attestation` + `trust-state` | **yes** | **4 keys over 3 purposes**, no pipeline control needed (unchanged from revision 3) |
| route B with one `release-artifact` key | no | `THRESHOLD_NOT_MET` |
| route B without a build attestation | no | `ARTIFACT_BUILD_UNATTESTED` |
| **route I:** an insider's malicious commit that the independent verifier accepts | **yes** | no key compromise. Bounded by the verification process (TB-4); root-registered source adds the root ceremony's review |
| a genuine older binary presented as an upgrade | no | `BINARY_T0_ROLLBACK` against the accepted-TBM high-water |
| a revoked genuine binary on an aged, expired or bypassed anchor (RV3-D-A15) | no | inclusion anchors, pin validity, currency proof (`24`) |

**True minimum under the architecture minimum.** Two routes remain:
- **Route S.** Two keys under OP-4 "no", three under OP-4 "yes", in both cases over distinct purposes, plus control of
  the build input.
- **Route B.** Four keys over three purposes.

No single key of any purpose, at any threshold, can mint an accepted production binary.

**Under the OP-2 options.**
- Root-registered production source raises route S to the root threshold. The minimum then becomes route B: four keys
  over three purposes.
- Verification threshold 2 raises route S by one key.

`05` §3, TB-3 and `21` OP-2 and OP-4 carry this table.

## 8. What is protected (HO-0001 §3.3 list)

| Asset | Protection |
|---|---|
| The binary | A1, A2, A4a |
| **Its source** | A4b: attested source, V8 source equality, TSS-referenced attestation, no REJECTED attestation; optional root registration |
| Compiled trust roots | TBM `root_chain` resolves (A6); accepted-TBM high-water (A7) |
| Compiled minimum floors, surface, precedence registration | the root-signed TPS named by the TBM (A6) |
| Compiled trust-policy identity | TBM `trust_policy` digest (A6) |
| Compiled historical-release set | TPS `eligibility.historical_releases[]` (root threshold) |
| Compiled trust state and bootstrap rules | TBM `trust_state` (A6); bootstrap in the TPS; enforcement code under the build attestation of attested source (A4a, A4b) |

## 9. Custodial rules (`05` §7 rules 3, 6, 7)

| Custodian | Before signing, MUST run | Refuses on |
|---|---|---|
| Independent verifier (`verification-attestation`) | reproduce the candidate payload from `source` with `build_inputs_digest` | any difference; attests REJECTED on failure |
| Rebuilder (`build-attestation`) | `gov trust verify-artifact --stage rebuilder`: A3, A4b, A6 against the draft | an unattested, rejected or non-matching source |
| `release-artifact` custodians | `--stage custodian`: A1, A3, A4a, A4b, A6 | as above |
| Trust-state publisher (`gov trust publish`) | `--stage publisher`: A1–A4b, A6 before referencing an artefact | as above |
| Root co-signers (OP-2 (iii)) and root ceremony (production-source registration) | the same, plus comparison with the owner's verification record | as above |

`VA4` rows "custodial pre-check" show each stage refusing the RV3-B-A08 artefact before any signature. These rules
narrow custodian error. The verifier-side A4b is the enforcement.

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-1 | The binary remains the TCB; a user who runs an unverified binary is outside the chain. | TA-1; `verify-artifact`; first-run self-check against the accepted-TBM high-water (RV3-M8 closed) | RT-92, RT-93 |
| TB-2 | The build attestation trusts the rebuilder's environment. | Bounds only "bytes equal a build of the attested source"; independent custody (TA-10); OP-2 may require two rebuilders | RT-92 |
| TB-3 | Compromise of a minimum capability set of §7. | Route S: 3 keys (OP-4 "yes") or 2 keys (OP-4 "no") plus pipeline input; route B: 4 keys over 3 purposes. Raised by the OP-2 options. Remedy: root rotation and revocation (`05` §9). | RT-92 source rows; `VA4` |
| TB-4 | A malicious commit accepted by an honest but deceived independent verifier (route I). | Procedural: verification scope and harnesses; OP-2 verification threshold 2; root-registered source adds a root review | — (process) |
