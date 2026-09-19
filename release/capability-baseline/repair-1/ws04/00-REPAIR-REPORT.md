# P2-AR-0017 — Repair iteration 1, round 1, WS-4 (part): repair report

| Field | Value |
|---|---|
| Run | P2-AR-0017 (fresh capability-repair builder) |
| Handoff | `P2-HO-0014-repair-1-ws04.md` under `P2-HO-0010-repair-1-common-protocol.md` |
| Agent model | `claude-opus-5[1m]` (Claude Opus 5, 1M context) |
| Branch / base | `phase2/repair-1-ws04` from `c6b60bc760a0bb42907f74210fd9e644a420851a` (`product_code_digest bd4d65d9…0547`, the cap2-candidate-0 product) |
| Product commits | `a1e2a5c` (repair) and `6fc7361` (keeps the §6 bullet-7 marking inside `context::compile`; see §6.2) |
| Product code digest at `6fc7361` | `399a43a875bf13efa2492def2660f23a16031a93f3273abaad4a94b542a4a2ed` (governed-state digest unchanged: `3dabf06a…ad91`) |
| Classes | BC-P2-21 (records side), BC-P2-17, BC-P2-19, BC-P2-20 (contract and lineage side) |
| Claims | all four `REPAIRED_CLAIMED` for the WS-4 side, each with named integration points for the other workstreams' sides |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` |

This is a builder's claim with regression evidence (Contract v3 O3). It is not acceptance. Independent verifiers
decide acceptance with their own attacks.

## 1. Summary

The WS-4 side of the four classes is implemented generally, in modules WS-4 owns:

| Module (new or changed) | What it does |
|---|---|
| `runtime/src/records.rs` (relation-fields/edges region only) | Every relation field now gives an edge that points the way its meaning points. Fields declared on the target side are emitted under explicit inverse storage types. New relation fields cover inputs, receipts, outputs and influence. `Record::edges()` returns the canonical view. |
| `runtime/src/graph/mod.rs` | Every traversal reads stored inverse edges back canonically. Also adds implicit consumers (every task consumes the current architecture), `upstream_set` (reverse lineage), canonical `edge_type_counts`, and a dangling-edge rule for produced files. |
| `runtime/src/graph/identity.rs` (new) | The nine W1 attributes of any governed artefact: canonical location, content hash, VCS provenance, supersession, and expected/actual consumers. Also misplaced-record detection and content-derived stable ids. |
| `runtime/src/graph/lineage.rs` (new) | Record-level lineage that needs no index: stale links, actual vs expected consumers, successor map. |
| `runtime/src/context/manifest.rs` (new) | The W3 mandatory task-input manifest. It is declared by fields, inheritance, applicability, explicit `required_inputs`/`optional_inputs` with constraints and reasons, `relations[]` notes, and `supplementary_context`. It is resolved deterministically. `require_ready()` is the READY check. |
| `runtime/src/context/receipt.rs` (new) | The W5 consumption-receipt contract. It includes the lossless worker-return ↔ report mapping. `validate()`/`require_valid()` check a receipt against the manifest and the packet. `untraceable_closed_tasks()` lists closed work that does not trace. |
| `runtime/src/context/mod.rs` | The W4/W10 packet. It carries full normative content with version and content hash per input, the `input_manifest` block with `delivery_state`, `input_hashes`, the `receipt_contract` and repository provenance. Every packet is kept by hash. It stays outage-tolerant and is validated against its own schema. |
| `runtime/src/orchestration/handoffs.rs` | `handoff return` validates the worker's return as the receipt and records the verdict (non-blocking). |
| `cli/src/main.rs` (additive) | `gov context manifest|verify|show|receipt`, `gov artefact show|check|lineage`. `gov context compile` no longer needs a working index. |
| `framework/schemas/context-packet.schema.json` | Packet contract. `$defs` cover the manifest entry, task input declaration, delivered input and consumption receipt. `x-output-contracts` is the typed output→input table. |
| `framework/schemas/{handoff,interface,record}.schema.json` | `receipt_validation` on handoffs. Documented direction of `consumers`/`producers`/`influences`. |
| `framework/policies/CONTEXT_POLICY.yaml` | Existing keys only: new packet block and deterministic fields. No new keys, so `ENFORCEMENT_MAP.yaml` (WS-3) is untouched. |

**Probe results.** I re-ran the zeta-r (Gate W) audit-of-record probes unedited against `target/release/gov` at
`6fc7361`:
- **47 FAIL→PASS, 0 PASS→FAIL** over 16 probes (before: `evidence/before/`, byte-identical outcomes to the audit of
  record; after: `evidence/after/`).
- The FAIL lines left in my classes all sit on another workstream's side of the class. §7 names the exact call to add
  for each one.
- The synthesis probes AC16-X1, AC16-X2 and LEAD-X5 show outcomes identical to the audit of record. Their lines for my
  classes also depend on integration points.

**Regression.**
- `cargo test --lib`: 57 passed (42 before + 15 new).
- `cargo test --test certification`: 79 passed, including `section6::section_6_coverage_is_derived_from_the_product`.
- R1 held-out suites, run unedited: identical to their recorded baselines, except AR-0033
  `hv_a::a1_the_derived_census_reproduces_independently_at_the_claimed_scale`. That test pins the candidate-4 scale
  (84 files / 740 functions); this tree has 88 / 832. The census the pin guards still finds **0 violations** when run
  with AR-0033's own machinery (§6.2).

## 2. BC-P2-21 — Artefact identity and relation-edge semantics (records side)

**Requirement.** Repair-delta §1 BC-P2-21; Contract v3 lines 1069-1080, 1090, 1133. The requirements are:
- Every W1 output type carries a stable id, type, version/hash, producer and supersession lineage that survive
  re-generation.
