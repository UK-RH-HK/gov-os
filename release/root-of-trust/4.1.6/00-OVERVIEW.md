# Governance OS Root-of-Trust Architecture (RoT-1) — revision 7, certified profile CP-1

| | |
|---|---|
| **Status** | PROPOSED — `ARCHITECTURE_REVISION_READY_FOR_REVIEW`. Not approved, not implemented, not accepted. |
| Revision | **7**, a concretisation of revision 6 (`4106885`) after review `ab6b1f8` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (blocking classes BC6-1…BC6-4) |
| Owner input | OWNER-DESIGN-REQUIREMENTS-0001 (`release/orchestration/phase-1/GATES/`): **binding design inputs**, not approval of D-0008 |
| Author role | Root-of-trust architect, run AR-0019 (Phase 1, handoff HO-0019). **Independence:** this session authored no earlier revision, review or owner text. It read review r6, re-ran what revision 7 relies on, and does not claim acceptance. |
| Date | 2026-09-14 |
| Base | branch `phase1/rot1-r7-architect` from `4ed71cc` |
| Rejected release baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | runtime, CLI, kernel (`framework/`), migrations, tests, fixtures, capabilities, Cargo files, released payloads, verifier artefacts, review and alternatives directories, orchestration files, D-0001…D-0007. D-0008 and ARCH-0002 are amended in place and remain PROPOSED (`status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false`, `in_effect: false`, no `chosen_option`). |

## Document map

