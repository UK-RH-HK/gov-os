# Independent architecture synthesis review (D) — RoT-1 revision 7, certified profile CP-1 (Governance OS 4.1.6)

| | |
|---|---|
| **Architecture verdict** | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Run | AR-0022, role `rot-review-synthesis`, handoff `HO-0022` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at `d07d200ac08a52c45071d33074e20cc62fbcc26e`; identical at this review's base `1d4d9f3` (`git diff --quiet`) |
| Panel verified | reviewer B `54be694cc6291538fe0901f3d71eb685ce3138d4` (`BLOCKING_FINDINGS_PRESENT`); reviewer C `34633ccc53a4928262b4f38e5d1d018239b7a322` (`BLOCKING_FINDINGS_PRESENT`); both directories identical at the base (checked) |
| Owner requirements | OWNER-DESIGN-REQUIREMENTS-0001 (`fbd09d5`) and OWNER-DESIGN-REQUIREMENTS-0002 (`30542e5`), verbatim texts, binding; -0002 post-dates revision 7 |
| Branch and base | `phase1/rot1-r7-review-d` from `1d4d9f3` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Orchestration context | The product owner has frozen the revision loop after this verdict; `11-CORRECTION-DELTA.md` is recorded as evidence for the later meta-architecture review and is not routed to another revision |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 / D-0007 | D-0008 `status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false`, `in_effect: false`, no `chosen_option`; ARCH-0002 `PROVISIONAL`, `PROPOSED`, `in_effect: false`; D-0007 `ACTIVE`. This review approves nothing; architecture acceptance would not be owner approval. |

## Scope

The whole of revision 7 as the one certified production profile CP-1 that governs 4.1.6, judged against HO-0022 §3's acceptance rule,
HO-0001 §3–§4 and both owner records, including CP-1's real combinations and exclusions. The review covers:
- reproduction of every panel probe behind a HIGH claim or a claim that a prior HIGH is closed, and of the architect's instruments;
- adjudication of every B and C finding and status claim;
- held-out attacks RV7-D-A01 … A10;
- owner requirements and resolutions, residuals and owner options;
- for each blocking class, its novelty and the kind of fix (HO-0022 §2a).

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, specialist proposal, reviewer B or C work, prior review or owner
  requirement.
- **Orchestration files read:** `HO-0022`, `HO-0001`, `AGENT_RUNS/README.md`, `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` and `.yaml`,
  `GATES/OWNER-DESIGN-REQUIREMENTS-0002.md` and `.yaml`. No state, ledger, checkpoint, run record, other handoff, other GATES file
  or `AGENT_RUNS/*.report.yaml` was opened.
  - Disclosure: `ls GATES/ | grep OWNER-DESIGN` listed the two owner records and their indexes (names only).
  - Disclosure: `git log --oneline -1 30542e5` and `-1 fbd09d5` printed those commits' subject lines to confirm the owner-record
    identities; `git diff --quiet` / `--stat` over the pack, spec, docs, implementation, B, C and review r6 paths confirmed identity
    (no orchestration file content was read that way).
- **Disclosure: memory index.** The host context included the user's auto-memory index (one-line summaries of earlier Governance OS
  reviews). No memory file was opened; nothing here rests on it.
- **Disclosure: harness files.** The harness saved two of this session's own command outputs (reviewer B's and C's report text) under a
  tool-results path in `~/.claude/projects/`. Those files were not opened; the content was re-read from the worktree.
- **Disclosure: Git reads.** Reviewer C's `register7.py` ran `git show` at the four legacy release commits in this review's worktree
  (read-only).
- **Not inspected:** other branches, other worktrees, other scratch directories, session or agent transcripts, task-output files.
- **Helper sessions:** none.
- **Treated as claims:** the response matrix (`22`), the class-remainder analysis (`28`), the register and its checks, the calculator,
  the generated statements, every architect evidence file, and every statement of reviewers B and C.
- **Hygiene:** `D-synthesis/evidence/README.md`.

## 1. Verdict against the acceptance rule (HO-0022 §3)

