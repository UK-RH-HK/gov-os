# Independent trust and security review (B) — RoT-1 revision 4 (Governance OS 4.1.6)

| | |
|---|---|
| **Role verdict** | **`BLOCKING_FINDINGS_PRESENT`** |
| Run | AR-0006, role `rot-reviewer-trust-security`, handoff `HO-0006` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` at `bca05a7e2c2791126fde1d3d812facdaa45b2e45`; byte-identical at this review's base `7a23900` (`evidence/REVIEWED-CONTENT-DIGESTS.txt`, 227 files) |
| Prior review relied on | review r3 `release/root-of-trust/4.1.6-review-r3/` (`79a09a1`); synthesis adjudication governs |
| Branch | `phase1/rot1-r4-review-b` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged between `da9c851` and `bca05a7` (checked) |
| Date | 2026-09-14 |
| Status of D-0008 / ARCH-0002 | Remain PROPOSED (`PROVISIONAL`, `in_effect: false`, no `chosen_option`). This review approves nothing and does not issue the architecture verdict. |

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, no prior review, not reviewer C's work.
- **Orchestration files read:** `HO-0006`, `HO-0001` (§3–§4) and `AGENT_RUNS/README.md` only.
- **Not read:** orchestrator state, ledger, checkpoints, run records, other handoffs, `AGENT_RUNS/*.report.yaml`, other
  branches, other worktrees and other scratch directories. Reviewer C's output was not read.
- **Treated as claims:** the architect's response matrix (`22`), class-remainder analysis (`28`) and evidence. Every
  architect instrument relied on was re-executed, and every closure claim was attacked independently.
- **Hygiene:**
  - probes ran in `…/scratchpad/ar-0006/` under `env -i`, with no `GOV_*` in any child;
  - `HOME` and `GOV_KERNEL_CACHE` pointed into scratch, and `PYTHONDONTWRITEBYTECODE=1` was set;
  - the worktree was checked clean, including ignored files, before commit;
  - legacy binaries were used read-only (digests in `evidence/ARCH-RERUN-LOG.json`).

## Method

1. **Read** the pack (00–28, schemas, inventory, checker, examples, evidence index), D-0008, ARCH-0002, and review r3
   (report, consolidated findings, correction delta, B's register and carried requirements, D's adjudication, register
   and residuals).
2. **Re-executed** the architect's instruments: CSI `selftest` and `check`, P4r4, VA4, and P1r4 on the real 4.1.5 binary.
3. **Re-executed** review r3's decisive trust probes from unmodified copies: B's A01, the A03/A14/A16 probes, the CSI
   injections and r2 P2; D's lattice and surface forward-compatibility/removal probes.
4. **Wrote an independent reference model** of revision 4 from the text (`RV4-B-M-reference-model.py`, not derived from
   P4r4). It covers:
   - review r3's model constructions;
   - a 336-row HO-0001 §3.2 matrix and an OP-7 parameter sweep;
   - binary acceptance over every key subset with honest custodians;
   - first-binary bootstrap, the accepted-TBM high-water, and label and decision-rule consistency.
5. **Recomputed** the decisive binary attacks with the architect's own P4r4 functions (`RV4-B-arch-functions.py`).
6. **Executed** held-out attacks with the pack's checker and the real 4.1.5 binary: unknown keys and files; a
   tunable-only kernel; pinned-digest mixing; confinement persistence; first-binary self-report.

## 1. Verdict against HO-0006 §4

| Condition | Result |
|---|---|
| Any CRITICAL or HIGH (blocking) | **Yes: 3 HIGH** — RV4-B-H1, RV4-B-H2, RV4-B-H3 |
| MEDIUM not carriable without an architecture change | none identified; RV4-B-M1…M4 carried (`04`) |

**Role verdict: `BLOCKING_FINDINGS_PRESENT`.**

## 2. Reproduction of the architect's claims and review r3 probes

Log: `evidence/ARCH-RERUN-LOG.json`. Prior-probe outputs: `evidence/r3-rerun/`.

| Instrument (owner) | Claim | Re-executed result |
|---|---|---|
| CSI `selftest` (architect) | 56 of 56 | **56 passed, 0 failed** |
| CSI `check` framework / 4.1.5 / 4.1.2 / 4.1.3 / 4.1.4 | 0 / 3 / 2 / 2 / 2 | **0 / 3 / 2 / 2 / 2** |
| P4r4 model (architect) | 54/54; 9/9 mutants; 132-row matrix: 77 refused, 42 core, 13 (d), 0 unstated | **byte-identical** |
| VA4 (architect) | 16/16 | **byte-identical** (its "route B" row is RV4-B-H1; see §6) |
| P1r4 on real 4.1.5 (architect) | parts A–D | **byte-identical** |
| RV3-B-A01 precedence to `immutable` (B) | revision 4 refuses | checker exit 3 (`precedence_unregistered`); output identical to the architect's re-run |
| RV3-B-A03/A14/A16 (B) | predicate ignores child-written pins; `on` exit 2; tunables exit 3 | legacy child still writes both pins (uid 1000, 0644); A14 exit 2 ×10; A16 exit 3; identical except one scratch path |
| RV3-B I01–I09 (B) | 2,2,2,2,2,2,3,3,2 | **identical** |
| r2 P2 gate-record forgery (B copy) | legacy behaviour | control `applied: false`; forged record `applied: true` (4.1.4 → 4.1.5) |
| RV3-D-A01/A02 lattice (D) | 0 unsound; tightenings are reductions | **identical** |
| RV3-D-A09/A10 unmodified (D) | R01–R09 exit 2 | **identical** (F01, F03–F11 exit 3, as the architect explains) |
| Review r3 model constructions (B A02, A04–A12; D A04, A12, A13, A15) | refused or stated | independent model: **18 of 18** hold under revision 4 |

## 3. Prior-finding status (classes, not instances)

| Finding | Status | Evidence |
|---|---|---|
| **BC-1** constitutional-surface soundness for project strength and absence | **CLOSED** | P1r4 byte-identical (harms flip on 4.1.5); RV3-B-A01 exit 3; lattice 0 unsound; R01–R09 exit 2; a tunable-only kernel yields no weaker outcome on 4.1.5 (RV4-B-A10). The parent class (HO-0001 §3.1, R2-H1: authentic content lowering effective controls) is **not** closed: RV4-B-H3. |
| **BC-2** anchor satisfaction and currency | **NARROWED → RV4-B-H2** | Inclusion anchors, pin validity, currency proofs and the witness purpose hold. Independent model: 18/18 constructions, 336-row matrix with 0 unstated rows and 0 `current`; the parameter sweep matches the stated exposures. Stale signed state still becomes the **first TCB** on new machines (H2). Carried: M1, M2, M3. |
| **BC-3** built-source legitimacy of production binaries | **OPEN → RV4-B-H1** | The `release-final` route is closed (V8 source equality). One `build-attestation` key or one `verification-attestation` key, plus pipeline input, yields an accepted malicious binary through honest custodians (AF1, AF2; model `BC`). |
| **BC-4** owner-option consequence statements | **OPEN** | OP-2 (S0)–(S3) minimum sets false (H1); `release-final` blast radius omits pinned-digest choice (H3); OP-4 text garbled (L7); OP-7 (c) witness input and custody incomplete (M2). OP-7 (a), (b), (d) exposures match the sweep. |
| RV3-H1 | **CLOSED** | as BC-1 |
| RV3-H2 | **CLOSED** as stated | model: A12 and D-A12 `BELOW_ANCHOR`/`REGRESSION`; A02 refused; A06 not witnessed; D-A15 refused |
| RV3-H3 | **CLOSED** as stated; class remainder RV4-B-H1 | model A08 `RELEASE_IDENTITY_MISMATCH(source)`; VA4 byte-identical |
| RV3-M1 | **CLOSED** | model A05: a pre-negative attestation does not lift; 3 keys |
| RV3-M2 | **NARROWED → RV4-B-M1** | direct pin writes ignored (model A03); persistence at one remove executed (A05) |
| RV3-M3 | **CLOSED** | model A07 refused at ingest; witness-only high-water. The RS-2 bound is a separate item (M3). |
| RV3-M4 | **CLOSED** | model A09: keep references `KNOWN`; drop them `REGRESSION` |
| RV3-M5 | **NARROWED → RV4-B-M4** | P1r4 part C reproduced (whitelist, vector); unrecorded machines are ungated |
| RV3-M7 | **CLOSED** (checker); runtime fallback spec-only (RT-107, RT-120) | R01–R09 exit 2; optional-file removals add no problem (U09, U10); owner-domain selftest S50–S52 |
| RV3-M8 | **CLOSED**; stateless scope RV4-B-L4 | model D-A13 realisable order accepted, older binary refused |
| RV3-M9 | **NARROWED → RV4-B-H1** | 9/9 mutants reproduced, but the oracle expects RV4-B-A01 as an `ACCEPTED` minimum set; no RT for honest-custodian or first-binary cases |
| RV3-L1 | **CLOSED**; new inconsistency RV4-B-L2 | model A10, A11 |
| RV3-L2 | **NARROWED → RV4-B-H3** | A16 exit 3; tunable-only kernel harmless (A10); the blast-radius sentence omits pinned digests |
| RV3-L3 | **CLOSED** (checker); binary spec-only (RT-110) | A14 exit 2 ×10 |
| RV3-L4 | **CLOSED** (design; spec-only RT-118) | `20` §8, R-RI-1 |
| RV3-L5 | **CLOSED** (design; P4r4 `CR-10` reproduced) | `19` §10.6 |
| RV3-L6 | **CLOSED** | model D-A04; `21` OP-7 (d) |
| RV3-L8 | **CLOSED** (design; P4r4 `RV3-D-A16` reproduced) | `05` §8, `17` §9 |
| RV3-I1 | **UNCHANGED** (INFO) → RV4-B-I1 | `27` §5 |

## 4. HO-0001 owner requirements (trust and security view)

| Requirement | Determination | Basis |
|---|---|---|
| §3.1 constitutional-floor closure | **NOT SATISFIED** | **Holds:** inventory; default deny, except wildcard-informational keys (L1); a floor mode per field; coverage check; schema evolution for precedence, presence and migrations; test-list items role→authority, irreversible gate, plugin/tool precedence, export, project override controls, install/update authority, exception authority, future unknown field. **Fails:** pinned content (secret patterns, and equally pinned tool descriptors, schemas, adapters) rolls back inside a higher-sequence release with no reduction, gate or detector (H3; executed harm). |
| §3.2 new-machine trust bootstrap | **NOT SATISFIED** | **Holds for trust state:** all seven machine classes under OP-7 (a)–(d) with repository/transport adversaries show only stated residuals; signed-state replay and repository gate records hold. **Fails for the binary on first install:** a transport adversary selects a revoked or remediated-malicious TCB; build-from-source and the migration path are self-reported (H2). Carried: M1–M3. |
| §3.3 binary and root authenticity | **NOT SATISFIED** | One threshold-1 attestation key plus pipeline input mints an accepted binary (H1). The first-binary chain is circular (H2). **Holds** for subsequent binaries: compiled roots, TPS, TSS and historical set (A6, A7); source not chosen by `release-final`. |
| §3.4 legacy-binary containment | not assessed by B (compatibility scope) | no B finding bears on LP-1 |
| §4 forward compatibility | no contrary evidence | a new constitutional file is default-denied (U07); D-A09 unmodified re-run identical |

## 5. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; every proposal is labelled. |
| OP-1 | accurate |
| OP-2 | **Not honest.** The (S0)–(S3) minimum capability sets are false. With pipeline input, malicious bytes need 1 key under every source authority, and malicious source needs 1 key under (S0) and (S3) (H1). The `release-final` blast radius omits pinned-digest choice (H3). Witness custody is incomplete (M2). |
| OP-3 | Accurate, except that "never answerable by any agent path … every `gov`-executed child" holds only for direct writes (M1); decision-pin expiry is unbounded (L5). |
| OP-4 | **Not honest.** The text is garbled and duplicated, and the key counts inherit H1 (L7). |
| OP-5, OP-6 | accurate |
| OP-7 | (a), (b) and (d) exposures match the independent sweep. (c): the witness service input and custody are unspecified (M2). The RS-2 clock bound claimed for (a) does not exist (M3). |

## 6. Findings

Full statements: `01-FINDINGS.md`.

| ID | Severity | Title |
|---|---|---|
| **RV4-B-H1** | **HIGH** | One stolen `build-attestation` key (or one `verification-attestation` key) plus release-pipeline input yields an accepted malicious production binary through honest custodians; route B's "4 keys" and "no single key" claims are false, and VA4 expects the attack as `ACCEPTED` |
| **RV4-B-H2** | **HIGH** | First-binary acceptance is outside the negative-set, anchor and currency rules; build-from-source compares a value the binary prints about itself; the migration plan self-verifies each consumer's first RoT-1 binary |
| **RV4-B-H3** | **HIGH** | Pinned content is registered per leaf without release binding: a Trust Policy that keeps an earlier digest lets a threshold-1 `release-final` restore it in a higher-sequence release, with no reduction, gate or detector (secret pattern rollback executed on 4.1.5) |
| RV4-B-M1 | MEDIUM | Write confinement is a deny list: a `gov`-run repository command plants code that later runs unconfined (planted `gov` on `PATH`, git hook) and forges VTS anchors and confirmations |
| RV4-B-M2 | MEDIUM | OP-7 (c) witness service input and custody are unspecified |
| RV4-B-M3 | MEDIUM | RS-2's rollback bound does not exist under OP-7 (a), (b), (d) or on stateless runners |
| RV4-B-M4 | MEDIUM | Computed weakening needs a recorded vector: a release-signed migration's weakening on a machine without a record is ungated |
| RV4-B-L1 | LOW | Wildcard `informational` rule admits unknown keys (`ROLES.authority_levels.*.*`) |
| RV4-B-L2 | LOW | `WITNESSED` C3 in the decision table contradicts the currency-proof definition |
| RV4-B-L3 | LOW | P1 "published as of" covers descendants issued after the proof |
| RV4-B-L4 | LOW | Accepted-TBM high-water absent on stateless runners; first-run recording unspecified |
| RV4-B-L5 | LOW | Decision pins have no maximum validity |
| RV4-B-L6 | LOW | A4a/A4b do not consult the negative set for attestations |
| RV4-B-L7 | LOW | OP-4 consequence text garbled; counts inherit H1 |
| RV4-B-I1 | INFO | Acting role remains caller-declared |

### The recurring class

| Finding | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| H1 | one threshold-1 attestation key, plus the release pipeline's input | an accepted production binary (the TCB) |
| H2 | transport- or source-selected genuine-but-revoked, remediated or self-reporting binary | the first trusted binary on a machine |
| H3 | a threshold-1 final choosing among root-registered pinned digests | the effective constitutional content of the newest release |

## 7. What revision 4 does close (confirmed)

- **Precedence and absence.** Registration-only precedence, the directed join, required presence, and project strength
  over effective policy (BC-1).
- **Anchors and currency.** Inclusion anchors; pin validity and integrity; currency proofs for C3; the separate witness
  purpose; no `current` label (the core of BC-2 as defined in review r3).
- **Binary source against `release-final`.** V8 source equality refuses a final that names a different source (RV3-H3 as
  stated).
- **Carried items closed.** Lift attestation, far-future statements, the artefact playbook, the decision table for
  `INCOMPLETE`, the YAML profile at the checker, the migration whitelist on recorded machines.

## 8. Held-out attacks

**17** attacks (RV4-B-A01…A17; `02-HELDOUT-ATTACKS.md`):

| Evidence class | Count | Attacks |
|---|---|---|
| Executed | 5 | A04, A05, A08, A09, A10 |
| Computed | 8 | A01, A02, A03, A06, A07, A11, A12, A13 |
| Design | 4 | A14, A15, A16, A17 |

14 contradict a pack claim, and 2 hold (A07 matrix, A10).

## 9. Residuals

Detail: `03-RESIDUALS.md`.

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | TB-1 (H2); TB-3 (H1); CS-2 as stated (H3); RS-2 as stated (M3) |
| ACCEPTED WITH CONDITION | RS-1b, RS-3, RS-5, CS-1, VR-3, LR-4, TG-2 |
| ACCEPTED | RS-1, RS-1c, RS-4 (scoping), OP-7 (d), TB-2 (scope), TB-4, VR-1/2/4, RR-1…3, TG-1, TG-3 |

## 10. Scope notes and items not run

- **Not re-run by this reviewer (compatibility scope):**
  - the architect's P3r3 and LR2;
  - reviewer C's r3 scripts;
  - D's `RV3-D-legacy-git-restore.py`.
- **Probe copies.** Copies of prior probes are stored unmodified in `evidence/r3-probe-copies/` with SHA-256 in
  `evidence/README.md`.
- **Consumer stand-in.** The real 4.1.5 binary stands in for a consumer, as in review r3 and P1r4. No RoT-1 binary
  exists; confinement (Landlock or sandbox) and `verify-artifact` are evaluated by design, model and legacy execution.
- **No scope deviation** from HO-0006 §6.

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | findings H1–H3, M1–M4, L1–L7, I1 |
| `02-HELDOUT-ATTACKS.md` | RV4-B-A01…A17 and the re-execution register |
| `03-RESIDUALS.md` | residual criteria and determinations |
| `04-CARRIED-REQUIREMENTS.md` | CR4-B-01…11 and re-review acceptance cases for H1–H3 |
| `evidence/` | scripts, outputs, re-run log, reviewed-content digests, README |
