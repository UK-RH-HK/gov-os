# 04 — HO-0001 §3–§4 owner requirements and owner options (AR-0004)

Each requirement is judged as a class: `SATISFIED` or `NOT SATISFIED`. Sub-items show the evidence. A class is
`SATISFIED` only if every sub-item holds under this review's and the panel's attacks, or its gap is a bound, carried
requirement.

## 1. Requirements

### §3.1 Constitutional-floor closure (R2-H1) — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| complete constitutional key inventory | holds | CSI `framework/` 113 files, 4.1.5 payload 121, exit 0 (reproduced) |
| default-deny handling of unknown new constitutional keys | holds for additions | S01–S03 (reproduced); B I01–I06; D-A09 F12 |
| explicit floor mode for each mutable constitutional field | **fails for precedence** | the precedence floor mode's order is unsound (D-A01) |
| coverage check fails the release if a field lacks floor semantics | holds for additions; **fails for absence** | D-A10: nine registered files removed, exit 0 |
| schema evolution cannot silently introduce an unfloored setting | **fails** | kernel move to `immutable` (RV3-B-A01), POLICY_PRECEDENCE deletion (D-A10 R07), TPS tightening (D-A02): each silently removes project strengthening |
| test: role → authority map | holds for kernel values | S04–S06; P1r3 T1 and harm (a) (reproduced) |
| test: sensitivity and indexing exclusions | **fails for project-owned exclusions** | RV3-B-A01 (b), executed |
| test: irreversible Human Gate authority | **fails for project narrowing** | RV3-B-A01 (c), executed |
| test: plugin and tool permission floor | holds (checker) | S10, S17 |
| test: outbound and export controls | holds (checker) | S11 |
| test: project override controls | **fails** | D-A01, D-A02, D-A10 R07; RV3-B-A01 |
| test: install and update authority | holds for kernel; project raises lost | S15; RV3-B-A01 (a) |
| test: exception authority | holds | S16; P1r3 T8 |
| test: a future unknown constitutional field | holds | S01–S03; D-A09 |

### §3.2 New-machine trust bootstrap (R2-H2) — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| first install | **fails** | `24` §5.1 says `BELOW_ANCHOR` when withheld, but the axis definition is sequence-based: one trust-state key satisfies the human anchor (RV3-B-A12; D-A12) |
| clean CI runner | **fails** | stale pin stays `ANCHORED`, `current` permitted (RV3-B-A02); trust-state key (D-A12); revoked binary re-accepted (D-A15) |
| machine restored from backup | holds as stated | anchor age shown; (b) refuses by age (P4r3 M3) |
| old trust epoch | holds as stated | P4r3 M4 |
| no trust epoch | holds under (a)–(c); (d) labelled | P4r3 M5; B matrix |
| two machines at different epochs | holds | P4r3 M6 |
| offline machine after a long absence | holds with age shown | P4r3 M7; the (c) text conflict is RV3-L1 |
| safety distinguished from freshness | holds structurally | `24` §2 |
| attacker selecting old signed state cannot create a current fact | **fails** | RV3-H2 |
| what is safe, gated, witness-bound, persisted; OP-7 effect | **fails for witness authority and OP-7 effects** | RV3-B-A06; §2 below |
| signed-state replay | holds | P4r3 R1, R2 |
| gate records supplied from repository state | holds (records are requests); same-account pins carried | model P2; RV3-M2 |
| OP-7 not decided | holds | `21`; D-0008 has no `chosen_option` |

### §3.3 Binary and root authenticity (R2-H3) — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| options evaluated (threshold root signature, attestation, certification binding, reproducible build, compiled state and policy digests, multi-signature) | holds | `25` §2 |
| protect the binary | **fails** | built source unbound (RV3-B-A08; D-A03) |
| protect compiled roots, floors, policy identity, historical set, trust state and bootstrap rules | holds against substitution | A6 resolution, A7 high-water (subject to RV3-M8) |
| a single lower-threshold key cannot mint a malicious binary | **fails** | `release-final` plus pipeline input gives `ACCEPTED` |
| non-circular chain | holds | `25` §6 |

