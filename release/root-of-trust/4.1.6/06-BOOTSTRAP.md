# Output 6 — Bootstrap model (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises bootstrap to CP-1 (`35`): the first-contact value is a pair of codes over statements signed at the
> root threshold (First-Contact Authority record) and at the trust-state threshold, published by two sources under separate
> custody that verify first-hand (`32`); the source identities and procedure come from the root ceremony record, not from any
> binary or carrier (`32` R-FCD, EX-24); the admission state is at most 24 hours old; re-admission applies both stores (`31`);
> environments are derived from the registered lock (`33`). Unselected source answers, platform package roots and the revision-6
> manifest are excluded (EX-04, EX-05, EX-17, EX-18, EX-23). Revision-6 text is history at `4106885`.

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. Trust enters once, by values
published independently of the download channel and read by a person now. It is carried forward by signatures and first-hand
establishment.

Revision 6 published one composed value per Trust State. Review r6 showed that its composer, the designation of the sources and a
package submitter selected the first TCB, and that stored values had no age bound (RV6-H1, RV6-H2).

Revision 7 publishes two codes. The **trust code** names the First-Contact Authority record, signed at root threshold after the
admitter was registered, reproduced and verified. The **state code** names a Trust State signed at 2 of 3 trust-state keys. Each
source custodian publishes both only after verifying them itself. What no mechanism removes, the **first-contact root**, is
stated with its computed minimum (`32` §9).

## 2. Production bootstrap

1. **Root ceremony** (once per lineage). Three root keys under the three custodial roles on offline hardware-backed devices;
   root v1 with the CP-1 purpose shapes (`05` §3). The ceremony record names the two first-contact sources (authenticated private
   release channel; immutable release mirror), their custodians and custody domains, the procedure text, the supplier and
   toolchain provenance registry, and the certified targets. Operators receive the source identities and the procedure from the
   organisation's copy of this record at onboarding (`32` R-FCD-2).
2. **Constitution.** `gov trust draft-policy` produces the Trust Policy draft, checks it against CP-1 (`PROFILE_NONCONFORMANT`
   otherwise), runs the derivation calculator and the pack checks (`29` §5.3, §5.5). The root ceremony reviews and signs.
3. **Release.**
   1. Reproducible payload build with source identity v2, input manifest v3 and the environment lock in source (`30` §4, `33` §3).
   2. `release-candidate` signature.
   3. Two independent verification records `verification-attestation.v5`, each from its own execution, for exactly the candidate,
      kernel, environments and toolchains the verifier reproduced, returned first-hand (OP-8).
   4. Promotion (`release-final`, 2 signatures).
   5. Environment reproductions of the derived manifests (`33` R-BENV-7″).
   6. **Registration** by 2 of 3 registration custodians (`30` R-REG-3 (a)–(h)), including each custodian's own reproduction
      and first-hand content derivation (`34` R-CON-1).
   7. Certification (optional; negatives only).
4. **Binaries.** Every certified target is built reproducibly by three independent reproducer roles, in re-assembled
   environments of two independent supplier classes and with two independent toolchain lineages. Each reproducer signs a
   one-signature reproduction and confirms first-hand to the publisher (`30` §7). The registration names the binary digests
   (OP-9 (d)). The publisher references exactly one digest per target in the next Trust State (`30` §8).
5. **First-contact authority.** When an admitter release or the certified targets change, the root ceremony signs a new FCA
   after checking the admitter's registration, reproductions and verification records (`32` R-FCA-1). Every Trust State
   references the FCA in force.
6. **Publication in the sources.** Each source custodian verifies the FCA and each new Trust State first-hand and publishes the
   trust code, state code, FCA payload, procedure and `gov-admit` bytes, byte-identical to the other source (`32` R-FCS-1…3).
7. **First binary on a machine: independent admission only** (`31` §4, `32`). The operator runs FC-1′…FC-3′ with platform
   tools. `gov-admit` enforces FC-4′…FC-10 and evaluates admission-predicate/1 (`25` §5) over the bytes it read, installs from
   its buffer, and writes the admission record in the protected admission store. There is no other first-binary path.
8. **Subsequent binaries** are accepted by the admitted `gov` running the same predicate, with its anchors and a currency proof
   of at most 24 hours naming the Trust State that publishes the binary (`25` AP-3).

## 3. First-install ceremony on a machine

