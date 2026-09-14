# Output 25 — Binary and trust-base authenticity

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 3. Closes R2-H3 as a class and satisfies HO-0001 §3.3. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

The `gov` binary carries T0: its compiled root chain, Trust Policy (floors, surface, bootstrap rules, historical
releases), Trust State, purpose table, schemas, operator semantics and the embedded kernel. It is the trusted computing
base.

Revision 2 authenticated binaries with an `artifact-final` statement under the threshold-1 `release-final` purpose. It
required no attestation, certification or trust-state reference, and had no field for the binary's compiled trust base.
One stolen token could mint a binary with arbitrary roots and floors, and every consumer following the documented upgrade
would install it. The mistaken equivalence was *release key ⇒ binary authenticity*.

Revision 3 rule: **the authentication of a binary MUST be at least as strong as the authority the binary carries.** A
binary carries root-threshold authority (compiled roots and floors), so its acceptance MUST require all of the following:
- a multi-key purpose that holds no other authority;
- independent reproduction of the exact bytes from the tagged source;
- a trust-state reference;
- a compiled trust base that resolves to root-signed and trust-state-signed statements.

## 2. Options evaluated (HO-0001 §3.3)

| Option | What it protects | Cost | Adopted? |
|---|---|---|---|
| Threshold **root** signature on every binary | everything, maximally | root keys (offline, independent custodians) touched for every binary build and target | **Not the default.** Offered in OP-2 as "root co-signature for production binaries". |
| Separate binary purpose (`release-artifact`) with compiled minimum threshold 2, disjoint from every other purpose | no single key, and no release or candidate key, can accept a binary | a second custodian per binary release | **Adopted** (§3). |
| Separate **root-bundle attestation** | the compiled root, TPS and TSS identity | — | Adopted as the **Trust Base Manifest** (TBM). Every component is itself a root- or trust-state-signed statement, so no extra signature is needed (§4). |
| Certification binding | a visible "certified" label for binaries | certification key | Adopted as **informational**: certification may name artifact statement digests. Under OP-3 mode A it relaxes nothing. |
| Reproducible-build or build-provenance evidence | that the bytes are what the tagged source produces, including the compiled TBM and all compiled rules | an independent rebuilder with its own key | **Adopted and mandatory** (`build-attestation` purpose, §3). |
| Compiled trust-state digest | that the binary's compiled TSS is a published one | — | Adopted (TBM `trust_state`). |
| Binary trust-policy digest | that compiled floors, surface and bootstrap rules are root-signed | — | Adopted (TBM `trust_policy`). |
| Multi-signature | no single-token compromise | custody | Adopted: `release-artifact` threshold ≥ 2, plus build attestation, plus trust-state reference. |

## 3. Purposes (additions to `05`)

| Purpose | Signs | May assert | May never assert | Compiled constraints |
|---|---|---|---|---|
| `release-artifact` | `artifact-final.v2+json` | that listed binary digests, each bound to its TBM digest, are the production artefacts of a final release | release authenticity, certification, trust state, build reproduction | **threshold ≥ 2** (compiled minimum; OP-2 may raise it or add a root co-signature); **KS-9:** keys disjoint from every other purpose |
| `build-attestation` | `build-attestation.v1+json` (schema `schemas/build-attestation.schema.json`) | that an independent rebuild of `source_commit` with `build_inputs_digest` produced the same binary digest and the same TBM digest | release or artefact authenticity, certification | threshold ≥ 1 (OP-2); **KS-10:** keys disjoint from `release-final`, `release-candidate` and `release-artifact` |

- `artifact-candidate.v2+json` stays under `release-candidate`. Candidate binaries are for evaluation only;
  production `verify-artifact` refuses them.
- `release-final` no longer signs any artefact statement.

## 4. Trust Base Manifest (TBM)

**Definition.** A canonical GOV-JCS-1 document compiled into every binary (schema
`schemas/trust-base-manifest.schema.json`). `gov version --trust` prints it together with its digest.

| Field | Content |
|---|---|
| `binary` | name, version, target, `trust_profile`, `source_commit`, `build_inputs_digest` (toolchain, lockfile, build script digests), toolchain id |
| `lineage` | `trust_root_id` |
| `root_chain[]` | `{version, statement_digest}` for every compiled root version |
| `trust_policy` | `{policy_version, statement_digest}`. The TPS contains floors, the Constitutional Surface (`23`), eligibility including the historical-release set, install authority, gating, the bootstrap block (OP-6 and OP-7 parameters) and lowering history. |
| `trust_state` | `{sequence, statement_digest}` |
| `embedded_release` | `{release_statement_digest, tree_digest}` |
| `compiled_rules` | `floor_schema_version`, operator vocabulary id (`floor-ops/2`), purpose-table digest, statement-schema-set digest, trust-format readers (`rot-1/legacy-path-occupation-v1`), command register digest |

**What each part protects:**
- **Signed components** (root chain, TPS, TSS, embedded release): the TBM names them by digest, so a verifier can check
  that they are genuine statements of the right purposes.
- **Compiled code** (purpose table, schemas, operator semantics, command register, bootstrap enforcement): these are
  protected by the build attestation. A reproduction of `source_commit` yields identical bytes only if the code is the
  tagged code.

## 5. `gov trust verify-artifact <binary> <artifacts.dsse.json>` (normative; replaces `06` §2 step 6 and R-BOOT-4)

