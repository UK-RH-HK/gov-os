# Governance OS Root-of-Trust Architecture (RoT-1) — revision 4

| | |
|---|---|
| **Status** | PROPOSED — `ARCHITECTURE_REVISION_READY_FOR_REVIEW`. Not approved, not implemented, not accepted. |
| Revision | **4**, amending revision 3 (`ca77a43`) after the independent review `79a09a1` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| Author role | Root-of-Trust architect, run AR-0005 (Phase 1, handoff HO-0005). **Independence:** this session did not author revisions 1–3 or any review of them. It is not a reviewer and does not claim acceptance. |
| Date | 2026-09-14 |
| Base | branch `phase1/rot1-r4-architect` from `f83da03` on `release/4.1.6-rc1` |
| Rejected release baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | runtime, CLI, kernel (`framework/`), migrations, tests, fixtures, capabilities, Cargo files, released payloads, verifier artefacts, review directories, D-0001…D-0007. D-0008 and ARCH-0002 are amended in place and remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). |

## Document map

| # | Output | File | Revision 4 |
|---|---|---|---|
| — | Summary | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | revised: G17–G19, G21 restated; G22, G23; A18; TA-7, TA-9 restated; TA-11; TH-67…TH-88 |
| 2 | Ingress map | `02-INGRESS-MAP.md` | revised: I-61…I-68; confined children |
| 3 | Trust chain | `03-TRUST-CHAIN.md` | revised |
| 4 | Authentication architecture | `04-AUTHENTICATION-ARCHITECTURE.md` | revised: V8 source equality; V11s presence, profile, exact precedence, migration whitelist; API rules 8–12 |
| 5 | Key purposes | `05-KEY-MANAGEMENT.md` | rewritten: twelve purposes; KS-11; SV-11; minimum keys re-derived; custodial rules; playbooks |
| 6 | Bootstrap | `06-BOOTSTRAP.md` | revised: attested source; protected pins; currency proof |
| 7 | Statements | `07-RELEASE-ENVELOPE-SPEC.md` | revised: `release.source`; attestation v2; build attestation v2; freshness witness; TPS schema 2.0.0 |
| 8 | Layout and lock | `08-FRAMEWORK-LOCK.md` | revised: ignore rule |
| 9 | Integration requirements | `09-INTEGRATION-REQUIREMENTS.md` | revised: R-ANCH-1…9, R-SURF-8…12, R-ART-5…7, R-CONF, R-FMT-6…7; codes; D038 |
| 10 | Retrieval-profile trust | `10-RETRIEVAL-PROFILE-TRUST.md` | revised: currency; confined plugins |
| 11 | Migration plan | `11-MIGRATION-PLAN.md` | revised: WP-20, WP-21; WP-18 re-issued migrations |
| 12 | Acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` | revised: property assertions only; RT-101…RT-127, RT-50b; every review-r3 attack mapped; conformance oracle with mutants |
| 13 | Legacy compatibility | `13-COMPATIBILITY.md` | revised |
| 14 | Risks | `14-RISKS.md` | revised: RK-31…RK-37 |
| 15 | D-0007 supersession and rules | `15-D-0007-SUPERSESSION.md` | revised: rules (1)–(21) |
| 16 | ADR summary | `16-ADR-D-0008.md` | rewritten |
| 17 | Monotonic trust state | `17-MONOTONIC-TRUST-STATE.md` | rewritten: inclusion anchors in S4; MS-2 lift attestation; MS-9 currency; clock; playbooks; blast radius |
| 18 | Verify-and-use transaction | `18-VERIFY-AND-USE-TRANSACTION.md` | revised: VU-14; C-2…C-4 |
| 19 | Eligibility and floor | `19-ELIGIBILITY-AND-SECURITY-FLOOR.md` | rewritten: registered precedence; directed join; E7/E8; weakening over effective policy; reductions in both directions |
| 20 | Rollback and recovery | `20-ROLLBACK-AND-RECOVERY.md` | revised: reinstall identity from the VTS record; RR-2 |
| 21 | Owner options | `21-OWNER-OPTIONS.md` | rewritten: OP-2 (source authority), OP-3, OP-4, OP-7 restated from corrected rules |
| 22 | Response matrix | `22-REVIEW-RESPONSE-MATRIX.md` | rewritten for review r3 |
| 23 | Constitutional Surface | `23-CONSTITUTIONAL-SURFACE.md` | rewritten: presence, YAML profile, exact precedence, two-directional order, Overlay Surface, owner domain |
| 24 | Freshness, anchoring and currency | `24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md` | rewritten: inclusion, pin validity and integrity, currency proof, witness purpose, confinement |
| 25 | Binary, built-source and trust-base authenticity | `25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md` | rewritten: attested source, A4a/A4b, A7, custodial stages, minimum capability sets |
| 26 | Legacy-binary containment | `26-LEGACY-BINARY-CONTAINMENT.md` | revised: LR-2 restated; ignore rule; strength over effective policy |
| 27 | Trust-decision authorisation | `27-TRUST-DECISION-AUTHORISATION.md` | revised: protected expiring decision pins; typed state fingerprint; confinement |
| **28** | **Class remainder analysis** | `28-CLASS-REMAINDER-ANALYSIS.md` | **new**: why BC-1…BC-3 survived; removal versus condition; architect self-attacks A-R4-01…A-R4-08 |
| — | Inventory and checker | `constitutional-surface/` | rewritten: `floor_schema_version` 3; `check`, `check-owner`, `reductions`, `selftest` (56 cases) |
| — | Schemas, examples, evidence | `schemas/`, `examples/rev4/`, `evidence/` | schemas revised and added; revision-4 examples validated; P1r4, P4r4, VA4, LR2, P3r3 re-run, review-probe re-runs |

## 1. Executive summary

**The class.** One class has rejected 4.1.3, 4.1.4, 4.1.5 and RoT-1 revisions 1, 2 and 3: **a lower-trust input
yielding a current, higher-trust fact.**

**Why revision 3 fell short.** Its three HIGH findings were narrowed remainders of the revision-2 classes. Each earlier
revision had added correct conditions downstream of a choice that a lower-trust party still made (`28`).

**Revision 4's approach.** It removes those inputs from the decision instead of adding conditions over them:

| Class | Mistaken equivalence (review r3) | Revision 4 answer: the input removed | Evidence |
|---|---|---|---|
| **BC-1** (RV3-H1) | *a rule that refuses more project overrides is at least as strong; every present leaf classified means the constitution is in force* | **The kernel no longer takes part in effective precedence:** POLICY_PRECEDENCE must equal its root-signed registration, and the project layer's rule comes only from registrations. **Absence no longer changes semantics:** registered content must be present. The project layer is a **directed join**, and a sound two-directional order makes a TPS removal of strengthening a gated reduction. **Project strength is evaluated over effective policy**, not overlay bytes. Migrations write only root-registered targets. | **P1r4 on real 4.1.5:** all 9 attack cases (5 modes, the review example, deletion, 2 TPS tightenings) lose strengthening under revision 3 and keep it under revision 4; harms (a) authority, (b) indexing, (c) gate flip; 0 unsound order pairs; the strength vector reports every revision-3 loss. Checker: framework exit 0, precedence-only kernels exit 3, deletions exit 2. **CSI self-test 56/56.** |
| **BC-2** (RV3-H2) | *an anchor number is met, so the anchored state is in force; anchored once means current* | **The supplier's sequence number** no longer satisfies an anchor: satisfaction is by inclusion only. **"Anchored once"** is no longer currency: pins expire, and every trust ingress and binary acceptance needs a currency proof (recent anchoring event, in-gate typed fingerprint, or ≥ 2 witness keys). **The trust-state key** cannot witness (a separate purpose). **The governed account** cannot write honoured pins (integrity predicate, confined repository commands). No surface says `current`. | **P4r4: 54/54 scenarios; 9/9 conformance-oracle mutants detected** (sequence anchors fail 3 scenarios); matrix of 132 rows: 77 refused, 42 stated core, 13 OP-7 (d) residual, 0 unstated, 0 labelled `current` |
| **BC-3** (RV3-H3) | *reproduced from the named commit, therefore built from verified source* | **`release-final` no longer chooses the binary's source:** the source is the one an independent verification attested for the candidate, and it must be equal in candidate, final (V8), build attestation and Trust Base Manifest. `verify-artifact` A4a/A4b and every custodian check it. | **VA4: 16/16** as expected. RV3-B-A08, its REJECTED variant and RV3-D-A03 are refused. Minimum sets stated: route S needs 3 keys + pipeline input (2 under OP-4 "no"); route B needs 4 keys over 3 purposes. |
| **BC-4** | OP-2, OP-4 and OP-7 consequence statements materially incorrect | Restated from the corrected rules, with evidence per consequence. OP-2 gains the binary source-authority choice (S0–S3). OP-7 gains pin-currency parameters, a witness authority above one key, and (d) scoped to the newest TSS. | `21`; VA4 routes; P4r4 matrix |

**Legacy containment is not regressed.** P3r3 was re-run unchanged on the real 4.1.2–4.1.5 binaries, and its summary,
property and chain results equal the committed ones. Reviewer C's 84 destructive invocations write nothing. Residual
LR-2 is restated with its reachable outcome after occupation removal or a Git restore; RoT-1 fails closed on all 24
resulting trees (`LR2`). The untracking idiom no longer drops the migration occupation.

**Medium and low findings** are addressed or carried with named tests in `17`, `19`, `20`, `23`–`27` and `12`:
- lift attestation (RV3-M1);
- pin integrity and confinement (RV3-M2);
- clock high-water (RV3-M3);
- artefact playbook (RV3-M4);
- migration whitelist (RV3-M5);
- LR-2 (RV3-M6);
- presence and owner files (RV3-M7);
- accepted-TBM high-water (RV3-M8);
- acceptance plan (RV3-M9);
- RV3-L1…L8, CR-01…CR-12 and C-1…C-5.

`22` maps every item to its change, file and evidence.

**Kept from revision 3** (CD3-0):
- the authentication core;
- the CSI as a root-signed section with default deny;
- release-local references, equivocation and computed lowering;
- no trust ingress without an anchor;
- local confirmations;
- `release-artifact` ≥ 2 with build attestation and TBM;
- the occupation layout and LP-1;
- the transaction area and union records.

## 2. Chain (summary; full diagram `03`)

```text
independent channels (root id, state fingerprints) ─► OP-6 + anchor (protected valid pin / human / in-gate fingerprint)
compiled TBM v2 (root chain · TPS with Constitutional Surface · TSS · embedded release · binary.source), accepted by
  verify-artifact (A4a/A4b attested source · A7 accepted-TBM high-water · A9 currency proof)
  → knowledge (union; future statements refused) → effective root · TPS (reductions both directions) · TSS (anchors by
    INCLUSION; unchained never effective) · negatives (lift attestation) · freshness · currency
  → authenticate (V0–V12; V8 source equality; V11s presence, YAML profile, exact precedence, migration whitelist)
  → eligibility E1–E10 (E7 surface; E8 KNOWN + ANCHORED/WITNESSED + currency proof) → local trust gate (typed fingerprint
    or protected expiring decision pin) → authority → confined children only after decisions
  → install transaction (trust-tx, union record, occupation layout + ignore rule, strength vector over effective policy)
  → every unit of work: installation state → snapshot generation → effective policy (floor joins; registered precedence
    ⊔ held registration; directed project join; registered-relaxable exceptions only)
  → operation class C0–C3 allowed by trust state × freshness × currency × OP-7