- Records outside their canonical location are reported.
- Every relation field yields an edge whose direction matches its meaning.
- Every declared upstream-input field (including `required_data`) yields an edge that impact traversal follows.

Migration-plan and catalogue identity is WS-9's side.

**What changed**

- **Edge direction.** A field declared on the record an edge points to is now listed in
  `records::INVERSE_RELATION_FIELDS`:
  - `consumers` → `T CONSUMES X`
  - `producers` → `P PRODUCES X`
  - `task` on reports, checkpoints and handoffs → `T PRODUCES X`
  - `task.human_gate` → `G BLOCKS T`
  - `superseded_by` → `Y SUPERSEDES X`

  The indexer can only store `(declaring record, type, target)`. These fields are therefore emitted in inverse storage
  types (`graph::INVERSE_EDGE_TYPES`: `CONSUMED_BY`, `PRODUCED_BY`, `BLOCKED_BY`, `SUPERSEDED_BY`). `graph::out_edges`
  and `graph::in_edges` read them back as the canonical edge, so `neighbours`, `impact_set`, `upstream_set`, CIT
  simulation and retrieval all see edges that point the way their meaning points. `Record::edges()` gives the same
  canonical view per record.

  Before the change:
  - `consumers` gave `X CONSUMES T`, `producers` gave `X PRODUCES P` and `report.task` gave `RPT PRODUCES T`. All three
    were inverted.
  - `task.human_gate` gave `T BLOCKS G`, which was also inverted.
- **Declared inputs yield followable edges.**
  - `required_data`, `required_inputs` and `optional_inputs` give `CONSUMES`.
  - `architecture` gives `GOVERNED_BY`.
  - `influences` gives `AFFECTS`.
  - Every input a task declares also gives `task CONSUMES input` (`records::TASK_INPUT_FIELDS`, and the
    input-typed `relations[]`). This covers `acceptance_tests`/`scenarios`, whose `VALIDATED_BY` edge impact does not
    follow from the test back to the task.
  - The context compiler delivers every ACTIVE/PROVISIONAL architecture record to every task, so impact traversal now
    follows `graph::IMPLICIT_CONSUMERS`. The compiler reads the same table.
- **Outputs and receipts yield lineage.**
  - Report/task `outputs_produced` / `files_changed` / `observed_files_changed` give `PRODUCES file:<path>`. Checkpoint
    snapshots are excluded (`records::OUTPUT_RECORD_TYPES`).
  - `closed_by_report` gives `PRODUCES`.
  - The receipt fields give `IMPLEMENTS` / `GOVERNED_BY` / `CONSUMES` / `VALIDATED_BY`.
  - A `PRODUCES` edge to an unindexed or deleted `file:` output is lineage, not a dangling reference
    (`graph::dangling_edges`).
- **Identity** (`graph::identity::identity`, `gov artefact show <id>`). This gives the nine W1 attributes for any
  governed record:
  - id and type
  - canonical dir and whether the record is in it
  - authority class
  - lifecycle state
  - declared version and SHA-256 of the record bytes
  - declared provenance fields plus version-control provenance (introducing commit, last-changing commit, uncommitted
    changes)
  - `supersedes` and a derived `superseded_by`
  - expected and actual consumers

  None of this reads the derived index.
- **Canonical location.** `graph::identity::misplaced_records` / `gov artefact check` report records outside their
  type's canonical directory; subdirectories count as canonical. The manifest also flags a consumed input stored
  outside its canonical location (`NON_CANONICAL_LOCATION`, advisory).
- **Stable ids for outputs without an authored id.** `graph::identity::stable_content_id(prefix, key parts)` is an id
  derived from the natural key, not from position. This is the scheme for audit findings (WS-2) and catalogue entries
  (WS-9).
- **Lineage queries** (`graph::lineage`): `stale_links` (current records linked to superseded or non-current targets),
  `unconsumed_outputs`, `consumers_of` and `successor_map`.

**Product checks that own it.**
- The canonical-edge layer is structural: every graph query goes through it.
- `gov artefact show|check|lineage` runs on demand.
- Unit tests pin the behaviour: `graph::tests::*`, `graph::lineage::tests::*`, `graph::identity::tests::*`.
- The full-audit (health-tier) families call these through integration points IP-7 and IP-10 (WS-2).

**Probes re-run (before → after)** — `evidence/after/COMPARE-before-after.out`

| Probe line | Before | After |
|---|---|---|
| W02 `W2-b8-consumes-direction-not-inverted` | FAIL | PASS |
| W02 `W2-b1-typed-edges`, `W2-b8-impact-uses-typed-edges`, `W2-b8-consumer-reached-from-producer-change` | PASS | PASS |
| W04b `W4b-impact-reaches-declaring-task:DATA-0001` / `:TST-0002` / `:ARCH-0001` | FAIL | PASS |
| W05 `W5-c3-report-task-edge-direction` | FAIL | PASS |
| W06 `W6-s4-graph-impact(dataset consumed via task.required_data)` | FAIL | PASS |
| W01 every b1/b2/b4/b5/b6/b8/b9 line, `W1-move-keeps-id`, `W1-move-still-delivered` | PASS | PASS |
| W01 `W1-b7-*` (10 lines), `W1-b3-noncanonical-location-flagged`, `W1-b1-audit-finding-id-stable`, `W1-b6-benchmark-hash-in-record` | FAIL | FAIL (see limits) |
| W01b migration plan (8 lines); LEAD-X5 `X5-W1-*`, `X5-T3-*` | FAIL | FAIL (WS-9 side) |

**Builder scenarios.** `evidence/after/ws04-scenarios.out` S4: 9/9 PASS. The negative control on the base binary is
0/9 (`evidence/before/ws04-scenarios-negative-control-base.out`).

