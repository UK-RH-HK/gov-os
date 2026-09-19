# P2-AR-0033: WS-2 repair report (repair iteration 1, round 3)

| Field | Value |
|---|---|
| Run | P2-AR-0033 (`capability-repair`, WS-2). Model: Claude Opus 5, 1M context (`claude-opus-5[1m]`) |
| Handoff | `release/orchestration/phase-2/HANDOFFS/P2-HO-0032-repair-1-r3-ws02.md`. Common protocols: P2-HO-0031 (including the availability rule), P2-HO-0020, P2-HO-0010 |
| Base | `53897c1a44157e5af81b176017bc7ded6a63b9cd`. This is the integrated round-2 tree. `product_code_digest` `797da37c…1fe1` |
| Branch | `phase2/repair-1-r3-ws02` |
| Product commits | `18ff93a`, `7c89135`, `2cff5b7`, `2e72007` |
| Final product commit | `2e7200728174a0fa27928b17a4d7c681cd46bfd9`. `product_code_digest` `edf5177d609c24bd077ba5cc61532e4001a966b0b03ba1034ace3be3981cf709` |
| Binary under test | Release `gov` sha256 `94f9ed9805a2bd6e0026dfd619185c810a23aefc31c918b953e4745bf8978151`. Base binary `5ff6ce9c…6b82`, built from a `git archive` export of the base |
| Classes | BC-P2-07, BC-P2-23 and BC-P2-44, plus the scheduler side of the availability rule |
| Claims | BC-P2-23 and BC-P2-44: `REPAIRED_CLAIMED`. BC-P2-07: `PARTIAL`. WS-2's whole tier contract is done; one acceptance line waits on WS-5's host call (R2-3). Availability rule, scheduler side: `REPAIRED_CLAIMED`. Per-IP status is in §4 and in `claims.yaml` |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`. §7 raises one question for the owner or orchestrator. It does not block the claims |

Everything below is builder evidence (Contract v3 O3). It is not acceptance.

---

## 1. The availability rule: scheduler side (P2-HO-0031)

The rule is designed once, in the catalogue, and exposed to hosts through one API.

### 1.1 Catalogue semantics (`runtime/src/scheduler/catalogue.rs`)

Every hard-block rule is a `BlockRule { min_severity, operations, scope, remedies }`.

**Scope** (`BlockScope`):
- **`Global`**: the failing check governs the whole repository. Examples: kernel integrity, secret leakage, policy precedence, an interrupted transaction, a release relying on everything.
- **`CoveredPaths`**: product-test families. The block applies to operations whose paths intersect the finding's `covers`.
- **`Subjects`**: the block applies only to operations whose subjects reach the finding's subjects.
  - A subject is a record id or a path. Ids and paths alias each other through the record store.
  - A finding that names no subject is scoped to the paths its check declares (`governed_paths`).
  - Work on anything else stays available.

**Remedies.** An operation listed in `remedies` whose subjects reach the block's subjects is the work that repairs the condition. It stays available under the block.
- A remedy that commits (`ops::COMMITTING`: task close, CIT-E, release, update, migration) commits only if the block is cleared once its change is applied. Nothing commits under a block it does not clear.
- The remedy vocabularies are:
  - `WORK_REMEDIES`: `cit.propose`, `cit.approve`, `cit.execute`. These are the change transaction on the named subjects.
  - `ALL_REMEDIES`: the same plus `update.apply`.
- The never-refused repairs are never in the operation vocabulary: doctor, audit, health, recover, rebuild-memory, pause/freeze/resume, kernel reinstall/verify, gate present/answer, checkpoint, `update --rollback`, `cit propagate`, and direct repair of a file.

**Rules as declared.** Every check's `enforcement` (`gov health checks`) carries its operations, scope and remedies. The full dump is in `evidence/gov-health-checks.json`.

| Rule | Severity | Scope | Refuses | Admits as remedy |
|---|---|---|---|---|
| `CRIT_ALL` | critical | Global | every governed operation | `ALL_REMEDIES` reaching the named subjects |
| `HIGH_RELY_WORK` | high | Subjects | task close, CIT-E | `WORK_REMEDIES` |
| `HIGH_RELY_SHIP` | high | Global | release build, update apply | `update.apply`, whose subjects are the kernel, the lock, the overlay and generated views (`ops::UPDATE_SUBJECTS`) |
| `graph_integrity` | high | Subjects | claim and close of the tasks a DAG defect names | `WORK_REMEDIES` |
| `graph_integrity` | high | Global | release (`HIGH_SHIP`) | none |
| D016 (interrupted transaction) | high | Global | CIT ops | none |
| D016 (interrupted transaction) | high | Subjects | close | none |
| product-test families | high | CoveredPaths | close | none |

`product_test_health` and D030 no longer refuse `update.apply`: an update does not rely on product-test results.

### 1.2 The host API (`runtime/src/scheduler/mod.rs`)

```rust
pub struct Request { pub operation: String, pub subjects: Vec<String> }   // Request::new(op).with_subjects(paths)
pub struct Admission { operation, subjects, remedy_for: Vec<Value>, reevaluated: Vec<String>, observed: Value }
impl Admission { fn is_remedy(&self) -> bool; fn obligation(&self) -> bool; fn to_value(&self) -> Value }

