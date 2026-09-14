# Governance OS Root-of-Trust Architecture (RoT-1) — revision 6

| | |
|---|---|
| **Status** | PROPOSED — `ARCHITECTURE_REVISION_READY_FOR_REVIEW`. Not approved, not implemented, not accepted. |
| Revision | **6**, amending revision 5 (`cdb4e14`) after review `d1228cb` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (blocking classes BC5-1…BC5-4) |
| Author role | Root-of-trust architect, run AR-0015 (Phase 1, handoff HO-0015). **Independence:** this session authored no earlier revision, review or specialist proposal. It read review r5 and its evidence, re-ran what revision 6 relies on, and does not claim acceptance. |
| Date | 2026-09-14 |
| Base | branch `phase1/rot1-r6-architect` from `17acb8b` |
| Rejected release baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | runtime, CLI, kernel (`framework/`), migrations, tests, fixtures, capabilities, Cargo files, released payloads, verifier artefacts, review and specialist directories, D-0001…D-0007. D-0008 and ARCH-0002 are amended in place and remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). |

## Document map

| # | Output | File | Revision 6 |
|---|---|---|---|
| — | Summary | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | amended: TA-5′, TA-7, TA-12′, TA-13, TA-14; A20–A22; G23–G25; TH-101…TH-110 |
| 2–4 | Ingress map, trust chain, authentication architecture | `02`–`04` | amended: I-75…I-79, I-68; V8 source identity v2; API rules 16–18 |
| 5 | Key purposes | `05-KEY-MANAGEMENT.md` | amended: registration revocation, environment reproduction, attestation v4, KS-14, generated minima, playbooks |
| 6 | Bootstrap | `06-BOOTSTRAP.md` | **rewritten**: first-contact code and procedure |
| 7–11 | Statements, layout, integration requirements, retrieval profiles, migration plan | `07`–`11` | amended: statement set, `.gitattributes` member, requirements and codes, WP-28…WP-33, Phase 4 burden |
| 12 | Acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` | amended: §4d RT-156…RT-183; §7d review-r5 attacks; §8.2; fourteen RTs revised |
| 13–20 | Compatibility, risks, D-0007 supersession, ADR, trust state, verify-and-use, eligibility, rollback | `13`–`20` | amended: rules (6), (7), (9), (10), (12), (16), (17), (19), (22)–(24) revised and (25)–(27) added; clock text; §9.1 member and §9.2 transaction area; E7 restrictors |
| 21 | Owner options | `21-OWNER-OPTIONS.md` | **rewritten**: OP-1…OP-16 with T1-a…T1-d as OP-13 (a)–(d) and E-a…E-c as OP-16 (a)–(c); generated consequences; no proposals; unsupported combinations stated |
| 22 | Response matrix | `22-REVIEW-RESPONSE-MATRIX.md` | **rewritten** for review r5 |
| 23–27 | Constitutional Surface, freshness, admission predicate, legacy containment, authorisation | `23`–`27` | amended (`25` rewritten): verifier reductions; clock and RS-2b; AP-1…AP-6 and AP-5r; LP-1s and ignore sources |
| 28 | Class remainder analysis | `28-…` | updated: root cause of BC5-1…BC5-4; A-R6-01…15 |
| 29 | Fact derivation and selection authority | `29-…` | **rewritten**: complete decision register (35 decisions), pack checks |
| 30–31 | Registration and reproduction; independent admission | `30`, `31` | **rewritten** for revision 6 |
| **32** | **First-contact root** | `32-FIRST-CONTACT-ROOT.md` | **new** (BC5-1) |
| **33** | **Build environment** | `33-BUILD-ENVIRONMENT.md` | **new** (BC5-2) |
| **34** | **First-hand constitutional content** | `34-FIRST-HAND-CONSTITUTIONAL-CONTENT.md` | **new** (BC5-3) |
| — | Decision register and pack checks | `decision-register/` | **new**: `DECISION_REGISTER.yaml`, `register_check.py`, `statements_check.py` (BC5-4) |
| — | Checker | `constitutional-surface/` | `verify-registration`, verifier reductions, registration changes; self-test 78 cases |
| — | Schemas, examples, evidence | `schemas/`, `examples/rev6/`, `evidence/r6/` | revision-6 schemas and instances; CS6, P4r6, DA03r6, FA6, CON6, ENV6, SRC6, ADM6, UW6, ATTR6, LAY6, DA07r6, re-runs |

## 1. Executive summary

**The class.** Eight rejections (4.1.3, 4.1.4, 4.1.5, revisions 1–5) share one class: **a lower-trust input yielding a
current, higher-trust fact.** Review r5 found it in three selectors revision 5 had not assigned, and in the consequence
statements derived from its partial decision register.

**Root cause accepted** (`28` §7). FD-1 was stated as a rule but applied only to the decisions revision 5 changed. The
register was not a complete, checked artefact, so neither the calculator's strategies nor the tests saw the omitted selectors.

**Revision 6** closes the four classes, each as a class:

| Class | Selector removed | Revision-6 mechanism | Evidence |
|---|---|---|---|
| **BC5-1** first-contact root (RV5-H1) | one channel page choosing lineage (bundle order), channel quorum (read from the selected Trust Policy) and evaluator (one-channel digest) | a **first-contact code** agreed across the OP-13 sources binds a manifest `{lineage, state epoch, admitter digests}`, the only selector of all three; operator procedure FC-1…FC-3 with platform tools before any evaluator runs; **compiled quorum**, lineage from the typed value, compiled lineage under (c)/(d), **evaluator binding** (FC-4…FC-8); the remainder stated as the **first-contact root**; its composition is owner option OP-13 (T1-a…T1-d) (`32`) | **FA6** (real Ed25519): executed first-contact minima equal the calculator's for all seven OP-13 answers; every revision-6 bootstrap mutant detected; FA5 unchanged (45/45, 17/17, 26/27) |
| **BC5-2** build environment (RV5-H2) | an image record nobody established | environments registered with upstream-pinned components, established by a **first-hand environment reproduction quorum**; reproducers re-assemble; the pipeline selects nothing; the common-mode residual is owner option OP-16 (E-a…E-c) (`33`) | **ENV6** (real Rust toolchain): pipeline image, substituted component and carrier substitution refused; conflicts refuse; diversity enforced; residual rows accepted only as stated; two runs bit-identical |
| **BC5-3** registered content (RV5-H3) | CI deriving the unit map; attestations reused across candidates; E7 without restrictors | custodians **derive content first-hand**; attestations bound to **exactly the registered candidate and kernel**; **E7 applies AP-5's restrictors**; reductions computed at the verifier; security-classified changes listed per project (`34`) | **CON6** (pack checker; real 4.1.5 consumer): D-A01 parts A and B, D-A05 N3/N4, B-A06, B-A09, B-A10 refused or listed; the `ASIA…` file stays excluded; genuine releases eligible |
| **BC5-4** register and statements (RV5-M5, D-A07) | hand-written consequences over a partial register | **complete register** (35 decisions; every rule id belongs to a decision; every selector a calculator strategy; every restrictor a failing scenario); **CS6** over 11 victim classes; every consequence a **generated block** (`29`, `21`) | `register_check.py` PASS; `statements_check.py` PASS; **CS6**: 1,648 configurations, 0 invariant failures; **DA07r6**: a failing RT for every review-r5 defect |

**Carried items.** RV5-M1…M9, RV5-L1…L9, RV5-I2, CR5-B-01…12 and reviewer C's items are addressed or carried with named tests
(`22` §3–§5). Examples:
- restrictor revocation only by the registration authority (AP-5r);
- first admission defined, re-admission keeps the store, and admissions serialised;
- source identity v2;
- the `.gitattributes` member and the ignore-source condition;
- the user-writable-installation consequence restated;
- the shared vectors R1–R5 in both executors;
- root threshold at least 2;
- the clock rule and RS-2b.

**Legacy containment is not regressed.** Reviewer C's matrix, re-run on the revision-6 layout, gives 30,735 rows: property
R2-H4 0 violations, LP-1r 0 violations, 0 classifications lost. The unchanged revision-5 instruments re-run byte-identical
(CS5, P4r5, DA03r5, FA5, REG5, P1r4), and the checker's 71 revision-5 cases are identical (`22` §1).

**Kept from revision 5** (review r5 CD5-0): the BC4-1, BC4-2 and BC4-3 closures as stated; the carried closures; legacy
containment.

## 2. Chain (summary; full statement `25` §6)

```text
first-contact sources (OP-13) ── first-contact code ─► first-contact manifest {lineage, state epoch, admitter digests}
release registration (root threshold | root-granted quorum ≥ 2; append-only) ── source identity v2 · input manifest v2 ·
    environments (first-hand environment reproductions) · final · targets · verification records (first-hand, for exactly the
    candidate and kernel) · constitutional units + kernel tree digest (derived first-hand by each custodian)
