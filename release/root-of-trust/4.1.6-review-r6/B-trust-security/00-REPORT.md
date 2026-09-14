# Independent trust and security review (B) — RoT-1 revision 6 (Governance OS 4.1.6)

| | |
|---|---|
| **Role verdict** | **`BLOCKING_FINDINGS_PRESENT`** |
| Run | AR-0016, role `rot-reviewer-trust-security`, handoff `HO-0016` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at `4106885dadebac55596067a2586cf4d3097fc025`; identical at this review's base `cd4526a` (checked) |
| Prior review | review r5 at `d1228cb77b9253c90406ab0cc3a8c3bd4b480e64` (synthesis adjudication governs); identical at the base (checked) |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Branch | `phase1/rot1-r6-review-b` |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 | Remain PROPOSED (`PROVISIONAL`, `in_effect: false`, no `chosen_option`). This review approves nothing and issues no architecture verdict. |

## Scope

Revision 6 attacked for trust and security, as HO-0016 §2–§3 sets out:
- root trust, the first-contact root and first-machine bootstrap under every OP-13 answer;
- build environments under every OP-16 answer;
- first-hand constitutional content under OP-2, OP-4 and OP-8;
- release registration, reproduction quorum and restrictor revocation;
- re-admission and the verifier trust store;
- anchors, currency, pins and witnesses for every HO-0001 §3.2 machine class under OP-7;
- constitutional floors as a class;
- key hierarchy and signature purpose;
- binary authenticity below the declared thresholds;
- revocation, downgrade and trust-state monotonicity;
- trust-decision authorisation;
- the honesty and completeness of OP-1…OP-16.

Legacy containment (HO-0001 §3.4) is compatibility scope and was not re-assessed.

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, specialist proposal, prior review or other panel review.
- **Orchestration files read:** `HO-0016`, `HO-0001` and `AGENT_RUNS/README.md` only.
- **Disclosure: memory index.** The host session context contained the user's auto-memory index: one-line summaries of
  earlier Governance OS reviews. No memory file was opened, and nothing here rests on it.
- **Disclosure: harness files.**
  - The harness saved two of this session's own command outputs under a tool-results path in `~/.claude/projects/`.
  - A background-task notification named an output file under `…/tasks/`.
  - Neither file was opened: the content was read again from the worktree, and the task's output was checked through this
    review's own scratch log.
- **Not inspected:** other branches, other worktrees, other scratch directories, transcripts, reviewer C's work.
- **Helper sessions:** none.
- **Treated as claims:** the response matrix (`22`), class-remainder analysis (`28`), the decision register and its checks,
  the CS6 calculator, the generated statements, and all architect evidence.

## Method

1. **Re-ran every revision-6 instrument** of the architect from scratch exports: CS6, P4r6, DA03r6, DA07r6, FA6 ×2, CON6,
   ENV6 ×2, SRC6 ×2, ADM6, UW6, ATTR6, the CSI self-test and checks, `register_check`, and `statements_check`. Also re-ran the
   retained revision-5 instruments (CS5, P4r5, DA03r5, FA5, REG5, P1r4).
2. **Re-ran review r5's decisive probes unmodified**: B-A01, A04, A05, A08, A09, A12; D-A01, A03, A04, A05, A07. Their
   revision-6 answers were taken from the architect's adaptations, re-run, and from this review's probes.
3. **Authored 16 held-out attacks** RV6-B-A01…A16: 8 executed, 6 computed, 2 design (`02`).
4. **Judged every declared residual** in trust scope against R-1/R-2 (`03`).

## 1. Reproduction summary

Detail: `02` §Re-execution; `evidence/rerun/COMPARISON.json`.

