# Output 22 — Response matrix to the independent review of revision 2

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> The review being answered is `release/root-of-trust/4.1.6-review-r2/` (commit `e5a6b8a`), which reviewed revision 2
> (`d37b05c`) and returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`. The task specification is HO-0001.
>
> This matrix claims **no finding as accepted or closed**. Acceptance is the next reviewers' decision. Each row states the
> class, the change, where it is specified and what evidence exists, using this status vocabulary:
> - **ADDRESSED — executed evidence**: real binaries or real consumers were run;
> - **ADDRESSED — reference evidence**: a model or checker encodes the revision-3 rules and was run;
> - **ADDRESSED — specification only**: not executable before implementation; acceptance scenarios are named.
>
> A row is never marked addressed on untested evidence.

## 1. Evidence produced by this revision (`evidence/`, `constitutional-surface/`)

| ID | Evidence | Result |
|---|---|---|
| **CSI** | `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml` (TPS v1 draft); `csi_check.py check` on `framework/`, the 4.1.5 payload, and the 4.1.2–4.1.4 payloads (`evidence/CSI-check-*.json`) | `framework/`: 113 files, exit 0, 0 unclassified. 4.1.5 payload: 121 files, exit 0. 4.1.2: exit 2 (1 unclassified key). 4.1.3 and 4.1.4: exit 3 (64 and 62 registration violations). |
| **CSI-ST** | `csi_check.py selftest` (`evidence/CSI-selftest.json`) | **26 of 26 cases as expected**: unknown key, file and nested key (exit 2); role map, sensitivity, gate, plugin, export, precedence ×3, install authority, exception, tool registry, invariant, schema, adapter, stronger-than-registered (exit 3); forward-compatible data-only classification (exit 0); lint refusals (exit 4, 5) |
| **P1r3** | `evidence/P1r3-floor-coverage.{py,json}` on the real 4.1.5 binary | Part 1: 121 files and every leaf classified; all **308** leaves the review listed as unfloored or partial have a class. Part 2: the review tamper and all nine §3.1 cases are ineligible, with effective harm keys equal to genuine; exception relaxation refused for security keys; join path raises floors. **Part 3: harms (a) authority, (b) AWS credential, (c) R5 gate flip; raised role and confidence floors are enforced (d, e).** |
| **P3r3** | `evidence/P3r3-pre-rot-register-matrix.{py,json,stderr}` with the real 4.1.2, 4.1.3, 4.1.4 and 4.1.5 binaries | Registers derived from each binary's `--help`: 104/109/115/119 leaves. Revision-3 layout L3: **695 invocations and 40 chains, 0 changes** to tracked bytes or Git; classification kept. Control L0: 36/42/46/47 changing invocations. Ablation L3A: 4 per binary. |
| **P4r3** | `evidence/P4r3-trust-state-model.{py,json}` | **34 of 34 scenarios agree.** Review B1–B6 all flipped; machine list M1–M7; replay R1–R6; forks E1–E3; whitelist K1–K3; verify-artifact A27–A29 and variants. |
| **G1** | `evidence/G1-git-occupation-behaviour.{sh,txt}` | ignored residue in the way is removed by pull; unignored residue aborts checkout; a fresh clone receives the occupation file |

## 2. HIGH findings

| Finding (class) | Revision 3 change | Specified in | D-0008 rule | Evidence | Status |
|---|---|---|---|---|---|
| **R2-H1** *registered floor keys ⇒ constitutional policy* | The **Constitutional Surface** is the whole kernel payload plus the precedence key universe. The **CSI** is root-signed inside the TPS. **Default deny.** A closed class and operator vocabulary. Per-key precedence lattice; exceptions after the join; compiled never-relaxable prefixes. E7 surface check at ingress and use (floor violations judged against the named TPS; joins against the effective TPS). Mechanical strengthening (`FLOOR_NOT_REGISTERED`). Consumer and decision-point registers. Schema evolution rules. Forward-compatible classification. **Different mechanism from CD2-1:** the surface is not the release statement's `security_critical` list, which a threshold-1 key signs. | `23`; `19` §3–§6, §10; `07` §3–§4; `09` R-SURF; `15` rule (6) | (6) | CSI, CSI-ST, P1r3 parts 1–3 | **ADDRESSED — executed** (harm flips on the real 4.1.5 binary consuming the revision-3 effective policy) **and reference** (checker, evaluator). The implementation's evaluator is specification only: RT-73…RT-79, RT-100. |
| **R2-H2** *compiled or repository knowledge ⇒ current state* | **Safety separated from freshness.** **Anchors:** pin (TA-9), human confirm-state (TA-5), witness (OP-7 c, TA-7), retained. New `freshness` axis; `CURRENT_KNOWN` withdrawn. Operation classes C0–C3 with a decision table. **Architecture minimum:** no trust ingress without an anchor. **OP-7** for governed use when unanchored. Monotonic VTS state. Machine list M1–M7 answered. Trust-state minimums only from the trust-state lineage; release-local references. RS-1 and RR-2 restated exactly. | `24`; `17` §2, §5, §7, §11; `20` §10; `21` OP-7; `09` R-ANCH | (7), (19) | P4r3 B5, M1–M7, R1, R2, R4–R6 | **ADDRESSED — reference.** Implementation behaviour is specification only: RT-35(d), RT-37(c), RT-38(c), RT-80. |
| **R2-H3** *release key ⇒ binary authenticity* | New purposes **`release-artifact`** (compiled threshold ≥ 2; shares with no other purpose) and **`build-attestation`** (independent reproduction). **Trust Base Manifest** compiled into every binary names the root chain, TPS (surface, floors, bootstrap, historical releases) and TSS digests. **`verify-artifact` A1–A10:** threshold, build attestation, TSS reference, TBM resolution, high-water, negative set, anchor. First-run self-check. Historical-identity statement withdrawn into the TPS. Options of HO-0001 §3.3 evaluated. | `25`; `05` §1–§3, §9; `06` §2; `07` §4; `09` R-ART | (9) | P4r3 A27, A27b–e, A28, A29, A_valid, K2 | **ADDRESSED — reference.** Specification only: RT-92, RT-93, RT-68, RT-69. |
| **R2-H4** *sentinel read afterwards ⇒ boundary* | **Legacy-path occupation layout.** RoT-1 authority under `governance/trust/`; overlay and views relocated; `governance/kernel`, `project`, `generated` are files; `framework.lock` is a directory; the no-install roots `spec/audits/GOVERNANCE-ADOPTION` and `.governance-runtime/migration` (tracked) are occupied. Class argument over each binary's command handlers. Legacy residue quarantined. **Property LP-1** replaces LC-1 and LC-2. Project-strength vector reports silent weakening; remedies cannot clear it. | `26`; `13` §3–§6; `08` §2; `18` §8–§9; `20` §1, §8 | (12), (20) | **P3r3** (real 4.1.2–4.1.5 binaries, full registers, chains, control, ablation), **G1** | **ADDRESSED — executed** for the layout against every derived command of all four legacy binaries. The strength-vector behaviour is specification only: RT-99. |

## 3. MEDIUM findings

| Finding | Revision 3 change | Specified in | Evidence | Status |
|---|---|---|---|---|
| **R2-M1** gate, decision and exception records authorise trust decisions | **Trust gates** (compiled kinds) are answered only by a **local VTS confirmation** (terminal challenge or operator decision pin) bound to kind, project and digests, consumed once. Never agent-resolvable. Repository records are requests. Exceptions cannot relax floor-class or compiled-prefix keys. Plugins and tool subprocesses are listed as writers (VR-3 extended); TA-8 limit stated. | `27`; `19` §5.3, §6 E9; `20` §4–§5; `02` §5 row 12; rule (18) | P4r3 R3; P1r3 part 2 exception relaxation | ADDRESSED — reference; specification: RT-89…RT-91 |
| **R2-M2** trust-state minimums from wrong purposes; freeze | Minimums only from TSS, TPS and root (MS-8). References elsewhere are release-local (S7). Unresolvable TSS ignored or `INCOMPLETE`; honest successors never regress. Blast radius corrected. | `17` S4, S7, §15; `05` §1 | P4r3 B1, B4, B4b | ADDRESSED — reference; RT-96 |
| **R2-M3** certification key alone lifts WITHDRAWN | A lift needs a higher CERTIFIED referenced by the effective TSS, with an ACCEPTED attestation it also references (MS-2). | `17` §2, S5 | P4r3 B2 | ADDRESSED — reference; RT-97 |
| **R2-M4** equivocation undefined | Equivocation among resolved statements; cumulative `prior_states[]`/`prior_policies[]` detect forks across gaps; anchors orphan forks; root-signed chain reset. | `17` S3, S4, S12 | P4r3 B3, E1, E2, E3, R5 | ADDRESSED — reference; RT-95 |
| **R2-M5** lowering keyed on declared `lowers[]`; mode order undefined | Reductions computed against the strongest held values; cumulative `lowering_history[]`; undeclared reduction invalidates the TPS; per-project `policy_lowering` trust gate. Precedence lattice defines the order and join. | `19` §10; `17` S3; `23` §4 | P4r3 B6; CSI-ST S12–S14 | ADDRESSED — reference; RT-78, RT-75 |
| **R2-M6** separation constraints incomplete | Compiled pairwise whitelist; KS-8 (trust-state ∩ certification or attestation), KS-9, KS-10; minimum distinct keys per consequence. | `05` §3 | P4r3 K1–K3 | ADDRESSED — reference; RT-94 |
| **R2-M7** long-lived snapshot never re-checked | VU-11 generation discipline per unit of work; bounded snapshot age; MCP server must adopt it. | `18` §2, §6.3 | — | ADDRESSED — specification only; RT-86 |
| **R2-M8** agent-facing content consumed from disk | Adapters carry pointers and CI; `gov kernel show`; VTS rendering record; D036; direct reads are T4. | `18` §12; `09` R-AGENT | CSI-ST S20 (adapter content pinned) | ADDRESSED — specification (consumption) and reference (registration); RT-88 |
| **R2-M9** trust directory exchange drops statements; `.tx/` in Git; `overlay.prev` unguarded | Union trust record on every transaction and exchange-back; transaction area moved to untracked `.governance-runtime/trust-tx/`, honoured only when VTS-registered (foreign otherwise); `overlay.prev` restore through the computed-weakening trust gate. | `18` §5; `20` §1, §5 | — | ADDRESSED — specification only; RT-83…RT-85 |
| **R2-M10** acceptance plan cannot detect findings | RV2-A01…A36 mapped with codes; pass/fail criteria for RT-35(d), 37(c), 38(c); RT-50 and RT-72 as properties; [FS] by verifier OS tracing; declared TBM and VTS state per scenario; harm assertions for formerly unfloored inputs; RT-73…RT-100. | `12` | — | ADDRESSED — specification |

## 4. LOW findings

| Finding | Change | Where | Status |
|---|---|---|---|
| **R2-L1** `CURRENT_KNOWN` and OP-5 age hide unproven freshness | `freshness` axis; `current` never shown unanchored; OP-5 age from anchor time and always shown unanchored | `24` §4.1; `21` OP-5; `17` S9–S10 | ADDRESSED — reference (P4r3 axis values); RT-80 |
| **R2-L2** hard links accepted until post-commit | VU-12 `st_nlink == 1` before exchange and at use | `18` §2–§3 | ADDRESSED — specification; RT-87 |
| **R2-L3** F1 evidence inconsistent; `22` relied on it | F1 superseded and cited only as history; P3r3 uses the exact FORMAT JSON, lock location, full layout and a fresh copy per command, with control and ablation | `13` §3; `26` §4 | ADDRESSED — executed (P3r3) |

## 5. HO-0001 owner requirements

### 5.1 §3.1 Constitutional-floor closure

| Requirement | Where | Evidence |
|---|---|---|
| complete constitutional key inventory | `constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml`; `23` §2, §5 | CSI check on `framework/` (113 files) and the 4.1.5 payload (121) |
| default deny of unknown keys | `23` §2, §6; `19` E7 | CSI-ST S01–S03, S05, S17, S19; P1r3 T9 |
| explicit floor mode per mutable field | `23` §3, §5 | inventory: floor 234, pinned 177 (+97 files), members 4, precedence 1, release_bound 32, project_tunable 57, informational 14, transaction_input 4 |
| coverage check failing the release | `csi_check.py` exit codes; `23` §6.1–§6.2; R-SURF-4 | CSI-ST (non-zero on every injected mutation) |
| no silent unfloored schema evolution | `23` §7; consumer register §6.5; lint §6.1 | CSI-ST S22 (data-only), S23–S25 (lint) |
| tests: role→authority map; sensitivity and indexing; irreversible gate; plugin and tool floor; outbound and export; project override; install and update authority; exception authority; future unknown field | `23` §8 | CSI-ST S04–S21; P1r3 part 2 T1–T9; P1r3 part 3 (a)–(e) |

### 5.2 §3.2 New-machine trust bootstrap

| Requirement | Where | Evidence |
|---|---|---|
| first install; clean CI; restored backup; old epoch; no epoch; two machines; long absence | `24` §5.1–§5.7 | P4r3 M1–M7 |
| safety vs freshness distinguished | `24` §2 | — |
| transport or repository cannot select old state into a current fact | `24` §2, §4.3; E8 | P4r3 B5, M2, R1 |
| what is safe without freshness; gated or read-only; witness; persisted state; OP-7 effect | `24` §4.3, §5, §8, §9 | P4r3 per machine × OP-7 |
| signed-state replay | `24` §6; `17` §10 | P4r3 R1, R2 |
| gate records from repository | `27`; `24` §7 | P4r3 R3 |
| OP-7 options, not decided | `21` OP-7 (proposal labelled) | — |

### 5.3 §3.3 Binary and root authenticity

| Requirement | Where | Evidence |
|---|---|---|
| options evaluated (threshold root signature, separate attestation, certification binding, reproducible build, compiled state digest, policy digest, multi-signature) | `25` §2 | — |
| protects binary, compiled roots, floors, policy identity, historical set, trust state and bootstrap rules | `25` §8 | P4r3 A27e, A28 |
| a single lower-threshold key cannot mint a binary | `25` §7; `05` KS-9 | P4r3 A27, A27b, A29 |
| non-circular chain | `25` §6; `06` §2 | — |

### 5.4 §3.4 Legacy-binary damage containment

| Requirement | Where | Evidence |
|---|---|---|
| mechanically hostile new-format projects; V3 evaluated and extended | `26` §2–§3 | P3r3 L3 vs L3A |
| kernel, legacy lock, trust, rollback, reinstall, init-force, migration paths | `26` §5 | P3r3 chains (update, init, reinstall, adoption, CIT) |
| no dependence on old binaries understanding RoT-1 | `26` §3 (class argument from their own handlers) | P3r3 registers from `--help` |
| no silent mutation into a state they then treat as valid | `26` §4 (no byte changes, so no such state) | P3r3 (legacy verify after change: no changes to verify) |

### 5.5 §4 Forward compatibility

The Capability Acceptance Contract, Gate W and the G0–G6 scheduler are classified with existing vocabulary (`23` §7.1).
Evidence: CSI-ST S22.

### 5.6 §5 Deliverables

| Deliverable | Where |
|---|---|
| Revision 3 of the pack | 00–27, `schemas/`, `constitutional-surface/`, `evidence/`, `examples/README.md` |
| OP-7 added; OP-2, OP-3, OP-4 restated | `21` |
| Response matrix | this file |
| Machine-readable inventory and checker | `constitutional-surface/` |
| D-0008 and ARCH-0002 as PROPOSED revision 3; `docs/DECISIONS.md` rows | `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` |
| P1, P3, P4 re-run | `evidence/P1r3-*`, `P3r3-*`, `P4r3-*` |

## 6. Correction delta CD2-0…CD2-14

| Item | Applied as | Different mechanism? |
|---|---|---|
| CD2-0 retain | retained: anchor chain, purposes, SV rules, JCS, tree digest, `authenticate`, VerifiedBlobs, KernelSnapshot, GovernedFs, install-authority required levels, computed weakenings, sticky negatives, account-database VTS, mode A, OP-6, test-profile binary | Two exceptions: (i) the in-place layout and sentinels are replaced by occupation; (ii) the historical-identity statement is replaced by the TPS historical set |
| CD2-1 total registration | `23` | **Yes**: the whole payload is the surface and the classification is root-signed. It does not use the release statement's `security_critical` list, which a lower-trust key would decide. Also added: the precedence lattice per concrete key and inventory lint. |
| CD2-2 bounded currency | `24` | **Extended**: pins, human confirmation and OP-7 as proposed, plus witness (c) and compiled-epoch (d) options; a no-C3-without-anchor architecture minimum; anchor-resolved forks; operation classes |
| CD2-3 binary purpose | `25` | **Extended**: `release-artifact` plus an independent `build-attestation` purpose; TBM resolution; first-run self-check |
| CD2-4 fail-before-write boundary | `26` | **Extended**: occupation of the no-install roots (`spec/audits/GOVERNANCE-ADOPTION`, tracked `.governance-runtime/migration`), found necessary by the P3r3 ablation; overlay relocated; strength vector |
| CD2-5 trust decisions not repository records | `27` | as proposed, with a defined confirmation record, terminal challenge and operator decision pins |
| CD2-6 trust-state facts only from trust-state purpose | `17` S7 | as proposed |
| CD2-7 lift needs two purposes | `17` MS-2 | as proposed |
| CD2-8 equivocation and chain continuity | `17` S3–S4 | **Extended**: cumulative `prior_states` (works across gaps) and anchor-resolved orphans |
| CD2-9 computed lowering and mode order | `19` §10, `23` §4 | as proposed, with cumulative history |
| CD2-10 separation | `05` §3 | as proposed |
| CD2-11 snapshot generation, link counts | `18` VU-11, VU-12 | as proposed |
| CD2-12 agent consumption | `18` §12 | as proposed |
| CD2-13 union record, `.tx`, `overlay.prev` | `18` §5, `20` §5 | **Different**: the transaction area moves outside Git with a VTS registry, instead of excluding `governance/.tx/` from version control |
| CD2-14 acceptance plan | `12` | as proposed |
| D-0008 rule changes (6), (7), (9), (12), (18), new (19), (20) | `15` §5; `spec/decisions/D-0008.yaml` | all drafted |

## 7. Review r2 §8 owner-option requirements

| Requirement | Where |
|---|---|
| Add OP-7 | `21` OP-7 |
| Extend OP-2 to `release-artifact` | `21` OP-2 (also `build-attestation`) |
| Restate OP-4 | `21` OP-4: "no" no longer exposes binaries |
| Note OP-3 mode A was not a bound against a repository writer | `21` OP-3: now a bound for ingress; Git-delivered use goes to OP-7 |

## 8. Re-review entry criteria (review r2 `11`)

| Criterion | State |
|---|---|
| 1. CD2 reflected in pack, schemas, D-0008 and ARCH-0002 | §6; schemas revised (`schemas/`); D-0008 and ARCH-0002 PROPOSED revision 3 |
| 2. P1, P3, P4 re-run against the revised specification, each `agrees` flipped or removed by design | P1r3 harm verdicts all true; P3r3 L3 property holds; P4r3 34/34, B1–B6 flipped |
| 3. Full pre-RoT command-register matrix for 4.1.2–4.1.5 | P3r3 (all four real binaries) |
| 4. `22` covers R2-H1…R2-L3 without untested "resolved" claims | §2–§4 (status vocabulary) |

## 9. Residuals (explicit; none presented as stronger than it is)

| ID | Residual | Defined in |
|---|---|---|
| RS-1…RS-4 | unseen metadata; clock under owner options; A3 and the VTS; pins controlled by the repository writer | `24` §10 |
| VR-1…VR-4 | same-user modification between units of work; advisory locks; non-`gov` subprocess writes; profile runtimes by path | `18` §11 |
| RR-1…RR-3 | ineligible state after automatic rollback; fresh machines; A3 deletes records | `20` §10 |
| CS-1, CS-2 | classification review responsibility; ceremony frequency | `23` §10 |
| TB-1…TB-3 | binary TCB; rebuilder environment; four-key binary compromise | `25` §9 |
| LR-1…LR-4 | unconverted working copies; A3 removes occupation; explicit output paths; fresh clones accept overlay | `26` §8 |
| TG-1…TG-3 | per-machine trust decisions; A3 forges confirmations; non-trust gates forgeable by A2 | `27` §7 |

## 10. Unresolved or not yet executable

- **Specification only (not executable before implementation):**
  - VU-11 (long-lived processes);
  - VU-12 (link counts);
  - the adapter rendering record;
  - the union trust record and foreign-journal handling;
  - trust-gate terminal confirmation;
  - the project-strength vector;
  - the consumer register build check;
  - `verify-artifact` on real binaries.

  Each has named acceptance scenarios in `12`.
- **Examples.** `examples/rev2/` is superseded and not regenerated for revision 3 (`examples/README.md`). The executable
  artefacts of revision 3 are the inventory, the checker and the evidence models.
- **Owner decisions pending (not answered here):** OP-1…OP-7.
- **Independence.** This revision was written by a fresh architect session (AR-0001). That session did not author
  revision 1, revision 2 or either review. It must be reviewed by fresh reviewers.
