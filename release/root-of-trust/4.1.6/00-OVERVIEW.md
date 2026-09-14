# Governance OS Root-of-Trust Architecture (RoT-1) — revision 3

| | |
|---|---|
| **Status** | PROPOSED — `ARCHITECTURE_REVISION_READY_FOR_REVIEW`. Not approved, not implemented, not accepted. |
| Revision | **3**, amending revision 2 (`d37b05c`) after independent review `e5a6b8a` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| Author role | Root-of-Trust architect, run AR-0001 (Phase 1, handoff HO-0001). **Independence:** this session did not author revision 1, revision 2, or either review. It is not a reviewer and does not claim acceptance. |
| Date | 2026-09-14 |
| Base | branch `phase1/rot1-r3-architect` from `71581dc` on `release/4.1.6-rc1` |
| Rejected release baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | runtime, CLI, kernel (`framework/`), migrations, tests, fixtures, capabilities, Cargo files, released payloads, verifier artefacts, review directories, D-0001…D-0007. D-0008 and ARCH-0002 are amended in place and remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). |

## Document map

| # | Output | File | Revision 3 |
|---|---|---|---|
| — | Summary | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | revised: AS-1 is the Constitutional Surface; G17–G21; A16–A17; TA-9, TA-10; TH-44…TH-66 |
| 2 | Ingress map | `02-INGRESS-MAP.md` | revised: I-48…I-60; plugins and tools as record writers |
| 3 | Trust chain | `03-TRUST-CHAIN.md` | revised |
| 4 | Authentication architecture | `04-AUTHENTICATION-ARCHITECTURE.md` | revised: V11s; authorisation with freshness and trust gates |
| 5 | Key purposes | `05-KEY-MANAGEMENT.md` | rewritten: eleven purposes; compiled whitelist; KS-8…KS-10 |
| 6 | Bootstrap | `06-BOOTSTRAP.md` | revised: binary acceptance; root plus state ceremony |
| 7 | Statements | `07-RELEASE-ENVELOPE-SPEC.md` | revised: release v3, TPS v2, TSS v2, artefact v3, build attestation |
| 8 | Layout and lock | `08-FRAMEWORK-LOCK.md` | rewritten: occupation layout; lock 3.0.0 |
| 9 | Integration requirements | `09-INTEGRATION-REQUIREMENTS.md` | revised: R-SURF, R-ANCH, R-GATE, R-ART, R-AGENT; error catalogue; D035–D037 |
| 10 | Retrieval-profile trust | `10-RETRIEVAL-PROFILE-TRUST.md` | paths updated |
| 11 | Migration plan | `11-MIGRATION-PLAN.md` | revised |
| 12 | Acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` | revised: RT-73…RT-100; RV2-A01…A36; property assertions |
| 13 | Legacy compatibility | `13-COMPATIBILITY.md` | rewritten |
| 14 | Risks | `14-RISKS.md` | revised |
| 15 | D-0007 supersession and rules | `15-D-0007-SUPERSESSION.md` | revised: rules (1)–(20) |
| 16 | ADR summary | `16-ADR-D-0008.md` | revised |
| 17 | Monotonic trust state | `17-MONOTONIC-TRUST-STATE.md` | rewritten: S1–S12; MS-8, MS-9 |
| 18 | Verify-and-use transaction | `18-VERIFY-AND-USE-TRANSACTION.md` | revised: VU-11…VU-13; transaction area; union; layout states |
| 19 | Eligibility and floor | `19-ELIGIBILITY-AND-SECURITY-FLOOR.md` | rewritten: E7 surface; effective policy; computed lowering |
| 20 | Rollback and recovery | `20-ROLLBACK-AND-RECOVERY.md` | revised |
| 21 | Owner options | `21-OWNER-OPTIONS.md` | revised: OP-7 added; OP-2, OP-3, OP-4 restated |
| 22 | Response matrix | `22-REVIEW-RESPONSE-MATRIX.md` | rewritten for review r2 |
| **23** | **Constitutional Surface** | `23-CONSTITUTIONAL-SURFACE.md` | **new** (R2-H1) |
| **24** | **Freshness anchoring and new-machine bootstrap** | `24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md` | **new** (R2-H2) |
| **25** | **Binary and trust-base authenticity** | `25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md` | **new** (R2-H3) |
| **26** | **Legacy-binary containment** | `26-LEGACY-BINARY-CONTAINMENT.md` | **new** (R2-H4) |
| **27** | **Trust-decision authorisation** | `27-TRUST-DECISION-AUTHORISATION.md` | **new** (R2-M1) |
| — | Inventory and checker | `constitutional-surface/` | **new**: inventory, library, derivation, checker |
| — | Schemas, examples, evidence | `schemas/`, `examples/`, `evidence/` | schemas revised and added; revision-2 examples superseded; P1r3, P3r3, P4r3, G1, CSI evidence |

## 1. Executive summary

The same class has rejected 4.1.3, 4.1.4, 4.1.5, revision 1 and revision 2: **a lower-trust input yielding a current,
higher-trust fact.** Revision 2's four HIGH findings were four more instances. Revision 3 treats each as a class, not as
its demonstrated example:

| Finding | Mistaken equivalence | Revision 3 answer | Evidence |
|---|---|---|---|
| R2-H1 | registered floor keys ⇒ constitutional policy | **Constitutional Surface** (`23`): the whole kernel payload, classified by a root-signed inventory; default deny; closed floor vocabulary; per-key precedence lattice; E7 surface check; joins; mechanical strengthening; consumer register | CSI check exits 0 on `framework/` (113 files) and fails the legacy payloads; self-test 26/26; **P1r3 on the real 4.1.5 binary: all three review harms flip; raised floors enforced** |
| R2-H2 | compiled or repository knowledge ⇒ current state | **Freshness anchoring** (`24`): safety separated from freshness; anchors (pin, human confirmation, witness); `freshness` axis; no trust ingress without an anchor; **OP-7** for governed use when unanchored; monotonic VTS; minimums only from the trust-state lineage | **P4r3: 34/34 scenarios**, B1–B6 flipped, machine list M1–M7 |
| R2-H3 | release key ⇒ binary authenticity | **Binary acceptance** (`25`): `release-artifact` (≥ 2) + independent `build-attestation` + trust-state reference + Trust Base Manifest resolving to root- and trust-state-signed statements; high-water | P4r3 A27–A29 variants |
| R2-H4 | sentinel read afterwards ⇒ boundary | **Legacy-path occupation** (`26`): RoT-1 authority relocated; every legacy authority path and no-install write root occupied by a wrong-typed entry; LP-1 property; project-strength vector | **P3r3 with the real 4.1.2, 4.1.3, 4.1.4 and 4.1.5 binaries: 695 invocations and 40 chains from their own `--help` registers, 0 changes**; control and ablation; G1 |

The medium and low findings are closed as classes in `17`, `18`, `19`, `20`, `05`, `12` and `27`:
- gate records as authorisation (R2-M1);
- purpose leakage (R2-M2);
- certification-only un-withdraw (R2-M3);
- equivocation (R2-M4);
- skip-version lowering (R2-M5);
- separation (R2-M6);
- long-lived snapshots (R2-M7);
- agent consumption (R2-M8);
- trust-record and recovery consistency (R2-M9);
- acceptance plan (R2-M10);
- the low findings R2-L1…R2-L3.

`22` maps every item to its change and evidence, with no "resolved" claim resting on untested evidence.

**Kept from revision 2**, as the review confirmed sound:
- compiled root chain and purpose-bound DSSE statements;
- the single authentication constructor;
- VerifiedBlobs, the install transaction and the KernelSnapshot;
- GovernedFs and the installation state machine;
- sticky negatives;
- the account-database Verifier Trust Store;
- mode A;
- OP-6 lineage confirmation;
- the separate test-profile binary.

## 2. Chain (summary; full diagram `03`)

```text
independent channels (root id, state fingerprints) ─► OP-6 + anchor (pin / human / witness)
compiled TBM (root chain · TPS with Constitutional Surface · TSS · embedded release), accepted by verify-artifact
  → knowledge (union) → effective root · TPS · TSS (resolution, orphans, equivocation, admissibility) · negatives · freshness
  → authenticate (V0–V12, V11s surface) → eligibility E1–E10 (E7 surface, E8 freshness) → local trust gate → authority
  → install transaction (trust-tx, union trust record, occupation layout, strength vector)
  → every unit of work: installation state → KernelSnapshot generation → effective policy (surface joins, precedence per key)
  → operation class C0–C3 allowed by trust state × freshness × OP-7