| Instrument or probe | Result |
|---|---|
| CS6 (JSON and results archive), P4r6, DA03r6, DA07r6, FA6 (both runs), CON6, ENV6 (both), SRC6 (both), UW6, ATTR6, CSI6 self-test, REGISTER-CHECK, STATEMENTS-CHECK | **byte-identical** to the committed outputs |
| CSI6 checks ×5 | identical except the `kernel_dir` path; exits 0/3/2/2/2 |
| ADM6 | identical except the unlocked mutant's race counts (reported, not asserted, as the architect states) |
| CS5, P4r5, DA03r5, REG5, P1r4; FA5 | byte-identical; FA5 equal in every leaf |
| RV5-B-A01, A04, A09, A12; RV5-D-A01, A04, A05 | byte-identical (they load retained revision-5 instruments, or checker modes revision 6 did not change) |
| RV5-B-A05, A08 | verdicts identical; time- or compiler-dependent digests differ |
| RV5-D-A03, A07 | differ where revision 6 changed the pack text and plan (GB-4′ and RT-138 restated; plan rows added) |

## 2. Verdict (role)

**`BLOCKING_FINDINGS_PRESENT`**: three HIGH findings. Each is the recurring class, a lower-trust input yielding a current,
higher-trust fact.

| Finding | Lower-trust input | Higher-trust fact obtained | Class |
|---|---|---|---|
| **RV6-B-H1** | the trust-state publisher process that composes first-contact manifests and codes (rank 3), carried by honest sources | the lineage, state and evaluator of every first-install machine under OP-13 (a), (b), (c) either, (d); P1/P2/CIR currency inputs | narrowed remainder of BC5-1 |
| **RV6-B-H2** | under OP-13 (c) "either suffices": the package submitter; a carrier replaying an old genuine package (`valid_until` optional) | a substituted evaluator, or a revoked (including malicious) binary, as first TCB | narrowed remainder of BC5-1 ∩ BC4-2 |
| **RV6-B-H3** | the environment manifest's author (recipe, component selection, upstream key reference, supplier-class label); the pipeline in a conforming process | the bytes of every production binary under OP-16 (a) and (b) | narrowed remainder of BC5-2 |

## 3. Findings

Full statements: `01-FINDINGS.md`.

| ID | Severity | Title |
|---|---|---|
| **RV6-B-H1** | **HIGH** | The first-contact code is composed by the trust-state publisher and only carried by the sources: one rank-3 party selects lineage, state and evaluator at first contact, and P1/P2/CIR currency inputs; declared root and consequences false |
| **RV6-B-H2** | **HIGH** | OP-13 (c) "either suffices": package submitter and replayed old packages select the first TCB outside the declared root; `valid_until` not required; FA6 exercises neither |
| **RV6-B-H3** | **HIGH** | No party establishes the environment manifest (recipe, selection, upstream key, supplier class): its author selects every binary's bytes under OP-16 (a)/(b); diversity by label |
| RV6-B-M1 | MEDIUM | Re-admission keeps the verifier trust store but does not apply it: an older genuine binary below the accepted-TBM high-water is admitted and runs |
| RV6-B-M2 | MEDIUM | Generated CONTENT statements print the repository-writer atom as "1 reproducer key" (8 of 24 rows); `statements_check` S1 cannot detect rendering errors |
| RV6-B-M3 | MEDIUM | Register completeness is checked over rule ids, not over selectors; the selectors behind H1–H3 are invisible to C2, CS6 and RT-128/RT-183 |
| RV6-B-L1 | LOW | R-CON-5 lists only name-matched security units (`COMMAND_CONTRACT`, overlay-template and taxonomy changes not listed) |
| RV6-B-L2 | LOW | Stale revision-5 text in `05` §1–§2 |
| RV6-B-L3 | LOW | Verification precedes environment registration; the verifier's environment source is unstated |
| RV6-B-L4 | LOW | Derivation-tool provenance at the registration ceremony is unstated |
| RV6-B-I1 | INFO | RV5-I1 unchanged |

## 4. Prior findings (review r5), status as classes