| Step | Command | Runs on | Establishes |
|---|---|---|---|
| 0 | FC-1′: read trust code, state code and procedure digest from both sources named at onboarding; FC-2′: `sha256sum` of the FCA payload equals the trust code, the target is certified; FC-3′: `sha256sum` of `gov-admit` equals the FCA's entry | the operator's platform tools (the procedure text from the ceremony record) | evaluator selection through the root-threshold record both sources show (the first-contact root) |
| 1 | `gov-admit --trust-code <source 1> --trust-code <source 2> --state-code <source 1> --state-code <source 2> --authority <fca> --statements <bundle> --install <dest> <candidate>` | `gov-admit` | TCB admission under the compiled lineage; state ≤ 24 hours; first admission decided by the protected store (`31` R-ADM-8″) |
| 2 | `gov trust confirm-root` (once per store, OP-6 (a)); `gov trust confirm-state <state code> <state code>` from both sources, or a protected pin, **on a protected installation** (`31` GB-4′) | the **admitted** `gov` | lineage confirmation; anchor with currency for 24 hours (`24` §3.2) |
| 3 | `gov trust refresh --from <bundle>` if the machine is `BELOW_ANCHOR` | the admitted `gov` | knowledge at the anchored epoch |
| 4 | `gov init` / `gov update --apply`, with the local trust gate (`27`) carrying both state codes | the admitted `gov` | installation |

Before step 1 completes, every RoT-1 `gov` on the machine runs C0-R only (`31` GB-1″). On a user-writable installation, steps 2
and 4 are refused; the classes reachable there are `31` §7.1.

**Automation.** Pins and decision pins live in the system pin directory only; they are provisioned outside the repository
writer's control (TA-9, `24` §3.5).

A **CI runner image** runs steps 0 and 1 at image build, within 24 hours of the state it admits. It writes a root-owned
protected store and an admission record valid for at most 7 days, beside a root-owned CI pin naming the same Trust State and
valid for at most 7 days, and runs jobs as another user. A job running as root, or with passwordless `sudo`, violates TA-9: pins
are ignored and C3 refuses (`31` GB-6). Images are rebuilt before the record or the pin expires.

An **air-gapped machine** uses media carrying the immutable mirror's material; admission refuses a state older than 24 hours
(owner trade-off OT-1, `35` §6).

No environment variable, flag, repository file or value printed by an unadmitted binary can confirm a lineage, anchor a state,
designate a source or admit a binary (D-0008 rules (15), (16)).

## 4. Lineage pinning and mismatch

The protected store and the account store pin the lineage (full 64-hex id); the lock records `trust_root.id`; a binary whose
compiled lineage differs is `TRUST_ROOT_LINEAGE_MISMATCH`. Re-rooting after a root threshold compromise needs
`gov trust adopt-lineage` by a human through the `adopt_lineage` trust gate, first admission of a binary under the new lineage,
and a new lineage confirmation (OP-6 (a)).

## 5. Consumer repository on a new machine

A clone carries `governance/trust/**` and the occupation entries (`26` §2). The trust tree includes kernel, release and
registration statements, state, root links, FORMAT, lock and the `.gitattributes` member. The admitted binary authenticates
them offline.

The new machine has no stores until first admission. It is `UNANCHORED` until step 2 and runs C0 (`24` §4.3); trust ingress is
refused.

## 6. Development builds

`cargo build` from a checkout compiles that checkout's trust data into a TBM marked `build: development`. Such a binary is never
admitted, never records an accepted TBM, and never produces production eligibility for unregistered material.

## 7. Test fixtures

`gov-test-profile` compiles the test lineage with the purposes of `05` §1, a test FCA and test codes per test Trust State.

## 8. Classification summary

| Class | Selected by | Authenticity / stage | Production eligibility | Doctor |
|---|---|---|---|---|
| Production final, registered | 2-of-3 registration referenced by the effective TSS, content derived first-hand | `AUTHENTICATED` / `final` | per `19` §6 (E7 with the release's registration and AP-5's restrictors; at or above the computed security minimum) | clean |
| Production final, not registered (or not yet held) | — | `AUTHENTICATED` / `final` | ineligible (`release_unregistered`) | HIGH |
| Production candidate | `release-candidate` | `AUTHENTICATED` / `candidate` | `ELIGIBLE_EVALUATION` only | HIGH |
| Legacy 4.1.2–4.1.5 | TPS `eligibility.historical_releases` (root threshold) | `HISTORICAL_IDENTIFIED` | never | CRITICAL when installed |
| Development unsigned | nobody | `DEVELOPMENT_UNSIGNED` | never | HIGH |
| Production binary | admission-predicate/1 by an evaluator other than the candidate; at first contact, the FCA and Trust State both sources show, ≤ 24 hours | admitted, record in the protected store | TBM ≥ accepted-TBM high-water; certified target | — |
