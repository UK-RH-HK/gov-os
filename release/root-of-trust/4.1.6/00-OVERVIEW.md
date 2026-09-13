# Governance OS Root-of-Trust Architecture (RoT-1) — revision 2

| | |
|---|---|
| **Status** | PROPOSED — `ROOT_OF_TRUST_ARCHITECTURE_READY_FOR_INDEPENDENT_REVIEW` (not approved, not implemented) |
| Revision | **2**, amending revision 1 (`676dfce`) after independent review `1c6027c` returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| Author role | Root-of-Trust architect. **Independence note:** this revision was written in the same session that produced the independent review of revision 1, so the next review must be done by a different, fresh reviewer. |
| Date | 2026-09-14 |
| Rejected baseline | branch `release/4.1.5-rc1`, tag `v4.1.5-rc1`, commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f`, payload `release/releases/4.1.5` (release_hash `962f9848…a314b`) |
| Target | immutable PATCH candidate 4.1.6 on `release/4.1.6-rc1`, migration `M-4.1.5-4.1.6` |
| Not modified | No runtime, CLI, kernel (`framework/`), migration, tool registry, fixture, test, released payload, verifier artefact or review artefact (`release/root-of-trust/4.1.6-review/`). **D-0007 is not edited.** D-0008 and ARCH-0002 are amended in place and remain PROPOSED, pending review and approval, not active (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). Revision 1 is preserved in Git at `676dfce`. |

## Document map

| # | Output | File | Revision 2 |
|---|---|---|---|
| — | Summary, vocabulary, root cause, owner parameters | `00-OVERVIEW.md` | rewritten |
| 1 | Threat model | `01-THREAT-MODEL.md` | revised: G11–G16, A12–A15, TH-24…TH-43 |
| 2 | Privileged-ingress map | `02-INGRESS-MAP.md` | revised: I-34…I-47, mutation inventory |
| 3 | Trust-chain diagram | `03-TRUST-CHAIN.md` | revised |
| 4 | Authentication architecture | `04-AUTHENTICATION-ARCHITECTURE.md` | revised: V0–V12 |
| 5 | **Key-purpose model** | `05-KEY-MANAGEMENT.md` | rewritten |
| 6 | Bootstrap model | `06-BOOTSTRAP.md` | revised |
| 7 | Envelope and statement specification | `07-RELEASE-ENVELOPE-SPEC.md` | revised |
| 8 | `framework.lock` and trust record | `08-FRAMEWORK-LOCK.md` | revised |
| 9 | Integration requirements, error catalogue, doctor | `09-INTEGRATION-REQUIREMENTS.md` | revised |
| 10 | Retrieval-profile trust | `10-RETRIEVAL-PROFILE-TRUST.md` | revised |
| 11 | Migration plan | `11-MIGRATION-PLAN.md` | revised |
| 12 | **Acceptance-test plan** | `12-ACCEPTANCE-TEST-PLAN.md` | revised: RT-01…RT-72 |
| 13 | **Legacy-version compatibility model** | `13-COMPATIBILITY.md` | rewritten |
| 14 | Risks | `14-RISKS.md` | revised |
| 15 | D-0007 supersession | `15-D-0007-SUPERSESSION.md` | revised: rules (1)–(18) |
| 16 | ADR summary | `16-ADR-D-0008.md` | revised |
| 17 | **Monotonic trust-state model** | `17-MONOTONIC-TRUST-STATE.md` | new |
| 18 | **Verify-and-use transaction model** | `18-VERIFY-AND-USE-TRANSACTION.md` | new |
| 19 | **Eligibility and security floor** | `19-ELIGIBILITY-AND-SECURITY-FLOOR.md` | new |
| 20 | **Rollback and recovery model** | `20-ROLLBACK-AND-RECOVERY.md` | new |
| 21 | **Owner options OP-1…OP-6** | `21-OWNER-OPTIONS.md` | new |
| 22 | **Response matrix** | `22-REVIEW-RESPONSE-MATRIX.md` | new |
| — | Schemas, examples, evidence | `schemas/`, `examples/`, `evidence/` | schemas revised and added; examples regenerated; F1 added |

## 1. Executive summary

**Unchanged from revision 1**, and confirmed sound by the independent review:
- compiled public trust anchors;
- offline signing;
- a signed statement that binds every kernel file;
- authentication before any trusted write;
- a journaled install transaction;
- `framework.lock` as a record;
- post-install verification;
- the in-memory embedded baseline;
- transport independence;
- labelled development and test paths.

Together they close V-H3 and the escalation probes E1–E5.

**What the review found.** Revision 1 closed *authenticity* but not the rest of the class. Four HIGH gaps remained, each
a lower-trust, stale or unverified input producing a current higher-trust fact:

| Finding | Mistaken equivalence | Revision 2 answer |
|---|---|---|
| RV-H1 | authenticity ⇒ currency | **Eligibility** (`19`): an authentic release is the current policy root only if the root-signed Trust Policy lineage, trust state and machine record allow it. Floors come from that lineage, joined with the kernel; they never move down except by explicit, gated root-signed lowering. Historical 4.1.2–4.1.5 kernels are recognised and never eligible. |
| RV-H2 | availability ⇒ freshness | **Monotonic trust state** (`17`): a trust-state purpose publishes admissible, hash-chained state; negative facts are sticky; absence is never positive; certification needs three signatures to be visible and relaxes nothing without a freshness proof; signed references detect staleness; ingress refuses stale state. |
| RV-H3 | verification ⇒ use | **Verify-and-use** (`18`): installation writes the verified buffers; enforcement reads only a verified in-memory snapshot; secure no-follow primitives; exclusive staging and read-back; installation state machine; protected paths written only by the transaction; no cache on any trust path. |
| RV-H4 | key role ⇒ any statement | **Purposes** (`05`): nine purposes, a compiled statement-type table, root grants under mandatory separation constraints, and purpose/lineage/profile/source checks on every statement; historical identities accepted only from the binary. |

The eight MEDIUM and four LOW findings are answered in `22`. Among them: an explicit trust-format boundary executed
against the real 4.1.5 binary (`13` §3, `evidence/F1-*`), and a Protected Path Set with GovernedFs covering adoption
rollback and every CIT file operation.

**Revision 2 chain.**

```text
compiled T0 (root chain · purposes + separation · schemas · floor operators · Trust Policy · Trust State · historical registry · embedded kernel)
  → knowledge set (T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh; verified only) → effective root, policy, admissible state, negative set, staleness
  → authenticate(source): secure read-once → purpose-bound signatures → identity/lineage/promotion → content → migrations → compatibility
  → AuthenticatedRelease (memory; CI = statement digest + tree digest)
  → eligibility (E1–E9) · trust-state requirement · gates (OP-3) · install-authority floor · computed weakenings · downgrade policy
  → install transaction (stage from buffers → read-back → atomic exchange → migrations → lock commit → snapshot CI equality)
  → every process: installation state → KernelSnapshot (read once, verified, eligible) or EmbeddedSnapshot
  → effective floor = Trust Policy ⊔ policy root ⊔ overlay strengthening → consumers read snapshot bytes only