pub fn admit(p, &Request) -> Result<Admission>          // G0 decision
pub fn confirm_remedy(p, &Admission) -> Result<Value>   // the remedy obligation, before commit
pub fn guard(p, op, paths) -> Result<Value>             // admit() for hosts that cannot confirm
pub fn subjects_reach(block_subjects, request) -> bool
```

**`admit`.** Called for a committing operation, it first observes the mutations made since the last observation (G1, §2).
- It then classifies every active block:
  - **refuses**: the operation is listed and the block's scope applies;
  - **remedy**: the operation is listed as a remedy and its subjects reach the block's subjects;
  - **none**.
- Blocks whose check inputs changed since they were recorded are re-evaluated first, so a stale block never refuses.
- The refusal is `HEALTH_HARD_BLOCK` (exit 4). It names every block with its check, scope, subjects, operations, remedies and message.

**`confirm_remedy`.** The host calls it after applying its change and before it commits.
- It re-evaluates the blocks the admission was granted under, fresh.
- It returns `HEALTH_REMEDY_INCOMPLETE` (exit 4, naming the blocks left) unless all of them are cleared. The host then rolls back.

**`guard`.** The same decision, with the paths as subjects.
- A committing operation admitted only as a remedy is refused here with `details.remedy_admissible: true`. Its host must apply-then-verify: CIT-E's repair mode already does, and other hosts can use `admit` + `confirm_remedy`.
- A non-committing remedy is allowed: proposing or approving the repairing CIT, or creating, claiming or handing off the repairing task.

### 1.3 How each routed availability item is resolved

| Item | Resolution | Evidence (supplementary, final binary; base in brackets) |
|---|---|---|
| WS-5 O-R2-2: one `graph_integrity` HIGH refused every claim | Scoped to `Subjects`. A missing dependency or a cycle blocks claim and close of the tasks it names. Every other task stays claimable. A release still relies on the whole graph | AV.1a–AV.1d PASS [AV.1a–c FAIL] |
| WS-4 R2-8 (the handoff's "R2-9"): may a critical block refuse proposing the CIT that repairs it? | No. Under `CRIT_ALL` a CIT whose subjects reach the block is a remedy. Proposing it is admitted. Executing it must clear the block (CIT-E repair mode or `confirm_remedy`). An unrelated CIT, and unrelated new work, stay refused (O5 S6 holds) | AV.2a, 2b, 2c, 2d PASS. AV.2b-e2e FAIL, because WS-3's generic G0 site still guards `cit propose` without paths (IP-R3-WS02-01, §6) |
| WS-8 IP-R2-WS08-5: update entry guard vs its own remedy | A `HIGH_RELY_SHIP` or `CRIT_ALL` block whose subjects lie in what an update changes (`ops::UPDATE_SUBJECTS`: the kernel, the lock, the project overlay its migrations may add to, the generated views, `framework.json`) admits `update.apply` as its remedy. Example: D006 "overlay file missing" on an older kernel. The update must clear the block before it commits. A block on records the update does not change refuses it at entry (AV.3b: `schema_invariants` on a requirement), and that block still leaves unrelated closes available (AV.3c). The host call belongs to WS-8 (§6) | AV.3a–c PASS [AV.3a, AV.3c FAIL] |
| WS-3 IP-R2-2: host guards must not refuse their own remedy (D014 vs the repairing CIT; D006/D007 vs `update --apply`; §5 update/rollback) | The remedy semantics above. `update --rollback` is never refused | AV.2b, AV.2d, AV.3a |
| WS-5 O-R2-1: a governance-affecting close is refused by the gaps it closes | Currency is separated from health gating. `currency::enforce_close_with` accepts the complete G2 result the close itself ran, keyed by the current inputs, even when it is not green. Its warnings are the gaps the work completes. The hard-blocks still gate the close | AV.4a, AV.4b PASS [FAIL] |
| Integration O-1: a W7 subject deleted later dangles and deadlocks | An investigation's `AFFECTS` link to a subject retired since is not a dangling edge. `lineage::is_resolved_investigation_edge` is used by `graph_integrity` and D015. The investigation is listed as complete and can be closed or withdrawn | AV.5a–c PASS [FAIL] |

---

## 2. BC-P2-07: tier duties at every trigger

| Tier | Trigger and duty | Where |
|---|---|---|
| G0 | Every governed operation's admission (§1.2) | `scheduler::admit`/`guard`, called by WS-3/4/5/8/9 hosts |
| **G1** | **Every material mutation, however made.** The product is not a daemon, so a mutation made by an editor, a worker, a script or `gov` is observed at the next `gov` invocation that relies on it: `admit` of a committing operation, `gov status` / `gov continue` / `gov health status`, or the start of `gov doctor`. The tree is compared with `health/observed.json` (the state the last observation, or a run that evaluated every G1 check, saw). The G1 checks whose declared inputs the change touched re-execute; the others are served from the cache. The result is recorded with trigger `mutation.observed` and the changed paths, and the hard-blocks it derives take effect for the admission that observed them. Nothing governed is written. Recursion is excluded (`SUITE_DEPTH`, `OBSERVING`), and so are sandboxes and uninstalled trees | `scheduler::observe` |
| G2 | At close: G0 with the close's subjects (task, inputs, touched paths); pre-implementation readiness re-checked (`TASK_READINESS_REGRESSED`, or recorded degraded when forced); the G2 run; currency against that run; product tests | `verification::close_gate` |
| G3 | At checkpoint/handoff (host: WS-4). New this round: `human_gate_integrity` names work that is CLAIMED, IN_PROGRESS or REVIEW on a task an unanswered gate blocks (medium, with the task and gate as subjects). This is work carried on, and then handed off or checkpointed, without the human decision it waits on | `families_ext::human_gate_integrity` |
| **G4** | After CIT-E, migration, memory or architecture changes. A mutation of a milestone class (`spec_architecture`, `kernel_migration`, `framework_lock`, `model_profile`), or of the memory profile, is observed at G4. The memory profile is the index manifest core plus the effective MEMORY_POLICY pins (embedding, reranker, chunking, lexical, index format). G4/G5/G6 host tier runs are recorded as governance-suite records (WS-4 R2-7, second half) | `observe`, `tier_run` (RecordPolicy::Always for G4–G6) |
| G5 | Full suite at adopt, update, release and full audit | hosts WS-8/WS-9; `gov audit` |
| G6 | A qualification run records `machine_posture` and `machine_trust_anchor_sha256`. `counts_as_qualification` is true only on a provisioned machine. A run declared `QUALIFICATION` on an unprovisioned machine is refused `QUALIFICATION_MACHINE_UNPROVISIONED` (WS-8 IP-R2-WS08-8; OWNER-DECISION-P2-0002 item 4) | `scheduler::qualification_run` |

Two defects found this round in the tier machinery are fixed (both in `2cff5b7`).
- **Trust-state changes did not re-key checks.** Every check now depends implicitly on this machine's trust state. The effective constitutional policy is read from the verified installed kernel, or else from the embedded baseline (`PolicySet::load` reads `kernel_trust::trust(..).policy_root`). So provisioning, installation or revocation re-evaluates what was judged under the previous trust state.
- **Stale blocks could not be cleared.** An explicitly selected catalogue family now runs even when the effective `TEST_POLICY` list does not name it. A block recorded under an earlier effective policy (for example the embedded 4.1.5 baseline before another kernel became the verified one) is therefore re-evaluated, and cleared, by the check that recorded it.
- Found by `ws08_r2::an_unprovisioned_machine_does_not_trust_kernel_material_it_never_admitted`. Machine B observed at G4 while unverified, which recorded a critical `policy_precedence` block. After provisioning and reinstalling, the block could not be re-evaluated, because the 4.1.1 kernel's `TEST_POLICY` does not list that family.

`7c89135` also fixes a sandbox copy race that surfaced as a `high` "could not execute: IO_ERROR" on isolated checks. SQLite removes `-wal`/`-shm` when the last connection closes, and more concurrent readers made the race likelier. A file removed between listing and copying is now skipped.

**Evidence** (final binary; base in brackets):
- Supplementary:
  - G1.a–G1.d PASS [G1.d only]. `gov status` observes direct edits. A planted secret becomes a critical hard-block at once. The next governed operation is refused. The repair is observed without a manual re-run.
  - G1.e–G1.f PASS. A direct architecture edit is observed at G4 and recorded.
  - G2.a, G3.a, G4.a and G6.a PASS [G2.a, G3.a and G6.a FAIL; G4.a PASS]. The G3.0 and G3.b controls pass on both binaries.
- epsilon-r `O5-tiers-G1-G6`, shim; the probe is unmarked:
  - G1: a direct secret edit is followed by the close being refused `HEALTH_HARD_BLOCK`. The base refused `CLAIM_REQUIRED`, never reaching health.
  - G4: governance-suite audit records go 1 → 2 after the architecture CIT-E (base 1 → 1).
- AC16-X1 `X1-W12-G4-wider-check-recorded`: FAIL → PASS.
- **Not yet PASS:** zeta-r `W12-G1-dependency-evidence-invalidated` is FAIL on both binaries.
  - After a direct edit and a rebuild, the dependency *invalidation writes* (retest flag, packet marker) are not made.
  - G1 now detects the unpropagated change: `upstream_change_propagation` names the task at the next observation.
  - The write is `cit::propagation::detect_and_propagate` at rebuild or claim, which is WS-4 R2-3, routed to WS-5 and WS-6 this round.
  - I did not duplicate it from `observe`, because observation must not write governed records from `gov status` or `gov doctor`.
- epsilon-r `O5-G5-update` cannot run on an unprovisioned machine. Both binaries give `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` at the probe's first step. G5 at update is WS-8's host (`ws08_r2::an_update_over_a_defect_the_full_suite_detects_is_refused_and_rolled_back`, green).

## 3. BC-P2-23 (W11 metrics) and BC-P2-44 (Gate U SLOs, one HEALTHY verdict)

### 3.1 W11: `verification::flow`, family `artifact_flow_health` (G4–G6)

The nine metrics of Contract v3:1173-1183 are computed from the repository's own state. Each carries its numerator, denominator, the items that pull it down, and a declared target.
- A metric below target is disclosed as `low`.
- The underlying defects are raised at their own severity by their owning checks, so W11 never double-counts a defect into the verdict.
- Orphan detection reports:
  - detections;
  - precision and false-positive rate, derived from how W7 investigations end;
  - recall, from the latest G6 qualification (only the hidden oracle knows the true orphan set). `null` with its source when none exists.

Evidence:
- Derived zeta-r `W11-quantitative-health.receipt.P2-AR-0033.py`: before 2 of 9 metric lines pass (m1, m8); after, 9 of 9. m2–m7 and m9 went FAIL → PASS.
- The copy's four changes are listed in its header. They are needed on both binaries (WS-5 receipt at close; the superseded-input task left open; tests `not_applicable_with_reason`).
- Supplementary W11.0–W11.m9: 11 of 11 PASS on the final binary, 0 on the base. Every metric moves with an injected fault and recovers when the fault is repaired.

### 3.2 Gate U: `verification::slo`, `framework/health/HEALTH_SLOS.yaml`

**SLOs.** All 15 Gate U SLOs are computed against a declared threshold.
- A threshold is either a kernel policy key (the effective value, so an overlay may tighten it) or a framework default declared in the YAML.
- Each SLO names its **owner**: the check whose finding changes the health state when the SLO is crossed. Examples: D021 for suite freshness; `product_test_health`; `memory_retrieval_regression` for Recall@K; `index_freshness`; `authority_unambiguous` for contradictions; `recovery_rebuild`; `fresh_agent_reconstruction`.
- Where no existing check raises the crossing, the owner is the new family `health_slos` (G1, G3–G6). It covers orphan-graph count, unresolved human gates, task traceability %, readiness coverage, packet size, tokens per task, first-pass completion and handoff failure. So the scheduler observes every SLO.
- Rate SLOs are judged once their population reaches `min_population`.

**The one verdict.** `slo::conditions` evaluates the 13 conditions of Contract v3:995-1008 from the latest outcome of each owning check.
- The owners are the suite families in the health state and the doctor checks, whether recorded or of the run in progress. The YAML lists them.
- `slo::repository_verdict` is the single repository verdict: `HEALTHY` only when all 13 hold. It is carried by:
  - `gov health status` / `gov status` → `health.repository`;
  - doctor **D035**, which fails for what the doctor's own checks do not already fail on. So the doctor verdict is HEALTHY only when the repository verdict is.

New families that own conditions nobody evaluated before:
- `authority_unambiguous` (H1; `contradictions::detect_all`)
- `legacy_authority` (H2)
- `feature_readiness` (H7: explicit readiness)
- `unresolved_audit_findings` (H11: unresolved critical findings of independent audit records)
- `upstream_change_propagation` (H4; `propagation::detect` and invalidated DONE work)
- `research_experiment_data_lifecycle` (H9; IP-WS10-06)

Evidence:
- epsilon-r `U-slos-and-healthy`, direct and shim (`evidence/*/epsilon-r.U-slos-and-healthy.summary.txt`).
  - On the base, these sections leave the audit HEALTHY: SLO-8, 9, 10, 12 and 13 (first case); H2; H7(b); and H11.
  - On the final binary, each of those makes the audit DEGRADED or UNHEALTHY (`health_slos`, `legacy_authority`, `feature_readiness`, `unresolved_audit_findings`), and D035 fails with it.
  - SLO-7 changes the state in the shim run: HEALTHY → DEGRADED, `health_slos`. The direct run cannot open its five gates on either binary; the probe's own `KeyError`.
- Supplementary U.0–U.H11c: 16 of 16 PASS on the final binary, 1 on the base (the U.H11c control).
- AC16-X1 `X1-UxO5-health-reflects-invalid-completed-work`: FAIL → PASS.

---

## 4. Integration points routed to WS-2

| IP | Status | What was done |
|---|---|---|
| WS-3 IP-R2-2 | DONE | Remedy semantics (§1); hosts keep one call |
| WS-5 O-R2-1 | DONE | `enforce_close_with`: a governance-affecting close relies on its own current, complete G2 result (§1.3) |
| WS-5 O-R2-2 | DONE | `graph_integrity` Subjects scope |
| WS-5 IP-R3-7 | DONE | Exit 4 for `GATE_NOT_AUTHORISED`, `GATE_NOT_ANSWERED`, `GATE_DECLINED` and `HEALTH_REMEDY_INCOMPLETE`. `TASK_NOT_READY` and `CLAIM_BASELINE_UNBOUND` stay class 1: they are not control-state or gate blocks. Unit test `error::tests::blocked_class_codes_exit_4` |
| WS-4 R2-7 (doctor/audit over freshness, bindings, contradictions, detect) | DONE | Checkpoint freshness in `continuity_checkpoint_handoff` (medium while the task is in progress); non-verified CIT bindings in `os_binding_integrity`, D033 and the `t2_bindings` currency class; `authority_unambiguous`; `upstream_change_propagation` (G1) |
| WS-4 R2-7, second half (the handoff's "R2-8": G4 results recorded) | DONE | `tier_run` records G4–G6 as governance-suite records |
| WS-4 R2-8 (the handoff's "R2-9": critical block vs proposing the repairing CIT) | DONE, scheduler side | A remedy (§1.3). End-to-end needs WS-3 (IP-R3-WS02-01) |
| WS-4 R2-9 / IP-WS02-20 (SKL-IMPACT-ANALYSIS V1 executable) | DONE | `mode: executable`. Supplementary SKL PASS |
| WS-8 IP-R2-WS08-2/3 | DONE | D032 discloses posture with its admission; `installation_authenticity` states the admission in its finding |
| WS-8 IP-R2-WS08-4 | DONE | `machine_trust_state` adds `floors_sha256`, `installed_record_sha256` and `verified_releases` |
| WS-8 IP-R2-WS08-5 | DONE, scheduler side | Update entry decision (AV.3). WS-8 adds the host call (§6) |
| WS-8 IP-R2-WS08-6 | DONE | No whole literal in `SKILL_SCENARIO_CHECKS.yaml`: `text_parts` are joined by `skills.rs` at run time. The `payload_dirs` addition is the release owner's next version |
| WS-8 IP-R2-WS08-8 | DONE | G6 qualification only on provisioned machines (§2) |
| WS-6 IP-R2-1 | DONE | `graph_integrity` and D015 raise `memory::integrity::check` findings (resolved-investigation edges excluded, O-1), with subjects; stale links de-duplicated |
| WS-6 IP-R2-3 | DONE | `memory::profile::status` in `index_freshness` and D025; D025 also compares the embedder runtime digest |
| WS-6 IP-R2-5 | DONE (confirmed) | `index_manifest` is a currency class. O4 §A row and zeta-r FR row PASS on both binaries |
| WS-6 IP-R2-12 | PARTIAL (deviation) | Store paths: the scheduler's claims input uses `ClaimsStore::path_for`; the sandbox copies the claims store from there to the same relative place (`2e72007`); D026 discloses misplaced state; `recovery_rebuild` reports `paths::misplaced_os_state`. **Reported `low`, not `medium`**: in this tree the owners have not moved the stores yet, so the misplacement is the product's own current layout, not a project defect. Medium would make every project DEGRADED. Raise it once BC-P2-31's moves land (§6) |
| WS-10 IP-WS10-06 | DONE | Family `research_experiment_data_lifecycle` over `lifecycle::suite_findings` and `experiment::task_merge_findings`, at WS-10's severities, subjects named. Consequence in §7 |
| WS-10 IP-WS10-07 | DONE | SKL-RESEARCH-BENCHMARK V1 `mode: executable`. Supplementary SKL PASS |
| WS-9 IP-R2-4 | DONE | An adoption baseline not T2-verified is an `os_binding_integrity`/D033 finding and part of `t2_bindings`. Supplementary T2.adopt |
| WS-2 R3-4 | KEPT (not mine) | WS-6's coverage verifier still reports held heading lines. The reporting-side confirmation step is kept |
| WS-2 R3-8 | DONE | Is BC-P2-23 and BC-P2-44 (§3) |
| WS-2 R3-11 | DONE | `os_binding_integrity`/D033 report plugin-registry entries whose T2 binding is not verified (`plugin_registry_unbound`), consuming WS-3/WS-7's `t2` API. Supplementary T2.reg; gamma-r FRESH.4/5 now name the hand-edited registry |
| Integration IF-1 | DONE | Consumption is not implementation (Contract v3 W5 lines 1115-1119; W7 line 1140; `lineage::work_implements`). A spec record has an implementation path only when one of these holds: a closing report or a CIT `IMPLEMENTS` it; an open task plans it (`requirements`/`scenarios`/`implements`/`tests`); or a DONE task closed before the receipt contract declared it. A DONE task closed under the receipt contract counts only through its receipt. `CONSUMES` (`inputs_consumed`, `required_inputs`) never counts. A requirement a receipt consumed but declared not implemented is a W7 delivery gap, and the finding names the receipts that consumed it. Supplementary IF1.a PASS (IF1.b control) |
| Integration O-1 | DONE | §1.3 |
| Integration O-5 | DONE | The literal is gone, so the embedded-kernel cache carries none. The test placing the cache in its project tree is the test owner's |
| IP-WS02-11 (optional) | NOT DONE | Needs a `TEST_POLICY` key that WS-3's `ENFORCEMENT_MAP` consumes. Left to WS-3 |

## 5. Regression and preservation (at `2e72007`)

- `cargo test --lib`: **213 passed / 0 failed**. The base had 207; six new tests were added (§8).
- `cargo test --test certification`: **136 passed / 0 failed**, run in five groups (`evidence/regression/certification-group*.out`).
- Zero build warnings on a clean rebuild of `gov-runtime`. rustfmt is clean on all 16 Rust files changed since base (`evidence/regression/build-warnings-fmt.out`).
- Three certification assertions changed. Each is justified in its comment, and nothing is weakened for the property the test asserts:
  - **`failure_injection`**: the end state may be unhealthy only through D035 or D031. D035 must name H8 (the scenario's never-undone missing dependency), and D031 must name `graph_integrity`. Before, every doctor check was required to recover. They still do; D035 now reports the scenario's own leftover defect instead of HEALTHY.
  - **`repair::embedder…`**: D025 must still report "consistent:". It now also reports the profile UNGOVERNED (IP-R2-3), because the pin was changed in the overlay directly.
  - **`repair2` chain**: D035 is excluded from the structural-check list. If it fails, it may fail only on H5/H10 with no `health_slos`-owned crossing.
- **R1 held-out**, private path (`evidence/r1-heldout/run-r1-heldout.sh`, measuring this worktree at `2e72007`). Every suite is copied `cmp`-identical, and every result is at its recorded baseline:
  - AR-0027: 26/3
  - AR-0029: 26/2, `ho_f` does not compile
  - AR-0031: 27/7
  - AR-0033: 30/1. The one failure is the known `hv_a::a1` size pin.
- Census: 120 files / 2059 functions. The labelled unpinned copy passes. `derive.py` finds 0 violations in every §6 activity.
- `r1-heldout-r3-ws02-2cff5b7.out` is the same run one commit earlier, with identical results. It is kept only because files cannot be deleted in this session.

## 6. Remaining integration points (for other workstreams)

| ID | Owner | Call / change | Why |
|---|---|---|---|
| IP-R3-WS02-01 | WS-3 | Drop `cit propose` from `control::GOVERNED_WORK_OPS`. The CIT host already guards it with its paths (`cit::propose` → `scheduler::guard(CIT_PROPOSE, guard_paths)`) | The generic site guards it without subjects, so a repairing proposal is refused before its host can be admitted as a remedy. This is the one failing supplementary line, AV.2b-e2e |
| IP-R3-WS02-02 | WS-8 | In `update::apply_update_opts`, after `authority::require`: `let adm = scheduler::admit(p, &Request::new(ops::UPDATE_APPLY).with_subjects(ops::UPDATE_SUBJECTS))?`. Then, before committing (after install and the G5 run), `scheduler::confirm_remedy(p, &adm)?`, rolling back on `HEALTH_REMEDY_INCOMPLETE` | IP-R2-WS08-5 without deadlocking the upgrade. AV.3 shows the decision |
| IP-R3-WS02-03 | WS-5 (hosts) | Pass subjects to `scheduler::guard` at `tasks::create`/`claim` (the task id and its declared inputs). Today they pass `&[]`, so they are judged as a whole | Subject-scoped blocks can then leave independent claims available at the host as well as in the decision (AV.1b uses the decision) |
| IP-R3-WS02-04 | WS-4 | CIT `guard_paths`: include non-record targets (file paths) of the manifest | A CIT repairing a file-level block, such as a secret in `src/…`, then reaches the block's subjects |
| IP-R3-WS02-05 | WS-5 / WS-6 | WS-4 R2-3: `detect_and_propagate` at index rebuild or claim | zeta-r `W12-G1-dependency-evidence-invalidated`. BC-P2-07's remaining line |
| IP-R3-WS02-06 | WS-5 | WS-4 R2-1: `require_current_inputs` at close | AC16-X1 `X1-G1xW6` (FAIL on both binaries) |
| IP-R3-WS02-07 | WS-4 + WS-6 | `records.rs` maps `revalidates` → `TESTS` (R TESTS T, task → task), but `memory::integrity` TESTS signatures do not admit a Work destination. Every generated revalidation task is therefore an `ill_typed` medium finding in `graph_integrity`/D015 (seen in AC16-X1 after the CIT). Map it as `T VALIDATED_BY R`, or admit Work in TESTS | A false integrity finding on every CIT that invalidates DONE work |
| IP-R3-WS02-08 | WS-8 | The `recover` writer produces reports whose `evidence`/`discoveries` objects violate the report schema (seen in `failure_injection`) | Schema-valid recovery evidence |
| IP-R3-WS02-09 | store owners (BC-P2-31: WS-5 claims, WS-3/WS-4/WS-7/WS-9 others) | Move the OS stores; then WS-2 raises `misplaced_os_state` to medium | IP-R2-12's severity |
| IP-R3-WS02-10 | WS-6 | R3-4: heading markers in `memory::coverage` | The confirmation step can then go |
| IP-R3-WS02-11 | WS-4 (optional) | CIT-E repair mode may refuse at entry when `details.remedy_admissible` is not true (the CIT does not reach the block), instead of applying and rolling back | Cheaper refusal; the same outcome |

## 7. Interactions disclosed, and one question

**PASS → FAIL lines** (`evidence/COMPARE-probes.out`). The totals are 9 FAIL → PASS, 2 PASS → FAIL, 48 PASS → PASS and 5 FAIL → FAIL. Both PASS → FAIL lines are probe *preconditions* that no longer hold, and both are explained with evidence.

1. **zeta-r `FR-baseline-green-current`** (BC-P2-03 currency matrix).
   - The probe's fixture scenario SCN-0001 declares no data requirements and has no independent test.
   - WS-10's H4 lifecycle findings (`SCENARIO_DATA_UNDECLARED`, `SCENARIO_WITHOUT_INDEPENDENT_TEST`, medium) now reach the suite through the IP-WS10-06 family. The fixture's baseline audit is therefore DEGRADED, and no green record is taken.
   - The matrix rows then pass vacuously against the init-time record.
   - **Currency itself holds.** The labelled derived copy `evidence/derived/FR-freshness-invalidation.h4-complete.P2-AR-0033.py` makes only the scenario H4-complete (a reasoned `data_requirements_not_applicable` plus one independent acceptance obligation). It gives **26/0 on both binaries**, with a green baseline.
   - epsilon-r O4 §A–§E are identical on both binaries. §C's fresh green holds after the SLO population fix in `7c89135`.
   - alpha-r, beta-r, gamma-r and delta-r FRESH are unchanged, apart from gamma-r FRESH.4/5 now naming a hand-edited plugin registry (R3-11).
2. **AC16-X1 `X1-O4-green-stale-after-direct-spec-change`**.
   - Its precondition is a green record, current right after the CIT that invalidated DONE work. In the same chain, `X1-UxO5` (BC-P2-44) requires that state not to be HEALTHY.
   - On the final binary the post-CIT audit is DEGRADED from:
     - the invalidated DONE work (`upstream_change_propagation`);
     - the generated revalidation task's `ill_typed` TESTS edge (IP-R3-WS02-07);
     - the fixture scenario's H4 gaps.
   - So D021 is already false before the direct edit. Once IP-R3-WS02-07 is fixed and the fixture is H4-complete, a green record still cannot coexist with the invalidated DONE work: Contract v3:1135-1136 says stale evidence cannot remain green.
   - The O4 property is shown directly by epsilon-r `O4-suite-currency` and by the derived FR copy.

**Question for the owner or orchestrator** (it does not block these claims). The two lines above are acceptance lines of BC-P2-03, which is not a WS-2 class this round.
- Should H4 scenario-chain authoring gaps (WS-10's `medium`) degrade suite health, as IP-WS10-06 specifies and this build implements?
  - If yes: the verifier should judge FR/X1-O4 on H4-complete fixtures (as the derived copy does).
  - If no: WS-10 lowers those severities in `lifecycle` (its file), and the unedited FR baseline turns green again with no WS-2 change.
- X1-O4 conflicts with X1-UxO5 by construction. One of them needs a chain-specific reading.

## 8. Files changed (base `53897c1` → `2e72007`)

**Runtime:**
- `runtime/src/scheduler/catalogue.rs`, `scheduler/mod.rs`, `scheduler/sandbox.rs`
- `runtime/src/verification/mod.rs`, `currency.rs`, `lineage.rs`, `reporting.rs`, `families_ext.rs`
- **new:** `runtime/src/verification/slo.rs`, `runtime/src/verification/flow.rs`
- `runtime/src/doctor.rs`
- `runtime/src/error.rs` (exit-code mapping)
- `runtime/src/skills.rs` (`text_parts`)

**Framework:**
- **new:** `framework/health/HEALTH_SLOS.yaml`
- `framework/health/SKILL_SCENARIO_CHECKS.yaml`
- `framework/policies/TEST_POLICY.yaml` (eight families appended)

**Tests:** `tests/certification/{failure_injection,repair,repair2}.rs` (§5).

All files are in WS-2's ownership list, apart from the three certification tests, which were updated for the behaviour change. No declared additive exception was needed.

**New unit tests:**
- `scheduler::catalogue::tests::committing_operations_and_update_subjects_are_known`
- `scheduler::tests::{subject_scoped_blocks_leave_independent_work_available, an_update_is_the_remedy_of_an_overlay_block_but_not_of_a_record_block}`
- `verification::slo::tests::{every_gate_u_slo_and_condition_is_declared_with_an_owner_and_threshold, healthy_only_when_every_condition_holds}`
- `error::tests::blocked_class_codes_exit_4`

Existing tests were extended for IF-1 and for the declared-rule block derivation.

## 9. Evidence index (`evidence/`)

| Path | What |
|---|---|
| `WS02-r3-supplementary.py`, `.after.out`, `.before.out` | Builder probe, 65 lines in groups AV, IF1, G1–G6, W11, U, T2, SKL: **64/65** final binary (AV.2b-e2e waits on WS-3), **11/65** base (controls) |
| `run-audit-probe.sh` (+ `.diff-vs-P2-AR-0023.txt`), `run-derived-probe.sh` | Private runners. Audit-of-record probes are run unedited. The adapter is the round-2 integration builder's derived root-channel shim, or its WS-5 receipt adapter (`*-ws05` labels), applied to both binaries alike |
| `before*/`, `after*/` | Probe outputs on the base binary and the final binary. `*.summary.txt` holds compact views of the unmarked epsilon-r U probe (`summarize_unmarked.py`) |
| `COMPARE-probes.out`, `compare_probes.py` | Marked-line comparison (P2-AR-0023's tool, unchanged) |
| `derived/` | Labelled derived copies, each header listing every change: W11 (receipt at close), FR (H4-complete scenario) |
| `gov-health-checks.json` | The catalogue as `gov health checks` reports it (deps, tiers, enforcement with scope and remedies) |
| `regression/` | lib, certification (5 groups), warnings and rustfmt at `2e72007` |
| `r1-heldout/` | Private R1 runner (phased; derived from P2-AR-0032's) and its outputs |