**Limits (what I did not do, and why)**
- `W1-b7-*` checks for provenance keys *inside the persisted text of probe-authored records*.
  - A product cannot add them without rewriting human-authored specs, and I chose not to do that.
  - Producer/provenance is established from version control and served by `gov artefact show` (the
    `provenance.version_control` block). The scenario line `S4-nine-w1-attributes` shows it.
  - For product-minted tasks, `gov task create` should stamp `provenance`. That is IP-4 (WS-5, `tasks.rs`).
  - A verifier may judge the version-control route. I record it as a design choice, not an owner question: the
    mechanism is the repair role's to choose.
- `W1-b3-noncanonical-location-flagged` looks only in audit/doctor output. The detector exists (`gov artefact check`
  names `spec/scenarios/REQ-0003.yaml`). Wiring it into the audit/doctor families is IP-7 (WS-2).
- `W1-b1-audit-finding-id-stable`: audit findings are minted by `verification::audit` (WS-2); IP-10 gives the call.
- `W1-b6-benchmark-hash-in-record`: the research record is minted by `memory::benchmark` (WS-6); IP-13. Its content
  hash is already served by `gov artefact show`.
- Migration plan and catalogue identity are WS-9's side by assignment.
- **Existing indexes.** The derivation of edges changed. An *incremental* rebuild re-derives only changed files, so an
  existing project needs a full `gov rebuild-memory` to get the new edges. Bumping `INDEX_VERSION` would force that
  through the existing pin check. That constant is in `lib.rs`, where I may add `pub mod` lines only, so it is IP-17.

## 3. BC-P2-17 — Mandatory task-input manifest semantics

**Requirement.** Repair-delta §1 BC-P2-17; Contract v3 lines 1084-1104. For each dependency a task declares:
- id, required/optional, required authority/lifecycle state, version/hash constraint where applicable, and reason;
- plus separately declared supplementary context.

Readiness and delivery enforce these declarations. A superseded or historical input never silently satisfies a
current requirement. The authority class survives into the packet. Output contracts declare what downstream stages may
consume.

**What changed** (`runtime/src/context/manifest.rs`; its module documentation holds the full declaration table)

- **Declarations.** These all feed one merged entry per `(slot, id)`, with its reasons and every place it was declared:
  - the typed fields;
  - the feature's inherited requirements/scenarios/acceptance tests/interfaces;
  - decisions that apply through `affects`/`governed_by`;
  - implicit current architecture (delivered, not required);
  - `required_inputs` / `optional_inputs` entries `{id, type?, required?, reason, required_status, required_state_class,
    version, content_hash}`;
  - `relations[]` of an input type, where the `note` is the reason;
  - `supplementary_context`, kept apart and never authority.
- **Resolution** runs from governed records only, and is identical with the index present or absent. An entry is
  satisfied only when all of these hold:
  - it resolves to exactly one record of the slot's type;
  - the record is current (or matches the declared `required_status`);
  - no successor supersedes it;
  - its authority class suits the slot (authority slots require AUTHORITATIVE unless declared otherwise);
  - it meets the declared `version` constraint (exact, `*`, `=`, `>=`, `>`, `<=`, `<`, `^`, `~`) and `content_hash`
    pin (SHA-256 or a prefix of 12 or more hex characters).
- **Typed problem codes.** `ABSENT`, `TYPE_MISMATCH`, `AMBIGUOUS_ID`, `SUPERSEDED`, `LIFECYCLE_STATE`,
  `AUTHORITY_CLASS`, `VERSION_MISMATCH`/`VERSION_UNAVAILABLE`, `HASH_MISMATCH`/`HASH_CONSTRAINT_INVALID` and
  `CONFLICTING_CONSTRAINTS` all block. `PROVISIONAL` and `NON_CANONICAL_LOCATION` are advisory. Each carries a
  remediation message.
- **Delivery state.** Any blocking problem on a required input makes the manifest `BLOCKED` and names it in
  `missing_inputs` / `input_violations`.
- **Flagged, never silent.** A superseded, non-current, non-authoritative or ambiguous input is delivered with an
  `authority_flag` (`UNKNOWN_OR_CONFLICTING`, `SUPERSEDED`, `HISTORICAL`, `NOT_AUTHORITATIVE`,
  `AMBIGUOUS_DUPLICATE_ID`, `CONSTRAINT_VIOLATION`) and its `state_class`. It never satisfies the manifest silently.
- **READY check.** `manifest::require_ready(p, store, task)` refuses with `INPUT_MANIFEST_UNSATISFIED`. The details and
  the remediation name every missing or violated input. This is the check WS-5 wires into READY derivation (IP-1).
- **Output contracts.** `framework/schemas/context-packet.schema.json` `x-output-contracts` declares, per output type,
  which manifest slots downstream stages may consume it as. The unit test
  `output_contracts_in_the_schema_are_the_enforced_table` pins the schema table to the table the resolver enforces.
- **CLI.** `gov context manifest <task>` shows the full resolution.

**Product checks that own it.**
- The resolution runs inside every packet compile; `continue` compiles at dispatch.
- `gov context manifest` runs on demand.
- READY gating comes through IP-1 (WS-5).
- Unit tests: `context::manifest::tests::*` (6).

**Probes re-run (before → after)**