| Condition | Result |
|---|---|
| Conformance with OWNER-DESIGN-REQUIREMENTS-0001 and -0002; excluded modes absent or refused; certification criterion explicit, executable/testable and non-circular | **Not met.** Deviations: OP-4 revocation purpose subordinate to trust-state listing (RV7-H1); OP-7 (a) and -0002 OT-1 B running-machine C3 on stale state (RV7-H2); -0002 OT-2 criterion not executable and label-based, owner label not adopted (RV7-M2); OP-10 (b) / OP-16 (b) "not labels" (RV7-M2). Exclusions: **met** (PROF7 113/113 checks and 24/24 exclusions reproduced; schema sweep reproduced). |
| No open CRITICAL or HIGH after adjudication | **Not met.** 2 HIGH: RV7-H1, RV7-H2 |
| Every HO-0001 §3 requirement `SATISFIED` as a class | **Not met.** §3.2 `NOT SATISFIED`; §3.1, §3.3, §3.4 and §4 `SATISFIED` (§5) |
| Every open MEDIUM carried as a bound, testable requirement; none needs an architecture change | **Not met** for RV7-M1, M2, M3, M4. RV7-M5 … M10 are carriable (`11` §6). |
| Every residual explicitly bounded under attack | **Not met.** FC-R1′/AD-1″, FC-R3′, CUR-R1, FC-R5 (G_REVOKED), RS-1b, RS-1c (C3), TB-S2″, TA-12″ not accepted (§6) |
| Owner options complete and honest, none pre-decided | **Not met** for completeness and honesty (§7). Met for "none pre-decided" and "no owner parameter reopened". |

**Verdict: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.** The correction is architectural and stated as classes in `11-CORRECTION-DELTA.md`.

### What revision 7 does close (confirmed by reproduction)

- **RV6-H1 as stated** (BC6-1): the First-Contact Authority record at root threshold; compiled quorum and lineage; first-hand custodian
  publication; no composer, printer, submitter or platform root. FA7 byte-identical over two runs; PROF7 byte-identical.
- **RV6-H2 as stated** (BC6-2): the compiled 24-hour admission state age for replayed, stored, media, CI and designated values;
  re-admission applies both stores. CUR7 and cur7x M2 byte-identical.
- **RV6-H3** (BC6-3): derived environment manifests; ENV7 byte-identical with the real `rustc 1.98.1`.
- **R2-H4 as a class**: reviewer C's `matrix7` reproduced (every property equal), `struct7` byte-identical, `gitops7` and `txn7` equal.
- **Concretisation to one profile**: every exclusion absent or refused (PROF7; RV7-B-A08, A09 reproduced); key subsets below threshold
  (BA12r7 byte-identical); constitutional surface default deny (CSI 78/78; RV7-D-A07 K1, K3).

## 2. Reproduction table

Detail: `D-synthesis/01-REPRODUCTION.md`; comparison `D-synthesis/evidence/reproduction/REPRODUCTION-COMPARISON.json`.

