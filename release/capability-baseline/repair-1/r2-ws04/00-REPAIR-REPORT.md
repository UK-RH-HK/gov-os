# P2-AR-0025 — Repair iteration 1, round 2, WS-4: change control, propagation, Gate-W delivery, continuity

| Field | Value |
|---|---|
| Run | P2-AR-0025, role `capability-repair`, agent model `claude-opus-5[1m]` (Claude Opus 5, 1M context) |
| Handoff | `release/orchestration/phase-2/HANDOFFS/P2-HO-0023-repair-1-r2-ws04.md` (with P2-HO-0020 and P2-HO-0010) |
| Branch / base | `phase2/repair-1-r2-ws04` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree; `product_code_digest b1ab1c8c…fbb1`) |
| Product commits | `172bf36`, `6b68a17`, `e9e4e20`, `2fb66d5`, `c4a16f6`, `cd02bfc` (product tip `cd02bfca3dd59f4e040b737d5569d97d17195aee`, `product_code_digest 65d804d81b844a10b9c79c648cd28cc579cd7a40dbf91085c20e30ef7e50aee1`, `governed_state_digest` unchanged `4981437f…c227d`) |
| Classes | BC-P2-04, BC-P2-05, BC-P2-11 (CIT side), BC-P2-13 (CIT-P side), BC-P2-18 (detection side) |
| Claims | all five **REPAIRED_CLAIMED** for the WS-4 side; host call sites in files other workstreams own are integration points (§4). Builder claims with regression evidence only (Contract v3 O3) — not acceptance. |
| Regression | `cargo test --lib` **160/0** (146 base + 14 new); `cargo test --test certification` **105/0** (100 base + 5 new, `section6` §6 derivation included); rustfmt clean on every touched file |
| R1 held-out | AR-0027 26/3, AR-0029 26/2 (+`ho_f` non-compiling), AR-0031 27/7 — identical to the recorded baselines; AR-0033 30/1 (`hv_a::a1` scale pin only: tree 109 files / 1580 functions vs pinned 84/740); unpinned census 0 violations in every §6 activity; AR-0033's own `derive.py` agrees |
| Probes | 48 audit-of-record probes (all 31 that exercise my classes plus 17 more that drive a CIT) + 3 labelled derived probes, before (base binary) and after (final binary), unedited, through the P2-AR-0022 owner-channel adapter: **88 FAIL→PASS, 4 PASS→FAIL** (all four K4 lines whose premise BC-P2-13 removes, §5.2) |
| Verdict | **READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION** — no owner-decision question |

## 1. What changed, in one paragraph per class

* **BC-P2-11 (CIT side).** A CIT's state is now OS-sealed T2 state (`cit::binding`): the transaction's content digest
  (proposal, trigger, targets, manifest), its simulated-impact digest and a binding digest over both and the CIT id.
  The gate CIT-P raises is a **system gate** (`gates::create_system`) whose `subject.sha256` is that binding digest —
  inside the package the owner signs. Approve and execute re-derive everything and refuse, typed: `APPROVAL_STALE`
  (content or impact changed after the answer), `GATE_MISMATCH` (record names another gate), `T2_UNBOUND` /
  `CIT_STATE_MISMATCH` (hand-written, copied or unsealed CIT state), `GATE_NOT_PRESENTED/NOT_ANSWERED/DECLINED`
  (answer read only through `gates::verified_answer`). A re-simulation that changes the content or impact raises a
  new gate; the stale one can no longer approve.
* **BC-P2-13 (CIT-P side).** `cit::materiality` derives which of the eight Contract v3:640-647 classes a change belongs
  to from **what it touches** (records and fields, paths, file content, declared path targets), never from the label
  alone. The effective triggers are *declared ∪ derived*; `auto_simulate_triggers`, `human_gate_triggers` and the
  radius floor apply to them, so a mislabelled material change is simulated at propose and gated. The same classifier
  answers "is this *performed* change material?" (`classify_paths`, `gov cit classify`) — the in-task detection API
  WS-5 calls at task close in round 3.
* **BC-P2-04.** `cit::propagation` makes an upstream change — through CIT-E **or directly** — reach open and
  **completed** consumers (retest/revalidation, a generated revalidation task), their closing reports and receipts,
  the validation evidence (test obligations, scenarios), checkpoints, handoffs and stored context packets
  (`invalidated`), idempotently, with normative-content hashing so bookkeeping edits never look like upstream
  changes. Direct changes are detected from what each task's work consumed (checkpoint/receipt/packet baselines), not
  from index freshness, and propagated by `gov cit propagate`; the close-side refusal (`require_current_inputs`) is
  exposed for WS-5.
* **BC-P2-05.** A checkpoint records the task's mandatory inputs (ids, versions, content and normative hashes, what
  was delivered), a state reference taken after bringing the index current, what the product observed, and the
  mandatory triggers that occurred since the previous checkpoint. It is **stale** when an input or the governed state
  it captured changed (`gov checkpoint freshness`). Handoffs refuse unsatisfied mandatory inputs and re-deliver a
  stale packet as an explicitly **degraded** handoff (marking the in-progress work for retest); `gov session close`
  is never refused but states its degradation; the watchdog counts commands and changed files itself and turns every
  unobserved trigger into a checkpoint at the next boundary (`observe_boundaries`).