| Probe line | Before | After |
|---|---|---|
| W02 `W2-b2-required-optional-marker`, `W2-b3-non-authoritative-not-promoted`, `W2-b6-stale-requirement-cannot-replace-current`, `W2-b7-output-schema-consumption-rules` | FAIL | PASS |
| W02 `W2-b2-declared-input-drop-is-explicit` | FAIL | PASS (see disclosure) |
| W02 `W2-b4-*`, `W2-b5-*`, `W2-b6-retrieval-excludes-superseded`, `W2-b6-stale-decision-flagged` | PASS | PASS |
| W03 `W3-m4-reason-delivered`, `W3-m4-relations-note-dependency-delivered`, `W3-m5-supplementary-declared-separately`, `W3-r2-superseded-input-not-silent`, `W3-r3-duplicate-id-conflict-handled` | FAIL | PASS |
| W03 `W3-m1`, `W3-r4-deterministic-resolution`, `W3-r3-conflicts-detected-by-*` | PASS | PASS |
| W03 `W3-m2-required-state-enforced`, `W3-m3-hash-pin-enforced`, `W3-r1-*` (5), `W3-r3-conflict-triggers-handling` | FAIL | FAIL — all read `gov task dag`/`create`/`status`/`claim`/`replan` (WS-5); IP-1 |
| W10 `W10-a2-variant-stale-structured-reference` | FAIL | PASS |

**Disclosures.**
- `W2-b2-declared-input-drop-is-explicit` passes on its second clause, the substring `dropped` anywhere in the packet.
  That substring comes from the new `budget.dropped_supplementary_slices` key.
  - The substantive behaviour is that `input_manifest.missing_inputs` names `RES-0001` (`TYPE_MISMATCH`: declared as a
    requirement, is research). That block sits outside `deterministic_authority` on purpose.
  - Putting the list inside the authority block would put `L-0001` there and regress `W2-b5-lesson-not-in-authority-block`.
- `W2-b7` is a static keyword scan of `framework/schemas`. Its substance is the `x-output-contracts` table and the test
  that pins it.
- The m2/m3 lines already resolve correctly on the manifest side: `gov context manifest TASK-0102` in that scenario
  reports `LIFECYCLE_STATE` / `HASH_MISMATCH`, as scenario S1 shows.

**Builder scenarios.** S1: 10/10 PASS (negative control 0/10).

**Limits.** READY derivation and claim gating are WS-5's. The contradiction-routing half of BC-P2-18 (a gate or
contradiction task) is WS-3's. My side makes the conflict a blocking manifest problem that READY gating can act on.

## 4. BC-P2-19 — Context-packet delivery, provenance and outage

**Requirement.** Repair-delta §1 BC-P2-19; Contract v3 lines 1106-1112, 1164-1171:
- Every declarable mandatory input type is delivered deterministically, with normative content, exact id and
  version/content hash.
- The packet hash changes whenever supplied content changes, and is traceable to input versions and repository state.
- A missing required input causes refusal or an explicit blocked state.
- A retrieval or index failure degrades only the supplementary block, explicitly marked.

**What changed** (`runtime/src/context/mod.rs`)

- **Content.** Each delivered input carries its whole record (`content`) and Markdown `body`, `version`,
  `content_hash`, `state_class`, `required`, `reason`, `declared_in`, and any `authority_flag`/`problems`.
- **Slots.** Requirements, decisions (active/conflicting), architecture, interfaces at task *and* feature level,
  scenarios, `test_designs`, `datasets`, `evidence_inputs` (experiments, research, …) and `other_inputs`. Each input
  appears once.
- **Blocks.** New top-level blocks, in addition to the existing ones:
  - `input_manifest` (hashed as `manifest_hash`) with `delivery_state`;
  - `input_hashes`;
  - `receipt_contract`;
  - `provenance` (`repo_commit`, uncommitted inputs, compiler versions);
  - `supplementary_state`;
  - `budget`.

  `packet_hash` covers the deterministic block, the manifest, the receipt contract and the supplementary block.
- **History.** Every packet is kept at `.governance-runtime/context/packets/<task>/<packet_hash>.json`.
  `context::load_packet` / `gov context show --hash` resolve a recorded hash.
- **Missing input.** A missing required input gives an explicit `delivery_state: BLOCKED` naming it.
  `context::ensure_dispatchable(&packet)` is the typed refusal (`INPUT_MANIFEST_UNSATISFIED`) for dispatch sites
  (IP-3).
- **Outage.** Retrieval, lesson retrieval and code-reference lookups no longer abort the compile. Their failures
  become `retrieved_intelligence.degraded` with reasons and remediation.
  - `compile` takes the index as `impl Into<IndexHandle>`; existing `&RuntimeDb` callers are unchanged.
    `compile_tolerant` opens the index itself and compiles with `IndexHandle::Unavailable` when it cannot.
  - `gov context compile` uses it, so a deleted, corrupted or re-pinned index still yields the complete mandatory
    packet.
- **Token pressure** drops only supplementary slices, including declared supplementary context. Over budget, the
  packet carries `budget.over_budget` and an explicit warning.
- **Schema.** The packet is validated against `context-packet.schema.json` at compile.
- **Verification.** `context::verify_delivery` / `gov context verify` re-resolves the manifest and checks:
  - every required input was delivered at its current hash;
  - the deterministic block still hashes to `deterministic_hash`;
  - the packet was not compiled blocked.

**Product checks that own it.**
- Every compile (and therefore every `continue` dispatch) delivers from the manifest, marks outage explicitly and
  validates the schema.
- `gov context verify` runs on demand; the audit context family comes through IP-9 (WS-2).
- The existing certification tests on packets (greenfield, repair, repair2, multi_machine, section6) stay green.

**Probes re-run (before → after)**

