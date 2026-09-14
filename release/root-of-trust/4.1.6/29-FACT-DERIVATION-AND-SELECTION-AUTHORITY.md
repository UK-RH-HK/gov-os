# Output 29 — Fact derivation and selection authority (rule FD-1)

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 5. It states, as one rule with mechanical checks, the property whose absence let the same rejection
> class survive four revisions: **a lower-trust input yielding a current, higher-trust fact** (D-0007). It combines
> specialist A's selection-authority invariant (SEL-1) and specialist B's derivation floor
> (`4.1.6-alternatives-r5/SYNTHESIS.md` §1). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Why a rule about facts

Every revision so far applied D-0007 to **inputs**: each statement was verified for its purpose and threshold, and each
constitutional file was classified. The facts that decisions consume were still derived from those inputs through three
shapes that no rule forbade:

| Shape | What happened | Findings |
|---|---|---|
| **Selection from an authorised set** | an authority approved a set; a lower-trust party chose which member became effective | RV4-H3 (registered digests), RV3-H2 (TSS satisfying an anchor), R2-H2, RV4-M3 (witness input), RV4-L10 (several valid pins) |
| **Pass-through** | a higher-threshold signer signed a fact it did not establish, so a lower-threshold establishment rode on it | RV4-H1 (custodians), RV3-H3 (artefact signers over a named commit), RV4-D-A07 (root co-signature) |
| **Evaluator inside the object** | the object whose trust was being decided evaluated, or supplied the bytes for, its own acceptance | RV4-H2 (first binary, Phase 4, ceremonies), RV-H3 (verified bytes are not the bytes used) |

## 2. The rule

**FD-1 (fact derivation and selection authority).** For every trust decision *D* that confers authority α(*D*) and currency
κ(*D*):

1. **Roles.** Every input of *D* has exactly one role in the compiled decision register (§4):
   - a **selector**: its value determines which of several authentic candidates becomes the effective fact (a binary, a
     source, build inputs, a trust state, constitutional content, an anchor, an installation state, an owner-file set);
   - a **restrictor**: it can only refuse, or strengthen through a monotone join;
   - a **carrier**: it transports bytes whose identity a selector already fixed.
2. **Selector authority.** Every selector MUST have authority ≥ α(*D*) and currency ≥ κ(*D*) (§3). Restrictors may come from
   any authenticated input. Carriers may come from anywhere.
3. **First-hand establishment.** A signature contributes to a selector's authority only for a fact its signer established
   itself. A signature over a fact received from another party adds nothing (no pass-through purposes).
4. **No self-evaluation.** The artefact under judgement is never a selector, and never the evaluator of its own acceptance.
   No trust ceremony runs on a binary that has not been accepted by an evaluator other than itself.
5. **Shortfall.** A decision whose selector cannot be supplied at the required authority and currency fails closed, unless the
   pack states the shortfall as a residual with an exact bound, a label on every surface that shows the state, and an
   acceptance test that fails when the bound is exceeded.

**FD-2 (derived strength).** The strength of a fact is the minimum, over every input that can change or select it, of that
input's authority. Where a derivation can be enumerated, the minimum is **computed**, never argued (FD-3).

**FD-3 (computed minima).** Every statement of the pack of the form "an accepted malicious binary needs at least …" MUST be
the output of the derivation calculator (§5.3) for the stated owner answers, with pipeline and infrastructure inputs as
atoms. Hand-enumerated routes are not evidence.

## 3. Authority and currency

**Authority** (highest first):

| Rank | Authority |
|---|---|
| 1 | the root threshold |
| 2 | a quorum of at least two distinct keys of one purpose whose keys hold no other purpose, each establishing the fact first-hand; or local machine authority: a human typing a value read now from an independent channel, a protected operator pin within its validity, a local confirmation |
| 3 | one key of one purpose |
| 4 | the repository writer, project configuration, the governed account |
| 5 | transport, unauthenticated input, the artefact under judgement |