* **BC-P2-18 (detection side).** `context::contradictions` detects contradictions precedence cannot resolve among
  current authoritative records (declared conflicts, supersession forks, decisions answering the same question
  differently), flags every member `CONTRADICTORY` in any manifest that includes one (so the manifest is `BLOCKED`
  and the members are never delivered together as authority), routes each to a system gate (`trigger:
  contradiction`) carrying the OS's own assessment, and honours only the verified answer.

## 2. Per class

### 2.1 BC-P2-11 — approval bound to content, impact and CIT (CIT side)

**Requirement** (repair-delta §2; Contract v3:430, :678): an approval binds the exact transaction content, simulated
impact and CIT it answered, and any later change makes it stale at approve and at execute. The plugin side
(registration gates) is WS-7's.

**Changes.**
* `runtime/src/cit/binding.rs` (new): `STATE_FIELD = "os_state"`; `content_of/content_digest`, `impact_of/impact_digest`,
  `binding_digest`, `approval_digest`, `writes_digest`; `CitState`; `seal` (T2 `t2::seal_value` over the sub-object,
  because `gates::answer/revoke` write the CIT record without re-sealing it — a whole-record seal would break on every
  gate answer), `verified_state` (`T2_UNBOUND`, `CIT_STATE_MISMATCH`), `binding_of`; `PathWrite`, `capture_writes`,
  `verified_writes` (ws05 IP-3, §3).
* `runtime/src/cit/mod.rs`: `propose` strips OS-owned fields from caller input and seals `PROPOSED`; `simulate_inner`
  requires a verified state, computes content/impact/binding digests, reuses the existing gate only when its
  `subject.sha256` equals the binding, otherwise raises a new `create_system` gate (`subject {kind: cit-transaction,
  cit, sha256, content_sha256, impact_sha256, radius, effective_triggers}`), drops a stale `decision` link, refuses to
  re-open a declined transaction; `gate_answer_for`; `approve` (verified state, content and impact digests, sealed gate
  vs record gate, verified answer, decline → `reject_sealed` + `GATE_DECLINED`, auto decisions sealed, approval
  digest sealed); `execute` checks the same before anything is applied and checks the gate before the sealed status
  (a forged status never reaches execution); `rollback` seals `ROLLED_BACK`; `bindings()` for audit; `list` shows the
  verified state.
* `framework/schemas/cit.schema.json` unchanged (open schema; `os_state` is OS-owned and stripped from input).

**Product checks and tier.** G0 at `cit.propose/approve/execute` (`scheduler::guard`), then the binding checks inside
`approve`/`execute` (every execution path). `gov cit show` carries the sealed `os_state`; `gov cit list` shows each CIT's verified state (`binding_of`).

**Probes (before → after).** delta-r L3 `L3.b4.s2` FAIL→PASS (manifest edited after the answer: `APPROVAL_STALE`),
`L3.b4.s3` FAIL→PASS (an R2 answer cannot authorise the R5 re-simulation), `L3.b4.o2` PASS→PASS (re-binding the gate
by hand: `T2_UNBOUND`), `L3.b4.o1` PASS→PASS (`GATE_MISMATCH`). Builder scenario S1 7/7 (base binary 1/7).

**Tests.** lib `digests_are_stable_across_the_record_writer_and_sensitive_to_content` (`cit::binding`); certification
`cit_approval_binds_content_impact_and_transaction`.