| Probe line | Before | After |
|---|---|---|
| W04 `W4-b1-normative-content-loaded(statement field)` / `(markdown body)`, `W4-b1-no-duplicate-delivery`, `W4-b4-input-versions-hashes-recorded`, `W4-b5-hash-changes-when-supplied-content-changes`, `W4-b5-packet-bound-to-repo-state`, `W4-b6-missing-required-input-refused-or-blocked` | FAIL | PASS |
| W04 `W4-b1-deterministic-load`, `W4-b2-*`, `W4-b3-supplementary-dropped-first`, `W4-b3-mandatory-never-displaced`, `W4-b3-over-budget-is-explicit`, `W4-b4-input-ids-recorded`, `W4-b6-missing-task-dependency-explicit` | PASS | PASS |
| W04 `W4-b3-over-budget-governed-at-dispatch` (A0-W4-05, INFO, non-blocking) | FAIL | FAIL — dispatch is `status::continue_work` (WS-5); IP-3 |
| W04b `W4b-delivered-deterministically:dataset/experiment/research/interface(task)/test-design`, `W4b-stale-input-marked-in-packet` | FAIL | PASS |
| W09 `W9-c2-packet-hash-tracks-input-content` | FAIL | PASS |
| W10 `W10-a4-derived-index-deleted(INV-010)` (+`-continue`), `-derived-index-corrupted`, `-embedder-repinned-before-reindex` (+`-continue`), `-reranker-unavailable` (+`-continue`) | FAIL | PASS |
| W10 `W10-a1-*`, `W10-a2-*`, `W10-a3-budget-*`, `W10-a4-vector-table-lost` (+`-continue`), `W10-a5-deterministic-block-separately-observable` | PASS | PASS |
| W10 `W10-a4-derived-index-corrupted-continue` | FAIL | FAIL — `gov continue`'s CLI arm opens the index with `db(&p)?` before any WS-4 code runs; IP-6 (WS-3/WS-5) |
| W10 `W10-a5-product-tests-delivery-against-declaration` | FAIL | FAIL — the governance-suite family is WS-2's; IP-9 wires `verify_delivery` |

**Builder scenarios.** S2: 10/10 PASS (the negative control aborts: the base packet has none of these fields).

**Limits.**
- Checkpoint and handoff continuity (W9 checkpoint input ids, handoff blocking on a stale or missing packet) is
  BC-P2-05, round 2. It builds directly on `input_hashes`, packet history and `ensure_dispatchable`.
- Packet invalidation on upstream change is BC-P2-04, round 2. It builds on `verify_delivery`.

## 5. BC-P2-20 — Consumption receipt and implementation traceability (contract and lineage side)

**Requirement.** Repair-delta §1 BC-P2-20; Contract v3 lines 1115-1126, 1147-1152:
- The worker's structured return is the consumption receipt (one contract, or a lossless validated mapping). It is
  validated against the manifest.
- Close refuses missing mandatory traceability and reports untraceable implementation.
- Code/test/output evidence links back to the authoritative inputs, and the links can be followed both ways.

Close-side validation is WS-5's.

**What changed** (`runtime/src/context/receipt.rs`; its module documentation holds the contract table)

- **One contract.** The receipt fields are `context_packet_hash`, `inputs_consumed` (`ID@<content_hash>` or
  `{id, content_hash}`), `outputs_produced` (alias `files_changed`), `requirements_implemented` /
  `scenarios_implemented` / `features_implemented`, `decisions_applied` / `constraints_applied`, `acceptance_evidence`
  (`{test, result, evidence}`), `deviations` and `unresolved` (alias `unknowns`).
  - `report_from_worker_return` maps the worker's `status` onto `outcome` and keeps every other field.
    `worker_return_from_report` is its inverse. The tests show the round trip is exact and that a schema-valid worker
    return maps to a schema-valid report (S0-W5-01).
  - The receipt is defined in `context-packet.schema.json` `$defs/consumption_receipt`.
  - Every packet carries the `receipt_contract` for its task: the inputs to acknowledge with their hashes, the ids to
    trace, and the tests needing evidence.
- **Validation.** `receipt::validate` refuses, with typed codes:
  - `RECEIPT_FIELDS_MISSING` — a required field is absent;
  - `MANIFEST_UNSATISFIED` — completion on absent or superseded inputs;
  - `PACKET_BLOCKED` — the named packet was compiled blocked;
  - `UNKNOWN_REFERENCE` / `WRONG_REFERENCE_TYPE` — fabricated trace;
  - `CLAIM_OUTSIDE_MANIFEST` — undocumented implementation;
  - `INPUT_NOT_ACKNOWLEDGED` — a required input not recorded as consumed;
  - `STALE_CONSUMPTION` — consumed at a hash that is no longer current;
  - `UNTRACEABLE_IMPLEMENTATION` / `TRACEABILITY_MISSING` / `TRACE_INCOMPLETE` — every required
    requirement/scenario/decision must be implemented or applied, or named in a deviation;
  - `TEST_EVIDENCE_MISSING` / `TEST_EVIDENCE_NOT_PASSING` — a declared acceptance test without passing evidence.

  Traceability is required for implementation-class tasks, and for any task whose outputs include repository-contract
  `source` paths. An unknown packet hash is a warning (`PACKET_UNKNOWN`), because packet history is machine-local;
  consumption is then proven by the content hashes alone.
- **Refusal and persistence.** `receipt::require_valid` returns the report fields to persist: the canonical receipt
  merged over the report, plus `receipt_validation`. Otherwise it refuses with `RECEIPT_INVALID` and every error in
  the details. WS-5 wires this into `tasks::close` (IP-2).
- **Handoff return.** `handoff return` validates the worker return as the receipt and records `receipt_validation` on
  the handoff and in its result. It does not refuse; refusal is close's.
- **Untraceable closed work.** `receipt::untraceable_closed_tasks` lists DONE tasks whose closing receipt does not
  trace (IP-8, WS-2).