```

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| Integrity | Are these bytes identical to a reference digest? | file map, tree digest | who chose the digest |
| Authenticity | Was the reference issued by a key granted this purpose? | purpose-bound signatures | goodness, currency, certification |
| **Surface registration** | Is every constitutional file and leaf classified and registered by the root-signed Trust Policy? | CSI, E7 (`23`) | currency |
| Eligibility | May this authentic release be the policy root given what this machine holds? | E1–E10 | freshness; certification |
| **Freshness** | Is what this machine holds the current published state? | anchors (`24`) | anything, when unanchored |
| Byte binding | Are the enforced bytes the verified bytes, in this unit of work? | `18` | — |
| **Binary acceptance** | Is this binary the reproducible production binary of a final release? | `25` | project eligibility |
| Authorisation | May this trust transition happen on this machine now? | local trust gates, authority floor (`27`, `19` §8) | authenticity |

## 4. Root cause

Revision 1 fixed *authenticity*; revision 2 fixed *authenticity ⇒ currency* for registered keys and retained machines.
The review of revision 2 exposed the third-order form of the same mistake: **a partial mechanism treated as a total
one**:
- the keys someone registered were treated as the whole constitution;
- the knowledge a machine happens to hold was treated as the current state;
- a release key's authority was treated as binary authority;
- a marker read after acting was treated as a boundary.

Revision 3 makes each mechanism total over its class:
- every constitutional leaf, with default deny;
- every machine, by distinguishing safety from freshness and requiring anchors;
- every binary, with authentication matched to carried authority;
- every legacy command, by occupying the paths it would write rather than hoping it reads a marker.

## 5. Owner parameters (analysed in `21`; none decided)

| ID | Revision 3 proposal (labelled, not a decision) | Security-material |
|---|---|---|
| OP-1 | 3 root keys, threshold 2; root also signs the Constitutional Surface | yes |
| OP-2 | eleven purposes; `release-artifact` 2 of 2; independent rebuilder for `build-attestation`; `release-final` threshold 1 with standby | yes |
| OP-3 | mode A (local trust gates) | yes |
| OP-4 | separate candidate key | yes |
| OP-5 | 180-day warning from anchor time, informational | no |
| OP-6 | confirm once per VTS, in the same ceremony as state anchoring | yes |
| **OP-7** | **(a) anchored only** | yes |

## 6. Unresolved and not yet executable

- **Not claimed resolved.** No finding is claimed accepted. Rows whose only evidence is specification are marked so in
  `22` §10, with acceptance scenarios named. They are: VU-11, VU-12, the adapter rendering record, the union trust record,
  foreign journals, trust-gate terminal confirmation, the strength vector, the consumer register, and `verify-artifact`
  on real binaries.
- **Examples.** Revision-2 examples are superseded, not regenerated.
- **Owner decisions.** OP-1…OP-7 are pending and are answered only after fresh reviews accept revision 3.

## 7. Verdict of this amendment

`ARCHITECTURE_REVISION_READY_FOR_REVIEW`
