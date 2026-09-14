# Governance OS Root-of-Trust Architecture (RoT-1) — revision 5

| | |
|---|---|
| **Status** | PROPOSED — `ARCHITECTURE_REVISION_READY_FOR_REVIEW`. Not approved, not implemented, not accepted. |
| Revision | **5**, the escalation synthesis amending revision 4 (`bca05a7`) after review `97a5545` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| Author role | Synthesis architect, run AR-0011 (Phase 1, handoff HO-0011). **Independence:** this session did not author revisions 1–4, any review, or either specialist proposal; it judged specialist A (`afda663`, AR-0009) and specialist B (`ed07926`, AR-0010) against the reviews and re-ran what revision 5 relies on. It does not claim acceptance. |
| Date | 2026-09-14 |
| Base | branch `phase1/rot1-r5-synthesis-architect` from `c8cdfac` |
| Rejected release baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | runtime, CLI, kernel (`framework/`), migrations, tests, fixtures, capabilities, Cargo files, released payloads, verifier artefacts, review and specialist directories, D-0001…D-0007. D-0008 and ARCH-0002 are amended in place and remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). |

## Document map

| # | Output | File | Revision 5 |
|---|---|---|---|
| — | Summary | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | amended: TA-1, TA-5 restated; TA-1b, TA-10′, TA-11, TA-12; A19, A20; TH-89…TH-100 |
| 2–4 | Ingress map, trust chain, authentication architecture | `02`–`04` | amended: I-69…I-74; chain of record `25` §6; API rules 13–15 |
| 5 | Key purposes | `05-KEY-MANAGEMENT.md` | **rewritten**: `release-registration`, `reproducer`; `release-artifact` and `build-attestation` withdrawn; KS-9′, KS-10′, KS-12, KS-13; Fact Threshold Check; computed minima |
| 6 | Bootstrap | `06-BOOTSTRAP.md` | **rewritten**: registration, reproduction, independent admission only |
| 7–10 | Statements, layout, integration requirements, retrieval profiles | `07`–`10` | amended |
| 11 | Migration plan | `11-MIGRATION-PLAN.md` | amended: WP-22…WP-27; Phase 3 release flow; Phase 4 via `gov-admit` |
| 12 | Acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` | amended: §4c RT-128…RT-155; §7c review-r4 attacks; §8.1 oracle |
| 13–14 | Compatibility, risks | `13`, `14` | amended; RK-38…RK-45 |
| 15–16 | D-0007 supersession, ADR | `15`, `16` | rules (5)–(24) |
| 17–20 | Trust state, verify-and-use, eligibility, rollback | `17`–`20` | amended: admissibility of registrations and published binaries; `18` §9.1–§9.2; E7 against the release's registration; CR4-B-04 |
| 21 | Owner options | `21-OWNER-OPTIONS.md` | **rewritten**: OP-1…OP-15, reconciled, no proposals |
| 22 | Response matrix | `22-REVIEW-RESPONSE-MATRIX.md` | **rewritten** for review r4 |
| 23 | Constitutional Surface | `23-CONSTITUTIONAL-SURFACE.md` | amended: **§12 release-scoped registration**; binding groups; CS-2 replaced |
| 24 | Freshness, anchoring, currency | `24-…` | amended: proofs name the state; witness input and custody; stateful clock high-water; RS-2 |
| 25 | Binary and trust-base authenticity | `25-…` | **rewritten**: admission-predicate/1 |
| 26–27 | Legacy containment, trust-decision authorisation | `26`, `27` | amended: subdirectory scope, LP-1r/LP-1s, LR-2; decision-pin maximum validity; allow-list confinement |
| 28 | Class remainder analysis | `28-…` | **updated**: accepted root cause; A-R5-01…13 |
| **29** | **Fact derivation and selection authority** | `29-…` | **new**: rule FD-1; decision register; mechanical checks |
| **30** | **Release registration and reproduction** | `30-…` | **new** (BC4-1) |
| **31** | **Independent admission** | `31-…` | **new** (BC4-2) |
| — | Checker | `constitutional-surface/` | release-scoped registration; self-test 71 cases |
| — | Schemas, examples, evidence | `schemas/`, `examples/rev5/`, `evidence/r5/` | four schemas added, eight revised; CS5, P4r5, DA03r5, FA5, SRC5, REG5, ST5, re-runs |
| — | Synthesis of the specialist alternatives | `../4.1.6-alternatives-r5/SYNTHESIS.md` | new |

## 1. Executive summary

**The class.** Seven rejections (4.1.3, 4.1.4, 4.1.5, revisions 1–4) share one class: **a lower-trust input yielding a
current, higher-trust fact.** Review r4 found three narrowed remainders (BC4-1…BC4-3) and incorrect owner-option statements
(BC4-4).

**Root cause accepted** (`28` §3). No rule classified, per trust decision, which inputs may *select* the effective fact and
at what authority and currency, and no mechanism computed the resulting minimum. Each revision therefore checked that a
lower-trust value belonged to an authorised set, or counted signatures per purpose, while a lower-trust party still chose
the member, supplied the fact a higher signer passed through, or evaluated itself.

**Revision 5** states that rule — **FD-1** (`29`) — and applies it to the three decisions that kept failing:

| Class | Selector removed | Revision-5 selector | Evidence |
|---|---|---|---|
| **BC4-1** (RV4-H1) | one `build-attestation` key + pipeline (bytes); one `verification-attestation` key (source); the release process (inputs); custodians passing through | **release registration** at root threshold or a root-granted quorum ≥ 2 (source identity, input manifest, final, targets, verification records, constitutional units) and **≥ 2 first-person reproductions confirmed first-hand** (bytes) (`30`) | **CS5**: 408 configurations, 0 invariant failures, no set with one key plus pipeline; **P4r5** VA5 rows refused; **DA03r5** |
| **BC4-2** (RV4-H2) | independent tooling A2–A6; values the candidate prints; Phase 4 self-verification; ceremonies on the unaccepted binary | **one admission predicate** run by `gov-admit` with a **fingerprint typed now**, over **measured bytes installed from the buffer**; **genuine-binary rule**; ceremonies only after admission (`31`, `25` §5) | **FA5** (real Ed25519): 45/45 scenarios, 17/17 vectors, 26/27 mutants; revision-4 paths (b) and (c) pass as controls |
| **BC4-3** (RV4-H3) | threshold-1 `release-final` choosing among registered digests | the **registration of exactly that release** fixes every non-join unit and the kernel tree; append-only; reversion, removal, narrowing are computed reductions (`23` §12) | **REG5** on real 4.1.5: the `ASIA…` file stays excluded; 15/15 mixed identities refused; legitimate releases eligible; **CSI5** 71/71 |
| **BC4-4** | hand-written consequences | OP-1…OP-15 from the calculator; no proposals (`21`) | CS5 table |

**Legacy containment is not regressed and is tightened** (carried RV4-M1): P3r3 re-run equal (2,085 jobs); across 6,292
subdirectory invocations of the real 4.1.2–4.1.5 registers, 112 wrote into the trust paths — all `COMPLETE` under revision 4,
none under `18` §9.1.

**Carried items** RV4-M2…M7, RV4-L1…L10, CR4-B-01…11 and C-2…C-6 are addressed or carried with named tests (`22` §3–§5).

**Kept from revision 4** (review r4 CD4-0): the authentication core; BC-1 closures; BC-2 closures; V8 (now a restrictor);
root-anchored containment; the carried closures. **Replaced:** revision 4's binary predicate and custodial stages.

## 2. Chain (summary; full statement `25` §6)

```text
independent channels ── root id · state fingerprints · admitter digest
release registration (root threshold | root-granted quorum ≥ 2; append-only) ── source {commit, content digest} · input manifest
    · final · targets · verification records (first-hand) · constitutional units + kernel tree digest
