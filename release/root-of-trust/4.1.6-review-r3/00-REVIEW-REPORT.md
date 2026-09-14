# Independent architecture synthesis review (D) — RoT-1 revision 3 (Governance OS 4.1.6)

| | |
|---|---|
| **Architecture verdict** | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Run | AR-0004, role `rot-review-synthesis`, handoff `HO-0004` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` at `ca77a431418bd6b349f465aa2521ca43bccfd5a6` (unchanged at this review's base; `D-synthesis/evidence/REVIEWED-CONTENT-DIGESTS.txt`) |
| Panel verified | reviewer B `7d8c73a91a7c5fc7912427c59314d9259fbe25c9` (`BLOCKING_FINDINGS_PRESENT`); reviewer C `9e013c161210f6fec0a9869cb3387fd57f033ebb` (`NO_BLOCKING_FINDINGS`) |
| Branch and base | `phase1/rot1-r3-review-d` from `90efd29` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 | Remain PROPOSED (record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`). This review approves nothing. Acceptance of an architecture would not be owner approval. |

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, not reviewer B's or C's work, no prior review.
- **Orchestration files read:** `HO-0004`, `HO-0001` (§3–§4) and `AGENT_RUNS/README.md` only.
- **Not read:** orchestrator state, ledger, checkpoints, run records, any `AGENT_RUNS` report, other branches, other worktrees, other scratch directories.
- **Treated as claims:** the architect's response matrix and evidence, and every statement in B's and C's directories. Every probe behind a HIGH claim and behind a `CLOSED` claim was re-run (§2).
- **Scripts reused as committed:** B's and the architect's scripts ran from this worktree. C's scripts hard-code C's worktree path, so they were copied to scratch with only that constant set to this worktree.
- **Hygiene:** all probes ran in scratch under `env -i`, with no `GOV_*` in any child. `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` pointed into scratch, and `PYTHONDONTWRITEBYTECODE=1` was set. The worktree was verified clean (including ignored files) after every run.

## 1. Verdict against the acceptance rule (HO-0004 §3)

| Condition | Result |
|---|---|
| No open CRITICAL or HIGH finding after adjudication | **Not met.** 3 HIGH: RV3-H1, RV3-H2, RV3-H3 (`10-BLOCKING-FINDINGS.md`) |
| Every HO-0001 §3 requirement `SATISFIED` as a class | **Not met.** §3.1, §3.2, §3.3 `NOT SATISFIED`; §3.4 `SATISFIED` (§5) |
| Every open MEDIUM carried as a bound, testable requirement; none needs an architecture change | Met for RV3-M1…M4 and M6…M9, which are carried (`11` §6). RV3-M5 shares RV3-H1's root and closes inside CD3-1. |
| Every residual explicitly bounded under attack | **Not met.** RS-1, RR-2, CS-1 and TB-3 are not accepted as stated, nor is the overlay part of VR-3 (§6). |
| Owner options complete and honest about security consequences, none pre-decided | **Not met** for honesty and completeness: the OP-2, OP-4 and OP-7 consequence statements are materially incorrect. Met for "none pre-decided". (§7) |

**Verdict: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.** The correction is architectural and stated as classes in
`11-CORRECTION-DELTA.md`.

### What revision 3 does close (confirmed by reproduction)

- **Default deny for added constitutional content.** Confirmed by checker exits, self-test 26/26, B's I01–I06, and this review's F12.
- **Legacy kernels.** They fail E7.
- **Review r2 P1 harms.** They flip (P1r3 byte-identical).
- **Trust-state items closed.**
  - Equivocation and forks (R2-M4).
  - The compiled purpose whitelist (R2-M6).
  - Release-local references.
  - Unresolvable trust state.
  - Certification-key-only un-withdraw is refused.
  - Computed lowering across a skipped version.
- **Repository gate records are requests, not authorisation.**
- **R2-H4 as a class.** No pre-RoT byte is written on the intact layout.
  - P3r3: 695 invocations and 40 chains.
  - C: 84 invocations.