- **Lineage.** The persisted receipt fields and outputs become edges (§2), so code, reports, tests and inputs are
  connected:
  - `graph::impact_set` finds the implementation and evidence affected by a requirement or decision change;
  - `graph::upstream_set` / `gov artefact lineage --direction up` traces an output back to its inputs.

**Product checks that own it.**
- Every `handoff return` validates and records the verdict.
- `gov context receipt` validates on demand.
- Close refusal comes through IP-2 (WS-5); the audit report through IP-8 (WS-2).
- Unit tests: `context::receipt::tests::*` (2), plus the edge tests in §2.

**Probes re-run (before → after)**

| Probe line | Before | After |
|---|---|---|
| W05 `W5-c3-code-linked-to-requirement`, `W5-c3-report-linked-to-requirement`, `W5-c3-report-task-edge-direction` | FAIL | PASS |
| W05 `W5-r1-packet-hash-on-close-checkpoint`, `W5-r2-outputs-produced`, `W5-r5-tests-status-enforced`, `W5-r6-deviations-persisted-when-given`, `W5-r6-handoff-return-requires-unknowns`, `W5-c2-undocumented-change-detected` | PASS | PASS |
| W05 `W5-c1-*`, `W5-r1-inputs-supplied-in-receipt`, `W5-r3-*`, `W5-r4-*`, `W5-r5-acceptance-evidence-bound-to-declared-tests`, `W5-r6-task-close-requires-unknowns`, `W5-r3r4-fabricated-trace-refused`, `W5-c2-untraceable-implementation-detected` | FAIL | FAIL — all refusals at `task close` (WS-5); IP-2 wires `require_valid` |
| W05 `W5-c3-task-to-code-edge` | FAIL | FAIL — needs `outputs_produced` on the task record at close (IP-2). The report-mediated path already passes (lines above). |
| W05 `W5-c2-untraceable-implementation-reported-by-audit` | FAIL | FAIL — WS-2 family; IP-8 |
| W05 `W5-c2-no-claim-observed-paths-correct` (A0-W5-03, LOW, non-blocking; `project.rs` porcelain parse, WS-3) | FAIL | FAIL — not in my classes |
| W08 `W8-l1-forward-reaches:file:src/lib.rs` / `:file:tests/ledger_test.rs`, `W8-l2-reverse-impact(REQ-0001|D-0001)->implementation` / `->evidence`, `W8-l5-cross-language-through-interface` | FAIL | PASS |
| W08 `W8-l1-forward-reaches:release` | FAIL | FAIL — release artefacts are not governed records with edges (WS-8); IP-16 |
| W08 `W8-l3-missing-task-to-code-link-detected`, `W8-l4-stale-link-to-superseded-detected` | FAIL | FAIL — audit/doctor families (WS-2); the detectors exist (`untraceable_closed_tasks`, `stale_links`; `gov artefact check` names `TASK-0003 → REQ-0009`); IP-7/IP-8 |
| AC16-X2 `X2-N4xW5-worker-return-usable-at-close` | FAIL | FAIL — `tasks::close` validates the report schema before any mapping; IP-2's first line |

**Builder scenarios.** S3: 8/8 PASS (the negative control aborts). Covered:
- a bare report is refused;
- fabricated trace is refused;
- the receipt built from `receipt_contract`, in worker-return shape, is accepted;
- a claim outside the manifest is refused;
- stale consumption is refused;
- handoff return records the verdict;
- after close, `file:src/lib.rs` traces up to the requirement, decision and report, and the requirement reaches down to
  the code.

**Limits.** Close-time refusal, and the task→code edge persisted on the task record, need `tasks.rs` (WS-5; IP-2).
Release lineage is WS-8's.

## 6. Preservation (AC-14) and regression

### 6.1 Product regression

| Suite | Base `c6b60bc` | Final `6fc7361` | Evidence |
|---|---|---|---|
| `cargo test --lib` | 42 passed / 0 failed | 57 passed / 0 failed (15 new) | `evidence/before/cargo-test-lib.out`, `evidence/after/cargo-test-lib.out` |
| `cargo test --test certification` | 79 / 0 | 79 / 0 (includes `section6::section_6_coverage_is_derived_from_the_product` and every context-packet test) | `evidence/{before,after}/cargo-test-certification.out` |
| `rustfmt --check` on the owned files I touched | — | clean (`records.rs`, `handoffs.rs`, `context/**`, `graph/**`) | — |

I changed no existing test. `cli/src/main.rs` was not rustfmt-clean at base. I kept its pre-existing lines
byte-identical, added only self-contained blocks, and did not reformat the file.

### 6.2 R1 held-out suites (required: `records.rs` is touched)

Each suite was run unedited, as `REPRODUCTION.md` §4-§6 describes, by `evidence/run-r1-heldout.sh`: copied
byte-identically, with only the dependency path satisfied by symlink, one test binary at a time, single-threaded.

| Suite | Recorded baseline | Base `c6b60bc` (clone) | Final `6fc7361` |
|---|---|---|---|
| AR-0027 | 26 passed / 3 failed (`b1`, `b2`, `d3`) | 26 / 3, same tests | 26 / 3, same tests |
| AR-0029 | 26 / 2 of 28 compiled; `ho_f_preservation` does not compile (`b3`, `b6`) | same | same |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | same | same |
| AR-0033 | 31 / 0 | 31 / 0 | **30 / 1**: `hv_a_derivation::a1_the_derived_census_reproduces_independently_at_the_claimed_scale` |

Evidence: `evidence/before/r1-heldout-base.out`, `evidence/after/r1-heldout-worktree.out`.

**AR-0033 `a1`.**
- The test asserts `files.len() == 84` and `funcs.len() == 740`: the candidate-4 scale pinned "rather than taking it
  from the repair report". It then derives the §6 census.