reproducers (≥ q, one signature each, inputs by digest, environments re-assembled) ── confirm first-hand ──► publisher
    (E7 restrictors on registrations) ── TSS (registrations[], published_binaries[], revocations)
first binary: operator FC-1…FC-3 ─► gov-admit (FC-4…FC-8; never executes the candidate) ── admission-predicate/1 ──►
    install from buffer · admission record in the store
later binaries: admitted gov (inclusion anchor + currency proof naming the TSS) ── admission-predicate/1 ──► binary N+1
every process: root discovery (refuse inside PPS and transaction area) → installation state (closed entry sets) → admission
    record of self (GB) → effective root (FTC, KS-14) · TPS · TSS · negatives → eligibility (E7 with AP-5's restrictors and
    verifier reductions) → local trust gate → effective policy → C0–C3
```

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| Integrity | Are these bytes identical to a reference digest? | file map, tree digest | who chose the digest |
| Authenticity | Was the reference issued by a key granted this purpose? | purpose-bound signatures | selection, currency |
| Registration | Did the registration authority fix, first-hand, this release's source, inputs, environments, content and final? | release registration (`30` §5, `33`, `34`) | that the source is benign (TB-4) |
| Reproduction | Did ≥ q independent reproducers obtain these bytes in registered environments? | first-person quorum (`30` §7) | that the upstream toolchain or environment is benign (TA-12, TA-12′) |
| Eligibility | May this registered release be the policy root here? | E1–E10 with AP-5's restrictors | currency |
| Anchoring | Does the effective TSS chain through what was confirmed out of band? | inclusion (`24` §3.4) | currency |
| Currency | Is there a proof naming this TSS as published as of a stated time? | P1 naming it, P2, P3 (`24` §4.4) | "current" beyond the bound |
| First contact | Which sources select lineage, state and evaluator on a machine with no prior trust? | first-contact code over the OP-13 sources (`32`) | that those sources are uncompromised (the stated root) |
| Admission | Was this binary accepted on this machine by an evaluator other than itself? | admission-predicate/1, admission record (`31`) | protection against A3 |
| Byte binding | Are the enforced bytes the verified bytes? | `18`; installation from the buffer | — |
| Authorisation | May this trust transition happen here now? | local trust gates, protected pins, confinement | authenticity |

## 4. Root cause

`28` §7 has the account for review r5's classes; §1–§6 keep the earlier analysis.

## 5. Owner parameters (analysed in `21`; none decided, none proposed, no default)

- OP-1 root keys (threshold ≥ 2).
- OP-2 registration authority.
- OP-3 gating.
- OP-4 candidate key and remaining custody.
- OP-5 age warning.
- OP-6 lineage confirmation after admission.
- OP-7 currency without a current proof.
- OP-8 verification records per registration.
- OP-9 reproducer set and registered binary digests.
- OP-10 common-mode toolchain archive.
- OP-11 retention of superseded releases.
- OP-12 admitter form.
- **OP-13 first-contact root** (a) one source = T1-a, (b) two sources = T1-b, (c) second authentication path = T1-c, (d)
  provisioning media = T1-d.
- OP-14 workstation admission-record validity.
- OP-15 revoked running binary scope.
- **OP-16 common-mode build environment** (a) = E-a, (b) = E-b, (c) = E-c.

## 6. Unresolved and not yet executable

`22` §10:
- No implementation exists; RT-128…RT-183 need it.
- CS6, P4r6, FA6 and the reference executor are reference instruments. ENV6 models environment assembly with real toolchain
  builds, not a distribution's package infrastructure.
- Cross-OS reproducibility and root-owned install locations are specification only, as are CR4-B-02, CR4-B-04, CR4-B-05 and
  C-2…C-6.

## 7. Verdict of this amendment

`ARCHITECTURE_REVISION_READY_FOR_REVIEW`
