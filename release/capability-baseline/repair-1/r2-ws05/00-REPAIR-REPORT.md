# WS-5 repair report — repair iteration 1, round 2 (P2-AR-0026)

| Field | Value |
|---|---|
| Run | P2-AR-0026, fresh `capability-repair` builder, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0024 (WS-5 round 2), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol) |
| Branch / base | `phase2/repair-1-r2-ws05` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree, `product_code_digest b1ab1c8c…fbb1`) |
| Work commits | `1de472e` (main repair), `a60b867` (builder tests `ws05.rs`), `090eded` (producer rule, unit tests); then the commit that adds this report and `evidence/` |
| Product after | `product_code_digest 7679602a12e887a2ea210fd50f253ca14e63daa431aaf03ee08c67235dcbd728` at `090eded` (`governed_state_digest` unchanged, `4981437f…227d`); `target/release/gov` sha256 `6d3db3c0…8e9a` |
| Classes | BC-P2-16 `REPAIRED_CLAIMED`; BC-P2-12 (DAG side) `REPAIRED_CLAIMED`; BC-P2-20 (close side) `REPAIRED_CLAIMED`; BC-P2-34 (task-role side) `REPAIRED_CLAIMED`. The BC-P2-09 close side (WS-3 IP-1, WS-5 IP-5) is implemented as integration points, not claimed as a class (the class is WS-3's), with a stated transitional limit (§5.4) |
| Integration points | all 17 routed IPs addressed (§6): 15 implemented in full; WS-4 IP-6 implemented on the WS-5 side (the CLI arm is WS-3's); WS-5 IP-5 implemented for reports and claim baselines, and for CIT records conditionally on CIT sealing (§5.4); none obsolete. 10 new round-3 IPs (§6.2) |
| Regression | `cargo test --lib` **151 / 0** (base 146); `cargo test --test certification` **107 / 0** (base 100; +7 `ws05`); 0 build warnings; rustfmt clean on every touched file |
| R1 held-out | at baseline in all four suites; AR-0033 `hv_a::a1` fails only on its 84/740 size pin — census of this tree **105 files / 1499 functions, 0 violations in every §6 activity** (§8) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims only; nothing here is acceptance (Contract v3 O3) |

Every figure below comes from a run recorded under `evidence/`. "Base" is the round-2 base binary (the integrated round-1
tree, built from `843d79c` in a private scratch path, sha256 `7095d188…0332`); "after" is this branch's binary.

---

## 0. What changed, in one view

`tasks.rs` is where several workstreams' round-1 APIs meet. This round wires them into one close, one claim and one
notion of "runnable", and closes the WS-5 classes on top.

| Area | Files | Change |
|---|---|---|
| Runnable is derived (BC-P2-16, BC-P2-12 DAG side) | `orchestration/dag.rs` | One evaluation (`dag::evaluate`, `DagCtx`, `TaskEval`) decides every route: the runnable set, `claim`, `task create --status READY`, `task status READY`, `replan`, `gov continue`. It checks dependencies and `blocks`, required data/tools/skills, the **mandatory task-input manifest** (`context::manifest::resolve`, WS-4 IP-1), **every governing Human Decision Gate** through `gates::task_gate_authorisation_in` (WS-3 IP-2) — the task's `human_gate` *and* the latest T2-verified gate whose `blocks_tasks` names it — readiness policy, TEST_POLICY including independence from recorded authorship, pending re-tests, DRAFT and **explicit holds**. |
| Claim consults the DAG (WS-5 IP-9) | `orchestration/tasks.rs::claim` | Refuses `TASK_NOT_RUNNABLE` (every reason in `details`) unless the DAG finds the task runnable; G0 hard-block guard (`scheduler::guard(task.claim)`, IP-WS02-03); recorded-authorship independence (`INDEPENDENCE_VIOLATION`). |
| READY routes | `tasks::create`, `tasks::set_status`, `dag::replan`, `readiness::plan` | `create --status READY` stores the status the DAG derives (with `ready_check` in the result); `task status READY` refuses `TASK_NOT_READY`; `DONE`/`CLAIMED`/`IN_PROGRESS` are refused `TASK_STATUS_REQUIRES_OPERATION` (reached only through close/claim); replan never promotes an explicit hold; the planner stores gap tasks as derived. |
| Close pipeline | `tasks::close`, `tasks::require_receipt` | The ordered checks of §0.1: worker-return normalisation (`receipt::report_from_worker_return`, WS-4 IP-2), claim and sealed baseline, role, independence, **gate authorisation** (`GATE_NOT_AUTHORISED`, WS-3 IP-1 second half), **T2-classified observation** (WS-3 IP-1), production merge, index, **receipt validation** (`receipt::validate`/`require_valid` semantics, WS-4 IP-2), **`verification::close_gate`** (WS-2 IP-WS02-01). The report is **sealed** (`t2::seal_record`); the task records `outputs_produced` (the task → output edge, WS-4 IP-2). |
| OS-written state at close (BC-P2-09 close side) | `tasks::classify_os_path`, `observe_against`, `closed_states`, `cit_window_paths` | A changed OS-managed path is the OS's own write only when its T2 seal verifies, or when it is an unsealed record of a kind not yet sealed by every writer; a broken seal, a missing seal on a kind the OS always seals (gates, gate-derived decisions, close reports, `t2::SEALED_RECORD_TYPES`), or a deleted governed record is the worker's mutation, refused whatever the report declares. Attribution reads only sealed reports; CIT window coverage honours sealed CIT records and, until CIT state is declared sealed, unsealed ones (§5.4). |
| Sealed claim evidence | `tasks::write_baseline`, `read_baseline`, `read_carried`, `write_carried` | The claim baseline (tree snapshot, committed CITs, reports present, **the task contract as claimed**) and the carried-mutation file are T2-sealed; a baseline that does not verify refuses the close (`CLAIM_BASELINE_UNBOUND`; an L3 `--force` falls back to git's view and records the override). The close is held to the contract as claimed as well as the record as it is (allowed/forbidden paths, merge permission, role, gate). |
| Recorded authorship (BC-P2-34) | `tasks::AuthorshipIndex`, `independence_conflicts`, `dag::DagCtx::{obligation_dependence, data_dependence}` | Authorship of a path = the latest sealed close report that accepted a change to it (content still what it accepted, or since changed only by an honoured COMMITTED CIT). Independence of tests (TEST_POLICY families) and test data from the implementer is established from it, never from `independent_of_implementer`/`author_role`; one session does not both implement a feature and do its independent test/data work. |
| Designated roles for independent gap work | `framework/taxonomy/READINESS_DIMENSIONS.yaml`, `readiness::plan` | `gap_task_role`: `independent_acceptance_tests → independent-test-designer`, `representative_test_data → data-author`; the planner sets `role`, which binds claim and close. |
| Producers of specification | `dag::produces_feature_specification`, `packet_blocked_only_by_inherited`, `tasks::require_receipt`, `status::continue_work` | A readiness gap task (or a specification-producing class) is not blocked in the DAG, refused at close (`MANIFEST_UNSATISFIED`/`PACKET_BLOCKED`) or withheld by `continue` because of inputs it only **inherits from its feature** and is itself writing; what it declares itself still binds (§1.4). |
| Guards | `tasks::create`, `claim`, `release`, `status::continue_work` | `scheduler::guard(task.create / task.claim)` (IP-WS02-02/03, `continue --claim` before any side effect); `control::guard_write("task release"[ --force])` in `release` (WS-5 IP-4). |
| Status / continue / intents | `status.rs`, `intents.rs` | `status.health` (`scheduler::status`, IP-WS02-04); `release_trust` from **this project's** `srr::installation::posture_of` (WS-8 IP-4; still reads `Degraded::load`); `continue_work(p, impl Into<IndexHandle>, claim)` compiles through the handle and never dispatches a packet whose mandatory inputs are unsatisfied (`ensure_dispatchable`, WS-4 IP-3/IP-6), reporting degradations; no proposal of `--by human` (WS-3 IP-3). |
| Claims store | `memory/claims.rs` | **A copied store is not the store**: the store records its canonical location; opened elsewhere (a health-scheduler sandbox, a restored runtime dir) its rows are not live claims and are cleared. Found because sandboxed skill scenarios were refused `CLAIM_SCOPE_CONFLICT` by the live project's claims, which made every governance-affecting close fail its G2 currency re-check once `close_gate` was wired (§6.3). |
| Schemas | `task`, `report`, `worker-return` `.schema.json` (1.1.0) | Task: `required_inputs`/`optional_inputs` (the W3 entry shape), `supplementary_context`, `architecture`, `relations[].note/required`, `provenance`, `provenance_requested`, `status_source`, `outputs_produced`, `closed_at`, `status_note` (WS-4 IP-5). Report and worker-return: the consumption-receipt fields (`$defs/consumption_receipt`); report also `receipt_validation`, `mutation_evidence`, `close_gate`, `os_binding`. |
| Provenance | `tasks::create`, `readiness::plan` | `provenance: {producer, session, role, created_at}` is written by the operation; a caller-supplied value is kept as `provenance_requested` (WS-4 IP-4; D-0007 rule 2). |

Files outside the WS-5 set (17 files changed in all, `git diff --stat 843d79c 090eded`): the new builder-test file
`tests/certification/ws05.rs`; `tests/certification/main.rs` gains one line (`mod ws05;`, the additive registration, as
`mod ws03;`/`mod ws08;` were added in round 1); six existing certification tests in `greenfield.rs`, `repair.rs`,
`repair2.rs`, `ws03.rs` and `failure_injection.rs` were updated under P2-HO-0010's regression rule ("if an intended
behaviour change breaks an existing builder test, update the test and state exactly why") — each reason is in §7. The
integrator should expect textual overlap in `tests/certification/main.rs` (every builder adding a `mod` line) and
possibly in `ws03.rs` (WS-3's round-1 test file; my change there only moves `task create`/`context compile` before the
doctor run). No other file outside `runtime/src/orchestration/{tasks,dag,readiness,claims,intents}.rs`,
`runtime/src/memory/claims.rs`, `runtime/src/status.rs`, `framework/schemas/{task,report,worker-return,test-obligation}.schema.json`
and `framework/taxonomy/**` changed (`orchestration/claims.rs` and `test-obligation.schema.json` were not needed).

### 0.1 The close, in order — and why this order

| # | Check | Refusal | L3 `--force` |
|---|---|---|---|
| 1 | normalise the worker return (lossless `status → outcome`) | — | — |
| 2 | another session's live claim | `TASK_CLAIMED` | overridden, recorded |
| 3 | evidence payload (`tests.status` ∈ TEST_POLICY, `work_completed`) | `EVIDENCE_REQUIRED` | no |
| 4 | the claim: this session, this working tree | `CLAIM_REQUIRED`, `CLAIM_WORKTREE_MISMATCH` | overridden, recorded |
| 5 | the claim baseline is the sealed one the claim wrote | `CLAIM_BASELINE_UNBOUND` | overridden (git's view), recorded |
| 6 | designated role, as recorded and as claimed | `ROLE_NOT_DESIGNATED` | overridden, recorded |
| 7 | independence from recorded authorship | `INDEPENDENCE_VIOLATION` | overridden, recorded |
| 8 | every governing Human Decision Gate authorises the work | `GATE_NOT_AUTHORISED` | **no** |
| 9 | observed mutations declared, in scope (now and as claimed), no T2 violation | `MUTATION_SCOPE_VIOLATION` (`details.t2_violations`) | no |
| 10 | production-merge permission (now and as claimed) | `PRODUCTION_MERGE_NOT_ALLOWED` | no |
| 11 | index pins and freshness | `INDEX_PIN_MISMATCH`, `INDEX_STALE` | stale only (degraded) |
| 12 | the consumption receipt | `RECEIPT_INVALID` | no |
| 13 | `verification::close_gate`: G0 hard-block, G2 re-check, O4 currency, O1 product tests | `HEALTH_HARD_BLOCK`, `GOVERNANCE_SUITE_STALE/_MISSING`, `PRODUCT_TEST*` | currency only (degraded) |

The handoff's essentials name "receipt normalisation → receipt validation → T2 classification → gate authorisation →
currency/product-test close gate". I kept normalisation first and the health gate last, but moved **gate authorisation
before, and receipt validation after, the T2-classified observation**, deliberately:

* who may close (2, 4-7) and whether gated work may complete at all (8) do not depend on the evidence, so they are
  decided before any evidence is weighed; a human gate is not an L3 decision, so `--force` never overrides it;
* the repository's own state, observed independently of the worker (9-10), is weighed **before** the worker's account
  of it (12): otherwise an incomplete receipt would mask an out-of-scope or forged mutation. The audit-of-record probes
  depend on this: zeta-r `W5-c2-undocumented-change-detected` and delta-r `L3.b5.9` expect `MUTATION_SCOPE_VIOLATION`
  on reports that are also receipt-incomplete;
* the evidence payload (3) keeps its long-standing place (beta-r C7-b5, zeta-r `W5-r5-tests-status-enforced`);
* the health gate (13) runs last because its G2 re-check may execute checks and record a governance-suite result,
  which nothing before it should cause for a close that is refused anyway.

---

## 1. BC-P2-16 — runnable / claimable / READY derived from the DAG

**Requirement** (repair-delta BC-P2-16; Contract v3:392, :522, :587, :1101). A task is claimable, stored READY or offered
as runnable only when the DAG allows it — dependencies, readiness policy, TEST_POLICY, gates, mandatory inputs present,
and not in a blocked status. Dep BC-P2-12, -17, -45 (all landed: WS-3/WS-4 round 1).

### 1.1 What changed

`dag::evaluate` is the single decision (§0). The routes that store or rely on READY all call it:

| Route | Before (base) | After |
|---|---|---|
| `task claim` | checked the stored status only | DAG must find the task runnable (`TASK_NOT_RUNNABLE` + reasons); a derived BLOCKED whose reasons cleared is claimable (the DAG, not a cached status, decides) |
| `task create --status READY` | stored READY | stores the derived status (READY / BLOCKED / WAITING_HUMAN) and returns `ready_check` |
| `task status X READY` | accepted | `TASK_NOT_READY` unless runnable |
| `task status X DONE / CLAIMED / IN_PROGRESS` | accepted | `TASK_STATUS_REQUIRES_OPERATION` (close / claim only) |
| `task status X BLOCKED / WAITING_HUMAN` | ignored by the DAG | an **explicit hold** (`status_source.operation = task status`): not runnable, not offered, never replanned; released only by an explicit, DAG-checked READY |
| `replan` | promoted on dependencies/gates only | promotes only runnable tasks; keeps explicit holds; records `status_source: replan` |
| `gov continue` | offered the runnable set | offers only runnable work this session may take (role, live claims, scope overlap, **independence**), dispatches only a dispatchable packet (§3) |
| `task release` | set READY | stores the derived status (an explicit hold set during the claim stays) |

The manifest check is WS-4's `context::manifest::resolve` (absent, superseded, conflicting, non-current,
authority-class, version/hash-violating inputs block). Readiness keeps reading the precedence-enforced project policy
(`p.project_policy()`, BC-P2-45).

### 1.2 Product checks

Every `task claim`, `task create`, `task status`, `task replan`, `task dag`, `gov status` and `gov continue` evaluates
the DAG. Builder tests: `ws05::runnable_ready_and_claimable_are_derived_from_the_task_dag` (certification);
`dag::tests::explicit_hold_is_only_a_status_set_by_task_status_and_still_in_force`,
`dag::tests::task_state_names_are_stable`, `tasks::tests::operation_only_statuses_name_their_route` (lib).

### 1.3 Probes re-run

| Probe line (audit of record) | Base | After | Mode |
|---|---|---|---|
| zeta-r `W3-r1-create-READY-with-missing-input` | FAIL | **PASS** | unedited and adapter |
| zeta-r `W3-r1-replan-READY-with-missing-input` | FAIL | **PASS** | both |
| zeta-r `W3-r1-status-READY-with-missing-input` | FAIL | **PASS** | both |
| zeta-r `W3-r1-claim-with-missing-input` | FAIL | **PASS** | both |
| zeta-r `W3-r1-missing-task-dependency-bypass-via-status` | FAIL | **PASS** | both |
| zeta-r `W3-m2-required-state-enforced`, `W3-m3-hash-pin-enforced` | FAIL | **PASS** | both |
| zeta-r `W3-r3-conflict-triggers-handling` | FAIL | **PASS** (the conflicting-decision task is not replanned READY; routing to a contradiction gate is WS-4's) | both |
| zeta-r W03 other 12 lines | as base | unchanged | both |
| zeta-r `W12-G0-current-version-substitution-blocked(claim)` | FAIL | **PASS** | adapter |
| AC16-X2 `X2-I4-blocked-not-runnable`, `X2-I4-continue-does-not-offer-blocked` | FAIL | **PASS** | derived X2 copy (adapter); the unedited probe stops earlier (§3.3) |
| gamma-r `E4.b5` (claim of a task whose dependency is open) | claim `ok`, then closed DONE | claim `TASK_NOT_RUNNABLE`, close `CLAIM_REQUIRED` | adapter |
| gamma-r `H3.b5` (L2 sets a readiness-blocked implementation task READY, implementer claims) | `task status READY` ok | **`TASK_NOT_READY`** | adapter |
| gamma-r `I2.b3`, `I2.b6`, F2F3 `(h)` | not runnable | not runnable (unchanged) | adapter |

Supplementary probe (`evidence/probes/ws05_r2_supplementary.py`, after 37/37 PASS; base 5 PASS — all five are labelled
controls — 31 FAIL): A1 create-READY derived, A2 status READY refused, A3 claim refused, A4 replan no promotion, A6
explicit hold not runnable and not offered, A7 DONE only by close, A8 missing-dependency bypass closed (all FAIL on base,
PASS after); A5 control.

### 1.4 The producer rule — found while wiring, and why it is general

Wiring the manifest into the DAG exposed a deadlock: WS-4's manifest makes every task of feature F inherit F's listed
requirements/scenarios/tests/interfaces as mandatory inputs. A readiness **gap task whose job is to write those records**
then waited for them: on a feature listing records that did not exist yet, the planner's gap tasks were all BLOCKED and
nothing was runnable (observed while wiring; that pre-fix run is not kept as evidence —
supplementary E6 is the regression check, with a feature listing an absent `REQ-0999`). The rule applied (DAG, close receipt, packet dispatch):
a task that produces its feature's specification — a readiness gap task, or a specification-producing class
(`discovery, research, specification, decision-preparation, data, architecture, test-design, security, performance`) —
is not blocked by entries it **only inherits from its feature**; what it declares itself still binds, and implementation
work of the feature stays blocked until the inputs exist (supplementary E6). The receipt keeps the same rule
(`INHERITED_INPUT_UNSATISFIED` becomes a recorded warning, not `MANIFEST_UNSATISFIED`/`PACKET_BLOCKED`). IP-R3-4 asks
WS-4 to move this into `manifest::resolve`, so `gov context manifest|receipt` agree natively.

### 1.5 Limits

* The gap work can now start and pass its receipt, but a **specification-class** close is governance-affecting, and
  WS-2's currency gate requires a *green* suite; a feature with dangling references keeps the suite DEGRADED
  (`graph_integrity`), so such closes are refused `GOVERNANCE_SUITE_STALE` until the references resolve or an L3
  `--force` records the degradation. Routed as observation O-R2-1 (WS-2).
* A dependency counts as DONE by its stored status (a sealed close report is not required for dependency completion);
  task records are not yet sealed (§5.4).
* Explicit holds apply to BLOCKED and WAITING_HUMAN set by `gov task status`; `task create --status BLOCKED` is a
  requested initial status, derived like any other.

---

## 2. BC-P2-12 (DAG side) — task-blocking gate semantics

**Requirement** (repair-delta BC-P2-12; Contract v3:678; framework §53). Work blocked by a gate becomes runnable only on
an authorising answer, returns to blocked when it is revoked or withdrawn, cannot be completed while the gate is
unanswered, and a reference to a missing gate blocks. WS-3 did the answer side in round 1 (`task_gate_authorisation`).

### 2.1 What changed

* The DAG asks `gates::task_gate_authorisation_in` for **every governing gate**: the task's `human_gate`, and the
  latest T2-verified gate whose `blocks_tasks` names the task (ordered by `raised_by.at`, then id). PENDING waits
  (WAITING_HUMAN); DECLINED, WITHDRAWN, MISSING and UNVERIFIED block with the gate's own reason. Removing `human_gate`
  from a task record by hand does not release it: the OS-written gate still names the task.
* `close` refuses `GATE_NOT_AUTHORISED` unless every governing gate — including the one recorded in the sealed claim
  baseline — authorises; `--force` does not override it. `claim` refuses through the DAG.
* `dag.human_gate_dependencies[]` carries each gate's authorisation.

### 2.2 Probes re-run

| Line | Base | After | Mode |
|---|---|---|---|
| delta-r `L3.b4.t2` declined answer | FAIL | **PASS** | adapter |
| delta-r `L3.b4.t3` revoked authorising answer | FAIL | **PASS** | adapter |
| delta-r `L3.b4.t4` withdrawn unanswered gate: replan + claim | FAIL | **PASS** | adapter |
| delta-r `L3.b4.t5` missing gate reference | FAIL | **PASS** | adapter |
| delta-r `L3s.1` close while the blocking gate is pending | FAIL | **PASS** | adapter |
| delta-r L3 other 35 lines | as base | unchanged | adapter |

(delta-r probes stop at setup unedited on both binaries — undeclared roles, WS-3 round 1 — so they are measured through
the evidence adapter, exactly as the round-1 integration did.) Supplementary B1-B7: B2-B6 FAIL on base, PASS after
(B6: close refused `GATE_NOT_AUTHORISED` while gated, **also with `--force`**); B5 shows the field-removal attack;
B1 and B7 are controls (B7 FAIL on the base with `USAGE`, a CLI surface the base lacks).

### 2.3 Limits

Answer semantics (which options authorise, owner-signed answers) stay WS-3's. A task referenced by an *unverified*
gate is blocked, so hand-written fixture gates block their tasks (by design, T2).

---

## 3. BC-P2-20 (close side) — the worker's return is the receipt

**Requirement** (repair-delta BC-P2-20; Contract v3:1115-1126, :1147-1152). The worker's structured return is the
consumption receipt, validated against the manifest; close refuses missing mandatory traceability and reports
untraceable implementation; code/test/output evidence links back to the authoritative inputs. WS-4 built the contract,
the mapping and the validator (round 1); the close side is WS-5's.

### 3.1 What changed

* `close` maps the return first (`report_from_worker_return`: `status` → `outcome`, lossless), so a worker return in
  the worker-return shape is the close report (X2-N4xW5's `SCHEMA_INVALID` collision is gone).
* Step 12 validates it with `receipt::validate` and refuses `RECEIPT_INVALID` with every error — `require_valid`'s
  behaviour, plus the producer rule of §1.4 (`tasks::require_receipt`). The canonical receipt and `receipt_validation`
  are persisted on the report; the report is sealed; the task records `outputs_produced` (what it was observed to
  produce, CIT-covered paths excluded), which yields the task → output lineage edges (`records::OUTPUT_FIELDS`).
* `worker-return.schema.json` and `report.schema.json` declare the receipt fields (the one contract). They are not
  `required` at the schema level: `handoff return` (WS-4) validates the return shape for handoffs that do not close a
  task, and the close enforces the receipt against the task's manifest.
* WS-2's `product::enforce_close` (via `close_gate`) decides the test claim. **WS-2 left the class interaction to WS-5**
  (its §4 limits): I apply no class exemption — a close claiming `tests.status: passed` needs recorded, current,
  passing product-test evidence for the covering families; where no product test can run, the report says
  `not_applicable_with_reason`. Contract v3:1004 ("test outcome at close is verified from recorded evidence") admits no
  exemption by task class.

### 3.2 Probes re-run

| Line | Base | After | Mode |
|---|---|---|---|
| zeta-r `W5-c1-refuses-missing-traceability` | FAIL | **PASS** | unedited |
| zeta-r `W5-r5-acceptance-evidence-bound-to-declared-tests` | FAIL | **PASS** | unedited |
| zeta-r `W5-r6-task-close-requires-unknowns` | FAIL | **PASS** | unedited |
| zeta-r `W5-r3r4-fabricated-trace-refused` | FAIL | **PASS** | adapter (receipt-completed report keeps the fabricated ids) |
| zeta-r `W5-c3-task-to-code-edge` | FAIL | **PASS** | adapter |
| zeta-r `W5-r1-inputs-supplied-in-receipt`, `W5-r2`, `W5-r3-…recorded`, `W5-r4-…recorded`, `W5-c3-code/report-linked`, `W5-c3-report-task-edge-direction` | PASS | PASS (unchanged) | adapter |
| zeta-r `W5-r5-tests-status-enforced`, `W5-r6-deviations-persisted-when-given`, `W5-r6-handoff-return-requires-unknowns`, `W5-c2-undocumented-change-detected` | PASS | PASS (unchanged) | adapter |
| zeta-r W08 (42 PASS / 6 FAIL) | 42/6 | 42/6 — identical | adapter |
| AC16-X2 `X2-N4xW5-worker-return-usable-at-close` | FAIL (`SCHEMA_INVALID`) | **PASS** | derived X2 copy (adapter), §3.3 |
| epsilon-r O1 §H (self-attested `passed` while the product suite fails) | close accepted (DONE) | unedited: refused `RECEIPT_INVALID`; adapter: accepted — adaptation (e) replaces the `passed` claim, so this line is read unedited only | both |

**Lines that change for fixture reasons, not regressions.** Unedited, the W05/W08/X1 probes close with bare
`{work_completed, files_changed, tests}` reports; the receipt refuses them (`RECEIPT_INVALID`). In W05 the lines that read
the persisted report (`W5-r1-packet-hash-on-close-checkpoint`, `W5-r2-outputs-produced`, `W5-c3-code-linked-to-requirement`,
`W5-c3-report-linked-to-requirement`) then read a report that was never written (PASS → FAIL), and the probe aborts
right after (`memory graph` of report id `None` raises `TypeError`), so its S2-S6 lines are not reached; W08 and X1
abort at their first close (`X1-C9-cit-p-candidates-deduplicated` not reached). Through the adapter, which completes
absent receipt fields only (§9), every one of those lines is as on the base (W05 r1-r4, r2, c3 PASS; W08 42/6);
`W5-r1-packet-hash-on-close-checkpoint` is FAIL under the adapter on both binaries because the adapter compiles a fresh
packet at close. Under the adapter the three S1 refusal lines (`c1`, `r5`, `r6`) are FAIL on both binaries, because the
adapter supplies what those lines test for; they are read unedited (FAIL → PASS above).
`W5-c2-untraceable-implementation-detected` (S6) is **not reached** under the adapter: an implementation task that
declares no scenario/test is not runnable (BC-P2-16), so the probe's `task claim` is refused `TASK_NOT_RUNNABLE` first;
`UNTRACEABLE_IMPLEMENTATION` is a rule of WS-4's validator; the close refuses every validator error through the same
`RECEIPT_INVALID` path (the `ws05` receipt test asserts `TRACEABILITY_MISSING` on it), but this run has no separate
evidence line for `UNTRACEABLE_IMPLEMENTATION` itself (see IP-R3-5).

### 3.3 X2-N4xW5 and the derived X2 copy

The unedited AC16-X2 stops at `task claim TASK-W` (an implementation task with no scenarios/tests is not runnable,
BC-P2-16). `evidence/derived/AC16-X2-authority-gate-chain.derived.P2-AR-0026.py` changes fixtures only (header lists
F1-F4: the two implementation tasks declare spec_base's REQ/SCN/TST; the TASK-H return carries the receipt fields from
its packet's `receipt_contract`; `gov verify product` records the evidence its `passed` claims; the worker releases the
refused TASK-W so TASK-H's claim does not overlap) and one diagnostic `note`. Every check line and criterion is
unchanged. Base-shim → after-shim: `X2-E1xG2`, `X2-N4xW5`, `X2-I4-blocked-not-runnable`,
`X2-I4-continue-does-not-offer-blocked` FAIL → **PASS**; unedited base → after: `X2-E1xG2` FAIL → **PASS**.

### 3.4 Limits

* Receipt semantics (which fields are required, the class list for traceability) are WS-4's; `UNTRACEABLE_IMPLEMENTATION`
  applies by class even when a task produced nothing (IP-R3-5).
* Every existing probe and fixture that closes with a bare report is refused; the adapter shows the other lines.

---

## 4. BC-P2-34 (task-role side) — independence from recorded authorship

**Requirement** (repair-delta BC-P2-34; Contract v3:366, :521, :526, :783-785; A0-E1-05, A0-H4-02). Independence is
established from recorded authorship (role and session of the author versus the implementer), bound to the evidence; a
task's designated role binds who may claim and close it. OWNER-DECISION-P2-0001 (Option A) keeps agent roles
adapter-declared: this run builds no credential.

### 4.1 What changed

* **Recorded authorship** (`tasks::AuthorshipIndex`): from the T2-sealed close reports and the exact content each
  accepted. An artefact whose content no sealed close accepted (hand-written, or edited since outside an honoured CIT)
  has **no** recorded author.
* **Tests** (`dag::DagCtx::obligation_dependence`): an obligation of a TEST_POLICY independence family counts as
  independent of implementation task T only when its recorded author exists, is not T itself, is not in T's designated
  role, and is not the session holding T's claim. `independent_of_implementer: true` is ignored as evidence.
* **Test data** (`data_dependence`): datasets an independent obligation relies on (`test_data`, `datasets`,
  `data_provenance` ids) block T when their recorded author — or the record itself (a self-declared *dependence* is
  believed) — is T's designated role or claim session.
* **Sessions** (`tasks::independence_conflicts`, at claim, close and in `continue`'s offer): a session may not claim or
  close an implementation task whose independent tests/data it authored, nor implementation and independent test/data
  work of the same feature (live claims and sealed closes). `INDEPENDENCE_VIOLATION`; L3 `--force` records the override.
* **Designated roles for generated independent work** (`gap_task_role`), binding claim and close.
* `test-obligation` records under `spec/tasks/` (`TST-*`) are no longer treated as OS-managed: they are authored work,
  observed at close, and their authorship is recorded by the close that accepts them. Only `task` records there are
  OS-managed.

### 4.2 Probes re-run

| Line | Base | After | Mode |
|---|---|---|---|
| gamma-r `E1.b4.b` — implementer-authored obligation declaring `independent_of_implementer: true` | TASK-IM2 **runnable** | **blocked**: "…its independence is not established from recorded authorship" | adapter |
| gamma-r `E1.b4.b` — implementer claims the test-design task | `ROLE_NOT_DESIGNATED` | `HEALTH_HARD_BLOCK` (the fixture's dangling `TASK-NOPE` makes `graph_integrity` HIGH, a hard-block on every claim — WS-2's rule, O-R2-2); `ROLE_NOT_DESIGNATED` is shown by `ws05`/supplementary | adapter |
| gamma-r `H4.b2` — test data authored by the implementer role | TASK-0001 blocked reasons `[]`, runnable | **blocked**: "test data TD-0001 (used by TST-0001) declares itself authored by the implementer (author_role 'backend-engineer')…" | adapter |
| gamma-r `H4.b1` complete chain | runnable | blocked — its hand-written acceptance obligation has no recorded author (fixture effect of the requirement) | adapter |

Supplementary E1-E5 (E1, E3, E4, E5 FAIL on base, PASS after; E2 control): self-declared independence rejected;
recorded authorship satisfies it; the authoring session cannot implement whatever role it declares; implementer-authored
test data blocks; the planner designates `independent-test-designer` and `data-author`.
`ws05::independence_is_established_from_recorded_authorship` (certification).

### 4.3 Limits

* Session and role are caller-declared (OWNER-DECISION-P2-0001 Option A; its recorded residual risk): recorded
  authorship binds what was declared when the work closed. A hostile agent that declares a fresh session per step is out
  of the accepted envelope.
* Adoption-stage independence (A5/A7/A10/A11), held-out protection and data-authorship records are WS-9, WS-2 and WS-10.
* Hand-written independent obligations in fixtures (beta-r `C7`, gamma-r H4/E1) now block the implementation tasks
  that rely on them — by design.

---

## 5. BC-P2-09 close side — OS-written state observed at close (WS-3 IP-1, WS-5 IP-5; integration points, no class claim)

**Requirement** (repair-delta BC-P2-09; Contract v3:365, :427, :675; D-0007 T2 and rule 2). A lower-trust write to
OS-written state is observed and refused at task close rather than exempted.

### 5.1 What changed

WS-3's recipe was "replace `OS_MANAGED_PREFIXES` with `t2::classify_path`: a non-`Verified` change is a worker
mutation". Applied literally to the integrated tree it would refuse almost every close, because most OS writers do not
seal yet (task records, checkpoints, audit records, CIT records, generated views). I satisfied the IP's purpose this way
(`tasks::classify_os_path`):

| Changed OS-managed path | Treated as |
|---|---|
| carries a T2 seal that verifies | the OS's own write (`os_managed_bound`) |
| carries a seal that does not verify (edited after sealing, foreign, key unavailable) | **worker mutation of T2 state** |
| unsealed, and of a kind the OS always seals: `human-gate`, decisions asserting human approval or derived from a gate, close **reports** (sealed by `close`, their only writer), any type in `t2::SEALED_RECORD_TYPES` | **worker mutation of T2 state** |
| a governed record under `spec/` deleted | **worker mutation of T2 state** |
| unsealed, of a kind not yet sealed by every writer | the OS's own write, **reported** (`os_managed_unbound`) |

A T2 violation is refused (`MUTATION_SCOPE_VIOLATION`, `details.t2_violations`) whether or not the report declares the
path or the scope includes it; a change an in-window honoured CIT made (e.g. propagation rewriting a record) is that
CIT's. IP-5: `closed_states` (attribution to closes inside the window) and recorded authorship read **only sealed
reports**; claim baselines and carried sets are sealed.

### 5.2 Probes and checks

| Line | Base | After |
|---|---|---|
| AC16-X2 `X2-E1xG2-worker-forgery-invisible-at-close` (derived X2 copy, unedited and adapter) | FAIL (close ok) | **PASS**: `MUTATION_SCOPE_VIOLATION`, t2_violations = the edited gate (BROKEN) and the unsealed gate-derived decision |
| delta-r `L3.b5.9` | not reached (stops at `L3.b5.6`, `T2_UNBOUND` on a hand-edited gate — WS-3) | not reached (same) |
| gamma-r `E1.b3.d` | close ok, forgery invisible | not reached (claim `HEALTH_HARD_BLOCK`, O-R2-2) |
| supplementary C1 forged answer + decision; C4 forged report | FAIL | **PASS** |
| supplementary C5 rewritten claim baseline | not reached (section C aborts on the base: its close removes the baseline file) | **PASS** (`CLAIM_BASELINE_UNBOUND`) |
| supplementary C2 (control: declared forgery refused), C3 (control: the OS's own sealed gate in the window is not attributed) | C2 PASS; C3 FAIL (`USAGE`: a CLI surface the base lacks) | PASS |

### 5.3 Tests

`ws05::close_observes_os_written_state_no_os_operation_produced` (forged gate answer and decision refused, declared or
not; restored → closes; the OS's own gate written in the window is `os_managed_bound`; a hand-written report refused; a
rewritten baseline refused, and `--force` records `claim_baseline_unbound`).

### 5.4 Transitional limit (stated, not overclaimed)

* Kinds not yet sealed by every writer (task records — also rewritten by `gates.rs` and `cit/`; checkpoints; audit
  records; handoffs; lessons; generated views; CIT records) are accepted as OS writes and **reported**, not refused.
  Each becomes enforceable the moment its writers seal it; nothing in `tasks.rs` needs to change for records that carry
  a seal (a broken seal is already refused).
* **CIT window coverage** honours a sealed CIT record that verifies, never a broken one, and an unsealed one only while
  `t2::SEALED_RECORD_TYPES` does not contain `cit`. WS-4 seals CIT state this round (WS-3 IP-4); once `cit` is declared
  there (one line, WS-3's file), an unsealed CIT record covers nothing. Requiring a seal now would have refused the
  legitimate in-window CIT coverage exercised by `greenfield_end_to_end` in this tree.

---

## 6. Integration points routed to WS-5

| IP | Purpose | Status | Where / how |
|---|---|---|---|
| IP-WS02-01 | close uses `verification::close_gate` | **implemented** | close step 13; `touched` = declared ∪ observed, **minus in-window CIT paths** (the CIT's G4 tier covers them); `degraded` merged into the report and result. epsilon-r O4 (adapter) §D: a governance close on a green made stale by a policy change is now `GOVERNANCE_SUITE_STALE` (base: DONE); §E: the L3 `--force` close whose own change staled the green now closes with `degraded: []` (base: `["governance suite stale"]`) because the gate's G2 re-check re-establishes currency first — WS-2's designed behaviour, noted for the verifier; §F: TASK-0001 is not runnable (a mandatory input is absent), so the claim and close are refused. Supplementary I1: `passed` without recorded product-test evidence → `PRODUCT_TEST_EVIDENCE_REQUIRED` |
| IP-WS02-02 | scheduler guard at task create | **implemented** | `tasks::create` (after G0 write guard and authority); epsilon-r O5 S6: `task create` in a RED repo → `HEALTH_HARD_BLOCK` (base: created) |
| IP-WS02-03 | guard at claim and `continue --claim` | **implemented** | `tasks::claim`; `continue_work` guards before any side effect when `--claim`; O5 S6 `continue --claim` → `HEALTH_HARD_BLOCK` |
| IP-WS02-04 | `status` shows health | **implemented** | `status.health` = `scheduler::status` (typed `UNKNOWN` if it cannot be computed) |
| WS-3 IP-1 | T2 classification at close; refuse unless gate Authorised | **implemented** (purpose; §5 explains the recipe change) | §2, §5 |
| WS-3 IP-2 | DAG readiness via `task_gate_authorisation_in` | **implemented** | §2 |
| WS-3 IP-3 | intents/status stop proposing `--by human` | **implemented** | `intents.rs` proposes `gate present`, `trust human-channel`, `decide <g> --option <id>` (relay), `cit approve <c>`; `status.next_action` names the channel. delta-r `L3s.2` FAIL → PASS |
| WS-4 IP-1 | manifest in DAG, READY routes, claim, replan | **implemented** | §1 |
| WS-4 IP-2 | close: normalise → validate → `outputs_produced` | **implemented** | §3 |
| WS-4 IP-3 | `continue` compiles tolerantly, refuses non-dispatchable packets | **implemented** | compiles each candidate through the handle; a `BLOCKED` packet is deferred with its reasons (never dispatched) unless the producer rule applies; over-budget and retrieval degradations reported in `degraded` |
| WS-4 IP-4 | provenance at task create | **implemented** | zeta-r `W1-b7-task` FAIL → PASS (adapter) |
| WS-4 IP-5 | task schema declares manifest fields | **implemented** | task schema 1.1.0; zeta-r `W3-m2m3m4-manifest-fields-schema` stays PASS |
| WS-4 IP-6 | accept `IndexHandle::Unavailable` from the CLI | **implemented on the WS-5 side** | `continue_work<'a>(p, db: impl Into<IndexHandle<'a>>, claim)`: the current CLI call (`&RuntimeDb`) and WS-3's (an `IndexHandle`) both compile; W10 `derived-index-corrupted-continue` passes once WS-3 changes the arm |
| WS-5 IP-4 | `guard_write` in `tasks::release` | **implemented** | see §6.1 |
| WS-5 IP-5 | T2 into `closed_states` / `cit_window_paths` | **implemented** (reports, baselines; CITs conditional) | §5.4 |
| WS-5 IP-9 | claim consults the DAG | **implemented** | §1 |
| WS-8 IP-4 | `status.release_trust` from this project's `posture_of` | **implemented** | fields `posture`, `authenticity`, `authenticity_established`, `verified_release`/`verified_payload_hash` (only when established), `bound_release`, `integrity`, `disclosure`, `scope`; `marking`/`below_floor` still from `Degraded::load` (R1 AR-0031 a8 inspects that body) |

### 6.1 IP-4 — `task release` below floor (R1 §5)

`OWNER-DECISION-0006` §5's allow-list (`srr::breakglass::PERMITTED_OPERATIONS`) is `checkpoint`, `kernel reinstall`,
`update --apply`, `update --rollback`; "task release" is not a §5 activity (the breakglass module states §5 "repair" is
realised by the installation entries). Releasing a claim writes the claims store and the task record — normal
privileged operation (§6 bullet 1) — so `guard_write("task release")` refusing it below floor is what the default-refuse
policy requires; no §5 route depends on it (`gov recover` reaches only `checkpoint`). The CLI's G0 already refused it
under FREEZE_WRITES/PAUSE; the runtime guard adds kernel trust and the below-floor refusal (supplementary F1: refused on a
tampered kernel, `KERNEL_TAMPERED`; base released it). R1 suites unchanged (§8), including AR-0029 `ho_b` B5's census of
`guard_write` labels (no read label added).

### 6.2 New integration points (for round 3)

| ID | Owner | Change | Why |
|---|---|---|---|
| IP-R3-1 | WS-3 (`gates.rs` `block_tasks`/`move_tasks`), WS-4 (`cit/mod.rs` retest marks) | re-seal task records they rewrite (`t2::seal_record(tr, "<operation>")` before `save_record`); then WS-5 seals task records and adds `task` to the must-be-sealed kinds | makes hand edits of *other* tasks' records (e.g. forged DONE) refusable at close (§5.4) |
| IP-R3-2 | WS-4 (+ WS-3 for `t2.rs`) | seal every CIT write (COMMITTED record with `execution.propagation.touched`); add `"cit"` to `t2::SEALED_RECORD_TYPES`; re-seal gate-derived decisions a CIT rewrites (rollback, set_field) | unsealed CIT records then cover nothing; a CIT rewriting a sealed decision is not a T2 violation elsewhere |
| IP-R3-3 | WS-4 | any OS write into a sealed report or an authored test obligation (BC-P2-04 staleness marks) either re-seals the report or records the path in a CIT's `touched` list | otherwise concurrent closes see a T2 violation / an undeclared change, and recorded authorship is lost |
| IP-R3-4 | WS-4 (`context::manifest::resolve`) | apply the producer rule (§1.4) in the manifest itself | packets, `gov context manifest/receipt` and the DAG agree; `tasks::require_receipt`'s filter and `continue`'s producer dispatch become no-ops |
| IP-R3-5 | WS-4 (`context::receipt`) | apply `UNTRACEABLE_IMPLEMENTATION` when implementation was produced (source outputs), not by class alone | a class-`implementation` task that produced nothing (X2's TASK-H fixture) is otherwise refused |
| IP-R3-6 | WS-4 (round 1 IP-3) → WS-5 round 3 | per-path content hashes written by CIT execution; `observe`/`scope_violations` accept an out-of-scope path only when its hash equals the in-window CIT's | binds "the CIT governing that specific change" to content |
| IP-R3-7 | WS-2 (`error.rs`) | map `GATE_NOT_AUTHORISED` (and optionally `TASK_NOT_READY`, `CLAIM_BASELINE_UNBOUND`) to exit 4 (blocked class, API-0002) | exit-code consistency |
| IP-R3-8 | WS-1 (`capability-evidence-map.yaml`) | owners: I4/W3/E4 runnable derivation → `dag::*` tests, `ws05::runnable_…`, supplementary A; L3 task gates → `ws05::gates_…`, B; W5 close → `ws05::close_requires_…`, D; E1/H4 independence → `ws05::independence_…`, E; BC-P2-09 close → `ws05::close_observes_…`, C | AC-10 |
| IP-R3-9 | docs (WS-3 round 2 owns `docs/**`) | document `TASK_NOT_READY`, `TASK_STATUS_REQUIRES_OPERATION`, `GATE_NOT_AUTHORISED`, `INDEPENDENCE_VIOLATION`, `CLAIM_BASELINE_UNBOUND`, `RECEIPT_INVALID` at close, explicit holds, recorded authorship, the producer rule, the close order (§0.1) | operator documentation |
| IP-R3-10 | WS-5 round 3 | BC-P2-24 generation from events; BC-P2-13 in-task material-change hook (WS-4 exposes the classifier this round) | handoff notes |

### 6.3 Observations routed (not WS-5 files; nothing changed for them)

| ID | What | Owner |
|---|---|---|
| O-R2-1 | Governance-affecting closes require a **green** governance suite (`currency::enforce_close`); a DEGRADED suite caused by the incomplete specification the work is completing (dangling references → `graph_integrity` MEDIUM) refuses every such close, so readiness gap work for a feature with unwritten records cannot close without an L3 `--force` (supplementary E6 detail: `GOVERNANCE_SUITE_STALE`). Consider separating currency (fresh, complete evidence) from health gating (the per-check hard-blocks). | WS-2 |
| O-R2-2 | `graph_integrity` HIGH (one task depending on a missing task) hard-blocks `task.claim` **globally**: every claim in the project is refused until the dangling dependency is fixed (gamma-r E1 fixture). The block rule's scope may deserve narrowing. | WS-2 |
| O-R2-3 | Health-scheduler sandboxes copied the live claims store, so a live `src/**` claim made the sandboxed SKL-BACKEND-IMPL V1 scenario fail `CLAIM_SCOPE_CONFLICT` and the suite DEGRADED — which, once `close_gate` was wired, refused every governance-affecting close. Fixed on the WS-5 side (a copied claims store is not the store, `memory/claims.rs`); WS-2 may additionally leave `claims.db` out of sandbox copies. | WS-2 (fixed here) |
| O-R2-4 | zeta-r `W7-o4b-feature-only-acceptance-test` turns FAIL → PASS under the adapter only because the probe scans `gov task dag` output and the DAG's independence reason names `TST-0010`; it is **not** orphan detection (BC-P2-22, WS-2). | verifier note |

---

## 7. Existing builder tests changed, and why

No assertion was weakened; each change follows an intended behaviour change.

| Test | Change | Reason |
|---|---|---|
| `greenfield::greenfield_end_to_end` | gap tasks claimed and closed by the role their dimension designates, each from its own session; the independent test designer's gap task writes `TST-0001` (previously written by the test directly); every close is a receipt (`ws05::receipt`); asserts the planner designated `independent-test-designer` and `data-author` | BC-P2-34 (recorded authorship, designated roles), BC-P2-20 (receipt) |
| `repair::task_close_enforces_mutation_scope` | the implementation task declares a requirement, scenario and `unit` test obligation (`ws05::traceable_inputs`), created READY and asserted READY; final close is a receipt claiming `not_applicable_with_reason` | BC-P2-16 (an implementation task with no scenarios/tests is not runnable, so its claim was refused); BC-P2-20; BC-P2-43 via `close_gate` (a `passed` claim now needs recorded product-test evidence the test never records) |
| `repair::authority_levels_are_enforced_on_executable_paths` | the L1 worker's close is a receipt | BC-P2-20 |
| `repair2::task_close_uses_observed_mutations_not_self_attestation` | the final successful close is a receipt | BC-P2-20 (the refused closes keep their `MUTATION_SCOPE_VIOLATION` assertions: observation precedes the receipt) |
| `repair2::project_policy_cannot_weaken_constitutional_floors`, `ws03::project_overlays_may_raise_floors_but_never_lower_them` | the task is created and its packet compiled **before** doctor records the CRITICAL D027; repair2 adds an assertion that `task create` is then refused `HEALTH_HARD_BLOCK` naming D027 | IP-WS02-02: task creation is guarded by the G0 hard-block; D027 critical blocks every governed operation |
| `failure_injection::injected_failures_are_detected_and_recovered` | the close that succeeds after the index refresh is a receipt | BC-P2-20 (the `INDEX_STALE` refusal is unchanged) |
| `tests/certification/main.rs` | `mod ws05;` | registers this round's builder tests |

New: `tests/certification/ws05.rs` (7 tests and the certified receipt helpers `receipt`, `receipt_with`,
`traceable_inputs`); lib unit tests `memory::claims::tests::a_copied_store_is_not_the_store_its_claims_are_not_live_there`,
`dag::tests::*` (2), `tasks::tests::*` (2).

---

## 8. Regression and R1 preservation

| Suite | Result | Evidence |
|---|---|---|
| `cargo test --lib` | **151 passed, 0 failed** (base 146) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` (incl. `section6::*`, `srr::*`, `ws03::*`, `ws08::*`) | **107 passed, 0 failed** (base 100), 210 s | `evidence/regression/cargo-test-certification.out` |
| rustfmt (edition 2021) on every Rust file changed; build warnings | clean; 0 | `evidence/regression/rustfmt-and-warnings.out` |

**R1 held-out suites, unedited**, through a private scratch crate location unique to this run
(`…/scratchpad/p2ar0026/r1-P2-AR-0026-private-2`, symlinks → this worktree; runner `evidence/r1-heldout/run-r1-heldout.sh`,
derived from P2-AR-0022's; every copied suite file `cmp`-identical, 26 `identical` lines), at `090eded` (0 product files
differing from HEAD):

| Suite | Recorded baseline | This tree |
|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (`b3`, `b6`); `ho_f_preservation` does not compile | **26 / 2**, same; `ho_f` does not compile (same) |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0; integrated round 1: 30 / 1 (`hv_a::a1` size pin) | **30 / 1**: `hv_a_derivation::a1` only |

AR-0033 `hv_a::a1`, as P2-HO-0020 item 7 requires: the labelled copy
`evidence/r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0026.rs.txt` differs from the held-out file in the two size
assertions only (the `diff` is in the output). It measures **105 files / 1499 functions** on this tree and **0
violations** in every §6 activity: human_gate_create 43 derived / 38 writers / 1 exempt; human_gate_approve 1/1;
release_certification 1/1; trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2; floor_lower_or_reset 3/1;
present_below_floor_release_as_current 1/1. AR-0033's own `derive.py` (ROOT line only substituted) agrees, 0 violations
under all three splitter configurations. No file under `runtime/src/srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`,
`init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`, `tools.rs` or `capabilities/**` changed; `status.rs`
(a reporting surface R1 inspects) still reads `Degraded::load`. An intermediate run at `a60b867` gave the same result
(`evidence/r1-heldout/intermediate-a60b867/`).

---

## 9. Evidence method

* **Audit-of-record probes** run unedited from `release/capability-baseline/audit-0/*/evidence/` by
  `evidence/audit-probes/run-audit-probe.sh` in four modes: `after`/`base` (this binary / the base binary, no adapter) and
  `after-shim`/`base-shim` (through `gov-adapter.py`). The adapter is P2-AR-0022's owner-channel adapter, unchanged in its
  adaptations (a)-(c) (role declaration, owner-signed relay of an already-rendered gate, missing package fields), plus
  **(d)** completing only the *absent* W5 receipt fields of a close report from the packet's `receipt_contract` (supplied
  fields, fabricated ones included, are kept; the probe's file is untouched) and **(e)** turning a bare `passed` in such a
  report into `not_applicable_with_reason` (lines about the O1 close rule are read in the unadapted mode). (d)/(e) mask
  the receipt and product-evidence rules themselves, so W05's refusal lines and O1 §H are read unedited. Base and after
  use the same adapter, so every before/after pair differs only in the binary. `COMPARE.out` (by `compare.py`) lists
  every marked verdict change; unmarked families (gamma-r, epsilon-r, alpha-r) are adjudicated above from the outputs.
  In the `base*` modes the mirror's non-binary entries point at this worktree, so source-grepping lines show this tree's
  source.
* **Marked verdicts, base → after, unedited**: W03 8 FAIL→PASS, 12 same; W04 13 same; W05 3 FAIL→PASS (c1, r5, r6),
  4 PASS→FAIL and 10 not reached — all the fixture effect of §3.2 (bare report refused, then the probe aborts); W08 24
  not reached (first close refused `RECEIPT_INVALID`); X1 1 not reached (first close refused `RECEIPT_INVALID`); X2 1
  same, 4 not reached (`task claim TASK-W` refused `TASK_NOT_RUNNABLE`: an implementation task with no scenario or
  test); derived X2 copy 1 FAIL→PASS (`X2-E1xG2`), 4 same.
* **Marked verdicts, base-shim → after-shim (adapter)**: W03 8 FAIL→PASS; L3 4 (t2-t5), 35 same; L3s 2 (L3s.1, L3s.2);
  W05 2 (r3r4, task-to-code edge), 15 same, 3 not reached (S6, §3.2); W01 1 (`W1-b7-task`), 69 same; W12 1 (G0
  claim), 3 same, 10 not reached (`task claim` of a task whose mandatory input `REQ-9999` is absent is refused); W07 1
  (O-R2-4); X1 1 (`X1-G1xW6`: TASK-0002 with `retest_required` is no longer claimable, so the pre-change packet cannot
  be closed), 14 same; derived X2 copy 4 FAIL→PASS, 11 same; W02, W04, W04b, W06, W08, W09, W10, C9, J1-J2 unchanged;
  **no PASS→FAIL**. Not reached after: X2 14 lines (claim of TASK-W, as unedited), W11 13 lines (`task claim TASK-0002`
  refused: its mandatory input `REQ-0001` is SUPERSEDED — the requirement W3/W11-m3 measure), C7 7 lines (the
  implementation task's hand-written acceptance obligation has no recorded author, §4.3).
* **Supplementary probe** `evidence/probes/ws05_r2_supplementary.py`: `after-090eded` 37/37 PASS; `base-843d79c` 36
  checks, 5 PASS (A5, B1, C2, E2, E6 — all labelled controls) and 31 FAIL, including the controls B7 and C3 (`USAGE`) and
  `C.ran` (section C aborts on the base because its close removes the baseline file, so C5 and D4 are not reached).
* Scratch: every probe project, machine state and R1 crate lives under this run's own scratch directory; outputs contain
  those absolute paths.

## 10. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `regression/` | final `cargo test --lib` (151/0), `--test certification` (107/0), rustfmt and warnings |
| `r1-heldout/` | `run-r1-heldout.sh`, `r1-heldout-090eded.out` (final), the labelled `hv_a` copy, `intermediate-a60b867/` |
| `supplementary/` | `ws05-r2-supplementary.after-090eded.out` (37/37), `…base-843d79c.out` (negative control), `intermediate-1de472e/` |
| `probes/ws05_r2_supplementary.py` | the supplementary probe |
| `audit-probes/` | `run-audit-probe.sh`, `gov-adapter.py`, `compare.py`, `COMPARE.out`, `after/`, `after-shim/`, `base/`, `base-shim/` (each `.out`, with `.shimlog` for adapter runs) |
| `derived/` | `AC16-X2-authority-gate-chain.derived.P2-AR-0026.py` (labelled fixture-only copy), `run-derived.sh`, outputs per mode |
| `intermediate-1de472e/` | the first after-mode probe runs (binary of `1de472e`), superseded by the final runs above |

## 11. Owner-decision questions

None. No class needed a change to an accepted architecture or trust boundary, a new dependency class, an open
security/availability trade-off or owner-controlled material. The independence rules rest on caller-declared sessions
and roles, which OWNER-DECISION-P2-0001 (Option A) accepts with its recorded residual risk.

## 12. Process disclosures

* Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the product owner was not contacted; no session
  or agent transcripts, task-output stores or user auto-memory were read. Long commands ran in the foreground with
  output redirected to files.
* Probes were never edited; the derived X2 copy and the adapter are separate, labelled files. No file under
  `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
  `release/capability-baseline/audit-0/` or another workstream's `repair-1/` directory changed; the Contract v3 source is
  byte-identical (`4c2df291…5ed3`).
* One shell command that included `rm -f` of evidence files was denied by the permission system; it was not retried as
  written — superseded outputs were moved into `intermediate-*` directories instead.
* Found and fixed during the run (each before the final evidence): the claims-store sandbox interaction (O-R2-3), the
  in-window CIT paths counted as the task's "touched" inputs for the currency gate, and the producer deadlock (§1.4).