- This tree has 88 files / 832 functions, from four new WS-4 modules and their functions, so the test stops at the pin
  before the census runs. Any Phase-2 repair that adds a product function fails this line the same way.
- To show that the property it guards still holds, I ran **AR-0033's own census machinery** in a separate harness
  (`evidence/r1-supplementary/census_unpinned.rs`). It links AR-0033's `common.rs`, copied byte-identically, and runs
  a1's census loop against the product's own `breakglass` signature, write-primitive and exemption tables, without the
  scale pin. The suite itself is not edited.
- Results (`evidence/before/r1-supplementary-census-unpinned-base.out`, `evidence/after/r1-supplementary-census-unpinned.out`):

| §6 activity | Base (84 / 740) derived / writers / exempt / violations | Final (88 / 832) |
|---|---|---|
| human_gate_create | 35 / 32 / 1 / 0 | 36 / 32 / 1 / 0 (the extra derived function is `graph::identity::canonical_dir`, a non-writing reader of `record_dir_for`) |
| human_gate_approve | 1 / 1 / 0 / 0 | 1 / 1 / 0 / 0 |
| release_certification | 2 / 1 / 0 / 0 | 2 / 1 / 0 / 0 |
| trust_policy_mutation | 7 / 1 / 0 / 0 | 7 / 1 / 0 / 0 |
| privileged_plugin_acquisition | 9 / 2 / 0 / 0 | 9 / 2 / 0 / 0 |
| floor_lower_or_reset | 3 / 1 / 0 / 0 | 3 / 1 / 0 / 0 |
| present_below_floor_release_as_current | 1 / 1 / 0 / 0 | 1 / 1 / 0 / 0 |

**AR-0033 `hv_b::b7`.**
- The first repair commit (`a1e2a5c`) moved the packet body into a private `compile_inner`, which failed `b7`: that
  test checks, by function body, that `context/mod.rs::compile` itself carries the §6 bullet-7 marking. The packet
  still carried the marking at runtime.
- Commit `6fc7361` moves the full body back into `compile`, and `b7` passes. I note this because the check is
  structural: a future refactor of `compile` must keep `present::presentation("context packet")` in that function's
  body.
- No SRR control was touched. None of `srr/**`, `kernel*.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`,
  `recovery.rs`, `tools.rs` or `capabilities/**` changed, and `records::save_record` (the record-write sink) is
  byte-identical.

### 6.3 Behaviour changes other workstreams will see

These consequences are intended; I record them for round 2 and for WS-2/WS-5:
- **Larger impact sets.**
  - An architecture record reaches every task.
  - A requirement or decision reaches its implementing tasks' reports, checkpoints, handoffs and produced files.
  - In a project with implemented work, CIT simulation can therefore reach more modules and features, and escalate its
    radius under the existing `CHANGE_POLICY.radius_rules`. That is the propagation W6 asks for.
  - Calibrating it is BC-P2-04/BC-P2-13 (round 2).
- **Inverse storage types.** The edges table now holds `CONSUMED_BY` / `PRODUCED_BY` / `BLOCKED_BY` /
  `SUPERSEDED_BY` rows. Code that reads `edges` directly must go through `graph::{out_edges,in_edges}` or
  `graph::canonical_of`. Today only `memory::heldout` does, to pick sample ids, which is unaffected.
- **Packet shape.** The packet grew: full content, and three extra blocks. `CONTEXT_POLICY.max_packet_chars` still
  displaces only supplementary slices; the mandatory blocks are never displaced.

## 7. Integration points (for the owning workstreams; not implemented here)

