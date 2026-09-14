# 01 — Alternative: fact-derivation architecture for the TCB and constitutional content (specialist B, AR-0010)

> **Proposal only.** Nothing here is a revision of the RoT-1 pack, D-0008 or ARCH-0002, which stay PROPOSED and not in
> effect. No owner option is decided. The synthesis architect decides what, if anything, enters revision 5.

## 1. Principle

**Derivation floor (proposed rule; generalises D-0007 from inputs to facts).** The strength of a fact that a decision
consumes is the minimum, over every input that can **change or select** that fact, of that input's establishment
strength. The following add nothing to that strength:
- a signature over something the signer did not establish;
- a choice made by a lower-trust party among higher-trust alternatives;
- an evaluation performed by the object being evaluated.

A decision may consume a fact only if its derived strength is at least the authority the decision confers. Where a
derivation can be enumerated, the minimum is **computed**, never argued.

Three structural rules follow. Each removes one class at its root (`00` §3).

| Rule | Removes | Class |
|---|---|---|
| **R-1 First-hand establishment.** The TCB acceptance predicate contains only statements whose purpose is first-hand establishment of one named fact. Each fact has a compiled minimum quorum of distinct keys. No purpose signs bytes, digests or data it received from another party. | pass-through | BC4-1 |
| **R-2 Independent evaluation with an identical base case.** TCB acceptance is one normative predicate. Every machine evaluates it with code that is not the candidate, over bytes that code measured, and installs exactly those bytes. The first acceptance on a machine uses the same predicate, with the independent channel as anchor and currency. | evaluator inside the object | BC4-2 |
| **R-3 Single-valued registration.** Every registration of non-orderable constitutional content is a function from release identity to exactly one value. Set-valued registrations are malformed. Reverting to superseded content, or rewriting a registered sequence, is a computed reduction. | selection from an authorised set | BC4-3 |

The mechanisms M1–M3 implement R-1…R-3. M0 makes the derivation floor mechanical.

## 2. M0 — Derivation checks (mechanical)