```

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| Integrity | Are these bytes identical to a reference digest? | file map, tree digest | who chose the digest |
| Authenticity | Was the reference issued by a key granted this purpose? | purpose-bound signatures | goodness, currency, certification |
| Surface registration | Is every constitutional file and leaf classified, present and registered, with precedence equal to its registration? | CSI, E7 (`23`) | currency |
| Eligibility | May this authentic release be the policy root given what this machine holds? | E1–E10 | freshness; certification |
| **Anchoring** | Does the effective TSS chain through what was confirmed out of band? | inclusion (`24` §3.4) | currency |
| **Currency** | Is there a proof that this was the published state as of a stated time? | P1/P2/P3 (`24` §4.4) | "current" beyond the bound |
| Byte binding | Are the enforced bytes the verified bytes, in this unit of work? | `18` | — |
| Binary acceptance | Is this binary the reproducible production binary of a final release, **built from attested source**? | `25` | project eligibility |
| Authorisation | May this trust transition happen on this machine now? | local trust gates, protected pins, confinement, authority floor (`27`, `24` §3.5, `19` §8) | authenticity |

## 4. Root cause

`28` has the full account. In summary:
- Revision 1 fixed *authenticity*.
- Revision 2 fixed *authenticity ⇒ currency* for registered keys and retained machines.
- Revision 3 made each mechanism total over its class, but evaluated the checks over values a lower-trust party chose:
  - the kernel's precedence rules;
  - the supplier's sequence numbers;
  - the release signer's commit name;
  - files the governed account could write.

Revision 4 moves every such decision onto inputs that party cannot choose:
- registrations signed at root threshold;
- inclusion of an out-of-band anchor;
- proofs of currency with stated bounds;
- the source an independent verification attested;
- pins outside the governed account's reach.

It lists what still enters from outside the root threshold, and how each is bounded (`28` §3).

## 5. Owner parameters (analysed in `21`; none decided)

| ID | Revision 4 proposal (labelled, not a decision) | Security-material |
|---|---|---|
| OP-1 | 3 root keys, threshold 2. Root also signs the Constitutional Surface, exact precedence, the Overlay Surface, owner-domain slots, bootstrap parameters and, under (S1), production sources. | yes |
| OP-2 | Twelve purposes; `release-artifact` 2 of 2; independent rebuilder; `release-final` threshold 1 with standby; `verification-attestation` threshold 1. **Binary source authority (S1), root-registered production sources.** | yes |
| OP-3 | mode A: local trust gates with typed state fingerprint; protected expiring decision pins | yes |
| OP-4 | separate candidate key | yes |
| OP-5 | 180-day warning from the latest anchoring event, informational | no |
| OP-6 | confirm once per VTS, in the same ceremony as state anchoring | yes |
| OP-7 | **(a) anchored only**, `pin_max_validity_days` 30, `c3_currency_window_hours` 168; witness threshold 2 if (c) | yes |

## 6. Unresolved and not yet executable

- **Not claimed resolved.** No finding is claimed accepted. Rows whose only evidence is specification are marked so in
  `22`, with acceptance scenarios named:
  - write confinement and the pin integrity predicate on real platforms;
  - the in-binary surface evaluator, directed join, strength vector and consumer-register build;
  - `verify-artifact` and its custodial stages;
  - reinstall identity from the VTS record;
  - C-2, C-4 and C-5.
- **Model probes.** Reviewer B's reference model and synthesis D's oracle probe model revision-3 functions. Their
  constructions are re-encoded as P4r4 scenarios, not re-run unmodified (`22` §1.1).
- **Examples.** Examples cover the new record shapes and statement fragments. No full signed release, TPS or TSS example
  is produced.
- **Owner decisions.** OP-1…OP-7 are pending and are answered only after fresh reviews accept revision 4.

## 7. Verdict of this amendment

`ARCHITECTURE_REVISION_READY_FOR_REVIEW`