| # | Output | File | Revision 7 |
|---|---|---|---|
| — | Summary | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | amended: TA-5′, TA-7, TA-12″; TA-13, TA-14 removed by exclusion; TH-111…TH-119 |
| 2–4, 7, 9–11, 13, 14, 17, 23 | Ingress map, chain, authentication, statements, integration, retrieval profiles, migration, compatibility, risks, trust state, Constitutional Surface | as named | revision-7 banner: CP-1 governs; excluded-mode text is history |
| 5 | Key purposes | `05-KEY-MANAGEMENT.md` | **rewritten** for CP-1: exact shapes, three-pair whitelist, KS-15…KS-18, `first-contact-authority` |
| 6 | Bootstrap | `06-BOOTSTRAP.md` | **rewritten**: FCA, both sources, onboarding designation |
| 8 | Layout and lock | `08-FRAMEWORK-LOCK.md` | amended: signed-file sentence (CR6-C-11) |
| 12 | Acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` | amended: §4e RT-184…RT-199; §4f rows under CP-1; §4g carried items (RT-200…RT-202) |
| 15, 16 | D-0007 supersession; ADR | `15`, `16` | rules (7), (9), (10), (14)–(16), (18)–(20), (22), (23), (25)–(27) restated; (28)–(31) added |
| 18–20, 26, 27 | Verify-and-use, eligibility, rollback, legacy containment, authorisation | as named | amended: carried items CR6-C-2, C-3, C-6…C-9, C-11, C-12; E3 security minimum; gate kinds |
| 21 | Owner selections | `21-OWNER-OPTIONS.md` | **rewritten**: selections, OT-1/OT-2, review r6 option families, non-production history |
| 22 | Response matrix | `22-REVIEW-RESPONSE-MATRIX.md` | **rewritten** for review r6 |
| 24, 25 | Anchoring and currency; admission predicate | `24`, `25` | **rewritten** for OP-7 (a), R-CLK-1, AP-SEC |
| 28, 29 | Class remainder; fact derivation | `28`, `29` | updated: BC6 classes, A-R7-01…15; register over inputs, S1a/S3 |
| 30–34 | Registration; admission; first-contact root; build environment; content | as named | **rewritten** for CP-1 (BC6-1…BC6-3) |
| **35** | **Certified profile CP-1** | `35-CERTIFIED-PROFILE.md` | **new**: every selection and exclusion with its enforcement; certified targets; owner trade-offs |
| — | Profile file | `profile/CP-1.yaml` | **new** |
| — | Decision register and pack checks | `decision-register/` | register over every schema field and procedure input; C9–C11; S1a, S3 |
| — | Schemas, examples, evidence | `schemas/`, `examples/rev7/`, `evidence/r7/` | revision-7 schemas (withdrawn ones in `schemas/withdrawn-non-production/`); CS7, FA7, CUR7, ADM7, ENV7, PROF7, PPR7, DA04r7, DA05r7, DA06r7, DA09r7, BA11r7, BA12r7, crashmig7, re-runs |

## 1. Executive summary

**The class.** Nine rejections (4.1.3, 4.1.4, 4.1.5, revisions 1–6) share one class: **a lower-trust input yielding a current,
higher-trust fact.** Review r6 found it in the parties that composed, designated and submitted first-contact values (BC6-1), in
first-contact values of unbounded age (BC6-2), in the author of the environment manifest (BC6-3), and in a register complete over
rule ids instead of inputs (BC6-4).

**Root cause accepted** (`28` §11). Revision 6 checked completeness over the objects it had written, not over the values that
enter decisions and the parties that establish them; its option tree multiplied the combinations in which such a party mattered.

**Revision 7** removes the option tree and applies the owner's selections exactly, as **one certified production profile CP-1**
(`35`). It closes the four classes, each as a class:

| Class | Selector removed | Revision-7 mechanism (CP-1) | Evidence |
|---|---|---|---|
| **BC6-1** first-contact authority (RV6-H1) | the trust-state publisher composing first-contact values; carriers and unadmitted binaries designating sources and steps; a package submitter | the **First-Contact Authority record** signed at root threshold 2-of-3 after the admitter's registration, reproduction and two verification records (owner "First-contact composer/signer"); **both sources publish its code and the Trust State's code only after verifying them first-hand**; designation from the root ceremony record at onboarding; no `fc-procedure` command; platform and submitter paths excluded (`32`) | **FA7** (real Ed25519): every composition, designation and submitter case refused; executed first-contact minima equal CS7's eight root sets; the revision-6-shaped control admits |
| **BC6-2** first-contact currency (RV6-H2) | replayed, stored and designated values; re-admission ignoring the store | a **compiled 24-hour state age** on every path (OP-7 (a)); **re-admission floors** AP-R1…AP-R6 (OP-14 (b)); **R-CLK-1**; residual CUR-R1 stated exactly (`32` §8, `31` §4.1, `24` §4.5) | **CUR7**, **ADM7**, **BA11r7**: replayed and stored values refused by age; re-admission refused below held state; the 24-hour window residual exactly as stated |
| **BC6-3** environment manifest (RV6-H3) | the manifest author; supplier labels; manifest-named keys | the **environment lock in registered source**; manifests **derived** by `gov-envmanifest/1`; authoritative only with **agreeing environment reproductions and the 2-of-3 registration over that exact identity** (owner "Build-environment manifest author/signer"); supplier classes and **toolchain lineages independent by root-registered provenance** (OP-16 (b), OP-10 (b)) (`33`) | **ENV7** (real `rustc 1.98.1`): authored manifests, inline lock content, manifest-named keys, relabelled suppliers and lineages refused; label-counting controls accept injected code |
| **BC6-4** register and statements (RV6-M2, RV6-M1) | completeness over rule ids; text-only statement checks | the register is **complete over every schema field and procedure input** with its establishing party (C9–C11); statements are **checked at atom level** with an injective renderer (S1a, S3); independent detection (`29`) | `register_check.py` PASS; `statements_check.py` PASS; **DA09r7** (every held-out register mutation fails the check); **DA06r7**; **DA04r7** |

**The profile.** OP-1 root 3 keys at 2-of-3 under three custodial roles; OP-2 (b) 2-of-3 delegated registration; OP-3 Mode A;
OP-4 separate candidate key, release-final threshold 2, trust state and revocation 2-of-3, no witness; OP-5 informational 30-day
warning; OP-6 (a); OP-7 (a) with 90-day and 7-day anchors and 24-hour production currency; OP-8 = 2; OP-9 (b) + (d); OP-10 (b);
OP-11 (b); OP-12 (a); OP-13 (b); OP-14 (b); OP-15 (a); OP-16 (b). Exclusions EX-01…EX-24 are absent or refused under every
declared mechanism (**PROF7**). Certified targets need CC-1…CC-9; the initial set (x86_64 and aarch64 linux-musl) is **not
certified pending criteria**.

**Owner trade-offs surfaced, not decided** (`35` §6): **OT-1** offline media versus the 24-hour production bound; **OT-2**
feasibility of independently bootstrapped compiler agreement for the current compiler version. No owner parameter is reopened.

**The unavoidable core** (owner text, OP-7): a machine that has never received newer metadata cannot know it. CP-1 bounds and
labels it (`24` §10 RS-1; `32` CUR-R1).

**Carried items.** RV6-M3…M6, RV6-L1…L12, RV6-I1/I2, CR6-B-01…07, CR6-C-1…12, CR4-B and C-2…C-6 are closed with executed or
reference evidence, or carried with a named test (`12` §4g; `22` §3–§6).

**Legacy containment is not regressed.** Reviewer C's `matrix6` re-run: property R2-H4 0 violations (`22` §1).

## 2. Chain (summary; full statement `25` §6)

```text
root ceremony (3 keys, 2-of-3) ─► Trust Policy · First-Contact Authority record {lineage, admitter per certified target, two sources}
two sources (separate custody) ─ verify first-hand ─► trust code · state code (byte-identical)
2-of-3 registration ─ source v2 · input manifest v3 · environment lock · derived environments (agreeing reproductions) ·
    two toolchain lineages · final (2) · two verification records · first-hand content · binary digests · security flag
