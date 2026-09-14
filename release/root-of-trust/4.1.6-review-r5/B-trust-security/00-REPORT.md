# Independent trust and security review (B) — RoT-1 revision 5 (Governance OS 4.1.6)

| | |
|---|---|
| **Role verdict** | **`BLOCKING_FINDINGS_PRESENT`** |
| Run | AR-0012, role `rot-reviewer-trust-security`, handoff `HO-0012` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` at `cdb4e14009bba60bea9b805563c1b60e84f30b4b`; identical at this review's base `bfaa943` (`evidence/REVIEWED-CONTENT-DIGESTS.txt`, 280 files) |
| Prior review relied on | review r4 `release/root-of-trust/4.1.6-review-r4/` (`97a5545`, identical at `cdb4e14`); synthesis adjudication governs |
| Branch | `phase1/rot1-r5-review-b` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged between `da9c851` and `cdb4e14` (checked) |
| Date | 2026-09-14 |
| Status of D-0008 / ARCH-0002 | Remain PROPOSED (`PROVISIONAL`, `in_effect: false`, no `chosen_option`). This review approves nothing and does not issue the architecture verdict. |

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, specialist proposal, earlier review, or reviewer C's
  work.
- **Orchestration files read:** `HO-0012`, `HO-0001` and `AGENT_RUNS/README.md` only.
- **Read, in scope:**
  - review r4 in full for B and D, plus its `00`, `10` and `11`. For reviewer C's r4 directory, only the file names and
    D's adjudication of it.
  - the specialist `SYNTHESIS.md`, by keyword search only (background).
- **Not read:** other branches, worktrees or scratch directories; reviewer C's r5 output; orchestrator state, ledger, run
  records and other reports.
- **Disclosure.** The host session context included the user's auto-memory index: one-line summaries of earlier Governance
  OS reviews. No memory file was opened, and nothing in this review rests on it.
- **Treated as claims:** the response matrix (`22`), class-remainder analysis (`28`), SYNTHESIS, and every evidence file.
  Every instrument relied on was re-executed.

## Method

1. **Read** the pack `00`–`31`, the schemas, the checker, and the reference instruments (`gov_admit_reference.py`, CS5,
   P4r5, FA5, REG5, SRC5, DA03r5); D-0008 and ARCH-0002; review r4 B, D and the consolidated files.
2. **Re-executed** from a scratch export of `cdb4e14` (`evidence/rerun/RERUN-LOG.json`):
   - the architect's instruments: CSI self-test and checks, P1r4, CS5, P4r5, DA03r5, FA5 (twice), REG5, SRC5;
   - review r4 B's four probes and six review-r3 copies;
   - review r4 D-A02, A03, A03b.
3. **Authored 19 held-out attacks** (`02-HELDOUT-ATTACKS.md`), each executed or computed where feasible:
   - with the architect's reference executor (real Ed25519), checker and oracle functions, unmodified;
   - with the real 4.1.5 binary, real Git, and the real Rust toolchain;
   - with CS5's `accepted` wrapped (never modified) to add strategies its honest-party model omits.
4. **Modelled** HO-0001 §3.2's machine classes × OP-7 × adversaries (296 rows) on the architect's P4r5 functions.
5. **Judged** residuals against R-1 and R-2 (`03`) and the owner-option consequence statements against the computed results.

## 1. Verdict against HO-0012 §4

| Condition | Result |
|---|---|
| Any CRITICAL or HIGH (blocking) | **Yes: 3 HIGH** — RV5-B-H1, RV5-B-H2, RV5-B-H3 |
| MEDIUM not carriable without an architecture change | none identified; RV5-B-M1 … M5 carried (`04`) |

**Role verdict: `BLOCKING_FINDINGS_PRESENT`.**

## 2. Reproduction of the architect's claims and prior probes

| Instrument (owner) | Claim | Re-executed result |
|---|---|---|
| CSI `selftest` (architect) | 71 of 71 | **71 passed, 0 failed** (identical ignoring scratch paths) |
| CSI `check` framework / 4.1.5 / 4.1.2 / 4.1.3 / 4.1.4 | 0 / 3 / 2 / 2 / 2 | **0 / 3 / 2 / 2 / 2** |
| CS5 calculator (architect) | 408 configurations, 21/21 self-checks, 1,752 invariant checks with 0 failures, 138,042 monotonicity checks with 0 violations | **byte-identical**. The model omits channel-selected lineage, the build image, the policy-root goal and restrictor revocation (A04, A06, A07, A08). |
| P4r5 oracle (architect) | 65/65; 42/42 retained; 0 expected-`ACCEPTED` attack rows | **byte-identical** |
| DA03r5 (architect) | 20/20 D-A03 rules; 17/17 revision-5 mutants | **byte-identical** |
| FA5 (architect) | 45/45 scenarios; 17/17 vectors; 26/27 mutants | **byte-identical, twice** |
| REG5 on real 4.1.5 (architect) | 10 verdicts true | **byte-identical** |
| P1r4 on real 4.1.5 (architect) | unchanged | **byte-identical** |
| SRC5 (architect) | "canonical content digest equal across repositories … 10/10" | Verdicts true, but **every digest differs from the committed output**. The function hashes `git archive` of a tree id, which is time-stamped, not the specified canonical digest (A05; RV5-B-M4). |
| review r4 B model and AF1–AF3 | revision-4 rules | byte-identical |
| review r4 B surface probes | U, T, P on 4.1.5 | U and T unchanged (U01, U02 still exit 0). **P: the retaining inventory is malformed (exit 5).** |
| review r4 B confinement and first binary | A, B | A unchanged (legacy); B shows the revision-5 TBM field names |
| review r3 copies (RV3-B-A01, I01–I09, D lattice, D forward compat/removal, A03/A14/A16, r2 P2) | as review r4 | identical (4 byte-identical, 2 ignoring scratch paths) |
| review r4 D-A02 / D-A03 / D-A03b | — | RETAIN form exit 5 for all targets; D-A03 and A03b byte-identical (on P4r4) |

## 3. Prior-finding status (classes, not instances)

| Finding | Status | Evidence |
|---|---|---|
| **BC4-1** independent decisions for the TCB | **OPEN → RV5-B-H2** (and M4) | The key-theft and pipeline shapes of review r4 are refused (CS5, P4r5 VA5 rows, re-run). The build image selects the bytes of every reproducer with no authority (A08, executed). |
| **BC4-2** anchored, non-circular first TCB | **NARROWED → RV5-B-H1** (and M3, L1, L2) | Revoked, remediated and moved-tag binaries, Phase 4 and ceremonies are refused (FA5 re-run). The channel alone selects lineage and evaluator, and the declared minima are false (A01, A04). |
| **BC4-3** release-scoped registration | **NARROWED → RV5-B-H3, M2** | Release-final mixing is refused (REG5, D-A02, part P re-run). Under OP-2 (b) the policy-root content selector lacks the verification restrictor (A06). Reductions are exact-match and ceremony-side only (A09, A10). |
| **BC4-4** owner options and blast radius | **OPEN** | OP-2 (b), OP-4, OP-8, OP-9, OP-10, OP-12, OP-13, OP-14 (b), OP-15 (a); AD-1 (§5) |
| RV4-H1 | **CLOSED as stated**; class remainder H2 | CS5 self-checks `rep1 + pipeline`, `va1 + pipeline` refused; P4r5 VA5-07…13, B-prime |
| RV4-H2 | **CLOSED as stated**; class remainder H1 | FA5 FB1a/b, FB2a/b/c, FB3, PH4, DA04 |
| RV4-H3 | **CLOSED as stated**; class remainder H3, M2 | REG5 15/15 mixed identities exit 3; `ASIA…` file excluded on 4.1.5 |
| RV4-M2 | **NARROWED** | Allow list in `27` §3.3 and rule (21), specification only (RT-103, RT-138). `24` §3.5 (3) still enumerates a deny list (L4). |
| RV4-M3 | **CLOSED by rule** | `24` §3.3 input and custody (RT-149 specification only) |
| RV4-M4 | **NARROWED** | Stateful high-water (P4r5 CLOCK reproduced). Restored-backup clock case (L3); contradictory witness-only text (L4). |
| RV4-M5 | **CLOSED** (selector); CR4-B-04 carried | Migrations registered per release (REG5); RT-146 specification only |
| RV4-M7 | **CLOSED** for the 20 mutants | DA03r5 20/20 and 17/17 reproduced. New rules without vectors: L1, A02, A03 (in M1, H1). |
| RV4-L1 | **OPEN** | U01, U02 exit 0 on the revision-5 checker; CR4-B-05 specification only |
| RV4-L2, L3, L4, L5 | **CLOSED** | P4r5 rows reproduced |
| RV4-L6 | **CLOSED as stated**; side effect **M1** | FA5 vectors; A03 |
| RV4-L7 | **NARROWED** | OP-4 restated; "release-final appears in no minimal set" is false for policy-root content (H3) |
| RV4-L8 | **CLOSED** for `release-final` alone; remainder H3 under OP-2 (b) | P4r5 `E7-D-A06`; REG5 |
| RV4-L9 | **CLOSED** | `production_sources[]` withdrawn |
| RV4-L10 | **CLOSED** (checker; binary RT-143 specification only) | self-test S66/S67 in 71/71 |
| RV4-I1 | **UNCHANGED** (INFO) | `27` §5 |

### Owner options OP-1 … OP-15 (consequence statements)

| Option | Determination | Basis |
|---|---|---|
| Pre-decided? | **No** | D-0008 has no `chosen_option`; `21` states no proposal. `24` §9 still carries revision 4's labelled OP-7 proposal (L4). |
| OP-1 | accurate, except that no minimum threshold is stated | L6 |
| OP-2 | (a) accurate. **(b) false for non-orderable content**: the minimal sets need no verification compromise and include `release-final`. | H3 (A06) |
| OP-3 | accurate | — |
| OP-4 | **false for policy roots** ("appear in no minimal set") | H3 |
| OP-5 | accurate | — |
| OP-6 | accurate as far as stated; the committed lineage is whatever the channel shows | H1 |
| OP-7 | (a), (b), (d): restated and accurate, with text caveats; (c) accurate | L3, L4 |
| OP-8 | **incomplete**: no effect on policy-root content | H3 |
| OP-9 | **false for first admission** (channels alone); key-theft sets overstated by `transport`; no effect on the image | H1, M1, H2 |
| OP-10 | **incomplete**: the build image is not covered; a diverse reproducer must share it | H2 |
| OP-11 | accurate ((a) states RR-2); register mislabels Git delivery | M5 |
| OP-12 | **incomplete**: every form selects the evaluator by the channel; no binding to `admitter_digests` or revocation | H1 |
| OP-13 | **false**: one channel (a) or two channels (b) suffice with zero keys; (b)'s quorum is read from the selected state | H1 |
| OP-14 | **incomplete**: (b) re-admission discards monotonic state | M3 |
| OP-15 | **incomplete**: (a) incident path via `gov-admit` discards monotonic state | M3 |

## 4. HO-0001 owner requirements (trust and security view)

| Requirement | Determination | Basis |
|---|---|---|
| §3.1 constitutional-floor closure | **NOT SATISFIED** | **Holds:** inventory; checker 0/3/2/2/2; self-test 71/71; unknown key and new file refused in registration mode (A11); precedence, presence and exceptions (P1r4, self-test re-run); `release-final` mixing refused (REG5); tunable-only kernel harmless (part T re-run, A16). **Fails:** sensitivity exclusions and tool commands under OP-2 (b) below the declared authority (H3); non-identical weakening reported by no mechanism, and reductions not computed at the verifier (M2); wildcard informational keys (RV4-L1). |
| §3.2 new-machine trust bootstrap | **SATISFIED for transport and repository adversaries, with carried conditions** | A12 (296 rows): 0 `current` labels. Revoked state is reachable only under stated RS-1, RS-1b, RS-1c and RS-B1 bounds and TA-7 clock rows. C3 is never allowed on a trust-state thief's descendant. First-admission shapes of review r4 are refused (FA5). Carried: M3 (re-admission discards monotonic state), L3, L4. The channel adversary is judged under §3.3 (H1). |
| §3.3 binary and root authenticity | **NOT SATISFIED** | The build image mints the TCB for every reproducer with one input (H2). First admission rests on the channel alone, and the declared minima and OP-9/OP-13 consequences are false (H1). The source identity is ambiguous (M4). **Holds:** one key of any purpose, with or without pipeline input, does not mint a binary (CS5 re-run); running-mode chain non-circular (P4r5); remediated and revoked binaries refused (FA5). |
| §3.4 legacy containment | not assessed by B (compatibility scope) | no B finding bears on it |
| §4 forward compatibility | **SATISFIED for classification** | A new constitutional file and an unknown key exit 2 in registration mode (A11) |

## 5. Findings

Full statements: `01-FINDINGS.md`.

| ID | Severity | Title |
|---|---|---|
| **RV5-B-H1** | **HIGH** | First admission is selected by the independent channel alone: the typed fingerprint selects the lineage and the channel's digest the evaluator; a channel attacker with no key admits a malicious TCB under OP-13 (a) and (b); declared first-admission minima false in 288/288 configurations |
| **RV5-B-H2** | **HIGH** | The build image selects the bytes of every production binary: legitimised by an "owner's image record" no rule assigns; every honest reproducer, including an OP-10 (b) diverse one, reproduces the same malicious bytes |
| **RV5-B-H3** | **HIGH** | Policy-root content under OP-2 (b): E7 has no verification-record restrictor and no policy-root goal is derived; {2 delegated custodians, `release-final`} or {2 delegated registration keys, trust-state, `release-final`} make malicious non-orderable content effective; OP-8 changes nothing |
| RV5-B-M1 | MEDIUM | Revocation removes restrictors (conflicting reproductions, REJECTED attestations); CS5 models their removal only by transport |
| RV5-B-M2 | MEDIUM | Registration reductions are exact-match and ceremony-side only: E7 accepts an undeclared reversion; a withheld intermediate hides it; non-identical weakening is reported by nothing |
| RV5-B-M3 | MEDIUM | Re-admission discards the machine's monotonic trust state (R-ADM-8 "first" undefined; OP-14 (b) and OP-15 (a) force `gov-admit`) |
| RV5-B-M4 | MEDIUM | Source identity digest ambiguous for newline-bearing paths; SRC5 tests a different, time-dependent function |
| RV5-B-M5 | MEDIUM | Decision register incomplete and misclassified in the architecture |
| RV5-B-L1 | LOW | Reference executor selects the lineage by bundle order |
| RV5-B-L2 | LOW | Unsigned admission record: GB rules bind only installs that did not ship a record |
| RV5-B-L3 | LOW | Clock set back on restored or long-offline machines re-opens P1 on stale anchors |
| RV5-B-L4 | LOW | Contradictory text: witness-only clock high-water, deny-list confinement, a retained OP-7 proposal |
| RV5-B-L5 | LOW | Calculator victim classes omit witness-reliant and CI-record runners |
| RV5-B-L6 | LOW | No minimum root threshold in the normative text |

### The recurring class

| Finding | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| H1 | one channel page (rank 2), no key | the root of trust and the first TCB on a machine |
| H2 | the build image record (no authority) | the bytes of every accepted production binary |
| H3 | two delegated custodians + one `release-final` key (or those keys + trust-state key) | the effective constitutional content (secret handling, tool commands) of the policy root |

## 6. Held-out attacks

**19** attacks (RV5-B-A01 … A19; `02-HELDOUT-ATTACKS.md`):

| Evidence class | Count | Attacks |
|---|---|---|
| Executed | 10 | A01, A02, A03, A05, A08, A09, A10, A11, A14, A16 |
| Computed | 6 | A04, A06, A07, A12, A13, A19 |
| Design or code | 3 | A15, A17, A18 |

- **Contradict a pack claim:** 17.
- **Hold:** A11 and A16, and A12 outside L3 and M3.

## 7. Residuals

Detail: `03-RESIDUALS.md`.

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | AD-1 (H1); TB-S2 as covering the build image (H2) |
| ACCEPTED WITH CONDITION | RS-2, RS-3, AD-2, TB-1′, TB-S1, TB-4′ (binaries only), CS-1, CS-2, VR-3, RR-2, TG-2, LR-4 |
| ACCEPTED | RS-1, RS-1b, RS-1c, RS-4 (scoping), RS-5, OP-7 (d), RS-B1, VR-B1, TB-S2 (toolchain archive), TB-S3, TB-4, AV-S1, TB-L4, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3 |
| Not assessed (compatibility scope) | LR-1 … LR-3 |

## 8. What revision 5 does close (confirmed by re-execution)

- **Key theft and pipeline shapes for binaries.** One key of any purpose, a key with pipeline input, and review r4's routes
  B′ and S′ are refused. `release-artifact` and `build-attestation` are withdrawn. The reproduction quorum, conflict rule
  and publication hold for running binaries.
- **First-binary instances of review r4.** Revoked and remediated binaries, a moved tag, Phase 4 self-verification and
  ceremonies on an unadmitted binary are refused. The candidate is never executed. Installation is from the measured buffer.
- **`release-final` as selector of constitutional content.** Mixed releases are refused under every claimed identity;
  retention sets are malformed; gap, inflated and stale-policy releases are refused.
- **Carried items.** P1 proof names its state; `WITNESSED` C3 has one rule; the stateful clock high-water; first-run TBM
  recording; decision-pin maximum validity; revoked evidence never counts; oracle coverage of D-A03's mutants.

## 9. Scope notes and deviations

- **Not re-run by this reviewer (compatibility scope):** P3r3, ST5-*, LR2, reviewer C's r4 scripts, RV4-D-A01.
- **Consumer stand-in.** The real 4.1.5 binary stands in for a consumer, as in review r4. No RoT-1 binary exists, so
  `gov-admit` and `verify-artifact` are evaluated through the architect's reference executor and oracle.
- **Harness corrections during the review.** Recorded for transparency; the committed outputs are from the corrected
  scripts.
  - The first A01 run placed the genuine root first in the attacker's bundle. The executor took the lineage from bundle
    order, which led to RV5-B-L1.
  - The first A12 run edited a Trust State's `arts` (non-admissible) and omitted the stateful clock high-water.
- **First scripted runs** of four prior probes omitted positional arguments and exited before doing anything. They were
  re-run with the arguments.
- **No scope deviation** from HO-0012 §6.

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | findings H1–H3, M1–M5, L1–L6 |
| `02-HELDOUT-ATTACKS.md` | RV5-B-A01 … A19 and the re-execution register |
| `03-RESIDUALS.md` | residual criteria and determinations |
| `04-CARRIED-REQUIREMENTS.md` | CR5-B-01 … CR5-B-12, carried review-r4 items, re-review acceptance cases for H1–H3 |
| `evidence/` | probes, outputs, re-run log, reviewed-content digests, README |
