# Independent architecture synthesis review (D) — RoT-1 revision 5 (Governance OS 4.1.6)

| | |
|---|---|
| **Architecture verdict** | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Run | AR-0014, role `rot-review-synthesis`, handoff `HO-0014` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at `cdb4e14009bba60bea9b805563c1b60e84f30b4b`; identical at this review's base (`git diff cdb4e14 59c1e5c` empty for those paths) |
| Panel verified | reviewer B `248f12a6b98c939ec2d9c3fef8045d9c19c82aae` (`BLOCKING_FINDINGS_PRESENT`); reviewer C `840d583273088caff4880c02edec03d2ade83156` (`NO_BLOCKING_FINDINGS`); both directories identical at base |
| Branch and base | `phase1/rot1-r5-review-d` from `59c1e5c` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 | Remain PROPOSED: record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`. This review approves nothing. Acceptance of an architecture would not be owner approval. |

## Scope

The whole of revision 5, as the architecture that governs 4.1.6, judged against the acceptance rule of HO-0014 §3 and the
owner requirements of HO-0001 §3–§4. The review covers:
- reproduction of every panel probe behind a HIGH claim or a claim that a prior HIGH is closed, and of the architect's
  instruments;
- adjudication of every B and C finding;
- held-out attacks RV5-D-A01…A08;
- owner requirements, residuals and owner options;
- for each blocking class, its novelty and the kind of fix it needs (HO-0014 §2a).

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, specialist proposal, reviewer B or C work, or prior
  review.
- **Orchestration files read:** `HO-0014`, `HO-0001` and `AGENT_RUNS/README.md` only. Orchestrator state, ledger,
  checkpoints, run records, other handoffs and `AGENT_RUNS/*.report.yaml` were not opened.
- **Disclosure: memory index.** The host session context included the user's auto-memory index: one-line summaries of
  earlier Governance OS reviews. No memory file was opened; nothing in this review rests on it.
- **Disclosure: repository clone.** Reviewer C's `register5.py` reads `cli/src/main.rs` at each release commit with
  `git show`. For that, the repository was cloned into scratch, which copies every ref. Only `59c1e5c` and the four release
  commits named by that script were read. No other branch was listed or inspected.
- **Not inspected:** other branches, other worktrees, other scratch directories.
- **Treated as claims:** the architect's response matrix (`22`), class-remainder analysis (`28`), `SYNTHESIS.md` and
  evidence, and every statement in reviewer B's and C's directories.
- **Reuse:** every instrument ran unmodified from scratch copies (architect, reviewer B, reviewer C, reviews r3 and r4).
- **Hygiene:** `D-synthesis/01-REPRODUCTION.md`.

## 1. Verdict against the acceptance rule (HO-0014 §3)

| Condition | Result |
|---|---|
| No open CRITICAL or HIGH after adjudication | **Not met.** 3 HIGH: RV5-H1, RV5-H2, RV5-H3 (`10-BLOCKING-FINDINGS.md`) |
| Every HO-0001 §3 requirement `SATISFIED` as a class | **Not met.** §3.1, §3.2, §3.3 `NOT SATISFIED`; §3.4 `SATISFIED` (§5) |
| Every open MEDIUM carried as a bound, testable requirement; none needs an architecture change | **Met.** RV5-M1 … RV5-M9 carried with acceptance tests (`11` §6). RV5-B-H3's route alone is re-rated to MEDIUM; its class is HIGH through D-A01 (§3). |
| Every residual explicitly bounded under attack | **Not met.** AD-1, TB-S2 (build environment), TB-4′ (content) and CS-2 are not accepted (§6). |
| Owner options complete and honest, none pre-decided | **Not met** for honesty and completeness (§7). Met for "none pre-decided". |

**Verdict: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.** The correction is architectural and stated as classes in
`11-CORRECTION-DELTA.md`.

### What revision 5 does close (confirmed by reproduction)

- **RV4-H1 as stated.**
  - One key of any purpose, with or without pipeline input, does not mint a binary.
  - `release-artifact` and `build-attestation` are withdrawn.
  - The reproduction quorum and conflict rule hold.
  - Evidence: CS5 byte-identical (408 configurations, 0 invariant failures); P4r5 VA5 rows.
- **RV4-H2 as stated.**
  - Revoked, remediated and moved-tag first binaries are refused.
  - The candidate is never executed; installation is from the measured buffer.
  - Ceremonies on unadmitted genuine binaries are refused.
  - Evidence: FA5 byte-identical, 45/45.
- **RV4-H3 as stated.**
  - `release-final` mixes are refused under every claimed identity.
  - The `ASIA…` file stays excluded on real 4.1.5.
  - Evidence: REG5 byte-identical; self-test 71/71.
- **R2-H4 as a class.**
  - No legacy write under `governance/trust/**` or the occupation is left `COMPLETE`.
  - Evidence: reviewer C's `matrix5` re-run (30,165 rows, 0 violations; `--root` 1,335 rows, 0 writes); review r4 C's
    10,618-invocation matrix and the architect's P3r3 and ST5, reproduced.
- **Carried closures:** CR4-B-06 … CR4-B-10; the stateful clock high-water; CR4-B-07 option 1; the 20 D-A03 oracle mutants
  (DA03r5 byte-identical).

## 2. Reproduction table

Detail: `D-synthesis/01-REPRODUCTION.md`; log `D-synthesis/evidence/reproduction/REPRODUCTION-LOG.json`.

| Probe (owner) | Behind claim | Reproduced |
|---|---|---|
| CSI `selftest` and `check` ×5 (architect) | BC4-3 closure | **yes**: 71/71; exits 0/3/2/2/2 (identical except a path field) |
| P1r4, P4r4 (architect) | retained BC-1 and BC-2 closures | **yes**, byte-identical |
| P4r5 (architect) | RV4-H1 closed as stated; B's CLOSED claims | **yes**, byte-identical (65/65, 42/42, 0 attack rows expecting `ACCEPTED`) |
| DA03r5 (architect) | RV4-M7 closure | **yes**, byte-identical (20/20, 17/17) |
| FA5 ×2 (architect) | RV4-H2 closed as stated | **yes**, byte-identical to the committed blob, both runs |
| REG5 on 4.1.5 (architect) | RV4-H3 closed as stated | **yes**, byte-identical |
| CS5 (architect) | RV4-H1 closed as stated; baseline of B-H1/H2/H3 | **yes**, byte-identical |
| SRC5 (architect) | `30` §4.1 | **verdicts only**: 16 digest leaves differ; the function tested is not the specified one (confirms RV5-B-M4) |
| RV5-B-A01 (B) | **RV5-B-H1** | **yes**, byte-identical |
| RV5-B-A04 (B) | **RV5-B-H1, H2, H3**, M1, L5 | **yes**, byte-identical |
| RV5-B-A08 (B) | **RV5-B-H2** | **yes**: every verdict identical; digests compiler-dependent |
| RV5-B-A09 (B) | **RV5-B-H3**, M2 | **yes**, byte-identical |
| RV5-B-A05, A12 (B) | M4; §3.2 | **yes** (A05 verdicts; A12 byte-identical) |
| review r4 B model, arch functions, surface probes; review r3 copies; review r4 D-A03, A03b | retained claims | **yes** (surface part P exit 5, as B reports) |
| reviewer C `register5`, `gitops5`, `matrix5`, `admit_tx` | **R2-H4 CLOSED**; C-M1, M2, L1–L3 | **yes**: byte-identical, or identical except paths and `elapsed`; `admit_tx` A11 race nondeterministic |
| reviewer C `repro_prior.sh`: review r4 C `subdir_escape`, `durability`, `legacy_regain`, 10,618-row matrix; review r4 D-A01; architect ST5 ×5; P3r3 | RV4-M1 closure; LP-1r | **yes**: byte-identical, or equal in every compared aggregate; ST5 D-A01 N2 differs only in run-dependent legacy file names |

## 3. Adjudication of the panel

Detail: `D-synthesis/02-ADJUDICATION.md`.

| Panel item | Panel severity | Adjudication | Consolidated |
|---|---|---|---|
| RV5-B-H1 first admission selected by the channel alone | HIGH | **CONFIRMED HIGH**, extended by D-A02 (evaluator selected by one channel under OP-13 (b)) | RV5-H1 |
| RV5-B-H2 build image selects the bytes | HIGH | **CONFIRMED HIGH** | RV5-H2 |
| RV5-B-H3 policy-root content under OP-2 (b) | HIGH | **CONFIRMED**. As B states it the route needs the designated registration authority at threshold, and would alone be MEDIUM. D-A01 shows the class at threshold 1 with honest custodians, so the consolidated finding is HIGH. B's proposed restrictor ("for its source") does not close D-A01 (computed). | RV5-H3 |
| RV5-B-M1 … M5 | MEDIUM | CONFIRMED MEDIUM | RV5-M1 … M5 |
| RV5-B-L1 … L6 | LOW | CONFIRMED LOW (L4 extended: `07` §3 and `04` V8 still name revision-4 source fields and artefact statements) | RV5-L1 … L6 |
| RV5-C-M1, M2 | MEDIUM | CONFIRMED MEDIUM | RV5-M6, M7 |
| RV5-C-L1, L2 | LOW | CONFIRMED LOW, extended to D-0008 rules (12) and (10) | RV5-L7, L8 |
| RV5-C-L3 | LOW | **DUPLICATE** of RV5-B-M3, consolidated at MEDIUM | RV5-M3 |
| B: RV4-H1/H2/H3 `CLOSED as stated` | status | CONFIRMED (reproduced) | §8 |
| B: BC4-3 `NARROWED → H3, M2` | status | CONFIRMED and widened (D-A01) | §8 |
| B: §3.2 `SATISFIED` for transport and repository adversaries | status | evidence reproduced; **not adopted as the class determination** (first install and workstation classes) | §5 |
| C: R2-H4 `CLOSED as a class` | status | CONFIRMED (reproduced) | §8 |
| C: `NO_BLOCKING_FINDINGS` | verdict | CONFIRMED within C's scope | — |

## 4. Consolidated findings

Full statements: `10-BLOCKING-FINDINGS.md`.

| ID | Severity | Title | Origin | Adjudication |
|---|---|---|---|---|
| **RV5-H1** | **HIGH** | The first TCB on a machine is selected by the independent channels alone: lineage and channel quorum by the typed fingerprint's own Trust Policy, evaluator by one channel; declared minima, AD-1 and the OP-9/12/13 consequences false | B + D | CONFIRMED HIGH, extended |
| **RV5-H2** | **HIGH** | The build environment selects the bytes of every production binary; no assigned authority, check, option or residual | B | CONFIRMED HIGH |
| **RV5-H3** | **HIGH** | Registered constitutional content is not established first-hand: {pipeline, `release-candidate`, `release-final`} (OP-4 "no": {pipeline, one key}) makes malicious non-orderable content effective everywhere; under OP-2 (b) also {two delegated custodians, `release-final`} | D + B | NEW class instance (D-A01) with B's route; CONFIRMED HIGH |
| RV5-M1 | MEDIUM | Revocation removes restrictors (conflict, REJECTED) | B | CONFIRMED |
| RV5-M2 | MEDIUM | Registration reductions exact-match and ceremony-side only | B | CONFIRMED |
| RV5-M3 | MEDIUM | Re-admission discards the monotonic verifier trust store; record placement | B + C | CONFIRMED (C-L3 duplicate) |
| RV5-M4 | MEDIUM | Source identity ambiguous; SRC5 tests another function | B | CONFIRMED |
| RV5-M5 | MEDIUM | Decision register incomplete and misclassified | B | CONFIRMED |
| RV5-M6 | MEDIUM | No `.gitattributes`: line-ending conversion corrupts kernel bytes (fail closed) | C | CONFIRMED |
| RV5-M7 | MEDIUM | Out-of-project ignore sources re-drop the occupation (fail closed) | C | CONFIRMED |
| RV5-M8 | MEDIUM | A user-writable installation can never anchor: C0 only under OP-7 (a)/(b)/(c without witnesses), not "C0–C2" | D | NEW |
| RV5-M9 | MEDIUM | The two executors of admission-predicate/1 disagree on AP-4/AP-5 cases; neither oracle carries them; `min_binary_version` unmodelled | D | NEW |
| RV5-L1 | LOW | Reference executor selects lineage by bundle order | B | CONFIRMED |
| RV5-L2 | LOW | Unsigned admission record honoured by digest | B | CONFIRMED |
| RV5-L3 | LOW | Clock set back on restored or long-offline machines | B | CONFIRMED |
| RV5-L4 | LOW | Contradictory and stale text | B + D | CONFIRMED, extended |
| RV5-L5 | LOW | Calculator victim classes incomplete | B | CONFIRMED |
| RV5-L6 | LOW | No minimum root threshold | B | CONFIRMED |
| RV5-L7 | LOW | LP-1s and rule (12) overclaim | C + D | CONFIRMED, extended |
| RV5-L8 | LOW | Transaction area outside §9.1/§9.2; rule (10) inconsistent | C + D | CONFIRMED, extended |
| RV5-L9 | LOW | OP-3 mode B consequence incomplete under CR4-B-07 option 1 | D | NEW |
| RV5-I1 | INFO | Acting role caller-declared | RV4-I1 | unchanged |
| RV5-I2 | INFO | Owner binding groups bind digests, not derivation (capability-contract phase) | D | NEW |

## 5. HO-0001 §3 owner requirements

Detail: `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` §1.

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure | **NOT SATISFIED** | **Holds:** inventory, default deny (RV4-L1 still open), floor modes, coverage checker (0/3/2/2/2), precedence and project override (P1r4), future unknown field (D-A05 N1 exit 2). **Fails:** sensitivity and indexing exclusions and the tool permission floor. Their non-orderable values are selected by {pipeline, `release-candidate`, `release-final`} (RV5-H3; D-A01 executed on 4.1.5: the `ASIA…` file indexed and served). |
| §3.2 New-machine trust bootstrap | **NOT SATISFIED** | **Holds for trust-state selection by transport and repository adversaries:** 296 machine × OP-7 × adversary rows, 0 `current`; C3 never on a thief descendant (A12 reproduced); replay; repository gate records. **Fails:** first install (RV5-H1); the user-writable installation class is misstated (RV5-M8); re-admission discards monotonic state (RV5-M3). |
| §3.3 Binary and root authenticity | **NOT SATISFIED** | **Holds:** no single key, with or without pipeline, mints a binary (CS5); running-mode chain non-circular (P4r5). **Fails:** the build environment selects the bytes and all compiled T0 (RV5-H2); at first contact one channel selects the evaluator and lineage (RV5-H1). |
| §3.4 Legacy-binary damage containment | **SATISFIED** | `matrix5` (30,165 rows) and the review r4 C matrix (10,618) reproduced; P3r3 and ST5 reproduced. Carried: RV5-M6, M7, L7, L8. |
| §4 Forward-compatibility constraint | **SATISFIED for classification** | D-A05 N1 default deny, N2 classified with existing vocabulary. The content of new kernel-shipped files inherits RV5-H3 (N3). |

## 6. Residual determinations

Detail: `D-synthesis/05-RESIDUALS.md`.

| Residual | Determination |
|---|---|
| RS-1, RS-1b, RS-1c, RS-5, OP-7 (d) | ACCEPTED |
| RS-2 | ACCEPTED WITH CONDITION RV5-L3, L4 |
| RS-3 | ACCEPTED WITH CONDITION CR4-B-01 |
| RS-4 | ACCEPTED as scoping (with CR5-B-12) |
| RS-B1 | ACCEPTED (stale page only) |
| **AD-1** | **NOT ACCEPTED** (RV5-H1) |
| AD-2 | ACCEPTED WITH CONDITION RV5-M3 |
| TB-1′ | ACCEPTED WITH CONDITION RV5-L2 |
| VR-B1 | ACCEPTED WITH CONDITION RV5-M8 |
| TB-S1 | ACCEPTED WITH CONDITION RV5-M1 |
| **TB-S2** | ACCEPTED for the toolchain archive; **NOT ACCEPTED** as covering the build environment (RV5-H2) |
| TB-S3, TB-4, AV-S1, TB-L4 | ACCEPTED |
| **TB-4′** | ACCEPTED for binaries; **NOT ACCEPTED** for constitutional content (RV5-H3) |
| CS-1 | ACCEPTED WITH CONDITION CR4-B-05 |
| **CS-2** | **NOT ACCEPTED** (RV5-H3) |
| VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3, LR-1, LR-2 | ACCEPTED |
| VR-3, TG-2 | ACCEPTED WITH CONDITION CR4-B-01 |
| RR-2 | ACCEPTED WITH CONDITION RV5-M3, M5 |
| LR-3 | ACCEPTED WITH CONDITION RV5-L8 |
| LR-4 | ACCEPTED WITH CONDITION CR4-B-04 |
| Layout durability (line endings; ignore sources) | ACCEPTED WITH CONDITION RV5-M6, M7 |

## 7. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; OP-1…OP-15 are pending with no proposal. Text inconsistency: `24` §9 keeps revision 4's labelled OP-7 proposal (RV5-L4). |
| Honest about security consequences? | **No.** See the list below. |
| Complete? | **No.** No option sizes the first-contact root beyond one or two owner channels (CD5-1). No option covers the common-mode build environment (CD5-2). No statement of the workstation installation burden (RV5-M8). |

Consequence statements found false or incomplete:
- OP-2, OP-4, OP-8: constitutional content (RV5-H3).
- OP-9, OP-12, OP-13: first admission (RV5-H1).
- OP-10: build environment (RV5-H2).
- OP-7, OP-12, OP-14: user-writable installs (RV5-M8).
- OP-14 (b), OP-15 (a): re-admission (RV5-M3).
- OP-3: mode B (RV5-L9).
- OP-1: minimum threshold (RV5-L6).
- `21` combinations: 10 of 15 examined combinations that change security are absent or wrong (D-A06).

## 8. Prior findings, consolidated status

| Finding | Status | Basis |
|---|---|---|
| RV4-H1 / BC4-1 | RV4-H1 as stated **CLOSED**; class **NARROWED → RV5-H2** (build environment) and RV5-H1 (evaluator at first contact) | CS5, P4r5 reproduced; B-A08 |
| RV4-H2 / BC4-2 | RV4-H2 as stated **CLOSED**; class **NARROWED → RV5-H1** | FA5 reproduced; B-A01, D-A02 |
| RV4-H3 / BC4-3 | RV4-H3 as stated **CLOSED**; class **NARROWED → RV5-H3** | REG5 reproduced; D-A01, B-A06 |
| BC4-4 | **OPEN → CD5-4** | §7 |
| R2-H4 | **CLOSED as a class** (confirmed again) | `matrix5`, review r4 C matrix, P3r3, ST5 reproduced |
| RV4-M1 | CLOSED for trust paths and occupation; remainder RV5-L8 | `matrix5` |
| RV4-M2 | NARROWED (specification only; CR4-B-01) | design |
| RV4-M3 | CLOSED by rule (specification only; RT-149) | design |
| RV4-M4 | NARROWED → RV5-L3 | A12, P4r5 CLOCK |
| RV4-M5 | CLOSED (selector); CR4-B-04 specification only | REG5 |
| RV4-M6 | CLOSED against the project `.gitignore`; remainder RV5-M7 | `gitops` |
| RV4-M7 | CLOSED for the 20 mutants; new gaps RV5-M9 | DA03r5; D-A04 |
| RV4-L1 | OPEN (CR4-B-05) | review r4 B part U |
| RV4-L2 … L5, L9, L10 | CLOSED | P4r5; self-test |
| RV4-L6 | CLOSED as stated; side effect RV5-M1 | FA5; B-A03 |
| RV4-L7 | NARROWED → RV5-H3 (OP-4 statement) | D-A01 |
| RV4-L8 | CLOSED for `release-final` alone; remainder RV5-H3 | D-A01 |
| RV4-I1 | unchanged → RV5-I1 | — |

## 9. Blocking classes: novelty and kind of fix (HO-0014 §2a)

| Class | Findings | Remainder of, or new | Root invariant not established | Kind of fix |
|---|---|---|---|---|
| **BC5-1** First-contact root of trust | RV5-H1 | **Narrowed remainder of BC4-2** (R2-H2/BC-2 ∩ R2-H3/BC-3) at its intersection with BC4-4. The instance is new (lineage, quorum, evaluator at first admission); the class is not materially new. | On first admission, every selector (lineage, state, required channel agreement, evaluator) is either an authenticated value that the values it governs cannot select, or the consulted channel set stated exactly as the first-contact root; the channel quorum is enforced independently of what the channels select, for every first-contact value. | **ENGINEERING_CORRECTION** (compiled quorum over all first-contact values, evaluator binding, exact residual, computed minima) **plus OWNER_TRADE_OFF**: which first-contact sources form the root. Options T1-a one channel; T1-b two channels under distinct custody; T1-c an independent second authentication path (a third-party signing party joins the TCB); T1-d physical provisioning (operational burden). Consequences in `11` CD5-1. |
| **BC5-2** Byte-determining build environment | RV5-H2 | **Narrowed remainder of BC4-1** (R2-H3/BC-3). The instance is new (the environment; CS5 modelled only the toolchain archive); the class is not materially new. | Every input that determines a binary's bytes has a first-hand-established selector or is a stated residual; the pipeline selects none; a quorum counts only across environments that share no unestablished input. | **ENGINEERING_CORRECTION** (assign authority, pinned and reproduced environment, calculator atoms, test) **plus OWNER_TRADE_OFF**: the common-mode environment. Options E-a accept upstream components (residual: their compromise); E-b environment diversity (cost, target restrictions); E-c owner-built environment (cost). Consequences in `11` CD5-2. |
| **BC5-3** First-hand constitutional content | RV5-H3 | **Narrowed remainder of BC4-3** (R2-H1/BC-1) at its intersection with BC4-1's first-hand principle. The instance is new (the registration signs content it did not establish); the class is not materially new. | Effective constitutional content is derived first-hand at the registration's authority, bound to verification of exactly the registered candidate; E7 applies AP-5's restrictors; no threshold-1 release key plus pipeline selects content. | **ENGINEERING_CORRECTION** only: D-A01 shows two mechanisms that refuse with no new residual. |
| **BC5-4** Complete register and derived statements | option statements; RV5-M5 | **Remainder of BC4-4** | Every consequence statement is derived from a complete decision register whose selector substitutions are calculator strategies | **ENGINEERING_CORRECTION** |

Each blocking class is the recurring rejection class: **a lower-trust input yielding a current, higher-trust fact**.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC5-1 | one channel page | the root of trust, the evaluator and the first TCB |
| BC5-2 | an image record of no assigned authority | the bytes of every production binary |
| BC5-3 | release pipeline + threshold-1 candidate and final keys | the effective constitutional content of a registered release |

## 10. Held-out attacks

This review authored **8** held-out attacks, RV5-D-A01 … A08 (`D-synthesis/03-HELDOUT-ATTACKS-RV5-D.md`).

| Evidence class | Attacks |
|---|---|
| Executed + computed | A01 (checker, real 4.1.5, P4r5), A04 (reference executor with real Ed25519, P4r5) |
| Executed | A05 (checker) |
| Computed | A03 (reference `gov_run`, P4r4), A07 (CS5 module, plan, register) |
| Design, with references to executed or computed rows | A02, A06, A08 |

| Required area (HO-0014 §2.3) | Attacks |
|---|---|
| Class-level interactions between the four R2 closures | A01, A03, A08 |
| Owner-option combinations | A02, A06 (and the OP-4 and OP-7 rows of A01, A03) |
| Forward-compatibility constraint | A05 (and A01's breadth) |
| Implementation plan's ability to detect regressions | A04, A07 |

## Output files

| File | Content |
|---|---|
| `00-REVIEW-REPORT.md` | this report |
| `10-BLOCKING-FINDINGS.md` | every consolidated finding, CRITICAL to INFO |
| `11-CORRECTION-DELTA.md` | blocking classes, invariants, engineering corrections, owner trade-offs with options, carried items, re-review entry criteria |
| `D-synthesis/01-REPRODUCTION.md` | reproduction method and results |
| `D-synthesis/02-ADJUDICATION.md` | per-item adjudication of B and C |
| `D-synthesis/03-HELDOUT-ATTACKS-RV5-D.md` | held-out register RV5-D-A01 … A08 |
| `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` | HO-0001 §3/§4 sub-items; owner options |
| `D-synthesis/05-RESIDUALS.md` | residual criteria and determinations |
| `D-synthesis/evidence/` | probes, outputs, reproduction log and scripts, reviewed-content digests, README |