- **Forward compatibility.** New Capability-Contract, Gate W and G0–G6 constitutional files and keys classify with inventory data only (RV3-D-A09).

## 2. Reproduction table

Full log: `D-synthesis/01-REPRODUCTION.md`, `D-synthesis/evidence/REPRODUCTION-LOG.json`.

| Probe (owner) | Behind claim | Reproduced |
|---|---|---|
| P4r3 trust-state model (architect) | pack closures of R2-M2…M6; B's `CLOSED` R2-M4, R2-M6 | **yes**, byte-identical |
| P1r3 floor coverage on real 4.1.5 (architect) | R2-H1 narrowing | **yes**, byte-identical |
| P3r3 pre-RoT register matrix, real 4.1.2–4.1.5 (architect) | R2-H4 closure (LP-1); R2-L3 `CLOSED` | **yes**: summary, `property_L3`, chain summary and job count equal |
| CSI checker `check` + `selftest` (architect) | R2-H1 default deny | **yes**: exits 0/0/2/3/3; 26 passed, 0 failed |
| RV3-B-M reference model (B) | **RV3-B-H2**, **RV3-B-H3** (A08), M1, M3, M4, L1 | **yes**, byte-identical |
| RV3-B-A01 precedence to `immutable`, real 4.1.5 + checker (B) | **RV3-B-H1** | **yes**, 0 differences |
| RV3-B-A03/A14/A16, real 4.1.5 + checker (B) | M2, L2, L3 | **yes** |
| RV3-B CSI injections I01–I09 (B) | default deny; M5 (I08) | **yes** |
| r2 P2 gate-record forgery, real 4.1.5 (B copy) | R2-M1 on the unchanged implementation | **yes** |
| r2 P4 under revision-2 rules (B copy) | B1–B6 disagreed under revision 2 | **yes**, byte-identical |
| C `destructive.json` (84 invocations, 4 real binaries) | R2-H4 `NARROWED`, LP-1 | **yes** |
| C `occ_removal.json` | C-1 (A04) | **yes** |
| C `full_removal_and_merge.json` | C-1 (A05); merge (A03) | **yes** |
| C `durability.json` | layout durability (A02, A06, A09) | **yes** |

## 3. Adjudication of the panel

Detail: `D-synthesis/02-ADJUDICATION.md`.