**Limits / not done.** `L3.b4.s1` (a gate re-answered **by editing its record** after approval must give
`APPROVAL_STALE` at execute) stays FAIL on the code: the edited gate is refused as `T2_UNBOUND` before the approval
check (execution is refused either way; the answer path through `gov decide` is WS-3's). The plugin half of the class
(gamma-r `F4.b5.x`) is WS-7's and was not run.

### 2.2 BC-P2-13 — materiality derived, material changes reach CIT-P (CIT-P side)

**Requirement** (Contract v3:446, :638-647; framework §47-48): whether a proposed or performed change is material for
each of the eight classes is determined from what it changes, and material changes cannot complete outside CIT-P/CIT-E
(the in-task half is WS-5's close-side detection, round 3).

**Changes.** `runtime/src/cit/materiality.rs` (new):
* `MATERIAL_CLASSES`, `BOOKKEEPING_FIELDS`, `PLANNING_FIELDS` (`priority`, `owner_role`, `legacy_source`: planning
  attributes of a specification record are not behaviour — found by the sweep, §5.3); the rule table in the module
  doc: architecture/interface/security record types and paths; acceptance criteria (requirement/scenario criteria,
  test obligations, feature scope, Gherkin `.feature` files); behaviour (other content of requirements, scenarios,
  features, decisions; product source); security (security-named path segments; removed/changed lines carrying a
  security check); governance (`governance/**` except generated, `framework/**`, policy/overlay files);
  infrastructure (paths and content: Terraform `resource`/`module`, Kubernetes `apiVersion`+`kind`; sizing diffs);
  data migration (migration paths, SQL DDL/DML, destructive SQL called out; dataset schema fields); decisions carry
  the class of their `tags`.
* `Finding {class, subject, rule, evidence, requires_cit_in_task}` (every class requires a CIT in-task except
  behaviour changes to product source, which an implementation task is contracted to make), `Materiality`
  (`classes`, `effective_triggers(declared)`, `effective_trigger`, `requiring_cit`, `to_value`), `Change`,
  `classify`, `changes_of_manifest` (manifest ops **and declared path targets** without a manifest — a CIT that only
  declares `governance/project/PROJECT_POLICY.yaml` is governance, R5, gated), `classify_manifest`,
  **`classify_paths(p, paths, base)`** (performed changes, the WS-5 API), `radius_floor`, `git_output`.
* `runtime/src/cit/mod.rs`: `propose` records `materiality` and auto-simulates on the effective triggers; appended
  records are schema-validated **at propose** (an invalid one never becomes an open transaction); `estimate_radius`
  takes the maximum class floor; the gate's `trigger` is the most severe effective trigger and its `subject` lists
  all; `gov cit classify [--id <CIT>] [--paths a,b] [--base <commit>]`.
* `framework/policies/CHANGE_POLICY.yaml`: comment stating that trigger lists apply to effective triggers.

**Product checks and tier.** Inside `propose`/`simulate` (every CIT, G0-adjacent); `gov cit classify` (read-only).

**Probes.** delta-r K3: all seven `K3.b*.mislabel` FAIL→PASS (`b1..b4, b6..b8`); `K3.b*.label` and `K3.b5.path` stay
PASS. `K3.outside.1-3` and gamma-r `G1.b3 (c)` stay FAIL: they observe a material edit **closed through an ordinary
task**, which is WS-5's `tasks::close` (IP R2-4). Builder scenario S2 7/7 (base 1/7), including
`S2.declared-governance-target` — the executable statement of WS-2's deferred skill scenario SKL-IMPACT-ANALYSIS V1
(R5 + human gate; base R2), so IP-WS02-20 can now be flipped to `mode: executable` by WS-2 (R2-9).

**Tests.** lib: `each_material_class_is_derived_from_what_changes_not_from_a_label`,
`bookkeeping_and_editorial_changes_are_not_material` (planning attributes included),
`the_declared_label_is_kept_but_never_lowers_the_derived_classes`,
`declared_path_targets_are_classified_without_a_manifest`; certification `materiality_is_derived_not_labelled`.

**Changed builder test.** `tests/certification/repair.rs::cit_auto_simulation_and_secret_redaction` auto-approved an
`editorial` CIT that writes product source. Writing product source is a behaviour change (R2, above the R1 auto
ceiling), so the approval now goes through the owner channel (`ws03::human_decide`) and the test still asserts what
it is about (`SECRET_IN_MANIFEST` at execute). Not weakened: the gate is now required and asserted.

**Limits.** The classifier is rule-based (paths, fields, content markers); an unusual layout (e.g. infrastructure
without recognisable markers in a free-named directory) is classified only by its declared label. The in-task half
(refusing a material edit closed outside a CIT) is WS-5's.

### 2.3 BC-P2-04 — upstream change invalidates completed work, evidence and packets

**Requirement** (Contract v3:632, :1129-1136, :788-789): when an authoritative upstream artefact changes — through
CIT-E or directly — dependent task evidence (open and completed), implementation/test/release evidence and compiled
packets become stale as impact analysis dictates, revalidation/rework is generated, close cannot clear staleness
without retest evidence, and an index rebuild never substitutes for dependency staleness. Handoff note: the round-1
packets and receipts must go stale when their inputs change.

**Changes.** `runtime/src/cit/propagation.rs` (new):
* `plan(p, store, changed, impact, only_tasks)`: consumers through the task-input manifests (dependency slot
  excluded — a dependency's status is not an input change), the CIT's impact tasks/tests, closing reports, declared
  tests, the validation closure (feature scenarios, acceptance tests), checkpoints/handoffs/packets of affected tasks
  and checkpoints that recorded the changed input.
* `apply(...)` under `CHANGE_POLICY.propagation.*`: open tasks `retest_required` + `staleness`; completed tasks
  `revalidation` + a generated revalidation task (`tasks::create`, class `validation`, `revalidates: <task>` — new
  relation `revalidates → TESTS` in `records.rs`); `staleness` on closing reports (the receipt they carry is the
  consumed-hash record, so it is stale with them), test obligations, scenarios, checkpoints, handoffs; stored packets
  `invalidated`. Accumulates causes; idempotent (a second run for a recorded change writes nothing).
* Normative hashing (`NON_NORMATIVE_FIELDS`, `normative_hash`, `record_hash`): markers and bookkeeping never look like
  upstream changes; packets/receipts/checkpoints carry normative hashes alongside byte hashes.
* Direct-change path: `Baseline` / `baseline_of` (what the work consumed: close checkpoint, else closing receipt, else
  last packet before close; open work: latest packet/checkpoint), `stale_inputs`, `task_staleness`, `detect`,
  `detect_and_propagate` (`gov cit propagate [--dry-run]`), `gov context staleness <task>`.
* Close side (API for WS-5): `require_current_inputs(p, store, task, report)` → `INPUTS_STALE` /
  `RETEST_EVIDENCE_REQUIRED`, returning what the close should persist.
* `cit::execute` runs propagation **inside** the transaction (the snapshot covers every path the plan may touch; a
  rollback undoes it); the CIT's `execution.propagation` and the accepted-CIT checkpoint record the summary.
* `runtime/src/context/mod.rs`: packet `input_hashes` + `input_normative_hashes` (dependency slot excluded),
  deterministic authority `input_staleness`; `compile_tolerant` marks the previous history copy invalidated and
  records `redelivery`; `ensure_dispatchable` refuses `PACKET_INVALIDATED`; `verify_delivery` compares normatively and
  reports invalidation. `context/receipt.rs`: a receipt may name the normative hash.
* `framework/policies/CHANGE_POLICY.yaml`: `propagation.{revalidate_completed_tasks, generate_revalidation_tasks,
  mark_evidence_stale, mark_checkpoints_stale, invalidate_context_packets}` (covered by the existing
  `CHANGE_POLICY.propagation.*` ENFORCEMENT_MAP wildcard). `CONTEXT_POLICY` authority fields `input_staleness`.

**Product checks and tier.** CIT-E (G4 milestone), `gov cit propagate` (write, `simulate_cit` authority),
`gov context staleness` (read), packet compile/dispatch.

**Probes.** zeta-r W06: the seven CIT-path lines FAIL→PASS (`s6 completed-task-revalidated` ×2, `s7
closed-task-evidence-not-green`, `s2 test-evidence-invalidated`, `s3 context-packets-invalidated`, `s3
checkpoint-packet-ref-flagged`, `s5 rework-tasks-generated`); delta-r K2 `K2.b4.4-6`, `K2.w6.1-2`, `K2.b8.2`
FAIL→PASS; AC16-X1 `X1-K2xW6-done-task-revalidated`, `-done-evidence-stale`, `-rework-generated`,
`-packet-invalidated` FAIL→PASS. Builder scenario S3 12/12 (base 2/12), including the direct change detected after an
index rebuild and propagated.

Still FAIL, host side: W06 `(direct)` lines, `W6-s1-direct-change-forces-cit`,
`AC16-W6xD1-rebuild-does-not-license-stale-consumption`, `W6-s7-retest-flag-not-cleared-by-close`, epsilon-r O4 §F
and AC16-X1 `X1-G1xW6-*` observe `task show`/`task claim`/`task close`/`memory rebuild`/`audit` after a direct edit —
WS-5's and WS-6's and WS-2's commands. The detection and refusal they need exist (`task_staleness`,
`detect_and_propagate`, `require_current_inputs`); wiring them is IP R2-1..R2-3, R2-6, R2-7.

**Tests.** lib: `staleness_accumulates_changes_and_is_idempotent`, `normative_content_ignores_bookkeeping_and_tracks_content`,
`receipts_name_consumed_hashes`; certification `upstream_change_reaches_completed_work` (CIT path, direct path,
idempotence).

**Limits.** Direct changes are propagated when something runs detection (`gov cit propagate`, a handoff of the
affected work, packet re-delivery); nothing runs it automatically at index rebuild, claim or close until round 3.

### 2.4 BC-P2-05 — checkpoint triggers, staleness, handoff/session continuity

**Requirement** (Contract v3:729-742, :1155-1160): every mandatory trigger produces a checkpoint without relying on
the agent; checkpoints record mandatory-input ids/versions (or a state reference current at checkpoint time) and go
stale when the material state they captured changes; handoff and session close are blocked or explicitly degraded
when checkpoint or required-input freshness violates a stated policy; the watchdog observes execution boundaries
itself.

**Changes.** `runtime/src/checkpoints.rs` (rewritten around the existing record): `working_tree_changes` (porcelain
`-z`, fixing the dropped first character; every changed file named, a wholly untracked directory with more than 20
files recorded as `dir/`), `observe_state` (task states, material decisions, routing digest, telemetry count),
`task_inputs` (inputs with content/normative/delivered hashes, `input_state`), `create` (index brought current
**before** the memory snapshot, `state_reference`, `observed_state`, `triggers_observed`, open questions as strings,
G3 `tier_run` recorded in `health` — IP-WS02-07), `latest` with freshness, `freshness(p, id)` /
`gov checkpoint freshness`, `observe_boundaries`, `watchdog` (operations = max(caller, gov commands since the last
checkpoint from telemetry, files changed since it); a command in the checkpoint's own second counts), `session_close`
/ `gov session close` (never refused; `degraded` names stale/missing/contradictory inputs), `FRESHNESS_POLICY`.
`runtime/src/orchestration/handoffs.rs`: G0 guard `handoff.create` and G3 health (IP-WS02-07), `handoff_freshness`
(`HANDOFF_INPUTS_UNSATISFIED` refusal; stale packet → re-delivered, `REFRESHED`, `degraded`, targeted direct
propagation marking the in-progress work for retest), the before-handoff checkpoint carries it.
`framework/policies/CHECKPOINT_POLICY.yaml` `fields` += `inputs, input_state, state_reference, observed_state,
triggers_observed`.

**Probes.** delta-r N1 `N1.b4b`, `N1.b6` FAIL→PASS; N2 `N2.b7` FAIL→PASS; N3 `N3.b1.5`, `N3.b2.1`, `N3.b3.1-3`
FAIL→PASS (18/18); zeta-r W09 six lines FAIL→PASS (15/16); AC16-X1 `X1-NxW9-checkpoint-stale-marked`,
`X1-NxW9-handoff-blocked-or-degraded` FAIL→PASS; W12 `W12-G3-continuity-verified(checkpoint)` FAIL→PASS. Builder
scenario S4 8/8 (base 0/8).

Still FAIL, host side: `N2.b1.other` (claim/status change → WS-5), `N2.b2` (gate answer → decision: WS-3), `N2.b4`
(index rebuild of 30 files: WS-6), `N2.b6` (routing switch: WS-3), `N2.b8` (generated pre-compaction hook: adapters),
`AC16-NxW9-doctor-checkpoint-freshness` (doctor: WS-2). `observe_boundaries` already turns each of these into a
checkpoint at the next boundary (scenario `S4.boundaries-observed`); the probes look immediately after the action.

**Tests.** lib: `transitions_decisions_and_routing_changes_are_triggers`, `material_decisions_are_gate_derived_human_or_wide`,
`files_changed_names_files_and_bounds_large_untracked_trees`; certification `checkpoint_and_handoff_continuity`.

### 2.5 BC-P2-18 — contradictions detected and routed (detection side)

**Requirement** (Contract v3:657-660, :1103; framework §50): contradictory authoritative inputs precedence cannot
resolve are detected and routed to agent resolution within policy or to a Human Decision Gate instead of being
delivered together as authority; a task whose mandatory inputs conflict does not become READY until resolved. The
resolution rules (who may answer) are WS-3's; READY derivation is WS-5's.

**Changes.** `runtime/src/context/contradictions.rs` (new): `Contradiction`, `detect_among`, `detect_all`,
`Resolution` / `resolution` (verified answer + the option→outcome table in `subject.outcomes`), `route` (system gate,
trigger `contradiction`, OS-assessed radius R1/R2/R3 and detection confidence), `route_for_task`.
`runtime/src/context/manifest.rs`: `apply_contradictions` (task inputs ∪ project-wide contradictions containing an
input → `CONTRADICTORY` + blocking `CONTRADICTION`; after resolution the set-aside member is
`SET_ASIDE_BY_RESOLUTION`, blocking only where a task declared it explicitly). `context/mod.rs`: packet authority
`contradictions`; `compile_tolerant` routes before compiling and records `contradiction_routing`. `records.rs`:
`conflicts_with`/`contradicts → CONSTRAINS`. `graph/identity.rs::check` reports contradictions with their
resolution. `CONTEXT_POLICY` authority fields += `contradictions`.

**Probes.** delta-r L1 `L1.b1.6` FAIL→PASS; `L1.b2.neg.*` PASS→PASS (WS-3's rules applied to the OS-sourced
assessment). zeta-r W03 `W3-r3-conflict-flagged-in-packet` PASS; `W3-r3-conflict-triggers-handling` stays FAIL:
the probe's conflict is a supersession (precedence resolves it, the manifest is `BLOCKED` with `SUPERSEDED`), and it
observes `task replan` making the task READY — WS-5's READY derivation (round-1 IP-1, R2-5). Builder scenario S5 6/6
(base 0/6).

**Tests.** lib: `precedence_resolves_first_and_undecidable_pairs_are_detected`,
`explicit_keys_questions_forks_and_declared_conflicts`; certification `contradictions_are_blocked_and_routed`.

**Limits.** Detection is structural (declared links, supersession graph, decision keys/questions/derived subjects);
two free-text requirements that contradict in prose are not detected (no semantic judgement in the kernel).

## 3. Integration points routed to WS-4 this round

| IP | Status | How |
|---|---|---|
| IP-WS02-05 (G0 at CIT propose/approve/execute) | implemented, one stated deviation | `scheduler::guard(ops::CIT_PROPOSE / CIT_APPROVE / CIT_EXECUTE, paths)`. **Deviation at execute (repair mode):** a transaction may execute under an active hard-block only if it repairs it — the guard re-runs after the manifest is applied and a transaction that leaves any block is rolled back with `HEALTH_HARD_BLOCK` and the block state re-established. Without it the brownfield certification (a governed repair of a HIGH schema block) deadlocks. Nothing commits under a block it does not clear. |
| IP-WS02-06 (G4 after CIT-E) | implemented | `tier_run(G4, Trigger::cit_execute)` after commit, recorded in `execution.health` (not a journal event: the K2 journal sequence is part of the record contract), then an incremental index rebuild. |
| IP-WS02-07 (G3 at checkpoint/handoff; guard at handoff) | implemented | `checkpoints::create` and `handoffs::create` record G3 `health` (skipped inside the sandbox); `guard(ops::HANDOFF_CREATE)`. |
| ws03 IP-4 | implemented | answers only via `gates::verified_answer(_in)`; CIT and contradiction gates via `create_system`; CIT state sealed (`cit::binding`); undecidable contradictions → system gate `trigger: contradiction`. |
| ws05 IP-1 (task contract in the packet) | implemented | deterministic authority `task_contract` = `tasks::contract_enforcement`; `CONTEXT_POLICY` field added (gamma-r I1I2 `I2.b4 required_data` and `I2.b9 production merge` now True in the packet). |
| ws05 IP-3 (per-path writes of an execution) | API implemented; WS-5 consumes in round 3 | `execution.writes` (sealed `writes_sha256`), `binding::verified_writes` (honoured only for a T2-verified `COMMITTED` CIT). |
| ws06 IP-5 | implemented | `failure` → `spec/reports/failures`, `FAIL`; retrieval-miss failures canonical under `memory::failures::MEMORY_QUALITY_DIR` (`graph::identity::canonical_dir_of`). |
| ws09-11 IP-5 | implemented | `migration-plan` → `spec/audits/GOVERNANCE-ADOPTION`, `MPLAN`. |
| ws04 IP-17 | implemented | `INDEX_VERSION = "4.1.5-idx4"` (edge derivation changed: `revalidates`, `conflicts_with`, `contradicts`). |

Incidental repairs inside `cit::execute` (non-blocking audit findings, recorded so they are not mistaken for scope
creep): A0-K2-03 (verification compares against a fresh pre-execution baseline — the index is brought current before
the dangling-edge baseline; `K2.b7.2` PASS in the valid-fixture copy) and A0-K2-02 (rollback regenerates derived
views so they match the restored state).

## 4. New integration points for round 3

| ID | Owner | File / function | Call to add | Why |
|---|---|---|---|---|
| R2-1 | WS-5 | `orchestration::tasks::close` | `cit::propagation::require_current_inputs(p, &store, task, &report)?` before DONE; persist its `revalidated_inputs`; clear `retest_required` **only** when it returns `clears_retest: true` | BC-P2-04 close side (W6-s7 retest flag, AC16-W6xD1, X1-G1xW6) |
| R2-2 | WS-5 | `orchestration::tasks::{claim, dag, list, show}` | `cit::propagation::task_staleness(p, &store, task)` → a stale-input reason; `claim` refuses while inputs are stale | direct-change staleness visible where work is picked (W06 `(direct)` lines) |
| R2-3 | WS-5 / WS-6 | `memory::indexer::rebuild` (end) or `tasks::claim/close` | `cit::propagation::detect_and_propagate(p, "index rebuild", false)` | direct changes propagate without an operator running `gov cit propagate` |
| R2-4 | WS-5 | `orchestration::tasks::close` | `cit::materiality::classify_paths(p, &changed, Some(claim_base)).requiring_cit()` → refuse (or require a covering committed CIT) for each finding; accept an out-of-scope path only when `cit::binding::verified_writes(cit)` contains it at its current hash | BC-P2-13 in-task half (K3.outside.*, G1.b3 c) and BC-P2-14 CIT coverage bound to content (ws05 IP-3) |
| R2-5 | WS-5 | `tasks::replan` / READY derivation | `context::manifest::require_ready` (round-1 IP-1) — now also blocks on `CONTRADICTORY` | W3-r3-conflict-triggers-handling |
| R2-6 | WS-5 / WS-3 | task status change, claim, `gates::answer`, routing selection | `checkpoints::observe_boundaries(p, db, next_action)` after the transition | N2.b1.other, N2.b2, N2.b6 immediately, not only at the next boundary |
| R2-7 | WS-2 | `doctor` / `verification` families | a check over `checkpoints::freshness`, `cit::bindings` + `binding::verified_state`, `contradictions::detect_all`, `propagation::detect` (G1); record G4 results as governance-suite records | AC16-NxW9-doctor, X1-UxO5, X1-W12-G4-wider-check-recorded, W6-s7-stale-evidence-surfaced |
| R2-8 | WS-2 | `scheduler::catalogue` (`CRIT_ALL` operations) | decide whether `cit.propose` belongs to governed work under a *critical* block: today (IP-WS02-05 as specified) a critical block refuses proposing the CIT that would repair it (alpha-r A3 §C5 aborts; epsilon-r O5 S6 now shows the refusal) | governed repair path vs O5 S6 |
| R2-9 | WS-2 | `framework/health/SKILL_SCENARIO_CHECKS.yaml` | SKL-IMPACT-ANALYSIS V1 → `mode: executable` (IP-WS02-20) | now TRUE: R5 + gate (scenario `S2.declared-governance-target`) |
| R2-10 | WS-6 | `memory::manifest::freshness` vs `memory::indexer::rebuild` | freshness must skip what the indexer excludes as `too_large` (> 2 MB) and duplicate-id records, or the indexer must list them in the manifest's `excluded` | pre-existing: such a file is "added" forever, so every CIT-E fails `index_freshness` verification (seen in beta-r R1-R2 until the checkpoint size fix, §5.3) |
| R2-11 | WS-6 | `memory::indexer::rebuild` | `checkpoints::observe_boundaries` when the rebuild indexes ≥ the significant-mutation threshold | N2.b4 |
| R2-12 | adapters owner | `adapters::generate` | provider hooks that call `gov checkpoint create --trigger before_compaction` and `gov session close` | N2.b8 |
| R2-13 | WS-3 | `control::COMMAND_GUARDS` / `g0_label` review | new labels: `cit classify` (read), `cit propagate` (`simulate_cit`, write), `cit propagate --dry-run` (read), `context staleness` (read), `checkpoint freshness` (read), `session close` (`checkpoint`, write) | classification added additively this round |
| R2-14 | WS-1 | evidence map | the 14 new lib tests, 5 `ws04r2` certification tests, the builder scenario probe | O3 regression evidence |
| R2-15 | WS-8 | release lineage | round-1 IP-16 stands | unchanged |

CLI additions (additive, self-contained blocks in `cli/src/main.rs`, each classified in `COMMAND_GUARDS` and
`g0_label`): `gov session close [--next-action] [--task]`, `gov cit classify [--id <CIT>] [--paths a,b] [--base <commit>]`,
`gov cit propagate [--dry-run]`, `gov context staleness <task>`, `gov checkpoint freshness [<id>]`.

## 5. Probe re-runs

### 5.1 Method

`evidence/run-probe.sh` re-runs an audit-of-record probe **unedited** against a chosen binary through the P2-AR-0022
owner-channel adapter (which adapts only the three paths WS-3 removed by design), `before` = a `git archive` export of
`843d79c` with the base binary (`sha256 7095d188…`), `after` = a private symlink mirror of this worktree with the final
binary (`sha256 7014aded…`, HEAD `cd02bfc`, 0 product files differing). Each output records the probe sha256 and the
real binary. `evidence/compare.py` pairs every verdict line (`COMPARE-before-after.out`);
`evidence/diff-unmarked.sh` gives the normalised diff of probes that print observations only
(`UNMARKED-normalised-diff.out`). Three **labelled derived** copies (`evidence/derived/`, one stated change each) are
run by `run-derived.sh`.

Probe set (48): delta-r K1, K2, K3, K4, L1, L2, L3, L3-supplement, N1-N2, N2-adopt, N3-N4-W9, FRESH, J1-J2; zeta-r
W01-W12, W04b, FR; synthesis AC16-X1, AC16-X2; epsilon-r O4, O5-G0-guard-matrix, O5-scheduler-requirements,
O5-tiers-G1-G6; gamma-r G1G2, E1, E2, E3, H1, I1I2, I3; alpha-r A3, A4, A5; beta-r C1, C2, C6, D6, R1-R2,
X-K2-D1-W6. The last 17 were added as a sweep of every audit probe that drives a CIT, to catch regressions outside my
classes.

### 5.2 Totals and every PASS→FAIL

**88 FAIL→PASS, 4 PASS→FAIL** (verdict lines) — per class in §2. The four PASS→FAIL are delta-r K4 `K4.a.traversal`,
`K4.b.semantic_breadth`, `K4.f.human_approval`, `K4.f.auto`: the probe produces its "R0" and "R1" rows by labelling
one **requirement-statement edit** `editorial` / `data_migration`. After BC-P2-13 that edit is a behaviour change
whatever its label (R2, gated), so all rows share one radius and the "grows with the radius"/"R0 auto-approves" lines
cannot hold. The derived copy `K4-impact-radius.derived-rows.P2-AR-0025.py` varies the radius through what each row
touches and gives 6/9 on both binaries (the radius effects themselves are unchanged; `K4.d/e/g` fail on both).

Other before/after differences, none a lost capability:
* delta-r K2 `K2.b3.2` is no longer printed: the schema-invalid appended record is refused at **propose**
  (`SCHEMA_INVALID`), so the probe's `if cbad:` branch never runs; nothing is persisted (the line's requirement,
  enforced earlier). K2 unedited 25/26: `K2.b7.2` stops on `HEALTH_HARD_BLOCK` because the probe's fixture feature
  lacks the schema-required `readiness` (a HIGH `schema_invariants` block once G4 runs after CIT-E); the valid-fixture
  derived copy gives 26/26.
* gamma-r I3 `I3.b6`: an `editorial` CIT changing a requirement's **acceptance criteria** is auto-approved by the
  probe; it is now `acceptance_criteria_change` (a human-gate trigger), so execute refuses and the event is not
  produced — BC-P2-13's intended effect on the probe's premise.
* alpha-r A3 §C5 aborts (traceback) and epsilon-r O5 S6 now prints `cit propose → HEALTH_HARD_BLOCK`: the probes plant
  a secret (critical D011) and then propose a CIT; G0 at `cit.propose` (IP-WS02-05 as specified) refuses. O5 S6 asks
  exactly whether a RED repository blocks governed work; whether proposing a repairing CIT should be exempt is R2-8.
* alpha-r A4 B5 (radius R1→R3; the CIT writes `spec/architecture/INFRA-note.md`, so architecture is derived alongside
  the declared infrastructure cost), beta-r C6 (R1→R2), epsilon-r O5-tiers (R2→R3): derived materiality.
* gamma-r E3 (`context_packet_hash` in handoff inputs), I1I2 (task contract in the packet), E1/E2 (message wording,
  line number), epsilon-r O5-tiers (the `before` root is a `git archive` export, so the probe's `git grep` fails
  there), O5-scheduler-requirements (inode/timings): environmental or additive.

Incidental passes **not claimed**: `W12-G0-superseded-target-substitution-blocked(cit)` passes because the CIT is now
gated (material), not because superseded targets are detected; `N3.b2.2` passes on both binaries through D021 (green
record currency), not a checkpoint-freshness doctor check (R2-7).

### 5.3 Regressions the sweep found and I repaired (in this run)

1. **gamma-r G2.b5** (rollback demonstration): an `editorial` CIT setting a requirement's `priority` had become gated
   (priority classified as behaviour). Planning attributes (`priority`, `owner_role`, `legacy_source`) are no longer
   behaviour (`2fb66d5`); the same edit in gamma-r I1I2 `I2.b8.x` (WS-5's BC-P2-14 probe premise) executes again. The
   normalised diff of G1G2 is now empty.
2. **beta-r R1-R2** (A11 remediation CIT failed `VERIFICATION_FAILED: index not fresh`): listing every untracked file
   made each brownfield checkpoint ~13 KB; the adoption classification that cites them grew past the indexer's 2 MB
   limit, and memory freshness (which does not know the limit) reports such a file as unindexed forever. Checkpoints
   now name every changed file but record a wholly untracked directory of more than 20 files as `dir/` (`c4a16f6`);
   R1-R2 is back to 22/4 as on base. The underlying freshness/indexer mismatch is WS-6's (R2-10).
3. **Watchdog timing**: commands in the checkpoint's own second were not counted (one-second timestamps, strict
   comparison), which made `ws04r2::checkpoint_and_handoff_continuity` fail once. The watchdog now counts them — it can
   fire early, never late (`cd02bfc`).

## 6. Regression and R1

* `evidence/regression/cargo-test-lib.out` — 160 passed / 0 failed at `cd02bfc` (146 base + 14 new unit tests).
* `evidence/regression/cargo-test-certification.out` — 105 passed / 0 failed (100 base + 5 `ws04r2`), including
  `section6` (§6 derivation) and the changed `repair::cit_auto_simulation_and_secret_redaction` (§2.2).
* `evidence/regression/rustfmt-check.out` — every touched Rust file clean (the pre-existing diffs rustfmt reports in
  `srr/breakglass.rs` and `srr/metadata.rs` are in files this run did not touch).
* `evidence/regression/timing.out` (indicative, one run): CIT execute 0.15 s → 0.42 s (propagation, G4 health, index
  rebuild), checkpoint 0.06 → 0.14 s and handoff 0.06 → 0.24 s (G3 health, index brought current).
* `evidence/r1-heldout/r1-heldout-worktree-cd02bfc.out` — private scratch `…/ar25/r1-P2-AR-0025-run3`, symlinks
  `srr1-r1-verify{,-2,-3,-4}` → this worktree, suites byte-identical (cmp-verified), HEAD `cd02bfc`. AR-0027 26/3
  (`b1`, `b2`, `d3`), AR-0029 26/2 (`b3`, `b6`; `ho_f_preservation` does not compile), AR-0031 27/7 (`a1`, `a5`,
  `a8`, `b6`, `c2`, `c3`, `d2`) — identical to the recorded baselines and to the round-1 integration; AR-0033 30/1:
  `hv_a_derivation::a1` fails only on its scale pin (84 files / 740 functions; this tree 109 / 1580). The labelled
  copy `hv_a_derivation.a1-unpinned.P2-AR-0025.rs.txt` (the two size assertions printed instead of asserted — the
  only diff, shown in the output) reproduces the census with **0 violations** in every §6 activity
  (human_gate_create 44 derived / 39 writers / 1 exempt; human_gate_approve 1/1; release_certification 1/1;
  trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2; floor_lower_or_reset 3/1;
  present_below_floor_release_as_current 1/1), and AR-0033's own `derive.py` (ROOT line only) agrees under all three
  splitter configurations. `records.rs` changes are confined to relation fields and `TYPE_DIR`/`TYPE_PREFIX`;
  `save_record` is untouched.

## 7. Files changed (product)

`runtime/src/cit/{mod.rs, binding.rs (new), materiality.rs (new), propagation.rs (new)}`,
`runtime/src/context/{mod.rs, manifest.rs, receipt.rs, contradictions.rs (new)}`, `runtime/src/checkpoints.rs`,
`runtime/src/orchestration/handoffs.rs`, `runtime/src/graph/identity.rs`, `runtime/src/records.rs` (relation fields,
`TYPE_DIR`/`TYPE_PREFIX` only), `runtime/src/lib.rs` (`INDEX_VERSION` only),
`framework/policies/{CHANGE_POLICY,CHECKPOINT_POLICY,CONTEXT_POLICY}.yaml`; additive exceptions:
`runtime/src/orchestration/control.rs` (six `COMMAND_GUARDS` entries), `cli/src/main.rs` (five subcommands, their
arms and `g0_label`), `tests/certification/main.rs` (`mod ws04r2;`); tests: `tests/certification/ws04r2.rs` (new),
`tests/certification/repair.rs` (one test updated, §2.2). No schema file changed (the schemas involved are open);
nothing under `release/verification/`, `release/root-of-trust/`, `release/releases/`,
`release/orchestration/phase-1/`, `release/capability-baseline/audit-0/` or another workstream's directory.

## 8. Owner-decision questions

None. R2-8 (whether a critical block should refuse *proposing* a repairing CIT) is a scheduler-policy choice for WS-2
and the orchestrator within the existing contract, not an owner question.