reproducers (≥ q, one signature each, inputs by digest) ── confirm first-hand ──► trust-state publisher ── TSS (registrations[],
    published_binaries[], revocations)
first binary: gov-admit (typed fingerprint; never executes the candidate) ── admission-predicate/1 ──► install from buffer ·
    admission record · fresh VTS
later binaries: admitted gov (inclusion anchor + currency proof naming the TSS) ── admission-predicate/1 ──► binary N+1
every process: root discovery (refuse inside PPS) → installation state (closed entry sets) → admission record of self (GB)
    → knowledge → effective root (FTC) · TPS · TSS · negatives → authenticate → eligibility (E7 against the release's own
    registration) → local trust gate → effective policy → C0–C3
```

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| Integrity | Are these bytes identical to a reference digest? | file map, tree digest | who chose the digest |
| Authenticity | Was the reference issued by a key granted this purpose? | purpose-bound signatures | selection, currency |
| **Registration** | Did the registration authority fix this release's source, inputs, final and constitutional units? | release registration (`30` §5) | that the source is benign (TB-4) |
| **Reproduction** | Did ≥ q independent reproducers obtain these bytes from the registered source and inputs? | first-person quorum (`30` §7) | that the toolchain is benign (TA-12) |
| Eligibility | May this registered release be the policy root here? | E1–E10 | currency |
| Anchoring | Does the effective TSS chain through what was confirmed out of band? | inclusion (`24` §3.4) | currency |
| Currency | Is there a proof naming this TSS as published as of a stated time? | P1 naming it, P2, P3 (`24` §4.4) | "current" beyond the bound |
| **Admission** | Was this binary accepted on this machine by an evaluator other than itself? | admission-predicate/1, admission record (`31`) | protection against A3 |
| Byte binding | Are the enforced bytes the verified bytes? | `18`; installation from the buffer | — |
| Authorisation | May this trust transition happen here now? | local trust gates, protected pins, confinement | authenticity |

## 4. Root cause

`28` has the full account; `../4.1.6-alternatives-r5/SYNTHESIS.md` §1 gives each specialist's diagnosis and the synthesis.

## 5. Owner parameters (analysed in `21`; none decided, none proposed)

OP-1 root keys; OP-2 registration authority; OP-3 gating; OP-4 candidate key and remaining custody; OP-5 age warning; OP-6
lineage confirmation after admission; OP-7 currency without a current proof; OP-8 verification records per registration;
OP-9 reproducer set and registered binary digests; OP-10 common-mode toolchain; OP-11 retention of superseded releases;
OP-12 admitter form; OP-13 channel agreement; OP-14 workstation admission-record validity; OP-15 revoked running binary scope.

## 6. Unresolved and not yet executable

`22` §10: no implementation exists; RT-128…RT-155 need it; CS5, P4r5 and FA5 are reference instruments; CR4-B-02, CR4-B-04,
CR4-B-05, C-2…C-6, cross-OS reproducibility and root-owned install locations are specification only.

## 7. Verdict of this amendment

`ARCHITECTURE_REVISION_READY_FOR_REVIEW`
