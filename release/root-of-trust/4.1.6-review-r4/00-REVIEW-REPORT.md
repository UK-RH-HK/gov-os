# Independent architecture synthesis review (D) — RoT-1 revision 4 (Governance OS 4.1.6)

| | |
|---|---|
| **Architecture verdict** | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Run | AR-0008, role `rot-review-synthesis`, handoff `HO-0008` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` at `bca05a7e2c2791126fde1d3d812facdaa45b2e45`; identical at this review's base (`git diff bca05a7 HEAD` empty for those paths) |
| Panel verified | reviewer B `152e68e58655649d97382ac3dca64ea7510f5828` (`BLOCKING_FINDINGS_PRESENT`); reviewer C `c6b8ba9985d195fd18470cfe3ae3d80968d71051` (`BLOCKING_FINDINGS_PRESENT`); both directories identical at base |
| Branch and base | `phase1/rot1-r4-review-d` from `9349d8c65c4d4fda06116ec336f0d2dd458d8524` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 | Remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). This review approves nothing. Acceptance of an architecture would not be owner approval. |

## Scope

The whole of revision 4 as the architecture that governs 4.1.6, judged against the acceptance rule of HO-0008 §3 and the
owner requirements of HO-0001 §3–§4: reproduction of the panel's decisive probes and the architect's instruments;
adjudication of every B and C finding; held-out attacks RV4-D-A01…A10; owner requirements; residuals; owner options; and
the novelty of each blocking class.

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, not reviewer B's or C's work, no prior review.
- **Orchestration files read:** `HO-0008`, `HO-0001` and `AGENT_RUNS/README.md` only. Orchestrator state, ledger,
  checkpoints, run records, other handoffs and `AGENT_RUNS/*.report.yaml` were not opened.
- **Disclosure.** The session context supplied by the host included the user's auto-memory index: one-line summaries of
  earlier Governance OS reviews. No memory file was opened. Nothing in this review rests on it.
- **Not inspected:** other branches, other worktrees, other scratch directories.
- **Treated as claims:** the architect's response matrix (`22`), class-remainder analysis (`28`) and evidence, and every
  statement in B's and C's directories.
- **Scripts reused as committed:** the architect's and B's scripts ran from this worktree. C's scripts ran from this
  worktree with its documented `AR7_WT` variable set to this worktree; no file was edited.
- **Hygiene:** every probe ran under `env -i` in `…/scratchpad/ar-0008/`, with `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` in
  scratch, `PYTHONDONTWRITEBYTECODE=1`, and no other `GOV_*` in any child. Legacy binaries were used read-only (SHA-256 in
  `D-synthesis/evidence/REPRODUCTION-LOG.json`). The canonical checkout was never written. The worktree was verified clean,
  including ignored files, before each commit.

## 1. Verdict against the acceptance rule (HO-0008 §3)

| Condition | Result |
|---|---|
| No open CRITICAL or HIGH after adjudication | **Not met.** 3 HIGH: RV4-H1, RV4-H2, RV4-H3 (`10-BLOCKING-FINDINGS.md`) |
| Every HO-0001 §3 requirement `SATISFIED` as a class | **Not met.** §3.1, §3.2, §3.3 `NOT SATISFIED`; §3.4 `SATISFIED` (§5) |
| Every open MEDIUM carried as a bound, testable requirement; none needs an architecture change | **Met.** RV4-M1 … RV4-M7 carried with acceptance tests (`11` §6). RV4-C-H1 is re-rated to MEDIUM (RV4-M1) with reasons (§3). |
| Every residual explicitly bounded under attack | **Not met.** TB-1, TB-3, CS-2 and RS-2 are not accepted as stated (§6). |
| Owner options complete and honest, none pre-decided | **Not met** for honesty and completeness: OP-2, OP-4 and OP-6 consequences are materially incorrect or incomplete; the `release-final` blast radius is mis-stated (§7). Met for "none pre-decided". |

**Verdict: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.** The correction is architectural and stated as classes in
`11-CORRECTION-DELTA.md`.

### What revision 4 does close (confirmed by reproduction)

- **BC-1 as stated by review r3 (RV3-H1).** Kernel precedence is refused unless equal to its registration and never enters
  effective policy; deletion is refused; the order is sound in both directions; TPS tightenings are computed reductions;
  project strength is evaluated over effective policy. P1r4 on real 4.1.5 byte-identical; CSI self-test 56/56; checker exits
  0/3/2/2/2; review-r3 A01, lattice and removal probes identical.
- **BC-2 as stated (RV3-H2).** Inclusion anchors, pin validity, currency proofs, the witness purpose and the absence of a
  `current` label. P4r4 byte-identical (54/54, 9/9 mutants); B's independent model byte-identical (336 rows, 0 unstated,
  0 `current`).
- **BC-3 as stated (RV3-H3).** A `release-final` key cannot choose a binary's source (VA4 byte-identical).
- **Legacy containment for root-anchored invocations.** 2,504 `--root` invocations of the real 4.1.2–4.1.5 registers on
  three layout variants write nothing (C's matrix reproduced).
- **Carried items closed:** RV3-M1, M3, M4, M8; RV3-L1, L3 (checker), L4, L5, L6, L8.

## 2. Reproduction table

Detail: `D-synthesis/01-REPRODUCTION.md`; log `D-synthesis/evidence/REPRODUCTION-LOG.json`.

| Probe (owner) | Behind claim | Reproduced |
|---|---|---|
| CSI `selftest` (architect) | BC-1 closure; B `CLOSED` BC-1 | **yes**: 56 passed, 0 failed |
| CSI `check` framework / 4.1.5 / 4.1.2 / 4.1.3 / 4.1.4 (architect) | exits 0/3/2/2/2 | **yes** |
| P4r4 model (architect) | BC-2 closure; B `CLOSED` RV3-H2, RV3-M1, M3, M4, M8 | **yes**, byte-identical |
| VA4 (architect) | BC-3 closure; the route B row behind **RV4-B-H1** | **yes**, byte-identical |
| P1r4 on real 4.1.5 (architect) | BC-1 closure; RV3-M5 | **yes**, byte-identical |
| `RV4-B-M-reference-model` (B) | **RV4-B-H1** (`BC`), **RV4-B-H2** (`FB`), M2, M3, L2–L4; 336-row matrix | **yes**, byte-identical |
| `RV4-B-arch-functions` AF1–AF3 (B) | **RV4-B-H1**, **RV4-B-H2** | **yes**, byte-identical |
| `RV4-B-surface-probes` U, T, P on real 4.1.5 (B) | **RV4-B-H3** (P), L1 (U), A10 (T) | **yes**, byte-identical |
| `RV4-B-confinement-and-first-binary` on real 4.1.5 (B) | **RV4-B-H2** part B; M1 part A | **yes**, byte-identical |
| B's copies of review-r3 probes: RV3-B-A01, A03/A14/A16, I01–I09, r2 P2, D lattice, D surface removal | B's `CLOSED` RV3-H1 and carried-item statuses | **yes**: identical except scratch path strings in two outputs |
| C `build_trees` | base trees | **yes** (exit 0) |
| C `subdir_escape` on real 4.1.5 | **RV4-C-H1** | **yes**, identical JSON |
| C `durability` | RV4-C-M1; durability | **yes**, identical JSON |
| C `legacy_regain` | LR-2 bound holds | **yes**, identical JSON |
| C `matrix` (4 real binaries, 10,618 invocations, 168 chains) | **RV4-C-H1**; `--root` property; R2-H4 status | **yes**: 10,618 rows; identical aggregates per layout × position; 56 rows writing `governance/trust/**`; identical state counts and writing commands |

## 3. Adjudication of the panel

Detail: `D-synthesis/02-ADJUDICATION.md`.

| Panel item | Panel severity | Adjudication | Consolidated |
|---|---|---|---|
| RV4-B-H1 one attestation key + pipeline input yields an accepted malicious binary | HIGH | **CONFIRMED HIGH**, extended by D-A07 (OP-2 (iii) does not help) | RV4-H1 |
| RV4-B-H2 first-binary acceptance outside anchors, negatives and currency; self-report; Phase 4 self-verification | HIGH | **CONFIRMED HIGH**, extended by D-A04 (first-install ceremonies on the unaccepted binary; OP-6) | RV4-H2 |
| RV4-B-H3 pinned registrations not release-bound | HIGH | **CONFIRMED HIGH**, broadened by D-A02 (tool descriptors, invariants, schemas, skills) and D-A06 (no gate on Git-delivered use) | RV4-H3 |
| RV4-C-H1 subdirectory escape writes the PPS with `COMPLETE` | HIGH | **CONFIRMED (reproduced), re-rated MEDIUM**, extended by D-A01 and D-A09 | RV4-M1 |
| RV4-B-M1 confinement deny list | MEDIUM | CONFIRMED MEDIUM | RV4-M2 |
| RV4-B-M2 witness input and custody | MEDIUM | CONFIRMED MEDIUM | RV4-M3 |
| RV4-B-M3 RS-2 bound nonexistent | MEDIUM | CONFIRMED MEDIUM | RV4-M4 |
| RV4-B-M4 unrecorded migration weakening | MEDIUM | CONFIRMED MEDIUM | RV4-M5 |
| RV4-C-M1 retained `.gitignore` line | MEDIUM | CONFIRMED MEDIUM | RV4-M6 |
| RV4-B-L1 … L7 | LOW | CONFIRMED LOW (L1 executed, L2–L4 computed, all reproduced; L5–L7 design) | RV4-L1 … L7 |
| RV4-B-I1 caller-declared role | INFO | CONFIRMED INFO | RV4-I1 |
| B: BC-1 `CLOSED`; RV3-H2 and RV3-H3 `CLOSED` as stated | status | CONFIRMED (reproduced) | §8 |
| C: "R2-H4 NOT CLOSED as a class" | status | **REFUTED as stated.** The class property of HO-0001 §3.4 (no silent mutation of the kernel or trust state into a state treated as valid) holds on D-A01's evidence; the containment argument's scope gap is carried as RV4-M1 | §8 |

**Why RV4-C-H1 is MEDIUM, not HIGH.**
- **What was shown.** Silent, persistent legacy writes under `governance/trust/**` while `18` §9 reports `COMPLETE`
  (reproduced), and, beyond C, nested installs from `governance/` and `governance/trust/kernel/` that make every legacy
  command operational beneath them (D-A01).
- **What the writes reach.** An edited installed kernel file is `KERNEL_TAMPERED` and a deleted trust lock gives
  `PARTIAL`: both fail closed. PPS litter enters no trust decision. An overlay rewrite leaves the state `COMPLETE`, is
  reported `PROJECT_STRENGTH_WEAKENED` where the vector was recorded, and is accepted by fresh clones under LR-4, the bounds
  review r3 accepted for LR-2.
- **What C claimed.** C states that no enforcement bypass was demonstrated.
- **Why it is carriable.** The correction tightens the `COMPLETE` predicate, defines root discovery, restates rules (10)
  and (12) and LR-2, and adds test positions. It changes no trust relationship.

## 4. Consolidated findings

Full statements: `10-BLOCKING-FINDINGS.md`.

| ID | Severity | Title | Origin | Adjudication |
|---|---|---|---|---|
| **RV4-H1** | **HIGH** | One threshold-1 attestation key plus pipeline input yields an accepted malicious production binary through honest custodians | B + D | CONFIRMED HIGH, extended |
| **RV4-H2** | **HIGH** | First-binary acceptance outside anchors, negatives and currency; self-reported comparisons; first-install ceremonies on the unaccepted binary | B + D | CONFIRMED HIGH, extended |
| **RV4-H3** | **HIGH** | Non-orderable registrations not release-bound: `release-final` restores superseded pinned, member or file content | B + D | CONFIRMED HIGH, broadened |
| RV4-M1 | MEDIUM | Subdirectory-rooted legacy commands escape the occupation defence; nested installs inside the PPS; `COMPLETE` examines no foreign entry | C + D | CONFIRMED, re-rated from HIGH, extended |
| RV4-M2 | MEDIUM | Confinement is a deny list: planted code later runs unconfined | B | CONFIRMED |
| RV4-M3 | MEDIUM | OP-7 (c) witness input and custody unspecified | B | CONFIRMED |
| RV4-M4 | MEDIUM | RS-2's rollback bound does not exist under OP-7 (a), (b), (d) or on stateless runners | B | CONFIRMED |
| RV4-M5 | MEDIUM | Computed weakening needs a recorded vector | B | CONFIRMED |
| RV4-M6 | MEDIUM | RV3-L7 fix depends on a replace-form `.gitignore` | C | CONFIRMED |
| RV4-M7 | MEDIUM | The conformance oracle detects 9 of 20 plausible single-rule regressions; 5 have no RT, including the "held" clause of inclusion anchors | D | NEW |
| RV4-L1 | LOW | Wildcard `informational` rule admits unknown keys | B | CONFIRMED |
| RV4-L2 | LOW | `WITNESSED` C3 contradicts the currency-proof definition | B | CONFIRMED |
| RV4-L3 | LOW | P1 "published as of" label inexact for later descendants | B | CONFIRMED |
| RV4-L4 | LOW | Accepted-TBM high-water gaps (stateless; first-run recording) | B | CONFIRMED |
| RV4-L5 | LOW | Decision pins have no maximum validity | B | CONFIRMED |
| RV4-L6 | LOW | A4a/A4b ignore revoked attestations | B | CONFIRMED |
| RV4-L7 | LOW | OP-4 consequence text garbled | B | CONFIRMED |
| RV4-L8 | LOW | `release-final` blast radius lists a gate that Git-delivered use never passes | D | NEW |
| RV4-L9 | LOW | OP-2 (S1) makes every binary release a computed reduction; cost omitted or rule mis-scoped | D | NEW |
| RV4-L10 | LOW | Owner-domain slots cannot bind a hash-bound contract set; multi-pin resolution undefined | D | NEW |
| RV4-I1 | INFO | Acting role caller-declared | B | CONFIRMED |

## 5. HO-0001 §3 owner requirements

Detail: `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md`.

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure | **NOT SATISFIED** | **Holds:** inventory; default deny (except RV4-L1); a floor mode per field; coverage check; precedence, presence and migration evolution; P1r4 harms flip. **Fails:** "schema evolution cannot silently introduce an unfloored setting" and the test-list items for sensitivity and indexing exclusions and the tool permission floor. A higher-sequence release restores a superseded secret pattern (executed on 4.1.5), tool descriptor, invariant, schema or skill with no reduction, gate or detector (RV4-H3). |
| §3.2 New-machine trust bootstrap | **NOT SATISFIED** | **Holds for trust state:** all seven machine classes, replay and repository gate records (B's 336-row model and P4r4 reproduced). **Fails:** on first install and on clean CI images, a transport or source adversary selects a revoked, remediated-malicious or self-reporting binary as the machine's TCB (RV4-H2); RS-2 as stated (RV4-M4). |
| §3.3 Binary and root authenticity | **NOT SATISFIED** | One threshold-1 attestation key plus pipeline input mints an accepted binary (RV4-H1); the first-binary chain is circular (RV4-H2). **Holds** for subsequent binaries: compiled roots, TPS, TSS, historical set, source not chosen by `release-final`. |
| §3.4 Legacy-binary damage containment | **SATISFIED** | Root-anchored registers write nothing (C reproduced). Subdirectory-rooted legacy writes never leave a changed kernel, trust statement, lock or occupation entry treated as valid (D-A01); overlay changes are bounded by the recorded strength vector and LR-4. Carried: RV4-M1, RV4-M6. |
| §4 Forward-compatibility constraint | **SATISFIED for classification** | New constitutional files are default-denied (B U07; review r3 D-A09 re-run identical); owner-domain slots classify the contract. RV4-H3's release binding and RV4-L10's set binding apply to new files too. |

## 6. Residual determinations

Detail: `D-synthesis/05-RESIDUALS.md`.

| Residual | Determination |
|---|---|
| RS-1 | ACCEPTED |
| RS-1b | ACCEPTED WITH CONDITION RV4-L3 |
| RS-1c | ACCEPTED |
| RS-2 | **NOT ACCEPTED as stated** (RV4-M4); acceptable once restated per CR4-B-03 |
| RS-3 | ACCEPTED WITH CONDITION RV4-M2 |
| RS-4 | ACCEPTED as scoping (CI `sudo` note, CR4-B-01 (d)) |
| RS-5 | ACCEPTED WITH CONDITION RV4-M3 |
| OP-7 (d) residual | ACCEPTED as owner-selectable |
| TB-1 | **NOT ACCEPTED** (RV4-H2); accepted-TBM part WITH CONDITION RV4-L4 |
| TB-2 | ACCEPTED only for what it bounds (rebuilder environment, not the key: RV4-H1) |
| TB-3 | **NOT ACCEPTED** (RV4-H1) |
| TB-4 | ACCEPTED (process) |
| CS-1 | ACCEPTED WITH CONDITION RV4-L1 |
| CS-2 | **NOT ACCEPTED as stated** (RV4-H3) |
| VR-1, VR-2, VR-4 | ACCEPTED |
| VR-3 | ACCEPTED WITH CONDITION RV4-M1, RV4-M2 |
| RR-1, RR-2, RR-3 | ACCEPTED |
| LR-1, LR-3 | ACCEPTED |
| LR-2 | ACCEPTED WITH CONDITION RV4-M1 (the subdirectory trigger on the intact layout) |
| LR-4 | ACCEPTED WITH CONDITION RV4-M5 |
| TG-1, TG-3 | ACCEPTED |
| TG-2 | ACCEPTED WITH CONDITION RV4-M2, RV4-L5 |

## 7. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** Every proposal is labelled; D-0008 has no `chosen_option`; OP-1 … OP-7 pending. |
| Honest about security consequences? | **No.** OP-2 (S0)–(S3) minimum sets and "owner must know" item 2 are false (RV4-H1); OP-2 (iii) is presented as raising binary protection but does not stop malicious bytes for genuine source (D-A07); the `release-final` blast radius omits the choice among registered non-orderable content (RV4-H3) and lists a gate Git delivery never passes (RV4-L8); OP-4 is garbled and inherits RV4-H1 (RV4-L7); OP-6 omits that TA-5 depends on first-binary acceptance (D-A04); OP-7 (a) claims an RS-2 bound that does not exist (RV4-M4); OP-7 (c) bound depends on an unspecified witness input (RV4-M3); OP-2 (S1) cost omits the reduction rule (RV4-L9). |
| Complete? | **No.** No option makes the faithful-build fact depend on more than one key except a second rebuilder, whose consequence is not stated; no option or rule gives anchored first-binary acceptance. |

## 8. Prior findings, consolidated status

| Finding | Status | Basis |
|---|---|---|
| R2-H1 / BC-1 | BC-1 as stated **CLOSED**; parent class **NARROWED → RV4-H3** | P1r4, self-test, lattice reproduced; D-A02 |
| R2-H2 / BC-2 | BC-2 as stated **CLOSED**; parent class **NARROWED → RV4-H2** | P4r4 and B's matrix reproduced; AF3, FB1/FB2 |
| R2-H3 / BC-3 | BC-3 as stated **CLOSED**; parent class **NARROWED → RV4-H1** | VA4 reproduced; AF1, AF2, BC |
| R2-H4 | **CLOSED as a class** for kernel and trust state; containment argument's scope **carried → RV4-M1** | C matrix reproduced; D-A01 |
| BC-4 | **OPEN → CD4-4** | §7 |
| RV3-M1, M3, M4, M8 | CLOSED | P4r4 and B model reproduced |
| RV3-M2 | NARROWED → RV4-M2 | B part A reproduced |
| RV3-M5 | NARROWED → RV4-M5 | P1r4 part C reproduced |
| RV3-M6 | bound holds (LR-2), carried; intact-layout trigger → RV4-M1 | C `legacy_regain`, D-A01 |
| RV3-M7 | CLOSED (checker); runtime fallback specification only (RT-107, RT-120) | removal probes reproduced |
| RV3-M9 | NARROWED → RV4-M7 and RV4-H1 (oracle row) | D-A03 |
| RV3-L1 | CLOSED; new inconsistency RV4-L2 | model reproduced |
| RV3-L2 | NARROWED → RV4-H3 (blast radius) | B A16, A10 reproduced |
| RV3-L3 | CLOSED (checker); binary RT-110 | A14 reproduced |
| RV3-L4, L5, L6, L8 | CLOSED (design or model) | P4r4 reproduced |
| RV3-L7 | NARROWED → RV4-M6 | C durability reproduced |
| RV3-I1 | unchanged → RV4-I1 | — |

## 9. Blocking classes and novelty

| Class | Findings | Relation to earlier classes | Invariant not yet established |
|---|---|---|---|
| **BC4-1** Independent decisions for the TCB | RV4-H1 | **Narrowed remainder of R2-H3 / BC-3.** Not materially new. | Each TCB fact (faithful build of S; S legitimately verified) is established by independent parties at a verifier-checked threshold at least as strong as the binary's authority; downstream signatures count only for facts their signers established. |
| **BC4-2** Anchored, non-circular first TCB | RV4-H2 | **Narrowed remainder of R2-H2 / BC-2 at its intersection with R2-H3 / BC-3.** The instance (first binary, Phase 4, first-install ceremonies) had not been attacked before; the class is not materially new. | Every TCB acceptance on a machine, first binary included, is anchored, negative-set-checked and currency-proven over externally measured digests; no TA-5 ceremony runs before it. |
| **BC4-3** Release-scoped registration of non-orderable content | RV4-H3 | **Narrowed remainder of R2-H1 / BC-1.** Not materially new. | Effective values of every constitutional leaf, member and file are fixed per release sequence; superseded content becomes effective later only through a computed, gated reduction. |
| **BC4-4** Owner options and blast-radius statements | §7 | Follows BC4-1 … BC4-3 (remainder of BC-4). Not a new mechanism class. | Consequence statements derived from the corrected rules. |

Each blocking class is the recurring rejection class: a lower-trust input yielding a current, higher-trust fact.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC4-1 | one threshold-1 attestation key plus release-pipeline input | an accepted production binary (the TCB) |
| BC4-2 | transport- or source-host-selected genuine-but-revoked, remediated or self-reporting binary | the first trusted binary on a machine |
| BC4-3 | a threshold-1 final choosing among permitted non-orderable registrations | the effective constitutional content of the newest release |

## 10. Held-out attacks

This review authored **10** held-out attacks, RV4-D-A01 … A10 (`D-synthesis/03-HELDOUT-ATTACKS-RV4-D.md`).

| Evidence class | Attacks |
|---|---|
| Executed (real 4.1.5 and Git; pack checker) | A01, A02 |
| Computed (architect's P4r4 functions, one-line mutants) | A03 (with A03b) |
| Computed from a reproduced stage function, and design | A07 |
| Design reading | A04, A05, A06, A08, A09, A10 |

## Output files

| File | Content |
|---|---|
| `00-REVIEW-REPORT.md` | this report |
| `10-BLOCKING-FINDINGS.md` | every consolidated finding, CRITICAL to LOW |
| `11-CORRECTION-DELTA.md` | blocking classes, invariants, what closes each, carried items, re-review entry criteria |
| `D-synthesis/01-REPRODUCTION.md` | reproduction method and results |
| `D-synthesis/02-ADJUDICATION.md` | per-item adjudication of B and C |
| `D-synthesis/03-HELDOUT-ATTACKS-RV4-D.md` | held-out register RV4-D-A01 … A10 |
| `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` | HO-0001 §3/§4 sub-items; owner-option combinations |
| `D-synthesis/05-RESIDUALS.md` | residual criteria and determinations |
| `D-synthesis/evidence/` | probes, outputs, reproduction log, reviewed-content digests, README |
