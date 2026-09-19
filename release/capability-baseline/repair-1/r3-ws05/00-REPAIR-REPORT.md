# WS-5 repair report — repair iteration 1, round 3 (P2-AR-0036)

| | |
|---|---|
| Run | P2-AR-0036, `capability-repair`, workstream WS-5 |
| Handoff | `release/orchestration/phase-2/HANDOFFS/P2-HO-0035-repair-1-r3-ws05.md` (+ P2-HO-0031, -0020, -0010) |
| Branch / worktree | `phase2/repair-1-r3-ws05` |
| Base | `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree), `product_code_digest` `797da37c…1fe1` |
| Product commits | `4927e77`, `25f935c`, `71dfa45`, `60460bc`, `48e4c7d`, `a7bb4d2` (product tree final at `a7bb4d2`, `product_code_digest` `658fcb12…8abc`; `governed_state_digest` unchanged `8f191e39…948f`) |
| Agent model | Claude Opus 5 (1M context), `claude-opus-5[1m]` |

Builder evidence only (Contract v3 O3). Nothing here is acceptance: every item is `REPAIRED_CLAIMED` (or `CONFIRMED`)
with evidence, for fresh independent verification.

## 0. What changed, in one view

| Item | Status | Where |
|---|---|---|
| **BC-P2-24** governed, linked work generated from every Contract v3:572-583 source and each health failure; W7 work adopted; idempotent | REPAIRED_CLAIMED | new `runtime/src/orchestration/generation.rs`, new `framework/taxonomy/WORK_GENERATION.yaml`, `tasks.rs` (`create_generated`, close), `status.rs` (`continue`), `dag.rs` (`replan`), CLI `task generate` + post-command site |
| **BC-P2-13 in-task hook** (WS-4 r2 R2-4; round-1 WS-5 IP-3 / WS-4 IP-R3-6) | REPAIRED_CLAIMED | `tasks.rs` close step 10a `material_changes` over `cit::materiality::classify_paths`; `cit_window_writes` over `cit::binding::verified_writes` |
| WS-4 r2 **R2-1** close calls `require_current_inputs` | REPAIRED_CLAIMED | `tasks.rs` close step 12a + post-DONE clearing |
| WS-4 r2 **R2-2** staleness in claim / dag / list / show | REPAIRED_CLAIMED | `dag.rs` step 7a (`stale_inputs`), `tasks::{list, show}`, claim refusal via the DAG |
| WS-4 r2 **R2-3** `detect_and_propagate` at claim | REPAIRED_CLAIMED | `tasks::claim` (index-rebuild side is WS-6's `memory/indexer.rs`; not needed once claim propagates) |
| WS-4 r2 **R2-5** READY through the manifest predicate | CONFIRMED (no change) | `dag.rs` step 3 = `context::manifest` entry satisfaction (`require_ready`'s predicate) |
| WS-4 r2 **R2-6** `observe_boundaries` after status changes and claims | REPAIRED_CLAIMED | `tasks::{set_status_internal, claim, continue claim}` |
| WS-10 r2 **IP-WS10-11** experiment tasks close through their lifecycle | REPAIRED_CLAIMED | `tasks.rs` close step 10b |
| WS-10 r2 **IP-WS10-12** DAG blockers and readiness cells from the scenario chain | REPAIRED_CLAIMED | `dag.rs` step 5 (`chain_blockers`), `readiness::evaluate_in` (computed chain cells) |
| WS-10 r2 **IP-WS10-13** `test_data` in the test-obligation schema; influence backlink at create | REPAIRED_CLAIMED | `test-obligation.schema.json` 1.1.0; `tasks::create` → `lifecycle::record_influence` |
| **BC-P2-31** claims store and claim trees at `paths::store_path` with `relocate_legacy` (WS-6 r2 IP-R2-7) | REPAIRED_CLAIMED (WS-5 writers) | `memory/claims.rs` (`path_for`, `open`, linked worktrees), `tasks::claim_trees_dir` |
| **Availability rule** at task create / claim / close | REPAIRED_CLAIMED (task operations) | `tasks::guard_work` (create, claim); close keeps the full gate so an uncleared remedy does not commit |

Owner-decision questions: **none**.

### 0.1 The close, in order (documented in `tasks::close`; three steps added, the rest unchanged)

`1` normalise the return · `2` another session's claim · `3` evidence payload · `4` the claim (session, worktree) · `5`
sealed claim baseline · `6` designated role · `7` independence · `8` governing gates · `9` observed mutations (scope, OS-written
state; CIT coverage now bound to content) · `10` production merge · **`10a` material changes only through change control** ·
**`10b` experiment lifecycle** · `11` index pins / freshness · `12` consumption receipt · **`12a` current inputs / re-test
evidence** · `13` health close gate. After DONE: report sealed, re-test flag cleared only as 12a allowed, a revalidation task
resolves the work it revalidates, and the work the report calls for is generated.

Why: who may close and whether the work may complete at all come first; the repository's own state (9-10b), observed
independently of the worker, is weighed before the worker's account (12, 12a), so an incomplete receipt never masks an
out-of-scope, forged or material mutation; the health gate (13) runs last because it may execute checks.

## 1. BC-P2-24 — governed work generated from events

**Requirement** (repair-delta BC-P2-24; Contract v3:571-583; AC-5): each source — failed tests, audit findings, research
discoveries, human decisions, CIT effects, lessons, missing tools/skills, retrieval failures, security findings, performance
regressions — and each health failure generates governed, linked work in the same DAG when it occurs. Accept: gamma-r
`I3-generation` ≥1 linked task per source; epsilon-r `O5` S8.

### 1.1 What changed

* **One engine** `orchestration::generation` (module documentation is the design). Each source is a detector over what the
  event durably left, never a caller's label: product-test records (`failed_tests`), the health state + latest honoured
  governance-suite record (`health_failures` → audit / health / security / knowledge-fabric findings), worker returns and
  sealed close reports (`discoveries`: discoveries, unresolved items, proposed decisions), T2-verified decisions derived from a
  human answer (`human_decisions`; a declining answer on governed work also `AFFECTS`/replans it), completed work a CIT marked
  for revalidation with no revalidation task (`cit_effects`), lesson records (`lessons`), open tasks whose required
  tools/skills do not resolve (`missing_capabilities`, the task `blocks` every task that needs it), open failure memory
  (`failures`: retrieval misses, tool failures, bugs, regressions — `memory::failures::open_failures` + `link_follow_up`), and
  telemetry measurements against their baseline or history (`detect_performance_regressions` → a durable `regression`
  failure record, then work).
* **Linked**: `derived_from` the source record(s) (a DERIVED_FROM edge), `generation: {source, subject, key, occurrence,
  records, detected_by, detected_at, contract, detail}`, `blocks`/`AFFECTS`, failure `follow_up.task`. Class, designated role
  and paths per source come from the kernel taxonomy `framework/taxonomy/WORK_GENERATION.yaml`.
* **Idempotent**: one task per occurrence key, at most one open task per source subject; CANCELLED declines the occurrence;
  after DONE only newer evidence recurs (`-rN`). Missing-capability work is **augmented** (more `blocks`), not duplicated.
* **Adoption**: WS-2 W7 orphan investigations (`generated_by: health:lineage_orphans`), CIT-propagation revalidation tasks
  (`revalidates`) and readiness-planner gap tasks count as their source's work (`source_of`), never duplicated (WS-2 r2 R3-5).
* **When the event occurs**: after every governed write command (CLI post-command site, additive; derived/maintenance
  commands excluded), inside `task close`, `continue` and `task replan`, and on demand `gov task generate [--dry-run]`
  (classified in `g0_label` and `COMMAND_GUARDS`). Read-only commands never write; what they record durably (a doctor result, a
  retrieval miss) becomes work at the next governed operation. Generation is a governed write (`control::guard_write`:
  FREEZE/PAUSE/trust), so under freeze nothing is generated and the report says why.
* **Current conditions only** (found by the O5 S8 re-run, fixed at `60460bc`): a failing health result made stale merely by
  the event's own records (the audit record, a generated task) is **re-evaluated** before generation reads it, exactly as the
  scheduler guard re-evaluates a stale block (`reevaluate_stale_failures`: families via `scheduler::run_suite`, doctor via
  `doctor::run`, no audit record), only for failures that could generate work and are not already remedied by open work.
* **No loops**: findings about generated work never generate work — health findings naming a generated task, and (fixed at
  `48e4c7d`, found by the W03 re-run) retrieval misses on queries made for generated work (a follow-up's own context compile).
* **Not project work**: `outside_project_checks` in the taxonomy — `installation_authenticity` (D032, bootstrap installation)
  is the administrator domain's (trust provisioning, OWNER-DECISION-P2-0002); it is reported under `skipped` with its remedy
  instead of a security task no role could close. `same_condition` merges a doctor check and a family reporting one condition
  (D011 → `path_map_compliance`, D012 → `secrets_sensitivity_indexing`, …); findings naming the same path merge.
* Generated tasks are created by `tasks::create_generated` (same create path, guard and DAG-derived status; provenance
  `gov work generation`); schema `task.schema.json` 1.2.0 declares `generation` (OS-owned; a caller value is kept as
  `generation_requested`) and `remedies`.

### 1.2 Product checks

`generation::reconcile` (every governed write, close, continue, replan, `task generate`); unit tests
`generation::tests::{generation_is_idempotent_per_occurrence_and_subject, missing_capability_work_is_augmented_not_duplicated,
the_taxonomy_declares_every_source, a_condition_no_project_role_can_remedy_is_reported_not_generated}`; certification
`ws05r3::{every_event_source_generates_linked_governed_work_once, a_red_result_made_stale_by_the_events_own_records_is_reevaluated_not_dropped,
a_security_finding_generates_remediation_that_stays_available_under_its_block, a_cit_effect_on_completed_work_generates_one_linked_revalidation_task,
a_failing_product_test_family_generates_repair_work}`. The stale-RED test and the no-loop assertion each fail with their fix
disabled (checked, then restored).

### 1.3 Probes re-run (unedited, through the adapter on both binaries; `evidence/audit-probes/COMPARE.out`)

gamma-r `I3-generation` (tasks generated at each event; base = round-3 base binary):

| source | base | after (task, link) |
|---|---|---|
| readiness gaps | 2 | 6 (readiness planner, adopted) |
| failed tests (`verify product`) | 0 | 1 — TASK-0007 derived_from AUD-0002 (the failing run) |
| audit findings (`audit`) | 0 | 1 — TASK-0008 derived_from AUD-0003 |
| research discoveries / unresolved / proposed decision / lesson (`handoff return`) | 0 | 4 — TASK-0009..0011 derived_from HND-0001; TASK-0012 derived_from L-0001 |
| human decisions (A; B declining) | 0 | 1 + 1 — TASK-0013 ← D-0001, TASK-0014 ← D-0002 |
| CIT effects | 0 | 0 — on **both** binaries the probe's `cit propose` yields no id, so `cit execute` runs with none (`USAGE`); the source is exercised by `ws05r3::a_cit_effect_on_completed_work_generates_one_linked_revalidation_task` |
| missing tool / skill | 0 | 2 — TASK-0015/0016 at `task create` of TASK-NEED, `blocks: [TASK-NEED]` |
| retrieval failures | 0 | 1 — TASK-0019, linked from FAIL-0001 `follow_up.task` (generated at the next governed write, the audit) |
| security findings | 1 (W7 only) | 3 — TASK-0018 security `path_map_compliance` ← AUD-0004; W7 TASK-0017 (adopted); TASK-0019 above |
| performance regressions | 0 | 1 — TASK-0020 derived_from FAIL-0002 (durable regression record) |

The probe's per-line counts attribute work to the next governed write where the event command is read-only (b8, b9).

epsilon-r `O5` S8 ("remediation / task generation from a RED health result"): base `task records before/after 0 / 0` →
after `0 / 2` (security remediation remedying D011 + `path_map_compliance`, audit finding `adapter_portability`).

### 1.4 Limits

* A `cit-effect` task is generated by the engine only when propagation could not generate its revalidation task; normally
  WS-4's propagation generates it and the engine adopts it (the certification test shows one, never two).
* Generated tasks take the next free sequential id, so a caller that passes explicit `--id`s in sequence can collide
  (`DUPLICATE_ID`, correctly refused). zeta-r W03 does this: W3-m4/-m5 FAIL unedited because TASK-0103/0104 were taken by the
  follow-ups of the retrieval misses its own `context compile` runs recorded; a labelled derived copy with only those three
  ids renamed gives 40/40 on both binaries (identical observations). INFO for verifiers/probe authors, not a defect claim.
* Every `context compile` miss (WS-6 detection) becomes a follow-up task; the volume is WS-6's miss policy.
* Cost: reconciliation runs after every governed write (and may re-run stale failing checks); not measured against the
  Gate U SLOs (IP R3-WS5-10).

## 2. BC-P2-13 in-task half — material changes made inside tasks

**Requirement** (Contract v3:446, :638-647; framework §47-48): materiality is determined from what changes, and material
changes cannot complete outside CIT-P/CIT-E, including edits made inside ordinary tasks. Accept: delta-r `K3`
K3.b*.mislabel and K3.outside.* PASS; gamma-r `G1G2` G1.b3.

**What changed.** Close step 10a `tasks::material_changes`: the paths the close observed are classified by
`cit::materiality::classify_paths(p, paths, claim_commit)` (WS-4); every finding `requiring_cit()` refuses
`MATERIAL_CHANGE_REQUIRES_CIT` (each finding named, with the remediation to propose a CIT inside the claim window) unless a
CIT committed **inside the claim window wrote exactly that content** (`cit_window_writes` over
`cit::binding::verified_writes`, WS-4 IP-R3-6; the same content binding now decides out-of-scope CIT coverage at step 9 —
round-1 WS-5 IP-3). Exempt, narrowly: initial authoring of specification by specification-producing work (a record created
in the window by a spec class, superseding nothing) and a readiness cell's own gap work. Product source may be changed only
by classes contracted to change it (`SOURCE_CHANGING_CLASSES`); a `discovery` task writing `src/**` is refused.

**Probes.** K3: `K3.outside.2` FAIL → PASS; K3.b1-b8.mislabel, K3.outside.1/.3 PASS on both. G1.b3 (c): base refused only
by `GOVERNANCE_SUITE_STALE` (evidence currency) → after `MATERIAL_CHANGE_REQUIRES_CIT: acceptance_criteria_change REQ-0001`.
gamma-r FRESH: governance-file edits by `governance` tasks are now refused as material (`governance_change`) before the
evidence-currency check.

**Tests.** `ws05r3::{material_changes_inside_a_task_complete_only_through_change_control, cit_coverage_is_bound_to_the_content_the_cit_wrote}`.

**Limits.** The classifier (what is material) is WS-4's; the hook applies it. delta-r N1-N2's discovery task that writes
`product/a.txt` stops at 10a instead of at the receipt (base stopped at `RECEIPT_INVALID`); both are refusals.

## 3. WS-4 round-2 APIs wired (R2-1, R2-2, R2-3, R2-5, R2-6)

* **R2-1** close step 12a `cit::propagation::require_current_inputs`: `INPUTS_STALE` / `RETEST_EVIDENCE_REQUIRED`; the
  re-test flag and staleness are cleared after DONE only when it returned `clears_retest`, and the close records
  `revalidated_inputs`.
* **R2-2** `dag::evaluate` step 7a names inputs changed since the task's work consumed them (unpropagated, direct edits);
  `task list` carries `stale_inputs`; `tasks::show` returns `derived.staleness` (`task_staleness`) and the DAG evaluation
  (the CLI `task show` arm still prints the stored record — IP below); a claim of stale work is refused through the DAG.
* **R2-3** `tasks::claim` runs `detect_and_propagate(p, "task claim", false)` before evaluating the task, so a direct change
  reaches its dependents (retest flags, revalidation work) without an operator; not-started work acknowledges it by
  re-delivering its context.
* **R2-5** confirmed, unchanged: READY/runnable are derived by `dag::evaluate`, whose step 3 applies the manifest's entry
  satisfaction (`require_ready`'s predicate, CONTRADICTORY included), with the documented producer exception.
* **R2-6** `tasks::observe_boundaries` (skips health-check sandboxes) after every status change, claim and `continue --claim`.

**Probes.** zeta-r W06 unedited cannot start on this tree: its fixture's implementation tasks are blocked by the computed
scenario chain (IP-WS10-12) before the W6 scenario begins. Labelled derived copy (fixture states its two unevidenced chain
cells `N/A_WITH_REASON`; the B1 claim outcome recorded instead of asserted): base 20 PASS / 8 FAIL → after 19 PASS / 3 FAIL.
B1's claim of the stale task: base granted → after refused (`TASK_NOT_RUNNABLE`: retest required after propagation — the
pre-change packet is never worked), so B1's six close-time observations (four of them FAIL on base) are not reached;
`W6-s7-retest-flag-not-cleared-by-close` FAIL → PASS; the three `(direct)` lines that read the stored flag through a
read-only `task list` immediately after the edit stay FAIL (at that moment the list shows `stale_inputs` and the DAG blocks
the task; the flag is stored at the next claim). delta-r N1-N2: 14 PASS on both.

**Tests.** `ws05r3::stale_inputs_are_seen_propagated_at_claim_and_cleared_only_by_retest_evidence`.

## 4. WS-10 round-2 integration points

* **IP-WS10-11** close step 10b `lifecycle::experiment::task_lifecycle_refusal` → `EXPERIMENT_LIFECYCLE_REQUIRED`
  (`--force` L3 recorded). Test `ws05r3::an_experiment_task_closes_only_through_its_lifecycle`.
* **IP-WS10-12** `dag::evaluate` step 5 adds `lifecycle::scenario::implementation_blockers` for implementation-class tasks
  (minus cells the feature states `N/A_WITH_REASON`); `readiness::evaluate_in` computes `success_criteria`, `failure_criteria`,
  `representative_test_data`, `independent_acceptance_tests` from `readiness_cells` — the chain refutes an assertion it
  contradicts, never upgrades a cell the author keeps open, and an authored silent N/A stays `invalid` (fixed at `71dfa45`,
  found by H2H3). gamma-r H2H3: silent-N/A cell → state MISSING, still listed invalid; chain gaps now named.
* **IP-WS10-13** `test-obligation.schema.json` 1.1.0 declares `test_data`; `tasks::create` records influence backlinks
  (`lifecycle::record_influence`) for cited evidence ids. Unit test `tasks::tests::cited_evidence_and_remedies_are_read_from_the_contract`.

## 5. BC-P2-31 (WS-5 writers) — claims store and claim trees

**Requirement** (Contract v3:188, :202, :352; D-0007 T2): claims survive deletion of everything classified derived.
**What changed** (WS-6 r2 IP-R2-7): `ClaimsStore::path_for` = `paths::store_path(root, "claims")`
(`.governance-state/claims.db`; a linked worktree resolves to the main worktree's store); `open` runs
`relocate_legacy_store` under the store lock, moving `.governance-runtime/claims.db` with every live claim (a copy is never
the store; a stray legacy file left after a move is reported by `paths::misplaced_os_state`); claim baselines and carried
sets at `store_path(root, "claim-trees")` (`.governance-state/tasks/<id>/`), relocated from the runtime directory on first use.

**Probes.** beta-r D6 unedited stops at the fixture's implementation-task claim on both binaries (independence gate / chain).
Labelled derived copy (claimed task is `refactor` without `--feature`; reranker override not applied, its plugin registration
being refused on both binaries): `[B] differences` base `{"claims": [[TASK-0001,S-probe]] → [], "control": …}` → after
`{"control": …}` only; an intruder session's claim after deleting `.governance-runtime/`: base `ok` → after `TASK_CLAIMED`.
`D6-b2-B` stays FAIL on both because emergency-control state still lives in the runtime directory (WS-3's writer, IP-R2-8).
gamma-r E4 unedited reaches the store by its old path (tracebacks where it ages a lease in that file); a derived copy using
the new path reproduces base behaviour (expired lease reported, swept by `recover`, clone has no claims).

**Tests.** unit `memory::claims::tests::a_legacy_store_moves_to_its_state_location_with_its_live_claims`; certification
`ws05r3::claims_and_claim_baselines_survive_deleting_the_derived_runtime`; `repair::claims_survive_full_memory_rebuild` and
`ws06::deleting_everything_classified_derived_keeps_claims_control_and_registration` updated (§8).

## 6. Availability rule (P2-HO-0031)

`tasks::guard_work` (create, claim): the write guard always runs; the health half is `scheduler::guard` with the paths the
operation relies on (a path-scoped block governs only work inside its scope); a hard-block whose check the work `remedies`
does not refuse it (`availability.remedied_blocks` reported); any other block refuses with the scheduler's typed
`HEALTH_HARD_BLOCK` naming each block, its check and scope. Close keeps the full close gate, so a remedy that has not cleared
its block does not commit. Generated remediation carries `remedies`. Test
`ws05r3::a_security_finding_generates_remediation_that_stays_available_under_its_block` (unrelated claim refused naming the
block; remediation claimable under it).

## 7. Integration points

### 7.1 Routed to WS-5 this round

| IP | Status |
|---|---|
| WS-6 r1 IP-4 (`open_failures` + `link_follow_up`) | done — `generation::failures`; failure records link their task |
| WS-2 r2 R3-5 (adopt W7 tasks) | done — `source_of` / `existing` |
| WS-4 r2 R2-1..R2-6, IP-R3-6; round-1 WS-5 IP-3 | done (R2-4 = §2; R2-5 confirmed) |
| WS-10 r2 IP-WS10-11/12/13 | done (§4) |
| WS-6 r2 IP-R2-7 | done (§5) |

### 7.2 New integration points (declared additive exceptions and follow-ups)

| # | Owner | Where | What | Why |
|---|---|---|---|---|
| R3-WS5-1 | WS-3 (declared additive here) | `cli/src/main.rs` | `TaskCmd::Generate` + `g0_label` arm + `run` arm; post-command block after `run(&cli)` calling `generation::after_command` | BC-P2-24 "when it occurs"; review with WS-3's role/guard semantics |
| R3-WS5-2 | WS-3 (declared additive here) | `orchestration/control.rs` `COMMAND_GUARDS` | `task generate` (`replan_tasks`, Write), `task generate --dry-run` (Read) | G0 classification of the new subcommand |
| R3-WS5-3 | integration (declared additive) | `orchestration/mod.rs` | `pub mod generation;` (new WS-5 file `orchestration/generation.rs`, new taxonomy `framework/taxonomy/WORK_GENERATION.yaml`) | new module |
| R3-WS5-4 | WS-3 | CLI `task show` arm | call `orchestration::tasks::show` (record + DAG evaluation + `task_staleness` + generation source) instead of printing the stored record | R2-2 "show" surface |
| R3-WS5-5 | WS-2 | `scheduler/sandbox.rs`, currency input, doctor D017/D026 | read `paths::store_path(root, "claims")` (WS-6 IP-R2-12, still open) | the store moved this round |
| R3-WS5-6 | WS-3 | `orchestration::control` state | `store_path(root, "emergency-control")` + `relocate_legacy` (WS-6 IP-R2-8) | D6-b2-B's remaining half |
| R3-WS5-7 | owner of `runtime/src/recovery.rs` | `recovery::recover` report | write `evidence` / `discoveries` / `unresolved` items as strings (the report schema) | pre-existing: a recovery report fails `schema_invariants` (HIGH) and, once re-evaluated, hard-blocks `task.close` (seen in `failure_injection`) |
| R3-WS5-8 | WS-4 / WS-10 | `cit::propagation` markers, `lifecycle::record_influence` | attribute OS writes made into governed records inside another task's claim window (seal or recorded write set) so that close never reads them as that worker's mutations | latent; not observed in the suites |
| R3-WS5-9 | WS-8 | `framework/KERNEL.yaml` `schema_versions` | `task` 1.2.0 (was already 1.1.0 vs listed 1.0.0); add `test-obligation` 1.1.0 | schema version registry |
| R3-WS5-10 | WS-2 | Gate U / SLO | measure the per-write reconciliation and claim-time checkpoint cost | performance of the event hooks |
| R3-WS5-11 | WS-2 / WS-6 | `memory_retrieval_regression` in a health sandbox | symbol route returns nothing inside the sandbox (`isolated_in_sandbox: true`); reproduced with the base binary | pre-existing; hidden by the cache |

## 8. Existing builder tests changed, and why

| Test | Change | Reason |
|---|---|---|
| `greenfield::greenfield_end_to_end` | scenario states `data_requirements_not_applicable` | IP-WS10-12: the H4 chain gates READY; a silent N/A is a gap |
| `repair::claims_survive_full_memory_rebuild` | store asserted at `.governance-state/claims.db`, not in the runtime dir | BC-P2-31 |
| `repair2::genuine_412_consumer_updates_…` | INV-013 tree hash excludes task records `generated_by: gov work generation` by exact path | generated work is OS-written, like the audits/reports already excluded |
| `ws03::round_two_call_sites_…` | a recorded miss is now linked to its follow-up task and no longer *open* | BC-P2-24 retrieval failures |
| `ws04r2::upstream_change_reaches_completed_work` | work writing `src/**` is `refactor`, not `discovery` | BC-P2-13 in-task: discovery may not change product source |
| `ws05::close_observes_os_written_state…` | claim baseline path `.governance-state/tasks/<id>/` | BC-P2-31 |
| `ws05::independence_is_established_from_recorded_authorship` | scenario data link explicit; the hand-written obligation is withdrawn before the designer authors it | IP-WS10-12; BC-P2-13 (changing an existing acceptance obligation inside a task is material) |
| `ws06::deleting_everything_classified_derived…` | `claims` no longer expected among misplaced stores; store asserted at its location | BC-P2-31 (the other two stores still expected misplaced) |

`tests/certification/main.rs` gains `mod ws05r3;` (additive); `tests/certification/ws05r3.rs` is new (10 tests).

## 9. Regression and R1 preservation (`evidence/regression/`, `evidence/r1-heldout/`)

* `cargo test --lib`: **215 passed / 0 failed** (base 207). `cargo test --test certification`: **146 passed / 0 failed**
  (base 136), run in three parts at `a7bb4d2` (63 + 55 + 28). `cargo build --release`: 0 warnings. `rustfmt --check` clean on
  every touched `.rs` file (the two reported files, `srr.rs` and `section6.rs`, are untouched and differ at the base).
* R1 held-out suites, unedited, private path `…/p2ar0036/r1-P2-AR-0036-private`, measuring this worktree at `48e4c7d` (product
  tree identical to `a7bb4d2` except the added test file): AR-0027 **26/3**, AR-0029 **26/2** + `ho_f` not compiling, AR-0031
  **27/7**, AR-0033 **30/1** (`hv_a::a1` size pin) — each equal to its recorded baseline. Census 119 files / 2060 functions;
  the unpinned `hv_a::a1` derivation reports §6 violations 0 for every activity (that copy is byte-identical to the round-2
  integration's labelled copy `integration-2/evidence/r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0032.rs.txt`, so its
  printed label names P2-AR-0032). `section6` certification tests green.

## 10. Evidence method

* `evidence/audit-probes/run-audit-probe.sh` — derived from WS-5's round-2 runner (diff in `runner-diff-vs-P2-AR-0026.out`).
  Modes `after-shim` (this binary) and `base-shim` (base `53897c1` built in scratch, gov `5ff6ce9c…`), both through the
  round-2 integration's root-channel adapter, unmodified. Change made this run: base modes mirror the **base tree** (its own
  framework payload); mirroring this worktree made the base binary refuse `init --source` on the changed payload, which would
  have masked base behaviour.
* `run-derived-probe.sh` runs the labelled derived copies in `derived/` (each header states exactly what it changes):
  E4 (store path), W03 (three explicit ids), W06 (two chain cells N/A; B1 claim outcome recorded), D6 (claimed task class;
  reranker override not applied). `compare.sh` → `COMPARE.out` prints the before/after lines used above.
* After-shim probes re-run at `a7bb4d2`; base-shim outputs are from the base binary (unchanged throughout).

## 11. Evidence index (`evidence/`)

`audit-probes/` (runners, `COMPARE.out`, `base-shim/`, `after-shim/`, `derived/`, runner diff) · `regression/`
(`*.final.*` at `a7bb4d2`; `*.dev.*` intermediate runs at `25f935c`; base lib run and base build) · `r1-heldout/`
(`run-r1-heldout.sh`, `r1-heldout-final-48e4c7d.out`, the unpinned `hv_a` derivation copy, runner diff vs P2-AR-0032).

## 12. Owner-decision questions

None.

## 13. Process disclosures

* The R1 held-out runner was started as a detached shell whose output the runner itself writes into
  `evidence/r1-heldout/`; its console went to a scratch file. No task-output store was read.
* Two scratch clean-ups (`rm -rf`) were refused by the environment; fresh scratch directories were used instead.
* Found and fixed during this run by probe re-runs (not by the handoff): stale-RED re-evaluation (O5 S8), the retrieval
  follow-up loop (W03), the silent-N/A invalid on chain cells (H2H3), D032 administrator-domain work (G1G2/O5), D011's
  condition mapping.
