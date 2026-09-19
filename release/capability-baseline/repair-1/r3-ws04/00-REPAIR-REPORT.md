# P2-AR-0035 — Repair iteration 1, round 3, WS-4: sealing and lineage completeness

| Field | Value |
|---|---|
| Run | P2-AR-0035, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0034 (WS-4 round 3), P2-HO-0031 (round-3 common, availability rule), P2-HO-0020, P2-HO-0010 |
| Branch / base | `phase2/repair-1-r3-ws04` from `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree; `product_code_digest 797da37c…1fe1`) |
| Work commits | `958b2b2` (main change), `ff529e9` (task-field protection; the pending gates.rs re-seal as an ignored integration test), `bda16a2` (CHANGE_POLICY comments). The final work commit is `bda16a2`, followed by the evidence commit that adds this directory. |
| Product after | `product_code_digest 67d7f7b87e62893cb4dcbc375d0b8232599907475c623736e3200a4c16b14b41` at `bda16a2`. `governed_state_digest` is unchanged (`8f191e39…948f`). |
| Items | Integration O-7; WS-5 r2 IP-R3-1, -2, -3, -4, -5, -6; WS-2 r2 R3-1, -2, -3; WS-10 r2 IP-WS10-08, -09, -10; WS-6 r2 IP-R2-2, -6, -10; WS-8 r2 IP-R2-WS08-7; the availability rule at WS-4's host sites. Every item is **REPAIRED_CLAIMED** on the WS-4 side. The parts in other owners' files are integration points (§16). One of them, **IP-R3-WS04-01** (WS-3, `gates.rs`), is **integration-critical**: it must land together with this branch. A patch for it is supplied, and the end state was measured green (§1.6). |
| Regression | `cargo test --lib` **215 / 0** (base 207, +8). `cargo test --test certification` **144 / 0, 1 ignored** (base 136, +8 `ws04r3`; the ignored test is IP-R3-WS04-01's, run at integration). Builds have 0 warnings. rustfmt is clean on every changed file. |
| R1 held-out | Measured at `bda16a2` through a private path. AR-0027 26/3, AR-0029 26/2 (`ho_f` does not compile), AR-0031 27/7 and AR-0033 30/1 (`hv_a::a1` size pin only) all match their recorded baselines, with the same failing tests. The normalised failure messages are identical to the round-2 integration (42 lines, empty diff). Census: **118 files / 2014 functions**. The unpinned copy finds **0 violations** in every §6 activity, and AR-0033's `derive.py` agrees. |
| Verdict | **READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION**. These are builder claims and regression evidence only (Contract v3 O3), not acceptance. |

---

## 0. What changed, in one view

| Area | Files | Change |
|---|---|---|
| Every CIT write sealed (IP-R3-2) | `cit/binding.rs`, `cit/mod.rs` | `binding::seal` seals the sealed-state block **and** T2-seals the whole record, as the last step of every CIT operation (propose, simulate, reject, approve, execute: EXECUTING, COMMITTED and ROLLED_BACK, rollback). The secret-material flag is bound into the block. The post-commit G4 health write re-seals only a record that still verifies. `gov cit list` shows `record_seal` and `origin`. |
| The OS re-seal rule (O-7; IP-R3-1, -3; R3-1) | `cit/binding.rs`, `cit/mod.rs`, `cit/propagation.rs`, `orchestration/handoffs.rs` | `binding::reseal_if_verified(rec, was_verified, entitled, op)` is one rule for every OS write into an existing record. A record whose seal verified before the write is re-sealed when the operation may establish what it wrote. Otherwise the record stays unsealed and the path is in a touched list. A hand edit is never re-sealed. The rule is applied by CIT manifest ops, the rollback's REJECTED decision (R3-1), propagation markers (IP-R3-1/-3) and handoff return. |
| Direct propagation as a sealed system transaction (IP-R3-3) | `cit/mod.rs::propagate_as_transaction`, `cit/propagation.rs`, `orchestration/handoffs.rs` | A change propagated outside CIT-E (`gov cit propagate`, or the handoff's re-delivery of a stale packet) is recorded as a sealed `COMMITTED` CIT with `origin: system` and `trigger: propagation`. It has no manifest. Its snapshot, touched list and per-path writes are exactly what the propagation marked. |
| Continuity records sealed | `checkpoints.rs`, `orchestration/handoffs.rs` | Checkpoint and handoff records are T2-sealed at creation. This is best effort for checkpoints, which are never refused. A tampered checkpoint or closing report is not taken as a staleness baseline. |
| Content-bound CIT coverage (IP-R3-6) | `cit/binding.rs` | `writes_by_path(store, include)` and `covers(map, path, sha)` form the API task close uses to accept a path only for the content an honoured committed CIT wrote. |
| Producer rule in the manifest (IP-R3-4) | `context/manifest.rs` | An inherited-only, unsatisfied input is not mandatory for a task that produces its feature's specification. It is flagged with the advisory `INHERITED_INPUT_UNSATISFIED`. |
| Non-governed evidence flagged (IP-WS10-10) | `context/manifest.rs` | A research or experiment input that is not governed evidence carries `authority_flag: EVIDENCE_NOT_GOVERNED` and a non-blocking problem. |
| Untraceable implementation (IP-R3-5) | `context/receipt.rs` | The finding is judged on production source that was produced, not on the task's class alone. The closed-task report follows the same rule. |
| Stale links (R3-2) | `graph/lineage.rs` | A finished CIT's links (COMMITTED, ROLLED_BACK, REJECTED) are history, not stale links. |
| Relation edges (R3-3, IP-WS10-08) | `records.rs` (relation region), `lib.rs` (`INDEX_VERSION` → `4.1.5-idx5`) | New edges: `evidence_refs → DERIVED_FROM`, `data_requirements → CONSUMES`, `test_data → CONSUMES`, `realises → IMPLEMENTS`. |
| Product release record type (IP-R2-WS08-7) | `records.rs` (`TYPE_DIR`/`TYPE_PREFIX`), `record.schema.json` | `release` → `spec/releases/REL-*`. The schema rule requires `version`, `derived_from` and `validated_by`. |
| CIT-E relationship integrity (IP-R2-2) | `cit/mod.rs` | `memory::integrity::check` runs before and after the manifest. A reversed, ill-typed or stale relationship the transaction itself introduced, or a new supersession cycle, rolls it back. Consequences for other records are reported. |
| Experiment promotion at CIT (IP-WS10-09) | `cit/mod.rs::promotion_check` | `lifecycle::experiment::promotion_refusal` is checked at approve and again at execute (`EXPERIMENT_NOT_PROMOTED`). |
| Retrieval-profile materiality (IP-R2-6) | `cit/materiality.rs` | A retrieval-profile decision (by tag or by its `retrieval_profile` pin) is a governance change. An overlay change to `MEMORY_POLICY.embedding.*` / `reranker.*` pins is named. |
| Rollback snapshots in the OS store (IP-R2-10) | `cit/mod.rs` | Snapshots live at `paths::store_path(root, "cit-snapshots")` (`.governance-state/cit/<id>`). The legacy tree is relocated once, and a conflict is resolved per transaction. |
| Availability rule at host sites | `orchestration/handoffs.rs` | The handoff G0 guard is asked for what the handoff relies on: the task record and the delivered inputs. |
| Observability | `graph/identity.rs` | `gov artefact show <id>` reports the record's `t2_binding` (which gov operation wrote it as it stands). |
| Schemas and policy | `cit.schema.json` 1.1.0, `record.schema.json` 1.1.0, `CHANGE_POLICY.yaml` (comments only) | These document `origin`/`system`/`os_state`/`os_binding`, the release rule, and the propagation, verification and snapshot behaviour. |

Files outside the WS-4 set: `tests/certification/main.rs` gains one line (`mod ws04r3;`), the additive registration every builder makes. `tests/certification/ws04r3.rs` is new. Nothing else changed outside `runtime/src/{cit/**, context/**, graph/**, checkpoints.rs, orchestration/handoffs.rs, records.rs (relation region, TYPE_DIR/TYPE_PREFIX), lib.rs (INDEX_VERSION)}`, `framework/policies/CHANGE_POLICY.yaml` and the cit/record schemas (`evidence/identity-and-scope.out`, `evidence/regression/rustfmt-warnings-diffstat.out`).

---

## 1. Integration O-7, WS-5 IP-R3-1/-2/-3, WS-2 R3-1 — every OS write into a sealed record

**Requirement.** Integration report §4.1/§8 O-7 and handoff P2-HO-0034; D-0007 T2 and rule 2; Contract v3:365, :427, :675
(BC-P2-09); BC-P2-04 (propagation). The requirement has three parts:
- Every OS write path to a sealed record type must either re-seal a previously verified record or record the path in the CIT's touched list.
- A hand edit must still break the seal.
- The CIT entry in `t2::SEALED_RECORD_TYPES` is coordinated with WS-3 by recording the integration point once all CIT writes are sealed.

### 1.1 The rule, stated once (`cit::binding`)

`bcf0139` made propagation re-seal a record only when its seal verified before the write. That rule is now general:

- `verified_before(rec)` is called before a write, and `reseal_if_verified(rec, was_verified, entitled, op)` after it.
- A record whose seal did not verify (unsealed, edited by hand, foreign) is written but **never sealed**.
- `entitled` says whether the writing operation may establish what it wrote:
  - Bookkeeping markers (staleness, retest and revalidation) are entitled on every record type.
  - A record's own lifecycle operation is entitled: rollback marking its approval decision REJECTED, handoff return, the CIT operations themselves.
  - A **governed content rewrite** (a CIT manifest op) is entitled only outside facts that only their own operation establishes (`content_write_entitled`):
    - never on `human-gate`, `cit`, `report`, `research`, `experiment`, `data` or `audit` records (`OPERATION_OWNED_TYPES`);
    - never on a decision's derivation (`chosen_option`, `human_approved`, `derived_from`, `approved_by*`, `cit`, digests, `approval`, `retrieval_profile`); this prevents a governed change from laundering an approval;
    - never on a task's lifecycle fields (`task_status`, `closed_by_report`, `outputs_produced`, `status_source`, `provenance`, …).

  Such a write is recorded in the touched list and left unsealed. It is reported in `execution.propagation.t2_seals.left_unsealed`.

### 1.2 Every CIT write is sealed (IP-R3-2)

`binding::seal` seals the whole record (`t2::seal_record`) right after the sealed-state block, as the last step before `save_record`. Every CIT operation calls it: propose, simulate, reject, approve, execute (EXECUTING, COMMITTED, ROLLED_BACK), rollback and the system propagation transaction.

A CIT operation seals only after it has verified or re-derived what the record asserts. These are the block's content, impact, approval and writes digests, and the gate, decision and approval against it. So:
- a hand edit of a bound field is refused (`APPROVAL_STALE`, `GATE_MISMATCH`, `T2_UNBOUND`) before any seal;
- a COMMITTED record is never re-sealed by a CIT operation except by rolling it back (fail-safe);
- the post-commit G4 health write re-seals only a record that still verifies.

The secret-material flag is now part of the sealed block (`CitState.secret_flagged`, present only when set, so older blocks' digests are unchanged). Removing `secret_flagged` from the record by hand used to release the transaction. On the base, execution then wrote the secret-flagged content (observation A6: base FAIL, this branch PASS).

### 1.3 Enumeration: every OS write path into a sealed record type

"Sealed" means a type the OS seals, or a record that carries a seal. Paths in other workstreams' files are listed with their integration point.

| # | Writer | Record(s) written | Behaviour now | Owner |
|---|---|---|---|---|
| 1 | `cit::propose/simulate/reject_sealed/approve/execute/rollback` | the CIT record | whole-record seal + sealed block, every operation | WS-4, done |
| 2 | `cit::execute` post-commit (G4 `health`) | the CIT record | re-sealed only if it still verifies | WS-4, done |
| 3 | `cit::approve` (automatic path) | a new decision | sealed (`cit approve (auto)`), as before | WS-4 |
| 4 | `cit::rollback` | the approval decision marked REJECTED | re-sealed if it verified before (`cit rollback`); R3-1 | WS-4, done |
| 5 | `cit::apply_op` `set_status` / `set_field` / `mark_stale` | any record | re-sealed if it verified before **and** the write is entitled (§1.1); otherwise left unsealed; the path is always in `touched` | WS-4, done |
| 6 | `cit::apply_op` `write_file` | a record rewritten wholesale | re-sealed if the record at that path verified before and both its old and new type allow a whole rewrite; `touched` | WS-4, done |
| 7 | `cit::apply_op` `move_file` / `delete_file` | a moved record keeps its content and seal; a deleted one is gone | `touched` | WS-4 |
| 8 | `cit::apply_op` `append_record` | a new record | any `os_binding` / `os_state` carried in the manifest is stripped (no replay of sealed state); `touched` | WS-4, done |
| 9 | `cit::propagation::save_set` (CIT-E) | tasks, close reports, test obligations, scenarios, checkpoints, handoffs | re-sealed if verified before; `touched` of the executing CIT | WS-4, done (`bcf0139` kept) |
| 10 | `cit::propagation::save_set` (direct: `gov cit propagate`, handoff re-delivery) | as 9 | re-sealed if verified before; `touched` and per-path `writes` of a **sealed system transaction** (§1.4) | WS-4, done |
| 11 | `cit::propagation::acknowledge_on_redelivery` | the task record | re-sealed if verified before (tasks are not yet a sealed kind; re-sealed once WS-5 seals them) | WS-4, done |
| 12 | `checkpoints::create` | a new checkpoint | sealed (`checkpoint create`), best effort | WS-4, done |
| 13 | `handoffs::create` / `return_result` | a new handoff / the handoff | sealed / re-sealed if verified before (`handoff return`); a non-handoff id is now refused | WS-4, done |
| 14 | `gates::answer` | the CIT record (decision id; declined → REJECTED) | **not re-sealed** → the whole-record seal breaks until WS-3 applies **IP-R3-WS04-01** | **WS-3 (integration-critical)** |
| 15 | `gates::revoke` | the CIT record (APPROVED → SIMULATED, approval removed) | as 14 | **WS-3 (IP-R3-WS04-01)** |
| 16 | `gates::answer` / `revoke` | decisions | sealed / re-sealed (existing) | WS-3 |
| 17 | `gates::block_tasks` / `move_tasks` | task records | WS-5 IP-R3-1, gates side (routed to WS-3 in P2-HO-0033) | WS-3 |
| 18 | `tasks::{create, set_status, claim, release, close}`, `dag::replan`, `readiness::plan` | tasks; close report (sealed) | WS-5's task-sealing plan (IP-R3-1) | WS-5 |
| 19 | `verification::lineage::remediate` | generated investigation tasks (`save_record`) | once tasks are a sealed kind, they must be sealed by this writer or created through `tasks::create` (IP-R3-WS04-05) | WS-2 / WS-5 |
| 20 | `recovery::recover` | a new `report` record, unsealed | WS-5's close classifies an unsealed `report` as a T2 violation: seal it (`t2::seal_record(&mut rec, "recover")`), or WS-5 excludes non-close reports (IP-R3-WS04-04) | WS-8 / WS-5 |
| 21 | `lifecycle::record_influence`, `lifecycle::validate_seal_save`, `memory::{benchmark, profile}`, `verification::{mod, product}`, `adopt` baseline | research, experiment, data, decisions, audits, adoption | sealed at write or re-sealed if verified before (existing) | WS-10 / WS-6 / WS-2 / WS-9 |
| 22 | `upstream::submit` (lessons), `memory::failures` (failure records), `migrations::*`, `init` (project) | kinds nobody seals | n/a | — |

### 1.4 Direct propagation recorded as a sealed system transaction (IP-R3-3)

`bcf0139` covered CIT-E propagation's reports. A change detected outside change control has no CIT, and propagation still writes into:
- **authored test obligations**: never sealed, with authorship recorded by content hash;
- **scenarios**;
- **legacy or unsealed reports**, which WS-5 classifies as T2 violations.

Without a touched list, a task claimed before the propagation found those marks in its claim window and was refused. `cit::propagate_as_transaction` fixes this:
1. It writes an EXECUTING CIT (`origin: system`, `trigger: propagation`, no manifest) with a rollback snapshot of the plan's paths, sealed.
2. It applies the propagation.
3. It records `execution.propagation.touched` and the content-bound `execution.writes`, and commits with the writes digest sealed.

The system transaction also carries:
- an `approval` naming its basis, `CHANGE_POLICY.propagation`, with no gate, because bookkeeping changes no authoritative content; WS-2's `change_control_integrity` therefore finds a recorded approval;
- an impact block with radius R0.

When a run writes nothing, no record is kept. A failure restores the snapshot and records ROLLED_BACK. `gov cit propagate` and the handoff's targeted propagation both use it.

The consumers need no change: WS-5's `cit_window_paths` and `AuthorshipIndex` already honour a COMMITTED, sealed CIT's touched list. Observation B3 (base FAIL `MUTATION_SCOPE_VIOLATION` → this branch PASS) and the certification test `direct_propagation_is_a_sealed_system_transaction_that_covers_its_marks` show a task claimed before a direct propagation closing with its own work only.

### 1.5 Hand edits still break the seal

The following are shown by `every_cit_write_is_sealed_and_a_hand_edit_stays_broken`:
- A decision edited by hand before a rollback is marked REJECTED but stays BROKEN (`approval_decision.resealed: false`).
- A committed CIT whose touched list was edited stays BROKEN through `gov cit propagate` and an index rebuild.
- A governed rewrite of how a decision was derived is left BROKEN, recorded in `t2_seals.left_unsealed` and in `touched` (`a_governed_change_reseals_only_what_the_os_may_seal`).
- The checkpoint baseline: a checkpoint or closing report whose seal is Broken is no longer taken as what the work consumed (`propagation::baseline_of`).

### 1.6 The CIT entry in `t2::SEALED_RECORD_TYPES`, and IP-R3-WS04-01

Every CIT write in WS-4's files is sealed. Two gate operations in WS-3's file also write CIT records:
- `gates::answer` records the decision id, and marks a declined CIT REJECTED;
- `gates::revoke` returns the CIT to SIMULATED and removes its approval.

They save without re-sealing, so those writes break the whole-record seal. Until the gate writers re-seal, the following happens (measured):
- **The interim regression, measured.** A CIT declined inside another task's claim window leaves a BROKEN OS-managed path. That task's close is then refused `MUTATION_SCOPE_VIOLATION` ("OS-written state changed outside a gov operation: spec/decisions/CIT-0001.yaml"). Evidence: the ignored test `ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close`, run with `--ignored` at `ff529e9`.
- **The consequence is confined.** A CIT answered A and then approved is re-sealed by `approve`, so the regression covers declines, revocations and answered-but-not-yet-approved CITs, observed by a concurrent close.

**IP-R3-WS04-01 (WS-3, integration-critical).** In `gates::answer` and `gates::revoke`, before modifying the CIT record, take `let was_verified = crate::cit::binding::verified_before(c);`. Before `save_record`, call `crate::cit::binding::reseal_if_verified(c, was_verified, true, "gate answer" | "gate revoke")?;`. The exact 6-line patch is `evidence/IP-R3-WS04-01.gates-reseal.patch`. After that, WS-3 adds `"cit"` to `t2::SEALED_RECORD_TYPES`, which is their item in P2-HO-0033.

The order matters. `cit` must **not** enter `SEALED_RECORD_TYPES` without the re-seal. If it did, every declined or revoked CIT would also become a `t2::audit` tampering finding.

**End state measured** (`evidence/observe/endstate-ff529e9.out`, `probes/run-endstate.sh`). This branch plus the patch plus `"cit"` in `SEALED_RECORD_TYPES`, in a private scratch clone:
- `cargo test --lib` 215/0;
- `cargo test --test certification -- --include-ignored` **145/0**, which includes the IP-R3-WS04-01 test.

With the patch alone, the ignored test passes and the observational probe is 22/22 (`evidence/observe/after-ff529e9-with-IP-R3-WS04-01.out`).

### 1.7 Tests and probes

- Certification (`ws04r3`): `every_cit_write_is_sealed_and_a_hand_edit_stays_broken`, `a_governed_change_reseals_only_what_the_os_may_seal`, `direct_propagation_is_a_sealed_system_transaction_that_covers_its_marks`, and the ignored `a_cit_declined_during_another_tasks_claim_does_not_block_its_close`.
- Lib (`cit::binding`): `the_os_reseals_only_what_it_verified_and_is_entitled_to_write`, `a_secret_flag_is_bound_into_the_block_only_when_set`.
- Observational probe (§14), base → this branch: A1, A2 (CIT record sealed), A4 (rollback decision not reported as tampering by `os_binding_integrity`, WS-2's R3-1 symptom), A5 (automatic decision re-sealed), A6 (secret flag), B1 (direct propagation recorded), B3 (concurrent close) and C11 (checkpoint sealed) go **FAIL → PASS**. The controls A3 and B2 are PASS on both.

---

## 2. WS-5 IP-R3-6 — CIT coverage by content hash (API complete)

**Requirement.** Contract v3:614 (BC-P2-14): a mutation outside the task's scope is accepted only when "a CIT governing that specific change" covers it, so coverage must bind content, not a path.

**Change.** `binding::writes_by_path(store, include)` maps each path to the committed CIT writes that cover it. It honours only CITs whose whole-record seal verifies and whose `verified_writes` holds (sealed COMMITTED state with an intact writes digest). `binding::covers(map, path, current_sha)` returns the covering CIT only when the path's current content is what the CIT wrote.

Every CIT-E and every system propagation transaction records content-bound `execution.writes`. The claim-window filter (`include`) remains WS-5's: `cits_committed` at the baseline.

**Tests.** Lib `coverage_is_bound_to_the_content_a_committed_cit_wrote`. The certification direct-propagation test checks that each recorded hash equals the file's content.

**Wiring.** This is WS-5's routed R2-4 (P2-HO-0035 "BC-P2-13 hook"): `tasks::observe_against` and `AuthorshipIndex` can replace path-only coverage with `covers(...)`. That is IP-R3-WS04-02.

## 3. WS-5 IP-R3-4 — the producer rule in `manifest::resolve`

**Requirement.** WS-5 r2 §1.4: packets, `gov context manifest|receipt`, the DAG and close must agree that a specification-producing task is not blocked by the inputs it only inherits from its feature.

**Change.** `apply_producer_rule` runs in `resolve_with` and again, after contradictions, in `resolve`. It applies to a task that `dag::produces_feature_specification` (a readiness gap task, or a specification-producing class). Each required input with these properties becomes non-required:
- every declaration of it is the feature's own list;
- it is not satisfied (absent, superseded, conflicting, …).

Its blocking problems become advisory, and `INHERITED_INPUT_UNSATISFIED` is added. What the task declares itself still binds. The feature's implementation work stays blocked.

**Effect.** The manifest is COMPLETE for the producer. WS-5's DAG filter, `tasks::require_receipt` filter and `continue`'s producer dispatch become no-ops (IP-R3-WS04-03: optional clean-up).

**Tests.** Lib `a_specification_producer_is_not_held_to_what_its_feature_still_lacks`; certification `the_manifest_applies_the_producer_rule_and_flags_ungoverned_evidence`; observation C3 FAIL → PASS. WS-5's supplementary probe, including E6 (the producer deadlock), is **37/37** on both binaries.

## 4. WS-5 IP-R3-5 — UNTRACEABLE_IMPLEMENTATION only when implementation was produced

**Requirement.** Contract v3:1125 (W5): "untraceable implementation is reported". It is judged on the implementation that was produced.

**Change** (`receipt::validate`):
- "Implementation produced" means production source among the receipt's outputs (`outputs_produced`/`files_changed`, plus `observed_files_changed` when a close persisted it).
- `UNTRACEABLE_IMPLEMENTATION` applies only to produced implementation. A traceability-class task that produced none gets the warning `NO_IMPLEMENTATION_PRODUCED` and must still account for every declared input (`TRACE_INCOMPLETE`).
- `TRACEABILITY_MISSING` likewise requires produced implementation.

`untraceable_closed_tasks` (WS-2's `product_traceability`) follows the same rule when the close recorded outputs. A legacy close with no recorded outputs is still judged by its class, since what it produced cannot be told.

**Tests.** Certification `untraceable_implementation_is_judged_on_what_was_produced`; observation C5 FAIL → PASS.

**Unchanged.** WS-5's `close_requires_and_persists_the_consumption_receipt` still sees `TRACEABILITY_MISSING` for a close that produced `src/lib.rs`. delta-r N1-N2 stops, on both binaries, at a discovery task that wrote `product/a.txt` (source) with no upstream, now reported "produced implementation".

## 5. WS-2 R3-2, R3-3 and WS-10 IP-WS10-08 — lineage edges

- **R3-2** (`graph::lineage::stale_links`). A finished Change-Impact Transaction's links (`FINISHED_CIT_STATES` COMMITTED, ROLLED_BACK, REJECTED) are history, and the detector no longer reports them. This is the same set WS-2's `reporting::current_stale_links` filters, which is now redundant (IP-R3-WS04-06). An open transaction's links still count. Tests: lib `a_finished_transactions_links_are_history_not_stale_links`; observation C8 FAIL → PASS.
- **R3-3** (`records.rs`). `evidence_refs → DERIVED_FROM`: gate answers record `evidence_refs`, and retrieval-profile decisions cite their benchmark and regression. Research consumption is therefore a graph fact. Observation C7 FAIL → PASS.
- **IP-WS10-08** (`records.rs`). `data_requirements → CONSUMES` (scenario → data requirement), `test_data → CONSUMES` (test obligation → test data), `realises → IMPLEMENTS` (test dataset → data requirement). WS-6's endpoint signatures accept all three.
- **`INDEX_VERSION`** is now `4.1.5-idx5`, because edge derivation changed and a full rebuild is forced.
- **Evidence.** Lib `citation_and_scenario_chain_fields_are_relation_edges`; observation C6 FAIL → PASS. gamma-r H4 (normalised diff `evidence/audit-probes/NORMDIFF-gamma-r.H4.out`): `SCN-0001 -> DATA-0001` went from **NOT an edge → TRACED via CONSUMES**. The fixture's DATA→TD and TD→TST links do not exist in its records (WS-10 §3.4), so they remain not traced.

## 6. WS-10 IP-WS10-09 — experimental output at the CIT that would carry it

**Requirement.** Contract v3:607-614 (J2): experimental output cannot enter the production tree without a governed promotion.

**Change.** `cit::promotion_check` calls `lifecycle::experiment::promotion_refusal` at **approve** and again at **execute**, so a promotion revoked after approval stops execution. A transaction is refused `EXPERIMENT_NOT_PROMOTED` in any of these cases, unless an approved, still-honoured promotion covers each path:
- it names an experiment;
- it moves a file out of an experiment's outputs;
- it writes bytes equal to an experimental output into production.

**Tests.** Certification `experimental_output_reaches_production_only_through_a_promotion`, which also shows other bytes to production are still approvable. Observation D2 is FAIL → PASS: on the base, the copy was approved and executed. WS-10's supplementary probe is **35/35** on both binaries.

## 7. WS-10 IP-WS10-10 — non-governed evidence in the manifest

`flag_ungoverned_evidence` runs in `manifest::resolve`. A delivered research or experiment input whose `lifecycle::evidence_status` is not citable carries:
- `authority_flag: EVIDENCE_NOT_GOVERNED` (when no other flag is set);
- a non-blocking `EVIDENCE_NOT_GOVERNED` problem naming its standing and reasons.

Both reach the packet (`evidence_inputs[*]`) and `gov context manifest`. The flag is advisory, as the IP specifies. Blocking stays with the manifest's own rules (lifecycle state, authority class).

Test: certification `the_manifest_applies_the_producer_rule_and_flags_ungoverned_evidence`. Observation C4 FAIL → PASS.

## 8. WS-6 IP-R2-2 — CIT-E relationship integrity

**Requirement.** BC-P2-28, WS-6 r2: a CIT must not introduce reversed, stale or ill-typed edges.

**Change.** CIT-E runs `memory::integrity::check` (record-level; dangling edges stay with the existing index-based check) before the manifest and again during verification. It classifies the **new** non-low findings:
- **introduced**, which fails the verification and rolls back:
  - a `reversed` or `ill_typed` relationship declared by a record the manifest's **content ops** wrote (its `mark_stale`/`delete_file` ops are excluded);
  - a `stale` relationship declared by such a record to a target the transaction did **not** itself change;
  - a new `supersession_cycle`.
- **consequences**, which are reported in `execution.propagation.relationship_integrity`: every other new finding. An example is current work still naming a requirement this transaction superseded; propagation marks that work for retest.

Superseding a record that other work names therefore still commits. `CHANGE_POLICY.yaml` documents the check (comment only; `verification_required` unchanged).

**Tests.** Certification `cit_e_rolls_back_relationships_it_introduces_but_not_their_consequences`; observation D1 FAIL → PASS. On the base, the reversed relationship committed.

**Regression.** The K2 valid-fixture derived probe is 26/26 and the K2 unedited probe 11/26 on both binaries. The unedited run stops at the fixture's schema-invalid feature (`readiness`), as WS-4 round 2 recorded. The ws04r2 scenario probe is 40/40 on both.

## 9. WS-6 IP-R2-6 — a retrieval-profile change is material for CIT-P

A decision that pins a retrieval profile is a **governance change** (R5 floor, human gate), whatever its label. It is recognised by its `retrieval-profile` / `embedder` / `reranker` tag, or by its `retrieval_profile` field. Previously such a decision derived only `behaviour_change`.

A policy-overlay change that alters `MEMORY_POLICY.embedding.*` / `reranker.*` pins adds a separate finding, "retrieval profile pins", naming the keys. So the simulation and the gate say that every semantic answer and context packet changes. For a `MEMORY_POLICY` file, the finding covers its `embedding`/`reranker` blocks.

The WS-6 option of letting `memory select` open a CIT is theirs and optional.

Tests: lib `a_retrieval_profile_change_is_material_for_cit_p`; observation C9 FAIL → PASS.

## 10. WS-6 IP-R2-10 — CIT snapshots to the BC-P2-31 store

`snapshot_base` resolves `paths::store_path(root, "cit-snapshots")`, which is `.governance-state/cit`, a directory that ignores itself in Git and is never walked or indexed. `snapshot_dir`, `take_snapshot`, `register_created`, `restore_snapshot`, `prune_snapshots` and `interrupted` all use it.

The legacy `.governance-runtime/cit` tree is relocated with `paths::relocate_legacy`. If both locations hold snapshots, each transaction's snapshot is moved unless one already exists at the store, and nothing is overwritten.

`take_snapshot` keeps the text the R1 held-out AR-0033 `hv_a` exemption inspects: `let dir = snapshot_dir(p, id);` and `let snap = dir.join("snapshot");`. Every write still targets the snapshot directory, and the exemption check passes.

Tests: certification `rollback_snapshots_survive_deleting_the_derived_runtime_directory` (legacy tree relocated; `git status` clean; `gov cit rollback` works after `.governance-runtime/` is deleted). Observations C1, C2 FAIL → PASS; on the base, rollback gave `SNAPSHOT_MISSING`.

## 11. WS-8 IP-R2-WS08-7 — product-release record type (WS-4 side)

- `TYPE_DIR` `release → spec/releases` and `TYPE_PREFIX` `REL` give canonical location, identity and misplacement reporting.
- The relation fields are `derived_from` (tasks, close reports) and `validated_by` (audits, evidence), both existing relation fields.
- `record.schema.json` 1.1.0 adds a rule that applies to `type: release` only: `version`, a non-empty `derived_from` and a non-empty `validated_by` are required. A release is validated by the record schema, as no `release.schema.json` exists, and a Governance OS kernel release (`release.rs`) is a different thing.

Tests: lib `a_product_release_is_a_governed_record_in_the_lineage`; observation C10 FAIL → PASS.

**Pending.** The creating command is WS-3's (`gov release record`, classified Write in `COMMAND_GUARDS`) and the writer WS-8's (`release::record` through `control::guard_write` + `records::save_record`); IP-R3-WS04-07. zeta-r `W8-l1-forward-reaches:release` needs that command, so it is FAIL on both binaries.

## 12. The availability rule at WS-4's host sites

The P2-HO-0031 rule has four parts: a hard-block refuses only the operations whose reliance it protects, scoped; remedies and independent work stay available; a remedy that does not clear its block does not commit; refusals are typed and name the block and its scope. At WS-4's host sites:

- **`handoffs::create`** used to ask the G0 guard with no paths. A path-scoped block could therefore never refuse a handoff, while a global block always did. It now asks for exactly what the receiving worker relies on: the task record and every input the manifest delivers.
- **CIT propose/approve/execute** already pass the transaction's manifest paths and targets (`guard_paths`). CIT-E keeps its repair mode: a transaction executes under a block only if it repairs it, is rolled back otherwise, and the block state is re-established.
- **Remedies stay available.** `checkpoint create` and `session close` are never refused for health. `gov cit propagate`, the staleness remedy, has no health guard.
- **Refusals are typed.** `scheduler::guard` returns `HEALTH_HARD_BLOCK` with the blocks and the paths asked.

Whether a critical block may refuse *proposing* a repairing CIT (BC-P2-06 requires CIT propose to be refused in a hard-block state) is WS-2's catalogue decision (P2-HO-0032). The host passes the paths that decision needs. No refusal a repair-delta class requires was re-opened.

---

## 13. Tests added and changed

- **Lib (+8):**
  - `cit::binding::{the_os_reseals_only_what_it_verified_and_is_entitled_to_write, a_secret_flag_is_bound_into_the_block_only_when_set, coverage_is_bound_to_the_content_a_committed_cit_wrote}`
  - `graph::lineage::a_finished_transactions_links_are_history_not_stale_links`
  - `graph::identity::{a_product_release_is_a_governed_record_in_the_lineage, citation_and_scenario_chain_fields_are_relation_edges}`
  - `context::manifest::a_specification_producer_is_not_held_to_what_its_feature_still_lacks`
  - `cit::materiality::a_retrieval_profile_change_is_material_for_cit_p`
- **Certification (+8, and 1 ignored):** `tests/certification/ws04r3.rs`, §1-§11. The ignored test documents IP-R3-WS04-01 and passes once the patch is applied (§1.6).
- **No existing test was changed.**

## 14. Probes

### 14.1 Observational supplementary probe (the negative control)

`evidence/probes/ws04r3_observe.rs` is not product code. `run-observe.sh` compiles it into a scratch copy of each tree's certification harness, which supplies provisioning, signed installs and the owner-signed channel. It is run against that tree's own binary. It never asserts; each line is `OBSERVE <id> PASS|FAIL`.

| Run | Result |
|---|---|
| base `53897c1` | **2 PASS / 20 FAIL**. The PASS lines are the controls A3 (decision REJECTED) and B2 (a sealed report re-sealed by propagation, `bcf0139`). |
| this branch `ff529e9` | **22 PASS / 0 FAIL** |
| this branch + IP-R3-WS04-01 | 22 / 0, and the ignored test passes |

`bda16a2` differs from `ff529e9` only in `CHANGE_POLICY.yaml` comments.

### 14.2 Audit-of-record probes, unedited, base vs this branch

The runner is `evidence/audit-probes/run-probe.sh`, derived from WS-4 round 2's. Both modes use the round-2 integration's labelled root-channel adapter, unedited. The comparison is in `COMPARE-base-after.out`:

**0 FAIL→PASS and 0 PASS→FAIL across 20 probe outputs.** Every stop point is identical on both binaries.

| Probe | Result, both binaries | Note |
|---|---|---|
| delta-r K2 | 11/26 | stops at the fixture's schema-invalid feature |
| K2 valid-fixture (derived) | 26/26 | |
| delta-r K3 | 18/19 | |
| delta-r L3 | 33/39 | stops at L3.b5.6, WS-3's T2 refusal |
| delta-r N1-N2 | 14/14 | |
| delta-r N3-N4-W9 | 18/18 | |
| delta-r J1-J2 | 8/9 | stops at `memory select`'s R5 gate |
| zeta-r W03 | 20/20 | |
| zeta-r W05 | 13/17 | |
| zeta-r W06 | 18/26 | |
| zeta-r W08 | 22/24 | |
| beta-r C2 | 9/10 | |
| beta-r D6 | — | stops at the fixture's non-independent acceptance test |
| AC16-X1 | 12/15 | |
| AC16-X2 unedited | 1/1 | stops |
| AC16-X2 (WS-5's derived copy) | 6/11 | stops at `verify product` in the fixture |
| ws04r2 scenarios (derived) | 40/40 | |
| WS-5 supplementary | 37/37 | |
| WS-10 supplementary | 35/35 | |

The one observation-only change is gamma-r H4's `SCN→DATA` edge (§5). The round-3 behaviours are mostly outside these probes' fixtures, so the observational probe (§14.1) is the discriminating evidence. It is regression and builder evidence only.

### 14.3 What the probes do not reach (stated)

- **The W06 `(direct)` lines** observe `task claim/close/show` after a direct edit. That is WS-5's wiring of `task_staleness` and `require_current_inputs` (R2-1/-2).
- **The W8 release line** needs the command (§11).
- **D6's snapshot part** is not reached. The certification test and observations C1-C2 cover it.

## 15. Regression and R1

| Suite | Result | Evidence |
|---|---|---|
| `cargo test --lib` at `bda16a2` | **215 passed, 0 failed** (base 207) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` at `bda16a2` | **144 passed, 0 failed, 1 ignored** (base 136) | `evidence/regression/cargo-test-certification.out` |
| rustfmt on changed files; build and test-build warnings | clean; 0 and 0 | `evidence/regression/rustfmt-warnings-diffstat.out` |
| end state (IP-R3-WS04-01 + `cit` sealed), scratch clone | lib 215/0; certification 145/0 with `--include-ignored` | `evidence/observe/endstate-ff529e9.out` |

**R1 held-out suites, unedited, through a private path** (`evidence/r1-heldout/`):
- **Runner.** `run-r1-heldout.sh` is the round-2 integration's runner with only the run id, the scratch root (`…/p2ar0035/r1-P2-AR-0035-private`), `CARGO_BUILD_JOBS=2` and phase-splitting changed. Its `wt/srr1-r1-verify{,-2,-3,-4}` links point at this worktree. Every copied file is `cmp`-identical.
- **Measured.** HEAD `bda16a2`, with 0 product files differing.

| Suite | Recorded baseline | This tree |
|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | **26 / 2**, same; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests |
| AR-0033 | 31 / 0 (30 / 1 on any larger tree) | **30 / 1**: `hv_a_derivation::a1` only (84 / 740 pin) |

- **Census** (AR-0033's walk of this tree): **118 files / 2014 functions**.
- **Unpinned copy.** The labelled copy `hv_a_derivation.a1-unpinned.P2-AR-0035.rs.txt` differs only in the two size assertions. It finds **0 violations** in every §6 activity:

  | Activity | Derived | Writers | Exempt |
  |---|---|---|---|
  | human_gate_create | 49 | 44 | 1 |
  | human_gate_approve | 1 | 1 | — |
  | release_certification | 1 | 1 | — |
  | trust_policy_mutation | 8 | 1 | — |
  | privileged_plugin_acquisition | 9 | 2 | — |
  | floor_lower_or_reset | 3 | 1 | — |
  | present_below_floor_release_as_current | 1 | 1 | — |
- **Independent derivation.** AR-0033's `derive.py` (ROOT line only) agrees under all three splitter configurations.
- **Failure messages.** The normalised failure messages are identical to the round-2 integration's: 42 lines, empty diff (`failure-messages-vs-round-2-integration.txt`).
- **R1-listed files.** `records.rs` is the only R1-listed file touched. The change is confined to relation fields and `TYPE_DIR`/`TYPE_PREFIX`; `save_record` is unchanged. The texts R1 suites inspect are kept: `cit::apply_op` (2 `guarded_record_effect(`, 2 `guard_effect(effect,`, `save_record(&p.root, r)`) and `cit::take_snapshot`. No new `guard_write` label was added.

## 16. Integration points (new, for integration and round 4)

| ID | Owner · file | Change | Why |
|---|---|---|---|
| **IP-R3-WS04-01** (integration-critical) | WS-3 · `orchestration/gates.rs` `answer`, `revoke` | Re-seal the CIT record they write when it verified before: `evidence/IP-R3-WS04-01.gates-reseal.patch` (6 lines). **Then** add `"cit"` to `t2::SEALED_RECORD_TYPES` (P2-HO-0033), never before. Un-ignore `ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close`. | Every CIT write is then sealed (IP-R3-2), and a declined or revoked CIT no longer blocks a concurrent close. End state measured: lib 215/0, certification 145/0 |
| IP-R3-WS04-02 | WS-5 · `tasks::observe_against`, `AuthorshipIndex` | Accept an out-of-scope path, and keep authorship over a CIT's write, only when `cit::binding::covers(&writes_by_path(store, in_window), path, current_sha)` names a covering CIT | IP-R3-6: coverage bound to content (BC-P2-14). WS-5's routed R2-4 |
| IP-R3-WS04-03 | WS-5 · `dag::evaluate` step 3, `tasks::require_receipt`, `status::continue_work` | Optional: remove the producer-rule filters; `manifest::resolve` applies the rule | IP-R3-4 done in the manifest. Keep `dag::produces_feature_specification` public and stable (the manifest reads it) |
| IP-R3-WS04-04 | WS-8 · `recovery::recover` (or WS-5 · `tasks::sealed_kind`) | Seal the recovery `report` (`t2::seal_record(&mut rec, "recover")`), or exclude non-close reports from WS-5's must-be-sealed kinds | An unsealed `report` written in a claim window is otherwise a T2 violation at that close (O-7 enumeration, row 20) |
| IP-R3-WS04-05 | WS-2 · `verification::lineage::remediate` (+ WS-5) | Once task records are a sealed kind, create generated investigation tasks through `tasks::create` or seal them | O-7 enumeration, row 19 |
| IP-R3-WS04-06 | WS-2 · `verification/reporting.rs` | `current_stale_links` is now redundant (optional removal). `change_control_integrity` may report `origin: system` propagation transactions separately; they carry a policy approval and no gate | R3-2; §1.4 |
| IP-R3-WS04-07 | WS-3 (`cli/src/main.rs`, `COMMAND_GUARDS`) + WS-8 (`release.rs`) | `gov release record --version --derived-from --validated-by` → `release::record` → `records::save_record` of a `release` record under `spec/releases/` | IP-R2-WS08-7; zeta-r W8-l1 release line |
| IP-R3-WS04-08 | WS-8 · `framework/KERNEL.yaml` `schema_versions` | `record: 1.1.0`, `cit: 1.1.0` | Schema versions bumped here |
| IP-R3-WS04-09 | WS-3 · `docs/**` | Document: system propagation transactions; `record_seal` in `cit list`; `t2_binding` in `artefact show`; `EXPERIMENT_NOT_PROMOTED` at CIT approve/execute; `NO_IMPLEMENTATION_PRODUCED`, `INHERITED_INPUT_UNSATISFIED`, `EVIDENCE_NOT_GOVERNED`; relationship-integrity verification at CIT-E; the snapshot location; the OS re-seal rule | Operator documentation |
| IP-R3-WS04-10 | WS-1 · `tests/governance/capability-evidence-map.yaml` | Owners: BC-P2-09/BC-P2-04 O-7 → `cit::binding` tests, `ws04r3::{every_cit_write…, a_governed_change…, direct_propagation…}`. BC-P2-14 → `coverage_is_bound…`. BC-P2-20 W5 → `untraceable_implementation…`. BC-P2-21/46 edges → `citation_and_scenario_chain…`, `a_product_release…`. BC-P2-28 → `cit_e_rolls_back…`, `a_finished_transactions…`. BC-P2-31 → `rollback_snapshots_survive…`. BC-P2-48 → `experimental_output…`. BC-P2-13/30 → `a_retrieval_profile_change…`. BC-P2-17 → `a_specification_producer…`, `the_manifest_applies…` | AC-10 |
| IP-R3-WS04-11 | WS-2 · `scheduler::catalogue` | Decide the block scope and remedy semantics for `cit.propose` / `handoff.create` using the paths hosts now pass (§12) | Availability rule, scheduler side |

Round-2 items not in this handoff are unchanged by this run: WS-4 r2 R2-1..R2-15 and R2-10/-11 (WS-6).

## 17. Owner-decision questions

None. Each change stays inside ARCH-0001/ARCH-0003 and D-0007: the T2 primitive, re-sealing only what the OS can vouch for, and system transactions for OS bookkeeping. No trust boundary, external dependency or owner-controlled material is involved.

## 18. Limits and what was not done

- **IP-R3-WS04-01 is not applied here.** It is WS-3's file. Until it lands, the interleaving in §1.6 refuses a concurrent close. That is measured and documented, with a patch and an ignored test for integration.
- **Direct propagation stays operator- or boundary-triggered.** It runs from `gov cit propagate` or handoff re-delivery. Running it automatically at claim, close or rebuild is WS-5/WS-6 wiring (R2-3). Once wired, each run that writes records one system transaction.
- **Checkpoint sealing is best effort.** A checkpoint is never refused. A checkpoint written unsealed says so in its result (`record_binding`). Unsealed legacy checkpoints are still believed as baselines; only Broken ones are not.
- **Relationship-integrity verification judges the relationships a transaction declares.** It does not judge the prose it writes. Its cost is two record-level integrity checks per CIT-E.
- **The retrieval-profile materiality recognises tags, the pin field and overlay keys.** A profile change made any other way is classified by its path (governance) only.
- **The product-release record type is ready; creating releases needs IP-R3-WS04-07.**
- **This is not acceptance.** Every figure above is regression and builder evidence (Contract v3 O3).

## 19. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. I spawned no sub-agents, did not contact the product owner, and read no session or agent transcripts, task-output stores or user auto-memory.
- **One foreground command was moved to the background by the tool.** The WS-5 and WS-10 supplementary probe runs, base then after, together exceeded the tool's 600 s limit. The tool moved the command to the background and notified completion. I did not read the task-output store. The results were read from the evidence files the command itself wrote (`evidence/audit-probes/{base,after}/builder.*.out`). Afterwards I ran long steps one per call.
- **An overlapping run was discarded.** A first attempt at the delta-r L3 probe for both modes in one call, under an outer `timeout`, killed the "after" run mid-way. The later clean re-run is the recorded one. The earlier partial output was overwritten, and I confirmed that no stray process remained.
- **The permission system denied one shell command.** It extracted a base copy for a formatting check and began with `rm -rf` of a scratch directory. It was not retried as written; a fresh uniquely named directory was used instead.
- **Negative-control mechanics.** The observational probe runs inside scratch exports and clones of the named commits. The end-state measurement uses a scratch clone with a local branch created only in that clone. No branch, worktree or reference of the source repository was modified. The two certification tests that rebuild released versions need the history, which is why a clone rather than an export was used for that measurement.
- **Scratch paths.** Outputs contain absolute scratch paths of this run (`…/scratchpad/p2ar0035/…`).

## 20. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `identity-and-scope.out` | product and governed digests (base, each work commit); Contract v3 sha256; protected-path scope check; the R1-listed file touched |
| `regression/` | lib (215/0), certification (144/0, 1 ignored), rustfmt, warnings and diffstat |
| `r1-heldout/` | runner (derived, phase-split), labelled unpinned `hv_a` copy, run at `bda16a2` (suites, census, S1, S2), failure-message comparison |
| `probes/` | `ws04r3_observe.rs` (observational probe), `run-observe.sh`, `run-endstate.sh` |
| `observe/` | base, this branch, this branch + IP-R3-WS04-01 (with the ignored test), end state (lib + certification with `cit` sealed) |
| `IP-R3-WS04-01.gates-reseal.patch` | the gates.rs change offered to WS-3 |
| `audit-probes/` | runner, derived runner, `compare.py`, `COMPARE-base-after.out`, `NORMDIFF-gamma-r.H4.out`, and `base/` and `after/` outputs (+ adapter logs) |