reproducers (2 of 3; two supplier classes; two toolchain lineages; by provenance) ─► publisher ─► Trust State (2-of-3)
first binary: FC-1′…FC-3′ ─► gov-admit (FC-4′…FC-10, AP-R1…AP-R6; 24 h) ─► install from buffer · record in the protected store
later binaries: admitted gov (anchor ≤ 90 d / 7 d; currency ≤ 24 h from both sources) ─► admission-predicate/1 ─► binary N+1
every process: root discovery → installation state → admission record · R-CLK-1 · GB-7 → effective root (CP-1 shapes) · TPS ·
    TSS · negatives → eligibility (E7, security minimum) → local trust gate → effective policy → C0-R…C3
```

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| Integrity | Are these bytes identical to a reference digest? | file map, tree digest | who chose the digest |
| Authenticity | Was the reference issued by a key granted this purpose? | purpose-bound signatures, CP-1 shapes | selection, currency |
| Registration | Did 2 of 3 custodians fix, first-hand, this release's source, inputs, environments, toolchains, content, final and binary digests? | release registration (`30` §5, `33`, `34`) | that the source is benign (TB-4) |
| Reproduction | Did 2 of 3 reproducers obtain these bytes across independent supplier classes and toolchain lineages? | first-person quorum (`30` §7) | that both classes or lineages are benign (TB-S2″, TA-12″) |
| Eligibility | May this registered release be the policy root here? | E1–E10 with AP-5's restrictors and the security minimum | currency |
| Anchoring | Does the effective TSS chain through what was confirmed out of band, within validity? | inclusion (`24` §3.4) | currency |
| Currency | Did both sources publish this TSS within 24 hours? | R-CUR-1, R-CUR-2 (`24` §4.4) | "current" beyond the bound |
| First contact | Which statements select lineage, state and evaluator on a machine with no prior trust? | FCA at root threshold; Trust State both sources publish (`32`) | that both sources are uncompromised (the stated root) |
| Admission | Was this binary accepted on this machine by the compiled admitter or an admitted binary? | admission-predicate/1, protected admission store (`31`) | protection against A3 |
| Byte binding | Are the enforced bytes the verified bytes? | `18`; installation from the buffer | — |
| Authorisation | May this trust transition happen here now? | local trust gates, protected pins, confinement | authenticity |

## 4. Root cause

`28` §11 has the account for review r6's classes; §1–§10 keep the earlier analysis.

## 5. Owner selections

Recorded in `21` §1 and enforced as `35` §2 states. Nothing in this pack decides beyond the owner text; OT-1 and OT-2 are open.

## 6. Unresolved and not yet executable

`22` §9:
- No implementation exists; RT-128…RT-202 need it. CC-1…CC-9 evidence cannot exist before implementation, so no target is
  certified.
- CS7, FA7, CUR7, ADM7, PPR7 and the reference executor are reference instruments; ENV7 builds with the real toolchain but models
  supplier and toolchain provenance; no independent compiler bootstrap was performed (OT-2).
- RV6-L1 (explicit `security_classified` per inventory row) is carried with RT-198; CR4-B-02, CR4-B-04, CR4-B-05 and C-2…C-6 remain
  specification only.

## 7. Verdict of this amendment

`ARCHITECTURE_REVISION_READY_FOR_REVIEW`