```

## 2. Inputs and method

- **The review, read in full:** report, matrices, reviews, owner-option review, attack register, acceptance criteria,
  findings, correction delta and evidence (`../4.1.6-review/`, `1c6027c`). Nothing in the review directory was changed.
- **Feasibility probe F1:** the real 4.1.5 binary run against a project written in the proposed trust format
  (`evidence/F1-format-boundary-probe.{py,json}`). It fails closed and names the required binary.
- **Source checks:**
  - `verify_kernel` and doctor D003 exist in the 4.1.2 (`8ad06be`), 4.1.3 (`26ab5b6`) and 4.1.4 (`47d8394`) sources;
  - every kernel path in the 4.1.2 and 4.1.5 payloads and `framework/` fits the ASCII tree rule;
  - floor operators align with the existing POLICY_PRECEDENCE vocabulary (`immutable`, `floor`/`ceiling` with kinds
    `level`/`radius`/`tier`/`number`/`ordered`, `additive`, `shrink_only`, `strengthen_only_bool`, `overridable`) and the
    real `AUTHORITY_POLICY.authority_levels_required` keys.
- **Examples:** schemas and examples generated and validated with `examples/make_example.py` (statement set per purpose,
  ephemeral keys, never persisted).

## 3. Vocabulary — properties kept separate

| Property | Question | Mechanism | Never implies |
|---|---|---|---|
| **Integrity** | Are these bytes identical to a reference digest? | SHA-256 file map, tree digest | who chose the digest |
| **Authenticity** | Was the reference issued by a key granted this purpose? | purpose-bound signature under the compiled root chain | goodness, currency, certification |
| **Currency / eligibility** | May this authentic release be the current policy root here, now? | eligibility predicate over T0, Trust Policy, trust state, VTS (`19` §6) | certification; authority to install itself |
| **Freshness** | Is this lifecycle fact the latest? | admissible trust state, signed references, optional expiry (`17`) | anything, when unproven: absence is never positive |
| **Byte binding** | Are the enforced bytes the verified bytes? | read-once buffers, KernelSnapshot (`18`) | — |
| **Provenance** | How was it produced and delivered? | signed fields, ledgers, logical source references | trust |
| **Authorisation** | May this actor adopt this eligible release now? | gates bound to digests, install-authority floor, computed weakenings (`04` §4) | authenticity |

## 4. Root cause

Revision 1's diagnosis of D-0007 stands (`15` §2, errors 1–8): trust by agreement, unclassified incoming material,
authorisation read from the source, a mutable cache as anchor, rules on readers not writers, and conflated vocabulary.

The review exposed a second-order form of the same mistake: **a genuine fact treated as a current fact.**
- An authentic historical kernel was treated as a current policy root.
- A genuine but stale certification was treated as current.
- Bytes verified a moment ago were treated as the bytes in use.
- A genuine key was treated as authorised for any statement type.

Revision 2 gives each its own mechanism and rule: D-0008 rules (6), (7), (8) and (9).

## 5. Owner parameters

Analysed in `21`, not approved:

| ID | Revision 2 recommended default | Security-material |
|---|---|---|
| OP-1 | 3 root keys, threshold 2; root also holds `trust-policy` | yes |
| OP-2 | custody matrix for nine purposes; `release-final` threshold 1 with equal-custody standby (threshold 2 optional) | yes |
| OP-3 | **mode A**: every production install, update and rollback gated; certification informational; known REJECTED/WITHDRAWN refused | yes |
| OP-4 | **separate `release-candidate` key** (reversed from rev 1) | yes |
| OP-5 | 180-day metadata-age warning, informational only | no |
| OP-6 | **confirm the trust root once per Verifier Trust Store** (human or pin file) | yes |

## 6. Unresolved findings

**None at the architecture level** (`22` §8). Accepted residuals are explicit and bounded (RS-1…RS-3, VR-1…VR-4,
RR-1…RR-3, LC-1…LC-3). RV-L3 (commit branch placement) and RV-L4 (record-schema status) need owner or implementation
action at approval time.

## 7. Verdict of this amendment

The recommended architecture is RoT-1 revision 2 as specified in outputs 0–22, the schemas and the examples. It keeps
every portion the independent review confirmed sound and addresses RV-H1…RV-H4, RV-M1…RV-M8 and RV-L1…RV-L4 at the
trust-class level.

`ROOT_OF_TRUST_ARCHITECTURE_READY_FOR_INDEPENDENT_REVIEW`