| Step | Check | Failure code |
|---|---|---|
| A1 | Read the binary once; SHA-256. | `ARTIFACT_DIGEST_MISMATCH` |
| A2 | The artifact statement verifies under the effective root for `release-artifact` at threshold (≥ 2 distinct keys; KS-9). | `PURPOSE_NOT_GRANTED` / `THRESHOLD_NOT_MET` |
| A3 | The entry matches: digest, target, `trust_profile: production`, lineage equal to this machine's pin, stage `final`. | `ARTIFACT_IDENTITY_MISMATCH` / `TRUST_ROOT_LINEAGE_MISMATCH` |
| A4 | At least the threshold of verified `build-attestation` statements (KS-10 keys) name the same artifact digest, the same TBM digest, and a `source_commit` equal to the referenced final release's `release_commit`. | `ARTIFACT_BUILD_UNATTESTED` |
| A5 | An admissible TSS held in knowledge references the artifact statement digest (`artifacts[]`). This is release-local: supply trust metadata if missing. | `ARTIFACT_UNREFERENCED` |
| A6 | Every TBM component resolves to a verified statement of the correct purpose with an identical digest: each root version, the TPS, the TSS and the embedded release statement. | `BINARY_T0_UNVERIFIED` |
| A7 | TBM root version, policy version and state sequence are each ≥ this VTS's high-water. No override. | `BINARY_T0_ROLLBACK` |
| A8 | The artifact and its statement are not in the negative set; binary version ≥ effective `min_binary_version`. | `ARTIFACT_REVOKED` / `BINARY_BELOW_TRUST_POLICY` |
| A9 | Freshness: this is trust ingress (C3), so `ANCHORED` or `WITNESSED` is required (`24` §4). | `TRUST_STATE_UNANCHORED` |
| A10 | Record the accepted TBM in the VTS high-water (§6). | — |

**Self-check at first run.** A binary whose compiled TBM is below the VTS high-water MUST refuse trusted operations with
`BINARY_T0_ROLLBACK`. This catches genuine older binaries even when `verify-artifact` was skipped. A malicious binary can
ignore it, which is why A1–A9 decide acceptance.

## 6. Non-circular chain

```text
independent channel ──(human, OP-6)──► trust_root_id ──► compiled root chain of the FIRST binary
   first binary obtained by: (i) build from source at the final tag, or (ii) independent tooling verifying A2–A6
   with public keys from root metadata whose id was compared on the channel (OpenSSL + an independent rebuild)

binary N (trusted) ──verify-artifact──► binary N+1
   A2 release-artifact ≥2 keys ── A4 build-attestation (independent rebuild) ── A5 trust-state reference
   A6 TBM components = root-threshold root/TPS, trust-state TSS, release-final embedded release ── A7 ≥ VTS high-water
```

**Why it is not circular:**
- Nothing in binary N+1 authenticates binary N+1.
- Nothing at the release host authenticates the first binary.
- Ordinary project installs never need to understand build internals: they run `verify-artifact`, and the build evidence
  is a signed statement.

## 7. What each compromise yields (corrects `05` §1 and review RK-11)

| Compromised | Can mint an accepted malicious binary? | Why |
|---|---|---|
| one `release-final` key | no | not granted `release-artifact` (`PURPOSE_NOT_GRANTED`, evidence `A27`) |
| one `release-artifact` key | no | threshold 2 (`A27b`) |
| both `release-artifact` keys | no | needs a build attestation (`A27c`) and a trust-state reference (`A27d`) |
| `release-artifact` ×2 plus `build-attestation` | no | needs a trust-state reference (`A27d`) |
| `release-artifact` ×2 plus `build-attestation` plus `trust-state` | **yes**, for machines that verify with those keys still granted | This is 4 keys over 3 purposes held by different custodians. Compiled floors or roots other than root-signed ones still fail A6, but the malicious code can ignore its TBM. Remedy: root rotation (`05` §9). |
| a genuine older binary presented as an upgrade | refused | `BINARY_T0_ROLLBACK` (`A28`) |
| OP-4 "no" (one key for candidate and final) | no effect on binaries | `release-artifact` is separate (`A29`) |

## 8. What is protected (HO-0001 §3.3 list)

| Asset | Protection |
|---|---|
| The binary | A1–A4 (digest, `release-artifact` threshold, independent reproduction) |
| Its compiled trust roots | TBM `root_chain` resolves to dual-threshold root statements (A6); high-water (A7) |
| Compiled minimum floors | inside the root-signed TPS named by the TBM (A6); a floor below high-water is refused (A7) |
| Compiled trust-policy identity | TBM `trust_policy` digest (A6) |
| Compiled historical-release set | moved into the root-signed TPS `eligibility.historical_releases[]` (the former threshold-1 historical-identity statement is withdrawn, `05` §2) |
| Compiled trust state and bootstrap rules | TBM `trust_state` (A6); bootstrap block inside the TPS; enforcement code under the build attestation (A4) |

## 9. Residuals

| ID | Residual | Bound |
|---|---|---|
| TB-1 | The binary remains the TCB; a user who runs an unverified binary is outside the chain. | TA-1. `verify-artifact` and first-run self-check (§5); documented procedure. |
| TB-2 | The reproducible-build attestation trusts the rebuilder's environment. | An independent custodian and toolchain; OP-2 may require two rebuilders (threshold 2). |
| TB-3 | Compromise of release-artifact ×2 plus build-attestation plus trust-state. | §7; root rotation. |