| Check | Where | What it does |
|---|---|---|
| **Fact Threshold Check (FTC)** | the binary, when accepting a root version (extends SV-4) | Refuses a root version whose grants give any fact-establishing purpose less than its compiled minimum quorum, or that lets such keys hold another purpose (`FACT_THRESHOLD_BELOW_MINIMUM`). Owner options can raise quorums, never lower them. |
| **Derivation calculator** | `gov trust draft-policy` and the canonical CI, before a root ceremony | Enumerates every capability subset over the release-process model (keys, verifier processes, pipeline) for the owner's registered answers, with honest parties acting only on first-hand checks. It fails when any minimal accepted set has fewer first-hand establishers of the attacked fact than its minimum. Its output is the owner-option consequence table. F1 is the reference: 32 configurations, 0 violations. |
| **Single-valued lint** | producer checker, TPS acceptance | `REGISTRATION_NOT_SINGLE_VALUED` for any registration that yields two values for one release identity (F3: exit 5 on revision 4's RETAIN form). |
| **Mutation oracle for the new rules** | conformance | Every rule of M1–M3 has a scenario that fails when the rule is removed. F2: 18 of 18 mutants detected. This extends the RV4-M7 requirement to the proposal's own rules. |

## 3. M1 — TCB legitimacy by first-hand establishment (BC4-1)

### 3.1 The facts and who establishes each

| Fact | Meaning | First-hand establishers | Compiled minimum | Inputs removed from the decision |
|---|---|---|---|---|
| **F-SRC** | the source identity is a legitimate production source for release sequence *n* | **independent verification runs** that reproduce and review the candidate from source. Two ways the machine can check it (owner choice OC-1, `03`): **L1**, a root-threshold Release Admission Statement (RAS) signed only against two first-hand verification records; **L2**, two verification attestations by distinct keys | two independent verifications, under either form | the pipeline's choice of commit (V8 kept); a single verifier; `release-final` |
| **F-BUILD** | SHA-256 of binary *B* and its TBM digest are the output of building source *S* for target *T* under the admitted build profile | **reproducers**, each building *S* from its own fetch and attesting the digest **it computed** | quorum *q* ≥ 2 distinct `build-attestation` keys (OC-2 may raise it) | the pipeline's bytes: no party signs bytes it was handed |
| **F-T0** | the roots, TPS, TSS, historical set, floor vocabulary and bootstrap rules compiled into *B* are genuine | none separately: they are files of *S*, so F-SRC ∧ F-BUILD establish them; the TBM digest is attested by the reproducers | — | — |
| **F-CUR** | *B* is announced and not revoked as of a currency proof | the Trust State Statement referencing *B* and the admission; the negative set; inclusion anchors and currency proofs (revision 4, kept) | as revision 4 | the supplier's choice of statements (inclusion anchors kept) |
| **F-LIN** | the root chain's lineage equals the machine's confirmed lineage | TA-5 | — | — |
| **F-EVAL** | the evaluator is not *B* | structural (M2) | — | self-report |
| **F-MEAS** | the bytes installed and executed are the bytes measured | the evaluator installs from its measured buffer; TCB-location predicate (CR4-B-01 (b)) | — | a re-read of the path |

**Source identity** is the triple (commit id, **canonical content digest**, build-profile digest).
- The canonical content digest is SHA-256 over the sorted list of (mode, path, SHA-256 of blob bytes) of the whole tree.
  It is recomputable from any copy of the tree, independent of commit history, archive tool and time.
- It replaces "SHA-256 of `git archive`". F4 shows that form binds the commit id and, for a tree, the current time.
- The build-profile digest names the toolchain, the lockfile and the **path-remapping build profile**. F5: plain release
  builds differ when the Cargo home path differs, with 188 embedded path strings. With `--remap-path-prefix` for source,
  Cargo home and toolchain home, four builds at different paths are bit-identical, with 0 path strings.

### 3.2 Purposes

| Purpose | In revision 5 as proposed | Change from revision 4 |
|---|---|---|
| `build-attestation` | signs (binary digest, TBM digest, source identity, target, profile), one statement per reproducer; counted as a quorum across statements by distinct unrevoked keys | threshold 1 → compiled quorum ≥ 2; keys hold no other purpose (FTC); **re-attestation after key rotation requires re-reproduction** (revision 4 `05` §8 re-signs retained statements, which would launder a stolen key's attestations) |
| `verification-attestation` | L2: counted, quorum 2. L1: advisory; a REJECTED attestation still refuses | threshold 1 → 2 (L2), or out of the predicate (L1) |
| Release Admission Statement | L1: `trust-policy` purpose at root threshold; names sequence, source identity and (OC-3 E1) the admitted final digest | new statement type |
| `release-artifact` | **retired** | its threshold-2 statement asserted nothing first-hand |
| `release-final`, `release-candidate` | authenticity of release content; V8 kept; not a TCB input | blast radius restated (§6.3) |
| `trust-state` | currency and selection among already-legitimate binaries; never legitimacy | reference rule: exactly one quorum digest per (final, target, profile) |
| `certification-status`, `revocation`, `freshness-witness`, `retrieval-profile`, `root`, `trust-policy` | as revision 4 | — |

### 3.3 Admission Predicate AP (normative order)

1. Trust state: `EQUIVOCATION`, `REGRESSION`, `BELOW_ANCHOR` or `ANCHOR_CONFLICT` refuses.
   `TRUST_STATE_INCOMPLETE(root_reference_unresolved)` if the effective TSS references a root version the evaluator does
   not hold.
2. V8: the final's source equals its candidate's source.
3. The TBM source identity equals the candidate's.
4. **F-BUILD:** at least *q* distinct valid, unrevoked `build-attestation` keys attest the measured digest, the TBM
   digest and the source.
5. **Single-valued:** no second quorum-attested digest exists for the same (final, target, profile)
   (`ARTIFACT_EQUIVOCATION`).
6. A REJECTED verification attestation for the candidate refuses.
7. **F-SRC:** L1, a valid RAS for (sequence, source identity, final digest) referenced by the effective TSS; L2, two
   ACCEPTED attestations by distinct keys referenced by the effective TSS.
8. **F-CUR:** the effective TSS references the binary digest; binary, final and candidate are not in the negative set.
   Revoked attestations do not count toward steps 4 and 7 (folds in RV4-L6).
9. Currency: C3 is allowed (a currency proof, revision 4 `24` §4.4).

The accepted-TBM high-water (A7) and TBM resolution (A6) are kept unchanged after step 9.

### 3.4 Honest-party rules the design relies on (modelled in F1)

| Party | Acts only on |
|---|---|
| verifier *i* | its own reproduction and review of the candidate; reports the verdict to the owner's first-hand record and signs it |
| root custodians (L1) | two first-hand verification records ACCEPTED for the source identity, and the canonical content digest each custodian recomputes from its own fetch |
| reproducer *i* | the admitted (L1) or quorum-attested (L2) source identity; builds from its own fetch under the admitted profile; attests only its own digest |
| trust-state publisher | references exactly one quorum-attested digest per (final, target, profile), received from reproducers; refuses on two; never references a candidate with a visible REJECTED verdict |

### 3.5 Result (F1, computed; reviewer B's model reused for anchors and currency)

| Goal | Revision 4 (reviewer B's enumeration, re-run) | Alternative, minimal accepted sets |
|---|---|---|
| malicious bytes for genuine source | `{ba, pipeline}`; `{ba, ra1, ra2, ts}` | *q* = 2: `{ba1, ba2, pipeline}`, `{ba1, ba2, ts}`, `{root1, root2}`. *q* = 3: `{ba1, ba2, ba3, pipeline}`, `{ba1, ba2, ba3, ts}`, `{root1, root2}` |
| malicious source, L1 | (S0), REJECTED not reaching: `{va, pipeline}`; (S1): none | `{vp1, vp2, pipeline}` (two compromised verification processes), `{root1, root2}` |
| malicious source, L2 | (S2), REJECTED not reaching: `{va, va2, pipeline}` | REJECTED suppressed: `{va1, va2, pipeline}` and process variants. REJECTED visible: `{vp1, vp2, pipeline}` or seven-capability sets. `{root1, root2}` in both. |

In every row, every minimal set contains at least two first-hand establishers of the attacked fact (F1 `invariant_check`,
0 violations over 32 configurations). A single stolen key plus pipeline input yields nothing under any owner answer.

### 3.6 Trust inputs, removals, additions, assumptions, costs

| | M1 |
|---|---|
| **Trust inputs** | root threshold; two independent verification processes; *q* reproducers; trust-state publisher (currency only); TA-5 lineage |
| **Removes** | `release-artifact` and custodial signing of received bytes; route enumeration by hand; `release-final` and a single verifier from the TCB; `source_tree_digest` over `git archive` |
| **Adds** | build-attestation quorum; canonical content digest; admitted build profile; FTC; derivation calculator; single-valued publisher rule; re-reproduction on re-attestation; RAS (L1) |
| **Assumes** | bit-for-bit reproducible builds under the admitted profile (F5: holds on one machine and toolchain with path remapping; not shown across OS images); reproducer independence is custodial (TA-4), not cryptographic; the admitted toolchain is not malicious (TB-2′) |
| **Costs** | *q* ≥ 2 reproducer services with disjoint custody (the two `release-artifact` custodians are freed); a normative build profile; under L1 one root ceremony per binary-shipping release, which revision 4's proposal (OP-2 (S1)) already implied; under L2 a second verifier |

## 4. M2 — Independent admission of the TCB on every machine (BC4-2)

### 4.1 Components

| Component | Specification |
|---|---|
| **AP specification** | §3.3 is published as a versioned specification (`admission-predicate/1`). Two implementations exist: `gov trust verify-artifact` and the admitter. Both are conformance-tested against one scenario oracle (F2 is the reference). |
| **Admitter `gov-admit`** | a small, separately reproducible program that implements only AP, statement verification and installation. Inputs: the candidate file (read once, hashed from the buffer), an untrusted statement bundle, and, typed or pasted by the operator from **both** independent channels, the lineage id and the current **state fingerprint**. Anchor = the fingerprint (inclusion). Negative set = the anchored TSS chain. Currency = the channel read now (P2-equivalent). It never executes the candidate. |
| **Admitter integrity** | its digest is registered in the root-signed TPS `bootstrap.admitter_digests[]` and published beside the lineage id in both channels; the operator compares with `sha256sum`, which is not `gov` |
| **Admission Record** | `{binary digest, target, lineage, state fingerprint, admitted_at, admitter digest, valid_until (images only)}`, written with the binary into a protected location (system directory, or the account location under the integrity predicate) |
| **Install** | the admitter installs from its measured buffer (write, fsync, atomic rename). F4 part T shows why re-reading the path is refused. |
| **First admission starts a fresh VTS** | any Verifier Trust Store present for the lineage before the first admission is moved aside, so records written by code that ran before admission are not read |
| **Genuine-binary rule** | a RoT-1 binary refuses C1–C3 and every TA-5 ceremony (`confirm-root`, `confirm-state`, in-gate fingerprints, trust-gate confirmations) unless a protected Admission Record names its own executable digest (`BINARY_NOT_ADMITTED`). It refuses when an image record has expired (`ADMISSION_RECORD_EXPIRED`) and when its held negative set names its own digest (`BINARY_REVOKED_SELF`). C0 stays available. |
| **Subsequent binaries** | the admitted `gov` runs AP with the machine's own anchors and currency (revision 4 A9) and writes the Admission Record for the new binary |
| **Build-from-source mode** | `gov-admit --built <binary> --source <checkout>` recomputes the canonical content digest of the checkout and the binary's SHA-256, and applies AP. The candidate is never run. |

### 4.2 Machine paths

| Path | Procedure |
|---|---|
| First install (M1) | download admitter, compare digest with both channels → `gov-admit` with both channels' fingerprint → install from buffer → the admitted `gov` performs `confirm-root` / `confirm-state` |
| Clean CI image (M2) | the image build runs `gov-admit` with an operator-provisioned fingerprint (TA-9), writing a root-owned Admission Record with `valid_until` ≤ `pin_max_validity_days` beside the state pin |
| Legacy consumer (Phase 4) | `gov-admit`; a legacy binary never verifies a RoT-1 binary |
| Restored backup, old epoch, two machines, long absence (M3, M4, M6, M7) | the binary is already admitted; revision 4's trust-state rules apply; the genuine binary self-refuses once it holds its own revocation |

### 4.3 Result (F2, computed; 32 of 32 scenarios hold)

| Attack | Result |
|---|---|
| RV4-B-A03 revoked binary, transport stripped / all served | `TRUST_STATE_BELOW_ANCHOR` / `ARTIFACT_REVOKED` |
| RV4-B-A03 remediated compromise: root v1 and pre-remediation TSS / root v2 withheld / everything served | `TRUST_STATE_BELOW_ANCHOR` / `TRUST_STATE_INCOMPLETE(root_reference_unresolved)` / `ARTIFACT_BUILD_QUORUM_NOT_MET` |
| RV4-B-A04 moved tag; self-reporting planted binary | `ARTIFACT_BUILD_QUORUM_NOT_MET` or `ARTIFACT_SOURCE_MISMATCH`. F4 executed: refused, the candidate never executed. |
| Phase 4 self-evaluation | `SELF_EVALUATION_REFUSED` |
| RV4-D-A04 ceremonies on an unadmitted genuine binary | `BINARY_NOT_ADMITTED` |
| A genuine revoked binary started without the admitter | `BINARY_NOT_ADMITTED` |
| One channel serving a stale fingerprint; substituted admitter | `CHANNEL_DISAGREEMENT`; `ADMITTER_DIGEST_MISMATCH` |
| Review-r3 RV3-B-A12/D-A12 and RV3-D-A15 through AP | refused in all three variants; the honest control refuses the revoked binary (`ARTIFACT_REVOKED`) |
| First-install minimal accepted sets (malicious bytes) | `{ch1, ch2}` (both channels: TA-5 core), `{ba1, ba2, ts}`, `{ba1, ba2, pipeline}` |

### 4.4 Trust inputs, removals, additions, assumptions, costs

| | M2 |
|---|---|
| **Trust inputs** | TA-5 (two independent channels); the operator's existing `sha256sum`; the admitter's root registration |
| **Removes** | `06` §2 step 6 (b) A2–A6 tooling and (c) self-report as acceptance paths; Phase 4 self-verification; ceremonies on unaccepted binaries; path re-read at install |
| **Adds** | the AP specification and a second implementation; Admission Records; fresh VTS at first admission; the genuine-binary rule; image record validity |
| **Assumes** | the operator follows the procedure. A malicious binary run directly ignores every rule (TB-1′). Same-user code run after admission is A3 (RS-3, TG-2 unchanged). |
| **Costs** | maintaining `gov-admit` and its differential conformance suite; one extra step on first install and in image builds; channel publication of the admitter digest; image records re-provisioned with pins |

## 5. M3 — Single-valued, release-scoped registration (BC4-3)

### 5.1 Forms (owner choice OC-3)

| Form | Registration | What `release-final` can still choose |
|---|---|---|
| **E1 admission by final digest** | the RAS for sequence *n* names the exact final statement digest; a final is eligible as policy root only if admitted | nothing that becomes a policy root; the TPS surface still classifies content and computes reductions between admitted releases |
| **E2-closed** | the TPS surface registers `digests_by_sequence` (and `registered_by_sequence` for member-id sets) with closed ranges; every release sequence is registered | `project_tunable`, `release_bound` and `informational` leaves of a registered sequence (revision 4's tunable blast radius, restated) |
| **E2-open** | as E2-closed, but the last range may be open-ended | as E2-closed, plus a later-sequence final carrying the content registered in the TPS a machine holds |

### 5.2 Rules common to all forms

1. **Lint.** Two values for one (key, sequence) are malformed. Revision 4's list form with more than one digest is
   malformed (F3: exit 5).
2. **E7 at sequence *n*** uses exactly the value registered for *n*. The installed release at its own sequence keeps its
   registration, so legitimate retention does not widen later sequences (F3: 4.1.6 at sequence 6 exit 0 in both forms).
3. **Reductions.** `content_reversion` (a later sequence registers a digest superseded at an earlier one) and
   `registration_rewritten` (an already-registered sequence changes value) are computed reductions: cumulative
   `lowering_history` plus the per-project `policy_lowering` gate. F3: exit 6 without history, 0 with.
4. **Member-id sets** are single-valued per sequence in the same way.
5. **Owner-domain slots** (RV4-L10) declare binding groups registered and confirmed as one set digest. When several valid
   decision pins name different sets, the gate refuses.

### 5.3 Result (F3, executed: unmodified revision-4 checker on projections; real 4.1.5 consumer)

| Case | Revision 4 RETAIN | E2-open | E2-closed |
|---|---|---|---|
| forged 4.1.8 carrying the superseded regex, at sequence 8 | exit 0; the `ASIA…` file is indexed and retrievable | exit 3 | exit 3 |
| the same kernel presented as sequence 7 | — | exit 3 | exit 3 |
| D-A02 T1 tool descriptor, T2 invariant, T3 schema, T4 skill: mixed release at sequence 8 | exit 0 (review r4 D) | exit 3 each | exit 3 each |
| installed 4.1.6 at sequence 6; fixed 4.1.7 at sequence 7 | 0; 0 | 0; 0 | 0; 0 |
| genuine 4.1.8 with 4.1.7's content, at sequence 8 | — | exit 0 | exit 3 until a TPS registers sequence 8, then 0 |
| machine holding only TPS v1; forged 4.1.8 with 4.1.6 content | — | **exit 0** (residual) | exit 3 |
| consumption on real 4.1.5 of the content each rule set selects | indexed, retrievable | not indexed, not retrievable | not indexed, not retrievable |

### 5.4 Trust inputs, removals, additions, assumptions, costs

| | M3 |
|---|---|
| **Trust inputs** | root threshold (TPS/RAS); per-project local gate for reductions |
| **Removes** | set-valued registrations; `release-final`'s choice among registered non-orderable content; the need for retention (installed releases keep their own sequence) |
| **Adds** | sequence-scoped registration fields; single-valued lint; two reduction kinds; binding groups for owner-domain slots; under E1, RAS by final digest |
| **Assumes** | a machine that never received a later TPS cannot learn it (RS-1 unchanged; the E2-open residual is its constitutional form) |
| **Costs** | E1 and E2-closed: a root-threshold registration for every release sequence (the same ceremony as L1). E2-open: a ceremony only when content changes. More registration data in the TPS. |

## 6. HO-0001 §3 and §4, as classes

### 6.1 §3.1 Constitutional-floor closure

| Requirement | Status under the alternative |
|---|---|
| complete constitutional key inventory; default deny of unknown keys; an explicit floor mode per mutable field; coverage check failing the release | kept from revision 4 (review r4: holds; this run re-executed the self-test, 56/56, and the review-r3 injections, lattice, precedence and removal probes, identical: F0). RV4-L1 carried. |
| schema evolution cannot silently introduce an unfloored setting | kept for keys, files and precedence. **Non-orderable content:** single-valued lint and the two reduction kinds (M3). |
| tests: role→authority map; irreversible Human Gate authority; outbound and export controls; project override controls; install and update authority; exception authority; future unknown field | kept (review r4 `04`: hold) |
| tests: sensitivity and indexing exclusions | F3 part P: exit 3; the consumer excludes the `ASIA…` file |
| tests: plugin and tool permission floor | F3 D-A02 T1 (tool descriptor): exit 3 |
| forward-compatible classification (§4) | kept; binding groups for the Capability Acceptance Contract set; every new registration shape is covered by the single-valued lint |

### 6.2 §3.2 New-machine trust bootstrap

| Machine | Trust state (kept from revision 4) | TCB (M2) |
|---|---|---|
| First install | inclusion anchor; C3 needs a proof | admitter with both channels; revoked, remediated and moved-tag binaries refused (F2) |
| Clean CI runner | valid, protected pin; C3 within the window | image-time admission record with validity; the genuine binary refuses when the record has expired or the image holds its revocation (F2) |
| Restored from backup; old epoch; no epoch; two machines at different epochs; offline long absence | as revision 4 (review r4: holds) | already admitted; self-refusal once its own revocation is held; no epoch = first install |
| Safety vs freshness, gated operations, persisted monotonic state, OP-7 | as revision 4. Admission is always C3 with the channel as currency; OP-7 does not relax it. | — |
| Signed-state replay; repository gate records | as revision 4 | as revision 4 |

**Carried:** RS-2 restated (RV4-M4) and the witness input and custody rule (RV4-M3), unchanged.

### 6.3 §3.3 Binary and root authenticity

| Evaluated item | Use |
|---|---|
| threshold root signature | L1/E1: the RAS admits source and final at root threshold. Root-signed binary digests with root co-signers who reproduce is option OC-2 (d). |
| separate binary or root-bundle attestation | the reproduction quorum replaces `release-artifact` |
| certification binding | not used; certification establishes neither build nor source |
| reproducible-build or provenance evidence | the core of F-BUILD; build profile admitted with the source; F5 |
| compiled trust-state digest; binary trust-policy digest | TBM kept (A6, A7); its digest is quorum-attested and its content is part of the admitted source |
| multi-signature | the quorum across statements; root threshold; FTC enforces the minima |

| Protected asset | How |
|---|---|
| the binary | F-BUILD quorum over a digest measured by a non-candidate evaluator; install from buffer |
| compiled trust roots, minimum floors, trust-policy identity, historical-release set, trust-state and bootstrap rules | files of the admitted source (canonical content digest) reproduced under F-BUILD; TBM resolution and the accepted-TBM high-water kept |
| non-circularity | M2 base case uses the same predicate; the evaluator is never the candidate |

**Restated blast radii (BC4-4):**
- **One `release-final` key.** Under E1 it forges authentic finals that never become policy roots. Under E2 it chooses
  the tunable, `release_bound` and informational leaves of a registered sequence; Git delivery passes no gate, but E7 at
  use holds. Under E2-open, on a machine holding only an older TPS, it can also make a later-sequence final carrying that
  TPS's content eligible (F3). It never chooses non-orderable content or a binary.
- **One `build-attestation` key.** Nothing (quorum).
- **One `verification-attestation` key.** Nothing under L1 or L2.
- **`trust-state` key.** Revision 4's statement stands; for binaries it selects among legitimate, unrevoked binaries only.
- **OP-4 "no".** Changes no smallest minimal set (F1); it changes only sets of seven capabilities under L2.

### 6.4 §3.4 Legacy-binary damage containment

Unchanged: the occupation layout, LP-1 for root-anchored invocations, LR-2 bounds. Review r4 found the class property
holds. RV4-M1 and RV4-M6 are carried with their acceptance tests. M2 writes no project path. Phase 4 no longer runs a
RoT-1 binary before admission.

## 7. Kept from revision 4

Everything in review r4 CD4-0 and review r3 CD3-0, except where this document replaces it:
- **Authentication core:** compiled root chain; DSSE and GOV-JCS-1; the single `authenticate` constructor;
  VerifiedBlobs, KernelSnapshot, EmbeddedSnapshot; GovernedFs and the Protected Path Set; KS-1…KS-11, with KS-9 retired
  together with `release-artifact`.
- **Constitutional Surface:** CSI in the TPS; default deny; closed vocabulary; exact precedence registration; the
  two-directional order; the directed join; required presence; one YAML profile; Overlay Surface and migration whitelist;
  strength over effective policy.
- **Trust state:** inclusion anchors; mandatory pin validity; currency proofs; the separate witness purpose; no
  `current` label; sticky negatives; cumulative `prior_states` and `prior_policies`; lift attestation; far-future refusal;
  artefact playbook; rotation re-signing, except that build attestations are re-issued only after re-reproduction.
- **Binaries:** V8 source equality; TBM with A6 resolution and the A7 accepted-TBM high-water.
- **Authorisation:** local trust gates; repository records are requests; confinement, with CR4-B-01 carried.
- **Legacy layout and transactions** as in §6.4.

**Carried unchanged:** RV4-M1…M7 and RV4-L1…L5, L7 with review r4's acceptance tests.

**Carried items this proposal changes:**

| Item | Change |
|---|---|
| RV4-L6 | folded into AP step 8: revoked attestations do not count |
| RV4-L8 | restated in §6.3 |
| RV4-L9 | under L1 admissions are single-valued RAS, not additions to `eligibility.production_sources[]`, so the reduction rule no longer applies to them |
| RV4-L10 | binding groups (M3 rule 5) |

## 8. Rule-text consequences for D-0008 (for the synthesis architect; not drafted here)

| Rule | Consequence |
|---|---|
| new | **Derivation floor**, as §1, with the FTC and the derivation calculator as its mechanical checks |
| (6) | non-orderable registrations are single-valued per release identity; reversion and rewrite are computed reductions |
| (9) | TCB acceptance is AP: F-SRC by two independent verifications; F-BUILD by a compiled quorum of reproducers attesting their own digests; no purpose signs received bytes; exactly one production digest per final, target and profile |
| (16) | no evaluator is the candidate, first acceptance included; first admission starts a fresh VTS; a genuine binary refuses trusted operations without an Admission Record for its own digest |
| (8) extended | the TCB bytes installed are the bytes measured |
| (17) | faithful build, source legitimacy, currency and eligibility are distinct facts with distinct establishers |

## 9. New or restated residuals

| ID | Residual | Bound |
|---|---|---|
| TB-1′ | A malicious binary run directly, outside the admission procedure, ignores every rule. | Genuine binaries, including revoked ones, refuse without an Admission Record. The documented procedure never runs a candidate. |
| TB-2′ | A compromised admitted toolchain or build input yields identical malicious bytes from every honest reproducer. | The toolchain is part of the admitted source identity. Mitigation (diverse toolchains) is not specified here. |
| TB-4′ | Two compromised verification processes plus pipeline input yield an admitted malicious source (L1), or two verification keys plus pipeline input with REJECTED suppressed (L2). | F1 minimal sets; a process residual beyond key custody. |
| RS-E2o | E2-open only: a machine holding an older TPS accepts a forged later-sequence final carrying that TPS's content. | No content beyond what that TPS registered; closed by E2-closed or E1. |
| AD-1 | Both independent channels compromised. | TA-5 core (`{ch1, ch2}` in F2). |
| AD-2 | Same-user code executed before the first admission. | A fresh VTS at first admission; afterwards RS-3/TG-2. |