| Panel item | Panel severity | Adjudication | Consolidated |
|---|---|---|---|
| RV3-B-H1 precedence order treats `immutable` as strongest | HIGH | **CONFIRMED HIGH**, extended by RV3-D-A01, A02, A10 | RV3-H1 |
| RV3-B-H2 anchors do not stop stale state becoming anchored-current | HIGH | **CONFIRMED HIGH**, extended by RV3-D-A11, A12, A15 | RV3-H2 |
| RV3-B-H3 binary source not bound to verified source | HIGH | **CONFIRMED HIGH**, extended by RV3-D-A03 | RV3-H3 |
| RV3-B-M1 lift with two keys | MEDIUM | CONFIRMED MEDIUM, carried | RV3-M1 |
| RV3-B-M2 pins writable by the governed account | MEDIUM | CONFIRMED MEDIUM, carried; not raised (a CI job running repository code before `gov`'s decision is outside TA-9 whatever the design; the `gov`-executed vector is bounded by CR-03) | RV3-M2 |
| RV3-B-M3 `issued_at` high-water poisoning | MEDIUM | CONFIRMED MEDIUM, carried | RV3-M3 |
| RV3-B-M4 playbook contradicts admissibility | MEDIUM | CONFIRMED MEDIUM, carried | RV3-M4 |
| RV3-B-M5 weakening computed over four overlay categories | MEDIUM | CONFIRMED MEDIUM; same root as RV3-H1 (strength not computed over effective policy), closed inside CD3-1; op × target whitelist carried | RV3-M5 |
| RV3-B-L1…L5 | LOW | CONFIRMED LOW (L1, L2, L3 reproduced; L4, L5 design) | RV3-L1…L5 |
| RV3-B-I1 caller-declared role | INFO | CONFIRMED INFO | RV3-I1 |
| C-1 occupation defence not robust to removal | MEDIUM | **CONFIRMED MEDIUM, broadened** (below) | RV3-M6 |
| C's statement "`governance/trust/**` is structurally outside every legacy binary's write vocabulary" | (claim) | **REFUTED as a general statement.** It holds only while the occupation is present. After one `git checkout <pre-migration> -- governance`, or after C's removal plus `init --force`, the real 4.1.5 binary executes a CIT that rewrites `governance/trust/kernel/policies/SECURITY_POLICY.yaml`, deletes `governance/trust/framework.lock` and removes an overlay classification (RV3-D-A06). | RV3-M6 |
| C-2…C-5 engineering constraints | carried | CONFIRMED as carried constraints | `11` §6 |
| C verdict `NO_BLOCKING_FINDINGS` (compatibility/transaction scope) | — | Agreed within C's scope: no HIGH in legacy containment or transactions | — |

**Why RV3-M6 remains MEDIUM although broadened.**
- **Precondition.** Occupation removal, or an explicit restore of pre-migration history.
- **RoT-1 side.** RoT-1 binaries report `PARTIAL(occupation)` or `KERNEL_TAMPERED` on the result and fail closed.
- **Overlay changes.** They are within the repository writer's authority (LR-4) and are detected on machines with a record.
- **Why no design removes it.** No design can stop Git from restoring pre-migration history (the LR-1 class).
- **What remains wrong.** LR-2 must state the reachable outcome, and the plan must assert it.

## 4. Consolidated findings

Full statements: `10-BLOCKING-FINDINGS.md`.

| ID | Severity | Title | Origin | Adjudication |
|---|---|---|---|---|
| **RV3-H1** | **HIGH** | The precedence order is refusal-only: a kernel precedence change, a deleted POLICY_PRECEDENCE file or a root-signed TPS tightening silently discards project-owned strengthening | B + D | CONFIRMED HIGH, extended |
| **RV3-H2** | **HIGH** | Stale state becomes anchored-current: anchors satisfied by sequence number, pins without currency, and a threshold-1 witness make revoked state a policy root, a C3 target and an accepted binary | B + D | CONFIRMED HIGH, extended |
| **RV3-H3** | **HIGH** | Binary acceptance never binds the built source to verified source; threshold-1 `release-final` chooses the TCB's source | B + D | CONFIRMED HIGH |
| RV3-M1 | MEDIUM | Lifting WITHDRAWN/REJECTED needs two keys: the pre-withdrawal attestation is reusable | B | CONFIRMED, carried |
| RV3-M2 | MEDIUM | State pins, decision pins and confirmations are writable by the governed account, including by `gov`-run repository commands | B | CONFIRMED, carried |
| RV3-M3 | MEDIUM | Any verified `issued_at` raises the clock high-water; one far-future value disables clock-based freshness | B | CONFIRMED, carried |
| RV3-M4 | MEDIUM | The artefact-compromise playbook contradicts TSS admissibility and freezes verifiers | B | CONFIRMED, carried |
| RV3-M5 | MEDIUM | Computed weakening covers four overlay categories; `release-final`-signed migrations write other security keys ungated | B | CONFIRMED; class closed inside CD3-1 |
| RV3-M6 | MEDIUM | The occupation defence is not robust to removal or to a Git restore of pre-migration paths; the legacy binary regains a verified install, serves newly classified material and writes `governance/trust` and the overlay | C + D | CONFIRMED, broadened, carried |
| RV3-M7 | MEDIUM | Surface totality covers present content, not registered content: removing a registered constitutional file passes E7; the pinned/members fallback is undefined; absence of non-kernel owner files is undetected | D | NEW, carried (the POLICY_PRECEDENCE case is RV3-H1) |
| RV3-M8 | MEDIUM | `verify-artifact` A7 and the first-run self-check compare with an ambiguous "VTS high-water"; under the TSS reading every realisable genuine binary is `BINARY_T0_ROLLBACK` | D | NEW, carried |
| RV3-M9 | MEDIUM | The acceptance plan's mandated oracle (P4r3 34/34) cannot distinguish the anchor defect and contains a non-realisable artefact scenario; the RTs lack the blocking cases | D + B | NEW (R2-M10 remainder), carried |
| RV3-L1 | LOW | Decision-table conflicts: OP-7 (d) with INCOMPLETE; OP-7 (c) with a non-witness anchor | B | CONFIRMED |
| RV3-L2 | LOW | `project_tunable` leaves read by security decision points; the `release-final` blast-radius sentence is inexact | B | CONFIRMED |
| RV3-L3 | LOW | The checker (YAML 1.1) and runtime (serde_yaml) parse booleans differently | B | CONFIRMED |
| RV3-L4 | LOW | Reinstall identity is taken from the A2-writable lock | B | CONFIRMED |
| RV3-L5 | LOW | TPS fields outside the surface are outside the computed-reduction set | B | CONFIRMED |
| RV3-L6 | LOW | The OP-7 (d) consequence names binaries older than the newest TPS; a revocation-only TSS also exposes binaries at the newest TPS | D | NEW |
| RV3-L7 | LOW | The tracked-but-ignored `.governance-runtime/migration` occupation is dropped from clones by the common "untrack ignored files" idiom | D | NEW |
| RV3-L8 | LOW | Rotation playbooks never re-sign honest statements of a removed key, so the documented remedy invalidates anchored history (C0 freeze) | D | NEW |
| RV3-I1 | INFO | Acting role remains caller-declared (V-L5) | B | CONFIRMED |

## 5. HO-0001 §3 owner requirements

Detail per sub-item: `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md`.

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure (R2-H1) | **NOT SATISFIED** | **Holds:** inventory, default deny for additions, coverage check for additions, most of the test list. **Fails:** "project override controls" and "schema evolution cannot silently introduce an unfloored setting". A precedence move to `immutable` passes E7 and removes project strengthening, executed on 4.1.5 (RV3-B-A01). The order is unsound for all five strengthening modes (RV3-D-A01). A root-signed TPS tightening is not a computed reduction (RV3-D-A02). Deleting POLICY_PRECEDENCE passes E7 and joins 66 of 85 rules to `immutable` (RV3-D-A10). |
| §3.2 New-machine trust bootstrap (R2-H2) | **NOT SATISFIED** | **Holds:** safety and freshness are separated structurally. **Fails:** repository or transport control plus one threshold-1 trust-state key creates an anchored-current fact on CI and first-install machines (RV3-B-A12; RV3-D-A12 with the architect's own functions). Stale pins stay `ANCHORED` under the proposed OP-7 (a) (RV3-B-A02). A revoked genuine binary is re-accepted on pinned CI (RV3-D-A15). The OP-7 effects are mis-stated. |
| §3.3 Binary and root authenticity (R2-H3) | **NOT SATISFIED** | **Holds:** protection of compiled roots, TPS, TSS and the historical set (A6/A7). **Fails:** "a single lower-threshold release key must not be able to mint a malicious binary" — `release-final` plus pipeline input yields `ACCEPTED` (RV3-B-A08). |
| §3.4 Legacy-binary damage containment (R2-H4) | **SATISFIED** | No pre-RoT byte written on the intact layout (P3r3 and C reproduced). The defence does not depend on old binaries reading RoT-1. RoT-1 fails closed on every removal or restoration state. The reachable legacy outcome after explicit restoration is carried as RV3-M6. |
| §4 Forward-compatibility constraint | **SATISFIED for classification** | RV3-D-A09 F01–F12: Gate W collections and floors, a new severity order, pinned durations, a hash-bound contract Markdown with compiled YAML, and default deny beside `project_tunable` keys, all by inventory data. RV3-H1's order and RV3-M7's removal semantics apply to new files as well. |

## 6. Residual determinations

Detail: `D-synthesis/05-RESIDUALS.md`.

| Residual | Determination |
|---|---|
| RS-1 (unseen metadata) | **NOT ACCEPTED as stated** (RV3-H2). Core accepted: a machine anchored before a revocation and never contacted again. Not core: sequence-satisfied anchors; pins with no currency bound labelled `ANCHORED`/`current`; a threshold-1 witness. |
| RS-2 (clock) | ACCEPTED WITH CONDITION RV3-M3 (CR-06) |
| RS-3 (A3 and the VTS) | deletion ACCEPTED; forging ACCEPTED WITH CONDITION RV3-M2 (CR-03) |
| RS-4 (pins provisioned by the repository writer) | ACCEPTED as scoping, with the TA-9 restatement of CR-03 |
| VR-1 | ACCEPTED (spec-only; RT-86) |
| VR-2 | ACCEPTED |
| VR-3 | PPS and records ACCEPTED; the overlay part is **NOT ACCEPTED** (RV3-H1, RV3-M5) |
| VR-4 | ACCEPTED |
| RR-1 | ACCEPTED |
| RR-2 | **NOT ACCEPTED as stated** (RV3-H2) |
| RR-3 | ACCEPTED |
| CS-1 | **NOT ACCEPTED** (RV3-H1, RV3-M7) |
| CS-2 | ACCEPTED |
| TB-1 | ACCEPTED WITH CONDITION RV3-M8 |
| TB-2 | ACCEPTED only for what it bounds (bytes equal a build of `source_commit`) |
| TB-3 | **NOT ACCEPTED** (RV3-H3) |
| LR-1 | ACCEPTED (C A09; D A05c) |
| LR-2 | ACCEPTED WITH CONDITION RV3-M6 (restated bound and harm tests) |
| LR-3 | ACCEPTED |
| LR-4 | ACCEPTED (A2 authority over project configuration) |
| TG-1 | ACCEPTED |
| TG-2 | ACCEPTED WITH CONDITION RV3-M2 |
| TG-3 | ACCEPTED |
| OP-7 (d) residual | ACCEPTED WITH CONDITION RV3-L6, as an owner-selectable residual whose consequence text is corrected |

## 7. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | No. Every proposal is labelled, D-0008 has no `chosen_option`, and OP-1…OP-7 are pending. |
| Honest about security consequences? | **No.** OP-7 (a) "makes the B5 class impossible everywhere" is false (RV3-B-A02, RV3-D-A15). OP-7 (c) "staleness bounded by the expiry window" is false under trust-state key compromise (RV3-B-A06). The OP-7 (d) residual is scoped to the TPS only (RV3-L6). OP-2 "an accepted malicious binary needs four keys over three purposes" is false (RV3-B-A08). OP-4 "'no' no longer exposes binaries" is false (RV3-D-A03). |
| Complete? | **No.** No option offers a witness authority above a single threshold-1 key for (c). The `release-final` threshold is not presented as bearing on binary acceptance. No pin-currency parameter exists. |

## 8. Prior findings (review r2), consolidated status

| Finding | Status | Basis |
|---|---|---|
| R2-H1 | **NARROWED → RV3-H1** | additions default-deny and r2 harms flip (reproduced); project-layer order unsound; removal |
| R2-H2 | **NARROWED → RV3-H2** | unanchored machines read-only under (a)–(c) (reproduced); anchors bypassable and uncurrent |
| R2-H3 | **NARROWED → RV3-H3** | purpose, threshold, TBM resolution hold (reproduced); built source unbound |
| R2-H4 | **CLOSED as a class**; residual RV3-M6 | LP-1 reproduced (P3r3; C) |
| R2-M1 | NARROWED → RV3-M2 | repository records are requests; same-account pins remain |
| R2-M2 | NARROWED → RV3-H2 (trust-state blast radius), RV3-M3 | B1, B4 reproduced |
| R2-M3 | NARROWED → RV3-M1 | B2 reproduced; lift reuses pre-withdrawal attestation |
| R2-M4 | CLOSED | B3, E1, E2, E3 reproduced (anchor-dependent fork handling is part of RV3-H2) |
| R2-M5 | NARROWED → RV3-H1, RV3-L5 | B6 reproduced; order unsound |
| R2-M6 | CLOSED | K1–K3 reproduced; whitelist read |
| R2-M7 | CLOSED (design; RT-86, spec-only) | VU-11 |
| R2-M8 | CLOSED (design; RT-88, spec-only) | `18` §12 |
| R2-M9 | CLOSED (design; RT-83…85, spec-only) | union record; transaction area outside Git |
| R2-M10 | NARROWED → RV3-M9 | oracle insensitivity; missing RT cases |
| R2-L1 | NARROWED → RV3-H2 | `current` permitted for stale or bypassed anchors |
| R2-L2 | CLOSED (design; RT-87) | VU-12 |
| R2-L3 | CLOSED | P3r3 reproduced |

## 9. Blocking classes and novelty

| Class | Findings | Relation to review r2 |
|---|---|---|
| **BC-1** Constitutional-surface soundness for the project layer and for removal | RV3-H1 (with RV3-M5's root and RV3-M7's precedence case) | **Narrowed remainder of R2-H1**, carrying R2-H4's harm (silent loss of project-owned control). Not materially new. |
| **BC-2** Anchor satisfaction and anchor currency | RV3-H2 | **Narrowed remainder of R2-H2.** Not materially new. |
| **BC-3** Built-source legitimacy of binaries | RV3-H3 | **Narrowed remainder of R2-H3.** Not materially new. |
| **BC-4** Owner-option consequence statements | OP-2, OP-4, OP-7 (§7) | Follows from BC-2 and BC-3. Not a new mechanism class. |

Each blocking class is the recurring rejection class: a lower-trust input yielding a current, higher-trust fact.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC-1 | a threshold-1 kernel, or a root-signed TPS without a per-project gate | the project's effective security configuration |
| BC-2 | repository or transport selection, plus at most one threshold-1 key | a current anchored trust state |
| BC-3 | a threshold-1 release statement choosing `release_commit` | the TCB |

## 10. Held-out attacks

This review authored **18** held-out attacks, RV3-D-A01…A18 (`D-synthesis/03-HELDOUT-ATTACKS-RV3-D.md`).

| Evidence class | Attacks |
|---|---|
| Executed with the real 4.1.5 binary and Git | A05, A06, A07 |
| Executed with the pack's checker | A09, A10 |
| Computed with the pack's lattice or the architect's own model | A01, A02, A04, A11, A12, A13, A15 |
| Design reading | A03, A08, A14, A16, A17, A18 |

## Output files

| File | Content |
|---|---|
| `00-REVIEW-REPORT.md` | this report |
| `10-BLOCKING-FINDINGS.md` | every consolidated finding, CRITICAL to LOW |
| `11-CORRECTION-DELTA.md` | blocking classes, what closes each, carried items, re-review entry criteria |
| `D-synthesis/01-REPRODUCTION.md` | reproduction method and results |
| `D-synthesis/02-ADJUDICATION.md` | per-item adjudication of B and C |
| `D-synthesis/03-HELDOUT-ATTACKS-RV3-D.md` | held-out register RV3-D-A01…A18 |
| `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` | HO-0001 §3/§4 sub-item table; owner-option combinations |
| `D-synthesis/05-RESIDUALS.md` | residual criteria and determinations |
| `D-synthesis/evidence/` | probes, outputs, reproduction log, reviewed-content digests, README |