| Finding | Status | Evidence |
|---|---|---|
| **BC5-1** first-contact root | **NARROWED → RV6-B-H1, RV6-B-H2** | FA6 re-run: under (b) and (c) "all", a one-page lineage and a one-page evaluator are refused; compiled quorum, lineage from the typed value, evaluator binding and 14/14 mutants hold. The composer, submitter and replay select outside the root (A01, A05, A06, A13). |
| RV5-H1 | **NARROWED**: as stated **CLOSED** (one page, quorum read from the selected state, bundle order, one-channel admitter digest); remainder H1, H2 | FA6 S2, S7 re-run; RV5-B-A01 unmodified re-run (revision-5 executor) byte-identical |
| **BC5-2** build environment | **NARROWED → RV6-B-H3** | ENV6 re-run (pipeline image refused, E1; substituted component refused, E2; carrier refused, E3; diversity checks, E5 and E9); A02, A07, A08, A09 accepted; computed INV-ENV-PIPELINE fails with an authored manifest |
| RV5-H2 | **NARROWED**: as stated (pipeline image record) **CLOSED**; remainder H3 | ENV6 E1; CS6 revision-5 profile control |
| **BC5-3** first-hand content | **CLOSED as a class** (within this review's attacks); carried RV6-B-L1, L4 | CON6 re-run 17/17; P4r6 G rows; A10: `verify-registration` exit 3 for every non-first-hand proposal; A12: no content set from release keys, trust-state key and infrastructure only; RV5-D-A01 re-run byte-identical (the checker's plain mode is unchanged; refusal is at R-CON-1 and R-CON-3) |
| RV5-H3 | **CLOSED** | as BC5-3 |
| **BC5-4** register and statements | **NARROWED → RV6-B-M2, RV6-B-M3**; the false OP-6, OP-9, OP-13 and OP-16 statements belong to H1–H3 | REGISTER-CHECK and STATEMENTS-CHECK re-run PASS; A03; A01 part C; A02 computed |
| RV5-M1 restrictor revocation | **CLOSED** | FA6 S5; P4r6 `R6-AP5r_*`; CS6 mutation `V_REVOCATION_AUTHORITY` (re-run) |
| RV5-M2 registration reductions | **CLOSED as stated**; listing scope → RV6-B-L1 | CON6 B-A09 exit 8, B-A10 exits 6 and 7; CSI S73–S76; A10 |
| RV5-M3 re-admission | **NARROWED → RV6-B-M1** | ADM6 A09/A09b/A10/A11; FA6 S6; A04 |
| RV5-M4 source identity | **CLOSED** | SRC6 re-run ×2 byte-identical (T1 refuses the two-tree construction) |
| RV5-M5 decision register | **NARROWED → RV6-B-M3** | the omitted decisions are listed (DR-03…06, 10, 13, 15, 16, 19, 25); selectors without rule ids remain absent |
| RV5-M8 user-writable installs | **CLOSED** (restated) | UW6 re-run; RV5-D-A03 re-run (pack text matches computed classes) |
| RV5-M9 executors disagree | **CLOSED** | FA6 S4: R1–R5 same codes as P4r6 |
| RV5-L1 bundle order | **CLOSED** | FA6 ORD-1…3; mutant detected |
| RV5-L2 unsigned record | **CLOSED** | FA6 S6; ADM6 A15 |
| RV5-L3 clock set back | **CLOSED by rule** (reference) | P4r6 `R6-CLOCK-*`; A11: 0 C3 rows under CLOCK-back |
| RV5-L4 stale text | **NARROWED → RV6-B-L2** | design |
| RV5-L5 victim classes | **CLOSED** | CS6 11 victim classes |
| RV5-L6 root threshold | **CLOSED** | P4r6 KS14; FA6 S5 |
| RV5-L9 OP-3 mode B | **CLOSED** | P4r6 `R6-OP3-B-*` |
| RV5-I1 acting role | unchanged → RV6-B-I1 | `27` §5 |
| RV5-I2 binding-group derivation | carried (RT-182) | design |

## 5. HO-0001 requirements (trust scope)

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure | **SATISFIED** within trust scope, with carried CR6-B-04, CR6-B-07, CR4-B-05 | CSI self-test 78/78 re-run; A10 default deny (unknown key and new file exit 2) and first-hand refusal; CON6 (`ASIA…` file excluded on 4.1.5; tool command listed); RV5-B-A09 re-run (wildcard `informational` key still admitted, RV4-L1) |
| §3.2 New-machine trust bootstrap | **NOT SATISFIED** | **First install:** H1 (composer) under OP-13 (a), (b), (c) either, (d); H2 under (c) either. **Re-admitted workstations:** M1. **Holds** for the other classes: A11, 352 rows, 0 `current`, 0 C3 on the thief descendant, CLOCK-back 0 C3, E10 kept on re-admission. |
| §3.3 Binary and root authenticity | **NOT SATISFIED** | **Bytes:** H3. **First-contact evaluator:** H1, H2. **Holds:** no accept from ≤ 1 key, or from release keys, trust-state key and infrastructure (A12, 246,608 subsets); running-mode chain non-circular. At first contact the first link is the composer (H1). |
| §3.4 Legacy-binary containment | not assessed (compatibility scope) | — |
| §4 Forward compatibility | **SATISFIED** for classification and content selection | A10 K6 exit 2; CON6 N2–N4 re-run |