| IP | Owner | File / function | Exact call | Closes |
|---|---|---|---|---|
| IP-1 | WS-5 | `orchestration::dag::compute`; `tasks::create` (status READY), `tasks::set_status(.., "READY")`, `tasks::claim`, `replan` | `let m = crate::context::manifest::resolve(p, &store, t); if !m.satisfied() { /* blocked with m.blocking_reason(), not runnable */ }`; at the READY/claim routes `crate::context::manifest::require_ready(p, &store, id)?;` | W3-r1-* (5), W3-m2, W3-m3, W3-r3-conflict-triggers-handling (UNKNOWN_OR_CONFLICTING decisions block), W12-G0 claim |
| IP-2 | WS-5 | `tasks::close` | Before any schema validation: `let report = crate::context::receipt::report_from_worker_return(&report);`. Then, before minting the report: `let report = crate::context::receipt::require_valid(p, &store, id, &report)?;`. After persisting: `tr.set("outputs_produced", json!(observed));` on the task record. Optionally add `$defs/consumption_receipt` properties to `report.schema.json`/`worker-return.schema.json`. | W5-c1, W5-r1, r3, r4, r5, r6, r3r4, c2-detected, c3-task-to-code-edge; X2-N4xW5; W12-G2 |
| IP-3 | WS-5 | `status::continue_work` | Compile with `crate::context::compile_tolerant(p, &next)` (or `compile(p, db, ..)`), then skip a `BLOCKED` packet or refuse with `crate::context::ensure_dispatchable(&packet)?`. Treat `packet["budget"]["over_budget"]` as a governed degradation. | W4-b6 at dispatch; A0-W4-05 (INFO) |
| IP-4 | WS-5 | `tasks::create` | Stamp `provenance: {producer: "gov task create", session: p.session_id, role: p.role, created_at: now_iso()}` | W1-b7-task |
| IP-5 | WS-5 | `framework/schemas/task.schema.json` | Declare `required_inputs` / `optional_inputs` (items as `context-packet.schema.json` `$defs/task_input_declaration`), `supplementary_context`, `architecture`, `relations[].note`/`required` | schema documentation of the W3 manifest |
| IP-6 | WS-3 + WS-5 | `cli/src/main.rs` `Cmd::Continue`; `status::continue_work` signature | Do not fail on `db(&p)?`. Open with `gov_runtime::context::open_index(&p)` and pass `IndexHandle::Unavailable(e)` through to `context::compile` when it cannot be opened (a corrupt index). | W10-a4-derived-index-corrupted-continue |
| IP-7 | WS-2 | `verification::run` `graph_integrity`; `doctor` D015/D023 | Report `crate::graph::identity::misplaced_records(Some(p), &store)`, `crate::graph::lineage::stale_links(&store)`, `crate::graph::lineage::unconsumed_outputs(&store)` | W1-b3-noncanonical-location-flagged, W8-l4, W7-o1 (BC-22 input) |
| IP-8 | WS-2 | `verification::run` `product_traceability` | Report `crate::context::receipt::untraceable_closed_tasks(p, &store)` | W5-c2-…-reported-by-audit, W8-l3 |
| IP-9 | WS-2 | `verification::run` `context_reproducibility` | For every task: `let pk = crate::context::compile(p, db, &id)?; crate::context::verify_delivery(p, &pk)?` and report undelivered/stale/BLOCKED | W10-a5, W12-G5 |
| IP-10 | WS-2 | `verification::audit` (finding ids, `GF-{n:04}`) | `crate::graph::identity::stable_content_id("GF", &[family, message, path])` | W1-b1-audit-finding-id-stable |
| IP-11 | WS-1 | `tests/governance/capability-evidence-map.yaml` | Owners for W1/W2/W3/W4/W5/W8/W10: the unit tests `graph::*`, `graph::lineage::*`, `graph::identity::*`, `context::manifest::*`, `context::receipt::*`; the checks `gov context manifest|verify|receipt`, `gov artefact check`; the WS-2 families after IP-7..IP-9 | AC-10 evidence owners |
| IP-12 | WS-6 | `memory/indexer.rs`; BC-P2-28 graph integrity | No change is needed for correctness (`Record::relations()` keeps its contract). BC-P2-28's reversed/ill-typed checks should use `Record::edges()` and `graph::canonical_of`. | — |
| IP-13 | WS-6 | `memory::benchmark` research record | Record `content_hash`/`version` of the benchmark result in the record | W1-b6-benchmark-hash-in-record |
| IP-14 | WS-9 | adoption plan and catalogue | Catalogue ids from the natural key (`stable_content_id("ART", &[path])`); plan `id/type/version/producer/supersedes`, with re-plan keeping history | W01b, LEAD-X5 X5-W1/X5-T3 |
| IP-15 | WS-2 (scheduler) | tier contract | Health tiers: G2 = IP-2 and IP-1; G3 = `ensure_dispatchable`/`verify_delivery` at checkpoint/handoff (round-2 BC-P2-05); G5 = IP-7..IP-9 | W12 |
| IP-16 | WS-8 | release records | Release artefacts as governed records with `derived_from`/`validated_by` edges to the reports and evidence they certify | W8-l1-forward-reaches:release |
| IP-17 | owner of `lib.rs` constants (WS-6 / orchestrator) | `runtime/src/lib.rs` `INDEX_VERSION` | Bump the index version. The edge derivation changed, and incremental rebuilds do not re-derive unchanged records; the existing pin check then forces a full rebuild. | existing projects get canonical edges |

The WS-4 round-2 classes (BC-P2-04, -05, -11, -13) were not started. They build on `verify_delivery`, the packet
history, `input_hashes`, `ensure_dispatchable` and the canonical edges.

## 8. Owner-decision questions

None. No class required changing an accepted architecture or trust boundary, adding a new external dependency class,
making an open trade-off, or touching owner-controlled material. Two notes, which are not owner questions:

1. **The R1 held-out scale pin** (§6.2). This is for the AC-14 R1-preservation verifier and the orchestrator. Every
   repaired candidate that adds a product function fails the pin, so the AC-14 verifier will have to decide how to
   treat it.
2. **Authored-record provenance** (§2 limits). It is served from version control rather than written into authored
   records. This is a mechanism choice within the repair role, graded by the next verifier.

## 9. Evidence index

| Path | Content |
|---|---|
| `evidence/rerun-zeta-probes.sh` | Re-runs the zeta-r probes unedited; outputs go to a chosen dir, never to the audit-of-record dir |
| `evidence/compare-probe-lines.py` | Per-observation before/after comparison |
| `evidence/before/*.out` | Base `c6b60bc`: all 16 zeta-r probes (identical outcomes to the audit of record), `cargo test` outputs, R1 held-out, unpinned census, WS-4 scenarios negative control on the base binary |
| `evidence/after/*.out` | Final `6fc7361`: all 16 zeta-r probes, `COMPARE-before-after.out` (47 FAIL→PASS, 0 PASS→FAIL), `cargo test` outputs, R1 held-out, unpinned census, `ws04-scenarios.out` (37/37), AC16-X1/AC16-X2/LEAD-X5 re-runs (identical outcomes to the audit of record) |
| `evidence/ws04-scenarios.py` | Builder regression scenarios S1-S4 through the binary; `WS04_GOV`/`WS04_ROOT` select the negative control |
| `evidence/run-r1-heldout.sh`, `evidence/r1-supplementary/census_unpinned.rs` | R1 held-out runner and the supplementary unpinned census harness |

**Transient disclosure.** During development a build made the out-of-class line `AC16-W12xO5-tier-scheduler-present`
flip to PASS. That probe greps product source for `\bG[0-6] `, and it matched tier names in my doc comments. I reworded
the comments, so the line reflects the product again (FAIL at `6fc7361`, as at base): the tier scheduler is WS-2's.