| Probe (owner) | Behind claim | Reproduced |
|---|---|---|
| RV7-B-A01, A01m, CS7 (B) | **RV7-B-H1**; M1 (CS7 A03) | **yes**, byte-identical |
| RV7-B-A02 (B) | **RV7-B-H2** | **yes**, byte-identical |
| RV7-B-A04-A05, A09 (B) | L1, L2; exclusion sweep | **yes**, byte-identical |
| RV7-B-A08 (B; PROF7 on a mutated schema copy) | exclusion checks are load-bearing | **yes**: exactly EX-01 and EX-04 fail (111/113 checks, 22/24 exclusions) |
| cur7x (C) | **RV7-C-H1** | **yes**, byte-identical |
| adm7x (C) | RV7-C-M1, L2, L3 | **yes**: equal except the run-dependent X5 race counts |
| ident7, design7 (C) | RV7-C-M2; design findings | **yes**: design7 byte-identical; ident7 equal except inode values (verdict equal) |
| registers7, build7, struct7, gitops7, txn7, **matrix7** (C) | **R2-H4 CLOSED as a class**; M3, M4, M5, L1 | **yes**: registers7 and struct7 byte-identical; build7 states equal; gitops7 equal for 45 operations; txn7 summary, honouring, roll-forward and uninstall equal; matrix7 all 196 position aggregates and every property equal after composing a P-TXN re-run (the first run's P-TXN rows hit scrubbed paths; `01` §matrix7): R2-H4 0 violations, LP-1r 3,572 rows 0 writes |
| CS7 (+ results), FA7 ×2, CUR7, ADM7, ENV7, BA11r7, BA12r7, PPR7, DA05r7, DA06r7, STATEMENTS-CHECK, PROF7, REGISTER-CHECK, DA09r7, DA04r7 (architect) | **RV6-H1/H2/H3 closed as stated**; profile conformance | **yes**, byte-identical (15 instruments, FA7 twice) |
| CSI self-test and checks (retained) | §3.1 | **yes**: self-test byte-identical; checks equal except `kernel_dir` |
| DA07r6 on the revision-7 plan, RV6-B-A03 (retained, B-L5 staleness claim) | RV7-B-L5 | **yes**: exactly the stale leaves B reports |

## 3. Adjudication of the panel

Detail: `D-synthesis/02-ADJUDICATION.md`.

| Panel item | Panel severity | Adjudication | Consolidated |
|---|---|---|---|
| RV7-B-H1 revocation effectiveness at first contact selected by listing | HIGH | **CONFIRMED HIGH**, extended (RV7-D-A01: admitter revocation; OP-11 (b) minimum) | RV7-H1 |
| RV7-B-H2 C3 currency names a state of unbounded age | HIGH | **CONFIRMED HIGH** (CI instance narrowed to gate-less C3, RV7-D-A10) | RV7-H2 |
| RV7-C-H1 C3 proof bounds the event; air-gapped media | HIGH | **CONFIRMED HIGH; DUPLICATE** root cause of B-H2 | RV7-H2 |
| C: C1–C2 on an anchored chain is a new owner trade-off | claim | **REFUTED** (RV7-D-A09) | RV7-I3 |
| RV7-B-M1 one onboarding record designates both sources | MEDIUM | **CONFIRMED MEDIUM**, not carriable | RV7-M1 |
| RV7-B-L1 label-based supplier and toolchain independence | LOW | **CONFIRMED, re-rated MEDIUM** (-0002 precondition), merged | RV7-M2 |
| RV7-C-L4 OT-2 label and criterion | LOW | **CONFIRMED, re-rated MEDIUM**, merged | RV7-M2 |
| RV7-C-M1 protected-store loss discards the account-store high-water | MEDIUM | **CONFIRMED MEDIUM**, not escalated | RV7-M5 |
| RV7-C-M2, M3, M4, M5 | MEDIUM | **CONFIRMED MEDIUM** | RV7-M6 … M9 |
| RV7-B-L2 … L6 | LOW | **CONFIRMED LOW** | RV7-L1 … L5 |
| RV7-C-L1 (+ A23), L2, L3 | LOW | **CONFIRMED LOW** | RV7-L6 … L8 |
| RV7-B-I1, I2 | INFO | CONFIRMED | RV7-I1, I2 |
| B: BC6-1, BC6-2 narrowed; BC6-3 closed; BC6-4 narrowed; RV6-H1/H2 closed as stated; RV6-H3 closed | status | CONFIRMED | §8 |
| B: OT-1 genuine owner trade-off | assessment | **SUPERSEDED** by -0002; its cadence and `win` points stand (RV7-L3, RV7-H1) | — |
| B: OT-2 not a new owner trade-off | assessment | CONFIRMED | — |
| C: R2-H4 CLOSED as a class | status | **CONFIRMED** (matrix7 reproduced) | §8 |
| C: CUR-R1 ACCEPTED | determination | **REFUTED** (omission, RV7-H1) | §6 |

## 4. Consolidated findings

Full statements: `10-BLOCKING-FINDINGS.md`.

| ID | Severity | Title | Origin | Adjudication |
|---|---|---|---|---|
| **RV7-H1** | **HIGH** | Restrictive facts issued by authorities other than the trust-state authority take effect at first contact only if a Trust State lists them; no party establishes the listing or bounds its delay | B + D | CONFIRMED HIGH, extended |
| **RV7-H2** | **HIGH** | Running-machine C3 currency bounds the anchoring event, not the named Trust State's age; deviates from -0002 OT-1 | B + C | CONFIRMED HIGH; consolidated |
| **RV7-M1** | MEDIUM (blocking) | One onboarding record designates both first-contact sources; the stated root omits `{onboard}` | B | CONFIRMED |
| **RV7-M2** | MEDIUM (blocking) | Certification independence criteria are label comparisons; CC-3 not executable; owner label not adopted (-0002 OT-2) | D + B + C | NEW; B-L1, C-L4 re-rated and merged |
| **RV7-M3** | MEDIUM (blocking) | One toolchain lineage plus the other supplier class yields accepted malicious bytes outside the stated bounds | D | NEW |
| **RV7-M4** | MEDIUM (blocking) | A clean CI runner cannot answer `project_first_use`; the claimed C1–C2 is unreachable | D | NEW |
| RV7-M5 | MEDIUM | First admission after protected-store loss discards a surviving high-water | C | CONFIRMED, carried |
| RV7-M6 | MEDIUM | No realizable per-project record identity | C | CONFIRMED, carried |
| RV7-M7 | MEDIUM | Journal honouring unreachable for a first install | C | CONFIRMED, carried |
| RV7-M8 | MEDIUM | `git clean -fdx` in the crash window defeats R-INIT-9 | C | CONFIRMED, carried |
| RV7-M9 | MEDIUM | Roll-forward depends on the in-memory ARO | C | CONFIRMED, carried |
| RV7-M10 | MEDIUM | Shared conformance vectors detect 14 of 22 held-out regressions | D | NEW, carried |
| RV7-L1 | LOW | Trust-root schema accepts root-held purposes at threshold 1 | B | CONFIRMED |
| RV7-L2 | LOW | Custodian without history publishes a drop | B | CONFIRMED |
| RV7-L3 | LOW | No Trust State issuance and publication cadence rule | B | CONFIRMED |
| RV7-L4 | LOW | Stale committed outputs; runner not self-contained | B | CONFIRMED |
| RV7-L5 | LOW | No genesis procedure for the custodians' verifier | B | CONFIRMED |
| RV7-L6 | LOW | Recovery undo readings; uninstall result inconsistent | C | CONFIRMED, merged |
| RV7-L7 | LOW | Clock high-water poisoned by the machine's own wrong-ahead clock | C | CONFIRMED |
| RV7-L8 | LOW | `floors.json` / `high-water.json` atomicity unstated | C | CONFIRMED |
| RV7-L9 | LOW | `clock_reset` has no replay or persistence semantics | D | NEW |
| RV7-L10 | LOW | Air-gapped second-channel procedure unstated | D | NEW |
| RV7-L11 | LOW | Wildcard `informational` subtree accepts new authority-bearing keys | D | NEW instance of carried CR4-B-05 |
| RV7-L12 | LOW | Unflagged security-relevant change not listed (RV6-L1) | r6 | CONFIRMED open |
| RV7-I1 | INFO | OP-8 independence is mechanically distinct ids only | B | CONFIRMED |
| RV7-I2 | INFO | ARCH-0002 has no `human_approved` field | B | CONFIRMED |
| RV7-I3 | INFO | -0002 read with OP-7 (a): C1–C2 within validity stands; no new owner trade-off | D | NEW |
| RV7-I4 | INFO | `17` keeps excluded-mode rows under a non-production banner | D | NEW |
| RV7-I5 | INFO | Caller-declared role (RV6-I1) | r6 | unchanged |
| RV7-I6 | INFO | Binding-group derivation carried (RV6-I2) | r6 | unchanged |

No CRITICAL finding.

## 5. HO-0001 §3 owner requirements and the owner records

Detail: `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md`.

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure | **SATISFIED** | CSI 78/78 and checks reproduced; RV5-D-A05 and RV6-D-A03 re-run by B; RV7-D-A07 K1, K3 default deny. Carried: RV7-L11, RV7-L12. |
| §3.2 New-machine trust bootstrap | **NOT SATISFIED** | Fails: first install, CI image build, re-admission (RV7-H1); old epoch, restored, offline returning, air-gapped C3 (RV7-H2); clean CI runner governed use (RV7-M4). Holds: unanchored and expired machines C0; R-CLK-1; admission age; two machines; no `current`. |
| §3.3 Binary and root authenticity | **SATISFIED** as a class | BA12r7 (0 accepts with ≤ 1 key); release-final ≥ 2; 2-of-3 registration and reproduction; FCA at root threshold; non-circular chain. Blocking residual and criterion defects recorded: RV7-M1, M2, M3. |
| §3.4 Legacy-binary damage containment | **SATISFIED** | matrix7 reproduced (R2-H4 0 violations; LP-1r 0 writes); struct7, gitops7, txn7. Carried: RV7-M6 … M9, RV7-L6. |
| §4 Forward-compatibility constraint | **SATISFIED** for classification | as §3.1; RV7-D-A07 |

| Owner record | Determination |
|---|---|
| OWNER-DESIGN-REQUIREMENTS-0001 | Conforms for Option C, OP-1 (compiled), OP-2 (b), OP-3, OP-5, OP-6 (a), OP-8, OP-9, OP-12 (a), OP-13 (b) mechanism, OP-14 (b) expiry, OP-15 (a), first-contact composer, environment manifest, scope and every exclusion. **Deviations:** OP-4 (RV7-H1), OP-7 (a) running C3 (RV7-H2), OP-10 (b) and OP-16 (b) independence by labels (RV7-M2), OP-11 (b) listing dependence (RV7-H1), OP-13 (b) stated consequence (RV7-M1). |
| OWNER-DESIGN-REQUIREMENTS-0002 **OT-1** | **A conforms** (immutable material from both channels; RV7-L10 text gap). **B deviates** for running-machine C3 (RV7-H2); admission conforms (FC-9); high-water after protected-store loss carried (RV7-M5). |
| OWNER-DESIGN-REQUIREMENTS-0002 **OT-2** | No interim certification, no fallback: **conforms**. Explicit, executable, non-circular criterion; not labels; the owner's label: **not met** (RV7-M2). The acceptance-without-certified-target precondition is therefore not met. |
| D-0008 / D-0007 state (HO-0022 §2b) | **conforms** |

## 6. Residual determinations

Detail: `D-synthesis/05-RESIDUALS.md`.

| Residual | Determination |
|---|---|
| **FC-R1′ / AD-1″, FC-R3′** | **NOT ACCEPTED as stated** (RV7-M1) |
| **CUR-R1**; FC-R5 for G_REVOKED | **NOT ACCEPTED** (RV7-H1) |
| **RS-1b**; RS-1c for C3 | **NOT ACCEPTED** (RV7-H2) |
| **TB-S2″, TA-12″** | **NOT ACCEPTED as stated** (RV7-M2, RV7-M3) |
| AD-2′ | ACCEPTED WITH CONDITION CR7-C-1 (strengthened) |
| RS-2b | ACCEPTED WITH CONDITION CR7-D-02 |
| RS-3, TG-2 | ACCEPTED WITH CONDITION CR4-B-01 |
| RR-2′, LR-4 | ACCEPTED WITH CONDITION CR7-C-2 (and RV7-M4 for runners) |
| CS-1 | ACCEPTED WITH CONDITION CR4-B-05, CR7-D-04 |
| Crash recovery; uninstall; C-2; C-4; RA-1 | ACCEPTED WITH CONDITION CR7-C-3…6; RT-123; RT-125; RT-198 |
| FC-R2′, FC-R5 (G_BYTES), RS-1 (C1–C2), RS-1c (C1–C2), RS-2, RS-4 (scoping), TB-1′, VR-B1′, TB-L4, TG-1, TG-3, TB-S1, TB-S1 (environment), TB-S3, TB-4, TB-4′, AV-S1, A8, CS-2, LR-1, LR-2, LR-3, layout durability | ACCEPTED |
| RS-5 | REMOVED BY EXCLUSION |

## 7. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; the architecture applies the owner's selections. |
| Complete? | **No.** The OP-3 Mode A × OP-11 (b) × clean-runner combination has no mechanism or stated consequence (RV7-M4). OT-1 and OT-2 are still presented as open (`21` §2, `35` §6); -0002 resolved them after revision 7. |
| Honest about security consequences? | **No.** CUR-R1 and CP-REVOKED (RV7-H1); RS-1b, `24` §5.2, §6, A-R7-08 (RV7-H2); CP-FC-ROOT and rule (25) (RV7-M1); CC-3 and rule (26) (RV7-M2); CP-TOOLCHAIN, CP-ENV, INV7-TC, INV7-ENV-B, `21` §4 (RV7-M3); `24` §5.2 CI C1–C2 (RV7-M4). |
| Owner parameters reopened? | **No.** Owner confirmation is needed only if the architect chooses a single designation atom (CD7-3 (1)) or a provisioned CI selection (CD7-4). |
| Genuinely new owner trade-off? | **None found.** |

## 8. Prior findings, consolidated status

| Finding or class | Status | Basis |
|---|---|---|
| BC6-1 / RV6-H1 | **CLOSED as stated**; class **NARROWED → RV7-M1** (designation) | FA7, PROF7, RV7-B-CS7 A03 |
| BC6-2 / RV6-H2 | **CLOSED as stated** at admission; class **NARROWED → BC7-1 (RV7-H1)** and **BC7-2 (RV7-H2)** | CUR7, cur7x, RV7-B-A01, A02; RV7-D-A01 |
| BC6-3 / RV6-H3 | **CLOSED** | ENV7 |
| BC6-4 / RV6-M2 | **NARROWED → BC7-3** (RV7-M1, M2, M3) and RV7-M10 | REGISTER-CHECK, DA09r7, DA04r7; RV7-D-A02, A06 |
| R2-H4 | **CLOSED as a class** (confirmed again) | matrix7, struct7, gitops7, txn7 |
| RV6-M1, RV6-M6 (trust), RV6-L2 … L7, L9, L11, L12 | CLOSED (L8 in specification) | as B and C, reproduced |
| RV6-M3, M4, M6 (defence) | NARROWED → RV7-M5 … M9 | txn7, ident7, adm7x |
| RV6-M5 | CLOSED (model); carried CR6-C-9 | PPR7 |
| RV6-L1 | OPEN → RV7-L12 | RV6-B-A10 (B re-run) |
| RV6-L10; C-4, C-6 | NARROWED | matrix, gitops7 |
| C-2, C-3, C-5 | OPEN (carried) | specification only |
| RV6-I1, RV6-I2 | unchanged → RV7-I5, RV7-I6 | — |

## 9. Blocking classes: novelty and kind of fix (HO-0022 §2a)

| Class | Findings | Remainder of, or new | Root invariant not established | Kind of fix and route |
|---|---|---|---|---|
| **BC7-1** First-contact restrictive-fact listing | RV7-H1 | **Narrowed remainder of BC6-2** (first-contact currency) on negative and minimum-raising facts, intersecting **BC6-4** (no establishing party, no calculator strategy). New instances; not a new class. | Every restrictive fact issued by its dedicated authority takes effect at first contact within a stated, enforced bound, established first-hand by a party the root counts; the trust-state authority or its publication process cannot suppress it by omission. | **ENGINEERING_CORRECTION** (custodians hold issued restrictive statements first-hand and refuse unlisted ones beyond a compiled delay, or a negative-set code; executors apply every held statement; register; calculator; restated CUR-R1). Not an owner trade-off: OP-4 and OP-7 (a) already fix the parties and the cadence. Route: **architect**. |
| **BC7-2** Running-machine currency of the named state | RV7-H2 | **Narrowed remainder of BC6-2** on the running path and of **R2-H2** (stateless currency). New instances; not a new class. Deviation from -0002 OT-1. | Every C3 decision uses a Trust State issued within the compiled 24-hour ceiling of the decision clock, in addition to naming the effective state. | **ENGINEERING_CORRECTION** (compiled state age at C3 under R-CLK-1; restated RS-1b, R-CUR-1/2, `24` §5.2, A-R7-08; calculator). The owner decided the parameter and the media consequence in -0002. Route: **architect**. |
| **BC7-3** Stated consequences and certification criteria not derived from normative rules and established facts | RV7-M1, M2, M3; the false statements of H1, H2, M4 | **Remainder of BC6-4**, with **BC6-1**'s designation remainder (M1). **Materially new component:** the OT-2 certification criterion under -0002 (M2). | Every stated bound is computed from rules the text has, over atoms that match delivery rules; every certification criterion is an executable, non-circular procedure over evidenced provenance, never labels. | **ENGINEERING_CORRECTION** (independent designation or a stated single atom; executable CC-3 with bootstrap evidence and canonical identities; reproduction coverage rule or restated cross pairs; regenerated statements). Owner confirmation only if a single designation atom is kept. Route: **architect** (then owner only in that case). |
| **BC7-4** Clean CI runner governed use | RV7-M4 | **Materially new** (OP-3 Mode A × OP-11 (b) × HO-0001 §3.2 clean runner) | Every machine class's stated reachable classes are reachable under the gate rules. | **ENGINEERING_CORRECTION**, with a possible **owner confirmation**: CI-a (provisioned per-project selection), CI-b (bounded `ci` decision pin for `project_first_use`) or CI-c (runners do no governed project work); whether CI-a or CI-b satisfies OP-3's local human gate for "adoption" is for the owner to confirm. Route: **architect, then owner** if CI-a or CI-b. |

Each of BC7-1 … BC7-3 is the recurring rejection class, **a lower-trust input yielding a current, higher-trust fact**:

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC7-1 | the trust-state publication process (rank 3), or at most the trust-state threshold | a revoked binary or admitter as the current TCB; a superseded release as eligible |
| BC7-2 | a stored, replayed or re-stamped code; stale offline media (rank 5) | C3 currency "published as of now" on an old state; a revoked release installed |
| BC7-3 | one onboarding document; free-text provenance labels; an unstated calculator rule | the owner's view of the first-contact root, of independence and of residual bounds; a future CERTIFIED label |

BC7-4 fails closed (availability).

**Unavoidable core versus these classes.** A machine cannot know metadata it never received; an operator must know where the owner
publishes; OP-7 (a) lets an anchored machine run C1–C2 within anchor validity. Those are core and stated. The findings are an unbounded
omission by a party other than the issuing authority, a stored or media value of unbounded age selecting C3 currency, and stated bounds
computed from atoms or rules the text does not have.

## 10. Held-out attacks

This review authored **10** held-out attacks, RV7-D-A01 … A10 (`D-synthesis/03-HELDOUT-ATTACKS-RV7-D.md`).

| Evidence class | Attacks |
|---|---|
| Executed (reference executor, real toolchain, CSI checker, retained model) | A01, A02, A03, A05, A06, A07 |
| Computed | A02 (part C) |
| Design | A04, A08, A09, A10 |

| Required area (HO-0022 §2.3) | Attacks |
|---|---|
| Class-level interactions between the four R2 closures | A01, A02, A05, A10 |
| Owner-option combinations | A02, A03, A04, A08, A09 |
| Forward-compatibility constraint | A07 |
| Implementation plan's ability to detect regressions | A06 |

## Output files

| File | Content |
|---|---|
| `00-REVIEW-REPORT.md` | this report |
| `10-BLOCKING-FINDINGS.md` | every consolidated finding, HIGH to INFO |
| `11-CORRECTION-DELTA.md` | blocking classes, invariants, engineering corrections, owner-confirmation points, carried items, re-review entry criteria (recorded as evidence) |
| `D-synthesis/01-REPRODUCTION.md` | reproduction method, results, deviations |
| `D-synthesis/02-ADJUDICATION.md` | per-item adjudication of B and C |
| `D-synthesis/03-HELDOUT-ATTACKS-RV7-D.md` | held-out register RV7-D-A01 … A10 |
| `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` | HO-0001 §3/§4; -0001 and -0002 conformance; owner options |
| `D-synthesis/05-RESIDUALS.md` | residual criteria and determinations |
| `D-synthesis/evidence/` | probes, outputs, run scripts, reproduction logs and comparison, reviewed-content digests, README |