**Currency** (highest first): established now (typed in the gate) > within a stated window (P1 pin or confirmation naming
that state; P3 witnesses) > as of a past anchor or compiled state > none.

Custody independence (different people, organisations, build environments) is not verifier-checkable at any rank. It is a
stated assumption (TA-4, TA-10′, TA-11) wherever a rank relies on it.

## 4. Decision register (compiled; R-SEL-1)

The register lists every trust decision with its selectors, restrictors and carriers. The rows below are the decisions
whose selectors revision 5 changes or states for the first time; the full register is a compiled table of the binary.

| Decision (confers) | Selectors (authority, currency) | Restrictors | Carriers | Specified in |
|---|---|---|---|---|
| **TCB acceptance** of binary *B* (T0) | source identity and build-input manifest: the **release registration** (rank 1, or rank 2 under OP-2 (b)); bytes: **first-hand reproduction quorum** ≥ 2 (rank 2); publication and negatives: the **selected Trust State** (running: inclusion anchor + currency proof; first admission: typed fingerprint) | REJECTED verification attestation; revocations; `min_binary_version`; accepted-TBM high-water; TBM consistency; the release-final signature; OP-8 verification records | Git host, pipeline, mirrors, bundles, download host | `30`, `25` §5, `31` |
| **Evaluator of TCB acceptance** | the admitted `gov` (binary N for N+1), or the independent executor `gov-admit` whose own digest is registered, reproduced and compared with the channels | — | — | `31` §3–§4 |
| **Bytes that run as `gov`** | the bytes the evaluator measured (installed from its buffer) | TCB-location predicate for C3 (CR4-B-01 (b)); the genuine-binary rule | file system | `31` §4–§5 |
| **Current trust state** (C3) | inclusion anchor plus a currency proof that names the selected TSS (P1 naming it, P2, P3) | negatives; admissibility; equivocation | repository, bundle, transport | `24` §3.4, §4.4 |
| **Policy root eligibility** of release *R* (T1-E) | the **registration of R** referenced by the effective TSS (exact per-release unit map and kernel tree digest) | floors (join with the effective TPS); registered precedence; E3/E4/E9/E10 | kernel payload, Git delivery | `23` §12, `19` §6 |
| **Effective non-orderable value** of a unit | the registration of the release that is the policy root; else the registration of the running binary's embedded release; else `SURFACE_VALUE_UNAVAILABLE` | consumer register fail-closed meaning | kernel bytes | `23` §12.3, `19` §5.2 |
| **Owner constitutional file set** | a local confirmation or protected decision pin naming the **binding-group digest** | exact set match only | repository | `23` §7.2 |
| **Installation state** `COMPLETE` | the closed entry sets recorded by the install transaction (trust top level, kernel content set, statement directories, occupation directory) | nested legacy markers | working tree | `18` §9 |
| **Project root for a command** | the nearest ancestor holding `governance/trust/FORMAT` | refusal inside the Protected Path Set | working directory | `18` §9 |
| **Witnessed state** (OP-7 (c)) | the owner's signing ceremony or the independent channel | witness key custody (two custodians) | Git host, bundle | `24` §3.3 |
| **Migration content** | the registration of the release that carries it | Overlay Surface whitelist; strength vector; CR4-B-04 pre-transaction requirements | release payload | `23` §11–§12, `19` §9 |

## 5. Mechanical checks

### 5.1 In the binary (R-SEL-1 … R-SEL-4)

| ID | Rule | Test |
|---|---|---|
| R-SEL-1 | The binary compiles the decision register: for every E1–E10 condition, every AP step (`25` §5), every anchor, currency and gate decision, and installation-state determination, its selectors with their authority and currency, its restrictors and carriers. | RT-128 (register present; each decision of §4 listed) |
| R-SEL-2 | A decision reads a selector only through a type constructible from the registered source (`Selected<T>`), as `Anchor` and `PrecedenceRule` already are (ARCH-0002). | RT-128 (compile-fail tests for an unregistered source) |
| R-SEL-3 | A new decision, or a new input of an existing decision, fails the build until it is registered (the counterpart of the consumer register, `23` §6.5). | RT-128 |
| R-SEL-4 | The conformance oracle has, for each registered selector, a mutant that substitutes the next-lower-authority input, and a distinguishing scenario. | RT-129; `evidence/r5/DA03r5-*` |