## 6. Owner options OP-1 … OP-16

| Option | Consequence statement | Basis |
|---|---|---|
| OP-1 | accurate | KS-14 executed (FA6 S5, P4r6) |
| OP-2 | selection statements hold; the CONTENT block misprints `repo` | CON6; RV6-B-M2 |
| OP-3 | accurate | P4r6 mode-B rows |
| OP-4 | holds ("kc appears in no set without the registration threshold and OP-8 verification"); CONTENT block misprint | A12; RV6-B-M2 |
| OP-5 | informational | — |
| OP-6 | **false**: the lineage confirmed is the one the composer selects | RV6-B-H1 |
| OP-7 | accurate, including user-writable installs | UW6; A11 |
| OP-8 | accurate | CON6; CS6 |
| OP-9 | **false** for P1 ("never on P1"), P2 and CIR sets | RV6-B-H1 (A13) |
| OP-10 | accurate | CS6 |
| OP-11 | (a) accurate for E10; incomplete for binary rollback at re-admission | A11 M8; RV6-B-M1 |
| OP-12 | accurate | — |
| OP-13 | **false**: composer (all answers but (c) "all"), submitter and replay ((c) either) | RV6-B-H1, RV6-B-H2 |
| OP-14 (b), OP-15 (a) | incomplete: re-admission keeps but does not apply the store | RV6-B-M1 |
| OP-16 | **false** for (a) and (b): the manifest author; diversity by label | RV6-B-H3 |
| Unsupported combinations (`21` §17) | The three stated are honest. **Incomplete:** OP-13 (c) "either" without a mandatory bounded `valid_until` and an established package; OP-16 (b) with classes sharing an author or an upstream. | A05, A06, A07c, A08 |
| Pre-decided? | No: D-0008 has no `chosen_option`; `21` states no proposal | design |

## 7. Residuals

Detail: `03-RESIDUALS.md`.

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | AD-1′/FC-R1 (H1, H2); FC-R3 (H2); RS-B1 on the (c) either platform path (H2); TB-S2′ under OP-16 (a), (b) (H3) |
| ACCEPTED WITH CONDITION | FC-R4, AD-2, TB-S1 (environment), TB-L4, RS-3, CS-1, VR-3, TG-2, LR-4 |
| ACCEPTED | FC-R2, RS-B1 (owner pages), TB-1′, VR-B1′, TB-S1, TB-S2, TB-S2′ (c), TB-S3, TB-4, TB-4′, RA-1, AV-S1, RS-1, RS-1b, RS-1c, RS-2, RS-2b, RS-4, RS-5, OP-7 (d), CS-2, DR-15, DR-25, DR-33, VR-1, VR-2, VR-4, RR-1, RR-2, RR-3, TG-1, TG-3 |

## 8. Held-out attacks

| Item | Count |
|---|---|
| Authored | 16 (RV6-B-A01…A16) |
| Executed / computed / design | 8 / 6 / 2 |
| Leading to HIGH / MEDIUM / LOW | 8 / 3 / 3 |
| Holding | A11, A12 (and A10 for selection and default deny) |

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | every finding: statement, evidence, failure scenario, severity, correction direction |
| `02-HELDOUT-ATTACKS.md` | RV6-B-A01…A16 and the re-execution of review r5 probes and architect instruments |
| `03-RESIDUALS.md` | residual criteria and determinations |
| `04-CARRIED-REQUIREMENTS.md` | CR6-B-01…07 with acceptance tests; re-review entry cases for H1–H3 |
| `evidence/` | probes, outputs, re-run logs and comparison, reviewed-content digests, README |