### §3.4 Legacy-binary damage containment (R2-H4) — **SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| new-format projects mechanically hostile; V3 evaluated and extended | holds | P3r3 L3 against L3A (reproduced) |
| kernel, legacy lock, trust, rollback, reinstall, init-force and migration paths | holds on the intact layout | P3r3 695 invocations + 40 chains; C 84 invocations: 0 changes |
| no dependence on old binaries understanding RoT-1 | holds | registers derived from each binary's `--help`; class argument `26` §3 |
| a pre-RoT binary cannot silently mutate the new kernel or trust state into a state **it** then treats as valid | holds on the intact layout | after explicit removal or a Git restore of pre-migration paths, the legacy binary operates a legacy layout it treats as valid and can write RoT-1 paths (C A05; D-A05, D-A06), while RoT-1 binaries fail closed. This is the explicit-restoration boundary, carried as RV3-M6. |

### §4 Forward-compatibility constraint — **SATISFIED for classification**

| Future artefact | Result | Evidence |
|---|---|---|
| Capability Acceptance Contract: hash-bound Markdown and compiled YAML | classified by data; edits and consistent replacement refused | D-A09 F09–F11; S22 |
| Gate W artifact-flow policy (manifests, receipts, lineage) | keyed requirement collection, receipt-field floor and strict booleans by data; weakening refused | D-A09 F01–F05 |
| G0–G6 scheduler | pinned durations, a new severity order inline; weakening refused | D-A09 F06–F08 |
| new key beside a `project_tunable` leaf | default deny | D-A09 F12 |

**Qualification.** Two open items apply to new constitutional files as well: RV3-H1's order and RV3-M7's absence semantics. Non-kernel owner files lack a reference evaluator (D-A18, carried).

## 2. Owner-option combinations that change security (RV3-D-A08)

| Answer set | Security consequence (from the rules as written) | Pack statement | Determination |
|---|---|---|---|
| OP-7 (a) (proposed) | CI runners are anchored by pins with no currency bound; A2 selects any genuine state ≥ the pin epoch. A trust-state key bypasses a current pin (sequence anchors). Revoked policy roots and binaries are accepted. | "makes the review's B5 class impossible on every machine" (`24` §9; `21`) | **incorrect** (RV3-B-A02, A12; D-A12, A15) |
| OP-7 (b) | age-bounded C2/C3; one far-future `issued_at` permanently disables it | "bounds staleness by time" | correct once CR-06 holds |
| OP-7 (c) × OP-2 `trust-state` threshold 1 (scheduled custody) | a thief mints witnesses; stateless runners are `WITNESSED` for C0–C3 | "staleness bounded by the expiry window"; `17` §15 "freeze" | **incorrect** (RV3-B-A06). Option set **incomplete**: no witness threshold or distinct purpose offered. |
| OP-7 (d) | unanchored C2 on attacker-selected state for any binary whose compiled TSS predates the newest TSS | "binaries older than the newest TPS" | **inexact** (D-A04, RV3-L6) |
| OP-4 "no" × OP-2 `release-final` threshold 1 | the everyday candidate key is the key that chooses a production binary's source | "'no' no longer exposes binaries" | **incorrect** (D-A03) |
| OP-2 `release-artifact` (i)/(ii) | two artefact custodians sign after checking only for an attestation | "an accepted malicious binary needs four keys over three purposes" | **incorrect** (RV3-B-A08) |
| OP-2 `release-artifact` (iii) root co-signature | root custodians' check unspecified; RV3-H3 persists unless it includes source legitimacy | "strongest" | **incomplete** |
| OP-2 `release-final` threshold 2 | raises the RV3-H3 key count to two; does not bind source | presented only for final authenticity | **incomplete** (not presented as a binary lever) |
| OP-3 mode B × OP-7 (b)/(c) | clock trust (TA-7) and high-water poisoning | TA-7 stated | correct once CR-06 holds |
| OP-3 mode A × decision pins | automation approvals are same-account files | "never answerable by any agent path" | **inexact** (RV3-M2) |
| OP-6 (b) trust on first use × OP-7 human anchor | first-binary lineage unconfirmed; compiled lineage still binds statements | TA-5 does not hold (stated) | correct |
| OP-1 3 keys / threshold 2 | one root ceremony per kernel-changing final | stated | correct |
| OP-5 | informational | stated | correct |

**Pre-decision.** None. Every proposal is labelled "not a decision". D-0008 records `recommended_option: C` with no `chosen_option`, `in_effect: false`.

**Completeness and honesty.** **Not met** for OP-2, OP-4 and OP-7 → blocking class BC-4 (`11` CD3-4).