### 5.2 On every root version: the Fact Threshold Check (FTC; `05` §3)

SV-4 refuses a root version (`ROOT_VERSION_INVALID`) when its grants give a fact-establishing purpose less than its compiled
minimum or let its keys hold another purpose: KS-9′ (reproducer quorum ≥ 2, single purpose), KS-10′ (registration threshold
≥ 2; root keys at root threshold or single purpose), KS-12 (verification keys are neither reproducer nor registration keys),
KS-13 (withdrawn purposes never granted). Owner options raise these minima, never lower them.

### 5.3 Before a root ceremony: the derivation calculator (FD-3)

`gov trust draft-policy --derivation` enumerates every capability subset of the owner's registered release-process model,
with honest parties acting only on first-hand checks, and computes the minimal capability sets for each attack goal and
victim class. It fails the draft when a minimal set violates the stated minima (invariants INV-BYTES, INV-SRC, INV-INPUTS,
INV-MIRROR, INV-ONE of `evidence/r5/CS5-tcb-capability-sets.py`). Its output is the consequence table of `21`.

**Reference result (revision-5 rules, `evidence/r5/CS5-tcb-capability-sets.json`):** 408 configurations (OP-2 × OP-8 ×
OP-9 × four victim classes × five goals, plus OP-10 for the toolchain goal), enumeration complete to size 10, 21 of 21
self-checks, 1,752 invariant checks with 0 failures, 138,042 monotonicity checks with 0 violations. Controls show that three
rules are load-bearing: reproductions reaching the publisher through the pipeline give {pipeline, 2 reproducer keys};
inputs fetched from a CI-named mirror give {mirror}; custodians naming a digest handed to them (the D-A07 shape) give
{pipeline, 2 reproducer processes}.

### 5.4 Conformance oracle (RV4-M7, review r4 §7 criterion 4)

`evidence/r5/P4r5-conformance-oracle.py` contains no expected-`ACCEPTED` row that is an attack; accepted attack sets live
only in the calculator. `evidence/r5/DA03r5-oracle-regression-sensitivity.py` re-runs review r4's twenty single-rule mutants
and seventeen mutants of the revision-5 rules against it (`22` §1).

## 6. What FD-1 removes in each persistent class

| Class | Selector below authority in revision 4 | Revision 5 selector | Specified in |
|---|---|---|---|
| BC4-1 | one `build-attestation` key plus pipeline (bytes); one `verification-attestation` key (source); the release process (build inputs); custodians passing through | registration at rank 1 or 2 (source, inputs, content, final); ≥ 2 first-hand reproductions (bytes); `release-artifact` and `build-attestation` withdrawn | `30` |
| BC4-2 | transport and the candidate (which binary, which statements, what it prints, which ceremonies it runs) | a fingerprint typed now (rank 2, currency now) selects state; `gov-admit` (not the candidate) evaluates; the measured bytes are installed; ceremonies only on admitted binaries | `31` |
| BC4-3 | threshold-1 `release-final` choosing among registered digests | the registration of exactly that release selects every non-orderable unit | `23` §12 |
| BC4-4 | hand-written consequence statements | calculator output and executed probes | `21`, `25` §7 |

## 7. Residuals admitted under FD-1 §2 (5)

Each is stated with its bound, label and test where it is defined: RS-1, RS-1b, RS-1c, RS-2 (restated), RS-3…RS-5 (`24`
§10); RS-B1 channel currency and AD-1, AD-2, TB-1′ (`31` §9); TB-4, TB-4′, TB-S1…TB-S3 (`30` §12); CS-1 (`23` §10); VR-, RR-,
LR-, TG- residuals (`18`, `20`, `26`, `27`).
